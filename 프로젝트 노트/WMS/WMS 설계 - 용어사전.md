---
출처: Claude 분석
원본: claude.ai 프로젝트 「미니프로젝트」 팀규칙/04_용어사전.md
작성일: 2026-09-18
tags: [용어]
---

> 상위: [[KDT_1차 정규프로젝트 MOC]]

# 04. 용어 사전 (Glossary)

> **한 개념 = 한 단어.** 코드, DB, API, 화면, 대화 전부에서 같은 단어를 쓴다.
> AI가 만든 이름이 여기와 다르면 AI 코드를 고친다. 사전에 없는 단어를 새로 써야 하면 **사전에 먼저 추가**하고 코드를 쓴다.
> `CLAUDE.md`의 용어 표에도 같은 내용을 복사한다.
>
> **현재 범위: 단일 WMS (화주 도입 전, 2026-09-19 기준).** 화주·Portal·메시지 관련 용어는 도입할 때 §6에서 옮겨 온다.

## 작성 규칙

- 한글 용어는 팀이 말할 때 쓰는 단어. 영문은 하나만 (동의어 금지).
- 코드 열에는 클래스/변수명, DB 열에는 테이블/컬럼명.
- "설명"에는 이 용어가 무엇이고 무엇이 **아닌지** 한 줄.
- 상태값은 별도 표로 enum 값 전체를 적는다.
- 수량 컬럼·필드는 `_qty` / `Qty` 접미사로 통일한다 (`quantity`, `count`, `amount` 섞어 쓰지 않음).

## 1. 엔티티 / 개념

### 1.1 기준정보

| 한글 | 영문 | 코드 | DB | 설명 |
|---|---|---|---|---|
| 창고 | warehouse | `Warehouse` | `warehouse` | 물류센터 건물 1곳. 지금은 WH-01 하나 |
| 구역 | zone | `Zone` | `zone` | 창고 안의 구획. A/B/C, 전부 상온, 각 120칸. **품목·화주별로 나누지 않는다** (표시용) |
| 로케이션 | location | `Location`, `locationCode` | `location`, `location_code` | 팔레트 랙의 **한 칸 = 표준 팔레트 1장 자리**. 코드 `A-01-03-2` = 구역-통로-베이-단. 창고·구역을 가리키는 말이 아니다 |
| 통로 / 베이 / 단 | aisle / bay / shelf level | `aisle`, `bay`, `shelfLevel` | `aisle`, `bay`, `shelf_level` | 로케이션 코드의 2·3·4번째 자리. 단 1 = 바닥 |
| 품목 | product | `Product`, `productCode` | `product`, `product_code` | 재고를 세는 최소 상품 단위. 규격이 다르면 다른 품목 |
| 품목코드 (SKU) | product code | `productCode` | `product_code` | 품목의 코드 값 `SKU-10001`. "SKU"는 값의 형식 이름일 뿐, 클래스·테이블명으로 쓰지 않는다 |
| 단위 | unit | `unit` | `unit` | 재고를 세는 단위 `EA` / `BOX`. 환산하지 않는다 |
| 소비기한 관리 여부 | expiry managed | `isExpiryManaged` | `is_expiry_managed` | N이면 소비기한을 `9999-12-31`로 저장 |
| 출고허용 잔여일 | min ship days | `minShipDays` | `min_ship_days` | 소비기한까지 이 일수보다 적게 남은 재고는 할당하지 않는다 |
| 팔레트 적재수량 | pallet qty | `palletQty` | `pallet_qty` | 이 품목을 한 칸에 최대 몇 개 올릴 수 있는지. 칸이 아니라 품목의 속성 |
| 안전재고 | safety stock | `safetyStock` | `safety_stock` | 이 수량 아래로 가용재고가 떨어지면 경고 (2차) |
| 사용자 | user | `User`, `userId` | `users`, `username` | 시스템 로그인 계정. 테이블만 예약어 회피로 복수형 |
| 사용여부 | active | `isActive` | `is_active` | 삭제 대신 비활성 (`Y` / `N`) |

### 1.2 입고

