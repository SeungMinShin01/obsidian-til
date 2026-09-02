---
출처: Claude 분석
원본: KDT_2026/2026B_BE/src/day01
작성일: 2026-08-10
tags: [학습, java]
---

# Java day01 — 자바 구조와 자료형

> 실습 파일: `2026B_BE/src/day01/Exam1.java`, `Exam2.java`, `Exam3.java`
> 허브: [[Java MOC]] · 다음: [[Java day02 타입 변환]]

## 1. 배운 내용

### 1-1. 자바 프로그램의 최소 단위 — Exam1.java

```java
package day01;

public class Exam1 {
    public static void main(String[] args) {
        System.out.println("안녕자바");
    }
}
```

각 요소의 의미는 이렇습니다.

| 요소 | 의미 |
| --- | --- |
| `public` | 공개용. 다른 패키지에서도 사용 가능 |
| `class` | 클래스 선언 키워드 |
| 클래스명 | 첫 글자는 대문자. **자바의 최소 컴파일 단위** |
| `{ }` | 클래스의 시작과 끝. 이 안에서만 코드 작성 |
| `main` | 실행 시작점. 번역된 코드를 읽는 흐름 단위 = 메인 스레드 |
| `;` | 한 문장의 끝. 컴파일러가 이 단위로 끊어 읽음 |

**선언 위치 규칙**
- 클래스 안 / main 밖 → 선언·정의만 가능
- main 안 → 선언 + 실행문 가능
- 클래스 밖 → 코드 작성 금지

**JS에 `main`이 없는 이유**: 브라우저 엔진이 스크립트를 위에서부터 바로 실행하기 때문입니다. 자바는 실행 진입점을 명시해야 합니다.

**VSCode 단축키**: `m` + Enter → `main` 자동완성, `so` + Enter → `System.out.println();`

### 1-2. 리터럴과 자료형 — Exam2.java

**리터럴** = 코드에 직접 적은 값 그 자체. `3`, `3.14`, `'유'`, `"유재석"`, `true`

**자료형** = 자료를 효율적으로 분류하는 방법. 여기서 효율이란 **자료 크기에 맞는 타입을 골라 빈 공간(여백)을 줄이는 것**입니다.

| 타입 | 크기 | 범위·특징 | 리터럴 예 |
| --- | --- | --- | --- |
| `boolean` | 1 byte | true / false | `true` |
| `char` | 2 byte | 문자 1개, 유니코드 (코드 ↔ 자연어) | `'A'` |
| `String` | N × 2 byte | 문자 N개 (**참조 타입**) | `"abc"` |
| `byte` | 1 byte | -128 ~ 127 | `100` |
| `short` | 2 byte | 약 ±3만 | `30000` |
| `int` | 4 byte | 약 ±21억 (**정수 리터럴 기본**) | `2000000000` |
| `long` | 8 byte | ±21억 초과 | `20000000000L` |
| `float` | 4 byte | 소수점 7~8자리 | `0.123456789F` |
| `double` | 8 byte | 소수점 15~17자리 (**실수 리터럴 기본**) | `0.1234...` |

**8가지 기본 타입 vs 그 외**
- 기본 타입 8개 — 리터럴을 값 그대로 저장
- 참조 타입 — `String`, 클래스, 배열, 인터페이스. **주소를 저장**

**정적 타입 vs 동적 타입**
- C / Java → 정적(직접) 타입. 개발자가 명시. 컴파일 시점에 타입 오류를 잡아줌
- Python / JS → 동적(자동) 타입. 런타임에 결정

**`long`과 `float` 리터럴 접미사**: `long l = 20000000000;`은 에러입니다. 리터럴 `20000000000`이 `int`로 해석되어 범위를 넘기 때문입니다. `L`을 붙여야 합니다. `float f = 0.1;`도 마찬가지로 `0.1`이 `double`이라 에러이고 `F`가 필요합니다.

**실수는 정밀 계산이 불가능합니다.** 부동소수점 표현이라 오차가 있습니다. 정교한 계산에는 전용 라이브러리가 필요합니다. → 2-2 참고

### 1-3. 출력 — Exam3.java

```java
System.out.println("자바안녕1");   // 출력 후 자동 줄바꿈
System.out.print("자바안녕2");     // 줄바꿈 없음
System.out.printf("형식", 자료);   // 형식 지정 출력
```

`System`(클래스) → `out`(출력 객체) → `println`(출력 함수) 구조입니다.

