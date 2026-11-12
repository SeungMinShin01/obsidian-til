---
출처: Claude 대화
작성일: 2026-11-10
tags: [프로젝트, java]
---

# AiOps - 이벤트 버퍼 BoundedEventBuffer

> 허브: [[AiOps 프로젝트 MOC]]

**PR `[AI-36] 버퍼 실구현 (BoundedEventBuffer)`** — 브랜치 `feat/starter-AI-36-event-buffer`. 커밋 2개(`eab5d44` 구현, `fa3e77b` 테스트). 11/3에 만들고 PR은 11/10에 올렸다. 그 사이 develop이 43커밋 앞서 가서 PR 직전에 develop을 받아 다시 돌렸다.

## 1. 배운 내용

### 1-1. 버퍼가 하는 일: 두 스레드 사이의 경계

```
[팀 앱 요청 스레드]  예외 → 어펜더 → offer() ─┐
                                               ├─ BoundedEventBuffer (크기 1000)
[aiops-sender 스레드]        drain(100) ◀──────┘   → HTTP 전송
```

- `offer`는 **팀 앱 스레드**에서 불린다. 여기서 0.1초만 멈춰도 팀 앱이 느려진다(규칙 5).
- `drain`은 **Starter 전용 스레드**에서 불린다. 여기서는 기다려도 된다.
- 그래서 버퍼는 "넣기만 하고 바로 돌아가는 곳"이어야 하고, 꽉 차면 **기다리지 않고 버린다.**

### 1-2. 코드 한 줄씩

```java
if (event == null || !queue.offer(event)) {   // put이 아니라 offer
    dropped.incrementAndGet();
    return false;
}
```

| 코드 | 이유 |
|---|---|
| `ArrayBlockingQueue(capacity)` | 크기가 정해진 큐. 무제한 큐(`new LinkedBlockingQueue<>()`)면 서버가 죽었을 때 팀 앱 메모리가 계속 는다 |
| **`offer`** (`put` 아님) | `put`은 꽉 차면 **빈자리가 날 때까지 기다린다**. `offer`는 바로 false. 이 한 단어가 규칙 5의 핵심 |
| `AtomicInteger dropped` | 여러 요청 스레드가 동시에 `++`하면 일반 int는 숫자가 빠진다 |
| `dropped.getAndSet(0)` | 읽기와 0으로 되돌리기를 한 번에. 따로 하면 그 사이에 버려진 1건이 사라진다 |
| `queue.drainTo(out, max)` | 한 번에 max개까지 꺼낸다. `poll`을 반복하는 것보다 잠금을 덜 건다 |
| 생성자: `capacity < 1`이면 기본값 | `new ArrayBlockingQueue<>(0)`은 예외를 던진다. 생성자에서도 예외 금지(규칙 4) |
| `synchronized` 없음 | 큐와 AtomicInteger가 이미 스레드 안전이다 |

**꽉 차면 새 것을 버린다.** 오래된 것을 지우고 새 것을 넣는 방식은 잠금이 더 필요하고 복잡하다. 대신 버린 개수를 `EventBatch.droppedCount`로 서버에 알려서, 못 보낸 사실은 숨기지 않는다. 서버는 이 값을 `ingest_stat.dropped_count`에 쌓는다(A의 AI-62).

### 1-3. null도 "버린 개수"에 센다

처음 버전은 null이면 false만 돌려주고 세지 않았다. 그런데 `EventBuffer` 인터페이스 주석이 **"꽉 찼거나 null이면 false (버린 개수 +1)"**이다. 인터페이스가 약속이니(규칙 2) 거기에 맞췄다. 코드를 쓰기 전에 **인터페이스 주석부터 다시 읽는 습관**이 필요하다.

### 1-4. 테스트 7개가 증명하는 것

| # | 테스트 | 증명하는 것 |
|---|---|---|
| 1 | 용량 1000에서 1001번째 | 꽉 차면 false, 버린 개수 1 |
| 2 | drain 순서·max | 넣은 순서대로(FIFO), max개까지만 |
| 3 | 비어 있으면 빈 리스트 | max 0도 빈 리스트 |
| 4 | takeDroppedCount | 읽은 뒤 0 |
| 5 | null | false, 예외 없음, 버린 개수 +1 |
| 6 | 8스레드 동시 offer | **넣은 것 + 버린 것 = 전체** (숫자가 새지 않음) |
| 7 | 꽉 찬 상태에서 100만 번 | **1초 미만 = 기다리지 않는다는 증거** |

