---
출처: 자동수집(Claude)
작성일: 2026-09-28
성격: 예습자료
tags: [학습, spring]
---

# Spring 예습 - B13 컨테이너 이미지와 배포

> 예습자료 — 자동 생성, 사용자 미검증. 결론이 아니라 **읽을 범위의 지도**다.
> 기준 버전: Spring Boot 4.1.1

## 이 모듈이 다루는 범위

B13은 문서에서 **한 챕터에 모여 있지 않다.** 두 곳에 나뉘어 있고, 그 분할 자체가 이 모듈의 성격을 말한다.

| 갈래 | 문서 위치 | 문서가 서 있는 자리 |
| --- | --- | --- |
| **패키징** | Reference → Packaging Spring Boot Applications | 만들어진 jar를 **어떤 모양으로 바꿔 내보낼 것인가** — 풀어 놓기, 캐시, 네이티브 이미지, 컨테이너 이미지 |
| **배포** | How-to → Deploying Spring Boot Applications | 그 산출물을 **어디에 얹을 것인가** — WAR·전통적 서버, 클라우드 플랫폼, OS 서비스 등록 |

앞 모듈들과의 관계가 뒤집힌다. B01~B12는 "애플리케이션 안에서 무엇이 어떻게 조립되는가"였고, B12(Actuator)가 처음으로 "밖에서 들여다보는 층"을 얹었다. B13은 그보다 한 걸음 더 밖 — **애플리케이션이 아니라 산출물(artifact)과 그것이 놓이는 환경**을 다룬다. 실행 가능한 jar의 구조(B02), 외부 설정이 환경변수로 들어오는 경로(B04), 프로파일(B05), 그리고 쿠버네티스 프로브가 읽는 `health`(B12)가 여기서 다시 쓰이는 것으로 보인다.

문서가 이 모듈에서 반복해서 꺼내는 물음은 **"jar 하나를 통째로 다루지 않고 쪼개면 무엇이 좋아지는가"** 로 읽힌다. 레이어·추출·캐시·버일드팩이 전부 같은 물음의 변주로 배치돼 있다.

- 원문(패키징 챕터): https://docs.spring.io/spring-boot/reference/packaging/index.html
- 원문(배포 How-to): https://docs.spring.io/spring-boot/how-to/deployment/index.html

## 목차 지도

### 1. Efficient Deployments — 풀어 놓기

- **Efficient Deployments** — 실행 가능한 jar를 그대로 돌리지 않고 **미리 풀어서(extract) 돌리는** 선택지를 설명하는 페이지. `java -Djarmode=tools -jar my-app.jar extract`로 `lib/` 디렉터리와 얇아진 jar를 만든다는 절차, 그리고 그 배치가 AOT 캐시·CDS와 맞물린다는 언급이 여기 있다

### 2. AOT Cache / AOT Processing — 미리 해 두기

- **AOT Cache** — Java 25+의 AOT 캐시로 기동 시간·메모리를 줄이는 자리. **훈련 실행(training run)** 이라는 개념 — 애플리케이션을 한 번 띄웠다가 컨텍스트 새로고침 시점에 끝내(`-Dspring.context.exit=onRefresh`) 캐시 파일을 뽑고, 이후 실행에서 그 파일을 물린다
  - **CDS** — Java 25 미만에서 같은 일을 하던 앞선 기술(`-XX:ArchiveClassesAtExit` / `-XX:SharedArchiveFile`). 문서는 25+에서는 AOT 캐시를 권한다고 말한다
- **Ahead-of-Time Processing With the JVM** — 위의 JVM 레벨 캐시와 **다른 층**인, 스프링 자체의 빌드 시점 AOT 처리

### 3. GraalVM Native Images — 아예 다른 산출물

