---
출처: Claude 분석
원본: KDT_2026/2026_React/src/example/day06/종합실습
작성일: 2026-09-21
tags: [학습, react]
---

# React day07 — 게시판 종합실습: 스킨 분해와 mode 전환

> 실습 파일: `src/example/day06/종합실습/skin_board.html` · `index.css` · `App.jsx` · `components/article/*` · `components/navigation/*` · `src/main.jsx`
> 허브: [[React MOC]] · 이전: [[React day07 useRef와 렌더링을 일으키지 않는 값]] · 다음: (예정)

지금까지 배운 것을 한 자리에 모으는 종합실습이다. 완성된 HTML 시안(`skin_board.html`) 하나를 받아 **컴포넌트로 쪼개고**, 목록·열람·쓰기 세 화면을 **`mode` 상태 하나로 갈아끼우는** 게시판을 만든다. JS 수업에서 DOM으로 만들던 게시판 CRUD를 리액트 방식으로 다시 세우는 출발점이고, 컴포넌트 분리(day02) · 조건부 렌더링(day02) · 배열 렌더링과 `key`(day02) · props와 콜백(day02)이 전부 한 코드에 등장한다.

## 1. 배운 내용

### 1-1. 시안 먼저, 분해는 그 다음 — `skin_board.html`

`skin_board.html`은 리액트가 아니라 **순수 HTML로 게시판 세 화면을 전부 그려 둔 시안**이다. 목록(`header`+`nav`+표) · 열람(`colgroup` 상세 표) · 작성(`form`+입력 표)이 한 문서에 세로로 나열되어 있고, `<style>`에 표 테두리·정렬 CSS까지 들어 있다.

작업 순서가 핵심이다.

1. 정적 HTML로 화면 전체를 먼저 완성한다 (디자인 확정)
2. 화면을 **의미 단위로 자른다** — 머리글 / 네비게이션 / 본문(article)
3. 잘라낸 조각을 컴포넌트 파일로 옮기고, `<style>` 내용은 `index.css`로 뺀다
4. 반복되는 데이터(글 목록의 `<tr>`)는 하드코딩을 걷어내고 배열 + 반복으로 바꾼다

HTML을 JSX로 옮길 때 손봐야 할 곳도 정해져 있다 — `class` → `className`, 닫는 태그 없는 `<input>`·`<col>`은 자기 닫힘(`/>`), 주석은 `{/* */}`.

### 1-2. 폴더 구조 — 성격별로 나눈 `components/`

```
종합실습/
├── App.jsx                        ← 조립 + mode 상태
├── index.css                      ← skin_board.html의 <style> 이관
├── skin_board.html                ← 원본 시안 (참고용)
└── components/
    ├── article/                   ← 본문 영역 3종
    │   ├── ArticleList.jsx        (목록 표)
    │   ├── ArticleView.jsx        (열람 표)
    │   └── ArticleWrite.jsx       (작성 폼)
    └── navigation/                ← 네비 영역 3종
        ├── NavList.jsx            (글쓰기 링크)
        ├── NavView.jsx            (목록·수정·삭제 링크)
        └── NavWrite.jsx           (목록 링크)
```

화면 단위(목록 화면·열람 화면)가 아니라 **영역 단위(article·navigation)** 로 폴더를 나눈 점이 눈에 띈다. 어느 화면이든 "네비 하나 + 본문 하나" 조합이라, 같은 자리에 꽂히는 부품끼리 모아 두면 세 화면이 항상 같은 골격을 유지한다.

### 1-3. `mode` 상태 하나로 세 화면 갈아끼우기

day02에서 `FrontComp`/`BackComp`를 골라 그리던 조건부 렌더링을 게시판 규모로 키운 형태다. **JSX를 변수에 담아 두고, `if`로 어떤 부품을 담을지 고른다.**

