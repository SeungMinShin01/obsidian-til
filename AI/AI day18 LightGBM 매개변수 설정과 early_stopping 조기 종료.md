---
출처: Claude 분석
원본: KDT_2026/2026_Python/day18/s-11.py
작성일: 2026-11-16
tags: [학습, ai, python]
---

# AI day18 — LightGBM 매개변수 설정과 early_stopping 조기 종료

> 실습 파일: `day18/s-11.py`
> 허브: [[AI 정리본 인덱스]] · 이전: [[AI day17 XGBoost·LightGBM 부스팅 분류기 설정과 모델 딕셔너리]] · 다음: [[AI day18 Optuna 스터디·목적함수 설정과 판다스 category 타입]]

`s-10.py`는 XGBoost와 LightGBM을 **같은 인자 다섯 개**로 묶어 딕셔너리 루프에 넣고 비교하는 데서 끝났다. 그때 `n_estimators`를 1,000~3,000으로 넉넉히 두고 **중간에 멈추라**는 주석이 있었는데, `s-11.py`가 그 장치를 실제로 건다. 같은 와인 자료·같은 분할에서 이번에는 **LightGBM 하나만** 골라 인자를 아홉 개로 늘려 쓰고(`n_estimators=1000, learning_rate=0.05, num_leaves=15, max_depth=6, min_child_samples=20, subsample=0.8, subsample_freq=1, colsample_bytree=0.8, class_weight="balanced"`), `fit`에 **`eval_set`과 `early_stopping` 콜백**을 넣어 1,000그루 중 310그루에서 멈추게 한다. 학습이 끝나면 `best_iteration_`·`feature_name_`·`feature_importances_` 세 속성을 읽고, 훈련·테스트 정확도와 macro F1을 찍은 뒤, 새 와인 두 병을 DataFrame으로 만들어 `predict`까지 간다. 이 노트는 인자 아홉 개를 앞 노트의 규제 인자 표에 맞춰 하나씩 풀고, 조기 종료가 실제로 어디서 왜 멈추는지를 손실 곡선과 함께 적는다. 수업 코드의 출력 주석(310 · `[579 2284 1447]` · 0.8845 / 0.8523 / 0.8192)은 이 노트에서 같은 씨앗으로 다시 돌려 그대로 확인했다.

## 1. 배운 내용

### 1-1. 같은 자료·같은 분할, 모델은 LightGBM 하나

```python
import pandas as pd
url = 'https://raw.githubusercontent.com/rickiepark/hg-mldl/master/wine.csv'
df = pd.read_csv(url)
X = df[['alcohol', 'sugar', 'pH']]
Y = df['class']
from sklearn.model_selection import train_test_split
X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size=0.2, random_state=42, stratify=Y)

from lightgbm import LGBMClassifier   # 분류. 회귀는 LGBMRegressor
```

자료 읽기와 분할은 day17 세 노트와 글자 하나 다르지 않다 — 6,497병 × 알코올·당도·pH → 레드(0) : 화이트(1) ≈ 25 : 75, `stratify=Y`로 비율을 지켜 8 : 2, `random_state=42`. 그래서 이 노트의 점수도 트리 0.865 · 숲 0.889 · 100그루 LightGBM 0.861 옆에 바로 놓을 수 있다. 앞 노트에서 두 라이브러리를 나란히 놓고 봤으니, 이번에는 그중 **LightGBM 하나를 골라 인자를 제대로 채우는** 단계다. `LGBMClassifier`/`LGBMRegressor` 짝은 `DecisionTreeClassifier`/`DecisionTreeRegressor`·`XGBClassifier`/`XGBRegressor`와 같은 규칙이고, 트리 계열이므로 표준화는 여기서도 하지 않는다.

### 1-2. 인자 아홉 개 — 앞 노트의 규제 표가 실제 값으로

