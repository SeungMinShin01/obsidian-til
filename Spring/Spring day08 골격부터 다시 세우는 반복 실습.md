---
출처: Claude 분석
원본: KDT_2026/2026B_Spring/springweb/src/main/java/day08/pratice5_Repeat, springweb/src/main/resources/sql/practice5.sql, springweb/src/main/resources/application.properties
작성일: 2026-09-08
tags: [학습, java]
---

# Spring day08 — 골격부터 다시 세우는 반복 실습

> 실습 파일: `day08/pratice5_Repeat/AppStart.java`, `day08/pratice5_Repeat/model/entity/BaseTime.java`, `day08/pratice5_Repeat/model/entity/BoardEntity.java`, `day08/pratice5_Repeat/model/entity/CommentEntity.java`
> 허브: [[Spring MOC]] · 이전: [[Spring day07 댓글 목록을 품은 DTO 만들기]]

앞 실습에서 게시글·댓글 한 벌을 끝까지 만들어 봤습니다. 이번에는 같은 것을 **보지 않고 다시 짜는** 반복 실습을 새 패키지에 시작합니다. 앞 노트들이 "무엇을 왜 그렇게 두는가"를 정리한 것이라면, 이번 실습이 확인하는 것은 다른 물음입니다 — **빈 폴더에서 시작했을 때 어느 순서로 손이 나가는가.**

지금은 계층 폴더를 다 만들어 두고 엔티티 세 파일까지 채운 상태입니다. 그래서 이 노트는 완성된 흐름이 아니라 **골격을 세우는 단계**를 정리합니다. 나머지 층이 채워지면 이 노트에 이어 붙입니다.

## 1. 배운 내용

### 1-1. 폴더를 먼저 다 만들고 아래층부터 채우기

패키지 안이 이렇게 열려 있습니다.

```
day08/pratice5_Repeat/
├── AppStart.java
├── controller/                 (비어 있음)
├── model/
│   ├── dto/                    (비어 있음)
│   ├── entity/    BaseTime · BoardEntity · CommentEntity
│   └── repository/             (비어 있음)
└── service/                    (비어 있음)
```

계층 축(`model/entity`·`model/dto`·`model/repository`·`service`·`controller`)은 앞에서 정리한 배치를 그대로 옮겨 왔습니다. 빈 폴더가 남아 있는 것은 빠뜨린 것이 아니라 **자리를 먼저 선언해 둔 것**입니다.

| 순서 | 층 | 이 층이 정하는 것 |
| --- | --- | --- |
| 1 | entity | 표 모양 — 컬럼과 관계 |
| 2 | repository | 표에 닿는 메소드 |
| 3 | dto | 밖으로 나갈 응답 모양 |
| 4 | service | 조립과 판단 |
| 5 | controller | 주소와 HTTP 방식 |

아래층부터 올라가는 이유는 **위층이 아래층의 이름을 쓰기 때문**입니다. 서비스는 리포지토리와 DTO의 이름을 부르고, 컨트롤러는 서비스의 메소드 이름을 부릅니다. 반대 순서로 짜면 아직 없는 이름을 계속 적어 두고 나중에 맞추게 됩니다. 골격만 먼저 세워 두면 "다음에 무엇을 채울 차례인가"가 폴더 모양으로 남습니다.

### 1-2. 실습 묶음마다 진입점·공통 클래스를 한 벌씩

`AppStart` 를 이 패키지에도 다시 둡니다. **패키지가 다르면 이름이 같아도 서로 다른 클래스**라, 실습 묶음마다 진입점이 한 벌씩 생기고 컴포넌트 스캔 범위가 그 묶음으로 잘립니다. 진입점이 여럿일 때 어느 것을 띄울지는 그레이들 쪽 `mainClass` 로 고릅니다.

`BaseTime` 도 마찬가지로 이 패키지 안에 한 벌 더 둡니다.

```java
@Getter
@NoArgsConstructor
@MappedSuperclass
@EntityListeners(AuditingEntityListener.class)
public class BaseTime {
    @CreatedDate
    private LocalDateTime createdAt;
    @LastModifiedDate
    private LocalDateTime updatedAt;
}
```

표시 넷이 각자 하는 일을 다시 확인해 두면 이렇습니다.