| 한글 | 영문 | 코드 | DB | 설명 |
|---|---|---|---|---|
| 발주 | purchase order | `PurchaseOrder`, `poNo` | `purchase_order`, `po_no` | 들어올 물건의 예정 1건 (= 입고예정). 번호 `PO-20260919-001` |
| 공급처명 | supplier name | `supplierName` | `supplier_name` | 물건을 보내는 곳의 이름. **거래처 테이블 없이 텍스트** |
| 발주 품목 | purchase order item | `PurchaseOrderItem` | `purchase_order_item` | 발주 안의 품목 1줄. 발주 1 : 품목 N |
| 예정수량 | expected qty | `expectedQty` | `expected_qty` | 발주 때 오기로 한 수량 |
| 검수 | inspection | `Inspection` | `inspection` | 도착한 물건을 세고 상태·소비기한을 확인한 결과. **품목 1줄 × 소비기한 1행** |
| 정상수량 / 불량수량 | good qty / reject qty | `goodQty`, `rejectQty` | `good_qty`, `reject_qty` | 불량은 재고가 되지 않는다 |
| 차이사유 | variance reason | `VarianceReason` | `variance_reason` | 검수 합계가 예정보다 적은 이유 |
| 적치 | putaway | `Putaway` | `putaway` | 검수된 정상품을 어느 칸에 몇 개 올릴지 지정한 것 |
| 입고확정 | confirm | `purchaseOrder.confirm()` | `completed_at` | 적치 지정대로 **재고가 생기는** 순간 |

### 1.3 재고

| 한글 | 영문 | 코드 | DB | 설명 |
|---|---|---|---|---|
| 재고 | stock | `Stock` | `stock` | **품목 × 로케이션 × 소비기한** 한 조합의 수량. 로트 번호는 쓰지 않는다 |
| 소비기한 | expiry date | `expiryDate` | `expiry_date` | 먹어도 되는 마지막 날. "유통기한"이라고 쓰지 않는다 |
| 남은 일수 | days left | `daysLeft` | (계산값) | 소비기한 − 오늘. 30일 이하면 임박 |
| 실물재고 | on hand | `onHandQty` | `on_hand_qty` | 칸에 실제로 있는 수량 |
| 선점재고 | allocated | `allocatedQty` | `allocated_qty` | 출고하기로 찜해 둔 수량. 아직 칸에 있다 |
| 가용재고 | available | `available()` | `available_qty` (생성 컬럼) | 실물 − 선점. 새 출고지시가 쓸 수 있는 수량 |
| 재고 이력 | stock history | `StockHistory` | `stock_history` | 재고 수량이 바뀔 때마다 남기는 한 줄. 수정·삭제하지 않는다 |
| 재고 조정 | adjustment | `stockService.adjust()` | `tx_type = 'ADJUST'` | 실사 결과에 맞춰 수량을 고치는 것. 사유 필수 |

### 1.4 출고

| 한글 | 영문 | 코드 | DB | 설명 |
|---|---|---|---|---|
| 주문 | order | `Order`, `orderNo` | `orders`, `order_no` | 배송처로 보내 달라는 요청 1건. 번호 `ORD-…`. 테이블만 예약어 회피로 복수형 |
| 배송지 | ship-to | `shipToName`, `shipToAddress`, `shipToPhone` | `ship_to_name`, `ship_to_address`, `ship_to_phone` | 주문 물건을 받는 곳. **거래처 테이블 없이 주문에 텍스트** |
| 주문 품목 | order item | `OrderItem` | `order_item` | 주문 안의 품목 1줄 |
| 출고지시 | delivery order | `DeliveryOrder`, `doNo` | `delivery_order`, `do_no` | 창고가 **여러 주문을 묶어** 한 번에 처리하는 작업 단위. 번호 `DO-…`. 주문과 다르다 |
| 출고지시 품목 | delivery order item | `DeliveryOrderItem` | `delivery_order_item` | 묶인 주문들의 품목별 합계 |
| 소요량 | required qty | `requiredQty` | `required_qty` | 출고지시 품목의 합계 수량 |
| 할당 | allocation | `Allocation`, `allocate()` | `allocation` | 소요량을 어느 재고 행에서 몇 개 가져올지 정하고 **선점**하는 것. 할당 1행 = 피킹 항목 1개 |
| FEFO | first expired, first out | `FefoAllocationPlanner` | — | 소비기한이 빠른 재고부터 할당. FIFO(입고 순)가 아니다 |
| 피킹 | picking | `startPicking()`, `pick()` | `pick_seq`, `picked_qty` | 작업자가 할당된 칸에서 물건을 집는 일. 순서는 로케이션 코드 순 |
| 피킹 순번 | pick sequence | `pickSeq` | `pick_seq` | 피킹 시작 때 로케이션 코드 순으로 매기는 번호 |
| 결품 | shortage | `shortQty` | `short_qty` | 할당된 칸에 물건이 모자란 것 (2주차) |
| 출고확정 | confirm shipment | `confirmShipment()`, `stockService.ship()` | `shipped_at` | 물건이 창고를 떠남. **실물재고가 줄어드는 유일한 순간** |

