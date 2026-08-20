---
출처: Claude 분석
원본: KDT_2026/2026B_BE/src/day14/exam
작성일: 2026-08-20
tags: [학습, java]
---

# Java day14 — 제네릭

> 실습 파일: `day14/exam/exam1.java`(제네릭 타입 선언·다중 타입 파라미터·중첩·제네릭 메소드·상속 제약)
> 허브: [[Java MOC]] · 이전: [[Java day13 Object 클래스와 리플렉션]]

day13에서 `Object` 가 "모든 타입을 받아 주는 그릇"이라는 걸 정리했다. 그런데 그릇이 아무거나 받아 주면 꺼낼 때가 문제가 된다. 무엇이 들어 있는지 컴파일러가 모르니 꺼낸 값은 다시 `Object` 고, 쓰려면 매번 타입 변환을 붙여야 한다.

**제네릭(Generic)은 이 문제를 반대 방향으로 푼다.** 클래스를 만들 때 타입을 정하지 않고 비워 두었다가, **쓰는 쪽이 타입을 정한다.** [[Java day09 ArrayList]] 에서 `ArrayList<String>` 의 꺾쇠 안에 타입을 적던 그 자리가 제네릭이고, [[Java day11 종합예제 인터페이스 DAO]] 에서 DAO 규격을 만들 때 쓴 것도 같은 문법이다. day14는 그 문법을 만드는 쪽에서 본다.

## 1. 배운 내용

### 1-1. 제네릭이 필요해지는 지점

값 하나를 담는 상자 클래스를 만든다고 하자. 문자열을 담으려면 이렇게 쓴다.

```java
class Box1 {
    String content;
}

Box1 box1 = new Box1();
box1.content = "안녕하세요";
```

여기까지는 문제가 없다. 그런데 같은 상자에 정수를 담고 싶어지면 `content` 의 타입이 `String` 이라 들어가지 않는다. 멤버변수 하나가 여러 타입을 동시에 가질 수는 없다.

```java
class Box2 {
    int content;
}

Box2 box2 = new Box2();
box2.content = 10;
```

결국 담을 타입 수만큼 클래스를 새로 만들게 된다. `Box1`, `Box2`, `Box3`… 구조는 완전히 같은데 **타입 한 글자만 다른 클래스가 계속 늘어난다.** [[Java day10 상속과 다형성]] 에서 중복된 멤버를 부모로 올려 정리했던 것과 비슷한 냄새인데, 여기서 중복되는 건 멤버가 아니라 **타입** 이라 상속으로는 풀리지 않는다.

### 1-2. 제네릭 타입 — 타입을 비워 두고 선언하기

해결은 타입 자리를 비워 두는 것이다. 클래스 이름 뒤에 꺾쇠를 붙이고 안에 **타입 자리 이름**을 적는다.

```java
class Box3<제네릭타입> {
    제네릭타입 content;
}
```

`제네릭타입` 은 아직 정해지지 않은 타입을 가리키는 이름표다. 이 클래스 안에서는 진짜 타입처럼 쓸 수 있고, **실제 타입은 객체를 만들 때 결정된다.**

```java
Box3<String>  box3  = new Box3<String>();
box3.content = "안녕하세요";

Box3<Integer> box33 = new Box3<>();   // 생성자 쪽 꺾쇠는 비울 수 있다
box33.content = 10;
```

정리하면 이렇다.

| 시점 | 하는 일 |
| --- | --- |
| 클래스를 정의할 때 | 타입을 정하지 않고 이름표(`T`)만 둔다 |
| 객체를 만들 때 | 꺾쇠 안에 실제 타입을 적어 이름표를 채운다 |

핵심은 **타입을 정하는 시점을 클래스 작성 시점에서 사용 시점으로 미루는 것**이다. day13의 리플렉션이 "무엇을 쓸지 결정하는 시점을 컴파일에서 실행으로 미루는" 장치였던 것과 결이 같다. 다만 제네릭은 여전히 컴파일 시점에 결정되므로, 타입이 틀리면 실행 전에 잡힌다.

