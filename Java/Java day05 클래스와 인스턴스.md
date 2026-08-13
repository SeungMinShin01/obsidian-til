---
출처: Claude 분석
원본: KDT_2026/2026B_BE/src/day05, src/Note/day04.txt
작성일: 2026-08-10
tags: [학습, java]
---

# Java day05 — 클래스와 인스턴스

> 실습 파일: `day05/exam/exam1.java`, `day05/practice/txt`, `Note/day04.txt`
> 허브: [[Java MOC]] · 이전: [[Java day04 제어문과 배열]] · 다음: [[Java day06 생성자와 콘솔 게시판]]

## 1. 배운 내용

### 1-1. 객체지향의 뼈대 — Note/day04.txt

| 용어 | 의미 |
| --- | --- |
| **객체** | 상태(멤버변수/필드/속성)와 행위(메소드/함수)를 정의하는 것 |
| **클래스** | 상태와 행위를 코드로 작성한 설계도 |
| **인스턴스** | 특정 클래스로 `new` 해서 만든 실체 |

**주체(개발자) vs 객체(프로그램의 모든 대상)** 구분이 핵심입니다. 객체지향 프로그래밍이란 개발자가 컴퓨터 안에 다룰 대상을 만드는 일입니다.

**클래스의 두 가지 용도**
1. 설계 클래스 — 객체 정의용 (`Student`, `Phone`, `계산기`)
2. 실행 클래스 — `main`을 갖는 진입점 (`exam1`)

**폴더 구조**: `src`(개발자 코드 `.java`) / `bin`(컴파일된 바이트코드 `.class`)

### 1-2. 클래스 만들기 — exam1.java

```java
class Student {
    int StudentID;        // 멤버변수(인스턴스 변수)
    String studentName;
}
```

클래스를 만드는 두 가지 위치
1. 새 `.java` 파일 생성
2. 현재 파일의 `class { }` **밖**

**관례**
- 클래스 타입은 참조 타입입니다
- 클래스명은 첫 글자 대문자, 기본 타입과 변수명은 소문자로 시작
- `new`는 인스턴스화 — 힙(heap) 메모리를 할당합니다
- 생성자는 클래스명과 동일하며 메소드와 비슷한 역할

### 1-3. 객체 생성과 참조

```java
Student s1 = new Student();
System.out.println(s1);            // 클래스명@해시코드 ← 주소
System.out.println(s1.StudentID);  // 0    (int 기본값)
System.out.println(s1.studentName);// null (참조 기본값)

s1.studentName = "유재석";   // 객체변수명.멤버변수명 = 새로운값
s1.StudentID = 10;
```

**`.`(도트/접근/참조) 연산자**는 변수가 가리키는 주소로 이동한다는 뜻입니다. 변수가 `null`이면 이동할 주소가 없어서 `NullPointerException`이 납니다.

### 1-4. new 1개 = 인스턴스 1개

exam1.java의 핵심 실험입니다.

```java
Student s2 = new Student();   // 인스턴스 A
Student s3 = new Student();   // 인스턴스 B
Student s4 = s2;              // 새 인스턴스 X — s2와 같은 주소를 참조

s2.studentName = "강호동";
System.out.println(s4.studentName);   // "강호동"  ← s4도 같은 객체를 봄
```

`s2`, `s3`, `s4`를 그대로 출력하면 `s2`와 `s4`의 해시코드가 같고 `s3`만 다릅니다.

**객체는 변수가 참조하지 않으면 자동으로 사라집니다(GC).**

### 1-5. pracitce1 — 클래스 5개를 직접 설계

`day05/practice/pracitce1.java`에서 서로 다른 성격의 클래스 5개를 만들었습니다.

```java
class Book { String title; String author; int price; }
class Pet { String name; int age; String species; }
class Rectangle { int width; int height; }
class BankAccount { String accountNumber; String ownerName; int balance; }
class Product { ... }
```

```java
// 1. 상태 대입
Book b1 = new Book();
b1.title = "이것이 자바다";
b1.author = "신용권";
b1.price = 300000;

// 3. 멤버변수로 계산
Rectangle r1 = new Rectangle();
r1.width = 10;  r1.height = 5;
System.out.println(r1.width * r1.height);   // 50

// 4. 상태 변경 — 입출금
BankAccount bank1 = new BankAccount();
bank1.balance = 10000;
bank1.balance += 5000;    // 15000
bank1.balance -= 3000;    // 12000
```

**클래스마다 성격이 다릅니다.**

| 클래스 | 성격 |
| --- | --- |
| `Book`, `Pet` | 순수 데이터 보관 |
| `Rectangle` | 데이터로 계산 (넓이) |
| `BankAccount` | 상태가 계속 변함 (입출금) |

`BankAccount`의 `balance += 5000`처럼 **필드를 직접 조작**하는 방식이 day08에서 `deposit()` 메서드와 setter로 바뀝니다. 잔액이 음수가 되는 걸 막을 수 없다는 게 여기서의 한계입니다. → [[Java day08 접근제한자와 static]]

`Rectangle`의 넓이 계산도 지금은 `main`에 있지만, day07에서 `getArea()` 메서드로 클래스 안에 들어갑니다. → [[Java day07 메소드와 미니프로젝트]]

**day05 → day06 → day07 → day08이 같은 클래스를 계속 개선해가는 흐름**입니다.

## 2. 추가로 알면 좋은 활용법

### 2-1. Book 인스턴스 개수 추적

인스턴스가 몇 개 만들어지고 몇 개가 살아남는지 따라가 보겠습니다.

