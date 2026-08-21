---
출처: Claude 분석
원본: KDT_2026/2026B_BE/src/day14/exam, day14/practice
작성일: 2026-08-20
tags: [학습, java]
---

# Java day14 — 제네릭

> 실습 파일: `day14/exam/exam1.java`(제네릭 타입 선언·다중 타입 파라미터·중첩·제네릭 메소드·상속 제약), `exam2.java`(컬렉션 프레임워크·List 인터페이스와 다형성·리스트 순회·구현체 구조 차이), `exam3.java`(Set 인터페이스·HashSet·Iterator·TreeSet), `day14/practice/parctice15.java`(제네릭 클래스 설계·와일드카드 컬렉션 인벤토리 실습)
> 허브: [[Java MOC]] · 이전: [[Java day13 Object 클래스와 리플렉션]] · 다음: [[Java day15 Map과 HashMap]]

day13에서 `Object` 가 "모든 타입을 받아 주는 그릇"이라는 걸 정리했다. 그런데 그릇이 아무거나 받아 주면 꺼낼 때가 문제가 된다. 무엇이 들어 있는지 컴파일러가 모르니 꺼낸 값은 다시 `Object` 고, 쓰려면 매번 타입 변환을 붙여야 한다.

**제네릭(Generic)은 이 문제를 반대 방향으로 푼다.** 클래스를 만들 때 타입을 정하지 않고 비워 두었다가, **쓰는 쪽이 타입을 정한다.** [[Java day09 ArrayList]] 에서 `ArrayList<String>` 의 꺾쇠 안에 타입을 적던 그 자리가 제네릭이고, [[Java day11 종합예제 인터페이스 DAO]] 에서 DAO 규격을 만들 때 쓴 것도 같은 문법이다. day14는 그 문법을 만드는 쪽에서 본다.

문법을 정리한 뒤에는 제네릭이 실제로 가장 많이 쓰이는 자리인 **컬렉션 프레임워크**로 넘어간다. `List`·`Set`·`Map` 이 어떻게 갈라지는지, 인터페이스로 선언하고 구현체를 갈아끼우는 다형성이 어떻게 쓰이는지, 담긴 값을 꺼내는 방법이 몇 가지인지까지 이어서 본다. 세 갈래 중 `List` 를 먼저 훑고, 이어서 **중복을 허용하지 않는 `Set`** 까지 실습으로 확인한다.

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

### 1-8. 컬렉션 프레임워크 — 자료구조를 미리 만들어 둔 묶음

제네릭이 가장 크게 쓰이는 곳이 **컬렉션 프레임워크**다. 이름을 그대로 풀면 이렇다.

| 낱말 | 뜻 |
| --- | --- |
| 컬렉션(Collection) | 수집 — 데이터를 모아 둔 목록 |
| 프레임워크(Framework) | 틀 — 미리 짜여 있어서 가져다 쓰는 구조 |

정리하면 **데이터를 담는 자료구조를 자바가 인터페이스와 클래스로 미리 만들어 둔 묶음**이다. 목적은 하나다. 리스트·집합·사전 같은 구조를 직접 구현하지 않고 가져다 쓰는 것.

크게 세 갈래다.

| 인터페이스 | 성격 | 구현체 |
| --- | --- | --- |
| `List` | 순서가 있고 중복을 허용한다 | `ArrayList`, `LinkedList`, `Vector`, `Stack` |
| `Set` | 순서가 없고 중복을 허용하지 않는다 | `HashSet`, `TreeSet` |
| `Map` | 키와 값을 한 쌍으로 담는다 | `HashMap`, `HashTable`, `TreeMap` |

여기서 [[Java day11 인터페이스]] 에서 정리한 개념 셋이 그대로 다시 쓰인다.

- **인터페이스** — 서로 다른 클래스를 하나의 타입으로 조작하는 규격
- **구현체** — 인터페이스의 추상메소드를 실제로 구현한 클래스
- **다형성** — 하나의 객체를 서로 다른 타입으로 다루는 것

