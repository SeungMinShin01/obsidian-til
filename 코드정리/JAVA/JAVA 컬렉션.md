---
출처: Claude 분석
작성일: 2026-08-21
tags: [코드정리]
---

# JAVA 컬렉션

> 상위: [[JAVA]]
> 세부: [[JAVA Stream 심화]] · [[JAVA Queue와 스택]]

## ArrayList

```java
import java.util.ArrayList;

ArrayList<String> list = new ArrayList<>();

list.add("A");
list.add(1, "B");
list.set(1, "C");
list.get(0);
list.remove(0);
list.size();
list.indexOf("A");
list.contains("A");
list.isEmpty();
list.clear();
```

- 배열의 고정 길이 한계를 푸는 가변 리스트다. `<제네릭>`에 담을 요소의 타입을 적는다
- `add(값)` 끝에 추가 / `add(i, 값)` i번째에 끼워 넣기(뒤가 밀리고 크기 +1) / `set(i, 값)` 덮어쓰기(크기 그대로) — add와 set 구분이 자주 헷갈린다
- `get(i)` 조회, `remove(i)` 삭제, `size()` 개수, `indexOf` 위치(없으면 -1), `contains` 포함 여부
- 길이 셋 비교: 배열 `arr.length`(필드) / 리스트 `list.size()`(메소드) / 문자열 `str.length()`(메소드)
- 제네릭에 기본 타입은 못 넣는다. `ArrayList<Integer>`처럼 래퍼 클래스를 쓴다(자동 변환 = 오토박싱)
- 입력 개수를 미리 모르는 상황이 리스트를 쓰는 이유다. 배열이면 크기부터 막힌다

## 내 클래스 담기

```java
ArrayList<Book> books = new ArrayList<>();
books.add(new Book("제목1", "저자1"));

for (Book b : books) {
    System.out.println(b);
}
```

- 제네릭에 직접 만든 클래스를 넣는 순간 실전 형태가 된다(게시글 목록, 회원 목록)
- 그대로 출력하면 주소가 나오니 Book에 `toString()`을 오버라이딩해 둔다
- 부모(인터페이스) 타입으로 선언하는 습관: `List<Book> books = new ArrayList<>();` — 나중에 구현체를 바꿔도 쓰는 코드가 그대로다

## 순회 중 삭제의 함정

```java
for (int i = list.size() - 1; i >= 0; i--) {
    if (조건) list.remove(i);
}

list.removeIf(b -> b.getWriter().equals("탈퇴회원"));
```

- 앞에서부터 돌며 remove하면 요소가 당겨져 다음 요소를 건너뛴다. **뒤에서부터** 돌면 안전하다
- `removeIf(조건람다)`가 가장 깔끔하다. 향상된 for문 안에서 remove하면 `ConcurrentModificationException`이 난다
- `ArrayList<Integer>`에서 `remove(1)`은 값 1이 아니라 **인덱스 1**을 지운다. 값으로 지우려면 `remove(Integer.valueOf(1))`

## 정렬

```java
import java.util.Collections;
import java.util.Comparator;

Collections.sort(list);
list.sort(Comparator.reverseOrder());
list.sort(Comparator.comparing(b -> b.getNo()));
list.sort(Comparator.comparing(Book::getNo).reversed());
```

- `Collections.sort`는 오름차순 기본이다(문자열은 사전순)
- 객체 리스트는 `Comparator.comparing(기준 람다)`으로 어떤 필드로 정렬할지 정한다. `.reversed()`를 붙이면 역순(최신순 정렬에 자주 쓴다)
- `Book::getNo`는 `b -> b.getNo()`의 축약(메소드 참조)이다

## Map ※

```java
import java.util.HashMap;
import java.util.Map;

Map<Integer, Book> map = new HashMap<>();
map.put(1, book);
Book b = map.get(1);
map.containsKey(1);
map.remove(1);

for (Map.Entry<Integer, Book> e : map.entrySet()) {
    System.out.println(e.getKey() + " → " + e.getValue());
}
```

- 키-값 쌍 저장소다. "번호로 찾기"가 리스트의 `indexOf`(O(n))보다 압도적으로 빠르다(`get` O(1))
- `put` 저장(같은 키면 덮어씀), `get` 조회(없으면 null), `containsKey` 존재 확인
- 순회는 `entrySet()`(키+값), `keySet()`(키만), `values()`(값만)
- JS의 객체 `{ }`와 같은 개념이다

## Set ※

```java
import java.util.HashSet;
import java.util.Set;

Set<String> set = new HashSet<>();
set.add("A");
set.add("A");
set.contains("A");

Set<String> unique = new HashSet<>(list);
```

- 중복을 허용하지 않는 집합이다. 같은 값을 두 번 add해도 하나만 남는다
- 리스트를 통째로 넣으면 중복 제거가 한 줄이다
- 순서가 필요하면 `LinkedHashSet`(입력순), 정렬이 필요하면 `TreeSet`

## 컬렉션 지도

```
Collection
├── List   순서 O, 중복 O  → ArrayList, LinkedList
├── Set    순서 X, 중복 X  → HashSet, TreeSet
└── Queue  선입선출        → ArrayDeque, PriorityQueue
Map        키-값            → HashMap, TreeMap
```

- 순서 있는 목록이면 List, 번호(키)로 찾으면 Map, 중복 제거면 Set — 이 셋이 실전의 대부분이다

