---
출처: Claude 분석
원본: KDT_2026/2026_Python/day21/dl-1.ipynb(3~8셀 파이토치 부분)
작성일: 2026-11-20
tags: [학습, ai, python]
---

# AI day21 — 파이토치 텐서 생성·차원 재구성과 시그모이드·ReLU

> 실습 파일: `day21/dl-1.ipynb` (`## Example` 뒤의 파이토치 셀 다섯 개)
> 허브: [[AI 정리본 인덱스]] · 이전: [[AI day21 구글 코랩 시작과 드라이브 마운트·런타임]] · 다음: (아직 없음)

앞 노트에서 `dl-1.ipynb`는 코랩 셀 두 개였는데, 같은 파일에 `## Example`이라는 마크다운 셀 뒤로 **파이토치(PyTorch) 셀 다섯 개**가 이어 붙었다. day12부터 사이킷런은 `모델().fit(X, y)` 한 줄 안에 학습이 숨어 있었다. 파이토치는 그 한 줄의 안쪽을 직접 만진다 — 숫자를 담는 그릇(**텐서**), 그릇의 모양 바꾸기(`reshape`·`unsqueeze`), 출력을 확률이나 양수로 바꾸는 **활성화 함수**(`sigmoid`·`relu`), 그리고 "이 변수는 미분을 기록하라"는 표시(`requires_grad=True`)를 단 가중치·편향으로 `y_pred = x * w + b`를 계산하는 데까지. 수업은 딱 그 예측값 하나를 찍고 멈춘다. 멈춘 자리가 다음 수업의 출발점(손실 → 역전파 → 갱신)이라서, 2절에서 그 한 걸음을 손으로 이어 계산해 두었다.

## 1. 배운 내용

### 1-1. `import torch` — 버전·GPU 확인·`device` 한 줄

```python
import torch                           # 파이토치 라이브러리
print(torch.__version__)               # 2.14.1+cpu
print(torch.cuda.is_available())       # False
device = 'cuda' if torch.cuda.is_available() else 'cpu'
print(device)                          # cpu
```

| 출력 | 뜻 |
| --- | --- |
| `2.14.1+cpu` | 설치된 파이토치 버전. `+` 뒤가 빌드 종류 — `+cpu`는 CUDA 없는 CPU 전용 빌드, GPU 빌드는 `+cu126`처럼 CUDA 버전이 붙는다 |
| `False` | `torch.cuda.is_available()` — 지금 이 파이썬이 쓸 수 있는 NVIDIA GPU(CUDA)가 없다 |
| `cpu` | 조건식이 고른 장치 이름. GPU가 있으면 `'cuda'` |

세 줄 중 셋째 줄이 파이토치 코드마다 맨 위에 두는 관용구다. **코드는 하나로 쓰고, 장치는 실행 환경이 정한다** — 이 뒤로 만드는 텐서와 모델에 `.to(device)`를 붙이면, GPU가 있는 코랩 T4 런타임에서는 GPU 메모리에, 없는 내 PC에서는 CPU에 올라간다. 출력이 전부 CPU 쪽이라는 것은 이 셀들이 CUDA 없는 빌드에서 돌았다는 뜻이고(노트북 메타데이터도 로컬 `Python 3 (ipykernel)`), 같은 셀을 코랩에서 T4 GPU 런타임으로 돌리면 `2.x+cu12x` · `True` · `cuda`로 바뀐다. 앞 노트 3-2에서 "`fit` 전에 GPU를 쓰는지 확인하는 한 줄"이라고 적어 둔 것이 바로 이 줄이다.

### 1-2. 텐서 — 넘파이 배열을 `torch.tensor`로

```python
import numpy as np
np_data = np.array([[10.0, 20.0, 30.0], [40.0, 50.0, 60.0]])
x = torch.tensor(np_data, dtype=torch.float32)   # X = torch.tensor(넘파이배열, dtype=torch.타입명)
print(x.shape, x.dtype)                           # torch.Size([2, 3]) torch.float32
```

