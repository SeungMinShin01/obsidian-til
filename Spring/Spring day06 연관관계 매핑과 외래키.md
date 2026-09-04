---
출처: Claude 분석
원본: KDT_2026/2026B_Spring/springweb/src/main/java/day06
작성일: 2026-09-04
tags: [학습, java]
---

# Spring day06 — 연관관계 매핑과 외래키

> 실습 파일: `2026B_Spring/springweb/src/main/java/day06/BoardEntity.java`, `CategoryEntity.java`
> 허브: [[Spring MOC]] · 이전: [[Spring day05 등록·수정 흐름과 변경 감지]]

day04·day05까지 다룬 엔티티는 전부 **표 하나가 혼자 서 있는** 모양이었다. `test` 한 표, `movie` 한 표, 각자 자기 컬럼만 갖고 서로를 모른다. 실제 DB에서 표는 그렇게 떨어져 있지 않고 외래키로 서로를 가리킨다. **이번은 표 둘 사이의 관계를 자바 코드로 옮기는 실습이다.**

지금까지의 방식이라면 게시글 표에 카테고리 번호를 담는 `Integer cno` 필드를 하나 두면 된다. 그런데 JPA에서는 그렇게 적지 않는다.

| | 지금까지 (JDBC 방식의 연장) | 이번 (연관관계 매핑) |
| --- | --- | --- |
| 필드 타입 | `Integer cno` — 번호 | `CategoryEntity category` — 객체 |
| 값을 꺼낼 때 | 번호로 다시 조회한다 | 필드를 타고 들어간다 |
| 표에 만들어지는 것 | `cno` 컬럼 | `cno` 컬럼 (같다) |

**표에 만들어지는 결과는 같은데 자바 쪽에서 다루는 모양이 갈린다.** 이것이 연관관계 매핑의 요점이다.

## 1. 배운 내용

### 1-1. 관계를 가진 표 두 벌 두기

카테고리와 게시판, 표 둘을 엔티티 둘로 둔다.

```java
@Entity
@Table(name = "category")
@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class BoardEntity {
    @Id
    private Integer cno;
    private String cname;
}
```

붙는 표시 한 벌은 day04·day05에서 굳어진 그대로다. `@Entity` 로 표와 짝짓고, `@Table(name=…)` 으로 표 이름을 지목하고, 롬복 넷(`@Data`·`@NoArgsConstructor`·`@AllArgsConstructor`·`@Builder`)으로 통로를 연다. → [[Spring day04 JPA 엔티티와 리포지토리]]

여기서 눈여겨볼 것은 **클래스 이름과 표 이름이 `@Table(name=…)` 으로 갈라져 있다는 점**이다. 이 속성이 있으면 클래스 이름이 무엇이든 괄호 안의 이름이 실제 표가 된다. 생략하면 클래스 이름을 스네이크로 바꾼 것이 표 이름이 된다. 둘이 어긋난 채로 있으면 코드만 봐서는 어느 표를 다루는 코드인지 헷갈리므로, 표를 기준으로 클래스 이름을 맞춰 두는 편이 나중에 읽기 편하다.

`@GeneratedValue` 가 없으면 번호를 DB가 아니라 넣는 쪽에서 정해 준다는 뜻이 된다. 카테고리처럼 미리 정해진 목록이면 그럴 수 있고, 계속 늘어나는 표라면 `@GeneratedValue(strategy = GenerationType.IDENTITY)` 를 붙여 `AUTO_INCREMENT` 에 맡긴다.

### 1-2. 외래키를 컬럼이 아니라 참조로 두기

관계를 갖는 쪽 엔티티에 상대 엔티티 타입의 필드를 둔다.

```java
@Entity
@Table(name = "board")
@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class CategoryEntity {
    @Id
    private Integer bno;
    private String bname;

    // 단방향 참조 FK
    @ManyToOne
    @JoinColumn(name = "cno")
    private CategoryEntity categoryEntity;
}
```

세 줄이 붙어 하나의 뜻을 만든다.

