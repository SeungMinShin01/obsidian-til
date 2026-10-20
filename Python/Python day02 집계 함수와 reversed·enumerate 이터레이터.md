---
출처: Claude 분석
원본: KDT_2026/2026_Python/day02/c4-4.py
작성일: 2026-10-20
tags: [학습, python]
---

# Python day02 — 집계 함수와 reversed·enumerate 이터레이터

> 실습 파일: `day02/c4-4.py`
> 허브: [[Python 정리본 인덱스]] · 이전: [[Python day02 range 함수와 for·while 반복문]] · 다음: [[Python day02 딕셔너리 연습문제 풀이]]

`range` 노트까지가 "무엇을 돌 것인가"였다면, 이 파일은 **리스트를 돌지 않고도 답을 얻는 내장 함수**와 **돌 때 번호·키를 같이 받는 법**이다. 교재 4-4 "문자열, 리스트, 딕셔너리와 관련된 기본 함수"에 해당하는 내용으로, `min`·`max`·`sum`으로 한 줄에 집계하기, `reversed()`가 리스트가 아니라 **이터레이터**를 돌려준다는 것과 `next()`로 하나씩 꺼내기, 이터러블·이터레이터라는 용어, `enumerate()`로 인덱스와 값을 짝지어 돌기, `dict.items()`로 키와 값을 함께 받기까지가 전부다. `range` 노트 끝에서 "필요할 때 하나씩 내놓는 자료"를 잠깐 언급했는데, 이번에 그 정체를 `reversed()`로 직접 눈에 담는다. 결국 `for`가 **무엇이든 돌 수 있는 이유**가 이 노트의 축이다.

## 1. 배운 내용

### 1-1. `min`·`max`·`sum` — 리스트를 돌지 않고 집계

```python
numbers = [103, 52, 273, 32, 77]
print(min(numbers))   # 32  — min(리스트) 최솟값
print(max(numbers))   # 273 — max(리스트) 최댓값
print(sum(numbers))   # 537 — sum(리스트) 합계
```

| 함수 | 돌려주는 것 | 직접 쓰면 |
| --- | --- | --- |
| `min(리스트)` | 가장 작은 요소 | `for`로 돌며 더 작은 값을 갈아끼우기 |
| `max(리스트)` | 가장 큰 요소 | `for`로 돌며 더 큰 값을 갈아끼우기 |
| `sum(리스트)` | 모든 요소의 합 | `total = 0` 두고 `for`로 더하기 |

세 함수 모두 **리스트를 통째로 넘기면 값 하나**를 돌려준다. 자바에서 최댓값을 구하려면 `int max = arr[0]; for (...) if (arr[i] > max) max = arr[i];`처럼 반복문을 손으로 쓰거나 `Arrays.stream(arr).max()`를 불러야 했는데, 파이썬은 이 셋이 내장 함수라 `import` 없이 바로 쓴다. `range` 노트의 `sum(range(1, 11))`도 같은 함수였다 — 인자가 리스트든 `range`든 **순서대로 꺼낼 수만 있으면** 받아 준다. 그 "꺼낼 수 있다"는 조건이 아래 1-3의 이터러블이다.

이 함수들은 리스트 자체를 바꾸지 않는다. `sort()`나 `append()`가 원본을 건드리고 `None`을 돌려주던 것과 반대로, `min`·`max`·`sum`은 원본을 그대로 두고 **결과만 새 값으로** 준다. 리스트 노트에서 나눠 두었던 "원본 변경 vs 새 값 반환" 구분을 여기에도 적용하면 된다.

### 1-2. `reversed()` — 리스트가 아니라 이터레이터가 나온다

```python
numbers_reversed = reversed(numbers)   # 리스트 뒤집기
print(numbers_reversed)                # <list_reverseiterator object at 0x...>
print(next(numbers_reversed))          # 77 — 하나 꺼낸다
print(list(numbers_reversed))          # [32, 273, 52, 103] — 남은 것을 리스트로
```

| 줄 | 결과 | 읽는 법 |
| --- | --- | --- |
| `reversed(numbers)` | `<list_reverseiterator object …>` | 뒤집힌 **리스트**가 아니라 "뒤에서부터 꺼낼 준비가 된 객체" |
| `next(…)` | `77` | 꺼내기 함수 — 마지막 요소부터 하나 |
| `list(…)` | `[32, 273, 52, 103]` | 남은 요소를 전부 꺼내 리스트로 모은다 |

