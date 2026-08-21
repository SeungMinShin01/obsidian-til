---
출처: Claude 분석
작성일: 2026-08-21
tags: [코드정리]
---

# CSS 텍스트와 배경

> 상위: [[CSS]]
> 세부: [[CSS 웹폰트와 아이콘]]

## 글꼴과 텍스트

```css
body {
    font-family: "Pretendard", "Malgun Gothic", sans-serif;
    font-size: 16px;
    line-height: 1.6;
    color: #333;
}

h1 { font-weight: 700; }
.subtitle { font-style: italic; }
.link { text-decoration: none; }
.title { text-align: center; }
.tag { letter-spacing: 1px; }
```

- font-family는 **후보 목록**이다. 앞 글꼴이 없으면 다음으로 넘어가고, 마지막에 계열 이름(sans-serif 등)을 안전망으로 둔다
- font-weight는 400이 보통, 700이 굵게다. text-decoration: none은 링크 밑줄 제거(a 태그 기본값 끄기)
- text-align은 **블록 요소 안의 인라인 내용**을 정렬한다 — 블록 상자 자체의 중앙 정렬(margin auto)과 다른 것이다

## 색

```css
.a { color: #1a73e8; }
.b { color: rgb(26, 115, 232); }
.c { background: rgba(0, 0, 0, 0.5); }
```

- 16진수(#rrggbb)가 기본, rgba의 넷째 값이 투명도(0~1)다 — 반투명 오버레이가 `rgba(0,0,0,.5)`
- 요즘은 투명도를 `#0008`(짧은 표기)나 `hsl()`로 쓰기도 한다

## 배경

```css
.hero {
    background-color: #f0f4f8;
    background-image: url("hero.jpg");
    background-size: cover;
    background-position: center;
    background-repeat: no-repeat;
}

.hero2 {
    background: url("hero.jpg") center / cover no-repeat;
}
```

- `cover`는 상자를 **빈틈없이 채우게** 확대(일부 잘림), `contain`은 이미지 전체가 보이게 축소(여백 생김)
- center + cover + no-repeat 세 개가 배너·카드 배경의 표준 조합이고, 축약형 한 줄(.hero2)로도 쓴다
- 콘텐츠 이미지는 img 태그, 장식 배경은 background — 의미가 있으면 태그, 꾸밈이면 CSS로 구분한다

## img 다루기 ※

```css
img { max-width: 100%; display: block; }
.thumb { width: 120px; height: 120px; object-fit: cover; }
```

- `max-width: 100%`는 이미지가 부모보다 커지지 않게 하는 반응형 기본기다
- `object-fit: cover`는 img 태그 버전의 background-size: cover다 — 썸네일을 찌그러뜨리지 않고 채운다