### 1-5. 코드로 보기: 생성자와 drain

```java
public BoundedEventBuffer(int capacity) {
    int safe = capacity < 1 ? Defaults.BUFFER_CAPACITY : capacity;   // 0 이하 → 1000
    this.queue = new ArrayBlockingQueue<>(safe);                     // 배열을 미리 잡는 고정 크기 큐
}

@Override
public List<ErrorEvent> drain(int max) {
    if (max <= 0) return List.of();                                  // ① 불변 빈 리스트
    List<ErrorEvent> out = new ArrayList<>(Math.min(max, queue.size()));   // ② 크기를 미리 잡음
    queue.drainTo(out, max);                                         // ③ 잠금 한 번에 여러 개
    return out;
}
```

| 번호 | 왜 |
|---|---|
| ① | `List.of()`는 매번 새로 만들지 않는 불변 빈 리스트다. 받는 쪽(Sender)은 읽기만 한다 |
| ② | `ArrayList`가 커질 때마다 배열을 다시 만드는 것을 피한다. `max`가 아니라 `min(max, size)`인 이유: 100을 요청해도 3개뿐이면 3칸만 잡는다 |
| ③ | `poll()`을 100번 부르면 잠금을 100번 잡는다. `drainTo`는 한 번 잡고 여러 개를 꺼낸다. 그 사이 팀 앱 스레드의 `offer`가 덜 기다린다(`offer`는 대기하지 않지만, 잠금 경쟁은 짧을수록 좋다) |

`ArrayBlockingQueue`는 **잠금 하나**(`ReentrantLock`)로 넣기·꺼내기를 모두 보호한다. `LinkedBlockingQueue`는 넣는 쪽·꺼내는 쪽 잠금이 따로라 경쟁이 적지만, 노드를 매번 새로 만들어서 GC 부담이 있다. 크기 1000짜리 경계에는 배열 기반이 단순하고 충분하다.

### 1-6. 코드로 보기: 동시성 테스트와 속도 테스트

```java
@Test
void 스레드_8개가_동시에_넣어도_넣은것과_버린것의_합이_맞다() throws Exception {
    BoundedEventBuffer buffer = new BoundedEventBuffer(1000);
    AtomicInteger accepted = new AtomicInteger();
    CountDownLatch start = new CountDownLatch(1);              // ① 출발 신호
    ExecutorService pool = Executors.newFixedThreadPool(8);

    for (int t = 0; t < 8; t++) {
        pool.submit(() -> {
            start.await();                                    // ② 8개 모두 여기서 대기
            for (int i = 0; i < 10_000; i++)
                if (buffer.offer(event(i))) accepted.incrementAndGet();
            return null;                                      // ③ Callable로 만들어 await의 예외 허용
        });
    }
    start.countDown();                                        // ④ 동시에 출발
    pool.shutdown();
    assertTrue(pool.awaitTermination(10, TimeUnit.SECONDS));

    int dropped = buffer.takeDroppedCount();
    assertEquals(1000, accepted.get());                       // 정확히 용량만큼만 들어감
    assertEquals(8 * 10_000, accepted.get() + dropped);       // ⑤ 하나도 새지 않음
}
```

| 번호 | 왜 |
|---|---|
| ①②④ | 스레드를 하나씩 `submit`하면 앞 스레드가 이미 끝나 있어서 **실제로 겹치지 않는다.** 래치로 출발선에 모아 두었다가 동시에 놓아야 경쟁이 생긴다 |
| ③ | `return null`이 있으면 람다가 `Callable`이 되어 `start.await()`의 checked 예외를 던질 수 있다. `Runnable`이면 try/catch가 필요하다 |
| ⑤ | `dropped`가 일반 `int`였다면 `++`가 겹쳐 숫자가 빠지고 이 합이 틀린다. `AtomicInteger`를 쓴 이유를 이 한 줄이 증명한다 |

