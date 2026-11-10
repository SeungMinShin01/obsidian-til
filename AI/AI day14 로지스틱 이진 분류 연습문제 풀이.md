---
출처: Claude 분석
원본: KDT_2026/2026_Python/ML_pracitce/practice4.py
작성일: 2026-11-10
tags: [학습, ai, python]
---

# AI day14 — 로지스틱 이진 분류 연습문제 풀이

> 실습 파일: `ML_pracitce/practice4.py`
> 허브: [[AI 정리본 인덱스]] · 이전: [[AI day14 로지스틱 회귀로 도미·빙어 분류]] · 다음: (아직 없음)

수업 `s-06.py`의 흐름 — 두 클래스만 남기기 → `stratify` 분할 → 표준화 → `LogisticRegression` → `predict`·`predict_proba`·`accuracy_score` — 를 **다른 자료에 옮기는** 연습이다. 재료는 캐글의 위스콘신 유방암 진단 데이터(569건 × 세포핵 측정값 30열, 진단 `M` 악성/`B` 양성)다. 도미·빙어는 특성 6개에 49마리였는데 여기는 특성 30개에 569건이고, 타깃을 문자열 그대로 두지 않고 **악성 1·양성 0 숫자로 바꾸는** 단계가 추가된다. 연습 파일에는 단계 1~6 지시문과 단계 1의 힌트 코드만 있고, 데이터 파일 `data.csv`도 아직 폴더에 없다. 그래서 풀이 코드를 여기에 적고, 실행 결과는 사이킷런에 내장된 같은 자료(`load_breast_cancer`, 569건·30열이 캐글 CSV와 동일)로 확인했다 — 열 이름 표기(`radius_mean` vs `mean radius`)만 다르고 값은 같다. 결론은 테스트 114건 중 110건 정답, 정확도 **0.965**. 도미·빙어의 1.0과 달리 이번엔 틀리는 표본이 생겨, 정확도 뒤의 혼동 행렬을 읽을 이유가 처음 생긴다.

## 1. 배운 내용

### 1-1. 단계 1 — 식별자·빈 열 제거와 타깃 숫자화

```python
import pandas as pd
df = pd.read_csv('./data.csv')              # (569, 33)
df = df.drop(columns=['id'])                # 식별자 제거
df = df.dropna(axis=1, how='all')           # 전부 NaN인 열(Unnamed: 32) 제거 → (569, 31)

Y = df['diagnosis'].map({'M': 1, 'B': 0})   # 악성 1 · 양성 0
X = df.drop(columns=['diagnosis'])          # (569, 30)
Y.value_counts()                            # 0: 357, 1: 212
```

세 가지가 새롭다. 첫째, **`id`는 특성이 아니다** — 환자 번호는 진단과 아무 관계가 없는데 숫자라서 그냥 두면 모델이 그 값으로도 선을 그으려 한다. 둘째, 캐글 CSV는 행 끝에 쉼표가 하나 더 붙어 있어 `Unnamed: 32`라는 **전부 결측인 열**이 생긴다. `dropna(axis=1, how='all')`은 "열 방향으로, 모든 값이 NaN인 열만" 지우라는 뜻이라 열 이름을 몰라도 안전하게 치운다(`how='any'`였다면 결측이 하나라도 있는 열을 다 지워 버린다). 셋째, `map({'M': 1, 'B': 0})`으로 타깃을 **0/1 숫자**로 바꾼다. 수업에서는 `'Bream'`/`'Smelt'` 문자열을 그대로 넣었고 사이킷런이 알파벳순으로 번호를 매겼는데, 지시문대로 직접 매핑하면 "1 = 악성"을 **내가 정한다**. 어느 쪽이 양성(positive)인지가 뒤의 확률 열 순서와 정밀도·재현율의 의미를 결정하므로, 의료처럼 "찾아야 할 쪽"이 분명한 문제에서는 직접 정하는 편이 안전하다. 특성 30열은 세포핵 10가지 측정값(반지름·질감·둘레·면적·매끄러움·조밀도·오목함·오목점·대칭·프랙탈 차원) × 3(평균 `_mean`·표준오차 `_se`·최악값 `_worst`)이다.

