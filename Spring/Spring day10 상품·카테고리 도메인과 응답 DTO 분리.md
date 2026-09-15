---
출처: Claude 분석
원본: KDT_2026/2026B_Spring/springweb/src/main/java/day10
작성일: 2026-09-14
tags: [학습, java]
---

# Spring day10 — 상품·카테고리 도메인과 응답 DTO 분리

> 실습 파일: `day10/AppStart.java`, `model/entity/ProductsEntity.java`, `model/entity/CategoryEntity.java`, `model/dto/ProductDto.java`, `model/dto/ProductResponseDto.java`, `model/dto/CategoryDto.java`, `model/dto/ReviewsDto.java`, `model/repository/ProductsRepository.java`, `model/repository/CategoryRepository.java`, `service/ProductsService.java`, `service/CategoryService.java`, `controller/ProductsController.java`, `controller/CategoryController.java`
> 허브: [[Spring MOC]] · 이전: [[Spring day09 화면 쪽 자바스크립트 기초 다시 훑기]] · 다음: [[Spring day10 리뷰 도메인과 쿼리 메소드로 자식 목록 받기]]

day09가 화면 쪽 문법을 훑는 자리였다면, 이번에는 다시 서버로 돌아와 **새 도메인 한 벌**을 세웁니다. 게시글·댓글이 아니라 상품(product)·카테고리(category)이고, 관계는 "카테고리 하나에 상품 여럿"입니다. 층은 지금까지와 같이 엔티티 → 리포지토리 → 서비스 → 컨트롤러 넷이고, 골격은 day08의 반복 실습에서 굳힌 모양 그대로입니다.

이번 자리에서 새로 갈리는 것은 세 가지입니다. 하나는 **받는 DTO와 내보내는 DTO를 따로 두는 것**(`ProductDto` 와 `ProductResponseDto`), 또 하나는 서비스가 연관 엔티티를 따라가 **응답을 평평하게 조립하는 것**, 마지막은 컨트롤러 위에 붙은 `@CrossOrigin("http://localhost:5173")` 로 **화면이 같은 서버가 아니라 Vite 개발 서버에서 온다**는 전제가 코드에 처음 드러난 것입니다.

정리하면 **같은 네 층을 상품 도메인으로 한 번 더 세우면서, 화면이 따로 도는 상황을 응답 DTO와 CORS 표시로 준비해 두는 자리**입니다.

## 1. 배운 내용

### 1-1. 진입점을 day10 패키지에 두기

```java
package day10;

@SpringBootApplication
public class AppStart {
    public static void main(String[] args) {
        SpringApplication.run(AppStart.class);
    }
}
```

앞 day들과 같은 배치입니다. `@SpringBootApplication` 이 붙은 클래스의 **패키지가 컴포넌트 스캔의 뿌리**가 되므로, `day10` 아래에 있는 `controller`·`service`·`model` 만 이 진입점으로 뜹니다. day08·day09 의 클래스들은 옆 패키지라 스캔 범위 밖이고, 한 프로젝트에 `main` 이 여럿 있을 때 실행할 것을 고르는 문제는 day02 에서 정리한 대로입니다.

| 항목 | 정리 |
| --- | --- |
| 스캔 범위 | 진입점이 있는 패키지와 그 하위 |
| 같은 프로젝트의 다른 day | 스캔 밖 — 서로 섞이지 않는다 |
| 엔티티 스캔 | 같은 규칙. `day10.model.entity` 만 표로 만들어진다 |

### 1-2. 상품 엔티티 — "다" 쪽

```java
@Entity
@NoArgsConstructor
@AllArgsConstructor
@Data
@Builder
@Table(name = "product")
public class ProductsEntity {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Integer bno;

    private String name;
    private Integer price;

    @JoinColumn(name = "cno")
    @ManyToOne
    private CategoryEntity categoryEntity;
}
```

클래스 이름은 `ProductsEntity` 이지만 `@Table(name = "product")` 로 표 이름을 따로 정했습니다. 클래스 이름과 표 이름이 어긋나도 이 한 줄로 짝이 맞습니다. 표 이름을 정하지 않으면 클래스 이름을 스네이크 표기로 바꾼 `products_entity` 가 표가 되므로, DB 쪽 이름을 먼저 정해 두는 편이 안전합니다.

관계는 `@ManyToOne` + `@JoinColumn(name = "cno")` 두 줄입니다. 상품 표에 `cno` 라는 외래키 컬럼이 생기고, 자바에서는 번호가 아니라 `CategoryEntity` 객체로 들고 있습니다. day06·day08 에서 게시글–댓글에 걸었던 것과 같은 구조이고, 이번엔 이름만 카테고리–상품으로 바뀌었습니다.

