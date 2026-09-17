---
출처: Claude 분석
원본: KDT_2026/2026_React/src/example/day04/practice
작성일: 2026-09-17
tags: [학습, react]
---

# React day05 — axios로 백엔드에 POST 보내기

> 실습 파일: `src/example/day04/practice/신승민.jsx` · `src/example/day04/practice/index.css` · `src/main.jsx`
> 허브: [[React MOC]] · 이전: [[React day05 외부 API 호출과 목록 렌더링]] · 다음: (예정)

외부 API를 `axios.get`으로 읽어 오는 것까지 해 봤으니, 이번에는 반대 방향 — **폼에 입력한 값을 `axios.post`로 백엔드에 보내는** 차례다. 코드가 놓인 자리는 day04에서 만든 사이드 네비 팀 소개 실습(`day04/practice/`)의 내 페이지인데, 내용은 라우팅이 아니라 이 날 배운 axios 통신이다. 라우트 하나에 꽂힌 페이지 컴포넌트 안에서 상태·폼·통신이 전부 돌아가는 형태라, day03의 제어 컴포넌트와 day02의 POST 요청이 axios 표기로 다시 합쳐지는 모양이 된다.

## 1. 배운 내용

### 1-1. 제어 입력 세 개 — 폼 값 하나에 상태 하나

```jsx
import { useState, useEffect } from "react";
import axios from "axios";

function ProductPrint(props) {
  const [name, setName] = useState("");
  const [price, setPrice] = useState("");
  const [cno, setCno] = useState("");
  …
}
```

입력 칸마다 `useState("")`를 하나씩 두고, `value`와 `onChange`로 묶는다.

```jsx
<input
  value={name}
  onChange={(e) => {
    setName(e.target.value);
  }}
  placeholder="제품명 (예: 기계식 키보드)"
/>
<input value={cno} onChange={(e) => setCno(e.target.value)} placeholder="카테고리 번호(cno) (예: 1)" />
```

day03에서 정리한 **제어 컴포넌트**다. 화면에 보이는 값의 출처가 DOM이 아니라 상태이므로, `value={name}`만 걸고 `onChange`를 빼면 타이핑이 아예 먹지 않는다. 두 줄이 한 벌이라는 점이 핵심이다.

`onChange` 핸들러는 중괄호 블록으로 써도 되고 `setCno(e.target.value)`처럼 한 줄 축약으로 써도 된다. 같은 동작이고, 한 파일 안에서는 한 표기로 통일하는 편이 읽기 편하다.

초기값을 `""`(빈 문자열)로 둔 것도 의미가 있다. `useState()`로 두면 초기값이 `undefined`라 React가 "제어 컴포넌트가 아니었다가 제어 컴포넌트가 되었다"고 경고한다. **입력 상태의 초기값은 언제나 빈 문자열**로 시작하는 것이 안전하다.

| 상태 | 담는 값 | 백엔드로 갈 때의 타입 |
| --- | --- | --- |
| `name` | 제품명 문자열 | 그대로 문자열 |
| `price` | 가격 | `<input>`에서 나온 값은 **문자열** — 숫자 컬럼이면 변환 필요(2-2) |
| `cno` | 카테고리 번호(외래키) | 같은 이유로 숫자 변환 대상 |

### 1-2. `axios.post` — 두 번째 인수가 곧 요청 본문

```jsx
const 제품등록 = async () => {
  await axios.post("https://<백엔드주소>/api/products", { name, price, cno });
};
```

day02에서 `fetch`로 POST를 보낼 때는 세 가지를 직접 챙겨야 했다.

```jsx
// fetch — 직접 챙기는 형태
await fetch(url, {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({ name, price, cno }),
});
```

axios는 이 셋이 전부 생략된다.

| 항목 | `fetch` | `axios` |
| --- | --- | --- |
| 메소드 | `method: "POST"` | 함수 이름이 곧 메소드 (`axios.post`) |
| 헤더 | `Content-Type` 직접 지정 | 기본값이 `application/json` |
| 본문 | `JSON.stringify(객체)` | **객체 그대로** 두 번째 인수에 |

정리하면 `axios.post(주소, 보낼객체)` 한 줄이 위 다섯 줄과 같은 일을 한다. 파일 맨 아래 주석에 정리해 둔 사용법도 같은 이야기다.

```
const 함수명 = async () => {
    const response = await axios.HTTP메소드명("통신할주소?쿼리스트링", { body });
    const data = response.data;
};
```

