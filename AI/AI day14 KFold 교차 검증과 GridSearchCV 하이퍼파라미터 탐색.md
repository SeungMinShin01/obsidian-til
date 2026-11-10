---
출처: Claude 분석
원본: KDT_2026/2026_Python/day14/s-04.py(10~11단계), day14/Fish.csv, 수업 PPT(KFold·GridSearchCV·joblib 슬라이드)
작성일: 2026-11-10
tags: [학습, ai, python]
---

# AI day14 — KFold 교차 검증과 GridSearchCV 하이퍼파라미터 탐색

> 실습 파일: `day14/s-04.py` (10)~11) 단계), `day14/Fish.csv`, 수업 PPT 슬라이드 9~10, [2]·[3] (`day14/선형회귀모델.pkl` 저장 코드)
> 허브: [[AI 정리본 인덱스]] · 이전: [[AI day14 사이킷런 Pipeline으로 다항·표준화·회귀 묶기]] · 다음: [[AI day14 로지스틱 회귀로 도미·빙어 분류]]

앞 노트에서 다항 확장 → 표준화 → 회귀를 파이프라인 하나로 묶었다. 이 노트는 그 파이프라인을 재료로 두 가지 질문에 답한다. 하나는 **"한 번 나눈 테스트 점수를 믿어도 되나"** — 앞 노트 1-2에서 `random_state`를 빼자 테스트 R²가 0.95~0.98 사이를 오갔다. 답은 자료를 K개로 나눠 K번 평가하고 평균을 내는 **K-Fold 교차 검증**이다. 다른 하나는 **"`degree`는 2인가 3인가, `alpha`는 얼마인가"** — day13에서 `alpha` 여섯 개를 `for`로 돌려 격차를 눈으로 고르던 일을, 후보 조합 전부를 교차 검증으로 전수 조사해 자동으로 고르는 **`GridSearchCV`** 가 맡는다. 두 도구는 따로가 아니라 `GridSearchCV(cv=KFold(…))`로 한 몸이고, 파이프라인의 `단계__파라미터` 이름 규칙 덕분에 전처리 차수와 모델 규제 강도를 **한 격자 안에서** 같이 고른다. 마지막으로 고른 최적 파이프라인을 `joblib`으로 파일에 저장하고 다시 읽어 새 물고기 한 마리를 예측하는 데까지 간다.

## 1. 배운 내용

### 1-1. K-Fold 교차 검증이란

K-Fold 교차 검증은 전체 훈련 데이터를 **K개의 동일한 크기의 하위 집합(Fold)** 으로 나눈 뒤, 각 폴드를 한 번씩 검증 데이터로 쓰고 나머지 (K−1)개 폴드로 학습하여 **총 K번의 평가를 반복**하는 검증 기법이다. 왜 필요한가 — 고정된 단일 분할(Train/Test Split)로만 평가하면 데이터가 우연히 한쪽으로 치우쳐 분할되는 편향이 생겨, 모델의 실제 일반화 성능을 왜곡하거나 과적합 여부를 정확히 진단하기 어렵기 때문이다.

슬라이드 그림의 다섯 단계를 그대로 옮긴다.

```text
전체 데이터 ──┬── 테스트 데이터 20%  ← 최종 평가용으로 격리, 교차 검증에 안 씀
             └── 훈련 데이터 80%   ← 이것만 K개 폴드로

K = 5 일 때                     검증 폴드(분홍)   학습 폴드(하늘)
  1회차  [■1][ 2][ 3][ 4][ 5]       1             2 3 4 5
  2회차  [ 1][■2][ 3][ 4][ 5]       2             1 3 4 5
  3회차  [ 1][ 2][■3][ 4][ 5]       3             1 2 4 5
  4회차  [ 1][ 2][ 3][■4][ 5]       4             1 2 3 5
  5회차  [ 1][ 2][ 3][ 4][■5]       5             1 2 3 4
                                  ──────────────────────────
                                  5개 점수의 평균 = 최종 성능
```

| 단계 | 내용 |
| --- | --- |
| 1. 데이터 분할 | 전체 중 20%는 최종 평가용(테스트)으로 격리하고, 나머지 80%(훈련 데이터)만 교차 검증에 쓴다 |
| 2. K개 폴드 분할 | 훈련 데이터를 동일한 크기의 K개 블록으로 균등하게 나눈다 |
| 3. 순환 학습 및 검증 (K회 반복) | 매 반복마다 1개 폴드는 검증용, 나머지 (K−1)개는 학습용으로 번갈아 교체하며 총 K번 학습·평가 |
| 4. 평균 성능 산출 | 도출된 K개의 평가 점수를 평균 내어 최종 모델 성능으로 확정 |
| 5. 핵심 목적 | 모든 데이터를 골고루 학습과 검증에 활용해 특정 분할로 인한 표본 편향과 과적합을 방지하고 일반화 신뢰도를 높인다 |

