---
출처: Claude 대화
작성일: 2026-11-16
tags: [프로젝트, java]
---

# AiOps - 안전성 테스트 7종 (Boot 4)

> 허브: [[AiOps 프로젝트 MOC]]

**PR #57 `[AI-49] 안전성 테스트 1부`** — 커밋 12개, 11/15 머지. "팀 앱을 절대 느리게 하거나 죽이지 않는다"를 일곱 가지 상황으로 고정한다. Boot 3.5 실행과 CI job은 2부(MVP 뒤, D-106).

## 1. 배운 내용

### 1-1. 일곱 가지

| 번호 | 클래스 | 만드는 상황 | 확인하는 것 |
|---|---|---|---|
| 1 | `ServerDownSafetyTest` | 수집 서버가 꺼져 있다 | 팀 앱은 정상으로 뜨고 요청에 응답한다 |
| 2 | `NoKeySafetyTest` | 키가 없다 | Starter만 꺼지고 앱은 뜬다 |
| 3 | `StartupFailureSafetyTest` | 앱이 시작하다 실패한다 | 원래 예외가 그대로 나온다 (Starter가 가리지 않는다) |
| 4 | `FloodSafetyTest` | 에러 1,500개가 연속으로 난다 | 버퍼(1,000)가 넘쳐도 앱 스레드가 멈추지 않는다 |
| 5 | `MaskingSafetyTest` | 메시지에 민감한 값이 있다 | 나가는 글자에 그 값이 없다 |
| 6 | `InternalErrorSafetyTest` | Starter 안에서 오류가 난다 | Starter만 꺼지고 앱은 뜬다 |
| 7 | `IgnoredLoggerSafetyTest` | 전송 쪽 로거가 ERROR를 찍는다 | 그 로그를 다시 수집하지 않는다 (무한 반복 방지) |

공통 도구: `Safety`(앱 띄우기·기다리기), `FakeIngestServer`(JDK `HttpServer`로 만든 가짜 수집 서버), `com.example.safetyapp.SafetyApp`(가장 작은 팀 앱).

### 1-2. 클래스마다 새 JVM인 이유

```groovy
tasks.register('safetyTest', Test) {
    filter { includeTestsMatching 'dev.aiops.starter.safety.*' }
    forkEvery = 1
}
```

`AiopsRuntime`의 상태(`instance`, `DISABLED`)는 `static`이라 JVM 하나에 하나뿐이다. 2번 테스트가 Starter를 꺼 두면 같은 JVM에서 도는 다음 테스트는 "이미 꺼진 Starter"로 시작한다. `forkEvery = 1`은 테스트 클래스 하나가 끝날 때마다 JVM을 새로 띄운다. 느려지지만(클래스 7개 = JVM 7번) 서로 영향을 주지 않는다. 그래서 일반 `test`와 작업을 나눴고 `check`에 묶었다.

### 1-3. 6번을 위한 실패 주입 스위치

Starter 안에서 진짜로 오류를 내야 "Starter만 꺼진다"를 볼 수 있다. `AiopsRuntime.failOnInitIfRequested()`가 시스템 속성 `aiops.test.fail-on-init=nosuchmethod`를 보면 일부러 `NoSuchMethodError`를 던진다.

- 운영 코드(`src/main`)에 들어가는 유일한 테스트용 코드다. Starter jar에도 실린다.
- 그래서 `aiops.*` 설정(yml·환경변수)이 아니라 **시스템 속성**으로만 켜진다. 팀이 설정 파일에서 실수로 켤 수 없다 (D-105).
- `Exception`이 아니라 `Error` 계열을 던지는 이유: 진입점이 `catch (Throwable)`인지(규칙 4)를 확인하려는 것이다. `catch (Exception)`이면 이 테스트가 빨강이 된다.

### 1-4. `@SpringBootTest`를 쓰지 않은 이유

테스트는 `SpringApplication.run(SafetyApp.class, ...)`으로 앱을 직접 띄우고 JDK `HttpClient`로 요청한다. 2부에서 같은 테스트를 Boot 3.5로 돌릴 때 테스트 도구(Boot 버전에 따라 이름이 바뀌는 것들)에 걸리지 않게 하려는 것이다.

## 2. 설계와 다른 점

| 명세 | 실제 | 이유 |
|---|---|---|
| 한 번에 Boot 4 + Boot 3.5 + CI | 1부(Boot 4)만 | D-106. Boot 3.5에서 실패하면 7종까지 같이 멈춘다 |
| 클래스 1개에 7개 메서드 | 클래스 7개 | D-104. static 상태 때문에 JVM을 나눠야 한다 |

## 3. 남은 것

- 2부: `-PtestBoot=3`, CI `starter-boot3` job, 브랜치 보호 규칙의 필수 체크. **Boot 3을 쓰는 팀을 받기 전에 필수** (D-102 조건 ①)
- Logback이 없는 앱(Log4j2)에서의 동작은 여기서 확인하지 않았다

## 관련 노트

[[AiOps 39 - 환경 정보 hello와 EnvCollector]] · [[AiOps 41 - LLM 기본 모델과 실패 로그]] · [[AiOps - Starter 생명주기]]
