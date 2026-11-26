---
출처: Claude 분석
원본: KDT_2026/2026_Python/ML_practice/주제.ipynb
작성일: 2026-11-26
tags: [학습, ai, python]
---

# AI day21 — Hugging Face datasets로 LBox 판결문 데이터셋 불러오기

> 실습 파일: `ML_practice/주제.ipynb` (코랩에서 실행한 두 셀 — `load_dataset` → `DatasetDict` 확인 → `to_pandas()`)
> 허브: [[AI 정리본 인덱스]] · 이전: [[AI day21 MSELoss 손실·backward 역전파와 경사하강법 한 걸음 갱신]] · 다음: [[AI day22 nn.Sequential 와인 이진 분류와 BCEWithLogitsLoss·AdamW 학습 루프]]

`ML_practice` 폴더에 수업 연습문제(`practiceN.py`)와는 결이 다른 파일이 하나 들어왔다. 이름이 **`주제`** — 프로젝트에서 다룰 자료를 미리 열어 보는 탐색용 노트북이다. 코랩(파이썬 3.13)에서 두 셀만 돌렸다. 내용은 짧지만 새로 등장한 도구가 하나 있다 — 지금까지 자료는 `read_csv(url)`·`sns.load_dataset`·`datasets.SVHN`으로 받았는데, 이번엔 **Hugging Face `datasets` 라이브러리**로 공개 데이터셋을 이름만으로 내려받는다. 자료는 **LBox Open** 중 **형사 판결 예측(`ljp_criminal`)** 서브셋이고, 사실관계 텍스트로 선고 형량을 맞히는 한국어 법률 NLP 과제다. 불러오는 법과 자료 모양만 간단히 정리해 둔다.

## 1. 배운 내용

### 1-1. `load_dataset("저장소", "구성")` — 허브에서 이름으로 받는다

```python
from datasets import load_dataset
data_ljp_criminal = load_dataset("lbox/lbox_open", "ljp_criminal")
```

```
Warning: You are sending unauthenticated requests to the HF Hub. Please set a HF_TOKEN ...
Generating train split: 0/8400 … valid 0/1050 … test 0/1050 … test2 0/928
```

| 인자 | 값 | 뜻 |
| --- | --- | --- |
| 첫째 | `"lbox/lbox_open"` | 허브 저장소 — `조직/데이터셋` 꼴. 로펌 엘박스가 공개한 한국어 법률 AI 벤치마크 모음 |
| 둘째 | `"ljp_criminal"` | 그 저장소 안의 **구성(config)** 이름. `lbox_open`에는 사건명 분류(`casename_classification`)·법령 분류(`statute_classification`)·형사 판결 예측(`ljp_criminal`)·민사 판결 예측(`ljp_civil`)·판결 요약(`summarization`) 등이 들어 있고 그중 하나를 고른다 |

`pip install datasets`는 코랩에 이미 깔려 있어 생략됐다. 첫 호출에 `README.md`와 분할별 파일(학습 18 MB 등)을 내려받아 `~/.cache/huggingface/`에 캐시하고, 다음부터는 캐시를 읽는다. 경고문의 `HF_TOKEN`은 허브 계정 토큰 — 없어도 공개 자료는 받아지지만 속도 제한이 있다는 안내다(토큰 값을 노트북에 적지 않고 코랩 보안 비밀이나 환경 변수로 두는 것이 원칙).

### 1-2. `DatasetDict` — 분할이 이미 나뉘어 온다

```python
print(data_ljp_criminal)
```

```
DatasetDict({
    train: Dataset({ features: ['id', 'casetype', 'casename', 'facts', 'label', 'ruling', 'reason'], num_rows: 8400 })
    valid: Dataset({ … num_rows: 1050 })
    test:  Dataset({ … num_rows: 1050 })
    test2: Dataset({ … num_rows: 928 })
})
```

