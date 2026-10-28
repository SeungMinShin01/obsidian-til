---
출처: Claude 분석
원본: KDT_2026/2026_Python/day08/p-01.py
작성일: 2026-10-28
tags: [학습, python]
---

# Python day08 — 판다스 데이터프레임 생성과 인덱싱·필터링

> 실습 파일: `day08/p-01.py`
> 허브: [[Python 정리본 인덱스]] · 이전: [[Python day07 넘파이로 따릉이 대여소 재배치 분석 실습]] · 다음: (아직 없음)

넘파이로 두 번의 분석 실습까지 마치고 드디어 **판다스**다. 넘파이 배열은 숫자가 한 가지 자료형으로만 담기고 열에 이름도 없어서, 따릉이 실습에서는 대여소 번호 표와 이름 표를 따로 들고 다녀야 했다. 판다스의 `DataFrame`은 그 불편을 그대로 해결한다 — **열마다 이름과 자료형이 따로 있고, 행에도 이름(인덱스)이 붙은 표**다. 이번 시간은 데이터프레임을 리스트·딕셔너리·넘파이 배열 세 가지 재료로 만들어 보고, `shape`·`columns`·`info()` 같은 속성으로 모양을 확인한 뒤, `iloc`/`loc`로 칸을 집고 열을 추가·수정하고 조건으로 행을 거르는 기본 동작을 한 바퀴 돌았다. 넘파이에서 익힌 인덱싱·슬라이싱·불리언 필터가 거의 그대로 이어진다.

## 1. 배운 내용

### 1-1. 데이터프레임 만들기 ① — 2차원 리스트

```python
import pandas as pd

data_list = [
    ['ant', 25, 'seoul'],
    ['bee', 30, 'busan'],
    ['cat', 35, 'incheon']   # 2차원 리스트
]
x = pd.DataFrame(data_list)
print(x)      # 행과 열 => 표 형식
```

```
     0   1        2
0  ant  25    seoul
1  bee  30    busan
2  cat  35  incheon
```

`import pandas as pd`는 `np`와 같은 별칭 관례다. 리스트 안의 리스트를 `pd.DataFrame()`에 넣으면 **바깥 리스트 하나가 행 하나**가 되고, 안쪽 요소가 열로 펼쳐진다. 열 이름을 주지 않으면 `0, 1, 2`가 자동으로 붙고, 행 번호(인덱스)도 `0, 1, 2`가 자동으로 붙는다. day02에서 2차원 리스트를 `[행][열]`로 읽으며 "판다스로 이어지는 자리"라고 적어 둔 그 자리다.

```python
x = pd.DataFrame(data_list, columns=['name', 'age', 'city'])
print(x)
```

```
  name  age     city
0  ant   25    seoul
1  bee   30    busan
2  cat   35  incheon
```

`columns=` 인자로 열 이름 리스트를 넘기면 숫자 대신 이름이 붙는다. 열 개수와 이름 개수가 맞아야 한다.

### 1-2. 데이터프레임 만들기 ② — 딕셔너리

```python
data_dict = {
  'name': ['ant', 'bee', 'cat'],
  'age':  [25, 30, 35],
  'city': ['seoul', 'busan', 'incheon'] }   # 딕셔너리

df = pd.DataFrame(data_dict)
print(df)
```

결과는 ①과 같은 표다. 차이는 재료의 방향이다.

| 재료 | 바깥 묶음 하나 = | 열 이름 |
| --- | --- | --- |
| 2차원 리스트 | **행** 하나 (`['ant', 25, 'seoul']`) | 따로 `columns=`로 지정 |
| 딕셔너리 | **열** 하나 (`'age': [25, 30, 35]`) | 키가 그대로 열 이름 |

