---
출처: Claude 분석
원본: KDT_2026/2026B_BE/src/day11
작성일: 2026-08-12
tags: [학습, java]
---

# Java day11 — 인터페이스

> 실습 파일: `day11/exam/KeyBoard.java`(인터페이스 정의), `exam1.java`(기본·구현·업캐스팅), `exam2.java`(키보드 규격 예제, 멤버 4종, 다중 구현)
> 허브: [[Java MOC]] · 이전: [[Java day10 상속과 다형성]]

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

[[Java day09 ArrayList]] 에서 본 Stream API의 `filter(s -> s.length() > 3)`가 바로 이것 — `Predicate`라는 함수형 인터페이스의 람다 구현이다. JS의 화살표 함수와 겉모양이 같은 이유가 여기 있다.

### 3-3. 인터페이스가 실무에서 서 있는 자리

- **JDBC**: `Connection`, `Statement`, `ResultSet`이 전부 인터페이스다. MySQL 드라이버든 Oracle 드라이버든 같은 코드로 쓰는 이유
- **컬렉션**: `List<String> list = new ArrayList<>()` — 왼쪽이 인터페이스, 오른쪽이 구현체. `ArrayList`를 `LinkedList`로 바꿔도 쓰는 코드는 그대로
- **[[Java day09 MVC 종합예제]] 의 다음 단계**: DAO를 인터페이스로 뽑으면 메모리 저장 ↔ DB 저장을 갈아끼울 수 있다 (3-1에서 예고했던 그 구조)

### 3-4. 다음에 볼 키워드

- `abstract class` — 추상클래스 문법
- 함수형 인터페이스 4대장: `Function`, `Consumer`, `Supplier`, `Predicate`
- 마커 인터페이스(`Serializable`) — 메소드 없이 표식만 하는 인터페이스

## 실습 파일

- `2026B_BE/src/day11/exam/KeyBoard.java` (인터페이스 정의)
- `2026B_BE/src/day11/exam/exam1.java` (기본 문법, 구현, 업캐스팅)
- `2026B_BE/src/day11/exam/exam2.java` (키보드 규격, 멤버 4종, 다중 구현·상속)

## 관련 노트

[[Java MOC]] · [[Java day10 상속과 다형성]] · [[Java day09 MVC 종합예제]] · [[Java day09 ArrayList]] · [[Java 오버로딩 오버라이딩과 인터페이스(이관)]] · [[Repository Pattern]] · [[KDT_2026 학습 지도]]
