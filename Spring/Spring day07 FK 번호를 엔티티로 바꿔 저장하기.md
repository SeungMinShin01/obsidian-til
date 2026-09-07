---
출처: Claude 분석
원본: KDT_2026/2026B_Spring/springweb/src/main/java/day07/practice/service/EnrollService.java, springweb/src/main/java/day07/practice/controller/EnrollController.java, springweb/src/main/java/day07/practice/model/dto/EnrollDto.java, springweb/src/main/java/day07/practice/model/entity/EnrollEntity.java
작성일: 2026-09-07
tags: [학습, java]
---

# Spring day07 — FK 번호를 엔티티로 바꿔 저장하기

> 실습 파일: `day07/practice/service/EnrollService.java`, `day07/practice/controller/EnrollController.java`, `day07/practice/model/dto/EnrollDto.java`, `day07/practice/model/entity/EnrollEntity.java`
> 허브: [[Spring MOC]] · 이전: [[Spring day07 계층 분리와 패키지 재편]] · 다음: [[Spring day07 댓글이 딸린 목록을 화면에 그리기]]

앞에서 DTO 변환 메소드를 만들면서 **"FK 번호를 엔티티로 바꾸는 일은 서비스 몫"** 이라고 비워 둔 자리가 있었습니다. 수강신청 갈래를 채우면서 그 자리가 실제로 어떻게 메워지는지 정리합니다. 관계를 가진 엔티티를 저장할 때 웹에서 온 번호와 JPA가 요구하는 객체 참조 사이에 생기는 틈이 이번 주제입니다.

## 1. 배운 내용

### 1-1. 요청은 번호로 오고, 엔티티는 객체를 요구한다

`EnrollEntity` 는 외래키를 번호가 아니라 상대 엔티티 타입으로 들고 있습니다.

```java
@JoinColumn(name = "course_id")
@ManyToOne
private CourseEntity courseEntity;

@JoinColumn(name = "student_id")
@ManyToOne
private StudentEntity studentEntity;
```

반면 화면에서 수강신청을 보낼 때 실을 수 있는 것은 번호뿐입니다. 과정 객체 한 벌을 JSON으로 통째 보내는 것이 아니라 `courseId: 1` 처럼 열쇠만 보냅니다. 그래서 `EnrollDto` 에는 엔티티에 없는 필드 두 개가 따로 있습니다.

```java
// 자바(JPA)에서 entity 로 FK 를 다루지만, 입력받을 때는 FK 번호로 받는다
private Integer courseId;
private Integer studentId;
```

| 층 | 관계를 담는 모양 | 이유 |
| --- | --- | --- |
| 요청 JSON | 번호 (`courseId`) | HTTP로 실어 보낼 수 있는 것은 값 하나 |
| DTO | 번호 (`Integer`) | 요청을 그대로 받는 그릇 |
| 엔티티 | 객체 참조 (`CourseEntity`) | JPA가 관계를 객체로 다룬다 |
| DB | 컬럼 (`course_id`) | 표에는 결국 번호 하나 |

양 끝(요청과 표)은 번호인데 가운데(엔티티)만 객체입니다. **번호 → 객체 → 번호로 한 번 갔다 오는 구간이 생기는 셈**이고, 그 변환을 누가 하는지가 이번 갈래의 요점입니다.

### 1-2. `toEntity()` 가 관계 필드를 비워 두는 이유

```java
public EnrollEntity toEntity() {
    return EnrollEntity.builder()
            .status(this.status)
            // 학생FK, 과정FK 는 서비스에서 엔티티로 변환
            .build();
}
```

DTO가 가진 것은 번호뿐이라 여기서는 `CourseEntity` 를 만들 수 없습니다. 번호로 객체를 얻으려면 DB를 한 번 읽어야 하고, 그것은 리포지토리를 아는 층의 일입니다. DTO는 리포지토리를 모르므로 **여기서 멈추는 것이 층 경계를 지키는 모양**입니다.

앞 노트에서 정리한 경계선이 그대로 적용된 자리입니다 — 엔티티 하나와 한 칸 이웃만 보면 나오는 값은 DTO가 채우고, 조회가 더 필요한 값은 서비스가 채웁니다. 번호를 객체로 바꾸는 일은 조회가 필요하므로 서비스 쪽입니다.

### 1-3. 서비스가 번호 두 개를 객체 두 개로 바꾸는 자리