- **Introducing GraalVM Native Images** — jar가 아니라 **네이티브 실행 파일**을 만드는 갈래의 소개
- **Advanced Native Images Topics** — 그 갈래의 심화 설정
- (How-to 쪽에 `Developing Your First GraalVM Native Application`·`Testing GraalVM Native Images`가 따로 있다)

### 4. Checkpoint and Restore — 떠 있는 상태를 저장하기

- **Checkpoint and Restore With the JVM** — CRaC(Coordinated Restore at Checkpoint). 리눅스 CRIU에 기반해 **워밍업이 끝난 JVM의 메모리 상태를 디스크에 떠 두었다가 그 지점에서 되살리는** 방식. 부트가 소켓·파일·스레드 풀 같은 자원의 생명주기를 어느 범위까지 대신 관리해 주는지가 이 페이지의 내용

### 5. Container Images — 컨테이너 이미지 (이 모듈의 중심)

- **Container Images** — 도커 호환 이미지를 만드는 두 갈래(Dockerfile / 버일드팩)를 가르는 입구 페이지
- **Efficient Container Images** — **왜 uber jar를 그대로 넣으면 안 되는가**를 세우는 자리. 의존성과 애플리케이션 코드가 한 레이어에 섞이면 캐시가 듣지 않는다는 문제 제기
  - **Layering Docker Images** — jar 안에 들어가는 `layers.idx`(YAML) 레이어 색인. 기본 레이어 네 개가 **바뀌는 빈도 순서**로 배치된다: `dependencies` → `spring-boot-loader` → `snapshot-dependencies` → `application`. WAR도 같은 방식을 지원한다는 언급, 그리고 레이어 구성 변경은 Maven·Gradle 플러그인 문서로 넘긴다
- **Dockerfiles** — 직접 Dockerfile을 쓰는 쪽. `spring-boot-jarmode-tools`와 `java -Djarmode=tools -jar my-app.jar`(하위 명령 `extract`·`list-layers`·`help`), 그리고 빌더 스테이지에서 레이어를 뽑아 런타임 스테이지로 `COPY`하는 **멀티 스테이지 빌드** 예시
  - **AOT Cache** / **CDS** 절 — 위 3절의 캐시를 Dockerfile 안에서 만들어 이미지에 굽는 방법(빌드 중 훈련 실행 → `ENTRYPOINT`에서 캐시 물리기)
- **Cloud Native Buildpacks** — Dockerfile을 쓰지 않는 쪽. **CNB(Cloud Native Buildpacks)** 규격과 부트가 내장한 플러그인 명령(`spring-boot:build-image` / `bootBuildImage`), **Paketo Spring Boot 버일드팩**이 위의 `layers.idx`를 그대로 읽는다는 연결. 버일드팩이 캐싱을 위해 리소스의 "최종 수정 시각" 메타데이터를 손댄다는 주의와 `spring.web.resources.cache.use-last-modified`

### 6. Deploying — 어디에 얹는가 (How-to)

- **Traditional Deployment** — jar가 아닌 **WAR로 내보내는** 갈래
  - **Create a Deployable War File** — `SpringBootServletInitializer` 상속과 `configure()` 재정의, 패키징을 `war`로 바꾸기, 내장 서블릿 컨테이너를 `provided` 범위로 내리기. WebFlux는 지원 대상이 아니라는 단서
  - **Convert an Existing Application to Spring Boot** — 기존 스프링 애플리케이션을 옮겨 오는 절차. `web.xml`의 서블릿·필터 등록을 `ServletRegistrationBean`·`FilterRegistrationBean` 빈으로 옮기는 대응표 성격
  - **Deploy to WebLogic** — 특정 WAS 하나에 대한 예외 처리
