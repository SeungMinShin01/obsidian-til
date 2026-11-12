---
출처: Claude 대화
작성일: 2026-11-03
tags: [프로젝트, java]
---

# AiOps - Starter 구조와 인터페이스

> 허브: [[AiOps 프로젝트 MOC]]

**PR:** #6 인터페이스(AI-8), #9 설정(AI-35), AI-36 버퍼(`feat/starter-AI-36-event-buffer`). 내가 직접 설계한 코드가 아니라서, 왜 이렇게 생겼는지 이해하려고 정리했다.

## 1. 배운 내용

### 1-1. 큰 그림: 스레드가 두 개다

```
[팀 앱 스레드]                                  [aiops-sender 스레드 (Starter 전용)]
 예외 발생                                        5초마다 또는 100개가 모이면
   │                                                 │
 ① 어펜더가 잡음 (AI-42)                           ④ EventSender: 버퍼에서 꺼냄 (AI-38)
 ② 예외 → ErrorEvent 변환 (AI-40)                     │
 ③ 마스킹 (AI-41)                                  ⑤ Transport: HTTP POST (AI-37)
   │                                                 │
   └──▶  EventBuffer.offer()  ══ 버퍼 ══  drain() ◀──┘          → 서버
```

- 왼쪽은 **팀 앱의 요청 스레드**다. 여기서 멈추면 팀 앱이 느려진다.
- 오른쪽은 **Starter가 따로 만든 스레드**다. 서버가 죽어서 3초를 기다려도 팀 앱과는 관계가 없다.
- 버퍼가 두 스레드 사이의 **경계**다. 왼쪽은 넣기만 하고 바로 돌아간다. 네트워크는 전부 오른쪽에서 한다.
- 북극성인 "팀 앱을 절대 느리게 하거나 죽이지 않는다"를 코드 구조로 지키는 방법이다.

### 1-2. 왜 인터페이스를 먼저 만들었나

인터페이스는 **무엇을 하는지만 정하고, 어떻게 하는지는 비워 둔 약속**이다.

1. **테스트할 때 가짜로 바꿔 끼운다.** 가장 큰 이유다. `BatchingEventSender`가 `Transport`를 생성자로 받으면, 테스트에서는 항상 실패하는 `FakeTransport`를 넣어 "실패하면 1번 재시도"를 서버 없이 확인할 수 있다. 바깥에서 넣어 주는 이 방식이 의존성 주입이다(스프링 `@Autowired`와 같은 원리).
2. **순서를 기다리지 않고 나눠 만든다.** AI-38은 AI-37이 끝나기 전에 가짜로 테스트하며 진행할 수 있다.
3. **약속을 코드에 적는다.** `EventBuffer` 주석의 "대기하지 않고, 예외를 던지지 않는다"를 구현이 지켜야 한다. 고정 규칙 2(메서드 이름·파라미터 변경 금지)가 이 약속을 지킨다.
4. **구현을 바꿔도 쓰는 쪽은 그대로 둔다.** 나중에 gzip이나 큐 방식으로 바꿔도 Sender는 고치지 않는다.

> 단점: 구현이 하나뿐이면 파일만 늘어나는 과한 설계가 될 수 있다. 여기서는 1번(서버 없이 테스트)과 스레드 경계 때문에 쓴다.

### 1-3. 왜 3개로 나눴나

| 인터페이스 | 맡는 질문 | 스레드 | 구현 |
|---|---|---|---|
| `EventBuffer` | 어디에 쌓아 둘까 | offer는 팀 앱, drain은 sender | AI-36 |
| `Transport` | 어떻게 보낼까 (HTTP 한 번) | sender | AI-37 |
| `EventSender` | 언제 보낼까 (5초/100개, 재시도, 하트비트) | sender | AI-38 |

하나에 다 넣으면 "HTTP가 실패했다"와 "재시도 타이밍이 틀렸다"를 따로 테스트할 수 없다. 조립은 AI-39 `AiopsRuntime`에서 한다.

```java
var buffer    = new BoundedEventBuffer(settings.bufferCapacity());
var transport = new HttpTransport(settings);
var sender    = new BatchingEventSender(buffer, transport, settings);
```

## 2. 코드에서 본 것

### 2-1. `AiopsSettings.fromOrNull` (AI-35)

- **record:** 설정은 한 번 읽으면 바뀌지 않는다. 필드가 전부 final이고 getter·equals·toString이 자동으로 생긴다.
- **예외 대신 null:** 키가 없을 때 예외를 던지면 팀 앱이 시작하다 죽는다. "Starter만 꺼지고 팀 앱은 산다"(규칙 4, D-087)를 지키려고 null을 돌려주고 경고 한 줄만 남긴다.

### 2-2. `BoundedEventBuffer` (AI-36)

```java
if (event == null || !queue.offer(event)) {   // put이 아니라 offer
    dropped.incrementAndGet();
    return false;
}
```

