---
출처: Claude 분석
원본: KDT_2026/2026B_BE/src/day12/종합예제
작성일: 2026-08-13
tags: [학습, java]
---

# Java day12 — 종합예제 (JDBC DAO)

> 실습 파일: `day12/종합예제/` (BoardView, BoardController, BoardDao·BaseDao, BoardDto)
> 허브: [[Java MOC]] · 이전: [[Java day12 예외 처리와 JDBC]]

[[Java day11 종합예제 인터페이스 DAO]] 는 저장소를 인터페이스로 규격화하고 데이터는 메모리(ArrayList)에 담았다. day12 종합예제는 같은 MVC 골격을 가져오되, 저장소를 **실제 DB에 연결**하는 쪽으로 방향을 튼 시작점이다. [[Java day12 예외 처리와 JDBC]] 에서 exam으로 익힌 JDBC 연동을, 이번에는 프로젝트 구조 안(DAO 계층)으로 옮겨 넣는 단계다.

## 1. 배운 내용

### 1-1. 구조 한눈에

```
BoardView (View)
   └─ BoardController (Controller)
         └─ BoardDao (Model·DAO)  ─ extends ─ BaseDao (JDBC 연동 부모)
DTO: BoardDto  ← DB 표(no·content·writer)를 담는 이동 객체
```

계층은 day11 종합예제와 같지만, 저장소 아래에 **BaseDao라는 연동 전담 부모 클래스**가 새로 붙었다. 이번 예제의 핵심은 "여러 DAO가 공통으로 쓰는 DB 연결을 어디에 두느냐"이고, 그 답을 부모 클래스 상속으로 잡았다.

### 1-2. BaseDao — 공통 JDBC 연동을 부모로 뽑기

```java
public class BaseDao {
    // 1. 연동 정보
    private String url = "jdbc:mysql://127.0.0.1:3306/mydb0813";
    private String user = "root";
    private String password = "****";   // 실습용 로컬 계정 (노트에는 값 생략)

    // 2. 연동 인터페이스 — protected: 상속관계면 다른 패키지도 접근 허용
    protected Connection conn;

    // 3. 연동 메소드
    private void connect() {
        try {
            Class.forName("com.mysql.cj.jdbc.Driver");            // 드라이버 로드
            conn = DriverManager.getConnection(url, user, password); // 연결 후 conn에 대입
        } catch (Exception e) {
            System.out.println("DB연동 실패" + e);
        }
    }

    // 4. 기본생성자에서 연동 실행 — 상속받아 만들어지면 자동으로 연결된다
    protected BaseDao() {
        connect();
    }
}
```

- `Class.forName(...)` → `DriverManager.getConnection(...)` 은 [[Java day12 예외 처리와 JDBC]] exam2에서 배운 그 두 단계다. 그 코드를 DAO마다 반복하지 않고 **부모 한 곳**에 모았다
- `conn` 을 `protected` 로 둔 이유가 핵심이다. `private` 이면 자식 DAO가 물려받아도 쓸 수 없다. 상속관계에서는 패키지가 달라도 접근되도록 `protected` 로 열어, 자식이 부모의 연결 객체(`conn`)를 그대로 이어서 쓰게 한다 — [[Java day08 접근제한자와 static]] 의 접근제한자가 상속 설계에서 왜 필요한지가 여기서 드러난다
- **생성자에서 `connect()` 를 부른다.** 자식 DAO가 만들어질 때 `super()` 로 부모 생성자가 먼저 돌아가므로, DAO 인스턴스가 생기는 순간 DB 연결까지 끝나 있다. [[Java day10 상속과 다형성]] 의 "자식 생성 → 부모 생성자 선실행"이 연동 자동화로 쓰인 셈이다

### 1-3. 규격(인터페이스)에서 공통 구현(부모 클래스)으로

day11 종합예제는 `IBaseDao` **인터페이스**에 연동 정보를 상수로 얹어 두기만 했다(행위만 규정, 연결은 미구현). day12는 `BaseDao` **부모 클래스**로 바꿔, 상수가 아니라 **실제 연결 코드(`connect()`)를 부모가 직접 들고** 자식에게 물려준다.

