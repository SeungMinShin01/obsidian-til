---
출처: 자동수집(Claude)
작성일: 2026-09-11
성격: 예습자료
tags: [학습, spring]
---

# Spring 예습 - B01 프로젝트 생성과 첫 실행

> 예습자료 — 자동 생성, 사용자 미검증. 결론이 아니라 **읽을 범위의 지도**다.
> 기준 버전: Spring Boot 4.1.1

## 이 모듈이 다루는 범위

공식 문서에서 B01에 대응하는 자리는 세 곳이다.

| 문서 | 문서가 서 있는 자리 |
| --- | --- |
| Tutorials → Developing Your First Spring Boot Application | 빈 폴더에서 시작해 "Hello World!" 를 응답하는 애플리케이션까지 가는 한 바퀴를 처음부터 끝까지 따라가게 한다 |
| Installing Spring Boot | 부트를 "설치한다"는 말이 실제로는 무엇을 뜻하는지 — 빌드 도구 쪽과 CLI 쪽 두 갈래 |
| System Requirements | 이 버전이 무엇 위에서 도는지 — 자바·빌드 도구·서블릿 컨테이너의 허용 범위 |

세 문서 모두 **Initializr를 쓰지 않는다.** 생성기가 만들어 준 결과물을 읽는 것이 아니라, 최소 구성을 손으로 적어 나가는 순서로 서술돼 있다는 점이 이 모듈의 성격이다.

## 목차 지도

### Developing Your First Spring Boot Application

- **Prerequisites** — 시작 전 확인할 자바·빌드 도구의 버전 확인 명령
- **Setting Up the Project With Maven** — `pom.xml` 최소 형태. `spring-boot-starter-parent` 를 부모로 두는 것이 여기서 나온다
- **Setting Up the Project With Gradle** — 같은 일을 `build.gradle` 에서 하는 갈래. 플러그인 두 개의 역할을 나눠 설명한다
- **Adding Classpath Dependencies** — 웹 애플리케이션을 만들기 위해 무엇 하나를 추가하는지, 그리고 그 하나가 무엇을 끌고 오는지
- **Writing the Code** — 애플리케이션 클래스 한 개를 쓴다. 아래 세 소절로 쪼개져 있다
  - *The `@RestController` and `@RequestMapping` Annotations* — 요청이 이 메소드로 오게 하는 표시 두 개를 각각 무엇을 정하는 표시로 설명하는지
  - *The `@SpringBootApplication` Annotation* — 이 표시가 어떤 애노테이션들의 묶음인지
  - *The "main" Method* — 자바의 보통 `main` 과 무엇이 같고 무엇이 다른지
- **Running the Example** — 빌드 도구로 직접 실행하는 명령(`spring-boot:run` / `bootRun`)과 확인 지점
- **Creating an Executable Jar** — 실행 가능한 jar를 만드는 설정과 명령, 그리고 "실행 가능한 jar" 가 왜 보통 jar와 다른 문제를 푸는지

### Installing Spring Boot

- **Installation Instructions for the Java Developer** — 부트가 특별한 설치를 요구하지 않는다는 전제
- **Maven Installation** / **Gradle Installation** — 빌드 도구 쪽에서 부트를 끌어오는 두 방식
- **Installing the Spring Boot CLI** — 빌드 도구와 별개인 명령행 도구. 필수가 아니라는 위치 규정
- **Manual Installation** · **SDKMAN!** · **Homebrew** · **MacPorts** · **Scoop** · **Command-line Completion** — CLI를 얻는 경로들

### System Requirements

- **Java / Spring Framework** — 이 부트 버전이 허용하는 자바 범위와 요구하는 프레임워크 버전
- **Build Tools** — Maven·Gradle의 최저 버전
- **Servlet Containers** — 내장으로 지원되는 컨테이너와 그 서블릿 스펙 버전
- **GraalVM Native Images** — 네이티브 이미지로 바꿀 때 요구되는 버전들

## 핵심 용어

| 용어 | 한 줄 |
| --- | --- |
| starter | 자주 함께 쓰이는 의존성 묶음을 하나의 이름으로 가져오는 의존성 기술자 |
| `spring-boot-starter-webmvc` | 서블릿 기반 웹 MVC 애플리케이션용 스타터 (4.x의 이름) |
| `spring-boot-starter-parent` | Maven에서 부모 POM으로 상속받는 특수 스타터. 기본값과 버전 관리를 물려준다 |
| `spring-boot-maven-plugin` / `bootJar` | 실행 가능한 jar를 만들어 내는 빌드 도구 쪽 장치 |
| executable jar (uber jar / fat jar) | 애플리케이션 클래스와 의존 라이브러리를 한 파일에 담아 단독 실행되게 만든 아카이브 |
| `@SpringBootApplication` | `@SpringBootConfiguration` + `@EnableAutoConfiguration` + `@ComponentScan` 의 메타 애노테이션 |
| `@EnableAutoConfiguration` | 클래스패스에 있는 것을 근거로 자동 설정을 켜는 표시 |
| `@RestController` | 반환값을 뷰 이름이 아니라 응답 본문으로 다루는 컨트롤러 스테레오타입 |
| `@RequestMapping` | 어떤 요청이 이 자리로 올지 정하는 표시 |
| `SpringApplication` | 스프링 애플리케이션을 기동하는 부트스트랩 클래스 |
| Spring Boot CLI | 빌드 도구 없이 빠른 시작·프로토타이핑에 쓰는 명령행 도구 |
| GraalVM Native Image | JVM 없이 도는 실행 파일로 애플리케이션을 미리 컴파일한 형태 |

