---
출처: Claude 분석
원본: KDT_2026/2026B_Spring/springweb/src/main/java/day07/practice/model/repository, springweb/src/main/java/day07/practice/service, springweb/src/main/java/day07/practice/controller, springweb/src/main/java/day07/practice/model/entity, springweb/src/main/java/day07/practice/model/dto
작성일: 2026-09-07
tags: [학습, java]
---

# Spring day07 — 계층 분리와 패키지 재편

> 실습 파일: `day07/practice/model/repository/CourseRepository.java`, `day07/practice/model/repository/StudentRepository.java`, `day07/practice/model/repository/EnrollRepository.java`, `day07/practice/service/CourseService.java`, `day07/practice/service/StudentService.java`, `day07/practice/service/EnrollService.java`, `day07/practice/controller/CourseController.java`, `day07/practice/controller/StudentController.java`, `day07/practice/controller/EnrollController.java`
> 허브: [[Spring MOC]] · 이전: [[Spring day07 연관 엔티티를 DTO로 펴기]]

엔티티 세 벌과 DTO 세 벌까지 만들어 둔 상태에서, 그 아래위로 리포지토리·서비스·컨트롤러를 한 층씩 얹은 자리를 정리합니다. 이번에 새로 배운 표시는 거의 없고 대신 **파일을 어디에 두는가**와 **각 층이 무엇을 알아야 하는가**가 주제가 됩니다.

## 1. 배운 내용

### 1-1. 한 패키지에 쌓이던 파일을 역할별 폴더로 가르기

day04~day06까지는 실습 묶음 하나가 패키지 하나였고 엔티티·DTO·리포지토리·서비스·컨트롤러가 같은 자리에 나란히 놓였습니다. 도메인이 셋(과정·학생·수강)으로 늘고 층이 다섯이 되면 파일이 열다섯 개 가까이 한 폴더에 쌓입니다. 이번 실습은 그 지점에서 폴더를 갈랐습니다.

```
day07/practice/
├── AppStart.java
├── model/
│   ├── entity/      CourseEntity · StudentEntity · EnrollEntity · BaseTime
│   ├── dto/         CourseDto · StudentDto · EnrollDto
│   └── repository/  CourseRepository · StudentRepository · EnrollRepository
├── service/         CourseService · StudentService · EnrollService
└── controller/      CourseController · StudentController · EnrollController
```

가르는 축이 **도메인(과정·학생·수강)이 아니라 계층(모델·서비스·컨트롤러)**이라는 점이 눈에 띕니다. 같은 층의 파일끼리 모이면 "지금 리포지토리 층을 채우는 중"처럼 층 단위로 작업이 묶이고, 도메인 하나를 따라 읽으려면 폴더 셋을 오가게 됩니다. 반대로 도메인 축으로 갈랐다면(`course/`·`student/`·`enroll/`) 읽는 방향이 뒤집힙니다. 어느 쪽이 옳다기보다 프로젝트가 자라는 방향에 맞춰 고르는 것이고, 도메인 수가 적고 층이 뚜렷할 때는 계층 축이 다루기 쉬운 편입니다.

`model` 밑에 entity·dto·repository 셋을 함께 둔 배치도 뜻이 있습니다. 셋 다 "데이터를 어떻게 담고 꺼내는가"에 속하고, 웹 요청을 아는 것은 controller 하나뿐입니다.

### 1-2. 패키지가 갈리면 import가 늘어난다

같은 패키지에 있는 동안에는 서로를 이름만으로 부를 수 있었습니다. 폴더를 가르면 `package` 선언이 달라지고, 다른 폴더의 클래스를 쓰려면 `import` 를 적어야 합니다.

```java
package day07.practice.model.repository;

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import day07.practice.model.entity.CourseEntity;   // 폴더가 갈려 필요해진 줄
```

`import` 목록이 곧 그 파일이 무엇에 기대고 있는지의 목록이 됩니다. 컨트롤러 파일을 열었을 때 `model.entity` 를 import 하고 있다면 엔티티가 웹 층까지 올라온 것이고, 서비스가 `web.bind.annotation` 을 import 하고 있다면 층이 섞인 것입니다. 패키지를 가르면 **의존 방향이 파일 머리에 그대로 드러난다**는 것이 폴더 나누기의 부수 효과입니다.

한 가지 짝지어 봐야 할 것은 폴더를 옮기면 `package` 선언도 함께 바뀌어야 한다는 점입니다. 자바에서 패키지는 폴더 경로와 같은 값이어야 하고, 둘이 어긋나면 컴파일 단계에서 걸립니다. 폴더만 옮기고 선언을 그대로 두거나, 선언만 고치고 파일은 그대로 두는 상태는 성립하지 않습니다.

### 1-3. 리포지토리 세 벌 — 제네릭 두 자리만 갈리는 복사

```java
@Repository
public interface CourseRepository extends JpaRepository<CourseEntity, Integer> {

}
```

