---
출처: Claude 분석
원본: KDT_2026/2026_Python/day14/s-06.py, day14/Fish.csv
작성일: 2026-11-10
tags: [학습, ai, python]
---

# AI day14 — 로지스틱 회귀로 도미·빙어 분류

> 실습 파일: `day14/s-06.py`, `day14/Fish.csv`
> 허브: [[AI 정리본 인덱스]] · 이전: [[AI day14 파이프라인·그리드서치·joblib 연습문제 풀이]] · 다음: [[AI day14 로지스틱 이진 분류 연습문제 풀이]]

day12부터 지금까지는 전부 **회귀**였다 — 타깃이 `Weight`라는 연속 숫자였고, 모델은 "몇 g인가"를 맞혔다. 이 노트에서 처음으로 타깃이 **범주**(`Species`)로 바뀐다. "도미인가 빙어인가"를 맞히는 **분류**다. day12 용어표에서 "타깃이 연속 숫자면 회귀·범주면 분류"라고 적어 둔 그 갈림길을 드디어 건넌다. 재미있는 것은 뼈대가 거의 그대로라는 점이다 — 읽기 → 특성/타깃 → 분리 → 표준화 → 모델 → 예측. 바뀌는 자리는 세 군데뿐이다. ① 타깃 열이 문자열이고, ② `train_test_split`에 `stratify=Y`가 붙고, ③ 모델 클래스가 `LinearRegression`에서 **`LogisticRegression`** 으로 바뀐다. 이름에 "회귀"가 들어 있지만 분류 모델이라는 것부터 정리한다.

## 1. 배운 내용

### 1-1. 도미(Bream)와 빙어(Smelt)만 고르기 — 이진 분류 자료 만들기

```python
import pandas as pd
df = pd.read_csv('./day14/Fish.csv')
df = df[(df['Species'] == 'Bream') | (df['Species'] == 'Smelt')]   # 두 종만 남긴다
X = df[['Weight', 'Length1', 'Length2', 'Length3', 'Height', 'Width']]
Y = df['Species']
```

`Fish.csv`의 159마리는 일곱 종이다(퍼치 56·도미 35·로치 20·파이크 17·빙어 14·파키 11·화이트피시 6). 처음 하는 분류니까 가장 단순한 형태인 **이진 분류**로 시작하기 위해 두 종만 남긴다. 도미는 무겁고 큰 쪽(평균 600 g대), 빙어는 10 g 남짓한 작은 물고기라 특성만 봐도 갈릴 만한 짝이다. 두 종을 고르고 나면 **49마리(도미 35·빙어 14)** 가 남는다.

| 항목 | 회귀(day12~14) | 이 노트 |
| --- | --- | --- |
| 특성 X | `Length2`·`Height`·`Width` 등 | `Weight`·`Length1`·`Length2`·`Length3`·`Height`·`Width` **여섯 개 전부** |
| 타깃 Y | `Weight` (연속 숫자) | `Species` (문자열 `'Bream'` / `'Smelt'`) |
| 문제 종류 | 회귀 — 몇 g인가 | 분류 — 어느 종인가 |

특성 쪽에 `Weight`가 들어온 것도 눈에 띈다. 회귀에서는 무게가 **정답**이라 특성에 못 넣었지만, 이제 정답이 종이니 무게는 당당한 **단서**가 된다. 같은 열이 문제에 따라 X가 되기도 Y가 되기도 한다.

행을 고르는 조건은 두 개의 불리언 시리즈를 `|`(또는)로 합친 것이다. 판다스에서 `|`는 `==`보다 **먼저** 계산되기 때문에 각 비교를 **괄호로 감싸는 것**이 필수다 — 괄호가 없으면 `'Bream' | df['Species']`가 먼저 시도되어 `TypeError`가 난다. day08의 불리언 인덱싱 규칙이 그대로다.

### 1-2. `train_test_split(…, stratify=Y)` — 클래스 비율을 지키며 나누기

```python
from sklearn.model_selection import train_test_split
# stratify=Y : 타깃 무작위 분리 시 클래스 비율 일정 유지
X_train, X_test, Y_train, Y_test = train_test_split(
    X, Y, test_size=0.2, random_state=42, stratify=Y
)
```

