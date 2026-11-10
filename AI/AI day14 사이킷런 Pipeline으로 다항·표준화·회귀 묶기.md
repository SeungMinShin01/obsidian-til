---
출처: Claude 분석
원본: KDT_2026/2026_Python/day14/s-04.py, day14/Fish.csv, 수업 PPT
작성일: 2026-11-10
tags: [학습, ai, python]
---

# AI day14 — 사이킷런 Pipeline으로 다항·표준화·회귀 묶기

> 실습 파일: `day14/s-04.py`, `day14/Fish.csv`
> 허브: [[AI 정리본 인덱스]] · 이전: [[AI day13 다항 규제 회귀 연습문제 풀이]] · 다음: [[AI day14 KFold 교차 검증과 GridSearchCV 하이퍼파라미터 탐색]]

day12~13에서 조각조각 배운 것을 **한 파일에 처음부터 끝까지** 다시 쓰는 날이다. 자료 수집 → 특성·타깃 선정 → 학습/테스트 분리 → 다항 항 추가 → 표준화 → 모델 학습 → 결정계수, 이렇게 일곱 단계를 번호를 붙여 차례로 적고 나서, 그중 **4~6단계(변환기 둘 + 모델 하나)를 `Pipeline` 하나로 묶는다**. 앞에서 `fit` → `transform`을 여섯 번 부르던 코드가 `pipe_model.fit(X_train, Y_train)` 한 줄이 되고, `score`도 변환 전 원본 특성을 그대로 넣으면 된다. day13 2-1에서 `make_pipeline`으로 미리 맛본 것을 이번엔 **단계마다 이름을 붙이는 `Pipeline` 클래스**로 정식으로 다룬다. 이름이 있으면 나중에 `poly__degree`처럼 단계 안의 파라미터를 바깥에서 집어 바꿀 수 있어서, 이 이름 규칙이 그리드 서치로 이어지는 문이 된다.

## 1. 배운 내용

### 1-1. 일곱 단계를 번호 붙여 다시 쓰기

```python
import pandas as pd
df = pd.read_csv("./day14/Fish.csv")                          # 1) 자료 수집
X = df[['Length2', 'Height', 'Width']]                         # 2) 특성 선정/구성 (2차원)
Y = df['Weight']                                               # 2) 타깃(정답) 선정/구성 (1차원)

from sklearn.model_selection import train_test_split
X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size=0.2)   # 3) 훈련/테스트 분리

from sklearn.preprocessing import PolynomialFeatures
poly = PolynomialFeatures(degree=2, include_bias=False)        # 4) 과소적합 방지 — 항 추가 (제곱·곱셈)
poly.fit(X_train)
X_train_poly = poly.transform(X_train)
X_test_poly  = poly.transform(X_test)

from sklearn.preprocessing import StandardScaler
ss = StandardScaler()                                          # 5) 항이 많아지면 단위 표준화
ss.fit(X_train_poly)
X_train_scaled = ss.transform(X_train_poly)
X_test_scaled  = ss.transform(X_test_poly)

from sklearn.linear_model import LinearRegression
model = LinearRegression()                                     # 6) 모델 선택 (규제 쓰려면 Ridge/Lasso + alpha)
model.fit(X_train_scaled, Y_train)

print('r2 : ', model.score(X_train_scaled, Y_train))           # 7) 결정계수
print('r2 : ', model.score(X_test_scaled, Y_test))
```

새 문법은 없다. 수업 주석의 번호가 곧 이 노트의 차례다. 정리하면 이렇다.

| 번호 | 단계 | 도구 | 어느 노트에서 왔나 |
| --- | --- | --- | --- |
| 1) | 자료 수집 | `pd.read_csv` | day08 |
| 2) | 특성(2차원)·타깃(1차원) 선정 | `df[[…]]` / `df['…']` | day12 1-3 |
| 3) | 훈련/테스트 분리 | `train_test_split` | day12 1-4 |
| 4) | 항 추가 — 과소적합 방지 | `PolynomialFeatures(degree=2, include_bias=False)` | day13 다항 회귀 |
| 5) | 표준화 — 항이 많아지면 | `StandardScaler` | day13 표준화·규제 |
| 6) | 모델 선택 (규제면 `alpha`) | `LinearRegression` / `Ridge` / `Lasso` | day12·13 |
| 7) | 결정계수 | `model.score` | day12 1-12 |

