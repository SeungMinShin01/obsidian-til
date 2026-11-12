---
출처: Claude 대화
작성일: 2026-11-10
tags: [프로젝트, java]
---

# AiOps - V3 콘솔 스키마 (B)

> 허브: [[AiOps 프로젝트 MOC]]

**12단계 첫 작업, 담당 B(조현우).** PR #24 `[AI-77] V3 콘솔 스키마`. 11/5 머지. 12~16단계가 모두 이 스키마를 보고 일한다. 나머지 12단계(AI-78~81)는 브랜치에서 끝났고 PR 결정을 기다린다.

## 1. 코드: 새 테이블

```sql
-- 로그인 사용자. 관리자 여부 컬럼은 없다 (관리자 = 환경변수 GitHub id 목록)
CREATE TABLE app_user (
    id               BIGSERIAL    PRIMARY KEY,
    github_id        BIGINT       NOT NULL UNIQUE,     -- ① login이 아니라 숫자 id로 식별
    login            TEXT         NOT NULL,
    name             TEXT,
    discord_user_id  TEXT,                             -- (AI-93 협의) UNIQUE 추가
    created_at       TIMESTAMPTZ  NOT NULL DEFAULT now()
);

-- 사용자 ↔ 팀
CREATE TABLE membership (
    id          BIGSERIAL    PRIMARY KEY,
    user_id     BIGINT       NOT NULL REFERENCES app_user(id),
    tenant_id   BIGINT       NOT NULL REFERENCES tenant(id),
    role        TEXT         NOT NULL CHECK (role IN ('OWNER', 'MEMBER')),   -- ② enum 대신 CHECK
    created_at  TIMESTAMPTZ  NOT NULL DEFAULT now(),
    UNIQUE (user_id, tenant_id)                                              -- ③ 한 팀에 한 번
);

-- 초대 링크. 원문 토큰은 저장하지 않는다
CREATE TABLE invitation (
    id          BIGSERIAL    PRIMARY KEY,
    tenant_id   BIGINT       NOT NULL REFERENCES tenant(id),
    token_hash  TEXT         NOT NULL UNIQUE,          -- ④ 해시만
    role        TEXT         NOT NULL CHECK (role IN ('OWNER', 'MEMBER')),
    max_uses    INT          NOT NULL,
    used_count  INT          NOT NULL DEFAULT 0,
    expires_at  TIMESTAMPTZ  NOT NULL,
    ...
);
-- cohort(기수), admin_access_log(관리자 접근 기록)
```

| 번호 | 왜 |
|---|---|
| ① | GitHub `login`(아이디)은 사용자가 바꿀 수 있다. 바뀌지 않는 숫자 id가 기준이다 |
| ② | Postgres enum 타입은 값을 추가하려면 `ALTER TYPE`이 필요하고 트랜잭션 제약도 있다. `text + CHECK`는 CHECK만 바꾸면 된다. 자바에서는 `@Enumerated(EnumType.STRING)` |
| ③ | 같은 사람이 같은 팀에 두 번 들어가지 않게 DB가 막는다 |
| ④ | 초대 링크의 토큰도 비밀번호와 같다. DB가 유출돼도 링크를 만들 수 없게 해시만 둔다(API 키와 같은 방식) |

## 2. 코드: 기존 테이블에 컬럼 추가

```sql
ALTER TABLE tenant
    ADD COLUMN status TEXT NOT NULL DEFAULT 'ACTIVE'                         -- ① 기존 행은 ACTIVE
        CHECK (status IN ('WAITING_OWNER', 'ACTIVE', 'SUSPENDED')),
    ADD COLUMN discord_role_id TEXT, ADD COLUMN discord_category_id TEXT,
    ADD COLUMN discord_channel_local_id TEXT, ADD COLUMN discord_channel_prod_id TEXT,
    ADD COLUMN discord_status TEXT NOT NULL DEFAULT 'NONE'
        CHECK (discord_status IN ('NONE', 'READY', 'FAILED', 'SUSPENDED')),   -- (AI-94 협의) SUSPENDED
    ADD COLUMN discord_error VARCHAR(100);                                     -- (AI-92 협의) "단계:상태"

ALTER TABLE api_key
    ADD COLUMN key_prefix VARCHAR(16),        -- ② 목록 표시용 앞자리 (복원 불가능한 길이)
    ADD COLUMN created_by BIGINT REFERENCES app_user(id),
    ADD COLUMN last_used_at TIMESTAMPTZ;

ALTER TABLE error_group
    ADD COLUMN status TEXT NOT NULL DEFAULT 'OPEN' CHECK (status IN ('OPEN','RESOLVED','IGNORED')),
    ADD COLUMN feedback TEXT CHECK (feedback IN ('UP','DOWN'));               -- 👍/👎
```

