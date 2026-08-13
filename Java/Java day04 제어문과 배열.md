---
출처: Claude 분석
원본: KDT_2026/2026B_BE/src/day04
작성일: 2026-08-10
tags: [학습, java]
---

# Java day04 — 제어문과 배열

> 실습 파일: `day04/exam/exam1.java`(조건문), `exam2.java`(반복문), `exam3.java`(배열), `day04/practice`
> 허브: [[Java MOC]] · 이전: [[Java day03 연산자]] · 다음: [[Java day05 클래스와 인스턴스]]

## 1. 배운 내용

### 1-1. 조건문 — exam1.java

```java
if (온도 <= 10)                          // 실행문 1개면 {} 생략 가능
    System.out.println("외투 입는다.");

if (온도 <= 10) { ... } else { ... }

if (온도 <= 10) { ... }
else if (온도 <= 30) ...
else ...
```

### 1-2. switch

```java
switch (grade) {
    case 'A':
        System.out.println("A등급 입니다.");
        break;              // 없으면 아래 case로 흘러내림(fall-through)
    case 'B':
        ...
        break;
    default:
        break;
}
```

`switch`가 받을 수 있는 타입: `byte` `short` `char` `int` `String`(Java 7+) `enum`. `long`, `double`, `boolean`은 안 됩니다.

### 1-3. 반복문 — exam2.java

```java
for (int i = 1; i <= 10; i++) { }   // 초기값 → 조건 → 실행문 → 증감식
while (i <= 10) { i++; }
for (;;) { }                        // 무한루프
```

- `break` — 가장 가까운 반복문 탈출
- `continue` — 가장 가까운 반복문의 증감식으로 이동

**구구단 (중첩 반복문)**
```java
for (int 단 = 2; 단 <= 9; 단++) {
    for (int 곱 = 1; 곱 <= 9; 곱++) {
        System.out.printf("%d X %d = %d %n", 단, 곱, 단 * 곱);
    }
}
```

**향상된 for문**
```java
for (int data : ary) {   // 콜론 오른쪽 배열의 요소를 왼쪽 변수에 하나씩
    System.out.println(data);
}
```

### 1-4. 배열 — exam3.java

```java
int[] arr1 = new int[3];                        // 크기 지정, 자동 초기화
String[] arr2 = {"유재석", "강호동", "신동엽"};   // 초기값 지정
```

**특징 3가지**
1. 동일한 타입끼리만
2. 고정(정적) 길이
3. 요소가 자동 초기화 (정수 0, 실수 0.0, boolean false, 참조 null)

```java
System.out.println(arr1);                   // [I@6c629d6e ← 메모리 주소
System.out.println(Arrays.toString(arr1));  // [0, 0, 0]  ← 실제 값
System.out.println(arr2.length);            // 요소 총개수 (필드, 괄호 없음)
arr2[0] = "유재석2";                         // 기존 요소 수정은 가능
// arr2.push("하하");  arr2.splice(0,1);    // 추가·삭제는 불가능
```

**JS 배열과의 차이**

| | Java 배열 | JS 배열 |
| --- | --- | --- |
| 타입 | 동일 타입만 | 아무거나 |
| 길이 | 고정 | 가변 |
| 추가·삭제 | 불가 | `push` `splice` |
| 초기값 | 자동 (0, null 등) | `undefined` |
| 길이 확인 | `.length` (필드) | `.length` (프로퍼티) |

→ [[JS day03 자료형과 연산자]]

### 1-5. 배열의 메모리 구조

메모리 구조로 보면 명확합니다.

```
int 1개 선언        → 4byte  → [ ][ ][ ][ ]
new int[3] 선언     → 4byte×3 → [101][102][103][104] [201][202][203][204] [301][302][303][304]
```

> 배열은 모든 인덱스의 주소값을 참조하지 않고 **가장 앞에 있는 주소값 1개(101호)만** 참조한다.
> `배열명[0]` = 101호, `배열명[1]` = 타입 크기만큼 이동 = 201호

**이게 배열 인덱스 접근이 O(1)인 이유입니다.** 주소를 계산으로 구하기 때문에 몇 번째든 같은 속도입니다. 반대로 연결 리스트는 처음부터 따라가야 해서 O(n)입니다.

## 2. 추가로 알면 좋은 활용법

### 2-1. 배열 순회 조건 — length와 인덱스

배열에서 가장 자주 만나는 예외가 `ArrayIndexOutOfBoundsException`입니다.

```java
int[] ary = { 92, 80, 75 };
```

`ary.length`는 **3**이지만 유효한 인덱스는 **0, 1, 2**뿐입니다. 조건에 `<=`를 쓰면 `ary[3]`에 접근하게 됩니다.

```java
for (int i = 0; i < ary.length; i++) { }        // 정답
for (int i = 0; i <= ary.length - 1; i++) { }   // 이것도 정답
```

**기억법**: 배열 순회 조건은 `i < length` 아니면 `i <= length - 1`입니다. `i <= length`는 **언제나 틀립니다.** 헷갈리면 향상된 for문을 쓰세요.

### 2-2. 중첩 switch를 안전하게 쓰기

중첩 switch에서 조심할 것이 두 가지 있습니다.

