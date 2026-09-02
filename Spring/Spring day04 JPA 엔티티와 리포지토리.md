---
출처: Claude 분석
원본: KDT_2026/2026B_Spring/springweb/src/main/java/day04/Exam, springweb/src/main/java/day04/practice2, springweb/src/main/java/day04/sample.sql, springweb/build.gradle
작성일: 2026-09-02
tags: [학습, java]
---

# Spring day04 — JPA 엔티티와 리포지토리

> 실습 파일: `2026B_Spring/springweb/src/main/java/day04/Exam/AppStart.java`, `ExamEntity.java`, `ExamRepository.java`, `ExamService.java`, `ExamController.java`, `day04/practice2/TestEntity.java`, `day04/sample.sql`, `springweb/build.gradle`
> 허브: [[Spring MOC]] · 이전: [[Spring day04 REST 컨트롤러 CRUD 골격]]

[[Spring day04 REST 컨트롤러 CRUD 골격]] 에서 되풀이를 줄이는 두 방향을 적어 뒀다. 공통을 위로 올리는 쪽(`BaseDao`)과 아예 코드를 쓰지 않고 규약으로 대신하는 쪽(JPA)이다. 이번 실습은 **뒤쪽 갈래를 실제로 밟아 보는 자리**다.

바뀌는 것이 두 가지다. 하나는 DB와 이야기하던 자리에서 **SQL이 사라진다.** 다른 하나는 컨트롤러와 DB 사이에 **Service 계층이 하나 끼어든다.**

```
지금까지   Controller  →  Dao (SQL을 손으로 적는다)
이번       Controller  →  Service  →  Repository (인터페이스만 적는다)
```

| 자리 | 하는 일 |
| --- | --- |
| `sample.sql` | 옮겨 담을 표를 먼저 만들어 두기 (1-1) |
| `ExamEntity` 의 `@Entity`·`@Table` | 표 하나를 자바 클래스에 짝지어 두기 (1-2) |
| `@Id`·`@GeneratedValue` | 어느 필드가 열쇠이고 누가 값을 채우는지 정하기 (1-3·1-4) |
| 엔티티에 붙은 롬복 표시 넷 | 값 그릇으로서의 통로를 열어 두기 (1-5) |
| `ExamRepository` 의 인터페이스 한 줄 | 구현을 적지 않고 규약만 남기기 (1-6·1-7) |
| `ExamService` | 컨트롤러와 DB 사이에 규칙을 담을 자리 두기 (1-9) |
| `final` + `@RequiredArgsConstructor` | 필요한 것을 만들지 않고 받기 (1-10) |
| `ExamController` | 엔티티를 그대로 주고받는 네 갈래 (1-11) |
| `build.gradle` 의 스타터 한 줄 | 이 전부를 켜는 선언 (1-12) |
| `board` 표와 `practice2` 패키지 | 표를 하나 더 두고 같은 벌을 다시 짜 보기 (1-14) |

## 1. 배운 내용

### 1-1. 옮겨 담을 표를 먼저 만들어 두기

`sample.sql` 에 표 하나가 있다.

```sql
DROP DATABASE if EXISTS mydb0902;
create DATABASE mydb0902;
use mydb0902;

create table exam(
    eno Int PRIMARY KEY AUTO_INCREMENT ,
    ename VARCHAR(255)
);
```

컬럼이 둘뿐이다. 번호와 이름 하나씩이라, 뒤에 나올 매핑을 눈으로 따라가기 좋은 크기다.

`AUTO_INCREMENT` 가 붙어 있는 것이 요점이다. 값을 넣을 때 번호를 적지 않으면 **DB가 다음 번호를 스스로 채운다.**

```sql
INSERT INTO exam( ename ) VALUES('유재석');
```

`ename` 만 넣었는데 `eno` 가 1, 2, 3으로 붙는다. 이 성질이 1-4의 `@GeneratedValue` 와 짝을 이룬다.

`application.properties` 의 `spring.datasource.url` 이 가리키는 DB 이름과 여기서 만든 이름이 같아야 붙는다. 설정 파일을 고쳤는데 연결이 안 되면 이 짝부터 보는 편이 빠르다.

### 1-2. 표 하나를 자바 클래스에 짝지어 두기 — @Entity와 @Table

DB의 표와 짝을 이루는 클래스를 만든다.

```java
@Entity                 // 엔티티 객체(빈) 등록
@Table(name = "exam")   // 매핑할 테이블 이름
public class ExamEntity {
    private Integer eno;
    private String ename;
}
```

두 표시의 역할이 갈린다.

| 표시 | 하는 일 |
| --- | --- |
| `@Entity` | 이 클래스를 **DB의 표와 짝지어 관리하겠다**고 선언한다 |
| `@Table(name = "exam")` | 짝지을 표의 이름을 지목한다 |

`@Table` 은 생략할 수 있다. 없으면 **클래스 이름이 그대로 표 이름**이 된다. 클래스가 `ExamEntity` 면 `exam_entity` 나 `ExamEntity` 를 찾게 되는데, 실제로 만들어 둔 표는 `exam` 이라 이름이 어긋난다. 그래서 지목해 두는 편이 분명하다.

필드와 컬럼도 이름으로 짝을 맞춘다.

```
클래스 ExamEntity  ↔  테이블 exam
필드   eno         ↔  컬럼   eno
필드   ename       ↔  컬럼   ename
```

[[Spring day04 REST 컨트롤러 CRUD 골격]] 에서 DTO 필드 이름이 JSON 키가 되고 화면 코드의 이름이 되는 관통을 봤는데, 여기서 **DB 컬럼 쪽으로 한 칸 더 이어진다.** 이름 하나가 컬럼 → 필드 → JSON 키 → 화면까지 관통하는 모양이 된다.

DTO와 엔티티는 이름이 비슷해도 서 있는 자리가 다르다.

| | DTO | 엔티티 |
| --- | --- | --- |
| 짝을 이루는 것 | 오가는 값의 모양 | DB의 표 |
| 관리 주체 | 그냥 자바 객체 | JPA가 상태를 추적한다 |
| 없어도 되는가 | 화면과 맞추려고 둔다 | 표가 있으면 반드시 하나 |

엔티티는 "값을 담는 그릇"에 **"DB의 어느 줄인가"라는 정체성이 얹힌** 객체다. 이 차이가 뒤에서 저장·수정이 갈리는 근거가 된다.

### 1-3. 엔티티에는 열쇠가 반드시 하나 있다 — @Id

필드 하나에 `@Id` 가 붙는다.

```java
@Id
private Integer eno;
```

**엔티티는 PK를 하나 이상 반드시 갖는다.** 없으면 뜰 때 걸린다.

이유는 JPA가 하는 일에서 나온다. JPA는 객체 하나가 표의 어느 줄인지를 늘 알고 있어야 하는데, 그 줄을 가리키는 유일한 이름이 PK다. 같은 줄을 두 번 읽으면 같은 객체를 돌려주고, 값이 바뀌면 그 줄만 골라 고칠 수 있는 것도 열쇠가 있어서다.

```
객체 ExamEntity(eno=1)  ←→  exam 표의 eno=1 인 줄
```

DB 쪽에서 `PRIMARY KEY` 를 붙인 것과 자바 쪽에서 `@Id` 를 붙인 것이 같은 이야기를 양쪽에서 하는 셈이다. 한쪽만 있으면 짝이 맞지 않는다.

### 1-4. 번호를 누가 채우는가 — @GeneratedValue

`@Id` 아래에 표시가 하나 더 붙는다.

```java
@Id
@GeneratedValue(strategy = GenerationType.IDENTITY)
private Integer eno;
```

`@GeneratedValue` 는 **번호를 코드가 정하지 않고 맡긴다**는 선언이다. `strategy` 가 맡길 상대를 고른다.

| 전략 | 번호를 만드는 쪽 | 어울리는 DB |
| --- | --- | --- |
| `IDENTITY` | DB의 자동 증가 컬럼 | MySQL |
| `SEQUENCE` | DB의 시퀀스 객체 | Oracle·PostgreSQL |
| `TABLE` | 번호를 따로 저장하는 표 | 어디서나 (느리다) |
| `AUTO` | 구현체가 DB를 보고 고른다 | (기본값) |

`IDENTITY` 를 고른 것은 1-1의 `AUTO_INCREMENT` 와 짝을 맞추기 위해서다. 표 쪽이 이미 번호를 채우게 되어 있으니, 자바 쪽도 "내가 안 채운다"고 적어 두는 것이다.

```
저장할 때   eno = null 로 보낸다
DB         AUTO_INCREMENT 가 다음 번호를 채운다
돌아올 때   eno 에 채워진 번호가 들어 있다
```

