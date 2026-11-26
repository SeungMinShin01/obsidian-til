---
출처: Claude 분석
원본: KDT_2026/2026_Python/day23/dl-3.ipynb
작성일: 2026-11-26
tags: [학습, ai, python]
---

# AI day23 — Conv2d·MaxPool2d CNN으로 SVHN 숫자 이미지 분류

> 실습 파일: `day23/dl-3.ipynb` (셀 0 — `torchvision.datasets.SVHN` 내려받기 · 셀 1 — 0) `device` → 1) 텐서 변환 → 2) CNN 컨테이너 → 3) `CrossEntropyLoss` → 4) `AdamW` → 5) 100 에포크 학습 → 6) 정확도 평가, 7) 추론은 주석 한 줄)
> 허브: [[AI 정리본 인덱스]] · 이전: [[AI day22 nn.Dropout 과적합 방지와 성적 회귀 신경망 뼈대]] · 다음: [[AI day24 TensorDataset·DataLoader 미니배치 학습으로 CNN 다시 돌리기]]

day21~22가 표 자료(와인 3열·성적 4열)를 `nn.Linear`로만 쌓은 신경망이었다면, 오늘은 입력이 **사진**이다. 자료는 구글 스트리트뷰에서 잘라 낸 집 주소 숫자 사진 **SVHN**(Street View House Numbers) — 32 × 32 칼라 이미지에 0~9 라벨이 붙어 있다. 그래서 새로 들어오는 것이 **합성곱 신경망(CNN)** 이다. `nn.Conv2d`·`nn.ReLU`·`nn.MaxPool2d`를 두 번 묶고 `nn.Flatten`으로 펴서 `nn.Linear`로 분류하는 구조인데, 뒤쪽 3)~6)은 day22의 학습 루프가 **손실 함수 한 줄만 바뀐 채** 그대로다. 파일 첫 줄 주석대로 코랩 런타임을 **T4 GPU**로 바꿔야 돌아가는 첫 실습이기도 하다 — 2만 장짜리 이미지 텐서를 `.to(device)`로 그래픽 메모리에 올려 놓고 학습한다. 바뀐 것(입력 모양·합성곱 층·다중 분류 손실·GPU)과 안 바뀐 것(학습 루프 여섯 박자·`eval()`·사이킷런으로 채점)을 가르며 정리한다.

## 1. 배운 내용

### 1-1. `torchvision.datasets.SVHN` — 내려받기 한 줄로 자료가 온다

```python
# CNN실습시 필수: 코랩 오른쪽 상단에 -> 연결v 클릭하여 -> 런타임 유형 변경
#   T4 GPU( 그래픽 사용 ) 클릭 -> 저장 -> 연결

# 0) 실습에 필요한 데이터셋( SVHN 칼라의 0 부터 9 까지의 이미지 )
from torchvision import datasets
raw_train = datasets.SVHN(root='./data', split='train', download=True)
raw_test  = datasets.SVHN(root='./data', split='test',  download=True)
```

```
100%|██████████| 182M/182M  [00:28<00:00, 6.41MB/s]
100%|██████████| 64.3M/64.3M [00:04<00:00, 14.5MB/s]
```

`torchvision`은 파이토치의 이미지 전용 짝 패키지로, 유명 이미지 데이터셋을 한 줄로 내려받는 `datasets`, 전처리 `transforms`, 사전학습 모델 `models`를 들고 있다(모델은 day24에서). `read_csv(url)` 자리를 `datasets.SVHN(...)`이 대신하는 셈이다.

| 인자 | 뜻 |
| --- | --- |
| `root='./data'` | 저장 폴더 — 코랩에서는 `/content/data/`라 런타임이 끊기면 사라진다(day21 경로 세 갈래). 다시 실행하면 다시 받는다 |
| `split='train'` / `'test'` | 학습용 73,257장 · 테스트용 26,032장. `'extra'`(53만 장)도 있다 |
| `download=True` | 없으면 받고, 있으면 건너뛴다 |

