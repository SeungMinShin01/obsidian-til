---
출처: Claude 분석
원본: KDT_2026/2026B_Spring/demo/build.gradle, demo/settings.gradle, demo/src/main/java/com/example/demo/AppStart.java, demo/src/main/java/com/example/demo/model/entity, demo/src/main/java/com/example/demo/model/dto, demo/src/main/resources/application.properties, demo/src/main/resources/sql/practice5.sql
작성일: 2026-09-08
tags: [학습, java]
---

# Spring day08 — 새 프로젝트로 옮겨 담는 도메인 층

> 실습 파일: `demo/build.gradle`, `demo/settings.gradle`, `demo/src/main/java/com/example/demo/AppStart.java`, `model/entity/BaseTime.java`, `model/entity/BoardEntity.java`, `model/entity/CommentEntity.java`, `model/dto/BoardDto.java`
> 허브: [[Spring MOC]] · 이전: [[Spring day08 댓글 쪽으로 한 번 더 관통시키기]]

앞의 두 노트는 같은 프로젝트(`springweb`) 안에 패키지를 하나 더 파서 게시판을 다시 짜는 실습이었습니다. 이번에는 한 걸음 더 나가서 **프로젝트 자체를 새로 만들고**(`demo`) 그 위에 같은 도메인을 옮겨 담았습니다.

패키지만 갈리던 때와 달리, 프로젝트가 갈리면 따라오는 것이 늘어납니다 — 빌드 스크립트, 프로젝트 이름, 설정 파일, 기본 패키지, 그리고 그 안에서 다시 그어야 하는 계층 폴더입니다. 도메인 코드는 익숙한데 **그 바깥을 감싸는 껍데기가 무엇 무엇으로 이루어져 있었는지**가 이번에 드러나는 자리입니다.

## 1. 배운 내용

### 1-1. 프로젝트 하나가 서기 위해 필요한 파일들

새로 받은 프로젝트에는 도메인 코드가 아직 하나도 없는데도 파일이 여럿 들어 있습니다. 각각이 무슨 몫인지 정리하면 이렇습니다.

| 파일 | 몫 |
| --- | --- |
| `settings.gradle` | 프로젝트 이름 하나(`rootProject.name`)를 정한다 |
| `build.gradle` | 플러그인·자바 버전·의존성·진입점을 적는다 |
| `gradlew`·`gradlew.bat`·`gradle/wrapper/` | 그레이들 자체를 내려받아 고정된 버전으로 돌리는 래퍼 |
| `src/main/java` | 실제 코드 |
| `src/main/resources` | 설정·시드 SQL·정적 파일 |
| `.gitignore`·`.gitattributes` | 형상관리 쪽 설정 |

핵심은 **래퍼**입니다. 그레이들이 컴퓨터에 깔려 있지 않아도 `gradlew` 한 줄이면 명시된 버전을 받아 와 빌드가 돕니다. 프로젝트를 옮겨 다녀도 빌드 환경이 같아지는 것이 이 네 파일의 값어치입니다.

`settings.gradle` 의 `rootProject.name` 은 새 프로젝트를 만들 때 정한 이름이 그대로 남는 자리라, 폴더 이름과 프로젝트 이름이 갈릴 수 있습니다. 옮겨 담을 때는 이 값과 `build.gradle` 의 `group`, `application.properties` 의 `spring.application.name` 이 각각 무엇을 가리키는지 한 번 훑어 두는 편이 나중에 헷갈리지 않습니다.

### 1-2. 의존성 네 묶음을 다시 세우기

`build.gradle` 의 `dependencies` 블록에 이번 실습에 필요한 것만 남기면 네 묶음입니다.

```gradle
dependencies {
	implementation 'org.springframework.boot:spring-boot-starter-webmvc'
	runtimeOnly 'com.mysql:mysql-connector-j'

	// 롬복
	compileOnly 'org.projectlombok:lombok'
	annotationProcessor 'org.projectlombok:lombok'

	// JPA
	implementation 'org.springframework.boot:spring-boot-starter-data-jpa'
}
```

| 앞말 | 언제 필요한가 | 예 |
| --- | --- | --- |
| `implementation` | 컴파일할 때도, 돌 때도 | 웹 스타터·JPA 스타터 |
| `runtimeOnly` | 돌 때만 (코드에서 이름을 부르지 않는다) | MySQL 드라이버 |
| `compileOnly` | 컴파일할 때만 (결과물에 안 남는다) | 롬복 |
| `annotationProcessor` | 컴파일 도중 코드를 만들어 내는 자리 | 롬복 |

