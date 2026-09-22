---
출처: 자동수집(Claude)
작성일: 2026-09-22
성격: 예습자료
tags: [학습, spring]
---

# Spring 예습 - B07 서블릿 웹 애플리케이션

> 예습자료 — 자동 생성, 사용자 미검증. 결론이 아니라 **읽을 범위의 지도**다.
> 기준 버전: Spring Boot 4.1.1

## 이 모듈이 다루는 범위

B07은 공식 문서의 **Reference → Web → Servlet Web Applications** 한 페이지가 통째로 대응한다. 페이지가 크게 세 덩어리로 나뉜다.

| 덩어리 | 문서가 서 있는 자리 |
| --- | --- |
| **The "Spring Web MVC Framework"** | 몸통. 부트가 Spring MVC 위에 **무엇을 자동으로 깔아 주는지**(뷰 리졸버·메시지 컨버터·정적 자원·에러 처리·CORS·API 버전)를 절별로 나열하는 자리 |
| **JAX-RS and Jersey** | MVC 대신 JAX-RS(Jersey·CXF)로 REST를 짜는 **대안** 절 |
| **Embedded Servlet Container Support** | 내장 톰캣/제티에 서블릿·필터·리스너를 **어떻게 등록하고 서버를 어떻게 손보는지** |

핵심 성격: 이 모듈은 "서블릿을 직접 만드는 법"이 아니라 **부트가 서블릿 웹을 대신 구성해 주는 층**을 다룬다. B06(자동설정)에서 본 `@AutoConfiguration`·조건 애노테이션이 여기서 실제로 무엇을 만들어 내는지가 이 페이지의 각 절이다.

- 원문: https://docs.spring.io/spring-boot/reference/web/servlet.html

## 목차 지도

### 1. The "Spring Web MVC Framework"

- **도입** — Spring MVC를 "모델-뷰-컨트롤러" 프레임워크로 소개하고, `@Controller`·`@RestController`·`@RequestMapping`과 함수형 라우팅(`RouterFunction`) 두 방식이 있다고 여는 자리
- **Spring MVC Auto-configuration** — 부트가 기본으로 켜 주는 것들의 목록. `ContentNegotiatingViewResolver`·`BeanNameViewResolver` 등록, 정적 자원·컨버터·포매터 등록. 그리고 `WebMvcConfigurer`로 **더하는** 길과 `@EnableWebMvc`로 **전부 끄고 직접 하는** 길, `WebMvcRegistrations`로 부품을 갈아 끼우는 길을 가르는 절
- **Spring MVC Conversion Service** — MVC의 변환·포맷 서비스가 프로퍼티 파일 변환과 어떻게 다른지. `spring.mvc.format.*`로 날짜·시간 형식을 지정하는 자리
- **HttpMessageConverters** — 요청/응답 본문을 객체로·객체를 본문으로 바꾸는 `HttpMessageConverter`를 부트가 어떻게 기본 세팅하고, 어떻게 추가·교체하는지
- **MessageCodesResolver** — 바인딩 에러 메시지의 에러 코드를 만드는 규칙(`spring.mvc.message-codes-resolver-format`)
- **Static Content** — `classpath:/static`·`/public` 등에서 정적 파일을 내보내는 기본 동작과 경로 규칙(`spring.mvc.static-path-pattern`·`spring.web.resources.*`·WebJars)
- **Welcome Page** — `index.html`(정적)이나 `index` 템플릿을 루트에 자동으로 연결하는 동작
- **Custom Favicon** — 파비콘을 자동으로 찾아 내보내는 자리
- **Path Matching and Content Negotiation** — 요청 경로를 매칭하는 전략(`PathPatternParser` vs `AntPathMatcher`)과, 어떤 미디어 타입으로 응답할지 고르는 협상 규칙(`spring.mvc.contentnegotiation.*`)
- **ConfigurableWebBindingInitializer** — 요청 값을 객체에 바인딩하는 초기화기를 갈아 끼우는 자리(`WebBindingInitializer`)
- **Template Engines** — FreeMarker·Groovy·Thymeleaf·Mustache의 자동설정, 템플릿 위치는 `src/main/resources/templates`
- **Error Handling** — 부트의 기본 에러 처리. `/error` 매핑, `BasicErrorController`, `ErrorAttributes`, 화이트라벨 페이지, `spring.mvc.problemdetails.enabled`로 RFC 7807(Problem Details) 켜기
  - **Custom Error Pages** — 상태 코드별 정적/템플릿 에러 페이지를 두는 규약
  - **Mapping Error Pages Outside of Spring MVC** — MVC를 안 쓸 때 `ErrorPageRegistrar`·`ErrorPage`로 직접 매핑
  - **Error Handling in a WAR Deployment** — WAR로 배포할 때의 에러 처리 차이
