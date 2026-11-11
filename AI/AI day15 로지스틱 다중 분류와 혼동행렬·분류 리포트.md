---
출처: Claude 분석
원본: KDT_2026/2026_Python/day15/s-07.py, day15/Fish.csv
작성일: 2026-11-11
tags: [학습, ai, python]
---

# AI day15 — 로지스틱 다중 분류와 혼동행렬·분류 리포트

> 실습 파일: `day15/s-07.py`, `day15/Fish.csv`
> 허브: [[AI 정리본 인덱스]] · 이전: [[AI day14 로지스틱 이진 분류 연습문제 풀이]] · 다음: (아직 없음)

day14에서는 도미·빙어 두 종만 남겨 **이진 분류**를 했다. 이 노트는 그 필터를 걷어내고 `Fish.csv`의 **일곱 종 전부**를 한 번에 맞히는 **다중 분류**다. 코드 뼈대는 한 줄도 바뀌지 않는다 — 읽기 → 특성/타깃 → `stratify` 분리 → 표준화 → `LogisticRegression` → 예측. 바뀌는 것은 결과의 **모양**이다. `predict_proba`가 2열에서 7열이 되고, `coef_`가 `(1, 6)`에서 `(7, 6)`이 되고, 정확도가 1.0에서 **0.81**로 내려온다. 그리고 처음으로 정확도 하나로는 모자라서 **정밀도·혼동행렬·분류 리포트**가 등장한다. day14 노트 2단에서 "일곱 종으로 늘려도 코드는 그대로"라고 미리 적어 두었는데, 이번에는 그 결과를 수업 코드로 직접 확인하고 **틀린 6마리가 어디서 틀렸는지** 읽는 법까지 정리한다.

## 1. 배운 내용

### 1-1. `drop(columns=['Species'])` — 어종을 뺀 나머지 전부가 특성

```python
import pandas as pd
fish = pd.read_csv('./day15/Fish.csv')
X = fish.drop(columns=['Species'])    # 어종 제외한 모든 열 → 6열
Y = fish['Species']                   # 어종 열 (7가지 값)
```

day14에서는 `df[['Weight', 'Length1', …]]`처럼 특성 여섯 개를 **이름으로 나열**했다. 이번에는 반대로 **타깃 하나만 빼고 나머지를 전부** 특성으로 삼는다. 열이 많을 때 나열하는 것보다 실수가 적고, 새 열이 추가되어도 코드를 고칠 필요가 없다. `drop`은 원본을 바꾸지 않고 새 데이터프레임을 돌려주므로 `fish` 자체는 그대로다.

| 항목 | day14 (이진) | 이 노트 (다중) |
| --- | --- | --- |
| 행 | 49마리 (도미 35·빙어 14) | **159마리 전부** |
| 특성 X | 여섯 열을 이름으로 나열 | `drop(columns=['Species'])` 여섯 열 |
| 타깃 Y | `'Bream'` / `'Smelt'` 2가지 | 7가지 — 퍼치 56·도미 35·로치 20·파이크 17·빙어 14·파키 11·화이트피시 **6** |

일곱 종의 머릿수가 고르지 않다는 것이 이 노트의 숨은 주제다. 퍼치는 56마리인데 화이트피시는 6마리뿐이다. 이 **클래스 불균형**이 뒤에서 `stratify`가 왜 필요한지, 정확도가 왜 부족한지를 전부 설명한다.

### 1-2. `train_test_split(…, stratify=Y)` — 일곱 종의 비율을 양쪽에 똑같이

```python
from sklearn.model_selection import train_test_split
X_train, X_test, Y_train, Y_test = train_test_split(
    X, Y, test_size=0.2, random_state=42, stratify=Y
)
```

수업 주석대로 "정답지에 학습용과 테스트용 비율 유지(분류 모델 권장)"다. 127/32로 나뉘고, 테스트 32마리의 구성은 **퍼치 11·도미 7·로치 4·파이크 4·빙어 3·파키 2·화이트피시 1** — 전체 비율(퍼치 35%·도미 22%…)이 그대로 축소되어 들어간다.

