---
출처: Claude 분석
원본: KDT_2026/2026_Python/practice/practice6.py, practice/train.csv
작성일: 2026-11-02
tags: [학습, python]
---

# Python day09 — 타이타닉 생존 데이터 EDA 실습

> 실습 파일: `practice/practice6.py` (문제 1), `practice/train.csv`
> 허브: [[Python 정리본 인덱스]] · 이전: [[Python day09 맷플롯립·시본 연습문제 풀이]] · 다음: [[Python day09 따릉이 대여이력 EDA 실습]]

판다스 전처리와 시본 시각화를 **가설 → 자료 수집 → 전처리 → 시각화 → 해석**이라는 분석 보고서 순서에 끼워 넣는 첫 실습이다. 재료는 캐글의 타이타닉 `train.csv`(승객 891명 × 12열)로, 데이터 분석 입문의 표준 교재 같은 데이터다. 문제 파일의 주석이 **가설 세 개**를 먼저 적어 두고 시작한다 — ① 여성과 아동의 생존율이 남성보다 높다, ② 객실 등급이 높을수록 생존율이 높다, ③ 승선 항구에 따라 (등급 분포 차이 때문에) 생존율이 다르다. 그다음 `info()`·`isnull().sum()`으로 결측을 진단하고, `Age`는 중앙값·`Embarked`는 최빈값으로 채운 뒤, 막대 → KDE 히스토그램 → 카운트플롯 세 장 → `groupby().mean()` 숫자 확인 순서로 가설을 하나씩 그림과 숫자로 대조한다. 지금까지는 "이 함수로 이 그림을 그린다"였다면, 이번에는 **"이 질문에 답하려면 어느 열을 어느 그림으로 봐야 하나"**가 주제다. 같은 파일의 문제 2(따릉이 대여이력)는 다음 노트에 따로 정리했다.

## 1. 배운 내용

### 1-1. 가설부터 쓰는 이유와 열 지도

```python
# 가설 1: 여성과 아동의 생존율이 남성보다 월등히 높을 것이다. (사회적 보호)
# 가설 2: 높은 객실 등급(1등석)을 이용한 승객일수록 생존율이 높을 것이다.
# 가설 3: 특정 항구에서 탑승한 승객은 객실 등급 분포에 따라 생존율 차이가 발생할 것이다.
df = pd.read_csv('./practice/train.csv')
```

| 열 | 뜻 | 자료형 | 가설과의 관계 |
| --- | --- | --- | --- |
| `Survived` | 생존 0/1 | int | **목표 변수** — 모든 그림의 `hue` |
| `Pclass` | 객실 등급 1·2·3 | int(뜻은 범주) | 가설 2 |
| `Sex` | male/female | object | 가설 1 |
| `Age` | 나이 | float, **결측 177** | 가설 1(아동) |
| `Embarked` | 승선 항구 C·Q·S | object, **결측 2** | 가설 3 |
| `Cabin` | 객실 번호 | object, **결측 687** | 이번엔 안 씀 |
| `Name`·`Ticket`·`Fare`·`SibSp`·`Parch`·`PassengerId` | 이름·표·요금·동반 가족 수·ID | — | 이번엔 안 씀 |

가설을 먼저 적으면 **열 열두 개 중 어느 넷을 볼지**가 바로 정해진다. 반대로 그림을 먼저 그리면 열 조합이 수십 가지라 길을 잃기 쉽다. 전처리 노트의 ①~⑩ 파이프라인이 "데이터를 깨끗하게"였다면, EDA는 "질문에 답하기"라서 순서가 가설 → 열 선택 → 그림이다. `Pclass`가 정수지만 뜻은 범주라는 점은 시본 노트의 "0/1 `hue`" 주의와 같은 맥락으로, 집계·그림에서 범주로 다뤄야 한다.

### 1-2. 결측 진단과 두 가지 채우기

```python
df.info()
print(df.isnull().sum())      # Age 177, Cabin 687, Embarked 2
df['Age'] = df['Age'].fillna(df['Age'].median())            # 28.0
df['Embarked'] = df['Embarked'].fillna(df['Embarked'].mode()[0])   # 'S'
print(df.isnull().sum())      # Age 0, Embarked 0 (Cabin은 그대로)
```