```java
Book b1 = new Book("Java Basics");       // ① 생성
Book b2 = new Book("OOP Concepts");      // ② 생성
Book[] library = new Book[3];            // 배열 객체 (Book 인스턴스 아님!)

library[0] = b1;                         // 참조 복사
library[1] = new Book("Data Structure"); // ③ 생성
Book b3 = library[1];                    // 참조 복사

b2 = library[0];                         // ② 가 참조를 잃음 → GC 대상

Book[] archive = library;                // 같은 배열 주소
archive[2] = new Book("Algorithm");      // ④ 생성 (= library[2])

library[0] = null;                       // ① 참조 하나 끊김
b1 = null;                               // ① 나머지 참조도 끊김 → GC 대상
```

- **생성된 Book 인스턴스: 4개** (①②③④)
- **끝까지 유효: 2개** — ③ `"Data Structure"`(library[1], b3가 참조), ④ `"Algorithm"`(library[2] = archive[2]가 참조)
- **참조를 잃어 GC 대상: 2개** — ① `"Java Basics"`, ② `"OOP Concepts"`

**핵심**: 배열 객체와 배열이 담는 객체는 별개입니다. `new Book[3]`은 Book 3개를 만드는 게 아니라 Book을 담을 **빈 칸 3개(전부 null)** 를 만듭니다. 인스턴스 개수를 셀 때 배열 자체를 함께 세지 않도록 주의합니다.

### 2-2. 가비지 컬렉터

`2026_FE/day03/memo`에서 던지신 질문의 답입니다.

| 언어 | 메모리 관리 |
| --- | --- |
| C | `malloc` / `free` 직접. 안 하면 **메모리 누수**, 두 번 하면 **double free** 크래시 |
| Java / JS / Python | 참조가 없는 객체를 **GC가 자동 회수** |

Java GC는 **Reachability(도달 가능성)** 기준입니다. GC Root(스택 지역변수, static 변수 등)에서 참조를 따라가 닿지 않는 객체를 회수합니다. 위 예제에서 `b1 = null`을 한 순간 `"Java Basics"`는 어디서도 도달할 수 없어 대상이 됩니다.

**Java에서도 메모리 누수는 납니다.** static 컬렉션에 계속 `add`만 하면 참조가 끊기지 않아 GC가 못 가져갑니다.

### 2-3. 힙과 스택

```java
Student s1 = new Student();
```

```
스택(Stack)              힙(Heap)
┌──────────┐            ┌────────────────┐
│ s1: 0x1A │ ─────────▶ │ Student 객체    │
└──────────┘            │ StudentID: 0    │
                        │ studentName:null│
                        └────────────────┘
```

- **스택** — 지역 변수, 참조값. 메소드가 끝나면 사라짐. 빠름
- **힙** — `new`로 만든 객체. GC가 관리. 상대적으로 느림

`Student s4 = s2;`는 힙의 객체를 복사하는 게 아니라 **스택의 주소값만 복사**합니다.

### 2-4. `toString()` 오버라이딩

```java
System.out.println(s1);   // day05.exam.Student@5ecddf8f
```

```java
@Override
public String toString() {
    return "Student [ID=" + StudentID + ", name=" + studentName + "]";
}
```

`println`이 내부적으로 `toString()`을 부르기 때문에 이것만 해두면 디버깅이 훨씬 편해집니다. VSCode에서 클래스 안에 커서를 두고 `Ctrl+.` → "Generate toString()"으로 자동 생성됩니다.

→ [[Java day08 접근제한자와 static]] 에서 실제로 적용합니다.

### 2-5. 멤버변수 이름은 소문자로

```java
int StudentID;    // 클래스처럼 보여 헷갈림
int studentId;    // 정답
```

## 3. 더 나아가 알면 좋은 것

### 3-1. `equals()`와 `hashCode()`

```java
Book b1 = new Book("Java");
Book b2 = new Book("Java");
b1 == b2;        // false (주소 비교)
b1.equals(b2);   // false ← 기본 equals도 주소 비교!
```

"제목이 같으면 같은 책"으로 취급하려면 `equals()`를 오버라이딩해야 합니다. 그리고 **`equals()`를 재정의하면 `hashCode()`도 반드시 같이** 재정의해야 합니다. 안 그러면 `HashMap`, `HashSet`에서 같은 객체가 중복 저장됩니다.

### 3-2. JS 객체와의 비교

```java
Student s = new Student();   // 클래스 설계도가 먼저 필요
s.studentName = "유재석";
```
```javascript
const s = { studentName: "유재석" };   // 설계도 없이 즉석 생성
```

Java는 **클래스 → 인스턴스**, JS는 **객체 리터럴을 바로** 만듭니다. 대신 JS도 `class` 문법을 지원합니다. → [[JS day07 객체]]

참조 복사 성질은 완전히 같습니다.
```javascript
const a = { x: 1 };
const b = a;
b.x = 2;
console.log(a.x);   // 2
```

### 3-3. `record` (Java 16+)

```java
record Book(String title, String author) { }
```

생성자, getter, `equals`, `hashCode`, `toString`이 전부 자동 생성됩니다. 데이터만 담는 클래스는 한 줄로 끝납니다.

## 실습 파일

- `2026B_BE/src/Note/day04.txt`
- `2026B_BE/src/day05/exam/exam1.java`
- `2026B_BE/src/day05/practice/pracitce1.java`, `txt`
- `2026_FE/day03/memo`

## 관련 노트

[[Java MOC]] · [[Java day04 제어문과 배열]] · [[Java day06 생성자와 콘솔 게시판]] · [[Java day08 접근제한자와 static]] · [[JS day07 객체]]
