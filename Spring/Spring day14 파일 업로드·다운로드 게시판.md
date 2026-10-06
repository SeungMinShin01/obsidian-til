---
출처: Claude 분석
원본: KDT_2026/2026B_Spring/springweb/src/main/java/day14
작성일: 2026-10-02
tags: [학습, java]
---

# Spring day14 — 파일 업로드·다운로드 게시판

> 실습 파일: `day14/BaseTime.java`, `BoardEntity.java`, `BoardRepository.java`, `BoardDto.java`, `BoardService.java`, `BoardController.java`, `FileService.java`
> 허브: [[Spring MOC]] · 이전: [[Spring day13 레디스 리스트로 값 쌓고 읽기]] · 다음: (아직 없음)

day14는 게시판 CRUD에 **첨부파일**을 얹는 날이다. 글 등록 요청에 파일이 함께 들어오면 서버 폴더에 저장하고, 저장된 파일 이름만 DB에 남기고, 나중에 그 이름으로 다운로드해 준다. 엔티티·리포지토리·서비스·컨트롤러의 계층 흐름은 이전 게시판 실습과 같고, 파일을 다루는 `FileService`가 새로 끼어든다.

## 1. 배운 내용

### 1-1. 엔티티와 감사 필드 분리 — `BaseTime`

```java
@Getter
@MappedSuperclass
@EntityListeners(AuditingEntityListener.class)
public class BaseTime {
    @CreatedDate
    private LocalDateTime createDate;
    @LastModifiedDate
    private LocalDateTime updateDate;
}

@Entity @Table(name = "board")
public class BoardEntity extends BaseTime {
    @Id @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    private String title;
    private String content;
    private String fileName;   // 서버에 저장된 첨부파일명
}
```

- 작성일·수정일을 모든 엔티티에 반복해서 쓰지 않도록 부모 클래스로 빼 둔다. `@MappedSuperclass`는 "테이블이 되지는 않지만 컬럼만 자식 엔티티에 물려주는 클래스"라는 표시다.
- `@EntityListeners(AuditingEntityListener.class)`와 `@CreatedDate`·`@LastModifiedDate` 조합으로 저장·수정 시각이 자동으로 채워진다. 이 동작은 앱 시작 클래스의 `@EnableJpaAuditing`이 켜져 있어야 작동한다(day12에서 정리).
- 파일 자체는 DB에 넣지 않고 **파일명(`fileName`) 문자열만** 컬럼으로 둔다. 파일 본체는 서버 폴더에, DB에는 그것을 찾아갈 이름만 남기는 구조다.

### 1-2. DTO — 업로드용 필드와 출력용 필드를 나란히

```java
public class BoardDto {
    private Long id;
    private String title;
    private String content;
    private MultipartFile file;      // 업로드용(등록 시 받는 값)
    private String fileName;         // 출력용(저장된 파일명)
    private LocalDateTime createDate;

    public BoardEntity toEntity() { ... }                       // title·content만 옮김
    public static BoardDto fromEntity(BoardEntity entity) { ... } // fileName·createDate 포함
}
```

- 파일은 글자가 아닌 바이트라서 `String`이 아니라 `MultipartFile` 인터페이스로 받는다. 같은 DTO 안에서 `file`은 요청 쪽, `fileName`은 응답 쪽으로 역할이 갈린다.
- `toEntity()`에는 `file`을 옮기지 않는다. 파일명은 업로드가 끝난 뒤 서비스가 따로 `setFileName`으로 채우기 때문이다.
- 첨부파일을 여러 개 받으려면 `List<MultipartFile>`로 바꾸면 된다(주석으로 남겨 둔 방향).

### 1-3. 컨트롤러 — `@ModelAttribute`로 폼 데이터 받기

```java
@CrossOrigin(origins = "http://localhost:5173")
@RestController
@RequestMapping("/api/board")
public class BoardController {
    @PostMapping("/write")
    public boolean write(@ModelAttribute BoardDto dto) { ... }

    @GetMapping("/list")
    public List<BoardDto> list() { ... }

    @GetMapping("/view")
    public BoardDto view(@RequestParam(name = "id") Long id) { ... }

    @GetMapping("/download/{id}")
    public void download(@PathVariable(name = "id") Long id, HttpServletResponse response) {
        String fileName = boardService.getFileName(id);
        if (fileName != null) {
            fileService.fileDownload(fileName, response);
        }
    }
}
```

