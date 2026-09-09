---
출처: Claude 분석
원본: KDT_2026/2026B_Spring/springweb/src/main/java/day07/practice5_test, springweb/src/main/resources/application.properties
작성일: 2026-09-08
tags: [학습, java]
---

# Spring day08 — 요구사항 명세를 API 규격으로 옮기기

> 실습 파일: `springweb/src/main/java/day07/practice5_test/` (`AppStart.java`, `model/entity`, `model/dto`, `model/repository`, `service`, `controller`), `springweb/src/main/resources/application.properties`
> 허브: [[Spring MOC]] · 이전: [[Spring day08 옮겨 담은 프로젝트에 상위 층 얹기]] · 다음: [[Spring day08 다른 클래스의 메소드를 부르는 네 가지 길]]

같은 게시판을 세 번째로 짰습니다. 앞의 두 번과 갈리는 점은 **요구사항 문서가 먼저 있다**는 것입니다. 조건 1부터 5까지가 엔티티 설계·감사 필드·REST API 규격·프론트 연동·시드 SQL로 나뉘어 적혀 있고, 그 문서를 읽어 각 조건이 어느 파일의 어느 줄로 내려앉는지를 정하는 것이 이번 작업이었습니다.

코드를 짜는 일과 **명세를 읽는 일**이 갈리는 자리입니다. 앞서는 "무엇을 만들지"를 스스로 정하면서 짰는데, 이번에는 주소·쿼리 파라미터 이름·응답에 들어갈 필드가 밖에서 정해져 옵니다. 그러면 **내 자유는 어디까지이고 맞춰야 하는 것은 무엇인지**가 선명해집니다.

## 1. 배운 내용

### 1-1. 조건 다섯 개가 내려앉는 자리

명세의 조건을 파일 기준으로 다시 정리하면 이렇게 갈립니다.

| 조건 | 내려앉는 곳 |
| --- | --- |
| 1. 엔티티 설계 | `model/entity/BoardEntity.java`, `CommentEntity.java` |
| 2. `BaseTime` 설계 | `model/entity/BaseTime.java` + `AppStart.java` |
| 3. REST API 기능 | `controller/`, `service/` |
| 4. 프론트엔드 연동 | 응답 DTO의 필드 이름 + 정적 파일 배치 경로 |
| 5. 샘플 SQL | `resources/sql/` + `application.properties` 의 시드 줄 |

눈에 띄는 것은 **조건 하나가 파일 하나로 안 떨어지는 자리**입니다. 조건 2(감사 필드)는 `BaseTime` 과 `AppStart` 두 파일에 걸쳐 있고, 조건 4(프론트 연동)는 파일이 아니라 **DTO 필드 이름이라는 계약**으로 존재합니다. 명세의 문단 나눔과 코드의 파일 나눔이 같은 축이 아니라는 뜻입니다.

조건 3이 서비스와 컨트롤러 둘로 갈리는 것도 같은 이야기입니다. 명세는 "기능"으로 적히는데 코드는 "층"으로 나뉘어서, 기능 하나가 컨트롤러 한 줄 + 서비스 한 덩어리로 쪼개집니다.

### 1-2. 명세가 정한 것과 내가 정하는 것

명세를 읽으며 갈라 본 결과입니다.

| 명세가 정함 | 내가 정함 |
| --- | --- |
| 주소 (`/api/board`, `/api/board/comments`) | 서비스 메소드 이름 |
| HTTP 방식 (POST·GET·DELETE) | 클래스를 몇 개로 나눌지 |
| 쿼리 파라미터 이름 (`id`·`password`·`commentId`) | 자바 매개변수 이름 |
| 요청 본문에 담기는 필드 | DTO의 변환 메소드 모양 |
| 응답에 들어가야 하는 값 (`createdAt`·`comments`) | 그 값을 어느 층에서 채울지 |
| 엔티티 필드와 관계 표시 | 계층 폴더 구조 |
| DB 이름·시드 데이터 | `ddl-auto` 같은 실행 설정 |

