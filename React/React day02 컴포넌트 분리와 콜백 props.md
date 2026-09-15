---
출처: Claude 분석
원본: KDT_2026/2026_React/src/example/day02
작성일: 2026-09-14
tags: [학습, react]
---

# React day02 — 컴포넌트 분리와 콜백 props

> 실습 파일: `src/example/day02/exam1.jsx` · `FrontComp.jsx` · `BackComp.jsx`
> 허브: [[React MOC]] · 이전: [[React day02 객체 배열과 map 렌더링]] · 다음: [[React day02 useState와 상태 갱신]]

day02의 두 번째 갈래다. day01에서는 부품 컴포넌트를 **같은 파일 안**에 두고 조립했는데, 이번에는 부품을 **파일 하나씩으로 떼어내** `import`로 가져온다. 그리고 지금까지 props는 문자열·배열 같은 "값"만 내려보냈는데, 이번에는 **함수**를 props로 내려보내 자식에서 일어난 클릭을 부모가 받는다. 이 두 가지가 오늘의 핵심이다.

## 1. 배운 내용

### 1-1. 부모 — Component1이 두 부품을 조립한다

```jsx
// src/example/day02/exam1.jsx
import FrontComp from "./FrontComp";
import BackComp from "./BackComp";

function Component1() {
  return (
    <>
      <h2>React-Modules</h2>
      <ol>
        <FrontComp
          onMyEvent1={() => {
            alert("프론트엔드 클릭됨(부모전달");
          }}
        ></FrontComp>
        <BackComp
          onMyEvent2={(msg) => {
            alert(msg);
          }}
        ></BackComp>
      </ol>
    </>
  );
}

export default Component1;
```

| 역할 | 파일 | 하는 일 |
| --- | --- | --- |
| 부모 | `exam1.jsx` → `Component1` | 두 부품을 불러와 `<ol>` 안에 배치하고, 각 부품에 함수 하나씩을 props로 내려준다 |
| 자식 | `FrontComp.jsx` | 프론트엔드 과목 목록을 그린다 |
| 자식 | `BackComp.jsx` | 백엔드 과목 목록을 그리고, 링크를 클릭하면 부모가 준 함수를 호출한다 |

`<h2>React-Modules</h2>`라는 제목 그대로, 컴포넌트를 **모듈** 단위로 나눈 예제다. day01의 헤더·메인·푸터 조립과 구조는 같고, 부품이 다른 파일에 산다는 점만 다르다.

### 1-2. 파일 하나 = 컴포넌트 하나 — export default와 import

```jsx
// FrontComp.jsx (부품 쪽)
export default function FrontComp() { … }

// exam1.jsx (쓰는 쪽)
import FrontComp from "./FrontComp";
```

| 쪽 | 문법 | 의미 |
| --- | --- | --- |
| 내보내기 | `export default 함수` | 이 파일의 대표 하나를 밖으로 낸다 (파일당 `default`는 하나) |
| 가져오기 | `import 이름 from "./파일"` | 상대 경로로 파일을 찾아 대표를 받아온다. `.jsx` 확장자는 Vite가 알아서 붙여 찾는다 |

`default`로 내보낸 것은 가져오는 쪽에서 **이름을 마음대로** 붙여도 된다. 다만 파일명과 컴포넌트 이름을 같게 맞추는 것이 관례다 — `FrontComp.jsx` 안에 `FrontComp`, 가져올 때도 `FrontComp`. 이렇게 맞춰 두면 파일 탐색기와 코드가 1:1로 대응해서 찾기 쉽다.

경로 앞의 `./`는 "지금 이 파일과 같은 폴더"라는 뜻이다. `./`를 빼고 `"FrontComp"`라고만 쓰면 `node_modules` 안의 패키지를 찾으러 가서 못 찾는다. day01에서 `import { useState } from "react"`처럼 `./` 없이 쓴 것은 패키지이기 때문이다.

### 1-3. 함수 표현식으로 쓴 컴포넌트

```jsx
// BackComp.jsx
const BackComp = ({ onMyEvent2 }) => {
  return ( … );
};
export default BackComp;
```

`FrontComp`는 `export default function` 한 줄로 선언하고 내보냈고, `BackComp`는 화살표 함수를 `const`에 담은 뒤 **맨 아래에서 따로** `export default BackComp`를 했다. day01 1-7에서 본 "함수 선언·화살표·함수 표현식 세 표기"가 실제 파일에서 갈린 모양이다. 둘 다 결과는 같다 — 컴포넌트는 JSX를 반환하는 함수이기만 하면 된다.

주석에 정리된 세 줄이 이 차이를 요약한다.

