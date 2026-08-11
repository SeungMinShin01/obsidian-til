---
출처: Claude 분석
원본: KDT_2026/2026_FE/day13, Note/day/day13
작성일: 2026-08-10
tags: [javascript, day13, localStorage, 쿼리스트링, setInterval]
---

# JS day13 — 웹 스토리지와 인터벌

> 실습 파일: `day13/exam/exam1.js`(스토리지), `exam2.js`(쿼리스트링·인터벌), `Note/day/day13`, `day13/new/`, `day13/practice/interval/`
> 허브: [[JavaScript MOC]] · 이전: [[JS day12 제품 사원 관리 CRUD]] · 다음: [[JS day14 게시판 CRUD]]

## 1. 배운 내용

### 1-1. 왜 웹 스토리지가 필요한가

흐름을 정리하면 이렇습니다.
> 브라우저는 HTML을 렌더링한다. F5(새로고침)하면 재요청·재렌더링하므로 **JS 변수가 전부 초기화된다.**
> 그래서 백엔드가 필요하다. 또는 브라우저 스토리지를 사용한다.

### 1-2. 세션 스토리지 vs 로컬 스토리지

| | 세션 스토리지 | 로컬 스토리지 |
| --- | --- | --- |
| 유지 | 브라우저(탭) 종료 시 삭제 | 삭제 전까지 영구 |
| 탭 간 공유 | X | O (같은 도메인) |
| 용도 | 임시 입력값, 1회성 상태 | 자동 로그인, 설정, 게시판 |

```javascript
localStorage.setItem("key", value);
localStorage.getItem("key");        // 없으면 null
localStorage.removeItem("key");     // 특정 키 삭제
localStorage.clear();               // 전체 삭제
```

확인 경로: **F12 → Application → Local Storage / Session Storage → 도메인**

특정 키만 지울 때는 `.remove()`가 아니라 **`.removeItem('key')`** 입니다. 이름이 길어서 자주 헷갈립니다.

### 1-3. 스토리지는 문자열만 저장합니다

```javascript
JSON.stringify(객체)   // 객체 → 문자열
JSON.parse(문자열)     // 문자열 → 객체
```

```javascript
sessionStorage.setItem("회원객체", JSON.stringify({ name: "유재석", age: 40 }));
let 회원객체 = JSON.parse(sessionStorage.getItem("회원객체"));
```

`JSON.stringify` 없이 객체를 저장하면 `"[object Object]"`라는 문자열이 들어갑니다.

### 1-4. 쿼리스트링 — 페이지 간 데이터 전달

```
list.html?no=3&page=1
URL ? 매개변수명=값 & 매개변수명=값
```

```javascript
const url = new URLSearchParams(location.search);
const no = url.get("no");      // "3"  ← 항상 문자열!
const page = url.get("page");
```

**페이지 전환 2가지**
```html
<a href="view.html?no=3">보기</a>
```
```javascript
location.href = "view.html?no=3";
```

### 1-5. 인터벌 — 주기적 반복

```javascript
let param = setInterval(함수명, 밀리초);   // 1000 = 1초
clearInterval(param);                     // 종료
```

**사용처**: 타이머(시계, 인증시간), CSS 이미지 슬라이드

**카운터**
```javascript
let value = 0;
function 증가함수() {
  value += 1;
  document.querySelector("#box1").innerHTML = value;
}
setInterval(증가함수, 1000);
```

**시계**
```javascript
function 시계함수() {
  let today = new Date();
  let hour = today.getHours();
  let min = today.getMinutes();
  let second = today.getSeconds();
  let time = `${hour} : ${min} : ${second < 10 ? "0" + second : second}`;
  document.querySelector("#box2").innerHTML = time;
}
setInterval(시계함수, 1000);
```

`second < 10 ? "0" + second : second` — 한 자리 수 앞에 0을 붙이는 삼항 연산자 활용입니다.

### 1-6. day13/new, practice/interval — list/view/write 3종

`write.html/js`, `list.html/js`, `view.html/js` 구조를 처음 만들어본 날입니다. 여기서 익힌 흐름이 [[JS day14 게시판 CRUD]] 에서 완성됩니다.

## 2. 추가로 알면 좋은 활용법

### 2-1. `getItem`은 null을 반환합니다

```javascript
let list = localStorage.getItem("boardList");
if (list == null) list = [];
else list = JSON.parse(list);
```

이 5줄이 파일마다 반복됩니다. 한 줄로 줄일 수 있습니다.
```javascript
const list = JSON.parse(localStorage.getItem("boardList") ?? "[]");
```

`??`(nullish 병합)를 쓰면 `null`/`undefined`일 때만 기본값이 들어갑니다. → [[JS day03 자료형과 연산자]]

### 2-2. 시간 표시 개선

```javascript
`${hour} : ${min} : ${second < 10 ? "0" + second : second}`
```

시·분도 한 자리면 어색합니다. `padStart`를 쓰면 전부 해결됩니다.
```javascript
const pad = (n) => String(n).padStart(2, "0");
const time = `${pad(hour)}:${pad(min)}:${pad(second)}`;
```

더 간단하게는 브라우저 내장 포맷터를 씁니다.
```javascript
new Date().toLocaleTimeString("ko-KR");   // "오후 2:30:15"
```

