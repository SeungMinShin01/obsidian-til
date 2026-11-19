---
출처: Claude 분석
원본: KDT_2026/2026_Python/day20/s-14.ipynb
작성일: 2026-11-19
tags: [학습, ai, python]
---

# AI day20 — Kiwi 형태소 분석과 TF-IDF로 네이버 쇼핑 리뷰 감성 분류

> 실습 파일: `day20/s-14.ipynb`
> 허브: [[AI 정리본 인덱스]] · 이전: [[AI day19 KMeans·PCA 통신사 고객 등급화 연습문제 풀이]] · 다음: [[AI day20 NSMC 영화 리뷰 감성 분석 연습문제 풀이]]

day12부터 지금까지 모델에 넣은 X는 전부 **숫자**였다 — 물고기 길이, 와인 성분, 학생 성적, 고객 요금. 이번 수업은 처음으로 X가 **문장**이다. 네이버 쇼핑 리뷰 20만 건에서 5,000건을 뽑아 "이 리뷰는 긍정인가 부정인가"를 맞히는 **감성 분석(sentiment analysis)**인데, 문장은 그대로 `fit`에 넣을 수 없으니 수업의 무게는 모델이 아니라 **문장을 숫자 행렬로 바꾸는 전처리**에 실린다. 정규표현식으로 특수문자를 걷어내고(1단계), 한국어 형태소 분석기 **Kiwi**로 문장을 단어 조각으로 쪼개고(2~5단계), `TfidfVectorizer`로 "문장 × 단어" **희소 행렬**을 만든 뒤(6~7단계), 그 위에 day14부터 써 온 `LogisticRegression`을 그대로 올린다(8단계). 모델은 익숙한 것이고 새로운 것은 그 앞의 세 단계다. 수업 파일이 `.py`가 아니라 **주피터 노트북(`.ipynb`)**이라 셀마다 출력이 함께 저장돼 있고, 이 노트의 숫자는 그 출력과 이 노트에서 다시 돌린 값(kiwipiepy 0.24 · scikit-learn 1.9)이다 — `random_state=42`가 전부 고정돼 있어 소수 열넷째 자리까지 같다.

## 1. 배운 내용

### 1-1. 자료 준비 — `read_table`로 URL의 탭 구분 텍스트 읽기, 평점 3 제외, `label` 만들기

```python
!pip install kiwipiepy          # 노트북 셀에서 !로 셸 명령

import pandas as pd
url = "https://raw.githubusercontent.com/bab2min/corpus/master/sentiment/naver_shopping.txt"
df = pd.read_table(url, names=['rating', 'review'])   # rating: 평점, review: 리뷰
df = df[df['rating'] != 3]                             # 평점 3 제외
df['label'] = (df['rating'] >= 4).astype(int)          # 4·5 → 1(긍정), 1·2 → 0(부정)
df_sample = df.sample(n=5000, random_state=42).reset_index(drop=True)
print(df_sample.shape)                                 # (5000, 3)
```

자료는 Kiwi를 만든 bab2min의 깃허브에 올라 있는 **네이버 쇼핑 리뷰 20만 건**이다. `.txt`이지만 "평점 ⇥ 리뷰" 두 칸이 **탭**으로 나뉜 표라 `read_csv`가 아니라 `read_table`(= `read_csv(sep='\t')`)로 읽고, 헤더 줄이 없어 `names=`로 열 이름을 준다. day11의 httpx·day19의 `read_csv(url)`처럼 URL을 바로 넘기면 판다스가 내려받는다.

| 단계 | 하는 일 | 결과 |
| --- | --- | --- |
| `read_table` | 20만 행 × 2열 | 평점 분포 1: 36,048 · 2: 63,989 · 4: 18,786 · **5: 81,177** |
| `rating != 3` | 중립 평점 제외 | 평점 3이 자료에 **원래 없다** — 그대로 20만 행 |
| `(rating >= 4).astype(int)` | 불리언 → 0/1 타깃 | 긍정 99,963 · 부정 100,037 — 거의 **반반** |
| `sample(n=5000, random_state=42)` | 무작위 5,000건 | 긍정 2,487 · 부정 2,513 |

세 가지를 적어 둔다. 첫째, `(df['rating'] >= 4)`는 `True/False` Series인데 `.astype(int)`를 붙여 **1/0 정수 열**로 만든다 — 분류 타깃은 숫자여야 `f1_score`가 바로 먹는다. 둘째, `.sample(n=5000)`은 20만 건 전부를 Kiwi로 쪼개면 시간이 오래 걸리기 때문이고, 뽑은 뒤 `reset_index(drop=True)`로 인덱스를 0~4999로 다시 매긴다 — 뒤에서 `.iloc[0]`과 `df_sample['cleaned_review'] = cleaned_list`(리스트 길이로 붙이기)가 어긋나지 않게 하는 습관이다. 셋째, 평점 3을 빼는 줄은 이 자료에서 아무 행도 지우지 않지만, 평점 3이 섞여 있는 다른 자료라면 "애매한 리뷰를 학습에서 뺀다"는 뜻이 있다 — 9단계의 0.4~0.6 **중립** 판정과 짝이 되는 설계다.

### 1-2. 1단계 — 정규표현식 `re.sub`로 한글·영문·숫자·공백만 남기기

```python
import re
cleaned_list = []
for text in df_sample['review']:
    text = re.sub(r'[^가-힣a-zA-Z0-9\s]', ' ', str(text))   # 패턴에 안 맞는 글자 → 공백
    cleaned_text = ' '.join(text.split())                   # 연속 공백 → 하나
    cleaned_list.append(cleaned_text)
df_sample['cleaned_review'] = cleaned_list
```

`re.sub(패턴, 치환문자, 문자열)`은 패턴에 맞는 부분을 모두 바꾼다. 패턴 `[^가-힣a-zA-Z0-9\s]`를 글자 단위로 읽으면 이렇다.