`stratify`를 빼고 같은 씨앗으로 나누면 테스트에 **로치 1마리·파키 1마리**만 들어가고 도미는 10마리나 들어간다. 시험지에 어떤 종은 한 마리뿐이면 그 종에 대한 평가는 "하나 맞혔다/틀렸다"가 전부라 아무 말도 할 수 없다. 클래스가 일곱이고 그중 둘은 머릿수가 열 남짓이니, 이진 분류 때보다 `stratify`가 훨씬 절실하다. 이 분리 규칙의 교차 검증판이 `StratifiedKFold`다(day14 KFold 노트).

### 1-3. `StandardScaler` — 학습용에 `fit_transform`, 테스트용은 `transform`만

```python
from sklearn.preprocessing import StandardScaler
ss = StandardScaler()
X_train_scaled = ss.fit_transform(X_train)   # fit + transform 한 번에
X_test_scaled = ss.transform(X_test)         # 학습용 평균·표준편차로만
```

day13부터 이어지는 규칙이고, 이번에는 `fit`과 `transform`을 따로 부르던 두 줄이 **`fit_transform` 한 줄**로 줄었다. 하는 일은 같다 — 학습용 127마리로 열마다 평균·표준편차를 재고(`fit`), 그 값으로 양쪽을 바꾼다. 테스트용에 `fit_transform`을 쓰면 테스트의 평균으로 다시 재버리므로, **`fit_transform`은 학습용에만** 쓴다는 것이 이 한 줄의 함정이다. 무게(수백 g)와 높이(수 cm)가 같은 저울에 오르지 않으면 규제도, 경사 하강법도 큰 열에 끌려간다.

### 1-4. `LogisticRegression(C=1.0, max_iter=1000, random_state=42)` — 이진이면 시그모이드, 다중이면 소프트맥스

```python
from sklearn.linear_model import LogisticRegression
model = LogisticRegression(C=1.0, max_iter=1000, random_state=42)
model.fit(X_train_scaled, Y_train)
```

수업 주석 세 줄이 이 모델의 설정을 전부 설명한다. 정리하면 이렇다.

| 인자 | 수업 주석 | 뜻 |
| --- | --- | --- |
| (자동) | "이진(시그모이드) 또는 다중(소프트맥스)에서 자동 선택" | 타깃 값이 2가지면 시그모이드, 3가지 이상이면 **소프트맥스**. 코드를 바꾸지 않아도 `fit`이 `Y_train`의 고유값 수를 보고 고른다 |
| `C=1.0` | "L2 규제(릿지). 손실(오차) 함수 계산. 기본값 / 하이퍼파라미터" | day13 릿지의 `alpha`와 같은 역할인데 **역수**다. `C`가 작을수록 규제가 세다. 1.0이 기본 |
| `max_iter=1000` | "계산 반복수(경사하강법). 기본값 100 / 권장 1000~3000" | 최적 가중치를 찾는 반복 상한. 모자라면 `ConvergenceWarning` |
| `random_state=42` | — | 재현성. 기본 풀이기(`lbfgs`)에서는 결과에 거의 영향이 없지만 습관으로 둔다 |

**소프트맥스**는 시그모이드의 일곱 클래스 판이다. 클래스마다 z 값(= 여섯 특성의 선형 결합 + 절편)을 하나씩 구한 뒤, `e^z`를 전부 더한 값으로 각각을 나눈다. 그래서 일곱 확률의 합이 정확히 1이 된다. 모델 안에는 **클래스마다 직선 하나씩** 있는 셈이라 `coef_`가 `(7, 6)`, `intercept_`가 길이 7이다.

