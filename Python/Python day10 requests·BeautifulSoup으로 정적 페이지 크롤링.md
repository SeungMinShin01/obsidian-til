---
출처: Claude 분석
원본: KDT_2026/2026_Python/day10/c-01.py
작성일: 2026-11-02
tags: [학습, python]
---

# Python day10 — requests·BeautifulSoup으로 정적 페이지 크롤링

> 실습 파일: `day10/c-01.py`
> 허브: [[Python 정리본 인덱스]] · 이전: [[Python day09 따릉이 대여이력 EDA 실습]] · 다음: [[Python day10 페이징 반복으로 베스트셀러 목록 크롤링]]

지금까지는 CSV 파일을 받아서 분석했는데, 이번에는 데이터를 **웹페이지에서 직접 가져오는** 단계다. 수업 정의 그대로 적으면 웹 크롤링은 "웹페이지에 존재하는 데이터들을 수집하는 기술"이다. 첫 예제는 네이버 검색 결과 페이지에서 현재 온도 하나를 뽑아내는 것인데, 이 작은 예제 안에 요청 → 파싱 → 추출의 뼈대가 전부 들어 있다.

## 1. 배운 내용

### 1-1. 웹 크롤링의 전제와 라이브러리 두 갈래

크롤링은 HTML을 상대하는 일이라 HTML/CSS 기초 지식이 먼저다. 어떤 태그 안에 값이 있는지, 그 태그를 어떤 **선택자**로 집을지 알아야 하기 때문이다. 파이썬 쪽 라이브러리는 페이지의 성격에 따라 둘로 나뉜다.

| 구분 | 라이브러리 | 언제 쓰나 |
| --- | --- | --- |
| 정적 | `requests` + `BeautifulSoup` | 서버가 내려주는 HTML 안에 데이터가 이미 들어 있을 때 |
| 동적 | `Selenium`, `Playwright` | 자바스크립트가 실행된 뒤에야 데이터가 화면에 생길 때 (브라우저를 직접 띄워서 조작) |

이번 수업은 정적 쪽이다. 브라우저 없이 "주소를 요청해서 받은 HTML 문자열"만으로 끝난다.

### 1-2. 크롤링 전에 확인할 두 가지

**① robots.txt** — 크롤링할 사이트의 `도메인/robots.txt`에 접속하면 그 사이트가 수집 로봇에게 허용한 범위가 적혀 있다. 수업에서 본 예시는 `https://www.jobkorea.co.kr/robots.txt`다.

| 항목 | 뜻 |
| --- | --- |
| `User-agent:` | 규칙이 적용되는 대상 — 특정 브라우저·검색 로봇·AI 크롤러 이름, `*`는 전부 |
| `Disallow:` | 수집 불가 경로 |
| `Allow:` | 수집 가능 경로 |

**② 개발자도구로 선택자 찾기** — `F12`로 개발자도구를 열고 `Ctrl+Shift+C`를 누르면 화면의 요소를 클릭해 그 요소의 마크업으로 바로 이동한다. 거기서 클래스·아이디 같은 **식별자**를 읽어 두면 그것이 곧 `select`에 넣을 선택자가 된다.

### 1-3. 설치와 import 이름

```bash
pip install requests
pip install beautifulsoup4
```

```python
import requests                 # URL 요청 라이브러리
from bs4 import BeautifulSoup   # 요청된 URL의 HTML 파싱 라이브러리
```

설치 이름은 `beautifulsoup4`인데 import는 `bs4`에서 한다. 넘파이(`numpy` → `np`)처럼 "설치 이름 ≠ import 이름"인 경우라 한 번 외워 두는 편이 안전하다.

### 1-4. 다섯 단계 — 주소 → 요청 → 파싱 → 추출 → 텍스트

```python
# 1. 크롤링 주소 가져오기 — 파라미터 정리, ?쿼리스트링
url = "https://search.naver.com/search.naver?&query=안양날씨"

# 2. requests 라이브러리로 해당 주소 요청하기
response = requests.get(url)     # requests.get("요청할 주소")
# print(response)                # <Response [200]>  — HTTP 코드 200은 통신 정상
# print(response.text)           # 요청한 주소의 HTML을 문자열로

# 3. 요청 성공했으면 HTML 파싱하기
soup = BeautifulSoup(response.text, "html.parser")   # 문자열 → HTML 구조

# 4. 특정한 식별자(마크업)의 텍스트/정보 추출
text = soup.select_one(".temperature_text")
print(text)
# <div class="temperature_text"> <strong><span class="blind">현재 온도</span>14.9<span class="celsius">°</span></strong> </div>

# 5. 마크업 사이의 텍스트 추출
print(text.get_text())
```

