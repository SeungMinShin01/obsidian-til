---
출처: Claude 대화
작성일: 2026-08-12
tags: [프로젝트노트, 수집기, Python, 코드분석]
---

# 수집기 05 - main.py 코드 분석

> 허브: [[수집기 프로젝트 MOC]]
> 세부: [[수집기 05-1 - 파이썬 문법 세부]] · [[수집기 05-2 - now_utc 함수 분석]] · [[수집기 05-3 - append_run_log 함수 분석]] · [[수집기 05-4 - main 함수와 진입점 가드]]

워크플로우의 셸 명령을 파이썬으로 옮긴 첫 파일을 한 덩어리씩 뜯어본 기록이다.

## 1. 배운 내용

### 1-0. 이 파일이 한 일은 기능 추가가 아니라 이동이다

셸로 하던 일을 파이썬으로 옮겼을 뿐 결과물은 같다.

| 전 (셸) | 후 (파이썬) |
| --- | --- |
| `mkdir -p data` | `DATA_DIR.mkdir(parents=True, exist_ok=True)` |
| `echo "..." >> data/run-log.md` | `LOG_FILE.open("a")` + `f.write(...)` |
| `date -u '+%Y-%m-%d %H:%M:%S'` | `datetime.now(timezone.utc).strftime(...)` |

셸로도 여기까지는 되지만 API 호출, 응답 정규화, DB 대조, 마크다운 생성까지 가면 셸로는 감당이 안 된다. 그래서 이 단계의 목적은 **통로 확보**다. VM에서 파이썬이 돌고 그 결과가 커밋되는 경로만 뚫어두면, 이후로는 파이썬 파일 안에서만 작업하면 되고 워크플로우 파일은 건드리지 않아도 된다.

결과를 고정한 채 구현만 바꾸는 것을 **리팩터링**이라고 한다. 결과가 이전과 같아야 한다는 것을 알고 있으므로, 다르면 원인이 파이썬 쪽 하나로 좁혀진다.

### 1-1. 전체 코드

```python
"""수집기 진입점.

지금은 실행 기록만 남긴다. 앞으로 이 자리에 수집 → 정규화 → 저장이 들어간다.
"""

from datetime import datetime, timezone
from pathlib import Path

DATA_DIR = Path("data")
LOG_FILE = DATA_DIR / "run-log.md"


def now_utc() -> str:
    """현재 시각을 UTC 문자열로 돌려준다."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")


def append_run_log(message: str) -> None:
    """실행 기록 파일에 한 줄 덧붙인다. 폴더가 없으면 만든다."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with LOG_FILE.open("a", encoding="utf-8") as f:
        f.write(message + "\n")


def main() -> None:
    stamp = now_utc()
    append_run_log(f"실행: {stamp} UTC (python)")
    print(f"기록 완료: {stamp} UTC")


if __name__ == "__main__":
    main()
```

### 1-2. 파일 설명(독스트링)

파일 맨 위의 삼중따옴표 문자열은 이 파일이 무엇을 하는지 적는 자리다. `#` 주석과 비슷하지만 파이썬이 인식해서 `help()` 같은 도구로 꺼내볼 수 있다. 파일과 함수 맨 위에 두는 것이 관례다.

### 1-3. 가져오기

```python
from datetime import datetime, timezone
from pathlib import Path
```

`from A import B`는 A라는 도구상자에서 B만 꺼내 쓰겠다는 뜻이다. 셋 다 파이썬 기본 내장이라 따로 설치할 필요가 없고, 그래서 아직 `requirements.txt`가 없다.

### 1-4. 상수와 경로

```python
DATA_DIR = Path("data")
LOG_FILE = DATA_DIR / "run-log.md"
```

대문자 이름은 바꾸지 않을 값이라는 관례다. 파이썬에는 재할당을 막는 언어 차원의 키워드(자바의 `final`, JS의 `const`)가 없어서 이름으로 약속한다. 값을 실제로 못 바꾸게 하는 수단은 따로 있다. → [[수집기 05-1 - 파이썬 문법 세부]]

두 번째 줄의 `/`는 나눗셈이 아니라 **경로 합치기**다. `Path`가 `/` 기호를 그렇게 동작하도록 만들어져 있다. 리눅스에서는 `data/run-log.md`, 윈도우에서는 `data\run-log.md`가 된다. 로컬(윈도우)과 VM(리눅스) 양쪽에서 돌리므로 이 차이를 대신 처리해주는 것이 중요하다.

맨 위에 모아두면 경로를 바꿀 때 이 두 줄만 고치면 된다.

### 1-5. 시각 함수

```python
def now_utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
```

- `-> str`은 **타입 힌트**다. 이 함수가 문자열을 돌려준다는 표시일 뿐 실행에는 영향이 없다. 사람이 읽기 좋고 편집기가 오류를 잡아주게 하는 용도다
- `datetime.now(timezone.utc)` — 시각을 UTC 기준으로 가져온다. 이것을 지정하지 않으면 로컬에서는 한국시간, VM에서는 UTC가 나와 환경마다 결과가 달라진다
- `.strftime("%Y-%m-%d %H:%M:%S")` — 시각 객체를 문자열로 바꾼다. `%Y`는 연도 4자리, `%m` 월, `%d` 일, `%H` 시, `%M` 분, `%S` 초

`datetime.now(...)`가 돌려준 결과에 바로 `.strftime(...)`을 이어 붙이는 것을 **체이닝**이라고 한다.

### 1-6. 파일에 쓰는 함수

```python
def append_run_log(message: str) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with LOG_FILE.open("a", encoding="utf-8") as f:
        f.write(message + "\n")
```

