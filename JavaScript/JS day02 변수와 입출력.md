---
출처: Claude 분석
원본: KDT_2026/2026_FE/day02, day03/day02, Note/JSNote
작성일: 2026-08-10
tags: [학습, javascript]
---

# JS day02 — 변수와 입출력

> 실습 파일: `day02/exam/exam1.js`, `day02/pracitce/Practice1~2.js`, `day03/day02`(2일차 노트), `Note/JSNote`
> 허브: [[JavaScript MOC]] · 다음: [[JS day03 자료형과 연산자]]

## 1. 배운 내용

### 1-1. 웹 3대 요소

| | 역할 |
| --- | --- |
| HTML | 하이퍼텍스트 마크업 언어. 웹 문서의 **뼈대** |
| CSS | 웹 문서 **꾸미기** |
| JS | 웹 문서 **동적 기능**. 프로그래밍 언어 |

HTML 안에 CSS와 JS가 포함되어 함께 렌더링됩니다.

**라이브러리·프레임워크 지도**

| 분류 | 이름 |
| --- | --- |
| 프론트엔드 | React, Angular, Vue, jQuery |
| 백엔드 | Node.js (2009년 이후) |
| 앱 | React Native |
| 웹 + 앱 | React Native Web |
| 소프트웨어 | NW.js |

### 1-2. 데이터 관련 3용어

| 용어 | 의미 |
| --- | --- |
| 데이터(자료) | 사실이나 값을 그대로 나타낸 객관적 자료 |
| 리터럴 | 코드에 직접 표현한 값 그 자체 (`'A'`, `3`) |
| 자료형 | 자료들을 분류하는 방법 |

### 1-3. 변수와 상수

```javascript
let 변수;              // 초기값 없이 선언
let 변수2 = 10;        // 초기값과 함께
const 상수 = 20;       // 수정 불가
```

| | 목적 |
| --- | --- |
| 변수 | 재사용성, 가독성 |
| 상수 | 절댓값, 협업 |

### 1-4. 출력 함수

```javascript
console.log(출력값);                                    // 개발자도구 Console 탭
alert("메시지");                                        // 브라우저 상단 팝업
document.querySelector("선택자").innerHTML = "HTML";     // HTML 요소를 동적 변경
```

세 번째가 JS day11 DOM 조작 의 예고편입니다.

### 1-5. 입력 함수

```javascript
let result = confirm("메시지");
// 확인 → true, 취소 → false

let result2 = prompt("메시지");
// 확인 → 입력한 문자열 (아무것도 안 넣으면 "")
// 취소 → null
```

**`prompt`는 항상 문자열을 반환합니다.** 숫자로 쓰려면 `Number()` 변환이 필요합니다.

### 1-6. HTML과 JS 연결 — exam1.html

```html
<body>
  <p style="text-decoration: underline; color: chocolate">HI</p>

  <script>
    // alert("HI");        ← 인라인 스크립트
  </script>

  <script src="exam1.js"></script>   <!-- 외부 파일, </body> 직전 -->
</body>
```

`index.html` 을 허브로 두고 각 실습 파일로 링크해두면 편합니다. 파일이 많아질수록 이런 진입점이 유용합니다.

```html
<a href="exam1.html">exam1 이동</a> <br />
<a href="Practice1.html">연습1 이동</a>
```

## 2. 추가로 알면 좋은 활용법

### 2-1. `var`를 쓰지 않는 이유

```javascript
for (var i = 0; i < 3; i++) { }
console.log(i);   // 3  ← 반복문 밖에서도 살아있음 (함수 스코프)

for (let j = 0; j < 3; j++) { }
console.log(j);   // ReferenceError ← 블록 안에서만 (블록 스코프)
```

**기본은 `const`, 재할당이 필요할 때만 `let`.** `var`는 쓰지 않습니다.

`const`도 배열·객체의 **내부 수정은 가능**합니다.
```javascript
const arr = [1, 2];
arr.push(3);       // OK — 참조는 그대로
arr = [1, 2, 3];   // TypeError — 재할당 불가
```

