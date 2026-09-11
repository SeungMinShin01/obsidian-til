---
출처: Claude 분석
원본: KDT_2026/2026_React/src
작성일: 2026-09-11
tags: [학습, react]
---

# React day01 — 컴포넌트와 렌더링

> 실습 파일: `index.html`, `src/main.jsx`, `src/example/day01/exam1.jsx` ~ `exam3.jsx`, `package.json`
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

### 2-3. props로 값 넘기기 (다음에 바로 쓰게 될 것)

```jsx
// 부모
<Greeting name="홍길동" />

// 자식
export default function Greeting(props) {
  return <p>안녕, {props.name}</p>;
}
```

JSX 안에서 `{}`는 JS 표현식을 끼워 넣는 자리다. 오늘 `props`를 받아만 두었는데, 이렇게 태그의 속성으로 넘긴 값이 `props` 객체에 담겨 온다. JS day10 함수의 매개변수 개념이 그대로다.

### 2-4. 컴포넌트 안의 JS 변수 쓰기

```jsx
export default function Today() {
  const now = new Date().toLocaleDateString();
  return <p>오늘은 {now}</p>;
}
```

`return` 위쪽은 평범한 JS 자리라 변수 선언·계산을 마음껏 한다. `return` 안 `{}`에서 그 값을 꺼내 쓴다. 문자열 붙이기(`"오늘은 " + now`) 대신 이 방식이 React의 표준 표기다.

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

- `props` 전달과 구조 분해 `function Comp({ name })`
- `useState` — 상태와 재렌더링
- 조건부 렌더링(`&&`, 삼항), 목록 렌더링(`map` + `key`)
- 이벤트 핸들러 `onClick`·`onChange`, 제어 컴포넌트(input)
- `useEffect` — 화면 그린 뒤 실행할 일(fetch 등)
- React 19의 React Compiler(`babel-plugin-react-compiler`가 devDependencies에 이미 있다)
- Vite의 HMR, `import.meta.env`

## 실습 파일

- `KDT_2026/2026_React/index.html`
- `KDT_2026/2026_React/src/main.jsx`
- `KDT_2026/2026_React/src/example/day01/exam1.jsx`
- `KDT_2026/2026_React/src/example/day01/exam2.jsx` — 헤더·메인·푸터 조립
- `KDT_2026/2026_React/src/example/day01/exam3.jsx` — 함수 표기 세 가지, 목록·폼 컴포넌트
- `KDT_2026/2026_React/src/App.jsx` (Vite 기본 생성 — 참고용)
- `KDT_2026/2026_React/package.json`

## 관련 노트

[[React MOC]] · [[KDT_2026 학습 지도]]
