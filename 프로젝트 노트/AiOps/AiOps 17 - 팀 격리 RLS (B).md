---
출처: Claude 대화
작성일: 2026-11-10
tags: [프로젝트, java]
---

# AiOps - 팀 격리 RLS (B)

> 허브: [[AiOps 프로젝트 MOC]]

**11단계, 담당 B(조현우).** PR #23 `Feat/server ai 16 isolation` (스토리 AI-16 = AI-70~75 한 번에). 11/5 머지. **설계자 선행 테스트 `IsolationTest` 8종이 수정 없이 초록**으로 들어갔다.

## 0. 전체 그림: "코드의 팀 번호"가 "DB의 팀 번호"가 되기까지

```
요청 스레드                            DB 커넥션
TenantFilter: 키 → TenantContext.set(7)
   └ @Transactional 메서드 호출
       TenantTransactionManager.doBegin ──▶ BEGIN
                                       ──▶ SELECT set_config('app.tenant_id', '7', true)
       SELECT * FROM error_event       ──▶ RLS: WHERE tenant_id = NULLIF(current_setting(...), '')::bigint
       COMMIT                          ──▶ app.tenant_id 사라짐 (true = 트랜잭션 범위)
finally TenantContext.clear()
```

**연결 고리는 세 개**이고, 하나라도 빠지면 0건이 나온다.

1. `TenantContext`: 자바 쪽 "지금 어느 팀"
2. `TenantTransactionManager`: 트랜잭션이 열릴 때 자바 값을 DB 변수로 옮기는 다리
3. `V2__rls.sql`: DB 변수로 행을 거르는 정책

## 1. AI-70 `TenantContext` + `TenantFilter`

```java
public final class TenantContext {
    private static final ThreadLocal<Long> CURRENT = new ThreadLocal<>();
    public static void set(Long tenantId) {
        if (tenantId == null) throw new IllegalArgumentException(...);   // ① null로 "지우기" 금지
        CURRENT.set(tenantId);
    }
    public static Optional<Long> get()  { return Optional.ofNullable(CURRENT.get()); }   // 없어도 됨
    public static Long require() { ... throw new TenantNotSetException(); }              // 없으면 실패
    public static void clear()   { CURRENT.remove(); }                                    // ② remove
}
```

- ① null을 받으면 "지운 건지 실수인지" 구분이 안 된다. 지우기는 `clear()` 하나로만.
- ② `set(null)`이 아니라 `remove()`. 스레드 풀 스레드의 ThreadLocal 맵에서 항목 자체를 없앤다.
- **순수 static 유틸**이고 Bean이 아니다. 트랜잭션 매니저가 Bean 생성 순서와 상관없이 부를 수 있어야 하기 때문이다.

```java
// TenantFilter.doFilterInternal (/v1/** 에만)
try {
    ResolvedKey key = apiKeyResolver.resolve(request.getHeader(ProtocolConstants.HEADER_API_KEY));
    TenantContext.set(key.tenantId());
    request.setAttribute(ENV_ATTRIBUTE, key.env());       // 컨트롤러가 @RequestAttribute로 꺼냄
    chain.doFilter(request, response);
} catch (InvalidApiKeyException e) {
    response.setStatus(401); response.getWriter().write("{\"error\":\"invalid_api_key\"}");   // ③
} finally {
    TenantContext.clear();                                 // ④ set한 곳이 지운다
}
```

- ③ **필터에서 난 예외는 `@RestControllerAdvice`가 받지 못한다**(필터는 DispatcherServlet 바깥). 그래서 필터가 직접 같은 JSON을 쓴다.
- ④ 예외가 나도 `finally`에서 지운다. 톰캣 스레드는 재사용되므로, 지우지 않으면 다음 요청이 이전 팀을 물려받는다.
- 12단계에서 이 필터는 `ApiKeyAuthFilter`(Spring Security 체인 안)로 흡수된다.

## 2. AI-71 트랜잭션 바인더 (`TenantTransactionManager`)

