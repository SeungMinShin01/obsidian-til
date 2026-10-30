---
출처: Claude 대화
작성일: 2026-10-30
tags: [프로젝트]
---

# AiOps - 레포와 브랜치 전략

> 허브: [[AiOps 프로젝트 MOC]]

## 1. 배운 내용

### 1-1. 왜 공개 레포인가

Starter를 다른 조가 `implementation 'com.github.<아이디>.aiops:starter:v0.1.0'` 한 줄로 받게 하려면 JitPack을 쓰는데, JitPack은 **공개 레포만 무료로 빌드**한다. 그래서 처음부터 Public. 대신 키·토큰·웹훅 주소는 코드에 절대 못 들어간다는 제약이 생기고, 이게 설계 규칙 10("비밀값은 환경변수로만")의 실제 이유가 됐다.

### 1-2. 브랜치는 두 단계, 병합은 역할이 다르다

```
feature/* ──(PR, 승인 0명, CI 초록이면 본인이 머지)──→ develop ──(배포 시점에만 PR, 나만 병합)──→ main
```

처음엔 "develop 없이 feature → main, 내가 다 병합"도 생각했다. 하지만 배포 뒤에도 개발은 계속되고, 그때 "운영에 올라간 상태(main)"와 "다음에 올릴 것(develop)"이 구분돼야 한다. 그래서 develop을 뒀다.

develop PR에 **승인을 0명**으로 둔 건 팀원이 내 승인을 기다리느라 멈추는 걸 막기 위해서다. 대신 "PR을 연다"는 형식은 유지해서 CI가 돌고 diff가 남게 했다. 테스트 파일을 몰래 고치는 걸 막는 장치는 결국 **PR이라는 검문소**뿐이라, 이걸 빼면 설계 규칙 9(테스트 수정 금지)가 공중에 뜬다.

### 1-3. "병합은 나만"을 GitHub 설정으로 거는 법

main 룰셋에 approvals를 1로 두면 문제가 생긴다 — develop → main PR을 **내가 열면 내가 승인할 수 없어서** 팀원 승인이 필요해진다. 대신:

| 브랜치 | Require PR | approvals | status check | Restrict pushes |
| --- | --- | --- | --- | --- |
| develop | ○ | 0 | `build` | 없음 (누구나 자기 PR 머지) |
| main | ○ | 0 | `build` | **나만** |

PR 머지도 "push"로 취급되기 때문에, main에 push 제한을 나로 걸면 머지 버튼이 나한테만 활성화된다. approvals 없이도 "병합은 나만"이 된다.

### 1-4. 선행 테스트는 develop에 올리면 안 된다

설계 결정 D-080: 마스킹·지문·격리·권한 테스트는 내가 **먼저 실패하는 상태로** 쓰고, 담당자가 수정 없이 초록으로 만든다. 그런데 빨간 테스트를 develop에 올리면 그 순간부터 develop CI가 전부 빨강이라 다른 사람 PR도 못 올라간다.

그래서 develop에 안 올리고 **담당자 브랜치의 출발점**으로 준다.

```bash
# 나
git checkout -b test/AI-41-masker develop
# MaskerTest 커밋 → push (PR 안 올림)

# 담당자 C
git fetch origin
git checkout -b feat/starter-AI-41-masker origin/test/AI-41-masker
# 구현 → 초록 → develop PR
```

### 1-5. Jira와 연결하면 브랜치 이름이 규칙이 된다

Jira의 "GitHub for Atlassian" 앱(Atlassian 제공, 옛 이름 GitHub for Jira)으로 레포를 연결하면, 브랜치·커밋·PR에 이슈 키(`AI-36`)가 들어 있을 때 Jira 이슈 화면 "개발" 칸에 자동으로 붙는다. 그래서 브랜치 규칙에 이슈 키를 넣었다.

```
브랜치:  <타입>/<범위>-<이슈키>-<내용>     예) feat/starter-AI-36-event-buffer
커밋:    <타입>(<범위>): <요약> [<이슈키>]  예) feat(starter): BoundedEventBuffer 구현 [AI-36]
PR 제목: [AI-36] 버퍼 실구현
```

## 2. 추가로 알면 좋은 활용법

### 2-1. Windows에서 커밋한 gradlew는 실행 권한이 없다

첫 CI가 `./gradlew: Permission denied`로 죽었다. Windows는 파일 실행 권한 비트가 없어서 git이 644로 저장하고, Linux 러너가 실행하려니 거부된 것. 한 줄로 고친다.

```bash
git update-index --chmod=+x gradlew
git commit -m "ci(infra): gradlew 실행 권한 추가 [AI-5]"
```

한 번 커밋해 두면 이후로는 유지된다.

### 2-2. 머지 방식은 기본값(Create a merge commit)

원자적으로 나눈 커밋 22개가 그대로 develop 이력에 남게 하려고. Squash는 1개로 뭉개고 Rebase는 머지 지점이 안 남는다. 팀 가이드(`docs/team-guide-pr.md`)에도 "기본값 그대로"로 적어 뒀다.

### 2-3. 0단계 PR은 나도 똑같이 PR로

develop 보호 규칙이 켜진 뒤로는 나도 직접 push가 안 된다. 0단계 뼈대도 `chore/infra-AI-5-bootstrap` 브랜치 → PR #1 → CI 초록 → 셀프 머지로 올렸다. 규칙을 만든 사람이 먼저 예외가 되면 안 된다.

## 3. 더 나아가 알면 좋은 것

### 3-1. 다음에 볼 키워드

- Settings → General → **Automatically delete head branches** — 머지하면 GitHub가 브랜치를 알아서 지운다. 안 켜면 몇 주 뒤 브랜치 수십 개가 쌓인다
- 코드래빗(CodeRabbit) — 공개 레포는 무료. 붙이면 develop PR에 자동 리뷰가 달려서 "셀프 머지 전에 코멘트 확인"을 습관으로 둘 수 있다. `.coderabbit.yaml`에 한국어 리뷰·`CLAUDE.md` 기준·테스트 파일 변경 경고를 넣을 계획
- 2FA — GitHub가 11/24까지 요구. 팀 공용 레포라 이번 주에 켠다

### 3-2. 확인할 것

develop에 직접 `git push`를 시도해서 거부되는지 한 번 본다. 보호 규칙이 실제로 작동하는지는 거부당해 봐야 안다.

## 관련 노트

[[AiOps 02 - Gradle 멀티 모듈 뼈대]]
