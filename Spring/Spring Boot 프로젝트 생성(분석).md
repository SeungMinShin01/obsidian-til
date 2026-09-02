---
출처: Claude 분석
원본: KDT_2026/2026B_Spring/springweb
작성일: 2026-08-24
tags: [학습, java]
---

# Java — Spring Boot 프로젝트 생성

> 실습 파일: `2026B_Spring/springweb/build.gradle` · `settings.gradle` · `gradle/wrapper/gradle-wrapper.properties` · `src/main/java/com/example/SpringwebApplication.java` · `src/main/resources/application.properties` · `src/test/java/com/example/SpringwebApplicationTests.java`
> 허브: Java MOC · 이전: Java day16 스레드 동기화 · 다음: Spring day01 서블릿과 HTTP 메소드

여기서부터 저장소가 하나 늘었다. `2026B_BE` 는 순수 자바로 콘솔 프로그램을 만들던 자리였고, 새로 생긴 `2026B_Spring` 은 **웹 애플리케이션**을 만드는 자리다. 아직 화면도 요청 처리도 없고 뼈대만 있는 상태라, 이번에는 만들어진 파일 하나하나가 무엇을 맡는지부터 정리해 둔다.

Java day16 스레드 동기화 에서 "요청마다 스레드를 붙이는 웹서버(톰캣)"를 이야기로만 봤는데, 이 프로젝트를 실행하면 그 톰캣이 실제로 뜬다. 지금까지 개념으로 다룬 것들이 어디에 놓이는지 확인하기 좋은 지점이다.

## 1. 배운 내용

### 1-1. 만들어진 것 — 스프링 부트 프로젝트의 뼈대

생성된 파일은 열두 개가 되지 않는다. 정리하면 이렇다.

```
springweb/
├── build.gradle                 빌드 설정 — 어떤 라이브러리를 쓸지
├── settings.gradle              프로젝트 이름
├── gradlew · gradlew.bat        그레이들 실행 스크립트(래퍼)
├── gradle/wrapper/              래퍼가 내려받을 그레이들 버전 정보
├── src/main/java/com/example/
│   └── SpringwebApplication.java   시작점
├── src/main/resources/
│   └── application.properties      설정값
└── src/test/java/com/example/
    └── SpringwebApplicationTests.java  테스트
```

`src/main` 과 `src/test` 로 갈라 두는 구조가 눈에 띈다. 지금까지는 `day16/exam/exam1.java` 처럼 폴더를 자유롭게 만들었는데, 여기서는 **소스 위치가 규칙으로 정해져 있다.** 빌드 도구가 `src/main/java` 를 컴파일 대상으로, `src/main/resources` 를 설정 파일 자리로, `src/test/java` 를 테스트 자리로 미리 약속해 두었기 때문이다.

| 폴더 | 담기는 것 | 결과물에 포함 |
| --- | --- | --- |
| `src/main/java` | 실제 동작하는 코드 | 포함 |
| `src/main/resources` | 설정 파일·정적 자원·템플릿 | 포함 |
| `src/test/java` | 테스트 코드 | 제외 |
| `build/` · `.gradle/` | 빌드 산출물·캐시 | 버전 관리 대상 아님 |

마지막 줄은 지금까지 `bin/` 과 `.class` 를 무시하던 것과 같은 이야기다. **소스만 남기고 만들어진 것은 남기지 않는다** — 새로 생긴 `.gitignore` 가 그 역할을 한다.

### 1-2. build.gradle — 무엇을 쓸지 적어 두는 파일

지금까지는 필요한 라이브러리를 직접 내려받아 `lib/` 에 넣고 클래스패스를 잡았다. Java day12 예외 처리와 JDBC 에서 MySQL 커넥터를 붙이던 방식이 그것이다. 빌드 도구를 쓰면 그 일을 **파일에 적어 두는 것**으로 바꾼다.

```groovy
plugins {
    id 'java'
    id 'org.springframework.boot' version '4.1.1'
    id 'io.spring.dependency-management' version '1.1.7'
}

group = 'springweb'
version = '0.0.1-SNAPSHOT'

java {
    toolchain {
        languageVersion = JavaLanguageVersion.of(21)
    }
}

repositories {
    mavenCentral()
}

dependencies {
    implementation 'org.springframework.boot:spring-boot-starter-webmvc'
    testImplementation 'org.springframework.boot:spring-boot-starter-webmvc-test'
    testRuntimeOnly 'org.junit.platform:junit-platform-launcher'
}

tasks.named('test') {
    useJUnitPlatform()
}
```

