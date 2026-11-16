---
출처: Claude 대화
작성일: 2026-11-15
tags: [프로젝트, java]
---

# AiOps - 종료 훅 onJvmShutdown

> 허브: [[AiOps 프로젝트 MOC]]

**PR #55 `[AI-46] JVM 종료 훅에서 남은 이벤트 전송`** — 커밋 2개, 11/15 머지. 앱이 끝날 때(Ctrl+C, kill, 컨테이너 stop) 버퍼에 남은 이벤트를 마지막으로 한 번 보낸다. 이게 없으면 종료 직전에 난 에러는 버퍼에 담긴 채 사라진다. 전체 시점 지도는 「AiOps - Starter 생명주기」.

## 1. 배운 내용

### 1-1. 이 PR이 하는 일

```
startIfAbsent (Starter 시작)
   └ registerShutdownHookOnce()   JVM에 "끝날 때 이걸 실행해" 등록 (JVM당 1번)

JVM 종료 신호
   └ 스레드 "aiops-shutdown" 실행 → onJvmShutdown()
        flushNow(2초)  전송 스레드에 "지금 비워" 요청하고 최대 2초 기다림
        stop()         전송 스레드 정지
```

### 1-2. 코드로 보기: 한 번만 등록

```java
private static final AtomicBoolean HOOK_REGISTERED = new AtomicBoolean();

static boolean registerShutdownHookOnce() {
    if (!HOOK_REGISTERED.compareAndSet(false, true)) {       // ①
        return false;
    }
    try {
        Thread hook = new Thread(() -> onJvmShutdown(), SHUTDOWN_THREAD_NAME);   // ②
        Runtime.getRuntime().addShutdownHook(hook);           // ③
        return true;
    } catch (Throwable t) {
        return false;                                         // ④
    }
}
```

| 번호 | 뜻 |
|---|---|
| ① | `compareAndSet(false, true)`: "false면 true로 바꾸고 성공을 알려 줘"를 **한 동작으로** 한다. 두 스레드가 동시에 와도 한 쪽만 true를 받는다. DevTools 재시작으로 `startIfAbsent`가 다시 불려도 훅이 쌓이지 않는다 |
| ② | 훅은 "아직 시작하지 않은 스레드"다. JVM이 끝날 때 대신 시작해 준다. 데몬이 아니다 — 데몬이면 JVM이 기다려 주지 않는다 |
| ③ | JVM에 등록. 종료 훅끼리는 **순서 보장 없이 동시에** 돈다 (Spring의 컨텍스트 닫기 훅과도 동시) |
| ④ | 이미 종료 중이면 `IllegalStateException`이 난다. 조용히 넘어간다 |

### 1-3. 코드로 보기: 훅 본문

```java
static void onJvmShutdown() {
    try {
        AiopsRuntime r = instance;        // 실행되는 "그 시점"의 instance를 본다
        if (r == null) {
            return;                       // 시작 전이거나 꺼졌으면 할 일 없음
        }
        r.sender.flushNow(SHUTDOWN_FLUSH_WAIT);   // 2초
        r.sender.stop();
    } catch (Throwable ignored) {
    }
}
```

- 훅을 등록할 때 `instance`를 붙잡아 두지 않는다. Starter가 중간에 꺼지면(`disable`) `instance`가 null이 되므로 훅은 아무것도 하지 않는다. 그래서 **훅을 뺄 필요가 없다.**
- 훅 안에서 예외가 나가면 종료 로그가 지저분해지고 다른 훅을 방해할 수 있다. 전부 삼킨다.

### 1-4. 왜 Spring의 @PreDestroy가 아닌가

| 방법 | 문제 |
|---|---|
| `@PreDestroy`, `SmartLifecycle` | Starter는 Bean이 아니다(Bean보다 먼저 뜬다). 컨텍스트가 뜨지 못한 경우(시작 실패)에는 불리지도 않는다 |
| **JVM 종료 훅 (선택)** | Spring과 무관하게, JVM이 정상적으로 끝날 때면 항상 돈다 |

### 1-5. 2초인 이유

컨테이너는 stop 신호 뒤 보통 10초를 기다렸다가 강제로 죽인다. 그 안에 팀 앱 자신의 정리(DB 연결 닫기 등)도 끝나야 한다. 우리가 오래 쓰면 팀 앱의 정리가 잘린다. AI-45에서 `flushNow`를 "부른 쪽은 정해진 시간만 기다린다"로 고쳐 둔 덕에 2초가 정확히 지켜진다.

### 1-6. 테스트 4개

| 테스트 | 확인 |
|---|---|
| 남은 이벤트 전송 | 버퍼에 3개 넣고 `onJvmShutdown()` → 가짜 서버에 3개 도착, 전송 스레드 종료 |
| 응답 없는 서버 | 2.5초 안에 돌아온다 (`flushNow` 2초 + `stop`의 인터럽트로 HTTP가 바로 끊김) |
| 한 번만 등록 | 재시작을 흉내 낸 뒤 다시 등록을 시도하면 false |
| 시작 전 | 아무것도 하지 않고 예외도 없다 |

진짜 JVM 종료는 테스트에서 일으킬 수 없어서(테스트 JVM이 같이 죽는다) 훅 본문을 직접 부른다.

## 2. 설계와 다르게 한 곳

| 명세 | 실제 | 이유 |
|---|---|---|
| `AiopsRuntime.start()`에서 등록 | `startIfAbsent()` | 그런 메서드가 없다 |
| `this::onJvmShutdown` | static 메서드 + 람다 | 런타임이 static 구조, 메서드 참조를 쓰지 않는 규칙 |
| 가짜 Transport | 가짜 HTTP 서버 | `AiopsRuntime`이 Transport를 안에서 만든다 |
| — | 훅 등록 플래그는 `resetForTest`에서 되돌리지 않음 | 훅은 실제 JVM에 남는다. 플래그만 되돌리면 테스트마다 쌓인다 |

## 3. 못 잡는 것

- `kill -9`, 전원 차단: 훅이 돌지 않는다. 포기한다.
- Windows에서 `gradlew bootRun`을 Ctrl+C로 끄면 Gradle이 JVM을 강제로 죽여 훅이 안 돌 수 있다 (⚠ 미확인).

## 4. 남은 것

- 수동 확인: 샘플 앱에서 에러 직후 Ctrl+C → 서버 DB에 행이 생기는지

## 관련 노트

[[AiOps 37 - 시작 실패 전송과 flushNow]] · [[AiOps 39 - 환경 정보 hello와 EnvCollector]]
