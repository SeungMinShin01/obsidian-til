---
출처: Claude 분석
원본: KDT_2026/2026_Python/day10/c-02.py
작성일: 2026-11-02
tags: [학습, python]
---

# Python day10 — 페이징 반복으로 베스트셀러 목록 크롤링

> 실습 파일: `day10/c-02.py`
> 허브: [[Python 정리본 인덱스]] · 이전: [[Python day10 requests·BeautifulSoup으로 정적 페이지 크롤링]] · 다음: [[Python day10 Playwright 비동기로 동적 페이지 크롤링]]

첫 예제가 값 하나를 뽑는 것이었다면, 두 번째 예제는 **여러 페이지에 걸친 목록**을 긁어 모은다. 예스24 일간 베스트셀러를 1~3페이지까지 돌며 책마다 제목·가격·저자를 딕셔너리로 묶어 리스트에 쌓는다. 요청 → 파싱 → 추출의 뼈대는 그대로이고, 거기에 **페이지 반복**과 **묶음 안에서 다시 추출**이라는 두 층이 얹힌다.

## 1. 배운 내용

### 1-1. 주소 분석 — 바뀌는 자리를 파라미터로 보기

```text
https://www.yes24.com/product/category/daybestseller?categoryNumber=001&pageNumber=1
```

브라우저에서 2페이지를 눌러 보면 `pageNumber=2`로만 바뀐다. 주소를 "고정 부분 + 바뀌는 파라미터"로 쪼개 읽는 것이 페이징 크롤링의 출발점이다.

| 파라미터 | 뜻 | 값 |
| --- | --- | --- |
| `categoryNumber` | 분류 | `001` 국내도서 · `002` 외국도서 |
| `pageNumber` | 페이지 번호 | 1, 2, 3, … |

```python
for page in range(1, 4):
    url = f"https://www.yes24.com/product/category/daybestseller?pageNumber={page}&categoryNumber=001"
```

`range(1, 4)`는 끝 미포함이라 1·2·3 세 페이지다. f-문자열의 `{page}` 자리에 반복 변수가 들어가면서 주소가 세 번 만들어진다. 파라미터 순서는 바뀌어도 상관없다 — 서버는 이름으로 읽는다.

### 1-2. 여섯 단계 흐름

```python
import requests
from bs4 import BeautifulSoup

book_list = []                                     # 결과 누적 — 반복문 바깥
for page in range(1, 4):
    url = f"…?pageNumber={page}&categoryNumber=001"   # 1) 주소 조립
    response = requests.get(url)                   # 2) URL 요청
    soup = BeautifulSoup(response.text, "html.parser")   # 3) HTML 파싱
    books = soup.select(".item_info")              # 4) 책 카드 여러 개 추출
    for book in books:                             # 5) 카드 하나 안에서 다시 추출
        title = book.select_one('.gd_name').get_text()
        price = book.select_one('.yes_b').get_text()
        auth = book.select_one('.info_auth').get_text().strip().replace("\n", "").replace("\r", "")
        book_list.append({"제목": title, "가격": price, "저자": auth})   # 6) 리스트에 담기
print(book_list)
```

| 단계 | 코드 | 지난 예제와 비교 |
| --- | --- | --- |
| 1 | f-문자열로 주소 조립 | 고정 주소 → 반복 변수가 들어간 주소 |
| 2 | `requests.get(url)` | 같음 |
| 3 | `BeautifulSoup(response.text, "html.parser")` | 같음 |
| 4 | `soup.select(".item_info")` | `select_one` 하나 → `select` **여러 개(리스트)** |
| 5 | `book.select_one('.gd_name')` … | `soup`가 아니라 **카드 태그**에서 다시 `select_one` |
| 6 | `book_list.append({…})` | 새로 생김 — 딕셔너리로 묶어 누적 |

### 1-3. 이중 반복 — 바깥은 페이지, 안쪽은 책

바깥 `for page`가 한 바퀴 돌 때마다 안쪽 `for book`이 그 페이지의 책 수만큼 돈다. day03 구구단의 이중 반복과 같은 구조인데, 여기서는 바깥 한 바퀴가 "요청 한 번"이고 안쪽 한 바퀴가 "책 한 권"이다. `book_list`를 바깥 반복문 **밖**에 선언했기 때문에 세 페이지의 결과가 한 리스트에 이어서 쌓인다. 안에 두면 페이지마다 초기화돼 마지막 페이지만 남는다.

### 1-4. 묶음 안에서 다시 `select_one` — 짝을 맞추는 방법

`.item_info`는 책 한 권의 정보 카드다. `soup.select(".item_info")`로 카드들을 리스트로 받은 뒤, 카드 하나(`book`)를 기준으로 그 **안에서만** `.gd_name`(제목)·`.yes_b`(가격)·`.info_auth`(저자)를 찾는다. `select_one`은 `soup`뿐 아니라 어떤 태그 객체에서도 부를 수 있고, 검색 범위가 그 태그의 자손으로 좁혀진다.

