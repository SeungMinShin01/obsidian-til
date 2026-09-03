---
출처: Claude 분석
원본: KDT_2026/2026B_Spring/springweb/src/main/java/day05/TestDto.java, springweb/src/main/java/day05/TestEntity.java, springweb/src/main/resources/sql/0903.sql, springweb/src/main/resources/application.properties
작성일: 2026-09-03
tags: [학습, java]
---

# Spring day05 — DTO 변환과 초기 데이터 적재

> 실습 파일: `2026B_Spring/springweb/src/main/java/day05/TestDto.java`, `TestEntity.java`, `springweb/src/main/resources/sql/0903.sql`, `springweb/src/main/resources/application.properties`
> 허브: [[Spring MOC]] · 이전: [[Spring day05 엔티티 제약과 감사 필드]] · 다음: [[Spring day05 조회 흐름에 DTO 얹기]]

[[Spring day05 엔티티 제약과 감사 필드]] 에서 엔티티가 표의 설계도가 되고, 공통 필드가 위로 올라갔다. 표 모양은 이걸로 정해졌다. 남은 것은 **그 표를 다루는 객체가 계층 밖으로 나갈 때 무엇으로 바뀌는가**다.

두 갈래를 이번에 잡는다.

```
① 엔티티 ↔ DTO      계층을 넘을 때 갈아입는 옷 — 빌더로 조립하고 변환 메소드로 오간다
② 서버가 뜰 때 INSERT  표만 만들어진 빈 DB에 확인용 데이터를 자동으로 채워 넣는다
```

| 자리 | 하는 일 |
| --- | --- |
| `TestEntity` 의 롬복 표시 한 벌 | 엔티티를 빌더로 조립할 수 있게 열기 (1-1) |
| `TestDto` | 계층을 넘어 다니는 객체 (1-2) |
| `@Builder` 와 `builder()…build()` | 이름으로 값을 넣어 객체 만들기 (1-3) |
| `toEntity()` · `from()` | 두 방향의 변환 메소드 (1-4·1-5) |
| `toEntity()` 와 `from()` 의 `static`·`this` | 방향이 메소드 모양을 정하는 자리 (1-6) |
| `spring.sql.init.*` | 뜰 때 SQL 파일을 실행하기 (1-8) |

## 1. 배운 내용

### 1-1. 엔티티를 빌더로 조립할 수 있게 열기

엔티티에 표시가 한 벌 더 붙었고, 상속이 걸렸다.

```java
@Entity
@Table(name = "test")
@NoArgsConstructor
@AllArgsConstructor
@Builder
@Getter
@Setter
@ToString
public class TestEntity extends BaseTime {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Integer no;
    ...
}
```

`extends BaseTime` 이 걸리면서 [[Spring day05 엔티티 제약과 감사 필드]] 의 `@MappedSuperclass` 가 실제로 쓰이는 자리가 생겼다. **표시를 붙여 둔 것만으로는 아무 일도 일어나지 않고, 상속을 걸어야 `create_date`·`update_date` 컬럼이 이 표에 붙는다.**

롬복 표시 넷이 함께 붙는 이유가 서로 물려 있다.

| 표시 | 왜 필요한가 |
| --- | --- |
| `@NoArgsConstructor` | JPA가 빈 객체를 먼저 만들어야 한다 |
| `@AllArgsConstructor` | `@Builder` 가 안에서 전체 생성자를 쓴다 |
| `@Builder` | 이름으로 값을 넣어 조립하는 통로 |
| `@Getter` | 변환 메소드가 값을 꺼내는 통로 |

**`@Builder` 만 붙이면 기본 생성자가 사라진다.** 자바는 생성자를 하나도 안 적었을 때만 기본 생성자를 넣어 주는데, `@Builder` 가 전체 생성자를 만들어 버리므로 그 조건이 깨진다. JPA는 조회해 온 줄을 객체로 되돌릴 때 빈 객체부터 만들기 때문에, 셋을 짝으로 붙여 두는 것이 관용이 된다.

```
@Builder 만       →  전체 생성자만 남는다  →  JPA가 객체를 못 만든다
셋을 함께 붙임    →  빈 생성자 + 전체 생성자 + 빌더  →  양쪽 다 통한다
```

### 1-2. DTO — 계층을 넘어 다니는 객체

새 파일이 하나 늘었다.

```java
@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
@Setter
@Getter
@ToString
public class TestDto {
    // 서로 계층간 이동객체 ( Controller에서는 엔티티 사용금지 )
    private Integer no;
    private String name;
    private String descri;
    private Integer price;
    private LocalDateTime createDate;
    private LocalDateTime updateTime;
    ...
}
```

[[Spring day04 JPA 엔티티와 리포지토리]] 에서 "엔티티를 그대로 주고받으면 표의 모양이 곧 응답의 모양이 된다"를 문제로 적어 뒀다. **이번에 그 문제를 실제로 갈라 두는 자리다.**

두 클래스가 서 있는 자리가 다르다.

| | 엔티티 | DTO |
| --- | --- | --- |
| 무엇을 나타내나 | DB 표의 한 줄 | 계층 사이를 오가는 값 한 벌 |
| 누가 관리하나 | 영속성 컨텍스트가 상태를 추적한다 | 그냥 객체 |
| 모양이 바뀌는 이유 | 표가 바뀔 때 | 화면·API가 바뀔 때 |
| 사는 범위 | Service·Repository 안 | Controller 바깥까지 |