세 파일이 모두 같은 모양이고 갈리는 것은 제네릭 첫 자리(다룰 엔티티)와 인터페이스 이름뿐입니다. PK 타입은 셋 다 `Integer` 라 두 번째 자리까지 같습니다. day04에서 "아래층으로 갈수록 갈림이 줄고 위층으로 갈수록 는다"고 적어 둔 것이 도메인이 셋으로 늘어난 자리에서 다시 확인됩니다.

정리하면 이렇습니다.

| 항목 | 내용 |
| --- | --- |
| `interface` 인 이유 | 구현을 물려받아야 해서 — 스프링이 시작할 때 구현 객체를 만들어 빈으로 등록한다 |
| 제네릭 첫 자리 | 다룰 엔티티 타입 |
| 제네릭 둘째 자리 | 그 엔티티 `@Id` 필드의 타입 |
| 몸통이 비어 있는데 되는 이유 | `findAll`·`findById`·`save`·`deleteById`·`count`·`existsById` 가 물려 내려온다 |
| `@Repository` | 없어도 등록되지만 붙이면 계층이 이름으로 드러나고, DB 예외를 스프링 표준 예외로 바꿔 준다 |

중간 엔티티인 `EnrollEntity` 도 리포지토리를 따로 갖습니다. 중간 표라고 해서 부모 리포지토리를 통해서만 다뤄야 하는 것은 아니고, 그 자체가 표 하나라 열쇠로 찾고 저장하는 통로가 필요합니다. 수강 상태를 바꾸는 갈래가 결국 이 리포지토리를 지나게 됩니다.

### 1-4. 서비스 — 리포지토리를 하나씩 들고 서는 자리

```java
@Service
public class CourseService {
    @Autowired
    private CourseRepository courseRepository;
}
```

`@Service` 는 `@Component` 와 등록 결과가 같고 이름이 계층을 말해 줍니다. `@Autowired` 를 필드에 붙이면 스프링이 컨테이너에서 같은 타입의 빈을 찾아 그 자리에 넣어 줍니다. `new` 로 만들지 않고, `getInstance()` 로 꺼내 오지도 않습니다.

여기서 서비스가 아는 것은 리포지토리 하나뿐입니다. 컨트롤러를 모르고, 웹 요청도 모릅니다. 그래서 서비스 파일만 놓고 보면 이 클래스가 HTTP로 불리는지 배치 작업으로 불리는지 알 수 없고, 그것이 층을 나눈 값어치입니다.

세 서비스 모두 아직 몸통이 비어 있습니다. 이 상태에서 서버를 띄우면 빈은 등록되고 주입도 되지만 부를 메소드가 없습니다. 자리만 잡아 둔 단계라는 뜻입니다.

### 1-5. 컨트롤러 — 도메인마다 주소 앞머리를 나누기

```java
@RestController
@RequestMapping("/api/course")
public class CourseController {
    @Autowired
    private CourseService courseService;

    // [1] 등록
    @PostMapping("")
    public boolean courseSave(@RequestBody CourseDto courseDto) {
        return courseService.courseSave(courseDto);
    }
}
```

클래스에 붙은 `@RequestMapping` 이 주소 앞머리를 정하고, 메소드의 `@PostMapping("")` 이 그 주소를 그대로 씁니다. 결과는 `POST /api/course` 한 자리입니다. 괄호를 비운 표기가 "앞머리만 쓰고 더 붙이지 않는다"는 뜻이라는 것은 day04에서 정리한 그대로입니다.

세 컨트롤러가 나란히 있으니 주소 설계가 눈에 들어옵니다.

| 컨트롤러 | 앞머리 | 다루는 것 |
| --- | --- | --- |
| CourseController | `/api/course` | 과정 등록·조회 |
| StudentController | `/api/student` | 학생 등록·조회 |
| EnrollController | (수강 갈래) | 수강신청·상태 변경 |

주소 앞머리는 **컨트롤러마다 겹치지 않게 갈라 두는 편이 안전합니다.** 앞머리가 같은 컨트롤러가 둘이면 메소드 주소와 방식이 겹칠 여지가 생기고, 겹치면 요청이 올 때가 아니라 서버가 뜰 때 걸립니다. 주소 표를 미리 만들어 두는 구조라서 그렇습니다. 앞 슬래시를 붙이는가 마는가 하는 표기도 한 프로젝트 안에서는 하나로 정해 두는 편이 읽기 편합니다.

### 1-6. 세 층에 걸친 의존 방향

이번 실습에서 파일 아홉 개를 만들며 실제로 그어진 선을 정리하면 이렇습니다.

```
Controller  ──▶  Service  ──▶  Repository  ──▶  Entity
    │                                              ▲
    └──▶ DTO ─────────────────────────────────────┘
             (toEntity / from 으로 엔티티와 오간다)
```

