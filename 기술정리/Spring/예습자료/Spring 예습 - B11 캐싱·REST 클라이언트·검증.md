---
출처: 자동수집(Claude)
작성일: 2026-09-26
성격: 예습자료
tags: [학습, spring]
---

# Spring 예습 - B11 캐싱·REST 클라이언트·검증

> 예습자료 — 자동 생성, 사용자 미검증. 결론이 아니라 **읽을 범위의 지도**다.
> 기준 버전: Spring Boot 4.1.1

## 이 모듈이 다루는 범위

B11은 공식 문서의 한 챕터가 아니라 **Reference → IO 챕터 안의 세 페이지**를 골라 묶은 모듈이다. IO 챕터는 "애플리케이션이 바깥과 주고받는 것"을 모아 둔 자리이고, 그 안에 Caching · Spring Batch · gRPC · Hazelcast · Quartz · Sending Email · Validation · Calling REST Services · Web Services · JTA 열 페이지가 나란히 있다. 이 모듈은 그중 세 개다.

| 페이지 | 문서가 서 있는 자리 |
| --- | --- |
| **Caching** | 스프링 프레임워크의 **캐시 추상**에 부트가 붙이는 자동설정. 캐시 제공자 10종을 어떤 순서로 찾아내는지 |
| **Calling REST Services** | 남의 HTTP API를 **호출하는 쪽**. `WebClient`·`RestClient`·`RestTemplate` 세 갈래와, 그 아래 HTTP 클라이언트 구현 선택 |
| **Validation** | 메서드 파라미터·반환값에 제약 애노테이션을 걸어 검사하게 하는 자리. **분량이 매우 짧다** |

세 페이지의 분량이 크게 다르다는 것부터가 이 모듈의 성격이다. Calling REST Services가 압도적으로 길고(부트 4.x에서 새로 커진 절이 여럿), Caching은 제공자별로 짧게 갈라지고, Validation은 한 화면 분량이다. 검증의 본체(제약 애노테이션 사용법·`@Valid`와 웹 계층 바인딩)는 부트 문서가 아니라 **Spring Framework 문서와 Bean Validation 스펙**으로 넘긴다.

B07(서블릿 웹)이 "요청을 **받는** 쪽"이었다면, 이 모듈의 REST 클라이언트는 "요청을 **보내는** 쪽"이다. B10에서 본 `@RestClientTest`가 테스트하는 대상이 바로 여기서 만드는 것이다.

- 원문(챕터): https://docs.spring.io/spring-boot/reference/io/index.html

## 목차 지도

### 1. Caching

- **Caching** — 스프링의 캐시 추상(`@Cacheable` 등)이 이미 프레임워크 기능이고, 부트는 `@EnableCaching`이 있을 때 **제공자를 골라 `CacheManager`를 만들어 주는 일**만 한다는 것을 여는 자리
- **Supported Cache Providers** — 제공자 **탐색 순서**와 `spring.cache.type`으로 못 박는 방법, `spring.cache.cache-names`로 캐시 이름을 미리 정하는 방법, `CacheManagerCustomizer`로 만들어진 매니저에 손대는 방법
- 이하 제공자별 절 — 각 절은 "무엇이 클래스패스/빈에 있으면 이 제공자가 선택되고, 어떤 프로퍼티·설정 파일로 조정하는가"의 같은 틀을 반복한다
  - **Generic** — `Cache` 빈을 직접 올렸을 때
  - **JCache (JSR-107)** — `CachingProvider`로 부트스트랩하는 표준 경로 (`spring.cache.jcache.provider`·`spring.cache.jcache.config`)
  - **Hazelcast** — 분산 인메모리 그리드를 캐시로 쓰는 쪽
  - **Infinispan** — 설정 파일을 요구하는 쪽 (`spring.cache.infinispan.config`)
  - **Couchbase** — Spring Data Couchbase와 함께 (`spring.cache.couchbase.expiration`)
  - **Redis** — `RedisCacheManager` (`spring.cache.redis.time-to-live` 등)
  - **Caffeine** — `spring.cache.caffeine.spec`, `CacheLoader`
  - **Cache2k** — 인메모리 캐시 한 갈래
  - **Simple** — 아무것도 없을 때의 **폴백**. `ConcurrentHashMap` 기반 `ConcurrentMapCacheManager`
  - **None** — 캐시를 끄는 no-op 경로
