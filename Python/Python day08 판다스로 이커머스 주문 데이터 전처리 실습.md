---
출처: Claude 분석
원본: KDT_2026/2026_Python/practice/practice4.py, practice/ecommerce_orders_cs_data.csv
작성일: 2026-11-02
tags: [학습, python]
---

# Python day08 — 판다스로 이커머스 주문 데이터 전처리 실습

> 실습 파일: `practice/practice4.py`, `practice/ecommerce_orders_cs_data.csv`
> 허브: [[Python 정리본 인덱스]] · 이전: [[Python day08 판다스 연습문제 풀이]] · 다음: [[Python day09 맷플롯립 시작과 선 차트]]

day08 전처리 노트에서 ①~⑩ 파이프라인으로 정리한 것을 **실제 CSV 한 장에 순서대로 적용하는** 실습이다. 재료는 이커머스 주문 1,000건(`Order_ID`·`Customer_ID`·`Order_Date`·`Category`·`Price`·`Quantity`·`Payment`·`Status` 여덟 열)이고, 일부러 중복 행 20건·`Category` 빈 문자열과 결측·`Price` 결측 38건·`Quantity`에 `-1`과 `999` 같은 비정상 값이 섞여 있다. Step 1~6은 **진단 → 중복 제거·자료형 → 공백·결측 → 이상치 → 파생변수 → 집계·정렬 → 인코딩** 순서로, 지난 노트의 사원 명부 20행에서 연습한 동작을 1,000행 데이터에 그대로 옮긴다. 새로 등장하는 것은 정규표현식으로 공백 문자열을 잡는 `replace(r'^\s*$', None, regex=True)`, 결측 **비율**을 보는 `isnull().mean()`, 조건에 따라 값을 바꾸는 `mask`, 그리고 `groupby().agg()`의 named aggregation을 **정렬까지 이어 붙이는** 흐름이다. 끝나면 980행 × 15열의 모델 입력용 표가 나온다.

## 1. 배운 내용

### 1-1. 출발점 찍기 — `read_csv(encoding='utf-8-sig')`·`info()`·`head()`

```python
df = pd.read_csv('./practice/ecommerce_orders_cs_data.csv', encoding='utf-8-sig')
df.info()
```

| 열 | non-null | dtype | 눈에 띄는 점 |
| --- | --- | --- | --- |
| `Order_ID` | 1000 | object | `ORD-20230067` 형식 문자열 |
| `Customer_ID` | 1000 | **int64** | 식별자인데 숫자로 읽힘 → Step 1에서 문자열로 |
| `Order_Date` | 1000 | **object** | 날짜인데 문자열 → Step 4에서 `datetime` |
| `Category` | **995** | object | 결측 5 + 보이지 않는 공백 문자열이 더 있음 |
| `Price` | **962** | float64 | 결측 38 |
| `Quantity` | 1000 | int64 | 결측은 없지만 `-1`·`999` 포함 |
| `Payment`·`Status` | 1000 | object | 범주 3종씩 |

`encoding='utf-8-sig'`는 따릉이 넘파이 실습에서 본 **BOM(`﻿`) 제거** 옵션이다 — 엑셀로 저장한 UTF-8 CSV의 첫 열 이름 앞에 붙는 보이지 않는 문자를 떼 준다. `info()` 한 번으로 "어느 열에 결측이 있고(`non-null`이 1000보다 작은 열), 어느 열의 자료형이 뜻과 다른가(`Customer_ID`가 숫자, `Order_Date`가 문자열)"를 먼저 적어 두는 것이 전처리의 시작이다. 단, `Category 995 non-null`에는 함정이 있다 — `''`·`'   '` 같은 **공백 문자열은 non-null로 세어지기** 때문에 실제 비어 있는 칸은 더 많다. 지난 노트의 `부서 20 non-null` 함정이 그대로 재현된다.

### 1-2. Step 1 — 중복 제거·인덱스 재정렬·식별자 문자열화

```python
df = df.drop_duplicates().reset_index(drop=True)
print(df.shape)                                    # (980, 8)
df['Customer_ID'] = df['Customer_ID'].astype(str)
```

