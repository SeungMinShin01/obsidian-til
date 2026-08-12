---
출처: Claude 대화
작성일: 2026-08-12
tags: [프로젝트노트, 수집기, SQLite, Python, 저장]
---

# 수집기 06 - SQLite 저장 계층

> 허브: [[수집기 프로젝트 MOC]] · 세부: [[수집기 06-1 - SQLite에 서버가 없다는 뜻]]

파일에 줄을 쌓던 것을 DB에 행을 쌓는 것으로 바꾸는 단계다. `collector/store.py`를 함수 하나씩 만들어가며 기록한다.

## 1. 배운 내용

### 1-1. 이번 단계의 진짜 목표

저장 자체가 아니라 **중복이 쌓이지 않는 것을 눈으로 확인하는 것**이다. 가짜 공고 3건을 넣고 두 번 실행하면 두 번째는 신규 0건이 나와야 한다. 이것이 앞으로 매일 API가 중복을 줘도 DB가 부풀지 않는 원리다.

### 1-2. `connect()` — 문을 열어주는 함수

```python
"""SQLite 저장 계층. DB 연결과 공고 저장을 담당한다."""

import sqlite3
from pathlib import Path

DB_PATH = Path("state") / "collector.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS jobs (
    id            TEXT PRIMARY KEY,
    title         TEXT NOT NULL,
    company       TEXT,
    first_seen_at TEXT NOT NULL
);
"""


def connect() -> sqlite3.Connection:
    """DB에 연결한다. 파일과 테이블이 없으면 만든다."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.executescript(SCHEMA)
    return conn
```

이 함수는 저장도 조회도 하지 않는다. **DB를 쓸 수 있는 상태로 만들어 넘겨주는 것**이 전부다. 세 줄이 각각 하나씩 맡는다.

**`DB_PATH.parent.mkdir(parents=True, exist_ok=True)`**
`DB_PATH`가 `state/collector.db`이므로 `.parent`는 `state` 폴더다. 폴더가 없으면 SQLite가 파일을 만들지 못하므로 먼저 만들어둔다. `main.py`에서 `data` 폴더를 만들 때와 같은 코드다.

**`conn = sqlite3.connect(DB_PATH)`**
파일이 없으면 자동으로 만든다. 서버에 접속하는 것이 아니라 파일 하나를 여는 것이다. → [[수집기 06-1 - SQLite에 서버가 없다는 뜻]]

**`conn.executescript(SCHEMA)`**
테이블을 만든다. `executescript`는 여러 SQL 문을 한 번에 실행할 수 있어서, 나중에 테이블이 늘어날 때를 대비한 선택이다.

### 1-3. `IF NOT EXISTS`가 핵심이다

```sql
CREATE TABLE IF NOT EXISTS jobs
```

이것이 없으면 두 번째 실행부터 실패한다. 이미 그 테이블이 있다는 에러가 나기 때문이다. 그런데 이 함수는 매일 호출되므로 "이미 있으면 조용히 넘어가라"가 필수다.

`mkdir(exist_ok=True)`와 완전히 같은 발상이고 이것이 **멱등성**이다. 무인 시스템에서는 이 패턴이 계속 반복된다. **이미 되어 있으면 아무것도 하지 않는다.**

### 1-4. 스키마 읽는 법

```sql
id            TEXT PRIMARY KEY,   -- 공고 고유 ID. 중복 판정의 열쇠
title         TEXT NOT NULL,      -- 제목. 비어 있으면 안 됨
company       TEXT,               -- 회사명. 비어도 됨
first_seen_at TEXT NOT NULL       -- 처음 본 시각
```

**`PRIMARY KEY`가 핵심이다.** 같은 `id`를 두 번 넣으려 하면 SQLite가 거부한다. 파이썬으로 "이거 이미 있나?"를 검사할 필요가 없고 **DB가 대신 막아준다.**

검사와 삽입 사이에 다른 것이 끼어들 틈이 없다는 점에서, 규칙을 데이터베이스 자체에 박아두는 편이 코드로 검사하는 것보다 안전하다. SQL day02에서 다룬 제약조건이 실전에서 쓰이는 방식이다.

`first_seen_at`을 `TEXT`로 둔 것은 SQLite에 날짜 타입이 따로 없기 때문이다. `2026-08-12 08:58:53` 형태로 넣으면 **글자순 정렬이 곧 시간순 정렬**이 되어 문제없이 쓸 수 있다.

### 1-5. 파일은 함수 단위가 아니라 역할 단위로 나눈다

`connect`, `count_jobs`, `upsert_jobs`는 전부 `store.py` 한 파일에 들어간다. 파일 하나에 함수가 여럿, 많으면 열 개가 넘어도 된다.

나누는 기준은 **같은 이유로 바뀌는가**이다.

- DB 스키마가 바뀌면 → `store.py`만 고친다
- 사람인 API 응답 형식이 바뀌면 → `sources/saramin.py`만 고친다
- 마크다운 모양을 바꾸려면 → `writer.py`만 고친다

이렇게 갈라두면 한 가지가 바뀔 때 한 파일만 열면 된다. 함수마다 파일을 만들면 파일이 수십 개가 되고 import가 복잡해진다. 반대로 전부 한 파일에 넣으면 수백 줄이 되어 찾기 어려워진다. 기준은 **이 파일을 왜 열게 되는가**이다.

## 2. 추가로 알면 좋은 활용법

### 2-1. 예정된 파일 구조

```
collector/
├── main.py          ← 순서 지휘 (오케스트레이터)
├── store.py         ← DB 관련 전부: 연결, 저장, 조회, 판정
├── normalize.py     ← API 응답 → 우리 형식으로 변환
├── writer.py        ← DB → 마크다운 생성
└── sources/
    ├── saramin.py   ← 사람인 API 호출
    └── arxiv.py     ← 나중에 논문
```

`main.py`에서 `import store`라고 쓸 수 있는 것은 두 파일이 같은 폴더에 있기 때문이다. 폴더가 깊어지면 `from collector import store` 형태로 바뀐다.

### 2-2. 워크플로우 쪽 변경

DB 파일이 `state/`에 생기므로 커밋 대상에 추가해야 한다.

```yaml
git add data/ state/
```

## 3. 더 나아가 알면 좋은 것

### 3-1. 다음에 볼 키워드

- `?` 자리표시자와 SQL 인젝션 — 값을 문자열로 이어붙이면 안 되는 이유
- `INSERT OR IGNORE` — 중복 판정의 가장 단순한 형태
- `conn.commit()` — DB의 커밋. git 커밋과 완전히 다른 개념
- 바이너리 파일을 git으로 관리할 때의 히스토리 크기
- 트랜잭션 — 여러 변경을 한 덩어리로 묶어 실패 시 되돌리기

## 관련 노트

[[수집기 프로젝트 MOC]] · [[수집기 05 - main.py 코드 분석]] · [[수집기 06-1 - SQLite에 서버가 없다는 뜻]]
