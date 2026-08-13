---
출처: Claude 분석
원본: shirhal/front-end/src/components
작성일: 2026-08-11
tags: [프로젝트, javascript]
---

# components 분석 - Login과 Admin

대상: `Login_Register/` 2개 · `Admin/` 7개
상위: [[보드게임카페예약사이트 프로젝트 MOC]]

## LoginForm.js — 로그인

파일에 `// 로그인 로직 및 디자인은 인터넷에 공유되있는 코드 가져옴`이라는 주석을 남겨뒀다. 출처를 코드에 적어둔 건 나중의 나를 위한 정직한 기록이다.

```javascript
const res = await fetch("/api/login", { method: "POST", ... });
if (data.user.is_admin === 1) {
  localStorage.setItem("is_admin", "1");
  navigate("/admin/dashboard");
} else {
  localStorage.setItem("user_id", data.user.user_id);
  localStorage.setItem("user_name", data.user.user_name);
  navigate("/home");
}
```

일반/관리자 로그인을 **엔드포인트 하나**(`/api/login`)로 처리하고 응답의 `is_admin`으로 분기한다. 로그인 결과는 `localStorage` 세 키에 저장 — 이후 모든 화면이 이 키들을 읽는다.

> **피드백** — 세션의 실체가 "localStorage에 문자열 세 개"라는 게 이 앱 인증의 전부다. 서버가 발급한 **토큰**이 없으니 이후 요청은 익명이나 마찬가지고, 콘솔에서 `localStorage.setItem("is_admin","1")` 한 줄로 관리자가 된다. 로그인 응답으로 JWT를 받고, axios 인터셉터로 모든 요청에 `Authorization` 헤더를 실어 보내는 구조가 다음 단계였다. → [[routes 분석 - 인증과 유저]]

## RegisterForm.js — 가입

`axios.post("http://localhost:5000/api/register", ...)` — 하드코딩 절대경로 네 곳 중 하나. 성공/실패 alert 후 로그인 화면으로 보낸다.

> **피드백** — 비밀번호 확인 입력, 아이디 형식 검사 같은 클라이언트 검증이 없다. 서버 검증이 최종이지만, 오타를 서버까지 보내서야 알게 하는 건 UX 낭비다.

## AdminRoute.js — 만들어놓고 안 쓴 가드

```javascript
export default function AdminRoute({ children }) {
  const isAdmin = localStorage.getItem("is_admin") === "1";
  if (!isAdmin) return <Navigate to="/admin/login" replace />;
  return children;
}
```

라우트 **Guard** 패턴의 교과서적 구현이다. 그런데 `App.js`에서 import만 하고 어떤 라우트도 감싸지 않았다( → [[App과 공통 레이아웃 분석]] ). 완성한 부품이 조립되지 않은 채 남았다.

## Admin_Login.js — 죽은 화면

`/api/admin/login`을 호출하는데 **백엔드에 이 라우트가 없다.** 일반 로그인의 `is_admin` 분기 방식으로 바꾸면서 이 화면은 갈 곳이 없어졌다. `AdminRoute`가 미인증 시 보내는 곳이 하필 이 죽은 화면이라, 가드를 적용했더라도 로그인이 안 되는 막다른 길이었다.

> **피드백** — 방향을 바꿀 때는 옛 경로의 화면·라우트·리다이렉트 대상을 한 번에 정리해야 한다. "어디서 이 화면으로 들어오는가"를 역추적하면 죽은 코드가 드러난다.

## 관리자 화면 5개 — CRUD의 재조합

| 화면 | 호출 | 내용 |
| --- | --- | --- |
| `AdminDashBoard` | `GET /api/admin/stats` | 유저·예약·문의·게임 수 카드 4개 |
| `AdminUserManagement` | `GET`/`DELETE /api/admin/users` | 목록 + 삭제 |
| `AdminReservationManagement` | `GET`/`PUT`/`DELETE /api/admin/reservations` | 목록 + 상태 변경 + 삭제 |
| `AdminInquiries` | `GET`/`PATCH /api/admin/inquiries` | 목록 + 처리 상태 변경 |
| `AdminNoticeForm` | `POST /api/admin/notices` | 공지 작성 |

전부 "목록 fetch → 테이블 렌더 → 행 단위 액션" 구조다. 기존 백엔드 CRUD를 화면으로 재조합한 것이라 새 로직이 거의 없다 — 기획에 없던 관리자 기능을 빠르게 붙일 수 있었던 이유다. 대시보드의 로그아웃은 `localStorage.removeItem("is_admin")`으로 키만 지운다(NavBar의 `clear()`보다 정확한 방식이 오히려 여기 있다).

> **피드백** — 다섯 화면의 "fetch → 목록 → 삭제/수정" 패턴이 복붙으로 반복된다. `useAdminResource("users")` 같은 훅 하나로 추상화하면 화면당 코드가 크게 줄었을 것이다 — 같은 모양이 세 번 보이면 추상화 신호다. 삭제 확인이 `window.confirm`인 것도 통일된 모달로 바꿀 자리. 그리고 이 모든 화면이 서버 인증 없이 열린 API를 부른다는 근본 문제는 여전하다( → [[routes 분석 - 고객지원과 관리자]] ).

## 관련 노트

[[보드게임카페예약사이트 프로젝트 MOC]] · [[routes 분석 - 인증과 유저]] · [[routes 분석 - 고객지원과 관리자]] · [[App과 공통 레이아웃 분석]] · [[전문용어 정리]]
