---
출처: Claude 분석
작성일: 2026-08-21
tags: [코드정리]
---

# JAVA 템플릿 메소드 패턴

> 상위: [[JAVA 패턴]]

전부 ※. **골격은 부모가, 빈칸은 자식이** 채우는 상속 활용 패턴이다.

## 구조

```java
abstract class BaseDao<T> {
    public final ArrayList<T> findAll() {
        ArrayList<T> list = new ArrayList<>();
        String sql = getSelectSql();
        try (Connection con = DBUtil.getConnection();
             PreparedStatement ps = con.prepareStatement(sql);
             ResultSet rs = ps.executeQuery()) {
            while (rs.next()) {
                list.add(mapRow(rs));
            }
        } catch (SQLException e) { }
        return list;
    }

    protected abstract String getSelectSql();
    protected abstract T mapRow(ResultSet rs) throws SQLException;
}
```

```java
class BookDao extends BaseDao<BookDto> {
    @Override
    protected String getSelectSql() { return "SELECT no, title FROM book"; }

    @Override
    protected BookDto mapRow(ResultSet rs) throws SQLException {
        return new BookDto(rs.getInt("no"), rs.getString("title"));
    }
}
```

- 부모의 `findAll()`이 **템플릿**이다: 연결→실행→반복→닫기의 순서(골격)를 확정해 두고, 달라지는 두 지점(SQL 문장, 행→DTO 변환)만 추상메소드 빈칸으로 뚫어놨다
- 자식은 빈칸 두 개만 채우면 완성된 findAll을 공짜로 얻는다. DAO가 10개여도 연결·반복·닫기 코드는 한 곳에만 존재한다
- 템플릿을 `final`로 막으면 자식이 골격 자체를 바꾸는 것을 금지할 수 있다

## 전략 패턴과의 구분

```
템플릿 메소드  →  상속으로 빈칸 채움 (컴파일 시점 고정)
전략 교체     →  인터페이스 구현체를 갈아끼움 (실행 중 교체 가능)
```

- 같은 "공통/가변 분리"인데 수단이 다르다. 실행 중 갈아끼울 필요가 없고 공통 코드가 크면 템플릿 메소드가 간단하다
- day12 종합예제의 BaseDao 상속 구조가 이 패턴의 실물이다. 스프링의 JdbcTemplate도 이름 그대로 이 패턴이다