딕셔너리 방식은 **키 = 열 이름, 값 리스트 = 그 열의 값들**이라 열 이름을 따로 줄 필요가 없다. 모든 값 리스트의 길이가 같아야 한다. 실제로는 DB에서 꺼낸 레코드나 API 응답처럼 "행 단위"로 들어오는 자료는 리스트 방식이, 열별로 모아 둔 자료는 딕셔너리 방식이 자연스럽다.

### 1-3. 열 하나 꺼내기 — `Series`

```python
ages = df['age']
print(ages)
print(type(ages))          # <class 'pandas.core.series.Series'>
print(type(ages.values))   # <class 'numpy.ndarray'>
```

```
0    25
1    30
2    35
Name: age, dtype: int64
```

`df['열이름']`으로 열 하나를 꺼내면 `DataFrame`이 아니라 **`Series`**가 나온다. 판다스의 두 자료형을 정리하면 이렇다.

| 자료형 | 차원 | 무엇인가 |
| --- | --- | --- |
| `Series` | 1차원 | 인덱스가 붙은 값 한 줄 — 열 하나, 또는 행 하나 |
| `DataFrame` | 2차원 | `Series`를 열로 여러 개 묶은 표 |

`ages.values`를 찍으면 `numpy.ndarray`가 나오는데, 이게 핵심이다. **판다스는 넘파이 위에 얹힌 포장**이라서 `Series` 안의 실제 값은 넘파이 배열이고, 거기에 인덱스(행 이름)와 열 이름이 붙은 것뿐이다. 그래서 넘파이에서 쓴 `mean`·`max`·불리언 비교가 `Series`에도 그대로 통한다.

### 1-4. 데이터프레임 만들기 ③ — 넘파이 배열과 `index=`

```python
import numpy as np
data_np = np.array(data_list)   # 넘파이 자료
df = pd.DataFrame(data_np, columns=['name', 'age', 'city'], index=['A', 'B', 'C'])
print(df)
```

```
  name age     city
A  ant  25    seoul
B  bee  30    busan
C  cat  35  incheon
```

넘파이 2차원 배열도 그대로 재료가 된다. 이번에는 `index=['A', 'B', 'C']`로 **행 이름**까지 직접 붙였다. 지금까지 자동으로 붙던 `0, 1, 2`가 인덱스였고, 이렇게 바꿔 달 수 있다는 뜻이다. 이 `A`·`B`·`C`가 바로 뒤 `loc`에서 행을 집는 열쇠가 된다.

한 가지 눈여겨볼 점이 있다. `data_list`에는 문자열과 정수가 섞여 있는데, 넘파이 배열은 자료형이 하나라서 `np.array(data_list)`를 만들 때 **전부 문자열**(`'25'`)로 통일된다. 그래서 이 방식으로 만든 데이터프레임의 `age` 열은 숫자가 아니라 문자열이다. 리스트·딕셔너리로 직접 만들면 열마다 자료형이 따로 잡히므로(`age`는 `int64`) 섞인 자료는 리스트나 딕셔너리로 바로 넣는 편이 안전하고, 넘파이를 거쳤다면 `info()`로 자료형을 확인하는 습관이 필요하다.

### 1-5. 주요 속성 — 표의 모양 확인

```python
print(df.shape)     # (3, 3)      행/열 크기
print(df.columns)   # Index(['name', 'age', 'city'], dtype='object')   컬럼 목록
print(df.index)     # Index(['A', 'B', 'C'], dtype='object')           인덱스 목록
print(df.values)    # 값만 2차원 배열로 추출
print(df.head(2))   # 상위 n개만 반환
print(df.tail(2))   # 하위 n개만 반환
df.info()           # 컬럼 이름, 결측치, 타입 확인
```

