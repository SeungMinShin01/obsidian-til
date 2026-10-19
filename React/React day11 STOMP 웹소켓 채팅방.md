---
출처: Claude 분석
원본: KDT_2026/2026_React/src/example/day10/ChatRoom.jsx, Notice.jsx, ChatRoom.css
작성일: 2026-10-19
tags: [학습, react]
---

# React day11 — STOMP 웹소켓 채팅방

> 실습 파일: `src/example/day10/ChatRoom.jsx` · `Notice.jsx` · `ChatRoom.css`
> 허브: [[React MOC]] · 이전: [[React day10 게시판 첨부파일 등록과 이미지 미리보기]] · 다음: [[React day12 물류 CS 챗봇 화면과 응답 서식 렌더러]]

지금까지 화면은 필요할 때 요청을 보내고 응답을 받는 방식이었다. 이번에는 한 번 연결해 두면 서버가 먼저 메시지를 밀어 주는 **웹소켓** 위에서 채팅방 화면을 만든다. 서버 쪽 짝은 Spring day15 수업의 웹소켓 설정 클래스이고, 화면은 `@stomp/stompjs` 라이브러리로 그 브로커에 붙는 쪽이다. 정리하면 "연결 객체를 `useRef` 에 보관", "접속하면 구독하고 입장 메시지 발행", "받은 메시지를 상태 배열에 쌓기" 세 가지가 핵심이다.

## 1. 배운 내용

### 1-1. 라이브러리 설치와 연결 객체

```bash
npm install @stomp/stompjs
```

```jsx
import { Client } from "@stomp/stompjs";

const client = new Client({
  brokerURL: "ws://localhost:8080/ws-chat",
  onConnect: () => { /* 연결된 뒤 할 일 */ },
});
client.activate();   // 연결 시작
```

- 주소가 `http` 가 아니라 `ws://` 로 시작한다. 서버 설정에서 열어 둔 엔드포인트(`/ws-chat`)와 맞아야 한다
- `activate()` 를 불러야 실제 연결이 시작되고, 연결이 끝나면 `onConnect` 콜백이 실행된다
- 닫을 때는 `deactivate()`

### 1-2. 상태 · ref 역할 나누기

| 변수 | 종류 | 담는 것 |
| --- | --- | --- |
| `message` | `useState("")` | 입력 중인 메시지 |
| `messages` | `useState([])` | 서버에서 받은 메시지 목록 |
| `isConnected` | `useState(false)` | 방 접속 여부 (화면 전환 기준) |
| `roomId` · `sender` | `useState("")` | 방 제목과 닉네임 입력값 |
| `clientRef` | `useRef(null)` | 연결된 `Client` 객체 |

연결 객체는 화면에 그릴 값이 아니고 재렌더링마다 초기화되면 안 된다. day07에서 정리한 "기억만 하면 ref" 기준이 그대로 쓰인다. 주석에도 지역변수 · 상태 변수 · 참조 변수를 비교해 두었다. 접속 함수에서 `clientRef.current = client` 로 넣어 두면 전송 · 퇴장 함수에서 같은 연결을 꺼내 쓸 수 있다.

### 1-3. 접속 — 구독하고 입장 메시지 발행

```jsx
onConnect: () => {
  setIsConnected(true);                                   // 1. 접속 상태 변경
  client.subscribe(`/sub/chat/room/${roomId}`, (message) => {   // 2. 방 주소 구독
    messages.push(JSON.parse(message.body));
    setMessages([...messages]);
  });
  client.publish({                                        // 3. 입장 메시지 발행
    destination: "/pub/chat/message",
    body: JSON.stringify({ type: "ENTER", roomId, sender, content: "", date: new Date().toLocaleTimeString() }),
  });
},
```

- **구독(`subscribe`)** 은 받는 쪽 주소, **발행(`publish`)** 은 보내는 쪽 주소다. 주소 앞 `/sub` · `/pub` 접두사는 서버 설정의 브로커 · 애플리케이션 목적지 접두사와 짝이다
- 구독 주소에 방 번호를 끼워 `/sub/chat/room/${roomId}` 로 만들기 때문에 같은 방을 구독한 사람끼리만 메시지가 돈다
- 서버가 보낸 본문(`message.body`)은 문자열이라 `JSON.parse` 로 객체로 바꿔 상태 배열에 넣는다. 배열은 주소값이 바뀌어야 재렌더링되므로 `push` 뒤 `[...messages]` 로 복사해 `setMessages` 에 넘기는 day02의 패턴 그대로다
- 메시지 객체는 `type` · `roomId` · `sender` · `content` · `date` 다섯 칸이고, 서버의 메시지 DTO 필드명과 맞춘다 (상태 이름 = JSON 키 = DTO 필드명 사슬)

### 1-4. 전송 · 퇴장

```jsx
clientRef.current.publish({
  destination: "/pub/chat/message",
  body: JSON.stringify({ type: "TALK", roomId, sender, content: message, date: ... }),
});
```

- 전송과 입장 · 퇴장이 **같은 발행 주소** 를 쓰고 `type` 값(`ENTER` / `TALK` / `QUIT`)으로 서버가 구분한다
- 퇴장은 `QUIT` 발행 → `deactivate()` → `isConnected` 를 `false` 로 → `messages` 비우기 순서다. 소켓을 닫고 상태도 같이 초기화해야 다음 접속 때 이전 방 내용이 남지 않는다
- 전송 함수 맨 앞의 `if (clientRef.current == null) return;` 은 연결 전에 눌리는 경우를 막는 방어 한 줄이다

