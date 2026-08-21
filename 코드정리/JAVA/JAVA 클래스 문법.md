---
출처: Claude 분석
작성일: 2026-08-21
tags: [코드정리]
---

# JAVA 클래스 문법

> 상위: [[JAVA]]
> 세부: [[JAVA enum]] · [[JAVA equals와 hashCode]] · [[JAVA record와 Lombok]]

## 클래스와 인스턴스

```java
class Student {
    int id;
    String name;
    void study() { }
}

Student s1 = new Student();
s1.name = "유재석";
Student s2 = s1;
```

- 클래스는 상태(멤버변수)와 행위(메소드)를 적은 설계도이고, `new`로 만든 실체가 인스턴스다(힙 메모리에 생긴다)
- `.`(도트)은 변수가 가리키는 주소로 이동한다는 뜻이다. 변수가 null이면 이동할 곳이 없어 `NullPointerException`이 난다
- `s2 = s1`은 객체 복사가 아니라 **주소 복사**다. s2로 바꾸면 s1에서도 바뀐 게 보인다
- 어떤 변수도 참조하지 않는 객체는 GC가 자동 회수한다
- 관례: 클래스명은 대문자 시작, 변수·메소드는 소문자 시작 카멜 표기

## 생성자와 this

```java
class Phone {
    String model;
    int price;

    Phone() { }

    Phone(String model, int price) {
        this.model = model;
        this.price = price;
    }

    Phone(String model) {
        this(model, 0);
    }
}
```

- 생성자는 클래스명과 같은 이름이고 반환 타입이 없다. 목적은 빠른 초기화와 생성 규칙(유효성 검사)이다
- `this.model`은 멤버변수, `model`은 매개변수다. 이름이 같을 때 this로 구분한다
- `this(...)`는 같은 클래스의 다른 생성자 호출이다. **생성자의 첫 줄에만** 올 수 있고, 초기화 로직을 한 곳에 모을 때 쓴다
- 함정: 정의 생성자를 하나라도 만들면 기본 생성자가 자동 생성되지 않는다. `new Phone()`을 쓰려면 `Phone() { }`을 직접 둬야 한다
- 생성자 안에서 `throw new IllegalArgumentException("...")`로 막으면 잘못된 객체가 아예 만들어지지 않는다

## 메소드와 오버로딩

```java
int add(int x, int y) { return x + y; }
void printSum(int x, int y) { System.out.println(x + y); }
boolean isEven(int n) { return n % 2 == 0; }

int add(int x, int y, int z) { return x + y + z; }
double add(double x, double y) { return x + y; }
```

- 형태는 `반환타입 이름(매개변수) { return 값; }`이고 반환이 없으면 `void`다
- `void`에서 `return;`은 그 자리에서 즉시 끝내라는 뜻이다. 유효성 검사의 조기 반환에 쓴다
- `is~` 이름으로 boolean을 반환하는 메소드는 if 조건에 바로 들어간다: `if (c.isEven(n))`
- 오버로딩은 같은 이름으로 매개변수의 **개수·타입·순서**만 다르게 여러 개 두는 것이다. 반환 타입만 다른 건 오버로딩이 아니다(컴파일 에러)
- 판단은 메소드가 하고 출력은 호출부가 한다 — 메소드가 boolean만 돌려주면 호출부에서 성공/실패 분기에 안내문을 붙일 수 있다
- ※ 가변 인자 `int sum(int... nums)`는 개수 제한 없이 받는다. printf가 이 방식이다

## 접근제한자와 캡슐화

```java
class User {
    private String name;

    public void setName(String name) {
        if (name == null || name.isBlank()) return;
        this.name = name;
    }

    public String getName() {
        return name;
    }
}
```

- 접근 범위: `public`(전체) > `protected`(같은 패키지 + 자식) > default(같은 패키지) > `private`(같은 클래스만)
- 캡슐화의 핵심은 숨기기가 아니라 **관문 두기**다. 필드를 private으로 막고 setter에서 검증하면 `user.name = 이상한값`을 원천 차단한다
- getter/setter 없이 필드가 public이면 잘못된 값 대입을 막을 방법이 없다
- DTO 관례 4가지: ①필드 전부 private ②getter/setter ③`toString()` ④기본 생성자 + 전체 매개변수 생성자
- VO는 getter만 있는 읽기 전용, DTO는 getter+setter로 계층 간 데이터를 나른다

## static과 final

```java
class Config {
    static int count = 0;
    final int fixed = 3;
    static final int MAX = 100;
}

Config.count++;
```

- `static`은 인스턴스가 아니라 클래스에 딸린 멤버다. 프로그램 전체에 1개만 있고 `클래스명.이름`으로 접근한다. 전체 발권 수 카운터처럼 인스턴스들이 공유할 값에 쓴다
- `final`은 재할당 금지다. 선언 시 초기값이 필수다
- `static final`이 상수다. 이름은 관례상 대문자(`MAX_VOLUME`)로 쓴다
- static 메소드 안에서는 non-static 멤버에 접근할 수 없다. static이 먼저 메모리에 올라갈 때 인스턴스는 아직 없기 때문이다(main이 static이라 필드를 바로 못 쓰는 이유)
- `final List<String> list`에 `list.add("a")`는 된다. final은 참조(주소)를 고정할 뿐 내용은 막지 않는다 — JS의 const와 같다

## toString 오버라이딩

```java
@Override
public String toString() {
    return "Student [id=" + id + ", name=" + name + "]";
}
```

- `println(객체)`는 내부적으로 `toString()`을 부른다. 재정의하지 않으면 `클래스명@해시코드`(주소)가 나온다
- DTO마다 만들어 두면 리스트 출력과 디버깅이 바로 읽힌다. IDE의 Generate toString으로 자동 생성하면 된다

