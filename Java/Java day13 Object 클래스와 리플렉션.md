---
출처: Claude 분석
원본: KDT_2026/2026B_BE/src/day13/exam, day13/practice
작성일: 2026-08-19
tags: [학습, java]
---

# Java day13 — Object 클래스와 리플렉션

> 실습 파일: `day13/exam/exam1.java`(Object·Class·리플렉션), `exam2.java`(래퍼 클래스·타입 변환·날짜/시간), `exam3.java`(String 클래스·문자 코드값), `exam4.java`(난수·UUID), `test.java`(콘솔 화면 렌더링), `day13/practice/practice14.java`(문자열 주차 데이터 실습)
> 허브: [[Java MOC]] · 이전: [[Java day12 종합예제 JDBC DAO]]

day12까지는 내가 만든 클래스들(DTO·DAO·Controller)을 어떻게 조립하는지가 주제였다. day13은 방향이 반대다. **자바가 이미 만들어 둔 클래스(라이브러리)를 어떻게 쓰는가**, 그중에서도 모든 클래스의 조상인 `Object` 와 클래스 자신의 정보를 담은 `Class` 를 본다.

라이브러리는 다른 사람들이 만들어 둔 클래스·메소드의 집합이다. `Scanner`·`String`·`ArrayList` 도 전부 라이브러리이고, day12에서 `lib` 폴더에 넣은 MySQL 드라이버 jar도 라이브러리다.

같은 흐름에서 **기본타입을 객체로 감싸는 래퍼 클래스**, **날짜·시간을 다루는 `java.time` 패키지**, **문자열을 다루는 `String` 클래스**, **난수를 만드는 `Random`·`UUID`** 도 함께 본다. 전부 "이미 만들어져 있으니 가져다 쓰는" 자바 표준 라이브러리다.

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

### 1-9. 래퍼 클래스 — 기본타입을 객체로 감싸기

1-5에서 갈라 둔 두 갈래를 이어 주는 장치가 **래퍼(Wrapper) 클래스**다. 출발점은 단순하다. **기본타입은 값만 있고 기능(메소드)이 없다.** `int` 변수에는 `.toString()` 을 붙일 수 없다.

```java
int value1 = 100;         // 기본타입 — 값만 있다
Integer value2 = 100;     // 참조타입 — 메소드를 쓸 수 있다
System.out.println(value2.toString());
```

그래서 기능이 필요하면 대응하는 참조타입으로 바꿔서 쓴다. 기본타입 8개에는 각각 짝이 되는 래퍼 클래스가 있다.

| 기본타입 | 래퍼 클래스 | 기본타입 | 래퍼 클래스 |
| --- | --- | --- | --- |
| `byte` | `Byte` | `float` | `Float` |
| `short` | `Short` | `double` | `Double` |
| `int` | **`Integer`** | `char` | **`Character`** |
| `long` | `Long` | `boolean` | `Boolean` |

이름은 대부분 첫 글자를 대문자로 바꾼 형태이고, `int` → `Integer`, `char` → `Character` 둘만 이름이 다르다.

두 세계를 오가는 변환은 자바가 알아서 해 준다.

```java
int value3 = value2;      // Integer(참조) → int(기본)   <언박싱>
Integer value4 = value1;  // int(기본) → Integer(참조)   <오토박싱>
```

- **오토박싱**: 기본타입 → 래퍼 객체로 자동 포장
- **언박싱**: 래퍼 객체 → 기본타입으로 자동 개봉

1-1에서 `Object o1 = 3;` 이 되던 이유가 정확히 이 오토박싱이다. `3` 이 `Integer` 로 포장되고, `Integer` 는 참조타입이라 `Object` 의 자식이니 대입이 성립한다. [[Java day09 ArrayList]] 에서 `ArrayList<Integer>` 처럼 컬렉션의 제네릭에 `int` 가 아니라 `Integer` 를 쓰는 것도 같은 이유다 — 컬렉션은 객체만 담을 수 있다.

### 1-10. 타입 변환 — 문자열과 숫자 사이

프로그램 바깥에서 들어오는 데이터는 거의 다 **문자열**이다. csv·엑셀·API 응답·JSON·XML, [[Java day01 자바 구조와 자료형]] 에서 쓴 `Scanner` 의 키보드 입력까지 전부 그렇다. 그래서 문자열 ↔ 숫자 변환은 어느 프로그램에나 나온다.

**문자열 → 기본타입**은 래퍼 클래스의 `parseXXX()` 가 담당한다. `XXXX.parseXXX(문자열)` 꼴로 외우면 편하다.

```java
int value5     = Integer.parseInt("100");        // "100" → 100
double value6  = Double.parseDouble("3.14");     // "3.14" → 3.14
boolean value7 = Boolean.parseBoolean("true");   // "true" → true
```

**기본타입 → 문자열**은 두 가지 방법이 있다.

```java
String s1 = 100 + "";              // 빈 문자열을 더한다
String s2 = String.valueOf(100);   // 뜻이 분명한 쪽
```

`100 + ""` 는 짧지만 "왜 빈 문자열을 더하지?"를 한 번 생각해야 읽힌다. `String.valueOf()` 는 하는 일이 이름에 드러나고, 2-4에서 정리한 대로 `null` 이 들어와도 `"null"` 을 돌려주므로 예외가 나지 않는다.

`parseInt()` 는 정적(static) 메소드라 객체를 만들지 않고 `클래스명.메소드()` 로 바로 부른다 — [[Java day08 접근제한자와 static]] 의 static 규칙이 라이브러리에서 쓰이는 모습이다.

[[Java day02 타입 변환]] 에서 본 `(int)` 형변환과는 층이 다르다는 점도 정리해 둔다. 캐스팅은 **기본타입끼리** 값의 그릇을 바꾸는 문법이고, `parseInt()` 는 **문자열을 읽어 숫자로 해석하는** 메소드다. `(int)"100"` 은 아예 컴파일되지 않는다.

### 1-11. 날짜·시간 클래스 — java.time

날짜와 시간은 직접 계산하면 윤년·월말·자정 넘김 같은 예외가 끝없이 나온다. 자바는 `java.time` 패키지에 이걸 전부 처리해 둔 클래스를 준비해 놨다.

| 클래스 | 담는 것 | 출력 예 |
| --- | --- | --- |
| `LocalDate` | 날짜만 | `2026-08-19` |
| `LocalTime` | 시각만 | `11:07:30.123` |
| `LocalDateTime` | 날짜 + 시각 | `2026-08-19T11:07:30` |

**현재 시각 가져오기 — `now()`**

```java
LocalDate     localDate     = LocalDate.now();
LocalTime     localTime     = LocalTime.now();
LocalDateTime localDateTime = LocalDateTime.now();
```

`now()` 앞에 `new` 가 없다. **정적 메소드**라 클래스 이름으로 바로 부르고, 객체는 메소드 안에서 만들어 돌려준다. 생성자를 감춰 두고 이런 메소드로만 객체를 만들게 하는 방식을 팩토리 메소드라고 부른다.

**정해진 날짜/시각 만들기 — `of()`**

```java
LocalDateTime dt = LocalDateTime.of(2026, 8, 19, 11, 7, 30);  // 연,월,일,시,분,초
```

`of()` 는 매개변수 개수에 따라 여러 벌이 준비돼 있다 — `of(연,월,일)`, `of(연,월,일,시,분)`, `of(연,월,일,시,분,초)`. 같은 이름에 매개변수만 다른 [[Java day07 메소드와 미니프로젝트]] 의 **오버로딩**이다.

