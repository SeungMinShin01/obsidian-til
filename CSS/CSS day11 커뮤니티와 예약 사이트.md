---
출처: Claude 분석
원본: KDT_2026/2026_FE/day11
작성일: 2026-08-10
tags: [학습, css]
---

# CSS day11 — 커뮤니티와 예약 사이트

> 실습 파일: `day11/practice/practiceCSS7.html/css`(베이킹 커뮤니티), `practiceCSS8.html/css`(스튜디오 예약), `practice7.*`, `teampractice/`, `assets/practice7`·`practice8`
> 허브: [[CSS MOC]] · 이전: [[CSS day10 카메라 강의 사이트]] · 다음: [[CSS day14 position과 가상요소]]

## 1. 배운 내용

JS DOM을 배우던 날([[JS day11 DOM 조작]])에 CSS로는 **완성도 높은 사이트 두 개**를 만들었습니다.

| 파일 | 사이트 |
| --- | --- |
| `practiceCSS7` | The 베이킹 — 로그인 메뉴 + 3열 커뮤니티 |
| `practiceCSS8` | THE 스튜디오 — 사진 스튜디오 예약 |

### 1-1. 공통 리셋 — 두 파일 모두 같은 3블록으로 시작

```css
* {
  box-sizing: border-box;   /* 여백까지 포함한 사이즈 */
  padding: 0px;
  margin: 0px;              /* 기본 여백 제거 */
}

a {
  text-decoration: none;    /* a 하이퍼링크 밑줄 제거 */
  color: #000;              /* 기본색상(파란색) 변경 */
}

li {
  list-style-type: none;    /* li 항목 글머리 제거 */
}
```

이 3블록이 사실상 **개인용 리셋 CSS**입니다. 이걸 `common/reset.css`로 빼두면 이후 모든 실습에서 `<link>` 한 줄로 재사용할 수 있습니다.

`box-sizing: border-box`를 처음부터 깔고 시작한 것이 [[CSS day10 카메라 강의 사이트]] 대비 크게 발전한 부분입니다.

### 1-2. practiceCSS7 — 2단 헤더 메뉴

```html
<div id="header">
  <div class="left_head"><img src="../assets/practice7/logo.png" /></div>
  <div class="right_head">
    <ol class="top_menu">
      <li><a href="#">신승민(smShin)님</a></li>
      <li><a href="#">|로그아웃</a></li>
      <li><a href="#">|정보수정</a></li>
    </ol>
    <ol class="bottom_menu">
      <li><a href="#">HOME</a></li>
      <li><a href="#">출석부</a></li>
      <li><a href="#">작품갤러리</a></li>
      <li><a href="#">게시판</a></li>
    </ol>
  </div>
</div>
```

```css
#header {
  display: flex;
  justify-content: space-between;   /* 로고는 왼쪽, 메뉴는 오른쪽 */
  align-items: center;
  width: 1280px;
  margin: 0 auto;
}

.top_menu {
  display: flex;
  justify-content: end;   /* 오른쪽 정렬 */
  gap: 5px;
  font-size: 14px;
}

.bottom_menu {
  display: flex;
  justify-content: end;
  gap: 95px;              /* 메인 메뉴는 간격을 크게 */
}

.bottom_menu > li {
  margin-top: 8px;
  font-size: 20px;
  font-weight: bold;
}
```

**flex 안에 flex** 구조입니다. 바깥 `#header`가 로고와 메뉴 묶음을 양끝으로 보내고, 안쪽 `.top_menu`/`.bottom_menu`가 각각 오른쪽 정렬됩니다.

상단 작은 메뉴(로그인 상태)와 하단 큰 메뉴(사이트 내비)를 세로로 쌓는 건 커뮤니티 사이트의 전형적인 헤더 구조입니다.

`justify-content: end`는 `flex-end`의 축약형입니다.

### 1-3. practiceCSS7 — 3열 본문

```css
#main {
  width: 1280px;
  margin: 0 auto;
  display: flex;
  justify-content: space-between;
}

.sidebar    { width: 20%; }
.left_main  { width: 38%; }
.right_main { width: 38%; }
```

20 + 38 + 38 = 96%, 남는 4%를 `space-between`이 두 틈으로 나눕니다. [[CSS day10 카메라 강의 사이트]] 의 2열(18% + 80%)에서 3열로 확장된 형태입니다.

### 1-4. 게시판 행 — 제목과 날짜 양끝

```html
<div class="section1">
  <h4>알림</h4>
  <ol>
    <div>
      <li>쿠키 클래스 연기 합니다.</li>
      <li>09.30</li>
    </div>
  </ol>
</div>
```

```css
.section1 > ol > div,
.section2 > ol > div {
  display: flex;
  justify-content: space-between;
}
```

**제목은 왼쪽, 날짜는 오른쪽** — 게시판 목록의 기본 배치입니다. 복수 선택자(`,`)로 두 섹션에 한 번에 적용했습니다.

