---
출처: Claude 분석
원본: KDT_2026/2026_Python/day03/C5-3.PY
작성일: 2026-10-21
tags: [학습, python]
---

# Python day03 — 콜백 함수와 map·filter·람다

> 실습 파일: `day03/C5-3.PY` (뒷부분 — 콜백·map·filter·람다)
> 허브: [[Python 정리본 인덱스]] · 이전: [[Python day03 튜플 선언과 구조분해·스왑]] · 다음: (아직 없음)

함수 노트 끝에 "함수도 값이다"라고 한 줄 적어 두었는데, 이 파일 뒷부분이 그 한 줄을 펼친다. 수업의 정의는 **콜백 함수 — 함수 그 자체를 매개변수로 전달하여, 전달받은 곳에서 함수를 호출하는 것**. 리액트에서 `onClick={회원가입}`이라고 쓰고 `onClick={회원가입()}`이라고는 쓰지 않던 이유가 여기서 파이썬 문법으로 다시 설명된다. 그다음은 그 콜백을 받는 대표 내장 함수 `map`·`filter`이고, 마지막이 콜백으로 넘길 한 줄짜리 함수를 이름 없이 만드는 `lambda`다. 수업은 매 단계마다 자바 스트림과 JS 배열 메소드를 나란히 적어 두었다 — `리스트.stream().map()` ↔ `리스트.map()` ↔ `map(함수, 리스트)`. 세 언어에서 **"반복하면서 각 요소에 함수를 적용한다"**는 같은 생각을 이미 두 번 배웠고, 이번이 세 번째다.

## 1. 배운 내용

### 1-1. 콜백 — 함수를 호출하지 않고 함수 자체를 넘기기

```python
# onClick( 회원가입() ) [X]  ---->  onClick( 회원가입 ) [O]
def call_10_items(func):     # 값 대신에 함수 받기
    func()                   # 받은 함수를 여기서 호출

def print_hello():
    print("안녕하세요")

call_10_items(print_hello)   # 함수 자체를 넘긴다 → 안에서 func()가 실행돼 "안녕하세요"
```

| 쓰는 모양 | 넘어가는 것 | 결과 |
| --- | --- | --- |
| `call_10_items(print_hello)` | 함수 객체 | `call_10_items` 안의 `func()`에서 호출되어 "안녕하세요" |
| `call_10_items(print_hello())` | `print_hello()`를 **먼저 실행한 결과** — 돌려주는 값이 없으니 `None` | "안녕하세요"는 넘기기 전에 찍히고, 안에서 `None()`을 부르려다 `TypeError` |

핵심은 **괄호의 유무**다. `print_hello`는 함수라는 값이고, `print_hello()`는 그 함수를 실행한 결과다. 함수 노트 1-1에서 "이름 뒤에 괄호를 붙여야 실행되고, 괄호가 없으면 함수 객체를 가리킬 뿐"이라고 정리한 그 성질이, 여기서는 **괄호를 일부러 떼어 함수를 값처럼 건네는** 쪽으로 쓰인다. 받는 쪽 `call_10_items`는 매개변수 `func`에 함수가 들어온다는 전제로 `func()`라고 괄호를 붙여 부른다. 넘기는 쪽은 괄호 없이, 받는 쪽은 괄호를 붙여서 — 이것이 콜백의 모양이다.

"콜백(callback)"이라는 이름은 **"나중에 다시 불러 달라"**는 뜻이다. 내가 지금 실행하는 게 아니라 함수를 맡겨 두면 상대가 적절한 때(버튼이 눌렸을 때, 요소를 하나씩 돌 때, 응답이 도착했을 때)에 대신 불러 준다. 리액트의 `onClick={handleClick}`, `useEffect(() => {...}, [])`, 자바 스프링의 `forEach(item -> …)`가 전부 이 구조다. 수업 주석의 `onClick(회원가입())`이 틀린 이유도 같다 — 괄호를 붙이면 렌더링 시점에 회원가입이 **즉시 실행**되고 버튼에는 그 결과값(`undefined`)이 걸린다.

### 1-2. 세 언어의 반복 삼총사 — forEach · map · filter

```python
# java   : 리스트.stream().forEach() , .map() , .filter()
# react  : 리스트.forEach() , 리스트.map() , 리스트.filter()
# python : for X in 리스트 , map(코드, 리스트) , filter(코드, 리스트)
# forEach 단순반복(return 없다) , map 반복+반환(return 있다) , filter 반복+(참이면)반환
```

