---
출처: Claude 분석
원본: 코드리뷰 세션 (claude.ai 프로젝트 「미니프로젝트」)
작성일: 2026-09-28
tags: [프로젝트, java]
---

> 상위: [[KDT_1차 정규프로젝트 MOC]]

# WMS 코드리뷰 - ED-10 ED-21 정렬 비교

## ED-10 입고 문서 목록 정렬 — 조현우

### 한 줄 요약

정렬 블록만 다르고 나머지는 같다. 차이는 동점 순서 하나이고, 더 큰 문제는 둘이 공유한다.

### 코드

**팀장**

```java
for (int i = 0; i < inbounds.size(); i++) {
    for (int j = i + 1; j < inbounds.size(); j++) {
        if (inbounds.get(j).getExpectedAt().isBefore(inbounds.get(i).getExpectedAt())) {
            DocumentEntity temp = inbounds.get(i);
            inbounds.set(i, inbounds.get(j));
            inbounds.set(j, temp);
        }
    }
}
```

**팀원**

```java
inbounds.sort((a, b) -> a.getExpectedAt().compareTo(b.getExpectedAt()));
```

### 메서드 단위

```
IN  : 파라미터 없음 → 실제 입력은 DB의 document 테이블 전체 (입고 + 출고)
  ↓ ① findAll()        전체 로드
  ↓ ② type 필터         INBOUND만 새 리스트에 담음
  ↓ ③ expectedAt 정렬   ← 두 코드가 다른 유일한 구간
  ↓ ④ DTO 변환          새 리스트에 담음
OUT : List<InboundListDto> (새로 만든 리스트, 엔티티는 밖으로 나가지 않음)
```

### 무엇이 다른가

**정렬 부분**

| | 팀원 (sort + compareTo) | 팀장 (이중 for + isBefore) |
|---|---|---|
| 동점 순서 | 유지됨 (안정 정렬) | 섞일 수 있음 |
| 비용 | O(n log n) | 항상 O(n²) |
| 코드가 드러내는 것 | "무엇을 기준으로 정렬하는지" | "어떻게 정렬하는지" (알고리즘을 직접 구현) |
| 주석 | compareTo의 반환값 규칙 설명 | isBefore의 의미와 temp 교환 설명 |

#### ① 이중 for문 vs sort

- 팀장: 이중 for문으로 자리를 직접 바꾸는 교환 정렬 (버블 정렬과 비슷한 방식)
- 팀원: `List.sort` 사용, 내부는 TimSort
- 팀장 코드는 불안정 정렬이라 예정일이 같은 건끼리 순서가 뒤집힐 수 있고, 팀원 코드는 안정 정렬이라 원래 순서가 유지된다.
- 단, 불안정 ≠ 무작위. 같은 입력이면 팀장 코드도 매번 같은 결과가 나온다.

```
입력: [A(10시), B(10시), C(5시)]
팀장 → [C, B, A]   (A, B 순서 뒤집힘)
팀원 → [C, A, B]   (A, B 순서 유지)
```

#### ② 성능

| | 팀장 코드 | 팀원 코드 |
|---|---|---|
| 시간복잡도 | 항상 O(n²). 이미 정렬돼 있어도 n(n-1)/2번 비교 | O(n log n). 이미 정렬돼 있으면 약 n번 비교로 끝남 |
| LinkedList가 들어오면 | `get(i)`가 O(n)이라 O(n³) | 내부에서 배열로 복사해 정렬하므로 영향 없음 |

입고 목록이 수십 건이면 체감할 차이는 없다. 하지만 더미 데이터로 성능을 측정할 계획이라면 차이가 드러난다.

#### ③ 시간 비교 방식 (isBefore와 compareTo)

- 팀장: `a.isBefore(b)` → a가 b보다 이전이면 true/false
- 팀원: `a.compareTo(b)` → 이전이면 음수, 같으면 0, 이후면 양수
- `LocalDateTime`에서는 둘의 결과가 같다. 날짜는 `<`로 비교할 수 없어서 둘 다 메서드로 비교한 것.
- 차이는 표현 방식뿐. `isBefore`는 조건문에, `compareTo`는 정렬 기준(Comparator)에 맞는 형태다.

### 각자 놓친 것

