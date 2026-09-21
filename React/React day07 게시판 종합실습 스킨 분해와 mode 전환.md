---
출처: Claude 분석
원본: KDT_2026/2026_React/src/example/day06/종합실습
작성일: 2026-09-21
tags: [학습, react]
---

# React day07 — 게시판 종합실습: 스킨 분해와 mode 전환

> 실습 파일: `src/example/day06/종합실습/skin_board.html` · `index.css` · `App.jsx` · `components/article/*` · `components/navigation/*` · `src/main.jsx`
> 허브: [[React MOC]] · 이전: [[React day07 useRef와 렌더링을 일으키지 않는 값]] · 다음: (예정)

지금까지 배운 것을 한 자리에 모으는 종합실습이다. 완성된 HTML 시안(`skin_board.html`) 하나를 받아 **컴포넌트로 쪼개고**, 화면들을 **`mode` 상태 하나로 갈아끼우는** 게시판을 만든다. 앞부분에서 목록·열람·쓰기 골격을 세운 뒤, 이어서 **열람에 데이터 연결 → 작성 처리 → 삭제 → 수정 처리**까지 실제 CRUD 네 동작을 완성했다. JS 수업에서 DOM으로 만들던 게시판 CRUD를 리액트 방식으로 다시 세우는 실습이고, 컴포넌트 분리(day02) · 조건부 렌더링(day02) · 배열 렌더링과 `key`(day02) · props와 콜백(day02) · 폼 제출(day03)이 전부 한 코드에 등장한다.

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
├── App.jsx                        ← 조립 + mode·no·nextNo 상태
├── index.css                      ← skin_board.html의 <style> 이관
├── skin_board.html                ← 원본 시안 (참고용)
└── components/
    ├── article/                   ← 본문 영역 4종
    │   ├── ArticleList.jsx        (목록 표)
    │   ├── ArticleView.jsx        (열람 표)
    │   ├── ArticleWrite.jsx       (작성 폼)
    │   └── ArticleEdit.jsx        (수정 폼)
    └── navigation/                ← 네비 영역 4종
        ├── NavList.jsx            (글쓰기 링크)
        ├── NavView.jsx            (목록·수정·삭제 링크)
        ├── NavWrite.jsx           (목록 링크)
        └── NavEdit.jsx            (뒤로·목록 링크)
```

화면 단위(목록 화면·열람 화면)가 아니라 **영역 단위(article·navigation)** 로 폴더를 나눈 점이 눈에 띈다. 어느 화면이든 "네비 하나 + 본문 하나" 조합이라, 같은 자리에 꽂히는 부품끼리 모아 두면 화면이 늘어도 항상 같은 골격을 유지한다. 수정 화면을 추가할 때도 `article/`과 `navigation/`에 한 파일씩만 늘었다.

### 1-3. `mode` 상태 하나로 화면 갈아끼우기

day02에서 `FrontComp`/`BackComp`를 골라 그리던 조건부 렌더링을 게시판 규모로 키운 형태다. **JSX를 변수에 담아 두고, `if`로 어떤 부품을 담을지 고른다.**

```jsx
const [boardData, setBoardData] = useState([...초기 글 3건...]);
const [mode, setMode] = useState("list");
const [no, setNo] = useState(null);        // 열람·수정 대상 글 번호
const [nextNo, setNextNo] = useState(4);   // 새 글에 붙일 일련번호

let articleComp, navComp, titleVar, selectRow;

if (mode === "list") {
  titleVar = "게시판-목록";
  navComp = <NavList onChangeMode={() => setMode("write")} />;
  articleComp = (
    <ArticleList boardData={boardData}
      onChangeMode={(no) => { setMode("view"); setNo(no); }} />
  );
} else if (mode === "view") { ... }
  else if (mode === "write") { ... }
  else if (mode === "delete") { ... }
  else if (mode === "edit") { ... }