여기서 [[Spring day04 REST 컨트롤러 CRUD 골격]] 에서 본 `Integer` 이야기가 다시 걸린다. `eno` 가 `int` 면 "아직 번호가 없다"를 담을 자리가 없어 0이 들어간다. **`null` 을 담을 수 있어야 "저장 전"과 "저장 후"가 갈린다.** 뒤에 나올 저장·수정 판정도 이 `null` 하나에 기댄다.

`AUTO` 는 편해 보이지만 구현체 버전에 따라 고르는 전략이 달라질 수 있다. 쓰는 DB가 정해져 있으면 지목해 두는 편이 안전하다.

### 1-5. 엔티티에 붙은 롬복 표시 넷

엔티티 위에도 롬복 표시가 붙는다.

```java
@Data
@AllArgsConstructor
@NoArgsConstructor
@Builder
public class ExamEntity { ... }
```

넷이 각각 다른 통로를 연다.

| 표시 | 열리는 통로 |
| --- | --- |
| `@Data` | getter·setter와 `toString`·`equals`·`hashCode` |
| `@NoArgsConstructor` | 매개변수 없는 생성자 |
| `@AllArgsConstructor` | 값을 다 채워 만드는 생성자 |
| `@Builder` | 이름을 적어 가며 조립하는 통로 |

`@NoArgsConstructor` 가 특히 빠지면 안 되는 자리다. **JPA는 DB에서 읽은 줄을 객체로 되돌릴 때 빈 객체를 먼저 만든 뒤 값을 채운다.** 규격 자체가 매개변수 없는 생성자를 요구한다.

[[Spring day04 REST 컨트롤러 CRUD 골격]] 의 DTO에서 본 사정과 같은 모양이다. 전체 생성자를 만들면 기본 생성자가 사라지므로 둘을 짝으로 붙여 둔다. `@Builder` 도 생성자를 하나 만드는 쪽이라, 함께 붙일 때 기본 생성자를 따로 적어 두는 것이 관용이 됐다.

`@Data` 를 엔티티에 붙이는 것은 편한 대신 딸려 오는 것이 있다. `equals`·`hashCode` 가 모든 필드로 만들어지고 `toString` 이 필드를 전부 찍는데, 엔티티는 연관이 얽히면 이 둘이 문제를 일으킬 여지가 있다. 2-6에서 이어서 본다.

### 1-6. 구현을 적지 않고 규약만 남기기 — JpaRepository

DB를 다루는 자리가 **인터페이스 하나**로 끝난다.

```java
@Repository
public interface ExamRepository
        extends JpaRepository<ExamEntity, Integer> {
}
```

몸통이 비어 있다. 그런데도 `findAll()`·`save()` 를 부를 수 있다.

`extends JpaRepository` 한 줄이 그 메소드들을 물려주기 때문이다. 제네릭 두 자리가 **무엇을 다루는지**를 적는 곳이다.

```
JpaRepository< 조작할 엔티티 , 그 엔티티의 PK 타입 >
JpaRepository< ExamEntity   , Integer            >
```

PK 타입이 `Integer` 인 것은 1-4에서 `eno` 를 `Integer` 로 둔 것과 짝을 맞춘 것이다. 여기가 어긋나면 뜰 때 걸린다.

구현체가 없는데 어떻게 도는가가 핵심이다. **스프링이 시작할 때 이 인터페이스를 찾아 구현 객체를 만들어 등록한다.** Spring day03 애노테이션과 리플렉션 에서 본 "표시를 읽어 동작을 만드는" 구조가 여기서는 인터페이스 자체를 읽는 쪽으로 간 셈이다.

```
인터페이스 선언  →  스프링이 읽는다  →  구현 객체를 만들어 빈으로 등록  →  주입받아 쓴다
```

지금까지 `BaseDao` 를 물려받고 `PreparedStatement` 에 `?` 를 채우던 자리가 통째로 사라진다. **적어야 하는 것이 "어떻게"에서 "무엇을"로 바뀌는 지점**이다. 이 발상 자체는 [[Repository Pattern]] 쪽에 정리해 둔 것과 같다 — 저장소를 인터페이스로 두고 그 뒤가 무엇인지는 쓰는 쪽이 모르게 하는 구조다.

`@Repository` 를 붙여 뒀는데, Spring Data가 이 인터페이스들을 스스로 찾아 등록하므로 없어도 동작한다. 붙여 두면 **읽는 사람에게 계층이 드러난다**는 값어치가 남는다.

### 1-7. 물려받은 메소드에 무엇이 있나

`JpaRepository` 하나로 딸려 오는 것이 적지 않다.

| 메소드 | 하는 일 | 대응하는 SQL |
| --- | --- | --- |
| `findAll()` | 전부 읽기 | `select * from exam` |
| `findById(1)` | 열쇠로 하나 읽기 | `select … where eno = 1` |
| `save(entity)` | 저장하거나 고치기 | `insert` 또는 `update` |
| `deleteById(1)` | 열쇠로 하나 지우기 | `delete … where eno = 1` |
| `count()` | 줄 수 세기 | `select count(*)` |
| `existsById(1)` | 있는지 확인 | `select … limit 1` |

[[개념 - CRUD]] 네 갈래가 이름만 바뀌어 그대로 있다. `BoardDao` 에 다섯 메소드를 손으로 적던 자리가 **상속 한 줄로 대체된다.**

이름 규칙이 눈에 띈다. `find`·`save`·`delete`·`count` 로 시작하고, 뒤에 조건이 붙는다. 이 규칙이 2-1에서 볼 "메소드 이름으로 쿼리 만들기"의 입구가 된다.

### 1-8. 표를 다루는 자리가 얼마나 줄었나

같은 일을 하는 코드를 견줘 보면 갈림이 분명하다.

| | 직접 JDBC | JPA 리포지토리 |
| --- | --- | --- |
| 연결 얻기 | `getConnection()` | (없음) |
| SQL 문자열 | 직접 적는다 | (없음) |
| 값 바인딩 | `setString(1, …)` | (없음) |
| 결과 훑기 | `while (rs.next())` | (없음) |
| DTO에 담기 | 컬럼마다 꺼내 `set` | (없음) |
| 자원 닫기 | `close()` | (없음) |
| 적는 것 | 위 전부 | 인터페이스 한 줄 |

빠진 것들이 사라진 것은 아니고 **구현체가 대신 한다.** 그래서 값어치와 뒷면이 같이 온다 — 코드가 짧아지는 대신 **무슨 SQL이 나가는지가 코드에 안 보인다.** 2-2에서 그 SQL을 눈으로 보는 방법을 정리한다.

### 1-9. 컨트롤러와 DB 사이에 계층 하나 — @Service

새 파일이 하나 늘었다.

```java
@Service
@RequiredArgsConstructor
public class ExamService {
    private final ExamRepository examRepository;

    public List<ExamEntity> findAll() {
        return examRepository.findAll();
    }

    public boolean save(ExamEntity entity) {
        ExamEntity saved = examRepository.save(entity);
        if (saved.getEno() >= 1) return true;
        return false;
    }
}
```

[[Spring day04 REST 컨트롤러 CRUD 골격]] 에서 "다음 단계"로 적어 둔 자리가 실제로 생겼다.

```
Controller  →  Service  →  Repository
  요청 받기     업무 규칙      DB
```

`findAll` 은 그냥 넘기기만 한다. 값어치가 드러나는 쪽은 `save` 다. **리포지토리가 돌려준 엔티티를 보고 `boolean` 으로 줄이는 판정**이 여기 들어 있다. 이 판정은 요청을 받는 일도 아니고 DB를 다루는 일도 아니라, 양쪽 어디에 둬도 어색한 코드다. 그것을 담을 자리가 Service다.

`@Service` 는 `@Component` 와 하는 일이 같다. 빈으로 등록된다는 결과는 같고, **이름이 계층을 말해 준다**는 것이 다르다. [[Spring day04 REST 컨트롤러 CRUD 골격]] 에서 정리한 `@Controller`·`@Service`·`@Repository` 셋의 갈림이 여기서 세 파일로 눈에 보이는 모양이 됐다.

뒤이어 삭제와 수정까지 붙어 네 갈래가 한 벌로 찼다.

```java
public boolean delete(int no) {
    examRepository.deleteById(no);
    return true;
}

public boolean update(ExamEntity entity) {
    Optional<ExamEntity> optional = examRepository.findById(entity.getEno());
    if (optional.isPresent()) {
        ExamEntity savedEntity = optional.get();
        savedEntity.setEname(entity.getEname());
        return true;
    }
    return false;
}
```

네 갈래가 리포지토리를 부르는 모양이 서로 다르다.

