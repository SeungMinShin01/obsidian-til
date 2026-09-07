---
출처: Claude 분석
원본: KDT_2026/2026B_Spring/springweb/src/main/java/day07/practice/CourseDto.java, springweb/src/main/java/day07/practice/StudentDto.java, springweb/src/main/java/day07/practice/EnrollDto.java, springweb/src/main/java/day07/practice/EnrollEntity.java
작성일: 2026-09-07
tags: [학습, java]
---

# Spring day07 — 연관 엔티티를 DTO로 펴기

> 실습 파일: `2026B_Spring/springweb/src/main/java/day07/practice/CourseDto.java`, `day07/practice/StudentDto.java`, `day07/practice/EnrollDto.java`, `day07/practice/EnrollEntity.java`
> 허브: [[Spring MOC]] · 이전: [[Spring day07 상태를 가진 중간 엔티티]] · 다음: [[Spring day07 계층 분리와 패키지 재편]]

앞에서 과정·학생·수강 세 엔티티로 관계를 세워 두었다. 관계를 여는 이야기를 할 때마다 "엔티티를 그대로 내보내지 않고 관계를 평평하게 편 DTO로 푼다"라고 적어 두었는데, 그 대응이 실제 코드로 나온 자리가 여기다.

엔티티가 서로를 필드로 들고 있는 동안 그 객체는 **그물**이다. 과정을 꺼내면 수강 목록이 딸려 오고, 수강 하나를 열면 다시 과정과 학생이 딸려 온다. 화면이나 API가 필요로 하는 것은 그 그물 전체가 아니라 **한 줄로 펴 놓은 값 몇 개**다. DTO는 그 펴는 작업의 결과를 담는 그릇이다.

## 1. 배운 내용

### 1-1. 관계를 가진 엔티티를 그대로 내보내지 않는 이유

`EnrollEntity` 는 번호가 아니라 상대 엔티티 타입으로 외래키를 든다.

```java
@JoinColumn(name = "course_id")
@ManyToOne
private CourseEntity courseEntity;

@JoinColumn(name = "student_id")
@ManyToOne
private StudentEntity studentEntity;
```

이 모양 그대로 바깥으로 나가면 걸리는 곳이 셋이다.

| 걸리는 곳 | 무엇이 생기나 |
| --- | --- |
| 순환 | 수강 → 과정 → 수강 목록 → 과정 … 을 왕복하다 끝나지 않는다 |
| 지연 로딩 | 직렬화가 목록을 건드리는 순간 조회가 따라 나간다 |
| 과다 노출 | 상대 표의 컬럼이 통째로 실려 나간다 |

셋 다 "관계를 타고 들어갈 수 있다"라는 하나의 성질에서 나온다. 그래서 대응도 하나다 — **관계를 타고 들어가는 일을 변환 시점에 미리 해 두고, 그 결과만 담은 평평한 객체를 내보낸다.**

### 1-2. 두 방향 변환 메소드 — `toEntity` 와 `from`

DTO마다 메소드가 둘씩 붙는다. 방향이 반대라 선언 모양도 갈린다.

```java
// 들어오는 방향 — 인스턴스 메소드
public StudentEntity toEntity() {
    return StudentEntity.builder()
            .studentName(this.studentName)
            .build();
}

// 나가는 방향 — 정적 메소드
public static StudentDto from(StudentEntity entity) {
    return StudentDto.builder()
            .studentId(entity.getStudentId())
            .studentName(entity.getStudentName())
            .createdAt(entity.getCreatedAt())
            .updatedAt(entity.getUpdatedAt())
            .build();
}
```

| 메소드 | 부르는 자리 | 선언 |
| --- | --- | --- |
| `toEntity()` | 이미 DTO를 손에 들고 있다 (요청 본문이 DTO로 바인딩된 뒤) | 인스턴스 메소드 — `this` 가 재료다 |
| `from(entity)` | 아직 DTO가 없다 (리포지토리가 엔티티를 돌려준 뒤) | 정적 메소드 — 없는 것을 만들어 내는 자리라 인스턴스가 있을 수 없다 |

