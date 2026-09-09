---
출처: Claude 분석
원본: KDT_2026/2026B_Spring/springweb/src/main/java/day08/exam/exam4.java
작성일: 2026-09-09
tags: [학습, java]
---

# Spring day08 — 메소드 레퍼런스로 줄인 람다

> 실습 파일: `day08/exam/exam4.java`
> 허브: [[Spring MOC]] · 이전: [[Spring day08 컬렉션 순회와 스트림 API]]

앞 노트에서 스트림 체인을 이어 보며 마지막에 메소드 레퍼런스를 이름만 훑고 지나갔습니다. 이번 실습은 그 표기 하나만 떼어 다시 보는 자리입니다. 이름 네 개짜리 리스트를 놓고 **같은 일을 람다로 한 번, 메소드 레퍼런스로 한 번씩 나란히 적어** 두 줄이 같은 결과를 내는지 눈으로 확인합니다.

정리하면 메소드 레퍼런스는 새 기능이 아니라 **축약의 마지막 단계**입니다. 익명 구현체 → 람다 → 메소드 레퍼런스 순으로 지워 온 것들의 끝이고, 지울 수 있는 조건이 그동안 두 번 나온 것보다 훨씬 좁습니다. 그 좁은 조건이 무엇인지가 이번 실습의 핵심입니다.

## 1. 배운 내용

### 1-1. 축약의 마지막 칸

같은 동작을 세 표기로 적으면 이렇게 줄어듭니다.

```java
// ① 람다 — 몸통을 다 적은 모양
Function<String, Integer> function1 = (x) -> {
    return Integer.parseInt(x);
};

// ② 메소드 레퍼런스 — 부를 메소드의 이름만 남긴 모양
Function<String, Integer> function2 = Integer::parseInt;

System.out.println(function1.apply("10")); // 10
```

`function1` 과 `function2` 는 타입도 같고 `apply("10")` 을 부르면 결과도 같습니다. 문자열 `"10"` 을 정수 `10` 으로 바꾸는 함수 하나를 값으로 들고 있다는 점에서 둘은 구분이 없습니다.

갈리는 것은 **적는 양이 아니라 적는 내용**입니다.

| 표기 | 적는 것 | 적지 않는 것 |
| --- | --- | --- |
| 익명 구현체 | 타입·메소드 이름·매개변수·몸통 | — |
| 람다 | 매개변수·몸통 | 타입·메소드 이름·접근제한자 |
| 메소드 레퍼런스 | **부를 메소드의 이름** | 매개변수·몸통까지 전부 |

람다까지는 "무엇을 할지"를 몸통으로 적었습니다. 메소드 레퍼런스는 몸통마저 지우고 **이미 있는 메소드를 손가락으로 가리키기만** 합니다. 그래서 가리킬 메소드가 미리 있어야 하고, 하려는 일이 그 메소드 호출 하나로 딱 떨어져야 합니다.

### 1-2. `::` 뒤에 괄호를 붙이지 않는 이유

표기에서 제일 먼저 눈에 걸리는 자리입니다.

```java
Integer::parseInt        // O
Integer::parseInt()      // X — 컴파일되지 않는다
System.out::println      // O
System.out::println()    // X
```

`parseInt("10")` 은 **지금 실행해서 값을 얻는** 문장입니다. `Integer::parseInt` 는 **나중에 실행할 그 메소드 자체**를 가리키는 값입니다. 실행하는 것이 아니라 넘기는 것이라 인수가 아직 없고, 인수가 없으니 괄호도 없습니다.

인수는 나중에 이 값을 받은 쪽이 채웁니다. `function2.apply("10")` 을 부르는 순간, 혹은 `names.stream().map(String::length)` 에서 스트림이 요소를 하나씩 흘려보내는 순간에 채워집니다. `::` 표기를 볼 때는 "여기서 실행되지 않는다"를 먼저 떠올리는 편이 안전합니다.

### 1-3. 같은 순회를 네 표기로

앞 노트에서 정수 리스트로 봤던 순회를 이번에는 문자열 리스트로 다시 적어 봅니다.

```java
List<String> names = List.of("유재석", "강호동", "신동엽", "서장훈");

// 1) 일반 for문 — 인덱스를 직접 굴린다
for (int index = 0; index < names.size(); index++) {
    System.out.println(names.get(index));
}
// 2) 향상된 for문 — 인덱스가 사라진다
for (String name : names) {
    System.out.println(name);
}
// 3) stream().forEach + 람다 — 도는 일을 스트림에 맡긴다
names.stream().forEach((name) -> {
    System.out.println(name);
});
// 4) stream().forEach + 메소드 레퍼런스 — 몸통까지 지운다
names.stream().forEach(System.out::println);
```