- **팀장**: 동점 순서가 보장되지 않고, 데이터가 많아지면 느리다(O(n²)). 표준 API로 되는 걸 직접 구현했다.
- **팀원**: 안정 정렬로 순서가 유지되지만 우연의 일치다. `findAll()`에 ORDER BY가 없어서 입력 순서 자체가 보장되지 않는다.
- **둘 다**: 동점일 때 기준(예: `document_id`)이 없다.
- **둘 다**: 전체를 가져와 자바에서 거르고 정렬한다. DB에서 `WHERE type='INBOUND' ORDER BY expected_at, document_id`로 처리할 수 있다.
- 참고: v1 스키마에서 `type`, `expected_at`은 둘 다 NOT NULL이라 DB에서 읽어온 엔티티라면 null로 인한 NPE는 나지 않는다. 따라서 null 처리는 두 코드 모두 필요 없다.

---

## ED-21 재고 조회 정렬 (FEFO) — 조현우

### 한 줄 요약

둘 다 안정 정렬이고 결과도 거의 같다. 차이는 정렬 기준의 단계 수(1단계 vs 3단계)와 반환 리스트의 수정 가능 여부이고, 더 큰 문제(N+1)는 둘이 공유한다.

### 코드

**팀장**

```java
List<StockDto> stockDtos = stockRepository.findAll().stream()
        // 소비기한 빠른 순 조회 (FEFO)
        .sorted((a, b) -> {
            return a.getLotEntity().getExpiryDate()
                    .compareTo(b.getLotEntity().getExpiryDate());
        })
        .map((stock) -> {
            return StockDto.from(stock);
        })
        .toList();
```

**팀원**

```java
List<StockEntity> stockEntities = stockRepository.findAll();
// FEFO정렬: 유통기한 오름차순 -> 유통기한없는 lot는 맨 뒤로 -> 같으면 stockId순으로
stockEntities.sort(
    Comparator.comparing((StockEntity s) -> s.getLotEntity().getExpiryDate(),
        Comparator.nullsLast(Comparator.naturalOrder()))
    .thenComparing(StockEntity::getStockId)
);
List<StockDto> stockDtos = new ArrayList<>();
stockEntities.forEach(stockEntity -> stockDtos.add(StockDto.from(stockEntity)));
```

### 메서드 단위

```
IN  : 파라미터 없음 → 실제 입력은 DB의 stock 테이블 전체 + 각 재고에 연결된 lot
  ↓ ① findAll()             전체 로드
  ↓ ② 소비기한 정렬 (FEFO)   ← 두 코드가 다른 구간 (기준 단계 수)
  ↓ ③ DTO 변환
OUT : List<StockDto>
      팀원 → ArrayList (수정 가능)
      팀장 → .toList() (수정 불가, add 하면 예외)
```

### 무엇이 다른가

**정렬 부분**

| | 팀원 (Comparator 조합) | 팀장 (stream + 람다) |
|---|---|---|
| 동점 순서 | `stockId` 순으로 고정 | 입력 순서 유지 (안정 정렬), 그러나 입력 순서가 보장 안 됨 |
| 정렬 기준 | 소비기한 → null은 뒤로 → stockId (3단계) | 소비기한 (1단계) |
| null 처리 | `nullsLast`로 맨 뒤 (스키마상 null 없음) | 없음 (스키마상 null 없어서 문제 없음) |
| 원본 리스트 | 직접 정렬 (이 메서드 안에서만 써서 문제 없음) | 건드리지 않음 |
| 반환 리스트 | 수정 가능 | 수정 불가 |

#### ① 정렬 방식: 둘 다 안정 정렬

- 팀원: 리스트에 바로 `sort` 적용 (List.sort, 안정 정렬)
- 팀장: `stream().sorted()` 사용 (순서가 있는 스트림이면 안정 정렬)
- 이번에는 안정/불안정 차이가 없다. 차이는 **정렬 기준을 몇 단계로 잡았는지**다.

#### ② 람다 직접 작성 vs Comparator 조합

- 팀장: `(a, b) -> a...compareTo(b...)`로 비교 규칙을 직접 작성
- 팀원: `Comparator.comparing()`, `nullsLast()`, `thenComparing()`을 조합
- 기준이 하나일 땐 두 방식이 같다. 기준이 늘어나면 조합 방식이 읽기 쉽고 null 처리도 붙이기 쉽다.
- 팀원 코드의 `(StockEntity s)` 타입 명시는 `thenComparing`을 이어 붙일 때 컴파일러가 타입을 추론하지 못해서 필요한 것이다.

