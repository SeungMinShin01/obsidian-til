---
출처: Claude 분석
원본: KDT_2026/2026_Python/practice/practice5.py
작성일: 2026-11-02
tags: [학습, python]
---

# Python day09 — 맷플롯립·시본 연습문제 풀이

> 실습 파일: `practice/practice5.py`
> 허브: [[Python 정리본 인덱스]] · 이전: [[Python day09 시본 범주 빈도·박스플롯·상관 히트맵]] · 다음: [[Python day09 타이타닉 생존 데이터 EDA 실습]]

day09에서 맷플롯립 다섯 차트(선·막대·산점도·히스토그램·박스플롯)와 시본 다섯 함수(`countplot`·`boxplot`·`heatmap`·`scatterplot`·`pairplot`)를 본 뒤, **같은 데이터프레임 하나로 열 가지 그림을 차례로 그리는** 연습문제다. 재료는 `np.random.seed(42)`로 고정해 만든 고객 200명 표 — 수치형 네 열(연령·월이용금액·구매건수·만족도점수)과 범주형 세 열(회원등급·주요결제수단·재구매여부)에 식별자 `고객ID`까지 여덟 열이다. 문제 1~5는 `plt.plot`·`plt.bar`·`plt.scatter`·`plt.hist`와 박스플롯으로 맷플롯립 쪽을, 문제 6~10은 `countplot`·`boxplot`·`heatmap`·`scatterplot`·`pairplot`으로 시본 쪽을 복습한다. 풀고 나면 "**열의 자료형 조합이 차트를 고른다**" — 수치 하나면 히스토그램·박스, 범주 하나면 카운트·막대, 범주+수치면 박스, 수치 둘이면 산점도, 수치 여럿이면 히트맵·페어플롯 — 이 열 문제를 꿰는 한 문장이 된다.

## 1. 배운 내용

### 1-1. 재료 만들기 — 난수 분포 네 가지와 f-문자열 ID

```python
np.random.seed(42)
n_samples = 200
common_data = {
    '고객ID': [f'USER_{i:03d}' for i in range(1, n_samples + 1)],
    '연령': np.random.randint(20, 60, size=n_samples),
    '월이용금액': np.random.normal(loc=150, scale=40, size=n_samples).round(1),
    '구매건수': np.random.poisson(lam=5, size=n_samples),
    '만족도점수': np.clip(np.random.normal(loc=75, scale=12, size=n_samples), 40, 100).round(1),
    '회원등급': np.random.choice(['Bronze', 'Silver', 'Gold', 'VIP'], size=n_samples, p=[0.4, 0.3, 0.2, 0.1]),
    '주요결제수단': np.random.choice(['신용카드', '간편결제', '계좌이체'], size=n_samples, p=[0.5, 0.35, 0.15]),
    '재구매여부': np.random.choice(['Yes', 'No'], size=n_samples, p=[0.7, 0.3])
}
df = pd.DataFrame(common_data)
```

| 열 | 함수 | 분포 | 뜻 |
| --- | --- | --- | --- |
| `연령` | `randint(20, 60)` | 균등 정수 (끝 미포함) | 20~59세 |
| `월이용금액` | `normal(150, 40)` | **정규** — 평균 150, 표준편차 40 | 단위 천 원 |
| `구매건수` | `poisson(lam=5)` | **포아송** — 평균 5회인 횟수 | 0 이상 정수 |
| `만족도점수` | `clip(normal(75, 12), 40, 100)` | 정규를 40~100으로 자름 | 점수 범위 보장 |
| 범주 세 열 | `choice([...], p=[...])` | 확률 가중 선택 | `p`의 합은 1 |

