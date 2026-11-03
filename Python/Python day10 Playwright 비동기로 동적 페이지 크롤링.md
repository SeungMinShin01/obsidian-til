---
출처: Claude 분석
원본: KDT_2026/2026_Python/day10/c-03.py
작성일: 2026-11-02
tags: [학습, python]
---

# Python day10 — Playwright 비동기로 동적 페이지 크롤링

> 실습 파일: `day10/c-03.py`
> 허브: [[Python 정리본 인덱스]] · 이전: [[Python day10 페이징 반복으로 베스트셀러 목록 크롤링]] · 다음: [[Python day10 Playwright 클릭으로 동적 페이지네이션 크롤링 실습]]

앞의 두 예제는 `requests`로 HTML을 한 번 받아 오면 끝이었다. 세 번째 예제는 그 방식이 통하지 않는 페이지를 다룬다. 네이버 이미지 검색 결과는 처음 받은 HTML에 사진이 거의 없고, **스크롤을 내릴 때마다 자바스크립트가 사진을 더 불러온다**. 그래서 진짜 브라우저(크로미움)를 코드로 띄워 놓고, 사람이 하듯 페이지를 열고 → 기다리고 → 스크롤하고 → 그려진 결과를 집는다. 이 일을 맡는 것이 `Playwright`이고, 브라우저와 주고받는 동작이 전부 비동기라 `asyncio`·`async`·`await`가 함께 들어온다.

## 1. 배운 내용

### 1-1. 설치 — 라이브러리와 브라우저, 두 번

```bash
pip install playwright      # 셀레니움과 비슷한 동적 페이지 조작 라이브러리
playwright install          # 백그라운드용 브라우저(크로미움) 설치
```

`pip install`로 끝나지 않는 점이 다르다. 파이썬 패키지는 "브라우저를 조종하는 코드"일 뿐이고, 조종당할 **브라우저 자체**는 두 번째 명령으로 따로 내려받는다. 크로미움은 구글이 공개한 오픈소스 브라우저로, 크롬의 뼈대다. 설치 뒤 `from playwright.async_api import async_playwright`가 되면 준비가 끝난 것이다.

### 1-2. 정적 크롤링과 무엇이 다른가

| 구분 | 정적 (`requests` + `BeautifulSoup`) | 동적 (`Playwright`) |
| --- | --- | --- |
| 받아 오는 것 | 서버가 보낸 HTML 문자열 | 브라우저가 **실행까지 마친** 화면의 DOM |
| 자바스크립트 | 실행되지 않음 | 브라우저가 실행함 |
| 스크롤·클릭·대기 | 불가 | `evaluate`·`click`·`wait_for_timeout` |
| 선택자 | `select` / `select_one` | `query_selector_all` / `query_selector` |
| 텍스트·속성 | `get_text()` / `tag["src"]` | `inner_text()` / `get_attribute("src")` |
| 속도·무게 | 빠르고 가벼움 | 브라우저를 띄우므로 느리고 무거움 |

요청 → 파싱 → 추출의 뼈대는 그대로이고, 가운데 "파싱"이 **브라우저가 대신 그려 주는 단계**로 바뀐 것이라고 보면 된다. 그래서 첫 예제에서 정리한 "정적으로 안 되면 동적으로"가 바로 이 자리다.

### 1-3. 주소 분석 — 탭과 검색어 파라미터

```text
https://search.naver.com/search.naver?ssc=tab.image.all&query=짱구
```

| 파라미터 | 뜻 |
| --- | --- |
| `ssc` | 검색 결과 탭 — `tab.image.all`이 이미지 탭 |
| `query` | 검색어 |

페이징 예제의 `pageNumber`처럼, 여기서도 바뀌는 자리는 `query` 하나다. 검색어를 변수로 빼면 어떤 단어든 같은 코드로 돌릴 수 있다.

### 1-4. 전체 흐름 — 비동기 함수 하나로 감싸기

```python
import asyncio
from playwright.async_api import async_playwright

url = "https://search.naver.com/search.naver?ssc=tab.image.all&query=짱구"

async def run():
    item_list = []
    async with async_playwright() as p:                       # 2-1) 플레이라이트 켜고 끝나면 끄기
        browser = await p.chromium.launch(headless=False)     # 2-2) 크로미움 띄우기
        page = await browser.new_page()                       # 2-3) 빈 탭 열기
        await page.goto(url)                                  # 2-4) 주소로 이동
        for i in range(2):                                    # 3) 스크롤 두 번
            await page.wait_for_timeout(3000)                 #    3초 대기
            await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            items = await page.query_selector_all(".tile_item")      # 4) 사진 카드 전부
            for item in items:                                       # 5) 카드 안에서 제목·이미지
                title = await item.query_selector('.info_title')
                title = await title.inner_text() if title else '제목없음'
                img = await item.query_selector('img._fe_image_tab_content_thumbnail_image')
                img = await img.get_attribute('src') if img else '이미지없음'
                item_list.append({'제목': title, '이미지링크': img})
    return item_list

item_list = asyncio.run(run())
print(item_list)
```

