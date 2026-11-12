---
출처: Claude 대화
작성일: 2026-11-02
tags: [프로젝트, java]
---

# AiOps - 선행 테스트 브랜치

> 허브: [[AiOps 프로젝트 MOC]]

**PR 없음** — `test/AI-41-masker`, `test/AI-51-fingerprinter` 두 브랜치만 원격에 올렸다. 담당자가 이 브랜치에서 자기 브랜치를 따고, 그 사람의 PR이 develop에 들어갈 때 테스트도 같이 들어간다.

## 1. 배운 내용

### 1-1. 왜 테스트를 내가 먼저 쓰나 (D-080)

마스킹(민감정보 유출)과 지문(같은 에러 판정)은 틀리면 서비스 전체가 무너지는 부품이다. 구현하는 사람이 테스트까지 쓰면, 특히 AI로 짤 때 "통과하는 테스트"를 만들기 쉽다. 그래서 **무엇이 맞는지는 설계자가 테스트로 정하고, 담당자는 그 테스트를 고치지 않고 초록으로 만든다**(규칙 9). 같은 방식이 격리 8종(AI-69)과 권한 E2E(AI-76)에도 있는데, 둘 다 v0.2·v0.3이라 아직 안 썼다.

### 1-2. 왜 develop이 아니라 test/ 브랜치인가

선행 테스트는 구현이 없어서 **컴파일조차 안 된다**(빨강). develop에 넣으면 CI `build`가 깨지고, 그러면 다른 모든 PR도 머지가 막힌다. 그래서 테스트만 든 브랜치를 따로 두고 담당자가 거기서 출발한다.

```
B: git fetch origin && git checkout -b feat/starter-AI-41-masker origin/test/AI-41-masker
A: git fetch origin && git checkout -b feat/server-AI-51-fingerprinter origin/test/AI-51-fingerprinter
```

"빨간 이유가 맞는지"는 `compileTestJava`로 본다. 오류가 `cannot find symbol … RegexMasker`·`Fingerprinter`만 나와야 한다. 다른 오류가 섞이면 테스트 자체가 틀린 것.

### 1-3. MaskerTest (AI-41, B) — 입력·기대값 표

| 규칙 | 입력 | 기대 |
| --- | --- | --- |
| 이메일 | `user hong@example.com not found` | `user ***@*** not found` |
| Bearer | `… with Bearer abc123.def456` | `… with Bearer ***` |
| Basic | `… with Basic dXNlcjpwYXNz` | `… with Basic ***` |
| 키=값 | `login failed password=1234` | `login failed password=***` |
| 대소문자·콜론 | `PASSWORD: hunter2` | `PASSWORD: ***` |
| api_key | `api_key=xyz` | `api_key=***` |
| JSON 따옴표 | `{"secret": "abc def"}` | `{"secret": "***"}` |
| 작은따옴표 | `token='abc def'` | `token='***'` |
| JDBC URL | `…?user=app&password=s3cret` | `…?user=app&password=***` |
| 긴 토큰 | 40자 영숫자 | `***` |
| 평범한 문장 | `Cannot invoke "String.length()" …` | 그대로 |

그 밖에 null → null, 6,000자 → 최대 2,000자 + `…(truncated)`, 10,000자 입력이 100ms 안(정규식 백트래킹 폭발 감시), `mask(ErrorEvent)`가 메시지·원인 메시지만 바꾸고 타입·스택·나머지 필드는 그대로인지.

- 키 이름은 남기고 **값만** 가린다. "어떤 키가 문제였는지"는 디버깅에 쓸모가 있다.
- Starter 테스트에는 AssertJ가 없다(새 의존성 금지). JUnit 기본 단언만.
- "규칙 하나가 예외를 내면 그 필드는 빈 문자열"은 테스트로 일부러 예외를 낼 방법이 없어서 PR 리뷰 때 코드로 본다.

### 1-4. FingerprinterTest (AI-51, A)

지문 = `예외타입|팀프레임1|팀프레임2|팀프레임3`(각 프레임은 `클래스#메서드`, 줄 번호 없음)의 SHA-256 hex. 기대값은 테스트 안에서 같은 문자열을 `MessageDigest`로 해시해 만든다.

케이스 9개: 줄 번호만 다르면 같은 지문 / 프레임워크 프레임은 건너뛰고 팀 프레임 상위 3개만 / 접두사 10개(`java.` `javax.` `jakarta.` `jdk.` `sun.` `org.springframework.` `org.hibernate.` `com.zaxxer.` `org.apache.` `dev.aiops.`) 모두 제외 / 팀 프레임이 없으면 전체 상위 3개 / 팀 프레임 1개면 그것만 / 예외 타입 다르면 다른 지문 / 빈 스택이면 타입만 / 64자 hex 소문자 / 같은 입력 같은 결과.

- 줄 번호를 빼는 건 코드 한 줄만 늘어도 다른 그룹이 되는 걸 막으려고, 프레임워크를 빼는 건 모든 에러가 Spring 내부 프레임으로 똑같아지는 걸 막으려고.
- 예외 **메시지**는 지문에 안 넣는다. id·시각이 들어가 매번 달라진다.

## 2. 추가로 알면 좋은 활용법

### 2-1. 경로가 깊어도 괜찮다

`server/src/test/java/dev/aiops/server/service/FingerprinterTest.java`가 너무 깊지 않나 싶었다. `src/test/java`는 Gradle 표준이고, `dev/aiops/server/service`는 패키지 이름이 곧 폴더 경로라서 생긴다. Windows 경로 제한(260자)에도 여유가 있다(가장 긴 게 약 110자). 다닐 때는 `Ctrl+P`로 파일 이름 검색, 또는 Java Projects 패널의 패키지 보기를 쓴다.

## 3. 더 나아가 알면 좋은 것

### 3-1. 아직 확정 안 된 설계 충돌 2건

테스트를 쓰다가 Jira 명세와 다르게 한 곳이다. 확정되면 Jira AI-41·AI-51 본문을 고친다.

- **Fingerprinter 입력 타입**: Jira는 `List<String>`(`"클래스#메서드:줄"` 문자열)인데 protocol의 스택은 `List<StackFrame>` record다. 테스트는 `fingerprint(String, List<StackFrame>)`로 썼다. 문자열을 다시 만들고 쪼갤 필요가 없다.
- **Basic 토큰**: Jira는 `Basic xxx → Bearer ***`인데 인증 방식이 틀어지므로 `Basic ***`로 썼다.

### 3-2. 다음에 볼 키워드

- 정규식 재앙적 백트래킹 — `(a+)+` 같은 중첩 수량자
- `@ParameterizedTest` + `@MethodSource` — 입력·기대값 표를 테스트로
- `HexFormat` (Java 17) — 바이트 배열 → hex 문자열

## 관련 노트

[[AiOps 09 - sample-app 에러 재현 앱]] · [[AiOps 11 - Starter 구조와 인터페이스]]
