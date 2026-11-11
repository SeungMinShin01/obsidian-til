---
출처: Claude 분석
원본: KDT_2026/2026_Python/day15/s-08.py
작성일: 2026-11-11
tags: [학습, ai, python]
---

# AI day15 — ColumnTransformer·OneHotEncoder로 범주형 특성 파이프라인

> 실습 파일: `day15/s-08.py`
> 허브: [[AI 정리본 인덱스]] · 이전: [[AI day15 Pipeline·StratifiedKFold·GridSearchCV로 다중 분류 C 탐색]] · 다음: [[AI day15 다중 분류 파이프라인 연습문제 풀이]]

day12부터 지금까지 특성은 전부 **숫자**였다. Fish의 길이·높이·너비, 학생 성적의 공부 시간, 유방암 자료의 세포핵 측정값 — 모델에 넣기 전에 한 일은 제곱항을 더하거나 표준화하는 것뿐이었다. `s-08.py`는 수업 첫 줄 주석 그대로 **"범주형(문자) 특성 갖는 학습 방법"**이다. 시본 내장 펭귄 자료(`penguins`)로 세 종을 맞히는데, 특성 여섯 중 `island`(섬 이름)와 `sex`(성별) 둘이 문자열이다. 문자열을 `LogisticRegression`에 그대로 넣으면 `could not convert string to float: 'Biscoe'`로 멈춘다. 해법은 두 도구다 — 범주를 0/1 열로 바꾸는 **`OneHotEncoder`**, 그리고 "이 열들엔 표준화, 저 열들엔 원-핫"처럼 **열마다 다른 변환기를 붙이는 `ColumnTransformer`**. 둘을 묶은 전처리 하나를 `Pipeline` 첫 단계에 넣으면 앞 노트의 `[('scaler', …), ('model', …)]` 두 단계 그림이 그대로 유지된다. day14 Pipeline 노트 2단에 "`ColumnTransformer`+`OneHotEncoder` 열별 전처리"라고 키워드만 적어 둔 것이 이번에 수업 코드로 나왔다.

## 1. 배운 내용

### 1-1. `sns.load_dataset('penguins')` → `dropna().reset_index(drop=True)` — 결측 행을 버리고 번호를 다시 매긴다

```python
import seaborn as sns
df = sns.load_dataset('penguins')          # (344, 7)
df = df.dropna().reset_index(drop=True)    # (333, 7)
df.info()
```

day12 연습(`tips`)처럼 시본이 들고 있는 내장 자료를 읽는다. 열은 일곱 — `species`(Adelie·Chinstrap·Gentoo), `island`(Biscoe·Dream·Torgersen), `bill_length_mm`·`bill_depth_mm`·`flipper_length_mm`·`body_mass_g`(부리 길이·부리 깊이·날개 길이·몸무게), `sex`(Male·Female). 344마리 중 측정값이 빠진 2마리와 성별이 빠진 11마리가 있어 **`dropna()`로 결측이 하나라도 있는 행을 통째로 버리면 333마리**가 남는다. Fish는 결측이 없어 이 줄이 없었고, day14 이진 분류 연습에서는 `dropna(axis=1, how='all')`로 **열**을 버렸다. 이번엔 기본값(`axis=0`, `how='any'`) — 행 방향, 하나라도 비면 제거다.

`reset_index(drop=True)`가 붙은 이유는 행을 버리면 인덱스에 구멍이 생기기 때문이다(0, 1, 2, 4, 5, …). 뒤의 `train_test_split`은 위치로 자르니 구멍이 있어도 돌아가지만, 나중에 `df.loc[3]` 같은 접근이 어긋나고 데이터프레임끼리 붙일 때 번호가 안 맞는다. `drop=True`가 없으면 옛 번호가 `index`라는 새 열로 남아 특성에 섞여 들어간다. 결측 행을 버린 뒤 바로 번호를 다시 매기는 습관은 여기서 챙겨 둔다.

| 열 | 형 | 값 | 처리 |
| --- | --- | --- | --- |
| `species` | object | Adelie 146 · Gentoo 119 · Chinstrap 68 | **타깃** |
| `island` | object | Biscoe 163 · Dream 123 · Torgersen 47 | 범주형 특성 → 원-핫 |
| `sex` | object | Male 168 · Female 165 | 범주형 특성 → 원-핫 |
| `bill_length_mm` ~ `body_mass_g` | float64 | 32~60 mm · 13~22 mm · 172~231 mm · 2,700~6,300 g | 수치형 특성 → 표준화 |

