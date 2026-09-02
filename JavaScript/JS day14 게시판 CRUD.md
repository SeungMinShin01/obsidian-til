---
출처: Claude 분석
원본: KDT_2026/2026_FE/day14/test
작성일: 2026-08-10
tags: [학습, javascript]
---

# JS day14 — 게시판 CRUD

> 실습 파일: `day14/test/note`(설계 문서), `write.js`, `list.js`, `view.js`, `update.js`
> 허브: [[JavaScript MOC]] · 이전: [[JS day13 웹 스토리지와 인터벌]] · 다음: JS 과제 LevelUP과 게시판

## 1. 배운 내용

### 1-1. 설계를 먼저 쓴 파일 — test/note

`day14/test/note` 에 **구현 전 4개 화면의 로직을 글로 먼저 서술**해뒀습니다.

이 습관 하나가 개발 실력을 가장 크게 좌우합니다. 코드를 쓰기 전에 "무엇을 어떤 순서로"를 적어두면 막히는 지점이 줄고, 나중에 읽을 때도 의도가 남습니다.

### 1-2. 5개 화면 구조

```
write.html/js   →  글 작성   (Create)
list.html/js    →  목록      (Read)
view.html/js    →  상세      (Read) + 삭제(Delete) + 수정 진입
update.html/js  →  수정      (Update)
```

### 1-3. write.js — 글 작성

`note` 에 적어둔 6단계 그대로입니다.

```javascript
function writefunc() {
  // 1. value 가져오기
  const title = document.querySelector("#titleInput").value;
  const content = document.querySelector("#contentInput").value;
  const pwd = document.querySelector("#pwdInput").value;

  // 2. value 객체화 (단축 속성명)
  const object = { title, content, pwd };

  // 3. localStorage에서 배열 가져오기
  let boardList = localStorage.getItem("boardList");
  if (boardList == null) boardList = [];
  else boardList = JSON.parse(boardList);

  // 4. no 속성 추가 — 마지막 인덱스의 no + 1
  object.no = boardList.length == 0 ? 1 : boardList[boardList.length - 1].no + 1;
  boardList.push(object);

  // 5. localStorage에 저장
  localStorage.setItem("boardList", JSON.stringify(boardList));

  // 6. 알림 및 페이지 이동
  alert("등록 완료");
  location.href = "list.html";
}
```

**글번호 자동 증가**가 핵심입니다. `AUTO_INCREMENT`를 JS로 흉내낸 것입니다. → SQL day02 테이블과 제약조건

**막힌 지점과 해결 과정을 주석으로 남겨두면** 나중에 같은 자리에서 다시 막혔을 때 큰 도움이 됩니다.

### 1-4. list.js — 목록

```javascript
readfunc();   // JS가 열릴 때 최초 1회 실행

function readfunc() {
  // 배열 가져오기
  let boardList = localStorage.getItem("boardList");
  if (boardList == null) boardList = [];
  else boardList = JSON.parse(boardList);

  let html = "";
  let tbody = document.querySelector("#tableTbody");

  for (let i = 0; i < boardList.length; i++) {
    const object = boardList[i];
    html += `<tr><td>${object.no}</td><td><a href="view.html?no=${object.no}">
    ${object.title}</a></td></tr>`;
  }
  tbody.innerHTML = html;
}
```

**제목을 `<a>`로 감싸고 `?no=` 쿼리스트링을 붙이는 것**이 목록 → 상세 연결의 핵심입니다. 이 한 줄이 두 페이지를 잇습니다.

`html` 문자열을 다 만든 뒤 마지막에 한 번만 `innerHTML`에 대입한 구조가 좋습니다.

### 1-5. view.js — 상세 조회

```javascript
viewfunc();

function viewfunc() {
  const url = new URLSearchParams(location.search);
  let selectNo = url.get("no");

  let boardList = localStorage.getItem("boardList");
  if (boardList == null) boardList = [];
  else boardList = JSON.parse(boardList);

  let title = document.querySelector("#viewTitle");
  let content = document.querySelector("#contentTitle");

  for (let i = 0; i < boardList.length; i++) {
    let object = boardList[i];
    if (object.no == selectNo) {
      title.innerHTML = object.title;
      content.innerHTML = object.content;
    }
  }
}
```

URL에서 번호를 꺼내 → 배열에서 찾아 → 화면에 출력하는 3단계입니다.

### 1-6. view.js — 삭제

```javascript
function deletefunc() {
  const url = new URLSearchParams(location.search);
  let selectNo = url.get("no");

  let boardList = localStorage.getItem("boardList");
  if (boardList == null) boardList = [];
  else boardList = JSON.parse(boardList);

  for (let i = 0; i < boardList.length; i++) {
    let object = boardList[i];
    if (object.no == selectNo) {
      let confirm = prompt("비밀번호 입력");
      if (confirm == object.pwd) {
        boardList.splice(i, 1);
        localStorage.setItem("boardList", JSON.stringify(boardList));
        alert("삭제 성공");
        location.href = "list.html";
      } else alert("삭제 실패 비밀번호 불일치");
    }
  }
}
```

