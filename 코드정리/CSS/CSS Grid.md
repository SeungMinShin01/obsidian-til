---
출처: Claude 분석
작성일: 2026-08-21
tags: [코드정리]
---

# CSS Grid

> 상위: [[CSS flexbox]]

전부 ※. 행과 열을 **동시에** 설계하는 2차원 레이아웃이다.

## 기본

```css
.grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 16px;
}
```

- 부모에 켜고 열 구성을 선언하면 자식들이 자동으로 칸에 채워진다
- `1fr`은 남은 공간의 비율 단위다. `repeat(3, 1fr)` = 균등 3열, `240px 1fr` = 고정 사이드바 + 가변 본문
- flexbox와의 구분: 한 줄 배치·정렬은 flex, **행×열 격자**(카드 그리드, 대시보드)는 grid가 자연스럽다

## 반응형 카드 그리드 — 외우는 한 줄

```css
.cards {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
    gap: 16px;
}
```

- "최소 220px을 보장하면서 들어갈 수 있는 만큼 열을 만들어라" — 화면이 좁아지면 열이 저절로 줄어든다
- 미디어쿼리 없이 반응형 그리드가 되는 가장 유명한 관용구다

## 칸 병합

```css
.header { grid-column: 1 / -1; }
.feature { grid-column: span 2; grid-row: span 2; }
```

- `1 / -1`은 첫 선부터 마지막 선까지 = 가로 전체를 차지한다(머리글 행)
- `span 2`는 두 칸 병합이다. 표의 colspan/rowspan과 같은 발상이다

## 영역 이름으로 배치

```css
.layout {
    display: grid;
    grid-template-areas:
        "header header"
        "sidebar main"
        "footer footer";
    grid-template-columns: 240px 1fr;
}

.layout > header { grid-area: header; }
.layout > aside { grid-area: sidebar; }
```

- 레이아웃을 **그림 그리듯** 문자열로 선언한다. 어디에 뭐가 오는지 코드만 봐도 보이는 게 장점이다
