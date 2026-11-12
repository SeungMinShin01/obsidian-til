---
출처: Claude 대화
작성일: 2026-11-10
tags: [프로젝트, java]
---

# AiOps - 마스킹 Masker

> 허브: [[AiOps 프로젝트 MOC]]

**PR #36 `[AI-41] 마스킹 실구현 (Masker + RegexMasker)`** — 브랜치 `feat/starter-AI-41-masker`. 커밋 7개 + develop 머지 1개. 처음 3개(인터페이스 → 테스트 → 테스트 NPE 수정) 뒤에 구현, 이어서 Jira 명세에 맞춘 수정 3개.

## 1. 배운 내용

### 1-1. 마스킹이 하는 일

```
[팀 앱 요청 스레드]  log.error("...", e)
   → 어펜더(AI-42) → EventMapper(AI-40) → Masker.mask(event) → buffer.offer
                                            (message + causes[].message를 한 번에)
```

- 팀 앱 스레드에서 돈다 → **빠르고, 예외를 던지지 않는다**.
- 실패하면 메시지를 **빈 문자열**로. 민감정보가 새는 것보다 메시지가 없는 게 낫다(S-05 "유출보다 누락").
- 서버·DB·LLM 프롬프트·디스코드까지 이 결과만 간다. 여기가 민감정보의 **유일한 관문**이다.

### 1-2. 테스트를 먼저, 그런데 혼자 쓴다 (D-080 운영)

D-080은 "마스킹 테스트는 설계자가 먼저 쓰고 담당자가 통과시킨다"이다. C가 빠져 설계자 = 구현자가 됐다.

| D-080이 막으려던 것 | 지금 |
|---|---|
| 구현자가 자기가 떠올린 경우만 테스트 | 막을 수 없음 (같은 사람) |
| AI가 테스트를 구현에 맞춰 느슨하게 고치는 편법 | **여전히 해당** — 테스트·구현을 둘 다 Claude가 쓰므로 |

그래서 이렇게 운영한다:

1. 같은 PR이지만 커밋 순서를 **인터페이스 → 테스트 → 구현**으로. 커밋 기록이 "테스트가 구현에 맞춰 바뀌지 않았다"는 증거가 된다.
2. 테스트 표는 **사람(나)이 직접 읽고** 빠진 경우·기대값을 검토한다. 이게 D-080을 대신하는 검토다.
3. 구현 중 테스트가 틀렸다고 생각되면 몰래 고치지 않고 PR에 "테스트 수정: 이유"를 적는다.
4. 빨간 테스트를 develop에 따로 넣지 않으므로 `@Disabled`는 필요 없다. 테스트 커밋 직후에는 `RegexMasker`가 없어 **컴파일 에러 = 빨강**.

### 1-3. 정책 표 (테스트가 고정하는 것)

| 묶음 | 예 | 결과 |
|---|---|---|
| 이메일 | `user kim@example.com not found` | `user *** not found` |
| 키=값 | `password=1234`, `PASSWORD = hunter2,`, `?password=s3cr3t&ssl=true` | 키 이름·구분자는 남기고 값만 `***` |
| 키 목록 | password, passwd, pwd, secret, client_secret, token, access_token, refresh_token, api_key/apiKey/x-api-key | `tokenizer=bert`처럼 단어 일부면 그대로 |
| 토큰 모양 | `Bearer abc…`, JWT `eyJ….….…`, `aiops_l_…`, 숫자+글자 32자 이상 | `***` (Bearer는 단어를 남김) |
| 따옴표 | `'kim'`, `"abc def"`, `User "kim"`, `password="hunter2"` | `'***'`, `"***"` |
| 그대로 | `127.0.0.1:5432`, `Can't connect…`, 긴 클래스 이름(숫자 없음), UUID, `''` | 바꾸지 않음 |
| 길이 | 5000자 | **가린 뒤** 2000자로 자름 |
| 실패 | 내부에서 RuntimeException·StackOverflowError | `""` |
| 속도 | 100만 자 1번 < 0.5초, 보통 메시지 1만 번 < 1초 | |

**정책상 일부러 더 가리는 것 (검토 후 수용)**: `Invalid token: expired` → `token: ***` (일반 단어여도 가림), `'users.name'` 같은 컬럼 이름, 64자 커밋 해시.