**왼쪽 열은 전부 "밖에서 보이는 것"입니다.** 주소, 방식, 키 이름, 응답 모양 — 화면이나 다른 서버가 이 코드를 부를 때 눈에 닿는 면입니다. 오른쪽은 안에서 어떻게 짜든 밖에서 구별되지 않는 것들입니다.

이 갈림이 곧 **공개 규격(API)과 구현의 경계**입니다. 왼쪽을 바꾸면 부르는 쪽이 깨지고, 오른쪽은 마음대로 바꿔도 됩니다.

### 1-3. 쿼리 파라미터 이름이 계약이다

명세가 댓글 삭제를 `DELETE /api/board/comments?commentId={commentId}&password={password}` 로 정해 뒀습니다. 바깥 이름은 `commentId` 인데, 자바 쪽에서는 `id` 로 받고 싶을 수 있습니다.

```java
@DeleteMapping("")
public boolean commentDelete(
        @RequestParam(name = "commentId") Integer id,
        @RequestParam(name = "password") String password) {
    return commentService.commentDelete(id, password);
}
```

`name` 속성이 **바깥 이름과 안쪽 이름을 갈라 두는 자리**입니다. 이름이 같을 때는 생략해도 되지만, 적어 두면 두 가지가 따라옵니다.

- 컴파일 옵션에 따라 매개변수 이름이 결과물에 안 남는 경우에도 안전하다
- 이 줄만 보면 **바깥에서 무슨 이름으로 오는지**가 바로 읽힌다

게시글 삭제 쪽은 `id` 로 오고 댓글 삭제 쪽은 `commentId` 로 오는데, 자바 매개변수는 둘 다 `id` 입니다. 밖이 다르고 안이 같은 이 상태를 표기로 흡수하는 자리입니다.

### 1-4. 주소를 아래에 붙이기

명세는 댓글 주소를 `/api/board/comments` 로 게시글 아래에 두었습니다.

```java
@RestController
@RequestMapping("/api/board/comments")
public class CommentController { ... }
```

앞 실습에서 나란히 두는 갈래(`/api/comments`)를 써 봤기 때문에 대비가 선명합니다. 아래에 붙이면 **주소가 소속을 드러냅니다** — 댓글은 게시글에 딸린 것이고, 부모 없이 댓글만 다루는 요청은 이 구조에서 자연스럽지 않습니다.

한 가지 주의할 점은 앞머리가 겹친다는 것입니다.

```
POST   /api/board              → 게시글 등록
GET    /api/board              → 게시글 목록
DELETE /api/board              → 게시글 삭제
POST   /api/board/comments     → 댓글 등록
DELETE /api/board/comments     → 댓글 삭제
```

`/api/board` 와 `/api/board/comments` 는 문자열이 겹치지만 완전히 같지는 않아서 충돌하지 않습니다. 다만 **주소 + 방식의 짝이 완전히 같아지면** 서버가 뜰 때 걸립니다. 앞머리를 겹쳐 쓸 때 눈여겨볼 자리입니다.

### 1-5. 응답 모양이 화면과 맺은 계약

명세의 조건 3에 "각 게시글 정보에는 작성일시(`createdAt`)와 해당 게시글에 달린 댓글 목록(`comments`)이 함께 포함되어야 한다"고 적혀 있습니다. 이 한 줄이 DTO의 모양을 정합니다.

```java
public class BoardDto {
    private Integer id;
    private String author;
    private String password;
    private String content;
    private LocalDateTime createdAt;
    private LocalDateTime upDatedAt;

    @Builder.Default
    private List<CommentDto> comments = new ArrayList<>();
    ...
}
```

**자바 필드 이름이 그대로 JSON 키가 되기 때문에**, 화면 코드가 `board.comments` 로 읽는다면 필드 이름이 `comments` 여야 합니다. 이름을 다르게 두고 싶으면 `@JsonProperty` 로 갈라 둘 수 있지만, 그러면 값을 따라갈 때 한 단계가 더 늡니다.