파이토치의 모든 데이터는 **텐서(tensor)** 객체다. day06 넘파이 `ndarray`와 거의 같은 물건 — 다차원 숫자 배열이고 `shape`·`dtype`이 있고 인덱싱·슬라이싱·브로드캐스팅이 같은 규칙으로 된다 — 인데, 두 가지가 더 있다. **GPU 메모리에 올라갈 수 있고**, **연산 과정을 기록해 미분할 수 있다**(1-5).

| | 넘파이 `ndarray` | 파이토치 `tensor` |
| --- | --- | --- |
| 모양 | `(2, 3)` 튜플 | `torch.Size([2, 3])` — 튜플처럼 쓰면 된다(`x.shape[0]` = 2) |
| 실수 기본 타입 | `float64` | 딥러닝 관례는 **`float32`** — 그래서 `dtype=torch.float32`를 명시 |
| 있는 곳 | CPU 메모리만 | CPU 또는 GPU(`.to('cuda')`) |
| 미분 기록 | 없음 | `requires_grad=True`면 연산을 기록 |
| 만드는 법 | `np.array(리스트)` | `torch.tensor(리스트 또는 배열, dtype=)` |

`float32`를 굳이 적는 이유는 세 가지다. 넘파이에서 넘어온 실수는 `float64`인데, 신경망 층(`nn.Linear` 등)의 가중치는 기본이 `float32`라 타입이 다르면 곱셈에서 오류가 난다. 메모리가 절반이라 GPU에 더 큰 배치를 올릴 수 있다. 그리고 GPU는 32비트 연산이 64비트보다 훨씬 빠르다. 소수 일곱 자리 정도의 정밀도로 충분한 자리라서 손해는 거의 없다.

### 1-3. 차원 재구성 — `reshape`와 `unsqueeze`

```python
print(x.reshape(3, 2).shape)     # torch.Size([3, 2])  차원 변경
print(x.unsqueeze(0).shape)      # torch.Size([1, 2, 3])  X.unsqueeze(차원위치)
print(x.unsqueeze(-1).shape)     # torch.Size([2, 3, 1])  차원 추가

x2 = x.reshape(3, 2)
x3 = x.unsqueeze(1)              # torch.Size([2, 1, 3])
```

출력을 모양과 함께 나란히 두면 두 함수의 차이가 보인다.

| 호출 | 결과 모양 | 하는 일 | 출력 |
| --- | --- | --- | --- |
| `x` | `[2, 3]` | 원본 | `[[10, 20, 30], [40, 50, 60]]` |
| `x.reshape(3, 2)` | `[3, 2]` | 원소 6개를 **순서대로 다시 채워** 3행 2열로 | `[[10, 20], [30, 40], [50, 60]]` |
| `x.unsqueeze(0)` | `[1, 2, 3]` | 맨 앞(0번)에 길이 1인 축 추가 | 원본을 한 겹 더 감쌈 |
| `x.unsqueeze(1)` | `[2, 1, 3]` | 가운데(1번)에 길이 1인 축 추가 | `[[[10, 20, 30]], [[40, 50, 60]]]` — 행 하나짜리 행렬 두 장 |
| `x.unsqueeze(-1)` | `[2, 3, 1]` | 맨 뒤(−1번)에 길이 1인 축 추가 | 원소 하나하나가 길이 1 벡터 |

`reshape`는 **원소 개수가 같은 다른 모양**으로 바꾼다(6 = 3 × 2). `unsqueeze`는 원소를 하나도 건드리지 않고 **길이 1인 축을 끼워 넣어 차원 수만 하나 올린다** — 넘파이의 `np.newaxis`·`expand_dims`와 같다. 반대로 길이 1인 축을 빼는 것이 `squeeze`다.

