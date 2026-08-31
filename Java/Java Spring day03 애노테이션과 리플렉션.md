---
출처: Claude 분석
원본: KDT_2026/2026B_Spring/springweb/src/main/java/day03/exam
작성일: 2026-08-31
tags: [학습, java]
---

# Java Spring day03 — 애노테이션과 리플렉션

> 실습 파일: `2026B_Spring/springweb/src/main/java/day03/exam/exam1.java`
> 허브: [[Java MOC]] · 이전: [[Java Spring day02 스프링 부트 실행과 계층 이식]]

[[Java Spring day02 스프링 부트 실행과 계층 이식]] 까지는 `@SpringBootApplication`·`@RestController`·`@GetMapping` 같은 애노테이션을 **가져다 쓰는** 쪽이었다. 붙이면 동작한다는 것까지는 확인했지만, 그 표시 하나가 어떻게 실제 동작으로 이어지는지는 열어 보지 않았다.

day03은 그 안쪽을 본다. 애노테이션을 직접 만들고, 만든 애노테이션을 클래스에 달고, **리플렉션으로 그 표시를 읽어 메소드를 실행**하는 데까지 한 파일에서 이어진다. 스프링이 하는 일을 아주 작게 줄여 놓은 축소판인 셈이다.

| 자리 | 하는 일 |
| --- | --- |
| `@Override`·`@Deprecated` | 자바가 미리 만들어 둔 표준 애노테이션 (1-2~1-3) |
| `@interface MyAnnotation` | 애노테이션을 직접 정의하기 (1-4~1-7) |
| `class TestClass` | 만든 애노테이션을 메소드에 달아 두기 (1-8) |
| `main` 의 리플렉션 부분 | 그 표시를 읽어 내고, 객체를 만들고, 메소드를 실행하기 (1-9~1-11) |

[[Java day13 Object 클래스와 리플렉션]] 에서 `Class` 와 `Class.forName()` 을 본 적이 있다. 그때는 "실행 중에 클래스를 문자열로 찾아 로드한다"까지였다면, 여기서는 찾아낸 클래스에서 **메소드를 꺼내고 붙어 있는 표시를 읽어 내는** 데까지 나간다.

## 1. 배운 내용

### 1-1. 애노테이션은 코드에 붙이는 표시다

애노테이션(annotation)은 `@` 로 시작하는 표시로, 클래스·메소드·필드 같은 코드 요소에 **부가 정보를 달아 두는** 장치다. 주석과 헷갈리기 쉬운데 결정적으로 다른 점이 있다.

| 구분 | 주석(`//`, `/* */`) | 애노테이션(`@`) |
| --- | --- | --- |
| 읽는 대상 | 사람 | 컴파일러·프레임워크(프로그램) |
| 컴파일 후 | 사라진다 | 클래스 파일에 남을 수 있다 |
| 실행 중 확인 | 불가능 | 설정에 따라 가능 |

핵심은 애노테이션이 **기계가 읽을 수 있는 메모**라는 점이다. 사람이 읽는 설명은 주석에 적고, 프로그램이 읽고 판단해야 할 정보는 애노테이션에 적는다.

그리고 애노테이션 자체는 **아무 일도 하지 않는다.** 붙여 두기만 해서는 표시로만 남고, 그것을 읽어서 무언가를 하는 코드가 따로 있어야 동작이 된다. 이 파일에서는 그 "읽는 쪽"을 직접 만들어 본다.

### 1-2. 표준 애노테이션 — 자바가 미리 만들어 둔 것들

먼저 상속 관계를 하나 만들어 두고, 자바가 기본으로 제공하는 애노테이션 둘을 붙인다.

```java
class SuperClass {
    void method1() {
    }
}

class Subclass extends SuperClass {
    @Override
    void method1() {
        super.method1();
    }

    @Deprecated
    void method2() {
    }
}
```

`main` 에서 호출하면 이렇게 된다.

```java
Subclass subclass = new Subclass();
subclass.method1();   // 부모 메소드가 아니라 재정의한 메소드가 실행된다
subclass.method2();   // 실행은 되지만 권장하지 않는다는 표시가 붙어 있다
```

### 1-3. @Override와 @Deprecated — 표시가 컴파일러에게 말을 건다

