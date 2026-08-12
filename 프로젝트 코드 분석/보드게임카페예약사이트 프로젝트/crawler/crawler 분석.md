---
출처: Claude 분석
원본: shirhal/back-end/crawler
작성일: 2026-08-11
tags: [프로젝트, 일지, 보드게임카페예약사이트, python, 크롤링]
---

# crawler 분석

대상: `crawler/redbutton.py` · `crawler/processCrawledData.js`
상위: [[보드게임카페예약사이트 프로젝트 MOC]]

보드게임 데이터를 손으로 입력하지 않으려고 만든 수집 파이프라인이다. 이 프로젝트에서 유일하게 Python이 들어간 구간이기도 하다.

## 파이프라인 구조

```
redbutton.py (Selenium)  →  boardgames.json  →  processCrawledData.js  →  MySQL
     수집                      중간 저장소            정제 + 적재
```

수집과 적재를 한 프로그램으로 안 만들고 **JSON 파일을 중간에 뒀다.** 적재 로직을 고칠 때마다 크롤링을 다시 돌릴 필요가 없다 — 크롤링 1회, 적재 N회. 크롤링이 분 단위로 걸리는 작업이라 이 분리의 효과가 컸다.

## redbutton.py — 수집

레드버튼 사이트를 **Selenium** 헤드리스로 열고, 페이지네이션을 돌면서 게임 이름·난이도·인원·시간을 긁는다. 정적 요청(requests)이 아니라 브라우저 자동화를 쓴 건 대상 페이지가 JS 렌더링이기 때문이다.

```python
# 재실행해도 중복이 쌓이지 않는다
merged = {g["name_kr"]: g for g in existing + game_list}
result = list(merged.values())
```

기존 JSON을 읽어서 `name_kr`을 키로 dict에 합친다. 같은 게임은 새 데이터로 덮이고, 몇 번을 돌려도 결과가 같다 — **멱등성**을 수집 단계부터 확보했다.

> **피드백** — 방향은 맞고, 두 가지가 더 있었으면 견고했다.
> ① **셀렉터 상수화.** CSS 셀렉터가 코드 곳곳에 문자열로 박혀 있어서 대상 사이트가 개편되면 수정 지점을 찾아다녀야 한다. 상단에 상수로 모으면 개편 대응이 한 곳으로 줄어든다.
> ② **실패 내성.** 페이지 하나가 타임아웃 나면 전체가 죽는다. 페이지 단위 try-except로 "실패한 페이지만 기록하고 계속"이 크롤러의 기본 자세다. robots.txt와 요청 간격 같은 크롤링 예절도 코드에 명시돼 있으면 좋았다.

## processCrawledData.js — 정제와 적재

```javascript
const difficultyMapping = { "very easy": "매우쉬움", easy: "쉬움", normal: "보통", ... };
const estimatedTime = game.play_time
  ? `${parseInt(game.play_time.replace("분", "").trim())}분` : null;
```

외부 표현(영어 난이도, 제각각인 시간 표기)을 서비스 내부 표현으로 바꾸는 **정제 경계**를 여기에 세웠다. 이 파일을 지나면 서비스 어디에서도 `very easy` 같은 외부 값이 보이지 않는다.

적재는 **업서트**다.

```sql
INSERT INTO board_game (...) VALUES (...)
ON DUPLICATE KEY UPDATE game_name_kr = VALUES(game_name_kr), ...
```

있으면 갱신, 없으면 삽입. 수집 단계의 dict 병합과 합쳐서 **파이프라인 전체가 멱등**이다. 실패하면 그냥 다시 돌리면 되는 구조 — 배치 작업 설계에서 가장 중요한 성질을 양쪽 끝에서 지켰다.

여기서는 `dotenv`도 제대로 썼다(`require("dotenv").config()`). 본체 `config/db.js`는 하드코딩인데 크롤러만 환경변수를 쓰는 비대칭이 남았다.

> **피드백** — 이 파이프라인은 사실상 **ETL**(Extract-Transform-Load)의 축소판이다. 다음에 같은 걸 만들면: 수집 로그(몇 건 수집·몇 건 갱신·몇 건 실패)를 남기고, 크롤링 일시를 컬럼으로 저장해서 "언제 데이터인지"를 추적 가능하게 만드는 것까지가 한 세트다. 루트에 굴러다니는 `boardgames.json` · `search_result.html`(195KB) 같은 중간 산출물은 `.gitignore`로 저장소 밖에 뒀어야 했다.

## 관련 노트

[[보드게임카페예약사이트 프로젝트 MOC]] · [[routes 분석 - 보드게임과 리뷰]] · [[전문용어 정리]]
