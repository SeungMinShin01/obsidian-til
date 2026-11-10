---
출처: Claude 분석
원본: KDT_2026/2026_Python/day12/s-01.py, day12/Fish.csv, 수업 PPT
작성일: 2026-11-04
tags: [학습, ai, python]
---

# AI day12 — 사이킷런 단순 선형 회귀로 물고기 무게 예측

> 실습 파일: `day12/s-01.py`, `day12/Fish.csv`
> 허브: [[AI 정리본 인덱스]] · 이전: (Python 폴더) Python day11 httpx로 착한가격업소 API 수집과 업종별 평균 가격 실습 · 다음: [[AI day12 사이킷런 선형 회귀 연습문제 풀이]]

day06~09가 **자료를 읽고·고치고·그리는** 단계였고 day10~11이 **자료를 바깥에서 가져오는** 단계였다면, day12는 드디어 그 자료로 **무언가를 맞히는** 단계다. 도구는 사이킷런(`scikit-learn`), 재료는 캐글의 Fish Market 데이터(물고기 159마리의 종·무게·길이·높이·너비)다. 첫 모델은 가장 단순한 **단순 선형 회귀** — 물고기의 대각선 길이(`Length2`) 하나만 보고 무게(`Weight`)를 맞히는 직선 하나를 긋는다. 코드는 열 줄 남짓이지만 **특성·타깃 → 학습/테스트 분리 → `fit` → `coef_`·`intercept_` → `predict` → 산점도 위에 직선 → 떼어 둔 테스트 자료로 RMSE·R² 평가**라는 머신러닝 코드의 뼈대가 전부 들어 있어, 앞으로 나올 모델들은 이 뼈대에서 `LinearRegression` 한 줄만 바뀐다. 직선 하나로는 안 맞는 자료가 있다는 "문제점"과 그 답(다항 회귀)까지 수업 끝에 예고되어 있다.

## 1. 배운 내용

### 1-1. 사이킷런 — 머신러닝 알고리즘 모음

```bash
pip install scikit-learn      # 설치 이름은 scikit-learn, import 이름은 sklearn
```

수업 주석의 정의는 "방대한 머신러닝 알고리즘 모델 제공 라이브러리"다. 넘파이·판다스 위에서 돌아가며, 회귀·분류·군집 같은 알고리즘을 **같은 사용법**(`fit` → `predict`)으로 쓸 수 있게 묶어 둔 것이 핵심이다. `pip install` 이름과 `import` 이름이 다르다는 점은 `beautifulsoup4`/`bs4`와 같은 패턴이다.

| 단계 | 라이브러리 | 역할 |
| --- | --- | --- |
| 자료 읽기 | 판다스 | CSV → 데이터프레임 |
| 자료 다듬기 | 판다스·넘파이 | 전처리·열 추출 |
| 모델 학습·예측 | **사이킷런** | `fit`·`predict` |
| 결과 보기 | 맷플롯립 | 산점도·직선 |

### 1-2. 머신러닝 용어 — 특성·타깃, 지도·비지도

수업 주석을 표로 정리하면 이렇다.

| 용어 | 뜻 | 이번 예제 |
| --- | --- | --- |
| 머신러닝의 목표 | 추론/예측 | 길이로 무게 맞히기 |
| 특성(feature) | 모델이 학습하는 자료 정보 | `Length2` (대각선 길이 cm) |
| 타깃(target) | 모델이 맞혀야 하는 정답 정보 | `Weight` (무게 g) |
| 지도학습 | 특성과 타깃을 **모두** 주고 학습 — 회귀 / 분류 | 이번 예제 (회귀) |
| 비지도학습 | 타깃 없이 특성만으로 학습 — 군집 / 토픽 / 주성분 | — |

같은 것을 부르는 이름이 여럿이라 처음엔 헷갈린다. 수업 주석이 한 줄에 모아 둔 대로 **독립변수 = 입력변수 = 특성 = X**, **종속변수 = 목표변수 = 타깃 = Y**다. 통계 책은 독립/종속, 머신러닝 책은 특성/타깃, 코드는 X/Y라고 쓸 뿐 가리키는 것은 하나다.

**회귀와 분류의 차이**는 타깃이 무엇이냐다. 무게처럼 **연속된 숫자**를 맞히면 회귀, 종(Bream·Perch…)처럼 **범주**를 맞히면 분류다. 같은 Fish 데이터로도 `Weight`를 타깃으로 두면 회귀 문제, `Species`를 타깃으로 두면 분류 문제가 된다.

### 1-3. 자료 불러오기 — `pd.read_csv` → `info()`

```python
import pandas as pd
df = pd.read_csv('./day12/Fish.csv')
df.info()
```

```text
RangeIndex: 159 entries, 0 to 158
 #   Column   Non-Null Count  Dtype
 0   Species  159 non-null    object
 1   Weight   159 non-null    float64
 2   Length1  159 non-null    float64
 3   Length2  159 non-null    float64
 4   Length3  159 non-null    float64
 5   Height   159 non-null    float64
 6   Width    159 non-null    float64
```

day08부터 이어 온 "읽자마자 `info()`" 습관 그대로다. 159행·7열, 결측 없음, `Species`만 문자열이고 나머지는 전부 `float64` — 전처리 없이 바로 모델에 넣을 수 있는 깨끗한 자료다. 경로가 `./day12/Fish.csv`인 것은 실행 위치가 `2026_Python` 폴더이기 때문으로, VS Code에서 어느 폴더를 열고 실행하느냐에 따라 상대 경로의 기준이 달라진다.

