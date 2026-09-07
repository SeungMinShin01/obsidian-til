---
출처: Claude 분석
원본: KDT_2026/2026B_Spring/springweb/src/main/java/day07/practice2, springweb/src/main/resources/sql/practice3.sql, springweb/src/main/resources/application.properties
작성일: 2026-09-07
tags: [학습, java]
---

# Spring day07 — 댓글 목록을 품은 DTO 만들기

> 실습 파일: `day07/practice2/model/entity/BoardEntity.java`, `day07/practice2/model/entity/CommentEntity.java`, `day07/practice2/model/dto/BoardDto.java`, `day07/practice2/model/dto/CommentDto.java`, `day07/practice2/service/BoardService.java`, `day07/practice2/controller/BoardController.java`
> 허브: [[Spring MOC]] · 이전: [[Spring day07 댓글이 딸린 목록을 화면에 그리기]]

앞에서 화면을 먼저 그려 보면서 **응답이 어떤 모양이어야 하는지**는 이미 정해졌습니다. 게시글이 배열로 오고, 게시글 한 벌 안에 댓글 배열이 또 들어 있는 모양이었습니다. 이번에는 그 모양을 실제로 만들어 내보내는 서버 쪽을 `practice2` 패키지에 한 벌 새로 짭니다.

앞의 수강신청 실습에서 한 일은 관계를 **평평하게 펴는 것**이었습니다. `EnrollEntity` 가 들고 있던 `CourseEntity` 를 한 칸 타고 들어가 이름만 꺼내 `courseName` 필드에 담았습니다. 이번은 방향이 반대입니다. 목록은 목록인 채로, **한 겹을 남긴 채** 내보냅니다. 같은 "DTO로 옮긴다"인데 결과 모양이 갈리는 자리라 나란히 놓고 보면 기준이 드러납니다.

## 1. 배운 내용

### 1-1. 게시글과 댓글 — 1:N 양방향 한 벌

관계 표시 자체는 day06에서 정리한 것과 같습니다. 새로 외울 것은 없고 어디에 무엇이 붙는지만 다시 확인합니다.

```java
@Entity
@Table(name = "board")
public class BoardEntity extends BaseTime {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Integer boardId;
    @Column(nullable = false, length = 20)
    private String author;
    @Column(nullable = false)
    private String password;
    @Column(nullable = false)
    private String content;

    @OneToMany(mappedBy = "boardEntity", cascade = CascadeType.ALL, fetch = FetchType.LAZY)
    @ToString.Exclude
    @Builder.Default
    private List<CommentEntity> commentEntities = new ArrayList<>();
}
```

```java
@Entity
@Table(name = "comment")
public class CommentEntity extends BaseTime {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Integer commentId;
    ...
    @JoinColumn(name = "board_Id")
    @ManyToOne
    private BoardEntity boardEntity;
}
```

| 자리 | 표시 | 하는 일 |
| --- | --- | --- |
| "다" 쪽 (댓글) | `@ManyToOne` + `@JoinColumn` | 외래키 컬럼을 만든다 — 표에 실제로 남는 것은 이쪽뿐 |
| "일" 쪽 (게시글) | `@OneToMany(mappedBy = "boardEntity")` | 자바 객체에서 반대 방향을 연다 — 표에는 아무것도 안 만든다 |
| | `@ToString.Exclude` | 서로를 타고 왕복하는 `toString` 순환을 한쪽에서 끊는다 |
| | `@Builder.Default` | 빌더로 만들 때 목록이 `null` 이 되는 것을 막는다 |

`mappedBy` 에 적는 `"boardEntity"` 는 표 이름도 컬럼 이름도 아니라 **상대 엔티티의 자바 필드 이름**입니다. 여기가 어긋나면 서버가 뜰 때 걸립니다.

`cascade = CascadeType.ALL` 이 게시글 → 댓글 방향으로 걸려 있습니다. 기준은 앞에서 정리한 그대로입니다 — **부모 없이는 존재할 이유가 없는 자식에만 겁니다.** 게시글이 지워졌는데 댓글만 남는 것은 뜻이 안 서니 이 관계는 조건에 맞습니다. 수강신청 실습에서 같은 표시를 놓고 "어느 부모에서 흘려보낼 것인가"를 따졌던 것과 견주면, 부모가 하나뿐인 이번 관계가 훨씬 단순합니다.

