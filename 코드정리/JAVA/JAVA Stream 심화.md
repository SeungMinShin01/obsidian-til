---
출처: Claude 분석
작성일: 2026-08-21
tags: [코드정리]
---

# JAVA Stream 심화

> 상위: [[JAVA 컬렉션]]

전부 ※. filter·map·toList 기본형 다음 단계 — 정렬·중복 제거·묶기·이어붙이기.

## 중간 연산 더

```java
books.stream()
    .sorted(Comparator.comparing(Book::getPrice).reversed())
    .distinct()
    .limit(5)
    .skip(1)
    .toList();
```

- `sorted(비교자)` 정렬, `distinct()` 중복 제거(equals 기준), `limit(n)` 앞 n개, `skip(n)` 앞 n개 건너뛰기
- "가격 비싼 순 TOP5"가 sorted + limit 두 줄이다. 인기 도서 랭킹이 이 모양이 된다

## collect — 리스트 밖의 수확

```java
import java.util.stream.Collectors;

Map<String, List<Book>> byAuthor = books.stream()
    .collect(Collectors.groupingBy(Book::getAuthor));

Map<String, Long> countByAuthor = books.stream()
    .collect(Collectors.groupingBy(Book::getAuthor, Collectors.counting()));

String titles = books.stream()
    .map(Book::getTitle)
    .collect(Collectors.joining(", "));
```

- `groupingBy(기준)`은 SQL의 GROUP BY다. "저자별로 묶기"가 한 줄이고, 두 번째 인자로 `counting()`을 주면 저자별 개수까지 나온다
- `joining(구분자)`은 문자열 이어붙이기의 수확 버전이다
- 읽는 법: collect는 "흐른 결과를 어떤 그릇에 담을까"의 지정이다

## 숫자 스트림

```java
int total = books.stream().mapToInt(Book::getPrice).sum();
OptionalDouble avg = books.stream().mapToInt(Book::getPrice).average();
IntStream.rangeClosed(1, 9).forEach(i -> System.out.println(3 * i));
```

- `mapToInt`로 숫자 전용 스트림으로 바꾸면 `sum` `average` `max` `min`이 열린다
- `IntStream.range(0, n)` / `rangeClosed(1, n)`은 for문의 스트림 버전이다(끝 포함 여부 차이)

## 언제 안 쓰나

- 반복 중에 바깥 변수를 바꾸거나(부수효과), 인덱스가 꼭 필요하거나, 중간에 break해야 하면 그냥 for문이 낫다
- 스트림은 "각 요소를 독립적으로 거르고 변환해 모은다"에 최적이다. 그 모양이 아니면 억지로 쓰지 않는다