`from` 이 `static` 인 이유는 규칙이 아니라 순서의 문제다. **DTO를 만들려고 부르는 메소드를 DTO 인스턴스에 붙여 두면 부를 수가 없다.** [[Spring day05 DTO 변환과 초기 데이터 적재]] 에서 정리한 배치가 도메인만 바뀌어 그대로 반복된다.

`toEntity()` 안에서 PK를 빼는 것도 그대로다. 번호는 DB가 채우는 값이라 등록 요청이 들고 올 자리가 아니다.

### 1-3. 입력은 번호로, 출력은 이름으로

`EnrollDto` 의 필드를 늘어놓으면 성격이 다른 두 벌이 한 클래스에 있다.

```java
private Integer enrollId;
private String status;
private LocalDateTime createdAt;
private LocalDateTime updatedAt;

// 들어올 때 쓰는 자리 — 외래키를 번호로 받는다
private Integer courseId;
private Integer studentId;

// 나갈 때 쓰는 자리 — 상대 표에서 이름만 가져온다
private String courseName;
private String studentName;
```

자바 쪽에서는 외래키가 엔티티 타입이지만, **요청으로 들어오는 값은 객체가 아니라 번호**다. 화면에서 과정을 고르면 넘어오는 것은 `course_id` 하나지 과정 객체 전체가 아니다. 반대로 응답에서 필요한 것은 번호가 아니라 사람이 읽을 이름이다.

| 방향 | 관계를 표현하는 값 |
| --- | --- |
| 요청 → 서버 | 번호 (`courseId`, `studentId`) |
| 서버 → 응답 | 이름 (`courseName`, `studentName`) |

같은 관계인데 방향에 따라 담기는 값이 다르다. 이 둘을 한 DTO에 함께 두면 클래스는 하나로 끝나는 대신 **어떤 요청에서도 늘 절반은 비어 있는 필드가 생긴다.** 실습 단계에서는 클래스 수가 적은 쪽이 흐름을 보기 쉽고, 화면이 늘면 용도별로 가르는 갈래가 있다 (2-1).

### 1-4. 관계를 타고 들어가 값 하나만 꺼내기

나가는 방향의 변환에서 상대 표의 값을 가져오는 줄은 이렇게 생겼다.

```java
public static EnrollDto from(EnrollEntity entity) {
    return EnrollDto.builder()
            .enrollId(entity.getEnrollId())
            .status(entity.getStatus())
            .courseName(entity.getCourseEntity().getCourseName())
            .studentName(entity.getStudentEntity().getStudentName())
            .build();
}
```

`entity.getCourseEntity().getCourseName()` 은 점을 두 번 찍어 **관계를 한 칸 타고 들어간 뒤 값 하나만 꺼내는** 모양이다. 이 한 줄이 하는 일을 나눠 보면 이렇다.

```
EnrollEntity ──getCourseEntity()──▶ CourseEntity ──getCourseName()──▶ String
   (그물의 매듭)                        (상대 매듭)                     (평평한 값)
```

여기서 그물이 끊긴다. `CourseEntity` 는 변환하는 동안만 손에 들렸다가 DTO 밖으로 나가지 않고, 나가는 것은 문자열 하나다. **관계를 타고 들어가는 일을 서버 안에서 끝내 두면 바깥에는 탈 수 있는 관계가 남지 않는다** — 순환도, 예상 못 한 조회도 여기서 함께 사라진다.

대신 이 줄은 **쿼리가 나갈 수 있는 자리**이기도 하다. `@ManyToOne` 을 `LAZY` 로 두면 `getCourseEntity()` 를 부를 때까지 과정은 안 읽히고, 이 줄에서 처음 읽힌다. 목록을 변환하면 줄 수만큼 그 일이 반복된다 (2-2).

### 1-5. 일부러 비워 두는 자리

들어오는 방향의 변환은 필드를 다 채우지 않는다.

```java
public EnrollEntity toEntity() {
    return EnrollEntity.builder()
            .status(this.status)
            .build();
}
```

`status` 만 담기고 과정·학생은 비어 있다. 이유는 **DTO가 가진 것과 엔티티가 원하는 것의 타입이 다르기 때문**이다.

