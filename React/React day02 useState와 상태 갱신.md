---
출처: Claude 분석
원본: KDT_2026/2026_React/src/example/day02
작성일: 2026-09-14
tags: [학습, react]
---

# React day02 — useState와 상태 갱신

> 실습 파일: `src/example/day02/exam2.jsx` · `p117_120/useState.jsx` · `p117_120/FrontComp.jsx` · `p117_120/BackComp.jsx`
> 허브: [[React MOC]] · 이전: [[React day02 컴포넌트 분리와 콜백 props]] · 다음: [[React day02 useEffect와 fetch로 서버 CRUD]]

day02의 세 번째 갈래다. 앞 두 노트에서 "언젠가 볼 것"으로 미뤄 둔 `useState`가 드디어 등장한다. 핵심 질문은 하나다 — **버튼을 눌러 변수를 늘렸는데 왜 화면은 그대로인가?** 이 질문에 답하면서 상태변수·재렌더링·주소값 비교까지 이어지고, 마지막에는 앞 노트의 콜백 props와 합쳐져 "자식 클릭으로 부모의 상태를 바꾸는" 패턴이 완성된다.

## 1. 배운 내용

### 1-1. 일반 변수는 늘어나도 화면에 안 보인다

```jsx
// src/example/day02/exam2.jsx
let 전역변수 = 0;
export default function Component2(props) {
  let 지역변수 = 0;
  const 증가함수1 = () => {
    전역변수++;
    지역변수++;
  };
  return (
    <>
      <h4>전역변수; {전역변수} , 지역변수 : {지역변수}</h4>
      <button onClick={증가함수1}>버튼1</button>
    </>
  );
}
```

버튼1을 눌러도 화면의 숫자는 0에서 멈춰 있다. 변수 자체는 분명히 늘어난다(콘솔에 찍어 보면 확인된다). 문제는 **`return`이 한 번만 실행됐다**는 데 있다. 컴포넌트 함수는 처음 렌더링될 때 한 번 호출되어 JSX를 돌려주고 끝난다. 그 뒤로 변수가 바뀌어도 함수를 다시 부르지 않으니 새 JSX가 만들어질 일이 없고, 화면은 처음 그린 그대로 남는다.

정리하면 이렇다.

| 구분 | 값이 바뀌는가 | 화면이 바뀌는가 | 이유 |
| --- | --- | --- | --- |
| 전역변수 | O | X | 함수가 재호출되지 않아 `return`이 다시 실행되지 않음 |
| 지역변수 | O | X | 위와 같음. 게다가 재호출되면 `0`으로 초기화됨 |
| 상태변수 | O | **O** | `setXXX`가 컴포넌트를 재호출해 `return`을 다시 실행 |

### 1-2. useState — 값을 바꾸면서 함수를 다시 부르는 장치

```jsx
// const [ 상태변수명, set상태변수명 ] = useState(초기값);
const [count, setCount] = useState(0);
const 증가함수2 = () => {
  setCount(++count);
};
<h4> 상태변수: {count} </h4>
<button onClick={증가함수2}>버튼2</button>
```

`useState(초기값)`은 **[현재 값, 값을 바꾸는 함수]** 두 칸짜리 배열을 돌려준다. 이걸 구조 분해로 받아서 `count`와 `setCount`라는 이름을 붙인다(이름은 자유지만 `xxx` / `setXxx` 짝이 관례다).

`setCount(새 값)`을 부르면 두 가지 일이 일어난다.

1. 상태의 값이 새 값으로 바뀐다
2. **컴포넌트 함수가 자동으로 다시 호출**되어 `return`이 다시 실행된다 — 수업 표현으로는 "함수 재호출", 화면 입장에서는 "새로고침"

재호출되면서 함수 안에 `let`으로 선언한 지역변수는 다시 `0`으로 초기화되지만, 상태변수는 React가 바깥에서 따로 기억하고 있어서 **값이 유지**된다. 그래서 버튼2를 누를 때마다 숫자가 1씩 올라간다. `useState`의 "state"가 곧 "함수가 다시 실행돼도 살아남는 값"이라는 뜻이다.

### 1-3. 주소값이 바뀌어야 새로고침된다

