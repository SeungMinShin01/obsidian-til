---
출처: Claude 분석
원본: KDT_2026/2026B_BE/src/day13/exam
작성일: 2026-08-19
tags: [학습, java]
---

# Java day13 — Object 클래스와 리플렉션

> 실습 파일: `day13/exam/exam1.java`(Object·Class·리플렉션), `test.java`(콘솔 화면 렌더링)
> 허브: [[Java MOC]] · 이전: [[Java day12 종합예제 JDBC DAO]]

day12까지는 내가 만든 클래스들(DTO·DAO·Controller)을 어떻게 조립하는지가 주제였다. day13은 방향이 반대다. **자바가 이미 만들어 둔 클래스(라이브러리)를 어떻게 쓰는가**, 그중에서도 모든 클래스의 조상인 `Object` 와 클래스 자신의 정보를 담은 `Class` 를 본다.

라이브러리는 다른 사람들이 만들어 둔 클래스·메소드의 집합이다. `Scanner`·`String`·`ArrayList` 도 전부 라이브러리이고, day12에서 `lib` 폴더에 넣은 MySQL 드라이버 jar도 라이브러리다.

## 1. 배운 내용

### 1-1. Object — 자바의 최상위 클래스

모든 클래스는 아무것도 쓰지 않아도 자동으로 `Object` 를 상속한다. 그래서 **어떤 자료든 `Object` 타입 변수에 담을 수 있다.**

```java
Object o1 = 3;              // 정수
Object o2 = 3.14;           // 실수
Object o3 = "유재석";        // 문자열
Object o4 = true;           // 논리
Object o5 = new int[3];     // 배열
Object o6 = new BoardDto(); // 내가 만든 클래스
```

이게 가능한 이유는 [[Java day10 상속과 다형성]] 에서 정리한 **업캐스팅**이다. 부모 타입 변수에 자식 객체를 담는 그 규칙이 최상위까지 올라간 형태다. 정리하면 `Object` 는 "모든 타입을 받아주는 그릇"이고, 제네릭이 없던 시절 컬렉션이 아무 타입이나 담을 수 있었던 것도 이 성질 덕분이다.

`o1 = 3` 처럼 기본타입을 참조타입 변수에 넣을 수 있는 건 자바가 `int` → `Integer` 로 자동 포장해 주기 때문이다(오토박싱). 기본타입 자체는 `Object` 의 자식이 아니지만, 대응하는 포장 클래스(Wrapper)가 있어서 경계를 넘어간다.

`Object` 가 물려주는 대표 메소드는 세 개다.

| 메소드 | 반환 | 하는 일 |
| --- | --- | --- |
| `toString()` | `String` | 객체를 문자열로 표현. 기본은 `클래스명@해시코드(16진수)` |
| `equals(Object)` | `boolean` | 객체 비교. 기본은 주소값 비교 |
| `hashCode()` | `int` | 객체를 식별하는 정수값 |

### 1-2. toString() — 출력할 때 몰래 불린다

```java
Object o5 = new int[3];
System.out.println(o5.toString());  // [I@5ecddf8f
System.out.println(o5);             // [I@5ecddf8f  ← 결과가 같다
```

`System.out.println(객체)` 는 내부에서 `toString()` 을 호출한다. 그래서 `.toString()` 은 생략할 수 있다. 기본 구현은 주소값 기반 문자열이라 사람이 읽을 정보가 없다.

여기서 오버라이딩의 쓸모가 나온다. `toString()` 을 재정의해 둔 클래스는 객체를 그냥 출력해도 **멤버변수 내용**이 보인다.

```java
Object o6 = new BoardDto();   // BoardDto에서 toString() 오버라이딩됨
System.out.println(o6);       // BoardDto [content=null, writer=null]
```

