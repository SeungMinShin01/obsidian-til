---
출처: Claude 분석
원본: KDT_2026/2026_Python/day13/s-02.py, day13/s-03.py, day13/Fish.csv
작성일: 2026-11-09
tags: [학습, python]
---

# Python day13 — 다항 회귀 제곱항 추가와 PolynomialFeatures

> 실습 파일: `day13/s-02.py`, `day13/s-03.py`, `day13/Fish.csv`
> 허브: [[Python 정리본 인덱스]] · 이전: [[Python day12 사이킷런 선형 회귀 연습문제 풀이]] · 다음: [[Python day13 StandardScaler 표준화와 릿지·라쏘 규제]]

day12의 마지막 주석이 남긴 숙제 — "직선은 비례만 안다, 다항 회귀로 특성을 추가하라" — 를 실제로 푸는 날이다. 재료는 그대로 Fish 데이터이고 모델도 그대로 `LinearRegression`인데, **특성 쪽에 제곱항을 더해** 직선 대신 곡선을 맞춘다. 전반부(`s-02.py`)는 `np.column_stack`으로 제곱항을 **손으로** 붙여 보고, 후반부(`s-03.py`)는 같은 일을 `PolynomialFeatures`가 **자동으로** 해 주는 것을 확인한다. 특성 하나에 제곱항 하나를 더했을 때 R²가 0.820 → 0.825로 찔끔 오르고, 특성 셋을 2차로 펼쳤을 때 0.972까지 뛰고, 차수를 10으로 올리자 0.073으로 무너지는 세 숫자가 이 노트의 뼈대다. "항을 더하면 좋아진다"와 "너무 더하면 망가진다"를 같은 자료에서 연달아 본다.

## 1. 배운 내용

### 1-1. 출발점 — day12 단순 선형 회귀를 다시 세우기

```python
import pandas as pd
df = pd.read_csv('./day13/Fish.csv')
X = df[['Length2']]        # 특성 — 2차원
Y = df['Weight']           # 타깃 — 1차원

from sklearn.model_selection import train_test_split
X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size=0.2, random_state=42)

from sklearn.linear_model import LinearRegression
model = LinearRegression()
model.fit(X_train, Y_train)

Y_pred = model.predict(X_test)
from sklearn.metrics import r2_score
print('r2 : ', r2_score(Y_test, Y_pred))   # 0.8199897860284712
```

day12의 여덟 단계가 그대로 앞에 깔린다. `random_state=42`를 같게 두었기 때문에 학습/테스트 분할도 같고, 결정계수도 day12와 소수점까지 같은 0.8200이 나온다. 이 숫자가 이번 날의 **비교 기준선**이다 — 이후의 모든 변화는 "0.82에서 얼마나 움직였나"로 읽는다. 바뀐 것은 `feature`·`target` 변수를 거치지 않고 `df[['Length2']]`처럼 바로 꺼낸 것뿐인데, 이중 대괄호가 특성을 2차원으로 만든다는 규칙은 그대로다.

### 1-2. 제곱항을 손으로 붙이기 — `np.column_stack`

```python
import numpy as np
X_train_poly = np.column_stack((X_train**2, X_train))
print(X_train_poly)   # [16.2] → [262.44  16.2]   (제곱항, 원본)
```

핵심 한 줄이다. `X_train**2`는 넘파이·판다스의 요소별 연산이라 길이 열 하나가 통째로 제곱되고(16.2 → 262.44), `np.column_stack`이 두 열을 **옆으로** 붙여 `(127, 1)` 두 개를 `(127, 2)` 하나로 만든다. day07에서 본 `hstack`의 1차원 친화 버전으로, 1차원 배열 두 개를 주면 각각을 열로 세워 붙인다. 괄호가 두 겹인 것은 붙일 배열들을 **튜플 하나로** 묶어 넘기기 때문이다.

