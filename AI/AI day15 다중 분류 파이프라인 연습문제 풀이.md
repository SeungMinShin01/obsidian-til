---
출처: Claude 분석
원본: KDT_2026/2026_Python/ML_pracitce/practice5.py
작성일: 2026-11-11
tags: [학습, ai, python]
---

# AI day15 — 다중 분류 파이프라인 연습문제 풀이

> 실습 파일: `ML_pracitce/practice5.py`
> 허브: [[AI 정리본 인덱스]] · 이전: [[AI day15 ColumnTransformer·OneHotEncoder로 범주형 특성 파이프라인]] · 다음: (아직 없음)

day14~15에 나온 도구를 **한 파일에 전부 모으는** 연습이다. 재료는 시본 내장 `diamonds`(53,940개 × 10열)에서 5,000개를 뽑은 표본이고, 맞힐 것은 다이아몬드의 **커팅 등급 `cut`** 다섯 가지(Fair·Good·Very Good·Premium·Ideal)다. 지시문 일곱 단계가 그대로 지금까지의 노트 순서다 — 적재·분리(`stratify`) → `ColumnTransformer`로 수치형 표준화 + 범주형 원-핫 → `Pipeline`에 `LogisticRegression` → 4대 지표와 혼동 행렬 → `StratifiedKFold` + `GridSearchCV(scoring='f1_macro')`로 `C` 탐색 → `joblib`로 저장·복원하고 **원본 형태의 새 표본 한 줄**을 바로 추론. 펭귄(`s-08.py`)에서는 모든 점수가 1.0이라 "돌아가는지"만 봤는데, 이번엔 매크로 F1이 **0.50 → 0.54**에서 멈추고 `Good` 등급의 재현율이 0.08에 그친다. 그래서 처음으로 "파이프라인이 돌아가는데도 점수가 낮으면 어디를 봐야 하나"를 생각하게 되는 자료다. 아래 숫자는 풀이 코드의 흐름을 그대로 돌려 확인한 값이다.

## 1. 배운 내용

### 1-1. 단계 1 — `sns.load_dataset('diamonds')` → `sample(n=5000)` → `cut`을 타깃으로

```python
import pandas as pd
import seaborn as sns

df = sns.load_dataset('diamonds')                              # (53940, 10)
df = df.sample(n=5000, random_state=42).reset_index(drop=True) # (5000, 10)

Y = df['cut']
X = df.drop(columns=['cut'])                                   # 9열 — 수치 7 + 문자 2
```

`diamonds`는 열이 열 개다. 수치형 일곱 — `carat`(무게), `depth`(깊이 비율 %), `table`(윗면 너비 비율 %), `price`(달러), `x`·`y`·`z`(mm 치수) — 과 범주형 셋 — `cut`(타깃), `color`(D가 최상 ~ J), `clarity`(IF가 최상 ~ I1). 5만 건을 전부 쓰면 그리드서치 4후보 × 5겹이 한참 걸려서 `sample(n=5000, random_state=42)`로 뽑고, 뽑힌 행의 원래 번호가 인덱스로 남아 있으니 `reset_index(drop=True)`로 0부터 다시 매긴다(펭귄 노트 1-1과 같은 이유). 뽑고 나면 `cut` 분포는 Ideal 1,953 · Premium 1,312 · Very Good 1,108 · Good 465 · Fair 162 — 대략 **39 : 26 : 22 : 9 : 3**으로, 일곱 종 Fish보다 더 쏠려 있다. 세 범주 열은 판다스 `category` 자료형으로 들어오는데(`df['cut'].cat.categories`를 찍으면 `Ideal, Premium, Very Good, Good, Fair` 순), 이 순서가 뒤에서 사이킷런이 쓰는 순서와 **다르다**는 점을 1-3·1-5에서 확인한다. 등급별로 수치 평균을 묶어 보면(`df.groupby('cut', observed=True)[['depth', 'table']].mean()`) `depth`는 Ideal 61.7 · Premium 61.3 · Very Good 61.9 · Good 62.4 · Fair 64.3, `table`은 Ideal 55.9 · Premium 58.7 · Very Good 58.0 · Good 58.6 · Fair 58.8 — 커팅 등급은 무게·가격보다 **비율(`depth`·`table`)** 로 갈리고, Ideal은 `table`이 가장 좁은 등급이다. 이 두 줄이 뒤의 점수를 해석하는 열쇠가 된다.

