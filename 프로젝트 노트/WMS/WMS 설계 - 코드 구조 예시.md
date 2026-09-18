---
출처: Claude 분석
원본: claude.ai 프로젝트 「미니프로젝트」 WMS/코드_구조_예시.md
작성일: 2026-09-18
tags: [프로젝트, spring]
---

> 상위: [[KDT1차 정규프로젝트 MOC]]

# 코드 구조와 예시 — 주말 MVP (단일 WMS)

> 팀 규칙 `02_코드컨벤션_백엔드.md`의 패키지 구조(도메인 = 폴더 = 담당자)를 따른다.
> 루트 패키지는 `com.team.wms`로 가정한다. 스택: Java 21, Spring Boot 3.x, Spring Data JPA, Lombok.
> 상태 전이 규칙은 나중에 넣는다. 지금은 **enum 값 + 행동 메서드 + `transitionTo()` 한 곳**까지만 만든다.

---

## 1. 만들어질 파일 전체

`(S0)` 주말, `(S1)` 이후 스프린트. 담당 표기: ① 출고 · ② 나 · ③ 재고 · ④ 입고

```
wms/
├── build.gradle
├── settings.gradle
├── docker-compose.yml                                   ② (S0) MySQL 8
├── CLAUDE.md                                            ② (S0) 팀 공용 AI 프롬프트
├── .github/workflows/ci.yml                             ② (S1)
│
└── src/
    ├── main/
    │   ├── java/com/team/wms/
    │   │   ├── WmsApplication.java
    │   │   │
    │   │   ├── global/                                  ② (S0) 토 10시까지
    │   │   │   ├── config/
    │   │   │   │   ├── JpaAuditingConfig.java           @EnableJpaAuditing
    │   │   │   │   ├── SecurityConfig.java              주말: permitAll
    │   │   │   │   └── SwaggerConfig.java
    │   │   │   ├── entity/
    │   │   │   │   └── BaseEntity.java                  createdAt, updatedAt
    │   │   │   ├── response/
    │   │   │   │   ├── ApiResponse.java                 {success, data, message, code}
    │   │   │   │   └── PageResponse.java                {content, page, size, totalElements, totalPages}
    │   │   │   ├── exception/
    │   │   │   │   ├── ErrorCode.java                   PO_001, STOCK_001 … (HTTP 상태 + 메시지)
    │   │   │   │   ├── BusinessException.java
    │   │   │   │   └── GlobalExceptionHandler.java
    │   │   │   └── util/
    │   │   │       └── DocumentNoGenerator.java         PO-/ORD-/DO-{yyyyMMdd}-{3자리}
    │   │   │
    │   │   └── domain/
    │   │       ├── warehouse/                           ② (S0) 창고·구역·로케이션 조회
    │   │       │   ├── controller/LocationController.java     GET /warehouses, /zones, /locations
    │   │       │   ├── service/LocationService.java
    │   │       │   ├── repository/WarehouseRepository.java
    │   │       │   ├── repository/ZoneRepository.java
    │   │       │   ├── repository/LocationRepository.java     findByLocationCode
    │   │       │   ├── entity/Warehouse.java
    │   │       │   ├── entity/Zone.java
    │   │       │   ├── entity/Location.java
    │   │       │   └── dto/WarehouseResponse.java, ZoneResponse.java, LocationResponse.java
    │   │       │
    │   │       ├── product/                             ② (S0)
    │   │       │   ├── controller/ProductController.java
    │   │       │   ├── service/ProductService.java
    │   │       │   ├── repository/ProductRepository.java      findByProductCode
    │   │       │   ├── entity/Product.java
    │   │       │   └── dto/ProductCreateRequest.java, ProductResponse.java
    │   │       │
    │   │       ├── stock/                               ③ (S0) 재고를 바꾸는 유일한 창구
    │   │       │   ├── controller/StockController.java        GET /stocks, /stocks/summary
    │   │       │   ├── controller/StockHistoryController.java GET /stock-histories
    │   │       │   ├── service/StockService.java              receive / findAllocatable / allocate / ship
    │   │       │   ├── service/StockQueryService.java         조회 전용
    │   │       │   ├── repository/StockRepository.java        findAllocatable (JPQL)
    │   │       │   ├── repository/StockHistoryRepository.java
    │   │       │   ├── entity/Stock.java
    │   │       │   ├── entity/StockHistory.java
    │   │       │   ├── entity/StockTxType.java                enum
    │   │       │   ├── entity/RefType.java                    enum
    │   │       │   └── dto/StockResponse.java, StockSummaryResponse.java, StockHistoryResponse.java
    │   │       │
    │   │       ├── purchaseorder/                       ④ (S0) 발주·검수·적치·입고확정
    │   │       │   ├── controller/PurchaseOrderController.java
    │   │       │   ├── service/PurchaseOrderService.java
    │   │       │   ├── repository/PurchaseOrderRepository.java
    │   │       │   ├── repository/PurchaseOrderItemRepository.java
    │   │       │   ├── repository/InspectionRepository.java
    │   │       │   ├── repository/PutawayRepository.java
    │   │       │   ├── entity/PurchaseOrder.java
    │   │       │   ├── entity/PurchaseOrderItem.java
    │   │       │   ├── entity/Inspection.java
    │   │       │   ├── entity/Putaway.java
    │   │       │   ├── entity/PurchaseOrderStatus.java        enum
    │   │       │   ├── entity/RejectReason.java               enum
    │   │       │   ├── entity/VarianceReason.java             enum
    │   │       │   └── dto/
    │   │       │       ├── PurchaseOrderCreateRequest.java
    │   │       │       ├── PurchaseOrderResponse.java
    │   │       │       ├── PurchaseOrderListResponse.java
    │   │       │       ├── InspectionSaveRequest.java
    │   │       │       └── PutawaySaveRequest.java
    │   │       │
    │   │       ├── order/                               ① (S0) 주문
    │   │       │   ├── controller/OrderController.java
    │   │       │   ├── service/OrderService.java
    │   │       │   ├── repository/OrderRepository.java        findByDeliveryOrderId
    │   │       │   ├── repository/OrderItemRepository.java
    │   │       │   ├── entity/Order.java                      @Table(name = "orders")
    │   │       │   ├── entity/OrderItem.java
    │   │       │   ├── entity/OrderStatus.java                enum
    │   │       │   └── dto/OrderCreateRequest.java, OrderResponse.java, OrderListResponse.java
    │   │       │
    │   │       ├── deliveryorder/                       ① (S0) 출고지시·FEFO 할당·피킹·출고확정
    │   │       │   ├── controller/DeliveryOrderController.java
    │   │       │   ├── controller/AllocationController.java   PATCH /allocations/{id}/pick
    │   │       │   ├── service/DeliveryOrderService.java
    │   │       │   ├── service/FefoAllocationPlanner.java     DB 없이 도는 순수 자바
    │   │       │   ├── service/AllocationPlan.java
    │   │       │   ├── repository/DeliveryOrderRepository.java
    │   │       │   ├── repository/DeliveryOrderItemRepository.java
    │   │       │   ├── repository/AllocationRepository.java
    │   │       │   ├── entity/DeliveryOrder.java
    │   │       │   ├── entity/DeliveryOrderItem.java
    │   │       │   ├── entity/Allocation.java
    │   │       │   ├── entity/DeliveryOrderStatus.java        enum
    │   │       │   ├── entity/AllocationStatus.java           enum
    │   │       │   └── dto/
    │   │       │       ├── DeliveryOrderCreateRequest.java    {orderIds}
    │   │       │       ├── DeliveryOrderResponse.java
    │   │       │       ├── AllocationResponse.java
    │   │       │       ├── PickListResponse.java
    │   │       │       ├── PickRequest.java                   {pickedQty}
    │   │       │       └── ShortageResponse.java              할당 실패 시 부족 수량
    │   │       │
    │   │       └── user/                                ③ (S1) 로그인·작업자 계정
    │   │           ├── controller/AuthController.java, UserController.java
    │   │           ├── service/AuthService.java, UserService.java
    │   │           ├── repository/UserRepository.java
    │   │           ├── entity/User.java                       @Table(name = "users")
    │   │           ├── entity/UserRole.java                   enum
    │   │           └── dto/LoginRequest.java, LoginResponse.java, UserCreateRequest.java, UserResponse.java
    │   │
    │   └── resources/
    │       ├── application.yml
    │       ├── application-local.yml
    │       └── db/
    │           ├── migration/
    │           │   ├── V1__init_schema.sql              (프로젝트 WMS/sql/)
    │           │   └── V2__seed_master.sql
    │           └── sample/
    │               └── sample_data.sql                  수동 실행 전용 (Flyway 경로 밖)
    │
    └── test/java/com/team/wms/
        ├── domain/deliveryorder/service/FefoAllocationPlannerTest.java   ① (S0)
        ├── domain/stock/service/StockServiceTest.java                   ③ (S0)
        └── scenario/InboundOutboundScenarioTest.java                    ② (S1) 13단계 자동화
```