시본 노트에서 `randint`·`choice(p=)`로 100명을 만들던 방법에 **`normal`·`poisson`·`clip`** 세 가지가 더해졌다. 정규분포는 연속값(금액·점수)에, 포아송은 "일정 기간 동안 일어난 횟수"(구매 건수·방문 수)에 어울리는 분포라 데이터를 흉내 낼 때 이렇게 골라 쓴다. `np.clip(…, 40, 100)`은 판다스 `clip`과 같은 함수의 넘파이판으로, 정규분포가 만들 수 있는 100 초과·40 미만 값을 경계에 붙인다. `f'USER_{i:03d}'`의 `:03d`는 **세 자리 0 채움**(`USER_001`) 서식이다. `seed(42)`를 맨 앞에 두었으므로 누가 돌려도 같은 200행이 나오고, 그래서 아래 숫자들을 적어 둘 수 있다 — 결제수단은 신용카드 88·간편결제 75·계좌이체 37명, 회원등급은 Bronze 77·Silver 67·Gold 42·VIP 14명이다.

### 1-2. 문제 1 — 선 두 개를 한 축에, `plt.plot` 두 번

```python
top10 = df.head(10)
plt.figure(figsize=(8, 4))
plt.plot(top10.index, top10['월이용금액'], label='월이용금액', marker='o')
plt.plot(top10.index, top10['만족도점수'], label='만족도점수', marker='s')
plt.title('상위 10명 고객 지표 추이');  plt.xlabel('고객 인덱스');  plt.ylabel('값')
plt.legend();  plt.show()
```

맷플롯립 노트의 "선 차트 일곱 단계" 그대로다 — `figure` → `plot` 두 번 → 제목·축 이름 → `legend` → `show`. x축에 `top10.index`(0~9)를 넣었으므로 `df.head(10)`의 **인덱스가 그대로 눈금**이 된다. 두 선의 단위가 다른데(천 원 vs 점) 한 축에 그렸으니 "흐름을 나란히 본다"는 목적에는 맞지만 절대값 비교는 뜻이 없다는 점을 기억해 둔다. 단위가 다른 두 지표를 제대로 겹치려면 `ax.twinx()`로 오른쪽 y축을 하나 더 두는 것이 다음 단계다. `label`을 준 선만 범례에 올라오므로, `legend()`가 비어 있으면 `label`을 빠뜨린 것이다.

### 1-3. 문제 2 — `value_counts`를 막대로, `index`와 `values`

```python
x = df['주요결제수단'].value_counts().index    # ['신용카드', '간편결제', '계좌이체']
y = df['주요결제수단'].value_counts().values   # [88 75 37]
bars = plt.bar(x, y)
plt.bar_label(bars, padding=3)
```

| 조각 | 돌려주는 것 | 역할 |
| --- | --- | --- |
| `value_counts()` | 많은 순으로 정렬된 `Series` (인덱스 = 범주, 값 = 개수) | 집계 |
| `.index` | 범주 이름들 | x축 |
| `.values` | 개수 넘파이 배열 | 막대 높이 |

`plt.bar`는 시본 `countplot`과 달리 **세어 주지 않는다** — 범주별 개수를 직접 만들어 x·y로 넘겨야 한다. 그 집계가 `value_counts()` 한 줄이고, 결과 `Series`의 `index`·`values`를 떼어 넣으면 된다. 많은 순으로 정렬되어 있어 막대가 자연스럽게 내림차순이 되고, `bar_label(bars, padding=3)`으로 막대 위에 숫자를 얹는 것은 맷플롯립 노트의 막대 차트와 같다. 같은 그림을 시본으로 그리면 `sns.countplot(data=df, x='주요결제수단')` 한 줄이지만, 정렬 순서는 `order=` 인자로 따로 줘야 한다.

### 1-4. 문제 3·4 — 산점도와 히스토그램, 열 하나·둘의 분포

```python
plt.scatter(df['연령'], df['월이용금액'], color='purple', alpha=0.6)     # 문제 3
plt.hist(df['만족도점수'], bins=10, edgecolor='black')                  # 문제 4
```

| 문제 | 열 | 질문 | 이 데이터에서 보이는 것 |
| --- | --- | --- | --- |
| 3 산점도 | 연령 × 월이용금액 (수치 둘) | 함께 움직이는가 | 상관계수 −0.09 — 거의 **무관**, 점이 구름처럼 퍼짐 |
| 4 히스토그램 | 만족도점수 (수치 하나) | 어디에 몰려 있나 | 75 근처 종 모양, 40·100에서 잘린 흔적 |