```java
public boolean enrollSave(EnrollDto enrollDto) {
    EnrollEntity enrollEntity = enrollDto.toEntity();           // 1. status 만 채워진 상태

    Optional<StudentEntity> optional1 = studentRepository.findById(enrollDto.getStudentId());
    Optional<CourseEntity>  optional2 = courseRepository.findById(enrollDto.getCourseId());

    if (optional1.isPresent() && optional2.isPresent()) {       // 2. 둘 다 있을 때만
        enrollEntity.setStudentEntity(optional1.get());
        enrollEntity.setCourseEntity(optional2.get());
        EnrollEntity savedEntity = enrollRepository.save(enrollEntity);
        if (savedEntity.getEnrollId() >= 1)
            return true;
    }
    return false;                                                // 3. 하나라도 없으면 저장 안 함
}
```

메소드 하나가 하는 일을 갈라 보면 이렇습니다.

| 단계 | 하는 일 | 쓰는 리포지토리 |
| --- | --- | --- |
| 1 | DTO를 엔티티로 (관계는 빈 채) | — |
| 2 | 번호 두 개를 각각 조회 | 학생·과정 |
| 3 | 조회한 객체를 관계 필드에 대입 | — |
| 4 | 저장하고 PK로 성공 판정 | 수강 |

**리포지토리 셋을 한 메소드 안에서 쓰는 첫 자리**입니다. 지금까지의 서비스는 자기 도메인 리포지토리 하나만 들고 있었는데, 관계를 만드는 갈래는 관계에 참여하는 표를 모두 알아야 합니다. 앞 노트에서 "여러 리포지토리를 함께 부르는 묶음의 경계가 서비스"라고 적어 둔 것이 실제 코드로 나타났습니다.

### 1-4. `findById` 가 "존재 확인"과 "객체 얻기"를 겸한다

눈여겨볼 것은 조회 두 줄이 목적을 두 개 갖는다는 점입니다.

- **객체를 얻는다** — 관계 필드에 넣을 `StudentEntity`·`CourseEntity` 를 구한다
- **존재를 확인한다** — 없는 번호로 보낸 요청을 여기서 걸러 낸다

없는 과정 번호로 수강신청이 들어오면 `optional2` 가 비어 `if` 를 통과하지 못하고 `false` 로 끝납니다. 저장 자체를 시도하지 않으므로 DB의 외래키 제약까지 가지 않습니다.

| 막는 자리 | 걸리는 방식 |
| --- | --- |
| 서비스의 `isPresent()` 검사 | 저장 전에 `false` 로 돌아온다 |
| DB의 외래키 제약 | 저장을 시도하고 예외가 튄다 |

둘 다 잘못된 번호를 막지만 **결과를 값으로 받느냐 예외로 받느냐가 갈립니다.** 앞 노트에서 등록 갈래의 `boolean` 이 잡는 실패 범위가 좁다고 적어 뒀는데, 이번 갈래는 그 범위가 조금 넓어진 모양입니다. "대상이 없음"이라는 실패 하나는 값으로 표현되기 때문입니다.

### 1-5. 빌더로 만들고 setter로 마저 채우기

관계 필드를 대입할 때 쓰는 것은 setter입니다.

```java
enrollEntity.setStudentEntity(studentEntity);
```

엔티티는 `@Builder` 로 만들었는데 만든 뒤에 setter로 채우는 모양이라 두 방식이 한 메소드 안에 섞여 있습니다. `@Data` 가 setter를 만들어 주기 때문에 성립하는 코드입니다.

```
builder()로 만들기 ──▶ [ status 만 채워진 엔티티 ] ──▶ setter 두 번 ──▶ [ 완성된 엔티티 ]
   (DTO가 아는 몫)                                     (서비스가 아는 몫)
```

빌더에 한 번에 다 넣지 않고 두 단계로 나뉜 이유는 **재료가 준비되는 시점이 다르기** 때문입니다. `status` 는 DTO에 이미 있고, 관계 객체는 DB를 읽어야 나옵니다. 조회를 먼저 해서 재료를 다 모은 뒤 빌더 한 번으로 만드는 순서로 적을 수도 있습니다.

```java
// 조회를 먼저 하고 빌더 한 번으로 끝내는 순서
EnrollEntity enrollEntity = EnrollEntity.builder()
        .status(enrollDto.getStatus())
        .studentEntity(studentEntity)
        .courseEntity(courseEntity)
        .build();
```