| 하는 일 | 자바 스트림 | JS / 리액트 | 파이썬 | 반환 |
| --- | --- | --- | --- | --- |
| 단순 반복 | `list.stream().forEach(f)` | `list.forEach(f)` | `for x in list:` | 없음 |
| 반복 + 변환 | `list.stream().map(f)` | `list.map(f)` | `map(f, list)` | 요소마다 `f`의 결과 |
| 반복 + 걸러내기 | `list.stream().filter(f)` | `list.filter(f)` | `filter(f, list)` | `f`가 참인 요소만 |

세 언어가 같은 세 가지를 갖고 있다. 다만 **호출 모양**이 다르다. 자바·JS는 `리스트.map(함수)`처럼 리스트 뒤에 점을 찍어 메소드로 부르고, 파이썬은 `map(함수, 리스트)`처럼 **내장 함수에 함수와 리스트를 둘 다 인수로** 넣는다. 함수가 첫 번째, 리스트가 두 번째라는 순서를 기억해 두면 된다. 파이썬에서 `forEach`에 해당하는 것은 따로 없고 그냥 `for`문이다 — 돌려주는 값 없이 요소마다 무언가 할 때는 `for`가 가장 읽기 쉽다.

구분하는 기준은 **무엇을 돌려주느냐**다. forEach는 아무것도 돌려주지 않고 찍거나 저장하는 부수 효과만 낸다. map은 요소 개수 그대로 **변환된 값**을 돌려주고, filter는 조건 함수가 참을 돌려준 요소만 **골라서** 돌려주므로 개수가 줄어들 수 있다. 리액트 수업에서 게시글 배열을 `<li>`로 바꿀 때 `map`을 쓰고, 검색어에 맞는 것만 남길 때 `filter`를 쓰던 구분과 같다.

### 1-3. `map` — 요소마다 함수를 적용해 새 값을 만든다

```python
def power(item):
    return item * item

list_a = [1, 2, 3, 4, 5]
output_a = map(power, list_a)      # power를 호출하지 않고 넘긴다
print(list(output_a))              # [1, 4, 9, 16, 25]
# JS map : list_a.map(power) , list_a.map(x => x * x)
```

| 단계 | 일어나는 일 |
| --- | --- |
| `map(power, list_a)` | "list_a의 각 요소에 power를 적용하겠다"는 **map 객체**를 만든다. 아직 계산 전 |
| `list(output_a)` | 실제로 하나씩 꺼내며 `power(1)`, `power(2)`, … 를 호출해 리스트로 담는다 |

`map`에 넘기는 `power`는 1-1의 콜백이다. `map` 안쪽에서 요소를 하나 꺼낼 때마다 `power(요소)`로 대신 불러 준다. 그래서 `power`는 **요소 하나를 받아 변환된 값 하나를 `return`하는** 함수여야 한다 — `return`이 없으면 결과가 전부 `None`이 된다.

`print(output_a)`를 그대로 찍으면 `[1, 4, 9, …]`가 아니라 `<map object at 0x…>`가 나온다. day02 이터레이터 노트에서 `reversed()`가 리스트가 아닌 이터레이터를 돌려주던 것과 같은 성질로, `map`도 **필요할 때 하나씩 계산하는 이터레이터**를 돌려준다. 그래서 눈으로 보려면 `list()`로 감싸고, `for`에 바로 넣으면 변환 없이 쓸 수 있다. 한 번 소진하면 다시 돌 수 없는 것도 같다. JS의 `list_a.map(power)`가 바로 새 배열을 만드는 것과 다른 점이다.

### 1-4. `filter` — 조건 함수가 참인 요소만 남긴다

```python
def under_3(item):
    return item < 3                 # True / False를 돌려준다

output_b = filter(under_3, list_a)
print(list(output_b))               # [1, 2]
# JS filter : list_a.filter(under_3) , list_a.filter(x => x < 3)
```

| 요소 | `under_3(요소)` | 남나 |
| --- | --- | --- |
| 1 | `True` | 남는다 |
| 2 | `True` | 남는다 |
| 3 | `False` | 빠진다 |
| 4, 5 | `False` | 빠진다 |

`filter`에 넘기는 함수는 **참·거짓을 돌려주는** 함수여야 한다. 요소마다 호출해서 `True`면 남기고 `False`면 버린다. `map`과 다르게 요소 자체는 바뀌지 않고 **개수만 줄어든다**. 비교식 `item < 3`은 day01 조건문 노트에서 본 대로 `bool` 값을 내므로 그대로 `return`하면 된다. `map`과 마찬가지로 filter 객체(이터레이터)를 돌려주므로 `list()`로 감싸서 본다.

