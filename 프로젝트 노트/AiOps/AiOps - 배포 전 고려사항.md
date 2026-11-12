---
출처: Claude 대화
작성일: 2026-11-10
tags: [프로젝트, java]
---

# AiOps - 배포 전 고려사항

> 허브: [[AiOps 프로젝트 MOC]]

**용도: 첫 배포(10단계) 전에 고치거나 결정해야 할 것들을 모아 둔 장부.** 코드 리뷰(11/10, develop 기준)에서 나왔다. 항목마다 방법과 비교표를 남겨 두었으니, 배포 전에 이 노트를 위에서부터 보면서 결정하고 처리한다. 처리하면 상태를 바꾸고 PR 번호를 적는다.

## 0. 한눈에 보기

| # | 문제 | 추천 | 비용 | 담당 | 언제까지 | 상태 |
|---|---|---|---|---|---|---|
| 1 | `dev.aiops.` 접두사에 샘플 앱이 걸림 | A: sample-app 패키지 변경 | 30분 | 나 | 마일스톤 1 전 | ✅ A 적용 (AI-44 브랜치, PR 머지 대기) |
| 2 | local에서 본 에러가 prod에서 나도 알림 없음 | B: 그룹 키에 env 추가 (D-093, V4) | 반나절 | A | **마일스톤 2 전 (데이터가 쌓이기 전)** | ⬜ 미결정 |
| 3-1 | 본문 크기 필터가 chunked 전송을 통과시킴 | A + C: 411 + 프록시 제한(Nginx, D-097) | 30분 + 한 줄 | A, 나 | 411은 지금, Nginx는 10단계 | ⬜ 미결정 |
| 3-2 | 정지된 팀의 키가 통과됨 | A: 13단계에서 + 캐시 evict | Jira 한 줄 | A | 13단계 | ⬜ 미결정 |
| 5 | 서버 기본 프로필이 `local` — 운영에서 프로필을 빠뜨리면 시드 팀·키가 운영 DB에 생기고 쿠키 secure=false | A: 기본 프로필 삭제 + 운영 `.env.example`에 `SPRING_PROFILES_ACTIVE=prod` | 한 줄 + 로컬 실행법 README | 나 | **배포 직전에 삭제** (10단계) | ✅ A 결정 (11/12), 적용 대기 |
| 6-1 | 프록시 뒤 `X-Forwarded-*` 미처리 → OAuth 리다이렉트가 http로 만들어짐 | A: `server.forward-headers-strategy: native` + Nginx `proxy_set_header` (서버 포트는 Nginx에만) | 한 줄 + Nginx 4줄 | B | 10단계 | ✅ A 결정 (11/12), Jira AI-65·102 반영 |
| 6-2 | 두 보안 체인 밖 경로가 검사 없이 통과 | A: 마지막 체인 `denyAll` (`/health`·`/error`만 허용) | 체인 하나 + 테스트 | B | 10단계 | ✅ A 결정 (11/12) |

표 읽는 법: **이점** = 적용하면 얻는 것 / **적용 비용** = 지금 해야 하는 작업과 손대는 범위 / **적용 후 단점** = 적용한 다음 남는 부작용·위험 / **되돌리기** = 나중에 마음이 바뀌었을 때 얼마나 쉽게 되돌리나.

---

## 1. `dev.aiops.` 접두사 — 샘플 앱 프레임이 걸러진다

### 문제

- `Fingerprinter.FRAMEWORK_PREFIXES`에 `dev.aiops.`가 있다. Starter 자기 프레임을 빼려는 것이다.
- 그런데 **sample-app 패키지가 `dev.aiops.sample`**이라 샘플 앱 프레임도 "프레임워크"로 빠진다.
  - 지문이 JDK 프레임 기준으로 계산된다 → 같은 예외 타입이 위치와 상관없이 한 그룹으로 섞일 수 있다.
  - `top_frame`(디스코드 embed의 "위치")이 `java.lang.String#length` 같은 값이 된다.
- **같은 원인으로 생기는 두 번째 문제:** 설계 ③(D-087)에 따라 Starter 어펜더는 `dev.aiops`로 시작하는 **로거를 무시**한다(자기 로그를 다시 잡는 무한 반복 방지). 그래서 샘플 앱이 **자기 로거로 직접 남긴 에러**(예: `/boom/caught`)는 아예 수집되지 않는다.
- 원인은 하나다: **샘플 앱이 우리 내부 코드와 같은 이름 공간을 쓴다.** 원래 내 선행 테스트(AI-51) 명세에서 시작된 문제다.

