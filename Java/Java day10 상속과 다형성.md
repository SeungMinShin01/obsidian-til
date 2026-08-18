---
출처: Claude 분석
원본: KDT_2026/2026B_BE/src/day10
작성일: 2026-08-11
tags: [학습, java]
---

# Java day10 — 상속과 다형성

> 실습 파일: `day10/exam/exam1.java`(상속·캐스팅), `exam2.java`(Object·instanceof), `exam3.java`(오버라이딩), `실습.java`(타이어 교체), `day10/pracitce/practice12.java`(연습문제 10개)
> 허브: [[Java MOC]] · 이전: [[Java day09 ArrayList]] · 다음: [[Java day11 인터페이스]]

## 1. 배운 내용

### 1-1. 상속

```java
class 동물 {                    // 부모(상위) 클래스
    String name;
    동물() { System.out.println("동물 탄생"); }
    void show() { System.out.println("동물 뜁니다."); }
}

class 조류 extends 동물 { }      // 하위클래스명 extends 상위클래스명
class 참새 extends 조류 { }
class 닭   extends 조류 { }
```

```
      동물
       │
      조류
    ┌──┴──┐
   참새    닭
```

**하위 클래스의 객체는 상위 클래스의 멤버(변수·메소드)를 그대로 쓴다.**

```java
조류 bird1 = new 조류();
bird1.name = "비둘기";   // 동물의 멤버변수
bird1.show();            // 동물의 메소드
```

`조류`에는 `name`도 `show()`도 없지만 동작한다. 물려받았기 때문이다.

### 1-2. 생성자는 위에서부터 실행된다

```java
동물 animal1 = new 동물();      // 동물생성자
조류 bird1 = new 조류();        // 조류생성자 + 동물생성자
참새 sparrow1 = new 참새();     // 참새생성자 + 조류생성자 + 동물생성자
닭 chicken1 = new 닭();         // 닭생성자 + 조류생성자 + 동물생성자
```

**상위 클래스의 객체가 먼저 생성되고 하위 클래스 객체가 생성된다.**

`참새` 하나를 만들면 실제로는 메모리에 `동물` → `조류` → `참새` 세 겹이 쌓인다. 이게 다음 항목의 다형성이 성립하는 물리적 근거다.

### 1-3. 다형성 — 하나의 자료, 여러 타입

> 하나의 자료가 다양한 형(형식·모양·형태·구분)을 갖는 성질

```java
참새 sparrow1 = new 참새();

조류 bird2   = sparrow1;   // 참새 → 조류
동물 animal2 = sparrow1;   // 참새 → 동물
```

`sparrow1`은 계속 같은 객체인데 타입만 바뀐다.

| 단계 | 자료 | 타입 |
| --- | --- | --- |
| 원래 | 참새 | 참새 |
| 업캐스팅 | 참새 | 조류 |
| 업캐스팅 | 참새 | 동물 |
| 다운캐스팅 | 참새 | 참새 |

**가능한 이유가 두 가지다.**
1. 논리적 — 상속 관계로 이어져 있다
2. 물리적 — 참새 인스턴스가 생성될 때 조류·동물 인스턴스도 함께 생성됐다

### 1-4. 업캐스팅과 다운캐스팅

```java
조류 bird2 = sparrow1;              // 자동 타입 변환 / 업캐스팅 (올라가기)
참새 sparrow2 = (참새) animal2;      // 강제 타입 변환 / 다운캐스팅 (내려가기)
```

기본 타입의 형변환과 구조가 같다. → [[Java day02 타입 변환]]

```java
int a = 3;              // 자료 3, 타입 int
byte b = (byte) a;      // 자료 3, 타입 byte
```

**다운캐스팅에서 주의할 점 두 가지**
1. 변환할 타입명을 `( )` 안에 명시한다
2. 변환할 자료가 그 타입을 실제로 포함하는지 확인한다

```java
동물 animal1 = new 동물();
참새 sparrow3 = (참새) animal1;   // 위험
```

`animal1`은 `동물`로 태어났다. 태어날 때 참새는 만들어지지 않았으므로 참새로 내려갈 수 없다.

> **자식이 태어날 때 부모도 태어나지만, 부모가 태어날 때 자식은 태어나지 않는다.**

컴파일은 통과하고 실행할 때 `ClassCastException`이 난다. 그래서 다음 항목의 `instanceof`가 필요하다.

### 1-5. Object — 모든 클래스의 조상

자바는 100% 객체지향 언어라서 **모든 클래스가 `Object`를 상속**한다.