받아 온 객체에서 쓰는 속성은 둘이다. **`raw_train.data`** 는 넘파이 `uint8` 배열로 모양이 `(73257, 3, 32, 32)` — 장수 × **채널(RGB 3) × 세로 × 가로** 순서이고, **`raw_train.labels`** 는 `(73257,)` 정수 배열로 값이 0~9다(원본 `.mat` 파일은 숫자 0을 10으로 적어 두는데 torchvision이 0으로 바꿔 준다). 자료 크기 182 MB·64 MB는 이 배열이 그대로 담긴 `.mat` 파일 크기다.

### 1-2. GPU 장치와 텐서 변환 — `.to(device)`와 `/ 255.0`

```python
# 0) GPU 연산 장치 설정
import torch   # 'cuda' : 엔비디아 그래픽 드라이버 이름
device = 'cuda' if torch.cuda.is_available() else 'cpu'
print(device)                                             # cuda

# 1) 파이토치의 텐서 타입으로 변경 — 샘플로 2만개만 사용
X_train = torch.tensor(raw_train.data[:20000],   dtype=torch.float32).to(device) / 255.0
Y_train = torch.tensor(raw_train.labels[:20000], dtype=torch.long).to(device)
X_test  = torch.tensor(raw_test.data[:2000],     dtype=torch.float32).to(device) / 255.0
Y_test  = torch.tensor(raw_test.labels[:2000],   dtype=torch.long).to(device)
```

day21에 적어 두기만 했던 `device` 관용구가 처음으로 **`cuda`** 를 찍는다. 런타임 유형을 T4로 바꿨기 때문이고, CPU 런타임이면 같은 코드가 `cpu`를 찍고 훨씬 느리게 돈다. 네 줄의 텐서 변환에서 달라진 점이 셋이다.

| 항목 | day22(표 자료) | day23(이미지) | 이유 |
| --- | --- | --- | --- |
| 입력 모양 | `(N, 특성 수)` 2차원 | **`(N, 3, 32, 32)` 4차원** | `Conv2d`는 (배치, 채널, 높이, 너비)를 받는다 |
| 전처리 | `StandardScaler` | **`/ 255.0`** | 픽셀은 전부 0~255 같은 단위라 최댓값으로 나눠 0~1로 — 표준화 대신 **정규화** |
| 타깃 타입 | `float32` + `unsqueeze(1)` → `(N, 1)` | **`torch.long`** 그대로 `(N,)` | 다중 분류 `CrossEntropyLoss`는 정수 클래스 번호 1차원을 받는다(day21 2-3 표의 그 줄) |
| 장치 | 없음(CPU) | **`.to(device)`** | 모델도 자료도 같은 장치에 있어야 연산된다 |

`[:20000]`으로 자른 것은 시간 때문이다 — 7만 장 전체를 한 번에 순전파하면 T4에서도 에포크 하나가 길고 메모리도 빠듯하다. 2만 장 × 3 × 32 × 32 × 4바이트 ≈ 246 MB가 GPU 메모리에 통째로 올라간다. 타깃 `Y`는 나누지 않는다는 주석("Y(타깃/정답) 제외")이 중요하다 — 라벨은 밝기가 아니라 **클래스 번호**라 스케일이 없다.

### 1-3. `nn.Conv2d` — 필터가 이미지를 훑으며 특성 맵을 만든다

```python
# 2) 합성곱 신경망 레이어 컨테이너 설정
import torch.nn as nn
model = nn.Sequential(
    # (1) 레이어1: 합성곱 -> 렐루 -> 풀링
    nn.Conv2d(in_channels=3, out_channels=16, kernel_size=3, padding=1),   # (3,32,32) -> (16,32,32)
    nn.ReLU(),
    nn.MaxPool2d(kernel_size=2, stride=2),                                   # (16,32,32) -> (16,16,16)
    # (2) 레이어2: 레이어 추가하여 중요한 특성 추가적으로 추출
    nn.Conv2d(in_channels=16, out_channels=32, kernel_size=3, padding=1),  # (16,16,16) -> (32,16,16)
    nn.ReLU(),
    nn.MaxPool2d(kernel_size=2, stride=2),                                   # (32,16,16) -> (32,8,8)
    # (3) 출력/분류기 레이어
    nn.Flatten(),                                                            # 32*8*8 = 2048 (1차원)
    nn.Linear(in_features=32*8*8, out_features=64),
    nn.ReLU(),
    nn.Linear(in_features=64, out_features=10),                              # 분류할 클래스 수
).to(device)   # GPU 연산 하라는 설정
```

