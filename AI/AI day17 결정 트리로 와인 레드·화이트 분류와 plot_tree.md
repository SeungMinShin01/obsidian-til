---
출처: Claude 분석
원본: KDT_2026/2026_Python/day17/s-09.py
작성일: 2026-11-13
tags: [학습, ai, python]
---

# AI day17 — 결정 트리로 와인 레드·화이트 분류와 plot_tree

> 실습 파일: `day17/s-09.py`
> 허브: [[AI 정리본 인덱스]] · 이전: [[AI day16 의료비 데이터 전처리와 ColumnTransformer·다항 릿지 그리드서치 실습]] · 다음: (아직 없음)

day12부터 day16까지는 모델이 전부 **선형**(선형 회귀·다항 회귀·릿지·로지스틱 회귀)이었다. day17은 처음으로 선형이 아닌 모델, **결정 트리(Decision Tree)**를 쓴다. 자료는 혼공머신 교재의 와인 데이터(`wine.csv`, 6,497병 × 알코올 도수·당도·pH → `class` 0 레드 / 1 화이트)이고, 과제는 세 가지 화학 수치로 **레드 와인인지 화이트 와인인지 맞히기**다. 코드는 짧다. 읽기 → 특성·타깃 → `stratify` 분할 → `DecisionTreeClassifier().fit` → 훈련·테스트 정확도 → `plot_tree`로 나무 그리기 → `max_depth`·`min_samples_leaf`를 건 **두 번째 트리**를 다시 학습해 점수 비교. 뼈대는 day14 로지스틱 분류와 똑같고 바뀐 것은 **모델 한 줄과 시각화 한 줄**뿐인데, 그 한 줄이 "기울기를 배우는 모델"에서 "질문을 배우는 모델"로 넘어가는 자리다. 그리고 뒤에 붙은 두 번째 모델이 그 나무를 **얼마나 자라게 둘지** 정하는 첫 경험이다.

## 1. 배운 내용

### 1-1. URL에서 바로 읽기와 자료 모양

```python
url = 'https://raw.githubusercontent.com/rickiepark/hg-mldl/master/wine.csv'
import pandas as pd
df = pd.read_csv(url)
# alcohol, sugar, pH, class (0: 레드 / 1: 화이트)
```

`read_csv`는 로컬 경로뿐 아니라 **URL 문자열**도 그대로 받는다. GitHub의 `raw.githubusercontent.com` 주소는 파일 내용만 돌려주므로 다운로드 없이 바로 DataFrame이 된다. 자료를 살펴보면 이렇다(이 노트에서 같은 코드로 확인).

| 항목 | 값 | 읽는 법 |
| --- | --- | --- |
| `shape` | `(6497, 4)` | 지금까지 다룬 자료 중 가장 크다(Fish 159 · insurance 1,338) |
| `alcohol` | 8.0~14.9, 평균 10.5 | 도수(%) |
| `sugar` | 0.6~65.8, 평균 5.4, 중앙값 3.0 | 잔당(g/L). 오른쪽 꼬리가 아주 길다 |
| `pH` | 2.72~4.01, 평균 3.22 | 산도 |
| `class` | 1(화이트) 4,898 · 0(레드) 1,599 ≈ 75 : 25 | 타깃. 클래스 불균형이 꽤 있다 |
| 결측 | 0 | 전처리 없이 바로 간다 |

타깃 `class`가 `0.0`·`1.0` 실수로 저장되어 있지만 값이 두 가지뿐이라 사이킷런은 분류 타깃으로 그대로 받는다.

### 1-2. 특성·타깃 분리와 `stratify` 분할

```python
X = df[['alcohol', 'sugar', 'pH']]    # 독립변수 — 2차원
Y = df['class']                       # 종속변수 — 1차원

from sklearn.model_selection import train_test_split
X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size=0.2, random_state=42, stratify=Y)
```

day12의 "특성은 이중 대괄호로 2차원, 타깃은 홑 대괄호로 1차원" 규칙 그대로다. `stratify=Y`는 day14 분류 노트에서 배운 대로 **훈련·테스트의 클래스 비율을 원본과 같게** 맞춘다. 75 : 25 자료를 그냥 나누면 테스트에 레드가 우연히 적게 들어갈 수 있는데, 층화 분할이면 훈련 5,197(화이트 3,918 · 레드 1,279)·테스트 1,300(화이트 980 · 레드 320)으로 양쪽 다 정확히 75 : 25가 된다. 분류 문제에서는 습관처럼 붙이는 인자다.

