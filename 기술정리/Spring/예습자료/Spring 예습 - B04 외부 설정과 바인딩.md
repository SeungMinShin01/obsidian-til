---
출처: 자동수집(Claude)
작성일: 2026-09-19
성격: 예습자료
tags: [학습, spring]
---

# Spring 예습 - B04 외부 설정과 바인딩

> 예습자료 — 자동 생성, 사용자 미검증. 결론이 아니라 **읽을 범위의 지도**다.
> 기준 버전: Spring Boot 4.1.1

## 이 모듈이 다루는 범위

B03이 "부팅이 어떤 순서로 일어나는가"였다면, B04는 **그 부팅이 읽어 들이는 값이 어디서 와서 어떤 규칙으로 객체에 꽂히는가**를 다룬다. 학습 지도에 ⭐⭐(분량·중요도 높음)로 표시된 모듈이고, 공식 문서에서도 단일 페이지로는 가장 긴 축에 속한다.

| 문서 | 문서가 서 있는 자리 |
| --- | --- |
| Reference → Core Features → Externalized Configuration | 본체. 한 페이지에 두 덩어리가 붙어 있다 |

한 페이지지만 성격이 다른 두 부분으로 갈린다는 점을 먼저 잡고 들어갈 것.

1. **값이 어디서 오는가** — 프로퍼티 출처의 우선순위, 파일 위치·이름 규칙, import·프로파일·멀티 도큐먼트, 플레이스홀더
2. **온 값이 어떻게 객체가 되는가** — `@ConfigurationProperties` 바인딩, 생성자 바인딩, 완화된 바인딩(relaxed binding), 변환, 검증

모듈명의 "외부 설정"이 1번, "바인딩"이 2번이다.

## 목차 지도

### 1부 — 값의 출처와 로딩

- **Externalized Configuration (도입)** — 같은 코드를 환경마다 다르게 돌리기 위해 설정을 코드 밖으로 빼는 수단들(프로퍼티 파일·YAML·환경 변수·커맨드라인 인자)을 한 줄로 열거하는 자리
- **PropertySource Order** — **이 모듈의 뼈대 절.** 같은 키가 여러 곳에 있을 때 무엇이 이기는가를 15단계 목록으로 못박는다. 기본 프로퍼티부터 커맨드라인 인자까지
- **Accessing Command Line Properties** — `--`로 시작하는 인자가 프로퍼티로 편입되는 경로
- **JSON Application Properties** — `spring.application.json` / `SPRING_APPLICATION_JSON`으로 JSON 덩어리를 통째로 넣는 경로
- **External Application Properties** — `application.properties`·`application.yaml`을 **어느 위치에서 어떤 순서로** 찾는지. `spring.config.name`(이름 바꾸기)·`spring.config.location`(찾을 곳 자체를 바꾸기)·`spring.config.additional-location`(더하기)의 차이
- **Optional Locations** — 없어도 되는 위치를 표시하는 `optional:` 접두사와 `spring.config.on-not-found`
- **Wildcard Locations** — 디렉터리 이름에 `*`를 써서 여러 벌을 한 번에 집는 표기
- **Profile Specific Files** — `application-{profile}.properties` 관례, 여러 프로파일이 걸렸을 때의 last-wins, 위치 그룹(`;`)
- **Importing Additional Data** — `spring.config.import`로 설정 파일을 사슬처럼 잇는 장치
- **Using "Fixed" and "Import Relative" Locations** — import 경로가 절대인가 상대인가를 가르는 기준(`/`·`file:`·`classpath:`로 시작하면 고정)
- **Property Ordering** — import끼리의 승패. 선언 순서가 아니라 무엇이 기준인가
- **Importing Extensionless Files** — 확장자 없는 파일을 읽힐 때 붙이는 힌트 `[.yaml]`
- **File Attributes** — 대괄호 속성을 여러 개 붙이는 표기(`[extension=.yaml][encoding=utf-8]`)
- **Using Environment Variables** — `env:` 접두사. 여러 줄짜리 환경 변수를 설정으로 읽어 들이는 경로
- **Using Configuration Trees** — `configtree:` 접두사. "파일 하나 = 값 하나"인 디렉터리 구조(쿠버네티스 ConfigMap·Secret, 도커 시크릿)를 설정으로 보는 방식
- **Property Placeholders** — `${name}`·`${name:기본값}`. 플레이스홀더를 풀 때 쓰이는 표준형(kebab-case) 이야기가 여기 붙어 있다
- **Working With Multi-Document Files** — 파일 하나를 논리적으로 쪼개는 구분자(YAML `---`, properties `#---`)
- **Activation Properties** — 쪼갠 조각을 **조건부로 켜는** 키. `spring.config.activate.on-profile`·`on-cloud-platform`
- **Encrypting Properties** — 부트가 내장 암호화를 제공하지 **않는다**는 선언과, 대신 끼어들 지점(`EnvironmentPostProcessor`)
- **Working With YAML** / **Mapping YAML to Properties** / **Directly Loading YAML** — YAML이 평평한 점 표기로 환산되는 규칙(리스트는 `my.servers[0]`), 그리고 스프링을 거치지 않고 직접 읽는 클래스들
- **Configuring Random Values** — `random.*` 출처. `${random.int(10)}`·`${random.int[1024,65536]}` 같은 문법
- **Configuring System Environment Properties** — 환경 변수 이름에 접두사를 붙여 한 머신에서 여러 앱을 가르는 수단

