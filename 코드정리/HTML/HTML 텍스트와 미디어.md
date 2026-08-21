---
출처: Claude 분석
작성일: 2026-08-21
tags: [코드정리]
---

# HTML 텍스트와 미디어

> 상위: [[HTML]]
> 세부: [[HTML 이미지 최적화]]

## 제목과 문단

```html
<h1>가장 큰 제목</h1>
<h2>절 제목</h2>
<p>문단. <strong>중요</strong>하거나 <em>강조</em>할 부분.</p>
<hr>
<br>
```

- h1~h6은 크기가 아니라 **문서의 계층**이다. h1은 페이지에 하나, 단계를 건너뛰지 않는 게 원칙이다(스타일은 CSS 몫)
- strong은 굵게+중요 의미, em은 기울임+강조 의미다. 순수 모양만 바꿀 거면 CSS를 쓴다
- br은 줄바꿈 하나. 문단 구분은 br 두 개가 아니라 p 태그로 한다

## 링크

```html
<a href="list.html">목록으로</a>
<a href="view.html?no=3">3번 글</a>
<a href="https://example.com" target="_blank" rel="noopener">새 탭</a>
<a href="#section2">페이지 내 이동</a>
```

- href가 이동 목적지다. `?no=3` 쿼리스트링으로 데이터를 실어 보내면 JS가 URLSearchParams로 꺼낸다 — 목록→상세 연결의 핵심
- `target="_blank"`는 새 탭 열기이고 `rel="noopener"`를 관례로 함께 붙인다
- `#아이디`는 같은 페이지 안에서 그 요소로 스크롤한다

## 목록

```html
<ul>
    <li>순서 없는 항목</li>
</ul>
<ol>
    <li>순서 있는 항목</li>
</ol>
```

- ul 점 목록, ol 번호 목록, 항목은 전부 li다. 내비게이션 메뉴도 관례상 ul > li > a 구조로 만든다
- li 안에 ul을 넣으면 중첩 목록이 된다

## 이미지와 미디어

```html
<img src="cat.jpg" alt="고양이 사진">
<video src="clip.mp4" controls width="640"></video>
<audio src="bgm.mp3" controls></audio>
```

- img의 `alt`는 이미지가 못 뜰 때·스크린리더가 읽을 대체 텍스트다. **항상 채운다**(장식용이면 `alt=""`)
- video·audio는 `controls`가 있어야 재생 버튼이 보인다. autoplay는 muted와 함께가 아니면 브라우저가 막는 경우가 많다
- 콘텐츠인 이미지는 img로, 장식 배경은 CSS background로 — 의미 유무로 갈라 쓴다
