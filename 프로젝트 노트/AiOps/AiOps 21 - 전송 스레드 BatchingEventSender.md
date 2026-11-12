---
출처: Claude 대화
작성일: 2026-11-10
tags: [프로젝트, java]
---

# AiOps - 전송 스레드 BatchingEventSender

> 허브: [[AiOps 프로젝트 MOC]]

**PR `[AI-38] 전송 스레드 실구현 (BatchingEventSender)`** — 브랜치 `feat/starter-AI-38-batching-sender`. 커밋 2개(`af3343d` 구현, `de282b6` 테스트). 11/10 PR. 작업하면서 질문한 것(Atomic, final, ProtocolConstants, 메서드 참조)을 3절에 같이 정리했다.

## 1. 배운 내용

### 1-1. 이 PR이 하는 일: "언제 보낼까"

```
[팀 앱 스레드]  offer() ─▶ BoundedEventBuffer (AI-36)
                               │
[aiops-sender 데몬 스레드]  0.2초마다 tick()
   ① hello가 맡겨져 있으면 1번 보냄 (실패하면 포기)
   ② 100개가 모였거나 5초가 지났으면 → 최대 100개 묶음 → transport.send()
        실패 → 1초 뒤 1번만 재시도 → 또 실패 → 버리고 개수를 다음 묶음에 실음
   ③ 60초가 지났으면 하트비트 (실패해도 재시도 없음)
```

| 규칙 | 코드에서 |
|---|---|
| 5초 또는 100개 중 먼저 | `buffer.size() >= MAX_BATCH_SIZE \|\| now - lastFlushAt >= flushIntervalMs` |
| 1회 재시도 후 포기 (무한 재시도·지수 백오프 금지) | `if (retry) { sleep 1초; send 한 번 더 }` |
| 하트비트는 이 스레드에서만 (D-086) | 별도 타이머 없이 `tick()` 안에서 |
| 데몬 스레드 | `thread.setDaemon(true)` — 팀 앱이 끝날 때 JVM을 붙잡지 않음 |
| 어떤 Error도 스레드를 죽이지 않음 (D-087) | `runLoop`에서 `tick()`을 `catch (Throwable)` |

### 1-2. 테스트하기 쉬운 구조 만들기

5초·60초를 테스트에서 진짜로 기다리면 테스트가 몇 분씩 걸린다. 그래서 세 가지를 바꿔 끼울 수 있게 만들었다.

| 바꿔 끼우는 것 | 실제 | 테스트 |
|---|---|---|
| `Clock` (지금 몇 시) | 실제 시계 | `MutableClock` — `advance(5초)`로 손으로 시간을 넘김 |
| `Sleeper` (재시도 전 1초 대기) | `d -> Thread.sleep(d.toMillis())` | `d -> sleeps.add(d)` — 잠들지 않고 "1초 기다리라고 했다"만 기록 |
| `Transport` | `HttpTransport` | `FakeTransport` — 호출 횟수·묶음 기록, 성공/실패/Error를 마음대로 |

그리고 **루프 한 바퀴를 `tick()` 메서드로** 뺐다. 테스트는 스레드를 띄우지 않고 `clock.advance(...)` → `s.tick()`을 직접 부른다. 진짜 스레드가 필요한 테스트는 2개뿐(데몬·이름, Error 생존)이다.

```java
@Test
void 세개는_5초가_지나야_한_묶음() {
    offer(3);
    s.tick();                                  // 시간 안 흐름 → 안 보냄
    assertEquals(0, transport.batches.size());
    clock.advance(Duration.ofSeconds(5));      // 5초 흐른 것처럼
    s.tick();                                  // 이제 보냄
    assertEquals(1, transport.batches.size());
}
```

인터페이스로 나눈 이유(가짜로 바꿔 끼우기, AiOps 11 - Starter 구조와 인터페이스 1-2)가 여기서 실제로 쓰였다.

### 1-3. 코드로 보기: 묶음 보내기 (`sendBatch`)

```java
synchronized (sendLock) {                                                   // ①
    List<ErrorEvent> events = buffer.drain(ProtocolConstants.MAX_BATCH_SIZE);
    int dropped = buffer.takeDroppedCount() + carriedDropped.getAndSet(0);  // ②
    if (events.isEmpty() && dropped == 0) return;                           // ③

    EventBatch batch = new EventBatch(env, appInfo, events, dropped);
    if (transport.send(batch)) return;
    if (retry) {
        sleeper.sleep(RETRY_DELAY);                                         // 1초 (테스트는 기록만)
        if (transport.send(batch)) return;
    }
    carriedDropped.addAndGet(events.size() + dropped);                      // ④
}
```

| 번호 | 이유 |
|---|---|
| ① | 전송 스레드(`tick`)와 종료 훅(`flushNow`)이 동시에 보낼 수 있다. drain→send→실패 처리를 **한 묶음**으로 지킨다. 여러 줄을 지켜야 해서 Atomic이 아니라 `synchronized` |
| ② | 버퍼가 버린 개수 + 지난번에 포기한 개수 |
| ③ | 보낼 것도, 알릴 것도 없으면 HTTP 요청 자체를 안 한다 |
| ④ | 포기한 이벤트 수 **+ 그 묶음의 droppedCount**. 명세는 events.size()만인데, 실패한 묶음의 버린 개수도 서버에 못 갔으므로 같이 넘긴다 (PR 설계와 다른 점) |

