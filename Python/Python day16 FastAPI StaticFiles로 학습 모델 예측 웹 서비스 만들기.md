---
출처: Claude 분석
원본: KDT_2026/2026_Python/ML_pracitce/total_practice/AppStart.py, ML_pracitce/total_practice/Controller.py, ML_pracitce/total_practice/Service.py, ML_pracitce/total_practice/static/index.html, ML_pracitce/total_practice/static/app.js, ML_pracitce/total_practice/static/style.css
작성일: 2026-11-12
tags: [학습, python]
---

# Python day16 — FastAPI StaticFiles로 학습 모델 예측 웹 서비스 만들기

> 실습 파일: `ML_pracitce/total_practice/AppStart.py`, `Controller.py`, `Service.py`, `static/index.html`, `static/app.js`, `static/style.css`
> 허브: [[Python 정리본 인덱스]] · 이전: [[Python day16 FastAPI APIRouter로 컨트롤러·서비스 파일 분리]] · 다음: (아직 없음)

앞 노트의 세 파일 구조(`AppStart` → `Controller` → `Service`)를 그대로 가져와, 서비스가 들고 있는 것을 **판다스 표 두 줄에서 학습이 끝난 머신러닝 모델**로 바꾼 종합 실습이다. 모델은 같은 폴더의 `sci.py`가 의료보험 자료로 학습해 `insurance_pipe.pkl`·`insurance_metrics.pkl`로 저장해 둔 것이고(그쪽은 AI 폴더의 "AI day16 의료비 데이터 전처리와 ColumnTransformer·다항 릿지 그리드서치 실습"에 정리, 학습 지도 경유), 이 노트는 그 `.pkl`을 **읽어서 웹 화면까지 연결하는 쪽**만 다룬다. 새로 등장하는 것은 셋이다. `joblib.load`를 서비스 생성자에 두는 것, `app.mount("/", StaticFiles(...))`로 FastAPI가 HTML·JS·CSS까지 직접 내주는 것, 그리고 브라우저 쪽에서 `axios.post`로 `/api/predict`를 부르는 작은 프론트다. 지금까지 `/docs` 화면으로만 눌러 보던 API를 처음으로 **진짜 화면**이 부른다.

## 1. 배운 내용

### 1-1. 폴더 한 장 — 누가 무엇을 만들고 누가 읽는가

```text
ML_pracitce/total_practice/
├── sci.py                   # 학습 스크립트 → .pkl 두 개 생성 (AI 노트)
├── insurance.csv            # 학습 자료
├── insurance_pipe.pkl       # 전처리+다항+릿지 파이프라인
├── insurance_metrics.pkl    # {'test_r2': 0.8828, 'cv_r2': 0.8198, 'best_params': …}
├── AppStart.py              # 앱 생성, 라우터 연결, 정적 파일 마운트, 서버 실행
├── Controller.py            # POST /api/predict
├── Service.py               # .pkl 로드, 입력 dict → DataFrame → 예측 → 응답 dict
└── static/
    ├── index.html           # 입력 폼 + 결과 카드
    ├── app.js               # BMI 계산, axios.post, 결과 표시
    └── style.css
```

학습(`sci.py`)과 서비스(`AppStart.py` 이하)는 **같은 파일을 쓰되 서로 import하지 않는다.** 학습은 한 번 돌려 `.pkl`을 남기고 끝나고, 서버는 그 `.pkl`만 읽는다. 학습 코드를 서버가 import하면 서버를 띄울 때마다 75번 학습이 다시 돌게 되므로, 둘 사이의 약속은 "파일 두 개"뿐이다.

### 1-2. `Service.py` — 생성자에서 `.pkl` 두 개 로드

```python
import pandas as pd
import joblib

class InsuranceService:
    def __init__(self):
        self.model   = joblib.load('./ML_pracitce/total_practice/insurance_pipe.pkl')
        self.metrics = joblib.load('./ML_pracitce/total_practice/insurance_metrics.pkl')
```

| 조각 | 뜻 |
| --- | --- |
| `joblib.load(...pipe.pkl)` | AI day14에서 `dump`한 것을 되읽는다. 결과는 `Pipeline` 객체 — `ColumnTransformer`·`PolynomialFeatures`·`Ridge`가 학습된 상태 그대로 들어 있다 |
| `joblib.load(...metrics.pkl)` | 딕셔너리 하나. 모델 자체는 "얼마나 맞히는지"를 모르므로 학습 때 계산한 점수를 따로 들고 온다 |
| 생성자에 두는 이유 | 모듈 끝의 `insurance_service = InsuranceService()`가 서버 프로세스에서 **한 번만** 실행된다(앞 노트 1-4의 모듈 캐시). 요청마다 디스크에서 4KB를 다시 읽지 않는다 |

