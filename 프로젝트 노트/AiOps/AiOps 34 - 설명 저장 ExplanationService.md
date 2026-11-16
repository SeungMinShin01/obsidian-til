---
출처: Claude 대화
작성일: 2026-11-15
tags: [프로젝트, java]
---

# AiOps - 설명 저장 ExplanationService

> 허브: [[AiOps 프로젝트 MOC]]

**PR #51 `[AI-56] 새 그룹 LLM 설명 저장 (1부)`** — 11/15 머지. 그룹 하나에 LLM 설명을 **한 번만** 붙인다. 아직 이 서비스를 부르는 곳은 없다. 처리 흐름(`ErrorProcessor`)에 한 줄 넣는 2부는 B의 AI-60 머지를 기다린다.

## 1. 배운 내용

### 1-1. 이 PR이 하는 일

```
ExplanationService.explain(tenantId, groupId)        ← @Transactional 없음
   ① ExplanationStore.load        짧은 트랜잭션 (그룹 + 가장 최근 이벤트 1건)
   ② 이미 설명이 있으면 끝 / 대표 이벤트가 없으면 끝
   ③ LlmQuota.tryAcquire          상한 (이 PR에서는 항상 허용, 구현은 AI-57)
   ④ LlmClient.complete           ★ 트랜잭션 밖. 최대 20초
   ⑤ ExplanationStore.saveIfEmpty 짧은 트랜잭션 (비어 있을 때만 저장)
```

### 1-2. 코드로 보기: LLM 호출을 트랜잭션 밖에 두는 이유

```java
ExplanationStore.Loaded loaded = store.load(tenantId, groupId);          // 트랜잭션 1 (끝남)
...
Optional<String> answer = llmClient.complete(prompt);                    // 트랜잭션 없음
...
boolean saved = store.saveIfEmpty(tenantId, groupId, answer.get());      // 트랜잭션 2
```

트랜잭션이 열려 있는 동안은 DB 연결 하나를 붙잡는다. 그 안에서 LLM을 부르면 응답을 기다리는 20초 동안 연결이 묶인다. 연결 풀은 10개 안팎이라, 새 에러가 몰리면 **수집·콘솔까지 DB를 못 쓴다.** 그래서 조회와 저장만 짧게 묶고 호출은 그 사이에 둔다.

### 1-3. 코드로 보기: Store를 다른 클래스로 뺀 이유

```java
@Service
public class ExplanationStore {
    @Transactional(readOnly = true) public Loaded load(...) { ... }
    @Transactional                  public boolean saveIfEmpty(...) { ... }
}
```

`@Transactional`은 Spring이 Bean을 감싼 **프록시**가 처리한다. 같은 클래스 안에서 `this.load()`로 부르면 프록시를 거치지 않아 **트랜잭션이 안 열린다.** 이 프로젝트는 트랜잭션이 열릴 때 `app.tenant_id`를 넣기 때문에(RLS), 트랜잭션이 없으면 팀 격리도 같이 빠진다. 그래서 DB 접근 두 개를 다른 Bean으로 뺐다.

### 1-4. 코드로 보기: 한 번만 저장

```java
@Modifying
@Query("""
        UPDATE ErrorGroupEntity g
        SET g.aiExplanation = :explanation, g.aiExplainedAt = :explainedAt
        WHERE g.id = :id AND g.tenantId = :tenantId AND g.aiExplanation IS NULL
        """)
int updateExplanationIfNull(...);
```

"읽고 → 비었으면 → 쓴다"를 코드로 하면, 같은 그룹에 두 스레드가 동시에 들어왔을 때 둘 다 "비었다"고 보고 덮어쓴다. **조건을 UPDATE의 WHERE에 넣으면** DB가 한 줄씩 처리하므로 먼저 온 쪽만 1을 받고 나머지는 0을 받는다. 초대 수락(노트 27)과 같은 방식이다.

### 1-5. 실패하면 NULL로 둔다

| 상황 | 저장 | 이유 |
|---|---|---|
| LLM이 empty (장애·타임아웃) | 안 함 | "설명 실패" 같은 글을 넣으면 재시도 대상에서 빠진다. NULL이어야 다시 시도한다 |
| 상한 | 안 함 | 위와 같음 |
| 예외 | 안 함, 로그에 **예외 클래스 이름만** | 메시지에 프롬프트·응답 내용이 섞일 수 있다 |

`explain`은 예외를 밖으로 던지지 않는다. 설명은 덤이다. 설명이 실패했다고 그룹 처리나 알림이 실패하면 안 된다.

### 1-6. 대표 이벤트

`findFirstByGroupIdOrderByReceivedAtDescIdDesc` — 그룹의 **가장 최근 1건.** 받은 시각이 같을 때를 위해 id를 두 번째 기준으로 넣었다(없으면 실행마다 다른 행이 나올 수 있다). 이벤트 본문(JSON)은 Jackson 3(`tools.jackson.databind.ObjectMapper`)으로 `ErrorEvent`로 바꾼다.

### 1-7. 테스트 6개

| 테스트 | 확인 |
|---|---|
| 한 번만 | 같은 그룹에 두 번 불러도 LLM 호출 1회 |
| 실패 시 NULL | empty면 저장 안 함 |
| 상한 | `tryAcquire`가 false면 LLM을 부르지도 않는다 |
| 트랜잭션 밖 | LLM 호출 시점에 활성 트랜잭션이 없다 |
| 다른 팀 그룹 | 저장 안 함 |
| 먼저 채워짐 | LLM을 기다리는 사이 다른 쪽이 먼저 저장했으면 덮어쓰지 않는다 |

LLM은 호출 횟수를 세는 가짜(`CountingLlm`)로 바꿨다. Mockito를 쓰지 않고 인터페이스를 직접 구현했다(메서드가 하나라 그게 더 짧다).

## 2. 설계와 다르게 한 곳

| 명세 | 실제 | 이유 |
|---|---|---|
| AI-56 한 번에 | 1부(서비스)·2부(`ErrorProcessor` 연결)로 나눔 | B의 AI-60이 같은 파일의 생성자를 바꾸는 중이다. 먼저 고치면 충돌한다 |
| 상한 없음 | `LlmQuota` 자리만 미리 (항상 허용) | AI-57에서 서비스 코드를 다시 열지 않으려고 |

## 3. 사고와 팁

| 증상 | 원인 | 해결 |
|---|---|---|
| `cannot find symbol: class Optional` (`ErrorEventRepository`) | 메서드만 붙이고 `import java.util.Optional;`을 빠뜨림 | import 한 줄 추가. **인터페이스에 메서드를 붙일 때는 돌려주는 타입의 import도 같이 본다** |
| 다음 브랜치에서 Java 파일 6개가 "수정됨"으로 뜸, 내용 차이는 없음 | 줄바꿈(CRLF/LF)만 다름. `git diff --ignore-cr-at-eol`이 비어 있으면 이 경우 | 진짜 바꾼 파일만 하나씩 커밋한 뒤 `git restore server/src` |

## 4. 남은 것

- 2부: 새 그룹이 생기는 자리에서 `explain` 호출, "같은 에러 10번 → 호출 1회" 테스트 (B의 AI-60 뒤)
- D-096: 처리 풀이 가득 찰 때의 정책, LLM 별도 풀
- 키가 없으면 가짜 응답이 저장된다 → AI-57의 재시도는 키가 없으면 아예 돌지 않게 했다

## 관련 노트

[[AiOps 33 - 프롬프트 조립 PromptBuilder]] · [[AiOps 35 - 로컬 환경변수를 env 파일로]]