| 형태 | 정의 | 호출 |
| --- | --- | --- |
| `let a;` | 변수 | `a` |
| `function a(){}` | 함수 선언 | `a()` |
| `const a = () => {}` | 화살표 함수를 담은 변수 | `a()` |

화살표 함수는 결국 **함수를 값으로 담은 변수**다. 그래서 `export default BackComp`처럼 변수 이름으로 내보낼 수 있고, 뒤에서 볼 "함수를 props로 넘기기"도 같은 원리로 된다.

### 1-4. 함수를 props로 내려보내기 — 콜백 props

```jsx
// 부모
<BackComp onMyEvent2={(msg) => { alert(msg); }}></BackComp>

// 자식
const BackComp = ({ onMyEvent2 }) => { … onMyEvent2("백엔드 클릭됨(자식전달)"); … }
```

지금까지 props에는 `name="…"`, `data={배열}`처럼 값을 넣었다. 오늘은 `onMyEvent2={함수}`처럼 **함수 자체**를 넣는다. 자식은 구조 분해로 `onMyEvent2`를 꺼내 두었다가 클릭이 일어나면 `onMyEvent2("…")`로 **호출**한다. 그러면 부모가 넘긴 화살표 함수가 실행되고, 인수로 넘긴 문자열이 부모 쪽 `msg`로 들어가 `alert`가 뜬다.

흐름을 순서대로 놓으면 이렇다.

| 단계 | 어디서 | 무엇이 |
| --- | --- | --- |
| ① | 부모 | `onMyEvent2`라는 이름으로 함수 `(msg) => alert(msg)`를 자식에게 준다 |
| ② | 자식 | props에서 `onMyEvent2`를 꺼내 들고만 있는다 (아직 실행 안 함) |
| ③ | 사용자 | `<a>`를 클릭한다 |
| ④ | 자식 | `onMyEvent2("백엔드 클릭됨(자식전달)")` — 부모의 함수를 호출하면서 메시지를 올려보낸다 |
| ⑤ | 부모 | `msg`로 메시지를 받아 `alert` |

**데이터는 부모→자식(props), 이벤트는 자식→부모(콜백 호출).** props는 읽기 전용이라 자식이 부모의 것을 직접 바꿀 수 없는데, 부모가 미리 함수를 쥐여 주면 자식은 그 함수를 부르는 방식으로 "부모에게 알릴" 수 있다. 이 패턴이 React에서 자식 → 부모로 값이 올라가는 **유일한 통로**다.

`onMyEvent1`·`onMyEvent2`는 React가 아는 이름이 아니라 **직접 지은 props 이름**이다. `onClick`처럼 `on`으로 시작하게 지은 것은 "이벤트를 받는 함수"라는 뜻을 이름에 담는 관례를 따른 것이다. `FrontComp`는 `onMyEvent1`을 받아 쓰지 않는데, 부모가 내려준 props를 자식이 꺼내 쓰지 않아도 오류는 나지 않는다 — 그냥 무시된다.

### 1-5. 콜백 함수 — 넘길 때는 호출하지 않는다

주석의 예제가 핵심을 그대로 보여준다.

```js
const plus = (x, y) => { return x + y };
const cal = (x) => { console.log(x(3, 4)) };

cal(plus(3, 5))   // plus를 먼저 실행 → 8이 넘어감 → x(3,4)는 "8(3,4)" 라서 오류
cal(plus)         // plus 함수 자체가 넘어감 → x(3,4) = 7
```

| 표기 | 넘어가는 것 | 결과 |
| --- | --- | --- |
| `cal(plus(3, 5))` | `plus`를 **실행한 결과값** 8 | `cal` 안에서 8을 함수처럼 부르니 오류 |
| `cal(plus)` | `plus` **함수 그 자체** | `cal` 안에서 `x(3, 4)`로 실행되어 7 |

React의 `onClick`도 똑같다.

```jsx
onClick={plus(3, 4)}              // 렌더링 순간 실행돼 7이 들어감 → 클릭과 무관, 오류
onClick={() => plus(3, 4)}        // 함수를 넘김 → 클릭할 때 실행
```

day01 1-10에서 "함수를 넘기고 실행하지 않기"로 본 그 규칙이다. 괄호 `()`가 붙으면 **지금 실행**, 안 붙으면 **나중에 실행할 함수를 건네는 것**. 인수를 넣어서 부르고 싶으면 화살표 함수로 한 번 감싼다.

### 1-6. `<a>`에서 preventDefault — CSR의 깜빡임 막기

