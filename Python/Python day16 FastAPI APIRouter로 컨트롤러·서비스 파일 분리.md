---
출처: Claude 분석
원본: KDT_2026/2026_Python/day16/AppStart.py, day16/Controller.py, day16/Service.py
작성일: 2026-11-12
tags: [학습, python]
---

# Python day16 — FastAPI APIRouter로 컨트롤러·서비스 파일 분리

> 실습 파일: `day16/AppStart.py`, `day16/Controller.py`, `day16/Service.py`
> 허브: [[Python 정리본 인덱스]] · 이전: [[Python day16 FastAPI 시작과 쿼리·경로·본문 파라미터]] · 다음: [[Python day16 FastAPI StaticFiles로 학습 모델 예측 웹 서비스 만들기]]

앞 노트의 `f-02.py`는 앱 객체·라우트·실행 코드가 한 파일에 다 들어 있었다. 라우트가 네 개일 때는 그래도 되지만, 상품·회원·주문처럼 주제가 늘어나면 한 파일이 금방 수백 줄이 된다. 이번 세 파일은 그 한 파일을 **역할별로 셋으로 쪼개는 가장 작은 형태**다. `AppStart.py`는 앱을 만들고 서버를 띄우기만 하고, `Controller.py`는 주소를 받고, `Service.py`는 실제 데이터를 만든다. Spring 수업에서 보던 Controller → Service 계층이 파이썬에서는 **모듈(파일) 단위의 import 사슬**로 표현된다는 점이 핵심이다. 데이터는 아직 DB가 아니라 day08의 판다스 데이터프레임인데, 덕분에 "데이터프레임을 JSON 배열로 돌려주는" 한 줄과, 그 표를 테이블처럼 다루는 저장·수정·삭제(`concat`·`loc`·불리언 필터)까지 같이 배우게 된다.

## 1. 배운 내용

### 1-1. 세 파일의 역할

| 파일 | 담는 것 | 하는 일 | Spring으로 치면 |
| --- | --- | --- | --- |
| `AppStart.py` | `app = FastAPI()`, `uvicorn.run(…)`, `include_router` | 앱을 만들고 라우터를 붙이고 서버를 띄운다 | `@SpringBootApplication` 메인 클래스 |
| `Controller.py` | `router = APIRouter(prefix="/api")`, `@router.get("/items")`·`@router.post("/save")`·`@router.put("/update")`·`@router.delete("/delete")` | 주소와 HTTP 메소드를 받아 서비스를 호출하고 결과를 돌려준다 | `@RestController` |
| `Service.py` | `class ItemService`(`items`·`save`·`update`·`delete`), `item_service = ItemService()` | 데이터를 들고 있다가 조회·저장·수정·삭제한다 | `@Service` |

화살표 방향이 중요하다. **AppStart → Controller → Service** 한 방향으로만 import한다. 서비스는 컨트롤러를 모르고, 컨트롤러는 앱 객체를 모른다. 이 방향이 지켜지면 파일이 몇 개로 늘어나도 "누가 누구를 부르는가"가 한눈에 보이고, 서로 import하다 막히는 순환 import도 생기지 않는다.

### 1-2. `AppStart.py` — 앱 생성, 라우터 연결, 서버 실행

```python
from fastapi import FastAPI
import uvicorn

app = FastAPI()

if __name__ == "__main__":
    uvicorn.run('AppStart:app', host="127.0.0.1", port=8000, reload=True)

# [2] 컨트롤러에 라우터 연결
import Controller
app.include_router(Controller.router)
```

| 조각 | 뜻 |
| --- | --- |
| `'AppStart:app'` | `모듈이름:변수이름`. 앞 노트의 `"f-01:app"`과 같은 import 문자열이고, 이번엔 모듈 이름에 하이픈이 없어 `import AppStart`로도 부를 수 있는 평범한 모듈명이다 |
| `import Controller` | 같은 폴더의 `Controller.py`를 모듈로 불러온다. 이 한 줄이 실행되는 순간 `Controller.py` 전체가 위에서 아래로 실행되어 `router` 객체가 만들어진다 |
| `app.include_router(Controller.router)` | 라우터에 등록된 라우트들을 앱에 **통째로 붙인다**. 이 줄이 없으면 `Controller.py`의 `@router.get`은 앱과 아무 관계가 없는 함수로 남는다 |

