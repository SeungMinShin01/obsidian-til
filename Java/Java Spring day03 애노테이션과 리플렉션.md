---
출처: Claude 분석
원본: KDT_2026/2026B_Spring/springweb/src/main/java/day03/exam, springweb/build.gradle
작성일: 2026-08-31
tags: [학습, java]
---

# Java Spring day03 — 애노테이션과 리플렉션

> 실습 파일: `2026B_Spring/springweb/src/main/java/day03/exam/exam1.java`, `exam2.java`, `exam3.java`, `RestController1.java`, `RestController2.java`, `AppStart.java`, `springweb/build.gradle`
> 허브: [[Java MOC]] · 이전: [[Java Spring day02 스프링 부트 실행과 계층 이식]]

[[Java Spring day02 스프링 부트 실행과 계층 이식]] 까지는 `@SpringBootApplication`·`@RestController`·`@GetMapping` 같은 애노테이션을 **가져다 쓰는** 쪽이었다. 붙이면 동작한다는 것까지는 확인했지만, 그 표시 하나가 어떻게 실제 동작으로 이어지는지는 열어 보지 않았다.

day03은 그 안쪽을 본다. 애노테이션을 직접 만들고, 만든 애노테이션을 클래스에 달고, **리플렉션으로 그 표시를 읽어 메소드를 실행**하는 데까지 한 파일에서 이어진다. 스프링이 하는 일을 아주 작게 줄여 놓은 축소판인 셈이다.

| 자리 | 하는 일 |
| --- | --- |
| `@Override`·`@Deprecated` | 자바가 미리 만들어 둔 표준 애노테이션 (1-2~1-3) |
| `@interface MyAnnotation` | 애노테이션을 직접 정의하기 (1-4~1-7) |
| `class TestClass` | 만든 애노테이션을 메소드에 달아 두기 (1-8) |
| `main` 의 리플렉션 부분 | 그 표시를 읽어 내고, 객체를 만들고, 메소드를 실행하기 (1-9~1-11) |
| `exam2.java` 의 `class Student` | 남이 만든 애노테이션(롬복)을 가져다 쓰기 — 컴파일 시점에 읽히는 갈래 (1-13~1-17) |
| `exam2.java` 의 `Student.builder()` | 애노테이션 하나로 객체 조립 방식 자체를 바꾸기 (1-18) |
| `exam3.java` | 객체를 **누가** 만드는가 — `new`·싱글톤·스프링 컨테이너 (1-19~1-22) |
| `AppStart.java` | day03 패키지에 진입점을 두고 스캔 범위를 잡기 (1-23) |
| `RestController1.java` | 지금까지 본 표시들을 실제 요청 처리에 얹기 — `@Controller`·`@GetMapping`·`@ResponseBody` (1-24~1-27) |
| `RestController2.java` | 나가는 쪽에서 **들어오는 쪽**으로 — `@RestController`·`@RequestMapping`·`@RequestParam`·`@ModelAttribute` (1-28~1-33) |

`exam2` 는 방향이 반대다. 만드는 쪽이 아니라 **이미 만들어진 애노테이션(롬복)을 가져다 쓰는** 쪽이고, 읽히는 시점도 실행 중이 아니라 컴파일 중이다. 같은 장치의 다른 갈래를 한 날에 둘 다 보는 셈이다.

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

### 1-13. 롬복 — 남이 만들어 둔 애노테이션을 가져다 쓰기

`exam1` 이 애노테이션을 **만들고 읽는** 쪽이었다면, `exam2` 는 이미 만들어져 있는 애노테이션을 **가져다 쓰는** 쪽이다. 여기서 쓰는 것이 롬복(Lombok)이다.

롬복은 DTO를 만들 때마다 되풀이하던 코드 — 생성자, getter·setter, `toString`, `equals`·`hashCode` — 를 애노테이션 하나로 대신 만들어 주는 라이브러리다. [[Java day05 클래스와 인스턴스]] 부터 [[Java Spring day02 스프링 부트 실행과 계층 이식]] 까지 DTO를 만들 때마다 손으로 적던 그 부분이다.

먼저 `build.gradle` 에 의존성을 추가한다.

```gradle
dependencies {
    // 3. 롬북
    compileOnly 'org.projectlombok:lombok'
    annotationProcessor 'org.projectlombok:lombok'
}
```

두 줄로 갈려 있는 것이 롬복의 성격을 그대로 말해 준다.

| 설정 | 뜻 |
| --- | --- |
| `compileOnly` | 컴파일할 때만 있으면 된다 — 실행할 때 배포본에는 들어가지 않는다 |
| `annotationProcessor` | 컴파일 중에 애노테이션을 읽고 코드를 생성하는 처리기로 등록한다 |

`implementation` 이 아니라 `compileOnly` 인 이유가 여기 있다. 롬복은 **컴파일이 끝나면 할 일이 끝나는** 라이브러리라 실행 시점에는 필요가 없다.

### 1-14. 컴파일 시점에 읽는 갈래 — 애노테이션 프로세서

`exam1` 에서 만든 `MyAnnotation` 은 `@Retention(RUNTIME)` 이었고, 실행 중에 리플렉션으로 읽혔다. 롬복은 반대쪽 갈래다.

| 갈래 | 언제 읽나 | 읽는 주체 | 결과 |
| --- | --- | --- | --- |
| 리플렉션 (`RUNTIME`) | 프로그램 실행 중 | 프레임워크 코드 | 그때그때 판단해서 동작 |
| 애노테이션 프로세서 (`SOURCE`) | 컴파일하는 중 | 컴파일러에 끼워 넣은 처리기 | **소스에 없던 코드가 생성된다** |

롬복은 컴파일할 때 `@Getter` 가 붙은 클래스를 보고 getter 메소드를 만들어 넣는다. 그래서 `.java` 파일에는 메소드가 안 보이는데 `.class` 에는 들어 있다. 실행 중에 롬복이 무언가를 하는 것이 아니라 **이미 만들어진 코드가 평범하게 실행되는** 것이라, 리플렉션과 달리 성능 부담이 없다.

같은 애노테이션이라는 장치를 놓고 `@Retention` 값에 따라 읽는 시점과 읽는 주체가 갈린다는 것이 1-5의 표가 실제로 쓰이는 자리다.

### 1-15. 생성자를 만들어 주는 애노테이션

`exam2` 의 `Student` 클래스에는 멤버변수만 남아 있고 생성자가 없다.

```java
@NoArgsConstructor
@AllArgsConstructor
// @RequiredArgsConstructor
class Student {
    private String name;
    private int kor;
    private int math;
}
```

셋의 갈림은 이렇다.

| 애노테이션 | 만들어 주는 생성자 | 손으로 쓰면 |
| --- | --- | --- |
| `@NoArgsConstructor` | 매개변수 없는 생성자 | `Student() {}` |
| `@AllArgsConstructor` | 모든 멤버변수를 받는 생성자 | `Student(String name, int kor, int math) {...}` |
| `@RequiredArgsConstructor` | `final` 이거나 `@NonNull` 인 멤버만 받는 생성자 | 필수 값만 받는 생성자 |

[[Java day06 생성자와 콘솔 게시판]] 에서 본 규칙 하나가 여기서 다시 걸린다 — 생성자를 하나라도 직접 정의하면 기본 생성자가 사라진다는 점이다. `@AllArgsConstructor` 만 붙이면 전체 생성자가 생기면서 기본 생성자가 없어지므로, 둘 다 필요하면 `@NoArgsConstructor` 를 함께 붙인다. 실제로 이 파일도 둘을 같이 붙였다.

기본 생성자가 왜 자꾸 필요한지는 1-11에서 본 그대로다. `newInstance()` 든 JSON을 객체로 되돌리는 과정이든, **프레임워크가 객체를 만드는 통로는 매개변수 없는 생성자**다.

`@RequiredArgsConstructor` 는 스프링에서 의존성 주입에 쓰이는 관용구이기도 하다. 멤버를 `final` 로 두고 이 애노테이션 하나만 붙이면 생성자 주입이 완성된다 — 3-5에서 이어서 본다.

### 1-16. getter·setter·toString

나머지 셋은 메소드를 만들어 준다.

```java
@Getter
@Setter
@ToString
```

| 애노테이션 | 생성되는 것 |
| --- | --- |
| `@Getter` | 멤버변수마다 `getName()`·`getKor()`·`getMath()` |
| `@Setter` | 멤버변수마다 `setName(...)`·`setKor(...)`·`setMath(...)` |
| `@ToString` | 멤버변수 값을 모아 문자열로 만드는 `toString()` |

`private` 으로 닫아 둔 멤버변수를 메소드로 여닫는 구조는 [[Java day08 접근제한자와 static]] 에서 본 캡슐화 그대로다. 손으로 적을 때는 멤버 하나 늘 때마다 메소드 둘을 따라 늘려야 했는데, 애노테이션으로 두면 **멤버변수만 고치면 나머지가 따라온다.**

`@ToString` 이 하는 일은 [[Java day13 Object 클래스와 리플렉션]] 에서 본 `toString()` 재정의다. 재정의하지 않으면 `클래스명@해시값` 이 찍히는 그 자리를, 멤버 값이 보이도록 바꿔 준다.

클래스가 아니라 멤버변수 하나에만 붙이는 것도 된다. 특정 필드만 열고 싶을 때 쓴다.

```java
@Getter @Setter
private String name;
```

### 1-17. @Data와 @EqualsAndHashCode — 묶음 애노테이션

```java
@Data
@EqualsAndHashCode
```

`@Data` 는 자주 같이 쓰는 것들을 하나로 묶은 애노테이션이다.

```
@Data = @Getter + @Setter + @ToString + @EqualsAndHashCode + @RequiredArgsConstructor
```

3-2에서 볼 합성 애노테이션과 같은 발상이다. **자주 쓰는 조합에 짧은 이름을 붙여 둔 것**이라, `@Data` 하나만 붙여도 위의 것들이 다 따라온다. 개별 애노테이션을 함께 적어 두면 무엇이 생기는지가 코드에 드러나는 이점은 있다.

`@EqualsAndHashCode` 는 `equals()` 와 `hashCode()` 를 멤버변수 값 기준으로 재정의한다. 기본 동작과 갈리는 지점이 핵심이다.

| | 재정의 전 | `@EqualsAndHashCode` 후 |
| --- | --- | --- |
| `equals` 기준 | 같은 객체인가(주소) | 멤버변수 값이 같은가 |
| `hashCode` | 주소 기반 | 멤버변수 값 기반 |

