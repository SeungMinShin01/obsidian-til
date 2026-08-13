---
출처: Claude 분석
원본: KDT_2026/2026B_BE/src/database/day02.sql, activity.sql
작성일: 2026-08-10
tags: [학습, sql]
---

# SQL day02 — 테이블과 제약조건

> 실습 파일: `database/day02.sql`, `activity.sql`(세탁 서비스 스키마), `practice2.sql`
> 허브: [[CS 이론 MOC]] · 이전: [[SQL day01 데이터베이스 기초]] · 다음: [[SQL day03 DML과 조인]]

## 1. 배운 내용

### 1-1. 테이블 DDL

```sql
CREATE TABLE test1(필드명1 INT, 필드명2 DOUBLE, 필드명3 TEXT);

SHOW TABLES;
DESCRIBE test1;
DROP TABLE test1;

ALTER TABLE test1 ADD 필드명4 FLOAT;                    -- 컬럼 추가
ALTER TABLE test1 MODIFY 필드명3 LONGTEXT;              -- 타입 변경
ALTER TABLE test1 CHANGE 필드명1 필드명5 BIGINT;         -- 이름 + 타입 변경
RENAME TABLE test1 TO new_test1;                       -- 테이블명 변경
TRUNCATE TABLE new_test1;                              -- 레코드 전체 삭제 (구조 유지)
```

**`MODIFY` vs `CHANGE`**: `MODIFY`는 타입만, `CHANGE`는 이름까지 바꿉니다. `CHANGE`는 새 이름과 타입을 **둘 다** 써야 합니다.

**`DELETE` vs `TRUNCATE` vs `DROP`**

| | 대상 | 롤백 | 속도 |
| --- | --- | --- | --- |
| `DELETE FROM t` | 레코드 (DML) | 가능 | 느림 |
| `TRUNCATE TABLE t` | 레코드 (DDL) | **불가** | 빠름 |
| `DROP TABLE t` | 테이블 자체 (DDL) | **불가** | - |

### 1-2. 자료형

| 분류 | 타입 |
| --- | --- |
| 정수 | `TINYINT`(1B) `SMALLINT`(2B) `MEDIUMINT`(3B) `INT`(4B) `BIGINT`(8B) |
| 실수 | `FLOAT` `DOUBLE` `DECIMAL` |
| 날짜 | `DATE` `TIME` `DATETIME` `TIMESTAMP` |
| 문자 | `CHAR(n)` `VARCHAR(n)` `TEXT` `LONGTEXT` |
| 논리 | `BOOLEAN` (실제로는 `TINYINT(1)`) |

짚어둘 포인트가 세 가지 있습니다.

**`UNSIGNED`** — 부호를 없애 양수 범위를 2배로
```
TINYINT          -128 ~ 127
TINYINT UNSIGNED    0 ~ 255
```

**`CHAR` vs `VARCHAR`**
```
"수박" → CHAR(3):    [수][박][공백]  ← 고정 길이, 남는 자리를 채움
       → VARCHAR(3): [수][박]        ← 가변 길이
```
`CHAR`는 길이가 항상 같은 값(주민번호, 우편번호, 코드), `VARCHAR`는 제각각인 값(이름, 제목)에 씁니다.

**`DECIMAL`** — 문자 기반이라 **소수점 오차가 없습니다.** 느리지만 **돈 계산에는 필수**입니다.
Java의 `BigDecimal`([[Java day01 자바 구조와 자료형]]), JS의 정수 변환([[JS day03 자료형과 연산자]])과 같은 맥락입니다.

`TEXT`는 `VARCHAR`와 달리 기본값을 줄 수 없고 인덱스에 제약이 있습니다. 길이를 예측할 수 있으면 `VARCHAR`가 낫습니다.

### 1-3. 제약조건

