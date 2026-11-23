---
출처: Claude 분석
원본: KDT_2026/2026_Python/day21/dl-1.ipynb(7~8셀 — 손실·역전파·갱신 부분)
작성일: 2026-11-20
tags: [학습, ai, python]
---

# AI day21 — MSELoss 손실·backward 역전파와 경사하강법 한 걸음 갱신

> 실습 파일: `day21/dl-1.ipynb` (`y_pred = x * w + b` 뒤에 이어 붙은 손실·역전파 셀과 갱신 셀)
> 허브: [[AI 정리본 인덱스]] · 이전: [[AI day21 파이토치 텐서 생성·차원 재구성과 시그모이드·ReLU]] · 다음: [[AI day22 nn.Sequential 와인 이진 분류와 BCEWithLogitsLoss·AdamW 학습 루프]]

앞 노트는 `w = 0.2`·`b = 0.0`으로 `y_pred = 0.4`를 찍은 자리에서 끝났고, 그 뒤에 올 세 줄을 2-1에 미리 손으로 적어 두었다. 수업이 그 자리를 그대로 이어받았다 — `nn.MSELoss()`로 **손실**을 구하고, `loss.backward()`로 **기울기**를 채우고, `torch.no_grad()` 블록 안에서 **가중치·편향을 한 번 고친다**. 셀 두 개, 코드 스무 줄이지만 이 안에 딥러닝 학습의 한 바퀴(순전파 → 손실 → 역전파 → 갱신)가 전부 들어 있다. 숫자가 전부 손으로 따라갈 만큼 작아서(표본 하나, 특성 하나) 각 줄이 무엇을 바꾸는지 값으로 확인할 수 있는 날이다.

## 1. 배운 내용

### 1-1. 손실 함수 `nn.MSELoss()` — 예측과 정답의 거리

```python
import torch.nn as nn
criterion = nn.MSELoss()          # 손실 함수 (오차를 구해 주는 함수)
loss = criterion(y_pred, y)       # 손실 구하기
print(loss)                       # tensor(0.3600, grad_fn=<MseLossBackward0>)
```

`y_pred = 0.4`, `y = 1.0`이니 오차는 −0.6이고, 이를 제곱한 **0.36**이 손실이다. `nn.MSELoss`는 평균제곱오차(Mean Squared Error) — 원소마다 `(예측 − 정답)²`을 구해 평균 낸다. 표본이 하나라 평균이 곧 그 값이다. day12 `LinearRegression`의 `score()`가 R²를 돌려주던 것과 달리, 파이토치는 **무엇을 작게 만들 것인지를 내가 고른다**. 그 "작게 만들 숫자"가 손실(loss)이고, `criterion`은 그 함수를 담는 변수 이름 관례다(기준·판정 기준이라는 뜻).

| 줄 | 하는 일 | 값 |
| --- | --- | --- |
| `criterion = nn.MSELoss()` | 손실 함수 객체 만들기 — 층처럼 한 번 만들어 두고 부른다 | |
| `criterion(y_pred, y)` | `(0.4 − 1.0)²` | `0.3600` |
| `grad_fn=<MseLossBackward0>` | 이 손실도 계산 그래프 위에 있다 — `y_pred`가 `requires_grad` 텐서에서 나왔기 때문 | |

출력의 `grad_fn=<MseLossBackward0>`가 중요하다. `w`·`b`에 붙인 `requires_grad=True`가 `y_pred`(`AddBackward0`)를 거쳐 `loss`까지 이어졌다는 뜻이고, 그래서 다음 줄의 `backward()`가 이 손실에서 출발할 수 있다. 손실 하나를 끝점으로 **`w → (x*) → (+b) → y_pred → (MSE) → loss`** 그래프가 완성된 상태다.

