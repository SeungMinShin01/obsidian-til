---
출처: Claude 분석
원본: KDT_2026/2026B_Spring/springweb/src/main/java/day06/exam.java, springweb/src/main/java/day06/BoardEntity.java, springweb/src/main/java/day06/CategoryEntity.java, springweb/src/main/java/day06/ReplyEntity.java, springweb/src/main/java/day06/activity
작성일: 2026-09-04
tags: [학습, java]
---

# Spring day06 — 양방향 참조와 순환참조

> 실습 파일: `2026B_Spring/springweb/src/main/java/day06/exam.java`, `BoardEntity.java`, `CategoryEntity.java`, `ReplyEntity.java`, `activity/`
> 허브: [[Spring MOC]] · 이전: [[Spring day06 연관관계 매핑과 외래키]]

앞 노트에서 게시글이 카테고리를 가리키는 단방향까지 만들었다. 게시글에서 카테고리는 타고 갈 수 있지만 카테고리에서 게시글로는 못 간다. **이번은 그 반대 방향을 실제로 열어 보고, 열자마자 따라오는 순환참조를 막는 자리까지 붙이는 실습이다.**

시작은 JPA가 아니라 순수 자바 객체다. 애노테이션을 걷어 내고 클래스 둘로 같은 관계를 만들어 보면, 양방향이 JPA가 만든 개념이 아니라 **자바 객체가 서로를 필드로 들고 있으면 자연히 생기는 모양**이라는 것이 보인다.

| | 단방향 | 양방향 |
| --- | --- | --- |
| 참조 필드 | 한쪽에만 | 양쪽 다 |
| 타고 갈 수 있는 방향 | 하나 | 둘 |
| DB에 만들어지는 것 | 외래키 하나 | 외래키 하나 (같다) |
| 새로 생기는 문제 | 없음 | 순환참조 |

**DB에 남는 것은 양쪽 다 외래키 하나로 똑같은데, 자바 쪽에서만 방향이 늘고 문제도 늘어난다.**

## 1. 배운 내용

### 1-1. 참조가 몇 개인지 세어 보기

관계 이야기를 하기 전에 "참조"라는 말을 숫자로 세어 보는 것부터 시작한다.

```java
int a = 3;
int b = 3;
// 두 변수가 참조하는 값은 몇 개인가 → 1개

String c = new String("유재석");
String d = new String("강호동");
// 두 변수가 참조하는 값은 몇 개인가 → 2개
```

기본형에 담긴 리터럴은 값 자체라 따로 세지 않는다. `new` 는 부를 때마다 객체를 새로 만들므로 **인스턴스 하나당 참조값 하나**가 생긴다.

```java
Test t = new Test();
t.name = new String("유재석");
// t 가 직접 참조하는 것은 1개
// t → Test(101번지) → name(201번지)
```

`t` 가 직접 들고 있는 것은 `Test` 객체 하나뿐이고, 그 안의 `name` 은 `Test` 가 들고 있는 것이다. **참조는 한 칸씩만 센다.** 이 세는 법이 뒤에 나올 순환참조를 이해하는 눈금이 된다.

### 1-2. 자바 객체만으로 관계 만들어 보기

애노테이션 없이 클래스 둘을 두고 같은 관계를 만든다.

```java
@Data
@AllArgsConstructor
class Board {
    private int bno;
    private String btitle;
    private Category category;   // 참조 FK
}

@Data
@AllArgsConstructor
class Category {
    private int cno;
    private String cname;
    private List<Board> list = new ArrayList<>();
}
```

카테고리를 만들고 그 카테고리에 속한 게시글을 만든다.

```java
Category c1 = new Category(1, "자유", new ArrayList<>());
Board b1 = new Board(1, "제목1", c1);
```

이 시점의 상태를 정리하면 이렇다.

| 물음 | 답 | 근거 |
| --- | --- | --- |
| `b1` 으로 `c1` 을 알 수 있나 | 가능 | `Board` 안에 `Category` 필드가 있다 |
| `c1` 으로 `b1` 을 알 수 있나 | 불가 | `Category` 의 목록이 비어 있다 |