"경사하강법 : 기울기(가중치)를 변경하면서 최적의 기울기/가중치를 찾는 과정"이라는 주석도 같이 적어 둔다. 선형 회귀는 최소제곱법 공식 한 번으로 끝났지만 로지스틱 회귀의 로그 손실은 그런 공식이 없어서, 손실이 줄어드는 방향으로 가중치를 조금씩 옮기는 일을 **반복**한다. `max_iter`는 그 반복 횟수의 상한이다. 표준화한 이 자료는 **38회**에 수렴했다 — 표준화 없이 `max_iter=100`으로 돌리면 100회를 다 쓰고도 경고가 난다. `max_iter`를 1000으로 넉넉히 두는 수업 설정은 그래서다.

### 1-5. `predict`·`predict_proba`·`classes_` — 7열짜리 확률표 읽기

```python
Y_pred = model.predict(X_test_scaled)
print(Y_pred[:3])                               # ['Bream' 'Perch' 'Smelt']
Y_pred_proba = model.predict_proba(X_test_scaled)
import numpy as np
print(np.round(Y_pred_proba[:3], 3))            # np.round(배열, 자릿수)
print(model.classes_)
# ['Bream' 'Parkki' 'Perch' 'Pike' 'Roach' 'Smelt' 'Whitefish']
```

실행 결과(위 세 줄을 그대로 실행한 값)는 이렇다.

| 테스트 행 | Bream | Parkki | Perch | Pike | Roach | Smelt | Whitefish | `predict` | 실제 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 0 | **0.959** | 0.006 | 0.008 | 0.001 | 0.002 | 0.000 | 0.024 | Bream | Bream |
| 1 | 0.027 | 0.065 | **0.559** | 0.016 | 0.282 | 0.004 | 0.046 | Perch | **Roach** |
| 2 | 0.000 | 0.046 | 0.137 | 0.001 | 0.077 | **0.737** | 0.002 | Smelt | Smelt |

읽는 법은 세 가지다.

- **열 순서는 `classes_`**다. 알파벳순 `['Bream' 'Parkki' 'Perch' 'Pike' 'Roach' 'Smelt' 'Whitefish']` — 자료에 나온 순서(도미가 먼저)가 아니다. 7열짜리 확률표는 `classes_`와 나란히 놓고 봐야 어느 열이 어느 종인지 안다.
- **`predict`는 가장 큰 열의 이름**이다. 이진 분류의 "0.5 기준"은 다중에서는 "최댓값 기준"(argmax)으로 바뀐다. 행 1은 0.559로 퍼치가 1등이라 퍼치로 찍었다.
- **확률이 낮은 행이 틀린다.** 행 0·2는 1등이 0.96·0.74로 확실한데, 행 1은 1등 퍼치 0.559·2등 로치 0.282로 둘이 갈렸고 실제 정답은 2등이던 **로치**였다. 틀린 예측은 틀리기 전에 확률표에서 먼저 티가 난다.

`np.round(배열, 3)`은 확률표를 읽기 좋게 소수 셋째 자리로 자르는 넘파이 함수다. 자르지 않으면 `9.59e-01` 같은 지수 표기가 섞여 눈으로 비교하기 어렵다.

### 1-6. 평가지표 ① `accuracy_score` — 32마리 중 26마리

```python
from sklearn.metrics import accuracy_score, precision_score
print(accuracy_score(Y_test, Y_pred))   # 0.8125
```

정확도 = 맞힌 수 / 전체 수 = **26 / 32 = 0.8125**. day14 이진 분류의 1.0에서 크게 내려왔다. 두 종을 가를 때는 도미(600 g대)와 빙어(10 g대)가 너무 달라 직선 하나로 충분했지만, 일곱 종 가운데 퍼치·로치·화이트피시는 생김새가 비슷한 중형 민물고기라 여섯 치수만으로는 갈리지 않는다. 학습 정확도도 0.819라 과대적합은 아니다 — 모델이 외운 게 아니라 **원래 어려운 문제**다.

### 1-7. 평가지표 ② `precision_score(average='macro')` — 정확도가 숨기는 것

```python
print(precision_score(Y_test, Y_pred, average='macro'))   # 0.631
```

