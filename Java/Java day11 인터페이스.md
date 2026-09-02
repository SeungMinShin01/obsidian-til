---
출처: Claude 분석
원본: KDT_2026/2026B_BE/src/day11
작성일: 2026-08-12
tags: [학습, java]
---

# Java day11 — 인터페이스

> 실습 파일: `day11/exam/KeyBoard.java`(인터페이스 정의), `exam1.java`(기본·구현·업캐스팅), `exam2.java`(키보드 규격 예제, 멤버 4종, 다중 구현), `exam3.java`(타이어 교체·익명 구현체), `day11/practice/practice13.java`(연습문제 9개)
> 허브: [[Java MOC]] · 이전: [[Java day10 상속과 다형성]] · 다음: [[Java day11 종합예제 인터페이스 DAO]]

## 1. 배운 내용

### 1-1. 타입 지도에서 인터페이스의 자리

```
기본타입(8개): byte, short, int, long, float, double, char, boolean
참조타입:     [ ]배열, 클래스(String, Dto, Scanner ...), 인터페이스  ← 오늘 추가
```

인터페이스도 **참조타입**이다. 즉 변수의 타입 자리에 올 수 있다 — 이게 뒤에 나오는 다형성의 출발점이다.

### 1-2. 인터페이스란 — 상수 + 추상메소드

```java
public interface KeyBoard {
    // 1. 상수 — 초기값 필수
    public static final String info = "인텔";
    String date = "2026-08-12";        // 붙이지 않아도 자동으로 public static final

    // 2. 추상메소드 — { } 없이 선언부만
    public abstract void aKey();
    int bkey(int x);                   // 생략해도 자동으로 public abstract
}
```

인터페이스의 핵심 성질 세 가지:

- 필드는 전부 **상수**가 된다 (`public static final` 생략 가능, 초기값 필수)
- 메소드는 기본이 **추상메소드** — 선언부만 있고 구현부 `{ }`가 없다
- **생성자가 없다 → `new` 불가 → 인스턴스를 만들 수 없다**

```java
// ExamInterFace ei = new ExamInterFace();   // 불가 — 생성자가 없다
```

그럼 뭐에 쓰나? **목적은 여러 인스턴스의 호환/관리**다. 인터페이스는 "무엇을 할 수 있어야 한다"는 규격만 정하고, 실제 동작은 구현 클래스가 채운다.

### 1-3. implements — 구현은 오버라이딩이 필수다

```java
class ExamClass implements ExamInterFace {
    @Override
    public void method1(int x) { System.out.println(x); }

    @Override
    public int method2(int x, int y) { return x + y; }
}
```

비교해서 기억할 것:

| | extends (상속) | implements (구현) |
| --- | --- | --- |
| 오버라이딩 | **선택** — 안 하면 부모 것 사용 | **필수** — 추상메소드를 전부 채워야 오류가 사라진다 |
| 물려받는 것 | 완성된 멤버 | 채워야 할 선언부 |

추상메소드를 모두 구현하는 순간 클래스의 컴파일 오류가 사라진다 — IDE의 빨간줄이 "아직 안 지킨 약속"의 목록인 셈이다.

### 1-4. 인터페이스 타입으로 업캐스팅

```java
ExamInterFace ei = new ExamClass();   // 업캐스팅 — 인터페이스 타입에 구현체 대입
ei.method1(10);                       // 실행되는 건 ExamClass의 오버라이딩
```

[[Java day10 상속과 다형성]] 에서 부모 타입에 자식을 담던 것과 같은 원리인데, 부모 자리에 **인터페이스**가 온다. 인터페이스 타입이더라도 **오버라이딩(구현체의 메소드)이 우선** 실행된다.

### 1-5. 키보드 규격 예제 — 다형성의 실전형

`exam2.java`의 흐름이 인터페이스의 존재 이유를 그대로 보여준다.

```java
KeyBoard myBoard;                 // 키보드 "규격" 타입 변수

myBoard = new SportsGame();       // 스포츠게임 실행
myBoard.aKey();                   // "슈팅"

myBoard = new ActionGame();       // 게임을 갈아끼움 (변수는 단 하나의 자료만 저장)
myBoard.aKey();                   // "공격"
```

```java
class SportsGame implements KeyBoard {
    public void aKey() { System.out.println("슈팅"); }
    public int bkey(int x) { System.out.println("수비"); return x; }
}
class ActionGame implements KeyBoard {
    public void aKey() { System.out.println("공격"); }
    public int bkey(int x) { System.out.println("방어"); return x; }
}
```

