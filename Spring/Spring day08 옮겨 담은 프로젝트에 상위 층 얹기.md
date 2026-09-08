---
출처: Claude 분석
원본: KDT_2026/2026B_Spring/demo/src/main/java/com/example/demo/model/repository, demo/src/main/java/com/example/demo/service, demo/src/main/java/com/example/demo/controller
작성일: 2026-09-08
tags: [학습, java]
---

# Spring day08 — 옮겨 담은 프로젝트에 상위 층 얹기

> 실습 파일: `demo/src/main/java/com/example/demo/model/repository/BoardRepository.java`, `CommentRepository.java`, `service/BoardService.java`, `service/CommentService.java`, `controller/BoardController.java`, `controller/CommentController.java`
> 허브: [[Spring MOC]] · 이전: [[Spring day08 새 프로젝트로 옮겨 담는 도메인 층]] · 다음: [[Spring day08 요구사항 명세를 API 규격으로 옮기기]]

앞 노트에서 새 프로젝트(`demo`)에 엔티티·DTO·설정까지 옮겨 담고, 리포지토리·서비스·컨트롤러는 폴더만 만들어 둔 채로 멈췄습니다. 이번에는 그 빈 자리를 채워 **게시글 세 갈래(등록·조회·삭제)와 댓글 두 갈래(등록·삭제)를 컨트롤러까지 관통**시켰습니다.

같은 게시판을 짜는 것이 이번이 두 번째라서, 코드보다는 **어디가 그대로이고 어디가 갈리는지**가 더 눈에 들어옵니다. 아래층(엔티티·리포지토리)은 거의 복사에 가깝고, 갈림은 주소 설계와 서비스가 무엇을 한 묶음으로 보느냐에서 나옵니다.

## 1. 배운 내용

### 1-1. 리포지토리 두 벌 — 규약만 남는 층

```java
@Repository
public interface BoardRepository
        extends JpaRepository<BoardEntity, Integer> {
}
```

```java
@Repository
public interface CommentRepository
        extends JpaRepository<CommentEntity, Integer> {
}
```

두 파일에서 갈리는 것은 **인터페이스 이름과 제네릭 첫 자리** 둘뿐입니다. PK 타입이 둘 다 `Integer` 라 둘째 자리도 같습니다. 몸통이 비어 있는데도 `save`·`findAll`·`findById`·`delete` 가 다 쓰이는 것은 이 층이 구현이 아니라 **규약을 물려받는 자리**이기 때문입니다.

| 항목 | 이유 |
| --- | --- |
| `interface` 여야 한다 | 구현체는 스프링 데이터가 실행 중에 만들어 끼운다 |
| 제네릭 두 자리 | 다룰 엔티티 타입과 그 PK 타입 |
| `@Repository` | 계층 표시 + DB 예외를 스프링 표준 예외로 바꿔 주는 자리 |

이 층이 짧다는 것이 곧 **위층이 무엇을 할지 정해져 있다**는 뜻이기도 합니다. 리포지토리가 주는 도구는 "한 줄 저장·전체 조회·번호로 조회·삭제" 넷뿐이라, 그 조합으로 표현되지 않는 일은 전부 서비스 몫이 됩니다.

### 1-2. 등록 — 변환 → 저장 → 판정 세 줄

```java
public boolean boardSave(BoardDto boardDto) {
    BoardEntity boardEntity = boardDto.toEntity();
    BoardEntity savedEntity = boardRepository.save(boardEntity);
    if (savedEntity.getId() >= 1)
        return true;
    return false;
}
```

세 줄이 각각 다른 층의 몫으로 갈립니다.

| 줄 | 몫 |
| --- | --- |
| `toEntity()` | DTO — 밖에서 온 값을 엔티티 모양으로 |
| `save()` | 리포지토리 — 실제 저장 |
| PK 확인 | 서비스 — 성공/실패 판정 |

성공 판정을 **돌려받은** 엔티티의 PK로 하는 것이 요점입니다. 넣기 전 엔티티의 `id` 는 아직 비어 있고, `save()` 가 돌려주는 쪽에 DB가 매긴 번호가 채워져 들어옵니다. `id` 를 `int` 가 아니라 `Integer` 로 둔 덕에 "아직 없음"이 `null` 로 표현될 수 있는 것과도 이어집니다.

다만 이 `boolean` 이 잡는 실패 범위는 좁습니다. 저장 자체가 막히면 예외로 튀어 나가지 이 자리로 `false` 가 돌아오지 않습니다. **정말로 `false` 가 되는 경우가 몇 가지인지 세어 보는 것**이 이 반환형을 계속 쓸지 판단하는 기준이 됩니다.