정밀도는 "**퍼치라고 찍은 것 중 진짜 퍼치**"의 비율이다. 이진 분류에서는 숫자 하나지만 다중 분류에서는 **종마다 하나씩** 일곱 개가 나오므로, 하나로 합치는 방법을 `average`로 정해야 한다.

| `average=` | 계산 | 이 자료 | 언제 |
| --- | --- | --- | --- |
| `'macro'` | 일곱 종의 정밀도를 **단순 평균** | **0.631** | 소수 클래스도 한 표로 — 불균형 자료에서 작은 종을 홀대하지 않으려면 |
| `'weighted'` | 종별 정밀도를 **머릿수로 가중** 평균 | 0.706 | 많은 종이 결과를 좌우해도 되면 |
| `'micro'` | 전체 TP / 전체 예측 | 0.8125 (= 정확도) | 다중 분류에서 마이크로 정밀도는 정확도와 같다 |
| `None` | 종별 일곱 개 배열 그대로 | `[1, 1, 0.67, 1, 0, 0.75, 0]` | 어느 종이 문제인지 볼 때 |

정확도 0.81과 매크로 정밀도 0.63의 **차이 0.18**이 핵심이다. 정확도는 "퍼치 11마리 중 10마리 맞힘"처럼 **많은 종의 성적**에 묻혀 높게 나오고, 매크로 정밀도는 로치·화이트피시의 **0점**을 똑같은 비중으로 셈해 낮아진다. 수업 코드가 정확도 다음에 굳이 매크로 정밀도를 찍는 이유가 이것이다 — 클래스가 불균형하면 정확도만으로는 작은 종이 전멸해도 모른다.

실행하면 `UndefinedMetricWarning`도 같이 뜬다. 로치와 화이트피시는 모델이 **한 번도 그 종으로 찍지 않아서** 정밀도의 분모(그 종으로 찍은 수)가 0이기 때문이다. 사이킷런은 0으로 나눌 수 없으니 0점을 주고 경고한다. `precision_score(…, zero_division=0)`으로 경고를 끄거나, 리포트에서 해당 종의 `support`를 확인하면 된다.

### 1-8. `ConfusionMatrixDisplay.from_predictions` — 틀린 6마리가 어디로 갔나

```python
import matplotlib.pyplot as plt
from sklearn.metrics import ConfusionMatrixDisplay, classification_report
ConfusionMatrixDisplay.from_predictions(Y_test, Y_pred)
plt.show()
```

혼동행렬은 **행 = 실제 종, 열 = 예측 종**인 7×7 표다. 대각선이 맞힌 수, 대각선 밖이 틀린 수다. `from_predictions`에 정답과 예측을 넘기면 행렬 계산과 색칠한 그림을 한 번에 해 준다(축 순서는 `classes_` 알파벳순). 이 테스트 세트의 숫자를 옮기면 이렇다.

| 실제 \ 예측 | Bream | Parkki | Perch | Pike | Roach | Smelt | Whitefish |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Bream (7) | **7** | | | | | | |
| Parkki (2) | | **2** | | | | | |
| Perch (11) | | | **10** | | | 1 | |
| Pike (4) | | | | **4** | | | |
| Roach (4) | | | **4** | | 0 | | |
| Smelt (3) | | | | | | **3** | |
| Whitefish (1) | | | **1** | | | | 0 |

대각선 합이 26, 그 밖이 6이다. 그리고 틀린 6마리 중 **5마리가 "퍼치" 열**에 모여 있다 — 로치 4마리 전부와 화이트피시 1마리를 퍼치로 찍었다. 나머지 1마리는 퍼치를 빙어로 찍은 것이다. 정확도는 "6마리 틀렸다"까지만 말하지만 혼동행렬은 "**로치를 퍼치와 구분하지 못한다**"고 말해 준다. 로치(평균 150 g)와 퍼치(수십~1,000 g 넓게 분포)는 치수가 겹치는 구간이 넓어, 여섯 치수의 직선 경계로는 로치를 떼어낼 자리가 없다. 다음에 무엇을 고쳐야 하는지(로치 표본 추가, 비선형 모델, 다른 특성)는 정확도가 아니라 이 표가 알려 준다.

