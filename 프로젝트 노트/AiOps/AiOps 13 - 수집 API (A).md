---
출처: Claude 대화
작성일: 2026-11-10
tags: [프로젝트, java]
---

# AiOps - 수집 API (A)

> 허브: [[AiOps 프로젝트 MOC]]

**2단계, 담당 A(김지환).** PR #12 `[AI-30] 키 인증` · #13 `[AI-31] 이벤트 수집` · #14 `[AI-32] 커밋 후 처리 요청` · #15 `[AI-33] hello·heartbeat` · #20 `[AI-34] ingest.http`. 11/3~11/4 머지. Starter가 보내는 요청을 받는 서버 입구 전체다.

> 코드는 **11/10 develop 기준**이다. 11단계(#23)에서 B가 RLS에 맞춰 일부를 고쳤으므로(키 확인이 `TenantFilter`로 이동, 팀은 `TenantContext`에서 꺼냄) PR 당시 코드와 조금 다르다. 바뀐 곳은 따로 표시했다.

## 0. 요청 하나가 지나가는 길

```
POST /v1/events  (헤더 X-AIOPS-KEY, 본문 EventBatch)
 ① IngestBodySizeFilter     본문 1MB 넘으면 413                    (#13)
 ② TenantFilter             키 → 팀 → TenantContext.set           (#23, 원래 #12·#13의 컨트롤러 안)
     └ ApiKeyResolver       해시 → 캐시 → DB → ResolvedKey          (#12, 캐시는 #23)
 ③ IngestController         validate → store → 202                (#13)
 ④ IngestService.store      @Transactional 한 번에:                (#13)
       error_event 저장 · ingest_stat 누적 · heartbeat_last 갱신 · ErrorsStored 발행
 ⑤ 커밋 → ErrorsStoredListener → ErrorProcessor.process (@Async)   (#14 → 6단계)
```

## 1. #12 키 인증 (AI-30)

### 코드: 키를 해시로 바꾸기

```java
public static String sha256Hex(String raw) {
    MessageDigest digest = MessageDigest.getInstance("SHA-256");
    byte[] hashBytes = digest.digest(raw.getBytes(StandardCharsets.UTF_8));  // ① 문자 인코딩을 UTF-8로 고정
    return HexFormat.of().formatHex(hashBytes);                              // ② 32바이트 → 소문자 hex 64자
}
```

- **DB에는 원문이 없고 해시만 있다**(`api_key.key_hash CHAR(64)`). 그래서 들어온 키도 같은 방식으로 해시해서 비교한다.
- ① 인코딩을 고정하지 않으면 서버 OS 기본값에 따라 해시가 달라질 수 있다.
- ② `HexFormat`(Java 17)은 `String.format("%02x")`를 반복하는 것보다 짧고 빠르다. 소문자로 고정해야 DB 값과 같다.

### 코드: 키 → 팀 (`ApiKeyResolver.resolve`)

```java
if (rawHeaderValue == null || rawHeaderValue.isBlank())
    throw new InvalidApiKeyException("invalid api key");       // ① 헤더가 없으면 DB까지 가지 않는다

String keyHash = ApiKeyHasher.sha256Hex(rawHeaderValue);
ResolvedKey cached = cache.get(keyHash);                        // ② (#23에서 추가) 60초 캐시
if (cached != null) return cached;

ApiKeyEntity key = apiKeyRepository.findByKeyHashAndRevokedAtIsNull(keyHash)   // ③ 폐기 안 된 키만
        .orElseThrow(() -> {
            log.warn("api key rejected hash={}", keyHash.substring(0, 8));     // ④ 원문 대신 해시 앞 8자
            return new InvalidApiKeyException("invalid api key");               // ⑤ 없음·폐기 같은 메시지
        });
ResolvedKey resolved = new ResolvedKey(key.getTenantId(), key.getEnv(), key.getId());
cache.put(keyHash, resolved);                                   // ⑥ 성공한 키만 캐시
return resolved;
```

| 번호 | 왜 |
|---|---|
| ③ | 메서드 이름 자체가 조건이다(`…AndRevokedAtIsNull`). 폐기 판단을 SQL에 맡긴다 |
| ④ | 규칙 10: 키 원문은 로그에 남기지 않는다. 앞 8자면 어느 키인지는 구분된다 |
| ⑤ | 없는 키와 폐기된 키를 다르게 알려 주면 "이 키는 예전에 있었다"는 정보가 샌다 |
| ⑥ | 실패한 키를 캐시하면(음성 캐싱) 새로 발급한 키가 60초 동안 401이 된다 |

**인증 판단은 이 클래스 한 곳에만** 있다. 다른 곳에 키 검증을 복사하지 않는다는 주석이 붙어 있다. 12단계 `ApiKeyAuthFilter`도 이 클래스를 호출만 한다.

### 코드: 예외 → 401

```java
@RestControllerAdvice
public class IngestExceptionHandler {
    @ExceptionHandler(InvalidApiKeyException.class)
    public ResponseEntity<Map<String, String>> handleInvalidApiKey(InvalidApiKeyException e) {
        return ResponseEntity.status(HttpStatus.UNAUTHORIZED).body(Map.of("error", "invalid_api_key"));
    }
}
```

예외 메시지(`e.getMessage()`)를 응답에 넣지 않는다. 응답은 항상 같은 JSON이다.

## 2. #13 이벤트 수집 (AI-31)

### 코드: 컨트롤러는 세 줄

```java
@PostMapping(ProtocolConstants.PATH_EVENTS)                    // "/v1/events" — Starter와 같은 상수
public ResponseEntity<Void> postEvents(
        @RequestAttribute(TenantFilter.ENV_ATTRIBUTE) String env,   // (#23) 필터가 키로 정한 env
        @RequestBody EventBatch batch) {
    ingestService.validate(batch);      // 100개 넘으면 TooManyEventsException → 400
    ingestService.store(env, batch);    // 저장
    return ResponseEntity.accepted().build();   // 202, 본문 없음
}
```

- **env를 본문에서 믿지 않는다.** 본문의 `batch.env()`가 아니라 **키에 붙은 env**를 쓴다. local 키로 prod 데이터를 넣을 수 없다. 둘이 다르면 경고만 남긴다.
- **202 Accepted** = "받았고, 처리는 나중에". 그룹화·LLM·디스코드를 기다리지 않는다.

### 코드: 저장은 한 트랜잭션 (`IngestService.store`)

```java
@Transactional
public void store(String env, EventBatch batch) {
    Long tenantId = TenantContext.require();                        // (#23) 팀은 필터가 정한 값만

    List<ErrorEventEntity> rows = new ArrayList<>();
    for (ErrorEvent event : batch.events())
        rows.add(new ErrorEventEntity(tenantId, env, toJson(event), appName, appCommit, hostHash));  // ① payload = JSON 통째로
    List<Long> eventIds = errorEventRepository.saveAll(rows).stream().map(ErrorEventEntity::getId).toList();

    ingestStatRecorder.record(tenantId, env, batch.events().size(), batch.droppedCount());  // ② 통계 (#22)
    heartbeatRecorder.touch(tenantId, env, hostHash, appName, null);                         // ③ 살아 있음
    if (!eventIds.isEmpty())
        publisher.publishEvent(new ErrorsStored(tenantId, eventIds));                       // ④ "저장됐다" 방송
}
```

| 번호 | 왜 |
|---|---|
| ① | 이벤트 필드를 컬럼으로 풀지 않고 **jsonb에 통째로** 둔다. protocol에 필드가 추가돼도 테이블을 고칠 필요가 없다 |
| ② | 받은 수·Starter가 버린 수. 같은 트랜잭션이라 저장이 실패하면 통계도 취소된다 |
| ③ | 에러 묶음도 "살아 있다"는 신호로 친다(D-086). 시작 시각은 모르니 `null` |
| ④ | 처리를 여기서 직접 부르지 않고 **이벤트를 발행**만 한다. 실제 호출은 커밋 뒤(#14) |

`toJson`에 try/catch가 없는 이유: **Boot 4의 Jackson 3는 `writeValueAsString`이 unchecked 예외**를 던진다(Jackson 2는 checked `JsonProcessingException`). 서버는 Jackson을 써도 된다. Starter만 금지다(D-085).

### 코드: 본문 크기 필터

```java
@Override
protected boolean shouldNotFilter(HttpServletRequest request) {
    return !ProtocolConstants.PATH_EVENTS.equals(request.getRequestURI());   // /v1/events만 검사
}
@Override
protected void doFilterInternal(...) {
    if (request.getContentLengthLong() > maxBytes) {          // 헤더의 크기만 보고, 본문은 읽지 않는다
        response.setStatus(413);
        response.getWriter().write("{\"error\":\"payload_too_large\"}");
        return;                                               // chain.doFilter를 부르지 않음 = 여기서 끝
    }
    chain.doFilter(request, response);
}
```

`OncePerRequestFilter`는 요청 하나에 한 번만 도는 필터다. 필터는 컨트롤러보다 앞에 있어서, 큰 본문을 **읽기 전에** 거절할 수 있다.

## 3. #14 커밋 후 처리 요청 (AI-32)

```java
@TransactionalEventListener(phase = TransactionPhase.AFTER_COMMIT)   // 커밋된 뒤에만 호출
public void onErrorsStored(ErrorsStored event) {
    errorProcessor.process(event.tenantId(), event.eventIds());      // @Async → 바로 돌아온다
}
```

- `@EventListener`였다면 `publishEvent` 순간 **트랜잭션 안에서** 바로 실행된다. 그러면 아직 커밋되지 않은 행을 다른 스레드가 읽으러 가서 못 찾을 수 있다.
- `AFTER_COMMIT`이면 **롤백되면 호출되지 않는다.** 테스트 2개(커밋 → 1번, 롤백 → 0번)가 이것만 확인한다.
- `ErrorsStored`에는 엔티티가 아니라 **id 목록만** 담는다. 처리 스레드는 자기 트랜잭션에서 DB를 다시 읽는다(엔티티는 스레드·트랜잭션을 넘기면 안 된다).

## 4. #15 hello·heartbeat (AI-33)

### 코드: 하나로 통일한 `touch`

```sql
INSERT INTO heartbeat_last (tenant_id, env, host_hash, app_name, started_at, last_seen_at)
VALUES (:tenantId, :env, :hostHash, :appName, CAST(:started AS timestamptz), now())
ON CONFLICT (tenant_id, env, host_hash)                       -- ① 팀·env·호스트당 1행
DO UPDATE SET last_seen_at = now(),
              app_name   = COALESCE(EXCLUDED.app_name,   heartbeat_last.app_name),
              started_at = COALESCE(EXCLUDED.started_at, heartbeat_last.started_at)   -- ② null이면 기존 값 유지
```

| 호출하는 곳 | started | 결과 |
|---|---|---|
| hello (`HelloService.storeHello`) | `now()` | 시작 시각 기록 + app_snapshot 1행 |
| heartbeat (`recordHeartbeat`) | `null` | last_seen만 갱신 |
| 이벤트 수집 (`IngestService.store`) | `null` | last_seen만 갱신 |

- ① 행이 없으면 만들고, 있으면 갱신한다(upsert). "조회 → 있으면 UPDATE, 없으면 INSERT"를 코드로 하면 동시에 두 요청이 오면 행이 두 개 생긴다. DB 한 문장이면 안전하다.
- ② `EXCLUDED`는 "넣으려다 충돌한 새 값"이다. 새 값이 null이면 기존 값을 쓴다.
- `CAST(:started AS timestamptz)`: null을 넘기면 Postgres가 타입을 몰라서 에러가 난다. 캐스트로 알려 준다.
- `hostHash`가 없으면 기록하지 않는다(`host_hash`가 NOT NULL).

## 5. #20 수동 요청 모음 (AI-34)

`server/http/ingest.http`에 6개 요청(202, 401×2, 400, 413, hello 202)이 있다. IntelliJ에서 Run all로 서버 쪽을 손으로 확인할 수 있다. Jira의 키(`aiops_local_dev_key`)와 필드명(`apiVersion`, `frames`)이 틀려서 **실제 시드 키(`aiops_l_local-dev-key-0001`)와 protocol 기준으로** 썼다. Jira 쪽은 아직 고치지 않았다.

## 6. 리뷰 메모

| 항목 | 내용 | 조치 |
|---|---|---|
| 본문 크기 필터 | `Content-Length`만 본다. **chunked 전송**(길이 헤더 없음, 값 -1)은 통과한다. Starter는 `ofString`이라 길이를 보내지만, 악의적인 요청은 막지 못한다 | 10단계 Caddy에서 `request_body max_size`로 한 번 더 막기 |
| 정지 팀 키 | `ApiKeyResolver` 5번 주석: 정지된 팀(SUSPENDED)의 키 거부는 아직 없음 | 13단계(팀 정지 API) 때 추가 |
| HeartbeatRecorder 범위 | AI-31에서 먼저 만들고 AI-33에서 시그니처 정리 | 설계자 승인(1안) |

## 7. 내가 알아야 할 것 (Starter 쪽)

- Starter `HttpTransport`(AI-37)는 헤더 `X-AIOPS-KEY`, 경로 `/v1/events`·`/v1/hello`·`/v1/heartbeat`를 `ProtocolConstants`로 쓴다. 서버와 같은 상수다.
- 서버는 **202**를 준다. Starter는 2xx면 성공으로 본다.
- **101개 이상이면 400**이므로 Starter 전송 스레드(AI-38)는 한 묶음을 100개 이하로 잘라야 한다.
- Starter가 `droppedCount`를 보내면 ②를 거쳐 `ingest_stat.dropped_count`에 쌓인다.

## 8. 다음에 볼 키워드

- `@TransactionalEventListener(AFTER_COMMIT)` vs `@EventListener`
- `ON CONFLICT … DO UPDATE`와 `EXCLUDED`
- `OncePerRequestFilter`와 `shouldNotFilter`
- Jackson 2(checked) vs Jackson 3(unchecked) 예외

## 관련 노트

[[AiOps 12 - 이벤트 버퍼 BoundedEventBuffer]] · [[AiOps 14 - 처리 풀과 그룹화 (A)]]