롬복이 `compileOnly` 와 `annotationProcessor` **두 줄로 짝**인 것이 다시 확인되는 자리입니다. 표시를 읽어 `getter` 를 만들어 주는 것은 애노테이션 프로세서이고, 그 표시 자체를 컴파일하려면 클래스가 있어야 하는데, 코드가 만들어지고 나면 배포본에는 롬복이 남아 있을 이유가 없기 때문입니다.

`spring-boot-starter-data-jpa` 한 줄이 데려오는 것도 그대로입니다 — JPA 규격, 구현체(하이버네이트), 스프링 데이터, 커넥션 풀. 맨 아래층은 여전히 JDBC입니다.

### 1-3. 계층 폴더를 기본 패키지 아래에 다시 긋기

새 프로젝트의 기본 패키지가 `com.example.demo` 로 잡혀 있어서, 계층 폴더는 그 아래에 다시 그었습니다.

```
com/example/demo/
├── AppStart.java
├── controller/
├── service/
└── model/
    ├── dto/
    ├── entity/
    └── repository/
```

`day07/practice` 아래에 그었던 것과 모양이 같습니다. **폴더가 갈리면 `package` 선언과 `import` 가 따라 바뀌므로**, 옮겨 담을 때 손이 가는 것은 도메인 로직이 아니라 파일 머리의 두 줄입니다.

여기서 한 가지가 갈립니다. 앞서는 한 프로젝트에 진입점이 여럿이라 `build.gradle` 의 `mainClass` 로 어느 것을 띄울지 골라 줘야 했는데, 새 프로젝트는 진입점이 하나뿐이라 그 고민이 없습니다. 다만 빌드 스크립트를 옮겨 오면 그 줄도 함께 따라오므로, **진입점 지정 줄이 지금 프로젝트의 어느 클래스를 가리키고 있는지**는 옮긴 직후에 한 번 보는 편이 안전합니다.

### 1-4. 감사 필드를 다시 세우는 세 자리

`BaseTime` 은 앞과 같은 모양으로 다시 세웠습니다.

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

감사가 실제로 도는 데 필요한 세 자리를 다시 정리하면 이렇습니다.

1. 필드에 `@CreatedDate`·`@LastModifiedDate`
2. 클래스에 `@EntityListeners(AuditingEntityListener.class)`
3. 진입점에 `@EnableJpaAuditing`

```java
@SpringBootApplication
@EnableJpaAuditing
public class AppStart {
    public static void main(String[] args) {
        SpringApplication.run(AppStart.class);
    }
}
```

셋 중 하나만 빠져도 **오류가 나지 않고 값만 `null` 로 남습니다.** 새 프로젝트로 옮길 때 세 자리가 서로 다른 파일에 흩어져 있다는 점이 특히 걸리기 쉬운 자리입니다. `@Setter` 를 두지 않는 것도 그대로입니다 — 이 두 값은 밖에서 넣는 값이 아니라 채워지는 값입니다.

`@MappedSuperclass` 는 자기 표를 갖지 않는 필드 묶음이라는 표시라, `extends BaseTime` 을 건 엔티티의 표에만 두 컬럼이 붙습니다.

### 1-5. 관계를 가진 엔티티 두 벌

게시글이 "일", 댓글이 "다" 쪽입니다.

```java
@Entity
@Table(name = "board")
@NoArgsConstructor @AllArgsConstructor @Data @Builder
public class BoardEntity extends BaseTime {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Integer id;

    private String author;
    private String password;
    private String content;

    @OneToMany(mappedBy = "boardEntity", cascade = CascadeType.ALL, fetch = FetchType.LAZY)
    @ToString.Exclude
    @Builder.Default
    private List<CommentEntity> commententities = new ArrayList<>();
}
```

"일" 쪽에 붙는 세 표시가 각각 무엇을 막는지는 여러 번 나온 그대로입니다.

| 표시 | 막는 것 |
| --- | --- |
| `mappedBy = "boardEntity"` | 중간 표가 따로 생기는 것 |
| `@ToString.Exclude` | `toString()` 이 양쪽을 왕복하다 스택이 넘치는 것 |
| `@Builder.Default` | 빌더로 만들 때 목록이 `null` 이 되는 것 |

