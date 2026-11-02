---
출처: Claude 대화
작성일: 2026-11-02
tags: [프로젝트, java]
---

# AiOps - 엔티티·리포지토리·Testcontainers

> 허브: [[AiOps 프로젝트 MOC]]

**PR #3 `[AI-6] 로컬 DB·테이블·서버 뼈대·시드` (3/3)** — 머지 커밋 `ddd9336`. 같은 내용을 main으로 잘못 연 PR #2는 닫았다.

V1 테이블 8개에 맞춰 엔티티 8개, 리포지토리 8개, 진짜 Postgres로 도는 테스트를 만들었다. 이 PR이 들어가야 A가 2단계(수집 API)를 시작할 수 있다.

## 1. 배운 내용

### 1-1. 서버 패키지 구조 — 기능별에서 계층으로 (D-088)

Jira 하위 작업 45개가 원래 기능별 패키지(`ingest/`, `processing/`, `llm/`, `notify/` …)로 적혀 있었다. 나는 익숙한 컨트롤러-서비스-모델 계층으로 가고 싶었고, 결국 이렇게 정했다.

```
dev.aiops.server.
  controller/ (admin/)   REST 컨트롤러, @RestControllerAdvice
  service/               비즈니스 로직
  model/
    entity/              JPA 엔티티
    repository/          JpaRepository
    dto/                 요청·응답 record
  config/  security/  client/(외부 호출)  scheduler/(@Scheduled)
```

순수 계층(controller/service/model만)은 필터·LLM 클라이언트·스케줄러까지 전부 `service/`에 들어가 40개 넘게 쌓인다. 그래서 **성격이 다른 것만 따로 뺀 절충안**이다. Jira 경로는 에이전트로 49개 이슈를 일괄 수정했다. 다만 처음엔 `model/`, `repository/`, `dto/`를 최상위로 적었는데 실제 내 폴더는 `model/` 안에 셋을 넣은 구조라 D-088을 한 번 더 고쳤다 — Jira 쪽 2차 수정은 중간에 멈춰서 일부만 반영됐을 수 있다(남은 일).

테스트 패키지는 대상 클래스와 같게(`test/.../model/repository/`), 공통 도구는 `support/`.

### 1-2. Lombok은 서버에만, 엔티티에는 두 개만 (D-089)

처음엔 getter를 직접 썼다. 이유는 (1) 규칙 3 "새 의존성 금지" (2) 클래스에 `@Getter`를 붙이면 `keyHash` 같은 비밀값에도 getter가 생김 (3) `@Data`·`@Setter`·`@ToString`은 엔티티에서 웹훅 주소가 로그에 찍히거나 아무 데서나 값이 바뀌는 사고를 만든다. 그런데 "왜 @Getter를 안 쓰냐"는 내 질문에서 다시 정했다.

- 규칙 3은 원래 **팀 앱에 들어가는 Starter**를 지키려는 규칙이라 서버는 예외로 둬도 된다.
- 엔티티 이름은 `XxxEntity`, 붙이는 건 `@Getter` + `@NoArgsConstructor(access = PROTECTED)`만.
- 비밀값 필드는 `@Getter(AccessLevel.NONE)`.

```java
package dev.aiops.server.model.entity;

import jakarta.persistence.*;
import lombok.AccessLevel;
import lombok.Getter;
import lombok.NoArgsConstructor;
import org.hibernate.annotations.JdbcTypeCode;
import org.hibernate.type.SqlTypes;
import java.time.Instant;

@Entity
@Table(name = "api_key")
@Getter
@NoArgsConstructor(access = AccessLevel.PROTECTED)
public class ApiKeyEntity {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(name = "tenant_id", nullable = false)
    private Long tenantId;

    // CHAR(64). 원문이 아니라 SHA-256 hex. 조회는 리포지토리로만 → getter 제외
    @Getter(AccessLevel.NONE)
    @JdbcTypeCode(SqlTypes.CHAR)
    @Column(name = "key_hash", nullable = false, unique = true, length = 64)
    private String keyHash;

    @Column(nullable = false, length = 10)
    private String env;

    @Column(name = "revoked_at", columnDefinition = "timestamptz")
    private Instant revokedAt;

    @Column(name = "created_at", nullable = false, columnDefinition = "timestamptz")
    private Instant createdAt;

    public ApiKeyEntity(Long tenantId, String keyHash, String env) {
        this.tenantId = tenantId;
        this.keyHash = keyHash;
        this.env = env;
        this.createdAt = Instant.now();
    }

    public void revoke() {
        if (revokedAt == null) {
            revokedAt = Instant.now();
        }
    }

    public boolean isActive() {
        return revokedAt == null;
    }
}
```