| 표시 | 하는 일 |
| --- | --- |
| `@MappedSuperclass` | 자기 표는 갖지 않고 필드만 물려준다 |
| `@EntityListeners(AuditingEntityListener.class)` | 값을 채워 줄 구현체를 붙인다 |
| `@CreatedDate` · `@LastModifiedDate` | 처음 한 번 / 저장·수정마다 채운다 |
| `@Getter` 만 두고 `@Setter` 는 안 둠 | 시각은 코드가 아니라 리스너가 채우는 값 |

감사가 도는 세 자리 — **필드 표시 · 엔티티 리스너 · 진입점의 `@EnableJpaAuditing`** — 중 하나라도 빠지면 값이 조용히 `null` 로 남습니다. 오류가 나지 않고 그냥 비어 있어서, 시각 컬럼이 비면 이 셋을 순서대로 확인하는 편이 빠릅니다.

### 1-3. "일" 쪽 세 표시를 손으로 다시 적어 보기

```java
@Entity
@Table(name = "board")
@NoArgsConstructor
@AllArgsConstructor
@Builder
@Data
public class BoardEntity {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Integer id;

    private String author;
    private String password;
    private String content;

    @OneToMany(mappedBy = "boardEntity", cascade = CascadeType.ALL, fetch = FetchType.LAZY)
    @ToString.Exclude
    @Builder.Default
    private List<CommentEntity> commentEntities = new ArrayList<>();
}
```

앞에서 정리한 세 표시가 그대로 붙습니다. 다시 적어 보면 각각이 **무엇을 막으려고 있는지**가 또렷해집니다.

| 표시 | 없으면 생기는 일 |
| --- | --- |
| `mappedBy = "boardEntity"` | 주인이 둘이 되어 관계 표가 따로 생기거나, 이름이 어긋나면 서버가 뜰 때 걸린다 |
| `@ToString.Exclude` | `toString` 이 게시글 → 댓글 → 게시글로 왕복한다 |
| `@Builder.Default` | 빌더로 만든 객체의 목록이 `null` 이 된다 |

`mappedBy` 에 적는 값은 표 이름도 컬럼 이름도 아니라 **상대 엔티티의 자바 필드 이름**입니다. 반복 실습에서 가장 먼저 막히기 쉬운 자리라, 자식 쪽 필드 이름을 먼저 정하고 그 이름을 그대로 옮겨 적는 순서가 안전합니다.

`cascade = CascadeType.ALL` 을 고른 근거도 그대로입니다 — **부모 없이는 존재할 이유가 없는 자식**이면 겁니다. 게시글이 지워졌는데 댓글만 남는 것은 뜻이 안 서니 이 관계는 조건에 맞습니다. `fetch = FetchType.LAZY` 는 `@OneToMany` 의 원래 기본값이라 없어도 같지만, 적어 두면 "이 목록은 필요할 때 읽는다"가 파일에 남습니다.

PK 필드 이름이 `id` 인 것이 눈에 띕니다. 앞 실습 끝머리에서 DTO 쪽 이름을 화면이 읽는 이름(`post.id`)에 맞춰 정리했는데, 이번에는 처음부터 그 이름으로 시작한 셈입니다. **이름은 나중에 바꾸기보다 시작할 때 정해 두는 편이 손이 덜 갑니다** — 이름이 만나는 자리는 `from()`·`toEntity()` 두 곳뿐이라 바꾸는 비용이 크지는 않지만, 골격 단계에서 정하면 그 두 곳도 안 건드립니다.

### 1-4. 관계의 "다" 쪽은 공통 클래스를 물려받는 자리부터

```java
@Entity
@Table(name = "comment")
@NoArgsConstructor
@AllArgsConstructor
@Data
@Builder
public class CommentEntity extends BaseTime {

}
```

`extends BaseTime` 한 줄이 먼저 들어가 있습니다. **표시 한 벌과 상속 자리를 먼저 잡고 필드를 채우는** 순서입니다. 필드가 비어 있어도 클래스에 붙는 표시는 이미 다 정해져 있어서, 뒤에 채울 것은 컬럼과 관계 필드뿐입니다.

여기에 들어갈 것은 시드 데이터가 알려 줍니다.

```sql
INSERT INTO comment (author, password, content, board_id, created_at, updated_at)
VALUES ('박명수', '1234', '첫 게시글 축하드립니다!', 1, NOW(), NOW());
```