### 1-3. `DecisionTreeClassifier` — 질문을 배우는 모델

```python
from sklearn.tree import DecisionTreeClassifier, DecisionTreeRegressor

model = DecisionTreeClassifier()
model.fit(X_train, Y_train)

print("Train Acc : ", model.score(X_train, Y_train))   # 0.998
print("Test Acc : ",  model.score(X_test,  Y_test))    # 0.865
```

로지스틱 회귀가 "알코올 × a + 당도 × b + pH × c + 절편"이라는 **직선 하나**로 경계를 긋는다면, 결정 트리는 **"당도가 4.33 이하인가?" → "알코올이 11.03 이하인가?" …** 식으로 특성 하나씩 기준값과 비교하는 **질문(노드)을 위에서 아래로 쌓아** 분류한다. 질문을 따라 내려가 더 나눌 수 없는 끝(리프)에 닿으면 그 리프에 많은 쪽 클래스가 답이다.

| 용어 | 뜻 |
| --- | --- |
| 루트 노드 | 맨 위 첫 질문. 전체 훈련 자료가 여기서 시작한다 |
| 노드(분기) | "특성 ≤ 기준값"의 참/거짓으로 자료를 둘로 가르는 질문 |
| 리프 노드 | 더 이상 가르지 않는 끝. 들어온 표본 중 다수 클래스가 예측값 |
| 깊이(depth) | 루트에서 리프까지 질문 수. 제한하지 않으면 리프가 거의 순수해질 때까지 자란다 |
| 지니 불순도(gini) | 노드 안이 얼마나 섞였는가. `1 − (p₀² + p₁²)`. 한 클래스뿐이면 0, 반반이면 0.5 |

트리는 **불순도를 가장 많이 줄이는 질문**을 매 노드에서 고른다. 루트의 지니는 `1 − (0.246² + 0.754²) ≈ 0.371`이고, 여기서 `sugar ≤ 4.325`로 가르는 것이 모든 특성·모든 기준값 중 불순도를 가장 크게 떨어뜨리는 질문이라 첫 질문이 된다. 선형 모델과 달리 **표준화가 필요 없다** — 기준값 비교는 열의 크기 단위에 영향을 받지 않으므로 `StandardScaler`를 끼우지 않아도 결과가 같다. day13부터 늘 앞에 붙이던 표준화 단계가 트리에서 빠지는 이유가 이것이다.

점수를 읽으면 훈련 0.998 · 테스트 0.865다. **훈련은 거의 만점인데 테스트는 13점 낮다** — 전형적인 과대적합이다. 제한 없이 자란 트리는 깊이 24, 리프 790개 안팎까지 뻗어 훈련 자료 한 병 한 병을 외우다시피 하는데, 그렇게 외운 규칙은 처음 보는 자료에는 그만큼 들어맞지 않는다. 같은 자료의 로지스틱 회귀(표준화 포함)가 훈련 0.783 · 테스트 0.776인 것과 비교하면, 트리는 **훨씬 잘 맞히지만 그만큼 외우기도 잘하는** 모델이라는 두 얼굴이 한눈에 보인다.

`DecisionTreeClassifier()`에 `random_state`를 넣지 않았다. 트리는 분기 후보 특성을 고를 때 순서를 무작위로 섞기 때문에, 불순도 감소량이 같은 후보가 있으면 실행마다 조금 다른 나무가 나온다. 이 자료에서는 테스트 정확도가 0.865~0.866 사이에서 흔들리는 정도다. 노트의 숫자를 그대로 다시 얻으려면 `random_state=42`를 넣는 편이 안전하다.

### 1-4. `plot_tree` — 배운 질문을 그림으로

```python
import matplotlib.pyplot as plt
from sklearn.tree import plot_tree

plot_tree(model, max_depth=2, feature_names=['alcohol', 'sugar', 'pH'])
plt.show()
```

| 인자 | 뜻 |
| --- | --- |
| `max_depth=2` | 루트부터 2단계까지만 그린다. 깊이 24짜리 나무를 전부 그리면 글자가 보이지 않는다 |
| `feature_names` | 노드 글자에 `x[1] <= 4.325` 대신 `sugar <= 4.325`로 열 이름을 쓴다 |

