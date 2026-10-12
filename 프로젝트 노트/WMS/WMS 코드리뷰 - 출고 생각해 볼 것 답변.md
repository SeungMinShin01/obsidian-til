---
출처: Claude 분석
원본: 코드리뷰 세션 (claude.ai 프로젝트 「미니프로젝트」)
작성일: 2026-09-28
tags: [프로젝트, java]
---

> 상위: [[KDT_1차 정규프로젝트 MOC]]

# WMS 코드리뷰 - 출고 생각해 볼 것 답변

Jira 코드리뷰 5~10번(출고 — 김지환, `@Transactional` 두 종류)의 "생각해 볼 것" 답. 코드는 Jira 문서에 있다. 근거는 V1 스키마, 검수→출고 MVP 명세, 팀규칙 02(백엔드 컨벤션), ADR 초안, Spring 수업 노트다.

## 5. 출고 문서 목록

### Q1. 두 코드가 DB에 보내는 SQL은 어떻게 다른가?

- 팀장: `SELECT … FROM document` — 조건도 정렬도 없다. `WHERE`(출고만)와 `ORDER BY`(예정일 순)는 **자바**의 `filter`·`sorted`가 한다.
- 팀원: `SELECT … FROM document WHERE type = ? ORDER BY expected_at ASC` — 거르기와 정렬을 **MySQL**이 한다.
- 결과 목록은 같다. 다른 건 일을 어디서 하느냐다.

### Q2. 문서 1만 건 중 출고 100건이면 자바로 올라오는 행 수는?

- 팀장: **10,000행.** 전부 엔티티로 만들어 영속성 컨텍스트에 올린 뒤 9,900개를 버린다.
- 팀원: **100행.**

### Q3. 팀원 코드는 Before인가 After인가? 측정 계획은?

- 팀원 코드는 이미 **After**다. 회고에 적은 Before(`findAll` + 반복문)는 팀장 코드 쪽이다.
- 그래서 측정은 "고치기 전/후"가 아니라 **두 구현을 같은 데이터로 나란히 재는** 방식으로 바꾼다. 팀원 코드는 되돌리지 않고, Before는 테스트나 별도 메서드로 남겨 둔다.
- 한 단계 더 있다. 지금 `document`에는 `type`·`expected_at` 인덱스가 없어서, 팀원 코드도 DB 안에서는 전체 스캔 + filesort다. 따라서 3단계로 잡는 게 좋다.
  1. Before: `findAll` + 자바 필터·정렬
  2. After 1: 쿼리 메서드 (현재 팀원 코드)
  3. After 2: + `(type, expected_at)` 복합 인덱스 (V2 마이그레이션, `EXPLAIN` 전후 비교)
- 잴 것: 응답 시간, 자바로 올라온 행 수, 쿼리 수(`logging.level.org.hibernate.SQL=debug`).

### Q4. `findByTypeOrderByExpectedAtAsc`는 누가 구현하나?

- **Spring Data JPA**가 구현한다. 서버가 뜰 때 `JpaRepository`를 상속한 인터페이스를 찾아 구현 객체(프록시)를 만들어 빈으로 등록한다.
- 이때 메서드 이름을 조각으로 읽는다: `find`(조회) / `By`(조건 시작) / `Type`(= type 필드) / `OrderBy` / `ExpectedAt` / `Asc`. 이걸 JPQL로 바꿔 둔다.
- 필드 이름이 틀리면(예: `Typ`) 요청 때가 아니라 **서버가 뜰 때** 에러가 난다.

## 6. 할당 (순서)

### Q1. 순서가 바뀌었는데 결과가 다른가? 무엇이 보장하나?

- `@Transactional` 안이라면 **결과는 같다.** 둘 다 한 트랜잭션이라 전부 반영되거나 전부 취소된다(원자성).
- 실제로 DB에 나가는 SQL 순서도 두 코드가 거의 같다. `detail` 저장은 PK가 `AUTO_INCREMENT`(IDENTITY)라 `save`를 부른 순간 INSERT가 나간다. 반면 이미 조회된 `stock`의 변경은 `save`를 먼저 불러도 커밋 때 UPDATE로 나간다. 그래서 팀장 코드도 "INSERT detail → UPDATE stock" 순서가 된다.
- `@Transactional`이 **없으면** 달라진다. 저장마다 따로 커밋되어 중간에 실패하면 반쪽이 남는다.
  - 팀장 순서: 선점은 늘었는데 기록(detail)이 없다 → 누가 잡았는지 모르는 선점
  - 팀원 순서: 기록은 있는데 선점이 안 늘었다 → 가용 수량이 부풀어 초과 할당 가능