### 1-2. 단계 2 — `stratify=Y`로 8:2, 다섯 등급 비율 그대로

```python
from sklearn.model_selection import train_test_split
X_train, X_test, Y_train, Y_test = train_test_split(
    X, Y, test_size=0.2, random_state=42, stratify=Y)
# 학습 4000 / 테스트 1000 — 테스트: Ideal 391 · Premium 262 · Very Good 222 · Good 93 · Fair 32
```

Fair가 3 %라 `stratify` 없이 나누면 테스트 천 건에 Fair가 20개도 안 들어갈 수 있다. 붙이면 양쪽 모두 39 : 26 : 22 : 9 : 3이고, 테스트의 Fair는 정확히 32개다. 뒤에서 Fair의 정밀도·재현율이 32개 위에서 계산되니 소수 클래스일수록 이 인자가 점수의 **신뢰도**를 정한다.

### 1-3. 단계 3 — `ColumnTransformer`: 수치 7열 표준화 + 범주 2열 원-핫 → 20열

```python
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer

num_features = ['carat', 'depth', 'table', 'price', 'x', 'y', 'z']
cat_features = ['color', 'clarity']

preprocessor = ColumnTransformer([
    ('num', StandardScaler(), num_features),
    ('cat', OneHotEncoder(drop='first', sparse_output=False), cat_features),
])
# fit 뒤 get_feature_names_out() → 20개
# num__carat … num__z (7) · cat__color_E … cat__color_J (6) · cat__clarity_IF, SI1, SI2, VS1, VS2, VVS1, VVS2 (7)
```

펭귄 노트 1-5의 가로 결합 그대로다. 수치 7열은 `price`가 335~18,823달러, `depth`가 54~71 %, `z`가 1.4~6.3 mm라 단위가 제각각이니 `StandardScaler`, 문자 2열은 `OneHotEncoder`. `color`는 범주 7개에서 하나를 떨어뜨려 6열, `clarity`는 8개에서 7열, 합쳐 7 + 6 + 7 = **20열**이 모델에 들어간다. 눈여겨볼 것은 **무엇이 떨어졌는가**다. `OneHotEncoder`는 판다스 `category` 순서가 아니라 **문자열 정렬순**으로 범주를 세우므로 `color`의 기준은 `D`, `clarity`의 기준은 `I1`이다(`I1` < `IF` < `SI1` < … 문자열 비교). 즉 원-핫 열이 전부 0인 다이아몬드는 "D 컬러에 I1 투명도"라는 뜻이고, 각 열의 기울기는 그 기준 대비 효과다. 어느 범주가 기준인지는 `preprocessor.named_transformers_['cat'].categories_`를 찍어 보면 바로 나온다.

### 1-4. 단계 4 — `Pipeline([('preprocessor', …), ('model', LogisticRegression(max_iter=1000))])`

```python
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression

pipe = Pipeline([
    ('preprocessor', preprocessor),
    ('model', LogisticRegression(max_iter=1000, random_state=42)),
])
pipe.fit(X_train, Y_train)          # 문자열 열이 섞인 원본 DataFrame을 그대로
pipe.named_steps['model'].n_iter_   # [121]
pipe.score(X_train, Y_train)        # 0.652
```

`X_train`은 `color`·`clarity`가 문자열인 원본 그대로인데 `fit` 한 번에 표준화·인코딩·학습이 이어진다. 두 가지가 눈에 띈다. 첫째, 지시문이 `max_iter=1000`을 붙인 이유 — 20열에 4,000건이라 기본 100회로는 수렴하지 못하고 **121회**에서 멈춘다(펭귄은 13회). 둘째, 학습 세트 정확도가 **0.652**밖에 안 된다. 지금까지는 학습 점수가 0.98~1.0이었는데 이번엔 학습 자료조차 3분의 1을 틀린다. 과적합이 아니라 **과소적합** 쪽 신호이고, 이것이 이 연습의 분위기를 정한다.

