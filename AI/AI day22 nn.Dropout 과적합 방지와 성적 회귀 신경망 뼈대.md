---
출처: Claude 분석
원본: KDT_2026/2026_Python/day22/dl-2.ipynb(4셀 — 학생 성적 회귀 DNN 시작 부분)
작성일: 2026-11-23
tags: [학습, ai, python]
---

# AI day22 — nn.Dropout 과적합 방지와 성적 회귀 신경망 뼈대

> 실습 파일: `day22/dl-2.ipynb` (마지막 셀 — `student-mat.csv` 회귀, 1)~2)까지 작성·3)~7)은 주석 계획)
> 허브: [[AI 정리본 인덱스]] · 이전: [[AI day22 nn.Sequential 와인 이진 분류와 BCEWithLogitsLoss·AdamW 학습 루프]] · 다음: (아직 없음)

와인 이진 분류를 끝까지 돌린 뒤, 같은 파일 마지막 셀에서 **두 번째 문제**가 시작된다. 자료는 day19 군집에서 쓴 UCI 학생 성적 `student-mat.csv`이고, 이번엔 공부 시간·결석·1차·2차 성적 네 열로 **기말 성적 `G3`를 맞히는 회귀**다. 셀은 1) 텐서 변환과 2) 신경망 컨테이너의 앞 세 층까지 쓰여 있고, 3) 손실 함수 ~ 7) 추론은 번호와 한 줄 설명만 주석으로 적혀 있다 — 다음 수업이 이어서 채울 뼈대다. 이 셀에서 새로 등장한 것은 둘이다. **`nn.Dropout(p=0.2)`** 층과, 분류가 아니라 **회귀를 신경망으로** 푸는 설정. 앞 노트와 무엇이 같고 무엇이 달라지는지를 중심으로 정리하고, 비어 있는 3)~7)은 앞 노트의 틀로 어떻게 채워질지 2단에 미리 적어 둔다.

## 1. 배운 내용

### 1-1. 자료 — day19의 학생 성적을 회귀 문제로

```python
import pandas as pd
url = 'https://raw.githubusercontent.com/arunk13/MSDA-Assignments/master/IS607Fall2015/Assignment3/student-mat.csv'
df = pd.read_csv(url, sep=';')
X = df[['studytime', 'absences', 'G1', 'G2']]
Y = df['G3']

from sklearn.model_selection import train_test_split
X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size=0.2, random_state=42)

from sklearn.preprocessing import StandardScaler
ss = StandardScaler()
X_train_scaled = ss.fit_transform(X_train)
X_test_scaled  = ss.transform(X_test)
```

day19 `s-13.py`와 같은 파일(395명 × 33열, 구분자가 쉼표가 아니라 **`sep=';'`**)인데 쓰는 방식이 다르다. day19는 `G3`까지 다섯 열을 전부 특성으로 넣고 정답 없이 그룹을 나눴고(비지도), 오늘은 `G3`를 **타깃**으로 떼어 내고 나머지 네 열로 맞힌다(지도·회귀). 같은 CSV가 문제 설정에 따라 군집 자료가 되기도, 회귀 자료가 되기도 한다.

| | day19 `s-13.py` | day22 `dl-2.ipynb` |
| --- | --- | --- |
| 쓰는 열 | `studytime`·`absences`·`G1`·`G2`·`G3` 다섯 | 특성 넷 + 타깃 `G3` |
| 문제 | 비지도 군집(KMeans·HDBSCAN) | 지도 **회귀**(신경망) |
| 분할 | `train_test_split(X, test_size=0.02)` 둘만 | `train_test_split(X, Y, 0.2, 42)` 넷 |
| `stratify` | — | **없음** — 회귀 타깃은 연속값이라 층화할 범주가 없다 |

앞 노트의 와인 분류에 있던 `stratify=Y`가 빠진 것이 첫 차이다. `G3`는 0~20점 연속 숫자이니 비율을 맞출 클래스가 없다(day12 `train_test_split`과 같은 꼴). 표준화는 그대로 — G1·G2는 0~20, 결석은 0~75, 공부 시간은 1~4로 단위가 제각각이라 신경망에 넣기 전에 반드시 맞춘다.

### 1-2. 텐서 변환 — 특성 넷, 타깃은 실수 그대로

```python
# 1) 딥러닝 하기 위한 파이토치 특성과 타깃 차원 일치화
X_train = torch.tensor(X_train_scaled, dtype=torch.float32)
X_test  = torch.tensor(X_test_scaled,  dtype=torch.float32)
Y_train = torch.tensor(Y_train.values, dtype=torch.float32)
Y_test  = torch.tensor(Y_test.values,  dtype=torch.float32)
```

