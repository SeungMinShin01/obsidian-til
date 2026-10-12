---
출처: Claude 분석
원본: 코드리뷰 세션 (claude.ai 프로젝트 「미니프로젝트」)
작성일: 2026-09-28
tags: [프로젝트, java]
---

> 상위: [[KDT_1차 정규프로젝트 MOC]]

# WMS 코드리뷰 - 생각해 볼 것 답변

코드리뷰 노트마다 달아 둔 "생각해 볼 것" 질문에 대한 답. 근거는 V1 스키마, 검수→출고 MVP 명세, ADR 초안이다.

## 1. 검수 등록 (inspectionSave) — 9/28 추가분

**팀장** (검증 없음)

```java
public Integer inspectionSave(InspectionDto inspectionDto) {
    DocumentItemEntity documentItemEntity = documentItemRepository.findById(inspectionDto.getDocumentItemId()).orElse(null);
    DocumentItemDetailEntity detailEntity = inspectionDto.toEntity(documentItemEntity);
    DocumentItemDetailEntity savedEntity = detailRepository.save(detailEntity);
    return savedEntity.getDetailId();
}
```

**팀원**

```java
public Integer inspectionSave(InspectionDto inspectionDto) {
    if (inspectionDto.getQty() == null || inspectionDto.getQty() <= 0) return null;
    DocumentItemEntity documentItemEntity = documentItemRepository.findById(inspectionDto.getDocumentItemId()).orElse(null);
    if (documentItemEntity == null) return null;
    if (!documentItemEntity.getDocumentEntity().getType().equals("INBOUND")) return null;
    if (!documentItemEntity.getDocumentEntity().getStatus().equals("WAITING")) return null;
    DocumentItemDetailEntity detailEntity = inspectionDto.toEntity(documentItemEntity);
    DocumentItemDetailEntity savedEntity = documentItemDetailRepository.save(detailEntity);
    return savedEntity.getDetailId();
}
```

### Q1. 팀장 코드에 없는 ID를 넣으면 어디서 무슨 에러가 나나?

- `findById`는 에러를 내지 않는다. 빈 Optional이 오고 `orElse(null)` 때문에 `documentItemEntity`가 조용히 null이 된다.
- null이 `toEntity(null)`로 넘어가 `document_item_id`가 빈 detail이 만들어지고, `save`에서 터진다. 스키마상 `document_item_id`가 NOT NULL이라 DB가 거부하고 `DataIntegrityViolationException`이 올라온다. `toEntity` 안에서 `documentItemEntity.getXxx()`를 호출한다면 그보다 먼저 NPE가 난다.
- 전역 핸들러를 거치면 응답은 **409 `DATA_CONSTRAINT_VIOLATION`**. 명세상 맞는 응답은 **404 `DOCUMENT_ITEM_NOT_FOUND`** 라서, 원인과 다른 에러가 나간다.
- (스프린트 1 회고 5장과 대조 필요)

### Q2. A안(첫 검수 저장 → `INSPECTED`)이면 품목 줄이 2개인 문서는?

- 1번 줄 검수 → 문서 `INSPECTED` → 2번 줄은 `status != WAITING`에 걸려 `null`. **두 번째 줄은 검수할 수 없다.**
- 품목 1줄이라도 LOT 2개를 나눠 저장하면 두 번째에서 똑같이 막힌다. 명세 S-2 완료 조건("한 품목에 LOT 2개 이상 등록 가능")과 충돌한다.
- A안으로 가면 검사 조건을 "`WAITING` 또는 `INSPECTED`"(적치 시작 전까지)로 넓혀야 한다.

### Q3. 네 가지 실패가 전부 `null`이다. 화면은 무엇을 알고 무엇을 모르나?

- 아는 것: "실패했다"는 사실 하나. 컨트롤러가 null을 200으로 그대로 내보내면 성공으로 오해할 수도 있다.
- 모르는 것: 이유. 원래는 수량 오류(400) / 없는 품목(404) / 입고 문서 아님(400) / 상태 위반(409)으로 서로 다른 응답이어야 한다.
- 그래서 화면은 "수량을 고치세요"인지 "새로고침하세요"인지 안내할 수 없다. `BusinessException(ErrorCode)`로 바꾸면 해결된다.

## 2. ED-10 입고 문서 목록 정렬

### Q1. 두 코드의 결과가 항상 같은가? 예정일이 같은 문서 둘이 있으면?

- 예정일이 모두 다르면 같다.
- 예정일이 같은 문서가 있으면 달라질 수 있다. `[A(10), B(10), C(5)]` → 팀장 `[C, B, A]`, 팀원 `[C, A, B]` (직접 실행해 확인).

### Q2. `compareTo`의 음수/0/양수가 어떻게 정렬 순서가 되나?

- 정렬 알고리즘은 두 원소를 고를 때마다 비교 함수를 호출하고 부호만 본다. 음수면 a가 앞, 양수면 b가 앞, 0이면 같음.
- `a.compareTo(b)`면 이른 날짜가 앞 → 오름차순. `b.compareTo(a)`로 뒤집으면 내림차순.

### Q3. 문서 1만 건이면 어느 쪽이 느린가? 왜?

