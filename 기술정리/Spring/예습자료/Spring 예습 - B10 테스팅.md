---
출처: 자동수집(Claude)
작성일: 2026-09-25
성격: 예습자료
tags: [학습, spring]
---

# Spring 예습 - B10 테스팅

> 예습자료 — 자동 생성, 사용자 미검증. 결론이 아니라 **읽을 범위의 지도**다.
> 기준 버전: Spring Boot 4.1.1

## 이 모듈이 다루는 범위

B10은 공식 문서의 **Reference → Testing** 챕터 하나가 통째로 대응한다. 앞선 모듈들과 달리 이 챕터는 한 페이지가 아니라 **여섯 페이지로 갈라져 있고**, 그중 「Testing Spring Boot Applications」 한 페이지가 챕터 분량의 대부분을 차지한다.

| 페이지 | 문서가 서 있는 자리 |
| --- | --- |
| **Test Modules** | 기능별로 갈라진 `-test` 모듈 목록. 어떤 슬라이스가 어느 모듈에서 오는지의 표 |
| **Test Scope Dependencies** | `spring-boot-starter-test` 하나에 무엇이 딸려 오는지 |
| **Testing Spring Applications** | 스프링 일반의 테스트(단위 vs 통합). 대부분 Spring Framework 문서로 넘긴다 |
| **Testing Spring Boot Applications** | 챕터의 몸통. `@SpringBootTest`와 **슬라이스 테스트** 전체 |
| **Testcontainers** | 실제 도커 컨테이너를 띄워 붙이는 갈래 |
| **Test Utilities** | 부트가 끼워 주는 작은 도구 4개 |

핵심 성격: 이 모듈은 "테스트 코드를 어떻게 잘 쓰는가"(그건 JUnit·AssertJ·Mockito 각자의 문서다)가 아니라, **부트가 테스트를 위해 애플리케이션 컨텍스트를 어떻게 잘라서 띄워 주는가**를 다룬다. B03(생명주기)·B06(자동설정)에서 본 "컨텍스트가 뜨는 방식"이 여기서 **테스트용으로 축소된 형태**로 다시 나온다.

- 원문: https://docs.spring.io/spring-boot/reference/testing/index.html

## 목차 지도

### 1. Test Modules

- **Test Modules** — 기능별 `-test` 모듈 24개를 표로 나열하는 자리. `spring-boot-webmvc-test`(`@WebMvcTest`)·`spring-boot-data-jpa-test`(`@DataJpaTest`)처럼 **모듈 하나 ↔ 슬라이스 애노테이션 하나**가 짝지어져 있다

### 2. Test Scope Dependencies

- **Test Scope Dependencies** — `spring-boot-starter-test`가 test 스코프로 끌고 오는 라이브러리 목록: JUnit, Spring Test & Spring Boot Test, AssertJ(유창한 단언), Hamcrest(매처), Mockito(모킹), JSONassert(JSON 단언), JsonPath(JSON용 XPath), Awaitility(비동기 테스트)
  - JUnit 4 테스트는 `junit-vintage-engine`으로 돌린다는 단서도 이 자리

### 3. Testing Spring Applications

- **Testing Spring Applications** — DI의 이점으로 단위 테스트가 쉬워진다는 것, `new`로 객체를 만들어 스프링 없이 테스트하는 쪽과 `ApplicationContext`를 띄우는 통합 테스트 쪽을 가르는 자리. 상세는 `spring-test` 모듈(프레임워크 문서)로 넘긴다

### 4. Testing Spring Boot Applications — 챕터의 몸통

#### 4-1. `@SpringBootTest` 자체

- **Detecting Web Application Type** — MVC냐 WebFlux냐를 부트가 어떻게 판정하는지와 `spring.main.web-application-type`
- **Detecting Test Configuration** — `@SpringBootApplication`·`@SpringBootConfiguration`을 찾아 올라가는 탐색 규칙, `@TestConfiguration`
- **Using the Test Configuration Main Method** — `main`으로 컨텍스트를 만들게 하는 `useMainMethod`(`ALWAYS`/`WHEN_AVAILABLE`)
- **Excluding Test Configuration** — 테스트 설정이 컴포넌트 스캔에 딸려 들어가지 않게 두는 방법(최상위 `@TestConfiguration` + `@Import`)
- **Using Application Arguments** — `args` 속성과 `ApplicationArguments` 주입

#### 4-2. 웹을 어떻게 띄울 것인가 — 두 갈래

