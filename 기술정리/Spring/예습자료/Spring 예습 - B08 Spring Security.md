---
출처: 자동수집(Claude)
작성일: 2026-09-23
성격: 예습자료
tags: [학습, spring]
---

# Spring 예습 - B08 Spring Security

> 예습자료 — 자동 생성, 사용자 미검증. 결론이 아니라 **읽을 범위의 지도**다.
> 기준 버전: Spring Boot 4.1.1

## 이 모듈이 다루는 범위

B08은 공식 문서에서 **한 페이지가 아니라 세 페이지에 흩어져 있다.** 문서가 "웹을 지키는 이야기"와 "범용 보안 프로토콜 이야기"를 일부러 갈라 놓았기 때문이다.

| 문서 위치 | 그 페이지가 서 있는 자리 |
| --- | --- |
| **Reference → Web → Spring Security** | 몸통. 클래스패스에 스프링 시큐리티가 들어오면 **부트가 기본으로 무엇을 켜는지**, 그리고 그 기본을 **어떻게 비키게 하는지** |
| **Reference → Security → OAuth2** | 클라이언트 / 리소스 서버 / 인가 서버 **세 역할**의 자동설정과 프로퍼티 |
| **Reference → Security → SAML 2.0** | 기업 간 SSO 규격인 SAML의 **Relying Party** 설정과 빌드 준비 |

> 문서 자체가 첫머리에서 갈라 준다 — 웹 애플리케이션을 지키려는 사람은 Web 쪽 페이지로, OAuth2·SAML 같은 범용 보안 기능을 찾는 사람은 Security 쪽으로 가라고 한다. B08을 읽을 때 **지금 내가 어느 질문을 하고 있는지**를 먼저 정하는 편이 길을 덜 잃는다.

이 모듈의 성격은 B06·B07의 연장선이다. B06이 "자동설정이 무엇을 조건부로 등록하는가"였고 B07이 "그래서 웹 계층에 무엇이 깔리는가"였다면, B08은 **그 앞단에 필터 체인이 하나 더 끼어들었을 때 무슨 일이 벌어지는지**다. 문서의 상당 부분이 기능 설명이 아니라 **"자동설정이 언제 물러나는지(back off)"** 의 조건을 말하는 데 쓰인다.

- 원문: https://docs.spring.io/spring-boot/reference/web/spring-security.html

## 목차 지도

### 1. Spring Security (Web)

- **도입** — 스프링 시큐리티가 클래스패스에 있으면 웹 애플리케이션이 **기본으로 잠긴다**는 선언. 부트의 `/error` 엔드포인트까지 포함해서 잠긴다는 점, 그리고 HTTP Basic으로 갈지 폼 로그인으로 갈지를 **콘텐츠 협상 전략**으로 고른다는 점을 여는 자리 (B07의 content negotiation이 여기서 다시 쓰인다)
- **기본으로 제공되는 것** — 문서가 세 가지를 나열한다: 인메모리 사용자 하나를 담은 `UserDetailsService`(리액티브면 `ReactiveUserDetailsService`), 애플리케이션 전체(액추에이터 엔드포인트 포함)에 걸리는 폼 로그인 또는 HTTP Basic, 인증 이벤트를 발행하는 `DefaultAuthenticationEventPublisher`
- **기본 사용자와 생성 비밀번호** — 사용자명은 `user`, 비밀번호는 시작할 때마다 무작위로 만들어져 **WARN 레벨 로그로 찍힌다**는 동작. 로그 문구 자체가 "개발용이며 운영 전에 보안 설정을 바꾸라"고 말한다. `spring.security.user.name`·`spring.security.user.password`로 덮어쓰는 자리
- **MVC Security** — 기본 구성이 어느 자동설정 클래스에 들어 있는지(`SecurityAutoConfiguration`·`UserDetailsServiceAutoConfiguration`·`SpringBootWebSecurityConfiguration`)와, **무엇을 빈으로 올리면 무엇이 물러나는지**의 규칙
  - `SecurityFilterChain` 빈을 올리면 → 기본 보안 구성이 꺼진다 (단 `UserDetailsService`는 남는다)
  - `UserDetailsService`·`AuthenticationProvider`·`AuthenticationManager` 중 하나를 올리면 → 기본 사용자까지 꺼진다
  - `spring-security-oauth2-client`·`spring-security-oauth2-resource-server`·`spring-security-saml2-service-provider` 가 클래스패스에 있으면 → 자동설정이 물러난다
  - 접근 규칙을 쓸 때 경로 문자열 대신 쓰는 매처: 액추에이터용 `EndpointRequest`, 정적 자원용 `PathRequest`
- **WebFlux Security** — 리액티브 쪽의 같은 구조. `ReactiveWebSecurityAutoConfiguration`·`ReactiveUserDetailsServiceAutoConfiguration`, 끄는 스위치는 `WebFilterChainProxy` 빈, 사용자까지 끄려면 `ReactiveUserDetailsService`·`ReactiveAuthenticationManager`. 규칙은 `SecurityWebFilterChain`과 `ServerHttpSecurity`로 쓴다
- **메소드 보안** — `@EnableMethodSecurity`를 붙여 메소드 단위 인가로 내려가는 자리 (여기서는 한 줄 언급이고, 상세는 스프링 시큐리티 본문서로 넘긴다)
- **OAuth2 / SAML 2.0** — 두 절 모두 "이런 것이 있다"만 말하고 Security 레퍼런스로 넘기는 **문지방** 절

