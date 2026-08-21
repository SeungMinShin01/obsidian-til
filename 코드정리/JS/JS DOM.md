---
출처: Claude 분석
작성일: 2026-08-21
tags: [코드정리]
---

# JS DOM

> 상위: [[JS]]
> 세부: [[JS 이벤트 심화]] · [[JS DOM 조작 심화]]

## 요소 선택

```javascript
const title = document.querySelector("#titleInput");
const rows = document.querySelectorAll(".row");
```

- `querySelector`는 CSS 선택자로 **첫 번째** 요소 하나를, `querySelectorAll`은 전부(NodeList)를 가져온다
- 선택자는 CSS와 똑같이 쓴다: `#아이디` `.클래스` `태그` `ul > li`
- 없는 요소를 선택하면 null이 오고, 거기에 `.value`를 읽으면 터진다 — 아이디 오타부터 의심한다

## 읽기·쓰기 — innerHTML · textContent · value

```javascript
viewTitle.innerHTML = post.title;
viewTitle.textContent = post.title;
const input = titleInput.value;
titleInput.value = "";
```

- `<div>` 같은 표시 요소엔 `innerHTML`(태그 해석) 또는 `textContent`(글자 그대로), `<input>`·`<textarea>`엔 **`.value`**다 — 조회 화면과 수정 화면에서 이 구분을 틀리면 값이 안 보인다
- 사용자 입력을 innerHTML에 그대로 넣으면 `<script>` 주입(XSS) 위험이 있다. 표시만 할 거면 textContent가 안전하다
- 입력창 비우기는 `value = ""`

## 목록 그리기

```javascript
let html = "";
for (const b of boardList) {
    html += `<tr><td>${b.no}</td><td><a href="view.html?no=${b.no}">${b.title}</a></td></tr>`;
}
tbody.innerHTML = html;

tbody.innerHTML = boardList
    .map(b => `<tr><td>${b.no}</td><td>${b.title}</td></tr>`)
    .join("");
```

- 문자열을 다 만든 뒤 **마지막에 한 번만** innerHTML에 대입한다. 반복마다 `innerHTML +=`을 하면 매번 전체를 다시 그려 느리다
- 템플릿 리터럴(백틱)의 `${}`에 값을 끼워 넣는다. 목록→상세 연결은 `?no=` 쿼리스트링을 링크에 붙이는 것으로 만든다
- map + join 버전이 같은 일의 함축형이다

## 이벤트 걸기

```javascript
button.addEventListener("click", writefunc);

form.addEventListener("submit", e => {
    e.preventDefault();
    save();
});
```

- `addEventListener("이벤트명", 함수)` — click, input, change, submit, keydown이 주로 쓰인다
- HTML에 `onclick="writefunc()"`을 쓰는 방식도 있지만 JS 쪽에서 거는 게 구조가 깨끗하다
- 폼의 submit은 기본 동작(새로고침)이 있어서 `preventDefault()`로 막고 내 로직을 돌린다

## 페이지 이동과 쿼리스트링

```javascript
location.href = "list.html";

const url = new URLSearchParams(location.search);
const no = Number(url.get("no"));
```

- `location.href` 대입이 페이지 이동이다(등록 후 목록으로)
- `URLSearchParams`로 `?no=3`에서 값을 꺼낸다. **문자열로 오므로 Number 변환**이 관용이다 — `===` 비교가 이것 때문에 틀어진다
