---
출처: Claude 분석
원본: KDT_2026/2026_Python/ML_pracitce/practice1.py
작성일: 2026-11-04
tags: [학습, ai, python]
---

# AI day12 — 사이킷런 선형 회귀 연습문제 풀이

> 실습 파일: `ML_pracitce/practice1.py`
> 허브: [[AI 정리본 인덱스]] · 이전: [[AI day12 사이킷런 단순 선형 회귀로 물고기 무게 예측]] · 다음: [[AI day13 다항 회귀 제곱항 추가와 PolynomialFeatures]]

day12 수업에서 물고기 길이로 무게를 맞히던 뼈대를 **다른 자료에 그대로 옮겨 보는** 연습이다. 재료는 시본에 내장된 `tips` 데이터셋 — 식당 손님 244팀의 식사 총액(`total_bill`)·팁(`tip`)·성별·흡연 여부·요일·시간대·인원이 들어 있고, 이번에는 **식사 총액 하나로 팁을 맞히는** 단순 선형 회귀다. 문제는 다섯 단계(자료 준비 → 분할 → 학습·파라미터 확인 → 평가·새 손님 예측 → 시각화·한계 분석)로 짜여 있고, 수업 `s-01.py`의 1)~12) 번호와 거의 1:1로 대응한다. 풀고 나면 `read_csv` 자리에 `sns.load_dataset`이 들어간 것 말고는 **코드가 한 줄도 바뀌지 않는다**는 것, 그리고 같은 뼈대라도 자료가 달라지면 R²가 0.82에서 0.54로 뚝 떨어진다는 것이 눈에 들어온다 — 팁은 식사 총액만으로는 절반밖에 설명되지 않는다.

## 1. 배운 내용

### 1-1. 문제 1 — 시본 내장 데이터셋으로 자료 준비

```python
import seaborn as sns
df = sns.load_dataset('tips')
df.info()
```

```text
RangeIndex: 244 entries, 0 to 243
 #   Column      Non-Null Count  Dtype
 0   total_bill  244 non-null    float64
 1   tip         244 non-null    float64
 2   sex         244 non-null    category
 3   smoker      244 non-null    category
 4   day         244 non-null    category
 5   time        244 non-null    category
 6   size        244 non-null    int64
```

day09에서 그래프 연습용으로 쓰던 `sns.load_dataset('tips')`를 이번엔 **모델 재료**로 쓴다. CSV 파일을 두지 않아도 되는 것이 편하지만, 처음 한 번은 인터넷에서 받아 오므로 오프라인이면 실패한다. `info()`로 보면 결측이 없고 숫자 열이 `total_bill`·`tip`·`size` 셋뿐이다 — 나머지 넷은 `category`라 선형 회귀에 바로 넣을 수 없고, 문제도 숫자 열 둘만 쓰라고 한다.

```python
feature = ['total_bill']   # 독립변수 X — 리스트라서 2차원
target = 'tip'             # 종속변수 Y — 문자열이라서 1차원
X = df[feature]
Y = df[target]
```

문제 지문이 "문제지"와 "정답지"라는 비유를 쓴다. 특성 = 문제지(X), 타깃 = 정답지(Y). **X는 2차원·Y는 1차원** 규칙은 수업과 같고, `feature`를 리스트로 두는 이유도 같다 — 나중에 `['total_bill', 'size']`처럼 이름을 더 적기만 하면 다중 회귀가 된다.

| 수업 (`s-01.py`) | 연습 (`practice1.py`) |
| --- | --- |
| `pd.read_csv('./day12/Fish.csv')` | `sns.load_dataset('tips')` |
| `feature = ['Length2']` | `feature = ['total_bill']` |
| `target = 'Weight'` | `target = 'tip'` |
| 159마리 | 244팀 |

### 1-2. 문제 2 — 80:20 분할과 `random_state=42`

```python
from sklearn.model_selection import train_test_split
X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size=0.2, random_state=42)
print(X_train.shape, X_test.shape)   # (195, 1) (49, 1)
```

