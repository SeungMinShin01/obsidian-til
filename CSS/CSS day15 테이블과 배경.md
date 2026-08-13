---
출처: Claude 분석
원본: KDT_2026/2026_FE/day15
작성일: 2026-08-10
tags: [학습, css]
---

# CSS day15 — 테이블과 배경

> 실습 파일: `day15/exam/exam1.css`(테이블), `exam3.css`(object-fit), `exam4.css`(background), `day15/assets/`
> 허브: [[CSS MOC]] · 이전: [[CSS day14 position과 가상요소]]

## 1. 배운 내용

### 1-1. 테이블 꾸미기 — exam1.css

```css
.basicTable th,
.basicTable td {
  border: 1px solid #000;
  padding: 10px;
}
.basicTable { border: 1px solid #000; width: 500px; }

.styleTable {
  width: 700px;
  border-collapse: collapse;   /* 이중 테두리를 하나로 병합 */
}
.styleTable th, .styleTable td { border: 1px solid black; }
```

`border-collapse: collapse` 없이는 `<table>`과 `<td>`의 테두리가 각각 그려져 **선이 두 겹**으로 보입니다.

### 1-2. 고급 선택자

```css
/* nth-child(N) — 동일한 선택자 중 N번째 */
.basicTable td:nth-child(1) { background-color: aqua; }
.basicTable td:nth-child(3) { background-color: beige; }

/* [속성명] — 특정 속성을 가진 요소 */
.basicTable td[colspan] { text-align: right; }

/* nth-of-type(even/odd) — 홀수/짝수 */
.styleTable > tbody > tr:nth-of-type(even) { background-color: #eeeeee; }

/* :hover — 행 강조 */
.styleTable > tbody > tr:hover { background-color: gray; }
```

**`nth-child` vs `nth-of-type`**
- `nth-child(2)` — 부모의 **모든** 자식 중 2번째. 타입이 달라도 셈
- `nth-of-type(2)` — **같은 태그** 중 2번째

`<div>` 사이에 `<p>`가 섞여 있으면 결과가 달라집니다. 헷갈리면 `nth-of-type`이 더 예측 가능합니다.

**줄무늬 테이블**은 `nth-of-type(even)` 한 줄로 완성됩니다. 가독성이 크게 올라갑니다.

### 1-3. object-fit — exam3.css

```css
.imgBox { width: 300px; height: 300px; }
.imgBox > img { width: 100%; height: 100%; }
```

| 값 | 동작 |
| --- | --- |
| `fill` (기본) | 영역을 꽉 채움, **비율 무시 (찌그러짐)** |
| `contain` | 전체가 보이도록 비율 유지 (여백 생김) |
| `cover` | 비율 유지하되 넘치는 부분 잘라냄 |
| `none` | 원본 크기 그대로 |

```css
object-position: left;   /* cover/contain에서 어느 부분을 보여줄지 */
```

**실무 기본값은 `cover`입니다.** 썸네일, 카드 이미지, 프로필 사진이 전부 `cover`입니다. 크기가 제각각인 이미지를 같은 틀에 넣어도 안 찌그러집니다.

`exam3.html`이 같은 이미지를 6개 상자에 넣고 값만 바꿔 비교하는 구조인데, [[CSS day08 flexbox]] 의 `.flexbox1~10`과 같은 좋은 학습법입니다.

### 1-4. background 속성군 — exam4.css

```css
background-color: rgba(0, 0, 255, 0.5);        /* 투명도 포함 */
background-color: #0000ff1c;                   /* 8자리 헥스 = 색 + 알파 */

background-image: url(../assets/배경.jpg);
background-repeat: no-repeat;                  /* repeat-x, repeat-y */
background-position: bottom;                   /* 또는 "10px 20px" */
background-size: cover;                        /* contain, 100px 100px */
background-attachment: fixed;                  /* 스크롤해도 배경 고정 (패럴랙스) */
```

`#0000ff1c`에서 뒤 2자리 `1c`가 투명도(alpha)입니다. 약 11%입니다.

### 1-5. CSS 스프라이트

`exam4.css` 주석에 정확히 정리하셨습니다.
> 아이콘 1개(이미지 1개)이므로 여러 아이콘들을 호출하는 것보다 아이콘들을 하나의 이미지에 모아두고 사용하는 예제

```css
.box2 {
  width: 100px; height: 100px;
  background-image: url(../assets/아이콘들.png);
  background-repeat: no-repeat;
  background-position: 10px 10px;   /* 이미지 안에서 보여줄 좌표 */
}
```

이미지 20개 = HTTP 요청 20번인데, 스프라이트 1장이면 요청 1번입니다. `day15/assets/아이콘들.png`, `day14/assets/popup_icons/`가 이 용도입니다.

## 2. 추가로 알면 좋은 활용법

### 2-1. `object-fit`이 안 먹을 때

```css
img { object-fit: cover; }              /* 크기가 없으면 의미 없음 */
img { width: 100%; height: 200px; object-fit: cover; }   /* 동작 */
```

`object-fit`은 "정해진 상자 안에서 이미지를 어떻게 맞출지"이므로 `width`와 `height`가 **둘 다** 필요합니다.

`aspect-ratio`와 조합하면 반응형에 유용합니다.
```css
.thumb { width: 100%; aspect-ratio: 16 / 9; object-fit: cover; }
```

[[CSS day09 카페 키오스크]] 의 카페 메뉴, [[CSS day11 커뮤니티와 예약 사이트]] 의 갤러리에 그대로 적용됩니다.

### 2-2. `background` vs `<img>` 선택 기준