| 동작 | 전 | 후 | 이유 |
| --- | --- | --- | --- |
| `drop_duplicates()` | 1000행 | **980행** | 여덟 열이 전부 같은 행 20건 제거 |
| `reset_index(drop=True)` | 인덱스에 구멍 | 0~979 연속 | 지운 자리 번호를 `index` 열로 남기지 않고 버림 |
| `astype(str)` | `int64` | `object` | 고객 ID는 더하거나 평균 낼 대상이 아님 |

`drop_duplicates()`·`reset_index()`·`astype()` 셋 다 **새 결과를 돌려주는** 메소드라 다시 대입해야 한다. 점으로 이어 쓴 첫 줄은 "중복을 지운 표에서 → 인덱스를 다시 매긴 표"를 한 번에 받은 것이다. `Customer_ID`를 문자열로 바꾸는 것은 지난 노트의 `사번` 그대로 — 숫자로 두면 뒤의 `describe()`·`corr()`·`get_dummies` 같은 곳에 "고객 번호의 평균" 같은 **의미 없는 숫자가 섞여 들어가기** 때문이다. 바꾼 뒤 `info()`를 다시 찍으면 `Customer_ID 980 non-null object`로 확인된다.

### 1-3. Step 2 — 정규표현식으로 공백 문자열 잡기와 결측 비율

```python
df['Category'] = df['Category'].replace(r'^\s*$', None, regex=True)
print(df.isnull().sum())          # Category 10, Price 38
print(df.isnull().mean() * 100)   # Category 1.02 %, Price 3.88 %
```

| 정규식 조각 | 뜻 |
| --- | --- |
| `^` | 문자열의 시작 |
| `\s*` | 공백 문자(스페이스·탭 등) 0개 이상 |
| `$` | 문자열의 끝 |
| 합치면 | **"처음부터 끝까지 공백뿐이거나 아예 비어 있는 문자열"** |

지난 노트에서는 `.str.strip()` 뒤 `replace('', None)` 두 단계로 했던 일을 **정규식 한 줄**로 끝낸다. `regex=True`를 켜면 첫 인자가 "값 그대로"가 아니라 **패턴**으로 해석되어, `''`도 `'   '`도 한 번에 `None`(→ `NaN`)으로 바뀐다. 그 결과 `Category` 결측이 info에서 본 5개에서 **10개**로 드러난다 — 공백 문자열 5개가 숨어 있었다는 뜻이다. `isnull().sum()`이 개수라면 `isnull().mean()`은 **비율**이다. 참을 1로 평균 내면 "결측 행 / 전체 행"이 되므로 `* 100`을 붙여 퍼센트로 읽는다. 결측이 1%인 열과 40%인 열은 대처가 다르기 때문에(채우기 vs 열 자체를 버리기) 개수보다 비율을 먼저 본다.

```python
df['Category'] = df['Category'].fillna(df['Category'].mode()[0])   # 최빈값 '식품'
df['Price'] = df['Price'].fillna(df['Price'].median())             # 중앙값 76,350
```

| 열 | 채운 값 | 왜 그 값인가 |
| --- | --- | --- |
| `Category`(범주) | `mode()[0]` = 가장 많은 카테고리 | 범주에는 평균이 없음 · `mode()`는 `Series`라 `[0]`으로 첫 값 |
| `Price`(수치) | `median()` | 평균은 극단값에 끌려가고 중앙값은 **이상치에 강건** |

채운 뒤 `isnull().sum()`을 다시 찍어 **전부 0**인지 확인하는 것으로 Step 2를 닫는다. "진단 → 처리 → 재진단"의 세 박자가 모든 단계에 반복된다.

### 1-4. Step 3 — 범위 밖 수량을 경계값으로 — `clip`

```python
df['Quantity'] = df['Quantity'].clip(lower=1, upper=10)
print(df['Quantity'].min(), df['Quantity'].max())   # 1 10
```

