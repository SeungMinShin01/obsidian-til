---
출처: Claude 분석
작성일: 2026-08-21
tags: [코드정리]
---

# CSS 웹폰트와 아이콘

> 상위: [[CSS 텍스트와 배경]]

전부 ※. 시스템 글꼴을 벗어나는 순간 필요한 것들이다.

## 웹폰트 불러오기 — link 방식

```html
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;700&display=swap" rel="stylesheet">
```

```css
body { font-family: "Noto Sans KR", sans-serif; }
```

- 구글 폰트 등에서 link 태그를 복사해 head에 붙이고, CSS에서 이름으로 지정한다 — 가장 흔한 경로다
- `display=swap`은 폰트 로딩 전에 기본 글꼴로 먼저 보여준다(빈 화면 방지)
- 한글 폰트는 용량이 커서 **쓸 굵기(400·700)만** 고르는 게 속도에 중요하다

## @font-face — 파일로 직접

```css
@font-face {
    font-family: "MyFont";
    src: url("fonts/MyFont.woff2") format("woff2");
    font-weight: 400;
    font-display: swap;
}
```

- 폰트 파일을 프로젝트에 두고 직접 등록하는 방식이다. woff2가 표준 포맷이다
- 같은 이름으로 weight별 블록을 여러 개 선언하면 `font-weight: 700`일 때 알맞은 파일이 쓰인다

## 아이콘 세 가지 길

```html
<button>🔍 검색</button>

<button><img src="icons/search.svg" alt="" width="16"> 검색</button>

<button><svg width="16" height="16" viewBox="0 0 24 24">…</svg> 검색</button>
```

- 이모지: 설치 0초, 가장 간단. 다만 OS마다 모양이 다르다
- SVG 파일/인라인: 요즘 표준. 인라인 svg는 `fill: currentColor`로 **글자색을 따라가게** 할 수 있어 hover 색 전환이 공짜다
- 아이콘 폰트(Font Awesome 등)는 클래스 하나로 쓰는 방식인데, 최근엔 SVG 쪽이 권장이다

## 숫자·코드 표시용 관용구

```css
.price { font-variant-numeric: tabular-nums; }
code { font-family: "D2Coding", Consolas, monospace; }
.clamp2 {
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
    overflow: hidden;
}
```

- `tabular-nums`는 숫자 폭을 고정해 표에서 자릿수가 흔들리지 않게 한다(가격·통계 표 필수)
- 코드·아이디는 monospace 계열로 — 저장 예시와 실제 화면이 같은 폭으로 보인다
- `.clamp2` 4줄 세트는 "두 줄 말줄임"의 고정 관용구다(한 줄 말줄임과 다른 세트)