| 줄 | 하는 일 |
| --- | --- |
| `@ManyToOne` | 이 관계가 **다대일**이라고 알린다 (게시글 여럿 : 카테고리 하나) |
| `@JoinColumn(name = "cno")` | 만들어질 **외래키 컬럼의 이름**을 지목한다 |
| `private CategoryEntity …` | 필드 타입이 **가리키는 상대 엔티티**를 정한다 |

**관계의 방향은 필드 타입이 정하고, 관계의 개수는 `@ManyToOne` 이 정하고, 표에 남는 컬럼 이름은 `@JoinColumn` 이 정한다.** 셋 중 하나만 바꿔도 뜻이 달라진다.

필드 타입에 자기 자신을 적으면 자기참조가 된다. 카테고리 안에 상위 카테고리를 두는 계층 구조가 그 모양이고, 조직도·댓글의 대댓글도 같은 꼴이다. 다른 표를 가리키려면 필드 타입을 그 표의 엔티티 클래스로 적는다.

### 1-3. `@ManyToOne` — 카디널리티 네 갈래 중 하나

관계의 개수를 적는 표시는 넷이다. 앞이 나, 뒤가 상대다.

| 표시 | 뜻 | 예 | 외래키가 붙는 쪽 |
| --- | --- | --- | --- |
| `@ManyToOne` | 나 여럿 : 상대 하나 | 게시글 → 카테고리 | **나** (게시글) |
| `@OneToMany` | 나 하나 : 상대 여럿 | 카테고리 → 게시글 | 상대 (게시글) |
| `@OneToOne` | 나 하나 : 상대 하나 | 회원 → 프로필 | 둘 중 골라서 |
| `@ManyToMany` | 나 여럿 : 상대 여럿 | 학생 ↔ 강의 | 중간 표를 따로 |

**외래키는 언제나 "다" 쪽에 붙는다.** 카테고리 하나에 게시글이 여럿 달리므로, 카테고리가 게시글 번호들을 컬럼 하나에 담을 방법은 없다. 반대로 게시글은 자기가 속한 카테고리 번호 하나만 들고 있으면 된다. 그래서 관계를 표현할 때 `@ManyToOne` 이 가장 먼저 나오고, 실무에서도 가장 많이 쓴다.

`@ManyToMany` 는 표시로는 한 줄이지만 중간 표를 자동으로 만들어 버려서 그 표에 컬럼을 더할 수 없다. 등록 시각이나 수량 같은 것이 붙을 여지가 있으면 중간 엔티티를 직접 만들어 `@ManyToOne` 둘로 푸는 편이 안전하다.

### 1-4. `@JoinColumn` — 만들어질 컬럼 이름 정하기

`@JoinColumn(name = "cno")` 는 이 관계가 표에 남길 외래키 컬럼의 이름을 적는 자리다. 생략하면 하이버네이트가 **`필드이름_상대PK컬럼이름`** 으로 만든다. 필드 이름이 `category` 이고 상대 PK가 `cno` 면 `category_cno` 가 된다.

이름이 길어지고 짐작에 기대게 되므로, `@Table(name=…)` 을 적어 두던 것과 같은 이유로 이쪽도 적어 두는 편이 낫다. → [[Spring day05 엔티티 제약과 감사 필드]]

`ddl-auto` 가 `create-drop` 이면 서버가 뜰 때 생성된 DDL이 콘솔에 그대로 찍히므로, 표시를 붙인 결과를 짐작하지 않고 눈으로 확인할 수 있다.

```sql
create table board (
    bno integer not null,
    bname varchar(255),
    cno integer,
    primary key (bno)
);

alter table board
    add constraint FK... foreign key (cno) references category (cno);
```

**`@JoinColumn` 한 줄이 컬럼 하나와 외래키 제약 하나로 갈라져 나온다.** 표시가 만드는 것이 컬럼만이 아니라는 점이 여기서 보인다.

`@JoinColumn` 에는 `nullable`·`unique` 같은 속성도 있어서 `@Column` 과 성격이 비슷하다. `nullable = false` 를 걸면 카테고리 없는 게시글을 못 만들게 되고, 조인 방식에도 영향을 준다.

### 1-5. 단방향 — 한쪽만 상대를 안다

