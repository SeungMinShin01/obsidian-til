---
출처: Claude 분석
원본: KDT_2026/2026B_Spring/springweb/src/main/java/day10
작성일: 2026-09-14
tags: [학습, java]
---

# Spring day10 — 리뷰 도메인과 쿼리 메소드로 자식 목록 받기

> 실습 파일: `day10/model/entity/ReviewsEntity.java`, `model/dto/ReviewsDto.java`, `model/repository/ReviewRepository.java`, `service/ReviewService.java`, `controller/ReviewController.java`
> 허브: [[Spring MOC]] · 이전: [[Spring day10 상품·카테고리 도메인과 응답 DTO 분리]] · 다음: [[Spring day10 WebClient로 공공데이터 API 대신 호출하기]]

앞 노트에서 DTO 만 자리를 잡아 두었던 **리뷰**가 엔티티부터 컨트롤러까지 한 벌로 채워졌습니다. 관계는 "상품 하나에 리뷰 여럿"이고, 카테고리 → 상품 → 리뷰 세 층이 완성되는 자리입니다. 리액트 쪽 `ReviewManager` 가 부르는 `/api/reviews` 가 여기입니다.

새로 갈리는 것은 셋입니다. 첫째, 상품 쪽에 리뷰 목록 필드를 두지 않은 **단방향 다대일**입니다. 둘째, `toEntity()` 가 연관 엔티티를 **매개변수로 받아** 끼우는 모양입니다. 셋째, 리포지토리에 `findByProductEntity_Bno` 라는 **연관 엔티티의 필드를 타고 들어가는 쿼리 메소드**가 선언된 점입니다.

정리하면 **부모(상품) 쪽을 건드리지 않고 자식(리뷰) 쪽만 세워 "이 상품의 리뷰 목록"을 받아 내는 자리**입니다.

## 1. 배운 내용

### 1-1. 리뷰 엔티티 — 한쪽만 아는 다대일

```java
@Entity
@NoArgsConstructor
@AllArgsConstructor
@Data
@Builder
@Table(name = "review")
public class ReviewsEntity {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Integer rno;

    private String reviewer;
    private String content;
    private int rating;

    @JoinColumn(name = "bno")
    @ManyToOne
    private ProductsEntity productEntity;
}
```

상품 엔티티가 카테고리를 들던 것과 같은 두 줄(`@ManyToOne` + `@JoinColumn`)입니다. 리뷰 표에 `bno` 외래키 컬럼이 생기고, 자바에서는 `ProductsEntity` 객체로 듭니다.

다른 점은 **상품 쪽에 `List<ReviewsEntity>` 가 없다**는 것입니다. 카테고리–상품은 양쪽이 서로를 알았지만(`@OneToMany(mappedBy=…)`), 상품–리뷰는 리뷰만 상품을 압니다. 이것이 단방향 관계입니다.

| | 카테고리–상품 (앞 노트) | 상품–리뷰 (이번) |
| --- | --- | --- |
| "다" 쪽 | `@ManyToOne` | `@ManyToOne` |
| "일" 쪽 | `@OneToMany(mappedBy=…)` 목록 있음 | 아무것도 없음 |
| 방향 | 양방향 | 단방향 |
| 표 모양 | 같다 — 외래키는 어차피 "다" 쪽 표에만 있다 | |

표 모양은 둘이 똑같습니다. 외래키는 어느 쪽이든 "다" 쪽 표에만 생기고, `@OneToMany` 목록은 그 외래키를 거꾸로 읽는 창일 뿐이기 때문입니다. 단방향으로 두면 `@ToString.Exclude`·`@Builder.Default` 같은 순환 방지 표시가 필요 없고, 상품 엔티티를 손대지 않아도 됩니다. 대신 "이 상품의 리뷰 목록"을 상품 객체에서 바로 꺼낼 수 없으니, 그 조회는 리포지토리가 맡아야 합니다(→ 1-3).