- 파일이 섞인 요청은 `multipart/form-data` 형식으로 오고, JSON 본문이 아니므로 `@RequestBody`가 아니라 `@ModelAttribute`로 DTO에 바인딩한다. 폼 필드 이름(`title`·`content`·`file`)이 DTO 멤버 이름과 같아야 채워진다.
- 다운로드는 응답 본문으로 객체를 돌려주는 대신, 반환형을 `void`로 두고 `HttpServletResponse`에 바이트를 직접 써 보낸다.
- `@PathVariable(name = "id")`는 `/download/3`처럼 경로 일부를 값으로 받는 방식이다. 쿼리스트링으로 받는 `@RequestParam`(`/view?id=3`)과 구분해 둔다.
- 리액트 개발 서버 포트(5173)의 요청을 허용하는 `@CrossOrigin`이 붙어 있다.

### 1-4. 서비스 — 업로드 먼저, 저장은 그다음

```java
public boolean boardWrite(BoardDto dto) {
    String savedFileName = null;
    if (dto.getFile() != null && !dto.getFile().isEmpty()) {
        savedFileName = fileService.fileUpload(dto.getFile());
        if (savedFileName == null) return false;   // 업로드 실패
    }
    BoardEntity entity = dto.toEntity();
    entity.setFileName(savedFileName);
    boardRepository.save(entity);
    return true;
}
```

- 순서는 **① 첨부파일이 있는지 확인 → ② 업로드하고 저장된 이름 받기 → ③ 그 이름을 엔티티에 넣어 저장**이다. 업로드가 실패하면 DB에 글을 넣지 않고 `false`를 돌려준다.
- 첨부파일이 없는 글은 `fileName`이 `null`인 채로 저장된다.
- 목록 조회는 `findAll().stream().map(BoardDto::fromEntity).collect(...)`, 개별 조회와 파일명 조회는 `findById`의 `Optional`을 풀어서 없으면 `null`을 돌려주는 형태다.

### 1-5. `FileService` — 업로드·다운로드·삭제

**저장 경로**

```java
private String baseDir = System.getProperty("user.dir");
private String uploadPath = baseDir + "/build/resources/main/static/upload/";
```

- `user.dir`은 현재 프로젝트 최상위 폴더다. 거기서 `build` 폴더 아래 `static/upload/`를 저장 위치로 삼는다.
- 코드를 쓰는 `src` 폴더가 아니라 실행 결과물이 놓이는 `build` 폴더에 올리는 이유가 주석에 정리되어 있다. 일반 사용자의 업로드는 개발자 폴더가 아닌 서버 폴더로 가야 하고, 클라우드(AWS 등)로 옮기면 이 경로가 클라우드 쪽 주소로 바뀐다.

**업로드**

```java
File dir = new File(uploadPath);
if (!dir.exists()) dir.mkdir();

String fileName = UUID.randomUUID().toString() + "_"
        + multipartFile.getOriginalFilename().replaceAll("_", "-");
multipartFile.transferTo(new File(uploadPath + fileName));
return fileName;
```

- 업로드 폴더가 없으면 먼저 만든다. `File`은 운영체제의 파일·폴더를 다루는 자바 클래스다.
- 서로 다른 사람이 같은 이름(`짱구.jpg`)으로 올려도 덮어쓰지 않도록 이름 앞에 `UUID`를 붙인다. 식별자로는 UUID 외에 업로드 일시나 게시물 번호를 쓰는 방법도 있다.
- UUID와 원래 이름을 `_`로 이어 붙이기 때문에, 원래 이름 안의 `_`는 `replaceAll("_", "-")`로 미리 바꿔 둔다. 나중에 `_` 기준으로 잘라 원래 이름을 되살리기 위한 약속이다.
- `transferTo(File)`이 임시로 받아 둔 업로드 내용을 지정한 경로에 실제 파일로 쓴다. 예외가 날 수 있어 `try-catch`로 감싸고, 실패하면 `null`을 돌려준다.