```jsx
const [array, setArray] = useState(["수박"]);
const 증가함수3 = () => {
  // array.push("사과");  → 내부적으로는 추가되지만 화면은 그대로
  array.push("사과");
  setArray([...array]);   // 새 배열을 만들어 넘겨야 다시 그린다
};
<h4> 상태변수: {array} </h4>
<button onClick={증가함수3}>버튼3</button>
```

배열 상태에서 흔히 부딪히는 대목이다. `array.push("사과")`만 하고 `setArray(array)`를 부르면 화면이 바뀌지 않는다. **React는 이전 상태와 새 상태를 주소값으로 비교**하기 때문이다 — `push`는 같은 배열 안에 요소를 넣을 뿐 배열의 주소는 그대로라서, React 입장에서는 "바뀐 게 없다"고 판단하고 재렌더링을 건너뛴다.

수업의 비유가 잘 들어맞는다.

- `3` → `4` : 리터럴은 고정값이라 값이 바뀌면 다른 상수를 가리킨다 (101호 → 102호). 숫자·문자열 상태는 그래서 그냥 `setCount(값)`으로 충분하다
- 과일상자(201호)에 수박(301호)을 넣고, 사과(302호)를 더 넣어도 **과일상자는 여전히 201호**다. 가방 하나에 핸드폰·지갑·노트를 넣어도 가방은 하나인 것과 같다

그래서 배열·객체 상태는 **스프레드 연산자로 복사본을 만들어** 넘긴다. `[...array]`는 요소는 같지만 주소가 다른 새 배열이고, `{...객체}`도 마찬가지다. 새 주소가 들어오니 React가 "바뀌었다"고 보고 다시 그린다.

| 상태 종류 | 갱신 방법 | 이유 |
| --- | --- | --- |
| 숫자·문자열·불리언 | `setCount(count + 1)` | 값 자체가 새 값 |
| 배열 | `setArray([...array, "사과"])` | 새 배열(새 주소)을 만들어야 함 |
| 객체 | `setObj({ ...obj, name: "새이름" })` | 새 객체(새 주소)를 만들어야 함 |

`{array}`처럼 배열을 JSX에 직접 넣으면 요소가 붙어서 출력된다(`수박사과`). 목록으로 보이게 하려면 [[React day02 객체 배열과 map 렌더링]]에서 본 `map`으로 `<li>`를 찍어야 한다.

### 1-4. 상태로 화면을 고르기 — 조건부 렌더링

```jsx
// src/example/day02/p117_120/useState.jsx
import { useState } from "react";
import FrontComp from "./FrontComp";
import BackComp from "./BackComp";

function Component3() {
  const [mode, setMode] = useState("both");
  let contents = "";
  if (mode == "front") {
    contents = <FrontComp onSetMode={(mode) => { setMode(mode); }} />;
  } else if (mode == "back") {
    contents = <BackComp setMode={setMode} />;
  } else {
    contents = (
      <>
        <FrontComp onSetMode={(mode) => { setMode(mode); }} />
        <BackComp setMode={setMode} />
      </>
    );
  }
  return (
    <>
      <h2>
        <a href="/" onClick={(event) => { event.preventDefault(); setMode("both"); }}>
          React-State
        </a>
      </h2>
      <ol>{contents}</ol>
    </>
  );
}
export default Component3;
```

교재 p117~120 예제다. 상태 `mode`가 `"front"` / `"back"` / `"both"` 중 하나를 갖고, **그 값에 따라 어떤 컴포넌트를 보여줄지가 달라진다**. 방법은 단순하다 — JSX를 변수 `contents`에 담아 두고 `if`로 갈아끼운 뒤 `return`에서 `{contents}`로 꽂는다. JSX도 결국 값이라 변수에 넣을 수 있고, `if`문은 `return` 바깥에서 쓴다는 것이 포인트다.

`setMode`가 불릴 때마다 `Component3`이 재호출되어 `if`가 다시 평가되고, 그 결과로 다른 컴포넌트가 그려진다. 상태 하나로 화면 구성을 통째로 바꾸는 셈이다. 제목 `React-State`를 누르면 `"both"`로 돌아간다.

### 1-5. 콜백 props로 자식이 부모 상태를 바꾼다

