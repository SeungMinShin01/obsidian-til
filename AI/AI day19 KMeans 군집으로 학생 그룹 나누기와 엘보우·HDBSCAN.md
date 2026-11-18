---
출처: Claude 분석
원본: KDT_2026/2026_Python/day19/s-13.py
작성일: 2026-11-18
tags: [학습, ai, python]
---

# AI day19 — KMeans 군집으로 학생 그룹 나누기와 엘보우·HDBSCAN

> 실습 파일: `day19/s-13.py`
> 허브: [[AI 정리본 인덱스]] · 이전: [[AI day18 LightGBM·Optuna 의료비 회귀 연습문제 풀이]] · 다음: (아직 없음)

day12부터 day18까지는 전부 **지도학습**이었다. 특성 X와 정답 Y를 같이 넣어 학습하고, 회귀면 R²·분류면 F1로 "얼마나 맞혔나"를 재는 흐름. day19는 처음으로 **정답이 없는** 자료를 다룬다 — 포르투갈 학생 395명의 공부 시간·결석일수·1~3학기 성적(`student-mat.csv`) 다섯 열만 가지고 "비슷한 학생끼리 묶으면 몇 그룹이 나오는가"를 묻는 **비지도학습 군집(클러스터링)** 이다. 쓰는 도구는 `KMeans` 하나가 중심이고, 뒤에 그룹 수 K를 어떻게 고르는지(SSE 엘보우·실루엣), 그리고 K를 미리 정하지 않는 밀도 기반 `HDBSCAN`이 짧게 붙는다. 코드 뼈대는 지금까지와 거의 같은데 `train_test_split`에서 Y가 사라지고, `score` 대신 `inertia_`가 나오고, 평가의 기준이 "정답과 비교"에서 "**뭉침의 모양**"으로 바뀐다. 이 노트는 그 차이를 따라가며, 같은 코드를 돌려 나온 숫자(이 노트에서 확인 — scikit-learn 1.9)를 뒤에 붙인다.

## 1. 배운 내용

### 1-1. 지도학습 vs 비지도학습 — 수업 첫 두 줄

```python
# 지도학습 : X특성(독립) 과 Y타깃(종속) 모델에 학습 하여 예측 , 회귀 r2, 분류 f1-score 평가지표
# 비지도학습 : X특성(독립) 모델 이용하여 거리/밀도 군집/클러스터/그룹 , 최적K( SSE, 실루엣 )
```

수업 파일 맨 위의 주석 두 줄이 이 날의 요약이다. 표로 정리하면 이렇다.

| | 지도학습 (day12~18) | 비지도학습 (day19~) |
| --- | --- | --- |
| 입력 | 특성 X **+ 타깃 Y** | 특성 X만 |
| 모델이 배우는 것 | X → Y 매핑(기울기·질문·트리) | X 안의 **구조**(가까운 것끼리 묶기) |
| 결과 | 예측값(숫자 또는 범주) | 그룹 번호(0, 1, 2 …) |
| 평가 | 정답과 비교 — 회귀 R²·RMSE, 분류 정확도·F1 | 정답이 없다 — SSE(응집도)·실루엣(분리도) |
| 하이퍼파라미터 | `alpha`·`C`·`max_depth` … | **그룹 수 K** |
| day12 용어표 대응 | 회귀 / 분류 | 군집 / 토픽 / 주성분 |

day12 첫 노트의 용어표에서 "지도학습 회귀/분류 vs 비지도 군집/토픽/주성분"이라고만 적어 두었던 오른쪽 칸이 처음 열린 것이다. 군집의 두 갈래도 주석에 들어 있다 — **거리** 기반(KMeans: 중심점과의 거리)과 **밀도** 기반(HDBSCAN: 점이 빽빽한 곳이 곧 그룹).

### 1-2. 자료 읽기와 타깃 없는 분할

```python
import pandas as pd
url = "https://raw.githubusercontent.com/arunk13/MSDA-Assignments/master/IS607Fall2015/Assignment3/student-mat.csv"
df = pd.read_csv(url, sep=';')
X = df[['studytime', 'absences', 'G1', 'G2', 'G3']]   # 공부시간, 결석일수, 1학기~3학기 성적
# 타깃/종속 없다. -> 비지도학습 이라서

from sklearn.model_selection import train_test_split   # 학습 98% 검증용 2% (중요도 떨어짐)
X_train, X_test = train_test_split(X, test_size=0.02, random_state=42)
```