`protected` 기본 생성자는 JPA(Hibernate)가 객체를 만들 때 쓰는 것이고, 내 코드는 인자 있는 `public` 생성자만 쓴다. `createdAt`을 생성자에서 채우는 건 DB의 `DEFAULT now()`가 있어도 Hibernate가 INSERT에 `null`을 명시적으로 넣어 NOT NULL 위반이 나기 때문.

### 1-3. validate를 통과시킨 세 가지 매핑

`ddl-auto: validate`는 엔티티 타입과 DB 컬럼 타입을 비교한다. 그냥 두면 어긋나는 곳이 세 군데였다.

| DB | 그냥 두면 | 해결 |
| --- | --- | --- |
| `CHAR(64)` | String은 varchar로 봐서 불일치 | `@JdbcTypeCode(SqlTypes.CHAR)` |
| `JSONB` | `@JdbcTypeCode(SqlTypes.JSON)`은 Hibernate가 JSON 변환기(Jackson)를 찾는데, Boot 4 기본은 Jackson 3이라 맞물리는지 확신 없음 | `columnDefinition = "jsonb"` + `@ColumnTransformer(write = "?::jsonb")` — 문자열을 그대로 jsonb로 캐스팅 |
| `TIMESTAMPTZ` | Instant의 타입 이름(`timestamp with time zone`)과 DB 이름(`timestamptz`) 비교가 실패할 수 있음 | `columnDefinition = "timestamptz"` |

```java
// ErrorEventEntity의 payload
    // protocol ErrorEvent JSON 원문. Jackson을 거치지 않고 문자열 → jsonb 캐스팅
    @Column(nullable = false, columnDefinition = "jsonb")
    @ColumnTransformer(write = "?::jsonb")
    private String payload;
```

`IngestStatEntity`·`LlmUsageEntity`·`HeartbeatLastEntity`는 공개 생성자가 없다. 쓰기는 2·7단계에서 `ON CONFLICT` 쿼리로만 하고 엔티티는 조회용이다. `ErrorGroupEntity`의 횟수도 엔티티에서 `count++` 하지 않는다 — 같은 에러가 동시에 들어오면 둘 다 1에서 2로 바꿔 하나가 유실된다. 6단계에서 `UPDATE … SET occurrence_count = occurrence_count + 1`로 DB가 더하게 한다.

### 1-4. 리포지토리 8개 — 메서드 이름이 곧 쿼리

| 리포지토리 | 추가 메서드 | 누가 쓰나 |
| --- | --- | --- |
| ApiKeyRepository | `findByKeyHashAndRevokedAtIsNull` | 2단계 키 인증 (폐기 안 된 키만) |
| ErrorGroupRepository | `findByTenantIdAndFingerprint` | 6단계 |
| AppSnapshotRepository | `findTopByTenantIdAndEnvOrderByReceivedAtDesc` | "마지막 hello" |
| HeartbeatLastRepository | `findByTenantIdAndEnv` | 연결 상태 |
| Tenant·ErrorEvent·IngestStat·LlmUsage | 없음 | 쓰는 단계에서 추가 |

Spring Data는 서버가 뜰 때 메서드 이름을 엔티티 필드와 대조한다. 오타가 있으면 `No property … found`로 서버가 안 뜬다. 그래서 bootRun이 뜬 것 자체가 검사다.

### 1-5. Testcontainers — 진짜 Postgres, 진짜 계정

```java
package dev.aiops.server.support;

import org.springframework.test.context.DynamicPropertyRegistry;
import org.springframework.test.context.DynamicPropertySource;
import org.testcontainers.postgresql.PostgreSQLContainer;
import org.testcontainers.utility.MountableFile;

/**
 * 진짜 Postgres 16을 띄우고, 로컬과 같은 01-roles.sh로 계정 3개를 만든다.
 * 서버는 app 계정, Flyway는 owner 계정으로 붙는다 (로컬·운영과 같은 구조).
 * 
 * @ServiceConnection을 쓰지 않는 이유: 슈퍼유저로 붙게 되어 RLS 테스트(11단계)가 무의미해진다.
 */
public abstract class PostgresContainerSupport {

    static final PostgreSQLContainer POSTGRES = new PostgreSQLContainer("postgres:16")
            .withDatabaseName("aiops") // 01-roles.sh가 'aiops'를 직접 쓴다
            .withUsername("postgres")
            .withPassword("postgres")
            .withEnv("AIOPS_OWNER_PASSWORD", "owner_test")
            .withEnv("AIOPS_APP_PASSWORD", "app_test")
            .withEnv("GRAFANA_RO_PASSWORD", "grafana_test")
            .withCopyFileToContainer(
                    MountableFile.forHostPath("../infra/local/init/01-roles.sh", 0755),
                    "/docker-entrypoint-initdb.d/01-roles.sh");

    static {
        POSTGRES.start(); // 모든 테스트 클래스가 컨테이너 하나를 같이 쓴다
    }

    @DynamicPropertySource
    static void dbProperties(DynamicPropertyRegistry registry) {
        registry.add("spring.datasource.url", POSTGRES::getJdbcUrl);
        registry.add("spring.datasource.username", () -> "aiops_app");
        registry.add("spring.datasource.password", () -> "app_test");
        registry.add("spring.flyway.user", () -> "aiops_owner");
        registry.add("spring.flyway.password", () -> "owner_test");
        registry.add("spring.flyway.locations", () -> "classpath:db/migration"); // 시드 제외
    }
}
```

