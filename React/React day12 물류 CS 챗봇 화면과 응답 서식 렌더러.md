---
출처: Claude 분석
원본: KDT_2026/2026_React/src/example/day11/ChatBot.jsx
작성일: 2026-10-19
tags: [학습, react]
---

# React day12 — 물류 CS 챗봇 화면과 응답 서식 렌더러

> 실습 파일: `src/example/day11/ChatBot.jsx`
> 허브: [[React MOC]] · 이전: [[React day11 STOMP 웹소켓 채팅방]] · 다음: (예정)

day11은 채팅 화면을 LLM 백엔드에 붙이는 단계다. 서버 쪽은 Spring day16 수업의 `/api/chat1` · `/api/chat2` ... 엔드포인트이고, 화면은 업무 카드로 서비스를 고르고 입력을 보낸 뒤 **마크다운 모양으로 돌아온 응답을 직접 서식으로 바꿔 그리는** 쪽이다. 파일 하나에 상태 · 서비스 정의 · 호출 · 서식 렌더러 · 인라인 스타일 객체가 모두 들어 있다.

## 1. 배운 내용

### 1-1. 서비스 정의를 데이터 배열로

```jsx
const SERVICES = [
  { key: "chat1", code: "01", title: "LLM API", desc: "...", auto: false, placeholder: "...", initialPrompt: null },
  { key: "chat2", code: "02", title: "배송·반품 관제 리포트", auto: true, ... },
  { key: "chat3", ... },   // 클레임 대응 파이프라인
  { key: "chat4", ... },   // 배송 CS 자동 라우팅
];
```

- 네 가지 업무를 컴포넌트 바깥 상수 배열로 두고 카드 화면은 `SERVICES.map(...)` 으로 만든다. 업무가 늘어도 배열에 한 칸만 추가하면 된다 (day02의 객체 배열 + `map`)
- `key` 는 서버 주소의 끝부분(`chat1`~`chat4`)과 같고, `auto` 는 입력 없이 바로 실행하는 업무인지 구분하는 표시다

### 1-2. 상태 구성

| 상태 / ref | 담는 것 |
| --- | --- |
| `activeService` | 선택된 업무 (`null` 이면 기본 모드) |
| `inputMessage` | 입력창 값 (제어 컴포넌트) |
| `loading` | 응답 대기 여부 |
| `messages` | 대화 목록 (환영 메시지 하나로 시작) |
| `messagesEndRef` | 대화 맨 아래 빈 `div` 의 ref |

대화 목록의 첫 항목은 `type: "welcome"` 이고, 이 메시지 안에서만 업무 카드 2×2 그리드가 같이 그려진다.

### 1-3. 자동 스크롤

```jsx
useEffect(() => {
  messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
}, [messages, loading]);
```

대화 맨 아래에 `<div ref={messagesEndRef} />` 를 두고, 메시지가 늘거나 로딩 상태가 바뀔 때마다 그 자리로 스크롤한다. day07에서 본 DOM 참조용 `useRef` 와 의존성 배열 `useEffect` 의 조합이다. `?.` 로 아직 DOM이 없는 첫 순간을 방어한다.

### 1-4. 공통 호출 함수 `executeApi`

```jsx
const executeApi = async (serviceKey, payloadText) => {
  setLoading(true);
  try {
    let url = `${BACKEND_BASE_URL}/api/${serviceKey}?_t=${Date.now()}`;
    if (serviceKey === "chat1") url += `&prompt=${encodeURIComponent(payloadText)}`;
    else if (serviceKey === "chat3") url += `&topic=${encodeURIComponent(payloadText)}`;
    else if (serviceKey === "chat4") url += `&userMessage=${encodeURIComponent(payloadText)}`;
    const res = await fetch(url, { method: "GET", headers: { "Cache-Control": "no-cache, no-store, must-revalidate" } });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const rawText = await res.text();
    let data; try { data = JSON.parse(rawText); } catch (e) { data = rawText; }
    ...
  } catch (err) { /* 오류 문구를 봇 메시지로 */ } finally { setLoading(false); }
};
```