### 1-5. 람다 — 이름 없는 한 줄 함수

```python
# lambda 매개변수 : 리턴값      ↔  PY : def 함수명(매개변수): return 리턴값
# JAVA 람다 : () -> { }         ↔  JAVA : public void 함수명() { }
# JS 람다   : () => { }         ↔  JS   : function 함수명() { }

power = lambda item: item * item       # def power(item): return item * item 과 같다
output_a = map(power, list_a)

# 인라인 람다 — 변수에 담지 않고 그 자리에서
output_a = map(lambda item: item * item, list_a)
```

| | `def` | `lambda` |
| --- | --- | --- |
| 모양 | `def power(item):` + 들여쓴 몸체 + `return` | `lambda item: item * item` — 한 줄 |
| 이름 | 있다 | 없다 (변수에 담으면 이름이 생기는 셈) |
| 몸체 | 여러 문장 | **식 하나** — 그 식의 값이 자동으로 반환값 |
| `return` | 직접 쓴다 | 쓰지 않는다 (쓰면 오류) |
| 쓰는 자리 | 여러 번 부를 함수 | `map`·`filter`·`sorted(key=)`처럼 **한 번 넘기고 말** 콜백 |

`lambda 매개변수: 식`은 `def`로 쓰면 세 줄이 될 함수를 한 줄로 줄인 것이다. 콜론 앞이 매개변수, 콜론 뒤가 `return`할 식이다. `power = lambda item: item * item`처럼 변수에 담으면 `def power`와 똑같이 `power(3)`으로 부를 수 있다. 하지만 수업 코드가 마지막에 보여 주듯 람다의 본래 자리는 **인라인** — `map(lambda item: item * item, list_a)`처럼 콜백이 필요한 그 자리에 바로 적고 끝내는 용도다. 한 번 쓰고 말 함수에 이름을 붙여 위에 따로 정의해 두는 수고를 덜어 준다. 연습문제 노트에서 `max(pairs, key=lambda p: p[0] * p[1])`로 쓴 것이 바로 이 용법이었다.

### 1-6. 세 언어의 람다 대응 — 리액트 코드와 나란히

```javascript
// React
// 1. 이름 붙여서
const power = (item) => { return item * item }
list_a.map(power)
// 2. 인라인
list_a.map((item) => { return item * item })
list_a.map(item => item * item)          // 중괄호·return 생략형
```

| 언어 | 이름 있는 함수 | 람다(익명 함수) | 화살표 방향 |
| --- | --- | --- | --- |
| 파이썬 | `def f(x): return x * x` | `lambda x: x * x` | 콜론 `:` |
| JS | `function f(x) { return x * x }` | `(x) => x * x` | `=>` |
| 자바 | `int f(int x) { return x * x; }` | `x -> x * x` | `->` |

세 언어 모두 "매개변수 → 식"의 모양이고 기호만 다르다. JS의 `item => item * item`에서 중괄호와 `return`을 생략한 형태가 파이썬 람다와 가장 비슷하다 — 둘 다 **식 하나를 그대로 돌려준다**. 자바 스프링 수업에서 `list.stream().map(x -> x * x)`로 쓰던 것도 같은 자리다. 수업 끝에 "람다는 JAVA 등과 비교하면서 공부해볼 것"이라고 적혀 있는데, 비교의 축은 **①이름이 없다 ②한 줄 식이다 ③콜백 자리에 바로 적는다** 세 가지다. 다만 JS·자바 람다는 중괄호를 열면 여러 문장을 쓸 수 있는 반면, 파이썬 람다는 **식 하나로 끝**이라 두 문장 이상이 필요하면 `def`로 돌아가야 한다.

## 2. 추가로 알면 좋은 활용법

### 2-1. `map`·`filter` 대신 컴프리헨션 — 파이썬다운 쓰기

```python
[item * item for item in list_a]                  # map(lambda item: item * item, list_a)
[item for item in list_a if item < 3]             # filter(lambda item: item < 3, list_a)
[item * item for item in list_a if item < 3]      # filter 후 map을 한 줄에
```