### Q2. 없는 stockId면 어디서 터지나? 그 차이가 DB에 영향을 주나?

- 팀장: `stockEntity.getAllocatedQty()` 줄에서 NPE. 아무것도 저장하기 전이다.
- 팀원: 먼저 `toEntity(documentItemEntity, null)`로 간다. `toEntity`가 stock에서 lot·location을 꺼낸다면 **그 안에서** NPE. 꺼내지 않는다면 detail을 만들어 INSERT한 뒤(`detail.lot_id`가 NOT NULL이라 여기서 DB가 막을 수도 있다) `setAllocatedQty` 줄에서 NPE.
- `@Transactional`이 있으면 NPE(RuntimeException)로 전부 롤백되므로 **DB에 남는 차이는 없다.**
- 없으면 팀원 쪽은 이미 INSERT된 detail이 남을 수 있다.
- 두 경우 모두 응답은 500이다. 명세상 맞는 응답은 404 `STOCK_NOT_FOUND`.

### Q3. 가용 수량보다 많이 할당하면 어디서 막히나?

- **자바에는 검사가 없다.** 막는 건 **DB**다. V1 `stock`의 `CHECK (allocated_qty >= 0 AND allocated_qty <= qty)`.
- 걸리는 시점은 UPDATE가 나가는 **커밋 때**다. 메서드 본문이 다 끝난 뒤 예외가 나고, 트랜잭션이 롤백되어 먼저 INSERT된 detail까지 취소된다. 응답은 409 `DATA_CONSTRAINT_VIOLATION`(명세 v1 에러 코드표의 "할당량 > 재고" 예시와 일치).
- 주의: CHECK는 **동시 요청을 막지 못한다.** 두 요청이 같은 `allocated_qty`를 읽고 각자 더해 쓰면 한쪽 증가가 사라진다(갱신 분실). 값이 한도를 넘지 않았으니 CHECK도 통과한다. 이건 락이나 조건부 UPDATE로 막아야 한다(동시성 측정 주제).
- v2에서는 자바에서 먼저 검사해 409 `INSUFFICIENT_STOCK`으로 돌려준다.

## 7. 피킹 리스트 정렬

### Q1. stream과 이중 for, 어느 쪽으로 통일하나? 기준은?

- 정렬은 **표준 API로 통일**한다(`sorted` 또는 `List.sort`). 기준은 ED-10에서 확인한 셋이다.
  - 안정 정렬: 같은 칸 코드 줄의 순서가 흔들리지 않는다.
  - O(n log n): 이중 for는 항상 O(n²)이다.
  - 의도가 보인다: "칸 코드 순"이라는 기준만 적으면 된다.
- 거르기·변환은 stream이든 `forEach` + `add`든 수업에서 둘 다 배웠다. 중요한 건 **한 프로젝트에서 한 가지로** 쓰는 것이다(Spring day07 노트의 기준).
- 더 나은 방향은 5번처럼 DB에 맡기는 것이다: `findByDocumentItemEntity_DocumentEntity_DocumentIdOrderByLocationEntity_LocationCode` 또는 `@Query`.

### Q2. `getLocationEntity()`가 null인 detail이 있을 수 있나?

- **있다.** V1 `document_item_detail.location_id`는 NULL 허용이고, 주석이 "입고 적재 전 NULL"이다.
- 입고 문서 ID를 넣으면 검수만 되고 적재 안 된 줄이 걸린다. 정렬 중 `getLocationCode()`에서 NPE → 500.
- 두 코드 모두 문서가 **출고인지 확인하지 않는다.** 입고 문서로 피킹 리스트를 뽑는 것 자체가 말이 안 되니, type 검사가 먼저다(v2 `DOCUMENT_TYPE_MISMATCH`).
- 출고 detail도 안심할 수 없다. 할당 `toEntity`가 stock의 location을 detail에 채우는지 확인해야 한다. 안 채운다면 출고 문서에서도 NPE가 난다.

