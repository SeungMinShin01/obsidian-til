---
출처: Claude 분석(데일리 인풋)
원본: https://techblog.woowahan.com/2661/
작성일: 2026-10-05
성격: 예습자료
tags: [학습, java]
---

# 뉴스 - 2026-10-05 Gradle 프로젝트에 JaCoCo 설정하기

> 상위: [[뉴스 인덱스]]
> 이전: [[뉴스 - 2026-10-04 하네스가 회사가 된다는 날, OS는 권한을 조였다]]
> 다음: [[뉴스 - 2026-10-05 멈춤과 폐기를 기본값으로]]

**오늘의 글** — Gradle 프로젝트에 JaCoCo 설정하기 · 연철(상품시스템팀) · 2020-02-02 · Backend / QA·Testing

## 배경

글은 상품시스템팀이 프로젝트를 세팅하며 겪은 삽질을 정리한 것이다. 팀은 커버리지 기준을 조금씩 올려 가며, 기준을 못 맞추면 배포를 막고 있다고 설명한다(브랜치 커버리지 100% 프로젝트도 있다고 한다). 그래서 Java와 Kotlin이 섞인 Gradle 프로젝트에서 JaCoCo를 어떻게 설정하는지를 다룬다. 글은 Gradle 6.0.1·JaCoCo 0.8.5 기준이며, 이전 버전에서 필요하던 다중 언어 소스 경로 설정은 이제 큰 설정 없이 된다고 말한다.

## 핵심

- 플러그인에는 task가 둘이다. `jacocoTestReport`는 바이너리 결과를 html/xml/csv 리포트로 만들고(xml·csv는 SonarQube 연동용), `jacocoTestCoverageVerification`은 기준 충족 여부를 빌드 성공/실패로 알려 준다.
- `test` task에서 `useJUnitPlatform()`을 주지 않으면(JUnit5) 테스트가 돌지 않아 두 JaCoCo task가 스킵된다고 설명한다.
- 순서를 `test → jacocoTestReport → jacocoTestCoverageVerification`으로 고정하지 않으면, 검증이 먼저 실패해 리포트가 갱신되지 않고 옛 리포트를 보게 될 수 있다. 그래서 `dependsOn`으로 묶고 `mustRunAfter`로 순서를 지정한 `testCoverage` task(group=`verification`)를 만든다.
- 매번 부르기 번거로우면 `test`에 `finalizedBy`를 걸어 자동 실행한다. 글은 이것을 "개인 취향"이라 한다.
- `violationRules`의 세 축: `element`(BUNDLE 기본·PACKAGE·CLASS·SOURCEFILE·METHOD), `counter`(INSTRUCTION 기본·LINE·BRANCH·CLASS·METHOD·COMPLEXITY), `value`(COVEREDRATIO 기본·MISSEDRATIO·TOTALCOUNT 등).
- 비율은 `BigDecimal`이라 `0.8`로 쓰면 결과도 `0.4`처럼 유효자리까지만 표시된다(`0.80`이면 `0.42`). 예제는 브랜치 33%·라인 42%로 90%·80% 기준을 못 넘어 실패시킨다. 여러 룰을 어기면 처음 위반한 룰만 보고된다.
- 제외는 `excludes`에 **경로가 아닌 패키지+클래스명**(와일드카드 `*`·`?`)으로 적는다. 글쓴이는 경로로 적어 헤맸다고 하며, QueryDsl이 생성하는 `Q*.class`와 spring-batch 설정 파일이 제외 대상 예로 나온다.
- 리포트 색: 초록은 커버, 빨강은 놓침, 노랑은 조건 일부만 테스트(if의 true/false 중 한쪽만).

## 내 프로젝트와의 연결

WMS(Spring Boot)에서는 입고·재고·출고 같은 상태 전이와 동시성 로직이 커지기 시작하면 "어느 분기를 테스트가 안 건드렸는지"가 보이는 장치가 필요해진다. 글의 노란색 줄(한쪽 분기만 테스트됨)이 재고 부족/충분 같은 경계 분기를 점검하는 데 구조적으로 비슷한 지점이다. 수집기는 GitHub Actions 파이프라인이므로, `testCoverage` 같은 검증 task를 워크플로 단계에 넣어 기준 미달이면 빌드를 실패시키는 방식으로 옮겨 볼 수 있다(수집기가 Java가 아니면 직접 연결은 약하다 — 그 경우 "게이트로서의 커버리지"라는 발상만 해당).

## 오늘 정리할 것

1. WMS 빌드 파일에서 `jacoco` 플러그인 적용 여부와 `useJUnitPlatform()` 설정을 확인하고, 없으면 `jacocoTestReport`만 먼저 돌려 html 리포트를 열어 본다.
2. `counter`(LINE/BRANCH/INSTRUCTION)와 `element`(CLASS/PACKAGE)의 차이를 표로 정리하고, 지금 코드에서 어느 조합이 의미 있는지 적는다.
3. `excludes`에 넣을 후보(QueryDsl `Q*`, 설정 클래스, DTO)를 목록화하되, 패키지+클래스명 형식으로 적어 본다.
4. `test → report → verification` 순서가 깨지면 무엇이 보이는지(옛 리포트) 일부러 `mustRunAfter`를 빼서 재현해 본다.
