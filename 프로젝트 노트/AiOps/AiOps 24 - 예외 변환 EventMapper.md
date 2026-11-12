---
출처: Claude 대화
작성일: 2026-11-10
tags: [프로젝트, java]
---

# AiOps - 예외 변환 EventMapper

> 허브: [[AiOps 프로젝트 MOC]]

**PR #37 `[AI-40] 예외 변환 실구현 (EventMapper + DefaultEventMapper)`** — 브랜치 `feat/starter-AI-40-event-mapper`. 커밋 9개: 처음 3개(인터페이스 → 테스트 → 구현) + 설계로 되돌린 6개(protocol 2 → 테스트 2 → 구현 2). **protocol 변경 포함.** 머지 대기.

## 1. 배운 내용

### 1-1. 매퍼가 하는 일

```
log.error("주문 실패", e)  [팀 앱 스레드]
 → 어펜더(AI-42) → EventMapper.map(event, RUNTIME) → Masker.mask → buffer.offer
시작 실패 [main 스레드]
 → (AI-45) EventMapper.mapThrowable(ex, STARTUP) → Masker.mask → sender.flushNow
```

Logback의 `ILoggingEvent`(또는 그냥 `Throwable`)를 서버와 약속한 `ErrorEvent` record로 옮긴다. **값을 판단하지 않고 옮기기만** 한다: 팀 코드 판별은 서버 지문(6단계), 민감정보는 Masker.

### 1-2. 코드로 보기: map

```java
IThrowableProxy proxy = event.getThrowableProxy();
if (proxy == null) return null;                       // ① 예외 없는 ERROR는 범위 밖
String message = proxy.getMessage();
if (message == null) message = event.getFormattedMessage();   // ②
return new ErrorEvent(event.getTimeStamp(), level, proxy.getClassName(), message,
        framesOf(proxy), causesOf(proxy), event.getThreadName(),
        phase,                                         // ③ 받은 그대로
        event.getLoggerName());                        // ④
} catch (Throwable t) { return null; }                 // ⑤
```

| 번호 | 이유 |
|---|---|
| ① | Logback은 예외를 `Throwable`이 아니라 `IThrowableProxy`로 들고 있다. 비동기 어펜더에서도 안전하게 넘기려는 Logback 설계 |
| ② | `new NullPointerException()`처럼 메시지 없는 예외가 많다. 그때만 `"주문 처리 실패 id=7"` 같은 로그 메시지로 대신 |
| ③ | null도 바꾸지 않는다. 부르는 쪽 버그가 데이터에 드러나게 (2-2) |
| ④ | 어느 로거가 찍었는지. protocol에 새로 추가한 필드 (2-1) |
| ⑤ | 팀 앱 스레드. 무엇이 터져도 그 로그만 건너뛴다 |

### 1-3. 코드로 보기: 원인 체인과 순환 방지

```java
Set<IThrowableProxy> seen = Collections.newSetFromMap(new IdentityHashMap<>());
seen.add(proxy);
IThrowableProxy cause = proxy.getCause();
while (cause != null && causes.size() < MAX_CAUSES && seen.add(cause)) {
    causes.add(new ErrorCause(cause.getClassName(), cause.getMessage()));
    cause = cause.getCause();
}
```

- `getCause()`를 `this`로 돌려주는 예외, A → B → A처럼 도는 예외가 실제로 있다. 그냥 따라가면 **팀 앱 스레드가 무한 루프**.
- `IdentityHashMap`: `equals`가 아니라 **같은 객체인가(==)**로 비교. 예외 클래스가 `equals`를 이상하게 덮어써도 안전하다.
- `seen.add()`는 이미 있으면 false → while 조건 하나로 "처음 보는 원인일 때만" 진행.
- 최대 10단. 원인 3단 예외(`RuntimeException ← IllegalStateException ← IOException`)는 바깥이 타입, **원인은 2개**.
- 원인은 타입·메시지만, 스택은 바깥 예외 것만 (D-013).

### 1-4. 테스트 13개와 도구

| 도구 | 쓴 곳 |
|---|---|
| `new LoggingEvent(fqcn, logger, Level.ERROR, msg, t, null)` | 진짜 Logback 이벤트. `log.error(msg, t)`와 같다 |
| `e.setStackTrace(100줄 배열)` | 스택 100줄 → 30줄 |
| 익명 클래스로 `getCause()`가 `this` | 순환 → `assertTimeoutPreemptively(1초)` |
| `java.lang.reflect.Proxy`로 만든 `ILoggingEvent` | **어떤 메서드든 예외를 던지는 가짜** → map이 null. Mockito 없이 인터페이스 가짜를 만드는 법 |
| 1000번 반복 < 1초 | 명세 "1회 1ms 안쪽" |