[[Java day13 Object 클래스와 리플렉션]] 에서 `equals` 를 값 비교로 바꿔야 했던 이유, [[Java day15 Map과 HashMap]] 에서 키로 쓸 객체는 `hashCode` 와 `equals` 가 짝으로 맞아야 했던 이유가 그대로 이어진다. 둘 중 하나만 재정의하면 `HashMap` 이나 `HashSet` 에서 어긋나므로, **짝으로 함께 만들어 주는 애노테이션 하나로 두는 편이 안전하다.**

정리하면 `Student` 클래스는 멤버변수 세 개만 적혀 있지만, 컴파일이 끝나면 생성자 둘과 메소드 열 개 남짓이 들어 있는 클래스가 된다. [[Java day12 종합예제 JDBC DAO]] 에서 DTO마다 길게 적던 부분이 애노테이션 몇 줄로 줄어든 셈이다.

### 1-18. @Builder — 객체를 조립해서 만든다

`Student` 클래스에 애노테이션이 하나 더 붙었다.

```java
@Builder   // 빌더 패턴 지원
```

이것 하나로 객체를 만드는 방식이 하나 더 생긴다.

```java
Student s3 = Student.builder()   // 빌더 시작
        .kor(100)                // 멤버변수에 값 넣기
        .name("강호동")
        .build();                // 빌더 끝 — 여기서 객체가 만들어진다
System.out.println(s3);
```

생성자로 만들 때와 나란히 두면 갈림이 분명하다.

| | 생성자 | 빌더 |
| --- | --- | --- |
| 표기 | `new Student("강호동", 0, 100)` | `Student.builder().name("강호동").kor(100).build()` |
| 값의 순서 | 선언 순서를 지켜야 한다 | **순서 무관** |
| 일부만 넣기 | 그 조합의 생성자가 따로 있어야 한다 | **넣고 싶은 것만 넣는다** |
| 무슨 값인지 | 위치로만 구분된다 | **이름이 코드에 남는다** |

`new Student("강호동", 100, 90)` 을 보면 뒤의 두 숫자가 국어인지 수학인지 코드만 봐서는 알 수 없다. 순서가 뒤바뀌어도 타입이 같으면 컴파일도 통과한다. 빌더는 값마다 이름이 붙으니 **읽는 사람도, 컴파일러도 자리를 헷갈릴 여지가 줄어든다.**

`Student.builder()` 가 객체 없이 바로 불리는 것은 이 메소드가 `static` 이기 때문이다. [[Java day08 접근제한자와 static]] 에서 본 그대로 — 객체가 있어야 부를 수 있는 인스턴스 메소드와 달리, `static` 메소드는 클래스 이름으로 부른다. 객체를 만들기 위한 출발점이라 객체가 없는 상태에서 불려야 하니 `static` 일 수밖에 없다.

`.kor(100).name("강호동")` 처럼 점이 계속 이어지는 것은 **메소드 체이닝**이다. 각 메소드가 값을 넣은 뒤 자기 자신(빌더 객체)을 돌려주기 때문에 다음 점을 바로 찍을 수 있다. 마지막 `build()` 에서 비로소 `Student` 객체가 만들어진다.

넣지 않은 값은 그 타입의 기본값이 된다. 위에서 `math` 를 생략했으니 `0` 이 들어간다 — [[Java day01 자바 구조와 자료형]] 에서 본 멤버변수 기본값 규칙이 그대로 적용되는 자리다.

### 1-19. 객체를 누가 만드는가 — 전통 방식

`exam3` 은 애노테이션에서 한 발 더 나가, **객체를 만드는 주체**를 다룬다. 세 가지 방식을 나란히 놓고 본다.

먼저 지금까지 계속 쓰던 방식이다.

```java
class SampleDao {
    void method() {
        System.out.println("메소드 실행");
    }
}

class SampleController {
    void method() {
        SampleDao sampleDao = new SampleDao();   // 인스턴스 생성(주체)
        sampleDao.method();
    }
}
```

[[Java Spring day02 스프링 부트 실행과 계층 이식]] 에서 컨트롤러가 DAO를 쓰던 모양 그대로다. **다른 클래스의 메소드를 부르려면 그 클래스의 객체가 필요하고, 그 객체를 자기가 직접 `new` 로 만든다.**

여기에 두 가지가 걸려 있다.

- `method()` 가 불릴 때마다 `SampleDao` 객체가 **새로 만들어진다.** 하는 일이 같은데도 호출 횟수만큼 객체가 쌓인다
- `SampleController` 안에 `SampleDao` 라는 이름이 **직접 박혀 있다.** 다른 구현으로 바꾸려면 컨트롤러 코드를 고쳐야 한다

앞의 것은 자원 문제고, 뒤의 것은 결합도 문제다. 뒤쪽이 더 큰데, [[Java day11 인터페이스]] 에서 "구현을 갈아 끼울 수 있게 하자"고 했던 이야기가 `new` 한 줄 때문에 막히는 자리이기 때문이다.

### 1-20. 싱글톤 — 객체를 하나로 고정한다

객체가 계속 만들어지는 쪽을 손으로 막아 보는 방식이다.

```java
class SampleDao2 {
    private SampleDao2() {
    }

    private static final SampleDao2 instance = new SampleDao2();

    public static SampleDao2 getInstance() {
        return instance;
    }
}
```

세 줄이 각자 하나씩 막고 열어 준다.

| 코드 | 하는 일 |
| --- | --- |
| `private SampleDao2()` | 생성자를 닫는다 → 바깥에서 `new` 를 **못 쓴다** |
| `private static final ... instance` | 클래스에 딱 하나 있는 객체를 미리 만들어 둔다 |
| `public static getInstance()` | 그 하나뿐인 객체를 꺼내 가는 **유일한 통로** |

[[Java day08 접근제한자와 static]] 에서 본 것 둘이 여기서 맞물린다. `static` 이라 객체마다가 아니라 **클래스에 하나**로 존재하고, `private` 이라 바깥에서 직접 손대지 못한다. `final` 까지 붙였으니 한 번 정해진 뒤에는 다른 객체로 바뀌지도 않는다.

생성자를 `private` 으로 닫은 것이 핵심이다. [[Java day06 생성자와 콘솔 게시판]] 에서 생성자는 객체를 만드는 입구라고 봤는데, 그 입구를 잠그고 대신 `getInstance()` 라는 창구 하나만 열어 둔 셈이다. 쓰는 쪽은 이렇게 된다.

```java
SampleDao2 dao = SampleDao2.getInstance();   // new 를 쓸 수 없다
```

몇 번을 불러도 같은 객체가 돌아온다. 자세한 이야기는 [[개념 - 싱글톤]] 에 정리해 두었다.

다만 이 방식에도 걸리는 게 있다. **클래스마다 이 세 줄을 손으로 되풀이해야 하고**, 여전히 쓰는 쪽 코드에 `SampleDao2` 라는 이름이 박힌다. 객체 개수 문제는 풀렸지만 결합도 문제는 그대로 남는다.

### 1-21. @Component — 컨테이너에게 맡긴다

스프링의 방식은 되풀이되던 그 세 줄마저 없앤다.

```java
import org.springframework.stereotype.Component;

@Component
class SampleDao3 {
    void method() {
    }
}
```

생성자를 닫지도, `static` 필드를 두지도, 창구 메소드를 만들지도 않았다. 표시 하나만 붙였을 뿐인데 **스프링이 시작할 때 이 클래스의 객체를 대신 만들어 컨테이너에 담아 둔다.** 이렇게 컨테이너가 관리하는 객체를 **빈(Bean)** 이라고 부른다.

1-12에서 정리한 구조가 그대로 돌아가는 자리다.

```
① 시작할 때 클래스를 훑는다
② @Component 가 붙어 있는지 읽는다        ← getAnnotation
③ 붙어 있으면 객체를 만들어 담아 둔다      ← newInstance
```

`@Component` 를 직접 만든다면 `@Retention(RUNTIME)` 에 `@Target(TYPE)` 일 것이라는 짐작도 여기서 선다. 서버가 뜬 뒤에 읽혀야 하니 `RUNTIME` 이고, 클래스에 붙으니 `TYPE` 이다.

그리고 스프링이 만들어 담아 두는 빈은 **기본적으로 하나만 만들어져 공유된다.** 싱글톤과 결과가 같은데, 그 처리를 클래스마다 손으로 적지 않고 컨테이너가 맡는다는 점이 다르다.

### 1-22. IoC와 DI — 제어가 넘어간다

세 방식을 한 표에 놓으면 무엇이 달라졌는지가 보인다.

| | [1] `new` | [2] 싱글톤 | [3] `@Component` |
| --- | --- | --- | --- |
| 객체를 만드는 주체 | 쓰는 쪽(컨트롤러) | 그 클래스 자신 | **스프링 컨테이너** |
| 객체 개수 | 호출할 때마다 새로 | 하나 | 기본 하나(공유) |
| 되풀이되는 코드 | `new` 한 줄 | 생성자·필드·창구 세 줄 | 표시 한 줄 |
| 쓰는 쪽에 박히는 이름 | 구현 클래스 | 구현 클래스 | 필요한 타입만 |

가장 크게 갈리는 것은 첫 줄이다. [1]과 [2]는 **객체를 만들 시점과 방법을 내 코드가 정한다.** [3]은 그 판단이 컨테이너로 넘어간다. 이 뒤집힘을 **IoC(Inversion of Control, 제어의 역전)** 라고 부른다.

| | 제어를 내가 쥘 때 | 제어가 넘어갔을 때 |
| --- | --- | --- |
| 객체 생성 | 내가 `new` 로 만든다 | 컨테이너가 만들어 둔다 |
| 내 코드가 하는 일 | 만들고 · 쓰고 | **쓰기만** 한다 |
| 필요한 것을 얻는 법 | 직접 찾아 만든다 | **받는다** |

마지막 줄이 **DI(Dependency Injection, 의존성 주입)** 다. 필요한 객체를 내가 만들지 않고 밖에서 넣어 주는 것을 말한다. 컨테이너가 객체를 관리하고(IoC), 필요한 곳에 넣어 주는(DI) 두 가지가 짝으로 움직인다.

이렇게 바뀌면 [1]에서 걸렸던 두 가지가 같이 풀린다.

- 객체가 하나로 관리되니 호출할 때마다 쌓이지 않는다
- 쓰는 쪽은 "이런 타입이 필요하다"고만 선언하므로, **구현을 갈아 끼워도 쓰는 쪽 코드가 그대로다.** [[Java day11 인터페이스]] 에서 인터페이스를 두는 이유로 본 그것이 여기서 실제로 성립한다

