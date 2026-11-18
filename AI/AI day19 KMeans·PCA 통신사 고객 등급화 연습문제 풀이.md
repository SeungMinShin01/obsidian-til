---
출처: Claude 분석
원본: KDT_2026/2026_Python/ML_practice/practice7.py
작성일: 2026-11-18
tags: [학습, ai, python]
---

# AI day19 — KMeans·PCA 통신사 고객 등급화 연습문제 풀이

> 실습 파일: `ML_practice/practice7.py`
> 허브: [[AI 정리본 인덱스]] · 이전: [[AI day19 PCA 주성분 분석으로 차원 축소와 주성분 가중치 읽기]] · 다음: (아직 없음)

`s-13.py`에서 학생 성적으로 밟은 "표준화 → 엘보우·실루엣 → KMeans → PCA → 그룹별 평균으로 등급 라벨링 → PCA 산점도"를 **통신사 고객 자료**로 처음부터 다시 쓰는 연습이다. 지시문은 여섯 단계이고, 자료가 바뀌면서 달라지는 것은 세 가지뿐이다 — 열이 다섯이 아니라 **셋**(`tenure`·`MonthlyCharges`·`TotalCharges`), 자료가 395명이 아니라 **7,032명**, 그리고 군집 알고리즘이 HDBSCAN이 아니라 **KMeans 하나**라 노이즈(−1)가 없다. 그 세 가지가 어디서 코드를 바꾸는지 따라가며 적는다. 숫자는 수업 주석의 값과 이 노트에서 다시 돌린 값(scikit-learn 1.9)을 같이 둔다 — `random_state`를 안 준 KMeans라 번호와 인원이 조금씩 다른데, 그 차이 자체가 이 노트의 한 주제다.

## 1. 배운 내용

### 1-1. 자료 준비 — `to_numeric(errors='coerce')`와 `dropna(subset=)`

```python
url = 'https://raw.githubusercontent.com/IBM/telco-customer-churn-on-icp4d/master/data/Telco-Customer-Churn.csv'
df = pd.read_csv(url)
df['TotalCharges'] = pd.to_numeric(df['TotalCharges'], errors='coerce')
df = df.dropna(subset=['TotalCharges'])
X = df[['tenure', 'MonthlyCharges', 'TotalCharges']]
```

IBM의 통신사 이탈(churn) 자료 7,043명 × 21열에서 세 열만 쓴다. 지시문 밖에 미리 적혀 있는 두 줄이 이 자료의 함정을 말해 준다.

| 열 | 뜻 | 범위(이 노트) |
| --- | --- | --- |
| `tenure` | 가입 기간(개월) | 1 ~ 72, 평균 32.4 |
| `MonthlyCharges` | 월 요금(달러) | 18.25 ~ 118.75, 평균 64.8 |
| `TotalCharges` | 누적 청구액(달러) | 18.8 ~ 8,684.8, 평균 2,283 |

`TotalCharges`는 CSV에서 **문자열(`object`)로 읽힌다.** 가입 첫 달이라 청구액이 아직 없는 고객 11명이 숫자 대신 빈칸(공백 한 칸)으로 들어 있어서 열 전체가 문자열이 된 것이다. `pd.to_numeric(errors='coerce')`는 숫자로 못 바꾸는 값을 **오류 대신 `NaN`으로** 돌려주고(day08 `to_datetime(errors='coerce')`와 같은 인자), 이어서 `dropna(subset=['TotalCharges'])`가 그 11행만 지워 7,032명이 남는다. `subset=`이 없으면 다른 열의 `NaN`까지 보고 지우니 열을 지정하는 습관이 안전하다. 세 열의 `corr()`를 찍어 보면 `tenure`–`TotalCharges`가 0.83, `MonthlyCharges`–`TotalCharges`가 0.65다 — 누적 청구액은 대략 "기간 × 월 요금"이라 두 열의 정보를 거의 담고 있고, 이 겹침이 4단계 PCA에서 그대로 드러난다.

### 1-2. 단계 1 — `StandardScaler().fit_transform(X)`, 분할 없이 전부

```python
ss = StandardScaler()
X_scaled = ss.fit_transform(X)
```