**enum은 토요일 오전에 먼저 push한다** (값만, 전이 규칙 없음): `PurchaseOrderStatus`, `OrderStatus`, `DeliveryOrderStatus`, `AllocationStatus`, `StockTxType`, `RefType`, `RejectReason`, `VarianceReason`, `UserRole`.

---

## 2. 예시: 발주 등록 + 입고확정 (④)

다른 도메인도 이 모양을 그대로 따른다.

### 2.1 공통 — `BaseEntity`, `ApiResponse`, `ErrorCode` (② 작성)

```java
@Getter
@MappedSuperclass
@EntityListeners(AuditingEntityListener.class)
public abstract class BaseEntity {
    @CreatedDate
    @Column(nullable = false, updatable = false)
    private LocalDateTime createdAt;

    @LastModifiedDate
    @Column(nullable = false)
    private LocalDateTime updatedAt;
}
```

```java
public record ApiResponse<T>(boolean success, T data, String message, String code) {
    public static <T> ApiResponse<T> success(T data) {
        return new ApiResponse<>(true, data, null, null);
    }
    public static ApiResponse<Void> fail(ErrorCode e) {
        return new ApiResponse<>(false, null, e.getMessage(), e.name());
    }
}
```

```java
@Getter
@RequiredArgsConstructor
public enum ErrorCode {
    PRODUCT_001(HttpStatus.BAD_REQUEST, "존재하지 않는 품목입니다"),
    LOCATION_001(HttpStatus.BAD_REQUEST, "존재하지 않는 로케이션입니다"),
    PO_001(HttpStatus.CONFLICT, "현재 상태에서는 처리할 수 없습니다"),
    PO_002(HttpStatus.BAD_REQUEST, "검수 합계가 예정수량을 초과합니다"),
    PO_004(HttpStatus.BAD_REQUEST, "적치 수량 합계가 정상수량과 다릅니다"),
    PO_NOT_FOUND(HttpStatus.NOT_FOUND, "존재하지 않는 발주입니다"),
    STOCK_001(HttpStatus.CONFLICT, "가용재고가 부족합니다");

    private final HttpStatus status;
    private final String message;
}
```

