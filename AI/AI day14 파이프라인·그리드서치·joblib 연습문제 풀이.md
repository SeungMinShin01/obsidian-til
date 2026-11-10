---
출처: Claude 분석
원본: KDT_2026/2026_Python/ML_pracitce/practice3.py, ML_pracitce/student_dataset_10000_rows.csv
작성일: 2026-11-10
tags: [학습, ai, python]
---

# AI day14 — 파이프라인·그리드서치·joblib 연습문제 풀이

> 실습 파일: `ML_pracitce/practice3.py`, `ML_pracitce/student_dataset_10000_rows.csv`
> 허브: [[AI 정리본 인덱스]] · 이전: [[AI day14 KFold 교차 검증과 GridSearchCV 하이퍼파라미터 탐색]] · 다음: [[AI day14 로지스틱 회귀로 도미·빙어 분류]]

day14 수업의 세 도구 — `Pipeline`, `KFold` + `GridSearchCV`, `joblib` — 를 **한 문제에 이어 붙여** 쓰는 연습이다. 재료는 day13 연습에서 썼던 캐글 학생 성적 데이터(1만 명 × 수치형 6열 → `exam_score`) 그대로다. 앞 연습에서는 `degree=2`·`alpha=1.0`을 **고정**하고 다항 변환과 표준화를 손으로 두 번씩 돌렸는데, 이번에는 그 전처리를 파이프라인 하나에 넣고, 차수와 규제 강도를 격자 탐색으로 **고르고**, 고른 파이프라인을 파일로 저장했다가 다시 읽어 새 학생 두 명의 점수를 예측한다. 연습 파일에는 1~6번 지시문만 있고 풀이 코드는 비어 있어, 지시문을 따라 적은 풀이와 실행 결과를 여기에 정리한다. 결론부터 적으면 최적 조합은 `degree=2`·`alpha=0.1`, 교차 검증 평균 R² 0.730, 테스트 R² 0.737 — day13 연습의 릿지(0.737)와 사실상 같은 점수다. 자료가 8,000행이라 `alpha`가 거의 영향을 못 주고, 차수 1 → 2의 차이(0.66 → 0.73)만 뚜렷하다.

## 1. 배운 내용

### 1-1. 문제 1·2 — 특성·타깃 구성과 분할

```python
import pandas as pd
df = pd.read_csv('./ML_pracitce/student_dataset_10000_rows.csv')

feature = ['study_hours', 'attendance', 'sleep_hours', 'internet_usage', 'assignments_completed', 'previous_score']
target = 'exam_score'
X = df[feature]          # (10000, 6)
Y = df[target]           # (10000,)

from sklearn.model_selection import train_test_split
X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size=0.2, random_state=42)
# 8000 / 2000
```

day13 연습 문제 1·2와 글자 하나 다르지 않다. 범주형 `placement_status`를 빼고 수치형 6열만 특성으로 쓰고, `random_state=42`로 8,000/2,000을 고정한다. 같은 씨앗이라 **앞 연습과 테스트 세트가 똑같다** — 그래서 이번 결과를 앞 연습의 0.737과 바로 비교할 수 있다.

### 1-2. 문제 3 — `Pipeline`에 변환기 둘 + 모델 하나

```python
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import PolynomialFeatures, StandardScaler
from sklearn.linear_model import Ridge

pipe = Pipeline([
    ('poly',   PolynomialFeatures(include_bias=False)),   # degree는 비워 둔다 → 격자가 채움
    ('scaler', StandardScaler()),
    ('ridge',  Ridge(random_state=42)),                   # alpha도 비워 둔다
])
```

day13 연습에서 `poly.fit` → `poly.transform` × 2 → `ss.fit` → `ss.transform` × 2 → 모델 `fit`으로 **호출 일곱 번**이던 것이 파이프라인 정의 한 번으로 줄었다. 핵심은 두 하이퍼파라미터를 **일부러 비워 둔다**는 점이다. `PolynomialFeatures()`의 `degree`도, `Ridge()`의 `alpha`도 기본값 상태로 두고, 어떤 값이 좋은지는 다음 단계의 격자가 정한다. 지시문이 "데이터 누수를 방지하고자 파이프라인을 구성한다"고 적은 이유는 수업 노트 그대로다 — `fit`은 학습 세트에만, `transform`은 둘 다, 이 순서를 파이프라인이 **구조적으로** 지켜 준다. 교차 검증 안에서 폴드가 다섯 번 바뀔 때마다 변환기도 그 폴드의 학습 부분으로만 다시 `fit`되는데, 손 코드였다면 이걸 직접 짜야 했다.