### 1-2. 특성·타깃 구성과 `stratify` 분할 — 앞 노트와 같은 자리

```python
X = df.drop(columns=['species'])   # 섬·부리·날개·몸무게·성별 여섯 열
Y = df['species']
from sklearn.model_selection import train_test_split
X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size=0.2, random_state=42, stratify=Y)
# 266 / 67 — 학습 Adelie 117·Gentoo 95·Chinstrap 54, 테스트 29·24·14
```

`s-07.py`의 `fish.drop(columns=['Species'])`와 같은 꼴이다. 타깃만 빼면 **문자열 열이 그대로 `X`에 남는다**는 점이 이번의 출발점이고, 이 `X`를 아직 숫자로 바꾸지 않는다 — 바꾸는 일은 파이프라인 안에서 한다. `stratify=Y`로 세 종의 비율(44:36:20)이 테스트 67마리에 그대로 축소된다. 세 종은 Fish의 일곱 종보다 훨씬 균형이 좋아(가장 적은 Chinstrap도 68마리) day15 앞 노트 같은 "한 마리짜리 종"은 없다.

### 1-3. 수치형·범주형 열 목록을 따로 적는다

```python
num_features = ['bill_length_mm', 'bill_depth_mm', 'flipper_length_mm', 'body_mass_g']
cat_features = ['island', 'sex']
```

`ColumnTransformer`는 "어느 열에 무엇을 할지"를 이름 목록으로 받으므로 먼저 열을 두 묶음으로 나눈다. 수업 주석의 "복합형 파이프라인 위한 수치형과 범주형 특성 분리"가 이 두 줄이다. 리스트로 적어 두면 뒤에서 열을 추가·제거할 때 이 자리만 고치면 된다. `df.select_dtypes(include='number').columns`로 자동으로 뽑을 수도 있지만(2-1), 수업처럼 손으로 적는 편이 무엇이 어디로 가는지 눈에 보인다.

### 1-4. `OneHotEncoder(drop='first', sparse_output=False)` — 범주 하나를 0/1 열 여러 개로

```python
from sklearn.preprocessing import StandardScaler, OneHotEncoder
# OneHotEncoder: 범주형 자료들을 0과 1로 표현
#   drop='first'        : 첫 번째 범주의 열은 제외 — 모두 0인 행이 첫 범주를 뜻한다
#   sparse_output=False : 넘파이 배열로 반환
```

원-핫 인코딩은 범주 하나를 **범주 개수만큼의 0/1 열**로 펼치는 것이다. `island`는 세 값이니 `island_Biscoe`·`island_Dream`·`island_Torgersen` 세 열이 생기고, 행마다 자기 섬 열만 1이다. "Biscoe = 0, Dream = 1, Torgersen = 2"처럼 번호를 매기면 안 되는 이유는 로지스틱 회귀가 그 숫자에 **기울기를 곱하기** 때문이다 — Torgersen이 Biscoe의 두 배라는 뜻이 되어 버린다. 열을 쪼개면 섬마다 독립된 가중치를 갖는다.

`drop='first'`는 수업 주석의 표 그대로다. 세 섬에 열 셋을 다 두면 "세 열 중 정확히 하나가 1"이라 한 열이 나머지 둘로 완전히 결정된다(합이 항상 1). 이것이 day13 규제 노트에서 본 **다중공선성**이고, 절편이 있는 선형 모델에서는 첫 열을 빼도 정보를 잃지 않는다.

| `island` | `island_Dream` | `island_Torgersen` |
| --- | --- | --- |
| Biscoe | 0 | 0 |
| Dream | 1 | 0 |
| Torgersen | 0 | 1 |

| `sex` | `sex_Male` |
| --- | --- |
| Female | 0 |
| Male | 1 |

범주는 **알파벳순**으로 정렬된 뒤 첫 번째가 빠진다(`categories_` → `['Biscoe', 'Dream', 'Torgersen']`·`['Female', 'Male']`). 그래서 기준 범주는 Biscoe와 Female이 되고, 남은 열의 가중치는 "기준 대비 얼마나"라는 뜻이 된다. 값이 둘뿐인 `sex`는 열 하나로 충분하다 — 0이면 Female, 1이면 Male.