### 2.2 Enum — 값만 (전이 규칙은 나중에)

```java
package com.team.wms.domain.purchaseorder.entity;

public enum PurchaseOrderStatus {
    REGISTERED,   // 발주등록 (= 입고예정)
    INSPECTING,   // 검수중
    PUTAWAY,      // 적치중
    COMPLETED,    // 입고완료
    CANCELED      // 취소

    // TODO(나): nextStates() / canMoveTo() 추가 예정 — 테이블_설계_근거 §5.3
}
```

### 2.3 Entity

```java
@Entity
@Table(name = "purchase_order")
@Getter
@NoArgsConstructor(access = AccessLevel.PROTECTED)          // JPA용 기본 생성자, 외부에서 new 금지
public class PurchaseOrder extends BaseEntity {

    @Id @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false, unique = true, length = 30)
    private String poNo;

    @Column(nullable = false, length = 100)
    private String supplierName;

    @Column(nullable = false)
    private LocalDate expectedDate;

    @Enumerated(EnumType.STRING)                              // 반드시 STRING
    @Column(nullable = false, length = 20)
    private PurchaseOrderStatus status;

    private String remark;
    private LocalDateTime completedAt;

    // 생성은 정적 팩토리 하나로 (팀 규칙: @Builder 또는 정적 팩토리 중 하나)
    public static PurchaseOrder create(String poNo, String supplierName, LocalDate expectedDate, String remark) {
        PurchaseOrder po = new PurchaseOrder();
        po.poNo = poNo;
        po.supplierName = supplierName;
        po.expectedDate = expectedDate;
        po.remark = remark;
        po.status = PurchaseOrderStatus.REGISTERED;
        return po;
    }

    // ── 행동 메서드: 상태는 여기서만 바뀐다 (@Setter 금지) ──
    public void startInspection() { transitionTo(PurchaseOrderStatus.INSPECTING); }
    public void planPutaway()     { transitionTo(PurchaseOrderStatus.PUTAWAY); }
    public void cancel()          { transitionTo(PurchaseOrderStatus.CANCELED); }

    public void confirm() {
        transitionTo(PurchaseOrderStatus.COMPLETED);
        this.completedAt = LocalDateTime.now();
    }

    private void transitionTo(PurchaseOrderStatus next) {
        // TODO(나): if (!status.canMoveTo(next)) throw new BusinessException(ErrorCode.PO_001);
        this.status = next;
    }
}
```