| 조각 | 뜻 |
| --- | --- |
| `[ ... ]` | 글자 집합 중 하나 |
| `^` (대괄호 안 맨 앞) | **부정** — 집합에 없는 글자 |
| `가-힣` | 완성형 한글 음절 전체(유니코드 AC00~D7A3) |
| `a-zA-Z0-9` | 영문 대소문자와 숫자 |
| `\s` | 공백·탭·줄바꿈 |

그러니까 "한글·영문·숫자·공백이 **아닌** 글자" — `...`, `!`, `~~`, `ㅋㅋ`(자모만 있는 글자는 `가-힣` 범위 밖), 이모티콘 — 를 전부 공백 한 칸으로 바꾼다. 그러면 `안좋아요...실밥도` 처럼 붙어 있던 자리에 공백이 여러 개 생기는데, `text.split()`(인자 없는 `split`은 공백 묶음 기준으로 쪼개고 빈 조각을 버린다)으로 단어 리스트를 만든 뒤 `' '.join(...)`으로 공백 하나씩 끼워 다시 붙이면 **공백이 정규화**된다. 수업 주석의 `'대한 민국' → ['대한', '민국'] → '대한 민국'`이 그 두 줄의 왕복이다. `str(text)`로 감싸는 것은 리뷰가 `NaN`(float)으로 들어와도 `re.sub`가 터지지 않게 하는 안전장치다 — 이 자료에는 결측이 없지만 연습문제의 영화 리뷰 자료에는 있다.

```
0  마감이 안좋아요...실밥도 많고 바느질도 부족한 부분이 몇군데 있네요...교환받기 ...
→  마감이 안좋아요 실밥도 많고 바느질도 부족한 부분이 몇군데 있네요 교환받기 귀찮아서 그냥 씁니다
```

수업 주석이 "리액트/JS 입력 유효성검사"와 견준 것처럼, 정규표현식 자체는 언어가 달라도 같은 문법이다 — 차이는 쓰는 자리가 **입력을 거르는 것**(프론트)에서 **학습 자료를 씻는 것**(텍스트 마이닝)으로 옮겨 왔다는 점이다. 리뷰 한 건 평균 39글자이고, 정제 뒤 빈 문자열이 된 리뷰는 0건이다.

### 1-3. 2~3단계 — `Kiwi()` 형태소 분석기와 `add_user_word`로 사전에 없는 말 등록

```python
from kiwipiepy import Kiwi
kiwi = Kiwi()
for word in ['가성비', '내돈내산', '총알배송']:
    kiwi.add_user_word(word, 'NNG')          # (단어, 품사 태그)
```

**형태소 분석**은 문장을 뜻을 가진 가장 작은 단위로 쪼개고 각 조각에 **품사 태그**를 붙이는 일이다. 영어는 공백으로 나누면 대충 단어가 되지만, 한국어는 `좋아요`·`좋고`·`좋네요`가 모두 "좋다"인데 공백 기준으로는 세 개의 다른 단어가 된다 — 조사·어미가 붙어 변하는 말이라 형태소 분석기가 필수다. Kiwi(`kiwipiepy`)는 C++로 짜인 한국어 형태소 분석기의 파이썬 포장으로, `pip install kiwipiepy` 한 줄로 설치되고 자바가 필요 없다(KoNLPy 계열은 JVM이 필요하다).

`kiwi.tokenize(문장)`의 결과를 직접 보면 이렇다 — 첫 리뷰의 앞부분이다.

```
마감/NNG 이/JKS 안/MAG 좋/VA 어요/EF 실/NNG 밥/NNG 도/JX 많/VA 고/EC 바느질/NNG 도/JX
부족/NNG 하/XSA ㄴ/ETM 부분/NNG 이/JKS 몇/MM 군데/NNB 있/VA 네요/EF 교환/NNG 받/VV-R 기/ETN
귀찮/VA 어서/EC 그냥/MAG 쓰/VV ㅂ니다/EF
```

`좋아요`가 `좋/VA + 어요/EF`로, `씁니다`가 `쓰/VV + ㅂ니다/EF`로 갈라진다 — **어간**과 **어미**가 분리된 것이다. 토큰 하나는 `t.form`(형태소 문자열)과 `t.tag`(품사)를 가진 객체다. 수업에서 쓴 태그만 표로 두면 이렇다(세종 품사 태그 체계).

| 태그 | 뜻 | 예 |
| --- | --- | --- |
| `NNG` | 일반 명사 | 마감, 배송, 가격 |
| `NNP` | 고유 명사 | 상품명·브랜드 |
| `VV` | 동사 | 쓰, 받, 터지 |
| `VA` | 형용사 | 좋, 많, 빠르 |
| `MAG` | 일반 부사 | 안, 그냥, 정말 |
| `JKS`·`JX`·`EF`·`EC`·`ETM` … | 조사·어미 | 이, 도, 어요, 고 — 뜻보다 문법 |

`add_user_word(단어, 품사)`는 사전에 없는 신조어를 **한 덩어리**로 인식하게 등록한다. 등록하지 않으면 `총알배송`은 `총알/NNG + 배송/NNG`로 갈라져 "총알"이라는 엉뚱한 명사가 생긴다(이 노트에서 확인 — `가성비`·`내돈내산`은 Kiwi 0.24 기본 사전에 이미 있어 등록 전후가 같다). 도메인마다 쪼개면 뜻이 사라지는 말이 있고, 그 목록을 사전에 더하는 것이 **형태소 분석기 튜닝의 첫 단계**다 — 연습문제에서는 영화 리뷰용으로 `노잼`·`꿀잼`·`갓작`·`발연기`·`인생영화`를 등록한다.

### 1-4. 4단계 — 불용어 `Stopwords()`와 직접 정한 `custom_stopwords`

```python
from kiwipiepy.utils import Stopwords
kiwi_stopwords = Stopwords()                    # 기본 불용어 100개
custom_stopwords = {'그냥', '그저', '모른다'}   # 이 자료에 맞춰 더 빼는 말
```

