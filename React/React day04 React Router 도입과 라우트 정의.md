---
출처: Claude 분석
원본: KDT_2026/2026_React/src/example/day04
작성일: 2026-09-16
tags: [학습, react]
---

# React day04 — React Router 도입과 라우트 정의

> 실습 파일: `src/example/day04/exam1.jsx` · `src/example/day04/App.jsx` · `src/example/day04/Home.jsx` · `src/example/day04/LayoutIndex.jsx` · `src/example/day04/NotFound.jsx` · `src/example/day04/TopNavi.jsx` · `src/example/day04/RouterHooks.jsx` · `src/example/day04/CommonLayout.jsx` · `src/example/day04/practice/*` · `src/main.jsx` · `package.json`
> 허브: [[React MOC]] · 이전: [[React day03 전화번호부 실습 배열 상태 추가와 삭제]] · 다음: (예정)

day04는 **React Router**를 처음 붙이는 날이다. 지금까지는 `main.jsx`에서 컴포넌트 하나를 골라 `render`하는 식으로 화면을 바꿨는데, 실제 사이트는 주소창의 경로(`/`, `/board`, `/login` …)에 따라 다른 화면이 나와야 한다. 이 "경로 → 컴포넌트" 대응을 맡는 라이브러리가 `react-router-dom`이고, 이번 예제는 그 최소 골격 — 라우터로 감싸기, 라우트 정의, 페이지 컴포넌트 — 세 조각만 세운다. 코드 자체는 몇 줄 안 되지만 앞으로 만들 모든 페이지가 이 틀 위에 올라가므로 구조를 정확히 잡아 두는 것이 목적이다.

## 1. 배운 내용

### 1-1. `react-router-dom` 설치와 의존성 확인

```json
"dependencies": {
  "react": "^19.2.8",
  "react-dom": "^19.2.8",
  "react-router-dom": "^7.18.4"
}
```

`npm install react-router-dom`으로 설치하면 `package.json`의 `dependencies`에 한 줄이 추가된다. day01에서 정리한 대로 `react`(컴포넌트·훅)와 `react-dom`(브라우저 DOM에 그리기)이 나뉘어 있듯, 라우팅도 React 본체가 아니라 **별도 패키지**다. 이름 끝의 `-dom`은 브라우저 주소창(History API)과 연동하는 웹용 구현이라는 뜻이고, 같은 라우터 핵심을 쓰는 네이티브용 패키지가 따로 있다.

버전 7은 `react-router`와 `react-router-dom`이 사실상 하나로 합쳐진 뒤의 버전이라, `import`할 때 두 이름 중 무엇을 써도 같은 컴포넌트가 나온다. 수업에서는 `react-router-dom`으로 통일한다.

### 1-2. 최초 렌더링 컴포넌트를 `BrowserRouter`로 감싸기

```jsx
import { BrowserRouter } from "react-router-dom";
import App from "../day04/App";

// 2. 최초 렌더링 되는 컴포넌트 앞뒤로 라우터 컴포넌트 감싼다.
create.render(
  <BrowserRouter>
    <App />
  </BrowserRouter>,
);
```

라우팅을 쓰려면 **가장 바깥 컴포넌트를 `BrowserRouter`로 한 번 감싼다.** `createRoot(root)`로 만든 `create`에 `render`하는 자리는 day01과 같고, 달라진 건 `<App />`이 `<BrowserRouter>` 안에 들어갔다는 것뿐이다.

| 조각 | 역할 |
| --- | --- |
| `BrowserRouter` | 주소창의 현재 경로를 읽고, 경로가 바뀌면 안쪽 컴포넌트들에게 알려 주는 **컨텍스트 제공자**. 앱에 하나만 둔다 |
| `<App />` | 이 안에서만 `Routes`·`Route`·`Link` 같은 라우터 부품을 쓸 수 있다 |

감싸는 위치가 중요하다. `Routes`나 `Link`는 `BrowserRouter` 바깥에서 쓰면 "라우터 컨텍스트가 없다"는 오류가 나므로, 진입점(`main.jsx`)에서 최상위 컴포넌트를 감싸 두는 것이 가장 단순하고 안전하다. 예제 파일은 `exam1.jsx`에 이 부분만 떼어 적어 두었고, 실제로는 `main.jsx`의 `create.render(...)` 자리에 그대로 옮겨 쓰면 된다.

### 1-3. `Routes`와 `Route` — 경로마다 컴포넌트 대응

```jsx
import { Route, Routes } from "react-router-dom";

export default function App(props) {
  return (
    <>
      <Routes>
        {/*여기에 들어가는 경로들은 주소정의에 따라 렌더링 */}
        <Route path="/도메인이후주소정의" element={<Home />} />
      </Routes>
    </>
  );
}
// <Route path="/도메인이후주소정의" element={ 컴포넌트/> } />
```

`App`이 하는 일은 **경로 표를 선언하는 것**이다.

| 조각 | 뜻 |
| --- | --- |
| `<Routes>` | 안에 든 `<Route>`들 중 **현재 주소와 맞는 하나**만 골라 그린다. `switch`문과 비슷하다 |
| `<Route path="…" element={…} />` | `path`가 주소창의 경로와 맞으면 `element`에 넣은 JSX를 렌더링한다 |
| `path` | 도메인 이후 부분. `http://localhost:5173/board`라면 `/board`가 `path`다 |
| `element={<Home />}` | 컴포넌트 이름이 아니라 **JSX 태그**를 넘긴다. `element={Home}`이 아니라 `element={<Home />}`다 |