```jsx
const [mode, setMode] = useState("list");
let articleComp, navComp, titleVar;

if (mode === "list") {
  titleVar = "게시판-목록";
  navComp = <NavList onChangeMode={() => setMode("write")} />;
  articleComp = <ArticleList boardData={boardData} onChangeMode={() => setMode("view")} />;
} else if (mode === "view") {
  titleVar = "게시판-열람";
  navComp = <NavView onChangeMode={(pmode) => setMode(pmode)} />;
  articleComp = <ArticleView />;
} else if (mode === "write") {
  titleVar = "게시판-쓰기";
  navComp = <NavWrite onChangeMode={() => setMode("list")} />;
  articleComp = <ArticleWrite />;
}
```

| 조각 | 역할 |
| --- | --- |
| `mode` | 지금 어떤 화면인지 나타내는 문자열 상태 (`"list"` / `"view"` / `"write"`) |
| `titleVar` | mode에서 **계산되는 파생값** — 별도 상태로 두지 않는다 |
| `navComp` · `articleComp` | mode에 맞는 부품을 담는 JSX 변수. `return`의 같은 자리에 꽂힌다 |
| `onChangeMode` | 자식이 부모의 `mode`를 바꾸게 하는 콜백 props (상태 끌어올리기) |

주소(URL)는 그대로 두고 상태만으로 화면을 바꾸는 방식이라, day04의 라우터 없이도 SPA 화면 전환이 된다. `mode` 값이 바뀌면 `App6` 함수가 재실행되고, `if`가 다른 부품을 골라 담고, 같은 자리에 다른 화면이 그려진다 — 재렌더링 한 번이 화면 전환 한 번이다.

콜백을 넘기는 모양도 두 가지가 함께 나온다. 목적지가 정해진 쪽은 `() => setMode("write")`처럼 **값을 박아서**, 목적지가 여러 개인 `NavView`는 `(pmode) => setMode(pmode)`처럼 **자식이 고른 값을 매개변수로 받아서** 처리한다.

### 1-4. `ArticleList` — 배열 props를 `for`로 돌려 `<tr>` 쌓기

글 목록 데이터는 부모가 `boardData` 배열(각 원소는 `no`·`title`·`writer`·`date`·`contents` 객체)로 내려 주고, 자식은 그리기만 한다.

```jsx
const lists = [];
for (let i = 0; i < props.boardData.length; i++) {
  let row = props.boardData[i];
  lists.push(
    <tr key={row.no}>
      <td className="cen">{row.no}</td>
      <td><a href={"/read/" + row.no}>{row.title}</a></td>
      <td className="cen">{row.writer}</td>
      <td className="cen">{row.date}</td>
    </tr>,
  );
}
return ( ... <tbody>{lists}</tbody> ... );
```

- 지금까지 주로 쓰던 `map` 대신 **`for` + `push`로 JSX 배열을 만드는** 방식이다. 결과물은 같다 — JSX 배열을 `{lists}`로 꽂으면 리액트가 순서대로 펼쳐 그린다. 조건에 따라 건너뛰거나 여러 줄을 밀어 넣는 등 반복 안에서 할 일이 많으면 이쪽이 오히려 읽기 쉬울 때가 있다
- `key={row.no}`는 인덱스가 아니라 **데이터의 고유값**으로 — 삭제·정렬이 생겨도 흔들리지 않는 기준이다
- 서버가 아직 없으므로 `boardData`는 컴포넌트 안의 하드코딩 배열이다. 나중에 이 자리만 `useEffect` + axios 조회로 바꾸면 되는 구조를 미리 잡아 둔 셈이다

### 1-5. `ArticleView` · `ArticleWrite` — 정적 조각의 이식

열람 화면은 `colgroup`으로 열 너비(30% / 나머지 `*`)를 잡은 상세 표, 작성 화면은 `form` 안에 입력 표(`input` 2개 + `textarea`)와 `submit` 버튼을 둔 구조다. 아직 props 없이 시안 그대로 옮긴 상태라, 다음 단계가 자연스럽게 보인다 — 열람은 "클릭한 행의 객체"를 props로 받아 채우고, 작성은 입력값을 읽어 부모 배열에 추가하는 것(day03 폼 제출·전화번호부 실습의 자리다).