`reload=True`일 때 서버가 도는 방식을 떠올리면 코드 순서가 이해된다. `uvicorn.run`은 import 문자열 `'AppStart:app'`을 받아 **별도 프로세스에서 `AppStart` 모듈을 새로 import**한다. 그 프로세스에서는 `__name__`이 `"AppStart"`라 `if __name__ == "__main__":` 블록은 건너뛰고, 그 아래 `import Controller`와 `include_router`까지 모듈 전체가 끝까지 실행된다. 그래서 라우터 연결 코드가 어디에 있든 서버 프로세스 안에서는 `app`에 라우터가 붙은 상태로 서비스가 시작된다. 다만 읽는 사람 입장에서는 "앱을 다 꾸민 뒤 맨 아래에서 띄운다"는 순서가 자연스럽기 때문에, 관례적으로는 `include_router`를 먼저 쓰고 `if __name__` 블록을 파일 맨 끝에 둔다 (2-1에서 다시).

### 1-3. `Controller.py` — `APIRouter`와 `prefix`

```python
from fastapi import APIRouter

router = APIRouter(prefix="/api")

from Service import item_service

@router.get("/items")
async def items():
    return item_service.items()
```

| 조각 | 뜻 |
| --- | --- |
| `APIRouter(prefix="/api")` | 앱 객체 대신 쓰는 **작은 앱 조각**. 여기 등록한 모든 주소 앞에 `/api`가 자동으로 붙는다 |
| `@router.get("/items")` | 앞 노트의 `@app.get`과 모양이 같다. 대상이 `app`에서 `router`로 바뀌었을 뿐 |
| 최종 주소 | `prefix` + 경로 = `/api/items`. 브라우저에서 `http://127.0.0.1:8000/api/items` |
| `from Service import item_service` | `Service.py`가 만들어 둔 인스턴스를 그대로 가져온다 (클래스가 아니라 **객체**를 import) |
| `return item_service.items()` | 컨트롤러는 데이터를 직접 만들지 않고 서비스에 넘긴다. 반환된 리스트는 FastAPI가 JSON 배열로 바꿔 응답한다 |

`prefix`의 쓸모는 주소를 짧게 쓰는 것만이 아니다. 프론트(React 등)가 호출하는 주소를 `/api/…`로 통일해 두면, 나중에 nginx 같은 서버에서 "`/api`로 시작하는 요청만 파이썬 서버로" 하는 식의 분기가 쉬워진다. Spring 수업에서 클래스 위에 `@RequestMapping("/api")`를 걸고 메소드마다 `@GetMapping("/items")`를 붙이던 것과 같은 구조다.

### 1-4. `Service.py` — 클래스와 모듈 수준 인스턴스

```python
import pandas as pd

class ItemService:
    def __init__(self):
        self.df = pd.DataFrame([
            {'id': 1, 'name': '콜라',   'price': 1000},
            {'id': 2, 'name': '사이다', 'price': 1500},
        ])

    def items(self):
        return self.df.to_dict(orient="records")

item_service = ItemService()
```

| 조각 | 뜻 |
| --- | --- |
| `class ItemService` | day05에서 배운 클래스 그대로. 생성자에서 데이터를 준비하고, 메소드가 그 데이터를 가공한다 |
| `self.df = pd.DataFrame([...])` | 딕셔너리 리스트로 데이터프레임을 만든다 (day08 1-1). 지금은 DB 대신 메모리에 든 표 두 줄 |
| `self.df.to_dict(orient="records")` | 데이터프레임을 **행 하나 = 딕셔너리 하나**인 리스트로 바꾼다 → `[{'id': 1, 'name': '콜라', 'price': 1000}, {...}]` |
| `item_service = ItemService()` | 클래스 정의 **바깥**에서 인스턴스를 하나 만들어 모듈 변수에 담는다 |

