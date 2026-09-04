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
| 하루 2회로 증설 | cron 두 줄 (09:00 · 18:00 KST) |

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

## 6. cron 두 줄 — 하루 1회에서 2회로

```yaml
on:
  schedule:
    # GitHub Actions cron은 UTC 고정 — KST = UTC+9
    - cron: "0 0 * * *"   # 09:00 KST
    - cron: "0 9 * * *"   # 18:00 KST — 사이트 실제 갱신(12~13시)을 당일에 수집
  workflow_dispatch:
```

`schedule:`은 매핑의 시퀀스라 `- cron:` 줄을 늘리면 그만큼 실행이 는다. 새 키가 아니라 **리스트 원소 추가**다.

시각 계산은 UTC 고정이 전부다. Actions는 타임존 설정이 없어 KST에서 9를 뺀다 — 09:00 KST가 `0 0`, 18:00 KST가 `0 9`. 지금까지 `0 0`이 09시에 돌던 이유도 이것이었고, 이 파일에서 유일하게 틀리기 쉬운 자리라 주석을 같이 남겼다.

**고친 것은 빈도가 아니라 위상이다.** 사이트 실제 갱신은 12~13시인데 09시 1회 체제는 그날 것을 다음날 받는 구조였다(「수집기 22」 이후 기록된 근거 어긋남). 18시 한 줄이 그 1일 지연을 없앤다. 「수집기 16」에서 정한 하루 5회에는 못 미치므로 그 결정과의 간극은 남는다 — 2회는 부분 이행이다.

`0분`은 전 세계 워크플로우가 몰리는 자리라 지연이 크다. 실행 시각 자체를 관측 기준선으로 쓰게 되면 `"7 0"`·`"7 9"`처럼 비켜두는 편이 낫다. 지금은 늦어도 무방해서 정각으로 뒀다.

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
- cron — 하루 2회까지 왔다. 「수집기 16」의 **하루 5회 결정과는 아직 3회 차이**. 예약 지연도 여기서 다뤄야 함
- `concurrency` 블록 — 2회는 9시간 간격이라 겹칠 일이 없지만, 5회로 올리면 필요해진다
- jumpit 붙었으니 실행 시간 증가 — timeout-minutes 고려
