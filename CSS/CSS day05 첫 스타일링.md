---
출처: Claude 분석
원본: KDT_2026/2026_FE/day05
작성일: 2026-08-10
tags: [css, day05, 시작]
---

# CSS day05 — 첫 스타일링

> 실습 파일: `day05/activity2.html`, `activity2.css`, `SKULOGO.png`, `example.png`
> 허브: [[CSS MOC]] · 다음: [[CSS day06 선택자와 기본 속성]]

## 1. 배운 내용

JS 반복문을 배우던 날([[JS day05 반복문]])에 CSS 파일을 처음 분리해 만든 실습입니다.

### 1-1. CSS 파일 분리

```html
<head>
  <link rel="stylesheet" href="activity2.css" />
</head>
```

[[HTML day02 문서 구조와 미디어]] 에서 `style="..."` 인라인으로 쓰던 것을 외부 파일로 옮기는 첫 단계입니다.

**세 가지 적용 방법의 우선순위**

| 방법 | 우선순위 | 재사용성 |
| --- | --- | --- |
| 인라인 `style=""` | 가장 높음 | 없음 |
| `<style>` 내부 시트 | 중간 | 한 문서 안 |
| 외부 `.css` 파일 | 중간 | **전체 문서** |

우선순위는 인라인이 높지만, **재사용성 때문에 외부 파일이 표준**입니다.

### 1-2. 이 실습에서 다룬 것

`SKULOGO.png`, `example.png`를 배치하고 스타일을 입히는 과제입니다. 이 단계에서 자연스럽게 만나는 문제들:

- 이미지 크기 조절 (`width`, `height`)
- 이미지가 찌그러지는 문제 → [[CSS day15 테이블과 배경]] 의 `object-fit`
- 요소를 가운데 두기 → `margin: 0 auto` 또는 [[CSS day08 flexbox]]
- 텍스트와 이미지를 나란히 → `display: inline-block` 또는 flex

## 2. 추가로 알면 좋은 활용법

### 2-1. 시작할 때 깔고 가면 좋은 3줄

```css
* { box-sizing: border-box; margin: 0; padding: 0; }
```

- `box-sizing: border-box` — `width`가 padding·border를 포함하게 됩니다. 크기 계산이 훨씬 직관적입니다
- `margin: 0` — 브라우저가 `<body>`에 기본으로 주는 8px 여백을 없앱니다
- `padding: 0` — `<ul>`의 기본 들여쓰기를 없앱니다

이 3줄만 있어도 "왜 딱 안 맞지?" 하는 상황이 크게 줄어듭니다.

### 2-2. 이미지 기본 처리

```css
img {
  display: block;      /* 아래 미세한 여백 제거 */
  max-width: 100%;     /* 부모보다 커지지 않게 */
  height: auto;        /* 비율 유지 */
}
```

`<img>`는 기본이 `inline`이라 글자처럼 취급되어 **아래에 3~4px 여백**이 생깁니다. 원인을 모르면 한참 헤매는 부분입니다. `display: block`으로 해결됩니다.

### 2-3. 가운데 정렬 3가지

```css
/* 블록 요소 가로 가운데 */
.box { width: 500px; margin: 0 auto; }

/* 텍스트·인라인 요소 가운데 */
.parent { text-align: center; }

/* 완전한 가운데 (권장) */
.parent { display: flex; justify-content: center; align-items: center; }
```

`margin: 0 auto`는 **`width`가 있어야** 동작합니다. 이걸 몰라서 안 되는 경우가 많습니다.

### 2-4. 색상 표기 4가지

```css
color: green;                  /* 색상명 */
color: rgb(0, 255, 0);         /* RGB */
color: rgba(0, 255, 0, 0.5);   /* 투명도 포함 */
color: #008000;                /* 헥스코드 */
color: #0f08;                  /* 4자리 축약 + 알파 */
```

VSCode에서 색상 코드 옆의 작은 사각형을 클릭하면 컬러 피커가 뜹니다.

### 2-5. 개발자 도구로 CSS 배우기

F12 → Elements 탭에서
- 요소를 클릭하면 **적용된 모든 CSS**가 보입니다
- 취소선이 그어진 속성 = 우선순위에서 밀린 것
- 값을 **직접 수정**해서 즉시 확인할 수 있습니다
- 박스 모델 다이어그램으로 margin/border/padding/content 크기를 볼 수 있습니다

CSS는 이 도구로 실험하며 배우는 게 가장 빠릅니다.

## 3. 더 나아가 알면 좋은 것

### 3-1. CSS 파일 구조화

프로젝트가 커지면 파일을 나눕니다.

```
css/
├── reset.css      브라우저 기본값 초기화
├── common.css     공통 (헤더, 푸터, 버튼)
├── layout.css     레이아웃
└── page.css       페이지별
```

```html
<link rel="stylesheet" href="css/reset.css" />
<link rel="stylesheet" href="css/common.css" />
```

**순서가 중요합니다.** 나중에 로드된 파일이 우선입니다.

`2026_FE`에 `common/reset.css`를 만들면 day05~day15의 모든 실습에서 재사용할 수 있습니다.

### 3-2. 클래스 이름 짓기

```css
/* BEM 방식 */
.card { }              /* 블록 */
.card__title { }       /* 요소 */
.card--featured { }    /* 변형 */
```

이름만 봐도 구조가 보입니다. 협업할 때 특히 유용합니다.

### 3-3. 다음 단계

| 배울 것 | 노트 |
| --- | --- |
| 선택자와 우선순위 | [[CSS day06 선택자와 기본 속성]] |
| 레이아웃의 핵심 | [[CSS day08 flexbox]] |
| 요소 겹치기 | [[CSS day14 position과 가상요소]] |
| 이미지 다루기 | [[CSS day15 테이블과 배경]] |

## 실습 파일

- `2026_FE/day05/activity2.html`, `activity2.css`
- `2026_FE/day05/SKULOGO.png`, `example.png`

## 관련 노트

[[CSS MOC]] · [[CSS day06 선택자와 기본 속성]] · [[JS day05 반복문]] · [[HTML day02 문서 구조와 미디어]]