이게 왜 첫 시간에 나오느냐 하면, 파이토치 모델은 입력을 거의 항상 **(배치, 특성)** 2차원 이상으로 기대하기 때문이다. 표본 하나짜리 벡터 `[3]`을 넣으려면 `unsqueeze(0)`으로 `[1, 3]`을 만들어야 한다 — day12에서 `predict([[30]])`에 대괄호를 두 겹 쓴 것과 정확히 같은 이유다. 이미지는 (배치, 채널, 높이, 너비) 4차원, 문장은 (배치, 길이, 임베딩) 3차원으로 다루니, 모양을 읽고 맞추는 일이 딥러닝 코드의 절반이다. 모양이 안 맞아 나는 오류 메시지(`shape mismatch`, `expected 2D`)를 만나면 `.shape`부터 찍어 보는 습관이 안전하다.

### 1-4. 활성화 함수 — `torch.sigmoid`와 `torch.relu`

```python
sample = torch.tensor([-2.0, 0.0, 3.0])
print(torch.sigmoid(sample))   # tensor([0.1192, 0.5000, 0.9526])  0~1 사이 확률값으로
print(torch.relu(sample))      # tensor([0., 0., 3.])              음수는 0으로, 양수만
```

둘 다 **원소별(element-wise)** 로 적용된다 — 입력 세 개가 각각 따로 바뀌어 모양이 그대로 `[3]`이다.

| 함수 | 식 | 출력 범위 | −2 | 0 | 3 | 쓰는 자리 |
| --- | --- | --- | --- | --- | --- | --- |
| 시그모이드 `sigmoid` | σ(z) = 1 / (1 + e^(−z)) | (0, 1) | 0.1192 | 0.5 | 0.9526 | 이진 분류의 **출력층** — 값을 확률로 |
| ReLU `relu` | max(0, z) | [0, ∞) | 0 | 0 | 3 | **은닉층** 기본 — 음수를 끊고 양수는 그대로 |

시그모이드는 day14 로지스틱 회귀에서 선형식 z를 0~1 확률로 바꾸던 바로 그 함수다. 0에서 0.5, 음수로 갈수록 0에, 양수로 갈수록 1에 붙는다. ReLU(Rectified Linear Unit)는 식이 `max(0, z)` 하나라 계산이 싸고, 양수 구간에서 기울기가 1이라 층을 깊게 쌓아도 기울기가 잘 살아남아서 은닉층의 기본값이 되었다.

왜 활성화 함수가 있어야 하는가 — 선형식 `wx + b`를 아무리 여러 층 쌓아도 합치면 다시 선형식 하나다(직선의 직선은 직선). 사이에 시그모이드나 ReLU 같은 **비선형 함수**를 끼워야 층을 쌓는 의미가 생기고, 곡선·경계가 구부러진 문제를 풀 수 있다. day13에서 직선 모델에 제곱항을 손으로 넣어 곡선을 만들었다면, 신경망은 활성화 함수가 그 구부림을 데이터에서 배운다.

### 1-5. `requires_grad=True` — 가중치·편향과 `y_pred = x * w + b`

```python
x = torch.tensor(2.0)                      # 특성값
y = torch.tensor(1.0)                      # 타깃값
w = torch.tensor(0.2, requires_grad=True)  # 가중치 — requires_grad=True 속성은 역전파 기록용
b = torch.tensor(0.0, requires_grad=True)  # 편향
learning_rate = 0.1
y_pred = x * w + b                         # y_pred = wx + b
print(y_pred)                              # tensor(0.4000, grad_fn=<AddBackward0>)
```

| 변수 | 값 | 역할 | `requires_grad` |
| --- | --- | --- | --- |
| `x` | 2.0 | 입력 특성(주어진 값) | 없음 — 상수 |
| `y` | 1.0 | 정답 타깃(주어진 값) | 없음 — 상수 |
| `w` | 0.2 | 가중치 — **학습으로 고칠 값** | `True` |
| `b` | 0.0 | 편향 — **학습으로 고칠 값** | `True` |
| `learning_rate` | 0.1 | 한 번에 얼마나 고칠지(학습률) | 파이썬 실수 |

