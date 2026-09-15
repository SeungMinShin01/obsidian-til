---
출처: Claude 분석
원본: KDT_2026/2026_React/src/example/day03/exam2.jsx
작성일: 2026-09-15
tags: [학습, react]
---

# React day03 — 폼 제출과 입력값 읽기

> 실습 파일: `src/example/day03/exam2.jsx` · `src/main.jsx`
> 허브: [[React MOC]] · 이전: [[React day03 JSX 스타일링과 이미지 경로]] · 다음: [[React day03 전화번호부 실습 배열 상태 추가와 삭제]]

day02의 `CategoryManager`에서는 입력값을 전부 `useState`에 묶는 제어 컴포넌트로 폼을 만들었다. 이번 예제는 그 반대편을 한 번 짚는다 — 상태 없이 `<form onSubmit>`의 **이벤트 객체에서 직접 값을 꺼내는** 방식이다. 같은 파일 안에 `<input>` 세 개를 나란히 놓고 "value를 어떻게 주느냐"에 따라 입력창이 어떻게 달라지는지도 비교한다. 작은 예제지만 React가 폼을 다루는 두 갈래(제어·비제어)와 상태의 역할이 한눈에 드러나서, 나중에 어느 쪽을 고를지 판단할 때 기준이 되는 내용이다.

## 1. 배운 내용

### 1-1. `<form onSubmit>` — submit 버튼이 누르는 곳은 폼이다

```jsx
function WriteForm(props) {
  return (
    <form
      onSubmit={(event) => {
        event.preventDefault();
        let gubun = event.target.gubun.value;
        let title = event.target.title.value;
        props.writeAction(gubun, title);
      }}
    >
      <select name="gubun">
        <option value="front">프론트엔드</option>
        <option value="back">백엔드</option>
      </select>
      <input type="text" name="title" />
      <input type="submit" value="추가" />
    </form>
  );
}
```

흐름을 순서대로 정리하면 이렇다.

| 순서 | 일어나는 일 |
| --- | --- |
| ① | `type="submit"` 버튼을 클릭하거나 입력창에서 엔터를 치면 **폼의** `submit` 이벤트가 난다 (버튼의 `onClick`이 아니다) |
| ② | `onSubmit`에 넘긴 콜백이 이벤트 객체 `event`를 매개변수로 받는다 |
| ③ | `event.preventDefault()`로 브라우저의 기본 동작(폼 데이터를 붙여 GET으로 페이지 이동)을 막는다 |
| ④ | `event.target`은 이벤트가 난 마크업, 즉 `<form>` 자신이다 |
| ⑤ | `event.target.name속성값`으로 폼 안의 특정 요소에 닿고, `.value`로 입력값을 읽는다 |
| ⑥ | 읽은 값을 부모가 내려 준 콜백 `props.writeAction(gubun, title)`에 실어 올려보낸다 |

핵심은 ④·⑤다. `<form>` 요소는 자기 안의 컨트롤을 **`name` 속성 이름으로 프로퍼티처럼** 노출한다. `event.target.gubun`은 `<select name="gubun">`이고, `event.target.title`은 `<input name="title">`이다. `document.querySelector`를 쓰지 않고도 폼 안을 뒤질 수 있는 이유가 여기 있다. 그래서 이 방식에서는 **`name` 속성이 필수**다 — 빠뜨리면 `undefined.value`에서 멈춘다.

`preventDefault`는 day02에서 `<a>`의 이동을 막을 때, 그리고 `CategoryManager`의 폼에서 쓴 것과 같은 메소드다. CSR에서는 페이지가 다시 로드되는 순간 상태가 전부 사라지므로, 폼을 다룰 때는 이 한 줄이 습관처럼 첫 줄에 들어간다.

### 1-2. 폼은 값을 올려보내고, 검증과 상태는 부모가 맡는다