리스트 노트 끝에 적어 둔 리스트 컴프리헨션이 `map`·`filter`와 같은 일을 한다. `for` 앞이 변환(map), `if` 뒤가 조건(filter)이다. 람다 없이 식을 그대로 적을 수 있고 결과가 바로 리스트라 `list()`로 감쌀 필요도 없어서, 실제 파이썬 코드에서는 `map`·`filter`보다 컴프리헨션을 더 많이 본다. `map`·`filter`가 어울리는 건 이미 `def`로 만들어 둔 함수를 그대로 넘길 때(`map(str, nums)`, `map(int, input().split())`)다.

### 2-2. `sorted`·`max`·`min`의 `key=` — 람다가 가장 자주 서는 자리

```python
students = [("철수", 85), ("영희", 92), ("민수", 78)]
sorted(students, key=lambda s: s[1])              # 점수 오름차순
sorted(students, key=lambda s: s[1], reverse=True)
max(students, key=lambda s: s[1])                 # ("영희", 92)
```

`key=`는 "무엇을 기준으로 비교할지"를 함수로 받는 콜백 매개변수다. 요소가 튜플·딕셔너리처럼 묶음일 때 어느 칸으로 정렬할지를 람다 한 줄로 지정한다. 딕셔너리 연습문제 노트에서 `sorted(counter.items(), key=lambda kv: kv[1])`로 값 기준 정렬을 했던 것이 이것이다. 자바 스트림의 `sorted(Comparator.comparing(...))`, JS의 `sort((a, b) => a.score - b.score)`에 대응한다.

### 2-3. `map`에 함수를 두 개 이상의 리스트와 함께

```python
list(map(lambda a, b: a + b, [1, 2, 3], [10, 20, 30]))    # [11, 22, 33]
list(map(int, ["1", "2", "3"]))                           # [1, 2, 3] — 변환 함수를 그대로
```

`map`은 리스트를 여러 개 받으면 같은 자리 요소끼리 묶어 함수에 넘긴다(`zip`과 같은 짝짓기). 그리고 `int`·`str`·`len` 같은 **내장 함수도 그냥 함수 값**이라 람다로 감쌀 필요 없이 바로 넘긴다 — `map(lambda x: int(x), …)`는 `map(int, …)`로 줄어든다.

### 2-4. 함수를 돌려주는 함수 — 클로저로 콜백 만들기

```python
def multiplier(n):
    def inner(x):
        return x * n        # 바깥 함수의 n을 기억한다
    return inner

double = multiplier(2)
list(map(double, [1, 2, 3]))     # [2, 4, 6]
```

함수가 값이면 **돌려줄 수도** 있다. `multiplier(2)`가 돌려준 `inner`는 만들어질 때의 `n = 2`를 기억하고 있어서(클로저) 나중에 `double(3)`을 부르면 6이 나온다. 리액트에서 `onClick={() => handleDelete(id)}`처럼 "id를 품은 콜백"을 만들던 것과 같은 필요에서 나온 문법이다. 2-3의 `lambda`로 쓰면 `lambda x: x * 2`를 매번 적는 대신 `multiplier`로 찍어 내는 셈이다.

## 3. 더 나아가 알면 좋은 것

### 3-1. 일급 객체 — 함수를 값으로 다룬다는 말의 범위

파이썬에서 함수는 **일급 객체**다. 변수에 담고(`power = lambda …`), 인수로 넘기고(콜백), 반환값으로 돌려주고(클로저), 리스트·딕셔너리에 넣을 수 있다(`{"add": add, "sub": sub}[op](a, b)` 같은 디스패치 테이블). `type(print_hello)`를 찍으면 `<class 'function'>`이 나오는데, 정수·문자열처럼 함수도 하나의 자료형이라는 뜻이다. 자바는 오래 메소드가 값이 아니었다가 람다·함수형 인터페이스(`Function`, `Predicate`)로 이 성질을 뒤늦게 들여왔고, JS는 처음부터 함수가 값이었다. 세 언어의 "람다"가 비슷해 보이는 이유는 결국 같은 목표 — 함수를 값으로 넘기기 — 를 향하기 때문이다.

### 3-2. 고차 함수와 `functools.reduce`

```python
from functools import reduce
reduce(lambda acc, x: acc + x, [1, 2, 3, 4, 5])      # 15 — ((((1+2)+3)+4)+5)
```

함수를 받거나 돌려주는 함수를 **고차 함수**라 하고, `map`·`filter`·`sorted(key=)`·`reduce`가 대표다. `reduce`는 누적값과 요소를 받아 하나로 줄여 나가는 콜백을 받는다 — 연습문제 노트의 `sum_value += i` 누적 패턴을 함수로 추상화한 것이고, JS의 `arr.reduce((acc, x) => acc + x, 0)`, 자바 스트림의 `reduce(0, Integer::sum)`과 같다. 합·곱·최대처럼 자주 쓰는 건 `sum`·`max`가 이미 있어 `reduce`는 드물게 쓰지만, 삼총사 뒤의 네 번째로 알아 두면 세 언어 비교표가 완성된다.