| 열 | 결측 | 비율 | 처리 | 이유 |
| --- | --- | --- | --- | --- |
| `Age` | 177 | 19.9% | 중앙값 28.0 | 수치 — 평균은 고령 극단값에 끌림 |
| `Embarked` | 2 | 0.2% | 최빈값 `S`(644명) | 범주 — 평균 없음, 2건이라 영향 미미 |
| `Cabin` | 687 | 77.1% | 손대지 않음 | 가설에 안 쓰이고, 77%는 채워도 의미 없음 |

이커머스 실습의 Step 2와 똑같은 두 줄이다 — **수치는 `median()`, 범주는 `mode()[0]`**. `Age`를 중앙값으로 채우는 것은 "이상치에 강건한(robust)" 선택이지만, 177명(20%)을 전부 28세로 만들기 때문에 **28세 자리에 인공적인 봉우리**가 생긴다는 부작용이 있다. 다음 그림(나이 히스토그램)에서 28 근처가 튀어 보이면 그것이 데이터가 아니라 채우기의 흔적이다. `Cabin`은 77%가 비어 있어 채워 봐야 추정값 덩어리라 그대로 두었고, 이커머스 실습 2-2의 "비율이 크면 열을 버리거나 결측 여부만 쓴다"는 선택지가 여기 해당한다 — 실제로 "객실 번호가 **기록된 승객**"은 1등석일 가능성이 커서 `Cabin.notna()` 자체가 유용한 파생변수가 된다.

### 1-3. 생존 분포 — `value_counts().sort_index()`를 막대로

```python
counts = df['Survived'].value_counts().sort_index()   # 0: 549, 1: 342
bars = plt.bar(['사망', '생존'], counts.values, color=['gray', 'skyblue'])
plt.bar_label(bars, padding=3)
```

전체 891명 중 생존 342명(38.4%)·사망 549명(61.6%)이다. `value_counts()`는 **많은 순**으로 정렬하므로 0(사망)이 먼저 오지만, 라벨 `['사망', '생존']`과 자리를 확실히 맞추려고 `.sort_index()`로 **0 → 1 순서를 고정**했다 — 연습문제 2번에서 `value_counts().index`를 그대로 x로 쓴 것과 달리, 라벨을 직접 적을 때는 순서 고정이 필수다. 색을 회색·하늘색 리스트로 준 것은 맷플롯립 노트의 "막대마다 색 리스트"다. 이 첫 그림은 가설을 검증하는 게 아니라 **기준선**이다 — 이후 모든 그룹의 생존율을 전체 38%와 비교해 "높다·낮다"를 말한다.

### 1-4. 나이 × 생존 — `histplot(hue=, kde=True)`

```python
sns.histplot(data=df, x='Age', hue='Survived', kde=True, bins=30)
```

| 인자 | 역할 |
| --- | --- |
| `x='Age'` | 수치 열의 분포 |
| `hue='Survived'` | 생존·사망 두 분포를 **겹쳐** 색으로 |
| `kde=True` | 막대 위에 부드러운 **커널 밀도 곡선** |
| `bins=30` | 0~80세를 30구간 |

`plt.hist`로는 그룹을 나누려면 두 번 그려야 했는데, 시본 `histplot`은 `hue` 하나로 겹쳐 그리고 범례까지 만든다. KDE 곡선은 막대의 들쭉날쭉함을 평균 낸 "분포의 윤곽"이라, 두 그룹의 **봉우리 위치 차이**를 읽기 좋다. 이 데이터에서 눈에 띄는 것은 0~10세 구간에서 생존 막대가 사망 막대보다 높다는 점 — 12세 이하 69명의 생존율이 58%로 전체 38%를 크게 웃돈다 — 이고, 이것이 가설 1의 "아동" 절반을 뒷받침한다. 28세 근처에 솟은 봉우리는 1-2에서 말한 중앙값 채우기의 흔적이니, 그 구간을 보고 "28세가 많이 탔다"고 읽으면 안 된다.

### 1-5. 성별·등급·항구 × 생존 — 카운트플롯 세 장

```python
sns.countplot(data=df, x='Sex', hue='Survived', palette='Set1')        # 5-4
sns.countplot(data=df, x='Pclass', hue='Survived', palette='Set2')     # 5-5
sns.countplot(data=df, x='Embarked', hue='Survived', palette='Pastel2')  # 5-6
```

