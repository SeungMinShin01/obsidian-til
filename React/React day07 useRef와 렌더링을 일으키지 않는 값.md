---
출처: Claude 분석
원본: KDT_2026/2026_React/src/example/day06
작성일: 2026-09-21
tags: [학습, react]
---

# React day07 — useRef와 렌더링을 일으키지 않는 값

> 실습 파일: `src/example/day06/useRefExam1.jsx` · `TopNavi.jsx` · `App.jsx`
> 허브: [[React MOC]] · 이전: [[React day06 내 서버를 거쳐 받는 공공데이터]] · 다음: (예정)

지금까지 컴포넌트가 기억하는 값은 전부 `useState`였다. 이번에는 세 번째 종류의 값 보관법인 `useRef`가 나온다. 핵심 질문은 하나다 — **값은 유지하고 싶은데 화면은 다시 그리고 싶지 않다면?** 이걸 확인하려고 같은 카운터를 세 가지 방법(state 변수·ref 변수·지역변수)으로 나란히 만들어 버튼 세 개로 비교하는 실험을 했다.

## 1. 배운 내용

### 1-1. 훅(Hook)이라는 이름 정리

`use`로 시작하는 함수들은 리액트가 만들어 둔 **컴포넌트와 연관된 기능들**이고, 이걸 훅이라고 부른다. 지금까지 쓴 것을 이 이름으로 다시 묶으면 이렇다.

| 훅 | 역할 |
| --- | --- |
| `useState` | 값 보관 + 바뀌면 재렌더링 |
| `useEffect` | 렌더링 뒤에 실행할 부수 작업 (마운트·언마운트·의존성) |
| `useRef` | 값 보관만, 재렌더링 없음 (이번 시간) |

훅은 컴포넌트 함수의 최상위에서만 부른다는 규칙은 `useRef`에도 똑같이 적용된다.

### 1-2. 카운터 셋을 나란히 — state · ref · 지역변수

`useRefExam1.jsx`의 뼈대다. 숫자 하나를 놓고 세 가지 보관법을 버튼으로 각각 증가시킨다.

```jsx
import { useState, useRef } from "react";

export default function UseRefExam1(props) {
  const [stateNum, setStateNum] = useState(0); // state 변수
  const refNum = useRef(0);                    // ref 변수
  let myNum = 0;                               // 지역변수

  const plusState = () => setStateNum(stateNum + 1);
  const plusRef = () => { refNum.current = refNum.current + 1; };
  const plusMyNum = () => { ++myNum; };

  return (
    <>
      <p> state : {stateNum}</p>
      <p> ref : {refNum.current}</p>
      <p> myNum : {myNum}</p>
      <button onClick={plusState}>증가1</button>
      <button onClick={plusRef}>증가2</button>
      <button onClick={plusMyNum}>증가3</button>
    </>
  );
}
```

`useRef(초기값)`이 돌려주는 것은 값 자체가 아니라 **`{ current: 초기값 }` 모양의 객체 하나**다. 그래서 읽을 때도 쓸 때도 `refNum.current`로 접근한다. `useState`가 `[값, setter]` 배열을 주는 것과 대비해 두면 헷갈리지 않는다.

| 구분 | 선언 | 접근 | 바꾸는 법 | 재렌더링 | 값 유지 |
| --- | --- | --- | --- | --- | --- |
| state 변수 | `useState(0)` | `stateNum` | `setStateNum(…)` | **일으킨다** | 유지 |
| ref 변수 | `useRef(0)` | `refNum.current` | `refNum.current = …` 직접 대입 | 일으키지 않는다 | **유지** |
| 지역변수 | `let myNum = 0` | `myNum` | `++myNum` | 일으키지 않는다 | 재렌더링마다 초기화 |

### 1-3. 버튼을 눌러 보면 드러나는 차이

실제로 눌러 보면 세 값의 성격이 그대로 화면에 나온다.

- **증가1(state)** — 누를 때마다 `setStateNum`이 재렌더링을 일으켜 화면 숫자가 바로 올라간다.
- **증가2(ref)** — 아무리 눌러도 **화면은 그대로**다. 재렌더링이 없으니 `{refNum.current}` 자리가 다시 계산되지 않는다. 하지만 값 자체는 객체 안에 계속 쌓이고 있어서, 나중에 증가1을 눌러 재렌더링이 일어나는 순간 **그동안 쌓인 ref 값이 한꺼번에** 나타난다.
- **증가3(지역변수)** — 누르는 순간 값은 올라가지만 화면에 안 보이는 건 물론이고, 다음 재렌더링 때 함수가 처음부터 다시 실행되면서 `let myNum = 0`으로 **되돌아간다**. 증가1을 눌러 보면 myNum이 다시 0인 것으로 확인된다.

정리하면 이렇다. 재렌더링 = 컴포넌트 함수의 재실행이라는 [[React day06 내 서버를 거쳐 받는 공공데이터]] 이전부터 이어져 온 원리가 여기서도 기준이 된다. 지역변수는 재실행에 쓸려 나가고, state는 리액트가 함수 바깥에 보관해 주면서 재실행까지 일으키고, **ref는 보관만 하고 재실행은 일으키지 않는** 중간 지대다.

### 1-4. day06 폴더의 라우팅 골격