| 속성·메소드 | 돌려주는 것 | 쓰는 때 |
| --- | --- | --- |
| `shape` | `(행 수, 열 수)` 튜플 | 넘파이 `shape`와 같다. 자료를 읽은 직후 크기 확인 |
| `columns` | 열 이름 목록 | 열 이름 오타 확인, 반복문으로 열 순회 |
| `index` | 행 이름 목록 | 행 이름이 뭔지, 기본 번호인지 확인 |
| `values` | 값만 담은 `numpy.ndarray` | 넘파이 함수에 넘길 때 |
| `head(n)` / `tail(n)` | 앞 n행 / 뒤 n행 | 수천 행짜리 자료를 전부 찍지 않고 맛보기 |
| `info()` | 열마다 non-null 개수와 dtype | **결측치**(빈 칸)와 자료형 점검 — 분석 시작 전 필수 |

`shape`·`columns`·`index`·`values`는 괄호가 없는 **속성**이고, `head()`·`tail()`·`info()`는 괄호가 있는 **메소드**다. `info()`는 값을 돌려주는 대신 화면에 바로 출력하는 메소드라 `print()`로 감싸지 않는다. 지난 노트에서 "판다스는 메소드형"이라 적었는데, `df.shape`처럼 속성으로 읽는 것도 섞여 있으니 둘을 구분해 두면 괄호 유무로 헤매지 않는다.

`info()`가 보여 주는 `Non-Null Count`가 행 수보다 작으면 그 열에 결측치가 있다는 뜻이다. 따릉이 실습에서 넘파이 `genfromtxt`로 읽을 때 빈 칸이 `nan`으로 들어오던 것을 떠올리면, 판다스는 그걸 열 단위로 세어서 미리 알려 주는 셈이다.

### 1-6. 인덱싱 — `iloc`(번호)와 `loc`(이름)

```python
print(df.iloc[1])          # 1행 (번호로)
print(df.iloc[1, 2])       # busan — 1행 2열
print(df.loc['B'])         # B행 (이름으로)
print(df.loc['B', 'city']) # busan — B행 city열
```

판다스에는 칸을 집는 창구가 둘이다.

| | `iloc` | `loc` |
| --- | --- | --- |
| 이름 | **i**nteger **loc**ation | **loc**ation(label) |
| 받는 것 | 정수 **번호** (0부터) | 행·열 **이름**(라벨) |
| `df.iloc[1, 2]` | 1행 2열 → `busan` | — |
| `df.loc['B', 'city']` | — | B행 city열 → `busan` |
| 넘파이 대응 | `arr[1, 2]`와 같다 | 넘파이에 없는 기능 |

행 하나만 집으면(`df.iloc[1]`·`df.loc['B']`) 그 행이 `Series`로 나오고 — 열 이름이 인덱스 자리에 온다 — 행과 열을 쉼표로 함께 집으면 값 하나가 나온다. 넘파이 `x[1, 2]`에서 쉼표 하나로 행·열을 동시에 지정하던 규칙이 `iloc`에 그대로 있다.

인덱스가 기본 번호 `0, 1, 2`일 때는 `iloc[1]`과 `loc[1]`이 같은 행을 가리켜 구분이 흐려지지만, 지금처럼 `A`·`B`·`C`를 붙여 두면 `loc[1]`은 "1이라는 이름의 행"을 찾다가 `KeyError`가 난다. **번호면 `iloc`, 이름이면 `loc`**로 처음부터 갈라 쓰는 편이 안전하다.

### 1-7. 슬라이싱 — 끝 포함 여부가 다르다

```python
print(df.iloc[0:2, 0:1])            # 0~1행, 0열      → ant, bee의 name
print(df.loc['A':'C', 'name':'age']) # A~C행, name~age열 (양 끝 포함)
```

```
  name
A  ant
B  bee
```
```
  name age
A  ant  25
B  bee  30
C  cat  35
```

| | `iloc[0:2]` | `loc['A':'C']` |
| --- | --- | --- |
| 끝 | **미포함** — 0, 1행 (2행 제외) | **포함** — A, B, C행 전부 |
| 이유 | 파이썬 리스트·넘파이 슬라이싱 규칙 그대로 | 이름에는 "하나 뒤"라는 개념이 없어서 끝까지 |

