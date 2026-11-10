---
출처: Claude 분석
원본: KDT_2026/2026_Python/ML_pracitce/practice2.py, ML_pracitce/student_dataset_10000_rows.csv
작성일: 2026-11-09
tags: [학습, ai, python]
---

# AI day13 — 다항 규제 회귀 연습문제 풀이

> 실습 파일: `ML_pracitce/practice2.py`, `ML_pracitce/student_dataset_10000_rows.csv`
> 허브: [[AI 정리본 인덱스]] · 이전: [[AI day13 StandardScaler 표준화와 릿지·라쏘 규제]] · 다음: [[AI day14 사이킷런 Pipeline으로 다항·표준화·회귀 묶기]]

day13 수업의 흐름 — 다항 특성 확장 → 표준화 → 선형·릿지·라쏘 세 모델 비교 — 를 **다른 자료에 통째로 옮겨 보는** 연습이다. 재료는 캐글의 학생 성적 데이터(1만 명 × 공부 시간·출석률·수면 시간·인터넷 사용·과제 완료 수·이전 점수·시험 점수·취업 여부)이고, 수치형 6개로 시험 점수(`exam_score`)를 맞힌다. 수업과 달리 차수는 `degree=2`, 규제 강도는 `alpha=1.0`으로 **고정**되어 있어 "고르기"는 없고 "같은 조건에서 세 모델이 어떻게 다른가"에 집중한다. 마지막에 상위권·하위권 학생 한 명씩을 지어내어 세 모델에 넣어 보는데, 선형·릿지는 거의 같은 답을 내고 라쏘만 10점 넘게 다른 답을 낸다 — 라쏘가 특성 27개 중 17개를 지워 버린 결과다.

## 1. 배운 내용

### 1-1. 문제 1 — 수치형 6열로 특성·타깃 구성

```python
import pandas as pd
df = pd.read_csv('./ML_pracitce/student_dataset_10000_rows.csv')
df.info()

feature = ['study_hours', 'attendance', 'sleep_hours', 'internet_usage', 'assignments_completed', 'previous_score']
target = 'exam_score'
X = df[feature]
Y = df[target]
```

```text
RangeIndex: 10000 entries, 0 to 9999
 0   study_hours            10000 non-null  int64
 1   attendance             10000 non-null  int64
 2   sleep_hours            10000 non-null  int64
 3   internet_usage         10000 non-null  int64
 4   assignments_completed  10000 non-null  int64
 5   previous_score         10000 non-null  int64
 6   exam_score             10000 non-null  float64
 7   placement_status       10000 non-null  object
```

8열 중 `placement_status`(Placed / Not Placed)만 문자열이고 지문대로 "범주형 변수를 제외한 6개 수치형 컬럼"을 특성으로 쓴다. 1만 행에 결측이 없어 전처리 없이 바로 간다. day12·13의 Fish가 159행이었던 것과 비교하면 자료가 60배 커졌는데, 코드는 한 줄도 달라지지 않는다 — 특성 이름을 리스트에 적고 `df[feature]`로 꺼내는 규칙이 특성이 6개가 되어도 그대로다.

| 열 | 뜻 | 범위 |
| --- | --- | --- |
| `study_hours` | 하루 공부 시간 | 1~11 |
| `attendance` | 출석률(%) | 40~100 |
| `sleep_hours` | 수면 시간 | 4~9 |
| `internet_usage` | 인터넷 사용 시간 | 1~11 |
| `assignments_completed` | 완료한 과제 수 | 0~20 |
| `previous_score` | 이전 시험 점수 | 35~95 |
| `exam_score` | **타깃** — 이번 시험 점수 | 26.7~100 |

### 1-2. 문제 2 — 8:2 분할

```python
from sklearn.model_selection import train_test_split
X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size=0.2, random_state=42)
# (8000, 6) (2000, 6)
```

세 번째 보는 줄이라 설명이 필요 없다. 학습 8,000명·테스트 2,000명이고 `random_state=42`로 재현성을 고정한다.

### 1-3. 문제 3 — 다항 확장 뒤 표준화, 둘 다 학습용에만 `fit`

```python
from sklearn.preprocessing import PolynomialFeatures, StandardScaler

poly = PolynomialFeatures(degree=2, include_bias=False)
poly.fit(X_train)                       # 학습 세트로만 fit
X_train_poly = poly.transform(X_train)
X_test_poly = poly.transform(X_test)
print(X_train.shape)        # (8000, 6)
print(X_train_poly.shape)   # (8000, 27)

ss = StandardScaler()
ss.fit(X_train_poly)                    # 다항 확장된 학습 세트 기준
X_train_scaled = ss.transform(X_train_poly)
X_test_scaled = ss.transform(X_test_poly)
```