앞 노트 2-5에서 "저장해 둔 모델을 서비스로 감싸기"로 미리 그려 본 모양이 그대로 수업 코드가 되었다. 서비스가 `self.df` 대신 `self.model`을 품는다는 점만 다르다.

### 1-3. `predict` — 입력 dict를 학습 때와 같은 모양의 DataFrame으로

```python
def predict(self, item):
    sample = pd.DataFrame([{
        'age'      : int(item['age']),
        'sex'      : item['sex'],
        'bmi'      : float(item['bmi']),
        'children' : int(item['children']),
        'smoker'   : item['smoker'],
        'region'   : item['region']
    }])
    charge = float(self.model.predict(sample)[0])
```

| 줄 | 왜 |
| --- | --- |
| `pd.DataFrame([{...}])` | 파이프라인 맨 앞의 `ColumnTransformer`가 **열 이름**으로 수치·범주를 가른다. 넘파이 2차원 배열이 아니라 학습 때와 열 이름이 같은 DataFrame 한 줄을 넣어야 한다. 대괄호는 앞 노트의 `pd.DataFrame([item])`과 같은 "행 하나짜리 표" 생성법 |
| `int(...)`·`float(...)` | 본문 JSON에서 온 값은 `"30"`처럼 문자열일 수도 있고, `age`가 `30.0`으로 올 수도 있다. 학습 자료의 자료형(`age` 정수·`bmi` 실수)에 맞춰 강제한다. `sex`·`smoker`·`region`은 문자열 그대로 — 원-핫 인코더가 학습 때 본 범주(`male`/`female`, `yes`/`no`, 네 지역)와 **글자가 같아야** 한다 |
| `self.model.predict(sample)[0]` | 결과는 길이 1인 넘파이 배열이라 `[0]`으로 꺼낸다 |
| `float(...)` | `numpy.float64`를 파이썬 `float`로. FastAPI의 JSON 직렬화가 넘파이 숫자에서 막히는 일을 미리 피한다(앞 노트 1-8) |

이 여섯 줄이 "서빙 때 흔한 두 오류 — 열 누락과 모르는 범주"(AI day15 연습 노트 2-5)를 코드로 막는 자리다. 열 이름을 하나라도 빠뜨리면 `columns are missing`, 범주를 `Yes`로 보내면 `Found unknown categories`가 난다.

### 1-4. 흡연자에게만 한 번 더 — 같은 사람의 "금연 시나리오"

```python
    nonsmoke = None
    if item['smoker'] == 'yes':
        sample['smoker'] = 'no'
        nonsmoke = float(self.model.predict(sample)[0])
```

예측 한 번으로 끝내지 않고, 흡연자라면 **`smoker` 열만 `'no'`로 바꾼 같은 표**를 다시 넣어 두 번째 숫자를 얻는다. 모델이 함수라서 가능한 일이다 — 입력 하나를 바꾸면 출력이 어떻게 달라지는지를 바로 물을 수 있다. 자료 평균으로 보면 흡연자 32,050달러 vs 비흡연자 8,441달러라 차이가 크고, 화면에서 "금연하면 연 N달러 절약 예상"으로 보여 준다. 비흡연자는 `None`으로 두어 프론트가 그 줄을 숨기게 한다. `sample['smoker'] = 'no'`로 DataFrame의 칸 하나를 바꾸는 문법은 day08 그대로다.

### 1-5. 응답 dict — 화면이 그릴 숫자만, 반올림해서

```python
    return {
        'charge'   : round(charge, 0),                                   # 연간 예상 의료비
        'monthly'  : round(charge / 12, 0),                              # 월 평균
        'nonsmoke' : None if nonsmoke is None else round(nonsmoke, 0),
        'r2'       : self.metrics['test_r2'],                            # 테스트 R²
        'cv_r2'    : self.metrics['cv_r2']                               # 교차검증 R²
    }
```

