---
출처: Claude 분석
작성일: 2026-08-10
tags: [규칙]
---

# Node.js Sync Engine 명세

옵시디언 Vault를 노션 Master DB로 미러링하는 엔진의 사양입니다.
설정값은 [[옵시디언-노션-VSCode 운영 규칙]] 과 같은 폴더의 `sync-config.json`에 있습니다.

## 1. 역할 경계

```
VS Code (읽기 전용)
   ↓ 분석
Claude          ← 노트를 쓰는 주체. 노션에 직접 개입하지 않음
   ↓ 작성
Obsidian Vault  ← 원본 (Single Source of Truth)
   ↓ 미러링
Node.js Sync Engine   ← 이 문서의 대상
   ↓
Notion Master DB
```

**최초 구축 이후 Claude는 노션 미러링에 관여하지 않습니다.** Claude의 역할은 VSCode 분석 → 옵시디언 노트 작성까지입니다.

## 2. 노션 식별자

| 항목 | ID |
| --- | --- |
| Workspace | `9448757f-e8c0-8119-882d-00037437461c` |
| 루트 페이지 (정리본) | `06c8757f-e8c0-83f5-add9-81ec640a0110` |
| Knowledge Base 페이지 | `3b88757f-e8c0-8114-abc8-c68e5fc39c96` |
| Dashboard 페이지 | `3b88757f-e8c0-8125-ac5f-ca3e455add7d` |
| **Master Database** | `20b7904a-3fc9-4c69-a46f-fdc5c3bf5c70` |
| **Master Data Source** | `afbff551-7b01-4549-a32b-108cd46bba88` |

`.env`
```
NOTION_TOKEN=secret_xxxxxxxx
VAULT_PATH=C:/Users/harry/Desktop/옵시디언/Vault
```

## 3. Property 매핑

| Notion | 타입 | 출처 | 비고 |
| --- | --- | --- | --- |
| Title | title | 파일명(확장자 제외) | |
| Category | select | Vault 최상위 폴더명 | `categoryMap` 참조 |
| Type | select | 파일명 규칙 | `typeRules` 참조 |
| Source | select | `frontmatter.출처` | |
| Day | number | 파일명의 `day\d{1,2}` | 없으면 빈값 |
| Repo | select | `frontmatter.원본`의 최상위 | |
| Tags | multi_select | `frontmatter.tags` | |
| **VaultPath** | rich_text | Vault 기준 상대경로 | **기본키** |
| SourcePath | rich_text | `frontmatter.원본` | |
| FileHash | rich_text | `sha256(본문)` | 변경 감지 |
| Status | select | **사용자 수동** | Sync가 절대 덮어쓰지 않음 |
| SyncedAt | date | 실행 시각 | |
| WordCount | number | 본문 길이 | |
| Related / Backlinks | relation | 위키링크 | 2-pass에서 연결 |

## 4. Type 판정 규칙 (위에서부터 우선)

| 조건 | Type |
| --- | --- |
| 파일명이 ` MOC`로 끝남 | MOC |
| 파일명이 `(이관)`으로 끝남 | 이관 |
| 파일명에 `인덱스` 포함 | 인덱스 |
| 파일명에 `규칙` 포함 | 규칙 |
| 파일명에 `day00`~`day99` 포함 | 학습노트 |
| 그 외 | 심화 |

## 5. Category 매핑

| Vault 폴더 | Notion Category |
| --- | --- |
| `Java/` | Java |
| `JavaScript/` | JavaScript |
| `HTML/` | HTML |
| `CSS/` | CSS |
| `Python/` | Python |
| `RPA/` | RPA |
| `AI/` | AI |
| `CS 이론/` | CS 이론 |
| `프로젝트 코드 분석/` | 프로젝트 |
| `_규칙/`, Vault 루트 | 운영 |

## 6. 동기화 알고리즘

