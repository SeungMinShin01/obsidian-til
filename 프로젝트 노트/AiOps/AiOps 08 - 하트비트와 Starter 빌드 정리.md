---
출처: Claude 대화
작성일: 2026-11-02
tags: [프로젝트, java]
---

# AiOps - 하트비트와 Starter 빌드 정리

> 허브: [[AiOps 프로젝트 MOC]]

**PR #4 `[AI-33] protocol 하트비트 추가·starter 빌드 정리`** — 머지 커밋 `9d6abb7`, 커밋 3개.

작은 PR이지만 두 사람이 이걸 딛고 선다. A는 2단계에서 `/v1/heartbeat` 수집 API를, 나는 3단계에서 전송 스레드의 60초 하트비트를 만든다. 그리고 Starter에서 Jackson을 뺐다.

## 1. 배운 내용

### 1-1. 왜 하트비트가 MVP에 들어왔나 (D-086)

hello는 앱이 켜질 때 1번만 간다. 그러면 콘솔에서 "이 팀 앱이 지금 연결돼 있나"를 알 수 없다 — 에러가 안 오는 게 앱이 멀쩡해서인지, 꺼져서인지, Starter가 죽어서인지 구분이 안 된다. Starter 안전성을 점검하다가 이 질문("Starter에서 오류가 나서 꺼지면 우리는 어떻게 아냐")이 나왔고, 원래 v0.6 기능(6-3)이던 하트비트를 당겼다. 보낼 에러가 없어도 60초마다 신호를 보내고, 서버는 3분 안에 신호가 있으면 "연결됨"으로 본다.

### 1-2. protocol 추가

```java
package dev.aiops.protocol;

/**
 * POST /v1/heartbeat 본문. 보낼 에러가 없어도 HEARTBEAT_INTERVAL_SECONDS마다 전송 (D-086).
 * 서버는 받으면 heartbeat_last.last_seen_at을 갱신하고, 3분 안에 신호가 있으면 "연결됨"으로 본다.
 * sentAt: epoch millis (UTC). ErrorEvent.time과 같은 형식
 */
public record Heartbeat(String env, AppInfo app, long sentAt) {
}
```

```java
package dev.aiops.protocol;

/* Starter와 서버가 같이 쓰는 상수. 바꾸면 양쪽 다 바꿔야 하므로 여기 한 곳에만 */
public final class ProtocolConstants {

    public static final String HEADER_API_KEY = "X-AIOPS-KEY";

    public static final String PATH_EVENTS = "/v1/events";
    public static final String PATH_HELLO = "/v1/hello";
    public static final String PATH_HEARTBEAT = "/v1/heartbeat";

    public static final String ENV_LOCAL = "local";
    public static final String ENV_PROD = "prod";

    /* 한 묶음에 담는 최대 이벤트 수. 서버는 초과하면 400 */
    public static final int MAX_BATCH_SIZE = 100;

    /* 바깥 예외의 스택 프레임 최대 개수 */
    public static final int MAX_STACK_FRAMES = 30;

    /* 마스킹 후 메시지 최대 길이 */
    public static final int MAX_MESSAGE_LENGTH = 2000;

    /* 보낼 에러가 없어도 하트비트를 보내는 주기 */
    public static final int HEARTBEAT_INTERVAL_SECONDS = 60;

    private ProtocolConstants() {
    }
}
```

- 시간은 `ErrorEvent.time`과 똑같이 epoch millis `long`(03의 2-1 — Instant는 Jackson jsr310 모듈이 필요).
- protocol은 **필드·클래스 추가만** 허용(규칙 1)이라 기존 record는 건드리지 않았다.
- "3분 이내 = 연결됨"은 서버만 쓰는 기준이라 protocol에 넣지 않았다. 양쪽이 같이 써야 하는 값만 여기에.

### 1-3. starter/build.gradle

```groovy
apply plugin: 'java-library'                     // api 의존성을 쓰려면 필요
apply plugin: 'io.spring.dependency-management'

dependencyManagement {
    imports {
        mavenBom "org.springframework.boot:spring-boot-dependencies:${springBootVersion}"
    }
}

dependencies {
    // 팀 앱이 protocol을 따로 넣지 않아도 컴파일 시점에 보이도록 api
    api project(':protocol')

    // 팀 앱이 이미 갖고 있는 것만 compileOnly. Starter는 새 의존성을 가져오지 않는다 (규칙 3)
    // JSON은 자체 JsonWriter. Jackson은 쓰지 않는다 (D-085)
    compileOnly 'org.springframework.boot:spring-boot'
    compileOnly 'org.springframework:spring-context'
    compileOnly 'ch.qos.logback:logback-classic'

    testImplementation 'org.springframework.boot:spring-boot'
    testImplementation 'org.springframework:spring-context'
    testImplementation 'ch.qos.logback:logback-classic'
    // JsonWriter 왕복 테스트용 (테스트에서만. Starter 본체에는 들어가지 않음)
    testImplementation 'com.fasterxml.jackson.core:jackson-databind'
    testImplementation 'org.junit.jupiter:junit-jupiter'
    testRuntimeOnly 'org.junit.platform:junit-platform-launcher'
}
```