- 업무마다 **쿼리 스트링 이름이 달라서**(`prompt` · `topic` · `userMessage`) 분기로 붙인다. 한글이 섞인 값은 `encodeURIComponent` 로 감싼다
- `_t=${Date.now()}` 와 `Cache-Control` 헤더는 같은 주소 요청이 캐시되지 않게 하는 관용구다
- 응답을 `res.text()` 로 먼저 받고 `JSON.parse` 를 시도해 실패하면 문자열 그대로 쓴다. 서버가 JSON을 줄 때도, 글자만 줄 때도 한 함수로 처리된다
- `try / catch / finally` 로 성공 · 실패 · 로딩 해제를 나눈다. 실패하면 오류 문구도 봇 말풍선으로 대화에 쌓는다
- 메시지 추가는 `setMessages(prev => [...prev, 새 메시지])` 함수형 업데이트다. 비동기 응답이 돌아오는 시점의 최신 목록 뒤에 붙이기 위함이다

### 1-5. 카드 선택과 전송

- `handleSelectServiceCard(service)`: 선택된 업무를 `activeService` 에 넣고, `auto` 인 업무(02번 리포트)는 사용자 말풍선 `[리포트 생성] 제목` 을 먼저 쌓은 뒤 바로 `executeApi(service.key, "")` 를 실행한다. 입력형 업무는 상태만 바꿔 입력창의 `placeholder` 가 그 업무에 맞게 바뀐다
- `handleSend(e)`: `preventDefault` 후 빈 입력 · 로딩 중이면 무시하고, 활성 업무가 없으면 기본 `chat1` 로 보낸다. 사용자 말풍선을 쌓고 `setInputMessage("")` 로 비운 뒤 호출한다
- 입력창은 `disabled={loading}`, 전송 버튼은 `disabled` + 투명도로 중복 전송을 막는다
- 활성 업무가 있으면 입력 위에 "[코드] 제목 모드 적용 중" 배너와 "기본 라우팅으로 복귀" 버튼이 조건부로 나타난다 (`activeService && <div>...`)

### 1-6. 응답 서식 렌더러

LLM 응답이 마크다운 문법(`##` 제목, `**굵게**`, `` `코드` ``, 표, 목록)으로 오기 때문에 라이브러리 없이 직접 해석해 JSX로 바꾼다. 줄 단위로 `split("\n")` 한 뒤 `while` 로 한 줄씩 훑으며 모양을 판정한다.

| 판정 순서 | 모양 | 결과 |
| --- | --- | --- |
| 1 | `\|` 로 시작해 `\|` 로 끝나는 연속 줄 | `renderTable` 로 표 |
| 2 | `---` `***` `___` | 구분선 `<hr>` |
| 3 | 빈 줄 | 높이 8px 여백 |
| 4 | `#####` / `####` / `##`·`###` | 제목 줄 (단계별 스타일) |
| 5 | `*` `•` `-` 로 시작 | 글머리 줄 (들여쓰기 2칸 = 14px) |
| 6 | `1.` `1)` 로 시작 | 번호 줄 |
| 7 | 나머지 | 일반 줄 |

- 판정마다 `continue` 로 다음 줄로 넘어가고, 표는 연속된 줄을 안쪽 `while` 로 모아 한 번에 넘긴다
- 정규식 `line.match(/^(\s*)([*•\-])\s+(.*)/)` 의 첫 그룹(들여쓰기 공백)으로 `Math.floor(길이 / 2)` 만큼 `paddingLeft` 를 더한다
- `parseInlineStyles(text)` 는 `text.split(/(\*\*.*?\*\*|`.*?`)/g)` 로 굵은 글씨 · 인라인 코드 조각을 분리해 `<strong>` · `<code>` 로 바꾸고 나머지는 글자 그대로 반환한다. 정규식에 괄호 캡처 그룹을 쓰면 구분자도 결과 배열에 남는 점이 핵심이다
- `renderTable` 은 첫 줄을 제목 셀, 둘째 줄(`:---:` 꼴)을 정렬 정보로 읽고(`:` 위치로 left · center · right) 나머지를 본문 행으로 그린다. 홀수 번째 행은 배경색을 달리하는 줄무늬다
- 서버 응답이 `<!doctype` / `<html` 로 시작하면 `formatBotResponse` 가 게이트웨이 오류 안내 문구로 바꿔 보여 준다. 객체면 `JSON.stringify(data, null, 2)` 로 들여쓴 문자열로 출력한다

