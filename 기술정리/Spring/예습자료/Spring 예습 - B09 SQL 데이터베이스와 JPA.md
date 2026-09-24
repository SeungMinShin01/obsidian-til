---
출처: 자동수집(Claude)
작성일: 2026-09-24
성격: 예습자료
tags: [학습, spring]
---

# Spring 예습 - B09 SQL 데이터베이스와 JPA

> 예습자료 — 자동 생성, 사용자 미검증. 결론이 아니라 **읽을 범위의 지도**다.
> 기준 버전: Spring Boot 4.1.1

## 이 모듈이 다루는 범위

B09는 공식 문서의 **Reference → Data → SQL Databases** 한 페이지가 몸통이고, 초기화 쪽은 **How-to → Database Initialization** 페이지가 따로 받는다. 학습 지도에 "분량 많음, 쪼갤 것"이라 적혀 있는 이유가 목차를 펼쳐 보면 드러난다 — 이 한 페이지 안에 **접근 방식이 다섯 갈래**로 들어 있다.

| 덩어리 | 문서가 서 있는 자리 |
| --- | --- |
| **DataSource** | 연결 자체. 내장 DB, 운영 DB, 커넥션 풀, JNDI, 지연 연결 프록시 |
| **JdbcTemplate / JdbcClient** | SQL을 직접 적는 갈래. 부트가 템플릿을 대신 등록해 주는 자리 |
| **JPA and Spring Data JPA** | 엔티티·리포지토리 갈래. 수업에서 다룬 자리 |
| **Spring Data JDBC / jOOQ** | JPA를 쓰지 않는 두 대안 |
| **R2DBC** | 블로킹하지 않는 리액티브 갈래 |

핵심 성격: 이 모듈은 "JPA를 어떻게 쓰는가"가 아니라 **부트가 데이터 접근 층을 어떻게 차려 주고, 어떤 갈래를 고를 수 있게 두는가**를 다룬다. 수업(day04~day08)은 이 중 JPA 갈래 하나만 지나왔다.

- 원문: https://docs.spring.io/spring-boot/reference/data/sql.html
- 원문(초기화): https://docs.spring.io/spring-boot/how-to/data-initialization.html

## 목차 지도

### 1. DataSource 쪽 — 연결을 어떻게 얻는가

- **Configure a DataSource** — 자바 표준 `DataSource` 인터페이스로 DB 연결을 잡는다는 것을 여는 자리
- **Embedded Database Support** — H2·HSQL·Derby 같은 인메모리 DB를 개발 중에 자동으로 붙여 주는 동작
- **Connection to a Production Database** — 운영에서는 풀링 `DataSource`가 자동설정된다는 자리
- **DataSource Configuration** — `spring.datasource.*` 프로퍼티. 표준 옵션과 구현체별 옵션이 갈리는 지점
- **Supported Connection Pools** — 부트가 어떤 순서로 풀 구현을 고르는지(HikariCP 우선)와 `DataSourceBuilder`
- **Connection to a JNDI DataSource** — WAS가 들고 있는 `DataSource`를 `spring.datasource.jndi-name`으로 받아 오기
- **Lazy Connection Proxy** — `spring.datasource.connection-fetch=lazy`로 실제 커넥션 획득을 미루는 자리

### 2. SQL을 직접 적는 갈래

- **Using JdbcTemplate** — 자동설정된 `JdbcTemplate`·`NamedParameterJdbcTemplate`을 주입받아 쓰기, `spring.jdbc.template.*`
- **Using JdbcClient** — `NamedParameterJdbcTemplate`이 있으면 함께 올라오는 더 최신 유연 API

### 3. JPA and Spring Data JPA

- **도입** — Jakarta Persistence(JPA)와 Spring Data JPA를 구분해 소개하고, `spring-boot-starter-data-jpa`가 무엇을 끌고 오는지 나열하는 자리
- **Entity Classes** — `@Entity`·`@Embeddable`·`@MappedSuperclass`를 어디서 훑는지, `@EntityScan`으로 범위를 바꾸는 자리
- **Spring Data JPA Repositories** — `Repository`·`CrudRepository`를 상속한 인터페이스, 메소드 이름에서 쿼리를 만드는 규칙, `@Query`, 그리고 **부트스트랩 모드 세 가지**(default / deferred / lazy)
- **Spring Data Envers Repositories** — `RevisionRepository`로 변경 이력(리비전)을 추적하는 지원
- **Creating and Dropping JPA Databases** — `spring.jpa.hibernate.ddl-auto`로 DDL을 다루는 자리와 하이버네이트 프로퍼티 전달
- **Open EntityManager in View** — `OpenEntityManagerInViewInterceptor` 등록과 `spring.jpa.open-in-view`. 지연 로딩이 뷰 렌더링까지 살아 있게 두는 설정

