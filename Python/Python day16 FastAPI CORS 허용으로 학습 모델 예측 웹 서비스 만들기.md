---
출처: Claude 분석
원본: KDT_2026/2026_Python/ML_pracitce/total_practice/AppStart.py, ML_pracitce/total_practice/Controller.py, ML_pracitce/total_practice/Service.py, ML_pracitce/total_practice/static/index.html, ML_pracitce/total_practice/static/app.js, ML_pracitce/total_practice/static/style.css
작성일: 2026-11-12
tags: [학습, python]
---

# Python day16 — FastAPI CORS 허용으로 학습 모델 예측 웹 서비스 만들기

> 실습 파일: `ML_pracitce/total_practice/AppStart.py`, `Controller.py`, `Service.py`, `static/index.html`, `static/app.js`, `static/style.css`
> 허브: [[Python 정리본 인덱스]] · 이전: [[Python day16 FastAPI APIRouter로 컨트롤러·서비스 파일 분리]] · 다음: (아직 없음)

앞 노트의 세 파일 구조(`AppStart` → `Controller` → `Service`)를 그대로 가져와, 서비스가 들고 있는 것을 **판다스 표 두 줄에서 학습이 끝난 머신러닝 모델**로 바꾼 종합 실습이다. 모델은 같은 폴더의 `sci.py`가 의료보험 자료로 학습해 `insurance_pipe.pkl`·`insurance_metrics.pkl`로 저장해 둔 것이고(그쪽은 AI 폴더의 "AI day16 의료비 데이터 전처리와 ColumnTransformer·다항 릿지 그리드서치 실습"에 정리, 학습 지도 경유), 이 노트는 그 `.pkl`을 **읽어서 웹 화면까지 연결하는 쪽**만 다룬다. 새로 등장하는 것은 셋이다. `joblib.load`를 서비스 생성자에 두는 것, `CORSMiddleware`로 **다른 출처에서 열린 화면이 API를 부를 수 있게 허용**하는 것, 그리고 브라우저 쪽에서 `axios.post`로 `http://127.0.0.1:8000/api/predict`를 부르는 작은 프론트다. 화면(`static/index.html`)은 FastAPI가 내주지 않고 **따로 연다** — 탐색기에서 더블클릭하거나 VS Code Live Server로 띄우면 되고, 그래서 서버와 화면의 주소(출처)가 달라지며 CORS가 필요해진다. 처음 정리할 때는 `StaticFiles`로 화면까지 FastAPI 한 서버에서 내주는 모양이었는데, 수업 코드가 CORS 방식으로 바뀌어 그쪽은 2-3에 대안으로 남겼다. 지금까지 `/docs` 화면으로만 눌러 보던 API를 처음으로 **진짜 화면**이 부른다.

## 1. 배운 내용

### 1-1. 폴더 한 장 — 누가 무엇을 만들고 누가 읽는가

```text
ML_pracitce/total_practice/
├── sci.py                   # 학습 스크립트 → .pkl 두 개 생성 (AI 노트)
├── insurance.csv            # 학습 자료
├── insurance_pipe.pkl       # 전처리+다항+릿지 파이프라인
├── insurance_metrics.pkl    # {'test_r2': 0.8828, 'cv_r2': 0.8198, 'best_params': …}
├── AppStart.py              # 앱 생성, CORS 미들웨어, 라우터 연결, 서버 실행
├── Controller.py            # POST /api/predict
├── Service.py               # .pkl 로드, 입력 dict → DataFrame → 예측 → 응답 dict
└── static/                  # 브라우저가 직접 여는 화면 (서버가 내주지 않음)
    ├── index.html           # 입력 폼 + 결과 카드
    ├── app.js               # BMI 계산, 입력 범위 검사, axios.post, 결과 표시
    └── style.css
```

