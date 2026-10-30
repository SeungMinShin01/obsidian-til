---
출처: Claude 대화
작성일: 2026-10-30
tags: [프로젝트]
---

# AiOps - CI와 PR 템플릿

> 허브: [[AiOps 프로젝트 MOC]]

## 1. 배운 내용

### 1-1. ci.yml

```yaml
# .github/workflows/ci.yml
name: build

on:
  pull_request:
    branches: [develop, main]
  push:
    branches: [develop, main]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-java@v4
        with:
          distribution: temurin
          java-version: '21'

      - uses: gradle/actions/setup-gradle@v4

      - name: Build and test
        run: ./gradlew build --no-daemon

      - name: Upload test reports
        if: failure()
        uses: actions/upload-artifact@v4
        with:
          name: test-reports
          path: '**/build/reports/tests/'
```

- `on`: develop·main으로 가는 **PR**과 그 두 브랜치에 **push**될 때만 돈다. 브랜치만 푸시하면 안 돈다 — 처음에 Actions 탭이 비어 있어서 "안 되나?" 했는데 PR을 열자 바로 돌았다. feature 브랜치마다 돌리면 무료 분량을 금방 쓴다.
- JDK 21로 돌리지만 컴파일 타깃은 Gradle 설정의 17이다.
- `gradle/actions/setup-gradle`이 의존성 캐시를 해 줘서 두 번째부터는 1분 안에 끝난다.
- 실패하면 테스트 리포트 HTML을 artifact로 올려서 PR 화면에서 내려받아 볼 수 있다.

### 1-2. job 이름이 곧 status check 이름이다

`jobs.build`라서 GitHub가 이 체크를 `build / build (pull_request)`로 표시한다. 보호 규칙의 "Require status checks to pass"에 추가할 이름도 `build`. 이 이름은 **CI가 한 번 돌고 나서야** 보호 규칙 검색창에 뜬다 — 그래서 순서가 "ci.yml 머지 → 첫 PR CI 통과 → 보호 규칙에 build 추가"였다.

### 1-3. PR 템플릿 다섯 칸

```markdown
<!-- docs/pull_request_template.md -->
## 작업 단위
<!-- Jira 하위 작업 키와 제목. 예: AI-36 버퍼 실구현 -->

## 한 것
-

## 테스트
<!-- 추가·변경한 테스트 클래스와 확인한 경우 -->
-

## 설계와 다른 점
<!-- 없으면 "없음". 있으면: 명세에는 X인데 Y로 했다. 이유. (설계자 확인 전 머지 금지) -->
없음

## 확인 (완료 기준)
<!-- Jira 하위 작업의 "확인" 칸을 그대로 옮겨서 체크 -->
- [ ]
```

"설계와 다른 점" 칸이 이 템플릿의 존재 이유다. 설계 규칙 3("설계와 다르게 해야 하면 코드 짜기 전에 멈추고 적어라")이 실제로 기록되는 자리. 이 칸이 "없음"이 아니면 셀프 머지하지 말고 내 답을 기다린다는 약속이다.

파일을 `.github/`이 아니라 `docs/`에 뒀는데, GitHub는 `.github/`·루트·`docs/` 세 곳을 다 인식한다.

### 1-4. 첫 PR 본문 (예시)

```markdown
## 작업 단위
AI-5 레포·Gradle·CI·protocol 만들기 (0단계)

## 한 것
- Gradle 멀티 모듈 뼈대: protocol / starter / server / sample-app
- protocol 모듈: record 11개
- CI 워크플로, PR 템플릿, .gitignore, 문서

## 테스트
- ./gradlew build 로컬 통과
- protocol 모듈에 Spring·Jackson·Logback import 없음 확인

## 설계와 다른 점
- Spring Boot 3.x → 4.1.1 (1차 프로젝트가 4.1.1, D-084)
- Starter 인터페이스를 설계자 선행 커밋 대신 C가 전부 작성 (D-083)
- ErrorEvent.time은 Instant가 아닌 long

## 확인 (완료 기준)
- [x] ./gradlew build 통과
- [x] PR에서 CI build 초록
- [x] protocol에 Spring import 없음
```

## 2. 추가로 알면 좋은 활용법

### 2-1. 원자적 커밋 — 파일 하나에 커밋 하나

0단계를 22개 커밋으로 나눴다. 처음엔 "Gradle 뼈대"를 한 덩어리로 커밋했다가, 이후부터 파일 단위로 쪼갰다.

```
chore(infra): .gitignore에 Claude 출력 폴더 추가 [AI-5]
ci(infra): PR·push 시 Gradle 빌드·테스트 워크플로 [AI-5]
docs(infra): PR 템플릿 (작업 단위·테스트·설계와 다른 점·확인) [AI-5]
docs(docs): CLAUDE.md AI 작업 규칙 (북극성, 고정 규칙 13개) [AI-5]
docs(docs): README 레포 구조·개발 환경·작업 흐름 [AI-5]
docs(docs): v0.1 설계 문서 (부품 명세, 결정 기록) [AI-5]
```

메시지 규칙 `타입(범위): 요약 [이슈키]`. 타입은 feat/fix/refactor/test/docs/chore/build/ci, 범위는 protocol/starter/server/sample/console/infra/docs. 요약은 한국어, 마침표 없음.

### 2-2. .gitignore

```
# Gradle
.gradle/
build/
!gradle/wrapper/gradle-wrapper.jar

# IDE
.idea/
*.iml
.vscode/

# 비밀값
.env
*.env
infra/prod/.env

# 로그
*.log

# Claude
.claude/
claude-output/
```

`!gradle/wrapper/gradle-wrapper.jar`가 중요하다. `build/`·`.gradle/`은 버리지만 wrapper jar는 커밋해야 clone한 사람이 `./gradlew`만으로 빌드할 수 있다.

## 3. 더 나아가 알면 좋은 것

### 3-1. 11단계부터 CI가 무거워진다

격리 테스트 8종이 Testcontainers로 진짜 Postgres를 띄운다. `ubuntu-latest` 러너에 Docker가 기본으로 있어서 설정 추가는 없지만, 빌드 시간이 1분 → 3~4분으로 늘 것. 그때 `-x test`로 건너뛰고 싶어지는데, 그게 바로 하면 안 되는 일(설계 규칙 8·9)이다.

### 3-2. 다음에 볼 키워드

- 브랜치 보호의 "Require branches to be up to date before merging" — develop이 앞서가면 PR을 다시 rebase/merge해야 하는 설정. 4명이면 충돌이 잦아져서 일단 안 켰다
- `concurrency` 키 — 같은 PR에 연속 푸시하면 이전 CI를 취소하는 설정. 분량 아끼기

## 관련 노트

[[AiOps 03 - protocol 데이터 형식]] · [[AiOps 05 - 로컬 Postgres와 계정 3개]]