`nn.Linear`는 입력의 **모든** 숫자를 출력의 모든 노드에 잇는다(완전 연결). 32 × 32 × 3 = 3,072개 픽셀을 그대로 `Linear`에 넣으면 "왼쪽 위 픽셀과 오른쪽 아래 픽셀"처럼 상관없는 쌍까지 전부 가중치를 두게 되고, 숫자가 한 칸만 옆으로 밀려도 다른 입력이 된다. **합성곱**은 작은 창(필터·커널) 하나를 이미지 위에서 **밀어 가며 같은 가중치를 재사용**하는 층이라, 위치가 바뀌어도 같은 무늬(모서리·획)를 잡아낸다.

| 인자 | 이 코드 | 뜻 |
| --- | --- | --- |
| `in_channels` | 3 → 16 | 들어오는 채널 수. 첫 층은 **이미지 채널**(흑백 1·칼라 3), 다음 층은 **앞 층의 `out_channels`** 와 같아야 한다 — `Linear`의 "다음 입력 = 앞 출력" 규칙과 동일 |
| `out_channels` | 16, 32 | 필터 개수 = 만들어지는 **특성 맵** 장수. 필터 하나가 무늬 하나를 담당한다 |
| `kernel_size` | 3 | 필터 크기 3 × 3 (5 × 5도 흔함). 작을수록 세밀한 무늬 |
| `padding` | 1 | 가장자리에 0을 한 겹 둘러 **크기를 유지**한다 — 3 × 3 필터에 패딩 1이면 입출력 가로세로가 같다 |

한 층의 매개변수 수는 `in × out × k × k + out`이다. 첫 층 3 × 16 × 9 + 16 = **448개**로 32 × 32 이미지 전체에 적용된다 — 같은 448개가 1,024개 위치에서 재사용되니 `Linear`로 같은 일을 하려면 수백만 개가 필요했을 자리다. 주석의 `(16, 32, 32)` 표기가 (특성 맵 수, 세로, 가로) 순서로 출력 모양을 읽는 법이다.

### 1-4. `nn.MaxPool2d` — 절반으로 줄이며 가장 강한 반응만 남긴다

`MaxPool2d(kernel_size=2, stride=2)`는 2 × 2 칸마다 **최댓값 하나**만 남기고 2칸씩 건너뛰므로 가로세로가 **절반**이 된다. 32 → 16 → 8. 학습할 매개변수는 없다.

| 역할 | 설명 |
| --- | --- |
| 크기 축소 | 다음 층의 계산량과 `Flatten` 뒤 `Linear` 입력 수를 줄인다(32 × 32에서 펴면 16,384 → 8 × 8에서 펴면 2,048) |
| 위치 둔감 | 2 × 2 안에서 무늬가 한 칸 움직여도 최댓값은 같다 — 작은 이동에 강해진다 |
| 요약 | "이 근처에 이 무늬가 있었나"만 남기고 정확한 좌표는 버린다 |

`Conv2d → ReLU → MaxPool2d` 묶음이 두 번 반복되는 것이 day22의 `Linear → ReLU → Dropout` 리듬의 CNN판이다. 첫 묶음은 획·모서리 같은 낮은 수준 무늬, 둘째 묶음(채널 16 → 32)은 그 조합인 더 큰 무늬를 잡는다는 것이 주석 "중요한 특성 추가적으로 추출"의 뜻이다.

### 1-5. `nn.Flatten`과 분류기 — 3차원 특성 맵을 펴서 `Linear`로

