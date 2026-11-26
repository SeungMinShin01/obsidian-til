---
출처: Claude 분석
원본: KDT_2026/2026_Python/day24/dl-4.ipynb(3셀 — [3] 이미지분류 사전학습 모델 추론)
작성일: 2026-11-26
tags: [학습, ai, python]
---

# AI day24 — resnet50 사전학습 모델 전이학습과 state_dict 저장

> 실습 파일: `day24/dl-4.ipynb` (마크다운 `### [3] 이미지분류 사전학습 모델 추론` 아래 셀 — 앞 셀의 미니배치 코드에서 2) 모델 블록을 `torchvision.models.resnet50`으로 바꾸고, 학습률 0.0001 · 5 에포크 · 끝에 `torch.save`; 셀 출력은 노트북에 저장돼 있지 않다)
> 허브: [[AI 정리본 인덱스]] · 이전: [[AI day24 TensorDataset·DataLoader 미니배치 학습으로 CNN 다시 돌리기]] · 다음: (아직 없음)

같은 파일 셋째 셀은 앞 셀을 또 한 번 복사한 뒤 `#####` 블록 세 군데를 바꾼 것이다. 2) 자리의 **직접 만든 CNN을 지우고 `models.resnet50(weights='DEFAULT')`** 를 불러 마지막 층만 갈아 끼우고, 4) 학습률을 **0.0001**로 50배 낮추고, 5) 에포크를 **5**로 줄였다. 그리고 처음으로 7)이 채워졌다 — **`torch.save(model.state_dict(), 'resnet50_custom.pth')`**. 100 에포크 돌려 76 %였던 자리에, 남이 1,400만 장으로 미리 학습해 둔 50층짜리 모델을 빌려 와 다섯 바퀴만 **미세 조정**하는 것이 **전이학습**이다. 왜 학습률과 에포크가 그렇게 바뀌는지, 마지막 층을 어떻게 바꾸는지, 그리고 저장한 `.pth`가 머신러닝의 `.pkl`과 어떻게 다른지를 정리한다.

## 1. 배운 내용

### 1-1. `models.resnet50(weights='DEFAULT')` — 가중치까지 들어 있는 모델을 받는다

```python
# 2) 기존 CNN 설정 지우고 사전학습으로 교체
################## 사전학습모델 #########################
import torch.nn as nn
import torchvision.models as models
model = models.resnet50(weights='DEFAULT')   # 사전학습 모델에 저장된 가중치 기본값 불러오기
```

`torchvision.models`에는 ResNet·VGG·EfficientNet·MobileNet 등 유명 구조가 **함수 하나**로 들어 있다. `weights='DEFAULT'`를 주면 구조만이 아니라 **이미지넷(ImageNet, 1,000 클래스 · 약 128만 장)으로 학습을 마친 가중치**를 함께 내려받는다(ResNet50은 약 100 MB, 코랩에서 첫 실행 때 받는다). `weights=None`이면 무작위 초기값의 빈 구조만 온다.

| 항목 | 내용 |
| --- | --- |
| ResNet50 | 2015년 ILSVRC 우승 구조. 합성곱 층 49개 + 완전 연결 1개 = 50층, 매개변수 약 2,560만 개 |
| 잔차 연결 | 몇 층 건너뛰어 입력을 출력에 더하는 지름길(`x + F(x)`) — 50·101층을 쌓아도 기울기가 사라지지 않게 해 준 아이디어 |
| `'DEFAULT'` | 그 구조의 가장 좋은 공개 가중치(현재 `IMAGENET1K_V2`, 이미지넷 top-1 약 80.9 %). 버전을 박아 두려면 `weights=models.ResNet50_Weights.IMAGENET1K_V2` |
| 입력 | `(N, 3, H, W)` — 앞 셀과 같은 모양이라 자료 준비 코드가 그대로 쓰인다. 첫 층이 7 × 7 합성곱 + 풀링, 끝이 `AdaptiveAvgPool2d`라 32 × 32도 224 × 224도 받는다 |

day23에서 13만 개 매개변수의 CNN을 처음부터 학습하던 것과 비교하면, 이번엔 **2,560만 개가 이미 "선·모서리·질감·물체 부분"을 알고 있는 상태**에서 시작한다. 이미지넷에 집 주소 숫자는 없지만 그 아래 단계의 시각 특징은 어떤 이미지 문제에나 쓸모가 있다 — 그래서 "전이"다.

### 1-2. `model.fc` 교체 — 1,000 클래스 머리를 10 클래스로

