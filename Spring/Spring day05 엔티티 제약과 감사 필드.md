---
출처: Claude 분석
원본: KDT_2026/2026B_Spring/springweb/src/main/java/day05, springweb/src/main/java/day05/practice, springweb/src/main/java/day04/practice2/AppStart.java, springweb/src/main/resources/application.properties, springweb/src/main/resources/sql/practice3.sql
작성일: 2026-09-03
tags: [학습, java]
---

# Spring day05 — 엔티티 제약과 감사 필드

> 실습 파일: `2026B_Spring/springweb/src/main/java/day05/TestEntity.java`, `BaseTime.java`, `AppStart.java`, `day05/practice/MovieEntity.java`, `day05/practice/BaseTime.java`, `day05/practice/AppStart.java`, `day04/practice2/AppStart.java`, `springweb/src/main/resources/application.properties`, `springweb/src/main/resources/sql/practice3.sql`
> 허브: [[Spring MOC]] · 이전: [[Spring day04 JPA 엔티티와 리포지토리]] · 다음: [[Spring day05 DTO 변환과 초기 데이터 적재]]

[[Spring day04 JPA 엔티티와 리포지토리]] 에서는 표를 SQL로 먼저 만들어 두고 엔티티를 거기에 맞췄다. 이번은 방향이 뒤집힌다. **엔티티가 표의 설계도가 되고, 표는 서버가 뜰 때 그 설계도대로 만들어진다.**

방향이 뒤집히면 적을 것이 늘어난다. 지금까지 엔티티에는 필드 이름과 타입밖에 없었는데, 표를 만들려면 `not null` 인지 몇 글자까지인지 중복이 되는지를 어딘가에 적어야 한다. 그 자리가 `@Column` 이다.

그리고 두 번째 갈래가 붙는다. **어느 표에나 똑같이 들어가는 필드**(만든 시각·고친 시각)를 표마다 되풀이해 적지 않고 위로 올려 두는 구조다.

```
day04   sample.sql 이 표를 만든다     →  엔티티가 그 표에 맞춘다
day05   엔티티가 표의 모양을 적는다    →  뜰 때 표가 만들어진다
```

| 자리 | 하는 일 |
| --- | --- |
| `application.properties` 의 `ddl-auto` | 표를 누가 만들지 정하기 (1-1) |
| `TestEntity` 의 `@Column` | 컬럼의 제약을 자바 쪽에 적기 (1-2·1-3) |
| `BaseTime` 의 `@MappedSuperclass` | 되풀이되는 필드를 위로 올리기 (1-5) |
| `@EntityListeners(AuditingEntityListener.class)` | 값을 채워 줄 구현체 붙이기 (1-6) |
| `@CreatedDate`·`@LastModifiedDate` | 어느 필드에 무엇을 채울지 표시하기 (1-7) |
| `AppStart` 의 `@EnableJpaAuditing` | 이 전부를 켜는 한 줄 (1-8) |
| `day05/practice` 의 `MovieEntity` | 같은 구조를 새 도메인에 옮겨 보기 (1-10) |
| `sql/practice3.sql` 과 `sql.init` 설정 | 실습마다 DB와 시드를 갈라 두기 (1-11) |

## 1. 배운 내용

### 1-1. 표를 SQL이 아니라 엔티티로 만들기

설정 파일에서 DB와 `ddl-auto` 가 함께 바뀌었다.

```properties
spring.datasource.url = jdbc:mysql://localhost:3306/mydb0903
spring.jpa.hibernate.ddl-auto=create-drop
spring.jpa.show-sql=true
spring.jpa.properties.hibernate.format_sql=true
```

`ddl-auto` 는 **서버가 뜰 때 표를 어떻게 할지**를 정하는 값이다. 다섯 갈래가 있다.

| 값 | 뜰 때 | 내려갈 때 |
| --- | --- | --- |
| `create` | 표를 지우고 다시 만든다 | (그대로) |
| `create-drop` | 표를 지우고 다시 만든다 | 표를 지운다 |
| `update` | 없으면 만들고 있으면 컬럼만 더한다 | (그대로) |
| `validate` | 엔티티와 표가 맞는지 보기만 한다 | (그대로) |
| `none` | 아무것도 하지 않는다 | (그대로) |

`create-drop` 을 고른 것은 **엔티티를 고칠 때마다 표를 새로 보고 싶기 때문**이다. 표시 하나를 바꿔 붙이고 서버를 다시 띄우면 그 결과가 표 모양에 바로 나타난다. 이번 실습처럼 `@Column` 속성을 하나씩 바꿔 가며 확인하는 자리에 어울린다.

대신 **뜰 때마다 데이터가 날아간다.** `create` 계열이 실제 데이터가 든 DB를 가리키고 있으면 그대로 지워지므로, 실습용 DB를 따로 두는 편이 안전하다. 여기서 DB 이름이 날짜별로 갈리는 것도 그런 배치로 읽힌다.

`show-sql` 과 `format_sql` 이 함께 켜져 있는 것이 이번에 특히 값어치가 있다. **하이버네이트가 만든 `create table` 문이 그대로 콘솔에 찍히기 때문**이다. `@Column` 을 고쳐 붙였을 때 실제로 무엇이 달라졌는지를 눈으로 확인하는 통로가 여기다.

```
Hibernate:
    create table test (
        no integer not null auto_increment,
        ...
    )
```

[[Spring day04 JPA 엔티티와 리포지토리]] 에서 "표는 SQL로 만들고 `validate` 로 두는 배치"를 적어 뒀는데, 그것은 운영 쪽 이야기다. 배우는 자리에서는 반대로 두고 엔티티가 표를 만들게 해 봐야 표시와 표의 대응이 보인다.

### 1-2. 컬럼의 제약을 자바 쪽에 적기 — @Column

엔티티가 표를 만들게 되면서, 지금까지 SQL에만 있던 것들을 자바에 적게 된다.

```java
@Entity
@Table(name = "test")
public class TestEntity {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Integer no;

    @Column(name = "name", nullable = true, length = 100, unique = true)
    private String name;

    @Column(columnDefinition = "varchar(100) not null default '제품설명'")
    private String desc;

    @Column(insertable = true, updatable = true)
    private Integer price;
}
```

