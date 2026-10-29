---
출처: Claude 분석
원본: KDT_2026/2026_Python/day09/g-01.py
작성일: 2026-10-29
tags: [학습, python]
---

# Python day09 — 맷플롯립 시작과 선 차트

> 실습 파일: `day09/g-01.py`
> 허브: [[Python 정리본 인덱스]] · 이전: [[Python day08 판다스 데이터 전처리 중복 제거와 타입 변환]] · 다음: (아직 없음)

넘파이(숫자 계산)·판다스(표 다루기)에 이어 세 번째 라이브러리, **맷플롯립(Matplotlib)**이다. 수업 첫 줄의 정의를 그대로 옮기면 "파이썬에서 시각적인 표현을 하는 라이브러리" — 지금까지 `print`로 숫자를 찍어 확인하던 결과를 **그림(차트)**으로 보는 도구다. 이 시간에 한 일은 셋이다. `import matplotlib`로 설치를 확인하고, 한글이 깨지지 않도록 폰트를 잡고, 학습 횟수(epoch)에 따른 손실(loss) 두 줄을 **선 차트** 하나에 겹쳐 그렸다. 차트 한 장을 만드는 일곱 단계가 번호로 적혀 있어서, 그 순서가 곧 맷플롯립의 기본 뼈대다. 같은 파일에 이어서 **막대 차트(`bar`)·산점도(`scatter`)·히스토그램(`hist`)** 세 가지가 더 붙었다. 범주를 비교할 때, 두 값의 관계를 볼 때, 값이 어떻게 퍼져 있는지 볼 때 각각 꺼내 쓰는 차트인데, 뼈대는 선 차트와 똑같고 2번 자리의 그리기 함수와 그 인자만 바뀐다는 것을 네 번 반복해서 확인하는 구성이다.

## 1. 배운 내용

### 1-1. 불러오기 — `matplotlib`와 `matplotlib.pyplot`

```python
import matplotlib
print(matplotlib.__version__)

import matplotlib.pyplot as plt
```

| 문장 | 뜻 |
| --- | --- |
| `import matplotlib` | 라이브러리 전체. 설치 확인용으로 `__version__`을 찍었다 |
| `import matplotlib.pyplot as plt` | 그 안의 **`pyplot` 모듈**만 `plt`라는 별칭으로 가져온다. 실제 그리기는 전부 이쪽으로 한다 |

넘파이가 `np`, 판다스가 `pd`였듯 맷플롯립은 **`plt`**가 관례다. 점(`.`)으로 이어진 `matplotlib.pyplot`은 "맷플롯립 안의 pyplot"이라는 뜻 — 라이브러리 전체가 아니라 그 안의 모듈 하나만 꺼내 오는 것이라 `import matplotlib`를 했어도 `plt`는 따로 선언해야 쓸 수 있다. 이름이 pyplot인 이유는 MATLAB의 `plot` 명령을 파이썬에 옮겨온 모듈이기 때문이고, 그래서 함수 이름(`plot`·`title`·`xlabel`·`legend`)이 MATLAB과 거의 같다.

### 1-2. 한글 폰트 설정 — 그리기 전에 먼저

```python
# 맷플롯립 그래프는 한글폰트 지원 안한다
plt.rc('font', family='Malgun Gothic')        # 윈도우 맑은고딕으로 설정
plt.rcParams['axes.unicode_minus'] = False    # 음수 기호 깨짐 방지
```

맷플롯립의 기본 폰트(DejaVu Sans)에는 한글 글자가 없어서, 제목이나 축 이름에 한글을 쓰면 글자 자리가 네모(□)로 찍힌다. 그래서 **차트를 그리기 전에** 폰트를 한글이 들어 있는 것으로 바꿔 둔다.

