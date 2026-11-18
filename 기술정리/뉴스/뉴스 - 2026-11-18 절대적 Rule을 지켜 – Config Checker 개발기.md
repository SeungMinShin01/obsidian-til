---
출처: Claude 분석(데일리 인풋)
원본: https://techblog.woowahan.com/7242/
작성일: 2026-11-18
성격: 예습자료
tags: [학습, spring]
---

# 뉴스 - 2026-11-18 절대적 Rule을 지켜 – Config Checker 개발기

> 상위: [[뉴스 인덱스]]
> 이전: [[뉴스 - 2026-11-17 믿고 들인 코드가 무너졌고, 통과는 검사가 아니었다]]
> 다음: [[뉴스 - 2026-11-18 아무도 안 쓰던 최적화가 뚫렸고, 비용은 멈추지 못한 단계에 있었다]]

> [!info] 예습자료 — 무인 세션이 자동 생성, 사용자 미검증

## 오늘의 글

- 제목: 절대적 Rule을 지켜 – Config Checker 개발기
- 저자: 남윤서(시스템신뢰성개발팀, WoowaTech 계정) · 2021-12-30 · Backend
- 원본: https://techblog.woowahan.com/7242/

## 배경

글은 SRE팀이 장애보고서를 월·연 단위로 회고하다가, 2020년 한 해 동안 Spring 애플리케이션 **설정값** 때문에 생긴 다운타임이 4시간 32분이었다는 점을 발견한 데서 출발한다고 설명한다. 원인은 HikariCP 커넥션 풀 크기 부족, DB 커넥션 SSL 사용, Redis 풀 크기 부족, Redis connection timeout 미설정, Aurora failover 미동작이었고, 이런 설정이 코드리뷰로만 걸러지고 있었다는 것이 문제의식이다. 먼저 `최소품질체크리스트`라는 가이드(라이브러리·CP별 주의사항과 추천값)를 만들었지만, 사람이 손으로 설정하는 이상 "적용했다고 착각"하는 실수를 막을 수 없어 자동 검사 시스템을 만들게 됐다고 한다.

## 핵심 (문제 → 시도 → 반려 → 해결)

- **언제 검사할까 — CI 정적 분석은 반려.** properties·yaml을 머지 후 CI에서 읽는 안은 ① 팀마다 CI를 고쳐야 하고 ② 파일은 *입력값*일 뿐 *적용된 값*이 아니며 ③ 적용 여부는 배포 후에야 알 수 있어 CI 성격과 맞지 않는다는 이유로 기각 → **배포 시점 동적 분석**으로.
- **어떻게 검사할까 — 배포 잡 추가도 반려.** 배포 파이프라인에 잡을 넣어 에이전트가 Config Checker API를 호출하는 안은 프로젝트별 스크립트 수정이 필요하고, 하루 수십~수백 번 배포되는 전사 배포 시간을 늘리며, 롤백·핫픽스 같은 긴급 배포까지 느려져 다운타임이 늘고, Checker 장애가 배포 실패로 번질 수 있어 기각. "스킵 옵션"은 사용률 저하로 이어진다고 봤다.
- **공통 단점 = 프로젝트별 적용 비용.** 에이전트 방식은 적용·변경 비용이 프로젝트 수에 비례한다. 플랫폼은 사일로를 없애는 게 목적이므로 NoOps를 지향해야 한다는 결론.
- **최종 구조 — 배포 이벤트 구독.** 배포 완료 → DynamoDB에 배포 내역 저장 → 트리거된 Lambda가 Kafka로 이벤트 발행 → Config Checker가 소비. 배포 시스템을 쓰는 모든 프로젝트에 별도 작업 없이 적용된다.
- **값을 가져오는 방식 — pull.** 이벤트의 인스턴스 정보로 Spring Boot Actuator 엔드포인트를 호출해 설정을 가져온다. 서비스는 `env`·`configprops` 엔드포인트만 열어 주면 된다. 에이전트가 push하던 방식보다 운영 비용이 적다고 한다.
- **`/actuator/env`는 한계.** 환경 변수·JVM 정보·yaml 값이 그대로 나오지만, 같은 HikariCP timeout도 `spring.datasource.hikari.connection-timeout`으로 줄 수도, 커스텀 prefix + `@ConfigurationProperties`로 줄 수도 있어 프로젝트마다 검사 경로가 달라진다.
- **`/actuator/configprops`로 전환.** `@ConfigurationProperties` 빈(AutoConfiguration의 `DataSourceProperties` 등)의 **최종 적용값**이 담겨, 설정 방식이 달라도 prefix만 다를 뿐 dataSource 하위 항목으로 똑같이 보인다 — "입력값 대신 적용값을 검사"가 핵심 전환.
- **Rule 관리.** 기본은 최소품질체크리스트, 서비스별로 값·조건 변경 가능. 전사 Key-Value 저장소에 JSON(`condition`, `ruleValue` 등)으로 두고 런타임에 읽어 Rule 추가에 Checker 재배포가 필요 없다. `condition`은 Predicate 람다를 가진 Enum으로 확장. 결과는 배포 직후 Slack 알람.
- **효과.** 장애가 나면 원인을 Rule로 추가 → 적용 서비스 전체에 재발 방지(선순환). 글 작성 시점까지 설정값 장애가 없었다고 하되, 각 팀의 노력 덕도 있다고 단서를 단다. 다음 과제는 AWS 서비스 설정 검사·k8s 배포 플랫폼 적용.

## 내 프로젝트와의 연결

WMS(Spring Boot)에는 꽤 직접적으로 옮겨올 수 있어 보인다. 글이 꼽은 장애 원인 — HikariCP 풀 크기, 타임아웃, failover — 은 WMS의 부하 테스트·동시성 락 실험에서 바로 드러날 설정들이다. 전사 플랫폼까지는 과하지만, "yaml(입력값)이 아니라 `configprops`(적용값)를 본다"는 원칙은 배포 후 스모크 테스트에서 `/actuator/configprops`를 한 번 찍어 `maximumPoolSize`·`connectionTimeout`이 의도대로 들어갔는지 확인하는 작은 형태로 쓸 수 있다. 수집기(GitHub Actions)와는 구조적으로 비슷한 지점만 있다: "검사 단계를 모든 파이프라인에 끼워 넣지 말고 이벤트를 구독하라"는 판단, 그리고 장애 원인을 Rule로 누적하는 선순환은 수집기 실패 사례를 체크리스트(타임아웃·재시도 설정)로 쌓는 방식과 닮았다.

## 오늘 정리할 것

1. WMS(또는 빈 Spring Boot 프로젝트)에서 `management.endpoints.web.exposure.include=env,configprops`를 켜고, `/actuator/env`와 `/actuator/configprops`에서 HikariCP 항목이 각각 어떻게 보이는지 나란히 비교해 본다.
2. 커스텀 prefix + `@ConfigurationProperties`로 같은 timeout을 줘서, env에서는 경로가 달라지고 configprops에서는 같은 자리에 나오는지 직접 확인한다.
3. 글이 꼽은 다섯 원인(풀 크기·SSL·Redis 풀·Redis timeout·failover)에 대해 Spring Boot 기본값을 찾아 표로 정리하고, WMS에서 바꿀 값/그대로 둘 값을 표시한다.
4. Actuator 엔드포인트를 외부에 열 때의 보안 문제(민감 값 마스킹, `show-values` 설정)를 공식 문서에서 확인해 메모한다.