블록별로 하는 일이 갈린다.

| 블록 | 하는 일 |
| --- | --- |
| `plugins` | 빌드에 기능을 붙인다 — 자바 컴파일, 스프링 부트 실행·패키징, 버전 관리 |
| `group` · `version` | 이 프로젝트의 좌표. 나중에 이 프로젝트가 라이브러리가 되면 이름표가 된다 |
| `java { toolchain }` | 어떤 자바 버전으로 컴파일할지 — 여기서는 21 |
| `repositories` | 라이브러리를 어디서 내려받을지 — `mavenCentral()` 이 공개 저장소 |
| `dependencies` | 필요한 라이브러리 목록 |
| `tasks.named('test')` | 테스트를 JUnit 5 방식으로 실행 |

핵심은 `dependencies` 다. 여기에 한 줄 적으면 그레이들이 저장소에서 그 라이브러리와 **그 라이브러리가 필요로 하는 것들까지 함께** 내려받는다. 직접 관리하던 의존성 문제가 선언 하나로 바뀌는 셈이다.

`implementation` 과 `testImplementation` 이 갈려 있는 것도 봐 둔다. 앞은 실제 실행에 쓰이고, 뒤는 테스트할 때만 쓰인다. 테스트 도구가 최종 결과물에 섞여 들어가지 않게 구분해 둔 것이다.

### 1-3. 스타터 — 묶음으로 가져오는 의존성

`spring-boot-starter-webmvc` 는 라이브러리 하나가 아니라 **묶음**이다. 웹 애플리케이션을 만들려면 보통 이런 것들이 함께 필요하다.

```
spring-boot-starter-webmvc
├── spring-web · spring-webmvc      요청을 받아 처리하는 핵심
├── spring-boot-starter-tomcat      내장 톰캣(웹서버)
├── spring-boot-starter-json        JSON 변환(Jackson)
└── spring-boot-starter             공통 — 자동 구성·로깅·설정
```

이렇게 자주 함께 쓰이는 조합을 미리 묶어 둔 것을 **스타터(starter)** 라고 부른다. 이름이 `spring-boot-starter-` 로 시작하면 대체로 이 성격이다.

| 스타터 | 붙이는 기능 |
| --- | --- |
| `starter-webmvc` | 웹 MVC + 내장 톰캣 |
| `starter-data-jpa` | JPA·Hibernate — DB를 객체로 다루기 |
| `starter-jdbc` | JDBC 템플릿 |
| `starter-thymeleaf` | 서버 사이드 템플릿 엔진 |
| `starter-security` | 인증·인가 |
| `starter-test` | JUnit·Mockito·AssertJ 묶음 |

**버전 번호를 적지 않았다**는 점이 눈에 띈다. `io.spring.dependency-management` 플러그인이 스프링 부트 버전(4.1.1)에 맞는 라이브러리 조합을 이미 알고 있어서, 서로 충돌하지 않는 버전을 알아서 맞춰 준다. 직접 버전을 고르다 어긋나는 문제를 없애려는 장치다.

### 1-4. 내장 톰캣 — 서버가 프로젝트 안에 들어온다

`starter-webmvc` 에 톰캣이 들어 있다는 사실이 구조를 바꾼다.

| | 예전 방식 | 스프링 부트 |
| --- | --- | --- |
| 서버 | 톰캣을 따로 설치해 둔다 | 프로젝트 의존성으로 들어 있다 |
| 배포 | war 파일을 톰캣에 올린다 | jar 하나를 그냥 실행한다 |
| 실행 | 서버를 켜고 앱을 올린다 | `main` 메소드를 실행하면 서버가 뜬다 |

즉 **앱이 서버 위에 올라가는 것이 아니라, 앱이 서버를 들고 있는** 형태다. 그래서 지금까지 해 오던 것처럼 `main` 메소드를 실행하는 것만으로 웹서버가 뜬다. 기본 포트는 8080이다.

Java day16 스레드 동기화 1-1의 그림이 여기서 실물이 된다 — 이 톰캣이 요청마다 스레드를 붙이고, 우리가 작성할 코드는 그 스레드 위에서 돈다.