- 컨트롤러는 서비스와 DTO를 안다. 엔티티는 모른다
- 서비스는 리포지토리·엔티티·DTO를 안다. 컨트롤러는 모른다
- 리포지토리는 엔티티만 안다
- 엔티티는 아무것도 모른다

**화살표가 한 방향으로만 간다**는 것이 요점입니다. 아래층은 위층의 존재를 모르므로 위층을 바꿔도 아래가 흔들리지 않고, 아래를 바꾸면 위가 따라오는 방향만 남습니다. 서비스가 유일하게 엔티티와 DTO를 둘 다 아는 층이라는 것도 day05에서 적어 둔 그대로입니다. 두 세계가 겹치는 자리를 하나로 좁혀 두는 배치입니다.

### 1-7. 껍데기를 먼저 세우고 갈래를 하나씩 채우기

파일을 만든 순서를 보면 리포지토리 → 서비스 → 컨트롤러로 아래에서 위로 올라갑니다. 아래층이 무엇을 할 수 있는지 정해져야 위층이 부를 것을 적을 수 있기 때문입니다.

다만 세 층을 모두 채운 것이 아니라 **아홉 파일의 자리를 먼저 잡고, 등록 한 갈래만 위쪽부터 이어 놓은 상태**입니다. 컨트롤러에 `courseService.courseSave(courseDto)` 라고 적으면 아래층에 무엇을 만들어야 하는지가 이름과 매개변수로 정해집니다. 위에서 이름을 먼저 정하고 아래를 채우는 방식이라 이름이 층을 관통하고, 따라 읽을 때 같은 이름이 세 파일에 나타납니다.

이 방식은 층을 다 채우기 전까지는 빌드가 지나가지 않는 구간이 생깁니다. 위층이 부르는 이름이 아래층에 아직 없기 때문입니다. 갈래 하나를 컨트롤러부터 리포지토리까지 세로로 먼저 관통시키고 다음 갈래로 넘어가면 그 구간이 짧아집니다.

비워 둔 그 자리를 실제로 채운 결과가 이어지는 1-8·1-9입니다.

### 1-8. 비어 있던 서비스에 등록 갈래를 채우기

컨트롤러가 먼저 이름만 정해 둔 `courseSave` 의 몸통이 서비스에 들어왔습니다.

```java
public boolean courseSave(CourseDto courseDto) {
    CourseEntity courseEntity = courseDto.toEntity();              // 1. dto -> entity
    CourseEntity savedEntity = courseRepository.save(courseEntity); // 2. 저장
    if (savedEntity.getCourseId() >= 1)                             // 3. pk가 채워졌는지
        return true;
    return false;
}
```

세 줄이 하는 일을 나눠 보면 층이 그대로 드러납니다.

| 줄 | 하는 일 | 그 일을 아는 층 |
| --- | --- | --- |
| `courseDto.toEntity()` | 웹에서 온 그릇을 표의 그릇으로 바꾼다 | DTO가 스스로 |
| `courseRepository.save(...)` | 표에 줄을 넣는다 | 리포지토리 |
| `savedEntity.getCourseId() >= 1` | 결과를 참·거짓 하나로 줄인다 | 서비스 |

성공 판정을 **저장 결과의 PK로** 하는 배치가 요점입니다. `toEntity()` 는 PK를 비워 두고 만들었는데, `save()` 가 돌려주는 객체에는 DB가 채운 번호가 실려 있습니다. 즉 `save()` 에 넣은 객체와 돌려받은 객체를 같은 것으로 보지 않고 **돌려받은 쪽을 봐야 번호를 알 수 있다**는 것이 이 줄의 전제입니다.

번호가 채워졌다는 것은 곧 insert가 나갔다는 뜻이라 성공 신호로 쓸 수 있습니다. 다만 이 판정이 잡아내는 실패의 범위는 좁습니다 (2-6).

### 1-9. 목록 변환과 중첩 DTO 조립

두 번째로 세로로 관통한 갈래가 전체조회입니다. 컨트롤러 쪽에는 `@GetMapping("")` 이 하나 붙고, 반환 타입이 `List<CourseDto>` 로 잡힙니다. 앞머리(`/api/course`)는 등록 갈래와 같고 **HTTP 방식만 갈립니다** — 같은 자원에 대해 주소는 하나로 두고 동사를 방식으로 표현하는 REST의 기본 모양입니다.

| 방식 | 주소 | 하는 일 |
| --- | --- | --- |
| `POST` | `/api/course` | 과정 하나 등록 |
| `GET` | `/api/course` | 과정 전체 조회 |

서비스 쪽 몸통은 이렇습니다.

```java
public List<CourseDto> courseFindAll() {
    List<CourseEntity> courseEntities = courseRepository.findAll();
    List<CourseDto> courseDtos = new ArrayList<>();
    courseEntities.forEach((courseEntity) -> {
        CourseDto courseDto = CourseDto.from(courseEntity);
        courseEntity.getEnrollEntities().forEach((enroll) -> {
            StudentDto studentDto = StudentDto.from(enroll.getStudentEntity());
            courseDto.getStudentDtos().add(studentDto);
        });
        courseDtos.add(courseDto);
    });
    return courseDtos;
}
```

