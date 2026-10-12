---
출처: 자동수집(Claude)
작성일: 2026-09-27
성격: 예습자료
tags: [학습, spring]
---

# Spring 예습 - B12 Actuator 엔드포인트·메트릭

> 예습자료 — 자동 생성, 사용자 미검증. 결론이 아니라 **읽을 범위의 지도**다.
> 기준 버전: Spring Boot 4.1.1

## 이 모듈이 다루는 범위

B12는 공식 문서의 **Reference → Production-ready Features 챕터 전체**에 대응한다. 앞선 모듈들이 "애플리케이션을 어떻게 만드는가"였다면, 이 챕터는 **띄운 뒤에 밖에서 안을 들여다보는 장치**를 모아 둔 자리다. 문서 스스로 "운영에 밀어 넣은 애플리케이션을 감시·관리하도록 돕는 기능들"이라고 여는 것부터가 성격을 말한다.

챕터는 페이지 12개로 갈라지며, 크게 세 덩어리로 읽힌다.

| 덩어리 | 페이지 | 문서가 서 있는 자리 |
| --- | --- | --- |
| **엔드포인트** | Enabling · Endpoints · Monitoring over HTTP · Monitoring over JMX | 애플리케이션 상태를 **꺼내 볼 창구**를 만들고, 그 창구를 어디에 열고 누구에게 허용할지 |
| **관측 가능성** | Observability · Metrics · Tracing · Loggers | 숫자(메트릭)·경로(트레이스)·기록(로그) 세 축으로 **내부 상태를 밖으로 내보내는** 파이프 |
| **그 외 운영 장치** | Auditing · Recording HTTP Exchanges · Process Monitoring · Cloud Foundry | 감사 이벤트, 요청·응답 기록, PID·포트 파일, 플랫폼 통합 |

앞 모듈과의 연결점이 많다. `management.*` 프로퍼티 계열은 B04(외부 설정)에서 본 바인딩 규칙을 그대로 따르고, 엔드포인트 보안은 B08(시큐리티)의 `SecurityFilterChain`을 다시 쓰고, HTTP 클라이언트 메트릭이 계측하는 대상은 B11에서 만든 `RestClient`·`WebClient`이고, 캐시·`DataSource`·Hibernate 메트릭은 B09·B11의 그 빈들이다. **B12는 새 기능을 배우는 자리라기보다, 앞서 만든 것들을 밖에서 관찰하는 층을 얹는 자리로 보인다.**

- 원문(챕터): https://docs.spring.io/spring-boot/reference/actuator/index.html

## 목차 지도

### 1. Enabling Production-ready Features

- **Enabling** — `spring-boot-starter-actuator` 의존성 하나가 이 챕터 전체의 입구라는 것만 말하는 짧은 페이지. Maven·Gradle 두 갈래 표기. "actuator(액추에이터)"라는 말이 기계 부품 용어에서 왔다는 설명도 여기에 있다

### 2. Endpoints — 창구의 규격

- **Endpoints** — 내장 엔드포인트 목록. 기술 중립 엔드포인트(`health`·`info`·`beans`·`env`·`configprops`·`conditions`·`loggers`·`metrics`·`mappings`·`threaddump`·`startup`·`shutdown`·`caches`·`scheduledtasks`·`sessions`·`auditevents`·`httpexchanges`·`flyway`·`liquibase`·`quartz`·`integrationgraph`)과 웹 전용(`heapdump`·`logfile`·`prometheus`)이 나뉜다
- **Controlling Access to Endpoints** — 엔드포인트별 **접근 수준**(`unrestricted`/`read-only`/`none`)을 정하는 자리. `management.endpoint.<id>.access`·`management.endpoints.access.default`
  - **Limiting Access** — `management.endpoints.access.max-permitted`로 상한선을 걸어, 개별 설정이 그보다 위로 못 가게 하는 장치
- **Exposing Endpoints** — 접근 허용과 **별개로**, HTTP·JMX 각 통로에 무엇을 내놓을지 고르는 자리. `management.endpoints.web.exposure.include`/`exclude`, 와일드카드 `*`
- **Security** — 시큐리티가 클래스패스에 있을 때의 기본 동작과, `EndpointRequest.toAnyEndpoint()`로 엔드포인트만 겨냥한 `SecurityFilterChain`을 따로 두는 예시
  - **Cross Site Request Forgery Protection** — 엔드포인트에 대한 CSRF 기본값