`mappedBy` 에 적는 값이 표 이름이 아니라 **상대 엔티티의 자바 필드 이름**이라, 자식 쪽 필드 이름을 먼저 정해 두고 그 이름을 그대로 적게 됩니다. 이름이 어긋나면 요청 때가 아니라 서버가 뜰 때 걸립니다.

"다" 쪽은 외래키를 든 쪽입니다.

```java
@Entity
@Table(name = "comment")
@NoArgsConstructor @AllArgsConstructor @Data @Builder
public class CommentEntity {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Integer id;

    private String author;
    private String password;
    private String content;

    @JoinColumn(name = "board_id")
    @ManyToOne
    private BoardEntity boardEntity;
}
```

방향은 필드 타입이, 개수는 `@ManyToOne` 이, 외래키 컬럼 이름은 `@JoinColumn` 이 정합니다. `@JoinColumn` 을 빼면 `필드이름_상대PK` 규칙으로 이름이 만들어지므로, 시드 SQL이 쓰는 컬럼 이름(`board_id`)과 맞추려면 적어 두는 편이 확실합니다.

`@ManyToOne` 은 기본 페치가 즉시 로딩이라 `@OneToMany` 와 반대라는 점도 그대로입니다. `@OneToMany` 쪽의 `fetch = LAZY` 는 원래 기본값이라 뜻을 적어 두는 표기지만, `@ManyToOne` 쪽은 적어야 실제로 바뀝니다.

### 1-6. 목록을 품은 DTO와 변환 메소드 두 개

`BoardDto` 는 댓글 DTO 목록을 필드로 듭니다.

```java
public class BoardDto {
    private Integer id;
    private String author;
    private String password;
    private String content;
    private LocalDateTime createdAt;
    private LocalDateTime updatedAt;

    @Builder.Default
    private List<CommetDto> comments = new ArrayList<>();

    public BoardEntity toEntity() {
        return BoardEntity.builder()
                .author(this.author)
                .password(this.password)
                .content(this.content)
                .build();
    }

    public static BoardDto from(BoardEntity entity) {
        return BoardDto.builder()
                .id(entity.getId())
                .author(entity.getAuthor())
                .password(entity.getPassword())
                .content(entity.getContent())
                .createdAt(entity.getCreatedAt())
                .updatedAt(entity.getUpdatedAt())
                .build();
    }
}
```

두 메소드가 담는 것과 담지 않는 것을 표로 두면 경계가 눈에 남습니다.

| 필드 | `toEntity()` | `from()` |
| --- | --- | --- |
| `id` (PK) | 안 담음 (DB가 채운다) | 담음 |
| 값 필드 셋 | 담음 | 담음 |
| 감사 필드 둘 | 안 담음 (리스너가 채운다) | 담음 |
| 댓글 목록 | 안 담음 | 비워 둠 (서비스가 채운다) |

`toEntity()` 가 인스턴스 메소드이고 `from()` 이 `static` 인 이유는 부르는 시점에 그 타입의 객체가 손에 있느냐의 차이입니다. DTO를 엔티티로 바꿀 때는 DTO가 이미 손에 있으니 `this` 를 쓰면 되고, 엔티티를 DTO로 바꿀 때는 만들려는 DTO가 아직 없으니 재료를 인자로 받습니다.

`from()` 이 댓글 목록을 비워 두는 것도 앞과 같은 경계선입니다 — **엔티티 하나와 한 칸 이웃까지 보면 나오는 값은 DTO가, 여러 엔티티를 모아야 하는 값은 서비스가** 채웁니다.

### 1-7. 설정과 시드를 함께 옮기기

`application.properties` 에서 이번 실습이 실제로 쓰는 줄은 이렇게 갈립니다.

| 묶음 | 줄 |
| --- | --- |
| 포트 | `server.port` |
| DB 연결 | `spring.datasource.url`·`username`·`password` |
| 표 만들기 | `spring.jpa.hibernate.ddl-auto=create-drop` |
| SQL 보기 | `show-sql`·`format_sql` |
| 시드 넣기 | `sql.init.data-locations`·`defer-datasource-initialization`·`sql.init.mode`·`sql.init.encoding` |

시드 쪽 네 줄이 함께 다니는 이유를 다시 정리하면 이렇습니다.