**앞 노트에서 "DTO 혼자서는 못 채운다"고 남겨 둔 자리가 여기서 채워집니다.** `CourseDto.from(courseEntity)` 은 과정 표에 있는 값만 채우고 학생 목록은 비운 채로 나옵니다. 그 빈 목록을 서비스가 관계를 타고 들어가 메웁니다.

관계를 몇 칸 타는지가 핵심입니다.

```
CourseEntity ──getEnrollEntities()──▶ EnrollEntity ──getStudentEntity()──▶ StudentEntity
   (과정)                                (수강)                              (학생)
                                                                              │
                                                                      StudentDto.from()
                                                                              ▼
                                                          courseDto.getStudentDtos().add(...)
```

과정에서 학생까지 **두 칸**입니다. 중간 표(수강)를 반드시 지나야 하는데, 앞서 다대다를 중간 엔티티로 풀어 둔 결과가 코드에 그대로 나타난 자리입니다. 표 설계에서 중간 표를 하나 세우면, 코드에서는 순회가 한 겹 늘어납니다.

바깥·안쪽 두 개의 `forEach` 가 하는 일도 성격이 다릅니다.

| 순회 | 도는 대상 | 만드는 것 |
| --- | --- | --- |
| 바깥 | 과정 목록 | 과정 DTO 한 개씩 |
| 안쪽 | 그 과정의 수강 목록 | 그 과정 DTO 안의 학생 DTO 목록 |

바깥이 결과 리스트의 **줄 수**를 정하고, 안쪽이 각 줄의 **깊이**를 채웁니다.

한 가지 더 눈에 띄는 것은 `courseDto.getStudentDtos().add(...)` 가 곧바로 통한다는 점입니다. `CourseDto` 의 목록 필드가 `= new ArrayList<>()` 로 선언 자리에서 초기화돼 있어 `getStudentDtos()` 가 `null` 이 아닌 빈 리스트를 돌려주기 때문입니다. **컬렉션 필드를 빈 값으로 초기화해 두면 쓰는 쪽에서 `null` 검사가 사라진다**는 관용이 여기서 값을 합니다 (2-8).

정리하면 이 메소드의 모양은 이렇습니다.

```
findAll() ─▶ 엔티티 목록 ─▶ [ from() 으로 한 겹 변환 ] ─▶ [ 관계 순회로 안쪽 채우기 ] ─▶ DTO 목록
                            (DTO가 할 수 있는 몫)          (서비스가 해야 하는 몫)
```

## 2. 추가로 알면 좋은 활용법

### 2-1. `@Autowired` 필드 주입과 생성자 주입의 갈림

지금 배치는 필드에 `@Autowired` 를 붙인 모양입니다. 같은 일을 생성자로 받을 수도 있습니다.

```java
@Service
@RequiredArgsConstructor
public class CourseService {
    private final CourseRepository courseRepository;
}
```

| 항목 | 필드 주입 (`@Autowired`) | 생성자 주입 (`final` + `@RequiredArgsConstructor`) |
| --- | --- | --- |
| 코드 길이 | 짧다 | 롬복 표시 한 줄이 더 붙는다 |
| `final` | 못 붙인다 (만든 뒤에 넣으므로) | 붙는다 — 만들어진 뒤 안 바뀐다 |
| 의존 개수 | 필드를 세어 봐야 안다 | 생성자 서명에 드러나 많아지면 눈에 띈다 |
| 테스트 | 스프링 없이 만들면 `null` 로 남는다 | 생성자로 직접 넣어 만들 수 있다 |
| 순환 참조 | 서버가 뜬 뒤에 드러날 수 있다 | 만드는 시점에 걸린다 |

실무에서는 생성자 주입을 기본으로 두는 편입니다. 다만 지금처럼 층 골격을 빠르게 세우는 자리에서는 필드 주입이 눈에 덜 걸리적거려서 먼저 쓰이곤 합니다. 어느 쪽이든 **한 프로젝트 안에서는 하나로 통일해 두는 편**이 읽기 낫습니다.

### 2-2. 계층별 표시 셋은 이름만 갈린 `@Component`

`@Controller`(그리고 그 합성인 `@RestController`)·`@Service`·`@Repository` 셋은 모두 `@Component` 를 품고 있습니다. 등록 결과는 같고 갈리는 것은 다음 정도입니다.

- 사람이 읽을 때 층이 이름으로 드러난다
- `@Repository` 는 DB 예외를 스프링 표준 예외(`DataAccessException` 계열)로 바꿔 준다
- AOP 대상을 층 단위로 고를 때 표시가 기준이 된다 (`@within(org.springframework.stereotype.Service)` 같은 표현)

