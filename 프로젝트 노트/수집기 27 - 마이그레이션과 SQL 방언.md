---
출처: Claude 대화
작성일: 2026-09-03
tags: [프로젝트노트, 수집기, SQLite, 저장]
---

# 수집기 27 - 마이그레이션과 SQL 방언

> 허브: [[수집기 프로젝트 MOC]]

866건 진짜 데이터가 쌓인 뒤 처음으로 **DB를 지우지 않고** 컬럼을 늘린 기록이다. `source`·`tech_stacks` 두 컬럼을 `ALTER TABLE`로 추가하면서, 마이그레이션 파일을 남기는 방식과 SQL 방언 차이를 배웠다.

## 1. 배운 내용

### 1-1. 이번엔 "지우고 새로"가 불가능했다

moef 확장 때는 가짜 3건뿐이라 DB를 지우고 재시작했다 — 「수집기 23」에서 "공짜 재시작의 마지막 기회"라고 부른 그것. 지금은 866건이 있고 그중 519건은 이미 마감돼 **다시 받을 수 없다.** 지우면 잃는다.

그래서 처음으로 진짜 **마이그레이션**을 했다. #되돌릴수있는가 → [[개념 - 되돌릴 수 있는 결정과 없는 결정]]

### 1-2. 스키마가 어디 사는가 — .sql 파일이 없던 이유

질문에서 시작했다: "처음 스키마 짤 때 .sql 파일이 안 보이는데?"

스키마는 별도 파일이 아니라 **`store.py` 안에 문자열로** 산다.

```python
SCHEMA = "CREATE TABLE IF NOT EXISTS jobs (...)"
def connect():
    conn.executescript(SCHEMA)   # 연결마다 실행
```

| | 코드 안 문자열 (우리) | 별도 .sql 파일 |
| --- | --- | --- |
| 실행 | `connect()`가 자동 | 따로 돌려야 |
| 코드-스키마 버전 | **항상 같이 커밋** | 따로 놀 수 있다 |
| 적합 | 테이블 한둘 | 수십 개 |

테이블 하나짜리라 문자열이 맞았다. "DB 준비"가 `connect()` 안에 완결되어 코드만 있으면 DB가 스스로 생기는 게 무인 운영에 맞았다.

### 1-3. 이제부터 마이그레이션은 파일로 쌓는다

지금까지 스키마 변경 이력이 어디에도 파일로 안 남았다(moef 때는 지우고 재시작). 진짜 `ALTER TABLE`로 가면서, 일회성으로 돌리고 지우면 **"DB가 어떻게 지금 모양이 됐는지"가 증발한다.**

```
collector/migrations/
└── 001_source_tech_stacks.sql    ← 남긴다. 지우지 않는다
```

`cleanup_fake.py`(쓰고 지움)와 다른 취급인 이유 — 그건 데이터 청소였고 이건 **구조의 역사**다. 번호를 붙여 쌓으면 파일 목록 자체가 스키마 연대기가 된다. 자바 생태계의 **Flyway**가 이걸 도구로 만든 것 — 번호 붙은 SQL을 순서대로 적용하고 어디까지 했는지 기록한다.

### 1-4. .sql은 스스로 못 돈다 — 러너가 필요하다

```python
# migrate.py
sql = Path(sys.argv[1]).read_text(encoding="utf-8")
conn = sqlite3.connect("state/collector.db")
conn.executescript(sql)
```

`.sql` 파일은 **어느 DB에 적용할지 스스로 모른다.** 돌리는 쪽(`migrate.py`)이 정한다 — 대상은 항상 `state/collector.db` 하나. 이 러너가 SQL 파일의 `USE` 역할을 대신한다.

### 1-5. 마이그레이션 파일 vs SCHEMA 문자열 — 역할이 다르다

| | 무엇을 | 언제 |
| --- | --- | --- |
| `migrations/001.sql` | **기존 DB를 다음 버전으로** | 손으로 한 번 |
| `store.py`의 SCHEMA | **빈 곳에서 최신 버전으로** | connect마다 자동 |

컬럼을 늘리면 **둘 다** 고쳐야 어긋나지 않는다. 마이그레이션은 이미 있는 866건짜리 DB용, SCHEMA는 나중에 빈 DB에서 시작할 때(새 PC, Actions 첫 실행)용이다.

### 1-6. id 접두사가 소급을 가능하게 했다

```sql
UPDATE jobs SET source = substr(id, 1, instr(id, ':') - 1);
```

`source` 컬럼을 새로 넣었지만 **기존 866건도 채울 수 있었다** — id에 `moef:` 접두사를 박아둔 덕에 거기서 역산했다. 원문(여기선 id 구조)을 남겨두면 나중에 파생 정보를 다시 계산할 수 있다는 원칙이 컬럼 하나로 실현됐다. 「수집기 18」에서 접두사를 박은 이유가 여기서 회수됐다.

## 2. SQL 방언 (dialect)

### 2-1. `TEXT DEFAULT ''` 에러가 사실은 MySQL 것이었다

마이그레이션 SQL을 짜서 돌렸더니 이 에러가 났다.

```
BLOB, TEXT, GEOMETRY or JSON column 'source' can't have a default value
```

**이건 SQLite가 아니라 MySQL 에러다.** `GEOMETRY`라는 타입 이름이 증거 — SQLite엔 그런 타입이 없다. 즉 그 SQL이 collector.db가 아니라 **수업용 MySQL 서버에서 실행됐다**(MySQL 클라이언트에서 돌린 것).

| | MySQL | SQLite |
| --- | --- | --- |
| `TEXT` 컬럼에 `DEFAULT ''` | **금지** | **허용** |

같은 SQL이 엔진마다 되고 안 되는 것 — 이게 **SQL 방언**이다. `CREATE TABLE IF NOT EXISTS`처럼 겹치는 표준부가 크지만, 타입 체계·기본값 규칙 같은 가장자리는 엔진마다 다르다.

### 2-2. .sql 파일은 "어디서 도느냐가 내용의 절반"

그래서 `migrate.py`가 하는 일이 중요하다 — **대상 DB를 고정**한다. 항상 `state/collector.db`. SQL 파일만 보면 어느 엔진용인지 모르고, 러너가 그걸 정한다.

SQLite엔 `USE`가 없다(「수집기 06-1」: 서버가 없으니 "서버 안 여러 DB 중 고르기"라는 개념 자체가 없다). 파일 하나가 곧 DB 하나라, `connect(경로)`가 곧 `USE`다.

## 3. 더 나아가 알면 좋은 것

- `ALTER TABLE`의 SQLite 제약 — 컬럼 삭제·타입 변경은 최근 버전에야 지원, 보통 테이블 재생성으로
- Flyway / Liquibase — 마이그레이션 버전 관리 도구 (WMS에서 Spring Boot 쓰면 만난다)
- `PRAGMA user_version` — SQLite에 스키마 버전을 손으로 기록하는 방법
- `ATTACH DATABASE` — SQLite에서 파일 여러 개를 한 연결에 붙여 조인 (논문 DB 분리할 때)
- ANSI SQL 표준과 방언 — 어디까지가 이식 가능한가

## 관련 노트

[[수집기 26 - jumpit 어댑터와 2단계 수집]]