| | day11 종합예제 | day12 종합예제 |
| --- | --- | --- |
| 공통 묶는 도구 | `interface IBaseDao` (규격) | `class BaseDao` (부모 클래스) |
| 연동 정보 | 상수만 선언 | 실제 연결 메소드 보유 |
| 저장 위치 | 메모리(ArrayList) | DB(JDBC 연결) 방향 |
| 자식과의 관계 | `implements` | `extends` |

순수 규격만 필요하면 인터페이스, **공통 구현까지 물려주려면 부모 클래스** — [[Java day11 인터페이스]] 3-1에서 정리한 선택 기준이 그대로 적용된 지점이다. 연결 코드처럼 "모든 DAO가 똑같이 실행할 본문"이 있으면 상속이 맞다.

### 1-4. 싱글톤으로 계층 배선하기

View·Controller·DAO 모두 `private 생성자 + static instance + getInstance()` 형태이고, 각 계층은 자기 아래 계층의 인스턴스를 `getInstance()` 로 받아 든다.

```java
public class BoardView {
    private BoardView() { }
    private static final BoardView instance = new BoardView();
    public static BoardView getInstance() { return instance; }

    // View → Controller 배선
    private BoardController bc = BoardController.getInstance();
}

public class BoardController {
    private BoardController() { }
    private static final BoardController instance = new BoardController();
    public static BoardController getInstance() { return instance; }

    // Controller → Dao 배선
    private BoardDao bd = BoardDao.getInstance();
}
```

- 계층마다 인스턴스가 하나만 존재하도록 고정한다. View가 Controller를, Controller가 Dao를 멤버로 잡아 **위에서 아래로 한 줄로 연결**한다 — [[Java day11 종합예제 인터페이스 DAO]] 에서 익힌 전 계층 싱글톤과 같은 배선이다
- 이렇게 참조를 미리 걸어 두면, 나중에 메뉴·CRUD 메소드를 붙일 때 `bc.save(...)`, `bd.findAll()` 처럼 이미 이어진 통로로 호출만 하면 된다. 지금은 그 통로를 먼저 세우는 단계다

### 1-5. BoardDto — 자바는 저장소가 아니다

```java
public class BoardDto {
    // DTO: 데이터 이동 객체. 자바는 저장소가 아니라, DB(저장소)의 자료를 실어 나른다
    private int no;          // DB 표의 컬럼과 1:1
    private String content;
    private String writer;

    public BoardDto() { }
    public BoardDto(int no, String content, String writer) {
        this.no = no; this.content = content; this.writer = writer;
    }
    // getter / setter / toString ...
}
```

- DTO의 멤버변수(`no`·`content`·`writer`)는 **DB 표의 컬럼을 그대로 옮긴 것**이다. CRUD로 주고받을 한 줄(레코드)을 자바 객체 하나로 표현한다
- "자바는 저장소가 아니다"는 말이 DTO의 역할을 정확히 짚는다. 값을 오래 보관하는 곳은 DB이고, DTO는 그 한 줄을 **DB ↔ 자바 사이에서 실어 나르는 그릇**일 뿐이다 — [[Java day08 접근제한자와 static]] 에서 만든 DTO 개념이 DB와 짝지어지는 지점
- `no` 는 [[SQL day02 테이블과 제약조건]] 의 `AUTO_INCREMENT` 로 DB가 매기므로, 저장할 때는 `content`·`writer` 만 채워 보내는 경우가 많다

## 2. 추가로 알면 좋은 활용법

### 2-1. 자식 DAO가 부모의 conn을 이어받는 그림

BaseDao를 상속하면 자식은 연결을 새로 만들 필요 없이 물려받은 `conn` 으로 바로 SQL을 실행한다.

```java
public class BoardDao extends BaseDao {
    private static final BoardDao instance = new BoardDao();
    private BoardDao() { }                     // super() → BaseDao() → connect() 자동 실행
    public static BoardDao getInstance() { return instance; }

    public boolean save(BoardDto dto) {
        String sql = "insert into board(content, writer) values(?, ?)";
        try {
            PreparedStatement ps = conn.prepareStatement(sql);   // 부모가 연결한 conn 사용
            ps.setString(1, dto.getContent());
            ps.setString(2, dto.getWriter());
            return ps.executeUpdate() == 1;
        } catch (Exception e) { return false; }
    }
}
```