| 단계 이름 | 객체 | 비워 둔 파라미터 | 격자 키 |
| --- | --- | --- | --- |
| `'poly'` | `PolynomialFeatures(include_bias=False)` | `degree` | `'poly__degree'` |
| `'scaler'` | `StandardScaler()` | — | — |
| `'ridge'` | `Ridge(random_state=42)` | `alpha` | `'ridge__alpha'` |

`Ridge`의 `random_state`는 `solver='sag'`/`'saga'`처럼 무작위성이 있는 풀이기에서만 쓰이고 기본 풀이기(`'auto'` → 촐레스키)에서는 아무 일도 하지 않는다. 지시문이 넣으라 했으니 넣되, 재현성을 위해 꼭 필요한 건 `train_test_split`과 `KFold`의 `random_state` 쪽이다.

### 1-3. 문제 4 — `KFold` + `GridSearchCV`로 차수·규제 강도 동시 탐색

```python
from sklearn.model_selection import KFold, GridSearchCV

kf = KFold(n_splits=5, shuffle=True, random_state=42)
param_grid = {
    'poly__degree': [1, 2],
    'ridge__alpha': [0.01, 0.1, 1.0, 10.0, 100.0],
}
grid = GridSearchCV(estimator=pipe, param_grid=param_grid,
                    scoring='r2', cv=kf, n_jobs=-1)
grid.fit(X_train, Y_train)

print(grid.best_params_)   # {'poly__degree': 2, 'ridge__alpha': 0.1}
print(grid.best_score_)    # 0.7301   ← 5폴드 평균 R²
best = grid.best_estimator_
print(best.score(X_train, Y_train))   # 0.7324
print(best.score(X_test,  Y_test))    # 0.7368
```

조합은 2 × 5 = **10개**, 폴드 5개이니 **50번** 학습하고 마지막에 최적 조합으로 전체 학습 세트에 한 번 더(`refit`) 학습한다. 학습 세트 8,000행을 5등분하면 폴드 하나가 1,600행 — 물고기 자료(127행 → 폴드 25행)와 달리 폴드마다 점수가 거의 흔들리지 않는다(표준편차 0.010). 수업과 격자가 조금 다르다. 수업은 `degree` 후보가 `[2, 3]`이었는데 여기는 **`[1, 2]`** 다. 1차가 후보에 있다는 건 "다항 항이 애초에 필요한가"까지 격자에 묻는 것이다.

`cv_results_`를 순위대로 펼치면 답이 또렷하다.

| 순위 | `degree` | `alpha` | 교차 검증 평균 R² | 표준편차 |
| --- | --- | --- | --- | --- |
| 1 | 2 | 0.1 | 0.7301 | 0.010 |
| 2 | 2 | 0.01 | 0.7301 | 0.010 |
| 3 | 2 | 1.0 | 0.7301 | 0.010 |
| 4 | 2 | 10 | 0.7283 | 0.010 |
| 5 | 2 | 100 | 0.6975 | 0.008 |
| 6~9 | 1 | 10 · 1 · 0.1 · 0.01 | 0.6605 | 0.007 |
| 10 | 1 | 100 | 0.6603 | 0.006 |

읽을 것은 두 가지다. 첫째, **차수가 전부**다 — 2차 다섯 조합이 모두 1차 다섯 조합 위에 있고, 1차 → 2차가 0.66 → 0.73으로 7점을 올린다(day13 연습의 "기준선 0.66·다항 뒤 0.74"와 같은 그림). 둘째, **`alpha`는 거의 상관없다** — 2차에서 0.01·0.1·1.0의 평균 점수가 소수점 넷째 자리까지 같고(0.7301·0.7301·0.7301), 100까지 가야 겨우 0.03 떨어진다. 1위가 0.1로 뽑힌 건 다섯째 자리 차이(0.730091 vs 0.730075)일 뿐이다. day13 연습에서 "자료가 많으면 규제 효과가 줄어든다"고 적었던 것을 격자 전체가 숫자로 보여 준다. 물고기 127마리에서는 `alpha`에 따라 0.07 → 0.97까지 요동쳤던 것과 대비된다. 최적 모델의 학습 0.732 / 테스트 0.737은 day13 연습의 `Ridge(alpha=1.0)` 0.732 / 0.737과 **같은 값**이다 — 같은 분할·같은 차수·사실상 같은 규제이니 당연한 결과이고, 격자가 "앞 연습의 고정값이 이미 거의 최적이었다"고 확인해 준 셈이다.

