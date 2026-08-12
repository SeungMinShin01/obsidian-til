---
출처: Claude 분석
원본: shirhal/front-end
작성일: 2026-08-11
tags: [프로젝트, 학습, 보드게임카페예약사이트, css, html]
---

# 공부할 코드 - CSS와 HTML

styled-components 안에 들어 있어서 눈에 잘 안 띄지만, KDT에서 배운 CSS·HTML이 실전에서 어떻게 쓰였는지 보이는 지점들입니다.
허브: [[보드게임카페예약사이트 프로젝트에서 배울 것]]

## 1. styled-components — CSS가 사라진 게 아니라 자리를 옮긴 것

이 프로젝트에는 `.css` 파일이 거의 없습니다(예외: `BoardGame.css`). 스타일은 전부 JS 파일 하단의 styled 정의에 있습니다.

```javascript
const HeaderImg = styled.img`
  width: 100%;
  height: 260px;
  object-fit: cover;      /* ← CSS 그대로다 */
`;
```

### 원리

템플릿 리터럴 안의 내용물은 **그냥 CSS**입니다. 선택자·속성·미디어쿼리 전부 CSS MOC 에서 배운 그대로이고, 바뀐 것은 스코프 방식뿐입니다.

```
전통 CSS:            클래스 이름으로 스코프 (.header-img { ... }) — 이름 충돌 관리가 내 몫
styled-components:   컴포넌트로 스코프 — 클래스명을 라이브러리가 생성(해시)해서 충돌이 없음
```

`className` 충돌 걱정 없이 `Container`라는 이름을 파일마다 써도 되는 이유가 이것입니다. **CSS 실력이 그대로 필요하다**는 게 핵심 — 라이브러리는 스코프만 해결하지, `object-fit`이 뭔지는 알려주지 않습니다.

### 겹치는 기초

`BoardGame.css` 하나만 전통 방식으로 남아 있어서, 같은 프로젝트 안에서 두 방식을 비교할 수 있습니다. 클래스 명명(BEM 같은 규칙)이 필요한 쪽과 필요 없는 쪽의 차이를 직접 확인해보면 styled-components가 어떤 문제를 풀려고 나왔는지 명확해집니다.

연결: CSS day05 첫 스타일링 선택자 · CSS MOC

## 2. 이미지 오버레이 — position 3종 세트의 실전형

모든 서브페이지 상단에 반복되는 헤더입니다 (`Reservation.js`, `store.js` 등).

```javascript
const HeaderImgSection = styled.div`
  position: relative;        /* 기준점 */
`;
const HeaderTextOverlay = styled.div`
  position: absolute;        /* 기준점 위에 겹침 */
  top: 50%; left: 50%;
  transform: translate(-50%, -50%);   /* 자기 크기의 절반만큼 되당김 → 정중앙 */
  color: white;
`;
```

### 원리

CSS day14 position과 가상요소 에서 배운 것이 그대로 조합됐습니다.

1. 부모 `relative` — 자식 absolute의 기준 좌표계가 됨
2. 자식 `absolute` + `top/left 50%` — 부모의 정중앙에 **왼쪽 위 모서리**가 옴
3. `translate(-50%, -50%)` — 자기 크기의 절반만큼 되돌려서 **중심점**이 정중앙에 옴

3단계에서 `%`의 기준이 바뀐다는 게 포인트입니다: `top: 50%`의 %는 **부모** 크기 기준, `translate(-50%)`의 %는 **자기 자신** 크기 기준. 이 차이 덕에 오버레이의 크기를 몰라도 중앙 정렬이 됩니다.

### 활용

이미지 위 텍스트, 카드 위 배지, 모달 중앙 정렬 — 전부 같은 3종 세트입니다. 요즘은 부모에 `display: grid; place-items: center`로 더 짧게 되지만, absolute 방식은 "이미지 위에 겹친다"는 의도가 명확해서 여전히 표준입니다.

## 3. transient prop — 스타일 분기와 DOM 오염

`App.js` 레이아웃에서 쓴 패턴입니다.

```javascript
const Main = styled.main`
  max-width: ${(p) => (p.$fullWidth ? "100%" : "1200px")};
`;
<Main $fullWidth={isAdminPage}>
```

### 원리

props로 스타일을 분기하는 것이 styled-components의 동적 스타일링 방식입니다. `$` 접두사(transient prop)가 붙으면 styled-components가 그 prop을 **DOM 속성으로 내려보내지 않습니다.** `$` 없이 `fullWidth`라고 쓰면 `<main fullwidth="true">`처럼 HTML에 존재하지 않는 속성이 실제 DOM에 찍히고 콘솔 경고가 납니다.

