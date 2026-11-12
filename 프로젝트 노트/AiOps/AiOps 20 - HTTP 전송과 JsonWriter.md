---
출처: Claude 대화
작성일: 2026-11-10
tags: [프로젝트, java]
---

# AiOps - HTTP 전송과 JsonWriter

> 허브: [[AiOps 프로젝트 MOC]]

**PR #29 `[AI-37] HTTP 전송 실구현 (HttpTransport + JsonWriter)`** — 브랜치 `feat/starter-AI-37-http-transport`. 커밋 4개(파일 하나에 하나). 11/10 머지.

## 1. 배운 내용

### 1-1. 이 PR이 하는 일: "어떻게 보낼까"만

```
BatchingEventSender (언제 보낼까, AI-38)
   └─ transport.send(batch)
        HttpTransport (어떻게 보낼까, 이 PR)
           JsonWriter.write(batch) → JSON 문자열
           HttpClient POST /v1/events (헤더 X-AIOPS-KEY)
           2xx → true / 그 외·예외 → false
```

재시도·타이밍은 여기 없다. `Transport` 인터페이스 주석의 약속("언제 보낼지는 EventSender 몫")을 지킨 것이다. 그래서 HTTP 실패와 재시도 규칙을 따로 테스트할 수 있다.

### 1-2. 왜 JsonWriter를 직접 만들었나 (D-085)

- Spring Boot 4 팀 앱에는 Jackson **3**(`tools.jackson`)이 있다. Starter가 Jackson **2**(`com.fasterxml`)를 참조하면 클래스가 없어서 `NoClassDefFoundError`가 난다. 이건 Exception이 아니라 **Error**라 팀 앱 시작이 죽을 수 있다.
- 팀이 ObjectMapper를 snake_case 등으로 설정해 두면 우리 JSON 모양이 바뀐다.
- 그래서 Starter는 **의존성 0**인 JSON 작성기를 갖는다. 테스트에서만 Jackson(`testImplementation`)으로 "다시 읽으면 원래 record와 같은지"를 확인한다.

### 1-3. 코드로 보기: JsonWriter

```java
private static void writeValue(StringBuilder out, Object value) {
    if (value == null)                         out.append("null");
    else if (value instanceof String s)        writeString(out, s);     // ① 패턴 매칭 instanceof
    else if (value instanceof Boolean b)       out.append(b.booleanValue());
    else if (value instanceof Number n)        writeNumber(out, n);
    else if (value instanceof Enum<?> e)       writeString(out, e.name());
    else if (value instanceof Collection<?> c) writeArray(out, c);
    else if (value.getClass().isRecord())      writeRecord(out, value); // ② record면 필드를 돌며
    else throw new IllegalArgumentException("JsonWriter가 지원하지 않는 타입: " + ...);
}

private static void writeRecord(StringBuilder out, Object record) {
    RecordComponent[] components = COMPONENTS.computeIfAbsent(record.getClass(), type -> type.getRecordComponents()); // ③
    out.append('{');
    for (int i = 0; i < components.length; i++) {
        if (i > 0) out.append(',');
        writeString(out, components[i].getName());              // "env"
        out.append(':');
        writeValue(out, components[i].getAccessor().invoke(record));   // ④ env() 호출 결과
    }
    out.append('}');
}
```

| 번호 | 설명 |
|---|---|
| ① | Java 16+ 문법. `instanceof String s`는 "String이면 s라는 이름으로 바로 써라". 캐스팅 줄이 없어진다 |
| ② | protocol 데이터가 전부 record라서, record면 **필드 목록을 리플렉션으로** 꺼낸다. protocol에 필드가 추가돼도 JsonWriter는 고칠 필요가 없다 |
| ③ | 리플렉션은 느리다. 클래스마다 한 번만 읽어 `ConcurrentHashMap`에 둔다. `computeIfAbsent(키, 키로 값을 만드는 코드)`는 키가 없을 때만 두 번째를 실행한다 (원래 코드는 `Class::getRecordComponents` — 아래 3-1 참고) |
| ④ | `getAccessor()`는 record의 `env()` 같은 메서드. `invoke(record)`로 그 객체에서 실행해 값을 얻는다 |

**이스케이프**: 따옴표·백슬래시·`\n\r\t`·0x20 미만 제어문자만 바꾼다. 한글·이모지는 그대로 둔다(본문이 UTF-8이라). 제어문자는 `\u0001`처럼 바꾼다.

### 1-4. 코드로 보기: HttpTransport

