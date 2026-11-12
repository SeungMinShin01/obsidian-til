---
출처: Claude 대화
작성일: 2026-11-10
tags: [프로젝트, java]
---

# AiOps - 디스코드 자동화 (B)

> 허브: [[AiOps 프로젝트 MOC]]

**15단계. 원래 A 담당이었는데 B가 진행했다.** PR #10 `[AI-90] 디스코드 준비` · #11 `[AI-91] DiscordApiClient` · #25 `[AI-92] 채널 자동 생성` · #26 `[AI-93] 팀원 디스코드 연결` · #27 `[AI-94] 정지 시 웹훅 삭제`. 11/3~11/5 머지. 하위 작업 5개가 모두 끝났다.

## 0. 전체 그림

```
팀 생성(13단계) 커밋 → TeamCreated → @Async DiscordProvisioner.provision          (#25)
   역할 → 카테고리 → #local·#prod 비공개 채널 → 웹훅 2개 → tenant에 저장 → READY
팀원 "디스코드 연결" → OAuthState 서명 → 디스코드 동의 → 콜백                         (#26)
   → code를 토큰으로 교환 → 서버 추가 + 팀 역할 → discord_user_id 저장 (토큰은 버림)
팀 정지 커밋 → TeamSuspended → 웹훅만 삭제(채널 보관) / 재개 → provision 재사용        (#27)
           모든 REST 호출은 DiscordApiClient 한 곳                                  (#11)
```

## 1. #10 디스코드 준비 (AI-90)

`docs/discord-setup.md`에 봇 권한 3개(역할·채널·웹훅 관리, 관리자 권한 없음, D-069) 설정법을 적었다. 코드는 설정 record 하나다.

```java
@ConfigurationProperties("aiops.discord")
public record DiscordProperties(String guildId, String botToken, String clientId,
                                String clientSecret, String redirectUri) {

    public boolean isBotConfigured() {                 // 값이 없으면(로컬·CI) 디스코드 기능을 건너뜀
        return hasText(guildId) && hasText(botToken);
    }

    @Override
    public String toString() {                         // 로그에 record가 찍혀도 비밀값이 안 보이게
        return "DiscordProperties[guildId=" + guildId
                + ", botToken=" + mask(botToken)
                + ", clientId=" + clientId
                + ", clientSecret=" + mask(clientSecret)
                + ", redirectUri=" + redirectUri + "]";
    }

    private static String mask(String secret) {
        return hasText(secret) ? "***" : "(없음)";     // 값이 있는지 없는지만 알려 줌
    }
}
```

record는 `toString`을 자동으로 만들어 **모든 필드를 그대로 출력**한다. 비밀값이 든 record는 반드시 덮어써야 한다. yml에 빈 기본값(`${AIOPS_DISCORD_BOT_TOKEN:}`)을 줘서 CI가 값 없이도 뜬다.

## 2. #11 DiscordApiClient (AI-91)

### 코드: 모든 호출이 지나는 `call`

```java
private <T> T call(String operation, Supplier<T> request) {
    try {
        return request.get();                                          // 1차 시도
    } catch (RestClientResponseException e) {
        if (e.getStatusCode().value() != 429)
            throw new DiscordApiException(e.getStatusCode().value(), operation);   // ① 본문 없이 상태·이름만
        waitBeforeRetry(retryAfter(e), operation);                     // ② 429면 Retry-After만큼 대기
    } catch (ResourceAccessException e) {
        throw new DiscordApiException(DiscordApiException.NO_RESPONSE, operation);
    }
    try {
        return request.get();                                          // ③ 딱 1회만 다시
    } catch (RestClientResponseException e) {
        throw new DiscordApiException(e.getStatusCode().value(), operation);
    } ...
}
```

| 번호 | 왜 |
|---|---|
| ① | 원래 예외를 cause로 붙이지 않는다. 원래 예외 메시지에는 **응답 본문**(웹훅 URL 등)이 들어 있다 |
| ② | 429 = "너무 많이 보냄, N초 뒤에". `Retry-After`가 비정상적으로 길면 최대 30초로 자른다 |
| ③ | 재시도를 반복하면 디스코드가 봇을 더 오래 막는다. 정책은 "1회만" |

