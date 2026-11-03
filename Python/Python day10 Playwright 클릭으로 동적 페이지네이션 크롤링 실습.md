---
출처: Claude 분석
원본: KDT_2026/2026_Python/practice/practice7.py
작성일: 2026-11-03
tags: [학습, python]
---

# Python day10 — Playwright 클릭으로 동적 페이지네이션 크롤링 실습

> 실습 파일: `practice/practice7.py`
> 허브: [[Python 정리본 인덱스]] · 이전: [[Python day10 Playwright 비동기로 동적 페이지 크롤링]] · 다음: [[Python day11 httpx로 공공데이터 API 호출과 JSON 데이터프레임 변환]]

day10의 세 예제를 한 문제에 모은 실습이다. 대상은 씨네21 영화 평점 페이지(`cine21.com/movie/point`)로, 영화 카드마다 **제목·포스터 이미지 주소·전문가 평점**을 뽑는다. 예스24 베스트셀러처럼 "카드 묶음에서 세 값을 짝지어 꺼내는" 구조인데, 결정적으로 다른 점이 하나 있다. 예스24는 주소의 `pageNumber`를 바꾸면 2·3페이지가 나왔지만, 씨네21의 페이지 번호 버튼은 **주소를 바꾸지 않고 자바스크립트로 목록만 갈아 끼운다**. 그래서 `requests`로는 1페이지밖에 못 받고, 브라우저를 띄워 **버튼을 직접 클릭**해야 다음 페이지가 나온다. 지난 예제의 스크롤(`evaluate`)이 이번에는 클릭(`click`)으로 바뀐 셈이고, 나머지 뼈대(`async with` → `launch` → `new_page` → `goto` → `wait_for_timeout` → `query_selector_all` → 카드 안 `query_selector`)는 그대로다.

## 1. 배운 내용

### 1-1. 문제 분석 — 주석 네 줄이 설계도

```python
# 1. 동적페이지(씨네21 동적 페이지네이션) vs 정적페이지
# 2. 주소: https://cine21.com/movie/point
# 3. 제목, 이미지 링크, 전문가 평점 = list_with_upthumb_item
#    p.title  , .img_wrap>img , .star_wrap > p.num
# 4. 클릭이벤트 : dom.click() ,  .pagination .page a
```

코드를 치기 전에 네 가지를 먼저 정했다. 이 순서가 크롤링 설계의 기본 틀이다.

| 순서 | 정한 것 | 이번 실습 |
| --- | --- | --- |
| 1 | 정적인가 동적인가 | 페이지 버튼을 눌러도 주소가 안 바뀌면 동적 → Playwright |
| 2 | 시작 주소 | `https://cine21.com/movie/point` |
| 3 | 카드 선택자와 카드 안의 값 선택자 | 카드 `.list_with_upthumb_item`, 그 안의 `.title`·`.img_wrap>img`·`.star_wrap > p.num` |
| 4 | 다음 페이지로 가는 동작 | `.pagination .page a` 버튼을 `click()` |

4번이 새로 생긴 칸이다. 정적 페이징(예스24)에서는 이 칸이 "주소의 `pageNumber`를 바꾼다"였고, 무한 스크롤(네이버 이미지)에서는 "`scrollTo`로 바닥까지 내린다"였다. **다음 묶음을 어떻게 불러올 것인가**가 세 예제를 가르는 기준이다.

### 1-2. 선택자 세 개 — 자손·자식 결합자

```text
.list_with_upthumb_item        영화 카드 하나
  .title                       제목
  .img_wrap>img                포스터 (.img_wrap 바로 아래 img)
  .star_wrap > p.num           전문가 평점 (.star_wrap 바로 아래 p 중 num 클래스)
```

| 선택자 | 읽는 법 |
| --- | --- |
| `.a .b` (공백) | `.a` 안쪽 어디든 있는 `.b` — 자손 |
| `.a > .b` | `.a`의 **바로 아래** `.b` — 자식 |
| `p.num` | `p` 태그이면서 `num` 클래스 |

`>` 주변의 공백은 있어도 없어도 같다(`.img_wrap>img` = `.img_wrap > img`). 자식 결합자를 쓰는 이유는 같은 클래스가 더 깊은 곳에도 있을 때 **원하는 층의 것만** 집기 위해서다. 개발자도구(`Ctrl+Shift+C`)로 카드를 찍어 구조를 본 뒤 정한 값이다.

### 1-3. 전체 흐름 — 번호 주석 1]~9]