| 단계 | 코드 | 하는 일 |
| --- | --- | --- |
| 2-1 | `async with async_playwright() as p` | 플레이라이트를 켜고, 블록을 빠져나가면 브라우저까지 정리 |
| 2-2 | `await p.chromium.launch(headless=False)` | 크로미움 실행. `False`면 창이 보이고 `True`면 백그라운드 |
| 2-3 | `await browser.new_page()` | 새 탭(빈 페이지) 하나 |
| 2-4 | `await page.goto(url)` | 그 탭에 주소를 넣어 이동 |
| 3 | `wait_for_timeout` → `evaluate(scrollTo)` | 기다렸다가 맨 아래로 스크롤 — 두 번 반복 |
| 4 | `await page.query_selector_all(".tile_item")` | 사진 한 장 단위 카드 전부 |
| 5 | `item.query_selector(…)` → `inner_text()` / `get_attribute('src')` | 카드 안에서 제목 글자와 이미지 주소 |

### 1-5. `async`·`await`·`asyncio.run` — 세 글자의 역할

브라우저에 "페이지 열어" 하고 시키면 실제로 열리기까지 시간이 걸린다. 그 사이 파이썬이 다음 줄로 넘어가 버리면 아직 안 그려진 화면에서 요소를 찾게 된다. 그래서 브라우저 관련 함수는 전부 **"기다려야 하는 함수"(코루틴)**로 되어 있고, 호출하는 쪽이 `await`를 붙여 **끝날 때까지 여기서 멈춰라**고 적는다.

| 글자 | 어디에 | 뜻 |
| --- | --- | --- |
| `async def run()` | 함수 선언 앞 | 이 함수 안에서 `await`를 쓰겠다는 선언. 호출해도 바로 실행되지 않고 "할 일(코루틴)"이 만들어진다 |
| `await 코루틴` | 기다릴 호출 앞 | 그 일이 끝날 때까지 멈추고, 끝나면 결과를 받는다. `async` 함수 안에서만 쓸 수 있다 |
| `asyncio.run(run())` | 맨 바깥 | 이벤트 루프를 열어 `run()`을 처음부터 끝까지 돌리고 반환값을 받는다. 보통 프로그램당 한 번 |

수업 주석의 표현을 빌리면 "비동기 페이지들을 동기화로 제어하는 함수"다. 브라우저 쪽은 비동기로 돌지만, 코드를 읽는 순서대로 한 줄씩 결과를 받아 쓰도록 `await`가 줄을 세워 준다. 그래서 `await`를 빼먹으면 값 대신 코루틴 객체가 들어와 `.inner_text()` 같은 다음 호출에서 어긋난다 — 플레이라이트 함수 앞에는 거의 전부 `await`가 붙는다고 보는 편이 안전하다. React 수업에서 서버 응답을 `await axios.get(…)`으로 받던 것과 같은 짝이다(그쪽 노트는 허브·지도 경유).

### 1-6. `async with` — 켠 것을 반드시 끄는 블록

```python
async with async_playwright() as p:
    ...
```

day04에서 파일을 `with open(...)`으로 열면 블록이 끝날 때 자동으로 닫혔던 것과 같은 문법의 비동기판이다. 브라우저는 프로세스를 하나 띄우는 무거운 자원이라, 예외가 나든 정상 종료하든 블록을 빠져나가면 플레이라이트가 정리된다. `browser.close()`를 따로 안 부르는 이유가 이것이다.

### 1-7. `headless` — 보면서 할지, 숨겨서 돌릴지

`launch(headless=False)`는 크로미움 창이 실제로 뜨고 스크롤이 내려가는 것이 눈에 보인다. 선택자가 맞는지, 몇 초를 기다려야 사진이 뜨는지 확인하기 좋다. 다 맞춘 뒤 `headless=True`(기본값)로 바꾸면 창 없이 백그라운드로 돈다 — 예약 실행이나 서버에서는 이쪽이다.

### 1-8. 스크롤 — `evaluate`로 자바스크립트 심기