| 갈래 | 부르는 메소드 | 돌려받는 것 | 판정하는 방법 |
| --- | --- | --- | --- |
| 조회 | `findAll()` | `List<엔티티>` | (판정 없음) |
| 저장 | `save(entity)` | 영속된 엔티티 | 채워진 번호를 본다 |
| 삭제 | `deleteById(no)` | 없음(`void`) | 되돌려 받을 값이 없다 |
| 수정 | `findById(no)` | `Optional<엔티티>` | 들어 있는지 본다 |

삭제만 돌려받는 값이 없다. **성공·실패를 알려면 지운 뒤 `existsById` 로 다시 확인하거나, 지우기 전에 있는지 먼저 보는 수밖에 없다.** 없는 번호를 지우려 하면 예외가 나는 쪽이라, 앞에 확인 한 줄을 두는 배치가 흔하다.

### 1-9-1. 없을 수도 있는 결과를 감싸는 상자 — Optional

`findById` 만 돌려주는 타입이 다르다. `ExamEntity` 가 아니라 `Optional<ExamEntity>` 다.

```
findAll()   →  List<ExamEntity>       없으면 빈 목록
findById(9) →  Optional<ExamEntity>   없으면 빈 Optional
```

목록은 "없음"을 빈 목록으로 말할 수 있는데, **하나를 찾는 일은 "없음"을 말할 방법이 `null` 뿐**이었다. `null` 을 그대로 돌려주면 받는 쪽이 확인을 빠뜨렸을 때 그 자리가 아니라 한참 뒤에서 터진다.

`Optional` 은 그 자리를 **타입으로 옮긴다.** 값을 상자에 넣어 돌려주므로, 꺼내려면 열어 보는 절차를 거치게 된다.

| 하는 일 | 메소드 |
| --- | --- |
| 들어 있는지 보기 | `isPresent()` / `isEmpty()` |
| 꺼내기 | `get()` |
| 없으면 대신 쓸 값 | `orElse(기본값)` |
| 없으면 예외 던지기 | `orElseThrow()` |
| 있을 때만 실행 | `ifPresent(…)` |

`isPresent()` 로 갈라 `get()` 으로 꺼내는 모양이 가장 눈에 익는 형태다. 다만 `get()` 은 비어 있을 때 예외가 나므로 **`isPresent()` 확인 없이 부르면 `null` 검사를 빠뜨린 것과 다를 바가 없다.** 확인과 꺼내기가 붙어 있어야 값어치가 산다.

조회 결과가 없을 때 그냥 실패로 끝낼 것이면 `orElseThrow()` 한 줄이 더 짧다.

```java
ExamEntity saved = examRepository.findById(no)
        .orElseThrow(() -> new IllegalArgumentException("없는 번호"));
```

### 1-9-2. update SQL을 적지 않고 값만 바꾸기

수정이 특이하다. **`save` 를 다시 부르지 않고 setter 하나로 끝난다.**

```java
ExamEntity savedEntity = optional.get();
savedEntity.setEname(entity.getEname());
```

`update` 라는 이름의 메소드도, `save` 호출도 없는데 값이 바뀐다는 이야기다. 이것이 3-1에서 볼 **영속성 컨텍스트**의 성질이다.

```
findById 로 꺼낸 엔티티  →  관리 대상(영속 상태)이 된다
setter 로 값을 바꾼다    →  JPA가 처음 읽은 값과 견준다
트랜잭션이 끝난다        →  달라진 필드만 update SQL로 나간다
```

이 자동 감지를 **더티 체킹**이라 부른다. 조회해 온 객체는 그냥 값 그릇이 아니라 **DB의 그 줄과 이어져 있는 객체**라는 것이 요점이다. 1-2에서 DTO와 엔티티의 갈림으로 적어 둔 "상태가 추적되는 객체"가 실제로 도는 자리가 여기다.

그래서 기억해 둘 것이 하나 있다. **더티 체킹은 트랜잭션이 살아 있는 동안에만 성립한다.** 조회와 값 변경이 같은 트랜잭션 안에서 일어나야 끝날 때 `update` 가 나가고, 트랜잭션 밖에서 꺼낸 객체는 관리 대상에서 풀려 아무리 setter를 불러도 DB에 반영되지 않는다. 수정 메소드에 `@Transactional` 을 붙이는 관용이 여기서 온다(2-7).

새로 만든 객체에 번호를 채워 `save` 로 밀어 넣는 갈래도 있다.

| | 조회 후 setter (더티 체킹) | `save` 를 다시 부르기 |
| --- | --- | --- |
| 나가는 SQL | 바뀐 컬럼만 `update` | `select` 로 확인 뒤 `update` |
| 안 보낸 필드 | 원래 값이 남는다 | `null` 로 덮일 수 있다 |
| 필요한 조건 | 트랜잭션 안이어야 한다 | PK가 채워져 있어야 한다 |

**안 보낸 필드가 어떻게 되는가**가 갈림의 핵심이다. 필드가 둘일 때는 차이가 안 보이는데, 화면에서 일부만 고쳐 보내기 시작하면 벌어진다. 조회 후 setter 쪽이 부분 수정에 자연스럽다.

### 1-10. 만들지 않고 받기 — final과 @RequiredArgsConstructor

컨트롤러와 서비스가 필요한 것을 들고 있는 방식이 바뀌었다.

```java
@RestController
@RequiredArgsConstructor      // final 멤버변수 생성자 자동
public class ExamController {
    private final ExamService examService;
}
```

`new` 도 `getInstance()` 도 없다. **`final` 로 선언만 해 두면 컨테이너가 넣어 준다.**

도는 순서는 두 단계다.

```
컴파일 시점  @RequiredArgsConstructor 가 final 필드를 받는 생성자를 만든다
실행 시점    스프링이 그 생성자로 객체를 만들면서 빈을 찾아 넣는다
```

앞 단계가 Spring day03 애노테이션과 리플렉션 에서 본 애노테이션 프로세서, 뒤 단계가 IOC/DI다. **컴파일 시점 코드 생성과 실행 시점 주입이 맞물려** 한 줄로 보이는 자리다.

[[Spring day04 REST 컨트롤러 CRUD 골격]] 에서 DAO를 `getInstance()` 로 꺼내 오며 남겨 뒀던 결합도 문제가 여기서 풀린다.

| | `getInstance()` 로 꺼내 오기 | 생성자 주입 |
| --- | --- | --- |
| 만드는 주체 | 컨트롤러 | 컨테이너 |
| 코드에 박히는 것 | 구현 클래스 이름 | 필요한 타입 |
| 테스트할 때 | 진짜 구현이 붙는다 | 다른 것을 넣어 볼 수 있다 |

`final` 로 둘 수 있는 것도 값어치다. 한 번 받은 뒤 바뀌지 않는 것이 코드에 드러나고, 빠뜨리면 컴파일에서 걸린다.

컨트롤러가 리포지토리를 건너뛰고 부르지 않는 것도 눈에 띈다. **각 계층은 자기 바로 아래만 안다.** 층을 건너뛰기 시작하면 계층을 나눈 값어치가 흐려진다.

### 1-11. 엔티티를 그대로 주고받기

컨트롤러도 네 갈래가 찼다.

```java
@GetMapping("/day04/exam")
public List<ExamEntity> findAll() {
    return examService.findAll();
}

@PostMapping("/day04/exam")
public boolean save(@RequestBody ExamEntity entity) {
    return examService.save(entity);
}

@DeleteMapping("/day04/exam")
public boolean delete(@RequestParam(name = "no") int no) {
    return examService.delete(no);
}

@PutMapping("/day04/exam")
public boolean update(@RequestBody ExamEntity entity) {
    return examService.update(entity);
}
```

주소 하나에 방식 넷이 붙었다. **주소는 자원을 가리키고 방식이 무엇을 할지를 말한다**는 배치가 여기서 온전한 모양이 된다.

| 방식 | 주소 | 뜻 | 받는 방법 |
| --- | --- | --- | --- |
| `GET` | `/day04/exam` | 목록 읽기 | (받는 값 없음) |
| `POST` | `/day04/exam` | 새로 만들기 | `@RequestBody` |
| `DELETE` | `/day04/exam?no=3` | 지우기 | `@RequestParam` |
| `PUT` | `/day04/exam` | 통째로 고치기 | `@RequestBody` |

**받는 방법이 두 갈래로 갈린다.** 삭제만 `@RequestParam` 이고 나머지는 `@RequestBody` 다.

```
@RequestParam   주소 뒤 쿼리 문자열     ?no=3          값 하나
@RequestBody    요청 본문의 JSON        {"eno":3,…}    객체 한 벌
```