주석에 적힌 두 문장이 4)·5)를 고르는 기준이다 — "과소적합 방지하고자 항 추가", "항 많아지면 항/특성 간에 단위 표준화". 4)와 5)는 둘 다 `fit`은 **학습용에만**, `transform`은 **학습용·테스트용 둘 다**라는 규칙이 그대로다. 그래서 변환기 하나당 세 줄, 둘이면 여섯 줄이 되고, 테스트용·새 입력에 같은 순서를 빠뜨리지 않고 반복해야 한다. 이 "같은 변환을 같은 순서로 두 번 이상"이 파이프라인이 해결하려는 문제다.

### 1-2. `random_state` 없는 분리 — 점수가 매번 달라지는 이유

3)의 `train_test_split`에 `random_state`를 주지 않았다. 실행할 때마다 127마리와 32마리가 다르게 갈리므로 7)의 결정계수도 매번 다르게 찍힌다.

| 실행 | 학습 R² | 테스트 R² |
| --- | --- | --- |
| 1회 | 0.982 | 0.981 |
| 2회 | 0.982 | 0.979 |
| 3회 | 0.985 | 0.954 |
| `random_state=42` | 0.983 | 0.972 |

학습 점수는 0.98 언저리로 안정적인데 테스트 점수는 0.95~0.98 사이를 오간다. 테스트가 32마리뿐이라 **어떤 물고기가 시험지에 들어가느냐**에 따라 점수가 흔들리는 것이다. day12에서 `random_state=42`를 고정했던 이유가 여기서 역으로 보인다 — 비교 실험을 할 땐 고정해서 분할 운을 빼고, 모델의 진짜 실력이 궁금할 땐 여러 번 갈라서 평균을 본다(2-5의 교차 검증). 한 번 찍힌 점수 하나로 "0.98짜리 모델"이라고 말하지 않는 편이 안전하다.

### 1-3. `Pipeline` — 4~6단계를 한 덩어리로

```python
from sklearn.pipeline import Pipeline
# pipe_model = Pipeline([("식별자", 클래스명())])   ← 파이썬 인스턴스 생성: 변수 = 클래스명(인자값)
pipe_model = Pipeline([
    ('poly',      PolynomialFeatures(degree=2, include_bias=False)),   # 4)
    ('scaler',    StandardScaler()),                                   # 5)
    ('regressor', LinearRegression()),                                 # 6)
])
```

`Pipeline`은 **(이름, 객체) 튜플의 리스트**를 받는다. 튜플 첫 칸이 그 단계의 식별자(문자열), 둘째 칸이 변환기나 모델의 **인스턴스**다. 수업 주석이 "파이썬 인스턴스 생성, 변수 = 클래스명(인자값)"을 굳이 다시 적어 둔 것은 둘째 칸에 들어가는 것이 `StandardScaler`라는 클래스 이름이 아니라 `StandardScaler()`로 **괄호를 붙여 만든 객체**라는 뜻이다. day05에서 `Student()`가 설계도에서 실체를 찍어 내는 인스턴스화였던 것과 같은 이야기다 — 파이프라인에는 설계도가 아니라 실체를 넣는다.

| 자리 | 쓰는 것 | 예 |
| --- | --- | --- |
| 식별자 | 소문자 문자열, 단계를 부르는 이름 | `'poly'` `'scaler'` `'regressor'` |
| 객체 | `fit`·`transform`이 있는 변환기 (마지막은 `fit`·`predict`가 있는 모델) | `PolynomialFeatures(…)` `StandardScaler()` `LinearRegression()` |
| 순서 | 리스트 순서 = 자료가 흐르는 순서 | 특성 3개 → 9개 → 표준화 → 회귀 |