한 값이 지나가는 자리를 세어 보면 넷입니다.

```
DB 컬럼(created_at) → 엔티티 필드(createdAt) → DTO 필드(createdAt) → JSON 키(createdAt) → 화면 코드
```

카멜↔스네이크 변환이 첫 칸에서 자동으로 일어나고, 나머지는 손으로 맞춥니다. **이름을 층마다 다르게 둘 수는 있지만 그럴 이유가 있을 때만** 두는 편이 낫습니다.

### 1-6. 감사 필드 세 자리를 다시

조건 2가 요구하는 것을 표시 단위로 풀면 이렇습니다.

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

```java
@SpringBootApplication
@EnableJpaAuditing
public class AppStart { ... }
```

| 자리 | 표시 | 없으면 |
| --- | --- | --- |
| 필드 | `@CreatedDate`·`@LastModifiedDate` | 값이 안 채워진다 |
| 클래스 | `@EntityListeners(AuditingEntityListener.class)` | 채워 줄 구현체가 안 붙는다 |
| 진입점 | `@EnableJpaAuditing` | 감사 기능 자체가 안 켜진다 |

셋 중 하나만 빠져도 **오류 없이 `null` 로 남습니다.** 명세가 이 조건을 따로 떼어 적어 둔 것도 세 자리가 서로 다른 파일에 흩어져 있어 빠뜨리기 쉬운 자리이기 때문일 것입니다.

`@MappedSuperclass` 는 자기 표를 갖지 않는 필드 묶음이라는 표시라, `extends BaseTime` 을 건 엔티티의 표에만 두 컬럼이 붙습니다.

### 1-7. 명세의 관계 표시를 그대로 옮기기

조건 1이 관계 표시를 문자 그대로 적어 두었습니다 — `@OneToMany(mappedBy = "boardEntity", cascade = CascadeType.ALL)` 와 `@ManyToOne`, `@JoinColumn(name = "board_id")`.

```java
@OneToMany(mappedBy = "boardEntity", cascade = CascadeType.ALL, fetch = FetchType.LAZY)
@ToString.Exclude
@Builder.Default
private List<CommentEntity> comments = new ArrayList<>();
```

`mappedBy = "boardEntity"` 가 **상대 엔티티의 자바 필드 이름**을 가리키므로, 자식 쪽 필드를 `boardEntity` 로 두는 것이 명세에서 이미 정해진 셈입니다. 이름이 어긋나면 컴파일은 지나가고 서버가 뜰 때 걸립니다.

`@JoinColumn(name = "board_id")` 도 마찬가지로 조건 5의 시드 SQL이 쓰는 컬럼 이름과 짝입니다. 명세의 조건 1과 조건 5가 **같은 이름 하나를 양쪽에서 잡고 있는** 구조라, 한쪽을 바꾸면 다른 쪽도 함께 봐야 합니다.

명세에 안 적혀 있지만 함께 붙인 두 표시도 있습니다.

| 표시 | 막는 것 |
| --- | --- |
| `@ToString.Exclude` | `toString()` 이 양쪽을 왕복하다 스택이 넘치는 것 |
| `@Builder.Default` | 빌더로 만들 때 목록이 `null` 이 되는 것 |

**명세는 도메인 요구를 적고, 이 둘은 도구(롬복)를 쓰기 때문에 따라오는 것**이라는 갈림입니다.

### 1-8. 설정에서 실습마다 손대는 두 줄

```properties
spring.datasource.url = jdbc:mysql://localhost:3306/test5
...
spring.jpa.hibernate.ddl-auto=create-drop
spring.jpa.show-sql=true
spring.jpa.properties.hibernate.format_sql=true
spring.sql.init.data-locations=classpath:/sql/practice5.sql
spring.jpa.defer-datasource-initialization=true
spring.sql.init.mode=always
spring.sql.init.encoding=UTF-8
```

실습이 늘 때 실제로 손대는 것은 **DB 주소와 시드 경로 두 줄**뿐이고, 나머지는 한 번 맞춰 두면 그대로 갑니다. 시드 쪽 네 줄이 늘 함께 다니는 이유를 다시 적으면 이렇습니다.

