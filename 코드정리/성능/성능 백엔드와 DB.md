---
출처: Claude 분석
작성일: 2026-08-21
tags: [코드정리]
---

# 성능 백엔드와 DB

> 상위: [[성능]]

네트워크 탭의 TTFB(초록 막대)가 길면 원인은 이쪽이다 — 서버 로직과 쿼리의 성능.

## 인덱스 — 조회 속도의 절대다수

```sql
CREATE INDEX idx_rental_member ON rental(member_no);

EXPLAIN SELECT * FROM rental WHERE member_no = 3;
```

- 인덱스 없는 WHERE는 **전체 행을 다 읽는다**(풀 스캔). 10만 건에서 체감이 수백 배 갈린다
- 걸 곳: WHERE·JOIN·ORDER BY에 자주 쓰는 컬럼. PK와 UNIQUE에는 자동으로 걸려 있다
- `EXPLAIN`을 쿼리 앞에 붙이면 인덱스를 탔는지(type: ref/range)·풀 스캔인지(type: ALL) 보인다 — "인덱스 추가로 조회 1.2s → 8ms" 같은 근거가 여기서 나온다
- 공짜는 아니다: 인덱스는 INSERT·UPDATE를 약간 느리게 한다. 조회 패턴이 있는 곳에만 건다

## N+1 — 반복문 안의 쿼리

```java
// 나쁨 — 목록 1번 + 행마다 1번 = N+1번 쿼리
for (RentalDto r : rentals) {
    BookDto b = bookDao.findByNo(r.getBookNo());
}
```

```sql
-- 좋음 — JOIN으로 1번
SELECT r.no, m.name, b.title
FROM rental r
JOIN member m ON r.member_no = m.no
JOIN book b ON r.book_no = b.no;
```

- 목록 100건이면 쿼리 101번이 나가는 구조다. **반복문 안에 dao 호출이 보이면 무조건 의심** — JOIN 한 방으로 바꾼다
- 발견법: 콘솔에 SQL을 로그로 찍어 두면 화면 하나에 같은 모양 쿼리가 수십 줄 찍히는 게 바로 보인다

## 필요한 만큼만 — LIMIT과 컬럼 선택

```sql
SELECT no, title, author
FROM book
ORDER BY no DESC
LIMIT 20 OFFSET 40;
```

- 전체를 자바로 가져와 자바에서 자르지 않는다 — **거르고 자르는 건 DB가** 하게 한다(WHERE·LIMIT·집계 전부)
- `SELECT *` 대신 쓸 컬럼만: 전송량과 메모리가 같이 준다. COUNT가 필요하면 행을 다 가져와 세지 말고 `SELECT COUNT(*)`를 쓴다

## 연결과 트랜잭션 비용

- DB 연결을 여닫는 것 자체가 비싸다 — 반복문 안에서 getConnection을 부르는 구조는 N+1의 연결판이다. 한 작업 한 연결로 묶고, 규모가 커지면 커넥션 풀로 간다
- 여러 쓰기를 개별 커밋하면 커밋마다 디스크를 기다린다 — 대량 INSERT는 한 트랜잭션으로 묶으면 수십 배 빨라진다(addBatch/executeBatch가 그 도구)

## 측정 루틴

```java
long t = System.nanoTime();
ArrayList<RentalDto> list = dao.findAllWithNames();
System.out.printf("findAll: %.1fms, %d건%n", (System.nanoTime() - t) / 1e6, list.size());
```

- DAO 메소드에 시간 로그를 넣어 두면 어떤 쿼리가 느린지 상시 보인다
- 테스트 데이터를 **수천~수만 건** 넣고 재야 차이가 드러난다(10건에서는 뭘 해도 빠르다). 더미 INSERT를 만들어 두는 것도 실력이다