- **Testing With a Mock Environment** — 서버를 띄우지 않고 목 환경에서 엔드포인트를 때리는 쪽. `@AutoConfigureMockMvc`·`@AutoConfigureRestTestClient`·`@AutoConfigureWebTestClient`, `MockMvc`·`MockMvcTester`·`RestTestClient`·`WebTestClient`
- **Testing With a Running Server** — 실제 서버를 띄우는 쪽. `webEnvironment=RANDOM_PORT`, `@LocalServerPort`, `TestRestTemplate`
- **Customizing RestTestClient** / **Customizing WebTestClient** — `RestTestClientBuilderCustomizer`·`WebTestClientBuilderCustomizer` 빈으로 손보는 자리

#### 4-3. 관측 계열 — 기본은 꺼져 있다

- **Using JMX** — `spring.jmx.enabled=true`와 `@DirtiesContext`
- **Using Observations** — `ObservationRegistry` 자동설정, `@AutoConfigureTracing`·`@AutoConfigureMetrics`
- **Using Metrics** — `@SpringBootTest`에서 미터 레지스트리가 기본으로 자동설정되지 **않는다**는 것과 켜는 방법
- **Using Tracing** — 같은 구조. `@AutoConfigureTracing`·`@ConditionalOnEnabledTracingExport`

#### 4-4. 빈을 바꿔치기

- **Mocking and Spying Beans** — `@MockitoBean`·`@MockitoSpyBean`으로 컨텍스트 안의 빈을 목·스파이로 교체하는 자리

#### 4-5. 슬라이스 테스트 — 이 챕터의 중심

- **Auto-configured Tests** — `@…Test`(슬라이스)와 `@AutoConfigure…`(추가 자동설정)의 관계를 여는 자리
- **Auto-configured JSON Tests** — `@JsonTest`. Jackson `JsonMapper`·`Gson`·`Jsonb`와 `JacksonTester`·`GsonTester`·`JsonbTester`·`BasicJsonTester`
- **Auto-configured Spring MVC Tests** — `@WebMvcTest`. MVC 인프라만 올리고 스캔 대상을 `@Controller`·`@ControllerAdvice`·`Converter`·`Filter`·`HandlerInterceptor`·`WebMvcConfigurer`·`HandlerMethodArgumentResolver` 등으로 **제한**한다
- **Auto-configured Spring WebFlux Tests** — `@WebFluxTest` + `WebTestClient`
- **Auto-configured Spring GraphQL Tests** — `@GraphQlTest` + `GraphQlTester`
- **Auto-configured Data JPA Tests** — `@DataJpaTest`. 인메모리 DB와 `TestEntityManager`
- **Auto-configured JDBC Tests** — `@JdbcTest` + `JdbcTemplate`
- **Auto-configured Data JDBC Tests** — `@DataJdbcTest` + `JdbcAggregateTemplate`
- **Auto-configured jOOQ Tests** — `@JooqTest` + `DSLContext`
- **Auto-configured Data MongoDB / Neo4j / Redis / LDAP Tests** — `@DataMongoTest`·`@DataNeo4jTest`·`@DataRedisTest`·`@DataLdapTest`
- **Auto-configured REST Clients Tests** — `@RestClientTest`. `RestClient.Builder`·`RestTemplate`로 만든 **클라이언트 쪽**을 서버 없이 테스트
- **Auto-configured Web Services Client Tests** — `@WebServiceClientTest` + `WebServiceTemplate`

#### 4-6. 슬라이스를 쓸 때 걸리는 것

- **User Configuration and Slicing** — 메인 애플리케이션 클래스에 특정 영역 설정을 얹으면 슬라이스가 오염된다는 자리
- **Using Spock** — Spock 프레임워크 지원
- **Test Context Caching** — 스프링 테스트 프레임워크가 컨텍스트를 테스트 사이에 **캐시**한다는 자리

### 5. Testcontainers

- **Testcontainers** — 도커 컨테이너를 테스트에 붙이는 갈래를 여는 자리
- **Using Spring Beans** — `@TestConfiguration` + `@Bean`으로 컨테이너를 스프링 빈으로 두기
- **Using the JUnit Extension** — Testcontainers 쪽 `@Testcontainers`·`@Container`로 생명주기를 맡기기
- **Importing Container Configuration Interfaces** — 컨테이너를 인터페이스의 정적 필드로 선언하고 `@ImportTestcontainers`로 재사용
- **Lifecycle of Managed Containers** — 컨테이너를 **누가**(Testcontainers냐 부트냐) 띄우고 내리는지가 방식에 따라 갈린다는 자리
- **Service Connections** — `@ServiceConnection`으로 컨테이너의 접속 정보를 자동으로 `ConnectionDetails`로 만들어 주는 자리
- **SSL with Service Connections** — `@Ssl`·`@JksKeyStore`·`@JksTrustStore`·`@PemKeyStore`·`@PemTrustStore`
- **Dynamic Properties** — 위 대신 `@DynamicPropertySource`·`DynamicPropertyRegistry`로 직접 프로퍼티를 주입하는 방식

