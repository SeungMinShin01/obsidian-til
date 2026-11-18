---
출처: Claude 분석
원본: KDT_2026/2026_Python/ML_practice/pratice6.py
작성일: 2026-11-16
tags: [학습, ai, python]
---

# AI day18 — LightGBM·Optuna 의료비 회귀 연습문제 풀이

> 실습 파일: `ML_practice/pratice6.py`
> 허브: [[AI 정리본 인덱스]] · 이전: [[AI day18 Optuna 스터디·목적함수 설정과 판다스 category 타입]] · 다음: [[AI day19 KMeans 군집으로 학생 그룹 나누기와 엘보우·HDBSCAN]]

`s-12.py`의 중고차 가격 흐름을 **자료만 바꿔 처음부터 끝까지 다시 쓰는** 연습이다. 재료는 day16 종합 실습에서 다항 릿지로 맞혔던 그 의료보험 자료 `insurance.csv`(1,338명 × 나이·BMI·자녀 수·성별·흡연·지역 → 연간 의료비 `charges`)이고, 이번엔 원-핫·표준화·다항 항 없이 **범주 열을 `category` 타입으로 표시만 하고 LightGBM에 그대로** 넣는다. 지시문 여섯 단계가 곧 `s-12.py`의 1)~8) 순서다 — 적재·`category` 변환·X/Y 분리 → 8:2 분할 → `objective(trial)` 안에 `KFold(5)` + `early_stopping` → `TPESampler(seed=42)` 스터디 20회 → `best_params` + `best_n_estimators`로 최종 모델 → `joblib` 저장·로드·신규 고객 2명 예측. 지시문이 건 목표는 **테스트 R² 0.85 이상**이고, 이 노트에서 돌린 결과(optuna 5.1 · lightgbm 4.7)는 0.883이다. 자료 크기가 중고차(2,456대 · 7특성)보다 작고 특성도 여섯뿐이라 20회 × 5폴드가 4.5초면 끝나고, 결과 숫자가 수업 파일보다 훨씬 **평평하게** 나온다 — 그 평평함을 읽는 것이 이 연습의 후반부다.

## 1. 배운 내용

### 1-1. 단계 1 — `read_csv(URL)` → `charges > 0` 필터 → `category` 변환 → X/Y

```python
import pandas as pd
url = 'https://raw.githubusercontent.com/stedy/Machine-Learning-with-R-datasets/master/insurance.csv'
df = pd.read_csv(url)

df = df[df['charges'] > 0]
num_cols = ['age', 'bmi', 'children']
cat_cols = ['sex', 'smoker', 'region']
for col in cat_cols:
    df[col] = df[col].astype('category')
X = df[num_cols + cat_cols]
Y = df['charges']
```

day16에서는 같은 자료를 로컬 `insurance.csv`로 읽었고, 여기서는 `s-12.py`처럼 **GitHub raw URL**로 바로 읽는다. 1,338행 × 7열이고 `charges`는 최소 1,122 · 중앙값 9,382 · 평균 13,270 · 최대 63,770달러다 — `s-12.py`의 중고차 가격엔 경매 미입찰 0이 43대 있었지만, 이 자료엔 0이 없어서 `df[df['charges'] > 0]`은 **한 행도 걸러내지 않는다**(1,338행 그대로). 그래도 이 한 줄을 습관처럼 두는 이유는 지시문대로 "결측치나 이상치 방지"다 — 타깃이 0이나 음수인 회귀 자료가 들어와도 코드가 그대로 버틴다. day16에선 중복 1행을 `drop_duplicates`로 걷었는데 이 연습은 그 단계가 없어 1,338행이 유지된다(그래서 뒤의 분할 수가 1,070 · 268로 day16의 1,069 · 268과 한 행 다르다).

범주 열 셋은 고유값이 적다 — `sex` 2(`male` 676 · `female` 662), `smoker` 2(`no` 1,064 · `yes` 274), `region` 4(`southeast` 364 · 나머지 셋 324~325). day16에선 이 셋을 `OneHotEncoder(drop='first')`로 1 + 1 + 3 = 5열로 펼쳤다. 여기서는 `astype('category')`로 **열 셋을 그대로 둔 채 "범주형" 표시만** 한다 — `s-12.py`에서 `model` 126개를 펼치지 않으려고 쓴 방식인데, 고유값이 2~4개뿐인 열에도 똑같이 통한다. 변환 뒤 `df[col].cat.categories`를 찍으면 `['female', 'male']`·`['no', 'yes']`·`['northeast', 'northwest', 'southeast', 'southwest']`처럼 **알파벳순**으로 범주 목록이 잡히고, 각 행은 그 목록의 몇 번째인지(`cat.codes`)로 저장된다. 이 목록이 뒤 단계 6의 "타입을 `X_train[col].dtype`과 똑같이"에서 다시 중요해진다.