마지막 줄이 이 파일의 핵심이다. 파이썬은 한 번 import한 모듈을 `sys.modules`에 캐시해 두고 다시 실행하지 않는다. 그래서 `Service.py` 맨 아래의 `item_service = ItemService()`는 **서버 프로세스 전체에서 딱 한 번** 실행되고, 어느 파일에서 `from Service import item_service`를 하든 같은 객체를 받는다. 데이터프레임을 요청마다 새로 만드는 게 아니라 처음 한 번 만들어 두고 계속 쓰는 셈이라, 앞 노트 2-4에서 `joblib.load`를 함수 밖에서 한 번만 하라고 적어 둔 것과 같은 원리다. Spring이 `@Service` 빈을 하나만 만들어 주입해 주는 것(싱글턴)을, 파이썬은 모듈 캐시로 얻는다.

### 1-5. 저장·수정·삭제 — 세 통로를 다 쓰는 CRUD 라우트

조회 하나뿐이던 컨트롤러에 저장·수정·삭제가 붙으면서 앞 노트에서 배운 **본문 파라미터와 쿼리 파라미터**가 한 파일 안에서 나란히 쓰인다.

```python
@router.post("/save")
async def save(item: dict):            # 본문 JSON → dict
    return item_service.save(item)

@router.put("/update")
async def update(item: dict):          # 본문 JSON → dict
    return item_service.update(item)

@router.delete("/delete")
async def delete(id: int):             # 경로에 없으니 쿼리 → ?id=1
    return item_service.delete(id)
```

| 라우트 | 메소드 | 호출 주소 | 값이 들어오는 통로 | 서비스 호출 |
| --- | --- | --- | --- | --- |
| `items` | GET | `/api/items` | 없음 | `item_service.items()` |
| `save` | POST | `/api/save` + 본문 `{"id":3,"name":"환타","price":2000}` | 본문(`dict`) | `item_service.save(item)` |
| `update` | PUT | `/api/update` + 본문 `{"id":1,"name":"펩시","price":3000}` | 본문(`dict`) | `item_service.update(item)` |
| `delete` | DELETE | `/api/delete?id=1` | 쿼리(`id: int`) | `item_service.delete(id)` |

매개변수 타입만 보고 FastAPI가 통로를 고른다는 규칙이 여기서 그대로 적용된다. `dict`처럼 묶음 타입이면 본문에서, `int` 같은 단일 값이고 경로에 `{id}` 칸이 없으면 쿼리스트링에서 읽는다. 그래서 삭제는 주소 뒤에 `?id=1`을 붙여 부른다. HTTP 메소드 네 개가 CRUD 동사 하나씩을 맡는 모양(GET 조회·POST 저장·PUT 수정·DELETE 삭제)도 이 표에서 한눈에 들어온다. 네 라우트 모두 컨트롤러는 한 줄짜리 전달자이고, 데이터를 실제로 건드리는 코드는 전부 `Service.py`에 있다.

### 1-6. `Service.py`의 저장·수정·삭제 — 데이터프레임을 테이블처럼 쓰기

```python
def save(self, item):
    saveDf = pd.DataFrame([item])                        # 딕셔너리 하나 → 한 줄짜리 표
    self.df = pd.concat([self.df, saveDf], ignore_index=True)
    return True

def update(self, item):
    uid = item.get('id')                                 # 수정 대상 id
    if uid not in self.df['id'].values:                  # 없는 id면 거절
        return False
    idx = self.df[self.df['id'] == uid].index            # 조건에 맞는 행의 인덱스
    self.df.loc[idx, item.keys()] = item.values()        # 그 행의 열들을 새 값으로
    return True

def delete(self, id):
    if id not in self.df['id'].values:
        return False
    self.df = self.df[self.df['id'] != id]               # 그 id만 뺀 표로 교체
    return True
```