### 2부 — 바인딩

- **Type-safe Configuration Properties** — `@Value` 대신 값 묶음을 객체에 통째로 받는 방식의 도입부
- **JavaBean Properties Binding** — getter/setter가 있는 클래스에 `@ConfigurationProperties("접두사")`를 붙이는 기본형. 중첩 객체·컬렉션
- **Constructor Binding** — setter 없이 생성자로 받는 불변형. `@ConstructorBinding`(생성자가 여럿일 때)·`@DefaultValue`·레코드 지원
- **Enabling @ConfigurationProperties** — 그 클래스를 실제로 등록시키는 두 경로(`@EnableConfigurationProperties` / 컴포넌트 스캔)
- **Relaxed Binding** — 프로퍼티 이름과 자바 필드 이름이 **철자가 달라도 맞는** 규칙. 대소문자·구분자 차이를 어디까지 허용하는가
- **Relaxed Binding Rules** — 위 규칙이 List/Set·Map에 적용될 때의 예시
- **Environment Variables** — 점 표기 키를 환경 변수로 쓸 때의 밑줄 관례
- **Merging Complex Types** — Map·컬렉션이 여러 출처에 걸쳐 있을 때 **합쳐지는가 덮어쓰는가**
- **Properties Conversion** — 문자열이 타입으로 바뀌는 자리. 기간(`@DurationUnit`)·주기(`@PeriodUnit`)·데이터 크기(`@DataSizeUnit`), 그리고 직접 만든 변환기를 끼우는 표시(`ConfigurationPropertiesBinding`)
- **@ConfigurationProperties Validation** — `@Validated`를 얹어 기동 시점에 값을 검사하는 경로와 JSR-303 애노테이션
- **@ConfigurationProperties vs @Value** — 두 방식을 기능별로 비교한 표(타입 안전성·완화된 바인딩·메타데이터·SpEL 등)로 페이지가 끝난다

## 핵심 용어

| 용어 | 한 줄 |
| --- | --- |
| `Environment` | 프로파일과 프로퍼티를 애플리케이션에 제공하는 추상 (프레임워크 쪽 용어) |
| `PropertySource` | 키-값 한 벌의 출처 하나. `Environment`는 이것들을 순서대로 쌓아 들고 있다 |
| 우선순위(precedence) | 같은 키가 여러 출처에 있을 때 무엇이 이기는지 정한 순서 |
| config data | `application.properties`/`.yaml` 계열, 즉 부트가 정해진 규칙으로 찾아 읽는 설정 파일들 |
| `spring.config.name` / `.location` / `.additional-location` | 설정 파일의 이름·찾을 위치를 각각 바꾸거나 더하는 키 |
| `optional:` 접두사 | 그 위치가 없어도 기동을 실패시키지 않겠다는 표시 |
| 프로파일 특화 파일 | `application-{profile}` 형태로 프로파일이 켜졌을 때만 얹히는 파일 |
| last-wins | 여러 프로파일이 동시에 켜졌을 때 나중 것이 이긴다는 규칙 |
| `spring.config.import` | 다른 설정 파일·출처를 현재 설정에서 끌어오는 키 |
| fixed / import-relative 위치 | import 경로를 절대 기준으로 볼지, 끌어온 파일 기준의 상대로 볼지 |
| `configtree:` | 디렉터리 트리(파일명=키, 파일내용=값)를 프로퍼티 출처로 삼는 접두사 |
| `env:` | 여러 줄 환경 변수를 설정 문서로 읽어 들이는 접두사 |
| 멀티 도큐먼트 파일 | 파일 하나를 `---`(YAML)·`#---`(properties)로 여러 논리 문서로 쪼갠 것 |
| `spring.config.activate.on-profile` | 쪼갠 문서 조각을 특정 프로파일일 때만 켜는 조건 키 |
| 플레이스홀더 | `${다른.키}`로 값 안에서 다른 값을 참조하는 표기 |
| `RandomValuePropertySource` | `random.*` 키에 난수를 제공하는 내장 출처 |
| `EnvironmentPostProcessor` | `Environment`가 굳기 전에 끼어들어 출처를 손보는 훅 (암호화 절이 가리키는 지점) |
| `@ConfigurationProperties` | 접두사 아래 프로퍼티 묶음을 객체 하나에 바인딩시키는 애노테이션 |
| 생성자 바인딩 | setter 없이 생성자 파라미터로 값을 받아 불변 객체를 만드는 방식 |
| `@ConstructorBinding` / `@DefaultValue` | 생성자가 여럿일 때 쓸 것을 지정 / 생성자 바인딩에서 기본값 지정 |
| `@EnableConfigurationProperties` | `@ConfigurationProperties` 클래스를 빈으로 등록시키는 경로 중 하나 |
| 완화된 바인딩(relaxed binding) | 프로퍼티 이름의 대소문자·구분자 차이를 흡수해 같은 대상으로 보는 규칙 |
| 표준형(canonical form) | 위 규칙에서 기준이 되는 표기(소문자-하이픈) |
| `@DurationUnit` / `@PeriodUnit` / `@DataSizeUnit` | 숫자만 적힌 값을 어떤 단위로 읽을지 지정하는 애노테이션 |
| `ConfigurationPropertiesBinding` | 직접 만든 변환기를 바인딩 전용으로 끼울 때 붙이는 한정자 |
| `@Validated` | 바인딩된 설정 객체를 기동 시점에 검증 대상으로 만드는 애노테이션 |

