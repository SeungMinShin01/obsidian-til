---
출처: Claude 분석
원본: KDT_2026/2026_React/src/example/day04/practice
작성일: 2026-09-18
tags: [학습, react]
---

# React day06 — 내 서버를 거쳐 받는 공공데이터

> 실습 파일: `src/example/day04/practice/신승민2.jsx` · `src/example/day04/practice/App.jsx`
> 허브: [[React MOC]] · 이전: [[React day05 axios로 백엔드에 POST 보내기]] · 다음: (예정)

day05에서 남의 서버(randomuser.me)를 직접 부르고, 그다음에는 내 백엔드로 `axios.post`를 보내 봤다. 이번에는 둘이 한 줄로 이어진다. 화면은 **내 서버만** 부르고, 공공데이터 API를 대신 다녀오는 일은 서버가 맡는다. 프론트 코드만 보면 day05의 `axios.get` 목록 렌더링과 모양이 거의 같은데, 부르는 주소가 `localhost:8080/api4` — 내가 만든 주소라는 점이 달라진다.

핵심은 세 가지다. **① 통신 상대가 한 칸 앞으로 당겨진 삼단 구조**, **② 서버가 공공데이터 응답을 그대로 흘려보내면서 생기는 `data.data` 두 겹 껍데기**, **③ 응답 키가 영문이 아니라 한글이라 프로퍼티 접근 표기가 달라지는 것**이다.

## 1. 배운 내용

### 1-1. 통신 상대가 바뀐 삼단 구조

day05의 외부 API 호출은 브라우저가 남의 서버를 직접 두드리는 2단이었다.

```
[브라우저] ──axios.get──▶ [randomuser.me]
```

이번 실습은 사이에 내 서버가 한 칸 들어간다.

```
[브라우저] ──axios.get("/api4")──▶ [내 스프링 서버] ──WebClient──▶ [공공데이터 API]
```

프론트가 얻는 것은 세 가지다. 인증키가 화면 코드에 드러나지 않고(브라우저로 내려간 JS는 누구나 열어 볼 수 있다), 공공데이터 쪽 CORS 정책과 무관해지며(내 서버끼리의 약속만 맞추면 된다), 응답을 서버에서 한 번 손봐서 내려줄 여지가 생긴다. 대신 서버가 살아 있어야 화면이 동작하므로, 개발 중에는 스프링 쪽을 먼저 띄워 두고 Vite를 켜는 순서가 된다.

### 1-2. 조회 컴포넌트의 뼈대는 그대로

```jsx
import { useState, useEffect } from "react";
import axios from "axios";

function DataList(props) {
  const [myJSON, setMyJSON] = useState([]);
  useEffect(() => {
    async function Data() {
      const response = await axios.get("http://localhost:8080/api4");
      const data = response.data;
      setMyJSON(data.data);
    }
    Data();
  }, []);
  // ...
}
```

지금까지 굳혀 온 형태가 그대로 다시 나온다.

| 자리 | 하는 일 |
| --- | --- |
| `useState([])` | 응답이 오기 전 첫 렌더링을 버티는 초기값 |
| `useEffect(…, [])` | 마운트 직후 한 번만 요청 |
| 안쪽 `async function` | effect 콜백 자체를 `async`로 만들지 않기 위한 표준형 |
| `setMyJSON(...)` | 상태 갱신 → 재렌더링 → 목록이 그려짐 |

`useEffect`의 콜백은 정리 함수를 반환하거나 아무것도 반환하지 않아야 하는데, `async` 함수는 항상 Promise를 반환한다. 그래서 안쪽에 함수를 하나 선언하고 바로 호출하는 표기를 쓴다. → [[React day05 컴포넌트 생명주기와 useEffect]]

### 1-3. `response.data.data` — 두 겹 껍데기 풀기

응답을 꺼내는 줄이 두 번 `.data`를 탄다. 이름이 같아서 헷갈리기 쉬운데, 두 `data`의 출신이 다르다.

