---
출처: Claude 대화
작성일: 2026-11-12
tags: [프로젝트, java]
---

# AiOps - 관리자 API 기수와 접근 기록 (A)

> 허브: [[AiOps 프로젝트 MOC]]

**PR #38 / #39** — 13단계(관리자 API)의 첫 두 작업. 담당 A.

- **#38 `[AI-87] 관리자 API 호출을 접근 기록에 자동 저장`** — 브랜치 `feat/server-AI-87-admin-access-log`. 커밋 1개(`468b29b`, 9파일 +400). 11/11 13:14 KST 머지(`965e681`).
- **#39 `[AI-82] 관리자 기수 생성·목록 API`** — 브랜치 `feat/server-AI-82-cohort-api`. 커밋 1개(`e9d3cdb`, 9파일 +375). 11/11 15:51 KST 머지(`c8ee552`).

> 코드는 11/11 develop(`c8ee552`) 기준. `AdminGuard`는 12단계에서 B가 만든 것(#31). 명세: Jira AI-18(13단계 전체)·AI-82·AI-87, `v0.3-web-console.md` 3-9·규칙 15, `mvp-requirements.md` M-01·M-06.

## 1. 배운 내용

### 1-1. 관리자 요청 한 건이 지나가는 길

```
브라우저 (AIOPS_SESSION 쿠키 + POST면 X-XSRF-TOKEN 헤더)
 → sessionChain (/api/**)        세션 없음 401 · CSRF 틀림 403   ← 여기서 막히면 기록 없음
 → DispatcherServlet
 → AdminGuard.preHandle          환경변수 GitHub id 목록에 없음 → 403 + false   ← 기록 없음
 → AdminAccessLogInterceptor     preHandle은 기본(true), 하는 일 없음
 → CohortController / AdminAccessLogController
 → (응답 완료)
 → AdminAccessLogInterceptor.afterCompletion → admin_access_log INSERT 1행 (별도 트랜잭션)
```

- **인터셉터(HandlerInterceptor)**: 컨트롤러 앞뒤에 끼워 넣는 스프링 MVC 장치. 필터보다 안쪽이라 "어느 컨트롤러 메서드가 맞았는지"를 안다.
- 등록 순서가 실행 순서다. `AdminGuard`가 `false`를 돌려주면 **그 뒤 인터셉터는 `preHandle`도 `afterCompletion`도 불리지 않는다.** 그래서 403은 자동으로 기록에서 빠진다.
- 컨트롤러는 관리자 여부를 다시 검사하지 않는다. 가드가 했다는 전제다(AI-82 "하지 말 것").

### 1-2. 코드로 보기: 등록 (`WebMvcConfig`)

```java
registry.addInterceptor(adminGuard).addPathPatterns("/api/admin/**");
// AI-87 : AdminGuard 바로 다음에 등록. 팀 API(/api/teams/**)에는 달지 않는다
registry.addInterceptor(adminAccessLogInterceptor).addPathPatterns("/api/admin/**");
```

| 번호 | 이유 |
|---|---|
| 같은 패턴 | 가드와 기록이 **같은 경로 패턴**을 본다. 한쪽만 거치는 관리자 경로가 생기지 않는다(AI-87 규칙) |
| 가드 다음 | 순서가 바뀌면 비관리자 403 시도까지 기록된다. 명세는 "관리자의 조회만 기록" |
| 팀 API 제외 | 팀이 자기 데이터를 보는 건 기록 대상이 아니다 |

### 1-3. 코드로 보기: 기록 인터셉터 (`AdminAccessLogInterceptor.afterCompletion`)

```java
try {
AppUserPrincipal admin = CurrentUser.get();
Long tenantId = teamId(request);

// AI-87 : 실제 주소(/api/admin/teams/7/suspend)가 아니라 맞은 패턴(/api/admin/teams/{teamId}/suspend)을 기록
String pattern = (String) request.getAttribute(HandlerMapping.BEST_MATCHING_PATTERN_ATTRIBUTE);   // ①
if (pattern == null) {
    pattern = request.getRequestURI();   // 맞는 컨트롤러가 없을 때(404)
}

// AI-87 : 처리 못 한 예외로 끝나면 이 시점의 response 상태는 아직 200 일 수 있다 (500 은 나중에 컨테이너가 정함) → 500 으로 기록
int status = response.getStatus();
if (ex != null && status < 400) {                                                                 // ②
    status = 500;
}

accessLogService.record(admin.appUserId(), tenantId, request.getMethod() + " " + pattern + " " + status);   // ③
} catch (RuntimeException e) {
    // AI-87 : 기록 실패는 로그만. 응답은 이미 나갔다
    log.error("관리자 접근 기록 실패", e);                                                          // ④
}
```

| 번호 | 이유 |
|---|---|
| ① | **패턴**을 남긴다. 쿼리 문자열(`?token=...`)도, 경로에 박힌 실제 값도 기록에 들어가지 않는다. 규칙 10(비밀값은 로그·기록에 남기지 않음)을 구조로 지킨다. 같은 API가 한 줄 모양으로 모여서 집계도 쉽다 |
| ② | 명세(`status = response.getStatus()`)보다 한 걸음 더 갔다. 처리 못 한 예외는 컨테이너가 나중에 500으로 바꾸므로, 이 시점 상태는 200일 수 있다. 테스트 `본_요청이_500으로_실패해도_기록은_1행_남는다`로 고정 |
| ③ | 저장 값은 `admin_user_id`, `tenant_id`(경로 변수 `teamId`가 있을 때만), `action` = `"GET /api/admin/cohorts 200"` 한 줄. **요청·응답 본문은 아예 읽지 않는다** — 13단계 조장 초대 응답에 토큰 원문이 들어가기 때문 |
| ④ | `afterCompletion`은 응답이 끝난 뒤라 예외를 던져도 클라이언트에 영향이 없다. 명세대로 로그만 |

`afterCompletion`을 고른 이유: `postHandle`은 컨트롤러가 예외를 던지면 불리지 않는다. `afterCompletion`은 성공·실패 모두 불리고, 응답 상태를 볼 수 있다.

### 1-4. 코드로 보기: 별도 트랜잭션으로 저장 (`AdminAccessLogService.record`)

```java
// AI-87 : 기록 1행 저장. REQUIRES_NEW = 본 요청 트랜잭션과 따로 커밋 → 본 요청이 롤백돼도 기록은 남음
// 비동기(@Async)로 빼지 않음 (유실 가능성). 호출하는 인터셉터가 예외를 잡아 로그만 남김
@Transactional(propagation = Propagation.REQUIRES_NEW)
public void record(Long adminUserId, Long tenantId, String action) {
    repository.save(new AdminAccessLogEntity(adminUserId, tenantId, action));
}
```

| 번호 | 이유 |
|---|---|
| `REQUIRES_NEW` | **전파 속성**: 이미 트랜잭션이 있으면 잠시 멈추고 새 트랜잭션을 연다. 실패한 요청의 롤백에 기록이 같이 휩쓸리지 않는다. (`open-in-view: false`라 afterCompletion 시점엔 보통 바깥 트랜잭션이 없지만, 의도를 코드로 박아 둔 것) |
| `@Async` 안 씀 | INSERT 1행은 싸다. 비동기 큐는 서버가 죽으면 기록이 사라질 수 있다 |
| 다른 Bean | 인터셉터 → 서비스 호출이라 프록시를 거친다. 같은 클래스 안 호출이면 `@Transactional`이 안 먹는다(AiOps 15 - 보관 삭제와 수집 통계 (A)의 Purger와 같은 이유) |

### 1-5. 코드로 보기: 추가만 하는 테이블 (리포지토리 + V4 마이그레이션)

```java
// AI-87 : 관리자 접근 기록. 추가만 하는 테이블이라 JpaRepository 가 아니라 Repository 를 씀
// (JpaRepository 를 쓰면 delete·deleteAll 같은 메서드가 같이 생김). save 와 조회만 둔다. RLS 없음 (D-023)
public interface AdminAccessLogRepository extends Repository<AdminAccessLogEntity, Long> {

    AdminAccessLogEntity save(AdminAccessLogEntity entity);
```

```sql
-- V4: admin_access_log 는 추가만 한다 (AI-87, D-024).
-- aiops_app(서버 계정)은 읽기·INSERT 만 가능하고 UPDATE·DELETE 는 못 한다.
-- 보관 정리가 필요하면 owner 계정으로 수동 (MVP).
-- 01-roles.sh 는 DB 를 처음 만들 때 테이블이 생기기 전에 돌아서 REVOKE 를 거기 쓸 수 없다 → 마이그레이션에 둔다.
REVOKE UPDATE, DELETE ON admin_access_log FROM aiops_app;
```

| 층 | 막는 방법 | 무엇을 막나 |
|---|---|---|
| 코드 | `Repository`(빈 인터페이스)에 `save`·조회만 선언 | 개발자가 실수로 `delete`를 부르는 것 |
| DB | `REVOKE UPDATE, DELETE ... FROM aiops_app` | 코드가 뚫려도(SQL 직접 실행 등) 서버 계정으로는 수정·삭제 불가 |

- **append-only(추가 전용)**: 쓰기만 하고 고치거나 지우지 않는 기록. 감사 기록은 "관리자가 자기 흔적을 지울 수 없다"가 핵심이라 DB 권한으로 막는다.
- 왜 REVOKE가 필요한가: `01-roles.sh`의 `ALTER DEFAULT PRIVILEGES`가 owner가 만드는 **모든 새 테이블**에 `SELECT, INSERT, UPDATE, DELETE`를 aiops_app에 자동으로 준다. 그래서 이 테이블만 따로 빼야 한다. `TRUNCATE`는 기본 권한에 처음부터 없어서 따로 막을 필요가 없다.
- 명세(AI-87)는 `01-roles.sql`에 쓰라고 했다. 하지만 그 스크립트는 DB를 처음 만들 때, **테이블이 생기기 전에** 돈다. 그래서 Flyway(owner 계정으로 실행) V4로 옮겼다. 운영 DB에도 똑같이 적용되므로 더 나은 선택.
- 테스트 `서버_계정은_기록을_추가하고_읽을_수_있지만_수정_삭제는_못_한다`가 실제 aiops_app 계정으로 UPDATE·DELETE가 거부되는 것을 확인한다.
- `admin_access_log`·`cohort`·`tenant`는 RLS(행 수준 보안, DB가 팀별로 행을 걸러 주는 기능)가 없다(D-023, V2 확인). 그래서 관리자 API가 `TenantContext` 없이 읽고 쓸 수 있다. 다른 팀의 **에러 데이터**를 볼 때는 다르다 — 현황 API(W13-5)는 RLS를 우회하지 않고 팀마다 `TenantContext`를 바꿔 조회해야 한다(D-082). 이번 두 PR에는 해당 없음.

### 1-6. 코드로 보기: 기수 생성 검증 순서 (`CohortService.create`)

```java
// 이름이 비어 있음 → 400
String name = request == null || request.name() == null ? "" : request.name().trim();
if (name.isEmpty()) {
    throw new AdminApiException(HttpStatus.BAD_REQUEST, "COHORT_NAME_REQUIRED", "기수 이름이 필요합니다");
}
// 종료일이 시작일보다 앞 → 400 (같은 날은 허용)
if (request.startDate() != null && request.endDate() != null && request.endDate().isBefore(request.startDate())) {
    throw new AdminApiException(HttpStatus.BAD_REQUEST, "COHORT_DATE_ORDER", "종료일이 시작일보다 빠릅니다");
}
// 같은 이름이 이미 있음 → 409
if (cohorts.existsByName(name)) {
    throw new AdminApiException(HttpStatus.CONFLICT, "COHORT_NAME_DUPLICATE", "이미 있는 기수 이름입니다");
}
```

| 번호 | 이유 |
|---|---|
| 싼 검사 먼저 | 이름·날짜는 DB 없이 판단. 중복 검사(DB 조회)는 마지막 |
| `trim()` | `" 2026-3기 "`와 `"2026-3기"`를 같은 이름으로 본다 |
| 날짜 null 허용 | V3 `start_date`·`end_date`가 NULL 허용이라 맞춤 |
| `AdminApiException` | 상태 코드 + 에러 코드를 들고 다니는 예외. `AdminExceptionHandler`가 `{ "error": 코드, "message": 설명 }`으로 바꾼다. AI-82가 "13단계 공통 틀을 여기서 잡는다"고 한 부분 |

`AdminExceptionHandler`는 `@RestControllerAdvice(basePackages = "dev.aiops.server.controller.admin")` — **패키지로 범위를 좁힌** 전역 예외 처리기. 수집 API(`IngestExceptionHandler`)의 에러 형식은 건드리지 않는다.

예외가 핸들러에서 처리되면 `afterCompletion`의 `ex`는 null이고 상태는 409·400으로 이미 정해져 있다. 그래서 기록에도 `POST /api/admin/cohorts 409`처럼 정확히 남는다.

### 1-7. 코드로 보기: 기수별 팀 수를 쿼리 한 번으로 (`list`)

```java
// AI-82 : 기수별 팀 수를 쿼리 한 번으로 (tenant 도 RLS 없음). 한 줄 = [cohortId, 팀 수]. 팀이 없는 기수는 안 나옴
@Query("select t.cohortId, count(t) from TenantEntity t where t.cohortId is not null group by t.cohortId")
List<Object[]> countTeamsByCohort();
```

```java
Map<Long, Long> teamCounts = new HashMap<>();
for (Object[] row : cohorts.countTeamsByCohort()) {
    teamCounts.put(((Number) row[0]).longValue(), ((Number) row[1]).longValue());
}
return cohorts.findAllByOrderByIdDesc().stream()
        .map(c -> new CohortResponse(c.getId(), c.getName(), c.getStartDate(), c.getEndDate(),
                teamCounts.getOrDefault(c.getId(), 0L)))
        .toList();
```

- 기수마다 `count` 쿼리를 따로 날리면 **N+1 문제**(목록 1번 + 항목 수만큼 N번)가 된다. GROUP BY 한 번 + 맵으로 합쳐 쿼리 2번에 끝낸다.
- 팀이 없는 기수는 GROUP BY 결과에 안 나오므로 `getOrDefault(..., 0L)`.
- `((Number) row[0])`: JPQL `count`는 `Long`, id도 `Long`이지만 드라이버·방언에 따라 타입이 달라질 수 있어 `Number`로 받는 안전한 습관.

### 1-8. 테스트 훑기

| 테스트 | 확인하는 것 |
|---|---|
| `AdminAccessLogTest` (8개) | 3번 호출 → 3행, `teamId` 경로 → tenant_id, 비관리자 403·세션 없음 401 → 0행, 500 실패도 1행, 응답 비밀값이 기록에 없음, 팀 API 0행, 조회 API도 기록됨, aiops_app UPDATE·DELETE 거부 |
| `CohortControllerTest` (8개) | 201, 409, 날짜 역전 400, 이름 빈칸·누락 400, 날짜 형식 400(`INVALID_REQUEST`), 최신 순 + teamCount, 비관리자 403·401, 기수 생성도 접근 기록에 남음 |

- 기록은 응답이 나간 **뒤에** 저장되므로 테스트가 `await().atMost(5, SECONDS)`로 기다린다(Awaitility). 바로 세면 가끔 0행이다.
- 실제 관리자 API가 아직 없어서 `@RestController static class TestEndpoints`로 **테스트 전용 관리자 경로**(`/api/admin/_test/...`)를 만들어 썼다.

## 2. 리뷰 메모

| 항목 | 내용 | 심각도 |
|---|---|---|
| 기수 이름 중복 검사가 DB로 보장되지 않음 | `CohortService.create`는 `existsByName` → `save` 두 단계. V3 `cohort.name`에 UNIQUE가 없다. 관리자 둘이 같은 이름을 거의 동시에 만들면 둘 다 통과해 같은 이름 기수가 2개 생긴다(검사와 저장 사이 틈, TOCTOU). 409 약속이 코드로만 지켜진다. `UNIQUE(name)` 마이그레이션 + `DataIntegrityViolationException` → 409 변환을 권함 | 중간 |
| 기록 저장 실패 시 관리자 동작은 그대로 성공 | `afterCompletion`의 `catch (RuntimeException e)`가 로그만 남긴다. DB 장애 등으로 INSERT가 실패하면 "기록 없는 관리자 동작"이 생긴다. 응답이 이미 나간 뒤라 막을 방법이 없고, **명세(AI-87 2번)가 정한 동작**이다. 규칙 15의 "전부 기록"과 긴장 관계라는 것만 알아 두기. 로그 알림(ERROR 감시)으로 보완 가능 | 메모 |
| 막힌 시도는 기록되지 않음 | 비관리자 403(가드), 세션 없음 401, CSRF 실패 403(보안 필터)은 전부 기록 밖. 명세가 "관리자의 조회만 기록"이라 의도대로. 다만 "누가 관리자 API를 두드렸나"는 이 테이블로 알 수 없다(서버 로그·Caddy 접근 로그에 의존) | 메모 |
| 비밀값 기록 여부 | 본문·쿼리 문자열은 저장 안 함, 경로도 패턴으로 저장 → 규칙 10 충족. 예외: 맞는 패턴이 없을 때 `getRequestURI()`(쿼리 제외 실제 경로)로 대체. 다만 스프링이 404 경로를 정적 리소스 핸들러(`/**`)로 매칭해 이 분기가 실제로 타는지는 **확인 못 함** | 낮음 |
| 테스트: 쿼리 문자열 비밀값 | `응답에_있는_비밀값은_기록에_없다`는 응답 본문만 본다. `?token=SECRET` 같은 쿼리·경로 변수 비밀값 테스트는 없다. 지금 구조상 안전하지만 회귀 방지용으로 1개 있으면 좋다. 명세의 "owner-invite 응답 토큰" 테스트는 API가 아직 없어 가짜 경로로 대신함 → W13-3 때 실제 경로로 한 번 더 | 낮음 |
| 관리자 API 에러 형식이 완전히 통일되지 않음 | `AdminExceptionHandler`는 `AdminApiException`과 본문 파싱 실패만 잡는다. `GET /api/admin/access-log?from=잘못된값`의 타입 변환 실패(`MethodArgumentTypeMismatchException`)는 스프링 기본 400 응답이라 `{ error, message }` 모양이 아니다 | 낮음 |
| `CohortRepository`는 `JpaRepository` | 접근 기록 쪽은 삭제 메서드를 숨기려고 `Repository`를 썼는데, 기수는 `JpaRepository`라 `deleteById` 등이 열려 있다. 주석 "고정 조건 메서드만 둠"과 살짝 어긋남. 명세상 삭제 금지는 API 기준이라 기능 문제는 아님 | 메모 |
| 명세와 다른 곳 (모두 타당) | ① REVOKE를 `01-roles.sql` 대신 Flyway V4로(테이블 생성 후 실행돼야 함) ② 예외 시 상태를 500으로 보정 ③ 생성 응답에 `teamCount: 0` 추가 ④ 파일 위치가 AI-18의 `admin/` 대신 D-088 구조(`security/`, `service/`, `controller/admin/`, `model/repository/`) | 메모 |
| 시각을 자바에서 찍음 | `AdminAccessLogEntity` 생성자가 `Instant.now()`로 `at`을 채운다. V3에는 `DEFAULT now()`가 있지만 쓰이지 않는다. 서버 시계 기준이라는 점만 알아 두면 됨 | 메모 |
| "중복 커밋" 질문 | **중복 아님.** `e9d3cdb`는 #39 브랜치의 유일한 커밋, `c8ee552`는 GitHub에서 만든 **머지 커밋**(부모 2개: `965e681`, `e9d3cdb`, 커미터 GitHub, 서명 있음). 머지 메시지를 기본 `Merge pull request #39 ...` 대신 PR 제목으로 바꿔서 제목이 같아 보인다. #38도 같다(`468b29b` ↔ 머지 `965e681`). `git diff e9d3cdb c8ee552`는 비어 있다(트리 동일). 단점: 머지 메시지에 PR 번호가 없어 `git log`만으로 #38·#39를 찾기 어렵다. PR 번호는 git에서 직접 확인 못 함 | 메모 |
| 쌓인 PR(stacked PR) | #39 브랜치는 develop이 아니라 `468b29b`(#38 커밋) 위에서 시작했다. #38을 일반 머지로 넣어서 문제없었다. #38을 스쿼시 머지했다면 #39에 같은 변경이 한 번 더 딸려 와 진짜 중복이 됐을 것. AI-82의 "기록 인터셉터 작업과 같이 또는 그 뒤에 머지" 조건은 지켜짐 | 메모 |

## 3. 더 나아가 알면 좋은 것

- `HandlerInterceptor`의 `preHandle` / `postHandle` / `afterCompletion` 호출 조건 (false를 돌려주면 누가 불리나)
- `HandlerMapping.BEST_MATCHING_PATTERN_ATTRIBUTE`, `URI_TEMPLATE_VARIABLES_ATTRIBUTE`
- 트랜잭션 전파 `REQUIRES_NEW`와 `REQUIRED`의 차이, `open-in-view`
- 감사 로그(audit log)와 append-only — DB `GRANT`/`REVOKE`, `ALTER DEFAULT PRIVILEGES`
- Spring Data `Repository` vs `CrudRepository` vs `JpaRepository` (노출 메서드 줄이기)
- 검사 후 저장 경쟁(TOCTOU)과 UNIQUE 제약 + 예외 변환
- `@RestControllerAdvice(basePackages = ...)`로 예외 처리 범위 좁히기
- N+1 문제와 GROUP BY 한 번 + Map 합치기
- GitHub 머지 방식 3가지(merge commit / squash / rebase)와 쌓인 PR

## 관련 노트

[[AiOps 27 - 팀 API 초대와 팀원 (B)]] · [[AiOps 29 - 어펜더 장착과 비활성 처리]]
