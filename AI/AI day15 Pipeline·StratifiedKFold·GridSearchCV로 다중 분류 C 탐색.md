---
출처: Claude 분석
원본: KDT_2026/2026_Python/day15/s-07.py(파이프라인 구성 이후), day15/Fish.csv
작성일: 2026-11-11
tags: [학습, ai, python]
---

# AI day15 — Pipeline·StratifiedKFold·GridSearchCV로 다중 분류 C 탐색

> 실습 파일: `day15/s-07.py`(뒷부분 "파이프라인 구성"부터), `day15/Fish.csv`
> 허브: [[AI 정리본 인덱스]] · 이전: [[AI day15 로지스틱 다중 분류와 혼동행렬·분류 리포트]] · 다음: [[AI day15 ColumnTransformer·OneHotEncoder로 범주형 특성 파이프라인]]

앞 노트에서 일곱 종 다중 분류는 정확도 0.81·매크로 F1 0.66에서 멈췄고, 틀린 여섯 마리 중 다섯이 "로치를 퍼치로" 였다. 그리고 2단에 "기본 `C=1.0`을 믿지 말고 훑어보되, 훑을 때는 교차 검증으로"라고 적어 두었다. 이 노트는 그 문장을 **수업 코드로 실제로 하는 부분**이다 — `s-07.py` 뒷부분에 **파이프라인 구성 → `param_grid` → `StratifiedKFold` → `GridSearchCV(scoring='f1_macro')` → `best_estimator_`로 리포트 재출력**이 이어 붙었다. 도구는 전부 day14에서 본 것이다(Pipeline·KFold·GridSearchCV). 달라진 것은 셋이다. 분할기가 `KFold`에서 **`StratifiedKFold`**로, 점수가 `r2`에서 **`f1_macro`**로, 후보가 `alpha`에서 **`C`** 하나로. 결과는 `C=100`이 뽑혀 테스트 정확도가 **0.81 → 0.97**, 로치 4마리가 전부 맞는다.

## 1. 배운 내용

### 1-1. 파이프라인 구성 — 스케일러와 로지스틱을 한 객체로

```python
from sklearn.pipeline import Pipeline
pipe = Pipeline([
    ('scaler', StandardScaler()),
    ('model',  LogisticRegression(max_iter=1000, random_state=42))
])
```

day14 Pipeline 노트의 `[('poly', …), ('scaler', …), ('regressor', …)]` 세 단계에서 **다항 항이 빠지고 모델이 로지스틱으로** 바뀐 두 단계 판이다. 식별자는 어떤 문자열이든 되지만 뒤의 `param_grid`에서 `식별자__매개변수명`으로 다시 쓰이므로, 마지막 단계 이름을 `'model'`로 두면 `"model__C"`가 된다. 앞 노트의 수동 코드(`ss.fit_transform(X_train)` → `ss.transform(X_test)` → `model.fit`)가 이 한 객체 안으로 들어간다. 파이프라인으로 묶어야 하는 이유는 다음 단계에서 분명해진다 — **교차 검증은 학습용 127마리를 다시 다섯 번 쪼개는데, 그때마다 스케일러를 학습 쪽으로만 `fit`해야** 하기 때문이다. 손으로 미리 표준화한 `X_train_scaled`를 넣으면 검증 폴드의 평균·표준편차가 스케일러에 새어 들어간다.

`C`는 여기서 **비워 둔다**(기본 1.0). `max_iter=1000`·`random_state=42`처럼 탐색하지 않을 설정만 적어 두고, 탐색할 설정은 `param_grid`가 채운다 — day14 연습 노트에서 `degree`·`alpha`를 비워 둔 것과 같은 요령이다.

### 1-2. `param_grid = {"model__C": [0.01, 0.1, 1.0, 10.0, 100.0]}` — 후보는 로그 눈금 다섯

```python
# 하이퍼 파라미터 후보군, "식별자__매개변수명": [후보값, 후보값]
param_grid = {"model__C": [0.01, 0.1, 1.0, 10.0, 100.0]}
```

수업 주석 그대로 **`식별자__매개변수명`**(밑줄 두 개)이 키다. `model`이라는 단계의 `C`라는 뜻이고, `LogisticRegression(C=…)`에 직접 넣는 것과 같다. 후보는 0.01부터 100까지 **10배씩** 다섯 개 — day13 릿지 `alpha`·day14 `ridge__alpha`와 같은 로그 눈금이다. 규제 세기는 "2배 차이"보다 "10배 차이"가 의미 있는 단위라 선형 눈금(1, 2, 3, …)으로 훑으면 한쪽 구석만 본다.