```jsx
<a
  href="/"
  onClick={(event) => {
    event.preventDefault();
    onMyEvent2("백엔드 클릭됨(자식전달)");
  }}
></a>
```

`<a href>`는 원래 클릭하면 **HTTP GET으로 페이지를 새로 요청**하는 태그다. 새 페이지를 받아오는 순간 화면이 한 번 비었다가 다시 그려지는 것이 "깜빡임"이다. React는 **CSR(Client Side Rendering)** — 처음 한 번 HTML·JS를 받은 뒤로는 서버에 페이지를 다시 달라고 하지 않고 브라우저 안에서 화면을 바꾼다. 그래서 `<a>`의 기본 동작이 그대로 살아 있으면 React가 만든 화면이 통째로 날아가고 처음부터 다시 로드된다.

`event.preventDefault()`는 이 기본 동작(페이지 이동)을 막는다. 이벤트 핸들러의 첫 매개변수 `event`는 JS DOM 이벤트와 같은 자리이고, DOM 조작에서 `form`의 `submit`을 막을 때 쓰던 것과 같은 메소드다. 링크처럼 보이되 이동은 막고 React 쪽 동작만 하고 싶을 때 이 두 줄이 세트로 들어간다.

| 방식 | 화면 갱신 | 서버 요청 |
| --- | --- | --- |
| 전통 방식 (`<a>` 그대로) | 페이지 통째로 다시 로드 | 이동할 때마다 HTML을 새로 요청 |
| CSR (React) | 바뀐 부분만 다시 그림 | 처음 1번 + 이후엔 데이터(JSON)만 |

### 1-7. props와 구조 분해 — 다시 한 줄로

주석 마지막 두 줄이 오늘의 용어 정리다.

- **props**: 상위 컴포넌트로부터 전달받은 속성들 — 하나의 **객체**다. `{ onMyEvent2: () => {} }` 모양으로 들어온다
- **구조 분해**: 객체 안의 속성을 각각 변수로 분해하는 것. `({ onMyEvent2 }) => …`라고 쓰면 `let onMyEvent2 = props.onMyEvent2`를 한 것과 같다

`BackComp`는 매개변수 자리에서 바로 구조 분해했고, day02 앞 노트의 `Profile`은 `props.name`으로 점 표기를 썼다. 어느 쪽이든 되지만, 받는 props가 2~3개면 구조 분해 쪽이 "이 컴포넌트가 뭘 받는지"를 함수 첫 줄에서 보여줘서 읽기 좋다.

## 2. 추가로 알면 좋은 활용법

### 2-1. 콜백 props 이름 짓기 — on + 동사

```jsx
<TodoItem onDelete={(id) => …} onToggle={(id) => …} />
<SearchBox onSearch={(keyword) => …} />
```

부모가 넘기는 함수 props는 `on무엇`으로, 자식이 그걸 부르는 내부 핸들러는 `handle무엇`으로 짓는 관례가 널리 쓰인다.

```jsx
function TodoItem({ id, onDelete }) {
  const handleClick = () => onDelete(id);   // 내부: handle…
  return <button onClick={handleClick}>삭제</button>;
}
```

`onMyEvent1`처럼 번호를 붙이는 대신 **무슨 일이 일어났는지**를 이름에 담으면, 부모 쪽 코드만 봐도 자식에서 어떤 이벤트가 올라오는지 읽힌다.

### 2-2. 클릭한 항목이 "누구"인지 함께 올려보내기

오늘은 문자열 하나를 올려보냈지만, 실전에서는 **어느 항목**에서 이벤트가 났는지가 필요하다. 앞 노트의 `map` 목록과 합치면 이 모양이 된다.

```jsx
function Practice1() {
  const data = [ /* { id, name, imageUrl } … */ ];
  return data.map((p) => (
    <Profile key={p.id} {...p} onSelect={(id) => alert(`${id}번 선택`)} />
  ));
}

function Profile({ id, name, imageUrl, onSelect }) {
  return (
    <div onClick={() => onSelect(id)}>
      <h3>{name}</h3><img src={imageUrl} alt={name} />
    </div>
  );
}
```

자식은 자기 `id`를 알고 있으니, 콜백을 부를 때 그 `id`를 인수로 실어 보내면 부모는 "몇 번이 클릭됐는지"를 알게 된다. 목록 렌더링(props로 내려감) + 콜백(이벤트로 올라옴)이 합쳐진 이 구조가 게시판·장바구니 같은 목록 화면의 기본 골격이다.

### 2-3. 콜백을 부모의 상태 변경에 연결하기

`alert` 자리에 `useState`의 setter를 두면 "자식 클릭 → 부모 상태 변경 → 화면 갱신"이 완성된다.