컬렉션은 이 셋이 한꺼번에 맞물린 사례라, 인터페이스를 왜 배웠는지가 여기서 눈에 보인다.

### 1-9. List 인터페이스와 다형성 — 선언은 인터페이스로

리스트를 만드는 방법은 두 가지다.

```java
ArrayList<String> list1 = new ArrayList<>();   // 구현체 타입으로 선언
List<String>      list2 = new ArrayList<>();   // 인터페이스 타입으로 선언
```

차이는 **나중에 바꿀 수 있는가**다.

```java
List<String> list2 = new ArrayList<>();
list2 = new LinkedList<>();   // O — 둘 다 List의 구현체라 같은 타입 자리에 들어간다
```

반면 구현체 타입으로 선언해 두면 형제 클래스끼리는 바꿔 끼울 수 없다. `ArrayList` 와 `LinkedList` 는 서로 부모·자식이 아니라 **같은 인터페이스를 구현한 형제**라서, 형제끼리의 타입 변환은 성립하지 않는다. [[Java day10 상속과 다형성]] 에서 정리한 "부모 타입으로 자식을 담는다"가 그대로 적용되는 자리다.

그래서 관용적으로 **왼쪽은 인터페이스, 오른쪽은 구현체**로 쓴다.

```java
List<String> list = new ArrayList<>();
```

인터페이스 타입으로 선언해도 구현체의 메소드가 그대로 불린다.

```java
list2.add("유재석");
System.out.println(list2.get(0));   // 유재석
list2.add("강호동");
```

`List` 인터페이스에는 `add`·`get` 이 추상메소드로만 적혀 있는데, 실제로 실행되는 것은 `ArrayList` 가 오버라이딩한 몸통이다. **선언 타입은 무엇을 부를 수 있는지를 정하고, 실제 객체가 어떻게 동작할지를 정한다** — [[Java 오버로딩 오버라이딩과 인터페이스(이관)]] 에서 본 오버라이딩이 다형성의 실행 축이라는 게 이 한 줄에 들어 있다.

### 1-10. 리스트 순회 세 가지

리스트에 담긴 값은 한 번에 다 꺼낼 수 없고 **하나씩 꺼낸다.** 꺼내는 방법이 세 가지다.

**① 일반 for문 — 인덱스로 접근**

```java
for (int index = 0; index < list2.size(); index++) {
    String str = list2.get(index);
}
```

인덱스를 직접 다루니 몇 번째인지 알아야 하거나 거꾸로 돌아야 할 때 쓴다. 인덱스는 0부터 시작하므로 **마지막 인덱스는 `size() - 1`** 이고, 조건은 `<` 로 둔다. `<=` 로 두면 마지막을 한 칸 넘어가 `IndexOutOfBoundsException` 이 난다 — 배열에서 길이를 넘겼을 때와 같은 자리다([[Java day04 제어문과 배열]]).

**② 향상된 for문 — 하나씩 대입**

```java
for (String str : list2) {
    // str에 항목이 하나씩 들어온다
}
```

콜론 오른쪽 목록에서 값을 하나씩 꺼내 왼쪽 변수에 넣고 반복한다. 인덱스가 필요 없을 때 가장 짧고, 범위를 넘길 일이 없다.

**③ forEach 메소드 — 반복을 메소드로**

```java
list2.forEach((str) -> {
    System.out.println(str);
});
```

`forEach` 는 문법이 아니라 **리스트가 가진 메소드**다. 괄호 안의 `(str) -> { }` 는 람다식으로, "항목 하나를 받아서 이렇게 처리해라"라는 동작 자체를 인자로 넘긴 것이다. 반복문은 도는 방법을 내가 쓰고, `forEach` 는 도는 일은 리스트에 맡기고 **처리 내용만** 넘긴다.

| 방법 | 인덱스 | 언제 쓰나 |
| --- | --- | --- |
| 일반 for | 있음 | 위치를 알아야 할 때, 역순·건너뛰기 |
| 향상된 for | 없음 | 전부 한 번씩 훑을 때 |
| forEach | 없음 | 처리 내용만 간단히 넘길 때 |