### 1-9. `classification_report` — 종별 정밀도·재현율·F1·support 한 장

```python
print(classification_report(Y_test, Y_pred))
```

```
              precision    recall  f1-score   support
       Bream       1.00      1.00      1.00         7
      Parkki       1.00      1.00      1.00         2
       Perch       0.67      0.91      0.77        11
        Pike       1.00      1.00      1.00         4
       Roach       0.00      0.00      0.00         4
       Smelt       0.75      1.00      0.86         3
   Whitefish       0.00      0.00      0.00         1
    accuracy                           0.81        32
   macro avg       0.63      0.70      0.66        32
weighted avg       0.71      0.81      0.75        32
```

수업 주석의 "평가 지도 보고서"다. 혼동행렬의 숫자를 종별 지표로 환산해 준다. 네 열의 뜻을 퍼치 행으로 정리하면 이렇다.

| 열 | 뜻 | 퍼치 행 계산 |
| --- | --- | --- |
| precision | 퍼치라고 찍은 것 중 진짜 퍼치 | 10 / (10 + 로치 4 + 화이트피시 1) = 10/15 = **0.67** |
| recall | 진짜 퍼치 중 퍼치로 찍은 것 | 10 / 11 = **0.91** |
| f1-score | 정밀도·재현율의 조화 평균 | 2 × 0.67 × 0.91 / (0.67 + 0.91) = **0.77** |
| support | 테스트에 있는 진짜 퍼치 수 | **11** |

퍼치는 재현율이 높고 정밀도가 낮다 — 진짜 퍼치는 거의 다 잡지만, **남의 것까지 퍼치로 끌어온다**. 반대로 빙어는 정밀도 0.75(퍼치 한 마리를 빙어로 잘못 끌어옴)에 재현율 1.0이다. 혼동행렬에서 "퍼치 열에 몰렸다"고 읽은 것이 리포트에서는 "퍼치 정밀도 0.67·로치 재현율 0"으로 나타난다. 같은 사실의 두 표현이다.

아래 세 줄은 요약이다. `accuracy`는 1-6의 0.81, `macro avg`의 precision 0.63은 1-7의 `average='macro'` 값과 정확히 같고, `weighted avg`는 머릿수 가중이다. **support가 1~4인 종**(화이트피시·파키·빙어·로치·파이크)의 지표는 표본 한두 마리에 좌우되므로 1.00이든 0.00이든 크게 믿지 않는 편이 안전하다. 테스트 32마리는 일곱 종을 평가하기에 작다.

### 1-10. 흐름 한 장 — day14와 무엇이 같고 무엇이 다른가

```
Fish.csv 159마리 (7종)
  → X = drop('Species') 6열 · Y = Species          ← 종 필터 없음
  → train_test_split(stratify=Y) 127/32           ← 7종 비율 유지
  → StandardScaler fit_transform(학습) · transform(테스트)
  → LogisticRegression(C=1.0, max_iter=1000)       ← 7클래스 → 소프트맥스 자동
  → predict (argmax) · predict_proba (7열, 합 1) · classes_ (알파벳순 7개)
  → accuracy 0.81 · precision(macro) 0.63          ← 둘의 차이 = 불균형의 신호
  → ConfusionMatrixDisplay (7×7) · classification_report (종별 4열 + 요약 3줄)
```

| | day14 이진 | day15 다중 |
| --- | --- | --- |
| 확률 함수 | 시그모이드 | 소프트맥스 (자동 전환) |
| `predict` 기준 | p ≥ 0.5 | 가장 큰 확률 (argmax) |
| `predict_proba` | `(n, 2)` | `(n, 7)` |
| `coef_` | `(1, 6)` | `(7, 6)` — 종마다 직선 하나 |
| 정확도 | 1.0 | 0.8125 |
| 추가 지표 | (없음) | 매크로 정밀도·혼동행렬·분류 리포트 |