**이 상태가 단방향이다.** 그리고 이 모양을 DB로 옮기면 게시글 표에 카테고리 번호를 담는 외래키 하나가 된다. JPA로 적을 때 `@ManyToOne` 이 붙던 자리다. → [[Spring day06 연관관계 매핑과 외래키]]

반대 방향을 열려면 카테고리 쪽 목록에 게시글을 넣어 준다.

```java
c1.getList().add(b1);
```

이제 `c1 → list → b1` 으로 타고 갈 수 있다. **필드에 값을 넣은 것뿐인데 방향이 하나 늘었다.** 양방향은 이렇게 자바 객체 차원에서 먼저 성립하고, JPA 표시는 그것을 DB 쪽 사정과 짝지어 주는 역할만 한다.

### 1-3. 양방향을 열면 따라오는 순환참조

양쪽이 서로를 들고 있으면 한쪽을 문자열로 찍을 때 상대를 찍고, 상대가 다시 나를 찍는다.

```java
System.out.println(b1);
// b1 → c1 → b1 → c1 → … 끝나지 않는다
```

`toString()` 은 원래 `Object` 클래스의 메소드로 객체의 주소값을 돌려주는데, 롬복의 `@Data`(안에 `@ToString`)가 이것을 **필드 값을 이어 붙인 문자열**로 재정의한다. 재정의된 `toString()` 이 연관 필드를 만나면 그 필드의 `toString()` 을 또 부른다. 양방향이면 이 호출이 서로를 왕복하며 스택을 채우고 결국 `StackOverflowError` 로 끝난다.

**끊는 자리는 한 곳이면 된다.** 양방향 중 한쪽 필드에 문자열 만들기에서 빠지라는 표시를 붙인다.

```java
@Data
@AllArgsConstructor
class Category {
    private int cno;
    private String cname;
    @ToString.Exclude          // 여기서 끊는다
    private List<Board> list = new ArrayList<>();
}
```

어느 쪽을 뺄지는 **목록을 들고 있는 쪽**이 기준이 된다. 게시글 하나를 찍을 때 카테고리 이름까지 보이는 것은 쓸모가 있지만, 카테고리 하나를 찍을 때 게시글 전부가 딸려 나오는 것은 대개 쓸모가 없다. `@ToString.Exclude` 는 필드 하나에 붙는 표시이고, 클래스 쪽에 `@ToString(exclude = "list")` 로 적어도 같은 뜻이 된다. → [[Spring day03 애노테이션과 리플렉션]]

### 1-4. 엔티티에 양방향 얹기

순수 자바로 확인한 모양을 그대로 엔티티에 옮긴다. 카테고리 쪽에 게시글 목록 필드를 더한다.

```java
@Entity
@Table(name = "category")
@NoArgsConstructor
@AllArgsConstructor
@Builder
@Data
public class CategoryEntity {
    @Id
    private Integer cno;
    private String cname;

    @OneToMany(mappedBy = "categoryEntity")   // 자바(JPA)에서만 매핑 연결
    @ToString.Exclude                         // 순환참조 방지
    @Builder.Default                          // 빌더에서도 초기값 유지
    private List<BoardEntity> boardList = new ArrayList<>();
}
```

세 표시가 각각 다른 문제를 막는다.

| 표시 | 없으면 생기는 일 |
| --- | --- |
| `@OneToMany(mappedBy = …)` | JPA가 양쪽 다 외래키 주인으로 보고 중간 표를 만든다 |
| `@ToString.Exclude` | `toString()` 이 양쪽을 왕복하며 스택이 넘친다 |
| `@Builder.Default` | 빌더로 만든 객체의 목록이 `new ArrayList<>()` 가 아니라 `null` 이 된다 |

`mappedBy` 괄호 안에 적는 것은 **상대 엔티티에 있는 필드 이름**이다. 표 이름이나 컬럼 이름이 아니라 자바 필드 이름이라, `BoardEntity` 의 `categoryEntity` 필드 이름을 바꾸면 이 문자열도 같이 바꿔야 한다. 문자열이라 오타가 나도 컴파일은 지나가고 서버가 뜰 때 걸린다.