분리는 day12와 똑같은 함수인데 인자가 하나 늘었다. `stratify=Y`는 **"Y의 클래스 비율을 학습 세트와 테스트 세트에서 똑같이 유지해라"** 는 뜻이다. 49마리를 8:2로 나누면 학습 39·테스트 10마리인데, 도미:빙어가 35:14 ≈ 5:2이므로 테스트 10마리에도 **도미 7·빙어 3**이 들어가도록 뽑는다. 학습 쪽도 도미 28·빙어 11로 같은 비율이다.

| `random_state` | `stratify` 없음 — 테스트 10마리 | `stratify=Y` — 테스트 10마리 |
| --- | --- | --- |
| 42 | 도미 7 · 빙어 3 | 도미 7 · 빙어 3 |
| 1 | 도미 6 · 빙어 4 | 도미 7 · 빙어 3 |
| 7 | 도미 8 · **빙어 2** | 도미 7 · 빙어 3 |

`stratify` 없이 그냥 섞어 자르면 씨앗에 따라 빙어가 2마리만 들어가기도 한다. 빙어가 14마리뿐이라 더 운이 나쁘면 테스트에 빙어가 0~1마리가 될 수도 있고, 그러면 "빙어를 맞히는 능력"을 아예 평가하지 못한다. 회귀에서는 타깃이 연속 숫자라 비율이라는 개념이 없어 이 인자를 쓸 일이 없었다 — **분류로 넘어오면서 처음 등장한 인자**이고, 앞 노트 2-6의 `StratifiedKFold`가 교차 검증에서 하는 일을 `train_test_split`에서 하는 셈이다. 소수 클래스가 있는 분류 자료라면 거의 항상 붙이는 편이 안전하다.

### 1-3. `StandardScaler` — 분류에서도 표준화는 그대로

```python
from sklearn.preprocessing import StandardScaler
ss = StandardScaler()
ss.fit(X_train)                            # 학습 세트의 평균·표준편차만 기억
X_train_scaled = ss.transform(X_train)
X_test_scaled  = ss.transform(X_test)
```

day13에서 배운 순서 그대로다. `fit`은 학습 세트에만, `transform`은 둘 다. 여섯 특성의 단위가 제각각이기 때문에(`Weight`는 수백 g, `Width`는 1~6 cm) 표준화 없이는 무게 열 하나가 거리와 기울기를 전부 좌우한다. 학습 세트에서 기억한 평균과 표준편차는 이렇다.

| 열 | `Weight` | `Length1` | `Length2` | `Length3` | `Height` | `Width` |
| --- | --- | --- | --- | --- | --- | --- |
| `mean_` | 439.8 | 24.7 | 26.9 | 31.0 | 11.5 | 4.2 |
| `scale_` | 322.8 | 9.1 | 10.1 | 11.9 | 6.1 | 1.9 |

학습 세트 첫 행(600 g·29.4·32.0·37.2·15.4·5.58, 도미)은 `[0.50, 0.51, 0.50, 0.52, 0.65, 0.70]`으로 바뀐다 — 모든 열이 평균보다 반 표준편차쯤 큰, 전형적인 도미다. 빙어는 여섯 열이 모두 음수로 바뀐다. 로지스틱 회귀는 선형 모델이라 기울기에 규제가 걸리는데(2-3), 규제가 있으면 표준화가 전제라는 day13의 결론이 분류에도 똑같이 적용된다.

### 1-4. `LogisticRegression` — 이름은 회귀, 하는 일은 분류

```python
from sklearn.linear_model import LogisticRegression
model = LogisticRegression()
model.fit(X_train_scaled, Y_train)
Y_pred = model.predict(X_test_scaled)
print(Y_pred)
# ['Bream' 'Bream' 'Smelt' 'Bream' 'Bream' 'Smelt' 'Smelt' 'Bream' 'Bream' 'Bream']
```

`sklearn.linear_model`에서 가져오는 것부터 `LinearRegression`과 같은 집안이라는 뜻이다. 안에서 하는 일도 반쯤 같다 — 여섯 특성에 기울기를 곱하고 절편을 더해 **직선 하나의 값 z** 를 만든다. 다른 점은 그 z를 그대로 내놓지 않고 **시그모이드 함수**에 넣어 0~1 사이의 확률로 바꾼 뒤, 0.5를 기준으로 클래스를 고른다는 것이다.