속성 여섯 개가 나온다. 각각이 `create table` 문의 어느 자리로 가는지가 요점이다.

| 속성 | 기본값 | 만들어지는 SQL |
| --- | --- | --- |
| `name` | 필드 이름 | 컬럼 이름 |
| `nullable` | `true` | `false` 면 `not null` |
| `length` | `255` | `varchar(길이)` |
| `unique` | `false` | `true` 면 `unique` 제약 |
| `columnDefinition` | (없음) | 적은 SQL 조각을 통째로 |
| `insertable`·`updatable` | 둘 다 `true` | (SQL이 아니라 JPA의 동작) |

앞의 넷과 뒤의 둘이 성격이 다르다. **`name`·`nullable`·`length`·`unique` 는 표를 만들 때 쓰이고, `insertable`·`updatable` 은 표와 상관없이 JPA가 SQL을 만들 때 쓰인다.**

```
nullable = false   →  create table 에 not null 이 붙는다
updatable = false  →  표는 그대로, update 문에서 이 컬럼이 빠진다
```

이 갈림이 뒤에서 감사 필드를 굳힐 때 실제로 쓰인다(2-3).

`length` 는 `String` 에만 걸린다. 숫자 타입에는 `varchar` 길이라는 개념이 없어서 무시된다. [[Spring day04 JPA 엔티티와 리포지토리]] 에서 "`VARCHAR(255)` 와 `VARCHAR(50)` 이 자바에서는 둘 다 `String` 이라 길이 제한이 DB에만 남는다"고 적어 뒀는데, `length` 가 그 제한을 코드로 끌어오는 자리다.

### 1-3. 애노테이션은 바로 다음 선언 하나에 붙는다

`@Column` 을 어디에 적는가가 눈에 띄는 대목이다. 애노테이션은 **바로 뒤에 오는 선언 하나**에만 붙는다. 사이에 빈 줄이 있어도 상관없고, 사이에 다른 애노테이션이 끼어 있어도 상관없다 — 셋이 쌓여 있으면 셋 다 같은 하나에 붙는다.

```java
@Id
@GeneratedValue(strategy = GenerationType.IDENTITY)
@Column(name = "name")
private Integer no;      // ← 위의 셋이 전부 no 에 붙는다

private String name;     // ← 아무것도 안 붙은 상태
```

표시가 위아래로 늘어서 있으면 어느 필드에 걸리는지가 눈으로는 흐려지는데, 규칙 자체는 "다음 선언 하나"로 단순하다. `@Column(name=…)` 이 실제로 어느 컬럼 이름을 바꿨는지는 1-1의 `show-sql` 로 찍히는 `create table` 문을 보면 바로 갈린다. **표시를 붙인 결과를 짐작하지 않고 생성된 DDL로 확인하는 습관**이 이 자리에서 값어치가 크다.

### 1-4. columnDefinition — SQL 조각을 그대로 적기

속성 하나가 성격이 다르다.

```java
@Column(columnDefinition = "varchar(100) not null default '제품설명'")
private String desc;
```

`nullable`·`length` 는 "무엇을"만 적고 SQL 문장은 하이버네이트가 만드는데, `columnDefinition` 은 **컬럼 정의 자리에 들어갈 SQL을 통째로 적는다.** 그래서 다른 속성으로는 못 적는 것을 적을 수 있다.

| 적고 싶은 것 | 전용 속성 | `columnDefinition` |
| --- | --- | --- |
| `not null` | `nullable = false` | 문자열 안에 적는다 |
| 길이 | `length = 100` | 문자열 안에 적는다 |
| `default` 값 | (없음) | 이 방법뿐 |
| `comment` | (없음) | 이 방법뿐 |
| DB 고유 타입 | (없음) | 이 방법뿐 |

**기본값(`default`)을 적을 자리가 전용 속성에는 없다.** 그래서 기본값이 필요해지면 `columnDefinition` 으로 넘어가게 된다.

잃는 것도 분명하다. 문자열 안이 곧 그 DB의 SQL이라 **DB를 갈아 끼우면 그대로 깨진다.** JPA를 쓰는 값어치 중 하나가 "어느 DB든 같은 코드"였는데, 이 속성을 쓰는 순간 그 자리만 DB에 묶인다.

`columnDefinition` 과 다른 속성을 같이 적으면 `columnDefinition` 쪽이 이긴다. 둘 다 적어 두면 코드에는 두 가지가 보이는데 표에는 하나만 반영되므로, 이 속성을 쓸 때는 그 컬럼의 제약을 전부 그 문자열 안에 모아 두는 편이 읽기에 낫다.

한 가지 더 있다. **기본값은 DB가 채우는 것이지 자바 객체가 아는 값이 아니다.** `default '제품설명'` 을 적어 두고 값을 넣지 않으면 표에는 기본값이 들어가지만, 방금 저장한 자바 객체의 그 필드는 여전히 `null` 이다. 값을 보려면 다시 읽어 와야 한다.

### 1-5. 되풀이되는 필드를 위로 올리기 — @MappedSuperclass

두 번째 갈래다. 새 파일이 하나 늘었다.

```java
@Getter
@NoArgsConstructor
@MappedSuperclass                                 // 현재 클래스는 상속용 매핑
@EntityListeners(AuditingEntityListener.class)    // 리스너 구현체 등록
public class BaseTime {
    @CreatedDate
    private LocalDateTime createDate;

    @LastModifiedDate
    private LocalDateTime updateDate;
}
```

**만든 시각과 고친 시각은 어느 표에나 들어간다.** 게시판에도 상품에도 회원에도 들어가는데, 표마다 엔티티에 두 필드를 되풀이해 적으면 같은 코드가 도메인 수만큼 늘어난다. [[Spring day04 JPA 엔티티와 리포지토리]] 의 `BaseDao` 때와 같은 모양의 문제다 — **같은 코드는 위로 올린다.**

올리는 방법이 두 갈래인데, 여기 쓰인 것이 `@MappedSuperclass` 다.