```jsx
export default function Component2(props) {
  const [message, setMessage] = useState("품질 검증 진행 중");
  return (
    <>
      <WriteForm
        writeAction={(gu, ti) => {
          if (gu !== "" && ti != "") {
            let frmValue = `검증 완료 : ${gu} ${ti}`;
            setMessage(frmValue);
          } else {
            alert("빈 값");
          }
        }}
      />
      <pre> {message}</pre>
    </>
  );
}
```

`WriteForm`은 상태를 하나도 갖지 않는다. 입력을 받아서 두 값을 부모에게 넘기는 것까지가 역할이고, 그 값을 어떻게 할지는 부모 `Component2`가 정한다 — 빈 값이면 `alert`, 아니면 `message` 상태를 바꿔 `<pre>`가 다시 그려진다. day02에서 정리한 콜백 props(데이터는 내려가고 이벤트는 올라간다)가 폼에도 그대로 적용된 모양이다.

이렇게 나누면 `WriteForm`은 어느 부모 밑에 붙여도 되는 재사용 부품이 된다. 검증 규칙이 바뀌어도 폼 컴포넌트는 손댈 일이 없다.

### 1-3. `<input>` 세 개 — value를 주는 방식에 따라 달라지는 것

```jsx
let 입력받은값 = "유재석";
const [입력받은값2, set입력받은값2] = useState("유재석2");

<input />
<input value={입력받은값} />
<input
  value={입력받은값2}
  onChange={(e) => { set입력받은값2(e.target.value); }}
/>
```

| 입력창 | 동작 | 이유 |
| --- | --- | --- |
| `<input />` | 자유롭게 타이핑된다. React는 값에 관여하지 않는다 | **비제어 컴포넌트** — DOM이 값을 스스로 들고 있다 |
| `<input value={일반변수} />` | 초기값은 보이지만 **타이핑해도 바뀌지 않는다** | `value`가 고정돼 React가 매번 같은 값으로 되돌린다. 일반 변수는 바꿔도 재렌더링이 없으니 화면이 못 따라온다 |
| `<input value={상태} onChange={…} />` | 정상적으로 타이핑된다 | **제어 컴포넌트** — 글자가 바뀔 때마다 `onChange`가 상태를 갱신하고, 재렌더링으로 새 `value`가 내려온다 |

두 번째 줄이 이 예제의 요점이다. `value`를 주는 순간 React는 "이 입력창의 값은 내가 정한다"고 선언한 셈이라, 값을 바꿀 길(`onChange` + 상태)까지 같이 주지 않으면 입력창이 잠긴다. 콘솔에도 `value`만 있고 `onChange`가 없다는 경고가 뜬다. 초기값만 주고 이후엔 자유롭게 두고 싶다면 `value`가 아니라 `defaultValue`를 쓴다.

정리하면 React에서 입력창은 두 부류로 나뉜다.

- **제어(controlled)**: `value` + `onChange` + `useState`. React 상태가 값의 원본이다. day02 `CategoryManager`가 이 방식
- **비제어(uncontrolled)**: `value`를 주지 않는다. DOM이 값의 원본이고, 필요할 때 `event.target.name.value`나 `ref`로 읽는다. 이번 `WriteForm`이 이 방식

### 1-4. main.jsx 진입점 교체

```jsx
import Component2 from "./example/day03/exam2.jsx";
create.render(<Component2></Component2>);
```

앞 노트와 같은 방식이다. `App`을 그리는 줄 뒤에 day03 컴포넌트를 `render`하면 같은 루트에 마지막 `render`만 남는다.

## 2. 추가로 알면 좋은 활용법

### 2-1. `FormData`로 한 번에 읽기

```jsx
onSubmit={(e) => {
  e.preventDefault();
  const data = Object.fromEntries(new FormData(e.target));
  props.writeAction(data.gubun, data.title);
}}
```