**찾기 → 비밀번호 확인 → `splice` → 저장 → 이동** 5단계입니다. `note`에 설계한 순서 그대로입니다.

### 1-7. update.js — 기존 값 채우기와 수정

```javascript
updatereadfunc();   // 페이지가 열리면 기존 정보를 폼에 채움

function updatereadfunc() {
  const url = new URLSearchParams(location.search);
  let selectNO = url.get("no");

  let boardList = localStorage.getItem("boardList");
  if (boardList == null) boardList = [];
  else boardList = JSON.parse(boardList);

  let newTitle = document.querySelector("#updateTitle");
  let content = document.querySelector("#updateContent");

  for (let i = 0; i < boardList.length; i++) {
    let object = boardList[i];
    if (object.no == selectNO) {
      newTitle.value = object.title;      // innerHTML이 아니라 value!
      content.value = object.content;
    }
  }
}
```

**`<input>`·`<textarea>`에는 `innerHTML`이 아니라 `.value`** 입니다. 조회 화면(`view.js`)은 `<div>`에 출력하므로 `innerHTML`, 수정 화면은 입력창에 채우므로 `.value` — 두 화면에서 정확히 구분해 써야 합니다. → JS day11 DOM 조작

```javascript
function updatefunc() {
  // ... 배열 가져오기
  for (let i = 0; i < boardList.length; i++) {
    let object = boardList[i];
    if (object.no == selectNO) {
      if (title.value != "") {
        boardList[i].title = title.value;
        boardList[i].content = content.value;
        boardList[i].pwd = pwd.value;

        localStorage.setItem("boardList", JSON.stringify(boardList));
        alert("수정 성공");
        location.href = "list.html";
      } else alert("비밀번호 미입력");
    }
  }
}
```

**수정 화면에 기존 값을 미리 채우는 것**이 UX의 핵심입니다. 빈 폼이 뜨면 사용자가 전부 다시 써야 합니다.

## 2. 추가로 알면 좋은 활용법

### 2-1. localStorage 코드를 common.js로 추출

같은 5줄이 write / list / view / update **4개 파일에 반복**됩니다.

```javascript
// common.js
const KEY = "boardList";

function getBoardList() {
  return JSON.parse(localStorage.getItem(KEY) ?? "[]");
}

function saveBoardList(list) {
  localStorage.setItem(KEY, JSON.stringify(list));
}

function findBoard(no) {
  return getBoardList().find(b => b.no === Number(no));
}

function findBoardIndex(no) {
  return getBoardList().findIndex(b => b.no === Number(no));
}

function getQueryNo() {
  return Number(new URLSearchParams(location.search).get("no"));
}
```

```html
<script src="common.js"></script>
<script src="write.js"></script>
```

"서로 다른 .js 파일이 동일한 HTML에 포함되면 코드 공유가 가능하다" 는 원리를 그대로 쓰는 것입니다.

이게 사실상 **Repository 패턴**이고, Java day07 메소드와 미니프로젝트 의 `OverallRepository`와 역할이 똑같습니다.

리팩터링 후 `write.js`
```javascript
function writefunc() {
  const title = document.querySelector("#titleInput").value.trim();
  const content = document.querySelector("#contentInput").value.trim();
  const pwd = document.querySelector("#pwdInput").value;

  if (!title)   { alert("제목을 입력하세요."); return; }
  if (!content) { alert("내용을 입력하세요."); return; }
  if (pwd.length < 4) { alert("비밀번호는 4자 이상이어야 합니다."); return; }

  const list = getBoardList();
  const no = list.length === 0 ? 1 : list[list.length - 1].no + 1;
  list.push({ no, title, content, pwd, createdAt: new Date().toISOString() });
  saveBoardList(list);

  alert("등록 완료");
  location.href = "list.html";
}
```

### 2-2. 쿼리스트링 타입 문제

```javascript
const no = url.get("no");           // "3" (문자열)
list.find(b => b.no === no);        // false! 못 찾음
list.find(b => b.no === Number(no)); // 정답
```

`==`를 쓰면 우연히 동작하지만, 나중에 `===`로 바꾸는 순간 조용히 깨집니다. **처음부터 `Number()` 변환**을 습관화하세요.

### 2-3. `no`와 `index`는 다릅니다

```javascript
list[no];                                 // 위험!
const idx = list.findIndex(b => b.no === Number(no));
if (idx === -1) { alert("게시물이 없습니다."); return; }
list.splice(idx, 1);
```