| 표시 | 하는 일 |
| --- | --- |
| `@Table(name = …)` | 클래스 이름과 별개로 표 이름을 정한다 |
| `@ManyToOne` | 이쪽이 "다", 상대가 "일" |
| `@JoinColumn(name = "cno")` | 외래키 컬럼 이름. 안 적으면 `필드명_상대PK` 규칙으로 생긴다 |
| `@Builder` + `@AllArgsConstructor` + `@NoArgsConstructor` | 빌더 조립과 JPA 가 요구하는 기본 생성자를 함께 갖추는 세트 |

기본형이 아니라 `Integer` 로 둔 점도 그대로입니다. 아직 저장되지 않은 새 상품은 번호가 없어야 하는데, `int` 는 `null` 을 담지 못해 `0` 이 되어 버립니다.

### 1-3. 카테고리 엔티티 — "일" 쪽과 롬복 두 표시

```java
@Entity
@Table(name = "category")
@NoArgsConstructor
@AllArgsConstructor
@Builder
@Data
public class CategoryEntity {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Integer cno;
    private String name;

    @OneToMany(mappedBy = "categoryEntity", cascade = CascadeType.ALL)
    @ToString.Exclude
    @Builder.Default
    private List<ProductsEntity> productList = new ArrayList<>();
}
```

`@OneToMany(mappedBy = "categoryEntity")` 의 값은 **상대 엔티티의 필드 이름**입니다. 상품 쪽에서 `private CategoryEntity categoryEntity;` 로 적었으므로 그 이름을 그대로 옮깁니다. 외래키는 "다" 쪽 표에만 있고, 이쪽 목록은 그 외래키를 거꾸로 읽는 창일 뿐이라 `mappedBy` 로 "주인은 저쪽"이라고 표시합니다.

목록 필드에 롬복 표시가 둘 붙어 있는 것이 이번 자리의 요점입니다.

| 표시 | 없으면 생기는 일 |
| --- | --- |
| `@ToString.Exclude` | `@Data` 가 만든 `toString()` 이 상품 목록 → 각 상품의 카테고리 → 다시 목록 … 으로 **무한히 서로를 부른다** |
| `@Builder.Default` | 빌더로 만들면 `= new ArrayList<>()` 초기화가 무시되어 목록이 `null` 이 된다 |

`@Data` 는 편하지만 양방향 관계에서는 `toString`·`equals`·`hashCode` 가 상대를 타고 넘어갑니다. 목록 쪽에서 끊어 두는 것이 가장 짧은 대처이고, day06 의 순환참조 정리가 JSON 이 아니라 `toString` 에서 다시 나타난 자리입니다.

`@Builder.Default` 는 빌더가 필드 초기화 식을 모른다는 사정에서 옵니다. 빌더는 `build()` 시점에 전달받은 값만 생성자에 넣고, 클래스에 적어 둔 `= new ArrayList<>()` 는 빌더가 만든 생성 경로에서는 지나갑니다. 이 표시를 붙이면 그 초기값을 빌더의 기본값으로 삼습니다. 컬렉션 필드를 빌더와 함께 쓸 때는 거의 항상 짝으로 붙는 표시입니다.

`cascade = CascadeType.ALL` 은 카테고리를 저장·삭제하면 딸린 상품에도 같은 일이 번지게 합니다. 카테고리를 지우면 상품이 같이 지워지는 것이라, 도메인에서 그래도 되는지 먼저 정해 두어야 하는 자리입니다.

### 1-4. 받는 DTO 와 내보내는 DTO 를 갈라 두기

```java
// 받는 쪽 — 화면이 보내는 값
public class ProductDto {
    private Integer bno;
    private String name;
    private Integer price;
    private Integer cno;
    …
}

// 내보내는 쪽 — 화면이 그릴 값
public class ProductResponseDto {
    private Integer bno;
    private String name;
    private Integer price;
    private Integer cno;
    private String cName;
    …
}
```

지금까지는 DTO 한 벌을 등록·조회에 겸용했습니다. 이번에는 **응답 전용 DTO** 가 따로 생겼고, 갈리는 필드는 `cName` 하나입니다.

