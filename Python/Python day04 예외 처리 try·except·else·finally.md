---
출처: Claude 분석
원본: KDT_2026/2026_Python/day04/c6-1.py, day04/c6-2.py, practice/p397-381.py
작성일: 2026-10-22
tags: [학습, python]
---

# Python day04 — 예외 처리 try·except·else·finally

> 실습 파일: `day04/c6-1.py`, `day04/c6-2.py`, `practice/p397-381.py`
> 허브: [[Python 정리본 인덱스]] · 이전: [[Python day03 함수·재귀·람다 연습문제 풀이]] · 다음: [[Python day05 클래스 정의와 생성자·메소드]]

day04는 **오류**를 다루는 날이다. 지금까지는 `int("안녕")`을 치면 빨간 글자가 쏟아지고 프로그램이 그 자리에서 죽는 걸 그냥 보고 넘어갔는데, 이번에는 그 빨간 글자가 무엇이고(구문 오류와 런타임 오류), 죽지 않게 하려면 어떻게 하는지(조건문으로 미리 피하기, `try`로 받아내기)를 배웠다. `try` 한 덩어리에 `except`·`else`·`finally`가 어떻게 붙고 각 블록이 언제 실행되는지를 네 번 고쳐 쓰며 확인했고, 마지막에는 파일을 열어 둔 채 예외가 터지면 어떻게 되는지 `file.closed`로 눈으로 봤다. 자바에서 `try`·`catch`·`finally`를 썼던 것과 모양이 거의 같은데, 파이썬에는 `else` 블록이 하나 더 있고 예외를 꼭 잡으라고 강제하지 않는다는 점이 다르다.

## 1. 배운 내용

### 1-1. 오류의 두 종류 — 구문 오류와 런타임 오류

```python
# 구문 오류 : 실행 전 오류 , 실행 자체 불가능
# 런타임 오류 : 실행 중 오류 , 예외
# 예외 처리 : 예외를 해결하는 모든 것
```

| 구분 | 언제 | 예 | 처리 |
| --- | --- | --- | --- |
| 구문 오류 (`SyntaxError`) | 실행 **전**. 파이썬이 코드를 읽는 단계에서 걸려 한 줄도 실행되지 않는다 | 괄호 짝이 안 맞음(`cursor.close)`), 콜론 빠짐, 들여쓰기 어긋남 | 코드를 고치는 것 외에 방법이 없다 — `try`로 잡을 수 없다 |
| 런타임 오류 = **예외** | 실행 **중**. 그 줄에 도달했을 때 값이나 상황이 맞지 않아 터진다 | `int("안녕")` → `ValueError`, `10 + "개"` → `TypeError`, `[1, 2, 3][10]` → `IndexError`, 없는 키 → `KeyError` | 조건문으로 미리 피하거나 `try`로 받아낸다 |

핵심은 **구문 오류는 프로그램이 시작조차 못 하는 오류**고, **예외는 돌아가다가 특정 줄에서 만나는 오류**라는 것이다. 예외 처리는 뒤쪽, 즉 "실행 중에 터지는 것"을 다루는 모든 기법을 가리킨다. 그동안 노트에 적어 둔 `ValueError`·`TypeError`·`KeyError`·`IndexError`·`RecursionError`가 전부 이 예외다.

### 1-2. 첫 번째 방법 — 조건문으로 미리 피하기

```python
input_a = input("정수입력: ")
# int(input_a)  # 숫자가 아닌 문자열이면 ValueError

if input_a.isdigit():       # 문자열이 전부 숫자이면 True
    int(input_a)
else:
    print("정수가 아닙니다.")
```

`input()`은 항상 문자열을 돌려주고(day01), `int()`는 숫자 모양이 아닌 문자열을 받으면 `ValueError`를 던진다. 그래서 변환하기 **전에** `isdigit()`으로 "이 문자열이 정수로 바뀔 수 있는가"를 먼저 묻고, 참일 때만 `int()`를 부른다. 예외가 생길 상황을 조건문으로 걸러 내는 방식이라, 예외가 실제로 발생하지는 않는다.

이 방법은 "무엇이 잘못될지"를 미리 알아야 쓸 수 있다. `isdigit()`은 `"-5"`나 `"3.14"`에는 `False`를 돌려주므로 음수·소수까지 받으려면 조건이 복잡해진다 — 그래서 두 번째 방법이 필요하다.

