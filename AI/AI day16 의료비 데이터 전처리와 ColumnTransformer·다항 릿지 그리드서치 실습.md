---
출처: Claude 분석
원본: KDT_2026/2026_Python/ML_pracitce/total_practice/sci.py, ML_pracitce/total_practice/insurance.csv, ML_pracitce/total_practice/insurance_pipe.pkl, ML_pracitce/total_practice/insurance_metrics.pkl
작성일: 2026-11-12
tags: [학습, ai, python]
---

# AI day16 — 의료비 데이터 전처리와 ColumnTransformer·다항 릿지 그리드서치 실습

> 실습 파일: `ML_pracitce/total_practice/sci.py`, `ML_pracitce/total_practice/insurance.csv`
> 허브: [[AI 정리본 인덱스]] · 이전: [[AI day15 다중 분류 파이프라인 연습문제 풀이]] · 다음: (아직 없음)

day12부터 day15까지 조각조각 배운 도구를 **한 파일에 처음부터 끝까지** 다시 쓰는 종합 실습이다. 자료는 캐글의 의료보험 데이터 `insurance.csv`(1,338명 × 나이·성별·BMI·자녀 수·흡연·거주 지역 → 연간 의료비 `charges`)이고, 과제는 회귀 — 사람 정보로 **1년 의료비(달러)를 맞히기**다. 흐름은 "자료 살피기 → 중복 제거·공백 정리 → 수치형 표준화 + 범주형 원-핫 → 다항 항 → 릿지 → K-Fold 그리드서치 → `.pkl` 두 개 저장"이고, 마지막에 저장한 모델은 같은 폴더의 FastAPI 서버(`AppStart.py`·`Service.py`)가 읽어 웹 화면에서 예측에 쓴다. 이 노트는 그중 **모델을 만드는 쪽**(`sci.py`)만 다루고, 서버와 화면 쪽은 Python 폴더의 "Python day16 FastAPI StaticFiles로 학습 모델 예측 웹 서비스 만들기"에 따로 정리한다(학습 지도 경유).

## 1. 배운 내용

### 1-1. 자료 살피기 — `shape`·`info`·`isnull`·중복·`describe`·`value_counts`

```python
import pandas as pd
df = pd.read_csv('./ML_pracitce/total_practice/insurance.csv')

print(df.shape)                      # (1338, 7)
print(df.head())
df.info()                            # 열 이름, 자료형, 결측 아닌 개수
print(df.isnull().sum())             # 결측치 확인 → 전부 0
print('중복 행 수 :', df.shape[0] - df.drop_duplicates().shape[0])   # 1
print(df.describe())                 # 숫자 열 범위
print(df['sex'].value_counts())      # 문자 열 값 종류
print(df['smoker'].value_counts())
print(df['region'].value_counts())
```

| 확인한 것 | 결과 | 읽는 법 |
| --- | --- | --- |
| `shape` | `(1338, 7)` | 행 1,338명, 열 7개(특성 6 + 타깃 1) |
| `info()` | 수치 `age`·`bmi`·`children`·`charges`, 문자 `sex`·`smoker`·`region` | 문자 열 셋이 있으니 day15의 `ColumnTransformer`가 필요하다 |
| `isnull().sum()` | 전부 0 | 결측 처리 단계는 건너뛰어도 된다 |
| 중복 행 수 | 1 | `drop_duplicates()` 전후 행 수 차이로 센다 |
| `describe()` | `age` 18~64, `bmi` 16~53, `children` 0~5, `charges` 1,122~63,770(평균 13,270) | 타깃의 범위가 넓고 오른쪽으로 길다 |
| `value_counts()` | `sex` 676:662, `smoker` no 1,064 : yes 274, `region` 네 지역 ≈ 325씩 | 흡연자가 1/5 — 뒤에서 가장 큰 영향 변수가 된다 |