### 1-2. 단계 2 — `train_test_split(test_size=0.2, random_state=42)`, `stratify` 없음

```python
from sklearn.model_selection import train_test_split
X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size=0.2, random_state=42)
# (1070, 6) (268, 6)
```

회귀라 `stratify`는 없다(day14~15 분류 연습에서 늘 붙이던 인자). 훈련 1,070 · 테스트 268이고, `random_state=42`가 뒤의 `KFold`·`LGBMRegressor`·`TPESampler`와 같은 씨앗이라 이 노트의 숫자가 다른 컴퓨터에서도 그대로 나온다. 분할 뒤에도 `X_train.dtypes`에서 `sex`·`smoker`·`region`은 `category`로 남아 있다.

### 1-3. 단계 3 — `objective(trial)`: `KFold(5)` 루프 안에 `suggest_*` 여섯 개와 `early_stopping`

```python
import optuna
from lightgbm import LGBMRegressor, early_stopping
import numpy as np
optuna.logging.set_verbosity(optuna.logging.WARNING)

def objective(trial):
    from sklearn.model_selection import KFold
    cv = KFold(n_splits=5, shuffle=True, random_state=42)
    cv_r2_scores = []
    best_iterations = []
    for train_idx, val_idx in cv.split(X_train, Y_train):
        X_tr, X_val = X_train.iloc[train_idx], X_train.iloc[val_idx]
        Y_tr, Y_val = Y_train.iloc[train_idx], Y_train.iloc[val_idx]
        model = LGBMRegressor(
            n_estimators=1000,
            learning_rate=trial.suggest_float('learning_rate', 0.01, 0.1),
            num_leaves=trial.suggest_int('num_leaves', 10, 30),
            max_depth=trial.suggest_int('max_depth', 3, 10),
            min_child_samples=trial.suggest_int('min_child_samples', 10, 50),
            subsample=trial.suggest_float('subsample', 0.6, 1.0),
            subsample_freq=1, verbose=-1, random_state=42, n_jobs=-1,
            colsample_bytree=trial.suggest_float('colsample_bytree', 0.6, 1.0),
        )
        model.fit(X_tr, Y_tr, eval_set=[(X_val, Y_val)],
                  callbacks=[early_stopping(stopping_rounds=50, verbose=False)])
        r2 = model.score(X_val, Y_val)
        cv_r2_scores.append(r2)
        best_iterations.append(model.best_iteration_)
    trial.set_user_attr('best_n_estimators', int(np.mean(best_iterations)))
    return np.mean(cv_r2_scores)
```

몸통은 `s-12.py` 4-1·4-2·4-3과 같다 — 시도 하나가 들어오면 훈련 세트(1,070행)를 다섯 폴드(856 · 214)로 나누고, 폴드마다 `trial.suggest_*`가 뽑은 여섯 인자로 `LGBMRegressor`를 만들어 **그 폴드의 검증 묶음을 `eval_set`으로** 조기 종료 학습을 한 뒤, 폴드별 R²와 멈춘 트리 번호를 모아 평균 R² 하나를 돌려준다. 지시문의 "탐색 공간을 자유롭게 설계"에 수업 파일의 범위(보폭 0.01~0.1 · 잎 10~30 · 깊이 3~10 · 잎 최소 행 10~50 · 행/열 표본 0.6~1.0)를 그대로 썼다. `n_estimators=1000, random_state=42, verbose=-1, n_jobs=-1`은 지시문이 **고정**하라고 적은 넷이고, `subsample_freq=1`은 `subsample`이 실제로 작동하려면 함께 켜야 하는 스위치라(앞 노트 1-2의 아홉 인자 표) 고정 자리에 같이 둔다.

### 1-4. 단계 4 — `TPESampler(seed=42)` 스터디 20회: 최고 0.858, 트리 82그루

