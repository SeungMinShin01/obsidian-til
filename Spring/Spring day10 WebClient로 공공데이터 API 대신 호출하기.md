---
출처: Claude 분석
원본: KDT_2026/2026B_Spring/springweb/src/main/java/day10
작성일: 2026-09-18
tags: [학습, java]
---

# Spring day10 — WebClient로 공공데이터 API 대신 호출하기

> 실습 파일: `day10/ApiController.java`, `day10/ApiService.java`, `resources/application.properties`
> 허브: [[Spring MOC]] · 이전: [[Spring day10 리뷰 도메인과 쿼리 메소드로 자식 목록 받기]] · 다음: (없음)

지금까지는 내 DB에 있는 데이터를 꺼내 JSON으로 내보냈습니다. 이번에는 방향이 하나 더 늘어납니다. 서버가 **클라이언트 입장이 되어** 바깥 공개 API를 호출하고, 받아 온 결과를 다시 내 API의 응답으로 흘려보내는 자리입니다. 컨트롤러 → 서비스 두 층은 그대로 두고, 서비스 아래가 리포지토리 대신 **HTTP 클라이언트**로 바뀐다고 보면 정리가 쉽습니다.

## 1. 배운 내용

### 1-1. 호출 계층이 하나 늘어난 구조

```
브라우저 ──▶ ApiController ──▶ ApiService ──▶ (HTTP) ──▶ 공공데이터 API
                 @RestController      WebClient
```

컨트롤러는 여전히 주소만 받고 아무 일도 하지 않습니다.

```java
@RestController
@RequiredArgsConstructor
public class ApiController {
    private final ApiService apiService;

    @GetMapping("/test1")
    public Map<String, Object> test1() {
        return apiService.test1();
    }
}
```

| 요소 | 하는 일 |
| --- | --- |
| `@RestController` | 반환값을 뷰 이름이 아니라 응답 본문으로 취급 (`@Controller` + `@ResponseBody`) |
| `@RequiredArgsConstructor` | `final` 필드만 골라 생성자를 만들어 주는 롬북 애노테이션 — 생성자 주입 |
| `private final ApiService` | 주입 대상은 여전히 빈(`@Service`)이고, 그 빈이 DB 대신 바깥 API를 봄 |
| 반환 타입 `Map<String, Object>` | DTO를 따로 만들지 않고 받은 JSON 구조를 그대로 흘려보내는 모양 |

### 1-2. `@Value` — 설정 파일 값을 필드에 꽂기

인증키처럼 **코드에 박으면 안 되는 값**은 `application.properties`에 두고 필드로 읽어 옵니다.

```properties
# application.properties
api.public-data.service-key = ****************
```

```java
@Service
public class ApiService {
    @Value("${api.public-data.service-key}")
    private String serviceKey;
```

| 표기 | 의미 |
| --- | --- |
| `${...}` | 프로퍼티 플레이스홀더 — 중괄호 안이 `properties` 키 이름 |
| `@Value("${a.b.c}")` | 해당 키의 값을 필드에 주입. 키가 없으면 기동 실패 |
| `@Value("${a.b.c:기본값}")` | 콜론 뒤는 키가 없을 때 쓸 기본값 |

주입은 **빈이 만들어질 때** 일어나므로, 이 애노테이션이 붙은 클래스는 반드시 스프링이 관리하는 빈이어야 합니다. `new ApiService()` 로 직접 만든 객체에는 값이 들어오지 않습니다.

키 값 자체는 노트나 저장소에 남기지 않는 편이 안전합니다. 공개 저장소에 인증키가 한 번 올라가면 커밋 이력에 계속 남기 때문에, 실제 프로젝트에서는 환경변수나 `application-local.properties`(gitignore 대상)로 빼는 방식을 씁니다.

### 1-3. `application.properties`에 모인 설정들

이번에 파일을 다시 훑으면서 지금까지 붙여 온 설정이 한자리에 정리됩니다.