**타입 파라미터 이름 규칙**

- 영문 **대문자**로 쓴다. 문법상 소문자나 한글도 통과하지만, 클래스명·변수명과 눈으로 구분되지 않아서 관례를 따르는 편이 읽기 쉽다
- 한 글자를 쓰는 관례가 굳어 있다 — `T`(Type), `E`(Element), `K`(Key), `V`(Value), `R`(Return)
- 여러 개를 둘 수 있다

### 1-3. 기본타입은 들어갈 수 없다 — 래퍼 클래스

꺾쇠 안에는 **참조타입만** 올 수 있다.

```java
Box3<Integer> box33 = new Box3<>();   // O
// Box3<int> box   = new Box3<>();    // X — 기본타입 불가
```

이유는 day13에서 정리한 자료형 두 갈래 그대로다. 제네릭은 결국 참조를 담는 자리라 값 자체를 담는 기본타입이 들어갈 수 없다. 그래서 `int` 를 담고 싶으면 짝이 되는 래퍼 클래스 `Integer` 를 쓴다.

```java
Box3<Integer> box = new Box3<>();
box.content = 10;        // 오토박싱 — int 10이 Integer로 포장돼 들어간다
int value = box.content; // 언박싱 — 꺼낼 땐 자동으로 풀린다
```

[[Java day09 ArrayList]] 에서 `ArrayList<Integer>` 라고 써야 했던 이유가 여기서 정리된다. 넣고 꺼내는 순간의 변환은 자바가 자동으로 해 주니, 쓸 때 신경 쓸 것은 **선언에 래퍼 클래스를 적는다**는 것 하나다.

| 기본타입 | 꺾쇠 안에 쓰는 것 |
| --- | --- |
| `int` | `Integer` |
| `double` | `Double` |
| `char` | `Character` |
| `boolean` | `Boolean` |

### 1-4. 타입 파라미터 여러 개, 그리고 중첩

타입 자리는 쉼표로 나눠 여러 개 둘 수 있다.

```java
class Box4<T, E> {
    T value1;
    E value2;
}

Box4<String, Integer> box4 = new Box4<>();
box4.value1 = "안녕하세요";
box4.value2 = 10;
```

두 값의 타입이 서로 달라도 되고, 같아도 된다. 키와 값을 한 쌍으로 담는 `Map<K, V>` 가 이 형태의 대표 사례다.

**꺾쇠 안에 다시 제네릭 타입을 넣는 것도 된다.**

```java
Box4<String, ArrayList<Integer>> box44 = new Box4<>();
box44.value2 = new ArrayList<Integer>();
```

`ArrayList<Integer>` 자체가 하나의 완성된 타입이라 그대로 자리에 들어간다. "정수를 담은 리스트를 값으로 갖는 상자"처럼 **타입을 조립해서 표현**할 수 있다는 뜻이고, `Map<String, List<BoardDto>>` 같은 형태가 실무에서 자주 나오는 이유다.

- 꺾쇠가 겹칠수록 읽기가 어려워지므로, 두 겹을 넘어가면 타입에 이름을 붙일 클래스를 하나 두는 편이 낫다
- 예전 자바에서는 `>>` 가 시프트 연산자로 읽혀 `> >` 처럼 띄어야 했지만 지금은 붙여 써도 된다

### 1-5. 제네릭 메소드 — 메소드에도 타입 자리를 둔다

클래스가 제네릭이 아니어도 **메소드 하나만 제네릭으로** 만들 수 있다. 반환 타입 앞에 꺾쇠로 타입 자리를 선언한다.

```java
class Util {
    public static <T> Box3<T> boxing(T 매개변수) {
        Box3<T> box = new Box3<>();
        box.content = 매개변수;
        return box;
    }
}
```

읽는 순서가 헷갈리기 쉬운 자리라 나눠서 정리한다.

