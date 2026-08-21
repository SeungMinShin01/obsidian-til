---
출처: Claude 분석
작성일: 2026-08-21
tags: [코드정리]
---

# CSS 반응형 심화

> 상위: [[CSS 패턴]]

전부 ※. 미디어쿼리 한 블록을 넘어 "전략"으로서의 반응형이다.

## 모바일 퍼스트

```css
.cards { display: flex; flex-direction: column; gap: 12px; }

@media (min-width: 768px) {
    .cards { flex-direction: row; flex-wrap: wrap; }
}

@media (min-width: 1024px) {
    .container { max-width: 1200px; }
}
```

- 기본 스타일을 **좁은 화면 기준**으로 쓰고 `min-width`로 넓은 화면을 얹는 방식이다(데스크톱 기준 + max-width로 깎는 것의 반대)
- 이유: 모바일 스타일이 단순해서 기본값으로 두기 좋고, 깜빡한 구간이 생겨도 좁은 화면이 안전하게 남는다
- 분기점은 콘텐츠가 깨지는 지점에서 정하는 게 원칙이되, 768/1024가 무난한 출발점이다

## 쿼리 없이 버티는 도구들

```css
.container { width: min(100% - 32px, 1200px); margin-inline: auto; }
h1 { font-size: clamp(1.4rem, 3vw + 0.5rem, 2.2rem); }
.grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(220px, 1fr)); gap: 16px; }
img { max-width: 100%; height: auto; }
```

- 이 네 줄이 "미디어쿼리 최소화 세트"다: 가운데 컨테이너, 흐르는 글자 크기, 자동 줄어드는 그리드, 넘치지 않는 이미지
- `min(100% - 32px, 1200px)`은 wrapper + 좌우 패딩을 한 식으로 합친 관용구다

## 반응형에서 자주 바꾸는 것들

```css
@media (max-width: 767px) {
    .sidebar { display: none; }
    .nav-links { flex-direction: column; }
    .table-wrap { overflow-x: auto; }
    .grid-3 { grid-template-columns: 1fr; }
}
```

- 좁은 화면의 단골 처리: 사이드바 숨기기(또는 햄버거 메뉴), 가로 메뉴 세로로, 표는 가로 스크롤 상자에 가두기, 다열 그리드 1열로
- 표를 억지로 줄이는 것보다 `overflow-x: auto` 래퍼가 현실적인 답인 경우가 많다

## 화면 말고 다른 조건

```css
@media (hover: hover) {
    .card:hover { transform: translateY(-4px); }
}

@media print {
    nav, footer { display: none; }
}
```

- `(hover: hover)`는 마우스가 있는 기기에서만 — 터치 기기에서 hover가 눌러붙는 문제를 피한다
- print 쿼리로 인쇄 때 메뉴·버튼을 걷어낸다. 컨테이너 쿼리(@container)는 "부모 폭 기준 반응"이라는 다음 단계 키워드로 알아두면 된다