앞 노트 1-2와 같은 네 줄이다. 분류에서 0.0 / 1.0이던 타깃이 여기선 **점수 그대로**(0~20)의 `float32`가 된다 — 회귀는 정답 숫자를 그대로 맞히는 문제이니 라벨 변환이 필요 없다.

회귀에서도 주석 그대로 **"특성과 타깃 차원 일치화"**가 목표다. 출력층 `nn.Linear(h, 1)`은 `(N, 1)`을 내놓으므로 `MSELoss`가 원소끼리 짝을 맞추려면 타깃도 `(N, 1)`이어야 한다. 타깃이 `(N,)` 1차원이면 파이토치가 두 모양을 브로드캐스팅으로 억지로 맞추면서 `Using a target size … different to the input size` 경고를 내고 손실이 전혀 다른 값으로 계산되므로, 회귀에서도 `.unsqueeze(1)`로 열 축을 붙여 두는 편이 안전하다(앞 노트 1-2 표의 둘째 줄과 같은 규칙).

### 1-3. `nn.Dropout(p=0.2)` — 매 순전파마다 은닉 뉴런 20 %를 꺼 버린다

```python
# 2) 신경망 DNN 레이어 컨테이너 설정
import torch.nn as nn
# model = nn.Sequential( 입력층 -> 은닉층 -렐루/드롭아웃-> 은닉층 -> 출력층 )
model = nn.Sequential(
    nn.Linear(4, 32),      # 학습할 특성의 수로 입력층 시작 — 파생 피처 32개는 자유
    nn.ReLU(),             # 활성화 함수
    nn.Dropout(p=0.2),     # 매 순전파마다 은닉층의 20 %를 무작위 비활성화 — 과적합 방지
)
```

첫 `Linear`의 입력 4는 특성 수(앞 노트 1-3의 규칙), 32는 자유롭게 정한 은닉 크기다. 새로 들어온 셋째 층이 **드롭아웃**이다.

| 항목 | 내용 |
| --- | --- |
| 하는 일 | 학습 중 순전파마다 앞 층 출력 32개 중 **무작위 20 %(약 6개)를 0으로** 만든다. 어느 6개인지는 매 바퀴 다르다 |
| 왜 | 특정 뉴런 몇 개에 의존해 학습 자료를 외우는 것을 막는다 — 매번 다른 부분집합으로 학습하니 **작은 신경망 여럿을 평균 내는 효과**(앙상블) |
| 학습 중 | 살아남은 80 %에 `1 / (1 − p)` = 1.25를 곱해 기대값을 유지(inverted dropout) |
| **`eval()` 중** | **아무 일도 하지 않는다** — 전부 통과. 그래서 앞 노트 1-7의 `model.eval()`이 이 층부터 **실제로 의미**를 갖는다 |
| 매개변수 | 0 — 학습하는 숫자가 없다. `p`만 하이퍼파라미터 |
| 위치 | 활성화 함수 **뒤**, 다음 `Linear` 앞 — 꺼지는 것은 "뉴런의 출력"이다 |

규제의 계보로 보면 day13 릿지·라쏘(기울기 크기에 벌점) → day17 트리의 `max_depth`·`min_samples_leaf`(가지치기) → day18 `early_stopping`(멈추기)에 이어 신경망 고유의 넷째 방법이다. 셋 다 "학습 자료를 너무 잘 맞히는 것을 방해한다"는 점에서 같고, 드롭아웃은 **매개변수가 아니라 연결을 무작위로 끊는** 방식이라는 점이 다르다. 비율 0.2~0.5가 흔히 쓰이고, 입력층 바로 뒤에는 보통 두지 않는다(특성 자체를 지우면 정보가 사라진다).

주석 "`-렐루/드롭아웃->`"처럼 `Linear → ReLU → Dropout`이 **한 묶음**으로 반복되는 것이 깊은 신경망의 기본 리듬이다. 계획된 모양은 `입력층 → 은닉층 → (렐루/드롭아웃) → 은닉층 → 출력층`이니, 이 셀이 이어지면 둘째 `Linear(32, …)`와 활성화, 그리고 `Linear(…, 1)` 출력층이 뒤에 붙는다 — 아직 **출력층이 없으니 지금 상태로 `model(X)`를 부르면 `(N, 32)`가 나온다**는 점만 기억해 두면 다음 수업에서 이어 붙일 자리가 분명하다.

### 1-4. ANN에서 DNN으로 — 이름이 바뀐 이유

