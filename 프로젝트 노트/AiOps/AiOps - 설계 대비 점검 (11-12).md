---
출처: Claude 대화
작성일: 2026-11-12
tags: [프로젝트]
---

# AiOps - 설계 대비 점검 (11/12)

> 허브: [[AiOps 프로젝트 MOC]]

origin/develop `da14c3a`(PR #42 머지 시점) 코드를 설계(레포 docs, Jira 명세, 대화 결정 D-092·094·095)와 하나씩 대조한 결과. 장부 성격이라 처리하면 각 줄에 처리 날짜를 단다.

## 0. 먼저 처리할 것 (요약)

| # | 항목 | 심각도 | 처리 |
|---|---|---|---|
| 1 | `JsonWriter` HEX 표 `"0123456789bcdef"` — `a` 빠짐. 0x0F·0x1F면 예외 → 묶음(최대 100건) 통째로 유실, 0x0B~0x0E·0x1A~0x1E(ANSI ESC 포함)는 잘못된 글자 | 높음 (확실) | hotfix PR |
| 2 | 서버 `spring.profiles.default: local` — 운영에서 프로필을 안 주면 시드 키(레포 공개)가 들어가고 세션 쿠키 secure=false | 높음 (배포 전) | 배포 전 고려사항에 추가 |
| 3 | `flushNow`가 마감을 묶음 사이에서만 확인 → 최악 약 10초. 시작 실패 3초·종료 2초(AI-45·46)를 못 지킴 | 중간 (5단계 전) | AI-45 때 수정 |
| 4 | 새 그룹 알림 연결이 develop에 없음 (B의 AI-60 브랜치에만). LLM 연결 지점도 거기 | 중간 | AI-60 머지 후 LLM |
| 5 | 정지된 팀 키 거부 미구현 (`ApiKeyResolver` 5단계 비어 있음) | 중간 | 13단계 정지(AI-85)와 함께 |
| 6 | `CallerRunsPolicy` + 커밋 후 리스너: 큐가 차면 요청 스레드에서 처리 → LLM 붙으면 수집 응답 지연·Starter 재시도·중복 저장 가능 | 중간 (추정) | LLM 전에 결정 |
| 7 | DevTools 재시작 시 sample-app에서 aiops-sender 2개 가능 (프로젝트 의존이라). jar 사용 팀은 해당 없음 | 낮음 (추정) | AI-49에서 확인 |
| 8 | Jira 상태 불일치: AI-82·87 머지됐는데 "할 일". LLM 파일 경로가 AI-12(`llm/`)와 AI-54(`client/`)에서 다름 → 서버 계층형(D-088)에 맞춰 `client/`·`service/`로 통일 | 메모 | 정리 |
| 9 | 레포 docs가 옛 버전(architecture v1.5, D-084~095·runtime/ 반영 안 됨) | 메모 | docs PR |
| 10 | 5단계 Jira 명세가 코드와 충돌: 키 이름 `aiops.key`(실제 `aiops.api-key`), `lifecycle/`·`AiopsLifecycleTest` 전제(실제 `runtime/`), SafetyTest가 WARN 로그 기대(실제 `System.err`), `DISABLED`가 JVM 전체라 SafetyTest는 JVM 분리 필요, AppInfo `commit=null` 고정, EnvCollector 시그니처 2개 | 중간 | 5단계 착수 전 명세 정리 |
| 11 | Logback 없는 앱(Log4j2)에서는 Starter 전체가 꺼짐. 팀 앱은 D-087로 안전 | 낮음 | AI-49에서 확인 |
| 12 | `StarterVersion`이 항상 `dev` — `starter/build.gradle`에 jar manifest 설정 없음 | 낮음 | build.gradle 몇 줄 |
| 13 | 메서드 참조(`::`) 남은 곳: `JsonWriter.java:73` 하나 | 메모 | MVP 후 리팩터링 |


## 1. Starter·protocol·sample-app

## Starter·protocol·sample-app 감사 (origin/develop @ da14c3a, 읽기 전용)

기준: 레포 `docs/aiops-v0.1-architecture.md`(develop에 있는 것은 **v1.5**, D-084~D-091 없음 — 프로젝트 문서는 v2.0), 프로젝트 `docs/mvp-requirements.md`(S-13·S-14 포함), `docs/mvp-worklist.md` v1.3, `CLAUDE.md`, Jira AI-8/9/10 + AI-35~49, 채팅 결정(D-092, D-094, runtime/·startIfAbsent, loggerName, 줄 번호 원값, phase 그대로 전달, 점 경계 무시 목록, LogbackAttacher 분리, disable 후 재활성 없음, D-095 제안, `::` MVP 후 정리).
경로 접두사 생략: `S/` = `starter/src/main/java/dev/aiops/starter/`.

---

### 1) 부품별 표

| 부품 | Jira | 상태 | 근거 파일 | 메모 |
|---|---|---|---|---|
| ⓟ protocol | (0단계) | 구현됨 | `protocol/src/main/java/dev/aiops/protocol/*.java` 13개 | record 11종 + `Heartbeat`(D-086). `ErrorEvent.loggerName`이 맨 뒤에 추가됨 + 옛 8인자 생성자 유지(합의 그대로). `StackFrame.lineNumber` 원값(-1/-2) 주석 있음. `ConfigKey`에 값 필드 없음. `protocol/build.gradle` 의존성 없음(junit만 test). P-02(추가만) 지켜짐 |
| ① AiopsSettings | AI-35 완료 | 구현됨 | `S/config/AiopsSettings.java`, `S/config/Defaults.java`, `S/config/StarterVersion.java` | 필드 7개·이름 일치. 키 없음 → `System.err` 한 줄 + null, enabled=false → 조용히 null, env 잘못된 값 → local+경고, buffer 100~10,000(기본 1,000), flush 1~60초(기본 5초), appName 기본 `unknown`. `toString`에서 키 `***`. 전체 `catch (Throwable)`. 기본 endpoint `https://ingest.aiops.invalid`(도메인 미정, 열린 질문 그대로). **StarterVersion은 MANIFEST `Implementation-Version`을 읽는데 `starter/build.gradle`에 jar manifest 설정이 없어 JitPack jar에서도 항상 `dev`**(확실) |
| ② AiopsEarlyInitializer / AiopsRuntime | AI-39 완료, AI-43 진행 중 | 구현됨 (설계와 다름: 패키지·메서드 이름 — 채팅 합의로 인정) | `S/runtime/AiopsEarlyInitializer.java`, `S/runtime/AiopsRuntime.java`, `S/runtime/LogbackAttacher.java`, `S/runtime/HostHash.java`, `starter/src/main/resources/META-INF/spring.factories` | `lifecycle/`→`runtime/`, `initOrGet`→`startIfAbsent`(합의). ORDER = `LoggingApplicationListener.DEFAULT_ORDER + 1` ✓. 세 시점(EnvPrepared/Prepared/Ready) 장착 확인 ✓. JVM당 1회(static volatile + LOCK, DCL) ✓. `onApplicationEvent` 전체 `catch (Throwable)` → `disable(t)` ✓, disable 1회만·`current()` null·재활성 없음 ✓, `[aiops] 비활성화됨: <타입> <메시지> (starter <버전>)` System.err ✓. spring.factories 키·클래스 정상(`dev.aiops.starter.runtime.AiopsEarlyInitializer`). **종료 훅 등록은 아직 없음**(②의 "종료 훅 등록"은 AI-46 몫). Jira AI-43 문서상 파일 경로(`lifecycle/`)·AI-39 "로거 dev.aiops.starter로 한 줄"은 갱신 안 됨 |
| ③ AiopsLogbackAppender | AI-42 진행 중 | 구현됨 | `S/capture/AiopsLogbackAppender.java` | `UnsynchronizedAppenderBase` ✓, 이름 `AIOPS` ✓, ERROR 이상 + throwableProxy 있는 것만 ✓, 무시 목록 3개 점 경계 비교 ✓, map→mask→offer ✓, `catch (Throwable)` + `addError` 최초 1회(예외 타입만, 메시지 없음) ✓, `accepted` 카운터 ✓, SLF4J 미사용 ✓ |
| ④ EventMapper | AI-40 완료 | 구현됨 | `S/capture/EventMapper.java`, `S/capture/DefaultEventMapper.java` | `map(ILoggingEvent, Phase)` + `mapThrowable(Throwable, Phase)`. 프레임 최대 30(`ProtocolConstants.MAX_STACK_FRAMES`) ✓, causes 최대 10단·IdentityHashMap 순환 방지 ✓, 메시지 null이면 formatted message ✓, 줄 번호 원값 ✓, phase 그대로 ✓, loggerName ✓(Throwable 경로 null), 실패 시 null ✓. Jira AI-45 본문의 `mapper.map(exception, ERROR, main, now, STARTUP)` 시그니처는 실제 `mapThrowable(t, Phase.STARTUP)`과 다름(문서 쪽 갱신 필요) |
| ⑤ Masker | AI-41 완료 | 구현됨 (Jira 본문과 일부 다름 — MaskerTest 기준) | `S/mask/Masker.java`, `S/mask/RegexMasker.java` | JWT·`aiops_[lp]_`·Bearer·이메일·키="값"·키=값·32자+ 영숫자 혼합·큰/작은따옴표·2,000자 자르기(서로게이트 보호)·PRE_CUT 10,000 ✓. D-094 NPE 템플릿이면 따옴표 규칙 생략 ✓. 실패 시 `""`(maskText) / 메시지·원인 비운 이벤트(mask) ✓. Jira AI-41 본문과의 차이: `Basic <토큰>` 규칙 없음, `authorization` 키 없음(값이 Bearer일 때만 가려짐), 자를 때 `…(truncated)` 접미사 없음, 긴 토큰에 `_ -` 미포함·숫자 필수. 🔴 MaskerTest가 통과 상태이므로 테스트가 기준이면 문제 없음 — 설계자 확인만 권장 |
| ⑥ EventBuffer | AI-36 완료 | 구현됨 | `S/transport/EventBuffer.java`, `S/transport/BoundedEventBuffer.java` | `ArrayBlockingQueue.offer`(대기 없음), null·꽉 참 → false + dropped++, `drainTo`, `takeDroppedCount` getAndSet(0), 1 미만이면 기본값 ✓ |
| ⑦ EventSender | AI-38 완료 | 구현됨 (flushNow 시간 상한은 설계와 다름 — 3) 참고) | `S/transport/EventSender.java`, `S/transport/BatchingEventSender.java` | 데몬 `aiops-sender` ✓, 200ms 루프, 100개 또는 flushInterval ✓, 실패 시 1초 뒤 1회 재시도 후 포기 ✓, 포기분 carriedDropped → 다음 droppedCount ✓, hello 1회(실패 포기) ✓, 60초 하트비트(같은 스레드) ✓, 루프 `catch (Throwable)` ✓, `stop()` interrupt + join(1000) ✓, Clock·Sleeper 주입 ✓. **`flushNow(maxWait)`는 묶음 사이에서만 마감 확인 + `sendLock` 대기 때문에 상한을 넘을 수 있음** |
| ⑧ Transport | AI-37 완료 | 구현됨 (JsonWriter 버그 1건) | `S/transport/Transport.java`, `S/transport/HttpTransport.java`, `S/transport/JsonWriter.java` | HttpClient 1개, connect 2s / request 3s, HTTP/1.1, `X-AIOPS-KEY`, `discarding()`, 2xx만 true, `catch (Throwable)`, Interrupted 복구, 첫 실패만 System.err(키 없음) ✓. JsonWriter record 리플렉션·캐시 ✓. **`HEX = "0123456789bcdef"`(15자, `a` 누락) — 확실한 버그**, 2) 위험 참조 |
| ⑨ reportStartupFailure | AI-45 할 일 | 미구현(5단계) | `S/runtime/AiopsEarlyInitializer.java:43` 주석만 | `AiopsRuntime.mapper()/masker()` getter와 `mapThrowable`은 준비됨 |
| ⑩ onJvmShutdown | AI-46 할 일 | 미구현(5단계) | — | `addShutdownHook` 코드 없음 |
| ⑪ EnvCollector | AI-47 할 일 | 미구현(5단계) | `S/runtime/HostHash.java`만 선행 | `env/` 패키지 없음. `AppInfo(name, null, null, hostHash)` 고정 |
| 안전성 테스트 7종 | AI-49 할 일 | 미구현(5단계) | — | `SafetyTest`·`FakeIngestServer`·`-PtestBoot`·`starter-boot3` CI job 없음 |
| sample-app | AI-48 완료, AI-44 할 일 | 부분 | `sample-app/**` | 엔드포인트 7종·`application-fail.yml`·`DbStartupCheck`·README ✓, DevTools `developmentOnly` ✓, `aiops.api-key: ${AIOPS_KEY:}` ✓(Jira AI-48/49의 `aiops.key`는 오타). **develop에서는 패키지가 `dev.aiops.sample`이라 앱 자신의 로거(`dev.aiops.sample.BoomController`)가 어펜더 무시 목록에 걸림 → `/boom/caught`는 수집 안 됨**(확실). `feat/sample-AI-44-milestone1`(764877e)에서 `com.example.sample`로 이름 변경 완료, 아직 미머지. 루트 README 절차도 그 브랜치에만 |

