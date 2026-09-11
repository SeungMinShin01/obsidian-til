---
출처: Claude 분석
작성일: 2026-09-11
tags: [허브, react]
---

# React MOC

React 학습노트의 허브입니다. 상위 지도는 [[KDT_2026 학습 지도]]. (JavaScript에서 분리 — 원본 코드: `KDT_2026/2026_React`, Vite 프로젝트 `src/example/dayNN`)

## 학습 순서

[[React day01 컴포넌트와 렌더링]]

## 노트

| 노트 | 핵심 |
| --- | --- |
| [[React day01 컴포넌트와 렌더링]] | Vite 프로젝트 구조(`package.json`·`type: module`·`react`/`react-dom` 분리), `index.html`의 빈 `#root`와 모듈 스크립트 진입점, `createRoot(root).render(<App />)` 3단계, 컴포넌트 = JSX를 반환하는 함수(대문자 이름·`props`·`export default`), 태그로 쓰는 컴포넌트, JSX와 HTML의 차이(`className`·`onClick={}`·자기 닫힘·프래그먼트), `useState`와 선언형 렌더링으로 이어지는 자리 |

## 앞선 갈래

순수 JS·DOM 조작(2026_FE)은 JavaScript MOC 관할이다. React 수업의 선행 흐름은 JS day11 DOM 조작 → JS day14 게시판 CRUD → 여기(평문 안내 — 구역 간 직접 링크는 걸지 않는다).