학습(`sci.py`)과 서비스(`AppStart.py` 이하)는 **같은 파일을 쓰되 서로 import하지 않는다.** 학습은 한 번 돌려 `.pkl`을 남기고 끝나고, 서버는 그 `.pkl`만 읽는다. 학습 코드를 서버가 import하면 서버를 띄울 때마다 75번 학습이 다시 돌게 되므로, 둘 사이의 약속은 "파일 두 개"뿐이다. 마찬가지로 서버와 화면도 서로를 모른다 — 둘 사이의 약속은 **주소 하나(`/api/predict`)와 JSON 키 이름**뿐이다.

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
| 생성자에 두는 이유 | 모듈 끝의 `result_service = InsuranceService()`가 서버 프로세스에서 **한 번만** 실행된다(앞 노트 1-4의 모듈 캐시). 요청마다 디스크에서 4KB를 다시 읽지 않는다 |

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

### 1-4. 응답 dict — 화면이 그릴 숫자만, 반올림해서

```python
    return {
        'charge'   : round(charge, 0),          # 연간 예상 의료비
        'monthly'  : round(charge / 12, 0),     # 월 평균
        'r2'       : self.metrics['test_r2'],   # 테스트 R²
        'cv_r2'    : self.metrics['cv_r2']      # 교차검증 R²
    }

result_service = InsuranceService()
```

| 키 | 값 | 프론트에서 |
| --- | --- | --- |
| `charge` | 연간 예측값(달러, 소수점 버림) | 큰 글씨 `$16,459` |
| `monthly` | `charge / 12` | "월 평균 $1,372" |
| `r2`·`cv_r2` | 지표 파일에서 그대로 | "모델 성능 : 테스트 R² 0.8828 · 교차검증 R² 0.8198" |

서비스가 돌려주는 것은 "모델 출력"이 아니라 **화면이 그릴 데이터**다. 12로 나누기, 반올림 같은 잔손질을 서버가 해 두면 프론트는 받은 숫자를 자리에 꽂기만 하면 된다. 반대로 R² 같은 지표는 요청마다 같은 값이지만, 별도 API를 하나 더 만드는 대신 예측 응답에 실어 보내 호출을 한 번으로 줄였다. 모듈 끝의 `result_service`는 앞 노트의 `item_service`와 같은 자리 — 이름이 바뀌어도 "모듈 한 번 import, 인스턴스 하나"라는 구조는 같다.

### 1-5. `Controller.py` — `POST /api/predict` 한 줄짜리 전달자

```python
from fastapi import APIRouter
router = APIRouter(prefix="/api")

from Service import result_service

@router.post("/predict")
async def predict(item: dict):
    return result_service.predict(item)
```

앞 노트의 `/save`와 똑같은 모양이다. `item: dict`라 본문 JSON이 통째로 딕셔너리로 들어오고(앞 노트 1-5의 "묶음 타입이면 본문"), 컨트롤러는 서비스에 넘기고 결과를 돌려줄 뿐이다. 주소는 `prefix` + 경로 = `/api/predict`. 조회가 아니라 **입력을 보내 계산을 시키는** 요청이라 `GET`이 아닌 `POST`를 쓴다 — 여섯 값을 쿼리스트링에 붙일 수도 있지만, 본문 JSON이 열 이름과 값을 짝지어 보내기에 자연스럽다.

### 1-6. `AppStart.py` — `CORSMiddleware`로 다른 출처의 화면을 허용

```python
from fastapi import FastAPI
import uvicorn

app = FastAPI()

if __name__ == "__main__":
    uvicorn.run('AppStart:app', host="127.0.0.1", port=8000, reload=True)

# CORS 허용
from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

# 컨트롤러에 라우터 연결
import Controller
app.include_router(Controller.router)
```

