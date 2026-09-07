---
출처: Claude 분석
원본: KDT_2026/2026B_Spring/springweb/src/main/java/day06/activity/RecipeEntity.java, springweb/src/main/java/day06/activity/MenuEntity.java, springweb/src/main/java/day06/activity/ProductEntity.java, springweb/src/main/resources/sql/sample.sql
작성일: 2026-09-04
tags: [학습, java]
---

# Spring day06 — 중간 엔티티로 푼 다대다

> 실습 파일: `2026B_Spring/springweb/src/main/java/day06/activity/RecipeEntity.java`, `activity/MenuEntity.java`, `activity/ProductEntity.java`, `resources/sql/sample.sql`
> 허브: [[Spring MOC]] · 이전: [[Spring day06 양방향 참조와 순환참조]] · 다음: [[Spring day07 상태를 가진 중간 엔티티]]

앞에서 재료와 입출고 기록을 1:N으로 잇고, 메뉴와 레시피는 목록 필드가 없는 껍데기로 자리만 잡아 뒀다. **이번은 그 껍데기를 채우면서 앞의 1:N으로는 안 되는 관계 하나를 만나는 자리다.**

버거 가게 도메인에서 메뉴와 재료의 관계를 세어 보면 이렇다.

| 물음 | 답 |
| --- | --- |
| 치즈버거 하나에 재료가 몇 개 들어가나 | 여러 개 (빵·패티·치즈·양상추…) |
| 빵 하나는 몇 개의 메뉴에 들어가나 | 여러 개 (거의 모든 버거) |

양쪽 다 "여러"다. 지금까지 쓴 `@ManyToOne` + `@OneToMany` 한 벌은 한쪽이 "하나"여야 성립하므로 이 관계에는 그대로 안 얹힌다. **외래키는 컬럼 하나이고, 컬럼 하나에 여러 번호를 담을 방법이 없기 때문이다.**

## 1. 배운 내용

### 1-1. 다대다는 표를 하나 더 두어 푼다

메뉴 표에 재료 번호를 담을 수도 없고 재료 표에 메뉴 번호를 담을 수도 없으니, **두 번호를 함께 담는 표를 하나 더 둔다.** 여기서는 `recipe` 표가 그 자리다.

```
menu ──1:N──▶ recipe ◀──N:1── product
        menu_no        product_no
```

가운데 표에서 보면 관계가 둘 다 N:1이 된다. 메뉴 하나에 레시피 줄이 여럿, 재료 하나에도 레시피 줄이 여럿이고, 레시피 한 줄은 메뉴 하나와 재료 하나를 가리킨다. **다대다를 1:N 둘로 갈라 놓은 모양이다.**

| 표 | 담는 것 |
| --- | --- |
| `menu` | 메뉴 자체의 정보 (이름·가격) |
| `product` | 재료 자체의 정보 (이름·단가) |
| `recipe` | 어느 메뉴에 어느 재료가 들어가는가 |

앞 노트에서 `@ManyToMany` 가 중간 표를 자동으로 만들어 준다는 것과 그 표에 컬럼을 더할 수 없다는 뒷면을 적어 뒀는데, 여기서는 그 중간 표를 **엔티티로 직접 만든다.** → [[Spring day06 연관관계 매핑과 외래키]]

### 1-2. 중간 엔티티에는 `@ManyToOne` 이 둘

중간 엔티티는 양쪽을 다 가리키므로 외래키 표시를 두 벌 든다.

```java
@Entity
@Table(name = "recipe")
@NoArgsConstructor
@AllArgsConstructor
@Builder
@Data
public class RecipeEntity {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Integer recipe_no;

    @ManyToOne
    @JoinColumn(name = "product_no")
    @ToString.Exclude
    private ProductEntity productEntity;

    private Integer recipe_order;

    @ManyToOne
    @JoinColumn(name = "menu_no")
    @ToString.Exclude
    private MenuEntity menuEntity;
}
```