중요한 것은 **테스트 세트는 여전히 따로 있다**는 점이다. 교차 검증은 훈련 80% 안에서 일어나는 일이고, 테스트 20%는 마지막에 한 번만 쓴다. 폴드별 "검증 데이터"는 테스트 세트가 아니라 훈련 데이터의 일부다.

| 종류 | 클래스 | 어울리는 문제 | 하는 일 |
| --- | --- | --- | --- |
| 표준 K-Fold | `KFold` | 타깃이 연속형 실수인 **회귀** | 인덱스를 순차적으로, 또는 무작위 셔플로 K개로 균등 분할. 과적합 방지와 분산 축소에 가장 널리 쓰이는 표준 방식 |
| 계층별 K-Fold | `StratifiedKFold` | 타깃 레이블 분포가 불균형한 **분류** | 각 폴드가 원본의 클래스 비율(예: 정상 95%·사기 5%)을 그대로 유지하도록 계층화해서 분할. 특정 폴드에 소수 클래스가 누락되어 학습·평가가 왜곡되는 문제를 원천 차단 |

이 노트의 Fish 무게 예측은 회귀이므로 `KFold`다. 나중에 종(`Species`) 분류로 넘어가면 종마다 마릿수가 다르니(브림 35마리, 화이트피시 6마리 …) `StratifiedKFold`가 필요해진다.

### 1-2. `GridSearchCV`란

그리드 서치는 사용자가 지정한 **하이퍼파라미터 후보군의 모든 조합을 격자(Grid)로 엮어 전수 조사**하고, 교차 검증을 병행해 최적 조합을 자동으로 찾는 튜닝 기법이다. 왜 필요한가 — 모델의 구조적 복잡도나 규제 강도를 정하는 하이퍼파라미터(릿지의 `alpha`, SVM의 `C`, 트리의 `max_depth` …)는 **데이터로부터 학습되지 않는 외부 설정값**이라, 손으로 하나씩 바꾸면 비효율적일 뿐 아니라 최적 조합을 체계적으로 찾아낼 수 없기 때문이다.

| 기능 | 내용 |
| --- | --- |
| 전수 탐색 및 자동 최적화 (Exhaustive Search & refit) | 딕셔너리로 넘긴 파라미터 격자의 **카테시안 곱** 전체를 교차 검증 폴드 수만큼 곱해 반복 학습. 끝나면 최고 성능의 최적 파라미터(`best_params_`)와 최고 점수(`best_score_`)를 뽑고, `refit=True`(기본값)로 **전체 훈련 데이터로 최종 모델을 즉시 재학습**해 완성본(`best_estimator_`)을 돌려준다 |
| 파이프라인 결합 튜닝 (Pipeline Integration) | 전처리 변환기 + 모델이 결합된 `Pipeline` 객체를 그대로 추정기로 넘긴다. **`스텝이름__파라미터명`**(예: `scaler__with_mean`, `model__C`) 문법으로 전처리 방식(스케일러 종류, 다항 차수)과 모델의 규제 계수를 **한 격자 안에서 동시에** 탐색하고, 교차 검증의 각 폴드 분할 시점마다 전처리를 독립적으로 다시 수행해 데이터 누수 없는 자동화 최적화를 실현 |

슬라이드의 손그림 격자가 직관적이다 — 세로축 `max_iter` (10, 100, 1000), 가로축 `alpha` (10, 20, 30)인 3×3 표에 체크 표시가 하나씩 찍히고, 가장 좋은 칸(`max_iter=100`, `alpha=20`)에 빗금이 쳐진다. "모든 칸을 다 해 보고 제일 좋은 칸을 고른다"가 그리드 서치의 전부다. 칸 하나마다 K번 학습하니 총 학습 횟수는 **조합 수 × K**다.

| 속성 | 뜻 |
| --- | --- |
| `best_estimator_` | 가장 성능이 좋은 최적의 학습 모델 (파이프라인이면 파이프라인 통째) |
| `best_params_` | 가장 좋은 성능을 낸 하이퍼파라미터 조합 |
| `best_score_` | 교차 검증을 통해 얻은 최고 점수 (K개 폴드 평균) |
| `cv_results_` | 모든 파라미터 조합에 대한 상세 결과 (딕셔너리 — 데이터프레임으로 보면 편하다) |

### 1-3. 코드 — 릿지 파이프라인에 격자 걸기

```python
pipe_poly_ridge = Pipeline([
    ('poly',   PolynomialFeatures(include_bias=False)),   # degree는 격자에서 정한다
    ('scaler', StandardScaler()),
    ('ridge',  Ridge())                                    # alpha도 격자에서
])
param_grid = {
    'poly__degree': [2, 3],
    'ridge__alpha': [0.01, 0.1, 1.0, 10.0, 100.0]
}
kf = KFold(n_splits=5, shuffle=True, random_state=42)
grid = GridSearchCV(
    estimator=pipe_poly_ridge,
    param_grid=param_grid,
    scoring='r2',
    cv=kf,
    n_jobs=-1
)
grid.fit(X_train, y_train)
best_pipe = grid.best_estimator_
```