## 2. 추가로 알면 좋은 활용법

### 2-1. 소프트맥스 손계산 — `decision_function`으로 확인

```python
z = model.decision_function(X_test_scaled[:1])[0]   # 7개의 z
# [ 6.10  0.95  1.36 -0.53 -0.10 -10.18  2.41 ]
p = np.exp(z) / np.exp(z).sum()
print(np.round(p, 3))   # [0.959 0.006 0.008 0.001 0.002 0.    0.024]  ← predict_proba 행 0과 동일
```

`decision_function`은 소프트맥스를 거치기 **전**의 z 값 일곱 개를 준다. `e^z`를 전부 더한 것으로 나누면 `predict_proba` 첫 행과 소수 셋째 자리까지 같다. 도미의 z가 6.1로 압도적이고 빙어가 −10.2로 바닥이라, 첫 테스트 물고기는 "도미 확실·빙어 절대 아님"이다. day14에서 시그모이드를 손으로 계산해 본 것의 다중 판이다.

### 2-2. 혼동행렬을 숫자로 — `confusion_matrix(labels=model.classes_)`

```python
from sklearn.metrics import confusion_matrix
cm = confusion_matrix(Y_test, Y_pred, labels=model.classes_)
print(cm)               # 1-8의 7×7 배열
print(cm.diagonal().sum() / cm.sum())   # 0.8125 — 정확도와 같다
```

그림 대신 배열로 받으면 "틀린 것만 모으기", "어느 쌍이 가장 많이 헷갈리나" 같은 계산을 할 수 있다. `labels=`로 축 순서를 명시해 두면 그림·리포트·`classes_`가 전부 같은 순서로 맞는다. `ConfusionMatrixDisplay.from_predictions(…, normalize='true')`를 주면 행마다 비율로 바꿔 보여 주어, 머릿수가 다른 종끼리 비교하기 좋다.

### 2-3. `C`를 바꿔 보기 — 이 자료에서는 규제를 **풀수록** 올라간다

| `C` | 학습 정확도 | 테스트 정확도 |
| --- | --- | --- |
| 0.01 | 0.48 | 0.50 |
| 0.1 | 0.73 | 0.72 |
| **1.0 (기본)** | **0.82** | **0.81** |
| 10 | 0.91 | 0.91 |
| 100 | 0.98 | 0.97 |

day13 릿지에서는 `alpha`를 **키워서**(규제를 세게) 과대적합을 잡았지만, 이 자료는 반대다. 특성 6개에 표본 127개라 과대적합할 여지가 적고, 오히려 기본 `C=1.0`의 규제가 **직선을 너무 눌러서** 로치·퍼치 경계를 못 그리고 있었다. `C=100`이면 테스트 0.97이고 학습과의 격차도 작다. 규제의 방향은 자료마다 다르므로 **기본값을 믿지 말고 훑어보는 것**이 안전하고, 훑는 도구가 day14의 `GridSearchCV(param_grid={'logreg__C': [0.01, …, 100]})`다. 다만 훑을 때는 아래 2-4처럼 교차 검증으로 해야 32마리짜리 테스트에 맞춰 버리는 일을 피한다.

### 2-4. `StratifiedKFold` + `Pipeline` 교차 검증 — 32마리 시험지의 운 걷어내기

```python
from sklearn.pipeline import Pipeline
from sklearn.model_selection import StratifiedKFold, cross_val_score
pipe = Pipeline([('scaler', StandardScaler()),
                 ('logreg', LogisticRegression(max_iter=1000, random_state=42))])
skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
scores = cross_val_score(pipe, X, Y, cv=skf)
print(np.round(scores, 3), scores.mean())   # [0.812 0.875 0.812 0.781 0.806] → 0.818
```