이렇게 하는 이유가 중요하다. 전체 `soup`에서 제목 리스트·가격 리스트·저자 리스트를 따로 세 번 `select`해서 인덱스로 짝지을 수도 있지만, 어느 책 하나에 가격 태그가 빠져 있으면 그 뒤로 짝이 전부 한 칸씩 밀린다. 카드 단위로 묶어서 안에서 꺼내면 한 권의 제목·가격·저자가 **같은 카드에서 나왔다는 것이 보장**된다.

### 1-5. 저자 문자열 정리 — `strip`과 `replace` 체이닝

```python
auth = book.select_one('.info_auth').get_text().strip().replace("\n", "").replace("\r", "")
```

저자 칸은 마크업 안에 줄바꿈과 들여쓰기가 섞여 있어 `get_text()` 결과에 `\n`·`\r`·공백이 따라 나온다. `.strip()`이 앞뒤 공백·줄바꿈을 떼고, `.replace("\n", "")`·`.replace("\r", "")`가 **중간**에 남은 줄바꿈까지 지운다. `\r\n`은 윈도우식 줄바꿈이라 둘 다 지워야 깨끗해진다. 문자열 메소드는 모두 새 문자열을 돌려주므로 점으로 이어 붙일 수 있다 — day01에서 본 `upper`·`strip`이 그대로 쓰인 자리다.

### 1-6. 결과 모양 — 리스트 안의 딕셔너리

```python
[
  {"제목": "…", "가격": "…", "저자": "…"},
  {"제목": "…", "가격": "…", "저자": "…"},
  …
]
```

"딕셔너리 하나 = 책 한 권, 리스트 = 전체 목록"이다. day02 딕셔너리 노트에서 "리스트 안의 딕셔너리는 API 응답 모양"이라고 정리했던 그 형태이고, day08에서 `pd.DataFrame(딕셔너리 리스트)`에 바로 넣었던 바로 그 재료다. 키 이름을 한글 `"제목"`·`"가격"`·`"저자"`로 두었으니 데이터프레임으로 바꾸면 그대로 열 이름이 된다.

## 2. 추가로 알면 좋은 활용법

### 2-1. 데이터프레임으로 받아 저장하기

```python
import pandas as pd
df = pd.DataFrame(book_list)
df.to_csv("bestseller.csv", index=False, encoding="utf-8-sig")
```

크롤링의 끝은 거의 항상 저장이다. `utf-8-sig`로 저장하면 엑셀에서 열어도 한글이 깨지지 않는다 — day07에서 공공데이터를 읽을 때 봤던 BOM 이야기의 반대 방향이다.

### 2-2. 가격을 숫자로 바꾸기

```python
price_text = "15,300원"
price = int(price_text.replace(",", "").replace("원", ""))   # 15300
```

`get_text()`로 받은 가격은 문자열이라 그대로는 합계·정렬이 안 된다. 쉼표와 단위를 지운 뒤 `int()`로 바꿔 두면 `sort_values`·`mean`이 바로 된다. 판다스라면 `df["가격"].str.replace(r"[^0-9]", "", regex=True).astype(int)` 한 줄로 열 전체를 처리할 수 있다.

### 2-3. 공백 정리의 다른 표현

```python
auth = book.select_one('.info_auth').get_text(strip=True)   # 앞뒤만
auth = " ".join(book.select_one('.info_auth').get_text().split())   # 중간 공백·줄바꿈 전부 한 칸으로
```

`split()`은 인수 없이 부르면 공백·탭·줄바꿈을 모두 구분자로 보고 빈 조각을 버린다. 그 결과를 `" ".join`으로 다시 붙이면 `replace`를 여러 번 체이닝하지 않아도 된다. "저자 외 2명" 같은 구분 공백은 살리고 싶을 때 이 방식이 낫다.

### 2-4. 순위 붙이기와 페이지 수 자동 종료

```python
rank = 0
page = 1
while True:
    soup = BeautifulSoup(requests.get(f"…pageNumber={page}…").text, "html.parser")
    books = soup.select(".item_info")
    if not books:          # 더 이상 책이 없으면 끝
        break
    for book in books:
        rank += 1
        book_list.append({"순위": rank, …})
    page += 1
    time.sleep(1)          # 요청 간격
```

페이지 수를 미리 모를 때는 `for range` 대신 `while True`로 돌다가 `select` 결과가 비면 `break`한다 — day02에서 정리한 "횟수를 모를 때 `while`"이 그대로다. `rank`를 바깥에서 세면 페이지가 넘어가도 순위가 이어진다. 요청 사이 `time.sleep`은 서버를 배려하는 최소한의 예의다.

### 2-5. 값이 빠진 카드 방어