둘째 풀링까지 지나면 모양이 `(N, 32, 8, 8)`이다. `nn.Flatten()`은 배치 축만 남기고 나머지를 한 줄로 펴 `(N, 2048)`로 만든다 — 그래서 바로 다음 `Linear`의 `in_features`가 **`32*8*8`** 이다. 이 숫자는 입력 이미지 크기·패딩·풀링 횟수에서 계산되는 값이라, 이미지가 64 × 64이면 `32*16*16`으로 바뀐다. 모양이 안 맞으면 `mat1 and mat2 shapes cannot be multiplied` 오류가 바로 나므로, 헷갈리면 모델을 만들기 전에 `model[:7](X_train[:1]).shape`처럼 앞부분만 통과시켜 확인하는 것이 안전하다.

| 층 | 출력 모양 | 매개변수 |
| --- | --- | --- |
| 입력 | `(N, 3, 32, 32)` | |
| `Conv2d(3, 16, 3, p=1)` · `ReLU` | `(N, 16, 32, 32)` | 448 |
| `MaxPool2d(2, 2)` | `(N, 16, 16, 16)` | 0 |
| `Conv2d(16, 32, 3, p=1)` · `ReLU` | `(N, 32, 16, 16)` | 4,640 |
| `MaxPool2d(2, 2)` | `(N, 32, 8, 8)` | 0 |
| `Flatten` | `(N, 2048)` | 0 |
| `Linear(2048, 64)` · `ReLU` | `(N, 64)` | 131,136 |
| `Linear(64, 10)` | `(N, 10)` | 650 |
| 합계 | | **136,874개** |

매개변수의 96 %가 `Linear(2048, 64)` 한 층에 몰려 있다 — 합성곱 층은 가볍고, 펴서 붙인 완전 연결 층이 무겁다는 것이 CNN의 전형적인 분포다. 마지막 `Linear(64, 10)`의 10은 **클래스 수**고, 뒤에 활성화가 없다 — 소프트맥스는 손실 함수가 품는다(1-6).

### 1-6. `CrossEntropyLoss` — 다중 분류의 손실, 소프트맥스를 품고 있다

```python
# 3) 손실함수: 다중분류 이므로 소프트맥스
crierion = nn.CrossEntropyLoss()
# 4) 옵티마이저
import torch.optim as optim
optimizer = optim.AdamW(model.parameters(), lr=0.005)
```

day21 2-3 표의 셋째 줄이 실제 코드가 됐다. 모델의 마지막 출력 10개(**로짓**)에 `CrossEntropyLoss`가 안에서 소프트맥스(`log_softmax`)를 씌워 확률로 바꾸고, 정답 클래스의 확률이 1에서 얼마나 먼지를 잰다. day22의 `BCEWithLogitsLoss`가 시그모이드를 품었듯 이쪽은 소프트맥스를 품었고, 그래서 **모델 끝에 `Softmax` 층을 두지 않는다**(두 번 씌우면 학습이 느려진다).

| | 이진 분류(day22 와인) | 다중 분류(오늘) |
| --- | --- | --- |
| 출력층 | `Linear(16, 1)` | `Linear(64, 10)` — 클래스 수만큼 |
| 손실 | `BCEWithLogitsLoss` (시그모이드 내장) | **`CrossEntropyLoss`** (소프트맥스 내장) |
| 타깃 | `float32` `(N, 1)` 0.0/1.0 | **`long` `(N,)`** 0~9 정수 — 원-핫 아님 |
| 확률로 읽기 | `torch.sigmoid(logits)` | `torch.softmax(logits, dim=1)` |
| 예측 클래스 | `>= 0.5` | **`argmax(dim=1)`** |

학습률은 0.005 — day22의 0.01보다 반으로 줄였다. 매개변수가 13만 개로 늘고 이미지 입력이라 보폭을 조금 좁힌 선택이다.

### 1-7. 학습 루프 — 여섯 박자 그대로, 손실 2.31 → 0.72

