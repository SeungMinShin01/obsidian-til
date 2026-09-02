---
출처: Claude 분석
원본: KDT_2026/2026_FE/day10
작성일: 2026-08-10
tags: [학습, css]
---

# CSS day10 — 카메라 강의 사이트

> 실습 파일: `day10/pracitce/practicce2.html`, `practice2.css`, `day10/exam/exam2.css`, `practice0.css`, `assets/`
> 허브: [[CSS MOC]] · 이전: [[CSS day09 카페 키오스크]] · 다음: [[CSS day11 커뮤니티와 예약 사이트]]

## 1. 배운 내용

JS 함수를 배우던 날(JS day10 함수)에 CSS로는 **카메라 강의 사이트**의 뼈대를 잡았습니다.

### 1-1. 3단 구조 + container 패턴

```html
<div id="header">
  <div class="container">
    <img class="headerLogo" src="./assets/logo.png">
  </div>
</div>

<div id="section">
  <img class="mainImg" src="./assets/main_img.png">
  <div class="container">
    <div class="sidebar">
      <div>사진이론</div>
      <div>카메라 동작 이론</div>
      <div>무조건 찍어 보자</div>
      <div>피사체 배경</div>
      <div>조리개와 심도</div>
      <div>카메라 촬영 모드</div>
    </div>
    <div class="section">1</div>
  </div>
</div>

<div id="footer">
  <div class="container">
    <img class="footerLogo" src="./assets/footer_logo.png">
  </div>
</div>
```

**바깥 `#header`/`#section`/`#footer`는 전체 폭, 안쪽 `.container`는 콘텐츠 폭**입니다.

```css
#header  { height: 50px; width: 1280px; }
#section { width: 1280px; }
#footer  { width: 1280px; height: 50px; }

.container {
  margin: 0 auto;        /* 가로 가운데 */
  width: 1080px;
  display: flex;
  justify-content: space-between;
}
```

이 **바깥은 전체 폭, 안쪽은 고정 폭 + `margin: 0 auto`** 구조가 거의 모든 웹사이트의 기본형입니다. 배경색·배경이미지는 바깥이 화면 끝까지 채우고, 글과 이미지는 안쪽에서 가운데 정렬됩니다.

### 1-2. 사이드바 + 본문 비율 배분

```css
.sidebar { width: 18%; }
.section { width: 80%; }
```

`.container`가 `display: flex`이므로 두 자식이 가로로 놓이고, `%`로 폭을 나눕니다. 18 + 80 = 98이라 사이에 2%의 여백이 생기는데, `justify-content: space-between`이 그 여백을 둘 사이로 보냅니다.

### 1-3. 배경 이미지를 푸터에

```css
#footer {
  background-image: url(./assets/bg.jpg);
  display: flex;
  justify-content: space-between;
}
```

**CSS 안의 경로는 CSS 파일 위치 기준**입니다. `practice2.css`가 `day10/pracitce/`에 있고 `assets`도 같은 폴더에 있으므로 `./assets/bg.jpg`가 맞습니다. HTML 기준이 아니라는 점이 헷갈리기 쉬운 부분입니다.

### 1-4. 레이아웃 확인용 테두리

```css
* {
  border: 1px red solid;
}
```

[[CSS day09 카페 키오스크]] 과 같은 습관입니다. 구조를 잡는 동안 모든 박스의 경계를 보이게 해두고, 완성 후 제거합니다.

주의할 점은 `border`가 실제 크기를 1px씩 키운다는 것입니다. `box-sizing: border-box`가 없으면 확인용 테두리 때문에 레이아웃이 미세하게 달라집니다.

```css
* { box-sizing: border-box; border: 1px red solid; }
```

## 2. 추가로 알면 좋은 활용법

### 2-1. `%` 대신 `flex`로 폭 나누기

```css
.sidebar { width: 18%; }
.section { width: 80%; }
```

`%`는 부모 폭이 바뀌면 같이 변합니다. 사이드바처럼 **폭이 고정이어야 하는 요소**는 px로 두는 게 안정적입니다.

```css
.container { display: flex; gap: 20px; }
.sidebar { width: 200px; flex-shrink: 0; }   /* 절대 안 줄어듦 */
.section { flex: 1; }                        /* 나머지 전부 */
```

`flex-shrink: 0`이 없으면 화면이 좁아질 때 사이드바 글자가 찌그러집니다. `gap`을 쓰면 `space-between`으로 여백을 만들 필요도 없어집니다.

### 2-2. container를 클래스 하나로 재사용

```css
.container {
  width: min(1080px, 100% - 40px);   /* 좁으면 여백 20px씩, 넓으면 1080px */
  margin: 0 auto;
}
```

`min()`을 쓰면 미디어 쿼리 없이도 모바일에서 양옆 여백이 확보됩니다. 지금처럼 `width: 1080px` 고정이면 폭 1080px 미만 화면에서 가로 스크롤이 생깁니다.

### 2-3. 사이드바 메뉴 꾸미기

```html
<div class="sidebar">
  <div>사진이론</div>
  <div>카메라 동작 이론</div>
</div>
```

`<div>` 나열보다 목록 태그가 의미상 맞습니다.

```html
<nav class="sidebar">
  <ul>
    <li><a href="#">사진이론</a></li>
    <li><a href="#">카메라 동작 이론</a></li>
  </ul>
</nav>
```