| 동작 | 핵심 한 줄 | 이미 배운 문법 |
| --- | --- | --- |
| 저장 | `pd.DataFrame([item])` → `pd.concat([…], ignore_index=True)` | 딕셔너리 리스트로 표 만들기(day08 1-1)·세로 연결(day08 연결·병합) |
| 존재 확인 | `uid not in self.df['id'].values` | `in` 연산자(day02)와 `.values`가 넘파이 배열인 점(day08) |
| 행 찾기 | `self.df[self.df['id'] == uid].index` | 불리언 필터링(day08)·`.index` 속성 |
| 수정 | `self.df.loc[idx, 열들] = 값들` | `loc[행, 열] = 값` 여러 칸 수정(day08 1-4) |
| 삭제 | `self.df = self.df[self.df['id'] != id]` | 조건을 뒤집은 불리언 필터로 "남길 행"만 고르기 |

몇 가지를 짚어 두면 이렇다.

- **`pd.DataFrame([item])`의 대괄호** — 딕셔너리 하나를 리스트로 감싸야 "행 하나짜리 표"가 된다. 생성자에서 두 줄짜리 표를 만들 때와 같은 생성법이라, 저장은 "표 한 줄을 만들어 아래에 이어 붙이는 일"이 된다. `concat`은 새 표를 돌려주므로 `self.df =`로 다시 받아야 멤버변수가 바뀐다.
- **`.values`를 붙이는 이유** — `uid in self.df['id']`처럼 Series에 바로 `in`을 쓰면 값이 아니라 **인덱스 라벨**(0, 1, 2…)을 뒤진다. `.values`로 넘파이 배열을 꺼내야 실제 `id` 값들 중에 있는지를 묻게 된다. 판다스에서 자주 헷갈리는 자리라 따로 기억해 둘 만하다.
- **`.index`로 행 번호를 얻는 이유** — `loc`은 라벨로 칸을 찍는다. `self.df['id'] == uid` 불리언으로 행을 고른 뒤 `.index`를 꺼내면 그 행의 라벨이 나오고, 이걸 `loc[idx, …]`에 넣어 "그 행의 이 열들"을 한 번에 덮어쓴다. 열 쪽에는 들어온 딕셔너리의 키들을, 값 쪽에는 값들을 넘기므로 `name`·`price`뿐 아니라 보낸 키가 무엇이든 그 열이 갱신된다.
- **삭제가 "지우기"가 아니라 "빼고 다시 받기"인 점** — 넘파이·판다스의 필터링은 원본을 바꾸지 않고 새 배열·새 표를 돌려준다. 그래서 삭제도 `drop` 없이 "`id`가 다른 행만 골라 `self.df`에 다시 대입"으로 끝난다. day07에서 `x[x > 30]`이 원본을 두고 새 배열을 만들던 것과 같은 성질이다.
- **반환값 `True`/`False`** — 성공·실패를 불리언으로 돌려주면 FastAPI는 JSON `true`/`false`로 응답한다. `/docs`에서 없는 id로 수정·삭제를 눌러 보면 `false`가 돌아오는 것으로 거절 분기를 확인할 수 있다.

데이터가 `item_service` 객체 하나의 멤버변수에 들어 있으므로, 서버가 떠 있는 동안에는 저장한 행이 다음 요청에서도 보인다. 다만 `reload=True` 상태에서 파일을 저장하거나 서버를 다시 띄우면 생성자가 다시 돌아 처음 두 줄로 되돌아간다 — 메모리 표는 "DB가 생기기 전까지의 자리"라는 뜻이다.

### 1-7. `/docs`에서 네 라우트를 순서대로 눌러 보기