**바뀌는 이유가 다른 것을 한 클래스에 담지 않는 것**이 요점이다. 표에 컬럼 하나를 더하면 엔티티는 당연히 바뀌어야 하는데, 그 변화가 API 응답까지 그대로 새어 나가면 표를 손볼 때마다 화면이 흔들린다.

주석에 적힌 "Controller에서는 엔티티 사용금지"가 그 경계선이다. 컨트롤러가 다루는 타입은 DTO뿐이고, 엔티티는 서비스 안쪽에서만 산다.

```
Controller  ──DTO──▶  Service  ──Entity──▶  Repository  ──▶  DB
Controller  ◀──DTO──  Service  ◀──Entity──  Repository  ◀──
```

필드 구성을 보면 엔티티와 거의 같은데, **감사 필드 둘이 더 있다.** 엔티티에서는 `BaseTime` 으로 올라가 있던 값이라 `TestEntity` 안에는 안 보이는데, DTO는 상속을 쓰지 않고 자기 필드로 직접 들고 있다. 나가는 쪽에서는 그 값이 어디서 왔는지가 아니라 "응답에 실릴 키가 무엇인가"만 중요하기 때문이다.

주석의 "기능별로 DTO 구성 — 등록DTO, 조회DTO, 수정DTO"는 이 클래스를 더 쪼개는 방향을 가리킨다(2-1).

### 1-3. 빌더 패턴 — 이름으로 값을 넣기

DTO 안의 변환 메소드가 둘 다 빌더로 객체를 만든다.

```java
return TestEntity.builder()      // ① static 메소드로 빌더를 얻고
        .name(this.name)         // ② 이름을 부르며 값을 넣고
        .descri(this.descri)
        .price(this.price)
        .build();                // ③ 마지막에 객체가 만들어진다
```

생성자와 견주면 갈리는 지점이 셋이다.

| | 생성자 | 빌더 |
| --- | --- | --- |
| 값의 순서 | 정해진 순서대로 | 상관없다 |
| 일부만 넣기 | 생성자를 따로 만들어야 | 안 부르면 그만 |
| 코드에 남는 것 | 값만 (`new TestEntity(1, "코카콜라", …)`) | 이름과 값 |

**필드가 늘어날수록 갈림이 커진다.** 생성자로 여섯 개를 넘기면 위치로만 구분되는 값이 여섯 줄 늘어서는데, 같은 타입이 이웃해 있으면 자리를 바꿔 넣어도 컴파일이 통과한다. 빌더는 값마다 이름이 붙어 있어 그 자리가 없다.

`builder()` 가 `static` 인 것이 순서상 당연하다. **객체를 만들려고 부르는 메소드라 아직 객체가 없다.** 클래스 이름으로 바로 부른다.

메소드 체이닝이 이어지는 원리는 각 메소드가 빌더 자신을 돌려주기 때문이다. 마지막 `build()` 만 완성된 객체를 돌려준다.

```
TestEntity.builder()  →  빌더 객체
    .name("코카콜라")  →  같은 빌더 객체
    .price(1000)      →  같은 빌더 객체
    .build()          →  TestEntity 객체
```

약점도 분명하다. **값을 빠뜨려도 컴파일이 막지 않는다.** 생성자는 인자 개수가 안 맞으면 그 자리에서 걸리는데, 빌더는 안 부른 필드가 조용히 `null` 로 남는다. 필수 값이 있는 객체라면 그 검사를 따로 만들어 둬야 한다.

### 1-4. DTO → 엔티티 — toEntity()

변환 메소드가 두 방향으로 하나씩 있다. 먼저 들어오는 쪽이다.

```java
public TestEntity toEntity() {
    return TestEntity.builder()
            .name(this.name)
            .descri(this.descri)
            .price(this.price)
            .build();
}
```

컨트롤러가 받은 DTO를 서비스가 엔티티로 바꿔 리포지토리에 넘길 때 쓴다. `this` 로 자기 필드를 꺼내므로 **인스턴스 메소드**다 — 바꿀 대상이 이미 자기 자신이라 밖에서 받을 것이 없다.

옮기는 필드가 셋뿐인 것이 눈에 띈다. `no`·`createDate`·`updateTime` 은 빠져 있다.

| 필드 | 왜 안 옮기나 |
| --- | --- |
| `no` | DB가 `AUTO_INCREMENT` 로 채운다 |
| `createDate`·`updateDate` | 감사 리스너가 채운다 |

**밖에서 온 값으로 채우면 안 되는 필드를 변환 자리에서 걸러 내는 것**이다. 요청 본문에 `no` 가 실려 오더라도 여기서 안 옮기면 엔티티에는 안 들어가고, PK가 비어 있으니 `save` 가 `insert` 로 갈린다([[Spring day04 JPA 엔티티와 리포지토리]] 의 기준). 변환 메소드가 경계 검사를 겸하는 자리다.

시각 필드도 마찬가지다. 요청이 보낸 시각을 그대로 쓰면 감사 기록이 아니게 되므로, 옮기지 않고 리스너에게 맡긴다.

### 1-5. 엔티티 → DTO — from()

나가는 쪽은 모양이 조금 다르다.

```java
public static TestDto from(TestEntity testEntity) {
    return TestDto.builder()
            .name(testEntity.getName())
            .descri(testEntity.getDescri())
            .price(testEntity.getPrice())
            .createDate(testEntity.getCreateDate())
            .updateTime(testEntity.getUpdateDate())
            .build();
}
```