| 단계 | 하는 일 | 손에 쥐는 것 |
| --- | --- | --- |
| 1 | 주소를 정리한다. `?` 뒤가 **쿼리스트링**이고 `query=안양날씨`가 검색어 파라미터 | `url` 문자열 |
| 2 | `requests.get(url)`로 서버에 요청 | `Response` 객체 (`[200]`이면 정상) |
| 3 | `response.text`(HTML 문자열)를 `BeautifulSoup(…, "html.parser")`에 넣어 구조로 변환 | `soup` 객체 |
| 4 | `soup.select_one(선택자)`로 원하는 마크업 하나를 집는다 | 태그 객체 |
| 5 | `.get_text()`로 태그 사이의 글자만 꺼낸다 | 문자열 |

핵심은 3단계다. `response.text`는 그냥 긴 문자열이라 거기서 "클래스가 temperature_text인 div"를 찾을 방법이 없다. `BeautifulSoup`이 그 문자열을 태그 트리로 바꿔 주기 때문에 CSS 선택자로 집을 수 있게 된다. 파싱한 이유가 곧 4단계다.

### 1-5. `select` vs `select_one`

| 메소드 | 반환 | 쓰는 때 |
| --- | --- | --- |
| `soup.select(선택자)` | 일치하는 태그 **전부**를 리스트로 | 목록(책 여러 권, 글 여러 개) |
| `soup.select_one(선택자)` | 일치하는 **첫 번째** 태그 하나 | 값 하나(온도, 제목) |

선택자 문법은 CSS와 같다. `.temperature_text`는 클래스, `#id`는 아이디, `div > span`은 자식, `ul li`는 자손 — 프론트에서 CSS 선택자를 쓰던 감각이 그대로 옮겨온다. `select`가 돌려주는 리스트는 비어 있을 수 있고, `select_one`은 못 찾으면 `None`을 돌려준다는 차이도 같이 기억해 둔다.

### 1-6. `get_text()`가 가져오는 범위

4단계에서 찍힌 마크업을 보면 온도 숫자 `14.9` 앞뒤에 `<span class="blind">현재 온도</span>`와 `<span class="celsius">°</span>`가 붙어 있다. `get_text()`는 **그 태그 아래의 글자를 전부 이어 붙여** 돌려주므로 결과는 `14.9`만이 아니라 "현재 온도14.9°" 모양이 된다(앞뒤 공백 포함). `blind` 클래스는 화면에서는 안 보이고 스크린리더용으로만 들어 있는 글자라, 눈에 보이는 것과 `get_text()` 결과가 다를 수 있다. 숫자만 필요하면 더 안쪽 태그를 집거나 뒤에서 문자열을 정리해야 한다 — 그 정리 방법은 2단에 적는다.

## 2. 추가로 알면 좋은 활용법

### 2-1. 응답 상태를 코드로 확인하기

```python
response = requests.get(url, timeout=5)
print(response.status_code)   # 200
response.raise_for_status()   # 4xx·5xx면 여기서 예외 발생
```

`print(response)`로 눈으로 보는 대신 `status_code`를 조건문에 쓰거나 `raise_for_status()`로 실패를 예외로 바꿔 두면 day04의 `try`/`except` 흐름에 자연스럽게 얹힌다. `timeout`을 주지 않으면 서버가 응답을 안 줄 때 무한정 기다리므로 넣어 두는 편이 안전하다.

### 2-2. 쿼리스트링을 `params`로 조립하기

```python
response = requests.get(
    "https://search.naver.com/search.naver",
    params={"query": "안양날씨"},
)
print(response.url)   # 한글이 퍼센트 인코딩된 최종 주소
```

주소에 한글을 직접 붙여도 `requests`가 알아서 인코딩해 주지만, 파라미터가 여러 개이거나 값이 바뀌는 경우에는 딕셔너리 `params`로 넘기는 쪽이 읽기 쉽다. `?`와 `&`를 손으로 붙이다 생기는 실수도 줄어든다.

### 2-3. `User-Agent` 헤더

```python
headers = {"User-Agent": "Mozilla/5.0"}
response = requests.get(url, headers=headers)
```

`requests`의 기본 `User-Agent`는 `python-requests/버전`이라 사이트에 따라 브라우저가 아닌 요청을 거절하거나 다른 HTML을 내려주기도 한다. 브라우저처럼 보이는 헤더를 붙이면 개발자도구에서 본 것과 같은 HTML을 받을 가능성이 높아진다. robots.txt의 `User-agent` 항목이 바로 이 값을 보고 규칙을 적용하는 것이기도 하다.

### 2-4. 텍스트 정리와 속성 꺼내기

```python
tag = soup.select_one(".temperature_text")
tag.get_text(strip=True)          # 앞뒤 공백·줄바꿈 제거
tag.get_text(" ", strip=True)     # 자손 텍스트 사이를 공백으로 구분
tag.select_one("strong").contents # 자식 노드 리스트

a = soup.select_one("a.link")
a["href"]                         # 속성값 (없으면 KeyError)
a.get("href")                     # 속성값 (없으면 None)
```

`get_text()`는 글자만 가져오므로 링크 주소나 이미지 경로처럼 **속성**에 든 값은 딕셔너리처럼 `tag["href"]`로 꺼낸다. 딕셔너리의 대괄호 vs `get`과 똑같은 구분이다.

### 2-5. `find`/`find_all`과의 대응