| | `@MappedSuperclass` | `@Entity` 를 상속 |
| --- | --- | --- |
| 부모가 표를 갖는가 | 갖지 않는다 | 갖는다 |
| 부모로 조회할 수 있는가 | 못 한다 | 할 수 있다 |
| 자식 표에 생기는 것 | 부모 필드가 컬럼으로 내려온다 | 전략에 따라 갈린다 |
| 쓰는 자리 | 공통 필드 모으기 | 상속 관계를 표로 옮기기 |

`@MappedSuperclass` 는 **"이 클래스는 표가 아니라 물려줄 필드 묶음이다"** 라는 선언이다. `BaseTime` 이라는 표는 만들어지지 않고, 이 클래스를 물려받은 엔티티의 표에 `create_date`·`update_date` 컬럼이 붙는다.

```
BaseTime            (표 없음)
  └─ 물려받은 엔티티  →  자기 컬럼 + create_date + update_date
```

물려받는 쪽에서 할 일은 `extends BaseTime` 한 줄이다. 상속을 걸어야 필드가 내려오고, 걸지 않으면 `BaseTime` 은 그냥 아무도 안 쓰는 클래스로 남는다. 표시가 아무리 붙어 있어도 **표시는 스스로 아무 일도 하지 않는다**는 Spring day03 애노테이션과 리플렉션 의 정리가 여기서도 그대로다.

`@Getter` 만 있고 `@Setter` 가 없는 것도 읽어 둘 만하다. **이 두 필드는 사람이 값을 넣는 자리가 아니라 프레임워크가 채우는 자리**라, 밖에서 고칠 통로를 열어 둘 이유가 없다. 꺼내 보기만 하면 된다.

### 1-6. 값을 누가 채우는가 — @EntityListeners

필드에 표시만 붙여 놓는다고 값이 채워지지는 않는다. **그 표시를 읽어 값을 넣어 주는 쪽**이 있어야 한다.

```java
@EntityListeners(AuditingEntityListener.class)
```

`AuditingEntityListener` 가 그 일을 하는 구현체다. JPA에는 **엔티티가 저장·수정·삭제되기 직전과 직후에 끼어드는 자리**(생명주기 콜백)가 있고, 리스너는 거기에 붙는 객체다.

```
save() 호출
  → 저장 직전   AuditingEntityListener 가 끼어든다
                @CreatedDate 필드에 현재 시각을 넣는다
  → insert 나감
```

`@EntityListeners(…)` 는 **어느 리스너를 이 엔티티에 붙일지 지목하는 표시**다. `BaseTime` 에 붙여 두면 이것을 물려받은 엔티티 전부에 함께 붙는다 — 공통 필드를 위로 올린 값어치가 표시 쪽에서도 나오는 자리다.

Spring day03 애노테이션과 리플렉션 에서 "정의 → 표시 붙이기 → 읽어서 실행" 세 단계를 직접 만들어 봤는데, 감사 기능이 그 구조 그대로다.

| 단계 | day03의 실습 | 여기 |
| --- | --- | --- |
| 표시를 정의한다 | `@interface` 로 직접 | 스프링이 만들어 둔 `@CreatedDate` |
| 표시를 붙인다 | 메소드에 | 필드에 |
| 읽어서 실행한다 | `getDeclaredMethods()` 로 훑기 | `AuditingEntityListener` |

### 1-7. 어느 필드에 무엇을 채울지 — @CreatedDate와 @LastModifiedDate

리스너가 필드를 알아보는 근거가 이 두 표시다.

| 표시 | 채워지는 때 |
| --- | --- |
| `@CreatedDate` | 처음 저장될 때 한 번 |
| `@LastModifiedDate` | 저장될 때와 고쳐질 때마다 |

**처음 저장될 때는 둘 다 채워진다.** 그래서 만들고 한 번도 안 고친 줄은 두 값이 같고, 고친 적이 있으면 갈린다. "이 줄이 수정된 적 있는가"를 두 값을 견줘 알 수 있는 것이 이 배치의 부수 효과다.

가져오는 자리가 `org.springframework.data.annotation` 인 것도 짚어 둘 만하다. `@Entity`·`@Column`·`@Id` 는 `jakarta.persistence`(JPA 규격)에서 오는데, 이 둘은 **스프링 데이터가 얹은 것**이다. 규격에는 없는 편의 기능이라 층이 다르다.

```
jakarta.persistence.*                    JPA 규격 — @Entity·@Id·@Column
org.springframework.data.annotation.*    스프링 데이터 — @CreatedDate·@LastModifiedDate
org.springframework.data.jpa.domain.*    스프링 데이터 JPA — AuditingEntityListener
```

[[Spring day04 JPA 엔티티와 리포지토리]] 에서 정리한 JPA(규격)·하이버네이트(구현체)·Spring Data JPA(편의 층) 세 층이, 애노테이션을 가져오는 패키지 이름에 그대로 드러나는 자리다. 자동 완성으로 고를 때 어느 층에서 온 것인지 보는 습관이 붙으면 나중에 문서를 찾을 자리도 갈라진다.

### 1-8. 이 전부를 켜는 한 줄 — @EnableJpaAuditing

마지막 조각이 진입점에 붙는다.

```java
@SpringBootApplication
@EnableJpaAuditing      // JPA Entity 등록/수정 감사 기능 활성화
public class AppStart {
    public static void main(String[] args) {
        SpringApplication.run(AppStart.class);
    }
}
```

`@Enable…` 계열은 스프링에서 자주 보게 되는 모양이다. **기능 한 벌에 필요한 빈들을 한 번에 등록하는 표시**로, 이름이 곧 켜는 기능이다(`@EnableScheduling`·`@EnableCaching`·`@EnableAsync` 등).

감사 기능이 도는 데 필요한 세 자리를 한 번에 놓고 보면 이렇게 된다.

```
① 필드에 표시            @CreatedDate / @LastModifiedDate      "무엇을 채울지"
② 엔티티에 리스너         @EntityListeners(AuditingEntityListener)  "누가 채울지"
③ 진입점에 활성화         @EnableJpaAuditing                    "그 누가를 만들어 둘지"
```

