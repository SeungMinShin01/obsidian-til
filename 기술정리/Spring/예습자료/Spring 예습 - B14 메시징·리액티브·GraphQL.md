---
출처: 자동수집(Claude)
작성일: 2026-09-29
성격: 예습자료
tags: [학습, spring]
---

# Spring 예습 - B14 메시징·리액티브·GraphQL

> 예습자료 — 자동 생성, 사용자 미검증. 결론이 아니라 **읽을 범위의 지도**다.
> 기준 버전: Spring Boot 4.1.1
> 학습 지도의 비고: **선택 — 필요할 때만**. 세 갈래를 한 모듈로 묶은 자리이므로, 정독 대상이 아니라 "무엇이 문서화돼 있는지"를 아는 쪽이 목적으로 보인다.

## 이 모듈이 다루는 범위

B14는 문서에서 **한 챕터가 아니다.** 서로 다른 세 곳을 묶은 모듈이고, 세 갈래를 하나로 묶은 근거는 문서가 준 것이 아니라 학습 지도가 준 것이다. 공통점을 문서에서 찾자면 **B07(서블릿 웹 애플리케이션)이 전제한 "요청–응답 한 번, 동기, HTTP"라는 틀에서 각자 다른 방향으로 벗어난다**는 점으로 읽힌다.

| 갈래 | 문서 위치 | 벗어나는 방향 |
| --- | --- | --- |
| **메시징** | Reference → Messaging (챕터 하나, 하위 7페이지) | 호출자·수신자가 **직접 연결되지 않는다**. 중간에 브로커가 있다 |
| **리액티브 웹** | Reference → Web → Reactive Web Applications | HTTP는 그대로지만 **스레드가 응답을 기다리며 묶이지 않는다**(non-blocking) |
| **GraphQL** | Reference → Web → Spring for GraphQL | 엔드포인트가 자원별로 갈라지지 않고 **하나(`POST /graphql`)이며, 무엇을 받을지는 클라이언트가 질의로 정한다** |

앞 모듈과의 연결로 문서가 반복해 꺼내는 지점:

- 세 갈래 모두 **자동설정의 문법은 B06과 동일하다** — 스타터를 넣으면 켜지고, 특정 빈을 직접 올리면 자동설정이 비킨다
- 설정 값은 전부 `spring.*` 프로퍼티로 들어온다(B04)
- 리액티브 웹의 페이지 구조는 B07(서블릿 웹) 페이지와 **절 이름이 거의 1:1로 대응한다** — 정적 자원, 웰컴 페이지, 에러 처리, 필터, API 버저닝. 같은 문제를 다른 층에서 다시 푸는 모양이므로 **대조해서 읽을 자리**로 보인다
- 메시징 각 페이지가 거의 예외 없이 **"보내기(Template)" / "받기(@Listener)" 두 절로 갈린다** — 브로커가 무엇이든 부트가 씌우는 모양이 같다는 뜻으로 읽힌다

- 원문(메시징 챕터): https://docs.spring.io/spring-boot/reference/messaging/index.html
- 원문(리액티브 웹): https://docs.spring.io/spring-boot/reference/web/reactive.html
- 원문(GraphQL): https://docs.spring.io/spring-boot/reference/web/spring-graphql.html

## 목차 지도

### 갈래 1 — Messaging (7페이지)