새로 나온 것이 둘이다. **`sep=';'`** — UCI 학생 성적 자료는 쉼표가 아니라 세미콜론으로 열을 나누기 때문에, 이 인자를 빼면 33개 열이 한 열로 뭉쳐 들어온다. day17 와인 자료처럼 `raw.githubusercontent.com` URL을 바로 읽는 건 같다. 전체는 395행 × 33열(학교·성별·나이·부모 학력·가족 관계 등)인데 그중 숫자 다섯 열만 뽑았다.

| 열 | 뜻 | 범위 | 평균 |
| --- | --- | --- | --- |
| `studytime` | 주당 공부 시간 등급 | 1~4 (1 = 2시간 미만 … 4 = 10시간 이상) | 2.04 |
| `absences` | 결석 일수 | 0~75 | 5.7 (중앙값 4, 오른쪽 꼬리가 길다) |
| `G1`·`G2`·`G3` | 1·2·3학기 성적 | 0~20 | 10.9 · 10.7 · 10.4 |

둘째는 **`train_test_split`의 반환값이 둘**이라는 점이다. 지금까지는 `X_train, X_test, Y_train, Y_test` 네 개를 받았는데 Y가 없으니 두 개만 돌아온다. 그리고 `test_size=0.02`로 테스트를 8명만 뗐다 — 주석의 "중요도 떨어짐"이 그 이유다. 지도학습에서 테스트 세트는 "정답을 숨겨 둔 시험지"라 20 %를 떼는 게 당연했지만, 군집에는 정답이 없어서 테스트 세트로 **점수를 낼 수가 없다**. 여기서 8명은 "학습에 안 쓴 새 학생이 어느 그룹에 떨어지는지 보는 견본" 역할이고, 그래서 387명 / 8명이다. 실무에서는 전체를 다 학습에 쓰는 경우도 많다.

### 1-3. `StandardScaler` — 군집에서는 선택이 아니라 필수

```python
from sklearn.preprocessing import StandardScaler
ss = StandardScaler()
X_train_scaled = ss.fit_transform(X_train)   # fit + transform => fit_transform
X_test_scaled  = ss.transform(X_test)
```

day13에서 배운 그대로다 — 학습용에만 `fit`(열마다 평균·표준편차를 외움), 테스트용은 `transform`만. 이 노트에서 확인한 `mean_`은 `[2.04, 5.69, 10.92, 10.73, 10.42]`, `scale_`은 `[0.84, 8.03, 3.29, 3.75, 4.59]`.

그런데 군집에서 표준화는 규제 때문이 아니라 **거리 때문에** 필수다. KMeans는 두 학생이 "비슷하다"를 다섯 열의 유클리드 거리로 재는데, 표준화 없이 재면 `absences`(0~75, 표준편차 8)가 `studytime`(1~4, 표준편차 0.84)보다 열 배 가까이 큰 폭으로 움직여서 거리가 거의 결석일수 하나로 정해진다. 공부 시간이 1에서 4로 바뀐 차이(최대폭)보다 결석이 4일에서 8일로 바뀐 차이가 더 멀어지는 셈이다. 표준화 뒤에는 다섯 열이 모두 "평균에서 표준편차 몇 개 떨어졌나"로 같은 자리에 서서 거리에 고르게 참여한다. 결과물이 `ndarray`라는 것도 기억해 둔다 — 1-5의 `[:, 4]` 인덱싱이 여기서 가능해진다.

### 1-4. `KMeans(n_clusters=3)` — 중심점 K개를 찾는 모델

```python
from sklearn.cluster import KMeans
model = KMeans(n_clusters=3)                 # 모델 생성
model.fit(X_train_scaled)                    # 군집 학습
train_labels = model.predict(X_train_scaled) # 군집 추론
print('앞에서 10명 그룹 확인:', train_labels[:10])   # 예: [1 0 0 1 2 0 0 1 1 0]
print('테스트 학생: ', model.predict(X_test_scaled))  # 예: [2 1 0 2 2 1 1 2]
```

