---
출처: Claude 분석
작성일: 2026-08-21
tags: [코드정리]
---

# HTML 메타와 SEO

> 상위: [[HTML 문서 구조]]

전부 ※. head 안의 몇 줄이 검색 노출과 공유 미리보기를 결정한다.

## 기본 메타

```html
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>도서 대여 관리 - 홈</title>
<meta name="description" content="도서 등록·대여·반납을 관리하는 서비스입니다.">
<link rel="icon" href="favicon.ico">
```

- title은 브라우저 탭이자 검색 결과의 제목이다. 페이지마다 다르게, "핵심 - 사이트명" 꼴이 관례다
- description은 검색 결과 제목 아래 요약문이다. 순위 자체보다 **클릭율**에 영향을 준다
- favicon은 탭 아이콘이다. 없으면 콘솔에 404가 뜨는 것으로 자주 눈에 띈다

## 공유 미리보기 — Open Graph

```html
<meta property="og:title" content="도서 대여 관리">
<meta property="og:description" content="등록·대여·반납 한 번에">
<meta property="og:image" content="https://example.com/og.png">
<meta property="og:url" content="https://example.com">
```

- 카톡·슬랙·트위터에 링크를 붙였을 때 뜨는 카드(제목·설명·이미지)가 이 네 줄에서 나온다
- og:image는 절대 URL이어야 하고 1200×630이 표준 크기다. 이 태그가 없으면 미리보기가 밋밋한 텍스트로만 뜬다

## 검색엔진 제어

```html
<meta name="robots" content="noindex">
<link rel="canonical" href="https://example.com/list">
```

- `noindex`는 "검색 결과에 넣지 마라"다 — 관리자 페이지·테스트 페이지에 붙인다
- canonical은 같은 내용이 여러 주소로 열릴 때(쿼리스트링 등) "정본은 이 주소"라고 알려주는 태그다

## SEO의 몸통은 마크업이다

- 메타보다 중요한 것: 페이지당 h1 하나, 제목 계층 지키기, a 태그에 의미 있는 텍스트("여기 클릭" 금지), img alt 채우기, 시맨틱 구역 태그
- 검색엔진은 결국 HTML 구조를 읽는다 — 문서 구조를 바르게 쓰는 것 자체가 최고의 SEO 기본기다