네 줄이 같은 출력을 냅니다. 위에서 아래로 갈수록 **"어떻게 도는가"가 사라지고 "무엇을 할 것인가"만 남습니다.**

| 표기 | 남아 있는 것 | 사라진 것 |
| --- | --- | --- |
| 일반 `for` | 인덱스·조건·증감·꺼내기·출력 | — |
| 향상된 `for` | 꺼내기·출력 | 인덱스 관리 |
| `forEach` + 람다 | 출력 | 꺼내는 일까지 |
| `forEach` + 메소드 레퍼런스 | **출력할 메소드의 이름** | 매개변수 이름까지 |

3)에서 4)로 갈 때 지워진 것은 `(name) -> { ... }` 라는 **매개변수 이름과 중괄호**뿐입니다. `name` 이라는 이름을 지어 준 다음 그대로 `println` 에 넘기기만 했으니, 이름을 짓는 일 자체가 군더더기였던 셈입니다. 이것이 뒤에 정리할 축약 조건의 절반입니다.

### 1-4. 값을 바꿔 내보내는 자리 — `map`

출력만 하면 `Consumer` 로 끝나지만, 값을 바꿔 돌려주려면 `Function` 이 필요합니다.

```java
// 스트림 + 람다
names.stream().map((name) -> {
    return name.length();
}).forEach((result) -> {
    System.out.println(result);
});

// 스트림 + 메소드 레퍼런스
names.stream().map(String::length).forEach(System.out::println);
```

두 번째 줄이 첫 번째 다섯 줄과 같은 일을 합니다. 각각 3, 3, 3, 3 을 찍습니다.

여기서 `String::length` 의 모양이 앞의 `Integer::parseInt` 와 미묘하게 갈립니다. 둘 다 `클래스::메소드` 인데 성질이 다릅니다.

- `Integer.parseInt(x)` — `parseInt` 는 `static` 이라 클래스가 직접 부릅니다. 넘어온 `x` 가 **인수**로 들어갑니다
- `name.length()` — `length()` 는 인스턴스 메소드라 문자열 객체가 부릅니다. 넘어온 `name` 이 **부르는 주체**가 됩니다

표기는 똑같이 `클래스::메소드` 인데, 넘어온 값이 한쪽에서는 인수 자리로 한쪽에서는 주체 자리로 들어갑니다. 컴파일러가 그 메소드가 `static` 인지 아닌지를 보고 알아서 가릅니다. 이 갈림이 다음 절의 표입니다.

### 1-5. 메소드 레퍼런스 네 모양

실습에 나온 것들을 모양별로 모으면 네 가지입니다.

| 모양 | 표기 | 실습의 예 | 풀어 쓰면 |
| --- | --- | --- | --- |
| 정적 메소드 | `클래스::정적메소드` | `Integer::parseInt` | `(x) -> Integer.parseInt(x)` |
| 특정 객체의 인스턴스 메소드 | `객체::메소드` | `System.out::println` | `(x) -> System.out.println(x)` |
| 임의 객체의 인스턴스 메소드 | `클래스::인스턴스메소드` | `String::length` | `(x) -> x.length()` |
| 생성자 | `클래스::new` | `Student::new` | `(x) -> new Student(x)` |

헷갈리는 자리는 2행과 3행입니다. 둘 다 인스턴스 메소드를 가리키는데, **부를 객체가 이미 정해져 있는가**로 갈립니다.

- `System.out::println` — `System.out` 이라는 **객체가 이미 손에 있습니다.** 넘어오는 값은 그 객체의 인수가 됩니다
- `String::length` — 부를 객체가 아직 없습니다. **넘어오는 값이 곧 그 객체**가 됩니다

정리하면 "`::` 왼쪽에 객체가 적혀 있으면 넘어오는 값은 인수, 클래스가 적혀 있고 오른쪽이 인스턴스 메소드면 넘어오는 값이 주체" 입니다.

### 1-6. 객체를 만들어 내는 자리 — 생성자 참조

리스트의 문자열마다 `Student` 객체를 만드는 일을 세 표기로 적습니다.