정리하면 오늘 본 것은 하나의 흐름이다. 애노테이션이라는 표시가 있고(1-1~1-8), 그 표시를 읽어 객체를 만들고 메소드를 부르는 장치가 있고(1-9~1-12), 그 장치 위에 스프링이 **객체 관리 자체를 대신 맡는** 구조를 얹었다(1-19~1-22). `@Component` 한 줄이 세 줄짜리 싱글톤을 대신할 수 있는 근거가 앞의 리플렉션 실습에 다 나와 있는 셈이다.

### 1-23. day03의 진입점 — 스캔 범위는 패키지가 정한다

앞의 세 파일이 `main` 을 직접 돌려 보는 실습이었다면, 여기서부터는 서버를 띄운 상태에서 확인한다. 그러려면 이 패키지에도 진입점이 하나 있어야 한다.

```java
package day03.exam;

@SpringBootApplication   // 1. 내장 톰캣 지원  2. IOC/DI 컴포넌트 지원
public class AppStart {
    public static void main(String[] args) {
        SpringApplication.run(AppStart.class, args);
    }
}
```

[[Java Spring day02 스프링 부트 실행과 계층 이식]] 에서 만든 것과 모양이 같다. 달라진 것은 **어느 패키지에 놓였는가** 하나뿐인데, 그 하나가 등록되는 빈의 범위를 정한다.

```
day02.AppStart  →  day02 패키지 아래만 스캔
day03.exam.AppStart  →  day03.exam 패키지 아래만 스캔
```

`@SpringBootApplication` 안에 `@ComponentScan` 이 들어 있고(3-2), 범위를 따로 적지 않으면 **이 클래스가 속한 패키지와 그 하위**가 대상이 된다. 그래서 같은 프로젝트 안에 컨트롤러가 여러 개 있어도, 띄운 진입점이 어디에 있느냐에 따라 살아나는 것이 갈린다.

1-21에서 `@Component` 를 붙여 두면 컨테이너가 객체를 만들어 준다고 했는데, 그 "훑는 범위"를 정하는 자리가 여기다. 2-10에서 적어 둔 "표시를 달았는데 동작하지 않으면 읽는 쪽부터 본다"가 실제로 걸리는 지점이기도 하다.

### 1-24. @Controller — @Component에 웹 기능을 얹은 표시

컨트롤러 클래스에 붙은 표시가 둘 중 하나로 갈린다.

```java
// @Component   // [싱글톤 대신] 스프링 컨테이너에 해당 클래스의 객체(빈) 등록
@Controller     // [서블릿 대신] HTTP 통신을 지원하는 서블릿 제공 + @Component
public class RestController1 {
```

`@Component` 만 붙여도 빈으로는 등록된다. 다만 그것만으로는 **요청을 받는 자리**가 되지 않는다.

| 표시 | 얻는 것 |
| --- | --- |
| `@Component` | 컨테이너가 객체를 만들어 관리한다 |
| `@Controller` | 그 위에 **HTTP 요청을 받아 처리하는 자리**라는 표시가 얹힌다 |

3-2에서 정리한 합성 애노테이션이 실제로 쓰이는 첫 자리다. `@Controller` 는 `@Component` 를 품고 있어서, 붙이는 순간 빈 등록과 요청 처리 등록이 함께 일어난다. [[Java Spring day01 서블릿과 HTTP 메소드]] 에서 `HttpServlet` 을 물려받아 만들던 자리를 표시 한 줄이 대신하는 셈이다.

계층별로 이름이 갈려 있는 것(`@Controller`·`@Service`·`@Repository`)도 같은 구조다. 셋 다 `@Component` 를 품고 있고, 읽는 쪽에서 계층을 구분할 수 있도록 이름만 나눠 둔 것이다(3-1).

### 1-25. @GetMapping과 @ResponseBody — 주소를 잇고, 나가는 모양을 정한다

메소드마다 표시 둘이 붙는다.

```java
@GetMapping(value = "/day03/task1")   // HTTP 요청 url 매핑/연결
@ResponseBody                          // HTTP 응답: JSON 타입 변환
public int task1() {
    return 10;
}
```

`@GetMapping` 은 주소를 메소드에 잇는다. 1-12에서 그린 "주소 → 메소드 표"에 이 줄이 한 칸으로 들어가고, 그 주소로 요청이 오면 `invoke` 로 이 메소드가 불린다.

속성 이름을 적는 방식과 생략하는 방식이 나란히 나온다.

```java
@GetMapping(value = "/day03/task1")   // 이름을 적은 표기
@GetMapping("/day03/task2")           // value 하나만 채우니 생략할 수 있다
```

2-1에서 본 `value` 생략 규칙이 그대로 적용되는 자리다. 둘은 같은 뜻이라, 값이 하나뿐일 때는 짧은 쪽을 쓰는 편이 읽기 좋다.

`@ResponseBody` 는 반환값을 **응답 본문에 그대로 싣겠다**는 표시다. 붙이지 않으면 `@Controller` 는 돌려준 문자열을 화면 이름으로 읽는다.

| | 반환값을 무엇으로 보나 |
| --- | --- |
| `@Controller` 만 | 보여 줄 **화면(뷰)의 이름** |
| `@Controller` + `@ResponseBody` | **데이터 그 자체** |

[[Java Spring day02 스프링 부트 실행과 계층 이식]] 에서는 클래스에 `@RestController` 를 붙여 이 둘을 한 번에 처리했다. 여기서는 `@Controller` 를 클래스에 두고 `@ResponseBody` 를 메소드마다 붙였는데, 결과는 같지만 **메소드 단위로 고를 수 있다**는 점이 다르다(2-17).

### 1-26. 반환 타입이 Content-Type을 정한다

네 메소드가 서로 다른 타입을 돌려준다. 자바 타입이 무엇이냐에 따라 응답의 `Content-Type` 이 갈린다.

```java
public int task1() { return 10; }
public String task2() { return "안녕하세요"; }
public Map<String, Object> task3() { ... }
public ExamDto task4() { ... }
```

| 반환 타입 | 나가는 Content-Type | 브라우저에 보이는 것 |
| --- | --- | --- |
| `String` | `text/plain` | `안녕하세요` |
| `int` 같은 기본형 | `application/json` | `10` |
| `Map<String, Object>` | `application/json` | `{"유재석":100,"강호동":90}` |
| DTO 객체 | `application/json` | `{"name":"유재석","age":10}` |

정리하면 **문자열만 평문으로 나가고 나머지는 JSON이 된다.** 문자열은 이미 그 자체로 글자라 더 바꿀 것이 없고, 나머지는 자바 안에서만 쓰는 모양이라 오갈 수 있는 형식으로 옮겨야 한다.

`Map` 을 그대로 돌려주면 **키가 JSON의 키가 되고 값이 값이 된다.** [[Java day15 Map과 HashMap]] 에서 본 `{ key : value }` 구조가 JSON의 모양과 거의 그대로 맞아떨어져서, DTO를 따로 만들지 않고도 응답을 조립할 수 있다.

```java
Map<String, Object> map = new HashMap<>();
map.put("유재석", 100);
map.put("강호동", 90);
return map;
```

값 타입을 `Object` 로 열어 둔 덕분에 숫자든 문자열이든 한 맵에 섞어 담을 수 있다 — [[Java day14 제네릭]] 에서 본 타입 파라미터를 넓게 잡는 쪽이다. 대신 꺼내 쓸 때 타입이 보장되지 않으므로, 서버 안에서 다시 쓰는 값이 아니라 **내보내고 끝나는 자리**에 어울린다.

이 변환을 스프링이 자동으로 해 준다는 점이 핵심이다. 서블릿으로 직접 짤 때는 `Content-Type` 을 손으로 정하고 문자열을 만들어 써 보냈는데, 여기서는 **반환 타입만 정하면 나머지는 알아서 맞춰진다**(3-8).

### 1-27. 롬복이 붙은 DTO가 JSON이 되는 자리

`task4` 가 돌려주는 `ExamDto` 는 같은 파일 아래쪽에 있다.

```java
@Data   // 롬복
class ExamDto {
    String name;
    int age;
}
```

1-17에서 본 `@Data` 하나로 getter·setter·`toString`·`equals`·`hashCode` 가 다 만들어진다. 그래서 멤버변수 둘만 적혀 있는데도 컨트롤러에서 이렇게 쓸 수 있다.

```java
ExamDto dto = new ExamDto();
dto.setName("유재석");   // @Data 가 만들어 준 setter
dto.setAge(10);
return dto;
```

돌아 나갈 때는 반대로 getter가 쓰인다. **JSON의 키를 정하는 것이 필드 이름이 아니라 getter 이름**이라, `getName()` 이 `"name"` 키가 된다. [[Java Spring day02 스프링 부트 실행과 계층 이식]] 에서 getter 이름과 JSON 키가 어긋나던 자리를 따져 본 것과 같은 이야기다.

여기서 오늘 본 것 둘이 한 줄에서 만난다.

```
@Data (컴파일 시점에 생성) ──▶ getter ──▶ @ResponseBody (실행 중에 읽음) ──▶ JSON
```

1-14에서 갈라 둔 두 갈래 — 컴파일 시점에 코드를 만드는 쪽과 실행 중에 표시를 읽는 쪽 — 가 실제로 이어져 하나의 응답을 만든다. 롬복이 만들어 둔 메소드를 스프링이 실행 중에 리플렉션으로 찾아 부르는 것이라, 둘 중 하나만 빠져도 응답이 비어 나간다.

DTO를 컨트롤러와 같은 파일에 둔 것은 실습 규모라서다. 계층을 나눈 [[Java Spring day02 스프링 부트 실행과 계층 이식]] 처럼 실제로는 `Model/Dto` 쪽으로 빼 두는 편이 찾기 쉽다.

정리하면 여기까지의 파일은 **앞에서 뜯어본 것을 다시 조립해 쓰는 자리**다. 애노테이션이 표시일 뿐이고 읽는 쪽이 있어야 동작한다는 것(1-1), 표시를 읽어 객체를 만들고 메소드를 부른다는 것(1-9~1-12), 그 관리가 컨테이너로 넘어간다는 것(1-19~1-22)이 `@Controller` + `@GetMapping` + `@ResponseBody` 세 줄로 압축되어 있다.