`Supplier<T>`로 요청을 받는 이유: **같은 요청을 두 번 실행**해야 해서 "실행할 코드"를 넘긴다. 메서드 10개(createRole, createCategory, createTextChannel, createWebhook, deleteWebhook, addMember, addRole, removeRole …)가 전부 이 `call`을 지난다. 기다리는 부분은 `Sleeper` 인터페이스로 빼서 테스트에서는 실제로 잠들지 않는다.

## 3. #25 채널 자동 생성 (AI-92)

### 코드: 멱등 — "저장된 id가 있으면 건너뛴다"

```java
String roleId = tenant.getDiscordRoleId();
if (isBlank(roleId)) {
    roleId = api.createRole("team-" + slug);
    tenants.updateDiscordRoleId(tenantId, roleId);           // ① 만들자마자 바로 저장 (REQUIRES_NEW)
}
step = "category";
String categoryId = tenant.getDiscordCategoryId();
if (isBlank(categoryId)) {
    categoryId = api.createCategory(slug, roleId);            // 역할에만 보이는 카테고리
    tenants.updateDiscordCategoryId(tenantId, categoryId);
}
// channel-local → channel-prod → webhook-local → webhook-prod 도 같은 모양
tenants.updateDiscordStatus(tenantId, DiscordStatus.READY, null);
```

```java
} catch (DiscordApiException e) {
    return fail(tenantId, step, String.valueOf(e.getStatus()));   // ② discord_error = "category:403"
}
```

| 번호 | 왜 |
|---|---|
| ① | 디스코드에는 **롤백이 없다.** 역할을 만든 뒤 채널에서 실패하면, 역할은 이미 디스코드에 있다. 그래서 하나 만들 때마다 id를 따로 커밋해 둔다. 다음 실행은 저장된 id를 보고 **없는 것만** 만든다 |
| ② | `step` 변수를 단계마다 바꿔 두어서 어디서 실패했는지 기록한다. 웹훅 URL은 절대 쓰지 않는다 |

**이름으로 찾지 않는다.** 디스코드는 같은 이름의 채널을 여러 개 허용한다. "team-a 채널이 있나?"로 판단하면 엉뚱한 채널을 잡을 수 있다.

### 코드: 같은 팀 동시 실행 막기

```java
ReentrantLock lock = locks.computeIfAbsent(tenantId, id -> new ReentrantLock());
if (!lock.tryLock()) return Result.IN_PROGRESS;      // 기다리지 않고 "진행 중"
try { return doProvision(tenantId); } finally { lock.unlock(); }
```

재시도 버튼 연타·이벤트 중복에도 자원이 두 벌 생기지 않는다. **메모리 잠금이라 서버 1대 기준**이다(DB 상태 컬럼 대신 선택, 스키마 변경 없음).

### 코드: 커밋 후 비동기 (`DiscordProvisionListener`)

```java
@Async
@TransactionalEventListener(phase = TransactionPhase.AFTER_COMMIT)
public void onTeamCreated(TeamCreated event)     { provisioner.provision(event.tenantId()); }

@Async
@TransactionalEventListener(phase = TransactionPhase.AFTER_COMMIT)
public void onTeamSuspended(TeamSuspended event) { provisioner.suspend(event.tenantId()); }   // (#27)

@Async
@TransactionalEventListener(phase = TransactionPhase.AFTER_COMMIT)
public void onTeamResumed(TeamResumed event)     { provisioner.provision(event.tenantId()); } // (#27) 재개 = 재생성
```

`@Async`가 붙어 있어서 별도 스레드에서 돈다. 팀 생성 API는 디스코드를 기다리지 않는다. 팀 저장이 롤백되면 채널도 만들지 않는다. **13단계(A)는 팀 저장 뒤 `publishEvent(new TeamCreated(id))` 한 줄**만 넣으면 된다.

## 4. #26 팀원 디스코드 연결 (AI-93)

### 코드: 서명된 state (`OAuthState`)

```java
public String create(Long userId, Long teamId) {
    long expires = clock.instant().plus(Duration.ofMinutes(10)).getEpochSecond();
    String payload = userId + ":" + teamId + ":" + expires;
    return B64.encodeToString(payload.getBytes(UTF_8)) + "." + B64.encodeToString(sign(payload));   // 내용.서명
}

public Payload verify(String state) {
    ...
    if (!MessageDigest.isEqual(sign(payload), signature))        // ① 상수 시간 비교
        throw new InvalidOAuthStateException("signature");
    if (now >= expires) throw new InvalidOAuthStateException("expired");
    return new Payload(userId, teamId);
}
```