```text
z = w1·Weight + w2·Length1 + … + w6·Width + b        ← 여기까지는 선형 회귀와 같다
p = 1 / (1 + e^(−z))                                 ← 시그모이드: 어떤 z든 0~1 사이로
p ≥ 0.5 → 'Smelt' (classes_[1]),  p < 0.5 → 'Bream' (classes_[0])
```

그래서 이름이 "로지스틱 **회귀**"다 — 시그모이드(로지스틱 함수)를 거친 **확률을 회귀**하는 모델이고, 그 확률로 분류를 한다. 학습이 끝난 모델 안을 들여다보면 회귀와 같은 속성이 들어 있다.

| 속성 | 값 | 뜻 |
| --- | --- | --- |
| `classes_` | `['Bream' 'Smelt']` | 클래스 이름을 **알파벳순**으로 정렬해 저장. 두 번째(`Smelt`)가 "양성(1)" 역할 |
| `coef_` | `[[-0.49 -0.69 -0.69 -0.72 -0.76 -0.71]]` | 여섯 특성의 기울기. 전부 음수 = 값이 클수록 z가 작아져 **도미 쪽** |
| `intercept_` | `[-2.80]` | 절편 |

기울기 여섯 개가 모두 비슷한 음수라는 것이 이 문제의 성격을 말해 준다 — "무엇이든 크면 도미, 작으면 빙어"다. 문자열 타깃을 그대로 넣어도 되는 것도 확인 포인트다. 사이킷런이 안에서 `'Bream'`→0, `'Smelt'`→1로 바꿔 학습하고, `predict`는 다시 문자열로 돌려준다. 회귀 때처럼 `coef_`가 2차원(`(1, 6)`)인 이유는 클래스가 셋 이상이면 클래스마다 한 줄씩 늘어나기 때문이다(2-5).

### 1-5. 결과 읽기 — 예측 10개와 정답 10개

```python
print(Y_pred)
# ['Bream' 'Bream' 'Smelt' 'Bream' 'Bream' 'Smelt' 'Smelt' 'Bream' 'Bream' 'Bream']
print(Y_test.values)
# ['Bream' 'Bream' 'Smelt' 'Bream' 'Bream' 'Smelt' 'Smelt' 'Bream' 'Bream' 'Bream']
print(model.score(X_test_scaled, Y_test))   # 1.0
```

수업 코드 4)는 `Y_pred`를 출력하는 데서 끝나고, 5)·6)에서 확률과 정확도로 이어진다(1-6). 열 개의 예측을 정답과 나란히 놓으면 **열 개 모두 맞았다** — 도미 7마리, 빙어 3마리. 회귀에서 `score`가 R²였듯이 분류에서 `score`는 **정확도**(맞힌 개수 ÷ 전체)이고, 여기서는 10/10 = 1.0이다. 학습 세트 39마리도 전부 맞혀 1.0이다. 도미와 빙어는 크기가 수십 배 차이 나는 쉬운 짝이라 완벽한 점수가 나오는 것이 이상하지 않다 — 중요한 것은 점수보다 **"회귀 뼈대 그대로, 클래스 이름만 바꿔 분류가 된다"** 는 사실을 눈으로 확인한 것이다.

`predict`가 숫자가 아니라 **문자열 배열**을 돌려준다는 점이 회귀와 가장 눈에 띄는 차이다. `score`도 R²에서 정확도로 의미가 바뀐다. 같은 메서드 이름이 문제 종류에 따라 다른 지표를 뜻하니, 분류 `score`를 보고 "결정계수"라고 읽지 않도록 한다.

### 1-6. 수업 코드 5)·6) — `classes_`·`predict_proba`·`accuracy_score`

```python
# 5) 결과 속성
print(model.classes_)                           # ['Bream' 'Smelt']  정답지 종류
print(model.predict_proba(X_test_scaled[:3]))   # 확률 반환
# [[0.99255987 0.00744013]      # Bream( 0 )열 , Smelt( 1 )열
#  [0.99568698 0.00431302]
#  [0.04598467 0.95401533]]

# 6) 정확도 평가 : accuracy_score( 테스트정답지 , 테스트예측 )
from sklearn.metrics import accuracy_score
acc = accuracy_score(Y_test, Y_pred)
print(acc)   # 1.0  => 100 %  현재 실습은 데이터가 적다
```

