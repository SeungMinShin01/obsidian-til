---
출처: Claude 분석
원본: KDT_2026/2026B_Spring/springweb/src/main/java/day15, springweb/build.gradle
작성일: 2026-10-09
tags: [학습, java]
---

# Spring day15 — 웹소켓 설정 클래스 뼈대

> 실습 파일: `day15/WebSocketConfig.java` · `MessageController.java` · `MessageDto.java` · `NoticeService.java` · `NoticeController.java` · `AppStart.java`
> 허브: [[Spring MOC]] · 이전: [[Spring day14 파일 업로드·다운로드 게시판]] · 다음: [[Spring day16 제미나이 API 키 서비스 뼈대]]

day15는 지금까지의 요청-응답 방식과 다른 **실시간 통신**으로 넘어가는 날이다. 처음에는 설정 클래스 뼈대만 있었지만, 이후 브로커 설정을 채우고 메시지를 받아 돌려주는 컨트롤러(양방향, 채팅)와 서버가 먼저 보내는 알림(단방향, SSE)까지 한 패키지에 모였다. 아래는 그 전체를 정리한 내용이다.

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

### 2-1. 설정 클래스가 채우는 두 메소드

`@EnableWebSocketMessageBroker`를 붙인 클래스는 `WebSocketMessageBrokerConfigurer`를 구현해 두 메소드를 채운다. 실습에서 채운 값은 다음과 같다.

```java
@Configuration
@EnableWebSocketMessageBroker
public class WebSocketConfig implements WebSocketMessageBrokerConfigurer {

    @Override
    public void configureMessageBroker(MessageBrokerRegistry registry) {
        registry.enableSimpleBroker("/sub");               // 구독 주소
        registry.setApplicationDestinationPrefixes("/pub"); // 발행 주소
    }

    @Override
    public void registerStompEndpoints(StompEndpointRegistry registry) {
        registry.addEndpoint("/ws-chat")                   // 소켓 연결 주소
                .setAllowedOriginPatterns("*");            // 모든 도메인 허용
    }
}
```

| 주소 | 역할 |
| --- | --- |
| `/ws-chat` | 백엔드와 프론트가 처음 연결을 맺는 소켓 주소 |
| `/sub/...` | 특정 방·경로를 구독하는 주소 (서버 → 클라이언트) |
| `/pub/...` | 특정 경로로 메시지를 발행하는 주소 (클라이언트 → 서버) |

`implements`는 인터페이스의 추상 메소드를 구현한다는 뜻이고, `extends`는 클래스를 상속한다는 뜻이다. 그래서 `@Override`는 여기서 추상 메소드 구현을 의미한다. 같은 설정 클래스 주석에서는 `@Configuration`·`@Controller`·`@Service`·`@Repository`·`@Component`가 모두 스프링이 객체(빈)를 만들어 컨테이너에 담는 표시라는 점도 같이 정리해 두었다.

### 2-2. 컨트롤러 쪽 짝 — `@MessageMapping`과 `SimpMessageSendingOperations`

REST의 `@GetMapping`·`@PostMapping`에 대응하는 것이 `@MessageMapping`이다. 클라이언트가 `/pub/chat/message`로 보내면 `@MessageMapping("/chat/message")` 메소드가 실행된다. `/pub` 접두사는 설정 클래스에서 정한 발행 주소가 앞에 붙은 것이다.

```java
@Controller
@RequiredArgsConstructor
public class MessageController {
    private final SimpMessageSendingOperations messageTemp;

    @MessageMapping("/chat/message")
    public void message(MessageDto messageDto) {
        if (messageDto.getType().equals("ENTER")) {
            messageDto.setContent(messageDto.getSender() + "님이 입장");
        } else if (messageDto.getType().equals("QUIT")) {
            messageDto.setContent(messageDto.getSender() + "님이 퇴장");
        }
        messageTemp.convertAndSend("/sub/chat/room/" + messageDto.getRoomId(), messageDto);
    }
}
```

- 받은 본문(body)이 `MessageDto`로 매핑된다.
- `type`이 `ENTER`·`QUIT`이면 서버가 입장·퇴장 문구를 만들어 `content`에 채우고, 그 외(`TALK`)는 받은 내용을 그대로 쓴다.
- `convertAndSend("/sub/chat/room/방번호", 내용)`으로 **같은 방을 구독 중인 모든 클라이언트**에게 보낸다. 방 번호가 주소 끝에 붙어서 방 단위로 나뉜다.
- 메시지를 DB에 영구 저장하거나 보낸 사람·방을 조회하는 부분은 주석으로 생략 자리만 표시해 두었다(JPA로 이어 붙일 수 있는 자리).

### 2-3. 메시지 DTO

```java
@NoArgsConstructor @AllArgsConstructor @Data @Builder
public class MessageDto {
    private String type;    // TALK 메시지 / ENTER 접속 등 형식
    private String roomId;  // 방번호
    private String sender;  // 보낸사람
    private String content; // 보낸내용
    private String date;    // 보낸시간
}
```

### 2-4. 알림은 SSE로 — 단방향 서버 푸시

채팅처럼 양쪽이 주고받는 경우는 웹소켓+STOMP, 서버가 클라이언트로만 보내는 알림은 **SSE(Server-Sent Events)** 로 나눠 쓴다.

| 구분 | 방향 | 용도 |
| --- | --- | --- |
| WebSocket + STOMP | 양방향 (클라이언트 ↔ 서버) | 채팅 |
| SSE | 단방향 (서버 → 클라이언트) | 알림 |