| 열 | 뜻 |
| --- | --- |
| `Species` | 종 (Bream 35·Perch 56·Roach 20·Pike 17·Smelt 14·Parkki 11·Whitefish 6) |
| `Weight` | 무게 (g) — **타깃** |
| `Length1` · `Length2` · `Length3` | 세로 길이 · 대각선 길이 · 가로 길이 (cm) |
| `Height` · `Width` | 높이 · 너비 (cm) |

### 1-4. 특성과 타깃 추출 — X는 2차원, Y는 1차원

```python
feature = ['Length2']       # 리스트 — 특성은 2차원
target = 'Weight'           # 문자열 — 타깃은 1차원

X = df[feature]             # DataFrame (159, 1)
Y = df[target]              # Series    (159,)
```

가장 중요한 모양 규칙이다. 수업 주석 그대로 **"사이킷런 모델 구조상 학습할 특성은 2차원"**이어야 한다. 그래서 `feature`를 문자열이 아니라 **리스트**로 두고 `df[feature]`로 꺼내 데이터프레임(2차원)을 만든다. 타깃은 열 이름 문자열로 꺼내 시리즈(1차원)로 둔다.

| 표기 | 결과 | 차원 | 사이킷런 자리 |
| --- | --- | --- | --- |
| `df['Length2']` | `Series` | 1차원 `(159,)` | 타깃 Y |
| `df[['Length2']]` | `DataFrame` | 2차원 `(159, 1)` | 특성 X |

왜 특성만 2차원이냐면, 사이킷런은 **"행 = 표본, 열 = 특성"**인 표를 입력으로 전제하기 때문이다. 특성이 하나뿐이어도 열이 하나인 표여야 하고, 나중에 특성을 늘리면 `feature = ['Length2', 'Height', 'Width']`처럼 리스트에 이름만 더하면 되는 구조다. 특성 하나를 1차원으로 넘기면 `Expected 2D array, got 1D array instead`라는 오류가 나는데, 이때 메시지가 알려 주는 대로 `reshape(-1, 1)`을 쓰거나 처음부터 이중 대괄호로 꺼내면 된다. day08의 "이중 대괄호로 열 여러 개"가 여기서 "열 하나라도 이중 대괄호"로 쓰인다.

### 1-5. 학습용과 테스트용으로 나누기 — `train_test_split`

```python
from sklearn.model_selection import train_test_split
X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size=0.2, random_state=42)
# (127, 1) (32, 1) (127,) (32,)
```

159마리를 전부 학습에 쓰면 모델이 얼마나 잘 맞히는지 **확인할 자료가 남지 않는다.** 그래서 `test_size=0.2`로 20%(32마리)를 떼어 두고 80%(127마리)로만 학습한다. 시험 문제를 미리 풀어 본 학생의 점수를 믿을 수 없는 것과 같은 이치다.

| 인자 | 뜻 |
| --- | --- |
| `X, Y` | 나눌 특성과 타깃 — **같은 행이 같은 쪽**으로 간다 |
| `test_size=0.2` | 테스트용 비율 (0.25가 기본값) |
| `random_state=42` | 섞을 때 쓰는 난수 씨앗 — 같은 숫자면 매번 같은 분할 |

반환값은 **네 개를 한 번에 튜플로** 돌려주고 day03의 언패킹으로 받는다. 순서가 `X_train, X_test, Y_train, Y_test`로 고정이라 변수 이름을 바꿔도 자리는 지켜야 한다. `random_state`는 day09의 `np.random.seed(42)`와 같은 역할로, 숫자를 고정해야 코드를 다시 돌려도 같은 결과가 나와 비교가 된다. 분할은 **무작위로 섞은 뒤** 자르기 때문에 CSV가 종별로 정렬되어 있어도 학습용에 한 종만 몰리지 않는다.

### 1-6. 모델 만들기와 학습 — `LinearRegression().fit()`

```python
from sklearn.linear_model import LinearRegression
model = LinearRegression()
model.fit(X_train, Y_train)
```

사이킷런의 모델은 전부 **① 클래스로 객체 만들기 → ② `fit(특성, 타깃)`** 두 줄이다. `fit`이 "학습"이고, 단순 선형 회귀의 학습이란 127개 점을 가장 잘 지나는 **직선 하나**를 찾는 것이다. day05에서 만든 클래스처럼 `LinearRegression()`으로 인스턴스를 만들고, `fit`을 부르면 그 인스턴스 안에 학습 결과가 저장된다. 학습용(`_train`)만 넘기고 테스트용은 아직 건드리지 않는다.

### 1-7. 학습 결과 읽기 — `coef_`와 `intercept_`

```python
print(model.coef_)        # [30.43...]   기울기
print(model.intercept_)   # -477.3...    절편
```

직선은 `y = a·x + b`이고, 사이킷런은 기울기 `a`를 `coef_`, 절편 `b`를 `intercept_`라는 **속성**에 넣어 둔다(끝의 밑줄은 "학습 뒤에 생기는 값"이라는 사이킷런 표기 관례). 이번 결과를 식으로 쓰면 다음과 같다.

```text
무게(g) ≈ 30.4 × 대각선 길이(cm) − 477
```

| 속성 | 값 | 읽는 법 |
| --- | --- | --- |
| `coef_` | `[30.43]` | 길이가 1 cm 늘면 무게가 약 30 g 는다 — **배열**인 이유는 특성이 여러 개면 기울기도 여러 개라서 |
| `intercept_` | `-477.3` | 길이 0일 때의 무게 — 음수라 현실엔 없는 값, 직선을 맞추다 보니 나온 숫자 |

절편이 음수인 것이 보여 주듯 이 직선은 **자료가 있는 범위(길이 8~63 cm) 안에서만** 의미가 있다. 길이 10 cm 아래로 내려가면 음수 무게가 나오는데, 이것이 단순 선형 회귀의 한계이자 3-1에서 다항 회귀가 나오는 이유다.

