---
출처: Claude 분석
원본: KDT_2026/2026_Python/day18/s-12.py
작성일: 2026-11-16
tags: [학습, ai, python]
---

# AI day18 — Optuna 스터디·목적함수 설정과 판다스 category 타입

> 실습 파일: `day18/s-12.py`
> 허브: [[AI 정리본 인덱스]] · 이전: [[AI day18 LightGBM 매개변수 설정과 early_stopping 조기 종료]] · 다음: (아직 없음)

`s-11.py`가 LightGBM 인자 아홉 개를 **손으로** 채우고 조기 종료로 트리 수만 자료에 맡기는 데서 끝났다면, `s-12.py`는 그 인자들을 **자동으로 고르는 도구** Optuna를 꺼내는 첫 파일이다. 자료도 과제도 바뀐다 — 와인 분류 대신 미국 중고차 2,499대(`USA_cars_datasets.csv`)의 **가격을 맞히는 회귀**이고, 특성에 수치형 둘(`year`·`mileage`)과 범주형 다섯(`brand`·`model`·`title_status`·`color`·`state`)이 섞여 있다. 이 파일에서 새로 배운 것은 셋이다. ① 가격이 0인 행을 걸러내는 한 줄, ② 범주형 다섯 열을 원-핫 인코딩이 아니라 **판다스 `category` 타입**으로 바꿔 LightGBM에 그대로 넘기는 방식, ③ `optuna.create_study(direction='maximize', sampler=TPESampler(seed=42))` → `study.optimize(objective, n_trials=20)`로 이어지는 **Optuna의 세 조각(목적함수·스터디·optimize)**. 수업 앞 시간(3h)에는 목적함수 `objective(trial)`의 몸통이 `pass`로 비어 있는 **골격**까지였고, 뒤 시간(4h)에 몸통이 채워진다 — 4) `KFold(5)`로 훈련 세트를 다시 다섯 번 쪼개 폴드마다 `LGBMRegressor`를 `trial.suggest_*` 인자로 만들고 `early_stopping`으로 학습한 뒤 R² 평균을 돌려주는 목적함수, 그리고 폴드별 `best_iteration_`의 평균을 `trial.set_user_attr('best_n_estimators', …)`로 시도에 적어 두고 5) `study.best_params`·`study.best_trial.user_attrs`로 꺼내는 마무리. 이 노트는 그 세 조각과 목적함수 몸통을 순서대로 정리하고, 같은 코드를 돌려 나온 숫자(이 노트에서 확인 — optuna 5.0 · lightgbm 4.7, 수업 주석의 결과와 일치)를 뒤에 붙인다.

## 1. 배운 내용

### 1-1. 중고차 자료 읽기와 가격 0 걸러내기

```python
import pandas as pd
url = 'https://raw.githubusercontent.com/rashida048/Datasets/master/USA_cars_datasets.csv'
df = pd.read_csv(url)

df = df[df['price'] > 0]
```

`pd.read_csv(URL)`은 day17 와인 자료와 같은 방식이다. 자료는 2,499행 × 13열(`price`·`brand`·`model`·`year`·`title_status`·`mileage`·`color`·`vin`·`lot`·`state`·`country`·`condition` + 이름 없는 인덱스 열)이고, 타깃 `price`는 평균 18,768달러 · 중앙값 16,900 · 최대 84,900인데 **최솟값이 0**이다 — 경매에서 아직 입찰이 없는 차 43대가 가격 0으로 들어가 있다. 가격 0은 "공짜 차"가 아니라 **값이 없다는 뜻**이라서 회귀 타깃으로 두면 모델이 그 43대를 맞히려 애쓰다 전체가 흔들린다. `df[df['price'] > 0]`은 day08 판다스의 불리언 필터링 그대로이고, 이 한 줄로 2,456행이 남는다. day16 의료비 실습에서 `drop_duplicates`로 중복 1행을 지운 것과 같은 자리의 전처리다 — **타깃에 말이 안 되는 값이 있는지 먼저 본다.**

### 1-2. 수치형·범주형 열 나누기와 도메인 특성

```python
num_cols = ['year', 'mileage']                                  # 수치형
cat_cols = ['brand', 'model', 'title_status', 'color', 'state'] # 범주형
# 모델 성능을 올리려면 도메인 지식으로 (계산식) 특성을 추가하는 것도 좋다
```

열 이름을 **두 리스트로 미리 나눠 두는** 것은 day15 `ColumnTransformer`에서 수치 열·범주 열에 다른 변환기를 걸 때 쓴 습관이다. 13열 중 7열만 골랐다 — `vin`(차대번호)과 `lot`(경매 번호)은 차마다 다른 식별자라 패턴이 없고, `country`는 거의 전부 `usa`, `condition`("10 days left")은 경매 남은 기간이라 가격과 무관하다. 다섯 범주 열의 고유값 수는 `title_status` 2(`clean vehicle` 2,334 · `salvage insurance` 122) · `brand` 28(포드 1,217대로 절반) · `state` 43 · `color` 47 · `model` 126이다.

