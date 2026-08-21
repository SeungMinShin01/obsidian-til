---
출처: Claude 분석
작성일: 2026-08-21
tags: [코드정리]
---

# CSS 선택자

> 상위: [[CSS]]
> 세부: [[CSS 우선순위]] · [[CSS 고급 선택자]]

## 기본 선택자

```css
p { color: gray; }
.card { padding: 16px; }
#header { height: 60px; }
* { box-sizing: border-box; }
```

- 태그는 그대로, 클래스는 `.`, 아이디는 `#`, 전체는 `*`다
- 클래스는 여러 요소에 재사용하고, 아이디는 페이지에 하나뿐인 요소에 쓴다 — 스타일은 클래스 위주로 가는 게 관례다
- JS의 `querySelector`가 받는 문자열이 바로 이 선택자 문법이다

## 결합 선택자

```css
nav a { color: white; }
ul > li { list-style: none; }
h2 + p { margin-top: 0; }
input.error { border-color: red; }
```

- 공백은 **자손 전부**(몇 단계든), `>`는 **직계 자식만**이다
- `+`는 바로 다음 형제 하나. `h2 + p`는 제목 바로 뒤 문단만 잡는다
- `input.error`처럼 붙여 쓰면 "그 태그이면서 그 클래스"라는 AND 조건이다(공백 있고 없고가 완전히 다른 뜻)

## 가상 클래스

```css
a:hover { text-decoration: underline; }
button:active { transform: scale(0.98); }
input:focus { outline: 2px solid royalblue; }
li:first-child { border-top: none; }
tr:nth-child(even) { background: #f5f5f5; }
li:last-child { border-bottom: none; }
```

- `:hover` 올렸을 때, `:active` 누르는 중, `:focus` 입력 커서가 있을 때 — 상태에 따른 스타일이다
- `:nth-child(even/odd/3n)`으로 줄무늬 표·규칙적 배치를 만든다. `first-child`/`last-child`로 양 끝만 다르게 처리한다

## 속성 선택자 ※

```css
input[type="text"] { padding: 8px; }
a[target="_blank"] { color: green; }
```

- `[속성="값"]`으로 HTML 속성 기준 선택이 된다. input 종류별 스타일에 자주 쓴다

## 그룹

```css
h1, h2, h3 { font-family: "Pretendard", sans-serif; }
```

- 쉼표로 여러 선택자에 같은 규칙을 한 번에 준다