### 1-4. 코드로 보기: 스레드 시작·종료

```java
public synchronized void start() {
    if (thread != null) return;                          // 두 번 불러도 하나
    running = true;
    thread = new Thread(() -> runLoop(), "aiops-sender"); // 새 스레드가 runLoop()를 실행
    thread.setDaemon(true);
    thread.start();
}

private void runLoop() {
    while (running) {
        try { tick(); } catch (Throwable t) { logOnce(t); }   // 무엇이 터져도 계속
        try { Thread.sleep(200); }
        catch (InterruptedException e) { Thread.currentThread().interrupt(); return; }  // stop()이 깨움
    }
}

public void stop() {
    running = false;      // ① 다음 바퀴에 while을 빠져나가게
    t.interrupt();        // ② 0.2초 sleep 중이면 바로 깨움
    t.join(1000);         // ③ 최대 1초만 기다림
}
```

`running`은 `volatile`이다. `stop()`을 부른 스레드가 바꾼 값을 aiops-sender 스레드가 **바로 보게** 하려는 것이다(3-1 표 참고).

### 1-5. `flushNow`의 한계

`flushNow(maxWait)`는 종료 훅·시작 실패 때 **부른 스레드에서 직접** 버퍼를 비운다(종료 중에는 데몬 스레드가 언제 돌지 알 수 없어서). maxWait는 묶음과 묶음 **사이에서** 확인하므로, 이미 보내는 중인 요청 하나는 HttpTransport 타임아웃(3초)까지 갈 수 있다. 최악의 경우 maxWait + 3초. **5단계 종료 훅(AI-46)에서 maxWait를 정할 때 감안**해야 한다.

## 2. 설계와 다르게 한 곳

| 다른 점 | 이유 |
|---|---|
| 포기 시 droppedCount도 이월 | 서버 집계가 적게 나오지 않게 |
| `flushNow`가 maxWait를 넘을 수 있음(최대 +3초) | 진행 중인 HTTP 요청은 끊을 수 없음. AI-46에서 감안 |
| `tick()`·`Sleeper`·Sleeper 생성자를 패키지 공개로 추가 | 테스트에서 시간을 기다리지 않으려고 |

## 3. 작업하면서 물어본 것

### 3-1. `Atomic` 클래스

**문제:** 스레드 둘이 같은 변수를 만지면 두 가지 사고가 난다.

```
count++ 는 사실 3단계: ① 읽기 ② +1 ③ 쓰기
A: 읽기(0)          +1   쓰기(1)
B:      읽기(0)          +1   쓰기(1)    → 두 번 더했는데 1 (lost update)
```

그리고 한 스레드가 바꾼 값이 다른 스레드에 늦게 보일 수 있다(CPU 캐시).

**Atomic 클래스**는 읽고-바꾸고-쓰기를 **한 동작**으로 묶고, 바꾼 값이 바로 보이게 한다. 잠금 없이 CPU 명령(CAS, compare-and-set)으로 처리해서 빠르다.

| 클래스 | 쓴 메서드 | 뜻 | 이 코드에서 |
|---|---|---|---|
| `AtomicInteger` | `incrementAndGet()` | `++`의 안전한 버전 | 버퍼의 버린 개수 |
| | `getAndSet(0)` | 값을 돌려주고 0으로. 사이에 끼어들 틈 없음 | `carriedDropped`, `takeDroppedCount` |
| | `addAndGet(n)` | n을 더함 | 포기한 개수 이월 |
| `AtomicBoolean` | `compareAndSet(false, true)` | false면 true로 바꾸고 성공, 이미 true면 실패 | 로그 한 번만 (`logOnce`) |
| `AtomicReference<T>` | `set(x)` / `getAndSet(null)` | 객체를 넣고 / 꺼내면서 비움 | `pendingHello` (hello 한 번만 보내기) |

**셋 중 무엇을 쓰나**

| 도구 | 언제 | 이 코드에서 |
|---|---|---|
| `volatile` | 한 스레드만 쓰고 나머지는 읽기만. "보이기"만 보장 | `running` |
| `Atomic*` | 여러 스레드가 읽고-바꾸고-쓰기 | 위 표 |
| `synchronized` | 여러 줄을 한 묶음으로 지켜야 할 때 | `sendLock` (drain→send→실패 처리) |

`if (!logged) { logged = true; ... }`를 일반 변수로 쓰면 두 스레드가 둘 다 if를 통과할 수 있다. `compareAndSet`은 둘 중 하나만 성공한다.

### 3-2. 왜 `final`이 많은가

**(1) `static final` = 상수**

```java
static final String THREAD_NAME = "aiops-sender";
static final Duration RETRY_DELAY = Duration.ofSeconds(1);
```