`fit` → `predict` 두 줄은 지금까지와 같지만, `fit`에 **Y가 없다**는 것이 모든 차이다. `KMeans.fit`이 안에서 하는 일을 순서대로 적으면 이렇다.

| 단계 | 하는 일 |
| --- | --- |
| ① 초기화 | 중심점(centroid) K개를 자료 안에서 고른다(기본 `init='k-means++'` — 서로 멀리 떨어진 점을 고르게 뽑음) |
| ② 할당 | 모든 학생을 **가장 가까운 중심점**의 그룹에 배정한다 |
| ③ 갱신 | 그룹마다 소속 학생들의 평균 좌표로 중심점을 옮긴다 |
| ④ 반복 | 중심점이 더 움직이지 않을 때까지(`tol`) 또는 `max_iter=300`까지 ②·③을 되풀이한다 |

그래서 `predict`는 "새 점이 K개 중심점 중 어디에 가장 가까운가"만 계산하는 아주 싼 연산이고, 학습 자료의 결과는 `model.labels_`에 이미 들어 있다(`predict(X_train_scaled)`와 같은 값, 이 노트에서 확인). 결과는 0·1·2 세 숫자인데, 이 **번호에는 뜻이 없다**. 분류의 `classes_`처럼 "0 = 레드"가 아니라, 초기화에 따라 어느 그룹이 0이 될지가 매번 달라진다. 수업 코드처럼 `random_state`를 주지 않으면 실행마다 `[1 0 0 1 2 …]`가 `[2 1 1 2 0 …]`으로 바뀌어 보이는데, 번호만 뒤바뀐 것이고 **묶임 자체는 같다**. 이 노트에서 `random_state=0·1·2`로 돌려 보니 세 번 모두 `inertia_` 1027.02로 똑같고 첫 열 명의 번호 순서만 달랐다.

번호가 아니라 **중심점을 읽어야** 그룹의 뜻이 보인다. `ss.inverse_transform(model.cluster_centers_)`로 원 단위에 되돌린 세 중심(이 노트, `random_state=42`)은 이렇다.

| 그룹 | 인원 | 공부시간 | 결석 | G1 | G2 | G3 | 읽는 법 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| A | 187 | 1.97 | 8.0 | 9.8 | 9.9 | 10.1 | 평균 성적·결석 많은 쪽 — **중간층** |
| B | 133 | 2.21 | 3.9 | 14.5 | 14.6 | 14.8 | 성적 상위·결석 적음 — **상위층** |
| C | 67 | 1.90 | 2.8 | 7.1 | 5.4 | 2.7 | G1→G3가 7 → 5 → **2.7**로 급락 — **중도 이탈층** |

세 번째 그룹이 눈에 띈다. 결석은 가장 적은데 3학기 성적이 2.7점이다 — 이 자료에는 `G3=0`인 학생이 38명 있는데(기말 미응시·중도 포기로 보이는 값), 그 학생들이 성적 급락 그룹으로 한데 묶였다. 정답 없이 거리만으로 "성적이 떨어지다가 사라진 학생"이라는 묶음이 드러난 것이 군집의 쓸모다. `print(train_labels[:10])`만 보면 숫자 열 개일 뿐이고, 그룹의 뜻은 중심점이나 그룹별 평균(`X_train.assign(c=labels).groupby('c').mean()`)에서 읽는다.

### 1-5. 산점도 — 다섯 차원을 둘로 눌러 보기

```python
import matplotlib.pyplot as plt
plt.scatter(X_train_scaled[:, 4], X_train_scaled[:, 1], c=train_labels)        # x = G3, y = absences, 색 = 그룹
plt.scatter(X_test_scaled[:, 4],  X_test_scaled[:, 1],  c="red", marker='*')   # 테스트 8명은 빨간 별
plt.show()
```

주석의 "특성 여러 개이므로 2D 시각화 한계"가 핵심이다. 학생은 5차원 공간의 점인데 화면은 2차원이라 **다섯 열 중 둘**(`[:, 4]` = G3, `[:, 1]` = absences)만 골라 찍었다. `c=train_labels`는 그룹 번호를 색으로 바꾸는 인자(day09 산점도의 `c=`와 같다)고, 테스트 8명은 색 대신 빨간 별로 얹어 "새 학생이 어느 무리 근처에 떨어졌나"를 눈으로 본다. 두 축으로 보면 G3 낮은 쪽에 한 그룹(C), 결석 많은 위쪽에 또 한 그룹(A)이 보이지만 B와 A는 G3 10~15 사이에서 겹친다 — 나머지 세 차원(공부 시간·G1·G2)의 거리가 화면에서 사라지기 때문이다. "2D에서 겹친다 = 군집이 틀렸다"가 아니라는 점을 기억해 둔다.