수업 `s-03.py`의 3)~4)를 그대로 옮겼다. 지문이 두 번이나 못 박는 것이 "**훈련 세트로만 `fit`**을 수행하고, `X_train`과 `X_test`를 각각 `transform`"이다 — 앞 노트 1-3의 데이터 누수 규칙이 연습문제 조건으로 명시된 셈이다. 특성 6개가 2차로 펼쳐지면 원본 6 + 제곱 6 + 서로 곱 15 = **27개**가 된다.

| 종류 | 개수 | 예 |
| --- | --- | --- |
| 원본 | 6 | `study_hours` |
| 제곱 | 6 | `study_hours^2` |
| 서로 곱 | 15 (= 6×5/2) | `study_hours attendance` |
| 합계 | 27 | |

표준화는 **다항 확장된 뒤**에 한다는 순서도 중요하다. 원본 6열을 먼저 표준화하고 제곱하면 제곱항의 크기가 다시 흩어지므로, 항을 다 만든 뒤 27열을 한꺼번에 표준화해야 모든 열이 같은 눈금에 놓인다. 지문의 "다항 확장된 훈련 세트(`X_train_poly`) 기준으로 `fit`"이 그 뜻이다.

### 1-4. 문제 4 — 세 모델 학습과 R² 비교

```python
from sklearn.linear_model import LinearRegression, Ridge, Lasso

lr = LinearRegression()
ridge = Ridge(alpha=1.0, random_state=42)
lasso = Lasso(alpha=1.0, random_state=42)

lr.fit(X_train_scaled, Y_train)
ridge.fit(X_train_scaled, Y_train)
lasso.fit(X_train_scaled, Y_train)

print("LinearRegression  Train R2:", lr.score(X_train_scaled, Y_train), " Test R2:", lr.score(X_test_scaled, Y_test))
print("Ridge             Train R2:", ridge.score(X_train_scaled, Y_train), " Test R2:", ridge.score(X_test_scaled, Y_test))
print("Lasso             Train R2:", lasso.score(X_train_scaled, Y_train), " Test R2:", lasso.score(X_test_scaled, Y_test))
```

세 모델을 **같은 표준화 자료**로 학습시키고 `score`로 학습·테스트 R²를 나란히 찍는다. 변수 이름을 `lr`·`ridge`·`lasso`로 따로 두어 세 객체가 동시에 살아 있게 한 점이 수업(매번 `model`에 덮어쓰기)과 다르다 — 문제 5에서 세 모델에 같은 입력을 넣어 비교해야 하기 때문이다.

| 모델 | 학습 R² | 테스트 R² | 격차 |
| --- | --- | --- | --- |
| `LinearRegression` | 0.732 | 0.737 | −0.004 |
| `Ridge(alpha=1.0)` | 0.732 | 0.737 | −0.004 |
| `Lasso(alpha=1.0)` | 0.630 | 0.632 | −0.002 |

읽을 점이 셋이다. **첫째**, 선형과 릿지가 소수 셋째 자리까지 같다 — 표본 8,000개에 특성 27개면 과대적합이 거의 없어 `alpha=1.0`의 벌점이 할 일이 없다. 앞 노트 3-2에서 적은 대로 자료가 많으면 규제의 영향이 줄어드는 것을 숫자로 본다. **둘째**, 라쏘만 0.63으로 10점 낮다 — 같은 `alpha=1.0`이어도 L1 벌점은 기울기를 0으로 **잘라 내므로** 자료가 충분한 상황에선 쓸 만한 특성까지 지워 성능을 깎는다. **셋째**, 세 모델 모두 테스트 점수가 학습 점수보다 살짝 높아 격차가 음수다 — 과대적합과는 반대 방향이고, 이 분할에서 테스트 2,000명이 우연히 조금 더 맞히기 쉬운 쪽이었다는 뜻이다.

```python
import numpy as np
print(np.sum(lasso.coef_ == 0))      # 17  ← 27개 중 17개가 0
```

지문에는 없지만 앞 노트 1-6의 한 줄을 붙여 보면 라쏘가 **27개 특성 중 17개를 지웠다**. 남은 10개는 `study_hours`·`assignments_completed`·`attendance previous_score` 같은 항들이고, 가장 큰 기울기는 `study_hours`(7.4)다 — 표준화했으므로 "공부 시간이 1표준편차(약 3시간) 늘면 시험 점수가 7.4점 오른다"로 읽는다.