다섯 겹 평균 0.818 — 수업의 0.8125와 거의 같아서 "이 설정은 대략 0.8 정도의 모델"이라고 말할 수 있다. `stratify=Y`의 교차 검증판이 `StratifiedKFold`이고, 스케일러를 파이프라인에 넣어야 폴드마다 학습 쪽으로만 `fit`된다(day14 Pipeline 노트). `cross_val_score(…, scoring='f1_macro')`로 바꾸면 매크로 F1로 평가할 수 있다.

### 2-5. 리포트를 표로 — `output_dict=True`

```python
rep = classification_report(Y_test, Y_pred, output_dict=True, zero_division=0)
pd.DataFrame(rep).T.round(2)
```

문자열 리포트는 눈으로 읽기엔 좋지만 정렬·저장이 안 된다. `output_dict=True`로 딕셔너리를 받아 데이터프레임으로 바꾸면 `sort_values('f1-score')`로 약한 종부터 줄 세우거나 CSV로 남길 수 있다. `zero_division=0`은 1-7의 경고를 명시적으로 끈다.

### 2-6. `np.round`·`set_printoptions` — 확률표 보기 좋게

`np.round(arr, 3)`은 새 배열을 돌려주고 원본은 두지만, 매번 감싸기 번거로우면 `np.set_printoptions(precision=3, suppress=True)`를 한 번 두면 이후 모든 출력이 소수 셋째 자리·지수 표기 없음으로 찍힌다. 확률표를 `pd.DataFrame(Y_pred_proba, columns=model.classes_).round(3)`으로 만들면 열 이름이 종 이름으로 붙어 `classes_`와 대조할 필요가 없어진다.

### 2-7. 클래스 불균형 다루기 — `class_weight='balanced'`

```python
model = LogisticRegression(C=1.0, max_iter=1000, class_weight='balanced')
```

로치·화이트피시가 전멸한 이유 중 하나는 손실 계산에서 56마리 퍼치가 6마리 화이트피시보다 **아홉 배 더 큰 목소리**를 내기 때문이다. `class_weight='balanced'`는 종마다 머릿수에 반비례하는 가중치를 주어 작은 종의 오답을 더 비싸게 만든다. 매크로 정밀도·재현율은 보통 오르고 정확도는 조금 내려간다 — 어느 쪽을 택할지는 "어느 실수가 더 비싼가"가 정한다.

## 3. 더 나아가 알면 좋은 것

### 3-1. 소프트맥스 회귀 vs One-vs-Rest

사이킷런의 `LogisticRegression`은 다중 클래스를 기본적으로 **다항(multinomial) 소프트맥스** 하나로 푼다 — 일곱 z를 한 손실 함수로 동시에 학습한다. 다른 방식은 **One-vs-Rest**(`OneVsRestClassifier`)로, "도미 vs 나머지", "파키 vs 나머지"… 이진 분류기 일곱 개를 따로 만들고 가장 자신 있는 것을 고른다. 결과는 비슷하지만 OvR은 확률 합이 1이 아니고, 클래스 수가 늘면 모델이 그만큼 늘어난다. SVM처럼 원래 이진인 알고리즘을 다중에 쓸 때는 OvR이 기본 전략이다.

### 3-2. 로치·퍼치 경계는 직선으로 안 그려진다 — 비선형 분류기

혼동행렬이 가리킨 "로치 → 퍼치" 문제는 로지스틱 회귀의 **결정 경계가 평면**이라는 한계다. 같은 뼈대에 클래스 이름만 바꾸면 되는 후보가 `KNeighborsClassifier`(가까운 k마리의 다수결), `DecisionTreeClassifier`/`RandomForestClassifier`(치수 범위로 쪼개는 규칙), `SVC(kernel='rbf')`(휘어진 경계)다. 트리 계열은 표준화가 필요 없고 `feature_importances_`로 어느 치수가 종을 가르는지 보여 준다. day12 3단부터 적어 둔 k-NN이 이제 바로 다음 순서다.

### 3-3. 다중 분류의 다른 지표 — 로그 손실·ROC-AUC(OvR)·Cohen's κ

