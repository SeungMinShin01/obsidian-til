---
출처: Claude 분석
원본: KDT_2026/2026_FE/day07, Note/day/day07
작성일: 2026-08-10
tags: [javascript, day07, 객체, Object]
---

# JS day07 — 객체

> 실습 파일: `Note/day/day07`, `day07/activity/activity1.js`, `day07/practice/practicce6.js`
> 허브: [[JavaScript MOC]] · 이전: [[JS day05 반복문]] · 다음: [[JS day10 함수]]

## 1. 배운 내용

### 1-1. 객체란

정의부터 정리합니다.
> 어떠한 대상의 속성(정보·상태 등)을 정의하는 것

```javascript
const user = { 속성명: 속성값, "속성명2": 속성값 };
```

- `{ }` 중괄호를 이용한 자료 타입
- 주로 변수·상수에 저장·참조합니다
- **`.`(접근/도트/참조) 연산자**로 속성 값을 호출합니다

### 1-2. 기본 조작

```javascript
const user = { 이름: "유재석", 나이: 40 };

user.이름;              // 조회
user["이름"];           // 대괄호 표기 (변수를 키로 쓸 때)
user.직업 = "개그맨";    // 추가
user.나이 = 41;         // 수정
delete user.나이;       // 삭제
"이름" in user;         // 존재 여부 → true
```

### 1-3. Object 메소드

| 메소드 | 반환 |
| --- | --- |
| `Object.keys(obj)` | 모든 속성명 **배열** |
| `Object.values(obj)` | 모든 속성값 배열 |
| `Object.entries(obj)` | `[키, 값]` 쌍 배열 |

```javascript
Object.keys({a:1, b:2});      // ["a", "b"]
Object.values({a:1, b:2});    // [1, 2]
Object.entries({a:1, b:2});   // [["a",1], ["b",2]]
```

`Object.keys`가 배열을 반환한다는 점이 중요합니다. 배열이 되면 `map`, `filter`, `forEach`를 전부 쓸 수 있습니다.

### 1-4. 중첩

```javascript
const obj = {
  key1: [1, 2, 3],           // 배열
  key2: { a: 1 },            // 객체
  key3: function() { }       // 함수 (= 메소드)
};
```

**속성값에는 어떤 타입이든 들어갑니다.**

### 1-5. 배열 vs 객체 — 선택 기준

`day07` 노트의 결론이 핵심입니다.
> 배열은 여러 자료들을 **인덱스**로 식별하고, 객체는 **속성명**으로 식별한다.
> 서로 다른 자료들의 의미·용도가 다르면 객체를 권장한다.

```javascript
// 나쁨 — 각 자리가 뭘 의미하는지 코드만 봐서는 모름
const user = ["유재석", 40, "개그맨"];

// 좋음 — 의미가 드러남
const user = { 이름: "유재석", 나이: 40, 직업: "개그맨" };
```

**같은 종류가 여러 개** → 배열, **다른 종류가 모임** → 객체입니다.

실전에서는 둘을 조합합니다.
```javascript
const users = [
  { 이름: "유재석", 나이: 40 },
  { 이름: "강호동", 나이: 45 },
];
```

## 2. 추가로 알면 좋은 활용법

### 2-1. 객체 순회 3가지

```javascript
const user = { 이름: "유재석", 나이: 40 };

for (const key in user) {
  console.log(key, user[key]);         // for...in — 객체 전용
}

Object.keys(user).forEach(key => console.log(key, user[key]));

for (const [key, value] of Object.entries(user)) {
  console.log(key, value);             // 가장 깔끔 (구조 분해)
}
```

**`for...in`은 객체용, `for...of`는 배열용**입니다. 배열에 `for...in`을 쓰면 인덱스가 문자열로 나옵니다.

### 2-2. 단축 속성명과 계산된 속성명

```javascript
const title = "제목", content = "내용";

const obj = { title: title, content: content };   // 일반
const obj2 = { title, content };                  // 단축 (변수명 = 키명일 때)

const key = "이름";
const obj3 = { [key]: "유재석" };                  // 계산된 속성명 → { 이름: "유재석" }
```

[[JS day14 게시판 CRUD]] 의 `write.js`에서 `const object = { title, content, pwd };`가 단축 문법입니다.

### 2-3. 구조 분해 할당