주석에 적힌 대로 `path`는 "도메인 이후 주소 정의"다. 루트 페이지는 `path="/"`, 게시판은 `path="/board"` 식으로 라우트를 한 줄씩 늘려 가면 된다. `element`에 JSX를 넘기므로 `<Home title="메인" />`처럼 props도 그 자리에서 줄 수 있다.

`Routes` 안에는 `Route`만 두는 것이 원칙이고, 헤더·푸터처럼 모든 페이지에 공통으로 보일 부분은 `Routes` **바깥**(형제 위치)에 둔다. 그러면 경로가 바뀌어도 헤더·푸터는 그대로 있고 `Routes` 자리만 갈아끼워진다.

### 1-4. 페이지 컴포넌트 — 경로 하나에 컴포넌트 하나

```jsx
export default function Home(props) {
  return <> 메인페이지/본문 </>;
}
```

`Home`은 지금까지 만든 컴포넌트와 다를 게 없다. JSX를 반환하는 함수이고 `export default`로 내보낸다. 라우터 입장에서 "페이지"란 특별한 종류가 아니라 **`Route`의 `element`에 꽂힌 보통 컴포넌트**일 뿐이다. 그래서 페이지 안에서 `useState`·`useEffect`·자식 컴포넌트를 쓰는 방식도 이전과 똑같다.

관례상 라우트에 직접 꽂히는 컴포넌트는 `pages/` 폴더에, 여러 페이지가 공유하는 부품은 `components/` 폴더에 두어 역할을 구분한다. 이번 예제는 골격만이라 `day04/` 한 폴더에 `App.jsx`(라우트 표)와 `Home.jsx`(페이지)가 나란히 있다.

### 1-5. 세 파일이 맞물리는 순서

```
main.jsx        createRoot → <BrowserRouter><App /></BrowserRouter>   (주소 감시 시작)
   └ App.jsx    <Routes> 안에 <Route path element> 목록                (경로 표)
        └ Home.jsx   path가 맞을 때 그려지는 페이지 컴포넌트           (화면)
```

정리하면 이렇다. `BrowserRouter`가 주소를 읽고, `Routes`가 그 주소에 맞는 `Route`를 하나 고르고, 그 `Route`의 `element`가 화면이 된다. 주소가 바뀌면 이 과정이 다시 돌아 다른 `element`가 그려진다 — 페이지 전체를 서버에서 새로 받는 게 아니라 **`Routes` 자리의 컴포넌트만 교체**되는 것이 SPA 라우팅의 핵심이다.

day02 콜백 props 노트에서 `<a href>`의 기본 동작을 `preventDefault`로 막는 이유를 "CSR에서는 페이지 전체가 다시 로드되면 상태가 날아가기 때문"으로 정리했는데, React Router는 그 문제를 라이브러리 차원에서 푼 것이다. 주소는 바뀌지만 문서는 그대로이고 상태도 남는다.

### 1-6. 라우트 표 확장 — `index` 라우트·중첩 경로·`*` 폴백

골격을 세운 뒤 `App.jsx`의 경로 표에 세 종류의 `Route`가 더 들어갔다.

```jsx
import { Route, Routes } from "react-router-dom";
import NotFound from "./NotFound";
import LayoutIndex from "./LayoutIndex";

export default function App(props) {
  return (
    <>
      <Routes>
        {/*여기에 들어가는 경로들은 주소정의에 따라 렌더링 */}
        <Route path="/도메인이후주소정의" element={<Home />} />
        <Route path="intro" element={<CommonLayout />} />
        <Route index element={<LayoutIndex />} />
        <Route path="*" element={<NotFound />} />
      </Routes>
    </>
  );
}
```

| 선언 | 언제 그려지는가 |
| --- | --- |
| `<Route index element={…} />` | `path` 대신 `index` 속성만 둔다. 부모 경로 **그 자체**(여기서는 `/`)로 들어왔을 때 기본으로 보여 줄 화면이다. 폴더의 `index.html`과 같은 발상이다 |
| `<Route path="intro" element={…} />` | 앞에 `/`가 없는 **상대 경로**. 부모 `Routes`가 `/`에 있으니 결과적으로 `/intro`에 맞는다. 나중에 이 `Route`를 다른 `Route` 안으로 옮기면 부모 경로 뒤에 자동으로 붙는다 |
| `<Route path="*" element={…} />` | 위 어느 것에도 맞지 않는 주소 전부. 오타·삭제된 페이지가 여기로 떨어진다 |

`index` 라우트에 꽂힌 `LayoutIndex`는 `<h3> 레이아웃 인덱스 페이지 </h3>` 한 줄짜리 컴포넌트다. 이름에 "레이아웃"이 붙은 이유는, 이 자리가 나중에 공통 레이아웃(헤더·푸터)의 **기본 자식**이 되기 때문이다. `intro`에 꽂힌 `CommonLayout`도 같은 맥락으로, 이 라우트들이 곧 부모 `Route` 아래로 들어가 중첩되는 구조(1-10·3-1)로 이어질 자리다. `import`는 파일을 만든 것부터 순서대로 붙여 나가면 된다.