```java
class A { }
class B extends A { }
class C extends A { }
class D extends B { }
class E extends C { }
```

```
        Object
          │
          A
       ┌──┴──┐
       B     C
       │     │
       D     E
```

객체를 하나 만들 때 실제로 생기는 인스턴스 개수는 이렇다.

| 생성 | 개수 | 경로 |
| --- | --- | --- |
| `new A()` | 2 | A → Object |
| `new B()` | 3 | B → A → Object |
| `new C()` | 3 | C → A → Object |
| `new D()` | 4 | D → B → A → Object |
| `new E()` | 4 | E → C → A → Object |

`toString()`을 오버라이딩할 수 있었던 것도 `Object`에서 물려받았기 때문이다. → [[Java day05 클래스와 인스턴스]]

### 1-6. instanceof — 변환 전에 확인하기

```java
System.out.println(e instanceof Object);   // true
System.out.println(e instanceof C);        // true
System.out.println(e instanceof D);        // false — E는 D를 포함하지 않는다
System.out.println(e instanceof B);        // false
```

형태: `인스턴스 instanceof 타입명`

**타입 변환 전에 `instanceof`로 확인한 뒤 변환하는 것이 안전하다.**

```java
if (animal2 instanceof 참새) {
    참새 s = (참새) animal2;
}
```

형제 관계는 서로 변환되지 않는다. `B`와 `C`는 둘 다 `A`를 상속하지만 서로를 포함하지 않는다.

```java
B b = new B();
// C c2 = (C) b;   // B는 C를 포함하지 않으므로 불가능
```

### 1-7. 오버라이딩 — 물려받은 메소드 재정의

```java
class 상위클래스 {
    int value1 = 10;
    int value2 = 20;
    상위클래스() { System.out.println("상위 탄생"); }
    void show() { System.out.println("상위 메소드 실행"); }
}

class 하위클래스 extends 상위클래스 {
    int value3 = 30;
    int value4 = 40;
    하위클래스() { System.out.println("하위 탄생"); }

    void show(int a) { }        // 오버로딩 — 매개변수가 다르다

    @Override
    void show() {               // 오버라이딩 — 선언부가 완전히 같다
        System.out.println("하위 메소드가 재정의 실행");
    }
}
```

| | 오버로딩 | 오버라이딩 |
| --- | --- | --- |
| 뜻 | 같은 이름으로 여러 개 선언 | 물려받은 메소드를 다시 정의 |
| 조건 | 매개변수의 **개수·타입·순서**가 다름 | 선언부가 **모두 동일** |
| 대상 | 생성자, 메소드 | 메소드 |

`@Override`는 메소드 위에 붙인다. VS Code에서는 빈 줄에 `Ctrl + Space` 또는 소스 작업으로 자동 생성된다.

**멤버변수와 메소드의 차이**
- 멤버변수 — 인스턴스 1개당 1개씩 생성
- 메소드 — 여러 인스턴스가 하나를 공유

### 1-8. 타입이 아니라 실제 객체를 따라간다

`exam3.java`의 핵심이다.

```java
하위클래스 obj2 = new 하위클래스();
obj2.show();                        // "하위 메소드가 재정의 실행"

상위클래스 obj3 = obj2;              // 타입만 상위로 바꿈
obj3.show();                        // "하위 메소드가 재정의 실행"  ← 여전히 하위!

상위클래스 obj4 = new 최하위클래스();
obj4.show();                        // "최하위 메소드가 재정의 실행"
```

**변수의 타입이 무엇이든 실제로 만들어진 객체의 메소드가 실행된다.**

반면 멤버변수는 타입을 따라간다.

```java
System.out.println(obj2.value3);   // 30 — 하위 타입이라 접근 가능
// System.out.println(obj1.value3);   상위 타입에는 value3가 없다
```

| | 무엇을 따라가나 | 결정 시점 |
| --- | --- | --- |
| 메소드 (오버라이딩) | **실제 객체** | 런타임 |
| 멤버변수 | **변수의 타입** | 컴파일 타임 |

이 차이가 [[Java 오버로딩 오버라이딩과 인터페이스(이관)]] 의 출력 문제와 정확히 같은 이야기다.

### 1-9. 실습 — 타이어 교체

다형성이 왜 쓸모 있는지 보여주는 예제다.

```java
class Car {
    Tire tire;
    void run() { this.tire.roll(); }
}

class Tire {
    void roll() { System.out.println("[일반] 타이어가 회전"); }
}
class HankookTire extends Tire {
    void roll() { System.out.println("[한국] 타이어가 회전(업그레이드)"); }
}
class KumhoTire extends Tire {
    void roll() { System.out.println("[금호] 타이어가 회전(업그레이드)"); }
}
```