```python
model = LGBMClassifier(
    n_estimators=1000,        # 1) 트리 최대 개수 (기본 100) — 넉넉히 두고 조기 종료로 자른다
    learning_rate=0.05,       # 2) 학습률, 트리 하나의 출력을 얼마나 반영할지 (기본 0.1)
    num_leaves=15,            # 3) 트리 하나의 최대 리프 수 (기본 31)
    max_depth=6,              # 4) 트리 하나의 최대 깊이 (기본 -1 = 무제한)
    min_child_samples=20,     # 5) 리프가 가져야 할 최소 샘플 수 (기본 20)
    subsample=0.8,            # 6) 트리마다 행의 80 %만 무작위로 쓴다 (기본 1.0)
    subsample_freq=1,         # 7) 6)을 매 트리마다 적용 (기본 0 = 꺼짐)
    colsample_bytree=0.8,     # 8) 트리마다 특성의 80 %만 무작위로 쓴다 (기본 1.0)
    class_weight="balanced",  # 9) 클래스 불균형 보정 (기본 None)
    verbose=-1,               # 학습 로그 숨김
    random_state=42, n_jobs=-1,
)
```

앞 노트 3-2에 "이름만 적어 둔" 규제 인자들이 전부 실제 값을 받았다. 아홉 개를 **역할별로 세 묶음**으로 나누면 외우기 쉽다.

| 묶음 | 인자 | 수업 값 | 기본값 | 하는 일 |
| --- | --- | --- | --- | --- |
| 얼마나 쌓을까 | `n_estimators` | 1000 | 100 | 트리 최대 개수 = 보정 횟수의 상한. 조기 종료가 실제 개수를 정한다 |
| | `learning_rate` | 0.05 | 0.1 | 트리 하나의 보폭. 작으면 트리가 더 필요하고 더 매끄럽다 |
| 트리 하나를 어디까지 키울까 | `num_leaves` | 15 | 31 | 트리 하나의 최대 리프 수 — **LightGBM의 본래 복잡도 인자** |
| | `max_depth` | 6 | −1 | 깊이 상한. 리프 15개는 깊이 4(2⁴ = 16)만 있으면 되므로 여기서는 `num_leaves`가 먼저 걸린다 |
| | `min_child_samples` | 20 | 20 | 리프 하나에 최소 20병. 앞 노트의 `min_samples_leaf` |
| 트리마다 무엇을 보여 줄까 | `subsample` | 0.8 | 1.0 | 행 80 %만 — 랜덤 포레스트의 부트스트랩에 해당(복원 없는 추출) |
| | `subsample_freq` | 1 | 0 | `subsample`을 몇 그루마다 다시 뽑을지. **0이면 `subsample`이 무시된다** |
| | `colsample_bytree` | 0.8 | 1.0 | 특성 80 %만 — 셋 중 둘(또는 셋). 랜덤 포레스트의 `max_features` |
| 어느 쪽을 더 무겁게 볼까 | `class_weight` | `"balanced"` | None | 빈도 역수 가중치 — 레드 ≈ 2.0 · 화이트 ≈ 0.66 |

**`num_leaves`와 `max_depth`의 관계**가 앞 노트와 반대로 걸린다. 앞 노트의 `max_depth=4`는 리프를 최대 16개로 묶었기 때문에 기본 `num_leaves=31`은 닿지 않는 상한이었다. 이번 `num_leaves=15`는 깊이 6에서 가능한 리프 64개보다 훨씬 작아서 **리프 수가 먼저 걸리고 깊이 6은 안전장치**로 남는다. LightGBM은 리프 단위(leaf-wise)로 자라므로 "리프 15개"가 트리 모양을 정하는 진짜 인자이고, `max_depth`는 한 가지만 비정상적으로 길게 뻗는 것을 막는 보조다. 공식 문서도 `num_leaves < 2^max_depth`로 두라고 적는다 — 15 < 64라서 이 조건을 만족한다.

**`subsample_freq=1`이 왜 따로 필요한가.** XGBoost는 `subsample=0.8`만 주면 매 트리마다 행을 다시 뽑지만, LightGBM은 `bagging_fraction`(= `subsample`)과 `bagging_freq`(= `subsample_freq`)가 **둘 다 켜져야** 배깅이 동작한다. 기본 `subsample_freq=0`이면 `subsample=0.8`을 줘도 조용히 무시된다 — 수업 주석의 "6과 같이 설정하되, 매 트리마다 배깅을 활성화"가 이 뜻이다. 두 라이브러리 사이에서 가장 자주 빠지는 함정이라 짝으로 외운다. `colsample_bytree`(= `feature_fraction`)는 반대로 단독으로 동작한다.