- `data-locations` — 어느 파일을 읽을지 (`classpath:` 는 `src/main/resources`)
- `defer-datasource-initialization=true` — 시드를 **표 생성 뒤로** 미룬다
- `sql.init.mode=always` — 기본값 `embedded` 는 내장 DB에서만 돌므로 MySQL에서는 켜 준다
- `sql.init.encoding=UTF-8` — 한글 시드가 깨지지 않게 읽을 인코딩

`ddl-auto=create-drop` 과 `show-sql` 의 조합이 실습에서 값을 하는 자리도 그대로입니다. 엔티티만 고쳐 서버를 다시 띄우면 콘솔에 나오는 `create table` 문으로 표 모양이 바로 확인됩니다.

접속 정보가 설정 파일에 평문으로 남는 성질도 여기서 다시 걸립니다. 실습용 로컬 DB라 넘어가지만, 이 파일이 형상관리에 그대로 올라가는 자리라는 점은 기억해 둘 만합니다.

### 1-9. 세 번 짜 보고 남는 것

같은 게시판을 패키지 하나(`pratice5_Repeat`), 새 프로젝트(`demo`), 그리고 명세를 놓고(`practice5_test`) 세 번 짰습니다. 매번 갈리는 것을 층으로 세어 보면 이렇습니다.

| 층 | 세 번 사이의 갈림 |
| --- | --- |
| 엔티티 | 거의 없음 (`package` 두 줄) |
| DTO | 거의 없음 |
| 리포지토리 | 없음 |
| 서비스 | 거의 없음 |
| 컨트롤러 | 주소·파라미터 이름 |
| 설정 | DB 이름·시드 경로 |

**갈림이 바깥층에 몰려 있습니다.** 도메인이 같으면 안쪽은 그대로이고, 바뀌는 것은 밖과 맞닿는 면입니다. 반복 실습에서 얻는 것이 "손에 익는 것"만이 아니라 **어디가 변하는 부분인지에 대한 실측**이라는 점이 이번에 드러납니다.

## 2. 추가로 알면 좋은 활용법

### 2-1. 명세를 읽는 순서

문서를 위에서 아래로 읽는 대신, 코드를 짜는 순서에 맞춰 재배열하면 손이 덜 왔다 갔다 합니다.

1. **조건 5(시드 SQL)** 를 먼저 본다 — 표 이름·컬럼 이름이 여기 다 있다
2. **조건 1·2(엔티티)** 로 그 표를 자바로 옮긴다
3. **조건 3(API)** 로 컨트롤러 표를 먼저 종이에 적는다
4. 그 표를 채우는 데 필요한 서비스 메소드를 정한다
5. **조건 4(프론트)** 로 응답 DTO 필드 이름을 맞춘다

시드 SQL을 먼저 보는 이유는 **컬럼 이름이 명세에서 가장 구체적인 부분**이라서입니다. `board_id`·`created_at` 같은 이름이 엔티티 필드 이름과 `@JoinColumn` 을 거꾸로 정해 줍니다.

### 2-2. 컨트롤러 표를 먼저 적어 두기

| 방식 | 주소 | 받는 것 | 돌려주는 것 |
| --- | --- | --- | --- |
| POST | `/api/board` | `BoardDto` (본문) | 성공 여부 |
| GET | `/api/board` | — | `List<BoardDto>` |
| DELETE | `/api/board` | `id`·`password` (쿼리) | 성공 여부 |
| POST | `/api/board/comments` | `CommentDto` (본문) | 성공 여부 |
| DELETE | `/api/board/comments` | `commentId`·`password` (쿼리) | 성공 여부 |

이 표가 곧 컨트롤러 파일의 목차입니다. 다섯 줄을 먼저 적어 두면 클래스를 몇 개로 나눌지, 각각 어떤 앞머리를 가질지가 표에서 바로 읽힙니다. 그리고 다 만든 뒤 **서버 시작 로그의 매핑 목록과 이 표를 대조**하면 빠뜨린 줄이 바로 나옵니다.