처리 전 `Quantity`의 분포는 `-1`이 122건, `999`가 108건으로, 정상 범위(1~5) 바깥 값이 전체의 23%나 된다. `clip(lower=1, upper=10)`은 1보다 작은 값을 **1로**, 10보다 큰 값을 **10으로** 눌러 붙이고 그 사이 값은 그대로 둔다. 행을 지우는 `df[(df['Quantity'] >= 1) & (df['Quantity'] <= 10)]`과 달리 **행 수가 유지**되므로 뒤의 집계에서 표본이 줄지 않는다. 다만 `999`가 전부 `10`이 되므로 "상한에 붙은 값이 유난히 많다"는 흔적이 남고, 이것이 실제 데이터라면 `999`가 결측 코드였을 가능성을 의심해 `NaN`으로 바꾸는 쪽이 맞을 수도 있다. 지난 노트의 "행 제거 · `NaN` 치환 · `clip` 세 갈래" 표가 여기서 선택지로 다시 나온다.

### 1-5. Step 4 — 파생변수 셋: 곱·날짜 분해·조건 라벨

```python
df['Total_Amount'] = df['Price'] * df['Quantity']

df['Order_Date'] = pd.to_datetime(df['Order_Date'])
df['Order_Year'] = df['Order_Date'].dt.year
df['Order_Month'] = df['Order_Date'].dt.month

df['VIP_Flag'] = 'Normal'
df['VIP_Flag'] = df['VIP_Flag'].mask(df['Total_Amount'] >= 300000, 'VIP')
print(df['VIP_Flag'].value_counts())   # Normal 712, VIP 268
```

| 파생 열 | 만든 방법 | 성격 |
| --- | --- | --- |
| `Total_Amount` | 열 × 열 (요소별 곱) | 수치 — 단가 × 수량 |
| `Order_Year`·`Order_Month` | `to_datetime` 뒤 `.dt.year`·`.dt.month` | 날짜 분해 — 월별 집계의 키 |
| `VIP_Flag` | 기본값 `'Normal'` 깔고 `mask(조건, 'VIP')` | 범주 — 30만 원 기준 두 갈래 |

`Price * Quantity`는 넘파이의 요소별 곱이 `Series`에 그대로 적용된 것이다 — 고객 구매 실습에서 `data[:, 4] / data[:, 1]`로 비율 지표를 만들던 것과 같은 동작이다. `Order_Date`는 문자열로 읽혔으므로 `pd.to_datetime`으로 `datetime64`로 바꿔야 `.dt` 접근자가 열리고, 그 뒤에야 연도·월을 **숫자 열로** 뽑을 수 있다. 데이터는 2023-01-01부터 2024-01-01까지라 `Order_Year`는 거의 2023이다.

`mask`는 이번에 처음 쓰는 메소드다. **`mask(조건, 값)` = 조건이 참인 자리를 값으로 바꾼다**. 연습문제의 `df.loc[df['Total_Amount'] >= 300000, 'VIP_Flag'] = 'VIP'`와 결과가 같지만, `loc` 대입이 원본을 고치는 문장이라면 `mask`는 **새 `Series`를 돌려주는 식**이라 체이닝에 끼워 넣기 좋다. 짝꿍 `where(조건, 값)`는 반대로 조건이 **거짓인** 자리를 바꾼다 — `np.where(조건, 참값, 거짓값)`와 이름이 같지만 인자 뜻이 달라 헷갈리기 쉬운 지점이다.

### 1-6. Step 5 — 카테고리별 세 지표 집계와 정렬

```python
new_df = df.groupby('Category').agg(
    주문건수=('Order_ID', 'count'),
    총매출=('Total_Amount', 'sum'),
    평균단가=('Price', 'mean')
)
new_df = new_df.sort_values(by='총매출', ascending=False)
```

| Category | 주문건수 | 총매출 | 평균단가 |
| --- | --- | --- | --- |
| 식품 | 272 | 75,627,500 | 81,799 |
| 패션의류 | 244 | 62,553,000 | 79,459 |
| 전자기기 | 238 | 56,047,350 | 72,385 |
| 생활용품 | 226 | 53,691,950 | 75,485 |

