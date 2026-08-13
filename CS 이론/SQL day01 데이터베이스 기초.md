---
출처: Claude 분석
원본: KDT_2026/2026B_BE/src/database/DB.txt, day01.sql
작성일: 2026-08-10
tags: [학습, sql]
---

# SQL day01 — 데이터베이스 기초

> 실습 파일: `database/DB.txt`, `day01.sql`, `practice1.sql`
> 허브: [[CS 이론 MOC]] · 다음: [[SQL day02 테이블과 제약조건]]

## 1. 배운 내용

### 1-1. 용어 — DB.txt

| 용어 | 정의 |
| --- | --- |
| **데이터베이스** | 여러 사람·프로그램이 공유하여 사용할 수 있도록 모은 데이터 집합 |
| **데이터베이스 서버** | MySQL 등. 요청에 따라 데이터를 처리하고 응답하는 프로그램 |

**특징 4가지**: 실시간 접근, 동시 공유, 내용에 의한 참조, 지속적인 변화

**종류**: 관계형 데이터베이스(RDB) / NoSQL

### 1-2. SQL 4분류

| 분류 | 이름 | 명령어 | 트랜잭션 |
| --- | --- | --- | --- |
| **DDL** | 데이터 정의어 | `CREATE` `DROP` `ALTER` `TRUNCATE` `RENAME` | **불가 (auto-commit)** |
| **DML** | 데이터 조작어 | `INSERT` `SELECT` `UPDATE` `DELETE` | 가능 |
| **DCL** | 데이터 제어어 | `GRANT` `REVOKE` (접근 권한·계정 관리) | - |
| **TCL** | 트랜잭션 제어어 | `COMMIT` `ROLLBACK` | - |

핵심은 이 한 문장입니다.
> DDL은 트랜잭션 불가능, DML은 취소(ROLLBACK) 가능

**`DELETE`(DML)는 롤백되지만 `TRUNCATE`(DDL)는 안 됩니다.** 실무에서 매우 중요한 차이입니다.

### 1-3. 실행 방법

```sql
-- 1. SQL 문법 작성
-- 2. ; 세미콜론으로 마침
-- 3. 실행할 문장에 커서를 두고 Ctrl+Enter (또는 RUN)
-- 전체 실행: Ctrl+Shift+Enter
```

**SQL 문법은 대소문자를 구분하지 않습니다.** 관례적으로 키워드는 대문자, 식별자는 소문자로 씁니다.

### 1-4. 데이터베이스 조작 — day01.sql

```sql
SHOW DATABASES;                        -- 서버 내 모든 DB 목록
SHOW VARIABLES LIKE 'datadir';         -- DB 파일의 로컬 경로 확인

CREATE DATABASE mydb0804;              -- 생성
DROP DATABASE mydb0804;                -- 삭제
DROP DATABASE IF EXISTS mydb0804;      -- 존재하면 삭제 (안전)

USE mydb0804;                          -- 활성화 (조작할 DB 선택)
```

**`IF EXISTS`가 중요합니다.** 없는 DB를 `DROP`하면 에러가 나서 스크립트가 중단됩니다.

### 1-5. 좋은 습관 — DROP부터 시작하기

```sql
DROP DATABASE IF EXISTS boardService;
CREATE DATABASE boardService;
USE boardService;
```

**DROP부터 쓰는 습관**을 들이면 스크립트를 몇 번 실행해도 **항상 같은 결과**가 나옵니다. 이 성질을 **멱등성(idempotency)** 이라고 합니다.

개발 중에는 매우 유용하지만, **운영 DB에서는 절대 금지**입니다. 데이터가 전부 날아갑니다.

### 1-6. practice1 — 제출용 실습

`database/practice1.sql`은 문제와 답을 한 파일에 담은 제출용 과제입니다.

```sql
/* [문제 1] 데이터베이스 생성 */
CREATE DATABASE my_db;

/* [문제 2] 데이터베이스 목록 확인 */
SHOW DATABASES;

/* [문제 3] 데이터베이스 사용 */
USE my_db;

/* [문제 4] 데이터베이스 삭제 */
DROP DATABASE my_db;

/* [문제 5] company_db가 존재하면 삭제 → 생성 → 활성화 */
DROP DATABASE IF EXISTS company_db;
CREATE DATABASE company_db;
USE company_db;
```

문제를 주석으로 남기고 그 아래에 답을 쓰는 형식으로 정리했습니다. 나중에 다시 봐도 "이 SQL이 무엇을 하려던 것인지"가 남습니다.

5번이 1~4번을 합친 문제입니다. `DROP IF EXISTS → CREATE → USE` 3단 콤보가 실습 스크립트의 표준 시작 형태이고, 이후 `day02.sql`, `day03.sql`, `activity.sql`, `practice2.sql`에서 전부 이 패턴으로 시작합니다.

## 2. 추가로 알면 좋은 활용법

### 2-1. `USE` 없이 작업하기

```sql
USE mydb;
SELECT * FROM member;

-- 또는 DB명을 직접 명시
SELECT * FROM mydb.member;
```