Jira 하위 작업 요약: AI-35·36·37·38·39·40·41 = 구현됨 / AI-42·43 = 구현됨(Jira 상태 '진행 중', develop에 머지 완료 — 상태 갱신 필요) / AI-44 = 부분(브랜치) / AI-48 = 구현됨 / AI-45·46·47·49 = 미구현(5단계 예정).

---

### 2) 규칙 위반·리팩터링 목록

| 항목 | 결과 | 위치 |
|---|---|---|
| 진입점 `catch (Exception)` | **없음**. 진입점은 전부 `Throwable` | `AiopsEarlyInitializer.java:30`, `AiopsRuntime.java:73`, `AiopsLogbackAppender.java:66`, `BatchingEventSender.java:87,130,139`, `HttpTransport.java:79`, `AiopsSettings.java:52` |
| 내부 `catch (RuntimeException)` | 진입점 아님(바깥 `Throwable`이 감쌈) — 문제 없음 | `AiopsSettings.java:100,113` |
| Starter 안 SLF4J 로깅 | **없음**. `LogbackAttacher`가 `LoggerFactory.getILoggerFactory()`만 호출(로그 출력 아님). 모든 출력은 `System.err` 또는 Logback `addError` | `S/runtime/LogbackAttacher.java:11-12,58` |
| 팀 앱 스레드에서 대기 | 없음 (Appender→Mapper→Masker→`ArrayBlockingQueue.offer`). 단, `AiopsEarlyInitializer`가 `ApplicationListener<ApplicationEvent>`라 Spring MVC의 `ServletRequestHandledEvent`(요청마다 발행, 기본 켜짐)를 Tomcat 스레드에서 받음 — `isDisabled()` + instanceof 몇 번이라 비용 무시 가능(추정, 동작상 문제 아님) | `AiopsEarlyInitializer.java:18,24` |
| 비밀값 로그 | 키 원문 출력 없음. `toString` 마스킹. 다만 `AiopsSettings.java:54`·`AiopsRuntime.disabledLine`이 `t.getMessage()`를 그대로 찍음 → 설정 플레이스홀더 해석 오류 등에서 설정 문자열이 메시지에 섞일 가능성(추정, 낮음) | `AiopsSettings.java:54`, `AiopsRuntime.java:125-129` |
| 메서드 참조 `::` (MVP 후 정리 대상) | **1곳**: `S/transport/JsonWriter.java:73` `Class::getRecordComponents`. (람다는 `BatchingEventSender.java:60` `d -> Thread.sleep(...)`, `:84` `() -> runLoop()` — `::` 아님) protocol·sample-app에는 없음 | |
| Jackson/새 의존성 main 범위 | 없음. `starter/build.gradle`: `api project(':protocol')`, `compileOnly` spring-boot·spring-context·logback-classic, jackson은 `testImplementation`만 ✓. main 소스에 jackson 문자열 없음 ✓ | `starter/build.gradle:12-25` |
| 규칙 7 패키지 | `runtime/`(합의로 `lifecycle/` 대체). `env/`는 아직 없음 | |
| 문서 불일치 | develop의 `docs/aiops-v0.1-architecture.md`는 v1.5(D-084~D-091·⑦ 하트비트·⑧ JsonWriter·③ 무시 로거 3개 반영 안 됨), `CLAUDE.md` "현재 단계: 1단계 진행 중"·규칙 7 `lifecycle`. D-092·D-094·D-095, runtime/ 이름, loggerName 추가는 레포 문서 어디에도 없음 | |

