---
출처: Claude 대화
작성일: 2026-11-10
tags: [프로젝트, java]
---

# AiOps - 부품 조립 AiopsRuntime

> 허브: [[AiOps 프로젝트 MOC]]

**PR #33 `[AI-39] 부품 조립 (AiopsRuntime + 진입점 등록)`** — 브랜치 `feat/starter-AI-39-runtime`. 커밋 6개(파일 하나에 하나) + develop 머지 1개. 3단계(보내기)의 마지막 작업.

## 1. 배운 내용

### 1-1. 이 PR이 하는 일: 부품을 이어 붙이고 스스로 켜지게

```
팀 앱 시작
 └ Spring Boot: ApplicationEnvironmentPreparedEvent
     ① LoggingApplicationListener (로깅 초기화, 순서 +20)
     ② AiopsEarlyInitializer       (우리, 순서 +21)  ← spring.factories로 등록
          └ AiopsRuntime.startIfAbsent(env)
               AiopsSettings → BoundedEventBuffer → HttpTransport
               → AppInfo(앱 이름, null, null, HostHash) → BatchingEventSender.start()
```

여기까지 오면 Starter가 **팀 앱 코드를 한 줄도 건드리지 않고** 스스로 켜진다. 아직 에러를 잡는 부분(4단계 어펜더)이 없어서 보내는 것은 60초마다 하트비트뿐이다.

### 1-2. 코드로 보기: AiopsRuntime

```java
private static volatile AiopsRuntime instance;              // ①

public static AiopsRuntime startIfAbsent(Environment environment) {
    AiopsRuntime current = instance;
    if (current != null) return current;                    // ② 빠른 길: 잠금 없이
    synchronized (LOCK) {
        if (instance != null) return instance;              // ③ 다시 확인
        try {
            AiopsSettings settings = AiopsSettings.fromOrNull(environment);
            if (settings == null) return null;              // ④
            ... 부품 생성 ...
            sender.start();
            instance = new AiopsRuntime(settings, buffer, sender);
            return instance;
        } catch (Throwable t) {                             // ⑤
            System.err.println("[aiops] 비활성화됨: ...");
            return null;
        }
    }
}
```

| 번호 | 이유 |
|---|---|
| ① | 어펜더(4단계)는 **팀 앱 요청 스레드**에서 `current()`를 읽는다. `volatile`이 없으면 다른 스레드가 만든 객체를 늦게 볼 수 있다 |
| ②③ | **이중 확인 잠금**. 이미 만들어졌으면 잠금 없이 바로 돌려준다. 없을 때만 잠그고, 잠근 뒤 한 번 더 본다(기다리는 사이 다른 스레드가 만들었을 수 있음) |
| ④ | 키가 없으면 아무 부품도 만들지 않는다. 경고는 AiopsSettings가 이미 한 줄 찍었다 |
| ⑤ | `Exception`이 아니라 `Throwable`. `NoClassDefFoundError` 같은 Error도 잡아야 팀 앱 시작이 안 죽는다 (D-087) |

`resetForTest()`는 패키지 공개. 테스트끼리 static 상태가 섞이지 않게 `@AfterEach`에서 스레드를 멈추고 비운다.

### 1-3. 코드로 보기: AiopsEarlyInitializer

```java
public final class AiopsEarlyInitializer
        implements ApplicationListener<ApplicationEnvironmentPreparedEvent>, Ordered {
    static final int ORDER = LoggingApplicationListener.DEFAULT_ORDER + 1;
    ...
}
```

- `spring.factories`의 `org.springframework.context.ApplicationListener=...` 한 줄로 Spring Boot가 이 클래스를 찾는다. Bean이 아니라서 **Bean 생성 전**에 돈다 → Bean 생성 실패(DB 연결 실패 등)도 나중에 잡을 수 있다.
- 순서가 로깅 초기화보다 빠르면, 로깅 초기화가 우리가 붙인 어펜더를 떼어 버린다. 그래서 `+1`.

### 1-4. 코드로 보기: HostHash

| 줄 | 이유 |
|---|---|
| `COMPUTERNAME` → `HOSTNAME` → `InetAddress` 순서 | `InetAddress.getLocalHost()`는 DNS 때문에 몇 초 걸리는 PC가 있다. 시작 스레드를 멈추지 않으려고 환경변수를 먼저 본다 |
| `toLowerCase` | 윈도우 환경변수는 대문자, InetAddress는 소문자일 수 있다. 같은 PC가 다른 해시가 되지 않게 |
| 6바이트 = 16진수 12자 | protocol `AppInfo.hostHash` 약속 |
| 실패해도 `"unknown-host"`의 해시 | **서버 `heartbeat_last.host_hash`가 NOT NULL**. null을 보내면 서버 저장이 실패한다 |

