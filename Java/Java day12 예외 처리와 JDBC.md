---
출처: Claude 분석
원본: KDT_2026/2026B_BE/src/day12/exam
작성일: 2026-08-13
tags: [학습, java]
---

# Java day12 — 예외 처리와 JDBC

> 실습 파일: `day12/exam/exam1.java`(예외 처리), `exam2.java`(JDBC 연동·조회), `sample.sql`(DB 준비)
> 허브: [[Java MOC]] · 이전: [[Java day11 종합예제 인터페이스 DAO]] · 다음: [[Java day12 종합예제 JDBC DAO]]

## 1. 배운 내용

### 1-1. 예외란 — 에러를 고치는 게 아니라 흐름을 제어하는 것

예외(Exception)는 실행 중 문제가 생겼을 때 프로그램을 멈추지 않고 **흐름을 다른 길로 돌리는** 장치다. `if` 로 매번 조건을 검사하는 것과 목적이 겹치지만, 예외는 "정상 흐름"과 "문제 대응 흐름"을 코드에서 시각적으로 분리해 준다.

- **일반예외(checked)**: 컴파일 전에 "여기서 예외가 날 수 있다"고 컴파일러가 미리 잡아 주는 종류. 처리 코드가 없으면 컴파일이 안 된다
- **실행예외(unchecked)**: 컴파일은 되지만 실행 중에 터지는 종류. 경험으로 예측하고 막아야 한다

### 1-2. try - catch - finally

```java
try {
    // 예외가 날 수 있는 코드
} catch (예외클래스 e) {
    // 예외가 났을 때 실행되는 코드 (e: 예외 정보를 담은 객체)
} finally {
    // 예외 여부와 무관하게 무조건 실행
}
```

`e` 는 변수이면서 예외 정보를 담은 객체다. `finally` 는 성공하든 실패하든 반드시 실행되므로 자원 정리(파일·DB 연결 닫기) 자리로 쓴다.

### 1-3. 자주 만나는 예외들

| 예외 | 언제 |
| --- | --- |
| `ClassNotFoundException` | `Class.forName("...")` 로 없는 클래스를 동적 로드할 때 |
| `InterruptedException` | `Thread.sleep(ms)` 중 스레드에 문제가 생길 때 |
| `NullPointerException` | `null` 인 참조로 멤버(`.length()` 등)에 접근할 때 |
| `NumberFormatException` | `Integer.parseInt("100a")` 처럼 숫자로 변환 불가할 때 |
| `ArrayIndexOutOfBoundsException` | 배열의 없는 인덱스(`arr[5]`)를 호출할 때 |
| `InputMismatchException` | `Scanner.nextInt()` 에 숫자가 아닌 입력이 들어올 때 |

`null` 은 "참조값이 없다 = 가리키는 객체(인스턴스)가 없다"는 뜻이라, 점(.) 연산자로 멤버에 접근하려는 순간 `NullPointerException` 이 난다. [[Java day05 클래스와 인스턴스]] 의 참조 개념과 바로 이어진다.

### 1-4. 다중 catch — 넓은 예외는 맨 아래

```java
try {
    int ch = scan.nextInt();
    Integer.parseInt("ABC");
} catch (InputMismatchException e) {
    System.out.println("정수만 입력하세요");
} catch (NumberFormatException e) {
    System.out.println("타입 변환 오류");
} catch (Exception e) {           // 위에서 못 잡은 나머지를 포괄
    System.out.println("예외 발생: 관리자에게 문의");
} finally {
    System.out.println("무조건 실행");
}
```

여러 예외를 각각 다르게 처리하려면 catch를 여러 개 쓴다. **상위 타입인 `Exception` 은 반드시 맨 마지막**에 둔다 — 위에 두면 하위 예외들을 전부 먼저 채가서 구체적인 catch가 실행되지 않는다. 좁은 예외 → 넓은 예외 순서가 규칙이다.

### 1-5. throws — 예외를 호출한 곳으로 떠넘기기

