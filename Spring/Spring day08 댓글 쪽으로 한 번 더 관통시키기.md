---
출처: Claude 분석
원본: KDT_2026/2026B_Spring/springweb/src/main/java/day08/pratice5_Repeat/model/dto/CommentDto.java, service/CommentService.java, controller/CommentController.java
작성일: 2026-09-08
tags: [학습, java]
---

# Spring day08 — 댓글 쪽으로 한 번 더 관통시키기

> 실습 파일: `day08/pratice5_Repeat/model/dto/CommentDto.java`, `service/CommentService.java`, `controller/CommentController.java`
> 허브: [[Spring MOC]] · 이전: [[Spring day08 골격부터 다시 세우는 반복 실습]]

앞 노트에서 게시글 갈래를 DTO → 서비스 → 컨트롤러까지 세로로 한 번 관통시켰습니다. 댓글 쪽은 클래스 자리만 잡아 둔 상태였는데, 이번에 같은 세 층을 댓글 쪽에서 한 번 더 밟았습니다.

같은 구조를 두 번째로 밟는 것이라 새로 나오는 표시는 거의 없습니다. 대신 **게시글 쪽에서는 안 나오던 자리**가 하나씩 드러납니다 — 번호로 온 부모를 객체로 바꿔 끼우는 단계, 주소 앞머리를 어디에 둘지, 그리고 서비스가 자기 표 말고 이웃 표까지 드는 자리입니다.

## 1. 배운 내용

### 1-1. 번호만 든 DTO에 변환 메소드 두 개 채우기

골격 단계에서 필드만 늘어놓았던 댓글 DTO에 변환 메소드가 들어갔습니다.

```java
@NoArgsConstructor
@AllArgsConstructor
@Data
@Builder
public class CommentDto {
    private Integer id;
    private String author;
    private String password;
    private String content;
    private LocalDateTime createdAt;
    private LocalDateTime updatedAt;
    private Integer boardId;

    public CommentEntity toEntity() {
        return CommentEntity.builder()
                .author(this.author)
                .password(this.password)
                .content(this.content)
                .build();
    }

    public static CommentDto from(CommentEntity entity) { … }
}
```

부모를 드는 자리가 `BoardEntity` 가 아니라 `Integer boardId` 하나뿐입니다. 게시글 DTO가 `List<CommentDto>` 를 통째로 들었던 것과 정확히 반대 방향입니다.

| DTO | 상대를 드는 모양 | 따라 나오는 성질 |
| --- | --- | --- |
| `BoardDto` | `List<CommentDto>` 객체 목록 | 게시글 하나를 받으면 댓글까지 딸려 온다 |
| `CommentDto` | `Integer boardId` 번호 하나 | 댓글에서 게시글로 되돌아 올라갈 길이 없다 |

**순환이 성립하지 않는 것은 이 비대칭 덕분입니다.** 엔티티는 양방향이라 어느 쪽에서 출발해도 상대를 탈 수 있는데, DTO에서는 한쪽만 객체로 두어 길을 한 방향으로 잘라 뒀습니다.

`toEntity()` 가 담는 것은 값 셋뿐입니다. 게시글 쪽과 같은 기준입니다 — **밖에서 정할 수 없는 값은 통로를 아예 안 연다.** 번호는 DB가, 시각은 감사 리스너가, 그리고 부모 참조는 서비스가 채웁니다. `boardId` 필드가 DTO에는 있는데 `toEntity()` 에서는 쓰이지 않는 것이 그래서입니다. **번호를 객체로 바꾸려면 리포지토리가 필요한데, DTO는 그것을 모르는 층입니다.**

### 1-2. 댓글 등록 — 번호를 객체로 바꿔 끼우기

앞에서 비워 둔 자리를 서비스가 메웁니다.

```java
@Service
public class CommentService {
    @Autowired
    private CommentRepository commentRepository;
    @Autowired
    private BoardRepository boardRepository;

    public boolean commentSave(CommentDto commentDto) {
        CommentEntity commentEntity = commentDto.toEntity();
        Optional<BoardEntity> optional = boardRepository.findById(commentDto.getBoardId());
        if (optional.isPresent()) {
            BoardEntity boardEntity = optional.get();
            commentEntity.setBoardEntity(boardEntity);
        }
        CommentEntity savedEntity = commentRepository.save(commentEntity);
        if (savedEntity.getId() >= 1) return true;
        return false;
    }
}
```