`axios.get`·`axios.post`·`axios.put`·`axios.delete`가 전부 같은 모양이고, `get`·`delete`는 보낼 본문이 없으니 두 번째 인수 자리에 옵션(쿼리·헤더)이 들어간다는 점만 다르다.

### 1-3. `{ name, price, cno }` — 단축 프로퍼티로 본문 만들기

보낼 객체를 `{ name: name, price: price, cno: cno }`로 쓰지 않고 `{ name, price, cno }`로 적었다. 키 이름과 변수 이름이 같을 때 쓰는 **단축 프로퍼티**로, day03 전화번호부 실습에서 배열에 넣을 객체를 만들 때 쓴 표기와 같다.

이 표기가 편한 대신 조건이 하나 붙는다. **상태 변수 이름이 곧 JSON 키 이름이 되고, 그것이 백엔드 DTO의 필드명과 맞아야** 한다. day02에서 정리한 "DB 컬럼명 = JSON 키 = 프로퍼티명" 사슬이 여기서도 그대로다. 서버가 `cno`를 기대하는데 상태 이름을 `categoryNo`로 지으면 값이 `null`로 들어가므로, 상태 이름을 지을 때 서버 쪽 필드명을 먼저 확인하는 순서가 안전하다.

### 1-4. `<input type="submit">`의 `onClick`으로 보내기

```jsx
<input type="submit" name="submit" value="등록" onClick={제품등록} />
```

`onClick={제품등록}`은 **함수를 넘기는 것**이고 `onClick={제품등록()}`이 아니다. 괄호를 붙이면 렌더링하는 순간 요청이 나가 버린다 — day01부터 반복해 온 규칙이 통신에서는 결과가 더 눈에 띄는 셈이다.

여기서는 `<form>` 없이 버튼의 `onClick`만으로 처리했다. 이렇게 하면 폼 제출 기본 동작(페이지 이동)이 애초에 일어나지 않아 `preventDefault`가 필요 없다. 반대로 `<form onSubmit>`으로 감싸면 엔터 키 제출·브라우저 기본 검증 같은 것이 따라오는 대신 `e.preventDefault()`가 필수가 된다. 둘 중 무엇을 쓸지는 **엔터로도 제출되길 원하는가**로 가르면 된다(2-1).

함수 이름을 `제품등록`처럼 한글로 지어도 자바스크립트 식별자로 문제없이 동작한다. 컴포넌트 이름의 대문자 규칙(day01)과는 다른 자리라 제약이 없다. 다만 협업에서는 영문으로 통일하는 편이 안전하다.

### 1-5. 페이지 컴포넌트 안에 부품 하나 — `ProductPrint` / `Seung`

```jsx
function ProductPrint(props) { … }          // 내보내지 않는 내부 부품

export default function Seung(props) {
  return (
    <>
      <ProductPrint></ProductPrint>
    </>
  );
}
```

`Seung`은 day04 라우트 표(`App3`)의 `path="seung"`에 꽂히는 **페이지 컴포넌트**이고, 실제 폼과 통신은 그 안의 `ProductPrint`가 맡는다. 한 파일 안에 컴포넌트를 두 개 두되 바깥 것만 `export default`하는 구조는 day01에서 헤더·메인·푸터를 조립할 때 쓴 형태와 같다.

이렇게 나눠 두면 나중에 같은 페이지에 목록 컴포넌트(`ProductList`)를 하나 더 붙일 때 `Seung`의 `return`에 태그 한 줄만 추가하면 된다. 등록 폼과 목록이 따로 있으면 "등록 후 목록 새로고침"을 콜백 props로 잇는 자리도 자연스럽게 생긴다(2-4).

### 1-6. 표 안에 폼을 넣을 때의 레이아웃 — `flex` 두 겹

```css
.sTbody {
  display: flex;
}
.inputWrap {
  display: flex;
  flex-direction: column;
}
.inputWrap > input {
  width: 500px;
  padding: 5px;
  margin-top: 10px;
}
```

입력 네 개를 세로로 쌓기 위해 `<div className="inputWrap">`으로 묶고 `flex-direction: column`을 줬다. `<td>` 하나에 입력들을 나란히 넣으면 가로로 늘어서는데, 감싸는 `div`에 세로 방향 `flex`를 걸면 줄바꿈 태그 없이 세로로 정렬된다.

여기서 알아 둘 점은 **`<table>` 계열 태그에 `display: flex`를 주면 표로서의 성질이 사라진다**는 것이다. `tbody`·`tr`·`td`는 각각 `display: table-row-group`·`table-row`·`table-cell`이 기본값이고, 이걸 `flex`로 덮으면 칸 정렬·`border` 합치기 같은 표 동작이 함께 바뀐다. 입력 폼처럼 자유로운 배치가 필요한 부분은 표 대신 `div` + `flex`로 짜고, 표는 여러 줄의 데이터를 줄 맞춰 보여 줄 때만 쓰는 편이 예측하기 쉽다.