```python
sampler = optuna.samplers.TPESampler(seed=42)
study = optuna.create_study(direction='maximize', sampler=sampler)
study.optimize(objective, n_trials=20)            # 20회 × 5폴드 = 100번 학습, 4.5초
print('최적 하이퍼파라미터: ', study.best_params)
# {'learning_rate': 0.0519, 'num_leaves': 20, 'max_depth': 3, 'min_child_samples': 25, 'subsample': 0.723, 'colsample_bytree': 0.976}
optional_model = study.best_trial.user_attrs['best_n_estimators']
print('최적 트리: ', optional_model)               # 82
```

R²라 `direction='maximize'`, 재현을 위해 `TPESampler(seed=42)`다. 20회 시도의 기록을 `study.trials_dataframe()`으로 꺼내 보면 이렇다(이 노트에서 확인).

| 시도 | 교차검증 R² | `best_n_estimators` | `learning_rate` | `num_leaves` | `max_depth` | `min_child_samples` | `subsample` | |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 0 | 0.852 | 140 | 0.044 | 29 | 8 | 34 | 0.66 | 무작위 구간(0~9) 시작 |
| 1 | 0.854 | 329 | 0.015 | 28 | 7 | 39 | 0.61 | 보폭이 작아 329그루 |
| 3 | 0.847 | 115 | 0.049 | 16 | 7 | 15 | 0.72 | 20회 중 최저 |
| 5 | 0.857 | 77 | 0.065 | 13 | 3 | 48 | 0.99 | 무작위 구간 최고 |
| 7 | 0.854 | 377 | 0.013 | 29 | 5 | 37 | 0.73 | 최다 트리 |
| 11 | 0.858 | 69 | 0.071 | 27 | 3 | 22 | 0.74 | TPE 구간(10~19) — 깊이 3이 몰린다 |
| 13 | 0.858 | 73 | 0.060 | 22 | 3 | 33 | 0.73 | |
| 15 | 0.857 | 49 | 0.086 | 23 | 3 | 18 | 0.69 | 최소 트리 |
| 18 | 0.857 | 75 | 0.071 | 25 | 3 | 42 | 0.78 | |
| **19** | **0.858** | **82** | **0.052** | **20** | **3** | **25** | **0.72** | **최고 — `best_trial.number = 19`** |

19번 시도의 폴드별 R²는 `[0.829, 0.848, 0.903, 0.832, 0.880]`, 폴드별 `best_iteration_`은 `[68, 92, 83, 95, 76]`이라 평균 82가 `best_n_estimators`가 됐다. 수업 파일(중고차)과 나란히 놓고 읽히는 것이 셋이다.

- **점수가 평평하다.** 20회가 전부 0.847~0.858 사이, 폭이 0.011이다. 중고차에서는 0.606~0.636으로 폭 0.03이었고 `subsample` 0.6대가 눈에 띄게 나빴는데, 여기선 어느 조합이든 비슷하다. 특성 여섯 개 중 `smoker` 하나가 의료비의 대부분을 설명하는 자료라(1-5), 트리를 어떻게 자르든 "흡연자인가 → BMI 30 넘는가 → 나이"의 세 갈래만 잡으면 점수가 거기서 거기다.
- **TPE가 `max_depth=3`으로 수렴했다.** 무작위 10회(깊이 3~10 뒤섞임) 중에서 최고였던 5번이 깊이 3이었고, TPE 10회는 9·10·11·13·15·17·18·19번이 전부 깊이 3이다. `get_param_importances`도 `subsample` 0.41 · `min_child_samples` 0.35 · `max_depth` 0.21이고 나머지 셋은 0.01 아래다 — 중고차에서 `max_depth`가 0.002로 "안 쓰이는 인자"였던 것과 정반대다. 행이 856개뿐인 폴드에서 깊이를 더 주면 과적합으로 검증 점수가 깎이니, 탐색이 **얕은 트리 쪽으로** 간 것이다.
- **트리 수가 적다.** 최고 조합 82그루 · 20회 평균 118그루로, 중고차의 174그루·와인 분류의 310그루보다 훨씬 빨리 멈춘다. 자료가 작고 신호가 단순해서 손실이 금방 바닥에 닿는다. `learning_rate` 0.013~0.015로 뽑힌 1·7번만 329 · 377그루까지 갔다 — 보폭과 트리 수가 반비례한다는 앞 노트의 관례가 표에서 그대로 보인다.

### 1-5. 단계 5 — 최종 모델: 훈련 0.874 · **테스트 0.883**, 특성 중요도