day14와 달리 키가 하나뿐이다. `degree × alpha` 12조합이던 격자가 **5조합 × 5폴드 = 25회 학습**으로 줄었다. 로지스틱 회귀에는 다항 항이 없으니(앞 노트의 결정 경계는 직선) 돌릴 손잡이가 `C` 하나다.

### 1-3. `StratifiedKFold(n_splits=5, shuffle=True, random_state=42)` — 다섯 겹 모두에 일곱 종

```python
# K폴드 이용한 교차 검증 분할기 (다중분류: StratifiedKFold)
from sklearn.model_selection import KFold, StratifiedKFold
cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
```

day14 KFold 노트의 표에 "`KFold`는 회귀, `StratifiedKFold`는 불균형 분류"라고 적어 둔 것이 **처음으로 코드에 등장**했다. `train_test_split(stratify=Y)`가 한 번 자를 때 비율을 지켰듯, `StratifiedKFold`는 다섯 겹 **각각**에 일곱 종이 전체 비율대로 들어가게 자른다. 학습용 127마리(퍼치 45·도미 28·로치 16·파이크 13·빙어 11·파키 9·화이트피시 5)를 같은 씨앗으로 두 분할기에 넣고 **검증 폴드마다 종별 머릿수**를 세면 차이가 보인다.

| 폴드 | `StratifiedKFold` (Bream·Parkki·Perch·Pike·Roach·Smelt·Whitefish) | `KFold(shuffle=True)` |
| --- | --- | --- |
| 1 | 6·2·9·3·3·2·1 | 5·3·8·1·7·1·1 |
| 2 | 6·2·9·3·3·2·1 | 5·2·12·3·1·2·1 |
| 3 | 6·2·9·2·3·2·1 | 7·2·9·2·1·4·**0** |
| 4 | 5·2·9·2·4·2·1 | 7·2·6·4·2·3·1 |
| 5 | 5·1·9·3·3·3·1 | 4·**0**·10·3·5·1·2 |

층화 쪽은 다섯 겹이 거의 복사본처럼 고르다. 섞기만 한 `KFold`는 3번 겹에 **화이트피시가 0마리**, 5번 겹에 **파키가 0마리**다. 그 겹에서는 그 종의 재현율을 아예 계산할 수 없고(분모 0), 매크로 F1이 "7종 평균"이 아니라 "6종 평균"이 되어 버린다. 또 로치가 1마리인 겹과 7마리인 겹이 섞이면 폴드마다 점수가 크게 출렁인다 — 실제로 `C=1.0`의 다섯 겹 매크로 F1은 층화가 `0.62~0.71`, 비층화가 `0.58~0.83`이다. 화이트피시가 학습용에 5마리뿐인 자료라, **다중 분류 + 불균형이면 `StratifiedKFold`가 기본**이다. 수업 코드가 `KFold`를 import만 하고 쓰지 않은 것은 그 대비를 보여 주기 위해서라고 읽었다.

`shuffle=True`는 day14와 같은 이유다 — `Fish.csv`는 종별로 정렬돼 있어 섞지 않으면 앞 겹은 도미만, 뒷 겹은 빙어만 들어간다. 층화 분할기도 `shuffle=False`면 각 종 안에서 순서대로 자르므로 섞어 두는 편이 안전하다.

### 1-4. `GridSearchCV(pipe, param_grid, cv=cv, scoring="f1_macro", n_jobs=-1)` — 점수는 매크로 F1

```python
from sklearn.model_selection import GridSearchCV
grid = GridSearchCV(pipe, param_grid, cv=cv, scoring="f1_macro", n_jobs=-1)
grid.fit(X_train, Y_train)       # 표준화 전 원본 X_train을 넣는다
```

인자는 day14와 같은 자리이고 바뀐 것은 `scoring`이다. day14는 회귀라 `'r2'`였고, 이번에는 앞 노트에서 "정확도는 작은 종의 전멸을 숨긴다"고 확인했으므로 **`'f1_macro'`** — 일곱 종의 F1을 단순 평균한 값으로 후보를 줄 세운다. 같은 격자를 `scoring='accuracy'`로 돌려 나란히 두면 왜 이 선택이 중요한지 보인다.