| 설정 | 하는 일 |
| --- | --- |
| `plt.rc('font', family='Malgun Gothic')` | 글꼴 묶음(`font`)의 `family` 항목을 맑은 고딕으로. 윈도우에 기본으로 깔린 한글 폰트다 |
| `plt.rcParams['axes.unicode_minus'] = False` | 음수 부호를 유니코드 마이너스(−) 대신 보통 하이픈(-)으로 찍는다. 한글 폰트로 바꾸면 유니코드 마이너스가 없어 `-0.5`가 `□0.5`로 깨지는 것을 막는다 |

`rc`는 runtime configuration의 약자로, 맷플롯립의 **전역 설정 사전** `rcParams`를 건드리는 두 가지 방법이다. `plt.rc('font', family=…)`는 `plt.rcParams['font.family'] = …`와 같은 일을 하는 짧은 표기이고, 둘 중 어느 쪽으로 써도 된다. 한 번 바꾸면 그 뒤로 그리는 모든 차트에 적용되므로 파일 맨 위, `import` 바로 아래에 두는 것이 관례다. 맑은 고딕은 윈도우 전용이라 맥에서는 `'AppleGothic'`, 리눅스에서는 `'NanumGothic'`(설치 필요)으로 이름이 달라진다.

### 1-3. 데이터 준비 — x축 하나, y축 둘

```python
epochs = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
train_loss = [0.9, 0.7, 0.55, 0.45, 0.38, 0.32, 0.28, 0.25, 0.23, 0.20]
val_loss   = [0.95, 0.75, 0.60, 0.52, 0.48, 0.45, 0.44, 0.43, 0.44, 0.45]
```

리스트 세 개가 차트의 재료다. `epochs`가 가로축(x), 나머지 둘이 세로축(y) 값이고 **길이가 10으로 같아야** 점이 하나씩 짝지어진다. 예제가 머신러닝 용어인 것은 뒤에 올 AI 수업을 염두에 둔 것 — epoch는 전체 데이터를 한 바퀴 학습한 횟수, loss는 모델의 예측이 정답에서 얼마나 틀렸는지 나타내는 값이다. 학습 데이터 손실(`train_loss`)은 계속 내려가는데 검증 데이터 손실(`val_loss`)은 7회쯤부터 다시 올라가는 모양으로 숫자가 짜여 있어, 선 두 개를 겹쳐 보면 "어디서부터 외우기 시작했나"가 한눈에 보이는 전형적인 그림이다.

### 1-4. 선 차트 그리기 — 일곱 단계

```python
plt.figure(figsize=(7, 4))                                   # 1) 차트 전체 크기

plt.plot(epochs, train_loss, label="Train Loss",             # 2) 선 하나
         color="blue", linestyle="-", marker="o")
plt.plot(epochs, val_loss, label="값 손실",                   #    선 하나 더 (같은 도화지)
         color="red", linestyle="--", marker="s")

plt.title("학습별 모델 손실 추세")   # 3) 차트 제목
plt.xlabel("학습 수")               # 4) x축 제목
plt.ylabel("손실")                  # 5) y축 제목
plt.grid(True)                      # 6) 눈금선
plt.legend()                        # 7) 범례

plt.show()                          # 차트 실행(창 띄우기)
```

수업 주석의 번호를 그대로 표로 옮기면 이렇다.

| 순서 | 함수 | 하는 일 |
| --- | --- | --- |
| 1 | `plt.figure(figsize=(가로, 세로))` | 빈 도화지를 만든다. 단위는 **인치** — `(7, 4)`는 가로 7인치·세로 4인치 |
| 2 | `plt.plot(x, y, label=, color=, linestyle=, marker=)` | 도화지에 **선 하나**를 올린다. 두 번 부르면 두 선이 같은 축 위에 겹친다 |
| 3 | `plt.title("…")` | 차트 제목 |
| 4 | `plt.xlabel("…")` | 가로축 이름 |
| 5 | `plt.ylabel("…")` | 세로축 이름 |
| 6 | `plt.grid(True)` | 배경 눈금선 켜기 |
| 7 | `plt.legend()` | 범례 — `plot`에 준 `label`들을 모아 상자로 표시 |
| 끝 | `plt.show()` | 지금까지 쌓은 것을 **실제로 그려서 창을 띄운다** |

