---
출처: Claude 분석
원본: KDT_2026/2026B_BE/src/database/day03.sql
작성일: 2026-08-10
tags: [학습, sql]
---

# SQL day03 — DML과 조인

> 실습 파일: `database/day03.sql` (DML 4종 + member/buy 테이블 + 샘플 데이터), `database/practice3.sql` (서점 스키마 DML·조회 20문제)
> 허브: [[CS 이론 MOC]] · 이전: [[SQL day02 테이블과 제약조건]] · 다음: [[SQL day04 집계와 정렬]]

## 1. 배운 내용

### 1-1. INSERT

```sql
INSERT INTO TEST(NO, NAME, COUNT) VALUES(1, "유재석", 10);
INSERT INTO TEST(NAME, COUNT) VALUES("강호동", 20);   -- 번호는 AUTO_INCREMENT로 자동
INSERT INTO TEST(NAME) VALUES("신동엽");              -- 나머지는 DEFAULT
INSERT INTO TEST VALUES(4, "하하", 30);               -- 전체 순서대로면 컬럼명 생략 가능
INSERT INTO TEST(NAME) VALUES("박명수"),("수박박"),("바나나나");  -- 다중 삽입
```

**컬럼명은 되도록 명시합니다.** 컬럼명을 생략하면 나중에 테이블 구조가 바뀔 때 조용히 깨집니다.

`UNIQUE` 컬럼에 중복 값을 넣으면 에러가 납니다.

### 1-2. SELECT

```sql
SELECT * FROM TEST;                          -- 전체 조회
SELECT NAME FROM TEST;                       -- 특정 컬럼
SELECT NAME, COUNT FROM TEST;
SELECT NAME FROM TEST WHERE NAME LIKE '%동%'; -- 부분 일치
SELECT * FROM TEST WHERE COUNT >= 5;
```

**`LIKE` 와일드카드**: `%`는 0글자 이상, `_`는 정확히 1글자

```sql
LIKE '김%'     -- 김으로 시작
LIKE '%수'     -- 수로 끝남
LIKE '%동%'    -- 동이 포함
LIKE '김_'     -- 김 + 한 글자
```

### 1-3. UPDATE / DELETE

```sql
UPDATE TEST SET COUNT = 10;                              -- WHERE 없음 → 전체!
UPDATE TEST SET COUNT = 30 WHERE NAME LIKE '%동%';
UPDATE TEST SET COUNT = 40, NAME = "강호동" WHERE NO = 7;  -- 여러 컬럼

DELETE FROM TEST;                       -- WHERE 없음 → 전체 삭제!
DELETE FROM TEST WHERE NAME LIKE '%수%';
DELETE FROM TEST WHERE NO = 2;
```

### 1-4. member / buy 테이블 — 조인의 재료

```sql
create table member(              # 아이돌 그룹
  mid char(8) not null,           # 식별키
  mname varchar(10) not null,     # 그룹명
  mnumber int not null,           # 인원수
  maddr char(2) not null,         # 지역
  mphone1 char(3),                # 지역번호
  mphone2 char(8),                # 전화번호
  mheight smallint,               # 평균키
  mdebut date,                    # 데뷔일
  constraint primary key (mid)
);

create table buy(
  bnum int auto_increment,        # 구매번호
  mid char(8),                    # 구매자 FK
  bpname char(6) not null,        # 제품명
  bgname char(4),                 # 분류명
  bprice int not null,            # 가격
  bamount smallint not null,      # 구매수량
  constraint primary key(bnum),
  constraint foreign key (mid) references member(mid)
);
```

**1:N 관계**입니다. 회원 한 명이 여러 번 구매할 수 있습니다. 이 구조가 조인을 배우는 표준 예제입니다.

### 1-5. practice3 — DML·조회 20문제

`database/practice3.sql`에서 서점 스키마(`books` 1 : N `orders`)로 DML과 `WHERE` 조건을 스무 문제 풀었습니다. 문제 1~9가 INSERT/UPDATE/DELETE, 10~20이 SELECT입니다.

**INSERT — 컬럼 목록을 명시하는 형태**

```sql
INSERT INTO BOOKS(BOOK_ID, TITLE, AUTHOR, GENRE, PRICE, STOCK, PUB_DATE)
    VALUES (1012, 'MySQL 실습', '김민수', '컴퓨터', 17000, 25, '2023-03-01');

INSERT INTO ORDERS(BOOK_ID, CUSTOMER, ORDER_QTY, ORDER_DATE)
    VALUES (1002, '최지훈', 1, '2023-08-15');   -- order_id는 AUTO_INCREMENT라 목록에서 뺀다
```