```python
# 5) 에포크(학습수) 단위 학습( 순전파 -> 오차계산 -> 역전파 -> 업데이트 )
for epoch in range(100):
    model.train()                        # 1- 학습모드
    optimizer.zero_grad()                # 2- 이전기울기 초기화
    logits = model(X_train)              # 3- 순전파(학습)
    loss = crierion(logits, Y_train)     # 4- 오차(학습과 정답 차이)
    loss.backward()                      # 5- 역전파
    optimizer.step()                     # 6- 가중치/편향 업데이트
    if epoch % 10 == 0:
        print(epoch, ": loss: ", loss.item())
```

day22 1-5의 여섯 줄과 한 글자도 다르지 않다. 2만 장을 한 번에 넣는 **배치 경사하강법**이라 에포크당 갱신이 한 번, 100 에포크에 100번이다.

| 에포크 | 손실 | 읽기 |
| --- | --- | --- |
| 0 | **2.3055** | ≈ ln 10 = 2.3026 — 열 클래스를 똑같이 1/10로 찍는 상태(day22의 ln 2 = 0.693과 같은 눈금) |
| 10 | 2.2290 | 느리다 |
| 20 | 2.1719 | |
| 30 | 1.9825 | 여기서부터 꺾인다 |
| 40 | 1.6054 | |
| 50 | 1.2989 | |
| 60 | 1.0783 | |
| 70 | 0.9365 | |
| 80 | 0.8115 | |
| 90 | **0.7177** | 아직 내려가는 중 |

처음 30바퀴 동안 거의 안 움직이다가 갑자기 떨어지는 모양이 눈에 띈다. 무작위 초기 가중치의 필터가 쓸 만한 무늬를 잡기 시작하는 데 시간이 걸리고, 한 에포크에 갱신이 한 번뿐이라 그 시간이 길게 보인다. 90에서도 기울기가 살아 있으니 에포크를 더 돌리거나(또는 day24처럼 미니배치로 갱신 횟수를 늘리거나) 하면 더 내려갈 여지가 있다.

### 1-8. 평가 — `argmax`로 클래스를 고르고 사이킷런으로 채점

```python
# 6) 모델 평가
model.eval()
with torch.no_grad():
    test_logits = model(X_test)                     # (2000, 10)
    test_pred = torch.argmax(test_logits, dim=1)    # (2000,) — 가장 큰 로짓의 자리 = 예측 클래스
from sklearn.metrics import accuracy_score          # sklearn 에서 텐서 사용불가
print(accuracy_score(Y_test.cpu().numpy(), test_pred.cpu().numpy()))   # 0.7585 — 실행마다 다름
```

`eval()` + `no_grad()`는 day22 그대로. 달라진 것은 로짓 → 예측을 **`argmax(dim=1)`** 로 한다는 점 — 열 개 로짓 중 가장 큰 자리의 번호가 예측 숫자다(주석의 `[0.6, 0.25, 0.15]` → 0번). 소프트맥스를 씌워도 순서는 같으니 확률이 필요 없으면 로짓에 바로 `argmax`를 건다.

그리고 **`.cpu().numpy()`** — GPU에 있는 텐서는 바로 넘파이로 못 바꾸므로(`can't convert cuda:0 device type tensor to numpy`) CPU로 옮긴 뒤 `numpy()`를 부른다. day21 2-1 표의 `.cpu()`가 실제로 필요해진 첫 자리다. 사이킷런은 넘파이만 받으니 정답·예측 둘 다 이렇게 넘긴다.

테스트 2,000장 정확도 **0.7585**. 열 클래스 무작위가 0.1이고, 가장 흔한 숫자 1만 찍어도 0.19쯤이니 작은 CNN을 100바퀴 돌려 76 %는 분명히 배운 것이다. 다만 SVHN은 잘 만든 CNN이 95 %를 넘는 자료라, 2만 장·배치 경사하강법·100 에포크의 한계가 남아 있다 — 그 첫 손질이 day24의 미니배치다. `manual_seed`를 고정하지 않아 "실행마다 다름"이라는 주석대로 숫자는 매번 조금씩 바뀐다.