1. `GET /api/items` — 콜라·사이다 두 줄 확인
2. `POST /api/save` — Request body에 `{"id":3,"name":"환타","price":2000}` → `true`
3. `GET /api/items` — 세 줄로 늘어났는지 확인 (`ignore_index=True` 덕에 인덱스도 0·1·2로 이어진다)
4. `PUT /api/update` — `{"id":1,"name":"펩시","price":3000}` → `true`, 다시 조회하면 1번 행이 바뀜
5. `DELETE /api/delete?id=1` — `true`, 다시 조회하면 두 줄
6. 없는 id로 4·5를 다시 — `false`

이 순서 자체가 서비스 메소드 하나하나의 단위 시험이다. 나중에 `TestClient`로 자동화할 때도 같은 순서를 코드로 옮기면 된다.

### 1-8. `to_dict(orient=…)` — 응답 모양을 정하는 인자

`orient`를 무엇으로 주느냐에 따라 같은 표가 전혀 다른 JSON이 된다. 프론트가 받기 가장 편한 모양은 거의 항상 `records`다.

| `orient` | 결과 모양 | JSON으로 보면 |
| --- | --- | --- |
| `"records"` | 행마다 딕셔너리, 전체는 리스트 | `[{"id":1,"name":"콜라","price":1000}, {...}]` — 표를 그리기 좋다 |
| `"list"` | 열 이름 → 값 리스트 | `{"id":[1,2],"name":["콜라","사이다"],"price":[1000,1500]}` |
| `"dict"`(기본값) | 열 이름 → {인덱스: 값} | `{"id":{"0":1,"1":2}, ...}` — 인덱스가 키로 섞여 들어온다 |
| `"index"` | 인덱스 → 행 딕셔너리 | `{"0":{"id":1,...}, "1":{...}}` |

데이터프레임 자체를 `return`하면 FastAPI가 JSON으로 바꾸지 못해 오류가 난다. 반드시 `to_dict`나 `to_json`으로 **파이썬 기본 자료형(리스트·딕셔너리·숫자·문자열)**까지 내려 보내야 한다. 넘파이 숫자(`numpy.int64`)가 섞여 있어도 직렬화가 막히는 경우가 있어, 그럴 땐 `astype(int)`나 `.tolist()`로 먼저 바꿔 둔다.

### 1-9. 요청 한 번이 지나가는 길

```text
브라우저  GET http://127.0.0.1:8000/api/items
   │
   ▼
uvicorn (포트 8000에서 대기)  →  app (FastAPI)
   │  "/api"로 시작 → Controller.router 담당
   ▼
Controller.items()            ←  @router.get("/items")
   │  item_service.items() 호출
   ▼
Service.ItemService.items()   →  df.to_dict(orient="records")
   │  [{'id':1,...}, {'id':2,...}]
   ▼
FastAPI가 JSON 배열로 직렬화 → 응답
```

파일이 셋으로 나뉘어도 요청 하나는 이 한 줄기를 따라 내려갔다 올라온다. 어느 단계가 어느 파일인지 짚을 수 있으면, 나중에 오류가 났을 때 "주소가 안 맞는가(Controller), 데이터가 이상한가(Service), 서버가 안 떴는가(AppStart)"로 범위를 바로 좁힐 수 있다.

### 1-10. 실행할 때 주의할 점 — 어디서 실행하는가

`import Controller`는 **현재 작업 폴더(또는 실행한 스크립트의 폴더)**에서 `Controller.py`를 찾는다. VS Code 실행 버튼으로 `AppStart.py`를 돌리면 그 파일의 폴더가 검색 경로에 들어가므로 바로 된다. 터미널에서 띄울 때는 `day16` 폴더로 이동한 뒤 `uvicorn AppStart:app --reload`를 쳐야 한다. 상위 폴더에서 `uvicorn day16.AppStart:app`처럼 띄우면 `AppStart`가 `Controller`를 못 찾는 `ModuleNotFoundError`가 날 수 있다 — 이는 코드 문제가 아니라 모듈 검색 경로 문제다.

## 2. 추가로 알면 좋은 활용법

### 2-1. 흔히 쓰는 파일 배치