```python
await page.wait_for_timeout(3000)
await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
```

`evaluate`는 문자열로 넘긴 **자바스크립트 코드를 페이지 안에서 실행**한다. 개발자도구 콘솔에 치는 것과 같다. `window.scrollTo(가로, 세로)`가 스크롤 이동 함수이고, `document.body.scrollHeight`가 문서 전체의 세로 높이라 둘을 합치면 "맨 아래로"가 된다. 스크롤이 바닥에 닿으면 네이버가 다음 묶음을 불러오므로, `range(2)`로 두 번 돌리면 사진이 두 번 늘어난다.

`wait_for_timeout(3000)`은 3000밀리초, 즉 3초를 그냥 기다리는 함수다. 불러오는 데 시간이 걸리니 먼저 기다리고 스크롤하는 순서다. 수업에서는 이렇게 고정 시간을 썼는데, 2-2에서 더 나은 방법을 정리한다.

### 1-9. 카드 안에서 다시 찾기 — `query_selector_all` → `query_selector`

```python
items = await page.query_selector_all(".tile_item")
for item in items:
    title = await item.query_selector('.info_title')
    img = await item.query_selector('img._fe_image_tab_content_thumbnail_image')
```

`.tile_item`이 사진 한 장과 제목을 함께 감싸는 카드다. `query_selector_all`로 카드 리스트를 받고, 카드 하나(`item`)에서 `query_selector`로 제목과 이미지를 찾는다. 페이징 예제의 `select` → `select_one`과 **완전히 같은 구조**이고, 이유도 같다 — 한 카드에서 꺼내야 제목과 이미지 링크가 같은 사진의 것임이 보장된다. 이름만 바뀐다.

| BeautifulSoup | Playwright | 뜻 |
| --- | --- | --- |
| `soup.select(".a")` | `await page.query_selector_all(".a")` | 전부 → 리스트 |
| `tag.select_one(".a")` | `await item.query_selector(".a")` | 첫 하나 → 없으면 `None` |
| `tag.get_text()` | `await tag.inner_text()` | 태그 사이 글자(`innerText`) |
| `tag["src"]` / `tag.get("src")` | `await tag.get_attribute("src")` | 속성값 |

선택자 `img._fe_image_tab_content_thumbnail_image`는 "img 태그이면서 그 클래스"라는 뜻으로, 첫 예제에서 정리한 CSS 선택자 그대로다. 개발자도구 `Ctrl+Shift+C`로 사진을 찍어 클래스 이름을 확인한 것이다.

### 1-10. `None` 방어를 한 줄로 — 조건부 표현식

```python
title = await title.inner_text() if title else '제목없음'
img = await img.get_attribute('src') if img else '이미지없음'
```

`query_selector`는 못 찾으면 `None`을 돌려주고, `None`에 `.inner_text()`를 부르면 오류다. 그래서 `A if 조건 else B` 꼴의 **조건부 표현식**으로 "있으면 글자를 꺼내고, 없으면 기본 문자열"을 한 줄에 적었다. 페이징 예제에서 "값이 빠진 카드 방어"로 따로 함수를 만들었던 그 일을 문법 하나로 처리한 모양이다. `await`가 `if` 앞쪽 식에만 걸린다는 점도 눈여겨볼 만하다 — `None`일 때는 `await`할 것이 없으니 바로 `'제목없음'`이 된다.

### 1-11. 결과 모양과 중복

반복 두 바퀴마다 `query_selector_all`을 **처음부터 다시** 하므로, 첫 바퀴에서 담은 카드가 두 번째 바퀴에 다시 들어온다. 결과 리스트에는 같은 사진이 두 번 들어갈 수 있다. 수업 코드는 이걸 그대로 출력하는 데까지이고, 중복 정리는 2-3에서 다룬다. 결과는 여전히 "리스트 안의 딕셔너리"라 `pd.DataFrame(item_list)`에 그대로 들어간다.

## 2. 추가로 알면 좋은 활용법

### 2-1. 검색어를 변수로 — 쿼리스트링 인코딩

```python
from urllib.parse import quote
keyword = "짱구"
url = f"https://search.naver.com/search.naver?ssc=tab.image.all&query={quote(keyword)}"
```

주소에 한글을 그대로 넣어도 플레이라이트가 알아서 인코딩해 주지만, 공백·`&` 같은 글자가 섞이면 깨질 수 있다. `quote`로 `%EC%A7%B1%EA%B5%AC`처럼 바꿔 넣는 것이 원칙이다. `requests`의 `params=`가 해 주던 일을 직접 하는 셈이다.

