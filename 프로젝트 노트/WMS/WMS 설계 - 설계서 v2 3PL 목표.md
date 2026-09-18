---
출처: Claude 분석
원본: claude.ai 프로젝트 「미니프로젝트」 WMS/설계서_v2.md
작성일: 2026-09-18
tags: [프로젝트]
---

> 상위: [[KDT1차 정규프로젝트 MOC]]

# WMS v2 설계서 — 식품·건기식 3PL 풀필먼트 (다중 화주)

> ℹ️ **현재 단계는 단일 WMS다** (`WMS/주말_MVP_명세_v2.md`). 이 문서는 화주·Portal을 붙인 뒤의 목표 설계다. 테이블·용어 이름은 단일 WMS 쪽(`팀규칙/04_용어사전.md`)을 따르고, 화주 도입 시 이 문서를 그 이름으로 맞춘다.


> 작성: 2026-09-18 · 4주 팀 프로젝트 / React + Spring Boot + MySQL
> 이 문서는 `WMS/요구사항명세서.md`(v1, 단일 화주 이커머스)를 **대체**한다. 두 문서가 충돌하면 이 문서가 우선한다.
> 표기: **[결정]** 확정된 사항 · **[가정]** 기본값으로 정해 둔 것. 팀 합의 시 바꿀 수 있다.

---

## 0. v1에서 바뀐 것

| 항목 | v1 | v2 |
|---|---|---|
| 도메인 | 이커머스 단일 창고 | 3PL, 화주 3개 고정 (A 건강기능식품 / B 음료 / C 상온 가공식품) |
| 화주 관리 | 없음 (멀티테넌시 범위 제외) | `tenant_id` 방식. 화주 추가·수정·삭제 **없음** (Flyway 시드로 고정) |
| 소비기한 | 범위 제외 | 재고를 **SKU + 소비기한**으로 구분. 로트 번호 없음 |
| 할당 정책 | FIFO / 근접 | **FEFO + 출고허용 잔여일** |
| 거래처(partners) | 공급처·판매처 CRUD | **삭제**. 화주가 그 역할을 한다 |
| 계정 | 누구나 회원가입 | **공개 회원가입 없음.** 관리자(OPERATOR)가 작업자(WORKER) 계정만 생성. 관리자·화주 계정은 시드 |
| 묶음 출고(웨이브)·동선 계산·랙 배치도 | 필수/권장 | **삭제**. 출고요청 1건 = 출고지시 1건 |
| 서버 | 단일 | **Portal 서버와 WMS Core 서버 물리 분리** + RabbitMQ |
| 멀티테넌시 방식 | — | **Core는 Shared Schema(`tenant_id`), Portal은 화주별 DB 분리** (D-11) |
| 화면 | 배치도·미니맵 | 표 형식만. API를 먼저 만들고 AI로 화면 생성 |
| 3~4주차 초점 | 성능 Before/After | 정합성·예외·장애처리 검증 (성능 측정은 여유 시) |

> ⚠ **`WMS/Sprint1_CRUD_MVP명세.md`(9/19~20 주말)는 v2와 맞지 않는다.** 회원가입과 거래처 CRUD는 v2에 없다. 이번 주말 작업은 `WMS/주말_MVP_명세.md`를 따른다.

---

## 1. 시스템 구성

```
                React (하나의 프로젝트: /portal, /wms, /picking)
                          │
                    nginx (리버스 프록시)
          /api/portal/** │                 │ /api/wms/**
                         ▼                 ▼
   ┌────────────────────────┐        ┌────────────────────────┐
   │ Portal 서버 (화주용)    │─명령──▶│ WMS Core 서버 (운영용) │
   │ portal_hlt/bev/fod     │ Rabbit │ core_db (공유 스키마)  │
   │                        │◀─결과──│ 재고 트랜잭션 전부     │
   │                        │  MQ    │                        │
   │                        │─조회──▶│ /internal/v1 (REST)    │
   └────────────────────────┘        └────────────────────────┘
```

**[결정] 통신 규칙**

| 종류 | 방향 | 수단 | 예 |
|---|---|---|---|
| 명령 | Portal → Core | RabbitMQ | 입고예정 등록, 출고요청 등록, 출고요청 취소 |
| 결과 | Core → Portal | RabbitMQ | 접수·거부, 할당, 출고완료, 부분출고 등 상태 변경 |
| 조회 | Portal → Core | REST (내부 API, 서비스 키) | 화주 재고 현황, 출고 상세 |
| 재고 트랜잭션 | Core 내부 | DB 트랜잭션 | 선점, 결품, 출고확정, 취소 원복. **MQ로 처리하지 않는다** |

- **DB 분리**: Core는 `core_db` 하나를 모든 화주가 공유한다(`tenant_id`). Portal은 **화주마다 DB를 따로 둔다**(`portal_hlt`, `portal_bev`, `portal_fod`). 로컬에서는 MySQL 인스턴스 하나에 DB 4개를 두고 서로 조인하지 않는다.
- **[결정] 멀티테넌시 방식을 서버마다 다르게 고른 이유 (D-11)**: Core에는 화주들이 함께 쓰는 자원(로케이션)과 화주를 넘나드는 규칙(혼적 금지), 운영자의 전체 화주 조회가 있어 DB를 나눌 수 없다. Portal에는 셋 다 없으므로 DB를 나눠 화주 데이터를 물리적으로 격리한다.
- **리포 구조**: 모노레포 + Gradle 멀티모듈 `core/`, `portal/`, `contracts/`(메시지 DTO 공유), `frontend/`.
- **[결정] Core는 Portal 없이도 전체 흐름이 돌아간다.** 운영자가 WMS 화면에서 입고예정과 출고요청을 대신 등록할 수 있다. REST 컨트롤러와 MQ 리스너가 **같은 애플리케이션 서비스**를 호출하므로, Portal은 나중에 붙여도 Core 쪽 비용이 작다. Core를 먼저 개발할 수 있는 근거가 이것이다.
- **분리의 시연 가치**: Core를 멈춰도 Portal은 요청을 계속 받고 메시지가 큐에 쌓인다. Core를 다시 켜면 쌓인 요청이 처리된다(§12 시연 7).

---

## 2. 기준정보 (Flyway 시드, CRUD 화면 없음)

### 2.1 화주

| id | 코드 | 화주 | 품목군 | 출고허용 잔여일 | 입고허용 잔여일 |
|---|---|---|---|---|---|
| 1 | `HLT` | A 화주 | 건강기능식품 (비타민, 유산균) | 180 | 365 |
| 2 | `BEV` | B 화주 | 음료 (생수, 탄산, 캔커피) | 60 | 120 |
| 3 | `FOD` | C 화주 | 상온 가공식품 (라면, 통조림, 즉석밥) | 90 | 180 |

- 모두 상온 보관이다. 냉동·냉장은 다루지 않는다.
- **[가정]** 잔여일 값은 시연용이다. SKU에 개별 값이 있으면 SKU 값을 우선한다.
- **출고허용 잔여일**: 소비기한까지 남은 날이 이 값보다 적은 재고는 할당하지 않는다.
- **입고허용 잔여일**: 남은 날이 이 값보다 적게 들어온 상품은 정상 입고하지 않는다(불량으로 처리).

### 2.2 SKU

**코드 규칙 [결정]**: `{화주코드}-{4자리 일련번호}` 예: `BEV-0001`. 코드만 봐도 어느 화주 상품인지 알 수 있다.

| 컬럼 | 설명 |
|---|---|
| `sku_code` | 위 규칙. 전역 UNIQUE |
| `sku_name`, `spec` | 상품명, 규격 |
| `base_unit` | 재고 기본단위 `EA` 또는 `BOX` |
| `units_per_box` | 박스당 입수(표시용, 환산하지 않음) |
| `min_ship_remaining_days` | 출고허용 잔여일 (null이면 화주 기본값) |
| `min_inbound_remaining_days` | 입고허용 잔여일 (null이면 화주 기본값) |