`plot_tree`는 맷플롯립 `pyplot`의 현재 figure에 그리므로 `import matplotlib.pyplot as plt`를 가져와 두어야 `plt.show()`로 창이 뜬다(`matplotlib` 패키지 자체에는 `show`가 없다). 그려진 노드 상자마다 네 줄이 적힌다.

```
sugar <= 4.325          ← 질문 (리프에는 없음)
gini = 0.371            ← 이 노드의 불순도
samples = 5197          ← 이 노드에 들어온 훈련 표본 수
value = [1279, 3918]    ← [레드, 화이트] 개수 → 다수인 화이트가 이 노드의 예측
```

왼쪽 가지가 "참(≤)", 오른쪽이 "거짓(>)"이다. 이 노트에서 `random_state=42`로 확인한 위 2단을 글로 옮기면 이렇다.

| 깊이 | 질문 | 의미 |
| --- | --- | --- |
| 0 | `sugar <= 4.325` | 당도가 낮은 쪽(왼쪽)에 레드가 몰려 있다 |
| 1 왼쪽 | `sugar <= 1.625` | 당도가 아주 낮으면 다시 화이트 쪽 |
| 1 오른쪽 | `sugar <= 6.625` | 당도 4.3~6.6 사이는 pH로, 6.6 초과는 알코올로 다시 가른다 |

레드 와인은 대체로 드라이(당도 낮음)하고 화이트는 단 것이 많다는 상식이 첫 질문에 그대로 나온다. 결정 트리의 가장 큰 장점이 이것이다 — 계수 세 개를 보고 해석해야 하는 로지스틱 회귀와 달리, **왜 그렇게 분류했는지가 질문 순서로 설명된다.** 다만 그림의 노드 글자는 노드 깊이가 조금만 깊어져도 작아지므로 `plt.figure(figsize=(12, 7))`로 figure를 먼저 키우는 편이 보기 편하다.

### 1-5. 같은 줄에서 가져온 `DecisionTreeRegressor`

import 줄에 `DecisionTreeRegressor`가 함께 있다. 쓰이진 않았지만 짝을 알아 두면 된다 — 트리는 **분류와 회귀 양쪽**에 쓰이고, 회귀 트리는 리프의 다수 클래스 대신 **리프에 들어온 표본의 타깃 평균**을 예측값으로 낸다. 불순도 대신 분산(MSE)을 줄이는 질문을 고른다. day16 의료비 회귀를 `Ridge` 대신 `DecisionTreeRegressor`로 바꿔 보면 흡연 여부로 먼저 갈라지는 나무가 나온다.

### 1-6. 흐름 한 장 — 로지스틱 분류와의 대조

| 단계 | day14 `s-06.py`(로지스틱) | day17 `s-09.py`(트리) |
| --- | --- | --- |
| 자료 | Fish 도미·빙어 | wine 레드·화이트 6,497병 |
| 분할 | `train_test_split(…, stratify=Y)` | 같음 |
| 표준화 | `StandardScaler` 필요 | **필요 없음** |
| 모델 | `LogisticRegression()` | `DecisionTreeClassifier()` |
| 평가 | `score` → 정확도 | 같음 |
| 해석 | `coef_`·`intercept_`(기울기) | `plot_tree`(질문 순서) |

### 1-7. 제한을 걸고 다시 학습 — `max_depth`·`min_samples_leaf`·`criterion`·`random_state`

```python
model = DecisionTreeClassifier(
    max_depth=3,
    min_samples_leaf=10,
    criterion="gini",
    random_state=42,
)
model.fit(X_train, Y_train)
print("Train Acc : ", model.score(X_train, Y_train))   # 0.846
print("Test Acc : ",  model.score(X_test,  Y_test))    # 0.841
```

1-3의 트리를 그대로 두지 않고, 같은 자료로 **인자 네 개를 건 두 번째 트리**를 다시 학습해 점수를 나란히 놓는다. 생성자에 넣는 인자가 전부 "나무가 얼마나 자랄지"를 정하는 하이퍼파라미터다.