핵심은 **`show()` 전까지는 아무것도 보이지 않는다**는 점이다. `figure`부터 `legend`까지는 "도화지에 이걸 올려라"는 지시를 쌓아 두는 단계이고, `show()`가 한 번에 렌더링한다. 그래서 순서는 `figure`(도화지) → `plot`(내용) → 제목·축·눈금·범례(꾸미기) → `show`(출력)로 외우면 되고, 3~7번은 서로 순서를 바꿔도 결과가 같다. `legend()`는 `plot`에서 `label=`을 줘야 표시할 내용이 생기므로, `label` 없이 `legend()`만 부르면 경고와 함께 빈 상자가 뜬다.

### 1-5. `plot`의 꾸미기 인자 — `color`·`linestyle`·`marker`

`plot`에 넘긴 키워드 인수 네 개는 선의 생김새를 정한다.

| 인자 | 예제 값 | 뜻 | 자주 쓰는 값 |
| --- | --- | --- | --- |
| `label` | `"Train Loss"` | 범례에 찍힐 이름 | 문자열 아무거나 |
| `color` | `"blue"` / `"red"` | 선 색 | 색 이름(`green`·`black`), 한 글자(`'b'`·`'r'`·`'g'`·`'k'`), `'#1f77b4'` 16진수 |
| `linestyle` | `"-"` / `"--"` | 선 종류 | `'-'` 실선, `'--'` 파선, `':'` 점선, `'-.'` 일점쇄선 |
| `marker` | `"o"` / `"s"` | 데이터 점 모양 | `'o'` 원, `'s'` 네모, `'^'` 삼각형, `'x'`, `'+'`, `'*'` |

학습 손실은 **파란 실선에 원**, 검증 손실은 **빨간 파선에 네모**로 구분했다. 색만 다르게 하지 않고 선 종류·점 모양까지 바꾼 것은 흑백으로 인쇄하거나 색각 차이가 있어도 두 선을 가를 수 있게 하는 습관이다. 세 인자는 `'bo-'`처럼 **한 문자열로 합쳐 세 번째 위치 인수로** 넘길 수도 있다 — `plt.plot(epochs, train_loss, 'bo-')`는 위와 같은 선이다(색·마커·선종류 순서는 자유).

### 1-6. 막대 차트 — `plt.bar`와 `bar_label`

```python
classes = ['Cat', 'Dog', 'Bird', 'Fish']
counts  = [120, 150, 80, 45]

bars = plt.bar(classes, counts, width=0.5,                            # 1) 막대
               color=['#222222', '#444444', '#666666', '#888888'])
plt.bar_label(bars, padding=3, fontsize=8)                            # 막대 끝에 값 레이블
plt.title('클래스별 샘플수')
plt.xlabel('클래스')
plt.ylabel('샘플 수')
plt.grid(True, alpha=0.5)                                             # alpha = 투명도
```

선 차트가 "순서에 따라 어떻게 변하나"를 보는 그림이라면, 막대 차트는 **범주끼리 크기를 비교**하는 그림이다. 가로축에 오는 것이 숫자가 아니라 `'Cat'`·`'Dog'` 같은 **범주(문자열)**라는 점이 가장 큰 차이고, 막대는 리스트에 적은 순서대로 왼쪽부터 선다.

| 인자 | 예제 값 | 뜻 |
| --- | --- | --- |
| 첫째 (x) | `classes` | 막대가 설 자리의 이름. 문자열 리스트를 그대로 넣으면 축 눈금 이름이 된다 |
| 둘째 (height) | `counts` | 막대의 높이. x와 길이가 같아야 한다 |
| `width` | `0.5` | 막대 폭. 범주 사이 간격을 1로 보고 그 비율로 준다. 기본값 0.8이라 `0.5`는 좀 더 홀쭉하게 |
| `color` | 리스트 4개 | 색을 **리스트로 주면 막대마다 다른 색**. 하나만 주면 전부 같은 색. 예제는 `#222222`→`#888888` 회색 네 단계 |

