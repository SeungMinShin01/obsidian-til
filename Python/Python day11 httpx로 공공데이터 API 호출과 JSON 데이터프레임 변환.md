---
출처: Claude 분석
원본: KDT_2026/2026_Python/day11/h-01.py
작성일: 2026-11-03
tags: [학습, python]
---

# Python day11 — httpx로 공공데이터 API 호출과 JSON 데이터프레임 변환

> 실습 파일: `day11/h-01.py`
> 허브: [[Python 정리본 인덱스]] · 이전: [[Python day10 Playwright 클릭으로 동적 페이지네이션 크롤링 실습]] · 다음: (아직 없음)

day10까지는 사람이 보라고 만든 **HTML 화면**을 긁어 데이터를 꺼냈다. day11은 처음부터 프로그램이 읽으라고 열어 둔 **API**를 부른다. 재료는 공공데이터포털(data.go.kr)의 "대구광역시 중구 맛집 현황"으로, 회원가입 후 활용 신청을 하면 **인증키(serviceKey)**가 발급되고, 그 키를 주소에 붙여 요청하면 서버가 JSON으로 자료를 돌려준다. 통신은 `httpx`라는 라이브러리가 맡고(`requests`와 거의 같은 사용법), 받은 JSON은 `.json()` 한 번으로 딕셔너리가 되어 `pd.DataFrame`에 바로 들어간다. 크롤링 노트들 끝마다 적어 두던 "공개 API가 있으면 그쪽이 먼저"가 바로 이 자리다. 파싱도, 선택자도, 브라우저도 없다 — **주소 분석 → 요청 → JSON 변환 → 데이터프레임** 네 단계가 전부다.

## 1. 배운 내용

### 1-1. `httpx` — 외부 API와 통신하는 라이브러리

```bash
pip install httpx        # 설치 1 — HTTP 통신
pip install xmltodict    # 설치 2 — XML 응답을 딕셔너리로 (JSON은 httpx만으로 충분)
```

수업 주석의 정의는 "외부 API 통신하는 라이브러리, API 연동 / Spring API"다. 정리하면 이렇다.

| 라이브러리 | 역할 | 비고 |
| --- | --- | --- |
| `httpx` | HTTP 요청을 보내고 응답을 받는다 | `httpx.get(url)` — `requests.get(url)`과 사용법이 거의 같다 |
| `.json()` | 응답 본문(JSON 문자열)을 파이썬 딕셔너리·리스트로 | `httpx`에 내장 |
| `xmltodict` | 응답이 XML일 때 딕셔너리로 | `httpx`는 XML 변환을 지원하지 않아 따로 설치 |

"Spring API"라고 적어 둔 이유는, 백엔드 수업에서 만든 Spring 컨트롤러가 돌려주는 JSON도 **정확히 같은 방식**으로 파이썬에서 받을 수 있기 때문이다. 공공데이터포털이든 직접 만든 서버든, 호출하는 쪽에서는 "주소에 GET 요청 → JSON 응답"이라는 모양이 같다.

### 1-2. 인증키 — 코드에 적되, 공개하지는 않는다

```python
service_key = "<공공데이터포털에서 발급받은 인증키>"
```

공공데이터포털은 활용 신청을 하면 계정마다 긴 16진수 문자열의 인증키를 준다. 이 키가 요청에 붙어야 서버가 응답한다(없거나 틀리면 인증 오류). 수업 코드는 키를 변수에 그대로 적었는데, 이 값은 **비밀번호에 준하는 개인 자격 정보**다. 깃허브 공개 저장소나 노트에 올리면 누구나 내 명의로 호출할 수 있으므로, 이 노트에서는 값을 가렸고 실제 코드에서도 2-1처럼 환경변수나 별도 파일로 빼는 것이 원칙이다.

### 1-3. 주소 분석 — 고정 부분과 파라미터

```text
https://api.odcloud.kr/api/15052602/v1/uddi:855807e2-…_201909031553
    ?page=1
    &perPage=10
    &serviceKey=<인증키>
```

| 부분 | 뜻 |
| --- | --- |
| `https://api.odcloud.kr/api/15052602/v1/uddi:…` | 이 데이터셋의 고정 주소 (포털의 "활용 신청 상세"에서 복사) |
| `page` | 현재 페이지 번호 |
| `perPage` | 페이지당 자료 수 |
| `serviceKey` | 인증키 |