### 1-3. 두 번째 방법 — `try`·`except`로 받아내기

```python
try:
    int(input_a)            # 예외가 발생할 것 같은 코드
except:
    print("정수가 아닙니다.")
```

| 블록 | 역할 |
| --- | --- |
| `try:` | 예외가 생길 가능성이 있는 코드를 감싼다. 안에서 예외가 터지면 그 줄에서 멈추고 `except`로 넘어간다 |
| `except:` | 예외가 **발생했을 때** 실행할 코드. 여기까지 오면 프로그램은 죽지 않고 다음 줄로 이어진다 |

조건문 방식과 비교하면, "미리 검사"가 아니라 **"일단 해 보고 안 되면 수습"**이다. 어떤 예외가 날지 몰라도 되고, 조건으로 쓰기 힘든 상황(파일이 없다, 네트워크가 끊겼다)에도 쓸 수 있다. 다만 `except:`만 쓰면 어떤 예외든 전부 받아버려 진짜 버그까지 덮을 수 있으니, 2단에서 보듯 예외 이름을 적는 편이 안전하다.

### 1-4. `pass` — 어떻게 처리할지 모르면 일단 넘어가기

```python
try:
    int(input_a)
except:
    pass                    # 아무것도 하지 않고 다음 줄로
```

`except` 블록은 비워 둘 수 없으므로(들여쓰기 블록이 비면 구문 오류), 아직 처리 방법을 정하지 않았을 때 `pass`로 자리를 채운다. day01의 `if` 블록, day03의 함수 몸체에 `pass`를 넣었던 것과 같은 자리 채움이다. "프로그램을 죽이지는 말되 아무 반응도 하지 않는다"는 뜻이라 개발 중 임시로는 쓸 만하지만, 실제 코드에 남겨 두면 예외가 조용히 사라져 원인을 찾기 어려워진다.

### 1-5. `else`·`finally` — 네 블록이 각각 실행되는 때

```python
try:                        # 예외가 발생할 가능성이 있는 코드
    int(input_a)
except:                     # 예외가 발생했을 때 실행
    print("정수가 아닙니다.")
else:                       # 예외가 발생하지 않았을 때 실행
    print("정수가 맞습니다.")
finally:                    # 예외가 발생하든 안 하든 무조건 실행
    print("코드가 끝났습니다.")
```

| 블록 | 예외 발생 | 예외 없음 | 비고 |
| --- | --- | --- | --- |
| `try` | 터진 줄까지만 | 전부 | |
| `except` | 실행 | 건너뜀 | |
| `else` | 건너뜀 | 실행 | `except` 뒤에만 올 수 있다. `try` 블록 안에 이어서 적어도 되지만, `else`에 두면 "이 코드는 예외 검사 대상이 아니다"가 분명해진다 |
| `finally` | 실행 | 실행 | `return`·`break`로 빠져나가도 실행된다 — 뒷정리(파일 닫기, 연결 끊기) 자리 |

입력이 `"12"`면 `정수가 맞습니다.` → `코드가 끝났습니다.`, 입력이 `"abc"`면 `정수가 아닙니다.` → `코드가 끝났습니다.`가 찍힌다. `try`/`except` 두 개만 알면 대부분 되지만, `else`는 "성공했을 때만 할 일"을 `try` 안에서 분리해 주고, `finally`는 "성공이든 실패든 꼭 할 일"을 한 곳에 모아 준다. 자바의 `try`·`catch`·`finally`에서 `catch`가 `except`로 바뀌고 `else`가 추가된 모양이다.

### 1-6. `finally`가 필요한 이유 — 열어 둔 파일

```python
try:
    file = open("info.txt", "w")    # open(파일명, 옵션) — "w"는 쓰기, 파일이 없으면 생성
    예외.발생()                     # 일부러 예외 발생 (정의되지 않은 이름 → NameError)
    file.close()                    # 예외 때문에 여기까지 오지 못한다
except:
    print("예외가 발생했습니다.")
print(file.closed)                  # False — 파일이 아직 열려 있다
```