### 1-3. 목록 조회 — 두 겹으로 조립하기

```java
public List<BoardDto> boardFindAll() {
    List<BoardEntity> boardEntities = boardRepository.findAll();
    List<BoardDto> boardDtos = new ArrayList<>();
    boardEntities.forEach((boardEntity) -> {
        BoardDto boardDto = BoardDto.from(boardEntity);
        boardEntity.getCommententities().forEach((commentEntity) -> {
            CommentDto commentDto = CommentDto.from(commentEntity);
            boardDto.getComments().add(commentDto);
        });
        boardDtos.add(boardDto);
    });
    return boardDtos;
}
```

바깥 순회와 안쪽 순회가 하는 일이 다릅니다.

| 순회 | 정하는 것 |
| --- | --- |
| 바깥(`boardEntities`) | 응답 배열의 **줄 수** |
| 안쪽(`getCommententities()`) | 각 줄의 **깊이** |

`from()` 이 댓글 목록을 비워 두기 때문에 여기서 채워 넣는 구조입니다. 경계선을 다시 적으면 **엔티티 하나와 한 칸 이웃까지 보면 나오는 값은 DTO가, 여러 엔티티를 모아야 하는 값은 서비스가** 채웁니다.

`boardDto.getComments().add(...)` 가 setter 없이 되는 것은 getter가 목록 **참조**를 돌려주기 때문입니다. 새 목록으로 갈아 끼우는 게 아니라 이미 있는 목록에 붙이는 표기라, 필드를 `new ArrayList<>()` 로 초기화해 두고 `@Builder.Default` 를 짝으로 붙여 둔 것이 여기서 값을 합니다.

그리고 **컬렉션을 건드리는 순간 지연 로딩 쿼리가 나갑니다.** 게시글이 N줄이면 목록 쿼리 하나에 댓글 쿼리 N개가 따라붙는 모양이라, 1+N이 `@ManyToOne` 이 아니라 컬렉션 쪽에서 생기는 자리입니다.

### 1-4. 삭제 — 조회 → 대조 → 삭제 세 걸음

```java
public boolean boardDelete(Integer id, String password) {
    Optional<BoardEntity> optional = boardRepository.findById(id);
    if (optional.isPresent()) {
        BoardEntity boardEntity = optional.get();
        if (boardEntity.getPassword().equals(password)) {
            boardRepository.delete(boardEntity);
            return true;
        }
    }
    return false;
}
```

`deleteById` 라는 한 줄짜리 메소드가 있는데도 `findById` 로 꺼내 오는 이유는 **지우기 전에 값을 봐야 하기 때문**입니다. 비밀번호를 대조하려면 저장된 줄이 손에 있어야 합니다.

실패 경로는 둘인데 결과는 하나로 뭉칩니다.

| 실패 | 지금 결과 |
| --- | --- |
| 그 번호의 글이 없음 | `false` |
| 비밀번호가 다름 | `false` |

`equals` 를 부를 때 **저장된 쪽을 앞에 두는** 표기도 습관으로 굳혀 둘 만합니다. 밖에서 온 값이 앞에 오면 그 값이 비었을 때 그 자리에서 막히는데, 저장된 쪽은 그럴 여지가 적습니다.

게시글 삭제에서는 `cascade = ALL` 이 실제로 번져 그 글에 달린 댓글이 함께 지워집니다. 반대로 댓글 삭제 쪽은 자식이 없어 번질 곳이 없습니다 — 같은 세 걸음인데 뒷정리 범위가 갈리는 대비입니다.

### 1-5. 댓글 등록 — 번호를 객체로 바꿔 끼우기

```java
public boolean commentSave(CommentDto commentDto) {
    CommentEntity commentEntity = commentDto.toEntity();
    Optional<BoardEntity> optional = boardRepository.findById(commentDto.getBoardId());
    if (optional.isPresent()) {
        BoardEntity boardEntity = optional.get();
        commentEntity.setBoardEntity(boardEntity);
    }
    CommentEntity savedEntity = commentRepository.save(commentEntity);
    if (savedEntity.getId() >= 1) {
        return true;
    }
    return false;
}
```

네 단계로 갈립니다: **변환 → 부모 조회 → 대입 → 저장.**

