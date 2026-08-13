---
출처: Claude 분석
원본: shirhal/back-end
작성일: 2026-08-11
tags: [프로젝트, javascript]
---

# server와 config 분석

대상: `back-end/server.js` · `back-end/config/db.js`
상위: [[보드게임카페예약사이트 프로젝트 MOC]]

## server.js — 진입점

Express 앱을 만들고 라우터 11개를 `/api` 아래에 붙이는 게 전부다. 진입점을 얇게 유지했다.

```javascript
app.use(cors());
app.use(express.json());

app.use("/api", authRoutes);
app.use("/api/reservations", reservationRoutes);
app.use("/api/admin", adminRoutes);
// ... 총 11개
app.listen(5000);
```

**미들웨어 체인**은 `cors()` → `express.json()` → 라우터 순. 요청 본문을 JSON으로 파싱한 뒤 각 라우터로 넘어간다. 프록시를 쓰는데도 `cors()`를 걸어둔 건, 프록시 없이 직접 호출할 때를 대비한 이중 안전장치였다.

`/success`, `/fail` 스텁 라우트도 여기 있다. Toss 결제 리다이렉트를 백엔드가 받을 계획이었다가, 결국 프론트 라우트(`pages/successpage.js`)가 받는 걸로 바뀌면서 죽은 코드가 됐다.

```javascript
const { error } = require("console");   // 어디에서도 쓰지 않는다
```

> **피드백** — 진입점이 얇은 건 유지하되, 두 가지가 빠졌다.
> ① **전역 에러 핸들러.** 지금은 라우트마다 `try-catch`를 반복한다. `app.use((err, req, res, next) => ...)`를 마지막에 한 번 걸면 각 라우트는 `next(err)`로 던지기만 하면 된다.
> ② **404 핸들러.** 없는 경로를 호출하면 Express 기본 HTML이 나간다. API 서버라면 `{ message: "Not Found" }` JSON으로 통일했어야 했다.
> 죽은 코드(`/success` 스텁, `require("console")`)는 방향이 바뀐 시점에 지웠어야 했다. 죽은 코드는 "이게 아직 쓰이나?"라는 질문 비용을 계속 만든다.

## config/db.js — 커넥션 풀

```javascript
const mysql = require("mysql2/promise");
const db = mysql.createPool({
  host: "localhost",
  user: "root",
  password: "1234",
  database: "shirhal",
  waitForConnections: true,
  connectionLimit: 10,
  queueLimit: 0,
});
module.exports = db;
```

**커넥션 풀**을 골랐다. 요청마다 연결을 새로 만들면 TCP 핸드셰이크 + 인증 비용이 매번 들기 때문에, 연결 10개를 만들어놓고 돌려 쓴다. `mysql2/promise`를 써서 모든 쿼리를 `async/await`로 다뤘고, 콜백 지옥 없이 흐름이 읽힌다. 이 파일 하나를 모든 라우트가 `require`해서 쓰는 구조라, DB 접근의 **단일 진입점**이기도 하다.

> **피드백** — 구조는 맞는데 값이 문제다.
> ① 접속 정보가 코드에 박혀 있다. `dotenv`가 이미 설치돼 있고 `crawler/processCrawledData.js`에서는 실제로 쓰고 있었는데, 정작 본체 DB 설정만 하드코딩으로 남았다. `process.env.DB_HOST` 방식으로 옮기고 `.env`는 `.gitignore`에 넣는 게 순서였다.
> ② `root` 계정을 그대로 쓴다. 애플리케이션용 계정을 따로 만들어 `shirhal` DB에 대한 권한만 주는 게 **최소 권한 원칙**이다. root가 뚫리면 DB 서버 전체가 뚫린다.
> ③ 커넥션 풀에 `timezone`과 `dateStrings` 설정이 없다. 예약 쪽에서 날짜가 UTC로 틀어지는 문제를 프론트에서 보정하며 살았는데, 원인은 여기였을 가능성이 크다. → [[routes 분석 - 예약]]

## 관련 노트

[[보드게임카페예약사이트 프로젝트 MOC]] · [[routes 분석 - 인증과 유저]] · [[전문용어 정리]]