```text
app/
├── main.py            # app = FastAPI(), include_router들, 맨 아래 if __name__
├── routers/
│   ├── __init__.py
│   ├── items.py       # router = APIRouter(prefix="/api/items", tags=["items"])
│   └── users.py
├── services/
│   ├── __init__.py
│   └── item_service.py
└── schemas/
    └── item.py        # pydantic 모델
```

```python
# main.py
from fastapi import FastAPI
from routers import items, users

app = FastAPI()
app.include_router(items.router)
app.include_router(users.router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
```

수업의 세 파일을 그대로 폴더로 승격한 모양이다. 폴더를 패키지로 만들려면 `__init__.py`(빈 파일이어도 된다)를 넣는다. `include_router`를 모두 끝낸 뒤 맨 아래에서 서버를 띄우는 순서로 두면 "앱 구성 → 실행"이 읽는 순서와 같아진다. `tags`를 주면 `/docs` 화면에서 라우터별로 묶여 보인다.

### 2-2. 서비스는 `Depends`로 받는다

```python
from fastapi import APIRouter, Depends
from services.item_service import ItemService

def get_item_service() -> ItemService:
    return ItemService()          # 또는 미리 만든 인스턴스를 반환

router = APIRouter(prefix="/api")

@router.get("/items")
async def items(svc: ItemService = Depends(get_item_service)):
    return svc.items()
```

수업처럼 `from Service import item_service`로 직접 가져오는 방식은 짧고 분명하지만, 테스트할 때 가짜 서비스로 바꿔 끼우기가 어렵다. `Depends`로 받으면 `app.dependency_overrides[get_item_service] = lambda: FakeService()` 한 줄로 교체할 수 있다. Spring에서 필드에 `new`를 쓰지 않고 생성자 주입을 받는 것과 같은 이유다. 앞 노트 3-3의 `Depends`가 바로 이 자리에서 쓰인다.

### 2-3. 응답 모양을 pydantic으로 고정하기

```python
from pydantic import BaseModel

class Item(BaseModel):
    id: int
    name: str
    price: int

@router.get("/items", response_model=list[Item])
async def items():
    return item_service.items()
```

`to_dict(orient="records")`의 결과는 딕셔너리 리스트라 `list[Item]`에 바로 맞는다. `response_model`을 달면 `/docs`에 응답 스키마가 표로 뜨고, 데이터프레임에 열이 하나 더 있어도 모델에 없는 키는 응답에서 걸러진다. 프론트와 "이 주소는 이 모양"을 약속하는 문서가 코드 안에 생기는 셈이다.

### 2-4. 수업의 CRUD를 한 단계 다듬기

```python
from fastapi import HTTPException
from pydantic import BaseModel

class Item(BaseModel):
    id: int | None = None
    name: str
    price: int

@router.get("/items/{item_id}")
async def item(item_id: int):
    found = item_service.item(item_id)
    if found is None:
        raise HTTPException(status_code=404, detail="없는 상품")
    return found

@router.post("/items", status_code=201)
async def save(item: Item):
    return item_service.save(item.model_dump())

@router.delete("/items/{item_id}")
async def delete(item_id: int):
    if not item_service.delete(item_id):
        raise HTTPException(status_code=404, detail="없는 상품")
    return {"deleted": item_id}
```

```python
# Service.py 쪽
def item(self, item_id: int):
    row = self.df[self.df['id'] == item_id]
    return None if row.empty else row.iloc[0].to_dict()

def save(self, item: dict):
    if item.get('id') is None:                               # id를 서버가 매긴다
        item['id'] = int(self.df['id'].max()) + 1 if len(self.df) else 1
    self.df = pd.concat([self.df, pd.DataFrame([item])], ignore_index=True)
    return item
```

