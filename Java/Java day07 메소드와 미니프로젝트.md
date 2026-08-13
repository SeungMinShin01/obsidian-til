---
출처: Claude 분석
원본: KDT_2026/2026B_BE/src/day07
작성일: 2026-08-10
tags: [학습, java]
---

# Java day07 — 메소드와 미니프로젝트

> 실습 파일: `day07/exam/exam1.java`(메소드), `day07/practice/miniProject.java`(세탁도우미), `practice9.java`
> 허브: [[Java MOC]] · 이전: [[Java day06 생성자와 콘솔 게시판]] · 다음: [[Java day08 접근제한자와 static]]

## 1. 배운 내용

### 1-1. 메소드 — exam1.java

```java
반환타입 메소드명(타입 매개변수) {
    return 반환값;
}
```

정리하면 이렇습니다.
- 함수를 자바에서는 **메소드**라고 부릅니다
- 클래스 내부에 선언합니다
- 목적: 재사용, 인수에 따른 서로 다른 결과물
- 반환 타입과 반환값의 타입이 일치해야 합니다
- 메소드명은 **소문자로 시작하는 카멜 표기법**

**4가지 조합** — `계산기` 클래스

| | 매개변수 없음 | 매개변수 있음 |
| --- | --- | --- |
| **반환값 있음** | `double getPi()` | `int add(int x, int y)` |
| **반환값 없음** | `void powerOn()` | `void printSum(int x, int y)` |

```java
class 계산기 {
    double getPi() { return 3.14; }
    void powerOn() { System.out.println("On"); return; }   // void도 return; 가능
    void printSum(int x, int y) { System.out.println(x + y); }
    int add(int x, int y) {
        this.printSum(x, y);   // 같은 클래스 안의 다른 메소드 호출
        return x + y;
    }
}
```

`void` 메소드에서 `return;`은 **거기서 즉시 끝내라**는 뜻입니다. 유효성 검사에서 조기 반환할 때 유용합니다.

### 1-2. this로 인스턴스 식별 — 사람타입

```java
class 사람타입 {
    String name;
    int age;
    String job;

    사람타입(String name) {   // 생성자
        this.name = name;
        age = 1;
    }

    void 취업성공(String 취업한직업) {   // 상태 변경 메소드
        this.job = 취업한직업;
        return;
    }
}
```

```java
사람타입 p1 = new 사람타입("강호동");
사람타입 p2 = new 사람타입("유재석");
p1.취업성공("개발자");

System.out.println(p1.job);   // 개발자
System.out.println(p2.job);   // null   ← p2는 영향 없음
```

**메소드는 클래스에 하나만 존재하지만, 실행될 때 `this`가 호출한 인스턴스를 가리킵니다.** 그래서 `p1.취업성공()`은 `p1`의 `job`만 바꿉니다.

설계 관점에서는 이렇게 대응됩니다.
- 사람이 가져야 할 상태 → 멤버변수
- 태어날 때 초기로 가져야 할 것 → 생성자
- 취업/행위/상태 변경 → 메소드

### 1-3. miniProject — 세탁도우미

지금까지 만든 것 중 구조가 가장 잘 잡힌 코드입니다. **3계층으로 분리**되어 있습니다.

```
miniProject (Controller)   메뉴 출력, 입력 받기, 결과 출력
        │
OverallRepository          데이터 저장·조회 (의류저장함수, 세탁법저장, findAll1, findAll2)
        │
의류 / 의류별세탁법 (Model)  데이터 구조
```

```java
switch (ch) {
    case 1:   // 의류 추가
        의류 새의류 = new 의류(의류ID, 의류명, 카테고리ID, 소재ID, 이미지경로);
        boolean result1 = repository.의류저장함수(새의류);
        System.out.println(result1 ? "[안내] 의류테이블 추가 성공" : "[안내] 추가 실패");
        break;
    case 3:   // 의류 출력
        의류[] 의류리스트 = repository.findAll1();
        for (의류 추가할의류 : 의류리스트) {
            if (추가할의류 != null) { ... }
        }
        break;
}
```

