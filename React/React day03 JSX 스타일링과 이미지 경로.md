---
출처: Claude 분석
원본: KDT_2026/2026_React/src/example/day03
작성일: 2026-09-15
tags: [학습, react]
---

# React day03 — JSX 스타일링과 이미지 경로

> 실습 파일: `src/example/day03/exam1.jsx` · `src/index.css` · `src/main.jsx`
> 허브: [[React MOC]] · 이전: [[React day02 모달과 컴포넌트 간 상태 전달]] · 다음: [[React day03 폼 제출과 입력값 읽기]]

day02까지는 상태와 서버 통신으로 **동작**을 만드는 자리였고, 이번에는 잠깐 숨을 고르며 **생김새**를 다룬다. React에서 스타일을 입히는 세 가지 길(인라인 `style` 객체, `className`으로 외부 CSS, `id` 선택자)과, 이미지를 불러오는 세 가지 경로(`public/` 절대 경로, `import`한 파일, 외부 URL)를 한 파일 안에서 나란히 비교한다. 예제는 작지만 Vite가 파일을 어떻게 다루는지가 그대로 드러나서, 나중에 프로젝트를 배포할 때 다시 돌아와 보게 될 내용이다.

## 1. 배운 내용

### 1-1. 인라인 스타일은 문자열이 아니라 객체다

```jsx
const myStyle = {
  color: "white",
  backgroundColor: "DodgerBlue",
  padding: "10px",
  fontFamily: "굴림",
};
const iWidth = { maxWidth: "300px" };

<li style={{ color: "red" }}>프론트엔드</li>
<li style={myStyle}>JSP</li>
<img src={log} style={iWidth} />
```

HTML에서는 `style="color: red"`처럼 문자열을 쓰지만, JSX의 `style`은 **자바스크립트 객체**를 받는다. 그래서 중괄호가 두 겹이 된다 — 바깥 `{}`는 "여기부터 JS 표현식", 안쪽 `{}`는 객체 리터럴이다.

| HTML/CSS | JSX `style` 객체 | 이유 |
| --- | --- | --- |
| `background-color: DodgerBlue` | `backgroundColor: "DodgerBlue"` | 하이픈은 JS 식별자에 쓸 수 없어 카멜케이스로 |
| `max-width: 300px` | `maxWidth: "300px"` | 단위까지 문자열로 적는다 |
| `font-family: 굴림` | `fontFamily: "굴림"` | 값은 항상 문자열(숫자만 있으면 `px`가 자동으로 붙는다) |

객체를 컴포넌트 **바깥**에 상수로 빼 두면(`myStyle`, `iWidth`) 렌더링마다 새로 만들어지지 않고, 여러 요소에 같은 스타일을 재사용하기도 편하다. 한 번만 쓰는 스타일은 `style={{ color: "red" }}`처럼 그 자리에 바로 적어도 된다.

### 1-2. 외부 CSS는 `import`로 끌어오고 `className`으로 붙인다

```jsx
import "../../index.css";

<li className="backEnd"> 백엔드 </li>
<li id="backEndSub">Java</li>
```

```css
/* src/index.css */
#backEndSub { font-size: 1.5em; font-weight: bold; }
.warnings  { color: white; background-color: red; font-size: 1.2em; }
```

핵심은 두 가지다.

- CSS 파일을 `<link>`가 아니라 **JS에서 `import`** 한다. Vite가 이 구문을 보고 CSS를 번들에 포함시켜 `<head>`에 `<style>`로 꽂아 준다. 경로는 컴포넌트 파일 기준 상대 경로(`../../index.css`)다.
- 클래스는 `class`가 아니라 **`className`** 이다. `class`는 JS의 예약어라서 JSX가 이름을 바꿔 두었다. `id`는 그대로 `id`를 쓴다.

한 번 `import`된 CSS는 **전역**으로 적용된다. 컴포넌트 안에서 불러왔더라도 그 파일의 `.warnings` 규칙은 앱 전체의 `.warnings`에 먹는다는 점을 기억해 두는 편이 안전하다.

### 1-3. 이미지를 불러오는 세 가지 경로

```jsx
import log from "../../assets/logo9.jpg";

<img src="/img/logo9.jpg" style={iWidth} />          // ① public 폴더
<img src={log} style={iWidth} />                      // ② src/assets를 import
<img src="http://nakja.co.kr/images/reactks.png" />   // ③ 외부 URL
```

| 방식 | 파일 위치 | 쓰는 법 | Vite가 하는 일 |
| --- | --- | --- | --- |
| ① 절대 경로 | `public/img/logo9.jpg` | `src="/img/logo9.jpg"` | 손대지 않고 그대로 복사. `/`가 곧 `public/` |
| ② `import` | `src/assets/logo9.jpg` | `import log from "…"` 후 `src={log}` | 번들에 포함, 파일명에 해시를 붙여 캐시 관리 |
| ③ 외부 URL | 다른 서버 | `src="http://…"` | 관여하지 않음(브라우저가 직접 요청) |