## 수업에서 안 다뤘을 만한 지점

이 모듈은 학습 지도에서 **복습**(day01·day02와 대조)으로 표시돼 있다. `Spring/` 구역의 「Spring Boot 프로젝트 생성(분석)」·day01·day02 노트를 읽고 공식 문서와 대조한 결과, 아래가 수업 쪽에 없거나 얕게 지나간 자리다.

- **Maven 갈래 전체.** 수업 노트는 Gradle(`build.gradle`·`gradlew`·`io.spring.dependency-management`)만 다루고, Maven은 "다음에 볼 키워드" 줄에만 이름이 있다. 공식 튜토리얼은 Maven을 먼저 놓고 Gradle을 나란히 둔다. 특히 `spring-boot-starter-parent` 를 **부모 POM으로 상속한다**는 구조는 Gradle 플러그인 방식과 형태가 달라서, 같은 문제(버전 맞추기)를 두 도구가 다르게 푼다는 대조가 생긴다.
- **Initializr 없이 시작하기.** 수업은 생성기가 만든 프로젝트를 열어 각 파일을 해설하는 방향이다. 공식 문서는 빈 폴더에서 최소 파일만 적어 나간다. "생성기가 넣어 준 것 중 무엇이 진짜 필수인가" 는 이 대조에서만 나온다.
- **개발 중 실행 명령.** 수업 노트의 실행은 IDE에서 `main` 실행, 또는 `./gradlew build` 후 `java -jar` 였다. 공식 문서는 빌드 도구가 직접 애플리케이션을 띄우는 명령(`mvn spring-boot:run` / `gradle bootRun`)을 실행 절의 기본으로 둔다 — 패키징과 실행이 별개의 단계라는 점이 여기서 갈린다.
- **시스템 요구사항 표 전체.** 자바 허용 범위, 요구되는 스프링 프레임워크 버전, 내장 지원 컨테이너(Tomcat·Jetty)와 그 서블릿 스펙 버전 — 수업 노트에는 이 표에 해당하는 서술이 없다. day01이 서블릿을 다뤘으므로 "그때 쓴 서블릿 규격 버전이 부트 4.1.1에서 몇인가" 를 이어 붙일 수 있는 자리다.
- **실행 가능한 jar의 내부.** 수업 노트는 "의존 라이브러리와 톰캣까지 들어 있다" 까지 갔다. 공식 문서는 이 절을 따로 두고 보통 jar로는 안 되는 이유 쪽을 설명한다 — 무엇이 문제였는지는 원문에서 확인할 것.
- **Spring Boot CLI와 GraalVM 네이티브 이미지.** 수업 노트에 전혀 없다. 둘 다 "부트를 쓰는 다른 경로" 로 문서에 존재한다는 사실만 알아 두면 되는 수준.

## 학습 세션에서 확인할 것

- [ ] 최소 구성으로 웹 애플리케이션 하나를 띄우는 데 정말로 필요한 파일과 항목은 무엇이고, Initializr가 추가로 넣어 주는 것은 무엇인가
- [ ] `spring-boot-starter-parent` 를 부모로 두는 Maven 방식과 Gradle 플러그인 방식은 각각 무엇을 대신해 주는가 — 둘이 푸는 문제가 같은가
- [ ] `mvn spring-boot:run` / `gradle bootRun` 과 `java -jar <빌드된 jar>` 는 실행 결과가 같은데 무엇이 다른가
- [ ] 보통 jar로 패키징하면 무엇이 안 되는가. 실행 가능한 jar는 그것을 어떻게 해결하는가
- [ ] `@SpringBootApplication` 을 구성하는 세 애노테이션을 각각 떼어 놓고 보면, 이 중 하나만 빠졌을 때 무엇이 먼저 깨지는가
- [ ] 부트 4.1.1이 요구하는 자바·서블릿 스펙 버전은 day01에서 쓴 `jakarta.servlet` 과 어떻게 이어지는가

## 원문 링크

- https://docs.spring.io/spring-boot/tutorial/first-application/index.html
- https://docs.spring.io/spring-boot/installing.html
- https://docs.spring.io/spring-boot/system-requirements.html
