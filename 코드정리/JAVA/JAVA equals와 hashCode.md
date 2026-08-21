---
출처: Claude 분석
작성일: 2026-08-21
tags: [코드정리]
---

# JAVA equals와 hashCode

> 상위: [[JAVA 클래스 문법]]

전부 ※. "내용이 같으면 같은 객체"로 취급하고 싶을 때 필요한 재정의다.

## 문제 — 기본 equals도 주소 비교다

```java
Book a = new Book("자바");
Book b = new Book("자바");

a == b;
a.equals(b);
```

- 둘 다 false다. `==`는 당연히 주소 비교고, Object에서 물려받은 기본 `equals`도 주소를 비교하기 때문이다
- `list.contains(book)`, `indexOf`가 기대대로 안 되는 원인이 대부분 이것이다

## 재정의

```java
@Override
public boolean equals(Object o) {
    if (this == o) return true;
    if (!(o instanceof Book)) return false;
    Book other = (Book) o;
    return Objects.equals(title, other.title);
}

@Override
public int hashCode() {
    return Objects.hash(title);
}
```

- 순서: 자기 자신이면 true → 타입이 다르면 false → 캐스팅 후 핵심 필드 비교. `Objects.equals`를 쓰면 null 걱정이 없다
- **equals를 재정의하면 hashCode도 반드시 같이** 재정의한다. HashMap·HashSet이 hashCode로 칸을 먼저 찾고 equals로 확정하는 2단 구조라, 한쪽만 고치면 같은 내용이 중복 저장된다
- `Objects.hash(필드들)`이 hashCode 구현의 관용구다. equals에 쓴 필드와 같은 필드를 넣는다
- IDE의 Generate equals()/hashCode(), 또는 record를 쓰면 자동으로 만들어진다

## 어떤 필드로 비교할까

- "무엇이 같으면 같은 것인가"를 정하는 설계 결정이다. 회원이면 회원번호, 도서면 ISBN처럼 **식별자 필드**만 넣는 게 보통이다
- 모든 필드를 넣으면 값 하나만 달라져도 다른 객체가 된다 — DTO엔 그게 맞을 때도 있다(record의 기본 동작)