## 2. 추가로 알면 좋은 활용법

### 2-1. 이미지 한 장 보기와 모양 확인 — 자료를 눈으로

```python
import matplotlib.pyplot as plt
img = raw_train.data[0]                 # (3, 32, 32) uint8
plt.imshow(img.transpose(1, 2, 0))      # imshow는 (H, W, C) 순서를 받는다
plt.title(raw_train.labels[0]); plt.show()
print(raw_train.data.shape, raw_train.labels.shape)   # (73257, 3, 32, 32) (73257,)
```

파이토치는 **채널 먼저**(C, H, W), 맷플롯립·PIL은 **채널 나중**(H, W, C)이라 그릴 때 `transpose`가 한 번 들어간다. 모양을 먼저 찍어 보는 습관(day21 `.shape`부터)이 CNN에서는 더 중요하다 — `Linear`의 `in_features` 2048이 어디서 왔는지가 여기서 보인다.

### 2-2. 혼동행렬 — 어떤 숫자끼리 헷갈리나

```python
from sklearn.metrics import confusion_matrix, classification_report
y_true, y_pred = Y_test.cpu().numpy(), test_pred.cpu().numpy()
print(confusion_matrix(y_true, y_pred))
print(classification_report(y_true, y_pred))
```

day15의 도구를 그대로 쓴다. 정확도 하나보다 3 ↔ 5, 1 ↔ 7처럼 **어느 쌍이 섞이는지**가 다음 손질의 단서가 된다. 클래스 분포도 `np.bincount(raw_train.labels)`로 한 번 보면 1·2가 많고 0·9가 적은 치우침이 있다.

### 2-3. `torchvision.transforms` — 전처리를 파이프라인으로

```python
from torchvision import transforms
tf = transforms.Compose([
    transforms.ToTensor(),                                   # uint8 (H,W,C) → float32 (C,H,W), 0~1
    transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5)),  # 채널별 (x − 평균) / 표준편차
])
train_set = datasets.SVHN(root='./data', split='train', download=True, transform=tf)
```

`/ 255.0`을 손으로 한 자리를 `ToTensor`가 대신하고, `Normalize`로 day13의 표준화를 채널 단위로 더할 수 있다. `transform=`을 데이터셋에 넘기면 한 장씩 꺼낼 때 자동 적용되고, `RandomCrop`·`RandomHorizontalFlip`·`ColorJitter` 같은 **데이터 증강**도 같은 자리에 끼운다(숫자는 좌우 뒤집으면 뜻이 바뀌니 플립은 빼는 것이 맞다). 이렇게 만든 데이터셋은 day24의 `DataLoader`에 바로 들어간다.

### 2-4. 출력 모양 계산 공식

합성곱·풀링 뒤 한 변의 크기는 `(입력 + 2 × padding − kernel) / stride + 1`이다. 32 × 32에 `k=3, p=1, s=1`이면 (32 + 2 − 3) / 1 + 1 = 32(유지), `MaxPool2d(2, 2)`면 (32 − 2) / 2 + 1 = 16(절반). `padding=0`으로 두면 3 × 3마다 2씩 줄어 30 → 28 → … 이 되고 `Flatten` 숫자도 따라 바뀐다. `nn.LazyLinear(64)`를 쓰면 `in_features`를 첫 순전파 때 자동으로 잡아 주므로 계산이 귀찮을 때 대안이 된다.

## 3. 더 나아가 알면 좋은 것

### 3-1. 왜 CNN인가 — 지역성·가중치 공유·계층적 특성

이미지의 정보는 **가까운 픽셀끼리** 뭉쳐 있고(지역성), 같은 무늬는 **어디에나** 나타날 수 있다(이동 불변). 합성곱은 이 두 가정을 구조에 박아 넣은 층이라 매개변수가 적으면서도 잘 일반화한다. 층을 쌓으면 앞은 모서리·색 변화, 가운데는 획·곡선, 뒤는 숫자 모양 전체처럼 **점점 큰 단위**를 보게 된다(수용 영역이 넓어진다). 1998년 LeNet-5(손글씨 우편번호)가 오늘 구조와 거의 같은 `Conv → Pool → Conv → Pool → FC`다.

