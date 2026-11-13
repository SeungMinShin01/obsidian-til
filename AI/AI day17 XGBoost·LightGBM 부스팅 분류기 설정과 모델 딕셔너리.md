---
출처: Claude 분석
원본: KDT_2026/2026_Python/day17/s-10.py
작성일: 2026-11-13
tags: [학습, ai, python]
---

# AI day17 — XGBoost·LightGBM 부스팅 분류기 설정과 모델 딕셔너리

> 실습 파일: `day17/s-10.py`
> 허브: [[AI 정리본 인덱스]] · 이전: [[AI day17 랜덤 포레스트로 와인 분류와 class_weight·max_features]] · 다음: (아직 없음)

`s-09.py`는 결정 트리 한 그루에서 시작해 랜덤 포레스트 — 트리 100그루를 **독립적으로** 길러 평균을 내는 배깅 앙상블 — 로 끝났다. `s-10.py`는 같은 와인 자료를 같은 방식으로 나눈 뒤 앙상블의 **다른 갈래인 부스팅**으로 넘어간다. 사이킷런 밖의 두 라이브러리 `xgboost`·`lightgbm`에서 `XGBClassifier`·`LGBMClassifier`를 가져오고, 둘을 **이름을 키로 한 딕셔너리**에 담아 같은 인자(`n_estimators=1000, learning_rate=0.05, max_depth=4, random_state=42, n_jobs=-1`)로 묶어 둔다. 수업 파일은 이 딕셔너리를 만드는 데서 끝나고 `fit`·`score`는 아직 없다 — 이 노트에서는 딕셔너리를 그대로 돌려 본 결과(`random_state=42`)를 앞 노트의 트리·숲 숫자와 나란히 놓고, 인자 하나하나가 무엇을 뜻하는지를 정리한다.

## 1. 배운 내용

### 1-1. 같은 자료·같은 분할 — 비교를 위한 고정

```python
url = 'https://raw.githubusercontent.com/rickiepark/hg-mldl/master/wine.csv'
import pandas as pd
df = pd.read_csv(url)
X = df[['alcohol', 'sugar', 'pH']]
Y = df['class']
from sklearn.model_selection import train_test_split
X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size=0.2, random_state=42, stratify=Y)
```

앞 두 노트와 글자 하나 다르지 않다. 6,497병 × 알코올·당도·pH → 레드(0) : 화이트(1) ≈ 25 : 75, `stratify=Y`로 비율을 지켜 8 : 2 분할, `random_state=42`. 모델을 바꿔 가며 비교하려면 **자료와 분할을 먼저 못 박아야** 점수 차이가 모델 차이가 된다 — 결정 트리 0.865 · 깊이 3 트리 0.841 · 깊이 3 `balanced` 숲 0.774가 전부 이 분할에서 나온 숫자라서, 이 노트의 부스팅 점수도 그 옆에 바로 놓을 수 있다. 트리 계열이라 **표준화는 여기서도 하지 않는다**.

### 1-2. 배깅과 부스팅 — 평균 내기와 순서대로 고치기

앞 노트 3-2에서 키워드로만 적어 둔 구분이 이번 수업의 본문이다.

| | 배깅 (랜덤 포레스트) | 부스팅 (XGBoost·LightGBM) |
| --- | --- | --- |
| 트리를 기르는 순서 | **병렬** — 100그루가 서로를 모른다 | **직렬** — 2번 트리는 1번 트리가 틀린 것을 보고 자란다 |
| 각 트리의 자료 | 부트스트랩 표본 (중복 허용 재추출) | 전체 자료, 단 **앞 트리들의 오차**가 학습 목표 |
| 트리 하나의 모양 | 보통 깊게 (`max_depth=None`) | 얕게 (`max_depth` 3~8) — "약한 학습기" |
| 예측 | 100그루 확률의 **평균** | 트리들의 출력을 **더한 값**에 시그모이드 |
| 줄이는 것 | 분산 (자료가 바뀌면 모양이 크게 바뀌는 문제) | 편향 (모델이 단순해서 못 맞히는 문제) |
| 트리를 늘리면 | 나빠지지 않는다 (앞 노트 1-5) | **과대적합한다** → `learning_rate`·조기 종료가 따라온다 |
| 핵심 인자 | `n_estimators`·`max_features` | `n_estimators`·**`learning_rate`**·`max_depth` |