둘의 갈림은 `toEntity()` 를 쓸 수 있느냐입니다. 앞 표기는 변환 책임을 DTO에 남겨 두고 부족한 부분만 채우고, 뒤 표기는 서비스가 조립을 전부 맡습니다. 변환 규칙이 늘어날수록 DTO 쪽에 모아 두는 편이 흩어지지 않습니다.

### 1-6. 조회 갈래 — `orElse(null)` 로 상자 벗기기

```java
public EnrollDto enrollFindAll(Integer enrollId) {
    EnrollEntity enrollEntity = enrollRepository.findById(enrollId).orElse(null);
    return EnrollDto.from(enrollEntity);
}
```

`findById` 가 돌려주는 `Optional` 을 여는 방법은 여럿인데 여기서는 `orElse(null)` 을 썼습니다. 지금까지 나온 것들을 모으면 이렇습니다.

| 표기 | 없을 때 | 성질 |
| --- | --- | --- |
| `isPresent()` + `get()` | `if` 안으로 안 들어간다 | 분기를 직접 적는다 |
| `orElse(기본값)` | 기본값이 나온다 | 분기가 사라진다 |
| `orElseThrow()` | 예외가 던져진다 | 없음을 실패로 다룬다 |
| 상자째 반환 | 판정이 위층으로 밀린다 | 컨트롤러가 벗긴다 |

`orElse(null)` 은 짧지만 **`Optional` 이 옮겨 둔 "없음"을 다시 `null` 로 되돌리는 표기**라는 점을 같이 봐 두면 좋습니다. 없음을 타입으로 드러내려고 상자에 담았는데 곧바로 벗겨 버리면 그 값어치가 남지 않습니다. 뒤에서 그 값을 그대로 쓰는 코드가 있다면 `null` 을 만나는 자리가 한 칸 뒤로 밀릴 뿐입니다.

관계를 가진 엔티티를 변환할 때는 이 점이 더 걸립니다. `EnrollDto.from()` 은 안에서 관계를 한 칸 타고 들어가 이름을 꺼내는 모양이기 때문입니다.

```java
.courseName(entity.getCourseEntity().getCourseName())
.studentName(entity.getStudentEntity().getStudentName())
```

값이 있을 때는 잘 도는 줄이지만, 넘어온 것이 비어 있으면 첫 번째 점에서 막힙니다. **관계를 타고 들어가는 코드 앞에는 대상이 있는지 확인하는 자리가 필요하다**는 것이 이 갈래에서 정리해 둘 점입니다. 조회 결과가 없을 수 있는 갈래는 다음 중 하나로 갈립니다.

- 서비스에서 `null` 을 걸러 그대로 `null` 을 돌려준다 (변환을 건너뛴다)
- `orElseThrow` 로 없음을 예외로 올리고 예외 처리에서 404를 만든다
- `Optional` 을 그대로 넘겨 컨트롤러가 `ResponseEntity` 로 갈라 준다

### 1-7. 컨트롤러 — 본문으로 받고 쿼리스트링으로 받기

```java
@PostMapping("")
public boolean enrollSave(@RequestBody EnrollDto enrollDto) {
    return enrollService.enrollSave(enrollDto);
}

@GetMapping("/detail")
public EnrollDto enrollFindAll(@RequestParam(name = "enrollId") Integer enrollId) {
    return enrollService.enrollFindAll(enrollId);
}
```

두 갈래가 값을 받는 통로가 갈립니다.

| 갈래 | 표시 | 값이 실려 오는 곳 | 받는 모양 |
| --- | --- | --- | --- |
| 등록 | `@RequestBody` | 요청 본문 JSON | DTO 한 벌 |
| 조회 | `@RequestParam` | 쿼리스트링 | 값 하나 |

등록은 채울 필드가 여럿이라 객체로 받고, 조회는 열쇠 하나만 있으면 되므로 값 하나로 받습니다. day03에서 정리한 "무엇을 받는가에 따라 표시가 갈린다"가 한 컨트롤러 안에 나란히 놓인 자리입니다.