- ① `NOT NULL DEFAULT`를 같이 주면 **기존 행에도 기본값이 채워진다.** 이미 있는 시드 팀이 계속 동작한다. `MigrationTest`가 "V2까지 적용 → 기존 행 넣기 → V3 적용 → 기본값 확인" 순서로 이걸 검사한다.
- ② 콘솔 키 목록에서 "aiops_l_ab12…"처럼 보여 주려는 것. 원문을 다시 만들 수 없는 길이로 제한한다.

## 3. 설계 결정: 새 테이블에 RLS를 걸지 않는다 (D-023)

```
로그인 직후: "이 사람이 속한 팀 목록" = SELECT * FROM membership WHERE user_id = ?
  → 이 시점에는 아직 팀을 모른다 (TenantContext 없음)
  → membership에 RLS를 걸면 항상 0건
```

그래서 RLS 대신 **리포지토리 메서드를 고정 조건으로만** 노출한다(`findByUserIdAndTenantId`, `findAllByUserId` 등). `findAll()` 같은 열린 메서드는 쓰지 않는다. `RlsPolicyTest`의 예외 목록에 membership·invitation·admin_access_log를 추가했다(tenant_id가 있지만 의도적으로 RLS 없음).

## 4. Grafana 컬럼 권한

```sql
-- invitation: 테이블 SELECT를 회수하고 token_hash를 뺀 컬럼만 다시 준다
REVOKE SELECT ON invitation FROM grafana_ro;
GRANT SELECT (id, tenant_id, role, max_uses, used_count, expires_at, created_by, created_at) ON invitation TO grafana_ro;

-- tenant·api_key: V2에서 이미 컬럼 단위로 바꿨으므로, 새 컬럼은 자동으로 안 붙는다 → 명시
GRANT SELECT (cohort_id, project_end_date, status, discord_role_id, discord_category_id, ...) ON tenant TO grafana_ro;
GRANT SELECT (key_prefix, created_by, last_used_at) ON api_key TO grafana_ro;
```

`invitation`은 새 테이블이라 `DEFAULT PRIVILEGES`가 **테이블 전체 SELECT를 자동으로 줬다.** 그래서 먼저 회수하고 안전한 컬럼만 다시 준다.

V2의 경고 주석("컬럼을 추가하면 같은 마이그레이션에서 GRANT를 명시")을 그대로 지켰다.

## 5. 설계와 다르게 한 곳

- 엔티티 위치 `model/entity/AppUserEntity.java`(Jira는 `model/AppUser.java`). D-089 규칙이 맞다.
- **V3에 함께 넣은 컬럼 3개**(AI-92 `discord_error`, AI-93 `discord_user_id` UNIQUE, AI-94 SUSPENDED). V3가 아직 어디에도 적용되지 않은 시점이라 V4를 따로 만들지 않았다. 좋은 판단이다. **이제부터는 V4로.** 적용된 V3를 고치면 Flyway 체크섬이 맞지 않아 서버가 뜨지 않는다.

## 6. 이후 12단계(AI-76·78~81) 상황 (11/10 기준)

- 내가 `test/AI-76-authorization`에 권한 E2E 7개 + 의존성 + `AppUserPrincipal`·`RequireOwner`를 올렸다.
- B가 그 위에 78(로그인) ⊂ 79(체인) ⊂ 80(가드) ⊂ 81(역할·관리자)를 쌓았고, **E2E 7개가 테스트 수정 없이 초록**이라고 보고했다(테스트 파일 diff 없음은 내가 확인).
- 결정: test/AI-76을 따로 머지하면 security 의존성만 들어가 develop이 302로 깨지므로 **AI-81 브랜치 PR 하나**로 올린다(D-091). `@RequireOwner`에 TYPE 추가(내 실수), `PostgresContainerSupport`의 `max_connections=300` 승인.

## 7. 다음에 볼 키워드

- Flyway 체크섬, "적용된 마이그레이션은 고치지 않는다"
- `ADD COLUMN … NOT NULL DEFAULT`가 기존 행에 하는 일
- 컬럼 단위 GRANT와 `ALTER DEFAULT PRIVILEGES`
- text + CHECK vs Postgres enum

## 관련 노트

[[AiOps 17 - 팀 격리 RLS (B)]] · [[AiOps 19 - 디스코드 자동화 (B)]]
