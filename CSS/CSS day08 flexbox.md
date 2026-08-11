---
출처: Claude 분석
원본: KDT_2026/2026_FE/day08
작성일: 2026-08-10
tags: [css, day08, flex, 레이아웃]
---

# CSS day08 — flexbox

> 실습 파일: `day08/exam/exam1.css`(flex 10패턴), `day08/practice/practice4~5.css`, `Note/CSSNote` 5번
> 허브: [[CSS MOC]] · 이전: [[CSS day06 선택자와 기본 속성]] · 다음: [[CSS day09 카페 키오스크]]

## 1. 배운 내용

### 1-1. 학습 방식이 좋았던 날

`exam1.css`가 **`.flexbox1` ~ `.flexbox10`까지 속성 하나씩만 바꿔 별도 클래스로 실험**한 구조입니다. 이건 CSS 학습의 정석입니다. 여러 속성을 한꺼번에 주면 어느 게 무슨 역할인지 알 수 없습니다.

### 1-2. flex의 기본

```css
.container { display: flex; }
```

부모에 `display: flex`를 주면 **자식들의 배치 방법**을 제어할 수 있습니다.

### 1-3. flex-wrap

```css
.flexbox1 { display: flex; flex-wrap: nowrap; width: 250px; }  /* 기본값 */
.flexbox2 { display: flex; flex-wrap: wrap; width: 250px; }
```

| 값 | 동작 |
| --- | --- |
| `nowrap` (기본) | 하위 요소가 구역보다 커지면 **자동으로 크기를 줄여** 한 줄에 맞춤 |
| `wrap` | 하위 요소가 커지면 **줄바꿈** |

### 1-4. flex-direction

```css
.flexbox3 { flex-direction: row; }     /* 기본값 — 가로 배치 */
.flexbox4 { flex-direction: column; }  /* 세로 배치 */
```

### 1-5. justify-content — 주축 정렬

```css
.flexbox5 { justify-content: flex-start; }    /* 기본값 — 왼쪽 */
.flexbox6 { justify-content: flex-end; }      /* 오른쪽 */
.flexbox7 { justify-content: center; }        /* 가운데 */
.flexbox8 { justify-content: space-between; } /* 양끝 여백 없이 사이 균등 */
.flexbox9 { justify-content: space-evenly; }  /* 모든 여백 균등 */
                                              /* space-around도 있음 */
```

**space 3형제**
```
space-between:  [1]    [2]    [3]      양끝 여백 0
space-around :  _[1]__[2]__[3]_        요소마다 좌우 절반씩 → 양끝은 절반
space-evenly :  _[1]_[2]_[3]_          모든 여백 완전 균등
```

### 1-6. align-items — 교차축 정렬

| 값 | 동작 |
| --- | --- |
| `stretch` (기본) | 하위 요소의 세로 크기가 고정이 아니면 **부모 높이만큼 늘어남** |
| `center` | 세로 가운데 |
| `flex-start` | 세로 윗변 |
| `flex-end` | 세로 밑변 |

### 1-7. gap

```css
gap: 10px;         /* 행·열 간격 동일 */
gap: 10px 20px;    /* 행 10px, 열 20px */
```

**`gap`은 요소 사이에만** 들어가고 바깥에는 안 들어갑니다. `margin`으로 하던 계산이 사라집니다.

### 1-8. 주축·교차축 — 한 문장 규칙

```
flex-direction: row    → justify-content = 가로, align-items = 세로
flex-direction: column → justify-content = 세로, align-items = 가로
```

`justify-content`는 항상 **주축**, `align-items`는 항상 **교차축**입니다. `direction`이 주축을 결정합니다. **이 한 문장만 기억하면 헷갈리지 않습니다.**

`Note/day/day14`에도 같은 내용을 정리해두셨습니다.
> row → align-items (세로) justify-content (가로)

## 2. 추가로 알면 좋은 활용법

### 2-1. flex 아이템 쪽 속성

부모가 아니라 **자식**에 주는 속성들입니다. day08에서는 안 다뤘지만 실전에서 매우 자주 씁니다.

```css
.item { flex: 1; }              /* 남는 공간을 균등 분배 */
.item { flex: 2; }              /* 다른 것의 2배 */
.item { flex-grow: 1; }         /* 늘어나는 비율 */
.item { flex-shrink: 0; }       /* 줄어들지 않음 (아이콘·로고) */
.item { flex-basis: 200px; }    /* 기본 크기 */
.item { align-self: flex-end; } /* 이 아이템만 다르게 정렬 */
.item { order: -1; }            /* 순서 변경 (HTML은 그대로) */
```