244팀의 20%인 48.8을 올림해 테스트 49팀, 나머지 195팀이 학습용이다. 지문의 "재현성을 위해 `random_state=42`로 고정"이 핵심 표현이다 — 씨앗을 고정해야 **다시 실행해도 같은 행이 같은 쪽**으로 가고, 그래야 기울기·R² 같은 숫자를 남과 비교할 수 있다. 숫자 42 자체에는 의미가 없고 관례일 뿐이다.

### 1-3. 문제 3 — 학습과 기울기·절편 확인

```python
from sklearn.linear_model import LinearRegression
model = LinearRegression()
model.fit(X_train, Y_train)
print("기울기:", model.coef_)        # [0.10696371]
print("y절편:", model.intercept_)   # 0.925235558557056
```

지문이 "수학적 파라미터"라고 부르는 것이 `coef_`(기울기)·`intercept_`(절편)이다. 읽으면 **`팁 ≈ 0.107 × 식사 총액 + 0.93`** — 식사비 1달러가 오를 때 팁이 약 10.7센트 오르고, 기본 팁이 약 93센트쯤 깔려 있다는 뜻이다. 물고기 예제에서 절편이 −477로 현실에 없는 값이었던 것과 달리 여기선 절편이 양수라 "식사비 0일 때 팁 0.93달러"라는 해석이 어색하긴 해도 범위 안에서는 그럴듯하다. `coef_`가 대괄호에 싸인 배열인 이유는 특성이 여러 개일 때 기울기도 여러 개라서다.

### 1-4. 문제 4 — R²·RMSE 산출과 새 손님 예측

```python
import numpy as np
from sklearn.metrics import mean_squared_error, r2_score

Y_pred = model.predict(X_test)                        # 테스트 49팀의 예측 팁
r2 = r2_score(Y_test, Y_pred)                         # 0.5449...
rmse = np.sqrt(mean_squared_error(Y_test, Y_pred))    # 0.7542...
print(f"R²: {r2:.2f}")       # R²: 0.54
print(f"RMSE: {rmse:.2f}")   # RMSE: 0.75
```

수업 12)의 평가 코드를 그대로 가져온 자리다. 지문의 "소수점 둘째 자리까지"는 day01의 f-문자열 형식 지정 `{값:.2f}`로 푼다 — `round(r2, 2)`로 반올림해도 되지만 `.2f`는 `0.5`를 `0.50`으로 자릿수까지 맞춰 준다.

| 지표 | 값 | 읽는 법 |
| --- | --- | --- |
| R² | 0.54 | 팁의 흩어짐 중 **54%**를 식사 총액이 설명 — 물고기(0.82)보다 훨씬 낮다 |
| RMSE | 0.75 | 예측 팁이 실제와 **평균 75센트** 어긋남 — 타깃과 같은 달러 단위 |

R²가 0.54라는 것은 식사비가 팁의 절반은 설명하지만 나머지 절반은 다른 요인(인원·요일·손님 성향)이라는 뜻이다. 식사비 ↔ 팁은 분명 비례하지만 "같은 식사비에 팁을 후하게 주는 사람과 박하게 주는 사람"의 차이가 커서, 점들이 직선에서 멀리 흩어진다. RMSE 0.75달러는 평균 팁(약 3달러)의 4분의 1이라 작지 않은 오차다.

```python
print(model.predict([[30], [100]]))   # [ 4.13  11.62 ]
```

지문의 "식사 총액이 $30, $100인 새 손님"은 표본 두 개를 한 번에 넘기는 `[[30], [100]]`이다. 30달러 식사엔 약 4.13달러, 100달러 식사엔 약 11.62달러 팁이 나온다. 손으로 확인하면 `0.107 × 30 + 0.925 ≈ 4.13`으로 `coef_`·`intercept_`와 맞는다. 다만 자료의 식사 총액 최댓값이 50.81달러라 **100달러는 자료 범위 밖**이다 — 직선을 바깥으로 쭉 늘인 외삽이라 숫자는 나오지만 믿을 근거가 약하다.

### 1-5. 문제 5 — 세 요소를 한 도화지에

수업 10)의 시각화 패턴을 테스트 세트에 그대로 옮긴 것이 문제 5의 답이다.