`sparse_output=False`는 결과를 넘파이 배열로 달라는 뜻이다. 기본값(`True`)은 희소 행렬(`scipy.sparse.csr_matrix`)을 돌려주는데, 범주가 수천 개라 대부분 0인 경우 메모리를 아끼려는 설계다. 여기선 열이 셋뿐이고 뒤에 표준화된 숫자 열과 **가로로 붙여야** 하므로 보통 배열로 받는 편이 보기 편하다.

### 1-5. `ColumnTransformer(transformers=[('식별자', 변환기(), 열목록)])` — 열마다 다른 변환기

```python
from sklearn.compose import ColumnTransformer
pp = ColumnTransformer(transformers=[
    ('num', StandardScaler(), num_features),                                  # 수치형 → 표준화
    ('cat', OneHotEncoder(drop='first', sparse_output=False), cat_features)   # 범주형 → 원-핫
])
```

`Pipeline`이 변환기를 **세로로**(앞 단계 출력이 다음 입력) 잇는다면, `ColumnTransformer`는 **가로로** 나눈다 — 열 묶음마다 다른 변환기를 적용하고 결과를 옆으로 이어 붙인다. 튜플 세 자리는 수업 주석의 `('식별자', 변환기(), 컬럼명목록)` 그대로다. `Pipeline`의 `(식별자, 인스턴스)`에 **세 번째 자리로 열 목록**이 추가된 모양이고, 역시 클래스가 아니라 `StandardScaler()`처럼 만든 인스턴스를 넣는다.

학습용 266마리를 넣으면 결과는 `(266, 7)` — 표준화된 숫자 4열 + 원-핫 3열이다. 열 이름은 `get_feature_names_out()`으로 확인할 수 있고 **`식별자__열이름`** 꼴이다(파이프라인의 `식별자__매개변수명`과 같은 밑줄 두 개 관례).

| 순서 | 열 | 어디서 |
| --- | --- | --- |
| 0~3 | `num__bill_length_mm` · `num__bill_depth_mm` · `num__flipper_length_mm` · `num__body_mass_g` | `StandardScaler` |
| 4~6 | `cat__island_Dream` · `cat__island_Torgersen` · `cat__sex_Male` | `OneHotEncoder` |

첫 두 마리로 보면 변환이 분명하다.

| | `island` | 부리 길이 | 부리 깊이 | 날개 | 몸무게 | `sex` | → 변환 뒤 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | Biscoe | 44.9 | 13.3 | 213 | 5,100 | Female | `[0.167, −1.992, 0.835, 1.082, 0, 0, 0]` |
| 2 | Dream | 50.7 | 19.7 | 203 | 4,050 | Male | `[1.227, 1.256, 0.121, −0.216, 1, 0, 1]` |

첫 마리는 Biscoe·Female이라 원-핫 세 자리가 전부 0이다 — "모두 0이면 첫 번째 범주"라는 주석이 이 행이다. 중요한 설계 하나는 **목록에 없는 열은 버려진다**는 것(`remainder='drop'` 기본). 여섯 열을 둘로 나눠 전부 적었으니 빠진 열은 없지만, 열 하나를 어느 목록에도 안 넣으면 조용히 사라진다(2-2).

### 1-6. `Pipeline([('pp', pp), ('model', LogisticRegression())])` — 전처리 묶음이 첫 단계

```python
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression
pipe = Pipeline([('pp', pp), ('model', LogisticRegression())])
pipe.fit(X_train, Y_train)          # 문자열이 섞인 원본 X_train을 그대로
Y_pred = pipe.predict(X_test)
print(Y_pred[:3])                   # ['Gentoo' 'Chinstrap' 'Adelie']
```

앞 노트의 `[('scaler', StandardScaler()), ('model', …)]`에서 **스케일러 자리에 `ColumnTransformer`가 들어간** 것뿐이다. `ColumnTransformer`도 `fit`·`transform`을 가진 변환기라 파이프라인의 중간 단계로 들어갈 수 있다. `fit`하면 안에서 `StandardScaler`는 네 열의 평균·표준편차를, `OneHotEncoder`는 두 열의 범주 목록을 **학습용으로만** 외우고, `predict(X_test)`는 그 기억으로 테스트를 변환한 뒤 모델에 넘긴다. 손으로 하면 스케일러 `fit`·`transform` 둘 + 인코더 `fit`·`transform` 둘 + `np.hstack`으로 붙이기 + 테스트에 같은 일 반복 — 여섯 줄이 넘는 일이 객체 하나에 들어간다.