중간의 "판다스 복습" 주석도 이 줄을 위한 것이다. 파이썬 리스트는 `list_2[:1]`처럼 **행 방향 슬라이싱만** 되고, `list_2[:, 1]`처럼 쉼표로 행·열을 동시에 자르는 문법은 넘파이 배열·판다스가 제공한다(day06 넘파이 인덱싱). `X_train_scaled`가 `ndarray`라서 `[:, 4]`가 되는 것이고, 표준화 전 `X_train`(DataFrame)이었다면 `X_train['G3']` 또는 `.iloc[:, 4]`로 썼어야 한다.

### 1-6. 최적 K 찾기 — SSE 엘보우

```python
sse_list = []
for k in range(2, 20):                                  # K = 2 ~ 19
    k_model = KMeans(n_clusters=k, random_state=42)     # K마다 모델을 새로 만든다
    preds = k_model.fit_predict(X_train_scaled)         # fit + predict 한 번에
    sse_list.append(k_model.inertia_)                   # 각 샘플과 자기 중심점 거리 제곱의 합
plt.plot(range(2, 20), sse_list, marker='o')
plt.show()
# 엘보우 지점(기울기가 완만하게 꺾이는 변곡점) 5 ~ 10
```

지도학습이라면 K를 `GridSearchCV`에 넣고 R²·F1이 가장 높은 값을 고르면 끝인데, 군집은 정답이 없으니 **그룹이 얼마나 단단히 뭉쳤나** 자체를 점수로 쓴다. 그것이 **`inertia_`** = SSE(Sum of Squared Errors) — 모든 학생에 대해 "자기 그룹 중심점까지 거리²"를 더한 값이다. 작을수록 각 그룹이 중심 둘레에 촘촘히 모였다는 뜻이다.

문제는 SSE가 K를 늘리면 **무조건 줄어든다**는 것이다(K = 387이면 학생마다 중심점이 하나씩이라 0). 그래서 최솟값이 아니라 **줄어드는 속도가 꺾이는 지점(엘보우, 팔꿈치)** 을 고른다. 이 노트에서 돌린 값(`random_state=42`)은 이렇다.

| K | SSE | 직전 K보다 줄어든 양 | 실루엣 |
| --- | --- | --- | --- |
| 1 (참고 — 전체 분산) | 1935.0 | | |
| 2 | 1238.7 | 696 | 0.320 |
| 3 | 1027.0 | 212 | 0.262 |
| 4 | 862.7 | 164 | 0.262 |
| **5** | **727.0** | **136** | **0.283** |
| 6 | 620.4 | 107 | 0.274 |
| 7 | 544.7 | 76 | 0.280 |
| 8 | 482.3 | 62 | 0.284 |
| 9 | 441.7 | 41 | 0.289 |
| 10 | 417.0 | 25 | 0.279 |
| 11~19 | 381 → 248 | 10~36 | 0.28~0.31 |

K=2에서 3으로 가며 700 → 212로 한 번 크게 꺾이고, 그 뒤 5~10 사이에서 줄어드는 양이 136 → 25로 완만해진다. 수업 주석의 "엘보우 5~10"이 이 구간이다. 엘보우는 **눈으로 읽는 기준**이라 사람마다 3이라 할 수도, 5라 할 수도 있다 — 그래서 주석이 두 번째 기준을 함께 적어 두었다.