```

| 조각 | 역할 |
| --- | --- |
| `mode` | 지금 어떤 화면인지 나타내는 문자열 상태 (`"list"` / `"view"` / `"write"` / `"delete"` / `"edit"`) |
| `no` | 목록에서 클릭한 **글 번호**. 열람·수정 분기가 이 번호로 대상 글을 찾는다 |
| `nextNo` | 다음 글에 붙일 일련번호. 글을 추가할 때마다 1씩 올린다 |
| `titleVar` | mode에서 **계산되는 파생값** — 별도 상태로 두지 않는다 |
| `navComp` · `articleComp` | mode에 맞는 부품을 담는 JSX 변수. `return`의 같은 자리에 꽂힌다 |
| `onChangeMode` | 자식이 부모의 `mode`를 바꾸게 하는 콜백 props (상태 끌어올리기) |

주소(URL)는 그대로 두고 상태만으로 화면을 바꾸는 방식이라, day04의 라우터 없이도 SPA 화면 전환이 된다. `mode` 값이 바뀌면 `App6` 함수가 재실행되고, `if`가 다른 부품을 골라 담고, 같은 자리에 다른 화면이 그려진다 — 재렌더링 한 번이 화면 전환 한 번이다.

콜백을 넘기는 모양도 여러 가지가 함께 나온다. 목적지가 정해진 쪽은 `() => setMode("write")`처럼 **값을 박아서**, 목적지가 여러 개인 `NavView`는 `(pmode) => setMode(pmode)`처럼 **자식이 고른 값을 매개변수로 받아서**, 목록의 행 클릭은 `(no) => { setMode("view"); setNo(no); }`처럼 **자식이 알려 준 데이터로 상태 두 개를 함께** 바꾼다.

### 1-4. `ArticleList` — 배열 props를 `for`로 돌려 `<tr>` 쌓기

글 목록 데이터는 부모가 `boardData` 배열(각 원소는 `no`·`title`·`writer`·`date`·`contents` 객체)로 내려 주고, 자식은 그리기만 한다.

```jsx
const lists = [];
for (let i = 0; i < props.boardData.length; i++) {
  let row = props.boardData[i];
  lists.push(
    <tr key={row.no}>
      <td className="cen">{row.no}</td>
      <td>
        <a href={"/read/" + row.no}
          onClick={(event) => {
            event.preventDefault();      // 문서 이동(새로고침) 취소
            props.onChangeMode(row.no);  // 클릭한 행의 글 번호를 부모로
          }}>
          {row.title}
        </a>
      </td>
      <td className="cen">{row.writer}</td>
      <td className="cen">{row.date}</td>
    </tr>,
  );
}
return ( ... <tbody>{lists}</tbody> ... );
```

- 지금까지 주로 쓰던 `map` 대신 **`for` + `push`로 JSX 배열을 만드는** 방식이다. 결과물은 같다 — JSX 배열을 `{lists}`로 꽂으면 리액트가 순서대로 펼쳐 그린다. 조건에 따라 건너뛰거나 여러 줄을 밀어 넣는 등 반복 안에서 할 일이 많으면 이쪽이 오히려 읽기 쉬울 때가 있다
- `key={row.no}`는 인덱스가 아니라 **데이터의 고유값**으로 — 삭제·정렬이 생겨도 흔들리지 않는 기준이다
- 제목의 `<a>`는 시안에서 옮겨 온 태그지만, `preventDefault`로 기본 이동을 막고 **클릭한 행의 `row.no`를 콜백에 실어 올려보낸다.** 반복 안에서 만든 핸들러가 자기 `row`를 기억하고 있어서(클로저), 행마다 다른 번호가 올라간다
- 서버가 아직 없으므로 `boardData`는 `App`의 하드코딩 배열이다. 나중에 이 자리만 `useEffect` + axios 조회로 바꾸면 되는 구조를 미리 잡아 둔 셈이다

### 1-5. 열람 — `no`로 대상 글을 찾아 props로 내려주기

목록에서 올라온 글 번호가 `no` 상태에 담기면, `view` 분기가 **렌더링할 때마다 `boardData`에서 그 번호의 객체를 찾아** `ArticleView`에 내려준다.

```jsx
} else if (mode === "view") {
  titleVar = "게시판-열람";
  navComp = <NavView onChangeMode={(pmode) => setMode(pmode)} />;
  for (let i = 0; i < boardData.length; i++) {
    if (no === boardData[i].no) selectRow = boardData[i];
  }
  articleComp = <ArticleView selectRow={selectRow} />;
}
```

`selectRow`는 상태가 아니라 **렌더링 중에 계산되는 지역변수**다. `no`와 `boardData`에서 언제든 다시 계산할 수 있는 값이라 상태로 둘 필요가 없다 — 1-3의 `titleVar`와 같은 "파생값" 원칙이다.

`ArticleView`는 받은 객체를 표에 채우는데, **글 내용의 개행 처리를 세 가지 방법으로 나란히 실험**한 부분이 이 파일의 볼거리다. 초기 데이터의 `contents`에 `\n`이 들어 있다.

| 방법 | 코드 | 결과 |
| --- | --- | --- |
| 그대로 출력 | `{props.selectRow.contents}` | HTML은 개행 문자를 공백 취급 — 줄바꿈이 사라진다 |
| 잘라서 `<br/>` | `contents.split("\n").map(...)` 으로 줄마다 `<br/>` 붙이기 | 줄바꿈 복원. 문자열을 배열로 만들어 JSX 배열로 그리는 응용 |
| CSS로 해결 | `<td style={{ whiteSpace: "pre-wrap" }}>` | 개행·공백을 보존하라고 브라우저에 맡기는 한 줄 해법 |

`split` + `map`은 "문자열도 배열로 만들면 배열 렌더링 패턴을 그대로 쓸 수 있다"는 확인이고, 실무에서는 CSS `white-space` 쪽이 코드가 가장 짧다. 인라인 스타일 객체(`{{ }}`)와 camelCase 속성명(`whiteSpace`)은 day03에서 정리한 규칙 그대로다.

### 1-6. 작성 — 폼 제출을 콜백으로 올려 배열에 추가

`ArticleWrite`는 폼 제출 이벤트에서 **`name`으로 입력값을 읽어**(day03 폼 제출 방식) 부모가 내려준 `writeAction` 콜백에 실어 올린다.

```jsx
<form onSubmit={(e) => {
  e.preventDefault();
  let title = e.target.title.value;
  let writer = e.target.write.value;
  let contents = e.target.contents.value;
  props.writeAction(title, writer, contents);
}}>
```

받는 쪽(`App`)이 게시판의 "등록 처리"다. 새 객체를 만들어 **복사본 배열에 추가하고** 상태를 갈아끼운 뒤 목록으로 돌아간다.

```jsx
writeAction={(t, w, c) => {
  let nowDate = new Date().toISOString().slice(0, 10);  // "YYYY-MM-DD"
  let addBoardData = { no: nextNo, title: t, writer: w, contents: c, date: nowDate };
  let copyBoardData = [...boardData];  // 복사본 생성
  copyBoardData.push(addBoardData);    // 복사본에 추가
  setBoardData(copyBoardData);         // 상태 변경 → 재렌더링
  setNextNo(nextNo + 1);               // 일련번호 증가
  setMode("list");                     // 목록으로 전환
}}
```

- **원본을 `push`하지 않고 스프레드 복사본에 `push`한다.** 배열 상태는 주소값이 바뀌어야 재렌더링된다(day02·day03에서 반복 확인). 복사본은 새 주소이므로 `push`로 채워도 된다 — `[...boardData, addBoardData]` 한 줄과 같은 원리다
- 일련번호를 `boardData.length + 1`이 아니라 **별도 상태 `nextNo`로 관리**한다. 글을 삭제해도 번호가 겹치지 않게 하는 장치다
- `new Date().toISOString().slice(0, 10)`은 날짜를 `"YYYY-MM-DD"` 문자열로 만드는 관용구다
- 상태 변경 세 번(`setBoardData`·`setNextNo`·`setMode`)이 한 핸들러에 모여 있어도 리액트가 모아서(배칭) 한 번만 재렌더링한다

### 1-7. 삭제 — 화면이 없는 mode

`NavView`의 삭제 링크는 `window.confirm`으로 한 번 묻고 나서 mode를 바꾼다.

```jsx
onClick={(event) => {
  event.preventDefault();
  if (window.confirm("삭제할까요?")) props.onChangeMode("delete");
}}
```

`delete` 분기는 다른 분기와 달리 **화면 부품을 담지 않는다.** 현재 `no`와 일치하지 않는 글만 새 배열에 옮겨 담아 상태를 갈아끼우고, 곧바로 목록으로 돌아간다.

```jsx
} else if (mode === "delete") {
  let newBoardData = [];
  for (let i = 0; i < boardData.length; i++) {
    if (no !== boardData[i].no) newBoardData.push(boardData[i]);
  }
  setBoardData(newBoardData);
  setMode("list");
}
```

"삭제 = 그 원소를 뺀 **새 배열**로 교체"라는 불변 업데이트 패턴은 전화번호부 실습(day03)의 삭제와 같다. `filter` 한 줄로도 같은 결과가 된다 — `boardData.filter((row) => row.no !== no)`.

### 1-8. 수정 — 열람의 형제 화면, 폼의 초기값 채우기

`edit` 분기는 `view`와 똑같이 `no`로 `selectRow`를 찾아 내려주되, 본문에 표가 아니라 **폼**을 꽂는다. `NavEdit`은 뒤로(열람으로)·목록 두 갈래라 콜백도 `onBack`·`onChangeMode` 두 개를 받는다 — 콜백 props의 이름은 자식이 "무슨 일이 일어났는지"를 기준으로 짓는다.

`ArticleEdit`은 작성 폼과 골격이 같지만 한 가지가 다르다. **빈 폼이 아니라 기존 글의 값이 채워진 채로 시작해야 한다.** 그래서 `selectRow`의 값을 초기값으로 삼는 상태를 세 개 두고, 입력칸마다 `value` + `onChange` 짝을 완성한 **제어 컴포넌트**로 만들었다.

```jsx
const [title, setTitle] = useState(props.selectRow.title);
const [writer, setWriter] = useState(props.selectRow.writer);
const [contents, setContents] = useState(props.selectRow.contents);