정확도·정밀도·재현율·F1은 **예측 라벨**만 보고, 확률표는 버린다. `log_loss(Y_test, Y_pred_proba)`는 "정답 종에 몇 %를 줬나"를 평가해 1-5의 행 1처럼 **틀렸더라도 2등에 0.28을 준 것**과 0.01을 준 것을 구분한다. `roc_auc_score(…, multi_class='ovr')`는 종마다 ROC-AUC를 내 평균하고, `cohen_kappa_score`는 "찍어도 맞는 만큼"을 뺀 일치도라 불균형 자료에서 정확도보다 정직하다. 지표를 하나로 고를 때는 "이 문제에서 어떤 실수가 비싼가"가 기준이다.

### 3-4. 다음에 볼 키워드

- 다중 분류 · 소프트맥스 / 다항 로지스틱 · `decision_function` z 7개 · argmax · One-vs-Rest / `OneVsRestClassifier`
- 클래스 불균형 · `stratify` / `StratifiedKFold` · `class_weight='balanced'` · 오버샘플링(SMOTE) / 언더샘플링
- `precision_score(average='macro'|'weighted'|'micro'|None)` · `recall_score` · `f1_score` · `zero_division` · `UndefinedMetricWarning`
- `confusion_matrix(labels=)` · `ConfusionMatrixDisplay(normalize='true')` · `classification_report(output_dict=True)` · support
- `C` 훑기(규제 방향은 자료마다) · `GridSearchCV('logreg__C')` + `StratifiedKFold` · `scoring='f1_macro'`
- `log_loss` · `roc_auc_score(multi_class='ovr')` · `cohen_kappa_score` · `KNeighborsClassifier` / `DecisionTreeClassifier` / `RandomForestClassifier` / `SVC`

## 실습 파일

- `KDT_2026/2026_Python/day15/s-07.py` — `Fish.csv` 읽기 → 1) `X = fish.drop(columns=['Species'])`·`Y = fish['Species']`("다중 분류 실습을 위한 특성/타깃(여러 어종) 구분") → 2) `train_test_split(test_size=0.2, random_state=42, stratify=Y)`("정답지에 학습용과 테스트용 비율 유지(분류 모델 권장)") → 3) `StandardScaler` `fit_transform(X_train)`·`transform(X_test)` → 4) `LogisticRegression(C=1.0, max_iter=1000, random_state=42)`("이진(시그모이드) 또는 다중(소프트맥스)에서 자동 선택"·"L2 규제(릿지), C=1.0 기본값/하이퍼파라미터"·"계산 반복수(경사하강법) 기본 100/권장 1000~3000"·"경사하강법 = 기울기(가중치)를 변경하면서 최적의 기울기/가중치 찾는 과정") → `predict[:3]` `['Bream' 'Perch' 'Smelt']` → `np.round(predict_proba[:3], 3)` → `classes_` 7종 알파벳순 → 평가지표 1) `accuracy_score` 0.8125("전체 예측 건수 중 맞힌 정답표") 2) `precision_score(average='macro')` → `ConfusionMatrixDisplay.from_predictions(Y_test, Y_pred)`·`plt.show()`("혼동행렬 시각화") → `classification_report`("리포트(평가 지도 보고서)")
- `KDT_2026/2026_Python/day15/Fish.csv` — 캐글 Fish Market, 159마리 × `Species`·`Weight`·`Length1~3`·`Height`·`Width` (퍼치 56·도미 35·로치 20·파이크 17·빙어 14·파키 11·화이트피시 6), day12~14의 같은 파일

## 관련 노트

[[AI 정리본 인덱스]] · [[AI day14 로지스틱 이진 분류 연습문제 풀이]] · [[AI day14 로지스틱 회귀로 도미·빙어 분류]] · [[AI day14 KFold 교차 검증과 GridSearchCV 하이퍼파라미터 탐색]] · [[AI day14 사이킷런 Pipeline으로 다항·표준화·회귀 묶기]] · [[AI day13 StandardScaler 표준화와 릿지·라쏘 규제]] · [[KDT_2026 학습 지도]]