**`static` 이고 매개변수를 받는다.** 방향을 생각하면 그럴 수밖에 없다. 만들려는 것이 DTO인데 아직 DTO가 없으므로, 클래스 이름으로 부르고 재료를 인자로 받는다.

| | `toEntity()` | `from()` |
| --- | --- | --- |
| 방향 | DTO → 엔티티 | 엔티티 → DTO |
| `static` | 아니다 | 그렇다 |
| 재료를 어디서 | `this` | 매개변수 |
| 부르는 자리 | 들어올 때 (C→S) | 나갈 때 (S→C) |

이렇게 이름 없이 `new` 를 부르지 않고 정적 메소드로 객체를 만드는 것을 **정적 팩토리 메소드**라 부른다. `from`·`of`·`valueOf` 같은 이름이 관용으로 쓰인다(3-1).

이쪽에는 감사 필드가 실려 나간다. `BaseTime` 에 있는 값이라 `TestEntity` 안에는 안 보이는데 **상속으로 내려온 `getCreateDate()` 는 그대로 부를 수 있다.** `@Getter` 를 `BaseTime` 에 붙여 둔 것이 여기서 쓰인다.

변환 메소드를 **DTO 쪽에 두는 배치**가 이번 선택이다. 엔티티가 DTO를 몰라도 되므로 의존 방향이 한쪽으로만 흐른다.

```
DTO  ──알고 있다──▶  Entity
DTO  ◀──모른다────   Entity
```

엔티티가 DTO를 알기 시작하면 응답 모양이 바뀔 때마다 엔티티를 손대게 되므로, 갈라 둔 값어치가 줄어든다.

### 1-6. static과 this — 두 메소드가 갈린 이유

한 클래스 안에 나란히 있는 두 변환 메소드가 한쪽은 `static` 이고 한쪽은 아니다. 취향으로 갈린 것이 아니라 **만들려는 것이 무엇인가**가 정한 결과다.

```java
public TestEntity toEntity() { … }                        // static 아님
public static TestDto from(TestEntity testEntity) { … }   // static
```

#### `static` 이 붙으면 무엇이 달라지나

`static` 은 **그 멤버가 객체가 아니라 클래스에 붙는다**는 표시다. 클래스가 메모리에 올라올 때 한 번 자리를 잡고, 객체를 몇 개 만들든 그 하나를 같이 쓴다.

| | 인스턴스 메소드 | `static` 메소드 |
| --- | --- | --- |
| 누구에게 붙나 | 객체 하나하나 | 클래스 |
| 부르는 법 | `dto.toEntity()` | `TestDto.from(entity)` |
| 부르기 전 필요한 것 | 객체가 있어야 한다 | 없어도 된다 |
| `this` | 쓸 수 있다 | 쓸 수 없다 |

마지막 줄이 핵심이다. **`static` 메소드 안에서는 `this` 를 못 쓴다.** 문법으로 막아 둔 것이 아니라, 애초에 가리킬 대상이 없다. 객체 없이도 불릴 수 있는 메소드라 "지금 이 객체"라는 것이 존재하지 않는 순간이 있기 때문이다.

```
dto.toEntity()          →  부르는 순간 dto 라는 객체가 있다        →  this = dto
TestDto.from(entity)    →  부르는 순간 TestDto 객체는 하나도 없다  →  this 가 가리킬 것이 없다
```

#### `this` 는 무엇을 가리키나

`this` 는 **지금 이 메소드를 부른 그 객체 자신**이다. 메소드가 실행될 때 자바가 몰래 넘겨 주는 값이라고 보면 이해가 빠르다.

```java
// 적는 모양
dto.toEntity();

// 실제로 일어나는 일에 가깝게 풀면
toEntity(dto);   // ← 이 dto 가 메소드 안에서 this 가 된다
```

`toEntity()` 안의 `this.name` 이 값을 꺼낼 수 있는 근거가 이것이다. 바꿀 대상이 이미 자기 자신이라 **밖에서 받을 것이 없다.**

```java
public TestEntity toEntity() {
    return TestEntity.builder()
            .name(this.name)      // this = 이 메소드를 부른 그 DTO
            .descri(this.descri)
            .price(this.price)
            .build();
}
```

`this.` 를 생략하고 `name` 이라고만 적어도 같은 값이 나온다. 자바가 지역변수부터 찾고 없으면 자기 필드를 찾기 때문이다. **적어 두면 "이건 매개변수가 아니라 내 필드"라는 것이 눈에 남으므로**, 변환 메소드처럼 양쪽 값이 섞이는 자리에서는 적어 두는 편이 읽기에 낫다.

#### 그래서 왜 방향마다 갈리나

두 메소드를 "부르는 순간 무엇이 이미 있고 무엇을 만들려는가"로 놓고 보면 갈림이 하나로 정리된다.

| | `toEntity()` | `from()` |
| --- | --- | --- |
| 부를 때 이미 있는 것 | DTO | 엔티티 |
| 만들려는 것 | 엔티티 | DTO |
| 만들려는 타입의 객체가 있나 | — (DTO는 있다) | 없다 |
| 그래서 | 있는 DTO에 붙여 `this` 로 꺼낸다 | 클래스에 붙이고 재료를 인자로 받는다 |

**`from()` 을 인스턴스 메소드로 만들 수가 없다.** 그러려면 `TestDto` 객체가 이미 있어야 하는데, 지금 만들려는 것이 바로 그 `TestDto` 다. 빈 DTO를 하나 만들어 놓고 `빈dto.from(entity)` 라고 부르는 모양이 되어 앞뒤가 맞지 않는다.