| | 수업 `s-07.py` 파이프라인 | 이번 `s-08.py` |
| --- | --- | --- |
| 첫 단계 | `StandardScaler()` — 모든 열에 같은 변환 | `ColumnTransformer` — 열 묶음마다 다른 변환 |
| 입력 `X` | 숫자 6열 | 숫자 4열 + **문자 2열** |
| 변환 뒤 | 6열 | 7열(4 + 원-핫 3) |
| 모델 | `LogisticRegression(max_iter=1000, random_state=42)` | `LogisticRegression()` 기본값 |
| 타깃 | 7종 | 3종 |

`LogisticRegression()`에 아무 인자도 없다. 기본 `max_iter=100`인데 표준화 덕에 **13회**에 수렴해 경고가 없다(표준화를 빼면 1,000회를 줘도 경고가 난다 — 2-3). 3클래스이므로 앞 노트처럼 소프트맥스가 자동 선택되고 `coef_`는 `(3, 7)`이다.

### 1-7. `f1_score(average='macro')` — 결과는 1.0

```python
from sklearn.metrics import f1_score
print(f1_score(Y_test, Y_pred, average='macro'))   # 1.0
```

앞 노트의 4대 지표 중 **매크로 F1 하나**만 찍는다. 세 종의 F1을 단순 평균한 값이고, 결과는 1.0 — 테스트 67마리를 전부 맞혔다(정확도도 1.0, 혼동행렬 대각선 29·14·24). 학습 정확도 0.996(266마리 중 1마리 오답)이라 과대적합도 아니다. Fish 일곱 종이 0.81에서 출발했던 것과 대비되는데, 펭귄 세 종은 **부리 길이 × 부리 깊이** 두 치수만으로도 거의 갈라지는 자료다(Adelie 부리 짧고 깊음 · Chinstrap 길고 깊음 · Gentoo 길고 얕음, 종별 평균 39/18 · 49/18 · 48/15 mm). 교차 검증(`StratifiedKFold` 5겹)으로 돌려도 0.977·1.0·1.0·1.0·1.0 — 한 겹에서만 한 마리 틀린다.

점수가 1.0이면 "범주형 특성이 도움이 됐나"가 궁금해지는데, 이 자료에서는 **숫자 4열만으로도 1.0**이다. 그래서 이 수업의 요점은 점수가 아니라 **문자열 열이 있어도 파이프라인이 돌아가게 만드는 방법**이다. 다만 섬은 종과 강하게 얽혀 있다 — Gentoo는 Biscoe에만, Chinstrap은 Dream에만, Adelie는 세 섬 모두에 산다. `coef_`에서 `island_Dream` 가중치가 Chinstrap 쪽 +1.24·나머지 둘 −0.62인 것이 그 사실을 모델이 배웠다는 뜻이다.

| 종 | 부리 길이 | 부리 깊이 | 날개 길이 | 몸무게 | `island_Dream` | `island_Torgersen` | `sex_Male` |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Adelie | **−2.27** | 1.04 | −0.57 | −0.09 | −0.62 | 0.53 | 0.90 |
| Chinstrap | **1.95** | 0.38 | −0.47 | −0.96 | **1.24** | −0.35 | −0.74 |
| Gentoo | 0.33 | **−1.41** | **1.04** | **1.05** | −0.62 | −0.18 | −0.16 |

읽으면 Adelie는 부리가 짧을수록, Gentoo는 부리가 얕고 날개가 길고 무거울수록, Chinstrap은 부리가 길고 Dream 섬일수록 점수가 오른다. 표준화 덕에 숫자 4열의 가중치끼리는 크기 비교가 되고, 원-핫 열은 "기준 범주(Biscoe·Female) 대비"로 읽는다.

### 1-8. 흐름 한 장

```
penguins 344 → dropna().reset_index(drop=True) 333 → X(6열: 숫자 4 + 문자 2) · Y(3종)
  → train_test_split(stratify) 266/67
  → ColumnTransformer([('num', StandardScaler(), 숫자 4열),
                       ('cat', OneHotEncoder(drop='first', sparse_output=False), 문자 2열)])  → 7열
  → Pipeline([('pp', 위), ('model', LogisticRegression())]).fit(X_train, Y_train)
  → predict(X_test) ['Gentoo' 'Chinstrap' 'Adelie'] → f1_score(average='macro') 1.0
```

