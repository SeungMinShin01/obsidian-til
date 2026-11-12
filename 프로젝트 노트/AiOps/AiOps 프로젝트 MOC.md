---
출처: Claude 대화
작성일: 2026-10-30
tags: [허브]
---

# AiOps 프로젝트 MOC

Spring Boot 앱에 **의존성 한 줄과 키 하나**만 넣으면 로컬 개발부터 배포까지 생기는 에러를 자동으로 모아 한국어로 설명하고 디스코드로 알려주는 서비스. KDT 2차 팀 프로젝트(4인)이고, 설계는 내가 하고 네 명 전부 개발한다.

이 MOC는 **코드와 환경 작업의 기록**이다. 설계 문서(요구사항, 부품 명세, 결정 기록 D-xxx)는 레포 `docs/`와 claude.ai 프로젝트 「AIOps」에 있고, Jira(Aiops_)에 단계별 스토리·하위 작업이 있다. 여기에는 그 설계를 실제로 코드로 옮기면서 **무엇을 왜 그렇게 했는지, 어디서 막혔는지**만 남긴다.

> 이 폴더의 노트는 서로만 연결되고, 바깥으로는 [[프로젝트 노트 MOC]] 하나에만 연결된다. 다른 프로젝트 MOC와는 잇지 않는다.

## 프로젝트 개요

| 항목 | 내용 |
| --- | --- |
| 목표 | MVP = v0.1(수집·그룹화·LLM 설명·디스코드) + v0.2(팀 격리 RLS) + v0.3(웹 콘솔). 18단계 83개 작업 단위 |
| 저장소 | `SeungMinShin01/aiops` (Public — JitPack 배포 때문) |
| 구조 | Gradle 멀티 모듈: `protocol` / `starter` / `server` / `sample-app` (+ `console` React, 17단계) |
| 스택 | Spring Boot 4.1.1, Gradle 9.7.1, 컴파일 타깃 Java 17, PostgreSQL 16(Docker), Flyway, Lombok(서버만, D-089), Testcontainers |
| 분담 | 처음: 나 = 환경·0·1·7·10·17·18 + 선행 테스트 / A = 2·6·13·15·16 / B = 8·9·11·12 / C = 3·4·5·14. **10/30 C 탈퇴** → 재배분안(미확정): 나 = 3·5·10(JitPack) / A = 2·6·7 / B = 4·8·9·10(VM·HTTPS·백업) |
| 브랜치 | `feature → develop`(PR, 승인 0, 셀프 머지) → `main`(배포 시점에만, 나만 병합) |
| 기간 | 10/30 ~ 11/6 (빡빡함. 밀리면 타임라인 조정) |

## 작성 원칙

