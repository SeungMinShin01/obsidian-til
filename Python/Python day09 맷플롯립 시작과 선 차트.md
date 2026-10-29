---
출처: Claude 분석
원본: KDT_2026/2026_Python/day09/g-01.py
작성일: 2026-10-29
tags: [학습, python]
---

# Python day09 — 맷플롯립 시작과 선 차트

> 실습 파일: `day09/g-01.py`
> 허브: [[Python 정리본 인덱스]] · 이전: [[Python day08 판다스 데이터 전처리 중복 제거와 타입 변환]] · 다음: (아직 없음)

넘파이(숫자 계산)·판다스(표 다루기)에 이어 세 번째 라이브러리, **맷플롯립(Matplotlib)**이다. 수업 첫 줄의 정의를 그대로 옮기면 "파이썬에서 시각적인 표현을 하는 라이브러리" — 지금까지 `print`로 숫자를 찍어 확인하던 결과를 **그림(차트)**으로 보는 도구다. 이 시간에 한 일은 셋이다. `import matplotlib`로 설치를 확인하고, 한글이 깨지지 않도록 폰트를 잡고, 학습 횟수(epoch)에 따른 손실(loss) 두 줄을 **선 차트** 하나에 겹쳐 그렸다. 차트 한 장을 만드는 일곱 단계가 번호로 적혀 있어서, 그 순서가 곧 맷플롯립의 기본 뼈대다.

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

### 2-4. 선 말고 다른 차트 — 함수 이름만 바뀐다

| 차트 | 함수 | 어울리는 자료 |
| --- | --- | --- |
| 선 | `plt.plot(x, y)` | 시간·순서에 따른 변화(손실, 주가, 월별 대여 건수) |
| 막대 | `plt.bar(x, height)` | 범주별 비교(부서별 인원, 대여소별 합계) |
| 산점도 | `plt.scatter(x, y)` | 두 값의 관계(방문 횟수 vs 구매 금액) |
| 히스토그램 | `plt.hist(values, bins=)` | 값의 분포(나이 분포, 손실 분포) |
| 원 | `plt.pie(sizes, labels=)` | 비율(부서 구성비) |

재료를 준비하고 `figure` → 그리기 함수 → 제목·축·범례 → `show`로 가는 뼈대는 전부 같고, 2번 자리의 함수만 바뀐다. 이 수업에서 선 차트 하나를 꼼꼼히 본 이유가 그것이다.

### 2-5. 한글 폰트가 없는 환경 확인하기

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

### 다음에 볼 키워드

- `plt.figure` · `plt.subplots` · `fig` · `ax` · `set_title`/`set_xlabel`
- `savefig` · `dpi` · `bbox_inches`
- `xlim`/`ylim` · `xticks`/`yticks` · `tight_layout`
- `bar` · `scatter` · `hist` · `pie` · `boxplot`
- `rcParams` · `font_manager` · 스타일 시트 `plt.style.use`
- 과적합 · 조기 종료 · 학습 곡선

## 실습 파일

- `KDT_2026/2026_Python/day09/g-01.py` — `import matplotlib`·`__version__` 설치 확인, `import matplotlib.pyplot as plt`, 한글 폰트 `plt.rc('font', family='Malgun Gothic')`·`rcParams['axes.unicode_minus']` 설정, epoch 1~10의 `train_loss`·`val_loss` 리스트, `figure(figsize)` → `plot(label·color·linestyle·marker)` 두 번 → `title`·`xlabel`·`ylabel`·`grid`·`legend` → `show()` 일곱 단계 선 차트

## 관련 노트

[[Python 정리본 인덱스]] · [[Python day08 판다스 데이터 전처리 중복 제거와 타입 변환]] · [[Python day06 넘파이 시작과 배열 생성]] · [[KDT_2026 학습 지도]]