**행·열 부분 추출이 하는 일**은 랜덤 포레스트와 같다 — 트리마다 조금씩 다른 자료를 보여 서로 닮지 않게 하고, 그 다양성이 과대적합을 누른다. 특성이 셋뿐이라 `colsample_bytree=0.8`은 트리마다 특성 둘 또는 셋을 쓰는 정도지만, 특성이 수십 개인 자료에서는 `subsample=0.8, colsample_bytree=0.8`이 거의 관례처럼 따라붙는다.

### 1-3. `early_stopping` 콜백 — 멈출 때를 검증 손실이 정한다

```python
from lightgbm import early_stopping
model.fit(X_train, Y_train,
          eval_set=[(X_test, Y_test)],                                   # 매 트리마다 손실을 잴 자료
          callbacks=[early_stopping(stopping_rounds=50, verbose=False)]) # 50그루 동안 안 좋아지면 멈춤
```

`fit`에 인자가 둘 붙었다. **`eval_set`** 은 `(X, Y)` 튜플의 리스트로, 트리를 한 그루 더할 때마다 이 자료의 손실(이진 분류 기본 `binary_logloss`)을 재서 기록한다. **`callbacks`** 는 학습 루프 중간에 끼어드는 함수 목록이고, `early_stopping(stopping_rounds=50)`은 "검증 손실이 **50그루 연속으로** 최솟값을 갱신하지 못하면 학습을 끊어라"는 콜백이다. `verbose=False`는 멈출 때 찍는 `Early stopping, best iteration is: …` 메시지를 끈다. 앞 노트 2-1에서 `lgb.early_stopping(50)`으로 미리 써 봤던 것이 수업 본문으로 올라온 셈이고, XGBoost라면 같은 일을 생성자의 `early_stopping_rounds=50`이 한다는 차이도 거기 적어 두었다.

실제로 돌리면 이렇게 움직인다(이 노트에서 `evals_result_`로 확인).

| 트리 번호 | 검증 `binary_logloss` | |
| --- | --- | --- |
| 1 | 0.668 | 시작 — 거의 아무것도 못 맞히는 상태(ln 2 ≈ 0.693 근처) |
| 10 | 0.521 | |
| 50 | 0.375 | 급하게 내려오는 구간 |
| 100 | 0.353 | |
| 200 | 0.340 | 완만해진다 |
| 300 | 0.3357 | |
| **310** | **0.3346** | 최솟값 → `best_iteration_ = 310` |
| 360 | 0.3361 | 50그루 동안 310을 못 넘어 **여기서 멈춤** |

그래서 `n_estimators=1000`을 줬지만 실제로 자란 트리는 **360그루**이고, 모델이 예측에 쓰는 것은 그중 **처음 310그루**다. 310 뒤의 50그루는 "더 나아지나 기다려 본" 몫이라 버려진다. `model.n_estimators_`·`model.booster_.num_trees()`를 찍어 보면 둘 다 310으로, 멈춘 뒤 최적 지점까지 잘라 둔 것을 알 수 있다. 1-2의 `n_estimators=1000`을 "넉넉히"라고 적은 이유가 여기 있다 — **상한만 크게 주고 실제 개수는 자료가 정하게** 한다. 앞 노트에서 수업 값 100그루가 "아직 오르막 중간"이었던 것과 비교하면, 이번 설정에서는 손실이 100그루에서 0.353, 310그루에서 0.335로 그 뒤 200그루가 더 필요했다.

`stopping_rounds`는 **참을성**이다. 10으로 줄이면 226그루에서 멈추고(테스트 0.846), 100·200으로 늘려도 310에서 똑같이 멈춘다 — 310 뒤에는 100그루를 기다려도 최솟값이 없기 때문이다. 손실 곡선이 울퉁불퉁한 자료에서는 참을성이 너무 작으면 일시적 정체에서 일찍 끊고, 너무 크면 과대적합 구간까지 들어간 뒤 돌아온다. 50은 그 사이의 흔한 기본값이다.

### 1-4. 학습 뒤 읽는 세 속성

```python
print(model.best_iteration_)       # 310  — 검증 손실이 가장 낮았던 트리 번호
print(model.feature_name_)         # ['alcohol', 'sugar', 'pH']
print(model.feature_importances_)  # [ 579 2284 1447]
```