주석의 **"도메인 지식의 계산식 특성"** 은 예컨대 `age = 2020 - year`(연식 → 차령), `mileage / age`(연평균 주행거리), `brand`별 평균 가격 같은 열을 사람이 만들어 넣는 **특성 공학**을 말한다. 트리 모델은 `year` 그대로도 잘 쪼개지만, 두 열의 비율처럼 트리가 한 번의 분할로 표현하기 어려운 관계는 미리 계산해 주면 성능이 오른다. day13의 `PolynomialFeatures`가 기계적으로 곱해 만든 특성이었다면, 이쪽은 "중고차 가격은 연식과 주행거리로 정해진다"는 **사람의 지식**으로 만든 특성이다.

### 1-3. 원-핫 대신 판다스 `category` 타입 — LightGBM의 네이티브 범주 처리

```python
for col in cat_cols:
    df[col] = df[col].astype('category')

X = df[num_cols + cat_cols]
Y = df['price']
from sklearn.model_selection import train_test_split
X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size=0.2, random_state=42)
```

day15·16에서 범주형은 늘 `OneHotEncoder`로 **열을 펼쳤다**(펭귄 섬 3종 → 열 2~3개). 이 자료에서 다섯 열을 원-핫으로 펼치면 `drop_first`를 해도 **243열**이 된다 — `model` 126개·`color` 47개가 그대로 열 수가 되기 때문이다. `astype('category')`는 열을 펼치지 않고 **열 하나를 "범주형"이라고 표시만 해 두는** 판다스 타입이다. 내부적으로는 고유값 목록(`cat.categories`, 예: `['acura', 'audi', 'bmw', …]`)과 각 행이 그중 몇 번째인지(`cat.codes`, 예: `[27, 8, 7, 8, 5]`)로 저장하므로 메모리도 문자열보다 작다.

| 방식 | 열 수 (이 자료) | 모델에 들어가는 것 | 쓰는 곳 |
| --- | --- | --- | --- |
| `OneHotEncoder` | 7 → 243 | 범주마다 0/1 열 | 선형 모델·로지스틱 — 범주 사이에 순서가 없다는 것을 보장 |
| `astype('category')` | 7 그대로 | 정수 코드 + "범주형" 표시 | **LightGBM·CatBoost·XGBoost(`enable_categorical`)** — 트리가 범주 묶음을 직접 나눔 |
| `LabelEncoder`/정수 코드만 | 7 그대로 | 정수 코드 (표시 없음) | 트리가 코드 크기로 자르므로 `acura < audi < bmw` 같은 가짜 순서가 생김 — 권장하지 않음 |

LightGBM은 DataFrame의 `category` 열을 **자동으로 범주형으로 인식**한다(`categorical_feature='auto'` 기본). 범주형으로 인식된 열은 "이 브랜드 묶음이면 왼쪽, 아니면 오른쪽" 식으로 **여러 범주를 한 번에 가르는 분할**을 찾는다 — 범주를 타깃 평균 순으로 정렬한 뒤 최적 경계를 찾는 Fisher 방식이라, 원-핫의 "범주 하나씩 묻기"보다 트리가 얕고 빠르다. 그래서 수업 주석이 "원핫인코딩이 아닌 판다스 카테고리 타입 변경"이라고 적은 것이다. 실제로 돌려 보면(이 노트에서 확인) 기본 `LGBMRegressor`가 `category` 7열로 테스트 R² **0.729**, 같은 모델에 243열 원-핫을 넣으면 0.663, 수치 두 열만 넣으면 0.191이다 — 범주 열이 가격 설명의 대부분이고, 그 범주 열을 **펼치지 않고 넘기는 쪽이 더 낫다.** `train_test_split`에는 `stratify`가 없다 — 회귀라서 층화할 클래스가 없다. 분할 뒤에도 `X_train.dtypes`를 보면 다섯 열이 `category`로 남아 있다(판다스가 행을 잘라도 타입은 유지).

### 1-4. Optuna의 세 조각 — 목적함수·스터디·`optimize`

```python
import optuna
optuna.logging.set_verbosity(optuna.logging.WARNING)   # 시도마다 찍는 INFO 로그를 끄고 경고만

def objective(trial):      # 4) 목적함수 — trial을 받아 점수 하나를 돌려준다 (몸통은 1-5)
    ...

sampler = optuna.samplers.TPESampler(seed=42)          # 3) 다음 후보를 고르는 전략 + 재현용 씨앗
study = optuna.create_study(direction='maximize', sampler=sampler)   #    회귀 R²를 쓸 예정이라 최대화
study.optimize(objective, n_trials=20)                 #    목적함수를 20번 부른다
```

`pip install optuna` 뒤 쓰는 Optuna는 **하이퍼파라미터 자동 탐색** 라이브러리다. day14의 `GridSearchCV`가 "격자에 적힌 조합을 전부 돌려 보는" 방식이었다면, Optuna는 "한 조합을 돌려 점수를 보고 → 그 결과를 참고해 다음 조합을 고른다"를 반복한다. 코드는 세 조각으로 나뉜다 — 수업 주석 번호로는 2) 로그 설정, 4) 목적함수, 3) 스터디 생성과 `optimize`다.

