---
출처: Claude 분석(데일리 인풋)
원본: https://techblog.woowahan.com/19491/
작성일: 2026-09-18
성격: 예습자료
tags: [학습, spring]
---

# 뉴스 - 2026-09-18 Spring Statemachine 도입기

> 상위: [[뉴스 인덱스]]
> 이전: [[뉴스 - 2026-09-17 Server-Sent Events로 실시간 알림 전달하기]]
> 다음: [[뉴스 - 2026-09-18 엔비디아가 GPU 커널을 Rust에 열었다]]
> 예습자료 — 자동 생성, 사용자 미검증. 정리본이 아니다.

## 오늘의 글

**Spring Statemachine 도입기**
이정수 · 2024-10-10 · Backend (#Spring Statemachine #State Machine)
https://techblog.woowahan.com/19491/

## 배경

글은 로보틱스LAB 로봇딜리버리플랫폼팀의 '로봇 배달 관리 서비스'를 소개하며 시작한다. 이 서비스는 배달 요청을 받아 가용 로봇을 찾고 임무를 할당한 뒤, 로봇이 배달을 끝낼 때까지 `유휴 → 픽업지로 이동 중 → 물품 적재 대기 → 물품 적재 중 → 전달지로 이동 중 → 전달 대기 → 전달 중 → 유휴` 흐름의 현재 상태를 중앙 서버에서 실시간으로 추적한다. 문제는 이 상태들을 조건문·flag·callback으로 관리하면 상태가 추가·삭제될 때마다, 전이 판단 기준이 바뀔 때마다 판단 코드와 부가 작업 코드가 여기저기 흩어져 유지보수가 어려워진다는 것이다. 글은 이 지점에서 state machine을 꺼내고, 직접 구현 → 프레임워크 채택 순으로 논지를 전개한다.

## 핵심

· state machine의 5개 요소를 먼저 정의한다 — **state**(변화 없이 유지되는 상태), **transition**(상태 간 이동), **event**(전이를 촉발하는 사건), **guard**(전이를 허용할지 판단하는 로직), **action**(전이·진입·이탈 시점에 수행되는 작업).
· 직접 구현하면 enum 상수에 `List<Transition> transitions`와 `Runnable action` 필드를 달아 자료구조를 만들고, 이벤트로 전이 후보를 찾고 → guard 실행 → 전이 → action 실행하는 프레임워크를 짜게 된다. 글은 여기에 이탈 action·초기 상태 지정·분산 서버 간 상태 동기화 요구가 붙으면 자료구조와 프레임워크가 계속 커진다고 본다.
· Squirrel Framework와 비교해 **Spring 친화적이고 업데이트가 더 활발하다**는 이유로 Spring Statemachine 3.2.1을 선택했다. 의존성은 `spring-statemachine-bom` 플랫폼 + `-starter` + `-data-redis` + (테스트) `-test`.
· 설정은 `EnumStateMachineConfigurerAdapter`를 상속해 configure 3개를 재정의한다 — 일반 설정(`autoStartup(true)`, `StateMachineListenerAdapter`로 stateChanged 로깅), 상태 등록(`.initial(IDLE)` + 각 state에 state action), 전이 등록(`.source().target().event().guard().action()`).
· `withExternal()`은 상태를 실제로 옮기고, `withInternal()`은 출발·도착이 같아 전이 없이 action만 실행한다. 팀은 적재함 문 열림/닫힘 기록에 `withInternal()`을 쓰고, guard `isLidClosed()`로 문이 닫혔을 때만 적재 완료 전이를 허용한다. timer 예약도 `withInternal()` 설정으로 건다.
· 데이터 전달은 두 갈래다 — 전이 1회만 유효한 **message header**(`MessageBuilder.withPayload(...).setHeader(k,v)`, guard·action에서 `context.getMessageHeader()`)와, state machine 수명만큼 사는 **extended state**(`getExtendedState().getVariables().put(...)`). 팀은 extended state에 로봇 ID·배달 ID·픽업지/전달지 좌표를 넣어두고 전이 action에서 꺼내 쓴다.
· 동시성은 4안을 비교해 **로봇별 전용 state machine**을 택했다. ①공용 1개 — 작업 큐가 필요하고, state action이 별도 스레드(로그상 transition은 `task-6`, action은 `parallel-4`)에서 비동기로 돌아 이전 로봇의 action이 다음 로봇의 context를 참조할 위험 + 대기 지연으로 반려. ②이벤트마다 생성·폐기 — 생성 비용이 커 CPU 낭비로 반려. ③로봇별 전용 — `robotStateMachines.computeIfAbsent(robotId, this::createStateMachine)`로 lazy 생성해 맵에 보관(단 로봇 수에 맞춘 scale 조정 필요, 팀은 운영 로봇 수를 미리 알기에 해결 가능). ④풀 — 하이브리드 대안으로만 언급.
· 다중 서버 동기화는 `StateMachinePersist` + Redis로 푼다. 전이 시작 전 `restore()`로 state context를 읽어 최신화하고, `doOnComplete`에서 `persist()`로 되돌려 쓴다. 1번 인스턴스가 '배차됨'을, 2번이 곧이어 '픽업지 도착'을 처리하는 상황을 근거로 든다. 내부 직렬화는 Kryo를 쓴다고 설명한다.
· 테스트는 2층이다 — `StateMachineTestPlanBuilder`로 초기 상태·전이·`expectVariable`을 검증하되 **action 동작은 확인할 수 없다는 한계**가 있고, 그래서 `@SpringBootTest` + `@EmbeddedKafka` + Embedded Redis로 통합 테스트를 붙였다. 케이스는 tc01~tc11로 순서 의존이며(앞 케이스가 저장한 state context에 의존), 비동기 side effect는 `Awaitility.await().atMost(...).pollInterval(...).until(...)`과 `verify(..., timeout(...).atLeastOnce())`로 기다려 확인한다.
· 단점으로는 학습 시간을 든다. 상태 관리 로직이 간단하면 직접 구현이, 기능이 다양하게 필요하면 프레임워크가 낫다는 판단 기준을 남긴다.

## 내 프로젝트와의 연결

WMS의 입고·출고 전표가 정확히 이 모양이다 — 출고가 `대기 → 할당 → 피킹 → 패킹 → 출고완료`로 흐르고, 중간에 취소·반품이 끼어든다. 지금 이걸 `status` 컬럼 + 서비스 메서드 안의 if로 관리한다면, 글이 말하는 "조건문·flag가 얽히는" 상태에 이미 가까울 수 있다. 다만 Spring Statemachine을 바로 도입할 이유로 읽히지는 않는다 — 글 자체가 "상태 관리가 간단하면 직접 구현이 낫다"고 못박고, 3주 프로젝트에 프레임워크 학습 비용을 얹는 건 비싸 보인다. 옮겨올 만한 것은 오히려 **전이표를 코드에 명시적으로 두는 방식**(어떤 상태에서 어떤 이벤트로 어디로 갈 수 있는지를 enum/맵으로 선언하고, 서비스는 그 표에 물어보게 하기)과 **guard/action 분리**(전이 가능 여부 판단과 부수효과를 섞지 않기)다. 구조적으로 비슷한 지점이 하나 더 있는데, 재고 선점·락 이야기와 겹치는 대목 — 여러 서버 인스턴스가 같은 전표의 상태를 동시에 바꿀 수 있다는 문제는 이 글이 Redis persist로, WMS에서는 낙관/비관 락으로 푸는 같은 문제의 다른 답이다. 수집기 쪽은 직접 연결이 약하지만, 수집 잡의 `대기 → 수집중 → 성공/실패 → 재시도` 흐름도 상태 전이라 전이표로 적어볼 여지는 있다.

## 오늘 정리할 것

1. WMS 출고 전표의 상태 전이를 종이에 상태도로 그려보기 — 상태 몇 개, 이벤트 몇 개, 불가능한 전이는 어디인지. 지금 코드에서 그 "불가능한 전이"를 실제로 막고 있는지 확인한다.
2. 내 서비스 코드에서 상태를 바꾸는 지점을 전부 grep해서 세어보기(`setStatus`, `status =` 등). 여러 곳에 흩어져 있다면 글이 말한 문제가 이미 있는 것이다.
3. `withExternal` vs `withInternal`에 대응하는 내 사례 찾기 — 상태는 그대로인데 부수효과만 남겨야 하는 이벤트(수량 정정, 메모 추가 등)가 있는지.
4. `Awaitility`가 무엇인지, `Thread.sleep`으로 버티는 비동기 테스트를 어떻게 대체하는지 찾아보기 (`awaitility` 의존성 하나 추가해 `until` 한 줄 써보기).