### 1-5. 그레이들 래퍼 — 빌드 도구까지 프로젝트가 들고 있다

`gradlew`·`gradlew.bat`·`gradle/wrapper/` 세 자리가 **래퍼(wrapper)** 다.

```properties
distributionUrl=https\://services.gradle.org/distributions/gradle-9.5.1-bin.zip
```

여기에 적힌 버전을 쓰겠다는 선언이고, `gradlew` 를 실행하면 그 버전이 없을 때 자동으로 내려받아 쓴다. 그레이들을 설치하지 않은 컴퓨터에서도 같은 버전으로 빌드되게 만드는 장치다.

- `./gradlew build` — 컴파일 + 테스트 + jar 생성
- `./gradlew bootRun` — 애플리케이션 실행
- `gradlew` 는 리눅스·맥, `gradlew.bat` 은 윈도우

같은 소스인데 사람마다 결과가 다른 상황을 막는 것이 목적이다. 자바 버전을 `toolchain` 으로 못 박은 것(1-2)도 같은 방향이다.

### 1-6. 시작점 — @SpringBootApplication

실제 자바 코드는 이 파일 하나뿐이다.

```java
package com.example;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

@SpringBootApplication
public class SpringwebApplication {

    public static void main(String[] args) {
        SpringApplication.run(SpringwebApplication.class, args);
    }

}
```

지금까지 만든 `AppStart` 와 형태는 같다 — `main` 이 있고 거기서 출발한다. 달라진 것은 두 줄이다.

**`@SpringBootApplication`** 은 애노테이션 세 개를 합쳐 놓은 것이다.

| 합쳐진 애노테이션 | 하는 일 |
| --- | --- |
| `@SpringBootConfiguration` | 이 클래스가 설정 클래스임을 표시 |
| `@EnableAutoConfiguration` | **자동 구성** — 의존성을 보고 필요한 설정을 알아서 한다 |
| `@ComponentScan` | 이 패키지와 하위 패키지를 훑어 관리 대상 클래스를 찾는다 |

세 번째가 특히 중요하다. `com.example` 아래에 클래스를 만들면 스프링이 **알아서 찾는다.** 그래서 시작 클래스는 항상 최상위 패키지에 두고, 나머지 코드는 그 아래에 만든다. 위치를 잘못 잡으면 만든 클래스를 스프링이 못 보는 일이 생긴다.

두 번째인 자동 구성은 "톰캣이 클래스패스에 있으면 웹서버를 띄우고, DB 드라이버가 있으면 커넥션 풀을 준비한다" 같은 판단을 대신해 주는 부분이다. 설정 파일을 길게 쓰지 않아도 도는 이유가 여기 있다.

**`SpringApplication.run(...)`** 은 스프링 컨테이너를 만들고, 컴포넌트를 찾아 등록하고, 내장 톰캣을 띄우는 일을 한 줄로 처리한다. 이 한 줄이 끝나도 프로그램이 종료되지 않는데, 톰캣의 스레드가 계속 살아 요청을 기다리기 때문이다 — Java day16 스레드 동기화 1-12에서 본 비데몬 스레드와 같은 성질이다.

### 1-7. application.properties — 설정을 코드 밖으로

```properties
spring.application.name=springweb
```

지금은 이름 한 줄뿐이지만, 여기가 **설정을 모아 두는 자리**다. 코드를 고치지 않고 값만 바꿔 동작을 조정하려는 것이 목적이다.

| 키 | 뜻 |
| --- | --- |
| `spring.application.name` | 애플리케이션 이름 — 로그·모니터링에서 식별용 |
| `server.port` | 서버 포트 (기본 8080) |
| `spring.datasource.url` | DB 접속 주소 |
| `logging.level.<패키지>` | 로그 상세도 |

Java day12 예외 처리와 JDBC 에서 DB 주소·계정을 자바 코드 안에 문자열로 박아 두었는데, 스프링에서는 이런 값이 전부 이쪽으로 나온다. 접속 정보처럼 환경마다 달라지는 값을 코드에서 떼어 내면, 같은 코드로 개발·운영 환경을 모두 돌릴 수 있다.

계정·비밀번호가 이 파일에 들어가므로 **버전 관리에 올릴 때 주의가 필요한 파일**이기도 하다. 실제로는 환경 변수나 별도 설정으로 빼는 방식을 쓴다.