웹에서 오는 관계는 번호(`boardId`)인데 JPA가 요구하는 것은 객체 참조라, 그 사이를 서비스가 메웁니다. `toEntity()` 가 이 일을 못 하는 이유는 능력이 아니라 층입니다 — **DTO는 리포지토리를 모릅니다.**

`findById` 는 여기서 두 몫을 겸합니다. 부모 객체를 얻는 것과, 없는 번호를 **DB 외래키 제약보다 앞에서 값으로 걸러 내는** 것입니다.

| 거르는 자리 | 돌아오는 모양 |
| --- | --- |
| 서비스의 `findById` | 값 (`Optional` 이 빔) |
| DB 외래키 제약 | 예외 |

댓글 서비스가 자기 표(`CommentRepository`)와 이웃 표(`BoardRepository`)를 **함께** 주입받는 것도 그대로입니다. 서비스의 단위가 "표 하나"가 아니라 "하나의 일"이라는 정리가 코드로 나타나는 자리입니다. 그리고 조회와 저장 사이에 틈이 생기므로, 이 메소드 전체가 곧 `@Transactional` 이 붙을 자리이기도 합니다.

### 1-6. 컨트롤러 — 주소를 나란히 둘 것인가 아래에 붙일 것인가

```java
@RestController
@RequestMapping("/api/board")
public class BoardController { ... }
```

```java
@RestController
@RequestMapping("/api/comments")
public class CommentController {
    @Autowired
    private CommentService commentService;

    @PostMapping("")
    public boolean commentSave(@RequestBody CommentDto commentDto) {
        return commentService.commentSave(commentDto);
    }

    @DeleteMapping("")
    public boolean commentDelete(
            @RequestParam(name = "id") Integer id,
            @RequestParam(name = "password") String password) {
        return commentService.commentDelete(id, password);
    }
}
```

앞 실습에서는 댓글을 `/api/board/comments` 로 게시글 **아래에** 붙였는데, 여기서는 `/api/comments` 로 **나란히** 두었습니다. 두 갈래의 성질을 정리하면 이렇습니다.

| 배치 | 성질 |
| --- | --- |
| `/api/board/comments` | 주소가 소속을 드러낸다. 부모 없이 댓글만 다루는 요청이 어색해진다 |
| `/api/comments` | 댓글이 독립 자원이 된다. 소속은 본문·쿼리로 따로 실어야 한다 |

기준은 **댓글을 게시글의 일부로 볼 것인가, 그 자체로 다룰 자원으로 볼 것인가**입니다. 목록을 항상 게시글과 함께 내려보내는 지금 구조라면 아래에 붙이는 쪽이 뜻에 가깝고, 나중에 "내가 쓴 댓글 전체"처럼 부모를 가로지르는 조회가 생기면 나란히 둔 쪽이 편해집니다.

### 1-7. 매핑 표시는 갈래마다 하나씩

클래스에 붙인 `@RequestMapping("/api/board")` 는 **앞머리**만 정합니다. 실제 주소 표에 한 줄이 오르려면 메소드마다 방식 표시(`@GetMapping`·`@PostMapping`·`@DeleteMapping`)가 하나씩 더 붙어야 합니다. 앞머리와 메소드 표시가 이어 붙어 한 자리가 되는 구조입니다.

```
@RequestMapping("/api/board") + @PostMapping("")  →  POST /api/board
@RequestMapping("/api/board") + @GetMapping("")   →  GET  /api/board
```

이 표시가 없는 메소드는 그냥 평범한 자바 메소드라, 컴파일도 지나가고 서버도 뜨는데 그 주소를 부르면 404가 돌아옵니다. 요청이 안 닿을 때 좁혀 보는 순서를 정해 두면 빠릅니다.

1. 서버가 떴는가 (포트·컨텍스트)
2. 시작 로그의 매핑 목록에 그 주소가 있는가
3. 있는데 안 닿는다면 방식(GET/POST/DELETE)이 맞는가
4. 닿는데 값이 안 들어온다면 `@RequestBody`·`@RequestParam` 중 무엇으로 받고 있는가

**주소 표에 올랐는지부터 보는 것**이 요점입니다. 2번에서 이미 없다면 3번 이후는 볼 필요가 없습니다.

### 1-8. 무엇을 받는가가 표시를 정한다

| 갈래 | 받는 것 | 표시 |
| --- | --- | --- |
| 등록 | 필드 여럿이 묶인 한 벌 | `@RequestBody` + DTO |
| 삭제 | 값 두 개 | `@RequestParam` |

