---
출처: Claude 분석
원본: KDT_2026/2026_React/src/example/day02/practice2
작성일: 2026-09-14
tags: [학습, react]
---

# React day02 — useEffect와 fetch로 서버 CRUD

> 실습 파일: `src/example/day02/practice2/CategoryManager.jsx` (+ `2026B_Spring/springweb/src/main/resources/sql/totalPractice.sql`, `useDB.sql`)
> 허브: [[React MOC]] · 이전: [[React day02 useState와 상태 갱신]] · 다음: [[React day02 모달과 컴포넌트 간 상태 전달]]

day02의 네 번째 갈래이자 실습 2다. 앞 노트에서 "언젠가 볼 것"으로 미뤄 둔 `useEffect`·서버 통신이 한꺼번에 들어온다. 실습 2는 카테고리·제품·리뷰 세 컴포넌트로 된 "통합 제품 관리" 화면인데, 이 노트는 그중 가장 작은 `CategoryManager` 하나로 **서버에서 목록을 받아 그리고, 등록·삭제 뒤 다시 받아오는** 기본 흐름만 정리한다. 나머지 두 컴포넌트(모달·컴포넌트 간 전달)는 다음 노트로 넘긴다.

## 1. 배운 내용

### 1-1. 실습 2의 전체 그림

```
ProductManager  ── 제품 목록·등록·수정·삭제 (화면 전체)
 ├─ CategoryManager  ── 카테고리 목록·등록·삭제 (모달 안)
 └─ ReviewManager    ── 제품 하나의 리뷰 목록·등록·삭제 (모달)
```

세 컴포넌트가 전부 `http://localhost:8080/api/...`로 요청을 보낸다. 백엔드는 Spring 쪽에서 준비하는 REST API이고, 프론트는 응답 JSON의 모양만 알면 된다. 그 모양은 같은 날 만들어 둔 SQL 샘플 데이터에 그대로 적혀 있다.

```sql
-- totalPractice.sql (일부)
INSERT INTO category (cno, name) VALUES (1, '전자기기');
INSERT INTO product (bno, name, price, cno) VALUES (1, '기계식 키보드', 89000, 1);
INSERT INTO review (rno, bno, reviewer, content, rating) VALUES (1, 1, '김철수', '키감이 매우 쫀득하고 좋습니다.', 5);
```

| 테이블 | 키 | 필드 | 프론트에서 쓰는 이름 |
| --- | --- | --- | --- |
| category | `cno` | `name` | `cat.cno`, `cat.name` |
| product | `bno` | `name`, `price`, `cno`(FK) | `p.bno`, `p.name`, `p.price`, `p.cno` |
| review | `rno` | `bno`(FK), `reviewer`, `content`, `rating` | `r.rno`, `r.reviewer`, `r.content`, `r.rating` |

DB 컬럼명 = JSON 키 = 프론트 프로퍼티명. 세 층의 이름을 맞춰 두면 변환 코드가 사라진다. 앞 노트(객체 배열과 map)에서 "필드 이름을 맞추는 일이 프론트·백 협업의 첫 약속"이라고 적어 둔 것이 여기서 실제로 나타난다.

### 1-2. CategoryManager — 상태 두 개

```jsx
// src/example/day02/practice2/CategoryManager.jsx
import React, { useState, useEffect } from 'react';

export default function CategoryManager({ oncategoryupdated }) {
  const [categories, setCategories] = useState([]);   // 서버에서 받은 목록
  const [name, setName] = useState('');               // 입력창 값
  // ...
}
```

| 상태 | 초기값 | 역할 |
| --- | --- | --- |
| `categories` | `[]` | 서버 응답을 담는 목록. 처음엔 비어 있다가 조회가 끝나면 채워진다 |
| `name` | `''` | 등록 폼의 입력값. 글자를 칠 때마다 바뀐다 |

목록의 초기값을 `[]`로 두는 것이 중요하다. 아직 서버 응답이 오기 전에도 `categories.map(...)`이나 `categories.length`가 오류 없이 돌아야 하기 때문이다. `null`로 두면 첫 렌더링에서 바로 터진다.

### 1-3. 조회 함수 — async/await + fetch

```jsx
const fetchcategories = async () => {
  try {
    const res = await fetch('http://localhost:8080/api/categories');
    if (res.ok) {
      const data = await res.json();
      const list = Array.isArray(data) ? data : [];
      setCategories(list);
      if (oncategoryupdated) oncategoryupdated(list);
    }
  } catch (err) {
    console.error('카테고리 조회 실패:', err);
  }
};
```

