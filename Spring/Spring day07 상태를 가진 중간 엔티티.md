---
출처: Claude 분석
원본: KDT_2026/2026B_Spring/springweb/src/main/java/day07/practice, springweb/src/main/resources/sql/practice4.sql, springweb/src/main/resources/application.properties
작성일: 2026-09-07
tags: [학습, java]
---

# Spring day07 — 상태를 가진 중간 엔티티

> 실습 파일: `2026B_Spring/springweb/src/main/java/day07/practice/CourseEntity.java`, `day07/practice/StudentEntity.java`, `day07/practice/EnrollEntity.java`, `day07/practice/BaseTime.java`, `day07/practice/AppStart.java`, `resources/sql/practice4.sql`, `resources/application.properties`
> 허브: [[Spring MOC]] · 이전: [[Spring day06 중간 엔티티로 푼 다대다]]

앞에서 메뉴와 재료의 다대다를 레시피 표 하나로 갈라 풀었다. 그때 중간 표에 `recipe_order` 같은 속성 하나가 붙을 수 있다는 것까지는 적어 뒀는데, 그 속성은 어디까지나 "레시피에 딸린 부가 정보"였다. **이번 실습4는 중간 표에 붙은 속성이 그 관계의 본체인 도메인이다.**

수강신청을 세어 보면 관계는 앞과 같은 모양이다.

| 물음 | 답 |
| --- | --- |
| 한 과정에 학생이 몇 명 등록하나 | 여러 명 |
| 한 학생이 몇 개 과정을 듣나 | 여러 개 |

양쪽 다 "여러"라 중간 표가 필요하다. 그런데 여기서 진짜로 알고 싶은 것은 "누가 무엇을 듣는가"만이 아니라 **"그 수강이 지금 어떤 상태인가"** 다. 수강중인지, 수료했는지, 중도포기했는지. 그 값이 들어갈 자리는 과정 표도 학생 표도 아니고 둘을 잇는 표뿐이다.

## 1. 배운 내용

### 1-1. 관계 자체가 담을 것을 갖는 도메인

표 셋을 늘어놓으면 이렇다.

```
course ──1:N──▶ enroll ◀──N:1── student
                 status
                 course_id  student_id
```

`enroll` 한 줄이 뜻하는 것은 "학생 하나가 과정 하나를 신청했다"라는 **사실 한 건**이다. 그 사실에 `status` 가 딸린다.

| 표 | 담는 것 |
| --- | --- |
| `course` | 과정 자체의 정보 (과정명) |
| `student` | 학생 자체의 정보 (이름) |
| `enroll` | 둘을 이었다는 사실 + 그 사실의 상태 |

앞 노트에서 "관계에 속성이 붙으면 그것은 이미 하나의 사실이라 표를 차지할 자격이 있다"라고 정리했다. **여기서는 그 문장의 순서가 뒤집힌다** — 속성이 나중에 붙은 것이 아니라, 상태를 담고 싶어서 표를 두게 된 쪽에 가깝다. 관계에 담을 것이 처음부터 있으면 `@ManyToMany` 는 아예 후보에 오르지 않는다.

### 1-2. 상태를 나타내는 컬럼 하나

시드에 들어가는 값은 이런 모양이다.

```sql
INSERT INTO enroll (status, course_id, student_id, created_at, updated_at)
VALUES ('수강중', 1, 1, NOW(), NOW());
```

`status` 는 `enroll` 표에만 있고, 과정을 바꾸거나 학생을 바꾸는 일 없이 이 값만 바뀐다. 상태 값을 어디에 두느냐로 갈라 보면 자리가 분명해진다.

| 두는 자리 | 되는가 |
| --- | --- |
| `student.status` | 안 된다 — 과정마다 상태가 다르다 |
| `course.status` | 안 된다 — 학생마다 상태가 다르다 |
| `enroll.status` | 된다 — 학생 하나와 과정 하나가 만나는 자리 |

상태는 학생의 성질도 과정의 성질도 아니고 **둘이 만난 자리의 성질**이다. 어느 표에 컬럼을 둘지 헷갈릴 때 "이 값이 무엇 하나가 바뀌면 따라 바뀌나"를 물어보면 자리가 정해진다.

### 1-3. 공통 시각 필드를 실습 묶음마다 다시 두기

