---
출처: Claude 분석
원본: KDT_2026/2026_Python/practice/practice3.py
작성일: 2026-11-02
tags: [학습, python]
---

# Python day08 — 판다스 연습문제 풀이

> 실습 파일: `practice/practice3.py`
> 허브: [[Python 정리본 인덱스]] · 이전: [[Python day08 판다스 데이터 전처리 중복 제거와 타입 변환]] · 다음: [[Python day08 판다스로 이커머스 주문 데이터 전처리 실습]]

day08의 데이터프레임 생성·`loc`/`iloc`·불리언 필터링·`rename`·`concat`·`merge`를 **문제 열 개로 다시 밟는** 파일이다. 문제마다 작은 데이터프레임(도서관 재고·카페 메뉴·쇼핑몰 상품·도서 대여·학생 성적·매장 재고·회원 실적·지점 실적·회원 주문)을 딕셔너리로 직접 만들어 쓰기 때문에 CSV 없이 혼자 돌려 볼 수 있다. 넘파이 연습문제가 "배열 문법"을 확인했다면, 이번에는 **표를 이름으로 다루는 법**이 주제다 — `loc`는 이름으로 양 끝 포함, `iloc`은 번호로 끝 미포함, 조건 필터링은 `&`·`|`에 소괄호, **조건에 맞는 행의 특정 열만 바꾸는 `df.loc[조건, '열'] = 값`**, 그리고 표 두 장을 세로로 잇는 `concat`과 키로 붙이는 `merge`. 풀고 나면 문제 5·6·7이 전부 같은 한 줄 패턴이라는 것, `merge`의 `inner`와 `outer`는 "빠지는 행"과 "생기는 `NaN`"의 차이라는 것이 또렷해진다.

## 1. 배운 내용

### 1-1. 딕셔너리로 만든 표의 네 가지 속성 — `shape`·`index`·`columns`·`info()`

```python
data_dict = {
    'BookTitle': ['Python Basic', 'Data Analysis', 'AI Agent'],
    'Stock': [15, 8, 23],
    'Location': ['Floor_1', 'Floor_2', 'Floor_1']
}
df = pd.DataFrame(data_dict)
print(df.shape)     # (3, 3)
print(df.index)     # RangeIndex(start=0, stop=3, step=1)
print(df.columns)   # Index(['BookTitle', 'Stock', 'Location'], dtype='object')
df.info()
```

| 확인한 것 | 결과 | 읽는 법 |
| --- | --- | --- |
| `shape` | `(3, 3)` | 행 3 × 열 3 — 속성이라 괄호 없음 |
| `index` | `RangeIndex(0, 3)` | `index=`를 안 줬으니 0·1·2 자동 번호 |
| `columns` | `Index([...])` | 딕셔너리의 **키**가 그대로 열 이름 |
| `info()` | `3 entries`, `Stock int64`, 나머지 `object` | 메소드라 괄호 있음 · 결측·자료형 점검용 |

딕셔너리로 만들 때는 **키 = 열 이름, 값 리스트 = 그 열의 세로 데이터**다. 2차원 리스트로 만들 때(바깥 리스트 = 행)와 재료 방향이 반대라는 것을 판다스 첫 노트에서 표로 정리했었다. `info()`에서 문자열 열이 `object`로 찍히는 것은 판다스가 문자열을 "파이썬 객체"로 들고 있기 때문이고, 숫자 열만 `int64`·`float64`로 잡힌다. `shape`·`index`·`columns`가 **속성**(괄호 없음)이고 `info()`·`head()`가 **메소드**(괄호 있음)인 구분은 이번에도 그대로다.

### 1-2. `loc`와 `iloc` — 이름이면 양 끝 포함, 번호면 끝 미포함

```python
df = pd.DataFrame({...}, index=['C1', 'C2', 'C3', 'C4'])
print(df.loc['C2':'C3', 'Menu':'Price'])
#          Menu  Price
# C2  Croissant   3800
# C3      Latte   5000
print(df.iloc[1, 2])   # Bakery
```

| 접근자 | 재료 | 슬라이스 끝 | 이 문제에서 |
| --- | --- | --- | --- |
| `loc` | **이름**(인덱스 라벨·열 이름) | **포함** | `'C2':'C3'` 두 행, `'Menu':'Price'` 두 열 |
| `iloc` | **정수 위치** | 미포함 | `[1, 2]` → 1번 행 `Croissant`의 2번 열 `Category` |