컬럼을 늘어놓으면 `author`·`password`·`content` 세 값 필드에 외래키 `board_id`, 그리고 감사 필드 둘입니다. 감사 필드는 `BaseTime` 이 물려주니 클래스에 적을 것은 PK·값 셋·관계 하나가 됩니다. 관계는 `@ManyToOne` + `@JoinColumn(name = "board_id")` 으로 두고, 이 필드 이름이 곧 부모 쪽 `mappedBy` 값이 됩니다.

시드가 감사 컬럼에 `NOW()` 를 직접 넣는 것도 그대로입니다. SQL로 바로 나가는 INSERT는 JPA를 거치지 않아 리스너가 값을 못 채우기 때문입니다.

### 1-5. 설정은 앞 실습 것을 그대로 이어 쓴다

`application.properties` 는 손대지 않았습니다. DB가 `practice5` 로, 시드가 `classpath:/sql/practice5.sql` 로 이미 맞춰져 있어서, **같은 실습을 다시 짜는 경우에는 설정에서 바꿀 것이 없습니다.**

| 줄 | 이번 실습에서 하는 일 |
| --- | --- |
| `datasource.url = …/practice5` | 앞 실습이 만들어 둔 DB를 그대로 쓴다 |
| `ddl-auto=create-drop` | 뜰 때마다 엔티티 기준으로 표를 새로 만든다 |
| `defer-datasource-initialization=true` | 시드를 표 생성 뒤로 미룬다 |
| `sql.init.mode=always` | 기본값 `embedded` 에서는 MySQL에 시드가 안 나간다 |
| `show-sql`·`format_sql` | 만들어진 `create table` 문을 눈으로 본다 |

이 조합 덕분에 **엔티티만 고쳐 서버를 띄우면 표 모양을 바로 확인할 수 있습니다.** 반복 실습에서는 이 점이 꽤 쓸모 있습니다 — 아래층을 다 채우기 전에도 엔티티가 의도한 표를 만드는지 먼저 볼 수 있습니다.

## 2. 추가로 알면 좋은 활용법

### 2-1. 엔티티만 채운 상태에서 표 모양 먼저 확인하기

리포지토리·서비스·컨트롤러가 비어 있어도 서버는 뜹니다. 스프링이 엔티티를 읽어 표를 만드는 것은 웹 층과 무관하기 때문입니다. 진입점을 이 패키지로 두고 띄우면 콘솔에 이런 것이 지나갑니다.

```sql
create table board (id integer not null auto_increment, ...)
create table comment (id integer not null auto_increment, board_id integer, ...)
```

여기서 볼 것은 두 가지입니다 — **자식 표에 외래키 컬럼이 하나 생겼는가**, 그리고 **부모 표에는 아무것도 안 생겼는가**. 양방향에서 DB에 실제로 남는 것은 자식 쪽 컬럼 하나뿐이라, 부모 표에 뭔가 더 생겼다면 `mappedBy` 가 안 걸린 것입니다. 아래층을 다 채운 뒤에 발견하는 것보다 이 자리에서 보는 편이 되돌리기 쉽습니다.

### 2-2. 반복 실습을 앞 실습과 대조하는 순서

다 짠 뒤에 앞 벌과 견줄 때, 파일을 통째로 비교하기보다 **층별로 무엇이 갈렸는지** 보는 편이 남는 것이 많습니다.

| 층 | 갈릴 만한 곳 |
| --- | --- |
| entity | 표시 누락(`@Builder.Default`·`@ToString.Exclude`), `mappedBy` 이름, `cascade` 범위 |
| repository | 제네릭 두 자리 — 거의 갈리지 않는다 |
| dto | 필드 이름(화면 쪽 이름을 썼는가), 컬렉션 필드의 초기화 |
| service | 순회 깊이, `Optional` 을 여는 자리, 성공 판정 기준 |
| controller | 값을 받는 표시(`@RequestBody`·`@RequestParam`), 주소 모양 |

아래층일수록 갈림이 줄고 위층일수록 느는 경향은 앞에서도 확인했던 것입니다. 그래서 **두 번째로 짤 때 시간이 걸리는 곳은 대체로 서비스 위쪽**입니다.

### 2-3. 관계 필드를 먼저 적을 때 컴파일이 막히는 순서

부모부터 적으면 `List<CommentEntity>` 를 쓰는 순간 아직 없는 클래스를 참조하게 됩니다. 자식부터 적으면 `@ManyToOne private BoardEntity …` 가 같은 이유로 막힙니다. 어느 쪽으로 시작해도 한 번은 걸리는 자리라, **두 클래스를 빈 껍데기로 먼저 만들어 두고 필드를 채우는** 순서가 편합니다. 실제로 이번 패키지도 세 파일이 함께 생긴 뒤 안이 채워지는 모양입니다.