`df.shape[0] - df.drop_duplicates().shape[0]`는 "중복을 뺀 뒤 몇 줄 줄었는가"를 숫자 하나로 보는 관용구다. 중복 1건은 19세 남성·BMI 30.59·북서부·1,639달러 행이 두 번 들어 있는 것으로, 자료 수집 과정에서 흔히 생기는 모양이다.

### 1-2. 전처리 — 중복 제거·인덱스 리셋·문자 공백 제거

```python
df = df.drop_duplicates().reset_index(drop=True)

df['sex']    = df['sex'].str.strip()
df['smoker'] = df['smoker'].str.strip()
df['region'] = df['region'].str.strip()

print(df.shape)                      # (1337, 7)
print('수정된 중복 행 수 :', df.shape[0] - df.drop_duplicates().shape[0])   # 0
print(df.isnull().sum())
```

| 줄 | 하는 일 | 왜 |
| --- | --- | --- |
| `drop_duplicates()` | 완전히 같은 행 제거 → 1,337행 | 같은 행이 둘이면 그 사람이 두 배로 학습되고, 분할 때 훈련·테스트 양쪽에 들어가 점수가 부풀 수 있다 |
| `.reset_index(drop=True)` | 0부터 다시 번호 매기기 | 행을 빼면 인덱스에 빈 번호가 생긴다. `drop=True`가 없으면 옛 번호가 새 열로 남는다(day08) |
| `.str.strip()` | 앞뒤 공백 제거 | `'yes'`와 `'yes '`는 원-핫 인코더에게 **다른 범주**다. 지금 자료엔 공백이 없지만, 문자 열은 인코딩 전에 항상 한 번 다듬는 습관이다 |

세 줄을 같은 패턴으로 반복하는 대신 `for c in ['sex', 'smoker', 'region']: df[c] = df[c].str.strip()`로 줄일 수 있고, 2-1에서 한 번 더 정리한다. 전처리 뒤 `shape`·중복·결측을 **다시 찍어 확인**하는 것까지가 한 세트다.

### 1-3. 특성·타깃 분리와 8:2 분할

```python
X = df.drop(columns=['charges'])
Y = df['charges']

from sklearn.model_selection import train_test_split
X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size=0.2, random_state=42)
```

day15 `s-07.py`에서 쓰던 `drop(columns=[타깃])` 방식 그대로다. `X`에는 문자 열이 그대로 들어 있는데, 이것이 가능한 이유는 다음 단계의 `ColumnTransformer`가 파이프라인 안에서 열 이름으로 숫자·문자를 갈라 처리하기 때문이다. 회귀라 `stratify`는 없고, `random_state=42`로 분할을 고정해 두어야 교차 검증 점수와 테스트 점수를 나중에 다시 재현할 수 있다. 1,337행의 8:2는 훈련 1,069 · 테스트 268이다.

### 1-4. `ColumnTransformer` — 수치 3열 표준화 + 범주 3열 원-핫 → 8열

```python
from sklearn.preprocessing import StandardScaler, OneHotEncoder, PolynomialFeatures
from sklearn.compose import ColumnTransformer

num_features = ['age', 'bmi', 'children']
cat_features = ['sex', 'smoker', 'region']
pp = ColumnTransformer(transformers=[
    ('num', StandardScaler(), num_features),                                    # 수치형
    ('cat', OneHotEncoder(drop='first', sparse_output=False), cat_features)     # 범주형
])
```

| 변환기 | 들어가는 열 | 나오는 열 | 설명 |
| --- | --- | --- | --- |
| `StandardScaler` | `age`·`bmi`·`children` 3열 | 3열 (`num__age`·`num__bmi`·`num__children`) | 열마다 `(x − 평균) / 표준편차`. 다음 단계가 다항·릿지라 표준화가 **전제**다(day13) |
| `OneHotEncoder(drop='first')` | `sex`(2종)·`smoker`(2종)·`region`(4종) | 1 + 1 + 3 = 5열 (`sex_male`·`smoker_yes`·`region_northwest`·`southeast`·`southwest`) | 범주마다 0/1 열을 만들되 첫 범주는 떨어뜨린다 — 전부 0이면 첫 범주(`female`·`no`·`northeast`)라는 뜻 |

