---
출처: Claude 대화
작성일: 2026-11-10
tags: [프로젝트, java]
---

# AiOps - 처리 풀과 그룹화 (A)

> 허브: [[AiOps 프로젝트 MOC]]

**6단계, 담당 A(김지환).** PR #16 `[AI-50] 처리 스레드 풀` · #17 `[AI-51] 지문 계산` · #18 `[AI-52] 그룹 upsert` · #19 `[AI-53] 재처리 스케줄러`. 11/3~11/4 머지. 저장된 이벤트를 "같은 원인끼리" 묶고, 새 그룹만 다음 단계(LLM·디스코드)로 넘긴다.

> 코드는 11/10 develop 기준이다. `TenantContext` 줄은 11단계(#23)에서 B가 넣은 것이다.

## 0. 흐름

```
(2단계) 커밋 → ErrorsStoredListener
   → ErrorProcessor.process(tenantId, ids)        @Async — aiops-proc- 스레드 4개, 큐 1000      (#16)
       for 이벤트: GroupingService.groupOne()      이벤트마다 짧은 트랜잭션                       (#18)
          payload JSON → ErrorEvent → 맨 안쪽 원인 + 스택 → Fingerprinter (#17) → 지문
          → GroupUpserter: INSERT … ON CONFLICT … RETURNING id, (xmax = 0)                     (#18)
          → error_event.group_id 연결, processed=true
       새 그룹 id 목록 → (7단계 LLM, 8단계 디스코드 자리)
ReprocessScheduler (aiops-sched-): processed=false && 2분 지난 것 → 같은 process()               (#19)
```

## 1. #16 처리 스레드 풀 (AI-50)

### 코드: 풀 설정 (`AsyncConfig`)

```java
@Bean("aiopsProcessingExecutor")
public ThreadPoolTaskExecutor aiopsProcessingExecutor(
        @Value("${aiops.processing.threads:4}") int threads,
        @Value("${aiops.processing.queue:1000}") int queue) {
    ThreadPoolTaskExecutor executor = new ThreadPoolTaskExecutor();
    executor.setCorePoolSize(threads);
    executor.setMaxPoolSize(threads);                // ① core = max
    executor.setQueueCapacity(queue);
    executor.setThreadNamePrefix("aiops-proc-");     // ② 로그에서 처리 풀 구분
    executor.setRejectedExecutionHandler(new ThreadPoolExecutor.CallerRunsPolicy());   // ③
    executor.setWaitForTasksToCompleteOnShutdown(true);
    executor.setAwaitTerminationSeconds(10);         // ④ 종료 때 최대 10초만 기다림
    return executor;
}
```

| 번호 | 왜 |
|---|---|
| ① | `ThreadPoolExecutor`는 **큐가 꽉 차야** max까지 스레드를 늘린다. 큐가 1000이면 사실상 늘어날 일이 없어서 같게 뒀다 |
| ③ | 큐까지 꽉 차면 거절(예외)하지 않고 **부른 스레드가 직접 실행**한다. 이벤트를 잃는 것보다 수집이 잠깐 느려지는 게 낫다는 판단 |
| ④ | 하던 처리는 마무리하되, 서버 종료가 끝없이 늘어지지 않게 |

`getAsyncUncaughtExceptionHandler()`도 등록했다. **`@Async void` 메서드의 예외는 아무도 받지 않아 조용히 사라진다.** 그래서 로그로 남긴다.

### 코드: 처리 입구 (`ErrorProcessor.process`)

```java
@Async("aiopsProcessingExecutor")
public void process(Long tenantId, List<Long> eventIds) {
    TenantContext.set(tenantId);                                   // ① (#23) 처리 스레드에서 팀 다시 설정
    try {
        List<Long> newGroupIds = new ArrayList<>();
        for (Long eventId : eventIds) {
            try {
                Long newGroupId = groupingService.groupOne(tenantId, eventId);
                if (newGroupId != null) newGroupIds.add(newGroupId);
            } catch (RuntimeException e) {                         // ② 한 건 실패해도 나머지 계속
                log.error("이벤트 처리 실패 tenantId={} eventId={}", tenantId, eventId, e);
            }
        }
        log.info("새 그룹 {}개 tenantId={}", newGroupIds.size(), tenantId);   // ③ 7·8단계가 붙을 자리
    } finally {
        TenantContext.clear();                                     // ④ 스레드는 재사용된다
    }
}
```

| 번호 | 왜 |
|---|---|
| ① | `TenantContext`는 ThreadLocal이라 **요청 스레드에서 처리 스레드로 넘어오지 않는다.** 그래서 팀을 파라미터로 받는다(D-081 `process(tenantId, ids)` 고정) |
| ② | 실패한 이벤트는 `processed=false`로 남아 재처리 스케줄러가 다시 줍는다 |
| ③ | 지금은 로그만. 여기에 `explanationService.explain` → `notifier.notifyNewGroup`이 붙는다 |
| ④ | 지우지 않으면 다음 작업이 이 팀을 물려받는다. 격리 사고의 전형 |

`@Async`가 동작하려면 **다른 Bean에서 불러야** 한다. 스프링이 프록시를 끼워 넣는 방식이라 같은 클래스 안에서 `this.process()`로 부르면 그냥 동기로 실행된다. 리스너·스케줄러가 별도 Bean이라 괜찮다.

테스트 `ErrorProcessorNonBlockingTest`: 처리가 3초 걸려도 커밋 쪽은 500ms 안에 끝난다. "받기는 빠르게, 처리는 따로"를 그대로 증명한다.

## 2. #17 지문 계산 (AI-51) — 선행 테스트 통과

```java
static final List<String> FRAMEWORK_PREFIXES = List.of(
        "java.", "javax.", "jakarta.", "jdk.", "sun.",
        "org.springframework.", "org.hibernate.", "com.zaxxer.", "org.apache.", "dev.aiops.");

public String fingerprint(String exceptionType, List<StackFrame> frames) {
    List<String> teamFrames = new ArrayList<>(), allFrames = new ArrayList<>();
    for (StackFrame frame : frames) {
        String name = frame.className() + "#" + frame.methodName();   // ① 줄 번호 없음
        allFrames.add(name);
        if (!isFramework(frame.className())) teamFrames.add(name);
    }
    List<String> chosen = teamFrames.isEmpty() ? allFrames : teamFrames;   // ② 팀 코드 우선
    StringBuilder text = new StringBuilder(exceptionType);
    for (int i = 0; i < chosen.size() && i < 3; i++) text.append("|").append(chosen.get(i));   // ③ 상위 3개
    return sha256Hex(text.toString());     // "NullPointerException|a.B#c|a.B#d|a.E#f" → 64자
}
```

| 번호 | 왜 |
|---|---|
| ① | 줄 번호를 넣으면 **코드 한 줄만 추가해도 다른 에러로 분류**된다. 메서드까지만 본다 |
| ② | 스택 위쪽은 대부분 Spring·JDK다. 팀 코드가 "어디서 났는지"를 더 잘 말해 준다 |
| ③ | 3개면 같은 메서드의 다른 호출 경로를 구분하면서, 깊은 프레임워크 변화에는 흔들리지 않는다 |

**Spring·JPA 의존이 없는 순수 클래스**라서 `new Fingerprinter()`로 만들어 쓴다. 테스트도 스프링 없이 돈다.

내가 먼저 쓴 `FingerprinterTest` 9개를 **수정 없이 통과**했다(D-080, 규칙 9가 처음으로 제대로 돌아간 사례).

## 3. #18 그룹 upsert (AI-52)

### 코드: SQL 한 문장으로 "찾거나 만들기"

```sql
INSERT INTO error_group (tenant_id, fingerprint, exception_type, top_frame, first_env,
                         first_seen_at, last_seen_at, occurrence_count)
VALUES (:tenantId, :fingerprint, :exceptionType, CAST(:topFrame AS varchar), :env,
        CAST(:seenAt AS timestamptz), CAST(:seenAt AS timestamptz), 1)
ON CONFLICT (tenant_id, fingerprint) DO UPDATE
  SET occurrence_count = error_group.occurrence_count + 1,
      last_seen_at = GREATEST(error_group.last_seen_at, EXCLUDED.last_seen_at)   -- ①
RETURNING id, (xmax = 0) AS is_new                                               -- ②
```

| 번호 | 왜 |
|---|---|
| ① | 처리 순서가 뒤바뀌어 **옛 이벤트가 늦게 처리돼도** 마지막 발생 시각이 뒤로 가지 않는다 |
| ② | Postgres에서 `xmax`는 행을 지운·바꾼 트랜잭션 번호다. **방금 INSERT된 행은 0**, UPDATE된 행은 0이 아니다. 조회를 따로 하지 않고 "새 그룹인지"를 안다 |

**코드로 "조회 → 없으면 INSERT"를 하면** 같은 에러가 동시에 8개 들어올 때 그룹이 여러 개 생긴다. 테스트 `스레드 8개 동시 → 행 1개, isNew 정확히 1번`이 그걸 막았다는 증거다.

### 코드: 이벤트 1건 처리 (`GroupingService.groupOne`)

```java
@Transactional                                                   // 이벤트마다 짧은 트랜잭션
public Long groupOne(Long tenantId, Long eventId) {
    ErrorEventEntity event = errorEventRepository.findById(eventId).orElse(null);
    if (event == null || !event.getTenantId().equals(tenantId) || event.isProcessed())
        return null;                                             // ① 두 번 불려도 안전

    ErrorEvent payload = objectMapper.readValue(event.getPayload(), ErrorEvent.class);
    String type = payload.exceptionType();
    if (!payload.causes().isEmpty())
        type = payload.causes().get(payload.causes().size() - 1).type();   // ② 맨 안쪽 원인

    String fingerprint = fingerprinter.fingerprint(type, payload.stack());
    UpsertResult result = groupUpserter.upsert(tenantId, event.getEnv(), fingerprint, summary);
    event.assignGroup(result.groupId());                         // ③ 더티 체킹으로 커밋 때 UPDATE
    return result.isNew() ? result.groupId() : null;
}
```

| 번호 | 왜 |
|---|---|
| ① | 재처리 스케줄러와 리스너가 같은 이벤트를 동시에 집어도 한 번만 처리된다(멱등) |
| ② | `RuntimeException("x", new SQLException(...))`처럼 감싼 예외는 **진짜 원인이 안쪽**에 있다. 바깥 타입으로 묶으면 다른 원인들이 한 그룹에 섞인다 |
| ③ | 엔티티 필드만 바꾸면 트랜잭션이 끝날 때 JPA가 알아서 UPDATE한다 |

이벤트마다 트랜잭션을 나눈 이유: 100개를 한 트랜잭션으로 묶으면 **하나만 깨져도 100개가 다 롤백**된다.

## 4. #19 재처리 스케줄러 (AI-53)

```java
@Scheduled(fixedDelayString = "${aiops.reprocess.interval:PT5M}",       // ① 끝난 뒤 5분 쉬고
           initialDelayString = "${aiops.reprocess.initial-delay:PT1M}") // ② 시작 1분 뒤 첫 실행
public void run() {
    Instant cutoff = Instant.now().minus(minAge);                         // ③ 2분 지난 것만
    for (TenantEntity tenant : tenantRepository.findAll()) {              // (#23) 팀마다
        List<Long> ids = unprocessedOf(tenant.getId(), cutoff, batch - total);   // set → 조회 → clear
        if (!ids.isEmpty()) errorProcessor.process(tenant.getId(), ids);  // ④ 같은 입구
    }
}
```

| 번호 | 왜 |
|---|---|
| ① | `fixedRate`는 이전 실행이 안 끝나도 다시 돈다. `fixedDelay`는 **겹치지 않는다** |
| ② | 서버·테스트가 뜨자마자 돌면 테스트 데이터를 건드려 결과가 흔들린다 |
| ③ | 방금 들어와서 처리 풀 큐에 있는 이벤트를 또 집지 않게 하는 유예 |
| ④ | 재처리용 경로를 따로 만들지 않는다. **처리 로직은 한 곳**이라 고칠 곳도 한 곳 |

스케줄러 풀(`aiops-sched-`, 2개)을 처리 풀과 분리했다. 스케줄러가 처리 풀 스레드를 차지하면 실시간 처리가 밀린다.

## 5. 리뷰 메모

| 항목 | 내용 | 조치 |
|---|---|---|
| ⚠ **`dev.aiops.` 접두사** | 프레임워크 접두사에 `dev.aiops.`가 있다(Starter 자기 프레임을 빼려는 것). 그런데 **sample-app 패키지가 `dev.aiops.sample`**이라 샘플 앱 프레임도 "프레임워크"로 빠진다. 그러면 지문이 JDK 프레임 기준이 되고, `top_frame`(디스코드 "위치")도 `java.lang.String#length` 같은 값이 나온다 | **내 선행 테스트 명세 문제.** `dev.aiops.starter.`·`dev.aiops.server.`로 좁히거나 sample-app 패키지를 바꾼다. 마일스톤 1·2 시연 전에 결정 |
| ⚠ **env와 그룹** | 그룹 유일 키가 `(tenant_id, fingerprint)`라 env가 빠져 있다. **local에서 먼저 본 에러가 prod에서 나면 새 그룹이 아니어서** 알림이 가지 않는다(알림 채널도 `first_env`) | 설계 질문. prod 첫 발생 알림이 필요한지 결정 |
| 오래된 주석 | `findUnprocessed` 주석의 "RLS가 켜지면 팀별 조회로 바꿈" — 쿼리는 그대로지만 팀마다 set하고 부르므로 이미 팀별로 동작 | 주석만 정리 |

## 6. 내가 알아야 할 것

- **7단계 LLM(내 담당)은 `ErrorProcessor`의 ③ 자리에 붙는다.** 트랜잭션 밖에서, 새 그룹마다 한 번(AI-56). 이미 `TenantContext`가 설정된 상태라 그 안에서 부르면 RLS를 통과한다.
- `top_frame`이 디스코드 embed의 "위치"가 된다. 위 리뷰 메모 1번을 고치지 않으면 시연 화면이 어색하다.

## 7. 다음에 볼 키워드

- `ON CONFLICT … RETURNING`과 `xmax`
- `CallerRunsPolicy`, core/max/queue의 관계
- `@Async` 프록시와 자기 호출(self-invocation)
- `fixedDelay` vs `fixedRate`

## 관련 노트

[[AiOps 13 - 수집 API (A)]] · [[AiOps 15 - 보관 삭제와 수집 통계 (A)]]
