---
출처: Claude 대화
작성일: 2026-11-15
tags: [프로젝트, java]
---

# AiOps - 환경 정보 hello와 EnvCollector

> 허브: [[AiOps 프로젝트 MOC]]

**PR #56 `[AI-47] 준비 완료 뒤 환경 정보(hello) 전송`** — 커밋 11개(새 파일 9, 수정 2), 11/15 PR. 앱이 준비되면 환경 정보를 한 번 모아 `/v1/hello`로 보낸다. AI 설명의 맥락(어떤 Java·Boot, 어떤 라이브러리)과 콘솔 "연결됨" 표시의 근거가 된다. **설정 값은 읽지 않는다.**

## 1. 배운 내용

### 1-1. 이 PR이 하는 일

```
Starter 시작 (startIfAbsent)
   └ GitInfoReader.read()  → AppInfo(앱 이름, 커밋, dirty=모름, 호스트 해시)   ← 에러 이벤트에도 실린다

ApplicationReadyEvent
   └ AiopsRuntime.submitHelloOnce(environment)        JVM당 1번
        DefaultEnvCollector.collect
           ├ javaVersion        Runtime.version()
           ├ springBootVersion  SpringBootVersion.getVersion()
           ├ dependencies       DependencyLister  (jar 파일 이름 → 이름·버전, 최대 300)
           └ configKeys         ConfigKeyLister   (키 이름 + 출처, 최대 500)
        sender.submitHello(hello)   → 전송 스레드가 다음 바퀴에 POST /v1/hello
```

새 패키지 `env/`에 다섯 개: `EnvCollector`(인터페이스), `DefaultEnvCollector`, `ConfigKeyLister`, `DependencyLister`, `GitInfoReader`.

### 1-2. 코드로 보기: 값을 읽지 않는다

```java
for (PropertySource<?> source : configurable.getPropertySources()) {
    if (!(source instanceof EnumerablePropertySource<?> enumerable)) {
        continue;                                             // ①
    }
    ConfigSource kind = kindOf(source.getName());             // ②
    for (String name : enumerable.getPropertyNames()) {       // ③ 이름만
        ...
        (file ? fromFiles : others).add(new ConfigKey(name, kind));
    }
}
```

| 번호 | 뜻 |
|---|---|
| ① | `PropertySource` = 설정이 들어 있는 통 하나(yml 파일, 환경변수, 시스템 속성…). 그중 "안에 든 이름을 나열할 수 있는" 통만 본다 |
| ② | 통의 이름으로 출처를 정한다. `.yml`이 들어 있으면 YML, `systemEnvironment`면 ENV… 모르면 OTHER |
| ③ | `getPropertyNames()`는 **이름 목록만** 준다. 이 클래스에는 `getProperty`(값 읽기) 호출이 하나도 없다 |

"가려서 보낸다"도 하지 않는다. 마스킹은 놓칠 수 있다. **읽지 않으면 샐 수 없다.** protocol의 `ConfigKey(key, source)`에 값 칸이 아예 없는 것도 같은 이유다.

테스트 `configValuesAreNeverIncluded`가 이것을 고정한다: 환경에 가짜 비밀번호를 넣고 → 모은 것을 JSON으로 바꾼 뒤 → 그 문자열에 값이 없고 키 이름은 있는지 본다. 객체의 칸을 보는 게 아니라 **실제로 나가는 글자**를 본다.

### 1-3. 코드로 보기: jar 파일 이름 → 이름과 버전

```java
private static final Pattern JAR = Pattern.compile("^(.+?)-(\\d[A-Za-z0-9._+\\-]*)\\.jar$");
```

- `(.+?)`: 가능한 **짧게** 잡는다(뒤의 `?`). 그래서 "`-숫자`가 처음 나오는 곳"에서 끊긴다.
- `spring-web-6.1.5.jar` → `spring-web` / `6.1.5`. `log4j-to-slf4j-2.24.3.jar` → `log4j-to-slf4j` / `2.24.3` (이름 속 `4j`는 앞이 `-`가 아니라서 버전으로 안 본다).
- `protocol.jar`처럼 버전이 없으면 건너뛴다.

보내는 것은 **파일 이름뿐**이다. 전체 경로에는 `C:\Users\이름\…`처럼 사용자 이름이 들어 있다.

```java
String classPath = System.getProperty("java.class.path", "");   // 개발 실행: 여기에 다 있다
...
if (loader instanceof URLClassLoader urlLoader) {               // 실행 jar: 여기서 찾는다
    for (URL url : urlLoader.getURLs()) { ... }
}
```

`java -jar app.jar`로 띄우면 `java.class.path`에는 `app.jar` 하나만 있다. 라이브러리는 jar 안의 jar(`BOOT-INF/lib/`)라서 Spring Boot의 클래스로더에게 물어야 한다. 주소 끝의 `!/`는 "jar 안의 jar"라는 표시라 떼고 이름만 남긴다.

