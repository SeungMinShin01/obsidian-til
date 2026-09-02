---
출처: Claude 분석
원본: KDT_2026/2026B_BE/src/day06
작성일: 2026-08-10
tags: [학습, java]
---

# Java day06 — 생성자와 콘솔 게시판

> 실습 파일: `day06/exam/exam1.java`(생성자), `day06/practice/OverallController.java`(게시판), `practice8.java`, `test.java`
> 허브: [[Java MOC]] · 이전: [[Java day05 클래스와 인스턴스]] · 다음: [[Java day07 메소드와 미니프로젝트]]

## 1. 배운 내용

### 1-1. 생성자 — exam1.java

```java
class Phone {
    String model;   // 1. 멤버변수
    String color;
    int price;

    Phone() { }                                  // 2-1. 기본생성자
    Phone(String model, String color) {          // 2-2. 정의생성자
        this.model = model;
        this.color = color;
    }
    Phone(String model, String color, int 가격) { // 오버로딩
        this.model = model;
        this.color = color;
        price = 가격;
    }
    // 3. 메소드
}
```

**선언 규칙 3가지**
1. 클래스 내부에 선언
2. 클래스명과 동일한 이름
3. 오버로딩 지원 — 매개변수의 개수/타입/순서가 다르면 같은 이름으로 여러 개

**목적 2가지**
1. 빠른 초기화
2. 객체 생성 규칙 / 유효성 검사

**종류**
- 기본 생성자 — 매개변수 없음
- 정의 생성자 — 매개변수 있음

**중요한 함정**: 생성자를 **하나도 안 쓰면** 컴파일러가 기본 생성자를 자동으로 만들어줍니다. 하지만 정의 생성자를 **하나라도 만들면 기본 생성자는 자동 생성되지 않습니다.**

```java
class Phone {
    Phone(String model) { ... }   // 정의 생성자만 있음
}
new Phone();   // 컴파일 에러!
```

필요하면 `Phone() { }` 를 직접 선언해야 합니다. 그래서 정의 생성자를 만들 때는 기본 생성자도 같이 두는 편이 안전합니다.

### 1-2. this

매개변수명과 멤버변수명이 같을 때 **멤버변수를 가리키는 식별자**입니다.

```java
Phone(String model, String color) {
    this.model = model;   // this.model = 멤버변수, model = 매개변수
    this.color = color;
}
```

세 번째 생성자에서 `price = 가격;`처럼 이름이 다르면 `this`를 생략해도 됩니다. 다만 **항상 붙이는 습관**이 안전합니다.

**메소드와 생성자의 차이**: 메소드는 반환값이 있지만, 생성자는 반환 타입 자체가 없습니다. 실제로는 생성된 객체의 주소값이 돌아갑니다.

### 1-3. OverallController — 배열 기반 콘솔 게시판

```java
Post[] posts = new Post[100];       // 고정 크기 100
Scanner scan = new Scanner(System.in);

for (;;) {                          // 무한 메뉴 루프
    System.out.println("1.게시물쓰기 2.게시물출력");
    int ch = scan.nextInt();

    if (ch == 1) {
        scan.nextLine();            // 버퍼 비우기
        String content = scan.nextLine();
        String writer = scan.nextLine();

        Post post = new Post(content, writer);
        boolean result = false;

        for (int index = 0; index <= posts.length - 1; index++) {
            if (posts[index] == null) {   // 빈 칸 찾기
                posts[index] = post;
                result = true;
                break;                     // 첫 빈 칸에만 저장
            }
        }
        System.out.println(result ? "[안내] 글쓰기 성공" : "[안내] 글쓰기 실패");

    } else if (ch == 2) {
        for (Post post : posts) {
            if (post != null) {            // null 아닌 것만 출력
                System.out.printf("작성자 : %s , 내용 : %s %n", post.writer, post.content);
            }
        }
    }
}
```

**핵심 아이디어**: 배열은 크기를 못 늘리니까 100칸을 미리 잡고 `null`인 자리를 "빈 칸"으로 취급합니다.

`break`가 반드시 필요합니다. 없으면 뒤의 모든 칸에 같은 글이 들어갑니다.

**같은 발상의 다른 구현**: JS 과제 LevelUP과 게시판 의 `Message_Board`에서 `index = -1`을 빈 칸으로 쓴 것과 완전히 같습니다. 언어가 달라도 문제 해결 구조는 같습니다.

`Post` 클래스가 day05에서 배운 설계 클래스, `OverallController`가 실행 클래스입니다. `Post`에 기본 생성자와 정의 생성자를 둘 다 둔 것도 day06 내용 그대로입니다.

### 1-4. practice8 — day05의 클래스를 생성자로 다시 쓰기

`day06/practice/practice8.java`는 [[Java day05 클래스와 인스턴스]] 에서 만든 클래스를 **생성자 버전으로 다시 작성**한 파일입니다.

```java
// day05 방식 — 만들고 나서 하나씩 대입
Book b1 = new Book();
b1.title = "이것이 자바다";
b1.author = "신용권";
b1.price = 30000;

// day06 방식 — 만들면서 한 번에
Book b1 = new Book("이것이 자바다", "신용권", 30000);
```