`day07/practice` 안에 `BaseTime` 이 다시 하나 있다.

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

Spring day05 엔티티 제약과 감사 필드 에서 정리한 세 자리(필드의 표시 · 엔티티의 리스너 · 진입점의 활성화)가 그대로다. 패키지가 다르면 같은 이름이라도 서로 다른 클래스이므로, 실습 묶음을 새로 열 때마다 이 클래스를 그 패키지에 한 벌 두게 된다.

눈여겨볼 곳은 **필드 이름이 곧 컬럼 이름을 정한다**는 점이다.

```
createdAt  → created_at
updatedAt  → updated_at
```

하이버네이트 기본 네이밍 전략이 카멜을 스네이크로 바꾸므로, 시드 SQL에 적는 컬럼 이름도 그 변환 결과를 따라간다. 공통 클래스의 필드 이름을 바꾸면 그것을 물려받은 **모든 표의 컬럼 이름이 한꺼번에 바뀌고**, 시드 SQL도 전부 같이 봐야 한다. 위로 올린 필드는 위로 올린 만큼 영향 범위도 넓다.

### 1-4. "일" 쪽에서 목록을 여는 표시 한 벌

과정 쪽에서 수강 목록을 들려면 앞에서 굳어진 세 표시가 그대로 온다.

```java
@OneToMany(mappedBy = "…", cascade = CascadeType.ALL, fetch = FetchType.LAZY)
@ToString.Exclude
@Builder.Default
private List<EnrollEntity> enrollEntity = new ArrayList<>();
```

| 표시 | 막는 것 |
| --- | --- |
| `mappedBy` | 외래키를 양쪽이 관리하려 들어 중간 표가 하나 더 생기는 일 |
| `@ToString.Exclude` | 서로의 `toString()` 을 왕복하다 스택이 넘치는 일 |
| `@Builder.Default` | 빌더가 초기값을 무시해 목록이 `null` 로 남는 일 |

여기서 새로 붙는 것은 `cascade` 와 `fetch` 두 속성이다.

- `cascade = CascadeType.ALL` — 과정에 걸린 동작(저장·삭제 등)을 목록의 수강 줄에도 함께 흘려보낸다
- `fetch = FetchType.LAZY` — 목록을 실제로 건드릴 때까지 조회를 미룬다. `@OneToMany` 는 원래 기본이 `LAZY` 라 적어 두는 쪽이 뜻을 드러내는 표기에 가깝다

`mappedBy` 에 적는 값은 표 이름도 컬럼 이름도 아니고 **상대 엔티티에 실제로 있는 필드 이름**이다. 문자열이라 컴파일은 지나가고 서버가 뜰 때 걸리므로, 양쪽 파일을 나란히 열어 이름을 맞춰 두는 것이 확인 순서다. 어느 상대인지는 문자열이 아니라 목록의 제네릭 타입이 정한다는 점도 그대로다.

### 1-5. 껍데기를 먼저 두고 아래층부터 채우기

실습4의 진행 순서는 앞 실습과 같다. 엔티티 파일 자리를 먼저 만들어 두고, 표 모양이 정해지는 쪽부터 채워 올린다.

```
day07/practice/
├── AppStart.java       진입점 (@SpringBootApplication + 감사 활성화)
├── BaseTime.java       공통 시각 필드
├── CourseEntity.java   과정
├── StudentEntity.java  학생
└── EnrollEntity.java   수강 (중간 + 상태)
```

관계를 양쪽에서 걸어야 짝이 성립하므로, 한쪽만 채워 둔 동안은 서버를 띄워도 짝이 안 맞는 상태다. **양쪽을 함께 채우고 나서 한 번 띄워 `create table` 문을 확인하는 것**이 표시를 붙인 결과를 짐작하지 않는 방법이다.

### 1-6. 실습마다 DB와 시드를 갈라 두기

설정에서 바뀌는 줄은 둘뿐이다.

```properties
spring.datasource.url = jdbc:mysql://localhost:3306/mydb0907
spring.sql.init.data-locations=classpath:/sql/practice4.sql
```

```properties
spring.jpa.hibernate.ddl-auto=create-drop
spring.jpa.defer-datasource-initialization=true
spring.sql.init.mode=always
spring.sql.init.encoding=UTF-8
```

