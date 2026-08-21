---
출처: Claude 분석
작성일: 2026-08-21
tags: [코드정리]
---

# JAVA enum

> 상위: [[JAVA 클래스 문법]]

전부 ※. "정해진 값들 중 하나"를 타입으로 만드는 문법이다. 문자열 상수보다 훨씬 안전하다.

## 기본

```java
enum Status { RENTED, RETURNED, OVERDUE }

Status s = Status.RENTED;

if (s == Status.RENTED) { }

switch (s) {
    case RENTED -> System.out.println("대여중");
    case RETURNED -> System.out.println("반납완료");
    case OVERDUE -> System.out.println("연체");
}
```

- 값이 세 개로 고정된 타입이 생긴다. `"대여중"` 같은 문자열로 상태를 관리하면 오타(`"대여 중"`)가 런타임 버그가 되지만, enum은 오타가 컴파일 에러로 잡힌다
- enum은 인스턴스가 하나씩뿐이라 `==` 비교가 안전하다(equals 불필요)
- switch와 궁합이 좋다. 모든 값을 다루지 않으면 IDE가 경고해 준다

## 필드와 메소드를 가진 enum

```java
enum Grade {
    BASIC(0), SILVER(100), GOLD(300);

    private final int point;

    Grade(int point) { this.point = point; }

    public int getPoint() { return point; }
}

int p = Grade.GOLD.getPoint();
```

- 각 값에 데이터(포인트·수수료율·라벨)를 붙일 수 있다. 생성자는 자동으로 private다
- 얻는 효과: "등급별 값 표"가 if-else 뭉치 대신 enum 정의 한 곳에 모인다

## 자주 쓰는 기본 메소드

```java
Status.values();
Status.valueOf("RENTED");
s.name();
s.ordinal();
```

- `values()` 전체 값 배열(메뉴 출력에 유용), `valueOf("문자열")` 문자열→enum(DB에서 읽은 값 복원), `name()` enum→문자열, `ordinal()` 선언 순번
- DB에는 `name()` 문자열로 저장하고 읽을 때 `valueOf`로 되돌리는 게 보통이다