DELETE에 본문을 잘 싣지 않는 관용 때문에 삭제는 쿼리스트링으로 갑니다. 대신 **쿼리스트링은 주소창과 접근 로그에 그대로 남는다**는 부담이 따라옵니다. 비밀번호를 여기에 싣는 지금 방식이 실습 범위를 넘어가면 다시 볼 자리입니다.

`@RequestParam(name = "id")` 처럼 이름을 적어 두면 **바깥 이름(쿼리스트링 키)과 자바 매개변수 이름을 갈라 둘 수** 있습니다. 컴파일 옵션에 따라 매개변수 이름이 결과물에 안 남는 경우가 있어서, 적어 두는 편이 안전합니다.

### 1-9. 컨트롤러 본문이 한 줄로 남는 것

컨트롤러 메소드들이 전부 `return xxxService.xxx(...)` 한 줄입니다. 얇아 보이지만 이게 층을 나눈 **결과**입니다.

| 층 | 아는 것 |
| --- | --- |
| 컨트롤러 | HTTP (주소·방식·값이 실린 자리) |
| 서비스 | 판단 (있는가·맞는가·무엇을 함께 할 것인가) |
| 리포지토리 | DB |

서비스 파일만 봐서는 이 코드가 HTTP로 불리는지 알 수 없다는 점이 이 나눔의 값어치입니다. 나중에 같은 로직을 배치 작업이나 테스트에서 부를 때 그대로 씁니다.

## 2. 추가로 알면 좋은 활용법

### 2-1. `@Transactional` 을 어디에 걸 것인가

지금 코드에는 트랜잭션 표시가 없습니다. 걸 자리를 고르는 기준은 **여러 번의 DB 접근 사이에 틈이 생기는가**입니다.

| 메소드 | 틈 | 표시 후보 |
| --- | --- | --- |
| 등록 | 저장 한 번 | 없어도 무방 |
| 목록 조회 | 조회 + 지연 로딩 여러 번 | `@Transactional(readOnly = true)` |
| 삭제 | 조회 → 삭제 | `@Transactional` |
| 댓글 등록 | 부모 조회 → 저장 | `@Transactional` |

목록 조회에 `readOnly = true` 를 거는 것은 성능뿐 아니라 **변환이 끝날 때까지 영속성 컨텍스트를 열어 두는** 역할도 겸합니다. 지연 로딩으로 댓글을 꺼내 조립하는 구간이 트랜잭션 밖으로 나가면 그 자리에서 막히기 때문입니다.

### 2-2. 필드 주입과 생성자 주입

```java
// 지금
@Autowired
private BoardRepository boardRepository;

// 대안
private final BoardRepository boardRepository;
public BoardService(BoardRepository boardRepository) { ... }
// 또는 @RequiredArgsConstructor 로 생성자를 만들어 받기
```

| 축 | 필드 주입 | 생성자 주입 |
| --- | --- | --- |
| 글자 수 | 짧다 | 길다 (롬복으로 줄일 수 있다) |
| `final` | 못 붙인다 | 붙는다 |
| 테스트에서 갈아 끼우기 | 반사(reflection)나 컨테이너가 필요 | `new` 로 바로 |
| 의존이 늘어날 때 | 눈에 안 띈다 | 생성자가 길어져 눈에 띈다 |

마지막 줄이 실무에서 자주 언급되는 이유입니다. **생성자가 길어지면 "이 서비스가 너무 많은 일을 한다"는 신호**가 코드 모양으로 드러납니다.

### 2-3. `boolean` 을 넘어서는 응답

지금은 다섯 갈래 모두 `true`/`false` 를 돌려줍니다. 실패 종류가 둘 이상 생긴 순간(없는 번호 / 비밀번호 불일치)이 이 반환형을 다시 볼 시점입니다.

| 갈래 | 모양 |
| --- | --- |
| `enum` 결과 | 서비스가 실패 종류를 값으로 돌려주고 컨트롤러가 상태 코드로 옮긴다 |
| 예외 + `@RestControllerAdvice` | 서비스가 예외를 던지고 한 곳에서 응답 모양을 맞춘다 |
| `ResponseEntity` | 컨트롤러가 본문과 상태 코드를 함께 정한다 |

어느 쪽이든 원칙은 같습니다 — **판단은 서비스가, HTTP 표현은 컨트롤러가.** 서비스가 `HttpStatus` 를 아는 순간 층이 섞입니다.

상태 코드로 옮기면 이렇게 갈립니다.

| 상황 | 코드 |
| --- | --- |
| 지워졌다 | 204 (또는 200) |
| 그런 번호가 없다 | 404 |
| 있는데 비밀번호가 다르다 | 403 |