`plt.bar(...)`는 그린 막대들을 묶음(`BarContainer`)으로 돌려주고, 그것을 `bars`에 받아 **`plt.bar_label(bars, padding=3, fontsize=8)`**에 넘기면 막대 끝에 값(`120`·`150`…)이 글자로 찍힌다. `padding`은 막대 끝과 글자 사이 간격(포인트), `fontsize`는 글자 크기다. 막대 차트에서 눈으로 높이를 어림하는 대신 숫자를 바로 읽게 해 주는 장치라 보고서용 그림에는 거의 항상 붙인다. `grid(True, alpha=0.5)`의 `alpha`는 **투명도(0 = 완전 투명, 1 = 불투명)** — 눈금선을 반쯤 흐리게 깔아 막대보다 뒤로 물러나게 하는 용도다.

### 1-7. 산점도 — `plt.scatter`

```python
x = [1.5, 2.5, 3.5, 4.5, 5.5, 6.5, 7.5]      # 공부시간
y = [2.3, 3.8, 5.1, 7.0, 7.8, 9.2, 10.5]     # 시험점수

plt.scatter(x, y, color='purple', s=80, alpha=0.8)
plt.title("공부시간과 시험점수의 상관관계")
plt.xlabel("공부시간")
plt.ylabel("시험점수")
```

산점도는 **(x, y) 짝 하나를 점 하나**로 찍어 두 값 사이에 관계가 있는지 보는 그림이다. 선 차트처럼 점을 잇지 않는 이유는 x가 "순서"가 아니라 그 자체로 하나의 측정값이기 때문 — 공부시간이 늘수록 점수가 오르는 **양의 상관**이면 점들이 오른쪽 위로 비스듬히 늘어선다. 예제 숫자가 그 모양이다.

| 인자 | 예제 값 | 뜻 |
| --- | --- | --- |
| `color` | `'purple'` | 점 색. `plot`과 같은 표기 |
| `s` | `80` | 점의 **크기**(면적, 포인트²). 기본 36보다 두 배쯤 크게 |
| `alpha` | `0.8` | 투명도. 점이 겹치는 자리가 짙어 보여 **밀도**를 읽을 수 있다 |

`plot(x, y, 'o')`처럼 마커만 찍어도 겉모양은 비슷하지만, `scatter`는 **`s`와 `color`에 리스트를 넘겨 점마다 크기·색을 다르게** 줄 수 있다는 점이 다르다. 세 번째 값을 점 크기에 실으면 버블 차트, 네 번째 값을 색에 실으면 색 지도가 되는 식으로 산점도 하나에 변수 네 개까지 올릴 수 있다. 뒤의 AI 수업에서 "공부시간으로 점수를 예측한다"는 회귀(regression)를 배울 때 이 점들 사이로 직선을 긋게 된다.

### 1-8. 히스토그램 — `plt.hist`와 `np.random.normal`

```python
import numpy as np
# 평균 170을 중심으로 표준편차 5만큼 퍼진 종 모양(가우시안 분포) 난수 1000개
heights = np.random.normal(loc=170, scale=5, size=1000)

plt.hist(heights, bins=30, edgecolor="black")   # bins = 구간 개수
plt.xlabel("키(cm)")
plt.ylabel("빈도/분포수")
```

히스토그램은 **값 하나의 분포**를 보는 그림이다. 막대 차트와 생김새는 같지만 재료가 다르다 — 막대 차트는 범주마다 높이를 내가 정해 넣는데, 히스토그램은 **연속된 숫자 1,000개를 통째로 넣으면 축을 `bins`개 구간으로 쪼개 각 구간에 몇 개가 들어갔는지 세는 것까지 해 준다.** 그래서 y값을 따로 주지 않는다.