### 1-8. 테스트 — 뜨는지부터 확인한다

```java
@SpringBootTest
class SpringwebApplicationTests {

    @Test
    void contextLoads() {
    }

}
```

메소드 안이 비어 있는데도 의미가 있는 테스트다.

- `@SpringBootTest` — 실제 애플리케이션과 같은 방식으로 **스프링 컨테이너를 띄운다**
- `contextLoads()` — 뜨는 도중 오류가 나면 테스트가 실패한다

즉 "설정이 잘못돼서 애초에 뜨지도 않는" 상황을 잡아 주는 안전망이다. 설정을 늘려 갈수록 이 테스트 하나의 값어치가 커진다.

`@Test` 는 JUnit 5의 애노테이션이고, 실행은 1-2의 `useJUnitPlatform()` 설정이 맡는다. 지금까지 `main` 에 코드를 넣어 눈으로 확인하던 것을, 앞으로는 이 자리에서 자동으로 확인하게 된다.

### 1-9. 정리 — 순수 자바에서 달라진 것

지금까지 만든 것과 나란히 두면 차이가 분명하다.

| | 2026B_BE (순수 자바) | 2026B_Spring |
| --- | --- | --- |
| 소스 위치 | 자유롭게 폴더 생성 | `src/main/java` 로 고정 |
| 라이브러리 | 직접 내려받아 `lib/` 에 배치 | `build.gradle` 에 한 줄 선언 |
| 실행 | 클래스 하나를 실행 | `main` 하나가 서버까지 띄운다 |
| 설정 | 코드 안에 문자열로 | `application.properties` 로 분리 |
| 객체 생성 | `new` 로 직접, 싱글톤도 직접 구현 | 컨테이너가 만들고 넣어 준다 (다음 주제) |

마지막 줄이 앞으로의 핵심이다. Java day11 종합예제 인터페이스 DAO · Java day12 종합예제 JDBC DAO 에서 `getInstance()` 로 직접 만들던 [[개념 - 싱글톤]] 구조를, 스프링에서는 컨테이너가 대신한다. 지금 프로젝트에 클래스가 하나뿐이라 그 장면이 아직 안 보일 뿐이다.

## 2. 추가로 알면 좋은 활용법

### 2-1. 첫 화면 띄우기 — 컨트롤러 하나

뼈대만으로는 브라우저에서 볼 것이 없다. 클래스 하나를 더하면 응답이 나온다.

```java
package com.example.controller;

import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
public class HelloController {

    @GetMapping("/hello")
    public String hello() {
        return "안녕하세요";
    }
}
```

- `@RestController` — 이 클래스가 요청을 받는 자리임을 표시하고, 반환값을 **그대로 응답 본문**으로 보낸다
- `@GetMapping("/hello")` — GET 방식으로 `/hello` 로 들어온 요청을 이 메소드에 연결

패키지가 `com.example.controller` 로 시작 클래스(`com.example`)의 **아래**라는 점이 중요하다. 1-6의 `@ComponentScan` 이 훑는 범위 안이어야 스프링이 찾는다.

`@Controller` 와 `@RestController` 가 갈리는 자리도 함께 잡아 둔다.

| 애노테이션 | 반환값의 뜻 |
| --- | --- |
| `@Controller` | **화면 이름** — 템플릿 파일을 찾아 렌더링 |
| `@RestController` | **데이터 그 자체** — 문자열·JSON으로 응답 |

JS day13 웹 스토리지와 인터벌 · JS day14 게시판 CRUD 에서 프론트가 데이터를 받아 화면을 그렸던 구조라면 `@RestController` 쪽이 짝이 된다.

### 2-2. 요청 방식과 값 받기

HTTP 요청 방식마다 애노테이션이 준비돼 있다.

| 애노테이션 | 방식 | 쓰이는 자리 |
| --- | --- | --- |
| `@GetMapping` | GET | 조회 |
| `@PostMapping` | POST | 등록 |
| `@PutMapping` | PUT | 수정 |
| `@DeleteMapping` | DELETE | 삭제 |

[[개념 - CRUD]] 의 네 동작이 그대로 방식 네 개에 대응한다. 콘솔에서 메뉴 번호로 갈랐던 것이, 웹에서는 **주소 + 방식**의 조합으로 갈리는 셈이다.

