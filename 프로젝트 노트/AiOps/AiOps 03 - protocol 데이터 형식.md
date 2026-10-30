---
출처: Claude 대화
작성일: 2026-10-30
tags: [프로젝트, java]
---

# AiOps - protocol 데이터 형식

> 허브: [[AiOps 프로젝트 MOC]]

## 1. 배운 내용

### 1-1. protocol 모듈이 하는 일

Starter(팀 앱 안)와 서버가 주고받는 JSON의 **모양을 자바 타입으로 못 박아 둔 모듈**이다. 양쪽이 같은 record를 참조하니까 필드 하나를 바꾸면 반대쪽이 컴파일 에러로 바로 드러난다. 설계 규칙 1: "protocol 클래스는 필드 추가만, 삭제·이름 변경 금지."

팀 앱에 들어가는 모듈이라 **의존성이 0**이어야 한다. Spring·Jackson·Lombok 어노테이션도 쓰지 않는다. Jackson은 record의 생성자를 보고 알아서 역직렬화하므로 `@JsonProperty`가 필요 없다.

```groovy
// protocol/build.gradle — 테스트용 JUnit뿐
dependencies {
    testImplementation 'org.junit.jupiter:junit-jupiter:5.11.4'
    testRuntimeOnly 'org.junit.platform:junit-platform-launcher'
}
```

### 1-2. record 11개 — 전체 그림

```
EventBatch (POST /v1/events 본문)
├─ env: "local" | "prod"
├─ app: AppInfo (name, commit, dirty, hostHash)
├─ events: List<ErrorEvent>
│   └─ ErrorEvent (time, level, exceptionType, message, stack, causes, thread, phase)
│       ├─ stack:  List<StackFrame> (className, methodName, fileName, lineNumber)
│       ├─ causes: List<ErrorCause> (type, message)
│       └─ phase:  Phase { STARTUP, RUNTIME }
└─ droppedCount: int

HelloRequest (POST /v1/hello 본문, 앱 시작 후 1회)
├─ env, app
├─ javaVersion, springBootVersion
├─ dependencies: List<Dependency> (group, artifact, version)
└─ configKeys:   List<ConfigKey> (key, source: ConfigSource)   ← 값 없음

ProtocolConstants — 헤더·경로·상한값
```

### 1-3. 에러 쪽 네 개

```java
package dev.aiops.protocol;

/** 에러가 난 시점. STARTUP = 앱이 뜨다가 실패, RUNTIME = 뜬 뒤 요청 처리 중 */
public enum Phase { STARTUP, RUNTIME }
```

```java
/** 스택트레이스 한 줄. lineNumber는 모르면 -1 */
public record StackFrame(String className, String methodName, String fileName, int lineNumber) {}
```

```java
/** 원인 예외(cause) 체인의 한 칸. 스택은 싣지 않고 타입·메시지만 */
public record ErrorCause(String type, String message) {}
```

```java
import java.util.List;

/**
 * 에러 1건.
 * time: epoch millis (UTC)
 * stack: 바깥 예외의 프레임, 최대 ProtocolConstants.MAX_STACK_FRAMES
 * causes: 원인 예외 체인 (바깥 → 안쪽 순)
 * message: 마스킹된 메시지, 최대 ProtocolConstants.MAX_MESSAGE_LENGTH
 */
public record ErrorEvent(
        long time,
        String level,
        String exceptionType,
        String message,
        List<StackFrame> stack,
        List<ErrorCause> causes,
        String thread,
        Phase phase
) {
    public ErrorEvent {
        stack = stack == null ? List.of() : List.copyOf(stack);
        causes = causes == null ? List.of() : List.copyOf(causes);
    }
}
```

원인 예외(`causes`)에 스택을 안 싣는 이유: 바깥 예외 스택 30줄이면 이미 충분히 크고, 그룹화(6단계)는 바깥 스택의 팀 코드 프레임만 본다. 원인은 "무슨 타입이 왜"만 알면 된다.

### 1-4. 묶음과 앱 정보

```java
/**
 * 보내는 앱이 누구인지.
 * commit: git 커밋 해시(모르면 null), dirty: 커밋 안 한 변경이 있는지(모르면 null)
 * hostHash: 호스트명의 SHA-256 앞 12자. 호스트명 원문은 보내지 않는다
 */
public record AppInfo(String name, String commit, Boolean dirty, String hostHash) {}
```

```java
/**
 * POST /v1/events 본문.
 * droppedCount: 이 묶음을 보내기 전까지 버퍼가 꽉 차서 버린 개수 (Starter가 센다)
 */
public record EventBatch(String env, AppInfo app, List<ErrorEvent> events, int droppedCount) {
    public EventBatch {
        events = events == null ? List.of() : List.copyOf(events);
    }
}
```

`dirty`가 `boolean`이 아니라 `Boolean`인 건 "모름"(null)을 표현하려고. `.git` 폴더가 없는 환경(jar로만 배포된 앱)에서는 커밋도 dirty도 알 수 없다.

### 1-5. hello 쪽 네 개 — 값은 절대 없다

```java
/** 설정 키가 어디서 왔는지. 값은 어디에도 싣지 않는다 (규칙 6) */
public enum ConfigSource { YML, PROPERTIES, ENV, SYSTEM_PROPERTY, OTHER }
```

```java
/** 설정 키 이름과 출처만. 값 필드는 없고, 앞으로도 추가하지 않는다 (규칙 6) */
public record ConfigKey(String key, ConfigSource source) {}
```

