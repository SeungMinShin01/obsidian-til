---
출처: Claude 분석
작성일: 2026-08-21
tags: [코드정리]
---

# JAVA AI 관용구

> 상위: [[JAVA]]


AI가 생성한 코드에 유독 자주 나오는, **짧지만 의미가 함축된 표현**들의 해독표다. 전부 ※(수업 밖)라고 보면 되고, 읽을 줄만 알아도 AI 코드가 훨씬 잘 보인다.

## 가드 절 — 먼저 거르고 일찍 나가기

```java
public boolean rent(int memberNo, int bookNo) {
    if (memberNo <= 0) return false;
    if (findBook(bookNo) == null) return false;

    // 여기부터는 정상 케이스만 남는다
    ...
}
```

- if를 중첩해 파고드는 대신, **비정상 케이스를 위에서 하나씩 쳐내고 바로 return** 한다
- 아래로 갈수록 "여기 도달했다 = 위 조건은 전부 통과했다"가 보장돼 본문이 평평해진다
- AI 코드의 메소드 첫 부분에 return이 여러 개 몰려 있으면 전부 이 패턴이다

## 삼항과 null 기본값

```java
String name = input != null ? input : "이름없음";
int no = list.isEmpty() ? 1 : list.get(list.size() - 1).getNo() + 1;
return count > 0;
```

- `A != null ? A : 기본값`은 "A가 있으면 A, 없으면 기본값" — null 대비 한 줄이다
- 두 번째 줄은 게시판 자동 번호의 관용형: 비었으면 1, 아니면 마지막 번호 + 1
- `return count > 0;`은 `if (count > 0) return true; else return false;` 4줄의 압축이다. 비교식 자체가 boolean이라 바로 반환한다

## Optional — null일 수도 있음을 타입으로 ※

```java
Optional<Book> found = list.stream().filter(b -> b.getNo() == no).findFirst();
Book book = found.orElse(null);
String title = found.map(Book::getTitle).orElse("(없음)");
```

- `Optional<T>`는 "T가 있을 수도, 없을 수도"를 감싼 상자다. null을 직접 다루다 터지는 걸 막으려는 장치다
- `orElse(기본값)` = 있으면 꺼내고 없으면 기본값. `isPresent()` = 있는지 확인. `map(...)` = 있으면 변환
- AI가 `findFirst()`·`findAny()` 뒤에 붙이는 `.orElse(...)` 체인이 이것이다

## Stream — for·if·add 3단을 한 줄로 ※

```java
List<Book> mine = books.stream()
        .filter(b -> b.getWriter().equals("유재석"))
        .toList();

List<String> titles = books.stream().map(Book::getTitle).toList();

long cnt = books.stream().filter(b -> b.getPrice() > 10000).count();
int total = books.stream().mapToInt(Book::getPrice).sum();
boolean any = books.stream().anyMatch(b -> b.getStock() == 0);
```

- `stream()`으로 흐름을 열고, 중간 연산을 점으로 잇고, 마지막에 결과로 닫는 구조다
- `filter(조건)` 거르기 = for+if / `map(변환)` 각 요소 바꾸기 / `toList()` 리스트로 수확
- `count` 개수, `sum` 합계, `anyMatch` 하나라도 있나, `allMatch` 전부 그런가
- JS의 `filter`/`map`/`reduce`와 같은 개념이다. 읽는 법: "books에서 → 유재석 것만 걸러 → 리스트로"
- `Book::getTitle`은 `b -> b.getTitle()`의 축약(메소드 참조)이다. `클래스::메소드` 꼴이 보이면 람다로 풀어 읽으면 된다

## Map 한 줄 관용구 ※

```java
int c = countMap.getOrDefault(key, 0);
countMap.put(key, countMap.getOrDefault(key, 0) + 1);
groupMap.computeIfAbsent(category, k -> new ArrayList<>()).add(book);
countMap.merge(key, 1, Integer::sum);
```

