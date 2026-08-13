---
출처: Claude 분석
원본: shirhal/back-end/routes
작성일: 2026-08-11
tags: [프로젝트, javascript]
---

# routes 분석 - 인증과 유저

대상: `routes/authRoutes.js` · `routes/usersRoutes.js`
상위: [[보드게임카페예약사이트 프로젝트 MOC]]

## authRoutes.js — 가입과 로그인

```javascript
// 가입
const [existing] = await db.query("SELECT * FROM users WHERE user_id = ?", [user_id]);
if (existing.length > 0) return res.status(409).json({ message: "이미 존재하는 아이디입니다." });
await db.query("INSERT INTO users (user_id, password) VALUES (?, ?)", [user_id, password]);

// 로그인
if (user.password !== password) {
  return res.status(400).json({ message: "비밀번호가 일치하지 않습니다." });
}
res.json({ user: { user_id: user.user_id, is_admin: user.is_admin } });
```

흐름 자체는 표준이다. 중복 아이디를 409로 거르고, **파라미터 바인딩**(`?` 플레이스홀더)으로 **SQL 인젝션**을 막았고, 로그인 성공 시 `is_admin`을 내려서 프론트가 관리자 분기를 하게 했다.

문제는 비밀번호를 **평문**으로 저장하고 문자열 비교로 검증한다는 것. `package.json`에 `bcryptjs`를 설치까지 해놓고 쓰지 않았다. 도입하려다 뒤로 밀렸던 것 같다.

> **피드백** — 이 프로젝트에서 가장 먼저 고쳐야 할 한 곳이다.
>
> ```javascript
> const bcrypt = require("bcryptjs");
> // 가입: 해시해서 저장
> const hash = await bcrypt.hash(password, 10);
> // 로그인: 해시끼리 비교
> const ok = await bcrypt.compare(password, user.password);
> ```
>
> **해싱**은 단방향이라 DB가 유출돼도 원래 비밀번호를 되돌릴 수 없다. 같은 비밀번호를 다른 사이트에 재사용하는 사용자가 많아서, 평문 저장의 피해는 이 서비스 밖으로 번진다.
>
> 그리고 로그인 성공이 **세션이나 토큰으로 이어졌어야 했다.** 지금은 응답 JSON을 프론트가 `localStorage`에 넣는 게 전부라, 서버는 이후 요청이 누구에게서 온 건지 알 방법이 없다. **JWT**를 발급하고 이후 요청의 `Authorization` 헤더를 검증하는 미들웨어가 다음 단계였다. → [[components 분석 - Login과 Admin]]

## usersRoutes.js — 유저 목록

```javascript
router.get("/users", async (req, res) => {
  const [results] = await db.query("SELECT * FROM users");
  res.status(200).json(results);
});
```

`SELECT *`라서 **비밀번호 컬럼까지 응답에 실린다.** 평문 저장과 겹치면, 이 엔드포인트 하나로 전 회원의 비밀번호가 노출된다.

같은 기능이 `controllers/userController.js`에도 있는데 그쪽은 `SELECT id, user_id, is_admin, created_at`으로 컬럼을 골랐다. 관리자 기능을 만들면서 새로 작성했고, 이 파일은 역할이 끝났는데 남아 있는 상태다.

> **피드백** — 같은 일을 하는 코드가 두 벌 있으면 하나만 안전해도 의미가 없다. 공격자는 안전하지 않은 쪽을 쓴다. `usersRoutes.js`는 `adminRoutes`가 생긴 시점에 지웠어야 했다. 응답에서 민감 컬럼을 빼는 습관은 `SELECT` 목록 명시가 기본이고, ORM을 쓴다면 직렬화 단계에서 제외 필드를 선언하는 방식으로 이어진다.

## 관련 노트

[[보드게임카페예약사이트 프로젝트 MOC]] · [[routes 분석 - 고객지원과 관리자]] · [[components 분석 - Login과 Admin]] · [[전문용어 정리]]