### 1-5. 테스트 3 + 6개

- **HostHashTest**: 12자 16진수, 원문 없음, 같은 입력 같은 해시, 실제 호스트에서도 null 아님
- **AiopsRuntimeTest**: 키 없음 → null·스레드 없음 / enabled=false → null / 키 있음 → 부품 연결·스레드 +1 / 두 번 불러도 같은 객체·스레드 그대로 / 순서 > 로깅 / spring.factories에 등록됨
- 스레드 개수는 "전 → 후" 차이로 센다. 다른 테스트가 남긴 `aiops-sender`가 있어도 흔들리지 않게.

### 1-6. 실제 도착 확인

서버(local 프로필) + sample-app(`AIOPS_KEY=aiops_l_local-dev-key-0001`) → 1분 뒤:

```
 env  |  host_hash   |  app_name  | last_seen_at
 local | b61b7ce3b5ab | sample-app | 2026-11-10 05:59:17+00
```

**사고**: 처음에 VS Code SQL 확장이 WMS 프로젝트 MySQL(3307)에 붙어 있어서 "Can't connect"가 났다. AiOps는 PostgreSQL 5432다. 확인은 `docker exec -it aiops-postgres psql -U postgres -d aiops -c "..."`로 한다. `postgres`는 슈퍼유저라 RLS에 막히지 않는다(`aiops_app`으로 보면 0건).

## 2. 설계와 다르게 한 곳

| 명세 (AI-39) | 실제 | 이유 |
|---|---|---|
| 패키지 `lifecycle/` | `runtime/` | 정정 메시지를 보기 전에 커밋. 진입점·조립·5단계 시작 실패·종료가 모두 AiopsRuntime에 모이니 이름도 맞다. Jira 에픽 AI-4 수정 |
| `initOrGet`, 꺼지면 "비활성 객체" | `startIfAbsent`, 꺼지면 null | 어펜더가 `current() == null`로 바로 판단 |
| 로거 `dev.aiops.starter`로 비활성 로그 | `System.err` | 로깅 초기화 중이라 로거가 불안정. AI-35와 같은 방식 |
| 임시 ErrorEvent로 error_event 행 확인 | 하트비트로 서버 도달 확인 | 에러 전송은 마일스톤 1(AI-44)에서 |
| 생성 중 NoClassDefFoundError 테스트 | 미포함 | 부품 생성을 바꿔 끼울 지점이 없음. AI-49 안전성 테스트에서 |

## 3. 더 나아가 알면 좋은 것

### 3-1. PR에 적은 D-번호는 무엇인가

설계 문서 5절 "결정 기록"의 번호다. 리뷰어가 근거를 바로 찾게 PR에 적는다.

| 번호 | 결정 | 이 PR에서 |
|---|---|---|
| D-005 | 진입점은 Bean이 아니라 spring.factories 리스너, 로깅 초기화 직후 | `AiopsEarlyInitializer`, `ORDER +1` |
| D-006 | 부품은 JVM당 1회, 어펜더 장착은 매번 확인 | static volatile + 이중 확인. DevTools 재시작에도 스레드가 늘지 않음 |
| D-084 | Boot 3.x·4.x 공통 API만 | `ApplicationListener`, `ApplicationEnvironmentPreparedEvent`, spring.factories |
| D-087 | Throwable까지 잡고 `[aiops] 비활성화됨` 한 줄 | 두 클래스의 catch |

### 3-2. 로컬 git 상태 점검에서 본 것

- develop을 머지하면 B의 server 파일 46개가 "수정됨"으로 보였다. `git diff --ignore-cr-at-eol` 결과 실제 변경 0줄 → **CRLF만 다름**. 커밋하지 말고 `git restore .`. 근본 해결은 `.gitattributes`에 `* text=auto eol=lf` (MVP 후 docs PR).
- `.git/objects/maintenance.lock`이 남아 있었다. 확인용 fetch가 남긴 것일 수 있다. 자동 정리를 막으니 지운다.
- 테스트는 머지 **전**에 돌렸지만 머지로 들어온 건 server뿐이라 starter 결과는 유효. 전체는 CI가 돌린다.

### 3-3. 다음에 볼 키워드

- 이중 확인 잠금(double-checked locking)과 `volatile`이 꼭 필요한 이유
- Spring Boot 시작 이벤트 순서: `ApplicationStarting` → `EnvironmentPrepared` → `ContextPrepared` → `Started` → `Ready` / `Failed`
- `spring.factories` vs `AutoConfiguration.imports`

## 관련 노트

[[AiOps 21 - 전송 스레드 BatchingEventSender]] · [[AiOps 23 - 마스킹 Masker]]
