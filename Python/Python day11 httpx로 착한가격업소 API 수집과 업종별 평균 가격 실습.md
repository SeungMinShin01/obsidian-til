---
출처: Claude 분석
원본: KDT_2026/2026_Python/practice/practice8.py
작성일: 2026-11-09
tags: [학습, python]
---

# Python day11 — httpx로 착한가격업소 API 수집과 업종별 평균 가격 실습

> 실습 파일: `practice/practice8.py`
> 허브: [[Python 정리본 인덱스]] · 이전: [[Python day11 httpx로 공공데이터 API 호출과 JSON 데이터프레임 변환]] · 다음: [[Python day12 사이킷런 단순 선형 회귀로 물고기 무게 예측]]

day11 수업에서 대구 중구 맛집 API를 호출하던 뼈대를 **다른 공공데이터에 옮겨 끝까지 분석까지 이어 보는** 연습이다. 대상은 공공데이터포털의 "행정안전부 착한가격업소 현황" — 지자체가 지정한 가격 착한 업소 목록으로, 업종·업소명·주소·대표 품목 가격이 들어 있다. 흐름은 네 단계다: 인증키를 붙여 100건을 호출하고 → 응답 JSON의 `data` 배열을 데이터프레임으로 만들고 → 가격 열을 숫자로 바꿔 평균을 내고 → 업종별로 묶어 평균 가격을 막대그래프로 그린다. 수업에서는 `info()`에서 멈췄던 자리에서 day08의 `to_numeric`·`groupby`, day09의 `barplot`이 이어 붙어 **수집 → 전처리 → 집계 → 시각화**가 한 파일에 들어간다. 크롤링·API 묶음(day10~11)과 판다스·시각화 묶음(day08~09)이 처음 한 흐름으로 만나는 지점이다.

## 1. 배운 내용

### 1-1. 문제 2-1 — 인증키 붙여 100건 요청

```python
import httpx
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

service_key = "<공공데이터포털에서 발급받은 인증키>"     # 노트에서는 값을 가린다

url = "https://api.odcloud.kr/api/3045247/v1/uddi:<데이터셋 고유 ID>"
url += "?page=1"
url += "&perPage=100"
url += f"&serviceKey={service_key}"

response = httpx.get(url)
print(response)      # <Response [200 OK]>
```

수업 `h-01.py`와 완전히 같은 조립법이다. 고정 부분(odcloud 주소 + 데이터셋 ID)에 `?`로 첫 파라미터를 열고 `&`로 나머지를 이어 붙인다. 지문의 "임의의 100건"은 `perPage=100` 한 칸이다 — `page=1`과 함께 "첫 페이지를 100건 단위로"라는 뜻이고, 전체가 몇 건이든 처음 100건만 온다.

| 파라미터 | 값 | 뜻 |
| --- | --- | --- |
| `page` | 1 | 몇 번째 묶음인가 |
| `perPage` | 100 | 한 묶음에 몇 건인가 → 지문의 "100건" |
| `serviceKey` | 발급 키 | 호출자 식별 — 없으면 401/403 |

인증키는 수업 노트에 적은 대로 **비밀번호에 준하는 자격 정보**다. 소스 파일에 값이 그대로 들어가 있으면 공개 저장소에 올라가는 순간 남이 내 한도로 호출할 수 있으므로, 이 노트에서는 값을 가리고, 코드도 2-1의 `.env` 분리 쪽으로 옮기는 것이 다음 단계다.

### 1-2. 문제 2-2 — `data` 배열을 데이터프레임으로

```python
response_json = response.json()
df = pd.DataFrame(response_json['data'])
df.info()
```

odcloud 계열 API의 응답은 수업에서 본 그대로 `currentCount`·`data`·`matchCount`·`page`·`perPage`·`totalCount` 여섯 키의 겉껍데기 안에 **`data` 리스트**가 알맹이로 들어 있다. 지문의 "실제 행 목록인 `data` 배열을 추출"이 `response_json['data']`이고, 딕셔너리 리스트는 `pd.DataFrame`이 바로 행·열로 펼친다. 100건을 요청했으니 `info()`에 `100 entries`가 찍히고, 열은 업소 정보 수십 개(업종·업소명·주소·연락처·품목·가격 등)가 전부 `object`다 — 공공데이터는 숫자도 문자열로 내려 주는 일이 많아, 다음 단계의 형 변환이 필요해진다.

