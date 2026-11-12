---
출처: Claude 대화
작성일: 2026-11-12
tags: [프로젝트, java]
---

# AiOps - 팀 API 초대와 팀원 (B)

> 허브: [[AiOps 프로젝트 MOC]]

**PR #34 / #35 / #32** — 셋 다 B(조현우), 11/10 오후 develop 머지.
- #34 `[AI-105] 초대 발급(issue)·수락 (조장이면 팀 ACTIVE, next=key-guide)` — `feat/server-AI-105-invitation-accept`, 11/10 15:11 KST. 11파일 +553
- #35 `[AI-89] 팀원 초대 링크 발급·목록·무효화, 팀원 목록·내보내기` — `feat/server-AI-89-member-invite`, 11/10 15:24 KST. 14파일 +614
- #32 `[AI-93] 디스코드 연결 컨트롤러 (/api/discord/connect·callback)` — `feat/server-AI-93-discord-join-controller`, 11/10 14:52 KST. 6파일 +328

14단계(AI-19) 팀 API 중 키 발급(AI-88)을 뺀 부분과, 15단계에서 남겨 둔 디스코드 연결 컨트롤러다.

## 1. 배운 내용

### 1-1. 전체 흐름

```
[관리자] AI-84(A, 아직) → InvitationService.issue(teamId, OWNER, 1, 7일, adminId)
   → 응답에 1회: <console>/invite/<원문 43자>       DB에는 sha256Hex(원문)만
[조장] 링크 열기 → GitHub 로그인 → POST /api/invitations/{token}/accept      (#34)
   → 해시로 찾기 → 만료·횟수 검사 → 조건부 UPDATE used_count+1
   → membership(OWNER) → 팀 WAITING_OWNER → ACTIVE → { next: "key-guide" }
[조장] POST /api/teams/{id}/invitations {maxUses:10}  @RequireOwner          (#35)
   → issueMemberInvite → 같은 issue(..., MEMBER, 10, 7일, 조장id)
[팀원] 링크 수락 → membership(MEMBER) → { next: "errors" }                   (#34)
[팀원] [디스코드 연결] GET /api/discord/connect?teamId= → 디스코드 동의 → callback (#32)
[조장] DELETE /api/teams/{id}/members/{userId}  @RequireOwner                 (#35)
   → membership 삭제 즉시 커밋 → 그 사람 다음 요청 403 → 디스코드 역할 회수
```

경로가 두 종류다. 수락은 `/api/invitations/**`, 나머지는 `/api/teams/{teamId}/**`. 수락하는 사람은 **아직 멤버가 아니다.** 팀 경로에 두면 MembershipGuard(팀 소속을 확인하는 인터셉터)가 403으로 막아서 영원히 수락할 수 없다.

### 1-2. 코드로 보기: 토큰 발급 `issue`

```java
private static final SecureRandom RANDOM = new SecureRandom();   // getInstanceStrong()은 리눅스에서 멈출 수 있어 쓰지 않는다
private static final Base64.Encoder TOKEN_ENCODER = Base64.getUrlEncoder().withoutPadding();
...
@Transactional
public Issued issue(Long tenantId, MemberRole role, int maxUses, Duration ttl, Long createdBy) {
    ...
    byte[] bytes = new byte[32];
    RANDOM.nextBytes(bytes);
    String raw = TOKEN_ENCODER.encodeToString(bytes);                       // ①

    Instant expiresAt = Instant.now().plus(ttl);
    InvitationEntity saved = invitations.save(
            new InvitationEntity(tenantId, ApiKeyHasher.sha256Hex(raw), role, maxUses, expiresAt, createdBy));   // ②
    log.info("초대 발급 teamId={} role={} maxUses={} by={}", tenantId, role, maxUses, createdBy);   // 원문 없음
    return new Issued(saved.getId(), raw, inviteUrl(raw), expiresAt, maxUses);
}

public record Issued(long invitationId, String rawToken, String inviteUrl, Instant expiresAt, int maxUses) {
    @Override
    public String toString() {   // 실수로 로그에 찍혀도 원문이 나가지 않게                 ③
        return "Issued[invitationId=" + invitationId + ", expiresAt=" + expiresAt + ", maxUses=" + maxUses + "]";
    }
}
```

