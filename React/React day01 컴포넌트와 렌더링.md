---
출처: Claude 분석
원본: KDT_2026/2026_React/src
작성일: 2026-09-11
tags: [학습, react]
---

# React day01 — 컴포넌트와 렌더링

> 실습 파일: `index.html`, `src/main.jsx`, `src/example/day01/exam1.jsx` ~ `exam5.jsx`, `package.json`
> 허브: [[React MOC]] · 이전: (없음 — React 첫 노트, 선행 흐름은 JS day14 게시판 CRUD) · 다음: (예정)

React 수업의 첫날이다. 2026_FE에서 하던 순수 JS·DOM 조작과 달리, 새 저장소 `2026_React`는 **Vite로 만든 프로젝트**이고 화면을 "컴포넌트"라는 함수 단위로 그린다. 오늘은 프로젝트가 어떻게 켜지는지(진입점)와 컴포넌트를 하나 만들어 화면에 띄우는 최소 흐름까지 다뤘다.

## 1. 배운 내용

### 1-1. 프로젝트 구조 — Vite + React

`package.json`을 보면 이 프로젝트가 무엇으로 굴러가는지 보인다.

| 항목 | 내용 |
| --- | --- |
| `"type": "module"` | 파일 전체를 ES 모듈로 취급 — `import`/`export`를 그대로 쓴다 |
| `dependencies` | `react`, `react-dom` — 런타임에 실제로 필요한 두 패키지 |
| `devDependencies` | `vite`, `@vitejs/plugin-react`, `eslint` 계열 — 개발·빌드 도구 |
| `scripts.dev` | `vite` — 개발 서버 실행 (`npm run dev`) |
| `scripts.build` | `vite build` — 배포용 정적 파일 생성 |

`react`는 컴포넌트·상태 같은 **핵심 개념**을 담고, `react-dom`은 그 결과를 **브라우저 DOM에 실제로 그리는** 쪽이다. 둘이 분리된 이유는 React 자체는 브라우저 전용이 아니기 때문이다(네이티브 앱 등 다른 렌더러가 있다).

### 1-2. 진입점 — index.html → main.jsx

```html
<!-- index.html -->
<body>
  <div id="root"></div>
  <script type="module" src="/src/main.jsx"></script>
</body>
```

HTML은 이것뿐이다. 빈 `#root` 하나와 모듈 스크립트 하나. 화면은 전부 JS가 만든다. 2026_FE 때처럼 HTML에 마크업을 직접 쓰는 방식과 가장 크게 갈리는 지점이다.

```jsx
// src/main.jsx
// [필수] 1. 리액트 라이브러리 최초 렌더링(그리기) 하는 함수
import { createRoot } from "react-dom/client";
// [필수] 2. index.html 에서 root 마크업 가져오기
const root = document.querySelector("#root");
// [필수] 3. 가져온 root 마크업을 createRoot 함수에 넣어서 렌더러 만들기
const create = createRoot(root);
// [선택] 최초로 화면을 그릴 컴포넌트 가져와서 렌더링
import App from "./App.jsx";
create.render(<App> </App>);
```

정리하면 렌더링은 세 단계다.

| 단계 | 코드 | 의미 |
| --- | --- | --- |
| ① 렌더 함수 가져오기 | `import { createRoot } from "react-dom/client"` | React 18 이후의 진입 API |
| ② 붙일 자리 찾기 | `document.querySelector("#root")` | JS day11 DOM 조작에서 쓰던 그 함수 그대로 |
| ③ 루트 만들고 그리기 | `createRoot(root).render(<App />)` | 이 자리 아래는 React가 관리한다 |

`createRoot`는 한 번만 만들고, 그 루트의 `render()`를 부르면 화면이 바뀐다. 같은 루트에 `render()`를 두 번 부르면 **마지막 것으로 교체**된다 — 실습 파일에서 `App`을 그린 뒤 `MyMarkUp`을 다시 그리면 `MyMarkUp`만 남는 이유가 이것이다.