### 2-2. 고정 대기 대신 조건 대기

```python
await page.wait_for_selector(".tile_item")                 # 카드가 나타날 때까지
await page.wait_for_load_state("networkidle")              # 네트워크 요청이 잠잠해질 때까지
```

`wait_for_timeout(3000)`은 느린 날은 모자라고 빠른 날은 낭비다. 플레이라이트에는 "그 요소가 뜰 때까지", "요청이 멎을 때까지"처럼 **조건이 충족될 때까지** 기다리는 함수가 있고, 기본 타임아웃(30초) 안에 안 되면 예외를 던진다. 스크롤 뒤 `wait_for_selector`로 카드 개수가 늘어난 것을 확인하는 식으로 바꾸면 더 안정적이다.

### 2-3. 스크롤 반복을 "더 안 늘어날 때까지"로 — 그리고 중복 제거

```python
prev = 0
while True:
    await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
    await page.wait_for_timeout(2000)
    items = await page.query_selector_all(".tile_item")
    if len(items) == prev or len(items) >= 200:    # 더 안 늘거나 충분하면 종료
        break
    prev = len(items)
# 반복이 끝난 뒤 한 번만 추출 → 중복이 생기지 않는다
```

스크롤 횟수를 `range(2)`로 박는 대신, 카드 수가 더 늘지 않을 때 멈추는 `while True` + `break`다(페이징 예제의 "페이지 수 자동 종료"와 같은 발상). 추출을 **반복이 끝난 뒤 한 번**만 하면 1-11의 중복 문제도 사라진다. 이미 담은 것을 거르고 싶다면 이미지 주소를 `set`에 넣어 `if img in seen: continue`로 막거나, 데이터프레임으로 바꾼 뒤 day08의 `drop_duplicates(subset="이미지링크")`로 정리한다.

### 2-4. `locator` — 요즘 권장되는 API

```python
cards = page.locator(".tile_item")
count = await cards.count()
for i in range(count):
    card = cards.nth(i)
    title = await card.locator(".info_title").inner_text()
    img = await card.locator("img").first.get_attribute("src")
```

`query_selector`는 그 순간의 요소를 잡는 반면, `locator`는 **선택자 자체를 들고 있다가** 쓸 때마다 다시 찾는다. 스크롤로 DOM이 바뀌어도 낡은 참조가 되지 않고, 자동 대기가 붙어 있어 요소가 뜰 때까지 알아서 기다린다. 공식 문서가 새 코드에는 `locator`를 권한다. 다만 `inner_text()`는 요소가 없으면 예외라, `count()`로 먼저 확인하거나 `text_content()`에 `try`를 두는 식으로 방어한다.

### 2-5. 이미지를 파일로 저장하기

```python
import requests, os
os.makedirs("imgs", exist_ok=True)
for i, d in enumerate(item_list):
    if d["이미지링크"].startswith("http"):
        r = requests.get(d["이미지링크"], timeout=5)
        with open(f"imgs/{i:03d}.jpg", "wb") as f:
            f.write(r.content)
```

이미지 주소를 모았으니 실제 파일로 내려받는 것은 `requests`가 더 간단하다. `r.content`가 바이트라 `"wb"`로 연다. 썸네일 주소에 `data:image/…`처럼 base64가 들어 있는 경우가 있어 `startswith("http")`로 거른다.

### 2-6. 동기 API와 `headless=True`

```python
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto(url)
    items = page.query_selector_all(".tile_item")
```

`async`·`await`가 아직 낯설면 `sync_api`가 있다. 함수 이름은 전부 같고 `await`만 빠진다. 크롤러 하나만 돌린다면 동기판으로 충분하고, 여러 페이지를 **동시에** 열어야 할 때 비동기판의 이점이 드러난다 — 3-1에서 이어서 본다. `headless=True`는 창을 안 띄워 빠르고, 서버처럼 화면이 없는 곳에서도 돈다.

## 3. 더 나아가 알면 좋은 것

### 3-1. 비동기의 진짜 쓸모 — `asyncio.gather`로 동시에

```python
async def crawl(keyword):
    ...  # 위의 run()을 검색어 받는 함수로
results = asyncio.run(asyncio.gather(crawl("짱구"), crawl("도라에몽"), crawl("코난")))
```

지금 코드는 `await`로 줄을 세워 사실상 순서대로 돈다. `asyncio.gather`에 코루틴 여러 개를 넘기면 한 페이지가 로딩되는 동안 다른 페이지도 진행해 전체 시간이 크게 준다. 이것이 `async_api`를 쓰는 이유다. 다만 탭을 너무 많이 열면 브라우저 메모리가 금방 차고 사이트에도 부담이니, `asyncio.Semaphore`로 동시 개수를 제한한다.