```java
Car myCar = new Car();

myCar.tire = new Tire();          myCar.run();   // [일반] 타이어가 회전
myCar.tire = new HankookTire();   myCar.run();   // [한국] 타이어가 회전(업그레이드)
myCar.tire = new KumhoTire();     myCar.run();   // [금호] 타이어가 회전(업그레이드)
```

**`Car`는 한 글자도 바뀌지 않는다.** `Tire` 타입 하나만 알고 있으면 어떤 타이어를 끼워도 그 타이어의 `roll()`이 실행된다.

```java
System.out.println(myCar.tire instanceof Tire);          // true
System.out.println(myCar.tire instanceof KumhoTire);      // true
System.out.println(myCar.tire instanceof HankookTire);    // false — 지금 낀 건 금호
```

`instanceof`는 **지금 실제로 들어있는 객체**를 기준으로 판단한다.

### 1-10. 상태는 각자, 행위는 공유 — exam4 재실습

타이어 예제를 차 두 대로 다시 돌려보면 인스턴스의 성질이 드러난다.

```java
Car myCar = new Car();      // @372f7a8d  ← 참조값이 서로 다르다
Car yourCar = new Car();    // @2f92e0f4

myCar.tire = new Tire();
myCar.run();                // [일반]
// yourCar.run();           // 오류! yourCar의 tire는 아직 null

myCar.tire = new HankookTire();
myCar.run();                // [한국] — myCar만 바뀌었다
yourCar.tire = new Tire();
yourCar.run();              // [일반] — yourCar는 영향 없다
```

- **멤버변수(`tire`)는 인스턴스마다 각각 생성된다** — 상태. 회원마다 '아이디'가 따로 있어야 하는 것과 같다
- **메소드(`run()`)는 여러 인스턴스가 하나를 공유한다** — 행위. '로그인' 기능을 회원마다 따로 만들 필요가 없는 것과 같다
- 대입 전의 멤버변수는 초기값이 없어서(null) 바로 쓰면 `this.tire is null` 오류가 난다 — **참조타입 멤버는 채우고 나서 쓴다**
- 변수란 결국 **하나의 자료(값/인스턴스)를 저장/참조하는 것** — `myCar.tire`에 새 타이어를 대입하면 이전 참조가 교체된다

## 2. 추가로 알면 좋은 활용법

### 2-1. super — 부모를 가리키는 키워드

`this`가 자기 인스턴스라면 `super`는 부모 쪽이다.

```java
class 하위클래스 extends 상위클래스 {
    하위클래스() {
        super();                    // 부모 생성자 호출 (생략하면 자동으로 들어감)
        System.out.println("하위 탄생");
    }

    @Override
    void show() {
        super.show();               // 부모 메소드를 먼저 실행하고
        System.out.println("하위 메소드가 재정의 실행");
    }
}
```

**`super()`는 생성자의 첫 줄에만 올 수 있다.** 안 써도 컴파일러가 자동으로 넣기 때문에 "상위가 먼저 탄생"하는 것이다.

부모에 기본 생성자가 없고 매개변수 생성자만 있으면 `super(값)`을 직접 써야 한다.

```java
class 동물 {
    String name;
    동물(String name) { this.name = name; }
}
class 조류 extends 동물 {
    조류(String name) { super(name); }   // 생략 불가
}
```

### 2-2. 오버라이딩의 세 가지 제약

```java
class 상위 {
    protected int show() { return 1; }
}
class 하위 extends 상위 {
    @Override
    public int show() { return 2; }     // OK
}
```

1. **선언부가 같아야 한다** — 이름·매개변수·반환타입
2. **접근 범위를 좁힐 수 없다** — `protected` → `public`은 되지만 `protected` → `private`은 안 된다
3. **`final` 메소드는 재정의할 수 없다**

접근 범위 규칙은 [[Java day08 접근제한자와 static]] 과 이어진다. 인터페이스 구현 시 `public`을 붙여야 하는 이유도 같다.

### 2-3. `@Override`를 꼭 붙이기

```java
class 하위클래스 extends 상위클래스 {
    void shwo() { }        // 오타 — 재정의가 아니라 새 메소드가 만들어진다
}
```

`@Override`를 붙이면 컴파일러가 "정말 부모에 이 메소드가 있는가"를 검사한다. 없으면 즉시 에러가 나서 조용히 새 메소드가 생기는 상황을 막는다.

