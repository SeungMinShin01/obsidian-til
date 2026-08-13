---
출처: Claude 분석
원본: shirhal/back-end
작성일: 2026-08-11
tags: [프로젝트, sql]
---

# 공부할 코드 - SQL과 데이터

백엔드·크롤러에서 원리를 정확히 알고 넘어가야 하는 코드 4개.
허브: [[보드게임카페예약사이트 프로젝트에서 배울 것]]

## 1. 구간 겹침 판정 — 조건 두 개면 모든 겹침이 걸린다

`reservations.js`에서 유저 중복·좌석 포화·방 배정 세 곳에 반복해서 쓴 조건입니다.

```sql
WHERE 기존.end_time > 신규.start_time
  AND 기존.reservation_date < 신규.end_time
```

두 구간 A, B가 겹친다 ⟺ `A.끝 > B.시작 AND A.시작 < B.끝`. 이것이 겹침의 **필요충분조건**입니다.

### 왜 두 개로 충분한가

겹치는 모양은 네 가지뿐입니다.

```
A:      ├──────┤
B: ├──────┤            앞겹침   → A.끝>B.시작 ✓  A.시작<B.끝 ✓
B:          ├──────┤   뒤겹침   → ✓ ✓
B:    ├──┤             포함됨   → ✓ ✓
B: ├────────────┤      포함     → ✓ ✓
B: ├──┤                안 겹침  → A.시작<B.끝 ✗
```

흔한 오답은 "B의 시작이 A 안에 있는가"만 보는 것 — 그러면 B가 A를 통째로 감싸는 네 번째 경우를 놓칩니다. 수직선을 직접 그려 다섯 경우를 조건에 대입해보는 것이 이 코드에서 얻는 가장 확실한 공부입니다.

### 활용

예약·회의실·일정·재고 기간·쿠폰 유효기간 — "기간이 겹치면 안 되는" 모든 도메인에서 이 두 줄이 그대로 재사용됩니다. 경계 처리(`>` vs `>=`)만 도메인마다 결정하면 됩니다: 10:00에 끝나는 예약과 10:00에 시작하는 예약을 겹침으로 볼 것인가 — 이 프로젝트는 `>`라서 안 겹침으로 처리했고, 그게 맞는 선택이었습니다.

연결: SQL day03 DML과 조인 WHERE 조건 조합 · Java day03 연산자 논리 연산자 · 코드 맥락은 [[routes 분석 - 예약]]

## 2. ORDER BY 화이트리스트 — 값 자리 vs 구조 자리

```javascript
const validColumns = ["likes", "difficulty", "game_id"];
const validOrders = ["ASC", "DESC"];
if (!validColumns.includes(sortBy)) return res.status(400).json({ ... });
db.query(`SELECT * FROM board_game ORDER BY ${sortBy} ${sortOrder}`);
```

이 코드의 학습 가치는 **"왜 여기만 `?` 바인딩을 안 썼는가"를 설명할 수 있게 되는 것**입니다.

### 원리

파라미터 바인딩은 SQL의 **값** 자리에만 동작합니다. DB는 쿼리를 먼저 컴파일(구조 확정)하고 값을 나중에 끼우는데, 컬럼명은 값이 아니라 **구조**라서 컴파일 시점에 정해져야 합니다. 그래서 바인딩이 원리적으로 불가능하고, 문자열 조립이 불가피하며, 조립하는 순간 인젝션 가능성이 생기므로 허용 목록 검사가 유일한 방어가 됩니다.

```
값 자리   → WHERE user_id = ?          → 바인딩으로 방어
구조 자리 → ORDER BY {컬럼}, {테이블}   → 화이트리스트로 방어
```

### 활용

이 구분이 서면 어떤 쿼리 빌더·ORM을 쓰든 위험 지점을 스스로 찾습니다. 예: knex의 `orderBy(사용자입력)`도 내부적으로 같은 문제가 있어 검증이 필요합니다. 동적 테이블 선택, 동적 컬럼 프로젝션도 전부 같은 자리입니다. 블랙리스트(금지어 필터)는 우회 조합이 늘 존재하므로 **항상 화이트리스트**로 짭니다.

연결: [[전문용어 정리]] SQL 인젝션 항목 · 코드 맥락은 [[routes 분석 - 보드게임과 리뷰]]