```python
in_features = model.fc.in_features    # 사전모델 학습의 특성맵 수 (2048)
# 다음 레이어 연결시 이전 레이어의 특성맵 수 알아야 한다.
model.fc = nn.Sequential(
    nn.Linear(in_features=in_features, out_features=128),   # 2048 -> 128
    nn.ReLU(), nn.Dropout(p=0.2),                            # 과적합 방지
    nn.Linear(in_features=128, out_features=10),             # 출력층 — 우리 클래스 수
)
model = model.to(device)   # GPU 사용
######################################################
```

ResNet50의 마지막 층 `fc`는 `Linear(2048, 1000)` — 이미지넷 1,000종을 고르는 **머리(head)** 다. 우리는 0~9 열 가지만 필요하니 이 한 층을 떼고 새 머리를 붙인다. 모델이 `nn.Module`의 속성(`model.fc`)으로 층을 들고 있어서 **대입 한 줄**로 교체된다.

| 줄 | 하는 일 |
| --- | --- |
| `model.fc.in_features` | 떼어 낼 층이 받던 입력 수 **2048**을 읽어 둔다 — 하드코딩 대신 읽는 이유는 ResNet18은 512, EfficientNet은 1280처럼 모델마다 다르기 때문 |
| `nn.Sequential(Linear(2048,128) → ReLU → Dropout(0.2) → Linear(128,10))` | 새 머리. day22의 `Linear → ReLU → Dropout` 묶음 한 번 + 출력층. 새로 만든 층이라 이 부분만 **무작위 초기값**이다 |
| `model.to(device)` | 교체한 뒤에 옮긴다 — `fc`를 바꾸기 전에 옮기면 새 `fc`만 CPU에 남아 장치 불일치 오류가 난다 |

앞에 붙어 있는 49개 층(몸통, backbone)은 그대로고 `requires_grad`도 켜져 있다. 즉 이 코드는 몸통을 **얼리지 않고** 전체를 함께 학습하는 **파인튜닝** 방식이다 — 그래서 4)의 학습률이 작아진다(1-3). 새 머리의 매개변수는 2048 × 128 + 128 + 128 × 10 + 10 = **263,562개**로, 몸통 2,350만 개에 비하면 1 %다.

### 1-3. 학습률 0.0001과 에포크 5 — 이미 잘 맞춰진 가중치를 흐트러뜨리지 않기

```python
# 3) 손실함수: 다중분류 이므로 소프트맥스
criterion = nn.CrossEntropyLoss()
# 4) 옵티마이저
import torch.optim as optim
################## 사전학습모델은 학습률 촘촘히 #########################
optimizer = optim.AdamW(model.parameters(), lr=0.0001)
########################################################################
# 5) 에포크(학습수) 단위 학습
for epoch in range(5):   # 반복문 수 줄이기
    model.train()
    total_loss = 0.0
    for bach_X, bach_Y in train_loader:         # 앞 셀의 128장 미니배치 그대로
        optimizer.zero_grad()
        logits = model(bach_X)
        loss = criterion(logits, bach_Y)
        loss.backward()
        optimizer.step()
        total_loss += loss.item()
    total_loss = total_loss / len(train_loader)
    print(epoch, ": loss: ", total_loss)
```

| | day23~24 CNN(처음부터) | ResNet50 파인튜닝 | 이유 |
| --- | --- | --- | --- |
| 학습률 | 0.005 | **0.0001** (1/50) | 몸통 가중치는 이미 좋은 자리에 있다. 큰 보폭이면 이미지넷에서 배운 것을 몇 스텝 만에 망가뜨린다(**파국적 망각**). 주석의 "촘촘히"가 이 뜻 |
| 에포크 | 100 | **5** | 몸통이 특징을 이미 뽑아 주니 머리만 맞추면 되고, 한 에포크가 50층 순전파 157번이라 비싸다 — 보통 수 에포크면 수렴 |
| 손실·루프 | `CrossEntropyLoss`·여섯 박자 | 동일 | 모델이 바뀌어도 학습 루프는 불변 — day22부터 이어지는 규칙 |
| 매개변수 | 13만 | 2,560만 | T4에서 32 × 32 이미지 128장 배치면 충분히 돈다 |

`model.parameters()`를 그대로 넘겼으니 몸통과 머리가 **같은 학습률**로 움직인다. 머리는 무작위 초기값이라 더 크게 움직여도 되고 몸통은 작게 움직여야 하는데, 그 구분은 2-1의 매개변수 그룹으로 할 수 있다. 셀 출력이 저장돼 있지 않아 이 파일의 손실·정확도 값은 남아 있지 않다. 다만 사전학습 모델은 첫 에포크부터 손실이 크게 내려가고, 같은 2만 장으로도 처음부터 만든 CNN보다 높은 정확도에 훨씬 적은 에포크로 닿는 것이 전이학습의 전형적인 그림이다.