- **Configuring Endpoints** — 응답 캐싱. `management.endpoint.<id>.cache.time-to-live`
- **Sanitize Sensitive Values** — 비밀값을 가리는 규칙. `show-values`의 `never`/`always`/`when-authorized`와 `roles`
- **Hypermedia for Actuator Web Endpoints** — `/actuator` 루트가 엔드포인트 목록을 링크로 내주는 발견 페이지. `management.endpoints.web.discovery.enabled`
- **CORS Support** — 브라우저 UI가 엔드포인트를 부를 때의 허용 출처·메서드
- **JSON** — 엔드포인트 응답 직렬화에 **애플리케이션과 같은 `JsonMapper`를 쓸지, 격리된 것을 쓸지**. `management.endpoints.jackson.isolated-json-mapper`
- **Implementing Custom Endpoints** — 직접 엔드포인트를 만드는 쪽. `@Endpoint`와 `@ReadOperation`·`@WriteOperation`·`@DeleteOperation`
  - **Receiving Input** / **Input Type Conversion** — 요청 본문에서 파라미터를 받고 형을 바꾸는 규칙 (`@EndpointConverter`)
  - **Custom Web Endpoints** — 웹 전용 확장(`@WebEndpoint`·`@EndpointWebExtension`)
    - **Web Endpoint Request Predicates** — 경로(`@Selector`)·HTTP 메서드·consumes·produces가 **오퍼레이션 종류에서 자동으로 유도된다**는 규약
    - **Web Endpoint Response Status** / **Range Requests** / **Security** — 상태 코드 결정, 범위 요청(힙덤프 같은 큰 응답), 엔드포인트 단위 보안
- **Health Information** — `health` 엔드포인트가 따로 큰 절을 갖는다. 상세 노출 수준(`show-details`·`show-components`·`roles`)
  - **Auto-configured HealthIndicators** — 자동으로 붙는 지표 목록(DB·디스크·Redis·메일 등)과 `management.health.<key>.enabled`로 끄는 법
  - **Writing Custom HealthIndicators** — `HealthIndicator`를 구현해 `Health.up()`/`down().withDetail(...)`을 돌려주기. 커스텀 상태와 `status.order`·`status.http-mapping`
  - **Reactive Health Indicators** — 리액티브 쪽 대응물

### 3. Monitoring and Management Over HTTP

- **Monitoring and Management Over HTTP** — 웹 애플리케이션이면 엔드포인트가 `/actuator/{id}` 규약으로 자동 노출된다는 기본. MVC·WebFlux·Jersey 세 갈래 지원
- **Customizing the Management Endpoint Paths** — 접두사(`base-path`)와 개별 경로(`path-mapping`) 바꾸기. base-path가 `server.servlet.context-path`에 **상대적**이라는 단서
- **Customizing the Management Server Port** — `management.server.port`로 **운영 엔드포인트를 다른 포트에** 내놓기
- **Configuring Management-specific SSL** — 관리 서버에 별도 인증서를 쓰는 자리
- **Customizing the Management Server Address** — `management.server.address`로 내부망 주소에만 바인딩하기
- **Disabling HTTP Endpoints** — `management.server.port=-1` 등으로 HTTP 노출을 끊기

### 4. Monitoring and Management over JMX

- **JMX** — `spring.jmx.enabled=true`로 켜는 별도 통로. `mbeanServer` 빈, `@ManagedResource`·`@ManagedAttribute`·`@ManagedOperation`, `spring.jmx.unique-names`, `management.endpoints.jmx.domain`. **기본은 꺼져 있다**

### 5. Observability — 세 기둥의 공통 층

