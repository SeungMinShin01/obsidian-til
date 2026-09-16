---
출처: Claude 분석
원본: KDT_2026/2026_React/src/example/day03/pracitce
작성일: 2026-09-15
tags: [학습, react]
---

# React day03 — 전화번호부 실습: 배열 상태 추가와 삭제

> 실습 파일: `src/example/day03/pracitce/practice.jsx` · `src/example/day03/pracitce/index.css` · `src/main.jsx`
> 허브: [[React MOC]] · 이전: [[React day03 폼 제출과 입력값 읽기]] · 다음: [[React day04 React Router 도입과 라우트 정의]]

day03 실습은 앞 예제 두 개를 한 화면에 합친 작은 전화번호부다. `exam2.jsx`의 비제어 폼(`event.target.name.value`)으로 성명·연락처·나이를 받고, 그 값을 객체로 묶어 **배열 상태**에 쌓은 뒤 `map`으로 목록을 찍고 삭제 버튼으로 지운다. 서버 없이 상태만으로 돌아가는 CRUD의 축소판이라, day02에서 따로따로 정리한 "배열 상태는 주소값이 바뀌어야 다시 그려진다"와 "폼은 값을 올려보내고 부모가 상태를 맡는다"가 실제로 어떻게 맞물리는지 확인하기 좋은 예제다.

## 1. 배운 내용

### 1-1. 폼 컴포넌트 — 입력 세 개를 콜백 하나로 올려보내기

```jsx
function WriteForm(props) {
  return (
    <>
      <form
        onSubmit={(e) => {
          e.preventDefault();
          let name = e.target.name.value;
          let number = e.target.number.value;
          let age = e.target.age.value;
          props.writeAction(name, number, age);
        }}
      >
        <input className="inputBox" type="text" name="name" placeholder="성명" />
        <input className="inputBox" type="text" name="number" placeholder="연락처 (예: 010-1234-5678)" />
        <input className="inputBox" type="text" name="age" placeholder="나이" />
        <input className="submitBtn" type="submit" name="submit" value="등록" />
      </form>
    </>
  );
}
```

앞 노트의 `WriteForm`과 같은 골격이다. 달라진 점은 입력이 셋으로 늘었다는 것뿐이고, 읽는 방법은 그대로 `e.target.<name>.value`다. `<input name="number">`는 `e.target.number`, `<input name="age">`는 `e.target.age`로 닿는다. `name` 속성이 곧 접근 키이므로 세 입력창 모두 `name`을 빠뜨리지 않는 것이 이 방식의 전제다.

`placeholder`는 값이 비어 있을 때 회색으로 보이는 안내 문구다. `value`가 아니므로 입력값에 영향을 주지 않고, 비제어 입력창에 "무엇을 넣으라"는 힌트를 주는 용도로 딱 맞다. 제출 버튼도 `<input type="submit">`이라 클릭하거나 입력창에서 엔터를 치면 폼의 `submit` 이벤트가 난다.

`WriteForm`은 여전히 상태가 없다. 값을 읽어 `props.writeAction(name, number, age)`로 올려보내는 데서 역할이 끝난다.

### 1-2. 배열 상태에 객체를 추가하기 — 스프레드와 단축 프로퍼티

```jsx
export default function Component3(props) {
  const [array, setArray] = useState([]);

  return (
    <>
      <h2>전화번호부</h2>
      <WriteForm
        writeAction={(name, number, age) => {
          if (name !== "" && number !== "" && age !== "") {
            setArray([...array, { name, number, age }]);
          } else {
            alert("빈값");
          }
        }}
      ></WriteForm>
      …
```

부모 `Component3`가 상태를 든다. 초기값은 빈 배열 `[]`이고, 폼에서 값이 올라오면 검증 뒤 한 줄로 추가한다.

| 조각 | 뜻 |
| --- | --- |
| `[...array, …]` | 기존 배열을 펼쳐 **새 배열**을 만든다. `push`처럼 원래 배열을 고치는 게 아니라 주소값이 다른 배열이 생기므로 React가 변경을 감지해 다시 그린다 |
| `{ name, number, age }` | `{ name: name, number: number, age: age }`의 **단축 프로퍼티** 표기. 변수 이름을 그대로 키로 쓴다 |
| `if (… !== "")` | 셋 중 하나라도 비어 있으면 `alert`로 막고 상태를 건드리지 않는다 |