규칙은 하나다 — **마지막 단계만 모델이고, 그 앞은 전부 변환기**여야 한다. 중간에 `fit`·`predict`만 있는 모델을 끼우면 다음 단계로 넘길 `transform` 결과가 없어 오류가 난다.

### 1-4. 파이프라인으로 학습하고 점수 내기

```python
pipe_model.fit(X_train, Y_train)                # 9) 원본 특성 3개를 그대로 넣는다
print('r2 :', pipe_model.score(X_train, Y_train))
print('r2 :', pipe_model.score(X_test,  Y_test))
```

`fit` 한 줄이 안에서 하는 일을 펼치면 1-1의 4)~6) 아홉 줄과 정확히 같다.

```text
pipe_model.fit(X_train, Y_train)
  ├─ poly.fit_transform(X_train)          → X_train_poly    (3열 → 9열)
  ├─ scaler.fit_transform(X_train_poly)   → X_train_scaled  (열마다 평균 0·편차 1)
  └─ regressor.fit(X_train_scaled, Y_train)

pipe_model.score(X_test, Y_test)   /   pipe_model.predict(새_입력)
  ├─ poly.transform(X_test)               ← fit 없이 transform만
  ├─ scaler.transform(X_test_poly)        ← fit 없이 transform만
  └─ regressor.score(X_test_scaled, Y_test)
```

핵심은 **`fit` 때는 변환기마다 `fit_transform`, `predict`·`score` 때는 `transform`만** 자동으로 골라 부른다는 점이다. day13 1-3에서 "테스트용에는 절대 `fit_transform`을 쓰지 않는다"고 손으로 지키던 규칙을 파이프라인이 구조적으로 강제한다 — 테스트 자료로 변환기를 다시 학습시키는 실수(데이터 누수)가 애초에 일어날 수 없다. 같은 분할로 손 코드와 파이프라인을 나란히 돌리면 학습 0.9833 / 테스트 0.9719로 **소수점 넷째 자리까지 같은 값**이 나온다. 하는 일이 같으니 당연하다.

여기서 주의할 것이 입력 자료다. 파이프라인에는 **변환하기 전 원본 특성**(`X_train`·`X_test`, 3열)을 넣는다. 이미 `transform`을 거친 배열을 넣으면 안에서 다항 확장과 표준화를 **한 번 더** 거쳐 9열이 54열이 되고, 모델이 학습한 모양과 달라 오류가 나거나 엉뚱한 점수가 나온다. 손으로 만든 `X_train_scaled` 같은 중간 변수는 파이프라인을 쓰는 순간 필요가 없어진다.

### 1-5. 손 코드 vs 파이프라인 — 무엇이 줄었나

| | 손 코드 (1-1) | 파이프라인 (1-3·1-4) |
| --- | --- | --- |
| 변환기 호출 | `fit` 2번 + `transform` 4번 | 없음 (안에서 자동) |
| 중간 변수 | `X_train_poly`·`X_test_poly`·`X_train_scaled`·`X_test_scaled` | 없음 |
| 새 물고기 예측 | `model.predict(ss.transform(poly.transform(새입력)))` | `pipe_model.predict(새입력)` |
| 테스트용 `fit` 실수 | 사람이 조심 | 구조적으로 불가능 |
| 저장 | 변환기 2개 + 모델 1개 따로 | 객체 하나 |
| 단계 바꾸기 | 코드 여러 줄 수정 | 튜플 한 줄 교체 |

줄어드는 것은 줄 수만이 아니다. "변환 규칙 + 모델"이 **객체 하나**가 되므로 저장·전달·비교 단위가 깔끔해진다. 6)의 주석대로 `LinearRegression()` 자리에 `Ridge(alpha=10)`을 넣으면 규제 모델 파이프라인이 되고, 나머지는 손댈 것이 없다 — 같은 분할에서 학습 0.963 / 테스트 0.970으로 day13 1-5의 결과가 그대로 재현된다.

### 1-6. 이름이 있어서 되는 일 — 단계 꺼내 보기