```jsx
import { useState } from "react";

function Parent() {
  const [msg, setMsg] = useState("");
  return (
    <>
      <p>{msg}</p>
      <BackComp onMyEvent2={(m) => setMsg(m)} />
    </>
  );
}
```

`alert`는 확인용이고, 실제로는 이렇게 **부모가 가진 상태**를 바꾸는 데 콜백을 쓴다. 상태는 부모에 있고 자식은 그걸 바꿔 달라고 요청만 한다 — 이것이 "상태 끌어올리기(lifting state up)"의 출발점이다.

### 2-4. `<a>` 대신 `<button>` — 이동이 목적이 아니면

이동하지 않을 링크라면 처음부터 `<button type="button">`을 쓰는 편이 단순하다. `preventDefault`가 필요 없고, 키보드 접근성도 버튼 쪽이 맞다. `<a>`를 유지해야 하는 경우(링크 모양이 필요하거나 실제 주소가 있을 때)에만 `preventDefault` 세트를 쓴다.

```jsx
<button type="button" onClick={() => onMyEvent2("백엔드 클릭됨")}>백엔드</button>
```

React 앱 안에서 페이지처럼 이동하고 싶으면 `<a>`가 아니라 **React Router의 `<Link>`**를 쓴다 — 주소창은 바뀌지만 페이지를 다시 로드하지 않는다(3-1).

### 2-5. 폴더로 묶기 — 부품이 늘어날 때

파일이 늘면 `components/` 폴더에 부품을 모으고, 화면 단위는 `pages/`에 두는 식으로 나눈다.

```
src/
├── components/   FrontComp.jsx, BackComp.jsx, Profile.jsx …
├── pages/        Home.jsx, Board.jsx …
└── App.jsx
```

가져올 때는 `import FrontComp from "./components/FrontComp"`처럼 경로만 길어진다. 컴포넌트 하나에 파일 하나, 파일명 = 컴포넌트명 원칙은 그대로다.

## 3. 더 나아가 알면 좋은 것

### 3-1. SPA와 React Router

오늘의 "`<a>`는 깜빡인다"가 곧 **SPA(Single Page Application)** 얘기다. React 앱은 HTML 한 장으로 시작해서 화면 전환을 전부 JS가 처리한다. 주소창의 경로에 따라 다른 컴포넌트를 보여주는 일은 **React Router**(`react-router-dom`)가 맡는다 — `<Link to="/board">`는 `<a>`처럼 보이지만 페이지 로드 없이 컴포넌트만 바꾼다. `preventDefault`를 손으로 쓰던 자리가 라이브러리로 대체되는 셈이다.

### 3-2. 콜백이 깊어질 때 — Context와 상태 관리

부모 → 자식 → 손자로 콜백을 계속 내려보내야 하면 중간 컴포넌트가 쓰지도 않는 props를 전달만 하게 된다(props drilling). 이때는 `useContext`로 트리 어디서든 꺼내 쓰거나, Redux·Zustand 같은 상태 관리 라이브러리로 상태와 함수를 한 곳에 모은다. 오늘의 콜백 props는 그 첫 단계이고, 2~3단 이내면 콜백 props가 가장 단순하다.

### 3-3. 다음에 볼 키워드

- `useState` + 콜백 props — 자식 이벤트로 부모 상태 바꾸기, 상태 끌어올리기
- `named export`(`export function A`)와 `default export`의 차이, 한 파일에서 여러 개 내보내기
- React Router — `<Link>`, `<Route>`, `useNavigate`
- 합성 이벤트(SyntheticEvent) — React의 `event`가 DOM 이벤트와 같은 점·다른 점
- `useCallback` — 자식에게 넘기는 함수를 매 렌더링마다 새로 만들지 않기

## 실습 파일

- `KDT_2026/2026_React/src/example/day02/exam1.jsx` — `FrontComp`·`BackComp`를 `import`해 조립하는 부모 `Component1`, 콜백 props `onMyEvent1`·`onMyEvent2`
- `KDT_2026/2026_React/src/example/day02/FrontComp.jsx` — 프론트엔드 과목 목록 부품, `export default function` 표기
- `KDT_2026/2026_React/src/example/day02/BackComp.jsx` — 구조 분해로 콜백을 받아 `<a>` 클릭 시 호출, `preventDefault`, 콜백·CSR·props·구조 분해 정리 주석

## 관련 노트

[[React MOC]] · [[React day02 객체 배열과 map 렌더링]] · [[React day02 useState와 상태 갱신]] · [[KDT_2026 학습 지도]]