같은 `aKey()`를 눌러도 꽂혀 있는 게임에 따라 동작이 달라진다. **키보드(규격)는 그대로, 게임(구현)만 바뀐다** — [[Java day10 상속과 다형성]] 의 타이어 교체와 똑같은 구조이고, 차이는 부모가 클래스냐 인터페이스냐뿐이다.

> **다형성을 구현하는 두 가지 길: 1) 상속 2) 인터페이스**

### 1-6. 인터페이스 멤버 4종

```java
interface Buy {
    public abstract void method1();        // 1) 추상메소드 — 구현부 없음, 구현 필수
    public default void method2() { }      // 2) 디폴트메소드 — 구현부 있음, 재정의 선택
    public static void method3() { }       // 3) 정적메소드 — 구현체 없이 Buy.method3()로 사용
    private void method4() { }             // 4) 비공개메소드 — 하위에서 오버라이딩 불가
}
```

| 종류 | 구현부 | 구현 클래스의 의무 | 용도 |
| --- | --- | --- | --- |
| 추상 | 없음 | **필수 구현** | 규격의 본체 |
| 디폴트 | 있음 | 선택 (그대로 써도 됨) | 기존 구현체를 안 깨고 기능 추가 |
| 정적 | 있음 | — (인터페이스명으로 직접 호출) | 규격에 딸린 도우미 |
| 비공개 | 있음 | — (외부/하위 접근 불가) | 디폴트메소드들의 공통 코드 분리 |

### 1-7. 다중 구현과 인터페이스 상속

클래스 상속(`extends`)은 하나만 되지만, **인터페이스 구현은 여러 개**가 된다.

```java
class Customer extends Object implements Buy, Sell {
    // 두 인터페이스의 추상메소드만 전부 구현하면 된다
    public void method1() { }   // Buy의 추상
    public void method5() { }   // Sell의 추상
}
```

인터페이스끼리는 상속도 된다 — 규격을 합쳐 더 큰 규격을 만든다.

```java
interface CustomerController extends Buy, Sell {   // 인터페이스는 다중 상속 가능
    void order();                                  // 자기 추상메소드 추가
}

class Customer2 implements CustomerController {
    // Buy + Sell + order() 전부 구현해야 한다
}
```

### 1-8. 익명 구현체 — 클래스 선언 없이 일회성 구현

`exam3.java`의 타이어 교체 예제가 인터페이스 다형성의 또 다른 쓰임을 보여준다. `Car`가 `Tire` 규격 타입 필드를 갖고, 꽂히는 타이어(구현체)에 따라 `run()` 의 동작이 달라진다.

```java
Car myCar = new Car();

myCar.tire = new HankookTire();   // 구현체 교체
myCar.run();                      // 한국타이어 회전
myCar.tire = new KumhoTire();
myCar.run();                      // 금호타이어 회전
```

구현 클래스를 딱 한 번만 쓸 거라면 클래스를 따로 선언하지 않고 그 자리에서 만들 수 있다 — **익명 구현체**다.

```java
myCar.tire = new Tire() {          // Tire는 인터페이스라 원래 new 불가지만
    @Override
    public void roll() {           // 그 자리에서 추상메소드를 구현하면 가능
        System.out.println("일반타이어 회전");
    }
};
myCar.run();
```

`new 인터페이스명() { 오버라이딩 }` 형태로, 이름 없는 구현체를 한 번 쓰고 버린다. 인터페이스 타입 변수에 뭐가 꽂혔는지 확인하는 건 여기서도 `instanceof` 다(`myCar.tire instanceof KumhoTire`). 익명 구현체는 뒤의 3-2 함수형 인터페이스·람다로 이어지는 출발점이다.

### 1-9. practice13 — 인터페이스 9문제

`day11/practice/practice13.java`에서 오늘 배운 문법을 문제 아홉 개로 한 번에 훑었습니다. 각 문제가 위의 어떤 절에 해당하는지 대응시켜 두면 복습이 빨라집니다.

**1번 — 구현 필수와 다형성의 기본형**

```java
interface Soundable { public abstract void makeSound(); }

class Cat implements Soundable { public void makeSound() { System.out.println("야옹"); } }
class Dog implements Soundable { public void makeSound() { System.out.println("멍멍"); } }
```

같은 규격을 두 클래스가 각자의 방식으로 채웁니다. → 1-3

**2번 — 상수 필드**

