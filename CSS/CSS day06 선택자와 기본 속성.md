---
출처: Claude 분석
원본: KDT_2026/2026_FE/day06, day08/exam/CSS.txt, Note/CSSNote
작성일: 2026-08-10
tags: [css, day06, 선택자, 우선순위, 박스모델]
---

# CSS day06 — 선택자와 기본 속성

> 실습 파일: `day06/exam/exam1.css`, `day06/practice/practice1~3.css`, `day08/exam/CSS.txt`, `Note/CSSNote`
> 허브: [[CSS MOC]] · 이전: [[CSS day05 첫 스타일링]] · 다음: [[CSS day08 flexbox]]

## 1. 배운 내용

### 1-1. CSS 적용 3가지 방법 — CSS.txt

```html
<!-- 1. 인라인 -->
<div style="color: red;">

<!-- 2. 내부 스타일시트 -->
<head><style> div { color: red; } </style></head>

<!-- 3. 외부 파일 (권장) -->
<head><link rel="stylesheet" href="main.css"></head>
```

### 1-2. 선택자 7종

| 선택자 | 문법 | 개수 |
| --- | --- | --- |
| 전체 | `*` | 공통 CSS |
| 태그 | `h4` | 복수 |
| 클래스 | `.className` | **복수** |
| 아이디 | `#idName` | **단일** |
| 자식 | `A > B` | 바로 아래 |
| 자손 | `A B` | 하위 전부 |
| 복수 | `A, B` | 동시 적용 |

**자식 vs 자손**
```html
<div>
  <ol>
    <li>여기</li>     <!-- div li (자손) O, div > li (자식) X -->
  </ol>
</div>
```
`div > li`는 `li`가 `div`의 **바로 아래**여야 합니다. 중간에 `ol`이 있으면 안 됩니다.

### 1-3. 우선순위 — exam1.css의 실험

```
#id > .class > 마크업명 > *
```
**동일한 수준이면 나중에 작성한 코드가 이깁니다.**

`exam1.css`가 이걸 직접 실험합니다.
```css
#구역2 { color: #fff; }
#구역2 { color: tomato; }   /* 이게 적용됨 */
```

### 1-4. 텍스트 속성

```css
font-family: "궁서";        /* 글꼴 — 눈누(한글), Google Fonts(영문) */
font-size: 12px;
font-style: italic;
font-weight: bold;
color: red;
word-spacing: 10px;         /* 어간 (단어 간격) */
letter-spacing: 5px;        /* 자간 (글자 간격) */
line-height: 160%;          /* 줄간격 */
text-align: center;         /* left right center */
text-decoration: underline; /* overline, line-through */
text-shadow: 0 0 5px red;   /* x y 흐림 색상 */
```

**색상 3가지** — 색상명 / `rgb()` / 헥스코드

### 1-5. 박스 속성

```css
border: solid 3px red;         /* 선종류 굵기 색상 — 순서 무관 */
border-radius: 20px;
box-shadow: 3px 3px 1px red;   /* x y 흐림 색상 */
width: 100px;
height: 100px;
padding: 10px;                 /* 테두리 안쪽 여백 */
margin: 10px;                  /* 테두리 바깥 여백 */
margin: 0 auto;                /* 가로 가운데 (width 필수) */
background-color: beige;
```

**HTML 마크업 1개 = 1개의 구역**입니다.

### 1-6. display

| 값 | 줄 차지 | 크기 지정 | 여백 | 대표 태그 |
| --- | --- | --- | --- | --- |
| `inline` | X | **불가** | 좌우만 | `<span>` `<a>` |
| `block` | O (한 줄 전체) | 가능 | 전부 | `<div>` `<h1>` |
| `inline-block` | X | **가능** | 전부 | `<img>` `<input>` |
| `none` | 표시 안 함 | - | - | - |
| `flex` | 하위 요소 배치 제어 | - | - | → [[CSS day08 flexbox]] |

`inline`은 `width`/`height`가 안 먹고 위아래 `margin`도 무시됩니다. **이게 `inline-block`이 존재하는 이유**입니다.

### 1-7. box-sizing — 가장 중요한 한 줄

```css
box-sizing: content-box;   /* 기본값: width = 콘텐츠만 */
box-sizing: border-box;    /* width = 콘텐츠 + padding + border */
```

`content-box`에서 `width: 100px; padding: 10px; border: 1px`이면 실제 폭은 **122px**입니다. `border-box`면 정확히 100px입니다.

### 1-8. 단위 — Note/CSSNote 7번

| 단위 | 기준 |
| --- | --- |
| `px` | 절대 — 화면 픽셀 하나 |
| `%` | **직계 부모** 요소의 크기 |
| `rem` | `<html>`의 font-size (기본 16px) |
| `em` | **자기 자신 또는 부모**의 font-size |
| `vw` / `vh` | 브라우저 창의 가로 / 세로 전체 |

`100vw` = 브라우저 가로 폭 전체, `100vh` = 세로 전체

## 2. 추가로 알면 좋은 활용법

### 2-1. 명시도(Specificity) 계산

우선순위는 `(인라인, id, class, 태그)` 4자리 점수입니다.