`print(reversed(numbers))`를 찍으면 뒤집힌 리스트 대신 `<list_reverseiterator object at 0x…>`라는 낯선 글자가 나온다. `range` 노트에서 `print(range(5))`가 `range(0, 5)`로만 찍혔던 것과 같은 현상이다 — **아직 아무것도 만들지 않고, 꺼낼 준비만 된 객체**가 돌아온 것이다. 그래서 눈으로 확인하려면 `list()`로 감싸 리스트로 바꿔야 한다.

중간에 `next()`가 한 번 끼어 있는 것이 이 예제의 핵심이다. `next(numbers_reversed)`가 `77`(원래 리스트의 마지막 요소)을 꺼내고 나면, 그 뒤의 `list()`에는 **이미 꺼낸 77이 빠진** `[32, 273, 52, 103]`만 담긴다. 이터레이터는 한 번 지나간 요소를 되돌리지 않는다. 책을 읽는 손가락처럼 "지금 어디까지 꺼냈는지"를 기억하고 앞으로만 간다. 리스트의 `reverse()` 메소드는 원본 자체를 제자리에서 뒤집고 `None`을 돌려주며, 슬라이싱 `[::-1]`은 뒤집힌 **새 리스트**를 만든다 — `reversed()`는 둘과 다르게 **한 번 돌 때 쓰고 버리는 꺼내기 객체**다. 셋의 차이를 표로 두면 이렇다.

| 방법 | 원본 | 돌려주는 것 | 두 번 쓸 수 있나 |
| --- | --- | --- | --- |
| `numbers.reverse()` | 바뀜 | `None` | 원본이 바뀌었으니 그대로 |
| `numbers[::-1]` | 그대로 | 새 리스트 | 가능 |
| `reversed(numbers)` | 그대로 | 이터레이터 | 한 번 소진하면 끝 |

주석에 있던 `int()`·`float()`·`str()`·`list()`는 **특정 타입으로 바꾸는 변환 함수**로 묶인다. day01에서 `input()`의 문자열을 `int()`로 바꾸던 것과 여기서 `list(reversed(...))`로 리스트를 만드는 것이 같은 종류의 일이다 — 이터레이터·`range`·문자열·튜플 무엇이든 `list()`에 넣으면 요소를 전부 꺼내 리스트로 담아 준다.

### 1-3. 이터러블과 이터레이터 — `for`가 돌 수 있는 조건

```python
# 이터러블   : 요소들을 하나씩 차례로 꺼내기 가능한 객체
# 이터레이터 : 이터러블에서 하나씩 차례로 빼내는 역할을 하는 객체
# 이터레이터를 가진 타입 : 리스트 / 딕셔너리 / 문자열 / 튜플 / range 등
# 하나씩 꺼내는 함수 = next()
# 즉, 이터레이터가 존재하는 자료만 for에 쓸 수 있다
```

| 용어 | 뜻 | 예 |
| --- | --- | --- |
| 이터러블(iterable) | 요소를 **하나씩 차례로 꺼낼 수 있는** 객체 | 리스트·문자열·튜플·딕셔너리·`range` |
| 이터레이터(iterator) | 이터러블에서 실제로 **하나씩 빼내는** 객체. `next()`로 다음 것을 준다 | `reversed(...)`·`enumerate(...)`의 결과 |
| `next(이터레이터)` | 다음 요소 하나를 꺼낸다. 더 없으면 `StopIteration` | `next(reversed(numbers))` |

수업에서는 두 단어를 이렇게 정리했다. **이터러블**은 "꺼낼 수 있는 자료" 전체를 가리키는 넓은 말이고, **이터레이터**는 그 자료에서 실제로 한 개씩 빼내는 **손**이다. 리스트·문자열·튜플·딕셔너리·`range`는 모두 이터러블이라서 `for`에 넣을 수 있고, `for`는 내부적으로 그 자료에서 이터레이터를 하나 얻어 `next()`를 반복해서 부른다. 그래서 `for`에 정수 `10`을 넣으면 `'int' object is not iterable`이라는 오류가 난다 — 정수는 하나씩 꺼낼 요소가 없기 때문이다. day02 리스트 노트에서 "리스트·문자열을 도는 `for`"로 적어 둔 것과 `range` 노트의 `for i in range(...)`가 **같은 규칙 하나**에서 나온다는 것이 이 정리의 결론이다. `for`가 리스트·문자열·`range`를 가리지 않는 것은 각각을 따로 지원해서가 아니라, 전부 "꺼낼 수 있는 자료"라는 약속을 지키기 때문이다.