`fetch = FetchType.LAZY` 는 `@OneToMany` 의 원래 기본값이라 없어도 같습니다. 그래도 적어 두면 "이 목록은 필요할 때 읽는다"는 뜻이 파일에 남습니다.

### 1-2. DTO 안에 DTO 목록 두기

이번 실습의 핵심은 이 한 필드입니다.

```java
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class BoardDto {
    private Integer boardId;
    private String author;
    private String password;
    private String content;

    @Builder.Default
    private List<CommentDto> commentDtos = new ArrayList<>();
    ...
}
```

DTO가 **엔티티가 아니라 다른 DTO의 목록**을 들고 있습니다. 이 한 줄이 JSON에서 중첩 배열이 되고, 화면이 카드 안쪽 댓글 목록을 그릴 재료가 됩니다.

엔티티 쪽 `@Builder.Default` 와 똑같은 표시가 DTO에도 붙어 있는 것이 눈에 띕니다. 이유도 같습니다. `@Builder` 는 필드 선언 자리의 초기값을 무시하므로, 그대로 두면 빌더로 만든 DTO의 목록이 `null` 이 됩니다. 뒤에서 `boardDto.getCommentDtos().add(...)` 로 채울 참이라 `null` 이면 그 자리에서 막힙니다. **컬렉션 필드는 선언 자리에서 빈 값으로 두고, 빌더를 쓰면 `@Builder.Default` 를 짝으로 붙인다** — 이 두 줄이 한 벌이라고 외워 두면 편합니다.

### 1-3. 순환이 재현되지 않게 펴는 방향을 한쪽으로 고정하기

엔티티 둘은 서로를 필드로 들고 있습니다(양방향). 그런데 DTO 둘은 그렇지 않습니다.

```java
public class BoardDto {
    private List<CommentDto> commentDtos;   // 댓글 DTO를 목록으로 들고 있다
}

public class CommentDto {
    private Integer boardId;                // 게시글은 번호로만 들고 있다
}
```

| | 게시글 → 댓글 | 댓글 → 게시글 |
| --- | --- | --- |
| 엔티티 | `List<CommentEntity>` (객체) | `BoardEntity` (객체) |
| DTO | `List<CommentDto>` (객체 목록) | `Integer boardId` (번호) |

엔티티에서는 양쪽이 다 객체라 `toString`·JSON 직렬화가 서로를 왕복합니다. DTO에서는 한쪽만 객체이고 반대쪽은 번호라 **탈 곳이 없어서 순환이 성립하지 않습니다.**

앞 노트에서 "DTO 목록을 양쪽으로 들면 순환이 재현되므로 펴는 방향을 한쪽으로 둔다"고 정리했던 것이 실제 코드로 나타난 자리입니다. 어느 쪽을 객체로 남길지는 **화면이 무엇을 한 번에 보는가**로 정합니다. 이 화면은 게시글 카드 안에 댓글을 함께 보여 주니 게시글 쪽이 목록을 듭니다.

### 1-4. `CommentDto.from()` — 관계를 한 칸 타고 들어가 번호만 꺼내기

```java
public static CommentDto from(CommentEntity entity) {
    return CommentDto.builder()
            .commentId(entity.getCommentId())
            .author(entity.getAuthor())
            .content(entity.getContent())
            .boardId(entity.getBoardEntity().getBoardId())   // 한 칸 타고 들어감
            .build();
}
```

`entity.getBoardEntity().getBoardId()` 의 점 두 개가 관계를 한 칸 건너가 값 하나만 꺼내는 자리입니다. 여기서 그물이 끊깁니다 — `BoardEntity` 객체 자체는 DTO로 넘어가지 않고 번호만 남습니다.

`BoardDto.from()` 쪽은 반대로 관계를 안 탑니다.

```java
public static BoardDto from(BoardEntity entity) {
    return BoardDto.builder()
            .boardId(entity.getBoardId())
            .author(entity.getAuthor())
            .content(entity.getContent())
            .build();                       // 댓글 목록은 여기서 안 채운다
}
```

댓글 목록 자리가 비어 있는 것은 빠뜨린 게 아니라 **경계선**입니다. 앞에서 정리한 기준 그대로입니다 — "엔티티 하나와 한 칸 이웃만 보면 나오는 값은 DTO가, 여러 엔티티를 모아야 하는 값은 서비스가." 목록을 채우려면 원소마다 `CommentDto.from()` 을 다시 불러야 하니 그 조립은 서비스 몫으로 남깁니다.

### 1-5. 서비스가 바깥·안쪽 두 겹으로 조립하기