**`@Override`** 는 "이 메소드는 상위 타입의 메소드를 재정의한 것"이라는 표시다. 붙이지 않아도 재정의는 되지만, 붙이면 컴파일러가 **실제로 재정의가 맞는지 검사**해 준다. 메소드 이름이나 매개변수가 어긋나 재정의가 아니라 새 메소드가 되어 버리는 상황을 컴파일 시점에 잡을 수 있어서, 재정의할 때는 붙여 두는 편이 안전하다.

실행 결과는 [[Java day10 상속과 다형성]] 에서 본 그대로다. 참조 타입이 무엇이든 **실제 객체의 재정의된 메소드가 불린다.** 그 안의 `super.method1()` 은 가려진 부모 쪽 메소드를 명시적으로 부르는 통로다.

**`@Deprecated`** 는 "더 이상 사용을 권장하지 않는다"는 표시다. 호출해도 실행은 되지만 컴파일러가 경고를 낸다. 라이브러리나 프레임워크를 만드는 쪽에서 **당장 지우면 쓰던 코드가 깨지니, 지우기 전에 미리 알리는** 용도로 쓴다. 스프링을 만드는 쪽이 이 표시로 웹 개발자에게 신호를 보내는 자리이기도 하다.

| 애노테이션 | 언제 확인되나 | 무엇을 알리나 |
| --- | --- | --- |
| `@Override` | 컴파일 시점 | 재정의가 맞는지 검사해 달라 |
| `@Deprecated` | 컴파일 시점(경고) | 이건 이제 쓰지 말라 |
| `@SuppressWarnings` | 컴파일 시점 | 이 경고는 무시해도 된다 |

셋 다 실행 중에 무언가를 하는 것이 아니라 **컴파일러에게 말을 거는** 표시다. 다음에 만들 애노테이션은 성격이 다르다 — 실행 중에 읽힌다.

### 1-4. 애노테이션 만들기 — @interface

애노테이션은 `@interface` 키워드로 정의한다. 인터페이스와 비슷하게 생겼지만 `@` 가 앞에 붙는다.

```java
@Retention(RetentionPolicy.RUNTIME)
@Target(ElementType.METHOD)
@interface MyAnnotation {
    String value();
    int data() default 1;
}
```

정의 자체에도 애노테이션이 둘 붙어 있다. 애노테이션에 붙는 애노테이션이라 **메타 애노테이션**이라고 부른다. 애노테이션을 만들 때는 "언제까지 살아 있을지"와 "어디에 붙일 수 있는지" 둘을 정해 주는 것이 기본이다.

필요한 import는 다음과 같다.

```java
import java.lang.annotation.ElementType;
import java.lang.annotation.Retention;
import java.lang.annotation.RetentionPolicy;
import java.lang.annotation.Target;
import java.lang.reflect.Method;
```

앞의 넷은 애노테이션을 만들기 위한 것이고, `java.lang.reflect.Method` 는 뒤에서 리플렉션으로 메소드를 꺼낼 때 쓴다. 패키지 이름이 갈리는 것에서 두 일이 서로 다른 축이라는 게 드러난다 — **만드는 쪽은 `annotation`, 읽는 쪽은 `reflect`** 다.

### 1-5. @Retention — 애노테이션이 언제까지 살아 있을까

`RetentionPolicy` 는 애노테이션의 생명주기를 정한다. 세 단계가 있다.

| 값 | 남는 곳 | 실행 중 읽기 |
| --- | --- | --- |
| `SOURCE` | 소스 코드에만 (컴파일하면 사라짐) | 불가 |
| `CLASS` | `.class` 파일까지 (기본값) | 불가 |
| `RUNTIME` | 실행 중 메모리까지 | **가능** |

여기서 `RUNTIME` 을 고른 이유는 뒤에서 **실행 중에 이 애노테이션을 읽어 낼 것**이기 때문이다. `SOURCE` 나 `CLASS` 로 두면 리플렉션으로 꺼낼 때 값이 잡히지 않는다.

`@Override` 처럼 컴파일러만 보고 끝나는 표시는 `SOURCE` 로 충분하고, 스프링의 `@RestController` 처럼 서버가 뜬 뒤 읽혀야 하는 표시는 `RUNTIME` 이어야 한다. 정리하면 **"누가 언제 읽을 것인가"가 곧 `@Retention` 값을 정한다.**

### 1-6. @Target — 어디에 붙일 수 있을까

`ElementType` 은 이 애노테이션을 붙일 수 있는 자리를 제한한다.