| 조각 | 코드 | 역할 |
| --- | --- | --- |
| **목적함수** `objective(trial)` | `def objective(trial): … return 점수` | Optuna가 **매 시도마다 부르는 콜백**. `trial` 객체에서 인자 후보를 받아(`trial.suggest_*`) 모델을 학습·평가하고 **숫자 하나**를 돌려준다 |
| **스터디** `create_study` | `direction='maximize'`/`'minimize'`, `sampler=` | 시도들의 기록장. `direction`은 돌려준 숫자를 **키울지 줄일지** — R²·정확도·F1은 `maximize`, MAE·RMSE·logloss는 `minimize` |
| **최적화** `study.optimize` | `(objective, n_trials=20)` | 목적함수를 `n_trials`번 부른다. 끝나면 `study.best_params`·`study.best_value`·`study.best_trial`에 최고 기록이 남는다 |

**목적함수가 콜백**이라는 점이 day03의 `map`·`filter`에 넘긴 함수, day18 앞 노트의 `early_stopping` 콜백과 같은 구조다 — 내가 부르는 게 아니라 **Optuna가 `trial`을 만들어 넣어 준다.** 그래서 매개변수가 `trial` 하나뿐이고, 자료(`X_train` 등)는 바깥 변수를 그대로 쓴다. `direction`을 회귀 R²에 맞춰 `'maximize'`로 둔 것은, 목적함수가 돌려줄 숫자가 "클수록 좋은" 값이라는 약속이다 — 방향을 잘못 두면 Optuna가 **가장 나쁜** 조합을 열심히 찾는다.

**`TPESampler(seed=42)`** 는 다음 후보를 고르는 전략이다. TPE(Tree-structured Parzen Estimator)는 지금까지의 시도를 "점수가 좋았던 쪽"과 "나빴던 쪽"으로 나눠 각각의 분포를 추정하고, **좋은 쪽에 속할 확률이 높은 값**을 다음 후보로 뽑는다. 기본 샘플러도 TPE이지만, `seed`를 주려면 이렇게 객체를 만들어 넘겨야 한다 — `random_state=42`와 같은 뜻으로, 씨앗이 없으면 돌릴 때마다 후보 순서가 달라져 `best_params`도 달라진다. 처음 10번(`n_startup_trials=10` 기본)은 아직 참고할 기록이 없어 **무작위**로 뽑고, 11번째부터 TPE가 작동한다.

**`set_verbosity(WARNING)`** 는 LightGBM의 `verbose=-1`과 같은 자리의 설정이다. 기본 INFO 레벨이면 시도마다 `Trial 3 finished with value: 0.55 and parameters: {…}` 한 줄씩 20줄이 찍히므로, 경고만 남기고 끈다.

### 1-5. 목적함수 몸통 — 폴드마다 `suggest_*`로 모델을 만들고 조기 종료로 학습

```python
from lightgbm import LGBMRegressor, early_stopping
import numpy as np

def objective(trial):
    # 4-1 교차 검증 KFold — 훈련 세트 안에서 다시 훈련용/검증용으로 다섯 번 나눈다
    from sklearn.model_selection import KFold
    cv = KFold(n_splits=5, shuffle=True, random_state=42)
    cv_r2_scores = []        # 폴드별 검증 점수
    best_iterations = []     # 폴드별 최적 트리 번호
    for train_idx, val_idx in cv.split(X_train, Y_train):
        X_tr, X_val = X_train.iloc[train_idx], X_train.iloc[val_idx]
        Y_tr, Y_val = Y_train.iloc[train_idx], Y_train.iloc[val_idx]
        model = LGBMRegressor(
            n_estimators=1000,                                             # 상한만 — 트리 수는 조기 종료가 정한다
            learning_rate=trial.suggest_float('learning_rate', 0.01, 0.1), # trial.suggest_XXX('이름', 시작, 끝)
            num_leaves=trial.suggest_int('num_leaves', 10, 30),
            max_depth=trial.suggest_int('max_depth', 3, 10),
            min_child_samples=trial.suggest_int('min_child_samples', 10, 50),
            subsample=trial.suggest_float('subsample', 0.6, 1.0),
            colsample_bytree=trial.suggest_float('colsample_bytree', 0.6, 1.0),
            subsample_freq=1, verbose=-1, random_state=42, n_jobs=-1,       # class_weight는 회귀라 없음
        )
        # 4-2 폴드별 학습 — 검증 폴드를 eval_set으로 두고 50번 개선 없으면 멈춤
        model.fit(X_tr, Y_tr, eval_set=[(X_val, Y_val)],
                  callbacks=[early_stopping(stopping_rounds=50, verbose=False)])
        # 4-3 폴드별 성능 저장
        cv_r2_scores.append(model.score(X_val, Y_val))
        best_iterations.append(model.best_iteration_)
    trial.set_user_attr('best_n_estimators', int(np.mean(best_iterations)))  # 폴드별 최적 트리 수의 평균을 시도에 적어 둔다
    return np.mean(cv_r2_scores)                                             # 검증 R² 평균 하나를 돌려준다
```

