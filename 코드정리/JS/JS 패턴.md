---
출처: Claude 분석
작성일: 2026-08-21
tags: [코드정리]
---

# JS 패턴

> 상위: [[JS]]
> 세부: [[JS 모듈]] · [[JS 디바운스와 쓰로틀]]

게시판·관리화면류를 만들 때 반복해서 쓰는 구조들이다.

## 저장소 함수 분리 — common.js

```javascript
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
```

- write/list/view/update 네 파일에 반복되던 localStorage 코드를 한 파일로 모은다. HTML에서 `<script src="common.js">`를 먼저 읽으면 뒤 스크립트가 공유한다
- 얻는 효과: 저장 방식이 바뀌어도(localStorage→서버) **이 파일만** 고친다. 자바의 DAO와 같은 역할이다
- 키 문자열을 상수 KEY 하나로 모으는 것도 세트다 — 오타로 다른 키에 저장되는 사고를 막는다

## 렌더 함수 — 상태에서 화면을 다시 그린다

```javascript
function render() {
    const list = getBoardList();
    tbody.innerHTML = list
        .map(b => `<tr><td>${b.no}</td><td>${b.title}</td></tr>`)
        .join("");
}

function addPost(post) {
    const list = getBoardList();
    list.push(post);
    saveBoardList(list);
    render();
}
```

- 화면 갱신 코드를 render 하나에 모으고, 데이터가 바뀌는 모든 곳에서 마지막에 render를 부른다
- 얻는 효과: "추가했는데 화면엔 안 보임" 류의 어긋남이 사라진다. 데이터가 진실이고 화면은 그 사본이라는 사고방식 — 리액트의 핵심 아이디어를 손으로 미리 해보는 것이다

## 자동 번호와 식별

```javascript
const no = list.length === 0 ? 1 : list[list.length - 1].no + 1;

const idx = list.findIndex(b => b.no === no);
if (idx === -1) { alert("게시물이 없습니다."); return; }
list.splice(idx, 1);
```

- 새 번호는 "마지막 글 번호 + 1"이다(비었으면 1). SQL의 AUTO_INCREMENT를 손으로 흉내 낸 것이다
- **no와 인덱스는 다르다.** 3번 글을 지우면 뒤 글들의 인덱스는 당겨지지만 no는 그대로다 — 반드시 findIndex로 찾고, -1 검사 후에 조작한다

## 화면 뼈대 — CRUD 4장

```
write.html/js  →  입력값 수집 → 검증 → 객체화 → 저장 → 목록으로 이동
list.html/js   →  전체 읽기 → 목록 렌더 (제목에 ?no= 링크)
view.html/js   →  쿼리스트링 no → find → 표시 / 삭제
update.html/js →  no → find → 폼에 기존 값 채우기(.value) → 수정 저장
```

- 각 화면의 순서를 코드 쓰기 전에 글로 먼저 적는다(설계 문서) — 막히는 지점이 줄고 의도가 남는다
- 수정 화면은 기존 값을 미리 채워야 한다(`input.value = 기존값`). 빈 폼이 뜨면 사용자가 전부 다시 써야 한다

## 검증은 조기 반환으로

```javascript
function writefunc() {
    const title = titleInput.value.trim();
    if (!title) { alert("제목을 입력하세요."); return; }
    if (pwd.length < 4) { alert("비밀번호는 4자 이상"); return; }
    ...
}
```

- 검증 실패를 위에서 하나씩 쳐내고 return한다. 통과한 아래쪽은 정상 케이스만 남는다
- `trim()`으로 공백 입력을 걸러내고, falsy 검사(`!title`)로 빈 값을 잡는다