| 요소 | 뜻 |
| --- | --- |
| `np.random.normal(loc=170, scale=5, size=1000)` | 넘파이 난수. `loc` 평균, `scale` 표준편차, `size` 개수 — 평균 170cm·표준편차 5cm인 **정규분포**에서 키 1,000개를 뽑는다 |
| `bins=30` | 가로축을 30개 구간으로 나눈다. 값이 크면 막대가 가늘어져 세밀하고, 작으면 뭉뚱그려진다 — 분포의 **해상도** |
| `edgecolor="black"` | 막대 테두리 색. 없으면 옆 막대와 붙어 한 덩어리로 보인다 |

정규분포라 170 근처 구간이 가장 높고 양쪽으로 멀어질수록 낮아지는 **종 모양**이 나온다. 표준편차 5의 뜻을 그림으로 보면, 165~175(±1σ) 안에 전체의 68%쯤, 160~180(±2σ) 안에 95%쯤이 들어온다. day07에서 `np.mean`·`np.std`로 숫자 하나씩 뽑아 보던 평균·표준편차가 히스토그램에서는 **봉우리의 위치와 폭**으로 바뀐다. 난수이므로 실행할 때마다 막대 높이가 조금씩 달라지는데, 이것이 "같은 분포에서 뽑아도 표본은 매번 다르다"는 통계의 기본 감각이기도 하다.

### 1-9. 네 차트 한눈에 — 재료의 모양이 차트를 고른다

| 차트 | 함수 | x에 오는 것 | y에 오는 것 | 답하는 질문 |
| --- | --- | --- | --- | --- |
| 선 | `plt.plot(x, y)` | 순서 있는 숫자(epoch·날짜) | 숫자 | **어떻게 변하나** (추세) |
| 막대 | `plt.bar(x, height)` | 범주(문자열) | 숫자 | **무엇이 많나** (비교) |
| 산점도 | `plt.scatter(x, y)` | 숫자 | 숫자 | **둘이 관계가 있나** (상관) |
| 히스토그램 | `plt.hist(values, bins=)` | 연속 값 하나 | (자동으로 셈) | **어떻게 퍼져 있나** (분포) |

네 차트 모두 `figure` → 그리기 함수 → `title`·`xlabel`·`ylabel`·`grid` → `show`의 뼈대가 같고, 바뀐 것은 **2번 자리의 함수와 그 함수만의 인자**(`linestyle`/`marker`, `width`/`bar_label`, `s`, `bins`/`edgecolor`)뿐이다. 차트를 고르는 기준은 "예쁜가"가 아니라 **재료가 어떤 모양인가** — x가 순서면 선, 범주면 막대, 둘 다 측정값이면 산점도, 값이 한 줄이면 히스토그램이다. day07·day08에서 만든 표를 떠올리면, 대여소별 합계는 막대, 방문 횟수 대 구매 금액은 산점도, 나이 열 하나는 히스토그램으로 간다.

## 2. 추가로 알면 좋은 활용법

### 2-1. 차트를 파일로 저장 — `savefig`

```python
plt.savefig('loss.png', dpi=150, bbox_inches='tight')  # show() 앞에
plt.show()
```

`show()`는 창을 띄울 뿐 파일을 남기지 않는다. 보고서에 넣으려면 `savefig`로 저장하는데, **`show()` 뒤에 부르면 빈 그림이 저장**되므로 반드시 앞에 둔다(`show()`가 도화지를 비우기 때문). `dpi`는 해상도, `bbox_inches='tight'`는 제목·범례가 잘리지 않게 여백을 자동으로 맞춘다. 확장자를 `.svg`·`.pdf`로 바꾸면 벡터 형식으로 저장된다.

### 2-2. 축 범위와 눈금 — `xlim`·`ylim`·`xticks`

```python
plt.ylim(0, 1)                 # 세로축을 0~1로 고정
plt.xticks(epochs)             # 가로축 눈금을 1, 2, …, 10 정수로
plt.yticks([0, 0.25, 0.5, 0.75, 1.0])
```

맷플롯립은 데이터 범위에 맞춰 축을 자동으로 잡는데, 손실처럼 "0이 바닥"인 값은 `ylim(0, …)`으로 0을 보이게 하는 편이 추세를 과장하지 않는다. `xticks(epochs)`를 주지 않으면 가로축에 `2.5`, `7.5` 같은 소수 눈금이 생길 수 있다 — epoch는 정수이므로 눈금을 데이터 그대로 박아 두는 것이 읽기 좋다.