| 값 | 붙는 자리 |
| --- | --- |
| `TYPE` | 클래스·인터페이스·열거형 |
| `METHOD` | 메소드 |
| `FIELD` | 멤버변수 |
| `PARAMETER` | 매개변수 |
| `CONSTRUCTOR` | 생성자 |
| `LOCAL_VARIABLE` | 지역변수 |

`METHOD` 하나만 지정했으니 이 애노테이션은 메소드에만 붙는다. 클래스나 필드에 붙이면 컴파일 오류가 난다.

제한을 걸어 두는 이유는 **잘못 붙이는 것을 컴파일 시점에 막기 위해서**다. 읽는 쪽 코드가 "메소드에 붙어 있을 것"을 전제로 짜여 있는데 엉뚱한 자리에 붙으면 실행 중에야 문제가 드러난다. 붙일 자리를 정의에서 못 박아 두면 그 사고 자체가 생기지 않는다.

여러 자리에 붙이고 싶으면 배열로 적는다.

```java
@Target({ ElementType.METHOD, ElementType.TYPE })
```

### 1-7. 애노테이션의 속성 — 추상메소드처럼 생겼다

애노테이션 안에 적는 것은 **속성**이다. 모양은 인터페이스의 추상메소드와 같지만 실제로는 "이 애노테이션이 받을 수 있는 값"의 선언이다.

```java
String value();          // 필수 — 값을 반드시 줘야 한다
int data() default 1;    // 선택 — 생략하면 1
```

| 표기 | 뜻 |
| --- | --- |
| `String value();` | `String` 타입 값을 받는 `value` 속성, 기본값 없음 → 필수 |
| `int data() default 1;` | `int` 타입 `data` 속성, 생략하면 `1` |

`default` 가 있으면 생략할 수 있고, 없으면 붙일 때 반드시 값을 줘야 한다. 이 갈림이 **"이 표시를 쓰려면 최소한 무엇을 알려 줘야 하는가"** 를 정하는 자리다.

속성으로 쓸 수 있는 타입은 기본형·`String`·`Class`·열거형·다른 애노테이션과 그 배열로 제한된다. 아무 객체나 담을 수는 없다.

### 1-8. 애노테이션 주입 — 만든 표시를 실제로 달아 본다

정의한 애노테이션을 클래스의 메소드에 붙인다.

```java
class TestClass {
    @MyAnnotation(value = "안녕하세요", data = 10)
    void method3() {
        System.out.println("메소드3 실행");
    }

    @MyAnnotation(value = "안녕하세요2")
    void method4() {
        System.out.println("메소드 4 실행");
    }
}
```

`method3` 은 속성 둘을 다 채웠고, `method4` 는 `data` 를 생략했다. 생략한 쪽은 `default 1` 이 그대로 값이 된다.

여기까지가 표시를 다는 데까지다. 이 상태에서 `TestClass` 를 그냥 실행해도 애노테이션은 아무 일도 하지 않는다. 값이 어딘가에 붙어 있을 뿐이다.

### 1-9. 리플렉션으로 클래스 정보 얻기

이제 읽는 쪽이다. 먼저 클래스의 정보를 담은 `Class` 객체를 얻는다.

```java
Class<TestClass> class2 = TestClass.class;
```

[[Java day13 Object 클래스와 리플렉션]] 에서 본 두 가지(`getClass()`·`Class.forName()`) 외에 세 번째 방법이다.

| 방법 | 표기 | 성격 |
| --- | --- | --- |
| 객체에서 | `obj.getClass()` | 객체가 이미 있어야 한다 |
| 이름 문자열로 | `Class.forName("패키지.클래스")` | 컴파일 시점에 검사 못 함 → 검사 예외 |
| 클래스 리터럴 | `TestClass.class` | 컴파일 시점에 확인된다 |

`.class` 표기는 객체를 만들지 않고도 클래스 정보를 얻는다. 이름을 코드에 직접 적으니 오타가 있으면 컴파일이 안 되고, 예외 처리도 필요 없다.

`Class<TestClass>` 처럼 제네릭으로 적어 두면 어떤 클래스의 정보인지가 타입에 남는다 — [[Java day14 제네릭]] 에서 본 그 타입 파라미터다. 뒤에서 `newInstance()` 가 돌려주는 값이 `TestClass` 타입으로 잡히는 것도 이 덕분이다.

### 1-10. 메소드를 꺼내고 애노테이션을 읽는다