네 단계로 읽힙니다.

| 단계 | 하는 일 | 이 단계가 필요한 이유 |
| --- | --- | --- |
| 1 | `toEntity()` 로 값 셋을 옮긴다 | DTO가 할 수 있는 데까지만 |
| 2 | `findById` 로 부모를 꺼낸다 | 번호로는 관계를 못 건다 |
| 3 | setter로 관계 필드에 끼운다 | 엔티티는 객체 참조를 요구한다 |
| 4 | 저장하고 돌려받은 번호로 판정한다 | 번호는 저장 후에만 있다 |

요점은 2·3단계입니다. **웹에서 오는 것은 번호인데 JPA가 요구하는 것은 객체 참조라, 그 틈을 메우는 조회가 한 번 끼어듭니다.** 번호 → 객체 → (표에 저장될 때) 다시 번호로 한 바퀴 갔다 오는 셈인데, 이 수고가 조회할 때 `comment.getBoardEntity().getAuthor()` 처럼 점으로 따라갈 수 있는 편의와 짝입니다.

`findById` 가 겸하는 일이 하나 더 있습니다 — **없는 번호를 걸러 내는 확인**입니다. DB 외래키 제약도 같은 것을 막지만, 제약에 걸리면 예외로 튀고 여기서 걸리면 값으로 돌아옵니다. 다루기 쉬운 쪽은 값입니다.

성공 판정은 게시글 쪽과 같습니다. **넘긴 객체가 아니라 `save` 가 돌려준 객체**의 번호를 봅니다. 저장 전에는 PK가 비어 있어서, 넘긴 쪽을 보면 언제나 `null` 입니다.

### 1-3. 댓글 주소를 따로 여는 자리

```java
@RestController
@RequestMapping("/api/comments")
public class CommentController {
    @Autowired
    private CommentService commentService;

    public boolean commentSave(@RequestBody CommentDto commentDto) { … }

    public boolean commentDelete(
            @RequestParam(name = "id") Integer id,
            @RequestParam(name = "password") String password) { … }
}
```

앞머리를 `/api/comments` 로 잡았습니다. 게시글이 `/api/board` 니 **두 주소가 나란히 서는 배치**입니다. 여기서 갈림이 하나 있습니다.

| 갈래 | 주소 모양 | 성질 |
| --- | --- | --- |
| 나란히 두기 | `/api/comments` | 댓글이 독립된 자원. 부모 번호는 본문·쿼리로 받는다 |
| 아래에 붙이기 | `/api/board/{boardId}/comments` | 관계가 주소에 드러난다. 부모 번호를 `@PathVariable` 로 받는다 |

**주소에 관계를 드러낼 것인가**가 기준입니다. 댓글은 게시글 없이는 뜻이 안 서는 자원이라 아래에 붙이는 쪽이 REST 관용에 가깝습니다. 다만 나란히 두면 부모가 늘어도 주소가 안 늘고, 지금처럼 부모 번호를 DTO 필드(`boardId`)로 이미 받고 있으면 통로가 하나로 모입니다.

받는 표시가 갈래마다 갈리는 것도 게시글 쪽과 같은 기준입니다.

| 갈래 | 받는 표시 | 받는 것 |
| --- | --- | --- |
| 등록 | `@RequestBody` | DTO 한 벌 (본문 JSON) |
| 삭제 | `@RequestParam` | 값 둘 (쿼리스트링) |

**필드가 여럿인 한 벌은 본문에, 값 한둘은 쿼리스트링에.** 표시를 고르는 일이 아니라 무엇이 오는지가 표시를 정합니다.

컨트롤러 본문은 서비스 호출 한 줄입니다. 넘기고 받아서 돌려주는 것 말고 하는 일이 없는 것이 정상입니다 — 판단은 서비스가, HTTP 표현은 컨트롤러가 맡는 배치라서 그렇습니다.

