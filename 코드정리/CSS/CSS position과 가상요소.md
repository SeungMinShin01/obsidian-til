---
출처: Claude 분석
작성일: 2026-08-21
tags: [코드정리]
---

# CSS position과 가상요소

> 상위: [[CSS]]
> 세부: [[CSS transform과 애니메이션]]

## position 5종

```css
.badge-parent { position: relative; }
.badge {
    position: absolute;
    top: -8px;
    right: -8px;
}

.header { position: fixed; top: 0; left: 0; width: 100%; }
.section-title { position: sticky; top: 0; }
```

- static(기본) → relative(원래 자리 기준 이동, 자리 유지) → absolute(문서 흐름에서 빠져 **조상 기준** 배치) → fixed(화면 기준 고정) → sticky(스크롤하다 걸리면 고정)
- **absolute의 기준은 "position이 static이 아닌 가장 가까운 조상"**이다. 그래서 부모에 `position: relative`를 깔고 자식에 absolute를 주는 게 항상 세트다 — 카드 위 배지, 이미지 위 텍스트가 전부 이 조합
- fixed는 상단 고정 헤더, sticky는 스크롤 중 붙는 섹션 제목에 쓴다
- 이동값은 top/right/bottom/left로 준다. absolute·fixed는 width를 따로 안 주면 내용만큼 줄어든다

## z-index

```css
.modal-overlay { position: fixed; z-index: 100; }
.modal { z-index: 101; }
```

- 겹친 요소의 위아래 순서다. **position이 있는 요소에만** 먹는다
- 10, 100, 1000처럼 층별로 간격을 두고 관리하면 나중에 끼워 넣기 좋다

## 가상요소 — ::before · ::after

```css
.title::after {
    content: "";
    display: block;
    width: 40px;
    height: 3px;
    background: royalblue;
    margin-top: 8px;
}

.required::before {
    content: "* ";
    color: red;
}
```

- HTML을 건드리지 않고 요소의 앞뒤에 **가짜 자식**을 만든다. `content` 속성이 없으면 아예 안 나타난다(빈 장식도 `content: ""` 필수)
- 제목 밑줄 장식, 필수 표시 별표, 인용부호 같은 "꾸밈용 요소"를 마크업 없이 처리한다 — HTML은 의미만, 장식은 CSS가 맡는 분업이다
- 가상 클래스(:hover, 콜론 1개)는 요소의 **상태**, 가상 요소(::before, 콜론 2개)는 **새로 만든 부분**이라는 구분이다

## 오버레이 관용구

```css
.card { position: relative; }
.card .overlay {
    position: absolute;
    inset: 0;
    background: rgba(0, 0, 0, 0.5);
    display: flex;
    justify-content: center;
    align-items: center;
}
```

- `inset: 0`은 top·right·bottom·left 전부 0 — 부모를 꽉 덮는다는 뜻이다
- 반투명 배경 + flex 중앙 정렬로 "이미지 위에 글자 띄우기"가 완성된다. 커뮤니티·강의 사이트의 카드가 이 구조다
