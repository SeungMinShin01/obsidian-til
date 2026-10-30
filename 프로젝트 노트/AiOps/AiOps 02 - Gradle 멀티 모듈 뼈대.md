---
출처: Claude 대화
작성일: 2026-10-30
tags: [프로젝트, spring]
---

# AiOps - Gradle 멀티 모듈 뼈대

> 허브: [[AiOps 프로젝트 MOC]]

## 1. 배운 내용

### 1-1. 레포 하나에 프로젝트 네 개

1차 프로젝트는 "프로젝트 1개 = `build.gradle` 1개"였다. 여기는 **레포 안에 모듈 4개**가 있고, 루트 `build.gradle`이 공통 설정, 모듈마다 자기 `build.gradle`이 있다. 루트의 `settings.gradle`이 "이 넷이 모듈이다"라고 알려주는 파일.

```
aiops/
├─ settings.gradle          모듈 목록
├─ build.gradle             공통 설정 (Java 17, UTF-8, JUnit)
├─ gradle.properties        버전 변수
├─ protocol/build.gradle    의존성 없음
├─ starter/build.gradle     compileOnly
├─ server/build.gradle      Boot 플러그인
└─ sample-app/build.gradle  Boot 플러그인, starter 의존
```

의존 방향: `starter → protocol`, `server → protocol`, `sample-app → starter`. protocol은 아무것도 의존하지 않는다. 이 방향 덕에 Starter와 서버가 주고받는 형식을 한쪽만 바꾸면 컴파일 에러로 바로 드러난다.

### 1-2. settings.gradle과 gradle.properties

```groovy
// settings.gradle
rootProject.name = 'aiops'

include 'protocol'
include 'starter'
include 'server'
include 'sample-app'
```

```properties
# gradle.properties
springBootVersion=4.1.1
dependencyManagementVersion=1.1.7
org.gradle.jvmargs=-Xmx1g -Dfile.encoding=UTF-8
```

버전을 `gradle.properties` 한 곳에 두는 이유는 모듈 4개가 전부 같은 Boot 버전을 참조해야 해서다. 모듈마다 적으면 언젠가 하나만 올리는 실수가 난다.

### 1-3. 루트 build.gradle — 공통 설정

```groovy
plugins {
    id 'java'
    id 'org.springframework.boot' version "${springBootVersion}" apply false
    id 'io.spring.dependency-management' version "${dependencyManagementVersion}" apply false
}

allprojects {
    group = 'com.github.seungminshin01.aiops'   // JitPack 규칙: com.github.<깃허브아이디>
    version = '0.1.0-SNAPSHOT'
    repositories { mavenCentral() }
}

subprojects {
    apply plugin: 'java'

    java {
        toolchain { languageVersion = JavaLanguageVersion.of(17) }
    }
    tasks.withType(JavaCompile).configureEach {
        options.encoding = 'UTF-8'
        options.release = 17
    }
    tasks.named('test') { useJUnitPlatform() }
}
```

`apply false`가 핵심이다. Boot 플러그인을 루트에서 **선언만** 하고 적용은 안 한다. 적용하면 모든 모듈이 실행 가능한 jar(bootJar)를 만들려 하는데, protocol·starter는 라이브러리라 일반 jar여야 한다. 그래서 server·sample-app에서만 `apply plugin: 'org.springframework.boot'`를 한다.

### 1-4. JDK는 21인데 타깃은 17

내 PC엔 JDK 21만 있다. 그래도 `toolchain 17` + `options.release = 17`로 **컴파일 타깃을 17로 고정**했다. Starter를 받아 쓰는 다른 조가 17일 수 있기 때문 — 라이브러리는 낮은 버전으로 빌드해야 양쪽에서 돈다. Gradle이 toolchain 17을 자동으로 받아 왔고(처음 빌드가 오래 걸린 이유), 팀원도 17이든 21이든 상관없다.

### 1-5. starter는 compileOnly

```groovy
// starter/build.gradle
apply plugin: 'io.spring.dependency-management'

dependencyManagement {
    imports { mavenBom "org.springframework.boot:spring-boot-dependencies:${springBootVersion}" }
}

dependencies {
    implementation project(':protocol')

    // 팀 앱이 이미 갖고 있는 것만 compileOnly. Starter는 새 의존성을 가져오지 않는다 (규칙 3)
    compileOnly 'org.springframework.boot:spring-boot'
    compileOnly 'org.springframework:spring-context'
    compileOnly 'ch.qos.logback:logback-classic'
    compileOnly 'com.fasterxml.jackson.core:jackson-databind'

    testImplementation 'org.springframework.boot:spring-boot'
    testImplementation 'org.springframework:spring-context'
    testImplementation 'ch.qos.logback:logback-classic'
    testImplementation 'com.fasterxml.jackson.core:jackson-databind'
    testImplementation 'org.junit.jupiter:junit-jupiter'
    testRuntimeOnly 'org.junit.platform:junit-platform-launcher'
}
```