### 1-7. `NotFound` — 폴백 페이지에는 돌아갈 길을 둔다

```jsx
import { Link } from "react-router-dom";

export default function NotFound(props) {
  return (
    <>
      <h3> 오류 페이지 </h3>
      <Link to="/">홈으로</Link>
    </>
  );
}
```

`*`에 걸린 사용자는 주소를 잘못 친 상태이므로 화면에 **홈으로 가는 링크** 하나는 반드시 있어야 한다. `<a href="/">`가 아니라 `Link`를 쓰는 이유는 다음 항목에서 정리한다. 이 파일이 `App.jsx`에 `import`되는 첫 번째 페이지 컴포넌트이기도 하다.

### 1-8. `TopNavi` — `<a>` · `NavLink` · `Link` 세 가지 이동 방식

```jsx
import { Link, NavLink } from "react-router-dom";

export default function TopNavi(props) {
  return (
    <>
      <div>
        <a href="/">Home</a> {/* html 링크 마크업 */}
        <NavLink to="/intro">인트로</NavLink>
        <NavLink to="/router">라우터관련훅</NavLink>
        <Link to="/xyz">잘못된주소</Link>
      </div>
    </>
  );
}
```

원본 주석에 핵심이 그대로 적혀 있다.

| 마크업 | 페이지 로드(새로고침) | `active` 클래스 | 쓰는 자리 |
| --- | --- | --- | --- |
| `<a href="이동할경로">` | **있다** — 브라우저가 서버에 문서를 다시 요청한다 | 없다 | 외부 사이트로 나갈 때만 |
| `<NavLink to="이동할경로">` | 없다 | **있다** — 현재 주소와 맞으면 자동으로 붙는다 | 상단 메뉴·탭처럼 "지금 어디인지" 표시할 때 |
| `<Link to="이동할경로">` | 없다 | 없다 | 본문 안의 일반 이동(상세 보기·홈으로 등) |

셋 다 렌더링 결과는 `<a>` 태그지만, `NavLink`·`Link`는 클릭 시 서버 요청 대신 **주소만 바꾸고 `Routes`가 다시 고르게** 한다. 그래서 상태가 날아가지 않고 화면의 `Routes` 자리만 바뀐다. `<a href="/">Home</a>`을 일부러 하나 남겨 둔 것은 눌러 보면 다른 두 줄과 달리 화면이 깜빡이며 처음부터 다시 뜨는 것을 눈으로 비교하기 위해서다. `Link to="/xyz"`는 존재하지 않는 경로라서 1-6의 `*` 라우트, 즉 `NotFound`가 뜨는 것을 확인하는 용도다.

`NavLink`의 `to`는 **라우트 표의 최종 주소와 글자 그대로 맞아야** 한다. 1-10처럼 `intro`·`router`가 `path="/"`인 부모 바로 아래에 나란히 중첩되어 있으면 최종 주소는 `/intro`·`/router`이고, `to`도 그 값으로 적는다. 자리표시 문자열이나 한 단계 더 깊은 주소(`/intro/router`)를 적으면 맞는 `Route`가 없어 `*`로 떨어지므로, 메뉴를 만들 때는 `App.jsx`의 중첩 구조를 옆에 두고 주소를 하나씩 대조하는 편이 안전하다.

`NavLink`의 `active` 클래스는 CSS에서 `.active { font-weight: bold; }` 식으로 잡아 주면 현재 메뉴가 강조된다. 클래스 이름을 바꾸거나 조건을 넣고 싶으면 `className={({ isActive }) => isActive ? "on" : ""}`처럼 함수를 넘긴다.

### 1-9. `main.jsx`에서 실제로 갈아끼우기

```jsx
import App from "./example/day04/App.jsx";
create.render(<App></App>);
```

day01부터 써 온 방식대로 `main.jsx` 맨 아래에 `import` + `create.render` 두 줄을 붙여 day04의 `App`을 최초 렌더링 대상으로 바꾼다. 1-2에서 정리한 대로 이 `<App />`은 `BrowserRouter`로 감싸야 `Routes`·`Link`가 동작하므로, `exam1.jsx`의 형태를 그대로 옮겨 `<BrowserRouter><App /></BrowserRouter>`로 두는 것이 완성형이다. 현재 `main.jsx`는 이 완성형으로 정리되어 있고, 렌더링 대상은 1-14 실습의 `App3`다.

```jsx
// [day04] Routes/Route 는 Router 컨텍스트 안에서만 동작하므로 BrowserRouter 로 감싼다.
import { BrowserRouter } from "react-router-dom";
import App3 from "./example/day04/practice/App";
create.render(
  <BrowserRouter>
    <App3></App3>
  </BrowserRouter>,
);
```

### 1-10. 라우트를 중첩시키기 — `Route` 안의 `Route`

1-6에서 나란히 두었던 `intro`·`index` 라우트를 이번에는 `Home` 라우트 **안쪽**으로 옮기고, `router` 라우트를 하나 더 달았다.

```jsx
<Routes>
  <Route path="/도메인이후주소정의" element={<Home />}>
    <Route path="intro" element={<CommonLayout />} />
    <Route index element={<LayoutIndex />} />
    <Route path="router" element={<RouterHooks />} />
  </Route>
  <Route path="*" element={<NotFound />} />
</Routes>
```

