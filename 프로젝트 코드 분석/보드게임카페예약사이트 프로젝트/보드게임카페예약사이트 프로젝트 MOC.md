---
출처: Claude 분석
원본: shirhal
작성일: 2026-08-11
tags: [허브]
---

# 보드게임카페예약사이트 프로젝트 MOC

2025년 3~6월에 만든 보드게임 카페 웹사이트 "Board Lake"를 다시 뜯어본 기록의 허브다.
분석은 저장소의 코드 폴더 구조 그대로 나눠서 남긴다.

상위: [[프로젝트 코드 분석 안내]]

> **학습 노트와의 연결은 이 MOC ↔ [[KDT_2026 학습 지도]] 한 줄뿐이다.**
> 개별 분석 노트에서 KDT day 노트로 직접 링크하지 않는다 — 어느 학습 주제와 닿는지는 학습 지도의 "프로젝트 매핑표"에서 찾는다.

## 학습 매핑 — 이 프로젝트 ↔ 학습 지도

이 프로젝트의 구간별로 어느 이론과 닿는지의 요약이다. (이론 쪽은 평문 — 세부는 [[KDT_2026 학습 지도]]의 매핑표와 각 언어 MOC의 "프로젝트 매핑" 표에서)

| 이 프로젝트의 노트 | 닿는 이론 (학습 지도 경유) |
| --- | --- |
| [[routes 분석 - 예약]] | SQL 조건·트랜잭션·N+1 → CS 이론 MOC |
| [[routes 분석 - 보드게임과 리뷰]] | 화이트리스트·UNIQUE·페이징 → CS 이론 MOC |
| [[routes 분석 - 인증과 유저]] · [[routes 분석 - 고객지원과 관리자]] | 해싱·JWT·미들웨어 → CS 이론 MOC · Java MOC(캡슐화) |
| [[controllers와 models 분석]] | MVC·Repository·인터페이스 → Java MOC |
| [[crawler 분석]] | dict 병합·멱등 → Python 인덱스 · CS 이론 MOC |
| [[hooks 분석]] · [[components 분석 - Reservation과 결제]] | 클로저·객체·스토리지 → JavaScript MOC |
| [[App과 공통 레이아웃 분석]] · [[data와 styles 분석]] | position·flexbox·폼 마크업 → CSS MOC · HTML MOC |
| `학습 관점/` 시리즈 | 위 주제들의 공부 순서·연습 과제 |

| 항목 | 내용 |
| --- | --- |
| 기간 | 2025-03-10 ~ 2025-06-09 (약 3개월, 커밋 7개) |
| 스택 | React 18 · Express 4 · MySQL 8 · Python(Selenium) |
| 규모 | JS 53개, 프론트 약 8,800줄 + 백엔드 약 1,200줄 |
| 저장소 폴더 | `shirhal` |

## 읽는 순서

각 노트는 「분석 → 피드백」 순서로 썼다. 분석 절에 나오는 **굵은 전문용어**는 [[전문용어 정리]]에 짧은 설명을 모아뒀고, 나중에 학습 관점 노트와 이어진다.

### back-end

| 노트 | 다루는 파일 |
| --- | --- |
| [[server와 config 분석]] | `server.js` · `config/db.js` |
| [[routes 분석 - 인증과 유저]] | `authRoutes.js` · `usersRoutes.js` |
| [[routes 분석 - 예약]] | `reservations.js` · `availabilityRoutes.js` · `myreservations.js` |
| [[routes 분석 - 보드게임과 리뷰]] | `boardgames.js` · `gamelikesRoutes.js` · `reviewRoutes.js` |
| [[routes 분석 - 고객지원과 관리자]] | `inquiryRoutes.js` · `noticeRoutes.js` · `adminRoutes.js` |
| [[controllers와 models 분석]] | `controllers/` 6개 · `models/` 2개 |

### crawler

| 노트 | 다루는 파일 |
| --- | --- |
| [[crawler 분석]] | `redbutton.py` · `processCrawledData.js` |

### front-end

