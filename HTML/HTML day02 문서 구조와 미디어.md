---
출처: Claude 분석
원본: KDT_2026/2026_FE/day02
작성일: 2026-08-10
tags: [학습, html]
---

# HTML day02 — 문서 구조와 미디어

> 실습 파일: `day02/index.html`, `day02/exam/exam1.html`, `exam2.html`, `day02/pracitce/*.html`, `day02/assets/`
> 허브: [[HTML MOC]] · 다음: [[HTML day04 폼과 테이블]]

## 1. 배운 내용

### 1-1. 문서의 골격

```html
<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>Page Title</title>
    <link rel="stylesheet" href="main.css" />
  </head>
  <body>
    <!-- 내용 -->
    <script src="exam1.js"></script>
  </body>
</html>
```

| 요소 | 역할 |
| --- | --- |
| `<!doctype html>` | HTML5 문서 선언 |
| `<meta charset="utf-8">` | **한글 깨짐 방지 (필수)** |
| `<meta name="viewport">` | 모바일 반응형의 시작점 |
| `<title>` | 브라우저 탭 제목, 검색 결과 제목 |
| `<link rel="stylesheet">` | CSS 연결 (`<head>` 안) |
| `<script src>` | JS 연결 (`</body>` 직전) |

정리하면 이렇습니다.
> HTML : 이동 가능한 텍스트 기반 마크업 언어
> 저장 : 코드 입력 후 Ctrl+S 또는 [FILE] → [AUTO SAVE] 활성화

### 1-2. 기본 태그

| 태그 | 용도 |
| --- | --- |
| `<h1>` ~ `<h6>` | 제목 (숫자가 작을수록 큼) |
| `<p>` | 문단 |
| `<br />` | 줄바꿈 |
| `<hr />` | 수평선 |
| `<div>` | 블록 구역 (의미 없음) |
| `<span>` | 인라인 구역 (의미 없음) |
| `<a href="">` | 링크 |
| `<img src="" alt="" />` | 이미지 |
| `<ul>` `<ol>` `<li>` | 목록 |

### 1-3. 인라인 스타일

```html
<body style="color: aquamarine; background-color: #fff">
  <p style="text-decoration: underline; color: chocolate">HI</p>
</body>
```

CSS를 배우기 전 단계라 `style` 속성을 직접 썼습니다. → [[CSS day06 선택자와 기본 속성]] 에서 외부 파일로 분리합니다.

### 1-4. 미디어 — day02/assets

`assets` 폴더에 mp4, mp3, webp, jpg, gif가 있는 걸 보면 미디어 태그를 실습하셨습니다.

```html
<img src="assets/gif.gif" alt="설명" />
<video src="assets/비디오.mp4" controls></video>
<audio src="assets/음악.mp3" controls></audio>
```

| 속성 | 의미 |
| --- | --- |
| `controls` | 재생 컨트롤 표시 |
| `autoplay` | 자동 재생 (대부분 `muted` 필요) |
| `loop` | 반복 |
| `poster` | 재생 전 썸네일 (video) |

### 1-5. 페이지 간 이동 — index.html을 허브로

```html
<a href="exam1.html">exam1 이동</a> <br />
<a href="exam2.html">exam2 이동</a> <br />
<a href="Practice1.html">연습1 이동</a>
```

**허브 페이지를 하나 두면 편합니다.** 파일이 많아질수록 진입점이 있는 쪽이 훨씬 낫습니다.

`<a>`의 다른 용법
```html
<a href="#section1">페이지 내 이동</a>
<a href="https://example.com" target="_blank" rel="noopener">새 탭</a>
<a href="mailto:a@b.com">메일</a>
<a href="tel:01012345678">전화</a>
```

`target="_blank"`에는 **`rel="noopener"`를 같이** 써야 보안상 안전합니다.

## 2. 추가로 알면 좋은 활용법

### 2-1. `alt`는 선택이 아니라 필수

```html
<img src="logo.png" />                 <!-- 접근성 위반 -->
<img src="logo.png" alt="회사 로고" />  <!-- 정답 -->
<img src="deco.png" alt="" />          <!-- 장식용은 빈 alt로 명시 -->
```

