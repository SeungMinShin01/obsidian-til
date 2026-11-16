---
출처: Claude 대화
작성일: 2026-11-15
tags: [프로젝트, java]
---

# AiOps - LLM 호출 창구 LlmClient

> 허브: [[AiOps 프로젝트 MOC]]

**PR #49 `[AI-54] LLM 호출 창구 (LlmClient + OpenAI 호환 구현)`** — 브랜치 `feat/server-AI-54-llm-client`. 파일 11개(코드 6, 테스트 2, 설정 3), 파일 하나에 커밋 하나. 11/15 머지. 7단계(LLM)의 첫 작업. 아직 이 창구를 **부르는 코드는 없다**(연결은 AI-56).

## 1. 배운 내용

### 1-1. 이 PR이 하는 일

```
(AI-56에서) ExplanationService
   └ LlmClient.complete(LlmPrompt(system, user))  → Optional<String>
        ├ OpenAiCompatibleLlmClient  키·주소·모델이 모두 있을 때
        │    POST {base-url}/chat/completions  (Bearer 키, temperature 0.2, max_tokens 800)
        └ FakeLlmClient              하나라도 없을 때 (로컬·테스트, "(가짜 응답)" 고정 문장)
```

나머지 서버 코드는 `LlmClient` 인터페이스만 안다. 어느 회사 LLM인지는 설정(주소·모델)이 정한다.

### 1-2. 코드로 보기: 실패는 예외가 아니라 empty

```java
try {
    Map<?, ?> response = rest.post().uri("/chat/completions").body(body).retrieve().body(Map.class);
    return contentOf(response);                                   // ①
} catch (RestClientResponseException e) {
    log.warn("LLM 호출 실패 status={}", e.getStatusCode().value());   // ② 상태 코드만
} catch (ResourceAccessException e) {
    log.warn("LLM 호출 실패 (연결·타임아웃)");
} catch (RuntimeException e) {
    log.warn("LLM 응답 처리 실패 {}", e.getClass().getSimpleName());
}
return Optional.empty();                                          // ③
```

| 번호 | 이유 |
|---|---|
| ① | `choices[0].message.content`만 꺼낸다. 모양이 다르거나 공백이면 empty |
| ② | 로그에 **요청·응답 본문과 헤더를 남기지 않는다.** 프롬프트에는 팀의 에러 메시지가, 헤더에는 키가 있다 |
| ③ | 설명이 없어도 알림은 가야 한다. 부르는 쪽이 try/catch를 안 써도 되게. 재시도는 여기서 안 하고 재처리 스케줄러가 한다 |

응답을 record가 아니라 `Map`으로 받고 `instanceof` 패턴으로 한 단계씩 확인했다. 기존 `DiscordApiClient`와 같은 방식이고, LLM 회사마다 응답에 다른 필드가 붙어도 깨지지 않는다.

```java
if (!(response.get("choices") instanceof List<?> choices) || choices.isEmpty()) return Optional.empty();
if (!(choices.get(0) instanceof Map<?, ?> first)) return Optional.empty();
```

`!(x instanceof T t)`로 걸러서 return하면 그 아래 줄에서 `t`를 쓸 수 있다(Java 17 흐름 범위).

### 1-3. 코드로 보기: 구현 고르기 — 조건부 Bean의 함정

명세는 `@ConditionalOnProperty("aiops.llm.api-key")`였다. 그런데 yml이 이렇다.

```yaml
api-key: ${AIOPS_LLM_API_KEY:}     # 환경변수가 없으면 "빈 문자열"
```

- `${이름:기본값}`: 환경변수가 있으면 그 값, 없으면 콜론 뒤. 콜론 뒤가 비면 **빈 문자열**이다.
- 속성 자체는 "있다". `@ConditionalOnProperty`는 값이 `false`만 아니면 통과 → **빈 키로 실구현이 등록**된다.
- `@ConditionalOnMissingBean`도 일반 `@Configuration`에서는 Bean 등록 순서에 따라 결과가 달라질 수 있다.

그래서 메서드 하나에서 직접 골랐다.

```java
@Bean
public LlmClient llmClient(LlmProperties properties) {
    if (!properties.isConfigured()) {        // 키·주소·모델 중 하나라도 비면
        return new FakeLlmClient();
    }
    return new OpenAiCompatibleLlmClient(builder(properties).build(), properties);
}
```

Spring 없이 `new LlmConfig().llmClient(props)`로 테스트할 수 있다는 덤도 있다.

### 1-4. 코드로 보기: LlmProperties

```java
@ConfigurationProperties("aiops.llm")
public record LlmProperties(String apiKey, String baseUrl, String model, Duration timeout) {
    public LlmProperties {                                   // 컴팩트 생성자: 값 다듬기
        if (timeout == null) timeout = DEFAULT_TIMEOUT;       // 20초
        if (baseUrl != null && baseUrl.endsWith("/")) baseUrl = baseUrl.substring(0, baseUrl.length() - 1);
    }
    @Override public String toString() { ... apiKey=*** ... }   // 로그·예외 메시지로 키가 새지 않게
}
```

