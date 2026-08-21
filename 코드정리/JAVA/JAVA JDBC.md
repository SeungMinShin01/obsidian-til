---
출처: Claude 분석
작성일: 2026-08-21
tags: [코드정리]
---

# JAVA JDBC

> 상위: [[JAVA]]
> 세부: [[JAVA JDBC 트랜잭션]] · [[JAVA DB 연결 관리]]

자바에서 MySQL에 SQL을 보내고 결과를 받는 표준 통로다. ※ 수업 진도 기준 최신 범위.

## 연결

```java
import java.sql.*;

String url = "jdbc:mysql://localhost:3306/mydb";
Connection con = DriverManager.getConnection(url, "root", "비밀번호");
```

- url 구조: `jdbc:mysql://호스트:포트/DB이름`. 3306이 MySQL 기본 포트다
- `Connection` `PreparedStatement` `ResultSet`은 전부 인터페이스다. 드라이버(구현체)만 바꾸면 Oracle이든 MySQL이든 같은 코드로 쓴다
- 계정·비밀번호를 코드에 하드코딩한 채 공개 리포에 올리지 않는다

## INSERT · UPDATE · DELETE — executeUpdate

```java
String sql = "INSERT INTO book(title, author) VALUES(?, ?)";

try (Connection con = DriverManager.getConnection(url, user, pw);
     PreparedStatement ps = con.prepareStatement(sql)) {

    ps.setString(1, "제목");
    ps.setString(2, "저자");

    int rows = ps.executeUpdate();
}
```

- 값이 들어갈 자리를 `?`로 비워 두고 `setString(순번, 값)`·`setInt(순번, 값)`으로 채운다. **순번은 1부터**다
- `?` 방식(PreparedStatement)이 필수인 이유: 문자열을 `+`로 이어 붙여 SQL을 만들면 입력값에 SQL을 섞는 공격(인젝션)에 뚫린다
- `executeUpdate()`는 바뀐 행 수를 반환한다. `rows == 1`로 성공 여부를 판단해 boolean으로 돌려주는 게 DAO의 기본 형태다
- try-with-resources 괄호에 넣으면 Connection·PreparedStatement가 자동으로 닫힌다

## SELECT — executeQuery와 ResultSet

```java
String sql = "SELECT no, title, author FROM book";

try (Connection con = DriverManager.getConnection(url, user, pw);
     PreparedStatement ps = con.prepareStatement(sql);
     ResultSet rs = ps.executeQuery()) {

    while (rs.next()) {
        int no = rs.getInt("no");
        String title = rs.getString("title");
        list.add(new BookDto(no, title, rs.getString("author")));
    }
}
```

- 조회는 `executeQuery()`이고 결과가 `ResultSet`(표 모양 커서)으로 온다
- `rs.next()`가 다음 행으로 이동하며 행이 있으면 true다. while로 돌리면 전체 행을 훑는다
- `rs.getInt("컬럼명")` `getString("컬럼명")`으로 현재 행의 값을 꺼낸다
- **ResultSet 한 행 = DTO 한 개**로 담아 리스트로 모으는 게 표준 패턴이다. DTO가 테이블 한 행의 자바 표현이라는 게 여기서 보인다

## 조건 있는 조회

```java
String sql = "SELECT * FROM book WHERE no = ?";
ps.setInt(1, no);
try (ResultSet rs = ps.executeQuery()) {
    if (rs.next()) {
        return new BookDto(rs.getInt("no"), rs.getString("title"), rs.getString("author"));
    }
    return null;
}
```

- WHERE의 값도 `?`로 바인딩한다
- 한 건 조회는 while 대신 `if (rs.next())`로 받고, 없으면 null(또는 실패 표시)을 반환한다

## DAO에 넣는 형태

```java
public class BookDao {
    private BookDao() { }
    private static final BookDao instance = new BookDao();
    public static BookDao getInstance() { return instance; }

    public boolean save(BookDto dto) {
        String sql = "INSERT INTO book(title, author) VALUES(?, ?)";
        try (Connection con = DriverManager.getConnection(url, user, pw);
             PreparedStatement ps = con.prepareStatement(sql)) {
            ps.setString(1, dto.getTitle());
            ps.setString(2, dto.getAuthor());
            return ps.executeUpdate() == 1;
        } catch (SQLException e) {
            return false;
        }
    }
}
```

- SQL 실행은 전부 DAO 안에만 둔다. View·Controller에는 SQL이 등장하지 않는다
- 메소드 하나 = SQL 하나 + 성공 여부(또는 DTO/리스트) 반환이 기본 단위다
- ArrayList 저장이던 DAO를 이 형태로 바꿔도 Controller는 한 줄도 안 바뀐다 — 계층을 나눈 보상이 여기서 나온다