`@Builder.Default` 는 앞에서 DTO를 만들 때 이름만 스쳐 간 표시인데, 목록 필드를 가진 엔티티에서 실제로 필요해진다. `@Builder` 는 필드 선언에 적은 초기값을 무시하고 빌더에 안 넣은 값을 타입의 기본값(참조형이면 `null`)으로 채운다. 목록이 `null` 이면 `add` 하는 순간 걸리므로 초기값을 살려 두는 이 표시가 짝으로 따라온다. → [[Spring day05 DTO 변환과 초기 데이터 적재]]

### 1-5. 관계를 셋으로 늘리기

카테고리-게시글에 댓글을 하나 더 잇는다. 댓글은 게시글에 딸린다.

```java
@Entity
@Table(name = "reply")
@NoArgsConstructor
@AllArgsConstructor
@Builder
@Data
public class ReplyEntity {
    @Id
    private Integer rno;
    private String rname;

    @ManyToOne
    @JoinColumn(name = "bno")
    private BoardEntity boardEntity;
}
```

게시글 쪽에서 댓글 목록을 여는 것도 카테고리에서 했던 것과 똑같다.

```java
@OneToMany(mappedBy = "boardEntity")
@ToString.Exclude
@Builder.Default
private List<ReplyEntity> replyList = new ArrayList<>();
```

이렇게 되면 게시글 엔티티가 **양쪽 역할을 동시에 맡는다.** 카테고리에게는 "다" 쪽이라 외래키를 들고 있고, 댓글에게는 "일" 쪽이라 목록을 들고 있다.

```
category ──1:N──▶ board ──1:N──▶ reply
           cno              bno
```

| 엔티티 | 위쪽 관계 | 아래쪽 관계 | 들고 있는 것 |
| --- | --- | --- | --- |
| `CategoryEntity` | 없음 | 게시글 `@OneToMany` | 목록 |
| `BoardEntity` | 카테고리 `@ManyToOne` | 댓글 `@OneToMany` | 외래키 + 목록 |
| `ReplyEntity` | 게시글 `@ManyToOne` | 없음 | 외래키 |

**표가 몇 개로 늘어도 붙이는 표시 한 벌은 그대로고, 새로 적는 것은 상대 엔티티 타입과 이름뿐이다.** day04에서 엔티티를 두 벌 만들 때 확인했던 되풀이가 관계에서도 같은 모양으로 나온다. → [[Spring day04 JPA 엔티티와 리포지토리]]

### 1-6. DB에는 양방향이 없다

같은 관계를 DB 쪽에서 보면 이야기가 훨씬 짧다.

| | 자바(JPA) | 데이터베이스 |
| --- | --- | --- |
| 단방향 | 필드 하나 | 외래키 하나 |
| 양방향 | 필드 둘 | **없음** (외래키 하나 그대로) |

DB는 참조하는 표에 상대 PK 값을 저장하는 것이 전부다. 조인은 어느 방향에서 걸어도 되므로 방향을 나눌 이유가 없다. 굳이 양쪽에 서로의 키를 두거나 매핑 표를 따로 만들 수는 있지만 실무에서 권장하지 않는다.

**정리하면, 양방향은 JPA에만 있고 DB에는 없다.** 그래서 양방향을 걸어도 표는 하나도 안 바뀌고, 늘어나는 것은 자바 쪽의 편의와 자바 쪽의 문제뿐이다. 실무에서 양방향을 아껴 쓰는 이유도 여기 있다. 필요 없는 자료까지 딸려 오는 통로를 열어 두는 셈이 되기 때문이다.

## 2. 추가로 알면 좋은 활용법

### 2-1. 관계 필드에는 방향 표시를 하나만 둔다

한 필드는 관계 하나를 나타낸다. `@ManyToOne` 과 `@OneToMany` 는 서로 반대 방향의 표시라 같은 필드에 함께 붙을 수 없고, 필드 타입도 한쪽은 엔티티 하나, 다른 쪽은 목록으로 갈린다.