**사이드바 + 본문 레이아웃**
```css
.layout { display: flex; }
.sidebar { width: 250px; flex-shrink: 0; }   /* 고정 */
.main    { flex: 1; }                        /* 나머지 전부 */
```

`flex-shrink: 0`이 없으면 화면이 좁아질 때 사이드바가 찌그러집니다.

### 2-2. 완벽한 가운데 정렬

```css
.parent {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
}
```

flex 이전에는 이게 꽤 어려운 문제였습니다. 지금은 3줄입니다.

### 2-3. `flex-wrap: wrap` + `gap`으로 카드 그리드

```css
.cards { display: flex; flex-wrap: wrap; gap: 20px; }
.card  { width: calc(33.333% - 14px); }   /* gap 20px × 2 ÷ 3 = 13.3 */
```

`calc()`로 gap을 빼야 정확히 3등분됩니다. [[CSS day09 카페 키오스크]] 에서 실제로 쓰입니다.

### 2-4. `margin: auto`를 flex 안에서

```css
.nav { display: flex; }
.logo { margin-right: auto; }   /* 로고는 왼쪽, 나머지는 오른쪽으로 밀림 */
```

`justify-content`로는 안 되는 배치를 이 한 줄로 만들 수 있습니다.

### 2-5. `text-align`이 flex 안에서 안 먹는 이유

`Note/day/day14`의 발견입니다.
> text-align — 하위의 텍스트만 정렬, 요소 정렬 X. `<a>` 태그가 있었기에 정렬이 안 됐다.

`text-align: center`는 **인라인 콘텐츠**를 정렬합니다. `<a>`는 인라인이지만, 부모가 `display: flex`면 `<a>`가 **flex 아이템**이 되어 인라인 성질을 잃습니다.

```css
/* 부모가 flex일 때 */
.nav { display: flex; justify-content: center; }   /* text-align이 아니라 이것 */
```

### 2-6. flex의 기본값을 알아두면 디버깅이 쉽습니다

```css
display: flex;
/* 자동으로 적용되는 기본값 */
flex-direction: row;
flex-wrap: nowrap;
justify-content: flex-start;
align-items: stretch;
```

`align-items: stretch`가 기본이라 **자식들의 높이가 저절로 같아집니다.** 카드 높이를 맞추려고 애쓸 필요가 없습니다.

## 3. 더 나아가 알면 좋은 것

### 3-1. CSS Grid — 2차원 레이아웃

flex는 1차원(가로 **또는** 세로), grid는 2차원(가로 **와** 세로)입니다.

```css
.grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);   /* 3등분 */
  gap: 20px;
}

/* 반응형 카드 — 미디어 쿼리 없이 자동 줄바꿈 */
.grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 20px;
}
```

두 번째 예제는 **화면 폭에 따라 열 개수가 자동으로 바뀝니다.** [[CSS day09 카페 키오스크]] 의 카페 메뉴 12개, [[CSS day10 카메라 강의 사이트]] 의 상품 8개에 최적입니다.

**전체 페이지 레이아웃**
```css
.layout {
  display: grid;
  grid-template-areas:
    "header header"
    "sidebar main"
    "footer footer";
  grid-template-columns: 250px 1fr;
}
.header { grid-area: header; }
```

**선택 기준**: 한 방향 나열 → flex, 행과 열이 모두 있는 격자 → grid

### 3-2. 반응형 전환

```css
.layout { display: flex; gap: 20px; }

@media (max-width: 768px) {
  .layout { flex-direction: column; }   /* 모바일에선 세로로 */
  .sidebar { width: 100%; }
}
```

**`flex-direction` 하나만 바꿔도 모바일 대응이 됩니다.** 이게 flex를 쓰는 큰 이유입니다.

### 3-3. flex 디버깅 팁

크롬 개발자도구 Elements 탭에서 `display: flex`인 요소 옆에 **`flex` 배지**가 뜹니다. 클릭하면 주축·교차축 방향과 정렬 상태를 시각적으로 보여줍니다. flex가 헷갈릴 때 가장 빠른 확인 방법입니다.

## 실습 파일

- `2026_FE/Note/CSSNote` (5. CSS flex 속성)
- `2026_FE/day08/exam/exam1.css`, `exam1.html`, `CSS.txt`
- `2026_FE/day08/practice/practice4.css`, `practice5.css`, `practice0.js`, `practice0.html`
- `2026_FE/day08/practice/pracitce4.html`, `pracitce5.html`

## 관련 노트

[[CSS MOC]] · [[CSS day06 선택자와 기본 속성]] · [[CSS day09 카페 키오스크]] · [[CSS day14 position과 가상요소]]