## 처음 보는 개념

학습 지도에서 B04는 **신규**(KDT 수업 노트에 없음)로 표시돼 있다. 아래는 이 모듈에서 처음 등장하는 축들이다 — 답을 여기서 확인하지 말고, 문서에서 자리만 짚어 둘 것.

- **설정 값에 승패 규칙이 있다는 것.** 지금까지는 `application.properties` 한 곳에 썼다. 문서는 같은 키가 15개 층에 있을 수 있고 그 순서가 고정돼 있다고 말한다. "왜 내가 바꾼 값이 안 먹히는가"가 이 절의 실질적 질문이다.
- **설정 파일을 찾는 위치 자체가 설정값이라는 것.** `spring.config.location`은 설정으로 설정을 바꾸는 키다. 닭이 먼저인가 문제가 생기고, 문서가 그 순서를 따로 규정한다.
- **파일 하나가 문서 여럿일 수 있다는 것.** `---`로 쪼갠 조각마다 조건을 달아 켜고 끌 수 있다. 프로파일별 파일을 따로 두는 방식과 둘 중 무엇을 쓸지가 갈린다.
- **`@Value` 말고 다른 수령 방식이 있다는 것.** 값 하나씩 받는 것과 묶음을 객체로 받는 것은 타입 검사·검증·IDE 지원에서 다르다고 문서는 말한다. 페이지 마지막 비교표가 그 자리다.
- **이름이 정확히 같지 않아도 바인딩된다는 것.** `my-app.page-size`·`MY_APP_PAGESIZE`·`myApp.pageSize`의 관계. 이 관용이 어디까지인지가 완화된 바인딩 절의 내용이다.
- **설정 값이 틀렸을 때를 기동 시점에 잡는 장치가 있다는 것.** `@Validated`는 "런타임에 터지는 설정 오타"를 앞으로 당겨 놓는 수단으로 제시된다.
- **쿠버네티스·도커를 전제한 출처 형태.** `configtree:`·`env:`는 파일 한 개에 값 한 개가 들어 있는 컨테이너 시크릿 관행을 그대로 읽기 위한 장치다. B13(배포)으로 이어진다.
- **부트가 암호화를 안 준다는 명시적 선언.** 기능이 없다는 사실 자체가 문서에 적혀 있고, 대신 어디에 끼어들라고만 말한다.

## 학습 세션에서 확인할 것

- [ ] 커맨드라인 인자 · 환경 변수 · jar 밖 `application.properties` · jar 안 `application.properties` — 이 넷만 놓고 순위를 매기면 어떻게 되는가. 그 순서가 그렇게 정해진 이유는 무엇인가
- [ ] `spring.config.location`과 `spring.config.additional-location`을 바꿔 쓰면 무엇이 깨지는가
- [ ] 프로파일별 파일(`application-dev.yaml`)과 멀티 도큐먼트 + `spring.config.activate.on-profile`은 같은 일을 하는가. 어느 쪽을 언제 쓰는가
- [ ] 완화된 바인딩은 어디까지 관용적인가 — `@Value`에도 똑같이 적용되는가
- [ ] Map이나 List 타입 설정이 두 출처에 걸쳐 있을 때, 합쳐지는가 통째로 덮이는가. 그 규칙이 타입마다 다른가
- [ ] `@ConfigurationProperties` 클래스는 무엇을 해야 실제로 빈이 되는가. 등록 경로가 둘인 이유는 무엇인가

## 원문 링크

- https://docs.spring.io/spring-boot/reference/features/external-config.html