```jsx
// p117_120/FrontComp.jsx — props 통째로 받기
export default function FrontComp(props) {
  return (
    <>
      <li>
        <a href="/" onClick={(event) => { event.preventDefault(); props.onSetMode("front"); }}>
          프론트엔드
        </a>
      </li>
      <ul><li>HTML5</li><li>CSS3</li><li>Javascript</li><li>jQuery</li></ul>
    </>
  );
}

// p117_120/BackComp.jsx — 구조 분해로 받기
const BackComp = ({ setMode }) => {
  return (
    <>
      <li>
        <a href="/" onClick={(event) => { event.preventDefault(); setMode("back"); }}>
          백엔드
        </a>
      </li>
      <ul><li>Java</li><li>Oracle</li><li>JSP</li><li>Spring Boot</li></ul>
    </>
  );
};
export default BackComp;
```

[[React day02 컴포넌트 분리와 콜백 props]]의 콜백 props가 여기서 `useState`와 만난다. 상태 `mode`는 부모 `Component3`에 있다. 자식은 상태를 직접 못 건드리니 부모가 **상태를 바꾸는 함수를 props로 내려보내고**, 자식이 클릭 시 그 함수를 부른다. 그러면 부모의 상태가 바뀌고 → 부모가 재호출되고 → 자식까지 새로 그려진다. "데이터는 내려가고 이벤트는 올라간다"는 흐름이 상태까지 포함해 한 바퀴 도는 것이다.

두 자식이 함수를 받는 방식이 다른 점도 눈여겨볼 만하다.

| 컴포넌트 | 부모가 넘기는 것 | 자식이 받는 방식 |
| --- | --- | --- |
| `FrontComp` | `onSetMode={(mode) => { setMode(mode); }}` — `setMode`를 한 번 감싼 화살표 함수 | `props.onSetMode("front")` |
| `BackComp` | `setMode={setMode}` — `setMode` 자체 | `({ setMode })` 구조 분해 후 `setMode("back")` |

동작은 같다. `setMode`를 감싸서 넘기면 부모 쪽에서 로그를 찍거나 값을 검증하는 코드를 끼워 넣을 자리가 생기고, 그대로 넘기면 코드가 짧다. `useState.jsx` 안에 `handleSetMode`라는 이름의 감싼 함수도 선언되어 있는데, 이 역시 같은 용도의 자리다.

### 1-6. main.jsx에서 갈아끼우기

```jsx
// src/main.jsx
import Component3 from "./example/day02/p117_120/useState.jsx";
create.render(<Component3></Component3>);
```

진입점 `main.jsx`는 여전히 `createRoot` → `render` 구조이고, 마지막 `render`에 어느 컴포넌트를 넣느냐로 실습 화면을 고른다. 앞 예제들은 주석 처리해 두고 오늘 것만 살려 두는 방식이다.

## 2. 추가로 알면 좋은 활용법

### 2-1. 이전 값을 바탕으로 갱신할 때는 함수형 업데이트

```jsx
setCount(count + 1);        // 지금 값 기준
setCount((prev) => prev + 1); // 이전 상태를 인수로 받아 계산
```

`setCount(count + 1)`을 한 핸들러 안에서 두 번 부르면 둘 다 같은 `count`를 읽어서 결국 1만 오른다. 함수형으로 쓰면 React가 직전 상태를 넣어 주므로 두 번 부르면 2가 오른다. 상태 갱신이 비동기적으로 묶여 처리(배칭)되기 때문인데, 이전 값에 의존하는 갱신은 함수형으로 쓰는 편이 안전하다. 같은 이유로 `++count`처럼 상태변수를 직접 증감하는 대신 `count + 1`로 새 값을 계산해 넘기는 습관이 낫다.

### 2-2. 배열 상태를 다루는 관용구

`push`·`splice`처럼 원본을 바꾸는 메서드 대신 **새 배열을 돌려주는 방식**으로 통일하면 주소값 문제를 원천 차단할 수 있다.

```jsx
setArray([...array, "사과"]);                     // 추가
setArray(array.filter((f) => f !== "사과"));      // 삭제
setArray(array.map((f) => (f === "수박" ? "멜론" : f))); // 수정
```

`filter`·`map`은 항상 새 배열을 만들고, 스프레드로 끝에 붙이는 것도 새 배열이다. 원본을 `push`한 뒤 복사하는 것보다 처음부터 새 배열을 만드는 편이 의도가 분명하다.

### 2-3. 조건부 렌더링의 짧은 표기