**[결정] 수량은 SKU별 기본단위 하나로만 관리한다.** 단위 환산(BOX↔EA)은 하지 않는다. 음료·가공식품은 BOX, 건기식은 EA로 둔다.

**시드 SKU (15개)**

| 화주 | 코드 | 상품명 | 규격 | 단위 |
|---|---|---|---|---|
| A | HLT-0001 | 종합비타민 | 90정 | EA |
| A | HLT-0002 | 오메가3 | 60캡슐 | EA |
| A | HLT-0003 | 프로바이오틱스 | 30포 | EA |
| A | HLT-0004 | 홍삼스틱 | 10ml×30포 | EA |
| A | HLT-0005 | 루테인 | 30캡슐 | EA |
| B | BEV-0001 | 생수 | 500ml×20 | BOX |
| B | BEV-0002 | 레몬 탄산수 | 350ml×24 | BOX |
| B | BEV-0003 | 이온음료 | 500ml×20 | BOX |
| B | BEV-0004 | 캔커피 | 240ml×30 | BOX |
| B | BEV-0005 | 보리차 | 500ml×20 | BOX |
| C | FOD-0001 | 컵라면 매운맛 | 12입 | BOX |
| C | FOD-0002 | 참치캔 | 150g×12 | BOX |
| C | FOD-0003 | 즉석밥 | 210g×24 | BOX |
| C | FOD-0004 | 감자칩 | 60g×20 | BOX |
| C | FOD-0005 | 3분 카레 | 200g×24 | BOX |

### 2.3 로케이션 (랙 번호)

창고는 1개(`WH1`)다.

**코드 규칙 [결정]**: `{구역}-{통로2}-{베이2}-{단1}`

```
S1-01-03-2
│  │  │  └ 단(층) 1~3 (1=바닥)
│  │  └──── 베이 01~10 (통로 안의 칸)
│  └─────── 통로 01~04
└────────── 구역 S1~S3 (Storage)
```

- 구역 이름을 A/B/C 대신 `S1~S3`으로 한 이유: A/B/C 화주와 헷갈리지 않게 하려고.
- 자리수를 0으로 채웠으므로 **코드 문자열 정렬 = 피킹 순서**가 된다(구역 → 통로 → 베이 → 단). S자 순회는 하지 않는다.

| 유형 | 코드 | 개수 | 용도 | 할당 대상 |
|---|---|---|---|---|
| `STORAGE` | `S1-01-01-1` ~ `S3-04-10-3` | 3구역 × 4통로 × 10베이 × 3단 = 360 | 보관 | O |
| `RECEIVING` | `RCV-01`, `RCV-02` | 2 | 입고확정 후 적치 전 대기 | X |

- 시드는 Flyway에서 MySQL 재귀 CTE로 한 번에 만든다.
- **[결정] 혼적 규칙 (STORAGE만 적용)**
  - 한 로케이션에는 **한 화주**의 재고만 둔다. 3PL에서 화주끼리 섞이면 오출고가 난다.
  - 한 로케이션에는 **한 SKU, 한 소비기한**만 둔다. 작업자가 같은 선반에서 소비기한을 구분해 집을 수 없기 때문이다.
  - 같은 SKU·같은 소비기한이면 이미 있는 로케이션에 더 적치할 수 있다(수량 합산).
- 로케이션 최대 적재량(용적)은 관리하지 않는다.

---

## 3. 재고 모델

### 3.1 재고 한 행의 의미

`stock` 한 행 = **(화주, SKU, 로케이션, 소비기한)** 조합의 수량.

| 컬럼 | 의미 |
|---|---|
| `on_hand_qty` | 실물재고 |
| `allocated_qty` | 선점재고 |
| `available_qty` | 가용재고. `on_hand_qty - allocated_qty`를 **생성 컬럼(STORED)**으로 둔다. 직접 쓰지 않는다 |

```sql
available_qty INT AS (on_hand_qty - allocated_qty) STORED,
CONSTRAINT chk_stock_qty CHECK (allocated_qty >= 0 AND allocated_qty <= on_hand_qty),
UNIQUE KEY uk_stock (tenant_id, sku_id, location_id, expiry_date)
```

- **CHECK 제약은 DB 차원의 최후 방어선**이다. 애플리케이션 버그가 있어도 가용재고가 음수가 될 수 없다(MySQL 8.0.16 이상에서 동작).
- 수량이 0이 된 행도 지우지 않는다. 이력이 이 행을 참조한다.

### 3.2 재고 이력 (`stock_history`)

모든 재고 변동은 **재고 수량 변경과 같은 트랜잭션에서** 이력 한 행을 남긴다.

| 유형 | 발생 시점 | 실물 | 선점 | 로케이션 |
|---|---|---|---|---|
| `INBOUND` | 입고확정 | + | | RCV |
| `PUTAWAY_OUT` / `PUTAWAY_IN` | 적치 (한 쌍) | − / + | | RCV → STORAGE |
| `ALLOCATE` | 출고할당 | | + | STORAGE |
| `DEALLOCATE` | 출고요청 취소 | | − | STORAGE |
| `SHORTAGE` | 피킹 결품 | − | − | STORAGE |
| `OUTBOUND` | 출고확정 | − | − | STORAGE |
| `ADJUST` | 재고조정 | ± | | 모두 |

이력 컬럼: `stock_id, tenant_id, sku_id, location_id, expiry_date, tx_type, on_hand_delta, allocated_delta, on_hand_after, allocated_after, ref_type, ref_id, reason, created_by, created_at`

**불변식 (테스트로 검증)**: 모든 재고 행에서 `Σ on_hand_delta = on_hand_qty`, `Σ allocated_delta = allocated_qty`가 성립해야 한다.

### 3.3 재고 수량 변화 예시

음료 B화주, 생수(BEV-0001) 30박스 출고요청, 이 중 2박스 결품:

| 시점 | 실물 | 선점 | 가용 | 이력 |
|---|---|---|---|---|
| 입고확정 (RCV) | 100 (RCV) | 0 | 0 (할당 대상 아님) | INBOUND +100 |
| 적치 (S1-01-03-2) | 100 | 0 | 100 | PUTAWAY_OUT −100, PUTAWAY_IN +100 |
| 출고할당 | 100 | 30 | 70 | ALLOCATE +30 |
| 피킹 28, 결품 2 | 98 | 28 | 70 | SHORTAGE −2/−2 |
| 출고확정 | 70 | 0 | 70 | OUTBOUND −28/−28 |

---

## 4. 정책

### 4.1 입고

| ID | 정책 |
|---|---|
| P-IN-1 | 입고예정은 화주(Portal) 또는 운영자(WMS)가 등록한다. `(tenant_id, external_ref_no)` UNIQUE로 같은 요청이 두 번 등록되지 않게 막는다 |
| P-IN-2 | 검수 결과는 예정 라인 하나에 **여러 행**을 둘 수 있다. 행 = (소비기한, 정상수량, 불량수량, 불량사유). 한 라인에 소비기한이 여러 개 섞여 도착할 수 있기 때문이다 |
| P-IN-3 | 라인별 `Σ(정상 + 불량) ≤ 예정수량`. **초과입고는 받지 않는다**. 합계가 예정보다 적으면 차이사유가 필수다 (`NOT_ARRIVED` 미도착 / `WRONG_ITEM` 오배송 / `ETC`) |
| P-IN-4 | 불량사유: `DAMAGED` 파손 / `EXPIRY_SHORT` 소비기한 부족. 불량수량은 재고를 만들지 않는다(반송 대상, 검수 기록만 남음) |
| P-IN-5 | 소비기한이 오늘 이전이면 오류다. 남은 날이 입고허용 잔여일보다 적으면 정상수량으로 받을 수 없고 `EXPIRY_SHORT` 불량으로 입력해야 한다 |
| P-IN-6 | 검수는 **임시저장**(몇 번이든 수정 가능) → **입고확정**. 확정하면 수량이 고정되고 정상수량만큼 RCV 로케이션에 재고가 생긴다(`INBOUND`). 확정 후에는 검수를 수정할 수 없다 |
| P-IN-7 | 적치: 검수 행 하나를 STORAGE 로케이션 **하나 이상에 나눠** 적치할 수 있다. 적치수량 합은 적치대기수량을 넘을 수 없다. 혼적 규칙(§2.3)을 검증한다. **적치된 수량부터 가용재고가 된다** |
| P-IN-8 | 모든 수량을 적치하면 입고가 `COMPLETED`가 된다 |
| P-IN-9 | 취소는 `REGISTERED`에서만 할 수 있다. 확정 이후의 오류는 재고조정(`ADJUST`)으로 처리한다 |