몸통은 수업 주석의 4-1·4-2·4-3 세 단계다. 한 시도(`trial`)가 들어오면 ① `KFold`로 훈련 세트를 다섯 번 나누고, ② 폴드마다 `trial.suggest_*`가 뽑아 준 인자로 `LGBMRegressor`를 만들어 **그 폴드의 검증 묶음을 `eval_set`으로** 조기 종료 학습을 하고, ③ 폴드별 R²와 멈춘 트리 번호를 모아 **평균 R² 하나**를 돌려준다. day14의 `cross_val_score` 한 줄이 하던 일을 `for train_idx, val_idx in cv.split(…)`으로 직접 푼 모양인데, 그렇게 손으로 쪼갠 이유가 바로 `eval_set`이다 — 폴드마다 검증 묶음을 따로 쥐고 있어야 `early_stopping`에 넘길 수 있고, `cross_val_score`는 그 묶음을 밖으로 내주지 않는다. `cv.split`이 돌려주는 것은 **행 번호 배열**이라 `X_train.iloc[…]`로 잘라야 한다(`loc`가 아니라 `iloc` — `train_test_split`을 거친 `X_train`의 인덱스는 0부터 이어지지 않는다).

| `suggest_*` | 뽑는 것 | 이 파일의 범위 |
| --- | --- | --- |
| `suggest_float(name, low, high)` | 실수 | `learning_rate` 0.01~0.1 · `subsample` 0.6~1.0 · `colsample_bytree` 0.6~1.0 |
| `suggest_int(name, low, high)` | 정수 | `num_leaves` 10~30 · `max_depth` 3~10 · `min_child_samples` 10~50 |
| `suggest_categorical(name, [a, b, c])` | 목록 중 하나 (이 파일엔 없음) | `boosting_type`, `'balanced'`/`None` 같은 선택지 |

`GridSearchCV`의 `param_grid`가 "값의 **목록**"이었다면 `suggest_*`는 "값의 **범위**"다 — 격자는 `learning_rate: [0.01, 0.05, 0.1]` 셋만 보지만 Optuna는 0.01~0.1 사이 어느 값이든 뽑을 수 있다. 앞 노트의 아홉 인자 중 **`n_estimators`는 탐색하지 않고 1000으로 고정**한 것이 이 파일의 선택이다 — 트리 수는 폴드마다 조기 종료가 자료에서 알아내므로 Optuna가 고를 인자에서 빠지고, 탐색 공간이 한 차원 줄어든다. `class_weight`가 빠진 것은 회귀라서 클래스가 없기 때문이다. `suggest_*`의 첫 인자(이름)는 `best_params` 딕셔너리의 키가 되므로 LightGBM 인자 이름과 **똑같이** 맞춰 두면 `LGBMRegressor(**study.best_params)`로 바로 풀 수 있다.

**`trial.set_user_attr`** 가 이 몸통에서 새로 나온 메서드다. 목적함수는 숫자 하나만 돌려줄 수 있는데, 조기 종료가 찾아낸 트리 수는 그 숫자에 들어가지 않는다. 그래서 폴드 다섯 개의 `best_iteration_` 평균을 **시도의 메모장**(`user_attrs` 딕셔너리)에 적어 두고, 스터디가 끝난 뒤 `study.best_trial.user_attrs['best_n_estimators']`로 꺼낸다. 점수와 함께 "이 조합이면 트리를 몇 그루 세워야 하는가"까지 남기는 장치라, 2-1의 최종 모델에서 `n_estimators`를 1000이 아니라 이 값으로 둔다. 점수는 **훈련 세트 안의 교차 검증**이고 `X_test`는 손대지 않는다 — 테스트 세트로 점수를 내면 테스트가 인자 선택에 참여해(앞 노트 2-1의 `eval_set` 문제와 같다) 최종 점수가 후해진다.

### 1-6. 돌려 보면 — 20번 시도와 `best_params`·`user_attrs`

```python
sampler = optuna.samplers.TPESampler(seed=42)
study = optuna.create_study(direction='maximize', sampler=sampler)
study.optimize(objective, n_trials=20)                 # 20번 × 5폴드 = LightGBM 100번 학습, 약 11초

print('최적 하이퍼파라미터:', study.best_params)
# {'learning_rate': 0.0655, 'num_leaves': 16, 'max_depth': 6, 'min_child_samples': 50, 'subsample': 0.9990, 'colsample_bytree': 0.9939}
print('최적 트리: ', study.best_trial.user_attrs['best_n_estimators'])   # 174
print(study.best_value, study.best_trial.number)                          # 0.6360, 19
```

수업 주석에 적힌 결과와 같은 숫자가 나온다(이 노트에서 확인) — `TPESampler(seed=42)`·`KFold(random_state=42)`·`random_state=42`를 다 박아 둔 덕에 다른 컴퓨터에서도 재현된다. 20번 시도의 기록은 이렇다.

