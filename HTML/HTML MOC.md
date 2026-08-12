---
출처: Claude 분석
작성일: 2026-08-10
tags: [html, MOC, 허브]
---

# HTML MOC

HTML 관련 노트의 허브입니다. 상위 지도는 [[KDT_2026 학습 지도]].
실제 프로젝트에서 이 주제가 쓰인 지점은 [[KDT_2026 학습 지도]]의 **프로젝트 매핑표**에서 찾습니다 (프로젝트 분석 노트와 직접 링크하지 않습니다).

## 프로젝트 매핑 — 학습 지도 ↔ 이 폴더

[[KDT_2026 학습 지도]]를 거쳐 들어온 경우, 프로젝트의 해당 주제는 이 노트들과 닿습니다. (프로젝트 쪽은 평문 — 직접 링크하지 않음)

| 프로젝트에서 만난 것 | 이 폴더의 이론 |
| --- | --- |
| 예약 폼 마크업 — label·placeholder·name 속성 | [[HTML day04 폼과 테이블]] |
| 표준 속성과 DOM 경고 (transient prop의 배경) | [[HTML day02 문서 구조와 미디어]] |
| 목록·표 데이터 마크업 | [[HTML day15 테이블 마크업]] |


| day | 노트 | 핵심 |
| --- | --- | --- |
| 02 | [[HTML day02 문서 구조와 미디어]] | 문서 골격, 텍스트·링크·이미지, 미디어 태그 |
| 04 | [[HTML day04 폼과 테이블]] | input 8종·속성 13개, table·colspan·rowspan |
| 15 | [[HTML day15 테이블 마크업]] | thead/tbody/tfoot, 시맨틱 구조 |

## 함께 쓰는 언어

- [[CSS MOC]] — HTML을 꾸미는 것
- [[JavaScript MOC]] — HTML을 조작하는 것

HTML 관련 정리는 `day04/exam/exam.txt`(입력 요소)와 `day08/exam/CSS.txt` 앞부분에 담겨 있습니다.

## HTML → CSS → JS 연결 고리

```
HTML  <div class="box" id="main">
        │              │        └── JS: document.querySelector("#main")
        │              └─────────── CSS: .box { }
        └────────────────────────── 뼈대
```

**CSS 선택자 문법을 그대로 JS가 씁니다.** [[CSS day06 선택자와 기본 속성]] 에서 배운 게 [[JS day11 DOM 조작]] 에서 그대로 쓰입니다.

| HTML 태그 | JS 속성 | 이유 |
| --- | --- | --- |
| `<div>` `<td>` `<p>` | `.innerHTML` | 닫는 태그 "사이"가 있음 |
| `<input>` `<select>` `<textarea>` | `.value` | 닫는 태그가 없음 |
| `<img>` | `.src` | 경로 속성 |
