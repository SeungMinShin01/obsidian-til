---
출처: Claude 대화
작성일: 2026-08-12
tags: [프로젝트노트, 수집기, GitHub-Actions, YAML]
---

# 수집기 - YAML과 워크플로우 파일

> 허브: [[수집기 프로젝트 MOC]]

## 1. 배운 내용

### 1-1. 왜 스크립트가 아니라 설정 파일인가

Actions는 워크플로우 파일을 실행하지 않고 읽는다. 리포에 푸시가 들어오면 GitHub 서버가 이 파일을 먼저 파싱해서 매일 0시에 돌릴 일정과 수동 실행 버튼을 미리 등록한다. 실제 실행은 그 다음이다.

그래서 이 파일은 명령이 아니라 언제·어디서·무엇을 할지 적어둔 신청서에 가깝다. 데이터여야 하므로 프로그래밍 언어가 아닌 데이터 형식을 쓴다.

### 1-2. 왜 하필 YAML인가

데이터 형식이라면 JSON도 된다. YAML은 JSON을 포함하는 상위 형식이라 JSON을 그대로 넣어도 유효하다. 그런데 설정 파일 용도로는 JSON이 불편하다.

- 주석을 못 쓴다. JSON 문법에는 주석이 없다. 설정 파일에서 이 줄을 왜 이렇게 했는지 못 적는 것은 치명적이다.
- 중괄호·따옴표·콤마가 많아 손으로 쓰다 실수하기 쉽다.

YAML은 그 불편을 덜어낸 형식이다. `#`로 주석을 달 수 있고, 중괄호 대신 들여쓰기로 구조를 표현한다.

### 1-3. 문법은 세 가지

| 문법 | 의미 | 예 |
| --- | --- | --- |
| `키: 값` | 하나의 속성 (JS 객체의 프로퍼티) | `name: hello-cron` |
| `- 항목` | 목록의 한 개 (JS 배열의 요소) | `- cron: "0 0 * * *"` |
| 들여쓰기 | 포함 관계 (누구의 자식인지) | 안쪽으로 들어갈수록 자식 |

처음 만든 워크플로우 파일은 이렇게 생겼다.

```yaml
name: hello-cron

on:
  schedule:
    - cron: "0 0 * * *"
  workflow_dispatch:

jobs:
  hello:
    runs-on: ubuntu-latest
    steps:
      - name: Say hello
        run: echo "Hello from Actions, $(date)"
```

같은 내용을 JSON으로 바꿔 쓰면 구조가 그대로 드러난다.

```json
{
  "name": "hello-cron",
  "on": {
    "schedule": [
      { "cron": "0 0 * * *" }
    ],
    "workflow_dispatch": null
  },
  "jobs": {
    "hello": {
      "runs-on": "ubuntu-latest",
      "steps": [
        { "name": "Say hello", "run": "echo \"Hello from Actions, $(date)\"" }
      ]
    }
  }
}
```

`schedule` 밑에 `-`가 붙는 이유는 스케줄을 여러 개 걸 수 있어서다. `steps`도 단계가 여러 개라 `-`가 붙는다. 둘 다 배열이다.

`workflow_dispatch:` 뒤에 아무것도 없는 것은 값이 비어 있는 키다. 수동 실행 기능을 켜는 스위치라 별도 설정값이 필요 없다.

### 1-4. YAML 문법과 키 이름은 다른 층이다

YAML은 그릇일 뿐이고, `name`·`on`·`jobs`·`runs-on` 같은 키 이름은 GitHub Actions가 정한 규격이다.

- `키: 값`, `- 목록`, 들여쓰기 → YAML의 규칙, 어디서든 동일하다
- `jobs` 안에는 `steps`가 있어야 한다 → Actions의 규칙, GitHub 문서를 봐야 아는 것이다

YAML 문법을 다 안다고 워크플로우를 쓸 수 있는 것이 아니고, 반대로 Actions 키를 외웠다고 YAML을 아는 것도 아니다. Docker Compose도 YAML을 쓰지만 키 이름은 완전히 다르다.

## 2. 추가로 알면 좋은 활용법

### 2-1. 자주 밟는 함정

- 탭은 쓸 수 없다. 스페이스만 쓴다. 붙여넣기 과정에서 탭이 섞이면 파싱이 깨진다.
- 콜론 뒤에는 공백이 필요하다. `name:hello`는 안 되고 `name: hello`가 맞다.
- 들여쓰기 칸 수는 자유지만 같은 층끼리는 반드시 같아야 한다.
- `.yml`과 `.yaml`은 완전히 같다. GitHub은 둘 다 인식하고, 관례로 짧은 쪽을 쓴다.

### 2-2. 파일 위치도 규칙이다

워크플로우 파일은 `.github/workflows/` 안에 있어야 Actions가 인식한다. 경로가 다르면 문법이 맞아도 아무 일도 일어나지 않는다. 윈도우 탐색기에서는 `.`으로 시작하는 폴더를 만들기 까다로워서 `mkdir .github\workflows`처럼 명령으로 만들거나 편집기 안에서 만드는 편이 편하다.

## 3. 더 나아가 알면 좋은 것

### 3-1. 다음에 볼 키워드

- GitHub Actions 워크플로우 문법 문서 — `jobs`·`steps` 외에 쓸 수 있는 키
- `uses` — 남이 만들어 둔 액션을 가져다 쓰는 방법
- YAML 앵커(`&`, `*`) — 중복되는 설정 묶기
- Docker Compose의 YAML — 같은 문법에 다른 키가 어떻게 쓰이는지

## 관련 노트

[[수집기 프로젝트 MOC]] · [[수집기 - 리포를 Private으로 정한 이유]]