### 2-4. 등록 응답에 번호를 실어 주기

`true` 만 돌아오면 화면은 방금 만든 글의 번호를 모릅니다. 그래서 전체 목록을 다시 부르는 방식이 되는데, 등록 응답에 만들어진 번호를 실어 주면 화면이 그 줄만 붙이는 **부분 갱신**이 가능해집니다. 서버가 무엇을 돌려주느냐가 화면의 갱신 방식을 정하는 자리입니다.

### 2-5. 메소드 이름을 층을 관통해 맞추기

`boardSave`·`boardFindAll`·`boardDelete` 가 서비스와 컨트롤러에서 같은 이름으로 놓여 있습니다. 한 갈래를 따라갈 때 이름이 바뀌지 않으면 검색 한 번으로 층을 다 훑을 수 있습니다.

다만 층마다 관용 이름이 조금 다르기도 합니다 — 리포지토리는 `findAll`·`save`(스프링 데이터 규약), 서비스는 도메인 동사(`register`·`remove`), 컨트롤러는 자유. 어느 쪽을 고르든 **한 갈래는 한 이름으로** 유지하는 것이 요점입니다.

## 3. 더 나아가 알면 좋은 것

### 3-1. 목록에 딸린 것을 다 실어 보내는 것의 한계

지금 목록 응답은 모든 게시글과 그 글의 모든 댓글을 담습니다. 글이 늘면 응답이 그만큼 커지고, 쿼리도 1+N으로 늡니다. 넘어가는 순서는 대개 이렇습니다.

1. `join fetch` 로 한 번에 가져오기 — 컬렉션이라 줄이 곱으로 늘어 `distinct` 가 필요하고, 페이징이 메모리에서 잘린다
2. `@BatchSize` 로 1+N을 1+1로 — 자식 조회를 `IN` 하나로 묶는다
3. 애초에 댓글을 목록에 안 싣고 글을 펼칠 때 따로 부르기 — 응답 계약을 바꾸는 갈래

3번이 가장 근본적인데 화면 설계까지 함께 바뀝니다. **"화면이 그 둘을 항상 함께 보는가"** 가 판단 기준입니다.

### 3-2. 페이징

`findAll()` 은 전부 가져옵니다. 스프링 데이터는 `Pageable` 을 매개변수로 받으면 페이징 쿼리를 만들어 주고, `Page<T>` 로 전체 개수·페이지 수까지 함께 돌려줍니다. 정렬(`Sort`)도 같은 자리에서 정해집니다.

- `Page<T>` — 전체 개수를 세는 쿼리가 한 번 더 나간다
- `Slice<T>` — 다음 페이지가 있는지만 본다 (무한 스크롤에 맞는다)

### 3-3. 비밀번호를 값으로 다루는 방식의 다음 걸음

글마다 비밀번호를 붙여 대조하는 방식은 로그인이 아니라 **값 하나**입니다. 실제 서비스로 가면 순서가 이렇게 이어집니다.

1. 저장할 때 해시로 (BCrypt), 대조는 `matches` 로 — 평문을 DB에 두지 않는다
2. 사용자 개념을 도입해 "누가 썼는가"를 세션이나 토큰으로 확인
3. Spring Security로 인증·인가를 층 바깥으로 빼기

지금 방식의 한계가 눈에 보이는 자리는 두 곳입니다 — 평문이 표에 그대로 있고, 삭제 요청에서 쿼리스트링에 실립니다.

### 3-4. 층별로 떼어 검사하기

다섯 갈래를 손으로 눌러 보는 대신 층마다 테스트를 두면 어디가 깨졌는지가 바로 갈립니다.

| 표시 | 띄우는 범위 |
| --- | --- |
| `@DataJpaTest` | JPA 층만 (내장 DB) |
| `@WebMvcTest` | 컨트롤러만 (서비스는 가짜로) |
| `@SpringBootTest` | 전부 |

위 둘이 빠른 이유는 **필요한 층만 띄우기** 때문입니다. 층을 나눠 둔 값어치가 여기서 한 번 더 나옵니다.

### 3-5. 다음에 볼 키워드

- `@Transactional` 의 전파 속성과 프록시 기반 동작(같은 클래스 안 호출에서 안 걸리는 자리)
- `@Valid`·`@NotBlank` 로 형식 검사를 컨트롤러 앞단에 두기
- `@RestControllerAdvice` 로 예외를 응답 모양으로 옮기기
- `Page`·`Slice`·`Sort` 와 커서 기반 페이징
- 조회 전용 DTO 프로젝션(인터페이스 프로젝션, `@Query` + `new` 표현식)
- BCrypt·Spring Security로 넘어가는 인증 흐름