붙는 표시는 지금까지 쓰던 것과 하나도 다르지 않다. **`@ManyToOne` + `@JoinColumn` 한 벌이 두 번 반복될 뿐이다.** 관계가 늘어도 새로 외울 표시가 없다는 점이 여기서 한 번 더 확인된다.

`@JoinColumn` 에 적은 이름은 앞의 재료-기록 관계와 갈래가 갈린다.

| 관계 | 외래키 컬럼 이름 | 상대 PK 이름 |
| --- | --- | --- |
| 기록 → 재료 | `product_id` | `product_no` |
| 레시피 → 재료 | `product_no` | `product_no` |
| 레시피 → 메뉴 | `menu_no` | `menu_no` |

둘 다 동작하므로 **어느 쪽이 옳다기보다 한 프로젝트 안에서 규칙을 하나로 정해 두는 편이 낫다.** 이름을 상대 PK와 같게 두면 시드 SQL이나 조인문을 적을 때 어느 컬럼이 어디를 가리키는지 바로 읽힌다.

### 1-3. 중간 엔티티가 있어야 담을 수 있는 것

`recipe` 표에는 두 외래키 말고 컬럼이 하나 더 있다.

```java
private Integer recipe_order;
```

레시피에서 재료를 넣는 **순서**다. 빵 → 소스 → 패티 → 치즈처럼 순서가 뜻을 갖는 도메인이라 관계 자체에 딸린 정보가 된다.

**이 컬럼 하나가 `@ManyToMany` 대신 중간 엔티티를 만드는 가장 실질적인 이유다.** `@ManyToMany` 는 두 번호만 담은 표를 만들어 주고 그 표에 컬럼을 더할 통로가 없다. 관계에 딸린 정보가 하나라도 생기면 그 순간 중간 엔티티로 갈아야 한다.

| 담고 싶은 것 | `@ManyToMany` | 중간 엔티티 |
| --- | --- | --- |
| 어느 것과 어느 것이 이어지나 | 가능 | 가능 |
| 순서·수량·단가 같은 관계의 속성 | 불가 | 가능 |
| 언제 이어졌나 (감사 필드) | 불가 | 가능 |

관계에 속성이 붙기 시작하면 그것은 이미 "이어져 있다"가 아니라 **하나의 사실**이다. 레시피 한 줄은 "이 메뉴의 몇 번째에 이 재료가 들어간다"라는 사실이라, 표 하나를 차지할 자격이 있다.

### 1-4. 양쪽에서 목록 열기

껍데기로 두었던 메뉴 엔티티에 레시피 목록을 채운다. 앞에서 쓴 세 표시 한 벌이 그대로 온다.

```java
@Entity
@Table(name = "menu")
public class MenuEntity extends BaseTime {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Integer menu_no;

    @Column(length = 50)
    private String menu_name;

    private Integer menu_price;

    @OneToMany(mappedBy = "menuEntity")
    @ToString.Exclude
    @Builder.Default
    private List<RecipeEntity> recipeList = new ArrayList<>();
}
```

재료 쪽도 같은 목록을 하나 더 연다. 이쪽은 입출고 기록 목록이 이미 있으므로 `@OneToMany` 가 둘이 된다.

```java
@OneToMany(mappedBy = "productEntity")
@ToString.Exclude
@Builder.Default
private List<ProductLogEntity> productLogList = new ArrayList<>();

@OneToMany(mappedBy = "productEntity")
@ToString.Exclude
@Builder.Default
private List<RecipeEntity> recipeList = new ArrayList<>();
```

`mappedBy` 값이 둘 다 `productEntity` 인데 문제가 없다. **`mappedBy` 는 "상대 엔티티에 있는 필드 이름"이라, 상대가 다르면 같은 문자열이어도 서로 다른 관계를 가리킨다.** 위쪽은 `ProductLogEntity.productEntity` 를, 아래쪽은 `RecipeEntity.productEntity` 를 뜻한다. 어느 상대인지는 문자열이 아니라 **목록의 제네릭 타입**이 정한다.

