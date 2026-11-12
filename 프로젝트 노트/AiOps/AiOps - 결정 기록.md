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

### D-092를 되돌릴 때

`ApiKeyService.issue(tenantId, env)`·`revoke(keyId)`를 컨트롤러와 분리해 두었다. v1.0 셀프 온보딩(5분 연결) 때 팀 컨트롤러에 `@RequireOwner` 엔드포인트만 붙이면 된다.

D-092 때문에 바뀐 것:
- AI-19(14단계) 담당 C → B, 에픽 AI-4 → AI-3
- AI-88 "키 발급·폐기 API — 관리자 발급"으로 변경
- AI-105 조장 수락 응답 `next`: `"issue-key"` → `"key-guide"`
- AI-22 콘솔: 팀 설정에서 발급 버튼 제거, 관리자 화면에 발급·폐기 추가
- 문서 📝: mvp-requirements C-01~C-03, v0.3 완료 기준 1번

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
