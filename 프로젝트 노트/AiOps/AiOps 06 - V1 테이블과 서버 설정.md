---
출처: Claude 대화
작성일: 2026-11-02
tags: [프로젝트, sql]
---

# AiOps - V1 테이블과 서버 설정

> 허브: [[AiOps 프로젝트 MOC]]

**PR #3 `[AI-6] 로컬 DB·테이블·서버 뼈대·시드` (1/3 → 05, 2/3 → 이 노트, 3/3 → 07)**

05에서 컨테이너와 계정 3개까지 만들었고, 이 노트는 서버가 그 DB에 붙어 테이블을 만들고 뜨는 데까지다. Jira 하위 작업으로는 AI-27(서버 기동)·AI-28(V1)·AI-29(시드) 부분.

## 1. 배운 내용

### 1-1. server/build.gradle

PR #3이 머지된 시점의 최종본이다. Lombok·Testcontainers 줄은 07에서 붙인 것.

```groovy
apply plugin: 'org.springframework.boot'
apply plugin: 'io.spring.dependency-management'

dependencies {
    implementation project(':protocol')

    implementation 'org.springframework.boot:spring-boot-starter-webmvc'
    implementation 'org.springframework.boot:spring-boot-starter-data-jpa'
    implementation 'org.springframework.boot:spring-boot-starter-validation'
    implementation 'org.springframework.boot:spring-boot-starter-flyway'
    implementation 'org.flywaydb:flyway-database-postgresql'
    runtimeOnly 'org.postgresql:postgresql'

    // 서버 모듈에만. 엔티티에는 @Getter, @NoArgsConstructor(PROTECTED)만 (D-089)
    compileOnly 'org.projectlombok:lombok'
    annotationProcessor 'org.projectlombok:lombok'

    testImplementation 'org.springframework.boot:spring-boot-starter-test'
    testImplementation 'org.springframework.boot:spring-boot-starter-webmvc-test'
    testImplementation 'org.testcontainers:testcontainers-postgresql'
    testRuntimeOnly 'org.junit.platform:junit-platform-launcher'
}
```

- Boot 4부터 스타터 이름이 바뀌었다. `spring-boot-starter-web` → `spring-boot-starter-webmvc`, Flyway도 `spring-boot-starter-flyway`가 따로 생겼다. 테스트도 `…-webmvc-test`처럼 모듈별.
- Flyway 10부터 DB별 지원이 별도 모듈이라 `flyway-database-postgresql`을 같이 넣어야 한다. 빠뜨리면 "Unsupported Database" 에러.

### 1-2. application.yml — 계정 두 개로 붙는다

```yaml
spring:
  application:
    name: aiops-server
  profiles:
    default: local              # 아무것도 안 주면 local로 뜬다

  datasource:                   # 서버 런타임 = app 계정 (테이블 소유자 아님 → 11단계 RLS 대상)
    url: ${AIOPS_DB_URL}
    username: ${AIOPS_DB_APP_USER}
    password: ${AIOPS_DB_APP_PASSWORD}

  flyway:                       # 마이그레이션 = owner 계정 (테이블 소유자)
    user: ${AIOPS_DB_OWNER_USER}
    password: ${AIOPS_DB_OWNER_PASSWORD}
    locations: classpath:db/migration

  jpa:
    open-in-view: false         # 요청 끝까지 DB 연결을 붙잡지 않는다
    hibernate:
      ddl-auto: validate        # 테이블은 Flyway만 만든다. JPA는 맞는지 검사만

server:
  port: 8080
```

```yaml
# application-local.yml
spring:
  datasource:
    url: jdbc:postgresql://localhost:5432/aiops
    username: aiops_app
    password: app_local
  flyway:
    user: aiops_owner
    password: owner_local
    locations: classpath:db/migration,classpath:db/seed # 로컬에서만 시드 포함
```

