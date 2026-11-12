---
출처: Claude 대화
작성일: 2026-11-12
tags: [프로젝트, java]
---

# AiOps - 어펜더 장착과 비활성 처리

> 허브: [[AiOps 프로젝트 MOC]]

**`[AI-43] 어펜더 장착·재장착·비활성 처리`** — 브랜치 `feat/starter-AI-43-attach` (PR #40 머지 후 develop 위). 커밋 5개: 테스트 → `LogbackAttacher`(새 파일) → `AiopsRuntime`(전체 교체) → `AiopsEarlyInitializer`(전체 교체) → sample-app DevTools. 테스트 AttachTest 6 + AiopsRuntimeTest 6 + AppenderTest 12 초록 (11/12 10:46).

## 1. 배운 내용

### 1-1. 이 PR이 하는 일: 어펜더를 "꽂는" 일

AI-42에서 만든 어펜더는 그 자체로는 아무 데도 연결돼 있지 않다. 이 PR이 **Logback 루트 로거에 꽂는다**.

```
SpringApplication.run()
 ├ ApplicationEnvironmentPreparedEvent
 │    ① LoggingApplicationListener  (순서 +20) — Logback 설정 = 기존 어펜더 리셋
 │    ② AiopsEarlyInitializer       (순서 +21) — startIfAbsent → 장착
 ├ ApplicationPreparedEvent          — 장착 확인 (중간에 리셋됐으면 다시)
 └ ApplicationReadyEvent            — 장착 확인
DevTools 재시작 → 같은 JVM에서 위가 다시 → 부품은 그대로, 어펜더만 다시 꽂힘
어디서든 Throwable → disable(): 어펜더 떼기 + 전송 스레드 멈추기 + System.err 한 줄
```

### 1-2. 전체 교체한 두 파일: 무엇이 바뀌었나

**AiopsRuntime** (AI-39 버전 → AI-43 버전)

| 부분 | 전 (AI-39) | 후 (AI-43) | 왜 |
|---|---|---|---|
| 클래스 설명 | 설정→버퍼→전송→스레드 연결 | + 어펜더를 Logback에 붙임, 한 번 꺼지면 다시 안 켜짐 | 역할이 늘었다 |
| 필드 | settings, buffer, sender | + `mapper`, `masker`, static `DISABLED` | 어펜더를 만들 때 넘겨야 하고, 시작 실패(AI-45)도 쓴다 |
| 생성자 | 인자 3개 | 인자 5개 | 위와 같음 |
| `startIfAbsent` 시작 | 바로 instance 확인 | **`DISABLED`면 null** 먼저 | 꺼진 뒤 DevTools 재시작으로 다시 켜지지 않게 |
| 부품 생성 | 3개 | + `new DefaultEventMapper()`, `new RegexMasker()` | JVM당 1번 만들고 재사용 |
| 실패 처리 | `System.err.println(...)` 직접 | **`disable(t)`** 호출 | 꺼지는 경로를 하나로 모음(한 줄만 찍기도 거기서 보장) |
| `attachAppenderIfMissing()` | 없음 | **새로** | 장착은 매번 확인 (D-006 후반) |
| `disable(Throwable)` | 없음 | **새로** | D-087 비활성 처리 |
| `isDisabled()`, `disabledLine()` | 없음 | **새로** | 상태 확인, 로그 문장 한 곳에서 생성 |
| `mapper()`, `masker()` | 없음 | **새로** | AI-45 시작 실패가 Logback 없이 씀 |
| `resetForTest()` | 스레드 멈추고 비움 | + 어펜더 떼기 + `DISABLED` 되돌리기 | 테스트끼리 상태가 섞이지 않게 |

**AiopsEarlyInitializer** (AI-39 버전 → AI-43 버전)

| 부분 | 전 | 후 | 왜 |
|---|---|---|---|
| 선언 | `public final class` | `public class` (final 없음) | 테스트가 `handle()`을 덮어써 `NoSuchMethodError`를 흉내 내야 함 |
| 받는 이벤트 | `ApplicationListener<ApplicationEnvironmentPreparedEvent>` | `ApplicationListener<ApplicationEvent>` | 세 시점(Environment·Prepared·Ready)을 다 받아야 함 |
| 본문 | try 안에서 `startIfAbsent` 한 줄 | `isDisabled()`면 바로 리턴 → `handle(event)` | 꺼진 뒤 이벤트는 아무것도 안 함 |
| 분기 | 없음 | `handle()`: Environment → 시작+장착, Prepared/Ready → 장착만 | 장착을 여러 번 확인 |
| catch | `System.err.println(...)` | `AiopsRuntime.disable(t)` | 어펜더 떼기·스레드 멈추기까지 같이, 한 줄은 한 번만 |
| import | StarterVersion 등 | 이벤트 3종, `ApplicationEvent` | 로그 문장은 AiopsRuntime이 만든다 |

### 1-3. 코드로 보기: LogbackAttacher (새 파일)

```java
Appender<ILoggingEvent> existing = root.getAppender(AiopsLogbackAppender.NAME);
if (existing != null && existing.isStarted()) {
    return;                                   // ① 중복 장착 금지
}
if (existing != null) {
    root.detachAppender(existing);            // ② 멈춘 것은 떼고 새로
}
AiopsLogbackAppender appender = new AiopsLogbackAppender(mapper, masker, buffer);
appender.setContext(context);
appender.start();                             // ③
root.addAppender(appender);
```

| 번호 | 이유 |
|---|---|
| ① | 이름 `AIOPS`로 찾는다. 두 번 붙으면 에러가 두 번 수집된다 |
| ② | 리셋으로 멈춘 어펜더가 이름만 남아 있으면, "있으니까 안 붙임" → **영원히 수집 안 됨**. 명세는 "없으면 붙임"이었지만 이 경우를 막으려고 "없거나 멈췄으면" |
| ③ | Logback은 start 안 된 어펜더에 append를 부르지 않는다 |

- `LoggerFactory.getILoggerFactory()`가 `LoggerContext`가 아니면(Log4j2 등) 아무것도 안 한다.
- **Logback에 직접 닿는 코드를 이 클래스 하나에 모았다.** Logback이 없는 앱에서 문제가 생겨도 여기서만 터지고, 부르는 쪽이 Throwable로 잡는다.
- 새 어펜더 객체를 매번 만들지만 **버퍼·매퍼·마스커는 같은 것**을 넘긴다 → 수집된 에러는 같은 전송 스레드로 간다.

### 1-4. 코드로 보기: disable

```java
public static void disable(Throwable cause) {
    if (!DISABLED.compareAndSet(false, true)) return;   // ① 딱 한 번
    synchronized (LOCK) {
        try { LogbackAttacher.detach(); } catch (Throwable ignored) { }
        AiopsRuntime r = instance;
        instance = null;                                 // ②
        if (r != null) { try { r.sender.stop(); } catch (Throwable ignored) { } }
    }
    System.err.println(disabledLine(cause));             // ③
}
```

| 번호 | 이유 |
|---|---|
| ① | 세 시점 이벤트에서 연달아 실패해도 한 줄만. `compareAndSet`은 처음 한 스레드만 true |
| ② | `current()`가 null → 다른 부품(어펜더, 앞으로 종료 훅)이 "꺼짐"을 한 방법으로 판단 |
| ③ | 로거(SLF4J)를 쓰면 우리 어펜더로 다시 들어올 수 있다(재귀). 스택트레이스 없이 한 줄 |

`synchronized(LOCK)` 안에서 `startIfAbsent`의 catch가 `disable`을 불러도 괜찮다 — 자바 `synchronized`는 **같은 스레드가 다시 잡을 수 있다**(재진입).

### 1-5. 테스트 AttachTest 6개

| 테스트 | 증명 |
|---|---|
| 순서 = 로깅 리스너 + 1 | 로깅 초기화 직후 (D-005) |
| `context.reset()` 후 장착 → AIOPS 1개, started | Spring 로깅 초기화가 하는 리셋을 흉내 |
| 두 번 장착해도 1개 | 중복 금지 |
| 장착 → 리셋(0개) → 장착(1개) | DevTools 재시작 흉내 |
| info / 예외 없는 error / error+예외 → 버퍼 1개, `password=***` | AI-42 명세의 sample-app 확인 항목을 실제 Logback으로 |
| `handle()`이 `NoSuchMethodError` → 정상 반환 ×2, `[aiops] 비활성화됨:` 정확히 1줄, `current()` null, 어펜더 0개 | D-087. `System.setErr`로 출력을 가로채서 줄 수를 셈 |

- `new ApplicationEvent("test") {}` — 추상 클래스를 익명 클래스로 바로 만드는 법.
- System.err 가로채기는 `try/finally`로 반드시 원래 것을 돌려놓는다.

## 2. 작업 중 생긴 일

### 2-1. AI-42: 구현 파일을 커밋하지 않고 PR → CI 빨강

PR #40에 테스트 커밋만 올라가고 `AiopsLogbackAppender.java`는 untracked였다. **로컬 테스트는 디스크 파일을 쓰니 통과**, CI는 커밋된 것만 받으니 `cannot find symbol`. 구현을 커밋·push해서 해결(이후 #40 머지).
교훈: push 전 `git status --short`에 `??`가 없는지 본다.

### 2-2. AI-43: 코드를 다른 파일에 붙여 넣음

`AiopsEarlyInitializer` 새 코드(④)를 `AiopsRuntime.java`에 붙여 넣었다 → 같은 패키지에 `AiopsEarlyInitializer`가 둘, `AiopsRuntime`은 사라짐 → IDE에 "isDisabled() is undefined". 다행히 **커밋된 AiopsRuntime(ec1dd71)은 올바른 버전**이었다.
- `git restore <AiopsRuntime.java>` → 커밋된 버전으로 복구
- `AiopsEarlyInitializer.java`에 ④를 다시 붙여 넣기 → 테스트의 "cannot inherit from final"도 같이 해결
교훈: 전체 교체 후 `git diff --ignore-cr-at-eol --stat`으로 **어느 파일이 몇 줄 바뀌었는지** 보면 엉뚱한 파일에 넣은 걸 바로 안다.

## 3. 설계와 다르게 한 곳

| 명세 (AI-43) | 실제 | 이유 |
|---|---|---|
| 패키지 `lifecycle/`, `initOrGet` | `runtime/`, `startIfAbsent` | AI-39(PR #33)에서 정함 |
| 장착 코드를 AiopsRuntime에 | `LogbackAttacher`로 분리 | Logback 의존을 한 곳에 |
| 없으면 붙임 | 없거나 멈췄으면 새로 | 이름만 남은 멈춘 어펜더 문제 |
| disable: 떼기 + 멈추기 | + `current()` null, 다시 안 켜짐 | "꺼짐" 판단을 하나로 |
| DevTools·커스텀 logback-spring.xml 확인 | AI-44(마일스톤 1)에서 | 서버를 띄워야 확인 가능 |

## 4. 더 나아가 알면 좋은 것

- Spring Boot 시작 이벤트 순서와 `LoggingApplicationListener`가 하는 일
- Logback `LoggerContext.reset()` — 루트의 모든 어펜더를 떼고 멈춘다
- `synchronized` 재진입(reentrant)과 `AtomicBoolean.compareAndSet`으로 "한 번만" 만들기
- `System.setErr`로 출력 가로채 테스트하기

## 관련 노트

[[AiOps 28 - 관리자 API 기수와 접근 기록 (A)]] · [[AiOps 30 - 마일스톤 1 끝까지 돌려보기]]