- yml의 `aiops.llm.api-key` → `apiKey` 칸으로 들어간다(이름을 자동으로 맞춰 준다).
- 주소 끝의 `/`를 떼는 이유: `baseUrl + "/chat/completions"`가 `//`가 되지 않게.
- record의 `toString`은 기본으로 모든 칸을 찍는다. 비밀값이 있으면 **반드시 덮어쓴다**(`DiscordProperties`와 같은 규칙).

### 1-5. RestClient를 Bean으로 내놓지 않은 이유

`RestClient`에 `Authorization: Bearer <키>`가 기본 헤더로 들어 있다. Bean이면 다른 코드가 주입받아 엉뚱한 주소로 키를 보낼 수 있다. `LlmConfig.builder(props)`(static)로만 만들고, 테스트는 그 Builder에 `MockRestServiceServer`를 붙인다 → **실제 설정 그대로**(주소·헤더) 요청 모양을 검사한다.

### 1-6. 테스트 12개

| 파일 | 본 것 |
|---|---|
| `OpenAiCompatibleLlmClientTest` (8) | 정상 응답 + 요청 모양(Bearer, model, messages 2개와 role·content, temperature 0.2, max_tokens 800) / 500 / 401 / 타임아웃(`withException(SocketTimeoutException)`) / choices 비어 있음 / content 공백 / JSON 아님 / 프롬프트 null이면 호출 0회 |
| `LlmConfigTest` (4) | 키 없으면 가짜 / 있으면 실구현 / toString에 키 없음 / 타임아웃 기본값·슬래시 제거 |

전부 키 없이 돈다. 가짜 서버가 요청을 받아 주므로 네트워크도 필요 없다.

## 2. 설계와 다르게 한 곳

| 명세 (AI-54) | 실제 | 이유 |
|---|---|---|
| 조건부 Bean 2개로 구현 선택 | `@Bean` 메서드 하나에서 선택 | 빈 문자열 키가 조건을 통과함 (1-3) |
| 설정 읽는 방식 명시 없음 | `LlmProperties` record 추가 | 기존 방식과 통일, 키 가림 |
| `RestClient` Bean | Bean 아님 | 인증 헤더가 든 객체 (1-5) |
| 기본 주소·모델 언급 없음 | Gemini의 OpenAI 호환 주소·Flash 모델 | D-101 |
| 컨텍스트 테스트로 Bean 확인 | 단위 테스트 | Spring을 띄울 필요가 없어짐 |

## 3. 같이 정한 것 (결정 기록)

- **D-101**: Gemini로 시작, 다른 조를 받는 운영 전에 유료 등급으로. 코드는 주소·모델 환경변수만 바꾸면 된다.
- 프롬프트는 원인 후보 2~3개 제시 (AI-55). 그룹 지문에 줄 번호·메시지가 없어서 한 그룹에 다른 원인이 섞일 수 있기 때문.
- 비용 감각: 설명은 **새 그룹이 생길 때만** 1회. 저가 모델 기준 1건 1원 안팎, 10개 팀이면 월 2달러 안쪽(추정). 폭주는 AI-57 일일 상한 + 서비스 콘솔의 월 한도로 막는다.

## 4. 사고와 팁

| 증상 | 원인 | 해결 |
|---|---|---|
| 11개 중 2개만 커밋됨 | PowerShell 변수 두 줄(`$S=…`, `$T=…`)을 한 줄에 붙여 넣어 변수가 비었다 → `git add /client/…` 실패 → `git commit`은 "커밋할 것 없음"으로 조용히 넘어감. 경로를 직접 쓴 파일만 성공 | 전체 경로로 다시 커밋. **커밋 뒤 `git status --short`와 `git log --oneline develop..HEAD`로 개수를 센다** |
| `.env`가 없다 | 원래 레포에 없는 파일(`.gitignore`). `bootRun`은 `.env`를 읽지도 않는다 | 로컬은 없어도 뜬다(값이 비면 건너뛰게 돼 있음). 키가 필요하면 서버를 띄우는 **같은 터미널**에서 `$env:AIOPS_LLM_API_KEY="…"` |
| `.env.example`에 빈 값으로 두면 | `AIOPS_LLM_BASE_URL=`처럼 정의하면 기본값이 아니라 **빈 값**이 된다 | 기본값과 다를 때만 쓰는 줄은 주석으로 둔다 |

용어 메모
- `/** … @param 이름 설명 */`: Javadoc 주석. 실행과 무관하고 IDE 툴팁에 뜬다. record는 칸 설명을 클래스 위 `@param`으로 적는다.
- `application.yml`: 서버 설정 파일. 들여쓰기가 문법(탭 금지). `application-local.yml`이 그 위에 덮어쓴다(프로필).

## 5. 남은 것

- 실제 키로 1회 호출 (AI-56 연결 뒤). 응답이 `max_tokens: 800`에서 잘리는지, 일부 최신 모델이 `max_tokens` 이름을 거부하는지 확인
- 운영에서 키를 빠뜨리면 알림에 "(가짜 응답)"이 실린다 → 운영은 설명 없이 보낼지 AI-56에서 결정
- D-096: LLM이 붙기 전에 처리 풀의 `CallerRunsPolicy`를 거절로(A), LLM은 별도 풀로(B)

## 관련 노트

[[AiOps 31 - JsonWriter HEX 표 버그 수정]] · [[AiOps 33 - 프롬프트 조립 PromptBuilder]]
