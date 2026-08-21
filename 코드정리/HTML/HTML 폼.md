---
출처: Claude 분석
작성일: 2026-08-21
tags: [코드정리]
---

# HTML 폼

> 상위: [[HTML]]
> 세부: [[HTML 폼 검증]] · [[HTML 폼 요소 심화]]

## form과 input

```html
<form id="writeForm">
    <label for="titleInput">제목</label>
    <input type="text" id="titleInput" placeholder="제목을 입력하세요">

    <label for="pwdInput">비밀번호</label>
    <input type="password" id="pwdInput">

    <button type="submit">등록</button>
</form>
```

- input의 값은 JS에서 `.value`로 읽고 쓴다. id가 JS·label 양쪽의 연결 고리다
- `label for="아이디"`는 라벨 클릭만으로 입력창에 커서가 가게 한다 — 폼 접근성의 기본기
- button의 기본 type은 submit이라 폼 안에서 누르면 **페이지가 새로고침**된다. JS로 처리할 거면 `type="button"`으로 바꾸거나 submit 이벤트에서 preventDefault를 한다

## input 종류

```html
<input type="text">
<input type="password">
<input type="number" min="1" max="99">
<input type="date">
<input type="checkbox" id="agree">
<input type="radio" name="grade" value="A">
<input type="radio" name="grade" value="B">
<input type="file" accept="image/*">
```

- type만 바꾸면 키보드·달력·체크박스가 알아서 바뀐다. number·date는 모바일에서 특히 이득이 크다
- 라디오는 **name이 같은 것끼리** 한 그룹이 되어 하나만 선택된다. 체크박스·라디오의 선택 여부는 `.value`가 아니라 `.checked`로 읽는다

## 여러 줄과 선택 목록

```html
<textarea id="contentInput" rows="5"></textarea>

<select id="categorySelect">
    <option value="">선택하세요</option>
    <option value="java">Java</option>
    <option value="js" selected>JavaScript</option>
</select>
```

- 여러 줄 입력은 textarea다. 값 읽기는 역시 `.value`
- select의 값은 선택된 option의 value다. 첫 option을 빈 값 안내문으로 두면 "미선택" 검증이 쉬워진다(`if (!sel.value)`)

## form 제출

```html
<form action="/search" method="get">
<form action="/boards" method="post">
```

- action은 보낼 주소, method는 방식이다. get은 값이 URL 쿼리스트링에 붙고(검색), post는 본문에 실린다(등록)
- 백엔드 없이 JS로만 처리하는 동안은 action 없이 submit 이벤트를 가로채는 방식(preventDefault)을 쓴다