| 키 | 값 | 프론트에서 |
| --- | --- | --- |
| `charge` | 연간 예측값(달러, 소수점 버림) | 큰 글씨 `$16,459` |
| `monthly` | `charge / 12` | "월 평균 $1,372" |
| `nonsmoke` | 흡연자만 숫자, 아니면 `None` → JSON `null` | 금연 비교 줄 표시/숨김 |
| `r2`·`cv_r2` | 지표 파일에서 그대로 | "모델 성능 : 테스트 R² 0.8828 · 교차검증 R² 0.8198" |

서비스가 돌려주는 것은 "모델 출력"이 아니라 **화면이 그릴 데이터**다. 12로 나누기, 반올림, `None` 처리 같은 잔손질을 서버가 해 두면 프론트는 받은 숫자를 자리에 꽂기만 하면 된다. 반대로 R² 같은 지표는 요청마다 같은 값이지만, 별도 API를 하나 더 만드는 대신 예측 응답에 실어 보내 호출을 한 번으로 줄였다.

### 1-6. `Controller.py` — `POST /api/predict` 한 줄짜리 전달자

```python
from fastapi import APIRouter
router = APIRouter(prefix="/api")

from Service import insurance_service

@router.post("/predict")
async def predict(item: dict):
    return insurance_service.predict(item)
```

앞 노트의 `/save`와 똑같은 모양이다. `item: dict`라 본문 JSON이 통째로 딕셔너리로 들어오고(앞 노트 1-5의 "묶음 타입이면 본문"), 컨트롤러는 서비스에 넘기고 결과를 돌려줄 뿐이다. 주소는 `prefix` + 경로 = `/api/predict`. 조회가 아니라 **입력을 보내 계산을 시키는** 요청이라 `GET`이 아닌 `POST`를 쓴다 — 여섯 값을 쿼리스트링에 붙일 수도 있지만, 본문 JSON이 열 이름과 값을 짝지어 보내기에 자연스럽다.

### 1-7. `AppStart.py` — `include_router` 다음에 `StaticFiles` 마운트

```python
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import uvicorn

app = FastAPI()

if __name__ == "__main__":
    uvicorn.run('AppStart:app', host="127.0.0.1", port=8000, reload=True)

import Controller
app.include_router(Controller.router)

app.mount("/", StaticFiles(directory="./ML_pracitce/total_practice/static", html=True))
```

| 조각 | 뜻 |
| --- | --- |
| `StaticFiles(directory=…)` | 폴더 하나를 통째로 "파일 그대로 내주는" 작은 앱으로 만든다. `/app.js`를 부르면 `static/app.js`를, `/style.css`를 부르면 `static/style.css`를 돌려준다 |
| `html=True` | 주소가 폴더(`/`)면 그 안의 `index.html`을 찾아 돌려준다. 이 옵션이 없으면 `http://127.0.0.1:8000/`가 404다 |
| `app.mount("/", …)` | 루트 주소에 붙인다. **`include_router` 뒤에** 써야 한다 — `/`에 마운트한 정적 앱은 자기 아래 모든 주소를 가로채므로, 먼저 붙이면 `/api/predict`도 "그런 파일 없음" 404가 된다 |

FastAPI는 등록 순서대로 주소를 찾는다. `/api/...` 라우트를 먼저 등록해 두면 그쪽이 먼저 걸리고, 거기 없는 주소(`/`, `/app.js`)만 정적 앱으로 떨어진다. 그래서 수업 코드처럼 **API 라우터 → 정적 마운트** 순서가 고정이다. `StaticFiles`는 `fastapi.staticfiles`에서 가져오며, 내부적으로는 Starlette의 것이다.

이렇게 하면 서버 하나가 두 역할을 한다. `http://127.0.0.1:8000/`로 들어오면 화면(HTML)을 주고, 그 화면의 JS가 같은 서버의 `/api/predict`를 부른다. **같은 출처(origin)**라서 CORS 설정도 필요 없다 — React 개발 서버(5173)에서 FastAPI(8000)를 부를 때 겪는 교차 출처 문제가 여기서는 생기지 않는다.

### 1-8. `index.html` — 폼 하나, 결과 카드 하나