갈림의 기준은 **보낼 것이 값 하나인가 객체 한 벌인가**다. 삭제는 번호 하나면 끝나므로 본문을 실을 것이 없고, 저장·수정은 필드가 여럿이라 JSON으로 묶는 편이 낫다. `@RequestParam(name = "no")` 처럼 이름을 적어 두면 **주소에 실리는 이름과 매개변수 이름을 따로 둘 수 있다** — 컴파일 설정에 따라 매개변수 이름이 남지 않는 경우가 있어, 이름을 적는 쪽이 안전하다.

번호를 주소 자체에 실어 `@PathVariable` 로 받는 갈래도 흔하다. 자원을 주소로 가리키는 REST 관점에서는 이쪽이 더 곧다.

```java
@DeleteMapping("/day04/exam/{no}")
public boolean delete(@PathVariable int no) { … }
```

`PUT` 과 `PATCH` 의 갈림도 여기 걸려 있다. `PUT` 은 **보낸 것으로 통째로 바꾼다**는 뜻이고, 일부만 고치는 것은 `PATCH` 다. 1-9-2에서 본 "조회 후 setter" 방식은 안 보낸 필드를 그대로 두므로 실제 동작은 `PATCH` 쪽에 가깝다. 뜻과 동작을 맞춰 두면 API를 읽는 쪽에서 헷갈릴 일이 준다.

달라진 것은 **오가는 타입이 DTO가 아니라 엔티티**라는 점이다.

```
요청 본문 JSON {"ename":"유재석"}
   → @RequestBody → ExamEntity(eno=null, ename="유재석")
   → save → DB가 번호를 채운다
   → ExamEntity(eno=4, ename="유재석")
```

`eno` 를 안 보내도 되는 것이 1-4의 `Integer`·`IDENTITY` 조합 덕분이다. JSON에 키가 없으면 `null` 이 되고, `null` 이면 DB가 채운다.

돌려줄 때는 `List<ExamEntity>` 가 그대로 JSON 배열이 된다. `@Data` 가 만들어 준 getter가 JSON 키를 정하므로, **컬럼 이름이 화면에서 꺼내는 이름까지 그대로 간다.**

한 가지 기억해 둘 것은 **표의 모양이 곧 응답의 모양이 된다**는 점이다. 표에 컬럼이 하나 늘면 응답 JSON에도 키가 하나 는다. 편한 만큼 밖으로 내보내면 안 되는 값까지 같이 나갈 여지가 생기는 자리라, 2-5에서 이어서 본다.

### 1-12. 이 전부를 켜는 한 줄 — 스타터

`build.gradle` 의 의존성이 하나 바뀌었다.

```gradle
// 4. JPA
implementation 'org.springframework.boot:spring-boot-starter-data-jpa'
```

이 한 줄이 데려오는 것이 여럿이다.

| 딸려 오는 것 | 하는 일 |
| --- | --- |
| JPA 규격 (`jakarta.persistence`) | `@Entity`·`@Id` 같은 표시의 정의 |
| 하이버네이트 | 그 표시를 읽어 실제로 SQL을 만드는 구현체 |
| Spring Data JPA | `JpaRepository` 와 구현 객체를 만들어 주는 부분 |
| 커넥션 풀·트랜잭션 | 연결을 미리 잡아 두고 묶음 처리를 거는 자리 |

[[Spring day04 REST 컨트롤러 CRUD 골격]] 에서 스타터가 "같이 쓰는 것들을 묶어 둔 꾸러미"라고 정리했는데, 이번 것이 그 성질이 가장 크게 드러나는 예다. 한 줄을 넣으면 **엔티티를 찾아 표와 맞춰 보고, 리포지토리 인터페이스를 찾아 구현을 만들고, 커넥션 풀을 띄우는** 일이 함께 켜진다.

의존성을 넣는 일이 곧 기능을 켜는 일이 되는 자동 설정 구조 그대로다. `spring.datasource.url` 이 이미 적혀 있으니 조건이 맞고, 그 값으로 연결이 만들어진다.

MySQL 드라이버가 `runtimeOnly` 로 남아 있는 것도 그대로다. JPA를 얹어도 실제로 DB와 이야기하는 것은 여전히 JDBC라, 그 아래층은 바뀌지 않는다.

### 1-13. 정리 — 한 벌이 얼마나 줄었나

도메인 하나를 붙이는 데 필요한 파일이 이렇게 된다.

```
sample.sql        표 만들기
ExamEntity        표와 짝지을 클래스 (필드 + 표시)
ExamRepository    인터페이스 한 줄
ExamService       규칙을 담을 자리
ExamController    주소와 방식
```

`BoardDao` 에 SQL 다섯 벌을 적던 자리가 **인터페이스 한 줄**로 줄었다. 대신 파일이 하나 늘었는데(Service), 줄어든 쪽과 늘어난 쪽의 성격이 다르다.

| | 줄어든 것 | 늘어난 것 |
| --- | --- | --- |
| 무엇 | 되풀이되는 연결·바인딩·매핑 코드 | 규칙을 담을 자리 |
| 성격 | 도메인이 달라도 같던 코드 | 도메인마다 다른 코드 |

**같은 코드는 프레임워크에 넘기고, 다른 코드를 담을 자리는 따로 만든다.** 계층이 하나 느는 것이 손해로 보이지 않는 이유가 여기 있다.

CRUD 네 갈래가 층을 타고 내려가는 모양을 한 번에 놓고 보면 이렇게 된다.

| 갈래 | 컨트롤러 | 서비스 | 리포지토리 | 나가는 SQL |
| --- | --- | --- | --- | --- |
| 조회 | `@GetMapping` | `findAll()` | `findAll()` | `select` |
| 저장 | `@PostMapping` + `@RequestBody` | `save()` | `save()` | `insert` |
| 삭제 | `@DeleteMapping` + `@RequestParam` | `delete()` | `deleteById()` | `delete` |
| 수정 | `@PutMapping` + `@RequestBody` | `update()` | `findById()` + setter | `select` 뒤 `update` |

수정만 리포지토리 호출과 나가는 SQL이 어긋난다. **`update` 를 부르는 자리가 없는데 `update` 가 나간다** — 적은 코드와 도는 동작이 처음으로 갈라지는 지점이다. 다른 셋은 코드에서 SQL을 읽어 낼 수 있는데 수정만 그렇지 않아서, 3-1의 영속성 컨텍스트를 알고 나서야 코드가 온전히 읽힌다.

### 1-14. 표를 하나 더 두고 같은 벌을 다시 짜 보기 — board

한 벌을 끝까지 따라간 뒤, 같은 순서를 표만 바꿔 다시 밟아 보는 자리가 이어진다. `sample.sql` 에 표가 하나 더 붙는다.

```sql
create Table board(
    bno INT PRIMARY KEY AUTO_INCREMENT,
    content VARCHAR(255),
    writer VARCHAR(50)
)

Insert INTO board(content , writer) VALUES ("안녕하세요" , "유재석");
Insert INTO board(content , writer) VALUES ("안녕하세요2" , "강호동");
```

`exam` 은 컬럼이 둘이었는데 `board` 는 셋이다. 늘어난 것은 컬럼 하나뿐이고, 열쇠 자리(`bno INT PRIMARY KEY AUTO_INCREMENT`)의 모양은 그대로다. **DB 하나 안에 표가 여럿이면 엔티티도 표마다 하나씩** 둔다는 배치가 여기서 처음 눈에 보인다.

#### 이름이 갈릴 때 @Table이 하는 일

새 엔티티는 이렇게 된다.

```java
@Entity
@Data
@Table(name = "board")
@AllArgsConstructor
@NoArgsConstructor
@Builder
public class TestEntity {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Integer bno;
    private String content;
    private String writer;
}
```

1-2에서 `@Table(name=…)` 을 생략하면 클래스 이름이 표 이름이 된다고 정리했는데, `ExamEntity` ↔ `exam` 은 이름이 거의 같아서 그 표시가 있어도 없어도 티가 안 났다. 여기서는 클래스가 `TestEntity` 이고 표가 `board` 라 **이름이 완전히 갈린다.** `@Table(name = "board")` 을 빼면 하이버네이트는 `test_entity` 라는 표를 찾다가 없다고 하게 된다. 자동 매핑에 기대지 않고 표 이름을 적어 두는 편이 안전한 이유가 이 자리에서 분명해진다.

나머지는 `exam` 때와 한 글자도 다르지 않다.

