---
출처: Claude 분석(데일리 인풋)
원본: https://techblog.woowahan.com/2655/
작성일: 2026-10-21
성격: 예습자료
tags: [학습]
---

# 뉴스 - 2026-10-21 Spock Extension과 Elasticsearch + Kibana 조합으로 테스트 결과를 빠르게 피드백 받기

> 상위: [[뉴스 인덱스]]
> 이전: [[뉴스 - 2026-10-20 완료 보고는 증거가 아니고, 산출량은 품질이 아니다]]

정용준 · 2019.12.16 · Backend / QA·Testing (예습자료 — 사용자 미검증)

## 배경
글은 버그가 드러나는 시점이 코드가 개발된 직후이므로 테스트 수행과 결과 피드백 사이의 간격이 짧을수록 원인을 빨리 찾는다고 설명한다. 수동 회귀 테스트는 이 간격이 길고, 로컬에서만 도는 자동화 테스트도 배포 직후 즉시 실행하거나 결과를 공유하기 어렵다는 점이 출발점이다. 그래서 회원·푸시 API 리그레션 테스트를 자동화하고, 결과를 Elasticsearch로 보내 Kibana로 거의 실시간 확인하게 구성했다고 한다.

## 핵심
- Rest-Assured + Spock으로 API 테스트 작성. Gradle 멀티모듈(`service-api-test` 아래 `member-internal-api`, `member-legacy-api`, `member-external-api`, `push-internal-api`, `push-legacy-api`, `commons`)
- Spock 확장: Built-in(`@Ignore`, `@Timeout`, `@Rule`, `@Retry`, `@Stepwise` 등 어노테이션 기반) / Custom(Global Extension, Annotation Driven Local Extension)
- 전체 테스트의 시작~종료를 기록해야 해서 Global Extension 선택. `META-INF/services/org.spockframework.runtime.extension.IGlobalExtension` 파일에 구현 클래스(`TestReportExtension`)를 적어두면 실행 시 자동 동작
- 상태별 작업은 `AbstractRunListener` 상속 리스너. 콜백 파라미터: `SpecInfo`(클래스), `FeatureInfo`(feature 메서드), `IterationInfo`(데이터 드리븐 세트), `ErrorInfo`(실패)
- Spec/Feature/Iteration 전후 시점에 JSON을 만들어 Elasticsearch로 전송
- Elasticsearch·Kibana는 docker 이미지로 실행
- 테스트 서버 배포 직후 자동 실행되도록 Jenkins Job 등록 → 수분 이내 실행, Kibana 대시보드로 확인, 실패 상세 조회 가능
- 사례: 관련 시스템 RDS 교체 후 약 10분 만에 부작용 없음 확인. 다만 글쓴이도 팀 도메인 일부에만 적용된 상태라고 밝힌다
- 반려한 대안을 따로 비교하는 서술은 글에 없다(수동 회귀 vs 자동화 + 즉시 피드백의 대비만 제시)

## 내 프로젝트와의 연결
직접 연결은 약하다(Spock/Groovy, Jenkins, ELK는 쓰는 스택이 아님). 구조적으로 비슷한 지점만: 수집기는 무인 파이프라인이라 "실행 결과를 구조화해 남기고 한눈에 본다"는 요구가 같고, 테스트 훅(시작/성공/실패/종료)에서 JSON을 내보내는 발상은 수집기 단계별 성공·실패·건수를 SQLite에 한 줄씩 적는 실행 로그와 대응된다. WMS는 입고·재고·출고 API 회귀 테스트를 배포 직후 자동 실행해 리팩터링·인덱스 추가 후 부작용 여부를 빠르게 확인하는 방식으로 옮겨볼 수 있다(JUnit의 Extension/TestExecutionListener가 Spock Global Extension과 비슷한 위치).

## 오늘 정리할 것
1. JUnit 5에서 글의 IGlobalExtension에 해당하는 것(Extension, TestExecutionListener, ServiceLoader 자동 등록)을 찾아 한 줄씩 비교해 적기
2. 글의 JSON 전송 단위(Spec/Feature/Iteration/Error)를 보고 수집기 실행 로그 테이블에 필요한 컬럼 3~5개 적기
3. WMS 핵심 API 3개(입고·재고 조회·출고)의 "배포 직후 돌릴 회귀 테스트 목록"을 한 줄씩 정리하기
4. 글이 언급한 '살충제 패러독스'가 무엇인지 찾아 정리하기
