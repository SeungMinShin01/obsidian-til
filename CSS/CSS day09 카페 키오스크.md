---
출처: Claude 분석
원본: KDT_2026/2026_FE/day09/activity
작성일: 2026-08-10
tags: [css, day09, 레이아웃, 키오스크, 웹폰트, fixed]
---

# CSS day09 — 카페 키오스크

> 실습 파일: `day09/activity/activity.html/css`(주문 화면), `activity1.html/css`(주문 내역), `assets/` 메뉴 이미지 12장
> 허브: [[CSS MOC]] · 이전: [[CSS day08 flexbox]] · 다음: [[CSS day10 카메라 강의 사이트]]

## 1. 배운 내용

[[CSS day08 flexbox]] 에서 배운 flex를 **키오스크 UI 두 화면**에 적용한 날입니다.

| 파일 | 화면 |
| --- | --- |
| `activity.html/css` | 주문 화면 — 카테고리 탭 + 메뉴 카드 그리드 |
| `activity1.html/css` | 주문 내역 — 선택 상품 + 수량 조절 + 결제 |

### 1-1. 웹폰트 불러오기

```css
@font-face {
  font-family: "Juache";
  src: url("https://cdn.jsdelivr.net/gh/projectnoonnu/noonfonts_one@1.0/BMJUA.woff")
    format("woff");
  font-weight: normal;
  font-display: swap;
}
* {
  font-family: "Juache";
}
```

`Note/CSSNote`에 적어두신 눈누(noonnu) 폰트를 실제로 적용했습니다.

- `@font-face` — 폰트 파일을 직접 등록. `font-family` 이름은 내가 정합니다
- `font-display: swap` — 폰트 로딩 전에는 기본 폰트로 먼저 보여주고, 다 받으면 교체합니다. 글자가 안 보이는 시간(FOIT)을 없애줍니다

### 1-2. 고정 헤더·푸터 — position: fixed

```css
header {
  width: 100%;
  height: 180px;
  max-width: 1080px;
  position: fixed;
  top: 0;
  z-index: 100;
  background-color: #e6ceb0;
  box-shadow: 0 6px 10px rgba(0, 0, 0, 0.12);
}

footer {
  position: fixed;
  bottom: 0;
  z-index: 100;
  box-shadow: 0 -6px 10px rgba(0, 0, 0, 0.12);
  display: flex;
  justify-content: center;
}
```

키오스크는 **헤더와 푸터가 항상 화면에 붙어 있어야** 하므로 `fixed`가 딱 맞습니다. → [[CSS day14 position과 가상요소]]

**포인트 3가지**
1. `z-index: 100` — 스크롤되는 본문 위에 올라오도록
2. `box-shadow`의 y값 부호 — 헤더는 `0 6px`(아래로), 푸터는 `0 -6px`(위로). 그림자가 본문 쪽을 향합니다
3. `background-color` 필수 — 배경이 없으면 아래 내용이 비쳐 보입니다

### 1-3. fixed가 만드는 공간 문제와 해결

`fixed`는 **문서 흐름에서 빠지므로 자리를 차지하지 않습니다.** 그래서 본문이 헤더 아래로 숨습니다.

```css
section {
  padding-top: 200px;    /* 헤더 높이(180px)만큼 밀어냄 */
  margin-top: 10px;
  min-height: 100vh;
}
```
```css
/* activity1은 margin으로 해결 */
section { margin-top: 180px; }
```

두 화면에서 `padding-top`과 `margin-top`을 각각 써보셨습니다. **본문에 배경색이 있으면 `padding`이 유리합니다.** `margin`은 그만큼 배경이 비어 보이기 때문입니다.

### 1-4. 스크롤바 숨기기

```css
body::-webkit-scrollbar {
  display: none;
}
```

키오스크·모바일 UI에서 자주 쓰는 기법입니다. **스크롤은 되지만 막대만 안 보입니다.**

### 1-5. 카드 레이아웃

```css
.컨테이너 { width: 1000px; }

.카드 {
  display: flex;
  justify-content: space-between;   /* 한 줄에 3개씩 균등 배치 */
  padding: 10px;
}

.박스 {
  width: 280px;
  height: 420px;
  border-radius: 12px;
  box-shadow: 4px 4px 12px #0000003f;
}
```

`.카드`(행) 안에 `.박스`(메뉴) 3개를 넣고, 행을 여러 개 쌓는 구조입니다. **`flex-wrap` 대신 행을 직접 나눈 방식**입니다.

`#0000003f` — 8자리 헥스로 검정 25% 투명도를 표현했습니다. → [[CSS day15 테이블과 배경]]