②에서 `log` 변수에 들어가는 값은 이미지 자체가 아니라 **빌드 후의 경로 문자열**이다. 그래서 `src={log}`처럼 중괄호로 넣는다. `import`한 이미지는 파일이 없으면 빌드 단계에서 바로 오류가 나므로 오타를 일찍 잡을 수 있고, `public/`은 런타임에 404가 나야 알 수 있다.

### 1-4. main.jsx에서 갈아끼우는 진입점

```jsx
import Component1 from "./example/day03/exam1.jsx";
create.render(<Component1></Component1>);
```

day01부터 이어 온 방식 그대로다. `main.jsx`는 `createRoot(root)`를 한 번 만들어 두고, 그날 볼 컴포넌트를 `import`해서 `render`한다. 이전 날 코드는 주석으로 남겨 두었다가 필요하면 되살린다. 이렇게 하면 예제마다 프로젝트를 새로 만들지 않고 파일 하나만 바꿔 가며 실습할 수 있다.

## 2. 추가로 알면 좋은 활용법

### 2-1. 조건에 따라 클래스 붙이기

```jsx
<li className={isActive ? "menu active" : "menu"}>홈</li>
<li className={`menu ${isActive ? "active" : ""}`}>홈</li>
```

`className`도 결국 문자열이라 삼항이나 템플릿 리터럴로 조립하면 된다. 조건이 여러 개면 `clsx`·`classnames` 같은 작은 라이브러리가 `clsx("menu", { active: isActive })` 형태로 정리해 준다.

### 2-2. 스타일 객체 합치기

```jsx
const base = { padding: "10px" };
<li style={{ ...base, color: "red" }}>강조</li>
```

day02에서 폼 객체를 `{ ...form, name }`으로 갱신했던 것과 같은 스프레드다. 공통 스타일에 개별 값을 덧씌울 때 쓴다.

### 2-3. 인라인과 CSS 파일의 역할 나누기

인라인 `style`은 **값이 상태에 따라 바뀌는 것**(진행률 바의 `width`, 색상 피커 결과)에 어울리고, 레이아웃·글꼴·색 팔레트처럼 고정된 것은 CSS 파일이 낫다. 인라인은 `:hover`·미디어 쿼리·가상 요소를 못 쓰고, 우선순위가 가장 높아 나중에 덮어쓰기 어렵다.

### 2-4. `public/`과 `src/assets/` 고르기

파비콘·robots.txt·이름이 고정돼야 하는 파일은 `public/`, 컴포넌트가 쓰는 일반 이미지는 `src/assets/`에 두고 `import`하는 것이 Vite 문서의 권장이다. `public/`은 경로가 `/`로 시작하므로 하위 경로에 배포하면 `base` 설정을 맞춰야 한다.

## 3. 더 나아가 알면 좋은 것

### 3-1. CSS Modules

`Button.module.css`처럼 이름 붙이면 Vite가 클래스명을 `Button_primary_x1y2z`식으로 바꿔 **컴포넌트 단위로 스코프**를 잡아 준다. 1-2에서 본 "import한 CSS는 전역"이라는 문제의 표준 해법이다.

```jsx
import styles from "./Button.module.css";
<button className={styles.primary}>확인</button>
```

### 3-2. CSS-in-JS와 유틸리티 CSS

styled-components·Emotion은 스타일을 JS 안에 템플릿 리터럴로 쓰고 props에 따라 바꾼다. Tailwind CSS는 반대로 미리 정의된 유틸리티 클래스(`p-2 text-white bg-blue-500`)를 `className`에 나열한다. 어느 쪽이든 1-1의 "스타일은 객체"와 1-2의 "클래스는 문자열"이라는 기본 위에 얹힌다.

### 3-3. 다음에 볼 키워드

- CSS Modules · `*.module.css`
- Tailwind CSS · styled-components
- Vite `base` 설정과 정적 자산 처리(`import.meta.env.BASE_URL`)
- `<img>`의 `alt`·`loading="lazy"`와 접근성
- React Router — 컴포넌트를 `main.jsx`에서 갈아끼우는 대신 경로로 나누기

## 실습 파일

- `KDT_2026/2026_React/src/example/day03/exam1.jsx` — 인라인 `style` 객체(바깥 상수·그 자리 리터럴), `className`·`id` 선택자, 이미지 세 경로 비교
- `KDT_2026/2026_React/src/index.css` — `#backEndSub`·`.warnings` 규칙, 컴포넌트에서 `import`되는 전역 CSS
- `KDT_2026/2026_React/src/main.jsx` — day03 컴포넌트로 진입점 교체

## 관련 노트

[[React MOC]] · [[React day02 모달과 컴포넌트 간 상태 전달]] · [[React day03 폼 제출과 입력값 읽기]] · [[React day01 컴포넌트와 렌더링]] · [[KDT_2026 학습 지도]]
