---
출처: Claude 대화
작성일: 2026-08-12
tags: [프로젝트노트, 수집기, Python, 함수분석]
---

# 수집기 05-3 - append_run_log 함수 분석

> 상위: [[수집기 05 - main.py 코드 분석]] · 세부: [[수집기 05-3 mkdir 소스 읽기]]

```python
def append_run_log(message: str) -> None:
    """실행 기록 파일에 한 줄 덧붙인다. 폴더가 없으면 만든다."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with LOG_FILE.open("a", encoding="utf-8") as f:
        f.write(message + "\n")
```

다섯 줄짜리지만 파이썬 고유 개념이 여럿 들어 있다. 한 줄씩 뜯고, 다른 방식과 비교하고, 약점까지 정리한다.

## 1. 한 줄씩

### 1-1. `def append_run_log(message: str) -> None:`

`message: str`은 매개변수와 타입 힌트, `-> None`은 반환값이 없다는 표시다.

여기서 드러나는 개념은 **이 함수가 값을 만드는 함수가 아니라 일을 하는 함수**라는 것이다.

```python
stamp = now_utc()          # 값을 받아옴 (반환값 있음)
append_run_log(message)    # 시키기만 함 (반환값 없음)
```

`now_utc()`는 결과를 받아서 쓰지만 `append_run_log()`는 받을 것이 없다. 대신 **파일이라는 바깥 세상을 바꾼다.** 이것을 **부수 효과(side effect)** 라고 한다. 함수 이름이 `append`라는 동사인 것도 같은 이유다. 일을 시키는 함수는 동사로 짓는 것이 관례다.

### 1-2. `DATA_DIR.mkdir(parents=True, exist_ok=True)`

이 한 줄에 개념이 두 개 있다.

**모든 것이 객체다**

`DATA_DIR`은 문자열이 아니라 `Path`라는 객체이고 `mkdir`은 그 객체가 가진 메서드다. 그러므로 이 줄은 경로 객체에게 폴더를 만들라고 시키는 것이다.

```python
DATA_DIR.mkdir(...)      # 경로 객체에게 시킨다
DATA_DIR.exists()        # 있는지 물어본다
DATA_DIR.parent          # 상위 폴더를 물어본다
```

파이썬은 숫자와 문자열, 함수까지 전부 객체라서 이 감각이 언어 전체에 퍼져 있다.

**키워드 인자 — 자바에 없는 문법**

```python
DATA_DIR.mkdir(parents=True, exist_ok=True)
```

인자를 이름을 붙여서 넘기고 있다. 자바라면 `mkdir(true, true)`처럼 써야 하고 어느 것이 무엇인지 알 수 없다. 파이썬은 이름을 적으므로 순서도 상관없고 읽기만 해도 의미가 드러난다. `exist_ok=True`를 보면 이미 있어도 괜찮다는 뜻이 바로 읽힌다.

`True`가 대문자인 것도 파이썬 고유다. 자바와 JS는 `true`, 파이썬은 `True` / `False` / `None`이다.

`mkdir`이 이 두 옵션을 안에서 어떻게 쓰는지는 소스를 열어보면 드러난다. → [[수집기 05-3 mkdir 소스 읽기]]

### 1-3. `with LOG_FILE.open("a", encoding="utf-8") as f:`

이 함수에서 가장 중요한 개념인 **컨텍스트 매니저**다. 열었으면 반드시 닫는다는 것을 자동화하는 문법이다.

`with` 없이 쓰면 이렇게 된다.

```python
f = LOG_FILE.open("a", encoding="utf-8")
try:
    f.write(message + "\n")
finally:
    f.close()          # 에러가 나도 반드시 닫아야 한다
```

파일은 닫지 않으면 내용이 디스크에 기록되지 않을 수 있고, 계속 열어두면 자원이 샌다. 중간에 에러가 날 수도 있으므로 `try` / `finally`로 감싸야 한다. `with`는 이 다섯 줄을 한 줄로 줄인다.

**자바에 정확히 대응하는 문법이 있다.**

```java
try (BufferedWriter w = Files.newBufferedWriter(path)) {
    w.write(message);
}   // 자동으로 close()
```

```python
with LOG_FILE.open("a") as f:
    f.write(message)
# 자동으로 close()
```

같은 문제(자원 해제)를 같은 방식으로 푼 것이고 파이썬 쪽 문법이 더 짧을 뿐이다.

`as f`는 열린 파일에 `f`라는 이름을 붙이는 것이고 `"a"`는 이어쓰기 모드다.

### 1-4. `f.write(message + "\n")`

- `+`는 문자열 연결이고 자바와 같다
- `"\n"`은 **이스케이프 시퀀스**다. 역슬래시로 시작하는 특수문자 표기이고 줄바꿈 한 글자를 뜻한다. `\t`(탭), `\\`(역슬래시 자체)도 같은 부류다

`write`는 `print`와 달리 줄바꿈을 자동으로 붙이지 않으므로 직접 더해야 한다.

그리고 **들여쓰기가 곧 블록**이다. `with` 아래로 들여쓴 줄이 with 블록 안이라는 뜻이고 들여쓰기를 풀면 블록이 끝난다. 자바의 중괄호 자리를 공백이 대신한다.