| 가진 것 | 원하는 것 | 사이에 필요한 일 |
| --- | --- | --- |
| `Integer courseId` | `CourseEntity` | 번호로 과정을 조회해 객체로 바꾼다 |
| `Integer studentId` | `StudentEntity` | 번호로 학생을 조회해 객체로 바꾼다 |

번호를 객체로 바꾸려면 조회가 필요하고, 조회는 리포지토리를 들고 있는 곳에서만 할 수 있다. DTO는 리포지토리를 모른다. 그래서 **번호→객체 변환은 서비스 몫으로 남는다.**

`CourseDto` 의 학생 목록도 같은 이유로 비어 있다.

```java
private List<StudentDto> studentDtos = new ArrayList<>();
```

과정 하나의 학생 목록은 `course` 표에 있는 값이 아니라 **수강 표를 거쳐야 나오는 값**이다. 관계를 두 칸 타고 들어가야 하고(과정 → 수강 → 학생), 그 중간에 조건이 붙을 수도 있다(수강중인 학생만 등). 한 엔티티만 보고 채울 수 있는 값이 아니라 조립하는 자리, 곧 서비스로 넘어간다.

정리하면 변환 메소드가 채우는 범위는 이렇게 갈린다.

| 채우는 자리 | 값의 성격 |
| --- | --- |
| DTO의 변환 메소드 | 엔티티 하나(와 그 한 칸 이웃)만 보면 나오는 값 |
| 서비스 | 조회가 더 필요하거나 여러 엔티티를 모아야 나오는 값 |

### 1-6. DTO가 감사 필드를 상속이 아니라 필드로 받는 자리

엔티티는 `extends BaseTime` 으로 시각 두 개를 물려받는데, DTO는 그러지 않고 같은 이름의 필드를 그냥 선언한다.

```java
private LocalDateTime createdAt;
private LocalDateTime updatedAt;
```

`BaseTime` 은 `@MappedSuperclass`·`@EntityListeners` 가 붙은 **JPA용 클래스**다. 표를 만들고 저장 시각을 자동으로 채우는 일이 목적이라, 표와 무관한 DTO가 물려받을 이유가 없다. DTO 쪽의 두 필드는 자동으로 채워지는 값이 아니라 **`from()` 이 엔티티에서 복사해 넣는 값**이다.

같은 이름이 두 층에 있지만 하는 일이 갈린다.

| 층 | `createdAt` 의 성격 |
| --- | --- |
| 엔티티 | 표의 컬럼이자 감사 리스너가 채우는 자리 |
| DTO | 그 값을 담아 나르는 평범한 필드 |

DTO에 상속을 두지 않으면 클래스마다 두 줄이 반복되지만, **표와 응답이 서로 다른 이유로 바뀌는 것들**이라 층을 섞지 않는 쪽이 나중에 갈라 두기 쉽다.

### 1-7. DTO에 붙는 롬복 네 표시

DTO마다 같은 네 개가 붙는다.

```java
@NoArgsConstructor
@AllArgsConstructor
@Builder
@Data
```

엔티티에 붙던 것과 같은 조합인데, 붙이는 이유가 조금 다르다.

| 표시 | DTO에서 하는 일 |
| --- | --- |
| `@NoArgsConstructor` | JSON 본문을 필드에 바인딩할 때 빈 생성자로 먼저 만든다 |
| `@AllArgsConstructor` | `@Builder` 가 쓸 전체 생성자를 만든다 |
| `@Builder` | `from()` 안에서 필드 이름을 적어 가며 채우는 통로 |
| `@Data` | getter·setter·`toString`·`equals` 한 벌 |

[[Spring day05 DTO 변환과 초기 데이터 적재]] 에서 `@Builder` 만 붙이면 기본 생성자가 사라지는 자리를 정리해 뒀는데, DTO에서는 그 문제가 JPA가 아니라 **요청 본문 바인딩**에서 나타난다. 넷을 짝으로 붙이는 관용이 두 층 모두에 통하는 이유다.

`@Data` 는 DTO에서는 무난하다. 관계를 이미 펴 놓아 `toString` 이 타고 들어갈 곳이 없기 때문이다 (2-3).