이유는 방향이 다르기 때문입니다. 화면이 상품을 등록할 때는 카테고리를 **번호**(`cno`)로 고릅니다. 이름을 보내면 서버가 다시 번호로 찾아야 하니 번호가 맞습니다. 반대로 목록을 그릴 때 화면에 필요한 것은 번호가 아니라 **이름**입니다. 번호만 내려주면 화면이 카테고리 목록을 따로 받아 짝을 맞춰야 합니다.

| | 받는 DTO (`ProductDto`) | 내보내는 DTO (`ProductResponseDto`) |
| --- | --- | --- |
| 카테고리 | `cno` 번호만 | `cno` + `cName` 이름까지 |
| 만드는 쪽 | 화면 → `@RequestBody` | 서버 → 엔티티에서 `from()` |
| 담는 기준 | 저장에 필요한 최소 | 화면이 그릴 때 필요한 만큼 |

두 DTO 모두 `toEntity()` 와 `from()` 두 변환 메소드를 갖고, `from()` 이 `static` 인 이유는 day08 에서 정리한 "부르는 시점에 그 타입의 객체가 손에 있느냐"입니다. `toEntity()` 가 `cno` 를 안 담는 것도 같은 사정입니다 — 번호를 `CategoryEntity` 객체로 바꾸려면 리포지토리가 필요한데 DTO 는 그 층을 모릅니다.

`CategoryDto` 에는 `List<ReviewsDto> reviewDto` 가 `@Builder.Default` 로 붙어 있습니다. 리뷰(`rno`·`bno`·`reviewer`·`content`·`rating`)는 아직 엔티티가 없어 DTO 만 자리를 잡아 둔 상태입니다. 다음 수업에서 리뷰 표가 상품에 붙을 자리로 읽힙니다.

### 1-5. 리포지토리 — 빈 몸통 그대로

```java
@Repository
public interface ProductsRepository
        extends JpaRepository<ProductsEntity, Integer> {
}
```

제네릭 두 자리(엔티티, PK 타입)만 바꾸면 `findAll`·`save`·`findById`·`deleteById` 가 그대로 따라옵니다. PK 를 `Integer` 로 두었으므로 두 번째 자리도 `Integer` 입니다. 이 층이 주는 도구는 여전히 넷뿐이고, 그 조합으로 안 되는 일은 서비스 몫입니다.

### 1-6. 서비스 — 연관 엔티티를 따라가 응답을 조립하기

```java
@Service
public class ProductsService {
    @Autowired
    private ProductsRepository productsRepository;

    public List<ProductResponseDto> productFindAll() {
        List<ProductsEntity> productsEntities = productsRepository.findAll();
        List<ProductResponseDto> productResponseDtos = new ArrayList<>();

        productsEntities.forEach((productsEntity) -> {
            ProductResponseDto productResponseDto = ProductResponseDto.from(productsEntity);
            // 상품 → 카테고리 → 그 카테고리의 상품 목록 …
            productsEntity.getCategoryEntity().getProductList().forEach((productList) -> {
                CategoryDto categoryDto = CategoryDto.from(productList);
                …
            });
        });
        …
    }
}
```

조회 흐름의 뼈대는 익숙합니다. `findAll()` 로 엔티티 목록을 받고, 하나씩 `from()` 으로 응답 DTO 로 바꿔 새 목록에 담습니다. 여기에 이번에 얹힌 것이 **점(`.`)으로 연관 엔티티를 따라가는 자리**입니다.

`productsEntity.getCategoryEntity()` 로 상품에서 카테고리로 건너가고, 거기서 `getName()` 을 꺼내 `cName` 에 채우면 응답이 평평해집니다. 화면은 중첩된 객체가 아니라 `{ bno, name, price, cno, cName }` 한 층짜리 JSON 을 받습니다. 연관 엔티티를 DTO 로 펴는 day07 의 정리가 상품 도메인에서 되풀이되는 자리입니다.

`getCategoryEntity()` 를 부르는 순간 무슨 일이 생기는지는 짚어 둘 만합니다. `@ManyToOne` 은 기본이 즉시 로딩(EAGER)이라 `findAll()` 때 카테고리도 함께 조인되어 옵니다. 반대로 `getProductList()` 처럼 `@OneToMany` 쪽 목록은 기본이 지연 로딩(LAZY)이라, **그 목록을 건드리는 순간 카테고리마다 추가 쿼리**가 나갑니다. 상품이 N 개면 목록 조회 1번 + 카테고리별 상품 목록 조회가 따라붙는 자리이고, 이것이 여러 노트에서 이름만 나왔던 1+N 이 실제로 생기는 코드 모양입니다.

