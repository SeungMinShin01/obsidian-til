---
출처: Claude 분석
원본: KDT_2026/2026B_Spring/springweb/src/main/java/day08/exam/exam3.java
작성일: 2026-09-09
tags: [학습, java]
---

# Spring day08 — 컬렉션 순회와 스트림 API

> 실습 파일: `day08/exam/exam3.java`
> 허브: [[Spring MOC]] · 이전: [[Spring day08 구현체를 값처럼 넘기는 람다]] · 다음: [[Spring day08 메소드 레퍼런스로 줄인 람다]]

앞 노트는 **동작 자체를 값으로 만들어 넘기는 표기**(익명 구현체·람다·표준 함수형 인터페이스 네 개)를 정리한 자리였습니다. 거기서 만든 람다는 대부분 직접 `apply()`·`test()` 를 불러 확인만 했고, "남의 메소드에 넘기는 자리"는 이름만 적어 두고 넘어갔습니다.

이번 실습이 그 자리입니다. 정수 열 개짜리 리스트 하나를 두고 **컬렉션을 도는 세 표기**(일반 `for`·향상된 `for`·`forEach`)를 나란히 적어 본 다음, 스트림 API의 중간 연산 다섯 개(`map`·`filter`·`sorted`·`distinct`·`limit`)를 하나씩 붙여 봅니다. 마지막에는 그 다섯을 한 줄로 이어 체인을 만들어 보는데, 이 모양이 그동안 서비스 층에서 엔티티 목록을 DTO 목록으로 바꾸며 계속 적어 온 `.stream().map(...).toList()` 의 정체입니다.

## 1. 배운 내용

### 1-1. 실습의 출발점 — 불변 리스트 하나

```java
List<Integer> numbers = List.of(1, 2, 3, 4, 5, 6, 7, 8, 9, 10);
```

`List.of(...)` 는 자바 9에서 들어온 정적 팩토리 메소드입니다. `new ArrayList<>()` 를 만들고 `add` 를 열 번 부르는 대신 한 줄로 값을 채웁니다. 다만 성질이 갈립니다.

| 만드는 법 | 성질 | 값 추가·삭제 |
| --- | --- | --- |
| `new ArrayList<>()` | 변경 가능 | 된다 |
| `List.of(...)` | **불변(immutable)** | 부르면 `UnsupportedOperationException` |
| `Arrays.asList(...)` | 크기 고정 | `set` 은 되고 `add`·`remove` 는 안 된다 |

실습이 하는 일이 "읽어서 새 리스트를 만드는 것"뿐이라 불변 리스트로 충분합니다. 스트림도 원본을 건드리지 않고 **새 결과를 만들어 돌려주는** 방식이라 이 조합이 자연스럽습니다.

### 1-2. 컬렉션을 도는 세 표기

같은 출력을 내는 세 가지를 나란히 적어 둡니다.

```java
// 1) 일반 for문 — 인덱스로 돈다
for (int index = 0; index <= numbers.size() - 1; index++) {
    System.out.println(numbers.get(index));
}

// 2) 향상된 for문 — 요소를 직접 꺼낸다
for (Integer data : numbers) {
    System.out.println(data);
}

// 3) forEach — 할 일을 넘긴다
numbers.forEach((data) -> {
    System.out.println(data);
});
```

세 표기의 갈림을 정리하면 이렇습니다.

| 표기 | 인덱스가 있는가 | 도는 주체 | 중간에 멈출 수 있는가 |
| --- | --- | --- | --- |
| 일반 `for` | 있다 (`index`) | 부르는 쪽 | `break`·`continue` 가능 |
| 향상된 `for` | 없다 | 부르는 쪽 | `break`·`continue` 가능 |
| `forEach` | 없다 | **컬렉션 쪽** | 불가 (`return` 은 그 회차만 건너뜀) |

핵심은 세 번째 칸입니다. 위 둘은 **내가 돌면서** 안에서 무엇을 할지 적는 구조(외부 반복)이고, `forEach` 는 **도는 일은 컬렉션에게 맡기고** 회차마다 할 일만 넘기는 구조(내부 반복)입니다. 앞 노트에서 정리한 "뼈대는 라이브러리가 갖고 달라지는 부분만 넘긴다"가 그대로 여기에 나타납니다.

