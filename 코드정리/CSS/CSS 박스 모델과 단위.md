---
출처: Claude 분석
작성일: 2026-08-21
tags: [코드정리]
---

# CSS 박스 모델과 단위

> 상위: [[CSS]]

## 박스 모델 — 모든 요소는 상자다

```css
.card {
    width: 300px;
    padding: 16px;
    border: 1px solid #ddd;
    margin: 20px;
}
```

- 안쪽부터 내용(content) → padding(안 여백) → border(테두리) → margin(밖 여백) 4겹이다
- padding은 배경색이 칠해지는 영역이고 margin은 이웃과의 거리다 — "안이냐 밖이냐"로 구분한다
- 축약형: `margin: 10px`(전부) / `10px 20px`(상하·좌우) / `10px 20px 30px 40px`(상→우→하→좌 시계방향)
- `margin: 0 auto`는 블록 요소 가로 중앙 정렬의 고전 관용구다(width가 있어야 동작)

## box-sizing

```css
* {
    box-sizing: border-box;
}
```

- 기본값(content-box)은 width가 내용만의 폭이라, padding·border를 더하면 상자가 300px보다 커진다
- `border-box`는 **padding·border를 width 안에 포함**시킨다. "300px이라고 했으면 300px"이 되어 계산이 직관적이다
- 그래서 거의 모든 프로젝트가 첫 줄에 전체 적용(`*`)으로 깔고 시작한다

## display — 상자의 성격

```css
span { display: inline; }
div { display: block; }
a.button { display: inline-block; }
.hidden { display: none; }
```

- block은 한 줄을 통째로 차지(div·p·h1), inline은 글자처럼 흐르며 width·height가 안 먹는다(span·a)
- inline-block은 흐르면서 크기 지정이 되는 절충형 — a 태그를 버튼처럼 만들 때 쓴다
- `display: none`은 자리조차 없이 사라진다(`visibility: hidden`은 자리는 남긴다)

## 단위

```css
.box { width: 50%; }
h1 { font-size: 2rem; }
.hero { height: 100vh; }
p { line-height: 1.6; }
```

- `px` 고정, `%` 부모 기준 비율, `rem` 루트(html) 글자크기 기준 배수, `em` 부모 글자크기 기준 배수
- `vw`/`vh`는 화면 폭·높이의 1%다. `100vh`가 화면 꽉 찬 첫 화면(hero)의 관용구다
- 글자 크기는 rem이 표준이다 — 사용자가 브라우저 글자 크기를 키우면 같이 커진다(px는 무시함)
- line-height는 단위 없는 배수(1.5~1.7)로 주는 게 관례다

## overflow ※

```css
.list { max-height: 300px; overflow-y: auto; }
.text { overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
```

- 내용이 상자보다 클 때: `auto` 스크롤 생성, `hidden` 잘라냄
- 두 번째 줄 세 속성 세트가 "한 줄 말줄임(...)"의 고정 관용구다
