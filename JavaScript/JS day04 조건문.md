---
출처: Claude 분석
원본: KDT_2026/2026_FE/day04, Note/day/day04
작성일: 2026-08-10
tags: [javascript, day04, 조건문, 분기]
---

# JS day04 — 조건문

> 실습 파일: `day04/exam/exam1.js`, `exam2.js`, `Note/day/day04`, `day04/practice/tictackto.js`
> 허브: [[JavaScript MOC]] · 이전: [[JS day03 자료형과 연산자]] · 다음: [[JS day05 반복문]]

## 1. 배운 내용

### 1-1. 조건문이 필요한 이유

정리하면 이렇습니다.
> 연산·함수의 결과는 항상 1개다. 분기/조건문은 상황에 따라 흐름을 분기·제어한다.
> 비가 오면 우산을 챙기고 아니면 우산을 두고 간다.

### 1-2. if의 6가지 패턴 — Note/day/day04

형태는 6가지로 나뉩니다. 형태만이 아니라 **의미 차이**까지 붙여 정리합니다.

**① 실행문 1개 — 중괄호 생략**
```javascript
if (10 > 3) console.log("10은 3보다 크다.");
```

**② 실행문 2개 이상 — 중괄호 필수**
```javascript
if (10 > 3) {
  console.log("10은 3보다 크다.");
  console.log("두 번째 줄");
}
```

**③ if ~ else — 참/거짓 양분**
```javascript
if (10 > 5) { ... } else { ... }
```

**④ if ~ else if ~ else — 다수 조건 중 하나만**
```javascript
if (10 > 3) console.log("A");
else if (10 < 11) console.log("B");   // ③이 참이면 여기는 검사조차 안 함
else console.log("나머지");
```

**⑤ if / if / if — 조건마다 각각 판단**
```javascript
if (10 > 3) console.log("A");    // 셋 다 참이면
if (10 < 11) console.log("B");   // 셋 다 출력됨
if (10 > 1) console.log("C");
```

**⑥ 중첩 if — 조건을 단계적으로 좁힘**
```javascript
if (10 > 3) {
  if (10 < 11) { ... }
}
```

**④ vs ⑤의 차이가 핵심입니다.** ④는 배타적(하나만), ⑤는 독립적(여러 개 가능)입니다. `exam1.js` 주석에 이걸 정확히 구분해 두셨습니다.

### 1-3. 삼항 연산자

```javascript
조건 ? 참 : 거짓

점수 >= 90 ? "합격" : "불합격"

// 중첩
조건1 ? 참1 : 조건2 ? 참2 : 조건3 ? 참3 : 거짓
```

`true`/`false`를 **다른 값으로 표현하고 싶을 때** 씁니다.

### 1-4. tictackto — 조건 분기 실전

`day04/practice/tictackto.html/js`는 조건문을 실제 게임 로직에 적용한 과제입니다. 승패 판정은 결국 8가지 조건(가로 3 + 세로 3 + 대각선 2)의 나열입니다.

## 2. 추가로 알면 좋은 활용법

### 2-1. 조기 반환(Early Return)으로 중첩 줄이기

```javascript
// 중첩이 깊어지는 코드
function 처리(user) {
  if (user) {
    if (user.age >= 18) {
      if (user.active) {
        console.log("통과");
      }
    }
  }
}

// 조기 반환 — 훨씬 읽기 쉬움
function 처리(user) {
  if (!user) return;
  if (user.age < 18) return;
  if (!user.active) return;
  console.log("통과");
}
```

**들여쓰기가 3단을 넘어가면 조기 반환을 검토**하세요. [[Java day08 접근제한자와 static]] 의 `setName`에서 쓴 `return;`과 같은 기법입니다.

### 2-2. switch로 바꾸면 좋은 경우

```javascript
if (ch === 1) { ... }
else if (ch === 2) { ... }
else if (ch === 3) { ... }
```

**같은 변수를 여러 값과 비교**할 때는 switch가 의도를 더 잘 드러냅니다.

