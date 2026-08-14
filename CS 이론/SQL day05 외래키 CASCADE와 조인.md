---
출처: Claude 분석
원본: KDT_2026/2026B_BE/src/database/day05.sql, practice5.sql
작성일: 2026-08-14
tags: [학습, sql]
---

# SQL day05 — 외래키 CASCADE와 조인

> 실습 파일: `database/day05.sql` (table1/table2 + FK 참조 동작 + INNER JOIN 3형태 + OUTER JOIN·합집합·차집합), `database/practice5.sql` (3테이블 스키마 실전 연습)
> 허브: [[CS 이론 MOC]] · 이전: [[SQL day04 집계와 정렬]]

이번에는 두 테이블을 PK-FK로 이어놓고, ① 부모 값이 바뀌면 자식은 어떻게 되는지(참조 동작), ② 이어진 두 테이블을 어떻게 하나로 조회하는지(JOIN)를 정리합니다. PK/FK 선언 자체는 [[SQL day02 테이블과 제약조건]], JOIN 첫 등장은 [[SQL day03 DML과 조인]] 에서 다뤘고, 여기서는 그 둘을 이어 붙입니다.

## 1. 배운 내용

### 1-1. 두 테이블을 PK-FK로 잇기

```sql
create table table1(
  num_pk int,
  constraint primary key( num_pk )       -- table1의 식별키
);

create table table2(
  no_pk int,
  constraint primary key( no_pk ),
  num_fk int,
  constraint foreign key( num_fk ) references table1( num_pk )  -- table1.num_pk를 참조
  on update cascade on delete cascade
);
```

`table2.num_fk`는 `table1.num_pk`를 가리키는 **외래키(FK)** 입니다. 이렇게 걸면 `num_fk`에는 `table1`에 실제로 있는 `num_pk` 값만 들어갈 수 있습니다 — 없는 값을 넣으려 하면 참조 무결성 위반으로 거부됩니다. FK는 "부모 테이블에 존재하는 값만 허용한다"는 약속입니다.

| 용어 | 이 예제에서 |
| --- | --- |
| 부모 테이블 | `table1` (참조되는 쪽, PK 보유) |
| 자식 테이블 | `table2` (참조하는 쪽, FK 보유) |
| 참조 대상 | `table1( num_pk )` |

### 1-2. ON UPDATE / ON DELETE CASCADE — 부모가 바뀌면 자식도 따라간다

```sql
constraint foreign key( num_fk ) references table1( num_pk )
on update cascade   -- 부모의 num_pk가 수정되면 자식 num_fk도 같이 수정
on delete cascade   -- 부모의 num_pk가 삭제되면 그 값을 참조하던 자식 행도 같이 삭제
```

이게 이번 수업의 핵심입니다. FK만 걸어두면 기본 동작은 "부모를 함부로 못 지운다"(RESTRICT)입니다 — 자식이 참조 중인 부모 행은 삭제·수정이 막힙니다. 여기에 `on delete cascade`를 붙이면 그 제약이 "막는다"에서 "**연쇄로 같이 처리한다**"로 바뀝니다. 부모 행을 지우면 그 값을 참조하던 자식 행들이 자동으로 함께 지워집니다.

정리하면 참조 동작(referential action)은 부모가 바뀔 때 자식을 어떻게 할지 정하는 규칙입니다.

| 옵션 | 부모 삭제/수정 시 자식은 |
| --- | --- |
| `RESTRICT` (기본) | 참조 중이면 부모 작업을 막음 |
| `CASCADE` | 자식도 같이 삭제/수정 |
| `SET NULL` | 자식 FK를 NULL로 |
| `NO ACTION` | RESTRICT와 사실상 동일 |

### 1-3. 샘플 데이터와 참조 관계

```sql
insert into table1 values( 1 ),( 2 ),( 3 ),( 4 ),( 5 );
insert into table2 values( 1,1 ),( 2,2 ),( 3,1 ),( 4,1 ),( 5,2 );
```

`table2`의 `num_fk`를 보면 `1,2,1,1,2` — 전부 `table1`에 있는 값입니다(무결성 통과). 참조 분포를 세어 보면 `num_pk=1`을 3개 행이, `num_pk=2`를 2개 행이 참조합니다. 이 관계가 아래 JOIN 결과 행 수를 결정합니다.

### 1-4. JOIN — 이어진 두 테이블을 하나로 조회

두 테이블을 한 번에 조회하면 먼저 **모든 조합**이 나옵니다(카티션 곱, cross join).