`reversed()`가 돌려준 것은 이터러블 중에서도 **이미 꺼내는 손이 쥐어진 상태**, 즉 이터레이터였다. 그래서 `next()`를 바로 부를 수 있었다. 리스트에는 `next(numbers)`를 바로 쓸 수 없고(`'list' object is not an iterator`), `iter(numbers)`로 손을 먼저 얻어야 한다 — 이 차이가 "이터러블이지만 이터레이터는 아니다"의 실제 모습이다.

### 1-4. `enumerate()` — 인덱스와 값을 짝지어 돌기

```python
numbers = [103, 52, 273, 32, 77]
print(enumerate(numbers))          # <enumerate object at 0x...>
print(list(enumerate(numbers)))    # [(0, 103), (1, 52), (2, 273), (3, 32), (4, 77)]

for index, value in enumerate(numbers):
    print(index, value)
# 0 103
# 1 52
# ...
```

| 표현 | 결과 |
| --- | --- |
| `enumerate(numbers)` | `<enumerate object …>` — 역시 꺼내기 객체 |
| `list(enumerate(numbers))` | `[(0, 103), (1, 52), …]` — **(인덱스, 값) 튜플**의 리스트 |
| `for index, value in enumerate(numbers):` | 튜플을 변수 두 개로 받아 번호와 값을 함께 쓴다 |

`enumerate(리스트)`는 각 요소에 **0부터 번호를 붙여 `(인덱스, 값)` 튜플**로 내놓는다. `print(enumerate(numbers))`가 `<enumerate object at …>`로 찍히는 것도 `reversed`와 같은 이유고, `list()`로 바꿔 보면 소괄호로 묶인 튜플이 줄지어 보인다. 리스트 노트에서 잠깐 이름만 적어 둔 그 `enumerate`다.

`for index, value in enumerate(numbers):`처럼 **변수 두 개**로 받는 모양이 관용구다. 한 바퀴마다 튜플 `(0, 103)`이 나오는데, 이것을 `index, value`에 나눠 담는다 — 리스트 노트에서 본 튜플의 "풀어서 받기"가 `for`문 머리에 들어간 것이다. `range` 노트의 `for i in range(len(fruits)): print(i, fruits[i])`와 결과는 같지만, 인덱스로 다시 `fruits[i]`를 꺼내는 수고가 없어 읽기 쉽다. 자바의 `for (int i = 0; i < arr.length; i++)`에서 `i`와 `arr[i]`를 둘 다 쓰던 자리를 파이썬은 이 한 줄로 대신한다.

### 1-5. `dict.items()` — 키와 값을 함께 받기

```python
dict_a = {"name": "유재석", "age": 10}
for key, value in dict_a.items():
    print(key, value)
# name 유재석
# age 10
```

딕셔너리 노트에서 `for`로 딕셔너리를 돌리면 **키만** 나온다고 정리했고, `items()`를 쓰면 `(키, 값)` 쌍이 나온다고 적어 두었다. 이 파일에서 그것을 `enumerate` 바로 옆에 두고 다시 본 이유가 분명하다 — **모양이 같다.** `enumerate`가 `(인덱스, 값)` 튜플을 내놓고 `items()`가 `(키, 값)` 튜플을 내놓으니, 받는 쪽은 둘 다 `for a, b in …:`로 똑같이 쓴다. 리스트는 번호가 자동으로 붙는 자료고 딕셔너리는 번호 대신 키가 붙은 자료라는 차이만 있다. `list(dict_a.items())`를 찍어 보면 `[('name', '유재석'), ('age', 10)]`로, `list(enumerate(numbers))`와 같은 "튜플의 리스트" 모양이 나온다.

## 2. 추가로 알면 좋은 활용법

### 2-1. 집계 함수의 인자 — 키 함수·기본값·빈 리스트

```python
words = ["banana", "kiwi", "apple"]
print(max(words, key=len))          # banana — 길이 기준 최댓값
print(min(words))                   # apple  — 문자열은 사전순

scores = {"철수": 80, "영희": 95}
print(max(scores, key=scores.get))  # 영희 — 값이 가장 큰 키

print(sum([]))                      # 0
print(max([], default=0))           # 0 — 빈 리스트에 max는 오류, default로 막는다
print(sum([1.5, 2.5], 10))          # 14.0 — 두 번째 인자는 시작값
```