| 키 | 뜻 |
| --- | --- |
| `server.port` | 내장 톰캣 포트 (기본 8080) |
| `spring.datasource.url` / `username` / `password` | DB 연결 정보 (비밀번호는 가려 둡니다) |
| `spring.jpa.hibernate.ddl-auto` | `create` · `create-drop` · `update` · `none` — 기동 시 테이블 처리 방식 |
| `spring.jpa.show-sql`, `...format_sql` | 실행 SQL을 콘솔에 보기 좋게 출력 |
| `spring.sql.init.data-locations` | 기동 시 실행할 SQL 파일 경로 (`classpath:` = `resources/`) |
| `spring.jpa.defer-datasource-initialization` | JPA가 테이블을 만든 **뒤에** 초기 SQL을 돌리도록 순서를 미룸 |
| `spring.sql.init.mode`, `...encoding` | 초기화 SQL을 항상 실행, 인코딩 UTF-8 |
| `api.public-data.service-key` | 스프링이 정한 키가 아닌 **내가 만든 키** — `@Value`로만 쓰임 |

`ddl-auto=create-drop` + `data-locations` 조합은 "서버를 켤 때마다 표를 새로 만들고 초기 데이터를 다시 넣는" 실습용 설정입니다. 운영에서는 `none` 또는 `validate`로 두고 스키마는 따로 관리하는 편이 안전합니다.

### 1-4. WebClient로 GET 요청 보내기

```java
String url = "https://api.odcloud.kr/api/…";
url += "?page=1&perPage=10";
url += "&serviceKey=" + serviceKey;

WebClient webClient = WebClient.builder().build();

Map<String, Object> response = webClient.get()
        .uri(url)
        .retrieve()
        .bodyToMono(Map.class)
        .block();
```

메소드 체인이 요청 한 번의 순서를 그대로 따라갑니다.

| 단계 | 하는 일 |
| --- | --- |
| `WebClient.builder().build()` | 클라이언트 객체 생성 (기본 헤더·baseUrl 등을 여기서 미리 지정 가능) |
| `.get()` | HTTP 메소드 선택 — `post()` · `put()` · `delete()`도 같은 자리 |
| `.uri(url)` | 요청 주소 |
| `.retrieve()` | 실제로 요청을 보내고 응답 본문을 받겠다는 선언 |
| `.bodyToMono(Map.class)` | 응답 JSON을 `Map`으로 역직렬화. `Mono`는 "값 0~1개가 나중에 온다"는 그릇 |
| `.block()` | 그 값이 올 때까지 현재 스레드를 세워 두고 기다림 — 결과를 동기로 받음 |

핵심은 **비동기 API를 동기처럼 쓰고 있다**는 점입니다. WebClient는 원래 논블로킹으로 설계된 클라이언트라 결과를 `Mono`/`Flux`로 돌려주고, `block()`은 거기서 값을 꺼내려고 기다리는 탈출구입니다. 지금 단계에서는 이해하기 쉬운 쪽을 택한 것이고, 성능이 걸리는 자리에서는 `Mono`를 그대로 컨트롤러까지 반환하는 방식으로 바꿉니다.

의존성은 `build.gradle`에 `spring-boot-starter-webflux`를 넣어야 `WebClient`를 쓸 수 있습니다. 스타터 이름이 webflux라고 해서 프로젝트 전체가 리액티브가 되는 것은 아니고, MVC와 함께 두고 클라이언트 용도로만 쓰는 조합이 흔합니다.

### 1-5. 인코딩이 두 번 걸리는 문제

공공데이터포털이 내려 주는 인증키는 이미 URL 인코딩된 문자열(`%2B`, `%3D` 같은 것이 섞인 값)입니다. 이 값을 문자열로 이어 붙인 주소를 그대로 넘기면, 클라이언트가 "아직 인코딩 안 된 주소"로 보고 `%`를 한 번 더 인코딩해 `%25…`로 만들어 버립니다. 그러면 서버 쪽에서는 키가 다르다고 판단합니다.

해결 방향은 둘 중 하나입니다.

| 방법 | 내용 |
| --- | --- |
| 이미 인코딩된 값을 쓰는 경우 | `URI.create(url)`로 `URI` 객체를 만들어 `.uri(URI)` 오버로드에 넘겨 재인코딩을 막음 |
| 디코딩된 원본 키를 쓰는 경우 | `UriComponentsBuilder`나 `.uri(builder -> builder.queryParam(...))`로 넘겨 인코딩을 한 번만 맡김 |

둘을 섞는 것이 사고의 원인이라, **키를 어느 형태로 보관할지 먼저 정하고 그에 맞는 한 가지 경로만 쓰는 편**이 안전합니다.

### 1-6. `Map.class`와 제네릭 소거

