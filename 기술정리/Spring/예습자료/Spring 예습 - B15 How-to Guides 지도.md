---
출처: 자동수집(Claude)
작성일: 2026-09-30
성격: 예습자료
tags: [학습, spring]
---

# Spring 예습 - B15 How-to Guides 지도

> 예습자료 — 자동 생성, 사용자 미검증. 결론이 아니라 **읽을 범위의 지도**다.
> 기준 버전: Spring Boot 4.1.1
> 학습 지도의 비고: **정독 아님 — 목차만 훑어 "어떤 문제가 문서화돼 있는지" 지도 작성. 30분**. 그래서 이 노트는 다른 예습자료와 성격이 다르다. 내용을 미리 보여 주는 지도가 아니라, **"나중에 막혔을 때 어디를 펼칠지"를 기억하기 위한 색인**에 가깝다.

## 이 모듈이 다루는 범위

Reference(B01~B14가 읽어 온 쪽)와 나란히 놓인 **How-to Guides** 섹션 전체다. 문서가 스스로 밝히는 성격이 Reference와 다르다.

> 원문 도입부: "This section provides answers to some common 'how do I do that…' questions that often arise when using Spring Boot. Its coverage is not exhaustive, but it does cover quite a lot." — 빠진 것이 있으면 Stack Overflow를 보거나 PR을 보내라는 안내가 뒤따른다.

여기서 읽히는 차이:

- Reference는 **"부트가 무엇을 하는가"**를 층별로 설명한다. How-to는 **"내가 이걸 하려는데 어떻게 하는가"**를 질문 단위로 답한다
- 그래서 목차 항목이 대부분 **동사로 시작한다** (Configure…, Change…, Disable…, Use…, Create…). 절 제목 자체가 질문이다
- **완전하지 않다고 문서가 먼저 말한다.** Reference처럼 "여기 다 있다"가 아니라 "자주 나오는 것만 모았다"는 자리
- 기여를 받는다고 명시한다 — 내용이 커뮤니티에서 올라온 질문의 퇴적물이라는 뜻으로 읽힌다

- 원문(섹션 첫 페이지): https://docs.spring.io/spring-boot/how-to/index.html

## 목차 지도

23개 페이지. 아래는 **페이지 목록과 그 안의 절 제목(= 문서화된 질문)**이다. 답은 옮기지 않았다.

### 1. Spring Boot Application — 애플리케이션 자체를 손보는 자리
https://docs.spring.io/spring-boot/how-to/application.html

- Create Your Own FailureAnalyzer
- Troubleshoot Auto-configuration
- Customize the Environment or ApplicationContext Before It Starts
- Build an ApplicationContext Hierarchy (Adding a Parent or Root Context)
- Create a Non-web Application

> B03(SpringApplication 생명주기)이 설명한 단계들에 손을 넣는 질문들이다.

### 2. Properties and Configuration
https://docs.spring.io/spring-boot/how-to/properties-and-configuration.html

- Automatically Expand Properties at Build Time (Maven / Gradle 두 절)
- Externalize the Configuration of SpringApplication
- Change the Location of External Properties of an Application
- Use 'Short' Command Line Arguments
- Use YAML for External Properties
- Set the Active Spring Profiles
- Set the Default Profile Name
- Change Configuration Depending on the Environment
- Discover Built-in Options for External Properties

> B04·B05의 실무 질문 쪽.

### 3. Embedded Web Servers — 이 섹션에서 가장 긴 페이지(28절)
https://docs.spring.io/spring-boot/how-to/webserver.html

- Use Another Web Server / Disabling the Web Server
- Change the HTTP Port / Use a Random Unassigned HTTP Port / Discover the HTTP Port at Runtime / Build URI Against the Test Web Server
- Enable HTTP Response Compression
- Configure SSL (Using PEM-encoded files · Using SSL Bundles) / Configure Server Name Indication
- Configure HTTP/2 (Tomcat · Jetty · Reactor Netty 각각)
- Configure the Web Server
- Add a Servlet, Filter, or Listener to an Application (스프링 빈으로 / 클래스패스 스캐닝으로 / 등록 비활성화)
- Configure Access Logging
- Running Behind a Front-end Proxy Server / Customize Tomcat's Proxy Configuration
- Enable Multiple Connectors (Tomcat · Jetty)
- Enable Tomcat's MBean Registry
- Create WebSocket Endpoints Using @ServerEndpoint