```python
import asyncio
from playwright.async_api import async_playwright

async def 실습7():
    async with async_playwright() as 비동기통신:                          # 3] 켜고, 끝나면 정리
        브라우저 = await 비동기통신.chromium.launch(headless=False)        # 4] 크로미움 (창 보이게)
        페이지 = await 브라우저.new_page()                                 # 5] 새 탭
        await 페이지.goto("https://cine21.com/movie/point")               # 6] 이동
        await 페이지.wait_for_timeout(5000)                                #    5초 대기
        for i in range(1, 4):                                              # 1~3페이지
            페이지버튼리스트 = await 페이지.query_selector_all('.pagination .page a')  # 7] 버튼 전부
            await 페이지버튼리스트[i - 1].click()                          # 8] i번째 버튼 클릭
            await 페이지.wait_for_timeout(5000)
            items = await 페이지.query_selector_all('.list_with_upthumb_item')       # 9] 카드 전부
            for item in items:
                영화제목 = await item.query_selector('.title')
                영화제목 = await 영화제목.inner_text() if 영화제목 else "제목없음"
                이미지링크 = await item.query_selector('.img_wrap>img')
                이미지링크 = await 이미지링크.get_attribute('src') if 이미지링크 else "이미지없음"
                전문가평점 = await item.query_selector('.star_wrap > p.num')
                전문가평점 = await 전문가평점.inner_text() if 전문가평점 else "전문가평점없음"
                print(영화제목, 이미지링크, 전문가평점)

asyncio.run(실습7())
```

| 단계 | 코드 | 지난 예제와 |
| --- | --- | --- |
| 1]~2] | `import asyncio` · `async def 실습7()` | 같음 — 비동기 함수 하나로 감싸기 |
| 3]~6] | `async with` → `launch` → `new_page` → `goto` | 같음 |
| 7] | `query_selector_all('.pagination .page a')` | **새로움** — 페이지 버튼 목록 |
| 8] | `await 버튼.click()` | **새로움** — 스크롤 대신 클릭 |
| 9] | 카드 전부 → 카드 안 세 값 | 같음 — 값이 둘에서 셋으로 |

새로 배운 것은 7]과 8] 두 줄뿐이다. 나머지는 `c-03.py`를 그대로 옮겨 적은 것이라, 처음 보는 사이트도 **"다음 묶음을 어떻게 불러오나"만 바꾸면** 같은 틀로 풀린다는 감각이 이 실습의 핵심이다.

### 1-4. `click()` — 사람이 누르는 것과 같은 이벤트

```python
페이지버튼리스트 = await 페이지.query_selector_all('.pagination .page a')
await 페이지버튼리스트[i - 1].click()
await 페이지.wait_for_timeout(5000)
```

`query_selector_all`이 돌려준 요소(핸들) 하나에 `.click()`을 부르면 브라우저가 그 자리에 **마우스 클릭 이벤트**를 보낸다. 사이트에 걸려 있던 `onclick`·`addEventListener` 처리기가 그대로 실행되므로, 주소 변경 없이 목록만 바꾸는 페이지네이션도 사람이 누른 것과 똑같이 반응한다. JS 수업에서 `dom.click()`·`dispatchEvent`로 이벤트를 흉내 내던 것의 브라우저 바깥 버전이라고 보면 된다(그쪽 노트는 허브·지도 경유).

클릭 뒤 `wait_for_timeout(5000)`을 둔 이유는 스크롤 때와 같다. 클릭은 "요청을 보내라"는 신호일 뿐이고, 새 목록이 서버에서 와서 그려지기까지 시간이 걸린다. 기다리지 않고 바로 `query_selector_all`을 하면 **이전 페이지의 카드**를 또 읽게 된다.

### 1-5. 버튼 목록을 반복마다 다시 찾는 이유

```python
for i in range(1, 4):
    페이지버튼리스트 = await 페이지.query_selector_all('.pagination .page a')   # 매번 새로
    await 페이지버튼리스트[i - 1].click()
```

버튼 목록을 `for` 바깥에서 한 번만 받아 두고 돌려 써도 될 것 같지만, 그렇게 하면 두 번째 바퀴에서 어긋나기 쉽다. 페이지가 바뀔 때 사이트가 **페이지네이션 영역을 통째로 다시 그리는** 경우가 많고, 그러면 처음 받아 둔 요소 핸들은 이미 화면에서 사라진 옛 요소를 가리킨다(이른바 stale element). 클릭하면 "요소가 DOM에 붙어 있지 않다"는 오류가 난다. 그래서 **클릭 직전에 다시 찾는** 것이 안전하다. `range(1, 4)`의 `i`를 `[i - 1]`로 0부터 시작하는 인덱스에 맞춘 것은 리스트 인덱싱 그대로다.