```sql
CREATE TABLE test3 (
    필드명1 TINYINT NOT NULL,         -- NULL 저장 금지
    필드명2 SMALLINT UNIQUE,          -- 중복 금지
    필드명3 INT DEFAULT 100,          -- 기본값
    필드명4 DATETIME DEFAULT now(),   -- 삽입 시각 자동
    필드명5 BIGINT AUTO_INCREMENT,    -- 자동 증가 (1, 2, 3...)
    CONSTRAINT PRIMARY KEY(필드명5)
);
```

**PK(기본키)** = `NOT NULL` + `UNIQUE`가 내장된 식별 키. 테이블당 1개
**FK(외래키)** = 다른 테이블의 PK를 참조하는 키

```sql
CREATE TABLE test4 (
    필드명1 BIGINT,
    CONSTRAINT FOREIGN KEY (필드명1) REFERENCES test3(필드명5)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);
```

| 참조 옵션 | PK가 삭제/수정되면 |
| --- | --- |
| `CASCADE` | FK 행도 같이 삭제/수정 |
| `SET NULL` | FK를 NULL로 |
| `RESTRICT` (기본) | FK가 있으면 삭제/수정 자체를 거부 |

**`CASCADE`는 위험합니다.** 회원을 지우면 그 회원의 글·댓글이 전부 사라집니다. 실무에서는 `RESTRICT`를 두고 "탈퇴 상태" 컬럼으로 관리하는 경우가 많습니다.

### 1-4. activity.sql — 세탁 서비스 스키마 설계

이 파일이 day02의 하이라이트입니다. 7개 테이블로 실제 서비스 스키마를 설계했습니다.

```
CATEGORY ─┐
          ├─→ CLOTHES ─┬─→ CLOTHESSYMBOLLIST ─→ WASHINGSYMBOL
MATERIAL ─┘            └─→ CLOTHESDRYINGLIST  ─→ DRYINGGUIDE

WASHINGGUIDE (의류별 세탁법)
```

**N:M 관계를 중간 테이블로 푼 설계**가 핵심입니다.

옷 한 벌에 세탁 기호가 여러 개, 세탁 기호 하나가 여러 옷에 쓰입니다. 관계형 DB는 N:M을 직접 표현할 수 없어서 `CLOTHESSYMBOLLIST` 같은 **연결(중간) 테이블**을 둡니다.

```sql
CREATE TABLE CLOTHESSYMBOLLIST (
    CLOTHESID INT,
    SYMBOLID INT,
    CONSTRAINT FOREIGN KEY (CLOTHESID) REFERENCES CLOTHES(COLTHESID),
    CONSTRAINT FOREIGN KEY (SYMBOLID) REFERENCES WASHINGSYMBOL(SYMBOLID)
);
```

이 스키마가 그대로 [[Java day07 메소드와 미니프로젝트]] 의 `의류`, `의류별세탁법` 클래스가 되었습니다. **DB 테이블 → 자바 클래스** 매핑이 DTO의 본질입니다. → [[Java day08 접근제한자와 static]]

### 1-5. practice2 — 쇼핑몰 스키마 4테이블

`database/practice2.sql`은 회원·상품·주문·주문상세 구조를 직접 설계한 실습입니다.

```sql
DROP DATABASE IF EXISTS PRACTICE2;
CREATE DATABASE PRACTICE2;
USE PRACTICE2;

-- 1번 회원
CREATE TABLE MEMBERS(
    MEMBER_ID   INT PRIMARY KEY AUTO_INCREMENT,
    MEMBER_NAME VARCHAR(50) NOT NULL,
    EMAIL       VARCHAR(100) NOT NULL UNIQUE,
    JOIN_DATE   DATETIME DEFAULT now(),
    IS_ACTIVE   BOOLEAN DEFAULT TRUE
);

-- 2번 상품
CREATE TABLE PRODUCTS(
    PRODUCT_ID   INT PRIMARY KEY AUTO_INCREMENT,
    PRODUCT_NAME VARCHAR(100) NOT NULL,
    PRICE        INT UNSIGNED NOT NULL,
    STOCK        INT DEFAULT 0 NOT NULL,
    CREATED_AT   DATETIME DEFAULT now()
);

-- 3번 주문
CREATE TABLE ORDERS(
    ORDER_ID    BIGINT PRIMARY KEY AUTO_INCREMENT,
    MEMBER_ID   INT,
    ORDER_DATE  DATETIME DEFAULT now(),
    TOTAL_PRICE INT UNSIGNED NOT NULL,
    FOREIGN KEY (MEMBER_ID) REFERENCES MEMBERS(MEMBER_ID)
);

-- 4번 주문상세
CREATE TABLE ORDER_ITEMS(
    ITEM_ID  INT PRIMARY KEY AUTO_INCREMENT,
    ORDER_ID BIGINT,
    ...
);
```