day14 Pipeline 노트(세로: poly → scaler → 모델) · day15 앞 노트(scaler → 모델 + 그리드서치) · 이번(가로 분기 `ColumnTransformer` → 모델). 세 노트를 합치면 "숫자와 문자가 섞인 표를 받아 → 열별 전처리 → 모델 → 교차 검증으로 하이퍼파라미터 탐색"이라는 실무 뼈대가 완성된다.

## 2. 추가로 알면 좋은 활용법

### 2-1. 열 이름을 자동으로 — `make_column_selector`

```python
from sklearn.compose import make_column_selector as selector
pp = ColumnTransformer([
    ('num', StandardScaler(), selector(dtype_include='number')),
    ('cat', OneHotEncoder(drop='first', sparse_output=False), selector(dtype_include='object'))
])
```

열 목록 자리에 **dtype으로 고르는 선택기**를 넣으면 열 이름을 손으로 적지 않아도 된다. 열이 30개쯤 되는 자료(day14 이진 분류 연습)에서 유용하고, 열이 추가돼도 코드가 안 바뀐다. 다만 `id`처럼 숫자지만 특성이 아닌 열이 섞여 들어가므로 `drop(columns=…)`는 그 전에 해 둔다.

### 2-2. `remainder`와 `set_output(transform='pandas')` — 빠진 열과 열 이름

```python
ColumnTransformer([('num', StandardScaler(), num_features)]).fit_transform(X_train).shape
# (266, 4) — island·sex가 조용히 사라진다 (remainder='drop' 기본)
ColumnTransformer([('num', StandardScaler(), num_features)], remainder='passthrough')
# (266, 6) — 나머지 열을 변환 없이 뒤에 붙인다: remainder__island · remainder__sex
pp.set_output(transform='pandas').fit_transform(X_train).head(2)   # 열 이름 달린 데이터프레임
```

두 목록 어디에도 안 넣은 열은 기본으로 **버려진다**. 의도치 않게 특성이 빠지는 실수가 생기기 쉬우니, 변환 뒤 `shape`나 `get_feature_names_out()`을 한 번 찍어 열 수를 확인하는 편이 안전하다. `remainder='passthrough'`는 나머지를 그대로 통과시키고, `remainder=StandardScaler()`처럼 변환기를 줄 수도 있다. `set_output(transform='pandas')`를 걸면 넘파이 대신 **열 이름 달린 데이터프레임**이 나와 1-5의 표를 코드로 바로 볼 수 있다(`sparse_output=False`가 전제).

### 2-3. 표준화를 빼면 — 수렴 경고가 돌아온다

```python
pp_raw = ColumnTransformer([('num', 'passthrough', num_features),
                            ('cat', OneHotEncoder(drop='first', sparse_output=False), cat_features)])
Pipeline([('pp', pp_raw), ('model', LogisticRegression(max_iter=1000))]).fit(X_train, Y_train)
# ConvergenceWarning — 1,000회를 다 쓰고도 수렴 못 함, 테스트 정확도 0.985
```

변환기 자리에 문자열 `'passthrough'`를 넣으면 그 열은 그대로 지나간다. 몸무게(수천 g)와 부리 깊이(십수 mm)의 크기 차가 그대로 들어가면 경사 하강법이 1,000회로도 끝나지 않고 점수도 조금 떨어진다. day13·day14에 적어 둔 "로지스틱 회귀 앞에는 표준화"가 범주형이 섞여도 그대로다 — **원-핫 열은 이미 0/1이라 표준화하지 않고**, 숫자 열만 한다. 수업 코드가 `'num'`에만 `StandardScaler`를 둔 이유다.

### 2-4. `drop='first'`를 안 쓰면 — 열이 둘 늘고 점수는 비슷

```python
OneHotEncoder(sparse_output=False)   # island_Biscoe·Dream·Torgersen + sex_Female·Male → 9열
```

세 열을 다 두면 변환 뒤 9열이 되고 테스트 정확도 0.985(L2 규제가 있어 다중공선성이 터지지는 않는다). 규제가 있는 로지스틱·릿지라면 둘 다 돌아가지만, 규제 없는 `LinearRegression`에서는 완전히 겹치는 열이 계수를 불안정하게 만든다. 트리 계열 모델에는 반대로 `drop` 없이 다 두는 편이 낫다 — 트리는 열 하나로 "Biscoe인가 아닌가"를 바로 가르고 싶어 하기 때문이다. `drop='if_binary'`를 주면 `sex`처럼 값이 둘인 열만 하나로 줄이고 셋 이상은 다 남긴다.