| 위치 | 뜻 |
| --- | --- |
| `static` 뒤의 `<T>` | 이 메소드에서 쓸 타입 자리를 여기서 선언한다 |
| `Box3<T>` | 반환 타입 — `T` 를 담은 상자를 돌려준다 |
| `(T 매개변수)` | 매개변수 타입도 `T` |

부르는 쪽은 타입을 따로 적지 않는다. **넘긴 인자를 보고 컴파일러가 `T` 를 알아낸다**(타입 추론).

```java
Box3<String> box333 = Util.boxing("사과");
System.out.println(box333.content);   // 사과
```

`"사과"` 가 `String` 이니 `T` 는 `String` 이 되고, 반환 타입도 `Box3<String>` 으로 확정된다. 명시하고 싶으면 `Util.<String>boxing("사과")` 처럼 쓸 수도 있지만 거의 쓰지 않는다.

`static` 메소드에서 제네릭을 쓰려면 **메소드 자신이 타입 자리를 선언해야 한다.** 클래스의 타입 파라미터는 객체마다 정해지는 것이라 객체 없이 부르는 static 메소드에서는 쓸 수 없다 — [[Java day08 접근제한자와 static]] 의 "static은 객체보다 먼저 존재한다"가 여기에도 적용된다.

### 1-6. 상속 관계로 제약 걸기 — `<T extends 상위타입>`

타입 자리를 완전히 열어 두면 아무 타입이나 들어온다. 상자 안의 값으로 계산을 하려면 "숫자만 받겠다"처럼 범위를 좁혀야 한다. 꺾쇠 안에 `extends` 를 붙인다.

```java
class Box5<T extends Number> {
    T content;
}
```

이제 `T` 자리에는 **`Number` 와 그 자식 타입만** 올 수 있다.

```java
Box5<Integer> box5 = new Box5<>();   // O — Integer는 Number의 자식
// Box5<String> box  = new Box5<>(); // X — String은 Number의 자식이 아니다
```

`Number` 는 `Integer`·`Double`·`Long`·`Float` 같은 숫자 래퍼 클래스들의 공통 부모다. 그래서 `<T extends Number>` 는 곧 "숫자 계열만"이라는 뜻이 된다.

제약을 걸면 얻는 것이 하나 더 있다. **상위 타입의 메소드를 클래스 안에서 쓸 수 있다.**

```java
class Box5<T extends Number> {
    T content;
    double half() {
        return content.doubleValue() / 2;   // Number가 가진 메소드라 호출 가능
    }
}
```

제약이 없으면 `T` 에 대해 컴파일러가 아는 것은 `Object` 뿐이라 `toString()`·`equals()` 정도밖에 부를 수 없다. 상한을 두면 그 타입이 보장하는 기능까지 쓸 수 있게 된다.

- 여기서 쓰는 `extends` 는 클래스 상속의 `extends` 와 글자만 같다. **인터페이스를 상한으로 둘 때도 `implements` 가 아니라 `extends` 를 쓴다** — `<T extends Comparable<T>>` 처럼
- 상한을 여러 개 두려면 `&` 로 잇는다 — `<T extends Number & Comparable<T>>`

### 1-7. 제네릭이 없으면 어떻게 되는가 — Object와의 비교

같은 상자를 `Object` 로 만들면 담기는 것 자체는 된다.

```java
class BoxObject {
    Object content;
}

BoxObject box = new BoxObject();
box.content = "안녕하세요";
String s = (String) box.content;   // 꺼낼 때 타입 변환이 필요하다
```

차이는 두 가지다.

| | `Object` 로 담기 | 제네릭으로 담기 |
| --- | --- | --- |
| 꺼낼 때 | `(String)` 형변환이 필요하다 | 그대로 `String` 이다 |
| 잘못된 타입을 넣으면 | 넣는 순간엔 통과, 꺼내 쓸 때 `ClassCastException` | **컴파일 단계에서 막힌다** |

두 번째가 제네릭의 본체다. 오류가 **실행 중이 아니라 컴파일 시점에 잡힌다.** day12에서 본 예외 처리가 "터진 뒤에 수습하는" 장치라면, 제네릭은 "애초에 터질 수 없게 타입을 고정하는" 쪽이다 — [[Java day12 예외 처리와 JDBC]] 와 나란히 놓고 보면 성격이 갈린다.

