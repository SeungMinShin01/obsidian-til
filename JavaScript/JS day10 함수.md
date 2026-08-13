---
출처: Claude 분석
원본: KDT_2026/2026_FE/day10, Note/day/day10
작성일: 2026-08-10
tags: [학습, javascript]
---

# JS day10 — 함수

> 실습 파일: `day10/exam/exam1.js`, `Note/day/day10`, `day10/pracitce/practice0~2.js`
> 허브: [[JavaScript MOC]] · 이전: [[JS day07 객체]] · 다음: [[JS day11 DOM 조작]]

## 1. 배운 내용

### 1-1. 함수란

`exam1.js` 주석의 어원 설명이 재미있습니다.
> 함(상자) 수(숫자/크기) — 상자 안에 들어오는 수·코드

**목적 3가지**
1. 재사용
2. 매개변수에 따른 서로 다른 결과물
3. 지역변수 (스코프 격리)

**종류 2가지**
1. 미리 만들어진 함수 (라이브러리) — `console.log`, `alert`, `prompt`, `document.querySelector`
2. 내가 만든 함수 (정의 함수)

### 1-2. 형태와 용어

```javascript
function 함수명(매개변수1, 매개변수2) {
    실행코드;
    return 반환값;
}
```

용어부터 정리합니다.

| 용어 | 의미 |
| --- | --- |
| **매개변수**(Parameter) | 인자값을 저장하는 변수. **지역변수 특징** |
| **인수/인자값**(Argument) | 함수에게 전달하는 값 |
| **return** | 함수를 종료하며 반환하는 값. 생략 가능 |

```
함수명(3, 10)  →  함수명(X, Y)
   인수            매개변수
```

**함수 호출 2가지 경로**
```javascript
함수명(인수, 인수);                                   // JS에서
```
```html
<button onclick="함수명('인수')">클릭</button>        <!-- HTML 이벤트 속성에서 -->
```

**변수와 함수의 대칭 구조**

| | 선언 | 호출 |
| --- | --- | --- |
| 변수 | `let sum;` | `sum` |
| 함수 | `function sum() { }` | `sum()` |

### 1-3. 믹서기 비유

```javascript
function 믹서기함수(과일) {
    return 과일 + "주스";
}
let 컵1 = 믹서기함수("사과");   // "사과주스"
let 컵2 = 믹서기함수("포도");   // "포도주스"
```

같은 기계에 다른 재료를 넣으면 다른 결과가 나옵니다. **매개변수의 존재 이유**를 한 번에 설명하는 좋은 비유입니다.

### 1-4. 4가지 조합

| | 매개변수 없음 | 매개변수 있음 |
| --- | --- | --- |
| **반환값 없음** | `func2()` | `fun3(x)` — `console.log()` 계열 |
| **반환값 있음** | `fun5()` | `fun4(x)` — `prompt()` 계열 |

Java의 메소드 4조합과 정확히 대응합니다. → [[Java day07 메소드와 미니프로젝트]]

## 2. 추가로 알면 좋은 활용법

### 2-1. 전역 변수 오염 피하기

함수 안에서 변수를 만들 때 가장 조심할 부분입니다.

```javascript
function 수학공식함수(x, y) {
    a = x + y;      // let/const 없음 → 암묵적 전역 변수
    return a;
}
```

선언 키워드 없이 대입하면 **전역 객체(window)의 프로퍼티**가 됩니다. 다른 함수에서 같은 이름을 쓰면 서로 값을 덮어써서, 원인을 찾기 매우 어려운 버그가 됩니다.

```javascript
function 수학공식함수(x, y) {
    const a = x + y;   // 지역 변수
    return a;
}
```

**예방책**: 파일 맨 위에 `"use strict";`를 넣으면 **에러로 잡힙니다.**
```javascript
"use strict";
a = 10;   // ReferenceError: a is not defined
```

### 2-2. 스코프 3단계

```javascript
const 전역 = 1;                    // 전역 스코프

function f() {
    const 함수 = 2;                // 함수 스코프
    if (true) {
        const 블록 = 3;            // 블록 스코프 (let/const만)
    }
    // console.log(블록);          // ReferenceError
}
```

**안쪽에서 바깥은 볼 수 있지만, 바깥에서 안쪽은 못 봅니다.**