### 1-2. 단계 2 — `stratify=Y`로 8:2 분할

```python
from sklearn.model_selection import train_test_split
X_train, X_test, Y_train, Y_test = train_test_split(
    X, Y, test_size=0.2, random_state=42, stratify=Y)
# 학습 455 (양성 285 · 악성 170) / 테스트 114 (양성 72 · 악성 42)
```

양성 357 : 악성 212 ≈ 63 : 37이고, `stratify=Y` 덕분에 학습·테스트 양쪽이 같은 비율이다. 수업에서는 빙어 14마리가 테스트에 0~1마리만 들어갈 위험 때문에 붙였는데, 여기서는 악성이 37 %라 그 위험은 작다. 그래도 붙인다 — 비율이 같아야 테스트 정확도가 학습 때 본 분포에서 나온 점수가 되고, 폴드나 씨앗을 바꿔도 비교가 공정해진다. 분류 자료에는 습관처럼 붙이는 인자다.

### 1-3. 단계 3 — `StandardScaler`, 30열이면 더 필요하다

```python
from sklearn.preprocessing import StandardScaler
ss = StandardScaler()
ss.fit(X_train)
X_train_scaled = ss.transform(X_train)
X_test_scaled  = ss.transform(X_test)
```

코드는 수업과 같지만 이유가 더 절실하다. 30열의 단위가 제각각이다 — `radius_mean`은 7~28, `area_worst`는 185~4,254, `smoothness_mean`은 0.05~0.16. 표준화 없이 넣으면 면적 열 하나가 다른 열들을 덮어 버리고, 로지스틱 회귀의 경사 하강이 수렴하지 못해 `ConvergenceWarning`이 난다. 실제로 표준화를 빼면 기본 `max_iter=100`에서 경고가 나고, `max_iter=10000`까지 늘려야 3,000번 넘게 돌아 겨우 끝나며 정확도도 0.94로 떨어진다. 표준화하면 **20번 만에** 수렴하고 0.965다. `fit`은 학습 세트에만, `transform`은 둘 다 — 이 원칙은 열이 30개여도 같다.

### 1-4. 단계 4·5 — 학습과 `accuracy_score`

```python
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score

model = LogisticRegression()
model.fit(X_train_scaled, Y_train)
Y_pred = model.predict(X_test_scaled)
print(accuracy_score(Y_test, Y_pred))        # 0.9649  (110 / 114)
print(model.score(X_train_scaled, Y_train))  # 0.9868
```

`accuracy_score(정답, 예측)`은 `model.score(X, Y)`와 같은 값(맞힌 수 ÷ 전체)인데, 인자가 **정답과 예측 배열**이라 모델 없이도 계산할 수 있다 — `Y_pred`를 파일에서 읽어 와도 되고, 임계값을 바꿔 만든 예측에도 쓸 수 있다. 수업 코드 6)에서 처음 쓴 함수이고, 회귀의 `r2_score(Y_test, Y_pred)`와 똑같은 자리·똑같은 인자 순서다. 학습 0.987 / 테스트 0.965 — 도미·빙어처럼 1.0이 아니라 **4건을 틀렸다**. 어디서 틀렸는지는 1-6에서 본다.

### 1-5. 단계 6 — 앞 세 건의 클래스와 확률

```python
print(model.classes_)                           # [0 1]
print(Y_pred[:3], Y_test.values[:3])            # [0 1 0]  [0 1 0]
print(model.predict_proba(X_test_scaled[:3]))
# [[0.9996 0.0004]      ← 양성 99.96 %
#  [0.0000 1.0000]      ← 악성 100 %
#  [0.9574 0.0426]]     ← 양성 95.7 %
```

`classes_`가 `[0 1]`이니 `predict_proba`의 열은 `[양성(0) 확률, 악성(1) 확률]`이고, 1-1에서 1 = 악성으로 정했기 때문에 **둘째 열이 "악성일 확률"** 이다. 수업에서는 `['Bream' 'Smelt']` 알파벳순이라 둘째 열이 빙어였는데, 매핑을 직접 했으니 열의 의미를 외울 필요 없이 내가 정한 대로다. 세 건 모두 확률이 0.95 이상으로 쏠려 있어 모델이 확신하는 표본들이다. 틀린 4건은 이 셋 중에 없다 — 0.5 근처의 애매한 확률을 가진 표본이 어딘가에 있고, 그것이 틀린 쪽이다.