```python
final_model = LGBMRegressor(
    random_state=42, verbose=-1, n_jobs=-1,
    **study.best_params,                 # 여섯 인자를 딕셔너리 전개로
    n_estimators=optional_model          # 1000이 아니라 82
)
final_model.fit(X_train, Y_train)
print('train r2: ', final_model.score(X_train, Y_train))   # 0.874
print('test r2: ', final_model.score(X_test, Y_test))      # 0.883  → 목표 0.85 달성
print(final_model.feature_name_)        # ['age', 'bmi', 'children', 'sex', 'smoker', 'region']
print(final_model.feature_importances_) # [220 150  67   9  75  26]
```

`**study.best_params`는 day03에서 본 `**kwargs` 전개다 — 딕셔너리의 키가 LightGBM 인자 이름과 같으니 그대로 풀린다. `n_estimators`를 `user_attrs`의 82로 두는 이유는 앞 노트 그대로 — 재학습엔 `eval_set`이 없어 조기 종료가 안 걸리므로, 폴드가 찾아 준 트리 수를 여기서 손으로 넣는다. 결과는 훈련 0.874 · 테스트 **0.883** · MAE 2,454달러로 지시문 목표 0.85를 넘긴다. 평균 의료비 13,270달러에 MAE 2,454면 18 %쯤 빗나가는 셈이고, 같은 자료에 day16 다항 릿지 파이프라인이 낸 테스트 0.883과 **같은 자리**다 — 원-핫·표준화·제곱항을 손으로 만들어 선형 모델에 먹인 것과, 범주 표시만 하고 얕은 트리 82그루를 쌓은 것이 같은 점수에 닿았다.

특성 이름은 `feature_name_`(LightGBM 고유)과 `feature_names_in_`(사이킷런 공통, day17 노트) 둘 다 있고 같은 목록을 돌려준다. `feature_importances_`는 **기본이 분할 횟수(`importance_type='split'`)** 라 `age` 220 · `bmi` 150 · `smoker` 75 순인데, 이 숫자만 보면 흡연이 셋째로 보인다. `booster_.feature_importance('gain')`으로 **손실을 얼마나 줄였나**를 보면 `smoker` 69.6 % · `bmi` 17.9 % · `age` 11.5 %고 `sex`·`region`·`children`은 1 % 아래다(이 노트에서 확인). 흡연 열은 `yes`/`no` 둘뿐이라 **한 번 자르면 끝**이라 횟수는 적지만, 그 한 번이 가장 크게 가른다 — 흡연자 평균 32,050달러 vs 비흡연자 8,434달러, 네 배 차이다. 연속값인 `age`·`bmi`는 트리마다 여러 번 잘게 쪼개지니 횟수가 많을 뿐이다. 중요도는 **어느 기준이냐**를 같이 봐야 한다.

### 1-6. 단계 6 — `joblib` 저장·로드와 신규 고객 2명: 4,429달러 / 44,540달러

```python
import joblib
joblib.dump(final_model, './ML_practice/gbm_model.pkl')
model = joblib.load('./ML_practice/gbm_model.pkl')     # 다른 .py 파일에서 읽는 상황을 가정

new_customers = pd.DataFrame([
    {'age': 28, 'bmi': 23.5, 'children': 0, 'sex': 'female', 'smoker': 'no',  'region': 'southwest'},
    {'age': 52, 'bmi': 34.2, 'children': 2, 'sex': 'male',   'smoker': 'yes', 'region': 'southeast'},
])
for col in cat_cols:
    new_customers[col] = new_customers[col].astype(X_train[col].dtype)   # 훈련 때의 범주 목록 그대로
new_customers = new_customers[num_cols + cat_cols]                       # 열 순서도 훈련과 같게

preds = model.predict(new_customers)
print('1번 고객 예측 의료비 : ', preds[0])   # 4429.44
print('2번 고객 예측 의료비 : ', preds[1])   # 44539.89
```

저장·로드는 day14 연습의 `joblib.dump`·`load` 그대로이고, `category` 열의 범주 목록도 모델(`booster_`)에 같이 저장된다. 예측은 28세 비흡연 여성 4,429달러 · 52세 흡연 남성(BMI 34.2) 44,540달러 — 비흡연자 평균 8,434 · 흡연자 평균 32,050, 그중 BMI 30 이상 흡연자 평균 41,558달러와 맞물리는 숫자다(이 노트에서 확인). 모델이 "흡연 + 비만 + 중년"의 세 갈래를 다 타고 내려가 가장 비싼 잎에 닿은 것이다.