| 속성 | 값 | 뜻 |
| --- | --- | --- |
| `best_iteration_` | 310 | 조기 종료가 고른 트리 수. 조기 종료를 안 걸면 `None`(또는 0)이고, `predict`는 이 번호까지만 쓴다 |
| `feature_name_` | `['alcohol', 'sugar', 'pH']` | `fit`에 열 이름이 있는 DataFrame을 넣었기에 생긴 이름. 사이킷런의 `feature_names_in_`에 해당 |
| `feature_importances_` | `[579 2284 1447]` | 특성별 **분할 횟수**(`importance_type='split'` 기본). 310그루 안에서 당도로 2,284번, pH로 1,447번, 알코올로 579번 갈랐다 |

세 숫자의 합 4,310은 310그루 × 평균 14번 분할 — 리프 15개짜리 트리는 분할이 14개라서 **거의 모든 트리가 리프 15개를 꽉 채웠다**는 뜻이다(`num_leaves`가 실제로 걸렸다는 증거). 앞 노트에서 적었듯 이 숫자는 **횟수**라 XGBoost의 `gain` 비율과 바로 비교할 수 없다. `model.booster_.feature_importance(importance_type='gain')`으로 바꿔 읽으면 `[4173, 30862, 6195]` — 당도가 손실 감소의 75 %를 차지해 결정 트리·랜덤 포레스트에서 본 "당도 하나가 거의 다"와 같은 그림이 된다. 분할 횟수로는 pH가 알코올의 2.5배인데, 이득으로는 1.5배다 — pH는 자주 쓰이지만 한 번에 조금씩 줄이는 특성이다.

### 1-5. 정확도 둘과 macro F1 — 격차 3점

```python
from sklearn.metrics import f1_score
Y_pred = model.predict(X_test)
print(model.score(X_train, Y_train))              # 0.8845
print(model.score(X_test, Y_test))                # 0.8523  → 훈련 − 테스트 ≈ 0.03 (3 %)
print(f1_score(Y_test, Y_pred, average='macro'))  # 0.8192
```

수업 주석이 훈련·테스트 격차를 **"0.03 → 3 %(10 % 아래)"** 라고 읽어 둔 것이 이 셋에서 건질 핵심이다. 앞 노트들의 숫자와 함께 보면 이렇다(같은 분할, 이 노트에서 확인).

| 모델 | 훈련 | 테스트 | 격차 | macro F1 | 레드 재현율 | 혼동행렬 `[[레드→레드, 레드→화이트], [화이트→레드, 화이트→화이트]]` |
| --- | --- | --- | --- | --- | --- | --- |
| 결정 트리 (제한 없음) | 0.998 | 0.865 | 13점 | 0.816 | 0.706 | `[[226, 94], [81, 899]]` |
| 랜덤 포레스트 (제한 없음) | 0.998 | **0.889** | 11점 | **0.849** | 0.756 | `[[242, 78], [66, 914]]` |
| LightGBM day17 설정 `100 × 0.05, depth 4` | 0.880 | 0.861 | 2점 | 0.807 | 0.675 | `[[216, 104], [77, 903]]` |
| **LightGBM day18 설정 + 조기 종료 310그루 (수업)** | **0.885** | **0.852** | **3점** | **0.819** | **0.863** | `[[276, 44], [148, 832]]` |
| 같은 설정, 조기 종료 없이 1,000그루 | 0.917 | 0.861 | 6점 | 0.828 | 0.859 | `[[275, 45], [136, 844]]` |
| 같은 설정, `class_weight=None` | 0.896 | 0.862 | 3점 | 0.809 | 0.688 | `[[220, 100], [80, 900]]` |

읽히는 것이 셋이다. ① **테스트 정확도 0.852는 day17의 100그루(0.861)보다 오히려 낮다.** 그런데 macro F1은 0.807 → 0.819로 올랐고 레드 재현율은 0.675 → **0.863**으로 크게 올랐다 — 혼동행렬에서 레드 320병 중 틀린 것이 104 → 44로 줄고, 대신 화이트 쪽 오답이 77 → 148로 늘었다. 이것이 `class_weight="balanced"`가 한 일이다. 랜덤 포레스트 노트에서 본 그대로 "정확도를 올리는 인자가 아니라 **어느 쪽을 틀릴지를 옮기는** 인자"라서, 정확도 하나로 보면 손해처럼 보이고 F1·재현율로 보면 이득이다. 같은 설정에서 `class_weight`만 빼면 정확도 0.862 · 레드 재현율 0.688로 day17 모양으로 돌아간다. ② **격차 3점.** 조기 종료 없이 1,000그루를 다 쌓으면 훈련 0.917로 올라 격차가 6점으로 벌어지고 테스트는 0.861로 1점 오른다 — 트리를 늘릴수록 훈련 자료를 외우는 부스팅의 성질이고, 조기 종료가 그 중간에서 끊은 것이다. 주석의 "10 % 아래"는 격차가 두 자리로 벌어지면 과대적합을 의심하라는 실무 눈대중이며, 트리·숲의 11~13점이 바로 그 예다. ③ 숲의 0.889에는 여전히 못 미친다. 특성이 셋뿐인 작은 자료에서는 깊은 숲이 이미 충분하고, 부스팅은 리프 15개·행 80 %로 눌려 있다 — 앞 노트의 "부스팅이 항상 이기지는 않는다"가 이번에도 그대로다.