### 2-4. 필드는 오버라이딩되지 않는다

```java
class 상위 { int value = 10; }
class 하위 extends 상위 { int value = 20; }

하위 h = new 하위();
상위 s = h;

System.out.println(h.value);   // 20
System.out.println(s.value);   // 10  ← 9

같은 이름의 필드를 하위에서 다시 선언하면 **가려질(shadowing) 뿐 덮어쓰이지 않는다.** 둘 다 메모리에 존재하고 변수의 타입에 따라 다른 쪽이 보인다.

혼란스러우니 **부모와 같은 이름의 필드는 만들지 않는 편이 안전하다.**

### 2-5. 패턴 매칭 instanceof (Java 16+)

```java
if (animal2 instanceof 참새) {
    참새 s = (참새) animal2;
    s.show();
}

// 위를 한 줄로
if (animal2 instanceof 참새 s) {
    s.show();
}
```

확인과 변환을 동시에 한다. 캐스팅을 따로 쓰지 않아 실수가 줄어든다.

### 2-6. 상속보다 조합을 먼저 검토하기

`실습.java`의 `Car`와 `Tire` 관계가 좋은 예다.

```java
class Car { Tire tire; }        // 조합 — Car "has a" Tire
class HankookTire extends Tire  // 상속 — HankookTire "is a" Tire
```

| 관계 | 판단 기준 | 예 |
| --- | --- | --- |
| 상속 (is-a) | "A는 B다"가 성립하는가 | 참새는 조류다 |
| 조합 (has-a) | "A가 B를 가진다"가 맞는가 | 자동차가 타이어를 가진다 |

자동차는 타이어가 **아니라** 타이어를 **가진다.** 그래서 `Car extends Tire`가 아니라 필드로 들고 있다.

상속은 부모가 바뀌면 모든 자식이 영향을 받아서 결합이 강하다. **"A는 B다"가 확실할 때만 상속을 쓴다.**

## 3. 더 나아가 알면 좋은 것

### 3-1. 추상 클래스

`동물`을 직접 만들 일이 없다면 `abstract`로 막을 수 있다.

```java
abstract class 동물 {
    String name;
    abstract void 울음();          // 본문 없음 — 자식이 반드시 구현
    void show() { System.out.println("동물 뜁니다."); }
}

class 참새 extends 동물 {
    @Override
    void 울음() { System.out.println("짹짹"); }
}
```

```java
// 동물 a = new 동물();   불가능 — 추상 클래스는 인스턴스를 만들 수 없다
동물 a = new 참새();       // 가능
```

**공통 코드를 물려주면서 일부는 반드시 구현하게 강제**할 때 쓴다.

### 3-2. 인터페이스와의 차이

| | 추상 클래스 | 인터페이스 |
| --- | --- | --- |
| 필드 | 일반 필드 가능 | `public static final` 상수만 |
| 생성자 | 있음 | 없음 |
| 다중 | `extends` 1개만 | `implements` 여러 개 |
| 의미 | "~는 ~이다" (is-a) | "~는 ~을 할 수 있다" (can-do) |

`Tire`를 인터페이스로 바꾸면 이렇게 된다.

```java
interface Tire { void roll(); }
class HankookTire implements Tire {
    public void roll() { System.out.println("[한국] 타이어가 회전"); }
}
```

→ [[Java 오버로딩 오버라이딩과 인터페이스(이관)]]

### 3-3. 다형성이 실제로 쓰이는 자리

`실습.java`의 타이어 교체 구조가 그대로 확장된다.

```java
interface BoardRepository { void save(BoardDto dto); }

class MemoryBoardDAO implements BoardRepository { ... }
class MySqlBoardDAO  implements BoardRepository { ... }
```

```java
BoardRepository repo = new MemoryBoardDAO();   // 이 한 줄만 바꾸면
```

`Car`가 `Tire`만 알듯이, Controller는 `BoardRepository`만 안다. 메모리 저장을 DB 저장으로 갈아끼워도 Controller는 그대로다. → [[Java day09 MVC 종합예제]]

### 3-4. 컬렉션에 부모 타입으로 담기

```java
ArrayList<동물> 동물원 = new ArrayList<>();
동물원.add(new 참새());
동물원.add(new 닭());