| 인자 | 뜻 | 기본값 |
| --- | --- | --- |
| `max_depth=3` | 질문을 루트부터 **세 단**까지만 쌓는다. 리프는 최대 2³ = 8개 | `None`(제한 없음) |
| `min_samples_leaf=10` | 가르고 난 뒤 **리프에 표본이 10개 미만**이 되는 분기는 만들지 않는다 | `1` |
| `criterion` | 분기 질문을 고를 때 쓰는 불순도 기준. `'gini'`(기본)·`'entropy'`·`'log_loss'` 셋 중 하나만 받고, 그 밖의 문자열은 `fit`에서 `InvalidParameterError`로 멈춘다 | `'gini'` |
| `random_state=42` | 불순도 감소량이 같은 후보 질문의 순서를 고정한다 → 실행마다 같은 나무 | `None` |

결과를 1-3과 나란히 두면 이렇다(이 노트에서 확인).

| 모델 | 훈련 | 테스트 | 격차 | 깊이 | 리프 수 |
| --- | --- | --- | --- | --- | --- |
| `DecisionTreeClassifier()` | 0.998 | 0.865 | 13.3점 | 24 | 789 |
| `max_depth=3, min_samples_leaf=10` | 0.846 | 0.841 | 0.5점 | 3 | 8 |

테스트 점수는 2.4점 내려갔지만 **훈련·테스트 격차가 13점에서 0.5점으로** 붙었다. 제한 없는 트리가 훈련 자료를 외운 결과를 테스트에서 못 쓰는 것과 달리, 깊이 3짜리는 배운 만큼 처음 보는 자료에도 그대로 맞힌다 — 이것이 과대적합을 눌렀다는 뜻이다. 핵심은 "테스트 점수가 가장 높은 모델"이 아니라 **"훈련과 테스트가 같이 가는 모델"**을 고르는 쪽이 안전하다는 점이다.

깊이 3 나무를 `export_text`로 읽으면 레드로 가는 리프가 **하나뿐**이다.

```
sugar <= 4.33
├─ sugar <= 1.62  → 화이트 (둘 다)
└─ sugar >  1.62
   ├─ alcohol <= 11.03 → 레드   ← 유일한 레드 리프
   └─ alcohol >  11.03 → 화이트
sugar >  4.33      → 화이트 (pH로 한 번 더 갈라도 넷 다 화이트)
```

풀어 쓰면 **"당도 1.6~4.3이고 알코올 11도 이하면 레드, 나머지는 화이트"**라는 규칙 하나가 정확도 0.84를 만든다. 특성 중요도도 당도 0.855 · 알코올 0.139 · pH 0.007로, 1-3의 깊은 나무(당도 0.515)보다 당도 쏠림이 훨씬 심하다 — pH 질문은 둘로 갈라도 양쪽 다 화이트라 불순도를 거의 줄이지 못한다. 혼동행렬로 보면 화이트 재현율 0.91 · 레드 재현율 0.62로, 얕은 나무는 소수 클래스인 레드를 많이 놓친다. 정확도 0.84 뒤에 이런 치우침이 있다는 것은 day15의 분류 리포트로만 보인다.

`min_samples_leaf=10`은 이 자료의 깊이 3 나무에서는 점수를 거의 바꾸지 않는다(0.8459 → 0.8457). `max_depth=3`만 걸면 리프 하나에 표본이 1개뿐인 가지가 생기는데, `min_samples_leaf=10`이 그 분기를 막아 기준값을 옮겨 리프 크기가 133이 된다 — 점수보다 **너무 작은 리프를 만들지 않는 안전장치**로 읽는 편이 맞다. 깊이를 제한하지 않고 이 값만 올리면 효과가 뚜렷하다.

| `min_samples_leaf` (깊이 제한 없음) | 훈련 | 테스트 | 깊이 | 리프 수 |
| --- | --- | --- | --- | --- |
| 1 | 0.998 | 0.865 | 24 | 789 |
| 10 | 0.899 | 0.862 | 14 | 222 |
| 50 | 0.878 | 0.860 | 10 | 64 |
| 100 | 0.867 | 0.849 | 7 | 34 |

리프 최소 표본을 10으로만 올려도 리프 수가 789 → 222로 줄고 훈련 점수가 10점 내려오는데 테스트는 거의 그대로다. `max_depth`가 "위에서 깊이를 자르는" 방법이라면 `min_samples_leaf`는 "아래에서 잔가지를 막는" 방법이고, 둘을 같이 거는 것이 두 번째 모델이다.

## 2. 추가로 알면 좋은 활용법

### 2-1. `max_depth`로 가지치기 — 과대적합 줄이기