그래서 컬렉션이 제네릭의 대표 활용처가 된다.

```java
ArrayList<String> list1 = new ArrayList<>();   // String만 담기는 리스트
String[] list2 = new String[10];               // 배열 — 처음부터 타입이 박혀 있다
```

배열은 원래 타입이 선언에 박혀 있는데 길이가 고정이고, `ArrayList` 는 길이가 자유로운 대신 아무거나 담길 위험이 있었다. 꺾쇠가 그 자리를 메워서 **배열의 타입 안전성 + 리스트의 가변 길이**가 한 그릇에 들어온 셈이다 — [[Java day04 제어문과 배열]] 과 [[Java day09 ArrayList]] 사이에서 갈렸던 장단점이 여기서 합쳐진다.

## 2. 추가로 알면 좋은 활용법

### 2-1. 다이아몬드 연산자는 왼쪽을 보고 채운다

```java
ArrayList<String> list = new ArrayList<>();
```

오른쪽 `<>` 는 비어 있지만 왼쪽 선언에 `<String>` 이 있으니 컴파일러가 채워 준다. 정리하면 **타입은 변수 선언 쪽에 적고, 생성자 쪽은 비운다**가 기본형이다. 왼쪽이 `var` 이면 채울 근거가 없으므로 오른쪽에 적어야 한다.

### 2-2. 관례적인 타입 파라미터 이름

한 글자 이름이 뜻을 담고 있어서, 맞춰 쓰면 코드를 읽는 사람이 역할을 바로 안다.

| 이름 | 쓰이는 자리 |
| --- | --- |
| `T` | 일반적인 타입 (Type) |
| `E` | 컬렉션의 원소 (Element) — `List<E>` |
| `K`, `V` | 맵의 키와 값 (Key, Value) — `Map<K, V>` |
| `R` | 반환 타입 (Return) |
| `N` | 숫자 (Number) |

### 2-3. 제네릭 인터페이스 — DAO 규격에 쓰던 그 형태

[[Java day11 종합예제 인터페이스 DAO]] 에서 DAO 규격을 만들 때 쓴 것이 제네릭 인터페이스다. 게시글이든 상품이든 CRUD의 모양은 같으니, **다루는 타입만 비워 두면 규격 하나로 여러 DAO를 덮을 수 있다.**

```java
interface IBaseDao<T> {
    boolean save(T dto);
    ArrayList<T> findAll();
}

class BoardDao implements IBaseDao<BoardDto> { ... }   // T가 BoardDto로 고정된다
```

구현 클래스에서 `IBaseDao<BoardDto>` 라고 적는 순간 `save(BoardDto dto)`·`findAll()` 의 반환이 `ArrayList<BoardDto>` 로 확정된다. 규격은 하나인데 타입만 갈아끼우는 구조라, [[Java day11 인터페이스]] 의 "규격과 구현 분리"에 타입 층이 하나 더 붙은 형태로 볼 수 있다.

### 2-4. 와일드카드 `<?>` — 읽기만 할 때

메소드가 "무슨 리스트든 받아서 크기만 세겠다"처럼 **타입을 몰라도 되는 경우**에는 물음표를 쓴다.

```java
static void printSize(ArrayList<?> list) {
    System.out.println(list.size());
}
```

`ArrayList<Object>` 로 받으면 `ArrayList<String>` 을 넘길 수 없다. 제네릭은 **상속 관계가 꺾쇠 안까지 이어지지 않기** 때문이다(`String` 은 `Object` 의 자식이지만 `List<String>` 은 `List<Object>` 의 자식이 아니다). 이 자리를 메우는 것이 와일드카드다.

- `<? extends Number>` — Number이거나 그 자식. **꺼내 읽기**에 쓴다
- `<? super Integer>` — Integer이거나 그 부모. **넣기**에 쓴다