```java
public static void method1() throws ClassNotFoundException {
    Class.forName("java.lang.Spring");   // 여기서 처리하지 않고
}

// 호출하는 쪽에서 처리
try {
    method1();
} catch (Exception e) {
    System.out.println("메소드 예외 발생");
}
```

메소드 선언부에 `throws` 를 붙이면 "나는 이 예외를 처리하지 않고 나를 부른 쪽으로 넘긴다"는 뜻이다. 예외를 어디서 처리할지(현재 메소드 vs 호출자)를 고르는 두 갈래 중 하나다.

### 1-6. JDBC 첫걸음 — 드라이버 로드

JDBC(Java Database Connectivity)는 **자바와 데이터베이스를 연동하는 인터페이스**다. 연동 준비는 두 단계다.

```java
// 1. lib 폴더에 'mysql-connector-j-x.x.x.jar' 를 넣는다 (MySQL용 드라이버)
// 2. 드라이버 클래스를 동적으로 로드한다
try {
    Class.forName("com.mysql.cj.jdbc.Driver");
    System.out.println("MySQL JDBC 드라이버 있음!");
} catch (ClassNotFoundException e) {
    System.out.println("드라이버 없음 - 라이브러리 추가 필요");
}
```

- `Class.forName(...)` 은 문자열로 클래스를 실행 중에 읽어 온다. jar가 없으면 `ClassNotFoundException` 이 나므로, 1-3에서 배운 예외 처리가 여기서 바로 실전으로 쓰인다
- 드라이버 로드는 DB에 연결하기 전의 준비 단계다. 이어서 실제 연결·질의로 넘어간다

### 1-7. 연결하고 SQL 실행하기 — getConnection · PreparedStatement

드라이버가 준비됐으면 DB 서버에 연결하고 SQL을 실행한다.

```java
// [2] DB 서버 연동
String url  = "jdbc:mysql://127.0.0.1:3306/mydb0813";
String user = "root";
String password = "****";                 // 실습용 로컬 계정 (노트에는 값 생략)
Connection conn = DriverManager.getConnection(url, user, password);

// [3] DML 실행 (insert / select / update / delete)
String sql = "insert into test( name ) values( '유재석' )";
PreparedStatement ps = conn.prepareStatement(sql);
int result = ps.executeUpdate();          // 실행된 레코드 수 반환 (1: 성공, 0: 실패)
System.out.println(result);
```

| 단계 | 타입·메소드 | 하는 일 |
| --- | --- | --- |
| 연결 | `DriverManager.getConnection(url, user, pw)` | DB 서버에 접속해 `Connection`(연결 객체)을 받는다 |
| 명령 준비 | `conn.prepareStatement(sql)` | 실행할 SQL을 담은 `PreparedStatement`를 만든다 |
| 실행 | `ps.executeUpdate()` | INSERT·UPDATE·DELETE를 실행하고 **바뀐 레코드 수**를 반환한다 |

- SQL은 자바 문자열로 적으므로 IDE의 자동완성이 안 된다. 오타가 실행 중에야 드러나기 쉬운 지점이다
- 연결·실행 중 문제는 `SQLException`(일반예외)으로 잡는다. 드라이버 없음(`ClassNotFoundException`)과 서버 연동 실패(`SQLException`)를 **다중 catch로 나눠** 원인을 구분한다 — 1-4에서 배운 다중 catch가 그대로 쓰인다
- `executeUpdate()` 는 조회(SELECT)가 아니라 **변경**용이라 결과로 "몇 줄이 바뀌었는지"를 돌려준다. 조회는 아래 1-7-1의 `executeQuery()` + `ResultSet` 이 담당한다

#### 1-7-1. 조회하기 — executeQuery · ResultSet

INSERT·UPDATE·DELETE는 `executeUpdate()` 로 "바뀐 줄 수"를 받지만, SELECT는 **결과 표(레코드 묶음)** 를 받아야 하므로 `executeQuery()` 와 `ResultSet` 을 쓴다.

