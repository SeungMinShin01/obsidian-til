---
출처: Claude 대화
작성일: 2026-08-12
tags: [프로젝트, python]
---

# 수집기 05-3-1 - mkdir 소스 읽기

> 상위: [[수집기 05-3 - append_run_log 함수 분석]]

`DATA_DIR.mkdir(parents=True, exist_ok=True)` 한 줄이 안에서 무엇을 하는지 표준 라이브러리 소스를 열어본 기록이다.

```python
def mkdir(self, mode=0o777, parents=False, exist_ok=False):
    """
    Create a new directory at this given path.
    """
    try:
        os.mkdir(self, mode)
    except FileNotFoundError:
        if not parents or self.parent == self:
            raise
        self.parent.mkdir(parents=True, exist_ok=True)
        self.mkdir(mode, parents=False, exist_ok=exist_ok)
    except OSError:
        # Cannot rely on checking for EEXIST, since the operating system
        # could give priority to other errors like EACCES or EROFS
        if not exist_ok or not self.is_dir():
            raise
```

## 1. 전체 전략

```python
try:
    os.mkdir(self, mode)      # ① 그냥 만들어본다
except FileNotFoundError:     # ② 부모가 없어서 실패
    ...
except OSError:               # ③ 그 외 실패 (이미 있음 등)
    ...
```

만들 수 있는지 먼저 확인하는 것이 아니라 **일단 만들어보고 실패하면 처리한다.** 이 방식을 **EAFP**(Easier to Ask Forgiveness than Permission)라고 한다.

## 2. 세 갈래 흐름

### 2-1. ① 성공하면 끝

`os.mkdir`이 통과하면 함수가 그대로 종료된다.

### 2-2. ② 부모가 없을 때

```python
except FileNotFoundError:
    if not parents or self.parent == self:
        raise
    self.parent.mkdir(parents=True, exist_ok=True)
    self.mkdir(mode, parents=False, exist_ok=exist_ok)
```

`data/채용/2026-08`을 만들려는데 `data/채용`이 없으면 여기로 온다.

**두 경우에는 포기하고 에러를 그대로 던진다.**

- `not parents` — 사용자가 `parents=False`로 두었다. 중간 폴더까지 만들어달라고 하지 않았으므로 만들면 안 된다
- `self.parent == self` — 더 올라갈 곳이 없다. 루트에 도달한 경우이고, 이 조건이 없으면 무한히 위로 올라가려다 죽는다. **재귀의 종료 조건**이다

`raise`를 단독으로 쓰면 지금 잡은 예외를 그대로 다시 던진다는 뜻이다. 새 에러를 만드는 것이 아니라 원본을 통과시킨다.

**`self.parent.mkdir(parents=True, exist_ok=True)`** 가 핵심이다. 자기 자신을 부모에 대해 다시 부르는 **재귀**다.

**`self.mkdir(mode, parents=False, exist_ok=exist_ok)`** 는 부모를 만든 뒤 자기를 다시 시도하는 것이다. 이번에는 `parents=False`인데, 부모를 이미 만들었으므로 또 실패하면 진짜 문제라서 재시도를 막는 것이다.

**재귀를 따라가면** `Path("a/b/c").mkdir(parents=True)`는 이렇게 동작한다.

```
mkdir(a/b/c)  → 실패(a/b 없음)
  └ mkdir(a/b)  → 실패(a 없음)
      └ mkdir(a)  → 성공
    ← 돌아와서 a/b 생성
← 돌아와서 a/b/c 생성
```

끝까지 올라갔다가 내려오면서 만드는 구조다.

### 2-3. ③ 그 외 실패 — 대개 이미 있는 경우

```python
except OSError:
    if not exist_ok or not self.is_dir():
        raise
```

폴더가 이미 있으면 `FileExistsError`가 나는데 이것은 `OSError`의 하위 종류라 여기서 잡힌다.

두 조건 중 하나라도 걸리면 에러를 던진다.

- `not exist_ok` — 이미 있어도 괜찮다고 하지 않았으면 에러가 맞다
- `not self.is_dir()` — **같은 이름의 파일이 있는 경우다.** `data`라는 이름의 파일이 있으면 폴더를 만들 수 없다. 이것은 `exist_ok=True`여도 넘어가면 안 된다

둘 다 통과하면 아무것도 하지 않고 함수가 끝난다. 조용히 성공한 것처럼 넘어가는 것이 `exist_ok=True`의 동작이다.

## 3. 우리 호출을 대입하면

```python
DATA_DIR.mkdir(parents=True, exist_ok=True)
```