- 로컬과 같은 `01-roles.sh`를 컨테이너 initdb에 복사해서 계정 3개를 똑같이 만든다. 경로가 `../infra/...`인 건 Gradle이 테스트를 `server/` 폴더에서 돌리기 때문.
- `@ServiceConnection`(Boot가 컨테이너에 자동으로 붙여 주는 기능)을 안 쓴 이유: 그러면 슈퍼유저 `postgres`로 붙는다. **슈퍼유저와 테이블 소유자는 RLS를 무시**해서 11단계 격리 테스트가 의미 없어진다. 그래서 `@DynamicPropertySource`로 app·owner 계정을 직접 넣었다.
- 테스트에선 시드를 빼고 `db/migration`만.
- CI(GitHub Actions ubuntu)에도 Docker가 있어서 그대로 돈다. 빌드 시간이 1분 → 2분 정도로 늘었다.

```java
package dev.aiops.server.model.repository;

import dev.aiops.server.model.entity.*;
import dev.aiops.server.support.PostgresContainerSupport;
import jakarta.persistence.EntityManager;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.transaction.annotation.Transactional;

import java.time.Instant;

import static org.assertj.core.api.Assertions.assertThat;

@SpringBootTest(webEnvironment = SpringBootTest.WebEnvironment.NONE)
@Transactional
class RepositoryTest extends PostgresContainerSupport {

    @Autowired
    TenantRepository tenants;
    @Autowired
    ApiKeyRepository apiKeys;
    @Autowired
    ErrorGroupRepository groups;
    @Autowired
    ErrorEventRepository events;
    @Autowired
    AppSnapshotRepository snapshots;
    @Autowired
    EntityManager em;

    @Test
    void 키_해시로_찾고_폐기하면_안_찾아진다() {
        TenantEntity t = tenants.save(new TenantEntity("테스트 팀"));
        String hash = "a".repeat(64);
        ApiKeyEntity key = apiKeys.saveAndFlush(new ApiKeyEntity(t.getId(), hash, "local"));

        assertThat(apiKeys.findByKeyHashAndRevokedAtIsNull(hash)).isPresent();

        key.revoke();
        apiKeys.saveAndFlush(key);

        assertThat(apiKeys.findByKeyHashAndRevokedAtIsNull(hash)).isEmpty();
    }

    @Test
    void payload가_jsonb로_저장되어_DB에서_필드를_꺼낼_수_있다() {
        TenantEntity t = tenants.save(new TenantEntity("테스트 팀"));
        ErrorEventEntity e = events.saveAndFlush(new ErrorEventEntity(
                t.getId(), "local",
                "{\"exceptionType\":\"java.lang.NullPointerException\"}",
                "sample", null, "abc123"));

        Object type = em.createNativeQuery(
                "select payload->>'exceptionType' from error_event where id = :id")
                .setParameter("id", e.getId())
                .getSingleResult();

        assertThat(type).isEqualTo("java.lang.NullPointerException");
    }

    @Test
    void 같은_팀_같은_지문은_하나의_그룹으로_찾아진다() {
        TenantEntity t = tenants.save(new TenantEntity("테스트 팀"));
        String fp = "b".repeat(64);
        groups.saveAndFlush(new ErrorGroupEntity(t.getId(), fp,
                "java.lang.NullPointerException", "dev.sample.Foo.bar:10", "local"));

        assertThat(groups.findByTenantIdAndFingerprint(t.getId(), fp)).isPresent();
        assertThat(groups.findByTenantIdAndFingerprint(t.getId(), "c".repeat(64))).isEmpty();
    }

    @Test
    void 마지막_hello는_가장_최근_것이다() {
        TenantEntity t = tenants.save(new TenantEntity("테스트 팀"));
        Instant now = Instant.now();
        snapshots.save(new AppSnapshotEntity(t.getId(), "local", "h1", "{\"v\":1}", now.minusSeconds(60)));
        AppSnapshotEntity newer = snapshots.saveAndFlush(
                new AppSnapshotEntity(t.getId(), "local", "h1", "{\"v\":2}", now));

        AppSnapshotEntity latest = snapshots
                .findTopByTenantIdAndEnvOrderByReceivedAtDesc(t.getId(), "local")
                .orElseThrow();

        assertThat(latest.getId()).isEqualTo(newer.getId());
    }
}
```

