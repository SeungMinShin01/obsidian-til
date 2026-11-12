---
출처: Claude 대화
작성일: 2026-11-10
tags: [프로젝트, java]
---

# AiOps - 디스코드 알림 (B)

> 허브: [[AiOps 프로젝트 MOC]]

**8단계, 담당 B(조현우).** PR #7 `[AI-58] 알림 보내기` · #8 `[AI-59] 채널 선택·분당 제한`. 11/3 머지. 남은 AI-60(마일스톤 2)은 브랜치에서 진행 중이다.

> 코드는 11/10 develop 기준. "정지된 팀이면 안 보냄"과 `notifyText`는 15단계(#25·#27)에서 추가됐다.

## 1. #7 알림 보내기 (AI-58)

### 코드: 인터페이스 (`Notifier`)

```java
public interface Notifier {
    void notifyNewGroup(Long tenantId, Long groupId);     // 새 그룹 1개를 알림
    void notifyText(Long tenantId, String env, String text);   // (#25) 연결 확인용 짧은 글
}
```

처리 로직(`ErrorProcessor`)은 **이 인터페이스만** 안다. 슬랙·이메일이 붙어도 처리 쪽은 그대로다. 그리고 주석의 약속: **구현은 어떤 경우에도 예외를 밖으로 던지지 않는다.** 알림이 실패해도 그룹은 이미 `processed=true`라서, 알림 실패가 처리 실패가 되면 안 된다.

### 코드: 보내는 순서 (`DiscordWebhookNotifier.notifyNewGroup`)

```java
ErrorGroupEntity group = groups.findById(groupId).orElse(null);
if (group == null || !group.getTenantId().equals(tenantId)) return;           // ① 다른 팀 그룹이면 안 보냄
env = group.getFirstEnv();                                                     // ② 채널 = 그룹의 env

TenantEntity tenant = tenants.findById(tenantId).orElse(null);
if (tenant != null && tenant.getStatus() == TenantStatus.SUSPENDED) return;   // (#27) 정지 팀
String webhook = webhookFor(tenant, env);                                      // local/prod 웹훅 선택
if (webhook == null || webhook.isBlank()) return;                             // 웹훅 없으면 INFO 후 끝
if ("local".equals(env) && !tenant.isNotifyLocal()) return;                   // (#8) local 끄기
if (!rateLimiter.tryAcquire(tenantId)) return;                                // (#8) 분당 상한

restClient.post().uri(URI.create(webhook)).body(embedBuilder.build(group))
          .retrieve().toBodilessEntity();                                     // 타임아웃 5초
```

```java
} catch (RestClientResponseException e) {
    log.warn("알림 실패: 디스코드 응답 {} tenantId={} env={}", e.getStatusCode().value(), tenantId, env);
} catch (ResourceAccessException e) {
    log.warn("알림 실패: 연결 오류·타임아웃 tenantId={} env={}", tenantId, env);
} catch (RuntimeException e) {
    log.warn("알림 실패: {} tenantId={} env={}", e.getClass().getSimpleName(), tenantId, env);
}
```

**예외 객체 `e`를 로그에 넘기지 않는다.** 이게 이 클래스의 핵심이다. `RestClientResponseException`의 메시지와 스택에는 **요청 주소 = 웹훅 URL**이 들어 있다. 웹훅 URL은 "아는 사람은 누구나 메시지를 보낼 수 있는 비밀값"이라(규칙 10) 상태 코드와 예외 이름만 남긴다. 테스트가 로그에 주소가 없는지 확인한다.

예외를 세 종류로 나눈 이유: 디스코드가 응답한 실패(4xx·5xx)와 연결 자체가 안 된 실패(타임아웃)는 원인이 다르다. 로그만 봐도 구분된다.

### 코드: embed 만들기 (`DiscordEmbedBuilder`)

```java
static final List<String> SECTIONS = List.of("원인 후보", "확인 방법", "해결 방향");

static List<Map<String, Object>> explanationFields(String explanation) {
    if (explanation == null || explanation.isBlank())
        return List.of(field("AI 설명", "설명 준비 중", false));         // ① 설명 없음
    int from = 0;
    for (int i = 0; i < SECTIONS.size(); i++) {
        int at = explanation.indexOf(SECTIONS.get(i), from);             // ② 세 제목을 순서대로 찾음
        if (at < 0) return List.of(field("AI 설명", explanation, false)); // ③ 못 찾으면 통째로 한 칸
        starts[i] = at; from = at + SECTIONS.get(i).length();
    }
    // 제목 사이 글자를 잘라 세 칸으로, 앞뒤의 ":", "##", "*" 같은 표시는 걷어냄
}
```

- 디스코드 제한: 제목 256자, 필드 값 1,024자, 필드 값은 비어 있으면 안 된다. 그래서 자르고, 비면 대체 글자를 넣는다.
- 스택 전체는 넣지 않는다. 자세한 건 콘솔에서 본다.

## 2. #8 채널 선택·분당 제한 (AI-59)

### 코드: 팀별 분당 카운터 (`NotifyRateLimiter.tryAcquire`)

```java
long minute = clock.millis() / 60_000;                                   // ① 지금이 몇 번째 "분"인지
Window window = windows.compute(tenantId,
        (id, old) -> (old == null || old.minute != minute) ? new Window(minute) : old);   // ② 분이 바뀌면 새 창
int count = window.count.incrementAndGet();
if (count <= perMinute) return true;
if (count == perMinute + 1) log.warn("알림 분당 상한 초과 …");             // ③ 넘은 첫 번째만 WARN
return false;
```

| 번호 | 왜 |
|---|---|
| ① | **고정 창(fixed window)** 방식. 단순하고 메모리가 거의 안 든다. 경계(59초·0초)에 몰리면 순간적으로 2배까지 갈 수 있지만, 도배 방지가 목적이라 충분하다 |
| ② | `ConcurrentHashMap.compute`는 같은 키에 대해 원자적으로 실행된다. 두 스레드가 동시에 새 창을 만드는 일이 없다 |
| ③ | 초과할 때마다 WARN을 찍으면 로그가 도배된다 |

**팀마다 따로 센다.** 전역 상한을 두면 한 팀의 에러 폭주가 다른 팀 알림을 막는다. 생성자에 `Clock`을 받는 것은 테스트에서 시간을 움직이기 위해서다("다음 분에는 다시 true" 테스트).

## 3. 설계와 다르게 한 곳

| PR | 다른 점 | 상태 |
|---|---|---|
| #7 | 채널을 `error_group.first_env`로 고름 | 인자에 env가 없어서 |
| #7 | 설명을 세 제목으로 나눌 수 있으면 세 칸, 아니면 한 칸 | **7단계(내 담당) 형식이 정해지면 맞춰야 함** |
| #8 | 위치 `notify/` (Jira는 `client/`·`service/`) | **D-090 임시 인정.** 15단계 전 정리 예정이었는데 15단계가 끝남 |

## 4. 리뷰 메모

| 항목 | 내용 |
|---|---|
| `first_env` | 그룹은 env 구분 없이 하나라서, local에서 처음 난 에러가 prod에서 나도 **새 그룹이 아니어서 알림이 없다.** 14번 노트 리뷰 메모와 같은 문제 |
| `windows` 맵 | 팀 수만큼 항목이 쌓이고 지우지 않는다. 팀 수가 한정돼 있어 문제없다 |

## 5. 내가 알아야 할 것

- **AI-12(LLM) 프롬프트는 출력을 "원인 후보 / 확인 방법 / 해결 방향" 세 제목으로 고정**해야 한다. `SECTIONS`의 글자와 정확히 같아야 세 칸으로 나뉜다.
- 마일스톤 2(AI-60)의 수동 확인은 Starter(마일스톤 1)와 LLM이 둘 다 내 쪽이라 내가 막고 있다. `EndToEndFlowTest`는 `/v1/events` 직접 호출 + Fake LLM이라 먼저 진행할 수 있다고 B에게 전달했다.

## 6. 다음에 볼 키워드

- `MockRestServiceServer`로 외부 HTTP 테스트
- 고정 창 vs 이동 창(sliding window) 속도 제한
- 예외 메시지·스택으로 비밀값이 새는 경로
- 테스트용 `Clock` 주입

## 관련 노트

[[AiOps 15 - 보관 삭제와 수집 통계 (A)]] · [[AiOps 17 - 팀 격리 RLS (B)]]
