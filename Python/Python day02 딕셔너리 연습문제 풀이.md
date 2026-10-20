---
출처: Claude 분석
원본: KDT_2026/2026_Python/practice/p227-229.py
작성일: 2026-10-20
tags: [학습, python]
---

# Python day02 — 딕셔너리 연습문제 풀이

> 실습 파일: `practice/p227-229.py`
> 허브: [[Python 정리본 인덱스]] · 이전: [[Python day02 집계 함수와 reversed·enumerate 이터레이터]] · 다음: (아직 없음)

딕셔너리와 반복문·집계 함수를 훑고 나서 교재 227~229쪽 확인문제를 푼 파일이다. 리스트 연습문제(213~215쪽)가 "리스트를 돌면서 조건으로 가르기" 한 가지를 변주했다면, 이번 세 문제는 **딕셔너리를 만들고·읽고·채우는 세 동작**을 하나씩 짚는다. 1번은 키 대입으로 쌍을 추가하고 `del`로 지우는 가장 기본적인 쓰기, 2번은 리스트 안에 든 딕셔너리를 `for`로 꺼내 f-문자열로 찍는 읽기, 3번은 빈 딕셔너리를 카운터로 삼아 등장 횟수를 쌓는 집계다. 셋 다 딕셔너리 노트에서 문법으로 본 것인데, 문제 상황에 꺼내 쓰니 "없는 키"를 어떻게 다루느냐가 매번 핵심으로 돌아온다는 점이 보인다. 뒤에 하나 더 붙인 네 번째 문제는 값의 자료형이 문자열·정수·딕셔너리·리스트로 제각각인 `character` 딕셔너리를 `type()`으로 갈라 가며 전부 찍는 연습이라, 앞의 세 문제가 "키 하나"를 다뤘다면 이번에는 "값의 모양"을 보고 분기하는 쪽으로 한 걸음 나아간다.

## 1. 배운 내용

### 1-1. 쌍 하나 넣고 빼기 — 키 대입과 `del`

```python
dict_a = {}
dict_a['name'] = '구름'     # {} → {'name': '구름'}

del dict_a['name']          # {'name': '구름'} → {}
```

| 시작 상태 | 적용한 코드 | 결과 | 동작 |
| --- | --- | --- | --- |
| `{}` | `dict_a['name'] = '구름'` | `{'name': '구름'}` | 없는 키에 대입 → 쌍 **추가** |
| `{'name': '구름'}` | `del dict_a['name']` | `{}` | 키로 쌍 **삭제** |

딕셔너리에는 리스트의 `append` 같은 "추가 메소드"가 따로 없다. **없는 키에 값을 대입하면 그것이 곧 추가**이고, 있는 키에 대입하면 수정이다. 반대로 지울 때는 `del 딕셔너리[키]`로 쌍 전체를 뺀다 — 리스트에서 `del list_a[2]`로 인덱스 자리를 지우던 문법과 같은 모양인데, 괄호 안이 인덱스가 아니라 키라는 점만 다르다. 두 줄을 나란히 두고 보면 딕셔너리 쓰기의 최소 단위가 "대괄호 + 키"라는 것이 분명해진다. 읽기(`dict_a['name']`)와 추가(`dict_a['name'] = …`)가 같은 대괄호 문법을 쓰므로, 대입 기호 `=`가 붙었는지로 읽는 줄인지 쓰는 줄인지 구분하는 습관을 들여 두면 헷갈리지 않는다.

### 1-2. 리스트 안의 딕셔너리를 돌며 꺼내 찍기

```python
pets = [
    {"name": "구름", "age": 5},
    {"name": "초코", "age": 3},
    {"name": "아지", "age": 1},
    {"name": "호랑이", "age": 1},
]

print("# 우리 동네 애완동물들")
for pet in pets:
    print(f"{pet['name']} {pet['age']}살")
```

```
# 우리 동네 애완동물들
구름 5살
초코 3살
아지 1살
호랑이 1살
```

| 반복 | `pet`에 들어오는 것 | `pet['name']` | `pet['age']` |
| --- | --- | --- | --- |
| 1회 | `{"name": "구름", "age": 5}` | `구름` | `5` |
| 2회 | `{"name": "초코", "age": 3}` | `초코` | `3` |
| … | … | … | … |

