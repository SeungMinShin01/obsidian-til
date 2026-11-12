---
출처: Claude 대화
작성일: 2026-11-10
tags: [프로젝트]
---

# AiOps - 결정 기록

> 허브: [[AiOps 프로젝트 MOC]]

대화 중에 정한 것을 모아 둔 장부. 번호(D-)가 붙은 것은 레포 `docs/aiops-v0.1-architecture.md` 5절에도 넣어야 한다(다음 docs PR). 상태: ✅ 확정 · ⏳ 제안·대기 · 📝 레포 문서 미반영

## 1. 번호 있는 결정

| ID | 날짜 | 결정 | 이유 | 기각한 대안 | 상태 |
|---|---|---|---|---|---|
| D-091 | 11/9 | PR 단위는 자유. 고정은 base develop·CI 초록·하위 작업 키·Merge commit 4가지 | 팀원이 PR을 배우는 단계. 방식보다 결과(깨지지 않는 develop)가 중요 | 하위 작업 단위 고정, 스토리 단위 고정 | ✅ (프로젝트 docs 반영, 레포 📝) |
| D-092 | 11/10 | **API 키는 관리자가 발급·폐기**. 조장은 콘솔에서 목록(앞 4자리·env·마지막 사용)만. 원문은 관리자가 디스코드 DM으로 1회 전달(local → 조장, prod → 배포 담당) | MVP 일정 단축, 키 수 통제. 기수당 5~10팀이라 수동 전달 가능 | A 조장 발급(원래 설계), C 팀 생성 시 자동 발급 + 채널 게시(원문이 채팅 기록에 남음, 규칙 40 예외 필요), D 관리자 발급 + 조장 조회 | ✅ Jira 반영 📝 |
| D-093 | — | (예약) 그룹 키에 env 추가 — AiOps - 배포 전 고려사항 2번 | | | ⏳ 결정 대기 |
| D-094 | 11/10 | **마스킹: JVM NPE 메시지 틀이면 따옴표 규칙을 건너뜀** | 가장 흔한 에러의 핵심 정보(어떤 호출에서 무엇이 null)를 살림. 틀 안의 따옴표 값은 코드 이름이지 데이터가 아님 | 1 명세 그대로(정보 손실), 2 코드 모양이면 남김(`"hunter2"`, `User "kim"` 유출) | ✅ 📝 |
| D-095 | 11/12 | **잡히지 않은 컨트롤러 예외는 Tomcat이 넘기는 가장 안쪽 원인만 받는다** (A안). MVP는 그대로 두고 문서화 | Starter는 Bean이 아님(D-005). 팀이 `log.error(msg, e)`로 찍은 예외는 체인이 온전함 | B `HandlerExceptionResolver` 등록(Bean·중복 행), C Tomcat 로거 특별 처리(구현 의존) | ✅ 📝 |
| D-096 | 11/12 | **수집 응답과 처리를 분리**: 처리 풀이 가득 차면 `CallerRunsPolicy` 대신 거절 + 경고 한 줄, 거절된 이벤트는 `ReprocessScheduler`가 나중에 처리(A). LLM 설명은 별도 작은 풀에서, 가득 차면 버리고 재시도에 맡김(B) | 리스너가 돌 때 이벤트는 이미 커밋됨 → 거절해도 유실 없음. LLM(최대 20초)이 붙으면 CallerRuns가 수집 요청 스레드를 붙잡아 Starter 타임아웃(3초) → 재전송·중복 위험 | C 지금처럼 CallerRuns 유지 | ✅ 📝 A는 LLM 착수 전, B는 AI-54·55와 함께 |
| D-097 | 11/12 | **리버스 프록시는 Caddy 대신 Nginx** | 자료·경험이 압도적으로 많아 막혔을 때 풀기 쉽고, 실무·포트폴리오에서 통하는 경험. 우리 규모에서 성능 차이는 없음 | Caddy(원래 설계: 인증서 자동·설정 짧음, 고른 이유는 기록에 없었음) | ✅ 📝 |
| D-098 | 11/12 | **React 콘솔: 뼈대는 설계자, 연동은 그 API를 만든 사람** (17단계 D-079 담당 변경). 나 AI-99 뼈대(목 화면 7개·공통 컴포넌트·client.ts·로그인 견본 연동)·AI-102 배포 / A AI-100 에러·AI-101 관리자 / B AI-106 팀 설정 | 내 남은 작업 21→약 15, 병렬 진행. 응답 형식을 아는 사람이 붙여 계약 어긋남을 바로 잡음 | A 설계자 전부(12월 초로 밀림), C 뼈대+B 혼자 연동 | ✅ 📝 Jira 담당·AI-22 댓글 반영 |
| D-099 | 11/12 | **운영은 AWS: EC2 1대 + RDS PostgreSQL(내부 전용)**. RDS 퍼블릭 액세스 끔, 5432는 EC2 보안 그룹에서만. 관리 접속은 EC2 경유 SSH 터널. EC2에는 IAM 역할(접근 키 없음) | 자동 백업·시점 복구, DB가 서버와 분리. "5432는 외부에 안 연다" 규칙 그대로 | A DB도 컨테이너(백업이 같은 디스크), C ECS+ALB(과함). ALB는 서버 2대 이상일 때 | ✅ 📝 Jira AI-64·67 댓글. ⚠ RDS에서 계정 3개·`BYPASSRLS` 되는지 첫 세팅 때 확인 |