4줄이 1줄이 되고, **초기화를 빼먹을 수 없게** 됩니다. 이게 생성자의 첫 번째 목적인 "빠른 초기화"입니다.

```java
class Book {
    String title; String author; int price;
    Book(String title, String author, int price) {
        this.title = title;
        this.author = author;
        this.price = price;
    }
}
```

**기본생성자와 정의생성자를 함께 둔 예**
```java
Goods g1 = new Goods();                 // 기본생성자
Goods g2 = new Goods("콜라", 2000);      // 정의생성자
System.out.printf("기본생성자: %s %d \n매개변수 생성자: %s %d \n",
                  g1.name, g1.price, g2.name, g2.price);
```

`g1`은 값을 안 넣었으므로 `null`과 `0`이 출력됩니다. **참조 타입의 기본값은 `null`, 정수는 `0`** 이라는 걸 눈으로 확인하는 예제입니다.

```java
Member m1 = new Member();
System.out.printf("%s %b \n", m1.id, m1.isLogin);   // null false
```

`boolean`의 기본값이 `false`라는 것도 함께 확인됩니다. → Java day01 자바 구조와 자료형

## 2. 추가로 알면 좋은 활용법

### 2-1. `this()` — 생성자에서 생성자 호출

exam1.java의 세 생성자가 같은 대입을 반복합니다.

```java
class Phone {
    String model;
    String color;
    int price;

    Phone() {
        this("미정", "미정", 0);           // 다른 생성자 호출
    }
    Phone(String model, String color) {
        this(model, color, 0);
    }
    Phone(String model, String color, int price) {   // 실제 초기화는 여기서만
        this.model = model;
        this.color = color;
        this.price = price;
    }
}
```

`this()`는 **생성자의 첫 줄**에만 올 수 있습니다. 초기화 로직이 한 곳에 모여서 유지보수가 쉬워집니다.

### 2-2. 생성자에서 유효성 검사

생성자의 목적 중 하나가 "객체 생성 규칙"입니다.

```java
Post(String content, String writer) {
    if (content == null || content.isBlank()) {
        throw new IllegalArgumentException("내용은 비어 있을 수 없습니다.");
    }
    this.content = content;
    this.writer = writer;
}
```

**잘못된 상태의 객체가 아예 만들어지지 않게** 막는 게 핵심입니다. 나중에 검사하는 것보다 훨씬 강력합니다. → Java day08 접근제한자와 static 의 setter 검증과 같은 맥락입니다.

## 3. 더 나아가 알면 좋은 것

### 3-1. ArrayList로 리팩터링

day09를 배운 뒤 다시 쓰면 코드가 극적으로 줄어듭니다.

```java
ArrayList<Post> posts = new ArrayList<>();

// 글쓰기 — 빈 칸 탐색 루프가 통째로 사라짐
posts.add(new Post(content, writer));
System.out.println("[안내] 글쓰기 성공");

// 출력 — null 체크 불필요
for (Post post : posts) {
    System.out.printf("작성자 : %s , 내용 : %s%n", post.writer, post.content);
}
```

100칸 제한도, `null` 검사도, "글쓰기 실패" 분기도 전부 없어집니다. **자료구조를 바꾸면 로직이 사라진다** — 이게 컬렉션을 배우는 이유입니다. → Java day09 ArrayList

### 3-2. 게시판을 CRUD로 완성하기

지금은 C(생성)와 R(조회)만 있습니다.

```java
// U — 수정
Post target = findByNo(no);
if (target != null) target.content = 새내용;

// D — 삭제
posts[index] = null;   // 배열이면 null로
posts.remove(index);   // ArrayList면
```

프론트 버전은 JS day14 게시판 CRUD 에서 완성됩니다. 두 코드를 나란히 놓고 보면 CRUD의 본질이 보입니다.

### 3-3. Post에 필드 추가하기

실제 게시판이 되려면 `no`(글번호), `createdAt`(작성일), `pwd`(비밀번호)가 필요합니다.

```java
class Post {
    int no;
    String content;
    String writer;
    LocalDateTime createdAt = LocalDateTime.now();
}
```

`no`는 static 카운터로 자동 증가시킬 수 있습니다.
```java
static int seq = 0;
Post(String content, String writer) {
    this.no = ++seq;   // 인스턴스가 만들어질 때마다 1씩
    ...
}
```

이게 SQL day02 테이블과 제약조건 의 `AUTO_INCREMENT`를 자바로 흉내낸 것이고, JS day14 게시판 CRUD 의 `마지막.no + 1`과 같은 목적입니다.

## 실습 파일

- `2026B_BE/src/day06/exam/exam1.java`
- `2026B_BE/src/day06/practice/OverallController.java`, `practice8.java`, `test.java`
- `2026B_BE/src/day06/test/test.java`

## 관련 노트

[[Java MOC]] · [[Java day05 클래스와 인스턴스]] · [[Java day07 메소드와 미니프로젝트]] · Java day09 ArrayList · JS day14 게시판 CRUD