이 단계에서 새로 배운 것은 **`astype(X_train[col].dtype)`** 이다. `s-12.py`는 새 차 두 대에 `astype('category')`를 그대로 썼는데, 그러면 범주 목록이 **새 자료 안의 값만으로** 만들어진다 — 두 고객의 `region`은 `['southeast', 'southwest']` 둘뿐이라 코드가 0·1이 되고, 훈련 때의 `['northeast', 'northwest', 'southeast', 'southwest']`에서는 2·3이었다. 지시문이 "범주형 카테고리 매핑 일치"라고 적은 것이 이 문제다. `X_train[col].dtype`은 `CategoricalDtype(categories=[…], ordered=False)` 객체라, 그걸 `astype`에 넘기면 새 자료도 **훈련 때의 범주 목록과 순서로** 코드가 매겨진다. 실제로는 LightGBM이 학습 때 본 범주 목록을 부스터에 기억해 두고 예측 때 다시 맞춰 주므로(`pandas_categorical`) 이 자료에선 두 방식의 예측이 같게 나오지만(이 노트에서 확인), 그 보정은 LightGBM의 호의일 뿐 다른 라이브러리·다른 전처리로 가면 없다 — **훈련 dtype을 그대로 꽂는 쪽이 어디서나 안전한 습관**이다. 열 순서를 `num_cols + cat_cols`로 다시 맞추는 줄도 같은 뜻이다: 서빙에서 들어오는 JSON은 키 순서가 보장되지 않는다.

### 1-7. 흐름 한 장 — 이 연습에 모인 것

| 단계 | 쓴 것 | 처음 나온 곳 |
| --- | --- | --- |
| 적재·필터 | `read_csv(URL)`, `df[df['charges'] > 0]` | day17 `read_csv(URL)`, day18 `s-12.py` 가격 0 걷기 |
| 범주 처리 | `astype('category')` → LightGBM 네이티브 범주 | day18 `s-12.py` |
| 분할 | `train_test_split(0.2, 42)` | day12 |
| 목적함수 | `KFold(5).split` + `iloc`, `suggest_float`·`suggest_int` 여섯, `early_stopping(50)`, `set_user_attr` | day14 `KFold`, day18 `s-11.py` 조기 종료, `s-12.py` Optuna |
| 스터디 | `TPESampler(seed)`, `create_study(maximize)`, `optimize(n_trials=20)` | day18 `s-12.py` |
| 최종 모델 | `**best_params` + `n_estimators=user_attrs[…]` | day18 `s-12.py` |
| 서빙 | `joblib.dump`·`load`, `astype(X_train[col].dtype)`, 열 순서 맞추기 | day14 연습 `joblib`, 이 연습 |

## 2. 추가로 알면 좋은 활용법

### 2-1. 튜닝 전과 후 — 기본 `LGBMRegressor()`는 0.866, 1000그루는 0.875

```python
base = LGBMRegressor(verbose=-1, random_state=42)          # 100그루 · 보폭 0.1 · 잎 31 · 깊이 제한 없음
base.fit(X_train, Y_train)
base.score(X_train, Y_train), base.score(X_test, Y_test)   # 0.941 / 0.866, MAE 2,615

m1000 = LGBMRegressor(**study.best_params, n_estimators=1000, random_state=42, verbose=-1)
m1000.fit(X_train, Y_train)
m1000.score(X_train, Y_train), m1000.score(X_test, Y_test) # 0.914 / 0.875
```

기본 모델도 테스트 0.866으로 이미 목표 0.85를 넘는다 — 이 자료는 쉬운 편이다. 튜닝이 바꾼 것은 점수 0.017보다 **훈련-테스트 간격**이다. 기본은 0.941 / 0.866으로 7.5점 벌어지고, 튠 모델은 0.874 / 0.883으로 테스트가 훈련보다 높다(day16에서도 같은 자료에서 테스트가 교차검증보다 높았다 — 268행이 우연히 맞히기 쉬운 쪽으로 뽑힌 분할). 깊이 3 · 잎 20 · 잎당 최소 25행이라는 얕은 설정이 과적합을 눌렀다는 뜻이다. 같은 `best_params`에 트리만 1000그루로 두면 0.914 / 0.875로 훈련이 오르고 테스트가 내려간다 — 조기 종료가 찾은 82그루를 넣어야 하는 이유가 중고차 때(0.933 / 0.709)보다 작지만 방향은 같다.