### 1-8. 예측 — `predict([[30]])`

```python
print(model.predict([[30]]))   # [435.7...]
```

학습된 직선에 새 길이를 넣어 무게를 돌려받는다. 입력이 `[[30]]`로 **대괄호 두 겹**인 것은 1-4와 같은 이유다 — "표본 1개, 특성 1개"인 2차원 표여야 한다. `[30]`으로 넣으면 1차원이라 오류가 난다. 손으로 확인하면 `30.43 × 30 − 477.3 ≈ 435.7`로 `coef_`·`intercept_`와 정확히 맞는다.

```python
model.predict([[0], [100]])    # [-477.3, 2566.1] — 표본 2개를 한 번에
```

표본 여러 개는 바깥 리스트에 줄을 더하면 되고, 반환값도 같은 길이의 배열이다. 이 줄이 바로 다음 산점도에서 직선을 긋는 데 쓰인다.

### 1-9. 산점도 위에 직선 그리기

```python
import matplotlib.pyplot as plt
plt.scatter(X_train, Y_train)                               # 학습용 점 127개
plt.scatter([30], model.predict([[30]]), color="red")       # 예측한 점 하나
plt.plot([0, 100], model.predict([[0], [100]]))             # 직선 — 양 끝 두 점
plt.show()
```

| 줄 | 그리는 것 | 왜 |
| --- | --- | --- |
| `scatter(X_train, Y_train)` | 학습에 쓴 점들 | 직선이 점들 사이를 지나는지 눈으로 확인 |
| `scatter([30], predict(...), color="red")` | 길이 30의 예측점 | 직선 위에 빨간 점으로 올라가는 것 확인 |
| `plot([0, 100], predict([[0], [100]]))` | 회귀 직선 | 직선은 **두 점만 있으면** 그려진다 — x 양 끝 0·100의 예측값을 잇기 |

day09의 산점도(`scatter`)와 선 차트(`plot`)를 한 도화지에 겹친 것이다. 직선을 그리려고 x를 촘촘히 만들 필요 없이 **양 끝 두 점의 예측값**만 이으면 되는 것이 선형 회귀라서 가능한 요령이다. 그림을 보면 점들이 직선 주위에 모여 있지만 길이가 길어질수록 위로 휘어 올라가는 경향이 보이는데, 이 "휨"이 3-1의 출발점이다. `show()`는 함수 호출이므로 괄호까지 적어야 창이 뜬다 — 괄호를 빼면 함수 객체를 참조만 하고 아무 일도 일어나지 않는다.

### 1-10. 문제점 — 직선은 비례만 안다

수업 주석 11)이 짚는 한계는 한 줄이다. "x, y가 직선 관계이며 실 자료들은 꼭 비례 증가가 아닐 수 있다." 단순 선형 회귀는 길이가 1 cm 늘 때 무게가 항상 30.4 g씩 는다고 가정하는데, 1-9의 그림에서 본 것처럼 실제 물고기는 길어질수록 무게가 **더 가파르게** 는다. 직선은 이 휨을 따라가지 못해 작은 물고기는 음수 무게로, 큰 물고기는 실제보다 가볍게 찍는다. 주석이 적어 둔 해결책은 **다항 회귀로 확장해 특성을 추가**하는 것 — `x` 하나였던 특성에 `x²`를 더해 곡선으로 맞추는 방법이고, 코드는 3-1에 정리해 둔다. 핵심은 "모델을 바꾸는" 것이 아니라 "특성을 더하는" 것이라는 점이다.

### 1-11. 모델 평가 — 테스트 자료로 RMSE와 R² 구하기

```python
Y_pred = model.predict(X_test)      # 테스트용 특성 32개 → 예측 무게 32개

import numpy as np
from sklearn.metrics import mean_squared_error
rmse = np.sqrt(mean_squared_error(Y_test, Y_pred))
print("rmse:", rmse)                # 160.0

from sklearn.metrics import r2_score
r2 = r2_score(Y_test, Y_pred)
print("r2:", r2)                    # 0.8199... → 82%
```

1-5에서 떼어 둔 테스트 자료 32마리가 드디어 쓰이는 자리다. 학습에 쓰지 않은 특성(`X_test`)을 넣어 예측을 받고, 그 예측을 **정답지(`Y_test`)와 비교**해 점수를 낸다. 수업 주석의 표현대로 "훈련 세트는 규칙을 찾는 자료, 테스트 세트는 학습 후 평가·예측 성능 점수"다. 두 함수 모두 인자 순서가 `(정답, 예측)`이다.

| 지표 | 함수 | 값 | 읽는 법 |
| --- | --- | --- | --- |
| RMSE (평균 제곱근 오차) | `np.sqrt(mean_squared_error(Y_test, Y_pred))` | 160 g | 예측 무게가 실제와 **평균 160 g** 어긋남 — 타깃과 같은 단위 |
| R² (결정계수) | `r2_score(Y_test, Y_pred)` | 0.82 | 무게의 전체 변동 중 **82%**를 길이 하나가 설명 — 0~1 비율 |

`mean_squared_error`는 오차를 제곱해 평균 낸 값이라 단위가 g²이고 숫자가 커서(약 25,600) 감이 안 온다. 그래서 넘파이의 `sqrt`로 제곱근을 씌워 **다시 g 단위로** 돌려놓은 것이 RMSE다. 제곱을 거치기 때문에 크게 틀린 표본이 더 무겁게 반영된다 — 큰 물고기 몇 마리를 많이 빗나간 것이 160 g을 키운 주범이다. R²는 수업 주석대로 "타깃 데이터의 전체 변동성 대비 모델이 얼마나 잘 설명하는지 0~1 비율"이다. 1이면 완벽, 0이면 평균으로만 찍는 것과 같고, 음수가 나오면 평균보다도 못한 모델이다. 82%면 직선치고 꽤 잘 맞는 편이지만, 남은 18%가 1-10의 "휨"이다.