- **Testing** — 테스트에서 캐시를 끄거나 다른 제공자로 바꿔 돌리는 자리 (`@AutoConfigureCache`)

### 2. Calling REST Services

#### 2-1. 세 갈래 클라이언트

- **WebClient** — 논블로킹·리액티브(WebFlux) 쪽에 권장되는 클라이언트
  - **WebClient Runtime** — `ClientHttpConnector` 구현을 클래스패스에서 찾아내는 규칙 (Reactor Netty → Jetty RS → Apache HttpClient → JDK HttpClient 순)
  - **Global HTTP Connector Configuration** — `spring.http.clients.reactive.connector`로 못 박기
  - **WebClient Customization** — 손보는 방법이 **세 층**(빌더를 주입받아 그 자리에서 / `WebClientCustomizer` 빈으로 전역 / 빌더를 복제해 새로)으로 갈린다는 자리
  - **WebClient SSL Support** — `WebClientSsl`로 SSL 번들을 얹기
- **RestClient** — 명령형(비리액티브) 쪽에 권장되는 클라이언트
  - **RestClient Customization** — 위와 같은 세 층 구조 (`RestClientCustomizer`)
  - **RestClient SSL Support** — `RestClientSsl`
- **RestTemplate** — 기존 코드를 위한 고전 경로. `RestTemplateBuilder`를 통해 받는다
  - **RestTemplate Customization** — 세 층 + `RestTemplateCustomizer` 빈
  - **RestTemplate SSL Support** — 빌더에 SSL 번들 적용

#### 2-2. 아래층 — 실제 HTTP를 누가 보내는가

- **HTTP Client Detection for RestClient and RestTemplate** — `ClientHttpRequestFactory` 구현을 클래스패스에서 찾는 순서(Apache HttpClient → Jetty → Reactor Netty → JDK `HttpClient` → `HttpURLConnection`)
- **Global HTTP Client Configuration** — `spring.http.clients.imperative.factory`로 특정 팩토리를 고르기

#### 2-3. 부트 4.x에서 커진 자리

- **API Versioning** — 호출하는 쪽에서도 버전을 헤더·쿼리 파라미터·URL 경로로 실어 보내게 하는 자리 (B07의 서버 쪽 API 버저닝과 대응)
- **HTTP Service Interface Clients** — 클라이언트를 직접 쓰는 대신 **애노테이션 붙인 자바 인터페이스**로 선언하는 방식
  - **Importing HTTP Services** — `@ImportHttpServices`
  - **Service Client Groups** — 공통 설정을 공유하는 이름 붙은 그룹
  - **Configuration Properties** — `spring.http.serviceclient.<group-name>.*` (`base-url`·`connect-timeout`·`read-timeout`)
  - **Customization** — `RestClientHttpServiceGroupConfigurer`·`WebClientHttpServiceGroupConfigurer`
  - **Advanced Configuration** — `AbstractHttpServiceRegistrar`로 프로그래밍 방식 등록
- **Applying Global Configuration to All HTTP Clients** — `HttpClientSettings`와 `spring.http.clients.*`(connect-timeout·read-timeout·redirects)로 **모든** 클라이언트에 공통 설정을 먹이는 자리
  - **InetAddress Filtering and SSRF Protection** — `InetAddressFilter`로 클라이언트가 어디로 나갈 수 있는지를 제한하는 보안 장치

### 3. Validation

- **Validation** — 클래스패스에 JSR-303 구현(보통 Hibernate Validator, `spring-boot-starter-validation`)이 있으면 **메서드 검증**이 자동으로 켜진다는 것. 대상 클래스에 `@Validated`를 붙이면 파라미터·반환값의 제약 애노테이션(`jakarta.validation.constraints.*`)이 검사된다
  - 제약 메시지의 파라미터는 애플리케이션의 `MessageSource`(`messages.properties`)로 풀린다는 단서
  - `ValidationConfigurationCustomizer` 빈으로 `ValidatorFactory`를 만들 때의 `Configuration`에 손대며, 여러 개면 `@Order` 순서로 불린다