```java
// ① 전통 방식 — 빈 리스트를 만들어 두고 채운다
List<Student> list1 = new ArrayList<>();
for (int index = 0; index < names.size(); index++) {
    Student student = new Student(names.get(index));
    list1.add(student);
}

// ② 스트림 + 람다
List<Student> list2 = names.stream().map((name) -> {
    return new Student(name);
}).toList();

// ③ 스트림 + 생성자 참조
List<Student> list3 = names.stream().map(Student::new).toList();
```

`Student` 는 이름 하나를 받는 생성자만 가진 작은 클래스입니다.

```java
class Student {
    private String name;

    public Student(String name) {
        this.name = name;
    }
}
```

①과 ③을 견주면 갈림이 분명합니다.

| 축 | ① 전통 | ③ 생성자 참조 |
| --- | --- | --- |
| 담을 그릇 | `new ArrayList<>()` 를 미리 만든다 | `toList()` 가 만들어 준다 |
| 넣는 일 | `add()` 를 직접 부른다 | 스트림이 모은다 |
| 적히는 것 | 어떻게 만들고 어떻게 담는지 | **무엇으로 바꿀 것인지** |
| 결과 리스트 | 변경 가능 | 불변 |

`Student::new` 가 성립하는 근거는 앞의 조건과 같습니다. 람다 몸통이 `new Student(name)` 하나뿐이고, 받은 `name` 을 손대지 않고 그대로 생성자에 넘기기 때문입니다. 중간에 `name.trim()` 같은 가공이 한 칸이라도 끼면 그 순간 줄일 수 없습니다.

한 가지 더, 마지막 줄의 결과가 `List<Student>` 로 잡히는 것은 **`map` 이 개수는 두고 타입만 바꾸기 때문**입니다. 이름 네 개가 들어가면 학생 네 명이 나옵니다. 앞 노트에서 `Stream<Entity>` 를 `Stream<Dto>` 로 만들던 것과 완전히 같은 구조이고, 실제로 다음 절이 그 이야기입니다.

### 1-7. 줄일 수 있는 조건

실습에서 줄인 자리와 줄이지 않은 자리를 모아 보면 조건이 두 줄로 정리됩니다.

> ① 람다 몸통이 **메소드 호출(또는 생성자 호출) 하나**뿐이고
> ② 받은 매개변수가 **가공 없이 그대로** 그 호출에 넘어갈 것

두 조건 중 하나라도 어긋나면 람다로 남겨 둡니다.

```java
// 줄일 수 있다 — 받은 값을 그대로 넘긴다
.map((name) -> new Student(name))        →  .map(Student::new)
.map((name) -> name.length())            →  .map(String::length)
.forEach((name) -> System.out.println(name))  →  .forEach(System.out::println)

// 줄일 수 없다 — 값을 가공하거나, 문장이 둘 이상이거나, 인수가 섞인다
.map((name) -> new Student(name.trim()))      // 가공이 끼었다
.map((name) -> name.length() + 1)             // 호출 뒤에 연산이 붙었다
.map((name) -> new Student(name, 20))         // 리터럴이 함께 들어간다
.forEach((name) -> {                          // 문장이 둘이다
    System.out.println(name);
    count++;
})
```

굳이 줄이지 않아도 되는 자리도 있습니다. 매개변수 이름이 의미를 담고 있어서 읽는 데 도움이 되면 람다로 두는 편이 낫습니다. 축약은 목적이 아니라 **군더더기가 실제로 있을 때만 쓰는 도구**입니다.

## 2. 추가로 알면 좋은 활용법

### 2-1. 서비스 층에서 이미 쓰고 있던 자리

그동안 반복 실습마다 적어 온 조립 코드가 정확히 이 표기입니다.

```java
// 지금까지 적어 온 모양
List<BoardDto> list = boardRepository.findAll().stream()
        .map((entity) -> BoardDto.from(entity))
        .toList();

// 줄이면
List<BoardDto> list = boardRepository.findAll().stream()
        .map(BoardDto::from)
        .toList();
```

`from()` 이 `static` 이라 `클래스::정적메소드` 모양(표의 1행)으로 성립합니다. 반대 방향은 모양이 갈립니다.

```java
// dto 목록을 엔티티 목록으로
.map(BoardDto::toEntity)     // 클래스::인스턴스메소드 (표의 3행)
```

