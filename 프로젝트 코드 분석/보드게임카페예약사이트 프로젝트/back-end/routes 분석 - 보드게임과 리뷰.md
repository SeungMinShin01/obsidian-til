---
출처: Claude 분석
원본: shirhal/back-end/routes
작성일: 2026-08-11
tags: [프로젝트, sql]
---

# routes 분석 - 보드게임과 리뷰

대상: `routes/boardgames.js` · `routes/gamelikesRoutes.js` · `routes/reviewRoutes.js`
상위: [[보드게임카페예약사이트 프로젝트 MOC]]

## boardgames.js — 목록·검색·필터·정렬

### 페이지네이션

```sql
SELECT DISTINCT * FROM board_game ORDER BY game_id DESC LIMIT ? OFFSET ?
```

`LIMIT/OFFSET` **오프셋 페이지네이션**으로 무한 스크롤의 서버 쪽을 받친다. 다만 `DISTINCT *`는 이상하다. PK가 있는 테이블의 전체 컬럼 `DISTINCT`는 중복이 나올 수 없어서 정렬 비용만 낸다. 화면에 중복이 보여서 급하게 붙였던 것 같은데, 진짜 원인은 크롤러 적재나 프론트 상태 누적 쪽이었을 것이다.

> **피드백** — 증상(중복 표시)에 대증요법을 쓰기 전에 원인(어디서 중복이 생기나)을 추적하는 순서였어야 했다. 그리고 `SELECT *`는 목록 조회에서 `description` 같은 긴 컬럼까지 끌고 온다. 필요한 컬럼 명시가 기본. 데이터가 커지면 오프셋 방식 자체도 뒤 페이지로 갈수록 느려지므로 **커서 페이지네이션**(`WHERE game_id < 마지막ID LIMIT n`)으로 넘어가는 게 다음 단계다.

### 정렬 — 화이트리스트

```javascript
const validColumns = ["likes", "difficulty", "game_id"];
const validOrders = ["ASC", "DESC"];
if (!validColumns.includes(sortBy)) return res.status(400).json({ error: "정렬 필드가 잘못되었습니다." });
const [results] = await db.query(`SELECT * FROM board_game ORDER BY ${sortBy} ${sortOrder}`);
```

`ORDER BY`의 컬럼명은 `?` 바인딩이 안 되니 문자열을 이어붙일 수밖에 없고, 그래서 **화이트리스트**로 막았다. 이게 없으면 `ORDER BY` 자리가 그대로 **SQL 인젝션** 통로가 된다. 값이 아니라 "구조"가 들어가는 자리는 바인딩이 아니라 허용 목록으로 지킨다는 원칙을 여기서 처음 실행했다.

## gamelikesRoutes.js — 추천

```javascript
const [check] = await db.query(
  "SELECT 1 FROM game_likes WHERE user_id = ? AND game_id = ?", [user_id, id]);
if (check.length > 0) return res.status(409).json({ message: "이미 추천한 게임입니다." });

await db.query("INSERT INTO game_likes (user_id, game_id) VALUES (?, ?)", [user_id, id]);
await db.query("UPDATE board_game SET likes = likes + 1 WHERE game_id = ?", [id]);
```

유저-게임의 N:M 관계를 `game_likes` **중간 테이블**로 풀고, 중복 추천을 409로 거른다. `likes = likes + 1`을 DB에서 계산하는 것도 맞는 선택 — 애플리케이션에서 읽고 더해서 쓰면 동시 요청 때 증가분을 잃는다.

TOP3 조회는 `ORDER BY likes DESC LIMIT 3`. 단순하고 충분하다.

> **피드백** — 확인-삽입-갱신 3단이 트랜잭션이 아니라서, 동시에 누르면 중복 검사를 둘 다 통과할 수 있다. `game_likes(user_id, game_id)`에 **UNIQUE 제약**을 걸면 DB가 최종 방어선이 되고, 코드는 중복 INSERT 에러를 409로 번역만 하면 된다. "애플리케이션 검사 + DB 제약"의 이중화가 정석이다. → SQL day02 테이블과 제약조건
> `likes` 컬럼 자체도 사실 `COUNT(game_likes)`로 유도 가능한 **비정규화** 값이다. 성능 때문에 두는 건 흔한 선택이지만, 어긋났을 때 재계산하는 보정 쿼리를 하나 마련해뒀어야 했다.

## reviewRoutes.js — 리뷰 CRUD

리뷰는 게임당 유저 1개로 제한했다. 등록 전에 기존 리뷰 존재를 확인하고, 수정·삭제는 `user_id` 일치를 확인한다.

```javascript
router.use((req, res, next) => { next(); });   // 빈 미들웨어
```

의미 없는 빈 미들웨어가 하나 있다. 로깅이나 인증을 넣으려던 자리로 보인다.

> **피드백** — 소유권 확인의 `user_id`가 **요청 본문/쿼리에서** 온다는 게 문제다. 클라이언트가 임의로 넣을 수 있는 값이라, 남의 `user_id`를 넣으면 남의 리뷰가 지워진다. 소유권 검증의 기준값은 반드시 서버가 신뢰하는 곳(세션·토큰)에서 와야 한다. 인증 부재가 여기서도 연쇄로 문제를 만든다 — 뿌리는 같다. → [[routes 분석 - 인증과 유저]]

## 관련 노트

[[보드게임카페예약사이트 프로젝트 MOC]] · [[hooks 분석]] · [[components 분석 - BoardGame과 Rule]] · [[crawler 분석]] · [[전문용어 정리]]