이미지 로딩 실패 시 대체 텍스트가 되고, 스크린 리더가 읽어주며, 검색엔진이 이미지를 이해합니다.

### 2-2. 이미지 최적화

```html
<img src="main.jpg" alt="" loading="lazy" width="800" height="600" />
```

- `loading="lazy"` — 화면에 보일 때 로딩 (초기 속도 개선)
- `width`/`height` 명시 — 이미지 로딩 전후로 레이아웃이 흔들리는 현상(CLS) 방지
- `.webp` — jpg 대비 25~35% 작음. `day02/assets/다운로드.webp`에서 이미 쓰고 계십니다

### 2-3. 상대 경로와 절대 경로

```html
<img src="assets/gif.gif" />      <!-- 현재 폴더 기준 -->
<img src="../assets/gif.gif" />   <!-- 상위 폴더 -->
<img src="/assets/gif.gif" />     <!-- 사이트 루트 -->
```

`day15/exam/exam4.css`에서 `url(../assets/배경.jpg)`를 쓰신 게 상대 경로 예입니다. **CSS 안의 경로는 CSS 파일 위치 기준**이라는 점이 헷갈리기 쉽습니다.

### 2-4. 주석

```html
<!-- 주석 -->
```
주석은 브라우저에 표시되지 않지만 **소스 보기로 누구나 볼 수 있습니다.** 민감한 정보를 남기면 안 됩니다.

## 3. 더 나아가 알면 좋은 것

### 3-1. 시맨틱 태그

```html
<header>  머리말, 로고·제목
<nav>     내비게이션
<main>    페이지의 주 내용 (문서당 1개)
<section> 주제별 구역
<article> 독립적으로 배포 가능한 콘텐츠 (블로그 글, 댓글, 상품 카드)
<aside>   곁다리 (사이드바)
<footer>  꼬리말
```

전부 `<div>`로 써도 화면은 똑같습니다. 그런데도 나눠 쓰는 이유는 **SEO**와 **접근성**입니다.

**선택 기준**

| 상황 | 태그 |
| --- | --- |
| 그 자체로 완결되고 다른 곳에 옮겨도 말이 되는가 | `<article>` |
| 관련된 내용의 묶음인가 | `<section>` |
| 의미 없이 스타일링만 필요한가 | `<div>` |

[[CSS day10 카메라 강의 사이트]], [[CSS day11 커뮤니티와 예약 사이트]] 의 페이지를 시맨틱 구조로 바꿔보면 감이 빨리 옵니다.

### 3-2. SEO 기본 메타 태그

```html
<meta name="description" content="페이지 설명 (검색 결과에 표시됨)" />
<meta property="og:title" content="공유 시 제목" />
<meta property="og:image" content="공유 시 썸네일" />
<link rel="icon" href="favicon.ico" />
```

카카오톡·슬랙에 링크를 붙일 때 나오는 미리보기가 Open Graph 태그입니다.

### 3-3. 유용한 최신 태그

```html
<details>
  <summary>더보기</summary>
  숨겨진 내용 (JS 없이 접기/펼치기)
</details>

<dialog id="modal">모달</dialog>   <!-- JS: modal.showModal() -->

<picture>
  <source media="(min-width:800px)" srcset="big.jpg">
  <img src="small.jpg" alt="">
</picture>

<progress value="70" max="100"></progress>
<time datetime="2026-08-10">2026년 8월 10일</time>
```

`<dialog>`는 [[JS day14 게시판 CRUD]] 의 `alert`/`confirm`을 대체하기 좋습니다.

## 실습 파일

- `2026_FE/day02/index.html`
- `2026_FE/day02/exam/exam1.html`, `exam2.html`
- `2026_FE/day02/pracitce/HTMLpractice1.html`, `Practice1.html`, `Pracitce2.html`
- `2026_FE/day02/assets/` (mp4, mp3, webp, jpg, gif)
- `2026_FE/Note/HTMLNote`

## 관련 노트

[[HTML MOC]] · [[HTML day04 폼과 테이블]] · [[JS day02 변수와 입출력]] · [[CSS day06 선택자와 기본 속성]]