이어지는 부분이 오늘의 핵심이다. 리플렉션 계열 호출은 대부분 검사 예외를 던지므로 `try-catch` 안에 들어간다.

```java
try {
    // 2. 메소드 꺼내기
    Method method = class2.getMethod("method3");

    // 3. 메소드에 붙은 애노테이션 확인
    MyAnnotation annotation = method.getAnnotation(MyAnnotation.class);

    // 4. 애노테이션의 속성 확인
    System.out.println(annotation.value());   // 안녕하세요
    System.out.println(annotation.data());    // 10
} catch (Exception e) {
    System.out.println(e);
}
```

한 줄씩 뜯어보면 이렇다.

| 호출 | 하는 일 |
| --- | --- |
| `class2.getMethod("method3")` | 이름이 `method3` 인 메소드를 `Method` 객체로 꺼낸다 |
| `method.getAnnotation(MyAnnotation.class)` | 그 메소드에 붙은 `MyAnnotation` 을 꺼낸다 |
| `annotation.value()` | 속성 값을 읽는다 — 선언할 때의 메소드 모양 그대로 부른다 |

여기서 애노테이션을 **속성 선언에 적은 메소드 이름으로 읽는다**는 게 드러난다. `String value();` 라고 적었으니 `annotation.value()` 로 꺼낸다. 추상메소드처럼 생긴 이유가 여기 있다.

`getAnnotation` 이 `null` 을 돌려줄 수 있다는 점은 기억해 둘 만하다. 해당 애노테이션이 붙어 있지 않거나, `@Retention` 이 `RUNTIME` 이 아니면 잡히지 않는다. 붙어 있을 것을 전제로 바로 `.value()` 를 부르면 `NullPointerException` 이 나므로, 확인을 먼저 두는 편이 안전하다(2-3).

### 1-11. 동적 로딩 — 객체를 만들고 메소드를 실행한다

읽어 낸 정보로 실제 실행까지 간다.

```java
// 5. 동적 로딩
TestClass testClass = class2.getDeclaredConstructor().newInstance();
method.invoke(testClass);   // 메소드3 실행
```

| 호출 | 하는 일 |
| --- | --- |
| `getDeclaredConstructor()` | 매개변수 없는 생성자를 꺼낸다 |
| `.newInstance()` | 그 생성자로 객체를 만든다 — `new TestClass()` 와 같은 결과 |
| `method.invoke(대상객체)` | 꺼내 둔 메소드를 그 객체에 대고 실행한다 |

`new` 를 쓰지 않고 객체를 만들었고, `testClass.method3()` 이라고 적지 않고 메소드를 실행했다. 이 두 줄이 **코드에 이름을 박지 않고도 객체를 만들고 메소드를 부를 수 있다**는 것을 보여 준다.

`invoke` 의 첫 번째 인자는 "어느 객체에 대고 부를 것인가"다. 인스턴스 메소드라 대상 객체가 필요하고, `static` 메소드라면 `null` 을 넘긴다. 메소드가 매개변수를 받는다면 두 번째 인자부터 값을 이어 붙인다.

```java
method.invoke(대상, 값1, 값2);
```

기본 생성자가 필요한 자리가 또 나온 셈이다. [[Java Spring day02 스프링 부트 실행과 계층 이식]] 에서 DTO에 기본 생성자를 남겨 두던 이유와 같다 — **프레임워크가 객체를 만들 때 쓰는 통로**이기 때문이다.

### 1-12. 정리 — 스프링이 하는 일의 축소판

한 파일 안에서 세 단계가 이어졌다.

```
① 표시를 정의한다        @interface MyAnnotation
② 코드에 표시를 단다      @MyAnnotation(value = "...") void method3()
③ 표시를 읽고 실행한다    getAnnotation → invoke
```

스프링이 하는 일이 정확히 이 구조다.

| 이 파일 | 스프링 |
| --- | --- |
| `@interface MyAnnotation` | `@RestController`·`@GetMapping` 정의 |
| `@MyAnnotation(value = "...")` | 개발자가 컨트롤러에 매핑 애노테이션 달기 |
| `getAnnotation` 으로 값 읽기 | 서버가 뜰 때 주소 값을 읽어 표에 등록 |
| `method.invoke(...)` | 요청이 오면 짝이 맞는 메소드를 실행 |