페이지 번호 버튼 묶음에는 "이전·다음" 화살표나 현재 페이지 표시가 함께 들어 있는 사이트가 흔하다. 몇 번째 `a`가 몇 페이지인지는 개발자도구에서 개수와 순서를 확인하고 인덱스를 맞춘다 — 2-1에서 더 튼튼한 방법을 정리한다.

### 1-6. 카드 안에서 세 값 — `None` 방어 세 번

```python
영화제목 = await item.query_selector('.title')
영화제목 = await 영화제목.inner_text() if 영화제목 else "제목없음"
이미지링크 = await item.query_selector('.img_wrap>img')
이미지링크 = await 이미지링크.get_attribute('src') if 이미지링크 else "이미지없음"
전문가평점 = await item.query_selector('.star_wrap > p.num')
전문가평점 = await 전문가평점.inner_text() if 전문가평점 else "전문가평점없음"
```

지난 예제의 두 줄짜리 패턴이 세 번 반복된다. 같은 변수에 **요소 → 값**으로 두 번 대입하는 모양이라 변수가 늘지 않는다. 전문가 평점은 평점이 아직 없는 영화 카드에서 빠져 있을 수 있어 `"전문가평점없음"` 기본값이 실제로 쓰인다. 포스터는 `src` 속성, 제목·평점은 태그 사이 글자(`inner_text`)라는 구분도 같다.

| 값 | 선택자 | 꺼내는 방법 |
| --- | --- | --- |
| 제목 | `.title` | `inner_text()` |
| 포스터 | `.img_wrap>img` | `get_attribute('src')` |
| 평점 | `.star_wrap > p.num` | `inner_text()` |

### 1-7. 한글 식별자 — 파이썬은 허용한다

```python
async def 실습7():
    async with async_playwright() as 비동기통신:
        브라우저 = await 비동기통신.chromium.launch(headless=False)
        페이지 = await 브라우저.new_page()
```

함수 이름·변수 이름이 전부 한글이다. 파이썬 3은 식별자에 유니코드 글자를 허용하므로 문법적으로 문제없고, 수업처럼 **각 줄이 무엇을 가리키는지 바로 읽히게** 하는 용도로는 꽤 유용하다. 다만 공유 코드·라이브러리·협업에서는 영문이 관례이고, 키보드 전환이 잦아지며, 일부 도구가 한글 이름을 어색하게 다루므로 연습용과 실전용을 구분하는 편이 좋다. `items`·`item`처럼 영문이 섞여 있어도 동작에는 아무 차이가 없다.

### 1-8. 결과 — 출력만 하고 담지는 않음

이번 코드는 세 값을 `print`로 찍는 데서 끝난다. `c-03.py`가 `item_list.append({...})`로 모아 반환하던 것과 비교하면 수집 단계까지다. 데이터프레임으로 넘기려면 2-3처럼 딕셔너리로 모아 두면 된다. 평점은 `"8.00"` 같은 **문자열**로 들어오므로 숫자 비교·평균을 내려면 `float()` 변환이 필요하다.

## 2. 추가로 알면 좋은 활용법

### 2-1. 몇 번째 `a`가 아니라 "글자가 2인 버튼"을 누르기

```python
await 페이지.click(f'.pagination .page a:has-text("{i}")')
# 또는
await 페이지.locator('.pagination .page a', has_text=str(i)).first.click()
```

인덱스로 버튼을 고르면 화살표가 섞이거나 버튼 수가 바뀔 때 엉킨다. Playwright의 `:has-text("2")` 의사 선택자나 `locator(..., has_text=)`로 **버튼에 적힌 글자**로 고르면 순서와 무관하다. `page.click(선택자)`는 "찾아서 클릭"을 한 번에 하고, 요소가 뜰 때까지 자동으로 기다린다.

### 2-2. 고정 5초 대신 "목록이 바뀔 때까지"

```python
first_before = await items[0].inner_text()
await 버튼.click()
await 페이지.wait_for_function(
    "prev => document.querySelector('.list_with_upthumb_item .title')?.innerText !== prev",
    arg=first_before,
)
```