Java의 `final`과 완전히 같은 성질입니다. → Java day08 접근제한자와 static

### 2-2. `prompt`의 결과는 문자열입니다

```javascript
let age = prompt("나이를 입력하세요");   // "20" (문자열!)
console.log(age + 1);       // "201"  ← 문자열 연결
console.log(Number(age) + 1);  // 21   ← 정답
```

`+`가 문자열 연결과 덧셈 두 가지 역할을 해서 생기는 대표적인 함정입니다.

### 2-3. `alert`·`prompt`·`confirm`은 실무에서 안 씁니다

세 함수 모두 **브라우저를 멈춰 세웁니다**(동기 블로킹). 사용자 경험이 나쁘고 디자인도 못 바꿉니다.

```html
<input id="nameInput" />
<button id="submitBtn">확인</button>
<dialog id="modal">...</dialog>
```

실무에서는 `<input>`으로 받고 `<dialog>` 또는 커스텀 모달로 보여줍니다. 학습 단계에서는 빠르게 확인할 수 있어 유용합니다.

### 2-4. `console`의 다른 메소드

```javascript
console.log()     // 일반
console.table(배열)  // 표 형태 — 객체 배열 볼 때 매우 유용
console.error()   // 빨간색
console.warn()    // 노란색
console.dir(dom)  // DOM을 객체 트리로
console.time("t"); console.timeEnd("t");   // 실행 시간 측정
```

`console.table`은 JS 과제 LevelUP과 게시판 의 회원·상품 배열을 볼 때 특히 좋습니다.

### 2-5. `<script>` 위치와 `defer`

```html
<head>
  <script src="app.js"></script>   <!-- body보다 먼저 실행 → querySelector가 null -->
</head>
```

```html
<script src="app.js" defer></script>   <!-- 권장: HTML 파싱 후 실행 -->
```

`</body>` 직전에 두신 게 올바른 방식이고, `defer`는 `<head>`에 두면서 같은 효과를 냅니다.

## 3. 더 나아가 알면 좋은 것

### 3-1. 템플릿 리터럴

```javascript
let age = 19;
console.log("나이는 " + age + "살");    // 문자열 연결
console.log(`나이는 ${age}살`);          // 템플릿 리터럴 (권장)
```

여러 줄도 그대로 쓸 수 있습니다.
```javascript
const html = `
  <tr>
    <td>${no}</td>
    <td>${title}</td>
  </tr>
`;
```

JS day14 게시판 CRUD 에서 테이블 행을 만들 때 이 방식이 핵심입니다.

### 3-2. `"use strict";`

파일 맨 위에 넣으면 실수를 에러로 잡아줍니다.

```javascript
"use strict";
a = 10;   // ReferenceError (선언 없는 대입 금지)
```

JS day10 함수 의 전역 오염 문제를 원천 차단합니다. ES 모듈(`type="module"`)은 자동으로 strict 모드입니다.

### 3-3. 개발자 도구 활용

| 탭 | 용도 |
| --- | --- |
| Console | `console.log` 확인, 즉석 코드 실행 |
| Elements | DOM 구조·적용된 CSS 확인 |
| Sources | 브레이크포인트 디버깅 |
| Application | localStorage·sessionStorage·쿠키 확인 |
| Network | 요청·응답 확인 |

JS day13 웹 스토리지와 인터벌 에서 Application 탭을 본격적으로 씁니다.

## 실습 파일

- `2026_FE/Note/JSNote`
- `2026_FE/day02/index.html`, `day02/exam/exam1.html`, `exam1.js`, `exam2.html`
- `2026_FE/day02/pracitce/Practice1.js`, `Practice2.js`
- `2026_FE/day03/day02` (2일차 정리 노트)

## 관련 노트

[[JavaScript MOC]] · [[JS day03 자료형과 연산자]] · HTML day02 문서 구조와 미디어 · Java day01 자바 구조와 자료형