**셋 중 하나라도 빠지면 값이 `null` 로 남는다.** 표시만 붙이면 읽는 쪽이 없고, 리스너까지 붙여도 그 리스너가 쓸 빈이 없으면 채울 것을 못 찾는다. 시각이 안 채워질 때 이 셋을 위에서부터 훑어 보는 것이 가장 빠른 순서다.

`@EnableJpaAuditing` 이 진입점에 붙는 것도 이유가 있다. 컴포넌트 스캔 범위와 마찬가지로 **이 설정은 애플리케이션 하나 단위**라, 실습마다 진입점이 갈려 있으면 감사를 쓰는 실습의 진입점에 붙어 있어야 한다.

### 1-9. LocalDateTime과 표의 타입

시각을 담는 타입으로 `LocalDateTime` 을 골랐다.

| 자바 타입 | 담는 것 | MySQL 쪽 |
| --- | --- | --- |
| `LocalDate` | 날짜만 | `date` |
| `LocalTime` | 시각만 | `time` |
| `LocalDateTime` | 날짜 + 시각 | `datetime` |

`java.util.Date`·`Calendar` 를 쓰던 자리를 자바 8의 `java.time` 이 대신한 것이라, 지금 새로 적는 코드에서는 이쪽을 고른다. 값이 바뀌지 않는 객체(불변)이고, 날짜 계산 메소드가 타입에 붙어 있어 다루기가 낫다.

`Local` 이 붙은 이름이 말하는 것은 **시간대 정보를 들고 있지 않다**는 뜻이다. "2026-09-03 14:30"만 있고 그것이 어느 지역의 14시 30분인지는 값에 없다. 서버가 한 곳에 있으면 문제가 안 되는데, 지역이 갈리는 사용자를 다루기 시작하면 걸리는 자리다(2-6).

### 1-10. 같은 구조를 새 도메인에 옮겨 보기

앞의 것들을 한 번 더, 이번에는 제품이 아니라 영화로 짜 본다. 실습 묶음이 `day05.practice` 라는 패키지로 따로 갈리고, 그 안에 **진입점·공통 클래스·엔티티 세 벌이 새로 놓인다.**

```
day05/                    TestEntity · BaseTime · AppStart
day05/practice/           MovieEntity · BaseTime · AppStart      ← 같은 세 자리를 다시
```

같은 이름의 클래스가 두 벌이 되는데, **패키지가 다르면 서로 다른 클래스**라 부딪히지 않는다. 진입점을 실습마다 따로 두는 배치도 그대로 이어진다 — 1-8에서 정리한 대로 `@EnableJpaAuditing` 은 애플리케이션 하나 단위라, 실습 묶음마다 진입점이 갈려 있으면 **그 묶음의 진입점에 붙어 있어야** 감사가 돈다.

엔티티는 이렇게 된다.

```java
@Entity
@Table
@Getter @Setter @ToString
@AllArgsConstructor @NoArgsConstructor
public class MovieEntity {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Integer movieId;

    @Column(nullable = false)
    private String title;

    @Column(length = 100)
    private String director;

    private LocalDate releasedate;
    private Double raiting;
}
```

필드마다 어떤 판단이 들어갔는지를 늘어놓으면 이렇다.

| 필드 | 적은 것 | 근거 |
| --- | --- | --- |
| `movieId` | `@Id` + `IDENTITY` | 키는 DB의 자동 증가에 맡긴다 |
| `title` | `nullable = false` | 제목 없는 영화는 두지 않는다 |
| `director` | `length = 100` | `varchar(255)` 를 100으로 줄인다 |
| `releasedate` | 표시 없음 | 제약이 필요 없으면 안 적는다 |
| 평점 | `Double` | 소수점이 붙는 값 |

**표시를 안 붙인 필드가 있다는 것이 오히려 요점이다.** `@Column` 은 제약을 적을 때만 붙이는 것이고, 붙이지 않으면 1-2 표의 기본값(`nullable = true`·`length = 255`·컬럼 이름은 필드 이름)이 그대로 걸린다. 제약이 없는 자리에까지 빈 `@Column` 을 붙일 이유는 없다.

`@Table` 을 이름 없이 붙인 것도 갈래가 하나다. 이름을 적지 않으면 **클래스 이름이 그대로 표 이름의 근거**가 되고, 2-8의 카멜→스네이크 변환이 여기에도 걸린다.

```
클래스 MovieEntity   →  표 movie_entity
필드  releasedate    →  컬럼 releasedate      (붙여 쓴 이름은 나눌 자리가 없다)
필드  movieId        →  컬럼 movie_id
```

표 이름을 다른 것으로 두고 싶으면 `@Table(name = "movie")` 처럼 적어야 한다. **자바 쪽 이름과 표 쪽 이름이 갈리기 시작하는 자리**라, 시드 SQL을 함께 쓸 때는 이 이름이 실제로 무엇으로 만들어졌는지를 `show-sql` 로 확인해 두는 편이 안전하다(1-1).

날짜 타입을 `LocalDate` 로 고른 것은 1-9의 표를 실제로 쓴 자리다. 감사 필드는 "언제 저장했는가"라 시각까지 필요해서 `LocalDateTime` 이었는데, **개봉일은 날짜만 있으면 되므로 `LocalDate`** 다. 담을 것에 맞춰 세 타입 중 하나를 고르는 것이지 큰 쪽을 늘 쓰는 것이 아니다.

### 1-11. 실습마다 DB와 시드를 갈라 두기

설정 파일이 이 실습에 맞춰 함께 움직인다. 바뀐 자리가 둘이다.

```properties
spring.datasource.url = jdbc:mysql://localhost:3306/practice3
spring.sql.init.data-locations=classpath:/sql/practice3.sql
spring.jpa.defer-datasource-initialization=true
spring.sql.init.mode=always
spring.sql.init.encoding=UTF-8
```

**연동할 DB와 넣을 시드가 짝을 이뤄 갈린다.** `ddl-auto` 가 `create-drop` 이라 뜰 때마다 표가 새로 만들어지므로(1-1), 시드도 뜰 때마다 다시 들어가야 눈으로 볼 데이터가 생긴다.