```python
df = df[['업종', '업소명', '주소', '가격1']]
print(df.head())
```

수십 개 열 중 지문이 요구하는 넷만 **이중 대괄호**로 골라 다시 담는다. day08의 열 선택 규칙 그대로이고, 뒤의 집계·그래프가 이 네 열만 쓰므로 일찍 좁혀 두면 `head()`로 보기도 편하다.

| 열 | 내용 |
| --- | --- |
| `업종` | 한식·중식·이미용·세탁 등 분류 — 2-4의 `groupby` 키 |
| `업소명` | 가게 이름 |
| `주소` | 소재지 |
| `가격1` | 대표 품목 1의 가격 — 문자열로 내려옴 |

### 1-3. 문제 2-3 — `to_numeric`으로 숫자화하고 평균

```python
df['가격1'] = pd.to_numeric(df['가격1'], errors="coerce")
print("가격1 평균 :", df['가격1'].mean())
```

`object`인 `가격1`을 그대로 `mean()`하면 문자열이라 계산이 안 된다. `pd.to_numeric`이 열 전체를 숫자로 바꾸는데, 핵심은 **`errors="coerce"`** — "8,000"처럼 쉼표가 섞였거나 빈 문자열인 값을 만나면 오류를 내는 대신 `NaN`으로 바꾼다(day08 전처리 노트의 `to_datetime(errors='coerce')`와 같은 옵션). 그래야 100건 중 몇 건이 지저분해도 나머지로 평균을 낼 수 있고, `mean()`은 `NaN`을 자동으로 빼고 계산한다.

| `errors=` | 변환 못 하는 값을 만나면 |
| --- | --- |
| `'raise'` (기본) | `ValueError`로 멈춤 |
| `'coerce'` | `NaN`으로 바꾸고 계속 |
| `'ignore'` | 원래 값 그대로 둠 (열이 `object`로 남음) |

이 한 줄이 "수집한 자료는 바로 계산할 수 있는 상태가 아니다"라는 day08의 교훈을 API 자료에서 다시 보여 준다. 변환 뒤 `df['가격1'].isna().sum()`으로 몇 건이 `NaN`이 됐는지 확인해 두면 평균이 몇 건 기준인지 알 수 있다.

### 1-4. 문제 2-4 — 업종별 평균과 막대그래프

```python
업종별평균 = df.groupby('업종')['가격1'].mean()
print(업종별평균)
```

day08의 `groupby('열')['값 열'].mean()` 그대로다. 결과는 업종이 인덱스, 평균 가격이 값인 **시리즈**다. 변수 이름을 한글로 둔 것은 파이썬이 한글 식별자를 허용하기 때문인데(day10 실습 노트에서 확인한 대로), 관례는 영문이므로 혼자 보는 스크립트가 아니면 `avg_by_type` 정도로 두는 편이 무난하다.

```python
plt.rc('font', family='Malgun Gothic')
plt.rcParams['axes.unicode_minus'] = False
sns.set_theme(font='Malgun Gothic', rc={'axes.unicode_minus': False}, style='whitegrid')

sns.barplot(x=업종별평균.index, y=업종별평균.values)
plt.title("업종별 평균 가격 비교")
plt.xlabel("업종")
plt.ylabel("평균 가격(원)")
plt.show()
```

시본으로 그리면서 **한글 설정을 두 번** 한 것이 눈에 띈다. day09 시본 노트에서 정리한 대로 `sns.set_theme`가 `rcParams`를 덮어쓰기 때문에, 맷플롯립 쪽 `plt.rc`만 해 두면 테마 적용 순간 폰트가 기본으로 돌아간다. 그래서 `set_theme` 안에 `font=`·`rc=`로 폰트와 음수 기호를 다시 넣어야 업종 이름이 네모로 깨지지 않는다. 앞의 `plt.rc` 두 줄은 테마 없이 맷플롯립만 쓸 때의 보험이다.