### 2. Security → OAuth2

- **도입** — OAuth2를 인가 프레임워크로 소개
- **Client** — 우리 애플리케이션이 **남의 인증을 빌려 쓰는** 역할. `spring.security.oauth2.client.registration.*`(우리가 등록한 클라이언트)와 `spring.security.oauth2.client.provider.*`(상대 제공자)의 두 갈래 프로퍼티, `OAuth2ClientProperties`, 로그인 필터(`OAuth2LoginAuthenticationFilter`), 승인된 클라이언트를 어디에 담아 둘지(`InMemoryOAuth2AuthorizedClientService`·`JdbcOAuth2AuthorizedClientService`)
- **OAuth2 Client Registration for Common Providers** — 구글·깃허브·페이스북·X·Okta는 **기본값이 미리 들어 있어** 등록을 짧게 쓸 수 있다는 자리
- **Resource Server** — 우리 애플리케이션이 **토큰을 검사하는** 역할. 토큰을 스스로 뜯어 보는 JWT 길(`spring.security.oauth2.resourceserver.jwt.*`, `JwtDecoder`)과 발급자에게 물어보는 불투명 토큰 길(`...opaquetoken.*`, `OpaqueTokenIntrospector`)로 갈린다
- **Authorization Server** — 우리 애플리케이션이 **토큰을 발급하는** 역할. `spring.security.oauth2.authorizationserver.client.*`, `RegisteredClientRepository`(인메모리·JDBC), `AuthorizationServerSettings`, 서명 키(`JWKSource`)

### 3. Security → SAML 2.0

- **도입** — 기업 간에 보안 정보를 주고받는 규격이라는 소개
- **Build Configuration / Using Maven / Using Gradle** — OpenSAML 라이브러리가 필요해 **Shibboleth 저장소를 빌드 파일에 추가**해야 한다는, 코드가 아니라 빌드 쪽 준비 절 (B02의 빌드 시스템과 이어진다)
- **Relying Party** — `spring-security-saml2-service-provider`가 클래스패스에 있을 때의 설정. `spring.security.saml2.relyingparty.registration.*` 아래에 서명 자격증명·복호화 자격증명·단일 로그아웃·상대편(asserting party)의 entity-id와 SSO URL을 적는 자리

## 핵심 용어

| 용어 | 한 줄 |
| --- | --- |
| 필터 체인(`SecurityFilterChain`) | 요청이 컨트롤러에 닿기 전에 통과하는 보안 필터들의 묶음이자, 그것을 정의하는 빈 타입 |
| `HttpSecurity` / `ServerHttpSecurity` | 그 체인을 어떻게 구성할지 적는 빌더 (앞은 MVC, 뒤는 WebFlux) |
| `UserDetailsService` | 사용자명으로 사용자 정보를 찾아오는 창구. 부트 기본은 인메모리 사용자 하나 |
| `AuthenticationManager` / `AuthenticationProvider` | 인증 시도를 처리하는 상위 진입점과, 실제 검증 방식 하나하나 |
| 인증(authentication) / 인가(authorization) | "누구인가"를 가리는 일과 "그것을 해도 되는가"를 가리는 일 — 문서가 절을 나누는 축 |
| 생성 비밀번호 | 기본 사용자에게 시작마다 무작위로 부여되어 WARN 로그에 찍히는 개발용 비밀번호 |
| back off(물러남) | 사용자가 특정 빈이나 모듈을 두면 자동설정이 스스로 비키는 동작 — B06의 조건 애노테이션이 만드는 결과 |
| `EndpointRequest` / `PathRequest` | 경로 문자열 대신 액추에이터 엔드포인트·정적 자원을 가리키는 요청 매처 |
| `@EnableMethodSecurity` | 메소드 단위로 인가 검사를 켜는 선언 |
| `DefaultAuthenticationEventPublisher` | 인증 성공·실패를 스프링 이벤트로 흘려보내는 기본 발행기 (B03의 이벤트 구조와 이어진다) |
| OAuth2 | 비밀번호를 넘기지 않고 제3자에게 권한을 위임하는 인가 프레임워크 |
| 클라이언트 / 리소스 서버 / 인가 서버 | OAuth2에서 우리 애플리케이션이 맡을 수 있는 세 역할 — 빌려 쓰는 쪽 / 검사하는 쪽 / 발급하는 쪽 |
| registration vs provider | OAuth2 클라이언트 설정의 두 축: 우리가 등록한 클라이언트 정보와, 상대 제공자의 엔드포인트 정보 |
| JWT / 불투명 토큰(opaque token) | 토큰 자체에 정보가 담겨 스스로 검증 가능한 것과, 내용을 알 수 없어 발급자에게 물어봐야 하는 것 |
| `JwtDecoder` / `OpaqueTokenIntrospector` | 위 두 검증 방식에 각각 대응하는 부품 |
| `RegisteredClientRepository` | 인가 서버가 "어떤 클라이언트를 아는지" 담아 두는 저장소 |
| SAML 2.0 | XML 기반으로 기업 간 SSO 정보를 교환하는 규격 |
| Relying Party / Asserting Party | SAML에서 인증을 **의지하는 쪽**(우리)과 인증을 **주장해 주는 쪽**(IdP) |
| OpenSAML / Shibboleth 저장소 | SAML 구현 라이브러리와, 그것이 올라와 있어 빌드 파일에 추가해야 하는 저장소 |