### 방법 비교

| 방법 | 이점 | 적용 비용 | 적용 후 단점 | 되돌리기 |
|---|---|---|---|---|
| **A. sample-app 패키지 변경** `dev.aiops.sample` → `com.example.sample` | 지문 문제와 **어펜더 무시 문제를 함께 해결**. 샘플이 실제 팀 앱과 같은 조건이 됨(AI-44: "팀 앱과 같은 조건이어야 의미가 있다"). 서버·Starter 규칙은 그대로 | 나, 30분. 파일 3개 이동 + `build.gradle` mainClass(있다면) + README·Jira AI-44의 패키지명 | 문서·노트에 남은 옛 이름이 헷갈릴 수 있음. 실제 팀 패키지가 우연히 `dev.aiops`로 시작하면 같은 문제(가능성 매우 낮음) | 쉬움 |
| B. 접두사를 `dev.aiops.starter.`·`dev.aiops.server.`로 좁힘 | 서버 쪽에서 근본적으로 막힘. 팀 패키지가 `dev.aiops`여도 안전 | A의 `Fingerprinter`·`GroupingService` 수정 PR + 내 선행 테스트 이름("10개") 수정. 2명이 손댐 | **어펜더 무시 문제는 남음.** 접두사가 11개가 되고, Starter에 새 패키지가 생기면 목록도 고쳐야 함 | 보통 |
| C. 접두사 목록을 yml 설정으로 | 팀별 프레임워크(MyBatis 등)도 나중에 뺄 수 있음 | 설정 클래스 + 테스트, 기본값 관리 | 설정을 잘못 넣으면 그룹화가 **조용히** 바뀜. 지금 쓸 사람이 없어 과한 설계 | 보통 |
| D. 그대로 둠 | 작업 없음 | 없음 | 시연 "위치"가 JDK 프레임. 그룹이 섞일 수 있음. `/boom/caught` 수집 안 됨 | — |

**추천: A.** 비용이 가장 작고, 하나로 두 문제를 해결하며, 되돌리기도 쉽다. B는 A 이후 방어용으로 고려할 수 있지만 필수는 아니다.

### 처리할 때 체크

- [ ] sample-app 패키지 이동 (`SampleApplication`, `BoomController`, `DbStartupCheck`)
- [ ] `sample-app/build.gradle` mainClass 확인
- [ ] README, Jira AI-44, 노트 09의 패키지명
- [ ] `/boom/caught`가 수집되는지 마일스톤 1에서 확인
- [ ] 디스코드 embed "위치"가 `com.example.sample.BoomController#npe`로 나오는지 마일스톤 2에서 확인

---

## 2. env별 첫 발생 알림 — local에서 본 에러가 prod에서 나도 조용하다

### 문제

- 그룹 유일 키가 `(tenant_id, fingerprint)`다. env가 없다.
- 그래서 local에서 처음 본 에러가 나중에 prod에서 나면 **새 그룹이 아니고**, 알림도 가지 않는다. 알림 채널도 `first_env`(local)를 따른다.
- 코드는 설계 ⑭(`(tenant_id, fingerprint)` 유니크)대로 만들어졌다. **설계의 빈틈**이다.
- 다른 문서들은 그룹이 env를 구분한다고 가정한다: 요구사항 V-01 "그룹 목록 env 필터", v1.2 "prod 에러 그룹만 장애를 연다".

### 방법 비교