예스24 베스트셀러 주소를 `categoryNumber`·`pageNumber`로 쪼개 읽던 것과 같은 **쿼리스트링** 분석이다. 차이는 응답이 HTML이 아니라 JSON이라는 점과, 파라미터의 뜻을 포털의 **API 명세 문서**가 정확히 알려 준다는 점이다. 크롤링에서는 파라미터 뜻을 추측했지만 API에서는 문서를 읽는다.

### 1-4. 주소 조립 — `+=`와 f-문자열

```python
url = "https://api.odcloud.kr/api/15052602/v1/uddi:855807e2-fe8a-4e47-8a5a-ce1894e410d7_201909031553"
url += "?page=1"
url += "&perPage=147"
url += f"&serviceKey={service_key}"
```

첫 파라미터 앞은 `?`, 그다음부터는 `&`로 잇는다. 한 줄로 적어도 되지만 파라미터마다 `+=`로 한 줄씩 붙이면 어디를 바꾸는지 눈에 잘 들어온다. 인증키만 f-문자열로 변수에서 끼워 넣었다. `perPage=147`은 이 데이터셋의 전체 건수에 맞춰 **한 번에 전부** 받으려는 값이다 — 응답 JSON의 `totalCount`로 전체 건수를 확인할 수 있다(2-3).

### 1-5. 요청과 응답 — `httpx.get(url)`

```python
response = httpx.get(url)
print(response)   # <Response [200 OK]>
```

`httpx.HTTP메소드명(주소)` 꼴이다. GET이면 `httpx.get`, POST면 `httpx.post`. 반환되는 응답 객체를 그냥 찍으면 `<Response [200 OK]>`처럼 **상태 코드**가 보인다. `requests`의 `<Response [200]>`과 같은 의미이고, 200이면 성공이다.

| 상태 | 뜻 | API에서 흔한 원인 |
| --- | --- | --- |
| `200 OK` | 성공 | — |
| `401`/`403` | 인증 실패·권한 없음 | 인증키 오타, 활용 신청 미승인 |
| `404` | 주소 없음 | 데이터셋 주소·버전(`v1`) 오타 |
| `429` | 요청 과다 | 일일 트래픽 한도 초과 |
| `500` | 서버 오류 | 포털 쪽 문제, 잠시 후 재시도 |

### 1-6. JSON 변환 — `.json()`

```python
response_json = response.json()
# {"currentCount": 147, "data": [ {...}, {...}, ... ], "matchCount": 147, "page": 1, "perPage": 147, "totalCount": 147}
```

응답 본문은 JSON **문자열**이다. `.json()`이 그걸 파이썬 자료형으로 바꿔 준다 — 중괄호는 딕셔너리, 대괄호는 리스트, 따옴표 글자는 문자열, 숫자는 숫자. day02 딕셔너리 노트에서 "리스트 안의 딕셔너리 = API 응답 모양"이라고 적어 둔 그 모양이 실제로 왔다.

| 키 | 뜻 |
| --- | --- |
| `data` | 실제 자료 — 가게 한 곳이 딕셔너리 하나인 **리스트** |
| `currentCount` | 이번 응답에 담긴 건수 |
| `totalCount` | 전체 건수 |
| `page` · `perPage` | 요청한 페이지·페이지당 수 그대로 |

겉껍데기(건수·페이지 정보)와 알맹이(`data`)가 나뉘어 있는 것이 공공데이터포털 `odcloud` 응답의 공통 구조다. 다른 API도 `items`·`results`·`body` 같은 이름으로 비슷하게 감싸 보내므로, 첫 호출에서 `print(response_json.keys())`로 **어느 키 아래에 알맹이가 있는지** 먼저 본다.

### 1-7. 데이터프레임으로 — `pd.DataFrame(response_json['data'])`

```python
import pandas as pd
df = pd.DataFrame(response_json['data'])
df.info()
```

`data`가 "리스트 안의 딕셔너리"이므로 `pd.DataFrame`에 그대로 넣으면 **딕셔너리 하나 = 행 하나, 키 = 열 이름**으로 표가 만들어진다. day08 전처리 노트의 사원 명부(딕셔너리 리스트 → 데이터프레임)와 같은 생성법이다. `info()`로 행 수·열 이름·결측·자료형을 먼저 확인하는 습관도 그대로다. 공공데이터는 열 이름이 한글이고(`업소명`·`소재지`·`전화번호` 등) 숫자처럼 보이는 열이 문자열로 오는 경우가 많아, 바로 다음 단계가 전처리다.

### 1-8. 크롤링과 API 호출 — 무엇이 달라졌나