### 1-4. 문제 5 — `joblib.dump` → `joblib.load`

```python
import joblib
joblib.dump(best, './best_student_performance_pipe.pkl')      # 약 2.4 KB
loaded_model = joblib.load('./best_student_performance_pipe.pkl')

loaded_model.named_steps['poly'].degree                # 2
loaded_model.named_steps['poly'].n_output_features_    # 27
loaded_model.named_steps['ridge'].alpha                # 0.1
loaded_model.named_steps['ridge'].coef_.shape          # (27,)
```

저장되는 것은 `best_estimator_` — 격자가 고른 조합으로 **전체 학습 세트에 재학습된 파이프라인** 통째다. 수업 노트 1-5에서 적은 대로 `poly`의 차수, `scaler`의 열 27개 평균·표준편차, `ridge`의 기울기 27개와 절편·`alpha`가 한 파일에 들어가고, 선형 모델이라 2.4 KB면 끝난다. 불러온 객체는 `named_steps`로 안을 들여다볼 수 있어 "격자가 정말 2차·0.1을 골랐나"를 파일 쪽에서 다시 확인할 수 있다.

### 1-5. 문제 6 — 원시 데이터프레임을 그대로 `predict`

```python
sample = pd.DataFrame([
    [9, 95, 7, 2, 18, 85],     # 상위권
    [2, 60, 5, 9,  4, 50],     # 하위권
], columns=feature)

loaded_model.predict(sample)   # [101.26  48.47]
```

day13 연습 문제 5와 가장 달라진 자리다. 그때는 `poly.transform(sample)` → `ss.transform(sample_poly)` → `predict`로 **변환기 둘을 손으로 통과**시켜야 했고, 순서를 바꾸거나 하나를 빼먹으면 조용히 틀린 값이 나왔다. 파이프라인은 `predict(원시 데이터프레임)` 한 줄이고 안에서 `poly.transform` → `scaler.transform` → `ridge.predict`가 저장된 순서대로 돌아간다. 열 이름이 있는 데이터프레임을 넣으니 학습 때 열 순서(`feature` 리스트)와 맞는지도 사이킷런이 확인해 준다. 결과 101.3 / 48.5는 앞 연습의 릿지 101.4 / 48.6과 거의 같다 — 모델이 같으니 답도 같다. 100을 넘는 예측값이 나오는 이유(타깃 천장 100·만점 3,520명)와 `np.clip` 처리도 앞 연습 그대로다.

### 1-6. 이 날의 흐름 한 장 — day13 연습과 나란히

```text
[day13 연습 practice2]                      [day14 연습 practice3]
poly.fit / transform ×2                     Pipeline([poly, scaler, ridge])
ss.fit   / transform ×2                         │  degree·alpha 비워 둠
lr·ridge(1.0)·lasso(1.0) .fit ×3                ▼
   └ 세 모델 score 비교                      KFold(5) + GridSearchCV(10조합 × 5폴드)
                                                │  best_params_ = {degree 2, alpha 0.1}
sample → poly.transform → ss.transform          ▼
       → 세 모델 predict                    joblib.dump(best_estimator_) → .pkl → joblib.load
                                                ▼
                                            loaded.predict(sample)  [101.3  48.5]
```

왼쪽은 "같은 조건에서 세 모델을 비교"하는 연습이었고 오른쪽은 "한 모델의 조건을 고르고 저장해 쓰는" 연습이다. 숫자는 같은 곳에 도착하지만, 오른쪽만이 **다른 파일·다른 시점에서 다시 쓸 수 있는 산출물**(`.pkl`)을 남긴다.

## 2. 추가로 알면 좋은 활용법

### 2-1. `cv_results_`를 표로 펼치기

```python
res = pd.DataFrame(grid.cv_results_)
cols = ['param_poly__degree', 'param_ridge__alpha', 'mean_test_score', 'std_test_score', 'rank_test_score']
print(res[cols].sort_values('rank_test_score').to_string(index=False))
```