| 표기 | 누가 만든 것 |
| --- | --- |
| `response.data` | **axios**가 씌운 껍데기. 상태 코드·헤더와 함께 본문을 담아 주는 자리 |
| `data.data` | **공공데이터 포털**이 정한 응답 형식. 목록이 `data` 키 아래 배열로 들어 있다 |

서버가 받아 온 JSON을 손대지 않고 그대로 내려보내면, 포털이 정한 모양이 화면까지 그대로 온다. 그래서 실제 배열을 쥐려면 껍데기를 두 번 벗겨야 한다. 응답 모양을 모를 때는 `console.log(response.data)`로 한 번 찍어 보고 어느 깊이에 배열이 있는지 확인한 뒤 코드를 쓰는 편이 빠르다. 서버 쪽에서 미리 배열만 꺼내 내려주면 프론트는 `response.data`만으로 끝나는데, 그 선택은 응답 DTO를 어디까지 다듬느냐의 문제다.

### 1-4. 한글 키를 가진 응답 다루기

공공데이터 포털의 JSON은 키가 한글인 경우가 많다.

```jsx
let trTag = myJSON.map((data) => {
  return (
    <tr key={data.관리기관명}>
      <td>{data.관리기관명}</td>
      <td>{data.관할경찰서명}</td>
      <td>{data.CCTV설치대수}</td>
    </tr>
  );
});
```

자바스크립트의 식별자 규칙은 유니코드 문자를 허용하기 때문에 `data.관리기관명` 처럼 점 표기를 그대로 쓸 수 있다. 다만 키에 공백이나 괄호·`%` 같은 기호가 섞이면 점 표기가 막히므로 그때는 대괄호 표기를 쓴다.

```jsx
data["소재지도로명주소"]
data["CCTV 설치 대수"]   // 공백이 있으면 점 표기 불가
```

공공데이터는 컬럼명에 단위나 괄호가 붙는 일이 흔하니, 키를 직접 타이핑하기 전에 응답을 한 번 찍어 **정확한 문자열**을 확인하는 습관이 안전하다. 키가 하나라도 어긋나면 에러 없이 빈 칸만 나와서 원인을 찾기 어렵다.

### 1-5. `map` 결과를 변수에 담아 `<tbody>`에 꽂기

```jsx
let trTag = myJSON.map((data) => { /* <tr> 반환 */ });

return (
  <table border="1">
    <thead>{/* 제목 행 */}</thead>
    <tbody>{trTag}</tbody>
  </table>
);
```

JSX 안에 `map`을 직접 쓰는 것과 결과를 변수에 담아 꽂는 것은 결과가 같다. 반환문이 길어질수록 변수로 빼 두는 쪽이 표 구조를 눈으로 따라가기 쉽다.

`key`는 형제 항목을 구분하는 표시라 **목록 안에서 겹치지 않는 값**이어야 한다. 기관명처럼 중복될 수 있는 값보다는 응답에 들어 있는 고유 번호나 코드가 있으면 그쪽이 낫고, 마땅한 값이 없으면 여러 필드를 이어 붙여 만들기도 한다. → [[React day05 외부 API 호출과 목록 렌더링]]

### 1-6. 라우트에 꽂는 컴포넌트 갈아 끼우기

팀 실습의 라우트 표에서 내 페이지 자리가 새 파일로 바뀐다.

```jsx
import Seung from "./신승민2";
// ...
<Route path="/" element={<Home />}>
  <Route path="seung" element={<Seung />} />
  <Route path="hwan" element={<김지환 />} />
</Route>
```