인덱스가 필요하면(몇 번째인지 출력해야 하거나, 앞뒤 요소를 함께 봐야 하거나) 일반 `for` 가 남습니다. 인덱스를 안 쓰는데 일반 `for` 로 도는 경우가 대부분이라 향상된 `for` 가 기본값이 되는 편입니다.

### 1-3. `forEach` 에 넘어가는 것의 정체

```java
numbers.forEach((data) -> {
    System.out.println(data);
});
```

`forEach` 의 시그니처는 `void forEach(Consumer<? super T> action)` 입니다. 즉 넘기는 람다는 **앞 노트에서 본 `Consumer`** 그 자체입니다.

| 앞 노트에서 만든 것 | 이번 실습에서 넘기는 자리 |
| --- | --- |
| `Consumer<T>` — 받기만 하고 반환 없음 | `forEach(...)` |
| `Function<T, R>` — 받아서 바꿔 반환 | `map(...)` |
| `Predicate<T>` — 받아서 참·거짓 반환 | `filter(...)` |
| `Supplier<T>` — 받지 않고 만들어 반환 | `orElseGet(...)` 등 |

넷을 따로 외운 것이 아니라, **스트림 메소드마다 요구하는 모양이 달라서 넷이 나뉘어 있는 것**이라고 보는 편이 이해가 빠릅니다. `map` 은 바뀐 값을 받아야 하니 반환이 있는 `Function` 을 요구하고, `filter` 는 남길지 말지를 받아야 하니 `Predicate` 를 요구합니다.

### 1-4. 스트림의 세 토막 구조

주석이 형태를 이렇게 적어 둡니다.

```
리스트객체.stream().중간연산1().중간연산2().최종연산();
```

세 토막으로 읽습니다.

| 토막 | 하는 일 | 돌려주는 것 | 예 |
| --- | --- | --- | --- |
| **소스** | 컬렉션을 흐름으로 바꾼다 | `Stream<T>` | `.stream()` |
| **중간 연산** | 흐름을 가공한다 | `Stream<T>` (다시 스트림) | `map`·`filter`·`sorted`·`distinct`·`limit` |
| **최종 연산** | 흐름을 끝낸다 | 스트림이 아닌 것 | `toList()`·`forEach()`·`count()` |

중간 연산이 계속 이어 붙을 수 있는 이유는 앞 노트에서 정리한 체이닝 조건과 같습니다 — **앞 호출이 객체(여기서는 다시 `Stream`)를 돌려주기 때문**입니다. 최종 연산은 `List` 나 `void` 를 돌려주므로 그 뒤로는 이어지지 않고, 그래서 "중간 연산은 여러 번, 최종 연산은 한 번"이라는 규칙이 문법 제한이 아니라 반환 타입에서 저절로 따라 나옵니다.

### 1-5. `stream().forEach()` — 리스트의 `forEach` 와 갈리는 자리

```java
numbers.stream().forEach((data) -> {
    System.out.println(data);
});
```

결과만 보면 `numbers.forEach(...)` 와 같습니다. 굳이 `stream()` 을 거치는 값어치는 **그 사이에 중간 연산을 끼울 수 있다**는 점 하나입니다. 거를 것도 바꿀 것도 없이 그냥 돌기만 한다면 `numbers.forEach(...)` 로 충분합니다.

| 표기 | 정의된 곳 | 중간 연산을 끼울 수 있는가 |
| --- | --- | --- |
| `numbers.forEach(...)` | `Iterable` | 못 끼운다 |
| `numbers.stream().forEach(...)` | `Stream` | 끼운다 |

### 1-6. `map` — 값을 갈아 끼우는 중간 연산

```java
List<Integer> newList = numbers.stream().map((data) -> {
    return data;
}).toList();
```

`map` 은 요소 하나를 받아 **다른 값 하나로 바꿔** 흘려보냅니다. 개수는 그대로 두고 내용물만 갈립니다.

읽을 때 중요한 자리는 `map` 이 **타입까지 바꿀 수 있다**는 점입니다. `Stream<A>` 에 `A → B` 를 넘기면 `Stream<B>` 가 나옵니다.