### 1-7. 말풍선 · 스타일 객체

- 봇 메시지는 `renderFormattedText(msg.text)`, 사용자 메시지는 글자 그대로 출력한다. `msg.sender` 로 좌우 정렬(`justifyContent`)과 말풍선 배경이 갈린다
- 스타일은 파일 끝 `styles` 객체 하나에 모아 `style={styles.bubble}` 처럼 쓰고, 조건이 붙는 곳은 `{ ...styles.bubble, ...styles.userBubble }` 스프레드로 합친다. day03에서 정리한 인라인 `style` 객체 방식을 규모 있게 쓴 경우다
- 응답을 기다리는 동안은 `loading` 일 때만 "데이터베이스 조회 및 물류 분석 중..." 말풍선이 하나 더 나온다

## 2. 추가로 알면 좋은 활용법

- **서식 렌더러 대체**: 마크다운 해석은 `react-markdown` + `remark-gfm` 으로 대체하면 표 · 목록 · 코드 블록까지 한 번에 처리된다. 직접 만든 렌더러는 동작 원리를 익히기에 좋고, 라이브러리는 유지보수에 안전하다
- **메시지 `key`**: `Date.now()` 기반 id 는 같은 밀리초에 두 번 쌓이는 경우를 생각해 `crypto.randomUUID()` 같은 겹치지 않는 값을 쓰는 방법도 있다
- **GET vs POST**: 긴 프롬프트나 개인 정보가 들어갈 수 있는 본문은 쿼리 스트링보다 `POST` 본문으로 보내는 쪽이 길이 제한 · 로그 노출 면에서 낫다
- **주소 상수화**: `BACKEND_BASE_URL` 은 `.env` 의 `VITE_` 변수로 빼 개발 · 배포 주소를 바꾼다
- **컴포넌트 분리**: 한 파일에 든 렌더러를 `MessageBubble` · `ServiceCard` · `MarkdownText` 로 쪼개면 재사용이 쉬워진다

## 3. 더 나아가 알면 좋은 것

- 응답을 글자 단위로 흘려 보여 주는 스트리밍(SSE · `ReadableStream`)
- 대화 이력을 서버에 보내 문맥을 이어 가는 멀티턴 구조
- 요청 취소(`AbortController`)와 중복 요청 정리
- 상태가 많아질 때 `useReducer` 로 메시지 · 로딩 · 활성 업무를 한곳에서 관리하기
- 사용자 입력을 그대로 HTML로 넣지 않는 이유(XSS)와 JSX 이스케이프

### 3-1. 다음에 볼 키워드

- `react-markdown`
- Server-Sent Events / 스트리밍 응답
- LLM 응답 JSON 스키마 고정(구조화 출력)
- 프롬프트 파이프라인(1차 판정 → 2차 보상안 → 3차 사과문)이 서버에서 이어지는 방식

## 실습 파일

- `KDT_2026/2026_React/src/example/day11/ChatBot.jsx` — 서비스 카드 · 상태 · `executeApi` · 마크다운 서식 렌더러 · `styles` 객체

## 관련 노트

[[React MOC]] · [[React day11 STOMP 웹소켓 채팅방]] · [[React day10 게시판 첨부파일 등록과 이미지 미리보기]] · [[React day07 useRef와 렌더링을 일으키지 않는 값]] · [[React day05 axios로 백엔드에 POST 보내기]] · [[KDT_2026 학습 지도]]