`<Route … />`로 닫던 것을 `<Route …> … </Route>`로 열어 자식 `Route`를 품게 한 것이 전부인데, 의미는 크게 바뀐다.

| 위치 | 맞는 주소 | 그려지는 것 |
| --- | --- | --- |
| 부모 `path="/…"` | 부모 경로로 시작하는 모든 주소 | 부모 `element`(`Home`)가 **항상** 먼저 그려진다 |
| 자식 `index` | 부모 경로 그 자체 | 부모 안에서 `LayoutIndex` |
| 자식 `path="intro"` | 부모 경로 + `/intro` | 부모 안에서 `CommonLayout` |
| 자식 `path="router"` | 부모 경로 + `/router` | 부모 안에서 `RouterHooks` |

자식 `path`에 `/`를 붙이지 않는 이유가 여기서 드러난다. 앞에 `/`가 없으면 **부모 경로 뒤에 이어 붙는 상대 경로**가 되고, `/`를 붙이면 부모와 무관한 절대 경로가 되어 중첩이 깨진다. `TopNavi`의 `NavLink to="/intro"`·`to="/router"`가 한 단계 주소인 것은 이 중첩 구조 — 부모가 `/`이고 그 바로 아래에 `intro`·`router`가 나란히 있는 것 — 를 그대로 옮긴 결과다.

정리하면 핵심은 **부모 `element` 안에 자식이 그려질 자리를 표시해야 한다**는 점이다. 그 자리를 표시하는 부품이 `Outlet`이고, 부모 컴포넌트에 `<Outlet />`이 없으면 주소가 맞아도 자식 화면은 나타나지 않는다. 처음 골격을 세울 때의 `Home`은 `메인페이지/본문` 한 줄만 반환했고, 그 다음 단계에서 `Home`에 상단 메뉴와 `<Outlet />`을 넣어 공통 레이아웃으로 키웠다(1-13).

### 1-11. `RouterHooks` — `useLocation`과 `useSearchParams`

`router` 라우트에 꽂히는 `RouterHooks`는 **라우터가 제공하는 훅**을 눈으로 확인하는 화면이다. `useState`·`useEffect`처럼 함수 컴포넌트 맨 위에서 호출하고, `BrowserRouter` 안에서만 쓸 수 있다.

```jsx
import { useLocation, useSearchParams } from "react-router-dom";

const location = useLocation();
const [searchParams, setSearchParams] = useSearchParams();
const mode = searchParams.get("mode");
const pageNum = searchParams.get("pageNum");
```

| 훅 | 돌려주는 것 | 예 (`/intro/router?mode=list&pageNum=3`) |
| --- | --- | --- |
| `useLocation()` | 현재 주소를 담은 객체. `pathname`(경로)·`search`(`?`부터의 쿼리 문자열)·`hash`·`state` | `pathname` → `/intro/router`, `search` → `?mode=list&pageNum=3` |
| `useSearchParams()` | `[읽기용 객체, 바꾸는 함수]` 한 쌍. `useState`와 같은 모양이다 | `searchParams.get("mode")` → `"list"`, `get("pageNum")` → `"3"` |

`useLocation`은 **읽기 전용**이다. 주소가 바뀌면 이 값이 바뀌고 컴포넌트가 다시 그려지므로, 화면에 `{location.pathname}`·`{location.search}`를 찍어 두면 주소창과 항상 같은 값이 보인다.

`useSearchParams`는 쿼리 스트링을 **상태처럼** 다룬다. `searchParams`는 브라우저 표준 `URLSearchParams` 객체라 `get(이름)`으로 값을 꺼내고, 없는 키는 `null`을 돌려준다. 값은 언제나 **문자열**이라 페이지 번호처럼 숫자로 쓸 것은 `parseInt`가 필요하다.

```jsx
const changeMode = () => {
  const nextMode = mode === "list" ? "view" : "list";
  setSearchParams({ mode: nextMode, pageNum });
};

const nextPage = () => {
  const pageTemp = pageNum === null || isNaN(pageNum) ? 1 : parseInt(pageNum) + 1;
  setSearchParams({ mode, pageNum: pageTemp });
};
```

`setSearchParams(객체)`를 부르면 그 객체가 **통째로 새 쿼리 스트링**이 되어 주소창이 `?mode=view&pageNum=3`처럼 바뀌고, 컴포넌트가 다시 그려진다. 그래서 하나만 바꿀 때도 `mode`·`pageNum`을 **둘 다** 넣어야 한다 — 빠뜨린 키는 주소에서 사라진다. `useState`의 `set`이 값을 교체하는 것과 같은 규칙이다.

`nextPage`·`prevPage`의 삼항식은 "쿼리에 `pageNum`이 없거나 숫자가 아니면 1부터, 있으면 ±1"이라는 방어 로직이다. 사용자가 주소를 직접 고칠 수 있는 쿼리 스트링은 언제나 비어 있거나 이상한 값일 수 있다고 보고 처리하는 편이 안전하다.

이 화면이 보여 주는 것은, **페이지 번호·보기 모드 같은 화면 상태를 `useState`가 아니라 주소에 둘 수 있다**는 점이다. 주소에 두면 새로고침해도 유지되고, 그 주소를 복사해 다른 사람에게 보내도 같은 화면이 나오고, 브라우저 뒤로 가기가 곧 "이전 페이지"가 된다. 게시판 목록의 페이지·정렬·검색어가 대표적인 후보다.