| 코드 | 이유 |
|---|---|
| `ArrayBlockingQueue` | 크기가 정해진 큐. 무한 큐면 서버가 죽었을 때 팀 앱 메모리가 계속 는다 |
| **`offer`** (`put` 아님) | `put`은 꽉 차면 기다린다. `offer`는 바로 false. 이 한 단어가 규칙 5의 핵심 |
| `AtomicInteger` | 여러 스레드가 동시에 `++`하면 일반 int는 숫자가 빠진다 (테스트 6번) |
| `getAndSet(0)` | 읽기와 초기화를 한 번에 한다. 따로 하면 그 사이에 버려진 1건이 사라진다 |
| `drainTo(out, max)` | 한 번에 꺼내서 `poll` 반복보다 잠금을 덜 건다 |
| 생성자 `capacity < 1` → 기본값 | `new ArrayBlockingQueue<>(0)`은 예외를 던진다. 생성자에서도 예외 금지 |
| null도 버린 개수에 셈 | `EventBuffer` 인터페이스 주석의 약속 (처음 버전은 세지 않았음 → 인터페이스에 맞춤) |

설계상 선택: 꽉 차면 **새 것을 버리고**, 버린 개수는 `EventBatch.droppedCount`로 서버에 알린다. 못 보낸 사실을 숨기지 않는다.

### 2-3. 코드로 보기: 인터페이스 3개 (PR #6)

```java
public interface EventBuffer {
    /** 넣기. 꽉 찼거나 null이면 false (버린 개수 +1). 대기하지 않고, 예외를 던지지 않는다 */
    boolean offer(ErrorEvent event);
    /** 최대 max개를 꺼낸다. 전송 스레드가 부른다. 비어 있으면 빈 리스트 */
    List<ErrorEvent> drain(int max);
    /** 지금까지 버린 개수를 읽고 0으로 되돌린다. EventBatch.droppedCount에 실린다 */
    int takeDroppedCount();
    int size();
}

public interface Transport {
    boolean send(EventBatch batch);          // POST /v1/events.   2xx면 true
    boolean hello(HelloRequest hello);       // POST /v1/hello
    boolean heartbeat(Heartbeat heartbeat);  // POST /v1/heartbeat (D-086)
}

public interface EventSender {
    void start();                            // 전송 스레드 시작. 이미 시작했으면 아무것도 안 함
    void submitHello(HelloRequest hello);    // 앱 준비 후 hello 1건을 맡김
    void flushNow(Duration maxWait);         // 부른 스레드에서 직접 비워 보냄 (종료 훅·시작 실패용)
    void stop();                             // 최대 1초 기다림
}
```

**읽는 법:** 메서드 이름보다 **주석이 계약**이다. "대기하지 않고", "예외를 던지지 않는다", "2xx면 true", "최대 1초"가 구현이 지켜야 할 약속이고, 테스트는 이 문장들을 그대로 확인한다. 반환값이 전부 `boolean`·빈 리스트인 것도 같은 이유다. **실패를 예외가 아니라 값으로** 돌려줘서, 부르는 쪽이 try/catch 없이 다음 행동을 정한다.

`flushNow(maxWait)`만 "부른 스레드에서" 실행된다. 앱이 꺼질 때(종료 훅)는 전송 스레드가 이미 멈췄을 수 있어서 직접 보내야 하고, 그래도 종료를 붙잡지 않게 최대 시간을 받는다.

### 2-4. 코드로 보기: 설정 읽기 (PR #9, AI-35)

#### `fromOrNull`: 실패하면 null

```java
public static AiopsSettings fromOrNull(Environment environment) {
    try {
        String enabled = environment.getProperty("aiops.enabled");
        if (enabled != null && enabled.trim().equalsIgnoreCase("false"))
            return null;                                              // ① 끄라고 했으면 조용히

        String apiKey = trimToNull(environment.getProperty("aiops.api-key"));
        if (apiKey == null) {
            System.err.println("[aiops] aiops.api-key 없음, 비활성");  // ② 로거 대신 System.err
            return null;
        }
        return new AiopsSettings(apiKey,
                readEnv(environment.getProperty("aiops.env")),
                readEndpoint(environment.getProperty("aiops.endpoint")),
                true,
                readBufferCapacity(environment.getProperty("aiops.buffer-capacity")),
                readFlushInterval(environment.getProperty("aiops.flush-interval")),
                readAppName(environment.getProperty("spring.application.name")));
    } catch (Throwable t) {                                            // ③ Exception이 아니라 Throwable
        System.err.println("[aiops] 비활성화됨: " + t.getClass().getName() + " " + t.getMessage()
                + " (starter " + StarterVersion.get() + ")");
        return null;
    }
}
```