| 시도 | 교차검증 R² | `best_n_estimators` | `learning_rate` | `num_leaves` | `subsample` | |
| --- | --- | --- | --- | --- | --- | --- |
| 0 | 0.607 | 267 | 0.044 | 29 | 0.66 | 무작위 구간(0~9) 시작 |
| 1 | 0.606 | 601 | 0.015 | 28 | 0.61 | 보폭이 작아 트리 601그루 |
| 5 | 0.629 | 385 | 0.065 | 13 | 0.99 | |
| 8 | 0.633 | 202 | 0.059 | 13 | 0.98 | 무작위 구간 최고 |
| 9 | 0.610 | 321 | 0.064 | 29 | 0.62 | 무작위 구간 끝 |
| 11 | 0.630 | 118 | 0.073 | 16 | 0.99 | TPE 구간(10~19) — `subsample`이 0.9 이상으로 몰림 |
| 12 | 0.634 | 202 | 0.059 | 15 | 1.00 | |
| 15 | 0.633 | 285 | 0.045 | 11 | 0.98 | |
| 16 | 0.633 | 267 | 0.033 | 17 | 0.97 | |
| **19** | **0.636** | **174** | **0.066** | **16** | **1.00** | **최고 — `best_trial.number = 19`** |

19번 시도의 폴드별 R²는 `[0.596, 0.669, 0.645, 0.638, 0.632]`, 폴드별 `best_iteration_`은 `[174, 173, 125, 164, 237]`이라 평균 174가 `best_n_estimators`로 적혔다. 읽히는 것이 셋이다. ① 무작위 10번은 0.606~0.633 사이에 흩어져 있고 TPE 10번은 0.62~0.636으로 **좁게 모인다** — `subsample`이 0.6대였던 시도(0·1·6·9번)가 하나같이 0.61 아래라, TPE가 11번째부터 `subsample`을 0.9 위로만 뽑은 것이 보인다(행이 2천 개뿐이라 절반만 쓰면 모자란다). 최고가 **마지막 19번**에서 나온 것도 TPE가 끝까지 좋은 쪽을 좁혀 갔다는 뜻이다. ② `best_params`의 `learning_rate=0.066 · num_leaves=16`은 앞 노트에서 손으로 고른 수업 값(0.05 · 15)과 거의 같은 자리이고, `min_child_samples=50`은 범위의 **끝값**이다 — 끝값에 걸리면 범위를 더 열어 볼 신호다(50 위에서 더 좋아질 수도 있다). ③ 트리 수는 174로, 앞 노트 와인 분류에서 조기 종료가 멈춘 310그루보다 적다 — 보폭이 0.066으로 조금 크고 자료가 작아 손실이 빨리 바닥에 닿는다.

## 2. 추가로 알면 좋은 활용법

### 2-1. 최고 조합으로 최종 모델 만들기 — `best_params` + `user_attrs`

```python
best = LGBMRegressor(**study.best_params,
                     n_estimators=study.best_trial.user_attrs['best_n_estimators'],   # 174
                     subsample_freq=1, verbose=-1, random_state=42, n_jobs=-1)
best.fit(X_train, Y_train)                                 # 훈련 세트 전체로 재학습 — eval_set 없이 174그루
print(best.score(X_train, Y_train), best.score(X_test, Y_test))   # 0.803 / 0.723
from sklearn.metrics import mean_absolute_error
print(mean_absolute_error(Y_test, best.predict(X_test)))           # 약 4,260달러
```

`study.optimize`는 **인자만 고르고 모델은 남기지 않는다.** 목적함수 안에서 만든 모델은 함수가 끝나면 사라지므로, `best_params`를 풀어 새 모델을 만들고 훈련 세트 전체로 다시 학습한다. 이때 `n_estimators`를 `user_attrs`의 174로 두는 것이 1-5에서 메모를 남긴 이유다 — 재학습에는 `eval_set`이 없으니 조기 종료가 작동하지 않고, 1000으로 두면 끝까지 쌓는다. 실제로 1000그루로 두고 돌리면 훈련 0.933 · 테스트 0.709로 **훈련만 오르고 테스트는 내려간다**(이 노트에서 확인) — 조기 종료가 막아 주던 과적합이 그대로 돌아온다. 목적함수에서 `suggest_*`로 뽑지 않고 고정한 인자(`subsample_freq=1`·`verbose`·`random_state`)는 `best_params`에 없으므로 다시 적어 준다.