네 덩어리를 차례로 읽는다.

| 코드 | 슬라이드 설명 |
| --- | --- |
| `param_grid = {'poly__degree': [2, 3], 'ridge__alpha': [0.01, 0.1, 1.0, 10.0, 100.0]}` | 파이프라인 내부의 특정 단계에 접근하는 `단계이름__파라미터명` 접두사 문법으로 후보군을 딕셔너리로 설정. 차수 2개 × 릿지 규제 강도 5개 = **카테시안 곱 10개 조합**을 전수 검사 |
| `kf = KFold(n_splits=5, shuffle=True, random_state=42)` | 훈련 데이터를 같은 크기의 5개 폴드로 나누는 검증기. `shuffle=True`와 고정 시드 `random_state=42`로 데이터를 무작위로 고르게 섞어, 특정 순서나 편향에 따른 표본 오차를 막고 객관적인 검증 환경을 만든다 |
| `GridSearchCV(estimator=pipe_poly_ridge, param_grid=param_grid, scoring='r2', cv=kf, n_jobs=-1)` | 파이프라인 추정기 + 파라미터 후보군 + 5분할 교차 검증기(`cv=kf`) + 평가 지표(`scoring='r2'`)를 결합한 탐색 엔진. `n_jobs=-1`은 joblib 백엔드로 **시스템의 모든 CPU 코어를 병렬 동원**해 50회(10조합 × 5폴드) 반복 훈련 속도를 높인다 |
| `grid.fit(X_train, y_train)` | 훈련 데이터로 10가지 조합 각각에 5-Fold 교차 검증을 병렬 수행해 가장 우수한 **평균 R²** 를 낸 파라미터 쌍을 확정. 탐색이 끝나면 `refit=True`(기본값) 동작으로 전체 `X_train`에 최적 파라미터를 적용한 최종 파이프라인을 단번에 재학습 |

`Ridge()`와 `PolynomialFeatures(include_bias=False)`에 `alpha`·`degree`를 **비워 둔 것**이 포인트다 — 격자가 채울 자리이기 때문이다. 앞 노트 2-1의 `set_params(poly__degree=3)`를 그리드 서치가 조합마다 자동으로 불러 주는 셈이다. `shuffle=True`가 왜 필요한지는 2-2에서 숫자로 확인한다.

### 1-4. 결과 읽기 — 최적 조합과 세 점수

```python
print("\n=== [GridSearchCV (Poly + Ridge) 최적화 결과] ===")
print(f"최적 파라미터 조합   : {grid.best_params_}")                        # {'poly__degree': 2, 'ridge__alpha': 0.1}
print(f"최적 교차 검증 평균 R2 : {grid.best_score_:.4f}")                    # 0.9731
print(f"최종 훈련 세트 R2 (Train): {best_pipe.score(X_train, y_train):.4f}")  # 0.9820
print(f"최종 테스트 세트 R2 (Test) : {best_pipe.score(X_test, y_test):.4f}")  # 0.9721
```

Fish 전체 159마리 · 특성 3개(`Length2`·`Height`·`Width`) · `random_state=42` 분할로 돌린 결과다. 10개 조합의 교차 검증 평균을 순위대로 놓으면 이렇다(`cv_results_`에서 뽑았다).

| 순위 | `poly__degree` | `ridge__alpha` | 5폴드 평균 R² | 폴드 간 표준편차 |
| --- | --- | --- | --- | --- |
| **1** | **2** | **0.1** | **0.9731** | 0.015 |
| 2 | 2 | 0.01 | 0.9728 | 0.016 |
| 3 | 2 | 1.0 | 0.9725 | 0.016 |
| 4 | 3 | 10.0 | 0.9710 | 0.016 |
| 5 | 3 | 1.0 | 0.9698 | 0.021 |
| 6 | 3 | 0.1 | 0.9687 | 0.025 |
| 7 | 3 | 0.01 | 0.9635 | 0.036 |
| 8 | 3 | 100.0 | 0.9611 | 0.028 |
| 9 | 2 | 10.0 | 0.9573 | 0.022 |
| 10 | 2 | 100.0 | 0.9169 | 0.042 |

읽히는 것이 몇 가지 있다. **차수 2가 3보다 낫다** — 3차는 특성이 9개에서 19개로 늘어 폴드 간 편차(0.02~0.04)도 커진다. 2차에서는 `alpha` 0.01·0.1·1.0이 거의 같고(0.972~0.973) 10·100으로 가면 규제가 세져 떨어진다. 3차에서는 반대로 `alpha=10`이 가장 좋다 — **특성이 많을수록 규제를 더 세게 걸어야 한다**는 day13의 결론이 격자 안에서 그대로 보인다. 세 점수의 관계도 보기 좋다 — 교차 검증 평균 0.9731(고를 때 쓴 점수) → 전체 훈련 세트 재학습 0.9820(학습 점수라 가장 높다) → 처음 보는 테스트 세트 0.9721(교차 검증 평균과 거의 같다). **교차 검증 평균이 테스트 점수를 잘 예고했다**는 뜻이고, 이것이 교차 검증을 믿는 근거다.