`if`로 `contents`를 채우는 방식은 분기가 많을 때 읽기 좋다. 분기가 단순하면 JSX 안에서 바로 쓴다.

```jsx
{mode === "front" && <FrontComp onSetMode={setMode} />}
{mode === "back" ? <BackComp setMode={setMode} /> : <FrontComp onSetMode={setMode} />}
```

`&&`는 "조건이 참일 때만 그린다", 삼항은 "둘 중 하나를 고른다"에 쓴다. 셋 이상 갈리면 오늘처럼 `if`나 객체 매핑(`{ front: <FrontComp/>, back: <BackComp/> }[mode]`)이 낫다.

### 2-4. 상태 끌어올리기

오늘 예제는 그 자체가 **상태 끌어올리기(lifting state up)**다. `FrontComp`와 `BackComp` 둘 다에 영향을 주는 값(`mode`)은 둘의 공통 부모에 두고, 자식에게는 값이나 갱신 함수만 내려보낸다. 상태를 어디에 둘지 고민될 때는 "이 값을 누가 읽고 누가 바꾸는가"를 적어 보고, 관련된 컴포넌트들의 가장 가까운 공통 조상에 두면 된다.

## 3. 더 나아가 알면 좋은 것

### 3-1. 재렌더링의 실제 동작 — Virtual DOM

`setXXX`가 컴포넌트를 "새로고침"한다고 했지만, 브라우저 화면을 통째로 다시 그리는 것은 아니다. 새 JSX(가상 DOM 트리)를 만들어 이전 트리와 비교(diffing)하고, **달라진 부분만 실제 DOM에 반영**한다. 그래서 `useState`로 값을 바꿔도 순수 JS로 `innerHTML`을 갈아끼우는 것보다 효율적이고, 입력 중이던 다른 요소의 포커스도 유지된다. 주소값 비교(`Object.is`)는 이 비교를 시작할지 말지 정하는 첫 관문이다.

### 3-2. 불변성(immutability)

"주소값이 바뀌어야 새로고침된다"를 일반화하면 **상태는 불변으로 다룬다**는 원칙이 된다. 상태를 직접 고치지 않고 항상 새 값을 만들어 넘기면, React가 변경을 놓치지 않을 뿐 아니라 이전 상태로 되돌리기(undo)나 상태 변화 추적도 쉬워진다. 중첩이 깊은 객체를 매번 스프레드로 복사하기 번거로우면 Immer 같은 라이브러리가 대신 해 준다.

### 3-3. 다음에 볼 키워드

- `useEffect` — 상태가 바뀐 뒤 실행할 일(서버 요청·타이머), 의존성 배열
- 제어 컴포넌트 — `<input value={text} onChange={(e) => setText(e.target.value)} />`로 입력값을 상태에 묶기
- `useReducer` — 상태 갱신 규칙이 여러 갈래일 때 `switch`로 모으기
- `useContext` — 부모→자식→손자로 `setMode`를 계속 내려보내지 않고 트리 어디서든 꺼내 쓰기
- `React.StrictMode`에서 개발 중 컴포넌트가 두 번 호출되는 이유

## 실습 파일

- `KDT_2026/2026_React/src/example/day02/exam2.jsx` — 전역변수·지역변수·상태변수 비교 버튼 세 개, `useState` 선언 형식, 배열 상태와 스프레드 복사, 주소값 비유 주석
- `KDT_2026/2026_React/src/example/day02/p117_120/useState.jsx` — `mode` 상태로 `FrontComp`·`BackComp`를 골라 그리는 `Component3`, `if`로 JSX 변수 채우기
- `KDT_2026/2026_React/src/example/day02/p117_120/FrontComp.jsx` — `props.onSetMode("front")`로 부모 상태 변경
- `KDT_2026/2026_React/src/example/day02/p117_120/BackComp.jsx` — `{ setMode }` 구조 분해로 받아 `setMode("back")` 호출
- `KDT_2026/2026_React/src/main.jsx` — `Component3`를 렌더링하도록 진입점 변경

## 관련 노트

[[React MOC]] · [[React day02 컴포넌트 분리와 콜백 props]] · [[React day02 useEffect와 fetch로 서버 CRUD]] · [[React day02 객체 배열과 map 렌더링]] · [[KDT_2026 학습 지도]]