| 구분 | 크롤링 (day10) | API 호출 (day11) |
| --- | --- | --- |
| 받는 것 | 사람용 HTML 화면 | 프로그램용 JSON 데이터 |
| 파싱 | `BeautifulSoup`·선택자 / Playwright | `.json()` 한 번 |
| 구조 변경 | 사이트 디자인이 바뀌면 선택자가 깨짐 | 명세가 버전(`v1`)으로 고정 |
| 인증 | 없음 (대신 robots.txt·차단 위험) | 인증키 필수·트래픽 한도 |
| 속도·부담 | 느리고 서버에 부담 | 빠르고 서버가 허용한 통로 |
| 문서 | 없음 — 개발자도구로 추측 | 요청·응답 명세 문서 제공 |

세 노트에 걸쳐 적어 둔 우선순위 **공개 API → 숨은 JSON → 정적 파싱 → 브라우저 자동화**의 첫 칸이다. 같은 자료가 API로 열려 있다면 크롤링할 이유가 없다.

## 2. 추가로 알면 좋은 활용법

### 2-1. 인증키를 코드 밖으로 — 환경변수와 `.env`

```python
# .env 파일 (깃에 올리지 않음 — .gitignore에 추가)
# DATA_GO_KR_KEY=발급받은키

import os
from dotenv import load_dotenv     # pip install python-dotenv
load_dotenv()
service_key = os.environ["DATA_GO_KR_KEY"]
```

키를 `.env` 파일에 두고 `.gitignore`에 올리면 코드는 공개해도 키는 새지 않는다. `os.environ["이름"]`은 없으면 `KeyError`, `os.getenv("이름")`은 `None`을 준다. 깃허브 Actions 같은 무인 환경에서는 저장소 **Secrets**에 넣고 환경변수로 주입한다. 수집기 프로젝트의 사람인 API 키도 같은 방식으로 다룬다(지도 매핑표 경유).

### 2-2. 주소 이어 붙이기 대신 `params=`

```python
response = httpx.get(
    "https://api.odcloud.kr/api/15052602/v1/uddi:…",
    params={"page": 1, "perPage": 147, "serviceKey": service_key},
    timeout=10,
)
```

`params=` 딕셔너리를 주면 `?`·`&`·인코딩을 `httpx`가 알아서 처리한다. 공공데이터포털 키는 발급 화면에 **인코딩된 키(Encoding)**와 **디코딩된 키(Decoding)** 두 가지가 보이는데, `params=`로 넘길 때는 디코딩 키를, 주소에 직접 붙일 때는 인코딩 키를 쓴다 — 두 번 인코딩되면 인증이 실패한다. `timeout`은 응답이 없을 때 무한정 기다리지 않게 하는 안전장치로, `requests`와 달리 `httpx`는 기본 5초 타임아웃이 있다.

### 2-3. 전체 건수만큼 돌기 — `totalCount`와 페이지 반복

```python
first = httpx.get(url, params={"page": 1, "perPage": 1, "serviceKey": key}).json()
total = first["totalCount"]
per = 100
rows = []
for page in range(1, total // per + 2):
    body = httpx.get(url, params={"page": page, "perPage": per, "serviceKey": key}).json()
    rows.extend(body["data"])
df = pd.DataFrame(rows)
```

`perPage=147`처럼 건수를 미리 알고 박는 대신, 첫 호출로 `totalCount`를 읽고 페이지 수를 계산해 돈다. 예스24의 `for page in range(1, 4)`와 같은 페이징 반복이 API에서도 그대로다. `perPage` 상한은 API마다 다르니(흔히 100~1000) 명세를 본다. `rows.extend`는 리스트를 펴서 이어 붙이고, `append`는 리스트 통째로 한 칸이 된다는 day02의 구분이 여기서 쓰인다.

### 2-4. 상태 코드 확인과 예외 처리

```python
try:
    response = httpx.get(url, params=params, timeout=10)
    response.raise_for_status()           # 4xx·5xx면 HTTPStatusError
    body = response.json()
except httpx.HTTPStatusError as e:
    print("응답 오류:", e.response.status_code, e.response.text[:200])
except httpx.RequestError as e:
    print("통신 실패:", e)
```

200이 아닌데 `.json()`을 부르면 오류 페이지를 파싱하다 `JSONDecodeError`가 난다. `raise_for_status()`로 먼저 걸러 내고, 통신 자체가 안 된 경우(`RequestError` — 네트워크·DNS·타임아웃)와 서버가 거절한 경우(`HTTPStatusError`)를 day04의 `except` 분기로 나눠 받는다. 공공데이터포털은 오류 사유를 응답 본문에 적어 주는 경우가 많아 `e.response.text`를 찍어 보는 것이 빠르다.