수업 코드에서 바뀌는 자리는 셋이다. **① 주소** — `/save`·`/update`·`/delete`처럼 동사를 주소에 쓰는 대신 자원 이름 `/items`를 두고 메소드로 동작을 구분하면(`POST /items`, `PUT /items/{id}`, `DELETE /items/{id}`) 앞 노트의 경로 파라미터가 자연스럽게 들어온다. **② 실패 응답** — `False` 대신 `HTTPException(404)`를 던지면 프론트가 상태 코드만 보고 실패를 알 수 있다. **③ 본문 검증** — `dict` 대신 pydantic 모델을 받으면 `price`에 문자열이 오거나 `name`이 빠졌을 때 FastAPI가 422로 막아 주고, `id`를 클라이언트가 아니라 서버가 매기도록 `None` 기본값을 둘 수 있다.

수정 쪽에서 한 가지 더 — `loc[idx, 열들] = 값들`에 딕셔너리의 `keys()`·`values()` 뷰를 바로 넘기는 것보다 `list(item.keys())`·`list(item.values())`처럼 **리스트로 바꿔 넘기는 편이 안전하다.** 판다스는 열 목록과 값 목록을 길이 있는 시퀀스로 기대하는데, 뷰 객체는 버전에 따라 "값 하나"로 해석돼 모든 칸에 같은 것이 들어갈 수 있다. 또 `'id'`까지 덮어쓰지 않으려면 `{k: v for k, v in item.items() if k != 'id'}`로 한 번 걸러 넘기는 습관을 들여 두면 좋다.

조건 필터링과 `pd.concat`은 day08에서 쓰던 그 문법이다. 서비스가 데이터프레임을 품고 있으니, 나중에 DB로 바꿀 때 `Service.py` 안쪽만 고치면 컨트롤러는 그대로 둘 수 있다 — 이것이 계층을 나누는 실질적인 이득이다.

### 2-5. 저장해 둔 모델을 서비스로 감싸기

```python
# services/predict_service.py
import joblib

class PredictService:
    def __init__(self, path="fish_model.pkl"):
        self.model = joblib.load(path)      # import 시 한 번만

    def predict(self, length: float, weight: float):
        return float(self.model.predict([[length, weight]])[0])

predict_service = PredictService()
```

AI 폴더 day14·15에서 `joblib`로 저장한 모델을 불러오는 코드를 서비스 클래스의 생성자에 두면, 모듈 캐시 덕분에 서버가 뜰 때 한 번만 읽힌다. 컨트롤러는 `predict_service.predict(...)`만 부른다. 앞 노트 2-4의 `/predict` 예제를 이 구조로 옮긴 것이다.

### 2-6. 라우터가 많아질 때 — `tags`와 `prefix` 중첩

```python
api = APIRouter(prefix="/api")
api.include_router(items.router)     # items.router의 prefix="/items" → /api/items
api.include_router(users.router)
app.include_router(api)
```

라우터는 라우터를 포함할 수 있다. 공통 접두사 `/api`를 상위 라우터 하나에 두고 하위 라우터들을 그 안에 모으면, 버전을 올릴 때(`/api/v2`) 한 곳만 바꾸면 된다.

## 3. 더 나아가 알면 좋은 것

### 3-1. 계층형 아키텍처 — Controller · Service · Repository

지금은 두 층(컨트롤러·서비스)이지만 실제 서비스는 한 층을 더 둔다. **Repository(또는 DAO)**가 DB와 직접 이야기하고, Service는 업무 규칙(할인 계산, 재고 확인 등)만, Controller는 요청·응답 변환만 맡는다. 층을 나누는 기준은 "바뀌는 이유가 다른가"다 — DB를 MySQL에서 PostgreSQL로 바꾸는 일과 할인 정책을 바꾸는 일이 서로 다른 파일을 건드리게 만드는 것이 목적이다. Spring 수업의 `@Repository`가 그 층이고, FastAPI에서는 SQLAlchemy·SQLModel 세션을 `Depends`로 받는 함수들이 보통 그 역할을 한다.

### 3-2. 모듈 싱글턴의 한계와 `lifespan`