수업 코드가 4) `predict` 뒤에 두 단계를 더 붙였다. 5)는 모델이 **무엇을 어떤 순서로 알고 있는지**를 보는 자리다. `classes_`가 `['Bream' 'Smelt']`이니 `predict_proba`가 돌려주는 두 열은 `[도미 확률, 빙어 확률]`이고, 행마다 둘의 합은 1이다. 첫 표본은 도미 99.3 %, 셋째 표본은 빙어 95.4 % — `predict`가 `'Bream'`·`'Smelt'`라고 결론만 내던 것의 **근거 숫자**다. 1-4의 수식에서 시그모이드를 거친 p가 바로 둘째 열이고, 0.5를 넘으면 `Smelt`가 된다. 수업 주석이 열에 `( 0 )`·`( 1 )`을 적어 둔 것은 사이킷런이 안에서 문자열 클래스를 0·1 번호로 다룬다는 뜻이다.

6)은 **회귀의 `r2_score(Y_test, Y_pred)` 자리에 `accuracy_score(Y_test, Y_pred)`** 를 놓은 것이다. 같은 `sklearn.metrics`, 같은 `(정답, 예측)` 순서, 하는 일은 "맞힌 개수 ÷ 전체". `model.score(X_test_scaled, Y_test)`와 값은 같지만 인자가 **정답·예측 배열**이라 모델 객체 없이도, 임계값을 바꿔 만든 예측에도 쓸 수 있다는 점이 다르다. 결과 1.0 뒤에 적힌 "현재 실습은 데이터가 적다"가 이 날의 결론이다 — 테스트 10마리로 100 %는 모델이 완벽하다는 뜻이 아니라 **시험지가 작다**는 뜻이고, 도미·빙어가 크기부터 수십 배 다른 쉬운 짝이라는 점까지 겹쳤다. 표본이 늘고 클래스가 비슷해지면 정확도는 내려오고, 그때부터 2-4의 혼동 행렬이 필요해진다. 같은 뼈대를 569건·30특성 자료에 옮긴 연습이 [[AI day14 로지스틱 이진 분류 연습문제 풀이]]다.

### 1-7. 이 날의 흐름 한 장

```text
Fish.csv 159마리 ──▶ Bream | Smelt 두 종만 ──▶ 49마리 (도미 35 · 빙어 14)
        │
        ▼  X = 여섯 특성 전부(Weight 포함)  ·  Y = Species(문자열)
train_test_split(test_size=0.2, random_state=42, stratify=Y)
        │        학습 39 (28·11)        테스트 10 (7·3)   ← 비율 5:2 유지
        ▼
StandardScaler  fit(학습) → transform(학습·테스트)
        ▼
LogisticRegression().fit  →  z = w·x + b  →  시그모이드  →  p ≥ 0.5 ? Smelt : Bream
        ▼
predict(테스트) = ['Bream' 'Bream' 'Smelt' …]  10/10 정답
        ▼
classes_ ['Bream' 'Smelt'] · predict_proba [도미 p, 빙어 p] · accuracy_score(Y_test, Y_pred) = 1.0
```

## 2. 추가로 알면 좋은 활용법

### 2-1. 확률까지 보기 — `predict_proba`와 `decision_function`

```python
model.predict_proba(X_test_scaled[:3]).round(3)
# [[0.993 0.007]      ← 도미 99.3 %
#  [0.996 0.004]
#  [0.046 0.954]]     ← 빙어 95.4 %
model.decision_function(X_test_scaled[:3]).round(2)
# [-4.89 -5.44  3.03]  ← 시그모이드 전의 z
```