"컴포넌트 세계의 데이터"와 "HTML 세계의 속성"이 다른 층위라는 것 — HTML day02 문서 구조와 미디어 에서 배운 표준 속성 개념이 있어야 왜 경고가 나는지 이해되는 지점입니다.

### 활용

활성 탭 강조, 관리자/일반 레이아웃 분기, 에러 상태 테두리 — "상태에 따라 스타일이 바뀌는" 모든 곳의 기본 도구입니다. 분기가 3개를 넘으면 prop 여러 개 대신 `variant="admin"` 하나로 받는 것이 관례입니다.

## 4. GlobalStyle — 리셋과 웹폰트의 자리

```javascript
const GlobalStyle = createGlobalStyle`
  @font-face { font-family: "Pretendard"; src: url(...); }
  * { margin: 0; padding: 0; box-sizing: border-box; }
  body { font-family: "Pretendard", sans-serif; }
`;
```

### 원리

브라우저 기본 스타일(마진·패딩·폰트)은 브라우저마다 달라서, 전부 0으로 밀고 시작하는 것이 **리셋**입니다. `box-sizing: border-box`는 width에 패딩·테두리를 포함시키는 계산법 — CSS day05 첫 스타일링 에서 배운 박스 모델의 실무 표준 설정입니다.

전역(리셋·폰트)과 지역(컴포넌트 스타일)의 경계를 이 파일 하나로 지킨 구조가 배울 점입니다. 반대로 색·간격 값이 컴포넌트마다 리터럴로 흩어진 것( [[App과 공통 레이아웃 분석]] )은 전역으로 올렸어야 할 것이 지역에 남은 사례 — **"어느 층위의 관심사인가"** 를 판단하는 연습 소재로 좋습니다.

### 겹치는 기초

CSS day06 선택자와 기본 속성 에서 배운 기본 속성들 위에 `@font-face` 웹폰트 적용이 얹힌 형태입니다. 차이는 위치뿐 — CSS 파일이 아니라 JS 안의 템플릿 리터럴.

## 5. 폼 마크업 — placeholder는 label이 아니다

예약 폼( [[components 분석 - Reservation과 결제]] )의 입력들입니다.

```javascript
<Input type="text" name="user_id" placeholder="예약자 아이디" ... />
<Select name="num_of_players" ... >
```

### 원리

HTML day04 폼과 테이블 에서 배운 폼 요소들이 styled로 감싸져 쓰였습니다. `name` 속성이 상태 키와 일치해서 `[e.target.name]` 계산된 속성명 핸들러( [[공부할 코드 - React 패턴]] )가 동작합니다 — **HTML 속성 설계가 JS 코드 구조를 결정**하는 사례입니다.

아쉬운 점이 학습 포인트입니다: `<label>`이 없고 placeholder가 그 역할을 대신합니다. placeholder는 ① 입력을 시작하면 사라져서 "뭘 쓰는 중이었지"를 잃게 하고, ② 스크린리더가 label만큼 안정적으로 읽지 않으며, ③ 클릭 영역 확장(label 클릭 → input 포커스)도 없습니다.

```html
<label htmlFor="user_id">예약자 아이디</label>
<input id="user_id" name="user_id" ... />
```

### 활용

폼 접근성의 최소선: 모든 입력에 label 연결, 버튼은 `<button>`(div+onClick 아님), 제출은 `<form onSubmit>`(버튼 onClick 아님 — 엔터 제출이 공짜로 따라옴). 이 프로젝트는 `<FormRow as="form" onSubmit={...}>`으로 form 제출을 쓴 것은 맞게 했습니다. `as` prop으로 styled 컴포넌트의 태그를 바꾸는 것도 시맨틱을 지키는 도구입니다.

## 6. 반복 레이아웃 — 카드 그리드와 flexbox

보드게임 목록·음료 메뉴·매장 카드가 전부 같은 패턴입니다: 데이터 배열 → `map` → 카드 → flex/grid 배치.

```javascript
const Grid = styled.div`
  display: flex;
  flex-wrap: wrap;
  gap: 24px;
`;
```

CSS day08 flexbox 로 배운 배치가 "JSX 반복 렌더링과 만나는" 지점입니다. 카드 폭을 고정하고 `flex-wrap`으로 줄바꿈하는 방식인데, 개수·간격 계산은 `display: grid; grid-template-columns: repeat(auto-fill, minmax(220px, 1fr))`가 더 정확하게 처리합니다 — flexbox(1차원)와 grid(2차원)의 선택 기준을 이 화면들로 연습할 수 있습니다.

연결: CSS day09 카페 키오스크 의 메뉴 그리드와 같은 문제 · CSS day11 커뮤니티와 예약 사이트 의 카드 배치

## 관련 노트

[[보드게임카페예약사이트 프로젝트에서 배울 것]] · [[공부할 코드 - React 패턴]] · [[전문용어 정리]]