클릭 뒤 5초는 느린 날엔 모자라고 빠른 날엔 낭비다. **첫 카드의 제목이 바뀌면 새 페이지가 그려진 것**이라는 조건을 `wait_for_function`에 자바스크립트로 넘기면 딱 필요한 만큼만 기다린다. 더 단순하게는 `wait_for_load_state("networkidle")`로 요청이 잠잠해질 때까지, 또는 `wait_for_selector`로 로딩 표시가 사라질 때까지 기다리는 방법이 있다.

### 2-3. 결과를 모아 데이터프레임으로

```python
rows = []
for item in items:
    ...
    rows.append({"페이지": i, "제목": 영화제목, "포스터": 이미지링크, "평점": 전문가평점})
# 반복이 끝난 뒤
import pandas as pd
df = pd.DataFrame(rows)
df["평점"] = pd.to_numeric(df["평점"], errors="coerce")   # "전문가평점없음" → NaN
df.to_csv("cine21_point.csv", index=False, encoding="utf-8-sig")
```

`print` 자리에 `append`만 넣으면 지난 예제들과 같은 "리스트 안의 딕셔너리"가 된다. 어느 페이지에서 왔는지 `"페이지": i`를 함께 넣어 두면 나중에 추적하기 쉽다. 평점 문자열은 `to_numeric(errors="coerce")`로 숫자로 바꾸면서 기본값 문자열을 `NaN`으로 흘려보낼 수 있다 — day08의 타입 변환·결측 처리가 그대로 이어진다.

### 2-4. 페이지 수를 미리 모를 때

```python
page_no = 1
while True:
    ... # 현재 페이지 수집
    next_btn = await 페이지.query_selector('.pagination .page a:has-text("다음")')
    if not next_btn or page_no >= 20:
        break
    await next_btn.click()
    page_no += 1
```

`range(1, 4)`처럼 세 페이지로 못 박지 않고, **"다음" 버튼이 없어질 때까지** 도는 꼴이다. 예스24 노트의 `while True` + `break` 자동 종료와 같은 발상이고, 상한(`>= 20`)을 하나 두어 무한 루프를 막는다.

### 2-5. 클릭 말고 쓸 수 있는 입력 동작

| 메소드 | 하는 일 |
| --- | --- |
| `click()` · `dblclick()` | 클릭 · 더블클릭 |
| `fill("검색어")` | 입력창 내용을 지우고 채움 |
| `type("가나다")` | 한 글자씩 타이핑 (자동완성 유발) |
| `press("Enter")` | 키 입력 |
| `select_option("2024")` | `<select>`에서 고르기 |
| `hover()` | 마우스 올리기 (드롭다운 펼칠 때) |
| `check()` / `uncheck()` | 체크박스 |

검색창에 영화 제목을 넣고 엔터를 치는 것, 연도 필터를 고르는 것까지 전부 같은 방식으로 흉내 낼 수 있다. `fill` + `press("Enter")` 조합이 가장 자주 쓰인다.

### 2-6. 눈으로 확인할 땐 `headless=False` + `slow_mo`

```python
브라우저 = await 비동기통신.chromium.launch(headless=False, slow_mo=500)
```

`slow_mo`는 모든 동작 사이에 밀리초만큼 틈을 두어 클릭이 어디에 떨어지는지 눈으로 따라갈 수 있게 한다. 선택자와 인덱스를 맞추는 단계에서 유용하고, 다 맞춘 뒤에는 빼고 `headless=True`로 돌린다. 막히는 순간에 `await 페이지.screenshot(path="debug.png")`를 끼워 두면 창 없이 돌릴 때도 상태를 볼 수 있다.

## 3. 더 나아가 알면 좋은 것

### 3-1. 클릭 뒤에 일어나는 요청을 가로채기

```python
async with 페이지.expect_response(lambda r: "point" in r.url and r.status == 200) as resp_info:
    await 버튼.click()
response = await resp_info.value
data = await response.json()   # 사이트가 JSON으로 주면 그대로 파싱
```

페이지 버튼을 누를 때 사이트는 뒤에서 서버에 요청을 보낸다. 개발자도구 Network 탭에서 그 요청을 찾아 보면 **JSON API**인 경우가 많고, 그러면 그려진 화면을 긁는 대신 응답 자체를 받는 쪽이 훨씬 안정적이다. Playwright의 `expect_response`로 클릭에 따라 들어오는 응답을 잡거나, 아예 그 주소를 `httpx`·`requests`로 직접 불러 브라우저를 생략할 수도 있다. 다음 수업(day11)에서 배우는 API 호출이 바로 이 "브라우저 없이 데이터만 받기"다.