| `C` | `f1_macro` 평균 | `accuracy` 평균 | `balanced_accuracy` 평균 |
| --- | --- | --- | --- |
| 0.01 | 0.156 | 0.433 | 0.199 |
| 0.1 | 0.494 | 0.717 | 0.527 |
| 1.0 | 0.666 | 0.811 | 0.689 |
| 10 | 0.776 | 0.890 | 0.786 |
| **100** | **0.829** | **0.922** | **0.844** |

이 자료에서는 세 지표가 같은 순서로 올라가 결론이 같지만, 숫자의 **크기**가 다르다. `C=0.01`은 정확도로는 0.43("절반은 맞힌다")인데 매크로 F1로는 0.16이다 — 퍼치·도미만 찍고 나머지 다섯 종을 전부 포기한 모델이라, 많은 종 위주의 정확도는 봐주고 종마다 한 표인 매크로 F1은 봐주지 않는다. 불균형 자료에서 "모델을 고르는 자"로 정확도를 쓰면 **작은 종을 버리는 쪽으로 선택이 기울 수 있다**. `scoring`은 어떤 실수를 비싸게 칠 것인지를 탐색기에 알려 주는 자리다.

`grid.fit`에 넣는 것이 **`X_train`(표준화 전)**인 점이 1-1에서 말한 핵심이다. 파이프라인 첫 단계가 스케일러이므로 폴드마다 학습 4겹으로 `fit`하고 검증 1겹을 `transform`하는 일을 탐색기가 알아서 반복한다. 앞 노트의 `X_train_scaled`를 넣으면 이중 표준화에 누수까지 겹친다. `n_jobs=-1`은 25회 학습을 모든 코어에 나눠 돌린다.

### 1-5. `best_params_`·`best_score_` — `C=100`, 교차 검증 매크로 F1 0.829

```python
print(grid.best_params_)   # {'model__C': 100.0}
print(grid.best_score_)    # 0.8289…
best_model = grid.best_estimator_
```

`cv_results_`를 표로 펼치면 다섯 후보의 순위가 이렇다.

| 순위 | `C` | 다섯 겹 평균 F1 | 표준편차 | 겹별 점수 |
| --- | --- | --- | --- | --- |
| 1 | **100** | **0.829** | 0.058 | 0.76 · 0.84 · 0.80 · 0.93 · 0.81 |
| 2 | 10 | 0.776 | 0.026 | |
| 3 | 1.0 (수업 기본값) | 0.666 | 0.036 | 0.69 · 0.71 · 0.62 · 0.62 · 0.69 |
| 4 | 0.1 | 0.494 | 0.027 | |
| 5 | 0.01 | 0.156 | 0.019 | |

읽을 것이 셋이다.

- **단조 증가** — `C`가 10배 커질 때마다 점수가 오르고 멈추지 않는다. 규제가 셀수록(`C` 작을수록) 나빠진다는 뜻이고, 앞 노트 2-3에서 테스트 세트로 훑어 본 방향(0.50 → 0.97)과 같다. day13·day14의 릿지가 `alpha=0.1~10`에서 멈춘 것과 반대로, 이 문제는 **기본 규제가 직선을 너무 눌러 과소적합**이었다.
- **뽑힌 값이 격자의 끝**이다. 1등이 가장 큰 후보라면 그 너머에 더 좋은 값이 있을 수 있다는 신호다(2-1에서 늘려 본다).
- **`C=100`의 표준편차 0.058이 가장 크다**. 겹별 0.76~0.93 — 어느 겹이 검증이 되느냐에 따라 매크로 F1이 0.17이나 움직인다. 검증 겹에 화이트피시 1마리·파키 2마리뿐이라 그 한두 마리의 결과가 종 하나의 F1을 0과 1 사이에서 뒤집기 때문이다. `best_score_` 0.83은 "대략 0.8 안팎"으로 읽는 편이 안전하다.

`best_estimator_`는 `refit=True`(기본)가 **127마리 전부로 다시 학습**한 파이프라인이다. 교차 검증 중의 다섯 모델은 각각 102마리로 배운 임시 모델이고, 최종 모델은 가장 좋았던 설정으로 전체를 다시 배운다. 학습 정확도 0.976·수렴 117회였다(`C=1.0`은 38회 — 규제가 약할수록 가중치가 커질 자리가 많아 오래 걸린다).