**Excel 검수 업로드 (P-IN-10)**

1. 입고예정 한 건에 대해 파일을 올린다.
2. 서버가 검증하고 **정상 N행 / 오류 M행** 미리보기를 돌려준다. 이 단계에서는 저장하지 않는다.
3. 사용자가 "정상행 저장"을 누르면 검수 **임시저장**에 반영된다. 재고는 아직 생기지 않는다.
4. 입고확정은 따로 누른다.

| 검증 | 오류 메시지 예 |
|---|---|
| 존재하지 않는 SKU | `없는 SKU입니다: BEV-9999` |
| 다른 화주의 SKU, 또는 이 입고예정에 없는 SKU | `이 입고예정에 없는 SKU입니다` |
| 수량이 음수이거나 정수가 아님 | `수량은 0 이상의 정수여야 합니다` |
| 라인별 (정상 + 불량) 합이 예정수량 초과 | `예정수량(100)을 초과합니다(합계 105)` |
| 이미 확정된 입고건 | `이미 확정된 입고입니다` (파일 전체 거부) |
| 소비기한 형식 오류, 과거 날짜, 입고허용 잔여일 미달인데 정상수량 입력 | `소비기한 잔여일 부족(45일 < 120일)` |
| 불량수량이 있는데 사유가 없음 | `불량사유를 입력하세요` |

### 4.2 출고할당 (FEFO)

| ID | 정책 |
|---|---|
| P-AL-1 | **할당 대상 재고**: 같은 `tenant_id` AND 같은 `sku_id` AND 로케이션 유형 `STORAGE` AND `available_qty > 0` AND `expiry_date ≥ 오늘 + 출고허용 잔여일` |
| P-AL-2 | **정렬 [결정]**: `expiry_date ASC, location_code ASC`. 소비기한이 같으면 로케이션 순. 정렬 순서가 항상 같아야 락을 거는 순서도 같아진다 |
| P-AL-3 | **분할할당**: 정렬된 순서대로 `min(가용재고, 남은 수량)`씩 채운다. 할당 1행 = (출고 라인, 재고 행, 수량) |
| P-AL-4 | **부족 시 [결정] 전부 아니면 전무(all-or-nothing)**: 한 라인이라도 가용이 부족하면 트랜잭션 전체를 롤백한다. 상태는 `ALLOCATION_FAILED`, 부족한 SKU와 수량을 기록하고 선점은 0으로 남는다. 나중에 다시 할당할 수 있다. 부분출고 경로를 피킹 결품 한 곳으로 모아 복잡도를 줄이기 위한 선택이다 |
| P-AL-5 | 할당은 운영자가 "할당 실행"으로 시작한다(단건 또는 여러 건 선택). 수신하자마자 자동으로 할당하는 방식은 선택 확장으로 둔다 |
| P-AL-6 | **동시성 [결정 후보, 둘 다 구현해 비교]** |

**P-AL-6 동시성 제어 두 가지**

① 비관적 락
```sql
SELECT * FROM stock
 WHERE tenant_id = ? AND sku_id = ? AND location_type = 'STORAGE'
   AND available_qty > 0 AND expiry_date >= ?
 ORDER BY expiry_date, location_code
 FOR UPDATE;
```
- 출고요청에 SKU가 여러 개면 **`sku_id` 오름차순으로** 처리해 트랜잭션끼리 락 순서가 엇갈리지 않게 한다(데드락 방지).

② 조건부 UPDATE (락 없이 원자적 갱신)
```sql
UPDATE stock SET allocated_qty = allocated_qty + :qty
 WHERE id = :id AND on_hand_qty - allocated_qty >= :qty;
-- 영향받은 행이 0이면 다른 요청이 먼저 가져간 것 → 다음 후보로 넘어가거나 다시 조회
```

①을 먼저 구현하고 ②를 추가한다. 동시 요청 100건으로 두 방식을 비교해(초과 선점 건수, p95, 데드락·재시도 횟수) 결정로그에 남긴다.

### 4.3 피킹 · 결품 · 부분출고

| ID | 정책 |
|---|---|
| P-PK-1 | `ALLOCATED` 상태에서 "피킹 시작"을 누르면 `PICKING`이 된다. 피킹리스트 = 할당 행을 `location_code` 순으로 정렬한 것 |
| P-PK-2 | 할당 행마다 실제 피킹수량을 입력한다(0 ≤ 피킹수량 ≤ 할당수량). 할당수량보다 적으면 결품사유가 필수다 (`NOT_FOUND` 없음 / `DAMAGED_IN_LOCATION` 로케이션 내 파손 / `ETC`) |
| P-PK-3 | **[결정] 결품은 입력하는 즉시 같은 트랜잭션에서 처리한다**: `결품 = 할당 − 피킹`만큼 실물과 선점을 **함께** 줄인다(`SHORTAGE`). 선점만 풀면 없는 재고가 다시 가용재고로 잡혀 다음 주문도 결품이 난다. 실물과 선점을 같은 양만큼 줄이므로 같은 행을 다른 주문이 선점하고 있어도 CHECK 제약이 깨지지 않는다 |
| P-PK-4 | **[결정] 결품분을 다른 로케이션에서 자동으로 다시 할당하지 않는다.** 미출고로 종결한다(자동 재할당은 선택 확장) |
| P-PK-5 | 모든 할당 행의 입력이 끝나면 `PICKED`가 된다. 결품이 즉시 반영되므로 입력한 행은 되돌리지 않는다 |

### 4.4 출고확정

| ID | 정책 |
|---|---|
| P-SH-1 | `PICKED`에서만 확정할 수 있다. 할당 행마다 피킹수량만큼 실물과 선점을 줄인다(`OUTBOUND`). **실물재고가 최종적으로 줄어드는 곳은 여기뿐이다** (결품 조정 제외) |
| P-SH-2 | 결과: 전량 출고면 `SHIPPED`, 일부만 출고면 `PARTIALLY_SHIPPED`, 출고수량이 0이면 `UNSHIPPED`. 셋 다 종료 상태다. 라인별로 요청 / 출고 / 미출고 수량과 사유를 기록한다 |
| P-SH-3 | 미출고분은 백오더로 남기지 않는다. 화주가 새 출고요청을 낸다 |
| P-SH-4 | 확정 처리, 재고이력, 출고이력, 결과 이벤트(outbox)는 **한 트랜잭션**이다 |

### 4.5 취소

| ID | 정책 |
|---|---|
| P-CN-1 | 출고요청은 `RECEIVED`, `ALLOCATION_FAILED`, `ALLOCATED`에서만 취소할 수 있다. `ALLOCATED`에서 취소하면 모든 할당 행을 원복한다(`DEALLOCATE`) |
| P-CN-2 | `PICKING` 이후 취소 → 409 `OUTBOUND_003` (실물이 이미 움직이고 있기 때문) |
| P-CN-3 | 이미 취소된 건을 또 취소 → 409. 단, **같은 messageId가 다시 들어온 경우**는 오류가 아니라 무시한다(멱등 처리, §4.7) |
| P-CN-4 | 입고예정은 `REGISTERED`에서만 취소할 수 있다 |