| 단계 | 코드 | 의미 |
| --- | --- | --- |
| ① 요청 | `await fetch(url)` | GET 요청을 보내고 응답 헤더가 올 때까지 기다린다. 결과는 `Response` 객체 |
| ② 상태 확인 | `res.ok` | HTTP 상태가 200번대면 `true`. 404·500이면 `false`라 본문을 읽지 않고 넘어간다 |
| ③ 본문 파싱 | `await res.json()` | 본문 문자열을 JS 값으로 바꾼다. 이것도 비동기라 한 번 더 `await` |
| ④ 방어 | `Array.isArray(data) ? data : []` | 배열이 아닌 것이 오면 빈 배열로 대체 — 이후 `map`이 안전해진다 |
| ⑤ 상태 갱신 | `setCategories(list)` | 새 배열 주소가 들어가므로 재렌더링된다 |
| ⑥ 실패 | `catch` | 서버가 꺼져 있거나 네트워크가 끊기면 여기로. `fetch`는 4xx·5xx로는 예외를 던지지 않고 **연결 자체가 안 될 때만** 던진다 |

`fetch`는 브라우저 내장이라 별도 설치가 없다. JS 수업에서 `XMLHttpRequest`·AXIOS로 하던 일을 같은 자리에서 하는 셈이다. `res.ok`와 `res.json()` 두 단계로 나뉘는 점이 AXIOS(`r.data` 한 번에)와 다른 부분이다.

⑥에서 `oncategoryupdated(list)`는 부모에게 "목록이 이렇게 바뀌었다"고 알리는 콜백 props다. 자세한 흐름은 다음 노트에서 본다.

### 1-4. useEffect — "처음 그려진 뒤 한 번" 조회

```jsx
useEffect(() => {
  fetchcategories();
}, []);
```

컴포넌트 함수 본문에서 `fetchcategories()`를 그냥 부르면 안 된다. 조회 → `setCategories` → 재렌더링 → 함수 본문 재실행 → 다시 조회 … 무한 반복이 된다. `useEffect`는 **렌더링이 끝난 뒤에** 실행할 일을 등록하는 훅이고, 두 번째 인수(의존성 배열)가 `[]`이면 **처음 한 번만** 실행된다.

| 두 번째 인수 | 실행 시점 |
| --- | --- |
| 없음 | 렌더링될 때마다 |
| `[]` | 첫 렌더링 뒤 한 번 |
| `[a, b]` | 첫 렌더링 뒤 + `a`나 `b`가 바뀐 렌더링 뒤 |

그래서 화면이 열리는 순서는 이렇게 된다 — ① 빈 목록으로 한 번 그림("등록된 카테고리가 없습니다") → ② `useEffect`가 조회 시작 → ③ 응답이 오면 `setCategories` → ④ 목록이 채워진 화면으로 다시 그림. 잠깐 빈 화면이 보이는 건 정상이다.

### 1-5. 등록 — POST와 재조회

```jsx
const handlecreate = async (e) => {
  e.preventDefault();
  if (!name.trim()) return alert('카테고리명을 입력해주세요.');
  try {
    const res = await fetch('http://localhost:8080/api/categories', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name }),
    });
    if (res.ok) {
      setName('');          // 입력창 비우기
      fetchcategories();    // 목록 다시 받기
    }
  } catch (err) { console.error('카테고리 등록 실패:', err); }
};
```

| 항목 | 설명 |
| --- | --- |
| `e.preventDefault()` | `<form onSubmit>`의 기본 동작(페이지 이동)을 막는다. 앞 노트의 `<a>`와 같은 이유 — CSR에서는 새로고침이 곧 상태 초기화다 |
| `name.trim()` | 공백만 친 입력을 걸러 낸다. 빈 문자열은 falsy라 `!`로 검사된다 |
| `method: 'POST'` | 두 번째 인수 객체로 메소드·헤더·본문을 지정한다. 안 주면 GET |
| `Content-Type: application/json` | 본문이 JSON임을 서버에 알린다. Spring의 `@RequestBody`가 이 헤더를 보고 DTO로 바꾼다 |
| `JSON.stringify({ name })` | 객체를 JSON 문자열로. `{ name }`은 `{ name: name }`의 축약 |
| 성공 뒤 `fetchcategories()` | 응답에 새 항목을 직접 끼워 넣지 않고 **목록을 통째로 다시 받는다**. 서버가 매긴 `cno`까지 정확히 반영되므로 가장 단순하고 안전한 방식 |

### 1-6. 삭제 — 쿼리 스트링과 DELETE

