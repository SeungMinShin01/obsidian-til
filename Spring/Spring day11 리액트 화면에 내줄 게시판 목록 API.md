---
출처: Claude 분석
원본: KDT_2026/2026B_Spring/springweb/src/main/java/day11, springweb/src/main/resources/sql/sample.sql, springweb/src/main/resources/sql/sampledb.sql, springweb/src/main/resources/application.properties
작성일: 2026-09-23
tags: [학습, java]
---

# Spring day11 — 리액트 화면에 내줄 게시판 목록 API

> 실습 파일: `day11/AppStart.java`, `day11/controller/ApiController.java`, `day11/service/ApiService.java`, `day11/model/dto/ApiDto.java`, `day11/model/entity/ApiEntity.java`, `day11/model/repository/ApiRepository.java`, `resources/sql/sample.sql`, `resources/sql/sampledb.sql`, `resources/application.properties`
> 허브: [[Spring MOC]] · 이전: [[Spring day10 WebClient로 공공데이터 API 대신 호출하기]] · 다음: (예정)

day10 마지막에서 `/api4`에 `@CrossOrigin`을 얹어 리액트 화면이 서버 응답을 읽을 수 있게 열었습니다. 이번에는 그 방향을 **내 DB 데이터**로 되돌립니다. 게시판 표(`board`) 하나를 엔티티 → 리포지토리 → 서비스 → 컨트롤러 네 층으로 다시 세우고, 목록 전체를 `/api` 한 주소로 내줍니다. 받는 쪽은 같은 날 React 수업에서 만든 게시판 목록 화면(React day08 노트, 허브 경유)입니다. 새 문법은 거의 없고, **화면이 요구하는 JSON 모양에 맞춰 백엔드 한 벌을 빠르게 세우는 연습**이 핵심입니다. 오후에는 같은 주소에 `POST`를 하나 더 얹어, 화면의 글쓰기 폼이 보낸 JSON을 받아 저장하는 쪽까지 이어 갑니다(1-5·1-6).

## 1. 배운 내용

### 1-1. 새 DB와 초기 데이터 — `sampledb.sql` · `sample.sql` · `application.properties`

```sql
-- sampledb.sql : DB 자체는 손으로 만든다
DROP DATABASE IF EXISTS mydb0923;
CREATE DATABASE mydb0923;
use mydb0923;
```

```properties
spring.datasource.url = jdbc:mysql://localhost:3306/mydb0923
spring.datasource.password=****            # 실습용 로컬 값 (노트에서는 가림)
spring.jpa.hibernate.ddl-auto=create-drop
spring.sql.init.data-locations=classpath:/sql/sample.sql
spring.jpa.defer-datasource-initialization=true
```

| 단계 | 누가 하나 | 결과 |
| --- | --- | --- |
| DB 생성 | 내가 `sampledb.sql` 실행 | 빈 `mydb0923` |
| 표 생성 | JPA `ddl-auto` (엔티티 기준) | `board` 표 |
| 데이터 적재 | `spring.sql.init` (`sample.sql`) | 게시글 10건 |

- `ddl-auto`는 **표**까지만 만든다. DB(스키마) 자체는 없으면 접속이 실패하므로 먼저 만들어 둔다.
- `defer-datasource-initialization=true`가 있어야 "엔티티로 표 생성 → 그다음 INSERT" 순서가 보장된다. 순서가 뒤집히면 없는 표에 넣으려다 실패한다.
- day10은 엔티티가 없어 `spring.sql.init.mode=never`로 꺼 두었다. 엔티티가 있는 패키지를 실행할 때는 `always`로 바꿔야 `sample.sql`이 실제로 돈다 — 설정 파일 하나를 여러 day가 같이 쓰기 때문에 생기는 스위치다.
- `create-drop`이라 서버를 끌 때 표가 지워지고, 켤 때마다 10건이 새로 들어간다. 실습 중에는 항상 같은 상태에서 시작하는 셈이다.

### 1-2. 표 이름과 클래스 이름 분리 — `@Table(name = "board")`

```java
@Entity
@Table(name = "board")
@Data @AllArgsConstructor @NoArgsConstructor @Builder
public class ApiEntity {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private int idx;
    private String subject;
    private String name;
    private String regdate;
    private String content;
}
```