---

### 3) 위험

| # | 위험 | 근거 | 확실/추정 |
|---|---|---|---|
| R1 | **JsonWriter 제어문자 이스케이프 버그**: `HEX`에 `a`가 빠져 15자. `0x0F`, `0x1F` → `ArrayIndexOutOfBoundsException` → `post()`가 false → 재시도도 같은 실패 → **그 묶음(최대 100건) 전체 버림**(독약 이벤트). `0x0B/0x0C/0x0E`, `0x1A~0x1E`(예: ANSI `ESC`=0x1B → `\u001c`)는 다른 글자로 바뀜(유효 JSON이라 조용히 틀림). 테스트는 `\u0001`만 확인해 통과 | `S/transport/JsonWriter.java:17,108`, `JsonWriterTest.java:90` | 확실 |
| R2 | **`flushNow`가 시간 상한(시작 실패 3초·종료 2초)을 못 지킴**: ① 마감은 `sendBatch` 사이에서만 확인 → 첫 POST가 최대 3초(REQUEST_TIMEOUT)라 2초 상한 초과 가능 ② `sendLock`을 전송 스레드가 쥔 채 `send(3s) + sleep(1s) + send(3s)` 중이면 호출 스레드가 최대 ~7초 대기 후 자기 전송 3초 → 최악 ~10초. 서버가 꺼진(연결 거부) 경우는 즉시 실패라 영향이 작고, 응답 없는 서버(타임아웃)에서 커짐. 테스트는 정상 Transport로만 확인 | `BatchingEventSender.java:104-113,172-197`, `HttpTransport.java:24` | 확실(코드상), 실제 지연 크기는 추정 |
| R3 | **DevTools 재시작 시 aiops-sender 2개 이상**: sample-app은 `implementation project(':starter')`라 bootRun/IDE에서 starter가 jar가 아닌 클래스 디렉터리 → DevTools가 재시작 클래스로더에 넣음 → 재시작마다 `AiopsRuntime` static이 새로 생겨 새 sender 시작, 옛 sender(데몬)는 멈추지 않고 하트비트 계속 + 옛 클래스로더 누수. Logback은 기본 클래스로더라 어펜더는 리셋 후 새 것 1개만 붙음. JitPack jar로 받는 팀 앱에서는 발생 안 함. AI-43 확인 기준 "jstack에 aiops-sender 1개"가 sample-app에서 깨질 수 있음. AI-46 종료 훅도 클래스로더마다 1회씩 누적됨. 대응 후보: sample-app `META-INF/spring-devtools.properties`의 `restart.exclude.*`로 starter 출력 디렉터리 제외, 또는 JVM 전역 표식(System property 등)으로 중복 방지 | `sample-app/build.gradle:5,10`, `AiopsRuntime.java:29-30` | 추정 (jstack로 검증 필요) |
| R4 | **Logback 없는 앱(Log4j2 등)에서 Starter 전체 꺼짐**: `attachAppenderIfMissing` → `LogbackAttacher` 로딩 시 `LoggerContext` 등 `NoClassDefFoundError` → 리스너가 잡아 `disable` → 앱은 살지만 시작 실패 보고·하트비트·hello까지 모두 꺼짐. 팀 앱 기동은 안전 | `S/runtime/LogbackAttacher.java`, `AiopsEarlyInitializer.java:30-31` | 추정 (열린 질문 "1차 프로젝트 로깅" 미해결) |
| R5 | **develop의 sample-app 패키지 `dev.aiops.sample`** → 앱 로그가 무시 목록(`dev.aiops`)에 걸림. `/boom/caught` 수집 안 됨(README는 "예"). 나머지 `/boom/*`는 Tomcat 로거로 찍혀 수집됨. AI-44 브랜치 머지로 해결 | `sample-app/src/main/java/dev/aiops/sample/*`, `AiopsLogbackAppender.java:30` | 확실 |
| R6 | 호스트명 조회가 main 스레드에서 블로킹 가능: `HOSTNAME`은 보통 export 안 된 셸 변수라 macOS/Linux에서 `InetAddress.getLocalHost()`까지 감 → 일부 PC에서 수 초 기동 지연 | `S/runtime/HostHash.java:41-46`, `AiopsRuntime.java:67` | 추정 |
| R7 | StarterVersion이 항상 `dev` (MANIFEST 미설정) → 비활성 로그로 버전 추적 불가 | `starter/build.gradle`(jar manifest 없음) | 확실 |
| R8 | 첫 하트비트가 시작 60초 뒤(`lastHeartbeatAt = now`). hello(AI-47) 전까지는 콘솔 "연결됨"이 최대 1분 늦음 | `BatchingEventSender.java:72-74` | 확실(영향 작음) |
| R9 | 키 없음일 때 `DISABLED`가 세팅되지 않음 → DevTools 재시작마다 `[aiops] aiops.api-key 없음` 반복 출력 | `AiopsRuntime.java:61-64` | 확실(영향 작음) |
| R10 | `startIfAbsent`에서 `sender.start()` 뒤 예외가 나면 sender가 instance 없이 남음(현재 코드상 그 뒤 예외 가능성은 거의 없음) | `AiopsRuntime.java:70-71` | 추정(낮음) |

동시성 메모: `instance` volatile + LOCK DCL, `DISABLED` CAS, `sendLock`으로 전송 직렬화, `tick` 상태는 단일 스레드 — 이상 없음. `disable()`은 LOCK을 쥔 채 `sender.stop()`(join 1초) — 호출자가 main 리스너뿐이라 허용 범위.

---

### 4) 5단계 준비 메모