여기서 순서가 중요해진다.

```
서버 뜸
 → 하이버네이트가 엔티티를 보고 create table          (ddl-auto)
 → 그 다음에 data-locations 의 SQL 이 돈다             (defer-…=true)
```

`defer-datasource-initialization=true` 가 하는 일이 **이 순서를 뒤로 미루는 것**이다. 이 값이 없으면 시드 SQL이 표가 만들어지기 전에 돌아서 넣을 표를 못 찾는다. `ddl-auto` 로 표를 만들면서 시드도 함께 쓰는 배치라면 이 한 줄이 늘 따라붙는다.

| 설정 | 하는 일 |
| --- | --- |
| `data-locations` | 넣을 SQL 파일의 자리 (`classpath:` = `resources/`) |
| `mode=always` | 내장 DB가 아니어도 시드를 돌린다 |
| `defer-datasource-initialization` | 표가 만들어진 뒤로 시드를 미룬다 |
| `encoding=UTF-8` | 한글이 든 SQL 파일을 읽을 때 |

`mode` 의 기본값이 `embedded` 라 **H2 같은 내장 DB에서만 돌고 MySQL에서는 그냥 넘어간다.** MySQL을 붙여 두고 시드가 안 들어가면 이 값을 먼저 본다.

시드 SQL 자체는 `insert` 를 줄지어 두는 단순한 모양이다.

```sql
insert into movie(title, director, releasedate, rating, created_date, updated_date)
    values('영화제목1', '감독1', '2026-09-04', 10, now(), now());
```

두 가지를 함께 짚어 둘 만하다. 하나는 **시드 SQL의 컬럼 이름이 실제로 만들어진 표와 맞아야 한다**는 것이다. 표를 엔티티가 만드는 배치에서는 컬럼 이름의 근거가 자바 필드 이름과 네이밍 전략이라, 시드를 손으로 적을 때 그 규칙을 따라가야 한다. 앞의 카멜→스네이크 이야기가 여기서 실제 값어치를 갖는다.

다른 하나는 문자열을 감싸는 따옴표다. MySQL은 큰따옴표도 문자열로 받아 주지만 **표준 SQL에서 문자열은 홑따옴표**이고, 큰따옴표는 식별자(컬럼·표 이름)를 감싸는 자리다. DB 설정에 따라 큰따옴표가 식별자로 읽히기도 하므로, 시드 SQL은 홑따옴표로 적어 두는 편이 안전하다.

감사 필드도 한 번 더 짚인다. `BaseTime` 을 같은 패키지에 다시 두더라도, **공통 클래스를 만드는 것과 그 필드를 물려받는 것은 별개의 단계**다. 1-5에서 정리한 대로 `extends BaseTime` 한 줄이 걸려야 `create_date`·`update_date` 컬럼이 그 표에 생긴다. 시드 SQL에 시각 컬럼이 들어 있다면 표에도 그 컬럼이 있어야 하므로, 상속이 걸렸는지와 만들어진 `create table` 문을 함께 보는 것이 확인 순서다.

### 1-12. 정리 — 이번에 늘어난 두 축

day04까지의 엔티티와 견주면 늘어난 것이 두 갈래다.

| | day04 | day05 |
| --- | --- | --- |
| 엔티티가 적는 것 | 필드 이름과 타입 | + 컬럼의 제약 |
| 표를 만드는 쪽 | `sample.sql` | 엔티티(`ddl-auto`) |
| 공통 필드 | 표마다 되풀이 | `@MappedSuperclass` 로 위에 |
| 값을 채우는 쪽 | 코드가 직접 | 리스너가 자동으로 |

두 갈래가 향하는 곳은 같다. **표에 관한 사실을 한 자리에 모으는 것**이다. 제약이 SQL 파일에만 있으면 자바 코드를 읽어서는 알 수 없고, 시각 필드를 표마다 적으면 같은 규칙이 여러 자리에 흩어진다. 엔티티 하나만 보면 그 표를 알 수 있게 두는 배치가 이번 실습의 방향이다.

## 2. 추가로 알면 좋은 활용법

### 2-1. @Column이 언제 일을 하는가

`ddl-auto` 값에 따라 `@Column` 의 무게가 달라진다.

| `ddl-auto` | `@Column` 이 하는 일 |
| --- | --- |
| `create`·`create-drop`·`update` | 표를 만들 때 실제로 반영된다 |
| `validate` | 표와 맞는지 검사하는 기준이 된다 |
| `none` | 표에는 영향이 없다 (문서로 남는다) |

운영에서 표를 SQL로 관리하면 `@Column` 은 표를 만들지 않지만, **`validate` 를 켜 두면 엔티티와 표가 어긋난 것을 서버가 뜰 때 잡아 준다.** 어긋남을 요청 처리 중이 아니라 시작 시점에 잡는다는 점에서 값어치가 있다.

`insertable`·`updatable` 은 `ddl-auto` 와 무관하게 언제나 일한다. 표를 만드는 속성이 아니라 SQL을 만드는 속성이기 때문이다.

### 2-2. 나가는 DDL을 파일로 남겨 보기

콘솔에 찍히는 것만으로 모자라면 생성된 DDL을 파일로 뽑을 수 있다.

```properties
spring.jpa.properties.jakarta.persistence.schema-generation.scripts.action=create
spring.jpa.properties.jakarta.persistence.schema-generation.scripts.create-target=schema.sql
```

엔티티에 적은 표시가 실제로 어떤 `create table` 이 되는지를 한 파일로 놓고 볼 수 있어서, **자동 생성으로 시작해 그 결과를 손질한 뒤 SQL 관리로 넘어가는** 이행에 쓰기 좋다.

### 2-3. 생성 시각을 굳히기 — updatable = false

`@CreatedDate` 는 처음 저장될 때만 채워지는데, 그 뒤 코드에서 값을 바꾸면 `update` 로 나갈 수 있다. 아예 막아 두려면 `@Column` 쪽에서 잠근다.

```java
@CreatedDate
@Column(updatable = false)
private LocalDateTime createDate;
```