### 1-4. 서비스가 이웃 표의 리포지토리를 드는 자리

댓글 서비스는 리포지토리를 둘 주입받습니다.

```java
@Autowired private CommentRepository commentRepository;
@Autowired private BoardRepository boardRepository;
```

게시글 서비스는 하나만 들었는데 댓글 서비스는 둘입니다. 갈리는 이유는 **하는 일이 이웃 표를 건드리는가**입니다.

여기서 나오는 정리가 하나 있습니다 — **서비스의 단위는 "표 하나"가 아니라 "하나의 일"입니다.** 리포지토리는 표를 따라 하나씩 생기지만, 서비스는 완결되는 일을 따라 생깁니다. 그래서 서비스 하나가 리포지토리 여럿을 부르는 것은 예외가 아니라 흔한 모양입니다.

이 점이 트랜잭션 경계와 이어집니다. 조회 한 번과 저장 한 번이 한 메소드 안에 있으면 **그 사이가 벌어질 수 있는 틈**이라, 둘을 한 묶음으로 처리해야 하는 자리가 곧 `@Transactional` 이 붙는 자리입니다. 표시가 서비스 층에 붙는 관용도 여기서 나옵니다.

## 2. 추가로 알면 좋은 활용법

### 2-1. 매핑 표시는 갈래마다 하나씩

주소 앞머리는 클래스 `@RequestMapping` 이 정하지만, **어떤 요청이 어느 메소드로 갈지는 메소드마다 붙는 방식 표시(`@PostMapping`·`@DeleteMapping` 등)가 정합니다.** 스프링은 뜰 때 이 표시들을 모아 주소 표를 만들어 두고, 요청이 오면 그 표를 봅니다. 표시가 없는 메소드는 표에 안 올라가니 평범한 자바 메소드로 남습니다 — 오류가 아니라 **요청이 안 닿는** 모양이라, 404가 뜨면 스캔 범위 → 클래스 표시 → 이어 붙은 주소 → 방식 순으로 좁혀 보는 편이 빠릅니다.

### 2-2. 관계를 채우는 두 가지 순서

지금은 빌더로 만든 뒤 setter로 관계를 마저 채웁니다. 조회를 먼저 하고 빌더 한 번으로 끝낼 수도 있습니다.

| 순서 | 모양 | 손익 |
| --- | --- | --- |
| 변환 → 조회 → setter | `toEntity()` 로 값만 옮기고 뒤에 끼운다 | 변환 책임이 DTO에 남는다 |
| 조회 → 빌더 한 번 | 서비스가 부모까지 들고 통째로 만든다 | 객체가 완성된 채로 태어난다 |

재료가 준비되는 시점이 달라 갈리는 자리입니다. 뒤쪽은 setter를 안 써도 되니 엔티티의 setter를 줄여 가는 방향과도 맞습니다.

### 2-3. `Optional` 을 여는 네 가지와 없을 때의 갈래

`isPresent()` → `get()` 은 가장 눈에 잘 보이는 표기지만, 다른 갈래도 있습니다.

| 표기 | 없을 때 |
| --- | --- |
| `isPresent()` + `get()` | `if` 안에서 직접 가른다 |
| `orElse(null)` | `null` 로 되돌아온다 — 상자에 담아 둔 뜻이 사라진다 |
| `orElseThrow(…)` | 예외로 튄다 — 아래 코드가 안 돌아간다 |
| 상자째 반환 | 판정을 부르는 쪽으로 넘긴다 |

부모가 없을 때 **저장까지 갈 것인가 거기서 멈출 것인가**는 도메인 판단입니다. 부모 없는 댓글이 뜻이 안 서는 도메인이라면 `orElseThrow` 로 그 자리에서 끊는 편이 뒤가 깔끔합니다. `if` 로 감싸 저장까지 감싸는 표기도 같은 뜻이 됩니다.

### 2-4. 연관관계 편의 메소드로 양쪽 채우기