```javascript
switch (ch) {
  case 1: ...; break;
  case 2: ...; break;
  default: ...;
}
```

**주의**: JS의 `switch`는 `===`로 비교합니다. `"1"`과 `1`은 다릅니다. [[JS day14 게시판 CRUD]] 의 쿼리스트링 문제와 연결됩니다.

`case`를 나열해 묶을 수도 있습니다.
```javascript
switch (grade) {
  case "A":
  case "B":
    console.log("합격");   // A와 B 둘 다 여기로
    break;
}
```

Java의 switch도 문법이 같습니다. → [[Java day04 제어문과 배열]]

### 2-3. 객체를 이용한 분기 (switch 대체)

조건이 많아지면 객체 매핑이 깔끔합니다.

```javascript
const 등급메시지 = {
  A: "A등급 입니다.",
  B: "B등급 입니다.",
  C: "C등급 입니다.",
};
console.log(등급메시지[grade] ?? "재시험입니다.");
```

`if`가 10개 넘어가면 이 방식을 검토해보세요. → [[JS day07 객체]]

### 2-4. 논리 연산자의 단축 평가

```javascript
if (user && user.name) { }     // user가 falsy면 뒤를 검사조차 안 함
const name = user && user.name;  // user가 없으면 user 자체를 반환

user?.name;                    // 옵셔널 체이닝 (더 명확)
```

순서를 바꾸면 터집니다.
```javascript
if (user.name && user) { }     // user가 null이면 TypeError
```

Java의 `&&`도 동일하게 단축 평가합니다. → [[Java day03 연산자]]

### 2-5. 조건을 변수로 빼기

```javascript
if (user.age >= 19 && user.verified && !user.banned) { }

// 이름을 붙이면 의도가 드러납니다
const 이용가능 = user.age >= 19 && user.verified && !user.banned;
if (이용가능) { }
```

## 3. 더 나아가 알면 좋은 것

### 3-1. 유효성 검사 패턴

폼 입력 검증은 조건문의 대표적 실전입니다.

```javascript
function validate(title, content, pwd) {
  if (!title.trim())  return "제목을 입력하세요.";
  if (!content.trim()) return "내용을 입력하세요.";
  if (pwd.length < 4) return "비밀번호는 4자 이상이어야 합니다.";
  return null;   // 통과
}

const error = validate(title, content, pwd);
if (error) { alert(error); return; }
```

에러 메시지를 반환값으로 돌려주면 **검증 로직과 화면 처리가 분리**됩니다. [[JS day14 게시판 CRUD]] 의 `write.js`에 넣으면 좋습니다.

Java의 setter 유효성 검사와 같은 목적입니다. → [[Java day08 접근제한자와 static]]

### 3-2. `if`를 아예 없애는 방법들

```javascript
// 기본값 매개변수
function greet(name = "익명") { }

// 옵셔널 체이닝 + nullish
const city = user?.address?.city ?? "미입력";

// 배열 메소드
const 성인 = users.filter(u => u.age >= 19);   // for + if 대체
```

### 3-3. HTML 폼과의 연결

day04에서 HTML `<input>` 타입도 배우셨습니다([[HTML day04 폼과 테이블]]). 브라우저 기본 검증을 쓰면 JS 조건문이 줄어듭니다.

```html
<input type="text" required minlength="2" />
<input type="number" min="0" max="100" />
<input type="email" required />
```

단, **클라이언트 검증은 우회 가능**하므로 서버 검증이 반드시 필요합니다.

## 실습 파일

- `2026_FE/Note/day/day04`
- `2026_FE/day04/exam/exam1.js`, `exam2.js`, `exam1.html`, `exam2.html`
- `2026_FE/day04/practice/practice1.js`, `practice3.js`, `tictackto.js`

## 관련 노트

[[JavaScript MOC]] · [[JS day03 자료형과 연산자]] · [[JS day05 반복문]] · [[HTML day04 폼과 테이블]] · [[Java day04 제어문과 배열]]