- DTO를 만들 때 `toString()` 을 오버라이딩해 두면 디버깅할 때 값을 눈으로 바로 확인할 수 있다 — [[Java day09 MVC 종합예제]] 의 DTO들이 그래서 `toString()` 을 갖고 있다
- 이클립스·VS Code는 `Source → Generate toString()` 으로 자동 생성할 수 있다
- `[I@...` 의 `[I` 는 "int 배열"이라는 뜻의 내부 표기다. 배열은 `toString()` 이 오버라이딩돼 있지 않아 내용이 아니라 주소가 나온다

### 1-3. equals()와 == — 주소 비교 vs 값 비교

```java
Object o6 = new BoardDto();
Object o7 = new BoardDto();
System.out.println(o6 == o7);        // false — 서로 다른 주소
System.out.println(o6.equals(o7));   // false — 오버라이딩 안 했으면 == 와 같은 결과
```

`Object` 의 기본 `equals()` 는 내부에서 `==` 를 그대로 쓴다. 즉 **오버라이딩하지 않으면 둘은 같은 동작**이다. `equals()` 가 "값 비교"가 되는 건 그 클래스가 재정의해 놨을 때뿐이다.

문자열이 대표 사례다.

```java
String str1 = "유재석";                  // 리터럴 — 상수 풀에 저장
String str2 = new String("유재석");      // new — 힙에 새 객체 생성

System.out.println(str1 == str2);        // false  (리터럴 vs 새 객체)
System.out.println(str1 == "유재석");     // true   (리터럴 == 리터럴, 같은 주소를 공유)
System.out.println(str2 == "유재석");     // false  (새 객체 vs 리터럴)
System.out.println(str2.equals("유재석"));// true   (내용 비교)
```

| 비교 방식 | 무엇을 보는가 |
| --- | --- |
| `==` | 참조타입이면 **주소값**, 기본타입이면 값 |
| `equals()` | 클래스가 재정의한 **내용** (String은 문자 배열이 같은지) |

- 같은 리터럴 문자열은 자바가 상수 풀(String Pool)에 하나만 만들어 두고 공유한다. 그래서 리터럴끼리는 `==` 가 `true` 다
- `new String(...)` 은 내용이 같아도 매번 새 객체라 주소가 다르다
- **문자열 비교는 항상 `equals()`** 로 쓴다. `==` 로 맞는 결과가 나오는 경우가 있어서 오히려 실수가 늦게 드러난다 — [[Java day03 연산자]] 에서 정리한 그 규칙이 왜 그런지가 여기서 설명된다

### 1-4. hashCode() — 객체를 식별하는 정수

```java
System.out.println(o6.hashCode());        // 729864207
System.out.println(o7.hashCode());        // 984849465  ← 다른 객체라 다른 값
System.out.println(str1.hashCode());      // 50621969
System.out.println("유재석".hashCode());   // 50621969   ← 내용이 같으면 같은 값
```

`hashCode()` 는 객체를 정수 하나로 요약한 값이다. 기본 구현은 주소를 기반으로 하므로 객체마다 다르고, `toString()` 이 찍는 `@5ecddf8f` 는 이 값을 16진수(0~9, a~f)로 표현한 것이다.

String처럼 `equals()` 를 오버라이딩한 클래스는 `hashCode()` 도 함께 재정의해서, **내용이 같으면 해시값도 같도록** 맞춰 둔다. 정리하면 `equals()` 는 "같은가?"를 정확히 판정하고, `hashCode()` 는 "같은 후보끼리 빠르게 모으는" 역할이다.

### 1-5. 기본타입과 참조타입 다시 정리

`Object` 를 배우고 나면 자료형 지도가 두 갈래로 정리된다.

| 구분 | 종류 | 변수에 담기는 것 |
| --- | --- | --- |
| **기본타입** | `byte` `short` `int` `long` `float` `double` `char` `boolean` | 값(리터럴 = 상수) 자체 |
| **참조타입** | 클래스(`String`·`Scanner`·`~Dto`), 인터페이스(`Connection` 등), 배열 `[]` | 주소값 |

