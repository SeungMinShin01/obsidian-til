---
출처: Claude 분석
원본: KDT_2026/2026_React/src/example/day02
작성일: 2026-09-14
tags: [학습, react]
---

# React day02 — 객체 배열과 map 렌더링

> 실습 파일: `src/example/day02/pracitce1.jsx`
> 허브: [[React MOC]] · 이전: [[React day01 컴포넌트와 렌더링]] · 다음: [[React day02 컴포넌트 분리와 콜백 props]]

React 둘째 날은 실습 하나로 채워졌다. "서버에서 받아왔다고 가정한 데이터"를 배열로 두고, 그 배열을 `map`으로 돌려 `Profile` 컴포넌트를 여러 개 찍는 과제다. day01의 1-9(배열 props를 반복문으로 목록 찍기)와 2-5(`for` 대신 `map`)를 합쳐서 **문자열 배열이 아니라 객체 배열**로, **`<li>`가 아니라 컴포넌트**로 한 단계 올린 것이다.

## 1. 배운 내용

### 1-1. 과제 — Practice1과 Profile 컴포넌트

```jsx
// src/example/day02/pracitce1.jsx
// REACT Practice1 : Practice1 과 Profile 컴포넌트를 구현하여 그림과 같이 완성하시오.
// AXIOS 이용하여 서버로 부터 받은 데이터/자료 가정
export default function Practice1(props) {
  const data = [
    { name: "Hedy Lamarr", imageUrl: "https://i.pravatar.cc/150?img=47" },
    { name: "Grace Hopper", imageUrl: "https://i.pravatar.cc/150?img=48" },
    { name: "Ada Lovelace", imageUrl: "https://i.pravatar.cc/150?img=49" },
    { name: "Margaret Hamilton", imageUrl: "https://i.pravatar.cc/150?img=50" },
  ];
  return (
    <>
      {data.map((i) => {
        return (
          <>
            <Profile name={i.name} imageUrl={i.imageUrl} />
          </>
        );
      })}
    </>
  );
}

function Profile(props) {
  return (
    <>
      <h3>{props.name}</h3>
      <img src={props.imageUrl} />
    </>
  );
}
```

구조는 day01 exam2와 같다 — `export default`로 내보내는 대표 컴포넌트 하나(`Practice1`)와, 같은 파일 안에서만 쓰는 부품 하나(`Profile`). 달라진 건 부품을 **데이터 개수만큼 반복해서** 찍는다는 점이다.

| 역할 | 컴포넌트 | 하는 일 |
| --- | --- | --- |
| 부모 | `Practice1` | 데이터 배열을 갖고 있고, 항목마다 `<Profile>`을 만들어 props로 값을 내려준다 |
| 자식 | `Profile` | `name`·`imageUrl` 두 props를 받아 `<h3>`와 `<img>`로 그린다. 데이터가 어디서 왔는지는 모른다 |

### 1-2. 객체 배열 — "한 줄 = 객체 하나"

day01 exam5의 `frontData`는 `["HTML5", "CSS3", …]`처럼 문자열 배열이었다. 오늘 `data`는 **객체 배열**이다. 한 사람에 대한 정보가 이름과 사진 주소 두 개라서, 값 하나로는 못 담고 `{ name, imageUrl }` 객체로 묶은 것이다.

| 형태 | 예 | 항목 하나가 |
| --- | --- | --- |
| 문자열 배열 | `["Java", "Oracle"]` | 값 1개 |
| 객체 배열 | `[{ name: "…", imageUrl: "…" }, …]` | 값 여러 개를 가진 레코드 1개 |

JS day07 객체에서 본 "키-값 묶음"이 배열 안에 여러 개 들어 있는 모양이다. 실제 서버 응답(JSON)이 거의 항상 이 모양이라, 주석에 적힌 대로 나중에 AXIOS로 받은 데이터가 `data` 자리에 그대로 들어온다고 보면 된다. 게시글 목록·회원 목록·상품 목록 전부 같은 꼴이다.