| 부르는 것 | 기본 페치 | 쿼리 |
| --- | --- | --- |
| `product.getCategoryEntity()` | EAGER (`@ManyToOne`) | 이미 조인되어 있음 |
| `category.getProductList()` | LAZY (`@OneToMany`) | 그 순간 카테고리마다 1번씩 |

응답에 필요한 것이 카테고리 **이름** 하나라면 `getCategoryEntity().getName()` 까지만 가면 됩니다. 목록까지 내려가는 순간 쿼리 수가 달라지므로, 서비스에서 점을 몇 칸까지 따라갈지는 "응답에 뭐가 필요한가"로 정하는 편이 안전합니다.

### 1-7. 컨트롤러 — CRUD 넷과 `@CrossOrigin`

```java
@CrossOrigin(value = "http://localhost:5173")
@RestController
@RequestMapping("api/products")
public class ProductsController {
    private final ProductsService productsService;

    ProductsController(ProductsService productsService) {
        this.productsService = productsService;
    }

    @GetMapping("")     public List<ProductResponseDto> productFindAll() { … }
    @PostMapping("")    public boolean productSave(@RequestBody ProductDto productDto) { … }
    @PutMapping("")     public boolean productUpdate(@RequestBody ProductDto productDto) { … }
    @DeleteMapping("")  public boolean productDelete(@RequestParam(name = "bno") Integer bno) { … }
}
```

주소 하나(`/api/products`)에 방식 넷으로 CRUD 를 가르는 배치, 등록·수정은 `@RequestBody`·삭제는 `@RequestParam` 으로 받는 갈림, 컨트롤러 본문이 서비스 호출 한 줄로 끝나는 모양 — 전부 day04·day08 에서 굳힌 그대로입니다. 생성자 주입(`final` + 생성자)으로 서비스를 받는 것도 같습니다.

새로 붙은 것은 맨 위 `@CrossOrigin(value = "http://localhost:5173")` 입니다. `5173` 은 **Vite 개발 서버의 기본 포트**입니다. 지금까지 화면은 `resources/static` 에 두어 서버(8080)가 직접 내보냈으므로 화면과 API 의 출처(origin)가 같았습니다. 이번엔 화면이 리액트 프로젝트(`2026_React`)에서 따로 돌고, 거기서 8080 의 API 를 부르는 구조입니다.

브라우저는 출처가 다른 곳으로의 요청을 기본적으로 막습니다(동일 출처 정책). 서버가 응답 헤더로 "이 출처는 허용한다"고 알려 줘야 하고, `@CrossOrigin` 이 그 헤더를 붙여 줍니다.

| 항목 | 정리 |
| --- | --- |
| 출처(origin) | 프로토콜 + 호스트 + 포트. `localhost:5173` 과 `localhost:8080` 은 다른 출처 |
| 막는 쪽 | 서버가 아니라 **브라우저**. `curl` 이나 포스트맨은 걸리지 않는다 |
| `@CrossOrigin(value = …)` | 그 출처에서 온 요청을 허용한다고 응답 헤더로 알린다 |
| 붙이는 자리 | 클래스(컨트롤러 전체) 또는 메소드 하나 |

`value` 를 비우면 모든 출처를 허용하는데, 개발 중에는 편하지만 공개 서버에서는 좁혀 두는 편이 안전합니다. 리액트 쪽에서 `axios.get('http://localhost:8080/api/products')` 처럼 절대주소로 부르게 되고, day02 에서 이름만 정리했던 CORS 가 실제로 걸리는 첫 자리입니다.

### 1-8. 카테고리 계층 한 벌 더 세우기 (수업 이어서 추가된 부분)

위까지가 상품 한 갈래였다면, 이어진 수업에서 **카테고리 쪽 세 층**(리포지토리 → 서비스 → 컨트롤러)이 같은 모양으로 붙었습니다. 리액트 실습의 `CategoryManager` 가 부르는 `/api/categories` 가 바로 이 자리입니다.