```sql
SELECT * FROM table1, table2;   -- 5 × 5 = 25행 (의미 없는 조합까지 전부)
```

여기서 "FK가 실제로 가리키는 짝"만 남기면 우리가 원하는 JOIN이 됩니다. 방법이 세 가지로 진화합니다.

```sql
-- [1] WHERE로 조인 조건
SELECT * FROM table1, table2
WHERE table1.num_pk = table2.num_fk;      -- 5행

-- [2] 테이블 별칭으로 짧게
SELECT * FROM table1 t1, table2 t2
WHERE t1.num_pk = t2.num_fk;              -- 같은 결과

-- [3] INNER JOIN ... ON (표준 조인 문법)
SELECT * FROM table1 t1
INNER JOIN table2 t2 ON t1.num_pk = t2.num_fk;   -- 같은 결과
```

세 쿼리 결과는 같습니다(5행). 25개 조합 중 `num_pk = num_fk`인 짝만 남기니, 자식 행 수(5)만큼 나옵니다.

| 방식 | 조인 조건이 붙는 곳 |
| --- | --- |
| `FROM a, b WHERE ...` | WHERE 절 (구식·암시적 조인) |
| `a INNER JOIN b ON ...` | ON 절 (명시적 조인) |

`INNER JOIN ... ON`을 쓰는 편이 안전합니다. 조인 조건(`ON`)과 데이터 필터(`WHERE`)가 분리돼 읽기 좋고, `ON`을 빠뜨리면 문법이 어색해져 실수(조건 없는 카티션 곱)를 눈치채기 쉽습니다.

### 1-5. OUTER JOIN — 짝 없는 행까지 살려서 조회

INNER JOIN이 "양쪽에 다 있는 짝만" 남긴다면, OUTER JOIN은 한쪽 테이블의 행을 짝이 없어도 전부 남깁니다. 짝이 없는 자리는 NULL로 채워집니다.

```sql
-- 왼쪽(table1) 전부 + 오른쪽 교집합. table1의 num_pk가 모두 참조되므로 여기선 8행
SELECT * FROM table1 t1
LEFT OUTER JOIN table2 t2 ON t1.num_pk = t2.num_fk;

-- 오른쪽(table2) 전부 + 왼쪽 교집합
SELECT * FROM table1 t1
RIGHT OUTER JOIN table2 t2 ON t1.num_pk = t2.num_fk;

-- OUTER는 생략 가능 (LEFT JOIN = LEFT OUTER JOIN)
SELECT * FROM table1 t1
RIGHT JOIN table2 t2 ON t1.num_pk = t2.num_fk;
```

`num_fk`가 `1,2,1,1,2`라 `num_pk=1`은 3번, `num_pk=2`는 2번 매칭됩니다. LEFT JOIN을 하면 매칭된 5행에 더해, 참조된 부모 행이 여러 자식과 짝지어지며 행이 늘어 8행이 나옵니다. `OUTER` 키워드는 생략해도 같은 동작이라 보통 `LEFT JOIN` / `RIGHT JOIN`으로 짧게 씁니다.

| 조인 | 남기는 기준 |
| --- | --- |
| INNER JOIN | 양쪽에 짝이 있는 행만 |
| LEFT (OUTER) JOIN | 왼쪽 전부 + 오른쪽 교집합 |
| RIGHT (OUTER) JOIN | 오른쪽 전부 + 왼쪽 교집합 |

### 1-6. 합집합(UNION) — 두 조회 결과를 세로로 합치기

JOIN이 테이블을 가로로 붙인다면, `UNION`은 두 SELECT 결과를 세로로 이어 붙입니다. MySQL에는 FULL OUTER JOIN이 없어서, LEFT JOIN과 RIGHT JOIN을 각각 구한 뒤 `UNION`으로 합쳐 흉내 냅니다(오라클의 FULL OUTER JOIN에 대응).

```sql
SELECT * FROM table1 t1 LEFT JOIN table2 t2 ON t1.num_pk = t2.num_fk
UNION
SELECT * FROM table1 t1 RIGHT JOIN table2 t2 ON t1.num_pk = t2.num_fk;
```

`UNION`은 중복 행을 제거하고 합칩니다. 중복까지 그대로 남기려면 `UNION ALL`을 씁니다. 위아래 두 SELECT는 **컬럼 개수와 타입이 맞아야** 합쳐집니다.

