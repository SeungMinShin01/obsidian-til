---
출처: Claude 분석
원본: KDT_2026/2026B_BE/src/database/day04.sql
작성일: 2026-08-11
tags: [sql, day04, GROUP BY, 집계, 정렬, 페이징]
---

# SQL day04 — 집계와 정렬

> 실습 파일: `database/day04.sql` (member/buy 테이블 + GROUP BY·집계·정렬·LIMIT)
> 허브: [[CS 이론 MOC]] · 이전: [[SQL day03 DML과 조인]]
> `day05.sql`은 현재 빈 파일입니다 — 다음 수업(day05) 준비로 비워둔 상태. 내용이 채워지면 SQL day05 노트로 정리합니다.

## 1. 배운 내용

### 1-1. GROUP BY — 그룹당 대표값 하나

```sql
SELECT bpname FROM buy GROUP BY bpname;          -- 제품명 기준 그룹
-- SELECT * FROM buy GROUP BY bpname;            -- [오류]
-- SELECT bpname, mid FROM buy GROUP BY bpname;  -- [오류]
```

그룹으로 묶으면 **그룹당 행이 하나**가 됩니다. 그래서 SELECT에 올 수 있는 것은 ① 그룹 기준 컬럼 ② 집계함수 결과, 둘뿐입니다. `mid`처럼 그룹 안에서 값이 여러 개인 컬럼을 그냥 조회하면 "여러 값 중 뭘 보여줄지" 정할 수 없어서 오류가 납니다.

> "~별", "~끼리"라는 말이 나오면 GROUP BY입니다. 회원별 구매수량, 지역별 평균 키.

### 1-2. 집계함수 5종

```sql
SELECT sum(bamount)   FROM buy;   -- 합계
SELECT avg(bamount)   FROM buy;   -- 평균
SELECT min(bamount)   FROM buy;   -- 최솟값
SELECT max(bamount)   FROM buy;   -- 최댓값
SELECT count(bamount) FROM buy;   -- 개수 (NULL 제외)
SELECT count(*)       FROM buy;   -- 개수 (NULL 포함)
```

**`count(필드)`와 `count(*)`는 다릅니다.** 필드를 지정하면 그 필드가 NULL인 행은 세지 않습니다. "행 수"가 필요하면 `count(*)`가 정답입니다.

### 1-3. GROUP BY + 집계함수

```sql
SELECT mid, sum(bamount) 총구매수량        FROM buy GROUP BY mid;  -- 회원별 총 구매수량
SELECT mid, sum(bamount * bprice) 총구매금액 FROM buy GROUP BY mid;  -- 회원별 총 구매금액
SELECT count(*), mid                       FROM buy GROUP BY mid;  -- 회원별 구매 횟수
```

집계 안에서 산술식(`bamount * bprice`)이 됩니다 — 행마다 수량×가격을 구한 뒤 그룹으로 합칩니다. 별칭(`총구매수량`)은 `AS` 생략 형태입니다( [[SQL day03 DML과 조인]] 1-2).

### 1-4. WHERE vs HAVING — 그룹 전 조건 / 그룹 후 조건

```sql
SELECT mid, sum(bamount) 총구매수량
FROM buy
GROUP BY mid
HAVING 총구매수량 > 5;      -- 그룹핑 *후* 집계 결과에 거는 조건

-- SELECT ... FROM buy WHERE 총구매수량 > 5 GROUP BY mid;   -- [오류]
```

WHERE에서 별칭·집계 결과를 못 쓰는 이유는 **처리 순서** 때문입니다. WHERE는 그룹핑 *전*에 행 단위로 걸러지는데, 그 시점에는 `sum()`이 아직 계산되지 않았습니다.

```
WHERE  → 어떤 행을 집계에 넣을까   (그룹 전, 행 단위)
HAVING → 어떤 그룹을 결과에 남길까 (그룹 후, 그룹 단위)
```

둘은 대체재가 아니라 역할이 다릅니다. "3개 이상 산 것만 집계"는 WHERE, "합계가 5 넘는 회원만"은 HAVING.

### 1-5. ORDER BY — 정렬과 다중정렬

```sql
SELECT * FROM member ORDER BY mdebut;              -- 오름차순(ASC, 기본값)
SELECT * FROM member ORDER BY mdebut DESC;         -- 내림차순
SELECT * FROM member ORDER BY maddr DESC, mdebut ASC;  -- 다중정렬
```

**다중정렬**은 1차 정렬에서 값이 같은 행들끼리만 2차 기준으로 다시 정렬합니다. 지역으로 먼저 정렬하고, 같은 지역 안에서 데뷔일 순 — 언제나 "동점 처리 규칙"이라고 읽으면 됩니다.

내림차순의 감각: `3 2 1`, `다 나 가`, `C B A`, `8-11 → 8-10` (최신 날짜가 위).

### 1-6. LIMIT — 결과 제한과 페이징

```sql
SELECT * FROM member LIMIT 2;       -- 앞에서 2개
SELECT * FROM member LIMIT 0, 2;    -- 0번부터 2개 (1페이지)
SELECT * FROM member LIMIT 5, 5;    -- 5번부터 5개 (2페이지, 페이지당 5개)
```