### 4. JPA를 쓰지 않는 갈래

- **Spring Data JDBC** — 매핑을 훨씬 얇게 두고 SQL을 생성하는 리포지토리. `@Query`, AOT 처리 시 `JdbcDialect` 고려
- **Using H2's Web Console** — 브라우저로 H2를 들여다보는 콘솔. `spring.h2.console.enabled`·`path`
  - **Changing the H2 Console's Path** — 경로 바꾸기
  - **Accessing the H2 Console in a Secured Application** — 시큐리티가 켜졌을 때 CSRF·`X-Frame-Options` 때문에 막히는 자리와 `SecurityFilterChain` 설정
- **Using jOOQ** — 타입 안전한 SQL 빌더. Java 21+ 요구
  - **Code Generation** — DB 스키마에서 코드를 생성하는 `jooq-codegen-maven`
  - **Using DSLContext** — 자동설정된 `DSLContext`를 주입받아 쿼리를 조립
  - **jOOQ SQL Dialect** — `spring.jooq.sql-dialect` 자동 판정
  - **Customizing jOOQ** — `DefaultConfigurationCustomizer` 또는 `Configuration` 빈을 직접 두기

### 5. R2DBC — 리액티브 갈래

- **Using R2DBC** — 논블로킹 DB 접근. `spring.r2dbc.*`로 `ConnectionFactory` 구성
- **Embedded Database Support** — 리액티브 쪽 인메모리 DB 자동설정
- **Using DatabaseClient** — 자동설정된 `DatabaseClient`로 리액티브 쿼리
- **Spring Data R2DBC Repositories** — 리액티브 리포지토리 인터페이스

### 6. (별도 페이지) Database Initialization

- **Initialize a Database Using Hibernate** — `spring.jpa.hibernate.ddl-auto`와 `import.sql`
- **Initialize a Database Using Basic SQL Scripts** — `schema.sql`·`data.sql`, `spring.sql.init.*`(mode·locations·platform·continue-on-error)
- **Initialize a Spring Batch Database** — 배치 스키마 자동 초기화
- **Use a Higher-level Database Migration Tool** — 마이그레이션 도구로 올라가는 자리
  - **Execute Flyway Database Migrations on Startup** — Flyway 구성(`spring.flyway.locations`)
  - **Execute Liquibase Database Migrations on Startup** — Liquibase 구성(`spring.liquibase.change-log`·`enabled`)
  - **Use Flyway / Liquibase for Test-only Migrations** — 테스트 전용 마이그레이션·컨텍스트
- **Depend Upon an Initialized Database** — 초기화가 끝난 뒤에 떠야 하는 빈의 순서 문제
  - **Detect a Database Initializer** / **Detect a Bean That Depends On Database Initialization** — 부트가 그 순서를 어떻게 자동 판정하는지

## 핵심 용어

day04~day08에서 이미 다룬 `@Entity`·`@Id`·`@GeneratedValue`·`JpaRepository`·쿼리 메소드·`@Query`·`@Transactional`·`ddl-auto`·`data.sql`은 여기서 뺀다. 이 모듈에서 **처음** 또는 새 맥락으로 나오는 것만.