**불용어(stopword)**는 자주 나오지만 긍정·부정을 가르는 데 뜻이 없는 말이다. `Stopwords()`가 가진 기본 100개를 들여다보면 거의 전부 **조사·어미·보조용언**이다 — `이/JKS`, `도/JX`, `는/ETM`, `어요`류 어미, `하/VV`, `있/VX`, `않/VX`, `같/VA`, `것/NNB`, `사람/NNG`. 품사 태그와 함께 저장돼 있어서 `지/EC`(어미)는 빼고 `지/NNG`(명사)는 남기는 식으로 구분한다. `kiwi.tokenize(text, stopwords=kiwi_stopwords)`에 넘기면 분석 결과에서 이 조각들이 빠진 채 나온다.

`custom_stopwords`는 **기본 목록 뒤에 내가 더 빼는 말**이다 — 집합(`set`)으로 두는 것은 `in` 검사가 빠르기 때문이다. `그냥`·`그저`는 쇼핑 리뷰에 흔하지만 감정 방향이 없는 부사이고, `모른다`는 "잘 모르겠어요"류의 유보 표현이다. 두 층으로 나뉜 이유는 기본 목록은 자료와 무관한 문법 조각이고, 추가 목록은 **자료를 보고 정하는** 것이라서다. 연습문제에서는 영화 리뷰용으로 `영화`·`진짜`·`정말`·`너무`·`완전`을 추가하는데, `영화`가 들어간 것이 핵심이다 — 영화 리뷰에서 "영화"라는 말은 모든 문장에 있어 아무 정보가 없다.

### 1-5. 5단계 — `tokenize_kiwi()` 직접 만든 토크나이저: 품사 고르기 → 1글자 빼기 → 어간에 `다` 붙이기

```python
def tokenize_kiwi(text):
    tokens = kiwi.tokenize(text, stopwords=kiwi_stopwords)
    target_tags = {'NNG', 'NNP', 'VV', 'VA', 'MAG'}
    result = []
    for t in tokens:
        if t.tag in target_tags and t.form not in custom_stopwords:
            if len(t.form) > 1 or t.form in {'못', '잘'}:
                word = t.form + '다' if t.tag in {'VV', 'VA'} else t.form
                result.append(word)
    return result

test_word = df_sample['cleaned_review'].iloc[0]
print(tokenize_kiwi(test_word))
# 마감이 안좋아요 실밥도 많고 바느질도 부족한 부분이 몇군데 있네요 교환받기 귀찮아서 그냥 씁니다
# → ['마감', '바느질', '부족', '부분', '교환', '귀찮다']
```

이 함수가 수업의 중심이다. 문장 하나를 받아 **단어 리스트**를 돌려주는데, 세 겹의 필터와 한 번의 변환을 거친다.

| 순서 | 조건 | 뜻 | 첫 리뷰에서 |
| --- | --- | --- | --- |
| ① | `t.tag in target_tags` | 명사·동사·형용사·부사만 — 조사·어미는 버린다 | `이`·`도`·`어요`·`고`·`네요` 탈락 |
| ② | `t.form not in custom_stopwords` | 추가 불용어 제외 | `그냥` 탈락 |
| ③ | `len(t.form) > 1 or t.form in {'못', '잘'}` | 1글자는 버리되 `못`·`잘`은 예외 | `안`·`실`·`밥`·`좋`·`많`·`있`·`쓰` 탈락 |
| ④ | `t.form + '다' if t.tag in {'VV', 'VA'} else t.form` | 동사·형용사 어간에 `다`를 붙여 **기본형** | `귀찮` → `귀찮다` |

③은 한 글자 조각이 대개 뜻이 없거나(`실`·`밥`처럼 잘못 쪼개진 것) 너무 흔해서(`것`·`수`) 두는 규칙이고, `못`·`잘`은 한 글자지만 부정·긍정을 가르는 부사라 살려 둔다. ④가 **표제어 복원(lemmatization)**의 간단판이다 — `좋아요`·`좋고`·`좋네요`가 전부 어간 `좋`으로 쪼개지니 `다`만 붙이면 `좋다` 하나로 모인다. 단어의 **활용형을 하나로 합치는** 것이 이 단계의 목적이고, 이게 없으면 7단계의 열(단어) 수가 몇 배로 늘어난다. 수업 주석 "파이썬 삼항연산자: 표현식 if 조건 else 거짓"이 ④의 한 줄 문법이다 — Java·JS의 `조건 ? 참 : 거짓`과 순서가 다르다.

한 가지 알아 둘 점이 있다. ③이 ④보다 **먼저** 돌기 때문에, `좋`·`많`·`크`·`싸`처럼 어간이 한 글자인 형용사·동사는 `다`가 붙기 전에 1글자 규칙에 걸려 사라진다. 그래서 7단계 어휘에 `좋다`·`많다`가 없고, 긍정의 가장 흔한 말인 "좋아요"가 모델에 안 들어간다 — 이 노트에서 돌린 어휘 4,106개에 `좋다`가 없는 것으로 확인된다. 그래도 0.816이 나오는 것은 `만족`·`빠르다`·`편하다`·`맛있다` 같은 두 글자 이상의 말이 그 몫을 대신하기 때문인데, 1글자 어간만 ④를 먼저 적용하거나 `{'못', '잘', '좋', '많'}`처럼 예외를 늘리는 식으로 손볼 자리다(2-2 참고).

이 노트에서 다른 리뷰 몇 건을 더 넣어 보면 함수가 무엇을 남기는지 감이 온다.

```
깨끗하게 잘 다듬어져 있어요 맛도좋고요            → ['잘', '다듬다']
재구매 배송빨라요 길냥이들이 잘먹어요 대용량이라 좋네요 → ['구매', '배송', '빠르다', '길냥이', '잘', '용량']
제품도 빨리 배송해주시고 꼼꼼하게 잘챙겨주셨어요    → ['제품', '빨리', '배송', '꼼꼼', '잘', '챙기다']
```

