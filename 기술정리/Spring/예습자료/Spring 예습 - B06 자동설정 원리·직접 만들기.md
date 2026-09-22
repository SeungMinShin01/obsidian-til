---
출처: 자동수집(Claude)
작성일: 2026-09-21
성격: 예습자료
tags: [학습, spring]
---

# Spring 예습 - B06 자동설정 원리·직접 만들기

> 예습자료 — 자동 생성, 사용자 미검증. 결론이 아니라 **읽을 범위의 지도**다.
> 기준 버전: Spring Boot 4.1.1

## 이 모듈이 다루는 범위

B06은 공식 문서에서 **서로 멀리 떨어진 두 페이지**를 한 모듈로 묶는다. 하나는 "쓰는 쪽"이고 하나는 "만드는 쪽"이다.

| 문서 | 문서가 서 있는 자리 |
| --- | --- |
| Reference → Developing with Spring Boot → **Auto-configuration** | 짧다. 이미 있는 자동설정을 **켜고·비키게 하고·끄는** 방법. 사용자 입장의 절 |
| Reference → Core Features → **Creating Your Own Auto-configuration** | 길다. 자동설정을 **직접 만드는** 쪽. 조건 애노테이션 목록, 후보를 찾아내는 파일 규약, 테스트, 스타터 제작까지 |

앞쪽이 "부트가 알아서 해 준다"고 말한 것의 **정체**를 뒤쪽이 밝히는 구조다. 학습 지도의 비고대로 day03(애노테이션·리플렉션)이 선행 지식이다 — 문서가 "메타데이터를 ASM으로 파싱한다"는 식으로 말을 던지고 지나간다.

B02(스타터·BOM)에서 "스타터를 넣으면 된다"고 했던 지점, B03(SpringApplication 생명주기)에서 컨텍스트가 뜨는 순서, B04(`@ConfigurationProperties` 바인딩)가 여기서 한 줄로 합쳐진다.

## 목차 지도

### 1부 — Auto-configuration (쓰는 쪽)

- **Auto-configuration (도입)** — 자동설정을 "추가한 jar 의존성을 근거로 애플리케이션을 알아서 구성하는 것"으로 정의하는 자리. `@EnableAutoConfiguration`과 `@SpringBootApplication`의 관계, `--debug`로 **무엇이 왜 적용됐는지** 보는 방법이 여기 있다
- **Gradually Replacing Auto-configuration** — 자동설정이 "비침투적(non-invasive)"이라는 성질. 내가 같은 빈을 직접 정의하면 자동설정이 **물러난다**는 동작을 사용자 입장에서 서술하는 절
- **Disabling Specific Auto-configuration Classes** — 원치 않는 자동설정을 빼는 두 경로: 애노테이션의 `exclude` 속성과 `spring.autoconfigure.exclude` 프로퍼티
- **Auto-configuration Packages** — 엔티티·Spring Data 리포지터리 같은 것을 **어느 패키지에서 찾는지**를 정하는 규칙. `@AutoConfigurationPackage`로 그 범위를 직접 지정하는 경로도 함께

### 2부 — Creating Your Own Auto-configuration (만드는 쪽)

- **Understanding Auto-configured Beans** — 자동설정 클래스가 `@AutoConfiguration`(안에 `@Configuration`이 메타 애노테이션으로 들어 있다)으로 표시되고, `@ConditionalOnClass`·`@ConditionalOnMissingBean` 같은 조건이 붙는다는 기본형
- **Locating Auto-configuration Candidates** — 부트가 자동설정 클래스를 **어떻게 찾아내는가**. jar 안의 `META-INF/spring/org.springframework.boot.autoconfigure.AutoConfiguration.imports` 파일에 한 줄씩 적는 규약 (`#` 주석, 중첩 클래스는 `$`). "이 파일에 이름이 적힌 것만으로 로드되어야 하고, 컴포넌트 스캔의 대상이 되어서는 안 된다"는 제약이 붙어 있다
  - **순서** — `@AutoConfiguration`의 `before`/`beforeName`/`after`/`afterName`, 별도 애노테이션 `@AutoConfigureBefore`·`@AutoConfigureAfter`, 서로를 모르는 것들 사이의 `@AutoConfigureOrder`. 문서는 이 순서가 **빈이 정의되는 순서**만 정하고 **생성되는 순서**는 의존관계·`@DependsOn`이 정한다고 선을 긋는다
  - **Deprecating and Replacing Auto-configuration Classes** — 클래스를 옮기거나 이름을 바꿀 때 쓰는 `…AutoConfiguration.replacements` 파일(`옛이름=새이름`)
