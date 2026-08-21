---
출처: Claude 분석
작성일: 2026-08-21
tags: [코드정리]
---

# CSS 고급 선택자

> 상위: [[CSS 선택자]]

전부 ※. 기본 선택자로 안 잡히는 "조건부" 선택들이다.

## :not — 빼고 고르기

```css
li:not(.active) { opacity: 0.6; }
input:not([type="checkbox"]) { width: 100%; }
```

- "이것만 빼고 전부"를 클래스 추가 없이 처리한다. 활성 탭만 남기고 흐리게가 한 줄이다

## :is · :where — 반복 묶기

```css
:is(h1, h2, h3) a { color: inherit; }
:where(article, section) p { margin-bottom: 1em; }
```

- `h1 a, h2 a, h3 a`처럼 반복하던 것을 묶는다
- 차이 하나: `:is`는 괄호 안 가장 높은 점수를 따르고 `:where`는 **0점**이다 — 나중에 쉽게 덮어쓸 기본 스타일은 :where로 깔아 둔다

## :has — 자식으로 부모 고르기

```css
.card:has(img) { padding: 0; }
label:has(input:checked) { font-weight: 700; }
form:has(:invalid) button[type="submit"] { opacity: 0.5; }
```

- 오랫동안 불가능했던 "무엇을 **가진** 요소" 선택이다. 이미지 있는 카드만 다른 레이아웃, 체크된 라벨 강조가 JS 없이 된다
- 세 번째 줄: 폼에 잘못된 입력이 있으면 제출 버튼을 흐리게 — 검증 시각화를 CSS만으로

## nth 계열 정밀 선택

```css
li:nth-child(3) { }
li:nth-child(2n) { }
li:nth-child(3n + 1) { }
li:nth-last-child(2) { }
p:first-of-type { }
img:nth-of-type(2) { }
```

- `2n` 짝수, `2n+1` 홀수, `3n+1` 3개마다 첫 번째 — 격자에서 줄 첫 칸만 고르기가 된다
- `nth-child`는 형제 전체에서 순서를 세고, `nth-of-type`은 **같은 태그끼리만** 센다 — 중간에 다른 태그가 끼면 결과가 달라지니 구분해서 쓴다

## 상태 조합

```css
input:disabled { background: #f5f5f5; }
input:checked + label { color: royalblue; }
li:hover > .actions { visibility: visible; }
.item:last-child { border-bottom: none; }
```

- `:checked + label`은 체크박스 바로 뒤 라벨 — 커스텀 체크박스 구현의 핵심 배선이다
- 행에 올렸을 때만 버튼 보이기(`li:hover > .actions`)처럼 상태 + 결합자를 조합하면 JS 없이 꽤 많은 인터랙션이 된다