맷플롯립 노트에서 산점도는 "공부시간과 시험점수"로 **양의 상관**이 보이는 예였다면, 이번 데이터는 열끼리 독립으로 생성했기 때문에 산점도에 기울기가 없다. "아무 관계도 안 보이는 산점도"를 한 번 보는 것도 의미가 있다 — 실제 데이터에서 그림이 이렇게 나오면 두 변수를 같이 쓸 근거가 약하다는 뜻이다. `alpha=0.6`은 점이 겹치는 곳을 진하게 보여 밀도를 드러낸다. 히스토그램의 `bins=10`은 40~100을 열 구간으로 나눈다는 뜻이고, `edgecolor='black'`으로 막대 경계를 그어야 구간이 구분된다. `clip`으로 잘라 낸 데이터라 양 끝 구간이 살짝 두꺼울 수 있다.

### 1-5. 문제 5 — 박스플롯으로 다섯 수치 요약과 이상치

```python
sns.boxplot(data=df, y='월이용금액')
```

| 요약값 | 월이용금액 | 상자에서의 위치 |
| --- | --- | --- |
| 최솟값 / 최댓값 | 20.3 / 304.1 | 수염 끝 또는 바깥 점 |
| Q1 (25%) | 122.2 | 상자 아랫변 |
| 중앙값 (50%) | 154.2 | 상자 안 가로선 |
| Q3 (75%) | 176.7 | 상자 윗변 |
| IQR = Q3 − Q1 | 54.5 | 상자 높이 |

`x` 없이 `y='월이용금액'`만 주면 **열 하나의 분포**를 세로 상자 하나로 그린다. 시본 노트의 "상자 읽는 법" 표 그대로 — 수염은 `Q1 − 1.5·IQR`(≈ 40.5)과 `Q3 + 1.5·IQR`(≈ 258.5)까지 뻗고, 그 밖의 값은 점으로 찍힌다. 이 데이터에서는 정규분포 꼬리에서 나온 **3개**가 이상치로 찍힌다. 히스토그램(문제 4)이 "모양"을 보여 준다면 박스플롯은 "**다섯 숫자와 이상치**"를 보여 주는 요약이라, 같은 열을 두 그림으로 번갈아 보는 습관이 EDA의 기본이다. 맷플롯립의 `plt.boxplot(df['월이용금액'])`도 같은 그림이지만 시본 쪽이 테마와 열 이름 축 라벨을 알아서 붙여 준다.

### 1-6. 문제 6·7 — 범주를 `hue`로 쪼개는 카운트플롯, 범주별 박스플롯

```python
sns.countplot(data=df, x='회원등급', hue='재구매여부', palette='Set2')    # 문제 6
sns.boxplot(data=df, x='주요결제수단', y='월이용금액')                    # 문제 7
```

| 문제 | x | y | hue | 읽는 것 |
| --- | --- | --- | --- | --- |
| 6 | 회원등급(범주) | 자동 집계 | 재구매여부 | 등급마다 Yes/No 막대 두 개 — **등급별 재구매 비율** |
| 7 | 주요결제수단(범주) | 월이용금액(수치) | — | 결제수단 셋의 **금액 분포 비교** — 중앙값 높이·상자 폭 |

문제 6은 시본 노트의 `countplot(x="멤버십", hue="이탈여부")`와 같은 구조다. `countplot`은 y를 주지 않아도 **알아서 센다**는 점이 `plt.bar`(문제 2)와 가장 다른 부분이고, `hue`로 색을 한 번 더 쪼개면 범주 두 개의 교차표가 그림이 된다. 문제 7은 문제 5의 상자를 **범주 개수만큼 옆으로 늘어놓은** 것이다. 세 상자의 중앙값 높이가 비슷하면 "결제수단에 따라 금액이 다르지 않다"는 뜻이고, 이 데이터는 독립으로 만들었으니 실제로 그렇게 나온다. 범주 수가 많거나 분포 모양까지 보고 싶으면 `violinplot`으로 바꿔 그린다.

### 1-7. 문제 8 — 수치 네 열의 상관 히트맵

```python
numeric_df = df[['연령', '월이용금액', '구매건수', '만족도점수']]
corr_matrix = numeric_df.corr()
sns.heatmap(corr_matrix, cmap='coolwarm', fmt='.2f', annot=True)
```