`index=['C1', …]`를 넘겼기 때문에 행에 이름이 생겼고, 그래서 `loc['C2':'C3']`처럼 **이름으로 범위**를 잡을 수 있다. 리스트·넘파이의 끝 미포함에 익숙하다가 `loc`에서 `'C3'`가 포함되는 것을 보면 어색한데, "이름 범위는 사람이 읽는 대로 양 끝을 넣는다"고 외워 두면 된다. `iloc[1, 2]`는 넘파이의 `arr[1, 2]`와 똑같이 **번호 두 개로 칸 하나**를 집는다. 같은 칸을 `loc`로 쓰면 `df.loc['C2', 'Category']`다. 행 이름이 있는 표에서 `df[1]`처럼 대괄호에 숫자만 넣으면 열 이름 1을 찾다가 `KeyError`가 나므로, 행을 고를 땐 항상 `loc`/`iloc`을 거친다.

### 1-3. 조건 두 개 — `&`(둘 다)와 `|`(하나라도)

```python
# 문제 3: 평점 4.0 이상 AND 리뷰 100 이상
print(df[(df['Rating'] >= 4.0) & (df['ReviewCount'] >= 100)])
#      Product  Rating  ReviewCount
# P1  Keyboard     4.5          150
# P3   Headset     4.2          210

# 문제 4: 대여 20회 이상 OR 연체 5일 이상
print(df[(df['RentCount'] >= 20) | (df['OverdueDays'] >= 5)])
#      Title  RentCount  OverdueDays
# B1  Book_A         12            7
# B2  Book_B         22            2
# B4  Book_D         25            6
```

| 행 | Rating ≥ 4.0 | ReviewCount ≥ 100 | `&` 결과 |
| --- | --- | --- | --- |
| P1 Keyboard | T | T | **T** |
| P2 Mouse | F | F | F |
| P3 Headset | T | T | **T** |
| P4 Webcam | T | F | F |

`df['Rating'] >= 4.0`은 행마다 참·거짓이 적힌 **불리언 `Series`**이고, 두 개를 `&`로 묶어 `df[…]`에 넣으면 참인 행만 남는다. 넘파이 연습문제 9번과 완전히 같은 규칙 — `and`/`or` 대신 `&`/`|`, 비교식마다 **소괄호 필수** — 이 판다스에도 그대로 적용된다. 결과 표에 원래 인덱스(`P1`·`P3`)가 따라오는 것이 넘파이와 다른 점이고, 그래서 어느 행이 살아남았는지 바로 읽힌다. `|` 쪽은 Book_B가 연체는 2일이지만 대여 22회로 통과했고, Book_C만 둘 다 못 넘어 빠졌다.

### 1-4. 조건에 맞는 행의 한 열만 바꾸기 — `df.loc[조건, '열'] = 값`

```python
# 문제 5: 90점 이상 → Grade 'A+'
df.loc[df['FinalScore'] >= 90, 'Grade'] = 'A+'
# 문제 6: 재고 10 미만 → Status 'Restock_Needed'
df.loc[df['Stock'] < 10, 'Status'] = 'Restock_Needed'
# 문제 7: 기본값 열을 먼저 깔고 → 30만 이상만 'VIP'
df['Membership'] = 'General'
df.loc[df['TotalSpent'] >= 300000, 'Membership'] = 'VIP'
```

| 문제 | 행 조건 | 바꿀 열 | 결과 |
| --- | --- | --- | --- |
| 5 | `FinalScore >= 90` | `Grade` | Bob 94·David 91 → `A+`, 나머지 그대로 |
| 6 | `Stock < 10` | `Status` | Notebook 6·Ruler 8 → `Restock_Needed` |
| 7 | `TotalSpent >= 300000` | `Membership`(새 열) | Lee·Park → `VIP`, Kim·Choi → `General` |

세 문제가 **같은 한 줄**이다. `loc`의 행 자리에 불리언 `Series`, 열 자리에 열 이름을 넣고 대입하면 "조건에 맞는 행의 그 열"만 바뀐다. 판다스 첫 노트에서 `df['passed'] = False`를 깔고 `loc[조건, 'passed'] = True`로 채우던 "필터링으로 새 열 만들기"가 문제 7의 모양이고, 문제 5·6은 **이미 있는 열**을 같은 방법으로 덮어쓰는 경우다. 중요한 것은 `df[df['FinalScore'] >= 90]['Grade'] = 'A+'`처럼 두 단계로 쓰지 않는 것이다 — 그렇게 하면 중간 결과가 복사본일 수 있어 원본이 안 바뀌고 `SettingWithCopyWarning`이 뜬다. **행 조건과 열을 `loc` 한 번에** 넣는 것이 정석이다. 문제 7처럼 기본값을 먼저 전부 깔아 두면 조건에 안 걸린 행이 `NaN`으로 남지 않는다.

