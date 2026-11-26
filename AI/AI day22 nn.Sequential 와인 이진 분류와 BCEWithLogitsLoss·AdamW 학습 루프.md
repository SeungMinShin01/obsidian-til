---
출처: Claude 분석
원본: KDT_2026/2026_Python/day22/dl-2.ipynb(1~3셀 — 와인 이진 분류 신경망)
작성일: 2026-11-23
tags: [학습, ai, python]
---

# AI day22 — nn.Sequential 와인 이진 분류와 BCEWithLogitsLoss·AdamW 학습 루프

> 실습 파일: `day22/dl-2.ipynb` (앞 세 셀 — 자료 준비·`nn.Sequential` 학습 루프·`model.eval()` 평가)
> 허브: [[AI 정리본 인덱스]] · 이전: [[AI day21 Hugging Face datasets로 LBox 판결문 데이터셋 불러오기]] · 다음: [[AI day22 nn.Dropout 과적합 방지와 성적 회귀 신경망 뼈대]]

day21은 표본 하나·특성 하나·가중치 둘(`w`·`b`)로 학습 한 바퀴를 손으로 돌렸다. 오늘은 그 바퀴를 **진짜 자료**(와인 6,497병 × 특성 3개)에 **진짜 신경망**(`nn.Sequential`로 쌓은 층 두 개)으로 1만 번 돌린다. 코드의 뼈대는 day21 2-1에서 미리 적어 둔 `for epoch` 루프와 3-1의 `optimizer.step()` 5박자 그대로이고, 바뀐 것은 `w`·`b`가 `nn.Linear` 안으로 들어갔다는 점, 손실이 `MSELoss`에서 이진 분류용 `BCEWithLogitsLoss`로 바뀐 점, 갱신을 `optim.AdamW`가 대신하는 점 셋이다. 자료는 day17 결정 트리·랜덤 포레스트·부스팅에서 쓰던 혼공머신 `wine.csv` 그대로라, 같은 문제를 신경망으로 풀면 어디쯤 나오는지 비교할 수 있다.

## 1. 배운 내용

### 1-1. 자료 준비는 사이킷런 그대로 — 바뀐 건 마지막 네 줄

```python
import pandas as pd
url = 'https://raw.githubusercontent.com/rickiepark/hg-mldl/master/wine.csv'
df = pd.read_csv(url)

X = df[['alcohol', 'sugar', 'pH']]
Y = df['class']                     # (0: 레드와인, 1: 화이트와인)

from sklearn.model_selection import train_test_split
X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size=0.2, random_state=42, stratify=Y)

from sklearn.preprocessing import StandardScaler
ss = StandardScaler()
X_train_scaled = ss.fit_transform(X_train)
X_test_scaled = ss.transform(X_test)
```

여기까지는 day14~17과 한 글자도 다르지 않다. `read_csv(url)`로 6,497병을 읽고, 특성 세 열(알코올·당도·pH)과 타깃 `class`(레드 0 : 화이트 1 = 25 : 75)를 나누고, `stratify=Y`로 비율을 지키며 8 : 2로 자르고, `StandardScaler`를 학습용에만 `fit`한다. 딥러닝이라고 자료 준비가 달라지는 것이 아니다 — **신경망은 사이킷런 모델 자리에 들어오는 또 하나의 모델**이고, 그 앞단은 지금까지 배운 판다스·사이킷런이 그대로 맡는다.

표준화가 트리 계열(day17)에서는 생략 가능했지만 신경망에서는 **다시 필수**가 된다. 경사하강법으로 가중치를 고치는 모델이라 특성 크기가 들쭉날쭉하면(당도 0.6~65 vs pH 2.7~4) 큰 특성 쪽 기울기가 학습을 휘어잡는다. day13의 "규제의 전제"가 여기선 "경사하강법의 전제"로 돌아온 셈이다.

### 1-2. 텐서로 바꾸기 — 특성과 타깃의 차원을 맞춘다

```python
# 1) 딥러닝 하기 위한 파이토치
print(X_train.shape)   # (5197, 3)
print(Y_train.shape)   # (5197,)    ← 신경망(DL)에서는 특성과 타깃 차원수 일치
import torch
X_train = torch.tensor(X_train_scaled, dtype=torch.float32)
X_test  = torch.tensor(X_test_scaled,  dtype=torch.float32)
Y_train = torch.tensor(Y_train.values, dtype=torch.float32).unsqueeze(1)
Y_test  = torch.tensor(Y_test.values,  dtype=torch.float32).unsqueeze(1)
print(X_train.shape)   # torch.Size([5197, 3])
print(Y_train.shape)   # torch.Size([5197, 1])
```