- **CORS Support** — 교차 출처 요청 허용. `@CrossOrigin`(지점별)과 `WebMvcConfigurer#addCorsMappings`(전역)
- **API Versioning** — 같은 API의 여러 버전을 다루는 절. 버전을 헤더/파라미터/경로 중 어디서 읽을지(`ApiVersionResolver`), 파싱·기본값·폐기 처리(`spring.mvc.apiversion.*`)

### 2. JAX-RS and Jersey

- MVC 대신 표준 JAX-RS 애노테이션(`@Path`·`@GET`)으로 REST를 짜는 길. Jersey를 서블릿/필터로 등록하는 방식(`ResourceConfig`·`spring.jersey.*`)

### 3. Embedded Servlet Container Support

- **도입** — 내장 톰캣·제티 지원, 기본 포트 8080
- **Servlets, Filters, and Listeners** — 서블릿 부품을 등록하는 두 갈래가 있다는 소개
- **Registering … as Spring Beans** — `ServletRegistrationBean`·`FilterRegistrationBean`·`ServletListenerRegistrationBean`을 빈으로 올려 등록하는 길
- **Servlet Context Initialization** — `ServletContextInitializer`로 컨텍스트 시작 시 초기화 코드를 끼우는 자리
- **Scanning for Servlets, Filters, and Listeners** — `@ServletComponentScan`으로 `@WebServlet`·`@WebFilter`·`@WebListener`를 훑어 등록하는 길(내장 컨테이너에서만)
- **The ServletWebServerApplicationContext** — 서블릿 웹일 때 쓰이는 애플리케이션 컨텍스트 종류
- **Customizing Embedded Servlet Containers** — 서버를 손보는 세 층위 소개(프로퍼티 → 프로그램 → 팩토리 직접)
  - **Programmatic Customization** — `WebServerFactoryCustomizer`로 코드에서 서버 설정을 바꾸기
  - **Customizing ConfigurableServletWebServerFactory** — 팩토리를 직접 만들어 세밀하게 손보기
- **JSP Limitations** — 내장 컨테이너 + 실행 가능한 jar에서 JSP가 갖는 제약

## 핵심 용어

day01에서 이미 본 서블릿·`HttpServlet`·필터·`@WebServlet`은 여기서 뺀다. 이 모듈에서 **처음** 또는 새 맥락으로 나오는 것만.

