---
출처: Claude 대화
작성일: 2026-10-30
tags: [프로젝트, sql]
---

# AiOps - 로컬 Postgres와 계정 3개

> 허브: [[AiOps 프로젝트 MOC]]

1단계(로컬 DB·테이블·서버 뼈대)의 앞부분. 이 노트는 **컨테이너·계정·시드**까지이고, 테이블(V1)·엔티티·서버 설정은 작업이 끝나면 다음 노트로 잇는다.

## 1. 배운 내용

### 1-1. 전체 그림

```
내 PC
├─ Docker 컨테이너 aiops-postgres        ← infra/local/docker-compose.yml
│   └─ DB "aiops"
│       ├─ 계정 3개                       ← infra/local/init/01-roles.sh (첫 기동 때 1회)
│       │    aiops_owner : 테이블 만드는 계정 (Flyway 전용)
│       │    aiops_app   : 서버가 쓰는 계정 (읽기·쓰기만)
│       │    grafana_ro  : 읽기만
│       └─ 테이블 6개 + 시드               ← Flyway (owner로 접속해서 실행)
└─ 서버 :8080 — Flyway는 owner, 런타임은 app 계정으로 같은 DB에 붙는다
```

### 1-2. 계정을 셋으로 나누는 이유 — RLS는 소유자에게 안 먹힌다

11단계에서 팀 격리를 **RLS(Row Level Security)** 로 건다. 서버가 "지금 팀은 7번"이라고 세션 변수에 넣으면 DB가 모든 쿼리에 `WHERE tenant_id = 7`을 자동으로 붙이는 장치. 네 명이 각자 AI로 코드를 쓰면 언젠가 한 번은 그 조건을 빠뜨리는데, 그 한 번이 다른 팀 데이터 유출이라 코드가 아니라 DB가 강제하게 했다.

그런데 Postgres의 RLS는 **테이블 소유자에게는 적용되지 않는다.** 서버가 테이블을 만든 계정으로 붙으면 정책이 있어도 무시된다. 그래서 테이블을 만드는 계정(owner)과 서버가 쓰는 계정(app)을 **1단계부터** 분리한다. 11단계 가서 나누려면 테이블 소유권을 옮기는 작업이 끼어든다.

`grafana_ro`는 10단계 Grafana용. 관리자가 전체 팀을 봐야 하니 11단계에서 `BYPASSRLS`를 붙이되, SELECT만 가능하게.

### 1-3. docker-compose.yml

```yaml
# infra/local/docker-compose.yml
services:
  postgres:
    image: postgres:16
    container_name: aiops-postgres
    ports:
      - "127.0.0.1:5432:5432"       # 내 PC에서만 접속
    environment:
      POSTGRES_DB: aiops
      POSTGRES_USER: postgres       # 슈퍼유저. 계정 3개를 만드는 init 스크립트용
      POSTGRES_PASSWORD: postgres
      AIOPS_OWNER_PASSWORD: owner_local
      AIOPS_APP_PASSWORD: app_local
      GRAFANA_RO_PASSWORD: grafana_local
    volumes:
      - ./init:/docker-entrypoint-initdb.d:ro
      - aiops-pgdata:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres -d aiops"]
      interval: 5s
      timeout: 3s
      retries: 10

volumes:
  aiops-pgdata:
```

- Postgres를 따로 설치하지 않는다. `docker compose up -d`가 `postgres:16` 이미지를 받아 띄운다. 망가지면 `down -v`로 지우고 다시 올린다.
- 포트를 `127.0.0.1`에만 묶어서 같은 네트워크의 다른 PC가 접속 못 하게.
- 비밀번호가 평문으로 있는 건 **로컬 전용**이라서. 운영(`infra/prod/`)은 `.env`로 뺀다.
- `./init`이 컨테이너의 `/docker-entrypoint-initdb.d/`에 연결된다. 그 폴더의 `*.sh`·`*.sql`을 **DB가 처음 생성될 때 딱 한 번** 실행하는 게 공식 postgres 이미지의 동작.