**다운로드 — 파일 → 바이트 배열 → 응답 스트림**

```java
File file = new File(uploadPath + fileName);
if (!file.exists()) return;

byte[] bytes = new byte[(int) file.length()];
FileInputStream fin = new FileInputStream(uploadPath + fileName);
fin.read(bytes);
fin.close();

String realFileName = fileName.split("_")[1];       // UUID_짱구.jpg → 짱구.jpg
response.setHeader("Content-Disposition",
        "attachment;filename=" + URLEncoder.encode(realFileName, "UTF-8"));
ServletOutputStream fout = response.getOutputStream();
fout.write(bytes);
fout.close();
```

- 흐름은 서버 디스크의 파일 → `FileInputStream`으로 읽어 바이트 배열 → 서블릿 출력 스트림으로 내보내기 → 브라우저다.
- `Content-Disposition: attachment; filename=...` 헤더가 브라우저에 "화면에 열지 말고 저장하라"고 알려 준다. 한글 파일명이 깨지지 않도록 `URLEncoder.encode`를 거친다.
- 저장된 이름은 `UUID_원래이름` 모양이므로 `split("_")[1]`로 UUID를 떼고 원래 이름만 다운로드 이름으로 쓴다. 업로드 때 `_`를 `-`로 치환해 둔 것이 여기서 맞물린다.
- 스트림은 쓰고 나서 직접 `close()`로 닫아 준다.

**삭제**

```java
File file = new File(uploadPath + fileName);
if (file.exists()) { file.delete(); return true; }
return false;
```

- 게시물을 지울 때 첨부파일도 함께 지우기 위한 함수다. 경로에 파일이 있으면 `delete()`로 지우고 결과를 `boolean`으로 알려 준다.

### 1-6. 요청 흐름 한눈에

| 단계 | 하는 곳 | 하는 일 |
| --- | --- | --- |
| 등록 | `POST /api/board/write` | 폼(제목·내용·파일)을 `BoardDto`로 받는다 |
| 저장 | `BoardService.boardWrite` | `FileService.fileUpload`로 파일 저장 → 파일명을 엔티티에 담아 DB 저장 |
| 조회 | `GET /api/board/list`·`/view` | 파일명(`fileName`)이 담긴 DTO를 응답 |
| 다운로드 | `GET /api/board/download/{id}` | id로 파일명 조회 → `FileService.fileDownload`로 바이트 전송 |

## 2. 추가로 알면 좋은 활용법

### 2-1. 업로드 크기 제한 설정

스프링 부트는 기본 업로드 크기에 제한이 있다. `application.properties`의 `spring.servlet.multipart.max-file-size`, `max-request-size`로 한 파일·한 요청의 최대 크기를 조절한다.

### 2-2. 다운로드는 `ResponseEntity`로도 쓴다

실습은 `HttpServletResponse`에 직접 쓰는 방식이다. 같은 일을 `ResponseEntity<Resource>`에 `Content-Disposition` 헤더를 담아 반환하는 방식으로도 할 수 있어, 서블릿 객체를 직접 다루지 않는 쪽이 코드가 짧다.

### 2-3. 큰 파일은 한 번에 읽지 않기

바이트 배열을 파일 크기만큼 한 번에 만드는 방식은 큰 파일에서 메모리를 많이 쓴다. `InputStream.transferTo(출력스트림)`이나 버퍼 단위로 나눠 읽고 쓰는 방식으로 바꾸면 부담이 줄어든다.

### 2-4. 파일 저장 위치 주의

`build` 폴더는 빌드를 다시 하면 비워질 수 있어 업로드 파일이 사라질 수 있다. 개발 중에는 편하지만, 보관이 필요한 파일은 프로젝트 밖의 고정 폴더나 클라우드 저장소에 두는 편이 안전하다.

### 2-5. 목록·페이징 확인용 샘플 데이터 넣기

게시물이 몇 건 없으면 목록 화면이나 페이징 동작을 눈으로 확인하기 어렵다. 그래서 `board` 테이블에 `INSERT`를 한 번에 30건 넣어 두고 확인하는 방식을 썼다.

