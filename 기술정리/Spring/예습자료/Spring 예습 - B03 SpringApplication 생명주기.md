---
출처: 자동수집(Claude)
작성일: 2026-09-18
성격: 예습자료
tags: [학습, spring]
---

# Spring 예습 - B03 SpringApplication 생명주기

> 예습자료 — 자동 생성, 사용자 미검증. 결론이 아니라 **읽을 범위의 지도**다.
> 기준 버전: Spring Boot 4.1.1

## 이 모듈이 다루는 범위

B01·B02가 "밖에서 본 부트"(어떻게 띄우고 어떻게 담기는가)였다면, B03은 **`main()`이 호출된 뒤 애플리케이션이 뜰 때까지 안에서 무슨 순서로 무슨 일이 일어나는가**를 다루는 자리다.

| 문서 | 문서가 서 있는 자리 |
| --- | --- |
| Reference → Core Features → SpringApplication | 본체. 부팅 실패 처리, 배너, 빌더, 가용성 상태, 이벤트 순서, 웹 환경 판정, 인자 접근, 러너, 종료, 기동 추적, 가상 스레드 |
| Reference → Web → Graceful Shutdown | 종료 쪽의 갈래 하나. 기동보다 **종료**가 어떤 단계를 거치는지 |

공식 문서에 「생명주기」라는 이름의 절은 **없다.** `SpringApplication` 한 페이지가 시작부터 종료까지를 순서대로 늘어놓고, 그 중 이벤트 목록 절이 실질적인 생명주기 표 역할을 한다. 이 모듈의 제목은 학습 지도 쪽 명명이지 문서의 목차명이 아니라는 점을 먼저 확인하고 들어갈 것.

## 목차 지도

### SpringApplication (본체)

- **SpringApplication** — `main()`에서 부트를 부팅시키는 진입 클래스라는 정의. 기동 로그의 성격(`spring.main.log-startup-info`로 끌 수 있다는 것)이 여기 붙어 있다
- **Startup Failure** — 뜨지 못했을 때 무엇이 그 메시지를 만드는가. `FailureAnalyzer`라는 빈이 등장하는 자리(포트 충돌이 예시). 분석기가 없을 때 디버그 로그로 떨어지는 경로도 같이
- **Lazy Initialization** — 빈 생성을 실제 필요 시점까지 미루는 선택지와 그 대가. `spring.main.lazy-initialization`
- **Customizing the Banner** — `banner.txt`와 치환 변수(`${application.version}`·`${spring-boot.version}` 등), `spring.banner.location`·`spring.banner.charset`·`spring.main.banner-mode`
- **Customizing SpringApplication** — 정적 `run()` 대신 인스턴스를 만들어 설정을 얹는 경로(`setBannerMode()` 등)
- **Fluent Builder API** — `SpringApplicationBuilder`. 부모/자식 **컨텍스트 계층**을 만들 수 있다는 사실이 이 절의 핵심 소재
- **Application Availability** — 컨테이너(쿠버네티스) 프로브와 맞물리는 상태 개념. 아래 세 갈래로 쪼개져 있다
  - *Liveness State* — "살아 있는가"
  - *Readiness State* — "트래픽을 받을 준비가 됐는가"
  - *Managing the Application Availability State* — 그 상태를 읽고 바꾸는 쪽(`ApplicationAvailability` 주입, 이벤트 발행)
- **Application Events and Listeners** — 기동 중 발행되는 이벤트의 **순서 목록**. 사실상 이 모듈의 뼈대 절
- **Web Environment** — 어떤 `ApplicationContext` 종류를 쓸지 부트가 무엇을 보고 정하는가. 판정 알고리즘과 강제 지정 수단
- **Accessing Application Arguments** — 커맨드라인 인자를 `ApplicationArguments`로 받는 경로
- **Using the ApplicationRunner or CommandLineRunner** — 기동이 끝난 뒤, 트래픽을 받기 전에 코드를 한 번 돌리는 두 인터페이스와 그 순서 제어
- **Application Exit** — 종료 훅과 종료 코드. `ExitCodeGenerator`·`DisposableBean`
- **Admin Features** — `spring.application.admin.enabled`로 열리는 MBean 경로(`SpringApplicationAdminMXBean`)
- **Application Startup Tracking** — 기동의 각 단계를 계측하는 장치. `ApplicationStartup`·`StartupStep`·`BufferingApplicationStartup`·`FlightRecorderApplicationStartup`
- **Virtual Threads** — Java 21+ 가상 스레드 사용(`spring.threads.virtual.enabled`)과, 그때 JVM을 살려 두는 문제(`spring.main.keep-alive`)

### Graceful Shutdown (웹 구역)