한 가지 일반 주의 — `suggest_*`로 뽑지 않고 목적함수 안에 **고정으로 적은 인자**(`subsample_freq=1` 등)는 `best_params`에 들어 있지 않다. 재학습할 때 `**best_params`만 풀면 그 인자들은 LightGBM 기본값으로 돌아가고, 특히 `subsample_freq`가 기본 0이면 `subsample` 값이 있어도 행 표본 추출이 **실제로는 꺼진 채** 학습된다. 교차 검증에서 고른 조합을 재학습에 그대로 재현하려면 고정 인자도 함께 적어 주는 편이 안전하다.

### 2-2. 범위를 자료에 맞게 — 깊이를 좁히고 `min_child_samples`를 열기

```python
max_depth=trial.suggest_int('max_depth', 2, 5),                 # 3이 계속 뽑혔으니 그 근처만
min_child_samples=trial.suggest_int('min_child_samples', 10, 100),   # 작은 자료엔 더 큰 값도
learning_rate=trial.suggest_float('learning_rate', 0.01, 0.3, log=True),   # 비율 간격으로 뽑기
```

1-4의 표가 말해 주는 대로 다음 탐색은 범위를 고쳐 돌리는 것이 맞다. `max_depth`는 3에 몰렸으니 2~5로 좁히고, 중고차에서 끝값 50에 걸렸던 `min_child_samples`는 위를 더 연다. `learning_rate`처럼 0.01과 0.1의 차이가 "10배"로 느껴지는 인자는 `log=True`를 주면 0.01~0.03 구간과 0.1~0.3 구간이 같은 비중으로 뽑힌다 — 선형 간격이면 0.01~0.1 안에서 큰 값 쪽이 과하게 많이 뽑힌다. 탐색 횟수를 20에서 50~100으로 늘리는 것은 그다음이다. 점수 폭이 0.011뿐인 자료에서 횟수만 늘려도 얻는 것이 적다.

### 2-3. `stopping_rounds`의 크기 — 30과 50은 무엇이 다른가

`early_stopping(stopping_rounds=N)`의 N은 "검증 손실이 N번 연속 안 좋아지면 멈춘다"의 N, 곧 참을성의 크기다. 작으면 일찍 멈추고(트리 수 ↓, 빠름, 잡음에 흔들려 너무 일찍 멈출 수도), 크면 더 기다린다(트리 수 ↑, 느림, 진짜 바닥을 찾을 확률 ↑). 이 자료처럼 60~90그루에서 바닥에 닿는 경우엔 30이든 50이든 `best_iteration_`은 거의 같은 자리고, `n_estimators` 상한 1000엔 어차피 닿지 않는다. 보폭을 0.01까지 작게 잡으면 손실이 천천히 내려가 잡음에 더 민감해지니 그때는 N을 50~100으로 두는 편이 안전하다.

### 2-4. 예측값에 "얼마나 틀릴 수 있나"를 붙이기 — 폴드별 모델과 분위 회귀

```python
# ① 폴드별 모델 다섯 개의 예측 퍼짐
preds = np.array([m.predict(new_customers) for m in fold_models])   # 목적함수 밖으로 모델을 모아 두었다면
preds.mean(axis=0), preds.std(axis=0)
# ② 분위 회귀 — 10 %·90 % 분위를 따로 학습
lo = LGBMRegressor(objective='quantile', alpha=0.1, **study.best_params, n_estimators=82)
hi = LGBMRegressor(objective='quantile', alpha=0.9, **study.best_params, n_estimators=82)
```

44,540달러라는 점 하나보다 "3만~5만 사이"가 서비스에선 더 쓸모 있을 때가 많다. 폴드별 모델을 버리지 않고 모아 두면 다섯 예측의 표준편차가 불확실성의 거친 추정이 되고, LightGBM의 `objective='quantile'`은 분위수 손실로 학습해 구간의 아래위를 따로 맞힌다. 의료비처럼 오른쪽 꼬리가 긴 타깃(최대 63,770 · 중앙값 9,382)엔 `TransformedTargetRegressor(func=np.log1p)`로 로그 변환 뒤 학습하는 것도 흔한 길이다 — 큰 값의 오차가 R²를 지배하는 것을 누그러뜨린다.