`@GetMapping("/board")` 가 붙은 메소드가 그 주소로 요청이 왔을 때 불리는 이유가 여기서 설명된다. 스프링이 시작할 때 클래스들을 훑어 애노테이션이 붙은 메소드를 모으고, **주소 → 메소드 표**를 만들어 둔 다음, 요청이 오면 그 표에서 찾아 `invoke` 로 부른다.

`@Retention(RUNTIME)` 이 왜 필요했는지도 여기서 이어진다. 서버는 컴파일이 다 끝난 뒤에 뜨므로, 그때까지 표시가 살아 있지 않으면 읽을 수가 없다.

## 2. 추가로 알면 좋은 활용법

### 2-1. value 하나만 쓸 때는 이름을 생략할 수 있다

속성 이름이 `value` 이고 그것 하나만 채울 때는 이름을 적지 않아도 된다.

```java
@MyAnnotation("안녕하세요")                 // value = 생략 가능
@MyAnnotation(value = "안녕하세요")          // 위와 같은 뜻
@MyAnnotation(value = "안녕", data = 10)    // 둘 이상이면 이름을 적는다
```

`@GetMapping("/board")` 처럼 스프링 애노테이션에 값을 하나만 던지는 표기가 이 규칙 위에서 돌아간다. 그래서 관습적으로 **가장 자주 쓰는 속성의 이름을 `value` 로 둔다.**

### 2-2. 붙어 있는지 먼저 확인하기 — isAnnotationPresent

`getAnnotation` 의 `null` 을 매번 검사하는 대신 존재 여부만 물어볼 수 있다.

```java
if (method.isAnnotationPresent(MyAnnotation.class)) {
    MyAnnotation ann = method.getAnnotation(MyAnnotation.class);
    System.out.println(ann.value());
}
```

또는 꺼낸 뒤에 `null` 을 거른다.

```java
MyAnnotation ann = method.getAnnotation(MyAnnotation.class);
if (ann != null) {
    System.out.println(ann.value());
}
```

둘 중 어느 쪽이든, **표시가 없을 수도 있다는 전제로 코드를 쓰는 것**이 리플렉션 쪽의 기본 자세다.

### 2-3. 메소드를 전부 훑어 표시된 것만 실행하기

이름을 하나 지정해 꺼내는 대신 **선언된 메소드를 모두 가져와** 애노테이션이 붙은 것만 고를 수 있다. 프레임워크가 실제로 하는 일에 훨씬 가까운 모양이다.

```java
for (Method m : TestClass.class.getDeclaredMethods()) {
    MyAnnotation ann = m.getAnnotation(MyAnnotation.class);
    if (ann != null) {
        System.out.println(m.getName() + " → " + ann.value() + ", " + ann.data());
        m.invoke(대상객체);
    }
}
```

이렇게 하면 `method3` 과 `method4` 가 모두 걸린다. 클래스에 메소드를 추가하고 표시만 붙이면 읽는 쪽 코드는 손대지 않아도 되는데, **컨트롤러에 매핑 하나를 더 추가하면 그냥 동작하는 이유**가 이 구조다.

### 2-4. getMethod와 getDeclaredMethod의 갈림

이름이 비슷한 메소드가 짝으로 있고, 가져오는 범위가 다르다.

| 메소드 | 범위 |
| --- | --- |
| `getMethod` / `getMethods` | `public` 만, 상속받은 것 포함 |
| `getDeclaredMethod` / `getDeclaredMethods` | 접근제한자 무관, 그 클래스에 선언된 것만 |

`TestClass` 의 `method3` 은 접근제한자를 적지 않아 default 범위인데, 같은 패키지에서 부르고 있어 `getMethod` 로도 잡힌다. 패키지가 갈리면 `getDeclaredMethod` 쪽을 써야 한다.

매개변수가 있는 메소드를 꺼낼 때는 타입까지 같이 넘긴다. 이름만으로는 오버로딩된 것 중 어느 쪽인지 정해지지 않기 때문이다.

```java
Method m = 클래스.getMethod("메소드명", String.class, int.class);
```

### 2-5. private 멤버에 접근하기 — setAccessible

`private` 으로 닫아 둔 필드나 메소드도 리플렉션으로는 열 수 있다.

```java
Method m = 클래스.getDeclaredMethod("숨은메소드");
m.setAccessible(true);   // 접근 검사 끄기
m.invoke(대상);
```