### 1-5. `joblib` — 최적 파이프라인을 파일로

```python
import joblib
model_filename = './day14/선형회귀모델.pkl'
joblib.dump(best_pipe, model_filename)
print(f"파이프라인 모델이 '{model_filename}' 파일로 저장되었습니다.")
```

`joblib.dump(best_pipe, 파일명)`은 전처리 변환기와 최종 모델 가중치가 포함된 **완성형 파이프라인 객체를 디스크에 이진(바이너리) 파일로 직렬화**한다. 내부 넘파이 배열을 효율적으로 압축하므로, 재학습 없이 실서비스 배포 환경으로 모델을 안전하게 옮기고 보관할 수 있다. 저장되는 것은 `poly`의 차수 2, `scaler`의 열별 평균·표준편차 9쌍, `ridge`의 기울기 9개와 절편·`alpha=0.1` — 앞 노트 2-4에서 적은 "한 파일"이다.

```python
import joblib
import pandas as pd

model_filename = './day14/선형회귀모델.pkl'
loaded_pipeline = joblib.load(model_filename)

sample_fish = pd.DataFrame({'Length2': [32.5], 'Height': [10.0], 'Width': [4.2]})
predicted_weight = loaded_pipeline.predict(sample_fish)
print(f"신규 관측 생선의 예상 무게: {predicted_weight[0]:.2f}g")      # 370.49g
```

`joblib.load(파일명)`은 `.pkl`을 메모리로 읽어 훈련 당시의 다항 변환 기준·스케일러 통계값·회귀 가중치가 온전히 보존된 파이프라인 객체로 복원한다. 복잡한 구축·학습 과정을 다시 거치지 않고 **즉시 서빙 상태**가 된다. 새 물고기는 열 이름이 있는 데이터프레임 한 행으로 만들어 넣는다 — 학습 때 열 순서가 `Length2`·`Height`·`Width`였으니 같은 이름으로 만들면 순서 실수가 없다. 길이 32.5 cm·높이 10.0·너비 4.2의 물고기는 약 **370 g** 으로 예측된다. 이 두 코드 블록은 **다른 파일, 다른 시점**에 돌아간다는 것이 요점이다 — 학습 스크립트와 서빙 스크립트가 `.pkl` 하나로 연결된다.

### 1-6. 이 날의 흐름 한 장

```text
X_train (80%) ──▶ GridSearchCV( Pipeline[poly → scaler → ridge],
                               param_grid 10조합, cv=KFold(5, shuffle) ) ── 50회 학습
                                  │  best_params_ {degree 2, alpha 0.1} · best_score_ 0.973
                                  ▼  refit → best_estimator_ (X_train 전체로 재학습, 0.982)
X_test (20%) ───▶ best_pipe.score ─── 0.972  (처음 보는 자료, 한 번만)
                                  │
                       joblib.dump ─▶ 선형회귀모델.pkl ─▶ joblib.load ─▶ predict(새 물고기) 370 g
```

### 1-7. 수업 코드 — `s-04.py` 10)~11) 단계

앞 노트의 `s-04.py`가 9) 파이프라인 학습에서 끝나지 않고 **10) 최적 파라미터 찾기 → 11) 서빙**까지 이어진다. 슬라이드 코드(1-3)와 같은 뼈대인데 수업에서 직접 친 버전이라 번호 주석이 붙어 있고, `alpha` 후보가 하나 더 많다.