### 3-2. 여러 페이지를 동시에 — 탭을 나눠 `asyncio.gather`

클릭 방식 페이지네이션은 **한 탭 안에서 상태가 이어지므로** 순서대로 눌러야 한다. 반면 페이지마다 독립 주소가 있다면 `new_page()`를 여러 개 열어 `asyncio.gather`로 동시에 긁을 수 있다. 어느 쪽이 가능한지는 1-1의 "다음 묶음을 어떻게 불러오나" 분석에서 갈린다.

### 3-3. 자동화 탐지와 속도

같은 IP에서 5초마다 기계적으로 클릭하면 봇으로 분류될 수 있다. `new_context(user_agent=…)`로 일반 브라우저처럼 보이게 하고, 대기 시간에 `random.uniform(2, 5)`로 흔들림을 주고, 하루에 필요한 만큼만 가져온다. 영화 포스터와 평점은 각각 저작권·이용약관이 있으므로 수집물을 어디까지 쓸 수 있는지는 따로 확인한다. `robots.txt` 확인은 정적 크롤링 노트에서 정리한 대로다.

### 3-4. 테스트 도구로서의 Playwright

Playwright는 원래 **웹 앱 자동 테스트** 도구다. "버튼을 누르면 목록이 바뀐다"를 코드로 검증하는 일이 본업이라, `expect(locator).to_have_text(...)` 같은 단언문과 트레이스 뷰어·녹화(`codegen`)가 들어 있다. `playwright codegen https://cine21.com/movie/point`를 실행하면 브라우저에서 클릭한 동작이 파이썬 코드로 자동 생성되어 선택자를 찾는 수고를 덜 수 있다. React로 만든 화면을 자동 테스트할 때도 같은 도구를 쓴다.

### 3-5. 다음에 볼 키워드

- `click`·`dblclick`·`fill`·`type`·`press`·`select_option`·`hover`·`check` · `page.click(선택자)` 한 번에
- `:has-text()`·`locator(has_text=)`·`get_by_role("link", name="2")`·`get_by_text` · stale element
- `wait_for_function`·`wait_for_load_state("networkidle")`·`wait_for_selector(state="hidden")` · `slow_mo`·`screenshot`
- `expect_response`·`page.route`·Network 탭 JSON · `httpx`/`requests`로 API 직접 호출(day11)
- `while True` + "다음" 버튼 유무로 종료 · 상한 두기 · `random.uniform` 대기
- `pd.DataFrame(rows)`·`to_numeric(errors="coerce")`·`to_csv(encoding="utf-8-sig")`
- `new_context(user_agent=)`·`asyncio.gather` 탭 병렬 · `playwright codegen`·`expect` 단언·트레이스 뷰어

## 실습 파일

- `KDT_2026/2026_Python/practice/practice7.py` — 씨네21 영화 평점 페이지(`cine21.com/movie/point`) 동적 페이지네이션 크롤링: 주석 1~4로 동적/정적 판별·주소·카드 선택자(`.list_with_upthumb_item` 안 `.title`·`.img_wrap>img`·`.star_wrap > p.num`)·클릭 대상(`.pagination .page a`) 설계, `import asyncio`·`from playwright.async_api import async_playwright`, `async def 실습7()` 안에서 `async with async_playwright() as 비동기통신` → `await 비동기통신.chromium.launch(headless=False)` → `new_page()` → `goto(...)` → `wait_for_timeout(5000)`, `for i in range(1, 4)`로 매 바퀴 `query_selector_all('.pagination .page a')` 다시 받아 `[i - 1].click()` → `wait_for_timeout(5000)` → `query_selector_all('.list_with_upthumb_item')` 카드마다 `query_selector` → `inner_text()`/`get_attribute('src')`를 조건부 표현식으로 `None` 방어("제목없음"·"이미지없음"·"전문가평점없음") → `print`, `asyncio.run(실습7())`

## 관련 노트

[[Python 정리본 인덱스]] · [[Python day10 Playwright 비동기로 동적 페이지 크롤링]] · [[Python day10 페이징 반복으로 베스트셀러 목록 크롤링]] · [[Python day10 requests·BeautifulSoup으로 정적 페이지 크롤링]] · [[Python day11 httpx로 공공데이터 API 호출과 JSON 데이터프레임 변환]] · [[Python day08 판다스 데이터 전처리 중복 제거와 타입 변환]] · [[KDT_2026 학습 지도]]