### 3-2. 유명 구조들 — 오늘 구조에서 무엇이 더해졌나

- **AlexNet**(2012) — ReLU·드롭아웃·GPU 학습으로 이미지넷 우승, 딥러닝 붐의 시작
- **VGG**(2014) — 3 × 3 필터만 깊게 쌓기(오늘 `kernel_size=3`의 근거)
- **ResNet**(2015) — 잔차 연결로 50·101층을 학습 가능하게 — day24에서 `resnet50`을 그대로 불러다 쓴다
- **배치 정규화** `nn.BatchNorm2d` — `Conv2d` 뒤에 두어 학습을 안정시키고 학습률을 키울 수 있게

### 3-3. 미니배치와 데이터 증강 — 76 %를 올리는 두 손잡이

2만 장을 한 번에 넣는 지금 방식은 에포크당 갱신 한 번이라 느리고 메모리도 많이 쓴다. `DataLoader(batch_size=128, shuffle=True)`로 쪼개면 에포크당 157번 갱신되어 같은 100 에포크에 훨씬 멀리 간다 — 그것이 다음 노트다. 그 다음은 회전·이동·밝기 변화를 섞는 증강과 `BatchNorm2d`·드롭아웃, 그리고 7만 장 전부 쓰기다.

### 3-4. 다음에 볼 키워드

- `torch.utils.data.TensorDataset`·`DataLoader` — 미니배치 학습 (다음 노트)
- `torchvision.models.resnet50(weights='DEFAULT')` — 사전학습 모델 전이학습 (day24)
- `nn.BatchNorm2d`·`nn.Dropout2d`·`nn.AdaptiveAvgPool2d`
- `stride`·`dilation`·`groups` — `Conv2d`의 나머지 인자
- `torchsummary`/`torchinfo.summary(model, (3, 32, 32))` — 층별 출력 모양·매개변수 표 자동 출력
- `torch.manual_seed`·`torch.backends.cudnn.deterministic` — GPU 재현성
- 수용 영역(receptive field)·특성 맵 시각화(`model[0].weight`)
- 전이학습·파인튜닝·ONNX 내보내기

## 실습 파일

- `KDT_2026/2026_Python/day23/dl-3.ipynb` — 셀 0: 런타임 T4 GPU 변경 주석 → `from torchvision import datasets` → `datasets.SVHN(root='./data', split='train'/'test', download=True)`(182 MB·64.3 MB) · 셀 1: 0) `device = 'cuda' if torch.cuda.is_available() else 'cpu'` → `cuda` → 1) `torch.tensor(raw_train.data[:20000], float32).to(device) / 255.0`·`labels` `torch.long`·테스트 2,000장 → 2) `nn.Sequential(Conv2d(3,16,3,p=1)·ReLU·MaxPool2d(2,2) → Conv2d(16,32,3,p=1)·ReLU·MaxPool2d(2,2) → Flatten → Linear(2048,64)·ReLU → Linear(64,10)).to(device)` → 3) `nn.CrossEntropyLoss()` → 4) `optim.AdamW(lr=0.005)` → 5) `range(100)` 여섯 박자 루프, 10바퀴마다 손실(2.3055 → 0.7177) → 6) `eval()`·`no_grad`·`argmax(dim=1)`·`accuracy_score(Y.cpu().numpy(), pred.cpu().numpy())` 0.7585 → 7) 모델 추론(주석)

## 관련 노트

[[AI 정리본 인덱스]] · [[AI day22 nn.Dropout 과적합 방지와 성적 회귀 신경망 뼈대]] · [[AI day24 TensorDataset·DataLoader 미니배치 학습으로 CNN 다시 돌리기]] · [[AI day21 구글 코랩 시작과 드라이브 마운트·런타임]] · [[AI day15 로지스틱 다중 분류와 혼동행렬·분류 리포트]] · [[KDT_2026 학습 지도]]
