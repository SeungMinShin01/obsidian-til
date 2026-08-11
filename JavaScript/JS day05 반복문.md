---
출처: Claude 분석
원본: KDT_2026/2026_FE/day05, Note/day/day05
작성일: 2026-08-10
tags: [javascript, day05, 반복문, for]
---

# JS day05 — 반복문

> 실습 파일: `day05/exam/exam1.js`, `exam2.js`, `Note/day/day05`, `day05/parcatice/practice4.js`
> 허브: [[JavaScript MOC]] · 이전: [[JS day04 조건문]] · 다음: [[JS day07 객체]]

## 1. 배운 내용

### 1-1. for문의 실행 순서

```javascript
for (초기값; 조건문; 증감식) { 실행문; }
```

순서를 하나씩 따라가면 이렇습니다.

```
for (let i = 1; i <= 3; i++) { logic }

1. 초기값 실행        i = 1
2. 조건문   1<=3 t
3. 실행문   logic
4. 증감식   i = 2
5. 조건문   2<=3 t
6. 실행문   logic
7. 증감식   i = 3
8. 조건문   3<=3 t
9. 실행문   logic
10. 증감식  i = 4
11. 조건문  4<=3 f → 종료
```

**초기값은 딱 한 번만 실행되고, 이후에는 조건 → 실행문 → 증감식이 반복**됩니다.

### 1-2. 반복문 유도 과정 — exam1.js

`exam1.js`가 좋은 이유는 **복붙 → 반복문** 순서로 필요성을 보여주기 때문입니다.

```javascript
// 방법 1: 복붙
console.log("안녕하세요");
console.log("안녕하세요");
console.log("안녕하세요");

// 방법 2: 반복문
for (let 반복수 = 1; 반복수 <= 3; 반복수++) {
  console.log("안녕하세요");
}
```

**패턴 찾기**가 핵심입니다.
- 반복되는 것 → 실행문
- 반복되지 않고 규칙적으로 변하는 것 → 증감식이 만드는 변수

```javascript
// 2단
console.log(`2 * 1 = ${2 * 1}`);
console.log(`2 * 2 = ${2 * 2}`);
// 반복되는 것: `2 * ? = ${2 * ?}`
// 변하는 것: 1~9, 1씩 증가
for (let i = 1; i < 10; i++) {
  console.log(`2 * ${i} = ${2 * i}`);
}
```

### 1-3. 중첩 반복문

정리하면 이렇습니다.
> 상위 for문이 1번 실행될 때마다 하위 for문은 전체 반복

```javascript
for (let i = 1; i <= 3; i++) {
  console.log(i);          // 3번 출력
  for (let j = 1; j <= 2; j++) {
    console.log(j);        // 총 6번 출력 (3 × 2)
  }
}
```

**구구단**
```javascript
for (let 단 = 2; 단 <= 9; 단++) {
  for (let 곱 = 1; 곱 <= 9; 곱++) {
    console.log(`${단} * ${곱} = ${단 * 곱}`);
  }
}
```

### 1-4. break / continue / 무한루프

```javascript
break;      // 가장 가까운 반복문 탈출·종료
continue;   // 가장 가까운 반복문의 증감식으로 이동
for (;;) { }  // 무한루프
```

### 1-5. 누적 합계

```javascript
let 총합계 = 1;
for (let i = 2; i < 6; i++) {
  총합계 = 총합계 + i;   // 총합계 += i 와 동일
}
```

**누적 변수는 반복문 밖에 선언**해야 합니다. 안에 선언하면 매번 초기화됩니다.

## 2. 추가로 알면 좋은 활용법

### 2-1. 배열 순회 4가지

```javascript
const arr = ["a", "b", "c"];

for (let i = 0; i < arr.length; i++) { arr[i]; }   // 인덱스 필요할 때
for (const item of arr) { item; }                  // 값만 필요할 때 (권장)
arr.forEach((item, i) => { });                     // 인덱스도 같이
for (const i in arr) { arr[i]; }                   // 비권장 (키를 문자열로 반환)
```

**`for...in`은 배열에 쓰지 마세요.** 인덱스가 문자열(`"0"`, `"1"`)로 나오고, 배열에 추가된 프로퍼티까지 순회합니다. `for...in`은 객체 전용입니다. → [[JS day07 객체]]

### 2-2. 반복문을 대체하는 배열 메소드

`day05`의 문제들을 배열 메소드로 다시 풀어보면 감이 옵니다.

```javascript
// 1부터 5까지 누적 합계
[1,2,3,4,5].reduce((acc, n) => acc + n, 0);   // 15

// 1부터 5까지 출력
Array.from({ length: 5 }, (_, i) => i + 1).forEach(n => console.log(n));

// 구구단 2단
Array.from({ length: 9 }, (_, i) => `2 * ${i+1} = ${2*(i+1)}`).join("\n");
```

Java의 Stream API와 같은 개념입니다. → [[Java day09 ArrayList]]

### 2-3. `break`가 미치는 범위

`break`는 **가장 가까운 반복문 하나만** 빠져나옵니다.

```javascript
outer:
for (let i = 0; i < 9; i++) {
  for (let j = 0; j < 9; j++) {
    if (i * j > 50) break outer;   // 라벨로 바깥까지 탈출
  }
}
```

Java도 문법이 같습니다. → [[Java day04 제어문과 배열]]

### 2-4. 무한루프 방지

```javascript
let i = 0;
while (i < 10) {
  console.log(i);   // i++ 를 빼먹으면 브라우저가 멈춤!
}
```

브라우저가 얼어붙으면 탭을 닫아야 합니다. `while`을 쓸 때는 **증감식을 먼저 쓰고 로직을 채우는** 습관이 안전합니다.

## 3. 더 나아가 알면 좋은 것

### 3-1. 반복문 성능

```javascript
for (let i = 0; i < arr.length; i++) { }   // 매 반복마다 length 계산
for (let i = 0, len = arr.length; i < len; i++) { }   // 한 번만
```

요즘 엔진은 최적화해주지만, 배열이 반복문 안에서 바뀔 수 있다면 의미가 있습니다.

### 3-2. `Array.from`과 `fill`

```javascript
Array.from({ length: 5 }, (_, i) => i);     // [0,1,2,3,4]
new Array(5).fill(0);                       // [0,0,0,0,0]
Array.from("abc");                          // ["a","b","c"]
[...Array(5).keys()];                       // [0,1,2,3,4]
```

### 3-3. 시간 복잡도

| 코드 | 복잡도 | n=10000 |
| --- | --- | --- |
| 단일 for | O(n) | 1만 |
| 이중 for | O(n²) | 1억 |

[[JS 과제 LevelUP과 게시판]] 의 `Message_Board`가 버블 정렬(O(n²))을 쓴 이유는 배열 사용 금지 제약 때문이었습니다. 배열이 있으면 `sort()`(O(n log n)) 한 줄입니다.

### 3-4. 비동기 반복

```javascript
for (const url of urls) {
  const res = await fetch(url);   // 순차 실행 (느림)
}

await Promise.all(urls.map(url => fetch(url)));   // 동시 실행 (빠름)
```

나중에 서버 통신을 배울 때 다시 만나게 됩니다.

## 실습 파일

- `2026_FE/Note/day/day05`
- `2026_FE/day05/exam/exam1.js`, `exam2.js`, `exampractice.js`, `exampractice.html`
- `2026_FE/day05/parcatice/practice4.js`, `practice4.html`

## 관련 노트

[[JavaScript MOC]] · [[JS day04 조건문]] · [[JS day07 객체]] · [[CSS day05 첫 스타일링]] · [[Java day04 제어문과 배열]]