캡슐화를 뚫는 동작이라 평소 코드에서 쓸 일은 없다. 다만 프레임워크가 `private` 필드에 값을 넣어 주는(의존성 주입, JSON 역직렬화 같은) 자리에서 실제로 쓰이는 통로다. [[Java day08 접근제한자와 static]] 에서 본 접근제한자가 **컴파일러의 약속이지 물리적인 잠금은 아니라는 점**이 여기서 드러난다.

### 2-6. 리플렉션에서 나오는 예외들

`catch (Exception e)` 하나로 묶었지만, 실제로는 여러 검사 예외가 나온다. 어떤 단계에서 실패했는지 갈라 보려면 나눠 잡는 편이 낫다.

| 예외 | 언제 |
| --- | --- |
| `ClassNotFoundException` | `Class.forName` 의 문자열에 해당하는 클래스가 없을 때 |
| `NoSuchMethodException` | 그 이름·매개변수의 메소드가 없을 때 |
| `IllegalAccessException` | 접근할 수 없는 멤버를 부를 때 |
| `InstantiationException` | 추상 클래스 등 객체를 만들 수 없을 때 |
| `InvocationTargetException` | `invoke` 로 부른 **메소드 안에서** 예외가 났을 때 |

마지막 것이 특히 헷갈리기 쉽다. 실행한 메소드가 던진 예외가 한 겹 감싸여 올라오는 것이라, 원래 원인은 `e.getCause()` 로 꺼내야 보인다.

```java
catch (InvocationTargetException e) {
    System.out.println(e.getCause());   // 진짜 원인
}
```

예외를 `System.out.println(e)` 로 찍고 끝내면 어디서 끊겼는지가 흐려진다. [[Java day12 예외 처리와 JDBC]] 에서 본 것처럼 예외 종류별로 갈라 두면 원인을 좁히기가 훨씬 쉽다.

### 2-7. 다른 메타 애노테이션들

`@Retention`·`@Target` 외에 애노테이션 정의에 붙일 수 있는 것이 몇 가지 더 있다.

| 메타 애노테이션 | 뜻 |
| --- | --- |
| `@Documented` | javadoc 문서에 이 애노테이션도 표시한다 |
| `@Inherited` | 클래스에 붙인 애노테이션을 자식 클래스도 물려받는다 |
| `@Repeatable` | 같은 애노테이션을 한 자리에 여러 번 붙일 수 있게 한다 |

`@Inherited` 는 `TYPE` 에 붙은 애노테이션에만 적용되고 메소드에는 상속되지 않는다는 제한이 있다. 필요한 것만 골라 붙이면 되고, 실무에서 가장 자주 정하는 것은 역시 `@Retention` 과 `@Target` 둘이다.

### 2-8. 애노테이션에 속성을 어떻게 나눌까

만드는 쪽에서 정할 것은 결국 두 가지다.

- **필수로 둘 것** — 이 표시를 쓰려면 반드시 알려 줘야 하는 정보 (`default` 없이)
- **선택으로 둘 것** — 대개 같은 값이라 생략할 수 있는 정보 (`default` 붙여서)

`@GetMapping` 을 떠올려 보면 주소는 사실상 필수고, 나머지(`produces`·`consumes` 등)는 기본값이 있어 대부분 생략한다. **자주 쓰는 경우가 짧게 적히도록** 기본값을 잡는 것이 쓰기 좋은 애노테이션의 모양이다.

### 2-9. 배열 속성과 기본값

속성 타입으로 배열도 쓸 수 있고, 기본값도 배열로 준다.

```java
@interface MyAnnotation2 {
    String[] tags() default {};
    Class<?> type() default Object.class;
}
```

값이 하나뿐이면 중괄호를 생략할 수 있다.

```java
@MyAnnotation2(tags = "one")            // { "one" } 과 같다
@MyAnnotation2(tags = { "one", "two" })
```

`@Target({ ElementType.METHOD, ElementType.TYPE })` 이 중괄호를 쓰는 것도 `ElementType[]` 속성이기 때문이다.

### 2-10. 애노테이션만으로는 아무 일도 일어나지 않는다

되짚어 둘 만한 지점이다. 애노테이션을 아무리 잘 정의하고 정성껏 달아도, **읽는 쪽 코드가 없으면 실행 결과는 달라지지 않는다.**

