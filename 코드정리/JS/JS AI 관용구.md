---
출처: Claude 분석
작성일: 2026-08-21
tags: [코드정리]
---

# JS AI 관용구

> 상위: [[JS]]

전부 ※. AI가 생성하는 JS에 유독 자주 나오는 함축 표현 해독표다.

## ?. — 옵셔널 체이닝

```javascript
const city = user?.address?.city;
const first = list?.[0];
onSave?.();
```

- `A?.B`는 "A가 null·undefined면 터지지 말고 undefined로 끝내라"다. null 검사 if 사다리가 사라진다
- 대괄호 접근(`?.[0]`)과 함수 호출(`?.()`)에도 붙는다 — 마지막 줄은 "onSave가 있으면 불러라"

## ?? — 널 병합

```javascript
const name = input ?? "이름없음";
const list = JSON.parse(raw ?? "[]");
count ??= 0;
```

- `A ?? B`는 A가 **null·undefined일 때만** B다. `||`와 달리 0이나 빈 문자열은 그대로 살린다(0이 유효한 값일 때 이 차이가 버그를 가른다)
- `??=`는 "없으면 채워 넣기"다

## || 와 && — 값을 고르는 논리 연산

```javascript
const title = input || "(제목 없음)";
isLoggedIn && showMenu();
```

- JS의 `||`는 boolean이 아니라 **값**을 돌려준다: 앞이 falsy면 뒤의 값. 기본값 채우기의 고전형이다
- `조건 && 실행()`은 "조건일 때만 실행"의 축약이다. 리액트 JSX의 조건부 렌더링(`{isOpen && <Modal/>}`)이 이 문법이다

## 화살표 + 암시적 반환

```javascript
const double = x => x * 2;
const toItem = b => ({ no: b.no, title: b.title });
list.sort((a, b) => a.no - b.no);
```

- 본문이 식 하나면 return 없이 그 값이 반환된다
- **객체를 암시적 반환할 땐 괄호로 감싼다** — `b => { no: ... }`는 객체가 아니라 함수 본문 블록으로 해석돼 undefined가 나온다. `({ ... })`가 정답

## 구조 분해 매개변수

```javascript
function createPost({ title, content, pwd = "" }) { }

list.map(({ no, title }) => `${no}: ${title}`);
```

- 객체를 받아 그 자리에서 풀어버린다. 매개변수가 많아질 때 순서 대신 이름으로 넘기는 방식이고, AI가 옵션 인수를 받을 때 거의 항상 이 모양이다

## 불변 업데이트

```javascript
const updated = { ...post, title: "새 제목" };
const added = [...list, newItem];
const removed = list.filter(b => b.no !== no);
const changed = list.map(b => b.no === no ? { ...b, title } : b);
```

- 원본을 고치지 않고 **바뀐 새 것**을 만든다. 삭제는 filter, 수정은 map+삼항, 추가는 스프레드가 각각의 관용형이다
- push·splice로 원본을 바꾸는 코드와 결과는 같지만, 리액트 상태 관리는 이 방식을 강제한다 — AI가 이유 없이 이렇게 쓰는 게 아니라 그 습관이다

## 짧은 판정·수집

```javascript
const exists = list.some(b => b.no === no);
const total = cart.reduce((s, i) => s + i.price, 0);
const names = [...new Set(list.map(b => b.author))];
```

- some 존재 확인, reduce 합계, Set 왕복 중복 제거 — for문 3~6줄씩의 압축이다

## async 관용구

```javascript
async function init() {
    try {
        const [books, members] = await Promise.all([fetchBooks(), fetchMembers()]);
    } catch (e) {
        console.error(e);
    }
}
```

- `Promise.all([...])`은 여러 요청을 **동시에** 보내고 전부 끝나길 기다린다. 순서대로 await 두 번 하는 것보다 빠르다
- 결과 배열을 구조 분해로 바로 나눠 받는 것까지가 세트다
