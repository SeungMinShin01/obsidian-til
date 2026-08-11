---
출처: 이관
원본: 노션 > Problem Solving > 정보처리기사 > day01, 1
작성일: 2026-08-10
tags: [java, 오버로딩, 오버라이딩, 인터페이스, 다형성]
---

# Java 오버로딩·오버라이딩과 인터페이스 (이관)

> 노션 `정보처리기사` 폴더의 `day01`, `1` 페이지에 섞여 있던 Java 부분만 이 폴더로 발췌·이관했습니다. 원본 페이지는 그대로 두었습니다.

## 1. 오버로딩 vs 오버라이딩 — 출력 결과 문제

```java
class A {
    String f(Object x) { return "1"; }
    String g() { return f("a"); }
}

class B extends A {
    String f(Object x) { return "2"; }   // 오버라이딩
    String f(String x) { return "3"; }   // 오버로딩
}

public class Test {
    public static void main(String[] args) {
        A a = new B();
        System.out.println(a.g());
    }
}
```

**답: `2`**

### 3단계 추적

**1단계 — `g()` 메서드 디스패치 (런타임)**
`g()`는 일반 메서드라 오버라이딩이 적용됩니다. Java는 변수의 **선언 타입(A)** 이 아니라 **실제 객체 타입(B)** 으로 메서드를 찾습니다. `B`가 `g()`를 오버라이딩하지 않았으므로 `A`에서 물려받은 `g()`가 실행됩니다.
→ `A`의 `g()` 본문: `return f("a");`

**2단계 — `f("a")` 오버로드 선택 (컴파일 타임)**
`A`의 `g()` 본문에 적힌 `f("a")`는 `this.f("a")`와 같습니다. 어떤 `f`를 부를지는 **컴파일 시점에 결정**되며, 후보는 **그 코드가 적힌 위치에서 보이는 메서드**뿐입니다.
`f("a")`는 `A` 클래스 안에 적혀 있으므로 `A`의 시야에서 보이는 것만 후보입니다.
- `A`에는 `f(Object x)` 하나뿐
- `B`의 `f(String x)`는 `A`의 시야에 없어 **후보조차 되지 않음**

→ 호출은 `f(Object)`로 컴파일 타임에 고정됩니다.

**3단계 — `f(Object)` 메서드 디스패치 (런타임)**
`f(Object)`로 고정된 호출이 실행될 때 다시 오버라이딩이 적용됩니다. `this`는 실제 객체인 `B`를 가리키고, `B`가 `f(Object)`를 오버라이딩했으므로 **`B`의 `f(Object)`가 실행되어 `"2"`를 반환**합니다.

### 한 줄 요약

> **오버로딩은 컴파일 타임, 오버라이딩은 런타임.**
> 어떤 시그니처를 부를지는 컴파일러가 정하고, 그 시그니처의 어느 구현을 쓸지는 JVM이 정합니다.

### 업캐스팅

```java
A a = new B();   // 업캐스팅
```
실제 객체는 `B`지만 변수의 선언 타입은 `A`입니다. 이 상태에서 `a.f("a")`를 직접 호출하면 `A`의 시야만 보이므로 `f(Object)`가 선택되어 역시 `"2"`가 나옵니다. `"3"`을 보려면 `((B) a).f("a")`처럼 다운캐스팅해야 합니다.

### 오버로딩 vs 오버라이딩 정리

| | 오버로딩 | 오버라이딩 |
|---|---|---|
| 위치 | 같은 클래스(또는 상속받은 클래스) | 부모-자식 |
| 조건 | 이름 같고 **매개변수 다름** | 이름·매개변수·반환타입 **모두 같음** |
| 결정 시점 | 컴파일 타임 (정적 바인딩) | 런타임 (동적 바인딩) |
| 반환 타입 | 달라도 됨 (단, 반환 타입만 다른 건 불가) | 같거나 하위 타입 |
| 접근 제한 | 무관 | 부모보다 **좁힐 수 없음** |

## 2. 인터페이스와 다형성

| 개념 | 설명 | 예시 |
|---|---|---|
| **인터페이스** | "이런 기능을 만들어라"는 약속(계약) | `interface Person { }` |
| **implements** | 인터페이스를 구현하겠다는 선언 | `class A implements Person { }` |
| **추상 메서드** | 선언만 있고 본문이 없는 메서드 | `void sayHello();` |
| **다형성** | 같은 메서드 호출이 객체에 따라 다르게 동작 | `Person p = new A();` |