```python
pipe_model.named_steps['poly'].get_feature_names_out()
# ['Length2' 'Height' 'Width' 'Length2^2' 'Length2 Height' 'Length2 Width' 'Height^2' 'Height Width' 'Width^2']

pipe_model['scaler'].mean_.round(2)
# [ 28.39   8.83   4.43  918.75  276.57  140.63  93.75  44.16  22.27]   ← 9열의 학습용 평균

pipe_model.named_steps['regressor'].coef_.round(1), pipe_model.named_steps['regressor'].intercept_
# [-335.  -6.3  65.3  559.5  545.8  -563.2  -272.5  44.6  307.]  386.8
```

`Pipeline`을 쓰는 보람이 여기 있다. 1-3에서 붙인 식별자로 `named_steps['poly']`(또는 딕셔너리처럼 `pipe_model['poly']`)를 꺼내면 **학습이 끝난 그 단계의 객체**가 나오고, day13에서 보던 `get_feature_names_out`·`mean_`·`coef_`를 전부 그대로 쓸 수 있다. `make_pipeline`은 이름을 `polynomialfeatures`·`standardscaler`·`linearregression`처럼 클래스 이름 소문자로 자동으로 붙이는데, 직접 지은 짧은 이름이 꺼내 쓸 때 편하다. 절편이 day12의 −477에서 **386.8**(무게 평균 근처)로 바뀐 것도 눈에 띈다 — 표준화된 특성은 평균이 0이라 "모든 특성이 평균일 때의 예측값"이 절편이 되기 때문이다.

### 1-7. 이 날의 흐름 한 장

```text
1) read_csv ─▶ 2) X(3열)·Y ─▶ 3) train_test_split
                                      │
         ┌────────────────────────────┴────────────────────────────┐
     손 코드                                                  Pipeline([
     4) poly.fit / transform ×2                                   ('poly',      PolynomialFeatures(2)),
     5) ss.fit   / transform ×2                                   ('scaler',    StandardScaler()),
     6) model.fit(X_train_scaled)                                 ('regressor', LinearRegression()) ])
     7) model.score(X_test_scaled)                            9) pipe.fit(X_train) · pipe.score(X_test)
         └──────────────── 같은 분할이면 같은 R² ────────────────┘
```

### 1-8. 수업 슬라이드 — 파이프라인이란

파이프라인은 데이터 전처리·특성 공학·최종 모델 학습과 예측에 이르는 **일련의 머신러닝 워크플로우를 하나로 묶어 단일 추정기처럼 동작하게** 만드는 기법이다. 왜 필요한가 — 스케일링·인코딩·결측치 처리 같은 전처리를 손으로 따로 관리하면 코드가 파편화되어 유지보수가 어려워지고, 무엇보다 **테스트 데이터나 교차 검증용 폴드의 정보가 전처리 과정에 새어 들어가는 데이터 누수(Data Leakage)** 가 자주 생기기 때문이다.

| 종류 | 설명 |
| --- | --- |
| 표준 파이프라인 `Pipeline` / `make_pipeline` | 여러 변환기(Transformer)의 `fit_transform()`을 차례로 거친 뒤 마지막 예측기(Estimator)의 `fit()`을 **단일 인터페이스**로 실행. 학습(Train)과 평가(Test)에서 동일한 변환 기준을 누락 없이 재현하고, 교차 검증(`cross_val_score`)·하이퍼파라미터 튜닝(`GridSearchCV`) 때 데이터 누수를 원천 차단 |
| 복합 특성 파이프라인 (`ColumnTransformer` 연계) | 수치형과 범주형이 섞인 현실 데이터에서 수치형 열에는 결측치 대체·표준화(`StandardScaler`), 범주형 열에는 원-핫 인코딩을 **병렬로** 지정한 뒤 모델 파이프라인에 연결. 서로 다른 타입의 전처리 복잡도를 낮추고 전처리부터 예측까지 **객체 하나**로 통제 |