### 1-11. List 구현체의 구조 차이

세 구현체는 **쓰는 방법(메소드)이 같고 내부 구조가 다르다.** 인터페이스가 규격을 고정해 두었기 때문에, 안이 달라도 바깥에서 부르는 이름은 같다.

**ArrayList — 인덱스 기반 배열 구조**

```
[A][B][C][D]
 0  1  2  3
```

- 뒤에 `E` 를 넣으면 마지막 칸 뒤에 그냥 붙는다 — 빠르다
- 중간의 `B` 를 지우면 뒤쪽 `C`·`D` 가 한 칸씩 앞으로 당겨진다 — 항목이 많을수록 비용이 커진다
- 인덱스로 바로 찾아가므로 `get(3)` 은 즉시 끝난다

**LinkedList — 노드 기반 연결 구조**

```
[head] → [A] → [B] → [C] → [tail]
```

- 각 노드가 값과 "다음 노드의 위치"를 함께 들고 있다
- 중간에 넣거나 빼는 것은 앞뒤 연결만 고쳐 끼우면 되므로 밀리는 일이 없다
- 대신 `get(3)` 은 처음부터 세 칸을 따라가야 한다

**Vector — ArrayList와 같은 구조 + 동기화 지원**

- 구조는 `ArrayList` 와 같고, 여러 작업이 동시에 접근해도 값이 꼬이지 않도록 잠금을 건다
- 그만큼 느려서, 지금은 단일 스레드에서 `ArrayList` 를 쓰는 것이 기본이다

정리하면 이렇다.

| 구현체 | 구조 | 조회 | 중간 삽입·삭제 |
| --- | --- | --- | --- |
| `ArrayList` | 배열 | 빠름 | 느림(뒤가 밀린다) |
| `LinkedList` | 노드 연결 | 느림(따라간다) | 빠름 |
| `Vector` | 배열 + 동기화 | 빠름 | 느림 |

대부분은 `ArrayList` 로 시작하고, 앞뒤에서 넣고 빼는 일이 많아지면 `LinkedList` 를 고려하는 순서가 무난하다.

### 1-12. Set 인터페이스 — 중복을 걸러내는 컬렉션

컬렉션의 두 번째 갈래인 `Set` 은 여러 자료를 담는다는 점에서 `List` 와 같고, **중복을 허용하지 않는다**는 점에서 갈린다. 만드는 모양은 `List` 와 똑같이 인터페이스로 선언하고 구현체를 오른쪽에 둔다.

```java
Set<String> set1 = new HashSet<>();

set1.add("유재석");
set1.add("강호동");
set1.add("유재석");              // 이미 있는 값이라 들어가지 않는다
set1.add(new String("유재석"));  // 새 객체를 만들어 넣어도 마찬가지

System.out.println(set1);   // [유재석, 강호동]
```

눈여겨볼 곳은 마지막 줄이다. `new String("유재석")` 은 **주소가 다른 새 객체**인데도 중복으로 걸러진다. `Set` 이 같음을 판단하는 기준이 주소 비교(`==`)가 아니라 **값 비교(`equals()`)** 이기 때문이다. [[Java day13 Object 클래스와 리플렉션]] 에서 정리한 `equals()`·`hashCode()` 가 실제로 일을 하는 첫 자리가 여기다.

정리하면 `Set` 의 중복 판정은 두 단계로 이뤄진다.

| 순서 | 무엇을 보는가 |
| --- | --- |
| 1 | `hashCode()` 가 같은 값을 내는가 — 다르면 그 자리에서 다른 값으로 본다 |
| 2 | `hashCode()` 가 같다면 `equals()` 로 실제 내용을 비교한다 |

`String` 은 이 두 메소드가 값 기준으로 재정의돼 있어서 위 코드가 자연스럽게 걸러진다. 직접 만든 DTO를 `Set` 에 담을 때 중복이 안 걸러지는 이유도 같은 자리에서 나온다 — 재정의하지 않으면 `Object` 의 기본 동작인 주소 비교가 그대로 쓰인다.