네 줄의 조합이 만드는 흐름은 앞과 같다 — 뜰 때마다 엔티티 기준으로 표를 새로 만들고(`create-drop`), 시드를 표 생성 뒤로 미루고(`defer`), MySQL에도 시드가 나가게 하고(`mode=always`), 한글 시드의 글자가 안 깨지게 읽는다(`encoding`). 실습이 늘 때 손대는 것은 **붙일 DB 주소와 시드 파일 경로 둘뿐**이라, 이 네 줄은 한 번 맞춰 두면 그대로 간다.

시드 안에서 지켜야 할 순서도 그대로다.

```sql
-- 1. 과정  → 2. 학생  → 3. 수강
```

`enroll` 은 `course_id`·`student_id` 두 외래키를 들고 있어 **부모 두 쪽이 먼저 들어가 있어야** 한다. 부모끼리는 순서가 상관없고 자식만 뒤에 오면 된다. 감사 컬럼에 `NOW()` 를 직접 적는 이유도 같다 — SQL로 바로 나가는 INSERT는 JPA를 거치지 않아 감사 리스너가 돌지 않는다.

접속 정보는 설정 파일에 그대로 들어가는 값이라, 실습용 로컬 계정이라도 파일이 밖으로 나가는 경로(공개 저장소 등)에 그대로 실리지 않게 두는 편이 안전하다.

## 2. 추가로 알면 좋은 활용법

### 2-1. 상태 값을 문자열로 둘 때와 열거형으로 둘 때

지금은 `'수강중'` 이라는 문자열이 그대로 들어간다. 값이 몇 가지로 정해져 있으면 자바 쪽에서 열거형으로 좁힐 수 있다.

```java
public enum EnrollStatus { 수강중, 수료, 중도포기 }

@Enumerated(EnumType.STRING)
private EnrollStatus status;
```

| 방식 | 성질 |
| --- | --- |
| `String` | 아무 값이나 들어간다. 오타가 데이터로 남는다 |
| `@Enumerated(EnumType.STRING)` | 정해진 값만. DB에는 이름 그대로 저장돼 눈으로 읽힌다 |
| `@Enumerated(EnumType.ORDINAL)` | 순번(0·1·2)으로 저장. 상수 순서를 바꾸면 기존 데이터의 뜻이 바뀐다 |

`ORDINAL` 은 저장 공간이 작은 대신 위험이 크다. 상수 하나를 가운데 끼워 넣는 순간 이미 쌓인 줄의 뜻이 밀린다. **문자열로 저장하는 쪽이 무난하다.**

### 2-2. 같은 신청이 두 번 들어가는 것 막기

한 학생이 같은 과정을 두 번 신청하는 줄은 도메인상 있으면 안 된다. 표 수준에서 막으려면 두 컬럼을 묶은 유니크 제약을 건다.

```java
@Table(name = "enroll",
       uniqueConstraints = @UniqueConstraint(columnNames = {"course_id", "student_id"}))
```

여기서 앞 노트의 대비가 되살아난다. 레시피 표는 같은 메뉴에 같은 재료가 순서만 달리해 두 번 들어갈 수 있어 이 제약을 못 걸었다. **수강은 같은 짝이 두 번 나오면 안 되는 관계**라 걸 수 있다. 같은 "중간 표"라도 도메인이 다르면 걸 수 있는 제약이 갈린다.

다만 재수강까지 생각하면 이야기가 또 달라진다. 같은 학생이 같은 과정을 다음 기수에 다시 들으면 그것은 별개의 사실이다. 그때는 기수·연도 같은 컬럼이 제약에 함께 들어가야 한다. **제약은 지금 데이터가 아니라 앞으로 들어올 데이터를 보고 정하는 편이 안전하다.**

### 2-3. `cascade` 를 어디까지 걸지

`CascadeType.ALL` 은 편한 만큼 넓다. 과정을 지우면 그 과정의 수강 줄이 전부 함께 지워진다.

| 값 | 함께 흘러가는 동작 |
| --- | --- |
| `PERSIST` | 저장 |
| `MERGE` | 병합 |
| `REMOVE` | 삭제 |
| `ALL` | 위 전부 |