- 노트 하나 = PR 하나가 기본. PR이 크면(PR #1, #3) 주제별로 나누고, 노트 맨 위에 어느 PR의 몇 번째 조각인지 적는다. 번호는 작업한 순서.
- 코드는 **실제로 커밋된 것**만 싣는다. 설계 문서에 적힌 계획과 다르게 됐으면 그 차이와 이유를 적는다.
- 세부 파생 노트(`NN-1`)는 만들지 않는다. 깊은 내용은 본문의 절로 담는다 (WMS와 같은 순수 리스트 변형).

## 주제 목록

표의 순서가 읽는 순서다.

| 주제 | 핵심 |
| --- | --- |
| [[AiOps 01 - 레포와 브랜치 전략]] | develop·main 두 단계, 승인 0명에 셀프 머지, 보호 규칙으로 "병합은 나만", Jira 연동, gradlew 실행 권한 |
| [[AiOps 02 - Gradle 멀티 모듈 뼈대]] | 모듈 4개와 의존 방향, compileOnly의 뜻, JDK 21로 Java 17 타깃, Boot 3.x → 4.1.1로 바꾼 이유, bootJar mainClass 에러 |
| [[AiOps 03 - protocol 데이터 형식]] | 순수 Java record 11개, 시간을 long으로 둔 이유, List.copyOf, 값 필드가 없는 ConfigKey, VS Code 패키지 오타 |
| [[AiOps 04 - CI와 PR 템플릿]] | job 이름이 곧 status check 이름, develop·main에만 도는 이유, PR 템플릿 다섯 칸, 원자적 커밋 |
| [[AiOps 05 - 로컬 Postgres와 계정 3개]] | 소유자와 사용자를 나누는 이유(RLS), init 스크립트는 첫 기동 한 번, 시드를 Flyway 반복 마이그레이션으로 옮긴 이유 |
| [[AiOps 06 - V1 테이블과 서버 설정]] | 계정 두 개로 붙는 yml, ddl-auto validate, V1 테이블 8개와 미룬 컬럼, 처음 띄울 때 만난 에러 |
| [[AiOps 07 - 엔티티·리포지토리·Testcontainers]] | 계층 패키지(D-088), 서버만 Lombok(D-089), CHAR·jsonb·timestamptz 매핑, 슈퍼유저를 피한 Testcontainers, 1차 캐시로 실패한 테스트, main으로 열린 PR |
| [[AiOps 08 - 하트비트와 Starter 빌드 정리]] | 하트비트를 MVP로 당긴 이유(D-086), protocol을 api로, Starter에서 Jackson을 뺀 이유(D-085), JitPack 함정 |
| [[AiOps 09 - sample-app 에러 재현 앱]] | 주소별 고장, 지연 연결이라 넣은 DbStartupCheck, 500·응답에 예외 이름 없는 이유, 팀 앱 문제와 Starter 문제 구분 |
| [[AiOps 10 - 선행 테스트 브랜치]] | 설계자가 테스트를 먼저 쓰는 이유(D-080), test/ 브랜치, MaskerTest 표, FingerprinterTest 케이스, 미확정 충돌 2건 |
| [[AiOps 11 - Starter 구조와 인터페이스]] | 스레드 두 개와 버퍼 경계, 인터페이스를 먼저 만든 이유 4가지, 인터페이스 3개로 나눈 이유, fromOrNull이 null을 돌려주는 이유 |
| [[AiOps 12 - 이벤트 버퍼 BoundedEventBuffer]] | offer와 put, getAndSet(0), null도 버린 개수, 테스트 7종, develop 43커밋 밀림, 테스트 201개 |
| [[AiOps 13 - 수집 API (A)]] | 키 해시 인증, 202와 413 필터, 커밋 후 처리 요청, touch로 통일한 하트비트, ingest.http |
| [[AiOps 14 - 처리 풀과 그룹화 (A)]] | @Async 처리 풀, 선행 테스트를 통과한 지문, ON CONFLICT + xmax로 새 그룹 판별, 재처리 스케줄러 |
| [[AiOps 15 - 보관 삭제와 수집 통계 (A)]] | 원본만 묶음 삭제, 같은 트랜잭션 통계, droppedCount가 서버까지 가는 길 |
| [[AiOps 16 - 디스코드 알림 (B)]] | Notifier 인터페이스, 웹훅 주소가 로그로 새는 경로, 분당 제한, LLM 출력 형식과의 연결 |
| [[AiOps 17 - 팀 격리 RLS (B)]] | TenantContext → set_config → RLS, 0건이 정상인 이유, 테스트에 @Transactional 금지, 격리 8종 초록 |
| [[AiOps 18 - V3 콘솔 스키마 (B)]] | RLS 없는 새 테이블 5개(D-023), text + CHECK, V3에 함께 넣은 컬럼, 12단계 PR 결정 |
| [[AiOps 19 - 디스코드 자동화 (B)]] | 저장된 id 기준 멱등, 롤백 없는 외부 시스템, 서명된 state, 웹훅만 지우는 정지 |
| [[AiOps 20 - HTTP 전송과 JsonWriter]] | 의존성 0 JsonWriter(record 리플렉션·캐시·이스케이프), 2초·3초 타임아웃, HTTP_1_1 고정, interrupt 복구, 첫 실패만 로그 |
| [[AiOps 21 - 전송 스레드 BatchingEventSender]] | 5초·100개 묶음, 1회 재시도와 개수 이월, 60초 하트비트, Clock·Sleeper·tick 테스트 구조, Atomic·final·ProtocolConstants Q&A |
| [[AiOps 22 - 부품 조립 AiopsRuntime]] | spring.factories 진입점과 순서 +1, 이중 확인 잠금, NOT NULL host_hash, 하트비트로 서버 도달 확인, D-005·006·084·087 |
| [[AiOps 23 - 마스킹 Masker]] | 정책 표, 혼자 쓰는 선행 테스트(D-080 운영), NPE 틀 예외(D-094), 가린 뒤 자르기, 정규식 lookaround |
| [[AiOps 24 - 예외 변환 EventMapper]] | 원인 체인 순환 방지(IdentityHashMap), 동적 프록시 가짜, protocol loggerName 추가, 설계로 되돌린 3가지(loggerName·phase null·줄 번호) |
| [[AiOps 25 - 어펜더 AiopsLogbackAppender]] | 팀 앱 스레드의 입구, UnsynchronizedAppenderBase, 무시 로거와 무한 루프, 점 단위 비교 |
| [[AiOps 26 - 로그인과 권한 (B)]] | 보안 체인 2개, GitHub OAuth2와 app_user, 세션 쿠키·CSRF, MembershipGuard → TenantContext, @RequireOwner, 권한 E2E 7종 |
| [[AiOps 27 - 팀 API 초대와 팀원 (B)]] | 초대 토큰(43자·해시만), 조건부 UPDATE로 동시 수락 막기, 수락 next=key-guide, 팀원 내보내기 즉시 403, 디스코드 연결 컨트롤러 |
| [[AiOps 28 - 관리자 API 기수와 접근 기록 (A)]] | 접근 기록 인터셉터(경로 패턴만 기록), V4 append-only(REVOKE), 기수 API, 이름 중복 검사의 경쟁 |
| [[AiOps 29 - 어펜더 장착과 비활성 처리]] | 루트 로거 장착·재장착(멈춘 것 교체), 세 시점 이벤트, disable 한 번만·한 줄, 전체 교체한 두 파일의 변경 표, 붙여넣기·미커밋 사고 |
| [[AiOps 30 - 마일스톤 1 끝까지 돌려보기]] | sample-app 패키지 이동 이유, 끝까지 돌린 결과표, 잡히지 않은 예외는 Tomcat이 가장 안쪽 원인만 넘김(D-095 제안), 키 터미널·curl.exe·페이저 |

## PR 대응표

| PR | 제목 | 노트 |
| --- | --- | --- |
| #1 | [AI-5] 레포·Gradle·CI·protocol 만들기 | 01 · 02 · 03 · 04 |
| #2 | (main으로 잘못 열어 닫음) | 07의 2-5 |
| #3 | [AI-6] 로컬 DB·테이블·서버 뼈대·시드 | 05 · 06 · 07 |
| #4 | [AI-33] protocol 하트비트 추가·starter 빌드 정리 | 08 |
| #5 | [AI-48] 샘플 앱 보강 (에러 API, 시작 실패 프로필) | 09 |
| — | `test/AI-41-masker`, `test/AI-51-fingerprinter` (PR 없음) | 10 |
| #6 | [AI-8] Starter 보내기 인터페이스 3개 | 11 |
| #7 | [AI-58] 알림 보내기 (B) | 16 |
| #8 | [AI-59] 채널 선택·분당 제한 (B) | 16 |
| #9 | [AI-35] 설정 읽기 실구현 (AiopsSettings) | 11 |
| #10 | [AI-90] 디스코드 준비 (B) | 19 |
| #11 | [AI-91] DiscordApiClient (B) | 19 |
| #12 | [AI-30] 키 인증 (A) | 13 |
| #13 | [AI-31] 이벤트 수집 (A) | 13 |
| #14 | [AI-32] 커밋 후 처리 요청 (A) | 13 |
| #15 | [AI-33] hello·heartbeat (A) | 13 |
| #16 | [AI-50] 처리 스레드 풀 (A) | 14 |
| #17 | [AI-51] 지문 계산 (A) | 14 |
| #18 | [AI-52] 그룹 upsert (A) | 14 |
| #19 | [AI-53] 재처리 스케줄러 (A) | 14 |
| #20 | [AI-34] ingest.http (A) | 13 |
| #21 | [AI-61] 보관 삭제 (A) | 15 |
| #22 | [AI-62] 수집 통계 (A) | 15 |
| #23 | [AI-16] 팀 격리 AI-70~75 (B) | 17 |
| #24 | [AI-77] V3 콘솔 스키마 (B) | 18 |
| #25 | [AI-92] 채널 자동 생성 (B) | 19 |
| #26 | [AI-93] 팀원 디스코드 연결 (B) | 19 |
| #27 | [AI-94] 정지 시 웹훅 삭제 (B) | 19 |
| #28 | [AI-36] 버퍼 실구현 (BoundedEventBuffer) | 12 |
| #29 | [AI-37] HTTP 전송 실구현 (HttpTransport + JsonWriter) | 20 |
| #30 | [AI-38] 전송 스레드 실구현 (BatchingEventSender) | 21 |
| #31 | [AI-81] 로그인·권한 (AI-76·78~81 포함, B) | 26 |
| #32 | [AI-93] 디스코드 연결 컨트롤러 (B) | 27 |
| #33 | [AI-39] 부품 조립 (AiopsRuntime + 진입점 등록) | 22 |
| #34 | [AI-105] 초대 발급·수락 (B) | 27 |
| #35 | [AI-89] 팀원 초대·목록·내보내기 (B) | 27 |
| #36 | [AI-41] 마스킹 실구현 (Masker + RegexMasker) | 23 |
| #37 | [AI-40] 예외 변환 실구현 (EventMapper + DefaultEventMapper, protocol loggerName) | 24 |
| #38 | [AI-87] 관리자 접근 기록 (A) | 28 |
| #39 | [AI-82] 관리자 기수 API (A) | 28 |
| #40 | [AI-42] 어펜더 (AiopsLogbackAppender) | 25 |
| #41 | [AI-88] 관리자 키 발급·폐기 (B) | (다음) |
| #42 | [AI-43] 어펜더 장착·재장착·비활성 처리 | 29 |
| #43 | [AI-44] 마일스톤 1 (sample-app 패키지 이동 + README) | 30 |
| — | `test/AI-76-authorization` (PR 없음, #31에 포함되어 머지) | 18의 5절 · 26 |

## 장부

| 노트 | 용도 |
| --- | --- |
| [[AiOps - 규칙제안 기록]] | 이 프로젝트가 Vault 규칙에 낸 제안과 처리 상태 |
| [[AiOps - 배포 전 고려사항]] | 첫 배포 전에 고치거나 결정할 것 (방법 비교표, 상태, 처리 체크) |
| [[AiOps - 결정 기록]] | 대화에서 정한 D-번호 결정·번호 없는 합의·일정 판단 (레포 문서 반영 여부 표시) |
| [[AiOps - 설계 대비 점검 (11-12)]] | develop 코드 전체를 설계·Jira 명세와 대조한 결과 (부품별 표, 위험, 5·7단계 준비 메모) |

## 개념 노트

아직 없다. 같은 개념을 두 곳 이상에서 만난 뒤에 만든다. 멱등성(디스코드 채널 생성, 그룹 upsert)과 빠른 실패(RLS fail closed)는 다른 프로젝트에 이미 개념 노트가 있어서, 만나면 공유할지 보고하고 정한다.

## 진행 기록

| 날짜 | 내용 |
| --- | --- |
| 2026-10-29 | 환경: GitHub 레포·보호 규칙·Jira 연동·Docker 확인. 0단계: Gradle 멀티 모듈, protocol 11개, CI, PR 템플릿, 문서 → PR #1 머지. Jira AI-5·24·25 완료 |
| 2026-10-30 | 1단계 착수: docker-compose, 계정 3개 init 스크립트, 시드. C 탈퇴 → C 몫(Starter 3·4·5단계)을 내가 이어받기로 |
| 2026-11-02 | 1단계 완료(V1·엔티티·리포지토리·Testcontainers) → PR #3. 하트비트·Starter 빌드 정리 → PR #4. sample-app → PR #5. 선행 테스트 2개 브랜치. 다음: 3단계 Starter 보내기(인터페이스 3개부터) |
| 11/3~11/5 | A: 2·6·9단계 머지(#12~#22). B: 8·11·15단계와 V3 머지(#7·#8, #10·#11, #23~#27). 9단계는 A, 15단계는 B로 바꿔서 진행 |
| 11/4 | 권한 E2E 선행 테스트 `test/AI-76-authorization` push (B의 V3 브랜치 위) |
| 11/10 | 진행률: B 14/19, A 11/21, 나 9/43 (머지 기준). 병목은 Starter(3·4·5)와 LLM(7). AI-36(#28)·AI-37(#29) 머지, AI-38 커밋 완료. 새 규칙: 메서드 참조(`::`) 대신 람다 |
| 11/10 오후 | AI-38(#30) 머지, AI-39(#33) PR, 하트비트 서버 도착 확인. D-092(키 관리자 발급), D-094(NPE 틀 예외). 14단계 B 이관. MVP 43%, 주말 완료 불가 판단 |
| 11/11~11/12 | AI-40(#37, protocol loggerName)·AI-42(#40) 머지, AI-43 PR #42. A: 13단계 착수(#38 접근 기록·#39 기수). B: 14단계 #34·#35·#41 머지. Jira 일정을 PR 실제 기간으로 정리. 팀원 PR 리뷰 노트 26~28. 다음: 마일스톤 1(AI-44, 11/13), LLM(11/15), main PR은 첫 배포 직전(11/18~19) |
| 11/12 | AI-43(#42) 머지. **마일스톤 1 확인**: sample-app 에러 5행 서버 DB 도착, 마스킹·재장착·서버 꺼짐 확인. nested 예외는 가장 안쪽 원인만(D-095 제안). 설계 대비 점검: JsonWriter HEX 표 버그 발견(hotfix), 기본 프로필 local 위험. 다음: hotfix → LLM(AI-54) |

## 관련 노트

[[프로젝트 노트 MOC]]