### 1-3. 컴포넌트 — 마크업을 반환하는 함수

```jsx
// src/example/day01/exam1.jsx
function ComponentName(props) {
  return;
}

export default function MyMarkUp(props) {
  return <div> 내가 만든 마크업/컴포넌트 </div>;
}
```

핵심은 이것이다. **컴포넌트 = 마크업(JSX)을 `return`하는 함수.** 함수 이름이 곧 태그 이름이 된다.

| 규칙 | 설명 |
| --- | --- |
| 이름은 **대문자**로 시작 | `MyMarkUp` — 소문자면 React가 일반 HTML 태그(`<div>`)로 본다 |
| 매개변수 `props` | 부모가 넘겨주는 값 묶음(객체). 오늘은 받기만 하고 안 썼다 |
| `return` 안에 JSX | HTML처럼 생겼지만 JS 표현식이다 |
| `export default` | 파일 하나당 대표 컴포넌트 하나를 내보내는 관용 |

`return;`만 있는 빈 함수도 문법상 컴포넌트다(아무것도 안 그림). 뼈대를 먼저 잡고 안을 채우는 순서로 보면 된다.

### 1-4. 컴포넌트를 화면에 올리기

```jsx
// main.jsx
import MyMarkUp from "./example/day01/exam1.jsx";
create.render(<MyMarkUp></MyMarkUp>);
```

만든 컴포넌트를 `import`하고, **함수 호출이 아니라 태그로** 쓴다. `MyMarkUp()`이 아니라 `<MyMarkUp />`. 이 태그를 `render()`에 넘기면 React가 함수를 대신 호출해서 나온 마크업을 `#root` 안에 그린다.

`<MyMarkUp></MyMarkUp>`과 `<MyMarkUp />`은 같다. 자식이 없으면 자기 닫힘 태그가 짧다.

### 1-5. JSX — HTML처럼 보이는 JS

`.jsx` 확장자 파일에서는 JS 안에 `<div>…</div>`를 그냥 쓸 수 있다. 브라우저가 이걸 아는 게 아니라 **Vite(Babel 플러그인)가 빌드 시점에 `React.createElement(...)` 호출로 바꿔 준다.** 그래서 `.jsx`는 HTML이 아니라 끝까지 JS다.

HTML과 다른 점은 다음 수업부터 계속 마주친다.

| HTML | JSX | 이유 |
| --- | --- | --- |
| `class="hero"` | `className="hero"` | `class`는 JS 예약어 |
| `onclick="fn()"` | `onClick={fn}` | 문자열이 아니라 함수 자체를 넘김 |
| `<img>` | `<img />` | 모든 태그는 닫아야 한다 |
| 여러 태그 나열 | `<>…</>`로 감쌈 | 컴포넌트는 루트 하나만 반환 |

기본 생성된 `App.jsx`에 이 네 가지가 전부 들어 있다(`className`, `onClick={() => …}`, `<img … />`, `<>…</>`).

### 1-6. 컴포넌트 안에 컴포넌트 — 한 파일에서 조립하기

```jsx
// src/example/day01/exam2.jsx
export default function Component1(props) {
  return (
    <>
      <Header></Header>
      <div> 메인페이지 </div>
      <Footer></Footer>
    </>
  );
}
function Header(props) { return <div> 헤더구역 </div>; }
function Footer(props) { return <div> 푸터구역 </div>; }
```

컴포넌트는 다른 컴포넌트를 태그로 품을 수 있다. 헤더·메인·푸터 세 덩어리를 각각 함수로 만들고, 대표 컴포넌트 `Component1`이 그 셋을 `<>…</>` 안에 나열해 한 화면으로 조립한다. 파일을 만드는 순서로 정리하면 이렇다.