- **Observability** — 관측 가능성을 로그·메트릭·트레이스 **세 기둥**으로 놓고, 부트가 그중 메트릭·트레이스를 **Micrometer Observation** 하나로 묶어 다룬다는 것을 여는 자리
  - `ObservationRegistry`를 주입받아 직접 관측을 만들기. **저카디널리티 태그는 메트릭과 트레이스로, 고카디널리티 태그는 트레이스에만** 간다는 구분
  - 자동 등록되는 확장점: `ObservationPredicate`·`GlobalObservationConvention`·`ObservationFilter`·`ObservationHandler`
  - **Context Propagation** — 리액티브 파이프라인·비동기 실행기에서 ThreadLocal 값을 넘기기 (`spring.reactor.context-propagation`, `ContextPropagatingTaskDecorator`)
  - **Common Tags** — `management.observations.key-values.*`로 모든 관측에 공통 차원 붙이기
  - **Preventing Observations** — 이름 접두사로 끄기, `ObservationPredicate` 구현
  - **Micrometer Annotations** — `@Observed`·`@Timed`·`@Counted`·`@MeterTag`·`@NewSpan` 스캔을 켜는 스위치와 aspectjweaver 요구
  - **OpenTelemetry Support** — `OpenTelemetry` 빈 자동설정, `management.opentelemetry.*`, **OTel SDK 환경변수(`OTEL_*`)를 부트 프로퍼티로 매핑**하는 표
  - **Metrics with OpenTelemetry** — 메트릭은 OTel SDK가 아니라 **Micrometer가 담당하고 OTLP로만 내보낸다**는 경계선
  - **R2DBC Observability** — `r2dbc-proxy` 의존성으로 켜지는 쪽

### 6. Metrics

- **Metrics** — Micrometer가 **17개 모니터링 시스템**(Prometheus·Datadog·Dynatrace·OTLP·StatsD·JMX·Graphite·Influx·New Relic·Stackdriver·Atlas·Elastic·Humio·KairosDB·AppOptics·Ganglia·Simple)의 파사드라는 것
- **Getting Started** — 합성(composite) `MeterRegistry` 자동설정, `MeterRegistryCustomizer`로 공통 태그 붙이기, 특정 레지스트리 끄기
- **Supported Monitoring Systems** — 시스템별 절. 전부 `management.<system>.metrics.export.*` 라는 **같은 프로퍼티 모양**을 반복한다. Prometheus는 `/actuator/prometheus` 스크레이프와 Pushgateway, Simple은 다른 레지스트리가 없을 때의 **폴백**
- **Supported Metrics and Meters** — 부트가 알아서 계측해 주는 것들의 목록. 각 절의 형식이 같다(무엇이 있으면 붙는지 / 미터 접두사 / 태그)
  - **JVM** (`jvm.`) · **System** (`system.`·`process.`·`disk.`) · **Application Startup** (`application.started.time`·`application.ready.time`) · **Logger** (`logback.events.`)
  - **Task Execution and Scheduling** — `ThreadPoolTaskExecutor`·`ThreadPoolTaskScheduler` 빈
  - **Spring MVC / WebFlux / Jersey** — 서버 요청 (`http.server.requests`), `ServerRequestObservationConvention`으로 태그 바꾸기
  - **HTTP Client** — `RestTemplate`·`RestClient`·`WebClient` (`http.client.requests`) — **자동설정된 빌더로 만든 것만** 계측된다
  - **Tomcat** (`tomcat.`, `server.tomcat.mbeanregistry.enabled` 요구) · **Cache** (`cache.`) · **DataSource** (`jdbc.connections.`·`hikaricp`) · **Hibernate** (`hibernate.generate_statistics` 요구) · **Spring Data Repository** (`spring.data.repository.invocations`) · **SSL Bundle** (`ssl.chain.expiry`) · **RabbitMQ · Kafka · MongoDB · JMS · Spring Integration · Batch · GraphQL**

### 7. Tracing