바깥은 **리스트**이므로 `for pet in pets`를 돌리면 요소가 하나씩 나오고, 그 요소가 **딕셔너리**이므로 몸체에서 `pet['name']`처럼 키로 값을 읽는다. 딕셔너리 노트 2-2에서 본 "API 응답의 기본 모양"이 그대로 문제가 된 것이다 — 같은 구조의 레코드가 여러 개 있을 때 리스트가 순서를, 딕셔너리가 각 레코드의 이름표를 맡는다. 출력은 f-문자열 하나로 끝나는데, 중괄호 안에 `pet['name']`처럼 **대괄호 식을 그대로 넣을 수 있다**는 점을 기억해 둘 만하다. 이때 바깥 따옴표가 `"…"`이면 안쪽 키는 `'…'`로 종류를 바꿔야 문자열이 중간에 끊기지 않는다. 자바로 치면 `List<Map<String, Object>>`를 향상된 `for`로 돌면서 `pet.get("name")`을 꺼내는 일이고, JS로 치면 객체 배열을 `for…of`로 도는 일이다.

### 1-3. 빈 딕셔너리를 카운터로 — 등장 횟수 세기

```python
numbers = [1, 2, 6, 8, 4, 3, 2, 1, 9, 5, 4, 9, 7, 2, 1, 3, 5, 4, 8, 9, 7, 2, 3]
counter = {}

for number in numbers:
    if number in counter:
        counter[number] += 1     # 이미 본 숫자 → 기존 횟수에 1 더하기
    else:
        counter[number] = 1      # 처음 보는 숫자 → 1로 시작

print(counter)
# {1: 3, 2: 4, 6: 1, 8: 2, 4: 3, 3: 3, 9: 3, 5: 2, 7: 2}
```

| 단계 | `number` | `number in counter` | 실행된 줄 | `counter` |
| --- | --- | --- | --- | --- |
| 1 | 1 | 거짓 | `counter[1] = 1` | `{1: 1}` |
| 2 | 2 | 거짓 | `counter[2] = 1` | `{1: 1, 2: 1}` |
| … | … | … | … | … |
| 7 | 2 | **참** | `counter[2] += 1` | `{1: 1, 2: 2, 6: 1, 8: 1, 4: 1, 3: 1}` |
| 8 | 1 | **참** | `counter[1] += 1` | `{1: 2, 2: 2, …}` |

이 문제의 핵심은 **키가 숫자이고 값이 횟수**라는 역할 분담이다. `numbers`의 요소 자체를 키로 삼아 `counter[number]`에 접근하는데, 처음 보는 숫자는 아직 키가 없으니 바로 `+= 1`을 하면 `KeyError`가 난다. 그래서 `in`으로 **키가 이미 있는지 먼저 묻고**, 있으면 더하고 없으면 1로 시작한다. 딕셔너리 노트에서 `in`이 값이 아니라 키를 확인한다고 적어 둔 것이 여기서 그대로 쓰인다. 결과를 보면 키는 넣은 순서(처음 등장한 순서)대로 찍히고, 값은 각 숫자의 등장 횟수다. `counter[number] += 1`은 `counter[number] = counter[number] + 1`의 줄임이라, 읽고 더하고 다시 같은 키에 대입하는 세 동작이 한 줄에 들어 있다. 리스트였다면 "숫자 몇 번"을 찾으려고 매번 전체를 뒤져야 했을 일을, 딕셔너리는 키로 바로 찾아가 세기 때문에 요소가 많아져도 느려지지 않는다.

### 1-4. 값의 자료형이 제각각인 딕셔너리 훑기 — `type()`으로 가르기

```python
character = {
    "name": "기사",
    "level": 12,
    "items": {
        "sword": "불꽃의 검",
        "armor": "풀플레이트"
    },
    "skill": ["베기", "세게 베기", "아주 세게 베기"]
}

for key in character:
    if type(character[key]) is str or type(character[key]) is int:
        print(f"{key} : {character.get(key)}")
    elif type(character[key]) is list or type(character[key]) is dict:
        for value in character[key]:
            print(f"{key} : {value}")
```

```
name : 기사
level : 12
items : sword
items : armor
skill : 베기
skill : 세게 베기
skill : 아주 세게 베기
```

| `key` | `character[key]` | `type(...)` | 실행된 가지 | 찍히는 줄 |
| --- | --- | --- | --- | --- |
| `name` | `'기사'` | `str` | 위쪽 `if` | `name : 기사` 한 줄 |
| `level` | `12` | `int` | 위쪽 `if` | `level : 12` 한 줄 |
| `items` | `{'sword': …, 'armor': …}` | `dict` | 아래쪽 `elif` → 안쪽 `for` | `items : sword`, `items : armor` |
| `skill` | `['베기', …]` | `list` | 아래쪽 `elif` → 안쪽 `for` | `skill : 베기` 외 두 줄 |

