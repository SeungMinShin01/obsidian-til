---
출처: Claude 분석
작성일: 2026-08-21
tags: [코드정리]
---

# JAVA 함수형 인터페이스

> 상위: [[JAVA 상속과 인터페이스]]

전부 ※. 추상메소드가 1개뿐인 인터페이스는 람다로 즉석 구현할 수 있다 — 그 대표 4개가 표준 라이브러리에 있다.

## 4대장

```java
import java.util.function.*;

Function<String, Integer> len = s -> s.length();
Consumer<String> print = s -> System.out.println(s);
Supplier<LocalDate> today = () -> LocalDate.now();
Predicate<Integer> isEven = n -> n % 2 == 0;

len.apply("java");
print.accept("hi");
today.get();
isEven.test(4);
```

- Function: 받아서 변환해 돌려준다(입력→출력). 실행은 `apply`
- Consumer: 받아서 쓰기만 하고 반환이 없다. 실행은 `accept`
- Supplier: 받는 것 없이 만들어 준다. 실행은 `get`
- Predicate: 받아서 참/거짓을 판정한다. 실행은 `test`
- 스트림의 `map(Function)` `forEach(Consumer)` `filter(Predicate)`가 정확히 이 타입들을 받는 자리다

## 메소드 참조

```java
Function<String, Integer> len = String::length;
Consumer<String> print = System.out::println;
Supplier<ArrayList<String>> maker = ArrayList::new;
```

- `클래스::메소드`는 "그 메소드를 그대로 쓰겠다"는 람다의 축약이다
- 세 꼴만 알면 다 읽힌다: `String::length`(인스턴스 메소드), `System.out::println`(특정 객체의 메소드), `ArrayList::new`(생성자)

## 직접 만드는 함수형 인터페이스

```java
@FunctionalInterface
interface Discount {
    int apply(int price);
}

Discount tenPercent = price -> price * 90 / 100;
Discount fixed500 = price -> price - 500;

int pay = tenPercent.apply(10000);
```

- `@FunctionalInterface`는 "추상메소드 1개"를 컴파일러가 지켜주게 하는 표식이다
- 얻는 효과: 할인 정책·요금 규칙처럼 **계산 방법 자체를 값처럼** 변수에 담아 갈아끼울 수 있다. 전략 교체 패턴을 클래스 없이 한 줄로 하는 셈이다
