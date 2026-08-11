---
출처: Claude 분석
원본: KDT_2026/2026_FE/day03, Note/day/day03
작성일: 2026-08-10
tags: [javascript, day03, 자료형, 배열, 연산자]
---

# JS day03 — 자료형과 연산자

> 실습 파일: `day03/exam/exam1.js`, `exam2.js`, `Note/day/day03`, `day03/memo`
> 허브: [[JavaScript MOC]] · 이전: [[JS day02 변수와 입출력]] · 다음: [[JS day04 조건문]]

## 1. 배운 내용

### 1-1. 자료형 6종

```javascript
typeof 자료   // 해당 자료의 타입 반환
```

| 타입 | 표기 | 비고 |
| --- | --- | --- |
| 숫자 | `10`, `3.14` | 정수·실수 구분 없음. 전부 부동소수점 |
| 문자열 | `' '` `" "` `` ` ` `` | 백틱은 템플릿 리터럴 |
| 논리 | `true` / `false` | |
| undefined | | 값이 **할당되지 않은** 상태 (시스템이 준 것) |
| null | | 값이 **존재하지 않음**을 개발자가 명시 |
| 배열 | `[ ]` | `typeof`는 `"object"`가 나옴 |
| 객체 | `{ }` | → [[JS day07 객체]] |
| 함수 | `function(){}` | `typeof`는 `"function"` |

### 1-2. 문자열

세 가지 표기가 가능하고 백틱은 **템플릿 리터럴**입니다.

```javascript
let age = 19;
console.log(`나이는 ${age}살 입니다.`);   // ${} 안에 연산·변수·함수 호출 가능
```

**이스케이프(제어) 문자**: `\\` `\'` `\"` `` \` `` `\n` `\t`

**언어별 백슬래시 출력 비교**

| 언어 | 표기 |
| --- | --- |
| Python | `print("\\")` |
| Java | `System.out.println("\\");` |
| JS | `console.log("\\")` |
| HTML | `&#92;` |

**문자열 연결 3가지**
```javascript
console.log("안녕", "하세요");   // 쉼표 — console.log 전용, 공백 자동 삽입
console.log("안녕" + "하세요");  // + 연산자
console.log(`안녕 ${3}`);        // 템플릿 리터럴
```

`"안녕" + 3`처럼 문자열과 숫자를 더하면 **문자열이 됩니다.**

### 1-3. 배열

```javascript
let arr = [자료, 자료, 자료];
```

- **인덱스**는 0번부터 시작합니다
- 수정: `arr = [새배열]` 또는 `arr[index] = 새값`

| 메소드 | 역할 |
| --- | --- |
| `arr.push(값)` | 끝에 추가 |
| `arr.splice(index, 개수)` | 삭제 / 중간 삽입 |
| `arr.indexOf(값)` | 위치 반환, 없으면 `-1` |
| `arr.includes(값)` | 존재 여부 `true`/`false` |
| `arr.length` | 총 개수 |

Java 배열과의 결정적 차이는 **가변 길이**와 **타입 자유**입니다. → [[Java day04 제어문과 배열]]

### 1-4. 형변환

```javascript
Number(자료)       // 숫자 타입으로
parseInt(자료)     // 정수로
parseFloat(자료)   // 실수로
String(자료)       // 문자열로
Boolean(자료)      // 논리형으로
```

**자동 형변환 2가지 규칙**
- `"문자열" * 1` → 숫자 변환 시도
- `"문자열" + 숫자` → 문자열 연결

### 1-5. 연산자 7종

| 종류 | 연산자 | 비고 |
| --- | --- | --- |
| 산술 | `+ - * / %` | 컴퓨터는 백분율을 모릅니다 (직접 계산 필요) |
| 연결 | `+` | 문자 ↔ 숫자 |
| 비교 | `> < >= <=` `==` `!=` `===` `!==` | |
| 논리 | `&&` `\|\|` `!` | |
| 대입 | `=` `+= -= *= /= %=` | |
| 증감 | `++x` `x++` `--x` `x--` | 전위/후위 |
| 삼항 | `조건 ? 참 : 거짓` | 중첩 가능 |

**`==` vs `===`** (노트에 정확히 정리하셨습니다)
- `==` — **값만** 같으면 true
- `===` — **값과 타입** 둘 다 같아야 true

**연산자 우선순위**
```
() → !,++,-- → *,/,% → +,- → <,> → ==,=== → && → || → ?: → =,+=
```

## 2. 추가로 알면 좋은 활용법

### 2-1. `==`가 만드는 함정

```javascript
0 == "";            // true
0 == "0";           // true
"" == "0";          // false  ← 위 둘이 true인데 이건 false
null == undefined;  // true
NaN == NaN;         // false  ← 자기 자신과도 다름
[] == false;        // true
```

**`===`만 쓰세요.** 예외적으로 `x == null`은 "null이거나 undefined" 검사로 유용합니다.

`NaN` 판별은 `Number.isNaN(x)`를 씁니다.

### 2-2. falsy 값 6개

```javascript
false, 0, "", null, undefined, NaN   // 이 6개만 falsy
```

나머지는 전부 truthy입니다. **`"0"`, `[]`, `{}`는 truthy**입니다.