### 2-3. 명세를 테스트로 옮기기

컨트롤러 표의 다섯 줄은 그대로 테스트 다섯 개가 됩니다.

```
POST /api/board 로 등록하면 → GET /api/board 목록에 그 글이 있다
POST /api/board/comments 로 댓글을 달면 → 그 글의 comments 에 들어 있다
DELETE /api/board 를 맞는 비밀번호로 부르면 → 목록에서 사라지고 댓글도 사라진다
DELETE /api/board 를 틀린 비밀번호로 부르면 → 그대로 남는다
```

손으로 눌러 보는 확인은 매번 처음부터 다시 해야 하는데, 테스트로 옮기면 **한 번 적어 두고 계속 돌립니다.** 명세가 있는 실습이 테스트를 쓰기 좋은 이유는 확인할 항목이 이미 문장으로 적혀 있기 때문입니다.

### 2-4. API 문서를 코드에서 뽑기

컨트롤러 표를 사람이 관리하면 코드와 어긋나기 시작합니다. `springdoc-openapi` 같은 도구를 넣으면 매핑 표시와 DTO를 읽어 OpenAPI 문서를 만들어 주고, 브라우저에서 바로 눌러 볼 수 있는 화면(Swagger UI)까지 나옵니다.

- 장점: 코드가 곧 문서라 어긋날 여지가 줄어든다
- 한계: 주소와 타입은 나오지만 "왜 이 규격인가"는 안 나온다

### 2-5. 응답에서 비밀번호를 빼기

지금 `BoardDto` 는 요청과 응답에 같이 쓰이는 겸용이라, 목록 응답에도 `password` 자리가 함께 나갑니다. 빼는 갈래가 셋 있습니다.

| 갈래 | 방법 |
| --- | --- |
| 변환에서 안 담기 | `from()` 에서 그 줄을 뺀다 |
| 표시로 막기 | `@JsonProperty(access = Access.WRITE_ONLY)` |
| DTO를 나누기 | 요청용·응답용을 따로 둔다 |

셋째가 가장 확실하지만 파일이 늘어납니다. 겸용 DTO는 갈래마다 **절반이 비는 필드**가 생기는 성질이 있어서, 필드가 늘수록 나누는 쪽이 유리해집니다.

## 3. 더 나아가 알면 좋은 것

### 3-1. 계약을 먼저 쓰는 방식

지금은 명세가 한국어 문서로 오고 그것을 코드로 옮겼습니다. 실무에서는 그 자리를 기계가 읽을 수 있는 형식이 대신하기도 합니다.

| 방식 | 성질 |
| --- | --- |
| 코드 먼저 → 문서 생성 | 어긋날 여지가 적다. 프론트가 기다려야 한다 |
| 문서(OpenAPI) 먼저 → 양쪽이 구현 | 프론트·백엔드가 동시에 간다. 문서를 고치는 합의가 필요하다 |

둘째를 **계약 우선(contract first)** 이라 부릅니다. OpenAPI 문서에서 서버 뼈대와 클라이언트 코드를 함께 뽑아낼 수도 있습니다. 이번 실습의 "명세를 먼저 읽고 짠다"가 그 방식의 손으로 하는 판이라고 볼 수 있습니다.

### 3-2. 값 검증을 어디에 둘 것인가

명세에 "일치 여부 확인 후 삭제"는 있지만 "빈 작성자를 막는다" 같은 조건은 없습니다. 실제로는 세 자리에서 걸러집니다.

| 자리 | 거르는 것 |
| --- | --- |
| 화면 | 눌러 보기 전에 (사용자 편의) |
| 서버(`@Valid`·`@NotBlank`) | 형식 — 비었는가·길이가 넘는가 |
| DB 제약(`nullable`·`length`·유니크) | 마지막 방어선 |