```python
for d in [1, 2, 3, 4, 5, 8, None]:
    m = DecisionTreeClassifier(max_depth=d, random_state=42).fit(X_train, Y_train)
    print(d, round(m.score(X_train, Y_train), 3), round(m.score(X_test, Y_test), 3))
```

| `max_depth` | 훈련 | 테스트 |
| --- | --- | --- |
| 1 | 0.754 | 0.754 |
| 2 | 0.806 | 0.811 |
| 3 | 0.846 | 0.841 |
| 5 | 0.872 | 0.858 |
| 8 | 0.900 | 0.859 |
| None | 0.998 | 0.865 |

깊이 1은 "당도 4.325 하나로만 가르기"라 화이트를 전부 맞히고 레드를 못 맞히는 수준(0.754 = 화이트 비율)이고, 깊이 3~5에서 훈련·테스트 차이가 1점 안쪽으로 붙는다. 그 뒤로는 훈련만 오르고 테스트는 제자리다. 테스트 정확도만 보면 제한 없는 트리(0.865)가 최고지만, **훈련·테스트 격차가 작고 설명이 쉬운 깊이 5(0.858)** 쪽이 실제로는 더 믿을 만한 모델이다. 이런 조정을 **가지치기(pruning)**라 하고, `max_depth` 외에 `min_samples_split`(노드를 가르려면 최소 몇 표본)·`min_samples_leaf`(리프에 최소 몇 표본)·`min_impurity_decrease`도 같은 역할을 한다. 1-7의 두 번째 모델(`max_depth=3, min_samples_leaf=10`)이 바로 이 표의 깊이 3 줄에 해당한다.

### 2-2. `feature_importances_` — 어느 특성이 많이 쓰였나

```python
print(dict(zip(['alcohol', 'sugar', 'pH'], model.feature_importances_.round(3))))
# {'alcohol': 0.234, 'sugar': 0.515, 'pH': 0.252}
```

각 특성이 트리 전체에서 불순도를 얼마나 줄였는지를 합이 1이 되게 정규화한 값이다. 당도가 절반을 차지하고 알코올·pH가 1/4씩이다. 로지스틱의 `coef_`가 "부호와 크기"를 말한다면 이 값은 "얼마나 자주·크게 쓰였나"를 말하며, 특성이 수십 개일 때 어느 것을 남길지 고르는 첫 기준이 된다.

### 2-3. `export_text` — 그림 대신 글로

```python
from sklearn.tree import export_text
print(export_text(model, feature_names=['alcohol', 'sugar', 'pH'], max_depth=2))
```

`plot_tree`와 같은 내용을 들여쓰기 텍스트로 출력한다. 터미널만 있는 환경이나 노트에 붙여 넣을 때는 이쪽이 편하고, `max_depth`로 자르는 것도 같다.

### 2-4. `GridSearchCV`로 깊이 고르기 — day14 틀 재사용

```python
from sklearn.model_selection import GridSearchCV, StratifiedKFold
grid = GridSearchCV(
    DecisionTreeClassifier(random_state=42),
    {'max_depth': range(2, 11), 'min_samples_leaf': [1, 5, 20]},
    cv=StratifiedKFold(5, shuffle=True, random_state=42), scoring='accuracy', n_jobs=-1
).fit(X_train, Y_train)
print(grid.best_params_, round(grid.best_score_, 3))
```

2-1에서 테스트 점수를 보며 깊이를 고르면 테스트 자료가 튜닝에 쓰여 버린다. day14·15에서 배운 대로 **교차 검증으로 고르고 테스트는 마지막 한 번만** 쓰는 것이 정석이고, 트리 모델도 같은 `GridSearchCV` 틀에 그대로 들어간다. 표준화 단계가 없으니 `Pipeline` 없이 모델을 바로 넣어도 된다.

### 2-5. 혼동행렬로 어느 쪽을 틀리는지 보기

```python
from sklearn.metrics import confusion_matrix, classification_report
pred = model.predict(X_test)
print(confusion_matrix(Y_test, pred))
print(classification_report(Y_test, pred, target_names=['red', 'white']))
```

75 : 25 불균형 자료에서는 정확도 0.865가 "화이트만 잘 맞히는" 결과일 수 있다. day15에서 배운 혼동행렬과 재현율·F1로 레드 쪽 재현율을 따로 확인해 두는 편이 안전하다.

## 3. 더 나아가 알면 좋은 것