- **Tracing** — Micrometer Tracing이 트레이서 라이브러리의 파사드이고, 부트가 지원하는 것은 **OpenTelemetry+OTLP**와 **OpenZipkin Brave+Zipkin** 두 갈래라는 것
- **로그 상관 ID** — `traceId`·`spanId`가 MDC로 들어가 로그 줄에 붙는다. `logging.pattern.correlation`
- **Propagating Traces** — 자동설정된 `RestTemplateBuilder`·`RestClient.Builder`·`WebClient.Builder`를 거친 호출만 트레이스를 이어 보낸다
- **Sampling** — `management.tracing.sampling.probability` **기본 10%**, 샘플러 종류(`always-on`/`always-off`/`trace-id-ratio`/`parent-based-trace-id-ratio`)
- **Creating Custom Spans** — 스팬을 직접 만들지 않고 `Observation`으로 만든다는 방향
- **Baggage** — 트레이스에 실려 다니는 키·값. `remote-fields`(HTTP 헤더로)와 `correlation.fields`(MDC로)
- **Tracer Implementations** — 스타터 두 개(`spring-boot-starter-opentelemetry`·`spring-boot-starter-zipkin`)와 각자의 export 프로퍼티, OTel 스팬 한도(`limits.max-attributes` 등)
- **Testing** — `@SpringBootTest`에서는 트레이싱이 **자동설정되지 않는다**는 단서 (B10과 이어지는 지점)

### 8. Loggers

- **Loggers** — `loggers` 엔드포인트로 **런타임에 로그 레벨을 읽고 바꾸는** 자리. 설정된 레벨과 유효 레벨의 구분, `POST {"configuredLevel": "DEBUG"}`, `null`로 되돌리기
- **OpenTelemetry Logging** — 로그를 OTLP로 내보내기(`management.opentelemetry.logging.export.otlp.endpoint`), export 간격·레코드 한도
- **Appender 등록** — `OpenTelemetryAppender.install(...)`을 `InitializingBean`에서 부르는 방식. 부트가 기본으로 로그를 SDK에 물려 주지는 않는다

### 9~12. 그 외 운영 장치

- **Auditing** — 시큐리티가 있을 때 인증 성공·실패·접근 거부를 감사 이벤트로 남기는 자리. `AuditEventRepository` 빈이 있어야 켜지고, 기본 구현 `InMemoryAuditEventRepository`는 개발용. `AuditApplicationEvent` 발행으로 업무 이벤트도 태우기
- **Recording HTTP Exchanges** — `HttpExchangeRepository` 빈을 올려야 켜지고, `InMemoryHttpExchangeRepository`가 최근 100건을 들고 있다. 기록 항목 선택(`management.httpexchanges.recording.include`). 문서가 **운영에서는 Zipkin·OpenTelemetry를 쓰라고 명시**한다
- **Process Monitoring** — `ApplicationPidFileWriter`·`WebServerPortFileWriter`로 `application.pid`·`application.port` 파일을 남기기. **기본 비활성**이며 `spring.factories` 또는 `addListeners()`로 켠다
- **Cloud Foundry Support** — 플랫폼이 관리 엔드포인트를 알아보게 하는 통합 절

## 핵심 용어