| 조각 | 뜻 |
| --- | --- |
| 출처(origin) | **프로토콜 + 호스트 + 포트** 세 가지의 묶음. `http://127.0.0.1:8000`과 `http://127.0.0.1:5500`(Live Server)은 포트가 달라 다른 출처이고, 더블클릭으로 연 `file://…/index.html`은 출처가 `null`이다 |
| 왜 막히나 | 브라우저의 **동일 출처 정책**(Same-Origin Policy). 한 출처에서 받은 스크립트가 다른 출처로 보낸 요청의 응답은, 서버가 "허락한다"고 헤더로 말해 주지 않으면 브라우저가 JS에 넘겨 주지 않는다. 서버는 정상 처리했는데 콘솔에만 `blocked by CORS policy`가 뜨는 이유 |
| `CORSMiddleware` | 모든 응답에 `Access-Control-Allow-Origin` 등 허락 헤더를 붙여 주는 미들웨어. `fastapi.middleware.cors`에서 가져오며 내부는 Starlette의 것 |
| `allow_origins=["*"]` | 어느 출처든 허락. 실습이라 전부 열었다. 실제라면 `["http://localhost:5173"]`처럼 프론트 주소만 적는다(2-4) |
| `allow_methods=["*"]` | GET뿐 아니라 POST·PUT·DELETE도 허락. 기본값은 `GET`만이라 POST를 쓰려면 꼭 적어야 한다 |
| `allow_headers=["*"]` | 요청에 어떤 헤더가 붙어도 허락. axios가 JSON을 보내며 붙이는 `Content-Type: application/json`이 여기에 걸린다 |
| `add_middleware` 위치 | 라우터 연결 앞이든 뒤든 상관없다. 미들웨어는 앱 전체를 감싸므로 `mount` 순서 문제(2-3)와 달리 **등록 순서가 주소 찾기에 영향을 주지 않는다** |

JSON 본문을 담은 POST는 브라우저가 본 요청 전에 **예비 요청(preflight, `OPTIONS /api/predict`)**을 먼저 보내 "이 메서드·이 헤더 써도 되냐"를 묻는다. `allow_methods`와 `allow_headers`가 그 질문에 답하는 자리이고, 둘 중 하나라도 빠지면 본 요청은 가 보지도 못한다. 서버 터미널에 `OPTIONS /api/predict 200`이 먼저 찍히고 `POST /api/predict 200`이 뒤따르면 정상이다.

Spring 수업에서 `@CrossOrigin`으로 풀었던 것과 같은 문제가(Vite 개발 서버 5173 ↔ 스프링 8080) 파이썬 서버에서 같은 모양으로 돌아왔다. 해결 방법도 같다 — **API 서버가 허락 헤더를 붙인다.** 프론트 코드로는 못 푼다.

### 1-7. `index.html` — 폼 하나, 결과 카드 하나

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
  <p class="hint">BMI : <span id="bmi">22.5</span> (예측 가능 범위 16~53)</p>
  ...
  <select id="smoker"><option value="no">비흡연</option><option value="yes">흡연</option></select>
  <select id="region"><option value="northeast">북동부</option> ... </select>
  <button type="submit">예측하기</button>
</form>

<section id="result" class="card result hidden">
  <p class="charge" id="charge">-</p>
  <p class="monthly" id="monthly">-</p>
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
| `.hint`의 "(예측 가능 범위 16~53)" | BMI는 직접 입력하는 칸이 아니라 `min`·`max`를 걸 곳이 없다. 대신 범위를 글자로 보여 주고, 실제 차단은 `app.js`의 범위 검사(1-8)가 맡는다 — 나이·자녀는 HTML 속성과 JS 검사가 겹치고, BMI는 JS 검사만 있는 셈이다 |
| `class="hidden"` | 결과 카드는 처음엔 숨겨 두고 응답이 오면 JS가 클래스를 떼어 보인다 (`.hidden { display: none; }`) |
| axios CDN | `fetch` 대신 React 수업에서 쓰던 axios를 `<script>`로 불러 같은 문법을 쓴다 |
| `style.css`·`app.js` 상대 경로 | HTML을 어디서 열든 **같은 폴더**의 두 파일을 찾는다. 서버가 내주는 것이 아니라 브라우저가 파일을 직접 읽는다 |