### D-092를 되돌릴 때

`ApiKeyService.issue(tenantId, env)`·`revoke(keyId)`를 컨트롤러와 분리해 두었다. v1.0 셀프 온보딩(5분 연결) 때 팀 컨트롤러에 `@RequireOwner` 엔드포인트만 붙이면 된다.

D-092 때문에 바뀐 것:
- AI-19(14단계) 담당 C → B, 에픽 AI-4 → AI-3
- AI-88 "키 발급·폐기 API — 관리자 발급"으로 변경
- AI-105 조장 수락 응답 `next`: `"issue-key"` → `"key-guide"`
- AI-22 콘솔: 팀 설정에서 발급 버튼 제거, 관리자 화면에 발급·폐기 추가
- 문서 📝: mvp-requirements C-01~C-03, v0.3 완료 기준 1번

### D-096 결정 전 상황과 비교 (11/12)

**지금 구조** (`AsyncConfig`, `ErrorsStoredListener`, `ErrorProcessor`)

```
수집 요청 → 이벤트 저장 → 커밋 → ErrorsStoredListener(AFTER_COMMIT) → ErrorProcessor.process (@Async)
처리 풀 aiopsProcessingExecutor: 스레드 4, 대기줄 1000, 가득 차면 CallerRunsPolicy
```

- 가득 차면 **부른 스레드 = 수집 요청 스레드**가 처리까지 직접 한다. 주석의 의도는 "이벤트를 잃는 것보다 낫다".
- 지금은 처리가 빨라서 문제가 드러나지 않는다. LLM 호출(타임아웃 20초)이 처리 안에 들어가면 풀이 쉽게 차고, 수집 응답이 수십 초 늦어진다.
- Starter 요청 타임아웃은 3초 → 서버는 저장했는데 Starter는 실패로 본다 → 다시 보내면 중복 저장, 버리면 실패 통계가 틀어진다.
- 핵심 사실: 리스너가 돌 때 이벤트는 **이미 DB에 있다**. 처리하지 못한 행은 `ReprocessScheduler`가 `findUnprocessed`로 다시 집는다. "잃는 것보다 낫다"는 전제가 성립하지 않는다.

| | A. 거절 + 재처리 스케줄러에 맡김 | B. LLM을 별도 풀로 분리 | C. 지금처럼 유지 |
|---|---|---|---|
| 방법 | 거절 정책으로 바꾸고 경고 로그 한 줄 | 그룹화·알림은 지금 풀, LLM 설명만 `aiopsLlmExecutor`(작은 풀, 가득 차면 버림) | 변경 없음 |
| 얻는 것 | 수집 응답이 처리 속도와 완전히 분리. 이벤트는 DB에 있어 유실 없음. 한두 줄 | 느린 LLM이 그룹화·알림을 막지 않음. 알림이 빨리 가고 설명은 나중에 채워짐 | 작업 없음. 처리를 항상 즉시 시도 |
| 잃는 것 | 몰릴 때 처리·알림이 스케줄러 주기만큼 늦어짐 | 풀이 하나 늘어 설정·테스트 증가. "설명 없이 먼저 가는 알림" 흐름을 설계해야 함 | LLM이 붙으면 수집 지연·중복·통계 오류 위험 |
| 되돌리기 | 정책 한 줄 | 풀 Bean·호출부 | — |