```java
public List<BoardDto> boardFindAll() {
    List<BoardEntity> boardEntities = boardRepository.findAll();

    List<BoardDto> boardDtos = new ArrayList<>();
    boardEntities.forEach((boardEntity) -> {
        BoardDto boardDto = BoardDto.from(boardEntity);
        boardEntity.getCommentEntities().forEach((comment) -> {
            CommentDto commentDto = CommentDto.from(comment);
            boardDto.getCommentDtos().add(commentDto);
        });
        boardDtos.add(boardDto);
    });
    return boardDtos;
}
```

순회가 두 겹입니다. 역할이 갈립니다.

| 순회 | 도는 것 | 정하는 것 |
| --- | --- | --- |
| 바깥 | 게시글 엔티티 목록 | 응답 배열의 **줄 수** |
| 안쪽 | 한 게시글의 댓글 목록 | 각 줄의 **깊이** |

수강신청 실습에서 과정 → 수강 → 학생으로 **두 칸**을 타고 들어가던 중첩과 모양이 같습니다. 그때는 중간 표를 지나느라 순회가 한 겹 더 필요했고, 여기서는 게시글 → 댓글 한 칸이라 두 겹으로 끝납니다. **중간에 표가 몇 개 끼는가가 순회 깊이를 정합니다.**

`boardDto.getCommentDtos().add(...)` 로 채우는 표기도 눈여겨볼 만합니다. `@Data` 의 getter로 목록 **참조**를 꺼내 거기에 원소를 넣습니다. 목록 자체를 새로 대입하는 것이 아니라 이미 있는 목록에 붙이는 것이라 setter가 필요 없습니다. 1-2에서 목록을 빈 값으로 초기화해 둔 것이 여기서 값어치를 냅니다.

그리고 여기가 **컬렉션 지연 로딩이 실제로 도는 자리**입니다. `boardEntity.getCommentEntities()` 를 건드리는 순간 그 게시글의 댓글을 읽는 쿼리가 나갑니다. 게시글이 셋이면 목록 조회 한 번 + 댓글 조회 셋, 곧 1+N입니다. 앞에서 여러 번 나왔던 이야기가 이번에는 `@ManyToOne` 이 아니라 **컬렉션 쪽에서** 나타났습니다. 이 갈림은 3-1에서 다시 봅니다.

### 1-6. 등록 갈래와 성공 판정

```java
public boolean boardSave(BoardDto boardDto) {
    BoardEntity boardEntity = boardDto.toEntity();
    BoardEntity savedEntity = boardRepository.save(boardEntity);
    if (savedEntity.getBoardId() >= 1)
        return true;
    return false;
}
```

`toEntity()` → `save()` → PK 확인 세 단계는 앞에서 정리한 그대로입니다. 판정을 **돌려받은** 엔티티(`savedEntity`)의 번호로 하는 것이 전제입니다. 넘긴 엔티티는 저장 전이라 번호가 비어 있고, `save` 가 돌려준 영속 엔티티에 DB가 채운 번호가 들어 있습니다.

`toEntity()` 는 관계 필드도 PK도 담지 않습니다.

```java
public BoardEntity toEntity() {
    return BoardEntity.builder()
            .author(this.author)
            .password(this.password)
            .content(this.content)
            .build();
}
```

밖에서 온 값이 번호나 시각 자리에 들어가지 않게 **DTO가 통로를 좁혀 둔 것**입니다. 감사 필드는 `BaseTime` 과 리스너가 채우고, 번호는 DB가 채웁니다.

### 1-7. 실습 묶음마다 진입점과 `BaseTime` 을 한 벌씩

```java
@SpringBootApplication
@EnableJpaAuditing
public class AppStart {
    public static void main(String[] args) {
        SpringApplication.run(AppStart.class);
    }
}
```

`practice2` 패키지에 진입점을 따로 두어 컴포넌트 스캔 범위를 이 실습으로 잘라 둡니다. `BaseTime` 도 이 패키지 안에 한 벌 더 있습니다. **패키지가 다르면 이름이 같아도 서로 다른 클래스**라, 실습 묶음마다 한 벌씩 두는 배치는 앞에서와 같습니다.

감사가 도는 세 자리도 다시 확인해 둡니다. 하나라도 빠지면 조용히 `null` 로 남습니다.

| 자리 | 표시 |
| --- | --- |
| 필드 | `@CreatedDate` · `@LastModifiedDate` |
| 공통 클래스 | `@MappedSuperclass` · `@EntityListeners(AuditingEntityListener.class)` |
| 진입점 | `@EnableJpaAuditing` |

