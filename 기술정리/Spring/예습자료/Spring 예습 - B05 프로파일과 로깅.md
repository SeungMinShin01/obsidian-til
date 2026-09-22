---
출처: 자동수집(Claude)
작성일: 2026-09-20
성격: 예습자료
tags: [학습, spring]
---

# Spring 예습 - B05 프로파일과 로깅

> 예습자료 — 자동 생성, 사용자 미검증. 결론이 아니라 **읽을 범위의 지도**다.
> 기준 버전: Spring Boot 4.1.1

## 이 모듈이 다루는 범위

B04가 "설정 값이 어디서 와서 어떻게 객체가 되는가"였다면, B05는 그 위에 얹히는 두 가지다. **어떤 설정 묶음을 켤지 고르는 스위치(프로파일)** 와, **애플리케이션이 자기 상태를 밖으로 내보내는 통로(로깅)**. 공식 문서에서 서로 다른 두 페이지고, 분량도 성격도 다르다.

| 문서 | 문서가 서 있는 자리 |
| --- | --- |
| Reference → Core Features → Profiles | 짧다. B04의 「프로파일 특화 파일」·`spring.config.activate.on-profile` 절이 설정 파일 쪽 이야기였다면, 이쪽은 **빈 등록**과 **프로파일 자체의 조합 규칙** |
| Reference → Core Features → Logging | 길다. 기본 포맷·레벨 같은 입문 절부터 구조화 로깅·Logback/Log4j2 확장까지 한 페이지에 다 들어 있다 |

두 페이지가 한 모듈로 묶인 이유는 문서 순서가 그렇기도 하지만, **`<springProfile>`** 절에서 실제로 맞물린다는 점을 염두에 둘 것.

## 목차 지도

### 1부 — Profiles

- **Profiles (도입)** — 프로파일을 "설정의 일부를 특정 환경에서만 쓰이게 격리하는 수단"으로 정의하고, `@Profile`로 빈 등록 자체를 조건부로 만드는 방식을 보여주는 자리. `spring.profiles.active`·`spring.profiles.default`가 여기서 나온다
- **Adding Active Profiles** — `spring.profiles.include`. 활성 프로파일을 **교체하지 않고 얹는** 키. `active`와 무엇이 다른지, 그리고 이 두 키를 쓸 수 있는 문서가 제한된다는 단서가 붙어 있다
- **Profile Groups** — `spring.profiles.group.<이름>`. 프로파일 하나를 켜면 여러 개가 함께 켜지도록 별명을 만드는 장치
- **Programmatically Setting Profiles** — `SpringApplication.setAdditionalProfiles(…)`. 설정 파일이 아니라 코드에서 프로파일을 더하는 경로
- **Profile-specific Configuration Files** — `application-{profile}` 파일 규칙을 프로파일 쪽 관점에서 다시 짚는 절. 상세는 B04(외부 설정)로 넘긴다

> 프로파일 이름에 쓸 수 있는 문자에 제약이 있고, 그 검사를 끄는 키(`spring.profiles.validate`)가 따로 있다는 점이 도입부에 있다.

### 2부 — Logging

**입문부**

- **Logging (도입)** — 부트가 Commons Logging에 대고 쓰며 Logback·Log4j2·JUL 중 하나가 실제 구현으로 붙는다는 구조. 의존성은 스타터가 끌고 온다
- **Log Format** — 기본 한 줄에 무엇이 어떤 순서로 찍히는지(시각·레벨·PID·애플리케이션 이름·스레드·로거 이름·메시지)
- **Console Output** — 콘솔 출력의 기본값, `--debug`·`--trace`로 한 번에 키는 방식
  - **Color-coded Output** — `%clr` 변환어와 `spring.output.ansi.enabled`
- **File Output** — `logging.file.name`과 `logging.file.path`. 둘이 어떻게 다른지가 이 절의 전부
- **File Rotation** — 파일이 언제 잘리고 몇 개까지 남는지. `logging.logback.rollingpolicy.*` / `logging.log4j2.rollingpolicy.*`
- **Log Levels** — `logging.level.<로거이름>=<레벨>`, `logging.level.root`
- **Log Groups** — `logging.group.<이름>`으로 로거 여러 개를 한 이름으로 묶어 한 번에 올리고 내리는 장치. `web`·`sql` 같은 기본 제공 그룹이 있다
- **Using a Log Shutdown Hook** — `logging.register-shutdown-hook`. 종료 시 로깅 자원을 정리하는 훅을 켜고 끄는 자리 (B03의 종료 절차와 이어진다)
- **Custom Log Configuration** — 프로퍼티로 모자랄 때 설정 파일을 직접 두는 경로. `logback-spring.xml` / `log4j2-spring.xml` / `logging.properties`, 그리고 `logging.config`