셋을 아무렇게나 바꿔 붙여도 대개 돌아가지만, 그러면 표시가 알려 주던 정보가 사라집니다. 표시를 고르는 일은 기능 선택이 아니라 **이 클래스가 어느 층인지 적어 두는 일**에 가깝습니다.

### 2-3. 서비스가 트랜잭션의 자리가 되는 이유

지금 서비스는 비어 있지만, 곧 여러 리포지토리를 함께 부르는 메소드가 생깁니다. 수강신청 하나만 봐도 과정이 있는지 확인하고, 학생이 있는지 확인하고, 수강 줄을 만드는 세 단계가 한 묶음이어야 합니다. 중간에서 끊기면 어중간한 상태가 남습니다.

그 "한 묶음"을 정하는 자리가 서비스입니다. 컨트롤러는 요청 하나를 받는 자리라 묶음의 경계로 삼기에는 웹에 너무 붙어 있고, 리포지토리는 한 표만 다뤄서 여러 표에 걸친 묶음을 알 수 없습니다. `@Transactional` 이 관례적으로 서비스에 붙는 것은 이 사정 때문입니다.

읽기만 하는 메소드에는 `@Transactional(readOnly = true)` 를 붙여 두면 스냅샷을 안 만들어 부담이 줄고, 실수로 값을 바꿔도 `update` 가 나가지 않습니다.

### 2-4. 컨트롤러가 `boolean` 을 돌려줄 때 남는 한계

지금 등록 갈래의 반환 타입은 `boolean` 입니다. 다루기 간단하지만 화면 쪽에서 보면 정보가 하나뿐입니다.

- 저장은 됐는데 번호를 모른다 → 방금 만든 것을 보려면 조회를 한 번 더 보낸다
- 실패했는데 이유를 모른다 → 값이 잘못됐는지, 대상이 없는지, 서버가 터졌는지가 같은 `false`

`ResponseEntity` 로 상태 코드를 갈라 주거나, 저장된 DTO를 그대로 돌려주는 갈래가 있습니다. 후자는 `from()` 한 번으로 번호와 감사 필드까지 응답에 실려서 요청 한 번이 줄어듭니다.

### 2-5. 도메인이 늘 때 손대는 파일 수

이번 실습에서 도메인 하나에 붙는 파일은 엔티티·DTO·리포지토리·서비스·컨트롤러 다섯입니다. 도메인이 하나 늘면 다섯이 늘고, 그중 리포지토리는 거의 복사이며 컨트롤러가 가장 많이 갈립니다.

되풀이를 줄이는 방향은 늘 두 갈래입니다.

- 공통을 위로 올리기 — 제네릭 기반 공통 서비스·공통 컨트롤러를 두는 갈래. 줄어들지만 층이 한 겹 늘고 특수한 갈래가 생기면 도로 내려와야 한다
- 규약으로 대신하기 — 코드 생성이나 프레임워크 기능에 맡기는 갈래. `JpaRepository` 가 이미 그 갈래다

지금 규모에서는 손으로 다섯 벌을 쓰는 편이 읽기 쉽습니다. 되풀이가 눈에 거슬리기 시작하는 지점을 지나고 나서 골라도 늦지 않습니다.

### 2-6. 저장 결과를 참·거짓 하나로 줄일 때 사라지는 것

PK가 채워졌는지로 성공을 판정하는 방식은 짧지만, `false` 가 나오는 경우가 사실상 없습니다. 저장이 실패하면 `false` 가 돌아오는 것이 아니라 **예외가 던져지기** 때문입니다.

| 상황 | 실제로 일어나는 일 |
| --- | --- |
| 정상 저장 | PK가 채워져 `true` |
| 제약 위반(중복 키·`not null` 등) | `DataIntegrityViolationException` — `if` 까지 못 간다 |
| 연결 문제 | `DataAccessException` 계열 — 역시 못 간다 |

그래서 `boolean` 반환은 "성공/실패"를 나누는 값이라기보다 **"예외 없이 여기까지 왔다"는 표시**에 가깝습니다. 실패 갈래를 정말 다루려면 판정을 값이 아니라 예외 처리 쪽에 두게 됩니다 — `@RestControllerAdvice` 로 예외를 응답으로 바꾸거나, 저장 전에 조건을 확인해 도메인 예외를 직접 던지는 갈래입니다.

저장된 DTO를 돌려주는 갈래(2-4)와 견주면 이렇게 갈립니다.

| 반환 | 화면 쪽이 알 수 있는 것 |
| --- | --- |
| `boolean` | 됐다/안 됐다 |
| 저장된 DTO | 번호·감사 필드까지 — 방금 만든 것을 바로 그릴 수 있다 |

### 2-7. `forEach` 와 `stream().map()`

목록 변환은 두 표기로 적을 수 있습니다.