**이스케이프 문자**: `\n` 줄바꿈, `\t` 들여쓰기, `\'`, `\"`, `\\`

**printf 서식**

| 서식 | 의미 | 예 |
| --- | --- | --- |
| `%s` | 문자열 | `%s` → 유재석 |
| `%d` | 정수 | `%d` → 40 |
| `%f` | 실수 | `%f` → 123.456789 |
| `%b` | 논리값 | `%b` → true |
| `%6d` | 폭 6, 오른쪽 정렬 | `    40` |
| `%-6d` | 폭 6, 왼쪽 정렬 | `40    ` |
| `%06d` | 폭 6, 앞을 0으로 | `000040` |
| `%5.2f` | 폭 5, 소수점 2자리 | `123.46` |

### 1-4. 입력 — Scanner

```java
import java.util.Scanner;          // 파일 상단에 import

Scanner scanner = new Scanner(System.in);
String str = scanner.next();       // 공백/엔터 전까지
int i = scanner.nextInt();
double d = scanner.nextDouble();
boolean b = scanner.nextBoolean();
char c = scanner.next().charAt(0);
String line = scanner.nextLine();  // 한 줄 전체
```

Scanner 한 줄은 다음 5단계로 이루어집니다.
1. `import java.util.Scanner;` — 해당 폴더에서 클래스를 가져옴
2. 클래스명은 대문자, 변수명은 소문자로 시작 (관례)
3. `=` 대입
4. `new` — 인스턴스화. 클래스로 객체를 만듦
5. `Scanner(System.in)` — 생성자 안에 시스템 입력 객체

## 2. 추가로 알면 좋은 활용법

### 2-1. `nextInt()` 다음 `nextLine()`의 함정

`day02/practice/practice1.java` 9번 문제에서 실제로 걸린 부분입니다.

```java
int 번호 = scan.nextInt();      // 숫자만 읽고 엔터(\n)는 버퍼에 남음
String 제목 = scan.nextLine();  // 남은 엔터를 읽어 빈 문자열이 됨!
```

```java
int 번호 = scan.nextInt();
scan.nextLine();                // 버퍼 비우기
String 제목 = scan.nextLine();  // 정상
```

Java day07 메소드와 미니프로젝트 의 `miniProject.java`에서 `scan.nextLine()`을 반복해서 넣은 이유가 이것입니다.

### 2-2. 실수 계산은 BigDecimal

```java
System.out.println(0.1 + 0.2);   // 0.30000000000000004
```

"100자리 이상 소수점은 어떻게 계산하나"에 대한 답입니다.

```java
import java.math.BigDecimal;

BigDecimal a = new BigDecimal("0.1");   // 반드시 문자열 생성자!
BigDecimal b = new BigDecimal("0.2");
System.out.println(a.add(b));           // 0.3 (정확)
```

`new BigDecimal(0.1)`처럼 double을 넣으면 이미 오차가 낀 값이 들어가 의미가 없습니다.
같은 문제의 JS 버전은 JS day03 자료형과 연산자 참고.

## 3. 더 나아가 알면 좋은 것

### 3-1. Scanner vs BufferedReader

`Scanner`는 내부적으로 정규식 파싱을 해서 느립니다. 코딩테스트 시간 초과의 단골 원인입니다.

```java
import java.io.*;

BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
int n = Integer.parseInt(br.readLine());
StringTokenizer st = new StringTokenizer(br.readLine());
```

### 3-2. try-with-resources

`Scanner`는 자원(resource)이라 닫아주는 게 원칙입니다.

```java
try (Scanner scan = new Scanner(System.in)) {
    // 사용
}   // 자동으로 close()
```

### 3-3. Text Block (Java 15+)

`practice1.java` 6번의 ASCII 아트처럼 이스케이프가 많은 문자열에 유용합니다.

```java
String art = """
    |\\_/|
    |q p|
    ( 0 )
    """;
```

### 3-4. `var` (Java 10+)

```java
var scan = new Scanner(System.in);   // Scanner로 타입 추론
```
지역 변수에 한해 가능합니다. 타입이 우변에서 명확할 때만 쓰는 게 좋습니다.

## 실습 파일

- `2026B_BE/src/day01/Exam1.java`, `Exam2.java`, `Exam3.java`
- `2026B_BE/src/Note/Java.txt` (자바 전 과정 종합 정리)

## 관련 노트

[[Java MOC]] · [[Java day02 타입 변환]] · JS day02 변수와 입출력 · [[KDT_2026 학습 지도]]