모양 없는 `torch.tensor(2.0)`은 0차원 텐서(스칼라)다. 표본 하나·특성 하나로 가장 작은 선형 모델을 만든 셈이고, day12 `LinearRegression`이 `coef_`·`intercept_`로 돌려주던 기울기와 절편이 여기서는 **내가 직접 선언한 `w`·`b` 두 변수**로 손에 잡힌다. 차이는 푸는 방식이다 — 사이킷런은 최소제곱법으로 한 번에 답을 구하고, 파이토치는 아무 값(0.2, 0.0)에서 출발해 **경사 하강으로 조금씩 고쳐 간다**. 그 "조금씩"의 보폭이 `learning_rate`다.

출력 `tensor(0.4000, grad_fn=<AddBackward0>)`에서 봐야 할 것은 뒤쪽이다. 값 0.4(= 2 × 0.2 + 0)는 당연하고, **`grad_fn=<AddBackward0>`** 는 "이 텐서는 덧셈 연산의 결과로 만들어졌고, 그 경로를 기억하고 있다"는 표시다. `requires_grad=True`인 텐서가 계산에 하나라도 끼면 결과 텐서도 자동으로 추적되며, 곱셈(`MulBackward0`) → 덧셈(`AddBackward0`)으로 이어진 **계산 그래프**가 뒤에 깔린다. 나중에 `loss.backward()`를 부르면 이 그래프를 거꾸로 타고 내려가 `w.grad`·`b.grad`에 기울기가 채워진다 — 이게 **역전파(backpropagation)** 이고, 주석의 "역전파 기록용"이 그 뜻이다. `x`·`y`에 `requires_grad`를 안 단 이유도 같다. 데이터는 고칠 대상이 아니라 기울기가 필요 없다.

### 1-6. 흐름 한 장 — 다섯 셀이 놓인 순서

```
torch 버전·cuda 확인 → device = 'cuda' or 'cpu'              (1-1)
  → 데이터: numpy 배열 → torch.tensor(dtype=float32)         (1-2)
  → 모양 맞추기: reshape(3, 2) / unsqueeze(0, 1, -1)          (1-3)
  → 비선형: sigmoid → 확률(0~1) / relu → 음수 차단            (1-4)
  → 모델: w, b (requires_grad=True) → y_pred = x*w + b         (1-5, 수업은 여기까지)
  → [다음] 손실 → loss.backward() → w -= lr * w.grad → 반복    (2-1에서 한 걸음만 미리)
```

## 2. 추가로 알면 좋은 활용법

### 2-1. 멈춘 자리에서 한 걸음 — 손실·`backward()`·갱신을 손으로 따라가기

수업 셀은 `y_pred`를 찍고 끝났다. 다음에 올 세 줄을 미리 적고, 값을 손으로 확인해 둔다.

```python
loss = (y_pred - y) ** 2          # 평균제곱오차(표본 1개) → tensor(0.3600, grad_fn=<PowBackward0>)
loss.backward()                   # 계산 그래프를 거꾸로 타고 w.grad, b.grad 채우기
print(w.grad, b.grad)             # tensor(-2.4000) tensor(-1.2000)

with torch.no_grad():             # 갱신 자체는 기록하지 않는다
    w -= learning_rate * w.grad   # 0.2 - 0.1 × (-2.4) = 0.44
    b -= learning_rate * b.grad   # 0.0 - 0.1 × (-1.2) = 0.12
    w.grad.zero_(); b.grad.zero_()   # 기울기는 누적되므로 매번 0으로
```