**보기 좋은 형식으로 출력 — `DateTimeFormatter`**

기본 출력은 `2026-08-19T11:07:30` 처럼 중간에 `T` 가 들어간 국제 표준 형식이라 화면에 그대로 쓰기엔 어색하다. 원하는 형식을 패턴 문자열로 정해서 바꾼다.

```java
DateTimeFormatter formatter = DateTimeFormatter.ofPattern("yyyy년 MM월 dd일 HH시 mm분 ss초");
System.out.println(dt.format(formatter));   // 2026년 08월 19일 11시 07분 30초
```

패턴 문자는 대소문자를 구분한다. 이 부분이 가장 헷갈리는 자리라 표로 둔다.

| 문자 | 뜻 | 문자 | 뜻 |
| --- | --- | --- | --- |
| `yyyy` / `yy` | 연도 4자리 / 2자리 | `HH` | 시각 (0~23) |
| `MM` | **월** (대문자 M) | `hh` | 시각 (1~12, 오전/오후) |
| `dd` | 일 | `mm` | **분** (소문자 m) |
| `EEEE` | 요일 (월요일) | `ss` | 초 |

- `M` 은 월, `m` 은 분이다. 대소문자를 바꿔 쓰면 엉뚱한 숫자가 찍히는데 예외가 나지 않아서 눈으로 확인하기 전까지 모른다
- 글자 수가 자릿수다. `M` 은 `8`, `MM` 은 `08`
- 한글이나 기호는 패턴에 그대로 넣으면 그대로 출력된다

**날짜 계산 — `plusXXX()` / `minusXXX()`**

```java
LocalDateTime result1 = dt.plusDays(10);   // 10일 뒤
```

`plusDays`·`plusMonths`·`plusYears`·`plusHours`·`plusMinutes` 가 있고, 반대 방향은 `minusXXX()` 다. 월말을 넘어가면 알아서 다음 달로 넘어간다.

여기서 중요한 성질이 하나 있다. **`java.time` 의 객체는 불변(immutable)이다.** `dt.plusDays(10)` 은 `dt` 자신을 바꾸지 않고 **계산 결과를 담은 새 객체**를 돌려준다. 그래서 결과를 변수에 받지 않으면 계산은 그냥 사라진다. `String` 이 불변이라 `str.toUpperCase()` 의 결과를 받아야 하는 것과 같은 구조다.

**값 하나만 꺼내기 — `getXXX()`**

```java
dt.getHour();         // 11
dt.getMonthValue();   // 8      — 정수
dt.getMonth();        // AUGUST — 영문 이름(열거형)
```

`getMonth()` 와 `getMonthValue()` 가 갈라져 있는 게 포인트다. 화면에 숫자로 찍을 거면 `getMonthValue()`, 이름이 필요하면 `getMonth()` 를 쓴다. 같은 계열로 `getYear`·`getDayOfMonth`·`getDayOfWeek`·`getMinute`·`getSecond` 가 있다.

[[Java day11 종합예제 인터페이스 DAO]] 에서 게시글에 작성일을 붙일 때 쓴 자리가 이 클래스들이다. 등록 시각을 `LocalDateTime.now()` 로 찍고, 목록에 보여 줄 때 `DateTimeFormatter` 로 다듬는 흐름이 가장 흔한 조합이다.

### 1-12. String 클래스 — 문자열은 배열이다

`String` 도 자바가 만들어 둔 클래스이고, 안에 **문자 배열(`char[]`)을 멤버변수로 갖고 있다.** 그래서 문자열을 다루는 메소드가 배열을 다루듯 인덱스로 움직인다.

```java
char   str1 = '유';                    // char는 작은따옴표, 1글자만
char[] str2 = { '유', '재', '석' };     // char 배열
String str3 = "유재석";                 // String 클래스 — 내부에 char 배열을 가짐
```

**문자와 코드값은 서로 바꿔 쓸 수 있다.** `char` 는 사실 정수 하나이고, 그 정수가 아스키코드(영문·일부 특수문자)와 유니코드(여러 언어) 표의 자리 번호다.

```java
char str4 = 65;
System.out.println(str4);              // A

char[] str5 = { 74, 65, 86, 65 };
System.out.println(str5);              // JAVA

char str6 = '유';
System.out.println((int) str6);        // 50976
```

- 숫자를 `char` 변수에 넣으면 그 번호의 문자로 해석된다. `(int)` 를 붙이면 반대로 코드값이 나온다 — [[Java day02 타입 변환]] 의 캐스팅이 문자에 적용된 자리다
- `char[]` 를 `println()` 에 넣으면 주소가 아니라 **글자들이 이어져 출력**된다. `println()` 이 `char[]` 전용으로 오버로딩돼 있기 때문이고, 1-2에서 `int[]` 가 `[I@...` 로 찍히던 것과 대비된다
- 1-8의 한글 폭 계산에서 `c >= 0xAC00 && c <= 0xD7A3` 로 비교하던 것도 이 성질이다. 한글 음절이 유니코드에서 연속된 구간을 차지하고 있어 범위 비교가 성립한다

**문자열 비교는 1-3에서 정리한 규칙 그대로다.**

```java
System.out.println("유재석".equals("유재석"));              // true
System.out.println("유재석" == "유재석");                   // true  (리터럴끼리는 같은 주소)
System.out.println(new String("유재석").equals("유재석"));   // true
System.out.println(new String("유재석") == "유재석");        // false (새 객체 vs 리터럴)
```

**자주 쓰는 String 메소드**를 표로 모아 둔다. 전부 원본을 바꾸지 않고 **새 문자열을 돌려준다**(`String` 은 불변).

| 메소드 | 하는 일 | 예 |
| --- | --- | --- |
| `concat(문자열)` | 뒤에 이어 붙인 문자열 반환 | `"자바".concat("프로그래밍")` → `자바프로그래밍` |
| `length()` | 문자 개수 | `"자바프로그래밍".length()` → `7` |
| `charAt(인덱스)` | 문자 1개 추출 | `"자바프로그래밍".charAt(2)` → `프` |
| `replace(기존, 새것)` | 있으면 치환해서 반환 | `"자바프로그래밍".replace("자바","JAVA")` → `JAVA프로그래밍` |
| `substring(시작)` | 시작 인덱스부터 끝까지 잘라 반환 | `"010339-2140421".substring(6)` → `-2140421` |
| `substring(시작, 끝)` | 시작부터 **끝 직전까지** | `.substring(0, 6)` → `010339` |
| `split(구분문자)` | 구분자로 쪼개 **배열** 반환 | `.split("-")` → `["010339", "2140421"]` |
| `indexOf(문자열)` | 처음 나오는 위치, 없으면 `-1` | `"자바 프로그래밍 언어".indexOf("프로")` → `3` |
| `contains(문자열)` | 포함 여부 `boolean` | `.contains("프로")` → `true` |
| `getBytes()` | 문자들을 바이트 배열로 | `"ABC".getBytes()` → `[65, 66, 67]` |

- `length()` 는 **메소드**다. 배열의 `length` 는 괄호 없는 필드라 모양이 다르다 — [[Java day04 제어문과 배열]] 과 함께 헷갈리기 쉬운 자리다
- 인덱스는 0부터 세고, `substring(시작, 끝)` 의 끝은 포함되지 않는다. 그래서 `substring(0, 6)` 이 6글자다
- `split()` 이 돌려주는 건 배열이라 그대로 출력하면 `[Ljava.lang.String;@...` 처럼 주소가 나온다. 원소를 꺼내 쓰거나 `Arrays.toString()` 으로 감싸야 내용이 보인다 — 1-2의 `toString()` 이야기가 여기서 다시 나온다