**구조화 로깅**

- **Structured Logging** — 사람이 읽는 한 줄이 아니라 기계가 파싱할 JSON으로 내보내는 방식. `logging.structured.format.console` / `.file`
  - **Elastic Common Schema** — `ecs` 포맷과 `logging.structured.ecs.service.*`
  - **Graylog Extended Log Format (GELF)** — `gelf` 포맷
  - **Logstash JSON format** — `logstash` 포맷, 마커로 태그를 붙이는 방식
  - **Customizing Structured Logging JSON** — 나가는 JSON의 필드를 빼고·이름 바꾸고·더하는 `logging.structured.json.*`
  - **Customizing Structured Logging Stack Traces** — 스택 트레이스를 얼마나·어떤 순서로 실을지(`...json.stacktrace.*`)
  - **Supporting Other Structured Logging Formats** — `StructuredLogFormatter` 구현으로 자기 포맷을 끼우는 확장점

**프레임워크 확장**

- **Logback Extensions** — 부트가 Logback 설정 파일에 더해 주는 태그들 (`-spring` 붙은 파일명에서만 동작한다는 조건이 여기 있다)
  - **Profile-specific Configuration** — `<springProfile>`. 1부의 프로파일이 로깅 설정 안으로 들어오는 지점
  - **Environment Properties** — `<springProperty>`. `Environment`의 값을 Logback 설정에서 꺼내 쓰는 태그
- **Log4j2 Extensions** — 같은 역할의 Log4j2 쪽
  - **Profile-specific Configuration** — `<SpringProfile>`
  - **Environment Properties Lookup** — `spring:` 접두 lookup
  - **Log4j2 System Properties** — Log4j2의 시스템 프로퍼티를 `Environment`로 지정하는 대응표

## 핵심 용어

| 용어 | 한 줄 |
| --- | --- |
| 프로파일(profile) | 설정·빈의 일부를 특정 이름이 켜졌을 때만 쓰이게 묶는 이름표 |
| `spring.profiles.active` | 지금 켤 프로파일을 지정하는 키 (쉼표로 여럿) |
| `spring.profiles.default` | 아무것도 지정되지 않았을 때 쓰일 프로파일 이름 (기본값 `default`) |
| `spring.profiles.include` | 활성 프로파일을 교체하지 않고 **추가로** 얹는 키 |
| `spring.profiles.group` | 프로파일 하나에 여러 프로파일을 묶어 두는 별명 정의 |
| `spring.profiles.validate` | 프로파일 이름 형식 검사를 켜고 끄는 키 |
| `@Profile` | 해당 프로파일일 때만 그 빈·설정 클래스를 등록하게 하는 애노테이션 |
| `setAdditionalProfiles(…)` | 코드에서 프로파일을 더하는 `SpringApplication`의 메서드 |
| `spring.config.activate.on-profile` | (B04) 설정 **문서 조각**을 조건부로 켜는 키 — `@Profile`과 층이 다르다 |
| Commons Logging | 부트 내부가 대고 쓰는 로깅 파사드. 실제 구현은 따로 붙는다 |
| `LoggingSystem` | 어떤 로깅 구현이 붙었는지를 추상화하는 부트 쪽 타입 |
| 로그 레벨 | TRACE·DEBUG·INFO·WARN·ERROR·FATAL·OFF |
| `logging.level.<로거>` | 특정 로거(보통 패키지 이름)의 레벨을 지정하는 키 |
| 로그 그룹 | 로거 여러 개를 한 이름으로 묶은 것. `logging.group.<이름>`, 기본 제공 `web`·`sql` |
| `logging.file.name` / `logging.file.path` | 파일 출력 지정 — 하나는 파일을, 하나는 디렉터리를 가리킨다 |
| 롤링(rotation) | 로그 파일이 일정 크기·주기에서 잘리고 보관 개수를 제한하는 동작 |
| `logging.config` | 프로퍼티 대신 쓸 로깅 설정 파일의 위치를 지정하는 키 |
| `logback-spring.xml` / `log4j2-spring.xml` | 부트 확장 태그가 동작하는 설정 파일명 규약 |
| 구조화 로깅(structured logging) | 로그를 사람이 읽는 문장이 아니라 파싱 가능한 JSON으로 내보내는 방식 |
| ECS / GELF / Logstash | 구조화 로깅의 내장 포맷 세 가지 (Elastic 표준 스키마 / Graylog / Logstash JSON) |
| `StructuredLogFormatter` | 내장 포맷 외에 자기 포맷을 끼울 때 구현하는 인터페이스 |
| `<springProfile>` / `<springProperty>` | Logback 설정 안에서 프로파일 조건과 `Environment` 값을 쓰게 해 주는 부트 확장 태그 |
| 로그 종료 훅 | 애플리케이션 종료 시 로깅 자원을 닫는 훅 (`logging.register-shutdown-hook`) |