day02 `useState` 노트에서 정리한 "배열은 주소값이 바뀌어야 재렌더링"이 여기서 그대로 쓰인다. `setArray(array)`처럼 같은 배열을 다시 넘기면 React는 바뀐 게 없다고 판단해 화면을 갱신하지 않는다. 그래서 추가는 항상 `[...array, 새항목]` 꼴이다.

객체를 배열에 넣는 순간부터 항목 하나는 `{ name, number, age }`라는 구조를 갖는다. 나중에 서버와 주고받는 JSON도 이 모양이 되므로, 폼에서 받은 낱개 값을 어디서 객체로 묶을지 정하는 자리가 이 콜백이다.

### 1-3. `map`으로 목록 그리기와 파생값

```jsx
{array.map((m, index) => {
  return (
    <>
      <div>
        <span>성명 : {m.name}</span>
        <span>연락처 : {m.number}</span>
        <span>나이 : {m.age}</span>
        <button onClick={() => { 삭제함수(index); }}>삭제</button>
      </div>
    </>
  );
})}
<div>총 인원 : {array.length}</div>
```

`array.map((m, index) => …)`의 두 번째 매개변수 `index`가 이번 예제의 핵심이다. 항목마다 자기 순번을 받아 두었다가, 삭제 버튼의 `onClick`에서 그 순번을 넘긴다. 버튼에 `onClick={() => 삭제함수(index)}`처럼 **화살표로 감싸는** 이유는 day01에서 정리한 대로다 — `onClick={삭제함수(index)}`라고 쓰면 렌더링 시점에 바로 실행돼 버린다.

`총 인원 : {array.length}`는 상태를 따로 두지 않고 배열 길이에서 바로 뽑는다. 추가·삭제로 `array`가 바뀌면 컴포넌트가 다시 호출되고, 그때 `array.length`도 새로 계산되니 항상 맞는 값이 보인다. 이렇게 **기존 상태에서 계산할 수 있는 값은 상태로 만들지 않는다**는 것이 React 상태 설계의 기본 원칙이다. 인원 수를 별도 `useState`로 들면 추가·삭제마다 둘을 같이 맞춰야 해서 어긋날 여지가 생긴다.

### 1-4. 삭제 — 원소를 빼고 새 배열로 갈아끼우기

```jsx
const 삭제함수 = (index) => {
  array.splice(index, 1);
  setArray([...array]);
};
```

`splice(index, 1)`은 `index` 자리에서 원소 하나를 잘라낸다. 그 뒤 `setArray([...array])`로 **펼쳐서 새 배열**을 넘기는 것이 포인트다. `splice`만 하고 끝내면 배열 내용은 줄었지만 주소값이 그대로라 화면이 바뀌지 않는다. 스프레드 한 번이 "주소값 갱신"을 담당한다.

정리하면 이 예제의 상태 변경은 두 군데 모두 같은 규칙을 따른다.

| 동작 | 코드 | 새 배열이 되는 지점 |
| --- | --- | --- |
| 추가 | `setArray([...array, { name, number, age }])` | 스프레드 + 새 항목 |
| 삭제 | `array.splice(index, 1); setArray([...array])` | 스프레드 |

### 1-5. 폼 전용 CSS를 컴포넌트에서 `import`

```jsx
import "./index.css";
```

```css
.inputBox {
  padding: 5px;
  margin-right: 15px;
  border-radius: 8px;
  border: solid 1px #858585;
}

.submitBtn {
  padding: 5px;
  border-radius: 5px;
  border: solid 1px #858585;
  background-color: #f0f0f0;
  width: 40px;
}
```