| 필드 타입 | 붙는 표시 | 짝이 되는 표시 |
| --- | --- | --- |
| `CategoryEntity category` | `@ManyToOne` | `@JoinColumn(name = …)` |
| `List<BoardEntity> boardList` | `@OneToMany` | `@ToString.Exclude`·`@Builder.Default` |

**타입이 목록인가 아닌가로 어느 쪽 표시가 와야 하는지가 정해진다.** 관계를 새로 적을 때 필드 타입을 먼저 정하고 그다음에 표시를 고르면 짝이 어긋나지 않는다. 짝이 어긋나면 요청 때가 아니라 서버가 뜰 때 걸리므로, 표시를 붙인 뒤에는 한 번 띄워 보고 생성된 DDL을 확인하는 편이 빠르다.

### 2-2. 양쪽 필드를 한 번에 맞추기

양방향을 걸어 두면 자바 객체 쪽에서 값이 어긋날 수 있다. 게시글에 카테고리를 넣었다고 카테고리의 목록이 저절로 채워지지는 않는다.

```java
board.setCategoryEntity(category);
// category.getBoardList() 는 여전히 비어 있다
```

DB에는 게시글 쪽 외래키만 있으니 저장 결과는 맞지만, **같은 트랜잭션 안에서 카테고리 목록을 읽으면 방금 넣은 게시글이 안 보인다.** 양쪽을 한 번에 맞추는 메소드를 두어 이 어긋남을 막는다.

```java
public void addBoard(BoardEntity board) {
    boardList.add(board);
    board.setCategoryEntity(this);
}
```

양방향을 쓰기로 했으면 사실상 짝으로 따라오는 코드다.

### 2-3. 순환은 JSON에서도 똑같이 생긴다

`@ToString.Exclude` 로 막은 것은 콘솔 출력뿐이다. 엔티티를 그대로 응답으로 내보내면 잭슨이 객체를 따라가며 직렬화하다 같은 자리에서 순환에 빠진다. `@JsonIgnore` 로 한쪽을 막을 수 있지만, **관계를 평평하게 편 DTO로 바꿔 내보내면 이 문제가 애초에 없다.**

```java
public static BoardDto from(BoardEntity entity) {
    return BoardDto.builder()
            .bno(entity.getBno())
            .bname(entity.getBname())
            .cname(entity.getCategoryEntity().getCname())
            .replyCount(entity.getReplyList().size())
            .build();
}
```

목록을 통째로 담는 대신 개수만 담는 식으로, **화면이 실제로 쓰는 모양까지만 꺼내는 자리**가 된다. → [[Spring day05 조회 흐름에 DTO 얹기]]

같은 이유로 `@EqualsAndHashCode` 도 연관 필드를 훑다 순환에 빠진다. PK만 보게 두면 막힌다.

```java
@EqualsAndHashCode(of = "bno")
```

### 2-4. 감사 필드 상속을 관계 실습에도 그대로

관계를 얹는 실습에서도 만든 시각·고친 시각은 계속 필요하다. `@MappedSuperclass` 로 올려 둔 공통 클래스를 실습 패키지마다 한 벌씩 두고 `extends` 로 물려받는다.

```java
@MappedSuperclass
@EntityListeners(AuditingEntityListener.class)
@Getter
@NoArgsConstructor
public class BaseTime {
    @CreatedDate
    private LocalDateTime createDate;
    @LastModifiedDate
    private LocalDateTime updateDate;
}
```

```java
@Entity
public class ProductLogEntity extends BaseTime {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Integer productlogNo;
    …
}
```

**상속으로 내려오는 필드와 관계로 이어지는 필드는 서로 간섭하지 않는다.** 상속은 컬럼을 이 표에 더하는 일이고, 관계는 다른 표를 가리키는 일이라 같은 엔티티에 겹쳐 쓸 수 있다. 감사가 실제로 도는 조건(필드 표시·엔티티 리스너·진입점의 `@EnableJpaAuditing`) 셋은 실습 패키지가 갈려도 그대로 필요하다. → [[Spring day05 엔티티 제약과 감사 필드]]