`rating` 이 `Integer` 가 아니라 `int` 인 것도 짚어 둘 만합니다. PK 처럼 "아직 없음"을 표현할 필요가 없는 값이라 기본형으로 두어도 되고, 그러면 `null` 이 들어올 자리가 원천적으로 사라집니다.

### 1-2. DTO — `toEntity()` 가 연관 엔티티를 받는 모양

```java
public ReviewsEntity toEntity(ProductsEntity productEntity) {
    return ReviewsEntity.builder()
            .reviewer(this.reviewer)
            .content(this.content)
            .rating(this.rating)
            .productEntity(productEntity)
            .build();
}

public static ReviewsDto from(ReviewsEntity entity) {
    return ReviewsDto.builder()
            .rno(entity.getRno())
            .bno(entity.getProductEntity().getBno())
            …
            .build();
}
```

앞 노트의 `ProductDto.toEntity()` 는 `cno` 를 아예 담지 않았습니다. 번호를 객체로 바꾸려면 리포지토리가 필요한데 DTO 는 그 층을 모르기 때문이었습니다. 이번엔 그 빈틈을 **매개변수**로 메웠습니다. 서비스가 상품 엔티티를 꺼내 `toEntity(productEntity)` 에 넘기면, 빌더 안에서 바로 연관 필드까지 채워집니다.

| 방식 | 모양 | 층 경계 |
| --- | --- | --- |
| 앞 노트 | `dto.toEntity()` 뒤 서비스가 `setCategoryEntity(…)` | DTO 는 연관을 모름, 서비스가 덧붙임 |
| 이번 | `dto.toEntity(productEntity)` | DTO 는 여전히 리포지토리를 모름, **객체를 받아서만** 끼움 |

둘 다 DTO 가 리포지토리를 부르지 않는다는 점은 같습니다. 이번 쪽은 엔티티가 만들어지는 순간 연관이 완성되어 `setter` 한 줄이 줄어들고, `productEntity` 가 없으면 컴파일부터 막힙니다.

`from()` 쪽은 `entity.getProductEntity().getBno()` 로 점 한 칸을 따라가 `bno` 를 평평하게 폅니다. 화면이 받는 JSON 은 `{ rno, bno, reviewer, content, rating }` 한 층입니다.

### 1-3. 리포지토리 — 연관 엔티티 안으로 들어가는 쿼리 메소드

```java
@Repository
public interface ReviewRepository extends JpaRepository<ReviewsEntity, Integer> {
    List<ReviewsEntity> findByProductEntity_Bno(Integer bno);
}
```

day08 에서 정리한 쿼리 메소드가 한 단계 더 나갔습니다. `findBy` 뒤에 필드 이름을 적으면 조건이 되는데, 그 필드가 **연관 엔티티**이면 밑줄(`_`)로 그 안의 필드까지 내려갈 수 있습니다.

| 조각 | 뜻 |
| --- | --- |
| `findBy` | 조회 |
| `ProductEntity` | 리뷰의 `productEntity` 필드 (연관 엔티티) |
| `_Bno` | 그 안의 `bno` 필드 |
| `(Integer bno)` | 조건값 |

스프링 데이터가 이 이름을 읽어 `select … from review r join product p … where p.bno = ?` 에 해당하는 쿼리를 만들어 줍니다. 밑줄은 `findByProductEntityBno` 처럼 붙여 써도 대개 풀리지만, `productEntity` 안에 `bno` 가 있다는 경계가 애매해질 수 있어 밑줄로 끊어 두는 편이 안전합니다.

단방향이라 상품 객체에서 리뷰 목록을 꺼낼 수 없다고 했는데, 바로 이 메소드가 그 대안입니다. 목록 필드 없이도 "이 상품의 리뷰"를 한 쿼리로 받습니다.

### 1-4. 서비스 — 전체를 받아 거르기 vs 조건으로 받기