| 용어 | 한 줄 |
| --- | --- |
| `DataSource` | DB 연결을 얻는 자바 표준 인터페이스. 그 아래 어떤 구현이 오는지가 이 모듈의 첫 절 |
| 커넥션 풀 | 연결을 미리 만들어 두고 빌려 주는 구조 |
| HikariCP | 부트가 기본으로 고르는 커넥션 풀 구현 |
| `DataSourceBuilder` | 어떤 풀 구현으로 `DataSource`를 만들지 코드에서 정하는 빌더 |
| JNDI `DataSource` | 애플리케이션 서버가 들고 있는 `DataSource`를 이름으로 받아 쓰는 방식 |
| 지연 연결 프록시 | 실제로 SQL이 필요해질 때까지 커넥션 획득을 미루는 래퍼 |
| `JdbcTemplate` | SQL을 직접 적으면서 반복 코드(연결·예외·매핑)를 걷어 내는 스프링 클래스 |
| `NamedParameterJdbcTemplate` | `?` 대신 `:name`으로 파라미터를 적는 템플릿 |
| `JdbcClient` | 위 둘 위에 얹힌 더 최신의 유연한 JDBC API |
| Jakarta Persistence(JPA) / 하이버네이트 | 표준 명세와 그 구현체. 둘을 구분하는 것이 이 절의 전제 |
| `@EntityScan` | 엔티티를 훑을 패키지 범위를 기본값과 다르게 지정하는 것 |
| 리포지토리 부트스트랩 모드 | 리포지토리 초기화 시점을 default / deferred / lazy로 고르는 설정 |
| Spring Data Envers / `RevisionRepository` | 엔티티의 변경 이력을 리비전으로 추적하는 확장 |
| `spring.jpa.open-in-view` | 영속성 컨텍스트를 뷰 렌더링까지 열어 둘지 정하는 설정 |
| `OpenEntityManagerInViewInterceptor` | 위 동작을 실제로 수행하는 인터셉터 |
| Spring Data JDBC | JPA 없이(영속성 컨텍스트·지연 로딩 없이) SQL을 생성하는 리포지토리 갈래 |
| `JdbcDialect` | DB 종류별 차이를 담는 Spring Data JDBC 쪽 구성 |
| H2 웹 콘솔 | 브라우저에서 H2 DB를 들여다보는 화면 (`spring.h2.console.*`) |
| jOOQ / `DSLContext` | 타입 안전한 SQL 빌더와 그 진입점 |
| jOOQ 코드 생성 | DB 스키마에서 자바 코드를 뽑아내는 빌드 단계 |
| R2DBC / `ConnectionFactory` | 논블로킹 DB 접근 규격과 그 연결 공급자 |
| `DatabaseClient` | R2DBC 위의 리액티브 쿼리 클라이언트 |
| `spring.sql.init.*` | `schema.sql`·`data.sql` 실행을 제어하는 프로퍼티 묶음 |
| `spring.jpa.defer-datasource-initialization` | JPA가 표를 만든 **뒤에** 스크립트를 돌리도록 미루는 설정 |
| `import.sql` | 하이버네이트가 DDL 생성 직후 읽는 초기 데이터 파일 |
| Flyway / Liquibase | 스키마 변경을 버전으로 관리하는 마이그레이션 도구 |
| 초기화 순서 감지 | 어떤 빈이 "DB 초기화 후"에 떠야 하는지를 부트가 판정하는 장치 |

## 수업에서 안 다뤘을 만한 지점

학습 지도에서 B09는 **복습**(day04~day07과 대조, ⭐⭐)으로 표시돼 있다. day04~day08 노트를 읽어 보면 수업이 지나온 자리는 이렇다 — day04에서 `@Entity`·`@Table`·`@Id`·`@GeneratedValue`·`JpaRepository`와 서비스 계층·`Optional`·스타터 한 줄까지, day05에서 `@Column` 제약·`@MappedSuperclass`·`@EntityListeners`·`@EnableJpaAuditing` 감사 필드·DTO 변환·`data.sql` 시드·변경 감지와 `@Transactional`까지, day06에서 `@ManyToOne`·`@JoinColumn`·양방향과 순환참조·중간 엔티티로 푼 다대다까지, day07에서 FK 번호를 엔티티로 바꿔 저장하는 흐름과 `getReferenceById`·`existsById`까지, day08에서 쿼리 메소드 키워드·네이티브 쿼리·`@Query`·프로젝션까지다.

즉 수업은 **JPA 갈래 안쪽을 꽤 깊이** 갔다. 그래서 이 모듈의 대조 지점은 "JPA를 더 배우는 것"이 아니라 **그 갈래 바깥과 아래층**에 있다.