`predict_proba`는 1-6의 수업 코드 5)에서 봤고, 여기에 `decision_function`을 더해 본다. `predict`는 결론만 주지만 `predict_proba`는 **클래스별 확률**을 준다. 열 순서는 `classes_`와 같아서 `[도미 확률, 빙어 확률]`이고 두 값의 합은 1이다. `decision_function`은 시그모이드에 넣기 **전의 z** 다 — 첫 행의 z = −4.89를 `1 / (1 + e^4.89)`에 넣으면 0.0074, 즉 빙어 확률 0.7 %가 그대로 나온다. 1-4의 수식을 숫자로 확인하는 가장 빠른 길이다. 확률이 0.5 근처인 표본이 있으면 "모델이 헷갈리는 물고기"이고, 그런 표본이 많을수록 정확도 1.0은 운일 가능성이 높다. 이 자료에서는 가장 애매한 것도 0.95라 걱정이 없다.

### 2-2. 새 물고기 한 마리 — 열 이름 데이터프레임 + 같은 스케일러

```python
new_fish = pd.DataFrame({'Weight': [300], 'Length1': [25], 'Length2': [27],
                         'Length3': [31], 'Height': [12], 'Width': [4.3]})
model.predict(ss.transform(new_fish))          # ['Bream']
model.predict_proba(ss.transform(new_fish))    # [[0.937 0.063]]
```

day13·14와 같은 원칙이다. 새 자료도 **학습 때 `fit`한 그 스케일러**로 `transform`한 뒤에 넣는다. 300 g짜리 물고기는 93.7 % 확률로 도미, 10 g짜리(`Weight` 10·`Length1` 11·…)를 넣으면 96.5 %로 빙어가 나온다. 전처리와 모델이 떨어져 있으면 이 "같은 스케일러" 원칙을 손으로 지켜야 하니, 앞 노트의 `Pipeline([('scaler', StandardScaler()), ('logreg', LogisticRegression())])`으로 묶으면 `pipe.predict(new_fish)` 한 줄로 끝난다.

### 2-3. `C` — 로지스틱 회귀에도 규제가 있다

```python
for C in [0.01, 0.1, 1, 10, 100]:
    m = LogisticRegression(C=C).fit(X_train_scaled, Y_train)
    print(C, m.coef_.round(2), m.score(X_test_scaled, Y_test))
# 0.01  [[-0.10 -0.11 -0.11 -0.11 -0.12 -0.11]]  0.8
# 0.1   [[-0.28 -0.36 -0.36 -0.37 -0.38 -0.36]]  1.0
# 1     [[-0.49 -0.68 -0.69 -0.72 -0.76 -0.71]]  1.0   ← 기본값
# 10    [[-0.71 -1.07 -1.09 -1.15 -1.24 -1.12]]  1.0
# 100   [[-0.63 -1.49 -1.53 -1.70 -1.95 -1.64]]  1.0
```

`LogisticRegression()`은 기본으로 **L2 규제(릿지와 같은 방식)** 를 건다. 강도 인자는 `C`인데 릿지의 `alpha`와 **방향이 반대**다 — `C`가 **작을수록 규제가 세다**(`C ≈ 1/alpha`). 표에서 `C`가 커질수록 기울기가 커지는 것이 보이고, `C=0.01`로 너무 세게 누르면 기울기가 거의 0에 붙어 정확도가 0.8로 떨어진다. day13에서 `alpha`를 고르던 일이 여기서는 `C`를 고르는 일이고, 앞 노트의 `GridSearchCV`에 `'logreg__C': [0.01, 0.1, 1, 10, 100]`으로 넣으면 그대로 돌아간다. 규제가 기본으로 켜져 있기 때문에 표준화(1-3)가 더욱 필요하다.

### 2-4. 분류 지표 — 정확도만으로 부족할 때

```python
from sklearn.metrics import confusion_matrix, classification_report
confusion_matrix(Y_test, Y_pred, labels=['Bream', 'Smelt'])
# [[7 0]
#  [0 3]]      행 = 정답, 열 = 예측
print(classification_report(Y_test, Y_pred))
```