여기가 헷갈리기 쉬운 지점이다. `iloc`는 지금까지 배운 `[시작:끝]` 끝 미포함 규칙을 따르고, `loc`는 **양 끝을 다 포함**한다. `'name':'age'`도 `name`·`age` 두 열이 다 나온다. 결과는 행·열 슬라이스 둘 다 범위라 `DataFrame`으로 나온다(`iloc[0:2, 0:1]`은 열이 하나지만 범위로 집었으므로 여전히 표 모양이다 — 넘파이에서 정수로 고르면 축이 사라지고 슬라이스로 고르면 남는 규칙과 같다).

### 1-8. 열 추가와 값 수정

```python
df['score'] = [100, 80, 95]   # 열 추가: df[새 열] = 값들
df['age']   = [31, 52, 40]    # 열 전체 수정: 있는 열 이름에 대입
df.iloc[0, 0] = 'apple'       # 칸 하나 수정: ant → apple
df.loc[['A', 'B'], 'score'] = [50, 60]   # 여러 칸 수정: A·B행의 score
print(df)
```

```
    name age     city  score
A  apple  31    seoul     50
B    bee  52    busan     60
C    cat  40  incheon     95
```

| 동작 | 문법 | 닮은 것 |
| --- | --- | --- |
| 열 추가 | `df['새이름'] = [값, …]` | 딕셔너리에 없는 키 대입 → 추가 |
| 열 수정 | `df['있는이름'] = [값, …]` | 딕셔너리에 있는 키 대입 → 수정 |
| 칸 하나 수정 | `df.iloc[행, 열] = 값` / `df.loc[행이름, 열이름] = 값` | 넘파이 `x[1, 2] = 값` |
| 여러 칸 수정 | `df.loc[[행들], 열] = [값들]` | 넘파이 팬시 인덱싱 대입 |

day02 딕셔너리에서 "없는 키에 대입하면 추가, 있는 키에 대입하면 수정"이라고 정리한 규칙이 열 단위로 그대로 적용된다 — 데이터프레임을 "열 이름을 키로 갖는 딕셔너리"로 보면 자연스럽다. 추가하는 값 리스트의 길이는 행 수와 같아야 하고, 스칼라 하나(`df['score'] = 0`)를 넣으면 넘파이 브로드캐스팅처럼 전 행에 같은 값이 들어간다. `loc[['A', 'B'], 'score']`처럼 행 자리에 **리스트**를 넣으면 여러 행을 한 번에 집는다. 넘파이 `x[ [0, 2] ]` 팬시 인덱싱과 같은 모양이다.

### 1-9. 필터링 — 조건으로 행 고르기

```python
print(df['score'] > 70)
```
```
A    False
B    False
C     True
Name: score, dtype: bool
```
```python
print(df[df['score'] > 70])             # 조건이 True인 행만
```
```
  name age     city  score
C  cat  40  incheon     95
```

넘파이 불리언 인덱싱과 똑같은 두 단계다. `df['score'] > 70`은 행마다 참·거짓이 적힌 **`bool` `Series`**를 만들고, 그걸 `df[...]` 안에 다시 넣으면 `True`인 행만 남는다. 다른 점은 결과에 인덱스 `C`가 그대로 따라온다는 것 — 넘파이는 걸러낸 뒤 원래 몇 번째였는지 잊지만 판다스는 행 이름을 들고 다닌다. 따릉이 실습에서 `argmax` 위치를 이름표에 꽂던 수고가 여기서는 필요 없다.

조건을 둘 이상 겹칠 때는 넘파이와 같은 규칙이다.

```python
cont = df['age'] >= 40
print(df[(df['score'] > 70) & cont])    # score 70 초과 이면서 age 40 이상
print(df[(df['score'] > 70) | cont])    # score 70 초과 이거나 age 40 이상
```