### 2-3. `setInterval` 중복 실행 방지

```javascript
let timeInter;
function 타이머시작() {
  timeInter = setInterval(타이머함수, 1000);   // 버튼을 두 번 누르면 2배속!
}
```

```javascript
function 타이머시작() {
  if (timeInter) return;             // 이미 돌고 있으면 무시
  timeInter = setInterval(타이머함수, 1000);
}
function 타이머정지() {
  clearInterval(timeInter);
  timeInter = null;                  // 반드시 초기화
}
```

`clearInterval`만 하고 변수를 `null`로 안 만들면 다음 검사에서 또 걸립니다.

### 2-4. `setInterval`은 정확히 1초가 아닙니다

브라우저가 바쁘면 밀립니다. 시계는 매번 `new Date()`를 읽으니 문제없지만, **경과 시간 카운트는 오차가 누적**됩니다.

```javascript
const start = Date.now();
setInterval(() => {
  const 경과 = Math.floor((Date.now() - start) / 1000);   // 절대 시각 기준
}, 1000);
```

탭이 백그라운드로 가면 브라우저가 인터벌을 1초 이상으로 늦추기도 합니다.

### 2-5. 쿼리스트링 값은 문자열입니다

```javascript
const no = url.get("no");           // "3"
boardList.find(b => b.no === no);   // no는 숫자 3 → false! 못 찾음
boardList.find(b => b.no === Number(no));   // 정답
```

`==`를 쓰면 우연히 동작하지만 `===`를 쓰면 즉시 드러납니다. [[JS day14 게시판 CRUD]] 에서 반드시 확인할 부분입니다.

값이 없으면 `null`이 반환됩니다.
```javascript
const page = Number(url.get("page") ?? 1);
```

### 2-6. 한글·특수문자는 인코딩

```javascript
location.href = `search.html?q=${encodeURIComponent("검색어 & 특수문자")}`;
const q = url.get("q");   // URLSearchParams가 자동 디코딩
```

`&`, `=`, `?`, 공백이 들어가면 쿼리스트링이 깨집니다.

## 3. 더 나아가 알면 좋은 것

### 3-1. localStorage의 한계

| 한계 | 실무 해법 |
| --- | --- |
| 용량 5~10MB | 서버 DB |
| 문자열만 저장 | JSON (지금 방식) |
| 동기 API (많으면 렌더링 블로킹) | IndexedDB |
| 브라우저·기기 간 공유 불가 | 서버 + 로그인 |
| 보안 없음 (F12로 누구나 열람) | HttpOnly 쿠키, 서버 세션 |

**"내 PC의 이 브라우저에서만 보이는 게시판"** 이 현재 상태입니다. 다른 기기에서 열면 글이 하나도 없습니다.

이게 백엔드가 필요한 이유이고, `2026B_BE`에서 Java와 MySQL을 배우는 이유입니다. → [[Java day09 ArrayList]]

### 3-2. `storage` 이벤트 — 탭 간 동기화

```javascript
window.addEventListener("storage", (e) => {
  if (e.key === "boardList") location.reload();   // 다른 탭에서 글을 쓰면 자동 갱신
});
```

localStorage가 탭 간 공유된다는 성질의 실전 활용입니다.

### 3-3. `setTimeout` vs `setInterval`

```javascript
setTimeout(fn, 1000);    // 1초 뒤 한 번만
setInterval(fn, 1000);   // 1초마다 계속

// setTimeout 재귀 — 이전 작업이 끝난 뒤 다음을 예약 (밀림 방지)
function tick() {
  // 작업
  setTimeout(tick, 1000);
}
tick();
```

무거운 작업을 인터벌로 돌리면 이전 작업이 안 끝났는데 다음이 시작될 수 있습니다. 재귀 `setTimeout`이 안전합니다.

### 3-4. 이미지 슬라이드 (인터벌 실전)

```javascript
const imgs = document.querySelectorAll(".slide");
let idx = 0;

setInterval(() => {
  imgs.forEach(img => img.classList.remove("active"));
  idx = (idx + 1) % imgs.length;      // 나머지 연산으로 순환
  imgs[idx].classList.add("active");
}, 3000);
```

`% imgs.length`가 배열 끝에서 0으로 돌아가게 합니다. → [[Java day03 연산자]]

CSS와 조합하면 페이드 효과가 붙습니다.
```css
.slide { opacity: 0; transition: opacity .5s; }
.slide.active { opacity: 1; }
```
→ [[CSS day14 position과 가상요소]]

## 실습 파일

- `2026_FE/Note/day/day13`
- `2026_FE/day13/exam/exam1.js`, `exam2.js`, `exam1.html`, `exam2.html`
- `2026_FE/day13/new/list.js`, `list.html`, `view.js`, `view.html`, `write.js`, `wirte.html`
- `2026_FE/day13/practice/interval/list.js`, `view.js`, `write.js`
- `2026_FE/day13/practice/practice10.js`, `practice10.html`

## 관련 노트

[[JavaScript MOC]] · [[JS day12 제품 사원 관리 CRUD]] · [[JS day14 게시판 CRUD]] · [[JS day07 객체]] · [[SQL day03 DML과 조인]]