메소드 매핑에 `/detail` 을 붙여 목록·상세를 주소로 가른 것도 눈에 띕니다. 같은 `GET` 이 둘이면 방식으로는 못 가르므로 주소를 달리해야 합니다. 다만 식별자를 주소에 싣는 갈래(`/detail/{enrollId}` + `@PathVariable`)가 REST 관용에는 더 가깝습니다 (2-3).

### 1-8. 지금까지 이어진 수강신청 흐름

세로로 관통한 갈래를 한 줄로 이어 보면 이렇습니다.

```
POST /api/... {courseId, studentId, status}
      │  @RequestBody
      ▼
EnrollDto ──toEntity()──▶ EnrollEntity (status 만)
      │                        ▲
      │ getStudentId()         │ setStudentEntity()
      │ getCourseId()          │ setCourseEntity()
      ▼                        │
studentRepository.findById() ──┘
courseRepository.findById()
      │
      ▼
enrollRepository.save() ──▶ enroll 표에 course_id·student_id 로 저장
```

번호로 들어와 객체가 되었다가 다시 번호로 저장됩니다. 가운데 구간이 있는 이유는 JPA가 관계를 객체로 다루기 때문이고, 그 덕분에 조회할 때 `enrollEntity.getCourseEntity().getCourseName()` 처럼 표를 넘나들지 않고 점으로 따라갈 수 있습니다. **저장할 때 드는 수고와 조회할 때 얻는 편의가 짝**입니다.

## 2. 추가로 알면 좋은 활용법

### 2-1. `findById` 대신 `getReferenceById` 로 조회를 줄이기

관계 필드에 넣을 객체는 사실 **번호만 정확하면 됩니다.** 저장할 때 나가는 SQL에는 `course_id` 컬럼에 들어갈 값 하나만 필요하지, 과정 이름이 필요하지 않습니다.

```java
CourseEntity courseRef = courseRepository.getReferenceById(enrollDto.getCourseId());
enrollEntity.setCourseEntity(courseRef);
```

`getReferenceById` 는 실제 조회를 미루고 번호만 든 프록시 객체를 돌려줍니다. 관계를 걸고 저장만 할 것이라면 `select` 두 번이 줄어듭니다.

| 항목 | `findById` | `getReferenceById` |
| --- | --- | --- |
| 조회 SQL | 바로 나간다 | 필드를 건드릴 때 나간다 |
| 없는 번호일 때 | 빈 `Optional` | 나중에 예외 |
| 존재 확인 | 겸할 수 있다 | 못 한다 |

존재 확인을 겸하고 싶은 자리에서는 `findById` 쪽이 맞습니다. 확인이 이미 끝났거나 외래키 제약에 맡길 생각이라면 `getReferenceById` 로 줄일 수 있습니다. **조회 두 번을 아끼는 대신 없는 번호를 값으로 못 거른다**는 맞바꿈입니다.

### 2-2. 존재 확인만 필요하면 `existsById`

객체가 아니라 있는지 없는지만 알면 되는 자리에서는 `existsById` 가 있습니다. `select 1` 에 가까운 쿼리라 엔티티를 통째로 읽지 않습니다.

```java
if (!studentRepository.existsById(studentId)) return false;
```

지금 갈래는 객체 자체가 필요하므로 `findById` 가 맞습니다. 삭제 전 확인처럼 **객체는 안 쓰고 존재만 보는 자리**에서 갈립니다.

### 2-3. 식별자를 주소에 싣는 갈래

조회 주소를 이렇게 두는 표기도 있습니다.

```java
@GetMapping("/{enrollId}")
public EnrollDto enrollFind(@PathVariable Integer enrollId) { … }
```

| 표기 | 주소 | 어울리는 자리 |
| --- | --- | --- |
| `@RequestParam` | `/detail?enrollId=1` | 조건·검색어·페이지 번호 |
| `@PathVariable` | `/enroll/1` | 자원을 식별하는 열쇠 |

"어떤 자원인가"는 주소에, "어떻게 걸러 볼 것인가"는 쿼리스트링에 두는 기준이 REST 관용입니다. 한 프로젝트 안에서 갈래마다 다르게 두면 화면 쪽에서 주소를 매번 확인하게 되므로 하나로 정해 두는 편이 낫습니다.

### 2-4. 주소 앞머리와 매핑이 겹칠 때