부스팅의 그림은 이렇다. 첫 트리가 자료를 대충 가른다. 틀린 표본이 남는다. 두 번째 트리는 **그 틀린 정도(잔차)를 맞히도록** 학습하고, 그 출력에 `learning_rate`를 곱해 첫 트리에 더한다. 세 번째 트리는 그래도 남은 오차를 맞히고… 이것을 `n_estimators`번 반복한다. 그래서 트리 하나하나는 얕아도 되고, 대신 **순서가 있어 병렬로 기를 수 없다** — `n_jobs=-1`은 트리들을 동시에 기르는 것이 아니라 **한 트리 안에서** 분할 후보를 찾는 계산을 여러 코어로 나눈다는 뜻이다. 랜덤 포레스트의 `n_jobs`와 이름은 같지만 쓰는 자리가 다르다.

### 1-3. `XGBClassifier` — 인자 다섯 개

```python
from xgboost import XGBClassifier
XGBClassifier(n_estimators=1000, learning_rate=0.05, max_depth=4, random_state=42, n_jobs=-1)
```

| 인자 | 뜻 | 수업 값 | 기본값 |
| --- | --- | --- | --- |
| `n_estimators` | 쌓을 트리 수 = 보정 횟수 | 1000 | 100 |
| `learning_rate` | 트리 하나의 출력을 얼마나 반영할지 (보폭, `eta`) | 0.05 | 0.3 |
| `max_depth` | 각 트리의 최대 깊이 | 4 | 6 |
| `random_state` | 열·행 부분 추출의 씨앗 | 42 | 0 |
| `n_jobs` | 한 트리를 기를 때 쓸 코어 수 | -1 (전부) | 전부 |

`n_estimators`와 `learning_rate`는 **짝으로** 읽어야 한다. 보폭이 0.05면 트리 하나가 답을 5 %씩만 고치므로 1,000그루가 있어야 충분히 다가가고, 보폭이 0.3이면 100그루로 비슷한 자리에 닿는다. 수업 값 `1000 × 0.05`는 "작게 여러 번"이고 기본값 `100 × 0.3`은 "크게 몇 번"이다. 작게 여러 번이 보통 더 매끄럽게 수렴하고 과대적합도 덜한 대신 느리다. 이 노트에서 하나씩 바꿔 보면 이렇다(나머지는 수업 값 고정).

| `n_estimators` | 훈련 | 테스트 | | `learning_rate` | 훈련 | 테스트 | | `max_depth` | 훈련 | 테스트 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 10 | 0.754 | 0.754 | | 0.01 | 0.886 | 0.857 | | 1 | 0.872 | 0.860 |
| 50 | 0.877 | 0.852 | | **0.05** | 0.918 | 0.869 | | 2 | 0.884 | 0.855 |
| 100 | 0.880 | 0.855 | | 0.1 | 0.949 | 0.877 | | 3 | 0.897 | 0.865 |
| 300 | 0.893 | 0.864 | | 0.3 | 0.985 | 0.874 | | **4** | 0.918 | 0.869 |
| **1000** | 0.918 | 0.869 | | 1.0 | 0.998 | 0.869 | | 6 | 0.957 | 0.879 |
| 3000 | 0.959 | 0.871 | | | | | | 8 | 0.984 | 0.882 |

읽히는 것이 세 가지다. ① 10그루 × 0.05는 아직 0.754 — 보정이 열 번 × 5 %라 답에 못 닿았다(랜덤 포레스트는 10그루로 0.80이었다). ② 트리를 3,000까지 늘리면 훈련은 0.96으로 계속 오르지만 테스트는 0.87에서 멈춘다 — **늘릴수록 훈련 자료를 외우기 시작**하는 것이 배깅과의 차이다. ③ `learning_rate=1.0`은 훈련 0.998 — 보폭이 크면 한 트리가 오차를 통째로 삼켜 외운다. `max_depth=1`(질문 하나짜리 트리, 스텀프)만 1,000그루 쌓아도 0.86이 나오는 것이 "약한 학습기를 많이"라는 말의 뜻이다.

### 1-4. `LGBMClassifier` — 같은 인자, 그리고 `verbose=-1`

```python
from lightgbm import LGBMClassifier
LGBMClassifier(n_estimators=1000, learning_rate=0.05, max_depth=4, random_state=42, n_jobs=-1, verbose=-1)
```

인자 이름이 XGBoost와 같아서 같은 값을 그대로 넣는다 — 두 라이브러리 모두 **사이킷런 추정기 규약**을 따르는 래퍼 클래스를 제공해서 `fit`·`score`·`predict_proba`·`feature_importances_`·`GridSearchCV`가 그대로 된다. 다른 점은 둘이다.

