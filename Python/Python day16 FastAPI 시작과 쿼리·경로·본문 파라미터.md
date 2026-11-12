---
출처: Claude 분석
원본: KDT_2026/2026_Python/day16/f-01.py, day16/f-02.py
작성일: 2026-11-12
tags: [학습, python]
---

# Python day16 — FastAPI 시작과 쿼리·경로·본문 파라미터

> 실습 파일: `day16/f-01.py`, `day16/f-02.py`
> 허브: [[Python 정리본 인덱스]] · 이전: [[Python day11 httpx로 착한가격업소 API 수집과 업종별 평균 가격 실습]] · 다음: [[Python day16 FastAPI APIRouter로 컨트롤러·서비스 파일 분리]]

day11까지는 남이 열어 둔 API를 `httpx`로 **부르는 쪽**이었다. day16은 방향이 뒤집힌다 — 이번에는 내가 API를 **열어 주는 쪽**이 된다. 도구는 FastAPI로, 파이썬 함수에 데코레이터 한 줄을 얹으면 그 함수가 곧 주소(엔드포인트)가 되고, 함수의 매개변수가 곧 요청 파라미터가 된다. 서버를 띄우는 일은 `uvicorn`이 맡는다. day12~15에서 사이킷런 모델을 `joblib`로 저장해 두었으니, 그 모델을 불러 예측 결과를 돌려주는 창구가 바로 이런 서버다(AI 폴더의 day15 연습 노트 끝에 "FastAPI 서빙"이라고 적어 둔 자리). 코드 전체가 스무 줄 남짓인데, 이 안에 **쿼리스트링·경로·본문** 세 가지 통신 방식이 전부 들어 있다.

## 1. 배운 내용

### 1-1. 설치와 두 라이브러리의 역할

```bash
pip install fastapi
pip install uvicorn
```

| 라이브러리 | 역할 | 비유 |
| --- | --- | --- |
| `fastapi` | 주소와 함수를 묶고, 요청 파라미터를 검사해 함수에 넣어 주고, 반환값을 JSON으로 바꾼다 | 안내 데스크 — 누가 무슨 용건으로 왔는지 가려 담당자에게 넘긴다 |
| `uvicorn` | 포트를 열고 HTTP 요청을 받아 FastAPI 앱에 전달하는 **서버**(ASGI 서버) | 건물 문 — 문이 열려 있어야 손님이 데스크까지 온다 |

FastAPI 자체는 서버가 아니다. 앱(라우팅 규칙 묶음)을 만드는 라이브러리고, 실제로 포트에서 기다리는 것은 `uvicorn`이다. Spring Boot가 내장 톰캣을 품고 있는 것과 달리, 파이썬 쪽은 이 둘을 따로 설치해 조합한다.

### 1-2. 가장 작은 서버 — `f-01.py`

```python
from fastapi import FastAPI
import uvicorn

app = FastAPI()                       # 앱 객체 하나 — 라우트는 전부 여기에 붙는다

if __name__ == "__main__":
    uvicorn.run("f-01:app", host="127.0.0.1", port=8000, reload=True)
```

| 인자 | 뜻 |
| --- | --- |
| `"f-01:app"` | `모듈이름:변수이름` 문자열. `f-01.py` 파일 안의 `app` 객체를 띄우라는 뜻 |
| `host="127.0.0.1"` | 내 컴퓨터에서만 접속 허용(localhost). 다른 기기에서 받으려면 `"0.0.0.0"` |
| `port=8000` | 열 포트. 브라우저 주소는 `http://127.0.0.1:8000` |
| `reload=True` | 파일을 저장할 때마다 서버를 자동 재시작 — 개발 중에만 켠다 |

`"f-01:app"`처럼 객체가 아니라 **문자열**로 넘기는 이유는 `reload=True` 때문이다. 자동 재시작은 서버 프로세스를 새로 띄우며 모듈을 다시 import해야 하는데, 객체를 직접 넘기면 다시 불러올 경로를 모른다. 그래서 `reload`를 켤 때는 반드시 import 문자열을 쓴다. 모듈 이름에 하이픈이 있으면 `import f-01` 같은 문장은 문법상 쓸 수 없지만, 이렇게 문자열 경로로 찾는 방식에서는 문제없이 열린다.