```java
String[] strAry = "010339-2140421".split("-");
System.out.println(strAry[0]);   // 010339
System.out.println(strAry[1]);   // 2140421
```

**`getBytes()` 와 `new String(byte[])`** 는 문자열과 바이트를 오가는 한 쌍이다.

```java
byte[] strAry2 = "ABC".getBytes();
System.out.println(Arrays.toString(strAry2));   // [65, 66, 67]
System.out.println(new String(strAry2));        // ABC
```

파일 저장·네트워크 전송처럼 프로그램 바깥으로 나갈 때 데이터는 결국 바이트다. 그래서 외부 통신 코드에서는 이 변환이 늘 등장한다. 1-10에서 "바깥에서 들어오는 데이터는 문자열"이라고 정리했는데, 한 층 더 내려가면 바이트인 셈이다.

**`StringBuilder`** 는 2-3에서 정리한 그대로다. `String` 이 불변이라 이어 붙일 때마다 새 객체가 생기므로, 조립할 때는 빌더 하나를 두고 `append()` 로 쌓는다.

```java
StringBuilder builder = new StringBuilder();
builder.append("자바");
builder.append("프로그래밍");
System.out.println(builder);   // 자바프로그래밍
```

### 1-13. Random과 UUID — 값을 만들어 내는 라이브러리

지금까지 본 라이브러리가 "가진 값을 다루는" 쪽이었다면, `Random` 과 `UUID` 는 **값을 만들어 내는** 쪽이다.

```java
Random random = new Random();

int value1 = random.nextInt();        // int 범위 전체에서 난수 — 378904417
int value2 = random.nextInt(10);      // 0 ~ 9
int value3 = random.nextInt(10) + 1;  // 1 ~ 10
boolean value4 = random.nextBoolean();// true / false
```

`nextXXX()` 는 뽑아낼 타입에 따라 이름이 갈린다(`nextInt`·`nextDouble`·`nextBoolean`·`nextLong`). 정리하면 규칙은 두 가지다.

| 형태 | 나오는 범위 |
| --- | --- |
| `nextInt()` | `int` 가 표현할 수 있는 전 범위 (음수 포함) |
| `nextInt(n)` | `0` 이상 `n` **미만** — 개수를 넣는다 |
| `nextInt(n) + 시작값` | `시작값` 부터 `n` 개 |

- 주사위(1~6)는 `nextInt(6) + 1`. "개수를 넣고 시작 번호를 더한다"로 외우면 헷갈리지 않는다
- 끝값이 포함되지 않는 건 [[Java day04 제어문과 배열]] 의 인덱스 규칙, 1-12의 `substring(시작, 끝)` 과 같은 결이다. 자바는 범위를 다룰 때 대체로 "시작은 포함, 끝은 제외"로 통일돼 있다

**UUID**(범용 고유 식별자)는 사실상 중복이 나지 않는 128비트 식별자다.

```java
String uuid = UUID.randomUUID().toString();
System.out.println(uuid);   // 91ce0f1e-7a0a-4034-be44-fd94d3d3b07e
```

- `randomUUID()` 는 `new` 없이 부르는 정적 팩토리 메소드다 — 1-11의 `LocalDate.now()` 와 같은 형태
- 반환값이 `UUID` 객체라 문자열로 쓰려면 `toString()` 을 붙인다. 1-2에서 정리한 그 `toString()` 이 여기선 하이픈으로 끊긴 36자 문자열을 돌려준다
- 쓰는 자리는 **회원번호·주문번호·업로드 파일명**처럼 "겹치면 안 되는 이름"이 필요한 곳이다. DB의 `AUTO_INCREMENT` 는 한 테이블 안에서만 유일하지만, UUID는 서버가 여러 대여도 각자 만들어 쓸 수 있다 — [[SQL day02 테이블과 제약조건]] 의 기본키를 정하는 선택지 중 하나다
- 업로드 파일명을 UUID로 바꿔 두면 같은 이름의 파일이 서로를 덮어쓰는 상황을 피할 수 있다

### 1-14. 문자열 하나에 담긴 표 데이터 다루기 (practice14)

`String` 메소드를 모아서 쓰는 실습으로 **타워 주차 관리** 과제가 붙는다. 요구사항의 핵심은 데이터를 클래스나 배열이 아니라 **문자열 하나**로 관리한다는 점이다.

```java
String carParkingList = "3,211가6231,202608190930\n8,452하1234,202608171227";
// 행 구분: \n   열 구분: ,   컬럼: 위치번호,차량번호,날짜시간(YYYYMMDDhhmm)
```

한 줄이 한 대의 차량이고, 줄 안에서 쉼표가 열을 가른다. 표를 문자열로 눌러 담은 형태라 결국 **두 번 쪼개는** 것이 기본 동작이 된다.

```java
String[] rows = carParkingList.split("\n");     // ① 행으로 자르기
for (String row : rows) {
    String[] col = row.split(",");              // ② 열로 자르기
    // col[0] 위치번호, col[1] 차량번호, col[2] 날짜시간
}
```

과제가 요구하는 세 기능을 문자열 연산으로 옮기면 이렇게 대응된다.

| 기능 | 쓰는 도구 |
| --- | --- |
| 위치 찾기 | 행마다 `split(",")` 후 `col[1].equals(차량번호)` 비교, 찾으면 `col[0]` 반환 / 없으면 `-1` |
| 입차 | 위치 중복을 먼저 확인한 뒤 `carParkingList + "\n" + 새 행` 으로 이어 붙이기 |
| 출차 | 해당 행을 빼고 남은 행들을 `String.join("\n", …)` 으로 다시 잇기 |

- 검색은 `indexOf`·`contains` 로도 되지만, **"어느 열에서 찾을지"가 정해져 있으면 쪼갠 뒤 열 단위로 `equals()` 비교**하는 편이 안전하다. 문자열 전체를 대상으로 하면 위치번호나 날짜에 우연히 같은 숫자가 들어 있을 때 걸린다
- 행을 지울 때 `replace(행, "")` 만 쓰면 줄바꿈이 남아 빈 줄이 생긴다. 남길 행만 모아 다시 잇는 방식이면 구분자가 저절로 정리된다. 조립은 2-3의 `StringBuilder` 나 `String.join()` 이 맡는다
- 요금 계산은 `202608190930` 같은 12자리를 `substring()` 으로 잘라 `LocalDateTime.of(...)` 로 만들고, 1-11의 `ChronoUnit.MINUTES.between()` 으로 분 차이를 구하는 흐름이 된다. 10분 단위 올림은 `(분 + 9) / 10` 처럼 정수 나눗셈으로 처리할 수 있다 — [[Java day03 연산자]] 의 정수 나눗셈 성질을 쓰는 자리다
- `DateTimeFormatter.ofPattern("yyyyMMddHHmm")` 을 만들어 `LocalDateTime.parse(문자열, formatter)` 로 한 번에 파싱하는 방법도 있다. 1-11의 포맷터가 출력뿐 아니라 입력에도 쓰인다는 점이 여기서 드러난다