합쳐서 **8열**이 다음 단계로 넘어간다. `drop='first'`는 day15 펭귄 노트에서 본 것과 같은 이유다. 열 n개가 합이 항상 1이 되는 완전 공선성을 피하려는 것인데, 릿지 자체는 공선성에 강하지만 열을 하나 줄이면 뒤의 다항 항 수도 줄어 계산이 가벼워진다. `sparse_output=False`는 결과를 희소 행렬이 아니라 보통 넘파이 배열로 받겠다는 뜻이고, `PolynomialFeatures`가 뒤에 오므로 밀집 배열이 편하다.

### 1-5. `Pipeline` — 전처리 → 다항 → 릿지, 튜닝 자리는 비워 둔다

```python
from sklearn.pipeline import Pipeline
from sklearn.linear_model import Ridge

pipe = Pipeline([
    ('pp',    pp),
    ('poly',  PolynomialFeatures(include_bias=False)),   # degree 튜닝
    ('model', Ridge(random_state=42))                     # alpha 튜닝
])
```

| 단계 이름 | 객체 | 역할 | 그리드서치가 만질 자리 |
| --- | --- | --- | --- |
| `pp` | `ColumnTransformer` | 8열 숫자 행렬 만들기 | 없음 |
| `poly` | `PolynomialFeatures(include_bias=False)` | 8열의 곱·제곱 항 추가 | `poly__degree` |
| `model` | `Ridge(random_state=42)` | 규제 붙은 선형 회귀 | `model__alpha` |

day14 `s-04.py`에서는 `PolynomialFeatures` → `StandardScaler` → `LinearRegression` 순서였는데, 여기서는 **표준화가 다항보다 앞**에 있다. 범주형 원-핫과 수치 표준화를 `ColumnTransformer` 한 덩어리로 먼저 끝내야 다항 단계가 "숫자 행렬"을 받을 수 있기 때문이다. 표준화된 값끼리 곱한 교차항은 크기가 대체로 ±몇 범위에 머물러 릿지가 다루기에도 무리가 없다. 주석의 "degree 튜닝"·"alpha 튜닝"처럼 **파이프라인을 만들 때는 값을 비워 두고**, 어떤 값이 좋은지는 다음 단계가 자료로 정한다.

`degree`에 따라 다항 단계가 만드는 열 수는 8열 기준 1차 8 · 2차 44 · 3차 164이다(`include_bias=False`, 원-핫 0/1 열은 제곱해도 자기 자신이라 사실상 중복 열이 섞인다 — 릿지가 그 중복을 눌러 준다).

### 1-6. `KFold` + `GridSearchCV` — 3 × 5 = 15조합, 폴드 5개

```python
from sklearn.model_selection import KFold, GridSearchCV

param_grid = {
    'poly__degree' : [1, 2, 3],
    'model__alpha' : [0.01, 0.1, 1.0, 10.0, 100.0]
}
kf = KFold(n_splits=5, shuffle=True, random_state=42)
grid = GridSearchCV(estimator=pipe, param_grid=param_grid, scoring='r2', cv=kf, n_jobs=-1)
grid.fit(X_train, Y_train)
```

| 인자 | 값 | 뜻 |
| --- | --- | --- |
| `param_grid` | 차수 3개 × alpha 5개 | 15조합 전수 조사 — 키는 `단계이름__매개변수`(밑줄 둘) |
| `cv=kf` | `KFold(5, shuffle=True, random_state=42)` | 훈련 1,069행을 5조각으로, 섞어서, 재현 가능하게. 회귀라 `StratifiedKFold`가 아니라 `KFold`(day14) |
| `scoring='r2'` | 결정계수 | 회귀의 기본 점수. 분류였다면 `f1_macro`(day15) |
| `n_jobs=-1` | CPU 전부 | 15조합 × 5폴드 = 75번 학습을 병렬로 |