**`verbose=-1`** — LightGBM은 학습 중 `[LightGBM] [Info] …`·`[Warning] …` 줄을 표준 출력에 찍는다. `-1`이면 치명적 오류만, `0`이면 경고까지, `1`(기본)이면 정보까지 보인다. 1,000그루 학습에서 로그가 수십 줄 나오므로 수업 코드가 꺼 둔 것이다. XGBoost는 `verbosity`라는 다른 이름이고 기본이 조용하다.

**트리를 키우는 방향** — XGBoost는 깊이 단위로(level-wise) 한 층을 꽉 채우고 다음 층으로 가고, LightGBM은 **손실을 가장 많이 줄이는 리프 하나를 골라** 거기만 가른다(leaf-wise). 그래서 LightGBM의 본래 제한 인자는 `max_depth`가 아니라 **`num_leaves`**(기본 31)이고, `max_depth=4`를 주면 리프가 최대 2⁴ = 16개라 `num_leaves=31`은 닿지 않는 상한이 된다. 같은 `max_depth=4`를 줘도 두 모델의 트리 모양이 다른 이유다. 또 LightGBM은 연속값을 미리 **히스토그램 구간(기본 255개)** 으로 묶어 분할 후보를 찾으므로 큰 자료에서 눈에 띄게 빠르다 — 6,497병에서는 둘 다 0.3초라 차이가 없다.

| | XGBoost | LightGBM |
| --- | --- | --- |
| 트리 성장 | 층 단위 (level-wise) | 리프 단위 (leaf-wise) |
| 깊이 제한 | `max_depth`(기본 6) | `num_leaves`(기본 31) + `max_depth`(기본 −1 = 무제한) |
| 분할 후보 | 정확 탐색 또는 히스토그램(`tree_method='hist'`가 기본) | 히스토그램 (기본 255구간) |
| 보폭 기본값 | 0.3 | 0.1 |
| 로그 끄기 | `verbosity=0` | `verbose=-1` |
| 강점 | 안정적·문서 많음 | 큰 자료에서 빠름·메모리 적게 |

### 1-5. 모델 딕셔너리 — 이름을 키로 묶어 같은 루프에 넣기

```python
models = {
    "XGBoost":  XGBClassifier(n_estimators=1000, learning_rate=0.05, max_depth=4, random_state=42, n_jobs=-1),
    "LightGBM": LGBMClassifier(n_estimators=1000, learning_rate=0.05, max_depth=4, random_state=42, n_jobs=-1, verbose=-1),
}
```

`s-09.py`에서는 모델을 바꿀 때마다 `model = …`을 **덮어썼다**. 그래서 트리와 숲의 점수를 나란히 보려면 출력 주석을 거슬러 읽어야 했다. 딕셔너리는 그 불편을 없애는 관용구다 — **표시용 이름을 키, 아직 학습하지 않은 모델 객체를 값**으로 두면, 뒤에 올 코드는 이름을 몰라도 된다.

```python
for name, model in models.items():
    model.fit(X_train, Y_train)
    print(name, "Train Acc :", model.score(X_train, Y_train), "Test Acc :", model.score(X_test, Y_test))
```

모델을 하나 더 비교하고 싶으면 루프는 두고 **딕셔너리에 한 줄만 추가**한다. 앞 노트의 `RandomForestClassifier`나 `DecisionTreeClassifier`를 같은 딕셔너리에 넣으면 네 모델이 한 표로 나온다. 학습된 모델도 딕셔너리 안 객체에 그대로 남으므로 루프가 끝난 뒤 `models["XGBoost"].feature_importances_`처럼 이름으로 꺼내 쓸 수 있다. day16 의료비 실습에서 `param_grid`를 딕셔너리로 적었던 것과 같은 발상이고, 사이킷런 추정기가 전부 같은 `fit`·`score`를 갖기 때문에 성립한다.

### 1-6. 돌려 보면 — 트리·숲·부스팅 한 표

딕셔너리를 1-5의 루프로 돌리고, 앞 두 노트의 모델을 같은 분할에서 다시 학습해 나란히 두었다(이 노트에서 확인, `random_state=42`).