`open()`으로 파일을 열면 운영체제 자원을 잡는다. 그런데 열고 나서 닫기 전에 예외가 터지면 `try` 블록은 그 줄에서 멈추므로 `file.close()`는 실행되지 않고, `except`로 빠져나온 뒤에도 파일은 열린 채 남는다. `file.closed`로 확인하면 `False`가 찍히는 것이 그 증거다. 이 실습을 실행하면 `info.txt`라는 빈 파일이 폴더에 생기는데, 이것은 수업 내용이 아니라 `open(..., "w")`가 만든 결과물이다.

그래서 **닫는 코드는 `finally`로 옮긴다**. `finally`는 예외가 나든 안 나든 실행되므로 `file.close()`를 거기 두면 어떤 경로로 빠져나가도 파일이 닫힌다.

```python
try:
    file = open("info.txt", "w")
    예외.발생()
except:
    print("예외가 발생했습니다.")
finally:
    file.close()
print(file.closed)                  # True
```

DB 연결, 네트워크 소켓, 락처럼 "빌렸으면 꼭 돌려줘야 하는 것"은 전부 같은 패턴이다. 2단의 `with` 문이 이 패턴을 한 줄로 줄여 준다.

### 1-7. 연습 — 오류 종류 구분과 `in` 검사

```python
numbers = [52, 273, 32, 103, 90, 10, 275]

print("# (1) 요소 내부에 있는 값 찾기")
number = 10000
try:
    number in numbers           # False — 하지만 예외는 아니다
    print("성공")
except:
    print("실패")
```

연습 파일 첫머리에는 `10 + "개"`(`TypeError`), `int("안녕하세요")`(`ValueError`), `cursor.close)`(`SyntaxError`), `[1, 2, 3, 4, 5][10]`(`IndexError`)처럼 오류 하나씩을 짝지어 적어 두었다. 이 가운데 `try`로 잡을 수 있는 것은 뒤의 셋뿐이고, `SyntaxError`는 1-1에서 본 대로 실행 전에 걸리므로 코드를 고쳐야만 한다.

본문의 `number in numbers`는 중요한 함정을 보여 준다. 10000은 리스트에 없으니 `in`은 `False`를 돌려주지만, **거짓 값은 예외가 아니다**. `try`는 "예외가 터졌는가"만 보기 때문에 그대로 `print("성공")`까지 내려간다. "값이 없으면 실패로 처리하고 싶다"면 `try`가 아니라 `if number in numbers:` 조건문이 맞고, `try`는 `numbers.index(number)`처럼 없을 때 실제로 `ValueError`를 던지는 메소드에 어울린다. 조건문(1-2)과 `try`(1-3)의 역할이 다르다는 걸 다시 확인하는 문제다.

### 1-8. 예외 객체 받기 — `except Exception as e`

```python
list_number = [52, 273, 32, 72, 100]
try:
    number_input = int(input('정수입력: '))
    print(list_number[number_input])
except Exception as e:
    print(e)
```

지금까지는 `except:` 뒤에 아무것도 적지 않고 "정수가 아닙니다"처럼 내가 정한 문장을 찍었다. 이번에는 `except Exception as e`로 **파이썬이 만든 예외 객체를 `e`라는 이름으로 받아** 그 메시지를 그대로 출력한다. `Exception`은 대부분의 내장 예외가 상속하는 공통 부모라서, 어떤 종류가 터지든 이 한 줄로 받을 수 있다.

같은 `try` 블록 안에 예외가 날 수 있는 지점이 **두 군데**라는 점이 이 예제의 핵심이다.

| 입력 | 터지는 줄 | 예외 | `print(e)` 출력 |
| --- | --- | --- | --- |
| `2` | (없음) | — | `32` |
| `10` | `list_number[number_input]` | `IndexError` | `list index out of range` |
| `abc` | `int(input(...))` | `ValueError` | `invalid literal for int() with base 10: 'abc'` |

`except:`만 썼다면 두 경우가 똑같은 문장으로 찍혀 무엇이 잘못됐는지 구분할 수 없지만, `e`를 출력하면 인덱스 범위 문제인지 변환 문제인지가 메시지에 드러난다. `print(e)`는 메시지만, `type(e).__name__`은 예외 이름(`IndexError`)을, `repr(e)`는 둘을 합친 모양을 보여 준다. day02에서 리스트 범위를 벗어나면 `IndexError`가 난다고 적어 뒀는데, 그 예외를 실제로 받아 메시지를 읽어 본 첫 자리다. 다음 단계는 2-1처럼 `Exception` 대신 `IndexError`·`ValueError`를 각각 적어 경우별로 다르게 처리하는 것이다.