<input type="text" name="title" value={title}
  onChange={(event) => setTitle(event.target.value)} />
// writer는 input, contents는 textarea — 셋 다 같은 짝
```

`textarea`도 HTML과 달리 태그 사이가 아니라 **`value` 속성으로** 내용을 넣는다 — 리액트가 입력 3종(input·textarea·select)을 전부 `value` + `onChange` 한 가지 모양으로 통일해 둔 덕이다. 제출은 작성 폼과 같은 모양으로 `event.target.이름.value`를 읽어 `editAction` 콜백에 실어 올린다.

받는 쪽(`App`)의 `editAction`이 수정의 마무리다. 새 객체를 만들되 **번호와 작성일은 원래 글의 것을 유지**하고, 복사본 배열에서 같은 번호의 원소만 갈아끼운 뒤 열람 화면으로 돌아간다.

```jsx
editAction={(t, w, c) => {
  let editBoardData = { no: no, title: t, writer: w, contents: c, date: selectRow.date };
  let copyBoardData = [...boardData];
  for (let i = 0; i < copyBoardData.length; i++) {
    if (copyBoardData[i].no === no) {
      copyBoardData[i] = editBoardData;
      break;                    // 찾았으면 더 돌 필요가 없다
    }
  }
  setBoardData(copyBoardData);
  setMode("view");              // 목록이 아니라 방금 고친 글의 열람으로
}}
```

추가(1-6)·삭제(1-7)·수정이 전부 "새 배열을 만들어 교체"로 끝나는 **불변 업데이트 삼형제**가 이로써 완성됐다. 수정 후 `setMode("view")`로 돌아가면, `view` 분기가 최신 `boardData`에서 같은 번호를 다시 찾으므로(2-3의 번호 방식) 고친 내용이 바로 열람 화면에 보인다.

### 1-9. `main.jsx` — 진입 컴포넌트 교체

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

`<a href="...">`를 그대로 클릭하면 브라우저가 문서를 새로 받아오면서 **리액트 상태가 전부 초기화**된다. 이번 실습의 네비·목록 링크가 전부 `preventDefault` + 콜백 조합인 이유다.

```jsx
// 콜백 방식 — 상태 전환 (이번 실습)
<a href="/" onClick={(e) => { e.preventDefault(); props.onChangeMode("list"); }}>목록</a>