### 3-2. 셀레니움과 플레이라이트

둘 다 "진짜 브라우저를 코드로 조종한다"는 점은 같다. 셀레니움은 오래됐고 자료가 많으며 브라우저별 드라이버를 맞춰야 한다. 플레이라이트는 마이크로소프트가 만들었고 설치가 `playwright install` 한 번, 크로미움·파이어폭스·웹킷을 같은 API로 다루며 자동 대기와 네트워크 가로채기(`page.route`)가 기본으로 들어 있다. 새로 배운다면 플레이라이트 쪽이 덜 번거롭다.

### 3-3. 브라우저를 띄우기 전에 — Network 탭 먼저

무한 스크롤은 대개 뒤에서 JSON API를 부른다. 개발자도구 Network 탭에서 스크롤할 때 생기는 XHR/Fetch 요청을 찾아 그 주소를 `requests.get` → `.json()`으로 받으면 브라우저 없이 훨씬 빠르게 같은 데이터를 얻는다. 플레이라이트는 그 API가 숨겨져 있거나 서명·토큰이 붙어 재현이 어려울 때의 다음 수단이다. 순서는 **공개 API → 숨은 JSON → 정적 파싱 → 브라우저 자동화**가 바람직하다.

### 3-4. 자동화 탐지와 예의

브라우저 자동화는 사이트 쪽에서도 알아챌 수 있다(`navigator.webdriver`, 요청 패턴). `robots.txt`와 이용약관을 먼저 보고, 요청 간격을 두고, 필요한 만큼만 가져오는 것이 원칙이다. 검색 결과 이미지는 각각 저작권이 있으므로 수집한 파일을 어디에 쓸 수 있는지도 따로 생각해야 한다.

### 3-5. 다음에 볼 키워드

- `async def`·`await`·`asyncio.run`·`asyncio.gather`·`Semaphore` · 코루틴·이벤트 루프 · `sync_api`
- `launch(headless=)`·`new_context()`(쿠키·뷰포트·User-Agent)·`new_page()`·`goto`·`close`
- `wait_for_selector`·`wait_for_load_state("networkidle")`·`wait_for_timeout`·기본 타임아웃 30초
- `evaluate`·`window.scrollTo`·`scrollHeight` · `mouse.wheel`·`keyboard.press("End")`
- `query_selector(_all)`·`locator`·`nth`·`count`·`inner_text`·`text_content`·`get_attribute`
- `click`·`fill`·`press`·`screenshot`·`pdf` · `page.route` 네트워크 가로채기·`response.json()`
- `urllib.parse.quote` · 이미지 다운로드 `"wb"`·`r.content` · `set`으로 중복 제거·`drop_duplicates`
- Selenium·`webdriver`·`navigator.webdriver` · Scrapy + playwright 플러그인 · 도커에서 크로미움

## 실습 파일

- `KDT_2026/2026_Python/day10/c-03.py` — 네이버 이미지 검색(`ssc=tab.image.all&query=짱구`) 동적 크롤링: `pip install playwright`·`playwright install` 주석, `import asyncio`·`from playwright.async_api import async_playwright`, `async def run()` 안에서 `async with async_playwright() as p` → `await p.chromium.launch(headless=False)` → `await browser.new_page()` → `await page.goto(url)`, `for i in range(2)`로 `wait_for_timeout(3000)` → `evaluate("window.scrollTo(0, document.body.scrollHeight)")` → `query_selector_all(".tile_item")` → 카드마다 `query_selector('.info_title')`의 `inner_text()`·`query_selector('img._fe_image_tab_content_thumbnail_image')`의 `get_attribute('src')`를 `if … else` 조건부 표현식으로 `None` 방어, `{'제목', '이미지링크'}` 딕셔너리 `append`, `asyncio.run(run())`으로 실행해 `print`

## 관련 노트

[[Python 정리본 인덱스]] · [[Python day10 페이징 반복으로 베스트셀러 목록 크롤링]] · [[Python day10 Playwright 클릭으로 동적 페이지네이션 크롤링 실습]] · [[Python day10 requests·BeautifulSoup으로 정적 페이지 크롤링]] · [[Python day04 예외 처리 try·except·else·finally]] · [[Python day08 판다스 데이터 전처리 중복 제거와 타입 변환]] · [[KDT_2026 학습 지도]]