### 6. Test Utilities

- **ConfigDataApplicationContextInitializer** — `@SpringBootTest` 없이도 `application.properties`를 읽게 하는 초기화자
- **TestPropertyValues** — `ConfigurableEnvironment`에 프로퍼티를 빠르게 얹는 유틸
- **OutputCaptureExtension** — `System.out`·`System.err`를 잡아 `CapturedOutput`으로 단언하게 하는 JUnit 확장
- **TestRestTemplate** — 통합 테스트용으로 리다이렉트·에러 처리가 다르게 동작하는 `RestTemplate` 대체물

### 7. (별도 페이지) How-to → Testing

- **Testing With Spring Security** — `@WithMockUser`로 특정 사용자·권한으로 테스트를 돌리는 자리
- **Structure `@Configuration` Classes for Inclusion in Slice Tests** — 슬라이스에 설정 클래스가 들어오고 빠지게 배치하는 방법

## 핵심 용어

| 용어 | 한 줄 |
| --- | --- |
| `spring-boot-starter-test` | 테스트에 필요한 라이브러리 묶음을 한 번에 끌고 오는 스타터 |
| AssertJ / Hamcrest | 단언을 적는 두 라이브러리. 유창한 체이닝 쪽과 매처 객체 쪽 |
| Mockito | 가짜 객체(목)를 만들어 협력 객체를 대신하게 하는 프레임워크 |
| JSONassert / JsonPath | JSON 응답을 비교하는 단언과, JSON 안을 경로로 짚는 표현식 |
| Awaitility | "언젠가 이렇게 된다"를 기다리며 검사하는 비동기 테스트 라이브러리 |
| `@SpringBootTest` | 애플리케이션 컨텍스트 전체를 테스트용으로 띄우는 애노테이션 |
| `webEnvironment` | 테스트에서 웹 환경을 어떻게 둘지(목 / 실제 서버 / 없음) 고르는 속성 |
| `@TestConfiguration` | 테스트에서만 쓰는 추가 설정. 컴포넌트 스캔에 자동으로 딸려 오지 않게 두는 장치 |
| `@LocalServerPort` | 랜덤 포트로 뜬 실제 서버의 포트 번호를 주입받는 애노테이션 |
| `MockMvc` / `MockMvcTester` | 서버를 띄우지 않고 MVC 처리 흐름을 그대로 태워 보는 도구 |
| `TestRestTemplate` / `RestTestClient` / `WebTestClient` | 실제 서버 또는 목 환경에 요청을 보내는 세 갈래 클라이언트 |
| **슬라이스 테스트** | 컨텍스트 전체가 아니라 한 층(MVC·JPA·JSON…)만 잘라서 띄우는 테스트 방식 |
| `@WebMvcTest` | 컨트롤러 층만 올리는 슬라이스 |
| `@DataJpaTest` | JPA 리포지토리·엔티티만 올리는 슬라이스 |
| `TestEntityManager` | `@DataJpaTest`가 끼워 주는, 테스트용으로 다듬은 `EntityManager` |
| `@JsonTest` | 직렬화·역직렬화만 떼어 보는 슬라이스 |
| `@RestClientTest` | 서버가 아니라 **클라이언트 코드**를 서버 없이 테스트하는 슬라이스 |
| `@AutoConfigure…` | 슬라이스에 특정 자동설정을 얹는 애노테이션 계열 |
| `@MockitoBean` / `@MockitoSpyBean` | 컨텍스트 안의 빈을 목 / 스파이로 갈아 끼우는 애노테이션 |
| 테스트 컨텍스트 캐싱 | 같은 설정의 컨텍스트를 테스트 사이에 재사용하는 스프링 테스트의 최적화 |
| `@DirtiesContext` | 캐시된 컨텍스트를 버리게 표시하는 애노테이션 |
| Testcontainers | 테스트 중에 실제 도커 컨테이너로 DB·미들웨어를 띄우는 라이브러리 |
| `@ServiceConnection` | 컨테이너의 접속 정보를 스프링 설정으로 자동 연결해 주는 애노테이션 |
| `ConnectionDetails` | 접속 정보를 프로퍼티 대신 객체로 표현하는 부트의 추상 |
| `@DynamicPropertySource` | 실행 시점에 정해지는 값(포트 등)을 `Environment`에 밀어 넣는 통로 |
| `OutputCaptureExtension` / `CapturedOutput` | 표준 출력·에러를 잡아 단언 대상으로 만드는 확장 |
| `TestPropertyValues` | 테스트에서 프로퍼티를 프로그래밍으로 얹는 유틸 |
| `@WithMockUser` | 시큐리티가 켜진 상태에서 특정 사용자로 요청을 흉내 내는 애노테이션 |

