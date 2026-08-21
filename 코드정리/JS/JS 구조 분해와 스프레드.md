---
출처: Claude 분석
작성일: 2026-08-21
tags: [코드정리]
---

# JS 구조 분해와 스프레드

> 상위: [[JS 함수]]

전부 ※에 가깝다. AI 코드·리액트 코드에서 가장 빈번하게 보이는 문법이다.

## 구조 분해 — 꺼내면서 이름 붙이기

```javascript
const { title, price } = product;
const { title: name } = product;
const { stock = 0 } = product;

const [first, second] = list;
const [head, ...rest] = list;
```

- 객체에서 같은 이름의 속성을 바로 변수로 뽑는다. `product.title`을 반복해서 쓰는 대신 첫 줄에서 한 번에 푼다
- `title: name`은 다른 이름으로 받기, `= 0`은 없을 때 기본값이다
- 배열은 순서대로 풀린다. `...rest`는 나머지 전부를 배열로 받는다
- 함수 매개변수에서도 된다: `function show({ title, price }) { }` — 객체를 통째로 받아 필요한 것만 푼다. AI가 옵션 객체를 받을 때 항상 이 모양이다

## 스프레드 — 펼치기

```javascript
const copy = [...list];
const merged = [...a, ...b];
const added = [...list, newItem];

const copiedObj = { ...obj };
const updated = { ...post, title: "새 제목" };
```

- `...`이 배열·객체를 그 자리에 펼친다. 복사·병합·추가가 전부 한 줄이다
- `{ ...post, title: "새 제목" }`은 **원본은 그대로 두고 title만 바뀐 새 객체**를 만든다 — 불변 업데이트라 부르고, 리액트 상태 변경의 표준형이다
- 얕은 복사라는 한계가 있다: 안에 든 객체·배열은 여전히 같은 주소를 본다. 중첩까지 복사하려면 `structuredClone(obj)`

## 관용구 모음

```javascript
const max = Math.max(...nums);
function log(...args) { console.log(...args); }
const unique = [...new Set(list)];
```

- 배열을 개별 인수로 펼쳐 넘기기(`Math.max`는 배열을 직접 못 받는다)
- `[...new Set(list)]`는 중복 제거 한 줄 관용구다 — Set으로 걸러 다시 배열로