지금 코드에서 게시글은 카테고리를 알지만 카테고리는 게시글을 모른다. **한쪽에만 참조 필드가 있는 배치를 단방향이라 부른다.**

DB 쪽에서 보면 외래키 하나로 양쪽 조인이 다 되므로 방향이라는 개념 자체가 없다. 방향은 **자바 객체 쪽에만 있는 이야기**다. 필드가 있어야 타고 갈 수 있기 때문이다.

```java
// 게시글 → 카테고리 : 필드를 타고 간다
String 카테고리이름 = board.getCategoryEntity().getCname();

// 카테고리 → 게시글 : 필드가 없으니 리포지토리로 찾는다
List<BoardEntity> 목록 = boardRepository.findByCategoryEntity(category);
```

반대 방향도 필드로 타고 가고 싶으면 카테고리 쪽에 목록 필드를 더한다.

```java
@OneToMany(mappedBy = "categoryEntity")
private List<BoardEntity> boards = new ArrayList<>();
```

`mappedBy` 는 **"외래키를 관리하는 쪽은 내가 아니라 저쪽"** 이라는 표시다. 괄호 안에는 상대 엔티티에 있는 필드 이름을 적는다. 이것이 없으면 JPA는 양쪽 다 외래키를 관리하려 들고 중간 표를 만들어 버린다.

양방향으로 만들면 코드가 편해지는 대신 관리할 것이 늘어난다. 처음에는 **필요한 방향만 단방향으로 두고, 반대 방향이 실제로 필요해질 때 더하는 순서**가 무난하다.

## 2. 추가로 알면 좋은 활용법

### 2-1. `@ManyToOne` 의 기본 로딩이 즉시 로딩이라는 점

`@ManyToOne` 과 `@OneToOne` 은 기본값이 `EAGER`(즉시 로딩)다. 게시글 하나를 읽으면 카테고리까지 함께 읽는다. 게시글 목록을 100건 읽으면 카테고리 조회가 뒤따라 100번 더 나갈 수 있다. 목록 조회 한 줄이 쿼리 수십 개가 되는 **N+1 문제**의 가장 흔한 입구다.

```java
@ManyToOne(fetch = FetchType.LAZY)
@JoinColumn(name = "cno")
private CategoryEntity categoryEntity;
```

`LAZY` 로 두면 필드를 실제로 건드릴 때까지 조회를 미룬다. 대신 미뤄 둔 자리를 트랜잭션이 끝난 뒤에 건드리면 걸린다. 서비스 안에서 DTO 변환까지 끝내 두면 이 문제가 안 생기는 배치가 된다. → [[Spring day05 조회 흐름에 DTO 얹기]]

**`@ManyToOne` 은 일단 `LAZY` 로 두고 필요한 곳에서 함께 읽기(fetch join)** 가 일반적인 기준이다. `@OneToMany` 는 기본값이 이미 `LAZY` 라 그대로 두면 된다.

### 2-2. `@Data` 와 연관관계가 겹칠 때

`@Data` 가 데려오는 `@ToString`·`@EqualsAndHashCode` 가 연관 필드까지 훑는다. 양방향이면 게시글의 `toString()` 이 카테고리를 찍고 카테고리가 다시 게시글을 찍어 끝없이 돈다.

```java
@ToString(exclude = "categoryEntity")
@EqualsAndHashCode(of = "bno")
```

연관 필드를 빼거나 PK만 보게 두면 막힌다. 엔티티에는 `@Data` 대신 필요한 표시만 개별로 붙이는 관용이 여기서 값을 한다.

JSON으로 내보낼 때도 같은 문제가 생긴다. 잭슨이 객체를 따라가며 직렬화하다 순환에 빠진다. `@JsonIgnore` 로 막을 수 있지만, **엔티티를 그대로 내보내지 않고 DTO로 바꿔 내보내면 이 문제가 애초에 없다.**

### 2-3. 저장할 때는 상대 객체를 넣는다

번호가 아니라 객체를 넣는다는 것이 저장 코드에서도 드러난다.

```java
CategoryEntity category = categoryRepository.findById(cno).orElseThrow();

BoardEntity board = BoardEntity.builder()
        .bname(dto.getBname())
        .categoryEntity(category)   // 번호가 아니라 객체
        .build();

boardRepository.save(board);
```