`import` 이름은 파일명과 달라도 되고(`default export`는 가져오는 쪽이 이름을 정한다), 확장자 `.jsx`는 생략할 수 있다. 라우트 표는 그대로 두고 `element`에 꽂히는 컴포넌트만 바꾸면 같은 주소에서 다른 화면이 나온다 — 화면 교체가 주소가 아니라 **표의 한 칸**을 고치는 일로 끝나는 것이 라우터를 쓰는 이유 중 하나다. → [[React day04 React Router 도입과 라우트 정의]]

## 2. 추가로 알면 좋은 활용법

### 2-1. 서버 주소를 코드 밖으로 빼기

`http://localhost:8080` 을 파일마다 적어 두면 배포 주소로 바꿀 때 전부 찾아 고쳐야 한다. Vite는 `.env` 파일의 `VITE_` 접두사 변수를 읽어 준다.

```
# .env.development
VITE_API_BASE=http://localhost:8080
```

```jsx
const BASE = import.meta.env.VITE_API_BASE;
await axios.get(`${BASE}/api4`);
```

한 발 더 가면 `axios.create({ baseURL: BASE })`로 인스턴스를 만들어 두고 `api.get("/api4")`처럼 짧게 쓴다. 공통 헤더·타임아웃·에러 처리를 한곳에 모을 수 있다.

### 2-2. 개발 중에는 프록시로 CORS를 우회하기

Vite 설정에 프록시를 두면 브라우저 입장에서는 같은 출처로 보이므로 CORS 자체가 발생하지 않는다.

```js
// vite.config.js
export default defineConfig({
  server: {
    proxy: { "/api": { target: "http://localhost:8080", changeOrigin: true } },
  },
});
```

이때 프론트는 `axios.get("/api4")` 처럼 상대 경로로만 부른다. 다만 이건 개발 서버의 편의 기능이라 빌드 결과물에는 적용되지 않는다. 운영에서는 서버 쪽 CORS 설정이나 같은 도메인 배포로 푼다.

### 2-3. 로딩·오류 상태 한 벌

바깥 API를 한 번 더 거치는 구조라 응답이 늦거나 실패할 여지가 늘어난다. 상태 세 개를 같이 두면 화면이 조용히 비어 있는 상황을 피할 수 있다.

```jsx
const [loading, setLoading] = useState(true);
const [error, setError] = useState(null);

try {
  const res = await axios.get(url);
  setMyJSON(res.data?.data ?? []);
} catch (e) {
  setError(e);
} finally {
  setLoading(false);
}
```

`res.data?.data ?? []` 처럼 옵셔널 체이닝과 널 병합을 걸어 두면, 응답 모양이 예상과 달라도 `map` 자리에서 터지지 않는다. 상태 초기값을 배열로 둔 것과 같은 목적의 방어다.

### 2-4. 표를 그리는 코드를 응답에 맞춰 줄이기

키 목록을 배열로 한 번만 적어 두면 제목 행과 본문 행이 같은 배열을 돌게 되어 손댈 자리가 줄어든다.

```jsx
const COLS = ["관리기관명", "관할경찰서명", "CCTV설치대수"];

<thead><tr>{COLS.map((c) => <th key={c}>{c}</th>)}</tr></thead>
<tbody>
  {myJSON.map((row, i) => (
    <tr key={i}>{COLS.map((c) => <td key={c}>{row[c]}</td>)}</tr>
  ))}
</tbody>
```

여기서는 키를 변수로 다루므로 점 표기 대신 대괄호 표기 `row[c]` 가 된다.

### 2-5. 페이지 수를 주소에 태워 보내기

공공데이터 API는 `page`·`perPage`를 받는 경우가 많은데, 그 값을 서버가 고정해 두는 대신 프론트가 넘기도록 열어 두면 페이징을 화면에서 다룰 수 있다.

```jsx
await axios.get(`${BASE}/api4`, { params: { page, perPage: 10 } });
```

`params` 객체를 주면 axios가 알아서 쿼리 스트링으로 만들고 인코딩까지 해 준다. 문자열을 직접 이어 붙이는 것보다 실수가 적다. `page`를 상태로 두고 `useEffect`의 의존성 배열에 `[page]`를 넣으면 버튼 클릭 → 재요청 흐름이 된다.