## 2. 추가로 알면 좋은 활용법

### 2-1. 용도마다 DTO를 가르기

지금은 도메인 하나에 DTO 하나다. 화면이 늘면 한 클래스가 감당하는 용도가 늘고, 늘 절반이 비는 필드가 생긴다. 가르는 기준은 **요청이냐 응답이냐**가 가장 먼저다.

```java
public record EnrollCreateRequest(Integer courseId, Integer studentId) {}
public record EnrollResponse(Integer enrollId, String status,
                             String courseName, String studentName) {}
```

| 방식 | 성질 |
| --- | --- |
| DTO 하나로 겸용 | 클래스가 적다. 어떤 필드가 언제 쓰이는지는 코드를 읽어야 안다 |
| 요청·응답 분리 | 클래스가 는다. 필드 목록 자체가 그 요청의 명세가 된다 |

`record` 는 값만 담고 바뀌지 않는 그릇을 짧게 쓰는 문법이라 응답 DTO와 잘 맞는다. 다만 요청 DTO로 쓰면 기본 생성자가 없어 바인딩 방식에 제약이 생기므로, 어느 쪽에 쓸지 정해 두고 들이는 편이 안전하다.

### 2-2. 목록을 변환할 때 따라붙는 쿼리

`from()` 이 관계를 타고 들어가는 줄은 목록 앞에서 성격이 달라진다.

```java
List<EnrollDto> list = repository.findAll().stream()
        .map(EnrollDto::from)
        .toList();
```

수강이 100줄이면 `findAll()` 로 한 번, 그리고 `getCourseEntity().getCourseName()` 이 100번 불리며 과정 조회가 최대 100번 더 나갈 수 있다. **1 + N** — 앞 노트들에서 이름만 적어 두었던 N+1이 실제로 생기는 자리가 여기다.

푸는 갈래는 조회 시점에 관계까지 함께 읽어 오는 것이다.

```java
@Query("select e from EnrollEntity e join fetch e.courseEntity join fetch e.studentEntity")
List<EnrollEntity> findAllWithNames();
```

| 방식 | 쿼리 수 |
| --- | --- |
| `findAll()` + 변환에서 관계 타기 | 1 + N |
| `join fetch` 로 함께 읽기 | 1 |

`EAGER` 로 바꾸는 것은 해법이 아니다. **읽는 시점만 앞당길 뿐 쿼리 수는 그대로**이고, 그 관계가 필요 없는 조회에서도 늘 따라 나간다. 로딩 전략은 `LAZY` 로 두고 **필요한 조회에서만 `join fetch` 로 앞당기는** 쪽이 기본이다.

한 가지 더 — 변환을 어디서 하느냐도 걸린다. 지연 로딩은 영속성 컨텍스트가 살아 있는 동안에만 통하므로, 변환은 트랜잭션 안(서비스)에서 끝내는 편이 안전하다. 컨트롤러까지 엔티티를 들고 나가서 거기서 변환하면 관계를 타는 순간 이미 닫혀 있을 수 있다.

### 2-3. `@Data` 가 DTO에서는 무난하고 엔티티에서는 위험한 이유

같은 표시인데 층에 따라 판단이 갈린다.

| 층 | `@Data` 가 만드는 `toString`·`equals` |
| --- | --- |
| 엔티티 | 연관 필드를 타고 상대를 부르고, 상대가 다시 이쪽을 부른다 → 순환 |
| DTO | 필드가 전부 값 타입이라 탈 곳이 없다 |

엔티티 쪽에서 `@ToString.Exclude` 로 한 곳을 끊어 두는 이유가 이것이고, DTO에는 그 표시가 필요 없다. **관계를 펴 두면 순환을 막을 표시도 함께 필요 없어진다** — DTO가 순환 대책이기도 한 이유다.

다만 DTO가 다른 DTO의 목록을 들면 이야기가 조금 돌아온다. `CourseDto` 가 `List<StudentDto>` 를 들고 학생 쪽에서 다시 과정을 들면 같은 왕복이 DTO 층에서 재현된다. **펴는 방향은 한쪽으로만 두는 것**이 기준이다.