| 순서 | 할 일 | 비고 |
| --- | --- | --- |
| ① | `컴포넌트명.jsx` 파일 생성 | 파일 하나 = 화면 조각 하나 |
| ② | `export default function 컴포넌트명(props) { }` | 다른 파일에서 `import`하려면 `export default` 필요 |
| ③ | `return` 안에 JSX, 두 줄 이상이면 `<>…</>`로 묶기 | `return` 밖은 그냥 JS |

`Header`·`Footer`에는 `export`가 없다. **이 파일 안에서만 쓰는 부품이면 내보내지 않아도 된다.** 바깥으로 나가는 건 `export default` 하나뿐이고, 그 하나가 `main.jsx`에서 `<Component1 />`로 그려진다. 함수 선언은 호이스팅되므로 `Component1`이 위에 있고 `Header`가 아래에 있어도 문제없다.

### 1-7. 컴포넌트를 정의하는 세 가지 함수 표기

```jsx
// src/example/day01/exam3.jsx
function FrontComp() { return ( <> <li>프론트엔드</li> <ul>…</ul> </> ); }   // 함수 선언
const BackComp = () => { return ( <> <li>백엔드</li> <ul>…</ul> </> ); };     // 화살표 함수
let FormComp = function () { return ( <> <form>…</form> </> ); };            // 함수 표현식

function Component2() {
  return (
    <>
      <div>
        <h2>React - Component</h2>
        <ol>
          <FrontComp></FrontComp>
          <BackComp />
        </ol>
        <FormComp />
      </div>
    </>
  );
}
export default Component2;
```

컴포넌트는 "JSX를 반환하는 함수"이기만 하면 되므로, JS day10 함수에서 본 세 가지 표기가 전부 통한다.

| 표기 | 형태 | 특징 |
| --- | --- | --- |
| 함수 선언 | `function A() {}` | 호이스팅됨 — 순서 신경 안 써도 됨 |
| 화살표 함수 | `const A = () => {}` | 요즘 가장 흔한 표기. `const`라 재할당 불가 |
| 함수 표현식 | `let A = function () {}` | 화살표 이전 방식. 잘 안 쓰지만 같은 것 |

어느 쪽이든 **이름이 대문자**여야 태그로 쓸 수 있다는 규칙은 같다. `export default`도 함수 선언에 바로 붙이든(`exam2`), 맨 아래에 `export default Component2;`로 따로 쓰든(`exam3`) 결과는 같다.

여기서 하나 더 보이는 것 — `<ol>` 안에 `<FrontComp>`·`<BackComp>`를 넣었는데 각 컴포넌트가 `<li>`로 시작하는 조각을 반환한다. `<>…</>`는 실제 DOM에 아무 태그도 남기지 않으므로, 결과 HTML은 `<ol><li>…</li><ul>…</ul><li>…</li><ul>…</ul></ol>`처럼 조각들이 부모 안에 그대로 펼쳐진다. 조각(Fragment)이 "포장 없이 묶는다"는 뜻이 이것이다.

### 1-8. props — 부모가 자식에게 넘기는 객체

```jsx
// src/example/day01/exam4.jsx
/*
    변수: 하나의 값을 저장하는 수
    매개변수: 함수/메소드에서 (인수)를 받아서 함수 안에서 사용하는 변수
    인수/인자값: 함수가 실행될 때 함수에게 전달하는 값
*/
function plus(x, y) {} // 함수 정의 — x, y 매개변수
plus(3, 4);            // 함수 호출 — 3, 4 인수
```

props에 들어가기 전에 용어부터 다시 잡았다. **매개변수**는 함수가 받는 자리 이름(`x`, `y`), **인수**는 부를 때 실제로 넣는 값(`3`, `4`)이다. `plus(3, 4)`는 3을 `x`에, 4를 `y`에 대입하는 것이다. 이 구분이 되어야 props가 무엇인지 한 줄로 설명된다.

> **props = 상위 컴포넌트가 하위 컴포넌트에게 전달하는 객체. 읽기 전용.**