```jsx
const handledelete = async (cno) => {
  if (!window.confirm('해당 카테고리를 삭제하시겠습니까? (연결된 제품 확인 필요)')) return;
  const res = await fetch(`http://localhost:8080/api/categories?cno=${cno}`, { method: 'DELETE' });
  if (res.ok) fetchcategories();
};
```

삭제는 본문이 없다. 지울 대상의 번호를 **쿼리 스트링** `?cno=3`으로 붙여 보낸다. 템플릿 리터럴(백틱)로 `${cno}`를 끼워 넣는다. `window.confirm`은 확인 창을 띄우고 "취소"면 `false`를 돌려주니 그 자리에서 함수를 끝낸다. 실습 2 전체가 같은 규칙이다 — 제품은 `?bno=`, 리뷰는 `?rno=`.

| 요청 | 메소드 | 대상 지정 | 본문 |
| --- | --- | --- | --- |
| 목록 조회 | GET | 없음 | 없음 |
| 등록 | POST | 없음 | JSON |
| 삭제 | DELETE | `?cno=` 쿼리 스트링 | 없음 |

### 1-7. 제어 컴포넌트 — 입력창과 상태를 묶기

```jsx
<form onSubmit={handlecreate}>
  <input type="text" value={name} onChange={(e) => setName(e.target.value)} />
  <button type="submit">추가</button>
</form>
```

`value={name}`으로 상태를 입력창에 내려 주고, `onChange`로 글자가 바뀔 때마다 상태를 올려 준다. 입력창의 값을 React 상태가 **소유**하는 이 방식을 제어 컴포넌트라고 한다. 덕분에 등록 뒤 `setName('')` 한 줄로 입력창이 비워진다 — DOM을 직접 만지지 않고 상태만 바꾼 것이다. JS 수업에서 `document.querySelector('#name').value = ''`로 하던 일이 상태 하나로 바뀐 셈이다.

버튼은 `type="submit"`이라 클릭이든 엔터든 `<form onSubmit>`으로 모인다. 버튼에 `onClick`을 따로 달지 않는다.

### 1-8. 빈 목록과 map을 삼항으로 가르기

```jsx
<tbody>
  {categories.length === 0 ? (
    <tr><td colSpan="3">등록된 카테고리가 없습니다.</td></tr>
  ) : (
    categories.map((cat) => (
      <tr key={cat.cno}>
        <td>{cat.cno}</td>
        <td>{cat.name}</td>
        <td><button onClick={() => handledelete(cat.cno)}>삭제</button></td>
      </tr>
    ))
  )}
</tbody>
```

앞 노트 2-5에서 예고한 조건부 렌더링이 그대로 쓰였다. `key`는 서버가 준 고유값 `cat.cno`다 — 삭제가 있는 목록이라 인덱스를 쓰면 안 되는 경우다. 삭제 버튼의 `onClick={() => handledelete(cat.cno)}`는 "함수를 넘기고 실행하지 않기"의 인수 있는 버전이다. 화살표로 한 겹 감싸야 클릭 시점에 실행된다.

## 2. 추가로 알면 좋은 활용법

### 2-1. 응답 실패도 화면에 알리기

지금은 실패하면 `console.error`만 남고 화면은 조용하다. 사용자가 알 수 있게 하려면 상태를 하나 더 둔다.

```jsx
const [error, setError] = useState(null);
const fetchcategories = async () => {
  try {
    const res = await fetch(url);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    setCategories(await res.json());
    setError(null);
  } catch (err) {
    setError(err.message);
  }
};
// JSX
{error && <p style={{ color: 'red' }}>{error}</p>}
```

`res.ok`가 아닐 때 직접 `throw`하면 4xx·5xx도 `catch` 한 곳에서 처리할 수 있다.

### 2-2. 로딩 상태

```jsx
const [loading, setLoading] = useState(true);
const fetchcategories = async () => {
  setLoading(true);
  try { /* ... */ } finally { setLoading(false); }
};
{loading ? <p>불러오는 중…</p> : categories.length === 0 ? <p>없음</p> : categories.map(/* ... */)}
```

`finally`는 성공·실패 상관없이 실행되므로 로딩 해제를 두 번 쓰지 않아도 된다. 삼항을 두 번 겹치는 것이 읽기 어려우면 `if`로 먼저 걸러 `return`하는 편이 낫다.

### 2-3. 주소를 상수로 뽑기

세 컴포넌트에 `http://localhost:8080`이 반복된다. 배포하면 주소가 바뀌므로 한 곳으로 모은다.

```jsx
// src/api.js
export const API = 'http://localhost:8080/api';
// 사용
fetch(`${API}/categories`)
```