여러 DB를 오가며 작업할 때는 `DB명.테이블명`이 실수를 줄여줍니다. **어느 DB에 있는지 헷갈려서 엉뚱한 곳에 테이블을 만드는 사고**가 은근히 자주 납니다.

```sql
SELECT DATABASE();   -- 현재 활성 DB 확인
```

### 2-2. 유용한 확인 명령

```sql
SHOW DATABASES;
SHOW TABLES;
DESCRIBE 테이블명;              -- 또는 DESC
SHOW CREATE TABLE 테이블명;     -- 생성 SQL 그대로 보기
SHOW INDEX FROM 테이블명;
SELECT VERSION();
```

`SHOW CREATE TABLE`은 남이 만든 테이블 구조를 이해할 때 가장 빠른 방법입니다.

### 2-3. 문자셋 설정

```sql
CREATE DATABASE mydb
  DEFAULT CHARACTER SET utf8mb4
  COLLATE utf8mb4_general_ci;
```

**한글과 이모지를 제대로 저장하려면 `utf8mb4`가 필요합니다.** MySQL의 `utf8`은 사실 3바이트라 이모지(4바이트)가 안 들어갑니다. 이름이 헷갈리는 유명한 함정입니다.

# 한 줄 주석 (MySQL 전용)
/* 여러 줄
   주석 */
```

MySQL은 `#`도 받아주지만 표준 SQL은 `--`입니다. 다른 DBMS로 옮길 때를 생각하면 `--`가 안전합니다.

### 2-4. 계정과 권한 (DCL)

```sql
CREATE USER 'devuser'@'localhost' IDENTIFIED BY 'password';
GRANT SELECT, INSERT, UPDATE ON boardService.* TO 'devuser'@'localhost';
FLUSH PRIVILEGES;

SHOW GRANTS FOR 'devuser'@'localhost';
REVOKE INSERT ON boardService.* FROM 'devuser'@'localhost';
```

**애플리케이션이 `root`로 접속하면 안 됩니다.** 필요한 권한만 가진 계정을 따로 만드는 게 원칙입니다. SQL 인젝션이 터져도 피해 범위가 제한됩니다.

## 3. 더 나아가 알면 좋은 것

### 3-1. 관계형 DB vs NoSQL

| | 관계형 (MySQL, PostgreSQL) | NoSQL (MongoDB, Redis) |
| --- | --- | --- |
| 구조 | 정해진 스키마 (테이블) | 유연 (문서, 키-값) |
| 관계 | JOIN으로 연결 | 중첩 또는 애플리케이션에서 처리 |
| 트랜잭션 | 강력 (ACID) | 제한적 |
| 확장 | 수직 (서버 성능 ↑) | 수평 (서버 대수 ↑) |
| 적합 | 금융, 주문, 정합성 중요 | 로그, 캐시, 대용량 |

**정합성이 중요하면 RDB, 규모와 유연성이 중요하면 NoSQL** 이 대략의 기준입니다.

[[JS day13 웹 스토리지와 인터벌]] 의 `localStorage`는 키-값 저장소라 NoSQL 계열에 가깝습니다.

### 3-2. 트랜잭션과 ACID

`정보처리기사 요약1` 노트의 이론이 여기서 실습이 됩니다.

```sql
START TRANSACTION;
UPDATE account SET balance = balance - 10000 WHERE id = 1;
UPDATE account SET balance = balance + 10000 WHERE id = 2;
COMMIT;      -- 둘 다 성공해야 반영
-- ROLLBACK; -- 하나라도 실패하면 전부 취소
```

| | 의미 |
| --- | --- |
| **A**tomicity (원자성) | All or Nothing |
| **C**onsistency (일관성) | 실행 후에도 일관성 유지 |
| **I**solation (고립성) | 다른 트랜잭션이 끼어들 수 없음 |
| **D**urability (지속성) | 완료된 결과는 영구 저장 |

**주의**: DDL은 auto-commit이라 `ROLLBACK`이 안 됩니다. `CREATE TABLE`을 트랜잭션 안에 넣어도 소용없습니다.

### 3-3. 백업과 복구

```bash
mysqldump -u root -p boardService > backup.sql        # 백업
mysql -u root -p boardService < backup.sql            # 복구
mysqldump -u root -p --all-databases > all.sql        # 전체
```

`DROP DATABASE`를 습관적으로 쓰다 보면 언젠가 사고가 납니다. 중요한 DB는 백업 먼저입니다.

### 3-4. 다음 단계

- [[SQL day02 테이블과 제약조건]] — 테이블 설계
- [[SQL day03 DML과 조인]] — 데이터 조작
- JDBC — [[Java day07 메소드와 미니프로젝트]] 를 실제 DB에 연결

## 실습 파일

- `2026B_BE/src/database/DB.txt`
- `2026B_BE/src/database/day01.sql`, `practice1.sql`

## 관련 노트

[[CS 이론 MOC]] · [[SQL day02 테이블과 제약조건]] · [[SQL day03 DML과 조인]] · [[Java day07 메소드와 미니프로젝트]]