day21 1-2·1-3에서 따로 연습한 `torch.tensor(…, dtype=torch.float32)`와 `unsqueeze`가 여기서 한꺼번에 쓰인다. 포인트는 수업 주석의 한 줄 — **신경망에서는 특성과 타깃의 차원 수를 맞춘다**.

| 변수 | 변환 전 | 변환 후 | 왜 |
| --- | --- | --- | --- |
| `X_train_scaled` | 넘파이 `(5197, 3)` | `torch.Size([5197, 3])` | 스케일러 출력은 이미 넘파이라 그대로 텐서로 |
| `Y_train` | 판다스 Series `(5197,)` | `torch.Size([5197, 1])` | `.values`로 넘파이 → 텐서 → `unsqueeze(1)`로 열 축 추가 |

사이킷런은 타깃이 1차원 `(5197,)`이어도 알아서 받았지만, 파이토치의 출력층 `nn.Linear(16, 1)`은 표본마다 숫자 **하나씩을 열로 가진** `(5197, 1)` 모양을 내놓는다. 손실 함수가 예측 `(5197, 1)`과 정답을 원소끼리 짝지어야 하니 정답도 `(5197, 1)`이어야 한다. `.values`를 먼저 부르는 것은 Series를 넘파이 배열로 꺼내는 단계다 — `torch.tensor`는 넘파이·리스트를 받지, 인덱스가 붙은 Series를 바로 받으라고 하면 경고가 나거나 모양이 뒤틀릴 수 있다.

`dtype=torch.float32`를 타깃에도 붙인 이유는 다음 손실 함수 때문이다. `BCEWithLogitsLoss`는 정답을 0.0 / 1.0 **실수**로 받는다(다중 분류의 `CrossEntropyLoss`가 `torch.long` 정수 라벨을 받는 것과 다르다 — day21 2-3 표).

### 1-3. `nn.Sequential` — 층을 순서대로 담는 컨테이너

```python
# 2) 신경망 ANN 레이어 컨테이너 설정
import torch.nn as nn
# model = nn.Sequential( 입력층 -> 은닉층 -> 출력층 )
model = nn.Sequential(
    nn.Linear(3, 16),   # 입력층: 최초로 학습할 피처/특성 수 → 파생 피처 16개
    nn.ReLU(),          # 활성화 함수: 음수는 0으로, 양수는 그대로 통과
    nn.Linear(16, 1)    # 출력층: 앞 레이어의 피처 수 → 결과 수
)
```

day21에서 `w`·`b`를 텐서 두 개로 직접 들고 있었는데, 그 자리를 `nn.Linear`가 대신한다. `nn.Linear(in, out)`은 안에 `(out, in)` 모양의 가중치 행렬과 `(out,)` 편향을 들고 있고, 입력 `x`에 `x @ W.T + b`를 계산한다 — day21의 `x * w + b`가 행렬 버전으로 커진 것뿐이다. `requires_grad=True`도 자동으로 붙어 있다.

| 층 | 모양 | 매개변수 수 | 역할 |
| --- | --- | --- | --- |
| `nn.Linear(3, 16)` | `(5197, 3)` → `(5197, 16)` | 3 × 16 + 16 = **64** | 특성 3개를 파생 특성 16개로 섞어 펼침 (입력층 → 은닉층) |
| `nn.ReLU()` | 모양 불변 | 0 | 음수를 0으로 잘라 **비선형성** 부여 |
| `nn.Linear(16, 1)` | `(5197, 16)` → `(5197, 1)` | 16 × 1 + 1 = **17** | 16개를 숫자 하나(로짓)로 모음 (은닉층 → 출력층) |

합쳐서 **81개**의 숫자를 학습한다. day14 로지스틱 회귀의 `coef_` 3개 + `intercept_` 1개 = 4개와 비교하면 20배인데, 그 차이가 곧 "직선 하나" 대 "직선 16개를 꺾어 이어 붙인 경계"의 차이다.

수업 주석에서 챙길 두 가지.

- **첫 `Linear`의 입력 수는 특성 수와 같아야 한다**(3). 틀리면 `mat1 and mat2 shapes cannot be multiplied` 오류가 바로 난다. 은닉층 크기 16은 자유롭게 정하는 하이퍼파라미터이고, **다음 층의 입력 수는 앞 층의 출력 수**(16)를 그대로 받는다 — 레고 블록처럼 앞 블록 끝과 뒤 블록 머리가 맞아야 한다.
- **`nn.ReLU()`가 층 사이에 없으면 두 `Linear`는 합쳐서 `Linear(3, 1)` 하나와 같다**(day21 1-4 "비선형성이 없으면 층을 쌓아도 선형식 하나"). 16개로 펼친 의미가 사라진다.