`재구매`가 `재/XPN + 구매`로 쪼개져 `구매`만 남고, `배송빨라요`처럼 띄어쓰기가 없어도 `배송`·`빠르다`로 갈라진다 — 공백 기준 토크나이저로는 불가능한 일이다. 수업 주석 "전처리: 학습 하기 전에 문장들을 단어로 분리"가 이 함수의 한 줄 요약이다.

### 1-6. 6단계 — `train_test_split(..., stratify=)`에 문장 Series를 그대로

```python
from sklearn.model_selection import train_test_split
X_train, X_test, Y_train, Y_test = train_test_split(
    df_sample['cleaned_review'], df_sample['label'],
    test_size=0.2, random_state=42, stratify=df_sample['label'])
```

X가 `cleaned_review` **문자열 Series 한 줄**이라는 것만 다르고 나머지는 day12부터와 같다. day12의 "특성은 2차원" 규칙이 여기서는 적용되지 않는다 — 벡터라이저가 1차원 문장 묶음을 받아 2차원 행렬로 **만들어 주는** 쪽이라, 이중 대괄호로 DataFrame으로 감싸면 오히려 오류다. `stratify=`는 day15의 `StratifiedKFold`와 같은 뜻으로 훈련·테스트의 긍정·부정 비율을 맞춘다(테스트 1,000건: 부정 503 · 긍정 497). 분할을 **벡터화보다 먼저** 하는 것이 중요하다 — 다음 단계의 `fit`을 훈련 문장으로만 해야 테스트 문장의 단어가 어휘에 새지 않는다(day13 `StandardScaler`의 `fit`/`transform` 분리와 같은 원칙).

### 1-7. 7단계 — `TfidfVectorizer(tokenizer=tokenize_kiwi, token_pattern=None)`로 희소 행렬

```python
from sklearn.feature_extraction.text import TfidfVectorizer
tfidf = TfidfVectorizer(
    tokenizer=tokenize_kiwi,   # 생략하면 공백 기준 — 직접 만든 함수를 넘긴다
    token_pattern=None,        # tokenizer를 줬으니 기본 정규식 패턴은 끈다(경고 방지)
)
X_train_tfidf = tfidf.fit_transform(X_train)    # 어휘 학습 + 변환
X_test_tfidf = tfidf.transform(X_test)          # 변환만
print(X_train_tfidf.shape)   # (4000, 4106)
print(X_test_tfidf.shape)    # (1000, 4106)
print(tfidf.get_feature_names_out()[:10])
# ['가게' '가겨' '가격' '가격대' '가관' '가구' '가까이' '가끔' '가늘다' '가능']
```

여기서 문장이 숫자가 된다. `TfidfVectorizer`는 두 가지 일을 한다 — `fit`에서 훈련 문장 4,000건을 `tokenize_kiwi`로 쪼개 나온 **모든 단어의 목록(어휘, vocabulary)**을 만들고, `transform`에서 문장마다 "어휘의 각 단어가 이 문장에 얼마나 중요한가"를 숫자로 채운 **한 행**을 만든다. 결과는 `(문장 수, 어휘 크기)` = `(4000, 4106)` 행렬이다 — 열 4,106개가 훈련 리뷰에 등장한 서로 다른 단어 수고, 테스트 행렬도 같은 4,106열이다(`transform`만 했으니 테스트에만 있는 단어는 열이 없고 그냥 무시된다). 수업 주석의 장난감 예가 원리를 보여 준다.

```
문장 1: 안녕 사과 바나나 하세요        어휘 = [안녕, 사과, 바나나, 하세요, 딸기]  → (2, 5)
문장 2: 안녕 딸기 하세요
                안녕  사과  바나나  하세요  딸기
문장 1            1     1     1      1     0
문장 2            1     0     0      1     1
```

이것이 **BoW(Bag of Words)** — 단어 순서를 버리고 "어떤 단어가 있나"만 남긴 표현이다. 0/1 대신 **TF-IDF** 값을 채우는 것이 `TfidfVectorizer`다.

| 항 | 뜻 | 효과 |
| --- | --- | --- |
| **TF**(term frequency) | 이 문장에 그 단어가 몇 번 나왔나 | 많이 나온 단어가 크다 |
| **IDF**(inverse document frequency) | 전체 문장 중 그 단어가 든 문장이 얼마나 적은가 (`log(N / df) + 1`) | 어디에나 있는 단어는 작아지고, 드문 단어는 커진다 |
| TF × IDF, 행마다 L2 정규화 | 두 값의 곱을 문장 길이로 나눈 꼴 | 긴 리뷰와 짧은 리뷰를 같은 저울에 |

이 노트에서 IDF가 가장 **낮은**(= 가장 흔한) 단어는 `잘`(2.85) · `너무` · `구매` · `배송` · `빠르다` · `사용` · `제품` · `가격` · `생각` · `만족`이고, 가장 높은 값 8.6을 가진 단어가 2,357개다 — 어휘 절반 이상이 **훈련 문장 4,000건 중 딱 한 번** 나온 단어다. 행 하나를 꺼내 보면 `[('맛있다', 0.486), ('손질', 0.874)]`처럼 **두 칸만 0이 아니고** 두 값의 제곱합은 1이다(L2 정규화). 4,000 × 4,106 = 1,640만 칸 중 값이 있는 칸은 21,415개(0.13 %), 한 리뷰당 평균 5.4단어 — 그래서 이 행렬은 **희소 행렬(sparse matrix, `scipy.sparse.csr_matrix`)**로 저장된다. 0을 다 적는 밀집 배열이면 1,640만 개 실수(130 MB)인데, 0이 아닌 자리와 값만 적으면 수십 KB다. `tokenizer=`를 넘기면서 `token_pattern=None`을 함께 두는 것은, 토크나이저가 있으면 기본 정규식 패턴이 쓰이지 않는데도 sklearn이 "둘 다 설정됐다"는 경고를 내기 때문이다.