```java
@Service
public class ReviewService {
    @Autowired private ReviewRepository reviewRepository;
    @Autowired private ProductsRepository productsRepository;

    public List<ReviewsDto> getreviews(Integer bno) {
        List<ReviewsEntity> reviewEntities = reviewRepository.findAll();
        List<ReviewsDto> reviewDtos = new ArrayList<>();
        reviewEntities.forEach((reviewEntity) -> {
            if (reviewEntity.getProductEntity().getBno().equals(bno)) {
                reviewDtos.add(ReviewsDto.from(reviewEntity));
            }
        });
        return reviewDtos;
    }
    …
}
```

조회는 `findAll()` 로 전부 받은 뒤 자바에서 `bno` 가 같은 것만 골라 담는 모양입니다. 리포지토리에 선언된 `findByProductEntity_Bno` 는 아직 서비스에서 부르지 않고 있습니다. 두 갈래를 나란히 두면 이렇습니다.

| | `findAll()` 뒤 자바에서 거르기 | `findByProductEntity_Bno(bno)` |
| --- | --- | --- |
| DB 가 주는 것 | 리뷰 표 전체 | 조건에 맞는 행만 |
| 거르는 곳 | 서비스(자바) | DB(`where`) |
| 리뷰가 많아지면 | 전부 실어 와서 대부분 버린다 | 필요한 만큼만 온다 |

리뷰가 몇 개일 때는 차이가 없지만, 표가 커지면 전체를 실어 오는 쪽은 메모리와 시간을 그만큼 씁니다. 조건이 있는 조회는 DB 에 맡기는 편이 안전하고, 리포지토리에 이미 그 메소드가 있으니 서비스 한 줄을 바꾸면 됩니다(→ 2-1).

`equals()` 로 비교하는 점은 짚어 둘 만합니다. `bno` 가 `Integer` 라 `==` 는 참조 비교가 되어 `-128~127` 밖에서는 같은 값도 `false` 가 날 수 있습니다. 래퍼 타입끼리는 `equals()` 가 맞습니다.

등록은 앞 노트 2-3 에서 "이렇게 될 것"이라 적어 둔 순서 그대로입니다.

```java
public boolean createreview(ReviewsDto reviewDto) {
    ProductsEntity productEntity = productsRepository.findById(reviewDto.getBno()).orElse(null);
    if (productEntity == null) return false;
    ReviewsEntity savedEntity = reviewRepository.save(reviewDto.toEntity(productEntity));
    return savedEntity.getRno() >= 1;
}
```

| 단계 | 하는 일 |
| --- | --- |
| `productsRepository.findById(bno).orElse(null)` | 번호 → 상품 객체. 없으면 `null` |
| `null` 이면 `false` | 없는 상품에 리뷰를 달 수 없다 |
| `reviewDto.toEntity(productEntity)` | 객체를 받아 연관까지 채운 엔티티 |
| `save()` → `getRno() >= 1` | IDENTITY 라 저장 직후 번호가 채워지는 것으로 성공 판정 |

서비스가 **이웃 표의 리포지토리(`ProductsRepository`)를 함께 드는** 것이 여기서 실제로 일어납니다. `Optional.orElse(null)` 은 day08 의 `isPresent()` 분기를 한 줄로 줄인 표기입니다.

삭제는 `deleteById(rno)` 한 줄에 `true` 를 돌려줍니다. 카테고리·상품 쪽은 `findById` 로 먼저 걸렀는데 이쪽은 바로 지웁니다. 없는 번호를 지우려 하면 예외가 나는 자리이므로, 일반적으로는 먼저 거르는 쪽이 안전합니다(→ 2-2).

### 1-5. 컨트롤러 — 세 매핑에 값을 싣는 자리

