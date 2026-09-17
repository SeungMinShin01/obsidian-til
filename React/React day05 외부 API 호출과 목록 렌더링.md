---
출처: Claude 분석
원본: KDT_2026/2026_React/src/example/day05/ExternalApiFetcher.jsx, src/main.jsx
작성일: 2026-09-17
tags: [학습, react]
---

# React day05 — 외부 API 호출과 목록 렌더링

> 실습 파일: `src/example/day05/ExternalApiFetcher.jsx` · `src/main.jsx`
> 허브: [[React MOC]] · 이전: [[React day05 컴포넌트 생명주기와 useEffect]] · 다음: [[React day05 axios로 백엔드에 POST 보내기]]

day05의 `TopNav`에 걸어 둔 세 갈래 중 **외부통신** 차례다. day02에서 `fetch`로 부른 서버는 같은 수업에서 만든 스프링 백엔드였는데, 이번에는 우리와 아무 상관 없는 **공개 API(randomuser.me)** 를 부른다. 도메인이 다른 남의 서버에서 JSON을 받아 와 표로 그리고, 표의 항목을 누르면 그 항목의 원본 데이터를 부모 쪽으로 올려보내는 것까지가 이 날의 범위다. 지금까지 따로 배운 조각들(`useState` · `useEffect(…, [])` · `map`+`key` · 콜백 props · `preventDefault`)이 한 컴포넌트 안에서 전부 맞물리는 예제라, 새 문법보다 **조각들이 붙는 순서**를 보는 것이 목적이다.

## 1. 배운 내용

### 1-1. 통신 컴포넌트의 기본 뼈대

외부 API를 부르는 컴포넌트는 언제나 같은 세 줄로 시작한다.

```jsx
import { useState, useEffect } from "react";

function RandomUser(props) {
  const [myJSON, setMyJSON] = useState({ results: [] });

  useEffect(() => {
    // 여기서 서버를 부르고, 받은 JSON을 setMyJSON 한다
  }, []);

  // myJSON을 map으로 돌려 화면을 그린다
}
```

| 조각 | 역할 | 주의할 점 |
| --- | --- | --- |
| `useState` | 응답 JSON을 담을 자리 | **초기값의 모양을 응답과 똑같이** 맞춘다 |
| `useEffect(…, [])` | 첫 렌더링 뒤 한 번만 요청 | 본문에서 부르면 요청 → 상태 변경 → 재렌더링 → 요청… 무한 반복 |
| `map` | 받아 둔 배열을 태그 목록으로 | `key` 필수 |

요청 도구는 최종적으로 **axios**로 정리했다. `npm install axios` 뒤 `import axios from "axios"` 한 줄을 더하고, 요청 부분이 이렇게 바뀐다.

```jsx
import { useState, useEffect } from "react";
import axios from "axios";

const response = await axios.get("https://api.randomuser.me?results=10");
const data = response.data;   // .json() 단계가 없다
setMyJSON(data);
```

`fetch`와 견주면 달라지는 곳은 두 줄뿐이다 — `res.json()`을 거치지 않고 `response.data`가 바로 파싱된 객체이고, HTTP 오류는 `res.ok` 확인 없이 `catch`로 간다. 나머지 구조(초기값·`useEffect(…, [])`·`map`)는 그대로다. 두 방식의 차이는 2-1에 표로 정리해 뒀고, 한 요청 안에서 섞지 않는 것이 요점이다. 쿼리 스트링(`?results=10`)으로 받아 올 인원 수를 정하는 것도 주소 문자열에 그대로 붙이면 된다(2-4).

여기서 제일 중요한 한 줄은 초기값 `{ results: [] }`이다. randomuser.me의 응답은 `{ "results": [ {...} ], "info": {...} }` 모양이라, 초기값도 같은 껍데기를 갖춰 둬야 한다. 초기값을 빈 객체 `{}`나 `null`로 두면 **응답이 도착하기 전 첫 렌더링에서** `myJSON.results.map(...)`이 `undefined`를 만나 그 자리에서 화면이 죽는다.

이유는 1-2에서 보듯 순서가 정해져 있기 때문이다. 요청은 화면이 그려진 **뒤에** 나가므로, 컴포넌트는 반드시 "아직 데이터가 없는 상태"로 한 번 그려진다. 그 첫 한 번을 버티게 해 주는 것이 초기값이다. **응답 형태가 객체면 객체로, 배열이면 `[]`로** — 이것이 통신 컴포넌트에서 초기값을 정하는 유일한 기준이다.