`nn.Sequential`은 괄호 안에 넣은 순서대로 입력을 흘려보내는 **컨테이너**다. `model(X_train)`이라고 부르면 `Linear → ReLU → Linear`를 차례로 지나 `(5197, 1)` 텐서가 나온다. 이름이 **ANN**(Artificial Neural Network, 인공신경망)인 것은 이 구조 — 입력층·은닉층·출력층 — 가 신경망의 가장 기본 형태이기 때문이다.

### 1-4. 출력층에 시그모이드가 없는 이유 — `BCEWithLogitsLoss`

```python
# 3) 손실함수: 시그모이드(2진분류) + Cross Entropy 하나로 합친
criterion = nn.BCEWithLogitsLoss()
```

day14 로지스틱 회귀는 `z = w·x + b`에 시그모이드를 씌워 0~1 확률을 만들고, 그 확률과 정답의 거리(로그 손실)를 줄였다. 파이토치에서 같은 일을 하려면 출력층 뒤에 `nn.Sigmoid()`를 붙이고 `nn.BCELoss()`로 손실을 재면 된다 — 그런데 수업은 그 둘을 **합친 하나**를 쓴다.

| 조합 | 출력층 뒤 | 손실 함수 | 비고 |
| --- | --- | --- | --- |
| 나눠 쓰기 | `nn.Sigmoid()` | `nn.BCELoss()` | 확률이 0이나 1에 바싹 붙으면 `log(0)`로 수치가 불안정 |
| **합쳐 쓰기(수업)** | 없음 — 로짓 그대로 | `nn.BCEWithLogitsLoss()` | 안에서 시그모이드 + 로그를 한 번에 계산해 **수치 안정** |

이름의 **로짓(logit)**은 시그모이드를 **씌우기 전**의 날 숫자다. 출력층 `nn.Linear(16, 1)`이 내놓는 값이 −∞~+∞ 어디든 될 수 있는 로짓이고, 그 로짓을 손실 함수에 그대로 넘기면 함수 안에서 σ(z)를 거쳐 **이진 크로스 엔트로피(BCE)** — `−[y·log p + (1−y)·log(1−p)]` 의 평균 — 를 돌려준다. day21 2-3 표에 "활성화를 품은 손실이 관례·마지막 층 활성화 없음"이라고 적어 둔 것이 바로 이 자리다.

그래서 **`model`은 확률을 내놓지 않는다.** 이 점이 1-6 평가 코드에서 `torch.sigmoid(model(...))`를 다시 씌우는 이유가 된다 — 학습 때는 손실 함수가 시그모이드를 품었으니, 추론 때 사람이 읽을 확률이 필요하면 밖에서 한 번 씌운다.

`criterion`이라는 변수명은 day21과 같다(기준·판정이라는 뜻의 관례).

### 1-5. `optim.AdamW` — 갱신 셀이 한 줄로 접힌다

```python
# 4) 옵티마이저
import torch.optim as optim
optimizer = optim.AdamW(model.parameters(), lr=0.01)
```

day21 1-3에서 `with torch.no_grad(): w -= lr * w.grad; b -= lr * b.grad`로 직접 썼던 갱신이, 옵티마이저 객체 하나로 접힌다. `model.parameters()`는 `nn.Sequential` 안의 가중치·편향 텐서 **81개 값(텐서 4개)** 을 차례로 넘겨주는 제너레이터이고, 옵티마이저는 그 텐서들을 기억해 두었다가 `step()`이 불릴 때마다 각자의 `.grad`를 보고 값을 고친다.

| 옵티마이저 | 갱신 식(요지) | 특징 |
| --- | --- | --- |
| `SGD` | `w -= lr × grad` | day21 손계산과 같음 — 학습률 하나에 전부 달림 |
| `Adam` | 기울기의 **평균(1차 모멘트)** 과 **제곱 평균(2차 모멘트)** 을 지수이동평균으로 추적해, 매개변수마다 보폭을 다르게 | 학습률에 덜 민감·수렴 빠름·기본 선택 |
| **`AdamW`(수업)** | Adam + **가중치 감쇠(weight decay)를 기울기와 분리**해 적용 | Adam의 L2 규제 구현 문제를 고친 판 — 트랜스포머·최근 모델의 표준 |

끝의 **W**가 weight decay다. day13 릿지가 "기울기 크기에 벌점"을 매기던 L2 규제의 딥러닝판이라고 보면 되고, `AdamW`는 그 벌점을 Adam의 적응형 보폭과 섞지 않고 따로 빼서 적용한다(기본값 `weight_decay=0.01`). 수업에서 `lr=0.01`을 준 것은 Adam 계열의 흔한 시작값 `0.001`보다 10배 큰 쪽인데, 자료가 표준화돼 있고 모델이 작아 공격적으로 가도 되는 상황이다.