```java
public class TenantTransactionManager extends JpaTransactionManager {
    static final String SET_TENANT_SQL = "SELECT set_config('app.tenant_id', ?, true)";   // ①

    @Override
    protected void doBegin(Object transaction, TransactionDefinition definition) {
        super.doBegin(transaction, definition);                // ② 커넥션 획득 + BEGIN
        Optional<Long> tenant = TenantContext.get();
        if (tenant.isEmpty()) return;                          // ③ 팀 없으면 아무것도 안 함 → 0건
        try {
            Connection connection = DataSourceUtils.getConnection(getDataSource());   // ④ 같은 커넥션
            try (PreparedStatement ps = connection.prepareStatement(SET_TENANT_SQL)) {
                ps.setString(1, String.valueOf(tenant.get()));
                ps.execute();
            }
        } catch (SQLException | RuntimeException ex) {
            rollbackQuietly();                                 // ⑤ 팀 없는 트랜잭션을 남기지 않음
            doCleanupAfterCompletion(transaction);
            throw new CannotCreateTransactionException("트랜잭션에 팀 번호를 설정하지 못했다", ex);
        }
    }
}
```

| 번호 | 왜 |
|---|---|
| ① | **세 번째 인자 `true` = 트랜잭션 범위.** `false`면 세션(커넥션) 범위라, 커넥션 풀에서 그 커넥션을 받은 **다음 요청(다른 팀)에게 값이 남는다.** 격리의 가장 위험한 한 글자 |
| ② | 부모가 커넥션을 잡고 트랜잭션을 연 **뒤에** 실행해야 같은 트랜잭션 안에 들어간다 |
| ③ | 예외를 던지지 않는다. 팀 없이 열리는 관리용 트랜잭션도 있다. 대신 RLS가 0건을 준다(fail closed) |
| ④ | `DataSourceUtils.getConnection`은 **지금 스레드에 묶인 트랜잭션의 커넥션**을 준다. `dataSource.getConnection()`을 쓰면 다른 커넥션이 와서 설정이 엉뚱한 곳에 들어간다. 그래서 `JpaConfig`에서 `tm.setDataSource(dataSource)`를 해 둔다 |
| ⑤ | 설정에 실패한 채로 트랜잭션을 쓰게 두면 "왜 0건이지?"만 남는다. 아예 실패시킨다 |

`JpaConfig`가 `transactionManager`라는 이름으로 이 Bean을 등록하면, Spring Boot 기본 트랜잭션 매니저는 만들어지지 않는다(`@ConditionalOnMissingBean`). 그래서 **모든 `@Transactional`이 자동으로 이 다리를 지난다.**

## 3. AI-72 RLS 정책 (`V2__rls.sql`)

```sql
ALTER TABLE error_event ENABLE ROW LEVEL SECURITY;
CREATE POLICY tenant_isolation ON error_event
    USING      (tenant_id = NULLIF(current_setting('app.tenant_id', true), '')::bigint)   -- 읽기·수정·삭제 대상
    WITH CHECK (tenant_id = NULLIF(current_setting('app.tenant_id', true), '')::bigint);  -- 쓰기 결과 검사
-- error_group, app_snapshot, ingest_stat, heartbeat_last 도 같은 모양
```

| 조각 | 의미 |
|---|---|
| `current_setting('app.tenant_id', true)` | 변수가 없으면 에러 대신 NULL (`true` = missing_ok) |
| `NULLIF(…, '')` | 한 번 설정됐던 커넥션은 트랜잭션 뒤 **빈 문자열**이 남을 수 있다. 빈 문자열을 bigint로 바꾸면 에러가 나니 NULL로 |
| `tenant_id = NULL` | SQL에서 NULL과의 비교는 항상 거짓 → **0건** |
| `USING` | SELECT·UPDATE·DELETE에서 "보이는 행" |
| `WITH CHECK` | INSERT·UPDATE에서 "써도 되는 행". 없으면 **다른 팀 번호로 저장**이 된다 |

- **FORCE를 걸지 않는다.** 테이블 소유자(`aiops_owner`, Flyway)는 RLS를 무시한다. 그래서 서버는 반드시 소유자가 아닌 `aiops_app`으로 붙는다(1단계에서 계정을 셋으로 나눈 이유).
- 정책에 역할을 지정하지 않았다(PUBLIC). 새 계정이 생겨도 자동으로 격리된다.
- `heartbeat_last`는 `ON CONFLICT DO UPDATE`를 쓰므로 USING과 WITH CHECK가 둘 다 평가된다.