```python
# 10) 최적(성능 좋은/오차 적은) 파라미터(매개변수/대입값) 찾기 — degree=2, alpha=0.01
# 1. 파이프라인 만들기
pipe_model = Pipeline([
    ('poly',   PolynomialFeatures(include_bias=False)),   # degree 튜닝
    ('scaler', StandardScaler()),
    ('ridge',  Ridge())                                    # alpha 튜닝
])
# 2. 파라미터 후보군 만들기 — { '식별자__파라미터명' : [후보값, 후보값] }
param_grid = {
    'poly__degree': [2, 3],
    'ridge__alpha': [0.001, 0.01, 0.1, 1, 10, 100]
}
# 3. k-fold 교차 검증 — KFold(n_splits=k개의 동일한 폴드로 분할, shuffle=분할 시 무작위 섞기, random_state=42)
kf = KFold(n_splits=5, shuffle=True, random_state=42)
# 학습 데이터를 5개로 나누어 4개로 학습하고 1개로 검증하는 과정을 5번 = 평균 오차/손실 성능

# 4. 그리드서치CV — 교차 검증과 다양한 파라미터를 자동으로 실행하고 최적 성능 찾기
# GridSearchCV(estimator=진행할 모델/파이프라인, param_grid={파라미터 후보군},
#              scoring='평가지표명', cv=교차검증, n_jobs=-1(CPU 성능 최대화))
grid = GridSearchCV(estimator=pipe_model, param_grid=param_grid, scoring='r2',
                    cv=kf, n_jobs=-1)
# 5. 그리드서치로 학습
grid.fit(X_train, Y_train)
# 6. 주요 속성
best_model = grid.best_estimator_        # 가장 성능 좋은 모델 반환
print(grid.best_params_)                 # 가장 성능 좋은 파라미터 조합 반환   {'poly__degree': 2, 'ridge__alpha': 0.1}
print(grid.best_score_)                  # 교차 검증에서 평균 점수 반환          0.9731
# 7. 최적 모델로 평가
print('r2 : ', best_model.score(X_train, Y_train))   # 0.9820
print('r2 : ', best_model.score(X_test,  Y_test))    # 0.9721

# 11) 서빙 — 학습된 모델 저장하고 다른 곳에서 호출
# 연구/학습 : 코랩(고사양)에서 학습 --> 실제 서버(FastAPI)에서 호출
# 실무     : GPU 서버에서 학습    --> 실제 서버(FastAPI)에서 호출
import joblib
joblib.dump(best_model, './day14/fish_model.pkl')
```

수업 주석의 1~7 소번호가 그대로 절차다. 정리하면 이렇다.

| 소번호 | 하는 일 | 슬라이드(1-3)와 다른 점 |
| --- | --- | --- |
| 1. 파이프라인 | `poly` → `scaler` → `ridge`, `degree`·`alpha`는 비워 둔다 | 같다 (변수명만 `pipe_model`) |
| 2. 후보군 | `'식별자__파라미터명': [후보…]` 딕셔너리 | `alpha`에 **0.001**이 추가되어 6개 → 2 × 6 = **12조합** |
| 3. 교차 검증 | `KFold(5, shuffle=True, random_state=42)` | 같다 |
| 4. 그리드서치 | `GridSearchCV(estimator, param_grid, scoring='r2', cv=kf, n_jobs=-1)` | 같다 — 총 학습 횟수는 12 × 5 = **60회** |
| 5. 학습 | `grid.fit(X_train, Y_train)` | 같다 |
| 6. 속성 | `best_estimator_` · `best_params_` · `best_score_` | 같다 |
| 7. 평가 | `best_model.score` 학습·테스트 | 같다 |

주석의 "degree=2, alpha=0.01"은 **찾으려는 답의 예시**이고, 실제로 돌리면 1-4와 같은 `{'poly__degree': 2, 'ridge__alpha': 0.1}`이 나온다. `alpha=0.001`을 더 넣어도 순위가 바뀌지 않는 것이 확인 포인트다 — 2차에서 0.001·0.01·0.1·1은 0.9725~0.9731로 사실상 같고, 3차에서 `alpha=0.001`은 0.9606(폴드 간 표준편차 0.046)으로 **12개 중 10위**다. 특성이 19개인 3차에 규제를 거의 안 걸면 폴드마다 점수가 크게 흔들린다는 뜻이고, day13의 "항이 많을수록 규제를 세게"가 숫자 하나로 다시 보인다. 2차·3차 모두 `alpha`가 너무 작아도(0.001) 너무 커도(100) 떨어지고 가운데 어딘가가 좋다 — 그 "어딘가"를 손이 아니라 격자가 찾는다.

11)의 주석 두 줄이 이 날 코드의 마지막 문장이면서 다음 단계의 그림이다. **학습하는 곳과 쓰는 곳이 다르다** — 공부할 땐 코랩 같은 고사양 환경에서, 실무에선 GPU 서버에서 `fit`을 돌리고, 결과물인 `.pkl` 하나만 실제 서비스 서버(FastAPI)로 옮겨 `load`·`predict`만 한다. 학습 환경은 무겁고 비싸지만 가끔 돌리면 되고, 서빙 환경은 가볍고 항상 떠 있어야 하니 둘을 떼어 놓는 것이 자연스럽다. 1-5의 두 코드 블록이 "다른 파일, 다른 시점"이라고 적은 이유가 이 주석에 있다. 저장되는 `fish_model.pkl`은 `poly` 차수 2 · `scaler` 통계 9쌍 · `ridge` 기울기 9개와 절편·`alpha=0.1`이 든 파이프라인 통째로, 2 KB가 채 안 된다 — 모델이 작다는 것이 아니라 선형 모델은 **가중치 몇 개가 전부**라는 뜻이다. 같은 폴더의 `s-05.py`는 아직 빈 파일이라, 저장한 모델을 불러 쓰는 쪽(1-5의 `joblib.load`)이 그 자리에 들어갈 차례다. 수업이 이어지면서 `s-04.py`는 7) 평가까지만 남기고 11) 서빙 블록은 파일에서 빠졌다 — 위 11) 코드와 주석은 수업 중 적었던 시점의 기록으로 둔다. 같은 날 `s-06.py`에서 타깃을 `Species`로 바꾼 첫 분류(로지스틱 회귀)로 넘어간다 → [[AI day14 로지스틱 회귀로 도미·빙어 분류]].

