---
출처: Claude 분석
작성일: 2026-08-21
tags: [코드정리]
---

# JS 함수

> 상위: [[JS]]
> 세부: [[JS 구조 분해와 스프레드]] · [[JS 클로저]] · [[JS this와 화살표 함수]]

## 세 가지 선언 방법

```javascript
function add(x, y) {
    return x + y;
}

const sub = function (x, y) {
    return x - y;
};

const mul = (x, y) => x * y;
```

- 선언식·표현식·화살표 셋 다 "부르면 실행되는 코드 덩어리"다. 화살표가 요즘 기본형이다
- 화살표에서 본문이 식 하나면 `{}`와 `return`을 생략한다(암시적 반환). `x => x * 2`처럼 매개변수가 1개면 괄호도 생략 가능
- 선언식은 선언 전에 불러도 되지만(호이스팅) 표현식·화살표는 선언 뒤에만 부를 수 있다
- 자바와 달리 오버로딩이 없다 — 같은 이름으로 다시 정의하면 **덮어쓴다**

## 매개변수

```javascript
function greet(name = "손님") {
    return `안녕하세요, ${name}`;
}

function sum(...nums) {
    let total = 0;
    for (const n of nums) total += n;
    return total;
}
```

- `= 기본값`은 인수를 안 넘겼을 때의 값이다(자바에는 없는 문법 — 오버로딩 대신 이걸 쓴다)
- `...nums`(rest)는 개수 제한 없이 받아 배열로 묶는다(자바의 가변 인자)
- 인수를 적게 넘기면 나머지는 undefined, 많이 넘기면 조용히 버려진다 — 에러가 안 나므로 주의

## 콜백 — 함수를 값으로 넘기기

```javascript
function repeat(n, action) {
    for (let i = 0; i < n; i++) action(i);
}

repeat(3, i => console.log(i));

button.addEventListener("click", () => save());
setInterval(() => tick(), 1000);
```

- 함수를 변수에 담고, 인수로 넘기고, 반환할 수 있다(일급 객체). 넘겨진 함수가 콜백이다
- "무엇을 할지"를 나중에·바깥에서 정하게 하는 장치다 — 자바에서 인터페이스 구현체를 갈아끼우던 그 자리를 JS는 함수 하나로 한다
- 이벤트 등록·타이머·배열 메소드(map/filter)가 전부 콜백을 받는 구조다

## 스코프

```javascript
const g = "전역";

function outer() {
    const local = "지역";
    if (true) {
        const block = "블록";
    }
}
```

- let·const는 **블록(`{}`) 단위** 스코프다. if·for 안에서 선언한 건 밖에서 안 보인다
- 안쪽에서 바깥 변수는 보인다(반대는 불가). 같은 이름이면 가까운 쪽이 이긴다