| 방법 | 이점 | 적용 비용 | 적용 후 단점 | 되돌리기 |
|---|---|---|---|---|
| A. 그대로 (원인별 그룹 1개) | 알림이 가장 적음. 작업 없음 | 없음 | **prod 첫 발생이 조용함.** 운영·발표 때 가장 필요한 알림이 빠짐. env 필터와 v1.2 규칙이 애매해짐 | — |
| **B. 그룹 키에 env 추가** `(tenant_id, env, fingerprint)` | 규칙이 가장 단순("env가 다르면 다른 그룹"). prod 첫 발생 알림이 자동으로 됨. V-01·v1.2와 바로 맞음 | A, 반나절. V4(유니크 제약 교체, `first_env` → `env`) + upsert SQL 한 줄 + 엔티티·Notifier의 `getFirstEnv` + 테스트. **데이터가 쌓이기 전인 지금이 가장 쌈** | 같은 원인이 local·prod **두 줄**로 보임. **LLM 호출 최대 2배**(일일 상한 안). 원인별 합계는 두 줄을 더해야 함 | **어려움** (V5로 합치고 쌓인 데이터를 병합해야 함) |
| C. 그룹 1개 + env별 첫 발생 테이블 (`error_group_env`) | 원인별 통계·LLM은 1개, prod 첫 알림도 됨. 데이터 모델로는 가장 정확 | A, 1~1.5일. 새 테이블 + RLS + upsert 2단계 + Notifier에 env 인자(B의 코드도 바뀜) + 테스트 대폭 수정 | 처리 경로가 복잡해져 동시성 버그 가능성 증가(8스레드 테스트 재작성). 콘솔 쿼리에 조인 증가 | 보통 |
| D. `error_group.prod_notified_at` 컬럼 1개 + "prod로 처음 오면 알림" 분기 | 스키마 변경이 작음. 그룹·LLM은 1개 유지 | A, 반나절. V4 컬럼 1개 + 처리 루프 분기 | local만 특별 취급하는 규칙이라 env가 늘면(staging) 다시 고쳐야 함. "새 그룹이 아닌데 알림" 예외 경로가 생김 | 쉬움 |

**추천: B.** 규칙이 단순하고 다른 문서와 맞으며, 단점(두 줄, LLM 2배)은 운영상 받아들일 만하다. **되돌리기 어려우니 마일스톤 2 전에 정하고 D-093로 기록**한다. "원인별로 하나"를 꼭 유지하고 싶으면 D가 가장 싼 대안이다.

### 처리할 때 체크 (B로 갈 경우)

- [ ] D-093 설계 문서 기록 (⑭ 유니크 키 변경, 기각: A·C·D)
- [ ] `V4__group_env.sql`: 유니크 제약 교체, `first_env` → `env`
- [ ] `GroupUpserter` SQL의 `ON CONFLICT (tenant_id, env, fingerprint)`
- [ ] `ErrorGroupEntity`, `DiscordWebhookNotifier`의 `getFirstEnv`
- [ ] 테스트: 같은 지문 local·prod → 그룹 2개, prod 첫 발생 → 알림 1번
- [ ] Grafana `grafana_ro` 컬럼 권한(컬럼 이름이 바뀌면 GRANT 다시)

---

## 3-1. 본문 크기 필터 — chunked 전송은 통과한다

### 문제

`IngestBodySizeFilter`는 `Content-Length` 헤더만 본다. chunked 전송(길이 헤더 없음, 값 -1)은 검사 없이 통과한다. 우리 Starter는 `ofString`이라 항상 길이를 보내지만, 악의적인 큰 요청은 막지 못한다.

### 방법 비교

| 방법 | 이점 | 적용 비용 | 적용 후 단점 | 되돌리기 |
|---|---|---|---|---|
| **A. 길이 헤더가 없으면 411 Length Required** | 앱에서 바로 막음. 로컬·운영 모두 적용 | A, 30분. 필터 조건 1개 + 테스트 1개 | chunked로 보내는 클라이언트는 거절(지금은 Starter뿐, Starter는 항상 길이를 보냄) | 쉬움 |
| B. 읽으면서 바이트를 세다가 넘으면 413 | chunked까지 정확히 막음. 클라이언트 제약 없음 | A, 반나절. 요청 래퍼 + 스트림 처리 + 테스트 | 코드가 가장 복잡. 읽던 도중 끊을 때 응답이 깨지는 경계 상황 | 보통 |
| **C. 프록시 본문 제한** (원래 Caddy `request_body max_size 1MB` → D-097로 Nginx `client_max_body_size 2m`) | 앱 앞에서 모든 경로를 막음. 앱 코드 그대로 | 나, 10단계 설정 한 줄 | 로컬에는 적용 안 됨(운영 전이라 실질 공백 없음) | 쉬움 |
| D. 그대로 | 작업 없음 | 없음 | 큰 chunked 요청이 서버 메모리를 씀(공격 경로) | — |

**추천: A + C.** 둘 다 작고 쉽게 되돌릴 수 있으며, 앱과 인프라 두 겹으로 막는다.

### 처리할 때 체크