## 2. 들어간 개념 정리

| 개념 | 어디에 | 자바·JS와 비교 |
| --- | --- | --- |
| 타입 힌트 | `message: str`, `-> None` | 자바는 강제, 파이썬은 메모 |
| 부수 효과 함수 | 반환값 없음 | `void`와 유사 |
| 객체와 메서드 | `DATA_DIR.mkdir()` | 같음 |
| 키워드 인자 | `parents=True` | **자바·JS에 없음** |
| 불리언 대문자 | `True` | `true` |
| 컨텍스트 매니저 | `with ... as f` | 자바 `try-with-resources` |
| 이스케이프 시퀀스 | `"\n"` | 같음 |
| 들여쓰기가 블록 | 전체 | 중괄호 대신 |

특히 **키워드 인자**와 **`with`** 두 가지는 앞으로 파이썬 코드에서 계속 나온다.

## 3. 다른 방식과 비교

### 3-1. `Path.write_text()` — 가장 짧지만 쓸 수 없다

```python
LOG_FILE.write_text(message)
```

한 줄로 끝나지만 **덮어쓴다.** 이어쓰기 옵션이 없어서 누적이 목적인 이 상황에는 맞지 않는다. 짧다고 맞는 것은 아니라는 예다.

### 3-2. 내장 `open()` — 차이가 거의 없다

```python
with open(LOG_FILE, "a", encoding="utf-8") as f:
```

`LOG_FILE.open(...)`과 완전히 같다. 경로 객체를 이미 갖고 있으므로 그 객체에게 시키는 쪽이 흐름상 자연스럽다는 정도의 차이다.

### 3-3. `print(file=...)` — 실수 여지가 더 적다

```python
with LOG_FILE.open("a", encoding="utf-8") as f:
    print(message, file=f)
```

`print`는 줄바꿈을 자동으로 붙이므로 `+ "\n"`이 사라지고, 줄바꿈을 빠뜨리는 실수도 원천 차단된다. `write`는 파일에 쓴다는 의도가 더 명확하지만 취향 수준의 차이다.

### 3-4. `logging` 모듈 — 지금은 과하다

```python
import logging
logging.basicConfig(filename="data/run.log", level=logging.INFO,
                    format="%(asctime)s %(message)s")
logging.info(message)
```

파이썬 표준 로깅이다. 시각을 자동으로 붙이고 INFO/ERROR 같은 수준을 구분하며 화면과 파일에 동시 출력도 된다.

다만 지금 만드는 것은 로그가 아니라 **옵시디언에서 읽을 마크다운 파일**이다. `logging`은 형식을 자기 방식대로 강제하므로 맞지 않는다. 실제 디버깅 로그가 필요해지면 그때 별도로 도입한다.

## 4. 이 코드의 약점

### 4-1. 함수가 전역 상수에 묶여 있다

```python
def append_run_log(message: str) -> None:
    DATA_DIR.mkdir(...)          # 이 함수는 DATA_DIR 외에는 쓸 수 없다
```

경로가 함수 안에 박혀 있어서 다른 경로에 쓰고 싶으면 이 함수를 쓸 수 없고, 테스트할 때도 실제 `data/` 폴더를 건드리게 된다. 경로를 매개변수로 받으면 유연해진다.

```python
def append_line(path: Path, message: str) -> None:
    """지정한 파일에 한 줄 덧붙인다."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        print(message, file=f)
```

어떤 파일에든 쓸 수 있고 테스트할 때는 임시 폴더 경로를 넘기면 된다. 대신 호출하는 쪽이 길어진다.

**안에 박아두면 부르기 쉽고, 밖에서 받으면 재사용과 테스트가 쉽다.** 코드에서 계속 만나는 저울질이다.

### 4-2. 에러 처리가 없다

디스크가 꽉 차거나 권한이 없으면 예외가 터지고 프로그램 전체가 죽는다.

지금은 오히려 그 편이 맞다. 조용히 실패해서 아무도 모르는 것보다 죽어서 실패 메일이 오는 편이 낫다. 다만 나중에 공고 100건은 잘 저장했는데 로그를 쓰다 실패해서 전부 날아가는 상황이 생길 수 있다. 그때는 **중요한 일과 부수적인 일의 실패를 다르게 다뤄야** 한다.

## 5. 지금은 고치지 않는 이유

4-1(전역 의존)만 고칠 가치가 있지만 지금은 두는 편이 맞다고 판단했다.

> 되돌릴 수 있는 것은 겪은 뒤에 정한다.

이 함수는 지금 한 군데에서만 호출된다. 두 번째 호출자가 생기는 순간 경로를 밖에서 받아야 한다는 것이 자연스럽게 드러나고, 그 시점에는 어떤 형태가 필요한지도 이미 알고 있다.

지금 미리 유연하게 만들면 쓰지도 않을 유연성 때문에 코드가 길어지고, 정작 필요한 형태는 다를 수도 있다. 이것을 **성급한 일반화**라고 한다.

## 관련 노트

[[수집기 05 - main.py 코드 분석]] · [[수집기 05-3 mkdir 소스 읽기]]
