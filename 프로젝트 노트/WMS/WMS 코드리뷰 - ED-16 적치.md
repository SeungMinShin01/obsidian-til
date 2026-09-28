---
출처: Claude 분석
원본: 코드리뷰 세션 (claude.ai 프로젝트 「미니프로젝트」)
작성일: 2026-09-28
tags: [프로젝트, java]
---

> 상위: [[KDT_1차 정규프로젝트 MOC]]

# WMS 코드리뷰 - ED-16 적치

## ED-16 적치 1건 — 조현우

### 한 줄 요약

재고를 찾고 더하거나 새로 만드는 흐름은 같다. 차이는 **검증 3개(취소 문서, 중복 적치, 비활성 칸)의 유무**와 **저장 방식(더티 체킹 vs save)** 이다. 팀장 코드는 같은 검수 결과를 두 번 적치하면 재고가 두 배로 늘어난다.

### 코드

**팀장**

```java
public boolean putaway(PutawayDto putawayDto) {
    Optional<DocumentItemDetailEntity> optional = detailRepository.findById(putawayDto.getDetailId());
    if (optional.isPresent()) {
        DocumentItemDetailEntity detailEntity = optional.get();

        Optional<LocationEntity> optional2 = locationRepository.findById(putawayDto.getLocationId());
        if (optional2.isPresent()) {
            LocationEntity locationEntity = optional2.get();

            StockEntity stockEntity = null;
            for (StockEntity stock : stockRepository.findAll()) {
                if (stock.getLotEntity().getLotId().equals(detailEntity.getLotEntity().getLotId())
                        && stock.getLocationEntity().getLocationId().equals(locationEntity.getLocationId())) {
                    stockEntity = stock;
                }
            }
            if (stockEntity == null) {
                stockEntity = StockEntity.builder()
                        .lotEntity(detailEntity.getLotEntity())
                        .locationEntity(locationEntity)
                        .qty(detailEntity.getQty())
                        .build();
            } else {
                stockEntity.setQty(stockEntity.getQty() + detailEntity.getQty());
            }
            StockEntity savedEntity = stockRepository.save(stockEntity);

            detailEntity.setLocationEntity(locationEntity);
            detailEntity.setStockEntity(savedEntity);
            detailRepository.save(detailEntity);
            return true;
        }
    }
    return false;
}
```

**팀원**

```java
public boolean carry(CarryingDto carryingDto) {
    DocumentItemDetailEntity detailEntity = documentItemDetailRepository.findById(carryingDto.getDetailId()).orElse(null);
    if (detailEntity == null) return false;

    String status = detailEntity.getDocumentItemEntity().getDocumentEntity().getStatus();
    if (status.equals("CANCELED")) return false;                   // 취소 문서 차단

    if (detailEntity.getLocationEntity() != null) return false;     // 중복 적치 차단

    LocationEntity locationEntity = locationRepository.findById(carryingDto.getLocationId()).orElse(null);
    if (locationEntity == null || !locationEntity.getIsActive()) return false;  // 비활성 칸 차단

    StockEntity stockEntity = null;
    for (StockEntity s : stockRepository.findAll()) {
        if (s.getLotEntity().getLotId().equals(detailEntity.getLotEntity().getLotId())
                && s.getLocationEntity().getLocationId().equals(locationEntity.getLocationId())) {
            stockEntity = s;
            break;
        }
    }
    if (stockEntity != null) {
        stockEntity.setQty(stockEntity.getQty() + detailEntity.getQty());   // save 없음 → 더티 체킹
    } else {
        stockEntity = StockEntity.builder()
                .lotEntity(detailEntity.getLotEntity())
                .locationEntity(locationEntity)
                .qty(detailEntity.getQty())
                .build();
        stockEntity = stockRepository.save(stockEntity);
    }

    detailEntity.setLocationEntity(locationEntity);                  // save 없음 → 더티 체킹
    detailEntity.setStockEntity(stockEntity);
    return true;
}
```

### 메서드 단위

```
IN  : CarryingDto / PutawayDto (detailId, locationId)
      + DB의 검수 결과 1건, 칸 1개, 재고 전체
  ↓ ① 검수 결과(detail) 조회        없으면 false
  ↓ ② [팀원만] 문서 CANCELED 확인    취소면 false
  ↓ ③ [팀원만] 이미 적치됐는지 확인   location이 있으면 false
  ↓ ④ 칸 조회                       없으면 false (+ [팀원만] 비활성이면 false)
  ↓ ⑤ 같은 lot + 같은 칸 재고 찾기    findAll 후 for문
  ↓ ⑥ 있으면 qty 더함 / 없으면 새 재고 생성
  ↓ ⑦ detail에 칸·재고 연결
OUT : boolean (성공 true / 실패 false)
      부수효과: stock 1행 INSERT 또는 UPDATE, detail 1행 UPDATE
```

### 무엇이 다른가

**전체 비교**

| | 팀원 (carry) | 팀장 (putaway) |
|---|---|---|
| 검증 | detail·칸 존재 + 취소 문서 + 중복 적치 + 비활성 칸 | detail·칸 존재 여부만 |
| Optional 처리 | `orElse(null)` + 바로 return (가드 절) | `isPresent()` + if 중첩 |
| 재고 찾기 | 첫 번째로 일치하면 `break` | 끝까지 돌고 마지막 일치 값을 씀 |
| 저장 | 새 재고만 `save`, 나머지는 더티 체킹 | 재고, detail 모두 `save` |
| 이름 | `carry`, `CarryingDto` | `putaway`, `PutawayDto` (용어사전과 일치) |