```java
// Integer → String 으로 타입이 갈리는 예
List<String> texts = numbers.stream()
        .map((n) -> "번호 " + n)
        .toList();
```

이 성질이 그대로 엔티티 → DTO 변환입니다. `Stream<BoardEntity>` 에 "엔티티 하나를 DTO 하나로 바꾸는 함수"를 넘기면 `Stream<BoardDto>` 가 되고, 최종 연산으로 리스트를 받습니다.

### 1-7. `filter` — 조건에 맞는 것만 남기기

```java
List<Integer> newList2 = numbers.stream().filter((data) -> {
    return data % 2 == 0;
}).toList();
System.out.println(newList2); // [2, 4, 6, 8, 10]
```

`filter` 에 넘기는 것은 `Predicate` 라 **반환이 반드시 `boolean`** 입니다. `true` 면 남고 `false` 면 버려집니다.

`map` 과 짝지어 성질을 정리해 두면 헷갈리지 않습니다.

| 중간 연산 | 개수 | 타입 | 넘기는 것 |
| --- | --- | --- | --- |
| `map` | 그대로 | 바뀔 수 있다 | `Function` |
| `filter` | 줄어든다 | 그대로 | `Predicate` |

### 1-8. `sorted` — 정렬과 `Comparator`

```java
List<Integer> newList3 = numbers.stream().sorted().toList();
```

매개변수 없는 `sorted()` 는 요소의 **자연 순서**(`Comparable` 의 `compareTo`)로 오름차순 정렬합니다. 숫자는 작은 것부터, 문자열은 사전순입니다.

순서를 바꾸려면 비교 기준을 넘깁니다.

```java
.sorted(Comparator.reverseOrder())            // 내림차순
.sorted(Comparator.comparing(BoardDto::getTitle))          // 제목 기준 오름차순
.sorted(Comparator.comparing(BoardDto::getCdate).reversed()) // 작성일 기준 내림차순
```

`Comparator` 도 추상 메소드가 하나뿐인 인터페이스라 람다로 적을 수 있고(`(a, b) -> b - a`), `Comparator.comparing(...)` 은 그 람다를 손으로 적지 않아도 되게 만들어 둔 도우미입니다. 정렬 기준이 두 개 이상이면 `thenComparing` 으로 이어 붙입니다.

한 가지 주의할 자리는 **정렬은 기본이 오름차순**이라는 점입니다. 내림차순이 필요한데 `sorted()` 만 적어 두면 결과가 반대로 나오는데, 예외가 나지 않고 조용히 순서만 갈리므로 출력으로 확인하는 편이 안전합니다.

### 1-9. `distinct` 와 `limit`

```java
List<Integer> newList4 = numbers.stream().distinct().limit(3).toList();
```

| 연산 | 하는 일 | 판정 기준 |
| --- | --- | --- |
| `distinct()` | 중복 제거 | `equals()`·`hashCode()` |
| `limit(n)` | 앞에서 `n` 개만 | 개수 |
| `skip(n)` | 앞 `n` 개 건너뛰기 | 개수 |

`distinct()` 의 판정이 `equals()` 라는 점이 실무에서 걸리는 자리입니다. `Integer`·`String` 은 값으로 비교하도록 이미 재정의되어 있어 기대대로 돌지만, 직접 만든 DTO·엔티티는 재정의하지 않으면 **주소로 비교**해서 내용이 같아도 중복으로 안 봅니다. 롬복의 `@EqualsAndHashCode` 나 자바 16의 `record` 를 쓰면 그 두 메소드를 만들어 줍니다.

`limit`·`skip` 두 개를 붙이면 "몇 개 건너뛰고 몇 개"가 되어 페이징과 모양이 같아집니다. 다만 DB에서 다 꺼내 온 뒤 메모리에서 자르는 것이라 실제 페이징과는 성질이 다릅니다 — 그 이야기는 3장에 적습니다.

### 1-10. 중간 연산을 이어 붙이기 — 순서가 결과를 정한다

실습의 마지막이 다섯 개를 한 줄로 잇습니다.