- 클래스는 `ApiEntity`지만 DB 표는 `board`다. `@Table`이 없으면 클래스 이름을 따라 `api_entity` 표가 생겨 `sample.sql`의 `INSERT INTO board`가 갈 곳이 없어진다.
- 필드 이름 = 컬럼 이름 = JSON 키가 한 줄로 이어진다: `subject`·`name`·`regdate`·`content`. 화면 쪽 `row.subject`, `row.regdate`가 여기서 온다.
- `regdate`를 날짜 타입이 아닌 `String`으로 받았다. 화면에서 `substring(0, 10)`으로 앞 10글자(`2026-09-01`)만 자르는 방식과 짝이 맞는다.

### 1-3. 네 층 한 벌 — 리포지토리 · 서비스 · 컨트롤러

```java
// 리포지토리 — 몸통 없이 CRUD 상속
public interface ApiRepository extends JpaRepository<ApiEntity, Integer> { }

// 서비스 — 엔티티 목록을 DTO 목록으로 펴기
public List<ApiDto> findAll() {
    List<ApiEntity> entities = apiRepository.findAll();
    return entities.stream().map((entity) -> ApiDto.from(entity)).toList();
}

// 컨트롤러 — 주소 하나, 다른 포트 허용
@GetMapping("/api")
@CrossOrigin("http://localhost:5173")
public List<ApiDto> findAll() { return apiService.findAll(); }
```

| 층 | 하는 일 | 앞에서 본 자리 |
| --- | --- | --- |
| Repository | `findAll()` 물려받기 | [[Spring day04 JPA 엔티티와 리포지토리]] |
| Service | `stream().map(DTO::from).toList()` | [[Spring day08 컬렉션 순회와 스트림 API]] |
| DTO | `from(entity)` 정적 팩토리 + `@Builder` | [[Spring day05 DTO 변환과 초기 데이터 적재]] |
| Controller | `@GetMapping` + `@CrossOrigin` | [[Spring day10 WebClient로 공공데이터 API 대신 호출하기]] |

- 서비스의 람다 `(entity) -> { return ApiDto.from(entity); }`는 `ApiDto::from`으로 줄일 수 있는 모양이다 → [[Spring day08 메소드 레퍼런스로 줄인 람다]].
- `@CrossOrigin("http://localhost:5173")` — 화면(Vite 개발 서버, 5173)과 API(톰캣, 8080)의 포트가 다르면 브라우저는 다른 출처로 보고 응답을 막는다. 컨트롤러 메소드 위에 허용할 출처를 적어 그 한 주소만 연다.

### 1-4. DTO 변환에서 빠지기 쉬운 칸

```java
public static ApiDto from(ApiEntity e) {
    return ApiDto.builder()
            .subject(e.getSubject())
            .name(e.getName())
            .regdate(e.getRegdate())
            .content(e.getContent())
            .build();
}
```

- 빌더는 **적은 칸만 채우고 나머지는 기본값(`null`)** 으로 둔다. 컴파일 오류가 나지 않기 때문에 한 칸이 빠져도 알아채기 어렵다.
- 화면이 번호를 `key`나 상세 주소(`/view/` + 번호)로 쓴다면 PK(`idx`)도 DTO로 옮겨야 한다. 응답 JSON을 브라우저나 포스트맨으로 한 번 열어 **화면이 쓰는 키가 모두 값을 갖는지** 확인하는 편이 안전하다.

### 1-5. 같은 주소에 쓰기 하나 더 — `POST /api` + `@RequestBody`

```java
// ApiController
@PostMapping("/api")
public boolean postMethodName(@RequestBody ApiDto apiDto) {
    return apiService.save(apiDto);
}

// ApiService
public boolean save(ApiDto apiDto) {
    ApiEntity apiEntity = apiDto.toEntity();
    ApiEntity saved = apiRepository.save(apiEntity);
    if (saved.getIdx() >= 1) return true;
    return false;
}
```

| 요청 | 주소 | 들어오는 것 | 나가는 것 |
| --- | --- | --- | --- |
| 목록 | `GET /api` | 없음 | `List<ApiDto>` (JSON 배열) |
| 쓰기 | `POST /api` | 본문 JSON → `ApiDto` | `true` / `false` |

