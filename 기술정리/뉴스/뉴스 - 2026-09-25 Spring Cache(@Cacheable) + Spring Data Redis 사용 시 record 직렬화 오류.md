---
출처: Claude 분석(데일리 인풋)
원본: https://techblog.woowahan.com/22767/
작성일: 2026-09-25
성격: 예습자료
tags: [학습, spring, java]
---

# 뉴스 - 2026-09-25 Spring Cache(@Cacheable) + Spring Data Redis 사용 시 record 직렬화 오류

> 상위: [[뉴스 인덱스]]
> 이전: [[뉴스 - 2026-09-24 사장님 입점신청 자동승인 주기를 10분에서 10초로]]

**원문**: [Spring Cache(@Cacheable) + Spring Data Redis 사용 시 record 직렬화 오류 원인과 해결](https://techblog.woowahan.com/22767/) — 조충범 · 2025.08.19 · Backend

## 배경

글은 `record`로 만든 DTO(`UserRecord(Long id, String name)`)를 `@Cacheable`로 Redis에 캐싱하던 중, **첫 요청은 정상이고 두 번째 요청부터** `InvalidTypeIdException: missing type id property '@class'`가 터진 상황에서 출발한다. 캐시 값 직렬화기는 `GenericJackson2JsonRedisSerializer` + `activateDefaultTyping(ptv, DefaultTyping.NON_FINAL, As.PROPERTY)`로 커스터마이즈한 `ObjectMapper`였다. 컴파일도 되고 첫 호출(캐시 미스)은 원본을 그대로 반환하니, 캐시 히트 경로를 실제로 태우는 테스트가 없으면 리뷰·테스트 단계에서 잡히지 않는 "런타임에만 드러나는" 유형이었다고 설명한다.

## 핵심

- **원인**: `DefaultTyping.NON_FINAL`은 final이 아닌 타입에만 `@class`를 붙인다. `record`는 암묵적으로 final이라 JSON이 `{"id":1,"name":"User-1"}`처럼 타입 정보 없이 저장된다. 캐시에서 꺼낼 때는 대상 타입이 `Object.class`라 JSON 안의 `@class`로만 타입을 추론해야 하는데, 그게 없으니 실패한다.
- **Jackson 버그가 아니라 설계 의도**: 필자는 처음 jackson-databind에 버그로 이슈(#5223)를 올렸지만, 논의 끝에 "final 타입은 다형성이 없으니 타입 정보가 불필요하다"는 Jackson의 정상 동작임을 받아들였다고 한다. 문제의 본질은 Jackson의 다형성 중심 설계와, 타입 정보가 늘 있을 거라 기대하는 Spring Data Redis 사이의 간극이라고 정리한다.
- **Spring Data Redis의 입장**(이슈 #2601): 직렬화기가 쓰는 `ObjectMapper`의 모듈 등록·커스텀 설정은 **사용자 책임**. Jackson 버전마다 동작이 달라지는 것을 라이브러리가 추적하면 오히려 불안정해진다는 이유.
- **반려한 대안 1 — `DefaultTyping.EVERYTHING`**: 모든 타입에 `@class`를 붙여 해결은 되지만, 직렬화 결과가 커지고 Jackson에서도 Deprecated 방향이라 추천하지 않는다고 한다.
- **반려한 대안 2 — record 대신 일반 class**: 가장 현실적이지만, 팀이 record를 많이 써서 누군가 record에 캐싱을 거는 실수가 반복될 수 있다.
- **반려한 대안 3 — Wrapper + `@JsonTypeInfo(use = Id.CLASS, include = As.WRAPPER_ARRAY)`**: base type을 `Object`로 강제해 타입 정보를 보장하지만, 매번 감싸야 해서 개발자가 계속 신경 써야 한다. 세 대안 모두 "개발자 실수 가능성"을 전제로 한다는 점이 반려 이유.
- **내부 확인**: `GenericJackson2JsonRedisSerializer`는 직렬화 때 `ObjectMapper`를 그대로 쓰고, 역직렬화 때 `resolveType()`이 타입이 `Object.class`이고 default typing이 켜져 있으면 JSON 속 타입 정보로 추론한다. → "직렬화 시점에 `@class`만 붙게 하면 된다"는 결론.
- **최종 해결 — `RecordSupportingTypeResolver`**: `DefaultTypeResolverBuilder`를 상속해 `useForType(JavaType t)`를 override, `t.getRawClass().isRecord()`면 `true`, 아니면 `super.useForType(t)`. `typeResolver.init(JsonTypeInfo.Id.CLASS, null).inclusion(As.PROPERTY)` 후 `mapper.setDefaultTyping(...)`으로 적용. 같은 id로 두 번 호출해 두 결과가 같은지 비교하는 `@SpringBootTest`로 전후를 검증했고, Jackson 컨트리뷰터에게도 긍정적 반응을 받았다고 한다.
- **주의**: 직렬화 형식이 바뀌면 기존 캐시 데이터와 호환이 깨진다. 배포 전 검증하고, 필요하면 `cacheName`에 버전을 붙여 충돌을 피하라고 권한다.

## 내 프로젝트와의 연결

WMS와 직접 닿는다. WMS의 성능 측정 단계에서 캐싱(Spring Cache + Redis)을 붙인다면, 응답 DTO를 record로 쓰는 순간 이 함정을 그대로 밟을 수 있다 — 특히 Before/After 측정 때 "첫 호출만 보고 캐시가 잘 붙었다"고 판단하기 쉽다는 점이 위험하다. 캐시 테스트는 **같은 키로 두 번 호출해 두 번째가 캐시 히트 경로를 타는지**까지 확인해야 한다는 교훈을 옮겨올 수 있다. 또 재고 수량처럼 자주 바뀌는 값은 캐시 대상이 아니고, 상품 마스터·로케이션 정보처럼 변경이 드문 조회에 한정하는 판단도 함께 필요하다. 수집기는 SQLite 단일 저장소라 Redis 캐시와는 직접 연결이 약하고, "저장 형식이 바뀌면 기존 데이터와 호환이 깨진다 → 버전을 키에 넣는다"는 스키마 변경 관점 정도만 구조적으로 비슷하다.

## 오늘 정리할 것

1. 작은 Spring Boot 프로젝트에서 record DTO + `@Cacheable` + `GenericJackson2JsonRedisSerializer`(NON_FINAL) 조합으로 같은 id를 두 번 호출해 `missing type id property '@class'` 예외를 직접 재현한다 (Redis는 Docker로 띄움).
2. `redis-cli`로 저장된 값을 `GET`해 `@class`가 없는 JSON을 눈으로 확인하고, record를 일반 class로 바꿨을 때 JSON이 어떻게 달라지는지 비교한다.
3. Spring Boot 기본 `RedisCacheManager`는 값 직렬화기로 무엇을 쓰는지(JDK 직렬화인지 JSON인지), 그리고 `Jackson2JsonRedisSerializer<T>`(타입 지정형)를 캐시별로 쓰면 이 문제가 생기는지 공식 문서에서 확인해 한 줄씩 적는다.
4. WMS에서 캐시 후보가 될 조회 API를 2~3개 골라, "변경 빈도 / 캐시 무효화 시점(`@CacheEvict`) / 응답 DTO가 record인지"를 표로 적어 본다.