**인덱스가 없다는 점이 메소드 구성을 바꾼다**

`Set` 은 순서를 보장하지 않으므로 "몇 번째"라는 개념 자체가 없다. `List` 에서 쓰던 메소드 중 인덱스에 기대던 것들이 그대로 빠진다.

| 하려는 일 | `List` | `Set` |
| --- | --- | --- |
| 추가 | `add(값)` / `add(인덱스, 값)` | `add(값)` 만 |
| 조회 | `get(인덱스)` | **없음** |
| 삭제 | `remove(인덱스)` | `remove(값)` — 값으로 지운다 |
| 찾기 | `indexOf(값)` / `contains(값)` | `contains(값)` 만 |
| 개수·비우기 | `size()` · `clear()` · `isEmpty()` | 동일 |

```java
set1.remove("강호동");        // 값으로 삭제
set1.contains("강호동");      // 있는지 여부만 확인
set1.clear();
set1.isEmpty();
```

`get()` 이 없다는 것은 **꺼내려면 순회해야 한다**는 뜻이고, 그래서 반복 방법도 `List` 와 달라진다.

### 1-13. Set 순회 — 향상된 for·forEach·Iterator

1-10에서 정리한 세 가지 중 **일반 for문은 쓸 수 없다.** 인덱스가 없어 `get(index)` 를 부를 수 없기 때문이다. 남는 두 가지는 그대로 쓰인다.

```java
for (String str : set1) { }        // 향상된 for문

set1.forEach((str) -> {            // forEach 메소드
    System.out.println(str);
});
```

여기에 컬렉션 공통으로 하나가 더 있다. **`Iterator`(순회자)** 다.

```java
Iterator<String> 순회자 = set1.iterator();

while (순회자.hasNext()) {
    System.out.println(순회자.next());
}
```

읽는 법을 나눠 두면 이렇다.

| 요소 | 하는 일 |
| --- | --- |
| `iterator()` | 컬렉션에서 순회자 객체를 하나 꺼낸다 |
| `hasNext()` | 다음에 꺼낼 자료가 남아 있는지 `true`/`false` |
| `next()` | 다음 자료를 하나 꺼내면서 커서를 한 칸 옮긴다 |

인덱스가 아니라 **"다음이 있는가 / 다음을 다오"** 두 물음만으로 도는 구조라, 인덱스가 없는 자료구조도 똑같은 방식으로 훑을 수 있다. `Iterator` 자체가 인터페이스이므로 `List`·`Set`·`Map` 어디서 꺼내든 쓰는 법은 같다 — [[Java day11 인터페이스]] 의 "규격만 맞으면 안이 달라도 똑같이 부른다"가 순회에도 적용된 형태다.

이 모양은 JDBC의 `ResultSet` 을 돌 때 쓰던 `while (rs.next())` 와 사실상 같은 구조다([[Java day12 예외 처리와 JDBC]]). 조회 결과를 한 줄씩 앞으로 밀면서 읽던 그 패턴이 컬렉션에도 그대로 있다고 보면 된다.

`Iterator` 를 굳이 쓰는 이유는 두 가지다. 순회 도중에 **안전하게 삭제**할 수 있다는 것(`순회자.remove()`), 그리고 순회 상태를 변수로 들고 다닐 수 있다는 것이다. 그 외의 단순 훑기에는 향상된 for문이 짧아서 더 자주 쓰인다.

### 1-14. TreeSet — 정렬된 상태로 담기는 Set

`Set` 의 또 다른 구현체가 `TreeSet` 이다. 이름 그대로 **이진 트리** 구조로 값을 담는다.

```java
TreeSet<Integer> set2 = new TreeSet<>();
set2.add(50);
set2.add(60);
set2.add(70);

System.out.println(set2);                  // [50, 60, 70]  — 기본이 오름차순
System.out.println(set2.descendingSet());  // [70, 60, 50]  — 내림차순으로 뒤집은 Set
```