### 1-4. NPE 메시지 결정 (D-094)

명세대로 "따옴표 안 값"을 모두 가리면 가장 흔한 에러가 이렇게 된다:

```
Cannot invoke "String.length()" because "s" is null
→ Cannot invoke "***" because "***" is null     ← 어디서 무엇이 null인지 사라짐, AI 설명 품질 저하
```

| 방법 | NPE 정보 | 유출 위험 |
|---|---|---|
| 1. 명세 그대로 | 사라짐 | 없음 |
| 2. 따옴표 안이 코드 모양(글자·숫자·`.`·`()`)이면 남김 | 남음 | **있음** — `"hunter2"`, `User "kim"`도 코드 모양 |
| **3. JVM NPE 메시지 틀일 때만 따옴표 규칙을 건너뜀** ✅ | 남음 | 없음 |

3번을 택했다. JVM의 친절한 NPE 메시지(JEP 358)는 **정해진 문장 틀**이고 따옴표 안은 메서드·필드·변수 이름이지 데이터가 아니다.

```
^Cannot (invoke|read field|assign field|load from X array|store to X array|read the array length
        |throw exception|enter/exit synchronized block)( "…")? because (the return value of )?"…" is null$
```

- 틀에 맞으면 따옴표 규칙만 건너뛴다(이메일·키=값·토큰 규칙은 그대로 적용).
- 틀이 아닌 `Cannot find user "kim"`은 가린다.
- 자바 버전이 바뀌어 문장이 달라지면 다시 가려진다 → **안전한 쪽으로 실패**.

### 1-5. 코드로 보기: RegexMasker

```java
public String mask(String raw) {
    if (raw == null) return null;
    try {
        return cut(doMask(raw));                 // ① 가린 뒤 자른다
    } catch (Throwable t) {
        return "";                               // ② 유출보다 누락
    }
}

String doMask(String raw) {
    String s = raw.length() > PRE_CUT ? raw.substring(0, PRE_CUT) : raw;   // ③
    boolean npe = NPE_TEMPLATE.matcher(s).matches();                      // ④
    s = JWT ... AIOPS_KEY ... BEARER ... EMAIL ... KEY_QUOTED ... KEY_VALUE ... LONG_TOKEN
    if (!npe) { s = DOUBLE_QUOTED ...; s = SINGLE_QUOTED ...; }            // ⑤
    return s;
}
```

| 번호 | 이유 |
|---|---|
| ① | 먼저 자르면 경계에 걸친 토큰이 32자 미만으로 잘려 **긴 토큰 규칙을 피해 새어 나간다**. 테스트 `자르기_전에_가린다`가 이걸 고정 |
| ② | `Throwable` — 정규식 StackOverflowError도 잡는다 |
| ③ | 정규식 전에 1만 자로 자른다. 100만 자 메시지에서 팀 앱 스레드가 오래 멈추지 않게. 결과는 어차피 2000자 |
| ④ | NPE 판단은 **다른 규칙을 적용하기 전 원문**으로 |
| ⑤ | 따옴표 규칙이 마지막. 앞 규칙이 이미 `***`로 바꾼 것을 `"***"`로 다시 감싸도 결과가 같다 |

| 정규식 | 포인트 |
|---|---|
| `LONG_TOKEN` `(?<![A-Za-z0-9])(?=…\d)(?=…[A-Za-z])[A-Za-z0-9]{32,}` | 숫자·글자가 **둘 다** 있어야 → `AbstractAutowireCapableBeanFactory`(숫자 없음)는 통과. 앞이 글자가 아닐 때만 시작 → 긴 단어에서 한 번만 검사(느려지지 않음). 하이픈을 빼서 UUID(조각 ≤ 12자)는 통과 |
| `SINGLE_QUOTED` `(?<![A-Za-z0-9])'[^'\r\n]+'` | 글자 바로 뒤 `'`는 아포스트로피(`Can't`, `it's`) |
| `KEY_QUOTED` → `$1$2$3***$3` | 1=키 이름, 2=`=`/`:`, 3=따옴표 종류. `password="hunter2"` → `password="***"` |
| `KEY_VALUE` 값 `[^\s,;&"']+` | `&`에서 멈춤 → JDBC URL 다음 파라미터는 남는다 |
| `cut` | 2000번째 글자가 서로게이트 앞쪽이면 1999에서 자른다(이모지 반쪽 방지) |