| 입력 | 모양 | 뜻 |
| --- | --- | --- |
| `X_train` | `(127, 1)` | 길이 x |
| `X_train**2` | `(127, 1)` | 길이의 제곱 x² |
| `column_stack((X_train**2, X_train))` | `(127, 2)` | [x², x] — 특성이 **둘**이 됨 |

모델 입장에서는 "길이"와 "길이의 제곱"이라는 **서로 다른 특성 두 개**가 들어온 것이다. 선형 회귀는 여전히 각 특성에 기울기 하나씩을 곱해 더하므로, 수식은 `y = w₁·x² + w₂·x + b`가 된다. x에 대해서는 2차 곡선이지만 특성 [x², x]에 대해서는 여전히 선형 — 그래서 모델 이름이 그대로 **선형** 회귀다. 수업 주석의 표현대로 "직선 공식(1차 방정식) `Y = WX + B`"에서 "곡선 공식(2차 방정식) `Y = W·X² + W·X + B`"로 바뀐 것이다.

### 1-3. 제곱된 특성으로 다시 학습하고 예측하기

```python
model = LinearRegression()
model.fit(X_train_poly, Y_train)
print(model.predict([[30**2, 30]]))   # [405.27748848]
```

모델 코드는 한 글자도 안 바뀌었다. 바뀐 것은 `fit`에 넘기는 특성이 `(127, 2)`가 되었다는 것뿐이다. 예측할 때도 **학습 때와 같은 모양**으로 넣어야 하므로 길이 30은 `[[30**2, 30]]` = `[[900, 30]]`으로 제곱항을 먼저, 원본을 뒤에 둔다. 열 순서를 `column_stack`에 넣은 순서와 맞추는 것이 중요하다 — 자리가 바뀌면 900을 길이로, 30을 제곱으로 읽어 엉뚱한 값이 나온다.

| 모델 | 길이 30 예측 | 기울기 | 절편 |
| --- | --- | --- | --- |
| 단순 선형 (day12) | 435.7 g | `[30.43]` | −477.3 |
| 제곱항 추가 | 405.3 g | `[0.25, 14.43]` (x², x 순) | −253.9 |

기울기가 둘로 늘고(`coef_`가 배열인 이유가 여기서 실감 난다), 절편이 −477에서 −254로 올라왔다. 직선이 작은 물고기 구간에서 음수로 깊이 내려가던 문제가 곡선에서는 완화된 것이다 — 아직 길이 10 cm에서 −84 g, 15 cm에서 +19 g이라 완전히 해결되진 않았지만 방향은 맞다.

### 1-4. 곡선 그리기 — 회귀선도 같은 변환을 거쳐야 한다

```python
point = np.arange(0, 101)                        # x 후보 0~100
point_poly = np.column_stack((point**2, point))  # 특성과 똑같이 제곱항 추가
import matplotlib.pyplot as plt
plt.scatter(X_train, Y_train)                     # 학습 점 127개
plt.plot(point, model.predict(point_poly), color="red")   # 곡선
plt.show()
```

day12에서는 직선이라 양 끝 두 점만 이으면 됐지만, 곡선은 **점을 촘촘히** 찍어야 한다. 그래서 `np.arange(0, 101)`로 0~100을 1 간격으로 만들고, 이 101개 x를 **학습 때와 똑같이** `column_stack((point**2, point))`로 변환해 `predict`에 넣는다. x축에는 원본 `point`, y축에는 예측값을 두고 `plot`으로 이으면 위로 휘어 올라가는 2차 곡선이 점들을 따라간다. "특성에 한 변환은 예측 입력에도 그대로"라는 원칙이 그림 코드에도 적용되는 셈이다.

### 1-5. 테스트 자료에도 같은 변환 — 결정계수 0.825

```python
X_test_poly = np.column_stack((X_test**2, X_test))   # 테스트용도 제곱항 추가
Y_pred = model.predict(X_test_poly)
print(r2_score(Y_test, Y_pred))   # 0.8249869834428712
```