바깥 `for key in character`는 딕셔너리 노트에서 본 대로 **키**를 하나씩 넘긴다. 문제는 키마다 값의 모양이 다르다는 점이다 — `name`·`level`은 값이 하나라 바로 찍으면 되지만, `items`·`skill`은 값 자체가 또 하나의 묶음이라 한 번 더 돌아야 요소가 나온다. 그래서 `type(character[key]) is str`처럼 **값의 자료형을 먼저 묻고** 가지를 나눈다. `type()`은 day01 시작 노트에서 자료형을 확인하는 용도로 봤는데, 여기서는 그 결과를 `is str`·`is int`로 비교해 조건문의 재료로 쓴다. `is`는 "같은 객체인가"를 묻는 비교라 자료형 객체끼리 견줄 때 자연스럽고, `or`로 두 자료형을 묶어 "값이 하나인 경우"와 "값이 묶음인 경우"의 두 갈래로 정리한 셈이다.

값이 묶음일 때 안쪽 `for value in character[key]`를 돌리면 리스트에서는 요소가, 딕셔너리에서는 **키**가 나온다. 출력에서 `items : sword`·`items : armor`처럼 안쪽 딕셔너리의 키가 찍히는 이유가 그것이다 — 딕셔너리를 `for`에 그대로 넣으면 값이 아니라 키를 넘긴다는 규칙이 중첩된 안쪽에서도 똑같이 적용된다. 안쪽 값(`불꽃의 검`)까지 보려면 `character[key][value]`로 한 번 더 대괄호를 쓰거나 2-4처럼 `items()`로 풀어 받아야 한다. 위쪽 가지에서 `character.get(key)`를 쓴 것도 눈여겨볼 만한데, 같은 줄의 `character[key]`와 결과는 같고 없는 키를 만났을 때 `None`을 돌려준다는 점만 다르다 — 이미 `for`가 넘겨준 키라 여기서는 둘 중 무엇을 써도 차이가 없다.

## 2. 추가로 알면 좋은 활용법

### 2-1. 횟수 세기를 짧게 — `get`·`setdefault`·`Counter`

```python
# 방법1: get에 기본값 0
for number in numbers:
    counter[number] = counter.get(number, 0) + 1

# 방법2: setdefault로 없을 때만 0을 넣고 바로 더하기
for number in numbers:
    counter.setdefault(number, 0)
    counter[number] += 1

# 방법3: 표준 라이브러리
from collections import Counter
counter = Counter(numbers)
print(counter.most_common(3))   # [(2, 4), (1, 3), (4, 3)]
```

| 방법 | 줄 수 | 특징 |
| --- | --- | --- |
| `if … in … else` | 4줄 | 동작이 전부 보여서 처음 배울 때 가장 명확하다 |
| `get(키, 0) + 1` | 1줄 | "없으면 0"을 `get`이 대신 판단한다 |
| `setdefault` | 2줄 | 없을 때만 초기값을 넣고 이후는 그대로 |
| `Counter` | 1줄 | 세기 전용 딕셔너리. `most_common`으로 상위 N개 정렬까지 |

1-3의 `if`·`else` 네 줄은 결국 "없으면 0에서 시작"을 손으로 쓴 것이라, 딕셔너리 노트 2-4에서 본 `get(키, 0)`을 쓰면 한 줄이 된다. 처음에는 `if` 버전으로 동작을 눈에 익히고, 손에 붙으면 `get` 버전으로 줄이는 순서가 자연스럽다. `Counter`는 딕셔너리를 상속한 클래스라 `counter[2]`처럼 똑같이 읽을 수 있고, 없는 키를 읽어도 `KeyError` 대신 0을 돌려준다.

### 2-2. 2번 문제를 조금 더 — `get`으로 빠진 키 막기와 `items()`로 풀어 받기

```python
for pet in pets:
    print(f"{pet.get('name', '이름없음')} {pet.get('age', '?')}살")

for pet in pets:
    for key, value in pet.items():
        print(key, value, end='  ')
    print()
```