이 배치로 재료 엔티티는 관계 둘의 "일" 쪽을 동시에 맡는다. 앞 노트에서 게시글 엔티티가 위아래로 다른 역할을 맡았던 것과는 모양이 다르다.

| 엔티티 | 맡는 역할 |
| --- | --- |
| `BoardEntity` (앞 노트) | 위로 "다", 아래로 "일" — 방향이 갈린다 |
| `ProductEntity` (여기) | 아래로 "일"이 둘 — 같은 역할이 겹친다 |

**표시 한 벌을 몇 번 반복하느냐의 문제일 뿐, 새 규칙이 생기지는 않는다.**

### 1-5. 짝이 맞아야 관계가 성립한다

앞 노트에서 껍데기로 남겨 뒀던 자리가 이번에 채워지면서 `mappedBy` 의 짝이 처음으로 완성된다.

| 여는 쪽 | `mappedBy` 값 | 짝이 되는 필드 |
| --- | --- | --- |
| `MenuEntity.recipeList` | `"menuEntity"` | `RecipeEntity.menuEntity` |
| `ProductEntity.recipeList` | `"productEntity"` | `RecipeEntity.productEntity` |
| `ProductEntity.productLogList` | `"productEntity"` | `ProductLogEntity.productEntity` |

**한쪽만 적어 두면 문자열이 가리킬 자리가 없어 서버가 뜰 때 걸린다.** 컴파일은 지나가므로, 관계를 새로 열 때는 목록 쪽과 외래키 쪽을 한 번에 채우고 바로 띄워 보는 편이 안전하다.

### 1-6. 감사 필드를 어디에 둘지

이번 실습의 엔티티 넷을 놓고 보면 상속이 갈린다.

| 엔티티 | `extends BaseTime` |
| --- | --- |
| `MenuEntity` | 있음 |
| `ProductEntity` | 있음 |
| `ProductLogEntity` | 있음 |
| `RecipeEntity` | 없음 |

**연결만 담는 표에 만든 시각·고친 시각이 꼭 필요한지는 도메인이 정한다.** 레시피가 언제 바뀌었는지를 추적할 일이 있으면 상속을 걸고, 메뉴 구성이 거의 안 바뀌면 컬럼 둘을 아끼는 쪽으로 둔다. 상속을 거는 순간 시드 SQL에도 `create_date`·`update_date` 를 채우는 자리가 생기므로, **엔티티 쪽 결정이 시드 쪽으로 그대로 번진다.** → [[Spring day05 엔티티 제약과 감사 필드]]

### 1-7. 시드는 부모 둘을 먼저 채운다

중간 표의 시드는 앞의 1:N보다 조건이 하나 더 붙는다. 외래키가 둘이라 **부모가 둘 다 먼저 들어가 있어야 한다.**

```sql
INSERT INTO product (product_name, product_price, create_date, update_date) VALUES
('햄버거빵', 500, NOW(), NOW()),
('소고기패티', 1200, NOW(), NOW());

INSERT INTO menu (menu_name, menu_price, create_date, update_date) VALUES
('치즈버거', 5000, NOW(), NOW());

INSERT INTO recipe (menu_no, product_no, recipe_order) VALUES
(1, 1, 1),
(1, 4, 2),
(1, 2, 3);
```

`product` → `menu` → `recipe` 순서가 지켜져야 외래키 제약에 안 걸린다. **부모끼리는 순서가 상관없고, 자식만 둘 다 뒤에 오면 된다.**

`recipe` 쪽 `INSERT` 에 시각 컬럼이 없는 것은 이 엔티티가 `BaseTime` 을 상속하지 않아 그 컬럼이 표에 없기 때문이다. 시드 SQL은 만들어진 표를 그대로 따라가므로, **엔티티를 고치면 시드도 같이 봐야 한다.**