```java
interface RemoteControl {
    public final static int MAX_VOLUME = 10;
    public final static int MIN_VOLUME = 0;
}
System.out.println(RemoteControl.MAX_VOLUME);   // 구현체 없이 인터페이스명으로 바로 접근
```

인터페이스 필드는 `public static final`이라 인스턴스 없이 인터페이스 이름으로 읽습니다. → 1-2, 2-3

**3번 — 매개변수 타입을 인터페이스로 받기**

```java
class Character {
    public void useWeapon(Attackable weapon) { weapon.attack(); }
}
character.useWeapon(sword);   // 검으로 공격
character.useWeapon(gun);     // 총으로 공격
```

여기가 인터페이스의 실전 요령입니다. `useWeapon`은 `Sword`도 `Gun`도 모르고 `Attackable`만 압니다. 무기를 새로 만들어도 `Character` 쪽 코드는 그대로입니다. → 2-1

**4번 — 다중 구현**

```java
class Duck implements Flyable, Swimmable {
    public void fly()  { System.out.println("하늘을 난다."); }
    public void Swin() { System.out.println("물에서 헤엄친다."); }
}
```

클래스 상속은 하나뿐이지만 구현은 여러 개를 겹칠 수 있습니다. "날 수 있다 + 헤엄칠 수 있다"처럼 능력을 조합하는 자리입니다. → 1-7, 3-1의 can-do

**5번 — Object 타입에 담고 instanceof로 되찾기**

```java
Object obj = new Duck();
if (obj instanceof Flyable)   { ((Duck) obj).fly(); }
if (obj instanceof Swimmable) { ((Duck) obj).Swin(); }
```

`instanceof`의 오른쪽에 **인터페이스도 올 수 있다**는 게 이 문제의 핵심입니다. "이 객체가 날 수 있는 놈인가?"를 클래스 이름이 아니라 능력으로 물어보는 방식입니다. → 2-4

**6번 — DAO 규격 갈아끼우기**

```java
DataAccessObject dao;
dao = new OracleDao();  dao.save();   // Oracle Db에 저장
dao = new MySqlDao();   dao.save();   // MYSQL DB 저장
```

3-3에서 예고한 구조가 그대로 나왔습니다. 저장소를 바꿔도 `dao.save()`를 부르는 쪽은 손대지 않습니다. → [[Java day11 종합예제 인터페이스 DAO]]

**7번 — 익명 구현체**

```java
Greeting g = new Greeting() {
    @Override
    public void welcome() { System.out.println("환영 인사"); }
};
g.welcome();
```

한 번만 쓸 구현이라 클래스를 따로 만들지 않았습니다. 추상메소드가 하나뿐이라 나중에 람다(`Greeting g = () -> System.out.println("환영 인사");`)로도 쓸 수 있는 형태입니다. → 1-8, 3-2

**8번 — 디폴트메소드**

```java
interface Device {
    void turnOn();
    void turnOff();
    public default void setMute(boolean mute) {
        if (mute) System.out.println("무음 처리합니다.");
        else      System.out.println("무음모드 종료");
    }
}
class Television implements Device { /* turnOn, turnOff만 구현 */ }
```

`Television`은 `setMute`를 구현하지 않았는데도 호출됩니다. 디폴트메소드는 구현이 선택이라 그렇습니다. → 1-6, 2-2

**9번 — 정적메소드**

```java
interface Calculator {
    public static int plus(int x, int y) { return x + y; }
}
System.out.println(Calculator.plus(10, 20));   // 30
```

구현 클래스도, 인스턴스도 없이 인터페이스 이름으로 바로 호출합니다. 규격에 딸린 도우미 함수 자리입니다. → 1-6

정리하면 이 아홉 문제는 **추상 → 상수 → 매개변수 다형성 → 다중 구현 → instanceof → 교체 → 익명 → 디폴트 → 정적** 순으로, 인터페이스에서 쓰는 문법이 전부 한 번씩은 나옵니다.

## 2. 추가로 알면 좋은 활용법

### 2-1. "규격 먼저" 설계 순서

exam2의 순서가 그대로 설계 순서다: ① 규격(인터페이스)을 먼저 정하고 → ② 구현체를 만들고 → ③ 쓰는 쪽은 규격 타입으로만 받는다. 쓰는 쪽 코드에 구현체 이름이 없으면 구현체를 갈아끼워도 쓰는 쪽이 안 바뀐다.

이게 [[Repository Pattern]] 의 핵심 그 자체다 — `RestaurantRepository`(규격) / `RestaurantRepositoryImpl`(구현) / Controller는 규격만 아는 구조. day11의 KeyBoard 예제를 이해했다면 Repository Pattern은 같은 것의 데이터 버전이다.