`LIMIT 시작인덱스, 개수` — 시작은 0번부터. **페이징 공식**: 페이지당 n개일 때 p페이지는 `LIMIT (p-1)*n, n`.

### 1-7. 절의 순서 — 문법 순서이자 사실상의 처리 순서

```sql
SELECT 필드
FROM 테이블
WHERE 행조건
GROUP BY 그룹필드
HAVING 그룹조건
ORDER BY 정렬필드
LIMIT 시작, 개수;
```

처리 흐름으로 읽으면: 테이블에서(FROM) → 행을 거르고(WHERE) → 묶고(GROUP BY) → 그룹을 거르고(HAVING) → 정렬하고(ORDER BY) → 자른다(LIMIT). WHERE에서 별칭이 안 되는 이유, HAVING이 GROUP 뒤에 오는 이유가 이 순서 하나로 전부 설명됩니다.

## 2. 추가로 알면 좋은 활용법

### 2-1. GROUP BY + JOIN — 이름을 붙인 집계

회원별 집계에 `mid` 대신 그룹명을 보여주려면 [[SQL day03 DML과 조인]] 의 JOIN과 합칩니다.

```sql
SELECT m.mname, sum(b.bamount * b.bprice) 총구매금액
FROM buy b
JOIN member m ON b.mid = m.mid
GROUP BY m.mname
ORDER BY 총구매금액 DESC;
```

집계·조인·정렬이 한 쿼리에 모이는 이 형태가 실무 리포트 쿼리의 기본형입니다.

### 2-2. ORDER BY 없는 LIMIT은 순서를 보장하지 않는다

`LIMIT`만 쓰면 "어떤 2개"가 올지 DB 마음입니다. 페이징은 반드시 `ORDER BY`와 함께 — 정렬 기준이 고정돼야 2페이지가 1페이지와 겹치지 않습니다.

### 2-3. 집계와 NULL

`buy`의 `bgname`에 NULL이 섞여 있는 것이 좋은 실험 재료입니다. `count(bgname)` < `count(*)`이고, `avg()`도 NULL을 빼고 나눕니다. "NULL은 0이 아니라 집계에서 빠진다"는 성질이 통계 숫자를 조용히 바꿉니다.

### 2-4. GROUP_CONCAT — 그룹 안의 값들을 이어붙이기

그룹당 하나만 보여줄 수 있다는 제약을 우회해서, 그룹 안의 값들을 문자열로 모아볼 수 있습니다.

```sql
SELECT mid, GROUP_CONCAT(bpname) 구매목록 FROM buy GROUP BY mid;
-- MMU  아이폰,에어팟,지갑,지갑
```

## 3. 더 나아가 알면 좋은 것

### 3-1. 실전 코드에서 이 문법들이 쓰인 자리

이전 프로젝트의 백엔드가 오늘 배운 것들의 실전판입니다.

| 오늘 배운 것 | 프로젝트에서 |
| --- | --- |
| `ORDER BY likes DESC LIMIT 3` | 인기 게임 TOP3 → routes 분석 - 보드게임과 리뷰 |
| `LIMIT ?, ?` 페이징 | 무한 스크롤의 서버 쪽 → routes 분석 - 보드게임과 리뷰 |
| `count(*)` | 관리자 대시보드 수치 4종 → controllers와 models 분석 |
| GROUP BY 집계 | 반복문 쿼리(N+1)를 한 방에 끝내는 해법 → routes 분석 - 예약 |

특히 마지막 — 30분 슬롯마다 `COUNT` 쿼리를 24번 돌린 코드는, 오늘 배운 GROUP BY로 1번에 끝낼 수 있습니다( 공부할 코드 - SQL과 데이터 4번 연습).

### 3-2. 오프셋 페이징의 한계

`LIMIT 100000, 20`은 DB가 100,020행을 만들고 100,000개를 버립니다. 깊은 페이지일수록 느려지는 구조라, 대량 데이터에서는 커서 방식(`WHERE id < 마지막ID LIMIT 20`)으로 넘어갑니다 → 전문용어 정리 페이지네이션 항목.

### 3-3. 윈도우 함수 — 다음 단계

GROUP BY는 그룹당 한 행으로 접지만, **윈도우 함수**는 행을 유지한 채 집계를 옆에 붙입니다.

```sql
SELECT mid, bpname, bprice,
       RANK() OVER (PARTITION BY mid ORDER BY bprice DESC) 가격순위
FROM buy;
```

"회원별 구매 순위", "누적 합계" 같은 요구가 나오면 이 키워드(`OVER`, `PARTITION BY`, `RANK`, `ROW_NUMBER`)를 찾으면 됩니다.

## 실습 파일

- `2026B_BE/src/database/day04.sql`
- `2026B_BE/src/database/day05.sql` (현재 빈 파일 — day05 수업 대기)
- `2026B_BE/src/Note/DB.txt` (누적 요약 노트)

## 관련 노트

[[CS 이론 MOC]] · [[SQL day03 DML과 조인]] · [[Java day09 ArrayList]]