```java
@Repository
public interface CategoryRepository extends JpaRepository<CategoryEntity, Integer> { }

@Service
public class CategoryService {
    @Autowired
    private CategoryRepository categoryRepository;

    public CategoryDto save(CategoryDto categoryDto) {
        CategoryEntity saved = categoryRepository.save(categoryDto.toEntity());
        if (saved.getCno() >= 1) return categoryDto;
        return null;
    }
    public List<CategoryDto> findAll() {
        return categoryRepository.findAll().stream().map(CategoryDto::from).toList();
    }
    public boolean delete(Integer cno) {
        Optional<CategoryEntity> optional = categoryRepository.findById(cno);
        if (optional.isPresent()) { categoryRepository.deleteById(cno); return true; }
        return false;
    }
}

@RestController
@RequestMapping("/api/categories")
@CrossOrigin(value = "http://localhost:5173")
public class CategoryController {
    @Autowired
    private CategoryService categoryService;

    @PostMapping("")   public CategoryDto save(@RequestBody CategoryDto dto) { … }
    @GetMapping("")    public List<CategoryDto> findAll() { … }
    @DeleteMapping("") public boolean delete(@RequestParam(name = "cno") Integer cno) { … }
}
```

카테고리는 등록·목록·삭제 셋뿐이고 수정이 없습니다. 이름 하나뿐인 표라 고칠 것이 없고, 화면(`CategoryManager`)도 그 셋만 씁니다. 세 층에서 새로 짚을 것은 다음 세 가지입니다.

| 자리 | 정리 |
| --- | --- |
| `findAll()` 이 스트림 한 줄 | `findAll().stream().map(CategoryDto::from).toList()` — day08 메소드 레퍼런스가 실제 서비스에 쓰인 첫 자리. `from()` 이 `static` 이라 `클래스::정적메소드` 로 붙는다 |
| 저장 성공 판정 | `save()` 가 돌려준 엔티티의 `cno` 가 `1` 이상이면 성공. PK 가 `IDENTITY` 라 저장 직후 번호가 채워지는 것을 판정에 쓴다 |
| 삭제 전 `findById` | 없는 번호에 `deleteById` 를 부르면 예외가 나므로, `Optional.isPresent()` 로 한 번 거른 뒤 지운다 |

응답 타입이 `boolean` 이 아니라 **받은 DTO 를 그대로 되돌려 주는** 것도 상품 등록과 같은 모양입니다. 화면은 등록 뒤 목록을 다시 받아오므로 응답에 번호까지 실리지 않아도 흐름은 이어집니다.

`cascade = CascadeType.ALL` 이 여기서 실제로 작동합니다. 카테고리를 `deleteById` 로 지우면 딸린 상품이 같이 지워지고, 그래서 화면에서 카테고리 하나를 지우면 그 카테고리의 상품 줄이 목록에서 함께 사라집니다.

### 1-9. 상품 서비스의 CRUD 채우기

상품 서비스도 조회만 있던 자리에 등록·수정·삭제가 채워졌습니다. 조회 쪽은 응답 DTO 의 이름 필드가 `categoryname` 으로 잡혔고, `from()` 이 상품 세 필드만 옮기므로 카테고리 번호·이름은 **서비스가 setter 로 덧붙이는** 모양입니다.

```java
// 1. 조회 — from() 뒤에 연관 엔티티 값 두 개를 덧붙인다
ProductResponseDto dto = ProductResponseDto.from(productsEntity);
dto.setCno(productsEntity.getCategoryEntity().getCno());
dto.setCategoryname(productsEntity.getCategoryEntity().getName());

// 3. 수정 — 영속 엔티티를 꺼내 필드를 바꾸고 save()
Optional<ProductsEntity> optional = productsRepository.findById(productDto.getBno());
if (optional.isPresent()) {
    ProductsEntity entity = optional.get();
    entity.setName(productDto.getName());
    entity.setPrice(productDto.getPrice());
    productsRepository.save(entity);
    return true;
}
return false;

// 4. 삭제 — findById 로 거른 뒤 delete(entity)
```

| 메소드 | 뼈대 | 돌려주는 것 |
| --- | --- | --- |
| `productSave` | `toEntity()` → `save()` → `getBno() >= 1` | 받은 `ProductDto` 또는 `null` |
| `productUpdate` | `findById` → `isPresent` → setter → `save()` | `boolean` |
| `productDelete` | `findById` → `isPresent` → `delete(entity)` | `boolean` |

수정·삭제는 `findById` 로 먼저 꺼내는 것이 공통입니다. 없는 번호를 거르는 동시에, 수정 쪽은 그렇게 꺼낸 **영속 상태 엔티티**의 필드만 바꾸므로 day05 에서 정리한 변경 감지가 붙을 자리이기도 합니다(지금은 `save()` 를 명시적으로 부르고 있습니다).