## 처음 보는 개념

학습 지도에서 B05는 **신규**(KDT 수업 노트에 없음)로 표시돼 있다. 아래는 이 모듈에서 처음 등장하는 축들이다 — 답을 여기서 확인하지 말고, 문서에서 자리만 짚어 둘 것.

- **프로파일이 두 층에서 작동한다는 것.** 하나는 설정 문서를 켜고 끄는 층(B04의 `spring.config.activate.on-profile`), 하나는 빈을 등록하고 안 하는 층(`@Profile`). 같은 이름을 쓰지만 판정 시점이 다르다.
- **`active`와 `include`가 다른 키라는 것.** 문서는 이 둘을 별개 절로 나누고, 게다가 "프로파일 특화 문서에서는 이 키들을 쓸 수 없다"는 제약을 붙인다. 제약이 있다는 건 그렇게 쓰면 모순이 생긴다는 뜻이다.
- **프로파일에 별명을 달 수 있다는 것.** `spring.profiles.group`은 `prod` 하나로 여러 개를 동시에 켜는 장치다. 환경이 늘어날 때의 관리 수단으로 제시된다.
- **로깅 설정이 부트의 프로퍼티와 로깅 프레임워크의 설정 파일, 두 갈래라는 것.** 문서는 프로퍼티로 되는 범위를 먼저 다 보여 준 뒤 "여기서부터는 파일"이라고 선을 긋는다. 그 선이 어디인지가 이 절의 핵심이다.
- **파일명에 `-spring`이 붙고 안 붙고가 기능 차이라는 것.** `logback.xml`과 `logback-spring.xml`은 같은 파일이 아니다. 부트 확장 태그가 동작하려면 후자여야 한다고 문서는 말한다.
- **로그가 사람이 읽는 형식만 있는 게 아니라는 것.** 구조화 로깅 절은 로그를 수집·검색 시스템의 입력 데이터로 본다. B12(Actuator·메트릭)와 B13(배포)에서 다시 만나는 관점이다.
- **로거 이름이 패키지 계층이고 레벨이 상속된다는 전제.** `logging.level.org.springframework.web=DEBUG`가 왜 그 아래 전부에 먹히는지는 문서가 당연시하고 넘어간다.

## 학습 세션에서 확인할 것

- [ ] `@Profile("dev")`가 붙은 빈과 `spring.config.activate.on-profile: dev`가 걸린 설정 조각은 각각 언제 판정되는가. 둘 중 하나만으로 안 되는 상황이 있는가
- [ ] `spring.profiles.active`와 `spring.profiles.include`를 바꿔 쓰면 무엇이 달라지는가. 왜 이 키들을 프로파일 특화 파일 안에서는 쓰지 못하게 막았는가
- [ ] `logging.file.name`과 `logging.file.path`를 둘 다 지정하면 어떻게 되는가
- [ ] 로그 그룹(`logging.group`)은 `logging.level`을 여러 줄 쓰는 것과 기능상 같은가, 다른가
- [ ] `logback.xml`이 아니라 `logback-spring.xml`이어야 하는 이유는 무엇인가 — 로딩 시점과 관련이 있는가
- [ ] 구조화 로깅을 켜면 콘솔의 사람이 읽는 출력은 어떻게 되는가. 운영에서 둘을 동시에 원할 때의 선택지는

## 원문 링크

- https://docs.spring.io/spring-boot/reference/features/profiles.html
- https://docs.spring.io/spring-boot/reference/features/logging.html
