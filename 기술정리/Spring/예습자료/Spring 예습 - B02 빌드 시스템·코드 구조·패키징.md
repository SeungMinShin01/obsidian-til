---
출처: 자동수집(Claude)
작성일: 2026-09-17
성격: 예습자료
tags: [학습, spring]
---

# Spring 예습 - B02 빌드 시스템·코드 구조·패키징

> 예습자료 — 자동 생성, 사용자 미검증. 결론이 아니라 **읽을 범위의 지도**다.
> 기준 버전: Spring Boot 4.1.1

## 이 모듈이 다루는 범위

B01이 "한 바퀴 돌려 보기"였다면 B02는 그 한 바퀴를 **세 갈래로 쪼개 각각을 규격으로 다시 보는** 자리다. 공식 문서에서 대응하는 자리는 네 곳이고, 앞의 두 개가 본체다.

| 문서 | 문서가 서 있는 자리 |
| --- | --- |
| Reference → Developing with Spring Boot → Build Systems | 빌드 도구가 부트에게서 무엇을 받아 가는지 — 의존성 버전 관리와 스타터라는 두 장치 |
| Reference → Developing with Spring Boot → Structuring Your Code | 부트가 패키지 배치에 **의존한다**는 사실과, 그래서 생기는 제약 |
| Reference → Developing with Spring Boot → Packaging Your Application for Production | 패키징 갈래들의 목차 역할만 하는 짧은 안내 페이지 |
| Specification → The Executable Jar Format | 실행 가능한 jar가 실제로 어떤 모양의 아카이브인지 — 규격 구역 |

`Packaging Your Application for Production`이 **레퍼런스가 아니라 이정표**라는 점이 이 모듈의 성격을 정한다. 컨테이너 이미지·네이티브 이미지 쪽은 B13으로 넘어가 있으므로, B02에서 패키징의 실체는 규격 구역의 `Executable Jar Format` 쪽에서 읽게 된다.

## 목차 지도

### Build Systems

- **Build Systems** — Maven·Gradle을 권장 도구로 놓고, 지원 수준이 도구마다 다르다는 전제를 먼저 깐다
- **Dependency Management** — 부트가 관리하는 의존성 목록(큐레이션)이 무엇이고, 사용자가 버전을 적지 않아도 되는 근거가 어디 있는지. `spring-boot-dependencies` BOM이 여기서 나온다
- **Maven** — Maven 쪽에서 이 관리를 받는 경로. 플러그인 문서·API 레퍼런스로 넘기는 자리
- **Gradle** — 같은 일을 Gradle 쪽에서 받는 경로
- **Ant** — Maven·Gradle이 아닌 경로가 존재한다는 것. `ivy.xml`·`build.xml` 예시와 Spring Boot AntLib 모듈
- **Starters** — 스타터가 "의존성 기술자"라는 정의와, 애플리케이션·프로덕션·기술 세 갈래의 스타터 목록 전체
  - *What is in a name* — 스타터 이름이 규칙을 따른다는 것. 공식 스타터와 서드파티 스타터의 이름 규칙이 갈리는 지점

### Structuring Your Code

- **Structuring Your Code** — 부트가 특정 배치를 **요구하지는 않지만** 따르면 편한 관행이 있다는 전제
- **Using the "default" Package** — 패키지 선언 없는 클래스가 왜 문제가 되는지. `@ComponentScan`·`@ConfigurationPropertiesScan`·`@EntityScan`·`@SpringBootApplication`이 이 문제와 어떻게 얽히는지
- **Locating the Main Application Class** — 메인 클래스를 루트 패키지에 두라는 권고와 그 근거. `@SpringBootApplication`이 암묵적으로 정하는 "탐색 기준 패키지" 개념, 도메인별 하위 패키지(`customer`·`order`)로 그린 전형적 배치도

### Packaging Your Application for Production

- 한 페이지짜리 안내. `Packaging Spring Boot Applications` 구역(Efficient Deployments · AOT Cache · Ahead-of-Time Processing With the JVM · GraalVM Native Images · Checkpoint and Restore With the JVM · Container Images)으로 넘기고, 프로덕션 준비물로 `spring-boot-actuator`를 가리킨다

### The Executable Jar Format (규격 구역)

- **The Executable Jar Format** — `spring-boot-loader` 모듈이 이 형식의 주체라는 것. "빌드 플러그인이 알아서 만들어 주므로 보통은 몰라도 된다"는 위치 규정이 먼저 나온다
- **Nested JARs** — 아카이브 내부 구조. 아래 다섯 소제목으로 쪼개져 있다
  - *The Executable Jar File Structure* — `META-INF/` · 로더 클래스 · `BOOT-INF/classes` · `BOOT-INF/lib` 의 자리
  - *The Executable War File Structure* — `WEB-INF/classes` · `WEB-INF/lib` 에 더해 `WEB-INF/lib-provided/` 가 따로 있는 이유
  - *Index Files* — 아카이브 안에 색인 파일을 두는 방식 일반
  - *Classpath Index* — `classpath.idx`. 어떤 상황에서만 적용되는지가 이 절의 핵심
  - *Layer Index* — `layers.idx`. 컨테이너 이미지 레이어와 이어지는 자리(B13의 선행 지식)