`AUTO_INCREMENT` 컬럼은 아예 목록에서 빼는 방식과 `VALUES(NULL, ...)`로 자리를 채우는 방식 둘 다 됩니다. 컬럼 목록을 쓰면 어느 쪽 값이 어디로 들어가는지 눈에 보이니 1-1에서 정리한 대로 명시하는 편이 안전합니다. 재고가 없는 도서는 `STOCK`에 `NULL`을 그대로 넣습니다.

**UPDATE — 값 대입, 산술 대입, NULL 채우기**

```sql
UPDATE BOOKS SET PRICE = 15000 WHERE BOOK_ID = 1004;          -- 지정 값
UPDATE BOOKS SET PRICE = PRICE + 2000 WHERE GENRE = '소설';    -- 기존 값 기준 인상
UPDATE BOOKS SET STOCK = 0 WHERE STOCK IS NULL;                -- NULL 정리
```

가운데 줄이 핵심입니다. `SET PRICE = PRICE + 2000`처럼 **오른쪽의 컬럼명은 수정 전 값**이라, 일괄 인상·할인은 이 한 줄이면 됩니다. 세 번째 줄의 조건을 `STOCK = NULL`로 쓰면 한 행도 안 걸립니다 — `NULL` 비교는 `IS NULL`뿐입니다. → 2-5

**DELETE — 조건이 곧 안전장치**

```sql
DELETE FROM ORDERS WHERE CUSTOMER = '이서연';
DELETE FROM BOOKS  WHERE STOCK <= 0;
DELETE FROM ORDERS WHERE ORDER_QTY >= 3;
```

`orders.book_id`가 `books.book_id`를 참조하는 외래키라, 부모인 `books`를 지울 때 자식 주문이 남아 있으면 막힙니다. 이 실습 파일은 외래키에 `ON DELETE CASCADE`를 걸어 두어 부모가 지워지면 관련 주문도 함께 사라집니다 — 편한 만큼 지워지는 범위가 넓으니 지우기 전에 `SELECT`로 대상을 먼저 확인하는 순서가 필요합니다. → 2-1, SQL day05 외래키 CASCADE와 조인

**SELECT — WHERE 조건 문법 총정리**

```sql
SELECT TITLE, PRICE FROM BOOKS WHERE PRICE > 20000;
SELECT TITLE, PRICE, STOCK FROM BOOKS WHERE PRICE >= 15000 AND STOCK >= 10;   -- AND
SELECT TITLE, GENRE FROM BOOKS WHERE GENRE IN ('컴퓨터', '경제');              -- IN
SELECT * FROM BOOKS WHERE NOT GENRE = '소설';                                  -- NOT
SELECT TITLE, STOCK FROM BOOKS WHERE STOCK IS NULL;                            -- IS NULL
SELECT TITLE, PRICE FROM BOOKS WHERE PRICE BETWEEN 14000 AND 18000;            -- BETWEEN(양끝 포함)
SELECT TITLE, AUTHOR FROM BOOKS WHERE TITLE LIKE '%자%';                       -- 포함
SELECT TITLE, AUTHOR FROM BOOKS WHERE AUTHOR LIKE '김__';                      -- 김 + 정확히 2글자
```

정리하면 이렇습니다.

| 조건 | 대신 쓸 수 있는 형태 | 메모 |
| --- | --- | --- |
| `IN (a, b)` | `= a OR = b` | 값이 늘어날수록 IN이 짧다 |
| `BETWEEN a AND b` | `>= a AND <= b` | **양끝을 포함**한다 |
| `NOT 조건` | `!=` / `<>` | NULL인 행은 어느 쪽에도 안 걸린다 |
| `IS NULL` | (없음) | `= NULL`은 항상 거짓 |
| `LIKE '김__'` | (없음) | `_`는 정확히 1글자, `%`는 0글자 이상 |

`NOT GENRE = '소설'`처럼 부정 조건을 쓸 때 장르가 `NULL`인 행은 결과에서 빠진다는 점이 자주 놓치는 부분입니다. `NULL`은 참도 거짓도 아니라서, 부정을 씌워도 통과하지 못합니다.

## 2. 추가로 알면 좋은 활용법