setter로 자식 쪽만 채우면 같은 트랜잭션 안에서 부모의 목록은 아직 비어 있습니다. DB에는 문제가 없지만(외래키는 자식 쪽 컬럼 하나뿐이니), 저장 직후 부모 객체를 다시 쓰는 코드가 있으면 어긋납니다.

```java
public void addComment(CommentEntity comment) {
    this.commentEntities.add(comment);
    comment.setBoardEntity(this);
}
```

부모 엔티티에 이렇게 묶어 두면 서비스는 한 줄만 부르면 되고, **짝을 맞추는 책임이 엔티티 안으로 들어갑니다.**

### 2-5. 삭제 갈래는 조회 → 대조 → 삭제

비밀번호로 지키는 삭제는 게시글 쪽과 같은 세 걸음입니다.

```java
Optional<CommentEntity> optional = commentRepository.findById(id);
if (optional.isPresent()) {
    CommentEntity entity = optional.get();
    if (entity.getPassword().equals(password)) {
        commentRepository.delete(entity);
        return true;
    }
}
return false;
```

`deleteById` 가 아니라 `findById` 로 꺼내 오는 이유는 하나입니다 — **지우기 전에 값을 봐야 하니 그 줄이 손에 있어야 합니다.** 게시글 삭제는 `cascade = ALL` 이 번져 딸린 댓글까지 지웠는데, 댓글 삭제는 자식이 없으니 그 줄 하나만 사라집니다.

이 자리에서 "없음"과 "비밀번호 불일치"가 같은 `false` 로 뭉치는 것도 그대로입니다.

## 3. 더 나아가 알면 좋은 것

### 3-1. 두 번째로 짤 때 실제로 걸린 곳

앞 노트에서 세워 둔 예상 — 아래층일수록 갈림이 줄고 위층일수록 는다 — 을 댓글 쪽에서도 확인해 보면 이렇습니다.

| 층 | 게시글 쪽과 갈린 곳 |
| --- | --- |
| dto | 상대를 목록으로 드는가 번호로 드는가 |
| service | 이웃 리포지토리를 함께 드는가, 번호→객체 변환 단계가 끼는가 |
| controller | 주소 앞머리를 나란히 둘지 아래에 붙일지 |

**같은 층이라도 관계에서 어느 쪽에 서 있는가에 따라 할 일이 갈립니다.** "일" 쪽은 목록을 조립하고 "다" 쪽은 부모를 찾아 끼웁니다. 표시가 갈리는 게 아니라 **하는 일이 갈리는** 자리라, 두 번째 도메인에서도 이 대비는 그대로 반복됩니다.

### 3-2. 없는 번호를 걸러 내는 세 자리

부모 번호가 잘못 왔을 때 그것을 막을 수 있는 자리가 셋입니다.

| 자리 | 걸리는 방식 | 언제 |
| --- | --- | --- |
| 화면 | 목록에서 고르게 해서 애초에 못 보냄 | 보내기 전 |
| 서비스 `findById` | 값(`Optional` 이 빔)으로 돌아옴 | 저장 전 |
| DB 외래키 제약 | 예외로 튐 | 저장 시점 |

셋을 겹쳐 두는 것이 낭비가 아닙니다. 앞쪽은 다루기 쉽고 뒤쪽은 확실합니다. **화면과 서비스는 뚫릴 수 있고 DB 제약은 못 뚫리니**, 마지막 줄은 언제나 DB에 두고 앞쪽은 사용자 경험을 위해 두는 배치입니다.

### 3-3. 실패 종류가 늘면 `boolean` 을 다시 볼 때

지금 세 갈래가 전부 `boolean` 을 돌려줍니다. 댓글 등록이 실패할 수 있는 이유를 세어 보면 이미 둘 이상입니다 — 부모가 없거나, 값이 제약을 어기거나. 삭제도 없음과 불일치 둘입니다.

| 표현 | 실을 수 있는 것 |
| --- | --- |
| `boolean` | 성공 여부 하나 |
| `ResponseEntity` + 상태 코드 | 없음(404)·권한 없음(403)·성공(200·204)을 갈라 준다 |
| 저장된 DTO 반환 | 새로 생긴 번호까지 화면에 준다 |