- **datasource는 app 계정, flyway는 owner 계정.** 같은 DB에 두 계정이 붙는다. 테이블을 만드는 건 owner(Flyway)뿐이고 서버 런타임은 app이라, 11단계에서 RLS를 걸면 서버 쿼리에 정책이 실제로 먹는다(05의 1-2).
- 공통 yml에는 `${AIOPS_DB_URL}` 같은 환경변수만 두고, 로컬 값은 `application-local.yml`에. `profiles.default: local`이라 아무것도 안 주면 local로 뜬다. 운영은 VM에서 환경변수로 넣는다.
- `ddl-auto: validate` — 테이블은 Flyway SQL로만 만들고, JPA는 엔티티와 테이블이 맞는지 **검사만** 한다. 안 맞으면 서버가 아예 안 뜬다. `update`로 두면 JPA가 몰래 컬럼을 고쳐서 마이그레이션 기록과 실제 DB가 어긋난다.
- `open-in-view: false` — 기본값 true면 HTTP 요청이 끝날 때까지 DB 연결을 붙잡는다. 수집 API는 요청이 많고 짧아서 끈다.
- 로컬에서만 `db/seed` 위치를 추가 → 시드(`R__seed_local.sql`)는 운영에 절대 안 들어간다.

### 1-3. V1 테이블 8개

| 테이블 | 무엇을 저장 | 누가 쓰나 |
| --- | --- | --- |
| `tenant` | 팀. 디스코드 웹훅(비밀값), local 알림 여부 | 전체 |
| `api_key` | 키 **해시**(SHA-256 hex, CHAR 64), env, 폐기 시각 | 2단계 키 인증 |
| `error_group` | 같은 원인 묶음. 지문, 첫/마지막 발생, 횟수, AI 설명 | 6·7단계 |
| `error_event` | Starter가 보낸 에러 원본 1건 = 1행. payload는 JSONB | 2단계 저장, 6단계 묶음 |
| `app_snapshot` | hello 1건 = 1행(앱 켤 때마다 INSERT) | 2단계, 콘솔 |
| `ingest_stat` | 팀·env·날짜별 받은 수·버린 수 | 9단계 |
| `llm_usage` | 날짜별 LLM 호출 수 (서버 전체 상한) | 7단계 |
| `heartbeat_last` | 앱 인스턴스별 마지막 신호 → "연결됨" 판정 (D-086) | 2단계 |