## 2. 추가로 알면 좋은 활용법

### 2-1. 클래스 이름을 바꾸면 생성자 이름도

엔티티를 `Tenant` → `TenantEntity`로 바꾸면서 생성자는 `Tenant(...)`로 남아 8개 전부 컴파일 에러가 났다. 자바는 생성자 이름이 클래스 이름과 같아야 하고, 다르면 "반환 타입 없는 메서드"로 본다(`invalid method declaration; return type required`). VS Code의 F2(Rename Symbol)로 바꾸면 생성자까지 같이 바뀐다.

### 2-2. 저장 안 된 빈 파일 — 두 번 당했다

`ErrorGroupEntity.java`가 0바이트였고, sample-app(09)에서는 `DbStartupCheck.java`가 또 0바이트였다. 탭에 ● 표시가 남아 있는데 넘어간 것. **File → Auto Save**를 켰다. 커밋 전에 `git diff --stat`으로 크기 0인 파일이 없는지 본다.

### 2-3. 실패한 테스트 하나 — 1차 캐시

마지막 hello 테스트가 처음엔 `payload`에 `"v": 2`(공백 있음)가 있는지 봤다. jsonb는 꺼낼 때 공백을 넣어 정규화한다는 가정이었는데, 결과는 `{"v":2}` 그대로였다. 테스트가 `@Transactional` 안이라 조회 결과가 DB를 거치지 않고 **영속성 컨텍스트(1차 캐시)에 있던 그 객체**로 돌아왔기 때문이다. 이 테스트가 보려는 건 "가장 최근 것을 고르나"였으니 **id 비교**로 바꿨다. jsonb 저장 자체는 두 번째 테스트가 네이티브 쿼리(`payload->>'exceptionType'`)로 DB에서 직접 확인한다. 테스트가 확인하려는 것 하나만 보게 만들어야 한다는 걸 배웠다.

### 2-4. HealthController가 model/entity에 들어갔다

controller로 옮긴다는 커밋(`3affcf8`)이 실제로는 `model/entity/HealthController.java`로 옮겨졌다. 컴포넌트 스캔은 하위 패키지 전부라 동작은 하지만 D-088 위반이다. 노트를 쓰며 발견했고 다음 PR에서 `controller/`로 옮긴다.

### 2-5. PR이 main으로 열렸다 — 두 번

develop으로 열어야 할 PR이 main으로 열렸고 "Review required"로 막혔다(main은 승인 1명). 원인은 레포 **기본 브랜치가 main**이라 PR 만들 때 자동으로 main이 잡힌 것. 열린 PR은 제목 옆 **Edit → base 변경**으로 고칠 수 있고, 이미 새로 열었으면 잘못 연 쪽을 Close(브랜치는 지우지 않음). Settings → General → Default branch를 develop으로 바꿔 재발을 막는다. "Checking for the ability to merge automatically…"가 안 끝나면 새로고침.

### 2-6. 줄 끝이 전부 바뀐 것처럼 보일 때

VM 쪽에서 `git diff`를 보면 build.gradle이 통째로 바뀐 것처럼 나왔다. 작업 폴더는 CRLF, 저장소는 LF. Windows git의 autocrlf가 커밋할 때 LF로 맞추므로 실제로는 2줄 추가였다. `git diff --ignore-cr-at-eol`로 진짜 변경만 볼 수 있다.

## 3. 더 나아가 알면 좋은 것

### 3-1. 엔티티에 관계(@ManyToOne)를 안 건 이유

`tenantId`, `groupId`를 객체가 아니라 `Long`으로 들었다. 팀 경계(RLS)는 DB가 `tenant_id` 컬럼으로 강제하고, 엔티티끼리 연관을 걸면 지연 로딩·N+1 같은 신경 쓸 거리만 늘어난다. 지금 필요한 조회는 전부 id로 충분하다.

### 3-2. 다음에 볼 키워드

- 영속성 컨텍스트와 `saveAndFlush` — flush는 SQL을 보내지만 1차 캐시는 그대로 남는다
- `@DynamicPropertySource` — 컨테이너 포트처럼 실행해야 아는 값을 설정에 넣는 방법
- `ON CONFLICT (tenant_id, fingerprint) DO UPDATE` — 6단계 그룹 upsert

## 관련 노트

[[AiOps 06 - V1 테이블과 서버 설정]] · [[AiOps 08 - 하트비트와 Starter 빌드 정리]]