값을 받는 방법도 자리에 따라 나뉜다.

```java
@GetMapping("/board")
public String find(@RequestParam int no) { ... }        // /board?no=3

@GetMapping("/board/{no}")
public String find2(@PathVariable int no) { ... }        // /board/3

@PostMapping("/board")
public String write(@RequestBody BoardDto dto) { ... }   // 본문의 JSON을 DTO로
```

세 번째가 특히 편한 부분이다. 요청 본문의 JSON을 자바 객체로 **알아서 변환**해 준다 — Java day15 Map과 HashMap 에서 정리한 JSON과 Map·DTO의 대응을 라이브러리가 대신 처리하는 자리다.

### 2-3. 의존성 주입 — new를 쓰지 않는다

스프링을 쓰는 이유의 절반이 여기 있다.

```java
@Service
public class BoardService {
    public String find() { return "글 목록"; }
}

@RestController
public class BoardController {
    private final BoardService service;

    public BoardController(BoardService service) {   // 생성자로 받는다
        this.service = service;
    }
}
```

`new BoardService()` 가 어디에도 없다. 스프링이 `@Service` 가 붙은 클래스를 찾아 객체를 만들어 두고, 그것이 필요한 곳의 **생성자에 넣어 준다.** 이것이 의존성 주입(DI)이다.

| 애노테이션 | 역할 표시 |
| --- | --- |
| `@Controller`·`@RestController` | 요청을 받는 계층 |
| `@Service` | 업무 로직 계층 |
| `@Repository` | 데이터 접근 계층 (DAO) |
| `@Component` | 위에 해당하지 않는 일반 관리 대상 |

Java day09 MVC 종합예제 의 네 계층이 이름만 바꿔 그대로 있다. 달라진 것은 **배선을 누가 하느냐**뿐이다 — 직접 `getInstance()` 를 불러 연결하던 자리를 컨테이너가 맡는다.

주입 방법은 생성자 주입을 쓰는 편이 낫다. 필드에 `@Autowired` 를 붙이는 방식보다 `final` 로 굳힐 수 있고, 테스트할 때 다른 구현을 넣기도 쉽다 — Java day11 인터페이스 의 "인터페이스로 받고 구현체를 갈아 끼운다"가 여기서 프레임워크 기능이 된다.

### 2-4. 자주 쓰는 설정값

`application.properties` 에 자주 들어가는 항목을 모아 둔다.

```properties
server.port=8081

spring.datasource.url=jdbc:mysql://localhost:3306/스키마명
spring.datasource.username=계정
spring.datasource.password=****

spring.jpa.hibernate.ddl-auto=update
spring.jpa.show-sql=true

logging.level.org.springframework.web=debug
```

`.properties` 대신 `.yml` 형식을 쓰기도 한다. 계층이 들여쓰기로 표현돼 항목이 많아질수록 읽기 편하다.

```yaml
server:
  port: 8081
spring:
  datasource:
    url: jdbc:mysql://localhost:3306/스키마명
```

둘 중 하나만 쓰면 되고, 내용은 같다.

### 2-5. 의존성 더하기 — DB를 붙일 때

Java day12 예외 처리와 JDBC 에서 하던 일을 스프링에서 이어 가려면 `build.gradle` 에 두 줄을 더한다.

```groovy
implementation 'org.springframework.boot:spring-boot-starter-data-jpa'
runtimeOnly 'com.mysql:mysql-connector-j'
```

드라이버가 `runtimeOnly` 인 이유가 있다. 코드에서 드라이버 클래스를 직접 부르지 않고 **실행할 때만** 필요하기 때문이다. 컴파일 단계에서 접근하지 못하게 막아 두면, 특정 DB에 코드가 묶이는 일을 줄일 수 있다.

의존성을 바꾸면 그레이들이 다시 내려받아야 한다. IDE에서는 새로고침 버튼을, 터미널에서는 `./gradlew build` 를 한 번 돌려 준다.

### 2-6. 개발할 때 편한 것들

| 의존성·설정 | 하는 일 |
| --- | --- |
| `spring-boot-devtools` | 코드를 고치면 자동 재시작 |
| `spring-boot-starter-actuator` | 상태 확인용 주소(`/actuator/health`) 제공 |
| `spring.output.ansi.enabled=always` | 로그에 색을 넣어 읽기 쉽게 |

