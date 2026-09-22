---
출처: Claude 분석(데일리 인풋)
원본: https://techblog.woowahan.com/15398/
작성일: 2026-09-20
성격: 예습자료
tags: [학습, java]
---

# Java의 미래, Virtual Thread

> 상위: [[뉴스 인덱스]]
> 이전: [[뉴스 - 2026-09-19 에이전트 지침이 AGENTS.md로 수렴했다]]
> 다음: [[뉴스 - 2026-09-20 에이전트가 시스템을 뚫기 시작했다]]

원문: [Java의 미래, Virtual Thread](https://techblog.woowahan.com/15398/) — 김태헌 · 2023.12.12 · Backend

## 배경

글은 팀의 모든 프로젝트가 Java였다고 설명한다. 2021년 사용자 인증 게이트웨이(I/O가 많고 병목이 장애로 전파되는 지점)를 만들며 경량 스레드가 필요해졌는데, 당시 Virtual Thread는 정식 feature가 아니어서 Kotlin coroutine이 유일한 선택지였고 실제로 게이트웨이를 Kotlin으로 개발했다고 한다. 이후 JDK21(2023.09)에 Virtual Thread가 정식 포함되자 "Kotlin 러닝커브 없이 Java 그대로 경량 스레드를 쓸 수 있는가"를 팀 스터디로 검증한 기록이다.

## 핵심

- 기존 Java 스레드는 커널 스레드와 1:1 매핑(Native Thread) — 스택 ~2MB, 생성 ~1ms, 컨텍스트 스위칭 ~100µs. 4GB 메모리면 스레드 4,000개가 한계라고 설명한다
- Virtual Thread는 플랫폼 스레드 위에서 JVM이 스케줄링 — 스택 ~10KB(일반 스레드의 1%), 생성 ~1µs, 스위칭 ~10µs. 시스템 콜 없이 생성된다
- 구조: `carrierThread`(실제 실행하는 플랫폼 스레드) + `scheduler`(ForkJoinPool, work stealing) + `runContinuation`(작업 본체). I/O·sleep을 만나면 park되어 힙으로 돌아가고, 커널 스위칭 없이 다른 가상 스레드가 실행된다
- 구현 방식이 핵심이라고 짚는다: `LockSupport.park/unpark`, `NIOSocketImpl.park`, `Thread.sleep`에 "현재 스레드가 Virtual인가" 분기만 추가해 기존 코드 수정 없이 완전 호환
- Ngrinder 테스트(힙 256MB, 300ms sleep API 3회 호출): I/O bound에서 Thread 대비 +51%, vuser 250 이상에서 Thread 모델은 서버가 죽었지만 Virtual Thread는 정상 처리. coroutine 대비 +37%, WebFlux(Reactive) 대비 +111%라고 보고한다
- 반대로 CPU bound(3억 합산 3회)는 일반 스레드가 우위 — 스위칭이 없으면 가상 스레드 생성·스케줄링 비용만 낭비된다. "It is more expensive to run a task in a virtual thread than running it in a platform thread"
- coroutine·Reactive의 공통 단점으로 '함수의 색 문제'(suspend/Mono 전염)와 프로덕션 코드 변경을 꼽는다. Virtual Thread는 전염이 없고 스택 트레이스가 온전하다고 설명한다
- 주의사항 4가지: ①풀링 금지(생성비용이 작아 풀 자체가 낭비 — 만들고 GC에 맡김) ②CPU bound 비효율 ③Pinned 이슈 — `synchronized`·`parallelStream`·네이티브 메서드에서 park 불가 상태가 됨, 긴 synchronized는 `ReentrantLock` 교체 검토 ④ThreadLocal은 작게(수시로 생성·소멸되므로)

## 내 프로젝트와의 연결

WMS의 동시성 축과 직결된다. 재고 선점 락에 `synchronized`를 쓰면 나중에 Virtual Thread를 켜는 순간 Pinned로 성능이 무너질 수 있다 — 글이 권하는 `ReentrantLock`이 안전한 기본값이 되는 이유다. 부하 테스트 주차에 "vuser를 올리다 서버가 죽는 지점"을 찾는 이 글의 실험 설계(고정 힙 + I/O bound API + 단계적 vuser 증가)도 그대로 재현해볼 만하다. Spring Boot 3.2+면 `spring.threads.virtual.enabled=true` 한 줄로 켜고 Before/After를 잴 수 있다.

## 오늘 정리할 것

1. WMS 코드에서 `synchronized` 사용처를 찾아 `ReentrantLock`으로 바꿀 수 있는지 목록화하기 (Pinned 예방)
2. `spring.threads.virtual.enabled=true`를 로컬 WMS에 켜고, 같은 조회 API의 Before/After 처리량 비교해보기
3. 스레드 덤프에서 carrierThread / ForkJoinPool이 실제로 보이는지 `jcmd Thread.dump_to_file`로 확인해보기
4. "CPU bound에서는 오히려 손해"를 손으로 재현 — 합산 루프 API를 만들어 일반/가상 스레드 응답시간 비교

## 남는 질문

- Pinned 상태는 JDK21 이후 버전에서 얼마나 완화되었나 (JDK24의 synchronized pinning 해소 작업은 어디까지 왔는지)
- 커넥션 풀(HikariCP)처럼 유한한 리소스 앞에서 백만 가상 스레드가 몰리면 무슨 일이 생기나 — 세마포어로 조절해야 하는지