| 번호 | 이유 |
|---|---|
| ① | 32바이트 = 256비트 난수. base64url(URL에 그대로 넣을 수 있는 `-`·`_` 쓰는 base64)에 패딩 `=`을 빼면 정확히 43자. `getInstanceStrong()`은 리눅스에서 `/dev/random`을 기다리느라 요청이 멈출 수 있어 11/10 합의대로 `new SecureRandom()` |
| ② | DB에는 SHA-256 해시만. DB가 새도 링크를 만들 수 없다. 해시 함수는 API 키와 같은 `ApiKeyHasher`를 재사용 |
| ③ | record는 `toString`을 자동으로 만들어 **모든 필드를 찍는다**(19번 노트의 DiscordProperties와 같은 함정). 원문이 든 필드를 빼고 덮어썼다 |

권한 판단은 `issue` 안에 없다. 관리자(A, AI-84)도 조장(AI-89)도 이 메서드를 그대로 부르게 하려는 것이다. 권한은 부르는 쪽(컨트롤러·가드)이 본다.

### 1-3. 코드로 보기: 수락과 조건부 UPDATE

```java
// 사용 횟수 +1 — 조건부 UPDATE 한 번이라 같은 토큰을 동시에 수락해도 max_uses를 넘지 않는다.
@Modifying(flushAutomatically = true, clearAutomatically = true)
@Query(value = "UPDATE invitation SET used_count = used_count + 1 "
        + "WHERE id = :id AND used_count < max_uses AND expires_at > now()", nativeQuery = true)
int incrementUsedCount(@Param("id") Long id);
```

```java
InvitationEntity invitation = invitations.findByTokenHash(ApiKeyHasher.sha256Hex(rawToken))
        .orElseThrow(InvitationNotFoundException::new);                       // ① 404
if (!invitation.getExpiresAt().isAfter(Instant.now())) {
    throw new InvitationGoneException("expired");                             // 410
}
if (invitation.getUsedCount() >= invitation.getMaxUses()) {
    throw new InvitationGoneException("used up");                             // 410
}
...
MembershipEntity existing = memberships.findByUserIdAndTenantId(userId, teamId).orElse(null);
if (existing != null) {
    return response(tenant, existing.getRole());                              // ② 이미 멤버
}
if (invitations.incrementUsedCount(invitation.getId()) == 0) {
    throw new InvitationGoneException("used up");                             // ③
}
memberships.save(new MembershipEntity(userId, teamId, invitation.getRole()));
if (invitation.getRole() == MemberRole.OWNER) {
    tenant.activateByOwner();   // WAITING_OWNER → ACTIVE (정지된 팀은 그대로)
    tenants.save(tenant);                                                     // ④
}
```

| 번호 | 이유 |
|---|---|
| ① | 원문으로는 찾지 못한다. 받은 원문을 다시 해시해서 비교한다. 없으면 404, 만료·소진이면 410(Gone, "있었지만 이제 없음") |
| ② | 이미 멤버면 횟수를 쓰지 않고 지금 역할로 응답. 팀원 링크 10명 중 한 사람이 두 번 눌러도 9명 몫이 남는다 |
| ③ | **"읽고 +1 저장"은 동시 요청에 뚫린다.** 두 요청이 둘 다 `used_count=0`을 읽고 둘 다 1을 저장하면 1회용 링크로 조장이 둘 생긴다. 조건을 `WHERE`에 넣은 UPDATE 한 문장은 DB가 행 잠금으로 줄을 세운다. 두 번째는 영향 행 0 → 410 |
| ④ | `clearAutomatically = true`가 UPDATE 뒤에 영속성 컨텍스트(JPA가 읽은 엔티티를 들고 있는 1차 캐시)를 비운다. 그래서 `tenant`는 더 이상 관리 대상이 아니고, 값만 바꾸면 저장되지 않는다(변경 감지 안 됨). `save`(=merge)를 명시적으로 부르는 이유 |