| CSS 선택자 방식 | 메소드 방식 |
| --- | --- |
| `select_one(".cls")` | `find(class_="cls")` |
| `select("div.cls")` | `find_all("div", class_="cls")` |
| `select_one("#main")` | `find(id="main")` |

둘 다 같은 일을 한다. `class`는 파이썬 키워드라 `find`에서는 `class_`로 쓴다. 선택자 문법에 익숙하면 `select` 계열 하나로 통일하는 쪽이 코드가 짧다.

### 2-6. 못 찾았을 때의 방어

`select_one`이 `None`을 돌려준 상태에서 `.get_text()`를 부르면 `AttributeError`가 난다. 페이지 구조가 바뀌었거나 로그인·동적 렌더링 때문에 HTML에 그 태그가 없을 때 흔히 만나는 상황이다.

```python
tag = soup.select_one(".temperature_text")
temp = tag.get_text(strip=True) if tag else None
```

조건부 표현식이나 `try`/`except AttributeError`로 감싸 두면 값 하나 때문에 전체가 멈추는 일을 막을 수 있다.

## 3. 더 나아가 알면 좋은 것

### 3-1. 정적인지 동적인지 판별하는 법

브라우저에서 `Ctrl+U`(페이지 소스 보기)로 열리는 원본 HTML에 원하는 값이 보이면 정적이다. 개발자도구 Elements 탭에는 보이는데 소스 보기에는 없다면 자바스크립트가 나중에 채운 것이라 `requests`로는 받을 수 없다. 이때는 두 갈래다 — 개발자도구 **Network 탭**에서 그 데이터를 내려주는 JSON 요청을 찾아 그 주소를 직접 `requests.get`하거나(가장 가볍다), `Selenium`/`Playwright`로 브라우저를 띄워 렌더링을 기다린 뒤 긁는다.

### 3-2. 지켜야 할 것들

robots.txt는 기술적 차단이 아니라 약속이다. 허용 범위 안에서, 요청 사이에 `time.sleep`으로 간격을 두고, 사이트 이용약관과 저작권·개인정보 범위를 확인하는 것까지가 크롤링이다. 공개 API가 있으면 크롤링보다 API가 먼저다 — 구조가 바뀌어도 깨지지 않고, 허용된 방식이기 때문이다.

### 3-3. 파서 선택과 저장

`"html.parser"`는 표준 라이브러리에 들어 있어 설치 없이 쓰지만, `lxml`을 설치하면 더 빠르고 깨진 HTML에 관대하다. 긁은 값은 결국 `pandas.DataFrame`으로 모아 `to_csv`로 저장하는 흐름으로 이어진다 — [[Python day08 판다스 데이터프레임 생성과 인덱싱·필터링]]에서 본 "딕셔너리 리스트 → 데이터프레임"이 바로 그 접점이다.

같은 작업을 자바에서는 Jsoup으로 했다(Spring day17). `connect().get()` → `select()` → `.text()` 순서가 `requests.get` → `select` → `get_text()`와 한 줄씩 대응된다. 실제 프로젝트에서 Selenium으로 수집해 멱등 업서트하는 흐름은 [[KDT_2026 학습 지도]]의 프로젝트 매핑표에서 찾는다.

### 3-4. 다음에 볼 키워드

- `requests.Session`·쿠키·로그인 유지 · `headers`·`Referer` · `timeout`·재시도(`urllib3.Retry`)
- `response.encoding`·`apparent_encoding`·한글 깨짐 · `response.json()`
- `select`·`select_one`·`find`·`find_all` · `.contents`·`.children`·`.parent`·`.next_sibling` · `.attrs`
- `lxml`·`html5lib` 파서 · `Selenium`·`Playwright`·헤드리스 브라우저
- `robots.txt`·`User-agent`·`Crawl-delay` · `time.sleep`·rate limit · 공개 API
- `Scrapy`·비동기 `httpx`/`aiohttp` · 스케줄링(`schedule`, cron, GitHub Actions)

## 실습 파일

- `KDT_2026/2026_Python/day10/c-01.py` — 웹 크롤링 정의·정적/동적 라이브러리 구분·robots.txt(`User-agent`/`Disallow`/`Allow`)·개발자도구(`F12`, `Ctrl+Shift+C`) 확인 절차 주석, `pip install requests`/`beautifulsoup4`, `url = "https://search.naver.com/search.naver?&query=안양날씨"`, `requests.get(url)` → `<Response [200]>`·`response.text`, `BeautifulSoup(response.text, "html.parser")`, `soup.select_one(".temperature_text")` 마크업 출력, `.get_text()`로 텍스트 추출

## 관련 노트

[[Python 정리본 인덱스]] · [[Python day09 따릉이 대여이력 EDA 실습]] · [[Python day10 페이징 반복으로 베스트셀러 목록 크롤링]] · [[Python day08 판다스 데이터프레임 생성과 인덱싱·필터링]] · [[Python day04 예외 처리 try·except·else·finally]] · [[KDT_2026 학습 지도]]
