---
출처: Claude 대화
작성일: 2026-11-15
tags: [프로젝트, java]
---

# AiOps - Starter 생명주기

> 허브: [[AiOps 프로젝트 MOC]]

팀 앱이 **태어나서 죽을 때까지의 각 시점에 Starter가 무엇을 하는지** 한 장으로 보는 지도. 작업이 머지되면 상태 칸을 고친다. 기준: 2026-11-15.

## 1. 한눈에

```
앱 시작 ─────────────── 준비 완료 ──────────── 종료
  │                        │                     │
  ├ 설정 읽기, 부품 조립    ├ 어펜더 다시 확인     └ 남은 이벤트 전송 (AI-46)
  ├ 전송 스레드 시작        └ 환경 정보 1회 전송
  ├ 어펜더 붙이기              (AI-47)
  │
  └ 뜨다가 실패하면 → 그 예외를 바로 전송 (AI-45)
```

## 2. 시점별 표

| 시점 | 신호 | 하는 일 | 코드 | 작업 | 상태 |
|---|---|---|---|---|---|
| 환경 준비됨 | `ApplicationEnvironmentPreparedEvent` | 설정 읽기 → 커밋 해시 읽기(.git) → 버퍼·전송·전송 스레드 조립 → 종료 훅 등록 → 어펜더 장착 | `AiopsRuntime.startIfAbsent`, `attachAppenderIfMissing` | AI-39·43 | ✅ |
| 컨텍스트 준비 | `ApplicationPreparedEvent` | 어펜더가 떨어졌으면 다시 장착 | `attachAppenderIfMissing` | AI-43 | ✅ |
| 앱 준비 완료 | `ApplicationReadyEvent` | 어펜더 다시 확인 | `attachAppenderIfMissing` | AI-43 | ✅ |
| 앱 준비 완료 | `ApplicationReadyEvent` | Java·Boot 버전, 의존성 등 환경 정보 1회 전송 (hello) | `AiopsRuntime.submitHelloOnce` → `DefaultEnvCollector` | AI-47 | 🔄 PR #56 |
| 돌아가는 중 | 로그 (ERROR + 예외) | 어펜더 → 변환 → 마스킹 → 버퍼 → 5초 또는 100개마다 전송, 60초마다 하트비트 | `AiopsLogbackAppender`, `BatchingEventSender` | AI-36~42 | ✅ |
| 시작 실패 | `ApplicationFailedEvent` | 그 예외를 STARTUP 이벤트로 **즉시** 전송, 최대 3초 | `AiopsRuntime.reportStartupFailure` | AI-45 | ✅ PR #54 |
| JVM 종료 | JVM 종료 훅 (`aiops-shutdown`) | 버퍼에 남은 것 전송 최대 2초 → 전송 스레드 정지 | `AiopsRuntime.onJvmShutdown` | AI-46 | ✅ PR #55 |
| Starter 내부 오류 | 어디서든 `Throwable` | Starter만 끈다 (어펜더 떼기, 스레드 정지, 한 줄 출력). 팀 앱은 그대로 | `AiopsRuntime.disable` | AI-43 (D-087) | ✅ |

진입점은 하나다: `AiopsEarlyInitializer` (spring.factories 등록, 로깅 초기화 바로 다음 순서). Bean보다 먼저 돌아서 Bean 생성 실패도 잡는다.

## 3. 왜 시작 실패와 종료만 따로 다루나

평소 길은 `로그 → 어펜더 → 버퍼 → 5초마다 전송`이다. **앱이 죽는 순간에는 이 길이 통하지 않는다.**

| 순간 | 평소 길이 안 되는 이유 | 대신 하는 일 |
|---|---|---|
| 시작 실패 | 5초를 기다리기 전에 JVM이 끝난다 | Spring이 넘겨준 예외를 직접 받아 지금 보낸다 |
| 종료 | 종료 직전의 에러가 버퍼에 담긴 채 사라진다 | 종료 훅에서 버퍼를 비운다 |

두 곳 모두 `flushNow(기다릴 시간)`를 쓴다. "전송 스레드에 지금 보내라고 하고, 부른 쪽은 정해진 시간만 기다린다."

## 4. 시간 상한 (늘리지 않는다)

| 무엇 | 상한 | 이유 |
|---|---|---|
| 시작 실패 전송 | 3초 | 앱 종료를 우리 때문에 늦추지 않는다 |
| 종료 훅 | 2초 | 컨테이너 stop의 유예 시간(보통 10초) 안에 다른 정리도 끝나야 한다 |
| HTTP 요청 1번 | 연결 2초, 응답 3초 | 서버가 죽어 있어도 전송 스레드가 오래 묶이지 않게 |
| 전송 스레드 정지 | 1초 | — |

## 5. 못 잡는 것 (알고 포기)

- `kill -9`, 전원 차단: 종료 훅이 돌지 않는다.
- 환경 준비 **이전**의 실패(JVM 옵션 오류, 메인 클래스 없음): Starter가 아직 시작 전이다.
- Windows에서 `gradlew bootRun`을 Ctrl+C로 끄면 Gradle이 JVM을 강제로 죽여 훅이 안 돌 수 있다 (⚠ 미확인. AI-46 수동 확인 때 본다).
- 시작 실패 뒤 Spring이 찍는 실패 로그는 어펜더가 `RUNTIME`으로 한 번 더 잡을 수 있다 (같은 그룹, 횟수만 +1).