슬라이드 그림이 1-4의 흐름을 한 장으로 그린다. 왼쪽 **Step 1** — `Training set`이 `pipeline.fit(…)`으로 들어가면 `Scaling` → `Dimensionality Reduction` 단계는 `.fit(…) & .transform(…)`을, 마지막 `Learning Algorithm`은 `.fit(…)`만 거쳐 `Predictive Model`이 된다. 오른쪽 **Step 2** — `Test set`이 `pipeline.predict(…)`로 들어가면 같은 단계들을 `.transform(…)`만으로 통과해 모델의 `.predict(…)`가 `Class labels`를 내놓는다. 굵은 화살표(학습)와 흰 화살표(예측)가 서로 다른 메소드를 타는 것이 핵심이다.

### 1-9. 수업 슬라이드 — `pipe_poly_lr` 세 단계의 명칭과 역할

```python
pipe_poly_lr = Pipeline([
    ('poly',      PolynomialFeatures(degree=2, include_bias=False)),
    ('scaler',    StandardScaler()),
    ('regressor', LinearRegression())
])
pipe_poly_lr.fit(X_train, y_train)

train_r2 = pipe_poly_lr.score(X_train, y_train)
test_r2  = pipe_poly_lr.score(X_test,  y_test)
print("\n=== [2차 다항 선형 회귀 Pipeline 평가] ===")
print(f"훈련 데이터 설명력 (Train R2): {train_r2:.4f}")      # 0.9833
print(f"테스트 데이터 설명력 (Test R2) : {test_r2:.4f}")     # 0.9719
```

슬라이드가 이 코드를 "비선형 패턴을 학습하려고 입력을 2차 다항식으로 확장하고, 폭발적으로 늘어난 특성의 단위를 표준화한 뒤, 최종 선형 회귀 모델로 전달하는 전체 과정을 **단 하나의 추정기(Estimator)** 로 캡슐화한 구조"라고 요약한다. 세 단계의 명칭과 역할표가 1-3의 표를 보완한다.

| 단계 | 명칭 | 종류 | 역할 |
| --- | --- | --- | --- |
| 1 `PolynomialFeatures(degree=2, include_bias=False)` | 2차 다항 특성 생성기 | 변환기 (Transformer) | 선형 모델의 한계인 비선형 표현력을 극복하려고 기존 피처 간의 거듭제곱 및 상호작용 항(Cross-product)을 생성 |
| 2 `StandardScaler()` | 표준 정규분포 스케일러 | 변환기 (Transformer) | 각 특성의 평균을 0, 표준편차를 1로 맞추는 표준화(Z-score 정규화) |
| 3 `LinearRegression()` | 정규방정식 기반 다중 선형 회귀 | 예측기 (Estimator) | 표준화된 고차 다항 특성을 입력받아 최소제곱법(OLS)으로 손실(MSE)을 최소화하는 가중치 w와 편향 b를 학습 |

앞 둘은 `fit`·`transform`을 가진 **변환기**, 마지막은 `fit`·`predict`를 가진 **예측기** — 1-3에서 적은 "마지막 단계만 모델" 규칙이 이 분류다. 슬라이드 코드는 타깃 변수를 소문자 `y_train`·`y_test`로 쓰는데, 수업 코드(`Y_train`)와 이름만 다르다. 같은 분할(`random_state=42`)이면 1-4에서 손 코드와 비교한 0.9833 / 0.9719가 그대로 나온다. 이 파이프라인이 다음 노트에서 `KFold`·`GridSearchCV`의 재료가 된다.

## 2. 추가로 알면 좋은 활용법

### 2-1. `단계__파라미터` — 바깥에서 안쪽 설정 바꾸기

```python
pipe_model.set_params(poly__degree=3)              # 'poly' 단계의 degree를 3으로
pipe_model.fit(X_train, Y_train)                   # 학습 0.990 / 테스트 0.977

pipe_model.set_params(poly__degree=2, regressor=Ridge(alpha=10))   # 단계 자체를 바꿀 수도
```

식별자와 파라미터 이름을 **밑줄 두 개**로 이으면 파이프라인 바깥에서 안쪽 단계의 설정을 집을 수 있다. `pipe_model.get_params()`를 찍으면 `poly__degree`·`poly__include_bias`·`scaler__with_mean`·`regressor__fit_intercept`처럼 쓸 수 있는 이름이 전부 나온다. 1-3에서 이름을 직접 지은 이유가 이 문법 때문이다 — `make_pipeline`이었다면 `polynomialfeatures__degree`라고 길게 적어야 한다.

