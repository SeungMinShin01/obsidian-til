---
출처: Claude 분석
원본: KDT_2026/2026B_Spring/springweb/src/main/java/day16
작성일: 2026-10-12
tags: [학습, java]
---

# Spring day16 제미나이 API 키 서비스 뼈대

> 실습 파일: `day16/AppStart.java`, `day16/LLMService.java`
> 허브: [[Spring MOC]] · 이전: [[Spring day15 웹소켓 설정 클래스 뼈대]] · 다음: (아직 없음)

day16은 새 패키지에 진입점을 두고, LLM(대규모 언어 모델) API를 부르는 서비스의 첫 칸을 만든 시점이다. 서비스 클래스에는 API 키를 설정 파일에서 받아 오는 필드와, 프롬프트를 요청 본문으로 감싸는 `ChatAi` 메서드의 첫 줄까지 있고, 실제 호출과 응답 처리는 이후 수업에서 채워진다.

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

### 1-3. 프롬프트를 요청 본문(Map)으로 구성하기

```java
/*
    LLM : 대규모 언어 모델 => AI 모델
    LLM API : 각 LLM 회사에서 API 제공 , API(유료/무료)
*/
public String ChatAi(String prompt) {
    // 1) 프롬프트 구성
    Map<String, Object> RequestBody = Map.of("contents", List.of(Map.of("parts",
            List.of(Map.of("text", prompt)))));
}
```

Gemini API는 `contents` 배열 안에 `parts` 배열을 두고, 그 안에 `text`로 질문을 담는 JSON을 받는다. `Map.of`와 `List.of`를 겹쳐서 이 JSON 모양을 그대로 자바 객체로 만든 것이다. 별도 DTO 없이 `Map`만으로 요청 본문을 만들 수 있고, `WebClient`의 `bodyValue`로 넘기면 JSON으로 직렬화된다. 메서드 본문은 아직 반환문이 없는 중간 단계다.

## 2. 추가로 알면 좋은 활용법

### 2-1. 키는 설정 파일 밖으로

`application.properties`에도 실제 키를 적어 두면 같이 올라가기 쉽다. 환경변수로 빼고 `api.gemini-key=${GEMINI_API_KEY}`처럼 참조하거나, 커밋하지 않는 로컬 전용 설정 파일을 따로 두는 편이 안전하다.

### 2-2. 이 서비스가 채울 자리

LLM API는 HTTP로 프롬프트를 보내고 답을 JSON으로 받는 구조다. day10에서 쓴 `WebClient`로 요청을 보내고, 응답을 DTO로 받아 컨트롤러가 화면에 내주는 흐름이 이어질 것이다.

## 3. 더 나아가 알면 좋은 것

- Gemini 등 LLM REST API의 요청·응답 JSON 구조
- `@ConfigurationProperties`로 API 설정을 묶어서 받기
- 응답 지연이 긴 호출을 위한 타임아웃·비동기 처리
- 앞서 본 웹소켓([[Spring day15 웹소켓 설정 클래스 뼈대]])으로 답변을 실시간으로 흘려 보내기

### 다음에 볼 키워드

- `WebClient`, `@ConfigurationProperties`, 환경변수, 프롬프트, 스트리밍 응답

## 실습 파일

- `KDT_2026/2026B_Spring/springweb/src/main/java/day16/AppStart.java` — day16 진입점
- `KDT_2026/2026B_Spring/springweb/src/main/java/day16/LLMService.java` — API 키를 설정에서 받는 서비스 뼈대

## 관련 노트

[[Spring MOC]] · [[Spring day15 웹소켓 설정 클래스 뼈대]] · [[Spring day10 WebClient로 공공데이터 API 대신 호출하기]] · [[KDT_2026 학습 지도]]