| 모델 | 훈련 | 테스트 | 학습 시간 | 레드 재현율 | 혼동행렬 `[[레드→레드, 레드→화이트], [화이트→레드, 화이트→화이트]]` |
| --- | --- | --- | --- | --- | --- |
| 결정 트리 (제한 없음) | 0.998 | 0.865 | 0.01초 | — | — |
| 결정 트리 `max_depth=3` | 0.846 | 0.841 | 0.01초 | 0.625 | — |
| 랜덤 포레스트 `max_depth=3, balanced` | 0.785 | 0.774 | 0.23초 | 0.859 | `[[275, 45], [249, 731]]` |
| 랜덤 포레스트 (제한 없음) | 0.998 | **0.889** | 0.30초 | — | — |
| **XGBoost** `1000 × 0.05, depth 4` | 0.918 | 0.869 | 0.28초 | 0.719 | `[[230, 90], [80, 900]]` |
| **LightGBM** `1000 × 0.05, depth 4` | 0.929 | 0.875 | 0.28초 | 0.738 | `[[236, 84], [79, 901]]` |

수업 인자 그대로의 두 부스팅은 테스트 0.87 안팎으로 **제한 없는 결정 트리(0.865)보다 조금 낫고, 제한 없는 랜덤 포레스트(0.889)에는 못 미친다.** "부스팅이 항상 이긴다"가 아니라는 것이 이 표의 첫 교훈이다 — 특성이 셋뿐이고 표본이 6천인 작은 자료에서는 깊은 숲이 이미 충분하고, 부스팅은 `max_depth=4`에 묶여 있다(1-3의 표에서 깊이 8이면 0.882까지 오른다). 둘째, 부스팅은 **훈련 0.92 · 테스트 0.87로 격차 5점** — 1,000그루를 쌓았는데도 숲의 11점보다 작다. 얕은 트리 × 작은 보폭이 과대적합을 누른 결과다. 셋째, 레드 재현율은 0.72~0.74로 가중치 없는 모델답게 화이트 쪽으로 기울어 있다 — 앞 노트의 `class_weight`에 해당하는 인자는 2-3에 적었다.

### 1-7. 설치와 가져오기

```
pip install xgboost lightgbm
```

둘 다 사이킷런에 **들어 있지 않은** 별도 패키지다. `from xgboost import XGBClassifier`·`from lightgbm import LGBMClassifier`가 `ModuleNotFoundError`를 내면 설치가 안 된 것이고, 설치 뒤에도 `import` 줄은 파일 맨 위가 아니라 분할 다음에 있어도 된다(수업 코드가 그렇다). 회귀용은 `XGBRegressor`·`LGBMRegressor`로, 앞 노트의 `DecisionTreeClassifier`/`DecisionTreeRegressor` 짝과 같은 규칙이다.

## 2. 추가로 알면 좋은 활용법

### 2-1. 조기 종료 — `n_estimators`를 크게 두고 멈출 때를 자료가 정하게

```python
# XGBoost — 생성자에 early_stopping_rounds, fit에 eval_set
from sklearn.model_selection import train_test_split
X_tr, X_va, Y_tr, Y_va = train_test_split(X_train, Y_train, test_size=0.2, random_state=42, stratify=Y_train)
xgb = XGBClassifier(n_estimators=3000, learning_rate=0.05, max_depth=4, random_state=42, n_jobs=-1,
                    early_stopping_rounds=50, eval_metric='logloss')
xgb.fit(X_tr, Y_tr, eval_set=[(X_va, Y_va)], verbose=False)
print(xgb.best_iteration)                  # 142

# LightGBM — 콜백
import lightgbm as lgb
lgbm = LGBMClassifier(n_estimators=3000, learning_rate=0.05, max_depth=4, random_state=42, n_jobs=-1, verbose=-1)
lgbm.fit(X_tr, Y_tr, eval_set=[(X_va, Y_va)], callbacks=[lgb.early_stopping(50, verbose=False)])
print(lgbm.best_iteration_)                # 244
```

1-3의 표에서 트리를 늘릴수록 훈련만 오르는 것을 봤다. 조기 종료는 **훈련 자료에서 따로 떼어 둔 검증 세트**의 손실을 트리를 하나 더할 때마다 재고, 50그루 동안 나아지지 않으면 거기서 멈추는 장치다. 이 자료에서는 XGBoost가 142그루, LightGBM이 244그루에서 멈춘다 — 수업의 1,000은 넉넉한 상한이었던 셈이다. 검증 세트를 **테스트 세트로 쓰면 안 된다**(테스트가 학습에 개입해 점수가 부풀어진다). 두 라이브러리의 호출 방식이 다른 것이 이 자리에서 가장 자주 헷갈린다: XGBoost는 생성자 인자, LightGBM은 `fit`의 `callbacks`.