### 2-2. 그리드 서치 — 차수와 `alpha`를 한꺼번에 고르기

```python
from sklearn.model_selection import GridSearchCV
from sklearn.linear_model import Ridge

pipe = Pipeline([('poly', PolynomialFeatures(include_bias=False)),
                 ('scaler', StandardScaler()),
                 ('regressor', Ridge())])
grid = GridSearchCV(pipe,
                    {'poly__degree': [1, 2, 3], 'regressor__alpha': [0.1, 1, 10, 100]},
                    cv=5)
grid.fit(X_train, Y_train)
print(grid.best_params_)              # {'poly__degree': 2, 'regressor__alpha': 0.1}
print(grid.best_score_)               # 0.978 (학습 자료 안 5겹 교차 검증 평균)
print(grid.score(X_test, Y_test))     # 0.972 (가장 좋은 조합으로 다시 학습한 모델의 테스트 점수)
```

day13에서 `alpha` 여섯 개를 `for`로 돌리고 차수는 따로 바꿔 보던 일을 **조합 12개(3 × 4)를 전부, 교차 검증으로** 한 번에 한다. 파이프라인이 없으면 차수마다 변환기를 다시 만들고 표준화를 다시 해야 해서 이 실험을 깔끔하게 쓰기 어렵다. 파라미터 이름이 2-1의 `단계__파라미터` 그대로라는 점이 핵심이다. `grid.best_estimator_`가 가장 좋은 조합으로 학습된 파이프라인 객체이고, `grid.cv_results_`를 데이터프레임으로 만들면 12개 조합의 점수를 표로 볼 수 있다.

### 2-3. 새 물고기 예측 — 변환 걱정 없이

```python
new_fish = pd.DataFrame([[30, 10, 4]], columns=['Length2', 'Height', 'Width'])
pipe_model.predict(new_fish)          # [341.2]  g
```

손 코드였다면 `model.predict(ss.transform(poly.transform(new_fish)))`로 변환 둘을 순서대로 거쳐야 했다. 파이프라인은 1-4의 흐름대로 `transform` 둘을 안에서 처리한다. 열 이름이 있는 데이터프레임으로 넣으면 학습 때와 열 순서가 다를 때 경고로 알려 주므로, `[[30, 10, 4]]` 리스트보다 안전하다.

### 2-4. 통째로 저장하고 불러오기

```python
import joblib
joblib.dump(pipe_model, 'fish_model.pkl')        # 변환 규칙 + 모델이 한 파일에
loaded = joblib.load('fish_model.pkl')
loaded.predict(new_fish)
```

day12 2-7에서 모델 하나만 저장하던 것과 달리, 파이프라인은 `poly`의 차수·`scaler`의 평균과 표준편차·`regressor`의 기울기가 **한 파일**에 담긴다. 서비스 코드에서 "표준화는 어떤 평균으로 했더라"를 따로 기억할 필요가 없다 — day11에서 본 API 서버 쪽에 모델을 붙인다면 이 파일 하나를 읽어 `predict`만 부르면 된다.

### 2-5. 교차 검증으로 1-2의 흔들림 재기

```python
from sklearn.model_selection import cross_val_score
scores = cross_val_score(pipe_model, X, Y, cv=5)
print(scores.round(3))                # [0.76  0.962 0.911 0.967 0.044]
print(scores.mean(), scores.std())
```

자료를 5겹으로 갈라 다섯 번 학습·평가한다. 매 겹마다 파이프라인 안의 변환기가 **그 겹의 학습 부분으로만 `fit`**되므로 누수 없이 공정하다 — 변환을 밖에서 미리 해 두고 `cross_val_score`에 넣으면 전체 자료의 평균·표준편차가 스며든다. 결과를 보면 겹 하나가 0.04로 무너지는데, `cross_val_score`는 기본적으로 **섞지 않고** 순서대로 자르기 때문이다. Fish.csv는 종(`Species`)별로 정렬되어 있어 마지막 겹에는 학습 때 못 본 종이 몰린다. `cv=KFold(5, shuffle=True, random_state=42)`로 섞으면 고르게 나온다. 1-2의 "분할 운"이 얼마나 큰지 숫자로 보는 방법이다.