| | 연령 | 월이용금액 | 구매건수 | 만족도점수 |
| --- | --- | --- | --- | --- |
| 연령 | 1.00 | −0.09 | 0.07 | −0.05 |
| 월이용금액 | −0.09 | 1.00 | −0.08 | −0.06 |
| 구매건수 | 0.07 | −0.08 | 1.00 | −0.14 |
| 만족도점수 | −0.05 | −0.06 | −0.14 | 1.00 |

`corr()`에 넘기기 전에 **수치 열만 이중 대괄호로 고르는** 것이 첫 단계다 — `고객ID`나 `회원등급` 같은 문자열 열이 섞이면 오류가 나거나 뜻 없는 값이 섞인다. 시본 노트의 히트맵은 `df['소득'] += df['나이'] * 40`으로 경향을 **일부러 심어서** 0.8대 상관이 보였지만, 이번 데이터는 전부 독립으로 생성했으므로 대각선 1.00을 빼면 **모두 ±0.15 안**이다. `coolwarm`이 0을 흰색 가까이, 양·음을 각각 빨강·파랑으로 칠하는 **발산형 팔레트**라 "거의 전부 흰색"인 그림이 나오고, 그것이 곧 "선형 관계가 없다"는 결론이다. 히트맵은 관계가 있을 때만 쓸모 있는 게 아니라 **없음을 확인하는 데도** 쓴다.

### 1-8. 문제 9·10 — `hue`로 그룹을 나눈 산점도와 페어플롯

```python
sns.scatterplot(data=df, x='구매건수', y='만족도점수', hue='회원등급')              # 문제 9
sns.pairplot(df[['연령', '월이용금액', '만족도점수', '재구매여부']], hue='재구매여부')  # 문제 10
```

| 문제 | 그리는 것 | 격자 크기 | 읽는 법 |
| --- | --- | --- | --- |
| 9 | 수치 둘 + 범주 색 | 1장 | 등급별 점 구름이 **다른 자리**에 몰리면 등급이 관계를 가른다 |
| 10 | 수치 셋의 모든 쌍 + 대각선 분포 | 3×3 = 9칸 | 비대각 = 산점도, 대각 = 히스토그램/KDE, 색 = 재구매여부 |

문제 9는 `plt.scatter`(문제 3)에 **`hue`를 더한** 시본판이다. 배열 둘을 직접 넘기는 대신 열 이름을 적고, 범주 열을 `hue`에 주면 색과 범례가 자동이다. `구매건수`는 포아송 정수라 점이 세로줄로 늘어서는데, 그런 경우 `alpha`를 낮추거나 `stripplot`·`swarmplot`으로 바꾸면 겹침이 풀린다. 문제 10의 `pairplot`은 시본 노트 끝에서 키워드로만 적어 둔 것을 실제로 그리는 자리다. **수치 열 셋**(연령·월이용금액·만족도점수)을 넣었으니 3×3 격자 — 비대각 여섯 칸은 두 열씩의 산점도, 대각 세 칸은 각 열의 분포이며, `재구매여부`는 축이 아니라 **색**으로만 쓰인다. 열이 많으면 격자가 제곱으로 커지므로 보통 네다섯 열까지만 넣고, 그 이상은 히트맵(문제 8)으로 먼저 줄인다.

### 1-9. 열 문제를 "열의 조합"으로 다시 보기

| 재료 | 차트 | 문제 | 함수 |
| --- | --- | --- | --- |
| 수치 하나 | 히스토그램 · 박스플롯 | 4 · 5 | `plt.hist` · `sns.boxplot(y=)` |
| 범주 하나 | 막대(집계 직접) · 카운트플롯(자동) | 2 · 6 | `plt.bar(value_counts)` · `sns.countplot` |
| 범주 + 수치 | 박스플롯 | 7 | `sns.boxplot(x=범주, y=수치)` |
| 수치 둘 | 산점도 (+범주 색) | 3 · 9 | `plt.scatter` · `sns.scatterplot(hue=)` |
| 수치 여럿 | 히트맵 · 페어플롯 | 8 · 10 | `sns.heatmap(corr())` · `sns.pairplot(hue=)` |
| 순서가 있는 x | 선 차트 | 1 | `plt.plot` 두 번 |