`HashSet` 이 순서를 보장하지 않는 것과 달리, `TreeSet` 은 **넣는 순간 정렬된 자리를 찾아 들어간다.** 값을 넣을 때마다 트리에서 비교하며 위치를 잡기 때문에, 꺼낼 때 따로 정렬하지 않아도 정렬된 순서로 나온다.

| 구현체 | 내부 구조 | 순서 |
| --- | --- | --- |
| `HashSet` | 해시 테이블 | 보장 없음 |
| `TreeSet` | 이진 트리 | 오름차순 정렬 |

한 가지 눈여겨볼 것은 선언 타입이다. `descendingSet()` 은 **`Set` 인터페이스에는 없고 `TreeSet` 에만 있는 메소드**라, `Set<Integer> set2 = new TreeSet<>();` 로 선언해 두면 부를 수 없다. 1-9에서 "왼쪽은 인터페이스로"가 기본형이라고 정리했지만, **구현체 고유 기능을 써야 할 때는 구현체 타입으로 선언한다.** 선언 타입이 부를 수 있는 메소드의 범위를 정한다는 [[Java day10 상속과 다형성]] 의 규칙이 여기서 실제 판단으로 나타나는 자리다.

### 1-15. 제네릭 클래스를 직접 설계해 보기 — 인벤토리 슬롯 실습 (practice15)

1-2에서 본 `Box3<T>` 는 필드 하나짜리 뼈대였다. 실습 과제는 여기에 **고정 타입 필드 하나를 섞는다.** 게임 인벤토리의 슬롯을 만드는데, 슬롯 번호는 언제나 정수이고 보관하는 물건만 타입이 달라진다.

```java
class InventorySlot<T> {
    private int slotNumber;   // 타입이 고정된 필드
    private T data;           // 타입이 열려 있는 필드

    public InventorySlot(int slotNumber, T data) {
        this.slotNumber = slotNumber;
        this.data = data;
    }

    public int getSlotNumber() { return slotNumber; }
    public T   getData()       { return data; }
}
```

한 클래스 안에서 **일부 필드만 제네릭으로 두는 것**이 가능하다는 게 핵심이다. 타입 파라미터는 "이 클래스의 모든 필드를 덮는 것"이 아니라 **비워 둘 자리를 골라서 지정하는 장치**다.

읽어 둘 곳이 두 군데 더 있다.

| 자리 | 정리 |
| --- | --- |
| 생성자 `(int slotNumber, T data)` | 생성자 이름 뒤에는 꺾쇠를 적지 않는다. 클래스 선언의 `T` 를 그대로 쓴다 |
| 게터 `public T getData()` | 반환 타입이 `T` 라 꺼낼 때 형변환이 필요 없다 — 1-7에서 정리한 `Object` 와의 차이가 그대로 나타난다 |

필드를 `private` 으로 닫고 게터로 꺼내는 구조는 [[Java day08 접근제한자와 static]] 의 캡슐화 그대로다. 제네릭이 붙어도 접근제한자 규칙은 달라지지 않는다.

**슬롯을 한 목록에 담을 때 생기는 문제**

슬롯마다 담긴 타입이 다르다.

```java
InventorySlot<String>  slot1 = new InventorySlot<>(1, "집행자의 검");
InventorySlot<Integer> slot2 = new InventorySlot<>(2, 500000);
InventorySlot<Double>  slot3 = new InventorySlot<>(3, 85.5);
```

이 셋을 한 리스트에 담으려면 원소 타입을 뭐라고 적어야 할까. `List<InventorySlot<String>>` 으로 두면 나머지 둘이 못 들어가고, `List<InventorySlot<Object>>` 로 두어도 마찬가지다. 2-4에서 적어 둔 **불공변**이 실제로 걸리는 자리다 — `String` 이 `Object` 의 자식이어도 `InventorySlot<String>` 은 `InventorySlot<Object>` 의 자식이 아니다.