테스트 R² 0.723은 가격의 72 %를 설명한다는 뜻이고, MAE 4,260달러는 평균 1만 9천 달러짜리 차에서 20 %쯤 빗나간다는 뜻이다. 기본 `LGBMRegressor()`(100그루 · 보폭 0.1 · `num_leaves` 31)는 훈련 0.889 · 테스트 0.729라 테스트 점수는 비슷하고 훈련-테스트 차이는 튠 모델이 8점 · 기본이 16점이다 — 튜닝이 테스트 점수를 끌어올리기보다 **과적합 폭을 줄인 쪽**으로 작동했다. 2,456대의 작은 자료에서 교차검증 1~2점은 폴드 운에 가까워, 튜닝이 항상 테스트 점수를 올리는 것은 아니라는 것을 다시 본다(day16 의료비에서 교차검증 0.82 · 테스트 0.88이었던 것과 같은 종류의 차이). `vin`·`condition`을 뺀 7열로는 이 정도가 한계라서, 1-2의 도메인 특성이 다음 손댈 곳이다.

### 2-2. 스터디 뒤에 읽을 것 — `trials_dataframe`·인자 중요도·시각화

```python
df_trials = study.trials_dataframe()                 # 시도별 value·params_*·user_attrs_best_n_estimators·duration이 한 표로
df_trials.sort_values('value', ascending=False).head()
optuna.importance.get_param_importances(study)       # {'subsample': 0.74, 'num_leaves': 0.09, 'colsample_bytree': 0.07, 'learning_rate': 0.07, …}
optuna.visualization.plot_optimization_history(study)   # 시도 번호 vs 점수 (plotly)
optuna.visualization.plot_param_importances(study)
```

`trials_dataframe()`은 1-6의 표를 그대로 꺼내 주는 메서드고, `set_user_attr`로 적은 값도 `user_attrs_best_n_estimators` 열로 함께 나온다. `get_param_importances`는 "어느 인자가 점수를 많이 움직였나"를 fANOVA로 추정한다 — 이 스터디에선 `subsample`이 0.74로 압도적인데, 1-6에서 본 대로 `subsample`을 0.6대로 뽑은 시도들이 점수를 크게 떨어뜨렸기 때문이다. 거꾸로 `max_depth`는 0.002로 거의 0이라(`num_leaves` 10~30이 먼저 걸려 깊이가 거의 안 쓰인다 — 앞 노트 1-2의 "`num_leaves`가 깊이보다 먼저 걸림") 다음 탐색에서 범위를 좁히거나 고정해도 된다. 시각화는 plotly 기반이라 주피터에서 바로 열리고, `.show()`로 브라우저에 띄울 수도 있다.

### 2-3. `direction='minimize'`와 MAE — 지표를 바꾸면 방향도 바뀐다

```python
from sklearn.metrics import mean_absolute_error
def objective_mae(trial):
    …  # 1-5와 같은 폴드 루프, 폴드마다
    cv_mae.append(mean_absolute_error(Y_val, model.predict(X_val)))
    return np.mean(cv_mae)                              # 작을수록 좋은 숫자
study2 = optuna.create_study(direction='minimize', sampler=optuna.samplers.TPESampler(seed=42))
study2.optimize(objective_mae, n_trials=20)
```

`model.score`는 회귀에서 R²라 "클수록 좋다"로 `maximize`가 맞았다. MAE로 바꾸면 "작을수록 좋다"이므로 `minimize`로 바꿔야 한다 — **돌려주는 숫자의 의미와 `direction`을 짝으로** 본다. 사이킷런 `scoring` 문자열을 쓰면 MAE가 `neg_mean_absolute_error`(음수)로 나오므로 그때는 거꾸로 `maximize`가 맞는다는 점이 헷갈리는 자리다. 같은 자료에 R² 최대화와 MAE 최소화는 다른 조합을 고를 수 있다 — 서비스에서 "평균 몇 달러 빗나가는가"가 중요하면 MAE를, 설명력을 보려면 R²를 목적으로 둔다.

### 2-4. 수업 코드의 짜임 — 조기 종료를 교차 검증 안에 넣은 이유

앞 노트에서 "`learning_rate`는 작게 고정하고 트리 수는 조기 종료에 맡기는" 관례를 적었다. 이 파일은 그 관례를 Optuna와 합친 꼴이다 — `n_estimators`는 1000 상한으로 고정하고, 폴드마다 `eval_set`을 떼어 `early_stopping(50)`을 걸어 트리 수는 자료가 정하게 두고, Optuna는 나머지 여섯 인자만 고른다. 그래서 `cross_val_score` 한 줄 대신 `cv.split` 루프를 손으로 돌리고, 조기 종료가 찾은 트리 수를 `set_user_attr`로 따로 챙긴다.

이 짜임의 대가는 **폴드마다 멈춘 자리가 다르다**는 점이다(19번 시도에서 125~237그루). 평균 174는 그 다섯 값의 타협이고, 최종 모델은 훈련 세트 전체(폴드보다 25 % 많은 행)로 학습하므로 조금 더 많은 트리가 맞을 수도 있다. 더 정확히 하려면 ① 재학습 때 `X_test` 말고 훈련 세트의 일부를 다시 떼어 `eval_set`으로 조기 종료를 한 번 더 걸거나, ② 트리 수까지 `suggest_int`로 탐색하고 조기 종료 없이 `cross_val_score`로 가는 길이 있다. 둘 다 한 번씩 돌려 보면 어느 쪽이 이 자료에 맞는지 보인다.

