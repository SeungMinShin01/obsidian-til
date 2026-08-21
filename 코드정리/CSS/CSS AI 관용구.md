---
출처: Claude 분석
작성일: 2026-08-21
tags: [코드정리]
---

# CSS AI 관용구

> 상위: [[CSS]]

전부 ※. AI가 생성하는 CSS 첫머리에 늘 깔리는 것들의 해독표다.

## 리셋 3종 세트

```css
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}
```

- 브라우저 기본 여백을 전부 0으로 밀고 border-box로 통일한다 — "예측 가능한 상태에서 시작"이라는 선언이다
- AI 생성 CSS의 첫 블록이 거의 항상 이것이고, 없으면 h1·body의 기본 margin이 레이아웃을 흔든다

## :root 변수 묶음

```css
:root {
    --bg: #ffffff;
    --text: #1f2937;
    --primary: #2563eb;
    --radius: 8px;
    --shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}
```

- 색·둥글기·그림자를 변수로 몰아 두는 스타일이다. 아래 코드에 `var(--primary)`가 보이면 값은 전부 여기서 찾으면 된다

## clamp — 반응형 크기 한 줄

```css
h1 { font-size: clamp(1.5rem, 4vw, 2.5rem); }
.container { width: min(90%, 1200px); }
```

- `clamp(최소, 선호값, 최대)` — 화면에 따라 4vw로 움직이되 1.5rem 아래·2.5rem 위로는 안 나간다. 미디어쿼리 없는 반응형 글자 크기다
- `min(90%, 1200px)`은 "둘 중 작은 쪽" — 넓은 화면에선 1200px, 좁으면 90%. wrapper 관용구의 함축형이다

## 배치 축약

```css
.overlay { position: absolute; inset: 0; }
.stack > * + * { margin-top: 12px; }
.row { display: flex; align-items: center; gap: 8px; }
```

- `inset: 0` = top/right/bottom/left 0 네 줄의 축약(꽉 덮기)
- `> * + *`는 "첫 자식 빼고 전부" — 사이 간격만 주는 트릭이다(요즘은 gap으로 대체되지만 읽을 줄은 알아야 한다)
- flex + align-items: center + gap 조합은 "아이콘과 글자를 나란히"의 기본형이다

## 이미지·비율

```css
.thumb { aspect-ratio: 16 / 9; object-fit: cover; width: 100%; }
```

- `aspect-ratio`가 높이를 비율로 자동 계산한다(높이 하드코딩 불필요). cover와 세트로 썸네일 규격 통일이 세 속성으로 끝난다

## 접근성·상태 관용구

```css
.visually-hidden {
    position: absolute;
    width: 1px; height: 1px;
    overflow: hidden;
    clip-path: inset(50%);
}

.button:disabled { opacity: 0.5; cursor: not-allowed; }
:focus-visible { outline: 2px solid var(--primary); }
```

- visually-hidden은 화면에선 숨기고 스크린리더에는 남기는 표준 클래스다(display: none과 목적이 다르다)
- disabled 반투명 + not-allowed 커서, 키보드 포커스에만 테두리(:focus-visible) — AI가 습관처럼 넣는 상태 스타일이다