```sql
-- V1: MVP 1부(v0.1) 테이블 8개. 소유자는 aiops_owner (Flyway 접속 계정).
-- 팀 데이터 테이블은 전부 tenant_id를 갖는다 → 11단계 RLS를 컬럼 추가 없이 건다.
-- 한 번 머지되면 이 파일은 수정하지 않는다. 바꿀 게 있으면 V2, V3…를 새로 만든다.

-- 팀
CREATE TABLE tenant (
    id                     BIGSERIAL    PRIMARY KEY,
    name                   VARCHAR(100) NOT NULL,
    discord_webhook_local  TEXT,                       -- 비밀값. 응답·로그에 노출 금지 (규칙 10)
    discord_webhook_prod   TEXT,
    notify_local           BOOLEAN      NOT NULL DEFAULT TRUE,
    created_at             TIMESTAMPTZ  NOT NULL DEFAULT now()
);

-- API 키 (원문 저장 금지, SHA-256 hex만)
CREATE TABLE api_key (
    id          BIGSERIAL   PRIMARY KEY,
    tenant_id   BIGINT      NOT NULL REFERENCES tenant(id),
    key_hash    CHAR(64)    NOT NULL UNIQUE,
    env         VARCHAR(10) NOT NULL CHECK (env IN ('local', 'prod')),
    revoked_at  TIMESTAMPTZ,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- 같은 원인끼리 묶은 그룹 (6단계가 채움)
-- status·resolved_at·feedback은 콘솔(16단계)용이라 V3에서 추가한다
CREATE TABLE error_group (
    id                BIGSERIAL    PRIMARY KEY,
    tenant_id         BIGINT       NOT NULL REFERENCES tenant(id),
    fingerprint       CHAR(64)     NOT NULL,
    exception_type    VARCHAR(300) NOT NULL,
    top_frame         VARCHAR(500),
    first_env         VARCHAR(10)  NOT NULL,
    first_seen_at     TIMESTAMPTZ  NOT NULL DEFAULT now(),
    last_seen_at      TIMESTAMPTZ  NOT NULL DEFAULT now(),
    occurrence_count  BIGINT       NOT NULL DEFAULT 1,
    ai_explanation    TEXT,
    ai_explained_at   TIMESTAMPTZ,
    UNIQUE (tenant_id, fingerprint)
);

-- Starter가 보낸 에러 원본 1건 = 1행 (2단계가 저장, 6단계가 그룹으로 묶음)
CREATE TABLE error_event (
    id           BIGSERIAL    PRIMARY KEY,
    tenant_id    BIGINT       NOT NULL REFERENCES tenant(id),
    env          VARCHAR(10)  NOT NULL,
    group_id     BIGINT       REFERENCES error_group(id),
    payload      JSONB        NOT NULL,                 -- protocol ErrorEvent를 받은 그대로
    app_name     VARCHAR(200),
    app_commit   VARCHAR(64),
    host_hash    VARCHAR(16),
    received_at  TIMESTAMPTZ  NOT NULL DEFAULT now(),
    processed    BOOLEAN      NOT NULL DEFAULT FALSE
);

-- hello 1건 = 1행 (앱이 켜질 때마다 INSERT. "마지막 hello" = max(received_at))
CREATE TABLE app_snapshot (
    id           BIGSERIAL    PRIMARY KEY,
    tenant_id    BIGINT       NOT NULL REFERENCES tenant(id),
    env          VARCHAR(10)  NOT NULL,
    host_hash    VARCHAR(16),
    payload      JSONB        NOT NULL,                 -- protocol HelloRequest를 받은 그대로
    received_at  TIMESTAMPTZ  NOT NULL DEFAULT now()
);

-- 팀·env·날짜별 받은 수·버린 수
CREATE TABLE ingest_stat (
    id              BIGSERIAL   PRIMARY KEY,
    tenant_id       BIGINT      NOT NULL REFERENCES tenant(id),
    env             VARCHAR(10) NOT NULL,
    day             DATE        NOT NULL,
    received_count  BIGINT      NOT NULL DEFAULT 0,
    dropped_count   BIGINT      NOT NULL DEFAULT 0,
    UNIQUE (tenant_id, env, day)
);

-- LLM 일일 호출 수 (서버 전체 상한. 팀 데이터가 아니므로 tenant_id·RLS 없음)
CREATE TABLE llm_usage (
    day         DATE    PRIMARY KEY,
    call_count  INT     NOT NULL DEFAULT 0
);

-- 앱 인스턴스(PC·서버 1대)별 마지막 신호. "연결됨" 판정의 근거 (D-086)
-- hello·하트비트·이벤트 묶음 중 무엇이든 받으면 UPSERT로 last_seen_at 갱신
CREATE TABLE heartbeat_last (
    id            BIGSERIAL    PRIMARY KEY,
    tenant_id     BIGINT       NOT NULL REFERENCES tenant(id),
    env           VARCHAR(10)  NOT NULL,
    host_hash     VARCHAR(16)  NOT NULL,
    app_name      VARCHAR(200),
    started_at    TIMESTAMPTZ,              -- 마지막 hello 시각 (이번 실행이 언제 시작됐나)
    last_seen_at  TIMESTAMPTZ  NOT NULL,
    UNIQUE (tenant_id, env, host_hash)
);

-- 인덱스
CREATE INDEX idx_error_event_tenant_received ON error_event (tenant_id, received_at);
CREATE INDEX idx_error_event_unprocessed     ON error_event (received_at) WHERE processed = FALSE;  -- 6단계 재처리용
CREATE INDEX idx_error_event_group           ON error_event (group_id);
CREATE INDEX idx_error_group_tenant_last     ON error_group (tenant_id, last_seen_at DESC);
CREATE INDEX idx_app_snapshot_tenant_env     ON app_snapshot (tenant_id, env, received_at DESC);
```

처음 설계와 다르게 정한 것 세 가지:

- `error_group.status`·`feedback`은 **V3으로 미뤘다.** 콘솔(16단계)에서만 쓰는 컬럼이라 v0.1에 넣으면 아무도 안 쓰는 컬럼이 생긴다. 대신 V1 주석에 "V3에서 추가"를 남겼다.
- `ingest_stat`은 `UNIQUE (tenant_id, env, day)` — 하루에 한 줄을 `ON CONFLICT … DO UPDATE`로 더해 가는 구조라 이 키가 있어야 한다.
- `llm_usage`에는 `tenant_id`가 없다. 팀 데이터가 아니라 "서버 전체가 오늘 LLM을 몇 번 불렀나"라서 RLS도 걸지 않는다.