`if __name__ == "__main__":` 블록에 넣은 것은 day05 이후 계속 보던 관용구 그대로다 — 이 파일을 직접 실행할 때만 서버를 띄우고, 다른 파일이 import할 때는 띄우지 않는다. 터미널에서 `uvicorn f-01:app --reload`로 띄우는 방법도 있는데, 이 블록 덕분에 VS Code 실행 버튼 하나로도 같은 결과가 난다.

실행하면 터미널에 `Uvicorn running on http://127.0.0.1:8000`이 찍힌다. 아직 주소를 하나도 안 붙였으니 브라우저로 열면 `{"detail":"Not Found"}`가 나오는데, 이 404 응답 자체가 "서버는 떠 있다"는 증거다.

### 1-3. 첫 라우트 — `@app.get("/")`와 `async def`

```python
@app.get("/")
async def index():            # async def 함수명() : 비동기 함수 선언
    return "안녕 파이썬 웹"
```

| 조각 | 뜻 |
| --- | --- |
| `@app.get("/")` | "GET 방식으로 `/` 주소에 요청이 오면 아래 함수를 실행하라" — 데코레이터가 함수를 앱에 등록 |
| `async def` | 비동기 함수(코루틴). day10 Playwright에서 `await`와 짝으로 쓰던 그 문법 |
| `return "안녕 파이썬 웹"` | 반환값이 그대로 응답 본문이 된다. 문자열이면 JSON 문자열 `"안녕 파이썬 웹"`으로 |

브라우저에서 `http://127.0.0.1:8000/`을 열면 따옴표가 붙은 `"안녕 파이썬 웹"`이 보인다. FastAPI는 반환값을 무조건 **JSON으로 직렬화**하기 때문에 문자열도 JSON 문자열이 된다. 딕셔너리를 돌려주면 JSON 객체(`{…}`), 리스트면 JSON 배열(`[…]`)이 된다 — day11에서 `.json()`으로 받던 모양을 이번엔 내가 만들어 보내는 셈이다.

`async def`로 쓴 이유는 FastAPI가 비동기 서버(ASGI) 위에서 돌기 때문이다. 함수 안에서 `await`로 기다리는 동안 다른 요청을 처리할 수 있다. 다만 `async`를 붙이지 않은 일반 `def`도 등록이 되고, 그 경우 FastAPI가 별도 스레드에서 돌려 준다. 지금 단계에선 "라우트 함수는 `async def`로 쓴다"로 외워 두고, 안에서 `await`할 것이 생길 때 그 의미가 살아난다.

### 1-4. 쿼리 파라미터 — 경로에 없는 매개변수는 `?키=값`으로

```python
@app.get("/user")
async def user(name, age: int):
    info = {'name': name, 'age': age, 'msg': '쿼리통신 성공'}
    return info
```

```text
http://127.0.0.1:8000/user?name=홍길동&age=20
→ {"name":"홍길동","age":20,"msg":"쿼리통신 성공"}
```

규칙은 하나다. **함수 매개변수 중 경로(`"/user"`)에 등장하지 않는 이름은 전부 쿼리스트링에서 찾는다.** `name`과 `age`가 경로에 없으니 `?name=…&age=…`로 받는다. day10·11에서 예스24 주소의 `pageNumber`, 공공데이터포털의 `page`·`perPage`를 **읽던** 자리를 이번엔 내가 **정의**하는 것이다.

| 매개변수 | 타입 힌트 | 받는 값 |
| --- | --- | --- |
| `name` | 없음 | 문자열 그대로 (`"홍길동"`) |
| `age: int` | `int` | 문자열 `"20"`을 정수 `20`으로 **변환해서** 넣는다 |

타입 힌트가 하는 일이 여기서 처음 실전이 된다. 쿼리스트링은 원래 전부 문자열인데, `age: int`라고 적어 두면 FastAPI가 알아서 `int`로 바꾸고, `?age=abc`처럼 바꿀 수 없는 값이 오면 함수를 실행하지 않고 **422 응답**(`"Input should be a valid integer"`)을 돌려준다. 기본값이 없는 매개변수는 필수라서 `?name=홍길동`만 보내면 `age`가 빠졌다는 422가 온다. 검증 코드를 한 줄도 안 썼는데 검증이 되는 것 — 이것이 FastAPI를 고르는 첫 번째 이유다.