지시문 그대로 **표준화 한 줄**이다. 개월(1~72)과 달러(18~8,684)는 단위가 달라, 그대로 거리를 재면 `TotalCharges` 하나가 군집을 다 정해 버린다(`s-13.py`에서 결석일수가 공부시간을 덮던 것과 같은 이유). `s-13.py`와 다른 점은 `train_test_split`이 **없다**는 것 — 비지도학습이라 테스트로 점수를 낼 일이 없고 수업에서도 2 %를 "새 학생 견본"으로만 썼으니, 이 연습은 7,032명 전부를 한 번에 군집한다. 그래서 변수 이름도 `X_train_scaled`가 아니라 `X_scaled`다.

### 1-3. 단계 2 — 엘보우 SSE와 실루엣을 같은 반복문에서, `range(2, 11)`

```python
sse_list = []
sil_list = []
for k in range(2, 11):
    k_teamp = KMeans(n_clusters=k, random_state=42)
    preds = k_teamp.fit_predict(X_scaled)
    sse_list.append(k_teamp.inertia_)
    sil_list.append(silhouette_score(X_scaled, preds))
plt.plot(range(2, 11), sse_list, marker='o'); plt.show()
plt.plot(range(2, 11), sil_list, marker='o'); plt.show()
```

`s-13.py` 4단계와 글자 하나까지 같은 틀이고 범위만 2~19에서 **2~10**으로 줄었다 — 고객을 열 등급 넘게 나눌 일은 없다는 판단이 범위에 들어 있다. 두 곡선을 이 노트에서 돌린 값으로 표에 두면 이렇다.

| K | SSE(`inertia_`) | 줄어든 양 | 실루엣 |
| --- | --- | --- | --- |
| 2 | 9,701 | — | **0.480** |
| 3 | 6,599 | 3,102 | 0.432 |
| 4 | **4,145** | 2,454 | **0.472** |
| 5 | 3,110 | 1,035 | 0.445 |
| 6 | 2,791 | 319 | 0.421 |
| 7 | 2,251 | 540 | 0.424 |
| 8 | 1,941 | 310 | 0.413 |
| 10 | 1,419 | 220 | 0.431 |

SSE는 K=4까지 2,000~3,000씩 뚝뚝 떨어지다가 K=5부터 1,000 아래로 완만해진다 — 엘보우가 **4 근처**다. 실루엣은 K=2가 0.48로 가장 높고 K=4가 0.47로 두 번째인데, 학생 자료(0.26~0.32)보다 전체가 높다. 열이 셋뿐이고 `tenure`·`TotalCharges`가 강하게 상관해 점들이 띠보다는 덩어리에 가깝기 때문이다. 두 곡선을 같이 읽으면 "K=2는 너무 거칠고(장기 vs 신규 둘로만), SSE가 꺾이는 자리에서 실루엣이 다시 오르는 **K=4**"가 자연스럽다. 3단계의 `n_clusters=4`가 이 판단이다. `silhouette_score`는 7,032 × 7,032 거리를 다 재니 K 하나에 1초 남짓 걸린다 — 범위를 좁힌 또 하나의 이유다.

### 1-4. 단계 3 — `KMeans(n_clusters=4)` 최종 군집과 `cluster` 열

```python
best_model = KMeans(n_clusters=4)
pred = best_model.fit_predict(X_scaled)
print(pred[:10])                 # [1 3 1 3 0 0 0 1 0 3]
X['cluster'] = pred
print(X['cluster'].value_counts())
# cluster
# 0    2279
# 2    1902
# 1    1695
# 3    1156
```

`fit_predict`로 7,032명의 그룹 번호를 받아 `X['cluster']` 열로 붙이고 `value_counts()`로 인원을 센다 — `s-13.py` 5단계에서 HDBSCAN 라벨을 `hdb_cluster` 열로 붙이던 패턴 그대로다. `X`는 `df[[...]]`로 잘라낸 표라 열을 붙일 때 `SettingWithCopyWarning`이 뜰 수 있는데, 미리 `X = df[[...]].copy()`로 받아 두면 조용하다(앞 노트와 같은 주의).

여기서 **`random_state`가 없다**는 점이 결과를 바꾼다. 수업 주석의 인원은 2279 · 1902 · 1695 · 1156인데, 이 노트에서 `random_state=42`로 돌리면 2269 · 1915 · 1695 · 1153이다. 네 묶음의 **크기는 거의 같고 번호만 다르다** — 초기 중심점이 달라 경계의 열 명 남짓이 옆 그룹으로 넘어갔고, 번호는 애초에 뜻이 없어 순서가 섞였다. 그룹의 **정체**는 번호가 아니라 중심점으로 읽어야 하고, 이 노트에서 `ss.inverse_transform(best_model.cluster_centers_)`로 원 단위로 되돌리면 이렇다.