DB와 시드를 실습마다 가르는 배치도 그대로입니다. `practice3.sql` 끝에 붙은 세 줄이 다음 실습이 쓸 DB를 미리 만들어 둡니다.

```sql
DROP DATABASE IF EXISTS practice5;
CREATE DATABASE practice5;
USE practice5;
```

설정에서 손대는 것은 DB 주소와 시드 경로 두 줄뿐이고, `create-drop`·`defer-datasource-initialization`·`sql.init.mode`·`encoding` 네 줄은 계속 그대로 갑니다.

### 1-8. 리포지토리와 컨트롤러 — 갈수록 얇아지는 위층

```java
@Repository
public interface BoardRepository extends JpaRepository<BoardEntity, Integer> { }

@Repository
public interface CommentRepository extends JpaRepository<CommentEntity, Integer> { }
```

몸통이 비어 있어도 `findAll`·`save`·`findById` 가 전부 물려 내려옵니다. 제네릭 첫 자리와 인터페이스 이름만 갈릴 뿐이라 리포지토리 층은 이제 거의 복사입니다.

```java
@RestController
@RequestMapping("api/board")
public class BoardController {
    @Autowired
    private BoardService boardService;

    @PostMapping("")
    public boolean boardSave(@RequestBody BoardDto boardDto) {
        return boardService.boardSave(boardDto);
    }

    @GetMapping("")
    public List<BoardDto> boardFindAll() {
        return boardService.boardFindAll();
    }
}
```

컨트롤러도 넘기고 받고 돌려주는 한 줄씩입니다. 같은 주소 `/api/board` 에 등록과 조회가 HTTP 방식으로만 갈려 놓이는 REST 기본 모양이고, 댓글 컨트롤러는 `/api/board/comments` 로 **게시글 주소 아래에** 붙어 관계가 주소에 드러납니다.

댓글 쪽 서비스·컨트롤러는 지금 리포지토리만 주입받은 껍데기입니다. 자리를 먼저 잡고 아래층부터 채워 올리는 순서를 계속 따르고 있는 것이라, 다음에 채울 자리가 파일 모양으로 남아 있는 셈입니다.

### 1-9. 이름 하나가 세 자리에 동시에 남는다

DTO의 필드 이름은 세 곳에서 동시에 쓰입니다.

| 자리 | 무엇이 되나 |
| --- | --- |
| 자바 | 필드 이름·getter 이름 |
| JSON | 응답 키 |
| 화면 | `res.data[i].키` 로 꺼내는 이름 |

컬럼 → 필드 → JSON 키 → 화면으로 이름 하나가 관통한다는 이야기를 계속 해 왔는데, **중첩 목록 필드도 예외가 아닙니다.** DTO의 목록 필드 이름이 곧 화면이 읽을 배열의 이름이 되므로, 서버 쪽 필드 이름을 정할 때 화면 코드가 무엇을 꺼내 쓰는지 함께 봐야 합니다. 값이 `undefined` 로 찍히면 응답 본문을 직접 열어 실제 키를 확인하는 것이 가장 빠릅니다.

이름을 자바 쪽과 JSON 쪽에서 다르게 두고 싶으면 방법이 따로 있습니다(2-1).

## 2. 추가로 알면 좋은 활용법

### 2-1. `@JsonProperty` 로 JSON 키를 따로 정하기

자바 필드 이름과 JSON 키를 갈라 두고 싶을 때 씁니다.

```java
@JsonProperty("comments")
private List<CommentDto> commentDtos = new ArrayList<>();
```

이러면 자바에서는 `commentDtos` 로 부르고 응답에는 `comments` 로 나갑니다. 화면 쪽 이름과 서버 쪽 이름이 각자 자기 관용을 따를 수 있습니다.

클래스 전체에 이름 규칙을 거는 갈래도 있습니다.

```java
@JsonNaming(PropertyNamingStrategies.SnakeCaseStrategy.class)
public class BoardDto { ... }     // commentDtos → comment_dtos
```

다만 이름을 두 벌로 두면 **찾기가 한 단계 늘어난다**는 값이 따라옵니다. 화면에서 본 키로 서버 코드를 검색해도 안 나옵니다. 특별한 이유가 없으면 한 이름으로 관통시키는 편이 손이 덜 갑니다.

### 2-2. 응답에서 비밀번호 빼기