```python
def text_of(tag, selector):
    found = tag.select_one(selector)
    return found.get_text(strip=True) if found else ""
title = text_of(book, ".gd_name")
```

카드에 따라 특정 태그가 없으면 `select_one`이 `None`을 돌려주고 `.get_text()`에서 `AttributeError`가 난다. 작은 함수로 감싸 두면 세 줄이 한 모양으로 정리되고, 빈 값은 나중에 판다스에서 `replace("", None)`으로 결측 처리할 수 있다.

### 2-6. `requests.Session`과 `params`

```python
with requests.Session() as s:
    s.headers.update({"User-Agent": "Mozilla/5.0"})
    for page in range(1, 4):
        r = s.get("https://www.yes24.com/product/category/daybestseller",
                  params={"categoryNumber": "001", "pageNumber": page}, timeout=5)
```

같은 사이트에 여러 번 요청할 때는 `Session`이 연결과 헤더·쿠키를 재사용해 빠르고 간결하다. 파라미터는 `params` 딕셔너리로 넘기면 f-문자열로 주소를 조립하지 않아도 된다.

## 3. 더 나아가 알면 좋은 것

### 3-1. 페이지 번호가 없는 목록 — 무한 스크롤과 Ajax

주소에 `pageNumber`가 없고 스크롤할 때마다 목록이 늘어나는 사이트는 자바스크립트가 뒤에서 JSON을 받아 와 그린다. 개발자도구 Network 탭(XHR/Fetch 필터)에서 그 요청을 찾으면 `?page=2&size=20` 같은 파라미터가 보이고, 그 주소를 `requests.get` → `response.json()`으로 받으면 HTML 파싱 없이 딕셔너리로 바로 떨어진다. 그것도 안 되면 `Selenium`/`Playwright`로 스크롤을 흉내 내는 단계로 간다.

### 3-2. 수집 결과를 쌓을 때 — 중복과 멱등성

매일 베스트셀러를 긁어 모으면 같은 책이 날마다 다시 들어온다. 그냥 `append`하면 중복이 쌓이고, day08의 `drop_duplicates`로 지우는 것은 사후 처리다. 처음부터 "같은 키면 덮어쓰고 없으면 넣는" **업서트**로 저장하면 몇 번을 돌려도 결과가 같아진다. 실제 수집기 프로젝트에서 이 방식을 어떻게 썼는지는 [[KDT_2026 학습 지도]]의 프로젝트 매핑표를 거쳐 찾는다.

### 3-3. 크롤러를 프레임워크로 — Scrapy·비동기

페이지 수가 수백 장이 되면 `requests`를 순서대로 기다리는 방식은 느리다. `httpx`·`aiohttp`로 요청을 동시에 보내거나, `Scrapy`처럼 요청 큐·파이프라인·저장소가 갖춰진 프레임워크로 옮긴다. 다만 동시 요청은 서버 부담도 그만큼 커지므로 `robots.txt`의 `Crawl-delay`와 사이트 정책을 먼저 본다.

### 3-4. 다음에 볼 키워드

- `while True` + `break` 페이징 · `enumerate(start=1)` 순위 · `time.sleep`·`random.uniform` 간격
- `requests.Session`·`params`·`headers`·`timeout` · `response.json()` · Network 탭 XHR
- `get_text(strip=True)`·`" ".join(split())` · 정규식 `re.sub`·`str.replace(regex=True)` · `int()`·`astype`
- `pd.DataFrame(리스트)`·`to_csv(encoding="utf-8-sig")`·`to_json` · `sqlite3`·업서트·`drop_duplicates`
- `Selenium`·`Playwright`·무한 스크롤 · `Scrapy`·`httpx`·`aiohttp`·비동기
- `schedule`·cron·GitHub Actions 예약 실행 · 로깅·실패 재시도

## 실습 파일

- `KDT_2026/2026_Python/day10/c-02.py` — 예스24 일간 베스트셀러(`categoryNumber=001` 국내도서) 페이징 크롤링: `book_list = []` 바깥 선언, `for page in range(1, 4)`로 f-문자열 주소 조립, `requests.get` → `BeautifulSoup(…, "html.parser")`, `soup.select(".item_info")` 카드 목록, 카드마다 `select_one('.gd_name')`·`('.yes_b')`·`('.info_auth')`의 `get_text()`와 `.strip().replace("\n","").replace("\r","")` 정리, `{"제목", "가격", "저자"}` 딕셔너리 `append`, `print(book_list)`

## 관련 노트

[[Python 정리본 인덱스]] · [[Python day10 requests·BeautifulSoup으로 정적 페이지 크롤링]] · [[Python day10 Playwright 비동기로 동적 페이지 크롤링]] · [[Python day02 딕셔너리 선언과 키로 값 다루기]] · [[Python day02 range 함수와 for·while 반복문]] · [[Python day08 판다스 데이터 전처리 중복 제거와 타입 변환]] · [[KDT_2026 학습 지도]]