- **Condition Annotations** — 자동설정이 **언제 적용될지**를 거는 조건들. 이 절이 2부의 몸통이다
  - **Class Conditions** — `@ConditionalOnClass` / `@ConditionalOnMissingClass`. 메타데이터를 ASM으로 읽기 때문에 런타임 클래스패스에 없는 클래스도 참조할 수 있다는 설명, 그리고 `@Bean` 메서드에 직접 걸 때의 주의(JVM 클래스 로딩이 조건 평가보다 먼저 일어난다)
  - **Bean Conditions** — `@ConditionalOnBean` / `@ConditionalOnMissingBean`. 타입(`value`)·이름(`name`)·검색 범위(`search`) 속성. 문서가 **경고**를 붙이는 지점: 이 조건들은 "지금까지 처리된 것"을 근거로 평가되므로 자동설정 클래스에만 쓰라고 권고한다. 더불어 `@Bean` 메서드의 **반환 타입에 타입 정보를 최대한 실으라**는 요구가 여기 붙는다
  - **Property Conditions** — `@ConditionalOnProperty`(`prefix`·`name`·`havingValue`·`matchIfMissing`), 불리언 전용 `@ConditionalOnBooleanProperty`
  - **Resource Conditions** — `@ConditionalOnResource`
  - **Web Application Conditions** — `@ConditionalOnWebApplication` / `@ConditionalOnNotWebApplication`, 그리고 WAR 배포 여부를 보는 `@ConditionalOnWarDeployment` / `@ConditionalOnNotWarDeployment`
  - **SpEL Expression Conditions** — `@ConditionalOnExpression`. 식 안에서 빈을 참조하면 그 빈이 **너무 이르게 초기화된다**는 경고가 달려 있다
- **Testing your Auto-configuration** — `ApplicationContextRunner`로 컨텍스트를 조건별로 띄워 보는 방식, 환경을 바꿔 가며 돌리기, 조건 평가 리포트(`ConditionEvaluationReport`) 확인
  - **Simulating a Web Context** — `WebApplicationContextRunner` / `ReactiveWebApplicationContextRunner`
  - **Overriding the Classpath** — `FilteredClassLoader`로 "그 클래스가 없는 상황"을 만들어 보는 방법
- **Creating Your Own Starter** — 남이 쓸 스타터를 만드는 절
  - **Naming** — 모듈 이름을 `spring-boot`로 시작하지 말라는 규칙, `acme-spring-boot`(자동설정) / `acme-spring-boot-starter`(스타터) / `acme-spring-boot-starter-test` 명명
  - **Configuration keys** — 전용 네임스페이스를 쓰고 Javadoc으로 문서화하라는 요구. 애노테이션 프로세서가 만드는 `META-INF/spring-configuration-metadata.json`
  - **The "autoconfigure" Module** — 자동설정 코드와 설정 키가 들어가는 모듈
  - **Starter Module** — 의존성만 모아 둔, 사실상 **빈 jar**. 문서는 두 모듈로 나누는 것이 필수가 아니며 언제 나눌 값어치가 있는지도 말한다

## 핵심 용어

| 용어 | 한 줄 |
| --- | --- |
| 자동설정(auto-configuration) | 클래스패스에 무엇이 있는지를 근거로 빈을 대신 정의해 주는 부트의 장치 |
| `@EnableAutoConfiguration` | 자동설정을 켜는 애노테이션. `@SpringBootApplication` 안에 들어 있다 |
| `@AutoConfiguration` | 자동설정 클래스를 표시하는 애노테이션 (`@Configuration`이 메타 애노테이션) |
| 비침투적(non-invasive) | 내가 정의한 빈이 있으면 자동설정이 물러나는 성질 |
| back off (물러남) | 조건이 어긋나 자동설정이 자기 빈 정의를 포기하는 동작 |
| `spring.autoconfigure.exclude` | 특정 자동설정 클래스를 프로퍼티로 제외하는 키 |
| `@AutoConfigurationPackage` | 자동설정이 훑을 패키지 기준점을 지정하는 애노테이션 |
| `AutoConfiguration.imports` | `META-INF/spring/…AutoConfiguration.imports` — 자동설정 후보를 한 줄씩 적는 파일 |
| `AutoConfiguration.replacements` | 자동설정 클래스를 옮기거나 이름 바꿀 때 옛 이름을 새 이름에 잇는 파일 |
| `@AutoConfigureBefore` / `@AutoConfigureAfter` / `@AutoConfigureOrder` | 자동설정끼리의 적용 순서를 거는 세 가지 수단 |
| 조건 애노테이션(condition annotation) | `@Conditional` 계열 — 설정이 적용될 조건을 선언으로 표현한 것 |
| `@ConditionalOnClass` / `@ConditionalOnMissingClass` | 특정 클래스의 유무로 설정을 켜고 끈다 |
| `@ConditionalOnBean` / `@ConditionalOnMissingBean` | 특정 빈의 유무로 켜고 끈다 — 평가 시점에 예민하다 |
| `@ConditionalOnProperty` / `@ConditionalOnBooleanProperty` | `Environment`의 프로퍼티 값으로 켜고 끈다 |
| `@ConditionalOnResource` | 특정 리소스가 있을 때만 켠다 |
| `@ConditionalOnWebApplication` / `@ConditionalOnWarDeployment` | 웹 애플리케이션인지, WAR로 배포됐는지로 켜고 끈다 |
| `@ConditionalOnExpression` | SpEL 식의 결과로 켜고 끈다 |
| ASM | 바이트코드를 읽는 라이브러리. 클래스를 로드하지 않고 애노테이션 메타데이터만 읽는 데 쓰인다 |
| 조건 평가 리포트(condition evaluation report) | 어떤 자동설정이 적용/미적용됐고 그 이유가 무엇인지 보여 주는 보고 (`--debug`) |
| `ApplicationContextRunner` | 조건을 바꿔 가며 컨텍스트를 띄워 보는 테스트 도구 |
| `FilteredClassLoader` | 테스트에서 "그 클래스가 없는 상황"을 흉내 내는 클래스로더 |
| 스타터(starter) | 어떤 기술을 쓰는 데 필요한 의존성 묶음을 제공하는 모듈 |
| autoconfigure 모듈 | 스타터 뒤에서 실제 자동설정 코드와 설정 키를 담는 모듈 |
| `spring-configuration-metadata.json` | 애노테이션 프로세서가 만드는, IDE 자동완성용 설정 키 메타데이터 |
| `spring-autoconfigure-metadata.properties` | 후보를 이른 단계에서 걸러 내기 위한 메타데이터 |