정리하면 이 실습은 **문자열 = 구분자로 눌러 담은 표**라는 관점을 연습하는 과제다. csv 파일이 정확히 이 구조라, 나중에 파일 입출력이나 API 응답을 다룰 때 같은 손놀림이 그대로 쓰인다.

### 1-15. 실습 뼈대 — 메뉴 루프와 기능 메소드 분리

구현을 시작하면서 잡은 골격은 [[Java day06 생성자와 콘솔 게시판]]·[[Java day07 메소드와 미니프로젝트]] 의 콘솔 프로그램과 같다. **무한 루프 + 번호 입력 + 분기**가 화면 쪽을 맡고, 실제 처리는 `static` 메소드로 빼 둔다.

```java
String carParkingList = "3,211가6231,202608190930\n8,452하1234,202608171227";
Scanner scan = new Scanner(System.in);

while (true) {
    System.out.print("1.위치찾기 2.입차 3.출차 선택:");
    int ch = scan.nextInt();

    if (ch == 1) {
        String carNumber = scan.next();
        int result = findCarLocation(carParkingList, carNumber);
        System.out.println(result);
    }
    if (ch == 2) { … }
    if (ch == 3) { … }
}
```

기능 메소드의 시그니처를 어떻게 잡느냐가 이 실습의 실제 설계 지점이다.

| 기능 | 형태 | 왜 이 모양인가 |
| --- | --- | --- |
| 위치 찾기 | `static int findCarLocation(String list, String carNumber)` | 데이터를 바꾸지 않고 읽기만 한다. 못 찾으면 `-1` |
| 입차 | `static String carCheckIn(String list, int location, String carNumber, LocalDate dt)` | 데이터를 **바꾸므로 갱신된 문자열을 돌려줘야** 한다 |
| 출차 | `static String carCheckOut(String list, String carNumber)` | 같은 이유로 반환형이 `String` |

여기서 1-12의 **`String` 불변** 성질이 설계에 직접 영향을 준다. 메소드 안에서 `list += "\n" + 새 행` 을 해도 그건 메소드 안 지역변수만 바뀐 것이라 **호출한 쪽의 원본은 그대로**다. 그래서 입차·출차는 결과를 반환하고, 호출부에서 다시 대입해야 실제로 반영된다.

```java
carParkingList = carCheckIn(carParkingList, location, carNumber, LocalDate.now());
```

매개변수로 넘긴 참조타입이라도 **재대입은 바깥에 전달되지 않는다**. 반대로 `ArrayList` 처럼 가변 객체를 넘겨 `add()` 로 내용을 바꾸면 바깥에도 보인다. 참조를 바꾸는 것과 참조가 가리키는 내용을 바꾸는 것이 다르다는 이야기이고, 문자열을 상태로 쓰기로 한 이상 "반환해서 다시 대입"이 유일한 갱신 방법이 된다.

**찾기 방식 두 갈래**

`split("\n")` 으로 자른 행을 다시 `split(",")` 하면 자연스럽게 2차원이 된다. 이걸 한 줄로 펴서 `ArrayList` 하나에 전부 담고 순회하는 방법도 있다.

```java
// ① 행 단위로 보기 — 열 위치가 이름 그대로 남는다
for (String row : list.split("\n")) {
    String[] col = row.split(",");
    if (col[1].equals(carNumber)) return Integer.parseInt(col[0]);
}

// ② 전부 펴서 한 줄로 보기 — 찾은 자리의 앞 칸이 위치번호
for (int i = 0; i < flat.size(); i++) {
    if (flat.get(i).equals(carNumber)) return Integer.parseInt(flat.get(i - 1));
}
```

②는 코드가 짧지만 "값을 찾은 뒤 인덱스를 되짚어 앞 칸을 꺼낸다"는 규칙이 열 순서에 묶인다. 컬럼이 하나 늘거나 순서가 바뀌면 `i - 1` 이 통째로 어긋나고, 첫 원소가 걸리면 인덱스가 음수로 내려간다. **행 안에서 열 번호로 접근하는 ①이 열 구조의 뜻을 코드에 남긴다는 점에서 안전한 편이다.**

- 반환값 규약은 하나로 정해 두는 편이 낫다. 과제 설명에는 `"미등록 차량"` 과 `-1` 이 같이 나오는데, 위치번호를 숫자로 쓸 거면 **`int` + 실패는 `-1`** 로 통일하고 메시지는 호출부에서 붙이는 쪽이 호출하는 코드가 단순해진다
- 입차의 중복 검사는 "그 위치에 이미 차가 있는지"를 묻는 것이므로, 찾기와 같은 순회를 `col[0]`(위치) 기준으로 한 번 더 돌리면 된다. 열만 바꾼 같은 모양이라 `findByColumn(list, 열번호, 값)` 식으로 하나로 묶어도 된다

### 1-16. 쪼개는 일을 헬퍼로 빼기 — 공유 상태와 clear()

세 기능이 전부 "문자열을 쪼개고 순회한다"로 시작하니, 쪼개는 부분만 메소드 하나로 빼면 중복이 줄어든다. 결과를 담을 곳을 멤버변수로 올려 두고 헬퍼가 그 자리를 채우는 형태가 된다.

```java
static ArrayList<String> carList = new ArrayList<>();

static void listSplit(String carParkingList) {
    carList.clear();                                  // ① 먼저 비운다
    for (String row : carParkingList.split("\n")) {
        for (String cell : row.split(",")) {
            carList.add(cell);                        // ② 전부 펴서 담는다
        }
    }
}
```

여기서 눈여겨볼 자리는 ①이다. `carList` 는 `static` 이라 프로그램이 도는 동안 **한 개만 존재하고 계속 살아 있다** — [[Java day08 접근제한자와 static]] 의 static 영역 이야기 그대로다. 비우지 않고 `add()` 만 하면 헬퍼를 부를 때마다 이전 내용 뒤에 계속 쌓여서, 두 번째 호출부터 리스트 길이가 두 배·세 배가 된다. **같은 입력으로 몇 번을 불러도 결과가 같아야** 메뉴 루프처럼 반복 호출되는 구조에서 안심하고 쓸 수 있다 (`#멱등성`).

반환하는 방식과 비교하면 성격이 갈린다.

| 방식 | 모양 | 성격 |
| --- | --- | --- |
| 공유 상태 | `static void listSplit(String s)` → `carList` 를 채움 | 호출부가 짧다. 대신 "지금 `carList` 안에 뭐가 들어 있나"를 늘 신경 써야 한다 |
| 반환 | `static ArrayList<String> split(String s)` | 호출할 때마다 새 리스트가 나오므로 섞일 일이 없다. 매번 새로 만드는 비용은 있다 |

작은 실습에서는 둘 다 돌아가지만, 메소드가 늘어날수록 반환 방식이 추적하기 쉬워진다. 공유 상태로 갈 거면 "채우는 쪽은 반드시 먼저 비운다"를 규칙으로 고정해 두는 편이 안전하다.

**시각을 밖에서 받아 넣기**

입차 메소드가 시각을 직접 만들지 않고 매개변수로 받는 형태를 잡았다.

```java
LocalDateTime now = LocalDateTime.now();                 // 호출부에서 만들고
String result = carCheckIn(carParkingList, location, carNumber, now);   // 넘긴다
```

메소드 안에서 `LocalDateTime.now()` 를 부르면 호출할 때마다 결과가 달라져서, 나중에 "2026-08-19 09:30에 들어온 차"처럼 특정 시각을 넣어 확인하고 싶을 때 손댈 방법이 없다. **바깥에서 만들어 넘기면 값이 하나 더 늘어나는 대신 결과를 내가 정할 수 있다.** [[Java day11 인터페이스]] 에서 구현을 밖에서 갈아끼운 것과 같은 결의 이야기고, 나중에 테스트 코드를 쓸 때 반복해서 만나는 방식이다.

