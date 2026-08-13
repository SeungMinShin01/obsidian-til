---
출처: Claude 분석
원본: KDT_2026/2026_FE/day14, Note/day/day14
작성일: 2026-08-10
tags: [학습, css]
---

# CSS day14 — position과 가상요소

> 실습 파일: `day14/exam/exam1.css`(position), `exam2.css`(링크·가상요소), `Note/day/day14`, `day14/practice/index.css`, `practice9~10.css`
> 허브: [[CSS MOC]] · 이전: [[CSS day11 커뮤니티와 예약 사이트]] · 다음: [[CSS day15 테이블과 배경]]

## 1. 배운 내용

### 1-1. position 5종 — exam1.css

| 값 | 배치 기준 | 특징 |
| --- | --- | --- |
| `static` (기본) | HTML 작성 순서 | `top/left` **사용 불가** |
| `relative` | 원래 자기 위치 | 원래 자리를 **차지한 채** 이동 |
| `absolute` | 가장 가까운 `static`이 아닌 조상 | 문서 흐름에서 **제거됨** (자리 안 차지) |
| `fixed` | 브라우저 화면(viewport) | 스크롤해도 고정 |
| `sticky` | 스크롤 위치에 따라 relative ↔ fixed | 헤더 고정에 사용 |

```css
.box2 { position: static; left: 50px; }      /* left가 무시됨 */
.box3 { position: relative; top: 50px; left: 50px; z-index: -999; }
.box4 { position: absolute; top: 50px; left: 50px; }
.box5 { position: fixed; bottom: 50px; right: 50px; }
.header { position: sticky; top: 0; }
```

### 1-2. 방향 속성의 이동 개념 — Note/CSSNote 8번

방향 속성은 이렇게 이해하면 헷갈리지 않습니다.
```css
top: 20px;     /* 위쪽에 20px 공간을 만들어 아래로 이동 */
left: 30px;    /* 왼쪽에 30px 공간을 만들어 오른쪽으로 이동 */
right: 20px;   /* 오른쪽에 공간을 만들어 왼쪽으로 이동 */
bottom: 10px;  /* 아래쪽에 공간을 만들어 위로 이동 */
```

"어느 쪽에서 밀어내는가"로 이해하면 헷갈리지 않습니다.

### 1-3. 가장 중요한 패턴 — 부모 relative + 자식 absolute

```css
.parent { position: relative; }   /* 기준점 선언 */
.box6   { position: absolute; top: 30px; left: 30px; }
```

한 줄로 정리하면 이렇습니다.
> position 부모가 static을 제외하면 하위 요소가 absolute로 부모 기준으로 위치를 잡는다.

**부모에 `relative`가 없으면 `<body>` 기준으로 날아가버립니다.** "요소가 엉뚱한 데로 갔다"면 이걸 먼저 확인하세요.

`absolute`는 조상을 타고 올라가며 `position`이 `static`이 **아닌** 첫 요소를 찾습니다.
```
.child(absolute) → .parent(static, 건너뜀) → .grandparent(relative, 여기!)
```

**실전 활용**: 이미지 위 뱃지, 카드 위 좋아요 버튼, 슬라이드 화살표, 툴팁

### 1-4. z-index

```css
.box3 { position: relative; z-index: -999; }
```

겹칠 때 앞뒤 순서를 정합니다. **`position`이 `static`이 아니어야 동작합니다.**

### 1-5. sticky 헤더

```css
.header {
  display: flex;
  background-color: #b0ffe5;
  position: sticky;
  top: 0;
}
```

주의할 점 3가지
- `top`(또는 다른 방향) 값이 **반드시 있어야** 동작합니다
- 부모에 `overflow: hidden`이 있으면 동작하지 않습니다
- 부모의 높이 범위를 벗어나면 sticky가 풀립니다

### 1-6. 링크 상태 선택자 — exam2.css

```css
a { text-decoration: none; color: black; }   /* 기본 밑줄·색상 제거 */
a:hover   { color: #244; }              /* 마우스 올렸을 때 */
a:visited { color: cornflowerblue; }    /* 방문한 적 있는 링크 */
a:active  { color: darksalmon; }        /* 클릭하는 순간 */
```

**순서가 중요합니다**: **L**ink → **V**isited → **H**over → **A**ctive (LoVe HAte)
순서를 바꾸면 뒤의 것이 앞의 것을 덮어써서 동작하지 않습니다.

### 1-7. 가상요소 `::before` / `::after`

```css
.box1::before { content: "[가상요소 '앞' 구역]"; }
.box2::after  { content: "[가상요소 '뒤' 구역]"; }

li { list-style-type: none; }              /* 기본 글머리 제거 */
.box2 > li::before { content: "🐳🐜"; }     /* 커스텀 글머리 */
.box2 > li::after  { content: "🐜🐳"; }
```

HTML을 건드리지 않고 요소 앞뒤에 콘텐츠를 추가합니다. **`content` 속성이 없으면 렌더링되지 않습니다.**