세 장 모두 **범주 하나 × 목표 변수 `hue`**라는 같은 구조다 — 시본 노트의 `countplot(x="멤버십", hue="이탈여부")`에서 `x`만 바꿔 끼운 것이다. 읽는 법도 같다. 범주마다 막대 두 개(사망·생존)가 서고, **생존 막대가 사망 막대보다 높은 범주**가 "생존에 유리한 조건"이다. 성별 그림에서는 female 쪽만 생존 막대가 높고, 등급 그림에서는 1등석만 생존이 더 높으며 3등석은 사망이 압도적이고, 항구 그림에서는 S가 수는 가장 많지만 사망 비율도 높고 C는 생존 쪽이 더 높다. 팔레트 세 가지(`Set1`·`Set2`·`Pastel2`)는 그림을 구분하려는 선택일 뿐 의미는 없다.

카운트플롯의 한계도 같이 보인다 — **절대 수**를 그리기 때문에 범주 크기가 다르면(S 644명 vs Q 77명) 비율 비교가 어렵다. 그래서 바로 다음 단계인 숫자 확인이 필요하다.

### 1-6. 숫자로 확인 — `groupby('열')['Survived'].mean()`

```python
print(df.groupby('Sex')['Survived'].mean())       # female 0.742, male 0.189
print(df.groupby('Pclass')['Survived'].mean())    # 1: 0.630, 2: 0.473, 3: 0.242
print(df.groupby('Embarked')['Survived'].mean())  # C 0.554, Q 0.390, S 0.339
```

| 가설 | 그룹별 생존율 | 판정 |
| --- | --- | --- |
| 1 여성·아동 | female **74.2%** vs male 18.9% · 12세 이하 58% | 뒷받침 — 성별 차이가 가장 큼 |
| 2 등급 | 1등석 **63.0%** → 2등석 47.3% → 3등석 24.2% | 뒷받침 — 등급 순서대로 단조 감소 |
| 3 항구 | C **55.4%** > Q 39.0% > S 33.9% | 차이 있음 — 다만 원인은 등급 분포일 가능성 |

`Survived`가 0/1이므로 **평균이 곧 생존율**이다 — 넘파이 연습문제에서 불리언 배열의 `.sum()`이 개수, `.mean()`이 비율이던 것과 같은 원리다. `groupby('Sex')['Survived'].mean()`은 "성별로 묶어 → 생존 열만 골라 → 평균"이라는 세 동작이고, 이커머스 실습의 `agg` 다중 집계를 열 하나로 줄인 가장 단순한 형태다. 카운트플롯이 "크기"를 보여 주고 이 숫자가 "비율"을 확정하는 관계라, 그림과 숫자를 **짝으로** 두어야 결론이 선다.

가설 3은 주의가 필요하다. 항구별 생존율 차이가 **항구 자체 때문인지, 항구마다 등급 구성이 달라서인지**를 가려야 한다. 교차표를 보면 C 항구 탑승객 168명 중 1등석이 85명(51%)인 반면 S 항구는 646명 중 1등석이 129명(20%)·3등석이 353명(55%)이다. 즉 C의 높은 생존율은 상당 부분 "1등석 비중이 높아서"로 설명된다 — 가설 3의 문장이 "등급 분포에 따라"라고 조건을 단 이유가 여기 있다. 이런 **숨은 변수(교란 변수)**를 확인하는 것이 EDA에서 "상관이 곧 원인은 아니다"를 실천하는 방법이다.

### 1-7. 분석 보고서 다섯 단계를 코드와 짝짓기

| 단계 | 이번 실습 | 쓴 도구 |
| --- | --- | --- |
| 1 문제 정의 | 침몰 사고에서 누가 살아남았나 | 주석 |
| 2 가설 | 성별·나이 / 등급 / 항구 세 가지 | 주석 |
| 3 자료 수집 | 캐글 `train.csv` → `read_csv` | 판다스 |
| 4 전처리 | `isnull().sum()` → `fillna(median)`·`fillna(mode()[0])` | 판다스 |
| 5 시각화·분석 | 막대 → KDE 히스토그램 → 카운트플롯 ×3 → `groupby().mean()` | 맷플롯립·시본·판다스 |