### Q3. `A-01-03`과 `A-01-10`을 문자열로 비교하면 순서가 맞나? `A-1-3`이면?

- 문자열 비교는 앞에서부터 **한 글자씩** 비교한다.
- `A-01-03` vs `A-01-10`: 6번째 글자 `0` < `1` → `A-01-03`이 앞. **맞다.** 자릿수를 0으로 채워 길이가 같기 때문이다.
- `A-1-3` vs `A-1-10`: 5번째 글자 `3` > `1` → `A-1-10`이 앞. **틀리다.** `A-2-1`과 `A-10-1`도 `A-10-1`이 앞에 온다.
- 그래서 칸 코드는 **고정 자릿수(0 채우기)** 가 규칙이어야 한다. 위치를 등록할 때 형식을 검증하면 정렬 문제가 원천 차단된다.

## 8. 출고확정

### Q1. 수업에서 배운 방식은? `Boolean`이 null을 돌려줄 수 있다는 게 응답 규칙과 맞나?

- **둘 다 수업에서 나왔다.** `isPresent()` + `get()`은 수정 갈래에서(Spring day04·05), `orElse(null)`은 조회 갈래에서(day07 이후) 썼다. 수업 노트에는 `orElse(null)`이 "Optional이 옮겨 둔 '없음'을 다시 null로 되돌리는 표기"라는 지적도 있다.
- 팀 컨벤션(02)은 둘 다 아니다. `orElseThrow(() -> new BusinessException(ErrorCode...))`로 던지고 `ApiResponse`로 감싸 돌려주는 게 규칙이다.
- `Boolean`은 true / false / **null** 세 상태를 가진다. 지금 코드는 null을 돌려주지 않지만, 누가 null을 돌려주면 컨트롤러는 200에 빈 본문을 내보낸다. 화면은 성공인지 실패인지 모른다. 응답 규칙(`{success, data, message, code}`)과 맞지 않는다.
- 수업에서 래퍼 타입(`Integer`)을 쓴 이유는 "안 보낸 값과 0을 가르기" 위해서였다. 응답의 성공 여부에는 그 이유가 없으니 `boolean`이 낫고, 더 나은 건 예외 + `ApiResponse`다.

### Q2. 같은 detailId로 두 번 부르면?

- 두 번째 호출도 그대로 `qty -= n`, `allocated_qty -= n`을 한다. 자바에는 막는 코드가 없다(문서 상태 확인 없음).
- 이 stock에 다른 할당이 없다면(`allocated_qty`가 정확히 n): `allocated_qty = -n` → **DB CHECK `allocated_qty >= 0`** 에 걸려 커밋 때 롤백, 409 `DATA_CONSTRAINT_VIOLATION`.
- 다른 출고 문서도 이 stock을 잡고 있다면(`allocated_qty` > n): **두 번째 호출이 성공한다.** 실물은 두 번 빠지고, 남의 선점까지 깎인다. 에러 없이 데이터가 틀어진다.
- 제대로 막는 자리는 문서 상태다. `PICKING`일 때만 출고확정, 끝나면 `SHIPPED` → 두 번째는 409 `INVALID_DOCUMENT_STATUS`(v2).
- (회의안건 5번과 대조 필요)

### Q3. 입고 문서의 detail ID를 넣으면?

- 적재 전: `stock_id`가 NULL이라 `getStockEntity()`가 **null** → `setQty` 줄에서 NPE → 500.
- 적재 후: 입고로 만든 stock이 나온다. 그 재고에서 `qty`와 `allocated_qty`를 빼는데, 선점이 없으면 `allocated_qty` 음수 → CHECK로 롤백. 다른 출고가 그 재고를 잡고 있으면 **성공해 버린다** — 입고분이 출고 처리된다.
- 결국 type 검사(출고 문서인지)가 없어서 생기는 문제다.

## 9. 컨트롤러 구조

### Q1. 주소는 같은데 무엇이 다른가?

