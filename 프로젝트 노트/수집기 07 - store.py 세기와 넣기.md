---
출처: Claude 대화
작성일: 2026-08-12
tags: [프로젝트노트, 수집기, SQLite, Python, 저장]
---

# 수집기 07 - store.py 세기와 넣기

> 허브: [[수집기 프로젝트 MOC]]

「수집기 06 - SQLite 저장 계층」에서 `connect()`까지 만들었다. 여기서 나머지 두 함수를 붙여 `store.py`를 완성한다. 세 함수가 각각 **열기 / 세기 / 넣기**를 맡는다.

## 1. 배운 내용

### 1-1. `count_jobs()` — 세는 함수

```python
def count_jobs(conn: sqlite3.Connection) -> int:
    """저장된 공고 총 개수."""
    return conn.execute("SELECT COUNT(*) FROM jobs").fetchone()[0]
```

지금 DB에 공고가 몇 건인지 답한다. 바깥을 건드리지 않고 값만 돌려주므로 몇 번을 불러도 DB는 그대로다.

한 줄이 세 단계로 이어져 있다.

```python
① conn.execute("SELECT COUNT(*) FROM jobs")   # SQL 실행 → 커서 반환
② .fetchone()                                  # 결과에서 한 줄 꺼냄 → (3,)
③ [0]                                          # 그 줄의 첫 번째 값 → 3
```

### 1-2. `[0]`이 필요한 이유

**SQL 결과는 항상 표 형태로 온다.** 한 칸짜리 답이어도 마찬가지다.

```
SELECT COUNT(*) FROM jobs
       ↓
┌──────────┐
│ COUNT(*) │   ← 열이 하나
├──────────┤
│    3     │   ← 행이 하나
└──────────┘
```

`fetchone()`이 돌려주는 `(3,)`은 **튜플**이다. 값이 하나여도 여러 값을 담을 수 있는 그릇으로 온다. 파이썬에서 원소가 하나인 튜플은 쉼표를 붙여 `(3,)`으로 쓴다. `(3)`이라고 쓰면 그냥 숫자 3이 된다.

`SELECT id, title FROM jobs`였다면 `("fake:1", "백엔드 개발자")`처럼 두 칸짜리 튜플이 오고 `[0]`은 id, `[1]`은 title이 된다.

| 메서드 | 돌려주는 것 | 언제 |
| --- | --- | --- |
| `fetchone()` | 행 하나 (없으면 `None`) | 결과가 한 줄일 것이 확실할 때 |
| `fetchall()` | 행 전부를 리스트로 | 여러 줄을 다 받을 때 |
| `fetchmany(n)` | n개씩 | 결과가 아주 클 때 나눠 받기 |

`fetchone()`은 결과가 없으면 `None`을 돌려주고 그러면 `[0]`에서 터진다. 다만 `COUNT(*)`는 테이블이 비어 있어도 `(0,)`을 돌려주므로 여기서는 안전하다. **집계 함수는 결과가 없어도 행 하나를 만들어낸다.** 다른 쿼리에서 `fetchone()[0]`을 쓸 때는 `None` 검사가 필요할 수 있다.

### 1-3. `upsert_jobs()` — 이 단계의 주인공

```python
def upsert_jobs(conn: sqlite3.Connection, jobs: list[dict], seen_at: str) -> int:
    """처음 보는 공고만 저장하고, 새로 들어간 개수를 돌려준다."""
    before = count_jobs(conn)
    conn.executemany(
        "INSERT OR IGNORE INTO jobs (id, title, company, first_seen_at)"
        " VALUES (?, ?, ?, ?)",
        [(j["id"], j["title"], j["company"], seen_at) for j in jobs],
    )
    conn.commit()
    return count_jobs(conn) - before
```

### 1-4. `INSERT OR IGNORE`

이미 있는 `id`면 조용히 건너뛴다. `PRIMARY KEY` 제약에 걸렸을 때 에러를 내는 대신 그 행만 넘어가는 것이고, **중복 판정의 가장 단순한 형태**다.

여기서도 멱등성이 나온다. 같은 데이터를 몇 번 넣어도 결과가 같고 두 번째부터 실패하지 않는다. #멱등성 → [[개념 - 멱등성]]

### 1-5. `?` 자리표시자 — 이건 습관으로 굳혀야 한다

값을 SQL 문자열에 이어붙이지 않고 따로 넘긴다.

```python
conn.execute("INSERT INTO jobs (id) VALUES (?)", (job_id,))     # 이렇게
conn.execute(f"INSERT INTO jobs (id) VALUES ('{job_id}')")      # 이러면 안 된다
```

아래처럼 f-string으로 만들면 두 가지가 깨진다.

- 공고 제목에 따옴표가 하나만 있어도 **쿼리 문장이 깨진다**
- 값에 SQL 문이 섞여 들어오면 **그대로 실행된다.** 이것을 **SQL 인젝션**이라고 한다