손계산으로 맞춰 보면 — 손실 L = (y_pred − y)² = (0.4 − 1)² = 0.36. 연쇄 법칙으로 ∂L/∂w = 2(y_pred − y) · x = 2 × (−0.6) × 2 = **−2.4**, ∂L/∂b = 2(y_pred − y) = **−1.2**. 기울기가 음수라는 것은 "w를 키우면 손실이 준다"는 뜻이라 `w -= lr × grad`로 빼면 w가 커진다(0.2 → 0.44). 갱신 뒤 다시 예측하면 2 × 0.44 + 0.12 = **1.0**, 정답에 딱 닿는다 — 표본 하나·학습률 0.1이라 한 걸음에 맞은 특수한 경우고, 보통은 이 세 줄을 에포크(epoch)만큼 반복한다.

세 가지 관용구가 여기서 생긴다. `torch.no_grad()` 안에서 갱신하는 이유는 "w를 고치는 연산"까지 그래프에 기록되면 다음 역전파가 꼬이기 때문이고, `.zero_()`를 부르는 이유는 `backward()`가 기울기를 **덮어쓰지 않고 더하기** 때문이며(미니배치를 쪼개 모을 때 쓰는 성질), 끝에 `_`가 붙은 메소드(`zero_`·`add_`)는 새 텐서를 만들지 않고 **제자리에서 바꾸는** in-place 연산이라는 파이토치 이름 규칙이다.

### 2-2. 텐서 ↔ 넘파이 ↔ 판다스 ↔ 파이썬 숫자

| 방향 | 코드 | 주의 |
| --- | --- | --- |
| 넘파이 → 텐서(복사) | `torch.tensor(arr, dtype=torch.float32)` | 수업 방식. 타입을 지정할 수 있다 |
| 넘파이 → 텐서(공유) | `torch.from_numpy(arr)` | 메모리를 공유해 한쪽을 바꾸면 다른 쪽도 바뀜, `float64` 유지 → `.float()`로 변환 |
| 판다스 → 텐서 | `torch.tensor(df.values, dtype=torch.float32)` | day08~20의 DataFrame을 넣는 길. 문자열 열은 먼저 인코딩 |
| 텐서 → 넘파이 | `x.numpy()` | CPU 텐서만. GPU면 `x.cpu().numpy()`, 추적 중이면 `x.detach().numpy()` |
| 텐서 → 파이썬 숫자 | `y_pred.item()` | 원소 하나짜리 텐서에서 `0.4` 같은 숫자를 꺼낼 때(출력·로그용) |
| 텐서 → 리스트 | `x.tolist()` | |
| 장치 이동 | `x.to(device)` · `x.cpu()` · `x.cuda()` | 연산하는 텐서끼리 같은 장치에 있어야 한다 |

### 2-3. 자주 쓰는 생성 함수와 `-1`·`view`

```python
torch.manual_seed(42)                 # 난수 고정 — 사이킷런의 random_state 자리
torch.zeros(2, 3); torch.ones(2, 3)   # 0·1로 채운 텐서
torch.rand(2, 3); torch.randn(2, 3)   # 균등분포 0~1 / 표준정규분포 — 가중치 초기화
torch.arange(0, 10, 2)                # 0, 2, 4, 6, 8
torch.linspace(0, 1, 5)               # 0, 0.25, 0.5, 0.75, 1
x.reshape(-1, 1)                      # -1 = 나머지에서 자동 계산 → [6, 1]
x.view(3, 2)                          # reshape와 같지만 메모리가 연속일 때만(복사 없음)
x.T / x.transpose(0, 1) / x.permute(2, 0, 1) / x.flatten()
```

`reshape(-1, 1)`은 day12에서 넘파이 배열을 특성 2차원으로 세우던 그 표현이다. `view`는 옛 코드에 많고, 안전한 쪽은 `reshape`(연속이 아니면 알아서 복사)다.

### 2-4. 활성화 함수 모음 — `torch.nn.functional`과 층 형태