일반 함수에 빗대면 `plus2({ v1: 3, v2: 4 })`처럼 **값 여러 개를 객체 하나에 담아 매개변수 하나로 넘기는 것**과 같다. 컴포넌트 함수의 매개변수 `props`가 그 객체를 받는 자리다.

```jsx
export default function Component3(props) {
  let name = "유재석";
  // --- return 부터 JSX 문법 구역, 주석: { /* 주석 */ }
  return (
    <>
      {/* JSX 주석 */}
      <div>{name} </div>
      <input type="text" value="안녕" name="입력상자" />
      <SubComp1 name="유재석" age="40" />
    </>
  );
}

function SubComp1(props) {
  console.log(props); // { name: "유재석", age: "40" }
  return (
    <>
      <h4>{props.name}</h4>
      <h4>{props.age}</h4>
    </>
  );
}
```

흐름을 표로 정리하면 이렇다.

| 위치 | 코드 | 의미 |
| --- | --- | --- |
| 부모 (인수) | `<SubComp1 name="유재석" age="40" />` | 태그의 속성이 곧 넘기는 값. 함수 호출로 치면 `SubComp1({ name: "유재석", age: "40" })` |
| 자식 (매개변수) | `function SubComp1(props)` | 속성들이 **객체 하나**로 묶여 `props`에 들어온다 |
| 자식 (사용) | `{props.name}` | JSX 안 `{}`에서 객체 프로퍼티로 꺼내 쓴다 |

`console.log(props)`를 찍어 보면 `{ name: "유재석", age: "40" }`이 나온다. 속성 이름이 그대로 키가 되고, 값은 **문자열**로 들어온다 — `age="40"`은 숫자 40이 아니라 `"40"`이다. 숫자로 넘기고 싶으면 `age={40}`처럼 중괄호를 써야 한다.

읽기 전용이라는 점이 중요하다. 자식 안에서 `props.name = "다른 이름"`처럼 고쳐 쓰지 않는다. 값을 바꾸는 주체는 항상 그 값을 넘겨준 부모다.

#### 함께 나온 JSX 표기 두 가지

| 표기 | 예 | 설명 |
| --- | --- | --- |
| JSX 주석 | `{/* 주석 */}` | `return` 안에서는 `//`·`/* */`를 그냥 못 쓴다. 중괄호로 JS 구역을 열고 그 안에 블록 주석을 넣는다 |
| 변수 끼워 넣기 | `<div>{name}</div>` | `return` 위에서 선언한 JS 변수를 `{}`로 꺼내 쓴다 (2-4와 같은 이야기) |

`return (` 을 기준으로 위는 평범한 JS 구역, 아래는 JSX 구역이다. 주석 표기가 달라지는 것도 이 경계 때문이다.

#### 구조 분해로 받기

```jsx
function SubComp2({ name, age }) {
  return (
    <>
      <h4>{name}님 {age}세</h4>
    </>
  );
}
```

`props`를 통째로 받아 `props.name`으로 꺼내는 대신, 매개변수 자리에서 **객체 구조 분해**로 필요한 키만 바로 뽑을 수 있다. `{ name, age }`는 `const { name, age } = props;`를 매개변수 자리에서 한 것과 같다. 본문에서 `props.`를 반복하지 않아도 되어 실무에서는 이쪽이 더 흔하다. 오늘 실습 파일에는 정의만 있고 부모에서 태그로 부르지는 않았지만, `<SubComp2 name="유재석" age="40" />`로 부르면 `SubComp1`과 같은 결과가 나온다.

`main.jsx`에서는 `import Component3 from "./example/day01/exam4.jsx"; create.render(<Component3 />);`로 이 컴포넌트를 그린다. 앞선 `exam1`·`exam2`의 렌더링 줄은 주석 처리되어 있다 — 같은 루트에 `render()`를 여러 번 부르면 마지막 것만 남는다는 1-2의 규칙 때문에, 실습마다 하나만 살려 두는 방식이다.

### 1-9. props로 배열 넘기고 목록으로 찍기