### 4. Spring MVC
https://docs.spring.io/spring-boot/how-to/spring-mvc.html

- Write a JSON REST Service / Write an XML REST Service
- Customize the Jackson JsonMapper / Customize the @ResponseBody Rendering
- Handling Multipart File Uploads
- Switch Off the Spring MVC DispatcherServlet / Switch Off the Default MVC Configuration
- Customize ViewResolvers
- Customize the 'whitelabel' Error Page

### 5. Jersey
https://docs.spring.io/spring-boot/how-to/jersey.html

- Secure Jersey Endpoints with Spring Security
- Use Jersey Alongside Another Web Framework

### 6. HTTP Clients — 단 2절
https://docs.spring.io/spring-boot/how-to/http-clients.html

- Configure RestTemplate to Use a Proxy
- Configure the TcpClient used by a Reactor Netty-based WebClient

### 7. Logging
https://docs.spring.io/spring-boot/how-to/logging.html

- Configure Logback for Logging / Configure Logback for File-only Output
- Configure Log4j for Logging / Use YAML or JSON to Configure Log4j 2 / Use Composite Configuration to Configure Log4j 2

### 8. Data Access — 두 번째로 긴 페이지(17절)
https://docs.spring.io/spring-boot/how-to/data-access.html

- Configure a Custom DataSource / Configure Two DataSources
- Use Spring Data Repositories
- Separate @Entity Definitions from Spring Configuration / Filter Scanned @Entity Definitions
- Configure JPA Properties / Configure Hibernate Naming Strategy / Configure Hibernate Second-Level Caching / Use Dependency Injection in Hibernate Components
- Use a Custom EntityManagerFactory / Using Multiple EntityManagerFactories / Use a Traditional persistence.xml File
- Use Spring Data JPA and Mongo Repositories
- Customize Spring Data's Web Support / Expose Spring Data Repositories as REST Endpoint
- Configure a Component that is Used by JPA
- Configure jOOQ with Two DataSources

### 9. Database Initialization
https://docs.spring.io/spring-boot/how-to/data-initialization.html

- Initialize a Database Using Hibernate / Using Basic SQL Scripts / Initialize a Spring Batch Database
- Use a Higher-level Database Migration Tool (Flyway on Startup · Liquibase on Startup · 각각의 test-only 마이그레이션)
- Depend Upon an Initialized Database (Detect a Database Initializer · Detect a Bean That Depends On Database Initialization)

### 10. NoSQL — 단 1절
https://docs.spring.io/spring-boot/how-to/nosql.html

- Use Jedis Instead of Lettuce

### 11. Messaging — 단 1절
https://docs.spring.io/spring-boot/how-to/messaging.html

- Disable Transacted JMS Session

### 12. Batch Applications
https://docs.spring.io/spring-boot/how-to/batch.html

- Specifying a Batch Data Source / Batch Transaction Manager / Batch Task Executor
- Running From the Command Line
- Restarting a Stopped or Failed Job

> 트랙 B의 어느 모듈에도 배치가 없다. **Reference에 있는데 학습 지도가 다루지 않는 영역**을 확인하는 자리로 보인다.

### 13. Actuator
https://docs.spring.io/spring-boot/how-to/actuator.html

- Change the HTTP Port or Address of the Actuator Endpoints
- Customizing Sanitization
- Map Health Indicators to Micrometer Metrics

### 14. Security
https://docs.spring.io/spring-boot/how-to/security.html

- Switch Off the Spring Boot Security Configuration
- Change the UserDetailsService and Add User Accounts
- Enable HTTPS When Running Behind a Proxy Server

> B08이 한 챕터였던 것에 비해 How-to는 3절뿐이다. 실제 설정 질문은 Spring Security 자체 문서로 넘어간다는 신호로 읽힌다.

### 15. Hot Swapping
https://docs.spring.io/spring-boot/how-to/hotswapping.html