#### ① 검증: 가장 큰 차이

- 팀원: 취소 문서, 이미 적치된 detail, 비활성 칸을 막는다.
- 팀장: detail과 칸이 존재하는지만 본다.
- 팀장 코드에서 같은 detail로 두 번 요청하면 **재고 qty가 두 번 더해진다.** 실제 물건은 한 번 올렸는데 재고는 두 배가 된다.
- 취소된 입고의 물건이 재고가 되거나, 쓰지 않는 칸에 재고가 생기는 것도 막지 못한다.

#### ② Optional 처리: 가드 절 vs if 중첩

- 팀원: 조건이 안 맞으면 바로 `return false` → 본 로직은 들여쓰기 없이 아래로 쭉 읽힌다.
- 팀장: `if (isPresent())` 안에 다시 `if (isPresent())` → 조건이 늘수록 들여쓰기가 깊어진다.
- 동작은 같다. 하지만 팀장 구조에 검증 3개를 추가하면 if가 5단까지 들어간다. 팀원 코드에 검증이 더 많은 건 구조가 추가하기 쉬웠던 영향도 있다.

#### ③ 재고 찾기: break 유무

- 팀원: 처음 일치한 재고에서 멈춘다.
- 팀장: 끝까지 돌며 일치할 때마다 덮어써서 **마지막** 일치 값을 쓴다.
- "같은 lot + 같은 칸 = 1행" 규칙이 지켜지면 결과는 같다. 그런데 v1 스키마에 `UNIQUE(lot_id, location_id)`가 없어서, 중복 행이 생기면 두 코드가 **서로 다른 행**에 수량을 더한다.

#### ④ 저장 방식: 더티 체킹 vs save

- 팀원: 이미 있는 재고와 detail은 setter만 호출하고 save하지 않는다. `@Transactional` 안이라면 커밋할 때 JPA가 변경을 감지해 UPDATE한다(더티 체킹).
- 팀장: 매번 `save`를 호출한다. 트랜잭션 안이라면 불필요한 호출이지만 동작에 문제는 없다.
- **`@Transactional`이 없으면 결과가 갈린다.** 팀원 코드는 수량 증가와 detail 연결이 DB에 반영되지 않고, 팀장 코드는 반영된다. 메서드나 클래스에 붙어 있는지 확인 필요.

### 각자 놓친 것

- **팀장**: 검증이 없어서 중복 적치 시 재고가 부풀고, 취소 문서와 비활성 칸도 통과한다. if 중첩이라 검증을 추가하기 어려운 구조다.
- **팀원**: 더티 체킹에 의존하므로 `@Transactional`이 필수다. 이름이 용어사전(적치 = putaway)과 다르다(`carry`, "적재").
- **둘 다**: 실패 이유가 모두 `false` 하나다. 호출하는 쪽에서 "없는 detail(404)"인지 "이미 적치됨(409)"인지 구분할 수 없다. 예외와 에러 코드로 바꾸는 게 API 명세 규칙에 맞다.
- **둘 다**: 재고를 찾으려고 `findAll()`로 전체를 가져온다. `stockRepository.findByLotEntityAndLocationEntity(lot, location)`로 1건만 조회할 수 있다.
- **둘 다**: 동시에 같은 요청이 두 번 들어오면 둘 다 검증을 통과해서 중복 적치나 중복 재고 행이 생길 수 있다. `UNIQUE(lot_id, location_id)` 제약과 락이 필요하다(성능·동시성 측정 주제).

---

## 개념 간단 정리

### 1. `Optional.orElse(null)` vs `isPresent()` + `get()`

```java
Entity e = repository.findById(id).orElse(null);       // 없으면 null
if (e == null) return false;

Optional<Entity> opt = repository.findById(id);        // 있는지 먼저 물어봄
if (opt.isPresent()) { Entity e = opt.get(); ... }
```

- 둘 다 "값이 없을 때"를 처리하는 방법이고 결과는 같다.
- 실패 시 예외를 던질 거라면 `orElseThrow(() -> new NotFoundException(...))` 한 줄로 끝난다.

### 2. 가드 절 (Guard Clause)

- 조건이 안 맞으면 **먼저 return해서 빠져나가는** 방식.
- 본 로직이 if 안으로 들어가지 않아 들여쓰기가 얕고, 검증을 위에 한 줄씩 추가하기 쉽다.

### 3. `break`

- for문을 즉시 끝낸다. 찾는 값이 하나뿐이라면 찾은 뒤 나머지를 돌 필요가 없다.
- 없으면 끝까지 돌면서 조건에 맞는 **마지막** 값이 남는다.

### 4. 더티 체킹 (Dirty Checking)

- 트랜잭션 안에서 조회한 엔티티(영속 상태)는 JPA가 처음 값을 기억해 둔다.
- 커밋 시점에 현재 값과 비교해서 바뀐 필드가 있으면 **save 없이도 UPDATE**를 날린다.
- 조건: `@Transactional` 안이어야 한다. 트랜잭션 밖에서 setter만 호출하면 DB에 반영되지 않는다.
- 새로 만든 엔티티(`builder().build()`)는 JPA가 모르는 객체라서 `save`로 등록해야 INSERT된다.

## 관련 노트

[[KDT_1차 정규프로젝트 MOC]]