```jsx
// src/example/day01/exam5.jsx
function FrontComp(props) {
  const liRows = []; // 배열
  for (let i = 0; i < props.propData1.length; i++) {
    // 부모로부터 전달받은 props 내 propData1 반복
    liRows.push(<li key={i}>{props.propData1[i]} </li>);
  }
  return (
    <>
      <li>{props.frTitle}</li> <ul> {liRows} </ul>
    </>
  );
}

// 원래 props 객체인데 구조 분해하여 propData2 변수와 baTitle 변수로 각각 저장
function BackComp({ propData2, baTitle }) {
  const liRows = [];
  for (let i = 0; i < propData2.length; i++) {
    liRows.push(<li key={i}>{propData2[i]} </li>);
  }
  return (
    <>
      <li>{baTitle}</li> <ul> {liRows} </ul>
    </>
  );
}

export default function Component4(props) {
  // *추후에 연동할 백엔드와 통신 AXIOS*
  const frontData = ["HTML5", "CSS3", "Javascript", "jQuery", "React"];
  const backData = ["Java", "Oracle", "JSP", "Spring Boot"];
  return (
    <>
      <div>
        <h2> 리액트 프롭스 </h2>
        <ol>
          <FrontComp propData1={frontData} frTitle="프론트엔드" />
          <BackComp propData2={backData} baTitle="벡엔드" />
        </ol>
      </div>
    </>
  );
}
```

1-7의 `FrontComp`·`BackComp`는 `<li>`를 하드코딩했는데, 여기서는 **부모가 배열을 props로 내려주고 자식이 반복문으로 `<li>`를 만든다.** 데이터와 화면이 분리되는 첫 장면이다. 주석에 적힌 대로 나중에는 이 배열 자리에 백엔드에서 AXIOS로 받아온 응답이 들어간다.

| 위치 | 코드 | 의미 |
| --- | --- | --- |
| 부모 | `propData1={frontData}` | 배열은 문자열이 아니므로 **중괄호**로 넘긴다 (2-3의 규칙 그대로) |
| 자식 | `const liRows = []; … liRows.push(<li>…</li>)` | JSX 조각도 JS 값이라 배열에 담을 수 있다 |
| 자식 | `<ul> {liRows} </ul>` | `{}` 안에 **배열**을 두면 요소가 순서대로 펼쳐진다 |
| 자식 | `key={i}` | 배열로 찍는 항목마다 붙이는 식별자. 없으면 콘솔 경고 |

같은 일을 두 가지 방식으로 짰다. `FrontComp`는 `props`를 통째로 받아 `props.propData1`로 꺼내고, `BackComp`는 매개변수 자리에서 `{ propData2, baTitle }`로 구조 분해한다. 1-8의 `SubComp1`·`SubComp2` 대비를 배열 props에서 한 번 더 반복한 것이다. 결과는 같고, 본문에서 `props.`가 사라지는 구조 분해 쪽이 읽기 편하다.

`key`는 반복으로 찍은 형제 요소들 사이에서 React가 "어느 게 어느 것"인지 알아보는 표식이다. 지금은 인덱스 `i`를 썼지만, 항목이 중간에 추가·삭제되는 목록이라면 인덱스가 밀려서 엉킨다 — 그런 경우는 데이터 자체의 고유값(id)을 쓰는 편이 안전하다. 오늘처럼 고정 배열이면 인덱스로 충분하다.

### 1-10. 이벤트 — onclick이 아니라 onClick={함수}

```jsx
// src/example/day01/exam5.jsx
export default function Component5(props) {
  function event1() { alert("이벤트발생"); }
  const event2 = function () { alert("이벤트발생2"); };
  const event3 = () => { alert("이벤트발생3"); };

  // onclick = "함수명()" --리액트 방법--> onClick = {함수명}
  // 1. c -> C   2. 함수 실행 X
  return (
    <>
      <button onClick={event1}>이벤트1</button>
      <button onClick={event2}>이벤트2</button>
      <button onClick={event3}>이벤트3</button>
      <button onClick={() => { alert("이벤트발생4"); }}>이벤트4</button>
    </>
  );
}
```