### 1-8. 중간 표의 열쇠를 무엇으로 둘까

중간 엔티티의 `@Id` 는 자기 번호 하나다.

```java
@Id
@GeneratedValue(strategy = GenerationType.IDENTITY)
private Integer recipe_no;
```

두 외래키를 묶어 복합키로 두는 갈래도 있는데, 이 도메인에서는 그쪽이 안 맞는다. 시드를 보면 같은 메뉴에 같은 재료가 두 번 들어가는 줄이 있다.

```sql
(1, 1, 1),   -- 치즈버거, 빵, 1번째
…
(1, 1, 5)    -- 치즈버거, 빵, 5번째
```

버거의 아래 빵과 위 빵이다. **`(menu_no, product_no)` 를 열쇠로 잡으면 이 두 줄이 같은 열쇠가 되어 들어가지 못한다.** 순서가 다르면 다른 줄이라는 도메인의 사정이 열쇠 설계로 그대로 이어진다.

| 열쇠 방식 | 성립 조건 |
| --- | --- |
| 복합키 `(menu_no, product_no)` | 같은 짝이 한 번만 나온다 |
| 복합키 `(menu_no, product_no, recipe_order)` | 순서까지 넣어야 유일해진다 |
| 대리키 `recipe_no` | 조건 없이 언제나 성립 |

**중간 표에 대리키를 두는 것이 편한 이유가 여기 있다.** 관계에 속성이 붙어 같은 짝이 여러 번 나올 수 있으면 자연키만으로는 줄을 구분하지 못한다. 대리키는 도메인 사정과 무관하게 줄 하나를 가리키므로, 나중에 조건이 바뀌어도 열쇠를 다시 설계할 일이 없다.

## 2. 추가로 알면 좋은 활용법

### 2-1. 중간 엔티티를 거쳐 반대편까지 가기

목록을 두 번 타고 들어가면 메뉴에서 재료까지 닿는다.

```java
menu.getRecipeList()
    .forEach(r -> System.out.println(r.getProductEntity().getProduct_name()));
```

중간 엔티티가 가운데 끼어 있어 한 칸이 더 늘었다. `@ManyToMany` 였다면 `menu.getProductList()` 한 번으로 끝날 자리인데, **관계의 속성을 담는 대가로 한 칸을 더 타고 가는 셈이다.**

쓰는 쪽 코드를 짧게 두고 싶으면 엔티티에 메소드를 하나 두어 그 한 칸을 감춰 둔다.

```java
public List<ProductEntity> getProducts() {
    return recipeList.stream()
            .map(RecipeEntity::getProductEntity)
            .toList();
}
```

### 2-2. 순서를 담았으면 꺼낼 때도 순서대로

`recipe_order` 를 담아 뒀어도 목록을 그냥 읽으면 DB가 돌려주는 순서 그대로다. 순서를 보장하려면 적어 둔다.

```java
@OneToMany(mappedBy = "menuEntity")
@OrderBy("recipe_order ASC")
private List<RecipeEntity> recipeList = new ArrayList<>();
```

`@OrderBy` 는 조회 SQL에 `order by` 를 붙이는 표시라 정렬을 DB가 한다. 괄호 안에 적는 것은 컬럼 이름이 아니라 **상대 엔티티의 필드 이름**이라, `mappedBy` 와 같은 기준으로 읽는다.

### 2-3. 관계가 늘수록 조회가 늘어나는 자리

`@OneToMany` 는 지연 로딩이라 목록을 건드릴 때 그때 조회가 나간다. 중간 엔티티를 거치면 그 입구가 한 겹 더 생긴다.

```java
List<MenuEntity> menus = menuRepository.findAll();        // 1번
menus.forEach(m -> m.getRecipeList()                      // 메뉴 수만큼
        .forEach(r -> r.getProductEntity().getProduct_name()));  // 레시피 줄 수만큼
```