### 1-3. map으로 컴포넌트 목록 찍기

```jsx
{data.map((i) => {
  return (
    <>
      <Profile name={i.name} imageUrl={i.imageUrl} />
    </>
  );
})}
```

핵심 한 줄이다. 흐름을 풀면 이렇다.

| 단계 | 코드 | 의미 |
| --- | --- | --- |
| ① JS 구역 열기 | `{ … }` | JSX 안에서 JS 표현식을 쓰는 중괄호 |
| ② 배열 변환 | `data.map((i) => …)` | 객체 4개짜리 배열 → JSX 4개짜리 배열 |
| ③ 항목 → 컴포넌트 | `<Profile name={i.name} imageUrl={i.imageUrl} />` | 콜백의 `i`가 객체 하나. 그 프로퍼티를 props로 꺼내 넘긴다 |
| ④ 배열 펼침 | 결과 배열이 `{}` 자리에 놓임 | day01 1-9에서 `{liRows}`가 펼쳐지던 것과 같다 |

`map`은 원래 배열은 그대로 두고 **각 항목을 콜백의 반환값으로 바꾼 새 배열**을 돌려준다. 콜백이 JSX를 반환하니 결과는 "컴포넌트 배열"이고, React는 `{}` 안의 배열을 순서대로 그린다. day01에서 `for` + `push`로 만들던 `liRows`를 임시 변수 없이 `return` 안에서 바로 만든 셈이다.

콜백 매개변수 이름은 자유다. 여기서는 `i`를 썼지만, 이 `i`는 **인덱스가 아니라 객체 하나**라는 점을 분명히 해 둔다. `map`의 콜백은 `(항목, 인덱스)` 순서로 받으므로 인덱스가 필요하면 두 번째 자리를 쓴다.

### 1-4. 하드코딩 두 줄 → 반복 한 줄

파일에는 `map` 위에 `<Profile name={data[0].name} … />`, `<Profile name={data[1].name} … />`처럼 **인덱스로 하나씩 꺼내 쓴 줄**도 남아 있고, 아래에는 `map` 부분을 통째로 주석으로 복사해 둔 블록도 있다. 수업이 진행된 순서가 그대로 보인다.

| 단계 | 방식 | 한계 |
| --- | --- | --- |
| 1 | `data[0]`, `data[1]` 직접 지정 | 항목이 4개면 4줄, 100개면 100줄. 데이터가 늘면 코드를 고쳐야 한다 |
| 2 | `data.map(…)` | 데이터가 몇 개든 한 줄. 서버 응답 길이를 몰라도 된다 |

"데이터가 바뀌면 화면이 따라온다"는 React의 방향(day01 3-2 선언형)은 이 반복 한 줄에서부터 시작한다. 목록을 그리는 코드는 앞으로 거의 전부 이 모양이다.

### 1-5. Profile — props만 받는 순수 부품

```jsx
function Profile(props) {
  return (
    <>
      <h3>{props.name}</h3>
      <img src={props.imageUrl} />
    </>
  );
}
```

`Profile`은 데이터 배열을 모른다. 이름 하나, 주소 하나만 받아서 그린다. 이렇게 **자기 화면에 필요한 값만 props로 받는 부품**은 어디서든 재사용할 수 있다 — 회원 목록에서도, 검색 결과에서도 `<Profile name=… imageUrl=… />`만 쓰면 된다. day01 1-8의 "props는 부모가 넘기고 자식은 읽기만 한다"가 실전 형태로 나타난 것이다.

`<img src={props.imageUrl} />` — 속성값이 변수이므로 따옴표가 아니라 중괄호다. `src="props.imageUrl"`로 쓰면 그 글자 그대로가 주소가 되어 버린다. 그리고 JSX에서 `<img>`는 반드시 `/>`로 닫는다(day01 1-5).