- Reload Static Content
- Reload Templates without Restarting the Container (Thymeleaf · FreeMarker · Groovy)
- Fast Application Restarts
- Reload Java Classes without Restarting the Container

### 16. Testing — 단 2절
https://docs.spring.io/spring-boot/how-to/testing.html

- Testing With Spring Security
- Structure `@Configuration` Classes for Inclusion in Slice Tests

### 17. Build
https://docs.spring.io/spring-boot/how-to/build.html

- Generate Build Information / Generate Git Information / Generate a CycloneDX SBOM
- Customize Dependency Versions
- Create an Executable JAR with Maven / Use a Spring Boot Application as a Dependency / Extract Specific Libraries When an Executable Jar Runs / Create a Non-executable JAR with Exclusions
- Remote Debug a Spring Boot Application Started with Maven
- Build an Executable Archive From Ant without Using spring-boot-antlib

### 18. Ahead-of-Time Processing
https://docs.spring.io/spring-boot/how-to/aot.html

- Conditions — `@Conditional`이 **빌드 시점에** 평가된다는 데서 나오는 문제와 Maven·Gradle에서 AOT 빌드의 프로파일을 지정하는 법

### 19. GraalVM Native Applications
https://docs.spring.io/spring-boot/how-to/native-image/index.html

- Developing Your First GraalVM Native Application — 샘플, Buildpacks로 굽기(시스템 요구사항·Maven·Gradle·실행), Native Build Tools로 굽기(사전 요구사항·Linux/macOS·Windows·Maven·Gradle·실행)
- Testing GraalVM Native Images — JVM에서 AOT 처리 테스트하기, Native Build Tools로 테스트(Maven·Gradle)

### 20. AOT Cache
https://docs.spring.io/spring-boot/how-to/aot-cache.html

- Packaging an Application Using AOT Cache and Buildpacks
- Packaging an Application Using AOT Cache and Dockerfiles
- Preventing Remote Services Interaction During the Training Run

### 21. Deploying Spring Boot Applications
https://docs.spring.io/spring-boot/how-to/deployment/index.html

- **Traditional Deployment** — Create a Deployable War File / Convert an Existing Application to Spring Boot / Deploying a WAR to WebLogic
- **Deploying to the Cloud** — Security considerations, Cloud Foundry(Binding to Services), Kubernetes(Container Lifecycle), Heroku, OpenShift, AWS(ECS · Elastic Beanstalk의 Tomcat/Java SE 두 플랫폼 · CloudCaptain), Azure, Google Cloud
- **Installing Spring Boot Applications** — Installation as a systemd Service / Microsoft Windows Services

> 「Convert an Existing Application to Spring Boot」는 **트랙 S(레거시)와 곧장 맞닿는 절**이다. S01에서 다시 펼칠 자리로 보인다.

### 22. Docker Compose
https://docs.spring.io/spring-boot/how-to/docker-compose.html

- Customizing the JDBC URL
- Sharing Services Between Multiple Applications

## 핵심 용어