### 2-5. 제네릭 안에서 못 하는 것들

`T` 는 실행 중에는 사라지는 이름표라(3-1) 다음이 막힌다. 처음 만나면 이유를 알기 어려운 자리라 적어 둔다.

```java
// T instanceof 검사 불가
// new T()          — 객체 생성 불가
// new T[10]        — 배열 생성 불가
// static T field;  — static 멤버에 클래스 타입 파라미터 사용 불가
```

객체를 만들어야 하면 생성 방법을 밖에서 받아 넘기는 식으로 우회한다. 1-5에서 `Util.boxing()` 이 값을 받아서 상자에 넣어 돌려준 것도 "안에서 만들지 않고 밖에서 받는" 같은 방향이다.

## 3. 더 나아가 알면 좋은 것

### 3-1. 타입 소거 — 제네릭은 컴파일 시점의 장치다

자바의 제네릭은 컴파일이 끝나면 **꺾쇠 정보가 지워진다.** `ArrayList<String>` 도 `ArrayList<Integer>` 도 실행 중에는 그냥 `ArrayList` 다. 컴파일러가 타입을 검사하고 필요한 형변환을 대신 넣어 준 뒤 이름표를 떼는 방식이라, 이것을 타입 소거(type erasure)라고 부른다.

```java
ArrayList<String>  a = new ArrayList<>();
ArrayList<Integer> b = new ArrayList<>();
System.out.println(a.getClass() == b.getClass());   // true — 실행 중엔 같은 클래스
```

day13에서 `getClass()` 로 실제 타입을 확인할 수 있다고 정리했는데, 꺾쇠 안까지는 확인되지 않는다는 뜻이다. 2-5의 제약들이 전부 여기서 나온다. 제네릭이 나중에 추가된 문법이라 예전 코드와 함께 돌아가야 했던 사정이 배경이다.

### 3-2. 공변과 불공변, 그리고 PECS

배열은 `Object[] arr = new String[3];` 이 통과한다(공변). 제네릭은 통과하지 않는다(불공변). 배열 쪽은 잘못된 타입을 넣으면 실행 중에 예외가 나지만, 제네릭은 그 상황 자체를 컴파일 단계에서 막는다.

와일드카드를 어느 쪽으로 쓸지는 **PECS**(Producer Extends, Consumer Super)로 외운다 — 데이터를 꺼내 오는(producer) 자리엔 `extends`, 넣는(consumer) 자리엔 `super`.

### 3-3. 다음에 볼 키워드

- 타입 소거와 브리지 메소드, `@SuppressWarnings("unchecked")`
- 와일드카드 상·하한과 PECS 원칙
- `Comparable<T>`·`Comparator<T>` 로 정렬 기준 만들기
- 컬렉션 프레임워크 전체 지도 — `List`·`Set`·`Map`·`Queue`
- `Map<K, V>` 와 `HashMap` 의 키·값 다루기
- 제네릭과 함수형 인터페이스 — `Function<T, R>`·`Supplier<T>`·`Consumer<T>`
- `Optional<T>` 로 null 다루기
- 제네릭 DAO·서비스 계층으로 CRUD 공통화하기
- `record` 와 제네릭의 조합

## 실습 파일

- `2026B_BE/src/day14/exam/exam1.java` (제네릭 타입 선언과 사용, 타입별 클래스 중복 문제, 래퍼 클래스 사용, 다중 타입 파라미터와 중첩, 제네릭 메소드와 타입 추론, `<T extends Number>` 상한 제약, 컬렉션과 제네릭)

## 관련 노트

[[Java MOC]] · [[Java day13 Object 클래스와 리플렉션]] · [[Java day12 예외 처리와 JDBC]] · [[Java day11 인터페이스]] · [[Java day11 종합예제 인터페이스 DAO]] · [[Java day10 상속과 다형성]] · [[Java day09 ArrayList]] · [[Java day08 접근제한자와 static]] · [[Java day04 제어문과 배열]] · [[JS day03 자료형과 연산자]] · [[KDT_2026 학습 지도]]