```java
List<Integer> newList5 = numbers.stream()
        .distinct()                          // 중복 제거 (중간)
        .filter((x) -> { return x % 2 == 0; }) // 짝수만  (중간)
        .map((x) -> { return x; })            // 변환     (중간)
        .sorted(Comparator.reverseOrder())    // 내림차순 (중간)
        .limit(3)                             // 앞 3개   (중간)
        .toList();                            // 리스트로 (최종)
System.out.println(newList5); // [10, 8, 6]
```

읽는 법은 **위에서 아래로 값이 흘러가는 파이프**입니다. 한 줄씩 따라가 보면 이렇습니다.

| 단계 | 흐름의 상태 |
| --- | --- |
| 소스 | `1 2 3 4 5 6 7 8 9 10` |
| `distinct()` | 그대로 (원래 중복이 없음) |
| `filter(짝수)` | `2 4 6 8 10` |
| `map(그대로)` | `2 4 6 8 10` |
| `sorted(내림차순)` | `10 8 6 4 2` |
| `limit(3)` | `10 8 6` |
| `toList()` | `[10, 8, 6]` |

여기서 얻어 갈 것은 **연산의 순서가 곧 결과**라는 점입니다. `sorted` 와 `limit` 의 자리를 바꾸면 "앞 3개를 뽑아서 정렬"이 되어 `[6, 4, 2]` 가 나옵니다. 같은 연산을 같은 개수로 썼는데 답이 갈리므로, 체인을 적을 때는 문장으로 먼저 읽어 보는 편이 안전합니다 — "짝수만 남겨서, 큰 것부터 정렬해서, 위에서 셋".

### 1-11. 메소드 레퍼런스

주석이 마지막에 이름만 적어 둔 표기입니다.

```java
numbers.forEach(x -> System.out.println(x)); // 람다
numbers.forEach(System.out::println);        // 메소드 레퍼런스
```

"받은 것을 그대로 어떤 메소드에 넘기기만 하는" 람다는 `클래스::메소드` 또는 `객체::메소드` 로 줄일 수 있습니다. 앞 노트에서 정리한 네 모양이 그대로 쓰입니다.

| 모양 | 예 | 같은 뜻의 람다 |
| --- | --- | --- |
| `객체::인스턴스메소드` | `System.out::println` | `x -> System.out.println(x)` |
| `클래스::static메소드` | `Integer::parseInt` | `s -> Integer.parseInt(s)` |
| `클래스::인스턴스메소드` | `String::toUpperCase` | `s -> s.toUpperCase()` |
| `클래스::new` | `BoardDto::new` | `() -> new BoardDto()` |

줄일 수 있는 조건은 하나입니다 — **람다 몸통이 메소드 호출 하나뿐이고 매개변수가 그대로 전달될 것.** 몸통에 다른 문장이 섞이면 람다로 남깁니다.

## 2. 추가로 알면 좋은 활용법

### 2-1. 실습이 마지막 줄에 적어 둔 자리 — 엔티티 ↔ DTO 변환

주석이 "JPA에서 Entity ↔ DTO 변환 과정에 자주 쓰임 (forEach, map)"이라고 적어 둔 그 자리입니다. 그동안 서비스 층에서 두 겹 `for` 로 적어 온 조립이 스트림으로는 이렇게 줄어듭니다.

```java
// 반복문으로 적을 때
List<BoardDto> result = new ArrayList<>();
for (BoardEntity entity : boardRepository.findAll()) {
    result.add(BoardDto.from(entity));
}
return result;

// 스트림으로 적을 때
return boardRepository.findAll().stream()
        .map(BoardDto::from)
        .toList();
```

`from` 이 `static` 이라 `BoardDto::from` 이라는 메소드 레퍼런스가 그대로 성립합니다. 앞 노트에서 정리한 "`toEntity()` 는 인스턴스 메소드, `from()` 은 `static`" 이라는 갈림이 여기서 표기 차이로 나타납니다.

| 변환 방향 | 메소드 | 스트림에서 |
| --- | --- | --- |
| 엔티티 → DTO | `static Dto from(Entity e)` | `.map(BoardDto::from)` |
| DTO → 엔티티 | `Entity toEntity()` (인스턴스) | `.map(BoardDto::toEntity)` |

두 번째 줄도 `클래스::인스턴스메소드` 모양이라 성립합니다 — 스트림이 흘려보내는 요소가 곧 그 메소드를 부를 주체가 되기 때문입니다.