DTO 하나를 요청과 응답에 겸용하면 **요청에만 필요한 필드가 응답에도 실립니다.** 비밀번호가 대표적입니다. 들어올 때는 필요하지만 나갈 때는 실릴 이유가 없습니다.

세 갈래가 있습니다.

```java
// ① 변환 자리에서 안 담기 — from() 에서 그 필드를 빼면 null 로 나간다
// ② 아예 응답에서 지우기
@JsonProperty(access = JsonProperty.Access.WRITE_ONLY)
private String password;          // 받기만 하고 내보내지 않는다

// ③ 요청 DTO와 응답 DTO를 갈라 두기
public class BoardSaveDto { ... }   // author·password·content
public class BoardResponseDto { ... } // boardId·author·content·commentDtos·시각
```

①은 값이 `null` 로라도 키가 남고, ②는 키 자체가 안 나갑니다. ③이 가장 확실한데 클래스가 늘어납니다. **필드 하나 때문에 클래스를 나눌지는 겸용 DTO에서 늘 절반이 비는 필드가 얼마나 되는가로 정합니다.**

`@JsonInclude(JsonInclude.Include.NON_NULL)` 로 비어 있는 필드를 응답에서 통째로 빼는 갈래도 있습니다. 겸용 DTO를 유지하면서 모양만 정리하는 절충입니다.

### 2-3. `stream()` 으로 중첩 조립 적기

지금 두 겹 `forEach` 는 스트림으로도 적을 수 있습니다.

```java
public List<BoardDto> boardFindAll() {
    return boardRepository.findAll().stream()
            .map(entity -> {
                BoardDto dto = BoardDto.from(entity);
                dto.setCommentDtos(
                    entity.getCommentEntities().stream()
                          .map(CommentDto::from)
                          .toList()
                );
                return dto;
            })
            .toList();
}
```

바깥 리스트를 미리 만들어 `add` 하는 줄이 사라집니다. 안쪽은 `map(CommentDto::from).toList()` 한 줄로 줄어듭니다.

더 깔끔하게 하려면 목록 조립까지 `from()` 안으로 넣는 갈래가 있습니다.

```java
public static BoardDto from(BoardEntity entity) {
    return BoardDto.builder()
            .boardId(entity.getBoardId())
            .author(entity.getAuthor())
            .content(entity.getContent())
            .commentDtos(entity.getCommentEntities().stream()
                               .map(CommentDto::from)
                               .toList())
            .build();
}
```

이러면 서비스가 `findAll().stream().map(BoardDto::from).toList()` 한 줄이 됩니다. 다만 1-4에서 그어 둔 경계선("여러 엔티티를 모으는 것은 서비스")을 DTO 쪽으로 조금 옮기는 셈입니다. 컬렉션이 **이미 엔티티 안에 들어 있는 것**이라 새 조회가 필요 없다는 점에서는 DTO가 맡아도 무리가 없습니다. 한 프로젝트 안에서 기준을 하나로 정해 두는 편이 낫습니다.

`forEach`+`add` 와 스트림 중 고르는 기준도 앞과 같습니다 — **곁가지 작업을 끼워 넣기 쉬운 쪽이 `forEach`, 짧은 쪽이 스트림**입니다. 섞어 쓰지 않는 것이 더 중요합니다.

### 2-4. 변환을 트랜잭션 안에서 끝내기

```java
@Transactional(readOnly = true)
public List<BoardDto> boardFindAll() { ... }
```

컬렉션을 지연 로딩으로 두었으니 `getCommentEntities()` 를 건드리는 동안 영속성 컨텍스트가 열려 있어야 합니다. `readOnly = true` 는 스냅샷을 줄여 조회를 가볍게 하는 동시에, **변환이 도는 구간을 트랜잭션 안에 넣어 주는 역할**을 겸합니다.

변환을 서비스 안에서 끝내고 컨트롤러에는 DTO만 넘기는 배치가 이것과 짝입니다. 컨트롤러까지 엔티티를 들고 나가면 그 시점엔 이미 트랜잭션이 닫혀 있어 목록을 건드리는 순간 막힙니다.

### 2-5. 등록 응답에 번호 실어 보내기

`boolean` 하나로는 **성공 말고는 아무것도 못 싣습니다.** 방금 만든 글의 번호도, 실패 이유도 안 실립니다.

```java
@PostMapping("")
public ResponseEntity<BoardDto> boardSave(@RequestBody BoardDto boardDto) {
    BoardDto saved = boardService.boardSave(boardDto);
    return ResponseEntity.status(HttpStatus.CREATED).body(saved);
}
```