| 노트 | 다루는 파일 |
| --- | --- |
| [[hooks 분석]] | `hooks/` 8개 |
| [[App과 공통 레이아웃 분석]] | `App.js` · `NavBar.js` · `styles/GlobalStyle.js` |
| [[components 분석 - BoardGame과 Rule]] | `BoardGame/` 3개 · `Rule/` 2개 · `pages/rulepages.js` |
| [[components 분석 - Reservation과 결제]] | `Reservation/` 3개 · `pages/successpage.js` · `pages/FailPage.js` |
| [[components 분석 - MainPage와 고객지원]] | `MainPage/` 6개 · `CustomerSupoort/CustomerSupport.js` |
| [[components 분석 - Login과 Admin]] | `Login_Register/` 2개 · `Admin/` 7개 |
| [[data와 styles 분석]] | `data/` 4개 · `public/data/rules.json` |

## 기획 — README가 설계도였다

`README.md`에 처음 기획을 그대로 남겨뒀다. 기능 축 네 개를 먼저 정하고 시작했다.

```
기능: 회원등록, 보드게임(내용 및 룰 설명), 예약(+채팅방), 고객지원
```

이 기획이 그대로 폴더 이름이 됐다. **도메인 단위 모듈화**다.

| README 기능 | 프론트 폴더 | 백엔드 라우트 | DB 테이블 |
| --- | --- | --- | --- |
| 회원등록 | `Login_Register/` | `authRoutes` | `users` |
| 보드게임 | `BoardGame/` `Rule/` | `boardgames` `gamelikes` `review` | `board_game` `game_likes` `game_reviews` |
| 예약 | `Reservation/` | `reservations` `availability` `myreservations` | `reservations` `rooms` |
| 고객지원 | `CustomerSupoort/` | `inquiry` `notice` | `inquiries` `notice` |
| (기획 외) 관리자 | `Admin/` | `adminRoutes` | — |

채팅방은 기획에만 있고 구현하지 않았다. 대신 기획에 없던 관리자 페이지가 들어왔다. WebSocket이라는 새 축을 여는 것보다, 이미 있는 CRUD에 운영 화면을 붙이는 쪽이 투자 대비 산출이 컸기 때문이었을 것이다.

> **피드백** — 기획 변경도 README에 남겼어야 했다. "채팅방 → 보류, 관리자 페이지 추가" 한 줄이면 몇 달 뒤에 코드와 기획이 어긋난 이유를 찾지 않아도 된다.

## 아키텍처

```
┌─────────────────────────────────────────┐
│  React (CRA + craco)     :3000          │
│  components / hooks / pages / data      │
└──────────────┬──────────────────────────┘
               │ proxy → localhost:5000
┌──────────────▼──────────────────────────┐
│  Express        :5000                   │
│  routes 11개 → (일부) controllers 6개    │
│  config/db.js — 커넥션 풀                │
└──────────────┬──────────────────────────┘
               │ mysql2/promise
┌──────────────▼──────────────────────────┐
│  MySQL — shirhal (테이블 8개)            │
└──────────────┴──────────────────────────┘
        ▲
        │ crawler: Selenium → JSON → 업서트
```

`package.json`의 `"proxy": "http://localhost:5000"` 한 줄로 개발 중 **CORS**를 우회했다. 프론트는 `/api/...` 상대경로로 호출하고 CRA 개발서버가 백엔드로 넘긴다.

> **피드백** — 프록시를 썼다면 끝까지 상대경로로 통일했어야 했다. 네 파일(`useBoardGameReview` · `successpage` · `RegisterForm` · `CalendarReservation`)만 `http://localhost:5000` 절대경로가 박혀 있어서, 배포하면 이 네 곳만 깨진다.

## 이 프로젝트를 관통하는 문제 세 가지

각 노트에서 반복해서 마주친 문제라 먼저 적어둔다.

1. **인증이 없는 것과 같다** — 비밀번호 평문 저장, `localStorage` 값 하나로 관리자 판정, 서버 측 인증 미들웨어 없음. → [[routes 분석 - 인증과 유저]]
2. **결제와 예약이 검증 없이 이어진다** — 결제 성공 URL만 믿고 예약을 넣는다. 승인(confirm) 단계가 없다. → [[components 분석 - Reservation과 결제]]
3. **계층이 반만 나뉘었다** — `models/`를 만들다 말았고, 라우트 8개는 직접 쿼리, 3개는 컨트롤러 위임으로 섞여 있다. → [[controllers와 models 분석]]

## 관련 노트

[[프로젝트 코드 분석 안내]] · [[전문용어 정리]] · [[Vault 홈]]

학습 관점 정리 → [[보드게임카페예약사이트 프로젝트에서 배울 것]]