- **연결 층이 통째로 비어 있다.** day04~day08 어디에도 `DataSource`·커넥션 풀·HikariCP가 없다. `application.properties`에 URL을 적으면 되던 자리 밑에서 무엇이 풀을 고르고 연결을 빌려 주는지가 B09의 첫 절이다. 수업이 "DB를 갈라 두기"(day05 1-11, day06 1-8)로 여러 DB를 쓴 것도 이 층 위의 이야기다.
- **SQL을 직접 적는 갈래를 안 봤다.** day08에서 네이티브 쿼리로 SQL 문자열을 적긴 했지만, 그것은 리포지토리 위에 얹은 것이다. `JdbcTemplate`·`JdbcClient`는 **리포지토리 없이** SQL을 쓰는 별도 갈래이고 수업에 없다.
- **JPA 자체가 선택지 중 하나라는 것.** Spring Data JDBC·jOOQ·R2DBC 세 대안이 같은 페이지에 나란히 놓여 있다. 수업은 JPA만 지나왔으므로 "무엇을 포기하고 무엇을 얻어서 JPA가 아닌 쪽을 고르는가"라는 질문 자체가 새로 생긴다. 특히 Spring Data JDBC는 영속성 컨텍스트·지연 로딩이 없는 쪽인데, day05 3-1(영속성 컨텍스트)과 day06 2-1(즉시/지연 로딩)에서 배운 것이 여기서는 **없는 상태**가 기본이 된다.
- **`open-in-view`.** day05·day06에서 지연 로딩과 변환 시점, 순환참조를 다뤘지만 이 설정 이름은 나오지 않았다. 지연 로딩이 서비스 밖에서도 되던(또는 안 되던) 경험이 어느 설정의 결과였는지가 이 절에 있다.
- **`@EntityScan`과 엔티티 탐색 범위.** day04~day08은 패키지를 재편하며(day07 계층 분리) 실습했지만, 엔티티를 어디서 훑는지의 기본 규칙과 그것을 바꾸는 수단은 다루지 않았다.
- **리포지토리 부트스트랩 모드.** day08 1-4에서 "이름이 어긋난 쿼리 메소드는 서버가 뜰 때 걸린다"고 관찰했는데, 그 초기화 시점을 deferred·lazy로 미룰 수 있다는 것이 이 절이다. 관찰과 설정이 정확히 맞물리는 자리다.
- **초기화 도구의 층위.** day05 1-8·2-6에서 `data.sql`·`schema.sql`을 썼고 2-7에서 "초기화가 안 먹힐 때 보는 순서"까지 갔다. How-to 문서는 그 위에 `spring.sql.init.*`·`defer-datasource-initialization`·하이버네이트 `import.sql`, 그리고 **Flyway·Liquibase**라는 상위 층을 둔다. day05 3-3에서 "표를 코드가 만들게 두지 않는 쪽 — 마이그레이션 도구"로 이름만 언급하고 넘어간 자리가 여기다.
- **초기화와 빈 순서.** "DB가 준비된 뒤에 떠야 하는 빈"이라는 문제 자체가 수업에 없다.
- **H2 웹 콘솔과 시큐리티의 충돌.** B08(Spring Security)을 예습한 직후라 이어지는 자리다. 콘솔이 프레임·CSRF 때문에 막히는 이유와 푸는 방법이 문서에 절로 있다.
- **Envers 리비전 추적.** day05에서 `@CreatedDate`·`@LastModifiedDate`로 "언제 바뀌었나"까지 갔다면, Envers는 "무엇이 어떻게 바뀌었나"의 이력을 남기는 쪽이다. 감사 필드의 연장선에 있지만 수업에 없다.

즉 day04~day08이 "엔티티와 리포지토리로 표를 다루는 법"이었다면, B09는 **"그 아래에 무엇이 깔려 있고, 그 옆에 어떤 갈래가 더 있는가"**다. 대조의 목적은 JPA 복습이 아니라 **JPA를 선택지의 하나로 다시 보는 것**이다.

## 학습 세션에서 확인할 것

- [ ] `application.properties`에 URL·계정만 적었을 때, 그 밑에서 `DataSource`와 커넥션 풀은 누가 무슨 기준으로 고르는가 — B06의 조건 애노테이션과 이어서
- [ ] day08의 네이티브 쿼리와 `JdbcTemplate`/`JdbcClient`는 무엇이 다른가 — 리포지토리를 거치는 것과 거치지 않는 것의 경계는 어디인가
- [ ] Spring Data JDBC를 고르면 day05·day06에서 배운 것 중 **무엇이 사라지는가**(영속성 컨텍스트·변경 감지·지연 로딩) — 그것을 포기하고 얻는 것은 무엇인가
- [ ] `spring.jpa.open-in-view`가 켜져 있을 때와 꺼져 있을 때, day06의 지연 로딩·순환참조 실습은 어디서 갈리는가
- [ ] day05에서 쓰던 `data.sql`과 `ddl-auto`는 Flyway·Liquibase로 올라가는 순간 어느 역할을 넘기게 되는가 — `defer-datasource-initialization`이 필요해지는 상황은 무엇인가
- [ ] day08에서 본 "서버 뜰 때 쿼리 메소드 이름이 걸리는" 동작은 부트스트랩 모드를 deferred·lazy로 바꾸면 어떻게 달라지는가

## 원문 링크

- https://docs.spring.io/spring-boot/reference/data/sql.html
- https://docs.spring.io/spring-boot/how-to/data-initialization.html