화면 쪽에서 등록 직후 전체 목록을 다시 받아 오는 대신 돌아온 한 벌만 붙일 수 있게 됩니다. 앞 노트에서 정리한 "전체 재조회 / 부분 갱신"의 갈림이 서버 응답 모양과 맞물리는 자리입니다.

**실패 종류가 둘 이상 생기는 순간이 `boolean` 반환을 다시 볼 시점**이라는 기준은 그대로 둡니다. 지금은 갈래가 하나뿐이라 `boolean` 으로도 버팁니다.

### 2-6. 댓글 등록 — 번호를 객체로 바꿔 넣기

댓글 서비스를 채울 때 나올 모양은 앞 노트에서 이미 밟은 그것입니다.

```java
public boolean commentSave(CommentDto commentDto) {
    Optional<BoardEntity> optional = boardRepository.findById(commentDto.getBoardId());
    if (optional.isEmpty()) return false;

    CommentEntity entity = commentDto.toEntity();
    entity.setBoardEntity(optional.get());        // 번호 → 객체
    return commentRepository.save(entity).getCommentId() >= 1;
}
```

`toEntity()` 가 관계 필드를 비워 두고 서비스가 `findById` 로 얻은 객체를 넣습니다. **DTO는 리포지토리를 몰라 번호로 객체를 못 얻는다**는 층 경계가 그대로 다시 나옵니다. `findById` 가 객체 얻기와 존재 확인을 겸해, 없는 번호를 DB 외래키 제약보다 앞에서 값으로 걸러 주는 것도 같습니다.

### 2-7. 부모를 통해 자식 저장하기

`cascade = CascadeType.ALL` 이 걸려 있으면 부모만 저장해도 자식이 함께 저장됩니다.

```java
board.getCommentEntities().add(comment);
comment.setBoardEntity(board);       // 양쪽을 함께 채운다
boardRepository.save(board);         // 댓글도 같이 insert 된다
```

두 줄을 함께 적는 것이 중요합니다. 한쪽만 채우면 같은 트랜잭션 안에서 목록과 외래키가 어긋납니다. 이것을 매번 두 줄로 적는 대신 **연관관계 편의 메소드**로 묶어 두는 관용이 있습니다.

```java
public void addComment(CommentEntity comment) {
    this.commentEntities.add(comment);
    comment.setBoardEntity(this);
}
```

부르는 쪽은 `board.addComment(comment)` 한 줄이 되고, 짝을 맞추는 책임이 엔티티 안으로 들어갑니다.

## 3. 더 나아가 알면 좋은 것

### 3-1. 컬렉션의 N+1 — `@ManyToOne` 때와 갈리는 지점

1-5의 조립은 게시글 수만큼 댓글 조회가 나갑니다. 이름은 같은 N+1인데, **컬렉션 쪽은 앞의 `@ManyToOne` 때보다 대응이 까다롭습니다.**

```java
@Query("select distinct b from BoardEntity b left join fetch b.commentEntities")
List<BoardEntity> findAllWithComments();
```

| | `@ManyToOne` 페치 | 컬렉션 페치 |
| --- | --- | --- |
| 결과 줄 수 | 안 늘어남 | 자식 수만큼 **곱해져 늘어남** |
| `distinct` | 필요 없음 | 필요 |
| 페이징 | 됨 | 메모리에서 자르게 되어 위험 |
| 컬렉션 둘 이상 페치 | — | 안 됨 (곱집합) |

게시글 셋에 댓글이 각각 둘이면 조인 결과가 여섯 줄이 되고, 하이버네이트가 같은 게시글 객체로 묶어 주더라도 목록에는 중복이 남습니다. 그래서 `distinct` 가 붙습니다.

컬렉션을 페치하면서 페이징까지 걸면 하이버네이트가 SQL로 자르지 못하고 전부 읽어 메모리에서 자릅니다. 게시판처럼 페이징이 당연한 화면에서는 이 조합이 곧 문제가 됩니다. 그래서 다른 갈래를 씁니다.

- `@BatchSize(size = 100)` / `hibernate.default_batch_fetch_size` — 게시글 100건의 댓글을 `in` 절 한 방으로 모아 읽는다. **1+N이 1+1이 된다**
- 목록에는 댓글 **개수만** 담고 펼칠 때 따로 받기
- 조회 단계에서 바로 DTO로 받기(프로젝션)