### 1-6. 정확도 뒤 — 틀린 4건의 방향

```python
from sklearn.metrics import confusion_matrix, classification_report
confusion_matrix(Y_test, Y_pred)
# [[71  1]      행 = 정답(양성 0 · 악성 1), 열 = 예측
#  [ 3 39]]
print(classification_report(Y_test, Y_pred, target_names=['B(0)', 'M(1)']))
#               precision  recall  f1-score  support
#        B(0)        0.96    0.99      0.97       72
#        M(1)        0.97    0.93      0.95       42
```

지시문에는 없지만 정확도 0.965의 내용을 읽어 본다. 양성 72건 중 1건을 악성이라 했고(거짓 양성), **악성 42건 중 3건을 양성이라 했다**(거짓 음성). 의료 분류에서 둘의 무게는 다르다 — 거짓 양성은 추가 검사로 끝나지만 거짓 음성은 악성을 놓치는 것이다. 악성의 **재현율** 0.93(42건 중 39건 찾음)이 이 모델의 약점이고, 정확도 0.965라는 한 숫자에는 그 사실이 묻혀 있다. 수업 노트 2-4에서 "불균형이면 정확도만으론 부족하다"고 적었는데, 비율이 63:37로 크게 불균형하지 않아도 **틀림의 비용이 비대칭**이면 같은 이유로 혼동 행렬을 봐야 한다.

### 1-7. 이 날의 흐름 한 장 — 수업 ↔ 연습

```text
[s-06.py 도미·빙어]                          [practice4 유방암 진단]
Fish.csv 159 → 두 종만 49                    data.csv 569 → id·빈 열 제거
Y = Species 문자열 ('Bream'/'Smelt')         Y = diagnosis.map({M:1, B:0})  ← 숫자화
X 6열                                        X 30열 (10측정 × mean·se·worst)
train_test_split(stratify=Y)   39/10         train_test_split(stratify=Y)   455/114
StandardScaler fit(학습) → transform ×2       동일 (30열이라 더 필수 — 수렴 20회 vs 3,000회+)
LogisticRegression.fit → predict             동일
classes_ ['Bream' 'Smelt'] (알파벳순)        classes_ [0 1] (내가 정한 순서)
predict_proba 열 = [도미, 빙어]               predict_proba 열 = [양성, 악성]
accuracy_score 1.0 (10/10)                   accuracy_score 0.965 (110/114) → 혼동 행렬
```

## 2. 추가로 알면 좋은 활용법

### 2-1. 어떤 특성이 악성 쪽으로 미는가 — `coef_` 읽기

```python
coef = pd.Series(model.coef_[0], index=X.columns).sort_values()
coef.tail(3)   # worst texture 1.43 · radius error 1.23 · worst symmetry 1.06  (+ → 악성)
coef.head(3)   # compactness error −0.91 · fractal dimension error −0.59 …    (− → 양성)
```

표준화한 뒤라 기울기 크기를 서로 비교할 수 있다(수업 노트 1-4의 `coef_`는 6개였고 여기는 30개). 양수 기울기는 값이 클수록 악성 확률을 올리고 음수는 내린다. 질감·반지름 오차·대칭의 최악값이 크면 악성 쪽 — 세포핵이 크고 불규칙할수록 악성이라는 의학적 직관과 맞는다. 다만 30개 특성 중 `radius`·`perimeter`·`area`는 거의 같은 정보라(다중공선성) 개별 기울기의 부호가 뒤섞일 수 있어, 기울기 하나하나를 "원인"으로 읽지는 않는다.

### 2-2. 임계값 내리기 — 악성을 놓치지 않으려면

```python
proba_m = model.predict_proba(X_test_scaled)[:, 1]
Y_pred_03 = (proba_m >= 0.3).astype(int)       # 0.5 대신 0.3
confusion_matrix(Y_test, Y_pred_03)
# [[71  1]
#  [ 1 41]]     ← 거짓 음성 3 → 1, 거짓 양성은 그대로 1
```