| 상황 | 흐름 |
| --- | --- |
| `data` 없음 | ① `os.mkdir` 성공 → 끝 |
| `data` 이미 있음 | ① 실패 → ③ `exist_ok=True`, 디렉터리가 맞음 → 조용히 통과 |
| `data`라는 이름의 파일이 있음 | ① 실패 → ③ `is_dir()`이 거짓 → 에러 (맞는 동작) |

두 번째 줄이 매일 벌어지는 일이다. **첫날만 ①로 가고 나머지는 ③에서 조용히 통과한다.**

## 4. EAFP와 LBYL

### 4-1. 두 방식

```python
# LBYL — 확인하고 실행
if not path.exists():
    os.mkdir(path)

# EAFP — 실행하고, 실패는 예외로 받음
try:
    os.mkdir(path)
except FileExistsError:
    pass
```

EAFP는 만들고 나서 확인하는 것이 아니라 **시도하고 실패가 예외로 날아오면 그것을 잡는** 방식이다.

### 4-2. 예외가 잦은 것은 문제가 아니다

**예외가 발생하는 것과 프로그램이 죽는 것은 다르다.** `try`/`except`로 감싸는 순간 그 예외는 예상된 흐름이 된다. 폴더가 이미 있어서 `FileExistsError`가 나는 것은 사고가 아니라 이미 있다는 정보다.

파이썬은 예외를 에러보다 넓은 의미로 쓴다. `for` 반복문이 끝나는 것도 내부적으로는 예외(`StopIteration`)로 처리된다. 비정상 상황이 아니라 신호 전달 수단이다.

### 4-3. LBYL이 더 위험할 수 있다

```python
if not path.exists():      # ← 여기서 없음을 확인
                           # ← 이 틈에 다른 프로그램이 만들어버리면?
    os.mkdir(path)         # ← 여기서 FileExistsError로 죽는다
```

확인과 실행 사이의 틈이 문제다. 그 사이에 상황이 바뀌면 확인이 무의미해진다. 이것을 **경쟁 상태(race condition)** 라고 한다.

그리고 LBYL도 결국 예외 처리가 필요하다. 확인을 통과해도 실패할 수 있기 때문이다.

```python
if not path.exists():
    try:                       # 확인했는데도 결국 try가 필요하다
        os.mkdir(path)
    except FileExistsError:
        pass
```

그럴 것이면 처음부터 예외 처리만 하는 편이 짧다. 확인 코드가 순수한 낭비가 된다.

### 4-4. 비교

| | LBYL | EAFP |
| --- | --- | --- |
| 방식 | 확인 후 실행 | 실행 후 예외 처리 |
| 예외 발생 | 적음 | 잦음 (하지만 처리된다) |
| 틈(경쟁 상태) | 있음 | 없음 |
| 코드 길이 | 확인 + 예외처리 | 예외처리만 |
| 성능 | 매번 확인 비용 | 성공 시 비용 없음 |

성능도 EAFP가 유리한 경우가 많다. 대부분 성공한다면 확인 비용이 매번 낭비되기 때문이다. 반대로 실패가 압도적으로 잦다면 미리 거르는 편이 나을 수 있다.

### 4-5. LBYL이 맞는 경우

```python
if user.confirmed_deletion:
    delete_everything()
```

**부작용이 크거나 되돌릴 수 없는 일**은 먼저 확인하는 것이 맞다. 일단 지워보고 아니면 되돌리는 것은 불가능하기 때문이다.

기준은 이렇다. **실패해도 안전하면 EAFP, 실패가 곧 피해면 LBYL.** 폴더를 만드는 일은 실패해도 아무 일이 일어나지 않으므로 EAFP가 맞다.

## 5. 이 짧은 함수에 들어간 개념

| 개념 | 어디에 |
| --- | --- |
| EAFP | 확인 없이 시도하고 예외로 처리 |
| 예외 계층 | `FileNotFoundError`는 `OSError`의 하위. 그래서 먼저 써야 잡힌다 |
| bare raise | `raise` 단독 — 잡은 예외를 그대로 재전파 |
| 재귀 | 부모에 대해 자기 자신을 호출 |
| 재귀 종료 조건 | `self.parent == self` — 없으면 무한 반복 |
| 기본값 매개변수 | `mode=0o777, parents=False, exist_ok=False` |

**예외 순서가 특히 중요하다.** `except OSError`를 위에 썼다면 `FileNotFoundError`도 거기서 잡혀버려 부모 생성 로직이 아예 돌지 않는다. **좁은 예외를 먼저, 넓은 예외를 나중에** 두어야 하고, 이는 자바의 catch 블록 순서 규칙과 같다.