**실루엣(silhouette)** 은 주석에만 있고 코드에는 없는데, 뜻은 "각 점이 **자기 그룹 안의 점들과는 얼마나 가깝고, 가장 가까운 다른 그룹과는 얼마나 먼가**"를 −1~1로 잰 값이다. 1에 가까우면 그룹이 서로 뚜렷이 떨어졌고, 0 근처면 경계가 흐리고, 음수면 다른 그룹에 더 가까운 점이 많다는 뜻. `sklearn.metrics.silhouette_score(X_train_scaled, preds)`로 구한다. 이 자료에서는 K=2가 0.32로 가장 높고 나머지는 0.26~0.31에서 평평하다 — 다섯 열 안에서 학생들이 **뚜렷한 덩어리로 갈라지지 않는** 자료라는 뜻이다(실루엣 0.5 이상이 "확실히 갈린다"로 읽힌다). SSE는 "안으로 뭉침"만, 실루엣은 "밖과의 거리"까지 보니 둘을 같이 놓고 읽는 것이 주석의 "두 차트 해석하여 최적의 K 해석"이다.

### 1-7. 최적 K로 다시 군집하기

```python
best_model = KMeans(n_clusters=5)
pred = best_model.fit_predict(X_train_scaled)
print(pred[:10])
```

엘보우 구간의 앞쪽 5를 골라 **모델을 다시 만들어** 학습한다 — 1-6 반복문 안의 모델들은 루프 변수에 덮어써져 사라졌으니 최종 모델은 따로 세운다. `fit_predict`는 `fit` 뒤 `labels_`를 돌려주는 한 줄 판으로, `fit_transform`과 같은 발상이다. K=5의 중심점을 원 단위로 되돌려 보면(이 노트) K=3보다 결이 하나 더 보인다.

| 그룹 | 인원 | 공부시간 | 결석 | G1 | G2 | G3 | 읽는 법 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0 | 49 | **3.43** | 3.8 | 10.2 | 10.4 | 9.8 | 공부 시간은 많은데 성적은 중간 |
| 1 | 37 | 1.78 | **23.2** | 10.2 | 9.6 | 9.6 | **결석이 아주 많은** 학생 |
| 2 | 56 | 1.75 | 2.6 | 7.0 | 4.9 | 2.3 | 성적 급락·이탈층 (K=3의 C) |
| 3 | 133 | 1.65 | 4.4 | 9.7 | 10.1 | 10.3 | 평균적인 중간층 |
| 4 | 112 | 2.13 | 3.9 | 14.9 | 14.9 | 15.1 | 상위층 (K=3의 B) |

K=3에서 187명이던 "중간층"이 **공부 많이 하는데 중간**(49) · **결석 많은 중간**(37) · **그냥 중간**(133)으로 갈라졌다. K를 올린다는 것은 이렇게 큰 덩어리를 더 잘게 나누는 일이고, 어디서 멈출지는 SSE 곡선과 "나눈 그룹이 말이 되는가"를 같이 보고 정한다.

### 1-8. `HDBSCAN` — K를 정하지 않는 밀도 기반 군집

```python
from sklearn.cluster import HDBSCAN
model = HDBSCAN(min_cluster_size=15, min_samples=5)
pred = model.fit_predict(X_train_scaled)
print(pred)   # 0, 1, 2, 3 … 그리고 -1
```

마지막 다섯 줄은 군집의 다른 갈래, **밀도 기반**이다. KMeans는 "그룹 K개를 반드시 만들고 모든 점을 어딘가에 넣는다"는 모델인데, HDBSCAN(Hierarchical Density-Based Spatial Clustering of Applications with Noise)은 **점이 빽빽하게 모인 곳**을 그룹으로 보고, 어디에도 빽빽하지 않은 점은 **노이즈(-1)** 로 남겨 둔다. 그래서 그룹 수 K가 입력이 아니라 **출력**이고, 대신 "그룹으로 인정할 최소 인원"을 준다.

| 인자 | 뜻 | 수업 값 |
| --- | --- | --- |
| `min_cluster_size` | 이보다 작은 뭉침은 그룹으로 인정하지 않는다 | 15 |
| `min_samples` | 한 점이 "빽빽한 곳에 있다"고 보려면 반경 안에 이웃이 몇 개여야 하나 — 클수록 보수적이고 노이즈가 늘어난다 | 5 |

이 노트에서 돌린 결과는 그룹 **4개 + 노이즈 46명**이고, 그룹별 평균을 보면 KMeans와 전혀 다른 기준으로 갈라졌다.

