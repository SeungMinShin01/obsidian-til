---
출처: Claude 분석(데일리 인풋)
원본: https://techblog.woowahan.com/2653/
작성일: 2026-09-30
성격: 예습자료
tags: [학습, sql]
---

# 뉴스 - 2026-09-30 Aurora MySQL를 운영하면서 알면 좋을 것 같은 미세한 팁

> 상위: [[뉴스 인덱스]]
> 이전: [[뉴스 - 2026-09-30 에이전트를 켜 두는 날, 새는 곳은 출력 바깥이었다]]

**Aurora MySQL를 운영하면서 알면 좋을 것 같은 미세한 팁** — 유영근(우아한형제들 DBA) · 2019-12-04(2026-01 수정) · Backend, Infra
원본: https://techblog.woowahan.com/2653/

## 배경
글은 Aurora가 MySQL 호환이지만 RDS MySQL·온프레미스와 동작이 달라, 운영 중 예상 밖 상황을 만난다고 설명한다. 두 가지 사례(캐시 워밍, Binlog 사용)를 실험으로 확인한다.

## 핵심
- Aurora는 캐시 레이어가 SQL 엔진과 분리돼 재시작 후에도 캐시가 유지된다고 알려졌지만, 글의 실험에서는 상황에 따라 다르다.
- MySQL의 `innodb_buffer_pool_dump_now` / `load_now`(RDS는 `mysql.rds_innodb_buffer_pool_dump_now()` 등)는 Aurora에서 수동 제어가 불가능하다(마스터 권한도 불가).
- 캐시 워밍 실험: Writer 재시작 시 Writer는 유지되나 Reader는 초기화, Reader 재시작은 둘 다 유지, Reader 추가·Failover 시 Reader 캐시 없음(승격된 Reader는 캐시 유지), 인스턴스 스펙 변경·스냅샷 복원은 둘 다 초기화.
- Reader 신규 추가 직후 초기 쿼리의 Select Latency가 증가한다. 권고: 캐시가 비는 작업은 바쁜 시간대를 피하고, 필요하면 `COUNT(*)` 등으로 수동 워밍.
- Aurora 내부 복제는 binlog를 쓰지 않지만, 계정 간 클러스터 동기화·RDS→Aurora 무중단 마이그레이션·5.6→5.7 무중단 업그레이드에는 binlog 외부 복제가 필요하다.
- 설정: `rds_set_configuration('binlog retention hours', 72)`, 복제 전용 계정(REPLICATION CLIENT/SLAVE), 스냅샷 시점의 binlog position 확인 후 `mysql.rds_set_external_master(...)` → `mysql.rds_start_replication`.
- 성능 영향(r5.xlarge, 100GB, sysbench류): 스레드 32에서 QPS 21,227(binlog OFF) → 20,353(Row, ON) → 11,423(Aurora–Aurora 복제 활성). 128스레드는 23,216 → 21,440 → 16,112. 복제 활성 시 일부 구간에서 QPS가 거의 절반이 된다.
- 결론으로 글은 "Master 부하를 미리 테스트해 QPS 하락을 고려한 스펙을 정하라", "눈으로 확인한 테스트 결과를 신뢰하라"고 말한다. 테스트 버전은 Aurora 2.04.6이라 최신 버전에서는 다를 수 있다고 덧붙인다.

## 내 프로젝트와의 연결
WMS는 배포·부하 테스트 단계에서 DB 재시작이나 스펙 변경 직후 첫 요청이 느려지는 구간을 같은 방식으로 볼 수 있다(Aurora를 쓰지 않더라도 "재시작 후 버퍼 풀이 비어 있다"는 구조는 InnoDB 공통). 또 "기능을 켜기 전과 후를 같은 조건으로 재서 Before/After로 남긴다"는 방법은 WMS 성능 측정 기록과 닮았다. 수집기의 SQLite와는 직접 연결이 약하다. 글은 2019년 기준이므로 현재 Aurora 동작은 사용자 검증이 필요하다.

## 오늘 정리할 것
1. InnoDB buffer pool이 무엇이고 재시작 후 왜 콜드 상태가 되는지 손으로 그림 한 장으로 정리한다(로컬 MySQL에서 `SHOW ENGINE INNODB STATUS`로 hit rate 확인).
2. WMS 부하 테스트 계획에 "재시작 직후 워밍 구간 제외" 항목을 넣을지 메모한다.
3. binlog ON/OFF가 쓰기 성능에 주는 영향을 로컬 MySQL에서 `log_bin` 토글로 간단히 재보고 수치를 남긴다.