| 용어 | 한 줄 |
| --- | --- |
| Actuator | 운영 중 애플리케이션을 감시·관리하는 기능 묶음. `spring-boot-starter-actuator` |
| 엔드포인트 ID | 엔드포인트 하나를 가리키는 이름(`health`·`env`·`loggers` …). 경로·프로퍼티 키가 모두 이 ID로 만들어진다 |
| 접근(access) | 엔드포인트를 **얼마나** 허용하는지 — `unrestricted`/`read-only`/`none` |
| 노출(exposure) | 엔드포인트를 **어느 통로**(HTTP·JMX)에 내놓는지. 접근과 별개의 축 |
| `max-permitted` | 개별 접근 설정이 넘을 수 없는 상한 |
| 관리 서버 | 운영 엔드포인트만 내놓는 별도 포트·주소·SSL의 서버 (`management.server.*`) |
| 발견 페이지 | `/actuator` 루트가 엔드포인트 목록을 링크로 내주는 하이퍼미디어 응답 |
| `@Endpoint` | 기술 중립 커스텀 엔드포인트를 선언하는 애노테이션 |
| `@ReadOperation`/`@WriteOperation`/`@DeleteOperation` | 각각 GET·POST·DELETE로 노출되는 오퍼레이션 |
| `@Selector` | 오퍼레이션 파라미터를 경로 변수로 받게 하는 애노테이션 |
| `HealthIndicator` | 한 조각의 건강 상태를 `Health` 객체로 돌려주는 인터페이스 |
| `Health` / 상태 | `UP`·`DOWN`·`OUT_OF_SERVICE`·`UNKNOWN` 등. 순서와 HTTP 코드 매핑을 설정으로 바꾼다 |
| `show-details` / `show-values` | 건강 상세와 설정 값을 누구에게까지 보여줄지 (`never`/`when-authorized`/`always`) |
| `EndpointRequest` | 시큐리티 설정에서 "엔드포인트들"을 가리키는 요청 매처 |
| JMX / MBean | 자바 표준 관리 인터페이스와 거기에 등록되는 관리 객체 |
| 관측 가능성(Observability) | 밖에서 안의 상태를 알 수 있는 정도. 로그·메트릭·트레이스 세 기둥 |
| Micrometer | 메트릭 수집의 벤더 중립 파사드 |
| Micrometer Observation | 한 번의 계측으로 메트릭과 트레이스를 함께 만드는 상위 추상 |
| `ObservationRegistry` | 관측을 만들고 핸들러에 전달하는 레지스트리 |
| 저카디널리티 / 고카디널리티 태그 | 값 종류가 적어 메트릭 차원이 될 수 있는 태그 / 종류가 많아 트레이스에만 붙는 태그 |
| `MeterRegistry` | 미터(계측기)를 등록·보관하는 레지스트리. 여러 개를 합성해 쓴다 |
| 미터 / 미터 접두사 | 계측기 한 개와, 그 이름들이 공유하는 앞머리(`jvm.`·`http.server.requests`) |
| `MeterRegistryCustomizer` | 자동설정된 레지스트리에 공통 태그 등을 먹이는 확장점 |
| 스크레이프 / 푸시 | 모니터링 시스템이 끌어가는 방식 / 애플리케이션이 밀어 보내는 방식 |
| Pushgateway | 짧게 살다 죽는 잡의 메트릭을 Prometheus 대신 받아 주는 중계 |
| Exemplar | 메트릭 한 점에 대응하는 트레이스를 가리키는 표본 링크 |
| OTLP | OpenTelemetry가 데이터를 실어 보내는 프로토콜 |
| 트레이스 / 스팬 | 요청 하나가 지나간 전체 경로 / 그 안의 한 구간 |
| `traceId` / `spanId` | 트레이스·스팬의 식별자. MDC로 로그에 붙는다 |
| 샘플링 확률 | 트레이스를 남길 비율. 기본 10% |
| Baggage | 트레이스와 함께 전파되는 사용자 정의 키·값 |
| Brave / Zipkin | 트레이서 구현 하나와 그 수집·조회 서버 |
| 설정된 레벨 / 유효 레벨 | 명시적으로 지정한 로그 레벨 / 상위에서 물려받아 실제로 적용되는 레벨 |
| `AuditEventRepository` | 감사 이벤트를 쌓는 인터페이스. 빈이 있어야 감사가 켜진다 |
| `HttpExchangeRepository` | 요청·응답 기록을 쌓는 인터페이스 |
| `ApplicationPidFileWriter` | 프로세스 ID를 파일로 남기는 리스너 |

## 처음 보는 개념

학습 지도에서 B12는 **⭐ 신규**로 표시돼 있다. `Spring/` 구역 day01~day08 노트에는 Actuator·Micrometer·트레이싱을 다룬 자리가 없다. 수업은 요청을 받아 응답을 돌려주는 데까지 갔고, **그 애플리케이션을 운영 중에 들여다보는 층은 처음 보는 영역**이다. 처음 만나는 골격을 미리 알아 두면 문서가 덜 흩어져 보인다.