`expires_at > now()`까지 UPDATE에 넣어서, 앞의 자바 검사와 UPDATE 사이에 만료되는 경우도 막았다. 합의안(`used_count < max_uses`)보다 한 조건 더 엄격하다.

응답 `next`는 상수다.

```java
static final String NEXT_OWNER = "key-guide";   // D-092: 키는 관리자가 디스코드 DM으로
static final String NEXT_MEMBER = "errors";
```

AI-105 원래 명세는 `"issue-key"`였다. D-092(키는 관리자가 발급)로 조장이 키를 직접 받을 화면이 없어져 `"key-guide"`로 바뀌었다. 콘솔이 `role`을 보고 갈 곳을 고르지 않게, **갈 곳을 백엔드가 정해 준다**(규칙 13: 권한 판단은 백엔드에서만).

### 1-4. 코드로 보기: 같은 사람이 동시에 두 번 누르면

```java
@PostMapping("/api/invitations/{token}/accept")
public AcceptResponse accept(@PathVariable String token) {
    Long userId = CurrentUser.get().appUserId();
    try {
        return invitationService.accept(token, userId);
    } catch (DataIntegrityViolationException e) {
        // 같은 사람이 같은 링크를 동시에 두 번 누른 경우: 먼저 끝난 쪽이 멤버를 만들었다 → 이미 멤버로 응답
        return invitationService.accept(token, userId);
    }
}
```

- `membership`에 `UNIQUE (user_id, tenant_id)`가 있다. 두 요청이 둘 다 "아직 멤버 아님"을 보고 INSERT하면 늦은 쪽이 제약 위반으로 터진다.
- 늦은 쪽 트랜잭션은 통째로 롤백된다(횟수 +1도 취소). 컨트롤러가 **새 트랜잭션으로 한 번 더** 부르면 이번에는 ②의 "이미 멤버"로 끝난다.
- 재시도를 서비스 안이 아니라 컨트롤러에 둔 이유: 서비스 안에서 잡으면 이미 "롤백만 가능" 표시가 붙은 트랜잭션 안이라 이어서 쓸 수 없다.

### 1-5. 코드로 보기: 팀원 링크 발급·무효화와 tenant_id

```java
@RequireOwner
@PostMapping("/api/teams/{teamId}/invitations")
public ResponseEntity<?> issue(@PathVariable Long teamId, @RequestBody(required = false) CreateInviteRequest body) {
    int maxUses = (body == null || body.maxUses() == null) ? MAX_USES_DEFAULT : body.maxUses();
    if (maxUses < 1 || maxUses > MAX_USES_LIMIT) {
        return ResponseEntity.badRequest().body(Map.of("error", "invalid_max_uses"));   // ①
    }
    ...
}
```

```java
// 이 팀의 링크 1개 (다른 팀 링크 id를 넣어도 안 나온다, AI-89)
Optional<InvitationEntity> findByIdAndTenantId(Long id, Long tenantId);              // ②
...
public boolean expire(Long tenantId, Long invitationId) {
    return invitations.findByIdAndTenantId(invitationId, tenantId)
            .map(i -> {
                i.expireNow();                                                       // ③
                invitations.save(i);
                return true;
            })
            .orElse(false);
}
```

| 번호 | 이유 |
|---|---|
| ① | 1~50, 비우면 10. 숫자 범위 검사는 백엔드에서 |
| ② | `invitation`에는 RLS(DB가 행마다 팀을 걸러 주는 기능)가 없다(D-023). 그래서 `findById(id)`를 쓰면 **다른 팀 링크 id로 무효화**할 수 있다. 메서드 이름에 `TenantId`를 고정해 두면 다른 팀 id는 "없음" → 404 |
| ③ | 지우지 않고 `expires_at = 지금`. 누가 언제 만든 링크였는지 기록이 남는다. 수락은 만료 검사에서 410 |

목록 응답 `InviteSummary`에는 원문도 해시도 없다(id·역할·횟수·만료·생성 시각만).

### 1-6. 코드로 보기: 내보내면 바로 403