이 파일은 서버 주소로 들어가서 받는 것이 아니다. `static/index.html`을 더블클릭하면 `file://` 주소로, VS Code의 Live Server로 열면 `http://127.0.0.1:5500/...`로 뜬다. 어느 쪽이든 API 서버(8000)와는 다른 출처다.

### 1-8. `app.js` — BMI 계산, 입력 범위 검사, `axios.post`, 결과 꽂기

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

  // 학습 데이터 범위 밖이면 예측하지 않음 (나이 18~64, BMI 16~53, 자녀 0~5)
  if (item.age < 18 || item.age > 64) { alert("나이는 18~64세 사이로 입력해 주세요."); return; }
  if (item.bmi < 16 || item.bmi > 53) { alert("BMI가 " + item.bmi + "입니다. … (BMI 16~53 범위만 예측 가능)"); return; }
  if (item.children < 0 || item.children > 5) { alert("자녀 수는 0~5명 사이로 입력해 주세요."); return; }

  const btn = document.querySelector("button");
  btn.disabled = true; btn.textContent = "예측 중...";
  try {
    const response = await axios.post("http://127.0.0.1:8000/api/predict", item);   // 객체 → JSON 본문
    const data = response.data;
    document.querySelector("#charge").textContent  = money(data.charge);
    document.querySelector("#monthly").textContent = "월 평균 " + money(data.monthly);
    document.querySelector("#metric").textContent  =
      "모델 성능 : 테스트 R² " + data.r2 + " · 교차검증 R² " + data.cv_r2;
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
| 범위 검사 세 개 | **학습 자료의 범위**(나이 18~64, BMI 15.96~53.13, 자녀 0~5)를 벗어나면 보내지 않는다. `min`·`max`로 나이·자녀는 브라우저가 이미 막지만, BMI는 키·몸무게에서 **계산되는 값**이라 HTML 속성으로는 막을 수 없어 JS가 검사한다. 범위 밖 입력도 모델은 숫자를 내놓지만(외삽) 믿을 수 없는 값이라 아예 거른다 |
| `return` | 검사에 걸리면 `alert`를 띄우고 핸들러를 끝낸다. 버튼 잠금 앞에 두어 잠긴 채로 남는 일이 없다 |
| `axios.post("http://127.0.0.1:8000/api/predict", item)` | **절대 주소**. 화면이 `file://`이나 5500에서 열리므로 `"/api/predict"` 같은 상대 주소는 자기 출처로 가 버린다. 객체를 넣으면 axios가 JSON으로 바꾸고 `Content-Type: application/json`을 붙인다 — 이 헤더가 1-6의 예비 요청을 일으킨다 |
| `await` + `try/catch` | 응답을 기다리는 동안 버튼을 잠그고 글자를 바꾼다. 서버가 꺼져 있으면 `catch`로 떨어져 안내. CORS에 막힌 경우도 axios는 네트워크 오류로 던지므로 같은 `catch`에 걸린다 — 어느 쪽인지는 콘솔 메시지로 가른다 |
| `toLocaleString("en-US")` | 천 단위 쉼표. 달러 표기라 영어 로케일 |

### 1-9. 요청 한 번이 지나가는 길 — 출처가 둘

```text
[화면 출처: file:// 또는 http://127.0.0.1:5500]        [API 출처: http://127.0.0.1:8000]
브라우저  index.html·style.css·app.js 를 파일에서 직접 읽음
(사용자가 폼을 채우고 예측하기 클릭 → JS 범위 검사 통과)
app.js    OPTIONS /api/predict  (예비 요청: POST + application/json 써도 되나?)
   │                                              ← CORSMiddleware: 허락 헤더 200
app.js    POST /api/predict  {age:30, sex:'male', bmi:22.5, children:0, smoker:'yes', region:'northeast'}
   │
   ▼
Controller.predict(item: dict)          ← @router.post("/predict")
   │  result_service.predict(item)
   ▼
Service.InsuranceService.predict
   │  DataFrame 한 줄 → model.predict → 16,459
   ▼
{'charge': 16459, 'monthly': 1372, 'r2': 0.8828, 'cv_r2': 0.8198}
   │  + Access-Control-Allow-Origin: *               ← 이 헤더가 없으면 브라우저가 JS에 안 넘김
   ▼
app.js    결과 카드 표시 — "$16,459 / 월 평균 $1,372 / 모델 성능 : 테스트 R² 0.8828 · 교차검증 R² 0.8198"
```

위 숫자는 화면 기본값(30세·남성·170cm·65kg·자녀 0·북동부)에 흡연만 `yes`로 바꿔 같은 파이프라인으로 확인한 값이다. 화면 → 예비 요청 → API → 서비스 → 모델 → 다시 화면까지가 한 줄기이고, 어디서 끊겼는지는 브라우저 개발자 도구의 Network 탭(`OPTIONS`가 갔는지, 응답 헤더에 `Access-Control-Allow-Origin`이 있는지)과 서버 터미널(파이썬 예외)을 같이 보면 바로 좁혀진다.

### 1-10. 실행 — 프로세스 둘, 작업 폴더 하나

`Service.py`의 `.pkl` 경로가 `./ML_pracitce/total_practice/…`로 시작하므로, 서버는 **`2026_Python` 루트에서** `python ML_pracitce/total_practice/AppStart.py`로 띄우는 것을 전제한다. 한편 `import Controller`는 실행한 스크립트의 폴더(`total_practice`)를 검색 경로에 넣으므로 그대로 찾힌다. 즉 "상대 경로 문자열은 작업 폴더 기준, 모듈 import는 스크립트 폴더 기준"이라는 두 규칙이 한 파일에서 함께 작동한다. 서버가 뜨면 `/docs`에 `POST /api/predict` 하나가 보이고, 화면은 **따로** `static/index.html`을 열어 쓴다. 서버만 켜고 `http://127.0.0.1:8000/`에 들어가면 `{"detail":"Not Found"}`가 뜨는 것이 정상이다 — 이 서버는 화면을 내주지 않는다.

## 2. 추가로 알면 좋은 활용법

### 2-1. 본문을 pydantic으로 받아 자료형·범주·범위를 서버가 검증

```python
from typing import Literal
from pydantic import BaseModel, Field

class InsuranceIn(BaseModel):
    age: int = Field(ge=18, le=64)
    sex: Literal['male', 'female']
    bmi: float = Field(ge=16, le=53)
    children: int = Field(ge=0, le=5)
    smoker: Literal['yes', 'no']
    region: Literal['northeast', 'northwest', 'southeast', 'southwest']

@router.post("/predict")
async def predict(item: InsuranceIn):
    return result_service.predict(item.model_dump())
```

`dict`로 받으면 `int(item['age'])` 같은 변환을 서비스가 직접 해야 하고, 키가 빠지면 `KeyError`가 500으로 터진다. 모델로 받으면 범위 밖·모르는 범주·빠진 키를 FastAPI가 **422로 먼저 거르고**, `/docs`에 입력 형식이 표로 뜬다. `app.js`의 범위 검사 세 개를 서버에도 두는 셈이다 — 프론트 검사는 사용자 편의, 서버 검사는 방어선이라 **둘 다** 두는 것이 보통이다. `Literal`은 원-핫 인코더가 아는 범주만 통과시키는 울타리다. `model_dump()`로 딕셔너리로 바꿔 넘기면 서비스 코드는 그대로다.

### 2-2. 경로를 파일 위치 기준으로 — 어디서 실행해도 되게

```python
from pathlib import Path
BASE = Path(__file__).resolve().parent            # total_practice/

self.model = joblib.load(BASE / 'insurance_pipe.pkl')
```

`./ML_pracitce/...` 상대 경로는 작업 폴더가 바뀌면 깨진다. `__file__` 기준으로 만들면 VS Code 실행 버튼이든 터미널이든 어디서 띄워도 같은 파일을 가리킨다. 배포(도커 등)에서 작업 폴더를 통제하기 어려울 때 특히 유용하다.

### 2-3. 화면까지 한 서버에서 — `StaticFiles` 마운트 (CORS가 필요 없는 길)

```python
from fastapi.staticfiles import StaticFiles

import Controller
app.include_router(Controller.router)

app.mount("/", StaticFiles(directory="./ML_pracitce/total_practice/static", html=True))
```

CORS 대신 **화면을 FastAPI가 직접 내주면** 출처가 하나라 미들웨어가 필요 없다. `StaticFiles`는 폴더 하나를 "파일 그대로 내주는" 작은 앱으로 만들고, `html=True`면 `/`에서 `index.html`을 찾아 준다. 이때 `app.js`의 주소는 `axios.post("/api/predict", item)` 상대 주소로 바꾼다. 주의할 것은 순서 — `/`에 마운트한 정적 앱은 자기 아래 모든 주소를 가로채므로 **`include_router` 뒤에** 써야 `/api/predict`가 먼저 걸린다. 미들웨어는 순서가 상관없지만 마운트는 상관있다. 두 방식의 차이는 이렇다.

| | CORS 방식(수업) | StaticFiles 방식 |
| --- | --- | --- |
| 화면 여는 법 | 파일 더블클릭·Live Server | `http://127.0.0.1:8000/` |
| 출처 | 둘 (화면 ≠ API) | 하나 |
| 필요한 설정 | `CORSMiddleware` | `app.mount` + 순서 |
| JS의 주소 | 절대 주소 | 상대 주소 |
| 어울리는 때 | 프론트가 따로 개발·배포될 때(React 개발 서버 등) | 작은 페이지를 API와 한 묶음으로 띄울 때 |

React로 만든 프론트라면 `npm run build` 결과(`dist/`)를 `StaticFiles`에 마운트해 같은 구조로 띄울 수 있고, 개발 중에는 Vite 서버(5173)에서 도니 CORS 방식으로 간다. 두 길을 다 알아 두면 된다.

### 2-4. `allow_origins`는 목록으로 좁히기

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5500", "http://localhost:5173"],
    allow_methods=["POST"],
    allow_headers=["Content-Type"],
)
```

`"*"`는 "누구든 내 API를 브라우저에서 불러도 된다"는 뜻이라 실습 밖에서는 **프론트 주소만** 적는다. 메서드·헤더도 실제 쓰는 것만 적으면 예비 요청의 답이 그만큼 좁아진다. 쿠키·인증 헤더를 함께 보내는 `allow_credentials=True`를 켜면 브라우저가 `"*"`를 거부하므로 그때는 목록이 필수다(3-1).

### 2-5. 모델 로딩을 `lifespan`으로 옮기기

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

### 2-6. 여러 명을 한 번에 — 배치 예측

```python
def predict_many(self, items: list[dict]):
    df = pd.DataFrame(items)                          # 행 n개
    return [float(v) for v in self.model.predict(df)]