```python
plt.rc('font', family='Malgun Gothic')                      # 한글 라벨 — day09 설정
plt.rcParams['axes.unicode_minus'] = False

plt.scatter(X_test, Y_test, label="실제 데이터")                            # ① 테스트 세트 실제 점 49개
plt.plot([5, 100], model.predict([[5], [100]]), label="회귀선")             # ② 식사비 5~100달러 회귀선 — 양 끝 두 점
plt.scatter([50], model.predict([[50]]), color="red", label="$50 예측")     # ③ 식사비 50달러 예측점 (붉은 점)
plt.title("식사 총액 vs 팁")
plt.xlabel("식사 총액($)")
plt.ylabel("팁($)")
plt.legend()
plt.show()
```

세 요소에 각각 `label=`을 달고 `legend()`로 범례를 띄우면 어느 점이 실제값이고 어느 점이 예측인지 그림만 보고도 구분된다. 한글 제목·축 이름을 쓰므로 그리기 전에 day09의 폰트 설정 두 줄이 먼저 와야 네모 글자가 안 생긴다. `plot([5, 100], predict([[5], [100]]))`은 day12 수업의 "직선은 양 끝 두 점이면 그려진다" 요령 그대로다.

수업과 다른 점은 산점도에 **학습 세트가 아니라 테스트 세트**를 올리라는 것이다. 테스트 점 위에 직선을 그리면 "모델이 처음 보는 자료에서 얼마나 빗나가나"가 그림으로 보이고, R² 0.54가 왜 나왔는지 — 점들이 직선 주위에 넓게 퍼져 있는 것 — 가 눈에 들어온다. 50달러 예측점은 약 6.27달러이고 직선 위에 정확히 올라간다.

**한계점 분석** 지문은 1-4의 해석을 글로 정리하면 된다. ① 식사 총액 하나만으로는 팁의 절반밖에 설명되지 않는다(R² 0.54). ② 식사비가 커질수록 팁의 편차도 커지는 부채꼴 모양이라 오차가 고르지 않다. ③ 100달러처럼 자료 범위 밖 예측은 외삽이라 신뢰하기 어렵다. 해결 방향은 수업 11)과 같다 — 특성을 더 넣거나(`size`·요일·시간대), 직선 대신 곡선을 쓰거나.

### 1-6. 수업 코드와 연습 코드 — 번호 대응표

| 수업 `s-01.py` | 연습 문제 | 같은 코드 |
| --- | --- | --- |
| 1) 자료 불러오기 | 문제 1 | `info()` |
| 2)~3) 특성·타깃 추출 | 문제 1 | `df[feature]`·`df[target]` |
| 4) 데이터 분리 | 문제 2 | `train_test_split(…, 0.2, 42)` |
| 5)~6) 모델 생성·학습 | 문제 3 | `LinearRegression().fit` |
| 7)~8) 기울기·절편 | 문제 3 | `coef_`·`intercept_` |
| 9) 예측 | 문제 4 | `predict([[30], [100]])` |
| 12) 평가 | 문제 4 | `r2_score`·`mean_squared_error` → `sqrt` |
| 10) 시각화 | 문제 5 | `scatter` + `plot` + 붉은 점 |
| 11) 문제점 | 문제 5 | 한계점 분석 |

순서만 조금 다르다 — 수업은 시각화를 먼저 하고 평가를 맨 뒤에 붙였고, 연습은 평가를 먼저 하고 시각화로 마무리한다. 실무에선 연습 쪽 순서(숫자로 먼저 평가 → 그림으로 확인)가 더 자연스럽다.

## 2. 추가로 알면 좋은 활용법

### 2-1. `score`로 학습·테스트 점수 나란히 보기

```python
print(f"학습 R²: {model.score(X_train, Y_train):.2f}")   # 0.43
print(f"테스트 R²: {model.score(X_test, Y_test):.2f}")   # 0.54
```