## 2. 추가로 알면 좋은 활용법

### 2-1. 격자 없이 교차 검증만 — `cross_val_score`

```python
from sklearn.model_selection import cross_val_score
scores = cross_val_score(pipe_poly_lr, X_train, y_train, cv=kf, scoring='r2')
print(scores.round(3))        # [0.992 0.944 0.982 0.978 0.966]
print(scores.mean().round(4)) # 0.9724
```

고를 하이퍼파라미터가 없고 "이 파이프라인의 점수를 믿을 만한가"만 알고 싶으면 `cross_val_score`다. 파이프라인을 넘기면 폴드마다 변환기가 그 폴드의 학습 부분으로만 `fit`되어 누수가 없다. 다섯 점수가 0.94~0.99로 퍼지는데, 그 **평균 0.972와 표준편차**를 같이 적는 것이 점수 하나만 적는 것보다 정직하다. `GridSearchCV`의 `best_score_`는 이 평균을 조합마다 구한 것이다.

### 2-2. `shuffle=True`가 왜 필요한가

```python
cross_val_score(pipe_poly_lr, X_train, y_train, cv=5).round(3)     # 섞지 않음 → [0.981 0.979 0.982 0.971 0.962]
cross_val_score(pipe_poly_lr, X, Y, cv=5).round(3)                 # 전체 자료, 섞지 않음 → [0.76 0.962 0.911 0.967 0.044]
```

`cv=5`처럼 정수만 주면 `KFold(5)`가 **섞지 않고 순서대로** 자른다. `train_test_split`을 거친 `X_train`은 이미 섞여 있어 괜찮지만, 원본 `Fish.csv`처럼 **종별로 정렬된 자료**를 그대로 넣으면 마지막 폴드에 학습 때 못 본 종이 몰려 0.04 같은 점수가 나온다. 1-3의 `KFold(n_splits=5, shuffle=True, random_state=42)`가 이 함정을 막는 장치이고, 시드를 고정해야 다른 조합끼리 **같은 폴드**로 비교된다.

### 2-3. `cv_results_`를 표로 보기

```python
res = pd.DataFrame(grid.cv_results_)
cols = ['param_poly__degree', 'param_ridge__alpha', 'mean_test_score', 'std_test_score', 'rank_test_score']
print(res[cols].sort_values('rank_test_score').round(4))
```

`cv_results_`는 딕셔너리라 그대로 보기 힘들다. 데이터프레임으로 바꿔 `rank_test_score`로 정렬하면 1-4의 표가 바로 나온다. `split0_test_score`~`split4_test_score` 열에 폴드별 점수가, `mean_fit_time`에 조합별 학습 시간이 들어 있어 "점수는 비슷한데 훨씬 느린 조합"을 걸러 내는 데도 쓴다. 1-4 표의 폴드 간 표준편차가 `std_test_score`다 — 평균이 비슷하면 **표준편차가 작은 쪽**이 안정적이다.

### 2-4. 조합이 너무 많을 때 — `RandomizedSearchCV`

```python
from sklearn.model_selection import RandomizedSearchCV
from scipy.stats import loguniform
rs = RandomizedSearchCV(pipe_poly_ridge,
                        {'poly__degree': [1, 2, 3], 'ridge__alpha': loguniform(1e-3, 1e2)},
                        n_iter=20, cv=kf, scoring='r2', random_state=42, n_jobs=-1)
rs.fit(X_train, y_train)
```

격자가 3×5라면 15조합이지만 파라미터가 4~5개로 늘면 수백·수천 조합이 되어 전수 조사가 불가능해진다. `RandomizedSearchCV`는 분포(`loguniform` 등)에서 `n_iter`개만 무작위로 뽑아 시험한다. `alpha`처럼 로그 눈금이 자연스러운 값은 `loguniform`으로 주면 0.001~100 사이를 고르게 훑는다. 속성 이름(`best_params_`·`cv_results_`)은 `GridSearchCV`와 같다.

### 2-5. `scoring` 고르기 — R²만 있는 것이 아니다

| `scoring` 문자열 | 뜻 | 방향 |
| --- | --- | --- |
| `'r2'` | 결정계수 | 클수록 좋음 |
| `'neg_root_mean_squared_error'` | −RMSE | 클수록(0에 가까울수록) 좋음 |
| `'neg_mean_absolute_error'` | −MAE | 위와 같음 |
| `'accuracy'` · `'f1'` · `'roc_auc'` | 분류용 | 클수록 좋음 |

