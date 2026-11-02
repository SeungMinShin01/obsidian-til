---
출처: Claude 대화
작성일: 2026-11-02
tags: [프로젝트, java]
---

# AiOps - sample-app 에러 재현 앱

> 허브: [[AiOps 프로젝트 MOC]]

**PR #5 `[AI-48] 샘플 앱 보강 (에러 API, 시작 실패 프로필)`** — 머지 커밋 `3bad74b`.

sample-app은 **다른 조의 Spring Boot 앱 역할**을 하는 테스트용 앱이다. Starter를 의존성으로만 달고, 일부러 정해진 종류의 에러를 낸다. 이후 단계(마일스톤 1, 그룹화, 알림, 통합 시나리오)를 누구나 같은 방법으로 재현하려고 만든다.

## 1. 배운 내용

### 1-1. BoomController — 주소마다 다른 고장

```java
package dev.aiops.sample;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

import java.io.IOException;
import java.util.Map;

/*
 * Starter를 시험하려고 일부러 고장 내는 엔드포인트 모음.
 * /boom/caught를 빼면 예외를 잡지 않는다. Spring이 ERROR 로그를 남기게 둔다.
 */
@RestController
public class BoomController {

    private static final Logger log = LoggerFactory.getLogger(BoomController.class);

    private final JdbcTemplate jdbc;

    public BoomController(JdbcTemplate jdbc) {
        this.jdbc = jdbc;
    }

    /* 정상 응답. Starter가 응답을 느리게 하지 않는지 비교용 */
    @GetMapping("/ok")
    public Map<String, String> ok() {
        return Map.of("status", "ok");
    }

    /* 런타임 에러 */
    @GetMapping("/boom/npe")
    public String npe() {
        String s = null;
        return String.valueOf(s.length());
    }

    /* 없는 테이블 조회 → BadSqlGrammarException (원인 체인에 PSQLException) */
    @GetMapping("/boom/sql")
    public Object sql() {
        return jdbc.queryForList("select * from no_such_table");
    }

    /* 원인이 3단으로 걸린 예외 → causes 체인 확인용 */
    @GetMapping("/boom/nested")
    public String nested() {
        throw new RuntimeException("outer",
                new IllegalStateException("middle",
                        new IOException("inner")));
    }

    /* 응답은 200인데 로그에만 ERROR가 남는 경우 */
    @GetMapping("/boom/caught")
    public Map<String, String> caught() {
        try {
            Integer.parseInt("abc");
        } catch (NumberFormatException e) {
            log.error("처리 실패", e);
        }
        return Map.of("status", "ok", "note", "에러는 로그에만 남음");
    }

    /* 메시지에 민감정보 → 서버에 ***로 도착해야 함 (마스킹 확인용) */
    @GetMapping("/boom/sensitive")
    public String sensitive() {
        throw new IllegalStateException(
                "login failed password=1234 user=test@example.com token=abc.def.ghi");
    }

    /* WARN만, 예외 없음 → 수집되면 안 됨 */
    @GetMapping("/boom/warn")
    public Map<String, String> warn() {
        log.warn("경고만 남김 (수집되면 안 됨)");
        return Map.of("status", "ok");
    }
}
```

| 주소 | 응답 | Starter에서 확인할 것 |
| --- | --- | --- |
| `/ok` | 200 | 응답이 느려지지 않는지 (비교 기준) |
| `/boom/npe` | 500 | 기본 런타임 에러가 잡히는지 |
| `/boom/sql` | 500 | DB 에러와 원인(PSQLException)이 같이 오는지 |
| `/boom/nested` | 500 | 원인 체인 3단이 순서대로 담기는지 |
| `/boom/caught` | **200** | 응답은 정상인데 로그에만 남은 ERROR도 잡히는지 |
| `/boom/sensitive` | 500 | 서버에 `***`로 가려져 도착하는지 |
| `/boom/warn` | **200** | **안 잡혀야 정상** (ERROR + 예외만 수집) |

### 1-2. DbStartupCheck — 없으면 시작 실패가 재현되지 않는다

```java
package dev.aiops.sample;

import org.springframework.boot.ApplicationArguments;
import org.springframework.boot.ApplicationRunner;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.stereotype.Component;

/**
 * 시작할 때 DB에 한 번 접속한다. 실제 팀 앱에서 JPA·Flyway가 시작 시 DB에 붙는 것을 흉내 낸다.
 * 커넥션 풀은 처음 쓸 때 연결하므로, 이게 없으면 fail 프로필에서도 앱이 정상으로 떠 버린다.
 * 여기서 실패하면 → 앱 시작 실패 → Starter가 STARTUP 에러로 전송 (5단계)
 */
@Component
public class DbStartupCheck implements ApplicationRunner {

    private final JdbcTemplate jdbc;

    public DbStartupCheck(JdbcTemplate jdbc) {
        this.jdbc = jdbc;
    }

    @Override
    public void run(ApplicationArguments args) {
        jdbc.queryForObject("select 1", Integer.class);
    }
}
```

처음엔 `fail` 프로필로 DB 주소를 틀리게 줘도 앱이 **정상으로 떠 버렸다.** Hikari 커넥션 풀은 **처음 쓸 때** 연결하기 때문이다. JPA나 Flyway가 있는 실제 팀 앱은 시작할 때 DB에 붙지만 sample-app은 JDBC만 있어서 아무도 안 붙었다. 그래서 시작 시 `select 1` 한 번을 넣었다.

```yaml
# application-fail.yml
# --spring.profiles.active=fail 로 실행하면 시작 실패를 재현한다 (DB 연결 실패)
spring:
  datasource:
    url: jdbc:postgresql://127.0.0.1:1/nope
    hikari:
      connection-timeout: 2000 # 오래 기다리지 않고 바로 실패
```