**혼동 행렬**은 "정답이 도미인데 빙어라고 한 것"처럼 틀린 방향을 보여 준다. 여기서는 대각선에만 숫자가 있어 전부 맞았다는 뜻이다. 정확도 하나로 말하기 위험한 경우는 클래스가 불균형할 때다 — 도미 95마리·빙어 5마리라면 무조건 "도미"라고 답해도 정확도 0.95가 나온다. 그래서 분류에는 **정밀도**(빙어라고 한 것 중 진짜 빙어 비율)·**재현율**(진짜 빙어 중 찾아낸 비율)·**F1**(둘의 조화 평균)이 따로 있고, `classification_report`가 클래스별로 한 번에 뽑아 준다. 앞 노트 2-5의 `scoring` 표에서 분류용으로 적어 둔 `'accuracy'`·`'f1'`·`'roc_auc'`가 바로 이 지표들이다.

### 2-5. 일곱 종 전부 — 다중 분류도 같은 클래스로

```python
X = df_all[['Weight', 'Length1', 'Length2', 'Length3', 'Height', 'Width']]
Y = df_all['Species']                                    # 일곱 종 그대로
X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size=0.2, random_state=42, stratify=Y)
ss = StandardScaler().fit(X_train)
model = LogisticRegression(max_iter=1000).fit(ss.transform(X_train), Y_train)
model.score(ss.transform(X_test), Y_test)                # 0.8125  (32마리 중 26)
model.coef_.shape                                         # (7, 6)  클래스마다 기울기 한 줄
model.predict_proba(ss.transform(X_test)[:1]).round(3)   # [[0.959 0.006 0.008 0.001 0.002 0.    0.024]]  합 = 1
```

두 종을 고르는 1-1을 빼면 **코드가 한 줄도 안 바뀐다.** 클래스가 셋 이상이면 사이킷런이 자동으로 **소프트맥스**(시그모이드의 다중 버전 — 일곱 확률의 합이 1)로 바꿔 학습하고, `coef_`는 클래스 수만큼 행이 생긴다. 정확도 0.81인데 혼동 행렬을 보면 틀린 것은 전부 **로치 4마리를 퍼치로**, 퍼치 1마리를 빙어로, 화이트피시 1마리를 퍼치로 — 생김새가 비슷한 종끼리 헷갈린 것이라 납득이 간다. `stratify=Y` 덕분에 화이트피시(전체 6마리)도 테스트에 1마리는 들어간다. 종이 일곱이면 `max_iter` 기본값 100으로는 수렴이 안 되어 경고가 날 수 있어 1000으로 올렸다.

### 2-6. 수렴 경고가 나면

| 상황 | 대처 |
| --- | --- |
| `ConvergenceWarning: lbfgs failed to converge` | 반복 횟수 부족. `max_iter=1000`으로 올리거나, **표준화를 했는지** 먼저 확인 — 이 자료에서 표준화 전엔 35번, 후엔 9번 반복으로 끝난다 |
| 클래스가 많거나 자료가 클 때 | `solver='saga'` 같은 다른 최적화기, 또는 `C`를 줄여 규제를 세게 |
| 완벽히 분리되는 자료 | 기울기가 무한히 커지려 해서 수렴이 느리다 — 규제(`C`)가 이를 막아 주는 것이 기본값이 L2인 이유 |

### 2-7. 두 종 고르기의 다른 쓰기 — `isin`

```python
df = df[df['Species'].isin(['Bream', 'Smelt'])]     # (49, 7)
```

`(a == x) | (a == y)`는 종이 셋·넷으로 늘면 길어진다. `isin(리스트)`가 같은 결과를 한 번에 돌려주고 괄호 실수도 없다. day08 판다스 필터링에서 본 그 메서드다.

## 3. 더 나아가 알면 좋은 것

### 3-1. 왜 선형 회귀로 분류하면 안 되는가

도미를 0, 빙어를 1로 놓고 `LinearRegression`을 돌리면 안 되나 — 된다, 그러나 예측이 −0.3이나 1.4처럼 **확률 범위 밖**으로 나오고, 극단 표본 하나가 직선을 기울여 경계가 흔들린다. 시그모이드는 어떤 z든 0~1로 눌러 담아 이 두 문제를 없앤다. 손실 함수도 바뀐다 — 회귀의 오차 제곱 합 대신 **로그 손실**(크로스 엔트로피, "정답 클래스에 준 확률의 로그"의 음수)을 최소화한다. 최소제곱법처럼 공식 한 번으로 풀리지 않아서 **경사 하강법 계열**(`lbfgs`)로 반복해 찾고, 그래서 `max_iter`와 수렴 경고(2-6)가 존재한다.