### 1-28. @RestController와 @RequestMapping — 공통을 클래스 자리로 올린다

`RestController1` 은 메소드마다 `@ResponseBody` 를 붙이고 주소도 `/day03/...` 을 통째로 적었다. `RestController2` 는 되풀이되던 두 가지를 클래스 자리로 올린다.

```java
// @Component  // 1. 스프링 컨테이너에 객체(빈) 등록
// @Controller // 2. HTTP 서블릿 지원 + @Component 포함
@RestController  // 3. 응답 content-type을 application/json 설정 + @Controller
@RequestMapping("/day03")   // 클래스 내 메소드들의 공통 URL 정의
public class RestController2 {
```

주석으로 남은 두 줄이 계단을 그대로 보여 준다. 아래로 갈수록 위의 것을 품는다.

| 표시 | 얻는 것 | 품고 있는 것 |
| --- | --- | --- |
| `@Component` | 빈 등록 | — |
| `@Controller` | 요청을 받는 자리 | `@Component` |
| `@RestController` | 반환값이 데이터로 나감 | `@Controller` + `@ResponseBody` |

3-2에서 정리한 합성 애노테이션이 세 단계로 겹쳐 있는 모양이다. 그래서 클래스에 `@RestController` 하나만 붙이면 **메소드마다 `@ResponseBody` 를 적지 않아도 된다.**

```java
@GetMapping("/task5")
public String task5() {
    return "서버에서 응답하는 메시지";
}
```

`@ResponseBody` 가 없는데도 문자열이 그대로 응답 본문으로 나간다. 1-25에서 본 "붙이지 않으면 뷰 이름으로 읽힌다"가 여기서는 걸리지 않는 셈이다.

고르는 기준은 2-17에 적어 둔 그대로다. **화면을 돌려줄 일이 있으면 `@Controller`, 전부 데이터면 `@RestController`** 다. 파일의 주석에도 같은 갈림이 적혀 있다 — `HTML(VIEW) → @Controller`, `JSON(값) → @RestController`.

`@RequestMapping("/day03")` 은 2-19에서 미리 적어 둔 그 표기다. 클래스의 값과 메소드의 값이 이어 붙는다.

```
@RequestMapping("/day03")  +  @GetMapping("/task5")  →  /day03/task5
```

`RestController1` 처럼 메소드마다 `/day03/task1` 을 전부 적으면, 주소 체계를 바꿀 때 메소드 수만큼 고쳐야 한다. 공통 부분을 클래스에 올려 두면 **한 자리만 고치면 전부 따라온다.**

`@RequestMapping` 은 메소드 방식을 지정하지 않으면 GET·POST를 가리지 않고 받는다. 클래스에 붙일 때는 방식을 정하지 않고 주소만 묶는 용도로 쓰고, 방식은 메소드 쪽의 `@GetMapping`·`@DeleteMapping` 에서 갈라 준다.

### 1-29. @RequestParam — 요청에 실려 온 값을 매개변수로 받는다

여기서부터 방향이 바뀐다. `RestController1` 이 **내보내는** 쪽만 다뤘다면, 이제 **들어오는** 값을 받는다.

```java
@GetMapping("/task6")
public int task6(@RequestParam String name, @RequestParam int age) {
    System.out.println(name);
    System.out.println(age);
    return 6;
}
```

`/day03/task6?name=유재석&age=10` 으로 요청하면 쿼리스트링의 값이 매개변수에 담긴다.

| 요청 쪽 | 받는 쪽 |
| --- | --- |
| `?name=유재석` | `@RequestParam String name` |
| `?age=10` | `@RequestParam int age` |

이름이 짝을 맞추는 기준이다. 쿼리스트링의 키와 매개변수 이름이 같으면 그대로 이어진다.

눈여겨볼 것은 `age` 의 타입이다. HTTP로 오는 값은 전부 문자열인데 매개변수는 `int` 다. **문자열 `"10"` 을 `int` 10으로 바꾸는 일을 스프링이 대신 해 준다.** [[Java Spring day01 서블릿과 HTTP 메소드]] 에서 `Integer.parseInt(request.getParameter("age"))` 라고 두 겹으로 적던 자리가 매개변수 선언 하나로 줄어든 셈이다.

| | 서블릿 | 스프링 |
| --- | --- | --- |
| 값 꺼내기 | `request.getParameter("age")` | 매개변수로 받는다 |
| 타입 변환 | `Integer.parseInt(...)` 를 직접 | 매개변수 타입에 맞춰 자동 |
| 값이 없을 때 | `null` 이 와서 직접 처리 | 속성으로 정한다(1-30) |

받아 오는 통로가 쿼리스트링만은 아니다. `@RequestParam` 은 **요청의 `Content-Type` 이 폼(`application/x-www-form-urlencoded`)일 때도 같은 방식으로** 값을 잡는다. 주소 뒤에 붙어 오든 본문에 폼으로 실려 오든 받는 쪽 코드가 같다는 뜻이다. [[JS day14 게시판 CRUD]] 에서 `fetch` 로 폼 데이터를 보내던 자리가 이 쪽으로 도착한다.

### 1-30. @RequestParam의 속성 — 이름·필수 여부·기본값

`task7` 은 같은 표시를 세 가지로 다르게 쓴다.

```java
@GetMapping("/task7")
public int task7(String name,                                      // @RequestParam 생략 가능
        @RequestParam(name = "age") int age,                        // 매핑할 매개변수명 지정
        @RequestParam(required = false, defaultValue = "10") int count   // 필수 여부·기본값
) {
```

한 줄씩 갈라 보면 이렇다.

| 표기 | 뜻 |
| --- | --- |
| `String name` | 표시를 생략해도 이름이 같으면 잡힌다 |
| `@RequestParam(name = "age")` | 요청 쪽 이름을 직접 지목한다 |
| `required = false` | 값이 안 와도 된다 |
| `defaultValue = "10"` | 안 왔을 때 채울 값 |

**표시를 생략할 수 있는 이유**는 스프링이 이름을 못 찾으면 매개변수 이름 그대로를 키로 삼기 때문이다. 다만 컴파일 옵션에 따라 매개변수 이름이 `.class` 에 남지 않는 경우가 있어, 이름을 명시해 두는 편이 안전하다. 1-5에서 본 "언제까지 살아 있는가"의 이야기가 여기서도 걸리는 셈이다 — **컴파일 뒤에 남아 있지 않은 정보는 실행 중에 읽을 수 없다.**

`name` 속성은 요청 쪽 이름과 자바 쪽 이름이 어긋날 때 쓴다. 화면에서 보내는 키를 바꾸지 못하는 상황에서 자바 쪽만 읽기 좋은 이름으로 두고 싶을 때가 대표적이다. 2-1에서 본 규칙대로 `@RequestParam("age")` 라고 짧게 적어도 같은 뜻이다.

`defaultValue` 가 숫자가 아니라 `"10"` 이라는 문자열인 점이 눈에 띈다. 애노테이션 속성으로 쓸 수 있는 타입이 제한돼 있어서(1-7) 매개변수 타입마다 다른 타입을 받을 수 없고, **문자열로 받아 두었다가 매개변수 타입에 맞춰 변환한다.** 요청으로 오는 값이 어차피 문자열이니 들어오는 경로도 같아지는 셈이다.

`defaultValue` 를 적으면 값이 없어도 채워지므로 `required = false` 는 사실상 따라온다. 반대로 `required = false` 만 두면 값이 안 왔을 때 `null` 이 들어가는데, 매개변수가 `int` 같은 기본형이면 `null` 을 담을 자리가 없다. 선택 값을 기본형으로 받을 때는 **`defaultValue` 를 함께 두거나 `Integer` 같은 래퍼 타입으로 받는 편이 안전하다.** [[Java day02 타입 변환]] 에서 본 기본형과 참조형의 갈림이 요청 처리에서 드러나는 자리다.

### 1-31. Map으로 한꺼번에 받기

키를 하나씩 나열하지 않고 통째로 받을 수도 있다.

```java
@DeleteMapping("/task8")
public int task8(@RequestParam Map<String, Object> map) {
    System.out.println(map);
    return 8;
}
```

요청에 실려 온 파라미터가 전부 맵에 담긴다. `?name=유재석&age=10` 이면 `{name=유재석, age=10}` 이 된다.

1-26에서 `Map` 을 **돌려주어** JSON으로 내보냈는데, 여기서는 같은 `Map` 으로 **받는다.** 방향만 반대일 뿐 `{ key : value }` 구조가 오가는 형식과 잘 맞아떨어진다는 점은 같다.

| | `Map` 을 쓰는 자리 | 성격 |
| --- | --- | --- |
| 내보낼 때(1-26) | 반환 타입 | 키가 그대로 JSON 키가 된다 |
| 받을 때(1-31) | 매개변수 | 요청 파라미터가 그대로 키가 된다 |

받을 때의 `Map` 은 **어떤 키가 올지 미리 정해 두지 않아도 되는** 대신 잃는 것이 있다.

- 값이 전부 문자열로 들어온다. `Object` 로 열어 두었을 뿐 `int` 로 변환되지 않으므로 꺼내 쓸 때 직접 바꿔야 한다
- 어떤 키가 필요한지가 코드에 드러나지 않는다. 메소드 서명만 봐서는 무엇을 받는지 알 수 없다
- 오타가 걸러지지 않는다. 잘못된 키가 와도 그냥 담긴다

그래서 받는 값의 모양이 정해져 있으면 다음에 볼 DTO 쪽이 다루기 쉽고, **키가 상황마다 달라지는 자리**(검색 조건을 자유롭게 받는 경우 등)에 `Map` 이 어울린다. 2-18에서 내보내는 쪽을 두고 정리한 것과 같은 갈림이다.

### 1-32. @ModelAttribute — 값을 DTO에 담아 받는다

매개변수를 나열하는 대신 객체 하나로 받는 방식이다.

```java
@DeleteMapping("/task9")
public int task9(@ModelAttribute ExamDto examDto) {
    System.out.println(examDto);
    return 9;
}
```

`ExamDto` 는 `RestController1` 에 있던 그 DTO다(1-27).

```java
@Data
class ExamDto {
    String name;
    int age;
}
```

`?name=유재석&age=10` 로 요청하면 `examDto` 에 값이 채워져 들어온다. 스프링이 하는 일은 이렇다.

```
① 기본 생성자로 ExamDto 객체를 만든다        ← newInstance
② 요청 파라미터 이름과 같은 필드를 찾는다
③ setter 를 불러 값을 넣는다                  ← invoke
```

