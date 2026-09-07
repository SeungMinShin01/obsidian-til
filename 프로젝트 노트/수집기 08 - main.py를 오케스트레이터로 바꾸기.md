---
출처: Claude 대화
작성일: 2026-08-12
tags: [프로젝트, python]
---

# 수집기 08 - main.py를 오케스트레이터로 바꾸기

> 허브: [[수집기 프로젝트 MOC]]

`store.py`가 완성되면서 `main.py`가 바뀌었다. 무엇이 바뀌었고 왜 그렇게 바꿨는지 기록한다.

## 1. 배운 내용

### 1-1. 왜 바꿨나

`main.py`는 지금까지 스스로 일을 했다. 시각을 만들고 파일에 썼다.

저장 계층이 생기면서 역할이 달라진다. **실제 작업은 `store.py`가 하고 `main.py`는 순서만 지휘한다.** 이런 역할을 **오케스트레이터**라고 한다.

이 변화가 중요한 이유는 앞으로 이 파일이 자라는 방식을 정하기 때문이다.

```python
def main() -> None:
    raw = saramin.fetch(keywords=[...])   # 수집
    jobs = normalize.to_jobs(raw)         # 정규화
    result = store.upsert(jobs)           # DB 대조·저장
    writer.render(result.new)             # 마크다운 생성
```

파일은 짧게 유지되지만 **이 함수만 읽으면 시스템이 무슨 순서로 일하는지 파악된다.** 오늘의 변경은 그 형태로 가는 첫걸음이다.

### 1-2. 바뀐 곳은 두 군데뿐

`now_utc`와 `append_run_log`는 손대지 않았다. 시각을 만들고 파일에 한 줄 쓰는 일은 저장 계층이 생겨도 그대로이기 때문이다.

**바뀔 것과 바뀌지 않을 것을 미리 갈라두면 이렇게 된다.** 처음 함수를 셋으로 나눌 때의 판단이 여기서 회수됐다.

### 1-3. 맨 위 — import와 상수

```python
from datetime import datetime, timezone
from pathlib import Path

import store

DATA_DIR = Path("data")
LOG_FILE = DATA_DIR / "run-log.md"

FAKE_JOBS = [
    {"id": "fake:1", "title": "백엔드 개발자", "company": "가나테크"},
    {"id": "fake:2", "title": "풀스택 개발자", "company": "다라소프트"},
    {"id": "fake:3", "title": "AI 엔지니어", "company": "마바랩스"},
]
```

**`import store`** — 방금 만든 `store.py`를 가져온다. 표준 라이브러리 다음에 한 줄 띄우고 쓰는 것이 관례다. **남이 만든 것 다음에 내가 만든 것** 순서다.

`from A import B`가 아니라 `import store` 형태를 쓴 것은 부를 때 `store.connect()`처럼 **어느 파일의 함수인지 이름에 드러나게** 하기 위해서다. 파일이 여러 개가 되면 이 차이가 커진다.

**`FAKE_JOBS`** — 진짜 API 대신 쓸 가짜 공고 3건이다. `{"id": ..., "title": ...}` 형태가 **딕셔너리**이고(JS의 객체에 해당) 그것이 3개 들어 있는 **리스트**다.

### 1-4. 가짜 데이터로 먼저 만드는 이유

사람인 API 키를 기다리는 동안 멈춰 있을 이유가 없다. 그리고 이 방식에는 그 이상의 이점이 있다.

- **수집 로직이 특정 API에 종속되지 않는다.** 나중에 `FAKE_JOBS` 자리에 `saramin.fetch()`를 끼우면 나머지는 그대로 돌아간다
- **파이프라인의 나머지 부분을 먼저 완성할 수 있다.** 저장·판정·마크다운 생성까지 다 만들어두고 어댑터만 갈아끼우는 순서가 된다
- **테스트가 쉽다.** 결과가 정해져 있으므로 "신규 3건 → 신규 0건"이 나오는지로 판정 로직을 확인할 수 있다. 진짜 API는 매일 응답이 달라서 이런 확인이 어렵다

### 1-5. `main()` 본문

```python
def main() -> None:
    stamp = now_utc()

    conn = store.connect()
    new_count = store.upsert_jobs(conn, FAKE_JOBS, stamp)
    total = store.count_jobs(conn)
    conn.close()

    message = f"실행: {stamp} UTC — 신규 {new_count}건, 누적 {total}건"
    append_run_log(message)
    print(message)
```

흐름은 네 단계다.

```python
conn = store.connect()                                  # ① 문 열기
new_count = store.upsert_jobs(conn, FAKE_JOBS, stamp)   # ② 넣고 몇 개 들어갔는지 받기
total = store.count_jobs(conn)                          # ③ 총 몇 개인지 묻기
conn.close()                                            # ④ 문 닫기
```

`main()`은 DB를 직접 만지지 않는다. SQL도 스키마도 여기에 없다. **`store`에게 시키고 결과만 받는다.**

**`conn.close()`** — 파일과 마찬가지로 DB도 다 쓰면 닫는다. 지금은 직접 부르고 있는데, 파일에서 `with`를 쓴 것처럼 커넥션도 `with`로 다룰 수 있다. 나중에 다듬을 부분이다.

**`message`를 변수에 담은 이유** — 같은 문자열을 파일에도 쓰고 화면에도 찍기 때문이다. 두 번 만들면 어긋날 수 있다. `stamp`를 한 번만 만든 것과 같은 이유다.

### 1-6. 로그가 알려주는 것이 달라졌다

```
전:  실행: 2026-08-12 08:58:53 UTC (python)
후:  실행: 2026-08-12 09:15:02 UTC — 신규 3건, 누적 3건
```

전에는 **돌았다는 사실**만 남았다. 이제는 **무엇이 일어났는지**가 남는다.

무인 운영에서 이 차이가 크다. 90일 뒤에 로그를 보면 매일 몇 건이 새로 들어왔는지가 그대로 보이고, 어느 날부터 신규가 0이 되었는지도 드러난다. **조용한 실패를 발견하는 단서**가 여기서 나온다.

## 2. 추가로 알면 좋은 활용법

### 2-1. 워크플로우도 한 줄 바뀐다

```yaml
git add data/ state/
```

DB가 `state/collector.db`에 생기므로 커밋 대상에 추가한다. 이것을 빼면 VM에서 DB가 만들어졌다가 폐기와 함께 사라지고, 매일 신규 3건만 반복된다.

### 2-2. 확인 방법

두 번 돌려서 두 번째가 신규 0건이면 성공이다. 로컬에서 먼저 확인하고 푸시한다.

## 3. 더 나아가 알면 좋은 것

### 3-1. 다음에 볼 키워드

- `sources/saramin.py` — `FAKE_JOBS` 자리를 대신할 첫 어댑터
- `normalize.py` — API 응답을 우리 스키마로 바꾸는 계층
- GitHub Secrets — API 키를 코드에 남기지 않고 워크플로우에 전달하기
- 예외 처리 — 한 소스가 실패해도 나머지가 돌아가게 하기

## 관련 노트

[[수집기 07 - store.py 세기와 넣기]] · [[수집기 09 - 브랜치 없이 main에서 작업하는 이유]]