- 참조타입만 `Object` 의 자식이고, `==` 가 주소 비교가 되는 것도 참조타입뿐이다
- 인터페이스 타입 변수(`Connection conn = ...`)도 참조타입이라 결국 구현체 객체의 주소를 담는다 — [[Java day11 인터페이스]] 의 규격·구현 분리가 타입 관점에서는 이 자리다

### 1-6. Class 클래스 — 클래스의 정보를 담은 클래스

`Class` 는 멤버변수·메소드·생성자 같은 **클래스 자신의 정보**를 담고 있는 클래스다. 얻는 방법이 두 가지다.

```java
// ① 객체에서 얻기 — getClass()
String obj1 = new String();
Class c1 = obj1.getClass();
System.out.println(c1);   // class java.lang.String  (패키지명 + 클래스명)

// ② 이름(문자열)으로 얻기 — Class.forName()
try {
    Class.forName("java.lang.String");
} catch (ClassNotFoundException e) {
    System.out.println(e);
}
```

`getClass()` 도 `Object` 가 물려준 메소드라 모든 객체에서 쓸 수 있다. 출력이 `class java.lang.String` 인 것에서, 그 객체의 실제 타입과 소속 패키지를 런타임에 확인할 수 있다.

### 1-7. 리플렉션 — 실행 중에 클래스를 읽어 오기

`Class.forName("패키지명.클래스명")` 이 하는 일이 **리플렉션**이다. 보통은 컴파일할 때 어떤 클래스를 쓸지 코드에 박혀 있지만, 리플렉션은 **최초 실행(컴파일) 시점에 객체를 로드·생성하지 않고 실행 도중에 문자열로 찾아 로드**한다.

```java
Class.forName("com.mysql.cj.jdbc.Driver");   // day12에서 이미 쓴 그 코드
```

- 클래스 이름이 문자열이라 컴파일러가 존재를 검사할 수 없다. 그래서 없을 때를 대비한 `ClassNotFoundException` 처리가 **필수(checked 예외)** 다 — [[Java day12 예외 처리와 JDBC]] 에서 잡던 그 예외의 정체가 이것이다
- 어떤 DB를 쓸지 코드가 아니라 설정 문자열로 정할 수 있는 이유가 여기 있다. MySQL이면 `com.mysql.cj.jdbc.Driver`, Oracle이면 다른 문자열로 바꾸면 끝이다
- 정리하면 리플렉션은 **"무엇을 쓸지 결정하는 시점을 컴파일 → 실행으로 미루는" 장치**다

### 1-8. 콘솔 화면 그리기 연습 (test.java)

같은 day13 폴더에 좌석 현황판을 콘솔에 그리는 연습 코드가 있다. 문법 자체는 새롭지 않지만, 지금까지 배운 것들이 화면 출력이라는 목적으로 모인 형태다.

```java
System.setOut(new PrintStream(System.out, true, StandardCharsets.UTF_8));  // 콘솔 인코딩 UTF-8 고정
System.out.println("=".repeat(70));    // 같은 문자 70번 반복
```

| 쓰인 것 | 역할 |
| --- | --- |
| `String.repeat(n)` | 문자열을 n번 이어 붙인다. 구분선·테두리를 만들 때 |
| `StringBuilder` | 한 줄을 조각조각 `append()` 해서 완성한 뒤 한 번에 출력 |
| `Deque<String>` / `ArrayDeque` | 최근 로그를 담는 자료구조 ([[Java day09 ArrayList]] 의 컬렉션 가족) |
| `List.of(...)` | 값을 나열해 바로 리스트를 만드는 팩토리 메소드 |
| `switch` 표현식 (`case "X" -> ...`) | 조건에 따라 라벨 문자열을 **반환**한다 |
| 이중 for | 바깥은 줄(line), 안쪽은 좌석(seat) — 격자 출력의 기본형 |