가설 하나에 그림 하나와 숫자 하나가 대응하는 구조다. 보고서를 쓸 때 "그림 5-4는 가설 1을, 표의 `groupby('Sex')`는 그 비율을" 식으로 번호를 맞추면 읽는 사람이 따라오기 쉽다.

## 2. 추가로 알면 좋은 활용법

### 2-1. 비율 막대 — 카운트플롯의 한계를 넘는 `barplot`

```python
sns.barplot(data=df, x='Pclass', y='Survived', errorbar=None)   # y 평균 = 생존율, 막대 높이가 바로 비율
rate = df.groupby('Embarked')['Survived'].mean().reset_index()
sns.barplot(data=rate, x='Embarked', y='Survived')
```

`barplot`은 `y`의 **평균**을 막대로 그리므로 0/1 열을 넘기면 생존율 막대가 된다. 범주 크기가 달라도 공정하게 비교되고, `errorbar`(기본 95% 신뢰구간)를 켜 두면 Q 항구처럼 표본이 적은 막대에 긴 오차 막대가 붙어 "숫자가 불안정하다"는 것까지 보여 준다.

### 2-2. 두 범주를 한 번에 — `pd.crosstab`과 `pivot_table`

```python
pd.crosstab(df['Embarked'], df['Pclass'])                                  # 항구 × 등급 인원
pd.crosstab(df['Sex'], df['Survived'], normalize='index')                   # 행 기준 비율
df.pivot_table(index='Pclass', columns='Sex', values='Survived', aggfunc='mean')   # 등급×성별 생존율
```

1-6의 교란 변수 확인에 쓴 것이 `crosstab`이다. `pivot_table`로 등급×성별 생존율을 만들면 "1등석 여성 97%, 3등석 남성 14%"처럼 **두 조건을 동시에** 읽을 수 있고, 그 표를 `sns.heatmap(annot=True)`에 넣으면 그림이 된다.

### 2-3. 나이를 구간으로 — `pd.cut`으로 아동 정의하기

```python
df['AgeGroup'] = pd.cut(df['Age'], bins=[0, 12, 18, 60, 100], labels=['아동', '청소년', '성인', '노년'])
df.groupby('AgeGroup', observed=True)['Survived'].mean()
```

가설 1의 "아동"을 수치로 정의하려면 구간화가 필요하다. 전처리 노트의 `pd.cut`이 여기서 쓰이고, 구간 경계를 바꿔 가며 결과가 흔들리는지 보는 것도 분석의 일부다.

### 2-4. 결측을 더 똑똑하게 — 그룹별 중앙값과 결측 지표

```python
df['Age'] = df['Age'].fillna(df.groupby(['Pclass', 'Sex'])['Age'].transform('median'))   # 등급·성별 중앙값으로
df['Cabin_known'] = df['Cabin'].notna().astype(int)                                      # 객실 기록 여부
df['Title'] = df['Name'].str.extract(r',\s*([^\.]+)\.')                                  # Mr/Mrs/Miss/Master 추출
```

전체 중앙값 28 하나로 채우는 대신 **같은 등급·성별의 중앙값**으로 채우면 28세 봉우리가 분산된다. `Name`에서 호칭을 뽑으면 `Master`(소년)·`Miss`로 나이 결측을 더 정확히 추정할 수 있어, 캐글 노트북들이 거의 예외 없이 쓰는 파생변수다.

### 2-5. 그림 세 장을 한 줄에 — `subplots`와 `ax=`

```python
fig, axes = plt.subplots(1, 3, figsize=(15, 4))
for ax, col in zip(axes, ['Sex', 'Pclass', 'Embarked']):
    sns.countplot(data=df, x=col, hue='Survived', ax=ax)
    ax.set_title(f'{col}별 생존 여부')
plt.tight_layout()
```

5-4·5-5·5-6이 같은 구조이므로 반복문으로 돌려 한 장에 놓으면 보고서용 그림이 된다. `zip(axes, 열목록)`으로 축과 열을 짝지어 도는 패턴은 자주 쓰인다.

### 2-6. 생존율 표를 보기 좋게

```python
(df.groupby('Pclass')['Survived'].agg(['count', 'mean'])
   .rename(columns={'count': '인원', 'mean': '생존율'})
   .assign(생존율=lambda d: (d['생존율'] * 100).round(1)))
```