### 2-4. 연관관계 편의 메소드를 골격 단계에서 넣어 두기

양방향 관계는 양쪽 필드를 함께 채워야 같은 트랜잭션 안에서 어긋나지 않습니다. 매번 두 줄로 적는 대신 부모 쪽에 메소드로 묶어 둘 수 있습니다.

```java
public void addComment(CommentEntity comment) {
    this.commentEntities.add(comment);
    comment.setBoardEntity(this);
}
```

엔티티를 짜는 단계에서 함께 넣어 두면 서비스가 이 메소드 한 줄만 부르면 됩니다. 짝을 맞추는 책임이 엔티티 안으로 들어가는 배치입니다.

## 3. 더 나아가 알면 좋은 것

### 3-1. 같은 것을 다시 짜 보는 연습이 잡아 주는 것

한 번 따라 친 코드와 안 보고 다시 짠 코드가 갈리는 지점은 대체로 **표시(annotation)** 입니다. 흐름은 기억에 남는데 표시 한 줄은 안 남습니다. 그런데 표시가 빠졌을 때 나타나는 증상이 제각각이라, 갈리는 자리를 알아 두면 진단이 빨라집니다.

| 빠진 것 | 나타나는 증상 |
| --- | --- |
| `@Builder.Default` | 목록이 `null` — 채우려는 순간 막힌다 |
| `@ToString.Exclude` | 로그를 찍는 순간 왕복한다 |
| `@EnableJpaAuditing` | 오류 없이 시각만 비어 있다 |
| `@NoArgsConstructor` | JPA가 엔티티를 못 만든다 |
| `mappedBy` | 서버가 뜰 때 표 모양이 어긋난다 |

**"오류가 나는 것"과 "조용히 비는 것"이 갈린다**는 점이 중요합니다. 뜰 때 걸리는 것은 그 자리에서 알게 되지만, 감사 필드처럼 조용히 `null` 로 남는 것은 나중에 화면에서 발견됩니다. 뒤쪽이 더 오래 걸립니다.

### 3-2. 골격을 손으로 만드는 것과 만들어 주는 도구

계층 폴더와 빈 클래스를 매번 손으로 만드는 되풀이를 줄이는 방향이 여럿 있습니다.

- IDE의 템플릿·라이브 템플릿으로 클래스 뼈대 만들기
- 스프링 이니셜라이저로 프로젝트 단위 골격 받기
- 코드 생성 도구(JHipster 등)로 엔티티에서 층을 뽑아내기
- `JpaRepository` 처럼 **규약으로 구현을 대신하는** 갈래

마지막 것이 지금까지 계속 봐 온 방향입니다. 리포지토리 층이 거의 복사에 가까워진 것도 그래서입니다. 되풀이를 줄이는 두 방향 — **공통을 위로 올리기**와 **규약으로 대신하기** — 중 스프링은 뒤쪽을 많이 씁니다.

다만 배우는 단계에서 골격을 손으로 만드는 것에는 다른 값이 있습니다. 생성기가 만들어 준 파일은 왜 그 자리에 있는지 안 남습니다.

### 3-3. 다음에 채울 층에서 다시 만날 것들

아래층부터 올라가면 앞 실습에서 정리한 자리들을 순서대로 다시 만나게 됩니다.

- repository — `extends JpaRepository<엔티티, PK타입>` 두 자리
- dto — 컬렉션을 품은 DTO, 펴는 방향을 한쪽으로 고정하기, `@Builder.Default`
- service — 두 겹 순회 조립, 번호를 객체로 바꿔 넣기, 조회 → 대조 → 삭제
- controller — 같은 주소를 HTTP 방식으로 가르기, `@RequestBody` 와 `@RequestParam` 이 갈리는 자리

그리고 컬렉션을 건드리는 순간 지연 로딩이 도는 자리 — 게시글 수만큼 댓글 조회가 나가는 1+N — 도 다시 나옵니다. 반복 실습에서는 이번엔 `@BatchSize` 나 `join fetch` 를 얹어 보면서 **쿼리 개수가 실제로 줄어드는지 콘솔로 확인**해 보는 것이 한 걸음 더 나가는 방향입니다. `show-sql` 이 켜져 있으니 세어 보기만 하면 됩니다.