`heartbeat_last`는 C 탈퇴 전후로 Starter가 팀 앱을 죽일 수 있는 경로를 점검하다가 생긴 테이블이다. hello는 앱이 켜질 때 1번뿐이라 "지금도 살아 있나"를 모른다. 60초마다 하트비트를 보내고 3분 안에 신호가 있으면 "연결됨"으로 본다. 원래 v0.6 기능이었는데 MVP로 당겼다(D-086, 08 노트).

### 1-4. GET /health

```java
package dev.aiops.server.model.entity;

import java.util.Map;

import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

/** 서버가 떴는지 확인용. 10단계 Caddy·VM 점검에도 쓴다 */
@RestController
public class HealthController {

    @GetMapping("/health")
    public Map<String, String> health() {
        return Map.of("status", "UP");
    }
}
```

서버가 떴는지 보는 가장 작은 API. (패키지가 `model.entity`로 들어간 건 옮기다 생긴 실수다. 07의 2-4에서 다룬다.) 10단계에서 Caddy·VM 점검에도 쓴다. PowerShell에서는 `curl`이 `Invoke-WebRequest`라 출력이 길게 나오지만 `Content : {"status":"UP"}`만 보면 된다.

## 2. 추가로 알면 좋은 활용법

### 2-1. 처음 띄울 때 만난 에러 세 개

| 증상 | 원인 | 해결 |
| --- | --- | --- |
| `'url' must start with "jdbc"` | `application-local.yml`이 없어서 `${AIOPS_DB_URL}`이 비어 있음 | local yml 생성 |
| `/health` 404 | HealthController를 아직 안 만들었음 | 생성 |
| `docker compose up -d`가 설정 파일 없다고 함 | compose 파일이 `infra/local/` 아래 | `docker compose -f infra/local/docker-compose.yml up -d` |

DB는 **처음 한 번 `up -d`** 해 두면 `restart: unless-stopped`라 Docker Desktop이 켜질 때 같이 뜬다. 팀원도 마찬가지 — Docker Desktop만 켜 두면 된다.

### 2-2. bootRun 로그에서 볼 줄

```
Successfully validated 2 migrations          ← V1 + R__seed_local (반복 마이그레이션도 개수에 들어감)
Schema "public" is up to date                ← 이미 적용됨
Found 8 JPA repository interfaces            ← (07) 리포지토리 8개를 다 찾음
Started AiopsServerApplication in 6.17 sec   ← ddl-auto validate 통과 = 엔티티와 테이블이 일치
```

### 2-3. V1은 한 번 머지되면 고치지 않는다

Flyway는 적용한 파일의 체크섬을 `flyway_schema_history`에 남긴다. V1을 고치면 다른 사람 DB에서 체크섬이 안 맞아 서버가 안 뜬다. 바꿀 게 생기면 V2, V3을 새로 만든다. 반대로 `R__` 파일은 내용이 바뀌면 다시 실행되는 게 정상 동작이다.

## 3. 더 나아가 알면 좋은 것

### 3-1. 키는 해시만

시드의 키 원문(`aiops_l_local-dev-key-0001`)은 SQL **주석에만** 있고 DB에는 SHA-256 hex만 들어간다. Starter가 헤더로 원문을 보내면 서버가 해시해서 `key_hash`와 비교한다. DB가 통째로 새도 키 원문은 안 샌다. 비밀번호처럼 솔트를 안 쓰는 건, 키가 충분히 길고 무작위라 사전 공격이 의미 없어서다.

### 3-2. 다음에 볼 키워드

- `ON CONFLICT … DO UPDATE` — ingest_stat·llm_usage·heartbeat_last·error_group이 전부 이 upsert로 쓰인다(2·6·7단계)
- 부분 인덱스 `WHERE processed = FALSE` — 재처리 대상만 인덱스에 넣어 작게 유지
- `flyway_schema_history` — 무엇이 언제 적용됐는지 DB 안에 남는 기록

## 관련 노트

[[AiOps 05 - 로컬 Postgres와 계정 3개]] · [[AiOps 07 - 엔티티·리포지토리·Testcontainers]]