메뉴 10개에 레시피가 각 7줄이면 조회가 80번 가까이 나간다. 한 번에 읽어 오거나, 애초에 화면이 쓰는 모양까지만 꺼내는 조회를 따로 두는 편이 낫다.

```java
@Query("select m from MenuEntity m join fetch m.recipeList r join fetch r.productEntity")
List<MenuEntity> findAllWithProducts();
```

### 2-4. 응답에서는 관계를 평평하게 편다

엔티티를 그대로 내보내면 메뉴 → 레시피 → 재료 → 레시피로 순환에 빠진다. 중간 엔티티가 끼어 사슬이 길어졌을 뿐 구조는 앞과 같다. **화면이 실제로 쓰는 모양까지만 꺼내는 DTO로 바꿔 내보내면 이 문제가 애초에 없다.** → [[Spring day05 조회 흐름에 DTO 얹기]]

```java
public static MenuDto from(MenuEntity entity) {
    return MenuDto.builder()
            .menuName(entity.getMenu_name())
            .products(entity.getRecipeList().stream()
                    .sorted(Comparator.comparing(RecipeEntity::getRecipe_order))
                    .map(r -> r.getProductEntity().getProduct_name())
                    .toList())
            .build();
}
```

재료 이름 목록으로 펴 놓으면 응답에는 중간 엔티티가 아예 안 드러난다. 중간 엔티티는 **DB 쪽 사정이지 화면 쪽 사정이 아니라는 점**이 여기서 갈린다.

### 2-5. 원가를 세는 자리

관계에 속성이 붙으면 그 속성으로 계산을 할 수 있다. 메뉴 하나의 재료 원가를 세는 것이 그 예다.

```java
int cost = menu.getRecipeList().stream()
        .mapToInt(r -> r.getProductEntity().getProduct_price())
        .sum();
```

같은 재료가 두 번 들어가면 두 번 세어진다. `recipe` 가 줄 단위로 사실을 담고 있으므로 세는 쪽에서 따로 묶을 필요가 없다. **관계를 표로 꺼내 둔 값어치가 조회가 아니라 계산에서 나는 자리다.**

## 3. 더 나아가 알면 좋은 것

### 3-1. `@ManyToMany` 를 언제 고를 수 있나

거의 없다는 쪽이 실무의 답에 가깝다.

| 물음 | 답이 "예"면 |
| --- | --- |
| 관계에 담을 정보가 정말 없나 | `@ManyToMany` 도 가능 |
| 앞으로도 안 생길 것이 확실한가 | 그래도 중간 엔티티가 안전 |
| 중간 표를 직접 조회할 일이 없나 | — |

관계에 속성이 나중에 하나만 붙어도 표 구조를 바꿔야 하고, 그때는 이미 데이터가 쌓여 있다. **처음부터 중간 엔티티로 두면 그 이행이 없다.**

### 3-2. 다음에 볼 키워드

- `@IdClass`·`@EmbeddedId` 로 복합키 엔티티 만들기와 `equals`·`hashCode` 를 직접 맞춰야 하는 조건
- `@OrderBy` 와 `@OrderColumn` 의 갈림 — 정렬을 DB가 하나 목록의 위치를 표에 저장하나
- 중간 엔티티에 `cascade`·`orphanRemoval` 을 걸어 레시피 줄을 메뉴와 함께 지우기
- 컬렉션 `join fetch` 와 페이징이 부딪히는 자리, `@BatchSize` 로 완화하기
- 집계를 쿼리로 내리기 — `@Query` 에서 `sum`·`group by` 로 메뉴별 원가 세기
- 재고를 기록의 합으로 계산하는 방식과 현재값 컬럼을 따로 두는 방식의 손익
- 다대다가 세 개로 늘 때(메뉴-재료-매장) 중간 엔티티를 어떻게 쪼갤지
- 스네이크 필드명과 카멜 필드명을 한 프로젝트에서 섞지 않는 규칙 세우기

## 실습 파일