1-11에서 리플렉션으로 해 본 것이 그대로 돌아간다. **오늘 오전에 손으로 짜 본 세 줄이 요청 처리에서 다시 나오는 자리**다.

여기서 `@Data` 가 왜 필요한지도 이어진다. 값을 넣는 통로가 setter라 `@Setter`(또는 이를 품은 `@Data`)가 있어야 하고, 객체를 만드는 통로가 기본 생성자라 그것도 있어야 한다. 1-15에서 "프레임워크가 객체를 만드는 통로는 매개변수 없는 생성자"라고 정리한 것이 세 번째로 걸리는 셈이다.

`System.out.println(examDto)` 가 값을 보여 주는 것은 `@Data` 안의 `@ToString` 덕이다(1-16). 재정의가 없으면 `클래스명@해시값` 만 찍혀 값이 들어왔는지 확인할 수 없다.

받는 세 방식을 나란히 놓으면 갈림이 분명하다.

| | `@RequestParam` | `@RequestParam Map` | `@ModelAttribute` |
| --- | --- | --- | --- |
| 받는 모양 | 값 하나씩 | 통째로 맵에 | DTO 객체에 |
| 어떤 값이 오는지 | 메소드 서명에 드러난다 | 드러나지 않는다 | DTO에 드러난다 |
| 타입 변환 | 매개변수 타입대로 | 안 된다(문자열) | 필드 타입대로 |
| 값이 늘어나면 | 매개변수를 계속 늘린다 | 그대로 | DTO에 필드만 추가 |
| 어울리는 자리 | 값이 두셋 | 키가 정해지지 않은 경우 | 값이 여럿이고 모양이 고정 |

1-18에서 빌더를 두고 본 이야기와 결이 같다. **값이 몇 개 안 되면 나열하는 쪽이 짧고, 많아지면 이름 붙은 묶음으로 받는 쪽이 읽기 좋다.**

`@ModelAttribute` 도 생략할 수 있다. 매개변수가 기본형·`String` 이 아닌 객체 타입이면 스프링이 이 방식으로 처리한다. 다만 생략하면 `@RequestBody` 로 받는 경우와 코드 모양이 같아져 구분이 흐려지므로, 적어 두는 편이 읽기에 낫다(2-22).

### 1-33. @DeleteMapping — 주소는 같고 방식으로 갈린다

`task8`·`task9` 에는 `@GetMapping` 대신 `@DeleteMapping` 이 붙었다.

```java
@DeleteMapping("/task8")
@DeleteMapping("/task9")
```

[[Java Spring day01 서블릿과 HTTP 메소드]] 에서 본 네 가지 방식이 각자의 짧은 표시를 갖는다.

| 표시 | 방식 | 뜻하는 일 |
| --- | --- | --- |
| `@GetMapping` | GET | 조회 |
| `@PostMapping` | POST | 등록 |
| `@PutMapping` | PUT | 수정 |
| `@DeleteMapping` | DELETE | 삭제 |

전부 `@RequestMapping(method = ...)` 을 줄인 합성 애노테이션이다(3-2). 주소가 같아도 방식이 다르면 다른 메소드로 이어지므로, `/day03/board` 하나에 조회·등록·수정·삭제를 전부 매달 수 있다. [[JS day14 게시판 CRUD]] 에서 `fetch` 의 `method` 를 바꿔 가며 부르던 그 쪽과 짝을 이루는 자리다.

DELETE 요청에 값을 실을 때는 대체로 **본문이 아니라 쿼리스트링**을 쓴다. `@RequestParam`·`@ModelAttribute` 둘 다 쿼리스트링에서 값을 잡으므로 여기서 `@DeleteMapping` 과 함께 쓰는 데 문제가 없다(2-23).

정리하면 `RestController2` 는 오늘 본 것의 마지막 조각이다. 나가는 쪽(1-24~1-27)에 이어 **들어오는 쪽**을 채웠고, 값을 받는 세 통로가 전부 1-9~1-12의 리플렉션 위에서 돌아간다. 표시를 읽고(`getAnnotation`), 객체를 만들고(`newInstance`), 메소드를 부르는(`invoke`) 구조가 응답뿐 아니라 **요청의 값을 매개변수에 담는 자리에서도 같은 모양으로 반복된다**(3-9).

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

롬복도 같은 이야기 위에 있다. 애노테이션을 아무리 붙여도 `annotationProcessor` 등록이 빠져 있으면 읽는 쪽이 없는 것이라 메소드가 생기지 않는다. IDE에서 `getName()` 을 못 찾겠다고 나오는 상황이 대체로 이 자리다.

### 2-11. 롬복이 만든 코드를 확인하는 방법

생성된 코드가 소스에 보이지 않는 것이 롬복의 불편한 점이다. 확인할 수 있는 통로는 몇 가지가 있다.

- 빌드 결과의 `.class` 를 디컴파일해 보면 생성된 메소드가 그대로 보인다
- IDE의 구조 보기(Outline)에는 생성된 메소드가 함께 잡힌다
- 리플렉션으로 훑어도 보인다 — `exam1` 에서 쓴 `getDeclaredMethods()` 로 확인할 수 있다

```java
for (Method m : Student.class.getDeclaredMethods()) {
    System.out.println(m.getName());
}
```

컴파일 시점에 만들어진 코드도 결국 평범한 메소드라, 실행 중에 리플렉션으로 보면 손으로 적은 것과 구별되지 않는다. 두 갈래가 결국 같은 `.class` 파일에서 만난다는 것이 여기서 드러난다.

### 2-12. 롬복 애노테이션을 고르는 기준

전부 붙이는 것보다 필요한 것만 고르는 편이 낫다. 대체로 이런 갈림이다.

| 상황 | 붙일 것 |
| --- | --- |
| 값을 담고 옮기기만 하는 DTO | `@Getter` + `@Setter` + `@NoArgsConstructor` + `@AllArgsConstructor` |
| 값이 바뀌지 않아야 하는 객체 | `@Getter` + `@AllArgsConstructor` (setter를 두지 않는다) |
| 스프링 빈에 의존성 주입 | 멤버를 `final` 로 두고 `@RequiredArgsConstructor` |
| 값 비교가 필요한 객체 | `@EqualsAndHashCode` 를 빠뜨리지 않기 |

`@Setter` 를 습관적으로 붙이면 아무 데서나 값을 바꿀 수 있게 된다. 바뀌면 안 되는 값에는 setter를 두지 않는 편이 안전하다. 캡슐화의 목적이 "메소드로 감싸는 것" 자체가 아니라 **바뀔 수 있는 경로를 정해 두는 것**이라는 점이 여기서 이어진다.

### 2-13. 순환 참조와 toString

`@ToString` 과 `@EqualsAndHashCode` 는 기본적으로 **모든 멤버변수**를 훑는다. 서로를 참조하는 객체 둘이 있으면 `toString()` 이 서로를 부르며 끝나지 않는 문제가 생길 수 있다.

특정 필드를 빼려면 이렇게 적는다.

```java
@ToString(exclude = "비밀번호")
@EqualsAndHashCode(of = { "학번" })
```

| 속성 | 뜻 |
| --- | --- |
| `exclude` | 이 필드는 제외한다 |
| `of` | 이 필드들만 포함한다 |

로그에 남으면 곤란한 값(비밀번호 등)을 `@ToString` 에서 빼 두는 것도 같은 통로다. 로그가 남는 자리에 무엇이 찍히는지는 한 번 확인해 두는 편이 안전하다.

`callSuper` 속성으로 부모 클래스의 필드까지 볼지도 정할 수 있다. 상속이 걸린 클래스에서 값 비교가 어긋나면 대개 이 자리다.

### 2-14. 빌더를 쓰는 자리와 걸리는 것들

빌더가 늘 나은 것은 아니다. 대체로 이런 갈림이다.

| 상황 | 어울리는 쪽 |
| --- | --- |
| 멤버가 두셋뿐이고 다 필수 | 생성자 |
| 멤버가 많고, 타입이 겹친다 | 빌더 |
| 넣는 값의 조합이 상황마다 다르다 | 빌더 |
| 값이 하나도 빠지면 안 된다 | 생성자(빠뜨리면 컴파일이 막는다) |

마지막 줄이 빌더의 약점이다. **빌더는 값을 빠뜨려도 컴파일이 막아 주지 않는다.** 생성자는 인자를 안 넣으면 컴파일 오류가 나지만, 빌더는 `build()` 를 그냥 부를 수 있고 빠진 값은 기본값이 된다. 반드시 있어야 하는 값이라면 `build()` 이후에 확인하는 절차를 따로 두는 편이 안전하다.

기본값을 `0`·`null` 이 아닌 다른 값으로 두고 싶으면 필드에 표시를 붙인다.

```java
@Builder.Default
private int math = 50;
```

`@Builder` 를 붙이면 내부적으로 전체 생성자가 쓰이기 때문에, `@NoArgsConstructor` 만 함께 붙이면 기본 생성자가 필요한 자리와 어긋날 수 있다. 이 파일처럼 **`@NoArgsConstructor` 와 `@AllArgsConstructor` 를 둘 다 붙여 두면** 프레임워크가 쓰는 기본 생성자와 빌더가 쓰는 전체 생성자가 모두 남는다. 1-15에서 본 "생성자를 직접 정의하면 기본 생성자가 사라진다"는 규칙이 롬복 조합에서도 그대로 걸리는 자리다.

### 2-15. 싱글톤을 손으로 만들 때 갈리는 방식

`exam3` 의 방식은 필드를 선언하면서 바로 객체를 만든다. 클래스가 메모리에 올라올 때 함께 만들어지므로 **이른 초기화(eager)** 라고 부른다.

| 방식 | 만들어지는 시점 | 성격 |
| --- | --- | --- |
| 이른 초기화 | 클래스가 로딩될 때 | 간단하고 안전하다. 안 쓰여도 만들어진다 |
| 늦은 초기화 | `getInstance()` 가 처음 불릴 때 | 필요할 때만 만든다. 여러 스레드가 동시에 부르면 어긋날 수 있다 |
| 홀더 방식 | 내부 클래스가 처음 쓰일 때 | 늦게 만들면서 스레드 문제도 피한다 |
| `enum` 방식 | 상수가 초기화될 때 | 가장 짧다. 상속이 안 된다 |