### 2-3. 넘파이·판다스와 같이 쓰기

```python
import numpy as np
x = np.arange(1, 11)
plt.plot(x, train_loss)

import pandas as pd
df = pd.DataFrame({'epoch': epochs, 'train': train_loss, 'val': val_loss})
df.plot(x='epoch', y=['train', 'val'], marker='o')   # 판다스가 맷플롯립을 대신 불러 준다
plt.show()
```

`plot`의 x·y 자리에는 리스트뿐 아니라 **넘파이 배열·판다스 `Series`**가 그대로 들어간다. 판다스 `DataFrame`에는 `.plot()` 메소드가 붙어 있어서 열 이름만 고르면 범례·축 이름까지 자동으로 채워 주는데, 그 안에서 돌아가는 것이 결국 이 수업의 `plt.plot`이다. day07·day08에서 만든 대여소 합계표나 부서별 평균 나이를 `df.plot(kind='bar')`로 넘기면 바로 막대 차트가 된다.

### 2-4. 차트를 따로 띄우기 — `figure()`를 다시 부르거나 `subplot`

```python
plt.figure(figsize=(7, 4)); plt.plot(epochs, train_loss)      # 1번 도화지
plt.figure(figsize=(5, 4)); plt.bar(classes, counts)           # 2번 도화지 (새로 만든다)
plt.show()                                                     # 창 두 개가 뜬다
```

pyplot 방식은 항상 **"지금 활성화된 도화지"**에 그린다. `figure()`를 한 번만 부르고 `plot`·`bar`·`scatter`·`hist`를 연달아 부르면 전부 같은 축 위에 겹쳐 올라가서, 축 단위가 다른 차트끼리 뒤섞인 그림이 된다. 차트마다 `plt.figure()`를 새로 불러 도화지를 갈아 주면 `show()` 때 창이 그 수만큼 뜨고, 한 창 안에 칸을 나누고 싶으면 `plt.subplot(2, 2, n)`(2행 2열의 n번째 칸)으로 그리기 직전에 칸을 고른다. 또는 차트 하나가 끝날 때마다 `show()`를 불러 끊어도 된다 — `show()`가 도화지를 비우기 때문이다.

### 2-5. 막대·산점도·히스토그램 한 단계 더

```python
plt.barh(classes, counts)                                   # 가로 막대 — 범주 이름이 길 때
plt.bar(classes, counts, bottom=base)                       # 누적 막대 — base 위에 쌓기
plt.scatter(x, y, s=sizes, c=values, cmap='viridis'); plt.colorbar()   # 크기·색에 값 싣기
plt.hist(heights, bins=30, density=True, range=(150, 190))  # 비율로·범위 고정
plt.axvline(np.mean(heights), color='red', linestyle='--')  # 평균 위치 세로선
```

| 확장 | 뜻 |
| --- | --- |
| `barh` | x·y를 바꾼 **가로 막대**. 대여소 이름처럼 긴 범주는 가로가 읽기 좋다 |
| `bottom=` | 앉힐 바닥 높이. 두 번 `bar`를 부르며 `bottom`에 앞 값을 주면 **누적 막대** |
| `c=`·`cmap=` | 점 색을 숫자 리스트로 주고 색 지도를 고른다. `colorbar()`가 색 눈금을 붙인다 |
| `density=True` | 막대 높이를 개수 대신 **비율**로 — 표본 수가 다른 두 분포를 겹쳐 비교할 때 |
| `range=` | 히스토그램의 가로축 범위를 고정. 난수라 실행마다 끝이 달라지는 것을 막는다 |
| `np.random.seed(0)` | 난수 고정. 같은 그림을 다시 그릴 수 있어 노트·보고서에 넣을 때 먼저 건다 |

### 2-6. 한글 폰트가 없는 환경 확인하기