### 1-5. 열 이름 바꾸고 집계 — `rename`·`sum`·`value_counts`

```python
df = df.rename(columns={'Units': '판매수량', 'Discount': '할인율'})
print(df['판매수량'].sum())            # 275
print(df['Grade'].value_counts())
# Grade
# A    2
# B    2
```

`rename(columns={옛: 새})`은 **새 표를 돌려주고 원본은 그대로**라서 `df = df.rename(…)`으로 다시 받아야 한다 — 넘파이의 `astype`, 판다스의 `drop_duplicates`와 같은 "반환형" 메소드다. 바꾼 뒤에는 당연히 **새 이름**으로 열을 불러야 하고(`df['Units']`는 이제 `KeyError`), 한글 열 이름도 문제없이 쓰인다. `sum()`은 숫자 열 하나의 합이고, `value_counts()`는 범주 열의 **고윳값별 개수**를 많은 순으로 돌려준다. 딕셔너리 연습문제에서 `counter` 딕셔너리로 등장 횟수를 세던 일이 메소드 하나로 접힌 셈이다. 결과가 `Series`라 `df['Grade'].value_counts()['A']`처럼 값 하나를 꺼낼 수도 있다.

### 1-6. 세로로 잇기 — `concat`과 `ignore_index=True`

```python
df_first = pd.DataFrame({'Code': ['S10', 'S20'], 'Revenue': [500, 750]})
df_second = pd.DataFrame({'Code': ['S30', 'S40'], 'Revenue': [620, 890]})
new_df = pd.concat([df_first, df_second], axis=0, ignore_index=True)
#   Code  Revenue
# 0  S10      500
# 1  S20      750
# 2  S30      620
# 3  S40      890
```

`concat`은 **리스트로 묶은 표들**을 `axis=0`이면 아래로(행 추가), `axis=1`이면 옆으로(열 추가) 붙인다. 넘파이의 `vstack`/`hstack`에 대응하되, 열 이름이 같은 것끼리 자동으로 맞춰 준다. `ignore_index=True`가 없으면 인덱스가 `0, 1, 0, 1`로 겹쳐 남는데, 상·하반기 실적처럼 "같은 종류의 행이 더 늘어난" 상황에서는 **새로 0부터 번호**를 매기는 쪽이 맞다. 전처리 노트의 `drop_duplicates().reset_index(drop=True)`와 같은 결과를 옵션 하나로 얻는 것이다.

### 1-7. 키로 붙이기 — `merge`의 `inner` vs `outer`

```python
df_user  = pd.DataFrame({'UID': [101, 102, 103], 'User': ['James', 'Emma', 'Lucas']})
df_order = pd.DataFrame({'UID': [102, 103, 104], 'Amount': [15000, 32000, 21000]})

pd.merge(df_user, df_order, on='UID', how='inner')
#    UID   User  Amount
# 0  102   Emma   15000
# 1  103  Lucas   32000

pd.merge(df_user, df_order, on='UID', how='outer')
#    UID   User   Amount
# 0  101  James      NaN
# 1  102   Emma  15000.0
# 2  103  Lucas  32000.0
# 3  104    NaN  21000.0
```

| `how` | 남는 UID | 행 수 | `isnull().sum()` | SQL |
| --- | --- | --- | --- | --- |
| `inner` | 양쪽 다 있는 102·103 | 2 | 전부 0 | `INNER JOIN` |
| `outer` | 한쪽에라도 있는 101~104 | 4 | `User 1`, `Amount 1` | `FULL OUTER JOIN` |

`concat`이 "같은 모양의 표를 더 쌓는" 것이라면 `merge`는 **공통 키(`UID`)로 다른 정보를 옆에 붙이는** 것이다. `inner`는 주문이 없는 James(101)와 회원 정보가 없는 104번 주문을 **버리고**, `outer`는 둘 다 살리되 비는 칸을 `NaN`으로 채운다. 그래서 `isnull().sum()`이 `inner`에서는 전부 0, `outer`에서는 `User`·`Amount` 각각 1이다. `Amount`가 `15000` → `15000.0`으로 바뀐 것도 눈여겨볼 점인데, `NaN`은 실수라 정수 열에 `NaN`이 하나라도 들어오면 열 전체가 **`float64`로 승격**된다 — 전처리 노트에서 `나이` 열이 `float64`가 된 것과 같은 이유다. "누락 확인이 목적이면 `outer` + `isnull`", "짝이 맞는 행만 분석하면 `inner`"로 고른다.