| 그룹(이 노트 번호) | 인원 | 가입 기간 | 월 요금 | 누적 청구액 | 읽는 법 |
| --- | --- | --- | --- | --- | --- |
| 1 | 1,695 | **10개월** | **32달러** | 304 | 신규·저요금 |
| 3 | 2,269 | 15개월 | 81달러 | 1,249 | 신규·고요금 |
| 2 | 1,153 | 54개월 | 35달러 | 1,825 | 장기·저요금 |
| 0 | 1,915 | **59개월** | **93달러** | 5,537 | 장기·고요금 |

기간(길다/짧다) × 요금(높다/낮다) **2 × 2 사분면**이 그대로 네 그룹이다. 수업 번호로는 `1`이 신규·저요금(1,695명으로 인원이 똑같다), `0`이 신규·고요금, `3`이 장기·저요금, `2`가 장기·고요금에 해당한다 — 5단계의 평균 순서로 확인된다.

### 1-5. 단계 4 — `PCA(n_components=2)`와 `components_.T` 읽기, `PC1`·`PC2` 열

```python
pca = PCA(n_components=2)
X_pca = pca.fit_transform(X_scaled)
print('행 마다의 가중치 : ', X_pca)        # (7032, 2)
print('주 특성별 가중치 :', pca.components_.T)
# [[ 0.56721122 -0.60697524]  'tenure'
#  [ 0.48571362  0.79237469]  'MonthlyCharges'
#  [ 0.66509677 -0.06101971]] 'TotalCharges'
X['PC1'] = X_pca[:, 0]
X['PC2'] = X_pca[:, 1]
```

3차원을 2차원으로 줄이는 것이라 학생 자료(5 → 2)보다 버리는 것이 적다. 이 노트에서 `explained_variance_ratio_`를 찍으면 **0.727 + 0.254 = 0.980** — 축 둘이 분산의 98 %를 담아, 2D 산점도가 거의 원본 그대로다(학생 자료는 75.8 %였다). 수업 주석의 가중치는 이 노트에서 돌린 값과 소수 여덟 자리까지 같다(PCA는 결정적 계산).

| 원래 열 | PC1 | PC2 | 읽는 법 |
| --- | --- | --- | --- |
| `tenure` | 0.57 | **−0.61** | PC2 음의 방향 |
| `MonthlyCharges` | 0.49 | **+0.79** | PC2 양의 방향 |
| `TotalCharges` | **0.67** | −0.06 | PC1 |

PC1은 세 열 **모두 양수**(0.49~0.67)다. 셋 다 커지는 방향 — 오래 쓰고, 많이 내고, 그래서 누적액이 큰 — "**고객 가치 축**"이고, 누적 청구액이 가장 크게 실린다. PC2는 `MonthlyCharges` +0.79와 `tenure` −0.61로 부호가 반대라 "**월 요금은 높은데 기간은 짧은**" 쪽이 양의 방향 — 신규 고요금 vs 장기 저요금을 가르는 축이다. 1-4의 2 × 2 사분면이 두 축으로 다시 보인다 — PC1이 왼쪽(신규·저요금 304달러)에서 오른쪽(장기·고요금 5,537달러)으로 가치를 늘어놓고, PC2가 그 중간의 두 그룹(신규·고요금 vs 장기·저요금)을 위아래로 가른다. 이 노트의 그룹별 PC 평균이 그 읽기와 맞는다: 신규·저요금 (−1.63, −0.27), 신규·고요금 (−0.44, **+0.87**), 장기·저요금 (−0.13, **−1.30**), 장기·고요금 (**+2.04**, −0.01).

학생 자료에서는 PC1이 "성적 축"이고 PC2가 그와 무관한 "생활 축"이었는데, 여기서는 PC2가 **같은 두 열의 차이**다. 열이 셋뿐이고 서로 상관하니 PCA가 "합"과 "차"로 축을 짠 셈이다 — `components_.T`의 부호 패턴(같은 부호 = 합, 반대 부호 = 차)을 읽는 연습으로 두 자료를 나란히 두면 좋다.

### 1-6. 단계 5 — 군집별 `TotalCharges` 평균을 오름차순으로

```python
cluster_means = X.groupby('cluster')['TotalCharges'].mean()
sorted_cluster = cluster_means.sort_values(ascending=True)
print(sorted_cluster)
# cluster
# 1     303.578466
# 0    1257.585257
# 3    1831.250389
# 2    5551.335936
```