`predict`는 악성 확률 0.5를 기준으로 자른다. 거짓 음성 3건이 아깝다면 기준을 0.3으로 내려 "조금이라도 의심되면 악성"으로 분류한다 — 이 자료에서는 놓친 악성이 3건에서 1건으로 줄고 거짓 양성은 늘지 않아 정확도도 0.982로 오른다. 보통은 재현율이 오르는 대신 거짓 양성이 느는 맞바꿈이 생기니, 운 좋은 경우라고 보는 편이 맞다. `accuracy_score`가 모델 없이 정답·예측 배열만으로 계산되는 함수라서 이렇게 **임계값을 바꾼 예측에도 그대로** 쓸 수 있다(1-4). 수업 노트 3-3의 "임계값 0.5는 고정이 아니다"를 실제로 돌려 보는 자리다. 어느 임계값이 좋은지는 `roc_curve`·`precision_recall_curve`로 한 번에 훑는다.

### 2-3. 층화 교차 검증으로 0.965를 다시 보기

```python
from sklearn.model_selection import StratifiedKFold, cross_val_score
from sklearn.pipeline import Pipeline
pipe = Pipeline([('scaler', StandardScaler()), ('logreg', LogisticRegression())])
skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
cross_val_score(pipe, X, Y, cv=skf, scoring='accuracy')   # 평균 0.974 · 표준편차 0.017
```

테스트 114건 중 4건 차이는 분할 운에 따라 2건도 6건도 될 수 있다. `KFold` 노트에서 회귀에 `KFold`를 썼듯 분류에는 **`StratifiedKFold`** — 폴드마다 악성 비율을 유지한다. 표준화를 파이프라인에 넣어야 폴드마다 스케일러가 그 폴드의 학습 부분으로만 `fit`된다. `scoring='recall'`로 바꾸면 악성 재현율의 평균·편차를 본다.

### 2-4. 수렴 경고가 나면 — 표준화부터

1-3에서 본 대로 30열짜리 자료는 표준화 없이 `LogisticRegression()`을 돌리면 `ConvergenceWarning`이 난다. `max_iter`를 늘리는 건 증상 처리이고, 원인은 열 사이 수백 배 스케일 차이다. 순서는 ① 표준화했는지 확인 → ② 그래도 나면 `max_iter=1000` → ③ 그래도 나면 `C`를 줄여 규제를 세게. 수업 노트 2-6과 같은 순서다.

### 2-5. `map` 대신 쓸 수 있는 것들

```python
Y = (df['diagnosis'] == 'M').astype(int)                 # 불리언 → 0/1
from sklearn.preprocessing import LabelEncoder
Y = LabelEncoder().fit_transform(df['diagnosis'])        # B → 0, M → 1 (알파벳순)
```

`map`은 사전에 없는 값을 NaN으로 바꾸므로 오타·대소문자가 섞인 자료라면 `Y.isna().sum()`으로 확인한다. `== 'M'` 불리언 비교는 "M이면 1, 아니면 0"이라 셋째 값이 들어와도 조용히 0이 되니 두 값뿐인지 `unique()`를 먼저 본다. `LabelEncoder`는 알파벳순이라 이 자료에서는 우연히 M = 1이지만, `'Benign'`/`'Malignant'`처럼 이름이 바뀌면 순서도 바뀐다 — 양성 클래스를 내가 정하려면 `map`이 가장 명시적이다.

## 3. 더 나아가 알면 좋은 것

### 3-1. 정밀도·재현율·F1·ROC-AUC — 분류 지표의 자리

정확도는 "전체 중 맞힌 비율", 정밀도는 "악성이라 한 것 중 진짜 악성", 재현율은 "진짜 악성 중 찾아낸 것", F1은 둘의 조화 평균이다. 임계값을 움직이면 정밀도와 재현율이 반대로 움직이고, 그 **모든 임계값을 한 곡선**으로 그린 것이 ROC(거짓 양성률 vs 재현율)와 PR 곡선이며, 곡선 아래 면적 AUC가 임계값에 무관한 모델 점수다. `GridSearchCV(scoring='roc_auc')`처럼 격자 탐색의 기준으로도 쓴다. 의료·사기 탐지처럼 양성이 드물고 비용이 큰 문제에서는 정확도 대신 이 지표들로 보고한다.