거꾸로 `toEntity()` 를 `static` 으로 만들 수는 있다. 다만 그러면 재료를 인자로 받아야 한다.

```java
// 지금 방식
dto.toEntity();

// static 으로 만들면
TestDto.toEntity(dto);   // 어차피 dto 를 넘겨야 한다
```

이미 손에 든 객체를 굳이 인자로 다시 넘기는 모양이라, 있는 것을 쓰는 쪽이 짧고 자연스럽다.

#### 한 줄로 남기면

```
만들려는 타입의 객체가 이미 있다   →  인스턴스 메소드,  재료는 this
만들려는 타입의 객체가 아직 없다   →  static 메소드,   재료는 매개변수
```

`static` 메소드가 객체 없이 불린다는 성질은 이미 여러 자리에서 만났다. [[Spring day03 애노테이션과 리플렉션]] 의 싱글톤 `getInstance()` 도, 빌더의 `builder()` 도 같은 이유로 `static` 이었다 — 셋 다 **객체를 얻거나 만들려고 부르는 메소드라 그 시점에 객체가 없다.**

| 메소드 | 부르는 모양 | `static` 인 이유 |
| --- | --- | --- |
| `getInstance()` | `Singleton.getInstance()` | 객체를 얻으려고 부른다 |
| `builder()` | `TestEntity.builder()` | 객체를 만들려고 부른다 |
| `from()` | `TestDto.from(entity)` | 객체를 만들려고 부른다 |
| `main()` | JVM이 부른다 | 프로그램 시작 시점엔 객체가 없다 |

`main` 이 언제나 `static` 인 것도 같은 사정이다. 실행을 시작하는 자리라 아직 아무 객체도 만들어지지 않았다.

### 1-7. 표시가 겹쳐 붙어 있는 자리

DTO에 `@Data` 와 `@Setter`·`@Getter`·`@ToString` 이 함께 붙어 있다. [[Spring day03 애노테이션과 리플렉션]] 에서 정리한 대로 `@Data` 는 묶음 표시라 그 안에 이미 셋이 들어 있다.

```
@Data  =  @Getter + @Setter + @ToString + @EqualsAndHashCode + @RequiredArgsConstructor
```

겹쳐 붙어도 같은 메소드가 두 벌 생기지는 않는다. **롬복이 이미 있는 메소드는 만들지 않는다.** 다만 코드를 읽는 쪽에서는 무엇이 왜 붙어 있는지가 흐려지므로, 묶음 하나로 두든지 개별 표시로만 적든지 한쪽으로 정리해 두는 편이 읽기에 낫다.

엔티티 쪽에 `@Data` 가 아니라 개별 표시가 붙어 있는 것도 이유가 있다. [[Spring day04 JPA 엔티티와 리포지토리]] 에 적어 둔 대로 `@Data` 가 데려오는 `@EqualsAndHashCode` 는 엔티티에서 걸리는 자리가 있다 — 값이 바뀌면 다른 객체로 판정되기 때문이다.

### 1-8. 서버가 뜰 때 데이터 채워 넣기

설정 파일에 세 줄이 늘었다.

```properties
# 5. 서버 실행될 때 data.sql (경로) 파일 실행 , classpath(resources폴더):
spring.sql.init.data-locations=classpath:/sql/0903.sql
spring.jpa.defer-datasource-initialization=true
spring.sql.init.mode=always
```

[[Spring day05 엔티티 제약과 감사 필드]] 에서 `ddl-auto=create-drop` 을 골라 뒀다. 뜰 때마다 표가 새로 만들어지므로 **DB가 매번 비어 있다.** 확인할 데이터를 손으로 넣으면 서버를 다시 띄울 때마다 그 일을 되풀이하게 된다. 그 되풀이를 없애는 자리다.

| 설정 | 뜻 |
| --- | --- |
| `spring.sql.init.data-locations` | 실행할 SQL 파일의 위치 |
| `spring.sql.init.mode` | 언제 실행할지 (`always`·`embedded`·`never`) |
| `spring.jpa.defer-datasource-initialization` | JPA가 표를 다 만든 뒤로 미룰지 |

세 번째 줄이 이번의 요점이다. **순서 문제**를 푼다.

```
기본 순서    SQL 초기화  →  JPA가 표 만들기      →  아직 표가 없는데 INSERT를 한다
defer=true   JPA가 표 만들기  →  SQL 초기화       →  표가 있는 상태에서 INSERT
```

원래 스프링은 SQL 초기화를 먼저 하도록 잡혀 있다. 표를 SQL로 직접 만들어 두는 배치를 전제로 한 순서다. 그런데 이번처럼 **표를 엔티티가 만들면 그 순서가 뒤집혀야** 한다. `defer-datasource-initialization=true` 가 그 한 줄이다.

`mode` 는 세 값이다.

| 값 | 언제 실행 |
| --- | --- |
| `embedded` | 내장 DB(H2 등)일 때만 — 기본값 |
| `always` | 언제나 |
| `never` | 실행 안 함 |

기본값이 `embedded` 라 **MySQL을 붙인 상태에서는 아무 일도 안 일어난다.** `always` 를 적어야 실제 DB에도 실행된다. 뒤집어 말하면, 실수로 이 값이 켜진 채 운영 DB를 가리키면 뜰 때마다 같은 INSERT가 나간다는 뜻이기도 하다.