```java
@RestController
@RequestMapping("/api/reviews")
@CrossOrigin(value = "http://localhost:5173")
public class ReviewController {
    @Autowired ReviewService reviewService;

    @GetMapping    public List<ReviewsDto> getreview(@RequestParam(name = "bno") Integer bno) { … }
    @PostMapping   public boolean createreview(@RequestBody ReviewsDto reviewDto) { … }
    @DeleteMapping public boolean deletereview(@RequestParam(name = "rno") Integer rno) { … }
}
```

| 요청 | 값이 실리는 곳 | 화면(`ReviewManager`) 쪽 |
| --- | --- | --- |
| `GET /api/reviews?bno=3` | 쿼리 스트링 → `@RequestParam` | 모달이 열릴 때 `product.bno` 로 조회 |
| `POST /api/reviews` | 본문 JSON → `@RequestBody` | 입력 폼 + `bno` 를 함께 보냄 |
| `DELETE /api/reviews?rno=7` | 쿼리 스트링 → `@RequestParam` | 줄마다 삭제 버튼 |

카테고리와 같이 수정이 없는 세 갈래입니다. 목록 조회가 `@RequestParam` 을 받는 것이 상품·카테고리와 다른 점인데, 리뷰는 "전체 목록"이 아니라 항상 **어느 상품의 목록**이라 조건 없는 `GET` 이 성립하지 않기 때문입니다. `@GetMapping` 에 빈 문자열 대신 아무것도 안 적어도 `@RequestMapping` 의 주소가 그대로 쓰입니다.

`@Autowired` 를 필드에 붙이는 방식이고, 상품 컨트롤러는 생성자 주입이었습니다. 한 프로젝트 안에서 두 방식이 섞여 있는 셈인데, 동작은 같고 관용은 생성자 주입 쪽입니다.

## 2. 추가로 알면 좋은 활용법

### 2-1. 조회를 쿼리 메소드 한 줄로

리포지토리에 선언된 메소드를 쓰면 서비스가 짧아집니다.

```java
public List<ReviewsDto> getreviews(Integer bno) {
    return reviewRepository.findByProductEntity_Bno(bno).stream()
            .map(ReviewsDto::from)
            .toList();
}
```

`where` 는 DB 가, 변환은 스트림이 맡습니다. 카테고리 서비스의 `findAll().stream().map(CategoryDto::from).toList()` 와 같은 모양에 조건만 붙은 것입니다.

정렬까지 이름에 넣을 수 있습니다.

```java
List<ReviewsEntity> findByProductEntity_BnoOrderByRnoDesc(Integer bno);
```

최신 리뷰가 위로 오는 목록이 되고, 화면에서 뒤집을 필요가 없어집니다.

### 2-2. 삭제 전에 거르기, 그리고 `boolean` 의 한계

```java
public boolean deletereview(Integer rno) {
    if (!reviewRepository.existsById(rno)) return false;
    reviewRepository.deleteById(rno);
    return true;
}
```

`existsById` 는 `findById` 보다 가벼운 존재 확인입니다. 엔티티를 실어 올 필요 없이 `count` 하나로 끝납니다. 이렇게 거르면 "없는 번호"가 예외가 아니라 `false` 로 화면에 돌아갑니다.

다만 `boolean` 하나로는 "없어서 실패"와 "다른 오류로 실패"를 갈라 보이지 못합니다. 이 갈림이 필요해지는 시점이 `ResponseEntity` 로 상태 코드(`404`·`400`)를 실어 보내는 자리입니다.

### 2-3. 단방향을 양방향으로 바꾸고 싶을 때

상품 상세에 리뷰 목록을 함께 실어야 하면 상품 쪽에 창을 하나 낼 수 있습니다.

```java
// ProductsEntity
@OneToMany(mappedBy = "productEntity", cascade = CascadeType.ALL)
@ToString.Exclude
@Builder.Default
private List<ReviewsEntity> reviewList = new ArrayList<>();
```