| 번호 | 왜 |
|---|---|
| ① | 사용자가 의도해서 끈 것이라 경고를 남기지 않는다 |
| ② | 설정은 **로깅이 아직 준비 중일 때** 읽힌다. 로거를 쓰면 메시지가 사라지거나 로깅 초기화를 꼬이게 할 수 있다 |
| ③ | `NoClassDefFoundError` 같은 **Error**도 잡는다(D-087). Boot 버전이 달라 클래스가 없을 때가 대표적이다. 예외를 던지는 대신 원인과 Starter 버전을 한 줄 남긴다 |

`@ConfigurationProperties`를 쓰지 않고 `Environment`에서 직접 읽는 이유: Bean이 만들어지기 **전**(로깅 초기화 직후)에 읽어야 하기 때문이다.

#### 값 하나씩 읽기: 잘못된 값은 기본값으로

```java
private static String readEndpoint(String raw) {
    String v = trimToNull(raw);
    if (v == null) return Defaults.ENDPOINT;          // "https://ingest.aiops.invalid"
    while (v.endsWith("/")) v = v.substring(0, v.length() - 1);   // "http://x/" + "/v1/events" 이중 슬래시 방지
    return v;
}

private static int readBufferCapacity(String raw) {
    try {
        int v = Integer.parseInt(raw.trim());
        if (v >= 100 && v <= 10_000) return v;        // 범위 밖이면
    } catch (RuntimeException ignored) { }            // null·숫자 아님이면
    return Defaults.BUFFER_CAPACITY;                  // 1000
}

/** "5", "5s", "500ms", "PT5S" 모두 허용. 1~60초 밖이면 기본 5초 */
private static Duration readFlushInterval(String raw) { ... }
```

- **설정이 틀려도 앱을 멈추지 않는다.** 틀린 값은 예외 대신 기본값이 된다. `raw.trim()`에서 null이면 NPE가 나지만 `catch (RuntimeException)`이 받아서 기본값으로 간다.
- 기본 endpoint가 `.invalid`인 이유: `.invalid`는 **실제로 연결되지 않는 예약 도메인**이다. 설정을 빠뜨려도 엉뚱한 서버로 데이터가 가지 않는다.
- `readEnv`는 `local`·`prod`가 아니면 경고 후 `local`. 오타로 prod 데이터가 엉뚱한 env로 섞이지 않게 한다.

#### `StarterVersion`

```java
public static String get() {
    try {
        String v = StarterVersion.class.getPackage().getImplementationVersion();   // jar의 MANIFEST
        return v == null ? "dev" : v;           // IDE·Gradle 실행 중에는 MANIFEST가 없음
    } catch (Throwable t) {
        return "unknown";                       // 버전 읽다가 앱을 죽이지 않는다
    }
}
```

처음에는 `Defaults.version()`에 넣었다가 따로 뺐다. `Defaults`는 "상수 모음"이고, 버전은 실행 환경에서 **읽어 오는 값**이라 성격이 다르다.

## 3. 스스로 확인 문제

**Q1. `offer`를 `put`으로 바꾸면 서버가 10분 동안 죽어 있을 때 팀 앱은?**
버퍼 1000칸이 금방 찬다. 그다음부터 에러를 로그로 남기는 요청 스레드가 하나씩 `put`에서 멈춘다. 톰캣 요청 스레드(기본 200개)가 다 묶이면 팀 앱이 **아무 요청도 처리하지 못한다**. 우리 서버 장애가 팀 앱 장애가 된다. 종료할 때도 멈춘 스레드 때문에 앱이 안 꺼질 수 있다.

**Q2. Sender가 `new HttpTransport()`를 직접 만들면?**
가짜로 바꿀 수 없다. "실패하면 1번 재시도"를 테스트하려면 일부러 실패하는 진짜 서버가 필요하고, 몇 번 호출됐는지 세기도 어렵다. 테스트가 느려지고 네트워크 상황에 따라 결과가 흔들린다. AI-37이 끝나기 전에는 AI-38을 테스트할 수도 없다.

**Q3. `fromOrNull`이 키가 없을 때 예외를 던지면 sample-app은?**
`aiops.api-key=${AIOPS_KEY:}`라 환경변수가 없으면 빈 값이다. 시작 중에 예외가 나면 스프링 컨텍스트가 실패해서 `APPLICATION FAILED TO START`로 **앱이 아예 뜨지 않는다**. 실제 팀이라면 키를 깜빡하거나, 키가 없는 CI의 `@SpringBootTest`에서 빌드가 깨진다. Starter가 팀 앱을 죽이는 이유가 된다.

## 4. 다음에 볼 키워드

- `ArrayBlockingQueue` vs `LinkedBlockingQueue` — 잠금 1개 vs 2개
- `offer` / `put` / `add` — 꽉 찼을 때 false / 대기 / 예외
- 의존성 주입(DI), 테스트 더블(Fake·Stub·Mock)
- `AtomicInteger`, CAS(compare-and-set)

## 관련 노트

[[AiOps 10 - 선행 테스트 브랜치]] · [[AiOps 12 - 이벤트 버퍼 BoundedEventBuffer]]