RMSE와 R²는 서로 보완한다 — R²는 단위가 없어 자료가 달라도 비교가 되고, RMSE는 "몇 g 틀리나"라는 현실 감각을 준다. 무게 평균이 398 g인 자료에서 160 g 오차는 작지 않으므로, R² 0.82라는 숫자만 보고 안심하긴 이르다.

### 1-12. 머신러닝 코드의 뼈대

```text
① 자료 읽기        pd.read_csv → info()
② 특성·타깃 분리   X = df[[...]] (2차원), Y = df['...'] (1차원)
③ 학습/테스트 분리 train_test_split(X, Y, test_size, random_state)
④ 모델 생성·학습   model = 알고리즘();  model.fit(X_train, Y_train)
⑤ 결과 확인        coef_ · intercept_ (모델마다 다름)
⑥ 예측            model.predict(새 X)
⑦ 시각화          scatter + plot
⑧ 평가            predict(X_test) → RMSE · R² (테스트 자료)
```

이 여덟 단계가 사이킷런 코드의 공통 틀이다. 알고리즘을 바꿔도 ④의 클래스 이름만 달라지고 `fit`·`predict`는 그대로이며, ⑧의 지표만 회귀(RMSE·R²)냐 분류(정확도)냐에 따라 바뀐다.

### 1-13. 수업 슬라이드 — 회귀 모델이란

슬라이드의 정의부터 다시 적어 둔다. 회귀 모델은 지도 학습의 한 갈래로, **종류를 분류하는 것이 아니라 연속적인 수치를 예측**하는 알고리즘이다. 물고기의 길이로 무게를 맞히는 것이 그 전형이다. 성능 평가도 분류처럼 "맞힌 비율(정확도)"이 아니라 **결정계수(R²)** 를 쓴다 — 0~1 사이 값으로, 1에 가까울수록 예측이 실제 자료를 잘 설명한다는 뜻이다. 슬라이드는 이 수업에서 다룰 회귀 모델을 세 갈래로 미리 그려 둔다.

| 모델 | 한 줄 정의 | 언제 |
| --- | --- | --- |
| 단순 선형 회귀 `LinearRegression` | 가중치(기울기)와 절편(편향)을 찾아 `Y = W × X + B` 직선을 긋는다 | 특성과 타깃이 비례에 가까울 때 |
| 다항 회귀 | 특성을 제곱하는 식으로 항을 늘려 2차 이상의 **곡선**으로 맞춘다 | 길이가 커질수록 무게가 곡선으로 뻗을 때 |
| 규제 회귀 `Ridge` / `Lasso` | 다항 항을 너무 많이 넣어 과대적합됐을 때 가중치를 누른다 | 릿지는 0에 가깝게 완만하게, 라쏘는 아예 0으로 만들어 특성 제거 |

이 노트가 첫째 줄이고, 다음 노트들이 둘째·셋째 줄이다. 슬라이드의 두 그림 — 직선 주위에 점이 흩어지고 점마다 세로 막대(오차)가 달린 왼쪽 그림과, `Polynomial Regression` 제목 아래 점들이 위로 휘어 올라가는 오른쪽 그림 — 이 각각 1-9의 산점도와 다음 노트의 곡선이다.

### 1-14. 수업 슬라이드 — 데이터 준비: `.copy()`와 종 하나만 고르기

```python
import pandas as pd
df = pd.read_csv('./fish.csv')
df = df[df['Species'] == 'Perch'].copy()     # 농어(Perch)만 골라 독립 복사본으로

features = ['Length2']
target = 'Weight'
X = df[features]      # 2차원 데이터프레임 (N, 1)
Y = df[target]        # 1차원 시리즈 (N,)
```

수업 코드(`s-01.py`)는 159마리 전부를 썼지만, 슬라이드는 **농어(`Perch`) 56마리만** 골라 쓴다. 종이 섞이면 같은 길이라도 무게가 제각각이라 직선이 잘 안 맞기 때문이다. 그래서 슬라이드의 기울기·절편·R²가 1-7·1-11의 숫자와 다르다 — 모델이 다른 것이 아니라 **재료가 다른 것**이다.

두 가지 표현을 슬라이드가 따로 짚는다.

| 코드 | 슬라이드 설명 | 왜 |
| --- | --- | --- |
| `df[df['Species'] == 'Perch'].copy()` | 원본 메모리를 참조하는 **뷰(View)** 가 아니라 독립된 메모리 공간의 **복사본** | 불리언 필터 결과에 열을 추가하거나 값을 바꾸면 "원본을 고치는 건지 사본을 고치는 건지" 모호하다는 `SettingWithCopyWarning`이 뜬다. `.copy()`를 붙이면 그 모호함이 사라진다 |
| `df[['Length2']]` (리스트) | 문자열 1개가 아니라 **컬럼명 리스트**를 넣어 `(샘플 수, 특성 수)` 2차원 `DataFrame` 반환 | 사이킷런의 `fit`은 특성이 1개여도 입력을 반드시 2차원 행렬로 요구한다 — 그래서 대괄호가 두 겹 |

슬라이드의 그림 한 장이 이 전부다 — `fish.csv` 표에서 `Length2` 열(46, 46, 49, 70, 60, 65 …)이 왼쪽 파란 상자 **X(특성/Features, 2차원 데이터프레임)** 로, `Weight` 열(181, 180, 195, 143, 370, 240 …)이 오른쪽 주황 상자 **Y(타깃/Target, 1차원 시리즈)** 로 빠져나오고, 가운데 화살표가 `X → 기계 학습 → Y`다. 입력 변수 = `features`(독립변수, X), 목표 변수 = `target`(종속변수, Y)이라는 용어 짝도 슬라이드 아래에 적혀 있다.

