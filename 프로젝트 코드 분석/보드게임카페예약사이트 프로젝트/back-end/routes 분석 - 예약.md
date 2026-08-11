---
출처: Claude 분석
원본: shirhal/back-end/routes
작성일: 2026-08-11
tags: [프로젝트, 일지, 보드게임카페예약사이트, 예약, sql]
---

# routes 분석 - 예약

대상: `routes/reservations.js`(177줄) · `routes/availabilityRoutes.js` · `routes/myreservations.js`
상위: [[보드게임카페예약사이트 프로젝트 개요]]

백엔드에서 가장 밀도 높은 구간이다. 동시성 문제를 처음으로 정면에서 만난 코드이기도 하다.

## reservations.js — 예약 생성

### 방어 로직 3단

예약 INSERT 전에 세 가지를 순서대로 검사한다.

```javascript
// ① 영업시간(10:00~22:00) 안인가
if (startMoment.isBefore(openTime) || endMoment.isAfter(closeTime)) → 400

// ② 같은 유저가 그 시간대에 이미 예약했는가
SELECT 1 FROM reservations WHERE user_id = ? AND end_time > ? AND reservation_date < ?  → 409

// ③ 그 좌석 타입(테이블식/좌식)이 이미 5개 다 찼는가
SELECT COUNT(*) ... WHERE reservation_date < ? AND end_time > ? AND seating_type = ?  → 409
```

**구간 겹침 판정**은 이 조건 하나로 끝난다.

```
기존.end_time > 신규.start  AND  기존.start < 신규.end
```

"시작이 사이에 있는가"만 보면 새 예약이 기존 예약을 통째로 감싸는 경우를 놓치는데, 이 두 조건이면 모든 겹침이 걸린다. 세 군데 검사에서 같은 조건을 일관되게 썼다.

가격은 `5000 * hours * players`로 서버에서 계산한다. 프론트가 보낸 금액을 믿지 않는 방향은 맞았다.

### 방 배정 — 무작위 재시도

```javascript
while (!roomAvailable) {
  room_id = seating_type === "테이블식"
    ? Math.floor(Math.random() * 5) + 1     // 1~5번 방
    : Math.floor(Math.random() * 5) + 6;    // 6~10번 방
  roomAvailable = await checkRoomAvailability(room_id, startTime, endTime);
}
```

빈 방을 무작위로 찍고, 차 있으면 다시 찍는다. 앞의 ③ 검사 덕에 "전부 찬" 상태로는 보통 진입하지 않지만, 검사와 배정 사이에 다른 요청이 들어오면 **무한 루프**가 된다. 운이 나쁘면 같은 방을 여러 번 찍어 DB 조회를 낭비하기도 한다.

> **피드백** — 반복 대신 집합 연산 하나로 끝나는 문제였다.
>
> ```sql
> SELECT room_id FROM rooms
> WHERE room_id BETWEEN ? AND ?
>   AND room_id NOT IN (
>     SELECT room_id FROM reservations
>     WHERE end_time > ? AND reservation_date < ? AND is_deleted = 0
>   )
> LIMIT 1
> ```
>
> "빈 방 찾기"를 애플리케이션 반복문이 아니라 SQL의 **부정 조건 서브쿼리**로 옮기면 루프도, 낭비 조회도, 무한 루프 가능성도 사라진다. → [[SQL day03 DML과 조인]]

### 트랜잭션 부재

```javascript
const { room_id } = await assignRoom(...);        // ① 빈 방 확인
await db.query("INSERT INTO reservations ...");    // ② 삽입
```

①과 ② 사이에 다른 요청이 같은 방을 잡으면 한 방에 두 예약이 들어간다. **경쟁 상태(race condition)** 다. 학기 프로젝트의 트래픽에서는 드러나지 않았지만 구조적으로 열려 있는 구멍이다.

> **피드백** — 확인과 삽입은 하나의 **트랜잭션**으로 묶고, 확인 쿼리에 `FOR UPDATE`를 붙여 잠갔어야 했다.
>
> ```javascript
> const conn = await db.getConnection();
> await conn.beginTransaction();
> // SELECT ... FOR UPDATE → INSERT → commit / 실패 시 rollback → release
> ```
>
> 이 패턴이 **ACID**의 격리성(Isolation)을 코드로 쓰는 방법이다. 예약·결제·재고처럼 "확인하고 쓰는" 로직에는 예외 없이 필요하다. → [[SQL day01 데이터베이스 기초]]

## availabilityRoutes.js — 잔여 좌석 조회

10:00~22:00을 30분 단위로 쪼개서, 슬롯마다 겹치는 예약 수를 세고 `총 방 수 - 겹침`을 내려준다. 예약 실패를 사후에 알리는 대신 **가능한 시간을 미리 보여주는** UX를 만든 근거 데이터다.

다만 슬롯이 24개면 **쿼리도 24번** 나간다. 반복문 안에서 쿼리하는 전형적인 **N+1 문제**다.

> **피드백** — 그날 예약을 한 번에 가져와서 메모리에서 슬롯별로 세면 쿼리 1번으로 끝난다. 더 SQL답게 하면 30분 슬롯 테이블(또는 재귀 CTE)과 `LEFT JOIN` + `GROUP BY`로 DB에서 집계를 끝낼 수도 있다. "반복문 안의 await db.query"가 보이면 일단 의심하는 습관으로 이어져야 한다.

## myreservations.js — 내 예약 조회

```sql
SELECT r.*, ro.room_name, DATE_FORMAT(r.reservation_date, '%Y-%m-%d %H:%i') AS ...
FROM reservations r JOIN rooms ro ON r.room_id = ro.room_id
WHERE r.user_id = ? AND r.is_deleted = 0
```

`rooms`와 **JOIN**해서 방 이름까지 붙이고, `is_deleted = 0`으로 **소프트 삭제**된 예약을 걸렀다. 날짜 포맷을 `DATE_FORMAT`으로 DB에서 맞춰 내려보낸 것도 프론트 부담을 줄였다.

> **피드백** — 방향은 맞다. 남은 문제는 `user_id`를 URL 파라미터로 받는다는 것. 로그인한 사용자가 누구인지 서버가 모르기 때문에 `/api/myreservations/다른아이디`를 호출하면 남의 예약이 보인다. 인증 토큰에서 사용자를 꺼내는 구조였다면 URL에 `user_id`가 등장할 일 자체가 없다. → [[routes 분석 - 인증과 유저]]

## 관련 노트

[[보드게임카페예약사이트 프로젝트 개요]] · [[components 분석 - Reservation과 결제]] · [[hooks 분석]] · [[전문용어 정리]] · [[SQL day01 데이터베이스 기초]] · [[SQL day03 DML과 조인]]