**중복 검사에서 비교 대상을 좁히기**

입차는 "그 위치에 이미 차가 있나"를 먼저 확인한 뒤 행을 이어 붙인다.

```java
if (중복) return location + "번 자리에는 중복 주차할 수 없습니다.";
carParkingList += "\n" + location + "," + carNumber + "," + nowTime;
return location;
```

이때 1-15의 ②처럼 펴 놓은 리스트 전체를 대상으로 비교하면, 위치번호가 우연히 다른 열의 값(차량번호 일부나 날짜 조각)과 같아도 걸린다. **위치는 위치 열끼리만 비교한다**는 조건을 코드에 남기려면 행 단위로 자른 뒤 `col[0]` 만 보는 형태가 필요하다. 데이터가 늘어나기 전에는 잘 드러나지 않는 종류의 차이라, 문자열 표를 다룰 땐 "어느 열을 보고 있는지"를 항상 코드에 적어 두는 습관이 남는다.

반환값도 두 갈래가 섞이기 쉽다. 성공하면 위치번호, 실패하면 안내 문구를 같은 `String` 으로 돌려주면 호출부에서 둘을 구분할 방법이 문자열 내용뿐이다. 갱신된 목록을 돌려줄지, 결과 코드만 돌려줄지 **하나로 정해 두고 메시지는 화면 쪽에서 붙이는** 편이 나중에 기능이 늘어도 흔들리지 않는다 — [[Java day09 MVC 종합예제]] 에서 view와 model을 갈라 둔 이유와 같다.

### 1-17. 출차 처리 — 고정폭 문자열 파싱과 요금 계산

세 기능 중 가장 손이 많이 가는 자리가 출차다. 행을 지우는 것 자체는 문자열 조작이지만, 그 전에 **저장해 둔 입차 시각을 다시 날짜 객체로 되살리고 요금을 계산**해야 한다. 1-11의 `java.time`, 1-12의 `substring()`, [[Java day03 연산자]] 의 정수 나눗셈이 한 메소드에서 전부 만난다.

**① 12자리 문자열을 날짜로 되돌리기**

`202608190930` 처럼 자리 수가 고정된 형식은 `substring()` 으로 잘라 숫자로 바꾸면 그대로 `LocalDateTime.of()` 의 인자가 된다.

```java
int year  = Integer.parseInt(s.substring(0, 4));    // 2026
int month = Integer.parseInt(s.substring(4, 6));    // 08
int day   = Integer.parseInt(s.substring(6, 8));    // 19
int hour  = Integer.parseInt(s.substring(8, 10));   // 09
int min   = Integer.parseInt(s.substring(10, 12));  // 30

LocalDateTime inTime = LocalDateTime.of(year, month, day, hour, min);
```

- `substring(시작, 끝)` 의 끝이 포함되지 않으므로 구간이 `0-4`, `4-6`, `6-8` 처럼 **앞 구간의 끝이 다음 구간의 시작**으로 이어진다. 이 규칙 덕분에 자리 수만 맞으면 경계를 세지 않고 쭉 나열할 수 있다
- 큰 단위부터 고정 자리 수로 붙여 저장한 형식이라 이런 잘라내기가 가능하다. 2-13에서 정리한 저장 형식의 장점이 실제로 쓰이는 자리다
- 같은 일을 2-13의 포맷터로 한 번에 처리할 수도 있다. 자리마다 `parseInt()` 를 부르는 대신 규격을 한 곳에 모아 두는 쪽이다

```java
DateTimeFormatter FMT = DateTimeFormatter.ofPattern("yyyyMMddHHmm");
LocalDateTime inTime = LocalDateTime.parse(s, FMT);
```

**② 두 시각의 간격 구하기**

입차 시각과 현재 시각의 차이를 분으로 환산해야 요금을 매길 수 있다. 날짜 부분과 시각 부분을 각각 분으로 바꿔 빼는 방식이 먼저 떠오른다.

```java
int inMinutesOfDay  = (inTime.getHour() * 60) + inTime.getMinute();
int nowMinutesOfDay = (now.getHour() * 60) + now.getMinute();
int totalMinutes = (diffDays * 24 * 60) + (nowMinutesOfDay - inMinutesOfDay);
```

시각 부분은 이 방식이 정확하지만, **날짜 차이를 직접 셈하는 쪽은 조심할 자리**다. 연·월·일을 숫자로 놓고 산술하면 윤년(365일이 아닌 해)과 월마다 다른 일수가 그대로 오차로 들어온다. 이런 계산은 라이브러리에 맡기는 편이 안전하다.

```java
long totalMinutes = ChronoUnit.MINUTES.between(inTime, now);
```

`ChronoUnit` 은 2-7에서 날짜 간격을 구할 때 본 그 유틸이고, `MINUTES` 말고도 `HOURS`·`DAYS`·`SECONDS` 를 같은 모양으로 쓸 수 있다. 정리하면 **"시각을 만드는 일은 내가, 시각끼리 빼는 일은 `java.time` 이"** 로 나누는 것이 기본형이다.

- 미래 시각이 들어오면 간격이 음수가 된다. 요금처럼 음수가 의미 없는 값은 `if (totalMinutes < 0) totalMinutes = 0;` 으로 바닥을 막아 두면 뒤쪽 계산이 단순해진다
- `between(a, b)` 는 `a` 에서 `b` 로 가는 방향이라 인자 순서가 부호를 정한다. 입차 → 현재 순서로 넣는다

**③ 요금 정책을 식으로 옮기기**

정책은 세 줄이지만 각각 계산 관용구가 하나씩 붙는다.

| 정책 | 식 |
| --- | --- |
| 최초 30분 무료 | `billable = remainMinutes - 30` (0 이하면 요금 없음) |
| 30분 초과분 10분당 1,000원 (올림) | `((billable + 9) / 10) * 1000` |
| 하루 최대 20,000원 | `if (fee > 20000) fee = 20000;` |
| 여러 날 주차 | `days * 20000 + 잔여분 요금` |

```java
int days          = totalMinutes / (24 * 60);   // 며칠치인가 — 몫
int remainMinutes = totalMinutes % (24 * 60);   // 하루 안에 남은 분 — 나머지
```

`/` 와 `%` 를 한 쌍으로 쓰는 이 모양이 "큰 단위로 묶고 나머지를 따로 본다"의 기본형이다. 초를 시·분·초로 쪼개거나 페이지 번호를 계산할 때도 같은 손놀림이 나온다.

**정수 나눗셈으로 올림 만들기**가 이 실습의 핵심 계산이다. 자바의 `/` 는 정수끼리면 소수점을 버리므로(내림), 올림이 필요하면 **나누는 수보다 1 작은 값을 미리 더한다.**

```java
(31 + 9) / 10 = 4   // 31분 → 4 × 1,000원
(40 + 9) / 10 = 4   // 40분 → 4 × 1,000원 (딱 나눠떨어지면 그대로)
(41 + 9) / 10 = 5   // 41분 → 5 × 1,000원
```

`Math.ceil()` 로 하면 실수 변환이 끼어들고 다시 `(int)` 로 되돌려야 한다. 정수만 다루는 자리에서는 `(a + b - 1) / b` 쪽이 짧고 오차도 없다.