## 2. 추가로 알면 좋은 활용법

### 2-1. 예외 이름을 적어서 잡기 — `except ValueError as e`

```python
try:
    value = int(input_a)
except ValueError as e:
    print("정수가 아닙니다:", e)        # invalid literal for int() with base 10: 'abc'
except (TypeError, IndexError):
    print("타입이나 인덱스 문제")
except Exception as e:
    print("예상 못 한 예외:", type(e).__name__)
```

1-8의 `except Exception as e`는 받기는 하되 종류를 가리지 않는다. `except:`만 쓰면 `KeyboardInterrupt`(Ctrl+C)나 오타로 생긴 `NameError`까지 전부 삼켜 버린다. 잡을 예외의 이름을 적으면 **의도한 실패만** 받고 나머지는 그대로 터지게 둘 수 있다. 여러 종류를 한 번에 받을 때는 튜플로 묶고, `as e`로 예외 객체를 받으면 메시지와 타입을 출력·기록할 수 있다. 자바에서 `catch (NumberFormatException e)`처럼 타입을 적던 것과 같은 자리다.

### 2-2. 조건문 vs `try` — 두 흐름을 고르는 기준

| | 조건문으로 미리 검사 (1-2) | `try`로 받아내기 (1-3) |
| --- | --- | --- |
| 전제 | 실패 조건을 미리 알고 검사할 수 있다 | 실패 조건을 모르거나 검사 자체가 어렵다 |
| 예 | `isdigit()`, `if key in dict`, `if len(lst) > i` | 파일 열기, 네트워크 요청, 외부 입력 변환 |
| 장점 | 흐름이 눈에 보인다, 예외 비용이 없다 | 검사 → 사용 사이에 상태가 바뀌어도 안전하다, 코드가 짧다 |
| 단점 | 검사가 빠지거나 불완전해지기 쉽다(`"-5"`) | 범위를 넓게 잡으면 다른 버그를 덮는다 |

파이썬 쪽에서는 `try`를 먼저 쓰는 쪽("일단 해 보고 안 되면 처리")이 관용적이다. 딕셔너리에서 `if key in d: d[key]` 대신 `try: d[key] except KeyError:`를 쓰거나 아예 `d.get(key)`를 쓰는 식이다. 다만 사용자 입력처럼 실패가 일상적이고 조건이 단순하면 조건문이 더 읽기 좋다.

### 2-3. `with open()` — `finally`의 파일 닫기를 한 줄로

```python
with open("info.txt", "w") as file:
    file.write("안녕")
# 블록을 벗어나면 예외 여부와 상관없이 file.close()가 자동 호출된다
print(file.closed)      # True
```

1-6에서 `finally: file.close()`로 썼던 것을 `with` 문이 대신한다. `with`가 열고, 블록이 끝나거나 예외로 빠져나갈 때 닫아 준다. 파일뿐 아니라 DB 연결, 락, 임시 디렉터리 등 "열고 닫는" 것은 거의 다 `with`를 지원한다. 자바의 try-with-resources(`try (var r = ...) {}`)에 대응한다.

### 2-4. 직접 예외 던지기 — `raise`

```python
def set_age(age):
    if age < 0:
        raise ValueError("나이는 0 이상이어야 합니다")
    return age

try:
    set_age(-1)
except ValueError as e:
    print(e)
```

예외는 받기만 하는 게 아니라 **내가 만든 함수가 던질 수도** 있다. 잘못된 인수를 받았을 때 `None`을 돌려주거나 조용히 넘어가는 대신 `raise`로 알리면, 호출한 쪽이 `try`로 결정할 수 있다. `except` 블록 안에서 인수 없이 `raise`만 쓰면 받은 예외를 그대로 다시 던진다(기록만 하고 처리는 위로 넘길 때).

### 2-5. 자바와 나란히 — 대응표