```java
@Test
void 꽉_찬_상태에서_100만번_넣어도_1초_안에_끝난다() {
    BoundedEventBuffer buffer = new BoundedEventBuffer(1000);
    ErrorEvent e = event(0);                                  // 객체 생성 시간을 빼려고 하나만
    long startNs = System.nanoTime();                         // currentTimeMillis가 아니라 nanoTime
    for (int i = 0; i < 1_000_000; i++) buffer.offer(e);      // 1000번째 이후는 전부 버려짐
    long elapsedMs = TimeUnit.NANOSECONDS.toMillis(System.nanoTime() - startNs);

    assertTrue(elapsedMs < 1000, "기다리지 않아야 한다. 걸린 시간: " + elapsedMs + "ms");
    assertEquals(1_000_000 - 1000, buffer.takeDroppedCount());
}
```

`offer`를 `put`으로 바꾸면 1001번째에서 **영원히 멈춘다.** 이 테스트는 빨강이 되는 게 아니라 끝나지 않는다(그래서 CI가 멈추면 이런 원인을 의심한다). "기다리지 않는다"를 측정 가능한 숫자(1초)로 바꾼 것이 Jira 완료 기준이다. `nanoTime`은 경과 시간 측정용이고, `currentTimeMillis`는 시계(벽시계)라 NTP 보정으로 뒤로 갈 수도 있다.

## 2. 추가로 알면 좋은 것

### 2-1. PR 전에는 develop을 받아서 다시 돌린다

AI-36 브랜치는 develop을 두 번 받았지만 PR #14까지만 들어가 있었고, 결국 **43커밋**이 밀렸다. 내 변경이 starter 파일 2개뿐이라 충돌은 없지만, **CI는 "develop + 내 변경"으로 돌기 때문에** 최신 develop을 받아 로컬에서 먼저 돌려 봐야 머지 뒤에 develop이 깨지지 않는다.

```powershell
git fetch origin
git merge origin/develop
./gradlew :starter:test     # 내 변경 (몇 초)
./gradlew build             # 전체 (몇 분, Docker 필요)
```

### 2-2. 테스트가 200개를 넘었다

develop에는 테스트 메서드가 201개 있다(파일 39개). 12단계까지 들어오면 239개가 된다. 하위 작업마다 테스트를 같이 쓰는 규칙(규칙 8) 때문이고, 파일당 평균 5개라 과한 것은 아니다. 문제는 개수가 아니라 **무게**다. 22개 클래스가 `@SpringBootTest` + 실제 Postgres라서 컨텍스트가 여러 번 뜨고, 커넥션 상한 100을 넘었다(B가 `max_connections=300`으로 해결). MVP 뒤에는 DB가 필요 없는 테스트를 단위 테스트로 나누면 빨라진다.

### 2-3. 작업 중 생긴 사고 기록

- **`git restore .`**: 윈도우에서 CRLF만 바뀐 파일이 계속 "수정됨"으로 보인다. 실제 변경은 `git diff --ignore-cr-at-eol --stat`으로 확인하고, 내용이 같으면 되돌린다.
- **`index.lock`**: 확인용으로 실행한 `git diff`가 `.git/index.lock`을 남겨 git이 막혔다. 직접 `Remove-Item .git\index.lock`으로 지웠다. 읽기만 할 때는 `GIT_OPTIONAL_LOCKS=0`을 붙이면 index를 갱신하지 않는다.
- **PR 템플릿 버그**: 레포 `pull_request_template.md`에 `## <!-- ... -->`처럼 주석 앞에 `##`가 붙은 줄이 2개 있다. 포매터가 바꾼 것으로 보이며, docs PR로 고쳐야 한다.

## 3. 더 나아가 알면 좋은 것

### 3-1. 다음에 볼 키워드

- `offer` / `put` / `add` — 꽉 찼을 때 false / 대기 / 예외
- `ArrayBlockingQueue` vs `LinkedBlockingQueue` — 잠금 1개 vs 2개, 상한 유무
- CAS(compare-and-set)와 `AtomicInteger`
- `CountDownLatch`로 동시성 테스트 만들기

## 관련 노트

[[AiOps 11 - Starter 구조와 인터페이스]] · [[AiOps 13 - 수집 API (A)]]