`get_feature_names_out()[:10]`의 `'가겨'`가 수업 주석 "(문제점) 오타 등으로 유사한 단어들을 분별 불가능해서 다른 단어로 취급 / (해결) 유사도 거리 계산(임베딩/BERT)"의 실물이다 — `가격`의 오타 `가겨`가 **완전히 다른 열**이 된다. BoW·TF-IDF는 단어를 글자 그대로 비교하므로 `가격`과 `가겨`, `예쁘다`와 `이쁘다`(이 노트의 긍정 가중치 상위에 둘이 따로 올라 있다)는 아무 관계가 없다. 그 한계를 넘는 것이 3-1의 임베딩이다.

### 1-8. 8단계 — `LogisticRegression`으로 분류, `score`·`f1_score`, `.toarray()`

```python
from sklearn.linear_model import LogisticRegression    # 실무적으로는 LightGBM도
model = LogisticRegression(C=1.0, max_iter=1000, random_state=42)
model.fit(X_train_tfidf, Y_train)
print(model.score(X_train_tfidf, Y_train))   # 0.89025
print(model.score(X_test_tfidf, Y_test))     # 0.816
Y_pred = model.predict(X_test_tfidf)
from sklearn.metrics import f1_score
print('f1 : ', f1_score(Y_test, Y_pred))     # 0.8087318087318087
print(X_train_tfidf.toarray()[0])            # [0. 0. 0. ... 0. 0. 0.]  수치 밀집행렬
```

모델은 day14의 도미·빙어 로지스틱 회귀 그대로다 — 4,106개 열마다 가중치 하나를 배워 `시그모이드(가중합)`을 긍정 확률로 쓴다. 희소 행렬을 **그대로** `fit`에 넣는다는 점이 새롭고(sklearn의 선형 모델은 `csr_matrix`를 받는다), `C=1.0`은 day13 릿지의 `alpha`와 반대 방향의 규제 세기(작을수록 강한 규제), `max_iter=1000`은 열이 4천 개라 기본 100번 안에 수렴하지 않을 때를 위한 여유다(이 노트에서는 18번에 수렴). 텍스트 분류에서 로지스틱 회귀가 기본 선택인 이유는 **열이 수천~수만 개인 희소 입력에 빠르고**, 가중치가 곧 "단어별 긍정·부정 점수"라 읽기 쉽기 때문이다.

| 지표 | 값 | 읽는 법 |
| --- | --- | --- |
| 훈련 정확도 | 0.890 | 4,000건 중 89 % |
| 테스트 정확도 | **0.816** | 처음 보는 1,000건 중 81.6 % |
| F1(테스트) | 0.809 | 긍정 클래스의 정밀도 0.837 · 재현율 0.783의 조화평균 |

훈련과 테스트의 7 %p 차이가 **과대적합의 크기**다 — 어휘의 절반이 한 번만 나온 단어라, 그 단어들은 훈련 문장 한 건의 라벨을 외우는 데만 쓰인다. 혼동행렬은 부정 503건 중 427 맞춤(76 틀림), 긍정 497건 중 389 맞춤(108 틀림)이라 **긍정 리뷰를 부정으로 보는 쪽**이 조금 더 많다 — 1-5에서 `좋다`가 빠진 것과 무관하지 않다. `f1_score`는 day14~15에서 본 것과 같이 양성(1 = 긍정)에 대한 값이고, 양·음이 반반인 이 자료에서는 정확도와 거의 같다. `.toarray()[0]`은 희소 행렬의 첫 행을 길이 4,106의 밀집 배열로 바꿔 보는 것인데, 거의 전부 0이라 `[0. 0. 0. ... 0. 0. 0.]`로 찍힌다 — "숫자 행렬이 되긴 됐다"를 눈으로 확인하는 용도다. 전체를 `toarray()`하면 메모리를 먹으니 행 하나만 보는 습관이 맞다.

가중치 `model.coef_[0]`을 어휘와 짝지어 정렬하면 모델이 배운 것이 그대로 보인다(이 노트).

| 부정 쪽(음수 큰 순) | 긍정 쪽(양수 큰 순) |
| --- | --- |
| `별로` −3.94 · `실망` −2.75 · `반품` −2.31 · `모르다` −2.14 · `못` −2.03 · `버리다` · `다시` · `귀찮다` · `택배` · `터지다` · `느리다` | `편하다` +3.34 · `빠르다` +3.29 · `만족` +3.28 · `맛있다` +3.10 · `이쁘다` · `감사` · `예쁘다` · `좋아하다` · `선물` · `잘` +2.26 · `가성비` +1.75 |

1-5에서 살려 둔 `못`(−2.03)과 `잘`(+2.26)이 정확히 반대 부호로 상위에 있다 — 1글자 예외 둘이 왜 그 둘이었는지가 가중치로 설명된다. `add_user_word`로 등록한 `가성비`도 +1.75로 긍정 단어가 됐다.

### 1-9. 9단계 — 새 리뷰 예측: 같은 정제 → `tfidf.transform` → `predict_proba` → 0.4/0.6 임계값

```python
new_reviews = [
    "배송도 정말 빠르고 가성비 최고입니다! 재구매 의사 있어요.",
    "마감 상태가 엉망이고 실밥이 다 터져서 왔네요. 최악입니다.",
    "그냥 가격만큼 하는 것 같아요. 특별히 좋지도 나쁘지도 않음."
]
cleaned_new = []
for text in new_reviews:                                    # 1단계와 같은 정제
    text = re.sub(r'[^가-힣a-zA-Z0-9\s]', ' ', str(text))
    cleaned_new.append(' '.join(text.split()))
new_tfidf = tfidf.transform(cleaned_new)                    # fit 없이 transform만
probs = model.predict_proba(new_tfidf)                      # (3, 2) — 열 0 부정확률, 열 1 긍정확률
for i in range(len(new_reviews)):
    pos = probs[i][1]
    if pos >= 0.6:   contents = '긍정'
    elif pos <= 0.4: contents = '부정'
    else:            contents = '중립'
    print(f'리뷰: , {new_reviews[i]} ')
    print(f'감성분석: , {contents} , 긍정확률:{pos}, 부정확률:{probs[i][0]}')
```