- **Graceful Shutdown** — 기본 활성. 내장 서버(Tomcat·Jetty·Reactor Netty)에서 종료 시 진행 중 요청을 마치게 두는 구간. 프레임워크의 `SmartLifecycle` 위에 얹혀 있다는 점이 명시된다
- **Rejecting Requests During the Grace Period** — 그 구간에 새로 들어오는 요청은 어떻게 되는가 (서버 구현마다 네트워크 계층에서 끊는 방식이 다르다)
- **Disabling Graceful Shutdown** — `server.shutdown=immediate` · `spring.lifecycle.timeout-per-shutdown-phase`

## 기동 이벤트 순서 (문서가 나열한 그대로의 자리표)

무엇을 뜻하는지는 쓰지 않는다 — **어느 지점에 이름이 박혀 있는지**만 옮긴다.

| 순서 | 이벤트 | 문서가 표시한 시점 |
| --- | --- | --- |
| 1 | `ApplicationStartingEvent` | 실행 시작 직후, 리스너·이니셜라이저 등록 외에는 아무 처리 전 |
| 2 | `ApplicationEnvironmentPreparedEvent` | `Environment`가 정해졌고 컨텍스트 생성 전 |
| 3 | `ApplicationContextInitializedEvent` | 컨텍스트가 준비되고 `ApplicationContextInitializer`가 불린 뒤, 빈 정의 적재 전 |
| 4 | `ApplicationPreparedEvent` | refresh 직전, 빈 정의 적재 후 |
| (사이) | `WebServerInitializedEvent` · `ContextRefreshedEvent` | 4와 5 사이에 추가로 발행됨 |
| 5 | `ApplicationStartedEvent` | 컨텍스트 refresh 후, 러너 호출 전 |
| 6 | `AvailabilityChangeEvent` (`LivenessState.CORRECT`) | 5 직후 |
| 7 | `ApplicationReadyEvent` | 러너 호출이 끝난 뒤 |
| 8 | `AvailabilityChangeEvent` (`ReadinessState.ACCEPTING_TRAFFIC`) | 7 직후 |
| — | `ApplicationFailedEvent` | 기동 중 예외가 났을 때 |

## 핵심 용어

| 용어 | 한 줄 |
| --- | --- |
| `SpringApplication` | `main()`에서 부트 애플리케이션을 부팅시키는 클래스 |
| `SpringApplicationBuilder` | 같은 일을 체이닝 방식으로 하되 부모/자식 컨텍스트 계층까지 구성할 수 있는 빌더 |
| `FailureAnalyzer` | 기동 실패를 사람이 읽을 메시지로 번역하는 빈 |
| lazy initialization | 빈을 미리 만들지 않고 처음 필요할 때 만드는 설정 |
| `ApplicationContextInitializer` | 컨텍스트가 refresh 되기 전에 끼어들어 손대는 콜백 |
| refresh | 컨텍스트가 빈 정의를 읽어 실제 빈을 만들어 올리는 단계 (프레임워크 쪽 용어) |
| `WebApplicationType` | 이 애플리케이션이 서블릿·리액티브·비웹 중 무엇인지 나타내는 값 |
| `AnnotationConfigServletWebServerApplicationContext` / `…ReactiveWebServerApplicationContext` / `AnnotationConfigApplicationContext` | 위 판정 결과로 선택되는 세 컨텍스트 구현 |
| `ApplicationArguments` | 커맨드라인 인자를 옵션/비옵션으로 갈라 담은 객체 |
| `CommandLinePropertySource` | 커맨드라인 인자를 `Environment`의 프로퍼티로 편입시키는 출처 |
| `CommandLineRunner` / `ApplicationRunner` | 기동 완료 후 한 번 실행되는 콜백 두 종류. 받는 인자 형태가 다르다 |
| `ApplicationAvailability` | 현재 가용성 상태를 읽는 인터페이스 |
| `LivenessState` / `ReadinessState` | 가용성의 두 축. 각각 "살아 있음"·"트래픽 수용" |
| `AvailabilityChangeEvent` | 위 상태 변화를 알리는 이벤트 |
| `ExitCodeGenerator` | 종료 코드를 직접 정하게 하는 인터페이스 |
| `SpringApplicationAdminMXBean` | 원격 관리용으로 노출되는 MBean |
| `ApplicationStartup` / `StartupStep` | 기동 단계를 계측하기 위한 추상과 그 한 단위 |
| `BufferingApplicationStartup` / `FlightRecorderApplicationStartup` | 계측 결과를 메모리에 모으는 구현 / JFR로 흘리는 구현 |
| 가상 스레드 (virtual threads) | Java 21+의 경량 스레드. `spring.threads.virtual.enabled` |
| `SmartLifecycle` | 시작·종료 순서를 단계(phase)로 통제하는 프레임워크 인터페이스. graceful shutdown이 이 위에 있다 |
| grace period | 종료 신호 후 진행 중 요청을 마치도록 기다려 주는 구간 |