### 2-5. 시간 제한과 중간 끊기 — `timeout`·`n_jobs`·Pruner

```python
study.optimize(objective, n_trials=200, timeout=600)        # 200번 또는 10분 중 먼저 오는 쪽
study.optimize(objective, n_trials=20, n_jobs=4)            # 시도 4개 병렬 (LightGBM n_jobs와 겹치지 않게)
study = optuna.create_study(direction='maximize', pruner=optuna.pruners.MedianPruner())
```

`n_trials`와 `timeout`을 같이 주면 먼저 닿는 조건에서 멈춘다. `n_jobs`는 시도를 병렬로 돌리는데, 목적함수 안의 LightGBM이 이미 `n_jobs=-1`로 코어를 다 쓰고 있으면 겹쳐서 느려지므로 한쪽만 켠다(day17 `GridSearchCV`에서 본 `n_jobs` 중복 주의와 같다). **Pruner**는 시도 하나가 돌아가는 **도중에** 가망이 없으면 끊는 장치다 — `trial.report(점수, step)`로 중간 점수를 보고하고 `trial.should_prune()`이 참이면 `raise optuna.TrialPruned()`를 던지는 식이라, 신경망처럼 에포크가 긴 학습에서 효과가 크다.

## 3. 더 나아가 알면 좋은 것

### 3-1. 격자 → 무작위 → 베이지안 — 탐색 전략 세 세대

| 전략 | 도구 | 다음 후보를 고르는 법 | 장단점 |
| --- | --- | --- | --- |
| 격자 탐색 | `GridSearchCV` (day14) | 적어 둔 조합 전부 | 빠짐없지만 인자가 늘면 조합이 곱으로 폭발(3값 × 9인자 ≈ 2만) |
| 무작위 탐색 | `RandomizedSearchCV` | 범위에서 무작위 `n_iter`개 | 같은 횟수면 격자보다 보통 낫다(중요 인자의 값이 더 다양) |
| 베이지안·순차 탐색 | **Optuna TPE**, scikit-optimize, Hyperopt | 앞 시도의 점수 분포를 보고 좋을 확률이 높은 곳을 | 횟수 대비 효율 최고. 단 처음 몇 번은 무작위, 짧은 탐색(≤ 20)에선 차이가 작다 |

1-6에서 TPE 10번이 `subsample`을 0.9 위로 좁혀 들어가 마지막 시도에서 최고를 낸 것이 세 번째 줄의 "앞 시도의 점수 분포를 보고"이고, 그래도 무작위 구간 최고(0.633)와 0.003 차이밖에 안 난 것이 "단" 쪽이다. Optuna의 강점은 **수백 번**을 돌릴 때, 그리고 인자 사이에 조건이 있을 때(`boosting_type='dart'`면 `drop_rate`도 뽑기 — `suggest_categorical` 결과에 따라 다음 `suggest_*`를 바꾸는 **동적 탐색 공간**) 드러난다. 격자 탐색은 그런 조건을 표현할 수 없다.

### 3-2. LightGBM 전용 자동 튜너 — `optuna.integration.lightgbm`

```python
import optuna.integration.lightgbm as lgb_opt      # pip install optuna-integration
tuner = lgb_opt.LightGBMTunerCV(params, dtrain, folds=kf, callbacks=[early_stopping(50)])
tuner.run(); tuner.best_params
```

앞 노트 3-3에서 이름만 적은 모듈이다. 인자를 한 번에 다 뽑는 대신 `feature_fraction` → `num_leaves` → `bagging` → `lambda_l1/l2` → `min_child_samples` 순으로 **한 종류씩 단계별로** 고정해 가는 방식이라, 일반 TPE보다 적은 시도로 LightGBM에 잘 맞는 조합에 닿는다. 네이티브 `lightgbm.Dataset`·`lgb.train` API 위에서 돌아가므로 사이킷런 래퍼(`LGBMRegressor`)와 인자 이름이 조금 다르다(`subsample` ↔ `bagging_fraction`).

### 3-3. 범주형 처리의 다른 길 — 타깃 인코딩·CatBoost

`category` 타입은 "트리가 범주 묶음을 직접 가른다"는 길이었다. 다른 길로 **타깃 인코딩**(범주를 그 범주의 평균 가격으로 바꾸기, 사이킷런 1.3+ `TargetEncoder`)이 있다 — `model` 126개를 열 하나로 압축하되, 훈련 자료의 타깃을 쓰므로 교차 방식으로 누수를 막아야 한다. **CatBoost**는 이 타깃 통계를 순서 기반(ordered)으로 내부 처리해 범주형 자료에서 손 안 대고도 강한 모델로 꼽히고, `cat_features=cat_cols`로 열 이름만 넘긴다. 고유값이 100개를 넘는 `model`·`color` 같은 열(고차원 범주)은 원-핫보다 이 셋(`category`·타깃 인코딩·CatBoost) 중 하나가 거의 항상 낫다.

### 3-4. 다음에 볼 키워드