### 1-8. 열 문제를 동작별로 다시 보기

| 동작 | 문제 | 핵심 한 줄 |
| --- | --- | --- |
| 만들고 살피기 | 1 | `pd.DataFrame(dict)` → `shape`·`index`·`columns`·`info()` |
| 골라 읽기 | 2 | `loc[이름:이름, 열:열]`(양 끝 포함) · `iloc[번호, 번호]` |
| 조건 필터 | 3·4 | `df[(조건1) & (조건2)]` · `df[(조건1) \| (조건2)]` |
| 조건 수정 | 5·6·7 | `df.loc[조건, '열'] = 값` (새 열이면 기본값 먼저) |
| 이름·집계 | 8 | `rename(columns={})` 다시 받기 · `sum()` · `value_counts()` |
| 두 표 합치기 | 9·10 | `concat([…], ignore_index=True)` · `merge(on=, how='inner'/'outer')` |

## 2. 추가로 알면 좋은 활용법

### 2-1. `loc`로 여러 조건을 등급으로 — `np.select`·`pd.cut`

```python
# loc 세 번
df['Grade'] = 'C'
df.loc[df['FinalScore'] >= 80, 'Grade'] = 'B'
df.loc[df['FinalScore'] >= 90, 'Grade'] = 'A+'   # 큰 조건을 나중에 덮어써야 한다

# 한 번에
df['Grade'] = np.select([df['FinalScore'] >= 90, df['FinalScore'] >= 80], ['A+', 'B'], default='C')
df['Grade'] = pd.cut(df['FinalScore'], bins=[0, 80, 90, 100], labels=['C', 'B', 'A+'], right=False)
```

`loc` 대입을 여러 번 겹칠 때는 **넓은 조건부터 좁은 조건 순서**로 덮어써야 한다(위 예에서 순서를 바꾸면 90점대가 `B`로 덮인다). 조건이 셋 이상이면 `np.select`나 `pd.cut`이 읽기 쉽다.

### 2-2. 조건 필터의 다른 얼굴 — `query`·`isin`·`between`

```python
df.query('Rating >= 4.0 and ReviewCount >= 100')     # 문자열 식 — 여기서는 and/or를 쓴다
df[df['Category'].isin(['Coffee', 'Dessert'])]        # 여러 값 중 하나
df[df['Price'].between(4000, 5000)]                   # 양 끝 포함 범위
```

`query`는 소괄호·`&` 없이 문자열로 조건을 적는 방식이라 조건이 길어질 때 편하다. 단, 한글 열 이름은 백틱(`` `판매수량` > 50 ``)으로 감싼다.

### 2-3. `rename`의 변형과 `inplace`를 쓰지 않는 이유

```python
df.rename(columns=str.lower)                 # 함수로 일괄 변환
df.columns = ['item', 'units', 'discount', 'grade']   # 전부 갈아끼우기
df.rename(columns={...}, inplace=True)       # 원본 수정 — 체이닝이 끊겨 권장하지 않음
```

`inplace=True`는 반환값이 `None`이라 `df = df.rename(..., inplace=True)`로 쓰면 `df`가 `None`이 되는 사고가 흔하다. **다시 받는 습관**이 안전하다.

### 2-4. `value_counts`의 옵션

```python
df['Grade'].value_counts(normalize=True)   # 비율 (A 0.5, B 0.5)
df['Grade'].value_counts(ascending=True)   # 적은 순
df['Grade'].value_counts(dropna=False)     # NaN도 한 줄로 세기
```

`normalize=True`는 "구성비"를 바로 주어 보고서용 숫자로 쓰기 좋다.

### 2-5. `merge`를 읽기 쉽게 — `indicator`·`suffixes`·`validate`

```python
pd.merge(df_user, df_order, on='UID', how='outer', indicator=True)   # _merge 열: left_only / right_only / both
pd.merge(a, b, on='ID', suffixes=('_user', '_order'))                # 같은 이름 열 구분
pd.merge(a, b, on='ID', validate='one_to_one')                       # 키 중복이면 오류 — 뻥튀기 방지
```

`indicator=True`는 `outer` 결과에서 **어느 쪽에만 있던 행인지** 열로 알려 주어 `isnull`보다 정확하다. `validate`는 키가 중복되어 행이 곱절로 늘어나는 사고를 미리 막는다.

