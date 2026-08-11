---
출처: Claude 분석
원본: KDT_2026/2026_FE/day11, Note/day/day11
작성일: 2026-08-10
tags: [javascript, day11, DOM, 이벤트, XSS]
---

# JS day11 — DOM 조작

> 실습 파일: `day11/exam/exam1.js`, `Note/day/day11`, `day11/practice/exam0.js`, `practice7.js`
> 허브: [[JavaScript MOC]] · 이전: [[JS day10 함수]] · 다음: [[JS day12 제품 사원 관리 CRUD]]

## 1. 배운 내용

### 1-1. DOM이란

**D**ocument **O**bject **M**odel — HTML 문서를 객체로 표준화한 모델입니다.

`exam1.js` 주석의 설명이 핵심을 정확히 짚습니다.
> HTML은 객체가 없다. 즉 변수·연산·함수가 없어서 제어·조작이 불가능하다.
> JS는 객체가 있다. 즉 **JS가 HTML을 제어·조작한다.**

`document`는 브라우저가 제공하는 **내장 객체**로, JS가 HTML 구조를 객체로 갖고 있는 형태입니다.

```javascript
console.log(document);   // HTML 전체 DOM 확인
```

### 1-2. 요소 선택

```javascript
document.querySelector("div")     // 일치하는 첫 1개
document.querySelector(".box2")   // 클래스
document.querySelector("#box3")   // 아이디
document.querySelectorAll("div")  // 일치하는 전부 (NodeList)
```

**CSS 선택자 문법을 그대로 씁니다.** [[CSS day06 선택자와 기본 속성]] 에서 배운 게 여기서 그대로 쓰입니다.

### 1-3. 주요 속성

| 속성 | 용도 | 쓸 수 있는 태그 |
| --- | --- | --- |
| `.innerHTML` | 태그 **사이**의 HTML 읽기·쓰기 | `<div>` `<td>` `<h1>` `<p>` `<span>` |
| `.value` | `value` 속성 읽기·쓰기 | `<input>` `<select>` `<textarea>` |
| `.src` | 이미지 경로 | `<img>` |
| `.style` | 인라인 CSS 대입 | 전부 |
| `.classList` | 클래스 목록 조작 | 전부 |

**핵심 구분**
```html
<div> 여기가 innerHTML </div>       <!-- 닫는 태그 사이가 있음 -->
<input value="여기가 value" />       <!-- 닫는 태그가 없어 "사이"가 없음 -->
```

`<input>`에 `innerHTML`은 안 되고, `<div>`에 `value`는 없습니다.

```javascript
element.classList.add("active");
element.classList.remove("active");
element.classList.toggle("active");   // 있으면 빼고, 없으면 넣기
element.remove();                     // 요소 자체 삭제
```

### 1-4. 실전 3단계 패턴

```javascript
function 등록함수() {
    const 입력값 = document.querySelector(".title").value;  // 1. 가져오기
    const 결과 = 입력값 + "!";                               // 2. 가공
    box2.innerHTML = 결과;                                   // 3. 출력
}
```

거의 모든 DOM 작업이 이 3단계입니다.

## 2. 추가로 알면 좋은 활용법

### 2-1. DOM 객체와 값 구분하기

초보 단계에서 가장 자주 막히는 지점입니다.

```javascript
const 입력마크업 = document.querySelector(".title").value;  // 이미 value를 꺼냄
const 입력받은값 = 입력마크업.value;                        // 문자열에 .value → undefined
```

변수명은 DOM 객체처럼 보이는데 실제로는 **값(문자열)** 이 담겨 있습니다. 문자열에는 `.value`가 없으므로 `undefined`가 나옵니다.

```javascript
function 등록함수() {
  const 입력마크업 = document.querySelector(".title");   // DOM 객체
  const 입력받은값 = 입력마크업.value;                    // 값
  box2.innerHTML = 입력받은값;
}
```

**예방 습관**: DOM 객체를 담는 변수는 `titleEl`, `$title`처럼 접미사를 붙이면 값과 헷갈리지 않습니다.

### 2-2. `.style`을 통째로 대입하면 위험합니다

```javascript
제목마크업.style = "color:red; font-size:5px";   // 기존 인라인 스타일이 전부 날아감
```

```javascript
제목마크업.style.color = "red";
제목마크업.style.fontSize = "5px";               // CSS의 font-size → JS는 카멜케이스
Object.assign(제목마크업.style, { color: "red", fontSize: "5px" });
```

**더 나은 방법** — CSS에 클래스를 정의하고 `classList`로 토글합니다.
```css
.highlight { color: red; font-size: 5px; }
```
```javascript
제목마크업.classList.add("highlight");
```

스타일은 CSS에, 로직은 JS에 — 역할이 분리됩니다. → [[CSS day11 커뮤니티와 예약 사이트]]

### 2-3. `querySelectorAll`은 배열이 아닙니다

```javascript
const divs = document.querySelectorAll("div");
divs.forEach(d => d.style.color = "red");   // forEach는 있음
divs.map(d => d.id);                        // TypeError! map은 없음
[...divs].map(d => d.id);                   // 전개해서 진짜 배열로
```

### 2-4. `innerHTML` vs `textContent` — XSS