## 2. 추가로 알면 좋은 활용법

### 2-1. key — 반복으로 찍는 컴포넌트마다 붙이기

day01 1-9에서 `<li key={i}>`를 썼듯, `map`으로 찍는 형제 요소에는 `key`가 있어야 한다. 없으면 콘솔에 경고가 뜨고, 항목이 추가·삭제될 때 React가 어느 것이 어느 것인지 놓쳐서 화면이 엉킬 수 있다.

```jsx
{data.map((person, idx) => (
  <Profile key={idx} name={person.name} imageUrl={person.imageUrl} />
))}
```

| 상황 | key로 쓸 것 |
| --- | --- |
| 서버 데이터에 `id`가 있다 | `key={person.id}` — 가장 안전 |
| 고정 배열, 순서가 안 바뀐다 | `key={idx}` (인덱스)로 충분 |
| 중간 삽입·삭제·정렬이 있다 | 인덱스 금지 — 고유값이 필요 |

`key`는 컴포넌트 태그에 직접 붙이고, `<>…</>`로 한 번 더 감싼 경우에는 그 감싸는 쪽에 붙여야 한다. 프래그먼트에 key를 주려면 짧은 `<>` 대신 `<Fragment key={…}>`를 써야 하므로, 항목 하나에 요소가 하나뿐이면 굳이 프래그먼트로 감싸지 않는 편이 단순하다.

### 2-2. 콜백을 줄이는 두 가지 표기

```jsx
// ① 중괄호 + return
{data.map((i) => { return <Profile name={i.name} imageUrl={i.imageUrl} />; })}

// ② 괄호로 바로 반환 (JSX 한 덩어리면 이쪽이 흔하다)
{data.map((i) => (
  <Profile name={i.name} imageUrl={i.imageUrl} />
))}

// ③ 콜백에서 구조 분해
{data.map(({ name, imageUrl }) => (
  <Profile name={name} imageUrl={imageUrl} />
))}
```

화살표 함수에서 본문이 표현식 하나면 `{ return … }`을 `( … )`로 줄일 수 있다(JS day10 함수). JSX가 여러 줄이면 소괄호로 감싸야 줄바꿈 뒤의 `return` 문제 없이 통째로 반환된다. ③은 day01 1-8의 구조 분해를 콜백 매개변수 자리에서 한 것이다.

### 2-3. 객체를 통째로 넘기기 vs 펼쳐 넘기기

```jsx
// 프로퍼티를 하나씩 넘김 — 오늘 방식
<Profile name={i.name} imageUrl={i.imageUrl} />

// 객체를 통째로 넘김
<Profile person={i} />          // 자식에서 props.person.name

// 스프레드로 펼쳐 넘김 — 키 이름이 props 이름과 같을 때
<Profile {...i} />              // name={i.name} imageUrl={i.imageUrl} 와 같다
```

| 방식 | 장점 | 주의 |
| --- | --- | --- |
| 하나씩 | 자식이 뭘 받는지 태그만 봐도 보인다 | 필드가 많으면 길어진다 |
| 통째로 | 짧다 | 자식이 객체 구조를 알아야 한다(결합이 생김) |
| 스프레드 | 짧고, 자식 props 이름은 그대로 | 필요 없는 키까지 다 넘어간다 |

배우는 단계에서는 하나씩 넘기는 오늘 방식이 가장 읽기 쉽다. 스프레드는 키 이름이 딱 맞을 때만 쓴다.

### 2-4. 목록 컴포넌트를 한 겹 더 나누기

```jsx
export default function Practice1() {
  const data = [ /* … */ ];
  return <ProfileList people={data} />;
}

function ProfileList({ people }) {
  return people.map((p) => <Profile key={p.name} {...p} />);
}

function Profile({ name, imageUrl }) {
  return (
    <>
      <h3>{name}</h3>
      <img src={imageUrl} alt={name} />
    </>
  );
}
```