**제약조건은 목적에 맞게 골라 써야 합니다.**

| 컬럼 | 제약 | 이유 |
| --- | --- | --- |
| `EMAIL` | `NOT NULL UNIQUE` | 로그인 식별자라 중복 불가 |
| `JOIN_DATE` | `DEFAULT now()` | 가입 시각 자동 기록 |
| `IS_ACTIVE` | `DEFAULT TRUE` | 탈퇴를 플래그로 관리 (소프트 삭제) |
| `PRICE` | `INT UNSIGNED` | 가격은 음수가 될 수 없음 |
| `STOCK` | `DEFAULT 0 NOT NULL` | 재고 미입력 시 0 |
| `ORDER_ID` | `BIGINT` | 주문은 회원보다 훨씬 많이 쌓임 |

**`UNSIGNED`로 음수를 원천 차단**하고, **주문 테이블만 `BIGINT`로 키운 것**이 실무 감각에 맞는 판단입니다. 회원 수는 `INT`(21억)로 충분하지만 주문·로그는 더 빨리 쌓입니다.

`IS_ACTIVE BOOLEAN DEFAULT TRUE`는 **소프트 삭제** 패턴입니다. 회원을 실제로 지우면 그 회원의 주문 기록도 참조가 깨지므로, 플래그만 `FALSE`로 바꾸는 방식이 안전합니다.

**주문 ↔ 주문상세를 나눈 이유**

주문 1건에 상품이 여러 개 담기므로 1:N입니다. 한 테이블에 넣으면 주문 정보(주문일, 회원)가 상품 수만큼 반복됩니다.

```
ORDERS (주문 1건)
  └─ ORDER_ITEMS (상품 N개)
```

[[JS 과제 LevelUP과 게시판]] 의 `주문`/`주문상세` 분리, [[JS day12 제품 사원 관리 CRUD]] 의 카테고리/제품 분리와 완전히 같은 사고입니다.

## 2. 추가로 알면 좋은 활용법

### 2-1. 중간 테이블의 복합 PK

```sql
CREATE TABLE CLOTHESSYMBOLLIST (
    CLOTHESID INT,
    SYMBOLID INT,
    CONSTRAINT PRIMARY KEY (CLOTHESID, SYMBOLID),   -- 복합 기본키
    CONSTRAINT FOREIGN KEY (CLOTHESID) REFERENCES CLOTHES(CLOTHESID),
    CONSTRAINT FOREIGN KEY (SYMBOLID) REFERENCES WASHINGSYMBOL(SYMBOLID)
);
```

복합 PK를 두면 **같은 조합이 두 번 들어가는 것을 DB가 막아줍니다.** 지금은 PK가 없어서 중복 저장이 가능합니다.

### 2-2. 자주 쓰는 컬럼 설계 관례

```sql
CREATE TABLE board (
    no        INT PRIMARY KEY AUTO_INCREMENT,
    title     VARCHAR(200) NOT NULL,
    content   TEXT,
    writer    VARCHAR(50) NOT NULL,
    view_cnt  INT DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    deleted   BOOLEAN DEFAULT FALSE     -- 소프트 삭제
);
```

- `created_at` / `updated_at` — 거의 모든 테이블에 넣습니다
- `deleted` — 실제로 지우지 않고 플래그만 세우는 **소프트 삭제**. 복구 가능하고 통계도 남습니다
- `ON UPDATE CURRENT_TIMESTAMP` — 수정 시각 자동 갱신