### 1-5. 문제 5 — 가상의 상위권·하위권 학생 예측

```python
sample = pd.DataFrame([
    [9, 95, 7, 2, 18, 85],     # 샘플 1 (상위권)
    [2, 60, 5, 9,  4, 50]      # 샘플 2 (하위권)
], columns=feature)

sample_poly = poly.transform(sample)        # 학습 때 fit한 변환기 그대로
sample_scaled = ss.transform(sample_poly)

print("LinearRegression :", lr.predict(sample_scaled))     # [101.2   48.5]
print("Ridge            :", ridge.predict(sample_scaled))  # [101.4   48.6]
print("Lasso            :", lasso.predict(sample_scaled))  # [111.9   66.1]
```

지문의 핵심 문장은 "**앞서 학습시킨 동일한 변환기**(`PolynomialFeatures`, `StandardScaler`)로 변환하세요"다. 새 학생 두 명을 `poly.transform` → `ss.transform` 순서로 통과시켜야 학습 자료와 같은 27열·같은 눈금이 되고, 그제야 세 모델에 넣을 수 있다. 새 자료에 `fit`을 다시 하면 두 명의 평균으로 표준화되어 엉뚱한 값이 나온다.

입력을 리스트가 아닌 **`pd.DataFrame(…, columns=feature)`**로 만든 것도 눈여겨볼 부분이다. 변환기가 학습 때 열 이름 있는 데이터프레임을 받았으므로 예측 때도 같은 열 이름으로 넘기면 경고가 없고, 여섯 숫자의 순서를 틀릴 위험도 줄어든다(day12 연습문제 2-2의 패턴).

| 학생 | 선형 | 릿지 | 라쏘 |
| --- | --- | --- | --- |
| 샘플 1 (공부 9h·출석 95%·과제 18·이전 85) | 101.2 | 101.4 | 111.9 |
| 샘플 2 (공부 2h·출석 60%·과제 4·이전 50) | 48.5 | 48.6 | 66.1 |

선형과 릿지는 두 학생 모두 0.2점 이내로 같고, 라쏘는 상위권을 10점, 하위권을 18점 더 높게 찍는다. 특성을 17개나 지운 라쏘는 남은 몇 개 특성에 기대어 "대충 평균 쪽으로" 예측하는 경향이 있어 하위권을 덜 낮게 본 것이다. 100점이 넘는 예측값(101.2·111.9)이 나오는 것은 선형 모델이 **타깃의 상한을 모르기** 때문이다 — 이 자료는 1만 명 중 3,520명이 만점 100점이라 상위권 구간이 천장에 붙어 있고, 직선·곡선은 그 천장을 뚫고 올라간다. 실무라면 `np.clip(pred, 0, 100)`으로 잘라 주거나 3-3의 다른 모델을 고려한다.

### 1-6. 수업 코드와 연습 코드 대응표

| 수업 `s-03.py` | 연습 `practice2.py` | 달라진 점 |
| --- | --- | --- |
| Fish 159행 · 특성 3개 | 학생 10,000행 · 특성 6개 | 자료 60배, 항 9 → 27 |
| `PolynomialFeatures(include_bias=False)` | `+ degree=2` 명시 | 기본값을 글로 적음 |
| `degree=10`으로 과대적합 확인 | 없음 (차수 고정) | |
| `StandardScaler` | 같음 | |
| `alpha_list` 반복문으로 릿지 고르기 | `Ridge(alpha=1.0, random_state=42)` 고정 | 고르기 생략 |
| `Lasso(alpha=10)` | `Lasso(alpha=1.0, random_state=42)` | |
| `model` 변수 덮어쓰기 | `lr`·`ridge`·`lasso` 따로 | 세 모델 동시 비교 |
| `np.sum(coef_ == 0)` | 없음 | |
| — | 샘플 2명 `DataFrame` → `transform` → 3모델 `predict` | 새 입력 변환 연습 |

`Ridge`·`Lasso`에 `random_state`를 준 것은 지문 조건이다. 릿지의 기본 풀이법은 공식 계산이라 난수가 끼지 않지만, 라쏘는 좌표 하강이라는 반복 알고리즘이고 특정 옵션에서 특성 순서를 무작위로 섞으므로 재현성을 위해 적어 둔다 — 결과에는 영향이 거의 없다.

## 2. 추가로 알면 좋은 활용법

### 2-1. 다항 없이 그냥 선형이면? — 기준선 만들기

```python
lin = LinearRegression().fit(X_train, Y_train)
print(lin.score(X_train, Y_train), lin.score(X_test, Y_test))   # 0.662  0.663
```