`<ol>` 안에 `<div>`가 들어간 구조인데, HTML 표준상 `<ol>`의 직계 자식은 `<li>`여야 합니다. 같은 효과를 내려면 `<li>` 하나에 두 요소를 넣는 방식이 안전합니다.

```html
<li>
  <span>쿠키 클래스 연기 합니다.</span>
  <span>09.30</span>
</li>
```
```css
.section1 li { display: flex; justify-content: space-between; }
```

### 1-5. 사이드바 제목 강조

```css
.sidebar > h3 {
  background-color: #0ba9a1;
  color: #fff;
  padding: 13px;
  margin-bottom: 8px;
}
```

블록 요소인 `<h3>`에 배경색을 주면 자동으로 가로 전체를 채웁니다. **띠 형태의 섹션 제목**을 만드는 가장 간단한 방법입니다.

### 1-6. practiceCSS8 — 로고 안에 강조색

```html
<h2><span>THE</span>스튜디오</h2>
```

```css
#header > h2 { font-size: 32px; }
#header > h2 > span {
  margin-right: 10px;
  color: #0f00e2;
}
```

한 제목 안에서 일부만 다른 색을 주려고 `<span>`으로 감쌌습니다. **`<span>`의 대표적인 용도**입니다. → [[CSS day06 선택자와 기본 속성]]

### 1-7. practiceCSS8 — 아이콘 + 텍스트 2열

```html
<div class="section1">
  <div>
    <img src="../assets/practice8/icon1.png" />
    <div>
      <h4>예약안내</h4>
      <div>스튜디오 대여는 사전에 인터넷 예약을 하셔야 합니다...</div>
    </div>
  </div>
  <div> ... icon2 ... </div>
</div>
```

```css
.section1 {
  display: flex;
  justify-content: space-between;
}
.section1 > div {
  display: flex;       /* 아이콘과 글을 가로로 */
  margin: 20px 10px;
}
.section1 > div > img {
  margin-right: 20px;
  width: 17%;
}
```

**아이콘 + 제목 + 설명** 조합은 서비스 소개 섹션의 표준 패턴입니다. 여기서도 flex 중첩(바깥 row → 안쪽 row)이 쓰였습니다.

### 1-8. 메인 이미지를 화면 폭보다 넓게

```css
#mainImage {
  width: 1500px;
  margin: 0 auto;
}
#mainImage > img {
  display: block;
  width: 1280px;
  margin: 0 auto;
}
#main { width: 800px; margin: 0 auto; }
```

바깥 컨테이너는 넓게, 실제 이미지는 1280px로 가운데 정렬했습니다. `display: block`을 준 이유는 `<img>`가 기본 inline이라 **아래에 3~4px 여백**이 생기기 때문입니다. → [[CSS day05 첫 스타일링]]

콘텐츠 폭이 구역마다 다릅니다 — 헤더 820px, 메인 이미지 1280px, 본문 800px. 의도적인 리듬일 수도 있지만, 보통은 하나의 `.container` 폭으로 통일하고 **풀블리드(full-bleed)가 필요한 요소만 예외**로 둡니다.

## 2. 추가로 알면 좋은 활용법

### 2-1. 여러 페이지 사이트의 CSS 구조

```
css/
├── reset.css      브라우저 기본값 초기화
├── common.css     헤더·푸터·버튼·색상 변수 (모든 페이지)
├── intro.css      소개 페이지 전용
└── reservation.css 예약 페이지 전용
```

```html
<link rel="stylesheet" href="css/reset.css" />
<link rel="stylesheet" href="css/common.css" />
<link rel="stylesheet" href="css/intro.css" />
```

**순서가 중요합니다.** 나중에 로드된 것이 우선입니다.

### 2-2. 서브페이지 헤더 패턴

`sub_intro.jpg`, `sub_reservation.jpg`처럼 페이지마다 다른 배경을 쓸 때

```css
.sub-header {
  height: 300px;
  background-size: cover;
  background-position: center;
  display: flex;
  align-items: center;
  justify-content: center;
}
.sub-header h2 { color: #fff; font-size: 2.5rem; }

/* 페이지별 배경만 교체 */
.sub-header.intro       { background-image: url(../assets/sub_intro.jpg); }
.sub-header.reservation { background-image: url(../assets/sub_reservation.jpg); }
```

```html
<div class="sub-header intro"><h2>소개</h2></div>
```

공통 구조 + 클래스 하나로 변형하는 게 유지보수에 좋습니다.

### 2-3. 이미지 슬라이드 (pre.png / next.png)

**CSS만으로**
```css
.slider { position: relative; overflow: hidden; }
.slides { display: flex; transition: transform .5s; }
.slide  { min-width: 100%; }

.arrow {
  position: absolute;
  top: 50%;
  transform: translateY(-50%);
  cursor: pointer;
}
.arrow.prev { left: 20px; }
.arrow.next { right: 20px; }
```