### 1-5. 경로 파라미터 — 주소의 일부가 값이 된다

```python
@app.get("/item/{name}/{age}")
async def item(name: str, age: int | None = None):
    return {name: name, age: age, 'msg': "경로 통신 성공"}
```

```text
http://127.0.0.1:8000/item/사과/3
→ {"사과":"사과","3":3,"msg":"경로 통신 성공"}
```

경로 문자열 안의 `{name}`·`{age}` 중괄호 자리가 **변수 칸**이다. 요청 주소의 그 자리에 들어온 글자가 같은 이름의 매개변수로 들어온다. `?키=값`이 붙지 않고 주소 자체가 데이터를 품는 방식이라, "3번 상품", "홍길동의 프로필"처럼 **대상을 가리키는 값**에 어울린다.

| 구분 | 쿼리 파라미터 | 경로 파라미터 |
| --- | --- | --- |
| 주소 모양 | `/user?name=홍길동&age=20` | `/item/사과/3` |
| 선언 | 경로에 없는 매개변수 | 경로의 `{이름}`과 같은 이름의 매개변수 |
| 어울리는 용도 | 검색 조건·페이지 번호·정렬 기준(선택적인 것) | 자원의 식별자(이 항목·이 사용자) |
| 생략 | 기본값을 주면 생략 가능 | 주소의 일부라 **항상 필수** |

`int | None = None`은 파이썬 3.10부터 쓰는 "정수 또는 None, 기본값 None" 표기다. 쿼리 파라미터에 이렇게 붙이면 "안 보내도 되는 선택 값"이 되는데, 경로 파라미터는 주소에서 빠질 수가 없어 기본값을 적어도 항상 들어온다. 기본값으로 선택·필수를 가르는 것은 쿼리 쪽 이야기라고 구분해 두면 된다.

딕셔너리 키에 변수를 넣으면 **변수의 값**이 키가 된다. `{name: name}`에서 `name`이 `"사과"`이면 키도 `"사과"`가 되어 위 출력처럼 `{"사과":"사과"}`가 찍힌다. 키를 글자 그대로 `"name"`으로 두고 싶으면 따옴표를 붙여 `{'name': name}`으로 쓴다 — day02 딕셔너리에서 본 "키 자리에도 식이 올 수 있다"는 규칙 그대로다. 숫자 `3`이 키로 들어가도 JSON으로 나갈 때는 문자열 `"3"`이 되는 것도 함께 보인다(JSON의 키는 항상 문자열).

### 1-6. 본문(body) 파라미터 — POST로 JSON 받기

```python
@app.post("/product")
async def product(product: dict):
    product['msg'] = "본문 통신 성공"
    return product
```

```text
POST http://127.0.0.1:8000/product
본문: {"name": "노트북", "price": 1500000}
→ {"name":"노트북","price":1500000,"msg":"본문 통신 성공"}
```

세 번째 통로다. `@app.post`로 바꾸고 매개변수 타입을 `dict`로 적으면, FastAPI는 "이건 쿼리도 경로도 아니고 **요청 본문의 JSON**"이라고 판단해 본문을 파싱한 딕셔너리를 넣어 준다. 받은 딕셔너리에 키 하나를 더해 돌려주니, 보낸 JSON에 `msg`가 추가되어 돌아온다.

| 매개변수 타입 | FastAPI의 판단 |
| --- | --- |
| `str`·`int`·`float`·`bool` 같은 단일 값 | 경로에 있으면 경로 파라미터, 없으면 쿼리 파라미터 |
| `dict`·`list`·pydantic 모델 같은 묶음 값 | 요청 본문(JSON) |

GET 요청은 브라우저 주소창으로 바로 시험할 수 있지만 POST는 본문을 실어야 해서 주소창으로는 안 된다. 서버를 띄운 뒤 `http://127.0.0.1:8000/docs`를 열면 FastAPI가 자동으로 만들어 주는 **Swagger UI**가 뜨고, 거기서 `/product`를 펼쳐 JSON을 적고 Execute를 누르면 된다. 네 개의 라우트와 각 파라미터의 타입이 코드 한 줄 안 쓰고 문서로 정리되어 있다 — 이것이 FastAPI를 고르는 두 번째 이유다. day11에서 공공데이터포털의 API 명세 문서를 읽고 파라미터를 알아냈는데, 내 서버는 그 문서를 자동으로 갖는다.

