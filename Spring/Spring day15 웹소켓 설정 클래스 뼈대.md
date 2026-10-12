---
출처: Claude 분석
원본: KDT_2026/2026B_Spring/springweb/src/main/java/day15
작성일: 2026-10-09
tags: [학습, java]
---

# Spring day15 — 웹소켓 설정 클래스 뼈대

> 실습 파일: `day15/WebSocketConfig.java`
> 허브: [[Spring MOC]] · 이전: [[Spring day14 파일 업로드·다운로드 게시판]] · 다음: [[Spring day16 제미나이 API 키 서비스 뼈대]]

day15는 지금까지의 요청-응답 방식과 다른 **웹소켓(WebSocket)** 으로 넘어가는 첫걸음이다. 이 시점에는 설정 클래스 하나가 뼈대만 만들어져 있고, 메시지를 주고받는 컨트롤러와 화면은 이후 수업에서 채워진다.

## 1. 배운 내용

### 1-1. 웹소켓 의존성

`build.gradle`에 `spring-boot-starter-websocket`이 들어 있어야 웹소켓 관련 애노테이션과 클래스를 쓸 수 있다.

```groovy
implementation 'org.springframework.boot:spring-boot-starter-websocket'
```

### 1-2. 설정 클래스 — `@Configuration` + `@EnableWebSocketMessageBroker`

```java
package day15;

@Configuration
@EnableWebSocketMessageBroker
public class WebSocketConfig {

}
```

| 항목 | 설명 |
| --- | --- |
| `@Configuration` | 스프링이 시작할 때 읽어 들이는 설정 클래스라는 표시. 이 안에서 빈 등록이나 설정 메소드를 정의한다 |
| `@EnableWebSocketMessageBroker` | 웹소켓 위에 **메시지 브로커**(메시지를 구독자에게 나눠 주는 중개자) 방식의 STOMP 메시징을 켠다 |

HTTP는 클라이언트가 요청해야 서버가 응답하는 구조라 서버가 먼저 말을 걸 수 없다. 웹소켓은 한 번 연결을 맺어 두면 양쪽이 언제든 메시지를 보낼 수 있어서 채팅·실시간 알림에 쓰인다.

## 2. 추가로 알면 좋은 활용법

### 2-1. 설정 클래스가 보통 채우는 두 가지

`@EnableWebSocketMessageBroker`를 붙인 클래스는 관례상 `WebSocketMessageBrokerConfigurer`를 구현해 두 메소드를 채운다.

```java
@Override
public void registerStompEndpoints(StompEndpointRegistry registry) {
    registry.addEndpoint("/ws").setAllowedOrigins("http://localhost:5173");
}

@Override
public void configureMessageBroker(MessageBrokerRegistry registry) {
    registry.enableSimpleBroker("/topic");          // 구독 경로
    registry.setApplicationDestinationPrefixes("/app"); // 보내는 경로
}
```

- `registerStompEndpoints` — 클라이언트가 처음 연결을 맺는 주소
- `configureMessageBroker` — 구독용 경로(`/topic`)와 서버로 보내는 경로(`/app`)의 접두사

### 2-2. 컨트롤러 쪽 짝

메시지를 받는 메소드에는 `@MessageMapping`, 받은 내용을 구독자에게 돌려주는 곳에는 `@SendTo`를 쓴다. 일반 REST 컨트롤러의 `@GetMapping`·`@PostMapping`에 대응하는 자리다.

## 3. 더 나아가 알면 좋은 것

- STOMP 프로토콜 — 웹소켓 위에서 구독(subscribe)·발행(send) 규칙을 정한 메시징 규약
- `SimpMessagingTemplate`으로 서버가 원하는 시점에 직접 메시지 밀어 주기
- 리액트 쪽 클라이언트 — `@stomp/stompjs`, `sockjs-client`
- 연결 시 세션·JWT로 사용자 식별, 인터셉터로 인증 처리 ([[Spring day12 컨트롤러가 받는 HttpServletRequest와 세션]]에서 다룬 세션과 비교)
- 서버 여러 대일 때 외부 브로커(Redis Pub/Sub, RabbitMQ) 사용 ([[Spring day13 레디스 리스트로 값 쌓고 읽기]]의 레디스와 이어지는 주제)

### 다음에 볼 키워드

- `WebSocketMessageBrokerConfigurer`, `@MessageMapping`, `@SendTo`, `SimpMessagingTemplate`, SockJS

## 실습 파일

- `KDT_2026/2026B_Spring/springweb/src/main/java/day15/WebSocketConfig.java` — 웹소켓 메시지 브로커를 켜는 설정 클래스(뼈대)
- `KDT_2026/2026B_Spring/springweb/build.gradle` — `spring-boot-starter-websocket` 의존성

## 관련 노트

[[Spring MOC]] · [[Spring day14 파일 업로드·다운로드 게시판]] · [[Spring day13 레디스 리스트로 값 쌓고 읽기]] · [[Spring day12 컨트롤러가 받는 HttpServletRequest와 세션]] · [[Spring day16 제미나이 API 키 서비스 뼈대]] · [[KDT_2026 학습 지도]]