### 1-6. 새 와인 두 병 예측 — DataFrame으로 넣기

```python
new_wine = pd.DataFrame([[11.5, 2.3, 3.1], [13.8, 11.2, 3.3]])   # 알코올, 당도, pH
new_pred = model.predict(new_wine)
print('예측1 : ', new_pred[0])   # 0 : 레드
print('예측2 : ', new_pred[1])   # 1 : 화이트
```

학습 때 `X`가 DataFrame이었으니 새 자료도 **2차원**으로, 열 순서를 학습 때와 같게(알코올 → 당도 → pH) 만들어 넣는다. 당도 2.3의 드라이한 병은 레드(0), 당도 11.2의 단 병은 화이트(1) — 결정 트리 노트에서 루트 질문이 `sugar <= 4.325`였던 것과 맞는 결과다. `predict_proba`로 확률까지 보면 첫 병은 `[0.543, 0.457]`로 **간신히** 레드, 둘째 병은 `[0.046, 0.954]`로 확실한 화이트다. 분류 결과만 보면 둘 다 자신 있게 맞힌 것처럼 보이지만 확률을 열어 보면 첫 병은 반반에 가깝다는 것을 알 수 있어서, 임계값을 옮기거나 "애매함"을 표시해야 하는 서비스(day16의 예측 웹 서비스처럼)라면 `predict` 대신 `predict_proba`를 돌려주는 편이 안전하다. 새 자료를 만들 때 `columns=['alcohol', 'sugar', 'pH']`를 함께 주면 학습 때의 열 이름과 맞춰지므로 열 순서 실수를 막고 "특성 이름이 없다"는 경고도 피할 수 있다.

## 2. 추가로 알면 좋은 활용법

### 2-1. 검증 세트를 훈련에서 따로 떼기

```python
X_tr, X_va, Y_tr, Y_va = train_test_split(X_train, Y_train, test_size=0.2, random_state=42, stratify=Y_train)
model.fit(X_tr, Y_tr, eval_set=[(X_va, Y_va)], callbacks=[early_stopping(50, verbose=False)])
print(model.best_iteration_)            # 391
print(model.score(X_test, Y_test))      # 0.843  — 테스트는 끝까지 손대지 않은 숫자
```

조기 종료의 `eval_set`은 **"몇 그루에서 멈출까"를 정하는 자료**다. 그 자리에 테스트 세트를 넣으면 테스트가 모델 선택(트리 수)에 참여한 셈이 되어 테스트 점수가 조금 후해진다. 훈련 세트에서 다시 20 %를 떼어 검증 세트로 쓰면 훈련 4,157 · 검증 1,040 · 테스트 1,300의 세 덩이가 되고, 이 자료에서는 391그루에서 멈춰 테스트 0.843이 나온다 — 1-5의 0.852보다 1점 낮은 이 숫자가 "처음 보는 자료"의 정직한 점수에 가깝다. day14의 교차 검증이 "하이퍼파라미터를 고르는 데 테스트를 쓰지 않기"였던 것과 같은 원칙이고, 교차 검증과 조기 종료를 같이 쓰려면 `GridSearchCV` 안에서 폴드마다 검증 세트를 떼는 수고가 필요해 보통은 **`learning_rate`를 고정하고 트리 수만 조기 종료로** 정한다.

### 2-2. 손실 곡선 보기 — `evals_result_`와 `log_evaluation`