3번 글을 지우면 4번 글의 **배열 인덱스는 당겨지지만 `no`는 4로 유지**됩니다. 반드시 `findIndex`로 찾아야 합니다.

### 2-4. `innerHTML +=` 대신 한 번에

```javascript
// 나쁨 — 반복마다 전체 재렌더링
for (const b of list) tbody.innerHTML += `<tr>...</tr>`;

// 좋음 — 문자열을 다 만들고 한 번만
tbody.innerHTML = list
  .map(b => `<tr><td>${b.no}</td><td><a href="view.html?no=${b.no}">${b.title}</a></td></tr>`)
  .join("");
```

→ JS day11 DOM 조작

### 2-5. XSS 대비

```javascript
tbody.innerHTML = `<td>${b.title}</td>`;   // 제목에 <script>를 넣으면?
```

학습 목적이라면 괜찮지만, 실무에서는 이스케이프가 필요합니다.
```javascript
const escape = (s) => String(s).replace(/[&<>"']/g,
  c => ({ "&":"&amp;", "<":"&lt;", ">":"&gt;", '"':"&quot;", "'":"&#39;" }[c]));

tbody.innerHTML = `<td>${escape(b.title)}</td>`;
```

또는 `createElement` + `textContent`를 씁니다. → JS day11 DOM 조작

### 2-6. 비밀번호를 평문으로 저장하지 마세요

```javascript
const object = { title, content, pwd };   // F12 → Application에서 그대로 보임
```

```javascript
async function hash(text) {
  const buf = await crypto.subtle.digest("SHA-256", new TextEncoder().encode(text));
  return [...new Uint8Array(buf)].map(b => b.toString(16).padStart(2, "0")).join("");
}
```

실제로는 **비밀번호 검증을 서버에서** 합니다. 클라이언트 검증은 우회가 너무 쉽기 때문입니다.

## 3. 더 나아가 알면 좋은 것

### 3-1. 기능 추가 아이디어

전부 배열 메소드로 풀립니다.

```javascript
// 검색
const 결과 = list.filter(b => b.title.includes(검색어));

// 최신순 정렬
list.sort((a, b) => b.no - a.no);

// 페이지네이션
const 페이지크기 = 10;
const 현재페이지 = list.slice((page - 1) * 페이지크기, page * 페이지크기);

// 조회수
board.views = (board.views ?? 0) + 1;

// 작성일
b.createdAt = new Date().toISOString();
new Date(b.createdAt).toLocaleDateString("ko-KR");
```

### 3-2. 백엔드 연결로 가는 길

```javascript
// 지금
function getBoardList() {
  return JSON.parse(localStorage.getItem(KEY) ?? "[]");
}

// 나중
async function getBoardList() {
  const res = await fetch("/api/boards");
  return res.json();
}

async function saveBoard(board) {
  await fetch("/api/boards", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(board)
  });
}
```

**`common.js`만 고치면 나머지 코드는 그대로입니다.** 이게 계층 분리의 이득입니다.

| localStorage | REST API | SQL |
| --- | --- | --- |
| `getItem` | `GET /boards` | `SELECT` |
| `setItem` (추가) | `POST /boards` | `INSERT` |
| `setItem` (수정) | `PUT /boards/3` | `UPDATE` |
| `splice` | `DELETE /boards/3` | `DELETE` |

→ SQL day03 DML과 조인

### 3-3. 백엔드 버전과 비교하기

Java day06 생성자와 콘솔 게시판 의 `OverallController.java`와 나란히 놓고 보세요.

| | JS (day14) | Java (day06) |
| --- | --- | --- |
| 저장소 | `localStorage` 배열 | `Post[100]` 배열 |
| 빈 자리 | 배열이 가변이라 불필요 | `posts[i] == null` |
| 번호 | `마지막.no + 1` | (미구현) |
| 화면 | HTML 5개 | 콘솔 메뉴 |
| 데이터 구조 | 객체 `{ }` | `Post` 클래스 |

**같은 게시판을 다른 층에서 만든 것**입니다. 두 코드를 비교하면 CRUD의 본질이 보입니다.

### 3-4. React로 가면

5개 HTML 파일이 컴포넌트 몇 개로 통합되고, `location.href` 대신 라우터가, `innerHTML` 대신 JSX가 들어옵니다. 지금 손으로 만든 경험이 있어야 그 편리함이 체감됩니다.

## 실습 파일

- `2026_FE/day14/test/note` (설계 문서)
- `2026_FE/day14/test/write.js`, `list.js`, `view.js`, `update.js`
- `2026_FE/day14/test/write.html`, `list.html`, `view.html`, `update.html`

## 관련 노트

[[JavaScript MOC]] · [[JS day13 웹 스토리지와 인터벌]] · JS 과제 LevelUP과 게시판 · Java day06 생성자와 콘솔 게시판 · CSS day14 position과 가상요소