### 1-4. 평가 — 그대로, 그리고 `Dropout`이 있으니 `eval()`이 다시 중요

```python
# 6) 모델 평가
model.eval()
with torch.no_grad():
    test_logits = model(X_test)
    test_pred = torch.argmax(test_logits, dim=1)
from sklearn.metrics import accuracy_score
print(accuracy_score(Y_test.cpu().numpy(), test_pred.cpu().numpy()))
```

앞 두 노트와 같다. 짚어 둘 점은 **`eval()`이 두 가지를 끈다**는 것 — 새 머리의 `Dropout(0.2)`, 그리고 ResNet 몸통 곳곳의 **`BatchNorm2d`**(day22 2-4에서 "또 하나의 모드 스위치 층"이라 적어 둔 것). 배치 정규화는 학습 중엔 그 배치의 평균·분산으로, 평가 중엔 학습 내내 누적한 이동 평균으로 정규화하므로 `eval()`을 빠뜨리면 2,000장 테스트가 하나의 거대한 배치 통계로 계산되어 숫자가 달라진다. 직접 만든 CNN에는 없던 층이 사전학습 모델 안에 들어 있으니, 모드 전환이 이제 "습관"이 아니라 **필수**가 된다.

### 1-5. `torch.save(model.state_dict(), '….pth')` — 가중치만 저장한다

```python
# 7) 모델 가중치 저장 , torch.save( model.state_dict(), '파일명.pth' )
torch.save(model.state_dict(), 'resnet50_custom.pth')
print('가중치 저장 성공')
# 머신러닝 pkl , 딥러닝가중치 pth , 딥러닝모델 onnx => 스프링 또는 파이썬 실행
```

day14 `joblib.dump(model, 'xxx.pkl')`의 파이토치판이다. 다만 저장하는 것이 **모델 객체가 아니라 `state_dict`** — 층 이름을 키로, 가중치 텐서를 값으로 가진 `OrderedDict`다(`'conv1.weight'`, `'fc.0.weight'`, `'fc.3.bias'` …, day22 2-2의 `'0.weight'` 순번 이름이 여기선 `fc.0`처럼 속성 이름 아래로 들어간다).

| 저장 방식 | 코드 | 불러오기 | 특징 |
| --- | --- | --- | --- |
| **가중치만**(권장) | `torch.save(model.state_dict(), 'a.pth')` | 같은 구조를 코드로 다시 만든 뒤 `model.load_state_dict(torch.load('a.pth'))` | 파일이 가볍고 코드 버전이 바뀌어도 안전. 구조 코드가 따로 있어야 한다 |
| 모델 통째 | `torch.save(model, 'a.pth')` | `torch.load('a.pth')` | 간편하지만 pickle이라 클래스 정의·파이토치 버전에 묶인다 |

불러올 때의 관용구는 셋이다 — ① 1-1~1-2와 **똑같이** `resnet50()` + `fc` 교체로 빈 구조를 만들고, ② `load_state_dict(torch.load(path, map_location=device))`로 가중치를 채우고(GPU에서 저장한 것을 CPU에서 열 때 `map_location`이 필요), ③ **`model.eval()`**. 확장자 `.pth`·`.pt`는 관례일 뿐 내용은 같다. 코랩의 `/content/`에 저장했으니 런타임이 끊기면 사라진다 — 드라이브 경로(`/content/drive/MyDrive/…`)에 저장하거나 `files.download`로 내려받아야 한다(day21).

주석 마지막 줄이 이 수업이 향하는 그림이다.

| 형식 | 만드는 쪽 | 담는 것 | 서빙하는 쪽 |
| --- | --- | --- | --- |
| `.pkl` | 사이킷런 `joblib.dump` (day14) | 파이프라인·모델 객체 | 파이썬 FastAPI (day16) |
| **`.pth`** | 파이토치 `torch.save(state_dict)` | 가중치 텐서 | 파이썬 — 구조 코드 + `load_state_dict` |
| `.onnx` | `torch.onnx.export(model, 예시 입력, 'a.onnx')` | **구조 + 가중치**를 프레임워크 중립 그래프로 | 파이썬 ONNX Runtime, **자바·스프링**(ONNX Runtime Java), C#, 브라우저 — 파이토치 없이 추론 |

파이토치 모델을 스프링 서버에서 쓰려면 `.pth`로는 안 되고(파이썬 구조 코드가 필요) **ONNX로 내보내야** 자바가 읽는다 — day16의 "파이썬 FastAPI 서빙"과 나란히 놓이는 두 번째 길이다.