### 2-5. 처음 보는 범주 — `handle_unknown='ignore'`

```python
enc.transform(pd.DataFrame({'island': ['Mars'], 'sex': ['Male']}))
# ValueError: Found unknown categories ['Mars'] in column 0 during transform
OneHotEncoder(drop='first', sparse_output=False, handle_unknown='ignore')   # → [0, 0, 1]
```

인코더는 `fit` 때 본 범주만 안다. 서빙 중에 새 섬 이름이 들어오면 기본값은 **오류**다. `handle_unknown='ignore'`를 주면 모르는 값은 전부 0으로(기준 범주처럼) 처리하고 지나간다. 조용히 넘어가는 게 항상 좋은 건 아니라, 입력 검증을 따로 두고 인코더는 오류로 두는 쪽이 안전할 때도 있다. 서빙 그림은 day14 `s-05.py`와 같다 — `joblib.dump(pipe)` 하나에 스케일러의 평균·표준편차와 인코더의 범주 목록과 로지스틱 가중치가 전부 들어가고, 새 펭귄은 문자열 그대로 데이터프레임 한 행으로 넣는다.

```python
new = pd.DataFrame([{'island': 'Biscoe', 'bill_length_mm': 45.0, 'bill_depth_mm': 14.5,
                     'flipper_length_mm': 215, 'body_mass_g': 5000, 'sex': 'Male'}])
pipe.predict(new), pipe.predict_proba(new).round(3)   # ['Gentoo'], [[0.005 0.001 0.993]]
```

### 2-6. `pd.get_dummies`와 무엇이 다른가

```python
pd.get_dummies(X_train[cat_features], drop_first=True)   # island_Dream·island_Torgersen·sex_Male (bool)
```

day12 노트 2단에 적어 둔 판다스 방식도 같은 열을 만든다. 차이는 **기억**이다. `get_dummies`는 그때그때 보이는 값으로 열을 만들어, 테스트에 Torgersen이 없으면 그 열이 사라져 학습 때와 열 수가 달라진다. `OneHotEncoder`는 `fit` 때의 범주를 외우므로 테스트·서빙에서 열이 항상 같다. 탐색(EDA) 단계의 빠른 확인은 `get_dummies`, 모델 파이프라인은 `OneHotEncoder` — 자리가 다르다.

### 2-7. 그리드서치와 합치기 — `pp__cat__drop`까지 후보로

```python
param_grid = {'model__C': [0.01, 0.1, 1, 10, 100],
              'pp__cat__drop': ['first', None]}         # 식별자__식별자__매개변수명
GridSearchCV(pipe, param_grid, cv=StratifiedKFold(5, shuffle=True, random_state=42), scoring='f1_macro')
```

`ColumnTransformer` 안의 변환기 매개변수는 **밑줄 두 개를 두 번** 거쳐 닿는다 — 파이프라인 단계 `pp` → 변환기 식별자 `cat` → `drop`. 앞 노트의 `model__C`와 같은 규칙이 한 층 더 깊어진 것뿐이다. 전처리 선택까지 교차 검증으로 고를 수 있다.

## 3. 더 나아가 알면 좋은 것

### 3-1. 범주가 수백 개일 때 — 희소 행렬·빈도 묶기·타깃 인코딩

섬 셋·성별 둘은 원-핫으로 충분하지만, 우편번호나 상품 코드처럼 범주가 수천 개면 열이 수천 개가 된다. 그때는 `sparse_output=True`(기본)로 희소 행렬을 쓰고, `min_frequency=10`·`max_categories=20`으로 드문 범주를 `infrequent` 하나로 묶는다. 다른 길은 **`TargetEncoder`**(범주를 그 범주의 타깃 평균으로 바꿈 — 누수 방지를 위해 내부 교차 적합)와 **`OrdinalEncoder`**(순서가 있는 범주 — 소·중·대 — 를 0·1·2로). 트리·부스팅 모델은 `OrdinalEncoder`로도 잘 돌아가고, 선형 모델은 원-핫이나 타깃 인코딩이 맞다.