- **주소는 같고 HTTP 메소드만 다르다.** 스프링은 주소 + 메소드 짝으로 매핑을 가르므로 `/api` 하나로 "읽기"와 "쓰기"를 나눌 수 있다 → [[Spring day04 REST 컨트롤러 CRUD 골격]].
- `@RequestBody`는 요청 본문 JSON을 키 이름 기준으로 DTO 필드에 채운다. 화면이 `{ name, subject, content }`만 보내면 `idx`·`regdate`는 비어 있는 채로 들어온다 — 둘 다 서버(DB)가 정할 값이라 그게 맞다.
- 저장이 성공했는지는 **돌려받은 엔티티의 PK**로 판단한다. `save()`가 돌려준 객체에는 IDENTITY 전략으로 DB가 매긴 번호가 채워져 있으므로 `1` 이상이면 들어간 것이다. 화면은 이 `true`만 보고 목록으로 넘어간다.

### 1-6. 반대 방향 변환 `toEntity()` · CORS를 클래스 위로

```java
public ApiEntity toEntity() {
    return ApiEntity.builder()
            .name(name)
            .content(content)
            .subject(subject)
            .build();
}
```

- `from(entity)`가 **엔티티 → DTO**(나가는 길)라면 `toEntity()`는 **DTO → 엔티티**(들어오는 길)다. 정적 메소드와 인스턴스 메소드로 방향을 나눠 두면 서비스 코드가 `ApiDto.from(e)` / `dto.toEntity()` 두 모양으로 읽힌다 → [[Spring day05 DTO 변환과 초기 데이터 적재]].
- 여기서는 `idx`를 일부러 넣지 않는다. PK가 비어 있어야 JPA가 새 행으로 보고 `INSERT`를 한다(값이 있으면 기존 행 수정으로 본다).
- `@CrossOrigin("http://localhost:5173")`을 메소드 위에서 **클래스 위로** 옮겼다. 클래스에 붙이면 그 컨트롤러의 모든 매핑(`GET`·`POST`)에 같은 허용이 걸린다. 메소드가 두 개로 늘어난 시점에 자연스러운 이동이다.
- `POST`에 JSON 본문을 실으면 브라우저가 본 요청 전에 `OPTIONS` 사전 요청(preflight)을 먼저 보낸다. `@CrossOrigin`이 이 사전 요청까지 같이 받아 주기 때문에 따로 처리할 것은 없다.

## 2. 추가로 알면 좋은 활용법

### 2-1. CORS를 한 곳에서 — `WebMvcConfigurer`

컨트롤러가 늘어나면 메소드마다 `@CrossOrigin`을 붙이는 대신 설정 클래스 하나로 모은다.

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

- `GET`만 쓰던 지금과 달리 글쓰기·수정·삭제가 붙으면 `POST`·`PUT`·`DELETE`와 사전 요청(`OPTIONS`)까지 허용 범위에 들어가야 한다.

### 2-2. 목록 응답은 정렬부터

- `findAll()`은 순서를 보장하지 않는다. 게시판 목록이라면 `findAll(Sort.by(Sort.Direction.DESC, "idx"))`나 쿼리 메소드 `findAllByOrderByIdxDesc()`로 최신 글이 위에 오게 한다 → [[Spring day08 쿼리 메소드와 네이티브 쿼리]].
- 목록에는 `content` 같은 긴 본문이 필요 없다. 목록용 DTO와 상세용 DTO를 나누면 응답 크기가 줄어든다.

### 2-3. 날짜를 날짜 타입으로

- `regdate`를 `LocalDateTime`으로 받고 `@CreatedDate`(감사 필드)로 자동 기록하면 문자열 자르기 없이 서버에서 형식을 정할 수 있다 → [[Spring day05 엔티티 제약과 감사 필드]].
- 응답 형식은 `@JsonFormat(pattern = "yyyy-MM-dd")`로 DTO 필드에 붙인다.

## 3. 더 나아가 알면 좋은 것

### 3-1. 목록 다음 단계 — 상세·쓰기 API

화면에 이미 `/view/번호`, `/write` 링크가 걸려 있으니 백엔드도 같은 흐름으로 늘어난다.