`classpath:` 접두사는 [[Spring day04 REST 컨트롤러 CRUD 골격]] 에서 정리한 `src/main/resources` 가 빌드하면 클래스패스 루트가 되는 규칙 그대로다. 파일 시스템 경로가 아니라 **빌드된 결과물 안에서의 경로**라, 실행 환경이 달라져도 같은 문자열로 찾힌다.

### 1-9. 확인용 INSERT와 컬럼 이름

실행되는 SQL 파일이다.

```sql
# day05 /TestEntity SAMPLE

INSERT INTO test(name, descri, price, create_date , update_date )
    VALUES('코카콜라', '맛있는 탄산음료1', 1000, NOW(), NOW()),
    ('사이다', '맛있는 탄산음료2', 1000, NOW(), NOW()),
    ('환타', '맛있는 탄산음료3', 1000, NOW(), NOW());
```

두 가지가 확인된다.

**첫째, 컬럼 이름이 스네이크다.** 자바 필드는 `createDate`·`updateDate` 인데 표에서는 `create_date`·`update_date` 다. [[Spring day05 엔티티 제약과 감사 필드]] 에서 정리한 하이버네이트 기본 네이밍 전략이 실제로 그렇게 만들었다는 것을, 이 SQL이 붙는다는 사실 자체가 확인해 준다. **엔티티가 만든 표에 SQL을 직접 적을 때는 변환 결과를 기준으로 적어야 한다.**

**둘째, 감사 필드에 `NOW()` 를 직접 넣는다.** 감사 리스너는 JPA를 거쳐 저장될 때 끼어드는데, 이 INSERT는 SQL로 바로 나가므로 **리스너를 거치지 않는다.** 값을 안 넣으면 `not null` 이 아니어도 `null` 로 남아 조회 결과가 비어 보인다. 자동으로 채워지는 통로와 직접 적는 통로가 갈리는 자리다.

`no` 를 안 적은 것은 `AUTO_INCREMENT` 가 채우기 때문이고, 여러 줄을 괄호로 이어 한 문장에 넣는 것은 `VALUES` 뒤에 쉼표로 나열하는 다중 행 INSERT 표기다.

### 1-10. 정리 — 이번에 붙은 두 갈래

```
① 계층 경계        Controller는 DTO만 · Entity는 Service 안쪽
   변환 자리        toEntity()  들어올 때 걸러 내기
                    from()      나갈 때 필요한 것만 싣기
   조립 방법        빌더 — 이름으로 값을 넣기

② 확인 데이터      뜰 때 SQL 파일 실행
   순서 조정        defer=true 로 표 생성 뒤로 미루기
   실행 조건        mode=always 로 실제 DB에도 켜기
```

앞의 갈래는 **바뀌는 이유가 다른 것을 갈라 두는** 이야기고, 뒤의 갈래는 **되풀이되는 손일을 설정으로 옮기는** 이야기다. 방향은 지금까지와 같다.

## 2. 추가로 알면 좋은 활용법

### 2-1. DTO를 기능별로 쪼개기

DTO 하나로 등록·조회·수정을 다 받으면, 요청에 따라 안 쓰는 필드가 생긴다.

| DTO | 담는 것 |
| --- | --- |
| 등록용 | `name`·`descri`·`price` (PK·시각 없음) |
| 수정용 | `no` + 바꿀 필드 |
| 응답용 | 전부 + 감사 필드 |

**하나로 두면 "이 요청에 무엇이 필요한가"가 코드에 안 남는다.** 등록에 `no` 를 실어 보내도 받아지고, 응답 전용 필드가 요청 DTO에도 있어 밖에서 채워 보낼 수 있다.

쪼개면 클래스가 늘어나는 대신 각 자리가 무엇을 받고 무엇을 내보내는지가 서명에 드러난다. 내부 클래스로 묶어 두는 배치도 자주 쓰인다.

```java
public class TestDto {
    public static class Create { … }
    public static class Update { … }
    public static class Response { … }
}
```

### 2-2. 빌더에 기본값 두기 — @Builder.Default

빌더로 만들면 필드 초기값이 무시된다.

```java
@Builder.Default
private Integer price = 0;
```

필드에 `= 0` 을 적어 둬도 **빌더가 안 부른 필드를 타입 기본값(`null`·`0`)으로 두기 때문**이다. 표시를 붙여야 초기값이 살아난다. 표시가 없으면 롬복이 경고를 띄우므로, 초기값을 적을 때는 짝으로 붙여 두는 편이 안전하다.

### 2-3. 필수 값을 빌더에서 지키기

빌더의 약점(1-3)을 다루는 갈래가 몇 가지다.

| 방법 | 언제 걸리나 |
| --- | --- |
| `build()` 안에서 검사 | 실행할 때 |
| `@NonNull` | 값을 넣을 때 |
| `@Valid` + `@NotNull` | 컨트롤러 경계에서 |
| 필수 값만 생성자로, 선택 값만 빌더로 | 컴파일할 때 |

경계에서 막을수록 안쪽 코드가 단순해진다. **요청으로 들어오는 값은 `@Valid` 로 컨트롤러에서 거르고, 안쪽에서 조립하는 객체는 `@NonNull` 로 두는** 배치가 무난하다.

### 2-4. 변환을 어디에 둘지

변환 메소드를 두는 자리가 세 갈래다.

