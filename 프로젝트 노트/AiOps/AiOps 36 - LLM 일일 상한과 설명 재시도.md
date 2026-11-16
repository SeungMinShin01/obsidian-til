---
출처: Claude 대화
작성일: 2026-11-15
tags: [프로젝트, java]
---

# AiOps - LLM 일일 상한과 설명 재시도

> 허브: [[AiOps 프로젝트 MOC]]

**PR #53 `[AI-57] LLM 일일 상한과 설명 재시도`** — 커밋 8개, 11/15 머지. LLM 비용이 통제 없이 나가지 않게 하루 상한을 두고, 상한·장애로 설명을 못 만든 그룹은 5분마다 다시 시도한다. 7단계(LLM)에서 내 몫은 이것으로 끝이고, 처리 흐름에 연결하는 AI-56 2부만 B의 AI-60을 기다린다.

## 1. 배운 내용

### 1-1. 이 PR이 하는 일

```
ExplanationService.explain
   └ LlmQuota.tryAcquire  → false면 WARN 후 끝 (설명 NULL 유지)

ExplanationRetryScheduler (5분마다, 서버 시작 2분 뒤부터)
   키 없음 → 아무것도 안 함
   팀마다 (정지 팀 제외): TenantContext set → 설명 NULL + 최근 24시간 그룹 조회 → explain → clear
   QUOTA_EXCEEDED가 나오면 그 자리에서 중단
```

### 1-2. 코드로 보기: 세기와 검사를 한 문장으로

```sql
INSERT INTO llm_usage (day, call_count) VALUES (CAST(:day AS date), 1)        -- ①
ON CONFLICT (day) DO UPDATE SET call_count = llm_usage.call_count + 1         -- ②
WHERE llm_usage.call_count < :limit                                           -- ③
RETURNING call_count                                                          -- ④
```

| 번호 | 뜻 |
|---|---|
| ① | 오늘 행이 없으면 1로 만든다 |
| ② | 있으면 +1 |
| ③ | 단, 상한보다 작을 때만. 아니면 **아무것도 바꾸지 않는다** |
| ④ | 바꾼 행이 있으면 돌려준다 → 행이 오면 허용, 안 오면 상한 |

"읽고 → 비교하고 → 올린다"를 Java로 하면 동시에 들어온 두 호출이 둘 다 "아직 199"를 읽고 통과한다. 한 문장이면 DB가 행을 잠그고 한 번에 하나씩 처리한다. 테스트 `concurrent`가 스레드 10개·상한 5로 **정확히 5개만** 허용되는지 본다.

```java
if (limit <= 0) {
    return false;   // INSERT 쪽(①)에는 상한 검사가 없어서 0 이하는 여기서 막는다
}
```

상한 검사 ③은 UPDATE에만 붙는다. 그날 첫 호출은 INSERT라 검사 없이 들어간다. 상한이 0이면 첫 호출이 통과해 버리므로 Java에서 먼저 막았다.

### 1-3. 왜 DB인가, 왜 날짜를 서버에서 구하나

- **메모리 카운터**는 서버를 재시작하면 0이 된다. 서버가 2대가 되면 상한이 2배가 된다.
- 날짜는 DB의 `CURRENT_DATE`가 아니라 `LocalDate.now(ZoneId.of("Asia/Seoul"))`. DB 시간대가 UTC면 한국 오전 9시에 날짜가 바뀐다. DB 설정에 기대지 않는다.
- `@Transactional(propagation = REQUIRES_NEW)`: 부르는 쪽 트랜잭션과 상관없이 바로 커밋한다. 세는 것은 뒤 작업이 실패해도 되돌리지 않는다(LLM은 이미 불렸거나 불릴 것이므로).

### 1-4. 코드로 보기: explain이 결과를 돌려준다

```java
public enum Outcome { SAVED, ALREADY_DONE, SKIPPED, NO_ANSWER, QUOTA_EXCEEDED, FAILED }
```

스케줄러가 "상한이면 멈춘다"를 하려면 결과를 알아야 한다. `boolean`으로는 "LLM 장애"와 "상한"을 구분할 수 없다. 장애면 다음 그룹을 계속 시도하고, 상한이면 나머지도 전부 거절당할 테니 멈춘다.

### 1-5. 재시도를 별도 스케줄러로 뺀 이유

기존 `ReprocessScheduler`(A 작성)는 "짧게 끝난다"가 전제다. LLM 호출은 건당 최대 20초라, 섞으면 이벤트 재처리까지 늦어진다. 스케줄러 스레드는 2개뿐이다.

재시도는 새 경로가 아니다. **같은 `explain`을 탄다.** 한 번만 저장, 트랜잭션 밖 호출, 상한이 전부 그대로 적용된다.

### 1-6. 키가 없으면 돌지 않는다

키가 없으면 `LlmClient`는 가짜 구현이고 "(가짜 응답)"을 돌려준다. 재시도가 돌면 설명 없는 그룹이 전부 가짜 글로 채워진다. 테스트에서는 더 나쁘다 — `@SpringBootTest` 컨텍스트가 2분 넘게 살아 있으면 스케줄러가 끼어들어 다른 테스트가 만든 그룹을 채운다(가끔만 깨지는 테스트). 그래서 `run()` 첫 줄에서 `isConfigured()`가 아니면 바로 끝낸다.

## 2. 설계와 다르게 한 곳

| 명세 | 실제 | 이유 |
|---|---|---|
| `ReprocessScheduler.run()` 안에 재시도 | 별도 `ExplanationRetryScheduler` | 1-5 |
| 언급 없음 | 키 없으면 재시도 안 함, 정지 팀 제외 | 1-6, 정지 팀에 비용을 쓰지 않으려고 |
| `explain`이 void | `Outcome` 반환 | 1-4 |
| `tryAcquire()` | `tryAcquire(Long tenantId)` + 테스트용 `tryAcquire(LocalDate, int)` | 팀별 상한 자리. 테스트가 오늘 칸을 건드리지 않게 옛 날짜로 센다 |

## 3. 팁

- 테스트 이름이 영어·한글로 섞여 있다. **Jira 명세에 이름이 적힌 테스트는 그 이름 그대로**(완료 기준에서 바로 검색되게), 추가한 테스트는 한글.
- `new LlmQuota(null, 0) { @Override tryAcquire … }`: 테스트에서 "항상 거절"을 만들 때. 덮어쓴 메서드만 불리므로 `EntityManager`는 null이어도 된다.
- 실제 호출 확인은 **아직 안 불러 본 에러 주소**로 해야 한다. 이미 있는 그룹은 24시간 범위 밖이라 재시도 대상이 아니다.

## 4. 남은 것

- 실제 키로 1회 호출 (형식, 길이, 로그에 키 없는지)
- 팀별 상한: `llm_usage`에 팀 칸이 없어 새 마이그레이션이 든다 (결정 대기)
- AI-56 2부가 붙으면 처리 스레드와 재시도가 같은 그룹에 LLM을 두 번 부를 수 있다 → 재시도 대상을 "생긴 지 2분 넘은 그룹"으로 좁힌다

## 관련 노트

[[AiOps 35 - 로컬 환경변수를 env 파일로]] · [[AiOps 37 - 시작 실패 전송과 flushNow]]