그 앞에 `torch.relu(y_pred)`를 한 번 부르는 줄이 있다. 0.4는 양수라 ReLU를 거쳐도 0.4 그대로이고, 결과를 변수에 담지 않았으니 `y_pred`도 그대로 `tensor(0.4000, grad_fn=<AddBackward0>)`다 — 앞 노트 1-4의 활성화 함수를 모델 출력에 적용해 보는 자리로 읽으면 된다. 음수 예측이었다면 0으로 잘렸을 것이고, 결과를 담아 썼다면 `grad_fn`이 `ReluBackward0`로 바뀌어 그래프에 한 노드가 더 생겼을 것이다.

### 1-2. `loss.backward()` — 역전파로 기울기 채우기

```python
loss.backward()                           # 역전파
print(w.grad.item(), b.grad.item())       # -2.4000000953674316 -1.2000000476837158
```

`backward()` 한 줄이 그래프를 거꾸로 타고 내려가 `requires_grad=True`였던 잎 텐서 두 개, `w`와 `b`의 `.grad`에 **손실이 그 변수에 대해 얼마나 민감한지(기울기)** 를 채운다. 호출 전에는 `w.grad`가 `None`이고, 호출 뒤에 숫자가 생긴다. `.item()`은 원소 하나짜리 텐서에서 파이썬 실수를 꺼내는 메소드라 출력이 `tensor(...)`가 아니라 맨 숫자다.

손으로 맞춰 보면 수업 출력과 같다.

| 기울기 | 연쇄 법칙 | 계산 | 값 |
| --- | --- | --- | --- |
| ∂loss/∂w | 2(y_pred − y) · ∂y_pred/∂w = 2(y_pred − y) · x | 2 × (0.4 − 1.0) × 2.0 | **−2.4** |
| ∂loss/∂b | 2(y_pred − y) · ∂y_pred/∂b = 2(y_pred − y) · 1 | 2 × (0.4 − 1.0) × 1 | **−1.2** |

`-2.4000000953674316`처럼 꼬리가 붙는 것은 `float32`가 −2.4를 정확히 표현하지 못해서다. 앞 노트 1-2에서 `float32`를 쓰는 대가가 이 소수 일곱 자리 뒤의 잡음이고, 학습에는 아무 영향이 없다.

**기울기의 부호를 읽는 법** — 수업 주석의 질문 "가중치를 올리면 오차는 줄어드는가? 편향은 내리면 오차는 줄어드는가?"에 답하는 자리다. 기울기는 "그 변수를 아주 조금 **올렸을 때** 손실이 어느 방향으로 움직이는가"다.

| 변수 | 기울기 | 뜻 | 손실을 줄이려면 |
| --- | --- | --- | --- |
| `w` | −2.4 | w를 올리면 손실이 **준다**(음수) | w를 **올린다** |
| `b` | −1.2 | b를 올리면 손실이 **준다**(음수) | b를 **올린다** |

둘 다 음수인 이유는 간단하다. 예측 0.4가 정답 1.0보다 **작으니**, `y_pred = 2w + b`를 키우는 어느 쪽이든(w를 올리든 b를 올리든) 정답에 가까워진다. w 쪽 기울기가 두 배 큰 것은 w 앞에 x = 2가 곱해져 있어서 같은 양을 움직여도 예측이 두 배 움직이기 때문이다. 그래서 다음 셀에서 **기울기의 반대 방향으로** 빼는 식이 나온다.

### 1-3. `torch.no_grad()` 안에서 경사하강법 — 가중치·편향 한 번 갱신

```python
# 기울기 이용하여 가중치/편향 수정 -> 1학습
with torch.no_grad():                     # 기울기 기록을 일시 중지하는 블록
    # 경사하강법 : 가중치 = 기존가중치 - (학습률 * 기울기)
    w -= learning_rate * w.grad           # 0.2 - (0.1 * -2.4) => 0.44
    print('업데이트 전 w :', w.item())    # 0.4399999976158142
    print('기울기 :', w.grad.item())      # -2.4000000953674316
    print('학습률 :', learning_rate)      # 0.1
    print(w)                              # tensor(0.4400, requires_grad=True)
    b -= learning_rate * b.grad           # 0 - (0.1 * -1.2) => 0.12
    # 가중치/편향 기울기 0으로 초기화 (다시 계산하기 위한)
    w.grad.zero_()
    b.grad.zero_()
    print('한번 업데이트 이후 : ', w.item(), b.item())   # 0.4399999976158142 0.12000000476837158
    print(w * x + b)                      # tensor(1.)  업데이트 이후 예측값
```