`read_csv`가 데이터프레임 하나를 주던 것과 달리, `load_dataset`은 **분할(split)별 `Dataset`을 딕셔너리처럼 묶은 `DatasetDict`** 를 준다. day12부터 늘 `train_test_split`으로 직접 나누던 일을 자료 제공자가 미리 해 둔 것이다 — 벤치마크라 누구나 같은 분할로 비교하기 위해서다. 학습 8,400 · 검증 1,050 · 테스트 1,050에 `test2` 928건이 하나 더 있다(추가 테스트 분할).

| 열 | 내용 |
| --- | --- |
| `id` | 번호 |
| `casetype` | `criminal` — 이 구성은 전부 형사 |
| `casename` | 사건명(죄명) — 머리 다섯 줄은 전부 `강제추행` |
| `facts` | **범죄 사실 텍스트** — 모델의 입력 X가 될 열 |
| `label` | **딕셔너리** — `text`(`'징역 6월'`·`'벌금 5000000원'` 같은 선고 문장)와 `fine_lv`·`imprisonment_with_labor_lv`·`imprisonment_without_labor_lv` 같은 **등급 숫자**(벌금·징역·금고를 구간으로 나눈 0~N) |
| `ruling` | 주문 |
| `reason` | 양형 이유 |

### 1-3. `to_pandas()` — 익숙한 판다스로 넘겨서 보기

```python
import pandas as pd
df = data_ljp_criminal['train'].to_pandas()   # 판다스로 변환
print(df.shape)       # (8400, 7)
print(df.columns)     # Index(['id', 'casetype', 'casename', 'facts', 'label', 'ruling', 'reason'])
print(df.head())
```

`DatasetDict['train']`으로 분할 하나를 꺼내고 **`.to_pandas()`** 로 데이터프레임을 만들면, 그다음은 day08~11에서 하던 `shape`·`columns`·`head()`·`value_counts()` 그대로다. `Dataset` 자체도 `ds[0]`(행 딕셔너리)·`ds['facts'][:3]`(열)·`ds.filter(...)`·`ds.map(...)`으로 다룰 수 있지만, 탐색 단계에서는 판다스로 넘기는 것이 가장 빠르다. `label` 열은 딕셔너리가 셀마다 들어 있는 `object` 열이라, 쓰려면 `df['label'].apply(lambda d: d['fine_lv'])`처럼 **꺼내서 새 열**로 만들어야 한다.

## 2. 추가로 알면 좋은 활용법

### 2-1. 타깃 정하기 — `label` 딕셔너리를 열로 펴기

```python
lab = pd.json_normalize(df['label'])             # text, fine_lv, imprisonment_with_labor_lv, ...
df = pd.concat([df.drop(columns='label'), lab], axis=1)
print(df['casename'].value_counts().head(10))
print(df['imprisonment_with_labor_lv'].value_counts().sort_index())
```

형량 예측은 보통 **등급 분류**(징역 구간 0~N을 맞히기 — day15 다중 분류·`classification_report`)로 푼다. `text`를 파싱해 개월 수 회귀로 가는 길도 있다. 클래스가 치우쳐 있을 가능성이 크니 `value_counts`부터 보고 `stratify`·`class_weight`(day17)를 생각해 둔다.

### 2-2. 텍스트 X — day20의 파이프라인을 그대로 올려 보기

`facts`는 한국어 문장이라 day20의 흐름(`re.sub` 정리 → Kiwi 토큰화 → `TfidfVectorizer` → `LogisticRegression`)을 그대로 얹어 **기준선**을 만들 수 있다. 법률 문장은 리뷰보다 길고 어휘가 정형적이라(피고인은 … 하였다) `max_features`·`ngram_range=(1, 2)`가 효과를 보는 편이다. 기준선이 서면 그다음이 사전학습 언어 모델(KoBERT·KLUE-RoBERTa) 파인튜닝 — day24의 `resnet50` 머리 교체와 같은 패턴을 텍스트에서 하는 것이다.