| 라벨 | 인원 | 공부시간 | 결석 | G1 | G2 | G3 |
| --- | --- | --- | --- | --- | --- | --- |
| 3 | 85 | **1.00** | 5.5 | 11.0 | 11.4 | 11.5 |
| 2 | 180 | **2.00** | 5.0 | 10.8 | 10.8 | 10.4 |
| 1 | 56 | **3.00** | 3.8 | 12.4 | 12.4 | 12.6 |
| 0 | 20 | **4.00** | 4.6 | 11.8 | 12.0 | 12.2 |
| −1 (노이즈) | 46 | 2.11 | 11.6 | 9.3 | 6.9 | 5.0 |

`studytime`이 1·2·3·4 **정수 네 값뿐**이라, 표준화된 공간에서 학생들은 공부 시간 축으로 네 개의 얇은 판에 깔려 있다. 밀도 기반 알고리즘에게는 그 판 하나하나가 "빽빽한 곳"이라 HDBSCAN이 공부 시간 등급 그대로 네 그룹을 돌려준 것이다 — 이산값 열이 섞여 있을 때 밀도 기반이 보이는 전형적인 모습이다. 그리고 KMeans가 "성적 급락 그룹"으로 묶었던 `G3=0` 학생들과 결석 20일 이상 학생들은 어느 판에도 빽빽하지 않아 **노이즈 46명**에 들어갔다(노이즈의 G3 중앙값 0, 결석 평균 11.6). KMeans는 이들을 반드시 어딘가에 넣고, HDBSCAN은 "이상치"라고 따로 떼어 준다 — 같은 자료에서 두 알고리즘이 보는 구조가 이렇게 다르다.

인자를 바꿔 보면(이 노트) `min_cluster_size=5`에서는 작은 뭉침까지 인정해 8그룹, `30`이면 20명짜리 `studytime=4` 판이 그룹 자격을 잃어 3그룹 + 노이즈 66명, `min_samples=15`로 올리면 노이즈가 121명까지 늘어난다. "몇 명부터 그룹인가"를 사람이 정하는 것이라, K 대신 이 두 인자가 HDBSCAN의 하이퍼파라미터다.

### 1-9. 흐름 한 장

```
읽기(sep=';') → 특성 5열만 (타깃 없음) → train_test_split(X) 둘만 반환 (98 : 2)
   → StandardScaler fit(학습)·transform(둘)          ← 거리 계산이라 필수
   → KMeans(n_clusters=3).fit → predict → 그룹 번호(뜻은 cluster_centers_에서)
   → scatter(G3, absences, c=labels) 2D로 눌러 보기
   → for k in 2~19: KMeans(k).fit_predict → inertia_ 모아 엘보우 (+ 실루엣)
   → KMeans(n_clusters=5).fit_predict 최종
   → HDBSCAN(min_cluster_size, min_samples).fit_predict → 그룹 + 노이즈(-1)
```

## 2. 추가로 알면 좋은 활용법

### 2-1. `random_state`·`n_init` — 결과를 고정하고 초기화 운을 줄이기

KMeans는 초기 중심점에 따라 다른 지역 최적해에 멈출 수 있다. `random_state=42`를 주면 번호와 결과가 고정되고, `n_init=10`을 주면 초기화를 열 번 바꿔 돌려 **SSE가 가장 작은 결과**를 고른다(사이킷런 1.4부터 기본값 `'auto'`는 k-means++ 초기화에서 1회). 엘보우 반복문에서 K마다 `random_state`를 고정하는 것은 곡선이 초기화 운으로 들쭉날쭉해지지 않게 하기 위한 것이다.

### 2-2. 그룹에 이름 붙이기 — 중심점 역변환과 그룹별 요약

```python
centers = pd.DataFrame(ss.inverse_transform(model.cluster_centers_), columns=X.columns)
summary = X_train.assign(cluster=train_labels).groupby('cluster').agg(['mean', 'count'])
```

`cluster_centers_`는 표준화된 좌표라 그대로는 읽기 어렵다. 스케일러의 `inverse_transform`으로 원 단위에 되돌리거나, 원본 DataFrame에 라벨 열을 붙여 `groupby`로 평균·인원을 보면 1-4·1-7의 표가 바로 나온다. 군집 결과를 보고서에 쓸 때는 "그룹 2"가 아니라 "성적 급락·결석 적음 그룹(67명)"처럼 **중심점에서 읽은 이름**으로 부른다.