답이 **와일드카드**다.

```java
List<InventorySlot<?>> inventory = new ArrayList<>();

inventory.add(slot1);
inventory.add(slot2);
inventory.add(slot3);
inventory.add(slot4);
```

`InventorySlot<?>` 는 "안에 무엇이 들었는지는 묻지 않는 슬롯"이라는 타입이다. 꺾쇠 안이 서로 달라도 **바깥 클래스가 같으면 같은 자리에 들어간다.**

순회는 1-10에서 정리한 `forEach` 를 쓴다.

```java
inventory.forEach((slot) -> {
    System.out.printf("[슬롯 %d번] 보관 : %s\n", slot.getSlotNumber(), slot.getData());
});
```

여기서 와일드카드의 성격이 드러난다.

- `getSlotNumber()` 는 반환이 `int` 로 고정이라 그냥 쓸 수 있다
- `getData()` 의 반환 타입은 `?` 라 컴파일러가 아는 것이 `Object` 뿐이다. 그래도 **출력에는 문제가 없다** — `printf` 의 `%s` 는 넘어온 값의 `toString()` 을 부르기 때문이다([[Java day13 Object 클래스와 리플렉션]])

반대로 꺼낸 값으로 **계산을 하려 하면 막힌다.** 그때는 `?` 대신 `<? extends Number>` 처럼 상한을 붙여 범위를 좁혀야 한다. 정리하면 이렇다.

| 하려는 일 | 필요한 선언 |
| --- | --- |
| 담고, 그냥 출력만 | `<?>` 로 충분하다 |
| 꺼내서 숫자로 계산 | `<? extends Number>` 로 상한을 준다 |
| 목록에 값을 넣기 | `<?>` 로는 못 넣는다 — 구체 타입이나 `<? super T>` 가 필요하다 |

마지막 줄이 `?` 의 대가다. 무엇이든 받는 대신 **읽기 쪽으로만 열려 있다.** 이 실습이 "만들어 담고 출력"에서 끝나는 것도 그래서 자연스럽다.

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

메소드 매개변수뿐 아니라 **컬렉션의 원소 타입 자리에도** 쓸 수 있다. 꺾쇠 안이 제각각인 객체들을 한 목록에 모을 때가 그 자리이고, 1-15의 인벤토리 실습이 그 형태다.

### 2-5. 제네릭 안에서 못 하는 것들

`T` 는 실행 중에는 사라지는 이름표라(3-1) 다음이 막힌다. 처음 만나면 이유를 알기 어려운 자리라 적어 둔다.

```java
// T instanceof 검사 불가
// new T()          — 객체 생성 불가
// new T[10]        — 배열 생성 불가
// static T field;  — static 멤버에 클래스 타입 파라미터 사용 불가
```

객체를 만들어야 하면 생성 방법을 밖에서 받아 넘기는 식으로 우회한다. 1-5에서 `Util.boxing()` 이 값을 받아서 상자에 넣어 돌려준 것도 "안에서 만들지 않고 밖에서 받는" 같은 방향이다.

### 2-6. 리스트를 돌면서 지울 때는 반복문 밖에서

향상된 for문이나 `forEach` 로 도는 도중에 `remove()` 로 항목을 지우면 `ConcurrentModificationException` 이 난다. 도는 중에 목록의 길이가 바뀌기 때문이다. 지우는 작업은 다음 중 하나로 처리하는 편이 안전하다.

```java
list.removeIf(str -> str.startsWith("강"));   // 조건에 맞는 항목을 한 번에
```

인덱스로 돌면서 지울 때는 **뒤에서 앞으로** 도는 방법도 쓴다. 앞에서부터 지우면 뒤쪽이 당겨지면서 한 칸씩 건너뛰기 때문이다.

### 2-7. 자주 쓰는 List 메소드

`add`·`get` 말고도 [[Java day09 ArrayList]] 에서 본 것들이 인터페이스 규격에 함께 들어 있다.