`toEntity()` 는 인스턴스 메소드라 넘어오는 `BoardDto` 가 **부르는 주체**가 됩니다. 앞선 실습에서 `dto.toEntity()` 와 `Dto.from(entity)` 가 갈렸던 근거 — 부르는 시점에 그 타입의 객체가 손에 있느냐 — 가 메소드 레퍼런스의 모양에서도 그대로 드러납니다. 같은 클래스의 두 변환 메소드가 표의 서로 다른 행에 놓입니다.

### 2-2. `Optional` 과 예외 생성자

`orElseThrow` 에 넘기는 것은 `Supplier` 이고, 그 자리에 생성자 참조가 잘 맞습니다.

```java
BoardEntity entity = boardRepository.findById(id)
        .orElseThrow(() -> new IllegalArgumentException("없는 번호"));

// 메시지가 필요 없으면
BoardEntity entity = boardRepository.findById(id)
        .orElseThrow(IllegalArgumentException::new);
```

메시지를 붙이려면 인수가 하나 들어가므로 람다로 남습니다. 위·아래 둘 다 **예외 객체를 그 자리에서 만들지 않고 만드는 방법만 넘기는** 점은 같습니다. 값이 있으면 예외는 만들어지지 않습니다.

`Optional` 안쪽에서도 같은 표기가 그대로 쓰입니다.

```java
Optional<String> title = boardRepository.findById(id).map(BoardEntity::getTitle);
title.ifPresent(System.out::println);
```

### 2-3. 정렬 기준과 맵 만들기

기준을 넘기는 자리마다 메소드 레퍼런스가 들어갑니다.

```java
// 제목 오름차순
list.stream().sorted(Comparator.comparing(BoardDto::getTitle)).toList();

// 작성일 내림차순, 같으면 제목 순
list.stream().sorted(
        Comparator.comparing(BoardDto::getCreatedAt).reversed()
                .thenComparing(BoardDto::getTitle)
).toList();

// 번호를 키로 하는 맵
Map<Integer, BoardDto> map = list.stream()
        .collect(Collectors.toMap(BoardDto::getId, Function.identity()));
```

`Comparator.comparing` 은 "무엇으로 비교할지"를 함수로 받습니다. 앞 노트에서 `Comparator.reverseOrder()` 로 통째 뒤집던 것과 달리, **어떤 필드로 정렬할지 고를 수 있는 것**이 이 표기의 값어치입니다.

`Function.identity()` 는 `(x) -> x` 를 표준으로 만들어 둔 것입니다. 받은 값을 그대로 돌려주는 함수라 "키만 뽑고 값은 원본 그대로"인 자리에 씁니다.

### 2-4. 자주 쓰는 표준 메소드 레퍼런스

외워 두면 손이 빨라지는 것들입니다.

| 표기 | 하는 일 | 자주 쓰는 자리 |
| --- | --- | --- |
| `Objects::nonNull` | `null` 이 아닌지 | `.filter(Objects::nonNull)` |
| `String::valueOf` | 문자열로 | `.map(String::valueOf)` |
| `Integer::parseInt` | 정수로 | 문자열 목록 변환 |
| `String::trim` | 앞뒤 공백 제거 | 입력값 다듬기 |
| `String::isBlank` | 비었는지 | `.filter(s -> !s.isBlank())` |
| `Function.identity()` | 그대로 | `toMap` 의 값 자리 |
| `클래스::new` | 만들기 | `map`·`orElseThrow` |

`isBlank` 처럼 **앞에 `!` 가 붙으면 줄일 수 없다**는 점은 조건 ①에 걸립니다. 부정이 필요하면 `Predicate.not(String::isBlank)` 으로 감싸는 갈래가 따로 있습니다.

## 3. 더 나아가 알면 좋은 것

### 3-1. 어느 생성자를 가리키는지는 받는 쪽이 정한다

`클래스::new` 는 생성자 이름을 적지 않습니다. 생성자가 여럿이면 어느 것인지 어떻게 정해지는지가 궁금해지는 자리입니다.

답은 **넘겨받는 자리의 타입**입니다.

```java
Supplier<Student> s = Student::new;          // 인수 0개짜리 생성자를 찾는다
Function<String, Student> f = Student::new;  // 인수 1개(String)짜리를 찾는다
```

같은 `Student::new` 인데 왼쪽 타입에 따라 다른 생성자로 이어집니다. 람다가 함수형 인터페이스의 추상 메소드 모양에 맞춰 해석되는 것과 같은 원리이고, 이것을 타겟 타이핑이라고 부릅니다. 맞는 생성자가 없으면 그 자리에서 컴파일 오류가 납니다.