day04 실습에서 쓰던 `index.css`에 이 규칙들이 덧붙었다. `import`한 CSS는 전역이므로(day03), 팀원 각자가 같은 파일에 규칙을 추가하면 클래스 이름이 겹칠 때 서로 영향을 준다. 그래서 `.sTbody`·`.inputWrap`처럼 **자기 페이지에서만 쓰는 접두사 붙은 이름**을 고르는 편이 안전하다.

## 2. 추가로 알면 좋은 활용법

### 2-1. `<form onSubmit>`으로 감싸기 — 엔터 제출과 초기화

```jsx
const 제품등록 = async (e) => {
  e.preventDefault();
  await axios.post(url, { name, price: Number(price), cno: Number(cno) });
  setName("");
  setPrice("");
  setCno("");
};

<form onSubmit={제품등록}>
  …
  <input type="submit" value="등록" />
</form>;
```

`<form>`으로 감싸고 `onSubmit`에 걸면 **입력 칸에서 엔터를 쳐도 제출**된다. 대신 기본 동작(GET 이동)을 `preventDefault`로 막아야 한다. 그리고 전송이 끝나면 상태를 빈 문자열로 되돌려 입력 칸을 비운다 — 제어 컴포넌트에서는 `setXXX("")` 한 줄이 곧 폼 초기화다.

### 2-2. 숫자 필드는 보내기 직전에 변환

`<input>`에서 나온 값은 `type="number"`를 줘도 **문자열**이다. 백엔드 DTO의 필드가 `int`·`long`이면 `"45000"` 같은 문자열이 그대로 가서 변환 오류가 나기 쉽다.

```jsx
await axios.post(url, {
  name: name.trim(),
  price: Number(price),
  cno: Number(cno),
});
```

보내기 직전에 한 번에 바꾸면 상태는 문자열로 단순하게 두고 요청만 정확해진다. `Number("")`는 `0`, `Number("abc")`는 `NaN`이므로 빈 값 검사와 같이 두는 것이 좋다.

### 2-3. 응답 확인과 오류 처리

```jsx
const 제품등록 = async () => {
  try {
    const response = await axios.post(url, body);
    console.log(response.status, response.data);
    alert("등록되었습니다");
  } catch (err) {
    console.error(err);
    alert("등록에 실패했습니다");
  }
};
```

`await`만 걸고 결과를 보지 않으면 **실패해도 화면에 아무 표시가 없다.** axios는 404·500 같은 HTTP 오류를 자동으로 `catch`로 보내 주므로(`fetch`는 `res.ok` 확인이 따로 필요하다) `try/catch`만 둘러 두면 성공·실패가 갈린다. `response.status`(201 등)와 `response.data`(서버가 돌려준 결과)를 확인하는 습관까지 붙이면 디버깅이 훨씬 빨라진다.

전송 중에 버튼을 여러 번 누르는 것을 막으려면 `const [sending, setSending] = useState(false)`를 하나 두고 `disabled={sending}`을 거는 방법이 간단하다.

### 2-4. 등록 후 목록 새로고침

서버에 값을 넣었다고 화면이 저절로 바뀌지는 않는다. 같은 화면에 목록이 있다면 등록 성공 뒤 목록을 다시 불러야 한다.

```jsx
await axios.post(url, body);
const res = await axios.get(url);   // 다시 조회
setList(res.data);
```

day02의 CRUD 노트에서 정리한 "POST 뒤 재조회"와 같은 흐름이다. 목록 컴포넌트가 분리되어 있으면 부모가 목록 상태를 들고 있고, 등록 폼은 콜백 props(`onRegistered`)로 "끝났다"만 알리는 구조가 깔끔하다.

### 2-5. 주소를 상수·환경 변수로 빼기

```jsx
const API_BASE = import.meta.env.VITE_API_BASE;
await axios.post(`${API_BASE}/api/products`, body);
```

백엔드 주소는 개발 중에 자주 바뀐다. 터널 주소나 임시 포트를 파일마다 적어 두면 바뀔 때마다 전부 고쳐야 하고, 저장소에 올라가면 그대로 공개된다. 컴포넌트 바깥 상수로 한 번만 두거나, Vite의 `.env`(`VITE_`로 시작하는 이름만 읽힌다)에 넣고 `.gitignore`에 `.env`를 추가해 두는 편이 안전하다.

