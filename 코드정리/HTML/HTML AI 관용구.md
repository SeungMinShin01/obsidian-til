---
출처: Claude 분석
작성일: 2026-08-21
tags: [코드정리]
---

# HTML AI 관용구

> 상위: [[HTML]]

전부 ※. AI가 생성하는 HTML에서 반복해서 보이는 함축 표현들이다.

## data-* — 요소에 데이터 싣기

```html
<button class="btn-delete" data-no="3">삭제</button>
<li data-category="java" data-price="15000">…</li>
```

- `data-이름="값"`은 표준이 허용하는 자유 속성이다. JS에서 `el.dataset.no`로 읽는다
- "이 버튼이 몇 번 글의 버튼인가"를 HTML에 실어 두고, 클릭 이벤트에서 dataset으로 꺼내는 게 목록 조작의 표준 배선이다

## button vs a — 동작이냐 이동이냐

```html
<a href="list.html">목록으로</a>
<button type="button" onclick="save()">저장</button>
```

- 페이지 **이동**은 a, 페이지 안 **동작**은 button — AI가 `<a href="#" onclick=...>`을 피하고 button을 쓰는 이유다
- 폼 안의 button은 기본이 submit이므로 동작용이면 `type="button"`을 명시하는 것까지가 관용이다

## 접근성 한 줄들

```html
<button aria-label="닫기">×</button>
<img src="deco.png" alt="">
<nav aria-label="주 메뉴">…</nav>
```

- `aria-label`은 화면에 글자가 없는 버튼(×, 아이콘)에 스크린리더용 이름을 붙인다
- 장식 이미지는 `alt=""`(빈 값)로 "읽지 말고 건너뛰어라"를 표시한다 — alt 생략과는 다른 의미다

## 템플릿·조각 관용구

```html
<div id="app"></div>

<template id="rowTemplate">
    <tr><td class="no"></td><td class="title"></td></tr>
</template>
```

- 빈 컨테이너(`#app`, `#tableTbody`)를 두고 JS가 내용을 채우는 구조 — "HTML은 그릇, 데이터는 JS"의 분업이다
- `<template>`은 화면에 안 보이는 조각 원본이다. JS가 복제(cloneNode)해서 값만 채워 붙인다 — innerHTML 문자열 조립의 대안

## meta·링크 상용구

```html
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta name="description" content="페이지 소개">
<link rel="icon" href="favicon.ico">
<script src="app.js" defer></script>
```

- viewport는 모바일 필수, description은 검색 결과에 뜨는 소개문이다
- `defer`는 "HTML 파싱 끝난 뒤 실행" — 스크립트를 head에 두고도 body 끝에 둔 효과를 낸다. AI가 head에 script를 넣을 때 거의 항상 붙어 있다

## 시맨틱 뼈대 습관

```html
<main>
    <section aria-labelledby="list-title">
        <h2 id="list-title">도서 목록</h2>
        …
    </section>
</main>
```

- AI는 div 대신 header/main/section/footer를 기본으로 깔고, 섹션마다 제목(h2)을 두는 습관이 있다 — 구역 이름이 곧 문서 개요가 된다