### 1-12. 훅은 컴포넌트 최상위에서 부른다

`useLocation`·`useSearchParams`도 훅이므로 React의 **훅 규칙**을 그대로 따른다. 컴포넌트 함수 본문의 맨 위에서, 조건문·반복문·안쪽 함수에 넣지 않고 호출한다. 훅 호출을 안쪽 함수에 넣으면 그 함수 밖(JSX나 다른 핸들러)에서는 `location`·`mode` 같은 변수가 보이지 않아 렌더링 자체가 되지 않는다. 훅으로 얻은 값과 그 값을 쓰는 핸들러·JSX가 **같은 스코프**에 있는지 확인하는 습관이 필요하다. 변수 이름의 대소문자(`pageNum`)와 JSX 태그 이름(`button`)도 한 글자만 달라도 다른 것으로 취급된다는 점은 day01의 JSX 규칙과 같다.

### 1-13. `Outlet` — 부모 컴포넌트 안에 자식이 그려질 자리 두기

1-10에서 라우트를 중첩시켜 놓고 비워 두었던 마지막 조각이 채워졌다. 부모 라우트에 꽂힌 `Home`이 상단 메뉴와 `<Outlet />`을 품는 **공통 레이아웃**이 된 것이다.

```jsx
import { Outlet } from "react-router-dom";
import TopNavi from "./TopNavi";

export default function Home(props) {
  return (
    <>
      <TopNavi />
      <h2> 메인페이지/본문 </h2>
      {/* 자식 Route 가 렌더링되는 자리 */}
      <Outlet />
    </>
  );
}
```

`Outlet`은 `react-router-dom`에서 가져오는 컴포넌트로, **"현재 주소에 맞는 자식 `Route`의 `element`를 여기에 그려라"**는 표시다. `Home` 자체는 항상 그려지고(부모 경로로 시작하는 모든 주소에 맞으니까), `<Outlet />` 자리만 주소에 따라 갈아끼워진다.

| 주소 | `TopNavi` + 제목 | `<Outlet />` 자리 |
| --- | --- | --- |
| `/` | 그대로 | `LayoutIndex` (`index` 라우트) |
| `/intro` | 그대로 | `CommonLayout` (`인트로 페이지`) |
| `/router` | 그대로 | `RouterHooks` |
| `/xyz` | **안 보임** — 부모 `Route`가 아니라 `*` 라우트에 걸린다 | `NotFound` 전체 화면 |

`App.jsx`의 부모 경로도 자리표시용 문자열이었던 것을 실제 루트 `path="/"`로 바꿨다. 그래야 `index` 라우트가 `/`에, 자식 `intro`·`router`가 `/intro`·`/router`에 맞는다. `TopNavi`의 `NavLink`도 이 최종 주소에 맞춰 `to="/intro"`·`to="/router"`로 정리했다. `router`를 `intro` 안에 한 번 더 중첩시켰다면 주소는 `/intro/router`가 되었을 것이다 — 자식 경로가 어떤 부모 밑에 있는지에 따라 최종 주소가 결정되므로, 라우트 표를 옮길 때마다 메뉴의 `to`도 같이 맞춰야 한다.

`CommonLayout`은 `<h3> 인트로 페이지 </h3>` 한 줄짜리 페이지 컴포넌트다. 이름과 달리 지금은 레이아웃 역할이 아니라 `intro` 자리에 꽂히는 **자식 화면**이고, 실제 레이아웃 역할은 `Home`이 맡았다. 정리하면 이렇다.

```
main.jsx      <BrowserRouter><App /></BrowserRouter>
 └ App.jsx    <Route path="/" element={<Home />}>   ← 부모 = 레이아웃
                 <Route index … />  <Route path="intro" … />  <Route path="router" … />
      └ Home.jsx   <TopNavi />  <h2>…</h2>  <Outlet />   ← 자식은 Outlet 자리에
```

헤더·푸터를 `Routes` 바깥에 두는 방법(1-3)과 비교하면, 이 방식은 **레이아웃마다 부모 `Route`를 하나씩** 둘 수 있어 "메뉴가 있는 화면"과 "없는 화면"(`NotFound`)을 자연스럽게 나눌 수 있다.

### 1-14. 실습 — 사이드 네비 레이아웃으로 팀 소개 페이지 만들기

`day04/practice/`는 위 구조를 그대로 써서 **왼쪽 사이드 메뉴 + 오른쪽 본문**을 가진 팀 소개 페이지를 만드는 실습이다. 파일은 네 종류다.

| 파일 | 역할 |
| --- | --- |
| `practice/App.jsx` (`App3`) | 라우트 표. `path="/"`에 `Home`, 그 아래 팀원별 자식 라우트 네 개(`seung`·`hwan`·`hyun`·`yoo`) |
| `practice/Home.jsx` | 레이아웃. `<div className="wrap">` 안에 `<SideNav />`·`<Outlet />` 두 칸만 (처음 넣었던 `<h2>Home</h2>` 제목은 주석 처리) |
| `practice/SideNav.jsx` | 왼쪽 메뉴. 제목·`<a href="/">`·팀원 `NavLink` 네 개 |
| `practice/<팀원>.jsx` | 본문. 이름·학과·자기소개를 `<table>` 또는 `<span>` 묶음으로 그리는 페이지 컴포넌트 네 개 |
| `practice/index.css` | `flex` 두 칸 레이아웃, 메뉴 색상, 본문 `.Box` 가운데 정렬 |