바뀐 점 세 가지:

1. **`java-library` 플러그인** — `api` 설정을 쓰려면 필요하다.
2. **`implementation project(':protocol')` → `api`** — `implementation`이면 Starter를 받은 팀 앱의 **컴파일 시점에 protocol 클래스가 안 보인다.** JitPack으로 받는 쪽에서 `ErrorEvent` 같은 타입을 쓸 일이 생기면 깨진다. `api`는 "이 의존성은 내 공개 API의 일부"라는 선언이라 받는 쪽 컴파일 클래스패스까지 전달된다.
3. **Jackson `compileOnly` 삭제 (D-085)** — 이게 핵심.

### 1-4. Starter에서 Jackson을 뺀 이유

Spring Boot 4의 기본 JSON은 **Jackson 3**(`tools.jackson.*`)이다. Starter가 Jackson 2(`com.fasterxml.jackson.*`)를 `compileOnly`로 컴파일해 두면, Boot 4 팀 앱에는 그 클래스가 없어서 실행 중에 `NoClassDefFoundError`가 난다. 이건 `Exception`이 아니라 **`Error`**라서 `catch (Exception e)`로 감싸도 빠져나가 팀 앱 기동을 죽일 수 있다. "팀 앱을 절대 죽이지 않는다"는 북극성과 정면으로 부딪힌다.

| | Jackson 사용 | 자체 JsonWriter (선택) |
| --- | --- | --- |
| 얻는 것 | 직렬화 코드를 안 짜도 됨 | Boot 3·4 어디서든 동작, 팀의 ObjectMapper 설정(snake_case 등)에 휘둘리지 않음 |
| 잃는 것 | Boot 버전에 따라 팀 앱이 죽을 수 있음 | 80~100줄을 직접 짜고 테스트로 지켜야 함 |

JsonWriter는 record를 리플렉션으로 돌아 JSON을 만든다(3단계 AI-37). protocol에 필드가 추가돼도 고칠 필요가 없고, Jackson으로 다시 읽어 원래 record와 같은지 보는 **왕복 테스트**로 출력을 고정한다. 그래서 Jackson은 `testImplementation`에만 남겼다.

## 2. 추가로 알면 좋은 활용법

### 2-1. 정말 빠졌는지 기계로 확인

```powershell
./gradlew :starter:dependencies --configuration compileClasspath | Select-String jackson
```

출력이 비어 있으면 Starter의 컴파일 의존성에 Jackson이 없다. (`Picked up JAVA_TOOL_OPTIONS…`는 JVM이 늘 찍는 줄.) PowerShell에는 `grep` 대신 `Select-String`.

### 2-2. PR 제목 형식

이 PR부터 제목을 `[이슈키] 스토리 제목` 형식으로 맞췄다(PR #1과 같은 형식). 커밋 메시지는 계속 `타입(범위): 요약 [이슈키]`. 이슈 키가 들어가야 Jira 이슈의 "개발" 칸에 PR이 붙는다. 머지된 PR도 제목은 Edit으로 고칠 수 있지만, 머지 커밋 메시지에 들어간 옛 제목은 develop 이력이라 그대로 둔다.

## 3. 더 나아가 알면 좋은 것

### 3-1. JitPack에서 생길 함정 (10단계 메모)

JitPack 공식 문서를 읽어 보니 기본으로 `./gradlew build publishToMavenLocal`을 돌린다. `build`는 server의 Testcontainers 테스트까지 돌리는데 JitPack에 Docker가 있다는 말은 없다. 그래서 `jitpack.yml`에서 명령을 `:protocol:publishToMavenLocal :starter:publishToMavenLocal`로 좁히고 `jdk: openjdk17`을 지정한다(기본이 Java 8). 레포가 public이어야 무료다. 팀 앱 쪽엔 `content { includeGroup 'com.github.seungminshin01.aiops' }`로 JitPack을 우리 그룹에만 쓰게 한다.

### 3-2. 다음에 볼 키워드

- `api` vs `implementation` vs `compileOnly` — 누구의 클래스패스에 무엇이 실리나
- `Class.getRecordComponents()` — JsonWriter가 쓰는 record 리플렉션
- `NoClassDefFoundError` vs `ClassNotFoundException` — 앞은 Error(컴파일 땐 있었는데 실행 때 없음), 뒤는 Exception

## 관련 노트

[[AiOps 07 - 엔티티·리포지토리·Testcontainers]] · [[AiOps 09 - sample-app 에러 재현 앱]]