| 용어 | 한 줄 |
| --- | --- |
| Spring MVC 자동설정 | 부트가 뷰 리졸버·메시지 컨버터·정적 자원 등을 조건에 따라 대신 등록해 주는 것 |
| `WebMvcConfigurer` | 자동설정을 **끄지 않고** 포매터·인터셉터·CORS·자원 핸들러를 더하는 확장 지점 |
| `@EnableWebMvc` | MVC 자동설정을 **전부 끄고** 처음부터 직접 구성하겠다는 선언 |
| `HttpMessageConverter` | 요청/응답 본문 ↔ 자바 객체 변환기 (JSON은 보통 Jackson) |
| `ContentNegotiatingViewResolver` | 요청이 원하는 형식(Accept 헤더·확장자 등)을 보고 뷰를 고르는 리졸버 |
| 콘텐츠 협상(content negotiation) | 같은 URL에 대해 어떤 미디어 타입으로 응답할지 정하는 규칙 |
| `PathPatternParser` / `AntPathMatcher` | 요청 경로를 매칭하는 두 전략 (부트 기본은 앞쪽) |
| 정적 자원(static content) | `classpath:/static` 등에서 코드 없이 그대로 내보내는 파일 |
| 웰컴 페이지 / 파비콘 | 루트 요청에 `index`를, 파비콘 요청에 아이콘을 자동 연결하는 동작 |
| `BasicErrorController` / `/error` | 처리되지 않은 예외를 받아 에러 응답을 만드는 부트 기본 컨트롤러와 그 경로 |
| `ErrorAttributes` | 에러 응답에 담길 필드(상태·메시지·타임스탬프 등)를 정하는 것 |
| `@ControllerAdvice` / `@ExceptionHandler` | 예외를 한곳에서 잡아 응답으로 바꾸는 전역 예외 처리 수단 |
| Problem Details (RFC 7807) | 에러를 표준 JSON 형식으로 내보내는 방식(`spring.mvc.problemdetails.enabled`) |
| `@CrossOrigin` / `CorsRegistry` | 교차 출처 요청을 지점별/전역으로 허용하는 수단 |
| API 버저닝 | 한 API의 버전을 헤더·파라미터·경로로 갈라 다루는 부트 기능 |
| `ServletRegistrationBean` / `FilterRegistrationBean` | 서블릿·필터를 **스프링 빈으로** 등록하는 래퍼 |
| `ServletContextInitializer` | 서블릿 컨텍스트가 뜰 때 초기화 코드를 끼우는 콜백 |
| `WebServerFactoryCustomizer` | 내장 서버(포트·스레드·압축 등)를 코드에서 손보는 확장 지점 |
| `server.*` 프로퍼티 | 포트·세션·SSL·압축·에러 등 내장 서버 설정 키 묶음 |
| Jersey / JAX-RS | Spring MVC 대신 표준 JAX-RS 애노테이션으로 REST를 짜는 대안 |

## 수업에서 안 다뤘을 만한 지점

학습 지도에서 B07은 **복습**(day01 서블릿·HTTP과 대조, ⭐)으로 표시돼 있다. day01(서블릿과 HTTP 메소드) 노트를 읽어 보면, 그 수업은 **날 것의 서블릿 API**에 머문다 — `HttpServlet`을 상속해 `doGet`·`doPost`를 재정의하고, `req.getParameter()`로 값을 꺼내고, `resp.getWriter()`로 HTML/JSON 문자열을 손으로 찍고, `@WebServlet`으로 주소를 붙이는 데까지다. 세션·필터·스코프·멀티스레드 안전성·상태 코드도 서블릿 수준에서 짚었고, 프론트 컨트롤러와 `DispatcherServlet`, `@RestController`는 "이렇게 줄어든다"고 **맛보기로만** 보여 준 상태다.

B07 공식 문서는 정확히 그 **맛보기 뒤쪽**, 즉 **부트가 자동으로 깔아 주는 층**을 다룬다. 대조하면 day01에서 비어 있는 자리들이 이렇다.