`grid.fit` 한 줄이 75번 학습하고, 조합마다 5폴드 평균 R²를 비교해 1등 조합으로 **훈련 자료 전체에 한 번 더 학습**한 모델을 `best_estimator_`에 넣어 둔다.

### 1-7. 최적 모델 평가 — `best_params_`·`best_score_`·훈련/테스트 R²

```python
best_model = grid.best_estimator_
print(grid.best_params_)   # {'model__alpha': 1.0, 'poly__degree': 2}
print(grid.best_score_)    # 0.8198  (교차검증 평균 R²)
print('train r2 : ', best_model.score(X_train, Y_train))   # 0.834
print('test  r2 : ', best_model.score(X_test,  Y_test))    # 0.8828
```

결과(이 노트에서 같은 코드로 확인)를 격자표로 펼치면 이렇다. 칸의 값은 5폴드 평균 R²다.

| degree \ alpha | 0.01 | 0.1 | 1.0 | 10 | 100 |
| --- | --- | --- | --- | --- | --- |
| 1 | 0.723 | 0.723 | 0.723 | 0.720 | 0.610 |
| 2 | 0.820 | 0.820 | **0.820** | 0.818 | 0.764 |
| 3 | 0.802 | 0.802 | 0.804 | 0.806 | 0.778 |

읽을 것 세 가지.

- **1차 → 2차에서 크게 오른다(0.72 → 0.82).** 의료비는 "흡연자이면서 BMI가 높을 때" 폭증하는 식으로 변수끼리 **곱해서 작용**한다. 2차 항에 `smoker_yes × bmi` 같은 교차항이 들어가면서 이 상호작용이 잡힌다. 3차는 오히려 조금 내려간다 — 164열은 1,069행에 비해 너무 많아 과대적합 쪽으로 기운다.
- **alpha는 0.01~1.0 사이에서 거의 평평하다.** 표준화된 특성에 규제를 조금 걸든 많이 걸든 차이가 없고, 100까지 가면 기울기를 너무 눌러 점수가 떨어진다. 동점일 때 사이킷런은 격자에서 먼저 나온 조합을 고르는데, 여기서는 반올림 전 미세한 차이로 `1.0`이 뽑혔다.
- **테스트 R²(0.883)가 교차 검증 평균(0.820)이나 훈련(0.834)보다 높다.** 보통은 반대를 기대하지만, 테스트 268행이 우연히 맞히기 쉬운 쪽으로 뽑혔다는 뜻이지 모델이 테스트를 봤다는 뜻은 아니다. 분할을 바꾸면(`random_state` 변경) 쉽게 뒤집히는 차이라, 서비스에 적을 "성능"으로는 **둘 다** 내보내는 편이 정직하다(1-8의 `metrics`가 그래서 두 값을 모두 담는다).

### 1-8. `joblib.dump` 두 번 — 모델과 지표를 따로 저장

```python
import joblib

joblib.dump(best_model, './ML_pracitce/total_practice/insurance_pipe.pkl')

metrics = {
    'test_r2'     : round(best_model.score(X_test, Y_test), 4),   # 0.8828
    'cv_r2'       : round(float(grid.best_score_), 4),            # 0.8198
    'best_params' : grid.best_params_                             # {'model__alpha': 1.0, 'poly__degree': 2}
}
joblib.dump(metrics, './ML_pracitce/total_practice/insurance_metrics.pkl')
print(metrics)
```

| 파일 | 담긴 것 | 쓰는 곳 |
| --- | --- | --- |
| `insurance_pipe.pkl` | `best_estimator_` — 전처리·다항·릿지가 **한 덩어리**로 든 파이프라인 | 서버가 `joblib.load`해서 원본 모양의 DataFrame을 그대로 `predict` |
| `insurance_metrics.pkl` | 딕셔너리 하나(테스트 R²·교차검증 R²·최적 파라미터) | 서버가 응답에 "모델 성능"으로 함께 실어 보낸다 |