### 1-7. 차집합 — IS NULL로 "짝 없는 쪽"만 골라내기

OUTER JOIN 결과에서 짝이 없어 NULL이 된 행만 남기면, 한쪽에만 있고 다른 쪽에는 없는 값(차집합)을 뽑을 수 있습니다.

```sql
-- table1에는 있지만 어떤 자식도 참조하지 않는 num_pk
SELECT num_pk FROM table1 t1
LEFT JOIN table2 t2 ON t1.num_pk = t2.num_fk
WHERE num_fk IS NULL;
```

`LEFT JOIN` 후 `WHERE num_fk IS NULL` 조건을 걸면, 오른쪽에서 짝을 못 찾은 왼쪽 행만 남습니다. "참조되지 않는 부모 찾기", "주문 없는 회원 찾기" 같은 질의가 이 패턴입니다.

### 1-8. 실전 스키마로 조인 연습 (practice5.sql)

앞의 `table1/table2`는 관계만 보이려고 만든 뼈대라 값에 의미가 없었습니다. 같은 개념을 이름 있는 3개 테이블로 다시 세워 봅니다 — 카테고리 → 제품 → 재고가 한 방향으로 이어지는 구조입니다.

```sql
create table pcategory(
  카테고리번호_pk int unsigned auto_increment,
  카테고리명 varchar(10) not null,
  primary key(카테고리번호_pk)
);

create table product(
  제품번호_pk int unsigned auto_increment,
  제품명 varchar(100) not null,
  제품가격 int unsigned not null,
  카테고리번호_fk int unsigned,
  primary key(제품번호_pk),
  foreign key(카테고리번호_fk) references pcategory(카테고리번호_pk)
);

create table stock(
  재고번호_pk int unsigned auto_increment,
  재고수량 int,
  재고등록날짜 datetime default now(),
  제품번호_fk int unsigned,
  primary key(재고번호_pk),
  foreign key(제품번호_fk) references product(제품번호_pk)
);
```

여기서 컬럼 선언에 새로 붙은 옵션들을 정리하면 이렇습니다.

| 옵션 | 뜻 |
| --- | --- |
| `auto_increment` | PK 값을 넣지 않으면 1씩 자동 증가시켜 채움 (수동으로 번호 매길 필요 없음) |
| `unsigned` | 음수 없는 정수 — 번호·가격·수량처럼 0 이상만 나오는 값에 범위를 두 배로 |
| `not null` | 빈 값 금지 (이름·가격은 반드시 있어야 함) |
| `default now()` | 값을 안 넣으면 현재 시각을 자동 기록 (등록 시각용) |

관계는 `pcategory 1 : N product`, `product 1 : N stock` 두 단계입니다. 재고를 카테고리까지 거슬러 보려면 두 개의 FK를 타고 세 테이블을 이어야 합니다.

**3개 테이블 조인** — INNER JOIN을 한 번 더 이어 붙이면 됩니다. 조인 조건(`ON`)을 테이블이 늘어난 만큼 계속 추가하는 게 핵심입니다.

```sql
-- 제품명 + 카테고리명 + 재고수량 한 번에
select p.제품명, c.카테고리명, s.재고수량
from product p
join pcategory c on p.카테고리번호_fk = c.카테고리번호_pk
join stock s     on p.제품번호_pk    = s.제품번호_fk;
```

**짝 없는 쪽까지 살리기** — "제품이 하나도 없는 카테고리도 목록에 나오게" 하려면 부모(카테고리)를 전부 남기는 LEFT JOIN을 씁니다. 1-5·1-7에서 본 패턴을 이름 있는 테이블에 그대로 적용한 것입니다.

```sql
-- 제품 없는 카테고리도 표시 (제품 자리는 NULL)
select c.카테고리명, p.제품명
from pcategory c
left join product p on c.카테고리번호_pk = p.카테고리번호_fk;

-- 재고가 한 번도 등록되지 않은 제품 = 짝 없는 쪽만 (차집합)
select p.제품명
from product p
left join stock s on p.제품번호_pk = s.제품번호_fk
where s.재고번호_pk is null;
```

**조인 + 집계** — 조인으로 테이블을 이어 붙인 뒤 [[SQL day04 집계와 정렬]]의 `group by`·집계 함수를 얹으면 "카테고리별 합계", "제품별 총재고" 같은 질문에 답할 수 있습니다.