1-5의 표에서 한 줄로 지나갔던 `onclick` → `onClick` 차이를 실제로 써 봤다. 주석의 두 규칙이 전부다.

| 규칙 | HTML | JSX | 이유 |
| --- | --- | --- | --- |
| ① 카멜케이스 | `onclick` | `onClick` | JSX 속성은 JS 프로퍼티 이름을 따른다 (`onChange`, `onSubmit`, `onKeyDown` 모두 같은 식) |
| ② 함수를 **넘긴다** | `onclick="event1()"` | `onClick={event1}` | 문자열이 아니라 함수 자체를 넘긴다. `onClick={event1()}`이라고 쓰면 렌더링 시점에 바로 실행되고 그 반환값(`undefined`)이 핸들러로 들어가 버린다 |

핸들러는 컴포넌트 함수 **안에서** 정의한다. 1-7의 세 가지 함수 표기(선언·표현식·화살표)가 여기서도 그대로 통하고, 네 번째 버튼처럼 `onClick={() => …}` 인라인 화살표로 그 자리에서 바로 써도 된다. 한 줄짜리면 인라인, 재사용하거나 길어지면 이름 있는 함수로 빼는 정도로 나누면 된다.

`return` 위에서 함수를 정의한다는 건, 이 함수들이 **컴포넌트가 그려질 때마다 새로 만들어진다**는 뜻이다. 지금은 신경 쓸 일이 없지만, 상태(state)를 배우고 나면 이 사실이 왜 중요한지 다시 만난다.

## 2. 추가로 알면 좋은 활용법

### 2-1. 실행 명령 세 개

```bash
npm install     # package.json의 의존성 설치 (node_modules 생성)
npm run dev     # 개발 서버 — 저장하면 브라우저가 즉시 갱신(HMR)
npm run build   # dist/ 에 배포용 파일 생성
```

`node_modules`는 git에 올리지 않고 `package.json`만 올린다. 받는 쪽은 `npm install`로 복원한다. `.gitignore`에 이미 들어 있다.

### 2-2. 컴포넌트 파일을 나누는 관용

```
src/
├── main.jsx          진입점 — createRoot·render만
├── App.jsx           최상위 컴포넌트
└── example/day01/    수업별 컴포넌트
```

`main.jsx`에는 렌더링 코드만 두고, 화면 내용은 전부 컴포넌트 파일로 뺀다. 컴포넌트 하나 = 파일 하나 = `export default` 하나가 기본 단위다.

파일 안의 작은 부품(`Header`·`Footer` 같은)이 다른 화면에서도 필요해지면 그때 파일을 분리하고 `export`를 붙인다. 하나의 파일에서 여러 개를 내보낼 때는 이름 내보내기를 쓴다.

```jsx
// components/Layout.jsx
export function Header() { return <header>…</header>; }
export function Footer() { return <footer>…</footer>; }

// 가져오는 쪽 — 중괄호로 이름을 골라 받는다
import { Header, Footer } from "./components/Layout.jsx";
```

`export default`는 파일당 하나, 가져올 때 이름을 마음대로 붙일 수 있다. `export`(이름 내보내기)는 여러 개 가능하고, 가져올 때 `{ }` 안에 원래 이름을 써야 한다.

### 2-2-1. 부모 컴포넌트에서 자식 부품 나열하기

`exam2`·`exam3` 패턴을 실제 페이지에 적용하면 이런 모양이 된다.

```jsx
export default function Page() {
  return (
    <>
      <Header />
      <main>
        <Nav />
        <Content />
      </main>
      <Footer />
    </>
  );
}
```

부모는 "무엇을 어디에 놓을지"만 정하고, 각 부품의 내용은 자기 함수 안에서 책임진다. 이 분리가 나중에 파일이 수십 개로 늘어도 구조를 읽을 수 있게 해 준다.

