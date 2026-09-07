---
출처: Claude 대화
작성일: 2026-09-03
tags: [프로젝트, sql]
---

# 변경이력 - store.py

SQLite 저장 계층의 진화. **저장소는 스키마가 계약이라**, 변화가 늘 컬럼·판정과 얽힌다. 누적형.

## 변경 궤적

| 커밋 | 무엇 | 컬럼 수 |
| --- | --- | --- |
| SQLite 저장 계층 추가 | 4컬럼, connect/count/upsert | 4 |
| moef 어댑터 | 15컬럼으로 확장, COLUMNS 도입 | 15 |
| source·tech_stacks 마이그레이션 | 17컬럼, all_ids 추가 | 17 |

## 1. 시작 — 4컬럼, 세 함수

```sql
CREATE TABLE IF NOT EXISTS jobs (
    id TEXT PRIMARY KEY, title TEXT NOT NULL,
    company TEXT, first_seen_at TEXT NOT NULL
);
```

`connect`(열기)·`count_jobs`(세기)·`upsert_jobs`(넣기). `IF NOT EXISTS`·`PRIMARY KEY`·`INSERT OR IGNORE`가 이때 다 등장했다(「수집기 06·07」). 스키마가 `.sql` 파일이 아니라 **문자열로 store.py 안에 산다** — connect마다 실행되니 코드만 있으면 DB가 스스로 생긴다.

## 2. moef 확장 — 4에서 15컬럼, COLUMNS 리스트 도입

진짜 API 필드에 맞춰 컬럼이 11개 늘었다. 이때 **upsert 방식이 바뀌었다.**

```python
COLUMNS = ["id", "title", ..., "raw", "first_seen_at"]
placeholders = ", ".join("?" for _ in COLUMNS)
conn.executemany(f"INSERT OR IGNORE INTO jobs ({', '.join(COLUMNS)}) VALUES ({placeholders})", ...)
```

이전엔 컬럼 이름을 SQL 문자열에 한 번, 튜플 순서에 또 한 번 적었다. 컬럼 15개면 그 이중 나열이 위험(「수집기 07」의 순서 어긋남 함정). **`COLUMNS` 하나에서 SQL과 값 순서를 둘 다 생성**해 어긋날 수 없게 했다. 여기서 `IF NOT EXISTS`가 옛 DB를 안 고쳐주는 함정도 처음 만났다(「수집기 23」) — 가짜 3건뿐이라 DB를 지우고 재시작.

## 3. source·tech_stacks — 첫 진짜 마이그레이션 + all_ids

866건 진짜 데이터가 쌓인 뒤라 **DB를 지울 수 없었다.** 처음으로 `ALTER TABLE`로 갔다(「수집기 27」).

```python
def all_ids(conn) -> set:
    return {row[0] for row in conn.execute("SELECT id FROM jobs")}
```

`all_ids`가 새로 생긴 게 중요하다 — store가 처음으로 **"신규 판정 재료를 바깥에 제공"**하는 역할을 얻었다. jumpit이 상세 호출을 아끼려면 "이미 아는 id"가 필요했고, main이 그걸 `all_ids`로 받아 어댑터에 넘긴다. SCHEMA 문자열과 COLUMNS에도 두 컬럼을 더했다 — **마이그레이션은 기존 DB용, SCHEMA는 빈 DB용**이라 둘 다 고쳐야 한다.

## 관찰

### 저장소의 변화는 늘 "판정"과 얽힌다

store의 세 번의 변화가 전부 중복·신규 판정과 연결됐다.

| 단계 | 판정 장치 |
| --- | --- |
| 4컬럼 | `PRIMARY KEY` + `INSERT OR IGNORE` (중복 자동 거부) |
| 15컬럼 | 같음, 컬럼만 확장 |
| 17컬럼 | `all_ids` 추가 — **저장 전 판정**을 어댑터에 위임 |

3단계에서 판정이 **두 층**이 됐다. store 내부의 `INSERT OR IGNORE`(저장 시)와, `all_ids`로 밖에 내보내는 사전 판정(수집 시). moef는 전자로 충분했지만 jumpit은 후자가 있어야 상세 요청을 아낀다.

### 스키마가 두 곳에 산다

같은 스키마가 SCHEMA 문자열(빈 DB용)과 migrations/(기존 DB용) 두 곳에 있다. 컬럼을 늘리면 **둘 다** 고쳐야 어긋나지 않는다. 지금은 손으로 챙기지만, 컬럼이 더 늘면 이 이중 관리가 부담이 된다 — Flyway 같은 도구가 푸는 문제다.

### 아직 안 바꾼 것

- `hire_type`은 moef·jumpit 둘 다 잘 안 채운다 — 실효 낮은 컬럼. 관측 더 하고 판단
- 재공고 판정용 컬럼(content_hash 등) — 설계 변경 기록 1번의 유예 항목. 데이터로 재공고 34쌍이 확인됐으니 곧 결정거리