```sql
-- 카테고리별 총 재고 수량
select c.카테고리명, sum(s.재고수량) as 총재고
from pcategory c
join product p on c.카테고리번호_pk = p.카테고리번호_fk
join stock s   on p.제품번호_pk    = s.제품번호_fk
group by c.카테고리명;

-- 제품별 총재고를 많은 순으로
select p.제품명, sum(s.재고수량) as 총재고수량
from product p
join stock s on p.제품번호_pk = s.제품번호_fk
group by p.제품명
order by 총재고수량 desc;
```

정리하면 practice5의 9문제는 결국 세 갈래입니다: ① 이어진 테이블을 조인으로 붙이기(2·3테이블), ② 짝 없는 쪽을 LEFT JOIN·`IS NULL`로 다루기, ③ 조인 결과에 `group by` 집계를 얹기. 앞 절들에서 하나씩 배운 조각을 실제 스키마에서 조합하는 연습입니다.

## 2. 추가로 알면 좋은 활용법

### 2-1. INNER JOIN은 "양쪽에 다 있는 것만"

INNER JOIN 결과에는 **짝이 맞는 행만** 남습니다. 만약 `table1`에 아무 자식도 참조하지 않는 `num_pk`가 있으면 그 행은 결과에서 빠집니다. "부모는 있는데 자식이 없는 경우까지 보고 싶다"면 `LEFT JOIN`으로 넘어갑니다.

```sql
SELECT * FROM table1 t1
LEFT JOIN table2 t2 ON t1.num_pk = t2.num_fk;   -- 짝 없는 부모도 NULL로 표시
```

교집합이 INNER, 왼쪽 테이블 전부 유지가 LEFT라고 잡아두면 됩니다.

### 2-2. CASCADE의 무게 — 편하지만 조용하다

`on delete cascade`는 부모 한 줄을 지우면 자식이 소리 없이 함께 사라집니다. 실수로 상위 데이터를 지웠을 때 연쇄로 대량 삭제가 일어날 수 있어, 실무에서는 정말 "부모 없이는 존재 의미가 없는 자식"에만 CASCADE를 씁니다(예: 주문 ↔ 주문상세). 반대로 로그·이력처럼 남겨야 하는 자식은 `SET NULL`이나 기본 RESTRICT로 두는 편이 안전합니다.

### 2-3. 조인 조건을 빠뜨리면 카티션 곱

`FROM a, b`만 쓰고 WHERE 조인 조건을 깜빡하면 조용히 `행수 × 행수`가 나옵니다. 큰 테이블에서는 이게 수백만 행이 되어 성능 사고로 이어집니다. `INNER JOIN ... ON` 문법이 이 실수를 구조적으로 줄여줍니다.

## 3. 더 나아가 알면 좋은 것

### 3-1. FK와 인덱스

FK 컬럼에는 조인·참조 검사가 자주 걸리므로 인덱스가 중요합니다. MySQL(InnoDB)은 FK를 만들 때 자식 쪽에 인덱스를 자동으로 만들어 줍니다. 조인이 느리면 "조인 키에 인덱스가 있는가"가 첫 점검 지점입니다.

### 3-2. 실전 코드에서 이 관계가 쓰인 자리

이전 프로젝트 백엔드가 이 PK-FK 조인의 실전판입니다. 예약·리뷰·게시글은 모두 "회원 한 명 ↔ 여러 건"이라는 부모-자식 관계이고, 화면에 회원 이름과 함께 목록을 뿌리려면 오늘 배운 INNER JOIN이 그대로 필요합니다. 매핑 상세는 [[KDT_2026 학습 지도]] 프로젝트 매핑표에서 찾습니다.

### 3-3. 다음에 볼 키워드

- `SELF JOIN` (같은 테이블을 자기 자신과 조인), `UNION ALL`과 `UNION`의 차이
- 참조 동작 나머지: `SET NULL`, `NO ACTION`, `RESTRICT`
- 다대다 관계와 연결 테이블(junction table)
- 서브쿼리 기반 차집합(`NOT IN`, `NOT EXISTS`)과 `IS NULL` 방식의 성능 비교
- 조인 성능과 실행 계획(`EXPLAIN`)

## 실습 파일

- `2026B_BE/src/database/day05.sql`
- `2026B_BE/src/database/practice5.sql` (pcategory·product·stock 3테이블 조인 연습)

## 관련 노트

[[CS 이론 MOC]] · [[SQL day04 집계와 정렬]] · [[SQL day03 DML과 조인]] · [[SQL day02 테이블과 제약조건]]