| 표시 | 하는 일 | `exam` 과 견줘 |
| --- | --- | --- |
| `@Entity` | DB와 짝지어 관리한다고 선언 | 같음 |
| `@Table(name=…)` | 붙일 표 이름 지목 | 이름이 갈려서 필수가 됨 |
| `@Id` | 열쇠 필드 지정 | 필드 이름만 `eno`→`bno` |
| `@GeneratedValue(IDENTITY)` | 번호 채우기를 DB에 맡김 | 같음 (`AUTO_INCREMENT` 짝) |
| 롬복 넷 | 값 그릇 통로 열기 | 같음 |

**표가 바뀌어도 붙는 표시 한 벌은 그대로다.** 도메인이 달라도 같은 코드는 프레임워크가 가져가고 다른 코드만 남는다던 1-13의 정리가, 두 번째 표를 짜 보면 실제로 무엇이 남는지로 확인된다 — 이번에 새로 적은 것은 표 이름과 필드 셋뿐이다.

#### 컬럼 길이는 자바 쪽에 없다

`content VARCHAR(255)` 와 `writer VARCHAR(50)` 은 길이가 다른데 자바에서는 둘 다 그냥 `String` 이다. 길이 제한이 DB에만 있고 엔티티에는 안 보이는 상태라, 50자를 넘는 값을 넣으면 자바 쪽은 통과하고 DB에서 걸린다. 길이를 코드에도 남기려면 `@Column(length = 50)` 을 붙인다 — 2-10에서 정리한 `@Column` 이 실제로 필요해지는 첫 자리다.

`bno` 가 `int` 가 아니라 `Integer` 인 것도 1-4·2-4와 같은 이유다. 저장 전에는 번호가 없어서 `null` 이고, 저장 뒤 DB가 채운 번호가 들어온다. `int` 로 두면 그 "없음"을 0으로 적게 되고, `save` 가 `insert` 인지 `update` 인지 가르는 기준이 흐려진다.

#### 자리를 먼저 만들어 두고 채우기

`practice2` 패키지에는 다섯 파일이 들어간다.

```
practice2/
├── AppStart.java        진입점 (@SpringBootApplication)
├── TestEntity.java      표와 짝지을 클래스   ← 채워진 상태
├── TestRepository.java  DB 조작              ← 자리만
├── TestService.java     규칙을 담을 자리      ← 자리만
└── TestController.java  주소와 방식          ← 자리만
```

한 벌이 몇 개의 파일로 이루어지는지를 1-13에서 정리해 뒀고, 그 목록대로 **빈 파일을 먼저 만들어 둔 뒤 아래층부터 채워 올라가는 순서**다. 엔티티(표와 짝짓기)가 먼저고, 그다음이 리포지토리, 서비스, 컨트롤러 순이 된다. 아래층이 정해져야 위층이 무엇을 부를지 적을 수 있어서 이 방향이 자연스럽다.

자리만 잡아 둔 단계에서 짚어 둘 것이 하나 있다. **리포지토리는 클래스가 아니라 인터페이스여야 한다.** `JpaRepository` 를 `extends` 해서 구현을 물려받는 구조(1-6)라, 몸통을 적는 `class` 로 두면 스프링이 구현 객체를 만들어 줄 수 없다. 골격 단계에서 `class` 로 잡아 뒀다면 채우기 전에 `interface` 로 바꿔야 한다.

```java
// 자리만 잡은 단계
public class TestRepository { }

// 채울 때
public interface TestRepository extends JpaRepository<TestEntity, Integer> { }
```

제네릭 두 자리에는 조작할 엔티티(`TestEntity`)와 그 PK 타입(`Integer`)이 들어간다. PK 타입은 `@Id` 필드 타입과 같아야 하니 `bno` 가 `Integer` 이면 여기도 `Integer` 다.

서비스와 컨트롤러도 채워질 모양은 `Exam` 쪽과 같다. `@Service` + `final` 리포지토리 + `@RequiredArgsConstructor`, `@RestController` + `final` 서비스 + `@RequiredArgsConstructor`, 그리고 CRUD 네 갈래가 층을 타고 내려가는 표(1-13)가 그대로 반복된다.

#### 진입점이 여럿일 때

`practice2/AppStart.java` 로 `@SpringBootApplication` 이 또 하나 늘었다. 실습 폴더마다 진입점을 두어 스캔 범위를 나누는 배치가 계속 반복되는 것인데, 한 프로젝트에 진입점이 여럿이면 **실행할 때 어느 것을 띄울지 골라야 한다.** 컴포넌트 스캔은 진입점이 있는 패키지 아래만 훑으니, `day04.practice2.AppStart` 를 띄우면 `day04.Exam` 의 빈들은 등록되지 않는다. 실습마다 독립된 앱을 하나씩 띄우는 셈이다.

## 2. 추가로 알면 좋은 활용법

### 2-1. 메소드 이름으로 쿼리 만들기

`JpaRepository` 가 주는 메소드로 모자라면, 인터페이스에 **이름만 적어 두면 된다.**

```java
public interface ExamRepository extends JpaRepository<ExamEntity, Integer> {
    List<ExamEntity> findByEname(String ename);
    List<ExamEntity> findByEnameContaining(String keyword);
    List<ExamEntity> findByEnoGreaterThan(Integer eno);
    boolean existsByEname(String ename);
}
```

몸통은 여전히 없다. 스프링이 **이름을 단어로 쪼개 읽어 쿼리를 만든다.**

```
findBy  Ename  Containing
 ↓       ↓       ↓
조회   ename   like %값%
```

| 이름 조각 | 만들어지는 조건 |
| --- | --- |
| `findByEname` | `where ename = ?` |
| `findByEnameContaining` | `where ename like %?%` |
| `findByEnoGreaterThan` | `where eno > ?` |
| `findByEnameOrderByEnoDesc` | `where ename = ? order by eno desc` |

여기서 걸리는 지점이 하나 있다. **필드 이름과 조각이 어긋나면 뜰 때 걸린다.** 실행 중에 나는 오류가 아니라 시작 단계에서 드러나므로, 오타를 일찍 잡을 수 있다는 뜻이기도 하다.

조건이 서넛을 넘어가면 이름이 길어져 읽기 어려워진다. 그때는 `@Query` 로 직접 적는 쪽이 낫다.

### 2-2. 어떤 SQL이 나가는지 눈으로 보기

1-8에서 남겨 둔 뒷면을 메우는 자리다. `application.properties` 에 두 줄을 더하면 나가는 SQL이 찍힌다.

```properties
spring.jpa.show-sql=true
spring.jpa.properties.hibernate.format_sql=true
```

`findAll()` 하나에 `select` 가 몇 번 나가는지, 저장이 `insert` 인지 `update` 인지를 눈으로 확인할 수 있다. **코드에 안 보이는 것을 로그로 옮겨 보는** 방법이다.

연관관계가 붙기 시작하면 이 로그가 특히 쓸모 있어진다. 목록 하나를 읽는데 쿼리가 수십 번 나가는 문제(3-4)를 알아채는 자리가 여기다.

### 2-3. 표를 자바 쪽에서 만들게 하기 — ddl-auto

지금은 `sample.sql` 로 표를 먼저 만들었다. 엔티티를 보고 표를 만들게 할 수도 있다.

```properties
spring.jpa.hibernate.ddl-auto=update
```

| 값 | 하는 일 |
| --- | --- |
| `none` | 아무것도 안 한다 |
| `validate` | 표와 엔티티가 맞는지 검사만 한다 |
| `update` | 모자란 컬럼·표를 더한다 |
| `create` | 뜰 때마다 지우고 다시 만든다 |
| `create-drop` | `create` + 내려갈 때 지운다 |

실습에서는 `update` 나 `create` 가 편하다. 다만 **`create` 계열은 뜰 때 표를 지운다.** 값이 들어 있는 DB에 붙이면 그대로 사라지므로, 어느 DB를 보고 있는지 확인하고 쓰는 편이 안전하다.

표를 SQL로 만들고 `validate` 로 두는 배치도 있다. 표의 모양은 사람이 정하고, 엔티티와 어긋나면 뜰 때 걸리게 하는 쪽이다.

### 2-4. save가 insert인지 update인지 갈리는 기준

`save()` 하나가 두 가지 일을 한다. 갈리는 기준은 **PK가 비어 있는가** 하나다.

```
entity.eno == null   →  insert  (DB가 번호를 채운다)
entity.eno == 3      →  select 로 확인한 뒤 update
```

1-4에서 `Integer` 로 둔 것이 여기서도 쓰인다. `int` 라면 값이 없을 때 0이 들어가는데, 0은 `null` 이 아니라서 **"3번을 고쳐라"와 같은 갈래로 읽힌다.**

`@RequestBody` 로 받은 값이 그대로 `save` 로 가는 구조에서는 이 성질이 그대로 드러난다. 등록 요청에 번호가 실려 오면 등록이 아니라 수정이 되므로, 받는 쪽에서 번호를 비우거나 요청용 클래스를 따로 두는 편이 분명하다(2-5).