### 2-5. 서빙 때 흔한 두 오류, 다시 — 모르는 범주와 열 누락

day15 연습 2-5에서 원-핫 파이프라인 기준으로 적었던 것을 `category` 방식으로 다시 보면 — `region='north'`처럼 **훈련 때 없던 값**은 `astype(X_train[col].dtype)`을 거치면 `NaN`이 된다(목록에 없으니 코드 −1). LightGBM은 결측을 자체 처리하므로 오류 없이 예측이 나오지만, 그 예측은 "지역 정보 없음" 취급이라 서비스에선 입력 검증으로 먼저 걸러야 한다. 열이 빠지면 `predict`가 `categorical_feature do not match` 오류로 멈춘다. 가장 조용한 함정은 **열 순서**다 — 2번 고객의 `age`와 `bmi` 자리만 바꿔 넘기면 오류 없이 42,863달러가 나온다(이 노트에서 확인, 바른 순서는 44,540). LightGBM은 DataFrame이라도 열 **이름이 아니라 위치**로 읽으므로, `new_customers[num_cols + cat_cols]` 한 줄이 그 보험이다.

## 3. 더 나아가 알면 좋은 것

### 3-1. 선형 + 손 특성 vs 트리 + 원자료 — 같은 0.883의 두 길

day16 다항 릿지(원-핫 5열 + 수치 3열 표준화 → 2차 항 → 릿지 → 테스트 0.883)와 이 연습(범주 표시 + 얕은 LightGBM 82그루 → 0.883)은 결과가 같다. 선형 모델은 `smoker × bmi` 같은 **상호작용을 사람이 제곱항으로 만들어 줘야** 잡고, 트리는 "흡연 → BMI" 두 번 가르기로 **스스로** 잡는다. 특성이 여섯뿐이면 둘 다 닿지만, 특성이 수십 개로 늘면 손으로 만들 상호작용이 폭발하므로 트리 쪽이 먼저 편해지고, 반대로 행이 수백 개뿐이면 트리가 과적합하기 쉬워 선형 쪽이 안정적이다. 어느 쪽이 맞을지는 자료 크기와 특성 수가 정한다 — 둘 다 돌려 보고 교차 검증으로 고르는 것이 보통이다.

### 3-2. 설명 — `shap`으로 "이 고객은 왜 44,540달러인가"

수업 설치 명령에 `pip install optuna shap`으로 같이 깔린 `shap`은 예측 하나를 특성별 기여로 쪼개 준다. `shap.TreeExplainer(final_model).shap_values(new_customers)`를 찍으면 2번 고객의 44,540달러가 "기준 13,270 + 흡연 +2만 + BMI +7천 + 나이 +3천 …"처럼 나뉜다 — 1-5의 `gain` 중요도가 모델 전체의 평균이라면, SHAP은 **행 하나**의 설명이다. 의료비·보험료·대출 심사처럼 "왜 이 값인가"를 사람에게 보여 줘야 하는 자리에서 트리 모델과 거의 늘 같이 쓴다.

### 3-3. 스터디를 남기고 이어 돌리기 — `storage`와 `load_if_exists`

```python
study = optuna.create_study(study_name='insurance_lgbm', storage='sqlite:///optuna.db',
                            direction='maximize', load_if_exists=True)
study.optimize(objective, n_trials=30)    # 어제 20회에 이어 30회 더
```

`create_study`에 `storage`를 주면 시도 기록이 SQLite 파일에 쌓이고, 다음 날 같은 이름으로 열면 이어서 돈다. 20회로 모자라 보일 때 처음부터 다시 돌리지 않아도 되고, `optuna-dashboard optuna.db`로 브라우저에서 1-4의 표와 2-2의 중요도를 그림으로 본다.

### 3-4. 다음에 볼 키워드

- `CategoricalDtype`·`astype(X_train[col].dtype)`·`cat.set_categories`·`cat.codes` −1(모르는 범주), LightGBM `pandas_categorical`
- `feature_importances_`의 `importance_type='split'` vs `'gain'`, `booster_.feature_importance('gain')`, 퍼뮤테이션 중요도
- `suggest_float(log=True)`·`suggest_categorical`, 범위 재조정과 `n_trials`, `get_param_importances`
- `objective='quantile'`·`alpha`, `TransformedTargetRegressor(func=np.log1p)`, 폴드별 모델 앙상블
- `shap.TreeExplainer`·`summary_plot`·`waterfall`
- `storage='sqlite:///…'`·`load_if_exists`·`optuna-dashboard`
- 입력 검증(pydantic 모델, day16 FastAPI)과 `.pkl` 서빙의 연결

