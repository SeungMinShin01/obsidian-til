---
출처: Claude 분석
작성일: 2026-08-21
tags: [코드정리]
---

# JAVA 빌더 패턴

> 상위: [[JAVA 패턴]]

전부 ※. 매개변수가 많은 객체를 **이름 붙여 조립**하는 생성 방법이다.

## 문제 — 생성자 지옥

```java
new Book(1, "제목", "저자", "출판사", 2026, 15000, true, null);
```

- 매개변수가 5개를 넘으면 순서를 외울 수 없고, 같은 타입이 이웃하면(가격·연도) 바꿔 넣어도 컴파일러가 못 잡는다
- 선택 항목이 많으면 조합마다 생성자를 만들어야 한다(오버로딩 폭발)

## 빌더

```java
public class Book {
    private final String title;
    private final String author;
    private final int price;

    private Book(Builder b) {
        this.title = b.title;
        this.author = b.author;
        this.price = b.price;
    }

    public static class Builder {
        private String title;
        private String author;
        private int price = 0;

        public Builder title(String v) { this.title = v; return this; }
        public Builder author(String v) { this.author = v; return this; }
        public Builder price(int v) { this.price = v; return this; }

        public Book build() {
            if (title == null) throw new IllegalStateException("제목은 필수");
            return new Book(this);
        }
    }
}
```

```java
Book b = new Book.Builder()
        .title("이것이 자바다")
        .price(30000)
        .build();
```

- 각 setter가 `return this;`로 자기 자신을 돌려줘서 점으로 잇는 **체이닝**이 된다
- 얻는 효과: ①값마다 이름이 붙어 순서 실수가 사라진다 ②선택 항목은 그냥 생략한다(기본값) ③`build()`에서 필수값 검증을 한 번에 한다 ④완성품은 setter 없는 불변으로 만들 수 있다
- AI가 생성하는 코드에서 `.xxx().yyy().build()` 체인이 보이면 전부 이 패턴이다

## 실무에서는

- 손으로 안 짜고 Lombok `@Builder` 한 줄로 만든다
- 판단 기준: 매개변수 4개 이하 + 전부 필수면 그냥 생성자가 낫다. 많고 선택적일 때 빌더가 이긴다