앞 노트 주석은 **ANN**(인공신경망), 이 셀 주석은 **DNN**(Deep Neural Network, 심층 신경망)이다. 같은 `nn.Sequential`인데 이름이 달라진 것은 은닉층이 **둘 이상**으로 깊어지기 때문이다.

| 이름 | 구조 | 이 파일에서 |
| --- | --- | --- |
| ANN | 입력 → 은닉 1개 → 출력 | 와인 분류 `Linear(3,16) → ReLU → Linear(16,1)` |
| **DNN** | 입력 → 은닉 **2개 이상** → 출력 (+ 드롭아웃·배치 정규화 등) | 성적 회귀 `Linear(4,32) → ReLU → Dropout → Linear(32,…) → … → Linear(…,1)` 계획 |

"딥러닝"의 딥이 바로 이 은닉층 수다. 층이 깊어질수록 더 복잡한 경계를 그릴 수 있지만 매개변수가 늘어 과대적합이 쉬워지고, 그래서 깊어지는 순간 드롭아웃이 함께 들어오는 것이 자연스럽다 — 이 셀의 세 층이 그 두 변화를 한 번에 보여 준다.

### 1-5. 비어 있는 3)~7) — 앞 노트와 바뀌는 자리 표

```python
# 3) 손실함수: MSELoss()
# 4) 옵티마이저 ; optimizer = optim.AdamW( model.parameters(), lr=학습률)
# 5) 에포크(학습수) 단위 학습( 순전파 -> 역전파)
# 6) 모델 평가. model.train() 학습모드 , model.eval() 평가/추론모드
# 7) 모델 추론
```

번호 다섯 개가 앞 노트의 3)~6)과 같은 자리이고, 7) 추론이 하나 더 붙었다. 분류 → 회귀로 바뀌면서 달라지는 칸만 추리면 이렇다.

| 단계 | 와인 분류(앞 노트) | 성적 회귀(이 셀 계획) | 바뀌는 이유 |
| --- | --- | --- | --- |
| 출력층 | `Linear(16, 1)` 로짓 | `Linear(…, 1)` 점수 | 모양은 같다 — 해석만 "확률 전 단계" → "예측값" |
| 3) 손실 | `BCEWithLogitsLoss` | **`MSELoss`** | day21의 그 손실 — `(예측 − 정답)²` 평균 |
| 4) 옵티마이저 | `AdamW(lr=0.01)` | `AdamW` 그대로 | 문제 종류와 무관 |
| 5) 학습 루프 | 5박자 | **5박자 그대로** | `train()`이 이번엔 드롭아웃을 **켠다** |
| 6) 평가 | `sigmoid ≥ 0.5` → `f1_score` | 출력 **그대로** → `r2_score`·RMSE | 확률·임계값이 없다 |
| 7) 추론 | — | 새 학생 한 줄 → 같은 스케일러 → 텐서 → `eval()`·`no_grad` → 점수 | day14 `s-05.py` 서빙과 같은 그림 |

핵심은 **학습 루프 5박자는 문제가 바뀌어도 한 글자도 바뀌지 않는다**는 점이다. 바뀌는 것은 손실 함수 한 줄과 평가에서 출력을 읽는 방법뿐이다 — day12 "알고리즘은 ④ 클래스 이름만 바뀐다"의 딥러닝판이다.

## 2. 추가로 알면 좋은 활용법

### 2-1. 뼈대 채우기 — 3)~7)을 앞 노트 틀로 써 보면

다음 수업을 기다리기 전에 주석 계획대로 채워 보면 이렇게 된다. 출력층을 붙이고, 타깃에 열 축을 더하고, 손실만 바꾼다.

```python
Y_train = Y_train.unsqueeze(1)            # (316,) → (316, 1)  — 1-2의 차원 일치
Y_test  = Y_test.unsqueeze(1)

model = nn.Sequential(
    nn.Linear(4, 32), nn.ReLU(), nn.Dropout(p=0.2),   # 은닉층 1
    nn.Linear(32, 16), nn.ReLU(),                      # 은닉층 2  ← "은닉층 -> 출력층"의 그 은닉층
    nn.Linear(16, 1),                                  # 출력층: 점수 하나
)
criterion = nn.MSELoss()                                                 # 3)
optimizer = optim.AdamW(model.parameters(), lr=0.01)                     # 4)

for epoch in range(2000):                                                # 5)
    model.train()                       # 드롭아웃 ON
    optimizer.zero_grad()
    pred = model(X_train)
    loss = criterion(pred, Y_train)
    loss.backward()
    optimizer.step()
    if epoch % 100 == 0:
        print(epoch, loss.item())       # MSE — 단위는 점²

model.eval()                            # 드롭아웃 OFF                   # 6)
with torch.no_grad():
    train_pred = model(X_train).numpy()
    test_pred  = model(X_test).numpy()
from sklearn.metrics import r2_score, mean_squared_error
import numpy as np
print(r2_score(Y_train.numpy(), train_pred), r2_score(Y_test.numpy(), test_pred))
print(np.sqrt(mean_squared_error(Y_test.numpy(), test_pred)))            # RMSE, 단위 점
```