`?`를 쓰면 DB가 그 자리를 값으로만 취급하므로 무엇이 들어와도 문장이 되지 않는다. 채용공고 제목처럼 **내가 만들지 않은 문자열**을 다룰 때는 예외 없이 이 형태를 쓴다.

### 1-6. `executemany`와 리스트 컴프리헨션

`executemany`는 같은 SQL을 값만 바꿔 여러 번 실행한다. 반복문으로 `execute`를 여러 번 부르는 것보다 빠르고, 무엇보다 의도가 드러난다.

두 번째 인자가 **리스트 컴프리헨션**이다.

```python
[(j["id"], j["title"], j["company"], seen_at) for j in jobs]
```

딕셔너리 목록을 튜플 목록으로 바꾼다. JS의 `map`에 해당한다.

```js
jobs.map(j => [j.id, j.title, j.company, seenAt])   // JS
```

**`?` 네 개의 순서와 튜플 안의 순서가 맞아야 한다.** 어긋나면 제목 자리에 회사명이 들어가는데, 문법 에러가 아니라 조용히 잘못된 데이터가 쌓인다.

### 1-7. `conn.commit()` — git 커밋과 다른 것

DB에서 **지금까지의 변경을 확정한다**는 뜻이다. 이것을 부르지 않으면 파일에 기록되지 않는다.

이름이 같아서 헷갈리지만 완전히 다른 층의 개념이다.

| | 무엇을 확정하나 | 어디에 |
| --- | --- | --- |
| `conn.commit()` | DB 변경 | `collector.db` 파일 |
| `git commit` | 파일 변경 | 저장소 이력 |

이 프로젝트에서는 둘 다 나온다. 파이썬이 `conn.commit()`으로 DB 파일을 확정하고, 그 파일을 워크플로우가 `git commit`으로 저장소에 올린다.

### 1-8. `before`와 뺄셈 — 신규 개수를 세는 방법

```python
before = count_jobs(conn)          # 넣기 전에 세고
...                                 # 넣고
return count_jobs(conn) - before   # 다시 세서 차이를 돌려준다
```

`INSERT OR IGNORE`는 **몇 건이 실제로 들어갔는지 알려주지 않는다.** 그래서 앞뒤로 세서 차이를 구한다.

단순하지만 정확하다. **DB가 판정한 결과를 그대로 읽는 방식**이라 파이썬 쪽 계산이 틀릴 여지가 없다. 만약 "이 id가 있나?"를 파이썬으로 하나씩 검사해서 셌다면, 검사와 삽입 사이가 어긋날 수 있고 코드도 길어진다.

## 2. 추가로 알면 좋은 활용법

### 2-1. 확인 방법

```cmd
python collector/main.py
python collector/main.py
```

두 번 돌리면 `data/run-log.md`가 이렇게 나온다.

```
실행: ... UTC — 신규 3건, 누적 3건     ← 처음이라 3건 다 새것
실행: ... UTC — 신규 0건, 누적 3건     ← 이미 아는 것들이라 0건
```

**두 번째 줄의 신규 0건**이 이 단계의 목표다. 같은 데이터를 몇 번 넣어도 쌓이지 않는다는 것, 매일 API가 중복을 줘도 DB가 부풀지 않는 이유다.

### 2-2. 문법 검사는 이름이 존재하는지 보지 않는다

`python -m py_compile`은 문장 구조만 본다. 함수 이름이나 모듈 이름이 실제로 존재하는지는 **그 줄이 실행될 때** 확인되므로, 컴파일이 통과해도 실행에서 터질 수 있다. 타입 힌트 자리에 없는 이름을 써도 마찬가지다.

그래서 검사는 두 단계로 한다. 문법 확인 뒤에 **실제로 임포트하고 돌려보는 것**까지 해야 이름 문제가 드러난다.

## 3. 더 나아가 알면 좋은 것

### 3-1. 다음에 볼 키워드

- 트랜잭션 — 여러 변경을 한 덩어리로 묶어 실패 시 되돌리기
- `with` 문으로 커넥션 다루기 — 파일처럼 DB 연결도 자동으로 닫을 수 있다
- `row_factory` — 조회 결과를 튜플이 아니라 이름으로 접근하기
- `INSERT ... ON CONFLICT DO UPDATE` — 있으면 갱신, 없으면 삽입. 변경 감지 단계에서 필요해진다
- `cursor.rowcount` — 실제로 영향받은 행 수. `INSERT OR IGNORE`에서는 기대대로 동작하지 않는 경우가 있어 확인이 필요하다

## 관련 노트

[[수집기 06 - SQLite 저장 계층]] · [[수집기 08 - main.py를 오케스트레이터로 바꾸기]]