**경사하강법(gradient descent)** 의 식은 주석 그대로다 — `새 가중치 = 기존 가중치 − 학습률 × 기울기`. 기울기가 음수이면 빼는 순간 더해져서 w가 커지고(0.2 → 0.44), 양수였다면 줄어든다. 즉 부호 판단을 사람이 하지 않아도 **식 하나가 항상 손실이 줄어드는 방향으로** 움직인다. `learning_rate = 0.1`은 그 한 걸음의 보폭이다.

| 줄 | 계산 | 전 | 후 |
| --- | --- | --- | --- |
| `w -= 0.1 * w.grad` | 0.2 − 0.1 × (−2.4) = 0.2 + 0.24 | 0.2 | **0.44** |
| `b -= 0.1 * b.grad` | 0.0 − 0.1 × (−1.2) = 0.0 + 0.12 | 0.0 | **0.12** |
| `w * x + b` | 0.44 × 2 + 0.12 | 0.4 | **1.0** |

갱신 뒤 예측이 정확히 정답 1.0에 닿았다. 손실 0.36이 한 걸음에 0이 된 셈인데, 이것은 표본 하나·특성 하나·학습률 0.1이 우연히 맞아떨어진 특수한 경우다(x = 2일 때 2w + b의 변화량 = 0.1 × (2 × 2.4 + 1.2) = 0.6 = 딱 모자란 만큼). 데이터가 수백 개면 한 표본에 맞추는 순간 다른 표본이 틀어지므로, 보통은 이 셀을 **에포크(epoch)만큼 반복**하며 손실이 천천히 내려가는 것을 본다.

이 셀에서 생기는 관용구가 세 개다.

| 관용구 | 왜 |
| --- | --- |
| `with torch.no_grad():` | `w -= ...`도 연산이라 그래프에 기록되면 "w를 고친 것"까지 다음 역전파에 끼어든다. 블록 안에서는 기록을 멈추므로 **갱신은 학습이 아니라 값 교체**로 처리된다. 밖에서 `w -= ...`를 하면 잎 텐서를 in-place로 바꾼다는 오류가 난다 |
| `w.grad.zero_()` | `backward()`는 `.grad`를 **덮어쓰지 않고 더한다**. 0으로 비우지 않으면 다음 역전파에서 −2.4 위에 새 기울기가 쌓여 보폭이 엉뚱해진다. 매 반복 시작 전(또는 갱신 직후)에 반드시 비운다 |
| 메소드 끝의 `_` | `zero_()`처럼 밑줄로 끝나는 메소드는 새 텐서를 만들지 않고 **그 자리에서 바꾸는(in-place)** 파이토치 이름 규칙. `w -= ...`도 in-place라 `w`의 `requires_grad=True`가 그대로 유지된다(출력 `tensor(0.4400, requires_grad=True)`) |

출력 첫 줄 `'업데이트 전 w :'` 뒤에 0.44가 찍히는 것은 `print`가 `w -= ...` 다음 줄에 있어서다 — 갱신은 이미 끝난 뒤라 바뀐 값이 나온다. 문자열보다 **줄의 순서**가 값을 정한다는 것을 보여 주는 출력이다.

### 1-4. 흐름 한 장 — 학습 한 바퀴

```
순전파   y_pred = x * w + b                 → 0.4        (앞 노트 1-5)
손실     loss = MSELoss(y_pred, y)          → 0.36       (1-1)
역전파   loss.backward()                    → w.grad −2.4, b.grad −1.2   (1-2)
갱신     with no_grad: w -= lr * w.grad     → w 0.44, b 0.12            (1-3)
초기화   w.grad.zero_(), b.grad.zero_()
확인     w * x + b                          → 1.0
```