### 2-3. props를 실전에서 쓰는 관용

1-8의 `SubComp1`·`SubComp2`를 실제 화면에 적용할 때 자주 붙는 표기 몇 가지다.

```jsx
// 숫자·불리언·배열·함수는 중괄호로 넘긴다 (따옴표는 전부 문자열)
<Profile name="유재석" age={40} isAdmin={true} hobbies={["축구", "요리"]} />

// 기본값 — 부모가 안 넘기면 이 값을 쓴다
function Profile({ name, age = 0, isAdmin = false }) { … }

// 목록 데이터를 props로 흘려 보내기
const users = [{ id: 1, name: "유재석" }, { id: 2, name: "강호동" }];
<ul>
  {users.map((u) => <UserItem key={u.id} name={u.name} />)}
</ul>
```

| 관용 | 설명 |
| --- | --- |
| `age={40}` | 문자열이 아닌 값은 반드시 `{}`. `age="40"`이면 `"40"` 문자열이 온다 |
| 기본값 | 구조 분해 자리에서 `= 값`으로 둔다. 없는 키를 `undefined`로 받는 사고를 막는다 |
| `key` | 배열을 돌려 컴포넌트를 여러 개 찍을 때 React가 각 항목을 구분하는 표식. props처럼 보이지만 자식 `props`에는 들어오지 않는다 |
| `children` | 태그 사이에 넣은 내용(`<Card>본문</Card>`)이 `props.children`으로 들어온다. 레이아웃 컴포넌트를 만들 때 쓴다 |

props는 부모→자식 한 방향으로만 흐른다. 자식이 부모 값을 바꾸고 싶으면 부모가 **함수를 props로 내려주고** 자식이 그 함수를 부르는 식으로 돌아간다(`onChange={handler}`). 이 패턴은 상태(state)를 배운 뒤에 다시 만난다.

### 2-4. 컴포넌트 안의 JS 변수 쓰기

```jsx
export default function Today() {
  const now = new Date().toLocaleDateString();
  return <p>오늘은 {now}</p>;
}
```

`return` 위쪽은 평범한 JS 자리라 변수 선언·계산을 마음껏 한다. `return` 안 `{}`에서 그 값을 꺼내 쓴다. 문자열 붙이기(`"오늘은 " + now`) 대신 이 방식이 React의 표준 표기다.

### 2-5. for + push 대신 map

1-9의 `for` + `liRows.push(...)`는 배열을 만드는 과정을 눈으로 따라가기 좋은 방식이다. 실무 코드에서는 같은 일을 `map` 한 줄로 쓴다.

```jsx
function BackComp({ propData2, baTitle }) {
  return (
    <>
      <li>{baTitle}</li>
      <ul>
        {propData2.map((item, i) => <li key={i}>{item}</li>)}
      </ul>
    </>
  );
}
```

`map`은 배열의 각 값을 다른 값으로 바꾼 **새 배열**을 돌려준다. 문자열 배열 → `<li>` 배열로 바꾸는 일이 정확히 그것이라, 임시 변수 없이 `{}` 안에 바로 둘 수 있다. 결과는 1-9와 같다. `for`로 먼저 익히고 `map`으로 줄이는 순서가 자연스럽다.

### 2-6. 핸들러에 값 넘기기와 이벤트 객체

1-10에서 `onClick={event1()}`이 안 되는 이유를 봤다. 그럼 핸들러에 인수를 주고 싶을 때는 어떻게 하는가 — 화살표 함수로 한 번 감싼다.

```jsx
function remove(id) { alert(id + "번 삭제"); }

<button onClick={() => remove(3)}>삭제</button>   // 클릭 시에만 remove(3) 실행

// 이벤트 객체는 첫 번째 인수로 자동 전달된다
<input onChange={(e) => console.log(e.target.value)} />
<form onSubmit={(e) => { e.preventDefault(); /* … */ }}>
```

