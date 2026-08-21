---
출처: Claude 분석
작성일: 2026-08-21
tags: [코드정리]
---

# JAVA 기본 문법

> 상위: [[JAVA]]

## 기본 구조와 main

```java
package day01;

public class Exam1 {
    public static void main(String[] args) {
        System.out.println("안녕");
    }
}
```

- `package`는 이 파일이 속한 폴더 선언이고 파일 맨 위에 온다
- 클래스명은 파일명과 같고 첫 글자 대문자다. 자바의 최소 컴파일 단위다
- `main`이 실행 시작점이다. 선언은 클래스 안 어디든 되지만 실행문은 main(또는 메소드) 안에만 쓸 수 있다
- 한 문장의 끝은 `;`다. 컴파일러가 이 단위로 끊어 읽는다

## System.out — 출력

```java
System.out.println("값");
System.out.print("값");
System.out.printf("%s는 %d점, 평균 %.2f %n", "유재석", 90, 88.567);
```

- `println`은 출력 후 줄바꿈, `print`는 줄바꿈 없음, `printf`는 서식 출력이다
- 서식: `%s` 문자열, `%d` 정수, `%f` 실수, `%b` 논리값, `%n` 줄바꿈
- 폭·정렬: `%6d` 오른쪽 정렬, `%-6d` 왼쪽 정렬, `%06d` 앞을 0으로, `%,d` 천 단위 콤마, `%5.2f` 소수점 2자리
- 이스케이프 문자는 `\n` 줄바꿈, `\t` 탭, `\"`, `\\`

## Scanner — 입력

```java
import java.util.Scanner;

Scanner scan = new Scanner(System.in);
int i = scan.nextInt();
double d = scan.nextDouble();
String word = scan.next();
String line = scan.nextLine();
char c = scan.next().charAt(0);
```

- `next()`는 공백·엔터 전까지 한 단어, `nextLine()`은 한 줄 전체를 읽는다
- 함정: `nextInt()` 뒤에 `nextLine()`을 부르면 버퍼에 남은 엔터를 읽어 빈 문자열이 된다. 사이에 `scan.nextLine();`을 한 번 넣어 버퍼를 비운다
- ※ 코딩테스트에서 입력이 많으면 `BufferedReader`가 훨씬 빠르다: `new BufferedReader(new InputStreamReader(System.in)).readLine()`

## 자료형과 형변환

```java
boolean b = true;
char c = 'A';
String s = "abc";
int n = 2000000000;
long l = 20000000000L;
double d = 0.123;
float f = 0.1F;
```

- 기본 타입 8개(boolean·char·byte·short·int·long·float·double)는 값을 그대로 저장하고, 참조 타입(String·배열·클래스·인터페이스)은 주소를 저장한다
- 정수 리터럴의 기본은 `int`, 실수는 `double`이다. 그래서 21억 넘는 정수엔 `L`, float엔 `F`를 붙여야 한다
- 형변환은 작은→큰 타입은 자동, 큰→작은은 `(byte) n`처럼 강제다. `(int) 3.9`는 3이 된다(버림)
- 정수끼리 나누면 정수 나눗셈이다: `5 / 2`는 2. 소수점이 필요하면 `(double) 5 / 2`
- ※ 정밀한 실수 계산은 `BigDecimal`을 쓴다: `new BigDecimal("0.1").add(new BigDecimal("0.2"))` → 정확히 0.3. 반드시 문자열 생성자로 만든다

## 연산자

```java
int r = 7 % 3;
boolean ok = a > 0 && b > 0;
String grade = score >= 60 ? "합격" : "불합격";
```

- 산술 `+ - * / %`, 대입 `= += -= *= /=`, 증감 `++ --`, 비교 `> < >= <= == !=`, 논리 `&& || !`, 삼항 `조건 ? 참 : 거짓`
- `%`는 나머지다. 짝수 판별 `n % 2 == 0`, 배열 순환 `i % arr.length`, 초→분·초 분리 `sec % 60`에 자주 쓴다
- 전위 `++a`는 먼저 증가시키고 쓰고, 후위 `a++`는 쓰고 나서 증가한다. 단독 문장으로는 차이가 없다
- 참조 타입에 `==`를 쓰면 주소 비교다. 문자열 값 비교는 반드시 `.equals()`: `"admin".equals(id)` — 리터럴을 앞에 두면 id가 null이어도 안전하다
- `&&`는 앞이 false면 뒤를 아예 실행하지 않는다(단축 평가). 그래서 null 검사를 앞에 둔다: `if (s != null && s.length() > 0)`
- 우선순위는 외우지 말고 괄호를 쓰는 편이 읽기 좋다

## if · switch — 조건문

```java
if (temp <= 10) {
    System.out.println("외투");
} else if (temp <= 30) {
    System.out.println("긴팔");
} else {
    System.out.println("반팔");
}

switch (grade) {
    case 'A':
        System.out.println("우수");
        break;
    default:
        break;
}
```

- 실행문이 1개면 `{}`를 생략할 수 있지만 붙이는 습관이 안전하다
- `else if` 계단은 **큰 값(좁은 조건)부터** 검사한다. 순서를 뒤집으면 넓은 조건이 다 먹어버린다
- `switch`의 각 case 끝에 `break`가 없으면 아래 case로 흘러내린다(fall-through)
- switch가 받는 타입: byte·short·char·int·String·enum. long·double·boolean은 안 된다
- ※ switch 표현식(Java 14+)은 break가 필요 없다: `String r = switch (g) { case 'A' -> "우수"; default -> "재시험"; };`

## for · while — 반복문

```java
for (int i = 0; i < 10; i++) { }

while (count < 10) { count++; }

for (;;) { }

for (String name : names) { }
```

- for는 초기값 → 조건 → 실행문 → 증감식 순서로 돈다
- `for (;;)`는 무한루프다(`while (true)`와 같다). 빠져나오는 통로가 break뿐이니 종료 조건을 먼저 써 둔다
- 향상된 for문(`:`)은 인덱스가 필요 없을 때 쓴다. 콜론 오른쪽 배열·리스트의 요소가 왼쪽 변수에 하나씩 들어온다
- `break`는 가장 가까운 반복문 탈출, `continue`는 다음 반복으로 건너뛴다
- 중첩 반복문을 한 번에 빠져나오려면 라벨을 쓴다: `outer: for(...) { for(...) { break outer; } }`
- 순회 조건은 `i < length`다. `i <= length`는 언제나 범위를 벗어난다

## 관련 노트

[[JAVA]]