```java
// 짧은 자기 트랜잭션으로 바로 커밋 → 그 사람의 다음 요청부터 MembershipGuard가 403
@Transactional
@Modifying(flushAutomatically = true, clearAutomatically = true)
@Query("delete from MembershipEntity m where m.userId = :userId and m.tenantId = :tenantId")
int deleteByUserIdAndTenantId(@Param("userId") Long userId, @Param("tenantId") Long tenantId);
```

```java
public void remove(Long teamId, Long userId, Long byUserId) {                 // ① @Transactional 없음
    if (userId.equals(byUserId)) {
        throw new CannotRemoveSelfException();                                // 400
    }
    if (memberships.deleteByUserIdAndTenantId(userId, teamId) == 0) {
        throw new MemberNotFoundException();                                  // ② 404
    }
    log.info("팀원 내보내기 teamId={} userId={} by={}", teamId, userId, byUserId);
    discordProvisioner.revokeRole(teamId, userId);                            // ③
}
```

| 번호 | 이유 |
|---|---|
| ① | 삭제가 리포지토리의 짧은 트랜잭션으로 **먼저 커밋**된다. 디스코드 호출이 느려도 DB 잠금을 오래 잡지 않는다 |
| ② | 영향 행 수로 판단. `tenant_id` 조건이 있어서 다른 팀 사람 id를 넣으면 0행 → 404 |
| ③ | 디스코드 역할 회수. 실패해도 예외를 던지지 않는다(AI-93: "회수 실패로 내보내기를 실패시키지 말 것"). 서버에서 쫓아내지는 않는다. 다른 팀 소속일 수 있다 |

"즉시 403"이 되는 진짜 이유는 MembershipGuard 쪽에 있다. 12단계에서 만든 가드가 **요청마다 DB로** 소속을 확인하고 세션에 캐시하지 않는다. 세션에 "이 사람은 팀 3 멤버"를 넣어 두면 내보낸 뒤에도 세션이 끝날 때까지 들어온다. 테스트 `내보낸_직후_그_사람의_다음_요청은_403`이 이걸 고정한다.

`@RequireOwner`는 `RequireOwnerInterceptor`가 읽는다. 가드가 요청 속성 `aiops.role`에 넣은 역할을 보므로, `WebMvcConfig`에서 **가드 다음에** 등록돼 있어야 한다. 순서가 바뀌면 역할이 없어 항상 403이다.

### 1-7. 코드로 보기: 디스코드 연결 컨트롤러 (#32)

```java
@GetMapping("/api/discord/connect")
public ResponseEntity<?> connect(@RequestParam Long teamId) {
    AppUserPrincipal user = CurrentUser.get();

    Result result = joinService.checkConnectable(user.appUserId(), teamId);    // ① 멤버 403, 미준비 409
    ...
    URI authorize = UriComponentsBuilder.fromUriString(AUTHORIZE_URL)
            ...
            .queryParam("scope", "identify guilds.join")   // 이 두 개만 (D-070)
            .queryParam("state", state)
            .queryParam("prompt", "consent")
            .encode()
            ...
    return ResponseEntity.status(HttpStatus.FOUND).location(authorize).build();
}

@GetMapping("/api/discord/callback")
public ResponseEntity<?> callback(@RequestParam(required = false) String code,
        @RequestParam(required = false) String state) {
    AppUserPrincipal user = CurrentUser.get();
    Long teamId = oauthState.verify(state).teamId();   // 실패하면 InvalidOAuthStateException → 400   ②
    if (code == null || code.isBlank()) {              // 사용자가 디스코드 동의 화면에서 취소한 경우
        return redirectToConsole(teamId, "failed");
    }
    Result result = joinService.complete(user.appUserId(), code, state);      // ③
    ...
}
```