```html
<form id="form" class="card">
  <div class="row">
    <label>나이 <input type="number" id="age" min="18" max="64" value="30" required /></label>
    <label>성별 <select id="sex"><option value="male">남성</option><option value="female">여성</option></select></label>
  </div>
  <div class="row">
    <label>키 (cm) <input type="number" id="height" min="120" max="220" value="170" required /></label>
    <label>몸무게 (kg) <input type="number" id="weight" min="30" max="200" value="65" required /></label>
  </div>
  <p class="hint">BMI : <span id="bmi">22.5</span></p>
  ...
  <select id="smoker"><option value="no">비흡연</option><option value="yes">흡연</option></select>
  <select id="region"><option value="northeast">북동부</option> ... </select>
  <button type="submit">예측하기</button>
</form>

<section id="result" class="card result hidden">
  <p class="charge" id="charge">-</p>
  <p class="monthly" id="monthly">-</p>
  <p class="compare hidden" id="compare"></p>
  <p class="metric" id="metric"></p>
</section>

<script src="https://cdn.jsdelivr.net/npm/axios@1.7.9/dist/axios.min.js"></script>
<script src="app.js"></script>
```

| 요소 | 역할 |
| --- | --- |
| `<option value="male">남성</option>` | 화면에는 한국어, **`value`는 학습 자료의 범주 글자 그대로**(`male`·`yes`·`northeast`). 서버로 가는 것은 `value`다 |
| `min`·`max`·`required` | 브라우저가 먼저 거르는 1차 검증. 학습 자료의 범위(나이 18~64)를 그대로 옮겨 모델이 본 적 없는 값을 막는다 |
| 키·몸무게 입력 | 모델의 특성은 `bmi`이지만 사람은 BMI를 모른다. 키·몸무게를 받아 **JS가 BMI로 환산**한다 |
| `class="hidden"` | 결과 카드와 금연 비교 줄은 처음엔 숨겨 두고 응답이 오면 JS가 클래스를 떼어 보인다 (`.hidden { display: none; }`) |
| axios CDN | `fetch` 대신 React 수업에서 쓰던 axios를 `<script>`로 불러 같은 문법을 쓴다 |

### 1-9. `app.js` — BMI 계산, `axios.post`, 결과 꽂기

```javascript
// 1) 키·몸무게로 BMI (몸무게 ÷ 키(m)²)
function calcBmi() {
  const h = Number(document.querySelector("#height").value) / 100;
  const w = Number(document.querySelector("#weight").value);
  if (h <= 0 || w <= 0) return 0;
  return Math.round((w / (h * h)) * 10) / 10;
}
document.querySelector("#height").addEventListener("input", () => {
  document.querySelector("#bmi").textContent = calcBmi();
});

// 2) 12345 → $12,345
function money(v) {
  return "$" + Number(v).toLocaleString("en-US");
}

// 3) 예측하기
document.querySelector("#form").addEventListener("submit", async (e) => {
  e.preventDefault();                                     // 새로고침 막기
  const item = {
    age: Number(document.querySelector("#age").value),
    sex: document.querySelector("#sex").value,
    bmi: calcBmi(),
    children: Number(document.querySelector("#children").value),
    smoker: document.querySelector("#smoker").value,
    region: document.querySelector("#region").value,
  };
  const btn = document.querySelector("button");
  btn.disabled = true; btn.textContent = "예측 중...";
  try {
    const response = await axios.post("/api/predict", item);   // 객체 → JSON 본문
    const data = response.data;
    document.querySelector("#charge").textContent  = money(data.charge);
    document.querySelector("#monthly").textContent = "월 평균 " + money(data.monthly);
    document.querySelector("#metric").textContent  =
      "모델 성능 : 테스트 R² " + data.r2 + " · 교차검증 R² " + data.cv_r2;
    const compare = document.querySelector("#compare");
    if (data.nonsmoke !== null) {
      compare.textContent = "금연하면 " + money(data.nonsmoke) +
        " (연 " + money(data.charge - data.nonsmoke) + " 절약 예상)";
      compare.classList.remove("hidden");
    } else {
      compare.classList.add("hidden");
    }
    document.querySelector("#result").classList.remove("hidden");
  } catch (err) {
    alert("서버와 연결할 수 없습니다. AppStart.py 가 실행 중인지 확인하세요.");
  }
  btn.disabled = false; btn.textContent = "예측하기";
});
```