연관 관계를 수정할 때 일반적으로 짚어 둘 점 하나. 상품이 속한 카테고리를 옮기는 일은 상품 쪽 **참조를 갈아끼우는** 일이라, `categoryRepository.findById(cno)` 로 목표 카테고리 엔티티를 꺼내 `setCategoryEntity(...)` 에 넣는 방향이 안전합니다. 연관 객체를 타고 들어가 그 객체의 PK 값을 바꾸는 것은 상대 표의 행을 건드리는 일이 되므로 구분해 두어야 합니다. 그래서 상품 서비스가 카테고리 리포지토리를 함께 드는 순간이 옵니다(→ 2-3).

## 2. 추가로 알면 좋은 활용법

### 2-1. 응답 DTO 를 나누는 기준

한 DTO 를 겸용하다가 갈라야 하는 신호는 대체로 셋입니다.

- 응답에는 있고 요청에는 없어야 하는 값이 생긴다 (`cName` 처럼 서버가 계산해 붙이는 값, 작성일 같은 감사 필드)
- 요청에는 있고 응답에는 없어야 하는 값이 생긴다 (비밀번호)
- 같은 엔티티인데 화면마다 필요한 모양이 다르다 (목록용은 짧게, 상세용은 길게)

이름은 `ProductRequestDto` / `ProductResponseDto` 처럼 방향을 접미사로 두는 관용이 흔합니다. 이번 코드처럼 받는 쪽만 접미사 없이 `ProductDto` 로 두어도 되지만, 갈래가 더 늘면 방향이 이름에 드러나는 편이 읽기 좋습니다.

### 2-2. `cName` 을 채우는 가장 짧은 표기

`from()` 안에서 연관 엔티티까지 함께 펴 두면 서비스가 짧아집니다.

```java
public static ProductResponseDto from(ProductsEntity entity) {
    return ProductResponseDto.builder()
            .bno(entity.getBno())
            .name(entity.getName())
            .price(entity.getPrice())
            .cno(entity.getCategoryEntity().getCno())
            .cName(entity.getCategoryEntity().getName())
            .build();
}
```

그러면 서비스는 스트림 한 줄이 됩니다.

```java
return productsRepository.findAll().stream()
        .map(ProductResponseDto::from)
        .toList();
```

day08 의 메소드 레퍼런스 정리대로 `from()` 이 `static` 이라 `클래스::정적메소드` 모양이 그대로 성립합니다. 다만 카테고리가 비어 있을 수 있는 도메인이면 `getCategoryEntity()` 가 `null` 을 돌려 `NullPointerException` 이 나므로, 그 경우는 `from()` 안에서 한 번 걸러 두어야 합니다.

### 2-3. 번호로 받은 카테고리를 객체로 바꿔 저장하기

등록에서 `ProductDto` 의 `cno` 를 엔티티에 끼우는 순서는 day08 댓글 등록과 같습니다.

```java
public boolean productSave(ProductDto dto) {
    CategoryEntity category = categoryRepository.findById(dto.getCno())
            .orElse(null);
    if (category == null) return false;          // 없는 카테고리 번호
    ProductsEntity entity = dto.toEntity();
    entity.setCategoryEntity(category);           // 번호 → 객체
    return productsRepository.save(entity).getBno() != null;
}
```

카테고리 리포지토리가 하나 더 필요해집니다. 서비스가 이웃 표의 리포지토리를 함께 드는 것은 "서비스의 단위는 표 하나가 아니라 하나의 일"이라 정리했던 그대로이고, 조회와 저장 사이의 틈이 `@Transactional` 을 붙일 자리입니다.

### 2-4. 목록 조회에서 1+N 을 피하는 두 갈래

카테고리 이름만 필요한데 `getProductList()` 까지 따라가면 쿼리가 늘어납니다. 필요한 만큼만 점을 따라가는 것이 첫째이고, 정말 목록까지 필요하면 리포지토리 쪽에서 한 번에 가져오는 갈래가 있습니다.

```java
@Query("select p from ProductsEntity p join fetch p.categoryEntity")
List<ProductsEntity> findAllWithCategory();
```

`join fetch` 는 연관 엔티티를 같은 쿼리로 함께 실어 오라는 JPQL 표기입니다. `@ManyToOne` 은 기본 EAGER 라 이 예제에서는 없어도 조인되지만, 실무에서는 `@ManyToOne(fetch = FetchType.LAZY)` 로 바꿔 두고 필요한 조회에서만 `join fetch` 를 쓰는 편이 관용입니다.

### 2-5. `@CrossOrigin` 을 한 곳에서 관리하기

컨트롤러마다 `@CrossOrigin` 을 붙이면 허용 출처가 흩어집니다. 설정 클래스 한 곳에서 묶는 갈래가 있습니다.