[[Java day11 종합예제 인터페이스 DAO]] 의 `boardList.add(obj)` 자리가 여기서는 **JDBC INSERT**로 바뀐다. 규격·계층 배선은 그대로 두고 저장 위치만 메모리 → DB로 옮기는 것이 day11이 예고한 방향이었다.

### 2-2. PreparedStatement의 ? 바인딩

SQL 문자열에 값을 직접 이어 붙이지 않고 `?` 자리표시자를 두고 `setString`·`setInt` 로 채우는 방식이다.

```java
String sql = "insert into board(content, writer) values(?, ?)";
PreparedStatement ps = conn.prepareStatement(sql);
ps.setString(1, content);   // 첫 번째 ?
ps.setString(2, writer);    // 두 번째 ?
```

값을 따로 넣으므로 문자열 안에 따옴표를 신경 쓸 일이 줄고, 사용자 입력이 SQL 구문으로 해석되는 SQL 인젝션도 막힌다 — [[Java day12 예외 처리와 JDBC]] 3-3에서 예고한 실무 관용구다.

### 2-3. 연결을 부모에 두는 것의 장단점

부모 생성자에서 연결하면 자식마다 연결 코드를 안 써도 되어 편하다. 다만 DAO 인스턴스가 사는 동안 연결이 계속 열려 있는 구조이기도 하다. 실무에서는 매 요청마다 열고 닫거나, 미리 만들어 둔 연결을 돌려 쓰는 **커넥션 풀**로 이 부분을 다듬는다(3-2).

## 3. 더 나아가 알면 좋은 것

### 3-1. 다음 단계 — CRUD 메소드 채우기

지금은 View→Controller→Dao 배선과 BaseDao 연결까지 세운 골격이다. 여기에 `save`·`findAll`·`update`·`delete` 를 붙이고, [[Java day12 예외 처리와 JDBC]] 의 `executeUpdate()`(변경)·`executeQuery()`+`ResultSet`(조회)을 각 메소드 안에 넣으면 [[Java day09 MVC 종합예제]] 의 콘솔 게시판이 **진짜 DB 게시판**으로 완성된다.

### 3-2. 연결 닫기와 커넥션 풀

연 것은 닫아야 한다. `finally` 나 `try-with-resources` 로 `conn`·`ps`·`rs` 를 닫고, 나아가 HikariCP 같은 커넥션 풀로 연결을 재사용하면 매번 여닫는 비용을 줄인다 — [[Java day12 예외 처리와 JDBC]] 3-3의 키워드가 이어진다.

### 3-3. 다음에 볼 키워드

- `PreparedStatement` 파라미터 바인딩, `executeUpdate` vs `executeQuery`
- `try-with-resources` 로 `Connection`·`ResultSet` 자동 닫기
- 커넥션 풀(HikariCP), 트랜잭션(`setAutoCommit(false)` · `commit` · `rollback`)
- Spring `JdbcTemplate` / JPA — DAO 반복 코드를 걷어낸 상위 도구, 이 구조의 완성형

## 실습 파일

- `2026B_BE/src/day12/종합예제/view/BoardView.java` (View, Controller 배선)
- `2026B_BE/src/day12/종합예제/controller/BoardController.java` (Controller, Dao 배선)
- `2026B_BE/src/day12/종합예제/model/dao/BaseDao.java` (JDBC 연동 부모 클래스)
- `2026B_BE/src/day12/종합예제/model/dao/BoardDao.java` (게시판 DAO, 싱글톤)
- `2026B_BE/src/day12/종합예제/model/dto/BoardDto.java` (DB 표를 담는 DTO)

## 관련 노트

[[Java MOC]] · [[Java day12 예외 처리와 JDBC]] · [[Java day11 종합예제 인터페이스 DAO]] · [[Java day11 인터페이스]] · [[Java day10 상속과 다형성]] · [[Java day09 MVC 종합예제]] · [[Java day08 접근제한자와 static]] · [[SQL day02 테이블과 제약조건]] · [[KDT_2026 학습 지도]]