### 2-3. 실루엣 코드와 두 지표를 한 그림에

```python
from sklearn.metrics import silhouette_score
sil_list = []
for k in range(2, 20):
    km = KMeans(n_clusters=k, random_state=42, n_init=10)
    labels = km.fit_predict(X_train_scaled)
    sse_list.append(km.inertia_)
    sil_list.append(silhouette_score(X_train_scaled, labels))   # K=1은 정의되지 않아 2부터
fig, ax = plt.subplots(1, 2, figsize=(10, 4))
ax[0].plot(range(2, 20), sse_list, marker='o'); ax[0].set_title('SSE (elbow)')
ax[1].plot(range(2, 20), sil_list, marker='o'); ax[1].set_title('silhouette')
```

주석에만 있던 실루엣을 같은 반복문에 넣으면 두 곡선이 한 번에 나온다. `silhouette_samples`로 점마다의 값을 꺼내 그룹별로 막대를 그린 **실루엣 그림**도 자주 쓰는 진단이다 — 폭이 좁고 음수가 섞인 그룹은 경계가 흐린 그룹이다. 비슷한 역할의 지표로 `calinski_harabasz_score`(클수록 좋음)·`davies_bouldin_score`(작을수록 좋음)가 있다.

### 2-4. `Pipeline`으로 묶고, 새 학생 배정하기

```python
from sklearn.pipeline import Pipeline
pipe = Pipeline([('scaler', StandardScaler()), ('km', KMeans(n_clusters=5, random_state=42, n_init=10))])
pipe.fit(X_train)                       # 원본 DataFrame 그대로
new = pd.DataFrame([{'studytime': 2, 'absences': 30, 'G1': 10, 'G2': 9, 'G3': 9}])
pipe.predict(new)                       # 표준화 → 가장 가까운 중심점 번호
```

day14에서 배운 파이프라인은 군집에도 똑같이 쓰인다. 스케일러와 KMeans를 묶어 두면 새 학생을 넣을 때 `transform`을 잊을 일이 없고, `joblib.dump`로 통째 저장해 서빙할 수도 있다(day16 FastAPI 노트의 `.pkl` 자리에 그대로 들어간다). 위 예시 학생은 결석 30일이라 K=5의 "결석 많은 그룹"에 떨어진다.

### 2-5. 군집 결과를 지도학습의 특성으로

군집 번호는 그 자체로 끝이 아니라 **새 특성**이 되기도 한다. 학생 그룹을 원-핫으로 바꿔 성적 예측 모델에 넣거나, 거꾸로 `G3`를 타깃으로 떼고 나머지 네 열로 군집한 뒤 "그룹별 G3 분포"를 보면 군집이 성적과 얼마나 맞물리는지 확인할 수 있다 — 정답이 있는 열 하나를 숨겨 두고 군집의 쓸모를 재는 방법이다. `make_blobs`로 정답이 있는 가짜 군집 자료를 만들어 `adjusted_rand_score`로 비교해 보는 것도 알고리즘 감을 잡는 데 좋다.

### 2-6. 그래프의 두 축을 고르는 다른 방법 — PCA

1-5에서 다섯 열 중 둘을 골라 그린 산점도는 나머지 셋을 버린다. `PCA(n_components=2)`로 다섯 열을 **분산이 가장 큰 두 방향**으로 눌러 그리면 다섯 열의 정보를 최대한 살린 2D 그림이 된다 — `pca.fit_transform(X_train_scaled)` 결과의 두 열을 `scatter`에 넣고 `c=labels`로 색을 주는 식이다. 수업 용어표의 "주성분"이 이것이고, 다음 수업에서 다룰 가능성이 큰 도구다.

## 3. 더 나아가 알면 좋은 것

### 3-1. KMeans의 가정과 한계

KMeans는 그룹이 **둥글고(구형) 크기가 비슷하다**고 가정한다. 길쭉한 띠 모양, 동심원, 밀도가 크게 다른 그룹에서는 중심점 거리만으로 자르니 엉뚱하게 갈린다 — 그런 자료에 밀도 기반(DBSCAN·HDBSCAN)이나 `AgglomerativeClustering`(계층 군집, 덴드로그램), `GaussianMixture`(각 그룹을 타원형 정규분포로 두고 소속 **확률**을 준다 — KMeans의 소프트 버전)를 쓴다. 이상치에도 민감하다 — 결석 75일 한 명이 중심점을 끌어당기므로 `RobustScaler`나 사전 제거를 생각해 볼 만하다. 범주형 열은 유클리드 거리가 성립하지 않아 k-modes·k-prototypes 같은 변형이 따로 있다.