### 2-6. axios 인스턴스로 공통 설정 모으기

```jsx
// src/api/http.js
import axios from "axios";
export const http = axios.create({
  baseURL: import.meta.env.VITE_API_BASE,
  timeout: 5000,
});

// 쓰는 쪽
import { http } from "../../api/http";
await http.post("/api/products", body);
```

`axios.create`로 만든 인스턴스는 `baseURL`·타임아웃·공통 헤더를 미리 물고 있다. 파일마다 긴 주소를 적지 않아도 되고, 나중에 로그인 토큰을 모든 요청에 붙일 때 인터셉터 한 곳만 고치면 된다.

## 3. 더 나아가 알면 좋은 것

### 3-1. 입력 여러 개를 객체 상태 하나로

입력이 늘어날수록 `useState`가 줄줄이 늘어난다. 폼 전체를 객체 하나로 두면 핸들러도 하나로 줄어든다.

```jsx
const [form, setForm] = useState({ name: "", price: "", cno: "" });

const onChange = (e) => {
  setForm({ ...form, [e.target.name]: e.target.value });
};

<input name="name" value={form.name} onChange={onChange} />
<input name="price" value={form.price} onChange={onChange} />

await axios.post(url, form);   // 그대로 본문으로
```

`[e.target.name]`은 **계산된 프로퍼티 이름**이다. 대괄호 안의 값이 키가 되므로 입력의 `name` 속성이 곧 상태의 키가 된다. 객체 상태는 주소값이 바뀌어야 재렌더링되므로 스프레드 복사(`{ ...form }`)를 잊지 않는다 — day02 `ProductManager`에서 쓴 방식과 같고, 폼 전체를 그대로 요청 본문으로 넘길 수 있다는 것이 덤이다.

### 3-2. 프론트 검증과 백엔드 검증은 따로

빈 값·형식 검사는 프론트에서 하면 사용자 경험이 좋아지지만, **보안 장치는 아니다.** 브라우저 개발자 도구나 별도 도구로 요청을 직접 보내면 프론트 코드를 거치지 않는다. 그래서 같은 검증을 백엔드에서 한 번 더 한다(스프링이라면 `@Valid` + DTO의 제약 어노테이션). 프론트 검증은 "실수를 빨리 알려 주는 장치", 백엔드 검증은 "잘못된 데이터를 막는 장치"로 역할이 다르다.

### 3-3. CORS와 개발용 터널 주소

로컬 Vite(`localhost:5173`)에서 다른 도메인의 백엔드를 부르면 출처가 달라 CORS 설정이 필요하다. 터널 서비스로 외부에 노출한 개발 서버도 마찬가지라 서버 쪽에서 허용 출처를 열어야 한다. 프론트 코드가 멀쩡한데 콘솔에 CORS 문구가 뜨면 볼 자리는 서버 설정이다. Vite의 `server.proxy` 설정으로 개발 중에만 우회하는 방법도 있다.

터널 주소는 재시작할 때마다 바뀌는 임시 주소이기도 하다. 코드에 박아 두면 다음 날 전부 고쳐야 하므로 2-5처럼 한 곳에 모아 두는 것이 실질적인 이득이 된다.

### 3-4. 다음에 볼 키워드

- `axios.create` 인스턴스 · 요청/응답 인터셉터 · 공통 에러 처리
- `FormData`와 파일 업로드(`multipart/form-data`)
- 낙관적 업데이트(요청 전에 화면 먼저 반영하고 실패하면 되돌리기)
- React Hook Form · Zod 같은 폼·스키마 검증 도구
- React Query의 `useMutation`(등록·수정·삭제와 캐시 무효화)
- 스프링 쪽 `@RestController` · `@RequestBody` · `@Valid` · CORS 설정

## 실습 파일

- `KDT_2026/2026_React/src/example/day04/practice/신승민.jsx` — 제어 입력 세 개 + `axios.post`로 제품 등록
- `KDT_2026/2026_React/src/example/day04/practice/index.css` — 폼 영역 `flex` 세로 배치(`.sTbody`·`.inputWrap`)
- `KDT_2026/2026_React/src/main.jsx` — `BrowserRouter`로 감싼 `App3` 렌더링 유지

## 관련 노트

[[React MOC]] · [[React day05 외부 API 호출과 목록 렌더링]] · [[React day04 React Router 도입과 라우트 정의]] · [[React day03 폼 제출과 입력값 읽기]] · [[React day02 useEffect와 fetch로 서버 CRUD]] · [[KDT_2026 학습 지도]]