카테고리 엔티티와 똑같은 세 표시가 따라옵니다. 대신 상품 목록을 조회할 때 리뷰까지 LAZY 로 딸려 올 수 있어 1+N 이 한 겹 더 생기는 자리이기도 합니다. 지금처럼 리뷰가 **모달에서 따로 조회**되는 화면이라면 단방향 + 쿼리 메소드가 더 가볍고, 상세 응답에 리뷰가 늘 붙어야 하면 양방향 + `join fetch` 쪽이 어울립니다.

### 2-4. 리뷰 등록 후 응답에 번호 실어 주기

지금은 `boolean` 만 돌려주고 화면이 목록을 다시 받습니다. 저장된 DTO 를 돌려주면 화면이 재조회 없이 목록에 한 줄을 붙일 수 있습니다.

```java
public ReviewsDto createreview(ReviewsDto dto) {
    ProductsEntity product = productsRepository.findById(dto.getBno()).orElse(null);
    if (product == null) return null;
    return ReviewsDto.from(reviewRepository.save(dto.toEntity(product)));
}
```

`save()` 가 돌려준 엔티티에는 `rno` 가 채워져 있으니 `from()` 으로 바로 응답이 됩니다.

### 2-5. 별점 값을 서버에서 막기

`rating` 은 `int` 라 `null` 은 못 들어오지만 `0` 이나 `99` 는 들어옵니다. DTO 필드에 검증 표시를 붙이고 컨트롤러 매개변수에 `@Valid` 를 두면 컨트롤러에 닿기 전에 걸러집니다.

```java
@Min(1) @Max(5)
private int rating;

@PostMapping
public boolean createreview(@Valid @RequestBody ReviewsDto reviewDto) { … }
```

`spring-boot-starter-validation` 의존성이 필요하고, 어긋나면 `400` 이 돌아갑니다.

## 3. 더 나아가 알면 좋은 것

### 3-1. 쿼리 메소드 이름이 길어질 때

`findByProductEntity_BnoAndRatingGreaterThanEqualOrderByRnoDesc` 처럼 조건이 쌓이면 이름으로 읽기 어려워집니다. 그 시점이 day08 에서 이름만 정리한 `@Query`(JPQL) 로 옮길 때입니다.

```java
@Query("select r from ReviewsEntity r where r.productEntity.bno = :bno order by r.rno desc")
List<ReviewsEntity> findReviews(@Param("bno") Integer bno);
```

`r.productEntity.bno` 처럼 JPQL 도 점으로 연관을 타고 들어갑니다. 쿼리 메소드의 밑줄이 JPQL 의 점과 같은 자리입니다.

### 3-2. 세 층이 완성된 뒤의 조회 설계

카테고리 → 상품 → 리뷰가 다 붙었습니다. 목록 화면마다 어디까지 실을지가 갈립니다.

| 화면 | 실을 것 | 조회 모양 |
| --- | --- | --- |
| 상품 목록 | 상품 + 카테고리 이름 | `@ManyToOne` EAGER 로 이미 조인 |
| 리뷰 모달 | 그 상품의 리뷰만 | `findByProductEntity_Bno` |
| 상품 상세(있다면) | 상품 + 리뷰 목록 | 양방향 + `join fetch` 또는 조회 둘 |

응답 DTO 를 화면마다 갈라 두는 앞 노트의 정리가 여기서 값어치를 냅니다. 목록은 짧게, 모달은 리뷰만, 상세만 길게.

### 3-3. 삭제가 번지는 방향

지금 구조에서 카테고리를 지우면 `cascade = ALL` 로 상품이 지워지는데, 상품 → 리뷰에는 cascade 가 없습니다. 상품에 리뷰가 달려 있으면 외래키 제약에 걸려 삭제가 실패하는 자리입니다. 도메인에서 "상품이 없어지면 리뷰도 없어진다"가 맞다면 양방향으로 바꿔 cascade 를 두거나, 서비스에서 리뷰를 먼저 지우는 순서를 두어야 합니다. 이 순서가 한 트랜잭션이어야 하므로 `@Transactional` 이 붙을 자리이기도 합니다.