### 1-6. 학습 루프 — 5박자가 그대로 코드가 된다

```python
# 5) 에포크(학습수) 단위 학습 (순전파 -> 역전파)
for epoch in range(10000):
    model.train()                     # 5-1 학습 모드
    optimizer.zero_grad()             # 5-2 이전 에포크의 기울기 초기화
    logits = model(X_train)           # 5-3 (순전파) 학습 자료를 넣어 예측
    loss = criterion(logits, Y_train) # 5-4 (손실) 정답과 비교해 손실 계산
    loss.backward()                   # 5-5 (역전파) 각 가중치에 기울기 계산
    optimizer.step()                  # 5-6 (업데이트) 가중치 반영
    if epoch % 100 == 0:
        print(epoch, ": loss: ", loss.item())
```

day21 3-1에 적어 둔 `zero_grad → forward → loss → backward → step` 5박자가 그대로 수업 코드가 되었다. 한 줄씩 day21의 어느 줄에 대응하는지 짚어 두면 전체가 낯설지 않다.

| 수업 줄 | day21의 손 코드 | 뜻 |
| --- | --- | --- |
| `model.train()` | (없음) | 학습 모드 스위치 — 지금 모델엔 영향 없지만 드롭아웃·배치 정규화가 들어오면 동작을 바꿈 (다음 노트) |
| `optimizer.zero_grad()` | `w.grad.zero_()`·`b.grad.zero_()` | **기울기는 누적**되므로 매 바퀴 비움 — 81개 전부 한 줄로 |
| `logits = model(X_train)` | `y_pred = x * w + b` | 순전파 — 5,197행이 세 층을 한 번에 통과 (반복문 없이 행렬 곱) |
| `loss = criterion(logits, Y_train)` | `loss = criterion(y_pred, y)` | `MSELoss` → `BCEWithLogitsLoss`로 바뀐 것뿐 |
| `loss.backward()` | `loss.backward()` | 81개 매개변수의 `.grad`를 채움 |
| `optimizer.step()` | `w -= lr * w.grad` 두 줄 | 갱신을 옵티마이저가 대신 |

`range(10000)`이 **에포크** 수다 — 학습 자료 전체(5,197행)를 한 번 다 보고 가중치를 한 번 고치는 것이 에포크 하나이고, 이 코드는 전체 자료를 한 덩어리로 넣으니 에포크 하나에 갱신도 한 번이다(배치 경사하강법, day21 3-2 표의 첫 줄).

`epoch % 100 == 0`으로 100바퀴마다 손실을 찍은 출력을 읽으면 학습이 어떻게 진행되는지 보인다.

| 에포크 | 손실 | 읽기 |
| --- | --- | --- |
| 0 | 0.6564 | 초기 가중치가 무작위라 거의 "모른다" — 50 : 50 예측의 BCE가 ln 2 ≈ 0.693 |
| 100 | 0.3892 | 100바퀴에 손실 절반 가까이 — 가장 가파른 구간 |
| 500 | 0.3083 | |
| 1,000 | 0.2936 | |
| 2,000 | 0.2884 | 여기부터 네 자리째가 느리게 움직임 |
| 5,000 | 0.2867 | |
| 9,900 | 0.2866 | 5,000 이후 1만까지 **0.0001 미만 변화** — 평평한 바닥 |

0.6564에서 시작해 0.2866까지 내려오는 곡선인데, 눈에 띄는 것은 뒷 절반 5,000바퀴가 거의 하는 일이 없다는 점이다. 0.2866 근처가 이 구조(은닉 16개·특성 3개)가 이 자료에서 도달할 수 있는 바닥이고, 이 뒤로는 에포크를 늘려도 얻는 것이 없다. 중간중간 `0.28668 → 0.28668 → 0.28667`처럼 아주 조금 **오르는** 구간도 보이는데, Adam 계열이 적응형 보폭으로 바닥 주변을 미세하게 흔드는 것이라 걱정할 일은 아니다. 이 손실 바닥이 곧 **학습을 언제 멈출지**를 알려 주는 신호이고(2-2), 수업 주석의 "확인용"이 그 눈 역할이다.

### 1-7. 평가 — `model.eval()`·`no_grad`·시그모이드·임계값 0.5

```python
# 모델평가: model.train() 학습 모드, model.eval() 평가/추론 모드
model.eval()                           # 추론/평가 모드로 전환
with torch.no_grad():                  # 기울기 저장 안 함
    train_pred = (torch.sigmoid(model(X_train)) >= 0.5).float()
    test_pred  = (torch.sigmoid(model(X_test))  >= 0.5).float()

from sklearn.metrics import f1_score
print(f1_score(Y_train.numpy(), train_pred.numpy(), average='macro'))   # 0.8284
print(f1_score(Y_test.numpy(),  test_pred.numpy(),  average='macro'))   # 0.8013
```