## 4. AI-73 경로 연결 / AI-74 키 캐시 / AI-75 Grafana

**AI-73:** 요청 밖에서 팀 테이블을 만지는 곳마다 같은 모양을 넣었다.

```java
TenantContext.set(tenantId);
try { /* @Transactional 메서드 호출 */ } finally { TenantContext.clear(); }
```

`ErrorProcessor.process`(처리 풀), `ReprocessScheduler`·`RetentionScheduler`(팀 목록을 돌며 팀마다). 서버 계정에 RLS 우회 권한을 주지 않았다(D-082).

**AI-74 키 캐시:** `ApiKeyCache`(`ConcurrentHashMap`, TTL 60초, 상한 10,000). 폐기는 커밋 **뒤에** 캐시에서 지운다.

```java
// ApiKeyService.revoke
key.revoke(); apiKeys.save(key);
TransactionSynchronizationManager.registerSynchronization(new TransactionSynchronization() {
    @Override public void afterCommit() { resolver.evict(keyHash); }   // 커밋 뒤에 지움
});
```

순서가 반대면(먼저 지우고 커밋) 커밋 전에 들어온 요청이 **옛 값(폐기 전)으로 캐시를 다시 채운다.** 메모리 캐시라 서버가 2대가 되면 다른 서버에는 전파되지 않는다는 한계도 주석에 적혀 있다(최대 60초 뒤 반영).

**AI-75 Grafana:** `grafana_ro`는 `BYPASSRLS`로 전체 팀을 보지만, `REVOKE SELECT ON api_key` 후 `GRANT SELECT (id, tenant_id, env, …)`처럼 **민감 컬럼을 뺀 컬럼 단위 권한**만 준다. 컬럼 단위 권한은 나중에 추가한 컬럼에 자동으로 붙지 않으므로, 컬럼을 추가할 때마다 GRANT를 명시해야 한다(V3에서 실제로 그렇게 했다).

## 5. 테스트에 `@Transactional`을 붙이면 안 되는 이유

```java
@Transactional          // ✗ 테스트 트랜잭션이 먼저 열림 → doBegin이 이미 지나감
@Test void test() {
    TenantContext.set(7L);                  // 이미 늦었다. set_config가 안 들어감
    repository.findAll();                   // → 0건
}
```

그래서 RepositoryTest를 내가 고쳐서 넘겼고, A의 테스트 9개도 B가 같은 방식(owner로 넣고, `TenantContext.set` 뒤 `TransactionTemplate`으로 실행)으로 고쳤다. 목적·검사 내용은 그대로이고 팀 합의로 진행했다.

## 6. 머지 후 할 일

`01-roles.sh`가 바뀌어서 로컬 DB를 다시 만들어야 한다: `docker compose … down -v` → `up -d`.

## 7. 내가 알아야 할 것

- **Starter는 영향 없음.** 키만 보내면 서버가 팀을 정한다.
- **LLM(AI-12)은 영향 있음.** `ExplanationService`는 처리 풀 스레드에서 돈다. `ErrorProcessor.process` 안(이미 set된 상태)에서 부르면 되고, 따로 스레드를 만들면 직접 set/clear해야 한다.
- 새 팀 테이블을 만들면 **같은 마이그레이션에 `tenant_isolation` 정책**을 넣는다. `RlsPolicyTest`가 `information_schema`로 빠진 테이블을 잡는다.

## 8. 다음에 볼 키워드

- PostgreSQL RLS: `USING` vs `WITH CHECK`, 소유자 우회, `FORCE ROW LEVEL SECURITY`
- `set_config(…, is_local)`, `current_setting(…, missing_ok)`
- `DataSourceUtils.getConnection`과 트랜잭션 동기화
- `TransactionSynchronization.afterCommit`

## 관련 노트

[[AiOps 16 - 디스코드 알림 (B)]] · [[AiOps 18 - V3 콘솔 스키마 (B)]]