### 3-4. 다음에 볼 키워드

- 쿼리 메소드 키워드 — `And`·`Or`·`OrderBy`·`Containing`·`Between`·`GreaterThan`, 연관 필드는 `_` 로 내려가기
- `@Query` + `@Param` — 이름이 길어질 때 JPQL 로 옮기기
- `existsById`·`countBy…` — 엔티티를 안 실어 오는 확인
- `@Valid`·`@Min`·`@Max` — 요청 DTO 검증과 `400`
- `ResponseEntity` — `boolean` 대신 `404`·`400` 으로 실패 이유 갈라 보내기
- 단방향 vs 양방향 — 화면이 목록을 따로 부르는지, 상세에 늘 붙는지로 고르기
- `@Transactional` — 자식 먼저 지우고 부모 지우는 순서를 한 단위로 묶기
- `@ManyToOne(fetch = FetchType.LAZY)` — 리뷰 목록 조회 때 상품이 매번 조인되는 것 끊기

## 실습 파일

- `2026B_Spring/springweb/src/main/java/day10/model/entity/ReviewsEntity.java` (**단방향 다대일** — `@ManyToOne` + `@JoinColumn(name = "bno")` 로 리뷰 표에 외래키를 두고 상품 쪽에는 목록 필드를 두지 않은 구조, 표 모양은 양방향과 같고 순환 방지 표시가 필요 없어지는 자리, `rating` 을 `int` 로 두어 `null` 자리를 없앤 점)
- `2026B_Spring/springweb/src/main/java/day10/model/dto/ReviewsDto.java` (**`toEntity(ProductsEntity)`** — 연관 엔티티를 매개변수로 받아 빌더 안에서 바로 끼우는 모양과 DTO 가 여전히 리포지토리를 모르는 층 경계, `from()` 이 `getProductEntity().getBno()` 로 한 칸 따라가 `bno` 를 평평하게 펴는 자리)
- `2026B_Spring/springweb/src/main/java/day10/model/repository/ReviewRepository.java` (**`findByProductEntity_Bno`** — 쿼리 메소드가 밑줄로 연관 엔티티 안의 필드까지 내려가는 표기, 단방향이라 상품 객체에서 못 꺼내는 리뷰 목록을 한 쿼리로 받는 대안)
- `2026B_Spring/springweb/src/main/java/day10/service/ReviewService.java` (**전체 받아 거르기와 조건 조회의 대비** — `findAll()` 뒤 자바 `if` 로 거르는 지금 모양과 리포지토리 메소드로 DB 에 맡기는 갈래, `Integer` 비교에 `equals()` 를 쓰는 이유, 등록에서 `productsRepository.findById(bno).orElse(null)` 로 번호를 객체로 바꿔 `toEntity(productEntity)` 에 넘기는 순서와 이웃 리포지토리를 함께 드는 서비스, `getRno() >= 1` 성공 판정, 삭제가 거르지 않고 바로 `deleteById` 하는 자리)
- `2026B_Spring/springweb/src/main/java/day10/controller/ReviewController.java` (`/api/reviews` 에 GET·POST·DELETE 셋 — 목록 조회가 항상 `bno` 를 `@RequestParam` 으로 받는 이유, `@GetMapping` 에 값을 안 적으면 클래스 주소가 그대로 쓰이는 점, 같은 `@CrossOrigin`, 필드 `@Autowired` 와 생성자 주입이 한 프로젝트에 섞인 자리)

## 관련 노트

[[Spring MOC]] · [[Spring day10 상품·카테고리 도메인과 응답 DTO 분리]] · [[Spring day10 WebClient로 공공데이터 API 대신 호출하기]] · [[KDT_2026 학습 지도]]