```java
/** 클래스패스에서 읽은 라이브러리 하나. version은 모르면 null */
public record Dependency(String group, String artifact, String version) {}
```

```java
/** POST /v1/hello 본문. 앱이 준비된 뒤 1회 전송하는 환경 정보 */
public record HelloRequest(
        String env,
        AppInfo app,
        String javaVersion,
        String springBootVersion,
        List<Dependency> dependencies,
        List<ConfigKey> configKeys
) {
    public HelloRequest {
        dependencies = dependencies == null ? List.of() : List.copyOf(dependencies);
        configKeys = configKeys == null ? List.of() : List.copyOf(configKeys);
    }
}
```

`ConfigKey`에 값 필드가 없는 건 실수로 빠뜨린 게 아니라 **타입으로 막아 둔 것**이다. `spring.datasource.password` 같은 설정 "값"이 우리 서버로 넘어오는 사고를 코드 구조로 불가능하게 만든다. 서버가 아는 건 "이 앱에 `spring.datasource.url`이라는 키가 yml에 있다"까지.

### 1-6. 상수

```java
/** Starter와 서버가 같이 쓰는 상수. 바꾸면 양쪽 다 바꿔야 하므로 여기 한 곳에만 */
public final class ProtocolConstants {
    public static final String HEADER_API_KEY = "X-AIOPS-KEY";
    public static final String PATH_EVENTS = "/v1/events";
    public static final String PATH_HELLO = "/v1/hello";
    public static final String ENV_LOCAL = "local";
    public static final String ENV_PROD = "prod";
    public static final int MAX_BATCH_SIZE = 100;      // 한 묶음 최대 이벤트 수. 서버는 초과하면 400
    public static final int MAX_STACK_FRAMES = 30;     // 바깥 예외의 스택 프레임 최대
    public static final int MAX_MESSAGE_LENGTH = 2000; // 마스킹 후 메시지 최대 길이
    private ProtocolConstants() {}
}
```

## 2. 추가로 알면 좋은 활용법

### 2-1. 시간을 Instant가 아니라 long으로 둔 이유

설계 문서 초안엔 `Instant`였다. 그런데 `Instant`를 JSON으로 쓰려면 Jackson의 `jsr310` 모듈이 등록된 ObjectMapper가 필요하다. Spring Boot가 만든 ObjectMapper엔 들어 있지만, Starter가 자기 ObjectMapper를 직접 만들면(팀 앱의 Bean을 건드리지 않으려고 그럴 가능성이 크다) 모듈을 따로 등록해야 하고, 그 모듈 jar가 compileOnly 목록에 없다. `long`(epoch millis)이면 아무 의존 없이 된다. 서버에서 `Instant.ofEpochMilli()`로 바꾸면 끝.

### 2-2. compact constructor에서 List.copyOf

record의 compact constructor(`public ErrorEvent { ... }`)는 필드 대입 전에 값을 손볼 수 있는 자리다. 여기서 `List.copyOf`를 하면 (1) null이 빈 목록으로 바뀌어 NPE가 안 나고, (2) 바깥에서 리스트를 고쳐도 record 안의 복사본은 안 바뀐다(불변). 서버가 payload를 JSONB로 그대로 저장하므로 받은 객체가 중간에 변하면 곤란하다.

### 2-3. VS Code가 패키지를 `main.java.dev...`로 넣는다

11개 파일을 만들고 보니 첫 줄이 전부 `package main.java.dev.aiops.protocol;`이었다. VS Code의 Java 확장이 소스 루트를 못 잡아서 폴더 경로를 그대로 패키지로 넣은 것. Gradle은 `src/main/java`를 소스 루트로 알아서 빌드는 통과하지만, 서버에서 `import dev.aiops.protocol.*`을 못 찾게 된다.

전체 바꾸기(`Ctrl+Shift+H`)로 고치고 수정 커밋 하나. 근본 원인은 `settings.gradle`이 생기기 전에 폴더를 열어서 프로젝트 정보가 옛날로 캐시된 것 — `Ctrl+Shift+P → Java: Clean Java Language Server Workspace`로 해결. 왼쪽 아래 Java Projects 패널에 모듈 5개가 뜨면 정상.

## 3. 더 나아가 알면 좋은 것

### 3-1. 원자적 커밋

파일 하나에 커밋 하나, 한글 메시지로 11개를 나눠 올렸다.

```
feat(protocol): Phase 열거형 (STARTUP, RUNTIME) [AI-5]
feat(protocol): StackFrame 레코드 [AI-5]
…
feat(protocol): ProtocolConstants (헤더·경로·상한값) [AI-5]
fix(protocol): 패키지 선언을 dev.aiops.protocol로 수정 [AI-5]
```

나중에 "이 필드가 언제 왜 들어왔지"를 `git log -p`로 파일 단위로 추적하려고. PR은 Create a merge commit으로 머지해서 이 커밋들이 develop에 그대로 남는다.

### 3-2. 다음에 볼 키워드

- protocol 모듈에 Spring이 안 섞였는지 기계로 확인하는 테스트(`ProtocolPurityTest`) — 클래스패스에 `org.springframework`가 없음을 단언. 지금은 `grep`으로 확인만 했다
- 필드 추가가 필요해지면 — 새 필드는 null 허용으로 넣어야 구버전 Starter가 보낸 JSON도 서버가 받는다

## 관련 노트

[[AiOps 02 - Gradle 멀티 모듈 뼈대]] · [[AiOps 04 - CI와 PR 템플릿]]