### 2-4. 입력 검증을 DTO에 붙이기

요청 DTO는 바깥에서 들어온 값이 처음 담기는 자리라, 값을 거르는 표시를 붙이기 좋은 위치다.

```java
@NotBlank(message = "상태값은 필수입니다")
private String status;

@NotNull(message = "과정 번호는 필수입니다")
private Integer courseId;
```

```java
@PostMapping
public EnrollDto save(@Valid @RequestBody EnrollDto dto) { … }
```

`@Valid` 를 파라미터에 붙여야 표시가 실제로 검사된다 — 표시만 달아 두면 아무 일도 일어나지 않는다. 서비스에 `if` 로 적는 갈래와 비교하면 이렇다.

| 자리 | 성질 |
| --- | --- |
| DTO + `@Valid` | 형식 검사(빈 값·길이·범위). 서비스에 닿기 전에 걸러진다 |
| 서비스 | 도메인 검사(이미 신청한 과정인가 등). DB를 봐야 알 수 있는 것 |

둘은 대체 관계가 아니라 **거르는 종류가 다르다.** 형식은 앞에서, 도메인은 뒤에서 거른다.

## 3. 더 나아가 알면 좋은 것

### 3-1. 변환 코드를 어디에 둘지

지금은 DTO 안에 변환 메소드가 있다. 자리 후보는 셋이다.

| 자리 | 성질 |
| --- | --- |
| DTO 안 (`toEntity`·`from`) | 변환할 짝과 코드가 같은 파일에 있다. DTO가 엔티티를 알게 된다 |
| 별도 매퍼 클래스 | DTO가 엔티티를 모르게 된다. 파일이 는다 |
| MapStruct 같은 생성기 | 인터페이스만 적으면 구현이 컴파일 시점에 만들어진다 |

DTO가 엔티티를 알아도 되는가는 의존 방향의 문제다. DTO는 바깥(웹)에 가깝고 엔티티는 안쪽(DB)에 가까운데, 지금 배치는 바깥이 안쪽을 알고 있는 모양이다. 규모가 작을 때는 파일이 적은 쪽이 읽기 쉽고, 도메인을 웹에서 떼어 내려는 단계에서 매퍼가 들어온다. **처음부터 도구를 들이지 않고 손으로 적는 줄이 지겨워지는 것을 신호로 삼는 편이 낫다.**

### 3-2. 응답을 조립하는 책임이 어디로 모이는가

DTO가 채우지 않고 남긴 자리(FK 객체 변환, 학생 목록)는 전부 서비스로 모인다. 서비스가 하는 일을 순서로 적으면 이렇다.

```
요청 DTO ─▶ 번호로 부모 조회 ─▶ toEntity() + 부모 채우기 ─▶ save
저장 결과 ─▶ from() ─▶ 목록·부가 값 채우기 ─▶ 응답 DTO
```

변환 메소드가 "혼자 채울 수 있는 것"만 맡고 나머지를 서비스에 남기면, **서비스를 읽는 것만으로 그 요청이 무엇을 모아 응답을 만드는지가 드러난다.** 반대로 변환 메소드가 리포지토리를 들고 조회까지 하면 조회가 코드 곳곳으로 흩어진다.

### 3-3. 응답 모양을 DB에서 바로 만들기

관계를 편 결과만 필요하면 엔티티를 거치지 않고 조회 단계에서 바로 그 모양으로 받는 갈래도 있다.

```java
@Query("select new day07.practice.EnrollDto(e.enrollId, e.status, " +
       "e.courseEntity.courseName, e.studentEntity.studentName) from EnrollEntity e")
List<EnrollDto> findAllFlat();
```

| 방식 | 성질 |
| --- | --- |
| 엔티티 조회 후 변환 | 엔티티가 손에 남아 수정·검증에 쓸 수 있다 |
| 조회에서 바로 DTO | 필요한 컬럼만 읽는다. 변경 감지가 안 걸린다 |