### 4.6 멀티테넌시 격리

| ID | 정책 |
|---|---|
| P-TN-1 | Core에서 화주가 소유하는 테이블은 전부 `tenant_id NOT NULL`이다 |
| P-TN-2 | **tenant_id를 어디서 가져오나**: Portal에서 온 메시지는 봉투(envelope)의 `tenantId`를 쓴다. 이 값은 Portal이 **로그인한 사용자 정보에서** 채운 것이며, 요청 본문에 든 값은 믿지 않는다. WMS 운영자는 화면에서 화주를 골라 파라미터로 보낸다 |
| P-TN-3 | **교차 검증**: 입고·출고 라인의 SKU는 반드시 요청한 화주의 것이어야 한다. 아니면 거부한다(`TENANT_001`) |
| P-TN-4 | 할당 쿼리에는 `tenant_id` 조건이 **반드시** 들어간다. P-TN-3과 함께 이중으로 막는다 |
| P-TN-5 | Portal의 모든 조회와 명령은 로그인한 사용자의 화주로 고정된다. 다른 화주의 리소스 id로 접근하면 **404**를 준다(403은 그 리소스가 있다는 사실을 알려주므로) |
| P-TN-6 | **[결정 후보]** Core는 리포지토리 메서드에 `tenantId`를 파라미터로 명시적으로 받는다. Hibernate Filter는 활성화를 깜빡하면 조용히 전체 화주가 조회되고 디버깅이 어려워 기각했다 |
| P-TN-7 | **Portal 로그인**: `화주코드 + 아이디 + 비밀번호`로 로그인한다. 화주코드로 DB를 고르고 그 DB의 `portal_user`를 조회한다. 공통 DB는 두지 않는다. JWT에 `tenantCode`를 넣는다 |
| P-TN-8 | **Portal 라우팅**: `AbstractRoutingDataSource`가 `TenantContext`(ThreadLocal)의 화주코드로 DB를 고른다. JWT 필터에서 `set`, **`finally`에서 반드시 `clear`**. 트랜잭션이 시작되기 전에 화주가 정해져 있어야 한다 |
| P-TN-9 | **요청 밖에서 도는 코드**: Outbox 발행 스케줄러는 화주 3개를 차례로 돌며 화주를 세팅하고 발행한다. Core 결과 이벤트 리스너는 봉투의 `tenantId`로 화주를 세팅한 뒤 처리한다. `processed_message`는 화주 DB마다 있다 |
| P-TN-10 | **DB·테이블 생성**: DB 3개는 docker 초기화 스크립트로 **미리** 만든다(로그인 시점에 만들지 않음). Flyway 스크립트는 한 폴더(`db/portal`)만 두고, 앱 시작 시 3개 DB에 차례로 실행한다 |
| P-TN-11 | **비상구**: Portal 테이블에도 `tenant_id` 컬럼을 남긴다. 일정이 밀리면 라우팅 설정을 "3개 키 → 같은 DB"로 바꿔 Shared Schema로 되돌린다 |

### 4.7 메시지 (RabbitMQ)

**익스체인지와 큐**

| 익스체인지 (topic) | 라우팅 키 | 큐 | DLQ |
|---|---|---|---|
| `portal.commands` | `inbound.plan.requested`, `outbound.order.requested`, `outbound.order.cancel-requested` | `core.commands` | `core.commands.dlq` |
| `wms.events` | `inbound.status-changed`, `outbound.status-changed` | `portal.events` | `portal.events.dlq` |

**봉투(envelope)**
```json
{
  "messageId": "7f3c…(UUID)",
  "type": "outbound.order.requested",
  "tenantId": 2,
  "occurredAt": "2026-09-30T10:15:00",
  "payload": { "externalRefNo": "BEV-OUT-20260930-001", "lines": [ { "skuCode": "BEV-0001", "qty": 30 } ] }
}
```

| ID | 정책 |
|---|---|
| P-MQ-1 | **발행 = Transactional Outbox**: 업무 데이터 변경과 `outbox_event` INSERT를 같은 트랜잭션에서 한다. 스케줄러(1초 주기)가 발행하고 `published_at`을 기록한다. 서버가 DB 커밋 직후 죽어도 메시지가 유실되지 않는다. 대신 **적어도 한 번**(중복 가능) 전달된다 |
| P-MQ-2 | **수신 = 멱등 처리**: `processed_message(message_id PK)` INSERT를 업무 처리와 **같은 트랜잭션**에서 한다. 키가 중복되면 이미 처리한 메시지이므로 ack하고 무시한다. 여기에 업무 키 `(tenant_id, external_ref_no)` UNIQUE를 한 번 더 건다 |
| P-MQ-3 | **오류 구분 [결정]**: 업무 오류(없는 SKU, 다른 화주 SKU, 상태 충돌)는 재시도해도 결과가 같으므로 **재시도하지 않는다**. `REJECTED` 결과 이벤트를 발행하고 ack한다. 기술 오류(DB 연결 실패, 락 타임아웃)만 재시도한다(1초 → 2초 → 4초, 3회). 그래도 실패하면 DLQ로 보낸다 |
| P-MQ-4 | DLQ에 쌓인 메시지는 운영자 관리 API로 조회하고 다시 처리한다 |
| P-MQ-5 | **순서 역전**: Portal은 생성 결과(`ACCEPTED`)를 받은 뒤에만 취소 버튼을 켠다. 그래도 Core에 없는 요청에 대한 취소가 오면 업무 오류(`REJECTED`)로 처리한다 |

---

## 5. 상태 전이

### 5.1 입고예정 `InboundPlanStatus`

| 값 | 의미 | 다음 상태 | 전이 계기 |
|---|---|---|---|
| `REGISTERED` | 예정 등록 | `INSPECTING`, `CANCELED` | 검수 첫 임시저장 / 취소 |
| `INSPECTING` | 검수 중(임시저장) | `CONFIRMED` | 입고확정 → RCV 재고 생성 |
| `CONFIRMED` | 확정, 적치 진행 중 | `COMPLETED` | 적치 잔량이 0이 됨 |
| `COMPLETED` | 입고 완료 | — | 종료 |
| `CANCELED` | 취소 | — | 종료 |

### 5.2 출고요청 `OutboundOrderStatus`

```
RECEIVED ──할당 실행──▶ ALLOCATED ──피킹 시작──▶ PICKING ──전 행 입력──▶ PICKED ──출고확정──▶ SHIPPED
   │  └──할당 실패──▶ ALLOCATION_FAILED ─재할당─┘   │                                    ├─▶ PARTIALLY_SHIPPED
   │                     │                         │                                    └─▶ UNSHIPPED
   └────────┬────────────┴─────────────────────────┘
            ▼
         CANCELED (ALLOCATED에서 취소하면 선점 원복)
```

| 현재 | 가능한 다음 상태 | 그 밖의 요청 |
|---|---|---|
| `RECEIVED` | `ALLOCATED`, `ALLOCATION_FAILED`, `CANCELED` | |
| `ALLOCATION_FAILED` | `ALLOCATED`, `ALLOCATION_FAILED`, `CANCELED` | |
| `ALLOCATED` | `PICKING`, `CANCELED` | |
| `PICKING` | `PICKED` | 취소 → 409 `OUTBOUND_003` |
| `PICKED` | `SHIPPED`, `PARTIALLY_SHIPPED`, `UNSHIPPED` | 취소 → 409 |
| 종료 상태 4개 | — | 모든 변경 → 409 |

### 5.3 할당 행 `AllocationStatus`