**결정: A + B.** A는 수집 API가 어떤 경우에도 처리 때문에 기다리지 않게 하는 안전장치, B는 원래 설계의 "새 그룹 알림 → 설명은 나중에" 흐름과 맞다.

**처리할 때 체크**
- [ ] `AsyncConfig`: `CallerRunsPolicy` → 거절 + 경고 로그(이벤트 id·팀 id만, 내용 없음)
- [ ] 테스트: 풀을 가득 채운 상태에서 수집 응답 시간이 늘지 않고, 스케줄러가 나중에 처리
- [ ] B: `aiopsLlmExecutor` 빈 + LLM 실패·거절 시 `ai_explanation` NULL 유지 → 재시도(AI-57) 대상
- [ ] 담당: 처리 풀은 A(김지환, AI-50 작성자)와 협의, LLM 풀은 나(AI-54·55)

### D-097 결정 전 비교 (11/12)

설계 문서(architecture 구성표, mvp-requirements O-04·O-05)에 Caddy가 적혀 있었지만 **고른 이유를 남긴 결정 기록은 없었다**. 배포 전 6-1(프록시 헤더)을 보다가 확인.

| | Caddy | **Nginx (선택)** |
|---|---|---|
| HTTPS 인증서 | 자동 발급·갱신 | certbot 설치·발급·갱신 타이머 직접. 갱신 빠지면 90일 뒤 끊김 |
| 설정 길이 | 도메인당 3~5줄 | 도메인당 20줄 안팎 |
| 프록시 헤더 | `X-Forwarded-*` 기본 | `proxy_set_header` 직접 |
| HTTP→HTTPS | 기본 | 직접 (certbot이 넣어 주기도 함) |
| 자료·경험 | 적음, 한국어 더 적음 | **압도적으로 많음**, 실무에서 익숙 |
| 성능 | 우리 규모에서 차이 없음 | 같음 |

- 얻는 것: 막혔을 때 검색으로 해결, 실무·면접에서 쓸 수 있는 경험, 세밀한 제어(캐시·속도 제한).
- 잃는 것: 인증서 운영과 설정 실수 지점이 늘어남. React 라우팅용 `try_files`, 헤더 4줄, 본문 크기 제한을 직접 챙겨야 함.
- 되돌리기: 설정 파일 하나 교체. 서버 코드는 프록시와 무관(주석 2곳만).

**바꿔야 할 곳**
- 레포 docs: `aiops-v0.1-architecture.md` 27·93줄, `mvp-requirements.md` O-04·O-05
- 서버 주석: `HealthController`, `SecurityConfig` ("Caddy 헬스체크")
- Jira: AI-65·102·22·1·15·23 — ✅ 11/12 반영 (AI-102의 `forward-headers-strategy: framed` 오타, AI-15의 `aiops.key` 오류도 함께 수정)
- 배포 전 3-1: Caddy `request_body` → Nginx `client_max_body_size 1m`

**Nginx 설정 때 체크**
- [ ] `ingest.`·`app.`·`grafana.` server 블록, certbot 발급 + 갱신 타이머 확인(`certbot renew --dry-run`)
- [ ] `proxy_set_header Host / X-Real-IP / X-Forwarded-For / X-Forwarded-Proto`
- [ ] `app.`: React 정적 파일 + `try_files $uri /index.html`, `/api/`·`/oauth2/`·`/login/`·`/logout`만 서버로
- [ ] `ingest.`: `client_max_body_size 2m` (서버 1MB보다 약간 크게, chunked 전송에도 적용됨)
- [ ] 서버 포트(8080)는 외부에 열지 않음 — Nginx만 접근

## 2. 번호 없는 합의