`agg(새이름=(원본열, 함수))` 모양의 **named aggregation**은 지난 노트의 `agg(인원수=('사번','count'), …)`과 같다. 열마다 **다른 함수**를 적용하면서 결과 열 이름까지 한 번에 정하는 것이 요점이고, 따릉이 넘파이 실습에서 `for i in ids: m = data[:, 0] == i; np.sum(data[m, 2])`로 돌리던 마스크 반복이 이 네 줄로 접힌다. `groupby` 결과는 `Category`가 **인덱스**로 올라간 표라 `sort_values(by='총매출')`로 열 이름을 바로 쓸 수 있고, `ascending=False`로 큰 순서를 만든다. 식품이 건수·매출 모두 1위인데 Step 2에서 결측 `Category` 10건을 최빈값 '식품'으로 채운 영향이 조금 섞여 있다는 점은 기억해 둘 만하다 — **채운 값은 집계에 섞인다**는 지난 노트의 주의가 숫자로 보이는 자리다.

### 1-7. Step 6 — 원-핫 인코딩 `get_dummies(dtype=int)`

```python
df_encoded = pd.get_dummies(df, columns=['Payment', 'VIP_Flag'], dtype=int)
print(df_encoded.columns)
# … 'Payment_간편결제', 'Payment_계좌이체', 'Payment_신용카드', 'VIP_Flag_Normal', 'VIP_Flag_VIP'
```

| 원래 열 | 값 | 생기는 열 |
| --- | --- | --- |
| `Payment` | 간편결제·계좌이체·신용카드 | `Payment_간편결제`·`Payment_계좌이체`·`Payment_신용카드` |
| `VIP_Flag` | Normal·VIP | `VIP_Flag_Normal`·`VIP_Flag_VIP` |

문자열 범주는 모델에 바로 넣을 수 없고, 번호를 매기면 "신용카드(3) > 간편결제(1)" 같은 **없는 순서**가 생긴다. 그래서 값마다 **0/1 열 하나씩**으로 펼치는 것이 원-핫 인코딩이다. `columns=`로 대상 열을 지정하면 나머지 열은 그대로 두고 그 열들만 바꾸고, `dtype=int`를 주면 기본값 `True`/`False` 대신 `1`/`0` 정수로 나온다 — 대부분의 모델 라이브러리가 숫자를 기대하므로 붙여 두는 편이 안전하다. 980행 × 8열로 시작한 표가 파생 네 열과 인코딩 다섯 열(원래 두 열은 사라짐)을 거쳐 **980행 × 15열**이 된 것이 최종 모양이다.

### 1-8. 여섯 단계를 지난 노트의 ①~⑩과 겹쳐 보기

| Step | 이번 실습 | 지난 노트 번호 | 새로 더해진 것 |
| --- | --- | --- | --- |
| 0 | `read_csv(encoding='utf-8-sig')`·`info()`·`head()` | 진단 | 실제 CSV · BOM |
| 1 | `drop_duplicates().reset_index(drop=True)`·`astype(str)` | ①② | 체이닝 한 줄 |
| 2 | `replace(r'^\s*$', None, regex=True)`·`isnull().mean()`·`fillna(mode/median)` | ③④⑥ | **정규식 · 결측 비율** |
| 3 | `clip(lower=1, upper=10)` | ⑦ | — |
| 4 | 곱·`to_datetime`+`.dt`·`mask` | ⑨ | **`mask`로 조건 라벨** |
| 5 | `groupby().agg(named)`+`sort_values` | ⑩ | **집계 → 정렬 연결** |
| 6 | `get_dummies(columns=, dtype=int)` | 원-핫 | `columns=`로 대상 지정 |

## 2. 추가로 알면 좋은 활용법

### 2-1. 공백 정제의 세 가지 표기

```python
df['Category'].replace(r'^\s*$', None, regex=True)          # 이번 실습 — 공백뿐인 값을 NaN으로
df['Category'].str.strip().replace('', None)                 # 지난 노트 — 두 단계
df['Category'].str.strip().replace('', np.nan)               # NaN을 명시적으로
```

