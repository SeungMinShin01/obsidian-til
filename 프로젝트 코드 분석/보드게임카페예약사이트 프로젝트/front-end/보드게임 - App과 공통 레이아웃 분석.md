---
출처: Claude 분석
원본: shirhal/front-end/src
작성일: 2026-08-11
tags: [프로젝트, javascript]
---

# App과 공통 레이아웃 분석

대상: `App.js` · `components/NavBar.js` · `styles/GlobalStyle.js`
상위: [[보드게임카페예약사이트 프로젝트 MOC]]

## App.js — 라우팅 테이블

react-router-dom 7로 전체 화면을 한 파일에서 배선한다. 일반 화면 + `/admin/*` 관리자 화면 + 결제 리다이렉트 화면까지 모두 여기 모여 있어서, 라우팅 테이블이 곧 **사이트맵** 역할을 한다.

```javascript
<Route path="/admin/dashboard" element={<AdminDashboard />} />
<Route path="/users/20250324/success" element={<SuccessPage />} />
```

두 가지가 눈에 걸린다.

**① `AdminRoute`를 import하고 쓰지 않았다.** 관리자 가드 컴포넌트( → [[보드게임 - components 분석 - Login과 Admin|components 분석 - Login과 Admin]] )를 만들어놓고 라우트를 감싸지 않아서, URL만 알면 관리자 화면이 열린다.

**② 결제 경로에 개발 날짜가 박혔다.** `/users/20250324/success` — Toss 개발자 콘솔에 등록한 리다이렉트 URL을 그대로 두면서 작업 날짜가 URL 구조로 굳었다.

styled-components 레이아웃에서 `$fullWidth` **transient prop**($ 접두사)을 썼다. $가 붙은 prop은 DOM으로 새어나가지 않아서 "unknown prop" 경고가 없다 — 라이브러리의 관례를 정확히 따른 부분.

Syncfusion 라이선스 키가 `registerLicense("ORg4...")`로 하드코딩돼 있다.

> **피드백** — 가드는 만든 순간 적용까지가 한 세트다. `<Route element={<AdminRoute><AdminDashboard/></AdminRoute>}>` 한 줄이 빠져서 가드 전체가 장식이 됐다. 결제 경로는 `/payment/success`처럼 의미 있는 이름으로 정하고 Toss 콘솔의 등록 URL도 같이 바꾸면 됐다. 라우트가 늘어날수록 이 파일이 비대해지므로, 다음 단계는 라우트 배열을 상수로 빼서 `map`으로 돌리거나 라우터의 중첩 라우트(Outlet)로 관리자 구역을 묶는 것.

## NavBar.js — 메뉴와 세션 표시

```javascript
const isAdmin = localStorage.getItem("is_admin") === "1";
// 관리자면 관리자 메뉴, 아니면 일반 메뉴
```

`localStorage`를 읽어 관리자/일반 메뉴를 분기하고, 로그인 상태면 이름을 보여준다. 메뉴 항목은 하드코딩이 아니라 `data/NavmenuData.js`의 `subMenus` 객체를 `map`으로 돌린다 — **데이터 주도(config-driven) 렌더링**이라 메뉴 추가가 JSX 수정 없이 끝난다. → [[보드게임 - data와 styles 분석|data와 styles 분석]]

로그아웃은 `localStorage.clear()`.

> **피드백** — `clear()`는 앱이 localStorage에 넣은 다른 값(추천 캐시, 예약 전달 데이터)까지 전부 날린다. 지울 키만 `removeItem`으로 지우는 게 안전하다. 그리고 localStorage 값은 어느 컴포넌트에서든 읽고 바뀌어서 **전역 상태의 비공식 저장소**가 돼 있다 — 로그인 상태는 Context 하나로 감싸서 "읽는 곳은 많아도 바꾸는 곳은 한 곳"으로 만들었어야 했다. React 상태가 아니라서 값이 바뀌어도 리렌더링이 안 되는 문제도 Context면 같이 풀린다.

## GlobalStyle.js — 전역 스타일

`createGlobalStyle`로 리셋 + Pretendard 웹폰트를 전역 적용한다. 컴포넌트 스타일은 전부 styled-components로 파일 안에 두고, 전역은 이 파일 하나로 모았다 — 전역/지역의 경계가 명확하다.

> **피드백** — 색·간격·글꼴 크기가 각 컴포넌트에 리터럴로 흩어져 있다. styled-components의 `ThemeProvider`로 **디자인 토큰**(색상 팔레트, spacing 단위)을 한 곳에 정의했으면 톤 변경이 한 파일 수정으로 끝난다. 지금은 주황색을 바꾸려면 파일 수십 개를 찾아야 한다.

## 관련 노트

[[보드게임카페예약사이트 프로젝트 MOC]] · [[보드게임 - components 분석 - Login과 Admin|components 분석 - Login과 Admin]] · [[보드게임 - data와 styles 분석|data와 styles 분석]] · [[보드게임 - 전문용어 정리|전문용어 정리]]