- **Spring Boot's "NestedJarFile" Class** — 중첩된 jar를 읽어 내는 쪽의 구현
- **Launching Executable Jars** — `Main-Class` 와 `Start-Class` 가 매니페스트에서 갈리는 이유, 실제 기동 순서
- **PropertiesLauncher Features** — 기본 런처 말고 설정 가능한 런처가 따로 있다는 것
- **Executable Jar Restrictions** — 이 형식으로 할 수 없는 것들
- **Alternative Single Jar Solutions** — 같은 문제를 푸는 다른 방식(shaded jar 등)과의 대조

## 핵심 용어

| 용어 | 한 줄 |
| --- | --- |
| BOM (Bill of Materials) | 서로 맞물리는 의존성들의 버전 조합을 한 곳에 적어 둔 POM. 부트의 것은 `spring-boot-dependencies` |
| dependency management | 버전 번호를 개별 의존성마다 적지 않고 한 출처에서 결정되게 하는 장치 |
| `spring-boot-starter` | 스타터 중 코어. 자동 설정·로깅·YAML 등 공통 묶음 |
| `spring-boot-starter-classic` | 4.x에 존재하는 코어 스타터의 다른 갈래 — 이름이 무엇을 가르는지는 원문에서 확인할 것 |
| 애플리케이션 스타터 / 프로덕션 스타터 / 기술 스타터 | 문서가 스타터 목록을 나눠 놓은 세 갈래. 기술 스타터는 기본 구현을 갈아 끼우는 용도(`starter-log4j2`·`starter-jetty-runtime` 등) |
| Spring Boot AntLib | Maven·Gradle 밖에서 Ant로 빌드할 때 쓰는 모듈 |
| default package | `package` 선언이 없는 클래스가 놓이는 자리 |
| root package | 메인 애플리케이션 클래스를 두는 최상위 패키지 |
| 탐색 기준 패키지(base "search package") | `@SpringBootApplication`이 선언된 클래스의 패키지. 컴포넌트 스캔·엔티티 탐색의 시작점이 된다 |
| `@ConfigurationPropertiesScan` / `@EntityScan` | 컴포넌트 스캔과 별개로 각각 설정 프로퍼티 클래스·JPA 엔티티를 찾는 표시 |
| `spring-boot-loader` | 중첩 jar를 읽어 실행 가능한 아카이브를 띄우는 모듈 |
| `BOOT-INF/classes` · `BOOT-INF/lib` | 실행 가능한 jar 안에서 애플리케이션 클래스와 의존 라이브러리가 각각 놓이는 자리 |
| `WEB-INF/lib-provided` | war에서 "내장 실행에는 필요하지만 컨테이너 배포에는 넣으면 안 되는" 의존성 자리 |
| `Main-Class` / `Start-Class` | 매니페스트의 두 항목. 전자는 로더, 후자는 실제 애플리케이션 클래스 |
| `classpath.idx` | 클래스패스 적재 순서를 적어 둔 색인 파일 |
| `layers.idx` | 아카이브를 컨테이너 이미지 레이어로 가르기 위한 색인 파일 |
| `NestedJarFile` | jar 안의 jar를 압축 해제 없이 읽기 위한 부트의 클래스 |
| `PropertiesLauncher` | 외부 라이브러리 경로 등을 프로퍼티로 조정할 수 있는 런처 |
| shaded jar / uber jar | 의존 클래스를 모두 한 네임스페이스에 펼쳐 넣는 다른 방식의 단일 jar |
| AOT / Checkpoint and Restore | 패킹 안내 페이지가 가리키는 최적화 갈래들 (본체는 B13) |

## 수업에서 안 다뤘을 만한 지점

이 모듈은 학습 지도에서 **복습**(day02·day08과 대조)으로 표시돼 있다. `Spring/` 구역의 「Spring Boot 프로젝트 생성(분석)」·day02·day07·day08 노트를 읽고 공식 문서와 대조한 결과, 아래가 수업 쪽에 없거나 다른 각도로 지나간 자리다.