### 1-15. 수업 슬라이드 — 분리와 학습, 용어 대응표

```python
from sklearn.model_selection import train_test_split
X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size=0.2, random_state=42)
```

슬라이드가 `train_test_split`의 세 가지를 풀어 적는다. 전체 문제지(X)와 정답지(Y)를 **1:1 대응을 유지한 채** 비율대로 네 덩어리로 나눈다는 것, `test_size=0.2`는 20%를 테스트(`X_test`·`Y_test`)·80%를 학습(`X_train`·`Y_train`)으로 쓴다는 뜻이라는 것, `random_state=42`는 섞을 때 쓰는 난수 생성기의 **씨앗(Seed)** 이라 고정하면 언제 몇 번을 돌려도 같은 분할이 나온다는 것. 이렇게 나누는 이유는 모델이 **이미 외워 버린 문제로 시험을 치르는 데이터 누수(Leakage)** 와 과적합을 막고, 새 데이터에 대한 실전 성능을 공정하게 재기 위해서다. 훈련 세트는 "규칙을 찾고 구조를 학습하는 데", 테스트 세트는 "학습이 끝난 뒤 점수를 매기는 테스트 목적으로만" 쓴다.

```python
from sklearn.linear_model import LinearRegression
model = LinearRegression()        # 최소제곱법(OLS) 기반 선형 회귀의 빈 인스턴스
model.fit(X_train, Y_train)       # 오차를 최소화하는 1차 함수 y = wx + b를 스스로 계산

print(model.coef_)                # 학습된 가중치(기울기) — 1차원 넘파이 배열
print(model.intercept_)           # 학습된 편향(y절편) — 실수 하나
Y_pred = model.predict(X_test)
```

`coef_`는 "길이가 1 cm 늘 때 무게가 평균 몇 g 느는가", `intercept_`는 "길이가 0일 때의 기본 시작점"이다. 슬라이드가 `intercept_`에 덧붙인 말이 1-7의 음수 절편 이야기와 같다 — **이 값이 큰 음수면 길이가 짧은 작은 물고기의 무게가 음수로 계산되는 주요 원인**이 된다. 네 가지 이름을 한 표로 묶어 둔 것이 유용하다.

| 수학 (1차 함수) | 사이킷런 코드 | 머신러닝 실무 용어 | 물고기 예제에서의 뜻 |
| --- | --- | --- | --- |
| y (종속변수) | `Y` (타깃) | Target | 예측하려는 무게 `Weight` |
| x (독립변수) | `X` (특성) | Feature | 입력인 길이 `Length2` |
| a (기울기) | `model.coef_[0]` | Weight(가중치) / 계수 | 길이 1 cm당 무게 증가량 |
| b (y절편) | `model.intercept_` | Bias(편향) / 절편 | 길이 0 cm일 때의 기본 시작점 |

슬라이드 오른쪽 그림이 최소제곱법(OLS)을 한 장으로 보여 준다 — 빨간 직선 `y = ax + b` 주위로 파란 점이 흩어져 있고, 점마다 직선까지 세로 점선(오차·잔차 d)이 달려 있다. **그 오차의 제곱합 Σd²을 가장 작게 만드는 a와 b를 찾는 것**이 `fit`이 하는 일이다(3-2).

### 1-16. 수업 슬라이드 — 평가와 1차 방정식 직접 계산

```python
from sklearn.metrics import mean_squared_error, r2_score
import numpy as np
rmse = np.sqrt(mean_squared_error(Y_test, Y_pred))
r2 = r2_score(Y_test, Y_pred)
print(f"R²: {r2:.4f} | RMSE: {rmse:.2f}g")

pred_50  = model.predict([[50]])
pred_100 = model.predict([[100]])
print(f"길이 50cm 예상 무게 : {pred_50[0]:.2f}g")
print(f"길이 100cm 예상 무게: {pred_100[0]:.2f}g")
```

RMSE는 잔차를 제곱해 평균 낸 MSE에 루트를 씌운 것이다. 제곱하면서 커진 단위를 **타깃의 물리 단위(g)로 되돌려** 주므로 "모델이 실제 무게와 평균 몇 g 정도 틀리는지"를 직관적으로 읽을 수 있다. R²는 타깃의 전체 변동 중 모델이 설명하는 비율이다(1-17에서 손으로 계산한다). `predict`는 학습을 마친 수식에 테스트 특성을 대입해 샘플별 예측값을 1차원 배열로 돌려준다.

슬라이드가 모델이 학습한 식을 **손으로 대입해 `predict`와 맞춰 본다**. 농어 56마리 기준이다.

```text
기울기 a (model.coef_[0])    : 39.0537
y절편 b (model.intercept_)   : −714.3652
완성된 식                    : 무게(y) = 39.0537 × 길이(x) − 714.3652

길이 50 cm 대입 (x = 50)
  1단계) a × x : 39.0537 × 50 = 1952.685
  2단계) + b   : 1952.685 + (−714.3652) = 1238.3198 g

직접 수식 계산 → 1238.32 g
model.predict([[50]]) → array([1238.32])
```

둘이 같다. `predict`가 하는 일이 "저장된 `coef_`·`intercept_`로 1차식을 계산하는 것" 그 이상도 이하도 아니라는 점이 확인된다. 농어만 쓴 직선은 R² 0.84·RMSE 138 g 정도로, 전체 종을 섞은 1-11(0.82·160 g)보다 조금 낫다.

### 1-17. 수업 슬라이드 — 결정계수를 손으로 계산하기