**`update` 문에서 이 컬럼이 빠지므로 어떤 경로로도 안 바뀐다.** 1-2에서 갈라 둔 "표를 만드는 속성 / SQL을 만드는 속성"의 뒤쪽이 실제로 쓰이는 자리다.

### 2-4. 누가 만들었는지까지 남기기 — @CreatedBy

감사에는 시각 말고 사람 축이 하나 더 있다.

| 표시 | 채워지는 것 |
| --- | --- |
| `@CreatedDate`·`@LastModifiedDate` | 시각 |
| `@CreatedBy`·`@LastModifiedBy` | 그 일을 한 사용자 |

사람 쪽은 시각과 달리 **"지금 누구인가"를 프레임워크가 스스로 알 수 없다.** 그래서 그것을 알려 주는 빈을 하나 등록한다.

```java
@Bean
public AuditorAware<String> auditorProvider() {
    return () -> Optional.of("현재 로그인한 사용자");
}
```

로그인 기능이 붙은 뒤에 실제 값이 들어가는 자리다. 시각은 표시만으로 되고 사람은 구현이 하나 필요하다는 갈림이, **프레임워크가 대신해 줄 수 있는 것의 경계**를 보여 준다.

### 2-5. 표시 대신 콜백 메소드로 채우기

스프링 데이터를 쓰지 않고 JPA 규격만으로도 같은 일을 할 수 있다.

```java
@PrePersist
public void onCreate() {
    createDate = LocalDateTime.now();
    updateDate = LocalDateTime.now();
}

@PreUpdate
public void onUpdate() {
    updateDate = LocalDateTime.now();
}
```

| | 감사 표시 | 생명주기 콜백 |
| --- | --- | --- |
| 필요한 것 | 스프링 데이터 + `@EnableJpaAuditing` | JPA 규격만 |
| 적는 양 | 표시 두 개 | 메소드 두 개 |
| 값을 바꾸기 | 리스너가 정한 대로 | 원하는 대로 |

`AuditingEntityListener` 가 하는 일이 결국 이 콜백을 대신 적어 주는 것이라, **직접 적어 보면 리스너가 무엇을 하는지가 손에 잡힌다.** 규격만으로 도는 쪽이라 스프링 밖에서도 그대로 동작한다는 것도 갈림이다.

### 2-6. 시간대가 걸리는 자리

`LocalDateTime` 은 시간대를 들고 있지 않아서, 서버가 여러 지역에 있거나 사용자의 지역이 갈리면 같은 값이 다르게 읽힌다.

| 타입 | 시간대 | 어울리는 자리 |
| --- | --- | --- |
| `LocalDateTime` | 없음 | 서버가 한 지역일 때 |
| `ZonedDateTime` | 지역까지 | 지역을 값에 남겨야 할 때 |
| `Instant` | UTC 기준 시점 | 저장은 UTC, 표시만 지역 |

흔한 배치는 **저장은 `Instant`(또는 UTC 기준)로 하고 보여 줄 때만 사용자의 지역으로 바꾸는** 쪽이다. DB 세션의 시간대 설정과 자바 쪽 기본 시간대가 어긋나면 몇 시간씩 밀리는 일이 생기므로, 시각을 다루기 시작하면 양쪽 설정을 함께 확인해 두는 편이 안전하다.

### 2-7. 예약어와 겹치는 컬럼 이름

DB에는 문법에 쓰이는 예약어가 있고(`desc`·`order`·`group`·`key` 등), 컬럼 이름이 그것과 겹치면 만들어진 SQL이 문법으로 읽혀 걸린다. 자바 쪽에서는 아무 문제가 없는 이름이라 **코드만 봐서는 짐작이 안 되고 실행할 때 드러나는** 갈래다.

피하는 방법이 몇 가지다.

| 방법 | 적는 곳 |
| --- | --- |
| 컬럼 이름을 바꾼다 | `@Column(name = "description")` |
| 식별자로 감싸게 한다 | `@Column` 의 이름을 백틱으로 감싸 적는다 |
| 전역으로 감싸게 한다 | `spring.jpa.properties.hibernate.globally_quoted_identifiers=true` |

필드 이름과 컬럼 이름을 갈라 둘 수 있다는 것이 `@Column(name=…)` 의 값어치다. 자바 쪽 이름은 읽기 좋게 두고 DB 쪽 이름만 바꿔 두면 된다.

### 2-8. 카멜과 스네이크가 갈리는 자리

`createDate` 라고 적은 필드가 표에서는 `create_date` 가 된다. 하이버네이트의 기본 네이밍 전략이 **카멜 표기를 스네이크로 바꾸기** 때문이다.

```
자바 필드   createDate
표 컬럼     create_date
```

`@Column(name=…)` 을 적으면 그 이름이 그대로 쓰이고, 안 적으면 이 변환이 걸린다. 표를 SQL로 먼저 만들어 둔 상태라면 이 변환 규칙이 표의 컬럼 이름과 맞는지가 붙고 안 붙고를 가른다. 규칙 자체를 바꾸려면 네이밍 전략 빈을 갈아 끼운다.

### 2-9. 공통 필드를 더 두기

`BaseTime` 에 시각 둘만 있지만, 같은 자리에 더 올릴 수 있는 것들이 있다.

| 올릴 만한 것 | 쓰이는 자리 |
| --- | --- |
| `deleted` 플래그 | 지우지 않고 지운 것으로 표시하기 |
| `@Version` | 동시에 고칠 때의 충돌 감지 |
| 등록자·수정자 | 감사의 사람 축 (2-4) |

다만 **정말 모든 표에 들어가는 것만** 올리는 편이 낫다. 일부 표에만 필요한 필드를 공통에 올리면 쓰지 않는 컬럼이 표마다 생기고, 그것을 피하려고 공통 클래스를 여러 벌 만들기 시작하면 원래 줄이려던 되풀이가 다른 모양으로 돌아온다.

## 3. 더 나아가 알면 좋은 것

### 3-1. 엔티티 생명주기 콜백 일곱 자리

2-5에서 본 `@PrePersist` 는 일곱 개 중 하나다.