**④ 결과를 화면에 내보내기**

계산이 끝나면 입·출차 시각을 사람이 읽는 형식으로 바꿔 안내문을 찍는다.

```java
DateTimeFormatter formatter = DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm");
System.out.println("입차시간: " + inTime.format(formatter));
System.out.println("출차시간: " + now.format(formatter));
System.out.println("주차요금: " + totalFee + "원");
```

저장용 형식(`yyyyMMddHHmm`)과 표시용 형식(`yyyy-MM-dd HH:mm`)이 다르다는 점이 여기서 분명해진다. 저장은 자르기 쉽게 붙여 쓰고, 화면은 읽기 쉽게 구분자를 넣는다. **같은 값이라도 층마다 형식이 다르다**는 것이 요지다.

**⑤ 반환값을 무엇으로 둘 것인가**

출차 메소드는 두 가지 결과를 동시에 갖는다 — 계산한 **요금**과, 그 행을 뺀 **갱신된 목록**이다. 자바 메소드는 값을 하나만 돌려주므로 둘 중 하나를 골라야 한다.

| 반환 | 장점 | 남는 문제 |
| --- | --- | --- |
| `int` 요금 | 호출부에서 바로 출력·집계에 쓴다 | 목록 갱신을 별도로 처리해야 한다 |
| `String` 갱신 목록 | 1-15의 입차와 반환 규약이 통일된다 | 요금을 따로 꺼낼 방법이 필요하다 |

1-15에서 정리한 대로 `String` 은 불변이라, 목록을 문자열 상태로 두는 이상 **갱신 결과는 반환해서 다시 대입**하지 않으면 호출부에 반영되지 않는다. 요금까지 함께 넘기려면 결과를 담는 작은 클래스를 하나 두거나, 목록을 `static` 멤버로 올려 메소드가 직접 갱신하게 하는 방법이 있다. 후자는 1-16에서 본 공유 상태 방식이라 호출부는 짧아지고 추적은 어려워지는 맞바꿈이 그대로 따라온다.

- 행 삭제는 2-10의 "남길 행만 모아 다시 잇기"가 그대로 쓰인다. `String.join("\n", 남길행들)` 이면 구분자 정리까지 한 번에 끝난다
- 값을 찾은 뒤 `i + 1`·`i - 1` 로 옆 칸을 꺼내는 방식은 1-15 ②의 성질을 그대로 갖는다. 컬럼이 늘거나 순서가 바뀌면 오프셋이 통째로 어긋나므로, 행으로 자른 뒤 `col[2]` 처럼 **열 번호로 짚는** 형태가 뜻을 코드에 남긴다

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

### 2-5. Integer 비교는 == 가 아니라 equals

1-3의 문자열 이야기가 래퍼 클래스에서 그대로 반복된다.

```java
Integer a = 100, b = 100;
System.out.println(a == b);        // true

Integer c = 1000, d = 1000;
System.out.println(c == d);        // false
System.out.println(c.equals(d));   // true
```

자바는 자주 쓰이는 작은 정수(`-128 ~ 127`)의 `Integer` 객체를 미리 만들어 두고 재사용한다. 그 범위 안이면 같은 객체를 가리켜 `==` 가 `true` 가 되고, 벗어나면 매번 새 객체라 `false` 가 된다. 문자열 상수 풀과 같은 구조다.

**래퍼 타입은 값 비교에 `equals()` 를 쓴다.** 값 계산만 할 거라면 애초에 래퍼가 아니라 기본타입(`int`)으로 두는 편이 안전하다.

### 2-6. 문자열 → 숫자 변환은 실패할 수 있다

```java
int n = Integer.parseInt("abc");   // NumberFormatException
```

`parseInt()` 는 숫자로 읽을 수 없는 문자열을 만나면 예외를 던진다. 사용자 입력이나 파일에서 읽은 값을 변환할 때는 감싸 두는 편이 안전하다.

```java
try {
    int n = Integer.parseInt(입력값);
} catch (NumberFormatException e) {
    System.out.println("숫자를 입력해 주세요.");
}
```

`NumberFormatException` 은 실행 중에만 드러나는 unchecked 예외라 컴파일러가 처리를 강제하지 않는다 — [[Java day12 예외 처리와 JDBC]] 에서 갈라 둔 두 종류 중 오른쪽이다. 앞뒤 공백 때문에 실패하는 경우가 많아 `입력값.trim()` 을 먼저 걸어 두면 잔실수가 줄어든다.

### 2-7. 날짜 다루기 관용구

```java
LocalDate today = LocalDate.now();
LocalDate 마감일 = today.plusDays(7);

// 순서 비교 — 부등호 대신 메소드
today.isBefore(마감일);   // true
today.isAfter(마감일);    // false
today.isEqual(마감일);    // false

// 두 날짜 사이의 간격
long 남은일수 = ChronoUnit.DAYS.between(today, 마감일);   // 7

// 문자열 → 날짜
LocalDate d = LocalDate.parse("2026-08-19");
```

날짜 객체는 참조타입이라 `<`·`>` 로 비교할 수 없다. 크기 비교는 `isBefore()`·`isAfter()` 로 한다. 1-10의 `parseInt()` 처럼 여기서도 `parse()` 가 문자열을 객체로 되돌리는 이름이다.

DB와 주고받을 때는 MySQL의 `DATE`·`DATETIME` 컬럼이 `LocalDate`·`LocalDateTime` 과 그대로 대응한다. `ResultSet` 에서 꺼낼 때는 `rs.getDate("regdate").toLocalDate()` 처럼 변환해서 받는다 — [[Java day12 종합예제 JDBC DAO]] 의 DAO가 DTO를 채우는 자리에서 쓰인다.

### 2-8. 문자열 다듬기 관용구

입력값을 그대로 믿고 쓰면 앞뒤 공백이나 빈 문자열 때문에 잔실수가 생긴다. 검증 전에 한 번 다듬어 두는 편이 안전하다.

```java
String 입력 = "  홍길동  ";
입력.trim();            // 앞뒤 공백 제거 — "홍길동"
입력.strip();           // trim의 유니코드 대응 버전 (자바 11+)
"".isEmpty();           // true  — 길이가 0인가
"   ".isBlank();        // true  — 공백만 있는가 (자바 11+)
"abc".toUpperCase();    // ABC
```

여러 조각을 합칠 때는 구분자를 직접 붙이는 것보다 `String.join()` 이 읽기 쉽고, 자리를 채워 문장을 만들 때는 `String.format()` 을 쓴다.

```java
String.join(", ", "사과", "포도", "감");        // 사과, 포도, 감
String.format("%s님, 잔액은 %,d원입니다.", "홍길동", 1234567);
```

| 서식 | 뜻 |
| --- | --- |
| `%s` | 문자열 |
| `%d` / `%,d` | 정수 / 천 단위 콤마 |
| `%.2f` | 소수점 둘째 자리까지 |
| `%5d` / `%-5s` | 폭 5로 오른쪽 정렬 / 왼쪽 정렬 |

`System.out.printf()` 는 `format()` 한 결과를 바로 출력하는 형태다. 1-8처럼 콘솔에 표를 그릴 때 폭 지정 서식으로 칸을 맞출 수 있다. 다만 한글은 두 칸을 차지해서 `%5s` 만으로는 어긋나므로, 글자 폭을 직접 세는 방식과 섞어 쓰게 된다.

### 2-9. 난수 관용구