원본 6열로 바로 선형 회귀를 돌리면 R² 0.66이다. 다항 2차 + 표준화 뒤의 0.74와 비교하면 **상호작용·제곱항이 8점 정도를 더 설명**한 셈이다. 어떤 전처리를 하든 "아무것도 안 한 기준선"을 먼저 찍어 두면 그 전처리가 실제로 도움이 됐는지 판단할 수 있다.

### 2-2. 상관계수로 특성 감 잡기

```python
print(df[feature + [target]].corr()[target].round(2))
# study_hours 0.56 · assignments_completed 0.39 · previous_score 0.32
# attendance 0.22 · sleep_hours 0.15 · internet_usage −0.15
```

모델을 돌리기 전에 day09의 `corr()`로 타깃과의 상관을 보면 공부 시간이 가장 세고 인터넷 사용만 음(−)이라는 그림이 먼저 잡힌다. 라쏘가 살려 둔 특성 중 기울기가 가장 큰 것이 `study_hours`였던 것과 맞아떨어진다. 회귀 결과를 해석할 때 상관표가 든든한 참고가 된다.

### 2-3. 세 모델을 반복문·딕셔너리로

```python
models = {'Linear': LinearRegression(), 'Ridge': Ridge(alpha=1.0), 'Lasso': Lasso(alpha=1.0)}
for name, m in models.items():
    m.fit(X_train_scaled, Y_train)
    print(f"{name:8s} Train {m.score(X_train_scaled, Y_train):.3f}  Test {m.score(X_test_scaled, Y_test):.3f}")
```

`lr`·`ridge`·`lasso` 세 변수를 딕셔너리에 담으면 `fit`·`score`·`predict`를 한 반복문으로 돌릴 수 있다(day02 딕셔너리 `items()`). 모델을 넷·다섯으로 늘려도 줄이 안 늘어나고, 출력 서식도 f-문자열 `:8s`·`:.3f`로 맞춰 표처럼 읽힌다.

### 2-4. 파이프라인 셋

```python
from sklearn.pipeline import make_pipeline
pipes = {name: make_pipeline(PolynomialFeatures(degree=2, include_bias=False), StandardScaler(), m)
         for name, m in models.items()}
for name, p in pipes.items():
    p.fit(X_train, Y_train)
    print(name, p.predict(sample))     # 원본 6열 그대로 — 변환은 안에서
```

문제 3·5의 `transform` 여섯 줄이 사라진다. 앞 노트 2-1의 파이프라인을 세 모델에 딕셔너리 컴프리헨션으로 한 번에 씌운 것이고, `sample`을 원본 그대로 넣어도 된다.

### 2-5. 예측값을 0~100으로 자르기

```python
pred = np.clip(lr.predict(sample_scaled), 0, 100)    # [100.  48.5]
```

1-5의 101.2·111.9 같은 값은 시험 점수로 존재할 수 없다. day08에서 `Quantity`를 1~10으로 자르던 `clip`을 예측값에 쓰면 상한·하한이 맞춰진다. 모델의 한계를 후처리로 가리는 것이지 모델이 좋아지는 건 아니므로, 보고할 때는 "모델은 101을 예측했고 상한으로 잘랐다"를 적어 두는 편이 정직하다.

### 2-6. `alpha` 고정이 아니라 고르기였다면

```python
from sklearn.linear_model import LassoCV
lasso_cv = LassoCV(cv=5, random_state=42).fit(X_train_scaled, Y_train)
print(lasso_cv.alpha_, lasso_cv.score(X_test_scaled, Y_test))
```

지문이 `alpha=1.0`으로 고정한 것은 비교 조건을 맞추기 위해서다. 실제로 라쏘를 쓰려면 `LassoCV`로 `alpha`를 고르는데, 이 자료에선 훨씬 작은 `alpha`가 뽑혀 선형 회귀와 비슷한 0.73대로 돌아온다 — 1-4의 0.63은 라쏘가 나빠서가 아니라 **규제가 너무 셌던** 결과임을 확인하는 방법이다.

## 3. 더 나아가 알면 좋은 것

### 3-1. 천장에 붙은 타깃 — 중도절단

시험 점수가 100에서 잘린 자료는 "진짜 실력은 110인데 100으로 기록된" 학생들이 섞여 있다. 통계에서는 이를 **중도절단(censoring)**이라 하고, 보통 선형 회귀는 이 때문에 상위권 기울기를 과소평가한다. 토빗(Tobit) 회귀처럼 절단을 모델에 넣는 방법, 또는 `exam_score >= 100` 여부를 분류 문제로 따로 떼는 방법이 있다. 1-5에서 100 넘는 예측이 나오는 근본 원인이 여기 있다.