Vite에서는 `.env` 파일의 `VITE_API_URL`을 `import.meta.env.VITE_API_URL`로 읽는 방식이 표준이다. 개발·배포 주소를 파일 하나 바꿔서 갈아 끼울 수 있다.

### 2-4. fetch를 감싼 헬퍼

`method`·`headers`·`JSON.stringify`가 매번 반복된다면 한 번 감싼다.

```jsx
const postJson = (url, body) =>
  fetch(url, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) });

await postJson(`${API}/categories`, { name });
```

AXIOS를 쓰면 `axios.post(url, { name })` 한 줄로 같은 일을 하고 JSON 변환·헤더도 자동이다. 수업 주석에 AXIOS가 예고돼 있으니, `fetch`로 원리를 익힌 뒤 갈아타면 된다.

### 2-5. useEffect 안에서 async를 쓰는 방법

`useEffect(async () => { ... }, [])`처럼 콜백 자체를 `async`로 만들면 안 된다 — `useEffect`의 콜백은 정리 함수를 반환해야 하는데 `async` 함수는 Promise를 반환하기 때문이다. 오늘처럼 **바깥에 `async` 함수를 정의하고 `useEffect` 안에서 부르는** 형태가 표준이다. 안에서 즉시 정의해 부르는 방식도 있다.

```jsx
useEffect(() => {
  (async () => { await fetchcategories(); })();
}, []);
```

## 3. 더 나아가 알면 좋은 것

### 3-1. CORS — 5173에서 8080으로 요청하면 막히는 이유

Vite 개발 서버는 `localhost:5173`, Spring은 `localhost:8080`이다. 포트가 다르면 브라우저는 **다른 출처**로 보고, 서버가 `Access-Control-Allow-Origin` 헤더로 허락하지 않으면 응답을 버린다. 그래서 백엔드 컨트롤러에 `@CrossOrigin`을 붙이거나 전역 CORS 설정을 두어야 오늘 코드가 돈다. 프론트 코드만으로는 해결할 수 없고, Vite의 `server.proxy` 설정으로 개발 중에만 우회하는 방법도 있다.

### 3-2. 재조회 대신 낙관적 갱신

지금은 등록·삭제마다 목록을 다시 받는다. 요청이 한 번 더 가지만 서버가 정답이라 안전하다. 목록이 크거나 반응을 더 빠르게 하고 싶으면 응답을 기다리기 전에 화면부터 바꾸고(낙관적 갱신), 실패하면 되돌리는 방식을 쓴다. 이 단계에서는 재조회가 정답이다.

### 3-3. 요청 취소와 StrictMode 이중 실행

개발 모드에서 `StrictMode`가 켜져 있으면 `useEffect`가 두 번 실행되어 조회가 두 번 간다. 결과가 같으니 오늘 코드에서는 문제가 없지만, 등록 같은 요청을 `useEffect`에 넣으면 두 번 등록된다. `useEffect`에는 **조회만** 넣고, 변경 요청은 이벤트 핸들러에 둔다는 원칙이 여기서 나온다. 정리 함수에서 `AbortController`로 진행 중인 요청을 취소하는 패턴은 그 다음 단계다.

### 3-4. 다음에 볼 키워드

- `useEffect` 정리 함수(cleanup)와 의존성 배열에 값이 있을 때의 재실행 — 다음 노트의 `[product?.bno]`
- AXIOS — `axios.get/post/delete`, 인스턴스와 `baseURL`, 인터셉터
- CORS와 `@CrossOrigin`, Vite `server.proxy`
- 커스텀 훅 — `useCategories()`로 조회·등록·삭제를 묶어 컴포넌트에서 빼기
- React Query(TanStack Query) — 서버 상태 캐싱·재조회를 라이브러리에 맡기기

## 실습 파일

- `KDT_2026/2026_React/src/example/day02/practice2/CategoryManager.jsx` — 카테고리 목록 조회(`useEffect` + `fetch`)·등록(POST JSON)·삭제(DELETE 쿼리 스트링), 제어 컴포넌트 폼, 빈 목록 삼항
- `KDT_2026/2026B_Spring/springweb/src/main/resources/sql/useDB.sql` — 실습 DB 생성·선택
- `KDT_2026/2026B_Spring/springweb/src/main/resources/sql/totalPractice.sql` — category·product·review 샘플 데이터 (프론트가 받는 JSON 필드 이름의 출처)

## 관련 노트

[[React MOC]] · [[React day02 useState와 상태 갱신]] · [[React day02 모달과 컴포넌트 간 상태 전달]] · [[React day02 객체 배열과 map 렌더링]] · [[KDT_2026 학습 지도]]
