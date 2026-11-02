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

## PR 대응표

| PR | 제목 | 노트 |
| --- | --- | --- |
| #1 | [AI-5] 레포·Gradle·CI·protocol 만들기 | 01 · 02 · 03 · 04 |
| #2 | (main으로 잘못 열어 닫음) | 07의 2-5 |
| #3 | [AI-6] 로컬 DB·테이블·서버 뼈대·시드 | 05 · 06 · 07 |
| #4 | [AI-33] protocol 하트비트 추가·starter 빌드 정리 | 08 |
| #5 | [AI-48] 샘플 앱 보강 (에러 API, 시작 실패 프로필) | 09 |
| — | `test/AI-41-masker`, `test/AI-51-fingerprinter` (PR 없음) | 10 |

## 장부

| 노트 | 용도 |
| --- | --- |
| [[AiOps - 규칙제안 기록]] | 이 프로젝트가 Vault 규칙에 낸 제안과 처리 상태 |

## 개념 노트

아직 없다. 같은 개념을 두 곳 이상에서 만난 뒤에 만든다. 멱등성(디스코드 채널 생성, 그룹 upsert)과 빠른 실패(RLS fail closed)는 다른 프로젝트에 이미 개념 노트가 있어서, 만나면 공유할지 보고하고 정한다.

## 진행 기록

| 날짜 | 내용 |
| --- | --- |
| 2026-10-29 | 환경: GitHub 레포·보호 규칙·Jira 연동·Docker 확인. 0단계: Gradle 멀티 모듈, protocol 11개, CI, PR 템플릿, 문서 → PR #1 머지. Jira AI-5·24·25 완료 |
| 2026-10-30 | 1단계 착수: docker-compose, 계정 3개 init 스크립트, 시드. C 탈퇴 → C 몫(Starter 3·4·5단계)을 내가 이어받기로 |
| 2026-11-02 | 1단계 완료(V1·엔티티·리포지토리·Testcontainers) → PR #3. 하트비트·Starter 빌드 정리 → PR #4. sample-app → PR #5. 선행 테스트 2개 브랜치. 다음: 3단계 Starter 보내기(인터페이스 3개부터) |

## 관련 노트

[[프로젝트 노트 MOC]]