```sql
DROP DATABASE IF EXISTS mydb1002;
CREATE DATABASE mydb1002;
USE mydb1002;

INSERT INTO board (title, content, file_name, create_date, update_date) VALUES
('첫 번째 공지사항', '게시판 서비스 오픈을 환영합니다.', NULL, NOW(), NOW()),
('스프링 부트 파일 업로드 가이드', 'MultipartFile을 활용한 첨부파일 업로드 안내입니다.', NULL, NOW(), NOW()),
-- ... 같은 모양으로 30건까지
('30번째 게시물 테스트', '게시판 30개 샘플 데이터 삽입 및 목록 페이징 검증용 레코드입니다.', NULL, NOW(), NOW());
```

- `VALUES` 뒤에 행을 쉼표로 이어 붙이면 한 문장으로 여러 건이 들어간다. 건마다 `INSERT`를 따로 쓰는 것보다 짧고 빠르다.
- `file_name`은 첨부 없는 글이므로 `NULL`로 둔다. 엔티티의 `fileName`이 비어 있어도 되는 컬럼이라는 점과 맞는다.
- `create_date`·`update_date`는 `BaseTime`이 자동으로 채우던 컬럼이다. SQL로 직접 넣을 때는 JPA 감사 기능이 개입하지 않으므로 `NOW()`로 직접 채워야 한다.
- 실습 때마다 `DROP DATABASE IF EXISTS` → `CREATE DATABASE` → `USE`로 새 스키마를 만들고 시작하면 이전 데이터와 섞이지 않는다. 이 세 줄만 따로 모아 두면 새 실습을 시작할 때 바로 쓸 수 있다.

## 3. 더 나아가 알면 좋은 것

- 여러 파일 첨부 — `List<MultipartFile>`과 첨부파일 전용 테이블(게시물 1 : 파일 N 관계, [[Spring day06 연관관계 매핑과 외래키]]에서 다룬 매핑 활용)
- 허용 확장자·MIME 타입 검사, 실행 파일 업로드 차단 같은 업로드 보안
- 클라우드 저장소(AWS S3 등)로 업로드 위치 옮기기
- 다운로드 시 `Content-Type` 지정과 이미지 미리보기(`inline`)
- 게시물 수정·삭제 시 기존 파일 교체·삭제(`fileDelete` 활용)와 DB·파일 불일치 방지(트랜잭션)
- 화면 쪽에서 `FormData`로 파일을 실어 보내는 방법

## 실습 파일

- `KDT_2026/2026B_Spring/springweb/src/main/java/day14/BaseTime.java` — 작성일·수정일 감사 필드를 모은 `@MappedSuperclass`
- `KDT_2026/2026B_Spring/springweb/src/main/java/day14/BoardEntity.java` — `BaseTime`을 상속한 게시물 엔티티(`fileName` 컬럼 포함)
- `KDT_2026/2026B_Spring/springweb/src/main/java/day14/BoardRepository.java` — `JpaRepository` 상속 리포지토리
- `KDT_2026/2026B_Spring/springweb/src/main/java/day14/BoardDto.java` — `MultipartFile`과 `fileName`을 함께 가진 DTO
- `KDT_2026/2026B_Spring/springweb/src/main/java/day14/BoardService.java` — 업로드 후 저장하는 등록, 조회, 파일명 조회
- `KDT_2026/2026B_Spring/springweb/src/main/java/day14/BoardController.java` — `/api/board` 등록·목록·상세·다운로드 엔드포인트
- `KDT_2026/2026B_Spring/springweb/src/main/java/day14/FileService.java` — 업로드(UUID 접두)·다운로드·삭제 서비스
- `KDT_2026/2026B_Spring/springweb/src/main/resources/sql/1002.sql` — 게시물 샘플 30건 `INSERT`
- `KDT_2026/2026B_Spring/springweb/src/main/resources/sql/useDB.sql` — 실습용 스키마를 새로 만들고 선택하는 세 줄

## 관련 노트

[[Spring MOC]] · [[Spring day13 레디스 리스트로 값 쌓고 읽기]] · [[Spring day06 연관관계 매핑과 외래키]] · [[KDT_2026 학습 지도]]