| 자리 | 모양 | 갈림 |
| --- | --- | --- |
| DTO 안 (이번) | `dto.toEntity()`·`TestDto.from(e)` | 파일이 안 늘고 의존이 한 방향 |
| 별도 Mapper 클래스 | `mapper.toEntity(dto)` | DTO가 엔티티를 몰라도 된다 |
| MapStruct 등 자동 생성 | 인터페이스만 적는다 | 필드가 많을 때 손일이 준다 |

필드가 늘어날수록 변환 메소드의 줄 수가 그대로 늘어난다. 필드 열 개짜리 DTO 세 종류면 변환 코드만 수십 줄이 된다. 그 지점이 자동 생성 도구를 보게 되는 자리다(3-2).

### 2-5. 변환 없이 조회 결과를 바로 DTO로 받기

리포지토리가 엔티티 대신 DTO를 바로 돌려주게 할 수도 있다.

```java
@Query("select new day05.TestDto(t.no, t.name, t.price) from TestEntity t")
List<TestDto> findAllDto();
```

인터페이스만 적어 두는 방법(프로젝션)도 있다.

```java
public interface TestSummary {
    String getName();
    Integer getPrice();
}
```

**필요한 컬럼만 `select` 하므로 조회량이 준다.** 엔티티를 통째로 읽어 와 일부만 옮겨 담는 낭비가 없어진다. 대신 영속성 컨텍스트가 관리하지 않는 객체라 더티 체킹은 안 걸린다 — 읽기 전용 화면에 어울리는 갈래다.

### 2-6. schema.sql과 data.sql

`spring.sql.init` 은 두 종류의 파일을 다룬다.

| 파일 | 하는 일 | 기본 경로 |
| --- | --- | --- |
| `schema.sql` | 표 만들기 | `classpath:schema.sql` |
| `data.sql` | 데이터 넣기 | `classpath:data.sql` |

이름을 그대로 두면 경로를 안 적어도 찾아 실행한다. 이번처럼 파일 이름을 날짜로 두면 `data-locations` 로 지목해야 한다. 여러 파일을 쉼표로 나열할 수도 있다.

**`schema.sql` 을 쓰기 시작하면 `ddl-auto` 를 `none`·`validate` 로 내리는 것이 짝이다.** 표를 만드는 쪽이 둘이 되면 어느 쪽이 이겼는지가 헷갈린다.

### 2-7. 초기화가 안 먹힐 때 보는 순서

데이터가 안 들어가 있으면 훑어 볼 자리가 정해져 있다.

```
① mode 가 always 인가       (기본값 embedded 면 MySQL에는 안 나간다)
② defer 가 true 인가         (표가 만들어지기 전에 INSERT가 나갔을 수 있다)
③ 경로가 맞는가              (classpath 기준, 빌드 결과물에 파일이 들어갔는가)
④ SQL 자체가 도는가          (컬럼 이름이 실제 표와 맞는가)
```

**로그에 나가는 SQL이 찍히므로**(`show-sql`) 어디까지 갔는지를 눈으로 따라갈 수 있다. `create table` 은 있는데 `insert` 가 없으면 ①·②, 둘 다 있는데 오류가 나면 ④ 쪽이다.

### 2-8. 확인용 데이터를 코드로 넣기

SQL 파일 말고 자바 코드로 넣는 갈래도 있다.

```java
@Bean
CommandLineRunner init(TestRepository repository) {
    return args -> repository.save(
        TestEntity.builder().name("코카콜라").price(1000).build()
    );
}
```

**JPA를 거치므로 감사 리스너가 돌아 시각이 자동으로 채워진다.** 1-9에서 `NOW()` 를 직접 적어야 했던 자리가 없어진다. 대신 SQL 파일보다 적는 양이 늘고, 이미 들어 있는지 확인하는 코드를 따로 둬야 한다.

| | SQL 파일 | `CommandLineRunner` |
| --- | --- | --- |
| 감사 필드 | 직접 적는다 | 자동으로 채워진다 |
| 적는 양 | 짧다 | 길다 |
| 중복 방지 | 표를 지우고 다시 만드는 전제 | 코드로 확인해야 |

### 2-9. 응답에서 필드 빼기

DTO를 갈라 두지 않은 상태라도, 나가는 JSON에서만 필드를 빼는 방법이 있다.

```java
@JsonIgnore
private String password;
```

`null` 인 필드를 아예 안 내보내는 설정도 있다.

```java
@JsonInclude(JsonInclude.Include.NON_NULL)
public class TestDto { … }
```

다만 이것들은 **나가는 모양만 손보는 것**이라, 들어오는 쪽까지 막지는 않는다. 요청 DTO와 응답 DTO를 갈라 두는 편이 근본에 가깝다.

## 3. 더 나아가 알면 좋은 것

### 3-1. 정적 팩토리 메소드의 이름 관용

`from` 이라는 이름이 아무렇게나 붙은 것이 아니다. 자바 표준 라이브러리에서 굳어진 관용이 있다.

| 이름 | 쓰는 자리 | 예 |
| --- | --- | --- |
| `from` | 하나를 받아 타입을 바꿀 때 | `Date.from(instant)` |
| `of` | 여러 개를 받아 모을 때 | `List.of(a, b, c)` |
| `valueOf` | 값을 그대로 옮길 때 | `Integer.valueOf("10")` |
| `getInstance` | 있으면 주고 없으면 만들 때 | 싱글톤 창구 |
| `newInstance` | 매번 새로 만들 때 | 리플렉션 |

**`new` 대신 정적 메소드를 쓰면 이름으로 의도를 남길 수 있다.** 생성자는 클래스 이름으로 고정돼 있어 같은 매개변수 조합을 두 가지 뜻으로 쓸 수 없는데, 정적 메소드는 이름이 갈리므로 가능하다.