### 2-3. 분할 쓰는 법 — `valid`는 튜닝, `test`는 마지막 한 번

제공된 네 분할을 역할대로 쓰면 day14의 교차 검증이 필요 없다. `train`으로 학습, `valid`로 하이퍼파라미터·조기 종료, `test`는 **마지막에 한 번만**. `test2`는 별도의 추가 시험지로 두어 일반화를 한 번 더 잰다. 허브 자료는 `load_dataset(..., split='train[:1000]')`처럼 일부만 받아 빠르게 실험할 수도 있다.

### 2-4. 캐시와 저장

`ds.save_to_disk('/content/drive/MyDrive/lbox_ljp')` → `load_from_disk(...)`로 드라이브에 두면 런타임이 끊겨도 다시 받지 않는다(day21 코랩 경로). 판다스로 바꾼 뒤 `to_parquet`으로 저장하는 것도 좋다 — CSV보다 작고 딕셔너리 열도 보존된다.

## 3. 더 나아가 알면 좋은 것

### 3-1. Hugging Face 허브 — 자료·모델·토크나이저가 한곳에

`datasets`(자료)·`transformers`(모델·토크나이저)·`tokenizers`·`evaluate`(지표)·`huggingface_hub`가 한 생태계다. `load_dataset`으로 받은 `Dataset`은 `.map(tokenize)`로 토큰화해 `Trainer`에 바로 넣을 수 있게 설계돼 있어, 사이킷런 파이프라인의 NLP판이라 보면 된다. 자료 카드(README)에 라이선스·출처·분할 기준이 적혀 있으니 프로젝트에 쓰기 전에 읽어 둔다.

### 3-2. 법률 판결 예측(LJP)이라는 과제

사실관계 → 죄명·적용 법조·형량을 맞히는 과제로, 중국 CAIL, 유럽 ECHR 등 벤치마크가 있고 LBox Open은 한국어 첫 공개 벤치마크다(2022). 형량은 양형 기준·전과·합의 여부 등 텍스트 밖 변수에 크게 좌우되어 정확도 상한이 낮고, 예측 결과를 어디에 쓰는지에 대한 윤리·공정성 논의(편향 재생산)가 항상 따라붙는 분야라는 점도 함께 적어 둔다.

### 3-3. 다음에 볼 키워드

- `Dataset.map`·`filter`·`train_test_split`·`select`·`shuffle(seed)`
- `pd.json_normalize` — 딕셔너리 열 펴기
- `transformers` `AutoTokenizer`·`AutoModelForSequenceClassification`·`Trainer`
- KoBERT·KLUE-RoBERTa·KoELECTRA — 한국어 사전학습 언어 모델
- 긴 문서 처리(512 토큰 제한)·계층적 분류
- 불균형 다중 분류 지표 — macro F1·가중 F1

## 실습 파일

- `KDT_2026/2026_Python/ML_practice/주제.ipynb` — 셀 0: `from datasets import load_dataset` → `load_dataset("lbox/lbox_open", "ljp_criminal")`(비인증 경고·분할 네 개 생성) · 셀 1: `print(DatasetDict)`(train 8,400 · valid 1,050 · test 1,050 · test2 928, 열 7개) → `['train'].to_pandas()` → `shape` `(8400, 7)`·`columns`·`head()`(`casename` 강제추행, `label` 딕셔너리 `text`·`fine_lv`·…)

## 관련 노트

[[AI 정리본 인덱스]] · [[AI day21 MSELoss 손실·backward 역전파와 경사하강법 한 걸음 갱신]] · [[AI day22 nn.Sequential 와인 이진 분류와 BCEWithLogitsLoss·AdamW 학습 루프]] · [[AI day20 Kiwi 형태소 분석과 TF-IDF로 네이버 쇼핑 리뷰 감성 분류]] · [[KDT_2026 학습 지도]]
