---
출처: Claude 분석(데일리 인풋)
원본: https://techblog.woowahan.com/21686/
작성일: 2026-09-16
성격: 예습자료
tags: [학습, spring]
---

# 뉴스 - 2026-09-16 IllegalArgumentException은 400 Bad Request인가

> 상위: [[뉴스 인덱스]]
> 이전: [[뉴스 - 2026-09-15 한꺼번에 짊어지던 배치를 내려놓고, 하나씩 흘려보내는 워크플로로]]
> 예습자료 — 자동 생성, 사용자 미검증. 정리본이 아니다.

## 오늘의 글

**IllegalArgumentException은 400 Bad Request인가?**
허용선 · 2025-05-13 · Backend (#Java #Spring)
https://techblog.woowahan.com/21686/

## 배경

글은 API를 만들다 보면 예외마다 어떤 HTTP 상태 코드를 돌려줄지 고민하게 되고, 스프링에서는 `@RestControllerAdvice` + `@ExceptionHandler` + `@ResponseStatus`로 예외 클래스와 응답을 손쉽게 매핑할 수 있다는 데서 출발한다. 그중 실무에서 아주 흔한 관행 — 비즈니스 로직에서 "요청이 잘못됐다"고 판단되면 `IllegalArgumentException`을 던지고, 전역 핸들러에서 그 예외를 `400 Bad Request`로 묶는 것 — 을 문제 삼는다. 글이 던지는 질문은 하나다: 이 예외는 정말 항상 클라이언트 잘못으로만 발생하는가? 글은 아니라고 답하며, 개발자 실수나 내부 로직 결함으로도 같은 예외가 나오기 때문에 범용 예외를 400으로 매핑하는 것이 왜 위험한지, 대안은 무엇인지를 다룬다.

## 핵심

- **4xx와 5xx는 "책임이 누구에게 있나"의 구분.** 4xx는 클라이언트가 잘못된 요청을 보낸 것이라 요청을 고치지 않으면 계속 실패하므로 자동 재시도(backoff)가 무의미하고, 5xx는 서버 내부 문제(로직 오류·DB 연결 실패·API 연동 실패)라 일시적일 수 있어 클라이언트가 간격을 두고 재시도할 수 있다고 설명한다.
- **운영·모니터링 관점이 진짜 이유.** 5xx는 즉각 대응해야 할 서버 신호로 경보가 걸려야 하고, 서버 오류를 4xx로 잘못 내면 운영팀이 클라이언트 문제로 오인해 대응이 늦어진다. 반대로 클라이언트 오류를 5xx로 내면 불필요한 경보가 늘어 무감각해지고 진짜 장애를 놓친다 — 양쪽 오탐 모두 비용이다.
- **스프링이 기본으로 IAE를 400에 매핑하지 않은 이유.** `IllegalArgumentException`은 Java 표준 라이브러리·스프링·하이버네이트 어디서든 발생하는데, 그것이 클라이언트 입력 때문인지 서버 내부 로직 때문인지 예외 자체로는 알 수 없기 때문이라고 글은 설명한다. 참고 이슈: spring-boot #34696 "IllegalArgumentException mapped to Status Code 500 instead of 400".
- **서버 버그가 400으로 위장되는 예시.** `Thread.setPriority(..)`는 1~10만 허용해 범위를 벗어나면 IAE를 던진다. 개발자가 이를 모른 채 `PriorityResolver`를 고쳤다면 클라이언트와 무관한 IAE가 발생하고, 이것이 400으로 매핑돼 있으면 "클라이언트 잘못"으로 기록돼 문제 파악이 늦어진다. 커스텀 예외만 400으로 매핑했다면 이 경우 500이 나와 서버 문제로 즉시 인식됐을 것이라는 논리다.
- **매핑 원칙 ①: 예상 못 한 상황은 5xx, 명백한 클라이언트 잘못만 4xx.** 스프링은 매핑되지 않은 예외를 500으로 응답하는데, 글은 이 기본값을 그대로 두고 조치 과정에서 클라이언트 잘못으로 판명된 것만 4xx로 옮기라고 한다.
- **매핑 원칙 ②: 비즈니스 예외 vs 시스템 예외.** "최소 주문 금액 미달" 같은 비즈니스 예외는 400, DB 연결 실패·API 연동 실패·`NullPointerException`·라이브러리 내부 오류 같은 시스템 예외는 5xx. 예측 가능한 시스템 예외는 대체 응답(Fallback)으로 5xx를 회피하되 모니터링은 남기라고 덧붙인다.
- **매핑 원칙 ③: 커스텀 예외로 클라이언트 잘못을 명시.** `IllegalArgumentException`·`IllegalStateException` 대신 `BusinessException`, `FieldNameDuplicatedException` 같은 커스텀 예외를 정의하고 그것만 400에 매핑한다.
- **예시 코드의 설계 포인트.** `BusinessException extends RuntimeException`에 `code`(클라이언트 개발자가 예외 상황을 식별하는 값, 예: `"expression.Invalid"`)와 `arguments`(`Map<String,Object>`, 이해를 돕는 부가 정보 — `position`, `hint` 등)를 두고, 구체 예외(`InvalidExpressionException`)는 이를 상속해 생성자에서 `addArgument`로 채운다. 핸들러는 `@ExceptionHandler(BusinessException.class)` 하나로 하위 예외까지 400으로 받는다.

## 내 프로젝트와의 연결

WMS 쪽에 가장 직접적이다. 입고·재고·출고 API에서 "재고 부족", "이미 출고된 주문", "존재하지 않는 로케이션" 같은 판정은 전부 이 글이 말하는 비즈니스 예외이고, 지금 이런 것을 `IllegalArgumentException`/`IllegalStateException`으로 던지고 있다면 글의 논리대로 서버 버그와 구분이 안 되는 상태다. 특히 재고 선점·분산 락(09-14 글)이나 동시성 처리 중에 나오는 예외는 클라이언트 잘못이 아닌데도 같은 IAE로 흘러가 400으로 위장될 수 있다는 점이 위험한 지점이다. `code` + `arguments`를 가진 `BusinessException` 계층을 두면 React 프론트가 상태 코드가 아니라 `code`로 분기할 수 있고, 5xx만 경보 대상이 되어 부하 테스트나 배포 후 모니터링에서 "진짜 서버 문제"만 걸러 볼 수 있다. 결정 로그(문제→대안→선택 근거)로 남기기 좋은 주제다. 수집기 쪽은 반대 방향 — 사람인 API를 **호출하는 클라이언트** 입장에서 응답이 4xx면 재시도해도 소용없고 5xx면 backoff 재시도가 유효하다는 글의 첫 절이 재시도 정책의 분기 기준이 된다. 구조적으로는 "예외의 종류가 아니라 책임 소재로 분류한다"는 원칙이 양쪽에 공통이다.

## 오늘 정리할 것

1. WMS 코드에서 `throw new IllegalArgumentException` / `IllegalStateException` 이 나오는 자리를 전부 찾아, 각각이 "클라이언트 잘못"인지 "서버 내부 판정 실패"인지 한 줄씩 분류해 본다 — 두 부류가 같은 예외 타입에 섞여 있는지 확인하는 것이 목적.
2. 글의 `BusinessException(code, arguments)` 구조를 WMS 도메인에 맞게 예외 3개(예: 재고 부족·중복 입고·잘못된 상태 전이)만 스케치하고, `code` 명명 규칙(`inventory.Insufficient` 같은 점 표기?)을 하나로 정한다.
3. 현재 `@RestControllerAdvice`가 어떤 예외를 어떤 상태 코드로 매핑하고 있는지 표로 적고, 매핑되지 않은 예외가 500으로 떨어지는 기본 동작을 실제로 한 번 호출해 확인한다.
4. 수집기의 API 호출 재시도 코드에서 4xx와 5xx를 구분해 처리하는지 확인한다 — 4xx에도 backoff 재시도를 하고 있다면 그것이 낭비인 이유를 글의 첫 절로 설명해 본다.
