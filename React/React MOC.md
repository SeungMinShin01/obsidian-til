---
출처: Claude 분석
작성일: 2026-09-11
tags: [허브, react]
---

# React MOC

React 학습노트의 허브입니다. 상위 지도는 [[KDT_2026 학습 지도]]. (JavaScript에서 분리 — 원본 코드: `KDT_2026/2026_React`, Vite 프로젝트 `src/example/dayNN`)

## 학습 순서

[[React day01 컴포넌트와 렌더링]] → [[React day02 객체 배열과 map 렌더링]] → [[React day02 컴포넌트 분리와 콜백 props]] → [[React day02 useState와 상태 갱신]] → [[React day02 useEffect와 fetch로 서버 CRUD]] → [[React day02 모달과 컴포넌트 간 상태 전달]] → [[React day03 JSX 스타일링과 이미지 경로]] → [[React day03 폼 제출과 입력값 읽기]]

## 노트

| 노트 | 핵심 |
| --- | --- |
| [[React day01 컴포넌트와 렌더링]] | Vite 프로젝트 구조(`package.json`·`type: module`·`react`/`react-dom` 분리), `index.html`의 빈 `#root`와 모듈 스크립트 진입점, `createRoot(root).render(<App />)` 3단계, 컴포넌트 = JSX를 반환하는 함수(대문자 이름·`props`·`export default`), 태그로 쓰는 컴포넌트, JSX와 HTML의 차이(`className`·`onClick={}`·자기 닫힘·프래그먼트), 컴포넌트 안에 컴포넌트 조립(헤더·메인·푸터, 내보내지 않는 내부 부품), 함수 선언·화살표·함수 표현식 세 표기, props(매개변수·인수 용어, 부모→자식 읽기 전용 객체, `props.name` vs 구조 분해 `{ name, age }`, JSX 주석 `{/* */}`), 배열 props를 반복문으로 `<li>` 목록 찍기(`key`, `{배열}` 펼침), 이벤트 `onClick={함수}`(카멜케이스·함수를 넘기고 실행하지 않기·인라인 화살표), `useState`와 선언형 렌더링으로 이어지는 자리 |
| [[React day02 객체 배열과 map 렌더링]] | 서버 응답을 가정한 객체 배열(`{ name, imageUrl }`)을 `data.map(...)`으로 돌려 `Profile` 컴포넌트 목록 찍기, 인덱스 하드코딩 → `map` 한 줄로 가는 이유, props만 받는 순수 부품, `key` 선택 기준, 콜백 축약·구조 분해·스프레드 props, 목록 컴포넌트 3겹 나누기, 빈 배열 처리, `useState`+`useEffect`+axios로 이어지는 자리 |
| [[React day02 컴포넌트 분리와 콜백 props]] | 부품을 파일 하나씩으로 나눠 `import`/`export default`로 조립(`./` 상대 경로, 파일명 = 컴포넌트명), 함수 선언 vs `const` 화살표 표기, 함수를 props로 내려보내고 자식이 호출해 부모에 알리는 콜백 props(데이터는 내려가고 이벤트는 올라감), 콜백은 넘길 때 실행하지 않기(`cal(plus)` vs `cal(plus(3,5))`), `<a>`의 GET 이동을 `preventDefault`로 막는 이유(CSR 깜빡임), props·구조 분해 용어 정리, `on`/`handle` 이름 관례, 클릭한 항목 id 올려보내기, 상태 끌어올리기·React Router·Context로 이어지는 자리 |
| [[React day02 useState와 상태 갱신]] | 전역·지역 변수는 늘어나도 화면이 안 바뀌는 이유(`return`이 한 번만 실행), `useState(초기값)` → `[값, setXXX]` 구조 분해, `setXXX`가 컴포넌트를 재호출해 화면을 새로고침하고 상태값은 유지되는 원리, 배열·객체 상태는 **주소값이 바뀌어야** 재렌더링(`push`만으로는 X → `[...array]`/`{...obj}` 스프레드 복사), `mode` 상태로 `FrontComp`/`BackComp`를 골라 그리는 조건부 렌더링(JSX를 변수에 담아 `if`로 갈아끼우기), 콜백 props로 자식이 부모 상태를 바꾸는 상태 끌어올리기(`setMode` 감싸 넘기기 vs 그대로 넘기기), 함수형 업데이트·불변성·Virtual DOM·`useEffect`로 이어지는 자리 |
| [[React day02 useEffect와 fetch로 서버 CRUD]] | 실습 2(통합 제품 관리)의 `CategoryManager`로 보는 서버 통신 기본형 — DB 컬럼명 = JSON 키 = 프로퍼티명(`totalPractice.sql`), 목록 초기값 `[]`, `async/await` + `fetch` → `res.ok` → `res.json()` → `Array.isArray` 방어, `useEffect(…, [])`로 첫 렌더링 뒤 한 번만 조회(본문에서 부르면 무한 반복), POST(`Content-Type: application/json` + `JSON.stringify`) 뒤 재조회, DELETE는 쿼리 스트링 `?cno=`, `window.confirm`, 제어 컴포넌트(`value`/`onChange`, `setName('')`로 비우기), `<form onSubmit>` + `preventDefault`, 빈 목록 삼항과 `key={cat.cno}`, 오류·로딩 상태, 주소 상수화, CORS·StrictMode 이중 실행·AXIOS로 이어지는 자리 |
| [[React day02 모달과 컴포넌트 간 상태 전달]] | `ProductManager`·`ReviewManager` — 상태 7개(목록·모달 boolean·모달+대상 객체·폼 객체), 객체 폼 상태의 스프레드 갱신(`{ ...form, name }`), `<select value>` 제어와 옵셔널 체이닝, 문자열 → `Number` 변환, 모달 = `상태 && <JSX>` + `position: fixed` 배경, 인라인 `style` 객체 두 겹, 자식→부모 콜백 `oncategoryupdated(list)`로 두 벌의 목록 맞추기, `product`·`onclose`로 자식이 모달 껍데기까지 그리는 패턴, `useEffect` 의존성 `[product?.bno]`, 수정 모달(폼 채우기 + PUT 본문에 키), `repeat`로 별점, `onChange` 합치기·`Modal` 컴포넌트와 `children`·상태 끌어올리기 한계 → Context·커스텀 훅·포털로 이어지는 자리 |
| [[React day03 JSX 스타일링과 이미지 경로]] | `exam1.jsx` — 인라인 `style`은 문자열이 아니라 객체(중괄호 두 겹, `backgroundColor` 카멜케이스, 단위까지 문자열, 컴포넌트 바깥 상수로 재사용), CSS 파일을 `import "../../index.css"`로 끌어와 `className`·`id`로 붙이기(`class` 예약어, import한 CSS는 전역), 이미지 세 경로(`public/` 절대 경로 vs `src/assets` `import`로 해시 경로 vs 외부 URL), `main.jsx`에서 진입 컴포넌트 갈아끼우기, 조건부 `className`·스타일 객체 스프레드·인라인과 CSS 파일 역할 나누기, CSS Modules·Tailwind·styled-components로 이어지는 자리 |
| [[React day03 폼 제출과 입력값 읽기]] | `exam2.jsx` — `<form onSubmit>`은 버튼이 아니라 폼의 이벤트, `preventDefault`로 GET 이동 차단, `event.target`이 폼 자신이라 `event.target.name속성.value`로 상태 없이 입력값 읽기(`name` 필수), 상태 없는 `WriteForm`이 값을 콜백 props로 올리고 부모가 검증·`message` 상태 갱신, `<input>` 세 개 비교(비제어 · 고정 `value`는 타이핑 불가 · `value`+`onChange` 제어), 제어 vs 비제어 고르는 기준, `FormData`·`reset()`·`trim()`·`defaultValue`, `useRef`·React Hook Form으로 이어지는 자리 |

## 앞선 갈래

순수 JS·DOM 조작(2026_FE)은 JavaScript MOC 관할이다. React 수업의 선행 흐름은 JS day11 DOM 조작 → JS day14 게시판 CRUD → 여기(평문 안내 — 구역 간 직접 링크는 걸지 않는다).
