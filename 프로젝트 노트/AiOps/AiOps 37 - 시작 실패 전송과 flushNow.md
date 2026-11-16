---
출처: Claude 대화
작성일: 2026-11-15
tags: [프로젝트, java]
---

# AiOps - 시작 실패 전송과 flushNow

> 허브: [[AiOps 프로젝트 MOC]]

**PR #54 `[AI-45] 시작 실패를 STARTUP 이벤트로 즉시 전송`** — 커밋 7개, 11/15 PR. 5단계(생명주기)의 첫 작업. 앱이 뜨다가 죽으면 그 예외를 바로 보낸다. 전체 시점 지도는 「AiOps - Starter 생명주기」.

## 1. 배운 내용

### 1-1. 이 PR이 하는 일

```
SpringApplication.run 실패
   └ Spring이 ApplicationFailedEvent 발행   ← 실패 로그를 찍기 "전"
        └ AiopsEarlyInitializer.handle
             └ AiopsRuntime.reportStartupFailure(예외)
                  mapThrowable(STARTUP) → 마스킹 → 버퍼 → flushNow(3초)
   └ 그 뒤 Spring의 원래 실패 흐름 (로그, 종료)
```

로그를 기다리지 않는다. 평소 길(로그 → 어펜더 → 5초마다 전송)로는 5초가 되기 전에 JVM이 끝난다.

### 1-2. 코드로 보기: 조용히 버린다

```java
public static void reportStartupFailure(Throwable failure) {
    try {
        AiopsRuntime r = instance;
        if (r == null || DISABLED.get() || failure == null) {
            return;                                               // ①
        }
        ErrorEvent event = r.mapper.mapThrowable(failure, Phase.STARTUP);
        ...
        ErrorEvent masked = r.masker.mask(event);                 // ②
        ...
        r.buffer.offer(masked);
        r.sender.flushNow(STARTUP_FAILURE_WAIT);                  // ③
    } catch (Throwable ignored) {                                 // ④
    }
}
```

| 번호 | 이유 |
|---|---|
| ① | 키가 없거나 꺼져 있으면 `instance`가 null이다. 아무것도 보내지 않는다 |
| ② | DB 연결 실패 메시지에는 주소와 비밀번호가 들어 있을 수 있다. 마스킹 없이 보내지 않는다 |
| ③ | 3초. 늘리지 않는다 |
| ④ | 다른 곳은 오류가 나면 `disable()`로 한 줄을 찍는데, **여기서는 찍지도 않는다.** 팀은 지금 "왜 앱이 안 뜨지"를 보고 있다. 그 화면에 우리 줄이 끼면 원래 실패를 가린다 |

### 1-3. flushNow의 문제: 3초가 10초가 된다

기존 구현은 **부른 스레드가 직접** 보냈다.

```
부른 스레드: flushNow(3초) → sendBatch → sendLock 대기 …
전송 스레드: (잠금 보유) 전송 3초 → 재시도 대기 1초 → 전송 3초  = 7초
부른 스레드: 잠금 획득 → 자기 전송 3초                           → 합계 약 10초
```

마감 시각은 묶음 **사이**에서만 확인했기 때문에 잠금 대기와 HTTP 한 번은 그대로 다 기다렸다.

### 1-4. 코드로 보기: 전송 스레드에 맡기고 기다리기만

```java
FlushRequest request = new FlushRequest(new CountDownLatch(1), deadline);
flushRequest.set(request);                                             // ① 요청을 남긴다
boolean finished = request.done().await(maxWait.toNanos(), TimeUnit.NANOSECONDS);   // ② 기다린다
if (!finished) {
    flushRequest.compareAndSet(request, null);                         // ③ 시간 초과면 거둔다
}
```

전송 스레드 쪽(`tick` 첫머리):

```java
FlushRequest request = flushRequest.getAndSet(null);
if (request != null) {
    try {
        drainUntil(request.deadlineNanos());
        lastFlushAt = now;
    } finally {
        request.done().countDown();          // ④ 실패해도 기다리는 쪽은 풀어 준다
    }
}
```