R²의 정의는 "아무 모델 없이 **평균값**으로만 찍었을 때의 오차 대비, 우리 회귀선이 오차를 얼마나 줄였는가"다.

```text
R² = 1 − SSE / SST = 1 − Σ(yᵢ − ŷᵢ)² / Σ(yᵢ − ȳ)²

SST (Total Sum of Squares) : 평균값 ȳ로만 뭉뚱그려 예측했을 때의 잔차 제곱합 — 자료 자체의 전체 변동
SSE (Sum of Squared Errors): 학습시킨 회귀선 ŷ으로 예측했을 때 여전히 남은 잔차 제곱합
```

슬라이드의 수치 예시 — 물고기 세 마리.

| | 값 |
| --- | --- |
| 실제 무게 y | 100 g, 200 g, 300 g |
| 평균 ȳ | (100 + 200 + 300) / 3 = 200 g |
| 모델 예측 ŷ | 120 g, 190 g, 310 g |

```text
1. SST = (100−200)² + (200−200)² + (300−200)² = 10,000 + 0 + 10,000 = 20,000
2. SSE = (100−120)² + (200−190)² + (300−310)² = 400 + 100 + 100   = 600
3. R²  = 1 − 600 / 20,000 = 1 − 0.03 = 0.97  (97%)
```

해석은 이렇다 — "아무 정보 없이 평균값으로 찍었을 때 생기던 오차 20,000 중 **97%를 길이(X)를 반영한 회귀선이 설명해 내어**, 남은 오차를 3%(600) 수준으로 줄였다." 그래서 1(100%)에 가까울수록 패턴을 완벽히 설명하는 모델, 0(0%)이면 평균으로 찍는 것과 차이가 없는 모델이다. **음수가 나오면 평균으로 예측하는 것보다도 못한 모델**이라는 뜻인데, 과대적합된 모델을 테스트 자료에 대면 실제로 큰 음수가 나온다(다음 노트의 `degree=10`).

### 1-18. 수업 슬라이드 — 시각화와 직선의 한계

```python
import matplotlib.pyplot as plt
plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False
plt.scatter(X_test, Y_test, color='steelblue', alpha=0.8, label='실제 데이터')
plt.scatter([40], model.predict([[40]]), color='red')                 # 특정 길이의 예측값 강조
plt.plot([15, 100], model.predict([[15], [100]]))                      # 회귀선 — 시작점 15, 끝점 100
plt.title('길이에 따른 무게 예측선'); plt.xlabel('길이 (cm)'); plt.ylabel('무게 (g)')
plt.legend(); plt.show()
```

1-9와 같은 구조인데 **테스트 세트**를 점으로 찍었다는 점이 다르다. 파란 점은 테스트 농어 — 길이 10~45 cm, 무게 0~1,000 g 언저리에 분포한다. 파란 직선은 모델이 학습한 `y = wx + b`를 [15, 100] 구간에 그린 것이고, 빨간 점은 길이 40 cm의 예측값(약 847 g)을 강조해 찍어 둔 것이다. 그림을 보면 왼쪽 아래 작은 물고기들이 직선 **아래**로 처져 있고, 직선은 15 cm 근처에서 이미 0 g 밑으로 내려간다.

슬라이드의 메모가 핵심이다 — x와 y가 직선 관계라고 가정했지만, 실제 물고기는 길이가 1씩 늘 때 무게가 꼭 비례해서 늘지 않는다. 초반에는 길이에 따라 무게가 3배씩 늘다가 중후반에는 2배, 1배로 둔해질 수 있다. 사람 키가 어릴 때는 쑥쑥 자라다 나이 들면 멈추는 것과 같다. 선형 회귀는 **구간마다 변화율이 달라지는 곡선 패턴을 단 하나의 직선으로 단순화**하기 때문에 과소적합과 음수 예측이라는 물리적 오류를 피할 수 없고, 그래서 거듭제곱 특성을 추가해 유연성을 높이는 **다항 회귀**로 넘어간다(3-1, 다음 노트).

## 2. 추가로 알면 좋은 활용법

### 2-1. 평가 지름길 `score`와 학습·테스트 점수 비교

```python
print(model.score(X_train, Y_train))   # 0.849
print(model.score(X_test, Y_test))     # 0.820  ← r2_score(Y_test, Y_pred)와 같은 값
```

회귀 모델의 `score`는 안에서 `predict`까지 하고 **R²를 바로 돌려주는** 지름길이다. 1-11의 `r2_score(Y_test, Y_pred)`와 값이 같다. 이 한 줄 덕에 학습용과 테스트용 점수를 나란히 놓기 쉬운데, 학습용 0.85·테스트용 0.82로 큰 차이가 없으면 외운 것이 아니라 일반화된 것이다. 학습용 점수만 높고 테스트용이 뚝 떨어지면 **과적합**이고, day09에서 `val_loss`가 다시 오르는 그래프로 본 현상이 이것이다.

```python
from sklearn.metrics import mean_absolute_error
print(mean_absolute_error(Y_test, Y_pred))   # 128.8 — 평균 절대 오차 (g)
```

RMSE의 짝으로 **MAE**(평균 절대 오차)도 자주 본다. 제곱 없이 오차의 절댓값을 평균 내므로 큰 실수에 덜 끌려간다. 같은 자료에서 MAE 129 g < RMSE 160 g인데, 이 차이가 클수록 "몇 마리를 크게 틀렸다"는 신호다.

### 2-2. 특성을 여러 개로 — 다중 선형 회귀

```python
feature = ['Length2', 'Height', 'Width']
X = df[feature]
# ... 나머지 코드는 그대로
print(model.coef_)        # 기울기 세 개
```

