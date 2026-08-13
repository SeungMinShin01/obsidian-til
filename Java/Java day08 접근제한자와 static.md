---
출처: Claude 분석
원본: KDT_2026/2026B_BE/src/day08
작성일: 2026-08-10
tags: [학습, java]
---

# Java day08 — 접근제한자와 static

> 실습 파일: `day08/exam/exam1~3.java`, `exam/package1/A.java`·`B.java`, `day08/pracitce/practice10.java`
> 허브: [[Java MOC]] · 이전: [[Java day07 메소드와 미니프로젝트]] · 다음: [[Java day09 ArrayList]]

## 1. 배운 내용

### 1-1. 접근제한자 4가지

| 제한자 | 같은 클래스 | 같은 패키지 | 자식 클래스 | 전체 |
| --- | :---: | :---: | :---: | :---: |
| `public` | O | O | O | O |
| `protected` | O | O | O | X |
| (default, 생략) | O | O | X | X |
| `private` | O | X | X | X |

**적용 대상**: 클래스, 멤버변수, 메소드, 생성자 — 선언 타입 앞에 붙입니다.

**목적**: 캡슐화. 실질적인 정보를 알약처럼 감싸 접근을 제한합니다.

`package1/A.java`와 `B.java`가 이걸 패키지 경계로 정확히 실험합니다.

```java
// package1/A.java
public class A {
    public int 공개변수;
    private int 비공개변수;
    int 일반변수;              // default

    public void 공개메소드() { }
    private void 비공개메소드() { }
}

// package1/B.java — 같은 패키지
public class B {
    public void 메소드() {
        A a = new A();
        a.공개변수 = 3;    // 가능
        a.일반변수 = 3;    // 가능 (같은 패키지)
        // a.비공개변수 = 3;  불가능
    }
    private B() { }       // 비공개 생성자 — 외부에서 객체 생성 금지
}

// day08.exam/exam1.java — 다른 패키지
A a = new A();
a.공개변수 = 3;     // 가능
// a.일반변수;      불가능 (다른 패키지)
// B b = new B();   불가능 (생성자가 private)
```

### 1-2. 캡슐화 — private 필드 + getter/setter

```java
class User {
    private String name;      // 직접 접근 차단
    private int age;

    public void setName(String name) {
        if (name.length() < 1) return;   // 유효성 검사
        this.name = name;
    }
    public String getName(String 비밀번호) { return this.name; }

    @Override
    public String toString() {
        return "User [name=" + name + ", age=" + age + "]";
    }
}
```

**캡슐화의 핵심은 "숨기는 것" 자체가 아니라 "관문을 두는 것"입니다.** `practice10.java`의 `Score`가 좋은 예입니다.

```java
class Score {
    private int score;
    public void setScore(int score) {
        if (score >= 0 && score <= 100) this.score = score;
        else System.out.println("유효하지 않은 점수입니다.");
    }
}
s1.setScore(85);    // 정상
s1.setScore(120);   // 거부
```

필드가 public이면 `s1.score = 120;`을 막을 방법이 없습니다.

### 1-3. VO vs DTO

| | 구성 | 용도 |
| --- | --- | --- |
| **VO** (Value Object) | getter만 | 읽기 전용 |
| **DTO** (Data Transfer Object) | getter + setter | 읽기/쓰기, 계층 간 데이터 전달 |

**DTO 관례 4가지**
1. 멤버변수는 전부 `private`
2. getter/setter 제공
3. `toString()` 제공
4. 생성자 2개 — 기본 생성자 + 전체 매개변수 생성자

### 1-4. MVC 패턴

| 계층 | 역할 | 기술 |
| --- | --- | --- |
| **M**odel | 데이터 담당 (DTO, VO) | Controller ↔ 외부 DB/클라우드 |
| **V**iew | 입출력 담당 | HTML/CSS/JS/React/Flutter |
| **C**ontroller | 제어·중계 | Java/Python/Node.js |

[[Java day07 메소드와 미니프로젝트]] 의 `miniProject`가 이미 M과 C를 분리한 형태입니다.

### 1-5. final과 static — exam3.java

```java
class D {
    public final int 고정변수 = 3;         // 초기값 필수, 이후 수정 불가
    public static int 정적변수 = 10;       // 인스턴스 없이 클래스명으로 접근
    public int 멤버변수 = 10;              // 인스턴스마다 별도 메모리
    public static final int 상수 = 30;     // 상수
}
```