`s-13.py` 7단계와 같은 `groupby → mean → sort_values`인데, 이번에는 **`!= -1` 필터가 없다.** KMeans는 모든 점을 어딘가에 넣으니 노이즈가 없고, 그래서 뺄 행도 없다 — HDBSCAN이었다면 그 한 줄이 먼저 와야 한다. 집계 열은 성적 `G3` 대신 **누적 청구액**이다. "매출 기여도가 낮은 군집부터"라는 지시문이 `ascending=True`로 들어갔고, 결과 304 → 1,258 → 1,831 → 5,551달러가 1-4 표의 읽기(신규·저 → 신규·고 → 장기·저 → 장기·고)와 정확히 같다. 이 노트에서는 번호가 1 → 3 → 2 → 0 순으로 304 → 1,249 → 1,825 → 5,537 — 번호는 다르지만 **정렬된 순서의 정체는 같다**.

### 1-7. 단계 5·6의 나머지 — `s-13.py` 8·9단계를 그대로 옮기면

파일에는 단계 5의 둘째·셋째 지시(`label_map` 자동 생성 → `replace`)와 단계 6(등급별 PCA 산점도)이 지시문만 적혀 있다. `s-13.py` 8·9단계와 같은 꼴이라 그 흐름대로 쓰면 이렇게 된다 — 이상치 줄만 빠진다.

```python
label_map = {}
for idx, cluster_id in enumerate(sorted_cluster.index, start=1):
    label_map[cluster_id] = f'Grade{idx}'
# 이 노트: {1: 'Grade1', 3: 'Grade2', 2: 'Grade3', 0: 'Grade4'}
# 수업 번호로는 {1: 'Grade1', 0: 'Grade2', 3: 'Grade3', 2: 'Grade4'}
X['cluster_label'] = X['cluster'].replace(label_map)

for lbl in label_map.values():
    sub = X[X['cluster_label'] == lbl]
    plt.scatter(sub['PC1'], sub['PC2'], marker='o', label=lbl)
plt.legend(); plt.show()
```

| `s-13.py` 8·9단계 | 이 연습 |
| --- | --- |
| `labels[-1] = 'Outlier'` 한 줄 추가 | 없음 — KMeans는 노이즈가 없다 |
| `if lbl == 'Outlier'`로 빨간 별 분기 | 없음 — 네 등급 전부 `marker='o'` |
| `Level1~3` (성적 하 → 상) | `Grade1~4` (매출 기여 하 → 상) |

`enumerate(start=1)`로 **정렬된 순서가 곧 등급 번호**가 되니, `random_state` 때문에 군집 번호가 바뀌어도 `Grade1`은 늘 신규·저요금, `Grade4`는 늘 장기·고요금이다 — 1-4에서 본 "번호는 다르고 정체는 같다"를 라벨링이 흡수한다. 이것이 번호를 손으로 적지 않고 `enumerate`로 만드는 이유다. 산점도에서는 Grade1 → Grade4가 PC1 축을 따라 왼쪽에서 오른쪽으로 놓이고, Grade2(신규·고요금)는 위쪽·Grade3(장기·저요금)는 아래쪽으로 PC2 방향에서 갈린다.

### 1-8. 흐름 한 장 — 학생 자료와 나란히

```
                 s-13.py (학생 395명 × 5열)              practice7.py (고객 7,032명 × 3열)
자료 준비        sep=';'  ·  train_test_split 2 %         to_numeric(coerce) · dropna(subset) · 분할 없음
1 표준화         StandardScaler fit_transform/transform    fit_transform 한 번
2 최적 K         range(2, 20) SSE + 실루엣                 range(2, 11) 같은 틀, 엘보우 4
3 군집           KMeans(5) → HDBSCAN(30, 10) 노이즈 −1    KMeans(4), 노이즈 없음, value_counts
4 PCA            5 → 2, 75.8 %, PC1 성적·PC2 생활         3 → 2, 98 %, PC1 가치·PC2 요금−기간
5 그룹 평균      != -1 제외 → groupby G3 → 오름차순        제외 없음 → groupby TotalCharges → 오름차순
   라벨링        enumerate → Level1~3 + Outlier → replace   enumerate → Grade1~4 → replace
6 산점도         등급별 scatter + Outlier 빨간 별            등급별 scatter (별 없음) + legend
```

## 2. 추가로 알면 좋은 활용법