### 2-6. `concat`으로 가로 붙이기와 `join`

```python
pd.concat([df_a, df_b], axis=1)       # 인덱스 기준으로 옆에 붙이기
df_user.set_index('UID').join(df_order.set_index('UID'), how='left')   # 인덱스 키로 merge
```

`concat(axis=1)`은 **인덱스가 같은 행끼리** 옆으로 붙이는 것이라 키 열이 아니라 인덱스를 본다. 키를 인덱스로 올려 둔 표끼리는 `join`이 간결하다.

## 3. 더 나아가 알면 좋은 것

### 3-1. `how` 네 가지와 SQL JOIN — 어느 쪽을 기준으로 남기나

`inner`·`outer` 외에 `left`(왼쪽 표의 행은 전부 유지)·`right`가 있다. 실무에서 가장 흔한 것은 **`left`** — "회원 목록은 전부 두고 주문이 있으면 붙인다"처럼 기준 표가 분명할 때다. SQL의 `LEFT JOIN`과 1:1 대응이고, `merge` 뒤 `isnull()`로 "주문 없는 회원"을 찾는 것이 `WHERE o.id IS NULL`과 같은 질의다.

### 3-2. 인덱스를 이름으로 쓰는 설계

이번 문제들처럼 `index=['C1', …]`로 **의미 있는 키를 인덱스에 올려** 두면 `loc`가 사전처럼 동작한다. `set_index('UID')`·`reset_index()`로 열 ↔ 인덱스를 오가며, `merge` 대신 `join`을 쓰거나 `df.loc['C2']` 한 번으로 행을 꺼내는 설계가 가능하다. 반대로 인덱스에 중복이 있으면 `loc`가 여러 행을 돌려주므로, 키로 쓸 열은 `is_unique`로 확인해 둔다.

### 3-3. 메소드 체이닝으로 전처리 읽기

```python
result = (pd.concat([df_first, df_second], ignore_index=True)
            .rename(columns={'Revenue': '매출'})
            .query('매출 >= 600')
            .sort_values('매출', ascending=False))
```

`rename`·`query`·`sort_values`가 전부 **새 표를 돌려주기** 때문에 점으로 이어 쓸 수 있다. 소괄호로 감싸 줄을 나누면 위에서 아래로 "잇고 → 이름 바꾸고 → 거르고 → 정렬"이 읽힌다. `inplace`를 피하는 이유가 여기서 드러난다.

### 3-4. 다음에 볼 키워드

- `loc`/`iloc`·`at`/`iat`(칸 하나 빠르게)·`set_index`/`reset_index`·`is_unique`
- `query`·`isin`·`between`·`~`(부정)·`np.select`·`pd.cut`
- `rename(columns=함수)`·`inplace` 지양·메소드 체이닝·`assign`
- `value_counts(normalize, dropna)`·`nunique`·`groupby().size()`
- `concat(axis=1, keys=)`·`merge(how='left', indicator, suffixes, validate)`·`join`
- `NaN`과 `float64` 승격·`'Int64'` nullable 정수

## 실습 파일

- `KDT_2026/2026_Python/practice/practice3.py` — 문제 1 도서관 재고 딕셔너리 → `DataFrame`·`shape`·`index`·`columns`·`info()`, 문제 2 카페 메뉴(`index=['C1'…'C4']`) `loc['C2':'C3', 'Menu':'Price']`·`iloc[1, 2]`, 문제 3 상품 평점·리뷰 `&` 필터, 문제 4 도서 대여·연체 `|` 필터, 문제 5 `loc[FinalScore >= 90, 'Grade'] = 'A+'`, 문제 6 `loc[Stock < 10, 'Status'] = 'Restock_Needed'`, 문제 7 `df['Membership'] = 'General'` 뒤 `loc[TotalSpent >= 300000, 'Membership'] = 'VIP'`, 문제 8 `rename(columns={'Units': '판매수량', 'Discount': '할인율'})`·`sum()` 275·`value_counts()`, 문제 9 `pd.concat([df_first, df_second], axis=0, ignore_index=True)`, 문제 10 `pd.merge(df_user, df_order, on='UID', how='inner'/'outer')`와 `isnull().sum()` 비교

## 관련 노트

[[Python 정리본 인덱스]] · [[Python day08 판다스 데이터 전처리 중복 제거와 타입 변환]] · [[Python day08 판다스로 이커머스 주문 데이터 전처리 실습]] · [[Python day08 판다스 데이터프레임 생성과 인덱싱·필터링]] · [[KDT_2026 학습 지도]]
