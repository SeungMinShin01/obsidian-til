---
출처: Claude 분석
원본: KDT_2026/2026_React/src/example/day05
작성일: 2026-09-17
tags: [학습, react]
---

# React day05 — 컴포넌트 생명주기와 useEffect

> 실습 파일: `src/example/day05/App.jsx` · `src/example/day05/Lifecycle.jsx` · `src/example/day05/TopNav.jsx` · `src/example/day05/exam.md` · `src/main.jsx`
> 허브: [[React MOC]] · 이전: [[React day04 React Router 도입과 라우트 정의]] · 다음: [[React day05 외부 API 호출과 목록 렌더링]]

day05는 **컴포넌트의 생명주기(lifecycle)** 를 눈으로 확인하는 날이다. day02에서 `useEffect`를 "첫 렌더링 뒤에 한 번 서버를 부르는 도구"로 썼는데, 그건 `useEffect`의 세 가지 쓰임 중 하나일 뿐이었다. 이번에는 상자를 좌우로 옮기는 아주 작은 컴포넌트 하나에 `console.log`를 심어, **컴포넌트가 언제 태어나고(마운트) 언제 다시 그려지고(업데이트) 언제 사라지는지(언마운트)** 를 콘솔 로그의 순서로 직접 본다. 화면에 보이는 결과보다 로그가 찍히는 순서가 이 날의 학습 대상이다.

## 1. 배운 내용

### 1-1. 재렌더링이 일어나는 기준

`exam.md`에 적어 둔 전제부터 정리한다.

- 컴포넌트는 **함수**이고, 그 함수는 `return` 한 번으로 화면에 그릴 JSX를 내놓는다
- 함수는 한 번 실행되고 끝나므로, 화면을 최신 상태로 바꾸려면 **함수를 다시 실행(재렌더링)** 하는 수밖에 없다
- 재렌더링의 방아쇠는 두 가지 — **state 변경**과 **props 변경**

| 상황 | 함수 재실행 | 화면 갱신 |
| --- | --- | --- |
| 일반 변수 `let x = 1` 을 바꿈 | X | X |
| `setXXX(...)` 로 state 변경 | O | O |
| 부모가 내려주는 props 값이 바뀜 | O | O |

SPA(Single Page Application)는 HTML 문서를 새로 받아오지 않고 이 재실행으로만 화면을 바꾸기 때문에, "언제 함수가 다시 도는가"를 아는 것이 곧 리액트의 동작을 아는 것이다.

### 1-2. `useEffect`의 세 가지 형태 — 의존성 배열이 전부를 정한다

`useEffect(콜백, 의존성배열)`에서 **두 번째 인수를 어떻게 주느냐**에 따라 실행 시점이 완전히 달라진다.

```jsx
useEffect(() => { ... }, []);          // 마운트 직후 한 번만
useEffect(() => { ... }, [state변수]);  // 마운트 + 그 값이 바뀔 때마다
useEffect(() => { ... });               // 렌더링될 때마다 (매번)
```

| 형태 | 실행 시점 | 쓰임 |
| --- | --- | --- |
| `[]` (빈 배열) | 마운트 직후 1회 | 첫 목록 조회, 타이머 등록, 이벤트 리스너 등록 |
| `[a, b]` | 마운트 + `a`나 `b`가 바뀐 렌더링 뒤 | 선택된 항목이 바뀔 때 상세 조회 |
| 배열 생략 | 모든 렌더링 뒤 | 거의 쓰지 않음 |

배열을 생략한 형태가 위험한 이유는 분명하다. 그 안에서 `setXXX`를 부르면 **상태 변경 → 재렌더링 → effect 실행 → 상태 변경**이 끝없이 돌아 무한 루프가 된다. 배열을 생략하는 건 "렌더링마다 반드시 다시 해야 하는 일"일 때뿐이고, 실무에서는 대부분 `[]`나 `[의존값]`을 쓴다.

의존성 배열은 **감시 목록**이라고 이해하면 편하다. 배열에 넣은 값이 직전 렌더링 때와 달라졌을 때만 콜백이 다시 돈다. 빈 배열은 "감시할 게 없다 = 다시 돌 일이 없다"가 되어 자연히 1회 실행이 된다.