파이프라인째로 저장하는 이유는 day14·15 연습에서 확인한 것과 같다. 서비스 쪽에서 `StandardScaler`의 평균·표준편차나 원-핫의 범주 목록을 다시 만들 필요 없이, 학습 때와 **똑같은 열 이름의 DataFrame 한 줄**만 넣으면 전처리부터 예측까지 한 번에 돌아간다. 지표를 별도 파일로 빼 둔 것은, 모델 객체 안에는 "얼마나 잘 맞히는가"가 들어 있지 않기 때문이다 — 점수는 테스트 자료가 있어야 나오는데 서버에는 테스트 자료가 없다. `float(grid.best_score_)`는 넘파이 실수를 파이썬 실수로 바꿔 JSON 직렬화와 피클 호환을 깔끔하게 하려는 습관이다.

### 1-9. 경로 — 어디서 실행하는가

파일 안의 경로가 전부 `./ML_pracitce/total_practice/…`로 시작한다. 즉 이 스크립트는 `total_practice` 폴더가 아니라 **`2026_Python` 저장소 루트에서 실행**하는 것을 전제한다(VS Code의 터미널이 열리는 자리). 저장도 같은 기준이라 `.pkl` 두 개가 `total_practice` 안에 생기고, 서버 쪽 `Service.py`도 같은 경로 문자열로 읽는다. 실행 위치가 다르면 `FileNotFoundError`가 나는데, 이는 코드가 아니라 작업 폴더 문제다 — day16 FastAPI 노트의 `import Controller`가 작업 폴더에 묶이는 것과 같은 성질이다.

### 1-10. 흐름 한 장 — 이 실습에 모인 노트들

| 단계 | 코드 | 처음 배운 곳 |
| --- | --- | --- |
| 자료 살피기 | `info`·`isnull`·`drop_duplicates`·`describe`·`value_counts` | Python day08 판다스 전처리 |
| 분할 | `train_test_split(test_size=0.2, random_state=42)` | AI day12 |
| 다항 항 | `PolynomialFeatures` | AI day13 |
| 표준화·릿지 | `StandardScaler`·`Ridge(alpha)` | AI day13 |
| 파이프라인 | `Pipeline([...])`·`단계__매개변수` | AI day14 |
| 교차 검증·격자 | `KFold`·`GridSearchCV(scoring='r2')` | AI day14 |
| 범주형 | `ColumnTransformer`·`OneHotEncoder(drop='first')` | AI day15 |
| 저장 | `joblib.dump` | AI day14 |

새로 등장한 문법은 없다. 이 실습의 요점은 **순서**와 **왜 그 순서인가**(표준화·원-핫을 먼저 묶고, 그 위에 다항, 그 위에 규제)이고, 결과 `.pkl`을 다른 프로그램이 쓰도록 넘기는 것까지가 머신러닝 쪽의 끝이다.

## 2. 추가로 알면 좋은 활용법

### 2-1. 문자 열 정리를 한 줄로, 대소문자까지

```python
cat_features = ['sex', 'smoker', 'region']
df[cat_features] = df[cat_features].apply(lambda s: s.str.strip().str.lower())
```

열 목록을 변수에 담아 두면 전처리와 `ColumnTransformer`가 같은 목록을 쓰게 되어 열을 빠뜨릴 일이 없다. `str.lower()`까지 걸어 두면 `'Yes'`·`'YES'`가 들어와도 한 범주로 모인다. 서비스에서 사용자 입력을 받을 때는 같은 정리를 서버 쪽 `predict` 직전에 한 번 더 하는 편이 안전하다.

### 2-2. `get_feature_names_out()`으로 8열의 이름 확인

```python
pp.fit(X_train)
print(pp.get_feature_names_out())
# ['num__age' 'num__bmi' 'num__children' 'cat__sex_male' 'cat__smoker_yes'
#  'cat__region_northwest' 'cat__region_southeast' 'cat__region_southwest']
```