### 3-3. 데코레이터 — 함수를 받아 함수를 돌려주는 관용구

```python
def log(func):
    def wrapper(*args, **kwargs):
        print("호출:", func.__name__)
        return func(*args, **kwargs)
    return wrapper

@log
def hello():
    print("안녕하세요")
```

2-4의 "함수를 돌려주는 함수"에 `@` 문법을 얹은 것이 데코레이터다. 재귀 노트의 `@lru_cache`가 그 예였고, 뒤에 플라스크·FastAPI의 `@app.route("/")`, 스프링 애노테이션과 비슷한 자리에 서게 된다. 안쪽 `wrapper`가 `*args, **kwargs`로 무엇이든 받아 그대로 넘기는 모양은 함수 노트의 가변 매개변수가 쓰이는 전형이다.

### 3-4. 지연 평가 — `map`이 이터레이터인 이유

`map(power, 리스트)`가 즉시 리스트를 만들지 않고 이터레이터를 돌려주는 것은 **필요할 때 하나씩 계산하기 위해서**다. 백만 개짜리 리스트에 `map`을 걸어도 메모리는 늘지 않고, `for`로 돌다가 중간에 `break`하면 나머지는 계산되지 않는다. 제너레이터(`yield`)·제너레이터 표현식(`(x * x for x in nums)`)이 같은 원리이고, 판다스 전에 큰 파일을 줄 단위로 처리할 때 이 성질에 기대게 된다. JS의 `map`이 즉시 새 배열을 만드는 것과의 차이를 "지연 vs 즉시"로 기억해 두면 된다.

### 3-5. 다음에 볼 키워드

- 일급 객체·고차 함수·콜백·클로저(`nonlocal`)
- `map`·`filter`·`reduce`와 리스트 컴프리헨션·제너레이터 표현식의 선택 기준
- `sorted`·`max`·`min`의 `key=`, `operator.itemgetter`·`attrgetter`
- 데코레이터(`@`)·`functools.wraps`·`lru_cache`
- 람다의 한계(식 하나·문장 불가)와 `def`로 돌아가야 할 때
- 이터레이터·지연 평가·`itertools`(`chain`·`islice`·`groupby`)
- 자바 함수형 인터페이스(`Function`·`Predicate`·`Consumer`)와 JS 콜백·화살표 함수 비교
- 타입 힌트로 함수 인수 적기 — `Callable[[int], int]`

## 실습 파일

- `KDT_2026/2026_Python/day03/C5-3.PY` (뒷부분) — 콜백·map·filter·람다. "함수 그 자체를 매개변수로 전달하여 전달받은 곳에서 호출" 정의와 `onClick(회원가입())` [X] / `onClick(회원가입)` [O] 대비, `def call_10_items(func): func()`에 `print_hello`를 괄호 없이 넘기기(괄호를 붙여 넘기는 경우와 비교), 자바 스트림·리액트 배열 메소드·파이썬의 `for`·`map(코드, 리스트)`·`filter(코드, 리스트)` 대응표와 "forEach 단순반복(return 없음) / map 반복+반환 / filter 반복+참이면 반환" 구분, `def power(item): return item * item`을 `map(power, list_a)`에 넘기고 `list()`로 감싸 `[1, 4, 9, 16, 25]` 출력(JS `list_a.map(power)` 대응), `def under_3(item): return item < 3`을 `filter(under_3, list_a)`에 넘겨 `[1, 2]` 출력(JS `list_a.filter(under_3)` 대응), `lambda 매개변수: 리턴값`과 `def`·자바 `() -> {}`·JS `() => {}` 대응, `power = lambda item: item * item`으로 변수에 담기와 `map(lambda item: item * item, list_a)` 인라인 람다, 리액트의 `const power = (item) => { return item * item }`·`list_a.map((item) => { return item * item })` 대응 주석, "람다는 JAVA 등과 비교하면서 공부해볼 것"

## 관련 노트

[[Python 정리본 인덱스]] · [[Python day03 튜플 선언과 구조분해·스왑]] · [[Python day03 함수 정의와 매개변수·가변 매개변수]] · [[Python day02 집계 함수와 reversed·enumerate 이터레이터]] · [[KDT_2026 학습 지도]]