```java
// 범위 난수 — a 이상 b 이하
int n = random.nextInt(b - a + 1) + a;

// 배열·리스트에서 하나 무작위로 뽑기
String pick = list.get(random.nextInt(list.size()));

// 인증번호 6자리 (앞자리 0이 사라지지 않게 서식으로 채운다)
String code = String.format("%06d", random.nextInt(1000000));

// 씨앗(seed)을 고정하면 매번 같은 순서가 나온다 — 테스트용
Random fixed = new Random(42);
```

`nextInt(list.size())` 가 인덱스 범위와 정확히 맞는 이유는 1-13에서 정리한 "끝값 제외" 규칙 덕분이다. 씨앗을 고정하는 건 난수가 실제로는 계산식으로 만들어지는 값이라 가능한 일이고, 결과가 매번 달라지면 곤란한 테스트에서 쓴다.

보안이 걸린 값(비밀번호 초기화 토큰 등)에는 `Random` 대신 `SecureRandom` 을 쓴다. `Random` 은 씨앗을 알면 다음 값을 예측할 수 있어서, 맞히면 안 되는 값에는 맞지 않는다.

### 2-10. 구분자로 담은 데이터를 다룰 때

```java
String data = "3,211가6231,202608190930\n8,452하1234,202608171227";

// 행 단위 순회
for (String row : data.split("\n")) { … }

// 남길 행만 모아 다시 잇기 (삭제)
StringBuilder sb = new StringBuilder();
for (String row : data.split("\n")) {
    if (!row.split(",")[1].equals(대상번호)) {
        if (sb.length() > 0) sb.append("\n");
        sb.append(row);
    }
}
String result = sb.toString();
```

`if (sb.length() > 0)` 로 구분자를 붙이는 건, 맨 앞이나 맨 뒤에 빈 줄이 남지 않게 하는 흔한 처리다. 자바 8부터는 `String.join("\n", 리스트)` 가 같은 일을 한 줄로 해 준다.

- `split()` 의 인자는 사실 정규표현식이다. `.` `|` `+` 같은 문자를 구분자로 쓸 때는 `split("\\.")` 처럼 이스케이프해야 의도대로 갈린다
- 줄바꿈은 운영체제마다 `\n`·`\r\n` 으로 다르다. 외부에서 받은 텍스트를 쪼갤 때는 `split("\\r?\\n")` 이 안전하다

### 2-11. Scanner의 next 계열 — 섞어 쓸 때 주의

메뉴 루프에서 숫자와 문자열을 번갈아 받으면 입력이 어긋나는 자리가 하나 있다.

| 메소드 | 읽는 범위 | 개행(`\n`) 처리 |
| --- | --- | --- |
| `nextInt()` / `nextDouble()` | 공백 전까지의 숫자 하나 | 뒤에 남은 개행을 **버리지 않는다** |
| `next()` | 공백 전까지의 단어 하나 | 마찬가지로 남긴다 |
| `nextLine()` | 개행 전까지 한 줄 전체 | 개행까지 읽고 버린다 |

그래서 `nextInt()` 뒤에 바로 `nextLine()` 을 부르면 남아 있던 개행만 읽고 빈 문자열이 돌아온다. 해결은 두 가지다.

```java
int ch = scan.nextInt();
scan.nextLine();              // ① 남은 개행을 한 번 비운다
String name = scan.nextLine();

int ch2 = Integer.parseInt(scan.nextLine());   // ② 전부 nextLine으로 받고 변환
```

②는 1-10의 `parseInt()` 를 쓰는 방식이라 입력 경로가 `nextLine()` 하나로 통일된다. 공백이 들어간 값(주소·제목 등)을 받아야 한다면 `next()` 는 첫 단어에서 끊기므로 어차피 `nextLine()` 이 필요하다.

숫자를 기대한 자리에 문자가 들어오면 `nextInt()` 는 `InputMismatchException` 을 던지고 입력이 버퍼에 그대로 남아 무한 루프가 된다. 메뉴처럼 계속 도는 구조라면 ②로 받아 2-6의 `NumberFormatException` 을 잡는 편이 흐름이 끊기지 않는다.

### 2-12. 지역변수에는 접근제한자·static을 붙이지 않는다

`public`·`private`·`static` 은 **클래스의 멤버**(멤버변수·메소드)에 붙이는 키워드다. 메소드 안에서 선언하는 지역변수에는 붙일 수 없다 — 지역변수는 메소드가 실행될 때 생겼다가 끝나면 사라지므로 "밖에서 접근하는 범위"라는 개념 자체가 성립하지 않는다.

```java
static void method() {
    ArrayList<String> list = new ArrayList<>();   // 지역변수 — 제한자 없이
}

public class A {
    private static int count;                     // 멤버변수 — 여기에 붙는다
}
```

- 여러 호출에 걸쳐 값을 유지해야 하면 그건 지역변수가 아니라 클래스 멤버로 올릴 자리다 — [[Java day08 접근제한자와 static]] 의 static 영역 이야기가 그대로 적용된다
- 지역변수에 붙일 수 있는 유일한 제한자는 `final` 이다. 한 번 대입한 뒤 바꾸지 않겠다는 표시로 쓴다

### 2-13. 날짜 포맷 문자는 대소문자가 다른 뜻이다

`DateTimeFormatter.ofPattern()` 에 넣는 문자는 대문자와 소문자가 서로 다른 값을 가리킨다. 눈으로는 잘 안 보이는데 결과는 완전히 달라진다.

| 문자 | 뜻 | 문자 | 뜻 |
| --- | --- | --- | --- |
| `yyyy` | 연도 | `YYYY` | 주 기준 연도 (연말·연초에 어긋난다) |
| `MM` | 월 | `mm` | 분 |
| `dd` | 일 | `DD` | 그 해의 몇 번째 날 |
| `HH` | 24시간 (0~23) | `hh` | 12시간 (1~12) |
| `ss` | 초 | `SS` | 밀리초 |

- 자주 걸리는 자리는 **`MM`(월) / `mm`(분)** 과 **`HH` / `hh`** 두 쌍이다. `hh` 로 찍으면 오후 3시가 `03` 이 되어 새벽 3시와 구분되지 않으므로, `a`(오전/오후)를 같이 쓰지 않는 이상 `HH` 가 기본이다
- 자리 수는 문자를 반복한 개수로 정해진다. `yy` 는 두 자리(`26`), `yyyy` 는 네 자리(`2026`)다. 데이터 규격이 `YYYYMMDDhhmm` 12자리라면 패턴은 `yyyyMMddHHmm` 이 된다
- 패턴은 출력과 입력 양쪽에 쓴다. 같은 포맷터로 `format()` 해서 저장하고 `LocalDateTime.parse(문자열, formatter)` 로 되읽으면 규격이 어긋날 일이 없다

```java
DateTimeFormatter fmt = DateTimeFormatter.ofPattern("yyyyMMddHHmm");
String saved = LocalDateTime.now().format(fmt);          // 202608191524
LocalDateTime back = LocalDateTime.parse(saved, fmt);    // 되읽기
```

- 포맷터는 상태를 갖지 않으므로 **한 번 만들어 상수로 두고 재사용**해도 된다. `static final DateTimeFormatter FMT = …` 형태가 흔하다
- 날짜를 문자열로 저장할 땐 `yyyyMMddHHmm` 처럼 **큰 단위부터 고정 자리 수로** 붙이는 형식이 좋다. 이러면 문자열을 그냥 사전순으로 정렬해도 시간순이 되고, `substring()` 으로 연·월·일을 잘라 내기도 쉽다