컨트롤러가 늘어나면 클래스 `@RequestMapping` 앞머리와 메소드 매핑이 이어 붙은 결과가 다른 컨트롤러와 겹칠 여지가 생깁니다. 겹치면 요청이 올 때가 아니라 **서버가 뜰 때** 걸립니다. 스프링이 시작하면서 주소 표를 먼저 만들기 때문입니다.

도메인이 늘 때 앞머리를 정하는 기준을 하나 정해 두면 겹침을 미리 피할 수 있습니다.

- 도메인 이름을 그대로 앞머리로 (`/api/enroll`)
- 상위 자원 밑에 두기 (`/api/course/{courseId}/enroll`)

두 번째는 "이 과정의 수강 목록"처럼 관계가 주소에 드러나는 표기입니다. 중간 표를 다루는 갈래는 어느 부모에 매달아 볼지에 따라 주소가 갈리므로, 어느 쪽에서 주로 조회할지를 먼저 정하고 주소를 잡는 편이 흔들리지 않습니다.

### 2-5. 관계를 만드는 갈래에 트랜잭션이 필요한 이유

지금 `enrollSave` 는 조회 두 번과 저장 한 번, 모두 세 번 DB에 나갑니다. 그 사이에 대상이 사라질 수 있습니다.

```
학생 조회 (있음) ──▶ 과정 조회 (있음) ──▶ [ 이 틈에 과정이 삭제되면 ] ──▶ save 에서 제약 위반
```

`@Transactional` 을 붙이면 세 번이 한 묶음이 되어 중간에 끊긴 상태가 남지 않습니다. 확인과 저장 사이의 틈을 완전히 없애려면 격리 수준이나 잠금까지 봐야 하지만, 우선은 **여러 번 나가는 DB 접근을 한 묶음으로 두는 것**이 서비스 메소드의 기본 모양이라고 정리해 둡니다.

### 2-6. 겸용 DTO에 남는 빈 필드

`EnrollDto` 는 필드가 여덟 개인데 갈래마다 쓰이는 것이 다릅니다.

| 필드 | 등록 요청 | 조회 응답 |
| --- | --- | --- |
| `status` | 채워 보낸다 | 채워 나간다 |
| `courseId`·`studentId` | 채워 보낸다 | 비어 있다 |
| `courseName`·`studentName` | 비어 있다 | 채워 나간다 |
| `enrollId` | 비어 있다 | 채워 나간다 |

한 클래스가 두 방향을 겸하면 **어느 방향에서든 절반이 비는 필드가 생깁니다.** 응답 JSON에 `courseId: null` 이 섞여 나가는 것도 이 사정입니다. 갈래가 늘면 요청용(`EnrollSaveRequest`)과 응답용(`EnrollResponse`)으로 가르는 방향이 있고, 지금처럼 갈래가 적을 때는 한 벌로 두고 필요한 것만 채우는 편이 파일 수가 적습니다.

응답에서 빈 필드를 지우고 싶으면 `@JsonInclude(JsonInclude.Include.NON_NULL)` 로 `null` 필드를 빼는 표기가 있습니다.

### 2-7. 관계를 채우는 코드가 되풀이될 때

도메인이 늘면 "번호를 받아 객체를 찾아 넣는" 모양이 계속 반복됩니다. 되풀이를 줄이는 갈래로는 이런 것들이 있습니다.

- 서비스 안에 `private` 보조 메소드로 뽑기 — 가장 가볍고, 실패했을 때 무엇을 돌려줄지만 정하면 된다
- 예외로 통일하기 — `orElseThrow(() -> new NotFoundException("과정"))` 로 적으면 `if` 중첩이 사라진다
- 매퍼 층 두기 — 변환 전담 클래스를 만들어 서비스에서 걷어 낸다

지금 규모에서는 첫 번째로 충분합니다. 조건이 둘일 때는 `if` 하나로 묶이지만, 셋 넷으로 늘면 중첩이 눈에 띄기 시작하고 그때가 예외 쪽으로 옮길 시점입니다.

### 2-8. `Optional` 변수 이름

지금은 `optional1`·`optional2` 로 번호를 붙여 두었습니다. 대상이 셋 넷으로 늘면 어느 것이 무엇인지 따라가기 어려워지므로 담긴 것을 이름에 남기는 편(`studentOptional`·`courseOptional`)이 읽기 편합니다. 변수 이름은 **한 메소드 안에서만 사는 정보**라 나중에 고치는 부담이 작은 자리이기도 합니다.