```
1. Vault 스캔
   - include: **/*.md
   - exclude: .obsidian/**, _템플릿/**, sync-config.json

2. 각 파일 파싱
   - frontmatter 분리 (--- 사이)
   - 본문 첫 # H1 제거 (노션 페이지 제목과 중복)
   - sha256(본문) 계산
   - 위키링크 수집

3. 노션 Master DB 조회
   - VaultPath로 기존 페이지 매칭

4. 분기
   - 없음        → 페이지 생성
   - FileHash 동일 → 건너뜀
   - FileHash 다름 → 본문 replace + 속성 갱신 (Status 제외)
   - Vault에 없음  → 아카이브 (삭제 아님)

5. 2-pass: Related 관계 연결
   - 1-pass에서 확보한 (Title → pageId) 맵으로
     위키링크를 relation으로 변환
   - 해석 안 되는 링크는 평문 유지

6. 상태 저장
   - .sync-state.json 에 { vaultPath: { pageId, hash, syncedAt } }
```

## 7. 마크다운 → 노션 변환 주의

| 항목 | 처리 |
| --- | --- |
| frontmatter | 제거 후 속성으로 |
| 최상단 `# 제목` | 제거 (페이지 제목과 중복) |
| 파이프 테이블 | 그대로 전달하면 노션이 변환 |
| 코드 블록 | 언어 미지정 시 `plain text` |
| 위키링크 | 2-pass에서 mention으로, 실패 시 평문 |
| 인용문 `>` | 그대로 |
| 페이로드 크기 | **요청당 10KB 이하로 분할** |
| 블록 수 | 요청당 100개 이하 |

## 8. 안전장치

- **방향은 단방향(옵시디언 → 노션)입니다.** 역방향 동기화 없음
- `Status`는 사용자 전용 속성 — 절대 덮어쓰지 않음
- Vault에서 지운 노트는 **아카이브만** 하고 삭제하지 않음
- 노션에서 사용자가 본문을 직접 고친 흔적이 있으면 **덮어쓰지 말고 로그로 보고**
- `Programmars` 페이지는 동기화 대상에서 제외
- API 레이트리밋: 3 req/s, 실패 시 지수 백오프 5회

## 9. 실행

구현체 위치: `C:\Users\harry\Desktop\옵시디언\sync-engine` (Vault 바깥이라 동기화 대상 아님)

```bash
node selftest.js "<Vault경로>"   # 의존성·토큰 없이 파싱·변환 검증
npm run dry                      # 쓰기 없이 계획만
npm run sync                     # 변경분만
npm run full                     # 전체 재동기화
npm run watch                    # 매일 10시 자동 실행
```

**첫 실행 순서**: `selftest` → `dry` → `sync`

권장 스케줄: 매일 오전 10시 (KST). Windows 작업 스케줄러 또는 `node-cron`(`schedule.js`).

### 검증 결과 (2026-08-10)

| 항목 | 값 |
| --- | --- |
| 노트 | 53개 |
| 변환 블록 | 3,036개 (최대 111개/노트) |
| 요청 청크 | 56건 |
| 표 / 코드블록 | 119개 / 669개 |
| 위키링크 | 424개, 해석 실패 0 |
| rich_text 2000자 초과 | 0 |
| Category·Type·출처 판정 실패 | 0 |

## 10. 필요한 패키지

```json
{
  "dependencies": {
    "@notionhq/client": "^2.2.15",
    "gray-matter": "^4.0.3",
    "@tryfabric/martian": "^1.2.4",
    "fast-glob": "^3.3.2",
    "dotenv": "^16.4.5",
    "node-cron": "^3.0.3"
  }
}
```

- `gray-matter` — frontmatter 파싱
- `@tryfabric/martian` — 마크다운 → 노션 블록 변환 (테이블·코드블록 지원)
- `fast-glob` — Vault 스캔

## 관련 노트

[[옵시디언-노션-VSCode 운영 규칙]] · [[Vault 홈]]