앞 노트에서 `src/index.css`를 `../../index.css`로 끌어왔다면, 이번엔 실습 폴더 안에 `index.css`를 두고 `./index.css`로 가져온다. 파일 위치가 다를 뿐 동작은 같다 — `import`한 CSS는 번들에 합쳐져 **전역**으로 적용되고, JSX에서는 `className="inputBox"`로 붙인다. 폴더마다 같은 이름의 `index.css`가 있어도 `import` 경로가 다르므로 Vite는 각각 다른 파일로 읽는다. 다만 클래스 이름은 전역이라 다른 폴더의 CSS와 이름이 겹치면 나중에 읽힌 규칙이 덮어쓴다는 점은 기억해 둘 만하다.

### 1-6. main.jsx 진입점 교체

```jsx
import Component3 from "./example/day03/pracitce/practice.jsx";
create.render(<Component3></Component3>);
```

같은 루트에 마지막 `render`만 남는다는 규칙은 앞 노트들과 같다. day03 폴더 안의 하위 폴더까지 경로를 적어 주면 된다.

## 2. 추가로 알면 좋은 활용법

### 2-1. 삭제는 `filter`로 새 배열을 만드는 쪽이 더 단순하다

```jsx
const 삭제함수 = (index) => {
  setArray(array.filter((_, i) => i !== index));
};
```

`filter`는 조건에 맞는 원소만 모아 **처음부터 새 배열**을 돌려준다. 원래 배열은 손대지 않으므로 스프레드로 다시 복사할 필요가 없고, "상태는 직접 바꾸지 않는다(불변성)"는 React 관례에 그대로 맞는다. 원본 배열을 먼저 고치고 복사하는 방식도 결과는 같지만, 이 관례를 기준으로 코드를 읽는 사람이 많으니 새 배열을 만드는 쪽으로 습관을 들이는 편이 안전하다.

### 2-2. 목록 항목에 `key` 주기

```jsx
{array.map((m, index) => (
  <div key={index}>…</div>
))}
```

`map`으로 찍은 목록에는 각 항목의 최상위 요소에 `key`를 붙인다. day01·day02에서 정리한 대로 React가 "어느 항목이 그대로고 어느 항목이 빠졌는지"를 판단하는 기준이다. 항목이 프래그먼트(`<>…</>`)로 감싸여 있으면 `key`를 줄 자리가 없으니 `<div key={…}>`처럼 실제 요소를 최상위로 두거나, `<Fragment key={…}>`로 긴 표기를 쓴다.

`key`로 인덱스를 쓰는 것은 항목이 뒤에만 붙고 앞에서 삭제되지 않을 때는 문제가 없지만, 이번처럼 중간 삭제가 있으면 삭제 뒤 남은 항목들의 인덱스가 당겨져 React가 항목을 잘못 짝지을 수 있다. 항목마다 고유값을 두는 쪽이 정석이다.

```jsx
setArray([...array, { id: Date.now(), name, number, age }]);
// 삭제: array.filter((m) => m.id !== id)
```

`Date.now()`나 `crypto.randomUUID()`로 만든 `id`를 항목에 넣고, 삭제도 인덱스가 아니라 `id`로 하면 `key`와 삭제 기준이 하나로 통일된다. 서버가 있으면 이 자리는 DB의 PK가 된다.

### 2-3. 제출 뒤 입력창 비우기

```jsx
onSubmit={(e) => {
  e.preventDefault();
  …
  props.writeAction(name, number, age);
  e.target.reset();
}}
```

비제어 폼은 상태가 없어서 `setName('')`으로 비울 수 없다. `<form>`의 `reset()`을 부르면 세 입력창이 모두 초기 상태로 돌아가 다음 사람을 바로 입력할 수 있다. 다만 검증에 실패한 경우(`alert("빈값")`)까지 지워지면 곤란하니, 콜백이 성공 여부를 돌려주게 하고 성공했을 때만 `reset()`하는 식으로 다듬을 수 있다.

### 2-4. 빈 값 검증을 한 줄로

```jsx
if ([name, number, age].every((v) => v.trim() !== "")) { … }
```

입력이 셋을 넘어가면 `&&` 사슬이 길어진다. 배열에 담아 `every`로 돌리면 개수가 늘어도 조건문은 그대로다. `trim()`을 같이 쓰면 공백만 넣은 경우도 걸러진다. 브라우저 단계에서 먼저 막고 싶으면 `<input required>`를 붙인다.