```java
// 1. 리스트를 미리 만들고 채우는 방식
List<CourseDto> dtos = new ArrayList<>();
entities.forEach(e -> dtos.add(CourseDto.from(e)));

// 2. 변환 결과를 그대로 모으는 방식
List<CourseDto> dtos = entities.stream()
        .map(CourseDto::from)
        .toList();
```

| 표기 | 성질 |
| --- | --- |
| `forEach` + `add` | 중간에 조건을 넣거나 다른 값을 함께 채우기 쉽다. 담을 리스트를 먼저 선언한다 |
| `stream().map()` | "무엇을 무엇으로 바꾼다"만 남아 짧다. 변환 도중 곁가지 작업을 넣기 어렵다 |

중첩 조립처럼 **변환 뒤에 손을 더 대야 하는 흐름**은 `forEach` 쪽이 자연스럽고, 단순히 한 겹만 바꾸는 흐름은 `stream` 쪽이 짧습니다. 표기 선택보다 중요한 것은 한 프로젝트 안에서 섞어 쓰지 않는 쪽이 읽기 편하다는 점입니다.

### 2-8. 컬렉션 필드 초기화와 `@Builder.Default`

```java
private List<StudentDto> studentDtos = new ArrayList<>();
```

선언 자리 초기화는 `null` 검사를 없애 주지만, `@Builder` 와 함께 두면 한 가지 걸리는 자리가 있습니다. **빌더로 만든 객체는 이 초기값을 쓰지 않고 `null` 로 남습니다.** 빌더가 채우지 않은 필드를 기본값이 아니라 타입의 기본(`null`)으로 두기 때문입니다.

```java
@Builder.Default
private List<StudentDto> studentDtos = new ArrayList<>();
```

`@Builder.Default` 를 붙이면 빌더로 만들 때도 초기값이 적용됩니다. 컬렉션 필드를 가진 DTO를 빌더로 만들어 놓고 바로 `add` 를 부르는 흐름이라면 **어느 경로로 만들어졌는지에 따라 결과가 갈리지 않도록** 짝을 맞춰 두는 편이 안전합니다.

### 2-9. 층을 관통하는 이름을 정하는 기준

컨트롤러가 부를 이름을 먼저 적으면 그 이름이 서비스·리포지토리까지 그대로 내려갑니다(1-7). 그래서 이름 규칙은 한 곳의 취향이 아니라 **세 파일에 동시에 남는 결정**이 됩니다.

- 자바 식별자에는 한글도 쓸 수 있지만, 팀 규약·도구 호환을 생각하면 영문으로 통일해 두는 편이 무난합니다
- 층마다 이름을 다르게 두면(`courseSave` ↔ `save` ↔ `insert`) 따라 읽을 때 매번 대응을 확인해야 합니다. 한 갈래는 한 이름으로 관통시키는 편이 읽기 쉽습니다
- 스프링 데이터가 쓰는 어휘(`findAll`·`findById`·`save`)를 위층에서도 그대로 쓰면 이름만 보고 무엇이 나가는지 짐작이 됩니다

## 3. 더 나아가 알면 좋은 것

### 3-1. 계층 축과 도메인 축, 패키지를 나누는 두 갈래

지금 배치는 계층 축(layered) 입니다. 도메인 축(package by feature)은 이렇게 됩니다.

```
day07/practice/
├── course/     CourseEntity · CourseDto · CourseRepository · CourseService · CourseController
├── student/    …
└── enroll/     …
```

| 축 | 좋은 점 | 걸리는 점 |
| --- | --- | --- |
| 계층 | 같은 층을 한 번에 훑는다. 층 규칙을 지키기 쉽다 | 기능 하나를 고치려면 폴더 여럿을 연다 |
| 도메인 | 기능 하나가 폴더 하나에 모인다. 떼어 내기 쉽다 | 층 규칙이 폴더로 안 드러나 섞이기 쉽다 |

도메인이 적고 층을 배우는 단계에서는 계층 축이 눈에 잘 들어옵니다. 도메인이 늘고 팀이 나뉘면 도메인 축이 손이 덜 갑니다. 나중에 서비스를 쪼갤 생각이 있다면 도메인 축이 경계선을 미리 그어 두는 셈이 됩니다.

### 3-2. 층을 나눠도 얇은 서비스가 남는 문제

컨트롤러가 서비스를 부르고 서비스가 리포지토리를 그대로 부르기만 하는 메소드는 층 하나가 통과 지점에 그칩니다. 층을 나눈 값어치가 안 나오는 자리입니다.

그렇다고 서비스를 없애면 판정이 컨트롤러로 올라가고, 그러면 웹과 규칙이 한 클래스에 섞입니다. 대개는 **얇은 서비스를 감수하고 자리를 남겨 둡니다** — 규칙이 생겼을 때 넣을 곳이 이미 있기 때문입니다. 얇음 자체가 문제라기보다, 지금 얇은 이유가 아직 규칙을 안 적어서인지 정말 넘기기만 하는 갈래여서인지 갈라 보는 편이 낫습니다.