레코드가 여러 개일 때 어떤 레코드에는 키가 빠져 있을 수 있다(외부 API 응답이 특히 그렇다). 대괄호로 읽으면 그 레코드에서 `KeyError`로 멈추므로, 키가 꼭 있다고 장담할 수 없으면 `get`에 대체값을 주는 편이 안전하다. 반대로 어떤 키가 있는지 모르는 채로 전부 보고 싶으면 `items()`로 `(키, 값)` 쌍을 풀어 받는다 — 집계 함수 노트에서 `enumerate`가 `(인덱스, 값)`을 넘기던 것과 같은 풀어 받기다.

### 2-3. 결과를 보기 좋게 — 키 순서로 정렬해 찍기

```python
for number in sorted(counter):
    print(f"{number}: {counter[number]}번")

for number, cnt in sorted(counter.items(), key=lambda kv: kv[1], reverse=True):
    print(f"{number}: {cnt}번")
```

1-3의 `counter`는 처음 등장한 순서로 키가 쌓이기 때문에 `print(counter)`를 찍으면 1, 2, 6, 8, … 순으로 나온다. 숫자 순서로 보고 싶으면 `sorted(counter)`가 키만 정렬해 돌려주고, 많이 나온 순으로 보고 싶으면 `items()`를 값 기준(`key=lambda kv: kv[1]`)으로 정렬한다. 딕셔너리 자체를 정렬하는 것이 아니라 **정렬된 키 목록을 따로 만들어 그 순서로 읽는다**는 점이 요령이다.

### 2-4. `isinstance`로 가르고 `items()`로 안쪽 값까지 꺼내기

```python
for key, value in character.items():
    if isinstance(value, (str, int)):
        print(f"{key} : {value}")
    elif isinstance(value, dict):
        for inner_key, inner_value in value.items():
            print(f"{key}.{inner_key} : {inner_value}")   # items.sword : 불꽃의 검
    elif isinstance(value, list):
        for item in value:
            print(f"{key} : {item}")
```

| 1-4의 방식 | 바꾼 방식 | 달라지는 점 |
| --- | --- | --- |
| `for key in character` + `character[key]` | `for key, value in character.items()` | 키와 값을 한 번에 풀어 받아 대괄호 반복이 사라진다 |
| `type(v) is str or type(v) is int` | `isinstance(v, (str, int))` | 자료형 여러 개를 튜플로 한 번에 묻는다 |
| 안쪽 딕셔너리를 `for value in …`로 | `value.items()`로 | 안쪽 키뿐 아니라 **값**(`불꽃의 검`)까지 나온다 |

`type(x) is str`은 정확히 그 자료형일 때만 참이고, `isinstance(x, str)`은 그 자료형을 상속한 것까지 참으로 본다. 2-1에서 본 `Counter`가 딕셔너리를 상속한 클래스라 `type(counter) is dict`는 거짓이지만 `isinstance(counter, dict)`는 참이다 — "딕셔너리처럼 다룰 수 있는가"를 묻는 상황이라면 `isinstance` 쪽이 뜻에 맞는다. 둘째 인자에 튜플을 주면 `or`로 이어 쓰던 비교가 한 번으로 줄어든다. 안쪽 딕셔너리는 `items()`로 풀어 받아 `items.sword`처럼 바깥 키와 안쪽 키를 점으로 이어 찍으면 어느 경로의 값인지 한눈에 들어온다. 리스트와 딕셔너리의 가지를 따로 두는 이유도 여기 있다 — 리스트는 요소를, 딕셔너리는 `(키, 값)` 쌍을 꺼내야 하므로 안쪽 `for`의 모양이 서로 다르다.

## 3. 더 나아가 알면 좋은 것

### 3-1. 딕셔너리로 세는 것이 빠른 이유 — 해시

1-3에서 `number in counter`와 `counter[number]`는 리스트가 길어져도 거의 같은 속도로 끝난다. 딕셔너리는 키를 해시 함수로 숫자로 바꿔 어느 칸에 둘지 정하므로, 전체를 훑지 않고 바로 그 칸으로 간다(평균 O(1)). 리스트의 `in`은 앞에서부터 하나씩 비교하므로 요소 수에 비례해 느려진다(O(n)). 리스트 연습문제에서 "나머지로 바구니에 나눠 담기"를 했던 것이 해시 테이블의 축소판이었고, 딕셔너리는 그 바구니 배정을 내부에서 자동으로 해 주는 셈이다. 그래서 키로 쓸 수 있는 것은 해시가 가능한 **불변 자료형**(숫자·문자열·튜플)뿐이고, 리스트는 키가 될 수 없다.