### 1-7. 세 통로를 한눈에

| 통로 | 데코레이터 | 선언 | 요청 예 | 수업 코드의 `msg` |
| --- | --- | --- | --- | --- |
| 쿼리스트링 | `@app.get("/user")` | 경로에 없는 매개변수 `name, age: int` | `/user?name=홍길동&age=20` | 쿼리통신 성공 |
| 경로 | `@app.get("/item/{name}/{age}")` | 경로 `{…}`와 같은 이름 | `/item/사과/3` | 경로 통신 성공 |
| 본문 | `@app.post("/product")` | `product: dict` | POST + JSON 본문 | 본문 통신 성공 |

흐름은 전부 같다. **요청 → 데코레이터가 주소·메소드로 함수 선택 → 매개변수 이름·타입으로 값을 꺼내 변환·검증 → 함수 실행 → 반환값을 JSON으로.** 백엔드 수업의 Spring 컨트롤러로 치면 `@GetMapping`·`@RequestParam`·`@PathVariable`·`@PostMapping`+`@RequestBody`에 각각 대응한다(Spring 폴더 노트 참고 — 평문 언급). 파이썬 쪽은 어노테이션 대신 "매개변수가 경로에 있나, 타입이 묶음인가"로 자동 판단한다는 점이 다르다.

## 2. 추가로 알면 좋은 활용법

### 2-1. 본문은 `dict`보다 pydantic 모델로 받는다

```python
from pydantic import BaseModel

class Product(BaseModel):
    name: str
    price: int
    stock: int = 0          # 기본값 → 선택 필드

@app.post("/product")
async def product(product: Product):
    return {"name": product.name, "total": product.price * product.stock}
```

`dict`로 받으면 아무 JSON이나 들어오고 키 이름이 틀려도 함수 안에서 `KeyError`로 터진다. `BaseModel`을 상속한 클래스로 받으면 필드 이름·타입·필수 여부가 **본문에도** 적용되어, `price`에 문자열이 오거나 `name`이 빠지면 422로 막힌다. day05에서 배운 클래스 문법에 타입 힌트만 얹은 모양이고, `/docs`에 요청 본문 예시까지 자동으로 그려진다. 응답 모양을 고정하고 싶으면 `@app.post("/product", response_model=Product)`로 반환값도 같은 모델로 검증·정리할 수 있다.

### 2-2. 쿼리 파라미터에 기본값·제약 붙이기

```python
from fastapi import Query

@app.get("/books")
async def books(page: int = 1, size: int = Query(10, ge=1, le=100), q: str | None = None):
    return {"page": page, "size": size, "q": q}
```

| 선언 | 뜻 |
| --- | --- |
| `page: int = 1` | 기본값이 있으면 **선택** 파라미터 — 안 보내면 1 |
| `Query(10, ge=1, le=100)` | 기본값 10, 범위 1~100 밖이면 422 |
| `q: str | None = None` | 있어도 되고 없어도 되는 검색어 |

day10·11에서 `page`·`perPage`를 붙여 부르던 API를 이제 내가 만들 때의 모양이다. 경로 파라미터에도 `Path(..., gt=0)`처럼 같은 식으로 제약을 건다.

### 2-3. 오류 응답은 `HTTPException`으로

```python
from fastapi import HTTPException

items = {1: "사과", 2: "배"}

@app.get("/items/{item_id}")
async def get_item(item_id: int):
    if item_id not in items:
        raise HTTPException(status_code=404, detail="없는 상품입니다")
    return {"id": item_id, "name": items[item_id]}
```

없는 자원을 달라고 하면 `return`이 아니라 `raise`로 끊는다. day11에서 정리한 상태 코드표(401·403·404·429·500)의 반대편 — 이번엔 내가 코드를 **골라서 보내는** 쪽이다. 함수가 정상 종료하면 200, `HTTPException`을 던지면 그 코드, 처리 안 된 예외가 나면 500이 된다. 성공 코드를 바꾸고 싶으면 `@app.post("/product", status_code=201)`처럼 데코레이터에 적는다.