| 모델 | 수식 | 테스트 R² |
| --- | --- | --- |
| day12 단순 선형 회귀 | `Y = W·X + B` (직선) | 0.8200 |
| day13 다항 선형 회귀 | `Y = W·X² + W·X + B` (곡선) | 0.8250 |

0.005 올랐다. 그림에서는 곡선이 직선보다 분명히 점들을 더 잘 따라가는데 숫자는 왜 이것뿐인가 — 길이 **하나만으로는** 무게의 흩어짐을 다 설명할 수 없기 때문이다. 같은 길이라도 종(Bream은 납작하고 Pike는 길쭉하다)에 따라 무게가 크게 다르고, 그 차이는 x²를 더한다고 줄지 않는다. 곡선으로 바꿔 "모양"은 맞췄지만 "정보"가 부족한 상태라, 다음 단계는 특성을 **더 넣는** 것이다.

### 1-6. 제곱항을 자동으로 — `PolynomialFeatures`

```python
from sklearn.preprocessing import PolynomialFeatures
poly = PolynomialFeatures()          # 객체 생성
poly.fit([[2]])                      # 특성(2)에서 규칙 찾기
print(poly.transform([[2]]))         # [[1. 2. 4.]]  → 절편용 1, 원래 값, 제곱값
```

1-2에서 손으로 하던 `column_stack((x**2, x))`를 사이킷런이 대신 해 주는 **변환기**다. 사용법이 모델과 닮아서 `fit`으로 규칙을 익히고 `transform`으로 적용하는데, 여기서 `fit`이 배우는 것은 "특성이 몇 개인가"뿐이다. 특성 하나짜리 `[[2]]`를 넣으면 `[1, 2, 4]` 세 칸이 나온다.

| 칸 | 값 | 뜻 |
| --- | --- | --- |
| 1 | `1.` | 절편(bias)용 상수항 — 모든 행에 1 |
| 2 | `2.` | 원래 값 x |
| 3 | `4.` | 제곱 x² |

```python
poly = PolynomialFeatures(include_bias=False)
poly.fit([[2]])
print(poly.transform([[2]]))         # [[2. 4.]]
```

`LinearRegression`은 절편을 스스로 학습하므로 상수항 1은 필요 없다. `include_bias=False`로 끄면 `[x, x²]`만 남아 1-2의 손 변환과 같은 내용이 된다(열 순서만 원본이 앞, 제곱이 뒤). 사이킷런 모델과 함께 쓸 때는 이 옵션을 끄는 것이 보통이다.

### 1-7. 특성이 둘·셋이면 — 제곱뿐 아니라 곱셈항까지

```python
poly = PolynomialFeatures(include_bias=False)
poly.fit([[2, 3]])
print(poly.transform([[2, 3]]))        # [[2. 3. 4. 6. 9.]]

poly.fit([[2, 3, 4]])
print(poly.transform([[2, 3, 4]]))     # [[2. 3. 4. 4. 6. 8. 9. 12. 16.]]  → 9개
```

특성이 둘이면 `[a, b, a², ab, b²]` 다섯 개가 된다. 손으로 할 때는 제곱만 생각했는데, `PolynomialFeatures`는 **서로 다른 특성끼리의 곱**(`ab`)도 항으로 넣는다. 셋이면 원본 3 + 제곱 3 + 곱 3 = 9개다.

| 특성 수 | 원본 | 제곱 | 서로 곱 | 합계 (2차, bias 제외) |
| --- | --- | --- | --- | --- |
| 1 | x | x² | — | 2 |
| 2 | a, b | a², b² | ab | 5 |
| 3 | a, b, c | a², b², c² | ab, ac, bc | 9 |