`feature` 리스트에 이름을 더하는 것만으로 **다중 선형 회귀**가 된다. 1-4에서 특성을 굳이 2차원으로 두는 이유가 여기서 드러난다 — 열이 늘어도 코드가 한 줄도 안 바뀐다. `coef_`가 배열인 이유도 같다. 다만 특성이 여럿이면 산점도 한 장으로는 못 그리므로, 그림 대신 `score`·오차로 평가한다.

### 2-3. 범주형 특성 넣기 — `get_dummies`

```python
X = pd.get_dummies(df[['Length2', 'Species']], columns=['Species'], dtype=int)
```

`Species`는 문자열이라 그대로는 모델에 못 넣는다. day08의 원-핫 인코딩(`get_dummies`)으로 종마다 0/1 열을 만들어 붙이면 "같은 길이라도 종에 따라 무게가 다르다"를 모델이 배울 수 있다. 전처리 노트에서 "모델 입력 직전 단계"라고 적어 둔 그 자리다.

### 2-4. 예측 입력을 데이터프레임으로

```python
new = pd.DataFrame({'Length2': [30]})
model.predict(new)
```

`predict([[30]])`처럼 순수 리스트를 넣으면 동작은 하지만 "학습 때는 열 이름이 있었는데 지금은 없다"는 경고가 나올 수 있다. 학습에 쓴 것과 **같은 열 이름의 데이터프레임**으로 넣으면 경고도 없고, 특성이 여러 개일 때 순서를 잘못 넣는 실수도 막는다.

### 2-5. 넘파이 배열로 넘길 때 — `reshape(-1, 1)`

```python
x = df['Length2'].values            # (159,) 1차원
model.fit(x.reshape(-1, 1), Y)      # (159, 1) 2차원
```

데이터프레임 대신 넘파이 배열로 작업할 때는 `reshape(-1, 1)`로 열 하나짜리 2차원을 만든다. `-1`은 "행 수는 알아서"라는 뜻이다. day06의 `reshape`가 사이킷런 입력 모양 맞추기에 그대로 쓰인다.

### 2-6. 그림 다듬기 — 제목·축 이름·범례

```python
plt.rc('font', family='Malgun Gothic')
plt.scatter(X_train, Y_train, label='학습 자료', alpha=0.6)
plt.plot([0, 100], model.predict([[0], [100]]), color='orange', label='회귀 직선')
plt.scatter([30], model.predict([[30]]), color='red', label='예측 (30cm)')
plt.title('대각선 길이와 무게'); plt.xlabel('Length2 (cm)'); plt.ylabel('Weight (g)')
plt.legend(); plt.grid(True, alpha=0.3); plt.show()
```

day09의 일곱 단계(figure → plot → title/xlabel/ylabel → grid → legend → show)를 그대로 얹은 것이다. `xlim`을 자료 범위(8~63)로 좁히면 음수 구간이 가려져 그림이 덜 어색하다.

### 2-7. 학습한 모델 저장 — `joblib`

```python
import joblib
joblib.dump(model, 'fish_lr.pkl')      # 저장
model = joblib.load('fish_lr.pkl')     # 다시 쓰기
```

학습은 한 번 하고 예측은 여러 번 하는 것이 보통이다. 모델 객체를 파일로 저장해 두면 다음 실행이나 다른 프로그램(예: API 서버)에서 `fit` 없이 바로 `predict`할 수 있다. day11의 "받은 뒤 바로 저장"과 같은 발상이다.

## 3. 더 나아가 알면 좋은 것

### 3-1. 직선이 안 맞을 때 — 다항 회귀

```python
from sklearn.preprocessing import PolynomialFeatures
from sklearn.pipeline import make_pipeline
poly_model = make_pipeline(PolynomialFeatures(degree=2), LinearRegression())
poly_model.fit(X_train, Y_train)
```

1-9의 그림에서 점들이 위로 휘는 것은 무게가 길이의 **세제곱**에 가깝게 늘기 때문이다(부피 ∝ 길이³). 직선 대신 `x²` 항을 추가한 곡선으로 맞추는 것이 다항 회귀이고, 절편이 음수가 되는 문제도 완화된다. `PolynomialFeatures`가 `x`에서 `x², x³…` 열을 만들어 주고, 그 뒤는 같은 `LinearRegression`이라 "선형" 회귀로 곡선을 맞출 수 있다. `make_pipeline`은 전처리와 모델을 한 객체로 묶어 `fit`·`predict`를 한 번에 부르게 한다.

### 3-2. 최소제곱법 — `fit`이 하는 일

`fit`은 "모든 점에서 직선까지의 **세로 거리 제곱의 합**이 최소가 되는 `a`·`b`"를 구한다. 이것이 최소제곱법이고, 단순 선형 회귀는 공식이 있어 한 번에 계산된다(`a = 공분산(x, y) / 분산(x)`, `b = ȳ − a·x̄`). day07의 분산·표준편차와 day09의 상관계수(`corr`)가 그대로 재료가 된다 — 상관계수가 높을수록 직선이 잘 맞고, R²는 상관계수의 제곱과 같다. 특성이 많거나 자료가 큰 모델은 공식 대신 **경사 하강법**으로 오차를 조금씩 줄여 가며 찾는데, day09의 epoch별 손실 그래프가 바로 그 과정의 기록이다.

### 3-3. 선형 회귀의 가정과 규제

직선 모델은 몇 가지를 가정한다 — 관계가 선형이고, 오차가 고르게 퍼져 있고, 특성끼리 서로 중복되지 않는다는 것. `Length1`·`Length2`·`Length3`처럼 거의 같은 정보를 담은 열을 다 넣으면 **다중공선성**으로 기울기가 불안정해지는데(day09 히트맵에서 0.85 이상 강한 상관을 확인하던 자리), 이를 누르는 것이 `Ridge`(L2)·`Lasso`(L1) 같은 **규제** 모델이다. 클래스 이름만 `LinearRegression` → `Ridge(alpha=1.0)`로 바꾸면 되는 것이 사이킷런의 장점이다.