```java
// select 필드명 from 테이블명;
String sql2 = "select * from test";
ps = conn.prepareStatement(sql2);
ResultSet rs = ps.executeQuery();   // 조회 결과를 ResultSet에 담는다
rs.next();                          // 커서를 첫(다음) 레코드로 이동
System.out.println(rs.getInt("no"));      // rs.get타입("속성명")
System.out.println(rs.getString("name"));
```

| 타입·메소드 | 하는 일 |
| --- | --- |
| `ps.executeQuery()` | SELECT를 실행하고 결과를 `ResultSet`(조회 결과 커서)으로 반환한다 |
| `rs.next()` | 커서를 다음 레코드로 옮긴다. 읽을 레코드가 있으면 `true`, 없으면 `false` |
| `rs.getInt("no")` / `rs.getString("name")` | 현재 레코드에서 **컬럼 이름**으로 값을 타입에 맞게 꺼낸다 |

- `ResultSet` 은 처음에 첫 레코드 **앞**을 가리키므로, 값을 읽기 전에 `rs.next()` 로 한 칸 내려야 한다. 여러 행을 읽을 땐 `while (rs.next()) { ... }` 로 반복한다
- `getInt`·`getString` 의 인자는 SELECT한 **컬럼명**이다. `sample.sql` 에서 만든 `no`·`name` 이 그대로 키가 된다
- 변경은 `executeUpdate()`(반환: 레코드 수), 조회는 `executeQuery()`(반환: `ResultSet`) — 이 둘을 나눠 쓰는 게 JDBC 실행의 갈림길이다

### 1-8. 실행 전 DB 준비 (sample.sql)

자바에서 연결하기 전에 DB와 테이블이 먼저 있어야 한다.

```sql
CREATE DATABASE mydb0813;
use mydb0813;

create table test (
    no   int PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(30)
);
```

- `getConnection` 의 URL 끝(`.../mydb0813`)이 여기서 만든 데이터베이스 이름과 정확히 같아야 연결된다
- `AUTO_INCREMENT` 라서 자바에서 `name` 만 넣어도 `no` 는 자동으로 매겨진다 — [[SQL day02 테이블과 제약조건]] 의 제약조건이 JDBC 실습의 밑바탕이다

같은 `sample.sql` 에는 exam2가 쓰는 `test` 외에 게시판용 `board` 테이블도 함께 준비돼 있다. 이어지는 [[Java day12 종합예제 JDBC DAO]] 가 이 표를 대상으로 CRUD를 돌린다.

```sql
create table board (
    no      int AUTO_INCREMENT,
    content VARCHAR(255),
    writer  VARCHAR(30),
    constraint PRIMARY KEY( no )
);
insert into board( content, writer ) values ( ..., ... ), ( ..., ... );  -- 조회용 시드 2줄
```

- 컬럼(`no`·`content`·`writer`)이 [[Java day12 종합예제 JDBC DAO]] 의 `BoardDto` 필드와 1:1로 맞물린다 — 자바 DTO가 곧 이 표의 한 줄이다
- 미리 넣어 둔 시드 2줄 덕분에, 종합예제에서 전체조회(`select * from board`)를 처음 실행할 때부터 결과가 비어 있지 않다
- `PRIMARY KEY` 를 컬럼 뒤가 아니라 `constraint PRIMARY KEY( no )` 로 따로 지정하는 방식도 같은 결과다 — [[SQL day02 테이블과 제약조건]] 에서 정리한 제약조건 선언 위치의 두 갈래다

## 2. 추가로 알면 좋은 활용법

### 2-1. 예외 계층과 checked / unchecked

```
Throwable
 ├─ Error            (복구 불가 — 건드리지 않음: OutOfMemoryError 등)
 └─ Exception
     ├─ (checked)    컴파일러가 처리를 강제: ClassNotFoundException, IOException ...
     └─ RuntimeException (unchecked) 실행 중 발생: NullPointer, NumberFormat ...
```