### 1-2. 실행 순서 — 화면이 먼저, 데이터는 나중

생명주기 노트에서 로그로 확인한 순서가 그대로 적용된다.

```
① 컴포넌트 함수 실행  → myJSON = { results: [] }  → 빈 표가 그려진다
② 화면이 그려진 뒤 useEffect 실행 → 요청이 나간다
③ 응답 도착 → setMyJSON(json) → 상태 변경
④ 컴포넌트 함수 재실행 → myJSON.results에 20명이 들어 있다 → 표가 채워진다
```

컴포넌트 함수는 최소 **두 번** 실행된다. 화면이 잠깐 비어 보이는 것은 실수가 아니라 이 구조의 필연이고, 그래서 로딩 표시(2-3)가 필요해진다. 그리고 `useEffect`의 의존성 배열이 `[]`이므로 요청은 마운트 때 한 번만 나간다. 배열을 빼면 응답이 올 때마다 상태가 바뀌고, 상태가 바뀌면 effect가 다시 돌아 또 요청이 나가는 고리가 만들어진다.

### 1-3. 응답 JSON의 구조를 먼저 읽는다

받은 JSON을 `console.log`로 찍어 **구조를 눈으로 확인한 뒤** 화면 코드를 쓰는 순서가 몸에 배어야 한다. randomuser.me의 사용자 한 명은 이런 모양이다.

```json
{
  "login":   { "md5": "e3a1…", "username": "bluecat", "password": "…" },
  "name":    { "title": "Mr", "first": "James", "last": "Wilson" },
  "picture": { "thumbnail": "https://…/48.jpg" },
  "nat": "GB",
  "email": "james.wilson@example.com",
  "cell": "081-…",
  "gender": "male"
}
```

day02에서 부른 스프링 서버는 `{ cno, cname }`처럼 **한 겹짜리 평평한 객체**였는데, 외부 API는 이렇게 **여러 겹으로 중첩된 객체**를 주는 경우가 흔하다. 그래서 값을 꺼낼 때 `data.name.first`, `data.picture.thumbnail`, `data.login.username`처럼 점을 여러 번 찍는다. DB 컬럼명 = JSON 키가 성립하던 자체 서버와 달리, **외부 API는 키 이름도 구조도 남이 정한 것**이라 문서나 실제 응답을 보고 맞추는 수밖에 없다.

### 1-4. `map`으로 `<tr>` 목록 만들기 — 반환값을 변수에 담는 방식

```jsx
let trTag = myJSON.results.map((data) => {
  return (
    <tr key={data.login.md5}>
      <td><img src={data.picture.thumbnail} alt={data.login.username} /></td>
      <td>{/* 링크 — 1-5 */}</td>
      <td>{data.name.title} {data.name.first} {data.name.last}</td>
      <td>{data.nat}</td>
      <td>{data.email}</td>
    </tr>
  );
});

return (
  <table border="1">
    <thead>
      <tr><th>사진</th><th>로그인</th><th>이름</th><th>국가</th><th>Email</th></tr>
    </thead>
    <tbody>{trTag}</tbody>
  </table>
);
```

JSX 안에 `{myJSON.results.map(...)}`을 직접 넣어도 결과는 같지만, 이렇게 **`map` 결과를 변수에 담아 두고 JSX에서는 `{trTag}`만 꽂는** 방식은 표가 복잡해질수록 읽기 쉽다. `return` 안에 로직이 섞이지 않고, 표의 뼈대(`thead`의 제목 순서)와 데이터 줄(`tbody`)을 따로 볼 수 있다.

`key`로는 `data.login.md5`를 썼다. **목록의 `key`는 그 항목을 다른 항목과 구별해 주는 고유값**이어야 하고, 외부 API 응답에는 보통 이런 id·해시·고유 문자열이 하나쯤 들어 있다. 배열 인덱스를 쓰면 목록의 순서가 바뀌거나 중간이 지워질 때 React가 항목을 잘못 짝지어 엉뚱한 줄이 남는다.

셀 안에서 `{data.name.title} {data.name.first} {data.name.last}`처럼 중괄호를 나눠 쓰면 그 사이의 공백이 그대로 글자로 들어간다. JSX에서 값과 값 사이를 띄우는 가장 간단한 방법이다.