`ALLOCATED` → `PICKED`(전량 피킹) / `SHORT`(일부 또는 전부 결품) / `CANCELED`(요청 취소)

### 5.4 Portal 요청 상태 (Portal DB, Core 상태를 비춘 값)

`SUBMITTED`(발행 대기·전송됨) → `ACCEPTED` / `REJECTED` → 이후 Core 결과 이벤트로 받은 상태(`ALLOCATED`, `SHIPPED`, `PARTIALLY_SHIPPED` 등)를 그대로 반영한다.

---

## 6. ERD

### 6.1 core_db

| 테이블 | 주요 컬럼 | 제약 |
|---|---|---|
| `tenant` | code, name, min_ship_remaining_days, min_inbound_remaining_days | code UQ |
| `app_user` | username, password(BCrypt), name, role(`OPERATOR`/`WORKER`), is_active | username UQ. 관리자는 시드, 작업자는 관리자가 생성 |
| `sku` | tenant_id, sku_code, sku_name, spec, base_unit, units_per_box, min_ship_remaining_days, min_inbound_remaining_days, is_active | sku_code UQ |
| `location` | location_code, zone_code, aisle, bay, shelf_level, location_type(`STORAGE`/`RECEIVING`), is_active | location_code UQ |
| `stock` | tenant_id, sku_id, location_id, expiry_date, on_hand_qty, allocated_qty, available_qty(생성) | UQ(tenant_id, sku_id, location_id, expiry_date), IDX(tenant_id, sku_id, expiry_date), CHECK |
| `stock_history` | §3.2 | IDX(tenant_id, sku_id, created_at), IDX(ref_type, ref_id) |
| `inbound_plan` | tenant_id, inbound_no, external_ref_no, source(`PORTAL`/`WMS`), expected_date, status, confirmed_at | UQ(tenant_id, external_ref_no) |
| `inbound_plan_line` | inbound_plan_id, sku_id, expected_qty, variance_reason | |
| `inbound_inspection` | inbound_plan_line_id, expiry_date, good_qty, reject_qty, reject_reason, putaway_qty(누적) | |
| `inspection_upload` | inbound_plan_id, file_name, ok_rows, error_rows, errors(JSON), status | 미리보기 보관용 |
| `outbound_order` | tenant_id, outbound_no, external_ref_no, source, ship_to_name, ship_to_address, requested_ship_date, status, fail_reason | UQ(tenant_id, external_ref_no) |
| `outbound_order_line` | outbound_order_id, sku_id, requested_qty, allocated_qty, shipped_qty, short_qty | |
| `outbound_allocation` | outbound_order_line_id, stock_id, allocated_qty, picked_qty, short_qty, short_reason, status | IDX(stock_id). 로케이션·소비기한은 stock 조인 |
| `outbox_event` | message_id, event_type, tenant_id, payload(JSON), published_at | message_id UQ, IDX(published_at) |
| `processed_message` | message_id(PK), message_type, processed_at | |

모든 테이블에 `id BIGINT PK`, `created_at`, `updated_at`을 둔다(팀 규칙, 추가만 하는 `stock_history`는 `updated_at` 제외). 적치 기록은 별도 테이블 없이 `inbound_inspection.putaway_qty`(누적)와 `stock_history`의 PUTAWAY 이력으로 남긴다. FK는 자식 → 부모 한 방향만 걸어 양방향·순환 참조가 없다(층 구조는 주말 MVP 명세 §3). **DDL 원본은 `V1__init_schema.sql`** (`WMS/주말_MVP_명세.md` 첨부).

### 6.2 Portal — 화주별 DB (`portal_hlt`, `portal_bev`, `portal_fod`)

세 DB의 테이블 구조는 같다. 같은 Flyway 스크립트(`db/portal`)를 세 DB에 적용한다.

| 테이블 | 주요 컬럼 |
|---|---|
| `portal_user` | username, password, name, tenant_id (화주당 1개, 시드). username은 **그 DB 안에서만** UNIQUE |
| `inbound_request` / `inbound_request_line` | tenant_id, request_no(= external_ref_no), expected_date, status, last_event_at / sku_code, qty |
| `outbound_request` / `outbound_request_line` | tenant_id, request_no, ship_to…, status, last_event_at / sku_code, requested_qty, shipped_qty, short_qty |
| `outbox_event`, `processed_message` | Core와 같은 구조 |

---

## 7. API

- 팀 규칙(`07_API_명세_규칙.md`)을 따른다. 각 서버는 `/api/v1/**`, nginx가 `/api/wms` → Core, `/api/portal` → Portal로 넘긴다.
- **예외**: Portal의 명령 API(입고예정·출고요청 등록, 취소)는 처리가 비동기이므로 **202 Accepted**와 `requestNo`, `status: SUBMITTED`를 돌려준다.

### 7.1 WMS Core (운영자·작업자)

| 기능 | 메서드 | URL | 비고 |
|---|---|---|---|
| 화주 / SKU / 로케이션 조회 | GET | `/tenants`, `/skus?tenantId=`, `/locations?type=&zone=` | 시드 조회만 |
| 입고예정 등록 (운영자 대리) | POST | `/inbound-plans` | Portal 메시지와 같은 서비스 호출 |
| 입고예정 목록 / 상세 | GET | `/inbound-plans?tenantId=&status=`, `/inbound-plans/{id}` | |
| 검수 임시저장 | PUT | `/inbound-plans/{id}/inspections` | 전체 교체 |
| 검수 Excel 검증 | POST | `/inbound-plans/{id}/inspection-uploads` | 미리보기 결과 반환, 저장 안 함 |
| 검수 Excel 정상행 저장 | PATCH | `/inspection-uploads/{uploadId}/apply` | 임시저장에 반영 |
| 입고확정 | PATCH | `/inbound-plans/{id}/confirm` | RCV 재고 생성 |
| 적치 | POST | `/inbound-plans/{id}/putaways` | `[{inspectionId, locationId, qty}]` |
| 입고예정 취소 | PATCH | `/inbound-plans/{id}/cancel` | |
| 입고검수서 | GET | `/inbound-plans/{id}/inspection-sheet` | 인쇄용 |
| 재고 요약 (SKU별) | GET | `/stocks/summary?tenantId=` | 실물/선점/가용, 임박 표시 |
| 재고 (로케이션·기한별) | GET | `/stocks?tenantId=&skuId=&locationId=` | |
| 재고이력 | GET | `/stock-histories?tenantId=&skuId=&txType=&from=&to=` | |
| 재고조정 | POST | `/stock-adjustments` | 사유 필수 |
| 출고요청 등록 (운영자 대리) | POST | `/outbound-orders` | |
| 출고요청 목록 / 상세 | GET | `/outbound-orders?tenantId=&status=`, `/outbound-orders/{id}` | 상세에 할당 결과 포함 |
| 할당 실행 | PATCH | `/outbound-orders/{id}/allocate` | |
| 출고요청 취소 | PATCH | `/outbound-orders/{id}/cancel` | 선점 원복 |
| 피킹 시작 | PATCH | `/outbound-orders/{id}/start-picking` | |
| 피킹리스트 | GET | `/outbound-orders/{id}/pick-list` | 로케이션 순, 인쇄용 |
| 피킹수량 입력 | PATCH | `/outbound-allocations/{id}/pick` | `{pickedQty, shortReason}` |
| 출고확정 | PATCH | `/outbound-orders/{id}/confirm-shipment` | |
| 출고명세서 | GET | `/outbound-orders/{id}/delivery-note` | 인쇄용 |
| DLQ 조회 / 재처리 | GET / POST | `/admin/dead-letters`, `/admin/dead-letters/{id}/replay` | |
| 시연 데이터 리셋 | POST | `/admin/demo-reset` | 리허설용 |
| 로그인 | POST | `/auth/login` | |
| 작업자 계정 생성 / 목록 | POST / GET | `/users` | OPERATOR만 호출 가능. 수정·삭제 없음 |

