---
출처: Claude 분석
원본: shirhal/front-end/src/hooks
작성일: 2026-08-11
tags: [프로젝트, javascript]
---

# hooks 분석

대상: `hooks/` 8개
상위: [[보드게임카페예약사이트 프로젝트 MOC]]

이 프로젝트에서 가장 중요한 설계 결정이 이 폴더다. 화면(components)은 그리기만 하고, 상태와 통신은 전부 **커스텀 훅**으로 뺐다. 예전 React의 Container/Presentational 분리를 훅으로 구현한 형태다.

| 훅 | 책임 | 소비처 |
| --- | --- | --- |
| `useBoardGameList` | 목록·검색·필터·무한스크롤·추천 | BoardGameList |
| `useBoardGameReview` | 리뷰 CRUD | ReviewSection |
| `useReservationForm` | 예약 폼·가격·시간대·결제 | Reservation |
| `useCustomerSupport` | 공지 조회·문의 등록 | CustomerSupport |
| `useCarousel` | 자동 재생 슬라이드 | MainPage |
| `useImageSlider` | 썸네일+메인 이미지 | ImageSliderSection |
| `useStore` | 카카오맵 렌더 | store |
| `useRuleData` | 규칙 JSON 조회 | rulepages |

`MainPage.js` 705줄, `CustomerSupport.js` 636줄 — styled-components 정의 때문에 화면 파일은 필연적으로 길다. 여기에 fetch와 상태까지 섞였다면 1,000줄을 넘겼을 것이다. **"화면이 긴 것"과 "로직이 복잡한 것"을 분리**한 게 이 폴더의 역할이다.

## useBoardGameList — 가장 복잡한 훅

**무한 스크롤**: 스크롤이 바닥 근처에 오면 다음 페이지를 요청한다. lodash **쓰로틀**로 스크롤 이벤트를 초당 몇 번으로 제한해서 과도한 호출을 막았다.

**조회 전략 분기** — 검색어·필터 상태에 따라 다른 엔드포인트를 고른다. **Strategy** 패턴의 원형이다.

```javascript
if (searchQuery.trim())        url = "/api/games/search?...";
else if (filter === "likes")   url = "/api/games/sorted?...";
else if (filter === "difficulty" && difficulty) url = "/api/games/filter?...";
else                           url = "/api/games?page=...";
```

**추천(좋아요)**: 서버 응답을 기다리지 않고 화면의 likes를 먼저 +1 하는 **낙관적 업데이트**를 쓰고, `localStorage` 캐시로 중복 요청 자체를 줄였다. 서버의 409 검사( → [[routes 분석 - 보드게임과 리뷰]] )까지 합치면 3중 방어다.

> **피드백** — 분기가 4개를 넘어가면 if-else 사슬보다 `{ 조건: URL생성함수 }` 객체 매핑이 낫다. 그리고 검색·필터·페이지가 각각 상태라서 조합이 어긋나는 경우(검색 중 필터 변경 등)를 상태 하나의 객체로 합쳐 관리했으면 리셋 로직이 단순해졌을 것이다. 이 훅이 하는 일(원격 데이터 + 캐시 + 페이지네이션)은 정확히 **TanStack Query** 같은 서버 상태 라이브러리가 해결하는 문제다 — 다음 프로젝트에서는 직접 만들지 말고 가져다 쓰는 판단도 필요하다.

## useReservationForm — 폼·가격·결제

- 가격을 `5000 * hours * players`로 실시간 계산해 보여준다 (최종 금액은 서버가 다시 계산)
- 날짜를 고르면 테이블식·좌식 잔여 조회 두 개를 `Promise.all`로 **병렬 요청**
- `formatDateToMySQL`로 날짜를 MySQL 형식으로 변환
- 제출하면 예약 데이터를 `localStorage`에 넣고 Toss 결제 위젯을 연다 — 결제 성공 페이지가 꺼내 쓰는 **페이지 간 전달 통로**다

> **피드백** — Toss `clientKey`가 코드에 하드코딩돼 있다. 클라이언트 키는 원래 공개되는 값이지만 환경변수(`REACT_APP_*`)로 빼는 게 운영 전환 시의 실수를 막는다. localStorage 전달 방식은 동작하지만, 새로고침·다중 탭에서 꼬일 수 있는 구조라 결제 위젯의 `orderId`에 예약 정보를 서버 세션으로 묶는 방식이 정석이다. → [[components 분석 - Reservation과 결제]]

## useStore — 외부 스크립트 대기

카카오맵 SDK가 로드됐는지 **폴링으로 재시도**하며 기다렸다가 지도를 그린다. 외부 스크립트의 로드 시점을 제어할 수 없다는 문제를 폴링으로 푼 것.

> **피드백** — 동작하지만, script 태그의 `onload` 콜백이나 SDK의 `kakao.maps.load()` 콜백을 쓰면 폴링 없이 정확한 시점을 잡을 수 있다. "폴링은 이벤트가 없을 때의 차선책"이라는 순서를 기억할 것.

## useBoardGameReview / useCustomerSupport / useCarousel / useImageSlider / useRuleData

- `useBoardGameReview`: 리뷰 목록·내 리뷰·등록·삭제를 한 훅에. `API_BASE_URL = "http://localhost:5000"` 하드코딩이 여기 있다 — 프록시 상대경로로 통일했어야 하는 지점.
- `useCustomerSupport`: 공지 조회와 문의 등록. 문의자 이름을 `localStorage`의 `user_name`으로 미리 채운다.
- `useCarousel`: `setInterval` 자동재생 + 마우스오버 일시정지. 클린업에서 인터벌을 정리한다 — JS day13 웹 스토리지와 인터벌 에서 다룬 패턴의 실전판.
- `useImageSlider`: 인덱스 상태 + 썸네일 버퍼 계산.
- `useRuleData`: `fetch("/data/rules.json")` — DB가 아니라 정적 파일을 데이터 소스로 쓴다. → [[data와 styles 분석]]

## 관련 노트

[[보드게임카페예약사이트 프로젝트 MOC]] · [[components 분석 - BoardGame과 Rule]] · [[components 분석 - Reservation과 결제]] · [[전문용어 정리]]