이걸 알아 두면 스프링에서 애노테이션을 붙였는데 동작하지 않을 때 볼 자리가 좁혀진다. 대체로 "표시를 안 달았다"가 아니라 **"읽는 쪽이 그 클래스를 훑지 않았다"** 쪽인 경우가 많다 — 컴포넌트 스캔 범위 밖에 클래스가 있는 상황이 대표적이다. [[Java Spring day02 스프링 부트 실행과 계층 이식]] 에서 진입점의 패키지가 곧 스캔 범위가 된다고 본 그 이야기와 이어진다.

## 3. 더 나아가 알면 좋은 것

### 3-1. 컴포넌트 스캔 — 클래스를 훑어 표시를 찾는다

스프링이 시작할 때 하는 일을 이제 조금 더 구체적으로 그릴 수 있다.

```
① 진입점 패키지 아래의 클래스 파일을 전부 찾는다
② 각 클래스에 @Component 계열 표시가 붙어 있는지 읽는다   ← getAnnotation
③ 붙어 있으면 객체를 만들어 컨테이너에 담는다              ← newInstance
④ 메소드마다 @GetMapping 같은 표시를 읽어 주소 표를 만든다
⑤ 요청이 오면 표에서 찾아 그 메소드를 부른다               ← invoke
```

오늘 쓴 세 호출(`getAnnotation`·`newInstance`·`invoke`)이 그대로 자리를 잡고 있다. 규모와 예외 처리·성능 최적화가 다를 뿐 구조 자체는 같다.

`@Controller`·`@Service`·`@Repository` 가 결국 같은 계열인데도 이름을 나눠 둔 이유도 여기서 보인다 — 읽는 쪽에서 **계층별로 다르게 처리할 여지**를 남기기 위해서다.

### 3-2. 메타 애노테이션과 합성 애노테이션

스프링 애노테이션은 애노테이션 위에 애노테이션을 쌓아 만든다.

```
@RestController = @Controller + @ResponseBody
@GetMapping     = @RequestMapping(method = GET)
@SpringBootApplication = @SpringBootConfiguration + @EnableAutoConfiguration + @ComponentScan
```

`@RestController` 하나만 붙여도 컨트롤러로 등록되고 반환값이 데이터로 나가는 이유가 이것이다. 읽는 쪽에서 **애노테이션에 붙은 애노테이션까지 따라 올라가며 확인**하기 때문에, 자주 쓰는 조합에 짧은 이름을 붙여 둘 수 있다.

직접 만들 때도 같은 방식을 쓸 수 있다. 사내 규칙을 담은 애노테이션 하나에 여러 표시를 모아 두는 식이다.

### 3-3. AOP와 프록시 — 표시를 보고 코드를 끼워 넣는다

애노테이션 + 리플렉션의 다음 단계가 AOP(관점 지향 프로그래밍)다. `@Transactional` 이 붙은 메소드를 실행할 때 앞뒤로 트랜잭션 시작·커밋 코드가 자동으로 끼어드는 것이 대표적이다.

원리는 대상 객체를 그대로 쓰지 않고 **한 겹 감싼 대리 객체(프록시)** 를 만들어 두는 것이다. 호출이 오면 프록시가 먼저 받아 앞뒤 처리를 하고 가운데서 원래 메소드를 `invoke` 한다.

- 로깅, 트랜잭션, 권한 검사처럼 **여러 곳에 되풀이되는 처리**를 한 자리로 모을 때 쓴다
- 프록시를 거치지 않는 호출(같은 클래스 안에서 자기 메소드를 직접 부르는 경우)에는 안 먹힌다는 제약이 있다

### 3-4. 애노테이션 프로세서 — 컴파일 시점에 읽는 갈래

여기서는 실행 중에 읽었지만(`RUNTIME`), 컴파일 시점에 읽어 **코드를 생성**하는 갈래도 있다.

- 롬복(Lombok)의 `@Getter`·`@Setter` 가 이 방식이다. 컴파일할 때 getter·setter 코드를 만들어 넣는다
- 실행 중에 하는 일이 없으니 성능 부담이 없다는 것이 장점이다
- 대신 생성된 코드가 소스에 보이지 않아 IDE 지원이 필요하다

DTO마다 getter·setter를 손으로 적던 [[Java day08 접근제한자와 static]] 의 되풀이를 줄이는 방향이기도 하다.

### 3-5. 리플렉션의 비용과 쓰는 자리

리플렉션은 편한 만큼 대가가 있다.