기준은 하나로 잡을 수 있다 — **부모 없이는 존재할 이유가 없는 자식에만 건다.** 수강 줄은 과정이 사라지면 남아 있을 이유가 없으니 이 기준에 맞는다. 반대로 학생 쪽에서 `REMOVE` 를 흘려보내면 학생 하나를 지웠을 때 그 사람의 수강 기록이 통째로 사라지는데, 기록으로 남겨야 하는 값이라면 그 편이 곤란하다. **같은 중간 표라도 어느 부모에서 흘려보내느냐로 판단이 갈린다.**

`orphanRemoval = true` 는 한 걸음 더 간다. 부모의 목록에서 빼기만 해도 그 줄이 지워진다. 목록을 화면에서 그대로 편집해 저장하는 구조에서 쓰이는데, 목록을 잠깐 비우는 코드가 곧 삭제가 되므로 걸어 둔 자리를 기억해 둘 필요가 있다.

### 2-4. 상태를 바꾸는 통로를 좁히기

상태 값은 아무 때나 아무 값으로 바뀌면 안 되는 종류다. `@Setter` 로 열어 두면 바꾸는 자리가 코드 전체로 흩어진다. 이름 붙인 메소드로 통로를 좁히면 무엇을 하는 일인지가 이름에 남는다.

```java
public void 수료처리() {
    this.status = EnrollStatus.수료;
}
```

Spring day05 등록·수정 흐름과 변경 감지 에서 정리한 더티 체킹이 여기서도 그대로 돈다 — 영속 상태의 엔티티에서 이 메소드를 부르면 트랜잭션이 끝날 때 `status` 컬럼만 `update` 로 나간다. 부르는 자리에 `save` 가 없어도 된다.

## 3. 더 나아가 알면 좋은 것

### 3-1. 상태가 바뀌는 규칙을 어디에 적을지

상태 값이 셋만 돼도 "어느 상태에서 어느 상태로 갈 수 있나"라는 규칙이 생긴다. 중도포기한 수강을 수료로 바꿀 수 있는가 같은 물음이다. 규칙을 적는 자리는 몇 갈래가 있다.

| 자리 | 성질 |
| --- | --- |
| 컨트롤러 | 요청마다 흩어진다. 같은 규칙이 여러 번 적힌다 |
| 서비스 | 판정을 모아 두기 좋다. 지금 단계에서 무난한 자리 |
| 엔티티 (도메인 메소드) | 상태와 규칙이 한 클래스에 있어 어긋날 여지가 적다 |

상태 전이가 복잡해지면 상태 기계(state machine)로 규칙 자체를 표로 그려 두는 방식도 있다. 다만 상태가 셋인 동안에는 `if` 몇 줄이 더 읽기 쉽다. **도구를 먼저 들이지 않고 규칙이 늘어나는 것을 보고 옮기는 편이 낫다.**

### 3-2. 지금 상태만 둘 것인가 바뀐 이력을 남길 것인가

`enroll.status` 는 **지금 상태 하나**만 담는다. 언제 수강중이 되었고 언제 수료로 바뀌었는지는 `updated_at` 이 마지막으로 바뀐 시각만 알려 줄 뿐이다.

이력이 필요하면 방향은 둘이다.

- 상태 변경 기록 표를 따로 두고 바뀔 때마다 한 줄씩 쌓기 — 앞에서 재고를 입출고 기록의 합으로 보던 방식과 같은 발상
- 현재 상태 컬럼은 그대로 두고 기록 표를 곁들이기 — 조회는 빠르고 이력도 남지만 두 곳이 어긋날 여지가 생긴다

어느 쪽이든 **"지금 값"과 "지나온 값"은 서로 다른 물음**이고, 컬럼 하나로 둘을 다 답하게 두면 나중에 이력을 뒤늦게 복원할 방법이 없다는 점이 판단의 기준이 된다.

### 3-3. 다음에 볼 키워드

