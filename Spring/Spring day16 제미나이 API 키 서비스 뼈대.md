---
출처: Claude 분석
원본: KDT_2026/2026B_Spring/springweb/src/main/java/day16, springweb/src/main/resources/application.properties
작성일: 2026-10-12
tags: [학습, java]
---

# Spring day16 제미나이 API 키 서비스 뼈대

> 실습 파일: `day16/AppStart.java`, `LLMService.java`, `LLMController.java`, `DeliveryLogRepository.java`, `DeliveryLog.java`, `1012.sql`
> 허브: [[Spring MOC]] · 이전: [[Spring day15 웹소켓 설정 클래스 뼈대]] · 다음: (아직 없음)

day16은 새 패키지에 진입점을 두고, LLM(대규모 언어 모델) API를 부르는 서비스를 끝까지 만든 시점이다. 설정 파일에서 API 키를 받아 오고, `WebClient`로 Gemini를 호출해 응답에서 본문 텍스트만 뽑는 `LLMCall`이 완성됐다. 그 위에 프롬프트를 그대로 넘기는 `chat1`, DB의 배송 로그를 프롬프트에 붙여 분석 보고서를 받는 `Chat2`가 얹히고, 컨트롤러가 두 경로로 열어 준다.

## 1. 배운 내용

### 1-1. 패키지마다 진입점 두기

```java
package day16;

@SpringBootApplication
public class AppStart {
    public static void main(String[] args) {
        SpringApplication.run(AppStart.class);
    }
}
```

`@SpringBootApplication`이 붙은 클래스의 패키지가 컴포넌트 스캔의 뿌리라서, `day16` 아래의 클래스만 빈으로 등록된다. day04부터 해 온 방식대로 실습 단위마다 진입점을 따로 둔다.

### 1-2. 서비스 클래스와 API 키 주입

```java
@Service
@RequiredArgsConstructor
public class LLMService {

    // 1. 서비스키 불러오기
    @Value("${api.gemini-key}")
    public String geminiApiKey;
}
```

| 항목 | 설명 |
| --- | --- |
| `@Service` | 서비스 계층 빈으로 등록하는 표시 |
| `@RequiredArgsConstructor` | 롬복이 `final` 필드용 생성자를 만들어 주는 애노테이션. 생성자 주입을 쓸 때 짝으로 붙인다 |
| `@Value("${...}")` | `application.properties`에 적어 둔 값을 필드에 넣는다. [[Spring day10 WebClient로 공공데이터 API 대신 호출하기]]에서 공공데이터 서비스키를 받던 방식과 같다 |

키를 코드에 직접 적지 않고 설정 파일에서 읽어 오면, 코드를 공개 저장소에 올려도 키가 새지 않는다.

### 1-3. 호출 도구 필드 세 개

```java
private final WebClient webClient = WebClient.builder().build(); // api 호출 라이브러리
private ObjectMapper objectMapper = new ObjectMapper();          // 직렬화 라이브러리
```

`WebClient`는 HTTP 요청을 보내는 도구이고, `ObjectMapper`는 객체와 JSON을 서로 바꾸는 도구다. 둘 다 서비스 안에서 필드로 하나씩 들고 쓴다.

### 1-4. `LLMCall` — 프롬프트 구성, 호출, 응답 추출

```java
public String LLMCall(String prompt) {
    // 1) 프롬프트 구성
    Map<String, Object> requestBody = Map.of("contents",
            List.of(Map.of("parts",
                    List.of(Map.of("text", prompt)))));
    // 2) WebClient로 LLM API 호출
    Map<String, Object> response = webClient.post()
            .uri(".../v1beta/models/<모델명>:generateContent?key={key}", geminiApiKey)
            .contentType(MediaType.APPLICATION_JSON)
            .bodyValue(requestBody)
            .retrieve().bodyToMono(Map.class)
            .block();
    // 3) 응답에서 text만 추출
    JsonNode root = objectMapper.valueToTree(response);          // Map -> JSON 트리
    JsonNode textNode = root.at("/candidates/0/content/parts/0/text");
    return textNode.asText();
}
```

| 단계 | 설명 |
| --- | --- |
| 요청 본문 | Gemini는 `contents` → `parts` → `text` 순서로 감싼 JSON을 받는다. `Map.of`와 `List.of`를 겹쳐 그 모양을 그대로 만든다 |
| 호출 | `post()` → `uri()` → `contentType()` → `bodyValue()` → `retrieve()` → `bodyToMono(Map.class)` → `block()` 순서. `{key}` 자리에는 두 번째 인자로 준 키가 들어간다 |
| 응답 추출 | 응답 `Map`을 `valueToTree`로 JSON 트리로 바꾸고, `at("/candidates/0/content/parts/0/text")`처럼 경로로 본문 한 칸만 꺼낸다 |

`block()`은 응답이 올 때까지 기다리는 동기 방식이다. [[Spring day10 WebClient로 공공데이터 API 대신 호출하기]]에서 쓴 호출 흐름과 같고, 이번에는 GET 대신 POST로 본문을 실어 보낸다.

### 1-5. `chat1` — 질문 그대로 보내기

```java
public String chat1(String prompt) {
    return LLMCall(prompt);
}
```

받은 프롬프트를 가공 없이 `LLMCall`에 넘기는 가장 단순한 형태다.

### 1-6. `Chat2` — DB 자료와 프롬프트 조합하기

