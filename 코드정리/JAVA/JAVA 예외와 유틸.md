---
출처: Claude 분석
작성일: 2026-08-21
tags: [코드정리]
---

# JAVA 예외와 유틸

> 상위: [[JAVA]]
> 세부: [[JAVA 사용자 정의 예외]] · [[JAVA 날짜와 포맷 심화]] · [[JAVA 파일 입출력]]

## try-catch ※

```java
try {
    int r = 10 / n;
} catch (ArithmeticException e) {
    System.out.println("0으로 나눌 수 없습니다: " + e.getMessage());
} finally {
    System.out.println("항상 실행");
}
```

- 위험한 코드를 try에 넣고, 터졌을 때의 처리를 catch에 쓴다. 프로그램이 죽는 대신 안내하고 계속 돌 수 있다
- `e.getMessage()`가 예외의 설명 문자열이다
- finally는 성공하든 실패하든 항상 실행된다. 자원 정리(닫기)가 이 자리다
- catch를 여러 개 두면 예외 종류별로 다르게 처리한다. 구체적인 예외를 위에, `Exception`(전부 잡기)을 아래에 둔다

## throw — 예외 던지기 ※

```java
if (qty <= 0) {
    throw new IllegalArgumentException("수량은 1 이상이어야 합니다.");
}
```

- 잘못된 상황을 발견한 쪽에서 예외를 만들어 던진다. 받는 쪽(호출부)이 try-catch로 처리한다
- 생성자나 setter에서 던지면 잘못된 객체·값이 아예 생기지 않는다

## try-with-resources ※

```java
try (Scanner scan = new Scanner(System.in)) {
    String s = scan.nextLine();
}
```

- 괄호 안에서 만든 자원은 블록이 끝나면 자동으로 `close()`된다. Scanner·JDBC의 Connection·PreparedStatement·ResultSet이 전부 이 대상이다
- 닫기를 잊어 생기는 자원 누수를 문법으로 막는다

## 자주 만나는 예외

```
NullPointerException              null인 변수에 . 으로 접근
ArrayIndexOutOfBoundsException    배열·리스트 범위 밖 인덱스
NumberFormatException             parseInt에 숫자 아닌 문자열
ClassCastException                 잘못된 다운캐스팅
ArithmeticException               정수를 0으로 나눔
InputMismatchException            nextInt에 문자 입력
ConcurrentModificationException   향상된 for 안에서 remove
```

- 예외 이름이 곧 원인 설명이다. 콘솔 스택트레이스의 첫 줄(예외명)과 내 코드가 나온 줄 번호부터 읽는다

## Math · 숫자

```java
Math.max(a, b);
Math.min(a, b);
Math.abs(x);
Math.random();
int dice = (int) (Math.random() * 6) + 1;
```

- `max`/`min` 큰·작은 값, `abs` 절댓값
- `Math.random()`은 0 이상 1 미만 실수다. n가지 정수로 만들려면 `(int) (Math.random() * n) + 시작값` 공식을 쓴다

## LocalDate — 날짜 ※

```java
import java.time.LocalDate;
import java.time.temporal.ChronoUnit;

LocalDate today = LocalDate.now();
LocalDate due = today.plusDays(14);
boolean late = today.isAfter(due);
long overdue = ChronoUnit.DAYS.between(due, today);
```

- `now()` 오늘, `plusDays/plusMonths` 더하기, `isAfter/isBefore` 앞뒤 비교
- 두 날짜의 차이는 `ChronoUnit.DAYS.between(앞, 뒤)`다. 대여 시스템의 반납예정일·연체일 계산이 이 두 줄이다
- 문자열 변환: `LocalDate.parse("2026-08-21")` ↔ `date.toString()`