- `2026B_Spring/springweb/src/main/java/day06/activity/RecipeEntity.java` (**다대다를 1:N 둘로 가른 중간 엔티티** — 메뉴와 재료가 양쪽 다 "여러"라 외래키 컬럼 하나로는 못 담는 자리와 두 번호를 함께 담는 표를 하나 더 두어 푸는 방향·가운데 표에서 보면 양쪽이 다 N:1이 되는 구조, `@ManyToOne`+`@JoinColumn` 한 벌이 두 번 반복될 뿐 새로 외울 표시가 없는 점과 `@JoinColumn` 이름을 상대 PK와 같게 두는 갈래·다르게 두는 갈래의 대비와 한 프로젝트 안에서 규칙을 하나로 정하는 편이 나은 이유, `recipe_order` 처럼 관계에 딸린 속성 하나가 `@ManyToMany` 대신 중간 엔티티를 만드는 가장 실질적인 이유가 되는 자리와 관계에 속성이 붙으면 그것은 이미 하나의 사실이라 표를 차지할 자격이 있다는 정리, 두 외래키를 묶은 복합키가 같은 짝이 여러 번 나오는 도메인에서는 성립하지 않는 자리와 대리키를 두면 도메인 사정과 무관하게 줄 하나를 가리켜 조건이 바뀌어도 열쇠를 다시 설계할 일이 없는 점, 연결만 담는 표에 감사 필드를 둘지는 도메인이 정하고 그 결정이 시드 SQL 쪽으로 그대로 번지는 자리)
- `2026B_Spring/springweb/src/main/java/day06/activity/MenuEntity.java` (**껍데기로 두었던 자리에 목록 채우기** — `@OneToMany(mappedBy=…)`+`@ToString.Exclude`+`@Builder.Default` 세 표시 한 벌이 그대로 오는 자리와 `mappedBy` 문자열이 상대 엔티티에 실제로 있는 필드 이름이라 한쪽만 적어 두면 서버가 뜰 때 걸리는 점·목록 쪽과 외래키 쪽을 한 번에 채우고 바로 띄워 보는 순서, `@Column(length=…)`·`@GeneratedValue(strategy=IDENTITY)` 가 관계를 든 엔티티에서도 그대로 쓰이는 자리)
- `2026B_Spring/springweb/src/main/java/day06/activity/ProductEntity.java` (**한 엔티티가 "일" 쪽을 둘 맡는 자리** — 입출고 기록 목록과 레시피 목록을 함께 들어 `@OneToMany` 가 둘이 되는 배치와 `mappedBy` 값이 둘 다 같은 문자열이어도 상대가 다르면 서로 다른 관계를 가리키는 점·어느 상대인지는 문자열이 아니라 목록의 제네릭 타입이 정한다는 기준, 앞 노트의 게시글 엔티티가 위아래로 다른 역할을 맡던 겹침과 같은 역할이 둘 겹치는 이 배치의 대비·표시 한 벌을 몇 번 반복하느냐의 문제일 뿐 새 규칙이 생기지 않는다는 확인)
- `2026B_Spring/springweb/src/main/resources/sql/sample.sql` (**외래키가 둘인 표의 시드** — 부모가 둘 다 먼저 들어가 있어야 하는 조건과 부모끼리는 순서가 상관없고 자식만 뒤에 오면 되는 점, 상속을 걸지 않은 엔티티의 시드에 시각 컬럼이 없는 자리와 시드 SQL은 만들어진 표를 그대로 따라가므로 엔티티를 고치면 시드도 같이 봐야 하는 점, 같은 메뉴에 같은 재료가 순서만 달리해 두 번 들어가는 줄이 복합키를 못 쓰게 만드는 실측)

## 관련 노트

[[Spring MOC]] · [[Spring day06 양방향 참조와 순환참조]] · [[Spring day07 상태를 가진 중간 엔티티]] · [[KDT_2026 학습 지도]]