`item_service = ItemService()`처럼 모듈을 import하는 순간 객체를 만드는 방식은 간단하지만, 생성에 시간이 걸리거나(큰 모델 로딩) 외부 자원(DB 연결)이 필요할 때는 "import만 했는데 DB에 붙는다"는 부작용이 생긴다. FastAPI의 `lifespan` 훅을 쓰면 서버 시작 직후에 초기화하고 종료 직전에 정리할 수 있고, 만들어진 객체는 `app.state`에 담아 `request.app.state.item_service`로 꺼내 쓴다. 테스트에서는 `lifespan`을 거치지 않고 가짜 객체를 넣을 수 있어 분리가 깔끔해진다.

### 3-3. 패키지·상대 import·순환 import

- 폴더를 패키지로 쓰면 `from .services import item_service`처럼 **상대 import**를 쓸 수 있다. 단, 상대 import는 그 파일을 스크립트로 직접 실행(`python Controller.py`)하면 깨지므로, 진입점(`main.py`)만 직접 실행한다
- A가 B를, B가 다시 A를 import하면 **순환 import**로 `ImportError`가 난다. 수업처럼 AppStart → Controller → Service 한 방향을 지키면 생기지 않는다. 꼭 양방향이 필요해 보이면 공통 부분을 셋째 모듈로 빼는 것이 정석이다
- `python -m uvicorn app.main:app`처럼 `-m`으로 띄우면 현재 폴더가 검색 경로에 들어가 패키지 import가 안정적이다

### 3-4. 설정 분리와 환경 변수

호스트·포트·모델 경로·DB 주소 같은 값은 코드에 박지 않고 `.env` 파일과 pydantic `BaseSettings`로 읽는다. day11에서 API 인증키를 코드 밖에 두던 것과 같은 원칙이며, 공개 저장소에 올릴 때 `.env`는 `.gitignore`에 넣는다.

### 3-5. 다음에 볼 키워드

- `APIRouter(dependencies=[...])` — 라우터 전체에 인증 의존성 걸기
- `app.state`와 `lifespan` — 시작·종료 시점 초기화
- SQLModel / SQLAlchemy — 데이터프레임 대신 DB 테이블을 서비스 뒤에 두기
- `dependency_overrides` + `TestClient` — 서비스 가짜로 바꿔 테스트
- 12-Factor App의 "설정은 환경에" — `BaseSettings`
- 프로젝트 템플릿 — `fastapi-template`, `full-stack-fastapi-template`의 폴더 구조 읽어 보기

## 실습 파일

- `KDT_2026/2026_Python/day16/AppStart.py` — `app = FastAPI()`, `if __name__ == "__main__":` 아래 `uvicorn.run('AppStart:app', host="127.0.0.1", port=8000, reload=True)`, `import Controller` 후 `app.include_router(Controller.router)`
- `KDT_2026/2026_Python/day16/Controller.py` — `router = APIRouter(prefix="/api")`, `from Service import item_service`, `@router.get("/items")` → `item_service.items()`, `@router.post("/save")`·`@router.put("/update")`의 `item: dict` 본문 → `save`·`update`, `@router.delete("/delete")`의 `id: int` 쿼리 → `delete`
- `KDT_2026/2026_Python/day16/Service.py` — `class ItemService`: 생성자에서 딕셔너리 두 개(`id`·`name`·`price`)로 `pd.DataFrame` 생성, `items()`가 `self.df.to_dict(orient="records")` 반환, `save()`가 `pd.DataFrame([item])`을 `pd.concat(ignore_index=True)`로 이어 붙임, `update()`가 `uid not in self.df['id'].values` 확인 후 `self.df[self.df['id'] == uid].index`로 찾은 행을 `loc[idx, item.keys()] = item.values()`로 덮어씀, `delete()`가 `self.df[self.df['id'] != id]`로 교체, 모듈 끝에서 `item_service = ItemService()`

## 관련 노트

[[Python 정리본 인덱스]] · [[Python day16 FastAPI 시작과 쿼리·경로·본문 파라미터]] · [[Python day05 클래스 정의와 생성자·메소드]] · [[Python day08 판다스 데이터프레임 생성과 인덱싱·필터링]] · [[KDT_2026 학습 지도]]