```jsx
// practice/App.jsx
import Seung from "./신승민";
import 김지환 from "./김지환";
import Hanwoo from "./조현우";
import Practice2 from "./권유린";

<Routes>
  <Route path="/" element={<Home />}>
    <Route path="seung" element={<Seung />} />
    <Route path="hwan" element={<김지환 />} />
    <Route path="hyun" element={<Hanwoo />} />
    <Route path="yoo" element={<Practice2 />} />
  </Route>
</Routes>

// practice/Home.jsx
import "./index.css";
<div className="wrap">
  <SideNav />
  {/* <h2>Home</h2> */}
  <Outlet />
</div>
```

레이아웃에서 `<h2>Home</h2>`를 주석으로 돌린 이유는 `.wrap`이 `display: flex`라 자식이 **가로로 한 칸씩** 놓이기 때문이다. 제목이 살아 있으면 사이드 메뉴 · 제목 · 본문 세 칸이 되어 본문이 오른쪽으로 밀리고, 빼면 사이드 메뉴 · 본문 두 칸이 되어 `.Box { margin: 0 auto }`가 본문을 남은 공간 가운데에 놓는다. 공통 제목이 필요하면 `flex` 컨테이너의 직계 자식이 아니라 `<Outlet />` 쪽 페이지 안이나 별도의 세로 컨테이너에 두는 편이 안전하다.

`import` 이름과 `Route`의 `path`, `SideNav`의 `to`가 **세 군데에서 서로 맞아야** 한 팀원 페이지가 열린다. 파일명은 한글(`./조현우`), 가져온 이름은 영문(`Hanwoo`), 주소는 또 다른 약칭(`hyun`)처럼 셋이 전부 달라도 동작에는 문제가 없다 — `import 이름`은 이 파일 안에서만 쓰는 별칭이고, 주소는 `path`와 `to`가 같은 문자열이면 되기 때문이다. 다만 세 이름이 다르면 나중에 "이 메뉴가 어느 파일로 가는가"를 좇기 어려우니, 실제 프로젝트에서는 파일명·컴포넌트명·경로를 한 단어로 통일하는 편이 안전하다.

팀원 페이지 네 개는 같은 `className="Box"`를 쓰되 안쪽 마크업은 각자 다르다. 셋은 `<table><tbody><tr><td>` 두 칸 표로, 하나는 `<div><span>` 묶음으로 학과·자기소개를 적었다. `Outlet` 자리에 꽂히는 컴포넌트는 **바깥 레이아웃과 무관하게 자기 마크업을 자유롭게 가질 수 있다**는 것을 보여 주는 예다. `.Box { margin: 0 auto; }`는 `flex` 컨테이너(`.wrap`) 안에서 본문 칸을 가운데로 밀어 두는 한 줄이다. 한 팀원 파일은 `import "./index.css"`를 자기 파일에도 한 번 더 적었는데, day03 스타일링 노트에서 정리한 대로 `import`한 CSS는 **전역**이라 `Home.jsx`에서 한 번 불러온 것과 겹쳐도 결과는 같다. 중복 `import`는 해가 없지만, 레이아웃을 맡은 파일 한 곳에서만 불러오는 쪽이 어디서 스타일이 들어오는지 추적하기 쉽다.

`Home`이 `import "./index.css"`로 CSS를 끌어오는 방식은 day03 스타일링 노트에서 정리한 그대로다. `.wrap { display: flex }`로 사이드 메뉴(`.Nav`, `width: 20%; height: 100vh`)와 본문을 가로로 나란히 놓고, `<Outlet />`이 오른쪽 칸이 된다. 컴포넌트 이름이나 파일명에 한글을 쓴 것도 동작에는 문제가 없다 — JSX 태그가 대문자로 시작하지 않으면 HTML 태그로 취급된다는 규칙(day01)은 있지만, 한글 첫 글자는 소문자 규칙에 걸리지 않아 사용자 정의 컴포넌트로 인식된다. 다만 팀 작업에서는 영문 이름으로 통일하는 편이 안전하다.

`SideNav`의 메뉴는 1-8에서 비교한 세 가지 이동 방식이 다시 나온다. 홈으로 가는 `<a href="/">`는 새로고침이 나고, 팀원 `NavLink`는 화면의 `<Outlet />` 자리만 바뀐다. `NavLink`에 `className="bottomNav"`를 준 것은 메뉴 항목의 여백·hover 색을 잡기 위해서인데, 현재 주소와 맞으면 라우터가 `active` 클래스를 **덧붙이므로** `.bottomNav.active { … }` 규칙을 하나 더 두면 "지금 보고 있는 팀원"이 강조된다.