### 1-5. 목록 항목을 눌러 원본 데이터 올려보내기

표의 `username` 칸은 링크이고, 클릭하면 그 줄의 데이터 전체가 부모로 올라간다.

```jsx
<a
  href="/"
  onClick={(e) => {
    e.preventDefault();
    props.onProfile(data);
  }}
>
  {data.login.username}
</a>
```

세 가지가 겹쳐 있다.

1. **`e.preventDefault()`** — `<a href="/">`는 본래 브라우저가 그 주소로 이동하며 페이지를 통째로 새로 받는다. SPA에서는 화면이 깜빡이고 지금까지 쌓은 상태가 전부 날아가므로, 기본 동작을 막고 자바스크립트로만 처리한다
2. **콜백 props** — 자식은 `props.onProfile`이 무슨 일을 하는지 모른 채 부르기만 한다. 데이터는 부모에서 자식으로 내려가고, 사건은 자식에서 부모로 올라간다
3. **인라인 화살표 함수** — `map` 안이라 각 줄마다 넘겨야 할 `data`가 다르다. `onClick={props.onProfile(data)}`로 쓰면 렌더링 시점에 즉시 실행되어 버리므로, **화살표 함수로 한 겹 감싸** 클릭 시점에 실행되게 한다

여기서 올려보내는 것은 화면에 보이던 `username` 문자열이 아니라 **그 줄의 원본 객체 `data` 전체**다. 목록에는 5개 열만 보여 주지만 응답에는 전화번호·성별·주소 등이 더 들어 있고, 그 전부를 부모가 받아 상세 화면이나 모달에 쓸 수 있다. 목록·상세를 나누는 화면 구조가 여기서 시작된다.

### 1-6. 부모 `ExternalApiFetcher` — 받은 데이터를 쓰는 자리

```jsx
function ExternalApiFetcher() {
  return (
    <>
      <h2>외부 서버 통신</h2>
      <RandomUser
        onProfile={(sData) => {
          console.log(sData);
          let info = `전화번호:${sData.cell} 성별:${sData.gender} username:${sData.login.username}`;
          alert(info);
        }}
      ></RandomUser>
    </>
  );
}

export default ExternalApiFetcher;
```

역할이 깔끔하게 둘로 갈렸다.

| 컴포넌트 | 하는 일 |
| --- | --- |
| `RandomUser` | 서버를 부르고 목록을 그린다 (데이터 담당) |
| `ExternalApiFetcher` | 항목이 선택됐을 때 무엇을 할지 정한다 (동작 담당) |

콜백을 `onProfile={...}` 형태로 **props 자리에 인라인으로 적어 내려보내는** 표기도 눈여겨볼 만하다. 자식에게 넘길 동작이 짧으면 따로 함수를 만들지 않고 이렇게 쓰는 편이 흐름을 따라가기 쉽다. `on...`으로 시작하는 이름은 "이 일이 일어나면 불러라"는 뜻의 관례다.

`alert`로 띄우는 문자열은 백틱 템플릿 리터럴로 조립했다. 여러 값을 한 문자열에 끼워 넣을 때 `+`로 잇는 것보다 읽기 쉽다.

한 가지 챙겨 둘 습관이 있다. **응답에 들어 있다고 해서 전부 화면에 내보내지는 않는다.** 이 API는 연습용 가짜 계정이라 비밀번호 같은 필드까지 주지만, 실제 서비스라면 그런 값은 로그로도 화면으로도 꺼내지 않는 것이 기본이다. `console.log(응답)`은 구조를 확인할 때만 쓰고, 확인이 끝나면 지우는 편이 안전하다.

### 1-7. `main.jsx` — 진입 컴포넌트 교체

```jsx
import { BrowserRouter } from "react-router-dom";
import ExternalApiFetcher from "./example/day05/ExternalApiFetcher";

create.render(
  <BrowserRouter>
    <ExternalApiFetcher></ExternalApiFetcher>
  </BrowserRouter>,
);
```

지금까지 해 온 대로 **진입 컴포넌트만 갈아끼워** 이번에 볼 화면을 띄운다. `main.jsx`에는 day01부터의 `import`와 `render`가 주석으로 차곡차곡 쌓여 있어서, 주석 한 줄을 옮기면 어느 날의 실습이든 바로 다시 볼 수 있다.