### 3-2. 리스트 안의 딕셔너리에서 표로 — 판다스의 자리

2번 문제의 `pets`처럼 "같은 키를 가진 딕셔너리의 리스트"는 곧 표(행·열) 구조다. 판다스의 `pd.DataFrame(pets)`는 이 리스트를 그대로 받아 `name`·`age` 열을 가진 표로 만들고, `df['age'].value_counts()`는 3번 문제의 횟수 세기를 한 줄로 한다. JSON 파일을 읽으면 대부분 이 모양으로 들어오므로, 지금 손으로 `for`를 돌리며 익혀 두는 구조가 뒤에서 라이브러리 한 줄로 바뀌는 자리다.

### 3-3. 깊이를 모르는 중첩 구조 — 재귀로 내려가기

```python
def show(data, prefix=""):
    if isinstance(data, dict):
        for key, value in data.items():
            show(value, f"{prefix}{key}.")
    elif isinstance(data, list):
        for item in data:
            show(item, prefix)
    else:
        print(f"{prefix[:-1]} : {data}")

show(character)
# name : 기사 / level : 12 / items.sword : 불꽃의 검 / items.armor : 풀플레이트 / skill : 베기 …
```

1-4와 2-4는 중첩이 **두 단계**라는 것을 알고 있어서 안쪽 `for`를 손으로 한 번 더 썼다. 그런데 `items` 안에 다시 딕셔너리가 들어 있거나, 리스트 요소가 딕셔너리인 구조(2번 문제의 `pets`가 그렇다)에서는 단계마다 `for`를 덧쓰는 방식이 금방 한계에 닿는다. 이럴 때는 "딕셔너리면 쌍마다, 리스트면 요소마다 **자기 자신을 다시 부르고**, 그 밖의 값이면 찍는다"는 규칙 하나로 깊이에 상관없이 내려가는 함수를 만든다. 이것이 재귀이고, JSON 파일을 `json.loads`로 읽어 들인 결과가 정확히 이런 모양(딕셔너리와 리스트가 번갈아 중첩)이라 API 응답을 탐색할 때 바로 쓰이는 틀이다. 함수 정의(`def`)와 기본 인자(`prefix=""`)는 아직 수업에서 다루지 않았으므로, 지금은 "분기 규칙을 함수로 묶으면 깊이가 사라진다"는 그림만 담아 두면 된다.

### 3-4. 다음에 볼 키워드

- `collections.Counter`·`defaultdict(int)` — 횟수 세기·그룹 묶기 전용 딕셔너리
- 딕셔너리 컴프리헨션 `{k: v for …}`과 `zip`으로 두 리스트를 딕셔너리로 합치기
- `sorted(d.items(), key=…)`·`max(d, key=d.get)` — 값 기준으로 키 고르기
- 중첩 딕셔너리(`d['a']['b']`)와 `json.loads`·`json.dumps`
- `isinstance(x, (str, int))` vs `type(x) is str` — 상속까지 보는 자료형 검사
- 재귀 함수로 깊이를 모르는 딕셔너리·리스트 중첩 훑기(`json` 탐색)
- 해시 가능(hashable) 자료형과 `set` — 딕셔너리의 키만 모아 둔 자료형
- 함수 정의(`def`)로 세기·출력을 묶어 재사용하는 자리

## 실습 파일

- `KDT_2026/2026_Python/practice/p227-229.py` — 교재 227~229쪽 딕셔너리 확인문제 풀이. 1번 빈 딕셔너리에 키 대입으로 쌍 추가·`del`로 삭제, 2번 리스트 안 딕셔너리(`pets`)를 `for`로 돌며 `pet['name']`·`pet['age']`를 f-문자열로 출력, 3번 빈 `counter`에 `if number in counter`로 키 유무를 가려 `+= 1` 또는 `= 1`로 등장 횟수 쌓기, 4번 값이 문자열·정수·딕셔너리·리스트로 섞인 `character` 딕셔너리를 `for key in character`로 돌며 `type(character[key]) is str`·`is int`·`is list`·`is dict`로 가지를 나눠 하나짜리 값은 바로, 묶음 값은 안쪽 `for`로 한 번 더 돌며 `f"{key} : {value}"`로 출력

## 관련 노트

[[Python 정리본 인덱스]] · [[Python day02 집계 함수와 reversed·enumerate 이터레이터]] · [[Python day02 딕셔너리 선언과 키로 값 다루기]] · [[KDT_2026 학습 지도]]