### 2-5. 엔티티를 그대로 내보내지 않기

1-11에서 엔티티를 그대로 주고받았다. 값이 늘면 이 배치가 걸리기 시작한다.

| 걸리는 지점 | 무슨 일이 생기나 |
| --- | --- |
| 표에 컬럼이 늘면 | 응답 JSON에 키가 자동으로 는다 |
| 내보내면 안 되는 값이 있으면 | 그것도 같이 나간다 |
| 요청에 PK가 실려 오면 | 등록이 수정으로 갈릴 수 있다 |
| 연관이 붙으면 | 딸린 객체까지 줄줄이 따라 나간다 |

공통점은 **DB의 모양이 밖으로 새어 나간다**는 것이다. 표를 고치면 API 응답이 같이 바뀌는데, 그건 원래 갈라져 있어야 하는 두 가지다.

```
요청  →  ExamRequest   →  (변환)  →  ExamEntity  →  DB
DB   →  ExamEntity     →  (변환)  →  ExamResponse →  응답
```

작은 실습에서는 파일만 늘어 보인다. 필드가 붙고 화면이 늘기 시작하면 갈라 두는 값어치가 커지는 자리다. 우선 한 클래스로 두더라도 `@JsonIgnore` 로 특정 필드를 응답에서 빼 두는 방법은 알아 둘 만하다.

### 2-6. 엔티티에 @Data를 붙일 때

1-5에서 미뤄 둔 이야기다. `@Data` 가 데려오는 것 중 엔티티와 잘 안 맞는 것이 있다.

| 딸려 오는 것 | 엔티티에서 걸리는 점 |
| --- | --- |
| `@EqualsAndHashCode` | 모든 필드로 같음을 판정한다 — 값이 바뀌면 다른 객체가 된다 |
| `@ToString` | 연관이 얽히면 서로를 찍다가 순환에 빠질 수 있다 |
| `@Setter` | 아무 데서나 값을 바꿀 수 있어 변경 시점이 흩어진다 |

엔티티는 값이 바뀌어도 **PK가 같으면 같은 줄**이다. 모든 필드로 비교하면 그 성질과 어긋난다. `@EqualsAndHashCode(of = "eno")` 처럼 열쇠만 보게 두거나, `@Getter` 와 필요한 생성자만 붙이는 갈래가 있다.

`@Setter` 를 빼는 쪽은 값을 바꾸는 통로를 메소드로 만드는 방식이다. `entity.setEname(…)` 대신 `entity.rename(…)` 처럼 두면, **무엇을 왜 바꾸는지가 이름에 남는다.**

### 2-7. 여러 단계를 한 묶음으로 — @Transactional

값을 바꾸는 일이 두 단계 이상이면 중간에서 끊길 수 있다.

```java
@Service
@RequiredArgsConstructor
public class ExamService {
    @Transactional
    public boolean saveAll(List<ExamEntity> list) { ... }
}
```

`@Transactional` 이 붙은 메소드는 **다 되거나 다 안 되거나** 둘 중 하나가 된다. 중간에 예외가 나면 앞에서 한 것도 되돌린다.

붙는 자리가 보통 Service인 것은 1-9에서 본 계층 성격 때문이다. "여러 단계를 하나의 일로 묶는다"는 판단은 요청을 받는 자리도, DB를 다루는 자리도 아니다.

조회만 하는 메소드에는 `@Transactional(readOnly = true)` 를 두는 관용이 있다. 변경을 추적하지 않아 조금 가벼워진다.

`@Transactional` 이 프록시로 도는 구조라 **같은 클래스 안에서 자기 메소드를 부르면 안 걸린다**는 제약도 기억해 둘 만하다.

### 2-8. boolean 대신 저장된 것을 돌려주기

지금 `save` 는 `boolean` 하나를 돌려준다. 저장은 됐는데 **번호가 몇 번으로 붙었는지가 나가지 않는다.**

```java
@PostMapping("/day04/exam")
public ResponseEntity<ExamEntity> save(@RequestBody ExamEntity entity) {
    ExamEntity saved = examService.save(entity);
    return ResponseEntity.status(HttpStatus.CREATED).body(saved);
}
```

화면 쪽에서 등록 직후에 그 항목을 가리켜야 하는 일이 흔하다. 번호를 같이 돌려주면 목록을 다시 읽지 않고도 이어 갈 수 있다.

[[Spring day04 REST 컨트롤러 CRUD 골격]] 에서 정리한 것과 같은 이야기다. `boolean` 하나로는 성공·실패 두 갈래만 말할 수 있고, 상태 코드를 쓰면 그 갈래가 넓어진다.

### 2-9. 목록이 커질 때 — 페이징과 정렬

`findAll()` 은 표의 줄을 전부 읽는다. 줄이 수만 개가 되면 그대로는 못 쓴다.

```java
Page<ExamEntity> page = examRepository.findAll(PageRequest.of(0, 10));
List<ExamEntity> sorted = examRepository.findAll(Sort.by("eno").descending());
```

`JpaRepository` 가 이 메소드들도 함께 물려준다. `Page` 는 내용뿐 아니라 **전체 개수·전체 쪽수·다음 쪽이 있는지**까지 들고 있어서, 화면의 쪽 번호를 그리는 데 필요한 값이 한 번에 나온다.

컨트롤러 매개변수에 `Pageable` 을 두면 `?page=0&size=10&sort=eno,desc` 를 그대로 받을 수도 있다.

### 2-10. 이름이 어긋날 때 — @Column과 네이밍 전략

컬럼 이름과 필드 이름이 다르면 지목해 준다.

```java
@Column(name = "exam_name", nullable = false, length = 100)
private String ename;
```

`nullable`·`length` 같은 속성은 `ddl-auto` 로 표를 만들 때 제약으로 나간다. 이미 있는 표에 붙이는 경우에는 검사(`validate`)에만 쓰인다.

이름을 하나하나 적지 않아도 되는 이유는 기본 규칙이 있어서다. 하이버네이트는 카멜 표기를 **스네이크 표기로 바꿔** 짝을 찾는다.

```
필드 examName  →  컬럼 exam_name
필드 ename     →  컬럼 ename
```

Spring day02 스프링 부트 실행과 계층 이식 에서 본 자바빈 프로퍼티 규약과는 또 다른 규칙이라, **같은 필드가 JSON 키로 갈 때와 컬럼으로 갈 때 이름이 갈릴 수 있다.** 값이 비어 보이면 어느 쪽 규칙이 걸린 것인지부터 갈라 보는 편이 빠르다.

## 3. 더 나아가 알면 좋은 것

### 3-1. 영속성 컨텍스트 — 객체를 관리하는 상자

JPA가 SQL을 대신 적어 주는 것으로만 보이지만, 그 아래에 상자가 하나 있다. 읽어 온 엔티티를 **담아 두고 상태를 추적하는** 자리다. 1-9-2에서 setter 하나로 수정이 끝나던 자리가 이 상자 위에서 도는 일이다.

```
findById(1)  →  상자에 없으면 select, 있으면 그대로 돌려준다
같은 것을 또 findById(1)  →  쿼리 없이 상자에서 꺼낸다
```

여기서 두 가지가 따라온다. 같은 열쇠로 읽으면 **같은 객체**가 나온다는 것(1차 캐시), 그리고 상자 안의 객체 값을 바꾸면 **`save` 를 부르지 않아도 `update` 가 나간다**는 것(더티 체킹)이다.

```java
@Transactional
public void rename(Integer eno, String name) {
    ExamEntity e = examRepository.findById(eno).orElseThrow();
    e.setEname(name);      // update 가 나간다
}
```

"값을 바꾸면 저장된다"는 것이 처음에는 낯선데, 상자가 원래 값과 지금 값을 견줘 달라진 것만 골라 내보내기 때문이다. 이 성질을 모르면 **의도치 않게 값이 바뀌어 나가는** 자리가 생긴다.

### 3-2. JPA·하이버네이트·Spring Data의 층

이름이 셋인데 서 있는 층이 다르다.

| 이름 | 무엇인가 |
| --- | --- |
| JPA | 자바의 **규격** — `@Entity`·`@Id` 같은 표시의 정의 |
| 하이버네이트 | 그 규격의 **구현체** — 실제로 SQL을 만들어 보낸다 |
| Spring Data JPA | 그 위에 얹은 **편의 층** — `JpaRepository`·이름으로 쿼리 만들기 |

JDBC와 드라이버의 관계와 같은 모양이다. 규격에만 기대어 코드를 적어 두면 구현체를 갈아 끼울 수 있다.

