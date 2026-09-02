---
출처: Claude 분석
원본: shirhal/back-end
작성일: 2026-08-11
tags: [프로젝트, javascript]
---

# controllers와 models 분석

대상: `controllers/` 6개 · `models/` 2개
상위: [[보드게임카페예약사이트 프로젝트 MOC]]

## controllers/ — 관리자 기능의 로직 층

| 파일 | 역할 |
| --- | --- |
| `userController.js` | 유저 목록(컬럼 선택) · 삭제 |
| `noticeController.js` | 공지 CRUD |
| `inquiryController.js` | 문의 등록·조회 · 상태 변경(PATCH) |
| `reservationController.js` | 전체 예약 조회 · 취소(소프트 삭제) · 완전 삭제 |
| `adminController.js` | 관리자 집계 |
| `totalDashboard.js` | 대시보드 수치 4종(유저·예약·문의·게임 COUNT) |

구조는 **MVC의 Controller 층**에 해당한다. 요청에서 값을 꺼내고, 쿼리하고, 상태코드와 JSON으로 응답하는 표준 형태다. Java day09 MVC 종합예제 에서 만든 Controller와 같은 자리다.

`reservationController`의 취소는 `UPDATE ... SET is_deleted = 1` **소프트 삭제**, 별도의 완전 삭제 엔드포인트는 `DELETE` 하드 삭제로 나눴다. 취소 내역을 보존하면서 관리자가 정리도 할 수 있게 한 두 단계 설계다.

`adminController.js`에는 `const db = require(...)`가 빠져 있다. 이 파일의 함수가 호출되는 순간 `db is not defined`로 죽는다. 라우트에 연결은 돼 있는데 실제로 호출된 적이 없는 경로라는 뜻이다.

> **피드백** — "연결돼 있지만 실행된 적 없는 코드"는 테스트가 없다는 신호다. 각 엔드포인트를 한 번씩 호출해보는 **스모크 테스트**만 있었어도 require 누락은 즉시 드러난다. supertest로 `GET /api/admin/...` 전부를 순회하는 테스트 하나면 충분했다.

## models/ — 만들다 만 Repository 층

`Notice.js`와 `inquiry.js` 두 개가 있고, **어느 컨트롤러도 이걸 쓰지 않는다.**

```javascript
// models/Notice.js — 존재한다
async createNotice({ title, content }) {
  const sql = "INSERT INTO notice (title, content) VALUES (?, ?)";
  ...
}

// controllers/noticeController.js — 하지만 직접 쿼리한다
await db.query("INSERT INTO notice (title, content, created_at) VALUES (?, ?, NOW())", ...);
```

**Repository 패턴** — 데이터 접근을 한 층에 모아 상위가 SQL을 모르게 하는 구조 — 을 시작했다가 중단한 흔적이다. 더 나쁜 건 두 코드가 미묘하게 어긋나 있다는 것:

- 모델은 `created_at`을 생략(DB DEFAULT 의존), 컨트롤러는 `NOW()` 명시
- `inquiry.js` 모델은 `name` 컬럼, 컨트롤러는 `user_id` 컬럼

모델을 만든 뒤 스키마가 바뀌었고 모델만 갱신되지 않았다. 읽는 사람은 어느 쪽이 진짜 스키마인지 코드만으로 알 수 없다.

> **피드백** — 계층은 "전부 쓰거나 전부 지우거나" 둘 중 하나였어야 했다. 반만 있는 계층은 없는 것보다 나쁘다 — 정보가 아니라 오정보를 주기 때문이다.
> 완성했다면 이렇게 이어진다: `routes → controllers → models → db`. 컨트롤러는 HTTP(상태코드·파라미터)만 알고, 모델은 SQL만 안다. 테스트할 때 모델을 가짜로 갈아끼우기도 쉬워진다. Java day09 MVC 종합예제 의 `BoardDAO`가 정확히 이 역할이었다 — 자바에서 만든 구조를 JS로 옮길 기회였는데 절반에서 멈췄다.
> 그리고 **스키마의 원본이 없다.** `.sql` 파일이 저장소에 없어서 테이블 구조를 코드의 쿼리에서 역추적해야 한다. `schema.sql` 하나 커밋해두는 것, 나아가 마이그레이션 도구(knex 등)로 스키마 변경을 코드로 남기는 것이 다음 단계다.

## 응답 형식 — 6가지가 섞여 있다

```javascript
res.json(results);                             // 배열 그대로
res.json({ data: ... });                       // data 래핑
res.json({ success: true, data: ... });        // success + data
res.json({ success: true, message: "..." });   // success + message
res.status(500).json({ error: "..." });        // error 키
res.status(500).json({ message: "서버 오류" }); // message 키
```

파일마다 응답 모양이 달라서, 프론트에 `if (!Array.isArray(data))` 같은 방어 코드가 생겼다.

> **피드백** — 응답 **직렬화 규약**을 초반에 한 장 정하고 시작했어야 했다. `{ success, data, message }` 하나로 통일하면 프론트의 방어 코드가 사라지고, 에러 처리를 axios 인터셉터 한 곳으로 모을 수 있다. 규약은 코드보다 먼저 정하는 게 싸다.

## 관련 노트

[[보드게임카페예약사이트 프로젝트 MOC]] · [[보드게임 - routes 분석 - 고객지원과 관리자|routes 분석 - 고객지원과 관리자]] · [[보드게임 - 전문용어 정리|전문용어 정리]]