| 표시 | 불리는 때 |
| --- | --- |
| `@PrePersist` / `@PostPersist` | `insert` 앞뒤 |
| `@PreUpdate` / `@PostUpdate` | `update` 앞뒤 |
| `@PreRemove` / `@PostRemove` | `delete` 앞뒤 |
| `@PostLoad` | 조회해 객체가 만들어진 뒤 |

이 자리들이 열려 있다는 것이 **엔티티에 관한 일을 서비스 코드에 흩지 않고 엔티티 자신에게 맡길 수 있는** 근거가 된다. 감사 필드가 그 첫 예다. 다만 콜백 안에서 다른 엔티티를 건드리거나 쿼리를 날리는 것은 권장되지 않는 쪽이라, 자기 필드를 손보는 정도로 두는 것이 무난하다.

### 3-2. 지우지 않고 지운 것으로 두기 — 소프트 삭제

감사 필드를 두는 이유가 "언제 무슨 일이 있었는지 남기기"인데, 그 연장선에 **삭제를 실제로 지우지 않는** 배치가 있다.

```java
@SQLDelete(sql = "update test set deleted = true where no = ?")
@SQLRestriction("deleted = false")
public class TestEntity extends BaseTime { … }
```

`delete` 를 `update` 로 바꿔치고, 조회에는 조건을 자동으로 끼워 넣는 방식이다. 지운 것도 이력으로 남으므로 되살릴 수 있고, 지운 시각까지 감사 필드에 남는다. 대신 모든 조회에 조건이 붙는다는 것과, 유니크 제약이 지운 줄까지 세는 문제가 따라온다.

### 3-3. 표를 코드가 만들게 두지 않는 쪽 — 마이그레이션 도구

`ddl-auto` 는 배우는 자리에서 편한데, 표가 이미 데이터를 들고 있는 자리에서는 쓸 수 없다. 그 자리를 맡는 것이 마이그레이션 도구다(Flyway·Liquibase).

```
V1__create_test.sql
V2__add_price_column.sql
V3__…
```

**표의 변경을 번호 붙은 SQL 파일로 쌓아 두고, 어디까지 적용됐는지를 DB가 기억한다.** 코드 이력과 표 이력이 같이 관리되므로 어느 시점의 코드가 어느 모양의 표를 기대하는지가 남는다. `ddl-auto` 는 `validate` 로 두고 실제 변경은 이쪽이 맡는 조합이 흔하다.

### 3-4. 동시에 고칠 때 — @Version과 낙관적 락

`@LastModifiedDate` 가 "마지막으로 고친 시각"을 남기는데, 두 사람이 거의 동시에 고치면 **나중 것이 앞의 변경을 덮어쓴다.** 시각은 남지만 사라진 변경은 알 수 없다.

```java
@Version
private Long version;
```

이 필드가 있으면 `update` 문에 버전 조건이 붙고, 그 사이에 다른 쪽이 고쳐 버전이 올라갔으면 예외가 난다. **막는 것이 아니라 부딪혔다는 것을 알려 주는** 방식이라 낙관적이라 부른다. 감사 필드가 기록이라면 이쪽은 판정이다.

### 3-5. 상속을 표로 옮기는 세 갈래

`@MappedSuperclass` 는 상속을 표로 옮기지 않고 필드만 내려보내는 쪽이었다. 상속 관계 자체를 표로 옮기는 갈래도 있다(`@Inheritance`).

| 전략 | 표가 몇 개 | 성질 |
| --- | --- | --- |
| `SINGLE_TABLE` | 하나 | 자식 필드가 전부 한 표에, 안 쓰는 칸은 `null` |
| `JOINED` | 부모 + 자식마다 | 정규화되지만 조회에 조인이 붙는다 |
| `TABLE_PER_CLASS` | 자식마다 | 부모로 조회하기가 까다롭다 |

공통 필드를 모으는 것과 상속을 표현하는 것은 목적이 다르다는 갈림이 여기서 분명해진다. **`BaseTime` 은 "부모"가 아니라 "필드 묶음"** 이라 표를 가질 이유가 없다.

### 3-6. 다음에 볼 키워드

- `@Embedded`·`@Embeddable` — 필드 몇 개를 값 타입으로 묶기 (상속과 다른 방향의 공통화)
- `@Temporal`·`@Enumerated` — 예전 날짜 타입과 열거형을 컬럼에 담기
- `@Table(uniqueConstraints=…)`·`@Index` — 여러 컬럼에 걸친 제약과 인덱스
- `AuditorAware`·시큐리티의 인증 정보와 감사 사람 축 잇기
- Flyway·Liquibase — 표 변경 이력 관리
- `@Version` 과 비관적 락(`@Lock`)의 갈림
- 하이버네이트 네이밍 전략 빈 갈아 끼우기
- 연관관계 매핑(`@ManyToOne`·`@OneToMany`)과 지연 로딩

## 실습 파일