[[JS day14 게시판 CRUD]] 의 `boardList` 객체와 비교해보면 실제 DB가 얼마나 더 챙기는지 보입니다.

## 3. 더 나아가 알면 좋은 것

### 3-1. 정규화

`activity.sql`은 이미 잘 정규화되어 있습니다.

| 단계 | 규칙 | activity.sql |
| --- | --- | --- |
| 1NF | 모든 값이 원자적 (한 칸에 여러 값 금지) | O |
| 2NF | 부분 함수 종속 제거 | O |
| 3NF | 이행적 함수 종속 제거 | `CATEGORY`, `MATERIAL` 분리 |

만약 `CLOTHES`에 `CATEGORYNAME`을 직접 넣었다면, "상의"를 "윗옷"으로 바꿀 때 **모든 행을 수정**해야 합니다. 별도 테이블로 빼면 한 행만 고치면 됩니다. **이게 정규화의 실익입니다.**

반대로 조회 성능을 위해 일부러 중복을 두는 것을 **비정규화**라고 하며, 대규모 서비스에서 씁니다.

### 3-2. 인덱스

```sql
CREATE INDEX idx_clothes_name ON CLOTHES(CLOTHESNAME);
SHOW INDEX FROM CLOTHES;
```

PK와 UNIQUE에는 인덱스가 자동 생성됩니다. `WHERE`, `JOIN`, `ORDER BY`에 자주 쓰는 컬럼에 인덱스를 걸면 검색이 극적으로 빨라집니다.

대신 `INSERT`/`UPDATE`가 느려지고 저장 공간을 더 씁니다. **읽기를 빠르게, 쓰기를 느리게** 하는 트레이드오프입니다.

주의: `WHERE name LIKE '%동%'`처럼 앞에 `%`가 오면 인덱스를 못 씁니다. 책의 색인이 "ㄱ으로 시작하는 단어"는 찾아도 "중간에 ㄱ이 든 단어"는 못 찾는 것과 같습니다.

### 3-3. 스키마 설계 순서

1. **요구사항 분석** — 무엇을 저장해야 하는가
2. **개념적 설계** — ER 다이어그램 (개체·관계·속성)
3. **논리적 설계** — 테이블·컬럼·관계로 변환, 정규화
4. **물리적 설계** — 자료형, 인덱스, 파티션
5. **구현** — `CREATE TABLE`

`정보처리기사 day01` 노트의 "데이터베이스 설계 절차"가 정확히 이것입니다. `activity.sql`은 3~5단계 결과물입니다.

**ER 다이어그램 표기** (정보처리기사 노트에 정리되어 있습니다)
- 사각형 = 개체 집합 / 마름모 = 관계 집합 / 타원 = 속성 / 밑줄 타원 = 기본키

### 3-4. JDBC로 연결하기

```java
String sql = "INSERT INTO CLOTHES(CLOTHESNAME, CATEGORYID) VALUES(?, ?)";
try (Connection con = DriverManager.getConnection(url, id, pw);
     PreparedStatement ps = con.prepareStatement(sql)) {
    ps.setString(1, 의류명);
    ps.setInt(2, 카테고리ID);
    ps.executeUpdate();
}
```

`activity.sql`의 스키마와 [[Java day07 메소드와 미니프로젝트]] 의 클래스가 이미 1:1 대응이라, JDBC만 붙이면 메모리 저장이 DB 저장으로 바뀝니다.

## 실습 파일

- `2026B_BE/src/database/day02.sql`
- `2026B_BE/src/database/activity.sql`
- `2026B_BE/src/database/practice2.sql`

## 관련 노트

[[CS 이론 MOC]] · [[SQL day01 데이터베이스 기초]] · [[SQL day03 DML과 조인]] · [[Java day07 메소드와 미니프로젝트]] · [[Java day08 접근제한자와 static]]
