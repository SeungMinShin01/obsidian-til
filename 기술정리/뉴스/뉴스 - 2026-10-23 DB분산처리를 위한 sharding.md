---
출처: Claude 분석(데일리 인풋)
원본: https://techblog.woowahan.com/2687/
작성일: 2026-10-23
성격: 예습자료
tags: [학습, spring, sql]
---

# 뉴스 - 2026-10-23 DB분산처리를 위한 sharding

> 상위: [[뉴스 인덱스]]
> 이전: [[뉴스 - 2026-10-22 알아낸 것과 결정한 것 사이에서 2년이 갔다]]
> 다음: [[뉴스 - 2026-10-23 비밀은 금고가 아니라 기록 속에서 샜다]]

우아한형제들 신사업부문 Thiiing팀(송재욱, 전병두) · 2020-07-06 · Backend

## 배경

글은 서비스 오픈 전에 "급성장 시점에 DB가 병목이 되면 안 된다"는 걱정에서 샤딩을 준비했다고 설명한다. 데이터 급증이나 특정 DB로의 트래픽 쏠림에 대비해 운영 중에도 빠르고 안전하게 증설할 수 있어야 했고, 외부 솔루션 대신 Spring 안에서 직접 구현해 모듈러·레인지 두 전략을 지원했다고 한다.

## 핵심

- 공통 요구사항: 유일한 샤딩키(PK) / 올바른 DB로의 라우팅 / 설정만으로 증설 가능.
- 모듈러 샤딩: PK를 DB 수로 나눈 나머지로 결정. 균일 분산이 장점이고 증설 시 기존 데이터 재정렬이 단점. 글은 데이터량이 일정한 곳(오픈 시점 콘텐츠 보존 24시간)에 어울린다고 본다.
- 레인지 샤딩: PK 범위로 결정. 증설 시 재정렬 비용이 없는 대신 활성 유저가 몰린 DB에 쏠릴 수 있다. 마지막 샤드의 range_max를 샤딩키 max값으로 두면 증설을 예약하듯 설정할 수 있다고 한다.
- yaml 설정: 데이터소스 이름 `slave-[module]-[index]`, 샤드마다 master/slave HA, slave 여럿이면 RoundRobin. 명명규칙이 곧 라우팅 규칙이다.
- `AbstractRoutingDataSource`를 상속한 DataSourceRouter의 `determineCurrentLookupKey()`에서 ThreadLocal의 샤딩 타겟·키로 샤드 번호를 정하고, 현재 트랜잭션 readOnly 여부로 master/slave를 고른다.
- `LazyConnectionDataSourceProxy`로 커넥션 획득을 실제 쿼리 시점까지 미뤄야 라우터가 그때 타겟을 결정할 수 있다고 설명한다.
- ThreadLocal(UserHolder)에 샤딩 정보를 담고 사용 후 반드시 초기화한다. 스레드 재사용 시 값이 남기 때문.
- `@Sharding` + RepositoryServiceAspect(`@Around`): RepositoryService 메서드의 첫 번째 파라미터가 샤딩키라는 팀 규약. find*는 `readOnly=true` + `REQUIRES_NEW`로 slave, 쓰기는 `readOnly=false`로 master.
- 유니크 샤딩키 생성(id generator)은 별도 과제. 증설 절차는 물리 DB 추가 → yaml 추가 → 배포.

## 내 프로젝트와의 연결

WMS에 샤딩을 직접 넣을 일은 드물지만 구조적으로 비슷한 지점이 있다. readOnly 트랜잭션 기준의 읽기/쓰기 라우팅은 조회(재고·이력)와 쓰기(입출고) 분리 실험으로 옮겨볼 수 있고, ThreadLocal 정리는 스레드 풀·동시성 테스트 전반에 해당한다. 샤딩키 선택(접근 패턴에 맞는 키)은 창고/로케이션 단위 분할을 가정할 때의 사고 틀이 된다. 수집기와는 연결이 약하다.

## 오늘 정리할 것

1. `determineCurrentLookupKey()` 호출 시점과, `LazyConnectionDataSourceProxy`가 없으면 라우팅이 안 되는 이유를 소스/문서에서 확인해 한 줄로 정리.
2. 모듈러 vs 레인지의 장단점 표 + "WMS 재고 테이블이라면 어떤 키·전략이 맞을지" 2줄.
3. ThreadLocal 미초기화 시 스레드 풀에서 생기는 버그를 작은 예제로 재현.
4. `readOnly=true`가 master/slave 라우팅에 쓰이는 원리와 `REQUIRES_NEW`를 쓴 이유를 자기 말로 설명.