### 2-2. `feature_importances_` — 두 라이브러리가 다른 것을 센다

```python
models["XGBoost"].feature_importances_    # [0.186 0.647 0.167]   ← gain 비율 (합 1)
models["LightGBM"].feature_importances_   # [3473 3367 3978]      ← 분할에 쓰인 횟수
```

같은 속성 이름인데 **의미가 다르다.** XGBoost 래퍼의 기본(`importance_type='gain'`)은 그 특성으로 가른 분할이 손실을 줄인 양의 비율이라 앞 노트의 사이킷런 숲과 같은 눈으로 읽을 수 있고, 여기서도 당도 0.65가 1등이다. LightGBM 래퍼의 기본(`importance_type='split'`)은 **그 특성이 분할에 쓰인 횟수**라서 세 값이 비슷하게 나오고 pH가 가장 크다 — 당도로 한 번 크게 가르고 pH·알코올로 잘게 다듬었다는 뜻이지 pH가 가장 중요하다는 뜻이 아니다. `LGBMClassifier(importance_type='gain')`으로 만들면 XGBoost와 같은 기준이 된다. 라이브러리를 섞어 중요도를 비교할 때는 **기준을 먼저 맞춘다.**

### 2-3. 불균형 — `scale_pos_weight`와 `class_weight`

앞 노트의 `class_weight="balanced"`에 해당하는 인자가 둘에서 다르다. XGBoost는 **`scale_pos_weight`** 하나로 양성(1) 클래스의 가중치를 주는데, 이 자료는 소수 클래스가 레드(0)라 `scale_pos_weight = 음성 수 / 양성 수 = 1279 / 3918 ≈ 0.33`처럼 1보다 작은 값을 줘야 레드 쪽이 무거워진다(보통은 소수 클래스를 1로 두므로 이 자료는 거꾸로다). LightGBM은 사이킷런과 같은 **`class_weight='balanced'`**를 받는다. 어느 쪽이든 앞 노트에서 본 것처럼 정확도를 내주고 재현율을 사는 거래이고, 2-1의 검증 세트에 `f1_macro`를 걸어 고르는 편이 안전하다.

### 2-4. `GridSearchCV`에 그대로 넣기

```python
from sklearn.model_selection import GridSearchCV, StratifiedKFold
grid = GridSearchCV(
    XGBClassifier(random_state=42, n_jobs=-1),
    {'n_estimators': [300, 1000], 'learning_rate': [0.05, 0.1], 'max_depth': [3, 4, 6]},
    cv=StratifiedKFold(5, shuffle=True, random_state=42), scoring='accuracy',
).fit(X_train, Y_train)
```

사이킷런 규약을 따르므로 day14·15의 틀이 그대로 된다. 다만 1-3에서 봤듯 `n_estimators`·`learning_rate`·`max_depth`는 서로 얽혀 있어 격자가 금방 커진다 — 보통 `learning_rate`를 0.05쯤으로 고정하고 `max_depth`·`min_child_weight`·`subsample`을 찾은 뒤, `n_estimators`는 격자 대신 2-1의 조기 종료로 정한다. `GridSearchCV(n_jobs=-1)`과 모델의 `n_jobs=-1`을 둘 다 켜면 코어를 서로 뺏으므로 한쪽만 켠다.

### 2-5. 설치 없이 같은 것 — `HistGradientBoostingClassifier`

```python
from sklearn.ensemble import HistGradientBoostingClassifier
HistGradientBoostingClassifier(random_state=42).fit(X_train, Y_train).score(X_test, Y_test)   # 0.875
```

사이킷런 안에도 LightGBM과 같은 히스토그램 방식 부스팅이 있다. 기본값 그대로 테스트 0.875로 수업 인자의 LightGBM과 같고, 결측값을 알아서 다루며 설치가 필요 없다. 옛 `GradientBoostingClassifier`(기본값 0.858)는 정확 탐색이라 큰 자료에서 느리다. 외부 라이브러리가 막힌 환경이라면 이쪽이 대안이다.

## 3. 더 나아가 알면 좋은 것

### 3-1. 그래디언트 부스팅의 원리 — 잔차에 트리를 맞춘다