```python
from lightgbm import log_evaluation
model.fit(X_train, Y_train, eval_set=[(X_train, Y_train), (X_test, Y_test)], eval_names=['train', 'valid'],
          callbacks=[early_stopping(50, verbose=False), log_evaluation(period=100)])
# [100]  train's binary_logloss: 0.314  valid's binary_logloss: 0.353
# [200]  train's binary_logloss: 0.279  valid's binary_logloss: 0.340
# [300]  train's binary_logloss: 0.257  valid's binary_logloss: 0.336
import matplotlib.pyplot as plt
res = model.evals_result_
plt.plot(res['train']['binary_logloss'], label='train'); plt.plot(res['valid']['binary_logloss'], label='valid')
plt.axvline(model.best_iteration_, ls='--'); plt.legend()
```

`eval_set`에 훈련 세트도 같이 넣으면 **훈련 손실과 검증 손실 두 곡선**이 생기고, 둘이 벌어지기 시작하는 지점이 과대적합의 시작이다 — 이 자료에서는 100그루에서 0.314 · 0.353으로 4점 차이던 것이 300그루에서 0.257 · 0.336으로 8점 차로 벌어지고, 훈련 손실은 계속 내려가는데 검증 손실만 310그루에서 바닥을 친다. 1-3의 표는 이 `evals_result_` 딕셔너리에서 꺼낸 것이다. `log_evaluation(period=100)`은 100그루마다 손실을 찍는 콜백으로, `verbose=-1`로 전체 로그를 끈 채 **필요한 줄만** 보는 조합이 된다. `eval_metric='auc'`·`'binary_error'`처럼 지표를 바꿔 조기 종료 기준으로 쓸 수도 있는데, 여러 지표를 넣었을 때 첫 지표만 기준으로 삼으려면 `early_stopping(50, first_metric_only=True)`를 준다.

### 2-3. 멈춘 자리에서 다시 — `best_iteration_`로 `n_estimators` 고정

```python
best = model.best_iteration_                              # 310
final = LGBMClassifier(**{**model.get_params(), 'n_estimators': best})
final.fit(X_train, Y_train)                               # eval_set 없이 310그루
final.score(X_test, Y_test)                               # 0.8523 — 1-5와 같다
```

조기 종료로 찾은 트리 수를 그대로 `n_estimators`에 박아 **검증 세트 없이** 다시 학습하면, 1-5의 모델과 숫자가 같다(이 노트에서 확인 — 훈련 0.8845 · 테스트 0.8523 · F1 0.8192). 이것이 "조기 종료는 트리 수를 고르는 도구"라는 말의 뜻이고, 2-1처럼 검증 세트를 뗀 뒤 최종 모델은 **훈련 + 검증을 합쳐** 그 트리 수로 다시 기르는 것이 흔한 마무리다. `joblib.dump(final, …)`로 저장해 day16처럼 서비스에 올리면 예측 때 `eval_set`을 신경 쓸 일이 없다.

### 2-4. 인자 하나씩 바꿔 보면

1-2의 수업 값을 기준으로 하나만 바꿔 같은 조기 종료(검증 = 테스트, 50그루)로 돌린 결과다(이 노트에서 확인).

| 바꾼 것 | 멈춘 트리 | 테스트 | macro F1 | 읽히는 것 |
| --- | --- | --- | --- | --- |
| **수업 값** | 310 | 0.852 | 0.819 | 기준 |
| `learning_rate=0.1` | 133 | 0.846 | 0.812 | 보폭 2배 → 트리 수 절반 이하, 점수는 조금 낮음 |
| `learning_rate=0.01` | 1000 (안 멈춤) | 0.845 | 0.812 | 보폭이 작아 1,000그루로도 바닥에 못 닿음 — 상한을 더 줘야 한다 |
| `num_leaves=31` (기본) | 261 | 0.851 | 0.817 | 리프가 많아 트리 하나가 더 맞히니 더 일찍 멈춤 |
| `num_leaves=63, max_depth=-1` | 139 | 0.855 | 0.823 | 더 복잡한 트리 → 139그루에서 끝. 점수는 비슷 |
| `subsample=1.0, colsample_bytree=1.0` | 594 | 0.861 | 0.827 | 부분 추출을 끄면 트리끼리 닮아 더 오래 걸리고, 이 작은 자료에선 점수가 오히려 조금 높다 |
| `min_child_samples=5` | 312 | 0.852 | 0.820 | 거의 변화 없음 — 5,197병에 리프 15개면 리프당 수백 병이라 20이나 5나 안 걸린다 |
| `class_weight=None` | 275 | 0.862 | 0.809 | 1-5 — 정확도 ↑ 레드 재현율 0.863 → 0.688 ↓ |