## 실습 파일

- `2026B_Spring/demo/src/main/java/com/example/demo/model/repository/BoardRepository.java`, `CommentRepository.java` (**규약만 물려받는 층** — 두 파일이 인터페이스 이름과 제네릭 첫 자리만 갈리고 PK 타입이 같아 둘째 자리도 같은 실측, `interface` 여야 실행 중에 구현이 끼워지는 점과 `@Repository` 가 계층 표시이자 DB 예외를 표준 예외로 바꾸는 두 몫, 이 층이 주는 도구가 넷뿐이라 그 조합으로 안 되는 일은 전부 서비스 몫이 되는 경계)
- `2026B_Spring/demo/src/main/java/com/example/demo/service/BoardService.java` (**게시글 세 갈래** — 등록의 변환→저장→판정 세 줄이 DTO·리포지토리·서비스 몫으로 갈리고 성공 판정을 돌려받은 엔티티의 PK로 하는 전제·`Integer` 라야 "아직 없음"이 표현되는 점, 목록 조회의 두 겹 조립에서 바깥이 줄 수를 안쪽이 깊이를 정하는 대비와 `from()` 이 목록을 비워 둬 조립이 서비스로 넘어오는 경계선·getter가 목록 참조를 돌려줘 setter 없이 붙는 표기·컬렉션을 건드리는 순간 지연 로딩이 나가 1+N이 컬렉션 쪽에서 생기는 자리, 삭제의 조회→대조→삭제 세 걸음과 `deleteById` 대신 `findById` 를 쓰는 이유가 "지우기 전에 값을 봐야 해서"인 점·없음과 불일치가 같은 `false` 로 뭉치는 자리·`equals` 에서 저장된 쪽을 앞에 두는 표기·`cascade = ALL` 이 실제로 번지는 확인)
- `2026B_Spring/demo/src/main/java/com/example/demo/service/CommentService.java` (**번호를 객체로 바꿔 끼우는 네 단계** — 웹은 번호로 JPA는 객체 참조로 관계를 담아 생기는 틈을 서비스가 메우는 배치와 `toEntity()` 가 그 일을 못 하는 이유가 능력이 아니라 "DTO는 리포지토리를 모른다"는 층 경계인 점, `findById` 가 부모 얻기와 없는 번호 걸러 내기를 겸해 DB 외래키 제약보다 앞에서 값으로 막는 자리와 서비스 검사(값)·DB 제약(예외)의 대비, 서비스 하나가 자기 표와 이웃 표의 리포지토리를 함께 드는 자리와 "서비스의 단위는 표 하나가 아니라 하나의 일"이라는 정리·조회와 저장 사이의 틈이 곧 `@Transactional` 이 붙는 자리인 점, 댓글 삭제는 자식이 없어 `cascade` 가 번질 곳이 없는 대비)
- `2026B_Spring/demo/src/main/java/com/example/demo/controller/BoardController.java`, `CommentController.java` (**주소 설계와 매핑 구조** — 댓글을 게시글 아래에 붙이는 갈래와 나란히 두는 갈래의 성질 대비 및 기준이 "댓글을 게시글의 일부로 볼 것인가 그 자체로 다룰 자원으로 볼 것인가"인 점, 클래스 앞머리와 메소드 방식 표시가 이어 붙어 한 자리가 되는 구조와 표시가 없으면 컴파일·기동은 지나가고 호출에서 404가 되는 자리·주소 표에 올랐는지부터 보는 진단 순서 넷, 무엇을 받는가가 표시를 정하는 갈림(`@RequestBody`·`@RequestParam`)과 DELETE에 본문을 잘 안 싣는 관용·쿼리스트링이 주소창과 로그에 남는 부담·`@RequestParam(name=…)` 으로 바깥 이름과 자바 매개변수 이름을 갈라 두는 표기, 컨트롤러 본문이 한 줄로 남는 것이 "판단은 서비스가 HTTP 표현은 컨트롤러가"라는 층 나누기의 결과인 점)

## 관련 노트

[[Spring MOC]] · [[Spring day08 새 프로젝트로 옮겨 담는 도메인 층]] · [[Spring day08 요구사항 명세를 API 규격으로 옮기기]] · [[KDT_2026 학습 지도]]
