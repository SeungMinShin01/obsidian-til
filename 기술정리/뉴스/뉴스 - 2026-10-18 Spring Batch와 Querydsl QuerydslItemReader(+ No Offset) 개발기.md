---
출처: Claude 분석(데일리 인풋)
원본: https://techblog.woowahan.com/2662/
작성일: 2026-10-18
성격: 예습자료
tags: [학습, spring, sql]
---

# 뉴스 - 2026-10-18 Spring Batch와 Querydsl QuerydslItemReader(+ No Offset) 개발기

> 상위: [[뉴스 인덱스]]
> 이전: [[뉴스 - 2026-10-16 기준선을 다시 재자 이득이 줄었고, 증류는 문을 닫았다]]

이동욱 · 2020-02-05 · Backend (우아한형제들 기술블로그). 예습자료이므로 아래는 "글은 ~라고 설명한다" 관점이며 사용자가 검증한 내용이 아니다.

## 배경

글은 정산시스템팀이 JPA + Querydsl을 쓰는데 Spring Batch가 Querydsl Reader를 공식 지원하지 않는다고 설명한다. 그래서 배치마다 AbstractPagingItemReader를 상속한 Reader와 페이징용 Repository를 따로 만들었고, 배치와 무관한 반복 코드(offset/limit 처리, results 채우기)와 신입 설명 비용이 늘었다고 한다. 100여 개 테이블·수십 개 배치를 운영해 Querydsl의 타입 안정성·컴파일 체크는 포기하기 어려웠고, ORDER BY id OFFSET n LIMIT m 페이징은 뒤 페이지로 갈수록 느려졌다.

## 핵심

- 문제: limit 10000, 20은 10,020행을 읽고 앞 10,000행을 버린다. 뒤 페이지일수록 비용이 커진다.
- 반려한 대안: ① 커버링 인덱스(id만 서브쿼리 조회 후 조인) — JPQL이 FROM절 서브쿼리를 지원하지 않아 불가, ② JpaPagingItemReader — Querydsl 장점을 잃고 offset 제거도 불가, ③ 배치마다 Reader 직접 작성 — 반복 코드·설명 비용.
- QuerydslPagingItemReader: JpaPagingItemReader에서 JPQL 실행부(doReadPage)만 Querydsl로 교체. createQuery()가 private이라 override가 안 돼 소스를 통째로 복사했다. 생성자에서 `Function<JPAQueryFactory, JPAQuery<T>>`를 받아 람다로 쿼리를 전달한다.
- EntityTransaction 코드 제거: `hibernate.default_batch_fetch_size`가 트랜잭션 commit 단위로 동작하는데 페이지 단위 트랜잭션이 이를 방해해서. 대신 Chunk 단위 트랜잭션으로 롤백이 정상 동작함을 확인했다고 한다.
- QuerydslNoOffsetPagingItemReader: offset 없이 limit만 쓰고, 마지막 아이템의 기준값을 캐시해 다음 페이지에 ASC면 `> 값`, DESC면 `< 값` 조건을 자동 추가. 기준 필드는 QClass 필드로 지정(`QuerydslNoOffsetNumberOptions`/`StringOptions`).
- 첫 페이지는 min()/max()로 시작 기준값을 구해 where에 넣는다 — 안 그러면 where 없는 전체 정렬이 발생하기 때문(인덱스 최소/최대만 읽어 비용 작음).
- 제약: Reader 쿼리에 order by/group by가 없거나 단일 기준 필드(PK·인덱스)여야 한다. 엔티티 Reader는 chunkSize = pageSize 권장. 검증 버전은 Spring Boot 2.1.3~2.2.4.
- 성능: 86.9만 건 21분 → 4분 36초(마지막 페이지 읽기 2.4초 → 0.03초), 118.9만 건 55분 → 2분 27초(5초 → 0.08초).

## 내 프로젝트와의 연결

수집기: 수집한 채용공고를 SQLite에서 대량으로 읽어 후처리·내보내기 할 때 OFFSET 페이징을 쓰면 같은 구조의 문제가 생길 수 있다. "마지막 id 기준으로 다음 구간을 읽는" 방식은 SQLite에서도 옮길 수 있고, 마지막 id를 저장하면 재개 지점이 되어 재시도·멱등성 설계와도 닿는다. WMS: 재고·입출고 이력처럼 쌓이는 테이블을 목록/배치로 훑을 때 인덱스 기준 keyset 페이징이 후보가 된다. 기준 필드가 유일해야 누락·중복이 없다는 전제는 글이 명시하지 않아 직접 확인이 필요하다.

## 오늘 정리할 것

1. `LIMIT 10000, 20` 같은 OFFSET 쿼리가 앞 행을 읽고 버리는 것을 EXPLAIN으로 offset 값을 바꿔가며 확인해 보기.
2. `id > 마지막값 ORDER BY id LIMIT n`(keyset)과 OFFSET 방식을 같은 더미 데이터에서 돌려 실행 시간 비교 정리하기.
3. 기준 필드 값이 중복될 때 keyset이 누락·중복을 내는 예를 만들어 보고, 해결책(복합 기준에 id 추가)을 한 줄로 적기.
4. JdbcCursorItemReader / JpaPagingItemReader / RepositoryItemReader 차이를 표로 정리하기.