[[Java day08 접근제한자와 static]] 에서 배우는 MVC 패턴의 **M과 C를 실제로 분리**한 형태입니다.

**DB 스키마와의 대응**: `database/activity.sql`의 `CLOTHES`, `WASHINGGUIDE` 테이블이 그대로 `의류`, `의류별세탁법` 클래스가 되었습니다. **DB 테이블 → 자바 클래스** 매핑이 DTO의 본질입니다. → [[SQL day02 테이블과 제약조건]]

`scan.nextLine()`을 case마다 반복해서 넣은 이유는 [[Java day01 자바 구조와 자료형]] 2-1의 버퍼 문제 때문입니다.

### 1-4. practice9 — 메소드 8문제

`day07/practice/practice9.java`에서 클래스 8개로 메소드의 모든 조합을 연습했습니다.

```java
class Printer {                       // 매개변수 X, 반환 X
    void printMessage() { System.out.println("안녕하세요, 메소드입니다."); }
}
class Greeter {                       // 매개변수 O, 반환 X
    void greet(String name) { ... }
}
class SimpleCalculator {              // 매개변수 O, 반환 O
    int add(int x, int y) { return x + y; }
}
class Checker {                       // 매개변수 O, boolean 반환
    boolean isEven(int n) { return n % 2 == 0; }
}
class Lamp {                          // 상태를 바꾸는 메소드
    boolean isOn;
    void turnOn()  { isOn = true; }
    void turnOff() { isOn = false; }
}
```

```java
Checker c1 = new Checker();
if (c1.isEven(101)) System.out.println("짝수입니다.");
else System.out.println("홀수입니다.");

Lamp l1 = new Lamp();
l1.turnOn();   System.out.println(l1.isOn);   // true
l1.turnOff();  System.out.println(l1.isOn);   // false
```

**`boolean`을 반환하는 메소드는 `if`의 조건으로 바로 들어갑니다.** `isEven`, `isOn` 같은 `is~` 접두어가 이 용도입니다.

`Lamp`가 특히 좋은 예제입니다. 메소드가 값을 반환하지 않고 **객체의 상태를 바꾸는 것**이 목적입니다. [[Java day06 생성자와 콘솔 게시판]] 의 `취업성공()`과 같은 성격입니다.

**심화 3문제**
```java
class Product { boolean sell(int qty) { ... } }        // 재고 판매 성공 여부
class Visualizer { String getStar(int n) { ... } }     // 숫자를 별 문자열로
class ParkingLot { int calculateFee(int min) { ... } } // 주차 요금 계산
```

```java
System.out.println(v1.getStar(10));           // ★★★★★★★★★★
System.out.println(park1.calculateFee(65));   // 구간별 요금
System.out.println(park1.calculateFee(140));
```

`getStar`는 반복문으로 문자열을 누적하는 문제이고, `calculateFee`는 **조건 분기 + 계산**을 메소드로 캡슐화한 실전형 문제입니다. 요금 정책이 바뀌어도 이 메소드만 고치면 됩니다 — 메소드로 묶는 이유가 여기 있습니다.

## 2. 추가로 알면 좋은 활용법

### 2-1. 메소드 오버로딩

```java
int add(int x, int y) { return x + y; }
double add(double x, double y) { return x + y; }
int add(int x, int y, int z) { return x + y + z; }
```

**매개변수의 개수/타입/순서**가 다르면 됩니다. **반환 타입만 다른 건 오버로딩이 아닙니다.**

```java
int add(int x, int y) { }
double add(int x, int y) { }   // 컴파일 에러!
```

JS에는 오버로딩이 없어서 나중 정의가 앞의 것을 덮어씁니다. → [[JS day10 함수]]

### 2-2. 가변 인자