곱셈항은 "길이가 길면서 동시에 높이도 높은" 식의 **상호작용**을 모델이 배우게 해 준다. 물고기 부피가 길이 × 높이 × 너비에 가깝다는 걸 생각하면 이 항들이 왜 효과적인지 짐작이 간다. 수업 주석의 결론 그대로, "수동으로 특성의 제곱항을 만들지 않고 자동(`PolynomialFeatures`)으로 다항 추가"하는 쪽이 특성이 늘수록 압도적으로 편하다.

### 1-8. 특성 셋으로 다항 회귀 — R² 0.972

```python
df = pd.read_csv('./day13/Fish.csv')
X = df[['Length2', 'Height', 'Width']]     # 특성 3개
Y = df['Weight']
X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size=0.2, random_state=42)

poly = PolynomialFeatures(include_bias=False)
poly.fit(X_train)                           # 학습용 특성으로 규칙 찾기
X_train_poly = poly.transform(X_train)
X_test_poly = poly.transform(X_test)        # 테스트용은 transform만
print(X_train.shape)        # (127, 3)
print(X_train_poly.shape)   # (127, 9)   → 항이 추가됨

model = LinearRegression()
model.fit(X_train_poly, Y_train)
Y_pred = model.predict(X_test_poly)
print('r2 : ', r2_score(Y_test, Y_pred))   # 0.9719372415762594
```

`feature` 리스트에 `Height`·`Width`를 더하고 `PolynomialFeatures`를 거치자 특성이 3 → 9개가 되었고, 결정계수는 **0.82 → 0.97**로 뛰었다. 1-5에서 0.005밖에 안 오르던 것과 비교하면 "곡선으로 바꾸기"보다 "정보를 더 넣기"가 훨씬 컸다는 뜻이다. 길이·높이·너비와 그 곱셈항들이 사실상 부피를 표현하므로 무게를 거의 설명해 낸다.

`fit`은 **학습용에만** 하고 테스트용은 `transform`만 한다는 순서가 여기서 처음 코드로 등장한다. 다항 변환은 통계량을 배우는 것이 아니라 항 조합 규칙만 익히므로 둘 중 어느 쪽에 `fit`해도 결과는 같지만, 다음 노트의 `StandardScaler`부터는 이 순서가 결과를 바꾼다 — 그래서 처음부터 습관을 들여 두는 것이다.

### 1-9. 차수를 올리면 — `degree=10`과 과대적합

```python
poly = PolynomialFeatures(include_bias=False, degree=10)
poly.fit(X_train)
X_train_poly2 = poly.transform(X_train)
print(X_train_poly2.shape)   # (127, 285)   ← 차수 2 → 10에 따라 9 → 285
X_test_poly2 = poly.transform(X_test)

model = LinearRegression()
model.fit(X_train_poly2, Y_train)
Y_pred = model.predict(X_test_poly2)
print('r2 : ', r2_score(Y_test, Y_pred))   # 0.07276663213888512
```

`degree`는 "몇 제곱까지 항을 만들 것인가"다(생략 시 2). 10으로 올리자 특성이 **285개**가 되었고, 테스트 결정계수는 **0.07**로 무너졌다. 학습용 점수는 0.955로 여전히 높다 — 즉 127마리는 거의 외웠는데 처음 보는 32마리는 전혀 못 맞히는 상태다. 수업 주석이 적은 대로 "특성이 너무 많아지면 훈련 데이터에 과하게 집착하여 **과대적합**이 발생해 점수가 낮아진다."

| degree | 특성 수 | 학습 R² | 테스트 R² | 상태 |
| --- | --- | --- | --- | --- |
| 1 (단순 선형, 길이만) | 1 | 0.85 | 0.82 | 과소적합 기미 |
| 2 (특성 3개) | 9 | 0.98 | 0.97 | 적절 |
| 10 (특성 3개) | 285 | 0.96 | 0.07 | 과대적합 |