### 2-5. XML로 주는 API — `xmltodict`

```python
import xmltodict
response = httpx.get(xml_api_url, params=params)
doc = xmltodict.parse(response.text)          # XML 문자열 → 딕셔너리
items = doc["response"]["body"]["items"]["item"]
df = pd.DataFrame(items)
```

공공데이터포털의 오래된 API는 JSON 대신 XML로 응답하는 것이 많다. `xmltodict.parse`가 XML 문자열을 중첩 딕셔너리로 바꿔 주면, 그다음은 JSON과 똑같이 키를 따라 내려가 `pd.DataFrame`에 넣는다. 태그가 하나뿐이면 리스트가 아니라 딕셔너리 하나로 들어오므로 `isinstance(items, dict)`이면 `[items]`로 감싸 주는 방어가 필요하다. 명세에 `_type=json` 같은 파라미터가 있으면 JSON으로 받는 쪽이 간단하다.

### 2-6. 중첩 JSON은 `json_normalize`

```python
df = pd.json_normalize(response_json["data"])          # 중첩 딕셔너리를 a.b 열로 펴기
df = pd.json_normalize(body, record_path=["data"], meta=["totalCount"])
```

값 안에 또 딕셔너리가 들어 있는 응답(`{"위치": {"위도": .., "경도": ..}}`)은 `pd.DataFrame`에 넣으면 그 열이 딕셔너리 그대로 남는다. `json_normalize`가 `위치.위도`·`위치.경도`처럼 점으로 이어진 열로 펴 준다. `record_path`로 알맹이 리스트의 경로를, `meta`로 겉껍데기 값을 같이 가져올 수 있다.

### 2-7. 받은 뒤 바로 저장 — 호출 횟수 아끼기

```python
df.to_csv("daegu_junggu_restaurants.csv", index=False, encoding="utf-8-sig")
# 다음부터는
df = pd.read_csv("daegu_junggu_restaurants.csv")
```

공공데이터포털은 개발 계정에 **일일 트래픽 한도**(보통 1,000건 안팎)가 있다. 분석하면서 셀을 실행할 때마다 다시 호출하면 금방 소진되므로, 한 번 받으면 CSV로 저장하고 이후에는 파일을 읽는다. `utf-8-sig`는 엑셀에서 한글이 깨지지 않게 하는 BOM 옵션으로 day08·day10에서 적어 둔 그대로다.

## 3. 더 나아가 알면 좋은 것

### 3-1. `httpx`를 고르는 이유 — 비동기 클라이언트

```python
import asyncio, httpx

async def fetch(client, page):
    r = await client.get(url, params={"page": page, "perPage": 100, "serviceKey": key})
    return r.json()["data"]

async def main():
    async with httpx.AsyncClient(timeout=10) as client:
        pages = await asyncio.gather(*(fetch(client, p) for p in range(1, 11)))
    return [row for page in pages for row in page]

rows = asyncio.run(main())
```

`requests`와 사용법이 같은데 굳이 `httpx`를 쓰는 이유가 여기 있다. `httpx.AsyncClient`는 day10 Playwright에서 배운 `async`·`await`·`asyncio.gather`와 그대로 맞물려, 페이지 열 개를 **동시에** 요청한다. 순서대로 열 번 기다리던 시간이 한 번 기다리는 시간으로 줄어든다. HTTP/2 지원, 동기·비동기 같은 API라는 점도 `httpx`의 장점이다. 다만 한꺼번에 많이 보내면 429가 오므로 `asyncio.Semaphore`로 동시 수를 제한한다.

### 3-2. REST API의 네 동사와 Spring 연동

| HTTP 메소드 | 뜻 | `httpx` | Spring 쪽 |
| --- | --- | --- | --- |
| GET | 조회 | `httpx.get(url, params=)` | `@GetMapping` |
| POST | 생성 | `httpx.post(url, json={...})` | `@PostMapping` + `@RequestBody` |
| PUT / PATCH | 수정 | `httpx.put` / `httpx.patch` | `@PutMapping` |
| DELETE | 삭제 | `httpx.delete` | `@DeleteMapping` |