`loss.item()`이 찍는 MSE는 점의 제곱 단위라 읽기 어렵고, `np.sqrt`를 씌운 RMSE가 "평균 몇 점 틀리나"로 읽힌다(day12 2-2의 그 이야기). R²는 day12부터 쓰던 그대로 — 파이토치가 평가지표를 따로 주지 않으니 사이킷런으로 잰다.

드롭아웃이 있는 모델은 **학습 중 손실과 `eval()` 뒤 점수가 다르게 나오는 것이 정상**이다. 학습 중엔 뉴런 20 %가 꺼진 채 계산한 손실이고, 평가 때는 전부 켜서 계산하므로 보통 평가 쪽이 좋다. 그래서 학습 중 `print`한 손실로 성능을 말하지 않고, 꼭 `eval()`로 다시 재는 습관이 필요하다.

### 2-2. 7) 추론 — 새 학생 한 명

```python
new_student = pd.DataFrame([[2, 4, 12, 13]], columns=['studytime', 'absences', 'G1', 'G2'])
x_new = torch.tensor(ss.transform(new_student), dtype=torch.float32)   # 같은 스케일러
model.eval()
with torch.no_grad():
    print(model(x_new).item())        # 예측 G3 (점)
```

학습 때 쓴 **같은 `ss`로 `transform`**하는 것이 전부다(day13 "fit은 학습용에만"). 열 이름을 맞춘 데이터프레임으로 넘기면 열 순서 실수를 스케일러가 잡아 준다. 사이킷런 파이프라인이 전처리와 모델을 한 객체로 묶어 주던 편의가 파이토치엔 없으니, 서빙할 때는 **스케일러(`joblib`)와 가중치(`state_dict`)를 따로 저장해 둘 다 불러와야** 한다 — day16 FastAPI 서비스에 올린다면 `Service.py` 생성자에서 두 파일을 함께 읽는 모양이 된다.

### 2-3. 드롭아웃 비율 바꿔 보기 — 효과를 눈으로

`p`를 0 · 0.2 · 0.5로 바꿔 학습 R²와 테스트 R²를 나란히 놓으면 드롭아웃이 하는 일이 보인다. 자료가 316행으로 작고 모델이 커질수록 `p=0`에선 학습 R²만 치솟고 테스트는 떨어지는 간격이 생기고, `p`를 올리면 학습 쪽이 내려오며 간격이 좁아진다. 너무 올리면(0.5 이상) 둘 다 내려가는 **과소적합**이 된다 — day13 `alpha`를 로그 눈금으로 훑던 것과 같은 그림이고, 격차가 가장 작은 `p`가 아니라 **테스트 점수가 가장 높은 `p`**를 고른다. 비교할 때 `torch.manual_seed`를 고정해야 초기 가중치 차이가 섞이지 않는다.

### 2-4. `Dropout` 말고 `BatchNorm1d` — 함께 쓰는 또 하나의 "모드 스위치" 층

`nn.BatchNorm1d(32)`는 배치마다 은닉층 출력을 표준화해 학습을 안정시키는 층으로, 드롭아웃과 함께 `train()`/`eval()`에 따라 동작이 바뀌는 대표 층이다(학습 중엔 배치 통계, 평가 중엔 누적 이동 평균). `Linear → BatchNorm → ReLU → Dropout` 순서가 흔하고, 둘을 같이 쓸 때는 드롭아웃 비율을 낮추는 편이다. 미니배치 크기가 아주 작으면(수십 미만) 배치 통계가 불안정해져 오히려 해롭다는 점도 함께 기억해 둔다.

## 3. 더 나아가 알면 좋은 것

### 3-1. 드롭아웃이 작동하는 원리 — 앙상블과 공적응 방지