day12부터 `모델.fit(X, y)` 한 줄에 숨어 있던 것이 이 여섯 줄이다. 사이킷런의 선형 회귀는 최소제곱 공식으로 한 번에 답을 냈지만, 신경망은 공식이 없어서 **이 바퀴를 수천 번 돌려 w·b를 조금씩 밀어 간다**. 앞으로 보게 될 `optimizer.zero_grad() → model(X) → loss → loss.backward() → optimizer.step()` 루프는 이 셀의 각 줄에 이름을 붙인 것이다.

## 2. 추가로 알면 좋은 활용법

### 2-1. 반복문으로 감싸기 — 에포크와 손실 곡선

수업 셀 두 개를 `for`로 감싸면 학습 루프가 된다. 손실을 리스트에 모아 두면 day09 맷플롯립으로 내려가는 곡선을 볼 수 있다.

```python
w = torch.tensor(0.2, requires_grad=True)
b = torch.tensor(0.0, requires_grad=True)
losses = []
for epoch in range(20):
    y_pred = x * w + b
    loss = criterion(y_pred, y)
    loss.backward()
    with torch.no_grad():
        w -= learning_rate * w.grad
        b -= learning_rate * b.grad
        w.grad.zero_(); b.grad.zero_()
    losses.append(loss.item())            # 그래프에서 떼어 낸 숫자만 저장
    if epoch % 5 == 0:
        print(f'{epoch:2d} loss={loss.item():.4f} w={w.item():.3f} b={b.item():.3f}')
```

`losses.append(loss)`가 아니라 `loss.item()`을 넣는 이유는, 텐서를 그대로 모으면 계산 그래프가 리스트에 붙잡혀 메모리가 계속 는다는 점 때문이다. 로그·그래프용 숫자는 항상 `.item()`(또는 `.detach()`)으로 꺼낸다.

### 2-2. 학습률이 결정하는 것 — 너무 크면 튀고 너무 작으면 멈춘다

같은 셀에서 `learning_rate`만 바꿔 보면 경사하강법의 성격이 보인다.

| 학습률 | 첫 갱신 뒤 w | 뒤 예측 | 양상 |
| --- | --- | --- | --- |
| 0.01 | 0.224 | 0.46 | 정답 쪽으로 조금씩 — 수렴은 하지만 느리다 |
| 0.1 | 0.44 | 1.0 | 이 수업의 값 — 한 걸음에 도달(특수한 경우) |
| 0.15 | 0.56 | 1.3 | 정답을 지나쳐 반대편으로(오차 −0.6 → +0.3) — 부호를 바꿔 가며 진동하다 수렴 |
| 0.3 | 0.92 | 2.2 | 지나친 폭(+1.2)이 원래 오차(0.6)보다 커서 걸음마다 멀어진다 — **발산** |
| 1.0 | 2.6 | 6.4 | 첫 걸음부터 열 배 밖으로 — 발산 |

이 예제에서 한 걸음에 예측이 움직이는 양은 학습률 × (2 × 2.4 + 1.2) = 학습률 × 6이라, 0.1이면 딱 0.6, 0.2를 넘으면 지나친 폭이 원래 오차보다 커져 발산한다. 경계값은 문제마다 다르지만 모양은 늘 같다 — 학습률은 모델이 배우는 값이 아니라 사람이 정하는 **하이퍼파라미터**다. day14 `GridSearchCV`로 `alpha`·`C`를 고르던 것처럼 딥러닝에서는 학습률이 첫 번째 탐색 대상이고, 보통 0.1·0.01·0.001처럼 10배 단위로 훑는다. 실제로는 처음엔 크게, 나중엔 작게 줄이는 스케줄러를 함께 쓴다.

### 2-3. 손실 함수 고르기 — 회귀·이진 분류·다중 분류

`nn.MSELoss`는 회귀용이다. 출력층의 활성화 함수와 손실 함수는 짝으로 고른다.