`learning_rate`와 **멈춘 트리 수가 반비례**하는 것이 가장 분명하다 — 보폭 0.1이면 133그루, 0.05면 310그루, 0.01이면 1,000그루로도 모자란다. 그래서 보폭을 작게 할수록 `n_estimators` 상한을 함께 올려야 하고, 상한에 닿은 채 끝났다면(`best_iteration_ == n_estimators`) 조기 종료가 작동하지 않은 것이므로 상한을 늘려 다시 돌린다. 트리 모양 인자(`num_leaves`·`max_depth`·`min_child_samples`)는 이 자료에서는 점수를 거의 움직이지 않는다 — 특성이 셋뿐이라 트리를 더 복잡하게 만들어도 볼 것이 없다. 수십 개 특성·수십만 행에서 이 표를 다시 그리면 `num_leaves`·`subsample`이 주역이 된다.

### 2-5. 불균형 인자 두 가지 — `class_weight`와 `is_unbalance`·`scale_pos_weight`

LightGBM의 사이킷런 래퍼는 `class_weight="balanced"` 외에 네이티브 인자 `is_unbalance=True`(자동 보정)와 `scale_pos_weight`(양성 가중치, 앞 노트 2-3)도 받는다. 셋을 동시에 켜면 보정이 겹치므로 **하나만** 쓴다. `class_weight`는 사이킷런 표준이라 `GridSearchCV`의 `param_grid`에 `{'class_weight': [None, 'balanced']}`로 넣어 F1 기준으로 켜고 끌 수 있고, 1-5의 표가 보여 주듯 "정확도 1점 vs 레드 재현율 18점"의 거래를 평가 지표(`scoring='f1_macro'`)가 정하게 하는 편이 안전하다.

## 3. 더 나아가 알면 좋은 것

### 3-1. LightGBM이 빠른 이유 — 히스토그램·GOSS·EFB

앞 노트에서 리프 단위 성장과 히스토그램 255구간을 적었다. 여기에 둘이 더 있다. **GOSS**(Gradient-based One-Side Sampling)는 기울기가 큰(= 아직 못 맞히는) 표본은 전부 쓰고 기울기가 작은 표본만 일부 뽑아 분할 후보를 찾는 방식이고, **EFB**(Exclusive Feature Bundling)는 동시에 0이 아닌 일이 없는 희소 특성들을 한 열로 묶어 특성 수를 줄인다. 둘 다 "정확도를 거의 잃지 않고 계산을 줄이는" 장치라서 LightGBM이 수백만 행에서도 돌아가는 이유다. `subsample`이 "무작위로 80 %"라면 GOSS는 "틀린 것 위주로 골라서"라는 차이가 있고, `boosting_type='goss'`로 켤 수 있다(그때 `subsample`은 쓰지 않는다).

### 3-2. 조기 종료의 다른 얼굴들

같은 생각이 모델마다 다른 이름으로 있다. XGBoost는 생성자 `early_stopping_rounds` + `fit(eval_set=…)`, CatBoost는 `od_type='Iter', od_wait=50` 또는 `early_stopping_rounds`, 신경망(케라스)은 `EarlyStopping(patience=…)` 콜백, 사이킷런의 `HistGradientBoostingClassifier`는 `early_stopping='auto'`가 기본이라 표본이 1만 개를 넘으면 **자동으로 검증 10 %를 떼어** 조기 종료한다(`early_stopping=True`로 강제할 수 있다). 공통점은 "훈련 손실이 아니라 **처음 보는 자료의 손실**이 더 안 내려가면 멈춘다"는 것이고, 앞 노트 3-1의 함수 공간 경사 하강에서 보폭(`learning_rate`)과 걸음 수(`n_estimators`)가 짝이라는 것을 떠올리면 조기 종료는 **걸음 수를 자료가 정하게 하는 장치**다. day13의 릿지 `alpha`가 계수를 눌러 과대적합을 막았다면, 조기 종료는 학습을 **시간축에서** 잘라 같은 일을 한다.

### 3-3. 인자 탐색 자동화 — Optuna·`RandomizedSearchCV`

