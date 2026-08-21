---
출처: Claude 분석
작성일: 2026-08-21
tags: [코드정리]
---

# JS 기본 문법

> 상위: [[JS]]
> 세부: [[JS 형변환과 비교]] · [[JS 문자열 메소드]]

## 변수 — let · const

```javascript
let count = 0;
const MAX = 100;
const list = [];
list.push("a");
```

- `let`은 재할당 가능, `const`는 재할당 금지다. 기본은 const로 쓰고 바뀌는 값만 let으로 연다
- const 배열·객체에 push·속성 변경은 된다 — 참조(주소)만 고정이고 내용은 아니다(자바의 final과 같다)
- 옛날 문법 `var`는 스코프가 함수 단위라 사고가 잦다. 새 코드에선 쓰지 않는다

## 출력과 입력

```javascript
console.log("값", a, b);
alert("알림");
const name = prompt("이름?");
const yes = confirm("삭제할까요?");
```

- `console.log`는 쉼표로 여러 값을 한 번에 찍는다. 디버깅의 기본이다
- `prompt`는 **항상 문자열**을 돌려준다. 숫자로 쓰려면 `Number()` 변환이 필요하다
- `confirm`은 확인/취소를 boolean으로 준다(삭제 확인 관용)

## 자료형

```javascript
typeof 3.14;
typeof "abc";
typeof true;
typeof undefined;
typeof null;
```

- 숫자는 정수·실수 구분 없이 전부 number 하나다(자바와 다른 점)
- `undefined`는 값을 아직 안 넣은 것, `null`은 "없음"을 일부러 넣은 것이다
- `typeof null`이 "object"로 나오는 건 유명한 역사적 버그다. null 검사는 `x === null`로 한다
- 동적 타입이라 변수에 아무 타입이나 들어간다. 타입 오류가 실행 중에야 드러나므로 `===`와 검증이 더 중요해진다

## 연산자

```javascript
7 % 3;
2 ** 10;
a === b;
a !== b;
cond ? x : y;
```

- 산술·대입·증감·비교·논리·삼항은 자바와 거의 같다. `**`(거듭제곱)이 추가로 있다
- 비교는 **항상 `===`, `!==`**를 쓴다(`==`는 타입을 멋대로 바꿔 비교한다 — 세부 노트 참고)
- 문자열은 `===`로 값 비교가 된다(자바의 equals 자리). `+`는 한쪽이 문자열이면 이어붙이기가 된다

## 조건문과 반복문

```javascript
if (score >= 90) { } else if (score >= 80) { } else { }

for (let i = 0; i < 10; i++) { }
while (n > 0) { }

for (const item of list) { }
for (const key in obj) { }
```

- if·for·while·break·continue는 자바와 같은 모양이다
- `for...of`는 배열의 **값**을 하나씩(자바의 향상된 for), `for...in`은 객체의 **키**를 하나씩 돈다 — of/in을 바꿔 쓰면 인덱스 문자열이 나와서 당황하게 된다
- switch도 자바와 같고 break 생략 시 흘러내림도 같다