### 2-5. 목록을 읽을 때 쿼리가 늘어나는 자리

`@OneToMany` 는 기본이 지연 로딩이라 목록 필드를 건드릴 때 그때 조회가 나간다. 게시글 목록 100건을 읽고 각 게시글의 댓글 수를 세면 댓글 조회가 100번 더 나간다.

```java
List<BoardEntity> boards = boardRepository.findAll();   // 1번
boards.forEach(b -> b.getReplyList().size());           // 100번
```

관계를 여럿 걸어 둘수록 이 입구가 늘어난다. 필요한 관계만 `join fetch`·`@EntityGraph` 로 한 번에 읽어 오거나, 애초에 개수만 필요하면 개수를 세는 쿼리를 따로 두는 편이 낫다.

## 3. 더 나아가 알면 좋은 것

### 3-1. 양방향을 열기 전에 물어볼 것

양방향은 편해 보이지만 관리할 것이 셋 늘어난다. 순환을 끊는 표시, 양쪽을 맞추는 메소드, 그리고 열린 통로로 딸려 오는 조회다.

| 물음 | 답이 "아니오"면 |
| --- | --- |
| 반대 방향을 실제로 타고 갈 일이 있나 | 단방향으로 둔다 |
| 리포지토리 조회로는 안 되나 | `findByCategoryEntity(…)` 로 충분한 경우가 많다 |
| 목록이 계속 늘어나는 관계인가 | 늘어나는 쪽은 목록으로 들고 있지 않는 편이 안전하다 |

게시글이 수만 건 달릴 수 있는 카테고리에 목록 필드를 두면, 그 목록을 한 번 건드리는 순간 전부 읽힌다. **"일" 쪽에 목록을 두는 것 자체가 규모에 따라 부담이 된다**는 점이 양방향을 아끼는 실질적인 이유다.

### 3-2. 다음에 볼 키워드

- `join fetch`·`@EntityGraph`·`@BatchSize` 로 관계를 읽을 때 쿼리 수 줄이기
- 컬렉션 fetch join과 페이징이 충돌하는 자리, `Set` 과 `List` 의 갈림
- `@JsonManagedReference`·`@JsonBackReference` 로 직렬화 방향 정하기
- `cascade`·`orphanRemoval` 을 부모-자식 관계에만 거는 기준
- 연관관계를 안 걸고 번호만 들고 있는 설계(간접 참조)와 그 손익
- `@ManyToMany` 를 중간 엔티티와 `@ManyToOne` 둘로 푸는 관용
- 스택 오버플로가 나는 다른 자리들 — 재귀 호출 깊이, `equals` 상호 호출
- 엔티티를 응답으로 내보내지 않는 규칙을 프로젝트 차원에서 굳히는 방법

## 실습 파일