```python
import torch.nn.functional as F
F.sigmoid(z); F.relu(z); F.tanh(z); F.leaky_relu(z, 0.01); F.softmax(z, dim=1)

import torch.nn as nn
nn.Sequential(nn.Linear(4, 16), nn.ReLU(), nn.Linear(16, 1), nn.Sigmoid())   # 층으로 끼워 넣을 때
```

| 이름 | 식 | 범위 | 자리 |
| --- | --- | --- | --- |
| Sigmoid | 1 / (1 + e^(−z)) | (0, 1) | 이진 분류 출력층 |
| Tanh | (e^z − e^(−z)) / (e^z + e^(−z)) | (−1, 1) | 0 중심이 필요할 때, RNN 내부 |
| ReLU | max(0, z) | [0, ∞) | 은닉층 기본 |
| Leaky ReLU | z > 0 ? z : 0.01z | (−∞, ∞) | ReLU의 "죽은 뉴런" 보완 |
| Softmax | e^(z_i) / Σ e^(z_j) | 합이 1 | 다중 분류 출력층 — day15 `predict_proba`의 그 확률 |

`torch.sigmoid`처럼 함수로 부르면 값만 바꾸고, `nn.Sigmoid()`처럼 층으로 만들면 `Sequential`에 끼워 넣을 수 있다. 학습할 가중치가 없는 층이라 둘은 결과가 같다.

## 3. 더 나아가 알면 좋은 것

### 3-1. 자동 미분(autograd)과 동적 계산 그래프

1-5의 `grad_fn`은 파이토치 **autograd**의 겉면이다. 순전파에서 `requires_grad` 텐서가 거친 모든 연산을 노드로 기록해 두었다가, `backward()` 한 번에 연쇄 법칙(chain rule)으로 모든 잎 텐서의 기울기를 구한다. 그래프는 **실행할 때마다 새로 그려지는 동적 그래프**라 파이썬 `if`·`for`를 모델 안에 그냥 써도 된다(옛 텐서플로 1.x의 정적 그래프와 갈라지는 지점). `x.requires_grad_()`로 나중에 켤 수 있고, `x.detach()`는 그래프에서 떼어 낸 값만 돌려준다. 중간 노드의 `.grad`는 기본으로 저장되지 않고(잎 텐서 `w`·`b`만), `backward()`는 그래프를 쓰고 버리므로 두 번 부르려면 `retain_graph=True`가 필요하다.

### 3-2. `nn.Module`·`nn.Linear`·옵티마이저 — 수업 셀이 자라날 모양

1-5의 `w`·`b`와 2-1의 세 줄은 실제 코드에서 이렇게 포장된다.

```python
model = nn.Linear(1, 1)                                   # 안에 weight(1×1)·bias(1) — requires_grad=True
loss_fn = nn.MSELoss()                                    # (y_pred - y)² 의 평균
optimizer = torch.optim.SGD(model.parameters(), lr=0.1)   # w -= lr × grad 를 대신 수행

for epoch in range(100):
    optimizer.zero_grad()                 # grad 0으로
    y_pred = model(x.unsqueeze(0).unsqueeze(1))   # 순전파 — 입력은 (배치 1, 특성 1)
    loss = loss_fn(y_pred, y.view(1, 1))
    loss.backward()                       # 역전파
    optimizer.step()                      # 갱신
```

| 사이킷런(day12~) | 파이토치 |
| --- | --- |
| `LinearRegression()` | `nn.Linear(in, out)` 또는 `nn.Module` 상속 클래스 |
| `fit(X, y)` 한 줄 | `zero_grad → forward → loss → backward → step` 루프 |
| `coef_`·`intercept_` | `model.weight`·`model.bias` (또는 `model.parameters()`) |
| 알고리즘 내부의 손실 | `nn.MSELoss`·`nn.BCELoss`·`nn.CrossEntropyLoss` 직접 선택 |
| 최소제곱(닫힌 해) | `SGD`·`Adam` 등 옵티마이저로 반복 |
| `predict(X)` | `model.eval()` + `with torch.no_grad(): model(X)` |