**JS로 동작**
```javascript
let idx = 0;
const slides = document.querySelector(".slides");
const total = document.querySelectorAll(".slide").length;

document.querySelector(".next").addEventListener("click", () => {
  idx = (idx + 1) % total;
  slides.style.transform = `translateX(-${idx * 100}%)`;
});
```

`% total`이 끝에서 처음으로 돌아가게 합니다. → [[JS day13 웹 스토리지와 인터벌]]

`position: absolute` + 부모 `relative`는 [[CSS day14 position과 가상요소]] 의 핵심 패턴입니다.

### 2-4. 갤러리 그리드

`photo1~5.jpg`, `image1~4.jpg` 배치에 grid가 유용합니다.

```css
.gallery {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 10px;
}
.gallery img {
  width: 100%;
  aspect-ratio: 4 / 3;
  object-fit: cover;
}

/* 첫 번째 사진만 크게 */
.gallery img:first-child {
  grid-column: span 2;
  grid-row: span 2;
}
```

`aspect-ratio`로 비율을 고정하면 이미지 크기가 제각각이어도 격자가 흐트러지지 않습니다.

### 2-5. SNS 아이콘

```css
.sns { display: flex; gap: 12px; }
.sns img {
  width: 32px;
  height: 32px;
  opacity: .7;
  transition: opacity .2s, transform .2s;
}
.sns img:hover { opacity: 1; transform: scale(1.1); }
```

아이콘이 3개뿐이면 개별 파일도 괜찮지만, 많아지면 SVG 스프라이트가 유리합니다. → [[CSS day15 테이블과 배경]]

## 3. 더 나아가 알면 좋은 것

### 3-1. 이 페이지들을 반응형으로

`practiceCSS8`(예약 사이트)이 반응형 연습에 가장 좋은 소재입니다.

```css
/* 데스크톱 */
.layout { display: flex; gap: 40px; }
.content { flex: 1; }
.sidebar { width: 300px; flex-shrink: 0; }

@media (max-width: 900px) {
  .layout { flex-direction: column; }
  .sidebar { width: 100%; }
  .gallery { grid-template-columns: repeat(2, 1fr); }
}

@media (max-width: 600px) {
  .gallery { grid-template-columns: 1fr; }
  .sub-header { height: 180px; }
  .sub-header h2 { font-size: 1.5rem; }
}
```

**흔한 브레이크포인트**: 480 / 768 / 1024 / 1280px

### 3-2. 모바일 햄버거 메뉴

```css
.hamburger { display: none; }

@media (max-width: 768px) {
  .hamburger { display: block; }
  nav ul {
    display: none;
    position: absolute;
    top: 80px; left: 0; right: 0;
    background: #fff;
    flex-direction: column;
  }
  nav ul.open { display: flex; }
}
```

```javascript
document.querySelector(".hamburger").addEventListener("click", () => {
  document.querySelector("nav ul").classList.toggle("open");
});
```

**CSS가 모양을, JS가 클래스만 토글**하는 게 표준 패턴입니다. → [[JS day11 DOM 조작]]

### 3-3. 이미지 용량

`practice8` 폴더의 이미지가 20여 장입니다. `.jpg` 원본이면 페이지 로딩이 상당히 느립니다.

| 조치 | 효과 |
| --- | --- |
| WebP 변환 | 25~35% 감소 |
| `loading="lazy"` | 초기 로딩 시간 단축 |
| 적정 해상도로 리사이즈 | 가장 큰 효과 |
| `srcset`으로 화면별 이미지 | 모바일 데이터 절약 |

가로 400px로 보여줄 이미지를 2000px 원본으로 넣는 게 가장 흔한 낭비입니다.

### 3-4. 다음 단계

`day11`에서 만든 페이지에 JS를 붙이면 완성도가 크게 올라갑니다.

- 슬라이드 자동 재생 → [[JS day13 웹 스토리지와 인터벌]]
- 예약 폼 검증 → [[JS day04 조건문]], [[HTML day04 폼과 테이블]]
- 갤러리 라이트박스 → `<dialog>` + [[JS day11 DOM 조작]]

## 실습 파일

- `2026_FE/day11/practice/practiceCSS7.html`, `practiceCSS7.css`
- `2026_FE/day11/practice/practiceCSS8.html`, `practiceCSS8.css`
- `2026_FE/day11/practice/practice7.html`, `practice7.css`, `practice7.js`
- `2026_FE/day11/practice/practiceCSS.css`, `exam0.css`, `exam0.html`
- `2026_FE/day11/practice/teampractice/practice1.css`, `practice1.html`, `practice2.css`, `practice2.html`
- `2026_FE/day11/assets/practice7/`, `practice8/`
- `2026_FE/day11/exam/exam1.css`

## 관련 노트

[[CSS MOC]] · [[CSS day10 카메라 강의 사이트]] · [[CSS day14 position과 가상요소]] · [[JS day11 DOM 조작]] · [[CSS day09 카페 키오스크]]
