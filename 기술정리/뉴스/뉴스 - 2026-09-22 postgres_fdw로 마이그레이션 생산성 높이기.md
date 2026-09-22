---
출처: Claude 분석(데일리 인풋)
원본: https://techblog.woowahan.com/20371/
작성일: 2026-09-22
성격: 예습자료
tags: [학습, sql]
---

# 뉴스 - 2026-09-22 postgres_fdw로 마이그레이션 생산성 높이기

> 상위: [[뉴스 인덱스]]
> 이전: [[뉴스 - 2026-09-21 내 데이터와 내 모델은 누가 쥐고 있나]]
> 다음: [[뉴스 - 2026-09-22 생성이 싸질 때 청구서는 읽는 쪽으로 간다]]

**원문**: [postgres_fdw로 마이그레이션 생산성 높이기](https://techblog.woowahan.com/20371/) — 권순호, 김수홍 · 2024.12.12 · Backend

## 배경

글은 배민 커머스 서비스(B마트·배민스토어·장보기 등)가 초기에 독립 시스템으로 각자 성장하다가, 규모가 커지자 중복 시스템의 운영 비용 때문에 '상품' 도메인을 하나로 통합하게 된 상황에서 출발한다. 1차(B마트) 통합 때는 Spring Batch로 마이그레이션 애플리케이션을 만들어 옮겼지만, 2차(배민스토어) 때는 배치 코드 없이 SQL만으로 옮기자며 postgres_fdw(PostgreSQL이 원격 PostgreSQL 테이블을 로컬 테이블처럼 다루는 Foreign Data Wrapper 모듈)를 택했다고 설명한다. 이벤트 기반 아키텍처 덕에 조회 트래픽이 상품 DB로 직접 오지 않았고, 새벽엔 셀러 활동도 없어 "마이그레이션 중 데이터 변경 없음"을 전제할 수 있었던 것이 채택의 조건이었다고 한다.

## 핵심

- 설정 4단계: `CREATE EXTENSION postgres_fdw` → `CREATE SERVER`(호스트·포트·dbname) → `CREATE USER MAPPING`(원격 유저 매핑) → `CREATE FOREIGN TABLE`(또는 `IMPORT FOREIGN SCHEMA`). 이후 원격 테이블을 로컬 SQL로 조회·조작할 수 있다
- 대부분의 테이블은 `INSERT ~ SELECT` 한 방으로 이관했다고 한다 — enum 변환은 CASE, 신규 컬럼은 상수, 필터링은 WHERE로. 배치 코드의 빌드·배포 과정 자체가 사라진다
- 4억 row 중 유효 데이터가 700만 row뿐인 테이블은 Foreign table에 직접 INSERT~SELECT 하니 40분 넘게 끝나지 않았고 → 원본 DB 쪽에서 `CREATE TABLE AS`로 700만 건짜리 사전 필터링 테이블을 만들어 그것만 이관하자 10분 내로 단축됐다고 한다
- DBA 자문의 핵심 규칙: **Local table ↔ Foreign table 조인 금지**. postgres_fdw는 fetch_size(기본 100)만큼 커서로 반복 fetch하는데, 로컬-원격 조인은 최악의 경우 원격 테이블 전체를 `SELECT *`로 끌어온 뒤 조인한다(사실상 FullScan). MySQL FEDERATED·SQL Server Linked Server도 동일한 함정이라고 짚는다
- 회피책: 원격 데이터를 미리 로컬 테이블(또는 Materialized View)로 복사해 로컬끼리 조인, CTE로 조회 대상 축소, fetch_size 상향(근본 해결책은 아니라고 명시)
- 복잡한 JSON 다층 구조(상품정보제공고시)는 단일 쿼리를 포기하고 3단계로: ① 매핑 테이블 생성 → ② Foreign table 조인은 전처리 단계에서 미리 수행해 원시 데이터 테이블 생성 → ③ 로컬끼리만 조인해 최종 INSERT
- 운영 당일 절차: 레거시 CUD 기능 차단 → RDS 스냅샷으로 마이그레이션 전용 DB 생성(서비스 영향 차단) → fdw 설정 → 쿼리 실행. 천만 건 단위를 45분 내 완료했다고 한다
- 주의사항: fdw는 원격에 INSERT/UPDATE/DELETE/TRUNCATE도 가능하므로 전용 유저 최소 권한 + `updatable=false, truncatable=false` 권장. 분산 트랜잭션(2PC) 미지원, 원격 트랜잭션은 REPEATABLE READ 자동 설정. 작업 후 Foreign table·fdw 설정 제거는 자원·보안상 필수라고 강조한다
- 배치 방식과 비교: 장점은 즉시 피드백(INSERT 전 SELECT로 결과 미리보기)·롤백 부담 없음·일회성 코드 관리 불필요, 단점은 복잡한 변환 로직의 SQL 표현 한계·테스트 코드 부재로 수동 검증 필요

## 내 프로젝트와의 연결

WMS에서 "재고 데이터 이관"이나 "레거시 테이블 구조 변경" 상황이 오면 같은 갈림길에 선다 — 배치 코드를 짤 것인가, SQL로 옮길 것인가. 글의 판단 기준(트래픽 차단 가능 여부, 데이터 변경 없음 전제, 변환 규칙의 복잡도)이 그대로 결정 로그 재료다. WMS는 MySQL이라 postgres_fdw 대신 같은 DB 안 스키마 간 INSERT~SELECT나 FEDERATED가 대응물이고, "원격-로컬 조인은 FullScan"이라는 함정은 수집기의 SQLite를 다른 저장소로 옮기는 상상을 할 때도 같은 구조다. 특히 "대량 테이블은 원본 쪽에서 먼저 필터링 테이블을 만들어라"는 전략은 DB 종류와 무관하게 옮겨 쓸 수 있어 보인다.

## 오늘 정리할 것

1. WMS의 MySQL에서 `INSERT ~ SELECT`로 테이블 간 데이터 복사를 직접 실행해 보고, 대량일 때 트랜잭션·락이 어떻게 걸리는지 확인
2. `CREATE TABLE AS SELECT`(CTAS)가 MySQL에서는 어떻게 되는지(MySQL 8의 CTAS 제약) 찾아서 정리
3. "짧은 트랜잭션으로 쪼개라"는 권고의 근거 — 긴 트랜잭션이 undo/MVCC에 주는 부담을 한 문단으로 정리
4. RDS 스냅샷으로 복제 DB를 만들어 작업하는 절차를 WMS 배포 계획 관점에서 시뮬레이션(어느 시점에 뜨고, 얼마나 걸리는지)

## 남는 질문

- 글은 "데이터 변경 없음"을 전제로 했는데, 무중단으로 옮겨야 한다면(CDC·이중 쓰기) 어느 지점부터 fdw 방식이 무너지는가?
- fetch_size를 얼마로 올리면 어느 정도까지 개선되는지 수치는 글에 없다 — 직접 재봐야 알 수 있는 부분