사이킷런은 "점수는 클수록 좋다"로 통일하려고 오차 지표에 **음수**를 붙인다. `neg_root_mean_squared_error`로 고르면 `best_score_`가 −45.2처럼 나오는데 부호만 뒤집으면 RMSE 45.2 g이다. 무게를 몇 g 틀리는지가 중요하면 R²보다 이쪽으로 고르는 편이 목적에 맞다. `scoring=['r2', 'neg_root_mean_squared_error']`처럼 여러 개를 넘기고 `refit='r2'`로 기준 하나를 정할 수도 있다.

### 2-6. 분류로 가면 — `StratifiedKFold`

```python
from sklearn.model_selection import StratifiedKFold
skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
GridSearchCV(clf_pipe, grid, cv=skf, scoring='accuracy')
```

1-1의 표 둘째 줄이다. 타깃을 `Species`로 바꾸면 종별 마릿수가 6~56으로 제각각이라, 보통 `KFold`로 자르면 어떤 폴드에는 화이트피시가 한 마리도 없을 수 있다. `StratifiedKFold`는 폴드마다 종 비율을 원본과 같게 유지한다. 사실 분류 문제에서 `GridSearchCV(cv=5)`처럼 정수만 주면 사이킷런이 **자동으로** `StratifiedKFold`를 쓴다 — 회귀면 `KFold`. 명시적으로 쓰는 것은 `shuffle`과 시드를 걸기 위해서다.

### 2-7. `joblib` 쓸 때 챙길 것

| 항목 | 내용 |
| --- | --- |
| `joblib` vs `pickle` | 둘 다 파이썬 객체 직렬화. `joblib`은 큰 넘파이 배열을 더 빠르고 작게 저장하고 `compress=3` 같은 압축 옵션이 있어 사이킷런 쪽 관례 |
| 버전 | `.pkl`은 저장한 사이킷런·넘파이 **버전에 묶인다**. 다른 버전에서 `load`하면 경고나 오류가 날 수 있으니 `requirements.txt`에 버전을 고정하고, 파일명이나 옆 메모에 버전을 남긴다 |
| 보안 | `load`는 임의의 파이썬 코드를 실행할 수 있다. **출처를 모르는 `.pkl`은 열지 않는다** |
| 무엇을 저장하나 | 모델만이 아니라 **파이프라인 통째**(1-5). 전처리 기준이 빠진 모델 파일은 서빙 때 쓸 수 없다 |
| 확장자 | `.pkl`·`.joblib` 둘 다 관례일 뿐 내용은 같다 |

### 2-8. 최적 파이프라인 안 들여다보기

```python
best_pipe.named_steps['ridge'].coef_.round(1)
best_pipe.named_steps['poly'].get_feature_names_out()
best_pipe.get_params()['ridge__alpha']            # 0.1
```

`best_estimator_`도 앞 노트 1-6과 같은 파이프라인이라 `named_steps`로 단계를 꺼내 기울기·특성 이름을 볼 수 있다. 그리드 서치가 고른 값이 실제로 들어갔는지 `get_params()`로 확인하는 습관이 좋다.

## 3. 더 나아가 알면 좋은 것

### 3-1. 중첩 교차 검증 — 고른 뒤의 점수는 낙관적이다

`GridSearchCV`의 `best_score_`는 10개 조합 중 **가장 좋은** 평균이라, 운 좋게 높게 나온 조합이 뽑혔을 가능성이 있어 약간 낙관적이다. 1-4에서 테스트 세트 점수를 따로 본 이유다. 테스트 세트조차 아끼고 싶으면 바깥 K-Fold 안에서 안쪽 `GridSearchCV`를 돌리는 **중첩 교차 검증**(`cross_val_score(GridSearchCV(...), X, y, cv=outer)`)으로 "고르는 과정까지 포함한" 성능을 잰다. 계산량이 K배로 늘지만 자료가 적을 때 가장 정직한 추정이다.

### 3-2. 시간 순서가 있는 자료 — `TimeSeriesSplit`

주가·대여량처럼 시간 순서가 있는 자료에 `shuffle=True`를 걸면 **미래 자료로 과거를 맞히는** 누수가 생긴다. `TimeSeriesSplit`은 항상 과거 폴드로 학습하고 바로 다음 구간으로 검증하도록 폴드를 앞으로만 늘린다. day09의 따릉이 월별 자료라면 1~2월로 3월을 맞히는 식이다. "어떤 분할기를 쓰나"가 자료의 성격에 따라 달라지는 첫 사례다.

### 3-3. 격자 너머 — 베이지안 최적화

그리드는 모든 칸을, 랜덤은 무작위 칸을 본다. **베이지안 최적화**(Optuna·scikit-optimize)는 지금까지 본 칸들의 점수로 "다음에 어디를 보면 좋을지"를 추정해 유망한 곳을 집중 탐색한다. 조합 하나 학습에 몇 분씩 걸리는 딥러닝·부스팅 모델에서 그리드 대신 쓰는 표준이 됐다. 인터페이스는 `study.optimize(objective, n_trials=50)` 식으로 다르지만, 안에서 하는 일은 결국 "교차 검증 점수를 목적 함수로 두고 하이퍼파라미터를 고르는 것"으로 같다.

