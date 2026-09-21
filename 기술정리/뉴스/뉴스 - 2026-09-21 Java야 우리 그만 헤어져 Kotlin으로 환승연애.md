---
출처: Claude 분석(데일리 인풋)
원본: https://techblog.woowahan.com/22586/
작성일: 2026-09-21
성격: 예습자료
tags: [학습, java, spring]
---

# 뉴스 - 2026-09-21 Java야 우리 그만 헤어져 Kotlin으로 환승연애

> 상위: [[뉴스 인덱스]]
> 이전: [[뉴스 - 2026-09-20 에이전트가 시스템을 뚫기 시작했다]]
> 다음: [[뉴스 - 2026-09-21 내 데이터와 내 모델은 누가 쥐고 있나]]

**원문**: [Java야…, 우리 그만 헤어져. Kotlin으로 환승연애](https://techblog.woowahan.com/22586/) — 주지민 · 2025.07.22 · Backend

## 배경

글은 배민페이플랫폼팀이 2018년부터 Java로 운영해온 포인트 시스템을 2025년 상반기에 Kotlin으로 전면 전환한 과정을 설명한다. 코드베이스가 무거워지고 의도를 읽기 어려운 코드가 늘어난 상태에서, 팀의 다른 시스템은 이미 Kotlin이 주력이라 언어 불일치로 리뷰·커뮤니케이션 비용이 쌓이고 있었다고 한다. 점진 개선 대신 전환을 택한 근거로 세 가지를 든다 — Kotlin의 null 안정성·간결함이 레거시에 더 안전하다는 판단, 팀 언어 통일의 협업 효율, 축적된 전환 레퍼런스가 많아 리스크를 예측할 수 있었다는 점. 6명이 약 3개월간 진행했다.

## 핵심

- 순서가 핵심이라고 설명한다: 운영 로직에 영향 없는 **테스트 코드부터** Kotlin으로 전환하고, 커버리지가 부족한 구간은 테스트를 먼저 보완한 뒤 서비스 코드로 넘어갔다. 이때 Kotest(FreeSpec/ShouldSpec, given-when-then)와 MockK로 테스트 스타일도 통일
- 배포는 대규모 병합이 아니라 **기능/패키지 단위 점진 배포** — 82개 티켓, 10번의 운영 배포, 장애 0건
- null 처리 기준 3단계: 정말 nullable인가(아니면 non-null 선언) → nullable이면 모든 사용 지점의 null 처리 확인 → 비즈니스상 null 불가면 `requireNotNull`로 명시 방어. `!!`나 `?.`로 때우면 오히려 더 위험한 코드가 된다고 지적한다
- git 히스토리 유실 방지: IntelliJ의 "Extra commit for .java > .kt renames" 옵션으로 rename 커밋을 분리. 단, squash 머지하면 소용없다
- Lombok 공존 문제: 빌드 순서(kapt → Kotlin → java annotation processor → java) 때문에 Kotlin이 Lombok 생성 메서드를 못 본다 → Lombok 컴파일러 플러그인(Kotlin 1.7.20+)으로 전환 순서의 유연성 확보. 같은 모듈의 `@Builder`는 여전히 인식 불가
- QueryDSL DTO 매핑은 `Projections.constructor()` 채택 — `fields()`는 data class에 var·기본값을 강제해 불변성이 깨지고, `@QueryProjection`은 DTO에 불필요한 의존이 담긴다는 이유로 반려했다
- Jackson 역직렬화: `jackson-module-kotlin` + `kotlin-reflect` 의존성 추가. 커스텀 ObjectMapper를 쓰면 `KotlinModule`을 명시 등록해야 `InvalidDefinitionException`이 사라진다
- 예외와 트랜잭션: Kotlin은 모든 예외가 unchecked라서 Java 시절 checked exception이던 것도 Spring 트랜잭션이 롤백된다. 기존 동작을 유지하려면 `@Throws`를 붙여야 한다고 설명한다
- 결과: 45,000줄 수정, Code Smells 330→4(-98.8%), Cognitive Complexity 1940→1713(-11.7%), 테스트 커버리지 61.5%→76.7%

## 내 프로젝트와의 연결

WMS를 Kotlin으로 바꿀 일은 없지만 구조적으로 겹치는 지점이 셋 있다. 첫째, "리팩토링 전에 테스트 커버리지부터 확보하고, 작은 단위로 배포해 영향 범위를 줄인다"는 순서는 WMS 성능 개선(인덱스·N+1·캐싱) 작업에도 그대로 적용되는 안전장치다. 둘째, Spring 트랜잭션이 unchecked 예외만 기본 롤백한다는 규칙은 Java에서도 동일해서, WMS 재고 로직의 예외 설계(어떤 예외에서 롤백돼야 하나)와 직결된다. 셋째, QueryDSL DTO 매핑 방식 비교는 WMS 조회 최적화에서 곧 만날 선택지다.

## 오늘 정리할 것

1. Spring `@Transactional` 기본 롤백 규칙(RuntimeException/Error만 롤백, checked는 미롤백)을 공식 문서에서 확인하고, `rollbackFor`로 뒤집는 실험을 손으로 돌려보기
2. QueryDSL `Projections.fields` vs `constructor` vs `@QueryProjection` 세 방식의 차이를 WMS 조회 코드 기준으로 표로 비교해보기
3. WMS 리포에 JaCoCo를 붙여 현재 테스트 커버리지 수치를 재보기 (이 글의 61.5%→76.7%처럼 Before를 먼저 기록)
4. git이 rename을 감지하는 조건(유사도 기준)과 squash 머지가 히스토리를 잃게 하는 이유 확인