DTO는 화면에서 번호만 받으므로, **번호를 객체로 바꾸는 조회 한 번이 서비스에 끼어든다.** 매번 조회가 부담이면 `getReferenceById` 로 실제 조회 없이 참조만 만들어 넣는 방법도 있다.

응답으로 나갈 때는 반대로 객체에서 필요한 값만 꺼내 DTO에 담는다.

```java
public static BoardDto from(BoardEntity entity) {
    return BoardDto.builder()
            .bno(entity.getBno())
            .bname(entity.getBname())
            .cno(entity.getCategoryEntity().getCno())
            .cname(entity.getCategoryEntity().getCname())
            .build();
}
```

**DTO가 표의 모양이 아니라 화면이 원하는 모양으로 관계를 평평하게 펴는 자리**가 된다. → [[Spring day05 DTO 변환과 초기 데이터 적재]]

### 2-4. 관계를 타고 조회 조건 적기

메소드 이름으로 쿼리를 만드는 규칙이 연관 필드에도 그대로 걸린다.

```java
List<BoardEntity> findByCategoryEntity(CategoryEntity category);
List<BoardEntity> findByCategoryEntity_Cno(Integer cno);
List<BoardEntity> findByCategoryEntity_CnameContaining(String cname);
```

밑줄로 상대 엔티티의 필드까지 파고들 수 있다. 이름이 어긋나면 요청 때가 아니라 서버가 뜰 때 걸린다.

### 2-5. 표를 먼저 만들 때와 엔티티가 만들 때

`ddl-auto` 가 `create` 계열이면 엔티티가 표와 외래키를 만든다. 표를 SQL로 먼저 만들어 두는 배치라면 SQL 쪽 `foreign key` 선언과 엔티티의 `@JoinColumn` 이 같은 이야기를 두 곳에서 하게 된다. 어긋나면 `validate` 로 시작 시점에 잡을 수 있다.

시드 SQL로 데이터를 넣을 때는 **부모 표부터 채워야 한다.** 카테고리가 없는데 게시글이 그 번호를 가리키면 외래키 제약에 걸린다.

## 3. 더 나아가 알면 좋은 것

### 3-1. 연관관계의 주인과 편의 메소드

양방향에서 외래키를 실제로 바꾸는 쪽을 **연관관계의 주인**이라 부른다. `mappedBy` 가 붙지 않은 쪽, 곧 외래키를 들고 있는 `@ManyToOne` 쪽이다. 주인이 아닌 쪽 목록에 아무리 `add` 해도 DB에는 아무 일도 일어나지 않는다.

양쪽을 한 번에 맞추려면 메소드 하나로 묶는다.

```java
public void addBoard(BoardEntity board) {
    boards.add(board);
    board.setCategoryEntity(this);   // 주인 쪽도 함께
}
```

**연관관계 편의 메소드**라 부르고, 양방향을 쓰기로 했으면 사실상 짝으로 따라온다.

### 3-2. 영속성 전이와 고아 객체

`cascade = CascadeType.ALL` 을 걸면 부모를 저장·삭제할 때 자식에게도 같은 일이 번진다. `orphanRemoval = true` 를 더하면 부모의 목록에서 빠진 자식이 삭제된다.

편한 만큼 위험하다. 카테고리를 지웠는데 게시글이 전부 사라지는 일이 여기서 나온다. **부모 없이는 존재할 이유가 없는 자식**(주문과 주문상세 같은)에만 걸고, 그 외에는 각자 저장·삭제하는 편이 안전하다.

### 3-3. 다음에 볼 키워드