`and`·`or`가 아니라 `&`·`|`를 쓰고, **비교식마다 소괄호**를 두른다. `&`·`|`가 `>`·`>=`보다 먼저 계산되기 때문에 괄호가 없으면 `70 & cont`가 먼저 묶여 의도와 다른 결과가 나오거나 오류가 난다. 지난 넘파이 노트에서 `ambiguous` 오류와 함께 정리한 내용 그대로다. 조건을 `cont`처럼 변수에 담아 두면 식이 짧아지고 재사용도 된다.

### 1-10. 수업 메모 — 매크로에서 RPA로

파일 중간에 "매크로(C 프로그램) → RPA(사무 업무/파이썬)"라는 한 줄이 있다. 옛날에 C로 짜던 매크로 자동화가 지금은 파이썬 기반 RPA로 넘어왔고, 그 RPA가 엑셀·CSV 같은 표 자료를 다룰 때 쓰는 도구가 바로 판다스라는 맥락이다. 넘파이 → 판다스로 이어지는 이 커리큘럼이 뒤의 RPA 과정과 맞닿는 지점이기도 하다.

## 2. 추가로 알면 좋은 활용법

### 2-1. 열 여러 개 고르기 — 이중 대괄호

```python
df['name']             # Series — 열 하나
df[ ['name', 'city'] ]   # DataFrame — 열 여러 개 (리스트를 넣는다)
df[ ['name'] ]           # DataFrame — 열 하나지만 표 모양 유지
```

대괄호 안에 리스트를 넣으면 열을 여러 개 뽑고, 결과는 항상 `DataFrame`이다. 열 하나를 `Series`가 아니라 표 모양으로 받고 싶을 때도 `df[ ['name'] ]`처럼 대괄호 안에 리스트를 넣는다. `df.name`처럼 점으로도 열을 읽을 수 있지만, 열 이름에 공백이 있거나 `shape`·`count`처럼 속성·메소드와 겹치면 안 되므로 대괄호 쪽이 안전하다.

### 2-2. CSV 읽기 — `read_csv`

```python
df = pd.read_csv('data.csv', encoding='utf-8-sig')
df.head()
df.info()
df.describe()   # 숫자 열의 개수·평균·표준편차·최소·사분위·최대 한 번에
```

이번 시간은 손으로 만든 세 줄짜리 표지만, 실제 시작점은 거의 `pd.read_csv`다. 따릉이 실습에서 `np.genfromtxt(delimiter=',', skip_header=1, encoding='utf-8-sig')`에 `dtype=str`을 따로 줘서 이름표를 별도로 읽어야 했던 일이, `read_csv` 한 줄이면 첫 줄을 열 이름으로 쓰고 열마다 자료형을 알아서 잡아 준다. 읽은 직후 `head()`·`info()`·`describe()` 세 개를 습관처럼 찍는 것이 분석의 첫 동작이다. `describe()`는 지난 노트의 `min`·`max`·`mean`·`std`·`median`(50%)을 열마다 한 표로 보여 준다.

### 2-3. 인덱스 다루기 — `set_index`·`reset_index`

```python
df2 = df.set_index('name')     # name 열을 인덱스로 올리기
df2.loc['bee']                 # 이제 이름으로 행을 집는다
df2.reset_index()              # 인덱스를 다시 보통 열로 내리고 0,1,2 번호로
```

`index=['A', 'B', 'C']`처럼 만들 때 주는 대신, 있는 열을 인덱스로 올리는 것이 더 흔하다. 대여소 번호나 고객 ID를 인덱스로 올려 두면 `loc[ID]`로 바로 행을 찾을 수 있다. 판다스의 대부분 메소드는 **원본을 바꾸지 않고 새 데이터프레임을 돌려주므로** 결과를 변수에 받아야 한다(`inplace=True` 옵션도 있지만 새 변수에 받는 쪽이 추적하기 쉽다).

### 2-4. 정렬·행 삭제·조건 수정