```javascript
const { 이름, 나이 } = user;
const { 이름: name, 나이: age } = user;        // 이름 바꿔 받기
const { 이름, 직업 = "무직" } = user;           // 기본값

function 출력({ 이름, 나이 }) { }               // 매개변수에서 바로 분해
출력(user);
```

### 2-4. 객체 복사

```javascript
const b = a;                       // 참조 복사 — 같은 객체
const shallow = { ...a };          // 얕은 복사 — 1단계만
const deep = structuredClone(a);   // 깊은 복사
const merged = { ...a, ...b };     // 병합 (뒤가 우선)
```

```javascript
const a = { info: { age: 40 } };
const shallow = { ...a };
shallow.info.age = 50;
console.log(a.info.age);   // 50 ← 안쪽 객체는 여전히 공유!
```

Python의 `m[:]` 얕은 복사, Java의 배열 참조 복사와 완전히 같은 원리입니다. → [[Java day05 클래스와 인스턴스]]

### 2-5. 옵셔널 체이닝과 기본값

```javascript
const city = user?.address?.city ?? "미입력";
```

중첩 객체가 깊어질수록 필수입니다.

### 2-6. `Object.freeze`

```javascript
const config = Object.freeze({ MAX: 100 });
config.MAX = 200;   // 조용히 무시 (strict 모드면 에러)
```

`const`는 재할당만 막고 내부 수정은 못 막습니다. 내용까지 고정하려면 `freeze`가 필요합니다. Java의 `final` + 불변 객체와 같은 목적입니다.

## 3. 더 나아가 알면 좋은 것

### 3-1. 객체의 메소드와 `this`

```javascript
const 계산기 = {
  값: 0,
  더하기(n) {            // 메소드 축약 문법
    this.값 += n;
    return this;         // 체이닝을 위해 자기 자신 반환
  },
  빼기(n) { this.값 -= n; return this; }
};

계산기.더하기(5).빼기(2);   // 메소드 체이닝
console.log(계산기.값);      // 3
```

**주의 — 화살표 함수는 메소드로 쓰면 안 됩니다.**
```javascript
const obj = {
  name: "유재석",
  hello1: function() { console.log(this.name); },   // "유재석"
  hello2: () => { console.log(this.name); }         // undefined!
};
```
화살표 함수는 자기 `this`를 갖지 않고 바깥 스코프의 것을 씁니다.

### 3-2. `class` 문법

```javascript
class Post {
  constructor(title, content) {
    this.title = title;
    this.content = content;
  }
  요약() { return this.title.slice(0, 10); }
}

const p = new Post("제목", "내용");
```

Java의 클래스와 문법이 거의 같습니다. → [[Java day05 클래스와 인스턴스]]

**private 필드** (`#` 접두어)
```javascript
class User {
  #password;                       // 외부 접근 불가
  setPassword(pw) { this.#password = pw; }
}
```
Java의 `private`과 같은 역할입니다. → [[Java day08 접근제한자와 static]]

### 3-3. `Map` — 객체로 부족할 때

```javascript
const map = new Map();
map.set("키", "값");
map.get("키");
map.has("키");
map.size;
map.delete("키");
```

| | 객체 `{}` | `Map` |
| --- | --- | --- |
| 키 타입 | 문자열·심볼만 | **아무거나** (객체도 가능) |
| 순서 | 보장 안 됨(숫자키) | 삽입 순서 보장 |
| 크기 | `Object.keys().length` | `.size` |
| 순회 | `for...in` | `for...of` 바로 가능 |

Java의 `HashMap`과 대응합니다. → [[Java day09 ArrayList]]

### 3-4. JSON 변환

```javascript
JSON.stringify(obj);        // 객체 → 문자열
JSON.parse(str);            // 문자열 → 객체
JSON.stringify(obj, null, 2);  // 들여쓰기 2칸 (읽기 좋게)
```

**함수와 `undefined`는 JSON에 담기지 않습니다.** `Date`는 문자열로 변합니다.

[[JS day13 웹 스토리지와 인터벌]] 에서 localStorage에 객체를 저장할 때 필수입니다.

## 실습 파일

- `2026_FE/Note/day/day07`
- `2026_FE/day07/activity/activity1.js`, `activiry1.html`
- `2026_FE/day07/practice/practicce6.js`, `practice6.html`
- `2026_FE/day07/day06.txt`

## 관련 노트

[[JavaScript MOC]] · [[JS day05 반복문]] · [[JS day10 함수]] · [[JS day13 웹 스토리지와 인터벌]] · [[Java day05 클래스와 인스턴스]]
