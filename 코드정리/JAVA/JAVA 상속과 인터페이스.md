---
출처: Claude 분석
작성일: 2026-08-21
tags: [코드정리]
---

# JAVA 상속과 인터페이스

> 상위: [[JAVA]]

## 상속과 super

```java
class 동물 {
    String name;
    void show() { System.out.println("동물"); }
}

class 참새 extends 동물 {
    참새() {
        super();
        System.out.println("참새 탄생");
    }

    @Override
    void show() {
        super.show();
        System.out.println("참새");
    }
}
```

- `extends`가 상속이다. 자식은 부모의 멤버(변수·메소드)를 그대로 쓴다. 클래스 상속은 **하나만** 된다
- 자식을 만들면 부모부터 생성된다(동물 → 참새 순). `super()`는 부모 생성자 호출이고 생략하면 자동으로 들어간다
- 부모에 기본 생성자가 없고 매개변수 생성자만 있으면 자식 생성자 첫 줄에서 `super(값)`을 직접 불러야 한다
- `super.show()`는 부모의 메소드를 실행한다. 재정의하면서 부모 동작을 유지하고 덧붙일 때 쓴다
- 상속(is-a)인지 조합(has-a)인지 먼저 판단한다. "자동차는 타이어다"가 아니라 "가진다"이므로 `class Car { Tire tire; }`처럼 필드로 둔다

## 다형성과 캐스팅

```java
참새 s = new 참새();
동물 a = s;
참새 s2 = (참새) a;
```

- 업캐스팅(자식→부모 타입)은 자동이다. 부모 타입 변수에 자식 객체를 담을 수 있다
- 다운캐스팅(부모→자식 타입)은 `(타입)`을 명시해야 하고, 실제로 그 타입으로 태어난 객체일 때만 된다. 아니면 실행 중 `ClassCastException`이 난다
- 부모 타입 변수라도 **실행되는 메소드는 실제 객체의 재정의본**이다(런타임 결정). 반대로 멤버변수는 변수의 타입을 따라간다(컴파일 결정) — 그래서 필드는 private + getter로 다룬다
- 활용 두 가지: 부모 타입 배열·리스트에 자식들을 섞어 담아 같은 방식으로 돌리기, 매개변수를 부모 타입으로 받아 어떤 자식이 와도 처리하기

## instanceof

```java
if (a instanceof 참새) {
    참새 x = (참새) a;
    x.show();
}
```

- "이 객체를 이 타입으로 취급해도 되는가"를 묻는다. 조상 방향은 전부 true다(`laptop instanceof Device`)
- 다운캐스팅 전에 instanceof로 확인하는 게 안전 수칙이다. 형제 타입끼리는 변환되지 않는다
- 오른쪽에 인터페이스도 올 수 있다: `if (obj instanceof Flyable)` — 능력으로 물어보는 방식
- ※ 패턴 매칭(Java 16+)으로 확인과 캐스팅을 한 줄에: `if (a instanceof 참새 x) { x.show(); }`

## 오버라이딩 vs 오버로딩

```java
@Override
void show() { System.out.println("재정의"); }

void show(int a) { }
```

- 오버라이딩: 물려받은 메소드를 선언부 그대로 다시 정의. 오버로딩: 같은 이름에 매개변수만 다르게 추가
- `@Override`를 붙이면 컴파일러가 부모에 정말 그 메소드가 있는지 검사한다. 오타로 새 메소드가 조용히 생기는 사고를 막아준다
- 오버라이딩 제약: 접근 범위를 좁힐 수 없고(`public` → `private` 불가), `final` 메소드는 재정의할 수 없다

## interface — 규격

```java
public interface Tire {
    int SIZE = 17;
    void roll();
}

class HankookTire implements Tire {
    @Override
    public void roll() { System.out.println("한국타이어 회전"); }
}

Tire t = new HankookTire();
t.roll();
```

- 인터페이스는 "무엇을 할 수 있어야 한다"는 규격만 정한다. 필드는 전부 자동으로 `public static final` 상수, 메소드는 기본이 추상(선언부만)이다
- 생성자가 없어 `new Tire()`는 불가하고, 구현 클래스(`implements`)가 추상메소드를 **전부** 오버라이딩해야 한다(상속과 달리 필수)
- 인터페이스 타입 변수에 구현체를 담는 게 다형성의 실전형이다. 구현체를 갈아끼워도 쓰는 쪽 코드는 그대로다
- `implements`는 여러 개 가능하다(다중 구현): `class Duck implements Flyable, Swimmable`
- 멤버 4종: 추상(구현 필수) / `default`(구현부 있음, 재정의 선택 — 기존 구현체 안 깨고 기능 추가용) / `static`(인터페이스명으로 직접 호출) / `private`(내부 공통 코드)
- 추상클래스와의 선택: 공통 상태+부분 구현을 물려주려면 추상클래스, 순수 행위 규격이면 인터페이스. is-a vs can-do

## 익명 구현체와 람다 ※

```java
Tire t = new Tire() {
    @Override
    public void roll() { System.out.println("일반 회전"); }
};

interface Calc { int calc(int x, int y); }
Calc add = (x, y) -> x + y;
```

- 익명 구현체는 한 번만 쓸 구현을 클래스 선언 없이 그 자리에서 만든다: `new 인터페이스() { 오버라이딩 }`
- 추상메소드가 **딱 1개**인 인터페이스(함수형 인터페이스)는 람다 `(매개변수) -> 결과`로 줄여 쓸 수 있다
- 컬렉션의 `removeIf(x -> 조건)`, `sort(Comparator.comparing(...))`에 넘기는 게 전부 이 람다다

## 관련 노트

[[JAVA]]