`best_params_` 하나만 보면 "0.1이 최적"이라고 믿게 되지만, 표로 펼쳐야 1-3의 "사실 0.01~1.0이 다 같다"가 보인다. 2위와 1위의 차이가 표준편차(0.010)보다 훨씬 작으면 그 순위는 의미가 없다. 격자 결과는 항상 **표준편차와 함께** 읽는 습관을 들이는 편이 안전하다. `return_train_score=True`를 주면 `mean_train_score` 열도 생겨 학습·검증 격차(과대적합 신호)까지 한 표에서 본다.

### 2-2. 격자 폭을 넓힐 때 — `np.logspace`와 `RandomizedSearchCV`

```python
import numpy as np
param_grid = {'poly__degree': [1, 2, 3],
              'ridge__alpha': np.logspace(-3, 3, 13)}     # 0.001 ~ 1000, 13개
# 3 × 13 = 39조합 × 5폴드 = 195회 — 특성 6개·8,000행이면 몇 초
```

이 자료는 작아서 격자를 키워도 금방이지만, 3차는 6개 특성이 83항으로 불어나고 자료가 커지면 전수 조사가 부담된다. 그럴 때는 수업 노트 2-4의 `RandomizedSearchCV(n_iter=20)`로 조합을 추첨하거나, 1차로 거친 격자(`[0.01, 1, 100]`)를 돌려 대략의 위치를 잡고 2차로 그 근처만 촘촘히 보는 **두 단계 탐색**이 흔한 요령이다.

### 2-3. `scoring`을 RMSE로 바꾸기

```python
grid = GridSearchCV(pipe, param_grid, scoring='neg_root_mean_squared_error', cv=kf, n_jobs=-1)
-grid.best_score_       # 약 7.8점
```

R²는 "전체 변동의 몇 %를 설명하나"라 점수 단위를 모른다. 시험 점수처럼 단위가 분명한 타깃이면 `neg_root_mean_squared_error`로 바꿔 "평균 몇 점 틀리나"를 바로 읽는 쪽이 보고서에 쓰기 좋다. 사이킷런은 "클수록 좋다"로 통일하려고 오차 지표에 `neg_` 접두사를 붙이니 부호를 뒤집어 읽는다.

### 2-4. 저장 파일에 꼬리표 달기

```python
import sklearn
bundle = {'model': best, 'feature': feature, 'sklearn': sklearn.__version__,
          'cv_r2': grid.best_score_, 'params': grid.best_params_}
joblib.dump(bundle, './best_student_performance_pipe.pkl')
loaded = joblib.load('./best_student_performance_pipe.pkl')
loaded['model'].predict(sample[loaded['feature']])
```

파이프라인만 저장하면 몇 달 뒤 "이게 어떤 열 순서로, 어느 버전에서, 점수 몇으로 만든 파일인지"를 잃는다. 딕셔너리로 싸서 열 목록·버전·검증 점수를 같이 넣어 두면 서빙 쪽에서 `loaded['feature']`로 열 순서를 맞추고 버전 불일치를 미리 잡을 수 있다. `.pkl`은 임의 코드를 실행할 수 있는 형식이라 **출처가 분명한 파일만** `load`한다는 수업 노트 2-7의 주의도 그대로다.

### 2-5. 상대 경로와 실행 위치

연습 코드의 `'./ML_pracitce/…csv'`와 `'./best_student_performance_pipe.pkl'`은 **현재 작업 폴더 기준**이다. VS Code에서 `2026_Python` 폴더를 열고 실행하면 CSV는 찾고 `.pkl`은 `2026_Python/` 바로 아래에 생긴다. 다른 폴더에서 실행하면 CSV부터 `FileNotFoundError`가 난다. 저장 파일이 어디 생겼는지 헷갈리면 `import os; os.path.abspath('./best_student_performance_pipe.pkl')`로 절대 경로를 찍어 본다.

## 3. 더 나아가 알면 좋은 것

### 3-1. 격자가 고른 점수도 낙관적이다 — 중첩 교차 검증

`best_score_` 0.730은 10개 조합 중 **가장 높은 것을 고른 뒤**의 점수라, 운 좋게 높게 나온 조합이 뽑혔을 가능성이 섞여 있다. 조합이 많을수록 이 낙관은 커진다. 엄밀히 하려면 바깥 `cross_val_score(GridSearchCV(...), X, Y, cv=5)`로 "격자 탐색까지 포함한 절차"를 다시 교차 검증한다(수업 노트 3-1). 이 자료에서는 조합이 10개뿐이고 테스트 0.737이 교차 검증 0.730과 거의 같아 걱정할 수준은 아니다.