- `fetch join`·`@EntityGraph` 로 N+1 없이 연관까지 한 번에 읽기
- `@BatchSize`·`hibernate.default_batch_fetch_size` 로 쿼리 수 줄이기
- JPQL에서 `join` 과 `join fetch` 의 갈림, 컬렉션 fetch join과 페이징이 충돌하는 자리
- 지연 로딩 프록시와 `LazyInitializationException`, `@Transactional` 범위와의 관계
- `@ManyToMany` 를 중간 엔티티 + `@ManyToOne` 둘로 푸는 관용
- 복합키 매핑 — `@Embeddable`·`@EmbeddedId`·`@IdClass`·`@MapsId`
- `@OneToOne` 에서 외래키를 어느 쪽에 둘지와 지연 로딩이 안 먹는 경우
- 연관관계를 안 걸고 번호만 들고 있는 설계(간접 참조)와 그 손익
- `@JoinColumn(foreignKey = @ForeignKey(...))` 로 제약 이름 정하기·제약을 안 만들기
- 양방향 매핑과 DTO 변환·`@JsonManagedReference`·`@JsonBackReference`

## 실습 파일

- `2026B_Spring/springweb/src/main/java/day06/BoardEntity.java` (**관계를 갖는 표 두 벌 중 참조되는 쪽** — `@Entity`·`@Table(name=…)`·`@Id`·롬복 넷으로 day04·day05에서 굳어진 표시 한 벌이 그대로 반복되는 자리와 클래스 이름과 표 이름을 `@Table(name=…)` 으로 갈라 둘 수 있어 둘이 어긋나면 코드만으로 어느 표인지 헷갈리는 점·표를 기준으로 이름을 맞춰 두는 편이 읽기 나은 이유, `@GeneratedValue` 없이 `@Id` 만 둔 배치가 번호를 넣는 쪽에서 정한다는 뜻이 되는 자리와 미리 정해진 목록이면 그럴 수 있고 계속 늘어나는 표면 `IDENTITY` 로 `AUTO_INCREMENT` 에 맡기는 갈림)
- `2026B_Spring/springweb/src/main/java/day06/CategoryEntity.java` (**외래키를 컬럼이 아니라 참조로 두기** — 지금까지의 방식이라면 `Integer cno` 하나면 될 자리에 상대 엔티티 타입 필드를 두는 갈림과 표에 만들어지는 컬럼은 같은데 자바 쪽에서 다루는 모양이 갈리는 것이 연관관계 매핑의 요점이라는 정리, 세 줄이 붙어 하나의 뜻을 만드는 구조 — 관계의 방향은 필드 타입이·개수는 `@ManyToOne` 이·표에 남는 컬럼 이름은 `@JoinColumn` 이 정한다는 갈래와 셋 중 하나만 바꿔도 뜻이 달라지는 점·필드 타입에 자기 자신을 적으면 자기참조가 되어 계층 구조·대댓글이 그 꼴인 자리, **카디널리티 네 갈래**(`@ManyToOne`·`@OneToMany`·`@OneToOne`·`@ManyToMany`)와 외래키가 언제나 "다" 쪽에 붙는 이유(하나가 여럿의 번호를 컬럼 하나에 담을 방법이 없다)·`@ManyToOne` 이 가장 먼저 나오고 가장 많이 쓰이는 근거·`@ManyToMany` 가 만드는 중간 표에 컬럼을 더할 수 없어 중간 엔티티 + `@ManyToOne` 둘로 푸는 관용, **`@JoinColumn` 이 만드는 것** — 생략 시 `필드이름_상대PK` 규칙과 이름을 적어 두는 편이 나은 이유·`create-drop` 으로 생성된 DDL을 눈으로 확인하면 한 줄이 컬럼 하나와 외래키 제약 하나로 갈라져 나오는 자리·`nullable`·`unique` 속성이 `@Column` 과 성격이 비슷한 점, **단방향** — 한쪽에만 참조 필드가 있는 배치와 방향이 DB가 아니라 자바 객체 쪽에만 있는 개념이라는 정리(외래키 하나로 양쪽 조인은 다 된다)·반대 방향은 리포지토리로 찾는 갈래와 `@OneToMany(mappedBy=…)` 로 필드를 더하는 갈래·`mappedBy` 가 "외래키를 관리하는 쪽은 저쪽"이라는 표시이며 없으면 양쪽이 다 관리하려 들어 중간 표가 생기는 자리·필요한 방향만 단방향으로 두고 반대가 필요해질 때 더하는 순서)

## 관련 노트

[[Spring MOC]] · [[Spring day05 등록·수정 흐름과 변경 감지]] · [[KDT_2026 학습 지도]]