- OAuth의 `state`는 "이 콜백이 내가 시작한 요청에서 온 것인가"를 확인하는 값이다. 여기서는 **누가, 어느 팀으로**까지 담고 HMAC으로 서명한다. 사용자가 URL의 teamId를 바꾸면 서명이 맞지 않는다.
- ① `Arrays.equals`는 첫 번째로 다른 바이트에서 바로 멈춘다. 걸린 시간으로 몇 바이트가 맞았는지 추측할 수 있다(시간차 공격). `MessageDigest.isEqual`은 항상 끝까지 비교한다.
- 서명 키는 환경변수 `AIOPS_STATE_SECRET`. 없으면 만들지도 검증하지도 않는다.

**사용자 access token은 지역 변수에만** 두고 버린다(D-070). 테스트가 `app_user` 행 전체와 로그에 토큰이 없는지 확인한다. 디스코드를 Spring Security 로그인으로 등록하지 않은 것도 같은 이유다. 디스코드로 로그인되는 경로가 생기면 안 된다.

## 5. #27 정지 시 웹훅 삭제 (AI-94)

```java
public void suspend(Long tenantId) {
    lock.lock();                                       // ① provision과 같은 잠금, 이번엔 기다림
    try {
        deleteWebhook(tenant.getDiscordWebhookLocal(), tenantId, "local");   // url에서 id만 꺼내 삭제
        tenants.updateDiscordWebhookLocal(tenantId, null);
        deleteWebhook(tenant.getDiscordWebhookProd(), tenantId, "prod");
        tenants.updateDiscordWebhookProd(tenantId, null);
        tenants.updateDiscordStatus(tenantId, DiscordStatus.SUSPENDED, null);
    } catch (DiscordApiException e) {
        recordSuspendFailure(tenantId, step + ":" + e.getStatus());   // ② 예외 없이 기록만
    } finally { lock.unlock(); }
}
```

- **웹훅은 삭제, 채널·역할은 보관(D-069).** 정지는 되돌릴 수 있어야 한다. 웹훅 삭제는 "URL이 유출돼도 무효"로 만들려는 것이다.
- ① provision은 `tryLock`(바로 포기), suspend는 `lock`(기다림). 정지는 반드시 실행돼야 하기 때문이다.
- ② 정지 자체는 이미 커밋됐으므로 되돌리지 않는다.
- **재개 = `provision` 재사용.** 멱등이라 역할·채널 id는 있으니 건너뛰고, 비어 있는 웹훅만 새로 만든다.

## 6. 아직 없는 것

| 빠진 것 | 이유 |
|---|---|
| `AdminDiscordController`(재시도 API) | 지금 만들면 아무나 부르는 관리자 API. 로그인(12)·접근 기록(13) 이후 |
| `DiscordJoinController`(`/api/discord/connect`, `/callback`) | 세션 사용자가 필요. 12단계 이후 |
| 실제 서버에서 수동 확인 | 13단계(팀 생성·정지 API) 이후 |

## 7. 리뷰 메모

| 항목 | 내용 |
|---|---|
| D-090 | `notify/` 임시 인정의 정리 시점이 "15단계 착수 전"이었는데 15단계가 끝났다. 정리할지 다시 정해야 한다 |
| 잠금 맵 | `locks`가 팀 수만큼 쌓인다. 팀 수가 한정돼 있어 문제없다. 서버를 2대로 늘리면(v0.5) DB 기반 잠금이 필요하다 |

## 8. 내가 알아야 할 것

- 머지 후 `.env`에 `AIOPS_STATE_SECRET` 추가.
- 10단계 운영 배포 때 **운영 디스코드 서버·봇은 내가** `docs/discord-setup.md`대로 만든다.

## 9. 다음에 볼 키워드

- 멱등 설계, "외부 시스템에는 롤백이 없다"
- OAuth2 `state`와 CSRF, HMAC 서명, 상수 시간 비교
- 429와 `Retry-After`
- `tryLock` vs `lock`
- record의 자동 `toString`과 비밀값

## 관련 노트

[[AiOps 18 - V3 콘솔 스키마 (B)]] · [[AiOps 20 - HTTP 전송과 JsonWriter]]
