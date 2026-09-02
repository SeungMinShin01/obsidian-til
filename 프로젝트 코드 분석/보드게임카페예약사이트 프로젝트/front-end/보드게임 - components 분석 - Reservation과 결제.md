---
출처: Claude 분석
원본: shirhal/front-end/src
작성일: 2026-08-11
tags: [프로젝트, javascript]
---

# components 분석 - Reservation과 결제

대상: `Reservation/Reservation.js` · `Reservation/CalendarReservation.js` · `Reservation/ReservationStatusPage.js` · `pages/successpage.js` · `pages/FailPage.js`
상위: [[보드게임카페예약사이트 프로젝트 MOC]]

## 전체 흐름

```
Reservation.js (폼 입력·시간 선택)
   └ useReservationForm → localStorage에 예약 데이터 저장 → Toss 결제 위젯
        결제 성공 → /users/20250324/success → successpage.js → POST /api/reservations
        결제 실패 → FailPage.js
예약 확인:
ReservationStatusPage.js → CalendarReservation.js → GET /api/myreservations/:id → Syncfusion 달력
```

## Reservation.js — 예약 폼

폼 상태·가격·시간대는 전부 훅( → [[보드게임 - hooks 분석|hooks 분석]] )에서 받고, 이 파일은 datepicker와 시간 슬롯 버튼, 결제수단 선택 UI만 그린다. 잔여 좌석을 30분 슬롯 단위로 미리 보여주는 화면이 여기다 — 예약 실패를 사후에 알리는 대신 **가능한 시간을 사전에 보여주는** UX.

`user_id`를 **입력 필드로 받는다.** 로그인해도 예약자 아이디를 손으로 친다.

> **피드백** — 로그인 정보(`localStorage.user_id`)로 자동 채우고 읽기 전용으로 만들었어야 했다. 남의 아이디로 예약이 들어갈 수 있는 입력이고, 서버도 이를 검증하지 않는다( → [[보드게임 - routes 분석 - 예약|routes 분석 - 예약]] ). "사용자가 이미 알려준 것을 다시 묻지 않는다"는 폼 설계 원칙과, "신원은 입력값이 아니라 세션에서 온다"는 보안 원칙이 같이 걸린 지점이다.

## successpage.js — 결제 성공 처리

이 파일이 실제 예약 INSERT를 일으킨다. 결제 위젯이 성공 URL로 리다이렉트하면, `localStorage`에 넣어둔 예약 데이터를 꺼내 서버로 보낸다.

**중복 제출 이중 차단**이 들어 있다.

```javascript
const didSubmit = useRef(false);                      // ① StrictMode 이중 실행 차단
if (didSubmit.current) return;
if (localStorage.getItem("reservation_submitted") === "true") return;   // ② 새로고침 차단
```

React 18 **StrictMode**는 개발 모드에서 effect를 두 번 돌린다. 예약 POST가 두 번 나가 예약이 두 건 생기는 걸 실제로 겪고 막은 흔적이다 — 콘솔 로그(`🛑 useRef: 이미 처리된 예약`)가 그대로 남아 있다. `useRef`는 리렌더링 간에 값이 유지되면서도 리렌더링을 일으키지 않아서 이런 실행 제어 플래그에 정확히 맞는 도구다.

### 결제 승인 검증이 없다

```javascript
// 결제가 "진짜" 됐는지 아무도 확인하지 않는다
await axios.post("http://localhost:5000/api/reservations", reservationData);
```

성공 URL에 도착했다는 사실만 믿는다. 브라우저 주소창에 성공 URL을 직접 치면 **결제 없이 예약이 생성된다.**

> **피드백** — Toss 결제의 정석 흐름은 리다이렉트가 아니라 **서버 승인(confirm)**이 기준이다.
>
> ```
> 성공 리다이렉트(paymentKey, orderId, amount 쿼리 포함)
>   → 프론트가 서버에 전달
>   → 서버가 Toss 승인 API 호출 (시크릿 키 사용)
>   → 금액 일치 확인 + 승인 성공 → 그때 예약 INSERT
> ```
>
> 리다이렉트는 "사용자가 돌아왔다"는 신호일 뿐이고, 돈이 움직였다는 증명은 서버 간 승인 호출이다. 시크릿 키가 서버에만 있어야 하는 이유도 여기 있다. localStorage로 예약 데이터를 옮기는 대신, 결제 전에 서버에 **가예약(pending)** 을 만들고 `orderId`로 묶은 뒤 승인 시 확정하는 구조면 새로고침·다중 탭 문제도 같이 사라진다.

## CalendarReservation.js — 예약 달력

`GET /api/myreservations/:user_id` 응답을 **Syncfusion ScheduleComponent**의 `eventSettings.dataSource` 형식으로 변환해서 달력에 그린다. 시작 시각 + 이용 시간으로 종료 시각을 계산하고, `isNaN` 검사로 깨진 날짜를 걸러낸 뒤 넘긴다 — 외부 라이브러리에 데이터를 넣기 전의 **어댑터 변환** 층을 컴포넌트 안에 만든 셈이다.

> **피드백** — 변환 로직(응답 → Syncfusion 이벤트)은 훅이나 유틸 함수로 꺼냈으면 테스트 가능한 순수 함수가 됐다. 그리고 여기도 `http://localhost:5000` 절대경로가 박혀 있다 — 프록시 상대경로로 통일할 네 파일 중 하나. 상용 라이브러리(Syncfusion)는 라이선스 키 관리와 번들 크기가 따라오는 선택이라, 읽기 전용 달력 정도면 FullCalendar 같은 오픈소스로 충분했을 것이다.

## FailPage.js

`alert("결제에 실패했습니다...")` 후 예약 화면으로 돌려보내는 15줄짜리 종착지. 실패 사유(쿼리의 `code`, `message`)를 버리고 있어서, 사용자는 왜 실패했는지 모른다.

> **피드백** — Toss가 실패 리다이렉트에 실어주는 `code`/`message`를 화면에 보여주기만 해도 "한도 초과"와 "취소"를 구분해 안내할 수 있었다.

## 관련 노트

[[보드게임카페예약사이트 프로젝트 MOC]] · [[보드게임 - routes 분석 - 예약|routes 분석 - 예약]] · [[보드게임 - hooks 분석|hooks 분석]] · [[보드게임 - 전문용어 정리|전문용어 정리]]
