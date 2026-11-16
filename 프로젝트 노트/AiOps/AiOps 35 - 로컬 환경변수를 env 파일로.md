---
출처: Claude 대화
작성일: 2026-11-15
tags: [프로젝트]
---

# AiOps - 로컬 환경변수를 env 파일로

> 허브: [[AiOps 프로젝트 MOC]]

**PR #52 `[AI-6] 로컬 실행 환경변수를 .env 파일로`** — 브랜치 `chore/infra-AI-6-dotenv`, 커밋 7개(빌드 3, 예시 1, 문서 3). 11/15 PR. 터미널에 매번 넣던 값을 `infra/local/.env` 파일 하나로 옮겼다.

## 1. 배운 내용

### 1-1. 왜 바꿨나

- 터미널에 넣은 값은 **그 창을 닫으면 사라진다.** 서버 창과 샘플 앱 창에 따로 넣어야 했다.
- 팀원에게 "무슨 값이 필요한지" 알려줄 곳이 없었다. 이제 `.env.example`(이름만, 값은 비어 있음)이 그 목록이다.

| 파일 | 커밋 | 내용 |
|---|---|---|
| `infra/local/.env.example` | 한다 | 이름과 설명. 진짜 값 없음 |
| `infra/local/.env` | **안 한다** (`.gitignore`) | 각자 PC에서 복사해 값을 채운다 |

### 1-2. 코드로 보기: gradle/dotenv.gradle

```groovy
tasks.matching { it.name == 'bootRun' }.configureEach {          // ①
    def envFile = rootProject.file('infra/local/.env')
    if (envFile.exists()) {                                       // ②
        envFile.readLines('UTF-8').each { line ->
            def text = line.trim()
            if (text.isEmpty() || text.startsWith('#') || !text.contains('=')) {
                return
            }
            def idx = text.indexOf('=')                           // ③
            def key = text.substring(0, idx).trim()
            def value = text.substring(idx + 1).trim()
            ...
            if (!value.isEmpty() && System.getenv(key) == null) { // ④
                environment key, value
            }
        }
    }
}
```

| 번호 | 이유 |
|---|---|
| ① | **`bootRun`에만** 건다. `test`·`build`에는 안 걸린다 (1-3) |
| ② | 파일이 없어도 그냥 넘어간다. CI와 처음 받은 사람의 PC에서 깨지지 않게 |
| ③ | **첫 번째 `=`** 에서만 나눈다. 값 안에 `=`가 들어 있는 경우가 흔하다 |
| ④ | 빈 값(`KEY=`)은 넣지 않는다 → yml의 `${KEY:기본값}`에서 기본값이 쓰인다. 터미널에 이미 넣은 값이 있으면 그쪽이 이긴다(잠깐 다른 값으로 돌려 볼 때) |

`server/build.gradle`, `sample-app/build.gradle`에는 `apply from: rootProject.file('gradle/dotenv.gradle')` 한 줄씩.

### 1-3. Spring이 아니라 Gradle에서 읽게 한 이유

| 방법 | 얻는 것 | 잃는 것 |
|---|---|---|
| Spring 설정(`spring.config.import`)으로 읽기 | IDE 실행 버튼에서도 읽힌다 | **테스트도 읽는다.** 내 PC의 진짜 키로 테스트가 LLM·디스코드를 실제로 부를 수 있다. 사람마다 테스트 결과가 달라진다 |
| **Gradle `bootRun`에서 읽기 (선택)** | 테스트·빌드·운영에 영향 없음. 의존성 추가 없음 | IDE 실행 버튼으로 띄우면 안 읽힌다 (`./gradlew :server:bootRun`으로 띄워야 함) |

되돌리려면 `build.gradle` 두 곳의 `apply from` 줄을 지우면 된다.

### 1-4. 빈 값의 함정 (노트 32에 이어서)

`.env`에 `AIOPS_LLM_BASE_URL=`처럼 이름만 있고 값이 비어 있을 때, 그대로 환경변수로 넣으면 기본 주소 대신 **빈 문자열**이 된다. 스크립트가 빈 값을 건너뛰기 때문에 `.env.example`을 그대로 복사해도 기본값이 유지된다.

## 2. 설계와 다르게 한 곳

`docs/discord-setup.md`에 "로컬은 IDE 실행 설정이나 셸에 넣는다. Spring은 `.env`를 읽지 않는다"고 적혀 있었다. 이 줄과 `README.md`, `sample-app/README.md`의 실행 안내를 `.env` 방식으로 고쳤다.

## 3. 확인한 것

터미널에 키를 넣지 않고 `./gradlew :sample-app:bootRun` → "키 없음" 안내가 뜨지 않음 → 에러 주소 호출 → 서버 DB `error_event`에 새 행.

## 4. 팁

- `.env`를 확인할 때는 **이름만** 본다. 값을 화면·채팅·노트에 붙이지 않는다 (규칙 10).
- 로컬 시드 키는 README에 이미 공개된 개발용 값이라 예시 파일에 넣었다. 진짜 키는 예시 파일에 넣지 않는다.
- 값을 바꾸면 `bootRun`을 다시 띄워야 한다 (시작할 때 한 번만 읽는다).

## 관련 노트

[[AiOps 34 - 설명 저장 ExplanationService]] · [[AiOps 36 - LLM 일일 상한과 설명 재시도]]