화면의 `.value` 는 언제나 문자열이라 **빈 문자열이 `nullable = false` 를 통과합니다.** 세 자리를 겹쳐 두는 이유가 여기 있습니다. 앞의 둘은 편의와 응답 품질이고, 데이터를 실제로 지키는 것은 마지막 자리입니다.

### 3-3. 로컬 서버를 밖에서 부를 수 있게 하기

명세의 제출 방법이 터널링 도구로 `localhost:8080` 을 임시 주소에 붙이는 방식입니다. 원리는 **내 컴퓨터에서 바깥 서비스로 연결을 걸어 두고, 그 통로로 요청을 되돌려 받는** 것입니다.

| 방식 | 성질 |
| --- | --- |
| 터널링 | 방화벽·공유기 설정을 안 건드린다. 주소가 임시다 |
| 포트포워딩 | 공유기 설정이 필요하고 고정 주소가 있어야 쓸 만하다 |
| 실제 배포 | 서버·도메인·인증서까지 붙는다 |

임시 주소가 뜨는 동안에는 **누구나 그 주소로 들어올 수 있다**는 점이 함께 따라옵니다. 확인이 끝나면 통로를 닫는 습관이 필요하고, 로컬 DB에 실제 값이 들어 있는 상태로 열어 두지 않는 편이 안전합니다.

### 3-4. 명세에 없는 것을 어디까지 채울 것인가

명세는 성공 경로만 적는 경우가 많습니다. 이번 문서에도 "없는 번호로 부르면" "비밀번호가 틀리면" 무엇을 돌려줄지는 안 적혀 있습니다.

실무에서 이 빈칸을 메우는 순서는 대개 이렇습니다.

1. 빈칸이 있다는 것을 먼저 알아채고 목록으로 적는다
2. 명세를 준 쪽에 물어볼 것과 스스로 정할 것을 가른다
3. 스스로 정한 것은 **어딘가에 적어 둔다** (주석이 아니라 문서나 테스트로)

3번이 요점입니다. 정한 것을 안 적어 두면 다음 사람이 다시 같은 빈칸을 만납니다.

### 3-5. 다음에 볼 키워드

- OpenAPI 3 문서 구조와 `springdoc-openapi`·Swagger UI
- 계약 우선 개발과 코드 생성(openapi-generator)
- `@Valid`·`@Validated` 와 검증 애노테이션들·`@RestControllerAdvice` 로 검증 오류 응답 모으기
- REST 자원 설계에서 중첩 자원(`/boards/{id}/comments`)과 `@PathVariable`
- 상태 코드로 실패를 가르기 (204·400·403·404·409)
- 소비자 주도 계약 테스트(consumer-driven contract)

## 실습 파일