사이킷런이라면 `model.predict(X_test)` 한 줄로 끝났을 자리가 네 단계로 풀려 있다. 각 단계가 왜 필요한지가 이 셀의 전부다.

| 단계 | 코드 | 왜 |
| --- | --- | --- |
| ① 모드 전환 | `model.eval()` | 학습 중에만 켜져야 할 층(드롭아웃 등)을 끈다 — `train()`과 짝, 쓰지 않으면 추론 결과가 매번 달라질 수 있다 |
| ② 그래프 끄기 | `with torch.no_grad():` | 추론엔 `backward()`가 없으니 계산 그래프를 만들 필요가 없다 — 메모리·속도 절약 (day21 1-3의 그 블록) |
| ③ 로짓 → 확률 | `torch.sigmoid(model(X))` | 모델은 로짓을 내놓으므로(1-4) 사람이 읽을 확률로 바꿔야 한다 |
| ④ 확률 → 라벨 | `(… >= 0.5).float()` | 0.5 기준으로 `True`/`False` → `1.0`/`0.0` — day14 `predict`가 안에서 하던 일 |

③·④를 합치면 `model(X) >= 0`이라고 써도 결과가 같다 — 시그모이드는 0에서 0.5를 지나는 단조 함수라 "확률 ≥ 0.5"와 "로짓 ≥ 0"이 같은 조건이다. 수업처럼 확률을 거쳐 가는 쪽이 읽기엔 분명하다.

점수는 **사이킷런 `f1_score`로 잰다** — 파이토치는 모델·손실·옵티마이저까지만 제공하고, 평가지표는 늘 쓰던 사이킷런을 그대로 쓴다. `Y_train.numpy()`·`train_pred.numpy()`로 텐서를 넘파이로 돌려 넘기는 것이 그 다리이고(day21 2-2 텐서↔넘파이 표), `(5197, 1)` 모양도 `f1_score`가 알아서 1차원으로 펴서 받는다.

| 세트 | macro F1 | 비교(같은 자료·같은 분할의 다른 모델) |
| --- | --- | --- |
| 학습 | **0.8284** | |
| 테스트 | **0.8013** | day17 XGBoost·LightGBM 100그루 0.80 수준 · day18 LightGBM 조기 종료 0.819 |

학습 0.83·테스트 0.80으로 격차가 3점 안팎이라 과대적합은 아니고, day17 로지스틱 회귀(정확도 0.78)는 넘고 부스팅과 비슷한 자리다. 특성 세 개짜리 작은 문제에서는 은닉 16개 신경망이 부스팅 트리를 크게 앞서지 못한다는 것도 솔직한 결과다 — 신경망의 진짜 힘은 특성이 수백·수천 개(이미지·문장)로 커질 때 나온다.

### 1-8. 흐름 한 장 — 사이킷런 모델 자리에 신경망 끼우기

```
판다스 read_csv → 특성/타깃 → train_test_split(stratify) → StandardScaler     ← day12~17 그대로
        ↓
torch.tensor(float32)  /  Y.unsqueeze(1)  → (N, 3) · (N, 1)                      ← 1-2
        ↓
model = nn.Sequential(Linear(3,16) → ReLU → Linear(16,1))                        ← 1-3  (w·b 81개)
criterion = nn.BCEWithLogitsLoss()      optimizer = optim.AdamW(params, lr)      ← 1-4·1-5
        ↓
for epoch:  train() → zero_grad() → model(X) → criterion → backward() → step()   ← 1-6  (× 10,000)
        ↓
eval() → no_grad → sigmoid → ≥ 0.5 → f1_score(numpy)                             ← 1-7
```

위 두 줄은 사이킷런, 가운데 네 줄이 파이토치, 마지막 줄의 점수는 다시 사이킷런이다. **딥러닝은 전처리·평가를 새로 배우는 일이 아니라 "모델 블록"만 바꿔 끼우는 일**이라는 것이 이 그림의 요지다.

## 2. 추가로 알면 좋은 활용법

### 2-1. 손실 곡선 그리기와 학습·검증 손실 나란히

`print`로 100바퀴마다 찍는 대신 리스트에 모아 그리면 1-6 표가 한눈에 보인다. day21 2-1에서 적어 둔 대로 `loss.item()`으로 **숫자만** 모아야 한다(텐서를 그대로 모으면 계산 그래프가 붙잡혀 메모리가 샌다).