늦은 초기화에서 `if (instance == null)` 검사와 객체 생성 사이에 다른 스레드가 끼어들면 객체가 둘 만들어질 수 있다. [[Java day16 스레드 동기화]] 에서 본 그 문제가 그대로 재현되는 자리다. 이른 초기화가 그 틈 자체를 없애는 방식이라, 특별한 이유가 없으면 이쪽이 안전하다.

다만 스프링을 쓰는 코드에서 이 세 줄을 직접 적을 일은 거의 없다. **컨테이너가 이미 같은 일을 해 주기 때문**이다. 알아 둘 값어치는 스프링 빈이 왜 기본적으로 하나인지, 그래서 왜 빈에 상태를 두면 곤란한지(2-16)를 이해하는 데 있다.

### 2-16. 하나뿐인 객체에 값을 담아 두면 곤란하다

빈이 하나만 만들어져 공유된다는 말은, **여러 요청이 같은 객체를 함께 쓴다**는 뜻이다. 그래서 빈 안에 값을 담아 두면 요청끼리 서로의 값을 덮어쓸 수 있다.

```java
@Component
class SampleDao4 {
    private String 마지막조회자;   // 요청마다 덮어써진다
}
```

메소드 안에서 선언한 지역변수는 호출마다 따로 만들어지므로 문제가 없다. 값을 오래 들고 있어야 하면 빈의 멤버변수가 아니라 매개변수·반환값·데이터베이스 쪽으로 넘기는 편이 안전하다. [[Java day16 스레드 동기화]] 에서 본 공유 자원 이야기가 스프링에서 다시 나오는 자리다.

정리하면 **빈은 기능을 담는 자리이지 데이터를 담는 자리가 아니다.** DAO·서비스·컨트롤러에 멤버변수를 둘 때는 "이게 요청마다 달라져야 하는 값인가"를 먼저 따져 보는 편이 낫다.

### 2-17. @RestController와 @Controller + @ResponseBody 중 무엇을 쓸까

같은 결과를 두 가지로 적을 수 있으니 기준을 정해 두는 편이 낫다.

| 상황 | 어울리는 쪽 |
| --- | --- |
| 클래스의 메소드가 전부 데이터를 내보낸다 | `@RestController` — 한 번만 적으면 된다 |
| 데이터와 화면을 한 클래스에 섞어 둔다 | `@Controller` + 필요한 메소드에만 `@ResponseBody` |
| 표시가 무엇을 하는지 코드에 드러내고 싶다 | `@Controller` + `@ResponseBody` |

`@RestController = @Controller + @ResponseBody` 이므로(3-2) 실제 동작은 갈리지 않는다. 다만 메소드마다 붙이면 **어떤 메소드가 데이터를 내보내는지가 눈에 보인다**는 이점이 있고, 화면을 돌려주는 메소드를 나중에 섞어 둘 여지도 남는다.

### 2-18. Map으로 내보낼 때 순서는 정해지지 않는다

`HashMap` 은 넣은 순서를 지키지 않는다. JSON으로 나갈 때 키 순서가 코드에 적은 순서와 달라질 수 있다는 뜻이다.

| 구현 | 순서 |
| --- | --- |
| `HashMap` | 보장하지 않는다 |
| `LinkedHashMap` | 넣은 순서 그대로 |
| `TreeMap` | 키를 정렬한 순서 |

[[Java day15 Map과 HashMap]] 에서 본 갈림이 응답에서 드러나는 자리다. 순서가 눈에 띄어야 하는 응답이라면 `LinkedHashMap` 을 쓰거나, 애초에 DTO로 모양을 고정해 두는 편이 안전하다.

키를 사람 이름처럼 **값에 가까운 것**으로 두면 화면 쪽에서 키를 미리 알 수 없다는 문제도 따라온다. 오가는 모양이 정해져 있어야 하는 응답은 `{"name": ..., "score": ...}` 처럼 **키를 고정하고 값을 채우는** 쪽이 다루기 쉽다.

### 2-19. 주소의 앞부분을 클래스로 묶기 — @RequestMapping

`RestController2` 에서 실제로 쓴 방식이다(1-28). `RestController1` 처럼 메소드마다 `/day03/...` 을 되풀이해 적는 대신, 공통 부분을 클래스에 올릴 수 있다.

```java
@Controller
@RequestMapping("/day03")
public class RestController1 {

    @GetMapping("/task1")   // 실제 주소는 /day03/task1
    @ResponseBody
    public int task1() { ... }
}
```

클래스의 값과 메소드의 값이 이어 붙는다. 주소 체계를 한 자리에서 바꿀 수 있어서, 컨트롤러가 커질수록 값어치가 커진다.

`@RequestMapping` 은 메소드 방식을 지정하지 않으면 전부 받는다. 방식을 갈라 두는 짧은 표기가 `@GetMapping`·`@PostMapping`·`@PutMapping`·`@DeleteMapping` 이고, 전부 `@RequestMapping(method = ...)` 을 줄인 합성 애노테이션이다(3-2).

### 2-20. 요청에서 값 받기 — @RequestParam

1-29~1-30에서 실제로 써 본 표시다. 주소에 실려 오는 값을 받을 때는 매개변수에 표시를 붙인다.

```java
@GetMapping("/day03/task5")
@ResponseBody
public String task5(@RequestParam String name) {
    return name + "님 안녕하세요";
}
```

`/day03/task5?name=유재석` 로 요청하면 `name` 에 값이 담긴다. 몇 가지를 더 정할 수 있다.

| 표기 | 뜻 |
| --- | --- |
| `@RequestParam("이름")` | 요청 쪽 이름과 매개변수 이름이 다를 때 짝지어 준다 |
| `@RequestParam(required = false)` | 값이 없어도 된다 (없으면 `null`) |
| `@RequestParam(defaultValue = "0")` | 값이 없을 때 채울 기본값 |

[[Java Spring day01 서블릿과 HTTP 메소드]] 에서 `request.getParameter("name")` 으로 꺼내던 자리를 표시 하나가 대신한다. 문자열로 꺼내 형변환하던 과정도 매개변수 타입에 맞춰 스프링이 처리한다.

값이 여럿이면 하나씩 나열하는 대신 DTO로 받을 수도 있다. 이때 스프링이 기본 생성자로 객체를 만들고 setter로 값을 채우는데, 1-11에서 본 `newInstance()` 가 실제로 쓰이는 자리이자 DTO에 기본 생성자를 남겨 두는 이유다. 1-32에서 `@ModelAttribute` 로 확인한 그대로다.

### 2-21. 주소 자체에 값을 싣기 — @PathVariable

값을 쿼리스트링이 아니라 **주소의 일부**로 받는 통로가 하나 더 있다.

```java
@GetMapping("/board/{no}")
public int detail(@PathVariable int no) {
    return no;
}
```

`/day03/board/10` 으로 요청하면 `no` 에 `10` 이 담긴다. 중괄호로 감싼 자리가 변수가 되고, 이름이 같은 매개변수에 이어진다.

| | `@RequestParam` | `@PathVariable` |
| --- | --- | --- |
| 값이 실리는 곳 | `?no=10` | `/board/10` |
| 뜻하는 것 | 조건·옵션 | **무엇을 가리키는가(식별자)** |
| 값이 없을 수 있나 | `required = false` 로 가능 | 주소가 달라지므로 사실상 필수 |

기준을 잡자면 **자원을 가리키는 값은 주소에, 걸러 내는 조건은 쿼리스트링에** 둔다. `/board/10` 은 10번 글 하나를 가리키고, `/board?page=2&size=10` 은 목록을 어떻게 잘라 볼지를 정하는 식이다.

이름이 다르면 지목해 준다.

```java
@GetMapping("/board/{boardNo}")
public int detail(@PathVariable("boardNo") int no) { ... }
```

### 2-22. @ModelAttribute와 @RequestBody — 어디에 실려 오느냐로 갈린다

DTO로 받는 표기가 둘이라 헷갈리기 쉽다. 갈림은 **값이 요청의 어디에 실려 오는가**다.

| | `@ModelAttribute` | `@RequestBody` |
| --- | --- | --- |
| 읽는 곳 | 쿼리스트링·폼 데이터 | 요청 **본문의 JSON** |
| `Content-Type` | `x-www-form-urlencoded` 등 | `application/json` |
| 값을 채우는 통로 | 기본 생성자 + setter | 기본 생성자 + setter(Jackson) |
| 어울리는 요청 | 폼 전송, GET·DELETE | `fetch` 로 JSON을 보낼 때 |

받는 쪽 코드 모양은 거의 같은데 동작하는 조건이 다르다. **JSON을 보냈는데 `@ModelAttribute` 로 받으면 값이 비어 들어오고**, 반대도 마찬가지다. DTO에 값이 안 채워질 때 먼저 볼 자리가 여기다.

[[JS day14 게시판 CRUD]] 에서 `fetch` 의 `headers` 에 `Content-Type` 을 적고 `body` 에 `JSON.stringify(...)` 를 실었는데, 그렇게 보낸 요청은 `@RequestBody` 쪽으로 도착한다. 보내는 쪽에서 정한 형식이 받는 쪽 표시를 정하는 셈이다.

3-8에서 본 메시지 컨버터가 들어오는 방향으로도 도는 자리다. 나갈 때 자바 객체를 JSON으로 바꾸던 Jackson이, 들어올 때는 JSON을 자바 객체로 되돌린다.

### 2-23. DELETE 요청에 값을 어떻게 실을까

`@DeleteMapping` 에 값을 넘기는 방식은 GET과 거의 같다.

- 쿼리스트링에 실어 `@RequestParam`·`@ModelAttribute` 로 받는 쪽이 무난하다
- DELETE에 본문을 싣는 것은 규격상 금지되지는 않지만 **중간 장비나 클라이언트가 본문을 버릴 수 있어** 기대대로 도착하지 않을 때가 있다
- 지울 대상 하나를 가리키는 요청이면 `/board/10` 처럼 주소에 두고 `@PathVariable` 로 받는 쪽이 뜻이 분명하다

정리하면 **DELETE는 "무엇을 지울지"만 알면 되는 요청**이라 값이 많이 필요하지 않고, 그래서 주소나 쿼리스트링으로 충분한 경우가 대부분이다.

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

DTO마다 getter·setter를 손으로 적던 [[Java day08 접근제한자와 static]] 의 되풀이를 줄이는 방향이기도 하다. 이 갈래는 1-13~1-17에서 실제로 써 봤다.

애노테이션 프로세서를 쓰는 라이브러리는 롬복 말고도 몇 가지가 더 있다. 성격을 알아 두면 빌드 설정에서 `annotationProcessor` 줄이 왜 필요한지가 같은 이야기로 읽힌다.