`ColumnTransformer`가 만든 열이 몇 개이고 어느 범주가 떨어졌는지(`female`·`no`·`northeast`가 기준)를 눈으로 확인할 수 있다. `best_model.named_steps['poly'].n_output_features_`를 찍으면 2차에서 44열이 된 것도 보인다.

### 2-3. 격자 결과 전체를 표로 — `cv_results_`

```python
r = pd.DataFrame(grid.cv_results_)
print(r.pivot(index='param_poly__degree', columns='param_model__alpha', values='mean_test_score').round(3))
```

`best_params_`는 1등 하나만 알려 준다. 1-7의 격자표처럼 전체를 펼쳐 보아야 "alpha는 어디서든 비슷하다", "3차는 내려간다"처럼 **격자 바깥을 더 뒤질지** 판단이 선다. 1등이 격자 가장자리(예: `alpha=0.01`)에 있으면 범위를 넓혀 다시 돌리는 것이 정석이다.

### 2-4. 타깃이 오른쪽으로 긴 자료 — 로그 변환

```python
from sklearn.compose import TransformedTargetRegressor
import numpy as np

model = TransformedTargetRegressor(
    regressor=Ridge(alpha=1.0),
    func=np.log1p, inverse_func=np.expm1
)
```

`charges`는 1,122~63,770으로 오른쪽 꼬리가 길다. R²는 큰 값의 오차에 민감해 고액 환자 몇 명이 점수를 좌우한다. 타깃에 로그를 씌워 학습하고 예측 때 되돌리면 "비율" 오차가 고르게 다뤄지는 경우가 많다. `TransformedTargetRegressor`로 감싸면 파이프라인 바깥에서 변환·역변환을 자동으로 해 준다.

### 2-5. 학습 자료 없는 서버에서 "달러 오차"를 말하려면

```python
from sklearn.metrics import mean_absolute_error
metrics['test_mae'] = round(mean_absolute_error(Y_test, best_model.predict(X_test)), 0)
```

R² 0.88은 사용자에게 와닿지 않는다. 평균 절대 오차(MAE)를 함께 저장해 두면 서비스 화면에 "평균 ±2,600달러 오차" 같은 말을 쓸 수 있다. 지표 딕셔너리는 자유롭게 키를 늘릴 수 있으니, **서비스가 보여 줄 숫자는 학습 스크립트가 다 계산해 넘기는** 구조가 맞다.

### 2-6. 상호작용만 골라 넣기

```python
PolynomialFeatures(degree=2, interaction_only=True, include_bias=False)
```

2차 44열 중 상당수는 `age²`·`bmi²` 같은 제곱과 원-핫 열의 제곱(자기 자신)이다. `interaction_only=True`를 주면 서로 다른 열의 곱만 남겨 열 수가 줄고, 이 자료에서 중요한 `smoker × bmi`·`smoker × age`는 그대로 유지된다. 점수가 비슷하다면 열이 적은 쪽이 해석도 쉽고 빠르다.

## 3. 더 나아가 알면 좋은 것

### 3-1. 선형을 넘어서 — 트리 계열 회귀

의료비처럼 "흡연 여부에 따라 세상이 둘로 갈리는" 자료는 결정 트리·랜덤 포레스트·그래디언트 부스팅(`HistGradientBoostingRegressor`)이 다항 릿지보다 더 잘 맞히는 경우가 많다. 트리 모델은 표준화도 다항 항도 필요 없고 원-핫만 있으면 되며, 상호작용을 가지 분기로 자연히 배운다. 같은 `Pipeline`·`GridSearchCV` 틀에서 `model` 단계만 바꿔 비교해 보는 것이 다음 단계다.

### 3-2. 재현성과 실험 기록