### 3-2. 범주 열도 쓰기 — 취업 여부와 원-핫

빼 두었던 `placement_status`는 타깃과 강하게 얽혀 있을 가능성이 크다(성적이 좋으면 취업도 잘 된다). day08의 `get_dummies`로 0/1 열로 바꿔 특성에 넣으면 R²가 오를 수 있지만, "취업 여부로 시험 점수를 예측"하는 것은 **인과가 거꾸로**라 시험 전에 알 수 있는 정보가 아니다. 예측 시점에 쓸 수 있는 특성만 넣는다는 원칙(미래 정보 누수)이 여기서도 등장한다.

### 3-3. 선형이 아닌 모델과 비교

같은 뼈대에 `RandomForestRegressor`·`GradientBoostingRegressor`·`HistGradientBoostingRegressor`를 넣어 보면 다항 항을 손으로 만들지 않아도 상호작용을 스스로 찾고, 천장(100)도 계단형으로 어느 정도 따라간다. 표준화도 필요 없다. 대신 `coef_` 같은 해석 가능한 식이 사라지므로, "공부 시간 1시간이 몇 점인가"를 설명해야 한다면 여전히 규제 선형 모델이 답이다.

### 3-4. 합성 데이터의 티

6개 특성이 모두 고르게 분포하고(`describe()`의 사분위가 등간격) 결측도 없는 것은 실제 설문이 아니라 **만들어 낸 자료**의 특징이다. 합성 데이터는 연습에 좋지만 실제 자료에서 흔한 치우침·결측·이상치·중복이 없어, 여기서 얻은 R² 0.74가 실제 학교 데이터에서 재현된다고 기대하면 안 된다. 캐글 데이터셋 설명 페이지에서 생성 방식을 확인하는 습관이 필요하다.

### 3-5. 다음에 볼 키워드

- 특성 6개 → 2차 27항 공식(원본 n + 제곱 n + 곱 n(n−1)/2) · 다항 확장 **뒤에** 표준화 · 훈련 세트로만 `fit`
- 자료가 많으면 규제 효과 ↓ · 같은 `alpha`에서 L1이 L2보다 세게 작용 · `np.sum(coef_ == 0)` · 라쏘 과소적합
- 새 입력 `pd.DataFrame(columns=feature)` → 동일 변환기 `transform` · `random_state` in `Lasso`(좌표 하강)
- 타깃 상한 100과 `np.clip` · 중도절단·토빗 · 미래 정보 누수(취업 여부) · 기준선 모델
- 모델 딕셔너리 반복 · 파이프라인 컴프리헨션 · `LassoCV` · 트리·부스팅 회귀 · 합성 데이터 판별

## 실습 파일

- `KDT_2026/2026_Python/ML_pracitce/practice2.py` — 다항 규제 회귀 연습문제: 문제 1 캐글 학생 성적 CSV `read_csv` → `info()`, 수치형 6열 `feature` 리스트·`target = 'exam_score'`, 문제 2 `train_test_split(…, test_size=0.2, random_state=42)`, 문제 3 `PolynomialFeatures(degree=2, include_bias=False)` 학습 세트 `fit` → `transform` 둘(6 → 27), `StandardScaler` 다항 학습 세트 `fit` → `transform` 둘, 문제 4 `LinearRegression()`·`Ridge(alpha=1.0, random_state=42)`·`Lasso(alpha=1.0, random_state=42)` 각각 `fit` → `score` 학습·테스트 R² 비교 출력, 문제 5 상위권·하위권 샘플 2행 `pd.DataFrame(columns=feature)` → `poly.transform` → `ss.transform` → 세 모델 `predict` 비교 출력
- `KDT_2026/2026_Python/ML_pracitce/student_dataset_10000_rows.csv` — 학생 10,000명 × 8열(`study_hours`·`attendance`·`sleep_hours`·`internet_usage`·`assignments_completed`·`previous_score`·`exam_score`·`placement_status`), 결측 없음, 시험 점수 만점 3,520명

## 관련 노트

[[AI 정리본 인덱스]] · [[AI day13 StandardScaler 표준화와 릿지·라쏘 규제]] · [[AI day14 사이킷런 Pipeline으로 다항·표준화·회귀 묶기]] · [[AI day13 다항 회귀 제곱항 추가와 PolynomialFeatures]] · [[AI day12 사이킷런 선형 회귀 연습문제 풀이]] · [[KDT_2026 학습 지도]]
