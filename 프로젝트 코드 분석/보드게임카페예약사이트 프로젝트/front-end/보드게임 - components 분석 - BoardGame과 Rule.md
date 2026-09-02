---
출처: Claude 분석
원본: shirhal/front-end/src/components
작성일: 2026-08-11
tags: [프로젝트, javascript]
---

# components 분석 - BoardGame과 Rule

대상: `BoardGame/BoardGameList.js` · `BoardGame/BoardGameDetail.js` · `BoardGame/ReviewSection.js` · `Rule/rule.js` · `Rule/RuleDetailModal.js` · `pages/rulepages.js`
상위: [[보드게임카페예약사이트 프로젝트 MOC]]

## BoardGameList — 목록 화면

로직은 전부 `useBoardGameList`( → [[보드게임 - hooks 분석|hooks 분석]] )에서 받고, 이 파일은 카드 그리드 렌더링과 검색창·필터 UI만 맡는다. **컨테이너(훅)/프레젠테이션(컴포넌트) 분리**가 가장 잘 지켜진 화면이다.

하나 어긋난 게 있다 — 훅 안에 무한 스크롤 리스너가 있는데, **컴포넌트에도 스크롤 리스너가 하나 더 붙어 있다.** 훅으로 로직을 옮기는 리팩토링을 하면서 옛 코드를 지우지 않은 흔적이다.

> **피드백** — 리스너가 두 개면 페이지 요청이 두 번 나갈 수 있다 — 목록 중복 표시의 유력한 원인이고, 백엔드에서 `DISTINCT *`라는 대증요법( → [[routes 분석 - 보드게임과 리뷰]] )이 생긴 배경일 것이다. 원인(중복 리스너)과 증상(중복 표시)이 프론트-백 양쪽에 남은 사례라, "옮겼으면 지운다"를 리팩토링의 마지막 단계로 못 박는 계기가 됐다.

## BoardGameDetail — 상세 패널

```javascript
export default function BoardGameDetail({ userId, game, onClose }) {
```

**자체 fetch가 없다.** 목록이 이미 가진 `game` 객체를 props로 받아 그대로 그린다. 목록 → 상세로 넘어갈 때 재요청이 없어 빠르고, 이 컴포넌트는 순수하게 **프레젠테이션 컴포넌트**다. 리뷰 영역만 `ReviewSection`을 끼워 넣는다.

> **피드백** — 목록 데이터 재사용은 좋은데, 상세에서만 필요한 무거운 필드(긴 설명 등)까지 목록 API가 전부 내려주고 있다는 뜻이기도 하다. 목록은 카드용 필드만, 상세는 진입 시 1회 fetch로 나누는 게 데이터가 커졌을 때의 방향이다. URL로 직접 진입(`/games/123`)하는 경우가 생기면 어차피 상세 fetch가 필요해진다.

## ReviewSection — 리뷰 CRUD

`useBoardGameReview` 훅에서 리뷰 목록·내 리뷰·등록·삭제를 받아 그린다. 100자 제한을 프론트에서 검사하고, 등록/수정을 같은 폼으로 처리한다.

> **피드백** — 글자 수 제한이 프론트에만 있다. API를 직접 치면 10,000자도 들어간다. 프론트 검사는 UX용, **최종 검증은 서버와 DB(`VARCHAR(100)`)**라는 이중화가 원칙이다. → SQL day02 테이블과 제약조건

## Rule 계열 — 규칙 열람

```
rule.js (목록)  →  rulepages.js (개별 규칙 페이지)  →  RuleDetailModal (이미지 확대)
                         └ useRuleData → fetch("/data/rules.json")
```

게임 규칙만은 DB가 아니라 **정적 JSON**이다. 크롤링한 게임 정보와 달리 규칙은 직접 썼고, 이미지가 섞인 긴 문서라 테이블 스키마에 맞추기 애매했을 것이다. 데이터 성격에 따라 저장소를 다르게 고른 판단이다.

`rule.js`에는 데이터 로딩 전에 클릭하면 `alert("잠시만 기다려주세요...")`를 띄우는 처리가 있다.

> **피드백** — alert 대신 로딩 상태로 버튼을 비활성화하는 게 요즘 방식이다. alert는 흐름을 끊고, 연타하면 계속 뜬다. `isLoading ? <Spinner/> : <목록/>` 조건부 렌더링이 같은 문제의 표준 해법. 그리고 `rules.json`의 이미지 경로가 `"a.jpg,b.png, ,c.png"`처럼 쉼표 문자열이라 파싱 코드에 빈 항목 방어가 필요해졌다 — 처음부터 배열로 저장했으면 방어 코드가 필요 없었다. **데이터 구조를 잘 고르면 코드가 준다.**

## 관련 노트

[[보드게임카페예약사이트 프로젝트 MOC]] · [[보드게임 - hooks 분석|hooks 분석]] · [[routes 분석 - 보드게임과 리뷰]] · [[보드게임 - data와 styles 분석|data와 styles 분석]] · [[보드게임 - 전문용어 정리|전문용어 정리]]