인원과 비율을 **나란히** 두어야 "Q 항구 39%"가 77명 기준이라는 맥락이 같이 읽힌다. 체이닝으로 이름 바꾸기·퍼센트 변환까지 한 번에 묶는다.

## 3. 더 나아가 알면 좋은 것

### 3-1. 교란 변수와 심슨의 역설

가설 3에서 본 것처럼, 두 변수의 관계가 **제3의 변수**(등급) 때문에 생기거나 사라질 수 있다. 극단적으로는 전체에서는 A가 유리한데 등급별로 나누면 모두 B가 유리한 **심슨의 역설**도 일어난다. EDA에서 `hue`나 `col`로 한 변수를 더 쪼개 보는 습관이 이 함정을 피하는 가장 싼 방법이다.

### 3-2. 차이가 우연인지 — 카이제곱 검정

성별 × 생존 교차표에서 "74% vs 19%"는 누가 봐도 크지만, 항구 × 생존의 "55% vs 34%"는 표본이 작을 때 우연일 수도 있다. `scipy.stats.chi2_contingency(pd.crosstab(df['Embarked'], df['Survived']))`가 그 차이가 우연으로 나올 확률(p-값)을 준다. 연습문제 노트 3-1에서 "무작위 데이터에서도 ±0.1 차이는 흔하다"고 적어 둔 감각을 숫자로 바꾸는 도구다.

### 3-3. EDA에서 모델로 — 같은 열이 입력 변수가 된다

이번에 가설로 고른 `Sex`·`Pclass`·`Age`·`Embarked`가 그대로 생존 예측 모델의 **입력 변수(feature)**가 된다. 이커머스 실습의 `get_dummies`로 `Sex`·`Embarked`를 0/1로 바꾸고, `Age`를 채우고, `Survived`를 목표로 로지스틱 회귀나 결정 트리를 학습하는 것이 캐글 타이타닉 과제의 표준 흐름이다. EDA는 그 전에 "어느 열이 목표와 관계있나"를 눈으로 고르는 단계다.

### 3-4. 다음에 볼 키워드

- `isnull().sum()`·`fillna(median/mode)`·`groupby().transform('median')`·결측 지표 열·`str.extract`
- `value_counts().sort_index()`·`groupby()['열'].mean()` 비율·`agg(['count','mean'])`
- `histplot(hue, kde, bins)`·`kdeplot`·`countplot` vs `barplot(errorbar)`
- `pd.crosstab(normalize=)`·`pivot_table`·`pd.cut`·`observed=True`
- `subplots`+`zip(axes, …)`·`ax=`·`tight_layout`
- 교란 변수·심슨의 역설·`chi2_contingency`·p-값
- feature·`get_dummies`·로지스틱 회귀·결정 트리·`train_test_split`

## 실습 파일

- `KDT_2026/2026_Python/practice/practice6.py` (문제 1) — 가설 세 개 주석, `pd.read_csv('./practice/train.csv')`·`info()`·`isnull().sum()`(Age 177·Cabin 687·Embarked 2), `Age.fillna(median())` 28.0·`Embarked.fillna(mode()[0])` 'S', `value_counts().sort_index()`를 `plt.bar(['사망','생존'], …, color=['gray','skyblue'])`+`bar_label`로, `sns.histplot(x='Age', hue='Survived', kde=True, bins=30)`, `sns.countplot(x='Sex'/'Pclass'/'Embarked', hue='Survived', palette=…)` 세 장, `groupby('Sex'/'Pclass'/'Embarked')['Survived'].mean()`
- `KDT_2026/2026_Python/practice/train.csv` — 캐글 Titanic 학습 데이터 891행 × 12열(`PassengerId`·`Survived`·`Pclass`·`Name`·`Sex`·`Age`·`SibSp`·`Parch`·`Ticket`·`Fare`·`Cabin`·`Embarked`)

## 관련 노트

[[Python 정리본 인덱스]] · [[Python day09 맷플롯립·시본 연습문제 풀이]] · [[Python day09 따릉이 대여이력 EDA 실습]] · [[Python day08 판다스로 이커머스 주문 데이터 전처리 실습]] · [[KDT_2026 학습 지도]]