## 2. 추가로 알면 좋은 활용법

### 2-1. 몸통 얼리기와 매개변수 그룹 — 전이학습의 두 가지 수위

```python
# (가) 특성 추출: 몸통은 얼리고 머리만 학습 — 자료가 적을 때, 가장 빠름
for p in model.parameters():
    p.requires_grad = False
model.fc = nn.Sequential(...)             # 새 층은 기본이 requires_grad=True
optimizer = optim.AdamW(model.fc.parameters(), lr=1e-3)

# (나) 차등 학습률: 몸통은 작게, 머리는 크게
optimizer = optim.AdamW([
    {'params': [p for n, p in model.named_parameters() if not n.startswith('fc.')], 'lr': 1e-5},
    {'params': model.fc.parameters(), 'lr': 1e-3},
])
```

수업 코드는 (다) 전체 파인튜닝(몸통도 작은 학습률로 함께)이다. 자료가 수천 장 이하면 (가)가 안전하고, 자료가 넉넉하고 도메인이 이미지넷과 멀면(의료 영상·숫자 사진) (나)·(다)가 더 올라간다. 얼린 매개변수는 `optimizer`에 넘겨도 움직이지 않지만, `requires_grad=False`로 두면 역전파 계산 자체를 건너뛰어 **속도와 메모리**가 크게 준다. 실무에서 흔한 순서는 (가)로 머리를 먼저 맞춘 뒤 (나)로 몸통을 조금 풀어 주는 2단계다.

### 2-2. 이미지넷 전처리에 맞추기 — 사전학습 가중치가 보던 입력대로

```python
from torchvision import transforms
weights = models.ResNet50_Weights.DEFAULT
tf = weights.transforms()                 # Resize 232 → CenterCrop 224 → ToTensor → Normalize(이미지넷 평균·표준편차)
```

사전학습 가중치는 특정 전처리(크기 224 × 224, 채널별 평균 `[0.485, 0.456, 0.406]`·표준편차 `[0.229, 0.224, 0.225]`로 정규화)로 학습됐다. 입력을 같은 분포로 맞춰 주면 몸통이 배운 특징이 그대로 살아난다. `weights.transforms()`가 그 전처리를 통째로 돌려주므로 day23 2-3의 `transform=`에 넣으면 된다. 32 × 32를 224로 키우면 계산이 49배가 되니, 작은 이미지는 `Normalize`만 맞추고 크기는 그대로 두는 절충도 흔하다 — 어느 쪽이든 테스트 정확도로 고른다.

### 2-3. 저장·복원 체크리스트와 체크포인트

```python
ckpt = {'model': model.state_dict(), 'optimizer': optimizer.state_dict(), 'epoch': epoch}
torch.save(ckpt, '/content/drive/MyDrive/svhn_resnet50.pth')
# 복원
ckpt = torch.load(path, map_location=device)
model.load_state_dict(ckpt['model']); optimizer.load_state_dict(ckpt['optimizer'])
```

중간에 끊길 수 있는 코랩에서는 가중치만이 아니라 **옵티마이저 상태와 에포크 번호**까지 묶어 드라이브에 저장해 두면 이어서 학습할 수 있다(AdamW는 1·2차 모멘트를 들고 있어 이것이 없으면 재개 직후 몇 스텝이 흔들린다). 서빙용으로는 `model.state_dict()`만 따로 저장한다. `load_state_dict`가 `Missing key(s)`·`Unexpected key(s)`를 내면 구조 코드가 저장 때와 다르다는 뜻이니 `fc` 교체 코드가 같은지부터 본다.

### 2-4. `torch.onnx.export` — 스프링에서 쓰기 위한 한 줄

```python
model.eval()
dummy = torch.randn(1, 3, 32, 32, device=device)       # 입력 모양 예시
torch.onnx.export(model, dummy, 'svhn_resnet50.onnx',
                  input_names=['input'], output_names=['logits'],
                  dynamic_axes={'input': {0: 'batch'}, 'logits': {0: 'batch'}})
```

예시 입력 한 번을 흘려 보내 계산 그래프를 기록하는 방식이라 `eval()`을 먼저 부르고(드롭아웃·배치 정규화 고정), 배치 축은 `dynamic_axes`로 가변으로 둔다. 자바 쪽은 `com.microsoft.onnxruntime:onnxruntime` 의존성으로 `OrtSession`을 열어 `float[1][3][32][32]`를 넣으면 로짓 10개가 나온다 — 전처리(`/ 255.0`·정규화)는 자바에서 똑같이 해 줘야 한다. 파이썬에서는 `onnxruntime.InferenceSession`으로 같은 파일을 검증할 수 있다.