`None`을 넣으면 판다스가 `NaN`으로 바꿔 저장한다. 앞뒤 공백만 있고 글자가 있는 값(`' 식품 '`)은 정규식 쪽에서는 그대로 남으므로, 그런 값까지 정리하려면 `.str.strip()`을 먼저 한 번 돌리는 편이 안전하다.

### 2-2. 결측 비율로 열의 운명 정하기

```python
null_ratio = df.isnull().mean()
cols_to_drop = null_ratio[null_ratio > 0.5].index    # 절반 넘게 비면 열 자체를 버림
df = df.drop(columns=cols_to_drop)
```

비율이 작으면 채우고, 크면 열을 버리고, 중간이면 "결측 여부" 자체를 새 열(`Price_missing = df['Price'].isnull().astype(int)`)로 남기는 선택지가 있다. 결측이 무작위가 아닐 때 그 사실 자체가 정보가 되기 때문이다.

### 2-3. `mask`·`where`·`np.where`·`loc` 네 가지 비교

```python
df['VIP_Flag'] = df['VIP_Flag'].mask(df['Total_Amount'] >= 300000, 'VIP')      # 참인 곳을 바꿈
df['VIP_Flag'] = df['VIP_Flag'].where(df['Total_Amount'] < 300000, 'VIP')      # 거짓인 곳을 바꿈 (같은 결과)
df['VIP_Flag'] = np.where(df['Total_Amount'] >= 300000, 'VIP', 'Normal')       # 기본값 없이 한 줄
df.loc[df['Total_Amount'] >= 300000, 'VIP_Flag'] = 'VIP'                        # 원본 수정 문장
```

결과는 넷 다 같다. 두 갈래면 `np.where` 한 줄이 가장 짧고, 셋 이상이면 `np.select`나 `pd.cut`, 체이닝 안에서는 `mask`/`where`, 일부만 고칠 때는 `loc`가 어울린다.

### 2-4. 월별 매출 — 날짜 파생열을 바로 집계에 쓰기

```python
monthly = df.groupby('Order_Month')['Total_Amount'].sum()
monthly = df.groupby(df['Order_Date'].dt.to_period('M'))['Total_Amount'].sum()   # 연-월 한 번에
df.set_index('Order_Date').resample('M')['Total_Amount'].sum()                    # 시계열 전용
```

`Order_Month`를 뽑은 이유는 결국 이런 집계 때문이다. 연도가 둘 이상 섞이면 월만으로는 겹치므로 `to_period('M')`이나 `resample`로 연-월을 함께 쓴다.

### 2-5. 집계 뒤 정렬·상위 N·비율 열

```python
new_df['매출비중'] = new_df['총매출'] / new_df['총매출'].sum() * 100
new_df.nlargest(2, '총매출')                 # 상위 2개
new_df.reset_index()                         # Category를 다시 열로
new_df['평균단가'] = new_df['평균단가'].round(0).astype(int)
```

집계표에 비중 열을 붙이면 "식품이 전체 매출의 30%"처럼 보고서 문장이 바로 나온다. `groupby` 결과의 인덱스를 열로 되돌리는 `reset_index()`는 차트나 `merge`에 넘기기 전에 자주 필요하다.

### 2-6. `get_dummies`의 `drop_first`와 `category` dtype

```python
pd.get_dummies(df, columns=['Payment'], dtype=int, drop_first=True)   # 열 하나 줄이기 (다중공선성 완화)
df['Payment'] = df['Payment'].astype('category');  df['Payment'].cat.codes   # 번호 인코딩 (트리 모델용)
```

범주 k개에서 열 k−1개만 있어도 정보는 같으므로 선형 모델에서는 `drop_first=True`를 흔히 쓴다. 트리 계열 모델은 순서 없는 번호로도 괜찮아 `cat.codes`가 가볍다.

## 3. 더 나아가 알면 좋은 것

### 3-1. 데이터 누수 — 전처리 통계는 학습 데이터에서만

`fillna(median())`·`clip`의 경계·Min-Max의 최소·최대는 전부 **데이터에서 계산한 값**이다. 모델을 평가할 때 테스트 데이터까지 섞어 이 값을 구하면 "답을 미리 본" 셈이 되어 성능이 부풀려진다(데이터 누수). 그래서 사이킷런은 `SimpleImputer`·`MinMaxScaler`를 `fit(train)` → `transform(test)`로 나눠 쓰게 설계했고, 이번 실습의 각 Step이 그 변환기 하나하나에 대응한다.