`bodyToMono(Map.class)`로 받으면 컴파일러가 `Mono<Map>`까지만 알고 `<String, Object>`는 모릅니다. 타입이 확인되지 않았다는 경고가 붙는 이유입니다. 제네릭 타입 정보를 살려서 받으려면 `ParameterizedTypeReference`를 씁니다.

```java
Map<String, Object> response = webClient.get()
        .uri(URI.create(url))
        .retrieve()
        .bodyToMono(new ParameterizedTypeReference<Map<String, Object>>() {})
        .block();
```

`new ...<>() {}` 끝의 중괄호는 익명 하위 클래스를 만드는 표기입니다. 자바 제네릭은 실행 시점에 타입이 지워지지만(타입 소거), 클래스를 상속하면 상위 타입 인자는 클래스 정보에 남기 때문에 이 우회로가 성립합니다. `클래스명.class`가 리플렉션으로 클래스 정보를 얻는 표기라는 것도 같은 맥락에서 같이 정리해 둡니다.

## 2. 추가로 알면 좋은 활용법

### 2-1. WebClient를 빈으로 꺼내 두기

메소드마다 `WebClient.builder().build()`를 호출하면 커넥션 풀이 매번 새로 생깁니다. 보통은 설정 클래스에서 한 번 만들어 주입받습니다.

```java
@Configuration
public class WebClientConfig {
    @Bean
    public WebClient publicDataClient(WebClient.Builder builder) {
        return builder
                .baseUrl("https://apis.data.go.kr")
                .defaultHeader(HttpHeaders.ACCEPT, MediaType.APPLICATION_JSON_VALUE)
                .build();
    }
}
```

`baseUrl`을 잡아 두면 서비스 쪽에는 `/B552657/…` 같은 경로만 남아 주소 조립이 짧아집니다.

### 2-2. 쿼리 파라미터를 문자열이 아니라 빌더로

```java
.uri(uriBuilder -> uriBuilder
        .path("/api/15052602/v1/uddi:…")
        .queryParam("page", 1)
        .queryParam("perPage", 10)
        .queryParam("serviceKey", serviceKey)
        .build())
```

`+=`로 이어 붙이면 `?`와 `&`, `=` 를 손으로 맞춰야 해서 한 글자만 빠져도 조용히 잘못된 주소가 만들어집니다. 빌더는 그 조립을 대신해 주고, 값에 특수문자가 들어가도 인코딩 규칙을 한 곳에서 관리할 수 있습니다.

### 2-3. 응답을 Map 대신 DTO로 받기

`Map`으로 받으면 `response.get("data")`처럼 문자열 키로 꺼내야 하고, 오타가 컴파일 시점에 안 잡힙니다. 자주 쓰는 응답이라면 필요한 필드만 담은 DTO를 만들어 두는 편이 낫습니다.

```java
public record PharmacyResponse(
        @JsonProperty("currentCount") int currentCount,
        @JsonProperty("data") List<PharmacyDto> data) {}
```

`@JsonIgnoreProperties(ignoreUnknown = true)`를 붙이면 안 쓰는 필드가 더 와도 그냥 무시합니다. DB 엔티티를 DTO로 펴서 내보내던 흐름과 방향만 반대일 뿐 같은 이야기입니다.

### 2-4. 응답 형식이 XML인 경우

공공데이터 API 중에는 기본 응답이 XML인 것이 많습니다. 대부분 `_type=json` 또는 `dataType=JSON` 파라미터를 붙이면 JSON으로 바뀌고, 그렇지 않으면 `bodyToMono(String.class)`로 원문을 받아 따로 파싱해야 합니다. 어떤 형식이 오는지는 호출해 보기 전에 문서에서 확인해 두는 편이 시간을 아낍니다.

### 2-5. 실패를 응답으로 갈라 주기

바깥 API는 내 통제 밖이라 언제든 실패합니다. 상태 코드에 따라 처리를 갈라 두면 원인을 빨리 찾습니다.

```java
.retrieve()
.onStatus(HttpStatusCode::is4xxClientError,
        res -> Mono.error(new IllegalArgumentException("요청 값이나 인증키를 확인")))
.onStatus(HttpStatusCode::is5xxServerError,
        res -> Mono.error(new IllegalStateException("공공데이터 서버 쪽 오류")))
.bodyToMono(...)
```

`.timeout(Duration.ofSeconds(5))`를 함께 걸면 상대가 응답하지 않을 때 내 서버까지 같이 멈추는 것을 막습니다.

## 3. 더 나아가 알면 좋은 것