### 3-4. `.pkl` 다음 — 모델 관리와 서빙

파일 하나로 시작하지만 모델이 쌓이면 "어떤 자료·어떤 파라미터로 언제 학습한 것인가"를 기록해야 한다. MLflow·DVC 같은 도구가 `.pkl`과 함께 파라미터·점수·자료 버전을 묶어 두는 **모델 레지스트리** 역할을 한다. 서빙은 `.pkl`을 읽은 파이썬 서버(FastAPI 등)가 요청 JSON을 데이터프레임으로 바꿔 `predict`를 돌려주는 구조가 기본이고, 스프링 같은 다른 백엔드는 그 파이썬 서버를 HTTP로 부른다 — day11의 httpx가 반대 방향에서 하던 일이다.

### 3-5. 다음에 볼 키워드

- `KFold(n_splits, shuffle, random_state)` · 폴드/검증 폴드 vs 테스트 세트 · `StratifiedKFold`(분류·불균형) · `TimeSeriesSplit`
- `GridSearchCV(estimator, param_grid, scoring, cv, n_jobs, refit)` · 카테시안 곱 · `best_params_`/`best_score_`/`best_estimator_`/`cv_results_` · `단계__파라미터`
- `cross_val_score` 평균·표준편차 · `shuffle=True`와 정렬 자료 · `RandomizedSearchCV`/`loguniform` · `scoring` 문자열과 `neg_` 접두사 · 다중 `scoring`+`refit`
- `joblib.dump`/`load` · 파이프라인 통째 저장 · 버전 고정 · `.pkl` 보안 · `named_steps`로 최적 모델 확인
- 중첩 교차 검증 · 베이지안 최적화(Optuna) · MLflow 모델 레지스트리 · FastAPI 서빙 · training-serving skew

## 실습 파일

- `KDT_2026/2026_Python/day14/s-04.py` — 10) 최적 파라미터 찾기: 1. `Pipeline([('poly', PolynomialFeatures(include_bias=False)), ('scaler', StandardScaler()), ('ridge', Ridge())])` → 2. `param_grid {'poly__degree': [2, 3], 'ridge__alpha': [0.001, 0.01, 0.1, 1, 10, 100]}`(`'식별자__파라미터명'` 주석) → 3. `KFold(n_splits=5, shuffle=True, random_state=42)`("5개로 나누어 4개 학습·1개 검증을 5번" 주석) → 4. `GridSearchCV(estimator=pipe_model, param_grid, scoring='r2', cv=kf, n_jobs=-1)`("CPU 성능 최대화" 주석) → 5. `grid.fit` → 6. `best_estimator_`·`best_params_`·`best_score_` → 7. `best_model.score` 학습·테스트, 11) 서빙 — "코랩/GPU 서버에서 학습 → 실제 서버(FastAPI)에서 호출" 주석, `joblib.dump(best_model, './day14/fish_model.pkl')`
- `KDT_2026/2026_Python/day14/s-05.py` — 빈 파일 (아직 내용 없음). `s-04.py`는 이후 10) 7. 평가까지만 남은 상태(11) 서빙 블록은 당시 기록)
- 수업 PPT 「9. KFold」·「10. GridSearchCV」·「[2] 선형 회귀: KFold, GridSearchCV」·「[3] joblib」 — K-Fold 정의와 5단계 그림, `KFold`/`StratifiedKFold` 비교, 그리드 서치 정의·전수 탐색·refit·파이프라인 결합 튜닝·주요 속성 4개, `pipe_poly_ridge` + `param_grid {'poly__degree': [2, 3], 'ridge__alpha': [0.01, 0.1, 1.0, 10.0, 100.0]}` + `KFold(5, shuffle=True, random_state=42)` + `GridSearchCV(scoring='r2', cv=kf, n_jobs=-1)` → `best_estimator_`·`best_params_`·`best_score_`·훈련/테스트 `score` 출력, `joblib.dump(best_pipe, './day14/선형회귀모델.pkl')` → `joblib.load` → `sample_fish` 데이터프레임(`Length2` 32.5·`Height` 10.0·`Width` 4.2) `predict`
- `KDT_2026/2026_Python/day14/Fish.csv` — 캐글 Fish Market, 159마리 × `Species`·`Weight`·`Length1~3`·`Height`·`Width`

## 관련 노트

[[AI 정리본 인덱스]] · [[AI day14 사이킷런 Pipeline으로 다항·표준화·회귀 묶기]] · [[AI day14 로지스틱 회귀로 도미·빙어 분류]] · [[AI day13 StandardScaler 표준화와 릿지·라쏘 규제]] · [[AI day13 다항 회귀 제곱항 추가와 PolynomialFeatures]] · [[AI day12 사이킷런 단순 선형 회귀로 물고기 무게 예측]] · [[KDT_2026 학습 지도]]