### 2-2. 디폴트메소드가 존재하는 이유

인터페이스에 추상메소드를 하나 추가하면 **기존 구현체 전부가 컴파일 오류**가 난다(구현 필수라서). `default`로 추가하면 기존 구현체는 그대로 두고 새 기능이 얹힌다. "이미 배포된 규격을 어떻게 확장하는가"에 대한 답으로 Java 8에서 들어온 문법이다.

### 2-3. 상수 필드 주의

인터페이스의 필드는 전부 `public static final`이라 **구현체별로 다른 값을 가질 수 없다.** 상태(값)가 구현체마다 달라야 하면 그건 인터페이스 상수가 아니라 클래스의 멤버변수 자리다. 인터페이스는 행위(메소드)의 규격이지 상태의 저장소가 아니다.

### 2-4. 타입 확인은 여기서도 instanceof

```java
if (myBoard instanceof SportsGame) { ... }
```

인터페이스 타입 변수에 뭐가 꽂혀 있는지 확인하는 방법은 [[Java day10 상속과 다형성]] 의 `instanceof` 그대로다.

## 3. 더 나아가 알면 좋은 것

### 3-1. 추상클래스 vs 인터페이스 — 선택 기준

| | 추상클래스 | 인터페이스 |
| --- | --- | --- |
| 상속/구현 개수 | 1개만 | 여러 개 |
| 상태(멤버변수) | 가질 수 있음 | 상수만 |
| 관계의 의미 | "~의 한 종류다" (is-a) | "~을 할 수 있다" (can-do) |

공통 **상태와 부분 구현**을 물려주고 싶으면 추상클래스, 순수하게 **행위 규격**만 정하고 싶으면 인터페이스. 실무에서는 인터페이스 쪽 비중이 훨씬 크다 — 다중 구현이 되고 결합이 느슨해서다.

### 3-2. 함수형 인터페이스와 람다

추상메소드가 **딱 1개**인 인터페이스는 람다식으로 구현체를 즉석에서 만들 수 있다.

```java
interface Calculator { int calc(int x, int y); }

Calculator add = (x, y) -> x + y;      // 클래스 선언 없이 구현
System.out.println(add.calc(3, 4));    // 7
```

Java day09 ArrayList 에서 본 Stream API의 `filter(s -> s.length() > 3)`가 바로 이것 — `Predicate`라는 함수형 인터페이스의 람다 구현이다. JS의 화살표 함수와 겉모양이 같은 이유가 여기 있다.

### 3-3. 인터페이스가 실무에서 서 있는 자리

- **JDBC**: `Connection`, `Statement`, `ResultSet`이 전부 인터페이스다. MySQL 드라이버든 Oracle 드라이버든 같은 코드로 쓰는 이유
- **컬렉션**: `List<String> list = new ArrayList<>()` — 왼쪽이 인터페이스, 오른쪽이 구현체. `ArrayList`를 `LinkedList`로 바꿔도 쓰는 코드는 그대로
- **Java day09 MVC 종합예제 의 다음 단계**: DAO를 인터페이스로 뽑으면 메모리 저장 ↔ DB 저장을 갈아끼울 수 있다 (3-1에서 예고했던 그 구조)

### 3-4. 다음에 볼 키워드

- `abstract class` — 추상클래스 문법
- 함수형 인터페이스 4대장: `Function`, `Consumer`, `Supplier`, `Predicate`
- 마커 인터페이스(`Serializable`) — 메소드 없이 표식만 하는 인터페이스

## 실습 파일

- `2026B_BE/src/day11/exam/KeyBoard.java` (인터페이스 정의)
- `2026B_BE/src/day11/exam/exam1.java` (기본 문법, 구현, 업캐스팅)
- `2026B_BE/src/day11/exam/exam2.java` (키보드 규격, 멤버 4종, 다중 구현·상속)
- `2026B_BE/src/day11/exam/exam3.java` (타이어 교체 다형성, 익명 구현체)
- `2026B_BE/src/day11/practice/practice13.java` (연습문제 9개 — 추상·상수·다중 구현·익명·디폴트·정적)

## 관련 노트

[[Java MOC]] · [[Java day11 종합예제 인터페이스 DAO]] · [[Java day10 상속과 다형성]] · Java day09 MVC 종합예제 · Java day09 ArrayList · Java 오버로딩 오버라이딩과 인터페이스(이관) · [[Repository Pattern]] · [[KDT_2026 학습 지도]]