1. **바깥 switch의 각 `case`에 `break`를 반드시** 넣습니다. 없으면 다음 `case`로 흘러내립니다(fall-through)
2. **각 switch의 대상 타입을 섞지 않습니다.** `char`는 내부적으로 정수라 `case 1`처럼 써도 컴파일은 통과하지만, `'B'`는 66이므로 절대 매칭되지 않습니다 ([[Java day02 타입 변환]] 참고)

**방법 1 — switch를 분리**
```java
switch (grade) {
    case 'A':
        switch (adult) {
            case 1: System.out.println("A등급 성인입니다."); break;
            case 0: System.out.println("A등급 미성년자 입니다."); break;
        }
        break;          // ← 이게 반드시 필요
    case 'B':
        switch (adult) {
            case 1: System.out.println("B등급 성인입니다."); break;
            case 0: System.out.println("B등급 미성년자입니다."); break;
        }
        break;
}
```

**해결 2 — switch 표현식 (Java 14+)**
```java
String msg = switch (grade) {
    case 'A' -> adult == 1 ? "A등급 성인입니다." : "A등급 미성년자입니다.";
    case 'B' -> adult == 1 ? "B등급 성인입니다." : "B등급 미성년자입니다.";
    default  -> "재시험입니다.";
};
System.out.println(msg);
```

`break`가 필요 없고 fall-through 버그가 원천 차단됩니다. 모든 경우를 다루지 않으면 컴파일 에러가 나서 누락도 막아줍니다.

### 2-3. Arrays 유틸리티

```java
import java.util.Arrays;

Arrays.toString(arr);                 // 내용 출력
Arrays.sort(arr);                     // 오름차순 정렬
Arrays.fill(arr, 5);                  // 전체 채우기
int[] copy = Arrays.copyOf(arr, 5);   // 크기 5로 복사 (길이 늘리기 트릭)
Arrays.equals(a, b);                  // 내용 비교 (== 는 주소 비교)
Arrays.binarySearch(arr, 80);         // 정렬된 배열에서 이진 탐색
int[][] deep = ...;  Arrays.deepToString(deep);   // 2차원 배열 출력
```

`Arrays.copyOf`가 "고정 길이" 한계를 우회하는 방법입니다. 새 배열을 만들어 복사합니다. **`ArrayList`가 내부에서 하는 일이 정확히 이것입니다.** → [[Java day09 ArrayList]]

### 2-4. 2차원 배열

```java
int[][] grid = new int[3][4];      // 3행 4열
int[][] jagged = new int[3][];     // 가변 배열 (행마다 길이 다름)
jagged[0] = new int[2];

for (int[] row : grid) {
    for (int cell : row) { }
}
```

구구단을 2차원 배열에 담아보면 감이 빨리 옵니다.

### 2-5. 라벨로 다중 반복문 탈출

`break`는 가장 가까운 반복문만 빠져나옵니다.

```java
outer:
for (int i = 0; i < 9; i++) {
    for (int j = 0; j < 9; j++) {
        if (i * j > 50) break outer;   // 바깥 for까지 탈출
    }
}
```

## 3. 더 나아가 알면 좋은 것

### 3-1. 배열 vs ArrayList vs LinkedList

| | 배열 | ArrayList | LinkedList |
| --- | --- | --- | --- |
| 내부 구조 | 연속 메모리 | 연속 메모리(배열) | 노드 연결 |
| 인덱스 조회 | O(1) | O(1) | O(n) |
| 중간 삽입·삭제 | 불가 | O(n) | O(1) (노드 찾은 후) |
| 크기 | 고정 | 가변 | 가변 |

`ArrayList`는 꽉 차면 **1.5배 크기의 새 배열을 만들어 복사**합니다. 크기를 미리 안다면 `new ArrayList<>(1000)`으로 초기 용량을 주는 게 좋습니다.

### 3-2. Stream API로 배열 다루기

```java
int[] arr = {92, 80, 75};

Arrays.stream(arr).sum();           // 247
Arrays.stream(arr).average();       // OptionalDouble[82.33]
Arrays.stream(arr).max();           // OptionalInt[92]
Arrays.stream(arr).filter(n -> n >= 80).toArray();
```

JS의 `reduce`, `filter`와 같은 개념입니다. → [[JS day05 반복문]]

### 3-3. 시간 복잡도 감각

| 코드 | 복잡도 | n=10000일 때 |
| --- | --- | --- |
| 단일 for | O(n) | 1만 번 |
| 이중 for | O(n²) | 1억 번 |
| 삼중 for | O(n³) | 1조 번 (사실상 불가) |

코딩테스트에서 반복문 중첩 수는 곧 지수입니다. 이중 for가 보이면 "n이 얼마나 커질 수 있는가"를 먼저 생각하는 습관이 필요합니다.

## 실습 파일

- `2026B_BE/src/day04/exam/exam1.java`, `exam2.java`, `exam3.java`
- `2026B_BE/src/day04/practice/pracitce1.java`, `practice2.java`

## 관련 노트

[[Java MOC]] · [[Java day03 연산자]] · [[Java day05 클래스와 인스턴스]] · [[Java day09 ArrayList]] · [[JS day04 조건문]] · [[JS day05 반복문]]