```

`pd.DataFrame([{...}])`의 대괄호 안에 딕셔너리를 여러 개 넣으면 그대로 n행이 되고, `predict`는 n개를 한 번에 돌려준다. 사이킷런은 한 줄씩 n번 부르는 것보다 n줄을 한 번 넣는 쪽이 훨씬 빠르다. 라우트는 `item: list[InsuranceIn]`으로 받으면 된다.

### 2-7. 같은 모델에 입력 하나만 바꿔 — "금연 시나리오"

```python
nonsmoke = None
if item['smoker'] == 'yes':
    sample['smoker'] = 'no'
    nonsmoke = float(self.model.predict(sample)[0])
```

모델이 함수라서, 같은 사람의 `smoker` 열만 `'no'`로 바꾼 표를 다시 넣으면 "금연하면 얼마나 줄어드나"가 바로 나온다(기본값 흡연자 16,459 → 비흡연 4,256). 응답에 `'nonsmoke'`를 더하고 프론트가 `null`이 아닐 때만 비교 줄을 보여 주는 식으로 붙인다. `sample['smoker'] = 'no'`로 DataFrame 칸 하나를 바꾸는 문법은 day08 그대로다.

### 2-8. `fetch`로 쓰면

```javascript
const res = await fetch("http://127.0.0.1:8000/api/predict", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify(item),
});
const data = await res.json();
```

axios 없이 브라우저 내장 `fetch`로도 같은 일을 한다. 헤더와 `JSON.stringify`를 직접 써야 하는 것이 axios가 대신해 주던 부분이다. CORS 조건은 똑같이 적용된다 — 도구가 아니라 브라우저의 규칙이기 때문이다.

## 3. 더 나아가 알면 좋은 것

### 3-1. CORS를 한 겹 더 — 예비 요청·자격 증명·캐시

예비 요청(`OPTIONS`)은 "단순 요청"이 아닐 때만 간다. `GET`이나 폼 형식의 `POST`는 단순 요청이라 바로 가고, `application/json` 본문·사용자 정의 헤더·`PUT`/`DELETE`는 예비 요청을 먼저 보낸다. 응답의 `Access-Control-Max-Age`(FastAPI `max_age=`)로 그 답을 브라우저가 몇 초 기억할지 정해 매번 두 번 왕복하는 비용을 줄인다. 쿠키·`Authorization` 헤더를 함께 보내려면 서버가 `allow_credentials=True`를 켜고 프론트도 `withCredentials`를 켜야 하며, 이때 `Access-Control-Allow-Origin: *`는 허용되지 않아 출처를 정확히 적어야 한다. CORS는 **브라우저만** 지키는 규칙이라 `httpx`·`curl`·Postman에서는 아예 등장하지 않는다 — "포스트맨에선 되는데 브라우저에선 안 된다"의 원인이 대개 이것이다.

### 3-2. 배포에서는 보통 nginx가 앞에 선다

실제 배포에서는 nginx가 정적 파일(`dist/`)과 `/api` 분기를 맡고 FastAPI는 API만 한다. 같은 도메인 아래에서 `/`는 파일로, `/api`는 8000번으로 넘기면 **브라우저가 보기엔 출처가 하나**라 CORS가 다시 필요 없어진다. 개발 중 CORS, 배포 후 리버스 프록시 — 둘은 같은 문제의 두 시기 답이다. React Router의 클라이언트 라우팅(`/about` 같은 주소)을 살리려면 못 찾는 주소를 전부 `index.html`로 돌리는 처리가 추가로 필요하다.

### 3-3. 모델 서빙 전용 도구

예측 API가 여러 모델·여러 버전으로 늘어나면 손으로 짠 FastAPI 대신 MLflow Models·BentoML·TorchServe 같은 서빙 틀을 쓴다. 입력 스키마·버전 관리·A/B 배포·모니터링(요청량, 지연, 입력 분포 변화)이 붙어 있다. 수업의 `Service.py`는 그 도구들이 자동으로 만들어 주는 것을 가장 작게 손으로 쓴 셈이다.

### 3-4. 동시 요청과 CPU 작업

`async def predict`로 선언했지만 안에서 `await`할 것이 없고 `model.predict`는 CPU를 쓰는 동기 작업이다. 요청이 몰리면 이벤트 루프가 그 시간 동안 막힌다. 간단한 해결은 라우트를 `def`(동기)로 선언해 FastAPI가 스레드풀에서 돌리게 하는 것이고, 더 가면 `uvicorn --workers N`으로 프로세스를 늘린다. 백엔드 수업 day16의 스레드 풀 이야기가 파이썬 서버에서 같은 모양으로 돌아온다.

### 3-5. 공개 저장소에 올릴 때

`.pkl`은 바이너리라 git 차이 비교가 안 되고 커질 수 있다. 작은 실습은 함께 올려도 되지만, 커지면 `.gitignore`에 넣고 재학습 스크립트(`sci.py`)만 올리거나 Git LFS·모델 저장소를 쓴다. 학습 자료 CSV도 출처·라이선스를 확인하고 올린다.

### 3-6. 다음에 볼 키워드

- 동일 출처 정책·`Access-Control-Allow-Origin`·예비 요청(`OPTIONS`)·`max_age`·`allow_credentials`
- `pydantic` `Literal`·`Field(ge=, le=)` — 입력 울타리(프론트 검사와 이중)
- `Path(__file__).parent` — 실행 위치에 독립적인 경로
- `fastapi.staticfiles.StaticFiles`·`app.mount` 순서 — 한 서버 방식
- `lifespan`·`app.state` — 시작 시 로딩
- `uvicorn --workers`·동기 `def` 라우트 — CPU 작업 처리
- nginx 리버스 프록시·`npm run build` — 배포에서 출처 합치기

## 실습 파일

- `KDT_2026/2026_Python/ML_pracitce/total_practice/AppStart.py` — `app = FastAPI()`, `uvicorn.run('AppStart:app', host="127.0.0.1", port=8000, reload=True)`, `app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])`, `import Controller` → `app.include_router(Controller.router)`
- `KDT_2026/2026_Python/ML_pracitce/total_practice/Controller.py` — `router = APIRouter(prefix="/api")`, `from Service import result_service`, `@router.post("/predict")`의 `item: dict` → `result_service.predict(item)`
- `KDT_2026/2026_Python/ML_pracitce/total_practice/Service.py` — `class InsuranceService`: 생성자에서 `joblib.load`로 `insurance_pipe.pkl`·`insurance_metrics.pkl`, `predict()`가 `pd.DataFrame([{age·sex·bmi·children·smoker·region}])`(`int`·`float` 변환) → `model.predict(sample)[0]` → `{'charge', 'monthly', 'r2', 'cv_r2'}` 반환, 모듈 끝 `result_service = InsuranceService()`
- `KDT_2026/2026_Python/ML_pracitce/total_practice/static/index.html` — 나이·성별·키·몸무게·BMI 표시·자녀 수·흡연·지역 폼(`value`는 영문 범주), 숨긴 결과 카드(`#charge`·`#monthly`·`#metric`), axios 1.7.9 CDN + `app.js`. 브라우저가 직접 여는 파일
- `KDT_2026/2026_Python/ML_pracitce/total_practice/static/app.js` — `calcBmi()`(kg ÷ m², 소수 1자리)·`input` 이벤트로 갱신, `money()` 천 단위 쉼표, `submit`에서 `preventDefault` → `item` 객체 → 나이 18~64·BMI 16~53·자녀 0~5 범위 검사(`alert` 후 `return`) → 버튼 잠금 → `await axios.post("http://127.0.0.1:8000/api/predict", item)` → 결과 꽂기 → `catch`에서 `alert`
- `KDT_2026/2026_Python/ML_pracitce/total_practice/static/style.css` — 카드·`.row` flex 2열·`.hidden { display: none }`·버튼 `:disabled` 색

## 관련 노트

[[Python 정리본 인덱스]] · [[Python day16 FastAPI APIRouter로 컨트롤러·서비스 파일 분리]] · [[Python day16 FastAPI 시작과 쿼리·경로·본문 파라미터]] · [[Python day05 클래스 정의와 생성자·메소드]] · [[Python day08 판다스 데이터프레임 생성과 인덱싱·필터링]] · [[KDT_2026 학습 지도]]