### 2-1. `random_state`를 주고 중심점으로 그룹을 확인하기

```python
best_model = KMeans(n_clusters=4, random_state=42, n_init=10)
centers = pd.DataFrame(ss.inverse_transform(best_model.cluster_centers_), columns=X.columns[:3]).round(1)
print(centers)
```

1-4의 차이가 보여 주듯 `random_state`가 없으면 돌릴 때마다 번호와 경계 인원이 바뀐다. 보고서에 숫자를 적을 거면 씨앗을 고정하고, 번호 대신 **중심점을 원 단위로 되돌린 표**로 그룹을 설명하는 편이 안전하다. `groupby('cluster')[['tenure', 'MonthlyCharges', 'TotalCharges']].mean()`도 같은 표를 준다(중심점은 표준화 공간의 평균이라 두 값이 거의 같다).

### 2-2. 등급을 이탈(`Churn`)과 맞대 보기 — 군집의 쓸모 확인

```python
X['Churn'] = df.loc[X.index, 'Churn']
pd.crosstab(X['cluster_label'], X['Churn'], normalize='index').round(3)
```

원본 21열 중 쓰지 않은 `Churn`(Yes/No)을 등급 옆에 붙이면 군집이 "뜻있는 묶음"인지 바로 보인다. 이 노트에서 돌리면 이탈률이 Grade1(신규·저요금) 24.8 % · **Grade2(신규·고요금) 48.3 %** · Grade3(장기·저요금) 5.0 % · Grade4(장기·고요금) 15.5 %다 — 월 요금은 높은데 기간이 짧은 그룹이 절반 가까이 떠나고, 오래 쓴 저요금 고객은 거의 남는다. 가격표만으로 나눈 군집이 이탈이라는 바깥 변수와 이렇게 맞물리면 "그룹에 뜻이 있다"고 말할 수 있다. `s-13.py` 마지막 주석의 "군집화한 결과 가지고 추후에 지도학습"이 이 자리다: `cluster_label`을 원-핫하거나 `category`로 바꿔 day17·18의 LightGBM 이탈 분류기에 **파생변수**로 넣는다. 단, 지도학습에 쓸 거면 군집도 훈련 세트로만 `fit`하고 테스트는 `predict`로 배정해야 누수가 없다(day14 `fit`/`transform` 분리와 같은 원칙).

### 2-3. 가중치의 겹침을 숫자로 — `explained_variance_ratio_`와 `corr()`

세 열의 `corr()`(0.83·0.65·0.25)와 PCA 98 %는 같은 말을 두 번 한 것이다. `TotalCharges ≈ tenure × MonthlyCharges`라서 셋째 열은 거의 파생값이고, 그래서 두 축이면 충분하다. 특성 설계 쪽에서 보면 `TotalCharges`를 빼고 `tenure`·`MonthlyCharges` 둘만으로 군집해도 사분면이 거의 같게 나온다 — 상관이 높은 열 하나를 빼는 것과 PCA로 접는 것의 차이를 비교해 볼 만하다.

### 2-4. 실루엣을 K마다 그림으로 — `silhouette_samples`

`silhouette_score`는 평균 하나지만 `silhouette_samples(X_scaled, preds)`는 **점마다의** 실루엣을 준다. 그룹별로 정렬해 가로 막대로 그린 실루엣 다이어그램을 K=2·4·5에 대해 나란히 보면, 평균이 비슷한 K끼리도 "한 그룹만 두껍고 나머지는 얇은지"가 보인다. 엘보우와 평균 실루엣이 애매할 때 결정을 돕는 세 번째 그림이다.

### 2-5. `Pipeline(scaler, kmeans)`로 새 고객 등급 매기기

```python
from sklearn.pipeline import Pipeline
pipe = Pipeline([('ss', StandardScaler()), ('km', KMeans(n_clusters=4, random_state=42, n_init=10))])
pipe.fit(X[['tenure', 'MonthlyCharges', 'TotalCharges']])
new = pd.DataFrame([[3, 85.0, 255.0], [60, 30.0, 1800.0]], columns=['tenure', 'MonthlyCharges', 'TotalCharges'])
[label_map[p] for p in pipe.predict(new)]   # ['Grade2', 'Grade3'] — 3개월·85달러는 신규·고요금, 60개월·30달러는 장기·저요금
```

표준화와 군집을 묶어 두면 새 고객 한 명도 `predict` → `label_map` 두 단계로 등급이 나온다. day18 연습의 서빙 주의(열 순서·열 이름)가 여기서도 그대로다.

