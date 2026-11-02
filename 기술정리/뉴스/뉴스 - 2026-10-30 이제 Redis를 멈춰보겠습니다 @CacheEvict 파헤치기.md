---
출처: Claude 분석(데일리 인풋)
원본: https://techblog.woowahan.com/23138/
작성일: 2026-10-30
성격: 예습자료
tags: [학습, spring]
---

# 뉴스 - 2026-10-30 이제 Redis를 멈춰보겠습니다 @CacheEvict 파헤치기

> 상위: [[뉴스 인덱스]]
> 이전: [[뉴스 - 2026-10-29 쌓는 속도는 세 배가 됐고, 쌓은 것의 값은 따로 재야 했다]]
> 다음: [[뉴스 - 2026-10-30 가중치는 열렸고, 숫자는 출처까지 따라가야 했다]]

원문: 이제 Redis를 멈춰보겠습니다: @CacheEvict 파헤치기 — 신익수 · 2025-11-04 · Backend (Spring Boot 3.3.7 / Spring Data Redis 3.3.7 / Lettuce 6.3.2)

## 배경

글은 테스트에서는 잘 돌던 `@CacheEvict(allEntries = true)`가 운영에서는 지연이나 장애로 이어지는 이유를, Spring 캐시 추상화와 싱글 스레드 Redis의 동작이 맞물리는 지점에서 찾는다고 설명한다. 어노테이션이 내부에서 어떤 Redis 명령으로 바뀌는지 구현체 끝까지 따라가 확인하는 구성이다.

## 핵심

- 글은 `@CacheEvict`가 `parseEvictAnnotation()`에서 `CacheEvictOperation`이 되고, `allEntries`가 `cacheWide`로 바뀌어 `performCacheEvicts()`에서 `doClear()`(전체) 또는 `doEvict()`(단건)로 갈라진다고 설명한다.
- `allEntries=false`(기본)는 특정 키에 `DEL`만 보내 O(1)이고, `true`면 `RedisCache.clear()`가 `캐시이름 + "*"` 패턴을 `DefaultRedisCacheWriter.clean()` → `batchStrategy.cleanCache()`로 넘긴다.
- BatchStrategy 구현체는 `Keys`와 `Scan` 두 가지이며, Spring Boot 자동 설정의 기본값은 `BatchStrategies.keys()`라고 한다. 공식 문서 근거는 KEYS가 모든 드라이버·운영 모드(Standalone/Cluster)에서 지원되고 SCAN은 Lettuce에서만 완전 지원된다는 점이다.
- `KEYS`는 전체 키를 훑는 O(N) 연산이라 싱글 스레드 Redis의 다른 요청을 막는다. `DEL`도 키가 많으면 메모리 해제가 이벤트 루프를 점유하므로 백그라운드 해제인 `UNLINK`(또는 `lazyfree-lazy-user-del`)을 권한다. Valkey 8.0부터는 DEL이 기본적으로 UNLINK처럼 동작한다고 한다.
- Scan으로 바꾸려면 `RedisCacheManagerBuilderCustomizer` 빈에서 BatchStrategy를 Scan으로 선언한다. 다만 `lockingRedisCacheWriter`를 쓰면 `cleanCache` 전후로 `doLock()/doUnlock()`이 걸려 SCAN이어도 블록된다.
- 실험에서는 Scan으로 바꾼 뒤 `allEntries=true` API를 호출하자 Pinpoint에 SCAN이 대량으로 찍혔고, 캐시량이 많아 API 타임아웃(60초)이 났다고 한다.
- 운영 Redis가 KEYS 같은 고위험 명령을 인프라에서 막아 두면 기본값 그대로는 `RedisCommandExecutionException`이 난다(우아한형제들도 막아 둠). 글의 결론은 운영 중 `allEntries=true`를 쓰지 말고, 전체 삭제가 꼭 필요하면 Scan 기반의 별도 로직(관리 endpoint·배치)으로 하라는 것이다.
- `allEntries=true`의 정당한 용도로는 대량 변경, 키 규칙(prefix) 변경, 테스트·장애 복구를 든다.

## 내 프로젝트와의 연결

WMS에서 재고·로케이션 조회에 `@Cacheable`을 붙이고 Redis를 도입한다면, 입고·출고로 재고가 바뀔 때의 무효화 전략이 그대로 이 글의 주제다. 글에 따르면 "상품 재고 전체 캐시 비우기"를 `allEntries=true`로 처리하는 순간 KEYS가 기본값으로 나갈 수 있으므로, 키를 정확히 계산해 단건 `@CacheEvict`로 지우는 설계가 먼저라는 쪽이다. 수집기는 SQLite 저장 계층이라 Redis 직접 연결은 약하고, "편한 추상화 기본값이 운영 비용을 숨긴다"는 구조적 유사점만 있다. (글의 주장이며 직접 검증은 아직 안 한 상태.)

## 오늘 정리할 것

1. 내 프로젝트의 `RedisCacheManager` 자동 설정이 어떤 `BatchStrategy`를 쓰는지 `RedisCacheWriter` 소스에서 직접 확인하기.
2. 로컬 Redis에 키 수만 개를 넣고 `KEYS cache::*`와 `SCAN`의 소요 시간을 비교해 보기.
3. WMS 재고 캐시의 무효화 지점(입고 확정·출고 확정)을 적고, 단건 키로 지울 수 있는지 `allEntries`가 필요한지 표로 정리하기.
4. `DEL`과 `UNLINK`의 차이를 `redis-cli`로 큰 키에 실행해 확인해 보기.