### 1-4. 코드로 보기: git 명령 없이 커밋 읽기

```
.git/HEAD          "ref: refs/heads/main"   또는  40자 해시(브랜치 없이 커밋을 직접 가리킬 때)
.git/refs/heads/main   40자 해시
.git/packed-refs       "해시 refs/heads/main" 줄들 (브랜치 파일이 없을 때 여기 있다)
```

작업 폴더에서 위로 최대 10단계 올라가며 `.git` 폴더를 찾는다. `git` 명령을 실행하지 않는 이유: 팀 PC에 git이 PATH에 없을 수 있고, 프로세스 실행은 느리고 위험하다. JGit 같은 라이브러리는 "새 의존성을 가져오지 않는다"(규칙 3)에 걸린다.

읽은 값은 40자 16진수 모양일 때만 쓴다. 아니면 null.

### 1-5. dirty를 "모름"으로 둔 이유

명세는 "`.git/index` 파일의 수정 시각이 커밋 파일보다 최신이면 dirty"였다. 그런데 `git status`만 실행해도 git이 index를 고쳐 쓴다. 개발 PC에서는 거의 항상 true가 나온다. **틀린 값은 모름보다 나쁘다** — "커밋 안 한 코드에서 난 에러"라고 잘못 알리게 된다. `AppInfo.dirty`는 원래 "모르면 null"이 허용된 칸이다.

### 1-6. 커밋을 시작할 때 읽는 이유

명세는 hello 때 읽으라고 했지만, **Starter가 시작할 때** 읽어 `AppInfo`에 넣었다. `AppInfo`는 에러 이벤트·하트비트·hello 모두에 실린다. 그래서 서버의 `error_event.app_commit`에 "이 에러가 어느 커밋에서 났는지"가 남는다. 지금까지는 항상 null이었다.

### 1-7. hello는 덤이다

```java
public static void submitHelloOnce(Environment environment) {
    try { ... } catch (Throwable ignored) { }     // disable()을 부르지 않는다
}
```

다른 곳은 오류가 나면 Starter를 끈다(`disable`). hello는 실패해도 **끄지 않는다.** 환경 정보를 못 모았다고 에러 수집까지 멈출 이유가 없다. 모으는 부품도 각각 따로 실패한다 — 의존성 목록이 실패하면 빈 목록, 나머지는 그대로 보낸다.

## 2. 설계와 다르게 한 곳

명세가 protocol과 어긋나 있었다. protocol은 바꾸지 않았다(규칙 1).

| 명세 | 실제 | 이유 |
|---|---|---|
| 출처 = PropertySource 이름(문자열) | `ConfigSource` enum 5종 | protocol이 enum |
| `gitCommit`·`gitDirty`·`hostHash`·`startedAt`이 hello 칸 | 커밋·호스트는 `AppInfo` 안, `startedAt` 없음 | protocol에 그 칸이 없다 |
| git은 hello 때 | 시작 때 | 1-6 |
| dirty = index 시각 비교 | 항상 null | 1-5 |
| 앱 이름 없으면 메인 클래스 이름 | 기존 기본값 `unknown` | 이미 `AiopsSettings`가 정함 |
| 테스트 값 `my.token=abc` | `tok-9f3k2zz` | `abc`는 해시(16진수)나 라이브러리 이름에 우연히 들어가 테스트가 가끔 깨진다 |

## 3. 팁

- 기존 파일을 고칠 때 조각으로 받으면 넣을 자리를 찾다 실수한다. **고치는 파일은 전체 코드로** 받는다.
- 커밋 전에 `git status`에 건드리지 않은 파일(`ShutdownHookTest`)이 "수정됨"으로 떴다. 줄바꿈만 다른 것이라 커밋에 넣지 않았고, 커밋 뒤에는 표시가 사라졌다.
- 새 파일을 import하는 기존 파일은 **새 파일을 먼저 넣은 뒤** 고쳐야 컴파일된다.

## 4. 남은 것 (확인 못 한 것)

- 출처 판별: Spring Boot가 설정 파일 통에 붙이는 이름에 `.yml`이 들어 있다는 전제. 샘플 앱의 `app_snapshot`에서 yml 키가 `YML`로 찍히는지 확인 (틀리면 전부 OTHER. 값이 새는 문제는 아님)
- 환경변수 **이름**이 수백 개 실린다 (PC의 모든 환경변수 이름). 값은 없지만 "수집 범위 공개" 문서에 적어야 한다. 빼려면 한 줄 수정
- 운영 서버에는 `.git`이 없어 커밋이 null이다. 운영에서 커밋을 알려면 빌드할 때 넣는 방식이 따로 필요하다
- 수동 확인: 샘플 앱 실행 → 서버 `app_snapshot` 1행

## 관련 노트

[[AiOps 38 - 종료 훅 onJvmShutdown]] · [[AiOps 40 - 안전성 테스트 7종 (Boot 4)]]