| 날짜 | 합의 | 내용 | 상태 |
|---|---|---|---|
| 11/10 | 12단계 PR 순서 | test/AI-76만 따로 머지하면 E2E가 302로 빨강 → AI-76 커밋을 로그인 PR에 함께. 결과: B가 AI-81 브랜치로 PR #31 머지 | ✅ |
| 11/10 | `@RequireOwner` TYPE | 명세(METHOD+TYPE)가 맞고 커밋에서 빠진 건 설계자 실수. B가 AI-81에서 추가 | ✅ |
| 11/10 | 마일스톤 1 기록 | 옮길 기존 기록 없음. AI-44 때 승민이 `docs/milestones.md`(B의 AI-60 브랜치에서 생성)에 작성 | ⏳ |
| 11/10 | Starter 진입점 패키지 | `lifecycle/` 대신 `runtime/` (AI-39). Jira 에픽 AI-4 수정 | ✅ |
| 11/10 | 초대 토큰 형식 | 원문 = `Base64.getUrlEncoder().withoutPadding()`(32바이트, 43자), 난수 `new SecureRandom()`(`getInstanceStrong()`은 리눅스에서 멈출 수 있음), DB `ApiKeyHasher.sha256Hex(원문)`만, 링크 `<aiops.console.base-url>/invite/<원문>`, 조장 링크 OWNER·max_uses 1·만료 7일, 수락 `POST /api/invitations/{token}/accept` | ✅ B 제안 + 보완 3개 |
| 11/10 | `InvitationService` 소유 | 명세는 A(AI-84)지만 B가 AI-105에서 issue·accept를 먼저 만듦 → B 것을 쓰고 A는 `issue(tenantId, OWNER, 1, 7일, adminId)` 호출만 | ⏳ 팀에 전달 필요, AI-84 명세의 `getInstanceStrong()` 수정 필요 |
| 11/10 | D-080 운영 (마스킹) | 설계자 = 구현자라 같은 PR, 커밋 순서 인터페이스 → 테스트 → 구현, 테스트 표는 사람이 검토 | ✅ AiOps 23 - 마스킹 Masker 1-2 |
| 11/10 | 메서드 참조 | 새 코드는 `::` 대신 람다. 머지된 것은 MVP 후 리팩터링 | ✅ |
| 11/10 | EventMapper 명세 대비 (AI-40, PR #37) | **설계대로 되돌림**: loggerName 담기, phase는 받은 그대로(null 포함), 줄 번호는 원본(-1 모름, -2 네이티브). **protocol에 맞춘 것**: `time`(epoch millis), `fileName` 포함, `MAX_STACK_FRAMES` | ✅ |
| 11/10 | `loggerName`을 ErrorEvent에 추가 | 처음엔 protocol에 칸이 없어 빼고 보고하지 않음(실수) → 리뷰 후 추가. 끝에 추가 + 기존 생성자 유지로 기존 코드 수정 없음. 서버는 payload JSONB라 DB 변경 없음 | ✅ PR #37 |
| 11/10 | phase null을 기본값으로 덮지 않음 | 덮으면 우리 버그(시작 실패를 RUNTIME으로)가 숨는다. AI-42·45 테스트에서 상수를 넘기는지 고정 | ✅ |
| 11/10 | Logback 없는 앱 | EventMapper가 `ILoggingEvent`를 써서 Log4j2 앱에서는 Starter 전체가 꺼질 수 있음(앱은 D-087로 안전). AI-49 안전성 테스트에서 확인 | ⏳ AI-49 |
| 11/10 | Jira 일정 정리 | 완료된 하위 작업 47개·스토리 9개의 시작일 = PR 브랜치 첫 커밋, 마감일 = PR 머지일(KST). 스토리에는 원래 계획 마감을 댓글로 남김. 완료 처리 시각(resolution)은 API로 못 바꿔서 그대로 | ✅ |

## 3. 일정 판단

| 날짜 | 판단 | 상태 |
|---|---|---|
| 11/10 | MVP 진행률: 하위 작업 83개 중 36개 완료(43%), 진행 중 7개 | 기록 |
| 11/10 | 이번 주말(11/15) MVP 완료 가능성 5% 미만. 주말까지 현실적: 마일스톤 1·2, B 12·14단계, A 13·16단계 API | 기록 |
| 11/10 | MVP 완료일 11/22(여유 11/24) 제안. 전제: React 콘솔을 B에게, A에게 LLM 또는 배포 중 하나 | ⏳ 결정 대기 |
