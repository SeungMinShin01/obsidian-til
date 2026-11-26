---
출처: Claude 분석
원본: KDT_2026/2026_Python/day24/dl-4.ipynb(0~1셀 — SVHN CNN에 미니배치 추가)
작성일: 2026-11-26
tags: [학습, ai, python]
---

# AI day24 — TensorDataset·DataLoader 미니배치 학습으로 CNN 다시 돌리기

> 실습 파일: `day24/dl-4.ipynb` (셀 0 — SVHN 내려받기 · 셀 1 — day23 CNN 코드에 `##### 미니 배치 #####` 블록 둘이 끼어든 판; 셀 출력은 노트북에 저장돼 있지 않다)
> 허브: [[AI 정리본 인덱스]] · 이전: [[AI day23 Conv2d·MaxPool2d CNN으로 SVHN 숫자 이미지 분류]] · 다음: [[AI day24 resnet50 사전학습 모델 전이학습과 state_dict 저장]]

day23 `dl-3.ipynb`를 통째로 복사한 뒤 `#####` 로 울타리를 친 두 블록만 끼워 넣은 파일이다. 하나는 텐서 변환 뒤에 **`TensorDataset` + `DataLoader`** 로 자료를 128장씩 묶는 설정, 다른 하나는 학습 루프 안에서 **배치마다** 순전파 → 손실 → 역전파 → 갱신을 도는 안쪽 `for`다. 모델·손실·옵티마이저·평가는 글자 하나 안 바뀌었다. day21 2-4 표와 day22 2-3에 "다음에"라고 적어 둔 **미니배치 경사하강법**이 드디어 코드가 된 날이라, 바뀐 두 블록이 무엇을 바꾸는지(갱신 횟수·메모리·손실 집계)만 집중해서 정리한다.

## 1. 배운 내용

### 1-1. `TensorDataset` — 특성과 정답을 1 : 1로 묶는다

```python
################## 미니 배치 설정 #########################
from torch.utils.data import TensorDataset, DataLoader
# 1- 특성과 정답 1:1 매핑하여 묶음
train_dataset = TensorDataset(X_train, Y_train)
```

`X_train`은 `(20000, 3, 32, 32)`, `Y_train`은 `(20000,)`. 둘을 따로 들고 섞으면 몇 번째 사진이 몇 번째 라벨인지 어긋날 수 있다. `TensorDataset`은 같은 길이의 텐서들을 받아 **`train_dataset[i]`가 `(X_train[i], Y_train[i])` 한 쌍**을 돌려주는 객체로 묶는다. 길이가 다르면 만들 때 바로 오류가 난다.

| 항목 | 내용 |
| --- | --- |
| 역할 | 색인 하나로 (입력, 정답) 쌍을 꺼내는 자료 묶음 — `__len__`·`__getitem__`만 있는 단순한 `Dataset` |
| 받는 것 | 길이(0번 축)가 같은 텐서 아무 개수 |
| 쓰임 | 이미 텐서로 만들어 둔 자료를 `DataLoader`에 넘길 때. 파일에서 한 장씩 읽어야 하면 `Dataset`을 직접 상속한다(2-3) |
| 주의 | 여기선 `X_train`이 이미 GPU에 있다 — 묶음도 GPU 텐서를 가리킬 뿐 복사하지 않는다 |

### 1-2. `DataLoader` — 배치 크기로 자르고 섞어서 내준다

```python
# 2- 묶은 데이터셋을 지정한 배치 크기 단위로 자르고 랜덤으로 병렬 로딩
train_loader = DataLoader(dataset=train_dataset, batch_size=128, shuffle=True)
```

`DataLoader`는 데이터셋을 **반복 가능한 객체**로 감싼다. `for bach_X, bach_Y in train_loader:` 한 바퀴가 128장짜리 묶음 하나다.

| 인자 | 이 코드 | 뜻 |
| --- | --- | --- |
| `dataset` | `train_dataset` | 1-1에서 묶은 것 |
| `batch_size` | 128 | 한 번에 꺼내는 장수. 2만 장 ÷ 128 = 156.25 → **157묶음**(마지막은 32장) |
| `shuffle` | `True` | **에포크마다** 순서를 새로 섞는다 — 같은 묶음이 매번 같은 조합이면 묶음 순서를 외우는 편향이 생긴다. 테스트용에는 `False` |
| `drop_last` | (기본 False) | 마지막 자투리 묶음을 버릴지 |
| `num_workers` | (기본 0) | 주석의 "병렬 로딩" — 디스크에서 읽는 데이터셋이면 워커 프로세스로 미리 읽어 둔다. GPU에 이미 올린 텐서라면 0이 맞다 |