### 1-6. 주문 내역 화면 — 가로 정렬

```html
<div class="섹션">
  <img src="./assets/Cafe_Latte.png" />
  <div class="정보">
    <div>카페 라떼</div>
    <div>5,000원</div>
  </div>
  <div class="수량선택">
    <button class="마이너스버튼">-</button>
    <div class="개수">1</div>
    <button class="플러스버튼">+</button>
  </div>
</div>
```

```css
.섹션 {
  height: 170px;
  display: flex;
  align-items: center;      /* 세로 가운데 — 높이가 다른 요소를 나란히 */
  margin: 15px 30px;
  border-radius: 12px;
  padding: 0 20px;
  box-shadow: 4px 4px 4px gray;
}

.정보 {
  display: flex;
  flex-direction: column;   /* 이름과 가격을 세로로 */
  align-items: center;
}
```

**바깥은 `row`, 안쪽은 `column`** — flex를 중첩해서 쓰는 전형적인 패턴입니다. 이미지·정보·수량이 가로로 놓이고, 정보 안에서만 세로로 쌓입니다.

### 1-7. 자식 선택자로 세밀하게

```css
header > div {
  font-weight: bold;
  line-height: 150px;    /* 헤더 높이 180px에 가깝게 → 세로 가운데처럼 보임 */
  padding-left: 20px;
  font-size: 48px;
}
.정보 > div { margin-bottom: 10px; }
```

`line-height`로 세로 정렬을 흉내내는 건 오래된 기법입니다. 한 줄 텍스트에만 통합니다.

### 1-8. 개발 중 테두리 확인

```css
* {
  /* border: solid 0.1px red; */
}
header {
  /* border: 3px solid blue; */
}
```

**모든 구역에 테두리를 잠깐 켜서 레이아웃을 확인하고 주석 처리**하는 습관이 코드 전반에 보입니다. CSS 학습 단계에서 매우 효과적인 방법입니다.

## 2. 추가로 알면 좋은 활용법

### 2-1. 카드 내부도 flex로 — 가격 위치 고정

```css
.박스 {
  display: flex;
  flex-direction: column;
}
.박스 .가격 {
  margin-top: auto;   /* 가격을 카드 맨 아래로 밀어냄 */
}
```

메뉴 이름이 한 줄인 카드와 두 줄인 카드가 섞여도 **가격 위치가 일정**해집니다. `margin-top: auto`가 남는 공간을 전부 위쪽에 몰아주는 트릭입니다.

`콜드브루 돌체라떼`처럼 이름이 긴 메뉴가 있어서 실제로 필요한 처리입니다.

### 2-2. 이미지 비율 고정

```css
.이미지 {
  width: 100%;
  height: 240px;
  object-fit: cover;   /* 원본 비율이 달라도 안 찌그러짐 */
}
```

메뉴 이미지 12장의 원본 크기가 제각각일 때 필수입니다. → [[CSS day15 테이블과 배경]]

### 2-3. 카테고리 탭 활성 상태

```html
<button class="category active">커피/라떼</button>
<button class="category">에이드</button>
```

```css
.category {
  border: none;
  background: none;
  font: inherit;        /* button은 폰트를 상속받지 않음 */
  padding: 10px 20px;
  cursor: pointer;
  border-radius: 20px;
}
.category.active {
  background-color: #8b5e34;
  color: #fff;
}
```

`active` 클래스를 이미 붙여두셨으니 JS로 토글만 하면 동작합니다.

```javascript
document.querySelectorAll(".category").forEach(btn => {
  btn.addEventListener("click", () => {
    document.querySelectorAll(".category").forEach(b => b.classList.remove("active"));
    btn.classList.add("active");
  });
});
```
→ [[JS day12 제품 사원 관리 CRUD]]

### 2-4. `fixed` 대신 `sticky`

```css
header { position: sticky; top: 0; }
```

`sticky`는 **원래 자리를 차지하다가 스크롤이 닿으면 고정**됩니다. `padding-top`으로 공간을 보정할 필요가 없습니다.

| | fixed | sticky |
| --- | --- | --- |
| 자리 차지 | X (본문이 밀려 올라옴) | O |
| 보정 필요 | `padding-top` 필요 | 불필요 |
| 부모 범위 | 뷰포트 전체 | 부모 높이 안에서만 |

키오스크처럼 **항상 붙어 있어야** 하면 `fixed`, 일반 웹페이지 헤더면 `sticky`가 편합니다.

### 2-5. `max-width`와 `width: 100%` 조합

```css
header { width: 100%; max-width: 1080px; }
```

