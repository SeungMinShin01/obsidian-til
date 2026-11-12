---
출처: Claude 대화
작성일: 2026-11-10
tags: [프로젝트, java]
---

# AiOps - 보관 삭제와 수집 통계 (A)

> 허브: [[AiOps 프로젝트 MOC]]

**9단계. 원래 B 담당이었는데 A가 진행했다.** PR #21 `[AI-61] 보관 삭제` · #22 `[AI-62] 수집 통계`. 11/4 머지. Jira 담당은 아직 B로 남아 있을 수 있다.

> 코드는 11/10 develop 기준. 팀마다 `TenantContext`를 설정하는 부분은 11단계(#23)에서 B가 넣었다.

## 1. #21 보관 삭제 (AI-61)

### 코드: 하루 한 번, 팀마다, env마다 (`RetentionScheduler.run`)

```java
@Scheduled(cron = "${aiops.retention.cron:0 0 4 * * *}", zone = "Asia/Seoul")   // ① 매일 04:00 서울
public void run() {
    List<TenantEntity> tenants = tenantRepository.findAll();      // tenant는 RLS 없음
    for (TenantEntity tenant : tenants) {
        if (Thread.currentThread().isInterrupted()) break;         // ② 서버 종료 중이면 멈춤
        TenantContext.set(tenant.getId());                         // (#23) 팀 설정 → RLS가 이 팀 행만 보여 줌
        try {
            localTotal += purgeEnv(tenant.getId(), "local", localDays);   // 3일
            prodTotal  += purgeEnv(tenant.getId(), "prod",  prodDays);    // 14일
        } finally {
            TenantContext.clear();
        }
    }
}
```

- ① `zone`을 주지 않으면 서버 OS 시간대를 따른다. 운영 VM이 UTC면 한국 시간 오후 1시에 돈다.
- ② 종료 신호(interrupt)를 존중한다. 삭제 중이라도 서버가 내려갈 수 있어야 한다.

### 코드: 0건이 될 때까지 묶음으로 (`purgeEnv`)

```java
Instant cutoff = Instant.now().minus(Duration.ofDays(days));
int deleted;
do {
    deleted = purger.purgeBatch(env, cutoff, batchSize);    // ① 묶음 하나 = 트랜잭션 하나
    total += deleted;
    if (deleted > 0 && pauseMs > 0) Thread.sleep(pauseMs);  // ② 묶음 사이에 쉼
} while (deleted > 0);
```

```sql
-- ErrorEventRepository.deleteOlderThan
DELETE FROM error_event
WHERE id IN (
    SELECT id FROM error_event
    WHERE env = :env AND received_at < CAST(:cutoff AS timestamptz)
    ORDER BY received_at
    LIMIT :batch                                             -- ③
)
```

| 번호 | 왜 |
|---|---|
| ① | `ErrorEventPurger.purgeBatch`가 따로 `@Transactional`이다. 묶음마다 **바로 커밋**해서 락을 오래 잡지 않는다. 스케줄러 메서드 자체에 `@Transactional`을 붙였다면 전부 한 트랜잭션이 됐을 것이다 |
| ② | DB가 숨 돌릴 틈. 그 사이에 수집 요청이 끼어든다 |
| ③ | Postgres의 `DELETE`에는 `LIMIT`이 없다. 그래서 "id를 batch개 골라서 그 id만 지운다" 모양으로 쓴다 |

**왜 Purger를 따로 뺐나:** `@Transactional`은 프록시 방식이라 **같은 클래스 안에서 부르면 적용되지 않는다.** 스케줄러 안의 private 메서드에 붙이면 트랜잭션이 생기지 않는다. 그래서 다른 Bean(`ErrorEventPurger`)으로 분리했다.

**지우는 것은 `error_event`(원본)뿐이다.** `error_group`의 횟수·첫 발생 시각, `ingest_stat`, `app_snapshot`은 남는다. 3일이 지나도 "이 에러가 몇 번 났다"는 그대로 보인다.

## 2. #22 수집 통계 (AI-62)

### 코드: 더하기를 DB에 맡긴다 (`IngestStatRecorder.record`)

```java
@Transactional                                              // ① 부른 쪽 트랜잭션에 합류
public void record(Long tenantId, String env, int received, int dropped) {
    int safeDropped = dropped < 0 ? 0 : dropped;            // ② 음수 방어 (+ WARN)
    em.createNativeQuery("""
        INSERT INTO ingest_stat (tenant_id, env, day, received_count, dropped_count)
        VALUES (:tenantId, :env, :day, :received, :dropped)
        ON CONFLICT (tenant_id, env, day) DO UPDATE
          SET received_count = ingest_stat.received_count + EXCLUDED.received_count,
              dropped_count  = ingest_stat.dropped_count  + EXCLUDED.dropped_count
        """)
        .setParameter("day", LocalDate.now(ZoneId.of("Asia/Seoul")))   // ③ 서울 기준 날짜
        ...
        .executeUpdate();
}
```

| 번호 | 왜 |
|---|---|
| ① | 기본 전파(REQUIRED)라 `IngestService.store`의 트랜잭션에 들어간다. **저장이 롤백되면 통계도 롤백**된다(`IngestStatRollbackTest`). `@Async`나 새 트랜잭션으로 빼지 않은 이유다 |
| ② | 서버는 Starter가 보낸 값을 추정하지 않는다. 음수만 0으로 보정한다 |
| ③ | DB의 `CURRENT_DATE`는 DB 서버 시간대를 따른다. 자바에서 서울 날짜를 계산해 넘기면 서버 설정과 상관없이 같다 |

"읽고 → 더하고 → 저장"을 코드로 하면 동시에 두 요청이 같은 값을 읽어 하나가 사라진다(lost update). **`+ EXCLUDED.`를 DB 한 문장으로 하면** 10스레드가 동시에 와도 합계가 정확하다(테스트 `concurrent`: 10스레드, 합계 100, 행 1개).

## 3. 설계와 다르게 한 곳

| PR | 다른 점 | 판단 |
|---|---|---|
| #21 | `retention/` 대신 D-088 구조(`scheduler/`, `service/`) | 레포 규칙이 맞음 |
| #21 | `pause-ms` 설정 추가 | 운영 조절용 |
| #22 | UTC → Asia/Seoul | Jira대로 |
| #22 | upsert를 리포지토리에서 Recorder로 이동 | 기록 책임을 한 곳에 |

## 4. 리뷰 메모

| 항목 | 내용 |
|---|---|
| 팀 수만큼 반복 | 팀이 100개면 04:00에 200번(local·prod)의 삭제 루프가 돈다. MVP 규모에서는 문제없다 |
| PR 제목 | #21은 브랜치 이름 그대로(`Feat/server ai 61 retention purge`). 기능 영향 없음 |

## 5. 내가 알아야 할 것

- **Starter `takeDroppedCount()`(AI-36)가 여기까지 이어진다.** 버퍼가 꽉 차서 버린 개수 → `EventBatch.droppedCount` → `IngestService.store` → `record(..., dropped)` → `ingest_stat.dropped_count`. 콘솔·리포트에서 "몇 건을 못 받았는지"의 근거가 된다.

## 6. 다음에 볼 키워드

- 대량 DELETE를 나누는 이유(락·WAL·autovacuum)
- `@Transactional` 자기 호출 문제 — 별도 Bean으로 빼는 이유
- lost update와 `ON CONFLICT … SET x = x + EXCLUDED.x`
- `@Scheduled(cron, zone)`

## 관련 노트

[[AiOps 14 - 처리 풀과 그룹화 (A)]] · [[AiOps 16 - 디스코드 알림 (B)]]