"앞 트리가 틀린 것을 다음 트리가 고친다"를 수식으로 쓰면, 현재까지의 예측 F(x)에 대해 손실(로그 손실)의 **기울기(gradient)의 음수 방향**을 다음 트리가 맞히고, F ← F + learning_rate × 트리 로 갱신한다. 경사 하강법을 함수 공간에서 하는 것이라 이름이 그래디언트 부스팅이다. XGBoost는 여기에 2차 미분까지 써서 분할 이득을 더 정확히 계산하고, 트리 복잡도에 벌점(`reg_lambda`·`gamma`)을 붙인 것이 "eXtreme"의 내용이다. day13의 릿지 규제가 트리 안으로 들어온 셈이다.

### 3-2. 과대적합을 누르는 인자들

| 인자 | 뜻 | 효과 |
| --- | --- | --- |
| `subsample` | 트리마다 쓸 행의 비율 (0.5~1) | 랜덤 포레스트의 부트스트랩에 해당 |
| `colsample_bytree` | 트리마다 쓸 열의 비율 | 랜덤 포레스트의 `max_features`에 해당 |
| `min_child_weight` / `min_child_samples` | 리프가 가져야 할 최소 무게·샘플 | 앞 노트 `min_samples_leaf` |
| `reg_lambda`·`reg_alpha` | 리프 값에 L2·L1 벌점 | 릿지·라쏘 |
| `gamma` (XGB) / `min_split_gain` (LGBM) | 분할이 줄여야 할 최소 손실 | 작은 이득의 분할 금지 |

이름이 두 라이브러리에서 조금씩 다르지만 역할은 같다. 수업 코드는 `max_depth`와 `learning_rate`만으로 눌렀는데, 특성이 수십 개인 자료에서는 `subsample=0.8, colsample_bytree=0.8`이 거의 관례로 따라붙는다.

### 3-3. CatBoost와 범주형 특성

세 번째 주자 CatBoost는 범주형 열을 **원-핫 없이** 그대로 받아 순서 통계로 인코딩하고, 기본값이 좋아 조정이 덜 필요하다. LightGBM도 `categorical_feature`로 범주형을 직접 받는다. day15·16에서 `OneHotEncoder`로 펭귄 섬·흡연 여부를 펼쳤던 자리를 이 인자들이 대신하는데, 범주가 수백 개(우편번호 등)면 원-핫보다 훨씬 효율적이다. 셋 다 `device='cuda'`·`tree_method='hist'` 같은 인자로 GPU에서 돌릴 수 있다.

### 3-4. 다음에 볼 키워드

- `early_stopping_rounds`·`eval_set`·`best_iteration` — 트리 수를 자료가 정하게
- `importance_type`(`gain`·`split`·`cover`) — 중요도 기준 맞추기
- `scale_pos_weight`·`class_weight` — 부스팅의 불균형 처방
- `subsample`·`colsample_bytree`·`reg_lambda`·`min_child_weight` — 부스팅 규제
- `HistGradientBoostingClassifier` — 사이킷런 내장 대안
- CatBoost·`categorical_feature` — 범주형을 원-핫 없이
- 스태킹(`StackingClassifier`) — 숲과 부스팅을 다시 묶기

## 실습 파일

- `KDT_2026/2026_Python/day17/s-10.py` — `pd.read_csv(URL)` 와인 자료 → `X`(알코올·당도·pH)·`Y`(class) → `train_test_split(test_size=0.2, random_state=42, stratify=Y)` → `from lightgbm import LGBMClassifier`·`from xgboost import XGBClassifier` → `{"XGBoost": XGBClassifier(n_estimators=1000, learning_rate=0.05, max_depth=4, random_state=42, n_jobs=-1), "LightGBM": LGBMClassifier(…같은 인자…, verbose=-1)}` 모델 딕셔너리까지 (학습·평가 루프는 아직 없음). 이 노트에서 돌린 결과(`random_state=42`): XGBoost 훈련 0.918 · 테스트 0.869 · 레드 재현율 0.719 · 중요도 `[0.186 0.647 0.167]` / LightGBM 0.929 · 0.875 · 0.738 · 분할 횟수 `[3473 3367 3978]` / 조기 종료 142·244그루 / `HistGradientBoostingClassifier` 0.875 / 제한 없는 랜덤 포레스트 0.889

## 관련 노트

[[AI 정리본 인덱스]] · [[AI day17 랜덤 포레스트로 와인 분류와 class_weight·max_features]] · [[AI day17 결정 트리로 와인 레드·화이트 분류와 plot_tree]] · [[AI day14 KFold 교차 검증과 GridSearchCV 하이퍼파라미터 탐색]] · [[AI day13 StandardScaler 표준화와 릿지·라쏘 규제]] · [[KDT_2026 학습 지도]]