처음에는 메뉴에 팀원 네 명이 있어도 라우트 표에는 두 명만 있어서, 라우트가 없는 `NavLink`를 누르면 `*` 라우트조차 없으니 오른쪽 칸이 **비어 있게** 되었다. 이후 팀원이 각자 자기 파일을 만들어 `App3`에 `import` 한 줄 + `Route` 한 줄씩 추가하는 식으로 네 자리가 모두 채워졌다. 2-5에서 정리한 "라우트 표는 목차" 방식이 팀 작업에서 실제로 어떻게 굴러가는지 — 각자 페이지 파일을 따로 만들고 목차(`App3`)에만 한 줄씩 합치면 충돌 없이 합쳐진다 — 를 보여 주는 순서다. 이 실습에는 `path="*"` 라우트가 없으므로 메뉴 밖의 주소를 치면 사이드 메뉴만 남고 본문이 비는데, 1-6·2-4에서 정리한 폴백 라우트를 자식 위치에 하나 두면 해결된다. `main.jsx`는 이 실습의 `App3`를 `BrowserRouter`로 감싸 렌더링하도록 바뀌었다.

## 2. 추가로 알면 좋은 활용법

### 2-1. `Link`로 페이지 이동 — `<a>` 대신

```jsx
import { Link } from "react-router-dom";

<nav>
  <Link to="/">홈</Link>
  <Link to="/board">게시판</Link>
</nav>
```

`<a href="/board">`를 쓰면 브라우저가 서버에 새 문서를 요청해 앱이 처음부터 다시 뜬다. `Link`는 렌더링 결과는 `<a>`지만 클릭 시 `preventDefault` + 주소만 바꾸기를 대신 해 주므로 `Routes`가 자연스럽게 다른 `element`를 그린다. 라우터를 쓰는 앱에서 내부 이동은 항상 `Link`(또는 `NavLink`)로 한다. `NavLink`는 현재 경로와 맞을 때 `active` 클래스를 자동으로 붙여 줘서 메뉴 강조에 쓴다.

### 2-2. `useNavigate` — 코드에서 이동

```jsx
import { useNavigate } from "react-router-dom";

function WriteForm() {
  const navigate = useNavigate();
  const onSubmit = async (e) => {
    e.preventDefault();
    await fetch(…);          // 등록 요청
    navigate("/board");      // 성공하면 목록으로
  };
  …
}
```

클릭이 아니라 "등록 완료 후 목록으로", "로그인 실패 시 로그인 페이지로"처럼 **로직 안에서** 이동해야 할 때는 `useNavigate` 훅을 쓴다. `navigate(-1)`은 뒤로 가기다. `BrowserRouter` 안의 컴포넌트에서만 쓸 수 있다는 점은 `Routes`와 같다.

### 2-3. 동적 경로와 `useParams`

```jsx
<Route path="/board/:bno" element={<BoardDetail />} />

function BoardDetail() {
  const { bno } = useParams();   // "/board/7" → bno = "7"
  …
}
```

`path`에 `:이름`을 넣으면 그 자리는 **무엇이 와도 맞는 변수 구간**이 된다. 상세 페이지처럼 번호마다 화면이 달라지는 경우 라우트를 번호 개수만큼 만드는 게 아니라 하나로 받는다. `useParams()`로 꺼낸 값은 문자열이므로 숫자로 쓰려면 `Number(bno)`가 필요하다. 쿼리 스트링(`?page=2`)은 1-11에서 정리한 `useSearchParams`로 읽는다. 경로 변수(`/board/7`)는 "어느 자원인가", 쿼리 스트링(`?page=2&sort=new`)은 "그 자원을 어떻게 보여 줄까"에 쓰는 것이 관례다.

### 2-6. `setSearchParams`로 일부 키만 바꾸기

```jsx
setSearchParams((prev) => {
  prev.set("pageNum", String(next));
  return prev;
});
```

1-11처럼 객체를 통째로 넘기면 빠진 키가 사라진다. 키가 여러 개일 때는 이전 `URLSearchParams`를 받는 **함수형**으로 넘겨 필요한 키만 `set`하면 나머지가 유지된다. `useState`의 함수형 갱신과 같은 발상이다. 값은 문자열로만 들어가므로 숫자는 `String()`으로 바꿔 넣는 편이 명확하다.

### 2-4. 없는 경로 처리와 인덱스 라우트

```jsx
<Routes>
  <Route path="/" element={<Home />} />
  <Route path="/board" element={<Board />} />
  <Route path="*" element={<NotFound />} />
</Routes>
```

`path="*"`는 위의 어느 `Route`와도 맞지 않을 때 걸리는 마지막 그물이다(1-6에서 실제로 넣었다). 라우트 표를 만들 때 처음부터 넣어 두면 오타 난 주소가 빈 화면이 아니라 404 안내로 떨어진다. `Routes`는 선언 순서가 아니라 **가장 구체적으로 맞는 경로**를 고르므로 `*`를 어디에 두어도 동작은 같지만, 읽기 편하게 맨 아래에 두는 편이 낫다.

### 2-5. 라우트 표는 한 파일에 모아 두기

라우트가 늘어나면 `App.jsx`는 "이 앱에 어떤 페이지가 있는가"를 한눈에 보여 주는 **목차** 역할을 한다. 페이지 로직을 `App.jsx`에 쓰지 않고 각 페이지 파일로 밀어내면, 새 페이지를 추가할 때 파일 하나 만들고 `Route` 한 줄 추가하는 것으로 끝난다.

## 3. 더 나아가 알면 좋은 것

### 3-1. 중첩 라우트와 `Outlet` — 공통 레이아웃