| 용어 | 한 줄 (사전적 수준) |
| --- | --- |
| `FailureAnalyzer` | 시작 실패 예외를 사람이 읽을 수 있는 진단 메시지로 바꾸는 인터페이스 |
| ApplicationContext 계층 (hierarchy) | 컨텍스트에 부모를 두어, 자식이 부모의 빈을 볼 수 있게 만든 구조 |
| 프로퍼티 확장 (property expansion) | 빌드 도구가 빌드 시점에 `@…@`·`${…}` 자리표를 실제 값으로 치환하는 것 |
| SSL Bundle | 인증서·키·트러스트스토어를 이름 붙인 한 묶음으로 선언해 여러 곳에서 참조하게 하는 부트의 설정 단위 |
| SNI (Server Name Indication) | 하나의 IP·포트에서 요청된 호스트 이름에 따라 다른 인증서를 내주게 하는 TLS 확장 |
| 커넥터 (connector) | 톰캣·제티에서 하나의 프로토콜·포트 조합을 받는 입구. 여러 개 둘 수 있다 |
| MBean Registry | JMX로 노출되는 관리 객체(MBean)의 등록소. 톰캣은 기본으로 끄고 있다 |
| 액세스 로그 (access log) | 들어온 HTTP 요청 자체를 한 줄씩 남기는 서버 층의 로그. 애플리케이션 로깅과 다른 층 |
| 화이트레이블 에러 페이지 | 부트가 기본 제공하는 무장식 오류 화면 |
| Jersey | JAX-RS(자카르타 REST) 구현. Spring MVC와 나란히 선택 가능한 웹 갈래 |
| 2차 캐시 (second-level cache) | 하이버네이트에서 세션을 넘어 공유되는 엔티티 캐시 |
| `EntityManagerFactory` | JPA에서 `EntityManager`를 만들어 내는 공장. 데이터소스마다 하나씩 둘 수 있다 |
| `persistence.xml` | JPA 표준의 영속성 단위 설정 파일. 부트는 보통 이것 없이 설정한다 |
| Jedis / Lettuce | 두 가지 Redis 자바 클라이언트. 부트 기본은 Lettuce |
| Sanitization (Actuator) | 엔드포인트가 내보내는 값 중 민감한 것을 `******` 등으로 가리는 처리 |
| Hot swapping | 애플리케이션을 멈추지 않고 정적 자원·템플릿·클래스를 바꿔 끼우는 것 |
| SBOM / CycloneDX | Software Bill of Materials(포함된 구성요소 목록)와 그 표준 형식 중 하나 |
| AOT (Ahead-of-Time) 처리 | 런타임에 하던 일(조건 평가·빈 정의 생성)을 빌드 시점으로 앞당기는 처리 |
| AOT Cache | 훈련 실행(training run)으로 얻은 결과를 이미지에 담아 기동을 앞당기는 캐시 |
| 훈련 실행 (training run) | 캐시를 만들기 위해 빌드 중에 애플리케이션을 한 번 돌려 보는 단계 |
| Native Build Tools | GraalVM 네이티브 이미지를 Maven·Gradle에서 굽게 해 주는 플러그인 묶음 |
| Buildpacks | Dockerfile 없이 소스에서 컨테이너 이미지를 만들어 주는 규격 |
| systemd 서비스 | 리눅스에서 부팅 시 프로세스를 띄우고 관리하는 단위 |

## 처음 보는 개념

학습 지도에서 B15는 마지막 모듈이고 **정독 대상이 아니다.** 그래서 "새 개념"보다 **이 섹션이 Reference와 어떻게 다른 물건인지**가 이 모듈의 내용으로 보인다. 목차를 훑어 눈에 걸리는 지점 넷:

1. **페이지 길이가 극단적으로 불균등하다.** Embedded Web Servers 28절·Data Access 17절인데, HTTP Clients 2절·NoSQL 1절·Messaging 1절·Testing 2절이다. Reference에서의 비중과 순서가 전혀 다르다 — 길이가 **"쓰다가 자주 막히는 자리"**를 가리키는 지표일 수 있다.
2. **Reference에 있는데 트랙 B에 없는 영역이 여기서 드러난다.** Batch Applications가 그 예다. Jersey, Docker Compose도 트랙 B의 어느 모듈에도 배정돼 있지 않다.
3. **레거시와 맞닿는 절이 딱 한 곳에 있다.** Traditional Deployment의 「Convert an Existing Application to Spring Boot」. 트랙 S 전체가 다루려는 대상을 공식 문서가 어떻게 취급하는지 볼 수 있는 자리로 읽힌다.
4. **패키징 관련 페이지가 넷으로 흩어져 있다** (Build, AOT Processing, GraalVM Native, AOT Cache). B13에서 한 덩어리로 본 것이 How-to에서는 나뉘어 있다.

WMS 프로젝트(Spring Boot + React)와의 관계에서 먼저 펼칠 가능성이 높아 보이는 페이지: Embedded Web Servers(프록시 뒤 HTTPS·포트), Data Access(DataSource 두 개·JPA 프로퍼티), Database Initialization(Flyway), Docker Compose, Deploying(Kubernetes 또는 Installing).

## 학습 세션에서 확인할 것