```java
@Service
public class NoticeService {
    private final List<SseEmitter> emitters = new CopyOnWriteArrayList<>();

    public SseEmitter subscribe() {
        SseEmitter emitter = new SseEmitter();
        emitters.add(emitter);
        emitter.onCompletion(() -> emitters.remove(emitter));
        emitter.onTimeout(() -> emitters.remove(emitter));
        emitter.onError((e) -> emitters.remove(emitter));
        return emitter;
    }

    public void onMessage(String message) {
        for (SseEmitter emitter : emitters) {
            try {
                emitter.send(SseEmitter.event().name("notice").data(message));
            } catch (IOException e) {
                emitters.remove(emitter);
            }
        }
    }
}
```

- `SseEmitter`는 연결을 유지한 채 서버가 나중에 내려보낼 수 있는 HTTP 응답 객체다. 구독한 클라이언트마다 하나씩 만들어 리스트에 보관한다.
- 구독 요청과 메시지 전송이 동시에 여러 개 들어오므로 동기화를 지원하는 `CopyOnWriteArrayList`를 쓴다. `ArrayList`는 동기화를 지원하지 않고, `Vector`는 지원한다는 비교도 함께 정리해 두었다.
- 연결이 끝나거나(`onCompletion`), 시간이 초과되거나(`onTimeout`), 오류가 나면(`onError`) 리스트에서 빼 준다. 리액트에서 새로고침(F5)하면 구독이 중복으로 쌓이는 문제가 생겨서 이 정리 코드가 필요하다.
- 전송이 실패한 emitter는 `catch`에서 리스트에서 제외한다.

```java
@RestController
@RequestMapping("/api/sse")
@CrossOrigin(origins = "*")
public class NoticeController {
    @GetMapping(value = "/subscribe", produces = MediaType.TEXT_EVENT_STREAM_VALUE)
    public SseEmitter subscribe() { return noticeService.subscribe(); }

    @GetMapping("/message")
    public void onMessage(@RequestParam(name = "msg") String msg) { noticeService.onMessage(msg); }
}
```

구독 매핑은 응답 `Content-Type`을 JSON이 아니라 `text/event-stream`(`MediaType.TEXT_EVENT_STREAM_VALUE`)으로 바꿔야 한다. `/message`는 알림이 가는지 확인하려고 만든 테스트용 전송 주소다.

### 2-5. 실행 클래스

`day15/AppStart.java`에는 `@SpringBootApplication`과 함께 `@EnableJpaAuditing`이 붙어 있다. 앞선 날들의 감사 필드(생성·수정 시간)를 쓰는 엔티티가 같은 프로젝트에 있어서 그대로 이어졌다.

## 3. 더 나아가 알면 좋은 것

- STOMP 프로토콜 — 웹소켓 위에서 구독(subscribe)·발행(send) 규칙을 정한 메시징 규약
- 실습에서 쓴 `SimpMessageSendingOperations`는 `SimpMessagingTemplate`의 상위 인터페이스로, 서버가 원하는 시점에 직접 메시지를 밀어 줄 때 쓴다
- `@SendTo`로 반환값을 구독 주소에 자동으로 돌려주는 방식과 `convertAndSend`를 직접 부르는 방식의 차이
- SSE의 `SseEmitter` 타임아웃 설정, 이벤트 이름(`name("notice")`)별로 클라이언트가 구독을 나누는 방법
- 리액트 쪽 클라이언트 — `@stomp/stompjs`, `sockjs-client`
- 연결 시 세션·JWT로 사용자 식별, 인터셉터로 인증 처리 ([[Spring day12 컨트롤러가 받는 HttpServletRequest와 세션]]에서 다룬 세션과 비교)
- 서버 여러 대일 때 외부 브로커(Redis Pub/Sub, RabbitMQ) 사용 ([[Spring day13 레디스 리스트로 값 쌓고 읽기]]의 레디스와 이어지는 주제)

### 다음에 볼 키워드

- `@SendTo`, `SimpMessagingTemplate`, SockJS, `SseEmitter` 타임아웃, 메시지 DB 저장(JPA)

## 실습 파일

- `KDT_2026/2026B_Spring/springweb/src/main/java/day15/WebSocketConfig.java` — 브로커·소켓 엔드포인트 설정 클래스
- `KDT_2026/2026B_Spring/springweb/src/main/java/day15/MessageController.java` — `@MessageMapping` 채팅 메시지 처리
- `KDT_2026/2026B_Spring/springweb/src/main/java/day15/MessageDto.java` — 채팅 메시지 DTO
- `KDT_2026/2026B_Spring/springweb/src/main/java/day15/NoticeService.java` · `NoticeController.java` — SSE 알림 구독·전송
- `KDT_2026/2026B_Spring/springweb/src/main/java/day15/AppStart.java` — 실행 클래스
- `KDT_2026/2026B_Spring/springweb/build.gradle` — `spring-boot-starter-websocket` 의존성

## 관련 노트

[[Spring MOC]] · [[Spring day14 파일 업로드·다운로드 게시판]] · [[Spring day13 레디스 리스트로 값 쌓고 읽기]] · [[Spring day12 컨트롤러가 받는 HttpServletRequest와 세션]] · [[Spring day16 제미나이 API 키 서비스 뼈대]] · [[KDT_2026 학습 지도]]