// 라우터 방식 — 주소 전환 (day04)
<Link to="/read/3">글 제목</Link>
```

시안에서 옮겨 온 `<a>` 태그는 이 처리를 붙이는 순간부터 진짜 SPA 부품이 된다. 라우터로 넘어가면 같은 자리를 `Link`/`NavLink`가 대신한다.

### 2-2. mode 문자열보다 한 단계 위 — 객체로 화면 표 만들기

`if/else if`가 길어지면 mode → 부품 대응을 객체 하나로 정리할 수 있다.

```jsx
const screens = {
  list:  { title: "게시판-목록", nav: <NavList ... />,  article: <ArticleList ... /> },
  view:  { title: "게시판-열람", nav: <NavView ... />,  article: <ArticleView ... /> },
  write: { title: "게시판-쓰기", nav: <NavWrite ... />, article: <ArticleWrite ... /> },
  edit:  { title: "게시판-수정", nav: <NavEdit ... />,  article: <ArticleEdit ... /> },
};
const screen = screens[mode];
```

분기가 데이터가 되면 화면을 추가할 때 객체에 한 줄만 늘리면 된다. day04의 라우트 표(`<Route path element />`)가 하는 일과 같은 발상이라, 이 모양이 익숙해지면 라우터로 넘어가는 것도 자연스럽다.

### 2-3. 번호를 올릴까, 객체를 올릴까

목록 → 열람으로 "무엇을 열었는지" 전달하는 방법이 두 가지 있고, 이번 실습은 후자다.

| 방식 | 흐름 | 특징 |
| --- | --- | --- |
| 객체 전체를 상태로 | `setSelectRow(row)` → 그대로 내려줌 | 찾는 수고가 없다. day05 외부 API 실습에서 쓴 방식 |
| **번호만 상태로 (지금)** | `setNo(row.no)` → 렌더링 때마다 배열에서 검색 | 상태가 원시값 하나라 가볍고, **글이 수정돼도 항상 최신 배열에서 다시 찾으므로 사본이 낡을 걱정이 없다** |

번호 방식은 나중에 라우터의 `/read/:no` + `useParams`로 옮길 때도 모양이 그대로다 — 주소에 실을 수 있는 건 객체가 아니라 번호이기 때문이다. 검색 반복문은 `find`로 줄일 수 있다: `boardData.find((row) => row.no === no)`.

### 2-4. 불변 업데이트 삼형제 — 추가·삭제·수정

배열 상태는 **주소값이 바뀌어야 재렌더링**되므로, 세 연산 모두 "새 배열을 만들어 교체"가 기본형이다.

```jsx
// 추가 — 스프레드 (1-6과 같은 결과)
setBoardData([...boardData, addBoardData]);