### 3-3. 컨트롤러가 여럿일 때 응답 모양을 맞추기

도메인마다 컨트롤러가 생기면 응답 모양이 갈릴 여지가 늘어납니다. 어떤 갈래는 `boolean`, 어떤 갈래는 DTO, 어떤 갈래는 `ResponseEntity` 가 되면 화면 쪽에서 매번 다르게 받아야 합니다.

맞추는 갈래로는 공통 응답 봉투(`{ code, message, data }`)를 두는 방법과, 상태 코드로만 갈라 주고 본문은 데이터만 담는 방법이 있습니다. 전자는 화면 쪽 처리가 하나로 모이고, 후자는 HTTP 규약을 그대로 쓰게 됩니다. `@RestControllerAdvice` + `@ExceptionHandler` 로 예외 응답을 한 자리에 모으는 것은 어느 쪽을 골라도 필요해집니다.

### 3-4. 중첩 조립이 목록 앞에서 커지는 방향

전체조회의 안쪽 순회(1-9)는 과정 수만큼 반복됩니다. 지연 로딩이 걸려 있으면 `getEnrollEntities()` 를 처음 건드릴 때 수강 조회가 나가고, 그 안에서 `getStudentEntity()` 를 건드릴 때 학생 조회가 또 나갑니다. 과정이 10개이고 과정마다 수강이 5줄이면 쿼리 수가 이렇게 자랍니다.

```
과정 조회 1
  + 과정마다 수강 조회 10
    + 수강마다 학생 조회 50
```

**관계를 한 겹 더 타면 곱셈이 한 겹 더 붙는다**는 것이 요점입니다. 앞 노트에서 정리한 N+1이 두 단계가 된 모양이고, 푸는 방향도 같습니다 — 조회 시점에 필요한 관계를 함께 읽어 오는 것입니다.

```java
@Query("select distinct c from CourseEntity c " +
       "join fetch c.enrollEntities e join fetch e.studentEntity")
List<CourseEntity> findAllWithStudents();
```

`distinct` 가 붙는 이유는 조인 결과가 과정 하나를 수강 줄 수만큼 되풀이해 내놓기 때문입니다. 다만 컬렉션을 `join fetch` 하면 페이징이 DB가 아니라 메모리에서 처리되는 제약이 따라오므로, **목록이 커질 화면이라면 조립 방식 자체를 다시 고르게 됩니다** — 과정만 페이징으로 읽고 학생 목록은 별도 조회로 한 번에 모아 붙이는 갈래가 그중 하나입니다.

### 3-5. 조회 전용 흐름을 표시해 두기

전체조회처럼 값을 바꾸지 않는 메소드는 표시로 그 성질을 적어 둘 수 있습니다.

```java
@Transactional(readOnly = true)
public List<CourseDto> courseFindAll() { … }
```

붙여서 얻는 것이 둘입니다. 하나는 변경 감지를 위한 스냅샷을 만들지 않아 목록이 클수록 부담이 줄어드는 것이고, 다른 하나는 **관계를 타고 들어가는 동안 영속성 컨텍스트가 열려 있는 것이 보장**된다는 점입니다. 중첩 조립은 지연 로딩에 기대는 코드라 컨텍스트가 닫힌 뒤에 관계를 건드리면 그 자리에서 걸립니다. 변환을 서비스 안에서 끝내는 배치가 이 사정과 짝입니다.

### 3-6. 다음에 볼 키워드

- `@Transactional` — 붙일 자리, `readOnly`, 자기 호출에 안 먹는 이유
- `@Valid` · `@NotBlank` · `@Min` — DTO 검사를 본문 앞으로 당기기
- `@RestControllerAdvice` · `@ExceptionHandler` — 예외 응답 한 자리에 모으기
- `ResponseEntity` · `HttpStatus` — 상태 코드로 결과 갈라 주기
- 서비스 인터페이스와 구현 분리 — 나눌 값이 있는 자리와 없는 자리
- 패키지 바이 피처 · 헥사고날 · 포트와 어댑터
- `@Query` · 메소드 이름 쿼리 — 리포지토리가 복사에서 벗어나는 지점
- `join fetch` · `@EntityGraph` · `distinct` — 컬렉션을 함께 읽을 때의 중복과 페이징 제약
- `@Builder.Default` — 빌더 경로와 생성자 경로에서 기본값이 갈리는 자리
- `stream().map().collect()` 와 `Collectors.groupingBy` — 목록을 모아 붙이는 표기
- `OpenSessionInView` 설정과 지연 로딩 예외가 어디서 나는지

## 실습 파일