### 3-4. 분류로 넘어가기 — 같은 뼈대

```python
from sklearn.neighbors import KNeighborsClassifier
X = df[['Length2', 'Weight']]; Y = df['Species']
clf = KNeighborsClassifier().fit(X_train, Y_train)
clf.predict([[30, 400]])     # 'Bream' 같은 종 이름
clf.score(X_test, Y_test)    # 정확도 (맞힌 비율)
```

같은 Fish 자료로 타깃을 `Species`로 바꾸면 분류 문제다. 1-12의 여덟 단계가 그대로이고, 모델 클래스와 `score`의 뜻(R² → 정확도)만 달라진다. k-최근접 이웃·로지스틱 회귀·결정 트리·랜덤 포레스트가 분류 쪽의 첫 모델들이다.

### 3-5. 특성 스케일링과 파이프라인

길이(cm)와 무게(g)처럼 단위와 범위가 다른 특성을 함께 쓰면 거리 기반 모델(k-NN·SVM)이나 규제 모델이 큰 숫자 쪽에 끌려간다. day07·08에서 손으로 하던 Min-Max 정규화·Z-score 표준화가 `MinMaxScaler`·`StandardScaler`로 제공되며, **학습용으로 `fit`한 스케일러를 테스트용에는 `transform`만** 적용해야 테스트 정보가 학습에 새지 않는다(데이터 누수). `Pipeline`으로 스케일러와 모델을 묶으면 이 순서가 자동으로 지켜진다.

### 3-6. 교차 검증과 하이퍼파라미터 탐색

한 번의 `train_test_split`은 운에 따라 점수가 흔들린다. `cross_val_score(model, X, Y, cv=5)`로 자료를 다섯 조각으로 나눠 다섯 번 평가한 평균을 보면 더 믿을 만하다. `degree`·`alpha`·`n_neighbors`처럼 사람이 정하는 값(하이퍼파라미터)은 `GridSearchCV`로 후보를 돌려 가장 좋은 조합을 고른다.

### 3-7. 다음에 볼 키워드

- `scikit-learn`/`sklearn` · 특성·타깃 · 지도학습(회귀/분류) · 비지도학습(군집/토픽/주성분) · 독립변수/종속변수
- `df[[...]]` 2차원 X vs `df['...']` 1차원 Y · `reshape(-1, 1)` · `Expected 2D array`
- `train_test_split(test_size, random_state, stratify)` · `fit`/`predict`/`score` · `coef_`/`intercept_` 밑줄 관례
- R²·MAE·RMSE·과적합 · `mean_absolute_error`/`mean_squared_error` · `cross_val_score`/`GridSearchCV`
- 다중 선형 회귀 · `get_dummies` 범주 특성 · `PolynomialFeatures`/`make_pipeline` 다항 회귀 · 최소제곱법·경사 하강법
- `Ridge`/`Lasso` 규제·다중공선성 · `StandardScaler`/`MinMaxScaler`·`Pipeline`·데이터 누수
- `KNeighborsClassifier`/`LogisticRegression`/`DecisionTreeClassifier` · `joblib` 모델 저장

## 실습 파일

- `KDT_2026/2026_Python/day12/s-01.py` — 사이킷런 단순 선형 회귀: `pip install scikit-learn` 주석과 머신러닝 목표·특성/타깃·지도/비지도 정의 주석, 캐글 Fish Market 출처 주석, `pd.read_csv('./day12/Fish.csv')` → `df.info()`, `feature = ['Length2']`(2차원 특성)·`target = 'Weight'` → `X = df[feature]`·`Y = df[target]`, `train_test_split(X, Y, test_size=0.2, random_state=42)` 네 변수 언패킹, `LinearRegression()` → `model.fit(X_train, Y_train)`, `model.coef_`·`model.intercept_` 출력, `model.predict([[30]])`, `plt.scatter(X_train, Y_train)` + 빨간 예측점 `scatter([30], …, color="red")` + `plt.plot([0, 100], model.predict([[0], [100]]))` 직선 → `show`, 11) 문제점 주석(직선 관계 가정·비례 증가가 아닐 수 있음 → 다항 회귀로 특성 추가), 12) 모델 평가 — `Y_pred = model.predict(X_test)` → `np.sqrt(mean_squared_error(Y_test, Y_pred))` RMSE(약 160 g) → `r2_score(Y_test, Y_pred)` 결정계수(0.82)
- `KDT_2026/2026_Python/day12/Fish.csv` — 물고기 159마리 × 7열(`Species`·`Weight`·`Length1`·`Length2`·`Length3`·`Height`·`Width`), 종 7가지, 결측 없음
- 수업 PPT 「1. 회귀모델 이란」·「[1]~[5] 단순 선형 회귀 : 데이터 준비·분리·학습 및 예측·평가·시각화」·「3. 결정계수 이란?」 — 회귀 세 갈래 표, `Perch` 필터 + `.copy()`, 2차원 특성 추출 그림, `train_test_split` 세 인자, OLS 그림과 용어 대응표, RMSE·R²와 1차식 직접 계산(39.0537 × 50 − 714.3652 = 1238.32), SST/SSE 손계산(0.97), 테스트 세트 산점도 + 40 cm 예측점 + [15, 100] 회귀선, 직선의 한계 메모

## 관련 노트

[[AI 정리본 인덱스]] · [[AI day12 사이킷런 선형 회귀 연습문제 풀이]] · [[KDT_2026 학습 지도]]