`index.css`는 `skin_board.html`의 `<style>`을 그대로 옮긴 전역 CSS다. `import "./index.css"` 한 줄로 붙이고, `#boardTable` 같은 `id` 선택자와 `.cen` 클래스가 JSX의 `className`과 만난다.

### 1-6. `main.jsx` — 진입 컴포넌트 교체

```jsx
import { BrowserRouter } from "react-router-dom";
import App6 from "./example/day06/종합실습/App";

create.render(
  <BrowserRouter>
    <App6></App6>
  </BrowserRouter>,
);
```

day마다 반복해 온 관례다 — `main.jsx`에서 이전 진입 컴포넌트를 주석으로 남기고 새 실습의 `App`을 꽂는다. 지금 화면 전환은 `mode` 상태가 담당하지만, `BrowserRouter`로 감싼 골격을 유지해 두었으므로 뒤에서 라우터 기반 전환으로 넘어갈 준비가 되어 있다.

## 2. 추가로 알면 좋은 활용법

### 2-1. SPA 안의 `<a href>`는 새로고침을 부른다

`<a href="...">`를 그대로 클릭하면 브라우저가 문서를 새로 받아오면서 **리액트 상태가 전부 초기화**된다. SPA에서 화면 안 이동은 다음 중 하나로 처리하는 편이 안전하다.

```jsx
// 콜백 방식 — 상태 전환
<a href="#" onClick={(e) => { e.preventDefault(); props.onChangeMode("list"); }}>목록</a>

// 라우터 방식 — 주소 전환
<Link to="/read/3">글 제목</Link>
```

`preventDefault`로 기본 이동을 막고 콜백을 부르거나(day02 컴포넌트 분리에서 정리한 패턴), 라우터를 쓴다면 `Link`/`NavLink`로 바꾼다. 시안에서 옮겨 온 `<a>` 태그는 이 처리를 붙이는 순간부터 진짜 SPA 부품이 된다.

### 2-2. mode 문자열보다 한 단계 위 — 객체로 화면 표 만들기

`if/else if`가 길어지면 mode → 부품 대응을 객체 하나로 정리할 수 있다.

```jsx
const screens = {
  list:  { title: "게시판-목록", nav: <NavList ... />,  article: <ArticleList ... /> },
  view:  { title: "게시판-열람", nav: <NavView ... />,  article: <ArticleView /> },
  write: { title: "게시판-쓰기", nav: <NavWrite ... />, article: <ArticleWrite /> },
};
const screen = screens[mode];
```

분기가 데이터가 되면 화면을 추가할 때 객체에 한 줄만 늘리면 된다. day04의 라우트 표(`<Route path element />`)가 하는 일과 같은 발상이라, 이 모양이 익숙해지면 라우터로 넘어가는 것도 자연스럽다.

### 2-3. 열람 화면에 "무엇을 열었는지" 전달하기

목록에서 행을 클릭해 열람으로 넘어갈 때는 mode만 바꿔서는 부족하고 **어느 글인지**도 함께 올라가야 한다. 상태를 하나 더 두는 것이 기본형이다.

```jsx
const [selectRow, setSelectRow] = useState(null);
// 목록에서: onClick={() => { setSelectRow(row); setMode("view"); }}
// 열람에서: <ArticleView article={selectRow} />
```

`App.jsx`에 `selectRow` 변수 자리가 이미 잡혀 있다 — 클릭한 행의 **객체 전체**를 올려보내는 패턴(day05 외부 API 실습에서 쓴 방식)이 그대로 이어진다.

### 2-4. 글 추가는 "복사해서 새 배열"로

작성 폼이 완성되면 `boardData`를 `useState`로 올리고, 추가는 스프레드 복사로 한다.