```python
train_losses, test_losses = [], []
for epoch in range(10000):
    model.train()
    optimizer.zero_grad()
    loss = criterion(model(X_train), Y_train)
    loss.backward()
    optimizer.step()
    if epoch % 100 == 0:
        model.eval()
        with torch.no_grad():
            test_loss = criterion(model(X_test), Y_test)
        train_losses.append(loss.item())
        test_losses.append(test_loss.item())

import matplotlib.pyplot as plt
plt.plot(train_losses, label='train')
plt.plot(test_losses,  label='test')
plt.xlabel('epoch (×100)'); plt.ylabel('BCE loss'); plt.legend()
```

두 곡선이 같이 내려가다 테스트 쪽만 다시 올라가기 시작하는 지점이 **과대적합이 시작되는 에포크**다. 1-6의 와인 자료에선 둘이 거의 붙어 평평해지는데, 다음 노트의 드롭아웃이나 더 큰 모델을 쓸 때 이 그림이 판단 근거가 된다. 평가 손실을 잴 때도 `eval()`·`no_grad`를 두르는 것을 잊지 않는다.

### 2-2. 에포크 수를 미리 정하지 않기 — 조기 종료 직접 쓰기

1만 바퀴 중 5천 바퀴가 놀았다. day18 LightGBM의 `early_stopping(50)`을 파이토치에선 직접 쓴다 — 검증 손실이 `patience`번 연속 나아지지 않으면 멈추고, **가장 좋았을 때의 가중치**를 복원한다.

```python
import copy
best_loss, best_state, patience, wait = float('inf'), None, 200, 0
for epoch in range(10000):
    # … 학습 5박자 …
    model.eval()
    with torch.no_grad():
        val_loss = criterion(model(X_test), Y_test).item()
    if val_loss < best_loss - 1e-5:
        best_loss, wait = val_loss, 0
        best_state = copy.deepcopy(model.state_dict())   # 가중치 81개 스냅숏
    else:
        wait += 1
        if wait >= patience:
            print('early stop at', epoch); break
model.load_state_dict(best_state)
```

`model.state_dict()`는 층 이름 → 가중치 텐서 딕셔너리(`'0.weight'`·`'0.bias'`·`'2.weight'`·`'2.bias'` — `nn.Sequential`은 층을 **순번**으로 이름 붙인다)이고, 이것이 `torch.save(model.state_dict(), 'wine_ann.pt')`로 저장하는 단위이기도 하다. 엄밀히는 테스트 세트로 멈출 때를 정하면 테스트가 더는 "처음 보는 자료"가 아니니, 학습 세트에서 검증 세트를 한 번 더 떼어 쓰는 것이 바르다(day18 2-1과 같은 이야기).

### 2-3. 미니배치 — `DataLoader`로 자료를 쪼개 넣기

5,197행을 한 번에 넣는 배치 경사하강법은 자료가 수십만 행이 되면 메모리에 안 들어간다. `TensorDataset`과 `DataLoader`로 쪼개면 에포크 하나에 갱신이 여러 번 일어나고(day21 3-2 미니배치), 섞어 넣는 효과로 바닥에서 빠져나오기도 한다.

```python
from torch.utils.data import TensorDataset, DataLoader
train_ds = TensorDataset(X_train, Y_train)
train_dl = DataLoader(train_ds, batch_size=256, shuffle=True)   # 5197 / 256 ≈ 21번 갱신/에포크

for epoch in range(200):                 # 에포크당 갱신이 21번이라 바퀴 수는 훨씬 적어도 된다
    model.train()
    for xb, yb in train_dl:              # 배치 하나씩 (256, 3)·(256, 1)
        optimizer.zero_grad()
        loss = criterion(model(xb), yb)
        loss.backward()
        optimizer.step()
```

`shuffle=True`는 에포크마다 행 순서를 섞는다 — 자료가 종류별로 정렬돼 있어도 배치마다 섞인 표본이 들어간다(day14의 `KFold(shuffle=True)`와 같은 이유). 배치 크기는 32·64·128·256처럼 2의 거듭제곱을 쓰는 관례가 있고, 작을수록 갱신이 잦고 요동이 크며 클수록 안정적이지만 한 에포크당 갱신 횟수가 줄어든다.

### 2-4. 확률 읽기와 임계값 바꾸기

1-7의 `>= 0.5`는 day14 2-4에서 본 것처럼 **움직일 수 있는 선**이다. 레드 와인(0, 소수 클래스 25 %)을 놓치지 않는 것이 중요하다면 화이트로 판정하는 기준을 올린다.

```python
model.eval()
with torch.no_grad():
    proba = torch.sigmoid(model(X_test)).squeeze(1).numpy()   # (1300,) 화이트일 확률

from sklearn.metrics import classification_report
for thr in [0.5, 0.6, 0.7]:
    pred = (proba >= thr).astype(int)
    print(thr, f1_score(Y_test.numpy(), pred, average='macro'))
print(classification_report(Y_test.numpy(), (proba >= 0.5).astype(int), target_names=['red', 'white']))
```