| 메소드 | 하는 일 |
| --- | --- |
| `add(값)` / `add(인덱스, 값)` | 끝에 추가 / 지정 위치에 끼워 넣기 |
| `get(인덱스)` | 조회 |
| `set(인덱스, 값)` | 해당 자리 값 교체 |
| `remove(인덱스)` | 삭제 |
| `size()` | 개수 |
| `contains(값)` / `indexOf(값)` | 포함 여부 / 위치 찾기 |
| `isEmpty()` / `clear()` | 비었는지 / 전부 비우기 |

### 2-8. 중복 제거는 Set을 한 번 거치면 끝난다

`Set` 이 실무에서 가장 자주 쓰이는 자리가 **중복 제거**다. 리스트를 직접 돌면서 걸러내는 대신 `Set` 에 한 번 넣었다 빼면 된다.

```java
List<String> 원본 = new ArrayList<>(List.of("유재석", "강호동", "유재석"));

Set<String>  중복없음 = new HashSet<>(원본);        // 리스트 → 셋
List<String> 결과     = new ArrayList<>(중복없음);  // 셋 → 리스트
```

컬렉션 구현체 대부분이 **다른 컬렉션을 인자로 받는 생성자**를 갖고 있어서 이렇게 서로 갈아탈 수 있다. 순서를 유지한 채 중복만 없애고 싶으면 `LinkedHashSet` 을 쓴다 — 해시로 중복을 걸러내면서 넣은 순서도 함께 기억하는 구현체다.

| 구현체 | 중복 제거 | 순서 |
| --- | --- | --- |
| `HashSet` | O | 보장 없음 |
| `LinkedHashSet` | O | 넣은 순서 유지 |
| `TreeSet` | O | 오름차순 정렬 |

### 2-9. 직접 만든 클래스를 Set에 담을 때

`String`·`Integer` 는 `equals()`·`hashCode()` 가 값 기준으로 이미 재정의돼 있어서 중복이 자연스럽게 걸러진다. 하지만 직접 만든 DTO는 그렇지 않다.

```java
Set<BoardDto> 글모음 = new HashSet<>();
글모음.add(new BoardDto(1, "제목"));
글모음.add(new BoardDto(1, "제목"));   // 내용이 같아도 둘 다 들어간다
```

내용이 같으면 같은 것으로 보고 싶다면 **두 메소드를 함께 재정의**한다. `hashCode()` 만 재정의하면 같은 칸에 모이기만 하고 걸러지지 않고, `equals()` 만 재정의하면 애초에 같은 칸으로 가지 않아 비교가 일어나지 않는다. 항상 짝으로 맞추는 편이 안전하다.

`TreeSet` 은 기준이 하나 더 다르다. 정렬해서 담아야 하므로 **크기를 비교할 수 있어야** 하고, 그래서 담기는 타입이 `Comparable` 을 구현하고 있거나 생성자에 `Comparator` 를 넘겨야 한다. 그렇지 않으면 넣는 순간 실행 예외가 난다.

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

### 3-3. 컬렉션의 마지막 갈래 — Map

`List` 와 `Set` 을 실습으로 확인했으니 남은 하나의 자리를 잡아 둔다. 셋의 차이는 **무엇을 기준으로 값을 찾는가**로 갈린다.

| | 찾는 기준 | 중복 | 순서 |
| --- | --- | --- | --- |
| `List` | 인덱스(몇 번째) | 허용 | 넣은 순서 유지 |
| `Set` | 값 자체 | 불가 | 보장 없음(`TreeSet` 은 정렬) |
| `Map` | 키 | 키는 불가, 값은 허용 | 보장 없음(`TreeMap` 은 정렬) |

`Map<K, V>` 는 타입 파라미터가 두 개인 대표 사례라, 1-4의 다중 타입 파라미터가 실제로 쓰이는 모습이기도 하다.

```java
Map<String, BoardDto> 게시글모음 = new HashMap<>();
게시글모음.put("1", dto);
BoardDto 찾은글 = 게시글모음.get("1");
```