- **"접근"과 "노출"이 다른 두 축이다.** 엔드포인트가 켜졌는지(`access`)와 어느 통로로 나가는지(`exposure`)를 문서가 따로 절로 나눠 둔다. 이 둘을 하나로 착각하면 설정이 왜 안 먹는지 설명이 안 된다 — 학습 세션에서 가장 먼저 분리해 볼 지점.
- **`management.*`는 `server.*`와 나란한 또 하나의 서버다.** 포트·주소·SSL을 따로 갖는다는 것은 "운영 창구는 서비스 트래픽과 다른 문"이라는 시각이다. B07에서 본 서버 커스터마이즈가 여기서 한 벌 더 나온다.
- **한 번 계측해서 둘로 나간다.** Observation 하나가 메트릭과 트레이스를 함께 만든다는 구조, 그리고 그 경계를 **태그의 카디널리티**가 가른다는 규칙이 이 챕터의 중심 아이디어로 보인다.
- **계측은 "부트가 만들어 준 것"에만 붙는다.** HTTP 클라이언트 메트릭이 자동설정된 빌더를 거친 클라이언트만 잡고, 트레이스 전파도 같은 조건이다. B11에서 "빌더를 주입받아 쓴다"가 규약이었던 이유가 여기서 한 번 더 나타난다.
- **개발용 기본 구현이 반복된다.** 감사·HTTP 교환 기록 모두 인메모리 구현이 딸려 오고 문서가 운영 부적합을 명시한다. B11의 Simple 캐시 폴백과 같은 모양 — "돌아가긴 하는 기본값"과 "운영용"의 구분.
- **끄고 켜는 기본값이 기능마다 다르다.** JMX는 꺼져 있고, 프로세스 파일 기록도 꺼져 있고, 감사·HTTP 교환은 빈이 없으면 안 켜지고, 메트릭·건강은 그냥 켜진다. 이 비대칭에 어떤 기준이 있는지가 볼 것.
- **테스트에서 트레이싱은 자동설정되지 않는다.** B10에서 본 "슬라이스마다 뭘 띄우는지"의 문제가 여기까지 이어진다.

## 학습 세션에서 확인할 것

- [ ] `access`와 `exposure`는 각각 무엇을 막는가 — 둘 중 하나만 열었을 때 요청은 어디서 걸리며, `max-permitted`는 왜 따로 필요한가
- [ ] 스타터만 넣었을 때 **기본으로 나오는 엔드포인트가 둘뿐인 것**은 어떤 판단인가. `include=*`를 운영에서 쓰면 무엇이 새어 나가는가
- [ ] `management.server.port`를 따로 두는 것과 시큐리티로 엔드포인트를 잠그는 것은 **무엇을 다르게 막는가** — 둘 다 해야 하는가
- [ ] `HealthIndicator`가 `DOWN`을 돌려주면 그 뒤에 무슨 일이 연쇄로 일어나는가 (HTTP 코드 · 로드밸런서 · 쿠버네티스 프로브) — 건강 상태를 누가 읽는다고 가정한 설계인가
- [ ] 저카디널리티/고카디널리티 태그의 구분을 어기면 무슨 일이 생기는가 — 사용자 ID를 메트릭 태그로 쓰면 왜 안 되는가
- [ ] 직접 `new RestClient…`로 만든 클라이언트는 왜 메트릭도 트레이스도 안 붙는가 — 자동설정된 빌더가 그 사이에서 하는 일은 무엇인가
- [ ] 샘플링 기본값 10%는 무엇을 위한 타협인가 — 100%로 올리면 무엇이 비싸지고, 낮게 두면 무엇을 못 보는가

## 원문 링크

- https://docs.spring.io/spring-boot/reference/actuator/index.html
- https://docs.spring.io/spring-boot/reference/actuator/enabling.html
- https://docs.spring.io/spring-boot/reference/actuator/endpoints.html
- https://docs.spring.io/spring-boot/reference/actuator/monitoring.html
- https://docs.spring.io/spring-boot/reference/actuator/jmx.html
- https://docs.spring.io/spring-boot/reference/actuator/observability.html
- https://docs.spring.io/spring-boot/reference/actuator/metrics.html
- https://docs.spring.io/spring-boot/reference/actuator/tracing.html
- https://docs.spring.io/spring-boot/reference/actuator/loggers.html
- https://docs.spring.io/spring-boot/reference/actuator/auditing.html
- https://docs.spring.io/spring-boot/reference/actuator/http-exchanges.html
- https://docs.spring.io/spring-boot/reference/actuator/process-monitoring.html