실무에서는 배치 페치 크기를 전역으로 걸어 두고 시작하는 편이 무난합니다. 페이징도 살고 쿼리도 줄기 때문입니다.

### 3-2. 관계를 몇 겹까지 응답에 담을 것인가

이번 응답은 두 겹입니다(게시글 → 댓글). 겹이 늘어날수록 응답은 한 번에 많은 것을 주지만 그만큼 무거워집니다.

| 갈래 | 방식 | 손익 |
| --- | --- | --- |
| 다 펴기 | 관계를 스칼라 값으로만 (`courseName`) | 가볍다 / 화면이 여러 번 요청 |
| 한 겹 남기기 | 목록을 중첩 (지금) | 한 번에 그린다 / 안 볼 것도 실린다 |
| 링크만 주기 | `commentsUrl` 같은 주소 | 아주 가볍다 / 왕복이 는다 |

기준은 **화면이 그 둘을 항상 함께 보는가**입니다. 게시글과 댓글은 같이 보이니 함께 보내는 편이 맞고, 게시글과 작성자의 전체 프로필은 함께 보이지 않으니 이름만 펴는 편이 맞습니다.

이 물음이 커지면 GraphQL이 하는 일이 됩니다 — 서버가 응답 모양을 정하지 않고 **화면이 필요한 만큼 골라 가져가는** 구조입니다. 지금 단계에서는 DTO를 화면마다 나누는 것으로 충분합니다.

### 3-3. 삭제가 관계를 타고 번지는 범위

`cascade = CascadeType.ALL` 은 `PERSIST`·`MERGE`·`REMOVE`·`REFRESH`·`DETACH` 를 전부 포함합니다. 저장뿐 아니라 **삭제도 함께 번집니다.** 게시글을 지우면 댓글도 지워집니다.

이 관계에서는 그것이 원하는 동작인데, `ALL` 을 습관처럼 붙이면 원하지 않는 곳까지 번집니다. 필요한 것만 고르는 갈래도 있습니다.

```java
@OneToMany(mappedBy = "boardEntity", cascade = {CascadeType.PERSIST, CascadeType.REMOVE})
```

`orphanRemoval = true` 는 한 걸음 더 갑니다. 부모 목록에서 **빼기만 해도** 자식이 지워집니다. "목록에서 없어진 것은 존재할 이유가 없다"는 뜻이라, 관계가 아주 강할 때만 겁니다.

DB 쪽에도 같은 이야기가 있습니다. 외래키에 `ON DELETE CASCADE` 를 걸면 DB가 지웁니다. 자바 쪽 `cascade` 와 DB 쪽 제약은 **서로 다른 층의 장치**라, 둘을 함께 걸면 어느 쪽이 실제로 지웠는지 헷갈립니다. 한 층에서만 정해 두는 편이 낫습니다.

지우지 않고 표시만 남기는 갈래(소프트 삭제)도 게시판에서는 흔합니다. `deleted` 컬럼을 두고 조회에서 걸러 내는 방식인데, 모든 조회에 조건이 붙는 부담이 따라옵니다. 하이버네이트의 `@SQLDelete`·`@Where` 로 그 조건을 엔티티에 붙여 두는 표기가 있습니다.

### 3-4. 다음에 볼 키워드

- `@BatchSize` · `default_batch_fetch_size` · `join fetch` 와 `distinct` · 컬렉션 페치의 페이징 제약
- 프로젝션(인터페이스·클래스 기반) · Querydsl · `@EntityGraph`
- `@JsonProperty` · `@JsonInclude` · `@JsonNaming` · `Access.WRITE_ONLY`
- 요청 DTO / 응답 DTO 분리 · `record` DTO · MapStruct
- `orphanRemoval` · `ON DELETE CASCADE` · 소프트 삭제와 `@SQLDelete` · `@Where`
- 연관관계 편의 메소드 · 양쪽 필드 동기화
- `@Transactional(readOnly = true)` · OSIV(`spring.jpa.open-in-view`)와 지연 로딩 시점
- `@Valid` · `@NotBlank` · `@Size` 로 등록 값 검사하기
- 페이징(`Page`·`Pageable`)과 게시판 목록
- 비밀번호 해시(BCrypt) · Spring Security
- 계층형 댓글(대댓글)과 자기참조 관계

## 실습 파일