### 3-2. 전처리를 함수로 — 재현 가능한 파이프라인

```python
def preprocess(df):
    df = df.drop_duplicates().reset_index(drop=True)
    df['Customer_ID'] = df['Customer_ID'].astype(str)
    df['Category'] = df['Category'].replace(r'^\s*$', None, regex=True)
    ...
    return df
```

Step을 함수 하나에 담아 두면 다음 달 CSV에도 같은 처리를 **한 줄로** 재적용할 수 있고, 단계 순서가 코드로 고정된다. 사이킷런의 `Pipeline`·`ColumnTransformer`가 이것을 모델 학습까지 묶는 정식 도구다.

### 3-3. 이상치 경계를 데이터에서 — IQR과 분위수

이번에는 `clip(1, 10)`처럼 **도메인 지식**으로 경계를 정했다. 기준이 없을 때는 `Q1 − 1.5·IQR`·`Q3 + 1.5·IQR`(박스플롯 수염)이나 `quantile(0.01)`·`quantile(0.99)` 같은 분위수를 경계로 쓴다. 시본 노트의 박스플롯이 이 경계를 그림으로 보여 주는 도구다.

### 3-4. 다음에 볼 키워드

- `read_csv(encoding, dtype=, parse_dates=, na_values=)`·BOM·`usecols`
- 정규표현식 `^`·`$`·`\s`·`*`·`regex=True`·`str.contains`·`str.extract`
- `isnull().mean()`·`notna`·`dropna(thresh=)`·결측 지표 열·MCAR/MAR
- `mask`/`where`·`np.where`/`np.select`·`pd.cut`/`qcut`
- `to_datetime(format=, errors='coerce')`·`.dt.to_period`·`resample`·`dayofweek`
- `groupby().agg` named aggregation·`transform`·`nlargest`·`reset_index`
- `get_dummies(drop_first)`·`category`·`OneHotEncoder`·`ColumnTransformer`·`Pipeline`·데이터 누수

## 실습 파일

- `KDT_2026/2026_Python/practice/practice4.py` — `pd.read_csv(encoding='utf-8-sig')`·`info()`·`head()`로 1,000행 8열 진단, Step 1 `drop_duplicates().reset_index(drop=True)` → 980행과 `Customer_ID.astype(str)`, Step 2 `replace(r'^\s*$', None, regex=True)`로 공백 문자열 결측화 → `isnull().sum()`(Category 10·Price 38)·`isnull().mean() * 100` 비율 → `fillna(mode()[0])`·`fillna(median())`, Step 3 `Quantity.clip(lower=1, upper=10)`, Step 4 `Total_Amount = Price * Quantity`·`to_datetime` + `.dt.year`/`.dt.month`·`VIP_Flag` 기본값 뒤 `mask(Total_Amount >= 300000, 'VIP')`(Normal 712·VIP 268), Step 5 `groupby('Category').agg(주문건수=('Order_ID','count'), 총매출=('Total_Amount','sum'), 평균단가=('Price','mean'))` → `sort_values(by='총매출', ascending=False)`, Step 6 `pd.get_dummies(columns=['Payment','VIP_Flag'], dtype=int)` → 15열
- `KDT_2026/2026_Python/practice/ecommerce_orders_cs_data.csv` — 주문 1,000건: `Order_ID`·`Customer_ID`·`Order_Date`(2023-01-01~2024-01-01)·`Category`(식품·패션의류·전자기기·생활용품)·`Price`·`Quantity`·`Payment`(간편결제·신용카드·계좌이체)·`Status`(배송완료·취소·반품요청)

## 관련 노트

[[Python 정리본 인덱스]] · [[Python day08 판다스 연습문제 풀이]] · [[Python day09 맷플롯립 시작과 선 차트]] · [[Python day08 판다스 데이터 전처리 중복 제거와 타입 변환]] · [[KDT_2026 학습 지도]]