| 문제 | 출력층 | 손실 함수 | 사이킷런에서의 자리 |
| --- | --- | --- | --- |
| 회귀 | 없음(선형) | `nn.MSELoss()` · `nn.L1Loss()`(이상치에 둔감) · `nn.HuberLoss()` | day12 `LinearRegression` |
| 이진 분류 | `sigmoid` | `nn.BCELoss()` — 또는 시그모이드를 안에 합친 **`nn.BCEWithLogitsLoss()`**(수치적으로 안전) | day14 로지스틱 회귀 |
| 다중 분류 | `softmax` | **`nn.CrossEntropyLoss()`** — 소프트맥스가 안에 들어 있어 선형 출력을 그대로 넣고, 정답은 `torch.long` 정수 라벨 | day15 다중 분류 |

`WithLogits`·`CrossEntropy`처럼 활성화를 손실 안에 품은 쪽을 쓰는 것이 관례다. 확률로 바꾼 뒤 로그를 취하면 0 근처에서 값이 폭주하는데, 합쳐진 구현은 그 계산을 안전하게 처리한다. 이때 모델의 마지막 층에는 활성화를 붙이지 않는다.

### 2-4. 기울기 확인 관용구

```python
print(w.grad)                      # backward() 전엔 None
w.grad is None                     # 첫 역전파 전인지 확인
torch.autograd.grad(loss, [w, b])  # .grad에 쌓지 않고 기울기만 튜플로 받기
with torch.no_grad(): ...          # 평가·예측 때도 같은 블록 — 그래프를 안 만들어 빠르고 메모리 적게
w.detach()                         # 값만 복사(그래프 없음) — 저장·그리기용
```

`torch.no_grad()`는 갱신뿐 아니라 **예측·평가 구간 전체**를 감싸는 데도 쓴다. 학습이 끝난 모델로 테스트 세트를 돌릴 때 기울기를 기록할 이유가 없으니 `model.eval()`과 함께 늘 따라붙는다.

## 3. 더 나아가 알면 좋은 것

### 3-1. `optimizer.step()` — 갱신 셀이 한 줄로 접히는 자리

1-3의 `with torch.no_grad(): w -= lr * w.grad; ...; w.grad.zero_()`는 **옵티마이저**가 대신한다.

```python
optimizer = torch.optim.SGD([w, b], lr=0.1)   # 갱신할 텐서 목록과 학습률

for epoch in range(100):
    optimizer.zero_grad()          # = w.grad.zero_(); b.grad.zero_()
    y_pred = x * w + b
    loss = criterion(y_pred, y)
    loss.backward()
    optimizer.step()               # = no_grad 안에서 w -= lr * w.grad; b -= lr * b.grad
```

`SGD`(확률적 경사하강법)의 `step()`이 수업 셀의 식과 정확히 같은 일을 한다. 여기에 **모멘텀**(이전 걸음의 관성을 더해 진동을 줄임)·**Adam**(변수마다 보폭을 자동 조절 — 요즘 기본값)·**AdamW**(가중치 감쇠 분리) 같은 변형이 `torch.optim`에 들어 있고, 바꾸는 것은 `optimizer = torch.optim.Adam(...)` 한 줄이다. `zero_grad()`를 루프 맨 앞에 두는 것이 관례인 이유도 1-3의 "기울기는 누적된다"와 같다.

### 3-2. 미니배치와 확률적 경사하강법

수업은 표본 하나로 기울기를 구했다. 실제로는 세 가지 중 하나를 고른다.

| 방식 | 한 걸음에 쓰는 표본 | 성격 |
| --- | --- | --- |
| 배치 경사하강법 | 전체 | 기울기가 정확하지만 느리고 메모리가 크다 |
| 확률적 경사하강법(SGD) | 1개 | 빠르지만 걸음이 들쭉날쭉 — 수업 셀이 이 모양 |
| **미니배치** | 32·64·128개 | 둘의 절충 — 사실상 표준. `DataLoader(batch_size=32, shuffle=True)`가 잘라 준다 |