`compileOnly`는 "컴파일할 때만 쓰고, 이 jar를 받는 쪽에는 같이 안 딸려감"이다. Starter는 팀 앱에 들어가는 라이브러리라, 팀 앱이 이미 가진 Spring·Logback·Jackson을 **빌려 쓰기만** 해야 한다. `implementation`으로 넣으면 팀 앱에 Spring이 한 벌 더 딸려 들어가 버전 충돌이 난다. 북극성("팀 앱을 절대 느리게 하거나 죽이지 않는다")의 빌드 수준 표현이다.

테스트에서는 실제로 실행해야 하니 `testImplementation`으로 같은 것들을 다시 넣는다.

### 1-6. server·sample-app — Boot 4 스타터 이름

```groovy
// server/build.gradle (0단계 시점. 1단계에서 JPA·Flyway 추가)
apply plugin: 'org.springframework.boot'
apply plugin: 'io.spring.dependency-management'

dependencies {
    implementation project(':protocol')
    implementation 'org.springframework.boot:spring-boot-starter-webmvc'

    testImplementation 'org.springframework.boot:spring-boot-starter-webmvc-test'
    testRuntimeOnly 'org.junit.platform:junit-platform-launcher'
}
```

`spring-boot-starter-web`이 아니라 **`-webmvc`** 다. Boot 4에서 스타터 이름이 바뀌었다(`starter-web → starter-webmvc`, `flyway-core → starter-flyway`, 테스트 스타터가 `*-test`로 분리). 설계 문서에 3.x 이름으로 적어 둔 게 전부 틀리게 된 지점.

## 2. 추가로 알면 좋은 활용법

### 2-1. Boot 3.x → 4.1.1로 바꾼 이유 (D-004 갱신, D-084)

설계 문서엔 "1차 프로젝트와 같은 3.x"라고 적었는데, 막상 1차 프로젝트 `build.gradle`을 열어 보니 **4.1.1**이었다. 10단계에서 1차 프로젝트에 Starter를 붙여 보는(도그푸딩) 계획이라, 서버와 sample-app은 4.1.1로 맞췄다.

Starter는 다른 조가 3.x일 수도 있으니 **3.x·4.x에 공통인 API만** 쓴다 — `ApplicationListener`, `Environment`, Logback `UnsynchronizedAppenderBase`, `java.net.http`. 5단계 안전성 테스트에 "3.x 샘플에서도 기동" 한 줄을 넣기로 했다.

### 2-2. bootJar가 mainClass를 못 찾는 에러

첫 `./gradlew build`가 여기서 죽었다.

```
> Task :sample-app:bootJar FAILED
Main class name has not been configured and it could not be resolved from classpath
```

컴파일까지는 다 통과했고(toolchain도 됐다는 뜻), 마지막에 실행 가능 jar를 묶으려는데 `main` 메서드가 있는 클래스가 없어서 멈춘 것. server·sample-app에 최소 Application 클래스를 넣어 해결.

```java
package dev.aiops.sample;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

@SpringBootApplication
public class SampleApplication {
    public static void main(String[] args) {
        SpringApplication.run(SampleApplication.class, args);
    }
}
```

sample-app은 C 담당이지만 이 3줄은 어느 Spring 앱이나 똑같은 뼈대라 0단계에 넣었다. C는 여기에 에러 내는 컨트롤러만 추가하면 된다.

### 2-3. 소스 폴더가 비어 있으면 Gradle이 모듈을 건너뛴다

`mkdir -p protocol/src/main/java/dev/aiops/protocol` 식으로 빈 패키지 폴더를 먼저 만들어 둬야 빌드가 네 모듈을 전부 인식한다.

## 3. 더 나아가 알면 좋은 것

### 3-1. sample-app이 왜 필요한가

Starter는 라이브러리라 혼자 실행이 안 된다. 어딘가 Spring 앱에 붙여야 동작을 볼 수 있는데, 다른 조 프로젝트를 매번 빌리기는 어려우니 레포 안에 가짜 팀 앱을 둔다. 마일스톤 1(4단계) `/boom/npe` → 서버에 행 생성, 5단계 안전성 테스트(서버 꺼도 앱 정상, DB 연결 실패 시 STARTUP 전송), 18단계 통합 시나리오가 전부 이 앱으로 돈다. "우리 Starter의 첫 고객이자 테스트 베드."

### 3-2. 다음에 볼 키워드

- `maven-publish` 플러그인 + `jitpack.yml` — 10단계에서 protocol·starter를 JitPack으로 내보낼 때
- Gradle 9의 deprecation 경고("incompatible with Gradle 10") — 지금은 플러그인 쪽 경고라 무시. Boot 플러그인이 따라오면 사라진다

## 관련 노트

[[AiOps 01 - 레포와 브랜치 전략]] · [[AiOps 03 - protocol 데이터 형식]]