### 3-2. 밀도 기반의 계보 — DBSCAN → HDBSCAN

`DBSCAN(eps, min_samples)`은 "반경 `eps` 안에 이웃이 `min_samples`개 이상이면 핵심점"이라는 규칙으로 그룹을 키우는데, `eps` 하나를 모든 그룹에 똑같이 쓰기 때문에 밀도가 다른 그룹을 동시에 잡기 어렵다. HDBSCAN은 `eps`를 모든 값으로 바꿔 가며 생기는 **군집 계층 구조**를 만들고 그중 가장 오래 살아남는 그룹을 고르므로 `eps`를 안 받는다. 사이킷런 1.3에 들어왔고(`sklearn.cluster.HDBSCAN`), `probabilities_`로 각 점의 소속 확신도를 주며, 새 점 배정은 `predict`가 없어 `approximate_predict`(원 `hdbscan` 패키지)나 가장 가까운 그룹 중심 찾기로 대신한다.

### 3-3. 비지도학습의 다른 갈래

군집 말고도 **차원 축소**(PCA·t-SNE·UMAP — 시각화와 노이즈 제거), **이상 탐지**(`IsolationForest`·`LocalOutlierFactor` — HDBSCAN의 노이즈처럼 "다른 점과 동떨어진 것" 찾기), **토픽 모델링**(LDA — 문서 묶음에서 주제 찾기), **연관 규칙**(장바구니 분석)이 비지도학습이다. 고객 세분화(RFM + KMeans), 추천 시스템의 사용자 그룹, 이미지 색상 양자화(픽셀 색을 K개로 묶기)가 KMeans의 대표 쓰임이다.

### 3-4. 다음에 볼 키워드

- `silhouette_score`·`silhouette_samples` — K 선택 두 번째 기준과 실루엣 그림
- `PCA(n_components=2)` — 다차원 군집 결과를 2D로 눌러 보기 (수업 용어표의 "주성분")
- `MiniBatchKMeans` — 자료가 수십만 행일 때 표본 묶음으로 빠르게
- `GaussianMixture` — 소속 확률을 주는 KMeans의 확률 버전
- `AgglomerativeClustering`·`dendrogram` — 계층 군집
- `DBSCAN`·`HDBSCAN(probabilities_)` — 밀도 기반과 노이즈
- `adjusted_rand_score`·`normalized_mutual_info_score` — 정답이 있을 때 군집 평가
- `IsolationForest` — 이상 탐지

## 실습 파일

- `KDT_2026/2026_Python/day19/s-13.py` — 지도/비지도 요약 주석 → `pd.read_csv(URL, sep=';')`(UCI 학생 성적 395 × 33) → `X = df[['studytime', 'absences', 'G1', 'G2', 'G3']]`(타깃 없음) → `train_test_split(X, test_size=0.02, random_state=42)` 둘만 반환(387 / 8) → `StandardScaler` `fit_transform`(학습)·`transform`(테스트) → `KMeans(n_clusters=3).fit` → `predict` 앞 10명·테스트 8명 → `scatter(G3, absences, c=labels)` + 테스트 빨간 별 → `for k in range(2, 20)` `KMeans(k, random_state=42).fit_predict` → `inertia_` 리스트 → 엘보우 `plot` → `KMeans(n_clusters=5).fit_predict` → `HDBSCAN(min_cluster_size=15, min_samples=5).fit_predict`

## 관련 노트

[[AI 정리본 인덱스]] · [[AI day18 LightGBM·Optuna 의료비 회귀 연습문제 풀이]] · [[AI day12 사이킷런 단순 선형 회귀로 물고기 무게 예측]] · [[AI day13 StandardScaler 표준화와 릿지·라쏘 규제]] · [[AI day14 사이킷런 Pipeline으로 다항·표준화·회귀 묶기]] · [[KDT_2026 학습 지도]]
