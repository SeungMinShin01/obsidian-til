---
출처: Claude 분석
원본: KDT_2026/2026B_BE/src/day02
작성일: 2026-08-10
tags: [학습, java]
---

# Java day02 — 타입 변환

> 실습 파일: `day02/exam/exam1.java`, `day02/practice/practice1~3.java`
> 허브: [[Java MOC]] · 이전: [[Java day01 자바 구조와 자료형]] · 다음: [[Java day03 연산자]]

## 1. 배운 내용

### 1-1. 자동(묵시적) 타입 변환

작은 타입 → 큰 타입. **자료는 유지되고 타입만 바뀝니다.**

```
byte → short → int → long → float → double
```

```java
byte bytevalue = 100;
short shortvalue = bytevalue;     // 가능
int intvalue = shortvalue;        // 가능
long longvalue = intvalue;        // 가능
float floatvalue = longvalue;     // 가능
double doublevalue = floatvalue;  // 가능
```

`long`(8byte)에서 `float`(4byte)로 가는데 왜 자동일까요? **크기가 아니라 표현 범위** 때문입니다. `float`는 지수 표현을 써서 훨씬 큰 수를 담을 수 있습니다. 대신 정밀도는 떨어집니다.

### 1-2. 연산 중 자동 타입 변환

```java
byte b1 = 10, b2 = 20;
int result = b1 + b2;        // byte + byte  => int
short s1 = 30;
int result2 = b2 + s1;       // byte + short => int
long l1 = 50L;
long result4 = i1 + l1;      // int + long   => long
float result5 = i1 + f1;     // int + float  => float
double result6 = i1 + d1;    // int + double => double
```

**규칙 두 가지**
1. `int`보다 작은 타입끼리 연산하면 무조건 `int`로 승격됩니다
2. 그 외에는 **더 큰 타입** 쪽으로 결과가 나옵니다

`byte + byte`를 `byte` 변수에 담으려면 캐스팅이 필요합니다.
```java
byte sum = (byte)(b1 + b2);
```

### 1-3. 강제(명시적) 타입 변환

큰 타입 → 작은 타입. `(타입)` 캐스팅이 필요하고 **자료 손실이 발생합니다.**

```java
double dvalue = 3.14;
float fvalue = (float)dvalue;
long lvalue = (long)fvalue;      // 3 (소수점 버림)
int ivalue = (int)lvalue;
short svalue = (short)ivalue;
byte bvalue = (byte)svalue;
```

**정수 → 정수 축소**는 상위 비트를 잘라냅니다.
```java
int i = 300;
byte b = (byte)i;   // 44 (300 % 256 = 44)
```

**실수 → 정수 축소**는 소수점을 **버립니다**(반올림 아님).
```java
(int) 3.99   // 3
(int) -3.99  // -3
```

### 1-4. practice — printf와 Scanner 실전

`practice1.java` 11문제에서 다룬 것들입니다.

```java
System.out.printf("제 이름은 %s, 나이는 %d세, 키는 %.1fcm 입니다.%n", name, age, height);

// 표 형태 출력 — 폭 지정 + 왼쪽 정렬
System.out.printf("%-3s %-5s %-10s%n", "번호", "작성자", "방문록");
System.out.printf("%-5d %-5s %-10s%n", num, writer, content);
```

`practice2.java` 4번 — **정수 나눗셈 함정**
```java
int num1 = 11, num2 = 21, num3 = 21;
double avg = (num1 + num2 + num3) / 3;         // 17.0  ← 정수 나눗셈!
double avg2 = (double)(num1 + num2 + num3) / 3; // 17.666...  ← 정답
```
합계가 `int`, 3도 `int`라서 `int` 나눗셈이 되어 소수점이 잘립니다. **어느 한쪽을 실수로 만들어야** 실수 나눗셈이 됩니다.

`practice3.java` 6번 — **문자열 비교**
```java
boolean result3 = "admin".equals(ID) && "1234".equals(PWD) ? true : false;
```
리터럴을 앞에 두는 **Yoda 조건문**입니다. `ID`가 `null`이어도 NullPointerException이 안 납니다.

## 2. 추가로 알면 좋은 활용법

### 2-1. `== ` vs `.equals()`

```java
String a = "hello";
String b = "hello";
System.out.println(a == b);        // true  ← 문자열 상수 풀 공유

String c = new String("hello");
System.out.println(a == c);        // false ← 다른 객체
System.out.println(a.equals(c));   // true  ← 내용 비교
```

`==`가 우연히 `true`가 나오는 경우가 있어서 더 위험합니다. **문자열은 무조건 `.equals()`** 를 쓰세요.

`Scanner`로 입력받은 문자열은 상수 풀에 없으므로 `==`가 항상 `false`입니다.

### 2-2. `%n` vs `\n`

```java
System.out.printf("...%n");   // OS에 맞는 줄바꿈 (권장)
System.out.printf("...\n");   // 항상 LF
```

윈도우는 `\r\n`, 리눅스·맥은 `\n`을 씁니다. `printf`에서는 `%n`이 안전합니다.

### 2-3. 오버플로

```java
int max = 2147483647;
System.out.println(max + 1);   // -2147483648  ← 음수로 뒤집힘
```

정수 오버플로는 **에러 없이 조용히** 값이 뒤집힙니다. 큰 수 계산은 `long`이나 `BigInteger`를 씁니다.

```java
long result = (long) a * b;   // a, b가 int여도 long으로 계산
```
`(long)(a * b)`는 이미 int로 계산한 뒤 변환이라 소용없습니다. **캐스팅 위치가 중요합니다.**

## 3. 더 나아가 알면 좋은 것

### 3-1. 래퍼 클래스와 오토박싱

```java
int i = 10;
Integer boxed = i;        // 오토박싱  int → Integer
int unboxed = boxed;      // 언박싱   Integer → int
```

제네릭(`ArrayList<Integer>`)에는 기본 타입을 못 넣기 때문에 필요합니다. → [[Java day09 ArrayList]]

**주의**: `Integer`끼리 `==`로 비교하면 안 됩니다.
```java
Integer a = 1000, b = 1000;
System.out.println(a == b);        // false! (-128~127만 캐시됨)
System.out.println(a.equals(b));   // true
```

### 3-2. 문자열 ↔ 숫자 변환

```java
int i = Integer.parseInt("123");
double d = Double.parseDouble("3.14");
String s = String.valueOf(123);
String s2 = 123 + "";       // 동작하지만 비권장
```

JS의 `Number()` / `parseInt()`와 대응합니다. → [[JS day03 자료형과 연산자]]

### 3-3. `char`는 사실 정수입니다

```java
char c = 'A';
int i = c;              // 65
char next = (char)(c + 1);   // 'B'
System.out.println('A' + 1); // 66 (char + int => int)
```

`System.out.println('A' + 'B')`가 `"AB"`가 아니라 `131`이 나오는 이유입니다. 문자열로 이으려면 `"" + 'A' + 'B'`.

이 성질이 [[Java day04 제어문과 배열]] 의 중첩 switch 문제와 연결됩니다.

## 실습 파일

- `2026B_BE/src/day02/exam/exam1.java`
- `2026B_BE/src/day02/practice/practice1.java`, `practice2.java`, `practice3.java`

## 관련 노트

[[Java MOC]] · [[Java day01 자바 구조와 자료형]] · [[Java day03 연산자]] · [[JS day03 자료형과 연산자]]
