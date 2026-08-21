---
출처: Claude 분석
작성일: 2026-08-21
tags: [코드정리]
---

# JAVA 팩토리 패턴

> 상위: [[JAVA 패턴]]

전부 ※. **new를 한 곳에 모아** 어떤 구현체를 만들지의 결정을 감추는 패턴이다.

## 정적 팩토리 메소드 — 이름 있는 생성자

```java
public class Rental {
    private final int bookNo;
    private final LocalDate due;

    private Rental(int bookNo, LocalDate due) {
        this.bookNo = bookNo;
        this.due = due;
    }

    public static Rental ofDays(int bookNo, int days) {
        return new Rental(bookNo, LocalDate.now().plusDays(days));
    }

    public static Rental standard(int bookNo) {
        return ofDays(bookNo, 14);
    }
}
```

```java
Rental r = Rental.standard(12);
```

- 생성자 대신 **이름이 있는 static 메소드**로 만든다. `standard`(기본 14일)처럼 이름이 생성 규칙을 설명한다
- 표준 라이브러리가 이 방식투성이다: `LocalDate.of(...)` `List.of(...)` `Integer.valueOf(...)` `Optional.ofNullable(...)` — `of` `from` `valueOf`가 보이면 팩토리다

## 조건 분기 팩토리 — 구현체 선택을 감추기

```java
public class DaoFactory {
    public static IBaseDao<BookDto> bookDao(String mode) {
        if (mode.equals("db")) return new MySqlBookDao();
        return new MemoryBookDao();
    }
}
```

```java
IBaseDao<BookDto> dao = DaoFactory.bookDao("db");
```

- "어떤 구현체를 쓸까"의 if가 프로그램 전체에 퍼지지 않고 팩토리 한 곳에만 존재한다
- 쓰는 쪽은 인터페이스 타입만 받는다 — 전략 교체(규격/구현 분리)와 세트로 움직이는 패턴이다
- 얻는 효과: 새 구현체가 생겨도 고치는 곳이 팩토리 하나다. 조립 담당(AppConfig)을 두는 Repository 구조도 이 발상의 확장이다
