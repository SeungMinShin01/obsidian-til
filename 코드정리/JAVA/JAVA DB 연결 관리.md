---
출처: Claude 분석
작성일: 2026-08-21
tags: [코드정리]
---

# JAVA DB 연결 관리

> 상위: [[JAVA JDBC]]

전부 ※. DAO마다 반복되는 연결 코드를 한 곳으로 모으는 방법이다.

## DBUtil — 연결 담당 클래스

```java
public class DBUtil {
    private static final String URL = "jdbc:mysql://localhost:3306/mydb";
    private static final String USER = "root";
    private static final String PW = "비밀번호";

    private DBUtil() { }

    public static Connection getConnection() throws SQLException {
        return DriverManager.getConnection(URL, USER, PW);
    }
}
```

```java
try (Connection con = DBUtil.getConnection();
     PreparedStatement ps = con.prepareStatement(sql)) { ... }
```

- url·계정·비밀번호가 **한 파일에만** 있게 된다. DB를 옮기면 여기 세 줄만 고친다
- static 메소드라 인스턴스 없이 `DBUtil.getConnection()`으로 바로 쓴다. private 생성자로 `new`를 막는 것까지가 세트다
- 각 DAO의 try-with-resources 첫 줄이 전부 이 한 줄로 통일된다

## 설정 파일로 빼기

```java
Properties prop = new Properties();
prop.load(Files.newInputStream(Path.of("db.properties")));
String url = prop.getProperty("url");
```

```
url=jdbc:mysql://localhost:3306/mydb
user=root
password=비밀번호
```

- 비밀번호를 코드 밖 파일로 빼면 **Public 리포에 코드를 올려도 계정이 안 샌다**(설정 파일은 .gitignore에 넣는다)
- 코드 수정·재컴파일 없이 접속 정보를 바꿀 수 있는 것도 이득이다

## 커넥션 풀 — 이름만 알아두기

- 연결을 매번 새로 여는 건 비싸다(네트워크 왕복). 실무는 연결 여러 개를 미리 만들어 두고 빌려 쓰는 **커넥션 풀**을 쓴다
- 표준처럼 쓰이는 라이브러리가 HikariCP이고, 스프링 부트는 이걸 기본 내장한다. 콘솔 미니프로젝트 규모에서는 DBUtil로 충분하다