### 2-1. WHERE 없는 UPDATE/DELETE의 위험

```sql
UPDATE TEST SET COUNT = 10;   -- 모든 행이 10이 됨!
DELETE FROM TEST;             -- 전체 삭제!
```

**실무 습관 3가지**

**① 먼저 SELECT로 대상 확인**
```sql
SELECT * FROM TEST WHERE NO = 2;   -- 이것만 지워지는지 확인
DELETE FROM TEST WHERE NO = 2;
```

**② Safe Update Mode 켜두기**
MySQL Workbench에서 PK 없는 UPDATE/DELETE를 막아줍니다.

**③ 트랜잭션으로 감싸기**
```sql
START TRANSACTION;
DELETE FROM TEST WHERE ...;
SELECT * FROM TEST;   -- 결과 확인
COMMIT;   -- 또는 ROLLBACK;
```

### 2-2. JOIN — 이 테이블로 바로 해볼 것

```sql
-- 내부 조인: 구매 기록이 있는 그룹만
SELECT m.mname, b.bpname, b.bprice, b.bamount
FROM member m
JOIN buy b ON m.mid = b.mid;

-- 외부 조인: 구매 기록이 없는 그룹도 포함
SELECT m.mname, b.bpname
FROM member m
LEFT JOIN buy b ON m.mid = b.mid;
```

`오마이걸`, `잇지`는 구매 기록이 없으므로 `INNER JOIN`에서는 빠지고 `LEFT JOIN`에서는 `NULL`로 나옵니다.

JS 과제 LevelUP과 게시판 의 `map` + `find`가 정확히 `LEFT JOIN`입니다.

| SQL | JS |
| --- | --- |
| `JOIN ... ON` | `map` + `find` |
| `LEFT JOIN` | `map` + `find` + `??` |
| `WHERE` | `filter` |
| `SUM()` | `reduce` |
| `ORDER BY` | `sort` |
| `COUNT()` | `length` |

**조인 종류** (정보처리기사 노트에 정리된 이론)

| 종류 | 설명 |
| --- | --- |
| 세타 조인 | 모든 비교 연산자(`=` `>` `<` `>=` `<=` `!=`) 사용 |
| 동등 조인 | 세타 조인 중 등호(`=`)만 사용 — 가장 일반적 |
| 자연 조인 | 동등 조인에서 중복 속성 제거 |
| 외부 조인 | LEFT/RIGHT/FULL — 조건 불만족 튜플도 NULL로 포함 |

### 2-3. 집계와 GROUP BY

```sql
SELECT COUNT(*), AVG(mheight), MAX(mnumber), MIN(mdebut) FROM member;

-- 지역별 그룹 수
SELECT maddr, COUNT(*) AS 그룹수
FROM member
GROUP BY maddr;

-- 그룹별 총 구매액 (10만원 이상만, 많은 순)
SELECT m.mname, SUM(b.bprice * b.bamount) AS 총구매액
FROM member m JOIN buy b ON m.mid = b.mid
GROUP BY m.mname
HAVING 총구매액 >= 100000
ORDER BY 총구매액 DESC;
```

**`WHERE` vs `HAVING`**
- `WHERE` — 그룹핑 **전**에 행을 거름
- `HAVING` — 그룹핑 **후** 집계 결과를 거름
- 집계 함수(`SUM`, `COUNT`)는 `HAVING`에서만 사용 가능

**실행 순서**
```
FROM → JOIN → WHERE → GROUP BY → HAVING → SELECT → ORDER BY → LIMIT
```

`SELECT`가 거의 마지막이라 **`SELECT`에서 만든 별칭을 `WHERE`에서 못 쓰는** 이유가 이것입니다. (MySQL은 `HAVING`, `ORDER BY`에서는 허용합니다)

### 2-4. 서브쿼리

```sql
-- 평균 키보다 큰 그룹
SELECT mname FROM member
WHERE mheight > (SELECT AVG(mheight) FROM member);

-- 구매 기록이 있는 그룹
SELECT mname FROM member
WHERE mid IN (SELECT DISTINCT mid FROM buy);

-- 구매 기록이 없는 그룹
SELECT mname FROM member
WHERE mid NOT IN (SELECT mid FROM buy WHERE mid IS NOT NULL);
```

**`NOT IN` 주의**: 서브쿼리 결과에 `NULL`이 하나라도 있으면 전체가 빈 결과가 됩니다. `NOT EXISTS`가 안전합니다.