> 이 페이지가 짧은 것 자체가 정보다. 검증 규칙을 **어떻게 쓰는가**는 Bean Validation 스펙과 Spring Framework의 일이고, 부트 문서는 "언제 켜지는가 / 어떻게 손보는가"만 말한다. 웹 요청 본문 검증(`@Valid` + `@RequestBody`)은 B07의 MVC 자동설정 쪽에 걸쳐 있다.

## 핵심 용어

| 용어 | 한 줄 |
| --- | --- |
| 캐시 추상 | 캐시 제공자를 바꿔도 코드가 그대로이게 하는 스프링의 중간 층 |
| `@EnableCaching` | 캐시 애노테이션 처리를 켜는 스위치. 부트의 캐시 자동설정도 이것이 있을 때 동작한다 |
| `@Cacheable` | 메서드 결과를 캐시에서 먼저 찾고 없으면 실행해 넣는 애노테이션 |
| `CacheManager` | 이름으로 `Cache` 인스턴스를 꺼내 주는 관리자 인터페이스 |
| `CacheResolver` | 호출마다 **어느 캐시를 쓸지** 고르는 확장점 |
| `CacheManagerCustomizer` | 자동설정이 만든 `CacheManager`에 뒤늦게 손대는 콜백 |
| `spring.cache.type` | 제공자 탐색을 무시하고 특정 제공자를 못 박는 프로퍼티 |
| JCache (JSR-107) | 자바 캐시 표준 API. `CachingProvider`로 구현을 부트스트랩한다 |
| Caffeine / Cache2k | 단일 JVM 안의 인메모리 캐시 라이브러리 두 갈래 |
| `ConcurrentMapCacheManager` | 아무 제공자도 없을 때 쓰이는 `ConcurrentHashMap` 기반 폴백 |
| `@AutoConfigureCache` | 테스트에서 캐시 자동설정을 조정하는 애노테이션 |
| `WebClient` | 논블로킹·리액티브 HTTP 클라이언트 |
| `RestClient` | 명령형 코드를 위한 유창한 API의 HTTP 클라이언트 (부트가 권장하는 신형) |
| `RestTemplate` | 고전 명령형 클라이언트. `RestTemplateBuilder`로 받는다 |
| `ClientHttpConnector` | 리액티브 클라이언트가 실제 전송에 쓰는 하부 추상 |
| `ClientHttpRequestFactory` | 명령형 클라이언트가 실제 전송에 쓰는 하부 추상 |
| `…Customizer` 빈 | 자동설정된 빌더 전체에 공통 변경을 먹이는 확장점 (`WebClientCustomizer`·`RestClientCustomizer`·`RestTemplateCustomizer`) |
| SSL 번들 | 키스토어·트러스트스토어 묶음을 이름으로 참조하는 부트의 추상 (`SslBundles`) |
| `@HttpExchange` / `@GetExchange` | 인터페이스 메서드를 원격 HTTP 호출로 선언하는 애노테이션 계열 |
| `@ImportHttpServices` | 애노테이션 붙인 인터페이스들을 HTTP 서비스 클라이언트로 등록하는 애노테이션 |
| 서비스 클라이언트 그룹 | 여러 HTTP 서비스 인터페이스가 base-url·타임아웃을 공유하도록 묶은 이름 있는 단위 |
| `HttpClientSettings` | 모든 HTTP 클라이언트에 공통으로 적용되는 설정 묶음 |
| `InetAddressFilter` | 클라이언트가 접속할 수 있는 주소를 걸러 SSRF를 막는 장치 |
| SSRF | 서버가 공격자가 지정한 내부 주소로 요청을 보내게 되는 취약점 |
| Bean Validation / JSR-303 | 제약 애노테이션으로 값을 검사하는 자바 표준과 그 스펙 번호 |
| Hibernate Validator | Bean Validation의 표준적 구현체 |
| `@Validated` | 메서드 수준 검증을 켜기 위해 대상 클래스에 붙이는 애노테이션 |
| `ValidationConfigurationCustomizer` | `ValidatorFactory`를 만들 때의 설정에 손대는 빈 |
| `MessageSource` | 메시지를 로케일별로 풀어 주는 스프링 추상. 제약 메시지도 여기서 온다 |