## 3. 더 나아가 알면 좋은 것

### 3-1. 프록시 서버라는 이름

내 서버가 바깥 API를 대신 불러 주는 이 구조를 보통 **백엔드 프록시**라고 부른다. 인증키 숨기기·CORS 회피·응답 가공 말고도, 호출 횟수 제한이 있는 API에서 **캐시를 서버에 두어** 같은 요청을 줄이는 목적이 크다. 공공데이터는 일일 호출 한도가 있는 경우가 많아, 자주 바뀌지 않는 데이터라면 서버가 한 번 받아 두고 일정 시간 재사용하는 편이 실질적이다.

### 3-2. 응답 모양을 서버에서 정리해 내려주기

`data.data` 두 겹을 프론트가 벗기는 대신, 서버가 목록만 꺼내 `List`로 내려주면 화면 코드가 짧아진다. 더 나아가 필요한 필드만 골라 영문 키로 바꾼 응답 DTO를 두면, 바깥 API의 키가 바뀌어도 화면을 고치지 않아도 된다. **바깥 형식과 내 화면 사이에 완충 층을 두는 것**이 DTO를 나누는 이유와 정확히 같은 이야기다.

### 3-3. 화면에 올리기 전에 정제하기

공공데이터는 값이 비어 있거나 `"Y"`/`"N"` 같은 코드 문자열이 섞여 오는 일이 흔하다. 화면에서 삼항 연산자를 여러 번 쓰기보다, 데이터를 받자마자 한 번 변환해 상태에 담는 쪽이 읽기 쉽다.

```jsx
const rows = (res.data?.data ?? []).map((r) => ({
  ...r,
  cctv: r.CCTV설치여부 === "Y" ? "설치" : "미설치",
}));
```

### 3-4. 다음에 볼 키워드

- `axios.create` 인스턴스 · 인터셉터 · `baseURL`
- `import.meta.env` 와 `.env.development` / `.env.production`
- Vite `server.proxy` · `changeOrigin` · `rewrite`
- `AbortController` 와 요청 취소 · 경쟁 상태(race condition)
- React Query(`useQuery`) — 캐시·재요청·로딩 상태를 맡기는 방향
- 커스텀 훅 `useFetch` 로 통신 코드 묶어 내기
- 서버 쪽 캐시(`@Cacheable`)와 호출 한도
- 페이징 UI — `page` 상태 · 의존성 배열 · 총 건수 받기
- 테이블 가상화(`react-window`) — 수천 행을 그릴 때

## 실습 파일

- `KDT_2026/2026_React/src/example/day04/practice/신승민2.jsx` — 내 스프링 서버의 `/api4`를 `axios.get`으로 불러 성동구 어린이보호구역 목록을 표로 렌더링. `useState([])` 초기값, `useEffect(…, [])` 안쪽 `async` 함수, `response.data.data` 두 겹 껍데기 풀기, 한글 키 점 표기(`data.관리기관명`), `map` 결과를 `trTag` 변수에 담아 `<tbody>`에 꽂기, 데이터 담당 부품(`DataList`)과 페이지 컴포넌트(`Seung`) 분리
- `KDT_2026/2026_React/src/example/day04/practice/App.jsx` — 팀 실습 라우트 표에서 `seung` 자리에 꽂히는 컴포넌트를 새 파일로 교체(`import Seung from "./신승민2"`), `Home` 아래 팀원별 자식 라우트 네 줄 유지

## 관련 노트

[[React MOC]] · [[React day05 axios로 백엔드에 POST 보내기]] · [[React day05 외부 API 호출과 목록 렌더링]] · [[React day05 컴포넌트 생명주기와 useEffect]] · [[React day04 React Router 도입과 라우트 정의]] · [[KDT_2026 학습 지도]]