**내부 API (Portal → Core, `X-Service-Key` 헤더)**

| 기능 | 메서드 | URL |
|---|---|---|
| 화주 재고 요약 | GET | `/internal/v1/tenants/{tenantId}/stock-summary` |
| 출고 상세 (할당·출고 결과) | GET | `/internal/v1/tenants/{tenantId}/outbound-orders/{externalRefNo}` |

### 7.2 Portal (화주)

| 기능 | 메서드 | URL | 응답 |
|---|---|---|---|
| 로그인 / 내 정보 | POST / GET | `/auth/login`, `/auth/me` | 로그인 본문에 `tenantCode` 포함 (P-TN-7) |
| 입고예정 등록 | POST | `/inbound-requests` | 202 |
| 입고예정 목록 / 상세 | GET | `/inbound-requests`, `/inbound-requests/{id}` | |
| 출고요청 등록 | POST | `/outbound-requests` | 202 |
| 출고요청 목록 / 상세 | GET | `/outbound-requests`, `/outbound-requests/{id}` | |
| 출고요청 취소 | PATCH | `/outbound-requests/{id}/cancel` | 202 |
| 재고 현황 | GET | `/stocks` | Core 내부 API 호출 |

### 7.3 에러 코드 (일부)

| 코드 | HTTP | 메시지 |
|---|---|---|
| `STOCK_001` | 409 | 가용재고가 부족합니다 |
| `STOCK_002` | 400 | 조정 후 수량이 선점수량보다 작을 수 없습니다 |
| `INBOUND_001` | 400 | 예정수량을 초과했습니다 |
| `INBOUND_002` | 409 | 이미 확정된 입고입니다 |
| `INBOUND_003` | 400 | 로케이션 혼적 규칙 위반입니다 |
| `OUTBOUND_001` | 409 | 이 상태에서는 할당할 수 없습니다 |
| `OUTBOUND_003` | 409 | 피킹이 시작된 출고요청은 취소할 수 없습니다 |
| `TENANT_001` | 400 | 다른 화주의 SKU가 포함되어 있습니다 |

---

## 8. 화면 — 표 형식, AI로 생성

**원칙 [결정]**: 백엔드 API와 Swagger를 먼저 완성한다. 그다음 Swagger 스펙(요청·응답 DTO)을 AI에 넣고 "표 + 폼 + 버튼" 화면을 생성한다. 디자인은 다듬지 않는다. 컴포넌트 라이브러리 하나를 정해 전원이 같이 쓴다.

| 경로 | 화면 | 핵심 요소 |
|---|---|---|
| `/wms/inbound` | 입고예정 목록 → 상세 | 검수 입력 표(라인 × 소비기한 행), Excel 업로드 결과 표(정상/오류), 확정 버튼, 적치 입력 표 |
| `/wms/stocks` | 재고 요약 / 로케이션별 | 실물·선점·가용 컬럼, 임박 행 강조 |
| `/wms/histories` | 재고이력 | 필터 + 페이징 |
| `/wms/outbound` | 출고요청 목록 → 상세 | 할당 결과 표(로케이션, 소비기한, 수량), 할당 / 취소 / 피킹 시작 / 확정 버튼 |
| `/wms/admin` | DLQ, 시연 리셋 | |
| `/picking` | 피킹 작업 | 로케이션 순 표, 행마다 피킹수량 + 결품사유 입력 |
| `/portal/*` | 로그인, 입고예정, 출고요청, 재고 | 화주별로 고정된 목록과 등록 폼 |

---

## 9. 일정 — Core 먼저, Portal은 나중에 붙인다

| 주 | 기간 | 테마 | 주말 체크포인트 |
|---|---|---|---|
| 1 | ~9/20 | 설계 v2 + 뼈대 | ERD·Flyway 시드·멀티모듈 뼈대·메시지 계약 확정 |
| 2 | 9/21~9/25 | **Core 한 바퀴 (B화주 하나로)** | WMS 화면만으로 입고부터 부분출고까지 한 바퀴 |
| 3 | 9/28~10/2 | 예외·격리 + **Portal 연결** | Portal 요청 → Core 처리 → Portal 상태 반영, 핵심 테스트 CI 통과 |
| 4 | 10/5~10/9 | 관측·마감·발표 | 리허설 2회 |

> ⚠ **추석 연휴(9/24~9/26 전후)와 10/9 한글날에 작업하는지 먼저 확인한다.** 2주차 목·금이 빠지면 2주차 체크포인트를 3주차 화요일로 미루고, 3주차의 Excel 업로드를 4주차로 넘긴다.

### 9.1 이번 주말 (9/19~20) — WMS 백엔드 MVP

**`WMS/주말_MVP_명세.md`를 따른다.** 목표: 화면 없이 WMS Core 백엔드만으로 입고 → 검수 → 확정 → 적치 → 출고요청 → FEFO 할당 → 피킹 → 출고확정 → 이력 조회가 Talend API Tester에서 끝까지 통과.

| 담당 | 주말 범위 |
|---|---|
| ① 출고 | 출고요청 등록·조회, FEFO 할당(락 없음), 피킹 시작·입력, 출고확정 |
| ② 나 | 뼈대, docker-compose, Flyway V1·V2, 기준정보 조회 API, 병합. 남는 시간에 Portal 라우팅 뼈대 |
| ③ 재고·인증 | `StockService` 5개 메서드 + 이력, 재고·이력 조회, 로그인(적용은 월요일) |
| ④ 입고 | 입고예정 등록·조회·취소, 검수 저장, 입고확정, 적치 |

- 수정(PUT) API는 만들지 않는다. 잘못 넣었으면 취소하고 다시 등록한다.
- 결품·부분출고·취소 원복·혼적 규칙·락은 2주차로 넘긴다.

### 9.2 2주차 — Core 한 바퀴 (단일 화주 B 음료)

| | 월·화 | 수·목 | 금 |
|---|---|---|---|
| ① 출고 | FEFO 할당 계획(후보 조회·정렬·분할·잔여일·all-or-nothing). ③의 `StockService` 인터페이스에 맞춰 단위 테스트부터 | 피킹 시작, 피킹 입력, 결품, 출고확정, 부분출고 | 통합 |
| ② 나 | Portal 로그인, 입고예정·출고요청 등록(DB 저장), CI(빌드 + Testcontainers) | Outbox 발행기, 익스체인지·큐·DLQ 설정, Core 리스너 뼈대 | 통합, **시험 배포 1회** |
| ③ 재고·인증 | `StockService`: 입고·적치·선점·해제·결품·출고 차감 + 이력 + CHECK, 비관적 락 | 취소 원복, 동시 100건 재현 테스트, 데드락 방지(락 순서) | 통합 |
| ④ 입고 | 검수 임시저장·확정 (소비기한 여러 행, 불량 분리, 입고허용 잔여일) | 분할 적치, 혼적 규칙 | 통합 |

**체크포인트**: WMS 화면만으로 입고예정 → 검수 → 확정 → 적치 → 출고요청 → FEFO 할당 → 피킹(결품 1건) → 부분출고 → 이력 조회까지 된다.

### 9.3 3주차 — 예외·격리·Portal 연결