- `trial.suggest_int`·`suggest_float(log=True)`·`suggest_categorical` — 탐색 공간 적는 법, 동적 탐색 공간
- `study.best_params`·`best_value`·`best_trial`·`trials_dataframe()`·`get_param_importances`
- `trial.set_user_attr`·`user_attrs` — 점수 외의 결과(최적 트리 수 등)를 시도에 적어 두기, `study.set_user_attr`
- `KFold.split`이 돌려주는 인덱스와 `iloc`, `cross_val_score`로는 못 하는 폴드별 `eval_set` 조기 종료
- `optuna.visualization` — `plot_optimization_history`·`plot_param_importances`·`plot_slice`
- `TPESampler(n_startup_trials, multivariate=True)`·`RandomSampler`·`GridSampler`·`CmaEsSampler`
- `MedianPruner`·`trial.report`·`TrialPruned`, `timeout`·`n_jobs`·`storage='sqlite:///…'`(스터디 저장·이어 돌리기)
- `LightGBMTunerCV`·`optuna-integration`
- `categorical_feature`·`cat.codes`·`TargetEncoder`·CatBoost `cat_features`
- 특성 공학 — 차령 `2020 − year`·연평균 주행거리·브랜드별 평균 가격, `TransformedTargetRegressor(func=np.log1p)` 로그 타깃

## 실습 파일

- `KDT_2026/2026_Python/day18/s-12.py` — `pd.read_csv(URL)` 미국 중고차 `USA_cars_datasets.csv`(2,499대 × 13열) → `df[df['price'] > 0]`(가격 0인 43대 제외 → 2,456대) → `num_cols = ['year', 'mileage']`·`cat_cols = ['brand', 'model', 'title_status', 'color', 'state']`·도메인 계산식 특성 주석 → `for col in cat_cols: df[col] = df[col].astype('category')`(원-핫 대신 판다스 카테고리 타입) → `X = df[num_cols + cat_cols]`·`Y = df['price']`·`train_test_split(test_size=0.2, random_state=42)` → `import optuna`·`optuna.logging.set_verbosity(optuna.logging.WARNING)` → 4) `def objective(trial)`: `KFold(n_splits=5, shuffle=True, random_state=42)` → `for train_idx, val_idx in cv.split(X_train, Y_train)`: `iloc`로 폴드 자르기 → `LGBMRegressor(n_estimators=1000, learning_rate=suggest_float(0.01~0.1), num_leaves=suggest_int(10~30), max_depth=suggest_int(3~10), min_child_samples=suggest_int(10~50), subsample=suggest_float(0.6~1.0), colsample_bytree=suggest_float(0.6~1.0), subsample_freq=1, verbose=-1, random_state=42, n_jobs=-1)` → `fit(eval_set=[(X_val, Y_val)], callbacks=[early_stopping(50, verbose=False)])` → 폴드별 `score`(R²)·`best_iteration_` 저장 → `trial.set_user_attr('best_n_estimators', int(np.mean(best_iterations)))` → `return np.mean(cv_r2_scores)` → 3) `TPESampler(seed=42)`·`create_study(direction='maximize', sampler=sampler)` → `study.optimize(objective, n_trials=20)` → 5) `study.best_params`·`study.best_trial.user_attrs['best_n_estimators']`(수업 결과 주석: `{'learning_rate': 0.0655, 'num_leaves': 16, 'max_depth': 6, 'min_child_samples': 50, 'subsample': 0.9990, 'colsample_bytree': 0.9939}` · 최적 트리 174). 이 노트에서 돌린 결과(optuna 5.0 · lightgbm 4.7, 수업 주석과 일치): 훈련 1,964 · 테스트 492, 기본 `LGBMRegressor` `category` 7열 테스트 R² 0.729 · MAE 4,141 / 원-핫 243열 0.663 / 수치 2열만 0.191, 20회 × 5폴드 약 11초 → `best_value` 0.6360 · 19번째 시도 · 폴드별 R² `[0.596, 0.669, 0.645, 0.638, 0.632]` · 폴드별 `best_iteration_` `[174, 173, 125, 164, 237]`, 무작위 10번 0.606~0.633 vs TPE 10번 0.62~0.636(`subsample` 0.6대 시도가 모두 0.61 아래 → TPE가 0.9 위로 좁힘), 인자 중요도 `subsample` 0.74 · `max_depth` 0.002, 최고 조합 + 174그루 재학습 훈련 0.803 · 테스트 0.723 · MAE 4,260 / 같은 조합 1000그루 0.933 · 0.709 / 기본 모델 0.889 · 0.729

## 관련 노트

[[AI 정리본 인덱스]] · [[AI day18 LightGBM 매개변수 설정과 early_stopping 조기 종료]] · [[AI day17 XGBoost·LightGBM 부스팅 분류기 설정과 모델 딕셔너리]] · [[AI day14 KFold 교차 검증과 GridSearchCV 하이퍼파라미터 탐색]] · [[AI day15 ColumnTransformer·OneHotEncoder로 범주형 특성 파이프라인]] · [[KDT_2026 학습 지도]]