```javascript
el.innerHTML = "<b>굵게</b>";     // 태그로 해석됨
el.textContent = "<b>굵게</b>";   // 글자 그대로 출력
```

**사용자 입력을 `innerHTML`에 그대로 넣으면 XSS 취약점이 생깁니다.**

```javascript
const 입력 = '<img src=x onerror="alert(document.cookie)">';
el.innerHTML = 입력;   // 스크립트가 실행됩니다!
el.textContent = 입력; // 안전
```

[[JS day14 게시판 CRUD]] 에서 제목·내용을 `innerHTML`로 출력하고 있는데, 실무라면 `textContent`를 쓰거나 이스케이프 처리를 해야 합니다. **정보처리기사 보안 파트의 XSS가 정확히 이 이야기입니다.**

### 2-5. `onclick` 속성 대신 `addEventListener`

```html
<button onclick="등록함수()">등록</button>   <!-- HTML에 JS가 섞임 -->
```

```javascript
document.querySelector("#btn").addEventListener("click", 등록함수);
```

**장점 4가지**
- HTML과 JS가 분리됨 (관심사 분리)
- 같은 요소에 이벤트 여러 개 등록 가능 (`onclick`은 하나만)
- `removeEventListener`로 해제 가능
- 이벤트 객체 `e`를 받을 수 있음

```javascript
btn.addEventListener("click", (e) => {
  e.preventDefault();      // 기본 동작 막기 (form 전송, a 링크 이동 등)
  console.log(e.target);   // 클릭된 요소
});
```

**자주 쓰는 이벤트**: `click` `input` `change` `submit` `keydown` `mouseover` `scroll` `DOMContentLoaded`

### 2-6. 스크립트 실행 시점

```html
<head>
  <script src="app.js"></script>   <!-- querySelector가 null을 반환 -->
</head>
```

**해결 3가지**
```html
<script src="app.js" defer></script>            <!-- 권장 -->
<body> ... <script src="app.js"></script></body>
```
```javascript
document.addEventListener("DOMContentLoaded", () => { /* 여기서 시작 */ });
```

`day02/exam/exam1.html`처럼 `</body>` 직전에 둔 게 올바른 방식입니다.

## 3. 더 나아가 알면 좋은 것

### 3-1. 동적 요소 생성 3가지

```javascript
// ① innerHTML 문자열 — 간단하지만 느리고 XSS 위험
tbody.innerHTML += `<tr><td>${no}</td></tr>`;

// ② insertAdjacentHTML — 기존 요소를 다시 만들지 않아 빠름
tbody.insertAdjacentHTML("beforeend", `<tr>...</tr>`);

// ③ createElement — 가장 안전
const tr = document.createElement("tr");
const td = document.createElement("td");
td.textContent = title;     // XSS 없음
tr.appendChild(td);
tbody.appendChild(tr);
```

**`innerHTML +=` 는 기존 내용을 전부 지우고 다시 그립니다.** 반복문 안에서 쓰면 매우 느리고, 기존 요소에 걸린 이벤트도 전부 날아갑니다.

```javascript
// 나쁨
for (const item of list) tbody.innerHTML += `<tr>...</tr>`;

// 좋음 — 문자열을 다 만들고 한 번만 대입
tbody.innerHTML = list.map(item => `<tr>...</tr>`).join("");
```

[[JS day14 게시판 CRUD]] 의 `list.js`에 그대로 적용됩니다.

### 3-2. 이벤트 위임

동적으로 만든 요소마다 이벤트를 다는 대신, 부모에 하나만 답니다.

```javascript
tbody.addEventListener("click", (e) => {
  const tr = e.target.closest("tr");
  if (!tr) return;
  location.href = `view.html?no=${tr.dataset.no}`;
});
```

게시판처럼 행이 계속 추가되는 화면에 딱 맞습니다.

### 3-3. `data-*` 속성

```html
<tr data-no="3" data-writer="유재석">
```
```javascript
tr.dataset.no;       // "3"
tr.dataset.writer;   // "유재석"
```

DOM에 데이터를 붙여둘 수 있어 쿼리스트링 없이도 값을 넘길 수 있습니다.

### 3-4. 탐색 메소드

```javascript
el.parentElement;         // 부모
el.children;              // 자식들
el.closest(".card");      // 가장 가까운 조상 중 조건에 맞는 것
el.nextElementSibling;    // 다음 형제
```

### 3-5. 다음 단계 — React

```javascript
// DOM 직접 조작 (지금)
document.querySelector("#count").innerHTML = count;

// React (상태만 바꾸면 화면이 따라옴)
setCount(count + 1);
```

React는 "무엇을 보여줄지"만 선언하면 DOM 갱신을 알아서 해줍니다. 지금 DOM을 손으로 만져보는 경험이 있어야 React가 왜 편한지 체감됩니다.

## 실습 파일

- `2026_FE/Note/day/day11`
- `2026_FE/day11/exam/exam1.js`, `exam1.html`, `exam1.css`
- `2026_FE/day11/practice/exam0.js`, `practice7.js`

## 관련 노트

[[JavaScript MOC]] · [[JS day10 함수]] · [[JS day12 제품 사원 관리 CRUD]] · [[CSS day11 커뮤니티와 예약 사이트]] · [[HTML day04 폼과 테이블]]