| 조각 | 뜻 |
| --- | --- |
| `Math.round(x * 10) / 10` | 소수 첫째 자리 반올림 관용구. 170cm·65kg → 22.5 |
| `"input"` 이벤트 | 키·몸무게를 한 글자 바꿀 때마다 BMI 표시를 갱신 — `"change"`는 포커스가 나갈 때만 |
| `item` 객체 | **키 이름이 서버의 `item['age']`·학습 자료의 열 이름과 같다.** 세 곳(학습 CSV·서비스·프론트)이 같은 이름을 쓰는 것이 이 실습의 보이지 않는 약속이다 |
| `axios.post("/api/predict", item)` | 상대 주소 — 같은 서버에서 화면을 받았으니 `http://127.0.0.1:8000`을 쓸 필요가 없다. 객체를 넣으면 axios가 JSON으로 바꾸고 `Content-Type: application/json`을 붙인다 |
| `await` + `try/catch` | 응답을 기다리는 동안 버튼을 잠그고 글자를 바꾼다. 서버가 꺼져 있으면 `catch`로 떨어져 안내 |
| `data.nonsmoke !== null` | 파이썬 `None`이 JSON `null`로 온다. `undefined`가 아니라 `null`이라 `!==`로 정확히 비교 |
| `toLocaleString("en-US")` | 천 단위 쉼표. 달러 표기라 영어 로케일 |

### 1-10. 요청 한 번이 지나가는 길

```text
브라우저  GET /                          → StaticFiles(html=True) → static/index.html
브라우저  GET /style.css, /app.js        → StaticFiles
(사용자가 폼을 채우고 예측하기 클릭)
app.js    POST /api/predict  {age:30, sex:'male', bmi:22.5, children:0, smoker:'yes', region:'northeast'}
   │
   ▼
Controller.predict(item: dict)          ← @router.post("/predict")
   │  insurance_service.predict(item)
   ▼
Service.InsuranceService.predict
   │  DataFrame 한 줄 → model.predict → 16,459
   │  smoker를 'no'로 → 다시 predict → 4,256
   ▼
{'charge': 16459, 'monthly': 1372, 'nonsmoke': 4256, 'r2': 0.8828, 'cv_r2': 0.8198}
   │
   ▼
app.js    결과 카드 표시 — "$16,459 / 월 평균 $1,372 / 금연하면 $4,256 (연 $12,203 절약 예상)"
```

위 숫자는 화면 기본값(30세·남성·170cm·65kg·자녀 0·북동부)에 흡연만 `yes`로 바꿔 이 노트에서 같은 파이프라인으로 확인한 값이다. 화면 → API → 서비스 → 모델 → 다시 화면까지가 한 줄기이고, 어디서 끊겼는지는 브라우저 개발자 도구의 Network 탭(요청이 갔는지, 상태 코드가 무엇인지)과 서버 터미널(파이썬 예외)을 같이 보면 바로 좁혀진다.

### 1-11. 실행 — 작업 폴더가 두 곳을 묶는다

`Service.py`의 `.pkl` 경로와 `AppStart.py`의 `static` 경로가 모두 `./ML_pracitce/total_practice/…`로 시작하므로, 서버는 **`2026_Python` 루트에서** `python ML_pracitce/total_practice/AppStart.py`로 띄우는 것을 전제한다. 한편 `import Controller`는 실행한 스크립트의 폴더(`total_practice`)를 검색 경로에 넣으므로 그대로 찾힌다. 즉 "상대 경로 문자열은 작업 폴더 기준, 모듈 import는 스크립트 폴더 기준"이라는 두 규칙이 한 파일에서 함께 작동한다. 브라우저에서 `http://127.0.0.1:8000/`을 열면 폼이 뜨고, `/docs`에 들어가면 `POST /api/predict` 하나가 보인다.

## 2. 추가로 알면 좋은 활용법

### 2-1. 본문을 pydantic으로 받아 자료형·범주를 서버가 검증

```python
from typing import Literal
from pydantic import BaseModel, Field

class InsuranceIn(BaseModel):
    age: int = Field(ge=18, le=64)
    sex: Literal['male', 'female']
    bmi: float = Field(gt=10, lt=60)
    children: int = Field(ge=0, le=5)
    smoker: Literal['yes', 'no']
    region: Literal['northeast', 'northwest', 'southeast', 'southwest']

@router.post("/predict")
async def predict(item: InsuranceIn):
    return insurance_service.predict(item.model_dump())
```