`barplot(x=인덱스, y=값)`은 day09 따릉이 EDA 실습에서 시간대별 대여량을 그릴 때와 같은 꼴이다 — `groupby` 결과 시리즈의 `.index`가 x, `.values`가 y다. `barplot`은 원래 평균을 계산해 주는 함수지만 이미 평균을 낸 시리즈를 넘기면 값 하나씩이라 그대로 막대 높이가 된다. `plt.title`·`xlabel`·`ylabel`·`show()`로 마무리하는 것은 day09 일곱 단계 그대로다.

### 1-5. 수업 코드와 연습 코드 — 어디까지가 같고 무엇이 새로운가

| 단계 | 수업 `h-01.py` | 연습 `practice8.py` | 출처 노트 |
| --- | --- | --- | --- |
| 주소 조립 | 고정 + `page`·`perPage`·`serviceKey` | 같음 (`perPage=100`) | day11 |
| 호출 | `httpx.get` → `.json()` | 같음 | day11 |
| 데이터프레임 | `pd.DataFrame(json['data'])` → `info()` | 같음 + 네 열 선택 | day11·day08 |
| 형 변환 | — | `to_numeric(errors='coerce')` | day08 |
| 집계 | — | `mean()`·`groupby().mean()` | day08 |
| 시각화 | — | `sns.barplot` + 한글 테마 | day09 |

수업은 "받아서 표로 만들기"까지였고, 연습은 그 뒤에 세 단계를 붙였다. 새 함수는 하나도 없다 — 전부 앞 노트들에서 따로 배운 것이고, 이 파일의 의미는 그것들을 **한 줄로 꿰었다**는 데 있다. 수집한 자료가 "보기만 하는 표"에서 "질문에 답하는 숫자와 그림"이 되는 순간이다.

## 2. 추가로 알면 좋은 활용법

### 2-1. 인증키를 코드 밖으로 — `.env`

```python
import os
from dotenv import load_dotenv
load_dotenv()                                   # 같은 폴더의 .env 파일을 읽는다
service_key = os.environ['DATA_GO_KR_KEY']
```

```text
# .env  (git에 올리지 않는다 — .gitignore에 추가)
DATA_GO_KR_KEY=여기에_발급키
```

수업 노트 2-1에서 적어 둔 패턴을 연습 파일에 적용하는 것이 첫 과제다. `pip install python-dotenv` 뒤 `.env`에 키를 적고 코드에서는 이름으로만 부른다. 소스를 공개해도 키가 새지 않고, 키를 바꿀 때 코드를 안 건드려도 된다.

### 2-2. 파라미터를 딕셔너리로 — `params=`

```python
params = {"page": 1, "perPage": 100, "serviceKey": service_key}
response = httpx.get("https://api.odcloud.kr/api/3045247/v1/uddi:<데이터셋 ID>", params=params)
print(response.url)     # 조립된 주소 확인
```

`+=` 세 줄로 문자열을 잇는 대신 딕셔너리를 넘기면 httpx가 `?`·`&`·URL 인코딩을 알아서 처리한다. 특히 인증키에 `+`·`/`·`=` 같은 글자가 섞여 있을 때 손으로 이어 붙이면 깨지는 경우가 있어, 포털이 주는 "디코딩 키"를 `params`로 넘기는 쪽이 안전하다.

### 2-3. 100건이 아니라 전부 — `totalCount`로 페이지 반복

```python
first = httpx.get(base, params={**params, "page": 1}).json()
total = first['totalCount']
pages = -(-total // 100)                     # 올림 나눗셈
rows = first['data']
for p in range(2, pages + 1):
    rows.extend(httpx.get(base, params={**params, "page": p}).json()['data'])
df = pd.DataFrame(rows)
```

착한가격업소는 전국에 수천 곳이라 100건으로 낸 평균은 "첫 100건의 평균"일 뿐이다. 응답 겉껍데기의 `totalCount`로 전체 건수를 알아내고, `perPage`로 나눠 페이지 수를 구한 뒤 반복한다. day10 페이징 크롤링의 `for page in range(1, 4)`가 API에서는 `totalCount` 기반의 정확한 반복으로 바뀐다. 호출 사이에 `time.sleep(0.5)` 정도를 두면 일일 한도와 서버에 예의를 지킬 수 있다.