### 1-6. `best_model.predict(X_test)` → `classification_report` — 로치 4마리가 돌아왔다

```python
Y_pred = best_model.predict(X_test)        # 원본 X_test — 파이프라인이 표준화
print(classification_report(Y_test, Y_pred))
```

```
              precision    recall  f1-score   support
       Bream       1.00      1.00      1.00         7
      Parkki       1.00      1.00      1.00         2
       Perch       1.00      1.00      1.00        11
        Pike       1.00      1.00      1.00         4
       Roach       0.80      1.00      0.89         4
       Smelt       1.00      1.00      1.00         3
   Whitefish       0.00      0.00      0.00         1
    accuracy                           0.97        32
   macro avg       0.83      0.86      0.84        32
weighted avg       0.94      0.97      0.95        32
```

앞 노트의 리포트(`C=1.0`)와 나란히 두면 무엇이 바뀌었는지 한눈에 들어온다.

| | `C=1.0` (앞 노트) | `C=100` (그리드서치) |
| --- | --- | --- |
| 정확도 | 0.81 (26/32) | **0.97 (31/32)** |
| macro avg precision · recall · F1 | 0.63 · 0.70 · 0.66 | **0.83 · 0.86 · 0.84** |
| 퍼치 precision | 0.67 (남의 것 5마리를 끌어옴) | **1.00** |
| 로치 recall | **0.00** (4마리 전부 퍼치로) | **1.00** (4마리 전부 로치로) |
| 화이트피시 | 0 / 1 (퍼치로) | 0 / 1 (**로치**로) |
| 틀린 마릿수 | 6 | **1** |

혼동행렬로 보면 `C=1.0`에서 퍼치 열에 몰려 있던 로치 4마리가 **전부 대각선으로 돌아왔고**, 퍼치 → 빙어 1마리도 사라졌다. 규제를 풀어 주자 모델이 로치와 퍼치 사이에 경계를 그을 수 있게 된 것이다 — 앞 노트에서 "직선 경계로는 로치를 떼어낼 자리가 없다"고 적었는데, 정확히는 **규제가 가중치를 눌러 그 자리에 경계를 세우지 못한 것**이었다. 하나 남은 오답은 화이트피시 1마리가 이제 로치로 가는데, 테스트에 한 마리뿐이라 이 종의 0.00은 여전히 "모른다"에 가깝다. 매크로 평균 0.84가 0.97 정확도보다 낮은 이유도 전적으로 이 한 마리(F1 0 ÷ 7)다.

교차 검증 평균 0.83과 테스트 매크로 F1 0.84가 거의 같다 — day14 KFold 노트의 "교차 검증이 테스트를 예고한다"가 분류에서도 성립한다. 테스트 32마리는 탐색에 한 번도 쓰이지 않았으므로 이 0.97은 **처음 보는 자료에 대한 점수**다.

### 1-7. 흐름 한 장 — day14 그리드서치와 무엇이 같고 무엇이 다른가

```
Fish.csv 159마리 → X(6열) · Y(7종) → train_test_split(stratify) 127/32   ← 앞 노트와 공유
  → Pipeline([('scaler', StandardScaler()), ('model', LogisticRegression(max_iter=1000))])
  → param_grid {'model__C': [0.01, 0.1, 1, 10, 100]}                         5조합
  → StratifiedKFold(5, shuffle=True, random_state=42)                       겹마다 7종 비율 유지
  → GridSearchCV(pipe, grid, cv, scoring='f1_macro', n_jobs=-1).fit(X_train, Y_train)   25회 학습
  → best_params_ C=100 · best_score_ 0.829 · best_estimator_ (127마리 refit)
  → predict(X_test) → classification_report: 정확도 0.97 · macro F1 0.84 · 로치 4/4
```

| | day14 `s-04.py` 10)~11) | day15 `s-07.py` 뒷부분 |
| --- | --- | --- |
| 문제 | 회귀 (무게) | **다중 분류** (7종) |
| 파이프라인 | poly → scaler → `Ridge` | scaler → `LogisticRegression` |
| 후보 | `poly__degree` × `ridge__alpha` 12조합 | `model__C` 5조합 |
| 분할기 | `KFold(5, shuffle=True)` | **`StratifiedKFold(5, shuffle=True)`** |
| `scoring` | `'r2'` | **`'f1_macro'`** |
| 결과 | degree 2 · alpha 0.1 (규제 **적당히**) | `C=100` (규제 **거의 없이**) |
| 마무리 | `joblib.dump` → `s-05.py` 서빙 | `classification_report` 재출력 |
| 규제 손잡이의 방향 | `alpha` 클수록 셈 | `C` 작을수록 셈 (= 1/alpha) |