### 1-3. 정리 함수(cleanup) — `return`이 언마운트 자리다

`useEffect`의 콜백이 **함수를 반환하면**, 그 반환된 함수가 정리(cleanup) 함수가 된다.

```jsx
useEffect(() => {
  console.log("useEffect 실행 --> 마운트");
  return () => {
    console.log("useEffect 실행 --> 언마운트");
  };
});
console.log("return 실행 --> 렌더링");
```

정리 함수가 불리는 시점은 두 가지다.

1. 컴포넌트가 화면에서 **사라질 때**(언마운트) — 라우트가 바뀌어 다른 페이지로 넘어가는 경우가 대표적이다
2. effect가 **다시 실행되기 직전** — 이전 effect가 벌여 놓은 일을 치우고 새로 시작한다

그래서 정리 함수의 본래 용도는 뒷정리다. `setInterval`로 켠 타이머를 `clearInterval`로 끄고, `addEventListener`로 붙인 리스너를 `removeEventListener`로 떼고, 진행 중인 요청을 취소한다. 이걸 빼먹으면 사라진 컴포넌트의 타이머가 계속 돌면서 메모리 누수와 "사라진 컴포넌트의 상태를 바꾸려 한다"는 경고로 이어진다.

### 1-4. 로그로 확인하는 실행 순서

`MoveBox` 컴포넌트에는 로그가 두 군데 심겨 있다. 컴포넌트 함수 본문의 `console.log("return 실행 --> 렌더링")`과 `useEffect` 안의 마운트·언마운트 로그다. 버튼을 눌러 상태를 바꾸면 콘솔에 이런 순서가 쌓인다.

```
return 실행 --> 렌더링        ← 함수 본문이 먼저 돈다
useEffect 실행 --> 마운트      ← 화면에 그려진 뒤 effect
(좌측이동 클릭)
return 실행 --> 렌더링        ← 상태가 바뀌어 함수 재실행
useEffect 실행 --> 언마운트    ← 이전 effect 정리
useEffect 실행 --> 마운트      ← 새 effect 실행
```

여기서 핵심 두 가지를 읽을 수 있다.

- **함수 본문이 먼저, `useEffect`는 나중.** effect는 "화면이 실제로 그려진 뒤"에 실행되는 후처리다. 그래서 effect 안에서는 이미 그려진 DOM을 만질 수 있고, 반대로 화면에 그릴 값을 effect에서 계산하면 한 박자 늦게 반영된다
- **재실행 때는 정리가 먼저 끼어든다.** 위 예시는 의존성 배열이 없으니 렌더링마다 정리와 실행이 한 쌍으로 반복된다. `[]`를 붙이면 이 쌍은 처음과 끝에 한 번씩만 나타난다

개발 모드에서는 React StrictMode가 마운트를 일부러 두 번 실행해 보기도 한다. 로그가 두 벌씩 찍히면 정리 함수가 제대로 짝을 맞추고 있는지 점검하라는 신호로 보면 된다.

### 1-5. `MoveBox` — 상태 두 개로 움직이는 상자

```jsx
function MoveBox(props) {
  const [position, setPosition] = useState(props.initPosition);
  const [leftCount, setLeftCount] = useState(1);

  const boxStyle = {
    backgroundColor: "red",
    position: "relative",
    textAlign: "center",
    width: "100px",
    height: "100px",
    margin: "10px",
    lineHeight: "100px",
    left: `${position}px`,
  };

  const moveLeft = () => {
    setPosition(() => position - 20);
    setLeftCount(() => leftCount + 1);
  };
  const moveRight = () => {
    setPosition(() => position + 20);
  };
  // ...
}
```

정리하면 이런 구조다.

| 조각 | 설명 |
| --- | --- |
| `props.initPosition` | 부모가 내려준 시작 좌표를 `useState`의 초기값으로 쓴다. 초기값은 **첫 렌더링에서 한 번만** 반영된다 |
| `position` | 상자의 `left` 값. 20px씩 더하고 뺀다 |
| `leftCount` | 좌측 이동을 누른 횟수. 상자 안 숫자로 표시한다 |
| `boxStyle` | day03에서 다룬 인라인 스타일 객체. 값이 숫자가 아니라 **단위까지 붙인 문자열**이라 문자열 조립이 필요하다 |