## 3. 더 나아가 알면 좋은 것

### 3-1. 연관관계 편의 메소드

지금은 수강 엔티티 쪽에만 값을 넣습니다. 과정 엔티티가 들고 있는 `enrollEntities` 목록은 그대로라 **같은 트랜잭션 안에서 양쪽이 어긋난 상태**가 됩니다. DB에는 제대로 저장되지만, 저장 직후 그 과정 객체의 목록을 읽으면 방금 넣은 수강이 안 보입니다.

```java
public void setCourse(CourseEntity course) {
    this.courseEntity = course;
    course.getEnrollEntities().add(this);   // 반대쪽도 함께
}
```

이렇게 양쪽을 한 번에 맞추는 메소드를 편의 메소드라고 부릅니다. 앞 노트의 양방향 참조에서 "양쪽 필드를 함께 채워야 짝이 성립한다"고 적어 둔 것이 저장 갈래에서 나타나는 자리입니다.

### 3-2. 중간 표의 중복을 막는 자리

같은 학생이 같은 과정에 두 번 신청하면 지금 코드는 그대로 저장합니다. 막으려면 세 자리 중 하나를 고르게 됩니다.

| 자리 | 방법 | 성질 |
| --- | --- | --- |
| DB | 복합 유니크 제약 | 어떤 경로로 들어와도 막힌다. 예외로 튄다 |
| 리포지토리 | `existsByStudentEntityAndCourseEntity` | 값으로 판정할 수 있다 |
| 서비스 | 위 조회를 저장 앞에 둔다 | 규칙이 코드에 드러난다 |

DB 제약만 두면 사용자에게 이유를 알려 주기 어렵고, 서비스 확인만 두면 다른 경로로 들어오는 저장을 못 막습니다. **둘을 겹쳐 두고 서비스에서 먼저 걸러 안내하고 DB는 마지막 방어선으로 두는 배치**가 흔합니다. 재수강처럼 같은 짝이 다시 들어올 수 있는 도메인이면 제약에 기수나 연도가 함께 들어가야 한다는 점도 앞에서 정리한 그대로입니다.

### 3-3. 상태 값을 바꾸는 갈래가 이어지는 자리

수강 엔티티의 `status` 는 지금 등록할 때 한 번 정해집니다. 다음에 붙을 것은 그 값을 바꾸는 갈래인데, 영속 상태의 엔티티는 setter 하나로 `update` 가 나갑니다.

```java
@Transactional
public boolean changeStatus(Integer enrollId, String status) {
    return enrollRepository.findById(enrollId)
            .map(enroll -> { enroll.setStatus(status); return true; })
            .orElse(false);
}
```

`save` 를 부르지 않아도 도는 것은 변경 감지 때문이고, `@Transactional` 이 없으면 오류 없이 값만 안 바뀝니다. 통로를 setter가 아니라 `enroll.수강취소()` 같은 이름 붙인 메소드로 좁혀 두면 어떤 상태 변화가 있는지가 엔티티에 목록으로 남습니다.

### 3-4. 저장 갈래에서 `boolean` 이 못 싣는 것

이번 갈래의 `false` 는 뜻이 둘입니다 — 학생이 없거나, 과정이 없거나. 화면 쪽에서는 어느 쪽인지 알 수 없습니다.

```java
if (optional1.isEmpty()) throw new NotFoundException("학생을 찾을 수 없습니다");
if (optional2.isEmpty()) throw new NotFoundException("과정을 찾을 수 없습니다");
```

예외로 갈라 두고 `@RestControllerAdvice` 에서 상태 코드와 메시지를 만들면 화면 쪽이 무엇을 고쳐 보내야 하는지 알 수 있습니다. **실패의 종류가 둘 이상 생기는 순간이 `boolean` 반환을 다시 볼 시점**입니다.

### 3-5. 조회에서 관계를 함께 읽어 오기

상세 조회 하나만 보면 쿼리가 셋 나갑니다 — 수강 하나, 과정 하나, 학생 하나. 변환 메소드가 관계를 두 칸 건드리기 때문입니다. 목록 조회로 늘어나면 이 곱셈이 그대로 커집니다.

```java
@Query("select e from EnrollEntity e join fetch e.courseEntity join fetch e.studentEntity where e.enrollId = :id")
Optional<EnrollEntity> findWithNames(@Param("id") Integer id);
```