### 3-2. 결정 경계 — 분류 모델이 공간을 나누는 선

여섯 특성의 선형 결합 z = 0인 지점이 **결정 경계**이고, 로지스틱 회귀의 경계는 언제나 직선(평면)이다. 도미·빙어처럼 직선 하나로 갈리는 자료에는 충분하지만, 동심원처럼 휘어진 경계가 필요하면 day13의 `PolynomialFeatures`를 앞에 붙이거나(특성을 늘려 직선을 휘게), `KNeighborsClassifier`·`DecisionTreeClassifier`·`SVC(kernel='rbf')`처럼 경계가 곡선인 모델로 간다. day12 3단에서 적어 둔 `KNeighborsClassifier`가 "같은 뼈대의 분류"로 다음 후보다.

### 3-3. 임계값 0.5는 고정이 아니다

`predict`는 p ≥ 0.5를 양성으로 보지만, 암 진단처럼 "놓치면 안 되는" 문제는 0.3으로 내려 재현율을 높이고, 스팸 필터처럼 "오탐이 더 싫은" 문제는 0.7로 올린다. `predict_proba`를 받아 `(p[:, 1] >= 0.3)`으로 직접 자르면 된다. 임계값을 0부터 1까지 훑으며 재현율·오탐률을 그린 것이 **ROC 곡선**이고, 그 아래 면적이 앞 노트의 `'roc_auc'`다.

### 3-4. 다음에 볼 키워드

- 분류 vs 회귀 · 이진 분류/다중 분류 · `stratify=Y`와 `StratifiedKFold` · 클래스 불균형
- `LogisticRegression` · 시그모이드/로지스틱 함수 · `classes_` 알파벳순 · `coef_`/`intercept_` · `predict_proba`/`decision_function` · 소프트맥스
- `C`(= 1/alpha, 작을수록 센 규제) · L2 기본 · `penalty='l1'`+`solver='liblinear'`/`'saga'` · `max_iter`/`ConvergenceWarning`
- 정확도·정밀도·재현율·F1 · `confusion_matrix`/`classification_report` · ROC·AUC · 임계값 조정
- 로그 손실(크로스 엔트로피) · 경사 하강법 · 결정 경계 · `KNeighborsClassifier`/`DecisionTreeClassifier`/`SVC` · `Pipeline(scaler → logreg)` + `GridSearchCV('logreg__C')`

## 실습 파일

- `KDT_2026/2026_Python/day14/s-06.py` — `Fish.csv` 읽기 → `Species`가 `Bream`/`Smelt`인 행만 → `X` 여섯 특성(`Weight`·`Length1~3`·`Height`·`Width`)·`Y = Species` → `train_test_split(test_size=0.2, random_state=42, stratify=Y)`("타깃 무작위 분리 시 클래스 비율 일정 유지" 주석) → `StandardScaler` `fit(X_train)`·`transform` 둘 → `LogisticRegression().fit(X_train_scaled, Y_train)` → `predict(X_test_scaled)` 출력 → 5) `classes_`·`predict_proba(X_test_scaled[:3])`("Bream(0)열, Smelt(1)열" 주석) → 6) `accuracy_score(Y_test, Y_pred)` 1.0("현재 실습은 데이터가 적다" 주석)
- `KDT_2026/2026_Python/day14/Fish.csv` — 캐글 Fish Market, 159마리 × `Species`·`Weight`·`Length1~3`·`Height`·`Width` (도미 35·빙어 14)

## 관련 노트

[[AI 정리본 인덱스]] · [[AI day14 파이프라인·그리드서치·joblib 연습문제 풀이]] · [[AI day14 로지스틱 이진 분류 연습문제 풀이]] · [[AI day14 KFold 교차 검증과 GridSearchCV 하이퍼파라미터 탐색]] · [[AI day14 사이킷런 Pipeline으로 다항·표준화·회귀 묶기]] · [[AI day13 StandardScaler 표준화와 릿지·라쏘 규제]] · [[AI day12 사이킷런 단순 선형 회귀로 물고기 무게 예측]] · [[KDT_2026 학습 지도]]
