---
출처: Claude 분석
작성일: 2026-08-21
tags: [코드정리]
---

# HTML 문서 구조

> 상위: [[HTML]]
> 세부: [[HTML 메타와 SEO]] · [[HTML 접근성 기초]]

## 기본 골격

```html
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>페이지 제목</title>
    <link rel="stylesheet" href="style.css">
</head>
<body>

    <script src="app.js"></script>
</body>
</html>
```

- head는 화면에 안 보이는 문서 정보(제목·인코딩·연결 파일), body가 실제 내용이다
- `charset="UTF-8"`이 없으면 한글이 깨진다. viewport 메타는 모바일에서 축소되지 않게 하는 반응형의 전제 조건이다
- CSS는 head에서 link로, JS는 **body 끝에서** script로 읽는 게 기본형이다 — 요소들이 다 만들어진 뒤 JS가 돌아야 querySelector가 null을 안 받는다
- 여러 JS 파일을 이어 붙이면 앞 파일의 함수·변수를 뒤 파일이 쓸 수 있다(common.js를 먼저 두는 이유)

## 시맨틱 태그 — 구역에 의미 붙이기

```html
<body>
    <header>로고·내비게이션</header>
    <nav>메뉴</nav>
    <main>
        <section>
            <h1>주제</h1>
            <article>독립된 글 하나</article>
        </section>
        <aside>사이드바</aside>
    </main>
    <footer>바닥글</footer>
</body>
</html>
```

- 전부 div와 똑같이 동작하지만 **이름이 역할을 말한다.** 검색엔진·스크린리더·다른 개발자가 구조를 바로 읽는다
- main은 페이지에 하나만 둔다. section은 주제 묶음, article은 떼어내도 말이 되는 독립 콘텐츠(게시글 하나)다
- 마땅한 의미가 없는 순수 묶음·꾸밈용 상자만 div로 남긴다

## 주석과 특수문자

```html
<!-- 주석 -->
&lt; &gt; &amp; &nbsp;
```

- `<` `>`를 내용으로 쓰려면 `&lt;` `&gt;`로 이스케이프한다. `&nbsp;`는 줄바꿈 안 되는 공백이다