## 처음 보는 개념

학습 지도에서 B06은 **신규**(KDT 수업 노트에 없음, ⭐⭐)로 표시돼 있다. 아래는 이 모듈에서 처음 등장하는 축들이다 — 답을 여기서 확인하지 말고, 문서에서 자리만 짚어 둘 것.

- **"알아서 된다"에 실체가 있다는 것.** 지금까지 스타터를 넣으면 동작하던 것들이 전부 어딘가의 `@AutoConfiguration` 클래스와 그 위에 걸린 조건이었다는 사실이 이 모듈에서 드러난다.
- **조건이 코드가 아니라 애노테이션이라는 것.** if 문이 아니라 선언으로 조건을 표현하고, 그 판정을 프레임워크가 대신 한다. day03의 애노테이션·리플렉션이 여기서 쓰인다.
- **클래스패스를 조건으로 삼는다는 발상.** "이 클래스가 있으면"이라는 조건을, 그 클래스를 **로드하지 않고** 판정한다(ASM). 왜 로드하면 안 되는지가 이 절이 감추고 있는 질문이다.
- **컴포넌트 스캔과 자동설정이 다른 통로라는 것.** 문서는 자동설정 클래스가 스캔 대상이 되면 안 된다고 못 박는다. `@Component`를 찾는 길과 `imports` 파일을 읽는 길이 나뉘어 있다.
- **순서에 두 종류가 있다는 것.** 빈 **정의**의 순서와 빈 **생성**의 순서를 문서가 명시적으로 분리한다. B03의 컨텍스트 부팅 단계와 겹쳐 보게 될 지점.
- **`@ConditionalOnMissingBean`의 위험이 문서에 경고로 적혀 있다는 것.** "지금까지 처리된 것"을 근거로 판정하기 때문에 아무 데나 쓰면 안 된다고 한다. 왜 자동설정 클래스에서만 안전한지가 핵심.
- **라이브러리를 만드는 쪽의 관점.** 2부 후반은 내가 쓰는 코드가 아니라 **남이 쓸 모듈**을 만드는 이야기다. 모듈 두 개로 나누는 관례, 이름 규칙, 설정 키 네임스페이스 — 지금까지의 모듈과 시점이 다르다.

## 학습 세션에서 확인할 것

- [ ] 내가 `DataSource` 빈을 직접 정의하면 `DataSourceAutoConfiguration`이 물러난다. 이 "물러남"은 어느 조건이 어느 시점에 평가돼서 일어나는가
- [ ] `@ConditionalOnMissingBean`을 일반 `@Configuration` 클래스에 걸면 무엇이 잘못될 수 있는가 — 문서가 "자동설정 클래스에만 쓰라"고 한 이유
- [ ] 자동설정 클래스를 컴포넌트 스캔 대상에 두면 안 되는 이유는 무엇인가. 스캔으로 잡히면 `imports`로 로드될 때와 무엇이 달라지는가
- [ ] `@ConditionalOnClass`를 `@Bean` 메서드에 직접 거는 것과 별도 `@Configuration` 클래스로 빼는 것의 차이 — JVM 클래스 로딩과 어떻게 얽히는가
- [ ] `@AutoConfigureAfter`로 순서를 잡아도 빈 생성 순서는 바뀌지 않는다고 한다. 그럼 순서를 잡아서 얻는 것은 정확히 무엇인가
- [ ] `--debug`의 조건 평가 리포트에서 "Negative matches"를 읽으면 무엇을 알 수 있는가. 자동설정이 안 먹을 때 어디부터 보는가
- [ ] 스타터를 두 모듈(`acme-spring-boot` / `acme-spring-boot-starter`)로 나누는 것이 언제 값어치가 있는가

## 원문 링크

- https://docs.spring.io/spring-boot/reference/using/auto-configuration.html
- https://docs.spring.io/spring-boot/reference/features/developing-auto-configuration.html