```java
this.client = HttpClient.newBuilder()
        .connectTimeout(Duration.ofSeconds(2))      // ① 연결 2초
        .version(HttpClient.Version.HTTP_1_1)       // ② h2c 업그레이드 시도 없이
        .build();                                    // ③ 생성자에서 1번만

private boolean post(String path, Object body) {
    try {
        HttpRequest request = HttpRequest.newBuilder(URI.create(endpoint + path))
                .timeout(Duration.ofSeconds(3))                         // ④ 응답 3초
                .header(ProtocolConstants.HEADER_API_KEY, apiKey)
                .POST(HttpRequest.BodyPublishers.ofString(json, UTF_8))
                .build();
        int status = client.send(request, HttpResponse.BodyHandlers.discarding()).statusCode();  // ⑤
        if (status >= 200 && status < 300) return true;
        logFirstFailure("HTTP " + status, path);
        return false;
    } catch (InterruptedException e) {
        Thread.currentThread().interrupt();          // ⑥
        return false;
    } catch (Throwable t) {                          // ⑦
        logFirstFailure(t.getClass().getSimpleName(), path);
        return false;
    }
}
```

| 번호 | 이유 |
|---|---|
| ①④ | 서버가 죽어 있어도 **3초 안에 false**. 전송 스레드가 오래 멈추면 버퍼가 비워지지 않는다 |
| ② | 기본값은 HTTP/2 업그레이드를 시도한다. 프록시·서버에 따라 문제가 될 수 있어 1.1로 고정 (명세에 없던 것, PR에 기록) |
| ③ | HttpClient는 스레드와 연결을 품고 있다. 요청마다 만들면 낭비, 하나를 재사용한다 |
| ⑤ | 응답 본문은 읽지 않는다. 상태 코드만 본다 |
| ⑥ | `InterruptedException`은 "멈춰" 신호다. 잡고 그냥 넘어가면 신호가 지워져서 AI-38의 `stop()`이 스레드를 못 멈춘다. 플래그를 다시 세운다 |
| ⑦ | 규칙 4: 어떤 경우에도 예외를 밖으로 던지지 않는다. Error까지 잡는다 |

`logFirstFailure`는 `AtomicBoolean.compareAndSet(false, true)`로 **첫 실패만** 한 줄 찍는다. 서버가 꺼져 있으면 5초마다 실패하는데, 매번 찍으면 팀 로그가 우리 메시지로 덮인다. 키 원문은 남기지 않는다.

### 1-5. 테스트 7 + 8개

- **JsonWriterTest**: EventBatch·HelloRequest를 쓰고 Jackson으로 읽어 `equals` (왕복), Heartbeat 필드 순서, null·빈 리스트, 이스케이프 8종(`@ParameterizedTest`), 지원 안 하는 타입은 예외
- **HttpTransportTest**: JDK 내장 `com.sun.net.httpserver.HttpServer`로 가짜 서버. 202→true, 500→false, 경로 3종, 헤더, **응답 안 주는 서버 → 3.5초 안에 false**, 닫힌 포트, 잘못된 주소에도 예외 없음, main 소스에 jackson import 없음

"응답 안 주는 서버"는 핸들러가 `CountDownLatch.await`로 붙잡혀 있게 만든다. 그래서 이 테스트는 일부러 3초를 기다린다.

## 2. 설계와 다르게 한 곳

| 다른 점 | 이유 |
|---|---|
| `HTTP_1_1` 고정 | h2c 업그레이드 문제 회피 |
| 닫힌 포트 기준 2.5초 미만 (명세 "즉시") | 윈도우는 거절된 연결을 몇 번 다시 시도해서 2초쯤 걸림 |
| jackson 확인을 grep 대신 import 검사 테스트로 | `Transport.java` 주석에 "Jackson" 단어가 이미 있음 |

## 3. 더 나아가 알면 좋은 것

### 3-1. 메서드 참조(`::`)는 쓰지 않기로 했다

`Class::getRecordComponents`, `Files::isRegularFile`처럼 `::`로 쓰는 메서드 참조는 읽기 어렵다. 앞으로 새 코드는 **람다**(`type -> type.getRecordComponents()`)로 쓴다. 이미 develop에 들어간 것(AI-37의 2곳, AI-36 테스트의 `ErrorEvent::message`)은 **MVP 이후 리팩터링** 때 정리한다. 자세한 설명은 AiOps 21 - 전송 스레드 BatchingEventSender의 3-1.

### 3-2. 다음에 볼 키워드

- 리플렉션: `Class.getRecordComponents()`, `Method.invoke`
- JSON 이스케이프 규칙(RFC 8259), 서로게이트 쌍
- `java.net.http.HttpClient`: connectTimeout vs request timeout
- `InterruptedException`을 잡았을 때 interrupt 플래그를 다시 세우는 이유

## 관련 노트

[[AiOps 19 - 디스코드 자동화 (B)]] · [[AiOps 21 - 전송 스레드 BatchingEventSender]]