| 상황 | 선택 |
| --- | --- |
| 콘텐츠로서 의미가 있는 이미지 (상품 사진, 로고) | `<img>` — `alt` 제공, SEO |
| 순수 장식 (배경, 패턴, 아이콘) | `background-image` |

스크린 리더는 `background-image`를 읽지 못합니다. 의미 있는 이미지를 배경으로 넣으면 접근성 문제가 됩니다.

### 2-3. 그라디언트

```css
background: linear-gradient(to right, #ff7e5f, #feb47b);
background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
background: radial-gradient(circle, #fff, #000);

/* 이미지 위 어두운 오버레이 (텍스트 가독성) */
background:
  linear-gradient(rgba(0,0,0,0.5), rgba(0,0,0,0.5)),
  url(../assets/배경.jpg);
background-size: cover;
```

배너 이미지 위에 흰 글씨를 올릴 때 오버레이는 사실상 필수입니다. → [[CSS day10 카메라 강의 사이트]]

### 2-4. background 단축 속성

```css
background: #fff url(bg.jpg) no-repeat center / cover fixed;
/*         색상  이미지      반복       위치   / 크기  고정 */
```

`background-position / background-size` 순서로 **슬래시(/)** 를 씁니다. 순서를 틀리면 적용이 안 되니 학습 단계에서는 개별 속성이 안전합니다.

### 2-5. 스프라이트보다 나은 요즘 방법

CSS 스프라이트는 HTTP/1.1 시절의 최적화입니다. HTTP/2 이후로는 요청이 여러 개여도 부담이 적어서, 지금은 다음이 더 흔합니다.

- **SVG 아이콘** — 벡터라 확대해도 안 깨지고 CSS로 색 변경 가능
- **아이콘 폰트** — Font Awesome, Material Icons
- **SVG 스프라이트** — `<use href="#icon-home">`

```html
<svg width="24" height="24"><use href="icons.svg#home"></use></svg>
```
```css
svg { fill: currentColor; }   /* 부모의 color를 따라감 */
```

`fill: currentColor`가 핵심입니다. hover 시 글자색만 바꿔도 아이콘 색이 따라옵니다.

## 3. 더 나아가 알면 좋은 것

### 3-1. 반응형 이미지

```html
<img
  src="small.jpg"
  srcset="small.jpg 400w, medium.jpg 800w, large.jpg 1600w"
  sizes="(max-width: 600px) 100vw, 50vw"
  alt="설명" loading="lazy">
```

브라우저가 화면 크기와 해상도에 맞는 이미지를 알아서 고릅니다. 모바일에서 1600px 이미지를 받지 않아 데이터가 절약됩니다.

### 3-2. 이미지 포맷

| 포맷 | 특징 |
| --- | --- |
| JPG | 사진, 손실 압축 |
| PNG | 투명도 필요, 무손실 (용량 큼) |
| **WebP** | JPG 대비 25~35% 작음, 투명도 지원 |
| AVIF | WebP보다 더 작음 |
| SVG | 벡터, 아이콘·로고 |
| GIF | 애니메이션 (요즘은 video가 나음) |

`day02/assets/다운로드.webp`, `day08/practice/수박.webp`처럼 이미 WebP를 쓰고 계십니다.

`day14/assets/goods/*.gif`(8개)가 정지 이미지라면 WebP로 바꿨을 때 용량이 크게 줄어듭니다. GIF는 색상이 256개로 제한되어 사진에 부적합합니다.

### 3-3. filter와 backdrop-filter

```css
img:hover { filter: brightness(1.1) saturate(1.2); }
.disabled { filter: grayscale(1); }
.glass {
  background: rgba(255,255,255,0.2);
  backdrop-filter: blur(10px);   /* 뒤 배경을 흐리게 — 유리 효과 */
}
```

`grayscale(1)`은 품절 상품 표시에, `backdrop-filter`는 모달 배경이나 고정 헤더에 자주 쓰입니다.

### 3-4. 반응형 테이블

테이블은 모바일에서 가장 깨지기 쉽습니다.

```css
/* 방법 1: 가로 스크롤 */
.table-wrap { overflow-x: auto; }
```

```css
/* 방법 2: 카드 형태로 전환 */
@media (max-width: 600px) {
  table, thead, tbody, tr, th, td { display: block; }
  thead { display: none; }
  td::before { content: attr(data-label); font-weight: bold; margin-right: 8px; }
}
```

`content: attr(data-label)`은 [[CSS day14 position과 가상요소]] 의 가상요소 활용입니다.

### 3-5. 테이블 헤더 고정

```css
thead th {
  position: sticky;
  top: 0;
  background: #fff;   /* 배경 필수 */
  z-index: 1;
}
```

행이 많은 게시판 목록에서 유용합니다. → [[JS day14 게시판 CRUD]]

## 실습 파일

- `2026_FE/day15/exam/exam1.css`, `exam1.html` (테이블)
- `2026_FE/day15/exam/exam2.css`, `exam2.html`
- `2026_FE/day15/exam/exam3.css`, `exam3.html` (object-fit)
- `2026_FE/day15/exam/exam4.css`, `exam4.html` (background)
- `2026_FE/day15/assets/배경.jpg`, `패턴.jpg`, `인물.jpg`, `아이콘들.png`
- `2026_FE/day15/project/test.css`, `test.html`

## 관련 노트

[[CSS MOC]] · [[CSS day14 position과 가상요소]] · [[HTML day15 테이블 마크업]] · [[CSS day09 카페 키오스크]] · [[JS day14 게시판 CRUD]]