### 3-3. 배치 차원·GPU 메모리·정밀도

- 배치 차원은 **항상 0번 축** — `unsqueeze(0)`이 자주 나오는 이유. 데이터가 커지면 `TensorDataset`·`DataLoader(batch_size=32, shuffle=True)`가 미니배치를 잘라 준다
- GPU에서는 텐서·모델·손실이 **같은 장치**에 있어야 한다 — `model.to(device)`, `X.to(device)`를 빠뜨리면 `Expected all tensors to be on the same device` 오류. 결과를 넘파이로 보려면 `.cpu()`
- `float32`가 기본, 큰 모델은 `float16`/`bfloat16` 혼합 정밀도(`torch.autocast`)로 메모리와 시간을 아낀다. 정수 라벨은 `torch.long`(`CrossEntropyLoss`가 요구)
- `torch.cuda.memory_allocated()`·`!nvidia-smi`로 GPU 메모리 확인, 배치가 안 올라가면 배치 크기를 줄이는 것이 첫 대응

### 3-4. 다음에 볼 키워드

- `loss.backward()` · `optimizer.step()` · `zero_grad()` — 학습 루프 세 박자
- 손실 함수 — MSE(회귀) · BCE(이진, 시그모이드와 짝) · CrossEntropy(다중, 소프트맥스 포함)
- 옵티마이저 — SGD · 모멘텀 · Adam, 학습률 스케줄러
- 에포크 · 배치 · `DataLoader` · `Dataset`
- 기울기 소실/폭발과 ReLU·배치 정규화·가중치 초기화(He·Xavier)
- `nn.Module` 상속 — `__init__`에 층, `forward`에 계산
- 과대적합 대책 — 드롭아웃 · 조기 종료(day18 `early_stopping`의 딥러닝판) · 가중치 감쇠(day13 릿지의 자리)
- `torch.save(model.state_dict())` / `load_state_dict` — day14 `joblib`의 파이토치판
- 텐서플로/케라스와의 대응 — `Dense` ↔ `nn.Linear`, `compile`+`fit` ↔ 학습 루프

## 실습 파일

- `KDT_2026/2026_Python/day21/dl-1.ipynb` — `## Example` 마크다운 셀 뒤 다섯 셀: ① `import torch` → `__version__` `2.14.1+cpu` · `cuda.is_available()` `False` · `device = 'cuda' if ... else 'cpu'` → `cpu` ② `np.array([[10., 20., 30.], [40., 50., 60.]])` → `torch.tensor(np_data, dtype=torch.float32)` → `torch.Size([2, 3]) torch.float32` ③ `reshape(3, 2)` `[3, 2]` · `unsqueeze(0)` `[1, 2, 3]` · `unsqueeze(-1)` `[2, 3, 1]` · `x2 = reshape(3, 2)`·`x3 = unsqueeze(1)` `[2, 1, 3]` 출력 ④ `torch.tensor([-2., 0., 3.])` → `sigmoid` `[0.1192, 0.5000, 0.9526]` · `relu` `[0., 0., 3.]` ⑤ `x=2.0`·`y=1.0`·`w=0.2(requires_grad)`·`b=0.0(requires_grad)`·`learning_rate=0.1` → `y_pred = x*w + b` → `tensor(0.4000, grad_fn=<AddBackward0>)`

## 관련 노트

[[AI 정리본 인덱스]] · [[AI day21 구글 코랩 시작과 드라이브 마운트·런타임]] · [[AI day12 사이킷런 단순 선형 회귀로 물고기 무게 예측]] · [[AI day14 로지스틱 회귀로 도미·빙어 분류]] · [[KDT_2026 학습 지도]]