`r2_score(Y_test, Y_pred)`와 `model.score(X_test, Y_test)`는 같은 값이다 — 후자는 `predict`까지 안에서 해 준다. 둘을 나란히 보면 이 자료는 테스트 점수가 학습 점수보다 **높게** 나오는데, 과적합의 반대 모양이다. 테스트로 뽑힌 49팀이 우연히 직선에 잘 맞는 손님들이었다는 뜻이고, 한 번의 분할이 얼마나 운에 좌우되는지 보여 주는 예다. 그래서 3-2의 교차 검증이 필요하다.

### 2-2. 예측 입력을 데이터프레임으로 — 경고 없애기

```python
import pandas as pd
new = pd.DataFrame({'total_bill': [30, 100]})
model.predict(new)
```

`predict([[30], [100]])`도 동작하지만 "X does not have valid feature names"라는 경고가 뜬다. 학습 때 `total_bill`이라는 **열 이름이 있는 데이터프레임**으로 `fit`했기 때문이다. 같은 열 이름의 데이터프레임으로 넘기면 경고가 사라지고, 특성이 여러 개가 되면 어느 값이 어느 열인지도 분명해진다.

### 2-3. 특성 하나 더 — 인원수 `size`

```python
feature = ['total_bill', 'size']
X = df[feature]
# 나머지 코드는 그대로 → coef_가 [a, b] 두 개
```

`tips`에 남은 숫자 열 `size`(인원)를 넣으면 다중 선형 회귀가 된다. `feature` 리스트에 이름을 하나 적는 것 외엔 바뀌는 코드가 없다. 다만 인원이 많으면 식사비도 커지므로 두 특성이 서로 겹치는 정보를 담고 있어(day09 히트맵의 강한 상관), R²가 크게 오르진 않는다.

### 2-4. 범주 열 넣기 — `get_dummies`

```python
X = pd.get_dummies(df[['total_bill', 'size', 'day', 'time']], drop_first=True)
```

`day`·`time` 같은 `category` 열은 그대로 넣을 수 없다. `get_dummies`가 `day_Sat`·`day_Sun`·`time_Lunch` 같은 0/1 열로 펼쳐 주고, `drop_first=True`는 기준 범주 하나를 빼서 열끼리 완전히 겹치는 것을 막는다. "주말 저녁 손님이 팁을 더 주나" 같은 질문은 이렇게 범주를 넣어야 모델이 답한다.

### 2-5. 팁 비율로 바꿔 보기 — 타깃 가공

```python
df['tip_pct'] = df['tip'] / df['total_bill'] * 100
```

팁의 절대 금액 대신 **식사비 대비 비율**을 타깃으로 두면 질문이 "얼마를 주나"에서 "몇 %를 주나"로 바뀐다. 비율은 식사비에 덜 끌려가므로 요일·시간대·인원 같은 다른 요인의 영향이 더 잘 드러난다. day08의 열 연산으로 타깃을 새로 만드는 것 자체가 **특성 공학**의 첫걸음이다.

### 2-6. 잔차 그림 — 오차가 고른지 보기

```python
resid = Y_test - Y_pred
plt.scatter(X_test, resid)
plt.axhline(0, color="gray")
plt.show()
```

실제값에서 예측값을 뺀 **잔차**를 x축에 대고 찍으면, 직선이 잘 맞는 자료는 0 주위에 고르게 흩어진다. `tips`는 식사비가 클수록 잔차가 위아래로 벌어지는 부채꼴이 보이는데, 이것이 문제 5의 "한계점"을 숫자가 아닌 그림으로 말하는 방법이다.

## 3. 더 나아가 알면 좋은 것

### 3-1. 분산이 커지는 자료 — 이분산성과 로그 변환

식사비가 커질수록 팁의 흩어짐도 커지는 현상을 **이분산성**이라 한다. 선형 회귀는 오차가 고르다고 가정하므로 이런 자료에선 큰 식사비 쪽 오차를 과소평가한다. 흔한 처방이 타깃에 `np.log`를 씌워 큰 값을 눌러 주는 **로그 변환**이고, 예측값은 `np.exp`로 되돌린다. 2-5의 비율 타깃도 같은 효과를 노린 것이다.