`var`는 블록 스코프가 없어서 `if` 밖에서도 보입니다. 그래서 안 씁니다. → [[JS day02 변수와 입출력]]

### 2-3. 호이스팅

```javascript
sayHi();                          // 정상 동작
function sayHi() { }              // 함수 선언문은 통째로 끌어올려짐

sayHello();                       // TypeError: sayHello is not a function
const sayHello = function() { };  // 함수 표현식은 안 됨
```

HTML의 `onclick="함수명()"`이 동작하는 것도 함수 선언문의 호이스팅 덕분입니다.

`let`/`const`는 선언 전에 접근하면 `ReferenceError`가 납니다(Temporal Dead Zone). `var`는 `undefined`가 나와서 더 위험합니다.

### 2-4. 화살표 함수

```javascript
const add = (x, y) => x + y;      // 중괄호·return 생략
const square = x => x * x;        // 매개변수 1개면 괄호도 생략
const greet = () => { console.log("hi"); };
const makeObj = () => ({ a: 1 }); // 객체 반환은 괄호로 감싸야 함
```

**`this`가 다릅니다.** 객체의 메소드에는 쓰지 마세요. 반대로 `map`, `filter`, `addEventListener` 콜백에는 훨씬 편합니다. → [[JS day07 객체]]

## 3. 더 나아가 알면 좋은 것

### 3-1. 클로저 — JS의 캡슐화

함수가 자기가 태어난 스코프의 변수를 계속 기억하는 성질입니다.

```javascript
function 카운터만들기() {
  let count = 0;                    // 외부에서 접근 불가
  return {
    증가: () => ++count,
    현재값: () => count
  };
}
const c = 카운터만들기();
c.증가();  c.증가();
c.현재값();   // 2
// c.count   // undefined — 직접 접근 불가
```

`count`는 함수 밖에서 절대 건드릴 수 없습니다. Java의 `private` + getter/setter와 목적이 같습니다. → [[Java day08 접근제한자와 static]]

[[JS day13 웹 스토리지와 인터벌]] 의 타이머에서 `time`, `timeInter`를 전역에 둔 부분을 클로저로 감싸면 안전해집니다.

### 3-2. 고차 함수

함수를 인자로 받거나 함수를 반환하는 함수입니다.

```javascript
[1,2,3].map(n => n * 2);              // map은 함수를 받는 고차 함수
setInterval(시계함수, 1000);           // setInterval도 마찬가지

function 곱하기만들기(n) {              // 함수를 반환
  return x => x * n;
}
const 두배 = 곱하기만들기(2);
두배(5);   // 10
```

### 3-3. 순수 함수

```javascript
// 순수 — 같은 입력 → 항상 같은 출력, 외부에 영향 없음
function add(x, y) { return x + y; }

// 비순수 — 외부 상태를 바꿈
let total = 0;
function addToTotal(n) { total += n; }
```

선언 없이 전역 변수를 건드리는 함수가 비순수 함수의 대표적인 예입니다. **순수 함수는 테스트하기 쉽고 예측 가능합니다.**

### 3-4. 함수 분리 기준

```javascript
// 하나의 함수가 너무 많은 일을 함
function 등록함수() {
  const title = document.querySelector("#title").value;   // 1. DOM 읽기
  if (!title) { alert("입력하세요"); return; }             // 2. 검증
  const list = JSON.parse(localStorage.getItem("list"));  // 3. 저장소 읽기
  list.push({ title });                                   // 4. 가공
  localStorage.setItem("list", JSON.stringify(list));     // 5. 저장
  location.href = "list.html";                            // 6. 이동
}
```

**한 함수는 한 가지 일만** 하도록 쪼개면 재사용과 테스트가 쉬워집니다. [[JS day14 게시판 CRUD]] 에서 `common.js`로 분리하는 게 이 원칙의 적용입니다.

## 실습 파일

- `2026_FE/Note/day/day10`
- `2026_FE/day10/exam/exam1.js`, `exam1.html`
- `2026_FE/day10/pracitce/practice0.js`, `practice1.js`

## 관련 노트

[[JavaScript MOC]] · [[JS day07 객체]] · [[JS day11 DOM 조작]] · [[CSS day10 카메라 강의 사이트]] · [[Java day07 메소드와 미니프로젝트]]