## 3. 멱등 파이프라인 — 다른 도구, 같은 성질

크롤러 파이프라인의 양 끝이 같은 성질(재실행해도 결과 동일)을 다른 도구로 만들었습니다.

```python
# 수집 (Python) — dict 키 덮어쓰기
merged = {g["name_kr"]: g for g in existing + game_list}
```

```sql
-- 적재 (SQL) — 업서트
INSERT INTO board_game (...) VALUES (...)
ON DUPLICATE KEY UPDATE game_name_kr = VALUES(game_name_kr), ...
```

### 원리

Python 쪽: dict는 같은 키에 마지막 값만 남습니다. `existing + game_list` 순서라서 새 데이터가 이깁니다. SQL 쪽: UNIQUE 제약에 걸리면 INSERT 대신 UPDATE가 실행됩니다. **`ON DUPLICATE KEY`는 UNIQUE/PK 제약이 없으면 아무 일도 하지 않는다**는 것이 핵심 — 제약이 곧 "중복"의 정의이기 때문입니다.

배치 작업은 반드시 실패하고, 실패하면 다시 돌립니다. 그래서 멱등성이 배치 설계의 1원칙입니다. 이 파이프라인은 "실패하면 그냥 다시 돌린다"가 성립합니다.

### 공부 순서

1. `game_likes`에 UNIQUE가 없어서 동시 요청에 중복이 뚫리는 것( [[routes 분석 - 보드게임과 리뷰]] )과 비교 — 같은 제약이 여기서는 멱등의 기반, 저기서는 최종 방어선
2. PostgreSQL의 `ON CONFLICT DO UPDATE`와 문법 비교
3. HTTP 메소드로 확장: GET/PUT/DELETE는 멱등, POST는 아님 — 결제 재시도 때 왜 멱등 키(idempotency key)를 쓰는지까지

연결: SQL day02 테이블과 제약조건 · Python 정리본 인덱스 · 코드 맥락은 [[crawler 분석]]

## 4. 30분 슬롯 계산 — 시간 코드의 함정 모음

`availabilityRoutes.js`는 10:00~22:00을 30분씩 자르며 슬롯마다 잔여 방 수를 계산합니다. 시간을 다루는 코드에서 만나는 함정이 한 파일에 모여 있습니다.

```javascript
while (startTime.isBefore(endTime)) {
  const slotStart = startTime.clone();               // ← clone이 없으면?
  const slotEnd = startTime.clone().add(30, "minutes");
  const [conflicts] = await db.query("SELECT COUNT(*) ...");  // ← 반복문 안 쿼리
  startTime.add(30, "minutes");                      // ← 원본 변이로 전진
}
```

### 함정 셋

1. **가변 객체의 변이** — moment 객체는 `add()`가 원본을 바꿉니다. `clone()` 없이 `slotEnd = startTime.add(30,...)`라고 쓰면 루프 변수까지 오염됩니다. JS day07 객체 의 참조 문제가 시간 라이브러리에서 재현되는 것. (요즘 표준인 dayjs·date-fns가 **불변**을 택한 이유가 이것입니다)
2. **N+1 쿼리** — 슬롯 24개 = 쿼리 24번. 반복문 안의 `await db.query`는 항상 의심 대상입니다.
3. **경계 정의** — 슬롯 [10:00, 10:30)과 예약 [10:30, 12:00)이 안 겹치려면 겹침 조건의 부등호가 정확해야 합니다. 1번 항목의 경계 처리와 같은 문제입니다.

### 연습

같은 로직을 세 버전으로 다시 써보기: ① 지금 그대로(쿼리 24번) → ② 그날 예약 전체 1회 조회 + 메모리 집계 → ③ `GROUP BY` DB 집계. 쿼리 수·코드량·읽기 난이도를 비교하면 "어디서 계산할 것인가"의 감각이 생깁니다.

연결: SQL day03 DML과 조인 GROUP BY · JS day13 웹 스토리지와 인터벌 시간 다루기 · 코드 맥락은 [[routes 분석 - 예약]]

## 관련 노트

[[보드게임카페예약사이트 프로젝트에서 배울 것]] · [[공부할 코드 - React 패턴]] · [[전문용어 정리]]