```java
return switch (s.getMealStatus()) {
    case "WAITING" -> "[대기중]";
    case "READY"   -> "[서빙완]";
    default        -> "[ ? ]";
};
```

- [[Java day04 제어문과 배열]] 의 `switch` 문이 값을 **돌려주는 표현식**으로 확장된 형태다. `break` 없이 `->` 로 쓰고, 결과를 바로 `return` 하거나 변수에 담을 수 있다
- 한글은 콘솔에서 두 칸을 차지하므로, 칸을 맞추려면 글자 폭을 세어(`0xAC00~0xD7A3` 범위면 2) 좌우 공백을 나눠 붙인다. 문자를 코드값(유니코드)으로 비교할 수 있다는 [[Java day01 자바 구조와 자료형]] 의 `char` 성질이 쓰이는 자리다
- 파일 맨 아래의 `class Seat` 처럼 **`public` 이 아닌 클래스는 한 파일에 여러 개** 둘 수 있다. `public` 클래스는 파일명과 이름이 같아야 하므로 파일당 하나뿐이다
- 화면(콘솔 출력)과 데이터(`Seat` 객체 배열)를 분리해 `render(seats, logs)` 로 넘기는 구조라, [[Java day09 MVC 종합예제]] 의 View 계층이 하는 일과 모양이 같다

## 2. 추가로 알면 좋은 활용법

### 2-1. equals()와 hashCode()는 짝으로 오버라이딩한다

DTO를 컬렉션에 담고 "내용이 같으면 같은 객체"로 다루고 싶으면 둘을 함께 재정의한다.

```java
@Override
public boolean equals(Object obj) {
    if (this == obj) return true;
    if (!(obj instanceof BoardDto)) return false;
    BoardDto other = (BoardDto) obj;
    return this.no == other.no;
}

@Override
public int hashCode() {
    return Objects.hash(no);
}
```

`equals()` 만 재정의하고 `hashCode()` 를 두면 `HashSet`·`HashMap` 에서 같은 값인데도 다른 자리에 들어가 중복이 생긴다. `instanceof` 로 타입을 먼저 확인하는 건 [[Java day10 상속과 다형성]] 의 다운캐스팅 안전장치와 같은 패턴이다.

### 2-2. null에 강한 비교 관용구

```java
Objects.equals(a, b);            // 둘 중 하나가 null이어도 예외 없이 비교
"admin".equals(입력값);           // 리터럴을 앞에 두면 입력값이 null이어도 안전
입력값.equalsIgnoreCase("ADMIN"); // 대소문자 무시 비교
```

`입력값.equals("admin")` 은 `입력값` 이 `null` 이면 `NullPointerException` 이 난다. 리터럴을 앞에 두는 습관 하나로 이 계열의 오류를 상당히 줄일 수 있다.

### 2-3. 문자열을 이어 붙일 땐 StringBuilder

`String` 은 한 번 만들면 바뀌지 않는(불변) 타입이라, `str += "a"` 를 반복하면 매번 새 객체가 생긴다. 반복문 안에서 문자열을 조립할 때는 `StringBuilder.append()` 를 쓰고 마지막에 `toString()` 으로 꺼낸다.

```java
StringBuilder sb = new StringBuilder();
for (String s : list) sb.append(s).append(", ");
System.out.println(sb);   // println이 toString()을 자동 호출
```

`System.out.println(sb)` 로 그냥 출력해도 되는 이유가 1-2의 `toString()` 이다.

### 2-4. 자주 쓰는 Object 계열 메소드 정리

| 표현 | 결과 |
| --- | --- |
| `obj.getClass().getName()` | 패키지 포함 클래스명 문자열 |
| `obj.getClass().getSimpleName()` | 패키지 뺀 클래스명 |
| `String.valueOf(obj)` | `null` 이어도 `"null"` 문자열을 돌려주는 안전한 문자열 변환 |
| `Objects.toString(obj, "기본값")` | `null` 일 때 대체 문자열 지정 |

