---
출처: Claude 대화
작성일: 2026-11-10
tags: [프로젝트, java]
---

# AiOps - 어펜더 AiopsLogbackAppender

> 허브: [[AiOps 프로젝트 MOC]]

**PR #40 `[AI-42] 어펜더 실구현 (AiopsLogbackAppender)`** — 브랜치 `feat/starter-AI-42-appender` (#37 머지 뒤 develop에서 시작). 커밋 2개: 테스트 → 구현. 머지 완료.

> 사고: 처음 push 때 구현 파일이 untracked라 테스트 커밋만 올라가 CI가 `cannot find symbol`로 빨강. 로컬은 디스크 파일로 컴파일돼 통과했다. 구현을 커밋·push해서 해결 → AiOps 29 - 어펜더 장착과 비활성 처리 2-1

## 1. 배운 내용

### 1-1. 어펜더가 하는 일: 팀 앱 스레드의 입구

```
팀 코드 log.error("주문 실패", e)
 → Logback → (모든 어펜더에게) doAppend(event)
     ├ CONSOLE 어펜더 (팀 것)
     └ AIOPS 어펜더 (우리)  ← 같은 팀 앱 스레드에서 실행
          ① ERROR 이상? ② 예외 붙음? ③ 무시 로거 아님?
          → mapper.map(event, RUNTIME) → masker.mask → buffer.offer → 끝 (기다림 없음)
```

Starter에서 **가장 위험한 부품**. 여기서 멈추거나 예외를 던지면 팀 앱 요청이 느려지거나 죽는다.

### 1-2. 코드로 보기: append

```java
protected void append(ILoggingEvent event) {
    try {
        if (!isTarget(event)) return;
        ErrorEvent mapped = mapper.map(event, Phase.RUNTIME);    // ① 상수로 RUNTIME
        if (mapped == null) return;
        ErrorEvent masked = masker.mask(mapped);
        if (masked == null) return;
        if (buffer.offer(masked)) accepted.incrementAndGet();     // ② 받아 준 것만 셈
    } catch (Throwable t) {
        reportOnce(t);                                            // ③
    }
}
```

| 번호 | 이유 |
|---|---|
| ① | phase를 상수로 넘긴다. 매퍼가 null을 고쳐 주지 않으므로(AI-40 2-2) 여기서 정확히 |
| ② | 꽉 차서 false면 버퍼의 droppedCount가 센다. 두 숫자가 겹치지 않게 |
| ③ | 처음 한 번만 Logback status에 기록, **예외 메시지는 넣지 않음**(민감정보 가능). 매번 남기면 팀 콘솔이 덮인다 |

### 1-3. 왜 UnsynchronizedAppenderBase인가 (D-007)

`AppenderBase.doAppend`는 `synchronized` → 요청 스레드 200개가 동시에 에러를 찍으면 **한 줄로 서서** 기다린다. `UnsynchronizedAppenderBase`는 잠금 없이 각자 실행. 우리 append는 공유 상태가 버퍼(스레드 안전)와 Atomic뿐이라 잠금이 필요 없다.

### 1-4. 무시 로거와 무한 루프 (D-087)

```
우리 HttpTransport 전송 실패 → JDK HttpClient가 jdk.internal.httpclient 로거로 ERROR
 → 우리 어펜더가 잡음 → 버퍼 → 전송 → 또 실패 → 또 로그 → …
```

`dev.aiops`(우리 자신), `jdk.internal.httpclient`, `java.net.http`를 무시한다.

**점 단위 비교**: `name.equals(p) || name.startsWith(p + ".")`. 그냥 `startsWith("dev.aiops")`면 `dev.aiopsshop.OrderService` 같은 **팀 패키지를 잘못 버린다**. 테스트로 고정. `p + "."`는 매번 문자열을 만들지 않게 미리 배열(`IGNORED_WITH_DOT`)로.

### 1-5. 테스트

- 진짜 `LoggerContext`·`LoggingEvent` + 진짜 `DefaultEventMapper`·`RegexMasker` + **가짜 버퍼(ListBuffer)**.
- `appender.setContext(CONTEXT); appender.start();` 후 `doAppend` — start 전에는 Logback이 append를 부르지 않는다.
- 잡는 것: ERROR+예외 1개(타입·RUNTIME·loggerName 확인), 마스킹된 값, `dev.aiopsshop` 팀 패키지
- 버리는 것: INFO·WARN, 예외 없는 ERROR, 무시 로거 4종(`@ParameterizedTest`)
- 안 터지는 것: Mapper가 예외 / 버퍼가 `StackOverflowError` → `assertDoesNotThrow`, 두 번 연속도
- 익명 클래스로 인터페이스 2개 메서드를 가진 가짜 Mapper (람다는 메서드 1개짜리 인터페이스에만)
- `ListBuffer`는 `final`이 없어야 한다. 테스트가 익명 클래스로 상속해 `offer`에서 `StackOverflowError`를 던지게 하기 때문 (처음 코드의 실수)

## 2. 설계와 다르게 한 곳

| 명세 | 실제 | 이유 |
|---|---|---|
| 무시: 접두사로 시작하면 | 점 단위 비교 | 비슷한 이름의 팀 패키지를 버리지 않게 |
| `accepted` 카운터 | `offer`가 true일 때만 | 버퍼의 droppedCount와 겹치지 않게 |
| `addError` 최초 1회 | + 예외 메시지 제외 | 민감정보 |
| sample-app 세 가지 로그 → 버퍼 1개 확인 | AI-43 AttachTest에서 실제 Logback으로 확인 | 장착은 AI-43 |

## 3. 더 나아가 알면 좋은 것

- Logback 구조: `LoggerContext` → `Logger` → `Appender` (`addAppender`, 루트 로거)
- `ContextAwareBase.addError`와 Logback status (`StatusPrinter`)
- `synchronized` 경합과 처리량

## 관련 노트

[[AiOps 24 - 예외 변환 EventMapper]] · [[AiOps 26 - 로그인과 권한 (B)]]