- **응답 본문을 손으로 안 찍는다는 것.** day01은 `resp.getWriter().print("{...}")`로 JSON 문자열을 직접 만들었다. B07의 **HttpMessageConverters** 절은 그 변환을 부트가 자동으로 한다고 말한다 — 반환한 객체가 어떻게 JSON이 되는지가 여기 있다. day01 2-2에서 "라이브러리로 변환하는 쪽이 실제 방식"이라고 넘긴 자리가 이 절이다.
- **정적 파일·웰컴 페이지·파비콘.** day01에는 아예 없던 주제다. `classpath:/static`에 파일을 두면 코드 없이 나가고, `index.html`이 루트에 자동 연결된다는 규약을 이 모듈에서 처음 만난다.
- **에러 처리가 자동화돼 있다는 것.** day01은 상태 코드를 `resp.setStatus()`·`sendError()`로 **직접** 지정했다. B07의 **Error Handling** 절은 처리 안 된 예외가 `/error`와 `BasicErrorController`로 흘러 화이트라벨 페이지가 뜨고, `@ControllerAdvice`+`@ExceptionHandler`로 전역에서 잡으며, Problem Details로 표준 형식을 낼 수 있다고 한다. 수업의 수동 상태 코드가 프레임워크 층에서 어떻게 대체되는지가 비어 있다.
- **콘텐츠 협상·경로 매칭 전략.** day01은 "주소 + HTTP 방식으로 분기"까지만 갔다. B07은 그 매칭을 누가(`PathPatternParser`) 하고, 응답 형식을 Accept 헤더로 어떻게 고르는지(content negotiation)를 절로 둔다.
- **템플릿 엔진 자동설정.** day01 3-5는 JSP와 타임리프를 "이런 게 있다"고 언급만 했다. B07은 `src/main/resources/templates`라는 **약속된 위치**와 자동설정을 규정한다 — 위치 규약이 day01에 없다.
- **서블릿을 빈으로 등록하는 길.** day01은 `@WebServlet` + `@ServletComponentScan`만 배웠다. B07은 그 외에 `ServletRegistrationBean`·`FilterRegistrationBean`으로 **빈으로 올려** 순서·URL을 코드로 지정하는 길을 따로 둔다. 두 길의 차이가 대조 지점이다.
- **내장 서버를 손보는 층위.** day01 3-3은 `server.tomcat.threads.max` 한 줄을 보여 줬다. B07은 프로퍼티(`server.*`) → `WebServerFactoryCustomizer`(코드) → 팩토리 직접의 **세 층위**로 정리한다 — 어디까지 프로퍼티로 되고 언제 코드로 내려가는지가 새로 보인다.
- **CORS·API 버저닝·JAX-RS.** 셋 다 day01에 전혀 없던 주제다. 특히 CORS는 프론트가 JSON API를 부르는 구조(day01이 3-5에서 가리킨 방향)로 가면 바로 부딪히는 자리다.
- **`WebMvcConfigurer` vs `@EnableWebMvc`의 갈림.** day01에는 없던, "자동설정을 **더할지 / 전부 끌지**"라는 선택이 B07의 첫 절에 있다. 부트 MVC를 쓰면서 커스터마이즈하는 표준 지점이 어디인지가 핵심.

즉 day01이 "서블릿이 무엇인지"였다면, B07은 "부트가 그 서블릿 웹을 어떻게 대신 차려 주는지"다. **같은 `DispatcherServlet` 뒤에서 자동설정이 무엇을 등록하는지**를 보는 것이 이 대조의 목적이다.

## 학습 세션에서 확인할 것

- [ ] day01에서 손으로 찍던 JSON 응답이, 부트에서는 무엇이 언제 개입해서 객체 → JSON으로 바뀌는가 (`HttpMessageConverter`의 자리)
- [ ] `WebMvcConfigurer`로 확장하는 것과 `@EnableWebMvc`를 붙이는 것은 결과가 어떻게 갈리는가 — 왜 보통은 앞쪽을 쓰는가
- [ ] 처리 안 된 예외가 `/error`까지 흘러가는 경로는 무엇이고, `@ControllerAdvice`로 잡는 것과 `BasicErrorController`가 받는 것은 어디서 갈리는가
- [ ] `@WebServlet`+`@ServletComponentScan`으로 등록하는 것과 `ServletRegistrationBean`으로 빈 등록하는 것은 각각 언제 쓰는가 — day01의 방식은 어느 쪽인가
- [ ] `server.*` 프로퍼티로 안 되는 서버 설정을 만났을 때 `WebServerFactoryCustomizer`로 내려가는 판단 기준은 무엇인가
- [ ] 정적 자원·웰컴 페이지가 "코드 없이" 나가는 것은 어느 자동설정이 무슨 조건으로 등록한 결과인가 (B06의 조건 애노테이션과 이어서)

## 원문 링크

- https://docs.spring.io/spring-boot/reference/web/servlet.html
