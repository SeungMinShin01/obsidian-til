---
출처: Claude 분석
작성일: 2026-08-21
tags: [코드정리]
---

# CSS 패턴

> 상위: [[CSS]]
> 세부: [[CSS 반응형 심화]] · [[CSS 다크모드]]

레이아웃을 짤 때 통째로 가져다 쓰는 조합들이다. ※가 섞여 있다.

## 중앙 정렬 3형제

```css
.text-center { text-align: center; }

.block-center { width: 600px; margin: 0 auto; }

.flex-center {
    display: flex;
    justify-content: center;
    align-items: center;
}
```

- 인라인 내용(글자·이미지)은 text-align, 블록 상자 자체는 margin auto, 가로+세로 동시는 flex — **무엇을 가운데 두느냐**로 셋 중 하나를 고른다

## 페이지 뼈대

```css
.wrapper {
    max-width: 1200px;
    margin: 0 auto;
    padding: 0 16px;
}
```

- 본문 폭을 제한하고 가운데 두는 컨테이너다. 거의 모든 사이트의 최상위에 이 상자가 있다
- max-width라서 좁은 화면에서는 자연스럽게 화면 폭을 따라간다(반응형의 절반은 이걸로 해결)

## 카드

```css
.card {
    background: #fff;
    border: 1px solid #e5e5e5;
    border-radius: 8px;
    padding: 16px;
    box-shadow: 0 1px 4px rgba(0, 0, 0, 0.08);
}
```

- 흰 배경 + 얇은 테두리 + 둥근 모서리 + 옅은 그림자 — "카드"의 표준 레시피다
- box-shadow 값 순서: x이동 y이동 번짐 색. 그림자는 옅게(투명도 0.1 내외)가 요즘 감각이다

## 미디어쿼리 — 반응형 분기 ※

```css
.cards { display: flex; flex-wrap: wrap; }

@media (max-width: 768px) {
    .sidebar { display: none; }
    .cards { flex-direction: column; }
}
```

- `@media (max-width: 768px)` 블록 안 규칙은 그 폭 이하에서만 적용된다 — 모바일에서 사이드바 숨기기·세로 쌓기
- 분기점(breakpoint)은 768px(태블릿)·1024px(노트북)이 관례적 출발점이다

## CSS 변수 ※

```css
:root {
    --primary: #1a73e8;
    --gap: 16px;
}

.button { background: var(--primary); }
.list { gap: var(--gap); }
```

- `:root`에 선언하고 `var()`로 꺼내 쓴다. 색·간격을 한 곳에서 바꾸면 전체에 반영된다
- 다크모드·테마 교체가 이 변수들을 재정의하는 방식으로 돌아간다

## hover 전환 ※

```css
.button {
    transition: background 0.2s, transform 0.2s;
}
.button:hover {
    background: #1557b0;
    transform: translateY(-2px);
}
```

- transition을 **평소 상태에** 걸어두면 hover로 갈 때·돌아올 때 모두 부드럽다(:hover 쪽에 걸면 돌아올 때 뚝 끊긴다)
- "살짝 떠오르는 버튼" = translateY(-2px) + 그림자 강화가 정석 조합이다