| 번호 | 이유 |
|---|---|
| ① | 경로가 `/api/teams/{teamId}/**`가 아니라 MembershipGuard를 안 탄다. 그래서 서비스가 `existsByUserIdAndTenantId`로 **직접** 멤버십을 확인한다 |
| ② | `state`(서버가 서명한 "누가·어느 팀" 값, 19번 노트)를 먼저 검증해서 돌려보낼 팀을 안다. 위조·만료면 400 |
| ③ | 서비스가 state를 한 번 더 검증하고 **state의 사용자 = 세션 사용자**인지 본다. 남의 연결 링크를 내 브라우저로 끝내는 것을 막는다. 콜백 시점에 멤버십도 다시 확인한다(그사이 내보내졌을 수 있다) |

콜백은 디스코드에서 돌아오는 최상위 GET 이동이라 `SameSite=Lax` 세션 쿠키가 실린다. 그래서 세션 기반으로 만들 수 있었다. 결과는 JSON이 아니라 콘솔 화면 `/teams/{id}/settings?discord=connected|failed`로 302 이동이다.

## 2. 리뷰 메모

| 항목 | 내용 | 심각도 |
|---|---|---|
| 토큰 형식 | `InvitationService`: 32바이트 → `Base64.getUrlEncoder().withoutPadding()` → 43자. 테스트 `원문은_43자_base64url이고_DB에는_해시만`. **합의대로** | 메모 |
| 난수 | `new SecureRandom()` static 1개. `getInstanceStrong()` 안 씀. **합의대로**. 단 AI-84(A) Jira 본문에는 아직 `getInstanceStrong()` 예시가 남아 있다. A가 그대로 따라 쓰지 않게 본문 갱신 필요 | 낮음 |
| 해시 저장 | `token_hash = ApiKeyHasher.sha256Hex(raw)`만 저장, 원문 컬럼 없음(V3). 테스트 `DB에는_토큰_원문이_없다`. **합의대로** | 메모 |
| 링크 | `<aiops.console.base-url>/invite/<raw>`, 끝 `/` 제거. **합의대로** | 메모 |
| 조건부 UPDATE | `incrementUsedCount`: `WHERE id = :id AND used_count < max_uses AND expires_at > now()`. 합의보다 만료 조건 1개 추가. **합의대로**. 다만 두 스레드 동시 수락 테스트는 없다(AI-84 명세는 "두 스레드 동시 consume → 하나만 성공" 테스트를 요구). 순차 2회 410만 있음 | 낮음 |
| 조장 링크 재수락 | `accept`가 "횟수 소진(410)" 검사를 "이미 멤버(200)" 검사보다 먼저 한다(AI-105 명세 순서 그대로). 그래서 **조장이 자기 1회용 링크를 다시 열면 410**. 조장이 더블클릭하면 두 번째 요청은 조건부 UPDATE에서 0행 → 410이고, 컨트롤러의 `DataIntegrityViolationException` 재시도도 재시도 때 소진 검사에서 410이 된다. 실제로는 가입됐는데 콘솔이 "만료된 링크"를 보여 줄 수 있다. 멤버 확인을 소진 검사 앞으로 옮기면 해결 | 중간 |
| `next` 값 | `NEXT_OWNER = "key-guide"`, `NEXT_MEMBER = "errors"`. 테스트 `..._next는_key_guide`. **D-092대로** | 메모 |
| 조장 TTL | yml `aiops.invite.owner-ttl: 7d`가 있지만 이 PR의 코드는 읽지 않는다(`issue`가 ttl을 인자로 받음). A의 AI-84가 이 값을 주입해 넘겨야 한다. 하드코딩 위험. `issueOwnerInvite` 같은 편의 메서드가 있으면 더 안전 | 낮음 |
| A 재사용 | `issue(tenantId, role, maxUses, ttl, createdBy)`는 권한 판단 없이 공개 → A가 그대로 부를 수 있다. AI-84 명세의 `consume(raw)`·`consumeIfAvailable`은 B가 `accept`·`incrementUsedCount`로 이미 만들었으니 A는 새로 만들지 말아야 한다(중복 구현 주의) | 낮음 |
| tenant_id 조건 | `findByIdAndTenantId`, `findAllByTenantIdAndExpiresAtAfter...`, `deleteByUserIdAndTenantId`, `findAllByTenantId` 모두 tenant_id 고정. **D-023대로**. 예외 2개: `findByTokenHash`(수락 시점엔 팀을 모른다, 해시가 곧 열쇠)와 `incrementUsedCount`(`WHERE id`만, 해시로 찾은 행의 PK라 실질 위험 없음) | 메모 |
| @RequireOwner | 링크 발급·목록·무효화 3개 + 팀원 내보내기에 있음. 팀원 목록만 없음(멤버 누구나, 명세대로). 테스트 `팀원은_링크_발급_목록_무효화_모두_403`, `팀원이_다른_팀원을_내보내면_403` | 메모 |
| MembershipGuard | 요청마다 `findByUserIdAndTenantId`(DB), 세션 캐시 없음. 내보내기 삭제는 즉시 커밋. **규칙 14대로** | 메모 |
| 토큰 로그 | `issue`·`accept` 로그에 원문 없음, `Issued.toString` 덮어씀. 앱 안에 요청 URI를 찍는 필터도 없음(확인함). 다만 원문이 **URL 경로**에 있어서 나중에 운영 앞단(nginx 등) 접근 로그가 경로를 남기면 원문이 남는다. AI-105 명세 7번 "경로 마스킹"은 아직 해당 코드가 없다. 앞단 설정은 저장소에 아직 없음 | 낮음 |
| 정지 팀 수락 | `accept`는 팀이 `SUSPENDED`인지 보지 않는다. 정지 팀 팀원 링크로 가입은 되고, 다음 팀 API부터 가드가 403. 해는 작지만 410/403으로 막는 편이 일관적 | 낮음 |
| 내보내기 응답 시간 | `MemberService.remove`가 `revokeRole`을 요청 스레드에서 동기로 부른다. 디스코드가 429면 `DiscordApiClient`가 최대 30초 기다린 뒤 1회 재시도 → DELETE 응답이 그만큼 늦을 수 있다. 삭제는 이미 커밋돼 있어 정확성 문제는 아님. `@Async`나 커밋 후 이벤트로 빼는 것을 고려 | 낮음 |
| 콜백 취소 경로 | `callback`에서 `code`가 비면 state 서명만 보고 사용자 일치 확인 없이 redirect. 남의 state면 그 팀 설정 화면 주소로 보낼 뿐이고 아무것도 바꾸지 않아 무해 | 메모 |
| 디스코드 토큰 | 컨트롤러는 access token을 다루지 않는다. 테스트 `콜백_성공이면_..._토큰은_어디에도_없음`. **D-070대로** | 메모 |
| AI-88 | 이 세 PR에는 키 API가 없다. 키 API(관리자 발급·폐기, 팀 키 목록, last_used_at)는 **PR #41**(`1543e72`)로 따로 머지됐다. 다음 노트 갱신 때 같이 본다 | 메모 |

## 3. 더 나아가 알면 좋은 것

- `SecureRandom` vs `SecureRandom.getInstanceStrong()`, `/dev/random`과 `/dev/urandom`
- base64url과 패딩, 256비트 토큰 길이 계산(32바이트 → 43자)
- 원문 대신 해시 저장 (API 키·초대 토큰·비밀번호 재설정 링크의 공통 패턴)
- 조건부 UPDATE와 영향 행 수로 동시성 막기 vs `SELECT ... FOR UPDATE` vs 낙관적 락(`@Version`)
- `@Modifying(clearAutomatically = true)` 뒤 엔티티가 detached 되는 것과 `save`(merge)
- `DataIntegrityViolationException`과 "롤백 전용" 트랜잭션, 트랜잭션 밖 재시도
- HTTP 410 Gone vs 404 Not Found
- RLS가 없는 테이블의 tenant_id 고정 리포지토리 메서드 (D-023)
- HandlerInterceptor 등록 순서와 요청 속성으로 값 넘기기
- OAuth2 `state` 재검증과 `SameSite=Lax` 쿠키가 실리는 조건

## 관련 노트

[[AiOps 26 - 로그인과 권한 (B)]] · [[AiOps 28 - 관리자 API 기수와 접근 기록 (A)]]