`len(train_loader)`는 **묶음 수**(157)이고 `len(train_dataset)`이 장수(20,000)라는 구분이 1-3의 평균 손실 계산에서 쓰인다. 128은 2의 거듭제곱 관례(GPU 메모리 정렬)이고 32·64·256도 흔하다.

### 1-3. 학습 루프 — 에포크 안에 배치 `for`가 하나 더 들어간다

```python
# 5) 에포크(학습수) 단위 학습( 순전파 -> 오차계산 -> 역전파 -> 업데이트 )
for epoch in range(100):
    model.train()                                # 1- 학습모드
    ################## 미니 배치 단위 학습 #########################
    total_loss = 0.0
    for bach_X, bach_Y in train_loader:          # 157묶음
        optimizer.zero_grad()                    # 2- 이전기울기 초기화
        logits = model(bach_X)                   # 3- 순전파 (128, 10)
        loss = criterion(logits, bach_Y)         # 4- 오차
        loss.backward()                          # 5- 역전파
        optimizer.step()                         # 6- 가중치/편향 업데이트
        total_loss += loss.item()
    total_loss = total_loss / len(train_loader)  # 평균 오차
    #################################################################
    if epoch % 10 == 0:
        print(epoch, ": loss: ", total_loss)
```

day23의 여섯 박자 중 2)~6)이 **안쪽 `for`로 들어갔다.** `model.train()`만 에포크 머리에 남고, `zero_grad → 순전파 → 손실 → backward → step`은 묶음마다 반복된다. 그래서 갱신 횟수가 달라진다.

| | day23 (배치 경사하강법) | day24 (미니배치) |
| --- | --- | --- |
| 한 번 순전파하는 장수 | 20,000 | 128 |
| 에포크당 갱신 | **1번** | **157번** |
| 100 에포크 갱신 | 100번 | **15,700번** |
| 기울기 | 전체 평균 — 정확하지만 한 걸음에 비싸다 | 128장 표본 평균 — 조금 거칠지만 157걸음 |
| 활성화 메모리 | 2만 장어치 특성 맵을 한 번에 들고 있어야 한다 | 128장어치만 — 7만 장 전부를 써도 터지지 않는다 |
| 손실 출력 | 마지막 순전파의 `loss.item()` | 157묶음 손실의 **평균** |

day23에서 "처음 30바퀴 동안 거의 안 움직였다"가 이 차이로 설명된다 — 그때는 30바퀴가 갱신 30번이었고, 오늘은 에포크 하나에 157번 갱신하니 첫 에포크가 끝나기 전에 그 구간을 지나간다. 같은 100 에포크를 돌려도 훨씬 멀리 가고, 그래서 미니배치가 딥러닝 학습의 **기본값**이다. 다만 묶음 하나의 기울기는 전체보다 흔들리므로(확률적) 손실이 매끈하게만 내려가지는 않는다 — 그 흔들림이 날카로운 최솟값을 피하게 돕는다는 것이 통설이기도 하다.

`total_loss`를 `len(train_loader)`로 나눠 **묶음 평균**을 찍는 것은 에포크 안의 157개 손실이 전부 다른 묶음에서 나온 값이기 때문이다. 한 값만 찍으면 그 묶음이 쉬웠는지 어려웠는지에 따라 들쭉날쭉하다. `loss.item()`으로 파이썬 숫자로 바꿔 더하는 것도 중요하다 — 텐서 그대로 더하면 157개 계산 그래프가 메모리에 붙잡힌다(day21 2-1).

### 1-4. 평가는 그대로 — 테스트 2,000장은 한 번에

```python
model.eval()
with torch.no_grad():
    test_logits = model(X_test)                    # 2,000장 한 번에
    test_pred = torch.argmax(test_logits, dim=1)
from sklearn.metrics import accuracy_score
print(accuracy_score(Y_test.cpu().numpy(), test_pred.cpu().numpy()))
```