`dict`로 받으면 `int(item['age'])` 같은 변환을 서비스가 직접 해야 하고, 키가 빠지면 `KeyError`가 500으로 터진다. 모델로 받으면 범위 밖·모르는 범주·빠진 키를 FastAPI가 **422로 먼저 거르고**, `/docs`에 입력 형식이 표로 뜬다. `Literal`은 원-핫 인코더가 아는 범주만 통과시키는 울타리다. `model_dump()`로 딕셔너리로 바꿔 넘기면 서비스 코드는 그대로다.

### 2-2. 경로를 파일 위치 기준으로 — 어디서 실행해도 되게

```python
from pathlib import Path
BASE = Path(__file__).resolve().parent            # total_practice/

self.model = joblib.load(BASE / 'insurance_pipe.pkl')
app.mount("/", StaticFiles(directory=BASE / "static", html=True))
```

`./ML_pracitce/...` 상대 경로는 작업 폴더가 바뀌면 깨진다. `__file__` 기준으로 만들면 VS Code 실행 버튼이든 터미널이든 어디서 띄워도 같은 파일을 가리킨다. 배포(도커 등)에서 작업 폴더를 통제하기 어려울 때 특히 유용하다.

### 2-3. 모델 로딩을 `lifespan`으로 옮기기

```python
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.model = joblib.load(BASE / 'insurance_pipe.pkl')   # 시작 때
    yield
    # 종료 때 정리할 것이 있으면 여기

app = FastAPI(lifespan=lifespan)
```

모듈 import 시점에 `.pkl`을 읽는 수업 방식은 짧지만, 테스트에서 `Controller`를 import만 해도 파일을 읽는다. 큰 모델이거나 GPU에 올려야 하면 서버 시작 훅에서 읽고 `request.app.state.model`로 꺼내 쓰는 편이 통제하기 쉽다(앞 노트 3-2).

### 2-4. 여러 명을 한 번에 — 배치 예측

```python
def predict_many(self, items: list[dict]):
    df = pd.DataFrame(items)                          # 행 n개
    return [float(v) for v in self.model.predict(df)]
```

`pd.DataFrame([{...}])`의 대괄호 안에 딕셔너리를 여러 개 넣으면 그대로 n행이 되고, `predict`는 n개를 한 번에 돌려준다. 사이킷런은 한 줄씩 n번 부르는 것보다 n줄을 한 번 넣는 쪽이 훨씬 빠르다. 라우트는 `item: list[InsuranceIn]`으로 받으면 된다.

### 2-5. 지표를 별도 API로, 화면은 처음에 한 번만

```python
@router.get("/metrics")
async def metrics():
    return insurance_service.metrics
```

수업처럼 예측 응답에 R²를 실어 보내도 되지만, 화면이 열릴 때 `GET /api/metrics`를 한 번 불러 "이 모델은 테스트 R² 0.88"을 미리 보여 주고, 예측 응답은 예측값만 담는 식으로 나눌 수도 있다. 지표 파일이 갱신되면(재학습) 그 자리만 바뀐다.

### 2-6. `fetch`로 쓰면

```javascript
const res = await fetch("/api/predict", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify(item),
});
const data = await res.json();
```

axios 없이 브라우저 내장 `fetch`로도 같은 일을 한다. 헤더와 `JSON.stringify`를 직접 써야 하는 것이 axios가 대신해 주던 부분이다. CDN 한 줄을 줄일 수 있어 작은 페이지라면 이쪽이 가볍다.

## 3. 더 나아가 알면 좋은 것

### 3-1. 정적 파일을 FastAPI가 내주는 것의 한계

`StaticFiles`는 개발·소규모엔 충분하지만, 실제 배포에서는 보통 **nginx가 정적 파일과 `/api` 분기를 맡고** FastAPI는 API만 한다. React로 만든 프론트라면 `npm run build` 결과(`dist/`)를 `StaticFiles`에 마운트해 같은 구조로 띄울 수 있고, 이때 React Router의 클라이언트 라우팅(`/about` 같은 주소)을 살리려면 못 찾는 주소를 전부 `index.html`로 돌리는 처리가 추가로 필요하다.

### 3-2. 모델 서빙 전용 도구

예측 API가 여러 모델·여러 버전으로 늘어나면 손으로 짠 FastAPI 대신 MLflow Models·BentoML·TorchServe 같은 서빙 틀을 쓴다. 입력 스키마·버전 관리·A/B 배포·모니터링(요청량, 지연, 입력 분포 변화)이 붙어 있다. 수업의 `Service.py`는 그 도구들이 자동으로 만들어 주는 것을 가장 작게 손으로 쓴 셈이다.