### 1-5. 단계 5 — 4대 지표와 혼동 행렬: 정확도 0.63, 매크로 F1 0.50

```python
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from sklearn.metrics import ConfusionMatrixDisplay, classification_report
import matplotlib.pyplot as plt

Y_pred = pipe.predict(X_test)
Y_pred_proba = pipe.predict_proba(X_test)          # (1000, 5), 행 합 = 1

print(pipe.classes_)                               # ['Fair' 'Good' 'Ideal' 'Premium' 'Very Good']
print('정확도 : ', accuracy_score(Y_test, Y_pred))                     # 0.629
print('정밀도 : ', precision_score(Y_test, Y_pred, average='macro'))   # 0.539
print('재현율 : ', recall_score(Y_test, Y_pred, average='macro'))      # 0.511
print('F1 : ', f1_score(Y_test, Y_pred, average='macro'))             # 0.503
ConfusionMatrixDisplay.from_predictions(Y_test, Y_pred)
plt.show()
```

`classes_`가 **알파벳순**(`Fair, Good, Ideal, Premium, Very Good`)이다 — 판다스 `category`의 품질 순서(Ideal → Fair)가 아니다. `predict_proba`의 다섯 열도, 혼동 행렬의 행·열도 이 순서라서 "셋째 열 = Ideal 확률"로 읽어야 한다. 정확도 0.629인데 매크로 F1은 0.503으로 더 낮다. 둘의 차이가 클수록 소수 클래스에서 무너지고 있다는 뜻인데, 혼동 행렬(행 = 정답, 열 = 예측, `classes_` 순)을 보면 어디인지 바로 드러난다.

```text
             Fair  Good  Ideal  Prem  VGood
Fair     [    18     4     4     5      1 ]   ← 32 중 18
Good     [     7     4    24    29     29 ]   ← 93 중 4  — 거의 못 맞힘
Ideal    [     0     0   335    31     25 ]   ← 391 중 335
Premium  [     1     0    33   192     36 ]
VeryGood [     3     6    79    54     80 ]   ← 222 중 80, 79개가 Ideal로
```

`classification_report`로 보면 Ideal F1 0.77 · Premium 0.67 · Fair 0.59 · Very Good 0.41 · **Good 0.07**(정밀도 0.29·재현율 0.04). Good 93개 중 4개만 Good이라 했고 나머지는 Ideal·Premium·Very Good로 흩어졌다. 등급이 **순서가 있는 다섯 단계**라 이웃 등급끼리 섞이는 것이 자연스럽고(Good ↔ Very Good, Very Good ↔ Ideal), 선형 경계 하나로는 그 사이를 못 가른다. 테스트 앞 세 건의 확률표는 `[0, .004, .929, .038, .029]`(Ideal 93 %) · `[.007, .08, .11, .377, .426]`(Very Good 43 % — 근소) · `[.007, .089, .463, .135, .306]`(Ideal 46 %)로 셋 다 정답이지만, 둘째·셋째는 1등과 2등 확률이 바짝 붙어 있다. 앞 노트들의 0.95 이상 확신과는 사뭇 다른 그림이다.

### 1-6. 단계 6 — `StratifiedKFold` + `GridSearchCV(scoring='f1_macro')`: `C=10`, 0.50 → 0.54

```python
from sklearn.model_selection import StratifiedKFold, GridSearchCV
param_grid = {'model__C': [0.01, 0.1, 1.0, 10.0]}
cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
grid = GridSearchCV(pipe, param_grid, cv=cv, scoring='f1_macro', n_jobs=1)
grid.fit(X_train, Y_train)

print(grid.best_params_)      # {'model__C': 10.0}
print(grid.best_score_)       # 0.526  (교차 검증 매크로 F1 평균)

best_model = grid.best_estimator_
Y_pred = best_model.predict(X_test)
print(classification_report(Y_test, Y_pred))
```