- `2026B_Spring/springweb/src/main/java/day06/exam.java` (**참조를 숫자로 세어 보고 순수 자바로 양방향 만들기** — 기본형 리터럴은 값 자체라 따로 세지 않고 `new` 는 부를 때마다 인스턴스 하나당 참조 하나가 생기는 점·참조는 한 칸씩만 세고 중첩된 것은 그 객체가 들고 있는 것이라는 눈금, 애노테이션 없이 클래스 둘로 같은 관계를 만들어 `Board` 안에 `Category` 필드가 있으면 게시글→카테고리는 타고 가지만 목록이 비어 있는 카테고리→게시글은 못 가는 단방향 상태와 그 모양이 DB의 외래키 하나로 옮겨지는 대응, `c1.getList().add(b1)` 으로 필드에 값을 넣은 것뿐인데 방향이 하나 늘어 양방향이 성립하는 자리와 양방향이 JPA가 만든 개념이 아니라 자바 객체가 서로를 들고 있으면 자연히 생기는 모양이라는 정리, `toString()` 이 원래 `Object` 의 주소값 반환 메소드이고 롬복이 필드 값을 이어 붙인 문자열로 재정의하는 점·재정의된 것이 연관 필드를 만나면 상대의 `toString()` 을 또 불러 왕복하다 스택이 넘치는 순환참조와 한쪽에 `@ToString.Exclude` 를 붙여 한 곳만 끊으면 되는 이유·목록을 들고 있는 쪽을 빼는 기준, DB는 참조 테이블에 상대 PK를 저장하는 단방향뿐이고 양방향은 매핑 테이블로만 흉내 낼 수 있어 실무에서 권장하지 않는 점·양방향은 JPA에만 있고 DB에는 없다는 결론과 실무에서 양방향을 아껴 쓰는 이유)
- `2026B_Spring/springweb/src/main/java/day06/CategoryEntity.java` (**엔티티에 양방향 얹기** — 순수 자바로 확인한 모양을 그대로 옮겨 `@OneToMany(mappedBy=…)`·`@ToString.Exclude`·`@Builder.Default` 세 표시가 각각 다른 문제를 막는 배치와 없으면 각각 중간 표가 생기고·스택이 넘치고·목록이 `null` 이 되는 갈림, `mappedBy` 괄호에 적는 것이 표 이름이나 컬럼 이름이 아니라 상대 엔티티의 자바 필드 이름이라 필드명을 바꾸면 문자열도 같이 바꿔야 하고 오타가 나도 컴파일은 지나가 서버가 뜰 때 걸리는 점, `@Builder` 가 필드 선언의 초기값을 무시하고 참조형을 `null` 로 채우는 성질과 목록이 `null` 이면 `add` 에서 걸리므로 `@Builder.Default` 가 짝으로 따라오는 자리)
- `2026B_Spring/springweb/src/main/java/day06/BoardEntity.java` (**한 엔티티가 양쪽 역할을 동시에 맡는 자리** — 카테고리에게는 "다" 쪽이라 `@ManyToOne`+`@JoinColumn` 으로 외래키를 들고 댓글에게는 "일" 쪽이라 `@OneToMany`+목록을 드는 겹침과 표가 몇 개로 늘어도 붙이는 표시 한 벌은 그대로고 새로 적는 것은 상대 엔티티 타입과 이름뿐이라는 확인, 한 필드는 관계 하나를 나타내므로 방향 표시를 하나만 두고 필드 타입이 목록인가 아닌가로 어느 표시가 와야 하는지가 정해지는 기준·필드 타입을 먼저 정하고 표시를 고르면 짝이 어긋나지 않는 순서와 어긋나면 서버가 뜰 때 걸리므로 띄워서 DDL을 확인하는 편이 빠른 점)
- `2026B_Spring/springweb/src/main/java/day06/ReplyEntity.java` (**관계를 셋으로 늘리기** — 댓글이 게시글에 딸리는 `@ManyToOne`+`@JoinColumn(name="bno")` 이 카테고리-게시글에서 했던 것과 같은 모양인 자리와 `category → board → reply` 로 이어지는 사슬에서 가운데 엔티티만 외래키와 목록을 함께 드는 구조)
- `2026B_Spring/springweb/src/main/java/day06/activity/BaseTime.java`, `activity/ProductLogEntity.java` (**감사 필드 상속을 관계 실습에도 한 벌 더** — `@MappedSuperclass`+`@EntityListeners(AuditingEntityListener.class)` 공통 클래스를 실습 패키지마다 두고 `extends` 로 물려받는 배치와 상속으로 내려오는 필드는 이 표에 컬럼을 더하는 일이고 관계 필드는 다른 표를 가리키는 일이라 서로 간섭하지 않아 겹쳐 쓸 수 있는 점, `@GeneratedValue(strategy=IDENTITY)`·`@Column(length=…)` 이 관계가 붙은 엔티티에서도 그대로 쓰이는 자리와 감사가 도는 세 조건이 실습 패키지가 갈려도 똑같이 필요한 점)

## 관련 노트

[[Spring MOC]] · [[Spring day06 연관관계 매핑과 외래키]] · [[KDT_2026 학습 지도]]