`max`·`min`에 `key=`를 주면 **무엇을 기준으로 크다고 볼지**를 함수로 넘길 수 있다. `key=len`이면 길이, `key=scores.get`이면 딕셔너리의 값이 기준이 된다 — 리스트 노트의 `sort(key=...)`와 같은 인자다. 빈 리스트에 `sum`은 0이지만 `max`·`min`은 비교할 것이 없어 `ValueError`를 내므로, 비어 있을 수 있는 자료라면 `default=`를 두는 편이 안전하다. `sum`의 두 번째 인자는 시작값이라, 10에서 출발해 더하고 싶을 때 쓴다.

### 2-2. `enumerate`의 시작 번호와 `zip`

```python
fruits = ["사과", "배", "감"]
for no, name in enumerate(fruits, start=1):   # 1부터 번호 붙이기
    print(f"{no}. {name}")

prices = [1000, 2000, 1500]
for name, price in zip(fruits, prices):       # 두 리스트를 나란히
    print(name, price)

for i, (name, price) in enumerate(zip(fruits, prices)):   # 번호까지
    print(i, name, price)
```

사람이 보는 목록은 1번부터 세는 일이 많은데, `enumerate(리스트, start=1)`로 시작 번호를 바꾸면 `no + 1`을 따로 계산하지 않아도 된다. 두 리스트를 **같은 자리끼리** 묶어 돌 때는 `zip`이 `(a, b)` 튜플을 내놓는다 — `enumerate`가 번호와 요소를 짝지었다면 `zip`은 요소와 요소를 짝짓는다. 둘을 겹치면 튜플 안에 튜플이 생기므로 `i, (name, price)`처럼 괄호로 모양을 맞춰 받는다. 길이가 다르면 짧은 쪽에서 멈춘다는 것만 기억해 두면 된다.

### 2-3. 이터레이터를 안전하게 소진하기 — `next`의 기본값과 한 번만 쓰기

```python
it = reversed([1, 2, 3])
print(next(it))              # 3
print(next(it))              # 2
print(next(it))              # 1
print(next(it, "끝"))        # "끝" — 더 없을 때 StopIteration 대신 기본값

it = reversed([1, 2, 3])
print(list(it))              # [3, 2, 1]
print(list(it))              # []  — 이미 소진됐다
```

`next()`에 두 번째 인자를 주면 요소가 바닥났을 때 오류 대신 그 값을 돌려준다. 이터레이터를 변수에 담아 두고 두 번 돌리면 두 번째는 빈 결과가 나오는데, 1-2에서 `next()` 뒤의 `list()`에 77이 빠져 있던 것과 같은 성질이다. **두 번 쓸 자료라면 `list()`로 받아 두고, 한 번 돌고 말 자료라면 이터레이터 그대로** 쓴다는 기준을 세워 두면 헷갈리지 않는다. `for` 안에서 바로 쓰는 `for x in reversed(numbers):`는 이 걱정이 없다.

### 2-4. 딕셔너리 집계 — `items()`·`values()`와 집계 함수 엮기

```python
scores = {"철수": 80, "영희": 95, "민수": 70}
print(sum(scores.values()) / len(scores))      # 81.666… — 평균
print(max(scores.values()))                    # 95
best = max(scores.items(), key=lambda kv: kv[1])
print(best)                                    # ('영희', 95) — 값 기준 최대 쌍

for rank, (name, score) in enumerate(sorted(scores.items(), key=lambda kv: kv[1], reverse=True), start=1):
    print(rank, name, score)                   # 1 영희 95 / 2 철수 80 / 3 민수 70
```

`values()`는 값만 모은 이터러블이라 `sum`·`max`에 바로 넘길 수 있고, `items()`를 넘기면서 `key`로 "튜플의 두 번째 칸"을 지정하면 **값이 가장 큰 (키, 값) 쌍**이 나온다. 마지막 줄은 이 노트의 재료를 전부 한 줄에 모은 것이다 — `items()`로 쌍을 만들고, `sorted(key=…)`로 값 순으로 세우고, `enumerate(start=1)`로 순위를 붙여 `rank, (name, score)`로 받는다. 딕셔너리 노트의 "횟수 세기 패턴"에 이 줄을 이으면 단어 빈도 순위표가 그대로 나온다.

## 3. 더 나아가 알면 좋은 것

### 3-1. `for`가 실제로 하는 일 — `iter()`와 `next()`

```python
numbers = [1, 2, 3]
it = iter(numbers)        # for가 맨 처음 하는 일
while True:
    try:
        x = next(it)      # for가 매 바퀴 하는 일
    except StopIteration:
        break             # 바닥나면 조용히 끝
    print(x)
```