### 1-4. 01-roles.sh — 계정과 "앞으로 만들 테이블"의 권한

```bash
#!/bin/bash
# infra/local/init/01-roles.sh
set -e

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    CREATE ROLE aiops_owner LOGIN PASSWORD '${AIOPS_OWNER_PASSWORD}';
    CREATE ROLE aiops_app   LOGIN PASSWORD '${AIOPS_APP_PASSWORD}';
    CREATE ROLE grafana_ro  LOGIN PASSWORD '${GRAFANA_RO_PASSWORD}';

    GRANT CONNECT ON DATABASE aiops TO aiops_owner, aiops_app, grafana_ro;
    GRANT CREATE, USAGE ON SCHEMA public TO aiops_owner;
    GRANT USAGE ON SCHEMA public TO aiops_app, grafana_ro;

    -- owner가 앞으로 만드는 테이블·시퀀스에 자동으로 권한 부여
    ALTER DEFAULT PRIVILEGES FOR ROLE aiops_owner IN SCHEMA public
        GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO aiops_app;
    ALTER DEFAULT PRIVILEGES FOR ROLE aiops_owner IN SCHEMA public
        GRANT USAGE, SELECT ON SEQUENCES TO aiops_app;
    ALTER DEFAULT PRIVILEGES FOR ROLE aiops_owner IN SCHEMA public
        GRANT SELECT ON TABLES TO grafana_ro;
EOSQL
```

- `.sql`이 아니라 `.sh`인 이유: 비밀번호를 compose의 환경변수에서 읽어 넣으려면 쉘이 필요하다. `.sql`은 변수 치환이 안 된다.
- `ALTER DEFAULT PRIVILEGES`가 핵심. 이 시점엔 테이블이 하나도 없다. "owner가 **앞으로** 만드는 테이블에 app은 읽기·쓰기, grafana_ro는 읽기만 자동 부여"를 미리 걸어 두는 것. 이게 없으면 Flyway가 만든 테이블을 서버(app)가 못 읽는다.
- `GRANT CREATE ON SCHEMA public`은 Postgres 15부터 public 스키마에 기본 CREATE 권한이 없어져서 필요한 줄.
- `set -e` + `ON_ERROR_STOP=1`: 한 줄이라도 실패하면 거기서 멈춘다. 반쯤 만들어진 계정 상태로 컨테이너가 "정상"으로 뜨는 걸 막는다.

### 1-5. 시드는 init 폴더에 두면 안 된다

처음 계획은 `infra/local/init/02-seed-local.sql`이었다. 그런데 init 폴더의 SQL은 컨테이너 첫 기동 때, 즉 **Flyway가 테이블을 만들기 전에** 실행된다. INSERT할 테이블이 없다.

그래서 시드를 Flyway의 **반복 마이그레이션**(`R__` 접두사)으로 옮겼다. 테이블(V1)이 만들어진 뒤에 돌고, 내용이 바뀌면 다시 실행된다. `local` 프로필에서만 위치(`db/seed`)를 읽게 해서 운영엔 절대 안 들어간다.

```sql
-- server/src/main/resources/db/seed/R__seed_local.sql
-- 로컬 개발용 시드. 운영에서는 실행되지 않는다 (local 프로필에서만 locations에 포함).
-- 키 원문: aiops_l_local-dev-key-0001   ← Starter 설정 aiops.api-key 에 넣는 값
-- 아래는 그 원문의 SHA-256 hex. DB에는 해시만 둔다 (규칙 10).

INSERT INTO tenant (id, name, notify_local, created_at)
VALUES (1, '로컬 테스트 팀', true, now())
ON CONFLICT (id) DO NOTHING;

INSERT INTO api_key (id, tenant_id, key_hash, env, created_at)
VALUES (1, 1, 'f0e8ca65e485ef8f10c8c35c7f0cb6417582105c7237e41f8cc692ac31f1e1f6', 'local', now())
ON CONFLICT (id) DO NOTHING;

-- 시퀀스를 시드 뒤로 맞춤 (안 하면 다음 INSERT가 id=1과 충돌)
SELECT setval('tenant_id_seq', (SELECT max(id) FROM tenant));
SELECT setval('api_key_id_seq', (SELECT max(id) FROM api_key));
```