### 3-2. `.pkl` 다음 — 서빙과 모델 관리

이 연습이 끝나는 자리(`loaded_model.predict(sample)`)가 곧 서빙 코드의 시작이다. 수업 `s-05.py`가 `fish_model.pkl`을 읽어 물고기 한 마리를 예측하듯, 이 파일을 FastAPI 엔드포인트에서 읽어 JSON으로 받은 학생 정보를 데이터프레임으로 만들어 `predict`하면 API가 된다. 모델이 여러 버전으로 쌓이면 파일명 대신 MLflow 같은 모델 레지스트리에 점수·파라미터·버전을 함께 기록하고, 사이킷런 모델을 다른 언어 런타임에서 쓰려면 ONNX로 내보낸다. 보안이 신경 쓰이면 `pickle` 대신 사이킷런 쪽에서 미는 `skops` 형식이 있다.

### 3-3. 특성 분포가 바뀌면 — 드리프트

저장한 모델은 2026년 학생 자료의 분포(공부 시간 1~10시간, 출석률 ~100 등)를 전제로 한다. 내년 자료에서 인터넷 사용 시간의 범위가 두 배가 되면 `scaler`의 평균·표준편차가 어긋나고 예측이 틀어진다. 서빙 입력의 분포를 학습 때와 주기적으로 비교(평균·분위수)해 **재학습 시점**을 정하는 것이 운영의 일부다 — `.pkl`은 한 번 만들면 끝이 아니다.

### 3-4. 다음에 볼 키워드

- 파이프라인에 **파라미터 비워 두기** → `단계__파라미터` 격자 · `degree` 후보에 1 포함(다항 필요성 검증) · 50회 + refit 1회
- `cv_results_` 표준편차와 함께 읽기 · 2차에서 `alpha` 무차별(자료 8,000행) · 1차 → 2차 7점
- `best_estimator_` = 재학습된 파이프라인 · `named_steps`로 확인 · 2.4 KB · `predict(원시 DataFrame)` 한 줄
- `np.logspace` · `RandomizedSearchCV` · 두 단계 탐색 · `neg_root_mean_squared_error` · 딕셔너리 번들 저장 · 상대 경로
- 중첩 교차 검증 · FastAPI 서빙 · MLflow · ONNX · `skops` · 드리프트와 재학습

## 실습 파일

- `KDT_2026/2026_Python/ML_pracitce/practice3.py` — 파이프라인·그리드서치·joblib 연습문제(지시문 1~6): 1 캐글 학생 성적 CSV → 수치형 6열 `X`·`exam_score` `y`, 2 `train_test_split(…, 0.2, random_state=42)`, 3 `Pipeline([('poly', PolynomialFeatures(include_bias=False)), ('scaler', StandardScaler()), ('ridge', Ridge(random_state=42))])`(데이터 누수 방지), 4 `KFold(n_splits=5, shuffle=True, random_state=42)` + `param_grid {'poly__degree': [1, 2], 'ridge__alpha': [0.01, 0.1, 1.0, 10.0, 100.0]}` + `GridSearchCV(scoring='r2', cv=kf, n_jobs=-1)` `fit`, 5 `best_estimator_`를 `joblib.dump('./best_student_performance_pipe.pkl')` → `joblib.load` → `loaded_model`, 6 상위권·하위권 샘플 2행 데이터프레임을 `.predict()`에 **원시 그대로** 전달해 비교 출력. 풀이 코드는 파일에 없고 지시문만 있어 이 노트에 풀이와 실행 결과를 적었다
- `KDT_2026/2026_Python/ML_pracitce/student_dataset_10000_rows.csv` — 학생 10,000명 × 8열, 결측 없음 (day13 연습과 같은 파일)

## 관련 노트

[[AI 정리본 인덱스]] · [[AI day14 KFold 교차 검증과 GridSearchCV 하이퍼파라미터 탐색]] · [[AI day14 로지스틱 회귀로 도미·빙어 분류]] · [[AI day14 사이킷런 Pipeline으로 다항·표준화·회귀 묶기]] · [[AI day13 다항 규제 회귀 연습문제 풀이]] · [[KDT_2026 학습 지도]]
