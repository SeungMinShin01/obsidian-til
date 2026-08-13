---
출처: Claude 분석
원본: KDT_2026/2026B_BE/src/day09
작성일: 2026-08-10
tags: [학습, java]
---

# Java day09 — ArrayList

> 실습 파일: `day09/exam/exam1.java`, `day09/practice/practice11.java`
> 허브: [[Java MOC]] · 이전: [[Java day08 접근제한자와 static]] · 함께: [[Java day09 MVC 종합예제]] · 다음: [[Java day10 상속과 다형성]]

## 1. 배운 내용

### 1-1. ArrayList란

배열의 "고정 길이" 한계를 푸는 **컬렉션 프레임워크** 클래스입니다.

```java
import java.util.ArrayList;

ArrayList<String> 변수명1 = new ArrayList<>();
```

핵심은 세 가지입니다.
1. 컬렉션(수집) 프레임워크 — 자료 수집 관련 클래스·기능 제공
2. 목적 — 가변 길이, 배열 관련 기능(메소드) 제공
3. `<제네릭타입>` — 리스트에 저장할 요소의 타입

**제약**: 제네릭에는 기본 타입을 넣을 수 없습니다.
```java
ArrayList<int> list;       // 컴파일 에러
ArrayList<Integer> list;   // 정답
```
자바가 자동으로 감싸주는 걸 **오토박싱**이라고 합니다. → [[Java day02 타입 변환]]

### 1-2. 주요 메소드 12가지

| 메소드 | 역할 | 배열 / JS 대응 |
| --- | --- | --- |
| `.add(값)` | 끝에 추가 | JS `push` |
| `.add(i, 값)` | i번째에 삽입 | JS `splice(i, 0, 값)` |
| `.set(i, 값)` | i번째 수정 | `arr[i] = 값` |
| `.get(i)` | i번째 조회 | `arr[i]` |
| `.remove(i)` | i번째 삭제 | JS `splice(i, 1)` |
| `.size()` | 개수 | `.length` |
| `.indexOf(값)` | 위치 (없으면 -1) | 동일 |
| `.contains(값)` | 존재 여부 | JS `includes` |
| `.clear()` | 전체 삭제 | `arr = []` |
| `.isEmpty()` | 비었는지 | `.length === 0` |

```java
ArrayList<String> list = new ArrayList<>();
list.add("유재석");
list.add(1, "하하");        // 중간 삽입
list.set(1, "서장훈");      // 수정
System.out.println(list.size());
System.out.println(list.get(1));
list.remove(1);
System.out.println(list.indexOf("강호동"));   // -1 (없음)
list.clear();
System.out.println(list.isEmpty());          // true
```

**길이 확인 메소드가 셋 다 다릅니다.**
```java
arr.length      // 배열 — 필드
list.size()     // 컬렉션 — 메소드
str.length()    // 문자열 — 메소드
```

### 1-3. 반복문과 리스트

```java
// 1. 일반 for문 — 인덱스가 필요할 때
for (int i = 0; i < list.size(); i++) { list.get(i); }

// 2. 향상된 for문 — 인덱스가 필요 없을 때 (권장)
for (String str : list) { }
```

### 1-4. 배열 vs ArrayList

| | 배열 | ArrayList |
| --- | --- | --- |
| 길이 | 고정 | 가변 (자동 확장) |
| 선언 | `new int[3]` | `new ArrayList<Integer>()` |
| 타입 | 기본 타입 가능 | 참조 타입만 (제네릭) |
| 추가·삭제 | 불가 | `add` / `remove` |
| 조회 | `arr[i]` | `list.get(i)` |
| 길이 | `arr.length` | `list.size()` |
| 출력 | `Arrays.toString(arr)` | `System.out.println(list)` |

`System.out.println(list)`가 바로 내용을 출력하는 이유는 `ArrayList`가 `toString()`을 오버라이딩해 뒀기 때문입니다. → [[Java day05 클래스와 인스턴스]]

### 1-5. practice11 — 리스트 실습 6문제

```java
// 1. 문자열 리스트
ArrayList<String> nameList = new ArrayList<>();
nameList.add("유재석"); nameList.add("강호동"); nameList.add("신동엽");
System.out.println(nameList);        // [유재석, 강호동, 신동엽]

// 2. 일반 for문 순회
for (int i = 0; i < fruits.size(); i++) System.out.println(fruits.get(i));

// 3. 향상된 for문 순회
for (String 변수명1 : fruits) System.out.println(변수명1);

// 4. 중간 삭제
list1.remove(2);                     // [A, B, D, E]

// 6. 객체 리스트
ArrayList<Book> bookList = new ArrayList<>();
bookList.add(new Book("책이름1", "저자1"));
bookList.add(new Book("책이름2", "저자2"));
```

`ArrayList<String>`을 그냥 출력하면 `[유재석, 강호동, 신동엽]`처럼 내용이 바로 나옵니다. 배열이 주소를 출력하던 것과 대비됩니다. → [[Java day04 제어문과 배열]]

**6번의 `ArrayList<Book>`이 가장 중요한 문제입니다.** 제네릭에 **내가 만든 클래스**를 넣는 순간, 리스트가 실전에서 쓰이는 형태가 됩니다.

```java
for (Book b : bookList) {
    System.out.println(b);           // toString()을 오버라이딩하지 않으면 주소가 출력
}
```

`Book`에 `toString()`을 추가하면 목록이 그대로 읽힙니다. → [[Java day05 클래스와 인스턴스]]