배열도 같은 표기가 됩니다.

```java
Student[] arr = list.stream().toArray(Student[]::new);
```

### 3-2. `System.out::println` 이 잡아 두는 것

`객체::메소드` 모양은 **그 표현식을 만나는 순간 왼쪽 객체를 평가해서 붙들어 둡니다.**

```java
Consumer<String> printer = System.out::println;  // 이 시점의 System.out 을 잡는다
// 이후 System.setOut(...) 으로 출력 대상을 바꿔도 printer 는 옛 대상을 본다
```

`(x) -> System.out.println(x)` 로 적으면 부를 때마다 `System.out` 을 다시 읽으므로 성질이 갈립니다. 평소에는 차이가 드러나지 않지만, 대상을 바꿔 끼우는 코드가 섞이면 두 표기가 다르게 움직입니다. 이런 자리에서는 짧다는 이유로 고르지 않는 편이 안전합니다.

### 3-3. 스트림에서 `null` 이 흐를 때

`map(Student::new)` 처럼 조립을 짧게 적으면, 흐르는 값에 `null` 이 섞였을 때 어디서 터졌는지 알아보기 어려워집니다. 스택 트레이스에는 람다가 만든 합성 이름이 찍혀 원본 줄과 바로 이어지지 않습니다.

거르는 자리를 앞에 두는 편이 안전합니다.

```java
names.stream()
     .filter(Objects::nonNull)
     .filter(name -> !name.isBlank())
     .map(Student::new)
     .toList();
```

앞 노트에서 `filter` 를 체인 앞쪽에 두는 이유로 정리했던 "뒤 연산이 도는 횟수를 줄인다"에, "터질 값을 미리 뺀다"가 하나 더 붙는 자리입니다.

### 3-4. 값 객체와 `record`

실습의 `Student` 는 필드 하나와 생성자만 가진 클래스입니다. 값을 담는 것이 목적인 클래스는 자바 16부터 `record` 로 줄일 수 있습니다.

```java
record Student(String name) { }
```

생성자·`getter`(`name()`)·`equals`·`hashCode`·`toString` 이 함께 만들어집니다. 그러면 `Student::new` 도 그대로 성립하고, `distinct()` 나 `toMap` 이 제대로 도는 전제인 `equals`·`hashCode` 도 채워집니다. 다만 필드가 전부 `final` 이라 값을 바꿀 수 없고, JPA 엔티티는 기본 생성자와 필드 변경을 요구하므로 `record` 로 만들지 않습니다. **DTO에는 어울리고 엔티티에는 어울리지 않는** 갈림입니다.

### 3-5. 축약이 어디까지 갈 수 있는가

익명 구현체에서 시작해 여기까지 온 흐름을 한 자리에 놓으면 이렇습니다.

```java
// ① 익명 구현체
names.forEach(new Consumer<String>() {
    @Override
    public void accept(String name) {
        System.out.println(name);
    }
});
// ② 람다 (몸통 다 적기)
names.forEach((name) -> { System.out.println(name); });
// ③ 람다 (중괄호 생략)
names.forEach(name -> System.out.println(name));
// ④ 메소드 레퍼런스
names.forEach(System.out::println);
```

네 줄 다 같은 객체를 만들어 넘깁니다. ③에서 ④로 가는 칸만 조건이 붙고, 앞의 칸들은 언제나 갈 수 있습니다.

읽기에 좋은 지점은 코드마다 갈립니다. 짧은 것이 늘 좋은 것은 아니고, **매개변수 이름이 설명 노릇을 하고 있으면 ③에서 멈추는 편**이 읽는 사람에게 낫습니다. 팀에서 한 갈래로 맞춰 두면 코드 리뷰에서 표기 얘기를 반복하지 않아도 됩니다.

### 3-6. 다음에 볼 키워드

- `Predicate.not`·`Predicate.and`·`or` — 부정과 조합을 표준으로 만들어 둔 자리
- `Function.compose`·`andThen` — 함수 두 개를 이어 붙이기
- `Collectors.groupingBy`·`counting`·`joining` — 최종 연산의 나머지 갈래
- `flatMap` — 목록의 목록을 한 겹 펴기
- `Comparator.nullsFirst`·`nullsLast` — 정렬 기준에 `null` 이 섞일 때
- `record` 와 컴팩트 생성자 — 값 객체로 DTO 적기
- `invokedynamic` — 람다·메소드 레퍼런스가 클래스 파일에 남는 방식
- 타겟 타이핑 — 같은 표기가 받는 자리에 따라 다르게 해석되는 규칙
- `@FunctionalInterface` 를 직접 만들어 보기 — 표준 넷으로 안 되는 모양일 때