`cv_results_`를 펼치면 C 0.01 → 0.405(±0.017), 0.1 → 0.497, 1.0 → 0.517, **10 → 0.526(±0.010)** 으로 규제를 풀수록 꾸준히 오르고 격자 끝에서 1등이다 — Fish 노트 2-1의 "1등이 격자 끝이면 격자를 늘린다"가 그대로 적용되는 상황(2-1에서 늘려 본다). 테스트에서 `best_model`은 정확도 0.643·매크로 F1 **0.536**. 리포트는 Fair 0.63 · Good **0.13**(재현율 0.08) · Ideal 0.78 · Premium 0.67 · Very Good 0.47 — Very Good이 0.41 → 0.47로 가장 많이 올랐고(222 중 80 → 99) Good은 4 → 7마리로 여전히 바닥이다. `C` 하나로 바꿀 수 있는 폭이 0.03 정도라는 것, 즉 **이 자료의 한계는 규제 강도가 아니라 모델의 모양**에 있다는 것이 이 단계에서 읽히는 결론이다. `n_jobs=1`은 병렬 없이 한 번에 하나씩 — 20후보(4 × 5겹)라 수 초면 끝난다.

### 1-7. 단계 7 — `joblib.dump`·`load`와 원본 형태 한 줄 추론

```python
import joblib
import numpy as np
joblib.dump(best_model, './diamond_pipeline.pkl')     # 약 5 KB
loaded_model = joblib.load('./diamond_pipeline.pkl')

sample = pd.DataFrame({'carat': [0.7], 'color': ['E'], 'clarity': ['SI1'], 'depth': [61.5],
                       'table': [55.0], 'price': [3000], 'x': [5.7], 'y': [5.75], 'z': [3.5]})
print('예측 등급 : ', loaded_model.predict(sample))    # ['Ideal']
proba = loaded_model.predict_proba(sample)
print(np.round(proba, 3))                               # [[0.  0.022 0.803 0.031 0.144]]
print('최대 확신도 : ', np.max(proba) * 100, '%')       # 80.3 %
```

day14 `s-05.py`·practice3와 같은 그림인데 이번 피클에는 **스케일러의 평균·표준편차와 인코더의 범주 목록까지** 들어 있다. 그래서 새 표본을 표준화도 인코딩도 하지 않은 원본 형태(`color='E'`, `clarity='SI1'` 문자열 그대로)의 DataFrame으로 넘기면 파이프라인이 안에서 `[−0.199, −0.192, −1.066, −0.224, −0.019, 0.025, −0.047, 1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0]` 20칸으로 바꿔 넣는다 — `table` 55는 평균(57.4)보다 꽤 작아 −1.07, `color_E`와 `clarity_SI1` 자리만 1. 결과는 Ideal 80.3 %, 다음이 Very Good 14.4 %. 1-1의 등급별 평균을 보면 Ideal은 `table`이 가장 작은 등급(55.9)이라 수긍이 간다. `np.max(proba)`는 다섯 열 중 가장 큰 값, 곧 `predict`가 고른 등급의 확률이고, `classes_[np.argmax(proba)]`로 등급 이름을 함께 꺼낼 수 있다.

### 1-8. 흐름 한 장 — 이 연습에 모인 노트들

```text
단계 1~2  적재·표본·stratify 분할          ← day14 이진 분류 노트, day15 다중 분류 노트
단계 3    ColumnTransformer(표준화 + 원-핫)  ← day15 ColumnTransformer·OneHotEncoder 노트
단계 4    Pipeline + LogisticRegression     ← day14 Pipeline 노트
단계 5    4대 지표(macro) + 혼동 행렬 그림   ← day15 다중 분류·혼동행렬 노트
단계 6    StratifiedKFold + GridSearchCV(f1_macro) + best_estimator_   ← day15 C 탐색 노트
단계 7    joblib dump/load + 원본 한 줄 추론  ← day14 KFold·GridSearchCV 노트(s-05), practice3
결과      학습 0.65 · 테스트 0.63 → C=10에서 0.64 · 매크로 F1 0.50 → 0.54 · Good 재현율 0.04 → 0.08
```

## 2. 추가로 알면 좋은 활용법

### 2-1. 격자 끝이 1등 — `C`를 더 늘려 봐도 평평하다

```python
# C=100 → 테스트 매크로 F1 0.547 / C=1000 → 0.544
```

