---
출처: Claude 대화
작성일: 2026-09-03
tags: [프로젝트노트, 수집기, git]
---

# 트러블슈팅 - git·환경

git·환경설정에서 터진 것들. 증상별로 쌓는다.

---

## `! [rejected] main -> main (fetch first / non-fast-forward)`

**증상** push가 거부됨.

**원인** 봇(`github-actions[bot]`)이 매일 원격에 커밋하므로 **로컬이 늘 뒤처진다.** 가만히 둬도 갈라진다.

**조치** `git pull` 후 다시 push. 「수집기 09」의 "작업 전에 git pull".

---

## `Merge conflict in data/run-log.md`

**증상** pull 하니 run-log에서 충돌.

**원인** 로컬(실험하며 붙인 줄)과 봇(아침 실행 줄)이 **같은 파일 끝에** 각자 줄을 쌓아 git이 자동 병합 못 함.

**조치** 로그는 양쪽 다 진실이므로 **「두 변경 사항 모두 수락」** → `git add` → commit. 시간순 조금 섞여도 무방.

---

## `Your local changes would be overwritten by merge` — 그런데 diff가 없다

**증상** pull이 막히는데, 확인해보면 내용은 같음. `14 files changed, 463 insertions, 463 deletions`처럼 **추가=삭제 줄 수가 같음**.

**원인** 줄바꿈 문자 차이. VS Code(윈도우)는 CRLF, 봇(리눅스)은 LF로 저장 → git이 "모든 줄이 바뀌었다"로 봄. `core.autocrlf` 미설정이 원인.

**조치**
- 확인: `git diff -w --ignore-cr-at-eol --stat` — 비면 줄바꿈뿐
- 버려도 되면(줄바꿈뿐, 재생성되는 폴더): `git stash → git pull → git stash drop`
- 근본 해결: `git config core.autocrlf true` (저장소엔 LF, 체크아웃 시 CRLF)

**재발 방지** autocrlf true 설정 후엔 안 생김. 이후 "LF will be replaced by CRLF" 경고는 정상 동작.

---

## `.git/index.lock` — 이후 모든 git 명령이 막힘

**증상** git 명령이 lock 파일 때문에 안 됨.

**원인** 원격 도구(device_bash)로 `git status` 등 **인덱스를 갱신하는 명령**을 돌렸다가 비정상 종료. 그 통로는 삭제 권한이 없어 lock이 남음.

**조치** `del .git\index.lock` 후 재시도.

**재발 방지** 원격 통로에선 **읽기 전용 git만**(`git show`·`log`·`diff --stat`). 인덱스 갱신 명령은 사용자 터미널에서. 이건 SQLite `disk I/O error`, writer 폴더 비우기 실패와 **같은 뿌리** — 삭제가 막힌 곳에서 "만들고 지우는 도구"는 다 같은 방식으로 실패한다.

---

## `SERVICE_KEY_IS_NOT_REGISTERED_ERROR` (403) — 미리보기는 되는데 코드는 안 됨

**증상** 포털 미리보기 버튼은 데이터가 나오는데, 코드로 부르면 403.

**원인** 인증키 두 형태 중 잘못 넣음. 코드는 키를 `urlencode` 밖에 그대로 붙이므로 **Encoding 키(%포함)**여야 하는데, Decoding 키(+·= 형태)를 넣으면 서버가 다른 값으로 받음. `.env`로 옮기며 또 틀렸다.

**조치** Encoding 키(94자, %포함)로 교체. 노출 없이 확인: `키 길이 · %포함 · +포함`만 출력해 형태 판별.

**재발 방지** 미리보기 성공 + 코드 실패 = 승인·주소는 정상, **키 형식 문제**로 범위 좁힘. `_call`에 `if "%" not in key: raise` 가드 — 빈 문자열·Decoding 키를 호출 전에 잡음.