DAO에서 조회 결과를 담을 때 `List` 로 순서대로 쌓을지, `Map` 으로 번호를 키 삼아 담을지가 갈리는 지점이라 [[Java day12 종합예제 JDBC DAO]] 와 이어서 보면 쓰임이 잡힌다. `Map` 이 키의 중복을 걸러내는 방식은 1-12에서 본 `Set` 과 같은 원리다 — 실제로 `HashSet` 은 내부에 `HashMap` 을 두고 키만 쓰는 구조로 만들어져 있다. 그래서 day13에서 정리한 `equals()`·`hashCode()` 가 세 갈래 중 둘을 떠받치고 있는 셈이다([[Java day13 Object 클래스와 리플렉션]]).

### 3-4. 다음에 볼 키워드

- 타입 소거와 브리지 메소드, `@SuppressWarnings("unchecked")`
- 와일드카드 상·하한과 PECS 원칙
- `Comparable<T>`·`Comparator<T>` 로 정렬 기준 만들기
- 컬렉션 프레임워크 전체 지도 — `List`·`Set`·`Map`·`Queue`
- `Map<K, V>` 와 `HashMap` 의 키·값 다루기 — `put`·`get`·`keySet`·`entrySet`
- `equals()`·`hashCode()` 규약과 IDE 자동 생성
- `LinkedHashSet`·`LinkedHashMap` — 순서를 기억하는 해시 구현체
- `Iterator` 와 `Iterable` 인터페이스, 향상된 for문이 실제로 하는 일
- 제네릭과 함수형 인터페이스 — `Function<T, R>`·`Supplier<T>`·`Consumer<T>`
- `Optional<T>` 로 null 다루기
- 제네릭 DAO·서비스 계층으로 CRUD 공통화하기
- `record` 와 제네릭의 조합

## 실습 파일

- `2026B_BE/src/day14/exam/exam1.java` (제네릭 타입 선언과 사용, 타입별 클래스 중복 문제, 래퍼 클래스 사용, 다중 타입 파라미터와 중첩, 제네릭 메소드와 타입 추론, `<T extends Number>` 상한 제약, 컬렉션과 제네릭)
- `2026B_BE/src/day14/exam/exam2.java` (컬렉션 프레임워크의 정의와 세 갈래, `List` 인터페이스 타입 선언과 다형성, 인터페이스 타입으로 구현체 메소드 호출, 리스트 순회 세 가지(일반 for·향상된 for·forEach), `ArrayList`·`LinkedList`·`Vector` 의 구조 차이)
- `2026B_BE/src/day14/exam/exam3.java` (`Set` 인터페이스와 중복 제거, `HashSet` 사용법과 인덱스 없는 메소드 구성, 값 기준 삭제·검색, `Set` 순회(향상된 for·forEach·`Iterator`), `Iterator` 의 `hasNext`·`next`, `TreeSet` 의 이진 트리 구조와 `descendingSet()`)
- `2026B_BE/src/day14/practice/parctice15.java` (인벤토리 슬롯 실습 — 제네릭 클래스 직접 설계, 고정 타입 필드와 제네릭 필드 혼용, 제네릭 생성자·게터, 와일드카드 `<?>` 를 원소 타입으로 둔 리스트, `forEach` 와 `printf` 로 순회 출력)

## 관련 노트

[[Java MOC]] · [[Java day15 Map과 HashMap]] · [[Java day13 Object 클래스와 리플렉션]] · [[Java day12 예외 처리와 JDBC]] · [[Java day12 종합예제 JDBC DAO]] · [[Java day11 인터페이스]] · [[Java day11 종합예제 인터페이스 DAO]] · [[Java day10 상속과 다형성]] · [[Java day09 ArrayList]] · [[Java day08 접근제한자와 static]] · [[Java day04 제어문과 배열]] · [[Java 오버로딩 오버라이딩과 인터페이스(이관)]] · [[JS day03 자료형과 연산자]] · [[KDT_2026 학습 지도]]