| 상황 | 표기 |
| --- | --- |
| 인수 없이 그냥 실행 | `onClick={handler}` |
| 인수를 주고 싶다 | `onClick={() => handler(값)}` |
| 이벤트 객체가 필요하다 | `onClick={(e) => …}` — `e.target`, `e.preventDefault()` |

`e.preventDefault()`는 JS day14 게시판 CRUD에서 폼 새로고침을 막던 그 함수다. React에서도 폼을 다룰 때 같은 자리에서 같은 역할을 한다.

## 3. 더 나아가 알면 좋은 것

### 3-1. render()를 다시 부르지 않는다 — 상태(state)

오늘은 `render()`를 두 번 불러 화면을 바꿨지만, 실제 React에서는 그렇게 하지 않는다. `App.jsx`의 카운터가 그 답이다.

```jsx
const [count, setCount] = useState(0);
<button onClick={() => setCount((count) => count + 1)}>Count is {count}</button>
```

`useState`로 값을 두고 `setCount`로 바꾸면 **React가 알아서 그 컴포넌트를 다시 그린다.** DOM을 직접 만지던 JS day11 DOM 조작의 `innerHTML = …` 방식이 "데이터를 바꾸면 화면이 따라온다"로 뒤집히는 지점이다. 이게 React를 쓰는 이유의 절반이다.

### 3-2. 선언형 vs 명령형

| 2026_FE 방식 (명령형) | React 방식 (선언형) |
| --- | --- |
| "이 요소를 찾아서 텍스트를 이걸로 바꿔라" | "데이터가 이럴 때 화면은 이렇게 생겼다" |
| `document.querySelector(...).innerHTML = ...` | `return <p>{value}</p>` |
| 바뀔 때마다 어디를 고칠지 직접 추적 | 데이터만 바꾸면 React가 차이를 계산해 반영 |

JS day14 게시판 CRUD에서 `list()` 함수가 매번 `innerHTML`을 통째로 다시 만들던 것을 떠올리면, React는 그 "다시 만들기"를 라이브러리가 대신하되 **바뀐 부분만** 갈아 끼운다(가상 DOM·재조정).

### 3-3. 다음에 볼 키워드

- `props.children`, `PropTypes`/TypeScript로 props 타입 잡기
- `useState` — 상태와 재렌더링, 자식→부모로 값을 올리는 콜백 props
- 조건부 렌더링(`&&`, 삼항), 목록 렌더링(`map` + `key`)
- `onChange`와 제어 컴포넌트(input) — `onClick`(1-10)의 다음 단계, 입력값을 state로 묶기
- `useEffect` — 화면 그린 뒤 실행할 일(fetch 등)
- React 19의 React Compiler(`babel-plugin-react-compiler`가 devDependencies에 이미 있다)
- Vite의 HMR, `import.meta.env`

## 실습 파일

- `KDT_2026/2026_React/index.html`
- `KDT_2026/2026_React/src/main.jsx`
- `KDT_2026/2026_React/src/example/day01/exam1.jsx`
- `KDT_2026/2026_React/src/example/day01/exam2.jsx` — 헤더·메인·푸터 조립
- `KDT_2026/2026_React/src/example/day01/exam3.jsx` — 함수 표기 세 가지, 목록·폼 컴포넌트
- `KDT_2026/2026_React/src/example/day01/exam4.jsx` — 매개변수·인수 용어, props 전달과 구조 분해, JSX 주석
- `KDT_2026/2026_React/src/example/day01/exam5.jsx` — 배열 props를 반복문으로 목록 렌더링(`key`), `onClick={함수}` 이벤트 핸들러 네 가지 표기
- `KDT_2026/2026_React/src/App.jsx` (Vite 기본 생성 — 참고용)
- `KDT_2026/2026_React/package.json`

## 관련 노트

[[React MOC]] · [[KDT_2026 학습 지도]]