```java
int sum(int... nums) {   // 개수 제한 없이 받기
    int total = 0;
    for (int n : nums) total += n;
    return total;
}
sum(1, 2);  sum(1, 2, 3, 4, 5);
```

`System.out.printf("%s %d", a, b)`가 이 방식으로 만들어져 있습니다.

### 2-3. 지역변수 vs 멤버변수

```java
class 계산기 {
    int result;                    // 멤버변수 — 인스턴스가 살아있는 동안 유지, 기본값 자동
    int add(int x, int y) {
        int temp = x + y;          // 지역변수 — 메소드 끝나면 소멸, 기본값 없음
        return temp;
    }
}
```

**지역변수는 초기화하지 않으면 컴파일 에러**입니다. 멤버변수는 자동으로 0/null이 들어갑니다. 매개변수도 지역변수의 일종입니다.

### 2-4. Repository에 CRUD 마저 넣기

지금은 저장(C)과 전체 조회(R)만 있습니다.

```java
public 의류 findById(int 의류ID) {
    for (의류 c : 의류배열) {
        if (c != null && c.의류ID == 의류ID) return c;
    }
    return null;   // 못 찾으면 null
}

public boolean delete(int 의류ID) {
    for (int i = 0; i < 의류배열.length; i++) {
        if (의류배열[i] != null && 의류배열[i].의류ID == 의류ID) {
            의류배열[i] = null;
            return true;
        }
    }
    return false;
}

public boolean update(int 의류ID, String 새의류명) {
    의류 target = findById(의류ID);
    if (target == null) return false;
    target.의류명 = 새의류명;
    return true;
}
```

[[JS day14 게시판 CRUD]] 의 `view.js` 삭제 로직과 구조가 똑같습니다.

## 3. 더 나아가 알면 좋은 것

### 3-1. Repository를 인터페이스로

```java
interface ClothesRepository {
    boolean save(의류 c);
    의류[] findAll();
    의류 findById(int id);
}

class MemoryClothesRepository implements ClothesRepository { ... }
class DbClothesRepository implements ClothesRepository { ... }
```

Controller는 `ClothesRepository` 타입만 알면 되므로, **메모리 저장 → DB 저장으로 갈아탈 때 Controller를 한 줄도 안 고쳐도 됩니다.** Spring이 이 원리로 돌아갑니다.

→ [[Java 오버로딩 오버라이딩과 인터페이스(이관)]]

### 3-2. 싱글톤

저장소는 프로그램 전체에 하나만 있어야 합니다.

```java
public class OverallRepository {
    private static final OverallRepository INSTANCE = new OverallRepository();
    private OverallRepository() { }
    public static OverallRepository getInstance() { return INSTANCE; }
}
```

`private` 생성자 + `static` 인스턴스 조합입니다. → [[Java day08 접근제한자와 static]]

### 3-3. JDBC로 실제 DB 연결

`activity.sql`의 스키마와 클래스가 이미 1:1로 대응하므로 JDBC만 붙이면 됩니다.

```java
String sql = "INSERT INTO CLOTHES(CLOTHESNAME, CATEGORYID) VALUES(?, ?)";
try (Connection con = DriverManager.getConnection(url, id, pw);
     PreparedStatement ps = con.prepareStatement(sql)) {
    ps.setString(1, 의류명);
    ps.setInt(2, 카테고리ID);
    ps.executeUpdate();
}
```

**`PreparedStatement`를 반드시 쓰세요.** 문자열을 이어붙이면 SQL 인젝션에 뚫립니다. → [[SQL day03 DML과 조인]]

## 실습 파일

- `2026B_BE/src/day07/exam/exam1.java`
- `2026B_BE/src/day07/practice/miniProject.java`, `practice9.java`
- `2026B_BE/src/database/activity.sql`

## 관련 노트

[[Java MOC]] · [[Java day06 생성자와 콘솔 게시판]] · [[Java day08 접근제한자와 static]] · [[SQL day02 테이블과 제약조건]] · [[JS day10 함수]]