이게 [[Java day06 생성자와 콘솔 게시판]] 의 `Post[100]`을 `ArrayList<Post>`로 바꾸는 것과 같은 형태입니다.

## 2. 추가로 알면 좋은 활용법

### 2-1. 반복문 중 remove의 함정

```java
for (int i = 0; i < list.size(); i++) {
    if (조건) list.remove(i);   // 버그!
}
```

`[A, B, C]`에서 `i=0`일 때 A를 지우면 리스트가 `[B, C]`가 되고, `i=1`은 C를 가리켜 **B를 건너뜁니다.**

**해결 1** — 뒤에서부터 순회
```java
for (int i = list.size() - 1; i >= 0; i--) {
    if (조건) list.remove(i);
}
```

**해결 2** — `removeIf` (Java 8+, 가장 깔끔)
```java
list.removeIf(post -> post.writer.equals("탈퇴회원"));
```

향상된 for문 안에서 `remove`를 호출하면 `ConcurrentModificationException`이 납니다.

### 2-2. `remove(int)` vs `remove(Object)` 오버로딩 함정

```java
ArrayList<Integer> list = new ArrayList<>(List.of(10, 20, 30));
list.remove(1);                    // 인덱스 1 삭제 → 20 제거
list.remove(Integer.valueOf(10));  // 값 10 삭제
```

`Integer` 리스트에서만 생기는데 실무에서 자주 걸립니다.

### 2-3. 초기 용량 지정

`ArrayList`는 내부가 배열이라 꽉 차면 **1.5배 크기의 새 배열을 만들어 복사**합니다.

```java
new ArrayList<>();       // 기본 용량 10
new ArrayList<>(1000);   // 처음부터 1000 — 복사 비용 절약
```

### 2-4. 리스트 정렬

```java
Collections.sort(list);                              // 오름차순
list.sort(Comparator.reverseOrder());                // 내림차순
list.sort(Comparator.comparing(p -> p.no));          // 특정 필드 기준
list.sort(Comparator.comparing(Post::getNo).reversed());  // 역순
```

[[JS day13 웹 스토리지와 인터벌]] 의 최신글 정렬과 같은 목적입니다.

### 2-5. OverallController 리팩터링

[[Java day06 생성자와 콘솔 게시판]] 의 배열 100칸 버전을 다시 쓰면:

```java
ArrayList<Post> posts = new ArrayList<>();

// 글쓰기
posts.add(new Post(content, writer));

// 출력
for (Post post : posts) {
    System.out.printf("작성자 : %s , 내용 : %s%n", post.writer, post.content);
}
```

빈 칸 탐색 루프, `null` 검사, 실패 분기가 전부 사라집니다.

## 3. 더 나아가 알면 좋은 것

### 3-1. 컬렉션 프레임워크 지도

```
Collection
├── List   순서 O, 중복 O  → ArrayList, LinkedList
├── Set    순서 X, 중복 X  → HashSet, TreeSet(정렬), LinkedHashSet(입력순)
└── Queue  선입선출        → ArrayDeque, PriorityQueue

Map        키-값 쌍        → HashMap, TreeMap, LinkedHashMap
```

**Map이 필요한 순간**: 게시판에서 "글번호로 빠르게 찾기"가 필요하면 `List`보다 `Map`이 압도적으로 빠릅니다. `list.indexOf()`는 O(n), `map.get()`은 O(1)입니다.

```java
Map<Integer, Post> posts = new HashMap<>();
posts.put(1, new Post("내용", "작성자"));
Post p = posts.get(1);
```

JS 객체 `{ }`와 개념이 같습니다. → [[JS day07 객체]]

**Set이 필요한 순간**: 중복 제거.
```java
Set<String> unique = new HashSet<>(list);
```

### 3-2. Stream API

```java
List<Post> mine = posts.stream()
    .filter(p -> p.writer.equals("유재석"))
    .toList();

List<String> titles = posts.stream().map(p -> p.content).toList();

long count = posts.stream().filter(p -> p != null).count();

int total = nums.stream().mapToInt(Integer::intValue).sum();
```

`for` + `if` + `add` 3단 구조가 한 줄이 됩니다. JS의 `filter`/`map`/`reduce`와 같은 개념입니다. → [[JS day05 반복문]]

### 3-3. 불변 리스트

```java
List<String> fixed = List.of("A", "B", "C");   // 수정 불가
fixed.add("D");   // UnsupportedOperationException
```

바뀌면 안 되는 데이터는 불변으로 두면 실수를 컴파일·런타임에 잡을 수 있습니다.

### 3-4. 다음 단계 — 영속화

현재는 프로그램을 끄면 데이터가 사라집니다.

```
메모리 (ArrayList)
    ↓ 파일 저장
java.nio.file.Files + JSON
    ↓ DB 연동
JDBC + MySQL           ← database/*.sql이 이미 준비됨
    ↓ 웹으로
Spring Boot + JPA
```

[[JS day13 웹 스토리지와 인터벌]] 이 `localStorage`로 해결한 문제를 백엔드에서는 DB로 해결합니다. **프론트의 localStorage ≒ 백엔드의 DB** — 같은 문제의 다른 답입니다.

## 실습 파일

- `2026B_BE/src/day09/exam/exam1.java`
- `2026B_BE/src/day09/practice/practice11.java`

## 관련 노트

[[Java MOC]] · [[Java day08 접근제한자와 static]] · [[Java day04 제어문과 배열]] · [[Java day06 생성자와 콘솔 게시판]] · [[SQL day03 DML과 조인]]