| | 월·화 | 수·목 | 금 |
|---|---|---|---|
| ① 출고 | 출고허용 잔여일 경계 테스트, 결품 복합 케이스(같은 재고 행을 여러 주문이 선점), 출고 결과 이벤트 내용 정의(②와 함께) | FEFO 시연 데이터 설계(기한이 섞인 재고), 버그 | 회고 |
| ② 나 | Core 리스너 멱등 처리, 오류 분류·재시도·DLQ, 결과 이벤트 → Portal 상태 반영 | Core 중지 → 적체 → 복구 시나리오, Prometheus 도메인 메트릭 | E2E |
| ③ 재고·인증 | 조건부 UPDATE 방식 추가, 두 방식 비교 → 결정로그, Core 화주 격리 테스트 | **Portal 합류**: 로그인 사용자 → 화주 고정, 다른 화주 접근 404, Portal 목록·상세·재고 화면 | 회고 |
| ④ 입고 | Excel 검수 업로드 (검증·미리보기·정상행 저장) | 인쇄 3종 (입고검수서, 피킹리스트, 출고명세서) | 회고 |

**체크포인트**: Portal에서 요청하면 상태가 돌아온다. 핵심 테스트(§11)가 CI에서 통과한다.

### 9.4 4주차 — 관측·마감

| 요일 | 할 일 |
|---|---|
| 월 | ②: Grafana 대시보드 1장, HTTPS 적용, Portal·Core 분리 배포 / 나머지: 시연 리셋, 버그 |
| 화 | 버그 수정, 시연 데이터 확정 |
| 수 | **오전 코드 프리즈**, 발표 자료 |
| 목 | 리허설 1회 + 피드백 반영 |
| 금 | 리허설 2회 또는 발표 |

### 9.5 "Core 먼저, Portal 나중" 구조에서 기억할 점

- **Portal이 늦어도 1순위 시연은 안전하다.** Core가 운영자 대리 등록 API를 갖고 있기 때문이다.
- **Portal을 붙이는 비용이 작다.** REST 컨트롤러와 MQ 리스너가 같은 서비스를 호출하므로, Core 쪽에는 리스너와 멱등 처리만 추가하면 된다.
- **위험: 인프라 전체(MQ, CI/CD, 배포, 관측)가 ②에게 몰린다.** Portal의 업무 화면은 3주차에 ③이 합류해 나눠 맡는다. 그래도 막히면 아래 삭감 순서를 따른다.

### 9.6 일정이 밀릴 때 삭감 순서

1. PDF → 브라우저 인쇄로 대체 (이미 기본값)
2. Grafana 대시보드 → `/actuator/prometheus` 메트릭 노출만
3. DLQ 재처리 → 조회만
4. Excel 검수 업로드
5. Portal 재고 조회(내부 REST) → Portal은 요청 상태만 보여줌

**절대 삭감 불가**: FEFO 분할할당, 동시성 제어, 결품·부분출고, 취소 원복, 이력 불변식, 화주 격리, 수신 멱등 처리

---

## 10. 역할 분담

원칙: **네 명 모두 발표와 면접에서 설명할 업무 규칙을 하나씩 갖는다.** 인프라를 맡은 사람도 예외가 아니다.

| 담당 | 맡는 것 | 화면 | 설명할 거리 (결정로그) |
|---|---|---|---|
| **① 출고 (FEFO)** | 출고요청, FEFO 할당 계획(후보·정렬·분할·잔여일·all-or-nothing), 피킹, 결품, 부분출고, 출고확정 | `/wms/outbound`, `/picking` | FEFO에 출고허용 잔여일을 더한 이유, 부족 시 전부 아니면 전무를 고른 이유, 결품 시 실물까지 줄인 이유 (D-04, D-05) |
| **② 나 (Portal·인프라)** | Portal 서버 뼈대·요청 흐름, 메시지 계약, Outbox, 멱등 수신, 재시도·DLQ, docker-compose, Flyway, CI/CD, HTTPS·배포, Prometheus·Grafana | `/portal/*` 일부, `/wms/admin` | 서버 분리와 명령=MQ·조회=REST, Outbox로 유실 방지, 업무 오류와 기술 오류를 나눠 DLQ 처리 (D-07~D-09) |
| **③ 재고·동시성·인증** | `StockService`(모든 재고 변경의 단일 창구, 이력, CHECK), 선점·해제·취소 원복, 비관적 락 vs 조건부 UPDATE 비교, 로그인·역할·작업자 계정, 화주 격리(Core + Portal). 3주차 후반 Portal 합류 | `/wms/stocks`, `/wms/histories`, `/portal/*` 일부 | 재고 변경 창구를 하나로 모은 이유와 이력 불변식, 두 락 방식 측정 비교, 격리 이중 방어 (D-06, D-10) |
| **④ 입고 · Excel · 전표** | 입고예정, 검수(소비기한 여러 행, 불량 분리, 입고허용 잔여일), 확정, 분할 적치·혼적 규칙, Excel 검수 업로드, 인쇄 3종 | `/wms/inbound` | 한 라인에 소비기한이 여럿인 검수 구조, 임시저장과 확정을 나눈 이유, Excel 검증 규칙과 정상행만 반영, 혼적 규칙 (D-02, D-03) |

- **HTTPS는 ②, 로그인·JWT는 ③이다.** HTTPS는 인증서와 nginx 설정이라 배포 인프라에 속한다.
- **④가 난이도가 가장 낮은 역할이다.** 동시성·메시지가 없고, 재고 변경은 ③의 `StockService`를 호출만 한다. 대신 입고는 흐름의 맨 앞이므로, 입고가 늦어져도 ①·③이 막히지 않도록 2주차에는 **재고 샘플을 SQL로 직접 넣어** 개발한다.
- **재고 테이블을 직접 UPDATE하는 코드는 ③의 `StockService` 밖에 두지 않는다.** 입고(④)와 출고(①)는 이 서비스만 호출한다. 어기면 PR에서 반려한다.

### 10.1 ①과 ③의 경계 — 할당 코드를 두 사람이 나누는 방법

FEFO(①)와 선점·락(③)은 같은 트랜잭션 안에서 만난다. **"무엇을 몇 개 잡을지"는 ①, "안전하게 잡는 방법"은 ③**으로 나눈다.

```java
// ③ 소유 — 락, 수량 변경, 이력, CHECK
interface StockService {
    List<StockRow> lockAllocatable(Long tenantId, Long skuId, LocalDate minExpiry); // 정렬·FOR UPDATE까지 책임
    void allocate(Long stockId, int qty, RefType refType, Long refId);
    void deallocate(Long stockId, int qty, RefType refType, Long refId);
    void shortage(Long stockId, int qty, String reason, Long refId);
    void ship(Long stockId, int qty, Long refId);
}

// ① 소유 — FEFO 정책. DB 없이 단위 테스트 가능
class FefoAllocationPlanner {
    AllocationPlan plan(List<StockRow> candidates, int requestedQty); // 분할 결과 또는 부족
}
```

- ①은 2주차 월요일에 가짜 `StockRow` 목록으로 `FefoAllocationPlanner` 단위 테스트부터 쓴다. ③의 구현을 기다리지 않는다.
- 조건부 UPDATE 방식으로 바꿔도 ③의 `StockService` 구현만 바뀌고 ①의 코드는 그대로다. 이 경계가 D-06 비교를 가능하게 한다.

## 11. 핵심 테스트 시나리오

> 락과 동시성 테스트는 H2에서 MySQL과 다르게 동작하므로 **Testcontainers(MySQL 8)**로 돌린다. GitHub Actions에서도 동작한다.