- **Deploying to the Cloud** — 플랫폼별 절. Cloud Foundry(`cf push`, `$VCAP_SERVICES`), **Kubernetes**, Heroku(`Procfile`), AWS(ECS·Elastic Beanstalk), Azure, Google Cloud, OpenShift
  - 쿠버네티스 절이 가장 길다 — 환경변수(`*_SERVICE_HOST`)로 플랫폼을 **자동 감지**하는 것, `preStop` 훅과 우아한 종료(graceful shutdown), 종료 유예 시간과 `spring.lifecycle.timeout-per-shutdown-phase`의 관계, Actuator 프로브를 HTTP 프로브로 쓰는 연결
  - **Forwarded Headers** 주의 — 클라우드 플랫폼이 이를 기본으로 켠다는 것과 `server.forward-headers-strategy`
- **Installing Spring Boot Applications** — OS 서비스로 등록하는 쪽. systemd `.service` 파일(`ExecStart`·`WorkingDirectory`·`SuccessExitStatus=143`), `systemctl enable`, 그리고 윈도우는 `winsw`

## 핵심 용어

| 용어 | 한 줄 |
| --- | --- |
| **uber jar / fat jar** | 의존성까지 전부 한 덩어리로 넣은 실행 가능한 jar (B02에서 본 그 구조) |
| **layers.idx** | jar 안에 들어가는 레이어 색인 YAML. 어떤 파일이 어느 레이어에 속하는지, 어떤 순서로 쌓을지를 적는다 |
| **레이어(layer)** | 도커 이미지를 이루는 변경 단위. 바뀌지 않은 레이어는 다시 만들지 않고 캐시에서 쓴다 |
| **jarmode** | jar를 애플리케이션으로 실행하는 대신 다른 동작(레이어 추출 등)을 시키는 실행 모드. `-Djarmode=tools` |
| **extract** | jar를 디렉터리 형태로 풀어 놓는 jarmode 하위 명령 |
| **멀티 스테이지 빌드** | Dockerfile에서 `FROM`을 여러 번 써서 준비용 컨테이너와 최종 실행 컨테이너를 나누는 방식 |
| **AOT 캐시** | Java 25+ JVM 기능. 미리 만든 캐시 파일을 물려 기동을 줄인다 |
| **훈련 실행(training run)** | 캐시 파일을 뽑기 위해 애플리케이션을 한 번 띄웠다 끝내는 빌드 단계 |
| **CDS** | Class Data Sharing. AOT 캐시 이전 세대의 같은 목적 기술 |
| **CRaC** | Coordinated Restore at Checkpoint. 떠 있는 JVM 상태를 저장했다가 되살리는 방식 |
| **CNB (Cloud Native Buildpacks)** | Dockerfile 없이 소스·아티팩트에서 컨테이너 이미지를 만드는 표준 |
| **빌더(builder) / 버일드팩(buildpack)** | CNB에서 이미지를 조립하는 쪽(빌더)과 언어·런타임별 규칙 뭉치(버일드팩) |
| **Paketo** | 부트가 기본으로 쓰는 버일드팩 구현 |
| **SpringBootServletInitializer** | WAR로 배포할 때 외부 서블릿 컨테이너가 애플리케이션을 띄우도록 잇는 진입점 |
| **provided 범위** | 빌드에는 필요하지만 산출물에 넣지 않는 의존성 범위 (WAR에서 내장 톰캣을 뺄 때) |
| **우아한 종료(graceful shutdown)** | 종료 신호를 받고도 처리 중인 요청을 끝낸 뒤 내려가는 것 |
| **preStop 훅** | 쿠버네티스가 컨테이너에 종료 신호를 보내기 **전에** 실행하는 단계 |

## 처음 보는 개념

학습 지도에서 B13은 **신규**로 표시돼 있다. 수업(`Spring/` 구역 day01~day08)은 애플리케이션을 만들어 IDE에서 띄우는 데까지였고, 산출물을 밖으로 내보내는 이야기는 없었다. 그래서 이 모듈은 대조할 day 노트가 없다. 대신 **처음 보는 축**이 세 개 있다.