## 2. 동작 / 동사

| 한글 | 영문 | 코드 | 설명 |
|---|---|---|---|
| 등록 | create | `createPurchaseOrder()` | 팀 규칙: create / get / getList / update / delete |
| 취소 | cancel | `purchaseOrder.cancel()` | 삭제가 아니라 상태를 `CANCELED`로 |
| 검수 저장 | save inspections | `saveInspections()` | 전체 교체 방식 (기존 행 지우고 새로 저장) |
| 적치 지정 저장 | save putaways | `savePutaways()` | 전체 교체 방식 |
| 입고확정 | confirm | `confirm()` | 발주 `PUTAWAY` → `COMPLETED`, 재고 생성 |
| 재고 입고 | receive | `stockService.receive()` | 재고 행 생성 또는 합산 + `INBOUND` 이력 |
| 할당 | allocate | `stockService.allocate()` | 선점 + `ALLOCATE` 이력. 실물은 그대로 |
| 선점 해제 | deallocate | `stockService.deallocate()` | 선점 − + `DEALLOCATE` 이력 (2주차) |
| 피킹 시작 | start picking | `startPicking()` | 순번 부여, 출고지시 `PICKING` |
| 피킹 완료 | pick | `allocation.pick(qty)` | 항목 `WAITING` → `PICKED` |
| 출고 | ship | `stockService.ship()` | 실물·선점 동시 차감 + `OUTBOUND` 이력 |

## 3. 상태값 (enum, 전부 `@Enumerated(EnumType.STRING)`)

### PurchaseOrderStatus (발주)

| 값 | 한글 | 의미 | 다음 상태 |
|---|---|---|---|
| `REGISTERED` | 발주등록 | 입고예정. 아직 도착 전 | `INSPECTING`, `CANCELED` |
| `INSPECTING` | 검수중 | 검수 결과를 저장함 (재저장 가능) | `PUTAWAY` |
| `PUTAWAY` | 적치중 | 적치 칸을 지정함 (재저장 가능) | `COMPLETED` |
| `COMPLETED` | 입고완료 | 재고 생성됨. 종료 | — |
| `CANCELED` | 취소 | 종료 | — |

### OrderStatus (주문)

| 값 | 한글 | 의미 | 다음 상태 |
|---|---|---|---|
| `RECEIVED` | 접수 | 출고지시에 아직 안 묶임 | `ASSIGNED`, `CANCELED` |
| `ASSIGNED` | 출고지시됨 | 출고지시에 묶임 | `SHIPPED`, `RECEIVED`(출고지시 취소 시) |
| `SHIPPED` | 출고완료 | 종료 | — |
| `CANCELED` | 취소 | 종료 | — |

### DeliveryOrderStatus (출고지시)