## 2. 설계와 다르게 했다가 되돌린 것 (이 PR의 핵심 대화)

처음 커밋은 명세와 세 곳이 달랐다. 리뷰에서 "왜 바꿨냐"를 물었고, 이유가 약해서 설계대로 되돌렸다.

### 2-1. loggerName — 충돌을 보고하지 않은 실수

- protocol `ErrorEvent`에 칸이 없어서 칸 없는 대로 짰다. **"설계와 충돌하면 먼저 보고" 규칙을 어겼다.**
- 비용도 부풀려 말했다("서버 DTO·DB 컬럼 필요"). 실제로는 서버가 이벤트를 **payload JSONB에 받은 그대로 저장** → DB·서버 코드 변경 0.
- 해결: `ErrorEvent` **끝에** `loggerName` 추가(필드는 추가만 허용) + **기존 8개 인자 생성자 유지** → `new ErrorEvent(...)`를 쓰던 7곳(서버 테스트 포함)은 수정 없음.
- 함정: `RegexMasker.mask(event)`가 이벤트를 다시 만들 때 옛 생성자를 쓰면 loggerName이 **조용히 사라진다**. 테스트(`마스킹 후에도 loggerName 유지`)로 고정.
- 걱정: record에 생성자가 2개면 Jackson이 헷갈릴 수 있다 → `JsonWriterTest` 왕복 통과로 확인(최신 Jackson은 record의 기본 생성자를 고른다).

### 2-2. phase null — "버그를 숨기는 기본값"

| | 설계 (null 그대로) | 처음 코드 (RUNTIME으로) |
|---|---|---|
| null이 생기는 경우 | 우리 코드 버그뿐 (어펜더는 RUNTIME, 시작 실패는 STARTUP 상수) | 같음 |
| 서버 | phase를 검사하지 않음 → 그냥 저장 | 그냥 저장 |
| 버그 발견 | `payload->>'phase' IS NULL`로 바로 보임 | 시작 실패가 실행 중 에러로 **섞여서 못 찾음** |

"서버가 null을 싫어할까 봐" 바꿨는데 확인해 보니 아니었고, 결국 **버그를 숨기는 효과만** 남았다. 교훈: **기본값으로 덮기 전에, 그 null이 무엇을 알려 주는지 먼저 본다.** 대신 AI-42·AI-45 테스트에서 RUNTIME·STARTUP을 넘기는지 고정한다.

### 2-3. 줄 번호 — 주석 한 줄을 과하게 따름

- protocol 주석 "모르면 -1"을 따라 -2(네이티브 메서드)도 -1로 바꿨다.
- -2에는 정보가 있고, 지문은 줄 번호를 안 쓰고, 콘솔은 "0 이하면 표시 안 함"이면 된다 → 바꿔서 얻는 게 없음.
- 원본 그대로로 되돌리고 주석을 "-1 모름, -2 네이티브"로 고쳤다.

### 2-4. 남은 차이 (protocol에 맞춘 것, 선택지 없음)

| 명세 | 실제 | 설계대로 하면 |
|---|---|---|
| `occurredAt` (Instant) | `time` (epoch millis) | protocol 타입 변경(규칙 위반) + 서버 수정 + JsonWriter가 Instant 미지원 |
| StackFrame에 fileName 없음 | 있음 | protocol 필드 삭제(규칙 위반). `UserService.java:42` 표시를 잃음 |
| `MAX_FRAMES` | `MAX_STACK_FRAMES` | 없는 상수 (명세 오타) |

## 3. 더 나아가 알면 좋은 것

### 3-1. Logback 없는 앱

`EventMapper`가 `ILoggingEvent`를 쓰므로 Log4j2 앱에서는 클래스를 불러오는 순간 `NoClassDefFoundError` → Starter 전체가 꺼질 수 있다. 팀 앱은 D-087(Throwable 잡기)로 안전. AI-49 안전성 테스트에서 확인.

### 3-2. git 팁

- `git show`가 `:`에서 멈추면 페이저(less)다. `q`로 나오거나 `git --no-pager show ...`.
- "push했다"와 원격 상태는 다를 수 있다 → `git ls-remote origin refs/heads/<브랜치>`로 확인.

### 3-3. 다음에 볼 키워드

- `IdentityHashMap`과 `equals`/`==`의 차이
- `java.lang.reflect.Proxy`로 인터페이스 가짜 만들기 (동적 프록시)
- Logback `IThrowableProxy`, `ThrowableProxy`의 순환 처리
- record 보조 생성자와 Jackson creator 선택

## 관련 노트

[[AiOps 23 - 마스킹 Masker]] · [[AiOps 25 - 어펜더 AiopsLogbackAppender]]
