---
출처: Claude 분석
작성일: 2026-08-21
tags: [코드정리]
---

# HTML 접근성 기초

> 상위: [[HTML 문서 구조]]

전부 ※. 스크린리더·키보드 사용자에게도 동작하는 페이지의 최소 규칙이다.

## 올바른 태그가 90%다

```html
<button type="button">삭제</button>
<a href="list.html">목록</a>
<label for="title">제목</label><input id="title">
```

- button은 키보드 포커스·엔터/스페이스 동작·스크린리더 안내가 **공짜로** 따라온다. div에 onclick을 단 가짜 버튼은 이걸 전부 잃는다
- "동작은 button, 이동은 a, 입력엔 label" — 이 세 가지만 지켜도 접근성의 대부분이 해결된다

## 이름 없는 요소에 이름 붙이기

```html
<button aria-label="검색">🔍</button>
<nav aria-label="주 메뉴">…</nav>
<input aria-label="검색어" placeholder="검색">
```

- 화면에 글자가 없는 아이콘 버튼은 스크린리더에겐 "버튼"으로만 읽힌다 — aria-label이 이름을 준다
- placeholder는 라벨 대용이 못 된다(입력하면 사라짐). label이 어려운 구조면 aria-label로라도 이름을 남긴다

## 상태 전달

```html
<button aria-expanded="false" aria-controls="menu">메뉴</button>
<div role="alert">저장에 실패했습니다.</div>
<img src="chart.png" alt="8월 대여 건수 상위 5권 막대그래프">
```

- 열림/닫힘 같은 상태는 aria-expanded로, JS가 토글할 때 값도 같이 바꾼다
- `role="alert"` 영역에 넣은 텍스트는 스크린리더가 즉시 읽어준다 — 에러 메시지 자리
- alt는 이미지의 **내용**을 쓴다("차트 이미지"가 아니라 무엇을 보여주는지)

## 키보드로만 써보기

```css
:focus-visible { outline: 2px solid royalblue; }
```

- 검사법이 간단하다: 마우스 없이 Tab·엔터만으로 모든 기능이 되는지 눌러 본다. 안 닿는 요소가 있으면 태그 선택이 틀렸을 가능성이 크다
- `outline: none`으로 포커스 테두리를 지우는 건 금물이다 — 지우고 싶으면 :focus-visible로 대체 스타일을 준다
- 색 대비는 글자 대 배경 4.5:1이 기준이다(연회색 글자 남용 주의)