### 2-14. 정수 나눗셈으로 단위 계산하기

요금·페이지·용량처럼 "단위로 묶어 세는" 계산은 `/` 와 `%` 두 연산자로 거의 다 처리된다. 관용구를 모아 두면 이렇다.

```java
int q = total / unit;              // 몫   — 몇 단위인가
int r = total % unit;              // 나머지 — 단위에 못 미친 부분

int up = (total + unit - 1) / unit;   // 올림 나눗셈
int fee = Math.min(계산값, 상한);      // 상한 걸기
int safe = Math.max(계산값, 0);        // 바닥 걸기
```

| 하고 싶은 것 | 식 |
| --- | --- |
| 10분 단위로 올림 | `(분 + 9) / 10` |
| 초 → 시·분·초 | `s/3600`, `(s%3600)/60`, `s%60` |
| 총 개수를 한 쪽 n개씩 나눈 페이지 수 | `(개수 + n - 1) / n` |
| 값을 0~100 사이로 가두기 | `Math.max(0, Math.min(100, 값))` |

- 자바의 정수 나눗셈은 소수점을 **버린다**(0 방향으로). 그래서 올림은 미리 `unit - 1` 을 더해 만든다 — [[Java day03 연산자]] 에서 `5 / 2` 가 `2` 였던 그 성질을 거꾸로 이용하는 셈이다
- `Math.min`·`Math.max` 는 `if` 로 쓰는 것과 결과가 같지만, 상한·바닥이라는 뜻이 이름에 드러나서 읽기 쉽다
- 나누는 수가 변수라면 0인지 먼저 확인한다. 정수를 0으로 나누면 `ArithmeticException` 이 나고, 실수는 예외 대신 `Infinity` 가 나와서 오히려 늦게 발견된다
- 금액처럼 정확해야 하는 값에 `double` 을 쓰면 `0.1 + 0.2` 가 `0.30000000000000004` 가 되는 부동소수점 오차가 따라온다. **원 단위 정수로 계산**하거나 `BigDecimal` 을 쓴다

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

### 3-4. 타임존과 시간의 절대 좌표

`LocalDateTime` 의 `Local` 은 "시간대 정보가 없다"는 뜻이다. `2026-08-19 11:07` 이라는 문자만 있고 그게 어느 지역의 11시인지는 담고 있지 않다. 혼자 쓰는 프로그램은 문제없지만, 서버와 사용자가 다른 나라에 있으면 이 구분이 필요해진다.

| 클래스 | 담는 것 | 쓰는 자리 |
| --- | --- | --- |
| `LocalDateTime` | 시간대 없는 날짜/시각 | 지역 안에서만 쓰는 화면 표시 |
| `ZonedDateTime` | 시간대(`Asia/Seoul`)까지 포함 | 여러 지역 사용자를 상대할 때 |
| `Instant` | 1970-01-01 UTC부터의 절대 시각 | 로그·정렬 기준, 서버 저장용 |
| `Duration` / `Period` | 시각 간격 / 날짜 간격 | 경과 시간, 남은 일수 계산 |

실무의 기본형은 **저장은 UTC(`Instant`), 표시할 때만 사용자 시간대로 변환**이다. 저장된 값 자체는 지역과 무관한 하나의 좌표로 두는 편이 나중에 문제가 적다.

### 3-5. java.time 이전의 Date·Calendar

검색하면 `java.util.Date`·`SimpleDateFormat`·`Calendar` 를 쓴 예제가 많이 나온다. 자바 8 이전의 방식이고, 지금은 `java.time` 이 표준이다. 옛 API는 객체가 가변이라 값이 중간에 바뀔 수 있고, 월이 0부터 시작하는 등 헷갈리는 지점이 있었다. **새로 쓰는 코드는 `java.time` 으로 통일**하고, 옛 API는 기존 코드를 읽을 때 알아보는 정도면 충분하다.

### 3-6. 다음에 볼 키워드

- `Objects` 유틸 클래스 — `equals`·`hash`·`requireNonNull`
- `HashMap`·`HashSet` 의 동작 원리 (해시 버킷과 `hashCode`)
- 어노테이션(`@Override`·`@Test`)과 리플렉션의 조합
- `String` vs `StringBuilder` vs `StringBuffer`
- 정규표현식으로 `split`·`replaceAll` 쓰기, `String.join`·`strip`·`isBlank`
- 문자 인코딩(UTF-8·EUC-KR)과 `getBytes(Charset)`
- `Math`·`Random` 등 나머지 표준 유틸 클래스
- `ChronoUnit`·`Duration`·`Period` 로 기간 계산하기
- 얕은 복사·깊은 복사, `clone()`
- `Random` vs `SecureRandom` vs `Math.random()`, `ThreadLocalRandom`
- `BigDecimal` 로 금액 다루기, 부동소수점 오차
- 여러 값을 한 번에 돌려주는 방법 — 결과 클래스·`record`·`Map`
- UUID 버전(v4 난수 기반)과 DB 기본키로 쓸 때의 장단점
- csv 파싱과 파일 입출력(`Files.readAllLines`), 문자열 대신 클래스로 표를 담기

## 실습 파일

- `2026B_BE/src/day13/exam/exam1.java` (Object 최상위 클래스, toString·equals·hashCode, 문자열 리터럴 비교, Class·getClass·Class.forName 리플렉션)
- `2026B_BE/src/day13/exam/exam2.java` (래퍼 클래스와 오토박싱·언박싱, parseXXX·String.valueOf 타입 변환, LocalDate·LocalTime·LocalDateTime, DateTimeFormatter, plusXXX·getXXX)
- `2026B_BE/src/day13/exam/exam3.java` (String 클래스 — 문자열과 char 배열, 아스키·유니코드 코드값 변환, concat·length·charAt·replace·substring·split·indexOf·contains·getBytes, StringBuilder)
- `2026B_BE/src/day13/exam/exam4.java` (Random 난수 — nextInt·nextBoolean, UUID.randomUUID 고유 식별자)
- `2026B_BE/src/day13/exam/test.java` (콘솔 좌석 현황판 렌더링 — StringBuilder, Deque, switch 표현식, 한글 폭 계산)
- `2026B_BE/src/day13/practice/practice14.java` (문자열 주차 관리 실습 — 구분자로 담은 표 데이터, split·indexOf·substring, 메뉴 루프와 기능 메소드 분리, 쪼개기 헬퍼와 static 공유 리스트, DateTimeFormatter로 입차 시각 기록, 출차 시 고정폭 문자열 파싱·시각 간격·요금 계산)

## 관련 노트

[[Java MOC]] · [[Java day12 종합예제 JDBC DAO]] · [[Java day12 예외 처리와 JDBC]] · [[Java day11 인터페이스]] · [[Java day11 종합예제 인터페이스 DAO]] · [[Java day10 상속과 다형성]] · [[Java day09 ArrayList]] · [[Java day09 MVC 종합예제]] · [[Java day08 접근제한자와 static]] · [[Java day07 메소드와 미니프로젝트]] · [[Java day06 생성자와 콘솔 게시판]] · [[Java day04 제어문과 배열]] · [[Java day03 연산자]] · [[Java day02 타입 변환]] · [[Java day01 자바 구조와 자료형]] · [[SQL day02 테이블과 제약조건]] · [[JS day03 자료형과 연산자]] · [[KDT_2026 학습 지도]]
