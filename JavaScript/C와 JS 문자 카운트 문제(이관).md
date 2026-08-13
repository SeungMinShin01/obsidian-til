---
출처: 이관
원본: 노션 > Problem Solving > Velog > day02
작성일: 2026-08-10
tags: [학습, javascript]
---

# C와 JS 문자 카운트 문제 (이관)

> 노션 `Velog > day02` 페이지에 있던 코드 문제를 이 폴더로 발췌·이관했습니다. 원본 페이지는 그대로 두었습니다.

## 문제

문자열이 `"BBABACB"`일 때 `B: 4 A: 2 C: 1`을 출력하는 코드를 작성하시오.

## 처음 쓴 답 (오답)

```c
#include <stdio.h>

int main()
{
    int w = 0, y = 0, z = 0;
    char str[] = "BBABACB";

    for (int i = 0; str[i] != '\0'; i++) {
        switch (str[i]) {
            case 'A': w+1;    // ← 값이 증가하지 않음
            break;
            case 'B': y+1;    // ← 같은 실수
            break;
            case 'C': z+1;
            break;
            default:
            break;
        }
    }
    printf("B: %d A: %d C: %d", y, w, z);
    return 0;
}
```

**오류 원인**: `w + 1`은 **계산만 하고 버립니다.** 결과를 어디에도 대입하지 않으므로 `w`는 그대로 0입니다.
`w++` 또는 `w = w + 1`이어야 합니다.

컴파일러는 이걸 에러가 아니라 **경고**로만 알려줍니다 (`-Wall` 옵션을 켜야 "statement with no effect"가 보입니다). 그래서 놓치기 쉽습니다.

## 수정 답안 (C)

```c
#include <stdio.h>

int main()
{
    int w = 0, y = 0, z = 0;
    char str[] = "BBABACB";

    for (int i = 0; str[i] != '\0'; i++) {
        switch (str[i]) {
            case 'A': w++; break;
            case 'B': y++; break;
            case 'C': z++; break;
            default: break;
        }
    }
    printf("B: %d A: %d C: %d", y, w, z);
    return 0;
}
```

## JS 버전

```javascript
let w = 0; // A 개수
let y = 0; // B 개수
let z = 0; // C 개수

const str = "BBABACB";

for (let i = 0; i < str.length; i++) {
  switch (str[i]) {
    case "A": w++; break;
    case "B": y++; break;
    case "C": z++; break;
    default: break;
  }
}

console.log(`A: ${w} B: ${y} C: ${z}`);
```

**C와 JS의 반복 조건 차이**
- C: `str[i] != '\0'` — 문자열 끝에 널 문자가 있어서 이걸로 끝을 압니다
- JS: `i < str.length` — 문자열 객체가 길이를 알고 있습니다

## 추가로 알면 좋은 것

### JS라면 더 짧게 쓸 수 있습니다

```javascript
// 방법 1: 객체로 카운트 (문자 종류가 늘어나도 코드 변경 불필요)
const count = {};
for (const c of "BBABACB") {
  count[c] = (count[c] || 0) + 1;
}
console.log(count);   // { B: 4, A: 2, C: 1 }

// 방법 2: reduce
const count2 = [..."BBABACB"].reduce((acc, c) => {
  acc[c] = (acc[c] ?? 0) + 1;
  return acc;
}, {});

// 방법 3: Map (키 순서가 삽입 순서로 보장됨)
const map = new Map();
for (const c of "BBABACB") map.set(c, (map.get(c) ?? 0) + 1);
```

`switch`는 **찾을 문자를 미리 알 때만** 쓸 수 있습니다. 객체/Map 방식은 어떤 문자가 나와도 자동으로 처리됩니다.

### `for...of`로 문자열 순회

```javascript
for (const c of str) { }        // 문자 하나씩
for (const i in str) { }        // 인덱스 (문자열엔 잘 안 씀)
str.split("").forEach(c => {}); // 배열로 바꿔서
[...str].forEach(c => {});      // 전개 연산자
```

`for...of`가 이모지 같은 유니코드 문자도 안전하게 처리합니다. `str[i]`는 서로게이트 쌍을 반쪽만 가져올 수 있습니다.

### switch의 fall-through 활용

```javascript
switch (c) {
  case "A":
  case "a":
    모음++;    // break가 없으면 아래로 흘러내림 — 의도적으로 쓸 때도 있음
    break;
}
```