## 처음 보는 개념

학습 지도에서 B10은 **⭐⭐ 신규 — 노트에 없음**으로 표시돼 있다. `Spring/` 구역 day01~day08 어디에도 테스트 관련 노트가 없다. 그래서 이 모듈은 대조가 아니라 **처음부터**다. 다만 앞선 예습 모듈들과 맞물리는 자리가 뚜렷하다.

- **"컨텍스트를 자른다"는 발상 자체.** B03에서 `SpringApplication`이 컨텍스트를 통째로 띄우는 순서를 봤다면, 슬라이스 테스트는 그 컨텍스트를 **일부만** 띄운다. 무엇을 기준으로 자르는지(스캔 대상 애노테이션 종류를 제한)가 B06의 자동설정 조건과 같은 층에 있다.
- **자동설정이 테스트에서 다르게 동작한다.** 메트릭·트레이싱이 `@SpringBootTest`에서 기본으로 켜지지 않는다는 서술은, 자동설정이 "환경에 따라 다르게 판정된다"는 B06의 이야기가 테스트 쪽에서 나타난 것이다.
- **B09와 직접 이어진다.** `@DataJpaTest`가 인메모리 DB를 쓴다는 것은 B09의 Embedded Database Support 절과 같은 기계다. Testcontainers는 그 반대편 — 실제 DB를 띄우는 쪽 — 이므로 B09에서 본 `DataSource` 자동설정이 어디서 갈리는지가 여기서 드러난다.
- **B07·B08과도 맞물린다.** `@WebMvcTest`의 스캔 대상 목록(`ControllerAdvice`·`Filter`·`HandlerInterceptor`·`WebMvcConfigurer`)은 B07에서 본 MVC 자동설정 구성요소와 그대로 겹친다. `@WithMockUser`는 B08의 시큐리티가 테스트에서 어떻게 비켜서는지의 자리다.
- **테스트 컨텍스트 캐싱.** 테스트가 느려지거나 이상하게 서로 간섭하는 현상의 근원이 이 절에 있다. 설정 조합이 하나라도 다르면 컨텍스트가 새로 뜬다는 규칙을 아직 본 적이 없을 것이다.
- **모듈이 잘게 쪼개져 있다.** 4.x에서 `-test` 모듈이 24개로 갈라져 있다는 것은, 슬라이스 하나를 쓰려면 그 모듈이 클래스패스에 있어야 한다는 뜻이다. "애노테이션은 아는데 안 먹힌다"의 흔한 원인이 여기다.

## 학습 세션에서 확인할 것

- [ ] `@SpringBootTest` 하나와 슬라이스 애노테이션 하나는 **무엇이 다른가** — 컨텍스트에 올라오는 빈의 범위는 누가, 어떤 기준으로 정하는가
- [ ] 목 환경(`MockMvc`)과 실제 서버(`RANDOM_PORT` + `TestRestTemplate`)는 각각 무엇까지 검증하고 무엇을 검증하지 못하는가 — 필터·서블릿 컨테이너는 어느 쪽에 들어오는가
- [ ] `@MockitoBean`으로 빈을 갈아 끼우면 **테스트 컨텍스트 캐싱**은 어떻게 되는가 — 테스트가 느려지는 조건은 무엇인가
- [ ] `@DataJpaTest`의 인메모리 DB와 Testcontainers의 실제 DB는 각각 무엇을 얻고 무엇을 놓치는가 — `@ServiceConnection`은 B09의 `DataSource` 자동설정 어디에 끼어드는가
- [ ] 메트릭·트레이싱이 테스트에서 기본으로 꺼져 있는 이유는 무엇이겠는가 — B06의 조건 애노테이션으로 설명하면 어떻게 되는가
- [ ] 시큐리티를 켜 둔 상태에서 `@WebMvcTest`를 돌리면 무슨 일이 일어나는가 — `@WithMockUser`는 그 지점의 무엇을 대신하는가

## 원문 링크

- https://docs.spring.io/spring-boot/reference/testing/index.html
- https://docs.spring.io/spring-boot/reference/testing/test-modules.html
- https://docs.spring.io/spring-boot/reference/testing/test-scope-dependencies.html
- https://docs.spring.io/spring-boot/reference/testing/spring-applications.html
- https://docs.spring.io/spring-boot/reference/testing/spring-boot-applications.html
- https://docs.spring.io/spring-boot/reference/testing/testcontainers.html
- https://docs.spring.io/spring-boot/reference/testing/test-utilities.html
- https://docs.spring.io/spring-boot/how-to/testing.html