| 선택자 | 점수 |
| --- | --- |
| `style=""` | 1,0,0,0 |
| `#id` | 0,1,0,0 |
| `.class`, `[attr]`, `:hover` | 0,0,1,0 |
| `div`, `::before` | 0,0,0,1 |
| `*` | 0,0,0,0 |

`div.box p` = 0,0,1,2 이고 `#main p` = 0,1,0,1 → **`#main p`가 이깁니다.**
**class 10개를 겹쳐도 id 하나를 못 이깁니다.**

### 2-2. `!important`는 마지막 수단

```css
.title { color: red !important; }
```

편해 보이지만 나중에 `!important`끼리 싸우게 되어 유지보수가 어려워집니다. **선택자를 더 구체적으로 쓰는 것**으로 먼저 해결하세요.

### 2-3. `rem`을 쓰면 접근성이 좋아집니다

사용자가 브라우저 기본 글꼴 크기를 키워도 `px`은 안 따라오지만 `rem`은 비례합니다.

```css
html { font-size: 16px; }
h1 { font-size: 2rem; }      /* 32px, 사용자 설정에 따라 커짐 */
```

`rem`은 항상 `<html>` 기준이라 예측 가능하고, `em`은 부모가 중첩되면 곱해져서 통제가 어렵습니다.
```css
.parent { font-size: 2em; }   /* 32px */
.child  { font-size: 2em; }   /* 64px! 부모의 2배 */
```

### 2-4. margin 상쇄(collapse)

```css
.box1 { margin-bottom: 30px; }
.box2 { margin-top: 20px; }
/* 사이 간격은 50px이 아니라 30px (큰 값만 적용) */
```

세로 방향 margin은 서로 겹칩니다. `padding`을 쓰거나 flex의 `gap`을 쓰면 피할 수 있습니다. **flex 컨테이너 안에서는 margin 상쇄가 일어나지 않습니다.**

### 2-5. CSS 변수

```css
:root {
  --main-color: #244;
  --gap: 16px;
}
.box {
  color: var(--main-color);
  padding: var(--gap);
}
```

색상을 한 곳에서 관리할 수 있어 다크모드 전환도 쉬워집니다. [[CSS day09 카페 키오스크]], [[CSS day10 카메라 강의 사이트]] 처럼 색을 반복해 쓴 파일에서 효과가 큽니다.

### 2-6. 선택자 몇 가지 더

```css
input[type="text"] { }        /* 속성 선택자 */
li:first-child { }
li:last-child { }
li:nth-child(2n) { }          /* 짝수 */
p + span { }                  /* 인접 형제 (바로 다음) */
p ~ span { }                  /* 일반 형제 (뒤의 모든) */
.box:not(.active) { }         /* 부정 */
a:hover { }                   /* 상태 */
```

`nth-child`, `nth-of-type`, `[colspan]` 은 day15에서 실제로 씁니다. → [[CSS day15 테이블과 배경]]

### 2-7. 웹폰트 적용

```css
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR&display=swap');
body { font-family: 'Noto Sans KR', sans-serif; }
```

`Note/CSSNote`에 적어두신 사이트
- 한글: `https://noonnu.cc`
- 영문: `https://fonts.google.com`

`font-family: "궁서"`처럼 로컬 폰트만 지정하면 그 폰트가 없는 PC에서는 다르게 보입니다. **웹폰트 또는 폴백 목록**을 두는 게 안전합니다.
```css
font-family: "Noto Sans KR", "맑은 고딕", sans-serif;
```

## 3. 더 나아가 알면 좋은 것

### 3-1. CSS 리셋

브라우저마다 기본 스타일이 다릅니다. 크롬은 `<body>`에 `margin: 8px`을 줍니다.

```css
*, *::before, *::after { box-sizing: border-box; }
* { margin: 0; padding: 0; }
ul, ol { list-style: none; }
a { text-decoration: none; color: inherit; }
img { display: block; max-width: 100%; }
button { border: none; background: none; cursor: pointer; font: inherit; }
```

### 3-2. 상속되는 속성 / 안 되는 속성

```css
/* 상속됨 — 부모에 주면 자식도 따라감 */
color, font-family, font-size, line-height, text-align, visibility

/* 상속 안 됨 */
width, height, margin, padding, border, background, display, position
```

`body`에 `font-family`를 한 번 주면 전체에 적용되는 이유입니다.

```css
.child { color: inherit; }   /* 강제로 상속받기 */
```

### 3-3. 반응형의 시작 — 미디어 쿼리

```css
.container { width: 100%; }             /* 모바일 우선 */

@media (min-width: 768px) {
  .container { width: 750px; }
}
@media (min-width: 1200px) {
  .container { width: 1140px; }
}
```

`<meta name="viewport">`가 있어야 동작합니다. → [[HTML day02 문서 구조와 미디어]]

## 실습 파일

- `2026_FE/Note/CSSNote`
- `2026_FE/day08/exam/CSS.txt`
- `2026_FE/day06/exam/exam1.css`, `exam1.html`, `activity1.js`
- `2026_FE/day06/practice/practice1.css`, `practice2.css`, `practice3.css`
- `2026_FE/day06/practice/practice1.html`, `practice2.html`, `practice3.html`

## 관련 노트

[[CSS MOC]] · [[CSS day05 첫 스타일링]] · [[CSS day08 flexbox]] · [[JS day11 DOM 조작]] · [[HTML day02 문서 구조와 미디어]]