- 팀장: n(n-1)/2 ≈ **5,000만 번** 비교.
- 팀원: n log n ≈ **13만 번** 비교. 약 400배 차이, 이미 정렬돼 있으면 약 1만 번으로 끝난다.
- 다만 두 코드 모두 `findAll()`로 1만 건을 전부 읽어 오는 비용은 똑같다.

## 3. ED-21 재고 조회 정렬

### Q1. `thenComparing(StockEntity::getStockId)`가 없으면 어떤 상황에서 문제가 되나?

- 소비기한이 같은 재고 두 줄의 순서가 `findAll()` 반환 순서에 맡겨진다. ORDER BY가 없으니 보장되지 않는다.
- MySQL은 대개 PK 순으로 돌려줘서 테스트는 보통 통과한다. 그래서 "첫 줄이 stockId 3" 같은 테스트는 데이터·실행 계획이 바뀌는 순간 **가끔만 깨진다.** 늘 깨지는 것보다 원인을 찾기 어렵다.

### Q2. `nullsLast` — 우리 스키마에서 소비기한 NULL이 생길 수 있나?

- 없다. `stock.lot_id`가 NOT NULL + FK, `lot.expiry_date`도 NOT NULL.
- DB에서 읽은 재고는 반드시 소비기한이 있다. `nullsLast`는 실행될 일 없는 방어 코드다.

### Q3. ADR의 FEFO 규칙("소비기한 → 입고일 → 가용 많은 칸")을 더 가깝게 구현한 건?

- 팀원이 조금 더 가깝지만 **둘 다 완전하지 않다.**
- 팀원의 2차 기준 `stockId`는 입고일의 대용품일 뿐이다. auto increment라 먼저 적치된 재고가 대체로 작은 번호지만, 입고일(`lot.created_at`) 자체는 아니다.
- 3차 기준 "가용 많은 칸"(`qty - allocated_qty` 내림차순)은 둘 다 없다.
- 참고: 프로젝트 ADR 초안에서는 FEFO가 ADR-003 번호로 되어 있다. 또 이 규칙은 원래 할당 순서 규칙이라, 조회 화면에도 그대로 적용할지는 따로 정할 문제다.

## 4. ED-16 적치 1건

### Q1. 팀원 코드에 `detailRepository.save`가 없는데 DB에 반영되나?

- 클래스나 메서드에 `@Transactional`이 있으면 반영된다. `findById`로 가져온 detail은 영속성 컨텍스트가 관리하는 엔티티라서, 커밋 시점에 바뀐 필드를 감지해 UPDATE를 보낸다(변경 감지, dirty checking).
- 없으면 반영되지 않는다. 새 stock만 `save`로 INSERT되고, 기존 재고 수량 증가와 detail의 칸·재고 연결은 사라진다.

### Q2. 팀원이 추가한 `return false` 네 개는 스토리에 있었나? 잘한 건가, 범위를 넘은 건가?

명세의 적재 스토리(v1 S-4, v2 S-12)로 대조했다. (ED-16 스토리 원문은 대조 필요)

- 없는 detail: v1 범위 (404 `DETAIL_NOT_FOUND`)
- 이미 적재됨 · 비활성 칸: v2 S-12 → 앞당겨 구현한 것
- 취소 문서: 어디에도 없다. 취소 API가 "다음 스프린트 후보"라 지금은 `CANCELED`가 만들어질 수 없어 실행될 일이 없는 코드다.

판단:

- **잘한 점**: 중복 적재 방어는 비용이 거의 없고 재고가 부풀어 오르는 걸 막는다.
- **범위를 넘은 점**: ADR-009는 1단계에서 검증 없이 문제를 먼저 겪자고 정했다. 또 `return false`로 넣은 검증은 v2에서 에러 코드로 다시 고쳐야 한다.

### Q3. `break` 유무로 결과가 달라지는 경우가 있나?

- 같은 lot + 같은 칸 재고가 **2행 이상일 때만** 달라진다. 팀원은 첫 행에, 팀장은 마지막 행에 수량을 더한다.
- 스키마에 `UNIQUE(lot_id, location_id)`가 없어서 동시 요청이 들어오면 중복 행이 실제로 생길 수 있다(ADR 초안에도 알려진 한계로 기록).
- 중복이 없으면 결과는 같고, 차이는 속도뿐이다.

### Q4. `findAll()`로 전체를 뒤진다. 재고 1만 건이면? 지금 고쳐야 하나, 남겨야 하나?

- 적재 1번마다 1만 개 엔티티를 메모리에 올리고, 커밋 때 변경 감지가 1만 개를 전부 스냅샷과 비교한다. 비용이 이중으로 든다.
- 성능 측정 계획이 있다면 **지금은 남긴다.** 이슈로 기록 → "Before" 기준선 측정 → `findByLotEntityAndLocationEntity` + `(lot_id, location_id)` 인덱스로 교체 → "After" 측정. 전후 비교 한 건이 완성된다.
- 결과가 틀리는 버그가 아니라 느린 것뿐이다. 측정 전에 고치면 Before 수치만 잃는다.

## 관련 노트

[[KDT_1차 정규프로젝트 MOC]]