### 1-6. 명세와 어긋났던 것을 push 전에 맞춤

처음 코드는 Jira AI-41 명세를 확인하지 않고 만들어서 세 가지가 달랐다. push 전에 커밋을 더해 맞췄다.

| 처음 | 명세에 맞춘 뒤 | 왜 중요한가 |
|---|---|---|
| `String mask(String)` 하나 | `ErrorEvent mask(ErrorEvent)` + `String maskText(String)` | 원인 메시지(causes)를 가리는 책임이 어펜더에 있으면 **빠뜨리는 순간 유출**. Masker 한 곳에서 보장하고 테스트로 고정 |
| 이메일 → `***` | `***@***` | 이메일이 있었다는 사실이 남아 AI 설명이 문맥을 이해 |
| 키 목록에 access_key 없음 | `access[-_]?key` 추가 | AWS 접근 키(20자)는 32자 토큰 규칙에도 안 걸려 **그대로 새던 구멍** |

`mask(ErrorEvent)` 포인트:
- record가 `List.copyOf`를 써서 **null 원소를 받지 않는다** → null cause는 건너뛴다.
- 다시 만들다 실패하면 메시지·원인을 비운 이벤트(스택은 유지 — 지문 계산용), 그것도 실패하면 null(어펜더가 건너뜀).
- 스택 프레임·예외 타입·스레드·시각·단계는 건드리지 않는다(테스트 `프레임_타입_스레드_시각은_그대로`).

### 1-7. 사고: 구현 파일이 test 폴더에

첫 구현 커밋에서 `RegexMasker.java`가 `src/test/java/...`에 들어갔다. 같은 패키지라 **테스트는 통과**했지만 라이브러리 jar에는 구현이 빠진다. push 전에 `git reset --soft HEAD~1` → `git restore --staged` → `Move-Item`으로 `src/main`에 옮겨 다시 커밋했다. 교훈: 테스트 초록만 보지 말고 `git show --name-only`로 **파일 경로**를 확인한다.

## 2. 설계와 다르게 한 곳

| 명세 | 실제 | 이유 |
|---|---|---|
| D-080: 설계자 선행 테스트를 별도 PR로, 담당자가 통과 | 같은 PR, 커밋 순서로 대신 | C 탈퇴로 같은 사람 (1-2) |
| S-05: 따옴표 안 값은 가림 | JVM NPE 메시지 틀은 예외 | D-094 (1-4) |
| 테스트를 먼저 쓴 뒤 NPE 줄 변경 | 테스트 표 수정 커밋 1개 추가 | 구현 전 정책 결정으로 바뀐 것. PR에 명시 |
| 키에 `authorization` 포함 | 제외 | `Authorization: Bearer x`가 `*** ***`로 망가짐. Bearer 규칙이 토큰을 가림 |
| `Basic <토큰>` 가림 | 제외 | "Basic configuration" 같은 일반 문장 오탐 |
| 자를 때 `…(truncated)` | 그냥 자름 | 꼭 필요하지 않음 |
| 10,000자 < 10ms | 100만 자 < 0.5초, 보통 메시지 1만 번 < 1초 | 정규식 전에 1만 자로 먼저 자름 |

## 3. 더 나아가 알면 좋은 것

### 3-1. 다음에 볼 키워드

- 정규식 **ReDoS**(재앙적 백트래킹)와 입력 길이 제한
- lookahead `(?=…)`, lookbehind `(?<!…)` — 글자를 소비하지 않는 조건
- `Matcher.replaceAll`의 `$1` 그룹 참조, `Matcher.quoteReplacement`가 필요한 경우(치환 문자열에 `$`·`\`가 있을 때)
- JEP 358 Helpful NullPointerExceptions
- 서로게이트 쌍(UTF-16에서 이모지가 2칸인 이유)

## 관련 노트

[[AiOps 22 - 부품 조립 AiopsRuntime]] · [[AiOps 24 - 예외 변환 EventMapper]]