```java
interface Person {
    void sayHello();   // 본문 없음, 세미콜론으로 끝남
}

class Student implements Person {
    public void sayHello() {   // public 필수!
        System.out.println("학생입니다");
    }
}
```

### `public`을 반드시 붙여야 하는 이유

인터페이스는 "외부에 공개하는 약속"이므로 메서드가 **자동으로 public**입니다. Java는 오버라이딩 시 접근 범위를 **좁힐 수 없으므로**, 구현 클래스에서도 `public`을 명시해야 합니다. 생략하면 default 접근 제어자가 적용되어 public보다 좁아지고 컴파일 에러가 납니다.

`day08`에서 배운 접근제한자 규칙이 여기서 다시 등장합니다.

### extends vs implements

| 키워드 | 대상 | 의미 | 개수 |
|---|---|---|---|
| `extends` | 클래스 → 클래스 | 상속 (기능을 물려받음) | **1개만** |
| `implements` | 클래스 → 인터페이스 | 구현 (약속한 기능을 만듦) | **여러 개 가능** |

Java는 다중 상속을 금지하지만 인터페이스는 여러 개 구현할 수 있습니다.
```java
class A extends B implements C, D, E { }
```

## 3. 추가로 알면 좋은 것

### 인터페이스를 쓰는 실제 이유

```java
interface Repository {
    void save(String data);
}

class MemoryRepository implements Repository { ... }
class DbRepository implements Repository { ... }

// 사용하는 쪽
Repository repo = new MemoryRepository();   // 나중에 DbRepository로 바꿔도
repo.save("데이터");                          // 이 코드는 그대로
```

`day07/practice/miniProject.java`의 `OverallRepository`를 인터페이스로 빼두면, 메모리 저장 → DB 저장으로 갈아탈 때 Controller 코드를 한 줄도 안 고쳐도 됩니다. Spring이 이 원리로 돌아갑니다.

### 추상 클래스 vs 인터페이스

| | 추상 클래스 | 인터페이스 |
|---|---|---|
| 필드 | 가능 | `public static final` 상수만 |
| 생성자 | 있음 | 없음 |
| 구현된 메서드 | 가능 | `default` 메서드로 가능 (Java 8+) |
| 다중 | 불가 (extends 1개) | 가능 |
| 의미 | "~는 ~이다" (is-a) | "~는 ~을 할 수 있다" (can-do) |

`Dog extends Animal` (개는 동물이다) vs `Dog implements Runnable` (개는 달릴 수 있다)

### Java 8+ 인터페이스의 확장

```java
interface Person {
    void sayHello();                                    // 추상 메서드
    default void greet() { System.out.println("안녕"); }  // 본문 있음, 오버라이딩 선택
    static Person create() { return new Student(); }     // 정적 메서드
}
```

`default` 메서드 덕분에 기존 구현 클래스를 깨지 않고 인터페이스에 기능을 추가할 수 있게 되었습니다.

### `@Override`를 항상 붙이세요

```java
@Override
public void sayHello() { }
```

컴파일러가 "정말 오버라이딩이 맞는지" 검사해줍니다. 메서드 이름이나 매개변수를 오타냈다면 즉시 에러가 납니다. 안 붙이면 새 메서드가 조용히 만들어져서 원인을 찾기 어려운 버그가 됩니다. `toString()` 을 재정의할 때도 붙입니다.

## 4. 함께 있던 CS 개념 (원본 위치 유지)

원본 `day01`, `1` 페이지에는 이 외에도 다음이 함께 있습니다. 이 항목들은 성격상 `CS 이론` 폴더에 남겨두었습니다.

- 공격 기법 — Watering Hole, Pharming, Phishing, Ransomware, Drive by Download, Business SCAM, Cyber Kill Chain
- 디자인 패턴 — Bridge, Observer, Adapter, Composite, Decorator, Facade, Proxy, Interpreter, Mediator, Visitor
- 데이터베이스 설계 절차, ISMS
- 응집도·결합도, Fan-in/Fan-out
- 네트워크 — HDLC, PPP, ATM, FEC/BEC, 해밍코드, 서브넷팅
- OS — 프로세스 스케줄링, IPC
- 테스트 커버리지, 테스트 오라클, 스텁/드라이버
- 빅데이터 신기술 — Hadoop, HDFS, Chukwa, Sqoop, Scrapy