```jsx
<Routes>
  <Route element={<Layout />}>        {/* 헤더·푸터 */}
    <Route path="/" element={<Home />} />
    <Route path="/board" element={<Board />} />
  </Route>
</Routes>

function Layout() {
  return (
    <>
      <Header />
      <Outlet />   {/* 자식 Route의 element가 여기 그려진다 */}
      <Footer />
    </>
  );
}
```

헤더·푸터를 `Routes` 바깥에 두는 방법(1-3)은 레이아웃이 하나일 때만 통한다. 관리자 페이지는 사이드바가 있고 일반 페이지는 없다면, `Route`를 **중첩**하고 부모 `element`에 `<Outlet />`을 두어 자식이 그려질 자리를 표시한다. day01에서 헤더·메인·푸터를 조립하던 것을 라우터가 대신 해 주는 셈이다. 1-10의 중첩 구조와 1-13의 `<Outlet />`으로 이 방식은 이미 한 번 만들어 보았다. 남은 변형은 위 예처럼 `path` 없이 `element`만 있는 부모 `Route`다 — 주소를 소비하지 않고 레이아웃만 씌우는 **레이아웃 라우트**라고 부르며, `path="/"`에 `Home`을 꽂는 지금 방식과 달리 여러 레이아웃을 같은 깊이에 나란히 둘 때 쓴다.

### 3-2. 새로고침 시 404 — 개발 서버와 배포 서버의 차이

`/board`에서 새로고침하면 브라우저는 서버에 `/board` 문서를 요청한다. Vite 개발 서버는 모든 경로를 `index.html`로 돌려주도록 되어 있어 문제가 없지만, 정적 호스팅이나 Spring Boot에 빌드 결과를 올리면 `/board`라는 파일이 없어 404가 난다. 배포 시에는 "모르는 경로는 전부 `index.html`"이라는 **폴백 설정**을 서버 쪽에 넣어야 한다. 이 설정이 어려운 환경에서는 주소에 `#`을 쓰는 `HashRouter`가 대안이다.

### 3-3. 데이터 라우터와 코드 분할

React Router 6.4 이후로는 `createBrowserRouter` + `RouterProvider`로 라우트를 객체 배열로 선언하고, 각 라우트에 `loader`(진입 전 데이터 요청)·`action`(폼 제출 처리)을 붙이는 **데이터 라우터** 방식이 있다. 지금의 `useEffect` + `fetch`가 라우트 정의로 옮겨 가는 구조다. 페이지가 많아지면 `React.lazy`로 페이지 파일을 라우트 진입 시점에만 내려받는 코드 분할도 같이 본다.

### 3-4. 다음에 볼 키워드

- `Link` · `NavLink` · `useNavigate` · `useParams` · `useSearchParams` 함수형 갱신 · `useLocation`의 `state`
- `path="*"` 404 처리 · `index` 라우트 · 중첩 라우트 + `Outlet` · 레이아웃 라우트
- `BrowserRouter` vs `HashRouter` · 배포 서버의 `index.html` 폴백
- `createBrowserRouter` · `loader`/`action` · `React.lazy` 코드 분할

## 실습 파일

- `KDT_2026/2026_React/src/example/day04/exam1.jsx` — `BrowserRouter`로 `<App />`을 감싸 `render`하는 진입부
- `KDT_2026/2026_React/src/example/day04/App.jsx` — `Routes` 안에 `Route path element`로 경로 표 선언, `Home` 라우트 아래 `intro`·`index`·`router` 중첩
- `KDT_2026/2026_React/src/example/day04/RouterHooks.jsx` — `useLocation`·`useSearchParams`로 경로·쿼리 스트링 읽고 바꾸기
- `KDT_2026/2026_React/src/example/day04/Home.jsx` — 부모 라우트의 레이아웃 컴포넌트. `TopNavi` + `<Outlet />`
- `KDT_2026/2026_React/src/example/day04/LayoutIndex.jsx` — `index` 라우트에 꽂히는 기본 화면
- `KDT_2026/2026_React/src/example/day04/CommonLayout.jsx` — `intro` 라우트에 꽂히는 인트로 화면
- `KDT_2026/2026_React/src/example/day04/NotFound.jsx` — `path="*"` 폴백 페이지, `Link to="/"`로 홈 복귀
- `KDT_2026/2026_React/src/example/day04/TopNavi.jsx` — `<a>` · `NavLink` · `Link` 세 이동 방식 비교
- `KDT_2026/2026_React/src/example/day04/practice/App.jsx` · `Home.jsx` · `SideNav.jsx` · `index.css` · 팀원별 `.jsx` 네 개(`신승민`·`김지환`·`조현우`·`권유린`) — 사이드 네비 레이아웃 팀 소개 실습, 자식 라우트 `seung`·`hwan`·`hyun`·`yoo`
- `KDT_2026/2026_React/src/main.jsx` — `BrowserRouter`로 감싼 실습 `App3`를 최초 렌더링 대상으로 교체
- `KDT_2026/2026_React/package.json` — `react-router-dom` 의존성 추가

## 관련 노트

[[React MOC]] · [[React day03 전화번호부 실습 배열 상태 추가와 삭제]] · [[React day02 컴포넌트 분리와 콜백 props]] · [[React day01 컴포넌트와 렌더링]] · [[KDT_2026 학습 지도]]
