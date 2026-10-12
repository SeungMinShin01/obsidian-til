---
출처: Claude 분석(데일리 인풋)
원본: https://techblog.woowahan.com/2601
작성일: 2026-10-08
성격: 예습자료
tags: [학습, spring]
---

# 뉴스 - 2026-10-08 Spring Cache 단건 다건 key에 같은 저장소 사용하기

> 상위: [[뉴스 인덱스]]
> 이전: [[뉴스 - 2026-10-07 끝냈는지가 아니라 되돌릴 수 있는지를 묻기 시작했다]]
> 다음: [[뉴스 - 2026-10-08 근거를 세우기 전에 손이 먼저 나간다]]

**오늘의 글**: Spring 의 Cache 추상화를 사용하면서, 단건/다건 key 에 대한 동일 저장소 사용하기
WoowaTech · 2019-01-04 · Backend (태그: cache, Spring)
https://techblog.woowahan.com/2601

## 배경
글은 Guava로 만들던 Local Cache를 Spring Cache Abstraction으로 옮기려는 상황에서 시작한다. 목표는 단건 조회(`find(Long)`)와 다건 조회(`find(Set<Long>)`)가 같은 요청/응답 형태를 유지하면서 하나의 Local Cache 저장소를 공유하게 하는 것이다. `@Cacheable`은 메서드 파라미터 전체가 key라서 다건 메서드에 붙이면 Set 통째로 key가 되어 단건 캐시와 섞이지 않는다.

## 핵심
- 첫 시도(다건 메서드 안에서 단건 메서드를 for문 호출)는 실패한다고 글은 설명한다. `@Cacheable`이 AOP 프록시 기반이라 같은 클래스 내부 호출(self-invocation)은 프록시를 거치지 않아 캐시가 적용되지 않는다.
- 채택안: `MultiKeyCacheService.multiCacheGet`을 만들어 캐시 API를 직접 호출한다. 파라미터는 `cacheKeyName`, `keyClass`, `valueClass`, `keys`, `notCachedValueFinder`(`Function<Set<K>, Set<V>>`), `keyExtractor`(`BiFunction<V, Class<K>, K>`) 6개.
- 동작 순서: `getCache(cacheKeyName)` → key마다 `cache.get(key, valueClass)` → hit은 `cachedValues`, miss는 `notCachedKeys` → miss만 원본(DB 등)에서 한 번에 조회해 캐시에 put → 합쳐서 반환.
- 단건은 기존 `@Cacheable(cacheNames=...)` 그대로, 다건은 `multiCacheGet`으로 같은 cacheNames 저장소를 공유한다. 로그로 두 경로가 같은 저장소에서 정상 캐싱되는 것을 확인했다고 한다.
- 파라미터 6개 줄이기: 런타임 커스텀 애노테이션 `@CacheKey`를 value 클래스의 key 필드에 붙이고, 리플렉션(`setAccessible(true)` 후 `field.get(v)`, 없으면 `method.invoke(v)`)으로 key를 추출. 타입 불일치·애노테이션 없음이면 `IllegalStateException`.
- 반려한 대안: 구현체 cache2k 1.2.0.Final(Spring Boot 2.0.6)에서 버그(cache2k/cache2k #94)를 만났고, 1.2.1 수정본이 아직 milestone라 Caffeine으로 교체.
- 예제 저장소: `woowabros/multi-key-spring-cache-example`.

## 내 프로젝트와의 연결
WMS에서 SKU·로케이션·재고 마스터처럼 읽기 위주 데이터를 입고/출고 화면에서 여러 건씩 조회할 때, N+1을 캐시로 줄이려는 지점과 구조적으로 닮았다. 다만 이 글은 단일 JVM의 Local Cache 전제이고 재고 수량처럼 자주 바뀌는 값의 무효화·동시성은 다루지 않는다고 읽힌다(글에 없음). 수집기 쪽과는 직접 연결이 약하고, "같은 클래스 내부 호출은 프록시를 우회한다"는 점은 Spring 어디서나 쓰이는 공통 함정이다.

## 오늘 정리할 것
1. `@Cacheable`이 프록시(AOP)로 동작한다는 것과 self-invocation이 우회되는 이유를 `기술정리/Spring` 노트에서 확인하고 내 말로 3줄 정리.
2. 간단한 Spring Boot 예제에서 같은 클래스 내부 호출 vs 다른 빈을 통한 호출로 캐시 hit 로그가 어떻게 달라지는지 직접 돌려 확인.
3. `cache.get(key, type)` 기반 hit/miss 분리 → miss만 일괄 조회하는 패턴을 의사코드로 적어 보고, WMS 어느 조회에 적용 가능한지 후보 1개 찾기.
4. Caffeine과 cache2k의 차이를 확인하고, 이 글의 반려 이유(버그·미배포 수정본)가 기술 선택 기록에서 어떤 "기각 사유" 유형인지 분류.