```java
@Entity
@Table(name = "purchase_order_item")
@Getter
@NoArgsConstructor(access = AccessLevel.PROTECTED)
public class PurchaseOrderItem extends BaseEntity {

    @Id @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @ManyToOne(fetch = FetchType.LAZY, optional = false)      // FK 쪽에만 연관관계 (단방향)
    @JoinColumn(name = "purchase_order_id")
    private PurchaseOrder purchaseOrder;

    @ManyToOne(fetch = FetchType.LAZY, optional = false)
    @JoinColumn(name = "product_id")
    private Product product;

    @Column(nullable = false)
    private int expectedQty;

    @Enumerated(EnumType.STRING)
    private VarianceReason varianceReason;

    public static PurchaseOrderItem create(PurchaseOrder po, Product product, int expectedQty) {
        PurchaseOrderItem item = new PurchaseOrderItem();
        item.purchaseOrder = po;
        item.product = product;
        item.expectedQty = expectedQty;
        return item;
    }
}
```
`PurchaseOrder`에는 `@OneToMany items`를 두지 않는다. 품목은 `purchaseOrderItemRepository.findByPurchaseOrderId()`로 찾는다.

### 2.4 Repository

```java
public interface PurchaseOrderRepository extends JpaRepository<PurchaseOrder, Long> {
    Page<PurchaseOrder> findByStatus(PurchaseOrderStatus status, Pageable pageable);
}

public interface PurchaseOrderItemRepository extends JpaRepository<PurchaseOrderItem, Long> {
    List<PurchaseOrderItem> findByPurchaseOrderId(Long purchaseOrderId);
}

public interface InspectionRepository extends JpaRepository<Inspection, Long> {
    @Query("select i from Inspection i where i.purchaseOrderItem.purchaseOrder.id = :purchaseOrderId")
    List<Inspection> findAllByPurchaseOrderId(@Param("purchaseOrderId") Long purchaseOrderId);
}

public interface PutawayRepository extends JpaRepository<Putaway, Long> {
    // 입고확정 때 이 발주의 적치 지정을 한 번에 가져온다 (검수 → 발주 품목까지 함께)
    @Query("""
        select p from Putaway p
          join fetch p.inspection i
          join fetch i.purchaseOrderItem it
          join fetch p.location
         where it.purchaseOrder.id = :purchaseOrderId
        """)
    List<Putaway> findAllByPurchaseOrderId(@Param("purchaseOrderId") Long purchaseOrderId);
}
```

### 2.5 DTO

```java
public record PurchaseOrderCreateRequest(
        @NotBlank String supplierName,
        @NotNull LocalDate expectedDate,
        String remark,
        @NotEmpty @Valid List<Item> items
) {
    public record Item(@NotBlank String productCode, @Min(1) int expectedQty) {}

    // toEntity는 자기 필드만. 품목(Product) 조회는 서비스에서
    public PurchaseOrder toEntity(String poNo) {
        return PurchaseOrder.create(poNo, supplierName, expectedDate, remark);
    }
}
```

```java
public record PurchaseOrderResponse(
        Long id, String poNo, String supplierName, LocalDate expectedDate,
        PurchaseOrderStatus status, List<ItemResponse> items
) {
    public record ItemResponse(Long itemId, String productCode, String productName, int expectedQty) {
        static ItemResponse from(PurchaseOrderItem item) {
            return new ItemResponse(item.getId(), item.getProduct().getProductCode(),
                    item.getProduct().getProductName(), item.getExpectedQty());
        }
    }

    public static PurchaseOrderResponse from(PurchaseOrder po, List<PurchaseOrderItem> items) {
        return new PurchaseOrderResponse(po.getId(), po.getPoNo(), po.getSupplierName(),
                po.getExpectedDate(), po.getStatus(),
                items.stream().map(ItemResponse::from).toList());
    }
}
```

### 2.6 Service