맷플롯립 노트의 "네 차트 비교표"와 시본 노트의 "네 그림 비교표"가 이 표 하나로 합쳐진다. 어떤 그림을 그릴지 고민될 때 먼저 묻는 것은 "열이 몇 개이고 각각 수치인가 범주인가"다.

## 2. 추가로 알면 좋은 활용법

### 2-1. 단위가 다른 두 선 — `twinx`

```python
fig, ax1 = plt.subplots(figsize=(8, 4))
ax1.plot(top10.index, top10['월이용금액'], marker='o', color='tab:blue');  ax1.set_ylabel('월이용금액(천원)')
ax2 = ax1.twinx()
ax2.plot(top10.index, top10['만족도점수'], marker='s', color='tab:red');   ax2.set_ylabel('만족도점수')
```

문제 1처럼 단위가 다른 두 지표는 오른쪽 축을 하나 더 두면 각자의 범위로 그려진다. 객체지향 방식(`ax.set_…`)을 써야 하는 첫 사례라 익혀 둘 만하다.

### 2-2. 막대 정렬과 비율 막대

```python
sns.countplot(data=df, x='주요결제수단', order=df['주요결제수단'].value_counts().index)   # 많은 순
(df['주요결제수단'].value_counts(normalize=True) * 100).plot.bar()                          # 비율 막대
```

`countplot`은 등장 순서로 그리므로 **`order=`에 `value_counts().index`**를 넘겨야 문제 2와 같은 내림차순이 된다. 판다스 `Series.plot.bar()`는 집계 결과를 바로 막대로 그리는 지름길이다.

### 2-3. 히스토그램에 밀도 곡선 — `sns.histplot(kde=True)`

```python
sns.histplot(data=df, x='만족도점수', bins=10, kde=True)
sns.histplot(data=df, x='만족도점수', hue='재구매여부', kde=True)   # 그룹별 겹쳐 보기
```

`plt.hist`에 없는 두 가지 — 부드러운 밀도 곡선(KDE)과 `hue` 분리 — 를 `histplot`이 준다. 다음 실습(타이타닉)에서 나이 분포를 생존 여부로 나눠 볼 때 바로 쓴다.

### 2-4. 이상치를 숫자로 꺼내기 — IQR 규칙

```python
q1, q3 = df['월이용금액'].quantile([0.25, 0.75]);  iqr = q3 - q1
outliers = df[(df['월이용금액'] < q1 - 1.5 * iqr) | (df['월이용금액'] > q3 + 1.5 * iqr)]
len(outliers)   # 3
```

문제 5의 박스플롯에 찍힌 점이 **어느 행**인지는 이렇게 뽑는다. 시본 노트 3-4에서 식으로만 적어 둔 것을 데이터에 적용하면 행 3개가 나온다.

### 2-5. 히트맵 반쪽만 — `mask`와 범위 고정

```python
mask = np.triu(np.ones_like(corr_matrix, dtype=bool))
sns.heatmap(corr_matrix, mask=mask, cmap='coolwarm', vmin=-1, vmax=1, annot=True, fmt='.2f')
```

상관 행렬은 대칭이라 위 삼각형을 가리면 읽을 칸이 절반으로 준다. `vmin=-1, vmax=1`로 색 범위를 고정해야 "전부 희미하다"는 인상이 데이터에 따라 왜곡되지 않는다 — 고정하지 않으면 ±0.14가 가장 진한 색으로 칠해져 관계가 있는 것처럼 보인다.

### 2-6. 페어플롯 다듬기 — `diag_kind`·`corner`·`vars`

```python
sns.pairplot(df, vars=['연령', '월이용금액', '만족도점수'], hue='재구매여부', diag_kind='kde', corner=True)
```

`vars=`로 열을 고르면 데이터프레임을 미리 자르지 않아도 되고, `corner=True`는 히트맵의 `mask`처럼 아래 삼각형만 그린다. `diag_kind='kde'`는 대각선을 히스토그램 대신 밀도 곡선으로 바꾼다.