## 실습 파일

- `2026B_Spring/springweb/src/main/java/day08/exam/exam4.java` (**메소드 레퍼런스만 따로 떼어 람다와 나란히 적어 본 예제** — 같은 함수를 `(x) -> Integer.parseInt(x)` 와 `Integer::parseInt` 로 두 번 적어 타입도 결과도 같은 값이라는 확인, `::` 뒤에 괄호를 붙이지 않는 이유가 "지금 실행하는 것이 아니라 나중에 실행할 메소드를 가리키는 값"이기 때문이라 인수가 아직 없는 자리, 이름 네 개짜리 불변 리스트를 일반 `for`·향상된 `for`·`stream().forEach` + 람다·`stream().forEach(System.out::println)` 네 표기로 돌며 위에서 아래로 갈수록 "어떻게 도는가"가 사라지고 "무엇을 할 것인가"만 남는 대비와 3)→4)에서 지워진 것이 매개변수 이름과 중괄호뿐이라는 실측, `map((name) -> name.length())` 을 `map(String::length)` 로 줄이며 `Integer::parseInt` 와 표기는 같은 `클래스::메소드` 인데 한쪽은 넘어온 값이 인수로 한쪽은 부르는 주체로 들어가는 갈림과 그 판정을 컴파일러가 `static` 여부로 하는 자리, 메소드 레퍼런스 네 모양(`클래스::정적메소드`·`객체::인스턴스메소드`·`클래스::인스턴스메소드`·`클래스::new`)의 표와 2행·3행이 "부를 객체가 이미 정해져 있는가"로 갈리는 정리, 문자열마다 `Student` 객체를 만드는 일을 전통 `for`·스트림+람다·`Student::new` 세 표기로 적어 담을 그릇과 넣는 일이 `toList()` 로 넘어가고 결과가 불변이 되는 대비, **줄일 수 있는 조건 두 줄**(몸통이 호출 하나일 것·받은 매개변수가 가공 없이 그대로 넘어갈 것)과 가공·연산·리터럴·여러 문장이 끼면 람다로 남는 네 반례, `map(BoardDto::from)` 이 `static` 이라 1행 모양이고 `map(BoardDto::toEntity)` 는 3행 모양이라 같은 클래스의 두 변환 메소드가 표의 다른 행에 놓이는 정리, `orElseThrow(IllegalArgumentException::new)` 의 생성자 참조와 메시지가 붙으면 람다로 남는 갈림, `Comparator.comparing(BoardDto::getTitle)`·`Collectors.toMap(BoardDto::getId, Function.identity())` 처럼 기준을 넘기는 자리들, `Objects::nonNull`·`String::trim` 등 표준 표기 표와 `!` 가 붙으면 줄일 수 없어 `Predicate.not` 으로 감싸는 갈래, `클래스::new` 가 어느 생성자를 가리키는지는 받는 쪽 타입이 정한다는 타겟 타이핑과 `Supplier`·`Function` 대비·`Student[]::new`, `System.out::println` 이 표현식을 만나는 순간의 객체를 붙들어 둬 나중에 출력 대상을 바꿔도 옛 대상을 보는 자리와 람다로 적었을 때와 갈리는 점, 조립이 짧아진 만큼 `null` 이 섞였을 때 터진 자리를 찾기 어려워져 `filter(Objects::nonNull)` 을 앞에 두는 습관, `record` 로 값 객체를 줄이면 `equals`·`hashCode` 가 채워져 `distinct`·`toMap` 의 전제가 함께 해결되지만 필드가 `final` 이라 엔티티에는 안 맞는 갈림, 익명 구현체→람다→중괄호 생략→메소드 레퍼런스 네 칸을 한 자리에 놓고 마지막 칸만 조건이 붙는다는 정리와 매개변수 이름이 설명 노릇을 하면 한 칸 앞에서 멈추는 편이 낫다는 판단 기준)

## 관련 노트

[[Spring MOC]] · [[Spring day08 컬렉션 순회와 스트림 API]] · [[KDT_2026 학습 지도]]