### 2-4. 저장해 둔 모델을 서빙하기

```python
import joblib
from pydantic import BaseModel

model = joblib.load("fish_model.pkl")       # 서버 시작 때 한 번만 읽는다

class Fish(BaseModel):
    Weight: float
    Length: float
    Diagonal: float
    Height: float
    Width: float

@app.post("/predict")
async def predict(fish: Fish):
    row = [fish.Weight, fish.Length, fish.Diagonal, fish.Height, fish.Width]
    return {"species": model.predict([row])[0]}   # 2차원(행 1개)으로 넣는다
```

day14~15에서 `joblib.dump`로 저장한 파이프라인(스케일러·인코더까지 한 덩어리)을 `load`로 올려 두고, 본문으로 받은 특성 한 줄을 `predict`에 넣어 돌려주면 끝이다. 모델을 **함수 밖에서** 한 번만 읽어 두는 것이 요점 — 요청마다 `load`하면 피클 파일을 매번 읽어 느려진다. 입력 열 이름·순서는 학습 때와 같아야 하므로 pydantic 모델의 필드를 학습 데이터의 열과 똑같이 맞춘다. 프론트(React)에서 `fetch`로 이 주소에 POST하면 화면에서 예측값을 받는 구조가 된다.

### 2-5. 프론트에서 부를 때 — CORS

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],   # Vite 개발 서버
    allow_methods=["*"],
    allow_headers=["*"],
)
```

브라우저에서 다른 출처(포트가 달라도 다른 출처)의 API를 `fetch`하면 CORS 정책에 걸려 막힌다. 서버 쪽에서 허용할 출처를 적어 주는 미들웨어가 이것이다. 파이썬 스크립트나 Swagger UI로 부를 때는 걸리지 않다가 React에서 붙이는 순간 만나는 벽이라 미리 적어 둔다.

### 2-6. 라우트가 늘어나면 `APIRouter`로 파일 나누기

```python
# routers/products.py
from fastapi import APIRouter
router = APIRouter(prefix="/products", tags=["products"])

@router.get("/")
async def list_products(): ...

# main.py
from routers import products
app.include_router(products.router)
```

한 파일에 라우트를 계속 붙이면 수업 코드처럼 금방 길어진다. 주제별로 `APIRouter`를 만들어 `prefix`를 걸고 `main.py`에서 모으면 Spring의 컨트롤러 클래스를 나누는 것과 같은 효과가 난다. `tags`는 `/docs` 화면에서 묶음 제목이 된다.

## 3. 더 나아가 알면 좋은 것

### 3-1. ASGI와 WSGI — `uvicorn`이 필요한 이유

Flask·Django(전통 방식)는 **WSGI**라는 동기 규약 위에서 돈다 — 요청 하나를 끝낼 때까지 그 작업자는 다른 일을 못 한다. FastAPI는 Starlette이라는 비동기 프레임워크 위에 만들어져 **ASGI** 규약을 쓰고, 그래서 `async def` 라우트가 `await`로 DB·외부 API를 기다리는 동안 같은 프로세스가 다른 요청을 받는다. `uvicorn`은 그 ASGI 규약을 구현한 서버다. day10에서 Playwright를 `asyncio.run`으로 돌리며 본 이벤트 루프가 서버 안에서 계속 돌고 있다고 보면 된다. 라우트 안에서 `time.sleep`·동기 DB 드라이버처럼 **막히는** 호출을 하면 이 장점이 사라지므로, 그런 코드는 일반 `def`로 두거나(스레드풀로 넘어감) 비동기 라이브러리(`httpx.AsyncClient`, `asyncpg`)로 바꾼다.

### 3-2. pydantic — 타입 힌트를 검증기로 바꾸는 엔진

쿼리·경로·본문의 변환과 422 응답은 전부 pydantic이 한다. 타입 힌트는 원래 파이썬이 실행 시점에 무시하는 주석인데, pydantic은 그 힌트를 읽어 실제 검증·변환 코드로 만든다. `EmailStr`·`conint(gt=0)`·`field_validator` 같은 세부 검증, `model_dump()`로 딕셔너리 변환, 설정 파일 읽기(`BaseSettings` — day11의 `.env` 인증키 분리를 여기에 얹는다)까지 쓰임새가 넓다. 현재는 v2가 기준이라 예전 글의 `.dict()`·`@validator`는 `.model_dump()`·`@field_validator`로 바뀐 점을 기억해 둔다.

### 3-3. 의존성 주입 `Depends`

```python
from fastapi import Depends

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/users")
async def users(db = Depends(get_db)): ...
```

DB 세션·로그인 사용자·공통 쿼리 파라미터처럼 여러 라우트가 같이 쓰는 재료를 함수로 빼고 `Depends`로 꽂는다. Spring의 `@Autowired` 생성자 주입에 대응하는 자리이고, `yield`를 쓰면 요청이 끝난 뒤 정리(`close`)까지 한 함수에서 처리된다.

### 3-4. 배포 — 개발 서버 그대로 올리지 않는다

`reload=True`·`127.0.0.1`은 개발용이다. 실제로 내놓을 때는 `host="0.0.0.0"`, `reload` 끄기, `uvicorn --workers N`이나 `gunicorn -k uvicorn.workers.UvicornWorker`로 프로세스 여러 개, 앞단에 nginx 같은 리버스 프록시, Docker 이미지로 묶기 순서로 간다. 환경변수로 포트·키를 받고, `/docs`는 운영에서 끄거나 인증 뒤로 숨긴다.

### 3-5. 테스트 — `TestClient`

```python
from fastapi.testclient import TestClient
client = TestClient(app)