인자가 아홉 개가 되면 격자 탐색은 조합 수가 폭발한다(값 3개씩만 줘도 3⁹ ≈ 2만). `RandomizedSearchCV(n_iter=50)`로 무작위 50조합만 보거나, **Optuna**처럼 앞 시도의 결과를 보고 다음 후보를 고르는 베이지안 탐색을 쓴다. Optuna는 LightGBM과 궁합이 좋아 `optuna.integration.lightgbm` 모듈이 단계별 튜닝(`feature_fraction` → `num_leaves` → `bagging` → 규제 → `min_child_samples`)을 자동으로 해 준다. 어느 방법이든 `learning_rate`는 작게 고정하고 **트리 수는 조기 종료에 맡기는** 것이 관례다.

### 3-4. 다음에 볼 키워드

- `evals_result_`·`log_evaluation`·`eval_metric`·`first_metric_only` — 손실 곡선 읽기와 조기 종료 기준 바꾸기
- `best_iteration_`로 `n_estimators` 고정 → 훈련 + 검증 합쳐 재학습 → `joblib.dump`
- `bagging_fraction`·`bagging_freq`·`feature_fraction` — 네이티브 이름과 사이킷런 래퍼 이름 대응
- `importance_type='gain'`·`booster_.feature_importance` — 분할 횟수 대신 이득으로
- `is_unbalance`·`scale_pos_weight`·`predict_proba` 임계값 조정
- `boosting_type='goss'`·`'dart'`, GOSS·EFB
- Optuna·`RandomizedSearchCV`·`lightgbm.cv`
- SHAP(`shap.TreeExplainer`) — 특성 중요도를 표본 하나 단위로

## 실습 파일

- `KDT_2026/2026_Python/day18/s-11.py` — `pd.read_csv(URL)` 와인 자료 → `X`(알코올·당도·pH)·`Y`(class) → `train_test_split(test_size=0.2, random_state=42, stratify=Y)` → `from lightgbm import LGBMClassifier`(회귀는 `LGBMRegressor`) → `LGBMClassifier(n_estimators=1000, learning_rate=0.05, num_leaves=15, max_depth=6, min_child_samples=20, subsample=0.8, subsample_freq=1, colsample_bytree=0.8, class_weight="balanced", verbose=-1, random_state=42, n_jobs=-1)` 인자 아홉 개 주석 → `from lightgbm import early_stopping` → `fit(X_train, Y_train, eval_set=[(X_test, Y_test)], callbacks=[early_stopping(stopping_rounds=50, verbose=False)])` → `best_iteration_`(310)·`feature_name_`(`['alcohol', 'sugar', 'pH']`)·`feature_importances_`(`[579 2284 1447]`) → `score` 훈련 0.8845 · 테스트 0.8523(주석: 격차 0.03 → 3 %, 10 % 아래)·`f1_score(average='macro')` 0.8192 → `pd.DataFrame([[11.5, 2.3, 3.1], [13.8, 11.2, 3.3]])` 새 와인 `predict` → 0 레드 · 1 화이트. 이 노트에서 돌린 결과(`random_state=42`, lightgbm 4.7): 수업 값 그대로 310 · `[579 2284 1447]` · 0.8845 / 0.8523 / 0.8192 일치, 360그루에서 멈춤(310 + 50), 검증 손실 1그루 0.668 → 100그루 0.353 → 310그루 0.3346 최솟값, 레드 재현율 0.863 · 혼동행렬 `[[276, 44], [148, 832]]`, gain 중요도 `[4173, 30862, 6195]`, `predict_proba` `[0.543, 0.457]`·`[0.046, 0.954]` / 조기 종료 없이 1,000그루 0.917 · 0.861 / `class_weight=None` 0.862 · 레드 재현율 0.688 / 검증 세트 분리 391그루 · 테스트 0.843 / `learning_rate` 0.1 → 133그루 · 0.01 → 1,000그루 안 멈춤 / `stopping_rounds` 10 → 226그루

## 관련 노트

[[AI 정리본 인덱스]] · [[AI day17 XGBoost·LightGBM 부스팅 분류기 설정과 모델 딕셔너리]] · [[AI day17 랜덤 포레스트로 와인 분류와 class_weight·max_features]] · [[AI day17 결정 트리로 와인 레드·화이트 분류와 plot_tree]] · [[AI day14 KFold 교차 검증과 GridSearchCV 하이퍼파라미터 탐색]] · [[AI day18 Optuna 스터디·목적함수 설정과 판다스 category 타입]] · [[KDT_2026 학습 지도]]