- [ ] `IngestBodySizeFilter`: `getContentLengthLong() < 0`이면 411 + 테스트
- [ ] 10단계 Nginx `ingest.` server 블록에 `client_max_body_size 2m;` — 서버 1MB와 같거나 약간 크게(AI-65). D-097로 Caddy에서 변경

---

## 3-2. 정지된 팀의 키 — 아직 통과한다

### 문제

`ApiKeyResolver` 5번 주석: 정지된 팀(SUSPENDED)의 키 거부는 13단계에서 추가할 예정이다. 지금은 정지 API가 없어서 실제 공백은 없다.

### 방법 비교

| 방법 | 이점 | 적용 비용 | 적용 후 단점 | 되돌리기 |
|---|---|---|---|---|
| **A. 13단계(AI-85 정지 API)에서 처리** | 정지 기능과 함께 만들고 함께 테스트. 지금 작업 없음 | Jira AI-85에 "키 거부 + **정지 시 캐시 evict**" 한 줄 추가 | 13단계 전에는 정지 개념 없음(실제 공백 없음) | — |
| B. 지금 `ApiKeyResolver`에 상태 확인 추가 | 미리 막아 둠 | A, 반나절. tenant 조회 + 정지 이벤트에서 evict | 정지 API가 없어 **테스트하기 어려움.** 키 확인마다 tenant 조회 증가(캐시로 상쇄) | 보통 |
| C. 키는 통과, 웹훅만 삭제(현재 AI-94) | 작업 없음 | 없음 | 정지 팀 데이터가 계속 쌓이고 LLM 호출도 계속됨 | — |

**추천: A.** 핵심은 **evict를 빠뜨리지 않는 것.** 빠뜨리면 정지 직후 최대 60초(캐시 TTL) 동안 키가 통과한다.

### 처리할 때 체크

- [ ] Jira AI-85 본문에 "정지 팀 키 401 + 그 팀 키 전부 캐시 evict" 추가
- [ ] 13단계 테스트: 정지 직후 같은 키 → 즉시 401

---

## 4. 같이 정리할 작은 것들

| 항목 | 내용 | 담당 |
|---|---|---|
| PR 템플릿 | `pull_request_template.md`에 `## <!-- … -->` 줄 2개(포매터가 바꾼 것). PR에서 빈 제목줄로 보임 | 나, docs PR |
| Jira AI-34 | 키 `aiops_local_dev_key` → `aiops_l_local-dev-key-0001`, 필드명 `apiVersion`·`frames` 오류 | 나 |
| D-090 | `notify/` 임시 인정. 정리 시점이 "15단계 전"이었는데 15단계가 끝남. 정리할지 결정 | 나 |
| 레포 문서 | 레포의 `docs/aiops-v0.1-architecture.md`가 1.3(D-083~091 없음), `CLAUDE.md`·`team-guide-pr.md`도 옛 버전 | 나, docs PR |
| `.gitattributes` | `* text=auto` 정리. 윈도우에서 CRLF만 바뀐 파일이 계속 "수정됨"으로 보임 | 나 |
| 주석 | `ErrorEventRepository.findUnprocessed`의 "RLS가 켜지면 팀별 조회로 바꿈" — 이미 팀마다 set해서 부르므로 주석만 정리 | A |
| 운영 디스코드 | 운영 서버·봇을 `docs/discord-setup.md`대로 생성, `.env`에 `AIOPS_STATE_SECRET` | 나, 10단계 |

---

## 5. 서버 기본 프로필이 `local` — 운영에서 빠뜨리면 조용히 local로 켜진다

### 문제

- `application.yml`의 `spring.profiles.default: local`. 운영에서 `SPRING_PROFILES_ACTIVE`를 빠뜨리면:
  - Flyway가 `db/seed`를 돌려 **시드 팀과 원문이 레포에 공개된 키**가 운영 DB에 생긴다.
  - 세션 쿠키가 `secure: false`.
  - DB 주소가 `localhost`로 덮여 연결 실패 — 원인을 찾기 어렵다.

### 방법 비교