`devtools` 는 특히 초반에 체감이 크다. 화면 하나 고칠 때마다 서버를 껐다 켜는 일이 사라진다.

### 2-7. 프로파일 — 환경별로 다른 설정

개발 컴퓨터와 실제 서버는 DB도 포트도 다르다. 파일을 나눠 두고 골라 쓴다.

```
application.properties            공통
application-dev.properties        개발용
application-prod.properties       운영용
```

```properties
spring.profiles.active=dev
```

이 한 줄로 `application-dev.properties` 가 함께 읽힌다. 실행할 때 인자로 넘겨 바꿀 수도 있어서, **같은 jar 파일을 환경만 바꿔 돌리는** 방식이 가능해진다.

### 2-8. 빌드 결과물 — jar 하나로

```
./gradlew build
→ build/libs/springweb-0.0.1-SNAPSHOT.jar

java -jar springweb-0.0.1-SNAPSHOT.jar
```

이 jar 안에는 우리 코드뿐 아니라 **의존 라이브러리와 톰캣까지** 들어 있다. 그래서 자바만 설치된 컴퓨터라면 어디서든 이 한 줄로 서버가 뜬다. 이런 형태를 실행 가능한 jar 라고 부르고, 스프링 부트 플러그인(1-2의 `org.springframework.boot`)이 만들어 준다.

배포가 "파일 하나를 옮기고 실행"으로 줄어드는 것이 스프링 부트가 널리 쓰이게 된 이유 중 하나다.

## 3. 더 나아가 알면 좋은 것

### 3-1. 제어의 역전 — 흐름의 주인이 바뀐다

스프링의 바탕에 있는 생각을 한 줄로 정리하면 **제어의 역전(IoC)** 이다.

| | 지금까지 | 프레임워크 위에서 |
| --- | --- | --- |
| 객체 생성 | 내가 `new` 한다 | 컨테이너가 만든다 |
| 호출 흐름 | 내 코드가 라이브러리를 부른다 | **프레임워크가 내 코드를 부른다** |
| 내가 쓰는 것 | 도구 | 빈칸을 채우는 사람 |

라이브러리와 프레임워크가 갈리는 자리가 여기다. `Scanner` 는 내가 필요할 때 부르는 도구지만, `@GetMapping` 을 붙인 메소드는 **내가 부르지 않는다** — 요청이 들어오면 스프링이 부른다. 만든 코드가 언제 실행될지를 프레임워크가 정하는 구조다.

Java day11 인터페이스 에서 익명 구현체로 만들어 넘기던 것, Java day16 스레드 동기화 에서 `Runnable` 을 만들어 풀에 넘기던 것이 작은 규모의 같은 형태다 — **할 일만 정의하고 실행 시점은 넘긴다.**

### 3-2. 빈과 컨테이너 — 싱글톤이 기본인 이유

스프링이 관리하는 객체를 **빈(bean)** 이라 하고, 담아 두는 곳을 **컨테이너**라고 부른다. 빈은 기본적으로 **하나만 만들어져 공유**된다.

| 스코프 | 개수 |
| --- | --- |
| `singleton` (기본) | 컨테이너당 하나 |
| `prototype` | 요청할 때마다 새로 |
| `request` | HTTP 요청마다 하나 |

여기서 Java day16 스레드 동기화 2-6이 그대로 이어진다. 컨트롤러·서비스·리포지토리가 전부 싱글톤이니, **여러 요청 스레드가 같은 객체의 메소드를 동시에 부른다.** 그래서 이 클래스들에 상태를 담는 필드를 두면 경쟁 상태가 생긴다.

- 안전한 형태 — 필드에는 주입받은 다른 빈만 두고(`final`), 처리에 쓰는 값은 매개변수와 지역 변수로
- 위험한 형태 — 처리 중인 데이터를 필드에 담아 두기

[[개념 - 싱글톤]] 을 직접 구현하며 정리한 성질이 프레임워크 규약으로 올라온 셈이고, 그래서 "스프링 빈은 무상태로 만든다"가 기본 방침이 된다.

### 3-3. 자동 구성은 어떻게 판단하는가