### 2-6. 열마다 다른 전처리 — `ColumnTransformer`

```python
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
pre = ColumnTransformer([
    ('num', StandardScaler(), ['Length2', 'Height', 'Width']),
    ('cat', OneHotEncoder(), ['Species']),
])
full = Pipeline([('pre', pre), ('regressor', Ridge(alpha=1))])
full.fit(df[['Length2', 'Height', 'Width', 'Species']], Y)
```

지금까지 특성이 전부 숫자여서 변환기 하나를 모든 열에 걸었다. 종(`Species`) 같은 문자열 열을 함께 쓰려면 숫자 열은 표준화, 범주 열은 원-핫(day08의 `get_dummies`에 해당하는 `OneHotEncoder`)처럼 **열 묶음마다 다른 변환기**가 필요하다. `ColumnTransformer`가 그 분배를 맡고, 그 자체가 변환기라 파이프라인의 한 단계로 들어간다. 파라미터 이름은 `pre__num__with_mean`처럼 밑줄이 한 번 더 깊어진다.

### 2-7. 결과를 데이터프레임으로 — `set_output`

```python
pipe_model.set_output(transform='pandas')
pipe_model[:-1].fit_transform(X_train).head()     # 모델 직전까지만 돌려 9열 데이터프레임으로 확인
```

변환기는 기본적으로 넘파이 배열을 돌려주어 열 이름이 사라진다. `set_output(transform='pandas')`를 걸면 `transform` 결과가 열 이름이 붙은 데이터프레임으로 나온다. `pipe_model[:-1]`처럼 슬라이싱하면 마지막 모델을 뺀 변환기 부분만 파이프라인으로 잘라 쓸 수 있어, 모델에 들어가기 직전 자료가 어떻게 생겼는지 들여다볼 때 편하다.

## 3. 더 나아가 알면 좋은 것

### 3-1. 파이프라인도 추정기다 — 같은 인터페이스

사이킷런의 모든 객체는 `fit`을 가진 **추정기(estimator)**이고, 그중 `transform`이 있으면 변환기, `predict`가 있으면 모델이다. `Pipeline`은 마지막 단계의 메소드를 자기 메소드처럼 내보내므로 바깥에서 보면 그냥 모델 하나다. 그래서 `GridSearchCV`·`cross_val_score`·`joblib`이 파이프라인인지 단일 모델인지 구분하지 않고 받는다. day12 1-12의 "알고리즘이 바뀌어도 `fit`·`predict`는 그대로"가 이 설계 덕분이고, 파이프라인은 그 규칙을 조합에까지 확장한 것이다. 직접 만든 변환 함수도 `FunctionTransformer(func)`로 감싸거나 `BaseEstimator`·`TransformerMixin`을 상속해 `fit`·`transform`을 정의하면 파이프라인 단계가 된다.

### 3-2. 타깃 쪽 변환 — `TransformedTargetRegressor`

특성은 파이프라인이 변환해 주지만 타깃 `Y`는 손대지 않는다. 무게처럼 오른쪽 꼬리가 긴 타깃은 로그를 취해 학습하고 예측값을 다시 지수로 되돌리는 편이 나을 때가 있는데, `TransformedTargetRegressor(regressor=pipe, func=np.log1p, inverse_func=np.expm1)`이 그 왕복을 맡는다. 특성 변환과 타깃 변환이 둘 다 있어도 `predict`는 여전히 한 줄이다.

### 3-3. 왜 "파이프라인"인가 — 다른 자리의 같은 이름