#### ③ 성능

- 정렬 자체는 둘 다 O(n log n)으로 같다.
- 성능 차이가 나는 곳은 정렬 알고리즘이 아니라 **정렬 중 `getLotEntity()` 호출**이다. lot이 LAZY 로딩이면 lot 개수만큼 추가 쿼리가 나간다(N+1). 이건 두 코드가 똑같다.

### 각자 놓친 것

- **팀장**: 동점 기준이 없다. 같은 소비기한 재고의 순서가 DB 반환 순서에 맡겨진다.
- **팀원**: v1 스키마에서 `stock.lot_id`와 `lot.expiry_date`가 둘 다 NOT NULL이라 "소비기한 없는 lot"은 존재할 수 없다. `nullsLast`는 일어나지 않는 경우를 처리하는 코드이고, 주석도 현재 설계와 맞지 않는다. 같은 이유로 팀장 코드의 "null 처리 없음"도 실제 문제는 아니다.
- **팀원**: 주석에 "유통기한"이라고 썼다. 팀 용어사전은 **소비기한(expiry date)** 으로 통일했다.
- **둘 다**: N+1 가능성. DB에서 `JOIN lot ORDER BY expiry_date, stock_id`로 처리할 수 있다.

---

## 정렬 API 간단 정리

### 1. `Comparator.comparing`

```java
Comparator.comparing(StockEntity::getStockId)
Comparator.comparing(s -> s.getLotEntity().getExpiryDate(), 비교방법)
```

- 객체에서 **"무엇을 기준으로 비교할지" 값을 꺼내는 함수**를 받아 Comparator를 만들어 준다.
- `compareTo`를 직접 쓰지 않아도 "이 값 기준으로 정렬"이라는 의도만 적으면 된다.
- 두 번째 인자로 그 값을 **어떻게 비교할지**(예: null 처리)를 따로 넘길 수 있다.

### 2. `Comparator.nullsLast(Comparator.naturalOrder())`

```java
Comparator.nullsLast(Comparator.naturalOrder())
```

- `naturalOrder()`: 값 자체의 기본 순서(`compareTo`)로 비교한다. 날짜면 이른 순, 숫자면 작은 순(오름차순).
- `nullsLast(...)`: null은 **맨 뒤**로 보내고, null이 아닌 값끼리는 안에 넣은 방법(`naturalOrder`)으로 비교한다.
- 이게 없으면 null을 만났을 때 `compareTo`를 호출하다가 NPE가 난다. 반대로 맨 앞에 두려면 `nullsFirst`를 쓴다.

### 3. `.thenComparing`

```java
Comparator.comparing(소비기한).thenComparing(StockEntity::getStockId)
```

- 앞의 기준으로 비교한 결과가 **같을 때(0일 때)만** 다음 기준으로 비교한다.
- 엑셀에서 "1차 정렬: 소비기한, 2차 정렬: 재고번호"와 같은 개념이다.
- 동점 순서를 고정하는 도구다. 이게 있어야 입력 순서와 상관없이 결과가 항상 같다.

### 4. `.sorted((a, b) -> { return ...compareTo(...); })`

```java
.sorted((a, b) -> {
    return a.getLotEntity().getExpiryDate()
            .compareTo(b.getLotEntity().getExpiryDate());
})
```

- 스트림의 `sorted`에 **비교 규칙을 람다로 직접** 넘긴 것이다. 람다가 Comparator의 `compare(a, b)` 역할을 한다.
- 반환값 규칙: 음수면 a가 앞, 0이면 같음, 양수면 b가 앞.
- 원본 리스트는 그대로 두고 **정렬된 새 흐름**을 만든다. 순서가 있는 스트림이면 안정 정렬이다.
- 같은 내용을 더 짧게 쓰면 `.sorted(Comparator.comparing(s -> s.getLotEntity().getExpiryDate()))`가 된다. 여기에 `nullsLast`나 `thenComparing`을 이어 붙일 수 있다.

## 관련 노트

[[KDT_1차 정규프로젝트 MOC]]