```java
private final DeliveryLogRepository deliveryLogRepository;

public String Chat2() {
    List<DeliveryLog> logList = deliveryLogRepository.findAll();          // 1) 로그 모두 꺼내기
    String jsonContext = objectMapper.writeValueAsString(logList);        // 2) 엔티티 -> JSON
    String prompt = """
            배송 및 반품 로그 데이터이며 데이터들을 분석하여 아래와 같이 보고서 작성하기
            1. 배송 일수가 길거나 반품률이 높은 지점 식별
            2. 파손, 배송 지연, 단순 변심 등 반품 패턴 분석
            3. 배송사 별로 배송(개수,평균,반품비율) 통계
            """ + jsonContext;                                            // 3) 지시문 + DB 자료
    return LLMCall(prompt);
}
```

흐름은 DB 조회 → JSON 문자열 변환 → 지시문 뒤에 이어 붙이기 → `LLMCall`이다. 자바 텍스트 블록(`"""`)으로 여러 줄 지시문을 그대로 적을 수 있고, `writeValueAsString`은 검사 예외를 던지므로 `try`/`catch`로 감싼다. LLM에게 자기 서비스의 데이터를 읽혀 분석시키는 구조다.

### 1-7. 리포지토리와 컨트롤러

```java
public interface DeliveryLogRepository extends JpaRepository<DeliveryLog, Integer> { }

@RestController
@RequiredArgsConstructor
@RequestMapping("/api")
@CrossOrigin(origins = "http://localhost:5173")
public class LLMController {
    private final LLMService llmService;

    @GetMapping("/chat1")
    public String chat1(@RequestParam("promt") String prompt) { return llmService.chat1(prompt); }

    @GetMapping("/chat2")
    public String chat2() { return llmService.Chat2(); }
}
```

`/api/chat1`은 쿼리스트링으로 질문을 받고, `/api/chat2`는 파라미터 없이 DB 분석 결과를 돌려준다. `@CrossOrigin`으로 리액트 개발 서버(5173)의 요청을 허용한다. `@RequestParam`의 이름은 화면에서 보내는 파라미터 이름과 글자까지 같아야 한다.

### 1-8. 분석용 데이터 — `1012.sql`

`delivery_log` 테이블에 주문번호, 배송사, 출발 허브, 배송 일수, 반품 여부, 반품 사유, 일자를 담은 200행짜리 `INSERT` 문이다. 허브·배송사별로 파손 집중, 단순 변심, 신선식품 변질, 정시 배송처럼 성격이 다른 묶음으로 나뉘어 있어, LLM이 패턴을 찾아내기 좋은 자료가 된다. 설정 파일에서는 `spring.sql.init.data-locations`로 이 SQL을 서버 실행 때 적재하도록 잡아 둔다. 엔티티 `DeliveryLog.java`는 파일만 만들어 둔 상태다.

## 2. 추가로 알면 좋은 활용법

### 2-1. 키는 설정 파일 밖으로

`application.properties`에도 실제 키를 적어 두면 같이 올라가기 쉽다. 환경변수로 빼고 `api.gemini-key=${GEMINI_API_KEY}`처럼 참조하거나, 커밋하지 않는 로컬 전용 설정 파일을 따로 두는 편이 안전하다.

### 2-2. 데이터를 통째로 붙일 때의 한계

`findAll()` 결과를 전부 프롬프트에 붙이면 행이 늘수록 길이와 비용이 같이 늘고, 모델의 입력 한도에도 걸린다. 집계를 DB에서 먼저 하고 요약만 넘기거나, 기간·조건으로 줄인 뒤 넘기는 편이 안전하다.

### 2-3. 응답 구조 로그로 확인하기

`System.out.println(response)`로 응답 전체를 먼저 찍어 보면 `candidates[0].content.parts[0].text` 경로가 어디서 나왔는지 눈으로 확인할 수 있다.

## 3. 더 나아가 알면 좋은 것

- Gemini 등 LLM REST API의 요청·응답 JSON 구조
- `@ConfigurationProperties`로 API 설정을 묶어서 받기
- 응답 지연이 긴 호출을 위한 타임아웃·비동기 처리 (`block()` 대신 `Mono`를 그대로 반환하기)
- 요청·응답을 `Map` 대신 DTO 클래스로 받기
- 앞서 본 웹소켓([[Spring day15 웹소켓 설정 클래스 뼈대]])으로 답변을 실시간으로 흘려 보내기

### 다음에 볼 키워드

- `WebClient`, `ObjectMapper`, `@ConfigurationProperties`, 환경변수, 프롬프트 설계, 스트리밍 응답

## 실습 파일

- `KDT_2026/2026B_Spring/springweb/src/main/java/day16/AppStart.java` — day16 진입점
- `.../day16/LLMService.java` — API 키 주입, `LLMCall`, `chat1`, `Chat2`
- `.../day16/LLMController.java` — `/api/chat1`, `/api/chat2`
- `.../day16/DeliveryLogRepository.java` — 배송 로그 JPA 리포지토리
- `.../day16/DeliveryLog.java` — 엔티티 (파일만 생성된 상태)
- `.../day16/1012.sql` — 배송·반품 로그 200행 초기 데이터
- `KDT_2026/2026B_Spring/springweb/src/main/resources/application.properties` — DB 연동, SQL 적재, 키 설정 (키 값은 노트에 적지 않음)

## 관련 노트

[[Spring MOC]] · [[Spring day15 웹소켓 설정 클래스 뼈대]] · [[Spring day10 WebClient로 공공데이터 API 대신 호출하기]] · [[KDT_2026 학습 지도]]