`BrowserRouter`로 감싼 형태를 유지한 것은 `TopNav`의 `NavLink`가 라우터 컨텍스트 안에서만 동작하기 때문이다. 이 컴포넌트 자체는 라우팅을 쓰지 않지만, 곧 `App4`의 `Routes`에 `/external` 경로로 꽂을 예정이라 껍데기를 그대로 두는 편이 낫다.

## 2. 추가로 알면 좋은 활용법

### 2-1. `fetch`와 `axios` — 두 갈래를 섞지 않기

서버를 부르는 방법은 크게 둘이고, **응답을 다루는 방식이 서로 다르다.**

```jsx
// ① fetch — 브라우저 내장, JSON 변환을 한 번 더 거친다
const res = await fetch(url);
if (!res.ok) throw new Error("요청 실패");
const json = await res.json();   // ← 이 단계가 필요하다

// ② axios — 별도 설치(npm i axios), 변환이 끝난 채로 온다
const res = await axios.get(url);
const json = res.data;           // ← .json() 없이 바로 data
```

| | `fetch` | `axios` |
| --- | --- | --- |
| 설치 | 불필요(내장) | `npm install axios` + `import axios from "axios"` |
| JSON 변환 | `res.json()` 직접 호출 | 자동(`res.data`) |
| HTTP 오류(404·500) | `catch`로 안 감 → `res.ok` 확인 필요 | 자동으로 `catch`로 감 |
| POST 본문 | `JSON.stringify` + 헤더 직접 | 객체 그대로 넘기면 됨 |

둘 다 Promise를 돌려주므로 `.then()` 체인으로도, `async/await`로도 쓸 수 있다. 중요한 건 **한 요청 안에서 두 방식을 섞지 않는 것**이다. `axios`로 받은 응답에 `.json()`은 없고, `fetch`로 받은 응답에 `.data`는 없다. 에러 메시지가 "…is not a function"으로 나오면 대개 이 지점이다.

### 2-2. `useEffect`와 `async` — 콜백 자체를 `async`로 만들지 않는다

`useEffect`의 콜백은 **정리 함수를 반환해야 하는 자리**인데, `async` 함수는 항상 Promise를 반환하므로 그 약속이 깨진다. 그래서 안쪽에 `async` 함수를 따로 만들어 부르는 형태가 표준이다.

```jsx
useEffect(() => {
  const getUsers = async () => {
    try {
      const res = await fetch("https://api.randomuser.me/?results=20");
      if (!res.ok) throw new Error(`요청 실패: ${res.status}`);
      const json = await res.json();
      setMyJSON(json);
    } catch (err) {
      console.error(err);
    }
  };
  getUsers();          // 선언하고 바로 호출
}, []);
```

`.then()` 체인으로 쓸 때는 `await` 없이 끝까지 체인으로만 잇는다.

```jsx
useEffect(() => {
  fetch("https://api.randomuser.me/?results=20")
    .then((res) => res.json())
    .then((json) => setMyJSON(json))
    .catch((err) => console.error(err));
}, []);
```

`await`와 `.then()`은 **같은 일을 하는 두 표기**라 한 줄 안에서 겹쳐 쓸 필요가 없다. `await`를 붙였으면 결과는 이미 풀린 값이고, `.then()`으로 이었으면 그 체인 끝에서 값을 받는다. 둘 중 하나만 고르는 것이 읽기에도 안전하다.

### 2-3. 로딩·오류 상태 — 상태 세 개가 한 벌

1-2에서 본 대로 화면은 데이터 없이 한 번 그려진다. 실무에서는 그 순간을 비워 두지 않고 상태 하나를 더 둔다.

```jsx
const [myJSON, setMyJSON] = useState({ results: [] });
const [loading, setLoading] = useState(true);
const [error, setError] = useState(null);

useEffect(() => {
  const run = async () => {
    try {
      setLoading(true);
      const res = await fetch(url);
      if (!res.ok) throw new Error(`요청 실패: ${res.status}`);
      setMyJSON(await res.json());
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);      // 성공하든 실패하든 반드시 끈다
    }
  };
  run();
}, []);

if (loading) return <p>불러오는 중…</p>;
if (error) return <p>오류: {error}</p>;
```

**데이터·로딩·오류 세 상태가 한 벌**이라는 감각을 들여 두면 어떤 통신 컴포넌트든 같은 뼈대로 쓸 수 있다. `finally`에 `setLoading(false)`를 두는 것이 핵심이고, 이 세 벌을 매번 쓰기가 번거로워지는 시점이 커스텀 훅(3-3)을 만들 때다.