- `data-locations` — 어느 파일을 읽을지 (`classpath:` 는 `src/main/resources`)
- `defer-datasource-initialization=true` — 시드를 **표 생성 뒤로** 미룬다 (기본은 그 반대라 표가 없어 실패한다)
- `sql.init.mode=always` — 기본값 `embedded` 는 내장 DB에서만 도므로 MySQL에서는 켜 줘야 한다
- `sql.init.encoding=UTF-8` — 한글 시드가 깨지지 않게 읽을 인코딩을 정한다

시드 SQL이 감사 컬럼에 `NOW()` 를 직접 적는 것도 같은 사정입니다. SQL로 바로 나가는 `INSERT` 는 JPA를 거치지 않으니 엔티티 리스너가 돌지 않고, 그래서 시각을 손으로 넣어 줍니다. 컬럼 이름(`created_at`·`board_id`)은 자바 필드 이름이 카멜↔스네이크 변환과 `@JoinColumn` 을 거쳐 만들어진 결과와 맞아야 합니다.

부모 `INSERT` 를 자식보다 먼저 두는 순서도 그대로입니다. 외래키가 가리킬 줄이 먼저 있어야 하기 때문입니다.

## 2. 추가로 알면 좋은 활용법

### 2-1. 옮겨 담을 때 손대는 것과 그대로 두는 것

같은 도메인을 새 프로젝트로 옮길 때 실제로 갈리는 곳을 세어 보면 층마다 다릅니다.

| 층 | 갈리는 것 |
| --- | --- |
| 빌드·설정 | 프로젝트 이름·진입점 지정·DB 주소·시드 경로 |
| 진입점 | 패키지 선언, 클래스 이름 |
| 엔티티·DTO | `package` 와 `import` 두 줄 (본문은 거의 그대로) |
| 리포지토리 | 제네릭 두 자리와 인터페이스 이름 |

**아래층일수록 갈림이 줄고 위층·바깥층일수록 늡니다.** 도메인 코드는 프로젝트가 바뀌어도 거의 그대로인데, 프로젝트를 감싸는 껍데기는 매번 새로 정해 줘야 하는 값들입니다.

### 2-2. 새 프로젝트를 만드는 두 갈래

| 갈래 | 성질 |
| --- | --- |
| Initializr(생성 마법사) | 의존성을 고르면 `build.gradle` 이 채워져 나온다. 버전 짝이 맞는 상태에서 시작 |
| 기존 프로젝트 복사 | 익숙한 설정이 그대로 오지만 앞 프로젝트의 값들도 함께 따라온다 |

복사로 시작하면 **앞 프로젝트를 가리키는 값들**(프로젝트 이름·진입점·DB 주소)이 남아 있게 되므로, 시작하자마자 한 번 훑어 두는 편이 좋습니다. 생성 마법사로 만들면 그 대신 의존성을 다시 고르는 수고가 듭니다.

### 2-3. `ddl-auto` 다섯 값과 지금 고른 것

| 값 | 하는 일 |
| --- | --- |
| `create` | 뜰 때 표를 지우고 다시 만든다 |
| `create-drop` | 거기에 더해 내려갈 때도 지운다 |
| `update` | 있으면 고치고 없으면 만든다 (지우지는 않는다) |
| `validate` | 엔티티와 표가 어긋나면 시작할 때 막는다 |
| `none` | 아무것도 하지 않는다 |

실습에서 `create-drop` 을 쓰는 이유는 엔티티를 고쳐 가며 표 모양을 확인하기 위해서입니다. 매번 표가 새로 만들어지니 시드도 매번 다시 들어갑니다. 반대로 값을 남겨 둬야 하는 자리에서는 `validate` 나 `none` 이 맞습니다.

### 2-4. 계층 폴더를 미리 다 만들어 두기

빈 폴더 다섯을 먼저 만들고 아래층부터 채워 올리면, 파일을 만들 때마다 어디에 둘지 다시 고민하지 않게 됩니다. 순서가 아래층부터인 이유는 **위층이 아래층의 이름을 부르기 때문**입니다 — 서비스를 먼저 쓰면 리포지토리 이름이 아직 없어 컴파일이 지나가지 않습니다.

반대로 위층 이름을 먼저 정해 두면 아래층에 무엇을 만들지가 이름과 매개변수로 정해지는 이점도 있습니다. 두 순서를 섞으면 층을 다 채우기 전까지 빌드가 안 지나가는 구간이 길어지므로, 한 갈래씩 세로로 관통시키는 편이 그 구간을 짧게 둡니다.