읽기 전용 화면은 뒤쪽이 가볍고, 값을 고칠 흐름은 앞쪽이 있어야 한다. **읽기와 쓰기가 필요로 하는 모양이 다르다**는 것이 이 갈림의 뿌리이고, 그 갈래를 아예 나눠 설계하는 이름이 CQRS다.

### 3-4. 다음에 볼 키워드

- `record` 와 `class` 를 DTO에 쓸 때의 갈림 — 불변·기본 생성자·바인딩 제약
- `@Valid` 와 `@Validated` 의 차이, 검증 실패 응답을 `@RestControllerAdvice` 로 한 곳에서 만들기
- `join fetch` 와 `@EntityGraph` — N+1을 푸는 두 표기와 페이징이 함께 걸릴 때의 제약
- 인터페이스 기반 프로젝션(`interface EnrollView { String getCourseName(); }`) 과 DTO 프로젝션의 손익
- `@JsonIgnore`·`@JsonProperty` 로 응답 모양을 손보는 갈래와 DTO를 따로 두는 갈래의 경계
- MapStruct 로 변환 구현을 생성하기 — 컴파일 시점에 걸리는 필드 불일치
- 페이징 응답을 담는 그릇(`Page<T>` 를 그대로 내보낼 때와 감싸서 내보낼 때)
- API 응답을 감싸는 공통 봉투(`{ code, message, data }`) 를 둘지 말지의 갈림

## 실습 파일

- `2026B_Spring/springweb/src/main/java/day07/practice/EnrollDto.java` (**관계를 편 DTO의 본보기** — 외래키를 요청에서는 번호로 받고 응답에서는 이름으로 내보내 같은 관계가 방향에 따라 다른 값으로 담기는 자리, `entity.getCourseEntity().getCourseName()` 이 관계를 한 칸 타고 들어가 값 하나만 꺼내며 그물을 끊는 지점과 그 줄이 곧 지연 로딩 쿼리가 나가는 자리라 목록 변환에서 N+1이 되는 점, `toEntity()` 가 `status` 만 담고 FK 객체 변환을 서비스에 남기는 이유가 DTO는 리포지토리를 모른다는 데 있다는 정리)
- `2026B_Spring/springweb/src/main/java/day07/practice/CourseDto.java` (**DTO 안에 DTO 목록을 두는 자리** — `List<StudentDto>` 가 한 엔티티만 보고는 채울 수 없는 값이라 서비스 조립 몫으로 남는 점과 과정→수강→학생 두 칸을 타야 나오는 값이라는 확인, DTO 층에서 목록을 양쪽으로 들면 순환이 재현되므로 펴는 방향을 한쪽으로 두는 기준)
- `2026B_Spring/springweb/src/main/java/day07/practice/StudentDto.java` (**두 방향 변환 메소드의 최소 형태** — `toEntity()` 가 인스턴스 메소드이고 `from()` 이 정적 메소드인 이유가 부르는 시점에 인스턴스가 있느냐로 갈린다는 정리, `toEntity()` 에서 PK를 빼 두는 배치와 감사 필드를 상속이 아니라 평범한 필드로 복사해 받는 자리·표와 응답이 서로 다른 이유로 바뀌므로 층을 섞지 않는다는 기준, DTO에 붙는 롬복 네 표시가 엔티티와 같은 조합이되 이유는 JPA가 아니라 요청 본문 바인딩이라는 점)
- `2026B_Spring/springweb/src/main/java/day07/practice/EnrollEntity.java` (**펴기 전의 모양** — 외래키를 상대 엔티티 타입으로 드는 `@ManyToOne`+`@JoinColumn` 두 벌이 순환·지연 로딩·과다 노출 셋의 공통 뿌리인 자리와 그 셋이 "관계를 타고 들어갈 수 있다"는 한 가지 성질에서 나오므로 대응도 하나라는 정리, `@Data` 가 엔티티에서는 순환을 만들고 DTO에서는 탈 곳이 없어 무난해지는 대비)

## 관련 노트

[[Spring MOC]] · [[Spring day07 상태를 가진 중간 엔티티]] · [[Spring day07 계층 분리와 패키지 재편]] · [[Spring day05 DTO 변환과 초기 데이터 적재]] · [[KDT_2026 학습 지도]]