| | 접근 방법 | 메모리 |
| --- | --- | --- |
| 멤버변수 | `객체명.멤버변수` | 인스턴스마다 1개 |
| static 변수 | `클래스명.정적변수` | 프로그램 전체에 1개 |

```java
D.정적변수 = 20;
D.정적변수 = 30;      // 총 메모리 1개

D 변수1 = new D();  변수1.멤버변수 = 20;
D 변수2 = new D();  변수2.멤버변수 = 30;   // 총 메모리 2개
```

**static의 생명주기**: 프로그램 시작 시 할당되고 종료 시 사라집니다.

**중요한 제약**: static에서는 non-static 멤버에 접근할 수 없습니다. static이 먼저 메모리에 올라가는데 그때 인스턴스는 아직 없기 때문입니다. 이게 `main`이 static인데 클래스 멤버를 바로 못 쓰는 이유입니다.

### 1-6. practice10.java — 6문제 종합

| 클래스 | 배운 것 |
| --- | --- |
| `Member` | 기본 getter/setter |
| `Score` | setter 유효성 검사 |
| `BankAccount` | 생성자로만 초기화 + getter만 (= VO) |
| `CircleCalculator` | `final double PI` 상수 |
| `TicketMachine` | `static int totalTickets` 공유 카운터 |
| `GameConfig` | `public static final` 설정 상수 |

`TicketMachine`이 static을 가장 잘 보여줍니다. **기계를 3대 만들어도 `totalTickets`는 하나**라서 전체 발권 수가 누적됩니다.

```java
machine1.issueTicket();
machine1.issueTicket();
machine2.issueTicket();
TicketMachine.printTotalTickets();   // 3
```

## 2. 추가로 알면 좋은 활용법

### 2-1. `final`의 세 가지 얼굴

```java
final int x = 3;            // 변수: 재할당 불가
final void method() { }     // 메소드: 오버라이딩 불가
final class Utils { }       // 클래스: 상속 불가 (String이 이 경우)
```

**주의**: `final List<String> list = new ArrayList<>();`에서 `list.add("a")`는 **가능합니다.** final은 "참조를 바꿀 수 없다"이지 "내용을 바꿀 수 없다"가 아닙니다. JS의 `const`와 정확히 같습니다. → [[JS day02 변수와 입출력]]

### 2-2. static 초기화 블록

```java
class Config {
    static final Map<String, String> MAP = new HashMap<>();
    static {
        MAP.put("key", "value");   // 클래스가 처음 로딩될 때 한 번만
    }
}
```

## 3. 더 나아가 알면 좋은 것

### 3-1. Lombok

클래스가 늘어나면 getter/setter가 폭발합니다.

```java
@Getter @Setter @ToString
@NoArgsConstructor @AllArgsConstructor
public class User {
    private String name;
    private int age;
}
```

어노테이션 5줄이 코드 50줄을 대체합니다. 컴파일 시점에 코드를 생성하는 방식이라 IDE 플러그인이 필요합니다.

### 3-2. 싱글톤 패턴

```java
public class Repository {
    private static final Repository INSTANCE = new Repository();
    private Repository() { }
    public static Repository getInstance() { return INSTANCE; }
}
```

`private` 생성자 + `static` 인스턴스. [[Java day07 메소드와 미니프로젝트]] 의 `OverallRepository`가 딱 이 패턴이 어울리는 자리입니다.

### 3-3. 캡슐화가 깨지는 흔한 실수

```java
public class Team {
    private List<String> members = new ArrayList<>();
    public List<String> getMembers() { return members; }   // 위험!
}

team.getMembers().clear();   // 외부에서 내부 리스트를 통째로 비움
```

**방어적 복사**로 막습니다.
```java
public List<String> getMembers() {
    return new ArrayList<>(members);
    // 또는 Collections.unmodifiableList(members);
}
```

### 3-4. `record` (Java 16+)

```java
record User(String name, int age) { }
```
DTO 관례 4가지가 전부 자동으로 만들어집니다. 단, 불변이라 setter는 없습니다.

## 실습 파일

- `2026B_BE/src/day08/exam/exam1.java`, `exam2.java`, `exam3.java`
- `2026B_BE/src/day08/exam/package1/A.java`, `B.java`
- `2026B_BE/src/day08/pracitce/practice10.java`, `test.java`

## 관련 노트

[[Java MOC]] · [[Java day07 메소드와 미니프로젝트]] · [[Java day09 ArrayList]] · [[Java 오버로딩 오버라이딩과 인터페이스(이관)]] · [[JS day10 함수]]