`MSELoss`가 "평균"인 이유가 여기서 드러난다 — 배치 32개의 제곱오차를 평균 내야 배치 크기와 무관하게 같은 학습률을 쓸 수 있다. 전체를 한 번 다 훑으면 1 **에포크**, 그 안의 갱신 한 번이 1 **스텝(iteration)** 이다.

### 3-3. 왜 기울기를 "거꾸로" 전하는가 — 연쇄 법칙과 층 쌓기

1-2의 표에서 ∂loss/∂w = ∂loss/∂y_pred × ∂y_pred/∂w로 쪼갠 것이 **연쇄 법칙(chain rule)** 이다. 층이 열 개여도 각 층은 "내 출력에 대한 기울기"를 받아 "내 입력·내 가중치에 대한 기울기"로 바꿔 앞 층에 넘기기만 하면 된다. 손실에서 출발해 입력 쪽으로 전해지니 **역**전파다. 이때 시그모이드의 기울기는 최대 0.25라 층마다 곱해지며 0으로 꺼지는 **기울기 소실**이 생기고, 이것이 은닉층에 ReLU(양수 구간 기울기 1)를 쓰는 이유다(앞 노트 1-4). 반대로 기울기가 커지며 폭주하는 **기울기 폭발**은 `torch.nn.utils.clip_grad_norm_`으로 자른다.

### 3-4. 다음에 볼 키워드

- `torch.optim.SGD`·`Adam`·`AdamW` — `zero_grad → forward → loss → backward → step` 루프
- 학습률 스케줄러 — `StepLR`·`CosineAnnealingLR`·`ReduceLROnPlateau`
- `nn.BCEWithLogitsLoss`·`nn.CrossEntropyLoss` — 활성화를 품은 손실
- `Dataset`·`DataLoader`·`batch_size`·`shuffle` — 미니배치
- `nn.Module` 상속과 `forward` — `w`·`b`가 `nn.Linear` 안으로 들어가는 모양
- `model.train()`/`model.eval()`과 `torch.no_grad()` 평가 블록
- 기울기 소실·폭발 — ReLU·배치 정규화·`clip_grad_norm_`·He/Xavier 초기화
- 검증 손실로 조기 종료 — day18 `early_stopping`의 딥러닝판
- 텐서보드·`tqdm`으로 손실 곡선 보기

## 실습 파일

- `KDT_2026/2026_Python/day21/dl-1.ipynb` — 파이토치 셀 다섯 번째(`y_pred = x * w + b`) 뒤에 이어진 부분과 여섯 번째 셀: ① `torch.relu(y_pred)` 호출 → `print(y_pred)` `tensor(0.4000, grad_fn=<AddBackward0>)` 그대로 ② `import torch.nn as nn` → `criterion = nn.MSELoss()` → `loss = criterion(y_pred, y)` → `tensor(0.3600, grad_fn=<MseLossBackward0>)` ③ `loss.backward()` → `w.grad.item(), b.grad.item()` → `-2.4000000953674316 -1.2000000476837158`(주석: 가중치를 올리면 오차가 준다) ④ `with torch.no_grad():` 안에서 `w -= learning_rate * w.grad`(0.2 − 0.1 × −2.4 = 0.44) → `'업데이트 전 w :' 0.4399999976158142`·`'기울기 :' -2.4…`·`'학습률 :' 0.1`·`tensor(0.4400, requires_grad=True)` → `b -= learning_rate * b.grad`(0.12) → `w.grad.zero_()`·`b.grad.zero_()` → `'한번 업데이트 이후 : ' 0.4399999976158142 0.12000000476837158` → `print(w * x + b)` `tensor(1.)`

## 관련 노트

[[AI 정리본 인덱스]] · [[AI day21 파이토치 텐서 생성·차원 재구성과 시그모이드·ReLU]] · [[AI day22 nn.Sequential 와인 이진 분류와 BCEWithLogitsLoss·AdamW 학습 루프]] · [[AI day21 구글 코랩 시작과 드라이브 마운트·런타임]] · [[AI day12 사이킷런 단순 선형 회귀로 물고기 무게 예측]] · [[KDT_2026 학습 지도]]