### 2-2. 람다 몸통 줄여 적기

실습은 배우는 자리라 `{ return ...; }` 를 다 적어 뒀지만, 실무 코드에서는 대부분 줄인 모양으로 만납니다.

```java
.map((data) -> { return data * 2; })  // 전부 적은 모양
.map((data) -> data * 2)              // 중괄호·return 생략
.map(data -> data * 2)                // 매개변수 괄호까지 생략
```

줄일 수 있는 조건입니다.

| 생략하는 것 | 조건 |
| --- | --- |
| 매개변수 타입 | 항상 (컴파일러가 추론) |
| 매개변수 괄호 | 매개변수가 **정확히 하나**일 때 |
| 중괄호와 `return` | 몸통이 **식 하나**일 때 |

두 줄 이상이 되면 중괄호와 `return` 이 다시 필요합니다. 처음에는 다 적어 두고 익숙해진 뒤 줄이는 순서가 읽기에 편합니다.

### 2-3. 최종 연산 — `toList()` 말고 무엇이 있는가

실습은 `toList()`·`forEach()` 두 개만 썼지만 최종 연산은 갈래가 더 있습니다.

| 최종 연산 | 돌려주는 것 | 쓰는 자리 |
| --- | --- | --- |
| `toList()` | `List<T>` (불변) | 결과 목록 |
| `collect(Collectors.toList())` | `List<T>` (가변) | 뒤에서 값을 더 넣어야 할 때 |
| `count()` | `long` | 개수만 필요할 때 |
| `sum()`·`average()`·`max()`·`min()` | 숫자·`Optional` | 집계 |
| `anyMatch`·`allMatch`·`noneMatch` | `boolean` | 조건 검사 |
| `findFirst()`·`findAny()` | `Optional<T>` | 하나만 꺼낼 때 |
| `reduce(...)` | `T`·`Optional<T>` | 직접 접어 넣기 |

`toList()` 는 자바 16에서 들어온 축약이고, 돌려주는 리스트가 **불변**이라 그 뒤에 `add` 를 부르면 예외가 납니다. 만든 목록에 값을 더 넣어야 한다면 `collect(Collectors.toList())` 를 쓰거나 `new ArrayList<>(...)` 로 감쌉니다.

### 2-4. `Collectors` — 리스트 말고 다른 모양으로 모으기

`collect()` 에 넘기는 도우미 묶음입니다. 실무에서 자주 만나는 셋만 적어 둡니다.

```java
// 1) 키로 묶기 — 게시글 목록을 작성자별로
Map<String, List<BoardDto>> byWriter = list.stream()
        .collect(Collectors.groupingBy(BoardDto::getWriter));

// 2) 키-값 맵으로
Map<Integer, String> titleById = list.stream()
        .collect(Collectors.toMap(BoardDto::getBno, BoardDto::getTitle));

// 3) 문자열로 잇기
String titles = list.stream()
        .map(BoardDto::getTitle)
        .collect(Collectors.joining(", "));
```

`groupingBy` 는 "댓글 목록을 게시글 번호별로 묶어 두고 게시글 조립할 때 꺼내 쓰기" 같은 자리에서 1+N 회피에 쓰이기도 합니다. `toMap` 은 키가 겹치면 예외가 나므로 키가 유일한지 먼저 확인하는 편이 안전합니다.

### 2-5. 중간 연산은 최종 연산이 부를 때 돈다 (지연 평가)

중간 연산만 적어 두면 **아무 일도 일어나지 않습니다.**

```java
Stream<Integer> s = numbers.stream()
        .filter(x -> { System.out.println("검사 " + x); return x % 2 == 0; });
// 여기까지는 아무것도 출력되지 않는다
s.toList(); // 이 줄에서 비로소 "검사 1" 부터 찍힌다
```

중간 연산은 "무엇을 할지"를 적어 두기만 하고, 최종 연산이 붙는 순간 요소가 한 번에 하나씩 파이프를 통과합니다. 요소별로 세로로 도는 것이지, 연산별로 열 개씩 가로로 도는 것이 아닙니다.

여기서 나오는 실용적인 결론 둘입니다.