- 코드를 **나누는 기준**이 다르다.
  - 팀장: 주소 앞머리(자원)마다 컨트롤러 하나 + 클래스 `@RequestMapping`. 앞머리를 한 곳에만 적는다.
  - 팀원: 출고 관련 전부를 컨트롤러 하나에, 메서드마다 전체 주소.
- 차이가 드러나는 순간:
  - 주소 규칙이 바뀔 때. ADR 초안의 경로 결정(`/wms/api/v1/...`)이 확정되면 팀장 방식은 클래스당 한 줄, 팀원 방식은 메서드마다 고쳐야 한다.
  - 코드를 찾을 때. 주소 `/wms/allocations`를 보고 팀장 방식은 `AllocationController`로 바로 간다.
- 메서드 이름도 다르다. 팀 컨벤션(02)은 `get` / `getList` / `create`라서 팀원 쪽(`getOutboundList`, `getOutboundDetail`)이 규칙에 가깝다.

### Q2. 입고 쪽은? 두 방식이 섞이면?

- 조현우 코드의 컨트롤러는 이 세션에서 보지 못했다(직접 확인 필요).
- 섞이면 생기는 일:
  - 새 기능을 어디에 둘지, 주소 앞머리를 어디서 바꿀지 매번 파일마다 다르다.
  - 경로 규칙을 바꿀 때 누락이 생긴다.
  - 리뷰에서 같은 논쟁이 반복된다.
- 팀의 `코드 구조 예시` 문서는 클래스 `@RequestMapping` 방식이다(`PurchaseOrderController`). 그쪽으로 맞추는 게 자연스럽다.

### Q3. ED-11 공통 규칙에 적혀 있나? 없다면 적어야 하나?

- ED-11 문서는 이 세션에서 찾지 못했다(직접 확인 필요). 팀규칙 02 컨벤션에는 메서드 이름 규칙만 있고 컨트롤러 나누는 기준은 없다.
- **적어야 한다.** 두 사람이 이미 다르게 썼다는 게 규칙이 필요하다는 증거다. 한 줄이면 된다: "컨트롤러는 자원(주소 앞머리)당 하나, 앞머리는 클래스 `@RequestMapping`에."

## 10. `@Transactional` 두 종류

### Q1. 뭐가 다른가?

| | `jakarta.transaction.Transactional` | `org.springframework.transaction.annotation.Transactional` |
|---|---|---|
| 출신 | Jakarta EE 표준 (JTA) | 스프링 |
| `readOnly` | **없음** | 있음 |
| 롤백 조건 지정 | `rollbackOn` / `dontRollbackOn` | `rollbackFor` / `noRollbackFor` |
| 그 외 | 전파만 (`value = TxType.…`) | `propagation`, `isolation`, `timeout` |

- 스프링은 둘 다 인식해서 트랜잭션을 걸어 준다. 기본 동작(RuntimeException이면 롤백)도 같다. 그래서 지금은 둘 다 **돌아간다.**
- 차이는 옵션을 쓰려는 순간 나온다. `jakarta` 쪽에 `readOnly = true`를 쓰면 **컴파일 에러**다.
- Spring 수업 노트(day04·05)에도 "jakarta와 스프링의 같은 이름 표시가 속성에서 갈린다"고 정리돼 있다.

### Q2. "조회는 readOnly"를 규칙으로 하려면?

- **스프링 쪽**(`org.springframework.transaction.annotation.Transactional`)이어야 한다.
- 팀규칙 02에 이미 "Service 클래스에 `readOnly = true`, 쓰기 메서드에만 `@Transactional`"이 적혀 있다. 이 규칙은 스프링 쪽 import에서만 가능하다.
- 조현우·팀장 코드의 `jakarta` import를 스프링 쪽으로 바꾸고, 규칙 문서에 import 경로까지 한 줄 적어 두면 자동 완성 실수를 막을 수 있다.
- `readOnly`의 효과: 변경 감지용 스냅샷을 만들지 않고 flush를 하지 않는다. 조회 성능이 조금 나아지고, 조회 메서드에서 실수로 setter를 불러도 DB에 반영되지 않는다.

## 관련 노트

[[KDT_1차 정규프로젝트 MOC]]