### 3-2. 한 번의 분할을 믿지 않기 — 교차 검증

2-1에서 테스트 점수가 학습 점수보다 높게 나온 것처럼 분할 하나는 운이다. `cross_val_score(model, X, Y, cv=5, scoring='r2')`로 다섯 번 나눠 평균을 보면 이 자료의 R²가 대략 0.4~0.5 사이라는 더 솔직한 답이 나온다. `random_state`를 바꿔 가며 몇 번 돌려 보는 것만으로도 감을 잡을 수 있다.

### 3-3. 직선이 전부가 아니다 — 트리·앙상블

`LinearRegression` 자리에 `DecisionTreeRegressor`·`RandomForestRegressor`를 넣어도 `fit`·`predict`·`score`는 똑같이 돈다. 트리 계열은 직선 가정이 없고 범주 특성과 상호작용(주말 × 저녁)을 스스로 찾아내므로, `tips`처럼 여러 요인이 얽힌 자료에선 선형 모델보다 점수가 오르는 경우가 많다. 대신 `coef_` 같은 "식"이 없어 해석은 어려워진다 — 해석력과 예측력의 맞교환이다.

### 3-4. 통계 쪽 시선 — `statsmodels`

```python
import statsmodels.formula.api as smf
result = smf.ols('tip ~ total_bill', data=df).fit()
print(result.summary())
```

사이킷런은 예측에 초점을 맞춰 기울기·절편만 돌려주지만, `statsmodels`는 같은 회귀를 돌려 **p-값·신뢰구간·R² 조정값**까지 표로 보여 준다. "식사비가 팁에 영향을 주는가"를 통계적으로 답하려면 이쪽이다. `'tip ~ total_bill + size + C(day)'` 같은 수식 문법으로 특성을 적는다.

### 3-5. 다음에 볼 키워드

- `sns.load_dataset` 내장 데이터셋 · `category` dtype · 문제지/정답지 비유 · `random_state` 재현성
- f-문자열 `{값:.2f}` 자릿수 맞추기 vs `round` · `coef_`/`intercept_` 해석(1달러당 10.7센트)
- `r2_score`·`mean_squared_error` → `np.sqrt` RMSE · `model.score` 동일값 · 테스트 > 학습 점수의 의미
- 외삽(자료 범위 밖 예측) · 테스트 세트 산점도 + 회귀선 + 붉은 예측점 · 잔차 그림·`axhline`
- 열 이름 데이터프레임 입력으로 경고 없애기 · `size` 다중 회귀 · `get_dummies(drop_first=True)` · 팁 비율 타깃·특성 공학
- 이분산성·로그 변환 · `cross_val_score` · `DecisionTreeRegressor`/`RandomForestRegressor` · `statsmodels` `ols`·p-값

## 실습 파일

- `KDT_2026/2026_Python/ML_pracitce/practice1.py` — 사이킷런 선형 회귀 연습문제: 문제 1 `sns.load_dataset('tips')` → `info()`·`feature = ['total_bill']`(2차원)·`target = 'tip'`(1차원), 문제 2 `train_test_split(…, test_size=0.2, random_state=42)` 네 변수 언패킹, 문제 3 `LinearRegression()` → `fit` → `"기울기:"` `coef_`·`"y절편:"` `intercept_` 출력, 문제 4 `predict(X_test)` → `r2_score`·`np.sqrt(mean_squared_error)` RMSE 산출(소수 둘째 자리)과 $30·$100 신규 손님 팁 예측, 문제 5 `plt.rc` 한글 폰트 설정 → 테스트 세트 산점도(`label="실제 데이터"`) + 식사비 5~100달러 회귀선(`label="회귀선"`) + 식사비 50달러 붉은 예측점(`label="$50 예측"`) → `title`·`xlabel`·`ylabel`·`legend`·`show`, 한계점 분석(지문)

## 관련 노트

[[AI 정리본 인덱스]] · [[AI day12 사이킷런 단순 선형 회귀로 물고기 무게 예측]] · [[AI day13 다항 회귀 제곱항 추가와 PolynomialFeatures]] · [[KDT_2026 학습 지도]]