Fish에서는 `C=100`에서 0.81 → 0.97로 뛰었지만, 여기선 10 → 100 → 1000으로 가도 0.536 → 0.547 → 0.544로 **평평**하다. 규제가 병목이 아니라는 뜻이다. 같은 자료에 `RandomForestClassifier(n_estimators=300)`을 모델 자리에 끼우면(전처리는 그대로) 매크로 F1 **0.71**·정확도 0.72로 한 번에 오른다. 등급 경계가 `depth`·`table`의 **구간**(너무 얕지도 깊지도 않은 범위가 Ideal)으로 정해지는데, 로지스틱 회귀는 "클수록 Ideal" 같은 **단조** 관계만 그릴 수 있어서다. 1-1의 등급별 평균 `depth`가 Ideal 61.7 · Premium 61.3 · Very Good 61.9 · Good 62.4 · Fair 64.3으로 Ideal이 양 끝이 아니라 **가운데**에 있는 것이 그 증거다. 파이프라인 덕에 모델만 바꿔 끼우면 되니, 이런 비교가 한 줄짜리 실험이 된다.

### 2-2. 표준화를 빼면 — 1,000회를 다 써도 수렴하지 않는다

수치 7열의 변환기를 `'passthrough'`로 바꿔 보면 `n_iter_`가 **1000**(한도 소진, `ConvergenceWarning`)이고 매크로 F1은 0.26으로 반토막이다. `price`가 수천 단위라 경사 하강이 그 열에 끌려다닌다. 펭귄 노트 2-3과 같은 실험이고, 20열·4,000건쯤 되면 "표준화 생략 = 모델 실패"가 된다.

### 2-3. 소수 클래스를 살리는 `class_weight='balanced'` — 맞바꿈이 있다

```python
LogisticRegression(max_iter=1000, random_state=42, C=10.0, class_weight='balanced')
# Good 재현율 0.08 → 0.28 (93 중 26), Fair 19 → 23
# 하지만 정확도 0.64 → 0.57, 매크로 F1 0.536 → 0.489
```

Good을 못 맞히는 게 아까우면 클래스별 가중치를 빈도 역수로 준다. Good·Fair는 더 찾아내지만 Ideal이 331 → 271로 크게 깎이고, 매크로 F1도 오히려 내려간다 — Good을 더 많이 **부르는** 대신 틀리게 부르는 것도 늘어나 정밀도가 떨어지기 때문이다. "어느 등급을 놓치면 안 되는가"라는 업무 기준이 없으면 균형 가중치가 항상 이득은 아니다. 다중 분류 노트 2-7의 메모를 실제로 돌려 본 결과다.

### 2-4. `color`·`clarity`는 사실 순서가 있다 — `OrdinalEncoder`와 비교

```python
from sklearn.preprocessing import OrdinalEncoder
order = [['J', 'I', 'H', 'G', 'F', 'E', 'D'],                       # 나쁜 → 좋은
         ['I1', 'SI2', 'SI1', 'VS2', 'VS1', 'VVS2', 'VVS1', 'IF']]
('cat', Pipeline([('ord', OrdinalEncoder(categories=order)), ('sc', StandardScaler())]), cat_features)
# 20열 → 9열, 테스트 매크로 F1 0.513 (원-핫 0.536)
```

컬러 D~J, 투명도 IF~I1은 **등급**이라 번호를 매겨도 의미가 생긴다. 원-핫 13열 대신 2열로 줄이고 "좋을수록 ~"라는 한 방향 기울기만 두는 방식인데, 이 자료에서는 원-핫이 0.02 더 높다 — 컬러·투명도가 커팅 등급과 거의 무관해서(2-6의 기울기표에서 두 범주 열의 크기가 모두 0.7 이하) 어느 쪽이든 큰 차이가 없다. 범주에 순서가 있으면 두 인코딩을 둘 다 시도해 보는 편이 맞고, `categories=`로 순서를 **직접** 주지 않으면 `OrdinalEncoder`도 알파벳순으로 번호를 매겨 의미가 어긋난다.

### 2-5. 서빙 때 흔한 두 오류 — 열 누락과 모르는 범주