| 번호 | 뜻 |
|---|---|
| ① | `AtomicReference`: 스레드 사이에 값 하나를 안전하게 넘기는 상자 |
| ② | `CountDownLatch(1)`: "끝나면 알려 줘" 신호. `await(시간)`은 신호가 오거나 시간이 다 되면 돌아온다 → **부른 쪽은 무슨 일이 있어도 maxWait에 돌아온다** |
| ③ | 아직 안 집어 갔으면 요청을 지운다. 아무도 안 기다리는데 뒤늦게 비우는 일을 막는다 |
| ④ | `finally`가 없으면 전송 중 오류가 났을 때 부른 쪽이 시간을 다 채워 기다린다 |

전송 스레드가 없으면(시작 전·정지 후) 예전처럼 부른 스레드가 직접 보낸다. 그래서 기존 테스트는 그대로 통과한다.

| 방식 | 얻는 것 | 잃는 것 |
|---|---|---|
| **전송 스레드에 요청 (선택)** | 상한을 정확히 지킨다. 명세와 같다. 종료 훅(AI-46)도 그대로 쓴다 | 요청이 집히기까지 최대 0.2초(루프가 쉬는 시간) |
| 잠금만 `tryLock(남은 시간)`으로 | 변경이 작다 | 잠금을 늦게 얻으면 HTTP 3초가 더해져 약 6초 |

### 1-5. 테스트에서 처음으로 Spring을 실제로 띄웠다

```java
SpringApplication app = new SpringApplication(BrokenApp.class);   // Bean 생성에서 예외를 던지는 설정
app.setWebApplicationType(WebApplicationType.NONE);
...
assertThrows(RuntimeException.class, () -> app.run("--aiops.api-key=…", "--aiops.endpoint=" + 가짜서버));
```

- 가짜 서버는 JDK 내장 `HttpServer`. 받은 본문에 `"STARTUP"`이 있는지, 가짜 비밀번호 글자가 없는지 본다.
- `run()`이 예외를 던지며 끝난 **직후에 이미 도착해 있어야** 한다. 전송이 동기라는 증거다.
- `getMessage()`가 `StackOverflowError`를 던지는 예외를 넘겨도 밖으로 나오지 않고 Starter도 꺼지지 않는다.

## 2. 설계와 다르게 한 곳

| 명세 | 실제 | 이유 |
|---|---|---|
| 패키지 `lifecycle/` | `runtime/` | 기존 구조 |
| `EventMapper.map(예외, level, thread, now, phase)` | `mapThrowable(예외, phase)` | 이미 있는 메서드 |
| 선행 커밋된 `AiopsLifecycleTest` | 없어서 `StartupFailureTest` 새로 작성 | — |
| `flushNow` 확인만 | 동작을 바꿈 | 1-3 |

## 3. 팁

| 주제 | 내용 |
|---|---|
| `/**` 와 `/*` | 별 하나 차이. `/**`(Javadoc)는 IDE 툴팁·`@param`·문서 생성에 쓰인다. `/*`와 `//`는 그 파일을 연 사람만 본다. **다른 파일에서 부르는 것(인터페이스·public 메서드)은 `/**`**, 메서드 안의 "왜"는 `//` |
| 커밋 메시지 | Javadoc 수정 커밋에 `[AI-45]`가 빠졌다. Jira 연동은 이슈 키로 묶이므로 다음부터 확인 |
| "로컬 확인"의 범위 | 커밋 목록과 테스트 결과만 보면 붙여 넣다 빠진 글자를 못 잡는다. **준 코드와 실제 차이(`git diff develop..브랜치`)를 대조**해야 한다 |
| 포매터 | 저장할 때 주석 정렬이 바뀌어 무관한 줄이 PR에 섞였다. 해는 없다 |

## 4. 남은 것

- AI-46 종료 훅: `flushNow(2초)` → `stop()`. JVM당 한 번만 등록
- 시작 실패 뒤 Spring의 실패 로그가 어펜더에 `RUNTIME`으로 한 번 더 잡힐 수 있다 (같은 그룹, 횟수 +1)
- 명세의 "3초 안에 종료"는 `reportStartupFailure`만 따로 쟀다 (`run()` 전체에는 Spring 기동 시간이 섞인다)

## 관련 노트

[[AiOps 36 - LLM 일일 상한과 설명 재시도]] · [[AiOps 38 - 종료 훅 onJvmShutdown]]