## 처음 보는 개념

학습 지도에서 B11은 **신규**로 표시돼 있다. `Spring/` 구역 day 노트에는 캐시·외부 API 호출·검증 어느 쪽도 다룬 자리가 없다. 다만 앞선 예습 모듈과 맞물리는 지점이 뚜렷하다.

- **"클래스패스를 보고 고른다"가 세 번 반복된다.** 캐시 제공자 탐색 순서, 리액티브 커넥터 탐색 순서, 명령형 팩토리 탐색 순서가 모두 같은 모양이다. B06에서 본 조건 애노테이션(`@ConditionalOnClass` 계열)이 세 자리에서 같은 방식으로 쓰인 것으로 읽히는지 확인할 자리.
- **커스터마이즈가 늘 세 층이다.** 부트 문서는 `WebClient`·`RestClient`·`RestTemplate` 세 곳에서 똑같이 "주입받은 빌더를 그 자리에서 / `Customizer` 빈으로 전역 / 빌더를 복제해 별도로"를 반복한다. 이 세 층이 **적용 범위와 순서에서 어떻게 다른지**가 이 모듈에서 새로 보는 것.
- **부르는 쪽과 받는 쪽의 대칭.** API 버저닝·메시지 컨버터·SSL은 B07(서버)에도 있었고 여기(클라이언트)에도 있다. 같은 개념이 방향만 바꿔 나타난다.
- **SSRF 방어가 프레임워크 기능으로 들어와 있다.** `InetAddressFilter`와 `spring.http.clients` 전역 설정은 "HTTP 클라이언트를 애플리케이션이 통제해야 하는 자원으로 본다"는 시각이다. B08(시큐리티)이 들어오는 요청을 막았던 것과 반대 방향.
- **선언형 HTTP 클라이언트.** `@ImportHttpServices`와 인터페이스 선언 방식은 데이터 접근에서 Spring Data 리포지토리 인터페이스가 하던 일(B09)과 구조가 같다 — 구현을 프레임워크가 만들어 준다.
- **검증 문서가 짧은 이유.** 부트는 "켜짐 조건과 손대는 법"만 말하고 규칙 자체는 스펙으로 넘긴다. 이 경계선이 어디에 그어져 있는지가 이 페이지에서 볼 것이다.

## 학습 세션에서 확인할 것

- [ ] `@Cacheable`만 붙이고 아무 캐시 라이브러리도 넣지 않으면 무슨 일이 일어나는가 — 어디까지가 프레임워크의 일이고 어디부터가 부트의 일인가
- [ ] 캐시 제공자 탐색 순서에서 **Simple(폴백)이 마지막인 것**의 결과는 무엇인가 — 운영에서 이것이 문제가 되는 상황을 상상할 수 있는가
- [ ] `RestClient`·`RestTemplate`·`WebClient` 셋 중 하나를 고르는 기준은 무엇이며, `RestClient`가 `RestTemplate`을 대체한다는 말은 **무엇이 달라졌다는 뜻인가**
- [ ] 클라이언트를 손보는 세 방법(주입받은 빌더 / `Customizer` 빈 / 빌더 복제)은 각각 어디까지 영향을 주는가 — 팀에서 타임아웃을 전사 통일하려면 어느 층인가
- [ ] 선언형 HTTP 서비스 인터페이스(`@ImportHttpServices`)는 직접 `RestClient`를 쓰는 것에 비해 무엇을 얻고 무엇을 잃는가 — B09의 Spring Data 리포지토리와 같은 이야기인가
- [ ] `@Validated` 없이 제약 애노테이션만 붙이면 검사가 되는가 — 웹 요청 본문의 `@Valid`와 메서드 검증은 **다른 기계인가**

## 원문 링크

- https://docs.spring.io/spring-boot/reference/io/index.html
- https://docs.spring.io/spring-boot/reference/io/caching.html
- https://docs.spring.io/spring-boot/reference/io/rest-client.html
- https://docs.spring.io/spring-boot/reference/io/validation.html