- `getOrDefault(키, 기본값)` = 키가 없어도 null 대신 기본값. 개수 세기의 정석이다(2번째 줄)
- `computeIfAbsent(키, k -> 새값)` = 키가 없으면 만들어 넣고, 그걸 반환한다. "카테고리별로 묶기"가 한 줄이 된다 — 없으면 빈 리스트를 만들고, 있으면 기존 리스트에 add
- `merge(키, 1, Integer::sum)` = 키가 없으면 1, 있으면 기존 값과 합침. 역시 카운팅 압축형
- 이 세 줄이 없으면 전부 "if (containsKey) ... else ..." 4~6줄짜리 코드다

## 불변 생성 — List.of, Map.of ※

```java
List<String> menu = List.of("아메리카노", "라떼");
Map<String, Integer> price = Map.of("아메리카노", 4500, "라떼", 5000);
```

- 고정 데이터를 즉석에서 만드는 축약이다. 단 **수정 불가**라 `add`하면 `UnsupportedOperationException`이 난다
- AI가 테스트 데이터·초기 메뉴를 만들 때 즐겨 쓴다. 수정할 거면 `new ArrayList<>(List.of(...))`로 감싼다

## var — 타입 추론 ※

```java
var list = new ArrayList<BookDto>();
var scan = new Scanner(System.in);
```

- 지역 변수에 한해 우변을 보고 타입을 추론한다. 타입이 우변에 명확할 때만 쓰는 게 좋다
- 안 보이는 타입이 아니라 **안 쓴** 타입이다. 컴파일 시점에 확정된다

## record — DTO 한 줄 ※

```java
record BookDto(int no, String title, String author) { }

BookDto b = new BookDto(1, "제목", "저자");
int no = b.no();
```

- 생성자·getter·equals·hashCode·toString이 전부 자동 생성된다. DTO 관례 4가지 중 setter만 없다(불변)
- getter 이름이 `getNo()`가 아니라 필드명 그대로 `no()`인 게 특징이다
- AI가 "데이터만 담는 클래스"를 만들 때 class 대신 record를 자주 택한다

## Objects 유틸 ※

```java
if (Objects.equals(a, b)) { }
this.title = Objects.requireNonNull(title, "제목은 필수");
```

- `Objects.equals(a, b)`는 a가 null이어도 안전한 equals다(`a.equals(b)`는 a가 null이면 터진다)
- `requireNonNull(값, 메시지)`는 null이면 즉시 NullPointerException을 던진다. 생성자 첫 줄에서 "이 값은 null 금지"를 선언하는 관용구다

## String.join과 반복 없는 조립 ※

```java
String csv = String.join(", ", names);
String line = "-".repeat(30);
```

- `join(구분자, 목록)`은 for로 이어 붙이던 것을 한 줄로 만든다(마지막 구분자 처리도 자동)
- `"-".repeat(30)`은 구분선 30칸이다. 콘솔 메뉴 출력에서 자주 보인다

## 종합 — AI 스타일 메소드 읽기

```java
public List<String> overdueTitles(List<Rental> rentals) {
    if (rentals == null || rentals.isEmpty()) return List.of();

    return rentals.stream()
            .filter(r -> r.getReturnDate() == null)
            .filter(r -> r.getDueDate().isBefore(LocalDate.now()))
            .map(r -> r.getBook().getTitle())
            .toList();
}
```

- 1행: 가드 절 — null·빈 목록이면 빈 리스트 반환(null을 반환하지 않는 것도 관용이다. 받는 쪽의 null 검사를 없애준다)
- 3~6행: 스트림 — "대여 목록에서 → 미반납만 → 기한 지난 것만 → 제목으로 바꿔 → 리스트로"
- 같은 일을 for+if 중첩으로 쓰면 12줄쯤 된다. 압축된 게 아니라 **단계가 이름으로 드러난** 것이라, 읽는 법만 알면 오히려 이쪽이 명세서에 가깝다

