---
출처: Claude 분석
작성일: 2026-08-10
tags: [CS, MOC, 허브]
---

# CS 이론 MOC

CS 이론·정보처리기사·데이터베이스 노트의 허브입니다. 상위 지도는 [[KDT_2026 학습 지도]].

## 데이터베이스 (day별)

| day | 노트 | 핵심 |
| --- | --- | --- |
| 01 | [[SQL day01 데이터베이스 기초]] | DB 개념, SQL 4분류, DDL |
| 02 | [[SQL day02 테이블과 제약조건]] | 자료형, PK/FK, 스키마 설계 |
| 03 | [[SQL day03 DML과 조인]] | INSERT/SELECT/UPDATE/DELETE, JOIN, 정규화 |
| 04 | [[SQL day04 집계와 정렬]] | GROUP BY, 집계함수, HAVING, ORDER BY, LIMIT 페이징 |

## 기타

- [[피그마 메모(이관)]] — 디자인 툴, Auto Layout ↔ flexbox 대응

## 노션에 남아있는 정보처리기사 노트

다음 항목은 노션 `CS 이론` 폴더에 원본 그대로 있습니다.

**요약1** — DB 스키마 3계층, 트랜잭션 ACID, 회복 기법(Redo/Undo, 로그·체크포인트·그림자 페이징), 동시성 제어(Locking)

**day01** — Watering Hole, DB 설계 절차, 디자인 패턴(Bridge/Observer), ISMS

**1** — 비기능 요구사항, 공격기법 7종, 사회공학, 다크 데이터, 빅데이터 신기술(Hadoop/HDFS/Chukwa/Sqoop/Scrapy), 데이터 웨어하우스·마이닝·마트, 디자인 패턴 10종, 서브넷팅, ER 다이어그램, 조인 종류, 응집도·결합도, Fan-in/Fan-out, 무결성 제약조건, 데이터 링크 프로토콜(HDLC/PPP/ATM), 오류 제어(FEC/BEC/해밍코드/CRC), 프로세스 스케줄링, IPC, 테스트 커버리지, 테스트 오라클, 스텁/드라이버, 파일 구조(순차/인덱스/해싱)

## 실습과 이론의 연결

정보처리기사 이론이 실제 코드에서 어디에 나타나는지 짚어두면 훨씬 잘 붙습니다.

| 이론 | 실제 코드 |
| --- | --- |
| 트랜잭션 ACID | [[SQL day03 DML과 조인]] `COMMIT`/`ROLLBACK` |
| 무결성 제약조건 | [[SQL day02 테이블과 제약조건]] `PRIMARY KEY`, `FOREIGN KEY` |
| 조인 종류 | [[SQL day03 DML과 조인]] / [[JS 과제 LevelUP과 게시판]] 배열 조인 |
| 정규화 | [[SQL day02 테이블과 제약조건]] `activity.sql` 7개 테이블 |
| XSS | [[JS day11 DOM 조작]] `innerHTML` 처리 |
| SQL 인젝션 | [[SQL day03 DML과 조인]] `PreparedStatement` |
| 응집도·결합도 | [[Java day07 메소드와 미니프로젝트]] Controller/Repository 분리 |
| 캡슐화 | [[Java day08 접근제한자와 static]] private + getter/setter |
| 다형성·인터페이스 | [[Java 오버로딩 오버라이딩과 인터페이스(이관)]] |
| 부동소수점 | [[Java day01 자바 구조와 자료형]] / [[JS day03 자료형과 연산자]] |
| 비트 연산(서브넷) | [[Java day03 연산자]] |
| 시간 복잡도 | [[JS day05 반복문]] / [[Java day04 제어문과 배열]] |
