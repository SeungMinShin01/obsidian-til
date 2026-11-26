---
출처: Claude 분석(데일리 인풋)
원본: https://techblog.woowahan.com/2575/
작성일: 2026-11-26
성격: 예습자료
tags: [학습, spring]
---

# 뉴스 - 2026-11-26 주소검색서버(woowahan-juso) 개발기(上)

> 상위: [[뉴스 인덱스]]
> 이전: [[뉴스 - 2026-11-25 거절과 채점은 남이 정했고, 라벨부터 다시 재야 했다]]

> [!info] 예습자료 — 글의 주장을 정리한 것이며 사용자가 직접 검증하지 않았다.

**원본**: 주소검색서버(woowahan-juso) 개발기(上) — 부제: SpringBoot Batch를 이용하여 주소DB 구축하기
정세빈(라이더스개발팀, 게시 계정 WoowaTech) · 2018-05-26 · Backend
https://techblog.woowahan.com/2575/

## 배경

배민라이더스의 라이더 운영 시스템 BROS는 픽업지·배달지 주소를 검색·변경할 서버가 필요했다. 글은 juso.go.kr이 주는 세 선택지(주소검색 솔루션, 주소검색 API, txt 원본 데이터) 중 **txt 원본을 받아 자체 DB를 재구축**하는 길을 골랐다고 설명한다. 이유는 세 가지다. ① 솔루션은 일정 기간 업데이트를 안 하면 서비스가 중단되고 API는 데이터를 정부가 관리해, BROS와 배민 사이의 주소 현황 싱크를 직접 통제할 수 없었다. ② 운영 중 테스트용 주소를 DB 차원에서 관리해야 했다. ③ 외부 서비스는 SLA를 보장하지 않아 이벤트 트래픽·장애 시 리스크가 된다. 이렇게 2천만 행이 넘는 txt를 적재하는 작업을 직접 짠 배치 프로세스가 아니라 Spring Batch로 만든 이유와 Job 구성이 이 글(上)의 주제다. 검색 자체(Amazon CloudSearch)는 (下)로 미뤘다.

## 핵심

- **반려한 대안**: 외부 주소검색 API·솔루션 — 데이터 갱신 주기를 남이 정하고 SLA가 없어서. 직접 짠 일반 배치 — 실패 시 처음부터 다시 돌려야 하는 비효율 때문에(글의 자체 Q&A).
- **Spring Batch를 고른 첫째 이유 = 재시작**: 2천만 행 이상의 txt를 미리 전수 검증하기 어렵고(빈 컬럼으로 인한 NPE, Unique 깨지는 데이터로 인한 SQL 예외), 실패했다고 처음부터 재실행하면 비효율적이다. Spring Batch는 `BATCH_JOB_EXECUTION_CONTEXT`·`BATCH_STEP_EXECUTION_CONTEXT` 테이블에 진행 상태를 남겨, 문제를 고친 뒤 **실패 시점부터 재실행**할 수 있었다고 한다.
- **둘째 이유 = 공통 인터페이스**: DB든 플랫파일이든 `ItemReader`/`ItemWriter` 하나의 인터페이스로 Step을 구현해 데이터 형태별 대응·교육 비용을 줄였다.
- **구조**: JobRepository(메타데이터 저장) · JobLauncher(실행 요청 수신) · Job(Step 컨테이너, 재시작 가능성 등 전역 속성) · Step · ItemReader → (ItemProcessor) → ItemWriter.
- **txt → DB Step**: `FlatFileItemReader` + LineTokenizer + FieldSetMapper로 한 줄을 도메인 객체로, `JdbcBatchItemWriter` + `NamedParameterJdbcTemplate`으로 MySQL에 insert. 데이터별(주소·지번·부가·도로명) Step을 각각 만들고 **chunk size**로 트랜잭션 커밋 단위를 정한다.
- **DB → DB Step**: 적재 결과(지번 약 800만·도로명 약 35만)에는 시도·시군구·행정동 목록이 따로 없어 다시 추출한다. `JdbcCursorItemReader`(read SQL·RowMapper를 파라미터로) + `JpaItemWriter`, 제네릭 `createStep` 메서드로 Step을 찍어낸다.
- **순서 보장**: Job에서 `start(jusoStep).next(sido).next(sigungu).next(dongOfAdmin)` — 원본 적재가 끝나야 파생 데이터를 뽑을 수 있으므로.
- **실행**: `-Dspring.batch.job.names=jobName`으로 원하는 Job만 실행.
- (참고) 원문의 코드 블록은 외부 임베드라 본 요약 수집 시 내용이 비어 있었다 — 코드 세부는 원문에서 직접 확인 필요.

## 내 프로젝트와의 연결

**수집기**와 구조적으로 가장 가깝다. 글의 문제("대량 외부 데이터를 적재하다 중간에 깨지면 어디서부터 다시 하나")는 GitHub Actions 무인 수집에서 API 응답 일부가 깨지거나 런이 중간에 죽었을 때와 같은 질문이다. 글은 실행 컨텍스트 테이블에 진행 위치를 남겨 재시작하는 방식을 쓰는데, 수집기의 SQLite 저장 계층에서는 "마지막으로 성공한 페이지/커서"를 별도 테이블에 남기는 방식으로 같은 효과를 낼 수 있는지 따져볼 만하다. chunk 단위 커밋은 "전부 아니면 전무" 대신 일부 성공을 보존하는 트레이드오프이므로, 재실행 시 중복 insert를 막는 멱등성 장치(UNIQUE + upsert)와 짝으로 봐야 한다. 또 "외부 API의 SLA가 보장되지 않아 원본을 받아 자체 저장한다"는 판단 자체가 수집기의 존재 이유와 겹친다. WMS 쪽은 초기 상품·로케이션 마스터 데이터를 대량 적재할 때 Step 순서(원본 → 파생) 개념 정도만 직접 연결된다.

## 오늘 정리할 것

1. Spring Batch 메타 테이블(`BATCH_JOB_INSTANCE`·`BATCH_JOB_EXECUTION`·`BATCH_STEP_EXECUTION`·`*_EXECUTION_CONTEXT`)이 각각 무엇을 저장하는지, 재시작 시 어떤 값(예: `FlatFileItemReader`의 읽은 줄 수)을 쓰는지 표로 정리하기.
2. chunk size가 트랜잭션 경계와 어떻게 맞물리는지, chunk 중간에 예외가 나면 그 chunk는 어떻게 되는지 공식 문서에서 확인하고 skip/retry 정책과 함께 한 장으로 적기.
3. 수집기 SQLite에 "마지막 성공 위치" 체크포인트 테이블을 둔다면 스키마를 어떻게 잡고, 재실행 시 중복을 UNIQUE+UPSERT로 막는 흐름을 의사코드로 써보기.
4. 글이 반려한 "외부 API 직접 호출" vs "원본 받아 자체 DB" 판단 기준(갱신 통제·테스트 데이터·SLA)을 수집기 결정 로그 형식(문제→대안→선택→기각 사유)으로 옮겨 써보기.