공공데이터는 GET 하나로 끝나지만, 직접 만든 Spring 서버에는 네 동사를 모두 쓴다. `json=` 인자에 딕셔너리를 주면 `httpx`가 JSON 본문과 `Content-Type: application/json` 헤더를 만들어 보내고, Spring의 `@RequestBody`가 그걸 객체로 받는다. 파이썬에서 분석한 결과를 Spring 서버에 POST로 넣거나, 반대로 Spring이 모아 둔 데이터를 파이썬이 GET으로 받아 분석하는 양방향 연동이 이 한 줄에서 시작된다. 수업 주석의 "API 연동 / Spring API"가 뜻하는 자리다(Spring 노트는 허브·지도 경유).

### 3-3. 인증 방식의 종류

공공데이터포털은 **쿼리스트링에 키**를 붙이는 가장 단순한 방식이다. 실무 API는 `headers={"Authorization": "Bearer <토큰>"}`처럼 헤더에 토큰을 싣는 방식(JWT·OAuth 2.0)이 흔하고, 토큰에 만료 시간이 있어 갱신 로직이 따라온다. 어느 방식이든 원칙은 같다 — **키는 코드·저장소·노트에 남기지 않는다.**

### 3-4. 응답 스키마 검증과 타입

API 응답은 서버 사정으로 열이 늘거나 값이 비어서 올 수 있다. `pydantic` 모델로 응답 모양을 선언해 두면 빠진 키·틀린 자료형을 받는 즉시 잡아낸다. 데이터프레임 단계에서는 `df.astype({...})`·`to_numeric(errors="coerce")`·`to_datetime`으로 열 자료형을 고정하고, `isnull().sum()`으로 결측을 세는 day08의 전처리가 그대로 이어진다.

### 3-5. 예약 수집과 멱등성

같은 API를 매일 호출해 쌓는다면 어제 받은 행을 오늘 또 넣지 않도록 **키 열 기준 업서트**(있으면 갱신, 없으면 삽입)가 필요하다. 몇 번을 돌려도 결과가 같아지는 성질이 멱등성이고, 수집기 프로젝트의 사람인 API 수집이 바로 그 구조다(지도 매핑표 경유). 공공데이터포털 API는 `?page=`가 아니라 수정일 파라미터를 제공하는 경우도 있어, 명세에서 **증분 수집**이 가능한지 먼저 본다.

### 3-6. 다음에 볼 키워드

- `httpx.get/post/put/delete`·`params=`·`json=`·`headers=`·`timeout=` · `Response.status_code`·`.json()`·`.text`·`raise_for_status`
- `HTTPStatusError`·`RequestError` · 401/403/404/429/500 · 일일 트래픽 한도
- 인코딩 키 vs 디코딩 키 · `.env`·`python-dotenv`·`os.environ`·GitHub Secrets·`.gitignore`
- `totalCount`·`perPage` 상한·페이지 반복·`extend` · `to_csv(utf-8-sig)` 캐시
- `xmltodict.parse`·`_type=json` · `pd.json_normalize(record_path, meta)`
- `httpx.AsyncClient`·`asyncio.gather`·`Semaphore`·HTTP/2 · `requests` vs `httpx` vs `aiohttp`
- REST·`@GetMapping`/`@PostMapping`/`@RequestBody` · Bearer 토큰·JWT·OAuth 2.0 · `pydantic` · 업서트·멱등성·증분 수집

## 실습 파일

- `KDT_2026/2026_Python/day11/h-01.py` — 공공데이터포털 "대구광역시 중구 맛집 현황" JSON API 호출: `pip install httpx`·`pip install xmltodict` 주석(httpx는 `.json()` 변환만 지원·XML은 xmltodict), `import httpx`·`import pandas as pd`, `service_key` 변수(노트에서는 값 가림), `def test1()` 안에서 고정 주소 `https://api.odcloud.kr/api/15052602/v1/uddi:…`에 `+=`로 `?page=1`·`&perPage=147`·f-문자열 `&serviceKey={service_key}` 조립 → `httpx.get(url)` `<Response [200 OK]>` → `response.json()`(`{"currentCount", "data": [...], ...}`) → `pd.DataFrame(response_json['data'])` → `df.info()`, `test1()` 호출

## 관련 노트

[[Python 정리본 인덱스]] · [[Python day10 Playwright 클릭으로 동적 페이지네이션 크롤링 실습]] · [[Python day10 페이징 반복으로 베스트셀러 목록 크롤링]] · [[Python day10 requests·BeautifulSoup으로 정적 페이지 크롤링]] · [[Python day08 판다스 데이터프레임 생성과 인덱싱·필터링]] · [[Python day04 예외 처리 try·except·else·finally]] · [[Python day02 딕셔너리 선언과 키로 값 다루기]] · [[KDT_2026 학습 지도]]