데이터를 갖는 컴포넌트(`Practice1`), 목록을 도는 컴포넌트(`ProfileList`), 항목 하나를 그리는 컴포넌트(`Profile`) 세 겹으로 나누면 각자의 책임이 한 줄로 설명된다. 파일이 커지기 시작하면 이 나눔이 읽기를 살린다. `<img>`에는 `alt`를 같이 넣어 두는 습관이 좋다 — 이미지가 안 뜰 때와 스크린리더에서 이름이 대신 나온다.

### 2-5. 빈 배열일 때

서버에서 받은 목록이 비어 있으면 `map`은 빈 배열을 돌려주고 화면에는 아무것도 안 뜬다. 오류는 아니지만 사용자는 "로딩 중인지, 정말 없는지" 알 수 없다. 이런 경우 조건부 렌더링을 앞에 둔다.

```jsx
{data.length === 0 ? <p>표시할 프로필이 없습니다.</p> : data.map(/* … */)}
```

삼항과 `&&`로 하는 조건부 렌더링은 다음 수업에서 정식으로 만난다.

## 3. 더 나아가 알면 좋은 것

### 3-1. AXIOS — "가정"이 실제가 되는 자리

주석의 "AXIOS 이용하여 서버로부터 받은 데이터/자료 가정"이 오늘의 방향 표시다. 지금은 `data`를 컴포넌트 안에 직접 적었지만, 실제로는 이렇게 바뀐다.

```jsx
import { useState, useEffect } from "react";
import axios from "axios";

export default function Practice1() {
  const [data, setData] = useState([]);           // 처음엔 빈 배열
  useEffect(() => {
    axios.get("/api/profiles").then((r) => setData(r.data));  // 받아오면 교체
  }, []);
  return data.map((p) => <Profile key={p.id} {...p} />);
}
```

`useState`로 목록을 상태로 두고, `useEffect` 안에서 서버에 요청해 응답으로 상태를 바꾸면 React가 다시 그린다. 오늘 짠 `map` 부분은 **그대로 남는다** — 데이터가 어디서 오든 "배열 → 컴포넌트 목록"으로 바꾸는 코드는 같기 때문이다. 여기가 오늘 실습을 하드코딩으로 먼저 해 두는 이유다.

### 3-2. 백엔드 쪽과 맞물리는 그림

Spring day04에서 만든 REST 컨트롤러가 `List<Dto>`를 JSON 배열로 내려주면, 그것이 바로 오늘의 `data` 모양이다. 백엔드의 `Dto` 필드 이름(`name`, `imageUrl`)이 프론트의 props 이름이 된다. 두 쪽의 필드 이름을 맞추는 일이 프론트·백 협업의 첫 번째 약속이다(평문 언급 — 구역 간 링크는 걸지 않는다).

### 3-3. 다음에 볼 키워드

- `useState` — 목록을 상태로 들고 추가·삭제하기, 그때 `key`가 왜 인덱스면 안 되는지
- 조건부 렌더링 — `&&`, 삼항, 빈 목록·로딩 표시
- `useEffect` + `axios` — 서버에서 목록 받아오기, 의존성 배열 `[]`
- `Fragment`에 `key` 주기, `React.memo`로 항목 컴포넌트 재렌더링 줄이기
- 리스트 항목 클릭 → 부모로 값 올리기(콜백 props)

## 실습 파일

- `KDT_2026/2026_React/src/example/day02/pracitce1.jsx` — 객체 배열을 `map`으로 돌려 `Profile` 컴포넌트 목록 렌더링, AXIOS 응답을 가정한 임시 데이터

## 관련 노트

[[React MOC]] · [[React day01 컴포넌트와 렌더링]] · [[React day02 컴포넌트 분리와 콜백 props]] · [[KDT_2026 학습 지도]]