## 3. 더 나아가 알면 좋은 것

### 3-1. RFM과 고객 세분화 — 이 연습이 흉내 낸 것

마케팅의 **RFM**(Recency 최근성 · Frequency 빈도 · Monetary 금액) 세분화가 이 연습의 원형이다. 통신사 자료에는 R·F가 없어 `tenure`(기간)·`MonthlyCharges`(단가)·`TotalCharges`(누적 금액) 셋으로 대신했고, "매출 기여도 순 등급"이 Monetary 축이다. 실무에서는 구매 로그에서 세 지표를 `groupby`로 만든 뒤 같은 흐름(표준화 → KMeans → 등급)을 돌린다 — 값이 한쪽으로 긴 꼬리를 가지면 `log1p` 변환을 표준화 앞에 끼운다.

### 3-2. 범주형 열까지 군집에 넣으려면 — k-prototypes·Gower 거리

원본 21열 대부분(계약 종류·인터넷 서비스·결제 방법)은 범주형이라 KMeans의 유클리드 거리에 바로 못 넣는다. 원-핫 뒤 KMeans는 거리가 왜곡되고, `category`를 아는 **k-prototypes**(수치는 거리·범주는 불일치 개수)나 Gower 거리 + 계층 군집이 그 자리다. 앞 노트 3-3의 "비지도학습 다른 갈래"가 여기서 구체화된다.

### 3-3. 군집 수를 데이터가 정하게 — GMM·BIC, HDBSCAN 다시

KMeans는 K를 사람이 고르지만, `GaussianMixture`는 K마다 **BIC/AIC**를 내어 가장 낮은 K를 고를 수 있고 소속 확률(`predict_proba`)까지 준다. 7,032명 자료에 `s-13.py`의 HDBSCAN을 돌리면 밀도 차이로 다른 그림이 나올 텐데, 그때는 1-6의 `!= -1` 줄과 1-7의 `Outlier` 분기가 다시 필요해진다 — 두 파일을 합치면 알고리즘을 바꿔도 되는 한 벌의 코드가 된다.

### 3-4. 다음에 볼 키워드

- RFM 세분화·`log1p` 변환 — 고객 가치 군집의 표준 틀
- `silhouette_samples`·실루엣 다이어그램 — K 결정의 세 번째 그림
- `crosstab(normalize='index')` — 군집과 라벨(이탈) 맞대기
- 군집 라벨을 파생변수로 — 누수 없이 `fit`/`predict` 분리
- k-prototypes·Gower 거리 — 범주형이 섞인 군집
- `GaussianMixture`·BIC — K를 지표로 고르기
- biplot — PC 좌표에 세 열의 가중치 화살표 겹치기

## 실습 파일

- `KDT_2026/2026_Python/ML_practice/practice7.py` — IBM Telco 고객 7,043명 CSV(URL) → `to_numeric(errors='coerce')`·`dropna(subset=['TotalCharges'])` 7,032명 → `tenure`·`MonthlyCharges`·`TotalCharges` 세 열 → 단계 1 `StandardScaler().fit_transform(X)` → 단계 2 `range(2, 11)` 반복문에서 `fit_predict`·`inertia_`·`silhouette_score` 두 리스트 → 선 그래프 두 장(엘보우 4) → 단계 3 `KMeans(n_clusters=4).fit_predict` → `X['cluster']`·`value_counts()`(2279 · 1902 · 1695 · 1156) → 단계 4 `PCA(n_components=2).fit_transform` → `components_.T`(PC1 셋 다 양수 0.49~0.67 가치 축, PC2 월 요금 +0.79 · 기간 −0.61) → `X['PC1']`·`['PC2']` → 단계 5 `groupby('cluster')['TotalCharges'].mean().sort_values(ascending=True)`(304 → 1,258 → 1,831 → 5,551달러) · 단계 5 라벨링·단계 6 산점도는 지시문 단계

## 관련 노트

[[AI 정리본 인덱스]] · [[AI day19 PCA 주성분 분석으로 차원 축소와 주성분 가중치 읽기]] · [[AI day19 KMeans 군집으로 학생 그룹 나누기와 엘보우·HDBSCAN]] · [[AI day13 StandardScaler 표준화와 릿지·라쏘 규제]] · [[AI day18 LightGBM·Optuna 의료비 회귀 연습문제 풀이]] · [[KDT_2026 학습 지도]]