### 3-1. RestTemplate · WebClient · RestClient

| 클라이언트 | 성격 |
| --- | --- |
| `RestTemplate` | 동기·블로킹. 오래 쓰였지만 유지보수 모드 |
| `WebClient` | 논블로킹. `Mono`/`Flux` 반환, `block()`으로 동기처럼도 사용 |
| `RestClient` | 스프링 6.1에서 추가. WebClient 스타일의 체인을 동기로 쓰는 쪽 |

동기로만 쓸 거라면 `RestClient`가 표기와 동작이 맞아떨어집니다. `WebClient` + `block()`은 그 사이에 있는 선택입니다.

### 3-2. Mono와 Flux

`Mono<T>`는 값이 0~1개, `Flux<T>`는 0~N개 흘러오는 그릇입니다. 값을 담고 있는 게 아니라 **값이 나중에 온다는 약속**이라, `map`·`flatMap`으로 "오면 이렇게 처리해라"를 미리 적어 두고 구독 시점에 실행됩니다. `block()`은 그 흐름을 끊고 결과를 꺼내는 동작이라, 논블로킹 스레드에서 호출하면 예외가 납니다.

### 3-3. 프록시 서버로서의 백엔드

화면에서 바로 공공 API를 부르지 않고 서버를 한 번 거치게 하는 데는 이유가 있습니다.

- 인증키를 브라우저에 노출하지 않음 (화면 코드는 누구나 볼 수 있음)
- 브라우저의 CORS 제약을 피함 (서버 간 호출에는 CORS가 없음)
- 응답을 내 화면에 맞는 형태로 가공하고 캐싱할 수 있음

앞서 `@CrossOrigin`으로 화면을 열어 줬던 이야기와 짝이 되는 자리입니다.

### 3-4. 캐싱과 호출 제한

공공 API는 대개 일일 호출 한도가 있습니다. 자주 바뀌지 않는 데이터는 `@Cacheable`로 메모리에 담아 두거나, 스케줄러(`@Scheduled`)로 하루 한 번 받아 내 DB에 적재한 뒤 화면은 내 DB만 보게 하는 방식이 흔합니다. 이렇게 하면 상대 서버가 잠깐 죽어도 화면은 계속 뜹니다.

### 3-5. 다음에 볼 키워드

- `RestClient` — 동기 호출을 위한 최신 표기
- `WebClient.Builder` · `ExchangeFilterFunction` — 공통 헤더·로깅 필터
- `UriComponentsBuilder` · `encode()` — 인코딩을 한 번만 걸기
- `@ConfigurationProperties` — 설정 키 묶음을 객체로 받기 (`@Value` 여러 개 대신)
- `@JsonProperty` · `@JsonIgnoreProperties` — 외부 JSON을 DTO에 맞추기
- `Mono` · `Flux` · `subscribe()` — 리액티브 스트림의 기본 연산
- `@Cacheable` · `@Scheduled` — 외부 호출 횟수 줄이기
- `Resilience4j` — 재시도·서킷 브레이커
- 환경별 설정 분리 — `application-{profile}.properties`, `spring.profiles.active`

## 실습 파일

- `2026B_Spring/springweb/src/main/java/day10/ApiController.java` (**바깥 API용 컨트롤러** — `@GetMapping("/test1")`·`/test2` 두 주소를 열고 몸통은 서비스 호출 한 줄만 두는 모양, 반환 타입이 엔티티·DTO가 아니라 `Map<String, Object>`인 점)
- `2026B_Spring/springweb/src/main/java/day10/ApiService.java` (**`@Value`로 인증키 주입 + WebClient 호출** — `WebClient.builder().build()` → `.get().uri().retrieve().bodyToMono(Map.class).block()` 체인, 이미 인코딩된 키를 그대로 이어 붙일 때 `URI.create`로 재인코딩을 막는 이유, `클래스명.class`가 리플렉션 표기라는 메모)
- `2026B_Spring/springweb/src/main/resources/application.properties` (**설정 키 총정리** — 포트·데이터소스·`ddl-auto`·`show-sql`·초기 SQL 실행 순서와, 스프링이 정한 키가 아닌 내가 만든 키(`api.public-data.service-key`)를 `@Value`로 읽는 구조)

## 관련 노트

[[Spring MOC]] · [[Spring day10 리뷰 도메인과 쿼리 메소드로 자식 목록 받기]] · [[KDT_2026 학습 지도]]