for (동물 a : 동물원) {
    a.show();       // 각자의 재정의된 show()가 실행된다
}
```

서로 다른 자식들을 **한 리스트에 담아 같은 방식으로 다룰 수 있다.** 다형성의 가장 흔한 실전 활용이다. → [[Java day09 ArrayList]]

### 3-5. 다음에 볼 키워드

- `abstract` / `interface` — 설계를 강제하는 두 방법
- `sealed` (Java 17+) — 상속할 수 있는 클래스를 제한
- `Object`의 `equals` / `hashCode` / `toString` — 모든 클래스가 물려받는 것들
- 리스코프 치환 원칙 — 부모 자리에 자식을 넣어도 문제없어야 한다는 설계 원칙

### 3-6. 연습문제 — practice12

`pracitce/practice12.java`에 오늘 개념을 문제 10개로 복습한 코드가 있습니다(앞서 6문제까지 풀던 파일이 10문제로 늘었습니다).

- `super(name)` — 부모에 기본 생성자가 없으면 자식 생성자가 **첫 줄에서** 부모 생성자를 명시 호출해야 합니다 (`Person(String)` ← `Student`)
- `Cat.makeSound()` 오버라이딩, `Figure f1 = new Triangle()` 업캐스팅, `Shape.draw()`가 자식 것으로 실행되는 이유 — 각 문제의 주석에 "결과 → 원인" 순으로 풀이를 달아둔 형식 자체가 복습 방법으로 좋습니다

늘어난 뒷부분 네 문제는 다형성을 "쓰는 쪽" 관점으로 옮겨 갑니다.

**7번 — 부모 타입 배열에 자식들을 섞어 담기**

```java
Beverage[] beverages = new Beverage[2];
beverages[0] = new Coke();
beverages[1] = new Coffee();
for (Beverage b1 : beverages) b1.drink();   // 콜라를 마십니다 / 커피를 마십니다
```

배열의 타입은 하나(`Beverage`)인데 실제로 담긴 객체는 서로 다르고, 반복문은 그걸 신경 쓰지 않습니다. 3-4에서 본 "한 리스트에 담아 같은 방식으로" 가 배열 버전으로 나온 형태입니다.

**8번 — 매개변수 타입을 부모로 받기**

```java
class Character {
    public void use(Weapon weapon) { weapon.attack(); }
}
character.use(sword);   // 검으로 공격합니다
character.use(gun);     // 총으로 공격합니다
```

`use`는 `Sword`도 `Gun`도 모르고 `Weapon`만 압니다. 무기를 하나 더 만들어도 `Character`는 그대로 둘 수 있습니다. 이 구조가 [[Java day11 인터페이스]] 에서 부모 자리를 인터페이스로 바꿔 그대로 다시 나옵니다.

**9번 — 필드와 메소드의 결정 시점이 다르다**

```java
SuperClass obj = new SubClass();
System.out.println(obj.name);   // 상위
obj.method();                   // 하위 메소드 출력
```

같은 변수인데 필드는 부모 것이, 메소드는 자식 것이 나옵니다. **필드는 선언한 타입(컴파일 시점)으로, 메소드는 실제 객체(실행 시점)로** 결정되기 때문입니다. 오버라이딩은 메소드에만 적용된다고 기억해 두는 편이 안전하고, 그래서 필드는 `private` + getter로 다루는 습관이 필요합니다. → [[Java day08 접근제한자와 static]]

**10번 — instanceof는 조상 전체에 true**

```java
Laptop laptop = new Laptop();          // Laptop → Electronic → Device
laptop instanceof Laptop      // true
laptop instanceof Electronic  // true
laptop instanceof Device      // true
```

상속이 여러 단계여도 위로 올라가는 조상은 전부 `true`입니다. `instanceof`가 "정확히 이 타입인가"가 아니라 "이 타입으로 취급해도 되는가"를 묻는 연산자라서 그렇습니다.

## 실습 파일

- `2026B_BE/src/day10/exam/exam1.java` (상속, 업·다운캐스팅)
- `2026B_BE/src/day10/exam/exam2.java` (Object, instanceof)
- `2026B_BE/src/day10/exam/exam3.java` (오버로딩 vs 오버라이딩)
- `2026B_BE/src/day10/exam/실습.java` (타이어 교체)
- `2026B_BE/src/day10/exam/exam4.java` (차 두 대 — 상태는 각자, 행위는 공유)
- `2026B_BE/src/day10/pracitce/practice12.java` (연습문제 10개 — 상속·오버라이딩·업캐스팅·instanceof)

## 관련 노트

[[Java MOC]] · [[Java day09 ArrayList]] · [[Java day09 MVC 종합예제]] · [[Java day05 클래스와 인스턴스]] · [[Java day08 접근제한자와 static]] · [[Java day02 타입 변환]] · [[Java 오버로딩 오버라이딩과 인터페이스(이관)]]