### 2-5. 껍데기만 먼저 두는 진행

리포지토리·서비스·컨트롤러 파일을 이름만 만들어 두고 도메인 층부터 채우는 순서는, 전체 그림을 먼저 눈에 넣고 세부를 채우는 방식입니다. 표가 어떻게 생겼는지가 정해져야 그 위 층에서 무엇을 주고받을지가 정해지기 때문에, 엔티티 → DTO → 리포지토리 → 서비스 → 컨트롤러 순서에는 이유가 있습니다.

다만 껍데기 상태로 오래 두면 어디까지 채웠는지가 흐려지므로, 한 갈래(예: 등록)를 골라 컨트롤러까지 한 번 관통시켜 두면 남은 갈래는 그 모양을 따라가면 됩니다.

## 3. 더 나아가 알면 좋은 것

### 3-1. 프로젝트를 나누는 기준

지금은 실습 묶음마다 패키지를 나누거나 프로젝트를 새로 만들고 있는데, 실제로는 다음이 기준이 됩니다.

| 나누는 단위 | 언제 |
| --- | --- |
| 패키지 | 같은 앱 안에서 관심사가 갈릴 때 |
| 그레이들 모듈 | 빌드 단위·의존 방향을 강제하고 싶을 때 |
| 프로젝트(리포지토리) | 배포 주기·소유가 갈릴 때 |

패키지로 나누면 잘못된 방향의 `import` 를 막을 방법이 없지만, 모듈로 나누면 의존 방향이 빌드에서 강제됩니다. 지금 규모에서는 패키지로 충분하고, 프로젝트를 새로 만드는 것은 "처음부터 다시 해 보기"라는 학습 목적이 이유가 됩니다.

### 3-2. 프로파일로 설정을 갈라 두기

실습마다 DB 주소와 시드 경로를 손으로 고치는 대신, 프로파일을 나누면 파일을 갈아 끼우는 모양이 됩니다.

- `application-local.properties`·`application-prod.properties` 로 나누고 `spring.profiles.active` 로 고른다
- 비밀번호 같은 값은 파일에 남기지 않고 환경변수·실행 옵션으로 넘긴다 (`${DB_PASSWORD}` 치환)

로컬 실습용 비밀번호라도 파일에 그대로 두는 습관이 붙으면 그대로 공개 저장소에 올라가는 자리가 생기므로, 갈라 두는 방법을 알아 두는 편이 낫습니다.

### 3-3. 옮겨 담기가 제대로 됐는지 확인하는 순서

새 프로젝트에서 처음 서버를 띄울 때 막히면, 대개 다음 순서로 좁혀집니다.

1. 빌드가 지나가는가 — 의존성·자바 버전
2. 컨텍스트가 뜨는가 — 진입점 위치와 컴포넌트 스캔 범위
3. 표가 만들어지는가 — DB 연결·`ddl-auto`·생성된 `create table` 문
4. 시드가 들어가는가 — `sql.init` 네 줄과 컬럼 이름
5. 값이 채워지는가 — 감사 세 자리

**앞 단계가 안 되면 뒤 단계는 볼 수 없으므로** 순서대로 좁히는 편이 빠릅니다. 특히 3번과 4번은 콘솔에 나오는 SQL로 직접 확인할 수 있어서, `show-sql` 을 켜 두는 값어치가 여기서 나옵니다.

### 3-4. 다음에 볼 키워드

- 그레이들 멀티 모듈과 의존 방향 강제
- `spring.profiles.active` 와 설정 분리·`@ConfigurationProperties`
- Flyway·Liquibase — `ddl-auto` 대신 스키마 변경을 이력으로 관리하기
- `@DataJpaTest`·`@WebMvcTest` 로 층별로 떼어 검사하기
- 프로젝트 템플릿·아키타입으로 껍데기 자체를 규약으로 만들기

## 실습 파일