## 2. 추가로 알면 좋은 활용법

### 2-1. 1등이 격자 끝이면 격자를 늘린다 — `C=1000`·`10000`

```python
param_grid = {"model__C": [0.01, 0.1, 1, 10, 100, 1000, 10000]}
```

| `C` | 교차 검증 F1 | 표준편차 | 테스트 정확도 |
| --- | --- | --- | --- |
| 100 | 0.829 | 0.058 | 0.97 |
| 1000 | 0.890 | 0.053 | **1.00** |
| 10000 | **0.898** | 0.075 | **1.00** |

늘려 보니 아직 오른다. `C=1000`부터는 학습 1.0·테스트 1.0 — 여섯 치수만으로 일곱 종이 **거의 완전히 갈라지는 자료**라, 규제를 사실상 끄는 것이 가장 좋다. 다만 표준편차는 다시 커지고(0.075), 학습 정확도 1.0은 과대적합의 전형적 징후이기도 하다. 32마리 테스트가 1.0이라고 "완벽한 모델"이 아니라, **이 자료 안에서는 규제가 필요 없을 만큼 경계가 또렷하다**는 뜻으로 읽는다. 격자의 끝이 1등이면 한 번은 늘려 보고, 점수가 평평해지는 지점(여기서는 1000 근처)을 고르는 편이 안전하다. 반대로 끝에서 떨어지기 시작하면 그 사이를 더 촘촘히(`np.logspace(2, 4, 9)`) 훑는다.

### 2-2. `cv_results_`를 데이터프레임으로 — 평균만 보지 말고 표준편차와 겹별 점수를 같이

```python
res = pd.DataFrame(grid.cv_results_)
cols = ['param_model__C', 'mean_test_score', 'std_test_score', 'rank_test_score'] \
     + [f'split{i}_test_score' for i in range(5)]
print(res[cols].sort_values('rank_test_score').round(3))
```

1-5의 표가 이 코드다. 매크로 F1은 작은 종 한두 마리에 흔들리므로 `std_test_score`와 `split*_test_score`를 같이 봐야 "1등이 운인지"를 가늠할 수 있다. 1등과 2등의 평균 차이(0.829 − 0.776 = 0.053)가 1등의 표준편차(0.058)와 비슷하면 두 후보는 사실상 동률이다. `return_train_score=True`를 주면 `mean_train_score`도 생겨 학습·검증 격차(과대적합)를 후보별로 볼 수 있다.

### 2-3. 흔들림을 줄이는 분할기 — `RepeatedStratifiedKFold`

```python
from sklearn.model_selection import RepeatedStratifiedKFold
rcv = RepeatedStratifiedKFold(n_splits=5, n_repeats=5, random_state=42)
grid = GridSearchCV(pipe, param_grid, cv=rcv, scoring='f1_macro', n_jobs=-1)
```

5겹을 씨앗만 바꿔 5번 반복해 **25개 점수의 평균**을 낸다. 같은 격자를 돌리면 `C=100`이 0.824(표준편차 0.088)로 순위는 그대로이고 평균이 조금 내려온다 — 한 번의 5겹이 조금 운이 좋았다는 뜻이다. 학습 시간은 5배지만 127마리 자료에서는 1초 안이고, 폴드 한 개에 화이트피시 1마리 같은 상황에서는 반복이 평균을 믿을 만하게 만든다.

### 2-4. `scoring`을 여러 개 — `refit`에 기준 하나를 지정

```python
grid = GridSearchCV(pipe, param_grid, cv=cv,
                    scoring={'f1': 'f1_macro', 'acc': 'accuracy', 'bacc': 'balanced_accuracy'},
                    refit='f1', n_jobs=-1)
# cv_results_에 mean_test_f1 · mean_test_acc · mean_test_bacc 열이 따로 생긴다
```