### 1-8. Note/day/day14의 발견 3가지

이 노트가 짧지만 밀도가 높습니다.

**① text-align이 안 먹은 이유**
> text-align — 하위의 텍스트만 정렬, 요소 정렬 X. `<a>` 태그가 있었기에 정렬이 안 됐다.

`text-align: center`는 **인라인 콘텐츠**를 정렬합니다. 부모가 `display: flex`면 `<a>`가 flex 아이템이 되어 인라인 성질을 잃습니다. → `justify-content`를 써야 합니다.

**② flex 축**
> row → align-items (세로) justify-content (가로)
→ [[CSS day08 flexbox]]

**③ position 기준**
> 부모가 static을 제외하면 하위 요소가 absolute로 부모 기준으로 위치를 잡는다.

### 1-9. practice/index — 쇼핑몰 메인의 실전 기법

`day14/practice/index.html/css` 는 지금까지 만든 것 중 가장 복잡한 레이아웃입니다.

**`display: contents`**
```css
#header {
  width: 100%;
  display: contents;
  /* display: contents : 박스를 생성하지 않고, 자식 요소만 존재하는 것처럼 만듦
     sticky 사용하기 위해서 사용됨 */
}
```

`display: contents` 는 **자기 박스를 없애고 자식들을 부모의 직계 자식처럼** 만듭니다.

`position: sticky`는 **부모의 높이 범위 안에서만** 동작합니다. `#header`라는 박스가 있으면 그 안에서만 붙어 있다가 헤더를 벗어나는 순간 풀립니다. `display: contents`로 헤더 박스를 없애면 자식(`#topMenu`, `#mainMenu`)이 `body`의 직계가 되어 페이지 전체 범위에서 sticky가 유지됩니다.

**상단 메뉴 — 구분선을 span으로**
```html
<li><a href="#">LOGIN</a><span>|</span></li>
<li><a href="#">JOIN</a><span>|</span></li>
```
```css
#topMenu {
  display: flex;
  justify-content: flex-end;
  border-bottom: 1px solid #dbdbdb;
}
#topMenu > li > span { padding: 0px 15px; }
```

구분선 `|`을 `<span>`으로 넣고 좌우 padding으로 간격을 만들었습니다. 가상요소로도 같은 효과를 낼 수 있습니다.
```css
#topMenu > li:not(:last-child)::after {
  content: "|";
  padding: 0 15px;
  color: #dbdbdb;
}
```
HTML이 깔끔해지고 마지막 항목의 구분선도 자동으로 빠집니다.

**드롭다운 서브메뉴**
```html
<li>
  <a href="#">MADE</a>
  <ul class="subMenu">
    <li><a href="#">티</a></li>
    <li><a href="#">셔츠</a></li>
    <li><a href="#">바지</a></li>
    <li><a href="#">아우터</a></li>
  </ul>
</li>
```

메뉴 안에 메뉴를 중첩한 구조입니다. CSS만으로 hover 드롭다운을 만들 수 있습니다.
```css
#mainMenu > ul > li { position: relative; }   /* 기준점 */
.subMenu {
  position: absolute;      /* 부모 기준으로 아래에 띄움 */
  top: 100%;
  left: 0;
  display: none;
  background: #fff;
  min-width: 120px;
  box-shadow: 0 4px 8px rgba(0,0,0,.1);
}
#mainMenu > ul > li:hover .subMenu { display: block; }
```

**부모 `relative` + 자식 `absolute`** 패턴이 그대로 쓰입니다(1-3 참고). `top: 100%`는 "부모 높이만큼 아래"라는 뜻입니다.

**전역 폰트 크기 고정**
```css
* {
  padding: 0px;
  margin: 0px;
  box-sizing: border-box;
  font-size: 12px;
}
```

`*`에 `font-size`를 주면 `<h1>`~`<h6>`의 기본 크기 차이가 전부 사라집니다. 쇼핑몰처럼 작은 글씨가 기본인 사이트에서 쓰는 방식인데, 제목 계층이 필요하면 개별로 다시 지정해야 합니다.

```css
body { font-size: 12px; }   /* 상속으로 처리하면 h1~h6 비율은 유지됨 */
```

## 2. 추가로 알면 좋은 활용법

### 2-1. 완벽한 가운데 정렬 3가지

```css
/* ① flex (가장 간단, 권장) */
.parent { display: flex; justify-content: center; align-items: center; height: 100vh; }

/* ② absolute + transform */
.child { position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); }

/* ③ grid */
.parent { display: grid; place-items: center; height: 100vh; }
```

②에서 `transform`이 필요한 이유: `top: 50%`는 **요소의 왼쪽 위 모서리**를 화면 중앙에 둡니다. 요소 크기의 절반만큼 되돌려야 정확히 중앙이 됩니다. `translate`의 `%`는 **요소 자신의 크기 기준**이라 크기를 몰라도 됩니다.

### 2-2. 가상요소 실전 활용