키 원문은 주석에만 있고 DB에는 SHA-256 해시만 들어간다. Starter가 `X-AIOPS-KEY: aiops_l_local-dev-key-0001`로 보내면 서버가 해시해서 비교한다. DB가 통째로 새도 키는 안 샌다.

## 2. 추가로 알면 좋은 활용법

### 2-1. Windows 줄 끝(CRLF)

`.sh`를 Windows에서 만들면 줄 끝이 CRLF가 돼서 Linux 컨테이너가 첫 줄을 `#!/bin/bash\r`로 읽고 실행기를 못 찾는다. VS Code 오른쪽 아래 `CRLF`를 눌러 `LF`로 바꾸고 저장. 이건 돌려 보기 전엔 모르는 종류의 실수라 확인 명령을 같이 둔다.

```bash
docker compose -f infra/local/docker-compose.yml up -d
docker compose -f infra/local/docker-compose.yml logs postgres | tail -5
docker exec -it aiops-postgres psql -U aiops_owner -d aiops -c "select current_user"
docker exec -it aiops-postgres psql -U aiops_app   -d aiops -c "select current_user"
docker exec -it aiops-postgres psql -U grafana_ro  -d aiops -c "select current_user"
```

셋 다 이름이 나오면 스크립트가 끝까지 돈 것.

### 2-2. init 스크립트는 다시 안 돈다

`01-roles.sh`를 고친 뒤 `docker compose restart`를 해도 **반영되지 않는다.** 볼륨에 이미 DB가 있으면 init을 건너뛴다. 고쳤으면 `docker compose down -v`(볼륨 삭제)로 완전히 지우고 다시 `up`.

### 2-3. 주어진 코드를 믿을지 판단하는 법

이 스크립트를 보고 "이거 믿고 써도 되나"가 됐는데, 기준은 이렇게 잡았다. (1) `docker-entrypoint-initdb.d`의 동작과 환경변수 치환은 공식 이미지 문서에 적힌 그대로다. (2) `CREATE ROLE`·`ALTER DEFAULT PRIVILEGES`는 표준 SQL이다. (3) 그래도 오타·줄 끝 문제는 돌려 봐야 안다 — 그래서 **확인 명령으로 검증한 뒤 커밋**, 그리고 이 작업은 실패해도 `down -v` 한 줄로 되돌릴 수 있어서 비용이 0이다. #되돌릴수있는가

## 3. 더 나아가 알면 좋은 것

### 3-1. 이어서 할 것 (1단계 나머지)

- `server/build.gradle`: data-jpa, validation, `spring-boot-starter-flyway` + `flyway-database-postgresql`, postgresql, Testcontainers
- `application.yml`: `datasource`는 app 계정, `spring.flyway.user`는 owner 계정, `ddl-auto=validate`, `open-in-view=false`, local 프로필이면 `flyway.locations`에 `classpath:db/seed` 추가
- `V1__init.sql`: tenant, api_key, error_group, error_event, app_snapshot, ingest_stat + 인덱스
- 엔티티 6개 + JpaRepository 6개, `GET /health`, Testcontainers 리포지토리 테스트 1개

### 3-2. 다음에 볼 키워드

- `BYPASSRLS` — 11단계에서 grafana_ro에 붙일 속성. 슈퍼유저만 줄 수 있어서 init 스크립트에서 해야 한다
- `set_config('app.tenant_id', ?, true)` — 세 번째 인자 true가 "이 트랜잭션 안에서만". false면 커넥션 풀이 그 연결을 다음 팀에 재사용할 때 이전 팀 번호가 남는다
- `pg_isready` — "컨테이너가 떴다"와 "접속을 받는다"는 다르다. healthcheck가 그 차이를 메운다

## 관련 노트

[[AiOps 04 - CI와 PR 템플릿]]