### 2-4. 가격 열 여럿 — `가격1`·`가격2`·`가격3`

```python
price_cols = [c for c in df.columns if c.startswith('가격')]
df[price_cols] = df[price_cols].apply(pd.to_numeric, errors='coerce')
```

이 데이터셋은 업소마다 대표 품목이 여럿이라 `품목1`·`가격1`·`품목2`·`가격2`… 식으로 열이 반복된다. 열 이름이 `가격`으로 시작하는 것만 리스트 컴프리헨션으로 골라 `apply(pd.to_numeric)`를 한 번에 씌우면 `to_numeric` 줄을 열 개수만큼 복사하지 않아도 된다. 긴 형식으로 바꾸려면 `pd.melt`를 쓴다.

### 2-5. 업종별 개수도 함께 — `agg`와 정렬

```python
summary = df.groupby('업종').agg(업소수=('업소명', 'count'), 평균가격=('가격1', 'mean'), 중앙값=('가격1', 'median'))
summary = summary.sort_values('평균가격', ascending=False)
print(summary)
```

평균 하나만 보면 업소가 1곳뿐인 업종이 평균을 과장할 수 있다. day08의 named aggregation으로 업소 수·평균·중앙값을 한 표에 두고 정렬하면 "표본이 몇인 평균인가"가 함께 보인다. 그래프도 `sns.barplot(data=summary.reset_index(), x='업종', y='평균가격', order=…)`처럼 정렬된 순서로 그리면 읽기 쉽다.

### 2-6. 막대가 많을 때 — 가로 막대와 라벨 회전

```python
sns.barplot(y=업종별평균.index, x=업종별평균.values)      # x·y 바꾸면 가로 막대
# 또는
plt.xticks(rotation=45, ha='right')                      # 세로 막대 + 라벨 기울이기
```

업종이 열 개를 넘으면 x축 라벨이 겹친다. day09 따릉이 실습의 "상위 10 대여소 가로 막대"처럼 x·y를 바꾸거나, `xticks(rotation=)`으로 라벨을 기울인다. `sns.barplot(…, errorbar=None)`으로 신뢰구간 막대를 끄면 이미 평균 낸 값에 의미 없는 선이 붙지 않는다.

### 2-7. 받은 것을 저장해 두기

```python
df.to_csv('cheap_price_shops.csv', index=False, encoding='utf-8-sig')
```

API는 일일 호출 한도가 있고 서버 상태에 따라 실패도 한다. 수집이 끝나면 CSV로 저장하고, 분석 단계에서는 파일을 읽어 쓰면 코드를 고칠 때마다 API를 다시 부르지 않아도 된다. 수업 노트 2-7의 "캐시로 한도 아끼기"를 실천하는 자리다.

## 3. 더 나아가 알면 좋은 것

### 3-1. 수집기 구조 — 함수로 나누기

```python
def fetch(page, per_page=100): ...          # 호출 + json → data 리스트
def collect_all(): ...                      # totalCount 반복 → DataFrame
def clean(df): ...                          # 열 선택 + to_numeric
def summarize(df): ...                      # groupby → 표
def plot(summary): ...                      # barplot
```

한 파일에 네 단계가 이어진 지금 모양을 함수 다섯 개로 쪼개면 각 단계를 따로 테스트하고 바꿀 수 있다. 수집기 프로젝트(학습 지도 매핑표 경유)가 사람인 API로 하는 일이 정확히 이 구조이고, `fetch`를 다른 API로 갈아 끼워도 나머지는 그대로다.

### 3-2. 실패에 대비하기 — 상태 코드·재시도·타임아웃

`httpx.get(url, timeout=10)`으로 무한 대기를 막고, `response.raise_for_status()`로 4xx·5xx를 예외로 바꿔 day04의 `try`/`except`로 받는다. 429(한도 초과)·5xx는 잠시 쉬었다 다시 시도하는 **지수 백오프**(1초 → 2초 → 4초)가 관례다. 무인으로 매일 도는 수집기라면 이 처리가 있느냐가 "가끔 멈추는 스크립트"와 "믿고 맡기는 프로그램"을 가른다.

### 3-3. 스키마 검증 — 열이 바뀌면 알아채기