표본 127개에 특성 285개면 자료보다 조절 손잡이가 많은 셈이라, 어떤 잡음이든 다 맞출 수 있는 대신 새 자료 앞에서는 제멋대로 움직인다. 수업 주석의 두 번째 교훈 — "모델 구현에서 다양한 속성값(`degree=N`)을 테스트하여 설계·구현한다" — 은 하이퍼파라미터는 정답이 없으니 **학습 점수와 테스트 점수를 나란히 보며** 고르라는 뜻이다. 이 과대적합을 특성은 그대로 두고 누르는 방법이 다음 노트의 **규제**다.

### 1-10. 정리 — 과소적합과 과대적합 사이

```text
특성이 적다 (모델 단순, 과소적합)   → 항 추가: PolynomialFeatures / degree ↑
특성이 많다 (모델 복잡, 과대적합)   → 규제:    Ridge(L2) / Lasso(L1) / alpha ↑
```

수업 끝 주석의 두 줄이 이 날의 요약이다. 직선 하나가 모자라면 항을 더해 표현력을 키우고, 항이 넘쳐 외우기 시작하면 규제로 눌러 준다. 둘 다 **모델 클래스는 `LinearRegression` 계열 그대로**이고 특성 쪽을 손보거나 손실 함수에 벌점을 더하는 방식이라, day12의 여덟 단계 뼈대에서 ②(특성 준비)와 ④(모델 생성)만 바뀐다.

## 2. 추가로 알면 좋은 활용법

### 2-1. 만들어진 항의 이름 확인 — `get_feature_names_out`

```python
poly = PolynomialFeatures(include_bias=False).fit(X_train)
print(poly.get_feature_names_out())
# ['Length2' 'Height' 'Width' 'Length2^2' 'Length2 Height' 'Length2 Width'
#  'Height^2' 'Height Width' 'Width^2']
```

`transform` 결과는 열 이름 없는 넘파이 배열이라 9개 열이 각각 무엇인지 모른다. `get_feature_names_out()`이 원본 열 이름으로 항 이름을 만들어 주므로 `coef_`와 나란히 놓으면 어느 항이 얼마나 기여하는지 읽을 수 있다. 데이터프레임으로 다시 감싸 두면 뒤 단계도 편하다.

```python
X_train_poly_df = pd.DataFrame(X_train_poly, columns=poly.get_feature_names_out(), index=X_train.index)
```

### 2-2. 제곱항만 원할 때 — `interaction_only`와 열 고르기

```python
PolynomialFeatures(degree=2, include_bias=False, interaction_only=True)   # a, b, ab  (제곱 없음)
```

`interaction_only=True`는 제곱항을 빼고 **서로 다른 특성의 곱만** 남긴다. 반대로 제곱만 필요하고 곱은 빼고 싶다면 `PolynomialFeatures` 대신 1-2처럼 `np.column_stack`이나 `X.assign(Length2_sq=X['Length2']**2)`로 직접 만드는 쪽이 간단하다. 자동 변환은 편하지만 항 수가 특성 수의 제곱에 비례해 늘어나므로, 필요한 항이 분명하면 손으로 고르는 것도 전략이다.

### 2-3. 변환과 모델을 한 덩어리로 — `make_pipeline`

```python
from sklearn.pipeline import make_pipeline
poly_model = make_pipeline(PolynomialFeatures(degree=2, include_bias=False), LinearRegression())
poly_model.fit(X_train, Y_train)            # 안에서 transform → fit
print(poly_model.score(X_test, Y_test))     # 0.972 — 안에서 transform → predict → R²
poly_model.predict([[30, 10, 4]])           # 원본 특성 3개만 넣으면 된다
```

1-8에서 `transform`을 학습용·테스트용·예측 입력에 세 번 따로 호출했는데, 파이프라인으로 묶으면 **원본 특성만 넘겨도** 안에서 변환이 자동으로 따라붙는다. `fit`은 학습용에만, 이후는 `transform`만이라는 순서도 파이프라인이 지켜 준다. day12 3-1에서 예고했던 바로 그 코드다.