- `2026B_Spring/springweb/src/main/java/day07/practice/model/repository/CourseRepository.java` (**리포지토리 층의 최소 형태** — `extends JpaRepository<CourseEntity, Integer>` 한 줄이 몸통 없이 CRUD 메소드를 물려받는 자리, `@Repository` 가 계층을 이름으로 드러내고 DB 예외를 표준 예외로 바꿔 주는 점, 폴더가 갈리며 엔티티를 `import` 하게 되어 의존이 파일 머리에 드러나는 자리)
- `2026B_Spring/springweb/src/main/java/day07/practice/model/repository/StudentRepository.java` (**제네릭 두 자리만 갈리는 복사** — 도메인이 늘어도 리포지토리 층은 엔티티 타입과 인터페이스 이름만 바뀐다는 실측)
- `2026B_Spring/springweb/src/main/java/day07/practice/model/repository/EnrollRepository.java` (**중간 엔티티도 자기 리포지토리를 갖는 자리** — 중간 표라고 부모를 통해서만 다루는 것이 아니라 그 자체가 표 하나라 열쇠로 찾고 저장하는 통로가 필요하다는 점, 상태를 바꾸는 갈래가 이 리포지토리를 지나게 되는 자리)
- `2026B_Spring/springweb/src/main/java/day07/practice/service/CourseService.java` (**서비스 층의 최소 형태이자 두 갈래를 채운 자리** — `@Service` 가 `@Component` 와 결과는 같고 이름이 계층을 말해 주는 점, `@Autowired` 필드 주입으로 리포지토리를 받아 `new`·`getInstance()` 가 사라지는 자리, 서비스가 컨트롤러를 모르므로 파일만 보고는 HTTP로 불리는지 알 수 없다는 점 / 등록 갈래에서 `toEntity()`→`save()`→`getCourseId() >= 1` 세 줄이 각각 DTO·리포지토리·서비스의 몫으로 갈리고 성공 판정을 **돌려받은** 엔티티의 PK로 한다는 전제, 그 `boolean` 이 잡는 실패 범위가 좁은 이유 / 전체조회 갈래에서 `findAll()` 결과를 `from()` 으로 한 겹 변환한 뒤 과정→수강→학생 **두 칸**을 순회해 `CourseDto` 의 빈 학생 목록을 메우는 조립, 바깥 순회가 줄 수를·안쪽 순회가 깊이를 정하는 대비, `getStudentDtos().add(...)` 가 바로 통하는 근거가 컬렉션 필드의 선언 자리 초기화라는 점)
- `2026B_Spring/springweb/src/main/java/day07/practice/service/StudentService.java` (**층 골격만 세워 둔 상태** — 몸통이 비어 있어도 빈은 등록되고 주입도 도는 자리와 자리만 잡아 둔 단계라는 뜻)
- `2026B_Spring/springweb/src/main/java/day07/practice/service/EnrollService.java` (**트랜잭션 경계가 놓일 자리** — 수강신청이 과정 확인·학생 확인·수강 줄 생성 세 단계라 한 묶음이 필요해지고, 컨트롤러는 웹에 붙어 있고 리포지토리는 한 표만 알아 서비스가 묶음의 경계가 되는 사정)
- `2026B_Spring/springweb/src/main/java/day07/practice/controller/CourseController.java` (**세로로 관통한 갈래 하나** — 클래스 `@RequestMapping` 앞머리와 `@PostMapping("")` 이 이어 붙어 `POST /api/course` 한 자리가 되는 구조, `@RequestBody` 로 DTO를 받아 서비스로 넘기는 세 줄 모양, 위층에서 부를 이름을 먼저 적으면 아래층에 무엇을 만들지가 이름과 매개변수로 정해지는 순서, `boolean` 반환이 남기는 한계, 뒤이어 `@GetMapping("")` 이 붙으며 같은 주소 `/api/course` 가 **방식으로만 갈리는** 두 자리가 되고 조회 갈래의 반환 타입이 `List<CourseDto>` 로 잡히는 대비)
- `2026B_Spring/springweb/src/main/java/day07/practice/controller/StudentController.java` (**도메인마다 주소 앞머리를 갈라 두는 배치** — 앞머리가 겹치면 메소드 주소+방식이 충돌할 여지가 생기고 그 충돌은 요청 때가 아니라 서버가 뜰 때 걸린다는 점)
- `2026B_Spring/springweb/src/main/java/day07/practice/controller/EnrollController.java` (**아직 갈래가 없는 컨트롤러** — 매핑 메소드가 없어도 빈으로 등록되는 자리와 주소 앞머리 표기를 한 프로젝트 안에서 하나로 정해 두는 편이 나은 이유)
- `2026B_Spring/springweb/src/main/java/day07/practice/model/entity`, `model/dto` (**재편의 결과** — 엔티티·DTO가 `model` 밑으로 들어가며 "데이터를 담고 꺼내는 층"과 "웹 요청을 아는 층"이 폴더로 갈리는 자리, 패키지 선언이 폴더 경로와 같은 값이어야 한다는 규칙)

## 관련 노트

[[Spring MOC]] · [[Spring day07 연관 엔티티를 DTO로 펴기]] · [[KDT_2026 학습 지도]]