### 2-4. 쿼리 스트링으로 요청 조절하기

외부 API는 대개 주소 뒤 쿼리 스트링으로 옵션을 받는다. randomuser.me도 `?results=20&nat=kr&gender=female` 같은 식이다.

```jsx
const [count, setCount] = useState(5);

useEffect(() => {
  fetch(`https://api.randomuser.me/?results=${count}`)
    .then((res) => res.json())
    .then(setMyJSON);
}, [count]);          // count가 바뀔 때마다 다시 부른다
```

여기서 의존성 배열이 `[]`이 아니라 `[count]`가 되는 것이 생명주기 노트에서 본 두 번째 형태다. **"이 값이 바뀌면 서버를 다시 불러야 한다"** 가 곧 의존성 배열에 넣을 값의 기준이다. 검색어·페이지 번호·선택한 카테고리가 전부 여기 해당한다.

주소를 컴포넌트 바깥 상수(`const API_URL = "https://api.randomuser.me/"`)로 빼 두면 나중에 주소가 바뀌어도 한 곳만 고치면 된다.

### 2-5. 선택한 항목을 상태로 올려 상세 화면 만들기

1-5에서 올려보낸 데이터를 `alert` 대신 상태에 담으면, day02에서 만든 모달·상세 화면으로 바로 이어진다.

```jsx
function ExternalApiFetcher() {
  const [selected, setSelected] = useState(null);

  return (
    <>
      <h2>외부 서버 통신</h2>
      <RandomUser onProfile={(data) => setSelected(data)} />
      {selected && (
        <div>
          <h3>{selected.name.first} {selected.name.last}</h3>
          <img src={selected.picture.large} alt="" />
          <p>{selected.email}</p>
          <button onClick={() => setSelected(null)}>닫기</button>
        </div>
      )}
    </>
  );
}
```

`상태 && <JSX>` — 값이 있으면 그리고 `null`이면 아무것도 그리지 않는 조건부 렌더링이다. 목록은 목록대로 두고 상세만 갈아끼우므로 서버를 다시 부를 일도 없다. 목록에서 이미 받아 둔 객체를 그대로 쓰기 때문이다.

### 2-6. 중첩된 값을 안전하게 꺼내기

`data.name.first`처럼 점을 여러 번 찍는 경로는 중간이 비어 있으면 그 자리에서 멈춘다. 외부 API는 항목마다 필드가 있다 없다 하는 경우가 있어서, 옵셔널 체이닝으로 받쳐 두면 화면이 죽지 않는다.

```jsx
{data?.name?.first ?? "이름 없음"}
{data.picture?.thumbnail}
```

`?.`는 "앞이 `null`·`undefined`면 거기서 멈추고 `undefined`를 내놓아라", `??`는 "왼쪽이 `null`·`undefined`일 때만 오른쪽 값을 쓴다"는 뜻이다. `||`와 달리 `0`이나 빈 문자열을 멀쩡한 값으로 인정한다.

### 2-7. 이미지 대체 텍스트와 빈 목록

`<img>`에는 `alt`를 채워 둔다. 이미지가 안 뜨거나 화면 낭독기를 쓸 때 대신 읽히는 값이고, 목록이면 그 항목을 식별할 수 있는 값을 넣는다. 그리고 응답이 비어 있을 때를 위해 삼항 하나를 더해 두면 표가 헤더만 남고 비는 상황을 설명할 수 있다.

```jsx
<tbody>
  {trTag.length > 0 ? trTag : (
    <tr><td colSpan="5">표시할 사용자가 없습니다</td></tr>
  )}