## 3. 더 나아가 알면 좋은 것

### 3-1. 전이학습이 되는 이유 — 앞 층은 범용, 뒤 층은 과제 특화

CNN의 앞 층 필터는 어떤 자료로 학습해도 비슷한 모서리·색 검출기로 수렴하고, 뒤로 갈수록 학습 자료에 특화된다(Yosinski 외, 2014). 그래서 몸통을 가져오고 머리만 바꾸는 전략이 통하며, 도메인이 멀수록 뒤쪽 층을 더 풀어 줘야 한다. 자연어 쪽의 BERT·GPT 파인튜닝도 같은 원리 — day20에서 "임베딩·BERT는 다음에"라 적어 둔 것이 이 방식으로 이어진다.

### 3-2. 백본 고르기 — 크기·속도·정확도

`torchvision.models`의 선택지와 대략의 자리: `resnet18`(1,100만, 빠름) · `resnet50`(2,560만, 기본값) · `efficientnet_b0`(530만, 정확도 대비 가벼움) · `mobilenet_v3_small`(250만, 모바일·엣지) · `convnext_tiny`(2,800만, 최신 CNN) · `vit_b_16`(8,600만, 트랜스포머). 서빙 환경(스프링 서버 CPU인지, GPU인지, 모바일인지)이 백본을 정하는 첫 기준이다. `timm` 라이브러리는 수백 가지 사전학습 모델을 같은 인터페이스로 준다.

### 3-3. 모델 허브 — 가중치를 공유하는 생태계

`torchvision.models` 밖에도 PyTorch Hub(`torch.hub.load`)와 Hugging Face Hub(`transformers`·`timm`)가 있다. 이미지 분류뿐 아니라 객체 탐지(`fasterrcnn_resnet50_fpn`)·분할(`deeplabv3`)·텍스트·음성 모델까지 같은 "불러서 머리만 바꾸기" 패턴으로 쓴다. 공개 가중치의 라이선스와 학습 자료 출처를 확인하는 것도 실무의 한 단계다.

### 3-4. 다음에 볼 키워드

- `requires_grad=False` 얼리기·`named_parameters`·차등 학습률·점진적 해동
- `ResNet50_Weights.DEFAULT.transforms()`·`Normalize` 이미지넷 통계
- `torch.onnx.export`·ONNX Runtime(파이썬·자바)·`torchscript`
- 체크포인트(`optimizer.state_dict()`·`epoch`)·`map_location`
- `timm`·PyTorch Hub·Hugging Face Hub
- 지식 증류·양자화·가지치기 — 큰 사전학습 모델을 작게
- Grad-CAM — 모델이 이미지의 어디를 보고 판단했는지 시각화

## 실습 파일

- `KDT_2026/2026_Python/day24/dl-4.ipynb` — 마크다운 `### [3] 이미지분류 사전학습 모델 추론` 아래 셀: 앞 셀과 같은 0) `device` → 1) 텐서 변환 + `TensorDataset`·`DataLoader(batch_size=128, shuffle=True)` → 2) **`import torchvision.models as models` → `model = models.resnet50(weights='DEFAULT')` → `in_features = model.fc.in_features` → `model.fc = nn.Sequential(Linear(in_features, 128)·ReLU·Dropout(0.2)·Linear(128, 10))` → `model.to(device)`** → 3) `nn.CrossEntropyLoss()` → 4) **`optim.AdamW(lr=0.0001)`**(주석 "사전학습모델은 학습률 촘촘히") → 5) **`range(5)`** 미니배치 여섯 박자·평균 손실 출력 → 6) `eval()`·`no_grad`·`argmax`·`accuracy_score` → 7) **`torch.save(model.state_dict(), 'resnet50_custom.pth')`** + 주석 "머신러닝 pkl, 딥러닝가중치 pth, 딥러닝모델 onnx => 스프링 또는 파이썬 실행" — 셀 출력은 저장되지 않음

## 관련 노트

[[AI 정리본 인덱스]] · [[AI day24 TensorDataset·DataLoader 미니배치 학습으로 CNN 다시 돌리기]] · [[AI day23 Conv2d·MaxPool2d CNN으로 SVHN 숫자 이미지 분류]] · [[AI day22 nn.Dropout 과적합 방지와 성적 회귀 신경망 뼈대]] · [[AI day14 KFold 교차 검증과 GridSearchCV 하이퍼파라미터 탐색]] · [[KDT_2026 학습 지도]]