- **느리다.** 이름으로 찾고 접근 검사를 우회하는 과정이 일반 호출보다 무겁다
- **컴파일러가 검사해 주지 못한다.** 메소드 이름을 문자열로 적으므로 오타가 실행 중에야 드러난다
- **리팩터링에 취약하다.** 이름을 바꿔도 문자열은 따라가지 않는다

그래서 요청이 올 때마다 반복해서 리플렉션을 돌리지 않고, **시작할 때 한 번 읽어 표로 만들어 두는** 방식을 쓴다. 스프링이 서버 기동 시점에 주소 표를 만들어 두는 것이 그 이유다.

일반 업무 코드에서 리플렉션을 직접 쓸 일은 드물다. 다만 **쓰는 라이브러리가 그것으로 돌아간다**는 것을 알아 두면, 기본 생성자가 왜 필요한지·`private` 필드에 값이 어떻게 들어가는지 같은 것이 설명된다.

### 3-6. 다음에 볼 키워드

- `@Component`·`@Service`·`@Repository` — 계층별 컴포넌트 표시와 스캔
- `@Autowired`·생성자 주입 — 컨테이너가 객체를 넣어 주는 통로
- `@Configuration`·`@Bean` — 직접 등록하는 방식
- `@Valid`·`@NotNull` — 검증도 애노테이션으로
- `@Transactional` 과 프록시 기반 AOP
- `ApplicationContext` 와 빈 생명주기(`@PostConstruct`·`@PreDestroy`)
- `HandlerMapping`·`HandlerAdapter` — 주소 표를 만들고 메소드를 부르는 실제 자리
- Lombok과 애노테이션 프로세서
- `MethodHandle` — 리플렉션보다 빠른 대안

## 실습 파일

- `2026B_Spring/springweb/src/main/java/day03/exam/exam1.java` (애노테이션이 주석과 갈리는 지점과 기계가 읽는 표시라는 성격, `@Override` 로 재정의를 컴파일러에게 검사시키기와 재정의된 메소드가 불리는 확인·`super` 로 부모 메소드 부르기, `@Deprecated` 로 사용 권장하지 않음을 알리기와 실행은 되지만 경고가 나는 자리, `@interface` 로 애노테이션 직접 정의하기, 메타 애노테이션 `@Retention` 과 `RetentionPolicy` 세 단계(`SOURCE`·`CLASS`·`RUNTIME`)·실행 중에 읽으려면 `RUNTIME` 이어야 하는 이유, `@Target` 과 `ElementType` 으로 붙일 자리 제한하기·여러 자리를 배열로 적기, 애노테이션 속성이 추상메소드 모양인 이유와 `default` 유무로 갈리는 필수·선택, 속성으로 쓸 수 있는 타입의 제한, 정의한 애노테이션을 메소드에 달고 속성 생략 시 기본값이 채워지는 자리, `java.lang.annotation` 과 `java.lang.reflect` 로 갈리는 두 축, `클래스.class` 리터럴로 `Class` 얻기와 `getClass()`·`Class.forName()` 과의 갈림·제네릭 `Class<T>` 로 타입 남기기, `getMethod(이름)` 으로 `Method` 꺼내기, `getAnnotation(애노테이션.class)` 로 표시 읽기와 `null` 이 나올 수 있는 자리, 속성 이름 그대로 메소드처럼 값 읽기, `getDeclaredConstructor().newInstance()` 로 `new` 없이 객체 만들기와 기본 생성자가 필요한 이유, `method.invoke(대상)` 으로 이름을 코드에 박지 않고 메소드 실행하기·`static` 이면 `null`·매개변수를 뒤에 잇기, 리플렉션 계열 호출이 검사 예외를 던지는 자리, 정의→주입→읽기 세 단계가 스프링의 컴포넌트 스캔·주소 매핑과 같은 구조라는 정리)

## 관련 노트

[[Java MOC]] · [[Java Spring day02 스프링 부트 실행과 계층 이식]] · [[Java Spring day01 서블릿과 HTTP 메소드]] · [[Java Spring Boot 프로젝트 생성(분석)]] · [[Java day13 Object 클래스와 리플렉션]] · [[Java day14 제네릭]] · [[Java day12 예외 처리와 JDBC]] · [[Java day11 인터페이스]] · [[Java day10 상속과 다형성]] · [[Java day08 접근제한자와 static]] · [[Java day05 클래스와 인스턴스]] · [[개념 - 싱글톤]] · [[KDT_2026 학습 지도]]