```java
@Service
@RequiredArgsConstructor
@Transactional(readOnly = true)                               // 클래스는 읽기 전용
public class PurchaseOrderService {

    private final PurchaseOrderRepository purchaseOrderRepository;
    private final PurchaseOrderItemRepository purchaseOrderItemRepository;
    private final InspectionRepository inspectionRepository;
    private final PutawayRepository putawayRepository;
    private final ProductRepository productRepository;
    private final StockService stockService;                  // ③의 창구. stock 테이블 직접 수정 금지
    private final DocumentNoGenerator documentNoGenerator;

    @Transactional                                            // 쓰기 메서드에만
    public PurchaseOrderResponse createPurchaseOrder(PurchaseOrderCreateRequest request) {
        PurchaseOrder po = purchaseOrderRepository.save(request.toEntity(documentNoGenerator.next("PO")));

        List<PurchaseOrderItem> items = request.items().stream()
                .map(i -> {
                    Product product = productRepository.findByProductCode(i.productCode())
                            .orElseThrow(() -> new BusinessException(ErrorCode.PRODUCT_001));
                    return purchaseOrderItemRepository.save(PurchaseOrderItem.create(po, product, i.expectedQty()));
                })
                .toList();

        return PurchaseOrderResponse.from(po, items);
    }

    @Transactional
    public PurchaseOrderResponse confirm(Long id) {
        PurchaseOrder po = purchaseOrderRepository.findById(id)
                .orElseThrow(() -> new BusinessException(ErrorCode.PO_NOT_FOUND));

        // ① 검증: 검수 행마다 적치 합계 = 정상수량
        List<Putaway> putaways = putawayRepository.findAllByPurchaseOrderId(id);
        Map<Long, Integer> putawaySum = putaways.stream().collect(
                Collectors.groupingBy(p -> p.getInspection().getId(), Collectors.summingInt(Putaway::getQty)));
        for (Inspection insp : inspectionRepository.findAllByPurchaseOrderId(id)) {
            if (putawaySum.getOrDefault(insp.getId(), 0) != insp.getGoodQty()) {
                throw new BusinessException(ErrorCode.PO_004);
            }
        }

        // ② 상태 변경 (나중에 여기서 전이 규칙 검사가 걸린다)
        po.confirm();                                         // save() 없음 — 변경 감지로 UPDATE

        // ③ 부수 효과: 적치 지정대로 재고 생성 + INBOUND 이력 (③의 StockService)
        for (Putaway p : putaways) {
            Inspection insp = p.getInspection();
            stockService.receive(
                    insp.getPurchaseOrderItem().getProduct().getId(),
                    p.getLocation().getId(),
                    insp.getExpiryDate(),
                    p.getQty(),
                    po.getId());
        }
        // 중간에 예외가 나면 ②의 상태 변경까지 전부 롤백된다

        return PurchaseOrderResponse.from(po, purchaseOrderItemRepository.findByPurchaseOrderId(id));
    }
}
```

### 2.7 Controller

```java
@Tag(name = "발주", description = "발주 등록·검수·적치·입고확정")
@RestController
@RequestMapping("/api/v1/purchase-orders")
@RequiredArgsConstructor
public class PurchaseOrderController {

    private final PurchaseOrderService purchaseOrderService;

    @Operation(summary = "발주 등록")
    @PostMapping
    public ResponseEntity<ApiResponse<PurchaseOrderResponse>> createPurchaseOrder(
            @Valid @RequestBody PurchaseOrderCreateRequest request) {
        return ResponseEntity.status(HttpStatus.CREATED)
                .body(ApiResponse.success(purchaseOrderService.createPurchaseOrder(request)));
    }

    @Operation(summary = "입고확정 — 적치 지정대로 재고 생성")
    @PatchMapping("/{id}/confirm")                            // 행동마다 API. PATCH /status 같은 범용 API 금지
    public ApiResponse<PurchaseOrderResponse> confirm(@PathVariable Long id) {
        return ApiResponse.success(purchaseOrderService.confirm(id));
    }
}
```

컨트롤러에는 로직이 없다: 검증(`@Valid`) → 서비스 호출 → `ApiResponse`로 감싸기.

---

## 3. 주말 규칙 요약 (전원)

| 해도 됨 | 하지 않음 |
|---|---|
| enum은 값만 | 상태를 문자열로 저장 |
| 행동 메서드 안에서 `transitionTo()`로 상태 변경 (검사는 TODO) | `@Setter`, `setStatus()`, `PATCH …/status` |
| 변경 감지로 UPDATE | `@Modifying @Query("update … set status")` |
| 앞 단계 데이터는 `sample_data.sql`로 채워서 테스트 | stock 테이블을 `StockService` 밖에서 수정 |
| `@ManyToOne(LAZY)` 단방향 | 부모에 `@OneToMany` |