### 2-4. 차수 고르기를 반복문으로

```python
for d in range(1, 6):
    pm = make_pipeline(PolynomialFeatures(degree=d, include_bias=False), LinearRegression())
    pm.fit(X_train, Y_train)
    print(d, round(pm.score(X_train, Y_train), 3), round(pm.score(X_test, Y_test), 3))
```

1-9의 표를 자동으로 만드는 코드다. 학습 점수는 차수가 오를수록 단조롭게 오르고 테스트 점수는 어느 지점에서 꺾이는데, 그 꺾이는 직전이 고를 차수다. 다음 노트의 `alpha` 고르기와 완전히 같은 모양의 반복문이라 한 번 익히면 둘 다 쓴다.

### 2-5. 다항 특성과 한글 열 이름

`get_feature_names_out()`은 열 이름을 그대로 이어 붙이므로 한글 열도 `'키 몸무게'`처럼 잘 나온다. 다만 공백으로 곱을 표시하기 때문에 열 이름 자체에 공백이 있으면 읽기 어렵다 — 다항 변환 전에 `rename`으로 공백을 밑줄로 바꿔 두면 깔끔하다.

### 2-6. 곡선 그릴 x 범위는 자료 범위로

1-4에서 `np.arange(0, 101)`로 0~100을 그렸지만 실제 길이는 8.4~63.4 cm다. 자료 밖 구간(0~8, 63~100)의 곡선은 **외삽**이라 믿을 근거가 없고, 2차 곡선은 바깥에서 급격히 치솟거나 음수로 떨어져 그림이 과장된다. `np.linspace(X['Length2'].min(), X['Length2'].max(), 100)`처럼 자료 범위로 좁히면 모델이 실제로 책임지는 구간만 보인다. day12 연습문제의 "100달러 외삽 주의"와 같은 이야기다.

## 3. 더 나아가 알면 좋은 것

### 3-1. 편향-분산 트레이드오프

1-9의 표가 보여 준 현상의 교과서 이름이다. 모델이 단순하면 자료의 모양을 못 따라가 **편향**이 크고(과소적합), 복잡하면 학습 자료의 잡음까지 따라가 새 자료마다 결과가 요동쳐 **분산**이 크다(과대적합). 테스트 오차는 둘의 합이라 U자 모양이 되고, 바닥이 적정 복잡도다. `degree`·`alpha`·트리 깊이·k-NN의 k 등 모든 하이퍼파라미터가 이 U자 위를 움직이는 손잡이다.

### 3-2. 한 번의 분할로 고르지 않기 — 검증 세트와 교차 검증

`degree`를 테스트 점수 보고 고르면 테스트 세트가 "선택"에 쓰여 더 이상 공정한 최종 평가가 아니다. 그래서 학습/**검증**/테스트 세 조각으로 나누거나, `cross_val_score`·`GridSearchCV(param_grid={'polynomialfeatures__degree': [1, 2, 3]})`로 학습 자료 안에서만 차수를 고른 뒤 테스트는 마지막에 한 번만 본다. 파이프라인 단계 이름에 이중 밑줄을 붙여 파라미터를 지정하는 문법도 이때 쓴다.

### 3-3. 스플라인·트리 — 곡선을 맞추는 다른 길

다항식은 전 구간에 하나의 식을 쓰기 때문에 한쪽을 맞추면 다른 쪽이 흔들린다(차수 10의 폭주가 그 극단). `SplineTransformer`는 구간마다 낮은 차수 곡선을 이어 붙여 국소적으로 맞추고, `DecisionTreeRegressor`·`RandomForestRegressor`·그래디언트 부스팅은 수식 없이 계단형으로 곡선을 근사한다. 물고기처럼 "길이³에 비례"라는 물리적 근거가 있을 땐 차수 2~3 다항식이 가장 해석하기 좋지만, 근거 없는 곡선은 트리 계열이 안전한 편이다.

