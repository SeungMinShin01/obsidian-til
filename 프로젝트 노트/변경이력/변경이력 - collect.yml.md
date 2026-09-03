---
출처: Claude 대화
작성일: 2026-09-03
tags: [프로젝트노트, 수집기, Actions]
---

# 변경이력 - collect.yml

GitHub Actions 워크플로우 파일의 진화. **워크플로우는 코드가 아니라 코드를 실행하는 무대**라, 변화의 성격이 다르다 — 대개 "무엇을 언제 어떤 권한으로 돌릴지"가 바뀐다. 누적형.

## 변경 궤적

| 커밋 | 무엇 |
| --- | --- |
| first commit | 빈 파일 푸시 → Actions 실패 메일 |
| Actions 첫 워크플로우 | hello-cron 골격 |
| 실행기록을 저장소에 남기도록 | 커밋·푸시 step 추가 |
| 파이썬으로 실행 | run 명령 변경 |
| SQLite 저장 계층 | 커밋 대상에 state/ 추가 |
| MOEF_SERVICE_KEY 주입 | env 블록 추가 |

## 1. 빈 파일을 먼저 푸시한 사고

첫 시도에서 내용 없는 yml을 커밋·푸시했고 Actions가 바로 실패 메일을 보냈다. "저장 ≠ 커밋 ≠ 푸시"를 처음 겪은 계기. 워크플로우는 **푸시되는 순간 살아나서** 문법이 틀리면 바로 티가 난다.

## 2. hello-cron 골격 — 트리거·권한·step

```yaml
name: hello-cron
on:
  schedule:
    - cron: "0 0 * * *"
  workflow_dispatch:
permissions:
  contents: write
jobs:
  hello:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
      - run: python collector/main.py
```

이 골격의 각 부분이 「수집기 02·03·04」의 학습 대상이었다 — `on`(트리거), `permissions`(봇이 커밋하려면 write), `uses`(재사용 액션), `runs-on`(VM). **이름 `hello-cron`과 job `hello`가 지금까지 그대로다** — 첫 실험 흔적이 배포본에 남아 있다.

## 3. 커밋·푸시 step — 결과를 저장소에 남기기

```yaml
      - name: 커밋하고 푸시
        run: |
          git config user.name "github-actions[bot]"
          git add data/ state/
          git diff --staged --quiet || git commit -m "실행 기록 추가"
          git push
```

VM은 폐기되므로 결과를 저장소에 커밋해야 다음 실행이 이어받는다(「수집기 04」). `git diff --staged --quiet ||`는 **변화 없으면 커밋 안 함** — 정상적 무변화를 실패로 만들지 않기. 편집 중 이 step이 통째로 사라진 사고도 있었다(다른 step과 함께 지워짐).

## 4. 커밋 대상 확장 — data/에서 state/까지

SQLite가 `state/`에 생기면서 `git add data/`가 `git add data/ state/`로. **저장 계층이 늘면 커밋 대상도 늘어야** VM 사이로 DB가 이어진다. 이걸 빠뜨리면 매 실행 빈 DB로 시작한다.

## 5. env 블록 — Secret 주입

12일 공백을 겪고 추가된, 이 파일의 가장 중요한 한 조각.

```yaml
      - name: 수집기 실행
        run: python collector/main.py
        env:
          MOEF_SERVICE_KEY: ${{ secrets.MOEF_SERVICE_KEY }}
```

파일엔 **키가 아니라 키 이름만** 적힌다(「수집기 22」). `env:`는 쓰는 step에만 — checkout·push는 키가 필요 없다. Secret 등록과 이 블록은 **별개 단계**라, 하나만 있으면 KeyError나 빈 문자열 403이 난다.

## 관찰

### 코드가 아니라 "실행 조건"이 바뀐다

main.py는 책임이 옮겨갔지만, collect.yml은 **무엇을 언제 어떤 권한·환경으로 돌릴지**가 바뀐다. 변경의 축이 다르다.

| main.py | collect.yml |
| --- | --- |
| 로직·책임 분할 | 트리거·권한·환경·커밋대상 |

### 이 파일은 원격 도구가 못 고친다

워크플로우 파일은 세션이 읽어서 검사만 하고, 편집은 사용자가 한다(권한 경계). 그래서 변경마다 "저장 → 세션이 yml 검사(탭·파싱·step 목록) → 커밋"의 리듬이 붙는다.

### 아직 안 바꾼 것들

- 이름 `hello-cron` / job `hello` — 첫 실험 그대로. 정리 대상
- cron `0 0 * * *` — 하루 1회. 「수집기 16」에서 하루 5회로 바꾸기로 했으나 **아직 반영 안 됨**. 예약 지연(최대 10시간)도 여기서 다뤄야 함
- `concurrency` 블록 — 빈도 올리면 동시 실행 방지 필요
- jumpit 붙었으니 실행 시간 증가 — timeout-minutes 고려