`getInstance` 는 [[Spring day03 애노테이션과 리플렉션]] 의 싱글톤에서, `newInstance` 는 리플렉션에서 이미 나왔다. 같은 갈래의 이름 규칙이었다는 정리가 여기서 붙는다.

### 3-2. 변환 코드를 생성으로 대신하기 — MapStruct

필드가 많아지면 변환 메소드가 사실상 같은 줄의 되풀이가 된다. 그 자리를 애노테이션 프로세서가 대신할 수 있다.

```java
@Mapper
public interface TestMapper {
    TestEntity toEntity(TestDto dto);
    TestDto toDto(TestEntity entity);
}
```

**인터페이스만 적으면 구현 클래스가 컴파일 시점에 생성된다.** 롬복과 같은 갈래(애노테이션 프로세서)라 실행 중 부담이 없고, 이름이 안 맞는 필드는 컴파일할 때 걸린다.

리플렉션으로 실행 중에 옮기는 도구(ModelMapper)도 있는데, 이쪽은 적는 양이 더 줄지만 필드 이름이 어긋나도 실행할 때까지 모른다. [[Spring day03 애노테이션과 리플렉션]] 에서 정리한 "컴파일 시점 생성 vs 실행 시점 리플렉션"의 갈림이 여기서도 그대로다.

### 3-3. record로 DTO 적기

자바 16부터 값만 담는 클래스를 짧게 적을 수 있다.

```java
public record TestDto(Integer no, String name, String descri, Integer price) {}
```

생성자·getter·`equals`·`hashCode`·`toString` 이 자동으로 생긴다. 롬복 없이도 되고, **필드를 바꿀 수 없다(불변)**는 것이 큰 갈림이다.

| | 클래스 + 롬복 | record |
| --- | --- | --- |
| 값 변경 | `@Setter` 로 열 수 있다 | 못 한다 |
| 기본 생성자 | 만들 수 있다 | 없다 |
| 상속 | 된다 | 안 된다 |

기본 생성자가 없어서 **엔티티로는 못 쓰고**, 폼 바인딩처럼 빈 객체를 만든 뒤 setter로 채우는 통로와도 안 맞는다. `@RequestBody` 로 받는 응답·요청 DTO에는 잘 맞는 편이다.

### 3-4. 순환 참조와 JSON

연관관계를 매핑하기 시작하면(`@OneToMany`·`@ManyToOne`) 엔티티끼리 서로를 가리키게 된다. 그 상태로 엔티티를 JSON으로 내보내면 **A가 B를 부르고 B가 다시 A를 부르며 끝나지 않는다.**

| 대응 | 방식 |
| --- | --- |
| `@JsonIgnore` | 한쪽 방향을 끊는다 |
| `@JsonManagedReference`·`@JsonBackReference` | 주·종을 지정한다 |
| DTO로 변환 | 애초에 엔티티를 안 내보낸다 |

세 번째가 이번에 잡아 둔 배치다. **DTO를 거치면 순환 자체가 안 생긴다** — 응답에 실을 것만 골라 담기 때문이다. 연관관계로 넘어가면 DTO 변환의 값어치가 한 겹 더 붙는 자리다.

`@ToString` 도 같은 문제를 겪는다. 엔티티에 붙여 두고 연관을 걸면 로그를 찍을 때 순환한다.

### 3-5. 지연 로딩과 변환 시점

연관관계는 기본적으로 필요할 때 읽어 오는데(지연 로딩), **트랜잭션이 끝난 뒤에 그 필드를 건드리면 예외가 난다.**

```
Service (트랜잭션 안)  →  엔티티 반환
Controller (밖)        →  entity.getItems()  →  세션이 닫혀 못 읽는다
```

**변환을 서비스 안에서 끝내 두면 이 문제가 안 생긴다.** DTO는 이미 값이 복사된 객체라 트랜잭션과 상관없다. 계층 경계에서 DTO로 바꾸는 배치가 순환 참조 말고도 이 자리에서 값어치를 낸다.

### 3-6. 실습 데이터를 격리하기 — Testcontainers

`create-drop` 과 초기화 SQL 조합은 실습에는 편한데, 여러 사람이 같은 DB를 보면 서로의 데이터를 지운다. 테스트 코드에서는 **DB 자체를 매번 새로 띄우는** 방식이 쓰인다.

```
테스트 시작  →  도커로 MySQL 컨테이너 띄우기  →  표 만들고 데이터 넣기
테스트 끝    →  컨테이너 버리기
```

실제 DB와 같은 엔진으로 검사하면서도 격리되므로, 내장 DB(H2)로 검사할 때 생기는 "H2에서는 되는데 MySQL에서는 안 되는" 자리를 줄인다.

### 3-7. 다음에 볼 키워드

- `@Valid`·`@NotBlank`·`@Size` — DTO에 값 검사 붙이기
- `@RestControllerAdvice` — 변환·검증 실패를 한 자리에서 응답으로 만들기
- `Page`·`Pageable` — 목록 DTO에 쪽 나누기 얹기
- `@Query` 와 JPQL 생성자 표현식·인터페이스 프로젝션
- MapStruct·ModelMapper — 변환 자동화 두 갈래
- record와 `@RequestBody` 의 조합
- `@OneToMany`·`@ManyToOne` 과 지연 로딩·N+1
- Flyway·Liquibase — 초기 데이터와 스키마 이력 관리
- `CommandLineRunner`·`ApplicationRunner` — 뜰 때 코드 실행하기

