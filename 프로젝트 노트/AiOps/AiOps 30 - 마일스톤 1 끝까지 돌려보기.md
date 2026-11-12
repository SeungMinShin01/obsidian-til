---
출처: Claude 대화
작성일: 2026-11-12
tags: [프로젝트, java]
---

# AiOps - 마일스톤 1 끝까지 돌려보기

> 허브: [[AiOps 프로젝트 MOC]]

**`[AI-44] 마일스톤 1: sample-app 에러가 서버 DB에 도착`** — 브랜치 `feat/sample-AI-44-milestone1`. 커밋: sample-app 패키지 이동(`dev.aiops.sample` → `com.example.sample`, 3파일) + README "로컬에서 끝까지 돌려보기". 코드 변경 없이 **Starter 3·4단계를 실제로 이어 붙여 확인**하는 작업.

## 1. 배운 내용

### 1-1. 왜 패키지를 옮겼나

어펜더는 `dev.aiops`로 시작하는 로거를 **무시**한다(무한 루프 방지, 노트 25의 1-4). sample-app이 `dev.aiops.sample`이면 `/boom/caught`처럼 **컨트롤러 로거로 찍은 에러가 통째로 버려진다**. 팀 앱 흉내를 내려면 팀 패키지처럼 `com.example.sample`이어야 한다. 테스트로는 안 보이고 끝까지 돌려야 보이는 종류의 문제.

### 1-2. 돌리는 순서 (터미널 2개)

```
터미널 1: docker compose up -d → 서버 bootRun (local 프로필, 시드 팀 1·키 생김)
터미널 2: $env:AIOPS_KEY="<시드 키>" → sample-app bootRun   ← 키는 같은 터미널에서
터미널 3: curl.exe localhost:8081/boom/npe ...
확인:     docker exec -it aiops-postgres psql -U postgres -d aiops -P pager=off -c "select ..."
```

### 1-3. 결과

| 호출 | 기대 | 실제 |
|---|---|---|
| `/boom/npe` | NPE 1행, 메시지 따옴표 유지 | ✅ D-094 NPE 틀 예외가 동작 |
| `/boom/sensitive` | 마스킹, 원문 검색 0건 | ✅ 원문으로 `payload::text LIKE` 검색 0건 |
| `/boom/caught` | `NumberFormatException`, 로거 `com.example.sample.BoomController` | ✅ 메시지 `"***"`(따옴표 값 가림, NPE 틀 아님) |
| `/boom/nested` | 바깥 예외 + 원인 2개 | ⚠️ `IOException "inner"`, 원인 0개 (1-4) |
| `/boom/warn`, `/ok` | 0행 | ✅ |
| DevTools 재시작 후 다시 호출 | 행 추가 | ✅ 5번째 행 도착 → 재장착 동작 (AI-43) |
| 서버 꺼 두고 `/ok` 100번 | 앱이 안 느려짐 | ✅ 2.04초 (요청 스레드는 버퍼에 넣고 끝) |

### 1-4. 발견: 잡히지 않은 컨트롤러 예외는 "가장 안쪽 원인"만 온다

```
컨트롤러가 throw new RuntimeException("outer", new IllegalStateException("mid", new IOException("inner")))
 → Spring이 ServletException으로 감싸 Tomcat에 넘김
 → Tomcat StandardWrapperValve가 **root cause**만 꺼내 log.error(..., rootCause)
 → 우리 어펜더가 받는 것: IOException("inner"), 원인 없음
```

- 매퍼 버그가 아니다. EventMapper 테스트(원인 3단 → 원인 2개)는 그대로 통과.
- `log.error("...", e)`로 **팀이 직접 찍은** 예외는 체인이 온전히 온다.
- 선택지: A 받아들임(문서화, D-095 제안) / B `HandlerExceptionResolver`를 Starter가 등록해 원본을 잡음(Bean 등록 → D-005 "Bean 아님"과 충돌, 중복 행) / C Tomcat 로거만 특별 처리(구현 의존). **A 추천, 결정 대기.**
- 손해: 지문이 바깥 예외 타입이 아니라 안쪽 타입으로 묶인다. 같은 원인의 다른 경로가 한 그룹이 될 수 있음.

### 1-5. 사고와 팁

| 증상 | 원인 | 해결 |
|---|---|---|
| 에러를 쳐도 0행 | sample-app 콘솔 첫 줄 `[aiops] aiops.api-key 없음, 비활성`. 키를 **다른 터미널**에서 설정 | 환경변수는 그 터미널 프로세스에만 있다. sample-app을 띄우는 터미널에서 설정 |
| `curl` 결과가 이상한 표 | PowerShell의 `curl`은 `Invoke-WebRequest` 별칭 | `curl.exe` |
| psql 결과 뒤 `:`에서 멈춤 | 페이저(less) | `q`, 또는 `-P pager=off` |
| 비활성 한 줄이 눈에 안 띔 | D-087: 팀 앱 로그를 어지럽히지 않으려고 `System.err` 한 줄만 | 끝까지 돌릴 때는 시작 로그 첫 화면에서 `[aiops]`부터 찾는다 |

## 2. 설계와 다르게 한 곳

| 명세 (AI-44) | 실제 | 이유 |
|---|---|---|
| 결과를 `docs/milestones.md`에 | README 절 + 이 노트 | milestones.md는 B의 AI-60 브랜치에만 있음. AI-60 머지 뒤 옮김 |
| 원인 체인 확인 | nested는 원인 0개 | 1-4 (Tomcat 동작). 팀이 직접 찍은 로그는 확인됨 |

## 3. 더 나아가 알면 좋은 것

- Tomcat `StandardWrapperValve`와 Spring `DispatcherServlet`의 예외 처리 순서 (`HandlerExceptionResolver` → `ServletException` → 컨테이너)
- 환경변수의 범위: 프로세스와 자식 프로세스만 물려받는다
- 점검 결과 장부: 「AiOps - 설계 대비 점검 (11-12)」

## 관련 노트

[[AiOps 29 - 어펜더 장착과 비활성 처리]]