- **`filter` 를 앞쪽에 둔다** — 뒤 연산이 처리할 개수가 줄어듭니다
- **`limit` 이 있으면 앞 연산도 필요한 만큼만 돈다** — 무한 스트림(`Stream.iterate`)이 성립하는 이유가 이것입니다

또 하나, 스트림은 **한 번 쓰면 끝**입니다. 최종 연산을 부른 스트림을 다시 쓰면 예외가 납니다. 같은 소스로 두 결과가 필요하면 `numbers.stream()` 을 두 번 부릅니다.

### 2-6. 반복문을 쓸지 스트림을 쓸지

무조건 스트림이 낫지는 않습니다. 갈리는 기준을 적어 둡니다.

| 상황 | 고르는 쪽 |
| --- | --- |
| 걸러서 바꿔서 모으기 | 스트림 (의도가 이름으로 드러남) |
| 인덱스가 필요 | 반복문 |
| 중간에 `break` 로 끊어야 함 | 반복문 (또는 `takeWhile`·`findFirst`) |
| 안에서 예외를 던지거나 잡아야 함 | 반복문 (람다 안 체크 예외는 다루기 번거로움) |
| 바깥 지역변수를 계속 고쳐야 함 | 반복문 (람다는 effectively final 제약) |

마지막 줄이 앞 노트에서 정리한 제약과 이어집니다 — 람다 안에서는 바깥 지역변수를 읽을 수만 있고 바꿀 수 없어서, 누적이 필요하면 `reduce`·`Collectors` 쪽으로 표현을 바꾸게 됩니다.

## 3. 더 나아가 알면 좋은 것

### 3-1. 기본형 스트림 — 박싱을 피하는 갈래

`Stream<Integer>` 는 요소마다 `Integer` 객체를 만듭니다. 숫자만 다룬다면 기본형 전용 스트림이 따로 있습니다.

```java
int sum = numbers.stream().mapToInt(Integer::intValue).sum();
IntStream.rangeClosed(1, 10).forEach(System.out::println);
```

`IntStream`·`LongStream`·`DoubleStream` 셋이 있고, `sum()`·`average()`·`max()` 같은 집계 메소드를 바로 갖고 있다는 점이 실용적인 차이입니다. `Stream<T>` 에서 넘어갈 때는 `mapToInt`, 돌아올 때는 `boxed()` 를 씁니다.

### 3-2. `Optional` 과 스트림 — 모양이 같은 이유

`Optional` 에도 `map`·`filter`·`ifPresent` 가 있습니다. "값이 0개나 1개인 스트림"이라고 보면 두 API의 모양이 같은 이유가 설명됩니다.

```java
boardRepository.findById(bno)
        .map(BoardDto::from)          // 있으면 변환
        .orElseThrow(() -> new IllegalArgumentException("없는 번호"));
```

`orElseThrow` 에 넘기는 것이 `Supplier` 라는 점도 앞 노트와 이어집니다 — 예외 객체를 **미리 만들어 두는 것이 아니라** 필요할 때 만들도록 미루기 위해서입니다.

### 3-3. 병렬 스트림과 그때 붙는 제약

`.stream()` 을 `.parallelStream()` 으로 바꾸면 여러 스레드가 나눠 처리합니다. 다만 조건이 붙습니다.

- 람다가 **바깥 상태를 건드리지 않아야** 한다 (건드리면 결과가 실행마다 갈릴 수 있다)
- 요소 순서에 의존하는 연산(`forEachOrdered`·`limit`)은 이득이 줄어든다
- 데이터가 적으면 스레드를 나누는 비용이 더 크다

웹 요청 처리 중에는 이미 요청마다 스레드가 나뉘어 있어 병렬 스트림을 더 얹는 것이 오히려 손해인 경우가 많습니다. 쓰기 전에 측정하는 순서가 안전합니다.

### 3-4. JPA와 스트림이 만나는 자리 — 편해 보이지만 조심할 지점

스트림으로 조립이 짧아지면 그 안에서 무슨 일이 벌어지는지 눈에 덜 띕니다.

```java
return boardRepository.findAll().stream()
        .map(entity -> BoardDto.from(entity, entity.getCommentList())) // 여기서 지연 로딩이 나간다
        .toList();
```