### 3-2. 결측을 버리지 않고 채우기 — `SimpleImputer`

`dropna()`로 11마리를 버렸는데, 결측이 많은 자료에서는 행을 버리는 비용이 크다. `ColumnTransformer` 안의 각 묶음을 다시 `Pipeline`으로 — 숫자는 `[('impute', SimpleImputer(strategy='median')), ('scale', StandardScaler())]`, 범주는 `[('impute', SimpleImputer(strategy='most_frequent')), ('onehot', OneHotEncoder(...))]` — 만들면 결측 채우기까지 파이프라인에 들어간다. 채우는 통계(중앙값·최빈값)도 학습용으로만 `fit`되니 누수가 없다. 가로(`ColumnTransformer`) 안에 세로(`Pipeline`)가 들어가는 중첩이 사이킷런 전처리의 일반형이다.

### 3-3. 전처리 그래프를 눈으로 — `set_config(display='diagram')`

주피터에서 `pipe`를 그냥 출력하면 `ColumnTransformer`의 분기와 `Pipeline`의 단계가 **상자 그림**으로 그려진다(`sklearn.set_config(display='diagram')`, 최근 버전은 기본). 전처리가 중첩될수록 코드보다 그림이 빠르다. 같은 그림이 서빙 쪽 문서가 되고, `pipe.named_steps['pp'].named_transformers_['cat'].categories_`처럼 안쪽 객체에 닿는 경로도 그림에서 읽을 수 있다.

### 3-4. 다음에 볼 키워드

- `dropna()` 행 vs `dropna(axis=1, how='all')` 열 · `reset_index(drop=True)` · 시본 내장 자료(`penguins`·`tips`·`titanic`)
- `OneHotEncoder(drop='first' | 'if_binary' | None, sparse_output, handle_unknown='ignore', min_frequency, max_categories)` · `categories_` 알파벳순 · 기준 범주와 다중공선성
- `ColumnTransformer([(식별자, 변환기, 열목록)], remainder='drop' | 'passthrough')` · `'passthrough'` · `make_column_selector(dtype_include)` · `get_feature_names_out()` `식별자__열` · `set_output(transform='pandas')`
- `Pipeline` 첫 단계로 `ColumnTransformer` · 폴드마다 인코더 범주 재학습 · `pp__cat__drop` 두 겹 밑줄 · `joblib.dump(pipe)` 서빙에 문자열 그대로 입력
- `pd.get_dummies` vs `OneHotEncoder`(기억 유무) · `OrdinalEncoder` · `TargetEncoder` · `SimpleImputer` 중첩 · `set_config(display='diagram')`

## 실습 파일

- `KDT_2026/2026_Python/day15/s-08.py` — "범주형(문자) 특성 갖는 학습 방법": 1) `sns.load_dataset('penguins')` → 2) `dropna().reset_index(drop=True)` · `info()` → 3) `X = df.drop(columns=['species'])` · `Y = df['species']` → 4) `train_test_split(…, test_size=0.2, random_state=42, stratify=Y)` → 5) `num_features` 4열 · `cat_features` 2열 → 6) `ColumnTransformer(transformers=[('num', StandardScaler(), num_features), ('cat', OneHotEncoder(drop='first', sparse_output=False), cat_features)])`(수업 주석: `drop='first'` 첫 범주 열 제외·모두 0인 행이 첫 범주, `sparse_output=False` 넘파이 배열) → `Pipeline([('pp', pp), ('model', LogisticRegression())])` → `fit` → `predict(X_test)[:3]` `['Gentoo' 'Chinstrap' 'Adelie']` → `f1_score(Y_test, Y_pred, average='macro')` 1.0. 자료는 파일 없이 시본이 내려받는다(344 → 333마리)

## 관련 노트

[[AI 정리본 인덱스]] · [[AI day15 Pipeline·StratifiedKFold·GridSearchCV로 다중 분류 C 탐색]] · [[AI day15 다중 분류 파이프라인 연습문제 풀이]] · [[AI day15 로지스틱 다중 분류와 혼동행렬·분류 리포트]] · [[AI day14 사이킷런 Pipeline으로 다항·표준화·회귀 묶기]] · [[AI day13 StandardScaler 표준화와 릿지·라쏘 규제]] · [[AI day14 로지스틱 이진 분류 연습문제 풀이]] · [[KDT_2026 학습 지도]]