| 라이브러리 | 컴파일 시점에 만드는 것 |
| --- | --- |
| Lombok | 생성자·getter·setter·`toString`·`equals` |
| MapStruct | 객체 A ↔ 객체 B 변환 코드(DTO ↔ 엔티티) |
| Querydsl | 타입이 검사되는 쿼리용 Q클래스 |

### 3-5. 생성자 주입과 @RequiredArgsConstructor

스프링에서 롬복이 가장 자주 쓰이는 자리는 DTO보다 오히려 **의존성 주입** 쪽이다.

```java
@RestController
@RequiredArgsConstructor
public class BoardController {
    private final BoardDao boardDao;   // final 멤버
}
```

`final` 멤버를 받는 생성자가 컴파일 시점에 만들어지고, 스프링은 그 생성자를 통해 필요한 객체를 넣어 준다. 생성자가 하나뿐이면 `@Autowired` 를 붙이지 않아도 주입된다.

- 필드 주입(`@Autowired` 를 멤버변수에 직접)보다 **생성자 주입이 권장되는 방식**이다
- `final` 이라 만들어진 뒤 바뀌지 않고, 필요한 것이 없으면 객체 생성 자체가 실패해 문제가 일찍 드러난다

[[Java Spring day02 스프링 부트 실행과 계층 이식]] 에서 컨트롤러가 DAO를 직접 `new` 로 만들던 자리가 이 구조로 바뀐다. 컨트롤러는 "필요하다"고 선언만 하고, 만들어 넣는 일은 컨테이너가 맡는 갈림이다.

### 3-6. 리플렉션의 비용과 쓰는 자리

리플렉션은 편한 만큼 대가가 있다.

- **느리다.** 이름으로 찾고 접근 검사를 우회하는 과정이 일반 호출보다 무겁다
- **컴파일러가 검사해 주지 못한다.** 메소드 이름을 문자열로 적으므로 오타가 실행 중에야 드러난다
- **리팩터링에 취약하다.** 이름을 바꿔도 문자열은 따라가지 않는다

그래서 요청이 올 때마다 반복해서 리플렉션을 돌리지 않고, **시작할 때 한 번 읽어 표로 만들어 두는** 방식을 쓴다. 스프링이 서버 기동 시점에 주소 표를 만들어 두는 것이 그 이유다.

일반 업무 코드에서 리플렉션을 직접 쓸 일은 드물다. 다만 **쓰는 라이브러리가 그것으로 돌아간다**는 것을 알아 두면, 기본 생성자가 왜 필요한지·`private` 필드에 값이 어떻게 들어가는지 같은 것이 설명된다.

### 3-7. 컨테이너가 관리하는 객체의 범위와 수명

`@Component` 로 맡긴 뒤에는 "몇 개를 만들지"와 "언제까지 살릴지"도 컨테이너가 정한다. 그 설정이 **스코프**다.

| 스코프 | 만들어지는 수 |
| --- | --- |
| `singleton` | 컨테이너에 하나 (기본값) |
| `prototype` | 꺼낼 때마다 새로 |
| `request` | HTTP 요청 하나마다 |
| `session` | 사용자 세션마다 |

기본값이 `singleton` 이라 따로 적지 않으면 1-20에서 손으로 만든 것과 같은 결과가 된다. 상태를 들고 있어야 하는 객체는 `prototype` 쪽을 고르지만, 그런 객체는 애초에 빈으로 두지 않는 경우가 더 많다.

객체를 담아 두는 컨테이너 자체는 `ApplicationContext` 라는 이름으로 존재한다. 빈 목록을 들고 있다가 필요한 곳에 넣어 주는 자리라, 여기서 빈을 직접 꺼내 볼 수도 있다.

만들어진 뒤·없어지기 전에 할 일이 있으면 표시를 붙여 둔다.

| 애노테이션 | 불리는 때 |
| --- | --- |
| `@PostConstruct` | 객체가 만들어지고 주입이 끝난 직후 |
| `@PreDestroy` | 컨테이너가 내려가기 직전 |

생성자에서 하기 어려운 초기화(주입된 값을 써야 하는 준비 작업)를 두는 자리다. **생성자가 불릴 때는 아직 주입이 끝나지 않았을 수 있다**는 점이 이 둘이 따로 있는 이유다.

같은 타입의 빈이 둘 이상이면 어느 것을 넣어야 할지 정해지지 않는다. 그때 갈라 주는 표시가 있다.

| 애노테이션 | 하는 일 |
| --- | --- |
| `@Primary` | 여럿 중 기본으로 쓸 것을 정한다 |
| `@Qualifier("이름")` | 받는 쪽에서 이름으로 지목한다 |

이 갈림이 성립하는 것 자체가 [[Java day11 인터페이스]] 에서 본 다형성 위에서다. 받는 쪽이 인터페이스 타입으로만 선언해 두면 **구현을 바꿔 끼우는 일이 설정 문제로 줄어든다** — 테스트할 때 가짜 구현을 넣는 것도 같은 통로다.

### 3-8. 메시지 컨버터 — 반환값이 본문이 되는 실제 자리

`@ResponseBody` 가 붙은 메소드의 반환값을 실제로 바꾸는 것은 **메시지 컨버터(`HttpMessageConverter`)** 다. 스프링이 반환 타입과 요청의 `Accept` 헤더를 보고 맞는 컨버터를 골라 변환을 맡긴다.

| 반환 타입 | 고르는 컨버터 |
| --- | --- |
| `String` | `StringHttpMessageConverter` |
| 객체·`Map`·컬렉션 | `MappingJackson2HttpMessageConverter` (Jackson) |

1-26에서 문자열만 평문으로 나가고 나머지는 JSON이 되던 갈림이 여기서 정해진다. 자바 객체를 JSON 문자열로 바꾸는 일(직렬화)은 Jackson이라는 라이브러리가 맡고, 스프링 부트의 web 의존성에 이미 들어 있어 따로 추가하지 않아도 된다.

Jackson이 값을 꺼낼 때 쓰는 것이 getter이므로, JSON 키를 바꾸고 싶으면 getter 쪽을 건드리거나 표시를 붙인다.

| 애노테이션 | 하는 일 |
| --- | --- |
| `@JsonProperty("이름")` | 이 필드를 다른 키 이름으로 내보낸다 |
| `@JsonIgnore` | 이 필드는 JSON에 넣지 않는다 |
| `@JsonInclude(NON_NULL)` | `null` 인 필드는 빼고 내보낸다 |

비밀번호처럼 나가면 곤란한 값을 `@JsonIgnore` 로 빼 두는 것은 2-13에서 `@ToString(exclude = ...)` 로 로그에서 빼던 것과 같은 발상이다. **나가는 자리마다 무엇이 실리는지 한 번씩 확인해 두는 편이 안전하다.**

들어오는 쪽도 같은 장치가 반대로 돈다. `@RequestBody` 가 붙으면 요청 본문의 JSON을 자바 객체로 되돌리는데(역직렬화), 이때 기본 생성자와 setter가 쓰인다.

### 3-9. 요청 값이 매개변수에 담기는 실제 자리 — ArgumentResolver

`@ResponseBody` 의 반환값을 바꾸는 것이 메시지 컨버터였다면(3-8), 들어오는 쪽에는 **`HandlerMethodArgumentResolver`** 가 있다. 메소드를 부르기 직전에 매개변수를 하나씩 훑어 값을 만들어 채우는 자리다.

```
① 주소 표에서 부를 메소드를 찾는다
② 그 메소드의 매개변수를 하나씩 본다              ← getParameters
③ 매개변수에 붙은 표시를 읽어 담당자를 고른다      ← getAnnotation
④ 담당자가 요청에서 값을 꺼내 만든다
⑤ 만들어진 값들을 인자로 메소드를 부른다          ← invoke(대상, 값1, 값2)
```

1-11에서 `method.invoke(대상, 값1, 값2)` 처럼 매개변수를 뒤에 이어 붙일 수 있다고 본 그 자리가 여기서 쓰인다. **매개변수 값을 미리 만들어 두고 마지막에 한 번에 넘기는** 구조라, 표시별로 담당자만 갈아 끼우면 받는 방식이 늘어난다.

| 매개변수 표시 | 담당자가 하는 일 |
| --- | --- |
| `@RequestParam` | 쿼리스트링·폼에서 이름으로 값을 꺼낸다 |
| `@PathVariable` | 주소 패턴에서 잘라 낸 값을 꺼낸다 |
| `@ModelAttribute` | 객체를 만들고 setter로 채운다 |
| `@RequestBody` | 메시지 컨버터에게 본문 변환을 맡긴다 |
| 표시 없는 `HttpServletRequest` 등 | 서블릿 객체를 그대로 넘긴다 |

컨트롤러 메소드의 매개변수 자리에 아무 타입이나 적어도 웬만하면 값이 채워져 들어오는 이유가 이것이다. **담당자 목록에 있는 타입·표시면 처리된다.** 직접 만들어 등록할 수도 있어서, 로그인한 사용자를 매개변수로 바로 받는 식의 처리를 한 자리로 모으는 데 쓴다.

값을 채우다 실패하면(숫자 자리에 글자가 오는 등) 메소드를 부르기 전에 예외가 난다. 요청 값 검증(`@Valid`)이 이 단계에 붙는 것도 같은 이유다 — **메소드 본문이 시작될 때는 이미 값이 갖춰져 있다**는 전제를 지키기 위해서다.

### 3-10. 다음에 볼 키워드