## 3. 더 나아가 알면 좋은 것

### 3-1. 리플렉션이 실무에서 쓰이는 곳

리플렉션은 "클래스 이름을 설정으로 받는" 모든 도구의 밑바탕이다.

- **JDBC 드라이버 로드** — 어떤 DB를 쓸지 문자열로 지정 ([[Java day12 예외 처리와 JDBC]])
- **스프링의 의존성 주입(DI)** — 어떤 구현체를 넣을지 설정에서 읽어 실행 중에 객체 생성. [[Java day11 인터페이스]] 의 "규격만 보고 구현은 갈아끼운다"를 프레임워크가 자동으로 해 주는 형태다
- **JSON ↔ 객체 변환(Jackson 등)** — 클래스의 필드 목록을 읽어 자동으로 값을 채운다
- **JUnit** — `@Test` 가 붙은 메소드를 찾아 실행한다

`Class` 객체에서는 `getDeclaredFields()`·`getMethods()`·`newInstance()` 로 필드·메소드 목록을 읽고 객체까지 만들 수 있다. 다만 컴파일러의 검사를 우회하는 방식이라, 직접 쓰기보다는 **프레임워크가 어떻게 동작하는지 이해하는 열쇠**로 알아 두는 편이 낫다.

### 3-2. Object 하나로 받는 방식의 한계 — 제네릭

`Object` 로 아무거나 받으면 꺼낼 때 매번 형변환해야 하고, 잘못된 타입을 넣어도 컴파일 시점에 걸리지 않는다.

```java
Object o = "문자열";
int n = (int) o;   // 컴파일은 통과, 실행 중 ClassCastException
```

이 문제를 컴파일 시점으로 끌어올린 게 제네릭(`<T>`)이다. [[Java day11 종합예제 인터페이스 DAO]] 에서 DAO 규격을 `<T>` 로 잡은 이유가 여기 있다.

### 3-3. record — DTO를 한 줄로

`toString()`·`equals()`·`hashCode()`·getter를 매번 만드는 게 DTO의 반복 작업인데, 자바 16부터는 `record` 가 이걸 자동으로 만들어 준다.

```java
public record BoardDto(int no, String content, String writer) { }
```

값만 담는 클래스라면 이 한 줄이 지금까지 쓰던 DTO와 같은 일을 한다.

### 3-4. 다음에 볼 키워드

- `Objects` 유틸 클래스 — `equals`·`hash`·`requireNonNull`
- `HashMap`·`HashSet` 의 동작 원리 (해시 버킷과 `hashCode`)
- 어노테이션(`@Override`·`@Test`)과 리플렉션의 조합
- `String` vs `StringBuilder` vs `StringBuffer`
- 래퍼 클래스와 오토박싱·언박싱
- 얕은 복사·깊은 복사, `clone()`

## 실습 파일

- `2026B_BE/src/day13/exam/exam1.java` (Object 최상위 클래스, toString·equals·hashCode, 문자열 리터럴 비교, Class·getClass·Class.forName 리플렉션)
- `2026B_BE/src/day13/exam/test.java` (콘솔 좌석 현황판 렌더링 — StringBuilder, Deque, switch 표현식, 한글 폭 계산)

## 관련 노트

[[Java MOC]] · [[Java day12 종합예제 JDBC DAO]] · [[Java day12 예외 처리와 JDBC]] · [[Java day11 인터페이스]] · [[Java day11 종합예제 인터페이스 DAO]] · [[Java day10 상속과 다형성]] · [[Java day09 ArrayList]] · [[Java day09 MVC 종합예제]] · [[Java day04 제어문과 배열]] · [[Java day03 연산자]] · [[Java day01 자바 구조와 자료형]] · [[JS day03 자료형과 연산자]] · [[KDT_2026 학습 지도]]