- `@Enumerated` 와 `AttributeConverter` — 열거형을 DB 값으로 바꾸는 두 갈래
- 복합 유니크 제약과 소프트 삭제가 부딪히는 자리 (지운 줄까지 세어 재신청이 막히는 문제)
- `@Where`·`@SQLRestriction` 으로 조회 조건을 엔티티에 붙여 두기
- 목록 조회에서 상태별 개수 세기 — `group by` 를 `@Query` 로 내리는 갈래와 자바에서 세는 갈래
- 중간 엔티티에 `@IdClass`·`@EmbeddedId` 로 복합키를 두는 갈래와 대리키를 두는 갈래의 손익
- 수강 목록을 화면에 낼 때의 N+1 — 과정 목록 한 번에 수강 줄 조회가 줄 수만큼 따라붙는 자리와 `join fetch`
- 상태 변경에 트랜잭션 경계를 어디까지 잡을지 — 여러 줄을 한꺼번에 수료 처리하는 경우
- 관계에 딸린 속성이 여럿으로 늘 때 중간 엔티티를 다시 쪼갤 기준

## 실습 파일

- `2026B_Spring/springweb/src/main/java/day07/practice/CourseEntity.java` (**"일" 쪽에서 수강 목록을 여는 자리** — `@OneToMany(mappedBy=…)`·`@ToString.Exclude`·`@Builder.Default` 세 표시 한 벌이 세 번째 도메인에서도 그대로 반복되는 확인과 `cascade`·`fetch` 두 속성이 더해지는 자리·`mappedBy` 가 상대 엔티티의 자바 필드 이름이라 양쪽을 함께 채워야 짝이 성립하는 점, `extends BaseTime` 으로 공통 시각 필드를 물려받는 자리와 관계 필드와 상속 필드가 서로 간섭하지 않는 점)
- `2026B_Spring/springweb/src/main/java/day07/practice/EnrollEntity.java` (**관계에 상태가 붙는 중간 엔티티** — 과정과 학생 사이의 다대다를 1:N 둘로 가르는 자리와 `status` 가 학생의 성질도 과정의 성질도 아닌 "둘이 만난 자리의 성질"이라 중간 표에만 놓일 수 있는 점·관계에 담을 것이 처음부터 있으면 `@ManyToMany` 가 후보에 오르지 않는 이유)
- `2026B_Spring/springweb/src/main/java/day07/practice/StudentEntity.java` (**반대편 "일" 쪽** — 같은 표시 한 벌이 과정 쪽과 대칭으로 오는 자리와 `cascade` 를 어느 부모에서 흘려보내느냐로 판단이 갈리는 점)
- `2026B_Spring/springweb/src/main/java/day07/practice/BaseTime.java` (**실습 묶음마다 공통 클래스를 한 벌 다시 두기** — `@MappedSuperclass`·`@EntityListeners`·`@CreatedDate`·`@LastModifiedDate` 네 표시의 배치가 그대로 오는 자리와 패키지가 다르면 같은 이름도 서로 다른 클래스인 점, 필드 이름이 카멜↔스네이크 변환을 거쳐 물려받은 모든 표의 컬럼 이름을 한꺼번에 정하는 자리)
- `2026B_Spring/springweb/src/main/java/day07/practice/AppStart.java` (**실습 묶음마다 진입점 하나** — 컴포넌트 스캔 범위가 진입점의 패키지 아래로 정해져 실습이 서로 독립된 앱이 되는 배치와 감사 활성화가 애플리케이션 하나 단위라 그 묶음의 진입점에 붙어야 하는 재확인)
- `2026B_Spring/springweb/src/main/resources/sql/practice4.sql` (**외래키가 둘인 표의 시드** — 과정·학생을 먼저 넣고 수강을 뒤에 두는 순서와 부모끼리는 순서가 상관없는 점, 감사 컬럼을 `NOW()` 로 직접 채우는 이유가 SQL로 바로 나가는 INSERT는 감사 리스너를 안 거치는 데 있다는 재확인·시드 컬럼 이름 `created_at`·`updated_at` 이 공통 클래스의 필드 이름에서 네이밍 전략을 거쳐 나온 결과라는 점)
- `2026B_Spring/springweb/src/main/resources/application.properties` (**실습이 늘 때 손대는 두 줄** — 붙일 DB 주소와 시드 경로만 갈아 끼우고 `ddl-auto=create-drop`·`defer-datasource-initialization`·`sql.init.mode=always`·`sql.init.encoding=UTF-8` 네 줄은 그대로 가는 배치, 접속 정보가 파일에 그대로 남는 성질과 밖으로 나가는 경로에 실리지 않게 두는 자리)

## 관련 노트

[[Spring MOC]] · [[Spring day06 중간 엔티티로 푼 다대다]] · [[KDT_2026 학습 지도]]