- **JMS** — 자바 표준 메시징 API를 부트가 어떻게 자동설정하는지. `ConnectionFactory`가 어디서 오는지를 브로커별로 나눠 설명하는 절들(ActiveMQ "Classic" `spring.activemq.*`, ActiveMQ Artemis `spring.artemis.*`의 embedded/native 두 모드, 애플리케이션 서버의 JNDI 조회), 그리고 커넥션 캐싱(`spring.jms.cache.*`)·풀링. 이어서 **보내기**(`JmsClient`·`JmsMessagingTemplate`·`JmsTemplate`) / **받기**(`@JmsListener`, 기본 `JmsListenerContainerFactory`, 트랜잭션이 `JtaTransactionManager` 유무에 따라 갈리는 지점) / **리스너 컨테이너 팩토리 직접 만들기**(`DefaultJmsListenerContainerFactoryConfigurer`, `ConnectionFactoryUnwrapper`)
- **AMQP** — RabbitMQ 쪽. `spring.rabbitmq.*` 연결 설정, **보내기**(`AmqpTemplate`·`AmqpAdmin`, 재시도 `spring.rabbitmq.template.retry.*`), **스트림으로 보내기**(`RabbitStreamTemplate`, `spring.rabbitmq.stream.*`) — 큐와 스트림을 다른 절로 나눠 둔 것이 눈에 걸리는 지점, **받기**(`@RabbitListener`, `spring.rabbitmq.listener.type`으로 컨테이너 종류를 고르는 자리, `MessageRecoverer`)
- **Apache Kafka Support** — `spring.kafka.*`와 `KafkaProperties`. **보내기**(`KafkaTemplate`, `spring.kafka.producer.transaction-id-prefix`를 주면 `KafkaTransactionManager`가 함께 붙는다), **받기**(`@KafkaListener`, `spring.kafka.listener.*`), **Kafka Streams**(`@EnableKafkaStreams`, `StreamsBuilder`, `spring.kafka.streams.application-id`) — 단순 송수신과 스트림 처리가 다른 층이라는 표시, **추가 프로퍼티**(부트가 이름을 매핑해 주지 않는 카프카 원본 설정을 넘기는 통로, producer/consumer/admin/streams별 override), **임베디드 카프카로 테스트**(`@EmbeddedKafka`)
- **Apache Pulsar Support** — 위 셋보다 절이 잘게 나뉘어 있다. 연결(`spring.pulsar.client.service-url`)·인증(`spring.pulsar.client.authentication.*`, **완화된 바인딩이 적용되지 않는다**고 명시된 예외 지점 — B04와 대조할 자리)·SSL·관리 API 연결(`spring.pulsar.admin.*`, `PulsarTopic` 빈으로 시작 시 토픽 생성), **보내기**(`PulsarTemplate`, `PulsarProducerFactory`의 캐시), **받기**(`@PulsarListener`), **읽기**(`@PulsarReader` — 커서를 직접 다루는, 받기와 구분된 별도 절), **트랜잭션**(`spring.pulsar.transaction.enabled`)
- **RSocket** — 프로토콜 자체가 요청–응답 외의 상호작용을 갖는 쪽. 페이로드 코덱(`RSocketStrategies`, 기본 순서 CBOR → JSON), 서버 자동설정(WebFlux 서버에 얹는 방식과 독립 TCP/WebSocket 서버 두 갈래, `spring.rsocket.server.transport`·`mapping-path`·`port`), 스프링 메시징 연동(`RSocketMessageHandler`, `@ControllerAdvice`), 그리고 클라이언트 쪽 `RSocketRequester`(서버 핸들러 메서드에 주입받아 **서버가 클라이언트를 부르는** 양방향 사용까지 예시에 있다)
- **Spring Integration** — 스타터 `spring-boot-starter-integration`, 클래스패스에 있으면 `@EnableIntegration`으로 자동 초기화. 폴링이 자동설정된 `TaskScheduler`에 얹힌다는 점과 기본 `PollerMetadata`(1초 간격), `spring.integration.poller.*`, JDBC 스키마 초기화(`spring.integration.jdbc.initialize-schema`), RSocket 연동, JMX로 메시지 처리 통계 노출
- **WebSockets** — 가장 짧은 페이지. 내장 톰캣·제티에 대한 자동설정이 있고 실제 내용은 스프링 프레임워크 문서로 넘긴다. MVC 쪽 스타터 `spring-boot-starter-websocket`, 리액티브 쪽은 `spring-boot-starter-webflux` + `jakarta.websocket-api` 의존성. WAR로 독립 컨테이너에 올릴 때는 **컨테이너가 설정 주체**가 된다는 단서
- (별도로 How-to → Messaging 페이지가 있다: https://docs.spring.io/spring-boot/how-to/messaging.html)

### 갈래 2 — Reactive Web Applications

B07의 서블릿 웹 페이지와 **같은 순서로 같은 주제를 다시 다룬다.** 대조 대상으로 읽을 자리.

- **The "Spring WebFlux Framework"** — WebFlux가 무엇인지, Reactive Streams와 Reactor(`Mono`·`Flux`) 위에 서 있다는 소개
- **Spring WebFlux Auto-configuration** — 부트가 기본으로 까는 것, `@EnableWebFlux`를 직접 붙이면 어떻게 되는지의 경계
- **Spring WebFlux Conversion Service** — `WebFluxConfigurer`와 `spring.webflux.format.*`
- **HTTP Codecs with HttpMessageReaders and HttpMessageWriters** — 서블릿 쪽 `HttpMessageConverter`에 대응하는 자리. `CodecConfigurer`·`CodecCustomizer`
- **Static Content** — 기본 위치(`/static`·`/public`·`/resources`), `spring.webflux.static-path-pattern`, WebJars
- **Welcome Page** — `index.html` 탐색
- **Template Engines** — Thymeleaf·FreeMarker·Mustache, `src/main/resources/templates`
- **Error Handling** — `WebExceptionHandler`·`ErrorAttributes`·`AbstractErrorWebExceptionHandler`, RFC 9457 Problem Details(`application/problem+json`), 화이트레이블
- **Custom Error Pages** — 상태 코드 이름의 파일(`404.html`·`5xx.mustache`)을 `error/`에 두는 규약
- **Web Filters** — 서블릿 `Filter`가 아니라 `WebFilter`, `@Order`, 스프링 시큐리티 필터가 `-100`에 놓인다는 언급
- **API Versioning** — 헤더·쿼리 파라미터·미디어 타입·경로 중 무엇으로 버전을 읽을지, `spring.webflux.apiversion.*`, `ApiVersionResolver`·`ApiVersionParser`·`ApiVersionDeprecationHandler`
- **Embedded Reactive Server Support**
  - **Customizing Reactive Servers** — `server.*` 프로퍼티(포트·주소·SSL·압축)
  - **Programmatic Customization** — `WebServerFactoryCustomizer`, 서버별 팩토리(`NettyReactiveWebServerFactory`·`JettyReactiveWebServerFactory`·`TomcatReactiveWebServerFactory`) — 기본이 Reactor Netty라는 점
  - **Customizing ConfigurableReactiveWebServerFactory Directly** — 팩토리를 직접 확장하는 마지막 수단
  - **Reactive Server Resources Configuration** — `ReactorResourceFactory`·`JettyResourceFactory`로 **서버와 `WebClient`가 이벤트 루프·커넥션 풀을 공유**하게 하는 절. B11의 `WebClient`와 이어지는 지점

### 갈래 3 — Spring for GraphQL

- **Introduction** — GraphQL Java 위에 선다는 것, 스타터 `spring-boot-starter-graphql`, 그리고 **전송 방식을 표로 나눠 둔다**(Spring MVC의 HTTP, WebSocket, WebFlux, RSocket) — 스키마·컨트롤러는 그대로 두고 전송만 갈아 끼우는 구조로 읽힌다
- **GraphQL Schema** — 스키마 파일을 어디서 찾는지(`src/main/resources/graphql/**`, `.graphqls`·`.gqls`), `spring.graphql.schema.locations`·`file-extensions`, 멀티 모듈에서 `classpath*:` 접두사, 인트로스펙션 차단(`spring.graphql.schema.introspection.enabled`)
- **GraphQL RuntimeWiring** — 스키마의 필드를 실제 코드에 잇는 층. `RuntimeWiringConfigurer`로 커스텀 스칼라·디렉티브·`DataFetcher`를 등록하는 낮은 길과, **문서가 권하는 길인 애노테이션 컨트롤러**(`@Controller` + `@QueryMapping`·`@Argument`)
- **Querydsl and QueryByExample Repositories Support** — `@GraphQlRepository`를 붙인 스프링 데이터 리포지토리가 최상위 질의의 `DataFetcher` 후보로 자동 등록되는 자리
- **Transports**
  - **HTTP and WebSocket** — 기본 `POST /graphql`(`spring.graphql.http.path`), 구독(subscription)을 SSE(`text/event-stream`)로 흘리는 선택지, WebSocket 경로(`spring.graphql.websocket.path`), CORS(`spring.graphql.cors.*`), 요청을 가로채는 `WebGraphQlInterceptor`
  - **RSocket** — `spring.graphql.rsocket.mapping`, 자동설정되는 `RSocketGraphQlClient.Builder` — 갈래 1의 RSocket과 만나는 지점
- **Exception Handling** — `DataFetcherExceptionResolver`들을 순서대로 불러 `GraphQLError` 목록으로 바꾸는 층. HTTP 상태 코드가 아니라 **응답 본문 안의 에러 목록**이라는 점이 B07의 `/error`와 갈리는 자리
- **GraphiQL and Schema Printer** — `/graphiql`(기본 꺼짐, `spring.graphql.graphiql.enabled`, devtools가 있으면 켜짐), `/graphql/schema`로 스키마 텍스트 노출(`spring.graphql.schema.printer.enabled`)

## 핵심 용어

| 용어 | 한 줄 (사전적 수준) |
| --- | --- |
| `ConnectionFactory` (JMS) | JMS 브로커와의 연결을 만들어 주는 팩토리. 부트가 브로커별 자동설정으로 이 빈을 공급한다 |
| `@JmsListener` / `@RabbitListener` / `@KafkaListener` / `@PulsarListener` | 메서드를 특정 목적지의 메시지 수신 지점으로 등록하는 애노테이션. 브로커마다 짝이 하나씩 있다 |
| 리스너 컨테이너 (listener container) | 브로커에서 메시지를 끌어와 리스너 메서드를 부르는 런타임 구성물. 팩토리(`...ListenerContainerFactory`)가 만든다 |
| AMQP | Advanced Message Queuing Protocol. 메시지 브로커용 와이어 프로토콜 표준이며 RabbitMQ가 그 구현 |
| Kafka Streams | 카프카 토픽을 입력으로 받아 변환·집계해 다시 토픽으로 내보내는 스트림 처리 라이브러리. 단순 송수신과 다른 층 |
| RSocket | 요청–응답 외에 fire-and-forget·요청–스트림·채널 같은 상호작용 방식을 규격에 포함한 양방향 메시징 프로토콜 |
| CBOR | Concise Binary Object Representation. JSON과 같은 데이터 모델을 이진으로 표현하는 형식. RSocket 기본 코덱 |
| Reactive Streams | 비동기 스트림 처리와 배압(backpressure)을 규정한 명세. `Publisher`·`Subscriber` 등 네 인터페이스 |
| `Mono` / `Flux` | Reactor가 제공하는 `Publisher` 구현. 각각 0~1개, 0~N개의 값을 나중에 내놓는 자리표 |
| non-blocking | 결과를 기다리며 스레드를 붙잡아 두지 않는 실행 방식 |
| WebFlux | 서블릿 요청–응답 모델 대신 Reactive Streams 위에 선 스프링의 웹 프레임워크 |
| `WebFilter` | WebFlux에서 요청·응답을 가로채는 인터페이스. 서블릿 `Filter`에 대응하는 자리 |
| Problem Details (RFC 9457) | HTTP 오류 응답의 본문 형식을 정한 표준. 미디어 타입 `application/problem+json` |
| GraphQL 스키마 | 질의 가능한 타입·필드를 선언하는 정의 파일. 이 프로젝트에서는 `.graphqls`/`.gqls` |
| `DataFetcher` | 스키마의 한 필드에 실제 값을 채워 넣는 함수. 애노테이션 컨트롤러가 이것으로 변환된다 |
| 인트로스펙션 (introspection) | 클라이언트가 스키마 자체를 질의해 알아내는 GraphQL 기능. 운영에서 끌 수 있게 프로퍼티가 있다 |
| 구독 (subscription) | GraphQL에서 값이 계속 흘러오는 연산 종류. 전송은 WebSocket 또는 SSE |

## 처음 보는 개념

학습 지도에서 B14는 **신규**(수업 노트에 없음)이고, 비고가 「선택 — 필요할 때만」이다. 문서에 처음 등장하는 축은 세 개로 보인다.

1. **중간에 브로커가 끼는 통신** — B01~B13은 전부 "요청이 들어오면 내 애플리케이션이 답한다"였다. 메시징 챕터는 호출자와 수신자가 서로를 모르는 구조를 다루고, 그래서 트랜잭션·재시도·수신 실패 회복(`MessageRecoverer`)이 각 페이지에 반복해 나온다. **프로젝트에서 실제로 브로커를 쓸 때까지는 정독할 이유가 약해 보이는 갈래다.**
2. **스레드를 묶지 않는 웹 층** — WebFlux는 B07과 기능 목록이 겹치는데 구현 층이 다르다. 문서는 둘을 별 페이지로 두고 서로 참조를 걸지 않는다. "왜 같은 문제를 두 번 푸는가"가 이 갈래의 물음으로 읽힌다.
3. **엔드포인트 하나 + 클라이언트가 정하는 응답 모양** — GraphQL은 URL 설계·상태 코드·응답 스키마가 REST와 다른 자리에 놓인다. B07의 에러 처리(`/error`, 상태 코드)와 GraphQL의 에러 처리(본문 안 `errors` 목록)를 나란히 두면 그 차이가 드러날 것으로 보인다.

WMS 프로젝트(Spring Boot + React, REST)와의 관계에서는 세 갈래 모두 **지금 당장 쓰지 않는 쪽**이다. 학습 지도가 이 모듈을 「선택」으로 둔 것과 일치한다.

## 학습 세션에서 확인할 것

- [ ] 메시징 7페이지가 거의 모두 "보내기 / 받기" 두 절로 갈린다. 부트가 브로커마다 반복해서 씌우는 이 **공통 모양**을 무엇이라 부를 수 있는가 — 그리고 브로커별로 달라지는 부분은 주로 어디에 몰려 있는가
- [ ] WebFlux 페이지와 서블릿 웹 페이지의 절 이름이 거의 1:1로 대응한다. 그 중 **이름만 같고 실제로 하는 일이 다른 절**은 어디인가 (정적 자원 / 에러 처리 / 필터 / API 버저닝을 각각 대조해 볼 것)
- [ ] 리액티브 서버의 「Reactive Server Resources Configuration」이 서버와 `WebClient`의 자원을 공유하라고 말한다. B11에서 본 `WebClient` 쪽 설명과 맞춰 보면, 공유하지 않을 때 무엇이 낭비되는가
- [ ] GraphQL은 엔드포인트가 하나이고 에러를 응답 본문에 담는다. 그러면 B12(Actuator·메트릭)·B08(Security)에서 배운 **경로 기반 장치**들은 GraphQL 앞에서 어떻게 되는가 — 문서가 그 자리에 무엇을 두었는지 찾아볼 것
- [ ] Pulsar 인증 프로퍼티만 **완화된 바인딩이 적용되지 않는다**고 문서가 못 박아 두었다. B04의 완화된 바인딩 규칙에서 이 예외가 필요해지는 이유는 무엇으로 보이는가
- [ ] 이 모듈은 「선택」이다. 세 갈래 중 지금 진도에서 **읽어 둘 값이 있는 것 / 미뤄도 되는 것**을 어떤 기준으로 가를 것인가

## 원문 링크

- 메시징 챕터: https://docs.spring.io/spring-boot/reference/messaging/index.html
- JMS: https://docs.spring.io/spring-boot/reference/messaging/jms.html
- AMQP: https://docs.spring.io/spring-boot/reference/messaging/amqp.html
- Apache Kafka: https://docs.spring.io/spring-boot/reference/messaging/kafka.html
- Apache Pulsar: https://docs.spring.io/spring-boot/reference/messaging/pulsar.html
- RSocket: https://docs.spring.io/spring-boot/reference/messaging/rsocket.html
- Spring Integration: https://docs.spring.io/spring-boot/reference/messaging/spring-integration.html
- WebSockets: https://docs.spring.io/spring-boot/reference/messaging/websockets.html
- 메시징 How-to: https://docs.spring.io/spring-boot/how-to/messaging.html
- 리액티브 웹 애플리케이션: https://docs.spring.io/spring-boot/reference/web/reactive.html
- Spring for GraphQL: https://docs.spring.io/spring-boot/reference/web/spring-graphql.html