**`ALL` / `ANY`** (정보처리기사 노트)
- `ALL` — 서브쿼리의 **모든** 값과 비교
- `ANY` — 서브쿼리의 **임의의** 값과 비교

### 2-5. NULL 다루기

```sql
SELECT * FROM member WHERE mphone1 IS NULL;      -- = NULL 은 안 됨!
SELECT * FROM member WHERE mphone1 IS NOT NULL;
SELECT IFNULL(mphone1, '없음') FROM member;
SELECT COALESCE(mphone1, mphone2, '연락처 없음') FROM member;
```

**`NULL`은 "값이 없음"이라 `=`로 비교할 수 없습니다.** `오마이걸`, `잇지`의 전화번호가 `NULL`인 게 이 실습 데이터의 포인트입니다.

`COUNT(*)`는 NULL 포함, `COUNT(컬럼)`은 NULL 제외라는 것도 자주 나오는 함정입니다.

### 2-6. 날짜 다루기

```sql
INSERT INTO member VALUES('TWC', '트와이스', 9, '서울', '02', '11111111', 167, '2015.10.19');
```

MySQL은 `'2015.10.19'` 형태도 받아주지만 **표준 표기는 `'2015-10-19'`** 입니다.

```sql
SELECT * FROM member WHERE mdebut >= '2016-01-01';
SELECT YEAR(mdebut), MONTH(mdebut) FROM member;
SELECT DATEDIFF(NOW(), mdebut) AS 데뷔일수 FROM member;
SELECT DATE_FORMAT(mdebut, '%Y년 %m월 %d일') FROM member;
```

## 3. 더 나아가 알면 좋은 것

### 3-1. SQL 인젝션

```java
// 위험!
String sql = "SELECT * FROM member WHERE mid = '" + input + "'";
// input = "' OR '1'='1" 이면 전체 행이 조회됩니다
```

```java
// 안전
String sql = "SELECT * FROM member WHERE mid = ?";
PreparedStatement ps = con.prepareStatement(sql);
ps.setString(1, input);
```

`PreparedStatement`는 값을 **데이터로만** 취급해서 SQL 구문으로 해석되지 않습니다. 정보처리기사 보안 파트의 SQL 인젝션이 정확히 이 이야기이고, JS day11 DOM 조작 의 XSS와 같은 부류의 문제입니다.

### 3-2. VIEW

```sql
CREATE VIEW 구매내역 AS
SELECT m.mname, b.bpname, b.bprice * b.bamount AS 금액
FROM member m JOIN buy b ON m.mid = b.mid;

SELECT * FROM 구매내역 WHERE 금액 >= 100000;
```

자주 쓰는 조회를 **가상 테이블**로 저장합니다. 복잡한 조인을 매번 쓰지 않아도 됩니다.

### 3-3. EXPLAIN으로 성능 진단

```sql
EXPLAIN SELECT * FROM member WHERE mname = '트와이스';
```

| type | 의미 |
| --- | --- |
| `const` / `eq_ref` | 최고 (PK·UNIQUE 조회) |
| `ref` | 좋음 (인덱스 사용) |
| `range` | 보통 |
| `ALL` | **전체 스캔 — 인덱스가 필요** |

느린 쿼리를 만나면 가장 먼저 보는 도구입니다.

### 3-4. 다음 단계

| 주제 | 내용 |
| --- | --- |
| `TRIGGER`, `PROCEDURE` | DB 안에서 도는 로직 |
| 트랜잭션 격리 수준 | READ COMMITTED, REPEATABLE READ 등 |
| ORM (JPA/Hibernate) | 자바 객체 ↔ 테이블 자동 매핑 |
| NoSQL | Redis(캐시), MongoDB(문서) |

Java day09 ArrayList 3-4의 "영속화 로드맵"과 이어집니다.

## 실습 파일

- `2026B_BE/src/database/day03.sql`
- `2026B_BE/src/database/practice3.sql` (books/orders 연습문제 20개 — INSERT·UPDATE·DELETE·WHERE 조건)

## 관련 노트

[[CS 이론 MOC]] · [[SQL day02 테이블과 제약조건]] · [[SQL day04 집계와 정렬]] · SQL day05 외래키 CASCADE와 조인 · JS 과제 LevelUP과 게시판 · Java day09 ArrayList · JS day14 게시판 CRUD