| 파이썬 | 자바 | 메모 |
| --- | --- | --- |
| `try:` | `try {` | |
| `except ValueError as e:` | `catch (NumberFormatException e) {` | 파이썬은 `except:`로 타입 생략 가능 |
| `else:` | (없음) | 성공했을 때만 실행 — 파이썬 고유 |
| `finally:` | `finally {` | 같다 |
| `raise ValueError("...")` | `throw new IllegalArgumentException("...")` | |
| `with open(...) as f:` | `try (var f = ...) {}` | 자원 자동 반납 |
| (없음) | `throws` 선언, checked exception | 파이썬은 모든 예외가 unchecked — 잡으라고 강제하지 않는다 |

## 3. 더 나아가 알면 좋은 것

- **예외 계층** — 모든 내장 예외는 `BaseException` → `Exception` 아래에 트리로 놓여 있다. `except Exception`은 거의 전부를 받고, `except LookupError`는 `KeyError`·`IndexError`를 한 번에 받는다
- **사용자 정의 예외** — `class InvalidAgeError(ValueError): pass`처럼 기존 예외를 상속해 내 프로그램만의 예외를 만들면, 호출한 쪽이 구체적으로 잡을 수 있다 (클래스 수업과 이어진다)
- **예외 체이닝** — `raise NewError("...") from e`로 원인 예외를 함께 남기면 트레이스백에 두 예외가 모두 찍힌다
- **`traceback`·`logging`** — `print(e)` 대신 `logging.exception("...")`을 쓰면 스택 추적까지 기록된다. `pass`로 삼키는 대신 최소한 로그를 남기는 습관
- **`assert`** — 개발 중 "여기선 반드시 참이어야 한다"를 확인하는 문. 실패하면 `AssertionError`. 사용자 입력 검증에는 쓰지 않는다(최적화 옵션에서 제거됨)
- **컨텍스트 매니저 만들기** — `__enter__`·`__exit__` 또는 `contextlib.contextmanager`로 내 자원도 `with`에 올릴 수 있다
- **EAFP vs LBYL** — "허락을 구하기보다 용서를 구하기 쉽다"(try 우선) vs "뛰기 전에 보라"(조건문 우선). 2-2의 기준을 파이썬 커뮤니티가 부르는 이름

### 다음에 볼 키워드

- `except … as e`, `raise … from`, `with`, 컨텍스트 매니저, 예외 계층, `logging.exception`, `assert`, EAFP

## 실습 파일

- `KDT_2026/2026_Python/day04/c6-1.py` — 구문 오류·런타임 오류·예외 처리 정의. `input()` 값을 `isdigit()` 조건문으로 걸러 `int()` 변환(예1), 같은 변환을 `try`/`except`로(예2), `except: pass`로 넘기기(예3), `try`/`except`/`else`/`finally` 네 블록(예4), `open("info.txt", "w")` 뒤 일부러 예외를 일으켜 `file.close()`가 건너뛰어지고 `file.closed`가 `False`로 남는 것 확인(`finally` 활용 예)
- `KDT_2026/2026_Python/day04/c6-2.py` — 정수를 입력받아 `list_number`의 인덱스로 쓰는 코드를 `try`로 감싸고, `except Exception as e: print(e)`로 예외 객체의 메시지를 그대로 출력. 범위를 벗어난 숫자(`IndexError`)와 숫자가 아닌 문자열(`ValueError`)이 서로 다른 메시지로 찍히는 것 확인
- `KDT_2026/2026_Python/practice/p397-381.py` — 오류 종류 메모(`10 + "개"`·`int("안녕하세요")`·`cursor.close)`·`[1, 2, 3, 4, 5][10]`)와 확인문제 (1): `numbers` 리스트에 `number in numbers`를 `try`로 감싸 "성공"/"실패" 출력 — 거짓 값은 예외가 아니라 `try`가 잡지 않는 것 확인
- `KDT_2026/2026_Python/info.txt` — 위 실습이 `open(..., "w")`로 만든 빈 결과 파일 (수업 내용 없음)

## 관련 노트

[[Python 정리본 인덱스]] · [[Python day03 함수·재귀·람다 연습문제 풀이]] · [[Python day05 클래스 정의와 생성자·메소드]] · [[Python day01 비교·논리 연산자와 if 조건문]] · [[Python day01 파이썬 시작과 키워드 확인]] · [[KDT_2026 학습 지도]]