`name`이 붙은 컨트롤이 많아지면 `event.target.xxx.value`를 줄줄이 쓰는 대신 `FormData`로 한 번에 객체를 만든다. 키가 곧 `name`이라, 1-1에서 `name`이 필수라는 점은 그대로다. 이 객체는 `JSON.stringify`해서 바로 POST 본문으로 보내기에도 맞다.

### 2-2. 어느 쪽을 고를까 — 제어 vs 비제어

| 상황 | 어울리는 쪽 |
| --- | --- |
| 타이핑 중 실시간 검증·글자 수 표시·조건부 버튼 활성화 | 제어 (상태가 있어야 매 글자마다 반응할 수 있다) |
| 제출 뒤 입력창 비우기(`setName('')`) | 제어 |
| 제출할 때만 값이 필요한 단순 폼, 파일 입력(`<input type="file">`) | 비제어 (상태 없이 가볍다) |
| 검색창처럼 입력값을 다른 컴포넌트가 같이 봐야 할 때 | 제어 |

한 폼 안에서 섞어 써도 되지만, 같은 입력창을 처음엔 비제어로 두다가 나중에 `value`를 주면 React가 "비제어 → 제어로 바뀌었다"는 경고를 낸다. 처음부터 한쪽으로 정해 두는 편이 안전하다.

### 2-3. 제출 후 폼 비우기 — 비제어일 때

```jsx
e.target.reset();
```

비제어 폼은 상태가 없으니 `setXXX('')`로 비울 수 없다. 대신 `<form>` 요소의 `reset()`을 부르면 모든 컨트롤이 초기값으로 돌아간다.

### 2-4. 빈 값 검증은 `trim()`까지

`gu !== ""` 같은 비교는 공백만 입력한 경우를 통과시킨다. `ti.trim() === ""`로 앞뒤 공백을 잘라 확인하거나, `<input required>`를 붙여 브라우저 단계에서 먼저 막아 두면 `alert`까지 가는 일이 줄어든다.

## 3. 더 나아가 알면 좋은 것

### 3-1. `useRef`로 비제어 입력 읽기

```jsx
const titleRef = useRef(null);
<input ref={titleRef} />
// 제출 시: titleRef.current.value
```

`event.target.name.value`는 폼 안에서만 통한다. 폼 밖의 입력창이나 포커스 이동(`titleRef.current.focus()`)까지 다루려면 `useRef`가 정석이다. 비제어 컴포넌트의 "DOM이 값을 든다"는 성질을 React 방식으로 붙잡는 훅이다.

### 3-2. 폼 라이브러리 — React Hook Form

입력이 열 개를 넘어가면 제어 컴포넌트는 상태와 `onChange`가 그만큼 늘고, 비제어는 검증 코드가 흩어진다. React Hook Form은 `register("title", { required: true })` 한 줄로 비제어 입력을 등록하고 검증·에러 메시지를 한곳에서 관리한다. 1-3에서 본 두 부류의 장점을 합친 도구로, Zod 같은 스키마 검증 라이브러리와 함께 쓰인다.

### 3-3. 다음에 볼 키워드

- `defaultValue` · `defaultChecked`
- `FormData` · `Object.fromEntries`
- `useRef` · `forwardRef`
- React Hook Form · Zod
- `<input type="file">`과 `multipart/form-data`

## 실습 파일

- `KDT_2026/2026_React/src/example/day03/exam2.jsx` — `WriteForm`의 `<form onSubmit>`·`preventDefault`·`event.target.name.value`, 부모 `Component2`의 콜백 검증과 `message` 상태, `<input>` 세 개(비제어 · 고정 `value` · 제어) 비교
- `KDT_2026/2026_React/src/main.jsx` — day03 `Component2`로 진입점 교체

## 관련 노트

[[React MOC]] · [[React day03 JSX 스타일링과 이미지 경로]] · [[React day03 전화번호부 실습 배열 상태 추가와 삭제]] · [[React day02 useEffect와 fetch로 서버 CRUD]] · [[React day02 컴포넌트 분리와 콜백 props]] · [[KDT_2026 학습 지도]]