| 화면 동작 | API | 서비스 |
| --- | --- | --- |
| 상세 보기 | `GET /api/{idx}` + `@PathVariable` | `findById(idx).orElseThrow()` |
| 글쓰기 (1-5에서 완성) | `POST /api` + `@RequestBody ApiDto` | `save(dto.toEntity())` |
| 수정 | `PUT /api/{idx}` | 조회 후 setter → 변경 감지 |
| 삭제 | `DELETE /api/{idx}` | `deleteById(idx)` |

- 수정 흐름은 [[Spring day05 등록·수정 흐름과 변경 감지]]에서 본 모양 그대로다.
- 쓰기 응답을 `boolean` 대신 `ResponseEntity.status(201).body(saved.getIdx())`처럼 **상태 코드 + 새 번호**로 돌려주면, 화면이 저장 직후 상세 화면(`/view/새번호`)으로 바로 넘어갈 수 있다.
- `@Valid` + `@NotBlank`를 DTO에 붙이면 빈 제목·빈 작성자를 서버에서 한 번 더 걸러 낼 수 있다(화면 검사만으로는 우회가 가능하다).

### 3-2. 다음에 볼 키워드

- `Pageable` · `Page<T>` — 목록 페이징(`?page=0&size=10`)
- `ResponseEntity<T>` — 상태 코드(200·404)를 함께 내보내기
- `@RestControllerAdvice` — 없는 번호 조회 같은 예외를 한 곳에서 응답으로 바꾸기
- 개발 서버 프록시(Vite `server.proxy`) — CORS 없이 같은 출처처럼 부르는 방법
- 설정 분리(`application-local.properties`, 환경 변수) — 비밀번호·키를 저장소 밖으로 빼기

## 실습 파일

- `KDT_2026/2026B_Spring/springweb/src/main/java/day11/AppStart.java` — day11 전용 실행 진입점, 이 패키지 기준으로 컴포넌트 스캔
- `KDT_2026/2026B_Spring/springweb/src/main/java/day11/model/entity/ApiEntity.java` — `@Table(name = "board")` 게시글 엔티티, IDENTITY PK와 문자열 필드 넷
- `KDT_2026/2026B_Spring/springweb/src/main/java/day11/model/repository/ApiRepository.java` — `JpaRepository<ApiEntity, Integer>` 상속만 있는 빈 인터페이스
- `KDT_2026/2026B_Spring/springweb/src/main/java/`day11/model/dto/ApiDto.java` — 빌더로 엔티티를 펴는 `from()` 정적 메소드와 반대 방향 `toEntity()`
- `KDT_2026/2026B_Spring/springweb/src/main/java/`day11/service/ApiService.java` — 스트림 `map`으로 엔티티 목록 → DTO 목록, `save()`로 저장 후 PK로 성공 판정
- `KDT_2026/2026B_Spring/springweb/src/main/java/`day11/controller/ApiController.java` — 클래스 단위 `@CrossOrigin("http://localhost:5173")`, `GET /api` 목록 + `POST /api` 쓰기
- `KDT_2026/2026B_Spring/springweb/src/main/resources/sql/sampledb.sql` — `mydb0923` DB 생성
- `KDT_2026/2026B_Spring/springweb/src/main/resources/sql/sample.sql` — `board` 게시글 10건 INSERT
- `KDT_2026/2026B_Spring/springweb/src/main/resources/application.properties` — 접속 DB를 `mydb0923`으로, 초기 SQL 경로를 `sample.sql`로 바꾼 설정

## 관련 노트

[[Spring MOC]] · [[Spring day10 WebClient로 공공데이터 API 대신 호출하기]] · [[Spring day05 DTO 변환과 초기 데이터 적재]] · [[Spring day08 컬렉션 순회와 스트림 API]] · [[KDT_2026 학습 지도]]

<!--
[문체 규칙]
- 내가 공부하며 정리한 노트다. 남의 코드를 평가하는 말투를 쓰지 않는다.
- 2인칭(하신, 쓰셨, 적으신)을 쓰지 않는다.
- 원본 코드의 오류·오타는 기록하지 않는다. 필요하면 파일 지목 없이 일반 주의사항으로 쓴다.
- 한 사람이 쭉 이어서 쓴 것처럼 문체를 일정하게 유지한다.
-->