```
리뷰: 배송도 정말 빠르고 가성비 최고입니다! 재구매 의사 있어요.     → 긍정  긍정확률 0.9205  부정확률 0.0795
리뷰: 마감 상태가 엉망이고 실밥이 다 터져서 왔네요. 최악입니다.      → 부정  긍정확률 0.0393  부정확률 0.9607
리뷰: 그냥 가격만큼 하는 것 같아요. 특별히 좋지도 나쁘지도 않음.    → 중립  긍정확률 0.4302  부정확률 0.5698
```

서빙의 원칙은 day18 연습(`astype(X_train[col].dtype)`)과 같다 — **학습 때 거친 전처리를 새 입력에도 똑같이**. 여기서는 세 단계다: ① 같은 정규표현식으로 정제, ② 학습된 `tfidf`로 `transform`(새로 `fit`하면 어휘가 바뀌어 모델과 열이 안 맞는다 — `tokenize_kiwi`는 `tfidf` 안에 들어 있으니 따로 부르지 않는다), ③ `predict_proba`. 반환은 `(3, 2)` 배열이고 열 0이 부정, 열 1이 긍정 확률이다(`model.classes_` 순서 = `[0, 1]`).

`predict`는 0.5를 기준으로 둘 중 하나를 고르지만, 수업은 **`predict_proba`에 임계값 두 개**를 둬 0.6 이상 긍정 · 0.4 이하 부정 · 그 사이 **중립**으로 셋을 만든다. 1-1에서 평점 3을 학습에서 빼 둔 것과 짝이다 — 모델은 긍·부정 둘만 배웠지만, 확신이 약한 구간을 따로 "중립"이라 부르면 애매한 리뷰를 억지로 한쪽에 넣지 않는다. 셋째 리뷰가 그 경우다 — 정제·토큰화를 거치면 `['가격', '특별히', '나쁘다']` 세 단어만 남고(`그냥`은 추가 불용어, `하`·`것`·`같`·`않`은 기본 불용어, `좋`은 1글자), 가중치 합이 거의 0 근처라 0.43이 나와 중립이 된다. `나쁘다`의 기여가 +0.17로 **양수**인 것도 눈여겨볼 만하다 — 훈련 리뷰에서 "나쁘지 않아요"가 긍정에 자주 쓰여 `나쁘다` 자체가 약한 긍정 단어가 된 것이다. BoW는 `않`을 불용어로 버려 **부정 표현의 방향을 못 본다**는 한계가 여기서 드러난다(2-3 참고).

### 1-10. 흐름 한 장 — 숫자 자료와 문장 자료의 파이프라인 비교

```
                day12~19 (숫자 X)                       s-14.ipynb (문장 X)
자료            read_csv → df[열 목록] (2차원 DataFrame)      read_table → df['cleaned_review'] (1차원 문장)
정제            to_numeric·dropna                       re.sub(r'[^가-힣a-zA-Z0-9\s]', ' ') + split/join
분할            train_test_split                         같음 (stratify)
숫자화          StandardScaler fit_transform/transform   TfidfVectorizer(tokenizer=tokenize_kiwi) fit_transform/transform
                 (열 수 그대로, 단위만 맞춤)               (문장 → 4,106열 희소 행렬 — 열이 여기서 생긴다)
                                                         └ Kiwi: tokenize → 품사 필터 → 1글자 제외 → 어간+다
모델            LogisticRegression / LightGBM            LogisticRegression (같은 클래스, 희소 입력)
평가            score·f1_score                           같음 (0.816 / 0.809)
서빙            같은 스케일러 transform → predict        같은 re.sub → 같은 tfidf.transform → predict_proba + 임계값 2개
```

## 2. 추가로 알면 좋은 활용법

### 2-1. 벡터라이저 인자로 어휘 다듬기 — `min_df`·`max_features`·`ngram_range`·`sublinear_tf`

```python
tfidf = TfidfVectorizer(tokenizer=tokenize_kiwi, token_pattern=None,
                        min_df=2,              # 2문장 미만에 나온 단어는 버림
                        ngram_range=(1, 2),    # 단어 하나 + 연속 두 단어(바이그램)
                        sublinear_tf=True)     # TF를 1 + log(tf)로 눌러 반복 단어 완화
```

1-7에서 어휘의 절반 이상(2,357개)이 한 번만 나온 단어였다. `min_df=2`는 그런 단어를 열에서 빼 과대적합을 줄이고 행렬을 가볍게 한다. `ngram_range=(1, 2)`는 `배송 빠르다`처럼 **연속한 두 단어를 한 열**로 더 만들어 "별로 아니다"류의 짝을 어느 정도 잡는다. 이 노트에서 `min_df=2 + (1, 2)`로 돌리면 어휘가 4,106 → 3,098로 **줄면서** 테스트 정확도는 0.816 → 0.822로 오른다 — 열을 늘리는 것보다 **쓸모없는 열을 빼는 것**이 먼저라는 교훈이다. `max_features=3000`은 IDF 기준 상위 N개만 남기는 상한이고, `sublinear_tf=True`는 같은 단어를 열 번 쓴 리뷰가 열 배 중요해지는 것을 막는다. 이 인자들을 day14의 `GridSearchCV`로 `Pipeline(tfidf, logreg)`에 묶어 `tfidf__min_df`·`logreg__C`를 함께 찾는 것이 다음 단계다.

### 2-2. `tokenize_kiwi`를 손보는 자리 — 1글자 어간 살리기, `Kiwi(model_type=)`, `kiwi.join`