- `@Component`·`@Service`·`@Repository` — 계층별 컴포넌트 표시와 스캔
- `@Autowired`·생성자 주입 — 컨테이너가 객체를 넣어 주는 통로
- `@Configuration`·`@Bean` — 직접 등록하는 방식
- `@Valid`·`@NotNull` — 검증도 애노테이션으로
- `@Transactional` 과 프록시 기반 AOP
- `ApplicationContext` 와 빈 생명주기(`@PostConstruct`·`@PreDestroy`)
- `HandlerMapping`·`HandlerAdapter` — 주소 표를 만들고 메소드를 부르는 실제 자리
- Lombok과 애노테이션 프로세서
- `@Builder` — 값이 많은 객체를 이름 붙여 조립하기
- `@Slf4j` — 로거를 애노테이션으로 만들어 두기
- `record` — 값 객체를 자바 문법 자체로 짧게 쓰는 방향
- MapStruct·Querydsl — 코드 생성 계열 라이브러리
- `MethodHandle` — 리플렉션보다 빠른 대안
- `@Scope`·`ApplicationContext` — 빈의 개수와 수명을 정하는 자리
- `@Primary`·`@Qualifier` — 같은 타입 빈이 여럿일 때 고르기
- `@Builder.Default`·`@Value` — 빌더의 기본값과 불변 객체
- `@RequestMapping`·`@PostMapping` — 주소를 클래스로 묶고 메소드 방식 나누기
- `@RequestParam`·`@PathVariable`·`@RequestBody` — 요청에서 값을 받는 세 통로
- `HttpMessageConverter`·Jackson — 반환값이 JSON이 되는 자리
- `@JsonProperty`·`@JsonIgnore` — JSON 키와 내보낼 필드 고르기
- `ResponseEntity` — 상태코드·헤더까지 함께 돌려주기
- `@ModelAttribute` — 폼·쿼리스트링 값을 DTO에 담아 받기
- `HandlerMethodArgumentResolver` — 매개변수에 값이 채워지는 실제 자리
- `@Valid`·`BindingResult` — 받은 값이 규칙에 맞는지 검사하기
- `WebDataBinder`·`Converter` — 문자열을 원하는 타입으로 바꾸는 규칙 직접 정하기
- `-parameters` 컴파일 옵션 — 매개변수 이름을 `.class` 에 남겨 두기
- `@RestControllerAdvice`·`@ExceptionHandler` — 값 변환 실패 같은 예외를 한 자리에서 처리하기

## 실습 파일

- `2026B_Spring/springweb/src/main/java/day03/exam/exam1.java` (애노테이션이 주석과 갈리는 지점과 기계가 읽는 표시라는 성격, `@Override` 로 재정의를 컴파일러에게 검사시키기와 재정의된 메소드가 불리는 확인·`super` 로 부모 메소드 부르기, `@Deprecated` 로 사용 권장하지 않음을 알리기와 실행은 되지만 경고가 나는 자리, `@interface` 로 애노테이션 직접 정의하기, 메타 애노테이션 `@Retention` 과 `RetentionPolicy` 세 단계(`SOURCE`·`CLASS`·`RUNTIME`)·실행 중에 읽으려면 `RUNTIME` 이어야 하는 이유, `@Target` 과 `ElementType` 으로 붙일 자리 제한하기·여러 자리를 배열로 적기, 애노테이션 속성이 추상메소드 모양인 이유와 `default` 유무로 갈리는 필수·선택, 속성으로 쓸 수 있는 타입의 제한, 정의한 애노테이션을 메소드에 달고 속성 생략 시 기본값이 채워지는 자리, `java.lang.annotation` 과 `java.lang.reflect` 로 갈리는 두 축, `클래스.class` 리터럴로 `Class` 얻기와 `getClass()`·`Class.forName()` 과의 갈림·제네릭 `Class<T>` 로 타입 남기기, `getMethod(이름)` 으로 `Method` 꺼내기, `getAnnotation(애노테이션.class)` 로 표시 읽기와 `null` 이 나올 수 있는 자리, 속성 이름 그대로 메소드처럼 값 읽기, `getDeclaredConstructor().newInstance()` 로 `new` 없이 객체 만들기와 기본 생성자가 필요한 이유, `method.invoke(대상)` 으로 이름을 코드에 박지 않고 메소드 실행하기·`static` 이면 `null`·매개변수를 뒤에 잇기, 리플렉션 계열 호출이 검사 예외를 던지는 자리, 정의→주입→읽기 세 단계가 스프링의 컴포넌트 스캔·주소 매핑과 같은 구조라는 정리)
- `2026B_Spring/springweb/src/main/java/day03/exam/exam2.java` (롬복으로 남이 만든 애노테이션을 가져다 쓰기, 컴파일 시점에 읽는 애노테이션 프로세서 갈래와 리플렉션 갈래의 갈림, `@NoArgsConstructor`·`@AllArgsConstructor`·`@RequiredArgsConstructor` 로 생성자 만들기와 전체 생성자를 두면 기본 생성자가 사라지는 자리, `@Getter`·`@Setter` 로 캡슐화 메소드 자동 생성·멤버변수 하나에만 붙이기, `@ToString` 이 `toString()` 재정의와 이어지는 자리, `@Data` 가 묶음 애노테이션이라는 점과 그 구성, `@EqualsAndHashCode` 로 값 기준 비교 만들기와 `equals`·`hashCode` 를 짝으로 두어야 하는 이유, 소스에 안 보이는 생성 코드를 확인하는 통로, `@Builder` 로 빌더 패턴 지원하기와 생성자와 갈리는 지점(순서 무관·선택적 대입·값에 이름이 남는 것)·`builder()` 가 `static` 인 이유·메소드 체이닝과 `build()` 에서 객체가 만들어지는 자리·생략한 값이 기본값이 되는 점과 빠뜨려도 컴파일이 막지 않는 약점·`@Builder.Default`)
- `2026B_Spring/springweb/src/main/java/day03/exam/exam3.java` (객체를 만드는 주체를 세 방식으로 나란히 보기, 전통 방식의 `new` 와 호출마다 객체가 쌓이는 점·쓰는 쪽에 구현 클래스 이름이 박히는 결합도 문제, 손으로 만드는 싱글톤과 `private` 생성자·`private static final` 인스턴스·`getInstance()` 창구 세 줄의 역할·클래스마다 되풀이되는 부담·이른 초기화와 늦은 초기화의 갈림, `@Component` 로 스프링 컨테이너에 빈 자동 등록하기와 표시 한 줄이 세 줄을 대신하는 근거가 앞의 리플렉션에 있다는 정리·빈이 기본적으로 하나로 공유되는 점, IOC(제어의 역전)와 DI(의존성 주입)의 갈림과 구현을 갈아 끼워도 쓰는 쪽이 그대로인 이유, 하나뿐인 객체에 상태를 담으면 요청끼리 덮어쓰는 문제)
- `2026B_Spring/springweb/src/main/java/day03/exam/AppStart.java` (day03 패키지에 진입점 두기, `@SpringBootApplication` 이 내장 톰캣과 IOC/DI 컴포넌트 지원을 함께 켜는 자리, 컴포넌트 스캔 범위가 진입점이 속한 패키지와 그 하위로 정해지는 점과 어느 진입점을 띄우느냐에 따라 등록되는 빈이 갈리는 자리)
- `2026B_Spring/springweb/src/main/java/day03/exam/RestController1.java` (`@Controller` 가 `@Component` 를 품고 웹 요청을 받는 자리를 얹는다는 점과 서블릿을 물려받던 자리를 대신하는 구조, `@GetMapping` 으로 주소를 메소드에 잇기와 `value =` 표기·생략 표기가 같은 뜻인 자리, `@ResponseBody` 로 반환값을 응답 본문에 싣기와 붙이지 않으면 뷰 이름으로 읽히는 갈림·메소드 단위로 고를 수 있다는 점, 반환 타입이 Content-Type을 정하는 규칙(`String` 은 `text/plain`·나머지는 `application/json`), `Map<String, Object>` 를 그대로 돌려줘 키·값이 JSON이 되는 자리와 값 타입을 `Object` 로 열어 섞어 담기·`HashMap` 의 순서가 보장되지 않는 점, `@Data` 가 붙은 DTO를 돌려주기와 setter로 값을 채우고 getter가 JSON 키를 정하는 자리, 컴파일 시점에 생성된 메소드를 실행 중에 읽어 응답을 만드는 두 갈래의 결합)
- `2026B_Spring/springweb/src/main/java/day03/exam/RestController2.java` (`@Component`→`@Controller`→`@RestController` 로 겹쳐 올라가는 표시의 계단과 `@RestController` 를 붙이면 메소드마다 `@ResponseBody` 를 생략할 수 있는 자리·화면을 돌려주면 `@Controller`·값을 돌려주면 `@RestController` 로 갈리는 기준, `@RequestMapping` 을 클래스에 올려 공통 URL을 한 자리에서 정하기와 클래스 값과 메소드 값이 이어 붙는 규칙, `@RequestParam` 으로 쿼리스트링·폼 값을 매개변수에 받기와 이름이 짝을 맞추는 기준·문자열로 오는 값을 매개변수 타입에 맞춰 스프링이 변환해 주는 자리, `@RequestParam` 을 생략할 수 있는 조건과 매개변수 이름이 `.class` 에 남지 않을 수 있다는 점, `name` 으로 요청 쪽 이름 지목하기, `required = false` 로 선택 값 만들기와 기본형에 `null` 을 담을 수 없어 생기는 갈림, `defaultValue` 가 문자열인 이유가 애노테이션 속성 타입 제한과 이어지는 자리, `@RequestParam Map<String, Object>` 로 파라미터를 통째로 받기와 값이 전부 문자열로 들어오는 점·무엇을 받는지가 서명에 드러나지 않는 점, `@ModelAttribute` 로 DTO에 담아 받기와 기본 생성자로 만들고 setter로 채우는 과정이 `newInstance`·`invoke` 와 같은 구조라는 정리·`@Data` 가 그 통로를 만들어 주는 자리, 값을 받는 세 방식의 갈림과 값 개수에 따라 고르는 기준, `@DeleteMapping` 으로 주소는 같고 방식으로 갈리는 매핑 만들기와 네 가지 방식별 짧은 표시)
- `2026B_Spring/springweb/build.gradle` (롬복 의존성 추가, `compileOnly` 로 실행 배포본에서 빠지는 이유와 `annotationProcessor` 로 컴파일 중 처리기를 등록하는 자리)

## 관련 노트

[[Java MOC]] · [[Java Spring day02 스프링 부트 실행과 계층 이식]] · [[Java Spring day01 서블릿과 HTTP 메소드]] · [[Java Spring Boot 프로젝트 생성(분석)]] · [[Java day13 Object 클래스와 리플렉션]] · [[Java day15 Map과 HashMap]] · [[Java day14 제네릭]] · [[Java day12 예외 처리와 JDBC]] · [[Java day16 스레드 동기화]] · [[Java day12 종합예제 JDBC DAO]] · [[Java day11 인터페이스]] · [[Java day10 상속과 다형성]] · [[Java day08 접근제한자와 static]] · [[Java day06 생성자와 콘솔 게시판]] · [[Java day05 클래스와 인스턴스]] · [[Java day02 타입 변환]] · [[Java day01 자바 구조와 자료형]] · [[JS day14 게시판 CRUD]] · [[개념 - 싱글톤]] · [[KDT_2026 학습 지도]]