**`mkdir`의 두 옵션이 핵심이다.**

- `parents=True` — 중간 폴더까지 만든다. 나중에 `data/채용/2026-08/`처럼 깊어질 때 필요하다
- `exist_ok=True` — 폴더가 이미 있어도 에러를 내지 않는다. 이것이 없으면 두 번째 실행부터 실패한다

이것이 **멱등성**이다. 몇 번을 실행해도 같은 결과가 나오고 터지지 않는 것, 무인 시스템의 기본 조건이다. #멱등성 → [[개념 - 멱등성]]

**`with ... as f:`** — 파일을 열고 블록이 끝나면 자동으로 닫는다. 파일은 닫아야 내용이 확실히 기록되는데, 직접 닫으려면 중간에 에러가 났을 때까지 대비해야 해서 번거롭다. 파이썬에서 파일을 열 때는 거의 항상 이 형태를 쓴다.

**`encoding="utf-8"`** — 명시하지 않으면 윈도우에서 한글이 깨진다. 윈도우 파이썬은 기본 인코딩이 UTF-8이 아니라서 리눅스에서 만든 파일과 결과가 달라진다. 파일을 열 때 인코딩을 적는 것은 습관으로 두는 편이 안전하다.

**`f.write(message + "\n")`** — `write`는 `print`와 달리 줄바꿈을 자동으로 붙이지 않는다. 붙이지 않으면 모든 기록이 한 줄로 이어진다.

### 1-7. 본체

```python
def main() -> None:
    stamp = now_utc()
    append_run_log(f"실행: {stamp} UTC (python)")
    print(f"기록 완료: {stamp} UTC")
```

`f"..."`는 **f-string**이고 중괄호 안의 변수를 문자열에 끼워 넣는다.

`stamp` 변수에 한 번 담아둔 이유가 있다. `now_utc()`를 두 번 부르면 그 사이에 초가 넘어가서 파일에 적힌 시각과 화면에 찍힌 시각이 달라질 수 있다. 한 번 찍어서 재사용한다.

`print`는 Actions 로그에 보이게 하려고 넣었다. 파일에만 쓰면 실행 중에 무엇이 일어났는지 알 수 없다.

### 1-8. 마지막 두 줄

```python
if __name__ == "__main__":
    main()
```

`__name__`은 파이썬이 자동으로 채워주는 변수다.

- 파일을 직접 실행하면 `"__main__"`이 들어간다
- 다른 파일이 이 파일을 가져다 쓰면(import) 파일 이름이 들어간다

그래서 이 줄은 직접 실행할 때만 `main()`을 돌리라는 뜻이다. 나중에 다른 파일에서 `now_utc()` 함수만 빌려 쓸 때 원치 않게 로그가 써지는 것을 막는다.

### 1-9. 실행 순서

`def`는 함수를 만들어두기만 하고 실행하지 않는다.

```
1. import 실행 (도구를 가져온다)
2. DATA_DIR, LOG_FILE 값을 만든다
3. now_utc 함수를 등록만 한다        ← 실행되지 않음
4. append_run_log 함수를 등록만 한다  ← 실행되지 않음
5. main 함수를 등록만 한다           ← 실행되지 않음
6. if __name__ ... 이 참이므로 main() 호출  ← 여기서 비로소 실행
7. main 안에서 now_utc() → append_run_log() → print() 순으로 실행
```

파일을 위에서 아래로 읽으면서 함수는 이름표만 붙여두고, 마지막 줄에 가서야 실제로 부른다.

## 2. 추가로 알면 좋은 활용법

### 2-1. 함수를 셋으로 나눈 이유

지금 규모에서는 과해 보이지만, `append_run_log`가 나중에 `save_to_db`로 바뀌어도 `main`의 구조는 그대로 남는다. 바뀔 것과 바뀌지 않을 것을 미리 갈라두는 것이다.

### 2-2. 로컬에서 먼저 돌린다

```cmd
python collector/main.py
```

로컬 테스트는 몇 초지만 Actions 왕복은 1~2분이다. 로컬에서 성공해야 VM에서도 되므로, 먼저 걸러내면 디버깅 사이클이 훨씬 짧아진다.

### 2-3. 워크플로우 쪽 변경

```yaml
      - name: 파이썬 설치
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"

      - name: 수집기 실행
        run: python collector/main.py
```

`with:`는 액션에 옵션을 넘기는 자리다. `uses`가 어떤 도구를 쓸지라면 `with`는 어떻게 설정할지에 해당한다. 파이썬 버전을 3.11로 고정한 것은 로컬 버전과 맞추기 위해서이고, 러너 이미지가 바뀌어도 파이썬 버전은 유지된다.

## 3. 더 나아가 알면 좋은 것

### 3-1. 다음에 볼 키워드

- `requirements.txt`와 `pip install` — 외부 패키지를 쓰기 시작하면 필요해진다
- `sqlite3` 표준 라이브러리 — 다음 단계에서 저장 계층에 쓸 도구
- 예외 처리(`try` / `except`) — API 호출이 실패했을 때 파이프라인을 죽이지 않는 방법
- 로깅(`logging`) — `print` 대신 수준별로 기록을 남기는 표준 방식

## 관련 노트

[[수집기 프로젝트 MOC]] · [[수집기 04 - 저장소에 결과 남기기]] · [[수집기 05-1 - 파이썬 문법 세부]] · [[수집기 05-2 - now_utc 함수 분석]] · [[수집기 05-3 - append_run_log 함수 분석]] · [[수집기 05-4 - main 함수와 진입점 가드]]