1-4의 비교표가 이 한 번의 탐색으로 나온다. 딕셔너리로 주면 지표마다 열이 생기고, `refit`에 **최종 모델을 고를 기준 하나**를 적어야 한다. `balanced_accuracy`는 종별 재현율의 평균이라 매크로 재현율과 같고, 불균형 자료에서 정확도 대신 쓸 수 있는 또 하나의 단일 숫자다. 분류용 `scoring` 문자열은 `'f1_macro'`·`'f1_weighted'`·`'precision_macro'`·`'recall_macro'`·`'balanced_accuracy'`·`'neg_log_loss'`(확률표를 평가)·`'roc_auc_ovr'` 등이고, 전체 목록은 `sklearn.metrics.get_scorer_names()`다.

### 2-5. 격자에 `class_weight`도 넣기 — 열쇠를 두 개 돌리기

```python
param_grid = {"model__C": [0.01, 0.1, 1, 10, 100],
              "model__class_weight": [None, 'balanced']}      # 5 × 2 = 10조합
```

앞 노트 2-7의 `class_weight='balanced'`를 후보로 넣으면 "규제 세기 × 불균형 보정"을 한 번에 훑는다. 결과는 `C=100 · 'balanced'`가 1등(교차 검증 F1 0.851), 테스트 매크로 F1 **0.95**·정확도 0.94 — 매크로 F1은 오르고 정확도는 조금 내려간다. 작은 종의 오답을 비싸게 치면 큰 종에서 한두 마리를 내주는 대신 작은 종을 더 잘 잡는다. 어느 쪽을 택할지는 `scoring`이 이미 말해 준다(매크로 F1로 고르면 `'balanced'`가 뽑힌다). 딕셔너리의 키가 둘이면 `GridSearchCV`가 **카테시안 곱** 전부를 돈다는 day14 규칙 그대로다.

### 2-6. 최종 모델 저장과 서빙 — day14 `s-05.py`와 같은 그림

```python
import joblib
joblib.dump(best_model, './day15/fish_clf.pkl')              # 스케일러 + 로지스틱 통째
clf = joblib.load('./day15/fish_clf.pkl')
new = pd.DataFrame([[150, 20, 22, 25, 6.5, 3.5]], columns=X.columns)
print(clf.predict(new), clf.predict_proba(new).round(3), clf.classes_)
```

`best_estimator_`가 파이프라인이므로 파일 하나에 스케일러의 평균·표준편차와 일곱 직선이 함께 들어간다. 서빙 쪽은 원시 치수 여섯 개를 열 이름 데이터프레임으로 넣으면 끝이고, `predict_proba`의 열 순서는 `classes_` 알파벳순(앞 노트 1-5)이라 같이 돌려주는 편이 안전하다.

## 3. 더 나아가 알면 좋은 것

### 3-1. 교차 검증으로 고른 점수는 낙관적이다 — 중첩 교차 검증

`best_score_` 0.829는 다섯 후보 중 **가장 좋았던 것의 점수**라, 후보가 많을수록 운 좋은 값이 섞일 확률이 커진다(다중 비교). 이 모델의 일반화 성능을 정직하게 재려면 "격자 탐색 전체"를 바깥 교차 검증으로 한 번 더 감싼 **중첩 교차 검증**(`cross_val_score(GridSearchCV(...), X, Y, cv=outer)`)이 필요하다. 이번 수업처럼 떼어 둔 테스트 세트가 있으면 그 역할을 테스트가 대신하고(0.97), 테스트를 고르는 데 쓰지 않는 한 그 숫자는 믿을 수 있다. day14 KFold 노트 3단에 적어 둔 키워드가 분류에서 다시 나온다.

### 3-2. 규제가 0에 가까워질 때 — `penalty=None`과 완전 분리

`C`를 키울수록 좋아지다가 1000부터 학습·테스트 1.0이라면, 자료가 선형으로 **완전 분리**에 가깝다는 뜻이다. 규제를 아예 끄면(`LogisticRegression(penalty=None)`) 로그 손실이 0을 향해 가중치가 무한히 커지는 쪽으로 밀려 수렴 경고가 나고 `predict_proba`가 0/1로 극단화된다. 작은 `C`는 이를 막는 안전장치이기도 하므로, 1.0이 나왔다고 규제를 없애기보다 **점수가 평평해지는 가장 작은 `C`**(1000 근처)를 두는 것이 보통의 선택이다. 분리가 가능한 자료라면 결정 경계 자체를 바꾸는 모델(k-NN·트리·SVC)이 규제 없이도 같은 결과를 낼 수 있다.