```python
import matplotlib.font_manager as fm
[f.name for f in fm.fontManager.ttflist if 'Gothic' in f.name]   # 설치된 고딕 계열 이름 목록
```

폰트 이름을 잘못 적으면 오류 대신 **경고만 찍고 기본 폰트로 돌아가** 한글이 다시 네모로 나온다. 어떤 이름을 써야 할지 모를 때는 `font_manager`로 설치된 폰트 이름을 뽑아 본 뒤 그 문자열을 `family=`에 넣는다. 운영체제를 가리지 않게 하려면 `platform.system()`으로 분기해 윈도우는 `Malgun Gothic`, 맥은 `AppleGothic`, 리눅스는 `NanumGothic`을 고르는 코드를 파일 머리에 두는 방법이 흔하다.

## 3. 더 나아가 알면 좋은 것

### 3-1. pyplot 방식 vs 객체지향 방식

```python
fig, ax = plt.subplots(figsize=(7, 4))          # 도화지(fig)와 축(ax)을 명시적으로 받는다
ax.plot(epochs, train_loss, label="Train Loss")
ax.plot(epochs, val_loss, label="Val Loss")
ax.set_title("학습별 모델 손실 추세")
ax.set_xlabel("학습 수"); ax.set_ylabel("손실")
ax.grid(True); ax.legend()
plt.show()
```

이 수업의 `plt.title()`·`plt.xlabel()`처럼 **`plt.`로 직접 부르는 방식**은 "지금 활성화된 도화지"에 그리는 상태 기반(state-based) 방식이다. 짧은 코드에는 편하지만 차트가 둘 이상이면 "지금 어느 도화지인가"가 헷갈린다. 그래서 공식 문서가 권하는 쪽은 `fig, ax = plt.subplots()`로 **도화지와 축 객체를 변수로 받아** `ax.plot`·`ax.set_title`처럼 부르는 객체지향 방식이다. 함수 이름이 `title` → `set_title`, `xlabel` → `set_xlabel`로 바뀌는 것만 다르고 나머지는 같다. day05에서 배운 "인스턴스에 메소드를 부른다"가 그대로 적용되는 자리다.

### 3-2. 여러 차트 한 장에 — `subplots(행, 열)`

`plt.subplots(1, 2)`는 가로로 두 칸, `(2, 2)`는 네 칸짜리 도화지를 만들고 `ax[0]`·`ax[1]`(2차원이면 `ax[0, 1]`)로 칸을 고른다. 학습 손실과 정확도를 나란히 놓거나, 대여소 상위 10곳과 하위 10곳을 좌우로 비교할 때 쓴다. 칸끼리 축을 공유하는 `sharex=True`·`sharey=True`, 칸 사이 여백을 맞추는 `plt.tight_layout()`이 함께 따라온다.

### 3-3. 손실 곡선이 말해 주는 것 — 과적합

예제 숫자를 다시 보면 `train_loss`는 10회까지 계속 내려가고 `val_loss`는 8회(0.43)에서 바닥을 찍고 다시 오른다. 두 선이 벌어지기 시작하는 지점이 모델이 학습 데이터를 **외우기 시작한(과적합, overfitting)** 지점이고, 실무에서는 검증 손실이 최저인 epoch에서 학습을 멈추는 **조기 종료(early stopping)**를 건다. 차트를 그리는 이유가 바로 이것 — 숫자 20개를 표로 보면 놓치는 "꺾이는 지점"이 선으로 그리면 바로 보인다. 뒤의 AI 수업에서 이 그림을 수없이 다시 만나게 된다.

### 3-4. 맷플롯립 위의 라이브러리들

| 라이브러리 | 관계 |
| --- | --- |
| seaborn | 맷플롯립을 감싸 통계 차트(분포·상관·회귀선)를 한 줄로. `sns.lineplot(data=df, x=, y=)` |
| pandas `.plot()` | 2-3에서 본 것. 안쪽은 맷플롯립 |
| plotly | 브라우저에서 마우스로 확대·툴팁이 되는 대화형 차트. 맷플롯립과 별개 엔진 |
| Streamlit·Dash | 차트를 웹 페이지로 묶어 배포 |