### 1-5. 화면 — 접속 전 / 접속 후 / 말풍선 세 갈래

```jsx
{!isConnected ? ( /* 방 제목 · 닉네임 입력 + 접속 버튼 */ ) : ( /* 채팅 화면 */ )}
...
{msg.type === "TALK"
  ? (msg.sender === sender ? /* 내가 보낸 메시지 */ : /* 상대가 보낸 메시지 */)
  : <i>{msg.content}</i>}   // 입장 · 퇴장 알림
```

- `isConnected` 삼항 하나가 day07의 `mode` 전환과 같은 역할로 입력 화면과 채팅 화면을 갈아끼운다
- 메시지 하나를 그릴 때 `TALK` 인지, 내가 보낸 것인지를 `sender` 비교로 다시 가른다. 내 말풍선은 시간 + 본문, 상대 말풍선은 이름 + 본문 + 시간 구성이다
- 입장 · 퇴장 같은 시스템 메시지는 `<i>` 로 가운데 안내 문구처럼 그린다

### 1-6. CSS — 태그와 구조로 고르는 선택자

`ChatRoom.css` 는 클래스를 하나도 달지 않은 JSX에 맞춰 `:has(b)` · `:has(p)` · `:has(small)` · `:has(i)` · `:nth-child(n)` 같은 선택자로 영역을 골라 꾸민다. `b` 가 있는 `div` 는 채팅 화면, 그 안 첫째 자식은 헤더, 둘째는 메시지 스크롤 영역, 셋째는 입력줄이라는 식이다. 스크롤바 꾸미기(`::-webkit-scrollbar`), 입력창 `:focus` 강조, 버튼 `:hover` 도 같은 방식으로 붙는다. `Notice` 가 그려 주는 안내 영역도 `:has(> div > p):has(> div > button)` 로 따로 골라 꾸민다.

### 1-7. Notice 컴포넌트

`Notice.jsx` 는 `ChatRoom` 과 같은 구성의 컴포넌트로, `ChatRoom` 끝에서 `<Notice />` 로 불러 같은 화면에 함께 그린다. 컴포넌트 안에 컴포넌트를 조립하는 day01 패턴이다.

## 2. 추가로 알면 좋은 활용법

- **구독 정리**: `useEffect` 의 정리(cleanup) 함수에서 `deactivate()` 를 불러 두면 컴포넌트가 사라질 때 연결이 남지 않는다.  퇴장 버튼 외에 화면 이동으로 컴포넌트가 사라지는 경우까지 챙기는 방법이다
- **자동 스크롤**: 새 메시지가 올 때마다 맨 아래로 내리려면 끝에 빈 `div` 를 두고 `ref` 로 잡아 `scrollIntoView` 를 `useEffect([messages])` 안에서 부른다
- **함수형 업데이트**: `setMessages(prev => [...prev, JSON.parse(message.body)])` 로 쓰면 구독 콜백이 만들어질 때의 `messages` 에 갇히는 문제(오래된 값 참조)를 피한다
- **엔터로 전송**: 입력줄을 `<form onSubmit>` 로 감싸 `preventDefault` 와 전송, 전송 뒤 `setMessage("")` 로 비우기
- **`map` 의 `key`**: 메시지에 고유 번호나 시각을 `key` 로 쓴다

## 3. 더 나아가 알면 좋은 것

- 재연결 옵션(`reconnectDelay`)과 연결 끊김 감지(`onWebSocketClose` · `onStompError`)
- `SockJS` 폴백과 `ws://` / `wss://` 구분(배포 환경에서는 보안 연결)
- 접속자 목록, 읽음 표시, 입력 중 표시처럼 메시지 `type` 을 늘려 가는 방식
- 채팅 기록을 DB나 Redis에 저장해 입장 시 불러오기
- 인증된 사용자 정보로 닉네임 대신 로그인 세션 쓰기

### 3-1. 다음에 볼 키워드

- `STOMP` 프로토콜 프레임 구조(CONNECT · SUBSCRIBE · SEND)
- 메시지 브로커 (Spring `enableSimpleBroker` vs 외부 브로커)
- `useEffect` cleanup 으로 연결 수명 관리
- Server-Sent Events 와 웹소켓 비교

## 실습 파일

- `KDT_2026/2026_React/src/example/day10/ChatRoom.jsx` — STOMP 클라이언트 연결 · 구독 · 발행, 접속 / 채팅 화면 전환, 말풍선 분기
- `KDT_2026/2026_React/src/example/day10/Notice.jsx` — 채팅방 아래에 조립되는 안내 컴포넌트
- `KDT_2026/2026_React/src/example/day10/ChatRoom.css` — `:has()` · `:nth-child()` 기반 선택자 스타일

## 관련 노트

[[React MOC]] · [[React day10 게시판 첨부파일 등록과 이미지 미리보기]] · [[React day12 물류 CS 챗봇 화면과 응답 서식 렌더러]] · [[React day07 useRef와 렌더링을 일으키지 않는 값]] · [[React day02 useState와 상태 갱신]] · [[KDT_2026 학습 지도]]
