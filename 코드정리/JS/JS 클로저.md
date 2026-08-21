---
출처: Claude 분석
작성일: 2026-08-21
tags: [코드정리]
---

# JS 클로저

> 상위: [[JS 함수]]

전부 ※. "함수가 자기가 태어난 곳의 변수를 계속 기억하는" 성질이다.

## 기본형 — 상태를 품은 함수

```javascript
function makeCounter() {
    let count = 0;
    return function () {
        count++;
        return count;
    };
}

const counter = makeCounter();
counter();
counter();
counter();
```

- 안쪽 함수가 바깥의 `count`를 붙잡고 있어서, makeCounter가 끝난 뒤에도 count가 살아 있다. 부를 때마다 1, 2, 3으로 늘어난다
- `makeCounter()`를 두 번 부르면 서로 **독립된 count**를 가진 카운터 둘이 생긴다 — 클래스 없이 인스턴스를 만든 셈이다

## 왜 쓰나 — 상태 은닉

```javascript
function createStore() {
    let data = [];
    return {
        add(item) { data.push(item); },
        getAll() { return [...data]; },
    };
}

const store = createStore();
store.add("글1");
store.getAll();
```

- 바깥에서 `data`에 직접 접근할 방법이 **없다**. add·getAll이라는 관문으로만 만진다 — 자바에서 private 필드 + 메소드로 하던 캡슐화를 함수로 한 것이다
- `getAll`이 복사본을 돌려주는 것까지 하면 방어적 복사도 같다

## 함정 — 반복문과 var

```javascript
for (var i = 0; i < 3; i++) {
    setTimeout(() => console.log(i), 100);
}

for (let i = 0; i < 3; i++) {
    setTimeout(() => console.log(i), 100);
}
```

- var 버전은 3, 3, 3이 찍힌다. 콜백 셋이 **같은 i 하나**를 붙잡아서다
- let은 반복마다 새 i가 생겨 0, 1, 2가 찍힌다 — "반복문에서는 let"의 진짜 이유가 클로저다
- 리액트의 커스텀 훅이 상태를 기억하는 원리도 이 클로저 위에 서 있다
