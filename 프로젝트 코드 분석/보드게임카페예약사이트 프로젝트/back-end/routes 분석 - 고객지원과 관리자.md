---
출처: Claude 분석
원본: shirhal/back-end/routes
작성일: 2026-08-11
tags: [프로젝트, 일지, 보드게임카페예약사이트, express]
---

# routes 분석 - 고객지원과 관리자

대상: `routes/inquiryRoutes.js` · `routes/noticeRoutes.js` · `routes/adminRoutes.js`
상위: [[보드게임카페예약사이트 프로젝트 MOC]]

## 라우트가 얇아진 지점

이 세 파일은 다른 라우트 8개와 구조가 다르다. 직접 쿼리하지 않고 컨트롤러에 위임한다.

```javascript
// inquiryRoutes.js — 전부 이 모양
router.post("/", inquiryController.createInquiry);
router.get("/", inquiryController.getUserInquiries);
```

커밋 순서상 인증·예약·보드게임 라우트가 먼저였고, 관리자 기능이 나중이다. 관리자 화면은 유저·공지·문의·예약을 한 URL 묶음에서 다뤄야 해서, 로직을 재사용 가능한 단위로 꺼낼 필요가 그때 처음 생겼다. **컨트롤러 분리는 계획이 아니라 필요가 만들었다.**

## adminRoutes.js — Facade

```javascript
const userController = require("../controllers/userController");
const noticeController = require("../controllers/noticeController");
const inquiryController = require("../controllers/inquiryController");
const reservationController = require("../controllers/reservationController");
const totalDashboard = require("../controllers/totalDashboard");

router.get("/users", userController.getAllUsers);
router.delete("/users/:id", userController.deleteUser);
router.post("/notices", noticeController.createNotice);
router.get("/inquiries", inquiryController.getAllInquiries);
router.patch("/inquiries/:id", inquiryController.updateInquiryStatus);
router.get("/reservations", reservationController.getAllReservations);
router.get("/stats", totalDashboard.getStats);
```

컨트롤러 6개를 `/api/admin/*` 하나로 감싼 **Facade** 구조다. 관리자 프론트는 컨트롤러가 몇 개인지 모르고 URL 묶음 하나만 안다. 파일 상단에 `// ✅ 기능별 컨트롤러 모듈화`라는 주석을 남겨둔 걸 보면, 이 시점에 구조를 의식적으로 바꿨다.

## 인증 미들웨어가 없다

이 파일의 치명적인 구멍. `/api/admin/*` 전체에 **아무 인증도 걸려 있지 않다.**

```javascript
// 누구든 호출할 수 있다
DELETE /api/admin/users/1
```

프론트의 `AdminRoute.js`(그마저 미적용)가 화면 접근을 막아도, API를 직접 호출하면 유저 삭제·예약 변경이 그대로 된다. **화면 가드는 편의이고 방어선은 서버**라는 원칙이 빠졌다.

> **피드백** — Facade로 묶은 구조가 오히려 기회였다. 묶여 있으니 한 줄이면 전체가 보호된다.
>
> ```javascript
> router.use(requireAdmin);   // 모든 admin 라우트 앞에
>
> const requireAdmin = (req, res, next) => {
>   const token = req.headers.authorization?.replace("Bearer ", "");
>   const payload = jwt.verify(token, process.env.JWT_SECRET);
>   if (!payload.is_admin) return res.status(403).json({ message: "권한 없음" });
>   req.user = payload;
>   next();
> };
> ```
>
> 이게 미들웨어 체인의 힘이다 — **횡단 관심사**(인증·로깅·검증)를 라우트마다 반복하지 않고 앞단에 한 번 끼운다. 로그인에서 JWT를 발급하지 않은 것( → [[routes 분석 - 인증과 유저]] )이 여기서 발목을 잡았다. 인증은 기능이 아니라 기반이라, 미루면 모든 층에 구멍이 남는다.

## 프론트에만 있는 관리자 로그인

`Admin/Admin_Login.js`는 `/api/admin/login`을 호출하는데, **백엔드에 이 라우트가 없다.** 일반 로그인(`/api/login`)의 `is_admin` 분기로 방향을 바꾸면서 백엔드를 안 만들었거나 지운 것으로 보인다. 죽은 화면이 하나 남은 셈이다. → [[components 분석 - Login과 Admin]]

## 관련 노트

[[보드게임카페예약사이트 프로젝트 MOC]] · [[controllers와 models 분석]] · [[routes 분석 - 인증과 유저]] · [[components 분석 - Login과 Admin]] · [[전문용어 정리]]