## 처음 보는 개념

학습 지도에서 B03은 **신규**(KDT 수업 노트에 없음)로 표시돼 있다. 아래는 이 모듈에서 처음 등장하는 축들이다 — 무엇인지 답을 여기서 확인하지 말고, 문서에서 자리만 짚어 둘 것.

- **"뜬다"가 한 덩어리가 아니라 단계라는 것.** 지금까지는 실행하면 떴다. 이 모듈은 그 사이에 최소 8개의 이름 붙은 지점이 있고, 각 지점마다 아직 존재하지 않는 것이 정해져 있다고 말한다. 예를 들어 `ApplicationEnvironmentPreparedEvent` 시점에는 컨텍스트가 아직 없다.
- **일부 이벤트는 빈으로 등록된 리스너가 받을 수 없다는 구조적 제약.** 문서는 컨텍스트가 만들어지기 전에 발행되는 이벤트가 있다고 밝히고, 그런 리스너를 등록하는 별도 경로를 제시한다. "왜 `@EventListener`로는 못 받는가"가 이 절의 실질적 질문이다.
- **`ApplicationContext`의 종류가 여러 개고, 부트가 클래스패스를 보고 고른다는 것.** 지금까지 컨텍스트는 하나였다. 판정 순서(MVC가 있으면 → 없고 WebFlux가 있으면 → 둘 다 없으면)와, 그 자동 판정을 사람이 덮어쓰는 수단이 나란히 있다.
- **컨텍스트가 계층(부모-자식)을 이룰 수 있다는 것.** `SpringApplicationBuilder`의 존재 이유. 트랙 S의 S02(레거시 컨텍스트 2단 구조)와 정면으로 짝이 되는 지점이므로, 여기서는 "가능하다"까지만 봐 두면 된다.
- **가용성(availability)이 "떴다/안 떴다"와 다른 축이라는 것.** 살아 있음과 트래픽 수용이 갈라져 있고, 상태를 애플리케이션 쪽에서 바꿀 수도 있다. B12(Actuator)·B13(배포)로 이어지는 선행 개념.
- **종료에도 단계가 있다는 것.** 기동만 배우고 종료는 안 배웠다. graceful shutdown은 기본값으로 켜져 있고 `SmartLifecycle`의 phase 위에서 돌아간다 — 즉 종료도 순서가 규정된 절차다.
- **기동 자체를 계측하는 장치가 표준으로 있다는 것.** `ApplicationStartup`은 "느리다"를 로그가 아니라 단계별 측정으로 보는 경로다.
- **러너 두 개(`CommandLineRunner`·`ApplicationRunner`)가 따로 있는 이유.** 이름이 다른 만큼 받는 인자가 다르고, 여러 개일 때의 순서 지정 수단이 따로 있다.
- **가상 스레드와 `spring.main.keep-alive`.** 4.x 기준 문서에만 있는 비교적 새 절. 가상 스레드를 켜면 JVM이 살아 있는 조건이 달라진다는 문제 제기가 붙어 있다.

## 학습 세션에서 확인할 것

- [ ] `ApplicationStartedEvent`와 `ApplicationReadyEvent` 사이에는 정확히 무엇이 끼어 있는가. 두 개를 하나로 합치면 무엇이 불가능해지는가
- [ ] 컨텍스트가 만들어지기 전에 발행되는 이벤트를 받으려면 리스너를 어떻게 등록해야 하는가. 왜 빈으로는 안 되는가
- [ ] 클래스패스에 Spring MVC와 WebFlux가 **둘 다** 있으면 부트는 무엇을 고르는가. 그 선택이 마음에 안 들 때 바꾸는 수단은 몇 가지인가
- [ ] `CommandLineRunner`와 `ApplicationRunner`는 무엇이 다르고, 둘 다 있을 때 실행 순서는 무엇이 정하는가
- [ ] lazy initialization을 켜면 기동은 빨라진다 — 대신 무엇이 뒤로 밀리는가. 그 대가가 문제가 되는 상황은 어떤 상황인가
- [ ] graceful shutdown이 켜져 있을 때 종료 신호를 받은 순간부터 프로세스가 끝날 때까지 무엇이 순서대로 일어나는가. 기동 이벤트 목록의 역순인가 아닌가

## 원문 링크

- https://docs.spring.io/spring-boot/reference/features/spring-application.html
- https://docs.spring.io/spring-boot/reference/web/graceful-shutdown.html