화면이 좁으면 화면 폭을, 넓으면 1080px을 유지합니다. **반응형의 기본 패턴**입니다.

다만 `fixed`는 부모가 아니라 뷰포트 기준이므로, 가운데 정렬을 하려면 추가 처리가 필요합니다.
```css
header {
  left: 50%;
  transform: translateX(-50%);
}
```

### 2-6. 스크롤바 숨기기 크로스브라우저

```css
body {
  scrollbar-width: none;      /* Firefox */
  -ms-overflow-style: none;   /* IE·구 Edge */
}
body::-webkit-scrollbar {
  display: none;              /* Chrome·Safari */
}
```

`::-webkit-scrollbar`만으로는 파이어폭스에서 막대가 그대로 보입니다.

## 3. 더 나아가 알면 좋은 것

### 3-1. grid로 카드 배치

지금은 `.카드`(행) 3개를 직접 만들어 3×N 격자를 구성했습니다. grid를 쓰면 행 구분 없이 자동 배치됩니다.

```html
<div class="컨테이너">
  <div class="박스">...</div>   <!-- 카드 12개를 그냥 나열 -->
</div>
```
```css
.컨테이너 {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
}
```

**메뉴가 늘거나 줄어도 HTML 구조를 바꿀 필요가 없습니다.** 행을 직접 나누면 메뉴 하나를 추가할 때마다 `<div class="카드">`를 다시 짜야 합니다.

반응형까지 넣으면
```css
.컨테이너 {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
  gap: 20px;
}
```

### 3-2. 메뉴를 배열로 관리

카드 12개를 HTML에 손으로 쓰면 수정이 힘듭니다.

```javascript
const menus = [
  { name: "아메리카노",  price: 4500, img: "Americano.png" },
  { name: "카페 라떼",   price: 5000, img: "Cafe_Latte.png" },
  { name: "바닐라 라떼", price: 5500, img: "Vanilla_Latte.png" },
];

document.querySelector(".컨테이너").innerHTML = menus.map(m => `
  <div class="박스">
    <img class="이미지" src="./assets/${m.img}" alt="${m.name}" />
    <div class="타이틀">${m.name}</div>
    <div class="가격">${m.price.toLocaleString()}원</div>
  </div>
`).join("");
```

`toLocaleString()`이 `4500` → `4,500`으로 바꿔줍니다. HTML에 `4,500원`을 직접 쓴 부분을 자동화할 수 있습니다.

→ [[JS day11 DOM 조작]] · [[JS day12 제품 사원 관리 CRUD]]

### 3-3. 주문 상태를 데이터로

두 화면(`activity`, `activity1`)이 지금은 정적입니다. 실제 키오스크가 되려면 장바구니 상태가 필요합니다.

```javascript
let cart = [];   // [{ name, price, qty }]

function 담기(menu) {
  const found = cart.find(c => c.name === menu.name);
  if (found) found.qty++;
  else cart.push({ ...menu, qty: 1 });
  render();
}

function 총액() {
  return cart.reduce((sum, c) => sum + c.price * c.qty, 0);
}
```

`총 금액`, `주문 수량`을 `<a>5,000</a>`으로 하드코딩한 부분이 `총액()` 결과로 바뀝니다.

수량 `+`/`-` 버튼도 여기에 연결됩니다.
→ [[JS day13 웹 스토리지와 인터벌]] 로 새로고침해도 장바구니가 유지되게 만들 수 있습니다.

### 3-4. 클래스 이름을 영문으로

`.페이지`, `.카드`, `.박스`, `.수량선택` — 한글 클래스명은 CSS·JS 모두 동작합니다. 학습 중에는 의미가 바로 보여 편합니다.

실무에서 영문을 쓰는 이유는 협업 시 IME 전환 비용과 일부 빌드 도구·CSS 압축기 호환성 때문입니다. 지금 단계에서는 **한글로 구조를 확실히 이해하는 게 우선**이고, 나중에 BEM 같은 규칙으로 옮기면 됩니다.

```css
.page { }
.menu-card { }
.menu-card__title { }
.qty-selector { }
```

## 실습 파일

- `2026_FE/day09/activity/activity.html`, `activity.css` (주문 화면)
- `2026_FE/day09/activity/activity1.html`, `activity1.css` (주문 내역)
- `2026_FE/day09/activity/assets/` (메뉴 이미지 12장)

## 관련 노트

[[CSS MOC]] · [[CSS day08 flexbox]] · [[CSS day10 카메라 강의 사이트]] · [[CSS day14 position과 가상요소]] · [[JS day12 제품 사원 관리 CRUD]]