```css
.sidebar li { list-style: none; }
.sidebar a {
  display: block;          /* 영역 전체가 클릭 가능해짐 */
  padding: 12px 16px;
  text-decoration: none;
  color: #333;
  border-left: 3px solid transparent;
  transition: all .2s;
}
.sidebar a:hover,
.sidebar a.active {
  background: #f5f5f5;
  border-left-color: #e74c3c;
}
```

`display: block` + `padding`이 핵심입니다. `<a>`는 기본이 inline이라 글자 부분만 클릭됩니다.

### 2-4. 메인 이미지 처리

```css
.mainImg { width: 1280px; }
```

```css
.mainImg {
  display: block;
  width: 100%;
  height: 400px;
  object-fit: cover;
}
```

`width` 고정이면 화면이 좁을 때 넘칩니다. `100%` + `object-fit: cover`가 안전합니다. → CSS day15 테이블과 배경

### 2-5. 헤더를 flex로 정렬

```css
#header .container {
  display: flex;
  justify-content: space-between;
  align-items: center;
  height: 100%;
}
```

`#header`에 `height: 50px`을 줬으니 `.container`에 `align-items: center`를 주면 로고가 세로 가운데로 옵니다. → CSS day08 flexbox

### 2-6. 푸터 배경 이미지 마감

```css
#footer {
  background-image: url(./assets/bg.jpg);
  background-size: cover;
  background-position: center;
  background-repeat: no-repeat;
}
```

`background-image`만 쓰면 원본 크기대로 깔리고 모자라면 반복됩니다. `cover` + `no-repeat`가 기본 조합입니다. → CSS day15 테이블과 배경

배경 위에 로고가 잘 안 보이면 오버레이를 겹칩니다.
```css
#footer {
  background:
    linear-gradient(rgba(0,0,0,0.45), rgba(0,0,0,0.45)),
    url(./assets/bg.jpg) center / cover no-repeat;
}
```

## 3. 더 나아가 알면 좋은 것

### 3-1. 시맨틱 구조로 바꾸기

```html
<header>
  <div class="container">
    <h1 class="logo"><a href="/"><img src="./assets/logo.png" alt="사이트명"></a></h1>
    <nav>...</nav>
  </div>
</header>

<main>
  <img class="mainImg" src="./assets/main_img.png" alt="">
  <div class="container">
    <aside class="sidebar">...</aside>
    <section class="content">...</section>
  </div>
</main>

<footer>...</footer>
```

`#header`/`#section`/`#footer` 로 이미 역할을 나눠뒀으니 태그만 바꾸면 됩니다. 사이드바에는 `<aside>` 가 맞습니다. → HTML day02 문서 구조와 미디어

### 3-2. 반응형 전환

```css
@media (max-width: 1080px) {
  #header, #section, #footer { width: 100%; }
  .container { width: 100%; padding: 0 20px; }
}

@media (max-width: 768px) {
  .container { flex-direction: column; }
  .sidebar { width: 100%; }
  .section { width: 100%; }
}
```

`flex-direction: column` 한 줄로 사이드바가 본문 위로 올라갑니다. 이게 flex 레이아웃의 큰 이점입니다.

### 3-3. 강의 목록을 데이터로

사이드바 6개 항목을 배열로 빼면 현재 페이지 표시도 쉬워집니다.

```javascript
const lectures = [
  "사진이론", "카메라 동작 이론", "무조건 찍어 보자",
  "피사체 배경", "조리개와 심도", "카메라 촬영 모드"
];
const current = 0;

document.querySelector(".sidebar ul").innerHTML = lectures
  .map((name, i) => `<li><a href="#" class="${i === current ? "active" : ""}">${name}</a></li>`)
  .join("");
```

→ JS day11 DOM 조작

### 3-4. CSS 변수로 사이즈 관리

```css
:root {
  --container-width: 1080px;
  --sidebar-width: 200px;
  --header-height: 50px;
}
.container { width: var(--container-width); }
.sidebar { width: var(--sidebar-width); }
#header { height: var(--header-height); }
```

폭을 한 번에 조정할 수 있고, 미디어 쿼리 안에서 변수만 바꾸면 전체가 따라옵니다.

```css
@media (max-width: 768px) {
  :root { --sidebar-width: 100%; }
}
```

### 3-5. 다음 단계

- [[CSS day11 커뮤니티와 예약 사이트]] — 같은 구조를 3열 커뮤니티·예약 사이트로 확장
- CSS day14 position과 가상요소 — 헤더 고정, 드롭다운 메뉴
- JS day10 함수 — 같은 날 배운 함수로 사이드바 동작 붙이기

## 실습 파일

- `2026_FE/day10/pracitce/practicce2.html`, `practice2.css`
- `2026_FE/day10/pracitce/practice0.html`, `practice0.js`, `practice1.html`, `practice1.js`
- `2026_FE/day10/exam/exam2.css`, `exam2.html`, `practice0.css`, `practice0.html`
- `2026_FE/day10/pracitce/assets/bg.jpg`, `logo.png`, `footer_logo.png`, `main_img.png`, `dslr.png`

## 관련 노트

[[CSS MOC]] · [[CSS day09 카페 키오스크]] · [[CSS day11 커뮤니티와 예약 사이트]] · JS day10 함수 · HTML day02 문서 구조와 미디어