#### AI-45 reportStartupFailure
- 연결 지점: `AiopsEarlyInitializer.handle()`(`:35-44`)에 `ApplicationFailedEvent` 분기 추가 → `AiopsRuntime.reportStartupFailure(event.getException())`.
- 구현: `AiopsRuntime` static 메서드. `current()`가 null이면 즉시 리턴(키 없음·비활성) → `r.mapper().mapThrowable(t, Phase.STARTUP)` → `r.masker().mask(...)` → `r.buffer().offer(...)` → `r.sender().flushNow(Duration.ofSeconds(3))`.
- **충돌 1**: 지금 `onApplicationEvent`의 `catch (Throwable)`은 `disable(t)` → 비활성 한 줄을 찍음. Jira는 "시작 실패 분기의 오류는 조용히 버림(한 줄도 찍지 않음)" → `reportStartupFailure` 안에서 자체 `catch (Throwable)`로 삼켜야 함.
- **충돌 2**: R2 — `flushNow`가 3초를 보장하지 않음. 묶음 안 마감 확인 + `sendLock` 대신 tryLock(남은 시간) 또는 sender `stop()` 후 flush, 그리고 남은 시간이 3초 미만이면 요청 타임아웃을 줄이는 경로가 필요(Transport에 시간 인자를 추가하면 인터페이스 변경 → 설계자 확인).
- **충돌 3**: 🔴 `AiopsLifecycleTest`(설계자 선행)는 Jira상 `dev.aiops.starter.lifecycle` 패키지를 가정. 실제는 `runtime/` → 테스트 패키지·import를 설계자가 맞춰야 함. 레포에 이 테스트 파일·브랜치는 확인 못 함.
- 시작 실패 시 Logback 어펜더도 같은 예외 로그(“Application run failed”)를 RUNTIME으로 잡아 버퍼에 넣을 수 있음 → STARTUP/RUNTIME 중복 1쌍(추정, Spring은 이벤트 후 로그를 찍음). flushNow 이후 찍히는 로그라 대개 전송 전에 JVM 종료되지만 확인 필요.

#### AI-46 onJvmShutdown
- 등록 위치: `AiopsRuntime.startIfAbsent()`에서 `instance` 생성 직후(LOCK 안), static 플래그로 1회. `new Thread(...)`는 `::` 대신 람다(새 코드 `::` 금지 규칙). 스레드 이름 `aiops-shutdown`, 비데몬.
- 본문: `current()` null이면 리턴 → `sender().flushNow(2s)` → `sender().stop()`, 전체 `catch (Throwable)`.
- **충돌**: R2(2초 < 요청 타임아웃 3초), R3(DevTools 클래스로더마다 static 플래그가 새로 생겨 훅 누적 — "재시작 2회 후 훅 1회" 기준이 sample-app에서 깨질 수 있음). `disable()`도 훅을 `Runtime.removeShutdownHook`할지 결정 필요(현재 disable은 sender만 멈춤 → 훅은 `current()` null로 무해).

#### AI-47 EnvCollector / GitInfoReader
- 새 패키지 `S/env/`: `EnvCollector`, `DefaultEnvCollector`, `GitInfoReader`, `DependencyLister`. hostHash는 `S/runtime/HostHash.get()` 재사용(`HostHash.java:11` 주석에 명시).
- 연결: `AiopsEarlyInitializer.handle()`의 `ApplicationReadyEvent` 분기(현재 `attachAppenderIfMissing`만)에 `AiopsRuntime.onReady(...)` 추가 → `sender().submitHello(...)`(이미 구현).
- **충돌 1 (스펙 불일치)**: Jira AI-10은 `HelloRequest hello()`, AI-47은 `HelloRequest collect(Environment env)`. 설계자 확정 필요.
- **충돌 2 (AppInfo 불변)**: `AppInfo`는 `startIfAbsent`에서 `commit=null, dirty=null`로 만들어 `BatchingEventSender` final 필드에 박힘(`AiopsRuntime.java:67-69`, `BatchingEventSender.java:39`). Ready 때 Git을 읽으면 hello에만 commit이 들어가고 events·heartbeat는 계속 null. commit을 묶음에도 싣으려면 `GitInfoReader`를 `startIfAbsent`(main, EnvPrepared 시점)에서 호출해 AppInfo 생성 때 넣어야 함 — Jira AI-47 "Ready 때 1회"와 시점 조정 필요.
- 설정 키 수집은 `getPropertySources()` + `EnumerablePropertySource.getPropertyNames()`만, `getProperty` 금지. 현재 `AiopsSettings`의 `getProperty`는 aiops.*·`spring.application.name`만이라 규칙 6 범위 안.
- `SpringBootVersion.getVersion()`은 Boot 3·4 공통이나 compileOnly라 Logback 없는 앱과 같은 식으로 NoClassDefFoundError 가능성 — `catch (Throwable)`로 필드만 null.
- `ProtocolConstants`에 `ConfigSource` 매핑(YML/PROPERTIES/ENV/SYSTEM_PROPERTY/OTHER)은 PropertySource 이름으로 판별해야 함(Jira는 "출처 이름"이라 하나 protocol은 enum — 문서 차이).

#### AI-49 SafetyTest 7종
- **충돌 1**: 테스트 2 기대 "경고 1줄(`dev.aiops` 로거, WARN)" ↔ 실제 `System.err` 한 줄(AI-35·AI-43 지시). 판정 기준을 System.err로 맞춰야 함. 키 이름도 `aiops.key`가 아니라 `aiops.api-key`.
- **충돌 2**: 테스트 6의 실패 주입 훅(`aiops.test.fail-on-init` 시스템 속성)이 main 코드에 없음 → `AiopsRuntime.startIfAbsent` 초입에 1회 읽기로 추가 필요(설계상 허용된 유일한 테스트 훅).
- **충돌 3**: `DISABLED`는 JVM 전역이고 재활성 불가 + 블랙박스 테스트라 `resetForTest()`(package-private, `runtime`)를 못 부름 → 테스트 6 이후 같은 JVM의 다른 테스트가 전부 꺼진 상태. 테스트별 JVM 분리(`forkEvery 1` 또는 테스트 클래스 분리 + Gradle 설정)가 필요. 현재 `build.gradle`·`starter/build.gradle`에 fork 설정 없음.
- 테스트 4(1,500회, 서버 10초 지연)에서 `EventBuffer` 크기를 블랙박스로 보려면 수단이 없음(가짜 서버 수신량·droppedCount로 간접 판정해야 함). droppedCount는 서버 지연 때문에 테스트 시간 안에 도착 안 할 수 있음.
- 테스트 7은 HttpClient 로그를 JUL→SLF4J 브리지로 Logback에 보내야 재현됨(Boot 기본 브리지 설치 여부 확인 필요). 무시 목록 점 경계 비교는 이미 구현.
- `-PtestBoot=3`: `starter/build.gradle`의 `dependencyManagement`가 `springBootVersion` BOM 하나라 테스트 범위만 3.5.x로 바꾸는 분기 추가 필요. `LoggingApplicationListener.DEFAULT_ORDER`는 컴파일 상수라 3.x에서도 문제 없음(추정).
- R1(JsonWriter) 수정 없이 테스트 5가 통과하더라도 제어문자 입력이 없으면 버그를 못 잡음 → `0x0F/0x1F/0x1B` 왕복 케이스는 JsonWriterTest(D-080 대상 아님, 담당자 테스트)에 추가 권장.

확인 못 함: 설계자 선행 `AiopsLifecycleTest` 존재 여부(레포·원격 브랜치에 없음), DevTools 2중 sender 실측, Logback 없는 앱 실측, Boot 3.x 실행.


## 2. 서버

## AIOps 서버 감사 (origin/develop, 읽기 전용)