def test_user():
    r = client.get("/user", params={"name": "홍길동", "age": 20})
    assert r.status_code == 200
    assert r.json()["age"] == 20
```

서버를 띄우지 않고 앱 객체에 바로 요청을 넣어 본다. `httpx` 기반이라 day11에서 쓰던 `get`·`params`·`.json()` 그대로다. `pytest`와 묶으면 라우트를 고칠 때마다 전체를 자동으로 다시 확인할 수 있다.

### 3-6. 다음에 볼 키워드

- `BackgroundTasks` — 응답을 먼저 보내고 메일 발송·로그 저장 같은 뒷일은 따로
- `WebSocket` 라우트 — 실시간 양방향 통신
- SQLModel / SQLAlchemy 2.0 async — FastAPI와 짝으로 쓰는 ORM
- OAuth2 + JWT (`OAuth2PasswordBearer`) — 로그인·토큰 인증
- `lifespan` 이벤트 — 서버 시작·종료 때 모델 로드·연결 정리
- OpenAPI 스키마(`/openapi.json`)로 프론트 타입 자동 생성

## 실습 파일

- `KDT_2026/2026_Python/day16/f-01.py` — 가장 작은 FastAPI 서버: `FastAPI()` 앱 객체 생성, `if __name__ == "__main__":` 아래 `uvicorn.run("f-01:app", host="127.0.0.1", port=8000, reload=True)`
- `KDT_2026/2026_Python/day16/f-02.py` — 라우트 네 개: `@app.get("/")` 문자열 반환(`async def` 주석), `@app.get("/user")` 쿼리 파라미터 `name, age: int` → 딕셔너리(`'msg': '쿼리통신 성공'`), `@app.get("/item/{name}/{age}")` 경로 파라미터 `name: str, age: int | None = None`(`"경로 통신 성공"`), `@app.post("/product")` 본문 `product: dict`에 `msg` 추가 반환(`"본문 통신 성공"`)

## 관련 노트

[[Python 정리본 인덱스]] · [[Python day11 httpx로 착한가격업소 API 수집과 업종별 평균 가격 실습]] · [[Python day16 FastAPI APIRouter로 컨트롤러·서비스 파일 분리]] · [[Python day11 httpx로 공공데이터 API 호출과 JSON 데이터프레임 변환]] · [[Python day10 Playwright 비동기로 동적 페이지 크롤링]] · [[Python day05 클래스 정의와 생성자·메소드]] · [[Python day02 딕셔너리 선언과 키로 값 다루기]] · [[KDT_2026 학습 지도]]