- `2026B_Spring/springweb/src/main/java/day07/practice5_test/readme.md` (**명세를 코드 자리로 나누는 작업** — 조건 다섯이 파일로 내려앉는 표와 조건 하나가 파일 하나로 안 떨어지는 자리(감사 필드는 두 파일에·프론트 연동은 DTO 필드 이름이라는 계약으로), 명세의 문단 나눔이 "기능" 축이고 코드의 나눔이 "층" 축이라 기능 하나가 컨트롤러 한 줄과 서비스 한 덩어리로 쪼개지는 대비, 명세가 정하는 것과 내가 정하는 것의 갈림이 곧 "밖에서 보이는 면"과 구현의 경계인 정리, 명세를 읽는 순서를 코드 짜는 순서로 재배열하기(시드 SQL의 컬럼 이름이 가장 구체적이라 먼저 보는 자리))
- `2026B_Spring/springweb/src/main/java/day07/practice5_test/model/entity/BaseTime.java`, `BoardEntity.java`, `CommentEntity.java` (**명세의 표시를 그대로 옮기는 자리** — 감사가 도는 세 자리(필드 표시·엔티티 리스너·진입점 활성화)와 하나만 빠져도 오류 없이 `null` 로 남는 점·명세가 이 조건을 따로 떼어 적어 둔 이유, `@MappedSuperclass` 가 자기 표를 안 갖는 필드 묶음이라는 표시인 점, `mappedBy` 가 상대 엔티티의 자바 필드 이름이라 자식 쪽 필드 이름이 명세에서 이미 정해진 셈인 자리와 어긋나면 서버가 뜰 때 걸리는 점, `@JoinColumn(name="board_id")` 이 조건 5의 시드 SQL 컬럼 이름과 짝이라 한쪽을 바꾸면 다른 쪽도 함께 봐야 하는 구조, 명세에 없는데 함께 붙는 `@ToString.Exclude`·`@Builder.Default` 가 도메인 요구가 아니라 도구를 써서 따라오는 것이라는 갈림)
- `2026B_Spring/springweb/src/main/java/day07/practice5_test/model/dto/BoardDto.java`, `CommentDto.java` (**응답 모양이 화면과 맺은 계약** — "작성일시와 댓글 목록이 포함되어야 한다"는 한 줄이 DTO 필드 모양을 정하는 자리와 자바 필드 이름이 그대로 JSON 키가 되므로 화면이 읽는 이름과 맞춰야 하는 점·`@JsonProperty` 로 갈라 두면 값을 따라갈 때 한 단계가 느는 대가, 한 값이 DB 컬럼→엔티티 필드→DTO 필드→JSON 키→화면 코드로 다섯 자리를 지나며 첫 칸만 자동 변환이고 나머지는 손으로 맞추는 실측, 겸용 DTO라 응답에도 비밀번호 자리가 함께 나가는 성질과 빼는 갈래 셋)
- `2026B_Spring/springweb/src/main/java/day07/practice5_test/controller/BoardController.java`, `CommentController.java` (**주소·파라미터 규격을 맞추는 자리** — 댓글 주소를 게시글 아래에 붙여 소속을 드러내는 갈래와 앞 실습의 나란히 두는 갈래의 대비, 앞머리가 겹쳐도 완전히 같지 않으면 충돌하지 않고 주소+방식의 짝이 같아지면 서버가 뜰 때 걸리는 점, `@RequestParam(name="commentId")` 이 바깥 이름과 자바 매개변수 이름을 갈라 두는 표기이고 밖은 다르고 안은 같은 상태를 흡수하는 자리·컴파일 옵션에 따라 매개변수 이름이 결과물에 안 남는 경우까지 덮는 안전장치인 점, 컨트롤러 표 다섯 줄을 먼저 적어 두고 서버 시작 로그의 매핑 목록과 대조하는 확인 방법)
- `2026B_Spring/springweb/src/main/java/day07/practice5_test/service/BoardService.java`, `CommentService.java`, `model/repository/` (**세 번째로 밟는 같은 층** — 등록의 변환→저장→PK 판정·조회의 두 겹 조립·삭제의 조회→대조→삭제·댓글 등록의 번호를 객체로 바꿔 끼우는 네 단계가 세 번 모두 같은 모양으로 나오는 실측과 갈림이 바깥층(주소·파라미터 이름·설정)에 몰려 있다는 정리, 반복 실습에서 얻는 것이 손에 익는 것만이 아니라 "어디가 변하는 부분인지"에 대한 실측이라는 점)
- `2026B_Spring/springweb/src/main/resources/application.properties` (**실습마다 손대는 두 줄** — DB 주소와 시드 경로만 갈리고 나머지는 한 번 맞춰 두면 그대로 가는 배치, 시드 네 줄이 함께 다니는 이유(파일 지정·표 생성 뒤로 미루기·MySQL에서도 돌게 하기·한글 인코딩)와 `ddl-auto=create-drop`+`show-sql` 로 엔티티만 고쳐 표 모양을 확인하는 통로, 접속 정보가 설정 파일에 평문으로 남아 형상관리에 그대로 올라가는 자리)

## 관련 노트

[[Spring MOC]] · [[Spring day08 옮겨 담은 프로젝트에 상위 층 얹기]] · [[Spring day08 다른 클래스의 메소드를 부르는 네 가지 길]] · [[KDT_2026 학습 지도]]