```python
df.sort_values('score', ascending=False)        # score 내림차순 — 새 표 반환
df.sort_values(['city', 'age'])                 # 여러 기준
df.drop(columns=['score'])                      # 열 삭제
df.drop(index=['A'])                            # 행 삭제
df.loc[df['age'] >= 40, 'score'] = 0            # 조건에 맞는 행의 특정 열만 수정
```

`np.argsort`로 순번을 얻어 다른 배열에 다시 끼우던 정렬이 `sort_values('열')` 한 줄이 된다. 행이 통째로 따라 움직이고 인덱스도 함께 간다. 마지막 줄은 `loc[조건, 열] = 값` 꼴로, 넘파이의 `scores[scores < 60] = 60` 조건 대입에 열 지정이 더해진 모양이다. 필터링한 결과에 바로 대입하는 `df[df['age'] >= 40]['score'] = 0`은 복사본에 쓰게 되어 원본이 안 바뀌는 경우가 있으니(`SettingWithCopyWarning`), 수정은 `loc` 한 번으로 하는 편이 안전하다.

### 2-5. 조건 필터의 다른 표현

```python
df[df['city'].isin(['seoul', 'busan'])]      # 값이 목록 안에 있는 행
df[df['age'].between(30, 50)]                # 30 ≤ age ≤ 50
df.query('score > 70 and age >= 40')         # 문자열로 조건 쓰기 — and/or 사용 가능
df[~(df['score'] > 70)]                      # 부정
```

`isin`은 `city == 'seoul' | city == 'busan'`을 줄인 것이고, `query`는 조건을 문자열로 적어 `&`·괄호 대신 `and`·`or`를 쓸 수 있다. 조건이 길어질 때 가독성이 좋다. `~`는 넘파이와 같은 부정 연산자다.

## 3. 더 나아가 알면 좋은 것

### 3-1. `groupby` — 마스크 반복을 한 줄로

```python
df.groupby('city')['score'].mean()
df.groupby('city').agg(합계=('score', 'sum'), 평균=('age', 'mean'), 개수=('name', 'count'))
```

따릉이 실습에서 `np.unique`로 대여소 번호를 뽑고 `for i in ids`·`m = data[:, 0] == i`·`np.sum(data[m, 2])`로 돌리던 **마스크 반복 group by**가 `groupby('열').sum()` 한 줄이다. 결과는 그룹 값이 인덱스로 올라간 `Series`/`DataFrame`이라 이름표를 따로 맞출 필요도 없다. `agg`로 열마다 다른 집계를 한 번에 걸 수 있고, SQL의 `GROUP BY`와 1:1로 대응하는 개념이다.

### 3-2. `merge`·`concat` — 표 두 장 붙이기

```python
pd.concat([df_a, df_b])                          # 세로로 이어 붙이기 (np.vstack)
pd.merge(station, names, on='대여소번호')        # 키 기준 결합 (SQL JOIN)
```

`concat`은 `np.vstack`에, `merge`는 SQL `JOIN`에 대응한다. 따릉이 실습에서 대여소 번호 표와 이름 표의 행 순서가 같다고 확인해 가며 나란히 썼던 작업이, `merge(on='대여소번호')`로 하면 순서가 달라도 키로 맞춰 붙는다. `how='left'/'inner'/'outer'`로 결합 방식을 고른다.

### 3-3. 결측치와 자료형 — `isna`·`fillna`·`astype`

```python
df.isna().sum()                      # 열마다 결측치 개수 (info()의 숫자판)
df.dropna()                          # 결측 행 제거
df.fillna({'score': 0})              # 열별 채우기
df['age'] = df['age'].astype(int)    # 문자열로 들어온 숫자를 정수로
```

`info()`로 결측치를 확인한 다음 단계가 이 셋이다. 1-4에서 본 "넘파이를 거치면 숫자가 문자열이 된다" 상황도 `astype(int)`로 되돌린다. `pd.to_numeric(errors='coerce')`는 숫자로 못 바꾸는 값을 `NaN`으로 처리해 주어 지저분한 CSV를 읽을 때 유용하다.