- **"빌드 산출물"과 "실행 환경"이 분리된 축.** 지금까지는 `main()`을 눌러 실행하는 것이 곧 실행이었다. 여기서는 jar → 이미지 → 컨테이너 → 플랫폼으로 단계가 늘고, 각 단계에 별도의 설정 지점이 생긴다
- **"바뀌는 빈도"가 설계 기준이 되는 축.** 레이어 네 개의 순서가 기능이 아니라 **변경 빈도**로 정해져 있다. 코드 구조를 나누는 기준이 패키지·역할이 아닌 경우를 처음 본다
- **기동 시간을 비용으로 취급하는 축.** AOT 캐시·CDS·CRaC·네이티브 이미지가 전부 같은 문제(기동이 느리다)에 대한 다른 답으로 놓여 있다. 왜 이것이 문제가 되는 환경이 따로 있는지가 배경으로 깔려 있는 듯하다

또 하나, 이 모듈은 **부트 문서가 남에게 넘기는 지점이 유난히 많다.** 레이어 구성은 Maven·Gradle 플러그인 문서로, CRaC 상세는 스프링 프레임워크 문서로, 버일드팩 내부는 Paketo로, 플랫폼별 절차는 각 클라우드 문서로 보낸다. "부트가 책임지는 경계가 어디까지인가"를 읽는 자리이기도 해 보인다.

## 학습 세션에서 확인할 것

- [ ] 레이어를 나누면 정확히 무엇이 절약되는가 — 이미지 크기인가, 빌드 시간인가, 전송량인가. 네 레이어의 **순서**가 바뀌면 왜 효과가 사라지는가
- [ ] `extract`해서 돌리는 것과 jar 그대로 돌리는 것의 차이는 언제 생기고 언제 사라지는가 — 기동 시점인가 실행 내내인가
- [ ] Dockerfile과 버일드팩 중 무엇을 고르는 기준은 무엇인가 — 버일드팩이 대신 정해 주는 것(베이스 이미지·JRE·기동 명령)을 넘기는 대가는 무엇인가
- [ ] 훈련 실행이 **빌드 시점에** 애플리케이션을 한 번 띄운다는 것은 무슨 뜻인가 — 그때 DB·외부 API에 실제로 붙는가, `spring.context.exit=onRefresh`가 그 경계를 어디에 긋는가
- [ ] 쿠버네티스에서 `preStop` 지연과 우아한 종료 타임아웃이 **둘 다** 필요한 이유는 무엇인가 — 각각 어떤 요청 손실을 막는가
- [ ] 지금도 WAR 배포를 하는 이유는 무엇이며, 내장 컨테이너를 `provided`로 내리는 것이 실제로 무엇을 피하는가 (트랙 S01과 짝이 되는 지점)
- [ ] AOT 캐시 · CDS · CRaC · 네이티브 이미지는 서로 **대안인가 조합 가능한가** — 각각이 포기하는 것은 무엇인가

## 원문 링크

- https://docs.spring.io/spring-boot/reference/packaging/index.html
- https://docs.spring.io/spring-boot/reference/packaging/efficient.html
- https://docs.spring.io/spring-boot/reference/packaging/aot-cache.html
- https://docs.spring.io/spring-boot/reference/packaging/native-image/index.html
- https://docs.spring.io/spring-boot/reference/packaging/checkpoint-restore.html
- https://docs.spring.io/spring-boot/reference/packaging/container-images/index.html
- https://docs.spring.io/spring-boot/reference/packaging/container-images/efficient-images.html
- https://docs.spring.io/spring-boot/reference/packaging/container-images/dockerfiles.html
- https://docs.spring.io/spring-boot/reference/packaging/container-images/cloud-native-buildpacks.html
- https://docs.spring.io/spring-boot/how-to/deployment/index.html
- https://docs.spring.io/spring-boot/how-to/deployment/traditional-deployment.html
- https://docs.spring.io/spring-boot/how-to/deployment/cloud.html
- https://docs.spring.io/spring-boot/how-to/deployment/installing.html