- `2026B_Spring/springweb/src/main/java/day07/practice2/model/entity/BoardEntity.java` (**"일" 쪽 세 표시가 다시 한 벌** — `@OneToMany(mappedBy=…)` 로 반대 방향을 열되 표에는 아무것도 안 만드는 점과 `mappedBy` 가 상대 엔티티의 자바 필드 이름이라 어긋나면 서버가 뜰 때 걸리는 자리, `@ToString.Exclude` 로 순환을 한쪽에서 끊기, `@Builder.Default` 로 빌더가 무시하는 초기값을 되살리기, `cascade = ALL` 을 "부모 없이는 존재할 이유가 없는 자식"이라는 기준에 비춰 판단하는 자리, `fetch = LAZY` 가 `@OneToMany` 의 원래 기본값이라 뜻을 적어 두는 표기인 점, `extends BaseTime` 으로 감사 필드를 물려받기)
- `2026B_Spring/springweb/src/main/java/day07/practice2/model/entity/CommentEntity.java` (**"다" 쪽 외래키 한 벌** — `@ManyToOne`+`@JoinColumn` 으로 표에 실제로 남는 컬럼을 만드는 자리와 양방향에서 DB에 존재하는 것은 이 컬럼 하나뿐이라는 점)
- `2026B_Spring/springweb/src/main/java/day07/practice2/model/dto/BoardDto.java` (**DTO가 다른 DTO의 목록을 필드로 드는 자리** — 이 한 줄이 JSON 중첩 배열이 되어 화면의 카드 안쪽 목록이 되는 구조, 컬렉션 필드를 선언 자리에서 빈 값으로 두고 `@Builder.Default` 를 짝으로 붙이는 관용, `from()` 이 댓글 목록을 비워 두어 "여러 엔티티를 모으는 것은 서비스"라는 경계선을 긋는 자리, `toEntity()` 가 PK·감사 필드·관계 필드를 담지 않아 밖에서 온 값이 안 들어가게 통로를 좁히는 배치)
- `2026B_Spring/springweb/src/main/java/day07/practice2/model/dto/CommentDto.java` (**펴는 방향을 한쪽으로 고정하기** — 게시글을 객체가 아니라 번호(`boardId`)로만 들어 DTO 쪽에서는 순환이 성립하지 않는 자리와 엔티티는 양방향인데 DTO는 한 방향인 대비표, `entity.getBoardEntity().getBoardId()` 로 관계를 한 칸 타고 들어가 값 하나만 꺼내며 그물을 끊는 지점)
- `2026B_Spring/springweb/src/main/java/day07/practice2/service/BoardService.java` (**바깥·안쪽 두 겹 조립** — 바깥 순회가 응답의 줄 수를 안쪽 순회가 깊이를 정하는 대비와 중간에 표가 몇 개 끼는가가 순회 깊이를 정한다는 정리, `getCommentDtos().add(...)` 가 목록 참조를 꺼내 붙이는 표기라 setter가 필요 없는 점, 컬렉션을 건드리는 순간 지연 로딩 쿼리가 나가 1+N이 `@ManyToOne` 이 아니라 컬렉션 쪽에서 생기는 자리, 등록 갈래의 `toEntity()`→`save()`→PK 확인 세 단계와 판정을 돌려받은 엔티티의 번호로 하는 전제)
- `2026B_Spring/springweb/src/main/java/day07/practice2/controller/BoardController.java` (**같은 주소를 방식으로만 가르는 REST 기본 모양** — `/api/board` 에 등록과 조회가 나란히 놓이고 등록은 `@RequestBody` 로 객체 한 벌을 받는 자리, 댓글 주소를 게시글 주소 아래에 붙여 관계를 드러내는 설계, 컨트롤러 본문이 넘기고 돌려주는 한 줄로 얇게 남는 배치)
- `2026B_Spring/springweb/src/main/java/day07/practice2/AppStart.java` (**실습 묶음마다 진입점 한 벌** — 컴포넌트 스캔 범위를 실습 단위로 자르는 배치와 `@EnableJpaAuditing` 이 감사가 도는 세 자리 중 하나인 점)
- `2026B_Spring/springweb/src/main/resources/sql/practice3.sql` (**시드 끝에 다음 실습 DB를 만들어 두기** — `DROP`·`CREATE`·`USE` 세 줄과 실습이 늘 때 설정에서 손대는 것이 DB 주소·시드 경로 두 줄뿐인 배치)

## 관련 노트

[[Spring MOC]] · [[Spring day07 댓글이 딸린 목록을 화면에 그리기]] · [[KDT_2026 학습 지도]]