- 이름이 뜻을 설명한다(`200` 대신 `LOOP_SLEEP_MS`, 매직 넘버 방지)
- 한 곳만 고치면 된다. 테스트도 `BatchingEventSender.THREAD_NAME`을 쓴다
- 실수로 다른 값을 넣을 수 없다(컴파일 에러)

**(2) `private final` 필드 = 생성자에서 한 번만**

```java
private final EventBuffer buffer;
private final Transport transport;
```

- 객체가 사는 동안 바뀌지 않는다. "누가 중간에 buffer를 바꾸면?" 걱정이 없다
- **스레드 안전에도 도움이 된다.** final 필드는 생성자가 끝나면 다른 스레드에서도 올바른 값이 보이도록 자바가 보장한다
- final이 **없는** 필드(`running`, `thread`, `lastFlushAt`, `lastHeartbeatAt`)는 실제로 바뀌는 값들이다

**헷갈리는 점**: `private final AtomicInteger carriedDropped`인데 값이 바뀐다?
`final`은 **"이 변수가 가리키는 상자를 바꾸지 못한다"**는 뜻이다. 상자(AtomicInteger) **안의 숫자**는 바뀔 수 있다. `carriedDropped.addAndGet(5)`는 되고, `carriedDropped = new AtomicInteger()`는 컴파일 에러다.

### 3-3. `ProtocolConstants`와 처음 보는 클래스들

`ProtocolConstants`는 자바 라이브러리가 아니라 **우리가 protocol 모듈에 만든 클래스**다(AI-5).

```java
public final class ProtocolConstants {
    public static final String HEADER_API_KEY = "X-AIOPS-KEY";
    public static final String PATH_EVENTS = "/v1/events";
    public static final int MAX_BATCH_SIZE = 100;
    public static final int HEARTBEAT_INTERVAL_SECONDS = 60;
    ...
    private ProtocolConstants() { }   // 객체를 만들 일이 없어서 생성자를 막음
}
```

**왜 따로 두나**: Starter(보내는 쪽)와 서버(받는 쪽)가 **반드시 같아야 하는 약속**이기 때문이다.

```
Starter: 한 묶음 최대 100개          ← MAX_BATCH_SIZE
서버:    101개 이상이면 400           ← MAX_BATCH_SIZE
```

양쪽에 숫자 `100`을 따로 쓰면, 한쪽만 바꿨을 때 Starter가 보낸 묶음이 서버에서 전부 400이 된다. 같은 상수를 둘 다 import하면 어긋날 수가 없다. protocol 모듈에 둔 이유는 **Starter와 서버가 둘 다 의존하는 유일한 모듈**이기 때문이다.

**처음 보는 이름 구분법: import를 본다**

| 이름 | 어디 것 | 뭔지 |
|---|---|---|
| `EventBatch`, `Heartbeat`, `HelloRequest`, `AppInfo`, `ErrorEvent` | `dev.aiops.protocol` (우리) | 서버로 보내는 데이터 모양(record) |
| `EventBuffer`, `Transport`, `EventSender`, `AiopsSettings` | `dev.aiops.starter` (우리) | 인터페이스 3개, 설정 |
| `Sleeper` | 이 클래스 안 (우리) | "기다리기"를 바꿔 끼우려고 만든 작은 인터페이스 |
| `Clock`, `Duration` | `java.time` (자바 표준) | 지금 시각 / 시간 길이. `long 5000`보다 단위가 분명 |
| `AtomicInteger` 등 | `java.util.concurrent.atomic` (자바 표준) | 3-1 |

`dev.aiops.`로 시작하면 우리가 만든 것, `java.`로 시작하면 자바 표준이다.

### 3-4. 메서드 참조(`::`) → 람다로

`this::runLoop`는 "runLoop를 부르는 코드를 넘긴다"를 줄인 것이다. 아래 셋은 같다.

```java
new Thread(this::runLoop, "aiops-sender");        // 메서드 참조
new Thread(() -> runLoop(), "aiops-sender");      // 람다 ← 앞으로 이걸로
new Thread(new Runnable() {                       // 람다도 없이
    @Override public void run() { runLoop(); }
}, "aiops-sender");
```

`Thread`는 "실행할 코드"(Runnable)를 받는다. `runLoop`를 지금 실행하는 게 아니라 **나중에 실행할 수 있게 건네주는 것**이다. 같은 이유로 `sleeps::add` → `d -> sleeps.add(d)`로 바꿨다. 이 PR부터 새 코드는 메서드 참조를 쓰지 않는다. 이미 들어간 것은 MVP 이후 리팩터링.

## 4. 다음에 볼 키워드

- CAS(compare-and-set), lost update, 메모리 가시성
- `volatile` vs `Atomic*` vs `synchronized`
- 데몬 스레드, `Thread.interrupt()`와 `join(timeout)`
- 테스트 더블: Fake·Stub, 시간 주입(`Clock`)
- final 필드의 초기화 안전성(safe publication)

## 관련 노트

[[AiOps 20 - HTTP 전송과 JsonWriter]] · [[AiOps 22 - 부품 조립 AiopsRuntime]]