`@ManyToOne` 은 컬렉션이 아니라 `join fetch` 를 걸어도 결과 줄 수가 늘지 않습니다. 컬렉션을 함께 읽을 때 따라오던 `distinct`·페이징 제약이 없는 쪽이라 손이 덜 갑니다. `@EntityGraph` 로 리포지토리 메소드에 표시만 붙이는 갈래도 같은 일을 합니다.

### 3-6. 다음에 볼 키워드

- `getReferenceById` · 프록시 객체 · 초기화 시점과 `LazyInitializationException`
- `existsById` · `existsBy…` 파생 쿼리
- `@Transactional` 의 경계와 확인·저장 사이의 틈 · 격리 수준
- `orElseThrow` · 사용자 정의 예외 · `@RestControllerAdvice` · `@ExceptionHandler`
- `@PathVariable` 과 중첩 자원 주소 설계
- 연관관계 편의 메소드 · 양쪽 필드를 함께 맞추는 자리
- 복합 유니크 제약 (`@Table(uniqueConstraints = …)`)
- `@JsonInclude` · 요청·응답 DTO 분리 · `record`
- `join fetch` · `@EntityGraph` · `@ManyToOne` 과 컬렉션 페치의 갈림
- `@Enumerated(EnumType.STRING)` — 상태 값을 문자열 대신 상수로

## 실습 파일

- `2026B_Spring/springweb/src/main/java/day07/practice/service/EnrollService.java` (**FK 번호를 엔티티로 바꾸는 자리** — DTO가 가진 번호로 `findById` 를 두 번 불러 객체를 얻고 setter로 관계 필드에 대입한 뒤 저장하는 네 단계, 리포지토리 셋을 한 메소드에서 쓰는 첫 자리이자 "여러 리포지토리를 함께 부르는 묶음의 경계가 서비스"라는 정리가 코드로 나타난 지점, `isPresent()` 검사가 객체 얻기와 존재 확인을 겸해 없는 번호를 DB 제약보다 앞에서 값으로 걸러 내는 배치, 조회 갈래에서 `orElse(null)` 로 `Optional` 을 곧바로 벗길 때 없음이 다시 `null` 로 돌아오는 점과 관계를 타고 들어가는 변환 앞에 대상 확인이 필요한 이유)
- `2026B_Spring/springweb/src/main/java/day07/practice/controller/EnrollController.java` (**한 컨트롤러에 두 통로가 나란히 놓인 자리** — 등록은 `@RequestBody` 로 DTO 한 벌을, 조회는 `@RequestParam` 으로 값 하나를 받는 갈림과 그 기준, 같은 `GET` 이 둘일 때 주소로 갈라야 하는 점과 식별자를 주소에 싣는 `@PathVariable` 갈래와의 대비, 도메인이 늘 때 주소 앞머리를 정하는 두 기준과 겹침이 서버 시작 때 걸리는 사정)
- `2026B_Spring/springweb/src/main/java/day07/practice/model/dto/EnrollDto.java` (**요청은 번호·응답은 이름으로 갈리는 겸용 DTO** — 엔티티에 없는 `courseId`·`studentId` 가 DTO에만 있는 이유와 `toEntity()` 가 관계 필드를 비워 두는 층 경계, `from()` 이 관계를 한 칸 타고 들어가 이름만 꺼내는 줄이 대상이 비어 있으면 막히는 자리, 갈래마다 절반이 비는 필드가 남는 겸용 DTO의 성질과 요청·응답을 가르는 갈래)
- `2026B_Spring/springweb/src/main/java/day07/practice/model/entity/EnrollEntity.java` (**관계를 객체 참조로 드는 쪽** — 외래키를 `Integer` 가 아니라 상대 엔티티 타입으로 두어 요청(번호)→엔티티(객체)→표(컬럼)로 한 번 갔다 오는 구간이 생기는 구조와 그 수고가 조회에서 점으로 따라가는 편의와 짝이라는 정리, 빌더로 만든 뒤 setter로 관계를 채우는 두 단계 조립과 재료가 준비되는 시점이 달라 갈리는 자리)

## 관련 노트

[[Spring MOC]] · [[Spring day07 계층 분리와 패키지 재편]] · [[Spring day07 댓글이 딸린 목록을 화면에 그리기]] · [[KDT_2026 학습 지도]]