**실패 종류가 둘 이상 생기는 순간이 `boolean` 을 다시 볼 시점**이라는 기준은 앞에서도 나왔습니다. 판단은 서비스가 하고 그것을 HTTP 표현으로 옮기는 일은 컨트롤러가 맡으면, 서비스 반환 타입을 바꾸지 않고도 상태 코드를 가를 수 있습니다.

### 3-4. 다음에 볼 키워드

- 중첩 리소스 주소(`/api/board/{id}/comments`)와 `@PathVariable` 로 부모 번호 받기
- `getReferenceById` 로 조회 한 번을 아끼는 갈래와 없는 번호를 값으로 못 거르는 맞바꿈
- `existsById` 로 객체를 안 꺼내고 존재만 확인하기
- `@Transactional` 의 경계와 조회~저장 사이의 틈
- 연관관계 편의 메소드 · `orphanRemoval`
- `ResponseEntity`·`@RestControllerAdvice` 로 실패를 상태 코드로 가르기
- 비밀번호 해시(BCrypt)와 `matches` · 세션·JWT로 넘어가는 다음 걸음
- `@Valid` + DTO 표시로 형식 검사를 본문 앞으로 당기기
- `@DataJpaTest`·`@WebMvcTest` 로 층을 떼어 검사하기

## 실습 파일

- `2026B_Spring/springweb/src/main/java/day08/pratice5_Repeat/model/dto/CommentDto.java` (**번호만 든 쪽 DTO에 변환 메소드를 채우는 자리** — 부모를 `Integer boardId` 하나로만 들어 게시글 DTO가 목록을 통째로 든 것과 정확히 반대 방향이 되는 대비와 그 비대칭 덕분에 순환이 성립하지 않는 점, `toEntity()` 가 값 셋만 담아 번호·시각·부모 참조의 통로를 안 여는 배치와 `boardId` 필드가 있는데도 변환에서 안 쓰이는 이유가 "번호를 객체로 바꾸려면 리포지토리가 필요한데 DTO는 그 층을 모른다"는 경계선인 점)
- `2026B_Spring/springweb/src/main/java/day08/pratice5_Repeat/service/CommentService.java` (**번호를 객체로 바꿔 끼우는 네 단계** — 웹에서 오는 것은 번호인데 JPA가 요구하는 것은 객체 참조라 그 틈을 메우는 조회가 끼어드는 구조와 번호→객체→번호로 한 바퀴 갔다 오는 수고가 조회에서 점으로 관계를 따라가는 편의와 짝인 점, `findById` 가 객체 얻기와 없는 번호 걸러 내기를 겸해 DB 외래키 제약보다 앞에서 값으로 막는 배치, 성공 판정을 넘긴 객체가 아니라 **돌려받은** 엔티티의 PK로 하는 전제, 리포지토리를 둘 주입받는 자리와 "서비스의 단위는 표 하나가 아니라 하나의 일"이라는 정리·조회와 저장 사이의 틈이 곧 `@Transactional` 이 붙는 자리가 되는 점)
- `2026B_Spring/springweb/src/main/java/day08/pratice5_Repeat/controller/CommentController.java` (**댓글 주소를 따로 여는 자리** — 앞머리를 `/api/comments` 로 잡아 게시글 주소와 나란히 두는 갈래와 `/api/board/{boardId}/comments` 로 아래에 붙이는 갈래의 대비·"주소에 관계를 드러낼 것인가"가 기준이 되는 점과 부모 번호를 DTO 필드로 이미 받고 있으면 통로가 하나로 모이는 사정, 등록은 `@RequestBody` 로 한 벌을·삭제는 `@RequestParam` 으로 값 둘을 받아 "무엇이 오는가가 표시를 정한다"가 다시 확인되는 자리, 컨트롤러 본문이 서비스 호출 한 줄로 남는 것이 "판단은 서비스가 HTTP 표현은 컨트롤러가"라는 층 나누기의 결과인 점)

## 관련 노트

[[Spring MOC]] · [[Spring day08 골격부터 다시 세우는 반복 실습]] · [[KDT_2026 학습 지도]]