`getCommentList()` 를 건드리는 순간 게시글 수만큼 댓글 조회 쿼리가 나갑니다(1+N). 반복문으로 적었을 때와 성질은 같은데, 한 줄로 압축되어 있어 발견이 늦어지는 것이 차이입니다. `show-sql` 로 쿼리 개수를 세어 보는 습관이 여기서도 그대로 쓰입니다. 대응은 `join fetch`·`@BatchSize`·`@EntityGraph` 쪽입니다.

또 하나, `limit`·`skip` 으로 자르는 것은 **DB에서 전부 꺼내 온 뒤** 메모리에서 버리는 방식입니다. 진짜 페이징은 리포지토리에서 `Pageable` 을 받아 SQL에 `LIMIT` 을 실어야 합니다.

### 3-5. 다음에 볼 키워드

- `Collectors` 전반 — `groupingBy`·`partitioningBy`·`counting`·`summingInt`·`mapping`
- `flatMap` — 목록의 목록을 한 겹 펴기 (게시글별 댓글을 전체 댓글 하나로)
- `Stream.iterate`·`generate`·`takeWhile`·`dropWhile` — 무한 스트림과 끊는 조건
- `reduce` — `sum`·`max` 가 사실은 이것의 특수한 경우인 자리
- `Comparator.comparing`·`thenComparing`·`nullsFirst` — 정렬 기준 조립
- `record` 와 `equals`·`hashCode` — `distinct`·`toMap` 이 제대로 도는 전제
- `Pageable`·`Page`·`Slice` — 메모리에서 자르지 않는 페이징
- `@EntityGraph`·`join fetch` — 조립 전에 미리 채워 오기
- `Stream.toList()` 와 `Collectors.toList()` 의 가변·불변 차이

## 실습 파일

- `2026B_Spring/springweb/src/main/java/day08/exam/exam3.java` (**컬렉션 순회 세 표기와 스트림 API 중간 연산 다섯 개를 한 자리에 모아 둔 예제** — `List.of` 로 만든 불변 리스트를 소스로 두고 일반 `for`·향상된 `for`·`forEach` 를 나란히 적어 앞 둘이 부르는 쪽이 도는 외부 반복이고 `forEach` 는 도는 일을 컬렉션에 맡기는 내부 반복이라 `break` 가 성립하지 않는 갈림, `forEach` 에 넘어가는 것이 앞 노트의 `Consumer` 이고 `map` 은 `Function`·`filter` 는 `Predicate` 를 요구해 함수형 인터페이스 넷이 스트림 메소드의 요구에 맞춰 나뉘어 있다는 정리, `소스 → 중간 연산 → 최종 연산` 세 토막 구조와 중간 연산이 다시 `Stream` 을 돌려주기 때문에 체이닝이 성립하고 최종 연산은 스트림이 아닌 것을 돌려줘 그 뒤가 끊기므로 "중간 여러 번·최종 한 번"이 반환 타입에서 저절로 따라 나오는 자리, `map` 이 개수는 두고 타입까지 바꿀 수 있어 `Stream<Entity>` 를 `Stream<Dto>` 로 만드는 것이 그대로 엔티티 변환인 점과 `filter` 는 타입을 두고 개수를 줄이는 대비, `sorted()` 의 기본이 자연 순서 오름차순이고 `Comparator.reverseOrder()`·`comparing`·`thenComparing` 으로 기준을 넘기는 표기, `distinct()` 의 판정이 `equals`·`hashCode` 라 직접 만든 타입은 재정의가 전제인 자리와 `limit`·`skip` 의 조합이 페이징과 모양만 같은 점, 다섯 연산을 한 줄로 이은 체인을 단계별 흐름 표로 따라가며 `sorted` 와 `limit` 의 자리를 바꾸면 결과가 갈리므로 순서가 곧 의미인 정리, 메소드 레퍼런스 네 모양과 줄일 수 있는 조건이 "몸통이 메소드 호출 하나이고 매개변수가 그대로 전달될 것"인 자리)

## 관련 노트

[[Spring MOC]] · [[Spring day08 구현체를 값처럼 넘기는 람다]] · [[Spring day08 메소드 레퍼런스로 줄인 람다]] · [[KDT_2026 학습 지도]]