`for x in numbers:`는 위 코드의 줄임말이다. `iter(자료)`로 이터레이터를 얻고, `next()`를 바닥날 때까지 부르며, `StopIteration`이 나면 멈춘다. 1-3에서 "이터레이터가 있는 자료만 `for`에 쓸 수 있다"고 한 말이 정확히 이 구조에서 나온다. 리스트처럼 `iter()`에 응답할 수 있으면 이터러블이고, 그 결과처럼 `next()`에 응답하면 이터레이터다. `range` 노트에서 "지연 평가"라 적어 둔 것도 결국 `next()`가 불릴 때마다 하나씩 계산한다는 뜻이었다. 자바의 `Iterable`·`Iterator` 인터페이스와 `hasNext()`·`next()`가 거의 같은 약속이고, 향상된 `for`가 그것을 감추는 구조도 같다.

### 3-2. 직접 만드는 이터레이터 — 제너레이터와 `yield`

```python
def countdown(n):
    while n > 0:
        yield n           # 값을 하나 내주고 멈춰 있다가, 다음 next()에 이어서 돈다
        n -= 1

for i in countdown(3):
    print(i)              # 3, 2, 1

squares = (x * x for x in range(5))   # 제너레이터 표현식 — 대괄호 대신 소괄호
print(next(squares))                  # 0
```

`reversed`·`enumerate`·`range`처럼 "필요할 때 하나씩" 내놓는 자료를 직접 만들려면 함수 안에 `return` 대신 `yield`를 쓴다. 이런 함수를 **제너레이터**라 부르고, 호출하면 바로 돌지 않고 이터레이터를 돌려준다. 리스트 컴프리헨션의 대괄호를 소괄호로 바꾼 **제너레이터 표현식**도 같은 성질이라, 정보처리기사 쪽에 이관된 코드 해석 문제에서 본 모양이 바로 이것이다. 백만 줄짜리 파일을 한 줄씩 읽거나, 크롤러가 페이지를 하나씩 넘기며 결과를 내놓는 자리에서 메모리를 아끼는 도구다.

### 3-3. 집계 함수 너머 — `sorted`·`any`·`all`·`functools.reduce`

`min`·`max`·`sum`처럼 이터러블을 받아 값 하나를 돌려주는 내장 함수가 더 있다. `any(조건들)`은 하나라도 참이면, `all(조건들)`은 전부 참이면 `True`다 — `any(x > 100 for x in numbers)`처럼 제너레이터 표현식과 함께 쓰면 "100 넘는 게 있나"를 한 줄로 묻는다. `sorted`는 새 정렬 리스트를 돌려주고, `len`은 개수를 센다. `sum`으로 안 되는 누적(곱하기, 문자열 이어 붙이기 규칙 등)은 `functools.reduce(함수, 이터러블)`이 맡는다. 자바 스트림의 `min`·`max`·`sum`·`anyMatch`·`allMatch`·`reduce`와 이름이 거의 같아서, 한쪽을 알면 다른 쪽도 짐작이 된다.

### 3-4. 다음에 볼 키워드

- `iter`·`next`·`StopIteration`과 `__iter__`·`__next__` — 클래스로 이터레이터 만들기
- 제너레이터(`yield`)와 제너레이터 표현식, `itertools`(`chain`·`islice`·`groupby`)
- `zip`·`enumerate`·`sorted`를 겹쳐 쓰는 관용구와 `lambda`로 `key` 넘기기
- `any`·`all`·`functools.reduce`, `collections.Counter`로 빈도 집계
- 함수 정의(`def`)와 매개변수 — 집계 로직을 함수로 묶기

## 실습 파일

- `KDT_2026/2026_Python/day02/c4-4.py` — `min`·`max`·`sum`으로 리스트 집계, `reversed()`가 `<list_reverseiterator object>`를 돌려주는 것과 `next()`로 하나 꺼낸 뒤 `list()`로 남은 요소 모으기, `int()`·`float()`·`str()`·`list()` 변환 함수, 이터러블·이터레이터 용어 정리와 `for`에 쓸 수 있는 자료(문자열·리스트·튜플·딕셔너리·`range`), `enumerate()`의 `<enumerate object>`와 `list()`로 본 `(인덱스, 값)` 튜플, `for index, value in enumerate(...)`, `for key, value in dict.items()`

## 관련 노트

[[Python 정리본 인덱스]] · [[Python day02 range 함수와 for·while 반복문]] · [[Python day02 딕셔너리 연습문제 풀이]] · [[KDT_2026 학습 지도]]