`findAll()` 을 부르면 Spring Data가 하이버네이트를 부르고, 하이버네이트가 SQL을 만들어 JDBC로 보낸다. **층이 셋 겹쳐 있고 맨 아래는 여전히 JDBC**라는 것이 1-12에서 드라이버가 그대로 남아 있는 이유다.

### 3-3. 표 사이의 관계를 객체로 옮기기

지금은 표가 하나뿐이라 관계가 없다. 표가 둘 이상이 되면 그 사이를 객체로 잇는다.

```java
@ManyToOne
@JoinColumn(name = "board_no")
private BoardEntity board;
```

`join` 을 적는 대신 **필드 하나로 관계를 표현한다.** `comment.getBoard().getTitle()` 처럼 객체를 따라가는 모양이 되는 것이 이 방식의 값어치다.

관계 표시가 넷이다 — `@OneToOne`·`@OneToMany`·`@ManyToOne`·`@ManyToMany`. 어느 쪽이 외래키를 들고 있는지(주인)를 정하는 이야기가 따라붙는다.

### 3-4. 목록 하나에 쿼리가 수십 번 나갈 때 — N+1

관계를 붙이면 흔히 만나는 문제다. 목록을 한 번 읽는 `select` 하나에, 줄마다 딸린 것을 읽는 `select` 가 하나씩 더 붙는다.

```
게시글 10건 조회        select 1번
각 글의 댓글을 꺼낼 때   select 10번
                        ─────────
                        11번
```

객체를 따라가는 모양이 편한 대신, **한 줄의 코드가 몇 번의 쿼리가 되는지 안 보인다**는 뒷면이 여기서 드러난다. `fetch join`·`@EntityGraph`·배치 크기 설정으로 줄이는 방법이 있고, 2-2의 SQL 로그가 이것을 알아채는 입구다.

### 3-5. 이름으로 모자랄 때 — JPQL과 Querydsl

조건이 복잡해지면 메소드 이름이 감당하지 못한다. 직접 적는 갈래가 있다.

```java
@Query("select e from ExamEntity e where e.ename like %:kw%")
List<ExamEntity> search(@Param("kw") String kw);
```

`from ExamEntity` 가 표 이름이 아니라 **클래스 이름**이라는 점이 눈에 띈다. JPQL은 표가 아니라 객체를 대상으로 적는 질의라, 필드 이름으로 조건을 건다.

조건이 실행 중에 갈리는 경우(검색 조건이 있을 때만 붙이기 같은)에는 문자열을 이어 붙이는 방식이 위태로워진다. Querydsl은 그 질의를 **자바 코드로 조립**해서 컴파일 시점에 검사받게 하는 갈래다.

### 3-6. 다음에 볼 키워드

- `@Entity`·`@Table`·`@Column`·`@Id`·`@GeneratedValue` — 매핑 표시 한 벌
- `GenerationType` 네 갈래와 DB별 어울리는 전략
- 영속성 컨텍스트·1차 캐시·더티 체킹·`flush`·`clear`
- 엔티티 생명주기 — 비영속·영속·준영속·삭제
- `EntityManager` — Spring Data 아래에서 실제로 도는 자리
- `JpaRepository` 계층 구조 (`Repository`→`CrudRepository`→`PagingAndSortingRepository`→`JpaRepository`)
- 쿼리 메소드 이름 규칙과 `@Query`·`@Param`·네이티브 쿼리
- `Optional` 과 `orElseThrow`·`findById` 가 `Optional` 을 돌려주는 이유
- `save` 의 `insert`·`update` 판정과 `saveAll`·`@Version`
- `spring.jpa.hibernate.ddl-auto` 다섯 값과 운영에서 `validate` 를 쓰는 이유
- `show-sql`·`format_sql`·`p6spy` — 나가는 SQL 확인하기
- `@Transactional` 과 프록시·전파 속성·`readOnly`·자기 호출 제약
- 연관관계 매핑 넷과 연관관계의 주인·`mappedBy`·`@JoinColumn`
- 지연 로딩과 즉시 로딩·`LazyInitializationException`
- N+1 문제와 `fetch join`·`@EntityGraph`·`default_batch_fetch_size`
- 엔티티와 DTO 분리·`@JsonIgnore`·순환 참조
- `Page`·`Pageable`·`Sort`·`Slice` — 페이징과 정렬
- Querydsl·JPQL·Criteria API의 갈림
- `@Embedded`·`@Embeddable` — 값 타입 묶기
- 하이버네이트 네이밍 전략과 카멜↔스네이크 변환
- `@CreatedDate`·`@LastModifiedDate`·`@EnableJpaAuditing` — 생성·수정 시각 자동 채우기
- JPA와 `JdbcTemplate`·MyBatis의 갈림과 같이 쓰는 배치

## 실습 파일