유닉스 셸의 `|`, 판다스의 메소드 체이닝(`.drop_duplicates().reset_index()`), 자바 스트림의 `map().filter().collect()`가 전부 "앞 단계의 출력이 다음 단계의 입력"이라는 같은 그림이다. 사이킷런 파이프라인이 특별한 점은 **학습 때와 예측 때 단계마다 하는 일이 다르다**(`fit_transform` vs `transform`)는 것을 객체가 기억한다는 것이고, 이것이 데이터 누수를 막는 장치가 된다. 실무에서 "학습 코드와 서비스 코드의 전처리가 미묘하게 달라 점수가 떨어지는" 문제(training-serving skew)를 피하는 가장 단순한 답이 전처리를 모델과 같은 객체에 넣는 것이다.

### 3-4. 분류로 가도 그대로

`regressor` 자리에 `LogisticRegression()`·`KNeighborsClassifier()`를 넣고 타깃을 `Species`로 바꾸면 분류 파이프라인이다. k-최근접 이웃은 거리를 재므로 `StandardScaler`가 선택이 아니라 필수에 가깝고, 그 변환을 파이프라인에 넣어 두면 잊을 일이 없다. `score`의 뜻이 R²에서 정확도로 바뀌는 것 외에 코드는 같다.

### 3-5. 다음에 볼 키워드

- `Pipeline([(이름, 객체), …])` · 마지막만 모델·앞은 변환기 · `make_pipeline` 자동 이름 · `named_steps`/`pipe['이름']`/`pipe.steps`/`pipe[:-1]`
- `fit` = 변환기 `fit_transform` + 모델 `fit` / `predict`·`score` = `transform`만 · 원본 특성을 넣는다 · 데이터 누수 구조적 차단
- `단계__파라미터` · `set_params`/`get_params` · `GridSearchCV(pipe, {'poly__degree': …, 'regressor__alpha': …})`·`best_params_`/`best_estimator_`/`cv_results_`
- `random_state` 없는 분할의 흔들림 · `cross_val_score(pipe, X, Y, cv=5)`·`KFold(shuffle=True)` · 정렬된 자료와 순서대로 자르기
- `joblib.dump(pipe)` 통째 저장 · `ColumnTransformer`+`OneHotEncoder` · `set_output(transform='pandas')` · `FunctionTransformer`·`TransformedTargetRegressor` · training-serving skew

## 실습 파일

- `KDT_2026/2026_Python/day14/s-04.py` — 1)~7) 번호 주석으로 `read_csv` → `df[['Length2', 'Height', 'Width']]`·`df['Weight']` → `train_test_split(test_size=0.2)` → `PolynomialFeatures(degree=2, include_bias=False)` `fit`·`transform` 둘 → `StandardScaler` `fit`·`transform` 둘 → `LinearRegression` `fit` → `score` 학습·테스트, "4 ~ 6 과정 묶음" 주석 아래 `Pipeline([('poly', …), ('scaler', …), ('regressor', …)])`와 "식별자, 클래스명() — 파이썬 인스턴스 생성" 주석, 9) `pipe_model.fit`·`score`
- `KDT_2026/2026_Python/day14/Fish.csv` — 캐글 Fish Market, 159마리 × `Species`·`Weight`·`Length1~3`·`Height`·`Width`
- 수업 PPT 「8. Pipeline」·「[1] 선형 회귀: Pipeline」 — 파이프라인 정의와 필요 이유(파편화·데이터 누수), 표준 파이프라인 vs `ColumnTransformer` 연계, Step 1 `fit`/Step 2 `predict` 그림, `pipe_poly_lr` 세 단계의 명칭·종류(변환기/예측기)·역할표, 훈련/테스트 R² 출력

## 관련 노트

[[AI 정리본 인덱스]] · [[AI day14 KFold 교차 검증과 GridSearchCV 하이퍼파라미터 탐색]] · [[AI day13 다항 규제 회귀 연습문제 풀이]] · [[AI day13 StandardScaler 표준화와 릿지·라쏘 규제]] · [[AI day13 다항 회귀 제곱항 추가와 PolynomialFeatures]] · [[AI day12 사이킷런 단순 선형 회귀로 물고기 무게 예측]] · [[KDT_2026 학습 지도]]