```yaml
# application.yml
server:
  port: 8081 # 우리 서버(8080)와 같이 띄우기 위해

spring:
  application:
    name: sample-app
  datasource: # 로컬 Postgres(1단계)에 접속만 한다. 테이블은 쓰지 않는다
    url: ${SAMPLE_DB_URL:jdbc:postgresql://localhost:5432/aiops}
    username: ${SAMPLE_DB_USER:aiops_app}
    password: ${SAMPLE_DB_PASSWORD:app_local}

aiops:
  api-key: ${AIOPS_KEY:} # 없으면 Starter는 경고 한 줄 남기고 꺼진다
  env: local
  endpoint: http://localhost:8080 # 로컬 서버로 보냄 (기본값은 운영 주소)
```

### 1-3. 설계와 다르게 한 곳 세 개

| Jira AI-48 | 실제 | 이유 |
| --- | --- | --- |
| `aiops.key` | `aiops.api-key` | 요구사항 S-01, 팀 안내 문서, 시드 주석이 모두 `api-key`. AI-48만 달랐다 |
| 별도 스키마 `sample` | 스키마 없음 | `/boom/sql`은 "없는 테이블 조회"라 테이블이 필요 없다. 스키마는 owner 권한이 필요해 일만 는다 |
| (없음) | DbStartupCheck 추가 | 위 1-2 |

## 2. 추가로 알면 좋은 활용법

### 2-1. 500이 정상이고, 응답에 예외 이름이 없는 것도 정상

`/boom/*`이 전부 500이라 처음엔 이상하다고 생각했다. 예외를 일부러 던지고 아무도 안 잡으니 Spring이 500을 주는 게 맞다 — 실제 팀 앱의 버그와 같은 상황이다. 응답에 `BadSqlGrammarException` 같은 이름도 안 나오는데, Spring Boot 기본값이 `server.error.include-exception: false`, `include-message: never`, `include-stacktrace: never`라서다. 응답에 넣으면 DB 종류·쿼리·`password=1234` 같은 내부 정보가 사용자에게 보인다.

**Starter가 잡는 건 응답이 아니라 로그다.** 예외 이름과 스택은 sample-app 터미널의 ERROR 로그에 있다. 사용자는 500만 보고, 개발자는 로그를 뒤져야 원인을 안다 — 이게 우리 서비스가 필요한 이유이기도 하다.

PowerShell에서는 `curl` 대신 `curl.exe`를 쓴다. `curl`(=Invoke-WebRequest)은 500에서 예외를 던진다.

### 2-2. 시작 실패 로그는 "Started" 다음에 터진다

```
Started SampleApplication in 2.178 seconds       ← 먼저 찍힘
HikariPool-1 - Starting...
ERROR ... Application run failed
CannotGetJdbcConnectionException: Failed to obtain JDBC Connection
  at dev.aiops.sample.DbStartupCheck.run
Caused by: PSQLException: 127.0.0.1:1 에 대한 연결이 거부되었습니다
Caused by: ConnectException: Connection refused
> Task :sample-app:bootRun FAILED
```

Spring Boot는 "Started"를 기록한 **뒤에** `ApplicationRunner`를 실행한다. 여기서 예외가 나면 `ApplicationFailedEvent`가 발생하고 앱이 종료된다. 5단계에서 Starter가 이 이벤트의 예외를 STARTUP 단계로 서버에 보낸다.

### 2-3. 팀 앱 문제인지 Starter 문제인지 구분하는 법

이 실패를 보고 "라이브러리 때문에 안 뜨는 거면 곤란한데"라는 생각이 먼저 들었다. 구분법:

- **스택에 `dev.aiops.starter.`로 시작하는 줄이 있나** — 이번엔 없었다. `DbStartupCheck`(팀 앱) → Spring → Hikari → 드라이버 → 연결 거부.
- **`[aiops] 비활성화됨: <원인> (starter <버전>)` 줄이 있나** — D-087. Starter는 진입점을 `catch (Throwable)`로 감싸 문제가 생기면 자기만 꺼지고 이 한 줄을 남긴다. 이 줄이 있으면 Starter 문제, 없으면 팀 앱 문제.
- 이걸 안전성 테스트 7종(서버 꺼짐, 키 없음, Jackson 없는 클래스패스, Boot 3·4 등)으로 보장한다. 7개가 다 통과해야 Starter 완료.

이번 실패는 **팀 앱이 잘못된 경우를 일부러 만든 것**이고, 국비 팀이 가장 오래 막히는 "컴파일은 되는데 안 뜨는" 바로 그 상황이다.

## 3. 더 나아가 알면 좋은 것

### 3-1. 원자적 커밋이 깨진 곳

머지된 이력을 보면 `DbStartupCheck.java`는 yml 커밋(`1946bb7 chore(sample): 포트·DB·aiops 설정`)에, `README.md`는 build.gradle 커밋(`f59c51a build(sample): JDBC·PostgreSQL 의존성 추가`)에 섞여 들어갔다. `git add`할 때 폴더나 여러 파일을 한꺼번에 넣은 것 같다. develop 이력이라 되돌리지 않고, 다음부터 `git status`로 무엇이 들어가는지 보고 파일을 하나씩 `add`한다.

### 3-2. 다음에 볼 키워드

- `ApplicationRunner` / `CommandLineRunner` — 앱이 뜬 직후 한 번 도는 코드
- `ApplicationFailedEvent` — Starter의 시작 실패 처리(⑨)가 듣는 이벤트
- Hikari `initializationFailTimeout` — 풀을 만들 때 연결을 시도할지 정하는 값

## 관련 노트

[[AiOps 08 - 하트비트와 Starter 빌드 정리]] · [[AiOps 10 - 선행 테스트 브랜치]]