- `2026B_Spring/springweb/src/main/resources/application.properties` (표를 SQL이 아니라 엔티티로 만들게 두기 — `ddl-auto` 다섯 값의 갈림과 `create-drop` 이 뜰 때 만들고 내려갈 때 지우는 성질·엔티티를 고쳐 가며 표 모양을 확인하는 자리에 어울리는 대신 데이터가 날아가므로 실습용 DB를 따로 두는 배치, `show-sql`·`format_sql` 이 켜져 있으면 하이버네이트가 만든 `create table` 문이 그대로 찍혀 `@Column` 을 고친 결과를 눈으로 확인할 수 있는 통로, 연동할 DB 이름이 실습마다 갈리는 배치)
- `2026B_Spring/springweb/src/main/java/day05/TestEntity.java` (컬럼의 제약을 자바 쪽에 적기 — `@Column` 여섯 속성(`name`·`nullable`·`length`·`unique`·`columnDefinition`·`insertable`/`updatable`)이 각각 `create table` 문의 어느 자리로 가는지와 앞의 넷은 표를 만들 때·뒤의 둘은 JPA가 SQL을 만들 때 쓰인다는 갈림, `length` 가 `String` 에만 걸리고 숫자 타입에는 무시되는 점과 DB에만 남던 길이 제한을 코드로 끌어오는 자리, 애노테이션이 바로 뒤에 오는 선언 하나에만 붙는다는 규칙과 표시가 여러 개 쌓여도 전부 같은 하나에 붙는 점·붙인 결과를 짐작하지 않고 생성된 DDL로 확인하는 습관, `columnDefinition` 이 컬럼 정의 자리에 들어갈 SQL을 통째로 적는 속성이라 `default`·`comment`·DB 고유 타입처럼 전용 속성이 없는 것을 적을 수 있는 대신 DB를 갈아 끼우면 그 자리만 깨지는 뒷면·다른 속성과 같이 적으면 이쪽이 이기는 점·기본값은 DB가 채우는 것이라 방금 저장한 자바 객체의 필드는 여전히 `null` 인 자리)
- `2026B_Spring/springweb/src/main/java/day05/BaseTime.java` (되풀이되는 필드를 위로 올리기 — 만든 시각·고친 시각이 어느 표에나 들어가므로 표마다 적지 않고 공통 클래스로 모으는 배치와 `BaseDao` 때와 같은 모양의 문제라는 정리, `@MappedSuperclass` 가 "표가 아니라 물려줄 필드 묶음"이라는 선언인 점과 `@Entity` 를 상속하는 갈래와의 대비(부모가 표를 갖는가·부모로 조회할 수 있는가)·`extends` 를 걸어야 필드가 내려오고 표시는 스스로 아무 일도 하지 않는다는 재확인, `@Getter` 만 두고 `@Setter` 를 두지 않는 이유(사람이 넣는 자리가 아니라 프레임워크가 채우는 자리), `@EntityListeners(AuditingEntityListener.class)` 로 값을 채워 줄 구현체를 붙이기와 JPA의 생명주기 콜백 자리에 리스너가 끼어드는 구조·공통 클래스에 붙여 두면 물려받은 엔티티 전부에 함께 붙는 값어치, `@CreatedDate` 는 처음 한 번·`@LastModifiedDate` 는 저장과 수정마다 채워지는 갈림과 처음 저장 때 둘 다 채워져 두 값을 견주면 수정 여부를 알 수 있는 부수 효과, 감사 표시가 `jakarta.persistence` 가 아니라 `org.springframework.data.annotation` 에서 오는 점과 JPA 규격·하이버네이트·스프링 데이터 세 층이 패키지 이름에 드러나는 자리, `LocalDateTime` 과 `LocalDate`·`LocalTime` 의 갈림·`java.util.Date` 를 대신하는 `java.time` 을 고르는 이유·`Local` 이 시간대를 안 들고 있다는 뜻과 지역이 갈리기 시작하면 걸리는 자리)
- `2026B_Spring/springweb/src/main/java/day04/practice2/AppStart.java` · `2026B_Spring/springweb/src/main/java/day05/AppStart.java` (감사 기능을 켜는 한 줄 — `@Enable…` 계열이 기능 한 벌에 필요한 빈을 한 번에 등록하는 표시라는 점과 이름이 곧 켜는 기능인 자리, 감사가 도는 데 필요한 세 자리(필드의 표시·엔티티의 리스너·진입점의 활성화)와 하나라도 빠지면 값이 `null` 로 남는 점·시각이 안 채워질 때 이 셋을 위에서부터 훑어 보는 순서, 활성화가 애플리케이션 하나 단위라 실습마다 진입점이 갈려 있으면 감사를 쓰는 쪽에 붙어 있어야 하는 자리와 컴포넌트 스캔 범위 이야기의 반복)

- `2026B_Spring/springweb/src/main/java/day05/practice/MovieEntity.java` · `day05/practice/BaseTime.java` · `day05/practice/AppStart.java` (같은 구조를 새 도메인에 옮겨 보기 — 실습 묶음을 패키지로 갈라 진입점·공통 클래스·엔티티 세 벌을 다시 두는 배치와 패키지가 다르면 같은 이름도 서로 다른 클래스인 점·`@EnableJpaAuditing` 이 애플리케이션 하나 단위라 그 묶음의 진입점에 붙어야 하는 재확인, 필드마다 `@Column` 을 붙일지 말지 고르는 판단(`nullable = false` 로 필수 값·`length` 로 `varchar` 줄이기·제약이 필요 없으면 표시를 안 붙이고 기본값에 맡기기), `@Table` 을 이름 없이 붙였을 때 클래스 이름이 표 이름의 근거가 되는 점과 카멜→스네이크 변환이 표 이름·컬럼 이름 양쪽에 걸리는 자리·표 이름을 따로 두려면 `name` 을 적어야 하는 갈림, 개봉일은 날짜만 필요하므로 `LocalDate` 를 고르는 판단과 담을 것에 맞춰 세 날짜 타입 중 하나를 고르는 기준·소수점이 붙는 값에 `Double` 을 쓰는 자리)
- `2026B_Spring/springweb/src/main/resources/sql/practice3.sql` · `springweb/src/main/resources/application.properties` (실습마다 DB와 시드를 갈라 두기 — 연동할 DB와 넣을 시드가 짝을 이뤄 바뀌는 배치와 `create-drop` 이라 뜰 때마다 표가 새로 만들어지므로 시드도 매번 다시 들어가야 하는 이유, `defer-datasource-initialization=true` 가 시드 SQL을 표 생성 뒤로 미루는 한 줄이고 없으면 넣을 표를 못 찾는 점, `sql.init.mode` 의 기본값이 `embedded` 라 MySQL에서는 그냥 넘어가므로 시드가 안 들어갈 때 먼저 보는 자리·`data-locations` 의 `classpath:` 가 `resources/` 를 가리키는 점·한글 시드에 필요한 `encoding=UTF-8`, 시드 SQL의 컬럼 이름이 엔티티와 네이밍 전략으로 만들어진 실제 표와 맞아야 하는 점과 문자열은 홑따옴표·큰따옴표는 식별자 자리라는 표준 SQL 쪽 구분)

## 관련 노트

[[Spring MOC]] · [[Spring day04 JPA 엔티티와 리포지토리]] · [[Spring day05 DTO 변환과 초기 데이터 적재]] · [[KDT_2026 학습 지도]]