| ID | 시나리오 | 기대 결과 |
|---|---|---|
| T-IN-1 | 예정 100, 정상 95 + 파손 5로 확정 | RCV 재고 95, 파손분 재고 없음, INBOUND 이력 1건 |
| T-IN-2 | 확정 전 재고 조회 | 재고 변화 없음 |
| T-IN-3 | 60 / 35로 나눠 적치 | 두 로케이션 가용 60 / 35, RCV 0, 입고 COMPLETED |
| T-IN-4 | 다른 화주 재고가 있는 로케이션에 적치 | `INBOUND_003` |
| T-IN-5 | Excel: 없는 SKU, 합계 초과, 과거 소비기한이 섞인 파일 | 오류행 3개 분류, 정상행만 저장, 재고 변화 없음 |
| T-IN-6 | 확정된 입고에 Excel 업로드 | 파일 전체 거부 |
| T-AL-1 | 소비기한 11/30(20개), 10/31(10개), 12/31 재고에 25개 요청 | 10/31 10개 → 11/30 15개 순으로 할당 |
| T-AL-2 | 한 로케이션 가용 부족 | 여러 로케이션으로 분할, 합계 = 요청수량 |
| T-AL-3 | 잔여일이 출고허용 잔여일보다 적은 재고만 있음 | 할당 대상에서 제외, `ALLOCATION_FAILED` |
| T-AL-4 | 라인 2개 중 1개만 부족 | 전체 롤백, 선점 0, 부족 수량 기록 |
| **T-CC-1** | 가용 100에 10개짜리 요청 동시 20건 | 성공 10건, 실패 10건, 선점 합계 100, 음수 없음 |
| **T-CC-2** | SKU 2개를 반대 순서로 담은 요청 동시 실행 | 데드락 없이 완료 |
| T-CC-3 | 같은 부하를 비관적 락과 조건부 UPDATE로 각각 실행 | 둘 다 초과 선점 0, p95·재시도 횟수 기록 |
| T-CN-1 | ALLOCATED에서 취소 | 모든 행 선점 원복, 가용 = 취소 전 가용 + 할당량, DEALLOCATE 이력 |
| T-CN-2 | PICKING에서 취소 | 409 `OUTBOUND_003`, 수량 변화 없음 |
| T-PK-1 | 할당 30, 피킹 28 | 실물 −2, 선점 −2, SHORTAGE 이력, 사유 기록 |
| T-PK-2 | 같은 행을 다른 주문도 선점한 상태에서 결품 | CHECK 제약 위반 없음, 다른 주문의 선점 유지 |
| T-SH-1 | 결품 있는 건 출고확정 | PARTIALLY_SHIPPED, 라인별 출고 / 미출고 기록, OUTBOUND 이력 |
| T-SH-2 | 전 행 결품 후 확정 | UNSHIPPED, 실물 차감 없음(결품 조정 제외) |
| **T-LG-1** | 위 시나리오를 모두 실행한 뒤 | 모든 재고 행에서 Σ이력 = 현재 수량 (불변식) |
| **T-TN-1** | A화주 출고요청에 B화주 SKU 포함 | `TENANT_001`, 선점 없음 |
| **T-TN-2** | A와 B가 같은 품목명의 SKU를 가진 상태에서 A 할당 | A 재고에서만 할당 |
| T-TN-3 | Portal A 사용자가 B 요청 id로 조회 | 404 (A의 DB에는 그 id가 없음) |
| **T-TN-4** | Portal 요청 처리 후 같은 스레드에서 다음 요청 | `TenantContext`가 비어 있음 (이전 화주가 남지 않음) |
| T-TN-5 | Outbox 스케줄러 1회 실행 | 화주 3개 DB의 미발행 이벤트가 각각 발행되고, 각 DB의 `published_at`만 갱신됨 |
| T-TN-6 | B화주 결과 이벤트 수신 | `portal_bev`에만 반영, 다른 DB 변화 없음 |
| **T-MQ-1** | 같은 messageId를 두 번 수신 | 한 번만 처리, 두 번째는 ack 후 무시 |
| T-MQ-2 | 업무 오류 메시지(없는 SKU) | 재시도 없음, REJECTED 이벤트, DLQ 비어 있음 |
| T-MQ-3 | 리스너에서 기술 오류 강제 발생 | 3회 재시도 후 DLQ |
| T-MQ-4 | Outbox 발행 직전에 발행기 중지 → 재시작 | 메시지 유실 없음 |

---

## 12. 발표·시연 시나리오 (약 12분)

| # | 시간 | 내용 | 보여줄 것 |
|---|---|---|---|
| 1 | 1분 | 한 줄 소개 + 아키텍처 1장 | Portal / Core 분리, 명령은 MQ, 재고 트랜잭션은 Core DB |
| 2 | 2분 | **입고**: B화주 Portal에서 생수 100박스 입고예정 → WMS에서 검수(소비기한 2종, 파손 5) → 확정 → 두 로케이션에 적치 | 확정 직후 가용 0 → 적치 후 가용 95 |
| 3 | 1.5분 | **FEFO 분할할당**: Portal에서 30박스 출고요청 → WMS 할당 | 임박 기한 로케이션부터 두 곳으로 나뉜 할당 표, 실물·선점·가용 변화 |
| 4 | 1.5분 | **동시성**: 테스트 또는 스크립트로 동시 요청 100건 | 초과 선점 0, Grafana 할당 성공·실패 그래프, 두 락 방식 비교표 |
| 5 | 2분 | **결품 → 부분출고**: 피킹에서 28박스만 입력 → 출고확정 | SHORTAGE·OUTBOUND 이력, Portal 상태 "부분출고 28/30" |
| 6 | 1분 | **취소 원복**: 다른 요청을 할당 후 취소 | 가용재고가 원래대로 |
| 7 | 1.5분 | **장애 처리**: Core 컨테이너 중지 → Portal에서 요청 3건 → 큐 적체 그래프 → Core 재시작 → 처리 완료, 같은 메시지 재발행 → 한 번만 처리 | RabbitMQ 큐 길이, processed_message |
| 8 | 1분 | **화주 격리**: A화주로 로그인 → B 데이터 안 보임, B의 SKU로 출고요청 → 거부 | 404, `TENANT_001` |
| 9 | 0.5분 | 마무리: 이력 불변식 검사 결과, CI 테스트 통과 화면, 결정로그 2개 | |

리허설 전에는 매번 `/admin/demo-reset`으로 데이터를 초기화한다.

---

## 13. 결정로그 작성 대상

`docs/결정로그.md`에 아래 순서로 남긴다. 기각한 대안을 반드시 적는다.

| ID | 결정 | 기각한 대안 |
|---|---|---|
| D-01 | 주제 전환: 성능 측정 중심 → 정합성·예외·멀티테넌시 중심 | v1 유지 |
| D-02 | 로트 없이 SKU + 소비기한으로 재고 구분 | 로트 번호 관리 |
| D-03 | 로케이션 한 곳 = 화주 1, SKU 1, 소비기한 1 | 자유 혼적 |
| D-04 | 할당 부족 시 전부 아니면 전무 | 가능한 만큼 부분할당 |
| D-05 | 결품 시 실물과 선점을 즉시 함께 차감 | 선점만 해제 / 재고조사 후 조정 |
| D-06 | 동시성: 비관적 락 vs 조건부 UPDATE (측정 후 선택) | 낙관적 락(@Version), Redis 분산 락 |
| D-07 | Portal·Core 물리 분리 + DB 분리 | 단일 서버 내 모듈 분리 |
| D-08 | 명령은 MQ, 조회는 REST | 전부 REST / 전부 MQ |
| D-09 | Transactional Outbox + processed_message | 커밋 후 바로 발행, 발행 실패 무시 |
| D-10 | 화주 필터를 리포지토리 파라미터로 명시 | Hibernate Filter, AOP 자동 주입 |
| D-11 | Core는 Shared Schema, Portal은 화주별 DB (공유 자원·교차 규칙·전체 조회 유무로 판단) | 양쪽 모두 Shared Schema / 양쪽 모두 DB 분리 / 로그인 시점에 DB 생성 |

---

## 14. 팀이 정해야 할 것 (월요일 오전까지)

- [ ] [가정] 표시된 잔여일 값 (§2.1)
- [ ] 추석 연휴 작업 여부 → 2주차 체크포인트 날짜
- [ ] 프론트 컴포넌트 라이브러리 하나
- [ ] 배포: 서버 2대(VM 분리)로 할지, VM 1대에 컨테이너만 분리할지
