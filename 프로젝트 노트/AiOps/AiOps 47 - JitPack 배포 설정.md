---
출처: Claude 대화
작성일: 2026-11-24
tags: [프로젝트, java]
---

# AiOps - JitPack 배포 설정

> 허브: [[AiOps 프로젝트 MOC]]

**PR #77 `[AI-63] JitPack 배포 설정 (protocol·starter)`** — 커밋 4개, 11/24 머지. 다른 프로젝트가 의존성 한 줄로 Starter를 받게 하는 설정. 태그 전에 커밋 번호로 시험 빌드를 했고 통과했다.

## 1. 배운 내용

### 1-1. JitPack이 하는 일

```
GitHub 공개 레포의 커밋(또는 태그)
   └ JitPack이 그 커밋을 내려받아 jitpack.yml의 명령을 실행
        └ 결과물(jar, pom)을 자기 저장소에 올림
             └ 다른 프로젝트: implementation 'com.github.SeungMinShin01.aiops:starter:<태그>'
```

Maven Central처럼 계정·서명 절차가 없다. 공개 레포와 빌드 설정만 있으면 된다. 대신 빌드를 JitPack이 하므로, 우리 PC에서 되는 것과 JitPack에서 되는 것은 별개다.

### 1-2. 코드로 보기: 주소는 JitPack이 만든다

```groovy
allprojects {
    group = 'com.github.SeungMinShin01'                                  // ①
    version = findProperty('releaseVersion') ?: '0.1.0-SNAPSHOT'         // ②
}
```

| 번호 | 뜻 |
|---|---|
| ① | JitPack 규칙은 `com.github.<사용자>`. 모듈이 여러 개인 레포는 JitPack이 `com.github.<사용자>.<레포>`로 바꿔서 내준다 |
| ② | 태그 이름이 버전이 되어야 한다. 값이 고정돼 있으면 `-Pversion=`으로도 안 바뀌어서, 따로 받는 속성을 뒀다 |

빌드 로그에 그대로 찍힌다.

```
Found artifact: com.github.SeungMinShin01:starter:5aed90ce98          ← 우리가 만든 것
✅ Build artifacts:
com.github.SeungMinShin01.aiops:starter:5aed90ce98                    ← JitPack이 내주는 주소
```

JitPack은 pom 안의 **의존성 주소도 같이 바꾼다**. 내주는 `starter` pom을 열어 보면 `protocol` 의존성이 `com.github.SeungMinShin01.aiops:protocol:5aed90ce98`로 되어 있다. 그래서 받는 쪽은 `starter` 한 줄만 적어도 `protocol`이 따라온다.

### 1-3. 코드로 보기: pom에 싣지 않는 것

```groovy
dependencyManagement {
    generatedPomCustomization { enabled = false }     // Spring Boot BOM을 pom에 안 싣는다
}
tasks.withType(GenerateModuleMetadata).configureEach { enabled = false }   // .module 파일을 안 만든다
```

- **BOM**: Starter가 Spring 버전 목록을 들고 가면 팀 앱의 버전 결정에 끼어든다. Starter는 팀 앱이 가진 것을 빌려 쓸 뿐이다(규칙 3, `compileOnly`). 결과 pom의 의존성은 `protocol` 하나다.
- **`.module`**: Gradle은 pom 말고 자기 전용 설명 파일도 올린다. JitPack이 주소를 바꿔 주는 것은 pom인데 이 파일은 옛 주소를 그대로 들고 있어서, 받는 쪽 Gradle이 이 파일을 먼저 읽으면 `protocol`을 못 찾는다(JitPack 이슈 #4476). 파일을 아예 안 만들면 pom만 읽힌다.

### 1-4. 코드로 보기: jar에 버전을 적는다

```groovy
tasks.named('jar') {
    manifest { attributes('Implementation-Version': project.version) }
}
```

`StarterVersion`은 jar의 이 값을 읽어 `[aiops] 비활성화됨: … (starter <버전>)`에 쓴다. 그런데 빌드가 이 값을 넣은 적이 없었다 — 읽는 코드만 있고 쓰는 설정이 없었던 것. 배포 설정을 하면서 찾았다.

### 1-5. 태그 전에 커밋 번호로 먼저

JitPack은 태그가 없어도 커밋 번호로 빌드한다. 한 번 민 태그는 옮길 수 없고(JitPack이 처음 결과를 기억한다) 틀리면 `v0.1.1`을 새로 붙여야 하므로, 설정이 맞는지는 커밋 번호로 먼저 본다. `develop-SNAPSHOT`처럼 움직이는 이름은 시험에 쓰지 않는다 — 같은 이름으로 다른 코드가 나온다.

## 2. 실수 기록

- `git checkout -c`는 없다. 새 브랜치는 `git switch -c` 또는 `git checkout -b`.
- PowerShell에서는 `/c/Users/...` 경로가 안 읽힌다(Git Bash용). PowerShell은 `C:\Users\...`, 실행은 `.\gradlew`.
- JitPack의 Commits 탭은 기본 브랜치(`main`)만 보여 준다. 코드가 `develop`에 있으면 옆의 화살표로 브랜치를 바꿔야 한다.

## 3. main에 처음 올리면서 알게 된 것

`develop`은 "CI 초록이면 본인이 머지"인데 `main`에는 **다른 사람 1명의 승인**이 더 걸려 있다. 자기 PR은 자기가 승인할 수 없다. 지금까지 `main`으로 머지한 적이 없어서 처음 만났다.

## 4. 남은 것

- 다른 프로젝트에서 실제로 받아서 실행 (hello 도착까지)
- `develop` → `main` 머지(승인 1명 필요) → 태그 `v0.1.0`
- 로그 맨 위의 `fatal: detected dubious ownership`은 JitPack 쪽 git 설정 경고이고 빌드에는 영향이 없었다

## 관련 노트

[[AiOps 40 - 안전성 테스트 7종 (Boot 4)]] · [[AiOps 11 - Starter 구조와 인터페이스]] · [[AiOps 46 - 콘솔 관리자 현황 화면]]
