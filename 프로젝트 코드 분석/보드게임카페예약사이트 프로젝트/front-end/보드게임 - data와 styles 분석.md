---
출처: Claude 분석
원본: shirhal/front-end/src
작성일: 2026-08-11
tags: [프로젝트, javascript]
---

# data와 styles 분석

대상: `data/` 4개 · `public/data/rules.json` · `styles/GlobalStyle.js`
상위: [[보드게임카페예약사이트 프로젝트 MOC]]

## data/ — 코드에서 분리한 정적 데이터

| 파일 | 내용 | 소비처 |
| --- | --- | --- |
| `NavmenuData.js` | 서브메뉴 구조 (`subMenus` 객체) | NavBar |
| `menuData.js` | 음료 메뉴 185줄 (커피/논커피/티) | Beverage |
| `storeData.js` | 매장 정보 — 좌표·주소·전화·영업시간·이미지 | store(카카오맵) |
| `summaryData.js` | 게임 요약 규칙 텍스트 | rulepages |

바뀔 수 있는 내용(메뉴·매장·규칙)을 JSX에서 꺼내 데이터 파일로 뒀다. 메뉴 하나 추가가 컴포넌트 수정 없이 끝나는 **데이터 주도 설계**다. `storeData`의 좌표(`lat`/`lng`)가 지도 렌더링의 단일 출처가 되는 것도 이 구조 덕분이다.

## public/data/rules.json — 번들 밖의 데이터

규칙 데이터만 `src/`가 아니라 `public/`에 있다. 차이는 로드 방식이다.

```
src/data/*.js      → import  → 번들에 포함, 빌드 시 고정
public/data/*.json → fetch   → 런타임 로드, 번들 크기와 무관
```

규칙 데이터는 크고(이미지 경로 다수) 화면 몇 곳에서만 쓰니, 초기 번들에서 빼고 필요할 때 가져오는 선택을 했다. **정적 import vs 런타임 fetch**를 데이터 크기·사용 빈도로 갈랐던 것.

> **피드백** — 방향은 맞는데 JSON 내부 구조가 아쉽다.
>
> ```json
> "image": "/images/splender.jpg,/images/rules/splender1.png, ,/images/rules/splender6.png, , ,..."
> ```
>
> 이미지 목록이 **쉼표 이어붙인 문자열**이고 빈 항목까지 섞여 있다. 소비 코드마다 `split(",")` + 공백 필터가 필요해졌다. 처음부터 배열 `["a.jpg", "b.png"]`였으면 그 코드가 전부 사라진다. 크롤러 파이프라인에서 배운 것과 같은 교훈 — **경계에서 데이터 모양을 바로잡으면 안쪽 코드가 준다.** 데이터가 더 커지면 이 JSON도 DB로 옮기고 규칙 편집 화면을 만드는 게 자연스러운 다음 단계다.

## summaryData.js — 구조가 내용을 못 담는 예

```javascript
스플렌더: [
  "1. 개발 카드별로 섞어서...",
  "a. 서로 다른 색의 보석 토큰 3개 가져가기.",
  "(이 액션은 ... 가능합니다.)",
]
```

번호·소항목·괄호 주석이 전부 **평평한 문자열 배열**에 들어 있다. 렌더링할 때 계층(1 → a → 주석)을 살릴 방법이 없어서 그냥 줄줄이 출력된다.

> **피드백** — 내용에 계층이 있으면 데이터에도 계층이 있어야 한다. `{ step: "...", subItems: [...], note: "..." }` 구조였다면 화면에서 들여쓰기·스타일을 제대로 입힐 수 있었다. 데이터 구조 설계는 "어떻게 저장하나"가 아니라 "어떻게 소비되나"에서 출발한다는 걸 보여주는 파일이다.

## styles/GlobalStyle.js

`createGlobalStyle` 리셋 + Pretendard 웹폰트. 상세는 [[보드게임 - App과 공통 레이아웃 분석|App과 공통 레이아웃 분석]] 에 적었다 — 요약하면 전역/지역 경계는 명확하나, 디자인 토큰(색·간격)이 없어서 스타일 값이 컴포넌트마다 흩어졌다.

## 관련 노트

[[보드게임카페예약사이트 프로젝트 MOC]] · [[보드게임 - App과 공통 레이아웃 분석|App과 공통 레이아웃 분석]] · [[보드게임 - components 분석 - BoardGame과 Rule|components 분석 - BoardGame과 Rule]] · [[보드게임 - crawler 분석|crawler 분석]] · [[보드게임 - 전문용어 정리|전문용어 정리]]