### 3-2. 선형 경계가 부족할 때

로지스틱 회귀는 30차원 공간을 **평면 하나**로 가른다(수업 노트 3-2). 정확도 0.965는 그 평면으로 거의 갈린다는 뜻이고, 남은 4건이 평면 근처에 몰려 있는 표본이다. 더 가르고 싶으면 수업 노트의 순서대로 `PolynomialFeatures`로 곡면을 만들거나, `KNeighborsClassifier`·`DecisionTreeClassifier`·`RandomForestClassifier`·`SVC`처럼 경계 모양이 다른 모델을 같은 뼈대에 끼운다. 이 자료는 사이킷런 예제로 흔히 쓰여 여러 모델이 0.95~0.98 사이에 모이는데, 그 차이가 분할 운보다 큰지는 2-3의 교차 검증으로만 판단할 수 있다.

### 3-3. 사이킷런 내장 자료와 캐글 CSV

`from sklearn.datasets import load_breast_cancer`는 같은 UCI 자료를 다운로드 없이 준다. `as_frame=True`로 받으면 데이터프레임이고, `target`은 캐글과 반대로 **0 = 악성, 1 = 양성**이다. 같은 자료라도 출처마다 양성 클래스 번호가 다르니 `target_names`를 먼저 확인한다 — 1-1에서 매핑을 직접 한 이유가 여기서도 드러난다. `load_iris`·`load_diabetes`·`load_wine`도 같은 방식이라 CSV 없이 분류·회귀 뼈대를 연습할 때 편하다.

### 3-4. 다음에 볼 키워드

- `drop(columns=['id'])` · `dropna(axis=1, how='all')` vs `how='any'` · `map({'M': 1, 'B': 0})`로 양성 클래스 직접 지정
- `stratify=Y` 63:37 · 30열 표준화 필수(수렴 20회 vs 3,000회+) · `accuracy_score(정답, 예측)` = `score`
- `classes_ [0 1]` → `predict_proba` 둘째 열 = 악성 확률 · 혼동 행렬 `[[71 1] [3 39]]` · 거짓 음성 3건 · 악성 재현율 0.93
- `coef_` 30개 부호 읽기 · 임계값 0.3 · `StratifiedKFold` + 파이프라인 · `LabelEncoder` vs `map`
- 정밀도·재현율·F1·ROC-AUC · `PolynomialFeatures`/k-NN/트리/SVC · `load_breast_cancer` 타깃 부호 반대

## 실습 파일

- `KDT_2026/2026_Python/ML_pracitce/practice4.py` — 로지스틱 이진 분류 연습문제(지시문 단계 1~6): 1 `./data.csv` 로드 → `id`·전부 결측인 `Unnamed: 32` 제거(`drop(columns=['id'])`·`dropna(axis=1, how='all')` 힌트 코드) → `diagnosis` M = 1·B = 0 매핑 `y`·나머지 30열 `X`, 2 `train_test_split(test_size=0.2, random_state=42, stratify=y)`, 3 `StandardScaler` 학습 세트 `fit` → `transform` 둘, 4 `LogisticRegression().fit`, 5 `predict` → `accuracy_score`, 6 테스트 앞 3건의 예측 클래스와 `predict_proba`(양성 0/악성 1 확률). 풀이 코드는 파일에 없고 `data.csv`도 폴더에 없어, 풀이는 이 노트에 적고 결과는 사이킷런 내장 `load_breast_cancer`(같은 569건·30열)로 확인했다
- (데이터) 캐글 Breast Cancer Wisconsin — 569건 × `id`·`diagnosis`·30 측정값·`Unnamed: 32`, 양성 357·악성 212

## 관련 노트

[[AI 정리본 인덱스]] · [[AI day14 로지스틱 회귀로 도미·빙어 분류]] · [[AI day14 파이프라인·그리드서치·joblib 연습문제 풀이]] · [[AI day14 KFold 교차 검증과 GridSearchCV 하이퍼파라미터 탐색]] · [[AI day13 StandardScaler 표준화와 릿지·라쏘 규제]] · [[KDT_2026 학습 지도]]