## 실습 파일

- `KDT_2026/2026_Python/ML_practice/pratice6.py` — "PythonML Practice6: LightGBM과 Optuna를 활용한 회귀 모델 해석" 지시문 단계 1~6과 풀이 코드: 1 `pd.read_csv(URL)` 의료보험 `insurance.csv`(1,338명 × 7열) → `df[df['charges'] > 0]`(걸러지는 행 없음) → `num_cols = ['age', 'bmi', 'children']`·`cat_cols = ['sex', 'smoker', 'region']` → `astype('category')` 세 열(`sex` 2 · `smoker` 2 · `region` 4) → `X = df[num_cols + cat_cols]`·`Y = df['charges']`, 2 `train_test_split(test_size=0.2, random_state=42)`(1,070 · 268), 3 `optuna.logging.set_verbosity(WARNING)` → `def objective(trial)`: `KFold(5, shuffle, 42)` → `cv.split` + `iloc` → `LGBMRegressor(n_estimators=1000, learning_rate=suggest_float(0.01~0.1), num_leaves=suggest_int(10~30), max_depth(3~10), min_child_samples(10~50), subsample(0.6~1.0), colsample_bytree(0.6~1.0), subsample_freq=1, verbose=-1, random_state=42, n_jobs=-1)` → `fit(eval_set=[(X_val, Y_val)], callbacks=[early_stopping(50, verbose=False)])` → 폴드별 `score`·`best_iteration_` → `set_user_attr('best_n_estimators', 평균)` → `return np.mean(R²)`, 4 `TPESampler(seed=42)`·`create_study(direction='maximize')`·`optimize(n_trials=20)` → `best_params`·`best_trial.user_attrs['best_n_estimators']`, 5 `LGBMRegressor(**best_params, n_estimators=최적 트리)` 재학습 → 훈련/테스트 R²·`feature_name_`·`feature_importances_`, 6 `joblib.dump('./ML_practice/gbm_model.pkl')`·`load` → 신규 고객 2명 DataFrame → `astype(X_train[col].dtype)`·`[num_cols + cat_cols]` → `predict`. 이 노트에서 돌린 결과(optuna 5.1 · lightgbm 4.7): 기본 `LGBMRegressor()` 0.941 / 0.866 · MAE 2,615, 20회 × 5폴드 4.5초 → 20회 전부 0.847~0.858 · 최고 19번 0.858 · 폴드별 R² `[0.829, 0.848, 0.903, 0.832, 0.880]` · `best_iteration_` `[68, 92, 83, 95, 76]` → `best_params` `{learning_rate 0.0519, num_leaves 20, max_depth 3, min_child_samples 25, subsample 0.723, colsample_bytree 0.976}` · 최적 트리 82, TPE 구간 8회가 `max_depth=3`, 인자 중요도 `subsample` 0.41 · `min_child_samples` 0.35 · `max_depth` 0.21, 최종 모델 훈련 0.874 · 테스트 **0.883** · MAE 2,454, `feature_importances_`(split) `[220 150 67 9 75 26]` vs gain `smoker` 69.6 % · `bmi` 17.9 % · `age` 11.5 %, 같은 조합 1000그루 0.914 / 0.875, 신규 고객 예측 4,429 / 44,540달러(흡연자 평균 32,050 · BMI 30 이상 흡연자 41,558), `astype('category')`와 `astype(X_train[col].dtype)` 예측 동일(LightGBM이 범주 목록을 다시 맞춤)
- `KDT_2026/2026_Python/ML_practice/gbm_model.pkl` — 단계 6에서 `joblib.dump`로 저장된 최종 모델(바이너리)

## 관련 노트

[[AI 정리본 인덱스]] · [[AI day18 Optuna 스터디·목적함수 설정과 판다스 category 타입]] · [[AI day19 KMeans 군집으로 학생 그룹 나누기와 엘보우·HDBSCAN]] · [[AI day18 LightGBM 매개변수 설정과 early_stopping 조기 종료]] · [[AI day16 의료비 데이터 전처리와 ColumnTransformer·다항 릿지 그리드서치 실습]] · [[AI day14 파이프라인·그리드서치·joblib 연습문제 풀이]] · [[KDT_2026 학습 지도]]