### 3-3. 동시 요청과 CPU 작업

`async def predict`로 선언했지만 안에서 `await`할 것이 없고 `model.predict`는 CPU를 쓰는 동기 작업이다. 요청이 몰리면 이벤트 루프가 그 시간 동안 막힌다. 간단한 해결은 라우트를 `def`(동기)로 선언해 FastAPI가 스레드풀에서 돌리게 하는 것이고, 더 가면 `uvicorn --workers N`으로 프로세스를 늘린다. 백엔드 수업 day16의 스레드 풀 이야기가 파이썬 서버에서 같은 모양으로 돌아온다.

### 3-4. 공개 저장소에 올릴 때

`.pkl`은 바이너리라 git 차이 비교가 안 되고 커질 수 있다. 작은 실습은 함께 올려도 되지만, 커지면 `.gitignore`에 넣고 재학습 스크립트(`sci.py`)만 올리거나 Git LFS·모델 저장소를 쓴다. 학습 자료 CSV도 출처·라이선스를 확인하고 올린다.

### 3-5. 다음에 볼 키워드

- `pydantic` `Literal`·`Field(ge=, le=)` — 입력 울타리
- `Path(__file__).parent` — 실행 위치에 독립적인 경로
- `lifespan`·`app.state` — 시작 시 로딩
- `fastapi.middleware.cors.CORSMiddleware` — 프론트가 다른 포트일 때
- `uvicorn --workers`·동기 `def` 라우트 — CPU 작업 처리
- nginx 리버스 프록시·`npm run build` + `StaticFiles` — 프론트 배포 두 갈래

## 실습 파일

- `KDT_2026/2026_Python/ML_pracitce/total_practice/AppStart.py` — `app = FastAPI()`, `uvicorn.run('AppStart:app', host="127.0.0.1", port=8000, reload=True)`, `import Controller` → `app.include_router(Controller.router)`, 그 뒤 `app.mount("/", StaticFiles(directory="./ML_pracitce/total_practice/static", html=True))`
- `KDT_2026/2026_Python/ML_pracitce/total_practice/Controller.py` — `router = APIRouter(prefix="/api")`, `from Service import insurance_service`, `@router.post("/predict")`의 `item: dict` → `insurance_service.predict(item)`
- `KDT_2026/2026_Python/ML_pracitce/total_practice/Service.py` — `class InsuranceService`: 생성자에서 `joblib.load`로 `insurance_pipe.pkl`·`insurance_metrics.pkl`, `predict()`가 `pd.DataFrame([{age·sex·bmi·children·smoker·region}])`(`int`·`float` 변환) → `model.predict(sample)[0]` → 흡연자면 `sample['smoker'] = 'no'`로 한 번 더 → `{'charge', 'monthly', 'nonsmoke', 'r2', 'cv_r2'}` 반환, 모듈 끝 `insurance_service = InsuranceService()`
- `KDT_2026/2026_Python/ML_pracitce/total_practice/static/index.html` — 나이·성별·키·몸무게·BMI 표시·자녀 수·흡연·지역 폼(`value`는 영문 범주), 숨긴 결과 카드(`#charge`·`#monthly`·`#compare`·`#metric`), axios 1.7.9 CDN + `app.js`
- `KDT_2026/2026_Python/ML_pracitce/total_practice/static/app.js` — `calcBmi()`(kg ÷ m², 소수 1자리)·`input` 이벤트로 갱신, `money()` 천 단위 쉼표, `submit`에서 `preventDefault` → `item` 객체 → 버튼 잠금 → `await axios.post("/api/predict", item)` → 결과 꽂기·`nonsmoke !== null`이면 금연 비교 표시 → `catch`에서 `alert`
- `KDT_2026/2026_Python/ML_pracitce/total_practice/static/style.css` — 카드·`.row` flex 2열·`.hidden { display: none }`·버튼 `:disabled` 색

## 관련 노트

[[Python 정리본 인덱스]] · [[Python day16 FastAPI APIRouter로 컨트롤러·서비스 파일 분리]] · [[Python day16 FastAPI 시작과 쿼리·경로·본문 파라미터]] · [[Python day05 클래스 정의와 생성자·메소드]] · [[Python day08 판다스 데이터프레임 생성과 인덱싱·필터링]] · [[KDT_2026 학습 지도]]