| 방법 | 이점 | 적용 비용 | 적용 후 단점 | 되돌리기 |
|---|---|---|---|---|
| **A. 기본 프로필 삭제** + 운영 `.env.example`에 `SPRING_PROFILES_ACTIVE=prod` | 프로필이 없으면 DB 설정이 없어 **시작 실패**. 실수가 바로 보임 | 한 줄 + README | 로컬 실행마다 `--spring.profiles.active=local`이나 IDE 설정. 기본 프로필에 기대는 테스트가 있으면 수정 | 줄을 다시 넣으면 끝 |
| B. 유지 + 시작 검사 Bean (local인데 DB가 localhost가 아니면 거부) | 로컬 습관 그대로 | Bean + 테스트 | 검사 조건이 틀리면 뚫림. 지킬 코드가 늘어남 | Bean 삭제 |
| C. 시드는 `seed` 프로필, 쿠키 기본 `secure: true` | 빠뜨려도 기본값이 안전 | 설정 재배치 | 로컬에서 프로필 2개 | 파일 다시 합침 |

**결정: A (11/12). 단, 개발 중 로컬 편의를 위해 삭제는 첫 배포 직전에 한다.**

### 처리할 때 체크

- [ ] 배포 직전: `application.yml`에서 `spring.profiles.default` 삭제
- [ ] 서버 테스트가 기본 프로필에 기대는지 확인 (`@ActiveProfiles`)
- [ ] README·IDE 실행 설정에 `local` 프로필 안내, 팀원 공지
- [ ] `infra/prod/.env.example`에 `SPRING_PROFILES_ACTIVE=prod` (값 없는 줄)
- [ ] 운영 첫 기동 후 tenant 테이블에 시드 팀이 없는지 확인

---

## 6. 프록시 뒤 설정 두 가지

### 6-1. `X-Forwarded-*` 처리 — A 결정

**문제:** 운영은 프록시(Nginx, D-097)가 HTTPS를 받고 서버에는 http로 넘긴다. 서버는 자신을 http로 알아서 GitHub 로그인 리다이렉트 주소가 `http://...`로 만들어지고 GitHub가 거부할 수 있다.

| 방법 | 이점 | 적용 비용 | 적용 후 단점 | 되돌리기 |
|---|---|---|---|---|
| **A. `forward-headers-strategy: native`** | 표준. Tomcat이 **사설 IP에서 온 헤더만** 믿어 외부 위조 무시 | 한 줄 | 서버 포트가 인터넷에 직접 열리면 의미 감소 → 포트는 Nginx에만 | 줄 삭제 |
| B. `framework` (`ForwardedHeaderFilter`) | 표준 `Forwarded` 헤더도 처리 | 한 줄 | 기본으로 모든 출처를 믿음 → 포트가 열리면 위조 가능 | 줄 삭제 |
| C. `redirect-uri`를 yml에 https로 고정 | 헤더를 믿지 않음 | 한 줄 | OAuth만 해결, `isSecure()` 등은 여전히 http | 줄 삭제 |

**결정: A (11/12).** 프록시는 Nginx(D-097). Nginx는 헤더를 기본으로 붙이지 않으므로 `proxy_set_header X-Forwarded-Proto $scheme` 등을 **반드시** 넣어야 하고, 서버 쪽 A도 여전히 필요.

### 6-2. 두 보안 체인 밖 경로 — A 결정

**문제:** 체인은 `/v1/**`와 `/api/**`·로그인 경로에만 걸린다. 그 밖(`/actuator/**`, 앞으로 생길 경로)은 **보안 검사 없이 통과**.

| 방법 | 이점 | 적용 비용 | 적용 후 단점 | 되돌리기 |
|---|---|---|---|---|
| **A. 마지막 체인 `denyAll`** (`/health`·`/error`만 허용) | 새 경로가 기본으로 닫힘 (fail closed) | 체인 하나 + 테스트 | 열어야 할 경로를 빠뜨리면 403 (헬스체크, 서버가 정적 파일을 서빙한다면 그 파일) | 체인 Bean 삭제 |
| B. 그대로 + actuator 노출만 `health`로 제한 | 동작 변화 없음, 한 줄 | 한 줄 | 앞으로 생기는 경로가 조용히 열림 | 줄 삭제 |

**결정: A (11/12).**

### 처리할 때 체크 (6-2)

- [ ] `SecurityConfig`에 가장 낮은 순서의 체인: `/health`·`/error` permitAll, 나머지 denyAll (지금 주석: `/health`·`/_test/**`는 어느 체인에도 없음. `_test`는 테스트 코드에만 있음)
- [ ] 테스트: 체인 밖 임의 경로 → 403, `/health` → 200. 테스트용 `/_test/**`가 막히지 않는지 확인
- [ ] 배포 헬스체크 주소가 허용 목록에 있는지 확인
- [ ] 담당 B(조현우)에게 전달