1-5의 1글자 규칙이 `좋`·`많`·`싸`를 지우는 것을 봤다. 어간에 `다`를 **먼저** 붙인 뒤 길이를 재면(`좋다`는 2글자) 형용사는 살리고 `실`·`밥` 같은 명사 조각은 그대로 버릴 수 있다 — 순서만 바꾸는 한 줄이다. 그 밖에 `Kiwi(model_type='sbg')`는 문맥을 더 보는 모델로 분석 정확도가 오르고(느려진다), `kiwi.tokenize(..., normalize_coda=True)`는 `ㅋㅋ`·`ㅠㅠ`처럼 받침만 남은 글자를 처리한다. Kiwi에는 `kiwi.join(tokens)`도 있어서 형태소 리스트를 다시 자연스러운 문장으로 **합칠** 수 있는데, 어간+어미 조합을 규칙으로 되돌리니 `+'다'` 수작업보다 정확한 기본형 복원에 쓸 수 있다. `kiwi.extract_add_words(texts)`는 자료에서 **신조어 후보를 자동으로** 찍어 주니 1-3의 `add_user_word` 목록을 손으로 만들기 전에 돌려 볼 만하다.

### 2-3. 부정 표현을 살리기 — `않`·`안`을 불용어에서 빼고 바이그램으로

1-9의 "나쁘지도 않음"이 보여 준 문제다. 기본 `Stopwords()`에 `않/VX`가 들어 있어 "나쁘지 않다"와 "나쁘다"가 같은 벡터가 된다. `kiwi_stopwords.remove(('않', 'VX'))`로 불용어에서 빼고 1글자 예외에 `안`·`않`을 더한 뒤 `ngram_range=(1, 2)`를 켜면 `나쁘다 않다`·`안 좋다`가 **한 열**로 생겨 부정의 방향을 어느 정도 배운다. 영어 텍스트 마이닝에서 `not_good`처럼 부정어 뒤 단어에 접두사를 붙이는 기법과 같은 발상이다. 완전한 답은 아니고, 문맥을 보는 3-1의 모델로 가는 중간 단계다.

### 2-4. 단어별 가중치 표로 모델 설명하기 — `coef_`와 `get_feature_names_out` 짝짓기

```python
import numpy as np
names = tfidf.get_feature_names_out()
coef = model.coef_[0]
order = np.argsort(coef)
print('부정 단어:', list(zip(names[order[:10]], coef[order[:10]].round(2))))
print('긍정 단어:', list(zip(names[order[::-1][:10]], coef[order[::-1][:10]].round(2))))
```

1-8의 표를 만든 코드다. 트리 모델의 `feature_importances_`(day17~18)가 "어느 열이 중요한가"만 주는 데 비해, 로지스틱 회귀의 `coef_`는 **방향(부호)**까지 준다 — 이것이 텍스트 분류에서 선형 모델이 사랑받는 또 하나의 이유다. 새 리뷰 하나의 판정을 설명하려면 `new_tfidf[i]`의 0 아닌 칸마다 `값 × coef`를 더해 보면 어느 단어가 확률을 밀었는지 나온다(1-9 셋째 리뷰: `특별히` −0.19 · `가격` +0.03 · `나쁘다` +0.17).

### 2-5. `CountVectorizer`·`HashingVectorizer`와의 자리 — 언제 TF-IDF인가

`CountVectorizer`는 TF-IDF 대신 **등장 횟수**(수업 주석의 0/1 표)를 채운다. 이 노트에서 같은 토크나이저로 바꿔 돌리면 테스트 0.814로 TF-IDF(0.816)와 거의 같다 — 리뷰가 짧아(평균 5.4단어) 한 단어가 두 번 나오는 일이 드물어서다. 긴 문서(기사·논문)일수록 TF-IDF의 길이 정규화와 IDF 가중이 효과를 내고, 베이즈 분류기(`MultinomialNB`)는 횟수를 기대하니 `CountVectorizer`와 짝이다. `HashingVectorizer`는 어휘 사전을 만들지 않고 해시로 열을 정하니 수백만 문서 스트리밍에 쓴다. 참고로 Kiwi를 빼고 기본 공백 토크나이저로 돌리면 어휘가 17,130개로 네 배가 되는데 정확도는 0.814로 비슷하다 — 형태소 분석의 이득은 정확도보다 **어휘 크기와 해석 가능성**(가중치 표가 `좋아요`·`좋고`·`좋네요`로 갈라지지 않는다)에서 먼저 나타난다.

## 3. 더 나아가 알면 좋은 것

### 3-1. 임베딩 — "오타·유사어를 거리로" (수업 주석의 해결책)

BoW의 열은 서로 **직각**이다 — `가격`과 `가겨`, `예쁘다`와 `이쁘다`의 거리가 `가격`과 `배송`의 거리와 같다. **임베딩(embedding)**은 단어를 수백 차원의 **밀집 벡터**로 두고, 비슷한 문맥에 나오는 단어가 가까운 벡터를 갖도록 학습한다(Word2Vec·FastText — 한국어는 글자 n-gram을 보는 FastText가 오타에 강하다). 그러면 `예쁘다`와 `이쁘다`의 코사인 유사도가 높아져 한 번도 본 적 없는 표기도 뜻이 전달된다. 문장 벡터는 단어 벡터의 평균으로 시작하고, 거기서 한 걸음 더 간 것이 **BERT**류 사전학습 언어 모델이다 — 같은 단어도 문맥에 따라 다른 벡터를 주고, "나쁘지 않다"의 부정을 문장 안에서 읽는다. 한국어는 KoBERT·KcELECTRA(댓글·리뷰로 학습) 같은 공개 모델을 Hugging Face `transformers`로 불러 `fit` 대신 **미세조정(fine-tuning)**한다. 수업 주석의 "(해결) 유사도 거리 계산(임베딩/BERT)"이 이 길이고, 인덱스의 "LLM 동작 원리 — 토큰, 임베딩, 어텐션"으로 이어진다.