### 3-3. 격자 밖으로 — `RandomizedSearchCV`·`loguniform`·베이지안 최적화

후보가 `C` 하나면 격자로 충분하지만, `class_weight`·`solver`·다항 차수까지 들어가면 조합이 곱으로 늘어난다. `RandomizedSearchCV(param_distributions={'model__C': loguniform(1e-2, 1e4)}, n_iter=20)`는 로그 눈금에서 20개를 뽑아 돌리고, Optuna 같은 베이지안 최적화는 앞 결과를 보고 다음 후보를 고른다. 규제 세기처럼 "크기의 자릿수"가 중요한 손잡이는 `loguniform`으로 뽑아야 0.01~1 구간이 100~10000 구간과 같은 비중으로 탐색된다.

### 3-4. 다음에 볼 키워드

- `Pipeline` 두 단계(scaler → model) · `식별자__매개변수명` · `X_train` 원본 입력(폴드별 스케일러 `fit`) · `refit=True`와 `best_estimator_` 재학습
- `StratifiedKFold` vs `KFold` 겹별 종 분포 · `RepeatedStratifiedKFold` · `StratifiedShuffleSplit` · `shuffle=True`와 정렬 자료
- `scoring='f1_macro'` vs `'accuracy'` vs `'balanced_accuracy'` · 다중 `scoring` + `refit` · `get_scorer_names()` · `'neg_log_loss'`·`'roc_auc_ovr'`
- `cv_results_`(`std_test_score`·`split*_test_score`·`rank_test_score`) · `return_train_score` · 격자 끝 1등 → 격자 확장 · `np.logspace`
- `C` 단조 증가 = 과소적합 신호 · 완전 분리와 `penalty=None` · `class_weight` 격자 · 중첩 교차 검증 · `RandomizedSearchCV`/`loguniform`/Optuna
- `joblib.dump(best_estimator_)` 파이프라인 통째 저장 → `predict_proba` + `classes_` 서빙

## 실습 파일

- `KDT_2026/2026_Python/day15/s-07.py`(뒷부분) — "파이프라인 구성" `Pipeline([(스케일러 식별자, StandardScaler()), ('model', LogisticRegression(max_iter=1000, random_state=42))])` → "하이퍼 파라미터 후보군, `식별자__매개변수명`: [후보값, …]" `param_grid = {"model__C": [0.01, 0.1, 1.0, 10.0, 100.0]}` → "K폴드 이용한 교차 검증 분할기(다중분류: StratifiedKFold)" `StratifiedKFold(n_splits=5, shuffle=True, random_state=42)`(`KFold`도 import) → "그리드서치" `GridSearchCV(pipe, param_grid, cv=cv, scoring="f1_macro", n_jobs=-1)` → `grid.fit(X_train, Y_train)` → `best_params_`("최적의 파라미터") `{'model__C': 100.0}` · `best_score_`("최고의 f1 점수") 0.829 → `best_model = grid.best_estimator_`("최적의 추정기/모델") → `best_model.predict(X_test)` → `classification_report(Y_test, Y_pred)`("파이프라인으로 최적의 모델 탐색하여 보고서 출력") 정확도 0.97 · macro F1 0.84. 앞부분(읽기 → `stratify` 분리 → 표준화 → `LogisticRegression` → 4대 평가지표 → 혼동행렬 → 리포트)은 [[AI day15 로지스틱 다중 분류와 혼동행렬·분류 리포트]]
- `KDT_2026/2026_Python/day15/Fish.csv` — 159마리 × `Species`·`Weight`·`Length1~3`·`Height`·`Width`, 학습용 127마리 종별 머릿수 퍼치 45·도미 28·로치 16·파이크 13·빙어 11·파키 9·화이트피시 5

## 관련 노트

[[AI 정리본 인덱스]] · [[AI day15 로지스틱 다중 분류와 혼동행렬·분류 리포트]] · [[AI day15 ColumnTransformer·OneHotEncoder로 범주형 특성 파이프라인]] · [[AI day14 KFold 교차 검증과 GridSearchCV 하이퍼파라미터 탐색]] · [[AI day14 사이킷런 Pipeline으로 다항·표준화·회귀 묶기]] · [[AI day14 파이프라인·그리드서치·joblib 연습문제 풀이]] · [[AI day14 로지스틱 회귀로 도미·빙어 분류]] · [[KDT_2026 학습 지도]]