- `2026B_Spring/springweb/src/main/java/day04/sample.sql` (옮겨 담을 표를 먼저 만들어 두기 — `DROP DATABASE if EXISTS` 로 다시 만들기, 컬럼 둘짜리 `exam` 표와 `PRIMARY KEY AUTO_INCREMENT` 가 엔티티의 `@Id`·`@GeneratedValue(IDENTITY)` 와 짝을 이루는 자리, 번호를 적지 않고 `INSERT` 하면 DB가 다음 번호를 채우는 성질, `spring.datasource.url` 이 가리키는 DB 이름과 여기서 만든 이름이 같아야 붙는 점, 컬럼 셋짜리 `board` 표가 뒤에 붙으면서 DB 하나에 표가 여럿이면 엔티티도 표마다 하나씩 두게 되는 배치가 드러나는 자리 — 열쇠 자리(`PRIMARY KEY AUTO_INCREMENT`)의 모양은 표가 바뀌어도 그대로인 점, `VARCHAR(255)` 와 `VARCHAR(50)` 처럼 길이가 갈려도 자바에서는 둘 다 `String` 이라 길이 제한이 DB에만 남는 점과 `@Column(length=…)` 으로 코드에도 남기는 갈래)
- `2026B_Spring/springweb/src/main/java/day04/Exam/ExamEntity.java` (표 하나를 자바 클래스에 짝지어 두기 — `@Entity` 로 DB와 짝지어 관리한다고 선언하기·`@Table(name=…)` 으로 표 이름 지목하기와 생략했을 때 클래스 이름이 표 이름이 되는 규칙, 필드 이름과 컬럼 이름이 짝을 이루어 컬럼→필드→JSON 키→화면으로 이름 하나가 관통하는 자리, DTO와 엔티티가 서 있는 자리의 갈림(오가는 값의 모양 vs DB의 표, 그냥 객체 vs 상태가 추적되는 객체), `@Id` 로 열쇠를 지정하고 엔티티는 PK를 반드시 하나 이상 갖는다는 규칙과 그 이유(객체가 표의 어느 줄인지 늘 알아야 한다), `@GeneratedValue` 로 번호 만들기를 맡기기와 `GenerationType` 네 갈래(`IDENTITY`·`SEQUENCE`·`TABLE`·`AUTO`)·MySQL의 `AUTO_INCREMENT` 와 `IDENTITY` 가 짝인 이유·저장 전 `null` 과 저장 후 채워진 번호를 갈라 보려면 `Integer` 여야 하는 자리, 엔티티에 붙은 롬복 표시 넷과 각각이 여는 통로·JPA 규격이 매개변수 없는 생성자를 요구하는 이유(빈 객체를 먼저 만든 뒤 값을 채운다)와 `@Builder`·`@AllArgsConstructor` 를 붙일 때 기본 생성자를 함께 두는 관용, `@Data` 를 엔티티에 붙일 때 딸려 오는 `@EqualsAndHashCode`·`@ToString`·`@Setter` 가 걸리는 지점과 PK만 보게 두거나 통로를 메소드로 만드는 갈래)
- `2026B_Spring/springweb/src/main/java/day04/Exam/ExamRepository.java` (구현을 적지 않고 규약만 남기기 — 몸통이 빈 인터페이스가 `extends JpaRepository` 한 줄로 메소드를 물려받는 구조·제네릭 두 자리가 조작할 엔티티와 그 PK 타입을 적는 곳이며 PK 타입이 엔티티의 `@Id` 필드 타입과 맞아야 하는 점, 스프링이 시작할 때 인터페이스를 찾아 구현 객체를 만들어 빈으로 등록하는 자리와 "표시를 읽어 동작을 만드는" 구조가 인터페이스 자체를 읽는 쪽으로 간 정리, 물려받는 메소드들(`findAll`·`findById`·`save`·`deleteById`·`count`·`existsById`)과 대응하는 SQL·CRUD 네 갈래가 이름만 바뀌어 그대로 있는 점, `@Repository` 를 붙이지 않아도 Spring Data가 등록하지만 읽는 사람에게 계층이 드러나는 값어치, 직접 JDBC와 견줬을 때 연결·SQL 문자열·값 바인딩·결과 훑기·자원 닫기가 전부 사라지는 자리와 그 대신 무슨 SQL이 나가는지 코드에 안 보이는 뒷면, 메소드 이름으로 쿼리 만들기 — 이름을 단어로 쪼개 읽는 규칙(`findByEname`·`Containing`·`GreaterThan`·`OrderBy`)과 필드 이름이 어긋나면 뜰 때 걸리는 점·조건이 늘면 `@Query` 로 넘어가는 기준)
- `2026B_Spring/springweb/src/main/java/day04/Exam/ExamService.java` (컨트롤러와 DB 사이에 계층 하나 두기 — `@Service` 가 `@Component` 와 결과는 같고 이름이 계층을 말해 주는 점, `findAll` 처럼 넘기기만 하는 자리와 `save` 처럼 리포지토리가 돌려준 값을 보고 판정하는 자리의 갈림·양쪽 어디에 둬도 어색한 코드를 담는 것이 Service의 값어치, `save` 가 영속된 엔티티를 돌려주므로 DB가 채운 번호를 그 자리에서 확인할 수 있는 자리, `final` + `@RequiredArgsConstructor` 로 리포지토리를 주입받기와 컴파일 시점 코드 생성과 실행 시점 주입이 맞물리는 구조·`getInstance()` 로 꺼내 오던 방식과의 갈림(만드는 주체·박히는 이름·테스트에서 다른 구현을 넣을 수 있는 값어치)·각 계층이 자기 바로 아래만 아는 배치, `save` 가 `insert` 인지 `update` 인지 PK가 비어 있는가로 갈리는 기준과 `int` 였다면 0이 "3번을 고쳐라"와 같은 갈래로 읽히는 문제, 여러 단계를 한 묶음으로 묶는 `@Transactional` 이 Service에 붙는 이유와 `readOnly`·프록시로 도는 구조와 자기 호출 제약, 삭제·수정이 붙어 네 갈래가 한 벌로 차는 자리 — `deleteById` 만 돌려주는 값이 없어 성공 여부를 `existsById` 로 따로 확인해야 하는 점, `findById` 가 `Optional<엔티티>` 를 돌려주는 이유(목록은 빈 목록으로 "없음"을 말할 수 있지만 하나를 찾는 일은 `null` 뿐이었다는 자리)와 `isPresent`·`get`·`orElse`·`orElseThrow`·`ifPresent` 의 갈림·확인 없이 `get()` 을 부르면 `null` 검사를 빠뜨린 것과 같아지는 점, 수정이 `save` 호출 없이 setter 하나로 끝나는 구조 — 조회해 온 엔티티가 영속 상태가 되어 트랜잭션이 끝날 때 바뀐 필드만 `update` 로 나가는 더티 체킹·이것이 트랜잭션 안에서만 성립한다는 조건, 조회 후 setter와 `save` 를 다시 부르는 두 갈래의 갈림(나가는 SQL·안 보낸 필드가 원래 값으로 남는가 `null` 로 덮이는가·부분 수정에 어느 쪽이 자연스러운가))
- `2026B_Spring/springweb/src/main/java/day04/Exam/ExamController.java` (엔티티를 그대로 주고받는 네 갈래 — 주소 하나에 `GET`·`POST`·`DELETE`·`PUT` 넷이 붙어 "주소는 자원을 가리키고 방식이 무엇을 할지 말한다"가 온전한 모양이 되는 자리, 받는 방법이 `@RequestParam`(주소 뒤 쿼리 문자열, 값 하나)과 `@RequestBody`(요청 본문 JSON, 객체 한 벌)로 갈리는 기준과 `@RequestParam(name=…)` 으로 이름을 적어 두는 편이 안전한 이유, 번호를 주소에 실어 `@PathVariable` 로 받는 갈래와 REST 관점에서의 값어치, `PUT`(통째로 바꾸기)과 `PATCH`(일부만 고치기)의 갈림과 조회 후 setter 방식의 실제 동작이 `PATCH` 쪽에 가까운 점, 주소는 같고 방식으로 갈리는 배치의 반복·오가는 타입이 DTO가 아니라 엔티티라는 점, `@RequestBody` 로 받은 JSON에 PK 키가 없으면 `null` 이 되고 DB가 번호를 채워 돌아오는 왕복, `List<ExamEntity>` 가 그대로 JSON 배열이 되고 `@Data` 의 getter가 JSON 키를 정하는 자리·표의 모양이 곧 응답의 모양이 되는 점과 내보내면 안 되는 값까지 나갈 여지, 엔티티를 그대로 내보내지 않는 갈래 — 표를 고치면 API 응답이 같이 바뀌는 문제·요청용과 응답용을 갈라 두기·`@JsonIgnore` 로 응답에서 필드 빼기, `boolean` 대신 저장된 엔티티와 상태 코드를 돌려줘 등록 직후 번호를 화면에 넘기기, 목록이 커질 때 `Page`·`Pageable`·`Sort` 로 쪽을 나누기와 `Page` 가 전체 개수·쪽수까지 들고 있는 점)
- `2026B_Spring/springweb/src/main/java/day04/Exam/AppStart.java` (실습 폴더마다 진입점을 두어 컴포넌트 스캔 범위를 나누는 구조의 반복 — 이 패키지 아래의 컨트롤러·서비스·리포지토리만 등록되는 자리)
- `2026B_Spring/springweb/src/main/java/day04/practice2/TestEntity.java` (표를 하나 더 두고 같은 벌을 다시 짜 보기 — 클래스 이름(`TestEntity`)과 표 이름(`board`)이 완전히 갈리면서 `@Table(name=…)` 이 있고 없고가 처음으로 티가 나는 자리·생략하면 `test_entity` 를 찾게 되므로 자동 매핑에 기대지 않고 표 이름을 적어 두는 편이 안전한 이유, 표가 바뀌어도 붙는 표시 한 벌(`@Entity`·`@Table`·`@Id`·`@GeneratedValue(IDENTITY)`·롬복 넷)은 그대로이고 새로 적는 것은 표 이름과 필드뿐이라는 확인 — "같은 코드는 프레임워크가 가져가고 다른 코드만 남는다"의 실측, `bno` 가 `int` 가 아니라 `Integer` 인 이유의 반복(저장 전 `null`·저장 후 채워진 번호·`save` 의 `insert`/`update` 판정))
- `2026B_Spring/springweb/src/main/java/day04/practice2/TestRepository.java`, `TestService.java`, `TestController.java`, `AppStart.java` (자리를 먼저 만들어 두고 아래층부터 채워 올라가는 순서 — 한 벌이 몇 개의 파일인지 정리해 둔 목록대로 빈 파일을 먼저 두는 배치와 엔티티→리포지토리→서비스→컨트롤러 방향이 자연스러운 이유, 리포지토리는 `class` 가 아니라 `interface` 여야 `JpaRepository` 를 `extends` 해 구현을 물려받을 수 있다는 점과 제네릭 두 자리에 들어가는 엔티티·PK 타입, 한 프로젝트에 `@SpringBootApplication` 이 여럿일 때 실행할 진입점을 골라야 하는 자리와 컴포넌트 스캔이 그 패키지 아래만 훑어 실습마다 독립된 앱이 되는 구조)
- `2026B_Spring/springweb/build.gradle` (스타터 한 줄로 JPA를 켜기 — `spring-boot-starter-data-jpa` 가 데려오는 것들(JPA 규격·하이버네이트 구현체·Spring Data JPA·커넥션 풀과 트랜잭션)과 의존성을 넣는 일이 곧 기능을 켜는 일이 되는 자동 설정 구조의 재확인, 엔티티를 찾아 표와 맞추고 리포지토리 인터페이스의 구현을 만드는 일이 함께 켜지는 자리, MySQL 드라이버가 여전히 `runtimeOnly` 인 이유 — JPA를 얹어도 맨 아래층은 JDBC라는 점, `spring.jpa.show-sql`·`format_sql` 로 나가는 SQL을 로그로 옮겨 보기와 `spring.jpa.hibernate.ddl-auto` 다섯 값의 갈림·`create` 계열이 뜰 때 표를 지우는 점과 표는 SQL로 만들고 `validate` 로 두는 배치)

## 관련 노트

[[Spring MOC]] · [[Spring day04 REST 컨트롤러 CRUD 골격]] · [[Repository Pattern]] · [[개념 - CRUD]] · [[KDT_2026 학습 지도]]