### 3-4. 축과 메소드형 — 넘파이와 같은 규칙, 다른 겉모습

| 넘파이 | 판다스 |
| --- | --- |
| `np.mean(arr, axis=0)` | `df.mean()` — 기본이 열마다(`axis=0`) |
| `np.mean(arr, axis=1)` | `df.mean(axis=1)` — 행마다 |
| `arr[arr[:, 4] > 2000]` | `df[df['매출'] > 2000]` |
| `np.argmax(arr[:, 4])` → `names[idx]` | `df['매출'].idxmax()` — 인덱스(이름)가 바로 나온다 |
| `np.argsort(...)[::-1][:5]` | `df.nlargest(5, '매출')` |

판다스는 함수형(`np.f(x)`)이 아니라 거의 메소드형(`df.f()`)이고, 집계의 기본 축이 `axis=0`(열마다)이다. 지난 노트에서 "표 데이터는 거의 `axis=0`"이라 적어 둔 것이 판다스의 기본값으로 굳어진 셈이다. `idxmax`는 `argmax`의 판다스판으로, 위치 번호가 아니라 **인덱스 이름**을 돌려주어 "가장 큰 값이 누구 것인가"가 한 번에 나온다.

### 다음에 볼 키워드

- `pd.DataFrame(리스트 / 딕셔너리 / ndarray, columns=, index=)`·`Series`·`.values`
- `shape`·`columns`·`index`·`head`/`tail`·`info`·`describe`
- `iloc`(번호·끝 미포함) vs `loc`(이름·끝 포함)·이중 대괄호로 열 여러 개
- `df[새열] = …`·`loc[조건, 열] = 값`·`SettingWithCopyWarning`
- 불리언 필터·`&`/`|`/`~`+소괄호·`isin`·`between`·`query`
- `read_csv`·`set_index`·`sort_values`·`drop`
- `groupby`·`agg`·`merge`·`concat`·`isna`/`fillna`·`astype`·`idxmax`·`nlargest`

## 실습 파일

- `KDT_2026/2026_Python/day08/p-01.py` — `import pandas as pd`, 2차원 리스트 `[['ant', 25, 'seoul'], …]`로 `pd.DataFrame(data_list)`(열 이름 `0, 1, 2` 자동)와 `columns=['name', 'age', 'city']` 지정, 딕셔너리 `{'name': […], 'age': […], 'city': […]}`로 만들기(키 = 열 이름), `df['age']`로 열 하나 꺼내 `type` 확인(`Series`·`.values`는 `numpy.ndarray`), `np.array(data_list)` 넘파이 배열 + `index=['A', 'B', 'C']`로 행 이름 붙이기, 주요 속성 `shape`·`columns`·`index`·`values`·`head(2)`·`tail(2)`·`info()`, `iloc[1]`·`iloc[1, 2]`·`loc['B']`·`loc['B', 'city']` 번호·이름 인덱싱, `iloc[0:2, 0:1]`·`loc['A':'C', 'name':'age']` 슬라이싱, `df['score'] = [100, 80, 95]` 열 추가, `df['age'] = [31, 52, 40]`·`iloc[0, 0] = 'apple'`·`loc[['A', 'B'], 'score'] = [50, 60]` 값 수정, `df['score'] > 70` 불리언 `Series`와 `df[df['score'] > 70]` 필터링, `cont = df['age'] >= 40` 조건 변수와 `&`·`|` 복합 조건, 매크로 → RPA 메모

## 관련 노트

[[Python 정리본 인덱스]] · [[Python day07 넘파이로 따릉이 대여소 재배치 분석 실습]] · [[Python day06 넘파이 인덱싱·슬라이싱과 배열 연산]] · [[Python day07 넘파이 통계 함수와 axis]] · [[Python day02 딕셔너리 선언과 키로 값 다루기]] · [[KDT_2026 학습 지도]]