- **버전이 맞춰지는 실제 경로.** 수업 노트는 `io.spring.dependency-management` 플러그인이 "버전을 알아서 맞춰 준다"까지 갔다. 공식 문서는 그 위에 `spring-boot-dependencies` **BOM**을 놓고, 플러그인은 그 BOM을 읽는 쪽이라는 층을 먼저 세운다. Maven이 부모 POM 상속으로 같은 BOM에 닿는다는 점과 나란히 놓으면, "플러그인"이 아니라 "큐레이션된 목록"이 주체라는 대조가 생긴다.
- **스타터 목록이 세 갈래로 나뉜다는 사실.** 수업 노트의 스타터 표는 기능별 나열이다. 공식 문서는 **애플리케이션 / 프로덕션 / 기술** 로 갈라 놓았고, 특히 기술 스타터(로깅 구현·서블릿 컨테이너 갈아 끼우기)는 "무엇을 추가한다"가 아니라 "기본값을 교체한다"는 성격이라 앞의 둘과 쓰임이 다르다. 수업에 이 축이 없다.
- **Ant 갈래.** 수업에는 그레이들만, 「더 나아가」 절에 메이븐과의 대조표가 있다. 공식 문서는 세 번째 갈래로 Ant + Ivy와 AntLib 모듈을 둔다 — 쓸 일은 드물어도 "부트가 특정 빌드 도구에 묶여 있지 않다"는 주장의 근거로 존재하는 절이다.
- **패키지 배치가 '관례'가 아니라 '동작에 영향을 준다'는 층위.** 수업의 패키지 이야기는 계층 축 대 도메인 축(day07 1-1·3-1), 소문자 관례(day02 3-5)처럼 **사람이 읽기 좋은 배치** 쪽이었다. 공식 문서의 `Structuring Your Code`는 다른 걸 말한다 — 메인 클래스의 위치가 컴포넌트 스캔·`@EntityScan`·`@ConfigurationPropertiesScan`의 **탐색 범위를 결정한다**. day02 1-17의 `mainClass` 이야기(어느 진입점을 띄우느냐에 따라 등록되는 컨트롤러가 달라진다)가 이 원리의 결과였는데, 수업 쪽에서는 현상으로만 만났고 규칙으로 정리되지는 않았다.
- **default 패키지 문제.** 수업 노트에 전혀 없다. 패키지 선언을 빼면 무엇이 깨지는지, 그리고 그것이 위의 탐색 범위 규칙과 어떻게 이어지는지가 문서에 별도 절로 있다.
- **실행 가능한 jar의 내부 구조 전체.** 수업 노트는 "의존 라이브러리와 톰캣까지 들어 있다"(프로젝트 생성 2-8)로 결과만 말한다. 공식 규격은 `BOOT-INF/classes` · `BOOT-INF/lib` 배치, 매니페스트의 `Main-Class`/`Start-Class` 이원 구조, 중첩 jar를 읽는 로더까지를 형식으로 규정한다. day08에서 프로젝트를 통째로 옮겨 담아 본 경험과 이어 붙일 자리다.
- **war 쪽과 `lib-provided`.** 수업은 jar 단일 경로만 다뤘다. 규격에는 war 레이아웃이 나란히 있고, "내장 실행에는 필요한데 컨테이너 배포에는 빠져야 하는" 의존성 자리가 따로 있다 — 트랙 S(S01 WAR·톰캣 배포)와 정면으로 이어지는 지점이다.
- **색인 파일 둘.** `classpath.idx`·`layers.idx`는 수업에 없다. 특히 레이어 색인은 B13(컨테이너 이미지)에서 쓰이는 것이므로, 여기서는 "이런 파일이 아카이브 안에 있다"까지만 봐 두면 되는 자리다.
- **의존성 앞말(`implementation`·`runtimeOnly`·`compileOnly`·`annotationProcessor`).** 반대로 이쪽은 **수업에만 있고 공식 문서에는 없다**(day08 1-2). Gradle 쪽 개념이라 부트 레퍼런스가 아니라 Gradle 플러그인 문서로 넘어가 있다 — 문서가 어디서 끊기는지를 확인하는 자리.

## 학습 세션에서 확인할 것

- [ ] `build.gradle`에 버전을 안 적어도 되는 일은 누가 하는가 — 플러그인인가 BOM인가, 그리고 Maven의 부모 POM 상속은 이 중 무엇에 해당하는가
- [ ] 기술 스타터(예: 로깅 구현이나 서블릿 컨테이너를 바꾸는 것)는 애플리케이션 스타터를 **추가**하는 것과 무엇이 다른가. 왜 그냥 더하면 안 되는가
- [ ] 메인 클래스를 하위 패키지로 한 칸 내리면 무엇이 먼저 안 뜨는가. day02에서 `mainClass`를 바꿀 때마다 등록되는 컨트롤러가 달라졌던 것과 같은 원리인가
- [ ] 계층 축이냐 도메인 축이냐(day07에서 따진 것)는 부트의 동작과 상관이 있는가 없는가 — 공식 문서가 정말로 요구하는 것은 무엇 하나뿐인가
- [ ] 매니페스트에 `Main-Class`와 `Start-Class`가 둘 다 있어야 하는 이유는 무엇인가. 하나로 합칠 수 없는가
- [ ] `BOOT-INF/lib` 안에 jar를 그대로 넣는 방식과, 모든 클래스를 펼쳐 담는 shaded jar는 각각 무엇을 포기하는가

## 원문 링크

- https://docs.spring.io/spring-boot/reference/using/build-systems.html
- https://docs.spring.io/spring-boot/reference/using/structuring-your-code.html
- https://docs.spring.io/spring-boot/reference/using/packaging-for-production.html
- https://docs.spring.io/spring-boot/specification/executable-jar/index.html
- https://docs.spring.io/spring-boot/specification/executable-jar/nested-jars.html
- https://docs.spring.io/spring-boot/reference/using/index.html