- [ ] 이 섹션은 스스로 "완전하지 않다(not exhaustive)"고 밝힌다. 그러면 **How-to에 없는 문제를 만났을 때** 다음으로 어디를 보는 순서가 되는가 — Reference / 각 프로젝트 자체 문서 / API 문서 중 무엇이 먼저인가
- [ ] 페이지별 절 수가 크게 다르다(웹서버 28 : NoSQL 1). 이 불균등이 **무엇을 알려 주는 신호**로 읽히는가 — 그리고 짧은 페이지(HTTP Clients 2절)는 내용이 없는 것인가, 다른 곳으로 넘긴 것인가
- [ ] How-to의 절 제목은 대부분 동사로 시작한다. Reference의 절 제목과 나란히 두면, **같은 주제를 두 섹션이 어떻게 나눠 가졌는지**가 보이는가 (Security 챕터 vs Security How-to 3절로 대조해 볼 것)
- [ ] Batch Applications·Jersey는 트랙 B의 어느 모듈에도 없다. 학습 지도에 **추가할 것 / 필요할 때 찾아볼 것**으로 남길 것 중 어느 쪽인가
- [ ] 「Convert an Existing Application to Spring Boot」는 트랙 S가 다룰 레거시와 정면으로 맞닿는다. S01에 들어가기 전에 이 절을 먼저 읽어 두는 것이 도움이 되는가, 아니면 레거시를 먼저 본 뒤 읽어야 대조가 되는가
- [ ] 이 모듈의 산출물은 "지도"다. 나중에 막혔을 때 실제로 **펼칠 수 있는 형태**가 되려면, 정리본은 페이지 목록 그대로가 좋은가 아니면 "증상 → 페이지" 역색인이 좋은가

## 원문 링크

- How-to Guides 첫 페이지: https://docs.spring.io/spring-boot/how-to/index.html
- Spring Boot Application: https://docs.spring.io/spring-boot/how-to/application.html
- Properties and Configuration: https://docs.spring.io/spring-boot/how-to/properties-and-configuration.html
- Embedded Web Servers: https://docs.spring.io/spring-boot/how-to/webserver.html
- Spring MVC: https://docs.spring.io/spring-boot/how-to/spring-mvc.html
- Jersey: https://docs.spring.io/spring-boot/how-to/jersey.html
- HTTP Clients: https://docs.spring.io/spring-boot/how-to/http-clients.html
- Logging: https://docs.spring.io/spring-boot/how-to/logging.html
- Data Access: https://docs.spring.io/spring-boot/how-to/data-access.html
- Database Initialization: https://docs.spring.io/spring-boot/how-to/data-initialization.html
- NoSQL: https://docs.spring.io/spring-boot/how-to/nosql.html
- Messaging: https://docs.spring.io/spring-boot/how-to/messaging.html
- Batch Applications: https://docs.spring.io/spring-boot/how-to/batch.html
- Actuator: https://docs.spring.io/spring-boot/how-to/actuator.html
- Security: https://docs.spring.io/spring-boot/how-to/security.html
- Hot Swapping: https://docs.spring.io/spring-boot/how-to/hotswapping.html
- Testing: https://docs.spring.io/spring-boot/how-to/testing.html
- Build: https://docs.spring.io/spring-boot/how-to/build.html
- Ahead-of-Time Processing: https://docs.spring.io/spring-boot/how-to/aot.html
- GraalVM Native Applications: https://docs.spring.io/spring-boot/how-to/native-image/index.html
- Developing Your First GraalVM Native Application: https://docs.spring.io/spring-boot/how-to/native-image/developing-your-first-application.html
- Testing GraalVM Native Images: https://docs.spring.io/spring-boot/how-to/native-image/testing-native-applications.html
- AOT Cache: https://docs.spring.io/spring-boot/how-to/aot-cache.html
- Deploying Spring Boot Applications: https://docs.spring.io/spring-boot/how-to/deployment/index.html
- Traditional Deployment: https://docs.spring.io/spring-boot/how-to/deployment/traditional-deployment.html
- Deploying to the Cloud: https://docs.spring.io/spring-boot/how-to/deployment/cloud.html
- Installing Spring Boot Applications: https://docs.spring.io/spring-boot/how-to/deployment/installing.html
- Docker Compose: https://docs.spring.io/spring-boot/how-to/docker-compose.html