## 3. 더 나아가 알면 좋은 것

### 3-1. 무작위 데이터의 "무관함"이 알려 주는 것

이번 데이터는 열끼리 **독립으로 생성**했으므로 상관계수가 전부 0 근처, 결제수단별 금액 분포가 비슷, 등급별 재구매 비율이 비슷하게 나온다. 실제 분석에서 "차이가 있다"고 말하려면 이 **아무 관계 없는 데이터에서 나오는 우연한 차이보다 커야** 한다는 것이 통계 검정(t-검정·카이제곱 검정)의 출발점이다. 시드를 바꿔 몇 번 돌려 보면 ±0.1 정도의 상관은 우연으로도 흔히 나온다는 감각이 생긴다.

### 3-2. 한 장에 열 그림 — `subplots` 격자와 `ax=`

```python
fig, axes = plt.subplots(2, 5, figsize=(22, 8))
sns.histplot(data=df, x='만족도점수', ax=axes[0, 0])
sns.boxplot(data=df, y='월이용금액', ax=axes[0, 1])
...
plt.tight_layout()
```

문제마다 `plt.show()`로 창을 열 개 띄우는 대신, 격자를 만들고 시본 함수에 `ax=`를 넘기면 **대시보드 한 장**이 된다. 맷플롯립 노트의 `subplots(행, 열)`과 시본 노트의 `ax=`가 만나는 지점이다.

### 3-3. figure-level 함수로 범주마다 자동 분할

`sns.catplot(data=df, x='주요결제수단', y='월이용금액', col='회원등급', kind='box')`처럼 `col=`을 주면 등급마다 그림을 **자동으로 나눠** 격자로 배치한다. `hue`로 색을 쪼개는 것보다 범주가 많을 때 읽기 쉽고, `relplot(kind='scatter')`·`displot(kind='hist')`가 같은 구조다.

### 3-4. 다음에 볼 키워드

- `np.random.normal`·`poisson`·`randint`·`choice(p=)`·`np.clip`·`seed`·f-문자열 `:03d`
- `twinx`·`set_ylabel`·객체지향 방식·`tight_layout`
- `value_counts().index/.values`·`order=`·`Series.plot.bar`·`normalize=True`
- `histplot(kde=True, hue=)`·`kdeplot`·`violinplot`·`stripplot`/`swarmplot`
- `quantile`·IQR·`np.triu`·`mask=`·`vmin`/`vmax`
- `pairplot(vars, diag_kind, corner)`·`catplot(col=)`·`relplot`·`displot`
- 상관 vs 우연·t-검정·카이제곱 검정·`scipy.stats`

## 실습 파일

- `KDT_2026/2026_Python/practice/practice5.py` — `np.random.seed(42)`로 고객 200명 데이터프레임 생성(`randint`·`normal`·`poisson`·`clip`·`choice(p=)`·`f'USER_{i:03d}'`), 문제 1 `plt.plot` 두 번으로 상위 10명 월이용금액·만족도점수 선 그래프, 문제 2 `value_counts().index/.values`를 `plt.bar`+`bar_label`로, 문제 3 `plt.scatter(연령, 월이용금액, alpha=0.6)`, 문제 4 `plt.hist(만족도점수, bins=10, edgecolor)`, 문제 5 `sns.boxplot(y='월이용금액')`, 문제 6 `sns.countplot(x='회원등급', hue='재구매여부', palette='Set2')`, 문제 7 `sns.boxplot(x='주요결제수단', y='월이용금액')`, 문제 8 수치 네 열 `corr()` → `sns.heatmap(cmap='coolwarm', fmt='.2f', annot=True)`, 문제 9 `sns.scatterplot(x='구매건수', y='만족도점수', hue='회원등급')`, 문제 10 `sns.pairplot(df[[연령, 월이용금액, 만족도점수, 재구매여부]], hue='재구매여부')`

## 관련 노트

[[Python 정리본 인덱스]] · [[Python day09 시본 범주 빈도·박스플롯·상관 히트맵]] · [[Python day09 타이타닉 생존 데이터 EDA 실습]] · [[Python day09 맷플롯립 시작과 선 차트]] · [[KDT_2026 학습 지도]]