`random_state=42`를 분할·폴드·릿지에 모두 박아 둔 덕에 이 노트의 숫자를 그대로 다시 얻을 수 있었다. 실험이 늘어나면 "어떤 격자로 어떤 점수가 나왔는지"를 파일로 남기는 도구(MLflow, 간단히는 `cv_results_`를 CSV로 저장)가 필요해진다. 지표를 `.pkl`로 따로 저장한 것은 그 가장 작은 형태다.

### 3-3. 저장한 모델의 수명 — 버전과 드리프트

`.pkl`은 저장한 사이킷런 버전과 다른 버전에서 열면 경고나 오류가 날 수 있다. 서비스 쪽 `requirements.txt`에 버전을 고정하거나, `skops`·ONNX처럼 버전에 덜 묶이는 형식을 쓴다. 또 자료 분포가 바뀌면(물가 상승으로 의료비 자체가 오르면) 모델은 그대로여도 예측이 어긋나기 시작한다(데이터 드리프트) — 주기적으로 다시 학습해 `.pkl`을 갈아 끼우는 흐름이 서비스 운영의 일부가 된다.

### 3-4. 다음에 볼 키워드

- `HistGradientBoostingRegressor`·`RandomForestRegressor` — 비선형 회귀
- `TransformedTargetRegressor`·`np.log1p` — 타깃 변환
- `cross_val_predict`·잔차 플롯 — 어디서 많이 틀리는지 보기
- `permutation_importance` — 어느 특성이 점수에 기여하는가
- `set_config(transform_output="pandas")` — 변환 결과를 열 이름 있는 DataFrame으로
- MLflow — 실험·모델 버전 기록

## 실습 파일

- `KDT_2026/2026_Python/ML_pracitce/total_practice/sci.py` — `pd.read_csv` → `shape`·`head`·`info`·`isnull().sum()`·중복 행 수(`shape[0] - drop_duplicates().shape[0]`)·`describe`·세 문자 열 `value_counts` → `drop_duplicates().reset_index(drop=True)`·`str.strip()` 세 줄 → `X = df.drop(columns=['charges'])`·`Y = df['charges']` → `train_test_split(0.2, 42)` → `ColumnTransformer([('num', StandardScaler(), 수치 3열), ('cat', OneHotEncoder(drop='first', sparse_output=False), 범주 3열)])` → `Pipeline([('pp', …), ('poly', PolynomialFeatures(include_bias=False)), ('model', Ridge(random_state=42))])` → `param_grid={'poly__degree': [1, 2, 3], 'model__alpha': [0.01, 0.1, 1.0, 10.0, 100.0]}`·`KFold(5, shuffle, 42)`·`GridSearchCV(scoring='r2', n_jobs=-1)` → `best_params_`·`best_score_`·훈련/테스트 `score` → `joblib.dump(best_model, 'insurance_pipe.pkl')`·`joblib.dump(metrics, 'insurance_metrics.pkl')`. 결과(이 노트에서 확인): `{'model__alpha': 1.0, 'poly__degree': 2}`, 교차검증 R² 0.8198, 훈련 0.834, 테스트 0.8828
- `KDT_2026/2026_Python/ML_pracitce/total_practice/insurance.csv` — 1,338행 × `age`·`sex`·`bmi`·`children`·`smoker`·`region`·`charges`, 결측 0, 중복 1
- `KDT_2026/2026_Python/ML_pracitce/total_practice/insurance_pipe.pkl`·`insurance_metrics.pkl` — 학습 산출물(파이프라인·지표 딕셔너리), FastAPI 서버가 읽는다

## 관련 노트

[[AI 정리본 인덱스]] · [[AI day15 다중 분류 파이프라인 연습문제 풀이]] · [[AI day15 ColumnTransformer·OneHotEncoder로 범주형 특성 파이프라인]] · [[AI day14 KFold 교차 검증과 GridSearchCV 하이퍼파라미터 탐색]] · [[AI day14 사이킷런 Pipeline으로 다항·표준화·회귀 묶기]] · [[AI day13 StandardScaler 표준화와 릿지·라쏘 규제]] · [[KDT_2026 학습 지도]]