## 실습 파일

- `2026B_Spring/springweb/src/main/java/day05/TestEntity.java` (엔티티를 빌더로 조립할 수 있게 열기 — `extends BaseTime` 이 걸리면서 `@MappedSuperclass` 로 올려 둔 필드가 실제로 이 표에 붙는 자리와 표시만으로는 아무 일도 안 일어난다는 재확인, 롬복 표시 넷(`@NoArgsConstructor`·`@AllArgsConstructor`·`@Builder`·`@Getter`)이 서로 물려 있는 이유와 `@Builder` 만 붙이면 전체 생성자가 생겨 기본 생성자가 사라지고 JPA가 조회 결과를 객체로 못 되돌리는 자리·셋을 짝으로 붙이는 관용, 엔티티에 `@Data` 대신 개별 표시를 쓰는 이유와 `@EqualsAndHashCode` 가 엔티티에서 걸리는 지점)
- `2026B_Spring/springweb/src/main/java/day05/TestDto.java` (계층을 넘어 다니는 객체 — 엔티티를 그대로 주고받을 때 표의 모양이 곧 응답의 모양이 되던 문제를 실제로 갈라 두는 자리와 두 클래스가 서 있는 자리의 대비(무엇을 나타내나·누가 관리하나·바뀌는 이유·사는 범위)·"Controller에서는 엔티티 사용금지"라는 경계선과 엔티티가 서비스 안쪽에서만 사는 배치, DTO가 감사 필드를 상속이 아니라 자기 필드로 들고 있는 이유(나가는 쪽에서는 값의 출처가 아니라 응답에 실릴 키가 중요하다), **빌더 패턴** — `builder()…build()` 체이닝이 각 메소드가 빌더 자신을 돌려주기 때문에 이어지는 원리와 `builder()` 가 `static` 일 수밖에 없는 순서·생성자와 갈리는 세 지점(순서 무관·일부만 넣기·값에 이름이 남는 것)·필드가 늘수록 위치로만 구분되는 값이 늘어나는 문제를 없애는 자리·값을 빠뜨려도 컴파일이 막지 않는 약점, **`toEntity()`** — `this` 로 자기 필드를 꺼내는 인스턴스 메소드이고 `no`·시각 필드를 안 옮겨 밖에서 온 값으로 채우면 안 되는 필드를 변환 자리에서 걸러 내는 구조·PK가 비어 있어 `save` 가 `insert` 로 갈리는 기준과 이어지는 자리, **`from()`** — 만들려는 것이 DTO라 `static` 이고 재료를 매개변수로 받는 방향의 필연성과 두 메소드를 `static` 여부·재료의 출처·부르는 자리로 갈라 보기·정적 팩토리 메소드라는 이름·상속으로 내려온 `getCreateDate()` 를 그대로 부를 수 있는 자리와 `BaseTime` 의 `@Getter` 가 쓰이는 지점·변환 메소드를 DTO 쪽에 둬 의존이 한 방향으로만 흐르게 하는 배치, `@Data` 와 개별 표시가 겹쳐 붙어도 메소드가 두 벌 생기지 않는 점과 한쪽으로 정리해 두는 편이 읽기 나은 이유)
- `2026B_Spring/springweb/src/main/resources/application.properties` (서버가 뜰 때 데이터 채워 넣기 — `ddl-auto=create-drop` 이라 뜰 때마다 DB가 비어 있어 확인 데이터를 손으로 넣는 되풀이가 생기는 자리와 그것을 설정으로 옮기기, `spring.sql.init.data-locations`·`mode`·`spring.jpa.defer-datasource-initialization` 세 줄의 역할, **순서 문제** — 기본 순서가 SQL 초기화 먼저라 표가 만들어지기 전에 INSERT가 나가고 `defer=true` 가 그 순서를 뒤집는 자리·표를 SQL로 만드는 배치를 전제한 기본값과 엔티티가 표를 만드는 배치의 갈림, `mode` 세 값과 기본값 `embedded` 라 MySQL에는 아무 일도 안 일어나는 점·`always` 를 켠 채 운영 DB를 가리키면 뜰 때마다 같은 INSERT가 나가는 뒷면, `classpath:` 가 파일 시스템 경로가 아니라 빌드 결과물 안에서의 경로라 실행 환경이 달라져도 같은 문자열로 찾히는 자리)
- `2026B_Spring/springweb/src/main/resources/sql/0903.sql` (확인용 INSERT와 컬럼 이름 — 자바 필드가 카멜인데 표 컬럼이 스네이크라 SQL을 직접 적을 때는 하이버네이트 네이밍 전략의 변환 결과를 기준으로 적어야 하는 점과 이 SQL이 붙는다는 사실 자체가 그 변환을 확인해 주는 자리, 감사 필드에 `NOW()` 를 직접 넣는 이유(SQL로 바로 나가는 INSERT는 JPA를 거치지 않아 감사 리스너가 안 돈다)와 자동으로 채워지는 통로·직접 적는 통로가 갈리는 자리, `no` 를 안 적는 것과 `AUTO_INCREMENT` 의 짝·`VALUES` 뒤에 쉼표로 여러 줄을 잇는 다중 행 INSERT 표기)

## 관련 노트

[[Spring MOC]] · [[Spring day05 엔티티 제약과 감사 필드]] · [[Spring day05 조회 흐름에 DTO 얹기]] · [[KDT_2026 학습 지도]]