평가는 기울기를 안 만드니 메모리가 가벼워 2,000장을 한 번에 넣는다. 테스트가 수만 장이면 여기도 `DataLoader(shuffle=False)`로 묶어 예측을 `torch.cat`으로 이어 붙인다(2-1). 셀 출력이 노트북에 저장돼 있지 않아 이 파일의 정확도 숫자는 남아 있지 않지만, 같은 모델·같은 에포크에서 갱신이 157배 많아졌으니 day23의 0.7585보다 손실은 훨씬 낮게 내려가고 테스트 정확도도 올라가는 것이 보통이다 — 다만 갱신이 많아진 만큼 학습 자료를 외우기도 쉬워져, 학습 손실만 보지 말고 테스트 점수와 **격차**를 함께 봐야 한다.

## 2. 추가로 알면 좋은 활용법

### 2-1. 테스트도 `DataLoader`로 — 큰 자료의 평가 관용구

```python
test_loader = DataLoader(TensorDataset(X_test, Y_test), batch_size=512, shuffle=False)
model.eval(); preds = []
with torch.no_grad():
    for bx, _ in test_loader:
        preds.append(torch.argmax(model(bx), dim=1))
test_pred = torch.cat(preds)              # (2000,)
```

`shuffle=False`라 순서가 보존되니 `Y_test`와 그대로 짝이 맞는다. 평가는 역전파가 없어 학습보다 큰 배치를 써도 된다.

### 2-2. 에포크마다 검증 정확도 같이 찍기 — 조기 종료의 재료

```python
history = []
for epoch in range(100):
    model.train(); total_loss = 0.0
    for bx, by in train_loader:
        ...                                        # 1-3과 동일
    model.eval()
    with torch.no_grad():
        acc = (torch.argmax(model(X_test), dim=1) == Y_test).float().mean().item()
    history.append((total_loss / len(train_loader), acc))
```

학습 손실은 내려가는데 검증 정확도가 멈추거나 내려가기 시작하는 지점이 과대적합의 시작이다(day18 `early_stopping`·day22 2-2). `history`를 `plt.plot`으로 그리면 두 곡선이 갈라지는 자리가 보인다. 가장 좋았던 에포크의 `state_dict`를 `copy.deepcopy`로 들고 있다가 끝나고 `load_state_dict`로 되돌리면 조기 종료가 된다.

### 2-3. 자료를 GPU에 다 못 올릴 때 — 배치마다 `.to(device)`

```python
X_cpu = torch.tensor(raw_train.data, dtype=torch.float32) / 255.0      # 7만 장, CPU에 둔다
loader = DataLoader(TensorDataset(X_cpu, torch.tensor(raw_train.labels)), batch_size=128,
                    shuffle=True, num_workers=2, pin_memory=True)
for bx, by in loader:
    bx, by = bx.to(device), by.to(device)        # 묶음 단위로만 GPU로
    ...
```

오늘 코드는 2만 장을 미리 GPU에 올려 두었는데, 7만 장 전부나 더 큰 이미지면 GPU 메모리에 안 들어간다. 그때는 자료를 CPU에 두고 **묶음을 꺼낼 때마다** 옮긴다. `num_workers`로 다음 묶음을 미리 준비시키고 `pin_memory=True`로 전송을 빠르게 하는 것이 이 방식의 짝이다. 이미지가 파일로 흩어져 있으면 `Dataset`을 상속해 `__getitem__`에서 한 장을 읽어 `transform`을 적용하게 만들고, 폴더가 클래스별로 나뉘어 있으면 `datasets.ImageFolder('경로', transform=tf)` 한 줄로 끝난다.

### 2-4. 배치 크기와 학습률 — 같이 움직이는 짝

배치를 키우면 기울기가 덜 흔들리므로 학습률을 키울 여지가 생기고(선형 스케일링 규칙), 배치를 줄이면 학습률도 낮추는 편이 안전하다. 128에 0.005가 잘 돌아갔다면 512로 올릴 때 0.01~0.02까지 시도해 볼 수 있다. 배치가 아주 크면 갱신 횟수가 줄어 일반화가 나빠진다는 보고도 있어, 32~256 사이가 실무의 흔한 출발점이다. 메모리가 부족하면 작은 배치로 여러 번 `backward()`한 뒤 한 번 `step()`하는 **기울기 누적**으로 큰 배치를 흉내 낸다 — day21의 "기울기는 누적된다"가 의도적으로 쓰이는 자리다.

## 3. 더 나아가 알면 좋은 것

