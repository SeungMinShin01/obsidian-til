---
출처: Claude 분석
원본: KDT_2026/2026B_BE/src/day13/exam
작성일: 2026-08-19
tags: [학습, java]
---

# Java day13 — Object 클래스와 리플렉션

> 실습 파일: `day13/exam/exam1.java`(Object·Class·리플렉션), `exam2.java`(래퍼 클래스·타입 변환·날짜/시간), `test.java`(콘솔 화면 렌더링)
> 허브: [[Java MOC]] · 이전: [[Java day12 종합예제 JDBC DAO]]

day12까지는 내가 만든 클래스들(DTO·DAO·Controller)을 어떻게 조립하는지가 주제였다. day13은 방향이 반대다. **자바가 이미 만들어 둔 클래스(라이브러리)를 어떻게 쓰는가**, 그중에서도 모든 클래스의 조상인 `Object` 와 클래스 자신의 정보를 담은 `Class` 를 본다.

라이브러리는 다른 사람들이 만들어 둔 클래스·메소드의 집합이다. `Scanner`·`String`·`ArrayList` 도 전부 라이브러리이고, day12에서 `lib` 폴더에 넣은 MySQL 드라이버 jar도 라이브러리다.

같은 흐름에서 **기본타입을 객체로 감싸는 래퍼 클래스**와 **날짜·시간을 다루는 `java.time` 패키지**도 함께 본다. 셋 다 "이미 만들어져 있으니 가져다 쓰는" 자바 표준 라이브러리다.

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
- `Math`·`Random` 등 나머지 표준 유틸 클래스
- `ChronoUnit`·`Duration`·`Period` 로 기간 계산하기
- 얕은 복사·깊은 복사, `clone()`

## 실습 파일

- `2026B_BE/src/day13/exam/exam1.java` (Object 최상위 클래스, toString·equals·hashCode, 문자열 리터럴 비교, Class·getClass·Class.forName 리플렉션)
- `2026B_BE/src/day13/exam/exam2.java` (래퍼 클래스와 오토박싱·언박싱, parseXXX·String.valueOf 타입 변환, LocalDate·LocalTime·LocalDateTime, DateTimeFormatter, plusXXX·getXXX)
- `2026B_BE/src/day13/exam/test.java` (콘솔 좌석 현황판 렌더링 — StringBuilder, Deque, switch 표현식, 한글 폭 계산)

## 관련 노트

[[Java MOC]] · [[Java day12 종합예제 JDBC DAO]] · [[Java day12 예외 처리와 JDBC]] · [[Java day11 인터페이스]] · [[Java day11 종합예제 인터페이스 DAO]] · [[Java day10 상속과 다형성]] · [[Java day09 ArrayList]] · [[Java day09 MVC 종합예제]] · [[Java day08 접근제한자와 static]] · [[Java day07 메소드와 미니프로젝트]] · [[Java day04 제어문과 배열]] · [[Java day03 연산자]] · [[Java day02 타입 변환]] · [[Java day01 자바 구조와 자료형]] · [[JS day03 자료형과 연산자]] · [[KDT_2026 학습 지도]]