드롭아웃 논문(Srivastava 외, 2014)의 설명은 두 갈래다. 하나는 매 바퀴 다른 부분 신경망을 학습해 `2^n`개 모델을 **암묵적으로 평균**하는 앙상블 효과(day17 랜덤 포레스트가 특성·표본을 무작위로 빼고 트리를 여럿 키우던 것과 닮았다). 다른 하나는 뉴런들이 "옆 뉴런이 있을 때만 맞는" 식으로 서로 기대는 **공적응(co-adaptation)** 을 막아 각 뉴런이 혼자서도 쓸모 있는 특징을 배우게 하는 것. 평가 때 전부 켜고 `1/(1−p)` 보정을 해 두면 평균 모델을 한 번의 순전파로 근사하는 셈이다.

### 3-2. 표 자료에서 신경망 vs 부스팅

특성 4개·316행짜리 표 자료에서는 day18의 LightGBM이 신경망보다 적은 수고로 더 좋은 R²를 내는 경우가 많다. 트리 모델은 표준화도 필요 없고 범주형도 `category` 타입으로 바로 먹는다(day18). 표 자료에서 신경망이 이기는 자리는 행이 수십만 이상이거나, 임베딩으로 고차원 범주를 다루거나, 다른 신경망(이미지·텍스트)과 한 모델로 묶어야 할 때다 — 그래서 실무에선 "표는 부스팅, 비정형은 딥러닝"이 기본 출발점이고, 이 수업은 **같은 문제를 신경망으로 풀면 코드가 어떻게 생기는지**를 익히는 데 뜻이 있다.

### 3-3. 회귀 출력층의 변형들

- 타깃 범위가 정해져 있으면(0~20점) 출력에 `sigmoid × 20`을 씌우거나 예측 뒤 `clamp(0, 20)`으로 자를 수 있다(day13 연습의 `np.clip`과 같은 발상).
- 이상치가 많으면 `MSELoss` 대신 `L1Loss`(MAE)나 `HuberLoss`/`SmoothL1Loss`가 안정적이다(day21 2-3 표).
- 타깃이 치우쳤으면(의료비처럼 오른쪽 꼬리) `log1p` 변환 뒤 학습하고 `expm1`로 되돌린다 — day16·18의 로그 타깃 이야기.
- 여러 값을 동시에 맞히면 `Linear(h, k)`로 출력을 `k`개 — 다중 출력 회귀는 손실이 알아서 열별 평균을 낸다.

### 3-4. 다음에 볼 키워드

- `nn.BatchNorm1d`·`nn.LayerNorm` — 정규화 층과 `train()`/`eval()`
- `weight_decay`(AdamW) vs 드롭아웃 — 두 규제를 함께 쓸 때의 균형
- `torch.manual_seed`·`torch.use_deterministic_algorithms` — 드롭아웃 무작위성과 재현성
- `nn.Module` 상속으로 `Linear → ReLU → Dropout` 블록 함수화 (`make_block(in, out, p)`)
- `random_split`·`DataLoader` — 검증 세트 분리와 미니배치 (앞 노트 2-3)
- `ReduceLROnPlateau` — 검증 손실이 멈추면 학습률 낮추기
- 몬테카를로 드롭아웃 — `eval()`에서도 드롭아웃을 켜 예측 불확실성 추정
- 표 자료 딥러닝: `nn.Embedding` 범주 임베딩·TabNet·FT-Transformer

## 실습 파일

- `KDT_2026/2026_Python/day22/dl-2.ipynb` — 마지막 셀: `read_csv(url, sep=';')` UCI `student-mat.csv` → `X = df[['studytime', 'absences', 'G1', 'G2']]`·`Y = df['G3']` → `train_test_split(test_size=0.2, random_state=42)`(층화 없음) → `StandardScaler` `fit_transform`/`transform` → 1) `torch.tensor(…, dtype=torch.float32)` 넷(특성·타깃) → 2) `nn.Sequential(nn.Linear(4, 32), nn.ReLU(), nn.Dropout(p=0.2))` + 주석 `입력층 -> 은닉층 -렐루/드롭아웃-> 은닉층 -> 출력층` → 3) `MSELoss()` · 4) `optim.AdamW(model.parameters(), lr=학습률)` · 5) 에포크 단위 학습(순전파 → 역전파) · 6) `model.train()`/`model.eval()` 평가 · 7) 모델 추론 — 3)~7)은 주석 계획만

## 관련 노트

[[AI 정리본 인덱스]] · [[AI day22 nn.Sequential 와인 이진 분류와 BCEWithLogitsLoss·AdamW 학습 루프]] · [[AI day19 KMeans 군집으로 학생 그룹 나누기와 엘보우·HDBSCAN]] · [[AI day21 MSELoss 손실·backward 역전파와 경사하강법 한 걸음 갱신]] · [[KDT_2026 학습 지도]]