```java
@Configuration
public class WebConfig implements WebMvcConfigurer {
    @Override
    public void addCorsMappings(CorsRegistry registry) {
        registry.addMapping("/api/**")
                .allowedOrigins("http://localhost:5173")
                .allowedMethods("GET", "POST", "PUT", "DELETE");
    }
}
```

허용 출처가 바뀌면 이 파일 한 곳만 고치면 됩니다. 컨트롤러가 늘어나는 시점에 옮겨 두면 좋은 자리입니다.

## 3. 더 나아가 알면 좋은 것

### 3-1. 화면이 따로 도는 구조가 바꾸는 것

화면을 `static` 에 두던 배치에서 리액트 개발 서버로 떼어 내면 달라지는 것이 몇 가지 있습니다.

| | `static` 에 화면 | 리액트 개발 서버 |
| --- | --- | --- |
| 출처 | API 와 같음 | 다름 → CORS |
| 화면 주소 | `/day09/index.html` | `http://localhost:5173/…` |
| API 주소 표기 | 상대주소 `/api/…` | 절대주소 또는 프록시 |
| 배포 | jar 하나 | 빌드 결과물을 따로 두거나 `static` 으로 복사 |

개발 중에는 `@CrossOrigin` 이나 Vite 의 `server.proxy` 설정(`/api` 를 8080 으로 넘기기) 둘 중 하나를 쓰고, 배포 때는 리액트 빌드 결과물(`dist/`)을 `resources/static` 에 넣어 출처를 다시 합치는 갈래가 흔합니다. 프록시를 쓰면 화면 코드가 상대주소 그대로라 배포 때 고칠 것이 줄어듭니다.

### 3-2. 응답 DTO 가 늘어나면 따라오는 것

응답 전용 DTO 가 생기면 엔티티 → DTO 변환이 화면마다 갈립니다. `from()` 을 DTO 마다 손으로 적는 것이 지금 방식이고, 변환이 많아지면 MapStruct 같은 매핑 도구가 컴파일 시점에 그 코드를 만들어 줍니다. 롬복이 생성자·getter 를 만들어 주던 것과 같은 자리(애노테이션 프로세서)입니다.

또 응답 DTO 는 값이 바뀌지 않아도 되므로 `record` 로 두는 갈래가 어울립니다. day08 에서 정리한 "DTO 는 되고 엔티티는 안 되는" 갈림이 응답 쪽에서 특히 잘 맞습니다.

### 3-3. 리뷰 표가 붙을 자리

`ReviewsDto` 가 미리 자리를 잡아 둔 리뷰는 상품에 `@OneToMany` 로 붙을 갈래입니다. 그러면 상품 상세 응답은 카테고리 이름(위로 한 칸) + 리뷰 목록(아래로 한 칸)을 함께 담게 되고, 카테고리 → 상품 → 리뷰 세 층이 됩니다. 목록 조회에서 리뷰까지 실으면 1+N 이 두 겹이 되므로, 목록은 짧게·상세만 길게 나누는 응답 DTO 분리가 여기서 값어치를 냅니다.

### 3-4. 다음에 볼 키워드

- `FetchType.LAZY` / `EAGER` — `@ManyToOne` 기본값을 바꾸는 이유와 `LazyInitializationException`
- `join fetch` · `@EntityGraph` — 연관 엔티티를 한 쿼리로 함께 실어 오기
- `@Transactional(readOnly = true)` — 조회 서비스에서 지연 로딩 구간을 열어 두기
- `WebMvcConfigurer.addCorsMappings` · Vite `server.proxy` — CORS 를 한 곳에서 다루기
- `ResponseEntity` · `@ResponseStatus` — `boolean` 대신 상태 코드로 결과 알리기
- `@Valid` · `@NotNull` · `@Min` — 요청 DTO 에서 값 검증하기
- MapStruct · `record` — 변환 코드 줄이기와 불변 응답 DTO

## 실습 파일