### 3-2. 텍스트 분류의 다른 모델들 — `MultinomialNB`·`LinearSVC`·LightGBM

로지스틱 회귀 옆에 두는 고전 셋이다. **나이브 베이즈**(`MultinomialNB`)는 단어 등장 횟수의 확률을 곱하는 모델로 학습이 거의 즉시고 작은 자료에서 뜻밖에 강하다. **선형 SVM**(`LinearSVC`)은 희소 고차원에서 로지스틱 회귀와 비슷하거나 조금 나은 경계를 찾고 텍스트 분류의 전통적 기준선이다. 수업 주석의 "실무적으로 LightGBM"은 day17~18의 부스팅을 희소 행렬 위에 올리는 것으로, 단어 간 **상호작용**(두 단어가 함께 나올 때)을 배우지만 수천 열의 희소 입력에서는 선형 모델보다 느리고 늘 더 낫지도 않다 — TF-IDF 뒤에 `TruncatedSVD`(희소 PCA, day19의 PCA와 같은 발상)로 수백 열로 줄인 뒤 트리에 넣는 것이 흔한 조합이다.

### 3-3. 감성 분석의 평가와 운영 — 임계값 조정, 라벨 노이즈, 데이터 양

0.4/0.6 임계값은 손으로 정한 값이다. 테스트 세트에서 `predict_proba`를 받아 임계값을 0.3~0.7로 움직이며 정밀도·재현율이 어떻게 변하는지(`precision_recall_curve`) 보면 "중립 구간을 얼마나 넓게 둘지"를 숫자로 정할 수 있다 — 고객 불만을 놓치면 안 되는 서비스라면 부정 쪽 임계값을 0.5 가까이 올린다. 평점을 라벨로 쓴 자료는 **라벨 노이즈**가 있다(5점인데 불만 글, 2점인데 배송만 탓하는 글) — 1-8의 7 %p 과대적합 일부는 이 잡음을 외운 것이다. 그리고 5,000건은 작다 — 20만 건 전체로 돌리면 어휘가 수만 개로 늘고 테스트 정확도가 0.9 가까이 오르니, 전처리 시간(Kiwi 토큰화 4,000건 3초 → 20만 건 수 분)과 성능의 교환을 직접 재 볼 만하다.

### 3-4. 다음에 볼 키워드

- 세종 품사 태그표 — `NNG`·`VV`·`VA`·`MAG`·`XSN`·`EF` 등 전체 목록
- 표제어 복원(lemmatization) vs 어간 추출(stemming) — `+'다'`가 흉내 낸 것
- `ngram_range`·`min_df`·`max_features`·`sublinear_tf` — 벡터라이저 인자
- `Pipeline(TfidfVectorizer, LogisticRegression)` + `GridSearchCV` — 전처리까지 한 번에 저장(`joblib`)
- `scipy.sparse.csr_matrix` — 희소 행렬 구조(`indices`·`data`·`nnz`)
- Word2Vec·FastText·BERT·KcELECTRA — 임베딩과 미세조정
- `MultinomialNB`·`LinearSVC`·`TruncatedSVD` — 텍스트 분류의 다른 길
- `precision_recall_curve` — 임계값을 데이터로 정하기
- 토픽 모델링(LDA)·워드클라우드 — 라벨 없는 텍스트 마이닝

## 실습 파일

- `KDT_2026/2026_Python/day20/s-14.ipynb` — `!pip install kiwipiepy` → 네이버 쇼핑 리뷰 20만 건 `read_table(url, names=['rating', 'review'])` → `rating != 3` 제외 → `label = (rating >= 4).astype(int)` → `sample(n=5000, random_state=42).reset_index(drop=True)` `(5000, 3)` → 1단계 `re.sub(r'[^가-힣a-zA-Z0-9\s]', ' ', str(text))` + `' '.join(text.split())` → `cleaned_review` 열 → 2~3단계 `Kiwi()` · `add_user_word('가성비'·'내돈내산'·'총알배송', 'NNG')` → 4단계 `Stopwords()` 기본 100개 + `custom_stopwords = {'그냥', '그저', '모른다'}` → 5단계 `tokenize_kiwi(text)`: `kiwi.tokenize(text, stopwords=)` → `{'NNG', 'NNP', 'VV', 'VA', 'MAG'}` 품사 필터 → `len > 1 or in {'못', '잘'}` → `VV`·`VA`에 `+'다'` → 첫 리뷰 `['마감', '바느질', '부족', '부분', '교환', '귀찮다']` → 6단계 `train_test_split(cleaned_review, label, test_size=0.2, random_state=42, stratify=label)` → 7단계 `TfidfVectorizer(tokenizer=tokenize_kiwi, token_pattern=None)` `fit_transform`/`transform` `(4000, 4106)`·`(1000, 4106)` · `get_feature_names_out()[:10]`(`가겨` 오타가 별도 열 — 임베딩/BERT 주석) → 8단계 `LogisticRegression(C=1.0, max_iter=1000, random_state=42)` 훈련 0.89025 · 테스트 0.816 · `f1_score` 0.8087 · `toarray()[0]` → 9단계 새 리뷰 3건 같은 `re.sub` → `tfidf.transform` → `predict_proba` → `pos >= 0.6` 긍정 / `<= 0.4` 부정 / 중립 (0.9205 긍정 · 0.0393 부정 · 0.4302 중립)

## 관련 노트

[[AI 정리본 인덱스]] · [[AI day19 KMeans·PCA 통신사 고객 등급화 연습문제 풀이]] · [[AI day20 NSMC 영화 리뷰 감성 분석 연습문제 풀이]] · [[AI day14 로지스틱 회귀로 도미·빙어 분류]] · [[AI day13 StandardScaler 표준화와 릿지·라쏘 규제]] · [[AI day15 로지스틱 다중 분류와 혼동행렬·분류 리포트]] · [[KDT_2026 학습 지도]]