`@EnableAutoConfiguration`(1-6)이 알아서 해 준다는 말이 마법처럼 들리지만, 규칙은 단순하다. **클래스패스에 무엇이 있는지 보고 결정한다.**

```
클래스패스에 톰캣이 있다     → 웹서버를 띄운다
DataSource 설정이 있다      → 커넥션 풀을 만든다
이미 내가 만든 빈이 있다     → 자동 구성은 물러난다
```

마지막 줄이 중요하다. 자동 구성은 **내가 직접 만든 설정이 없을 때만** 동작한다. 그래서 기본값으로 시작했다가 필요한 부분만 직접 정의해 덮어쓰는 방식이 가능하다.

어떤 자동 구성이 적용됐고 왜 빠졌는지는 실행 인자 `--debug` 로 확인할 수 있다. "왜 이게 안 되지"를 풀 때 먼저 보는 자리다.

### 3-4. 요청이 지나가는 길

주소 하나가 처리되는 경로를 그려 두면 앞으로 배울 것들의 자리가 잡힌다.

```
브라우저
  ↓ HTTP 요청
내장 톰캣            ← 요청마다 스레드 배정 (day16)
  ↓
DispatcherServlet   ← 모든 요청의 진입점
  ↓ 주소를 보고 담당자를 찾는다
Controller          ← @GetMapping 등
  ↓
Service             ← 업무 로직
  ↓
Repository          ← DB 접근 (JDBC·JPA)
  ↓
MySQL
```

Java day09 MVC 종합예제 에서 View·Controller·DAO·DTO로 나눈 구조가 웹으로 옮겨온 모습이다. 달라진 부분은 맨 위 두 층 — 콘솔에서 `Scanner` 로 받던 입력이 HTTP 요청이 되고, 그것을 나눠 주는 `DispatcherServlet` 이 앞에 선다.

`DispatcherServlet` 하나가 모든 요청을 받아 담당자에게 넘기는 구조를 프론트 컨트롤러 패턴이라고 부른다.

### 3-5. JPA — 다음에 만날 큰 주제

`starter-data-jpa` 를 붙이면 DB를 다루는 방식이 또 한 번 바뀐다.

| | JDBC (day12) | JPA |
| --- | --- | --- |
| SQL | 직접 문자열로 작성 | 대부분 생성해 준다 |
| 결과 처리 | `ResultSet` 에서 하나씩 꺼내 DTO에 담기 | 객체로 바로 받는다 |
| 관점 | 표(row)를 다룬다 | **객체를 다룬다** |

```java
public interface BoardRepository extends JpaRepository<Board, Long> {
    List<Board> findByTitleContaining(String keyword);
}
```

구현 클래스를 만들지 않았는데 동작한다. 인터페이스의 **메소드 이름을 해석해** 스프링이 구현체를 만들어 넣는 방식이다. Java day11 종합예제 인터페이스 DAO 에서 인터페이스로 규격을 잡고 구현을 따로 만들던 구조에서, 구현 쪽을 프레임워크가 가져간 형태로 볼 수 있다.

편한 만큼 안에서 어떤 SQL이 나가는지 모르면 성능 문제로 이어지기 쉬워서, JDBC와 SQL을 먼저 본 순서가 도움이 된다 — SQL day03 DML과 조인 · SQL day05 외래키 CASCADE와 조인 의 조인 이해가 그대로 쓰인다.

### 3-6. 빌드 도구 — 그레이들과 메이븐

자바 빌드 도구는 크게 둘이다.

| | 메이븐 | 그레이들 |
| --- | --- | --- |
| 설정 파일 | `pom.xml` (XML) | `build.gradle` (Groovy·Kotlin) |
| 성격 | 정해진 흐름을 따른다 | 스크립트라 자유도가 높다 |
| 속도 | — | 증분 빌드·캐시로 대체로 빠르다 |

둘 다 하는 일은 같다 — 의존성을 내려받고, 컴파일하고, 테스트하고, 패키징한다. 이 프로젝트는 그레이들 쪽이다. 자료를 찾을 때 `pom.xml` 예시가 나오면 `dependencies` 표기만 바꿔 읽으면 된다.

### 3-7. 스프링과 스프링 부트의 관계

이름이 비슷해 헷갈리기 쉬운데 층이 다르다.

- **스프링 프레임워크** — DI 컨테이너, MVC, 트랜잭션 등 실제 기능
- **스프링 부트** — 그 위에 얹어 **설정을 자동화하고 실행을 단순하게** 만든 것