### 3-4. 다음에 볼 키워드

- 계층별 빈 클래스 골격과 IDE 템플릿 · 스프링 이니셜라이저
- `@MappedSuperclass` 와 `@Inheritance` 세 전략의 갈림
- `mappedBy` 와 연관관계의 주인 · 주인을 잘못 잡았을 때 생기는 표
- 연관관계 편의 메소드 · 양쪽 필드 동기화
- `create-drop` 과 `validate` 로 엔티티·표 어긋남을 시작 시점에 잡기
- `@BatchSize` · `default_batch_fetch_size` · `join fetch` 와 `distinct`
- `show-sql` 로 쿼리 개수 세어 보기 · `p6spy` 로 바인딩 값까지 보기
- 테스트 코드로 반복 실습 검증하기 (`@DataJpaTest`)

## 실습 파일

- `2026B_Spring/springweb/src/main/java/day08/pratice5_Repeat/AppStart.java` (**실습 묶음마다 진입점 한 벌** — 패키지가 다르면 이름이 같아도 다른 클래스라 컴포넌트 스캔 범위가 묶음 단위로 잘리는 배치와 진입점이 여럿일 때 그레이들 `mainClass` 로 고르는 자리, `@EnableJpaAuditing` 이 감사가 도는 세 자리 중 하나인 점)
- `2026B_Spring/springweb/src/main/java/day08/pratice5_Repeat/model/entity/BaseTime.java` (**공통 필드를 물려주는 클래스를 실습마다 한 벌씩** — `@MappedSuperclass` 로 자기 표 없이 필드만 내려보내는 선언과 `@EntityListeners(AuditingEntityListener.class)` 로 값을 채울 구현체를 붙이는 자리, `@CreatedDate`·`@LastModifiedDate` 의 갈림, `@Setter` 를 두지 않아 시각을 코드가 아니라 리스너가 채우게 두는 배치, 감사 세 자리 중 하나만 빠져도 오류 없이 `null` 로 남는 점)
- `2026B_Spring/springweb/src/main/java/day08/pratice5_Repeat/model/entity/BoardEntity.java` (**"일" 쪽 세 표시를 손으로 다시 적어 보는 자리** — `mappedBy` 가 상대 엔티티의 자바 필드 이름이라 자식 쪽 필드 이름을 먼저 정하고 옮겨 적는 순서, `@ToString.Exclude` 로 왕복을 한쪽에서 끊기, `@Builder.Default` 로 빌더가 무시하는 초기값을 되살리기, `cascade = ALL` 을 "부모 없이는 존재할 이유가 없는 자식"이라는 기준으로 판단하는 자리, `fetch = LAZY` 가 `@OneToMany` 의 기본값이라 뜻을 적어 두는 표기, PK 필드 이름을 처음부터 화면 쪽 이름(`id`)으로 정해 두면 변환 메소드 두 곳도 안 건드리게 되는 점)
- `2026B_Spring/springweb/src/main/java/day08/pratice5_Repeat/model/entity/CommentEntity.java` (**표시 한 벌과 상속 자리를 먼저 잡고 필드를 채우는 순서** — `extends BaseTime` 이 먼저 들어가 있어 뒤에 적을 것이 PK·값 셋·관계 하나로 좁혀지는 자리, 관계 필드 이름이 곧 부모 쪽 `mappedBy` 값이 되는 짝)
- `2026B_Spring/springweb/src/main/resources/sql/practice5.sql` (**시드가 채울 컬럼을 알려 주는 자리** — 감사 컬럼에 `NOW()` 를 직접 넣는 이유가 SQL로 바로 나가는 INSERT는 JPA 리스너를 안 거치기 때문인 점과 `board_id` 외래키가 자식 표에만 있는 구조)
- `2026B_Spring/springweb/src/main/resources/application.properties` (**같은 실습을 다시 짤 때는 설정에서 바꿀 것이 없는 자리** — `create-drop`·`defer-datasource-initialization`·`sql.init.mode=always`·`show-sql` 조합 덕분에 엔티티만 고쳐 띄워도 `create table` 문으로 표 모양을 바로 확인할 수 있는 점)

## 관련 노트

[[Spring MOC]] · [[Spring day07 댓글 목록을 품은 DTO 만들기]] · [[KDT_2026 학습 지도]]