// 삭제 — filter (1-7의 for문과 같은 결과)
setBoardData(boardData.filter((row) => row.no !== no));

// 수정 — map (editAction의 for + break와 같은 결과)
setBoardData(boardData.map((row) => (row.no === no ? editedRow : row)));
```

`for` + `push`로 풀어 쓴 코드와 배열 메소드 한 줄은 같은 일을 한다. 풀어 쓴 쪽으로 원리를 익히고, 익숙해지면 메소드 쪽으로 줄이는 순서가 자연스럽다.

### 2-5. 입력칸의 세 가지 다루기 — 비제어 · ref · 제어

이번 실습에 폼 데이터를 읽는 방식이 여러 개 등장했으니 한 자리에 정리해 둔다.

| 방식 | 읽는 법 | 등장 |
| --- | --- | --- |
| 비제어 + `name` | 제출 시 `e.target.이름.value` | 작성 폼 (day03 방식) |
| 비제어 + `ref` | `inputRef.current.value` | 비밀번호 확인 (day07 useRef) |
| 제어 컴포넌트 | `value={state}` + `onChange` | 수정 폼 (`ArticleEdit`) |

주의할 일반 규칙 하나 — **입력칸에 `value`를 지정하면 그 순간부터 리액트가 값의 주인**이 되어, `onChange`로 상태를 갱신해 주지 않으면 타이핑이 화면에 반영되지 않는다. 초기값만 채우고 이후 입력은 브라우저에 맡기려면 `defaultValue`를 쓰고, 검증·글자수 세기처럼 입력을 실시간으로 다루려면 `value` + `onChange` 짝을 완성한다.

### 2-6. 상태 변경은 이벤트 핸들러에서 끝내기

컴포넌트 함수 본문은 화면을 계산하는 자리라(day05 생명주기에서 정리), **`setXXX`는 이벤트 핸들러나 `useEffect` 안에서 부르는 편이 안전하다.** 렌더링 도중 상태가 바뀌면 재렌더링이 곧바로 이어져 흐름을 따라가기 어려워진다. 삭제처럼 "화면 없이 처리만 하는 일"도 mode 분기 대신 확인 창을 띄운 그 이벤트 핸들러 안에서 배열 교체까지 끝내는 형태로 옮길 수 있다 — 콜백에 `deleteAction(no)`을 내려주는 모양이 추가(`writeAction`)·수정(`editAction`)과도 나란해진다.

## 3. 더 나아가 알면 좋은 것

### 3-1. mode 전환 vs 라우터 전환

같은 게시판을 두 방식으로 만들 수 있다.

| | mode 상태 방식 (지금) | 라우터 방식 (day04) |
| --- | --- | --- |
| 화면 전환 | `setMode(...)` | `<Link to>` / `useNavigate` |
| 주소창 | 안 바뀜 | `/`, `/write`, `/read/3`처럼 바뀜 |
| 새로고침·북마크 | 항상 첫 화면으로 | 보던 화면 유지 |
| 뒤로 가기 | 페이지 이탈 | 이전 화면으로 |

mode 방식은 구조가 단순해 컴포넌트 분해와 상태 흐름을 익히기 좋고, 실제 서비스에서는 주소가 화면을 대표해야 하므로 라우터 방식으로 옮겨 간다. `/read/:no` 동적 세그먼트와 `useParams`로 글 번호를 주소에서 꺼내는 것이 다음 단계다 — `no`만 상태로 올린 지금 구조(2-3)가 그대로 이식된다.

### 3-2. 서버 연동으로 가는 길

지금 하드코딩된 `boardData`는 스프링 쪽 수업에서 만든 게시판 API와 만날 자리다. 목록 조회는 `useEffect(…, [])` + `axios.get`, 등록은 `writeAction` 안의 배열 추가가 `axios.post` 후 재조회로, 삭제는 `axios.delete`, 수정은 `axios.put`으로 바뀐다 — **CRUD 네 동작의 자리가 이미 콜백 하나씩으로 나뉘어 있어서**, 몸통만 통신 코드로 갈아끼우면 된다. 프론트(2026_React)와 백엔드(2026B_Spring)가 같은 게시판 도메인으로 수렴하는 중이다.

### 3-3. 다음에 볼 키워드

- `editAction`의 `for` + `break`를 `map` 한 줄로 줄이기 (2-4의 합류점)
- `useReducer` — mode·no·nextNo·boardData처럼 얽힌 상태 여러 개를 액션으로 묶기
- `Context` — `onChangeMode`를 여러 층 내려보내는 props drilling 줄이기
- `<Outlet>` + 중첩 라우트로 게시판 레이아웃 만들기 (day04 복습)
- 목록 페이징(`slice` 또는 서버 `params`)과 정렬
- 입력 검증 (`trim()`, 빈 값 막기)과 `react-hook-form`

## 실습 파일

- `KDT_2026/2026_React/src/example/day06/종합실습/skin_board.html` — 게시판 세 화면(목록·열람·작성)의 순수 HTML 시안
- `KDT_2026/2026_React/src/example/day06/종합실습/index.css` — 시안의 `<style>`을 옮긴 전역 CSS
- `KDT_2026/2026_React/src/example/day06/종합실습/App.jsx` — `boardData`·`mode`·`no`·`nextNo` 상태와 다섯 분기(list·view·write·delete·edit)
- `KDT_2026/2026_React/src/example/day06/종합실습/components/article/ArticleList.jsx` · `ArticleView.jsx` · `ArticleWrite.jsx` · `ArticleEdit.jsx` — 본문 4종
- `KDT_2026/2026_React/src/example/day06/종합실습/components/navigation/NavList.jsx` · `NavView.jsx` · `NavWrite.jsx` · `NavEdit.jsx` — 네비 4종
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