전부 맷플롯립의 `figure`·`axes` 개념 위에 있거나 그것을 흉내 내므로, 이 수업의 일곱 단계를 알면 다른 라이브러리 문서도 같은 눈으로 읽힌다.

### 3-5. 산점도의 숫자판 — 상관계수 `np.corrcoef`

```python
r = np.corrcoef(x, y)[0, 1]      # -1 ~ 1
```

산점도가 "관계가 있어 보인다"를 눈으로 확인하는 도구라면, 상관계수는 그것을 숫자 하나로 적는 도구다. 1에 가까우면 오른쪽 위로 곧게 늘어선 모양, −1에 가까우면 오른쪽 아래, 0 근처면 구름처럼 흩어진 모양이다. 예제의 공부시간·시험점수는 0.99쯤 나온다. 다만 상관이 높다고 원인·결과가 정해지는 것은 아니고, 직선 관계만 잡으므로 곡선 관계는 산점도로 먼저 보는 편이 안전하다 — 그림과 숫자를 항상 같이 두는 이유다.

### 3-6. 분포를 요약하는 다른 그림 — `boxplot`

히스토그램이 분포의 모양 전체를 보여 준다면, `plt.boxplot(heights)`는 중앙값·사분위(25%·75%)·이상치를 상자 하나로 요약한다. 여러 그룹(부서별 나이, 대여소 그룹별 순유출)을 나란히 비교할 때는 히스토그램을 여러 장 겹치기보다 상자 여러 개를 한 축에 세우는 쪽이 읽기 쉽다. day07 Step 2에서 정렬본의 `int(n * 0.9)` 위치값으로 손으로 자르던 분위수가, 상자 그림에서는 상자의 위아래 변으로 그대로 보인다.

### 다음에 볼 키워드

- `plt.figure` · `plt.subplots` · `fig` · `ax` · `set_title`/`set_xlabel`
- `savefig` · `dpi` · `bbox_inches`
- `xlim`/`ylim` · `xticks`/`yticks` · `tight_layout`
- `bar` · `bar_label` · `barh` · `bottom=` · `width` · `alpha`
- `scatter` · `s` · `c=`/`cmap` · `colorbar` · `np.corrcoef` · 회귀
- `hist` · `bins` · `edgecolor` · `density` · `range` · `np.random.normal` · `np.random.seed` · 정규분포·표준편차
- `pie` · `boxplot` · `axvline`/`axhline`
- `rcParams` · `font_manager` · 스타일 시트 `plt.style.use`
- 과적합 · 조기 종료 · 학습 곡선

## 실습 파일

- `KDT_2026/2026_Python/day09/g-01.py` — `import matplotlib`·`__version__` 설치 확인, `import matplotlib.pyplot as plt`, 한글 폰트 `plt.rc('font', family='Malgun Gothic')`·`rcParams['axes.unicode_minus']` 설정, epoch 1~10의 `train_loss`·`val_loss` 리스트, `figure(figsize)` → `plot(label·color·linestyle·marker)` 두 번 → `title`·`xlabel`·`ylabel`·`grid`·`legend` → `show()` 일곱 단계 선 차트, 이어서 `classes`·`counts`로 `plt.bar(width=0.5, color=[…])`·`plt.bar_label(bars, padding=3, fontsize=8)`·`grid(True, alpha=0.5)` 막대 차트, 공부시간·시험점수 리스트로 `plt.scatter(color, s=80, alpha=0.8)` 산점도, `np.random.normal(loc=170, scale=5, size=1000)` 난수를 `plt.hist(bins=30, edgecolor='black')`로 그린 히스토그램

## 관련 노트

[[Python 정리본 인덱스]] · [[Python day08 판다스 데이터 전처리 중복 제거와 타입 변환]] · [[Python day06 넘파이 시작과 배열 생성]] · [[KDT_2026 학습 지도]]