```javascript
if ([]) console.log("실행됨");    // 빈 배열도 truthy!
if (arr.length) { }              // 배열이 비었는지는 length로
```

### 2-3. `||` vs `??`

```javascript
const name1 = input || "익명";   // falsy 전체를 걸러냄 (0, "" 포함 — 주의!)
const name2 = input ?? "익명";   // null, undefined만 걸러냄
```

`input`이 `0`일 때 `||`는 기본값으로 넘어가지만 `??`는 `0`을 유지합니다. **숫자를 다룰 땐 `??`** 를 쓰세요.

[[JS day14 게시판 CRUD]] 에서 `localStorage.getItem()`이 `null`을 반환하므로 `??`가 딱 맞습니다.

### 2-4. 부동소수점 — day03/memo의 질문

```javascript
console.log(0.1 + 0.2);          // 0.30000000000000004
console.log(0.1 + 0.2 === 0.3);  // false
```

JS는 모든 숫자가 `double`(IEEE 754)입니다.

```javascript
Number((0.1 + 0.2).toFixed(2));       // 0.3
(0.1 * 100 + 0.2 * 100) / 100;        // 0.3  ← 정수로 올려서 계산
```

**금액은 원 단위 정수로 다루는 게 가장 안전합니다.** Java의 `BigDecimal`, SQL의 `DECIMAL`과 같은 맥락입니다. → [[Java day01 자바 구조와 자료형]]

### 2-5. `let a = [10]`과 `let b = [10]`은 같은가

`day03/memo`의 질문입니다. **다릅니다.**

```javascript
let a = [10], b = [10];
a === b;        // false — 서로 다른 객체 (주소 비교)
a[0] === b[0];  // true  — 원시값 10끼리 비교

let c = a;
c.push(20);
console.log(a);   // [10, 20] ← a와 c는 같은 배열
```

- **원시 타입** (number, string, boolean) — 값 자체를 복사
- **참조 타입** (object, array, function) — 주소를 복사

[[Java day05 클래스와 인스턴스]] 의 `Book[] archive = library;`와 정확히 같은 구조입니다. Python도 마찬가지입니다. → Python 폴더의 얕은 복사 문제

**복사 3단계**
```javascript
const b = a;                    // 참조 복사
const shallow = [...a];         // 얕은 복사 (1단계만)
const deep = structuredClone(a); // 깊은 복사
```

### 2-6. `parseInt`의 함정

```javascript
parseInt("12abc");    // 12   ← 앞에서부터 읽다가 멈춤
Number("12abc");      // NaN  ← 전체가 숫자여야 함
parseInt("");         // NaN
Number("");           // 0    ← 주의!
parseInt("08");       // 8
```

**엄격한 검증이 필요하면 `Number`, 관대하게 읽고 싶으면 `parseInt`** 입니다.

## 3. 더 나아가 알면 좋은 것

### 3-1. 배열 고급 메소드

```javascript
const nums = [1, 2, 3, 4, 5];

nums.forEach(n => console.log(n));      // 순회
nums.map(n => n * 2);                   // [2,4,6,8,10] 변환
nums.filter(n => n % 2 === 0);          // [2,4] 걸러내기
nums.reduce((acc, n) => acc + n, 0);    // 15 누적
nums.find(n => n > 3);                  // 4 (첫 번째 요소)
nums.findIndex(n => n > 3);             // 3 (첫 번째 인덱스)
nums.some(n => n > 4);                  // true (하나라도)
nums.every(n => n > 0);                 // true (전부)
nums.join("-");                         // "1-2-3-4-5"
nums.slice(1, 3);                       // [2,3] 자르기 (원본 유지)
nums.sort((a, b) => b - a);             // 내림차순
```

**`sort()` 주의**: 인자 없이 쓰면 **문자열 기준** 정렬입니다.
```javascript
[10, 9, 100].sort();          // [10, 100, 9]  ← 틀림
[10, 9, 100].sort((a,b)=>a-b); // [9, 10, 100] ← 정답
```

**원본을 바꾸는 메소드**: `push` `pop` `shift` `unshift` `splice` `sort` `reverse`
**새 배열을 만드는 메소드**: `map` `filter` `slice` `concat` `toSorted`(신규)

### 3-2. 구조 분해와 전개 연산자

```javascript
const [a, b] = [1, 2];
const { name, age } = user;
const merged = { ...obj1, ...obj2 };
const copy = [...arr];

const [first, ...rest] = [1, 2, 3];   // first=1, rest=[2,3]
```

[[JS day14 게시판 CRUD]] 의 `const object = { title, content, pwd };`가 축약 문법의 예입니다.

### 3-3. 옵셔널 체이닝

```javascript
const city = user?.address?.city;   // 중간이 undefined여도 에러 안 남
const len = arr?.length ?? 0;
```

## 실습 파일

- `2026_FE/Note/day/day03`
- `2026_FE/day03/exam/exam1.js`, `exam2.js`, `exam1.html`, `exam2.html`
- `2026_FE/day03/practice/practice2.js`, `practice2.html`
- `2026_FE/day03/memo`

## 관련 노트

[[JavaScript MOC]] · [[JS day02 변수와 입출력]] · [[JS day04 조건문]] · [[Java day02 타입 변환]] · [[Java day04 제어문과 배열]]