```python
loaded_model.predict(sample.drop(columns=['z']))   # ValueError: columns are missing: {'z'}
sample.assign(color='Q')                            # ValueError: Found unknown categories ['Q'] in column 0 during transform
```

`ColumnTransformer`는 `fit` 때 본 열 이름을 기억하므로 새 표본에 열 하나가 빠지면 즉시 멈추고(열 순서가 바뀌는 건 괜찮다), `OneHotEncoder`는 학습 때 못 본 범주를 만나면 기본값(`handle_unknown='error'`)으로 멈춘다. 운영에서는 `handle_unknown='ignore'`(그 행의 원-핫을 전부 0 = 기준 범주 취급)로 바꾸거나, 입력 검증을 파이프라인 앞에 둔다. 펭귄 노트 2-5의 메모를 실제 오류 메시지로 확인한 것이다.

### 2-6. 기울기표 `(5, 20)` 읽을 때 주의 — `x`·`y`가 서로 상쇄한다

`best_model.named_steps['model'].coef_`를 20열 이름과 함께 펼치면 `x`가 Premium +11.1·Very Good −12.8, `y`가 Premium −15.2·Very Good +13.3처럼 **큰 값이 반대 부호로** 짝지어 있다. `x`와 `y`는 다이아몬드의 가로·세로 치수라 거의 같은 값(이 표본에서 상관 0.999, `z`·`carat`과도 0.97 이상)이고, 둘을 함께 넣으면 모델이 한쪽에 +, 다른 쪽에 −를 주며 서로 상쇄시킨다 — 다중공선성의 전형이다. 예측은 멀쩡하지만 기울기를 "원인"으로 읽으면 틀린다. day14 이진 분류 연습 노트 2-1에서 `radius`·`perimeter`·`area`에 대해 적어 둔 것과 같은 주의이고, 해석이 목적이면 `x`·`y`·`z` 중 하나만 남기거나 `carat`으로 대신한다. 반대로 해석이 선명한 열은 `table`(Ideal −2.1 — 윗면이 좁을수록 Ideal)과 `depth`(Fair +1.5 — 깊을수록 Fair)다.

## 3. 더 나아가 알면 좋은 것

### 3-1. 순서가 있는 등급 — 서열 회귀(ordinal regression)

Fair < Good < Very Good < Premium < Ideal은 명목 범주가 아니라 **서열**이다. 소프트맥스 다중 분류는 Good을 Ideal로 틀리는 것과 Very Good으로 틀리는 것을 같은 값으로 취급하지만, 서열 회귀(`mord` 라이브러리, 누적 로짓 모델)는 "한 칸 틀림"을 "세 칸 틀림"보다 가볍게 본다. 지표도 정확도 대신 평균 절대 오차(등급 차이)나 Cohen's κ(가중)로 본다.

### 3-2. 선형이 모자랄 때의 순서 — 특성 공학 → 비선형 모델 → 앙상블

2-1에서 확인했듯 이 자료의 한계는 경계의 모양이다. 선택지는 셋이다. ① `PolynomialFeatures`로 `depth²`·`table²`을 더해 "가운데가 Ideal"인 구간을 로지스틱이 그릴 수 있게 하기(day13의 제곱항 추가를 분류에 적용), ② 결정 트리·랜덤 포레스트처럼 구간을 바로 자르는 모델, ③ 그래디언트 부스팅(`HistGradientBoostingClassifier`·LightGBM·XGBoost) — 표 형태 자료의 분류 대회에서 가장 흔한 1등이다. 어느 쪽이든 `Pipeline`의 `'model'` 자리만 바꾸면 되고, `GridSearchCV`의 `param_grid` 키도 `model__max_depth`처럼 이름만 바뀐다.

### 3-3. 피클 밖으로 — 모델 서빙의 다음 단계

`joblib` 파일은 같은 사이킷런 버전에서만 안전하게 열린다(버전이 다르면 `InconsistentVersionWarning`). 운영 환경에서는 `requirements.txt`로 버전을 고정하고, 파이프라인을 FastAPI 같은 서버 뒤에 두어 JSON 한 줄을 DataFrame으로 바꿔 `predict_proba`를 돌려주는 식으로 감싼다. 입력 검증(열 이름·범주 집합·수치 범위)과 모델 버전 기록(MLflow 등)이 그 다음 키워드다.

