---
출처: Claude 분석
작성일: 2026-08-21
tags: [코드정리]
---

# JAVA JDBC 트랜잭션

> 상위: [[JAVA JDBC]]

전부 ※. "두 개 이상의 SQL을 전부 성공 아니면 전부 취소"로 묶는 방법이다.

## 왜 필요한가

```
대여 처리 = ① rental에 INSERT + ② book 재고 UPDATE
```

- ①만 성공하고 ②에서 터지면 기록은 있는데 재고는 안 줄어든 이상한 상태가 된다
- 계좌 이체(출금+입금), 주문(주문 생성+재고 차감)처럼 **여러 테이블을 함께 바꾸는 모든 작업**이 같은 문제를 가진다

## 기본형 — setAutoCommit · commit · rollback

```java
Connection con = null;
try {
    con = DriverManager.getConnection(url, user, pw);
    con.setAutoCommit(false);

    try (PreparedStatement ps1 = con.prepareStatement(
            "INSERT INTO rental(member_no, book_no) VALUES(?, ?)")) {
        ps1.setInt(1, memberNo);
        ps1.setInt(2, bookNo);
        ps1.executeUpdate();
    }

    try (PreparedStatement ps2 = con.prepareStatement(
            "UPDATE book SET stock = stock - 1 WHERE no = ? AND stock > 0")) {
        ps2.setInt(1, bookNo);
        if (ps2.executeUpdate() == 0) throw new SQLException("재고 없음");
    }

    con.commit();
} catch (Exception e) {
    if (con != null) con.rollback();
} finally {
    if (con != null) { con.setAutoCommit(true); con.close(); }
}
```

- JDBC는 기본이 자동 커밋(SQL 하나마다 즉시 확정)이다. `setAutoCommit(false)`로 끄면 `commit()`을 부를 때까지 보류된다
- 중간에 뭐든 터지면 catch에서 `rollback()` — 그때까지의 변경이 전부 없던 일이 된다
- **두 SQL이 같은 Connection을 써야** 한 트랜잭션이다. 각자 연결을 열면 묶이지 않는다
- `stock > 0` 조건을 UPDATE에 넣고 결과 행 수 0이면 던지는 것도 관용구다 — 확인과 차감을 한 문장으로 합쳐 틈을 없앤다

## 요약 규칙

- 읽기만 하면 트랜잭션 신경 안 써도 된다. **쓰기가 2번 이상 묶이면 무조건** 트랜잭션이다
- commit은 딱 한 번, 마지막에. rollback은 catch에서. autoCommit 복구는 finally에서
- 스프링에선 `@Transactional` 어노테이션 하나가 이 전체 골격을 대신한다