</tbody>
```

## 3. 더 나아가 알면 좋은 것

### 3-1. CORS — 외부 서버를 부를 때 처음 만나는 벽

브라우저는 **지금 열려 있는 주소와 다른 출처(도메인·포트·프로토콜)로 나가는 요청**의 응답을, 그 서버가 허락하지 않으면 자바스크립트에 넘겨 주지 않는다. 이것이 CORS(Cross-Origin Resource Sharing)다.

randomuser.me처럼 공개용 API는 `Access-Control-Allow-Origin` 헤더를 열어 두기 때문에 아무 설정 없이 불린다. 반대로 같은 수업에서 만든 스프링 서버를 `localhost:5173`(Vite)에서 부를 때 막히는 이유도 같다 — 포트가 다르면 다른 출처다. 해결은 **서버 쪽**에서 허용 출처를 여는 것이고(스프링이라면 `@CrossOrigin` 또는 CORS 설정), 개발 중에는 Vite의 프록시 설정으로 우회하기도 한다. 요청이 분명히 나갔는데 콘솔에 CORS 문구가 뜬다면 프론트 코드가 아니라 서버 설정을 볼 자리다.

### 3-2. 요청 취소와 경쟁 상태(race condition)

응답이 도착하기 전에 사용자가 다른 페이지로 넘어가면, 사라진 컴포넌트의 `setMyJSON`이 불린다. 검색어를 빠르게 바꾸면 **먼저 보낸 요청의 응답이 나중에 도착해** 엉뚱한 결과가 화면에 남기도 한다. 둘 다 정리 함수로 막는다.

```jsx
useEffect(() => {
  const controller = new AbortController();
  fetch(url, { signal: controller.signal })
    .then((res) => res.json())
    .then(setMyJSON)
    .catch((err) => {
      if (err.name !== "AbortError") console.error(err);
    });
  return () => controller.abort();   // 떠나거나 다시 부르기 직전에 취소
}, [url]);
```

생명주기 노트에서 "켜는 effect에는 끄는 정리 함수를 붙인다"고 정리한 원칙이 요청에도 그대로 적용되는 경우다.

### 3-3. 커스텀 훅으로 묶어내기

2-3의 세 상태 묶음은 통신하는 컴포넌트마다 똑같이 반복된다. 이 덩어리를 함수 하나로 빼면 컴포넌트에는 화면 코드만 남는다.

```jsx
function useFetch(url) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  useEffect(() => { /* 2-3과 같은 내용 */ }, [url]);
  return { data, loading, error };
}

// 쓰는 쪽
const { data, loading, error } = useFetch("https://api.randomuser.me/?results=20");
```

`use`로 시작하는 이름을 붙이고 내부에서 다른 훅을 쓰면 그것이 곧 커스텀 훅이다. 새 문법이 아니라 **훅을 쓰는 함수를 따로 뺀 것**뿐이라는 점이 요점이다.

### 3-4. 캐싱과 데이터 패칭 라이브러리

같은 목록을 보러 페이지를 오갈 때마다 서버를 다시 부르는 것은 낭비다. React Query(TanStack Query)나 SWR 같은 라이브러리는 응답을 캐시해 두고, 중복 요청을 합치고, 오류 시 재시도하고, 화면에 다시 들어올 때만 갱신하는 일을 대신한다. `useEffect`로 직접 짜던 2-3·3-2의 코드가 설정 몇 줄로 줄어든다. 다만 **직접 한 번 짜 보고 나서 쓰는 것**과 처음부터 쓰는 것은 이해의 깊이가 다르므로, 지금 단계에서는 손으로 짜 보는 것이 남는 게 많다.

### 3-5. API 키와 환경 변수

공개 API 중에는 키를 발급받아야 하는 곳이 많다. 프론트 코드에 키를 그대로 적으면 브라우저 개발자 도구에서 그대로 보이고, 저장소에 올리면 그대로 공개된다. Vite에서는 `.env` 파일에 `VITE_API_KEY=...`로 두고 `import.meta.env.VITE_API_KEY`로 읽되, **`.env`는 `.gitignore`에 넣는다.** 그래도 빌드 결과에는 값이 들어가므로, 정말 감춰야 하는 키는 백엔드에 두고 프론트는 우리 서버를 거쳐 부르는 구조로 간다.

### 3-6. 다음에 볼 키워드

- `axios` 인스턴스와 인터셉터(공통 헤더·토큰 자동 첨부)
- `Promise.all`로 여러 요청 동시에 보내기
- 페이지네이션·무한 스크롤(`IntersectionObserver`)
- `Context` / 전역 상태 관리 — day05의 "내부통신" 갈래
- React Query의 `useQuery`·캐시 키
- 목록 → 상세 라우팅(`:param` + `useParams`)으로 모달 대신 주소 쓰기

## 실습 파일

- `KDT_2026/2026_React/src/example/day05/ExternalApiFetcher.jsx`
- `KDT_2026/2026_React/src/main.jsx`

## 관련 노트

[[React MOC]] · [[React day05 컴포넌트 생명주기와 useEffect]] · [[React day05 axios로 백엔드에 POST 보내기]] · [[KDT_2026 학습 지도]]