### 3-1. 배치·확률적·미니배치 — 세 경사하강법의 자리

| 방식 | 한 걸음에 쓰는 자료 | 장점 | 단점 |
| --- | --- | --- | --- |
| 배치(day21~23) | 전부 | 기울기 정확·구현 단순 | 느리고 메모리 큼, 지역 최솟값에 갇히기 쉬움 |
| 확률적(SGD, 1장) | 1 | 빠른 갱신·탈출 쉬움 | 너무 흔들림, GPU 병렬 못 씀 |
| **미니배치**(오늘) | 32~512 | 둘의 절충 — GPU 행렬 곱을 꽉 채우며 자주 갱신 | 배치 크기·학습률이 하이퍼파라미터로 추가 |

`optim.SGD`라는 이름이 붙어 있어도 실제로는 거의 항상 미니배치로 쓴다. 에포크(전체 한 바퀴)와 스텝(갱신 한 번)을 구분하는 습관이 여기서 생긴다 — 논문·문서의 "10k steps"는 에포크가 아니다.

### 3-2. `Sampler`·불균형 자료·`collate_fn`

`DataLoader`는 섞는 방법도 바꿀 수 있다. 클래스가 치우쳐 있으면 `WeightedRandomSampler`로 적은 클래스를 더 자주 뽑고(day17 `class_weight`의 로더판), 길이가 제각각인 문장 자료는 `collate_fn`으로 묶음 안에서 패딩을 맞춘다. 검증 세트를 떼어 낼 때는 `torch.utils.data.random_split(dataset, [0.8, 0.2])`가 편하다.

### 3-3. 학습률 스케줄러 — 스텝 수가 많아진 뒤의 다음 손잡이

갱신이 1만 번을 넘으면 학습률을 고정하는 것보다 줄여 가는 쪽이 보통 낫다. `optim.lr_scheduler.StepLR`(몇 에포크마다 곱하기), `CosineAnnealingLR`(코사인 곡선으로 0까지), `OneCycleLR`(올렸다 내리기), `ReduceLROnPlateau`(검증 손실이 멈추면 낮추기) 중 하나를 `optimizer.step()` 뒤에 `scheduler.step()`으로 붙인다.

### 3-4. 다음에 볼 키워드

- `torchvision.models.resnet50` 전이학습 — 같은 로더를 그대로 쓰며 모델만 교체 (다음 노트)
- `Dataset` 상속·`ImageFolder`·`transforms` 증강
- `random_split`·`WeightedRandomSampler`·`collate_fn`
- `pin_memory`·`num_workers`·`persistent_workers` — 입력 파이프라인 속도
- 기울기 누적·`torch.cuda.amp` 혼합 정밀도 — 메모리와 속도
- `tqdm(train_loader)` 진행 막대
- 학습률 스케줄러·웜업

## 실습 파일

- `KDT_2026/2026_Python/day24/dl-4.ipynb` — 셀 0: `datasets.SVHN(root='./data', split='train'/'test', download=True)` · 셀 1: day23과 같은 0) `device` → 1) 텐서 변환(2만 장·2,000장, `/ 255.0`, `long` 라벨, `.to(device)`) → **`from torch.utils.data import TensorDataset, DataLoader` → `TensorDataset(X_train, Y_train)` → `DataLoader(dataset=…, batch_size=128, shuffle=True)`** → 2) 같은 CNN `nn.Sequential` → 3) `nn.CrossEntropyLoss()` → 4) `optim.AdamW(lr=0.005)` → 5) `range(100)` 안에 **`for bach_X, bach_Y in train_loader:` 여섯 박자 + `total_loss += loss.item()` → `/ len(train_loader)` 평균**, 10바퀴마다 출력 → 6) `eval()`·`no_grad`·`argmax`·`accuracy_score(.cpu().numpy())` — 셀 출력은 저장되지 않음

## 관련 노트

[[AI 정리본 인덱스]] · [[AI day23 Conv2d·MaxPool2d CNN으로 SVHN 숫자 이미지 분류]] · [[AI day24 resnet50 사전학습 모델 전이학습과 state_dict 저장]] · [[AI day21 MSELoss 손실·backward 역전파와 경사하강법 한 걸음 갱신]] · [[AI day18 LightGBM 매개변수 설정과 early_stopping 조기 종료]] · [[KDT_2026 학습 지도]]