`squeeze(1)`은 1-2에서 붙인 열 축을 다시 떼어 `(1300,)`로 돌리는 것으로, `unsqueeze`의 반대다. `classification_report`로 보면 macro F1 0.80이 레드·화이트 어느 쪽에서 깎였는지가 보인다 — day17 랜덤 포레스트에서 `class_weight`로 레드 재현율을 끌어올렸던 것처럼, 여기서는 `BCEWithLogitsLoss(pos_weight=torch.tensor([…]))`로 양성(화이트) 손실의 가중치를 조절하거나 임계값을 옮기는 두 길이 있다.

### 2-5. 사이킷런 ↔ 파이토치 대응표

| 하는 일 | 사이킷런(day14 로지스틱) | 파이토치(오늘) |
| --- | --- | --- |
| 모델 만들기 | `LogisticRegression()` | `nn.Sequential(Linear, ReLU, Linear)` |
| 손실 정하기 | 안에 고정(로그 손실) | `nn.BCEWithLogitsLoss()` — 내가 고른다 |
| 최적화 방법 | 안에 고정(`lbfgs`) | `optim.AdamW(model.parameters(), lr)` — 내가 고른다 |
| 학습 | `fit(X, Y)` 한 줄 | `for epoch:` 5박자 — 바퀴 수·멈출 때도 내가 정한다 |
| 확률 | `predict_proba(X)[:, 1]` | `torch.sigmoid(model(X))` |
| 라벨 | `predict(X)` | `(sigmoid(…) >= 0.5).float()` |
| 평가 | `score`·`f1_score` | `f1_score`(넘파이로 돌려서) — **같다** |
| 저장 | `joblib.dump(model)` | `torch.save(model.state_dict(), '….pt')` |
| 규제 | `C`(= 1/alpha) | `AdamW(weight_decay=)`·드롭아웃(다음 노트) |

오른쪽 열이 길어진 만큼 **고를 것이 많아졌다**는 것이 핵심이다. 사이킷런이 묶어 두었던 결정(손실·최적화·반복·멈춤)이 전부 내 손에 들어왔고, 그만큼 잘못 고르면 학습이 안 되기도 한다 — day21 2-2의 학습률 표가 그 첫 예다.

## 3. 더 나아가 알면 좋은 것

### 3-1. `nn.Module`을 상속해 모델 클래스로 쓰기

`nn.Sequential`은 입력이 한 줄로 흘러가는 구조에만 맞다. 두 갈래로 나뉘거나, 건너뛰는 연결(ResNet의 skip connection)이 있거나, 중간 값을 꺼내 봐야 하면 `nn.Module`을 상속해 `forward`를 직접 쓴다 — day05에서 배운 클래스 상속이 여기서 쓰인다.

```python
class WineNet(nn.Module):
    def __init__(self, in_features=3, hidden=16):
        super().__init__()
        self.fc1 = nn.Linear(in_features, hidden)
        self.act = nn.ReLU()
        self.fc2 = nn.Linear(hidden, 1)
    def forward(self, x):
        return self.fc2(self.act(self.fc1(x)))

model = WineNet()
```

`model(X)`가 `forward`를 부르는 것은 `nn.Module`의 `__call__`이 그렇게 돼 있기 때문이고(day05 특수 메소드), `model.parameters()`·`state_dict()`·`train()`/`eval()`은 상속으로 그대로 따라온다. 실무 코드와 논문 구현은 거의 이 꼴이고, `nn.Sequential`은 그 안에서 블록 하나를 묶는 데 자주 쓰인다.

### 3-2. 다중 분류로 넘어가면 — `CrossEntropyLoss`와 정수 라벨

출력층을 `nn.Linear(16, 7)`로, 손실을 `nn.CrossEntropyLoss()`로 바꾸면 day15의 일곱 종 물고기 분류가 된다. 이때 정답은 `(N, 1)` 실수가 아니라 **`(N,)` 모양의 `torch.long` 정수 라벨**(0~6)이어야 하고, `unsqueeze(1)`도 하지 않는다 — 이진과 다중에서 타깃의 모양·타입 규칙이 다르다는 것이 처음 가장 많이 걸리는 자리다. 추론은 `torch.softmax(logits, dim=1).argmax(dim=1)`로 가장 큰 확률의 열 번호를 고르면 day15 `predict`와 같다.

| 문제 | 출력층 | 손실 | 타깃 모양·타입 | 추론 |
| --- | --- | --- | --- | --- |
| 회귀 | `Linear(h, 1)` | `MSELoss` | `(N, 1)` float | 그대로 |
| 이진 분류(오늘) | `Linear(h, 1)` | `BCEWithLogitsLoss` | `(N, 1)` float 0/1 | `sigmoid ≥ 0.5` |
| 다중 분류 | `Linear(h, K)` | `CrossEntropyLoss` | `(N,)` long 0~K−1 | `softmax → argmax` |