| 값 | 한글 | 의미 | 다음 상태 |
|---|---|---|---|
| `CREATED` | 생성 | 주문을 묶고 품목을 합산함. 선점 없음 | `ALLOCATED`, `CANCELED` |
| `ALLOCATED` | 할당완료 | 선점됨 | `PICKING`, `CANCELED`(2주차) |
| `PICKING` | 피킹중 | 순번 부여됨 | `PICKED` |
| `PICKED` | 피킹완료 | 모든 항목 입력됨 | `SHIPPED` |
| `SHIPPED` | 출고완료 | 실물 차감됨. 종료 | — |
| `CANCELED` | 취소 | 종료 | — |

### AllocationStatus (할당 겸 피킹 항목)

| 값 | 한글 | 다음 상태 |
|---|---|---|
| `WAITING` | 대기 | `PICKED`, `SHORT`(2주차), `CANCELED`(2주차) |
| `PICKED` | 완료 | — |
| `SHORT` | 결품 | — |
| `CANCELED` | 취소 | — |

### 기타 enum

| enum | 값 |
|---|---|
| `UserRole` | `ADMIN` 관리자 / `WORKER` 작업자 |
| `StockTxType` | `INBOUND` 입고 / `ALLOCATE` 선점 / `DEALLOCATE` 선점 해제 / `SHORTAGE` 결품 / `OUTBOUND` 출고 / `ADJUST` 조정 |
| `RefType` | `PURCHASE_ORDER` / `DELIVERY_ORDER` / `ADJUSTMENT` |
| `RejectReason` | `DAMAGED` 파손 / `EXPIRY_SHORT` 소비기한 부족 |
| `VarianceReason` | `NOT_ARRIVED` 미도착 / `WRONG_ITEM` 오배송 / `ETC` 기타 |

## 4. 쓰지 않기로 한 단어 (동의어 금지)

| 쓰지 않음 | 대신 | 이유 |
|---|---|---|
| inventory | stock | |
| sku (클래스·테이블명) | product | SKU는 품목코드 값의 형식 이름으로만 쓴다 |
| lot, 로트, batch | stock (재고 행) | 로트 번호를 관리하지 않는다. 소비기한으로 구분 |
| 유통기한, shelf life | 소비기한, expiry date | 2023년부터 식품 표시가 소비기한으로 바뀜 |
| receipt, inbound order | purchase order (발주) | |
| shipment, outbound order (출고지시 의미) | delivery order (출고지시) | |
| reserve, reservation, hold | allocate, allocated (선점) | |
| quantity, count, amount (수량) | qty | 기존 팀 테이블과 맞춤 |
| member, account | user | |
| partner, 거래처, client, vendor, customer | 공급처명 `supplierName` / 배송지 `shipTo…` | 거래처 테이블을 만들지 않는다 (화주 도입 후에는 화주의 거래처라서) |
| 입고예정 (코드에서) | purchase order | 말로는 "입고예정"도 쓰지만 코드는 하나로 |

## 5. 에러 코드 접두

| 접두 | 도메인 |
|---|---|
| `PRODUCT_` | 품목 |
| `LOCATION_` | 로케이션 |
| `PO_` | 발주·검수·적치·입고확정 |
| `STOCK_` | 재고 |
| `ORDER_` | 주문 |
| `DO_` | 출고지시·할당·피킹·출고확정 |

## 6. 아직 도입하지 않은 용어 (예약)

도입하는 날 위 표로 옮기고 여기서 지운다.

| 한글 | 영문 | 도입 시점 | 메모 |
|---|---|---|---|
| 화주 | tenant | 화주 도입 시 | 창고에 물건을 맡긴 회사. 거래처와 다르다 |
| 출고요청 | outbound request | Portal 도입 시 | 화주가 Portal에서 보내는 요청. WMS 안에서는 주문으로 들어온다 |
| 입고요청 | inbound request | Portal 도입 시 | 화주가 보내는 입고예정. WMS 안에서는 발주로 들어온다 |
| 부분출고 | partial shipment | 2차 | 결품이 있어도 피킹된 수량만 출고 |

## 7. 화면 용어

화면은 2주차에 만든다. 라우트는 `/wms/{복수명사}` (예: `/wms/purchase-orders`), 컴포넌트는 `{엔티티}ListPage`, `{엔티티}DetailPage`로 통일한다.