- `2026B_Spring/demo/settings.gradle`, `demo/build.gradle` (**프로젝트 한 벌이 서는 자리** — 프로젝트 이름이 폴더 이름과 따로 정해지는 점과 그레이들 래퍼 네 파일이 빌드 환경을 고정하는 값어치, 의존성 앞말 넷(`implementation`·`runtimeOnly`·`compileOnly`·`annotationProcessor`)이 각각 필요한 구간을 정하는 규칙과 롬복이 두 줄로 짝인 이유·JDBC 드라이버가 `runtimeOnly` 인 반대 사정, 진입점 지정 줄이 빌드 스크립트를 옮길 때 함께 따라오므로 지금 프로젝트를 가리키는지 확인하는 자리)
- `2026B_Spring/demo/src/main/java/com/example/demo/AppStart.java` (**진입점과 감사 활성화** — `@SpringBootApplication` 의 컴포넌트 스캔 범위가 이 클래스의 패키지 아래라는 점과 기본 패키지 바로 밑에 두는 배치, `@EnableJpaAuditing` 이 감사가 도는 세 자리 중 하나이고 나머지 둘과 다른 파일에 흩어져 있어 빠지면 조용히 `null` 로 남는 자리)
- `2026B_Spring/demo/src/main/java/com/example/demo/model/entity/BaseTime.java` (**표를 갖지 않는 공통 필드 묶음을 다시 세우는 자리** — `@MappedSuperclass` 로 필드만 물려주고 `@EntityListeners` 로 값을 채워 줄 구현체를 붙이는 두 표시의 몫, `@CreatedDate`(처음 한 번)와 `@LastModifiedDate`(저장·수정마다)의 갈림과 `@Setter` 를 두지 않는 이유가 밖에서 넣는 값이 아니라 채워지는 값이라는 점)
- `2026B_Spring/demo/src/main/java/com/example/demo/model/entity/BoardEntity.java` (**"일" 쪽 세 표시를 손으로 다시 적는 자리** — `mappedBy` 가 상대 엔티티의 자바 필드 이름이라 자식 쪽 이름을 먼저 정하게 되고 어긋나면 서버가 뜰 때 걸리는 점, `@ToString.Exclude` 가 왕복을 한 곳에서 끊고 `@Builder.Default` 가 빌더에서 목록이 `null` 이 되는 것을 막는 배치, `cascade = ALL` 을 "부모 없이는 존재할 이유가 없는 자식"이라는 기준에 비추는 판단과 `fetch = LAZY` 가 `@OneToMany` 에서는 원래 기본값이라 뜻을 적어 두는 표기인 점)
- `2026B_Spring/demo/src/main/java/com/example/demo/model/entity/CommentEntity.java` (**외래키를 든 "다" 쪽** — 방향은 필드 타입이·개수는 `@ManyToOne` 이·컬럼 이름은 `@JoinColumn` 이 정하는 갈림과 생략 시 `필드이름_상대PK` 규칙이 시드 SQL의 컬럼 이름과 맞아야 하는 자리, `@ManyToOne` 의 기본 페치가 즉시 로딩이라 `@OneToMany` 와 반대로 적어야 바뀌는 점)
- `2026B_Spring/demo/src/main/java/com/example/demo/model/dto/BoardDto.java` (**목록을 품은 DTO와 변환 메소드 두 개** — `toEntity()` 가 PK·감사 필드·관계를 안 담아 밖에서 온 값이 들어갈 통로를 좁히고 `from()` 이 댓글 목록을 비워 둬 "한 칸 이웃까지는 DTO·여러 엔티티를 모으면 서비스"라는 경계선이 다시 그어지는 자리, 인스턴스 메소드와 `static` 이 갈리는 근거가 부르는 시점에 그 타입의 객체가 손에 있느냐라는 점, 컬렉션 필드를 빈 값으로 초기화하고 `@Builder.Default` 를 짝으로 붙이는 관용)
- `2026B_Spring/demo/src/main/resources/application.properties`, `demo/src/main/resources/sql/practice5.sql` (**설정과 시드를 함께 옮기는 자리** — 시드 네 줄이 함께 다니는 이유(`data-locations` 로 파일을 정하고 `defer-datasource-initialization` 으로 표 생성 뒤로 미루고 `mode=always` 로 MySQL에서도 돌게 하고 `encoding` 으로 한글이 깨지지 않게 읽기)와 `ddl-auto=create-drop`+`show-sql` 로 엔티티만 고쳐 표 모양을 확인하는 통로, 시드가 SQL로 바로 나가 리스너를 거치지 않으므로 감사 컬럼에 `NOW()` 를 직접 적는 점과 부모 `INSERT` 를 자식보다 먼저 두는 순서)

## 관련 노트

[[Spring MOC]] · [[Spring day08 댓글 쪽으로 한 번 더 관통시키기]] · [[KDT_2026 학습 지도]]