- `2026B_Spring/springweb/src/main/java/day10/AppStart.java` (**진입점** — `@SpringBootApplication` 이 붙은 패키지가 컴포넌트 스캔의 뿌리라 `day10` 아래만 이 진입점으로 뜨는 배치)
- `2026B_Spring/springweb/src/main/java/day10/model/entity/ProductsEntity.java` (**"다" 쪽 엔티티** — `@Table(name = "product")` 로 클래스 이름과 표 이름을 따로 두는 자리, `@ManyToOne` + `@JoinColumn(name = "cno")` 로 외래키 컬럼을 이쪽 표에 두고 자바에서는 객체로 드는 구조, PK 를 `Integer` 로 두어 저장 전 `null` 을 담는 점)
- `2026B_Spring/springweb/src/main/java/day10/model/entity/CategoryEntity.java` (**"일" 쪽 엔티티** — `@OneToMany(mappedBy = "categoryEntity")` 의 값이 상대 필드 이름이고 외래키 주인은 저쪽이라는 표시, `cascade = CascadeType.ALL` 이 저장·삭제를 상품까지 번지게 하는 점, `@ToString.Exclude` 가 `@Data` 의 `toString` 순환을 끊는 자리, `@Builder.Default` 가 없으면 빌더 경로에서 목록이 `null` 이 되는 사정)
- `2026B_Spring/springweb/src/main/java/day10/model/dto/ProductDto.java` (**받는 DTO** — 카테고리를 `cno` 번호로만 받는 이유, `toEntity()` 가 `cno` 를 담지 않는 것이 층 경계인 점)
- `2026B_Spring/springweb/src/main/java/day10/model/dto/ProductResponseDto.java` (**내보내는 DTO** — `cName` 하나가 더 있어 화면이 카테고리 이름을 따로 맞추지 않아도 되는 자리, `from()` 이 `static` 인 이유)
- `2026B_Spring/springweb/src/main/java/day10/model/dto/CategoryDto.java` (`List<ReviewsDto>` 를 `@Builder.Default` 로 잡아 둔 자리)
- `2026B_Spring/springweb/src/main/java/day10/model/dto/ReviewsDto.java` (아직 엔티티가 없는 리뷰의 자리 — `rno`·`bno`·`reviewer`·`content`·`rating`)
- `2026B_Spring/springweb/src/main/java/day10/model/repository/ProductsRepository.java` (`JpaRepository<ProductsEntity, Integer>` 빈 몸통)
- `2026B_Spring/springweb/src/main/java/day10/service/ProductsService.java` (**응답 조립** — `findAll()` 결과를 `from()` 으로 바꾸며 `getCategoryEntity()` 로 연관 엔티티를 따라가 응답을 평평하게 만드는 자리, `@ManyToOne` 은 EAGER 라 이미 조인되어 있고 `@OneToMany` 목록은 LAZY 라 건드리는 순간 카테고리마다 쿼리가 나가는 1+N 의 실제 모양)
- `2026B_Spring/springweb/src/main/java/day10/controller/ProductsController.java` (**CRUD 넷과 CORS** — 주소 하나에 방식 넷, 등록·수정은 `@RequestBody`·삭제는 `@RequestParam`, 생성자 주입, `@CrossOrigin("http://localhost:5173")` 이 Vite 개발 서버에서 오는 요청을 허용하는 헤더를 붙이는 자리와 막는 쪽이 서버가 아니라 브라우저인 점)
- `2026B_Spring/springweb/src/main/java/day10/model/repository/CategoryRepository.java` (`JpaRepository<CategoryEntity, Integer>` 빈 몸통 — 상품 쪽과 제네릭 두 자리만 다르다)
- `2026B_Spring/springweb/src/main/java/day10/service/CategoryService.java` (**카테고리 등록·목록·삭제** — `findAll().stream().map(CategoryDto::from).toList()` 로 메소드 레퍼런스가 서비스에 실제 쓰인 자리, 저장 성공을 `getCno() >= 1` 로 판정, 삭제 전 `findById` + `isPresent()` 로 거르는 뼈대)
- `2026B_Spring/springweb/src/main/java/day10/controller/CategoryController.java` (`/api/categories` 에 POST·GET·DELETE 셋 — 수정이 없는 이유, 리액트 `CategoryManager` 가 부르는 주소, 같은 `@CrossOrigin`)
- `2026B_Spring/springweb/src/main/java/day10/service/ProductsService.java` — 추가분 (**상품 CRUD 채움** — 조회에서 `from()` 뒤 `setCno`·`setCategoryname` 으로 연관 값을 덧붙이는 모양, 수정·삭제가 `findById` → `isPresent` 로 시작하는 공통 뼈대, 연관 참조를 옮길 때는 상대 엔티티를 꺼내 `setCategoryEntity` 로 갈아끼우는 방향)

## 관련 노트

[[Spring MOC]] · [[Spring day09 화면 쪽 자바스크립트 기초 다시 훑기]] · [[Spring day10 리뷰 도메인과 쿼리 메소드로 자식 목록 받기]] · [[KDT_2026 학습 지도]]