부트가 없던 시절에는 XML 설정을 길게 쓰고 톰캣에 war를 올렸다. 부트는 그 준비 과정을 줄여 주는 쪽이고, 안에서 도는 것은 여전히 스프링 프레임워크다. 그래서 부트를 쓰더라도 결국은 스프링의 개념(빈·DI·AOP)을 알아야 한다.

### 3-8. 다음에 볼 키워드

- 스프링 부트 프로젝트 생성 — Spring Initializr, group·artifact·패키징
- 그레이들 — `plugins`·`dependencies`·`repositories`·toolchain, 래퍼(`gradlew`)
- `implementation`·`testImplementation`·`runtimeOnly` 의존성 범위
- 스타터(starter)와 의존성 버전 관리(`dependency-management`)
- 내장 톰캣과 실행 가능한 jar, war 배포와의 차이
- `@SpringBootApplication` = `@SpringBootConfiguration` + `@EnableAutoConfiguration` + `@ComponentScan`
- 컴포넌트 스캔 범위와 패키지 배치 규칙
- `SpringApplication.run()` 이 하는 일 — 컨테이너 구동·빈 등록·서버 기동
- `application.properties` / `.yml`, 프로파일(`spring.profiles.active`)
- `@SpringBootTest` 와 `contextLoads`, JUnit 5(`useJUnitPlatform`)
- `@Controller` 와 `@RestController`, `@GetMapping`·`@PostMapping`·`@PutMapping`·`@DeleteMapping`
- `@RequestParam`·`@PathVariable`·`@RequestBody` 와 JSON 변환(Jackson)
- 의존성 주입(DI)과 제어의 역전(IoC), 생성자 주입과 `@Autowired`
- 스테레오타입 애노테이션 — `@Service`·`@Repository`·`@Component`
- 빈(bean)과 컨테이너, 빈 스코프(singleton·prototype·request)
- 싱글톤 빈과 무상태 설계 — 멀티스레드 안전성
- `DispatcherServlet` 과 프론트 컨트롤러 패턴, 요청 처리 흐름
- 자동 구성의 판단 근거와 `--debug` 로 확인하기
- `spring-boot-devtools`·`actuator`
- JPA·Hibernate, `JpaRepository`, 메소드 이름 기반 쿼리, `ddl-auto`
- 그레이들과 메이븐, `build.gradle` 과 `pom.xml`
- 스프링 프레임워크와 스프링 부트의 층위, AOP·트랜잭션

## 실습 파일

- `2026B_Spring/springweb/build.gradle` (스프링 부트·의존성 관리 플러그인 적용, 자바 21 툴체인 지정, `mavenCentral()` 저장소, `spring-boot-starter-webmvc` 의존성 선언, 테스트 의존성과 `useJUnitPlatform()` 설정)
- `2026B_Spring/springweb/settings.gradle` (루트 프로젝트 이름 `springweb`)
- `2026B_Spring/springweb/gradle/wrapper/gradle-wrapper.properties` (그레이들 9.5.1 배포본 URL, 래퍼 경로·타임아웃 설정)
- `2026B_Spring/springweb/src/main/java/com/example/SpringwebApplication.java` (`@SpringBootApplication` 을 붙인 시작 클래스, `SpringApplication.run` 으로 컨테이너·내장 톰캣 기동)
- `2026B_Spring/springweb/src/main/resources/application.properties` (`spring.application.name` 설정)
- `2026B_Spring/springweb/src/test/java/com/example/SpringwebApplicationTests.java` (`@SpringBootTest` 로 컨텍스트를 띄우는 `contextLoads` 테스트)

## 관련 노트

Java MOC · Spring day01 서블릿과 HTTP 메소드 · Java day16 스레드 동기화 · Java day15 Map과 HashMap · Java day12 예외 처리와 JDBC · Java day12 종합예제 JDBC DAO · Java day11 인터페이스 · Java day11 종합예제 인터페이스 DAO · Java day09 MVC 종합예제 · [[개념 - 싱글톤]] · [[개념 - CRUD]] · SQL day03 DML과 조인 · SQL day05 외래키 CASCADE와 조인 · JS day14 게시판 CRUD · [[KDT_2026 학습 지도]]