### 3-3. 가중치 초기화·재현성·GPU

`nn.Linear`의 가중치는 만들 때 무작위로 정해진다(Kaiming 균등 분포). 그래서 1-6의 첫 손실 0.6564는 다시 실행하면 다른 값이 되고, 최종 F1도 소수 둘째 자리에서 흔들릴 수 있다 — 사이킷런의 `random_state=42`에 해당하는 것이 `torch.manual_seed(42)`이고 모델을 만들기 **전에** 불러야 한다. 완전한 재현을 위해선 `numpy`·`random` 씨앗과 `torch.backends.cudnn.deterministic` 설정까지 맞춘다.

오늘 코드는 CPU에서 돌았다(5,197 × 3 자료라 1만 에포크도 몇 초). day21의 `device` 관용구를 붙이면 코랩 T4에서 그대로 돈다 — `model.to(device)`와 `X_train.to(device)`·`Y_train.to(device)`를 **같은 장치**로 보내는 것만 지키면 된다. 평가에서 `f1_score`에 넘기기 전엔 `.cpu().numpy()`로 돌려야 한다.

### 3-4. 다음에 볼 키워드

- `nn.Dropout`·`nn.BatchNorm1d` — `train()`/`eval()` 스위치가 실제로 동작을 바꾸는 첫 층 (다음 노트)
- `torch.optim.lr_scheduler` — `StepLR`·`CosineAnnealingLR`·`ReduceLROnPlateau`로 학습률을 바꿔 가며 바닥에 더 가까이
- `Dataset`·`DataLoader`·`random_split` — 미니배치와 검증 세트 분리
- `torch.save`/`torch.load`·`state_dict`·체크포인트 — `joblib` 자리
- `torchmetrics`·`BCEWithLogitsLoss(pos_weight=)` — 파이토치 안에서 지표 재기·불균형 가중
- `nn.Embedding`·`nn.Conv1d`/`Conv2d`·`nn.LSTM`/`Transformer` — 표 자료를 넘어 문장·이미지로
- 케라스 `Sequential → compile(loss, optimizer) → fit(epochs)` — 같은 그림의 다른 문법
- `skorch` — 파이토치 모델을 사이킷런 `fit`/`predict`·`GridSearchCV`에 끼우는 어댑터
- 기울기 소실·He 초기화·잔차 연결 — 층을 깊게 쌓을 때 생기는 문제들

## 실습 파일

- `KDT_2026/2026_Python/day22/dl-2.ipynb` — 앞 세 셀: ① `read_csv(url)` 혼공머신 `wine.csv` → `X = df[['alcohol', 'sugar', 'pH']]`·`Y = df['class']`(0 레드 · 1 화이트) → `train_test_split(test_size=0.2, random_state=42, stratify=Y)` → `StandardScaler` `fit_transform`/`transform` ② 1) `X_train.shape (5197, 3)`·`Y_train.shape (5197,)` → `torch.tensor(…, dtype=torch.float32)` 넷·타깃 `.values` + `.unsqueeze(1)` → `torch.Size([5197, 3])`·`torch.Size([5197, 1])` / 2) `nn.Sequential(nn.Linear(3, 16), nn.ReLU(), nn.Linear(16, 1))` / 3) `nn.BCEWithLogitsLoss()` / 4) `optim.AdamW(model.parameters(), lr=0.01)` / 5) `for epoch in range(10000)`: `model.train()` → `optimizer.zero_grad()` → `logits = model(X_train)` → `loss = criterion(logits, Y_train)` → `loss.backward()` → `optimizer.step()` → `epoch % 100 == 0`마다 `loss.item()` 출력(0 : 0.6564 → 100 : 0.3892 → 1000 : 0.2936 → 5000 : 0.2867 → 9900 : 0.2866) ③ `model.eval()` → `with torch.no_grad():` `(torch.sigmoid(model(X_train)) >= 0.5).float()`·테스트 동일 → `f1_score(Y_train.numpy(), train_pred.numpy(), average='macro')` **0.8284** · 테스트 **0.8013**

## 관련 노트

[[AI 정리본 인덱스]] · [[AI day21 Hugging Face datasets로 LBox 판결문 데이터셋 불러오기]] · [[AI day21 MSELoss 손실·backward 역전파와 경사하강법 한 걸음 갱신]] · [[AI day22 nn.Dropout 과적합 방지와 성적 회귀 신경망 뼈대]] · [[AI day17 결정 트리로 와인 레드·화이트 분류와 plot_tree]] · [[KDT_2026 학습 지도]]