## 처음 보는 개념

학습 지도에서 B08은 **⭐ 신규** — `Spring/` 구역 day01~day08 어디에도 대응하는 수업이 없다. 수업에서는 로그인을 세션과 직접 만든 필터·인터셉터로 다뤘을 뿐, 스프링 시큐리티라는 **별도의 필터 체인 층**은 등장하지 않는다. 따라서 이 모듈은 대조가 아니라 **처음 세우는 지도**에 가깝다. 특히 다음이 새 지점이다.

- **"아무것도 안 했는데 잠긴다"는 출발점.** 이 문서는 기능을 켜는 법이 아니라 **이미 켜져 있는 것을 다루는 법**으로 시작한다. 의존성을 넣은 순간 전부 잠기고 로그에 비밀번호가 찍히는 상태에서 읽기 시작한다는 것이 다른 모듈과 다르다.
- **끄는 법이 곧 설정하는 법이라는 구조.** 문서의 MVC/WebFlux 절은 대부분 "무엇을 빈으로 올리면 무엇이 물러나는가"다. `SecurityFilterChain`을 올리면 보안 구성만 꺼지고 사용자는 남는다 — 이 **부분적으로 물러남**이 B06에서 본 조건 애노테이션의 구체적 사례다.
- **보안이 요청 처리보다 앞선다는 위치 감각.** B07에서 본 `DispatcherServlet`·`/error`·정적 자원이 전부 보안 필터 **뒤쪽**에 있다. 그래서 `/error`까지 잠긴다는 도입부 한 줄과, 액추에이터·정적 자원에 별도 매처(`EndpointRequest`·`PathRequest`)가 필요한 이유가 같은 사실의 두 얼굴이다.
- **MVC와 WebFlux가 서로 다른 타입 이름을 쓴다는 것.** `SecurityFilterChain`↔`SecurityWebFilterChain`, `HttpSecurity`↔`ServerHttpSecurity`처럼 이름이 한 칸씩 다르다. 검색할 때 엉뚱한 예제를 집어 오기 쉬운 자리다.
- **OAuth2를 "기능"이 아니라 "역할"로 나눈다는 것.** 문서가 클라이언트·리소스 서버·인가 서버로 절을 나눈다. 같은 OAuth2라도 우리 애플리케이션이 어느 자리에 서느냐에 따라 읽을 절과 프로퍼티 묶음이 완전히 갈린다.
- **SAML은 코드보다 빌드·인증서 이야기가 먼저라는 것.** Shibboleth 저장소 추가와 인증서·개인키 경로 지정이 절의 대부분이다. 다른 모듈에 없던 종류의 준비 작업이다.
- **이 페이지가 일부러 얇다는 것.** 메소드 보안·OAuth2 상세·SAML 상세를 모두 스프링 시큐리티 본 문서로 넘긴다. B08은 **부트가 관여하는 경계선**까지만 그린 지도이고, 그 밖은 다른 문서라는 사실 자체가 읽을 때의 정보다.

## 학습 세션에서 확인할 것

- [ ] 의존성만 추가했을 때 잠기는 범위는 정확히 어디까지인가 — `/error`와 정적 자원, 액추에이터는 각각 어느 쪽에 들어가는가
- [ ] `SecurityFilterChain` 빈 하나를 올렸을 때 **꺼지는 것과 남는 것**은 무엇이고, 기본 사용자까지 없애려면 무엇을 더 올려야 하는가
- [ ] 보안 필터 체인은 B07에서 본 `DispatcherServlet`·`FilterRegistrationBean`과 실행 순서상 어디에 놓이는가
- [ ] OAuth2에서 우리 애플리케이션이 클라이언트일 때와 리소스 서버일 때, 읽어야 할 프로퍼티 묶음과 부품은 어떻게 갈리는가
- [ ] JWT 검증과 불투명 토큰 인트로스펙션은 각각 무엇을 근거로 토큰을 믿는가 — 선택 기준은 무엇인가
- [ ] `spring.security.user.password`로 비밀번호를 고정하는 것이 왜 개발용에 그치는가 — 운영에서는 무엇이 그 자리를 대신하는가

## 원문 링크

- https://docs.spring.io/spring-boot/reference/web/spring-security.html
- https://docs.spring.io/spring-boot/reference/security/index.html
- https://docs.spring.io/spring-boot/reference/security/oauth2.html
- https://docs.spring.io/spring-boot/reference/security/saml2.html
