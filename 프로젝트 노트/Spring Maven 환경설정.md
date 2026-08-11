---
출처: Claude 대화
작성일: 2026-08-11
tags: [프로젝트노트, Spring, Maven]
---

# Spring Maven 환경설정

> 허브: [[프로젝트 노트 MOC]]

## 1. 배운 내용

### 1-1. 개발 환경 확인

새 미니프로젝트(`KDT_miniP/back-end`)를 시작하기 전에 JDK와 Maven이 이미 설치돼 있는지부터 확인했다.

```
java -version   → 21.0.10 (LTS)
mvn -version     → Apache Maven 3.9.12
```

둘 다 이미 잡혀 있어서 별도 설치 없이 바로 프로젝트 생성 단계로 넘어갈 수 있었다.

### 1-2. Spring Initializr로 프로젝트 생성

https://start.spring.io 에서 아래 설정으로 프로젝트를 생성했다.

| 항목 | 값 |
| --- | --- |
| Project | Maven |
| Language | Java |
| Java | 21 |
| Group | com.example |
| Artifact | back-end |
| Packaging | Jar |
| Dependencies | Spring Web, Spring Data JPA, MySQL Driver, Lombok |

생성된 zip을 풀어서 `back-end` 폴더에 그대로 넣는 방식으로 진행했다.

### 1-3. pom.xml 구조

- `<parent>` : `spring-boot-starter-parent`를 상속받아 각 라이브러리 버전을 일일이 안 적어도 Spring Boot가 검증된 조합을 맞춰준다. 이번에 잡힌 버전은 4.1.0.
- 프로젝트 좌표(`groupId`/`artifactId`/`version`) : groupId는 패키지 최상위 경로, artifactId는 프로젝트 이름, version의 `SNAPSHOT`은 개발 중이라는 표시.
- `<dependencies>` :
  - `spring-boot-starter-data-jpa` — DB를 객체처럼 다루는 JPA 기능
  - `spring-boot-starter-webmvc` — 웹/REST 서버 기능(내장 톰캣 포함). Spring Boot 4부터 기존 `spring-boot-starter-web`이 `-webmvc`로 이름이 바뀌었다.
  - `mysql-connector-j` (`scope: runtime`) — MySQL 연결 드라이버, 컴파일 시점에는 필요 없고 실행할 때만 필요해서 runtime 스코프
  - `lombok` (`optional: true`) — getter/setter 등을 어노테이션으로 자동 생성
  - `-test`로 끝나는 의존성들은 테스트 코드에서만 쓰이는 것들 (`scope: test`)
- `<build><plugins>` :
  - `spring-boot-maven-plugin` — 실행 가능한 jar로 패키징하거나 `spring-boot:run`으로 바로 실행할 때 필요
  - `maven-compiler-plugin` — Lombok 어노테이션 프로세서를 컴파일 시점에 처리하도록 지정. 이 설정이 없으면 Lombok이 동작하지 않는다.

## 2. 추가로 알면 좋은 활용법

### 2-1. 실행 확인

프로젝트 루트에서 아래 명령으로 서버가 뜨는지 확인할 수 있다.

```
.\mvnw spring-boot:run
```

`http://localhost:8080` 접속해서 정상 기동 여부를 볼 수 있다.

## 3. 더 나아가 알면 좋은 것

### 3-1. 다음에 볼 키워드

- Spring Boot 4의 starter 이름 변경 목록 (webmvc 외에 또 뭐가 바뀌었는지)
- `application.properties`에서 MySQL 연결 설정하는 법
- Lombok 어노테이션 종류 (`@Getter`, `@Setter`, `@Builder` 등)

## 관련 노트

[[프로젝트 노트 MOC]]