- 기준: `origin/develop` = `da14c3a` (2026-11-12 10:53 +0900, PR #42까지). 파일 경로는 `server/src/main/java/dev/aiops/server/` 기준 상대 경로(이하 `S/`).
- 설계 출처: 레포 `CLAUDE.md`, Project 문서 `aiops-v0.1-architecture.md`(v2.0), `v0.2-multitenancy.md`, `v0.3-web-console.md`, `mvp-requirements.md`, `mvp-worklist.md`, Jira AI-7·11~14·16~21 및 하위 작업, 채팅 결정(D-092 등).
- develop에 안 들어간 서버 브랜치는 **`origin/feat/server-AI-60-milestone2` 1개뿐** (커밋 `8bc95d2`, 1개). 나머지 server 브랜치는 전부 develop에 머지됨.

#### B의 AI-60 브랜치 내용
- `S/service/ErrorProcessor.java`: `Notifier` 주입(`@Autowired` 2인자 생성자) + 테스트용 1인자 생성자(`NO_NOTIFY` 무동작 Notifier). 새 그룹 루프에서 `notifier.notifyNewGroup(tenantId, groupId)`를 그룹별 try/catch로 호출. 그 바로 앞에 `// TODO(7단계 AI-12): explanationService.explain(tenantId, groupId)` 주석 자리.
- `server/src/test/java/dev/aiops/server/EndToEndFlowTest.java`: 실제 HTTP `/v1/events` → JDK `HttpServer` 가짜 웹훅 → POST 1번, embed에 `"설명 준비 중"` 포함을 **단언**, 같은 에러 1건 더 → 추가 POST 없음·횟수 2. (Jira AI-60은 `MockRestServiceServer`·`FakeLlmClient`를 말하지만 B는 JDK HttpServer 사용, 설명은 아직 없음)
- `docs/milestones.md`: 마일스톤 2 체크리스트 뼈대, 수동 확인 전부 미확인, "막혀 있는 것: 7단계 LLM, Starter 실제 전송".

---

### 1) 단계별 표

상태: 구현됨 / 부분 / 미구현 / 설계와 다름

| 단계 | Jira | 상태 | 근거 | 메모 |
|---|---|---|---|---|
| 2 키 인증 ⑫ | AI-30 | 구현됨 | `S/security/ApiKeyResolver.java`, `ApiKeyHasher`, `ApiKeyCache` | SHA-256 해시 조회, 폐기 키 거부, 음성 캐싱 없음. **정지 팀 거부 없음**(5번 주석 "13단계에서 추가" 그대로) → AI-85 몫 |
| 2 이벤트 수집 ⑬ | AI-31 | 구현됨 | `S/controller/IngestController.java`, `IngestBodySizeFilter`(413), `IngestService.validate`(>100 → 400), `IngestService.store` | env는 키 기준, 본문 env 불일치는 WARN만. payload JSONB 원문 저장 |
| 2 커밋 후 처리 요청 | AI-32 | 구현됨 | `S/service/ErrorsStored.java`, `ErrorsStoredListener`(`@TransactionalEventListener(AFTER_COMMIT)`) | "커밋 후 처리 요청" 규칙 충족 |
| 2 hello·하트비트 | AI-33 | 구현됨 | `S/service/HelloService.java`, `HeartbeatRecorder`, `HeartbeatLastRepository.touch`(ON CONFLICT) | D-086 충족. hostHash 없으면 기록 생략 |
| 2 ingest.http | AI-34 | 구현됨 | `server/http/ingest.http` | |
| 6 처리 풀 | AI-50 | 구현됨 | `S/config/AsyncConfig.java`(`aiopsProcessingExecutor`, threads 4/queue 1000, **CallerRunsPolicy**), `ErrorProcessor.process(Long, List<Long>)` | D-081 시그니처 고정 충족. CallerRuns 위험은 3절 |
| 6 지문 🔴 | AI-51 | 구현됨 / 문서와 다름(경미) | `S/service/Fingerprinter.java` | 접두사 10개(`javax.`·`org.apache.`·`dev.aiops.` 추가). worklist W06-2 문서는 7개. 설계자 선행 테스트 기준이라 문서 갱신만 필요(추정) |
| 6 그룹 upsert | AI-52 | 구현됨 | `S/service/GroupUpserter.java`(ON CONFLICT, `xmax = 0`로 isNew), `GroupingService.groupOne`(이벤트당 짧은 tx, `assignGroup` → processed=true) | 예외 타입 = 원인 체인 맨 안쪽 |
| 6 재처리 | AI-53 | 구현됨 | `S/scheduler/ReprocessScheduler.java`(팀 순회 set→조회→clear, D-082), `SchedulingConfig` | **설명(LLM) 재시도 루프 없음** → AI-57 몫 |
| 7 LLM 호출 ⑮ | AI-54 | 미구현 | `LlmClient`·`LlmPrompt`·`OpenAiCompatibleLlmClient`·`FakeLlmClient`·`LlmConfig` 없음. `application.yml`에 `aiops.llm.*` 없음, `infra/prod/.env.example`에 `AIOPS_LLM_API_KEY` 없음 | 4절 |
| 7 프롬프트 | AI-55 | 미구현 | `PromptBuilder` 없음 | |
| 7 저장·연결 | AI-56 | 미구현 (자리만 있음) | `ErrorGroupEntity.explain(String)`(엔티티 변경 메서드)·컬럼 `ai_explanation`/`ai_explained_at`(V1) 존재, `ErrorGroupRepository`에 `updateExplanationIfNull` 없음, `ExplanationService`/`ExplanationStore` 없음 | AI-60 브랜치에 TODO 자리 |
| 7 일일 상한 | AI-57 | 미구현 (테이블만) | `llm_usage(day PK, call_count)` V1, `LlmUsageEntity`, 빈 `LlmUsageRepository` | `LlmQuota` 없음 |
| 8 알림 ⑯ | AI-58 | 구현됨 | `S/notify/Notifier.java`, `DiscordWebhookNotifier.java`, `DiscordEmbedBuilder.java` | 예외 밖으로 안 던짐, 예외 객체 로그 안 남김(웹훅 url 보호). embed는 `ai_explanation`을 "원인 후보/확인 방법/해결 방향" 순서로 찾아 3칸, 없으면 "설명 준비 중". D-090에 따라 `notify/` 패키지 임시 인정 |
| 8 채널 선택·제한 | AI-59 | 구현됨 | `webhookFor(tenant, env)`, `notify_local`, SUSPENDED 팀 생략, `NotifyRateLimiter`(팀별 분당 10) | |
| 8 마일스톤 2 | AI-60 | 부분 (develop 미머지) | develop의 `ErrorProcessor`는 새 그룹 수만 로그("트랜잭션 밖. 지금은 로그만"). 연결은 `feat/server-AI-60-milestone2`에만 | **develop에서는 새 그룹 알림이 아예 안 나감** |
| 9 보관 삭제 ⑰ | AI-61 | 구현됨 | `S/scheduler/RetentionScheduler.java`(04:00 Asia/Seoul, 팀 순회), `ErrorEventPurger`(묶음별 tx), `ErrorEventRepository.deleteOlderThan` | error_event만 삭제 |
| 9 수집 통계 | AI-62 | 구현됨 | `S/service/IngestStatRecorder.java`(ON CONFLICT, 서울 날짜, 음수 보정) | store와 같은 tx |
| 11 격리 전체 | AI-69~75 | 구현됨 | `S/security/TenantContext.java`, `TenantTransactionManager.java`(`set_config(...,true)`), `S/config/JpaConfig.java`, `db/migration/V2__rls.sql`(5개 테이블 USING+WITH CHECK+NULLIF), `ApiKeyAuthFilter`(set/finally clear), `ErrorProcessor`(첫 줄 set/finally clear) | grafana_ro 컬럼 권한도 V2·V3 |
| 12 V3 | AI-77 | 구현됨 | `V3__console.sql`, `V4__admin_access_log_append_only.sql` | cohort.name UNIQUE 없음(기존 지적) 그대로 |
| 12 GitHub 로그인 | AI-78 | 구현됨 | `GithubLoginSuccessHandler`, `GithubLoginFailureHandler`, `AppUserService.upsertFromGithub`, `MeController` | access token은 기본 `InMemoryOAuth2AuthorizedClientService`에 남음(기존 지적, 여전) |
| 12 보안 체인 | AI-79 | 구현됨 | `S/security/SecurityConfig.java`(`/v1/**` 키 STATELESS, `/api/**`·`/oauth2/**`·`/login/**`·`/logout` 세션+CSRF 쿠키) | 두 체인 밖 경로 무방비·forward-headers 없음(기존 지적, 여전) |
| 12 MembershipGuard | AI-80 | 구현됨 | `S/security/MembershipGuard.java`, `S/config/WebMvcConfig.java` | 경로에서 직접 teamId 파싱, 요청마다 DB, SUSPENDED 403+reason, afterCompletion clear |
| 12 역할·관리자 | AI-81 | 구현됨 | `RequireOwner`(`@Target(METHOD)`만, 기존 지적 여전), `RequireOwnerInterceptor`, `AdminGuard`, `AdminProperties` | |
| 13 기수 | AI-82 | 구현됨 (Jira는 "할 일") | `S/controller/admin/CohortController.java`, `CohortService`, `AdminExceptionHandler` | Jira 상태 갱신 필요. 이름 중복은 `existsByName` 선검사뿐(경합 시 중복 가능) |
| 13 팀 일괄 생성 | AI-83 | 미구현 | `AdminTeamController`·`AdminTeamService` 없음. `TeamCreated` 레코드·`DiscordProvisionListener.onTeamCreated`만 있고 **발행하는 곳 없음** | **설계와 다름**: Jira AI-83은 `DiscordProvisioner` 인터페이스+`NoopDiscordProvisioner`를 만들라고 하지만 develop에는 이미 구체 클래스 `S/service/DiscordProvisioner.java`와 AFTER_COMMIT 이벤트 경로가 있음 → AI-83은 `publishEvent(new TeamCreated(id))`만 하면 됨(TeamCreated.java 주석과 일치). Jira 문구 정리 필요 |
| 13 조장 초대 링크 | AI-84 | 부분 | `InvitationService.issue(tenantId, OWNER, 1, ttl, adminId)` 존재(토큰 32바이트 base64url·`new SecureRandom()`·sha256Hex만 저장 = 채팅 결정과 일치). **관리자 엔드포인트 `/api/admin/teams/{teamId}/owner-invite` 없음**, `aiops.invite.owner-ttl` yml에만 있고 읽는 코드 없음 | Jira AI-84의 `getInstanceStrong()`은 채팅 결정(new SecureRandom)으로 대체됨 — 코드가 맞음 |
| 13 정지·재개 | AI-85 | 미구현 | 정지 API 없음, `TeamSuspended`/`TeamResumed` 발행처 없음, `ApiKeyResolver` 정지 체크 없음, 팀 키 일괄 evict 메서드(`findAllHashesByTenantId`) 없음 | 소비 쪽(`DiscordProvisioner.suspend`, Notifier·MembershipGuard의 SUSPENDED 처리)은 준비됨 |
| 13 전체 현황 | AI-86 | 미구현 | `AdminOverviewController`/`Service`/`TenantStatsQuery` 없음 | |
| 13 접근 기록 | AI-87 | 구현됨 (Jira는 "할 일") | `S/security/AdminAccessLogInterceptor.java`(afterCompletion, 패턴·상태만, 본문 미기록), `AdminAccessLogService`(REQUIRES_NEW), `AdminAccessLogController`, V4 REVOKE | Jira 상태 갱신 필요 |
| 13 채널 재시도(M-07) | (AI-83/92 범위) | 미구현 | 재시도 엔드포인트 없음 | `DiscordProvisioner.provision`(멱등, IN_PROGRESS 잠금)은 있음 |
| 14 초대 수락 | AI-105 | 구현됨 (기존 지적 여전) | `InvitationController.accept`, `InvitationService.accept`(조건부 UPDATE `incrementUsedCount`, OWNER면 `activateByOwner`, next=`key-guide`/`errors`) | 사용 끝난 링크를 조장이 다시 열면 410 — `used_count >= max_uses` 검사가 기존 멤버 확인보다 앞(기존 지적 확인) |
| 14 키 발급·폐기 | AI-88 | 구현됨 (D-092) | `S/controller/admin/AdminKeyController.java`(POST 201 원문 1회, DELETE 204/404), `TeamKeyController`(GET 목록만), `ApiKeyService`(AFTER_COMMIT evict), `ApiKeyResolver` last_used_at | `KeyIssued.toString()` 원문 제외. 로그에 원문 없음 |
| 14 팀원 초대·관리 | AI-89 | 구현됨 | `InvitationController`(발급/목록/무효화 @RequireOwner), `MemberController`, `MemberService.remove`(즉시 커밋 → 다음 요청 403, 역할 회수) | |
| 15 디스코드 | AI-90~94 | 구현됨 | `S/client/DiscordApiClient.java`, `DiscordOAuthClient`, `S/service/DiscordProvisioner.java`(멱등·자원마다 REQUIRES_NEW 저장), `DiscordJoinService`/`DiscordJoinController`(state 서명, 토큰 지역 변수만), `DiscordProvisionListener`(TeamCreated/Suspended/Resumed) | 트리거(13단계 API)가 없어 실제로 돌 경로가 없음 |
| 16 목록 | AI-95 | 미구현 | `ErrorGroupController`·`ErrorGroupQueryService` 없음, `ErrorGroupRepository`는 `findByTenantIdAndFingerprint`만 | |
| 16 상세 | AI-96 | 미구현 | 없음 | |
| 16 상태·평가 | AI-97 | 미구현 | `ErrorGroupEntity`에 status/feedback 컬럼만, 변경 메서드 없음, GroupUpserter 재오픈 없음 | |
| 16 연결 확인 | AI-98 | 미구현 | `ConnectionController` 없음, `aiops.console.connected-within` 없음 | `HeartbeatLastRepository.findByTenantIdAndEnv`만 |

요약: 2·6·8(마일스톤 제외)·9·11·12·14·15 완료. **7단계 전부, 13단계 중 83·84(엔드포인트)·85·86, 16단계 전부 미구현.** Jira 상태 중 AI-82·AI-87은 실제로는 구현·머지됨.

---

### 2) 규칙 점검

| 규칙 | 결과 | 근거 |
|---|---|---|
| D-023 RLS 없는 테이블은 tenant_id 고정 조건 | 대체로 지킴 | `ApiKeyRepository.findAllByTenantIdOrderByCreatedAtDesc`/`findByIdAndTenantId`, `InvitationRepository.findAllByTenantIdAndExpiresAtAfter…`/`findByIdAndTenantId`, `MembershipRepository.findByUserIdAndTenantId`/`deleteByUserIdAndTenantId`. 주의 1건: `ApiKeyService.revoke(Long keyId)`가 **public이고 팀 조건 없음**(현재는 `revoke(tenantId, keyId)`와 테스트만 호출). 이후 팀 API에서 직접 부르면 다른 팀 키 폐기 가능 → package-private 권장(추정 위험) |
| 규칙 10 비밀값 로그·응답 | 지킴 | 키: 원문은 `KeyIssued` 1회, 로그는 keyId·해시 앞 8자. 초대: `Issued.toString` 원문 제외, 로그에 토큰 없음. 웹훅: `DiscordWebhookNotifier`·`DiscordProvisioner`는 예외 객체·url 미기록. 디스코드 access token 지역 변수만. `client/` 패키지에 로그 호출 없음. 접근 기록은 본문 미기록 |
| 규칙 10 "두 번 반환 금지" | 지킴 | 키 목록 `ApiKeySummary`는 prefix(12자)만, 초대 목록 `InviteSummary`는 원문·해시 없음 |
| 규칙 14 `/api/teams/{teamId}/**`는 MembershipGuard | 지킴 | 팀 경로 컨트롤러 3개(`TeamKeyController`, `MemberController`, `InvitationController` 팀 부분) 모두 `/api/teams/{teamId}/…` 아래, `WebMvcConfig`가 `/api/teams/**`에 등록. 예외 경로 `/api/discord/connect?teamId=`·`/api/invitations/{token}/accept`는 서비스가 직접 멤버십/토큰 확인 |
| 규칙 15 관리자 접근 기록 | 지킴 | `/api/admin/**` 전부 `AdminGuard → AdminAccessLogInterceptor`. 가드가 막은 403은 미기록(의도, 클래스 주석) |
| LLM 트랜잭션 밖 | 해당 없음(미구현) | 연결 지점(`ErrorProcessor.process`의 그룹화 루프 이후)은 트랜잭션 밖이 맞음 — `process`에 `@Transactional` 없음, `groupOne`만 tx |
| 커밋 후 처리 요청 | 지킴 | `IngestService.store` → `publishEvent(ErrorsStored)` → `ErrorsStoredListener` AFTER_COMMIT |
| D-081 `process(tenantId, ids)` | 지킴 | `ErrorProcessor.process(Long tenantId, List<Long> eventIds)`, 리스너·재처리 모두 이 형태 |
| v0.2 규칙 10 set한 곳이 finally clear | 지킴 | `ApiKeyAuthFilter`, `MembershipGuard.afterCompletion`, `ErrorProcessor`, `ReprocessScheduler.unprocessedOf`, `RetentionScheduler` |
| 규칙 11 팀 테이블 RLS | 지킴 | V2: error_event·error_group·app_snapshot·ingest_stat·heartbeat_last |
| 규칙 3 새 의존성 | 지킴 | `server/build.gradle`: webmvc·jpa·validation·flyway·security·oauth2-client·postgres·lombok(D-089)·testcontainers |

---

### 3) 위험·버그 (새로 본 것)

마일스톤 2·첫 배포를 막는 것부터.

1. **[확실·마일스톤 2 차단] develop에는 알림 연결이 없다.** `S/service/ErrorProcessor.java`는 새 그룹을 로그로만 남긴다. 연결은 `feat/server-AI-60-milestone2`에만 있고, 그 브랜치의 `EndToEndFlowTest`는 `"설명 준비 중"`을 단언한다 → 7단계가 들어오면 이 테스트를 바꿔야 함(규칙 9: 설계자 승인 별도 PR). 머지 순서: AI-60 먼저 → 7단계는 그 위에 `explain` 한 줄 + 테스트 갱신 PR.
2. **[확실·첫 배포 위험] 기본 프로필이 `local`.** `application.yml` `spring.profiles.default: local`, `application-local.yml`은 DB를 `localhost`로 덮고 Flyway `locations`에 `db/seed`를 넣는다. 운영에서 `SPRING_PROFILES_ACTIVE`를 빼먹으면 `R__seed_local.sql`이 돌아 **원문이 레포에 적힌 로컬 시드 키를 가진 팀 1**과 조장 계정이 운영 DB에 생기고, 세션 쿠키 `secure: false`가 됨. `infra/prod/.env.example`에 `SPRING_PROFILES_ACTIVE`·`AIOPS_DB_*`·`AIOPS_LLM_API_KEY` 줄이 없음. 운영 compose/Dockerfile은 레포에 없음(확인 못 함).
3. **[확실] 정지 팀 키가 계속 수집됨.** `ApiKeyResolver` 5번 자리 비어 있음. AI-85 전까지 정지해도 `/v1/**` 202. (Notifier·콘솔은 정지 처리하므로 알림은 안 감)
4. **[추정] CallerRunsPolicy + AFTER_COMMIT 조합.** 처리 풀 대기줄(1000)이 차면 `process`가 **요청 스레드의 AFTER_COMMIT 콜백 안에서** 돈다. (a) Spring 문서상 afterCommit 단계에서 REQUIRED `@Transactional`(`groupOne`)은 끝난 원 트랜잭션에 "참여"해 쓰기가 커밋되지 않을 수 있음(REQUIRES_NEW 필요). (b) 7단계가 붙으면 LLM 20초×새 그룹 수만큼 `/v1/events` 응답이 막혀 Starter 3초 타임아웃 → 1회 재시도 → **이미 커밋된 묶음이 중복 저장**(횟수 부풀림). 대안: 처리 풀 거절 시 버리고(processed=false라 재처리가 줍는다) 로그만 — 설계자 결정 필요.
5. **[추정] 새 그룹 다수일 때 처리 스레드 장시간 점유.** 한 묶음(최대 100개)이 전부 새 그룹이면 `explain`이 순차 20초씩 → 스레드 4개가 금방 묶임 → 4번과 연결. 일일 상한(200)과 별개로 "한 process 호출당 설명 N개까지, 나머지는 재시도 루프로" 같은 제한 고려.
6. **[추정·설계 구멍] 알림 유실.** 그룹화 tx 커밋(processed=true) 후 알림 전에 서버가 죽으면 그 그룹 알림은 영영 안 감(재처리는 processed=false만 줍고, AI-57 재시도는 설명만). MVP 허용 범위인지 확인 필요.
7. **[추정] 수집 1건 오류가 묶음 전체를 롤백.** `error_event.host_hash VARCHAR(16)`, `app_commit VARCHAR(64)`, `app_name VARCHAR(200)`, `heartbeat_last.host_hash VARCHAR(16)` — Starter가 더 긴 값을 보내면 `store` 트랜잭션 전체 실패 → 500, 이벤트 100개 손실. 서버 쪽 길이 절단 없음.
8. **[확실·경미] `@Async`(무지정)인 `DiscordProvisionListener`는 기본 실행기 해석에 의존.** `AsyncConfig`가 `getAsyncExecutor()`를 정의하지 않고 TaskExecutor 빈이 2개(`aiopsProcessingExecutor`, `aiopsScheduler`)라 Spring이 `SimpleAsyncTaskExecutor`(호출마다 새 스레드)로 떨어질 가능성이 큼(추정). 팀 일괄 생성 50개면 스레드 50개.
9. **[확실·경미] 초대 수락이 팀 상태를 안 봄.** MEMBER 링크로 SUSPENDED·WAITING_OWNER 팀에도 합류 가능(`InvitationService.accept`). 합류 후 MembershipGuard가 SUSPENDED는 막지만 WAITING_OWNER는 통과.
10. **[확실·문서] Jira 파일 경로 불일치.** AI-12 본문은 `llm/`·`processing/` 패키지, AI-54는 `client/`, AI-55~57은 `service/`, AI-56은 `repository/ErrorGroupRepository.java`(실제는 `model/repository/`). D-088 기준으로 `client/`(LlmClient·LlmPrompt·OpenAiCompatibleLlmClient·FakeLlmClient), `config/LlmConfig`, `service/`(PromptBuilder·ExplanationService·ExplanationStore·LlmQuota), `model/repository/ErrorGroupRepository`로 통일 권장.
11. **[확실·문서] AI-83의 `DiscordProvisioner` 인터페이스/Noop 지시는 develop과 충돌**(1절 13단계 행). 구현자가 Jira대로 인터페이스를 새로 만들면 기존 구체 클래스와 이름이 겹침.

기존 지적 재확인(새 항목 아님, 전부 **여전히 존재**): 조장 재접속 410(`InvitationService.accept` 검사 순서), GitHub access token 인메모리 보관(`SecurityConfig`에 `authorizedClientService`/`OAuth2AuthorizedClientRepository` 설정 없음), `server.forward-headers-strategy` 없음(`application.yml`), 두 체인 밖 경로 보호 없음(`SecurityConfig` securityMatcher), `@RequireOwner` `@Target(METHOD)`만, `cohort.name` UNIQUE 없음(V3). D-093(env 그룹 키)은 미반영 — 현재 지문은 env 무관, `error_group.first_env` 하나라 local에서 먼저 난 그룹이 prod에서 재발하면 **prod 채널 알림 없음**(D-093 결론 필요). D-095 관련: `GroupingService`는 `causes` 마지막을 타입으로 쓰므로 Starter가 root cause만 보내도 지문은 일관(추정).

---

### 4) LLM 7단계 연결 지점

#### 4-1. "새 그룹"이 생기는 곳과 트랜잭션 경계
```
POST /v1/events (Tomcat)
  ApiKeyAuthFilter: TenantContext.set ─ finally clear
  IngestService.store  @Transactional ─ error_event INSERT, ingest_stat, heartbeat_last, publishEvent(ErrorsStored)
  ── 커밋 ──▶ ErrorsStoredListener.onErrorsStored (AFTER_COMMIT)
                └ ErrorProcessor.process(tenantId, eventIds)   @Async("aiopsProcessingExecutor"), @Transactional 없음
                    TenantContext.set(tenantId)
                    for eventId: GroupingService.groupOne(...)  @Transactional (이벤트당 1 tx)
                         └ GroupUpserter.upsert → RETURNING id, (xmax=0) is_new
                         └ isNew면 groupId 반환 → newGroupIds
                    ★ 여기(모든 groupOne tx가 끝난 뒤, TenantContext는 아직 이 팀) ★
                    finally TenantContext.clear()
ReprocessScheduler.run (aiops-sched-, 5분) → 팀별 미처리 이벤트 → 같은 process(...)
```
- 훅: `S/service/ErrorProcessor.java` `process(...)` 안, 그룹화 for 루프 뒤. AI-60 브랜치 기준으로는 `for (Long groupId : newGroupIds)` 안 `notifier.notifyNewGroup` **바로 앞** TODO 줄:
  ```java
  try { explanationService.explain(tenantId, groupId); } catch (RuntimeException e) { log.warn("설명 실패 tenantId={} groupId={}", tenantId, groupId); }
  try { notifier.notifyNewGroup(tenantId, groupId); } catch (RuntimeException e) { ... }
  ```
  이 지점은 트랜잭션 밖(확실)이고 TenantContext가 설정돼 있어 `ExplanationStore`의 `@Transactional`이 `set_config`를 받아 RLS를 통과한다.
- 재발 그룹은 `newGroupIds`에 안 들어오므로 "새 그룹에만 1회"는 구조로 보장. 멱등은 `ai_explanation IS NULL` 조건 UPDATE로 이중 보장.

#### 4-2. B의 AI-60이 이미 기대하는 것
- 순서 고정: 설명 → 알림, 각각 try/catch (TODO 주석·Jira AI-60).
- 생성자: `@Autowired ErrorProcessor(GroupingService, Notifier)` + 테스트용 `ErrorProcessor(GroupingService)`. 기존 테스트 `ErrorProcessorTest`(`new ErrorProcessor(groupingService)` 3곳)와 `ErrorProcessorNonBlockingTest.SlowErrorProcessor`(`super(null)`)가 **1인자 생성자에 의존**(규칙 9로 수정 불가) → 7단계는 `@Autowired (GroupingService, ExplanationService, Notifier)` 3인자를 추가하고 1인자 생성자는 무동작 explain/notify로 유지해야 함.
- `DiscordEmbedBuilder.SECTIONS = ["원인 후보","확인 방법","해결 방향"]`를 `ai_explanation` 텍스트에서 **이 순서로** 찾는다. PromptBuilder system 지시의 출력 형식(`원인 후보:` / `확인 방법:` / `해결 방향:`)과 일치하면 3칸, 아니면 통째로 1칸. 필드값 1,024자에서 잘림.
- `EndToEndFlowTest`는 `"설명 준비 중"`을 단언 → `FakeLlmClient` 도입 시 테스트 갱신(설계자 PR) 필요. `docs/milestones.md`의 "설명 포함 확인 추가" 항목이 그 자리.

#### 4-3. 이미 있는 DB·코드 자원
- `error_group.ai_explanation TEXT`, `ai_explained_at TIMESTAMPTZ` (V1), RLS 대상(V2) → 조회·UPDATE는 TenantContext 안 tx에서. 엔티티 `S/model/entity/ErrorGroupEntity.java`에 `explain(String)`이 있으나 Jira AI-56은 detached save 금지 → `ErrorGroupRepository`에 `@Modifying` `UPDATE error_group SET ai_explanation=:text, ai_explained_at=now() WHERE id=:id AND tenant_id=:tenantId AND ai_explanation IS NULL` 추가.
- 대표 이벤트: `error_event.group_id`(인덱스 `idx_error_event_group`) + `payload JSONB` = protocol `ErrorEvent`(message 마스킹됨, stack, causes, phase, **loggerName** 신규). `ErrorEventRepository`에 "그룹의 최신 1건" 쿼리 없음 → 추가 필요. 보관 삭제로 원본이 없을 수 있음(그룹만 남음) → PromptBuilder는 그룹 요약(`exception_type`, `top_frame`, `first_env`, `occurrence_count`)만으로도 동작해야 함(추정).
- 앱 환경(Java/Boot 버전): `AppSnapshotRepository.findTopByTenantIdAndEnvOrderByReceivedAtDesc`.
- `llm_usage(day DATE PK, call_count INT)` V1, RLS 없음, `LlmUsageEntity`·빈 `LlmUsageRepository`. AI-57의 한 문장 `INSERT … ON CONFLICT (day) DO UPDATE … WHERE llm_usage.call_count < :limit RETURNING call_count`는 `IngestStatRecorder`처럼 `EntityManager` 네이티브 쿼리 + `@Transactional(REQUIRES_NEW)`로. 날짜는 `LocalDate.now(ZoneId.of("Asia/Seoul"))`.
- HTTP: `RestClient`는 이미 `DiscordWebhookNotifier`가 `SimpleClientHttpRequestFactory` 타임아웃으로 쓰는 패턴 있음 → `config/LlmConfig`에 같은 방식(타임아웃 20초).
- 설정: `application.yml`에 `aiops.llm.{api-key: ${AIOPS_LLM_API_KEY:}, base-url, model, timeout: 20s, daily-limit: 200, retry-window: PT24H, retry-batch: 50}` 신규, `infra/prod/.env.example`·`infra/local/.env.example`에 `AIOPS_LLM_API_KEY=` 추가.

#### 4-4. 재시도(AI-57) 연결
- `S/scheduler/ReprocessScheduler.run()` 끝에 추가. **RLS 때문에 팀 순회 필수(D-082)**: `tenantRepository.findAll()` → 팀마다 `TenantContext.set` → readOnly tx로 `error_group WHERE ai_explanation IS NULL AND first_seen_at > now()-24h ORDER BY first_seen_at LIMIT n` → (TenantContext 유지한 채) `explanationService.explain(tenantId, groupId)` → finally clear. `LlmQuota` false면 전체 루프 중단.
- 주의: 이 경로는 **알림을 다시 보내지 않는다**(이미 "설명 준비 중"으로 나간 알림은 갱신 안 됨). 의도인지 설계자 확인.
- `ReprocessSchedulerTest`는 `@MockitoBean ErrorProcessor`로 SpringBootTest라 생성자 인자 추가는 DI로 해결(직접 `new ReprocessScheduler` 하는 테스트 없음, 확인함).

#### 4-5. 착수 시 막히는 것 / 결정 필요
- AI-60 브랜치 머지 선행(같은 파일 `ErrorProcessor` 충돌 방지).
- 3절 4·5번(CallerRuns + 순차 LLM) 정책 결정.
- D-093(env 그룹 키) 결론에 따라 "새 그룹" 정의가 바뀌면 설명·알림 횟수도 바뀜.
- 패키지 경로 통일(3절 10번).