```css
/* 필수 입력 표시 */
.required::after { content: " *"; color: red; }

/* 툴팁 */
.tooltip { position: relative; }
.tooltip::after {
  content: attr(data-tip);              /* HTML 속성값 읽어오기 */
  position: absolute; bottom: 100%; left: 0;
  background: #333; color: #fff; padding: 4px 8px;
  white-space: nowrap;
  opacity: 0; transition: opacity .2s;
  pointer-events: none;
}
.tooltip:hover::after { opacity: 1; }

/* 제목 밑줄 장식 */
.title::after {
  content: "";
  display: block;
  width: 60px; height: 3px;
  background: #e74c3c;
  margin: 12px auto 0;
}
```

`content: attr(data-tip)`은 HTML의 `<span data-tip="설명">`을 CSS가 읽어오는 기법입니다.

**주의**: `<img>`, `<input>` 같은 빈 태그(replaced element)에는 가상요소를 쓸 수 없습니다. 자식을 가질 수 없기 때문입니다.

### 2-3. transition으로 부드럽게

```css
.card {
  transition: transform .3s ease, box-shadow .3s ease;
}
.card:hover {
  transform: translateY(-8px);
  box-shadow: 0 10px 20px rgba(0,0,0,0.2);
}
```

`a:hover` 에 `transition` 한 줄을 더하면 훨씬 자연스러워집니다.

**성능 팁**: 애니메이션은 `transform`과 `opacity`만 쓰세요. `width`, `top`, `margin`을 애니메이션하면 매 프레임 레이아웃 재계산이 일어나 버벅입니다.

### 2-4. 이미지 위 뱃지 (실전 패턴)

```css
.product { position: relative; }
.product .badge {
  position: absolute;
  top: 8px; left: 8px;
  background: #e74c3c;
  color: #fff;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: .8rem;
}
```

`day14/practice/index`(쇼핑몰)의 상품 카드에 "NEW", "SALE" 뱃지를 붙일 때 쓰는 구조입니다.

### 2-5. 맨 위로 버튼

```css
.top-btn {
  position: fixed;
  bottom: 30px; right: 30px;
  width: 50px; height: 50px;
  border-radius: 50%;
  z-index: 999;
}
```

`fixed`의 대표적 활용입니다. `day14/assets/popup_icons/up.png`가 이 용도로 보입니다.

## 3. 더 나아가 알면 좋은 것

### 3-1. `position: fixed`가 안 될 때

부모에 `transform`, `filter`, `perspective`, `will-change`가 있으면 `fixed`가 **그 부모 기준**이 됩니다. 뷰포트 기준이 아니게 됩니다.

애니메이션을 넣은 컨테이너 안에 모달을 두면 화면 고정이 깨지는 원인이 이것입니다. 모달은 `<body>` 바로 아래에 두는 게 안전합니다.

### 3-2. z-index 쌓임 맥락

```css
.parent { position: relative; z-index: 1; }
.child  { position: absolute; z-index: 9999; }

.other  { position: relative; z-index: 2; }
```

`.child`가 `z-index: 9999`여도 **`.other`보다 아래**에 깔립니다. 부모가 `z-index: 1`로 쌓임 맥락(stacking context)을 만들었기 때문에, 자식은 그 안에서만 순서를 다툽니다.

"z-index를 아무리 올려도 안 올라온다"는 증상의 원인입니다. 부모의 `z-index`를 확인하세요.

### 3-3. `:has()` — 부모 선택자

```css
.card:has(img) { padding: 0; }              /* 이미지가 있는 카드만 */
label:has(input:checked) { font-weight: bold; }
```

오랫동안 CSS에 없던 "부모 선택자"입니다. 이제 대부분의 브라우저에서 쓸 수 있습니다.

### 3-4. 상태 선택자 더 보기

```css
input:focus { outline: 2px solid #4a90d9; }
input:disabled { background: #eee; }
input:checked + label { font-weight: bold; }
input:invalid { border-color: red; }
.box:not(.active) { opacity: .5; }
li:first-child, li:last-child, li:nth-child(2n) { }
```

`:focus`의 `outline`을 없애면 **키보드 사용자가 현재 위치를 알 수 없게 됩니다.** 없애려면 대체 스타일을 반드시 주세요.

## 실습 파일

- `2026_FE/Note/day/day14`, `Note/CSSNote` (8. position)
- `2026_FE/day14/exam/exam1.css`, `exam1.html`
- `2026_FE/day14/exam/exam2.css`, `exam2.html`
- `2026_FE/day14/practice/index.css`, `index.html`
- `2026_FE/day14/practice/practice9.css`, `practice9.html`, `practice10.css`, `practice10.html`
- `2026_FE/day14/assets/` (로고, 상품 gif 8개, popup_icons 7개)

## 관련 노트

[[CSS MOC]] · [[CSS day11 커뮤니티와 예약 사이트]] · [[CSS day15 테이블과 배경]] · [[CSS day08 flexbox]] · [[JS day14 게시판 CRUD]]