### 3-4. 다음에 볼 키워드

- `sns.load_dataset('diamonds')` 53,940 × 10 → `sample(n=5000, random_state=42)` · `cut` 다섯 등급 39 : 26 : 22 : 9 : 3 · `stratify` 테스트 Fair 32개
- `ColumnTransformer` 7 + 6 + 7 = **20열** · `OneHotEncoder` 기준 범주는 **문자열 정렬순**(`color` D, `clarity` I1) — 판다스 `category` 순서와 다름 · `classes_` 알파벳순 `Fair, Good, Ideal, Premium, Very Good`
- `max_iter=1000` 필요(121회 수렴) · 학습 0.652 = 과소적합 신호 · 정확도 0.63 vs 매크로 F1 0.50 · Good 재현율 0.04 · 이웃 등급끼리 섞임
- `GridSearchCV(scoring='f1_macro')` C 10 → 0.526 · 격자 끝 1등 · 테스트 0.536 · `C=100`·`1000` 평평 · 랜덤 포레스트 0.71
- `joblib` 5 KB · 원본 형태 한 줄 → 20칸 변환 · Ideal 80.3 % · `np.max(proba)` · `classes_[np.argmax(proba)]`
- 표준화 생략 → 1,000회 미수렴 0.26 · `class_weight='balanced'` 맞바꿈 · `OrdinalEncoder(categories=)` 9열 0.513 · 열 누락·모르는 범주 오류 · `x`·`y` 상쇄 기울기
- 서열 회귀 · `PolynomialFeatures` 분류 적용 · 부스팅 · 사이킷런 버전 고정·FastAPI 서빙

## 실습 파일

- `KDT_2026/2026_Python/ML_pracitce/practice5.py` — "PythonML Practice5: 다중 분류" 지시문 단계 1~7과 풀이 코드: 1 `sns.load_dataset('diamonds')` → `sample(n=5000, random_state=42).reset_index(drop=True)` → `Y = df['cut']`·`X = df.drop(columns=['cut'])`, 2 `train_test_split(test_size=0.2, random_state=42, stratify=Y)`, 3 `num_features` 7열 `StandardScaler` + `cat_features` 2열 `OneHotEncoder(drop='first', sparse_output=False)`를 `ColumnTransformer`로 묶은 `preprocessor`, 4 `Pipeline([('preprocessor', …), ('model', LogisticRegression(max_iter=1000, random_state=42))])`에 원본 DataFrame 그대로 `fit`, 5 `predict`·`predict_proba`·`classes_`·`accuracy_score`·`precision_score`/`recall_score`/`f1_score(average='macro')`·`ConfusionMatrixDisplay.from_predictions`·`plt.show()`, 6 `param_grid={'model__C': [0.01, 0.1, 1.0, 10.0]}`·`StratifiedKFold(5, shuffle, 42)`·`GridSearchCV(scoring='f1_macro', n_jobs=1)`·`best_params_`·`best_score_`·`best_estimator_`로 `classification_report`, 7 `joblib.dump`/`load('./diamond_pipeline.pkl')`·원본 형태 한 줄 `sample` DataFrame → `predict`·`np.round(predict_proba, 3)`·`np.max(proba)*100`. 결과(이 노트에서 확인): 정확도 0.629·매크로 F1 0.503 → `C=10` 0.536, 표본 예측 Ideal 80.3 %. 피클은 실행 폴더 기준 `./diamond_pipeline.pkl`에 생긴다

## 관련 노트

[[AI 정리본 인덱스]] · [[AI day15 ColumnTransformer·OneHotEncoder로 범주형 특성 파이프라인]] · [[AI day15 Pipeline·StratifiedKFold·GridSearchCV로 다중 분류 C 탐색]] · [[AI day15 로지스틱 다중 분류와 혼동행렬·분류 리포트]] · [[AI day14 파이프라인·그리드서치·joblib 연습문제 풀이]] · [[AI day14 로지스틱 이진 분류 연습문제 풀이]] · [[KDT_2026 학습 지도]]