### 3-1. 트리 하나에서 숲으로 — 랜덤 포레스트·그래디언트 부스팅

트리 하나는 자료가 조금만 바뀌어도 모양이 크게 달라지고(분산이 크다) 쉽게 과대적합한다. 그래서 실무에서는 트리 **여러 개를 모아** 쓴다. `RandomForestClassifier`는 부트스트랩 표본과 무작위 특성 부분집합으로 트리 수백 개를 길러 다수결을 내고, `GradientBoostingClassifier`·`HistGradientBoostingClassifier`는 앞 트리의 오답을 다음 트리가 고치는 식으로 얕은 트리를 순서대로 쌓는다. 둘 다 `fit`·`score`·`feature_importances_` 인터페이스가 같아서 이 노트의 코드에서 모델 한 줄만 바꾸면 된다. 와인 자료는 랜덤 포레스트에서 테스트 0.89 안팎까지 오른다.

### 3-2. 분기 기준 — 지니 vs 엔트로피, 축에 평행한 경계

`criterion='entropy'`로 바꾸면 지니 대신 정보 이득(엔트로피 감소)으로 질문을 고른다. 결과는 대체로 비슷하다. 더 본질적인 한계는 트리의 경계가 항상 **축에 평행한 직각 계단**이라는 점이다 — "알코올 + 당도 > 15" 같은 비스듬한 경계는 계단 여러 개로 흉내 낼 수밖에 없어 깊이가 깊어진다. 그런 자료는 선형 모델이나 특성 조합(`alcohol * sugar` 열 추가)이 더 낫다.

### 3-3. 비용 복잡도 가지치기와 검증 세트

`DecisionTreeClassifier(ccp_alpha=…)`는 리프 수에 벌점을 매겨 자란 나무를 뒤에서 잘라 내는 방식(cost-complexity pruning)이고, `cost_complexity_pruning_path`로 후보 alpha 목록을 뽑아 교차 검증으로 고른다. 교재에서는 훈련·**검증**·테스트 세 덩어리로 나눠 검증 세트로 깊이를 고르는 방법도 함께 다루는데, 자료가 충분히 클 때 교차 검증 대신 쓰는 단순한 대안이다.

### 3-4. 다음에 볼 키워드

- `RandomForestClassifier`·`ExtraTreesClassifier` — 배깅 앙상블
- `HistGradientBoostingClassifier`·XGBoost·LightGBM — 부스팅 앙상블
- `cost_complexity_pruning_path`·`ccp_alpha` — 사후 가지치기
- `permutation_importance` — 테스트 자료 기준 특성 중요도
- `DecisionTreeRegressor` — 회귀 트리(리프 평균)
- 교차 검증 + 검증 세트 — 하이퍼파라미터 고르기의 두 방법

## 실습 파일

- `KDT_2026/2026_Python/day17/s-09.py` — `pd.read_csv(URL)`(혼공머신 `wine.csv`, 6,497 × `alcohol`·`sugar`·`pH`·`class`) → `X = df[['alcohol', 'sugar', 'pH']]`·`Y = df['class']` → `train_test_split(test_size=0.2, random_state=42, stratify=Y)` → `DecisionTreeClassifier().fit` → 훈련·테스트 `score` → `plot_tree(model, max_depth=2, feature_names=[…])`·`show()` → `DecisionTreeClassifier(max_depth=3, min_samples_leaf=10, criterion=…, random_state=42)`로 두 번째 학습·`score` 비교. 결과(이 노트에서 `random_state=42`로 확인): 제한 없는 트리 훈련 0.998 · 테스트 0.865, 깊이 24, 루트 `sugar <= 4.325`, 특성 중요도 당도 0.515 · pH 0.252 · 알코올 0.234 / 깊이 3 트리 훈련 0.846 · 테스트 0.841, 리프 8, 레드 리프 1개(당도 1.62~4.33 & 알코올 ≤ 11.03)

## 관련 노트

[[AI 정리본 인덱스]] · [[AI day16 의료비 데이터 전처리와 ColumnTransformer·다항 릿지 그리드서치 실습]] · [[AI day14 로지스틱 회귀로 도미·빙어 분류]] · [[AI day14 KFold 교차 검증과 GridSearchCV 하이퍼파라미터 탐색]] · [[AI day15 로지스틱 다중 분류와 혼동행렬·분류 리포트]] · [[KDT_2026 학습 지도]]