스타일 객체 안의 `left`처럼 **변수를 문자열에 끼워 넣을 때는 백틱(`` ` ``)으로 감싼 템플릿 리터럴**을 쓴다. 따옴표로 감싸면 `${...}` 표기가 그대로 글자로 남아 CSS 값으로 해석되지 않으므로, 좌표가 움직이지 않을 때 가장 먼저 확인할 자리다. `position: "relative"`가 함께 있어야 `left`가 기준점 대비 이동으로 동작한다는 것도 같이 챙긴다.

버튼은 day01에서 정리한 대로 `onClick={moveLeft}` — **함수를 넘기고 실행하지 않는다.** 클릭 → `setXXX` → 상태 변경 → 함수 재실행 → 새 `boxStyle` 계산 → 상자가 옮겨 그려지는 흐름이 1-1의 "재렌더링 기준"과 정확히 맞물린다.

### 1-6. `TopNav` — day05의 진행 방향이 적힌 네비게이션

```jsx
import { NavLink } from "react-router-dom";

export default function TopNavi(props) {
  return (
    <div>
      <NavLink to="/">생명주기</NavLink>
      <NavLink to="/local">내부통신</NavLink>
      <NavLink to="/external">외부통신</NavLink>
    </div>
  );
}
```

day04에서 만든 `NavLink`를 그대로 가져와 세 갈래를 걸어 뒀다. 메뉴 이름이 곧 day05의 목차다 — **생명주기**(지금), **내부통신**(컴포넌트끼리 값을 주고받기), **외부통신**(서버와 주고받기). 이렇게 네비게이션을 먼저 세워 두면 새 주제를 배울 때마다 `Route` 한 줄과 컴포넌트 하나만 추가하면 된다.

### 1-7. `App4` — 공통 헤더 + 라우트 표

```jsx
import { Routes, Route } from "react-router-dom";
import Lifecycle from "./Lifecycle";
import TopNavi from "./TopNav";

export default function App4(props) {
  return (
    <>
      <TopNavi></TopNavi>
      <Routes>
        <Route path="/" element={<Lifecycle />} />
      </Routes>
    </>
  );
}
```

day04에서 정리한 구조 그대로다. **경로가 바뀌어도 그대로 남을 것(`TopNavi`)은 `Routes` 바깥에, 경로에 따라 갈아끼울 것은 `Routes` 안에** 둔다. `main.jsx`에서는 진입 컴포넌트를 day05의 `App4`로 바꾸고 `BrowserRouter`로 감싼 형태를 유지한다.

```jsx
import { BrowserRouter } from "react-router-dom";
import App4 from "./example/day05/App";

create.render(
  <BrowserRouter>
    <App4></App4>
  </BrowserRouter>,
);
```

라우터 부품(`Routes`·`Route`·`NavLink`)은 파일마다 `react-router-dom`에서 **직접 `import` 해야** 쓸 수 있다. 같은 앱 안이라고 자동으로 따라오지 않으니, 컴포넌트를 새 파일로 나눌 때는 import 목록부터 맞추는 습관을 들인다.

### 1-8. 세 형태를 한 자리에서 바꿔 가며 보기 — 최종 형태는 `[leftCount]`

`MoveBox`의 `useEffect`는 결국 의존성 배열 자리를 이렇게 정리했다. 세 형태를 각각 주석으로 남겨 두고 하나만 살려 두는 방식이라, 주석을 옮겨 가며 콘솔 로그가 어떻게 달라지는지 바로 비교할 수 있다.

```jsx
useEffect(() => {
  console.log("useEffect 실행 --> 마운트");
  return () => {
    console.log("useEffect 실행 --> 언마운트");
  };
  //});           // [1] 배열 생략   : 마운트 + 렌더링될 때마다
  // }, []);      // [2] 빈 배열     : 마운트 때 한 번
}, [leftCount]);  // [3] 값 지정     : 마운트 + leftCount가 바뀔 때
```

`[leftCount]`를 고르면 재미있는 비대칭이 생긴다. 두 버튼 모두 상태를 바꾸므로 **렌더링 로그는 양쪽 다 찍히는데, effect는 좌측이동에서만 다시 돈다.**

| 누른 버튼 | 바뀌는 상태 | `return 실행 --> 렌더링` | effect 정리 + 재실행 |
| --- | --- | --- | --- |
| 우측이동 | `position`만 | O | X (`leftCount`가 그대로라서) |
| 좌측이동 | `position` + `leftCount` | O | O |

여기서 얻는 감각이 핵심이다. **재렌더링과 effect 실행은 별개의 사건**이다. 상태가 바뀌면 함수는 반드시 다시 돌지만, effect가 따라 도는지는 오직 의존성 배열이 정한다. 화면을 다시 그리는 일과 "값이 바뀌었으니 서버를 다시 부른다" 같은 부수 작업을 분리해 두는 장치가 바로 이 배열이다.

주석으로 세 형태를 붙여 둔 코드는 그대로 두고, 나중에 `useEffect`가 왜 이 시점에 돌았는지 헷갈릴 때 다시 열어 보면 좋다. 배열을 비웠을 때(`[]`) 좌측이든 우측이든 effect가 한 번도 다시 돌지 않는 것까지 확인해 두면 세 형태의 차이가 로그 한 벌로 남는다.

## 2. 추가로 알면 좋은 활용법

### 2-1. 함수형 업데이트 — 이전 값을 인수로 받기

`setXXX`에 함수를 넘기면, 그 함수의 **매개변수로 직전 상태값**이 들어온다.

```jsx
setPosition((prev) => prev - 20);   // prev = 직전 position
setLeftCount((prev) => prev + 1);
```

바깥 변수 `position`을 그대로 쓰는 것과 결과가 같아 보이지만, 차이가 드러나는 순간이 있다. 한 이벤트 안에서 `setCount(count + 1)`를 두 번 부르면 둘 다 같은 `count`를 읽어 **1만 증가**한다. React가 여러 상태 갱신을 모아 한 번에 처리(배칭)하는 동안 `count`는 옛 값 그대로이기 때문이다. `setCount((prev) => prev + 1)`로 쓰면 앞선 갱신의 결과를 받아 2가 증가한다.

기준은 단순하다. **새 값이 이전 값에서 계산되면 함수형으로** 쓰는 편이 안전하다. 비동기 콜백이나 `setTimeout` 안에서 상태를 바꿀 때도 마찬가지다.

### 2-2. `useEffect` 정리 함수의 실제 쓰임

```jsx
useEffect(() => {
  const id = setInterval(() => {
    setPosition((prev) => prev + 1);
  }, 100);
  return () => clearInterval(id);   // 반드시 짝을 맞춘다
}, []);
```

```jsx
useEffect(() => {
  const onResize = () => setWidth(window.innerWidth);
  window.addEventListener("resize", onResize);
  return () => window.removeEventListener("resize", onResize);
}, []);
```

**무언가를 "켜는" effect에는 반드시 "끄는" 정리 함수를 붙인다** — 타이머, 이벤트 리스너, 구독, WebSocket 연결이 모두 여기 해당한다. 서버 요청에는 `AbortController`로 취소 신호를 보내 두면, 응답이 오기 전에 페이지를 떠났을 때 헛된 상태 갱신을 막을 수 있다.

### 2-3. 렌더링 중에 하면 안 되는 일

컴포넌트 함수 본문은 **화면에 그릴 JSX를 계산하는 자리**이고, 여러 번 불려도 결과가 같아야 한다. 그래서 다음은 본문이 아니라 `useEffect`나 이벤트 핸들러로 옮긴다.

- 서버 요청 보내기 (본문에서 부르면 렌더링마다 요청이 나가 무한 반복)
- `document.title` 바꾸기, DOM 직접 조작
- 타이머·리스너 등록
- 상태 변경 (`setXXX`를 본문에서 그대로 부르면 곧바로 무한 루프)

반대로 `console.log`처럼 결과에 영향을 주지 않는 관찰은 본문에 둬도 괜찮고, 이번 예제가 바로 그 용도로 쓴 경우다.

### 2-4. 클래스 컴포넌트 생명주기와의 대응

용어가 "마운트·업데이트·언마운트"인 이유는 훅 이전의 클래스 컴포넌트에서 왔기 때문이다. 옛 코드나 블로그 글을 읽을 때를 위해 대응표만 기억해 둔다.

| 클래스 메서드 | 훅 표현 |
| --- | --- |
| `componentDidMount` | `useEffect(() => {...}, [])` |
| `componentDidUpdate` | `useEffect(() => {...}, [의존값])` |
| `componentWillUnmount` | `useEffect`의 `return` 정리 함수 |

세 갈래로 흩어져 있던 것을 `useEffect` 하나가 **"관련된 일끼리 묶어서"** 처리하는 형태로 바꾼 것이 훅의 설계 의도다. 타이머 등록과 해제가 한 함수 안에 나란히 있는 편이 읽기 쉽다.

### 2-5. 초기값은 한 번만 — props로 초기화할 때의 함정

`useState(props.initPosition)`의 초기값은 **첫 렌더링에서만** 쓰인다. 이후 부모가 `initPosition`을 바꿔 내려보내도 이미 만들어진 state는 따라 바뀌지 않는다. props 변경에 상태를 맞춰야 한다면 `useEffect(() => setPosition(props.initPosition), [props.initPosition])`처럼 명시하거나, 아예 `key` 값을 바꿔 컴포넌트를 새로 마운트시키는 방법을 쓴다.

## 3. 더 나아가 알면 좋은 것

### 3-1. 왜 effect가 "그린 뒤"에 실행되는가

브라우저가 화면을 실제로 칠하는 일을 막지 않기 위해서다. `useEffect`는 화면이 그려진 **다음**에 비동기로 실행되므로, 무거운 작업을 넣어도 첫 화면이 늦게 뜨지 않는다. 반대로 "그려지기 전에 반드시 끝나야 하는" 측정·보정 작업이 있다면 `useLayoutEffect`를 쓴다. 이쪽은 화면 칠하기를 잠시 막고 동기로 실행되므로, 깜빡임 없이 위치를 잡아야 할 때만 예외적으로 고른다.

### 3-2. `useRef` — 재렌더링을 일으키지 않는 저장소

타이머 id처럼 **값은 기억해야 하지만 화면과는 상관없는 것**은 state에 두면 낭비다. 값이 바뀔 때마다 재렌더링이 일어나기 때문이다. `useRef`는 `.current`에 값을 담아 두고 렌더링을 거쳐도 유지하되, 바꿔도 재렌더링을 일으키지 않는다. DOM 요소를 직접 잡을 때(`ref={inputRef}` → `inputRef.current.focus()`)도 같은 훅을 쓴다.

### 3-3. 애니메이션은 CSS transition에 맡기기

상자를 20px씩 옮기는 예제를 부드럽게 만들려면, 매 프레임 상태를 바꾸는 대신 스타일에 `transition: "left 0.2s"` 한 줄을 더하는 편이 낫다. 위치 계산은 리액트가 하고, 그 사이를 메우는 일은 브라우저에 맡기는 분담이다. 상태를 프레임마다 바꾸면 그만큼 컴포넌트 함수가 다시 돌아 비용이 커진다.

### 3-4. 다음에 볼 키워드

- `useEffect` 의존성 배열과 ESLint `exhaustive-deps` 규칙
- `useLayoutEffect` · `useRef` · `useMemo` · `useCallback`
- StrictMode의 이중 마운트와 정리 함수 검증
- 커스텀 훅으로 생명주기 로직 묶어내기 (`useInterval`, `useFetch`)
- 데이터 패칭 라이브러리(React Query)가 effect를 대신하는 이유
- `Context` / 전역 상태 관리 — day05의 "내부통신" 갈래
- `axios`와 비동기 통신 패턴 — day05의 "외부통신" 갈래

## 실습 파일

- `KDT_2026/2026_React/src/example/day05/App.jsx`
- `KDT_2026/2026_React/src/example/day05/Lifecycle.jsx`
- `KDT_2026/2026_React/src/example/day05/TopNav.jsx`
- `KDT_2026/2026_React/src/example/day05/exam.md`
- `KDT_2026/2026_React/src/main.jsx`

## 관련 노트

[[React MOC]] · [[React day04 React Router 도입과 라우트 정의]] · [[React day05 외부 API 호출과 목록 렌더링]] · [[KDT_2026 학습 지도]]