### 2-5. 연락처·나이 형식 검사

```jsx
<input type="tel" name="number" pattern="01[0-9]-\d{3,4}-\d{4}" placeholder="010-1234-5678" />
<input type="number" name="age" min="0" max="150" />
```

`placeholder`는 안내일 뿐 형식을 강제하지 않는다. `pattern`·`type="number"`·`min`/`max` 같은 HTML 검증 속성을 쓰면 `submit` 전에 브라우저가 걸러 준다. 비제어 폼과 잘 맞는 검증 방식이다.

## 3. 더 나아가 알면 좋은 것

### 3-1. `useReducer` — 추가·삭제·수정이 한곳에 모인다

```jsx
function reducer(state, action) {
  switch (action.type) {
    case "add":    return [...state, action.item];
    case "remove": return state.filter((m) => m.id !== action.id);
    default:       return state;
  }
}
const [array, dispatch] = useReducer(reducer, []);
// dispatch({ type: "add", item: { id, name, number, age } });
```

지금은 추가·삭제 두 가지라 `setArray` 두 줄로 충분하지만, 수정·정렬·전체 삭제가 붙기 시작하면 상태를 바꾸는 규칙이 컴포넌트 곳곳에 흩어진다. `useReducer`는 "어떤 동작(`action`)이 들어오면 상태를 어떻게 바꾼다"를 함수 하나에 모아 둔다. 불변성 규칙(항상 새 배열 반환)도 한곳에서만 지키면 된다.

### 3-2. 새로고침해도 남게 — localStorage와 서버

이 전화번호부는 새로고침하면 비어 있는 `[]`로 돌아간다. 브라우저에 남기려면 `useEffect`로 `array`가 바뀔 때마다 `localStorage.setItem("phonebook", JSON.stringify(array))`하고, 초기값을 `useState(() => JSON.parse(localStorage.getItem("phonebook")) ?? [])`로 읽어 온다. 여러 사람이 같이 써야 한다면 day02 `CategoryManager`처럼 서버에 POST·DELETE를 보내고 응답으로 목록을 다시 받는 구조로 바뀐다 — 지금의 `setArray` 두 줄이 그때 `fetch` 호출로 치환되는 자리다.

### 3-3. 목록 항목을 컴포넌트로 빼기

`map` 안의 `<div>` 덩어리를 `<Contact m={m} onRemove={…} />` 같은 부품으로 분리하면 `Component3`는 상태와 흐름만 남고, 항목의 생김새는 따로 관리된다. 항목 수가 많아지면 `React.memo`로 바뀌지 않은 항목의 재렌더링을 건너뛸 수도 있다.

### 3-4. 다음에 볼 키워드

- `filter` · `map` · `every` — 배열을 바꾸지 않고 새 배열을 돌려주는 메소드들
- `key`와 고유 `id` (`crypto.randomUUID()`)
- `useReducer` · 불변성(immutability) · Immer
- `localStorage` + `useEffect`로 상태 유지
- 목록 항목 컴포넌트 분리 · `React.memo`

## 실습 파일

- `KDT_2026/2026_React/src/example/day03/pracitce/practice.jsx` — 비제어 `WriteForm`(입력 3개 + `placeholder`)이 콜백으로 값을 올리고, 부모 `Component3`가 배열 상태에 `{ name, number, age }` 추가·`splice` + 스프레드로 삭제·`map`으로 목록·`array.length`로 인원 표시
- `KDT_2026/2026_React/src/example/day03/pracitce/index.css` — `.inputBox`·`.submitBtn` 폼 스타일, 컴포넌트에서 `./index.css`로 `import`
- `KDT_2026/2026_React/src/main.jsx` — day03 `Component3`로 진입점 교체

## 관련 노트

[[React MOC]] · [[React day03 폼 제출과 입력값 읽기]] · [[React day04 React Router 도입과 라우트 정의]] · [[React day02 useState와 상태 갱신]] · [[React day02 객체 배열과 map 렌더링]] · [[KDT_2026 학습 지도]]