`Exception` 을 catch 하나로 다 잡을 수 있는 이유는 위 예외들이 전부 `Exception` 의 자식이라서다 — [[Java day10 상속과 다형성]] 의 업캐스팅이 예외 처리에도 적용된 것이다.

### 2-2. JDBC 연동의 전체 흐름

JDBC 연동은 6단계로 흐른다. exam2는 ①~⑤(드라이버 로드·연결·명령 준비·실행·`ResultSet` 조회)까지 구현했고, 닫기(⑥)가 다음 몫이다.

```
① 드라이버 로드   Class.forName("com.mysql.cj.jdbc.Driver")
② 연결          DriverManager.getConnection(URL, ID, PW)
③ 명령 준비      Connection.prepareStatement("insert ... / SELECT ...")
④ 실행          executeUpdate()  (변경) / executeQuery()  (조회)
⑤ 결과 처리      ResultSet 순회
⑥ 닫기          close() (finally 또는 try-with-resources)
```

②의 `URL·ID·PW` 는 [[Java day11 종합예제 인터페이스 DAO]] 의 IBaseDao에 상수로 미리 심어 둔 그 값과 같은 자리다. day11 종합예제의 메모리 저장 DAO의 `save()` 안을 ①~④로 바꾸면 진짜 DB 저장이 된다.

### 2-3. try-with-resources로 close 자동화

DB 연결·파일은 `finally` 에서 닫는 대신, 괄호 안에서 열면 블록이 끝날 때 자동으로 닫힌다.

```java
try (Connection con = DriverManager.getConnection(URL, ID, PW)) {
    // 사용
}   // con.close() 자동 호출
```

닫기를 빠뜨려 연결이 쌓이는 실수를 막아 주는 문법이다.

## 3. 더 나아가 알면 좋은 것

### 3-1. Connection·Statement·ResultSet은 전부 인터페이스

JDBC의 핵심 타입이 전부 인터페이스라, MySQL 드라이버든 Oracle 드라이버든 **같은 코드로 쓸 수 있다.** 드라이버(구현체)만 갈아끼우면 되는 이 구조가 [[Java day11 인터페이스]] 에서 배운 "규격과 구현의 분리"의 대표 실무 사례다.

### 3-2. 사용자 정의 예외

`throw new IllegalArgumentException("메시지")` 처럼 예외를 직접 던질 수 있고, `Exception` 을 상속해 도메인 전용 예외(`중복회원예외` 등)를 만들 수도 있다. 예외를 흐름 제어를 넘어 "약속 위반 신호"로 쓰는 방식이다.

### 3-3. 다음에 볼 키워드

- `PreparedStatement` — 값을 `?` 로 바인딩해 SQL 인젝션을 막는 방식
- 커넥션 풀(HikariCP) — 연결을 매번 열지 않고 재사용
- `try-with-resources`, `AutoCloseable`
- Spring의 `JdbcTemplate` / JPA — JDBC 반복 코드를 걷어낸 상위 도구

## 실습 파일

- `2026B_BE/src/day12/exam/exam1.java` (예외 종류, 다중 catch, throws)
- `2026B_BE/src/day12/exam/exam2.java` (JDBC 드라이버 로드 → 연결 → PreparedStatement → executeUpdate → executeQuery·ResultSet 조회)
- `2026B_BE/src/day12/exam/sample.sql` (실습용 DB 생성 — exam2용 `test` 표 + 종합예제용 `board` 표·시드 데이터)

## 관련 노트

[[Java MOC]] · [[Java day12 종합예제 JDBC DAO]] · [[Java day11 종합예제 인터페이스 DAO]] · [[Java day11 인터페이스]] · [[Java day10 상속과 다형성]] · [[Java day05 클래스와 인스턴스]] · [[SQL day01 데이터베이스 기초]] · [[SQL day02 테이블과 제약조건]] · [[KDT_2026 학습 지도]]