공공데이터는 예고 없이 열 이름이 바뀌거나(`가격1` → `가격`) 새 열이 생기기도 한다. 받은 직후 `set(['업종', '업소명', '주소', '가격1']) <= set(df.columns)`로 필요한 열이 다 있는지 확인하거나, `pydantic` 모델로 행 하나의 형식을 선언해 두면 구조가 바뀐 날 조용히 틀린 평균을 내는 대신 바로 오류로 알 수 있다.

### 3-4. 주소에서 지역 뽑기 — 문자열 분리와 지도

`주소` 열의 앞 두 어절(`df['주소'].str.split().str[:2]`)을 시도·시군구로 뽑으면 업종별 평균을 지역별로도 자를 수 있다. 공공데이터의 주소는 표기가 제각각이라 정규식 정리가 필요하고, 좌표가 있으면 `folium`으로 지도 위에 찍는 것이 다음 단계다. 지역 × 업종 두 축의 평균은 `pivot_table`이 한 줄로 만든다.

### 3-5. 데이터베이스에 적재 — 업서트

매일 받은 업소 목록을 CSV로 쌓기보다 SQLite·MySQL에 넣고, 같은 업소가 다시 오면 덮어쓰는 **업서트**로 저장하면 중복 없이 최신 상태가 유지된다. 수업 노트 3-5에서 예고한 멱등성 이야기이고, 수집기 프로젝트의 SQLite 저장 계층이 바로 이 역할이다.

### 3-6. 다음에 볼 키워드

- `perPage=100`으로 N건 요청 · `page`/`totalCount`로 전체 수집 · `params=` 딕셔너리와 인코딩/디코딩 키 · `.env`/`python-dotenv`
- `response.json()['data']` → `DataFrame` · 이중 대괄호 열 선택 · 공공데이터의 문자열 숫자
- `pd.to_numeric(errors='coerce')` · `NaN`과 `mean()` · `isna().sum()` · 여러 가격 열 `apply(to_numeric)`
- `groupby().mean()` 시리즈 → `.index`/`.values`로 `barplot` · `sns.set_theme(font=)` 폰트 재지정 · `errorbar=None`·가로 막대·`xticks(rotation)`
- `agg` 업소 수+평균+중앙값 · `sort_values`·`order=` · `to_csv` 캐시 · 함수 분리 · `timeout`·`raise_for_status`·백오프 · 스키마 검증 · 주소 분리·`pivot_table`·업서트

## 실습 파일

- `KDT_2026/2026_Python/practice/practice8.py` — API 데이터 수집 연습: 지문 주석(행정안전부 착한가격업소 현황·httpx 호출·pandas 구조화·통계 분석, 2-1 인증키 포함 100건 / 2-2 `data` 배열 → DataFrame / 2-3 `가격1` `to_numeric`·평균 / 2-4 `groupby('업종')` 평균 + `barplot`), odcloud 주소 고정 부분 + `?page=1`·`&perPage=100`·`&serviceKey=` f-문자열 조립(키 값은 노트에서 가림), `httpx.get` → `print(response)` → `.json()` → `pd.DataFrame(response_json['data'])` → `info()`, `df[['업종', '업소명', '주소', '가격1']]` 네 열 선택 → `head()`, `pd.to_numeric(df['가격1'], errors="coerce")` → `mean()` 출력, `df.groupby('업종')['가격1'].mean()` → 한글 변수 `업종별평균`, `plt.rc` 두 줄 + `sns.set_theme(font='Malgun Gothic', rc=…, style='whitegrid')`, `sns.barplot(x=index, y=values)` → `title`·`xlabel`·`ylabel`·`show`

## 관련 노트

[[Python 정리본 인덱스]] · [[Python day11 httpx로 공공데이터 API 호출과 JSON 데이터프레임 변환]] · [[Python day12 사이킷런 단순 선형 회귀로 물고기 무게 예측]] · [[Python day08 판다스 데이터 전처리 중복 제거와 타입 변환]] · [[Python day09 시본 범주 빈도·박스플롯·상관 히트맵]] · [[Python day09 따릉이 대여이력 EDA 실습]] · [[Python day10 페이징 반복으로 베스트셀러 목록 크롤링]] · [[KDT_2026 학습 지도]]