### 3-4. 로그 변환 — 곱셈 관계를 덧셈으로

무게 ≈ c × 길이 × 높이 × 너비라면 양변에 로그를 씌워 `log(무게) = log c + log 길이 + log 높이 + log 너비`로 만들 수 있다. 그러면 다항 항 없이 **단순 선형 회귀**로 곱셈 관계를 맞추고, 예측값은 `np.exp`로 되돌린다. 특성 수가 늘지 않아 과대적합 위험이 적고 음수 예측도 사라진다. 어떤 변환이 맞는지는 자료의 생성 원리를 생각해 보는 것이 출발점이다.

### 3-5. 다음에 볼 키워드

- `np.column_stack` · 요소별 `**2` · `[[x², x]]` 입력 순서 · 선형 회귀가 곡선을 맞추는 이유(특성에 대해 선형)
- `PolynomialFeatures(degree, include_bias, interaction_only)` · `fit`/`transform` · `get_feature_names_out` · 곱셈(상호작용)항
- 특성 수 공식 `(n+d)!/(n!·d!) − 1` · `degree=10` → 285 · 과대적합 vs 과소적합 · 학습 R² vs 테스트 R² 나란히 보기
- `make_pipeline` · `GridSearchCV`의 `단계__파라미터` 문법 · 검증 세트 · 편향-분산 트레이드오프
- `np.arange` vs `np.linspace`로 곡선 x 만들기 · 외삽 · `SplineTransformer` · 로그 변환

## 실습 파일

- `KDT_2026/2026_Python/day13/s-02.py` — 단순 선형 회귀 재구성(`df[['Length2']]`·`train_test_split(…, 0.2, 42)`·`LinearRegression().fit`·`r2_score` 0.8200) → `np.column_stack((X_train**2, X_train))`으로 제곱항 수동 추가([16.2] → [262.44, 16.2]) → 같은 `LinearRegression` 재학습·`predict([[30**2, 30]])` 405.3 → `np.arange(0, 101)`을 `column_stack`으로 같은 변환 후 `scatter` + 빨간 `plot` 곡선 → 테스트 특성에도 제곱항 추가해 `r2_score` 0.8250, 끝 주석 day12 직선(1차) vs day13 곡선(2차) 결정계수 비교
- `KDT_2026/2026_Python/day13/s-03.py` (1]~3]) — `PolynomialFeatures()` `fit([[2]])`·`transform` → `[1, 2, 4]`(절편·원본·제곱), `include_bias=False` → `[2, 4]`, 특성 2개 `[2, 3]` → 5항(제곱/곱셈), 특성 3개 → 9항, `df[['Length2', 'Height', 'Width']]` 3특성 다항 회귀 — 학습용 `fit`·`transform`/테스트용 `transform`, `(127, 3)` → `(127, 9)`, `r2_score` 0.9719, `degree=10` → `(127, 285)`·`r2_score` 0.0728과 과대적합 주석, 끝 주석 "특성이 적으면 항 추가 / 많으면 규제"
- `KDT_2026/2026_Python/day13/Fish.csv` — day12와 같은 물고기 159마리 × 7열

## 관련 노트

[[Python 정리본 인덱스]] · [[Python day12 사이킷런 선형 회귀 연습문제 풀이]] · [[Python day13 StandardScaler 표준화와 릿지·라쏘 규제]] · [[Python day12 사이킷런 단순 선형 회귀로 물고기 무게 예측]] · [[Python day07 넘파이 배열 병합·정렬과 조건 필터링]] · [[Python day06 넘파이 인덱싱·슬라이싱과 배열 연산]] · [[Python day09 맷플롯립 시작과 선 차트]] · [[KDT_2026 학습 지도]]