이번 예제도 이전처럼 라우트 표에 꽂아서 본다. `App.jsx`에 `/`·`/use-ref1`·`/use-ref2` 세 경로를 두고, `TopNavi`의 `NavLink` 두 개로 예제 사이를 오가는 구조다. 라우터 골격은 day04에서 만든 그대로이고, `element`에 꽂히는 예제 컴포넌트만 갈아 끼운다.

## 2. 추가로 알면 좋은 활용법

### 2-1. state로 둘까 ref로 둘까 — 판단 기준

기준은 한 줄이다. **그 값이 바뀔 때 화면도 바뀌어야 하면 state, 화면과 무관하게 기억만 하면 되면 ref.**

ref가 어울리는 값의 전형은 이런 것들이다.

- 타이머 id (`setInterval` 반환값) — 해제할 때만 필요하고 화면에는 안 나온다
- 이전 렌더링의 값 저장 (prev 값 비교)
- "이미 요청을 보냈는지" 같은 플래그 — 화면에 표시하지 않는 진행 상태
- 렌더링 횟수 세기 — state로 세면 세는 행위가 또 렌더링을 일으켜 무한 루프가 된다

반대로 ref 값을 화면에 `{refNum.current}`로 찍는 것은 이번 실험처럼 원리를 확인할 때나 쓰는 모양이고, 실전에서는 화면에 보일 값을 ref에 두지 않는 편이 안전하다. 갱신이 안 된 낡은 값이 표시된 채 남기 때문이다.

### 2-2. 훅 import 빠뜨리지 않기

훅은 전부 `react` 패키지에서 구조 분해로 가져와야 한다. 쓰는 훅이 늘 때마다 첫 줄의 `import { useState, useRef } from "react"`에 함께 추가하는 습관을 들이는 편이 안전하다. import 없이 훅 이름만 쓰면 정의되지 않은 함수 호출로 바로 에러가 난다.

같은 맥락에서 JSX 태그 이름도 주의할 점이 있다. **컴포넌트 태그는 반드시 대문자로 시작해야 한다.** 소문자로 시작하는 태그(`<div>`처럼)는 리액트가 HTML 기본 태그로 취급하기 때문에, 컴포넌트를 소문자 이름으로 꽂으면 화면에 아무것도 안 나온다. `use...`로 시작하는 예제 파일이라도 컴포넌트 이름은 `UseRefExam1`처럼 대문자로 시작시키고 태그도 그렇게 쓴다.

### 2-3. NavLink에는 `to`가 필요하다

`NavLink`는 `<a>`의 `href`에 해당하는 `to` 속성으로 목적지를 받는다. 라우트 표의 `path`와 짝을 맞춰 `<NavLink to="/use-ref1">useRef1</NavLink>`처럼 쓰면, 현재 주소와 일치할 때 `active` 클래스가 붙는 것까지 day04에서 본 그대로다.

### 2-4. ref 갱신과 렌더링 타이밍

ref는 바꿔도 리액트에 알림이 가지 않으므로, **렌더링 도중(함수 본문)에 읽고 쓰는 것보다 이벤트 핸들러나 `useEffect` 안에서 다루는 편이 안전하다.** 본문에서 `refNum.current`를 바꾸면 언제 실행됐는지 추적이 어려워지고, StrictMode의 이중 호출 같은 상황에서 값이 두 번 바뀔 수 있다.

## 3. 더 나아가 알면 좋은 것

### 3-1. useRef의 두 번째 얼굴 — DOM 참조

`useRef`의 진짜 주 용도는 값 보관보다 **DOM 요소를 직접 잡는 것**이다. JSX 태그에 `ref={inputRef}`를 걸면 렌더링 뒤 `inputRef.current`에 실제 DOM 노드가 들어오고, `inputRef.current.focus()`처럼 직접 조작할 수 있다. 순수 JS에서 하던 `document.querySelector`의 리액트식 대체다. 비제어 입력값 읽기(`inputRef.current.value`)도 이 길로 간다 — [[React MOC]]의 day03 폼 노트에서 예고했던 `useRef`가 바로 이것이다.

### 3-2. 다음에 볼 키워드

- `forwardRef` — 부모가 자식 컴포넌트 안쪽의 DOM에 ref를 꽂고 싶을 때
- `useImperativeHandle` — 자식이 부모에게 노출할 조작 메소드를 골라 주기
- ref 콜백(`ref={(el) => …}`) — 목록처럼 개수가 변하는 요소들의 ref
- `useMemo` · `useCallback` — 재렌더링 사이에 "계산 결과·함수"를 유지하는 또 다른 훅들 (ref가 값을 유지하듯)
- `flushSync` — 배칭을 건너뛰고 즉시 렌더링이 필요한 예외 상황

## 실습 파일

- `KDT_2026/2026_React/src/example/day06/useRefExam1.jsx` — state·ref·지역변수 카운터 세 개를 버튼으로 비교하는 실험 (`useRef(0)`과 `.current`, 재렌더링 여부와 값 유지 여부의 조합)
- `KDT_2026/2026_React/src/example/day06/TopNavi.jsx` — useRef 예제 사이를 오가는 `NavLink` 상단 네비
- `KDT_2026/2026_React/src/example/day06/App.jsx` — `/`·`/use-ref1`·`/use-ref2` 라우트 표, day04 라우터 골격 재사용

## 관련 노트

[[React MOC]] · [[React day06 내 서버를 거쳐 받는 공공데이터]] · [[KDT_2026 학습 지도]]