```jsx
const [boardData, setBoardData] = useState(초기배열);
setBoardData([...boardData, { no: 다음번호, title, writer, date, contents }]);
```

배열 상태는 **주소값이 바뀌어야 재렌더링**된다(day02·day03에서 반복 확인). `push`만 하면 화면이 안 바뀌는 것부터 의심한다.

## 3. 더 나아가 알면 좋은 것

### 3-1. mode 전환 vs 라우터 전환

같은 게시판을 두 방식으로 만들 수 있다.

| | mode 상태 방식 (지금) | 라우터 방식 (day04) |
| --- | --- | --- |
| 화면 전환 | `setMode(...)` | `<Link to>` / `useNavigate` |
| 주소창 | 안 바뀜 | `/`, `/write`, `/read/3`처럼 바뀜 |
| 새로고침·북마크 | 항상 첫 화면으로 | 보던 화면 유지 |
| 뒤로 가기 | 페이지 이탈 | 이전 화면으로 |

mode 방식은 구조가 단순해 컴포넌트 분해와 상태 흐름을 익히기 좋고, 실제 서비스에서는 주소가 화면을 대표해야 하므로 라우터 방식으로 옮겨 간다. `/read/:no` 동적 세그먼트와 `useParams`로 글 번호를 주소에서 꺼내는 것이 다음 단계다.

### 3-2. 서버 연동으로 가는 길

지금 하드코딩된 `boardData`는 스프링 쪽 수업에서 만든 게시판 API와 만날 자리다. 목록은 `useEffect(…, [])` + `axios.get`, 등록은 폼 값 `axios.post` 후 재조회 — day02 CRUD 실습과 day05 axios 실습에서 만든 뼈대가 그대로 들어온다. 프론트(2026_React)와 백엔드(2026B_Spring)가 같은 게시판 도메인으로 수렴하는 중이다.

### 3-3. 다음에 볼 키워드

- `useReducer` — mode·selectRow·boardData처럼 얽힌 상태 여러 개를 액션으로 묶기
- `Context` — `onChangeMode`를 여러 층 내려보내는 props drilling 줄이기
- `<Outlet>` + 중첩 라우트로 게시판 레이아웃 만들기 (day04 복습)
- 제어 컴포넌트로 작성 폼 완성하기 (`value`/`onChange`, 검증, `trim()`)
- 목록 페이징(`slice` 또는 서버 `params`)과 정렬

## 실습 파일

- `KDT_2026/2026_React/src/example/day06/종합실습/skin_board.html` — 게시판 세 화면(목록·열람·작성)의 순수 HTML 시안
- `KDT_2026/2026_React/src/example/day06/종합실습/index.css` — 시안의 `<style>`을 옮긴 전역 CSS
- `KDT_2026/2026_React/src/example/day06/종합실습/App.jsx` — `boardData`·`mode` 상태와 화면 조립
- `KDT_2026/2026_React/src/example/day06/종합실습/components/article/ArticleList.jsx` · `ArticleView.jsx` · `ArticleWrite.jsx` — 본문 3종
- `KDT_2026/2026_React/src/example/day06/종합실습/components/navigation/NavList.jsx` · `NavView.jsx` · `NavWrite.jsx` — 네비 3종
- `KDT_2026/2026_React/src/main.jsx` — 진입 컴포넌트를 종합실습 `App6`으로 교체

## 관련 노트

[[React MOC]] · [[React day07 useRef와 렌더링을 일으키지 않는 값]] · [[KDT_2026 학습 지도]]

<!--
[문체 규칙]
- 내가 공부하며 정리한 노트다. 남의 코드를 평가하는 말투를 쓰지 않는다.
- 2인칭(하신, 쓰셨, 적으신)을 쓰지 않는다.
- 원본 코드의 오류·오타는 기록하지 않는다. 필요하면 파일 지목 없이 일반 주의사항으로 쓴다.
- 한 사람이 쭉 이어서 쓴 것처럼 문체를 일정하게 유지한다.
-->
