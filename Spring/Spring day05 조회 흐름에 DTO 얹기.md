---
출처: Claude 분석
원본: KDT_2026/2026B_Spring/springweb/src/main/java/day05/TestController.java, springweb/src/main/java/day05/TestService.java, springweb/src/main/java/day05/TestRepository.java
작성일: 2026-09-03
tags: [학습, java]
---

# Spring day05 — 조회 흐름에 DTO 얹기

> 실습 파일: `2026B_Spring/springweb/src/main/java/day05/TestController.java`, `TestService.java`, `TestRepository.java`
> 허브: [[Spring MOC]] · 이전: [[Spring day05 DTO 변환과 초기 데이터 적재]]

[[Spring day05 DTO 변환과 초기 데이터 적재]] 에서 `toEntity()` 와 `from()` 두 방향의 변환 메소드를 만들어 뒀다. 만들어 두기만 하고 부르는 자리는 없었다. **이번은 그 메소드가 실제로 불리는 자리를 세 계층에 배치하는 실습이다.**

전체조회 한 갈래를 끝까지 이어 본다.

```
요청  GET /test
      Controller  →  Service  →  Repository  →  DB
                                    List<TestEntity>
                     from() 으로 한 줄씩 변환
      List<TestDto>  ←  응답 JSON 배열
```

| 자리 | 하는 일 |
| --- | --- |
| `TestRepository` | 엔티티와 열쇠 타입만 적어 두기 (1-1) |
| `TestService.findAll()` | 엔티티 목록을 DTO 목록으로 바꾸기 (1-2·1-3) |
| `TestController.전체조회()` | 주소를 잇고 DTO 목록을 돌려주기 (1-4) |
| `TestService.save()` | 반대 방향 — 들어온 DTO를 엔티티로 (1-5) |

## 1. 배운 내용

### 1-1. 리포지토리 — 엔티티와 열쇠 타입만 적어 두기

아래층부터 본다.

```java
public interface TestRepository
        extends JpaRepository<TestEntity, Integer> {
}
```

[[Spring day04 JPA 엔티티와 리포지토리]] 에서 정리한 모양 그대로다. 제네릭 두 자리에 **다룰 엔티티와 그 엔티티의 PK 타입**을 적는다. `TestEntity` 의 `no` 가 `Integer` 이므로 뒤 자리도 `Integer` 다.

몸통에 아무것도 안 적어도 `findAll`·`findById`·`save`·`deleteById` 가 물려 내려온다. 이번 실습에서 실제로 쓰는 것은 `findAll()` 하나다.

`class` 가 아니라 `interface` 인 것이 조건이다. **구현을 물려받는 자리라 구현을 적을 수 있는 형태면 안 된다.** 인터페이스는 "무엇을 할 수 있다"는 규약만 담는 자리이고, 그 규약을 보고 스프링이 시작할 때 구현 객체를 만들어 빈으로 등록한다.

같은 맥락에서 **인터페이스에는 상태(멤버변수)를 두지 않는다.** 인터페이스에 적은 필드는 자동으로 `public static final` 이 되어 상수가 되고, 인스턴스마다 갖는 값이 아니게 된다. 의존 객체를 들고 있어야 하는 자리는 인터페이스가 아니라 클래스(서비스·컨트롤러) 쪽이다.

| | 인터페이스 | 클래스 |
| --- | --- | --- |
| 담는 것 | 규약 | 구현과 상태 |
| 필드 | 상수만 | 인스턴스마다 값 |
| 이 실습의 자리 | `TestRepository` | `TestService`·`TestController` |

### 1-2. 서비스 — 엔티티 목록을 DTO 목록으로 바꾸기

가운데 층이 이번의 요점이다.

```java
@Service
public class TestService {
    @Autowired
    private TestRepository testRepository;

    // 1. 전체조회
    public List<TestDto> findAll() {
        List<TestEntity> entities = testRepository.findAll();
        // 2. 모든 엔티티 -> DTO 변환하기
        List<TestDto> list = new ArrayList<>();
        entities.forEach((entity) -> {
            TestDto dto = TestDto.from(entity);
            list.add(dto);
        });
        // 3. 반환
        return list;
    }
}
```

**메소드의 반환 타입이 `List<TestDto>` 라는 것이 경계선이다.** 리포지토리에서 나온 것은 `List<TestEntity>` 인데, 이 메소드를 나갈 때는 DTO 목록이 된다. [[Spring day05 DTO 변환과 초기 데이터 적재]] 에 적어 둔 "컨트롤러가 다루는 타입은 DTO뿐"이 서명 하나로 지켜지는 자리다.

세 단계가 주석 번호대로 나뉘어 있다.

```
① 꺼내기    리포지토리에서 엔티티 목록을 받는다
② 바꾸기    한 줄씩 DTO로 옮긴다
③ 돌려주기  DTO 목록을 반환한다
```

②가 서비스에 있는 것이 배치의 핵심이다. **엔티티가 살아 있는 범위가 이 메소드 안으로 닫힌다.** 컨트롤러는 엔티티라는 타입을 아예 보지 않으므로, 표가 바뀌어도 컨트롤러를 열어 볼 이유가 없다.

`@Autowired` 로 리포지토리를 받는 것은 [[Spring day03 애노테이션과 리플렉션]] 의 DI 그대로다. 필드에 직접 붙이는 갈래이고, `final` + `@RequiredArgsConstructor` 로 생성자 주입을 받는 갈래와 갈린다(2-5).

### 1-3. forEach와 람다로 목록 훑기

변환 부분만 떼어 보면 이렇다.

```java
List<TestDto> list = new ArrayList<>();

entities.forEach((entity) -> {
    TestDto dto = TestDto.from(entity);
    list.add(dto);
});
```

`forEach` 는 컬렉션이 물려받은 메소드로, **원소 하나하나에 대해 넘겨받은 코드 조각을 실행한다.** 그 코드 조각을 적는 표기가 람다다.

```
리스트객체.forEach( (반복변수) -> { 반복변수로 할 일 } );
```

`for` 문과 견주면 갈리는 지점이 있다.

| | `for (TestEntity e : entities)` | `entities.forEach(e -> …)` |
| --- | --- | --- |
| 반복을 누가 도나 | 내가 적은 반복문 | 컬렉션이 안에서 돈다 |
| 적는 것 | 도는 방법 + 할 일 | 할 일만 |
| 중간에 빠져나오기 | `break`·`continue` | 안 된다 |

**"어떻게 돌지"가 아니라 "무엇을 할지"만 적는 쪽**으로 옮겨 간 표기다. 대신 중간에 멈출 수 없어서, 조건에 맞는 것만 골라 내거나 하나를 찾으면 그만두는 자리에는 안 맞는다.

`(entity) -> { … }` 에서 괄호 안이 반복변수의 이름이다. 타입을 안 적어도 되는 것은 컴파일러가 `List<TestEntity>` 의 원소 타입으로 짐작하기 때문이다. 매개변수가 하나면 괄호도 생략할 수 있고, 본문이 한 줄이면 중괄호와 세미콜론도 줄어든다.

```java
entities.forEach(entity -> list.add(TestDto.from(entity)));
```

**바깥에 만들어 둔 `list` 를 람다 안에서 쓰는 구조**도 짚어 둘 만하다. 람다는 자기 밖의 지역변수를 읽을 수 있는데, 그 변수 자체를 다시 대입하는 것은 안 된다(사실상 final). 여기서는 `list` 라는 참조는 그대로 두고 그 안에 원소만 더하므로 걸리지 않는다.

같은 일을 스트림으로 적으면 빈 리스트를 미리 만드는 단계가 없어진다(2-1).

### 1-4. 컨트롤러 — 반환 타입이 DTO 목록인 자리

맨 위층은 짧다.

```java
@RestController
public class TestController {
    @Autowired
    private TestService testService;

    // 1. 전체조회
    @GetMapping("/test")
    public List<TestDto> 전체조회() {
        return testService.findAll();
    }
}
```

[[Spring day04 REST 컨트롤러 CRUD 골격]] 에서 정리한 "컨트롤러는 넘기고 받고 돌려주는 세 줄"이 한 줄로까지 줄어든 모양이다. **판정할 것이 없으면 줄일 것도 없다.**

반환 타입이 `List<TestDto>` 라서 응답은 JSON 배열이 된다. 배열의 원소 하나하나는 DTO의 getter가 만드는 키를 갖는다.

```json
[
  { "no": null, "name": "코카콜라", "descri": "…", "price": 1000, "createDate": "…", "updateTime": "…" },
  …
]
```

**엔티티가 아니라 DTO의 필드 이름이 응답 키가 된다**는 것이 갈라 둔 값어치가 눈에 보이는 자리다. 표 컬럼을 바꿔도 DTO를 그대로 두면 화면 쪽 코드는 손댈 것이 없다.

`@GetMapping("/test")` 하나만 붙어 있고 클래스 레벨 `@RequestMapping` 은 없다. 매핑이 하나뿐이라 아직 공통 앞머리를 뽑을 필요가 없는 상태다. 갈래가 늘면 클래스로 올리게 된다(2-6).

메소드 이름이 한글인 것은 자바가 식별자에 유니코드를 허용하기 때문이다. **주소 매핑은 표시가 정하므로 메소드 이름은 요청 처리에 관여하지 않는다.** 다만 팀으로 넘어가면 파일 인코딩·도구 호환 때문에 영문으로 맞추는 편이 무난하다.

### 1-5. 저장 방향은 반대로 흐른다

조회의 반대 방향도 자리를 잡아 뒀다.

```java
// 2. 저장
public boolean save(TestDto testDto) {
    // 1. dto --> entity 변환함수 : toEntity 함수
    TestEntity testEntity = testDto.toEntity();
    …
}
```

**받는 타입이 DTO이고 안에서 엔티티로 바꾼다.** 조회가 "엔티티 → DTO"였다면 이쪽은 "DTO → 엔티티"이고, 부르는 메소드도 `from()` 이 아니라 `toEntity()` 다.

| | 조회 | 저장 |
| --- | --- | --- |
| 들어오는 것 | (없음) | `TestDto` |
| 변환 메소드 | `TestDto.from(entity)` | `dto.toEntity()` |
| 나가는 것 | `List<TestDto>` | 저장 결과 |
| 변환이 도는 방향 | 서비스 → 컨트롤러 | 컨트롤러 → 서비스 |

이어서 채울 자리는 `testRepository.save(testEntity)` 다. [[Spring day04 JPA 엔티티와 리포지토리]] 에 적어 둔 대로 `save` 는 영속된 엔티티를 돌려주므로, DB가 채운 번호를 그 자리에서 확인할 수 있다. `toEntity()` 가 `no` 를 안 옮기는 덕분에 PK가 비어 있고, 그래서 `insert` 로 갈린다.

돌려주는 타입을 `boolean` 으로 둘지 저장된 DTO로 둘지는 갈림이 있다(2-4).

### 1-6. 세 계층을 한 줄로 놓고 보기

이번 실습에서 각 계층이 아는 타입이 갈려 있다.

| 계층 | 아는 타입 | 모르는 타입 |
| --- | --- | --- |
| Controller | `TestDto` | `TestEntity` |
| Service | 둘 다 | — |
| Repository | `TestEntity` | `TestDto` |

**엔티티를 아는 범위가 서비스 아래로 닫히고, DTO를 아는 범위가 서비스 위로 열린다.** 서비스가 두 세계가 겹치는 유일한 자리이고, 그래서 변환 메소드를 부르는 자리도 서비스다.

```
Controller   [ DTO ]
                ↕     ← 여기서 변환한다
Service      [ DTO | Entity ]
                ↕
Repository   [ Entity ]
```

day04까지는 엔티티가 컨트롤러까지 올라왔다. 그때 적어 둔 문제(표의 모양이 곧 응답의 모양이 된다)가 이 배치로 실제로 없어진다. **변환 메소드를 만든 것이 절반이고, 부르는 자리를 정한 것이 나머지 절반이다.**

## 2. 추가로 알면 좋은 활용법

### 2-1. 스트림으로 같은 변환 적기

빈 리스트를 만들어 두고 채우는 대신, 목록을 통째로 바꾸는 표기가 있다.

```java
return testRepository.findAll().stream()
        .map(TestDto::from)
        .toList();
```

| | `forEach` + `add` | `stream().map()` |
| --- | --- | --- |
| 빈 리스트 | 미리 만든다 | 필요 없다 |
| 하는 일 | 원소마다 실행 | 원소를 바꿔 새 목록 |
| 결과 | 바깥 변수에 쌓인다 | 그 자리에서 반환 |

`TestDto::from` 은 `entity -> TestDto.from(entity)` 를 줄여 적은 것(메소드 참조)이다. **매개변수를 그대로 넘기기만 할 때** 쓸 수 있는 표기다.

`.toList()` 는 자바 16부터 쓸 수 있고, 그 전에는 `.collect(Collectors.toList())` 로 적는다. 앞엣것이 돌려주는 목록은 값을 바꿀 수 없다는 갈림이 있다.

### 2-2. 변환을 어느 계층에서 끝낼까

변환 자리를 컨트롤러로 올릴 수도 있다.

| 배치 | 서비스가 돌려주는 것 | 갈림 |
| --- | --- | --- |
| 서비스에서 변환 (이번) | `List<TestDto>` | 컨트롤러가 엔티티를 모른다 |
| 컨트롤러에서 변환 | `List<TestEntity>` | 컨트롤러가 엔티티를 알게 된다 |

뒤쪽은 지연 로딩이 걸리기 시작하면 문제가 커진다. **트랜잭션이 끝난 뒤에 엔티티의 연관 필드를 건드리면 읽어 올 수 없기 때문**이다. 서비스 안에서 변환을 끝내 두면 컨트롤러가 받는 것은 이미 값이 복사된 객체라 그 자리가 안 생긴다.

### 2-3. 조회 전용이라고 적어 두기 — @Transactional(readOnly = true)

조회만 하는 메소드에는 표시를 붙여 둘 수 있다.

```java
@Transactional(readOnly = true)
public List<TestDto> findAll() { … }
```

**변경 감지(더티 체킹)를 위한 스냅샷을 안 만들므로 메모리와 시간이 준다.** 실수로 값을 바꿔도 `update` 가 안 나간다는 것도 안전 쪽으로 붙는 값어치다. 조회 메소드에 기본으로 붙여 두는 편이 무난하다.

### 2-4. 저장이 무엇을 돌려줄까

`boolean` 은 성공 여부만 남긴다.

| 반환 | 화면에서 할 수 있는 일 |
| --- | --- |
| `boolean` | 성공·실패 판정 |
| 저장된 DTO | 번호까지 받아 바로 상세로 이동 |
| `ResponseEntity<TestDto>` | 201 상태 코드와 함께 |

`save` 가 영속된 엔티티를 돌려주므로 **번호를 받아 DTO로 바꿔 돌려주는 데 드는 비용이 거의 없다.** `boolean` 으로 줄이면 방금 만든 자원을 다시 찾는 요청이 한 번 더 필요해지는 자리가 생긴다.

### 2-5. @Autowired 필드 주입과 생성자 주입

받는 방법이 두 갈래다.

```java
// 필드 주입
@Autowired
private TestService testService;

// 생성자 주입
private final TestService testService;   // + @RequiredArgsConstructor
```

| | 필드 주입 | 생성자 주입 |
| --- | --- | --- |
| 적는 양 | 짧다 | 표시 하나 더 |
| `final` | 못 붙인다 | 붙는다 |
| 테스트에서 갈아 끼우기 | 리플렉션이 필요 | 생성자로 넣으면 된다 |
| 의존이 몇 개인지 | 필드를 세어 봐야 | 생성자 서명에 드러난다 |

**바뀌면 안 되는 값을 `final` 로 잠글 수 있는가**가 가장 큰 갈림이다. 스프링 쪽 권장도 생성자 주입이고, 의존이 하나뿐이면 표시 없이 생성자만 적어도 주입된다.

### 2-6. 갈래가 늘 때의 주소 배치

지금은 매핑이 하나라 `@GetMapping("/test")` 만 있다. CRUD 네 갈래가 붙으면 앞머리가 되풀이된다.

```java
@RestController
@RequestMapping("/test")
public class TestController {
    @GetMapping("")        public List<TestDto> findAll() { … }
    @PostMapping("")       public boolean save(@RequestBody TestDto dto) { … }
    @PutMapping("")        public boolean update(@RequestBody TestDto dto) { … }
    @DeleteMapping("/{no}") public boolean delete(@PathVariable Integer no) { … }
}
```

**주소는 자원을 가리키고 방식이 무엇을 할지 말한다.** 앞머리를 클래스로 올려 두면 주소 체계를 한 자리에서 바꿀 수 있다.

### 2-7. 목록이 커질 때

`findAll()` 은 표의 모든 줄을 읽어 온다. 줄이 늘면 그대로 부담이 된다.

```java
public Page<TestDto> findAll(Pageable pageable) {
    return testRepository.findAll(pageable).map(TestDto::from);
}
```

`Page` 는 `map` 을 가지고 있어 **쪽 정보를 유지한 채 안의 타입만 바꾼다.** 전체 개수·쪽 번호가 함께 실려 나가므로 화면에서 쪽 나누기를 그릴 수 있다.

### 2-8. 목록이 비었을 때

`findAll()` 은 결과가 없으면 빈 리스트를 돌려준다. `null` 이 아니라 빈 리스트라 **받는 쪽에서 검사 없이 그대로 훑을 수 있다.** 변환 코드도 원소가 없으면 한 번도 안 돌고 빈 목록이 나간다.

응답은 `[]` 가 되고, 화면 쪽에서는 길이가 0인 배열로 받는다. "없음"을 굳이 오류로 만들지 않는 편이 목록 조회에서는 다루기 쉽다.

### 2-9. 변환이 비어 보일 때 보는 순서

응답 JSON에 값이 `null` 로 찍히면 훑어 볼 자리가 정해져 있다.

```
① from() 이 그 필드를 옮기고 있는가
② 엔티티 쪽에 getter가 있는가          (@Getter·상속받은 자리 포함)
③ DB에 값이 들어 있는가                (초기화 SQL이 돌았는가)
④ DTO 필드 이름과 화면에서 꺼내는 키가 같은가
```

**변환 메소드가 옮기지 않은 필드는 조용히 `null` 로 남는다.** 빌더가 빠뜨린 값을 막지 않는다는 성질이 여기서 드러나는 자리다.

## 3. 더 나아가 알면 좋은 것

### 3-1. forEach와 스트림이 갈리는 지점

`forEach` 는 돌려주는 값이 없다(`void`). 그래서 결과를 남기려면 바깥 변수가 필요하다. 스트림은 각 단계가 다시 스트림을 돌려주므로 이어 붙일 수 있다.

| 갈래 | 성질 |
| --- | --- |
| `forEach` | 부수 효과(바깥을 바꾸기)로 결과를 남긴다 |
| `map`·`filter` | 원본을 두고 새 값을 만든다 |
| `collect`·`toList` | 이어 온 것을 모아 끝낸다 |

**여러 사람이 동시에 도는 상황(병렬 스트림)에서는 바깥 변수를 함께 고치는 방식이 위험해진다.** 스트림 쪽 표기가 권장되는 이유가 짧아서만은 아니다.

### 3-2. 변환을 아예 안 하는 갈래 — 프로젝션

엔티티를 통째로 읽어 일부만 옮겨 담는 것이 낭비인 자리가 있다.

```java
public interface TestSummary {
    String getName();
    Integer getPrice();
}

List<TestSummary> findAllBy();
```

**필요한 컬럼만 `select` 하므로 읽는 양이 준다.** 영속성 컨텍스트가 관리하지 않는 객체라 더티 체킹은 안 걸린다 — 읽기 전용 목록에 어울린다.

### 3-3. 목록 하나에 쿼리가 여러 번 나갈 때 — N+1

연관관계를 매핑하기 시작하면, 목록을 한 번 읽은 뒤 원소마다 연관을 읽는 쿼리가 더 나갈 수 있다.

```
findAll()          →  select * from test              (1번)
변환하며 연관 접근  →  select … where … = ?  × 줄 수   (N번)
```

**변환 코드는 그대로인데 나가는 쿼리가 줄 수에 비례해 는다.** `fetch join`·`@EntityGraph` 로 한 번에 읽어 오거나, 애초에 필요한 값만 프로젝션으로 읽는 갈래로 다룬다. 로그에 찍히는 SQL 개수를 세어 보는 것이 가장 빠른 확인이다.

### 3-4. 컨트롤러만 따로 검사하기

계층이 갈려 있으면 위층만 떼어 검사할 수 있다.

```java
@WebMvcTest(TestController.class)
class TestControllerTest {
    @MockBean TestService testService;   // 서비스는 가짜로
    …
}
```

**서비스가 인터페이스든 클래스든 밖에서 넣어 줄 수 있는 구조라야 이것이 된다.** 생성자 주입을 권하는 이유(2-5)가 검사 자리에서 실제로 값어치를 내는 지점이다.

### 3-5. 다음에 볼 키워드

- `stream()`·`map`·`filter`·`collect` 와 메소드 참조
- `@Transactional(readOnly = true)` 와 조회 전용 트랜잭션
- `Page`·`Pageable`·`Sort` 로 목록에 쪽 나누기 얹기
- `@Valid`·`@RequestBody` 로 저장 요청 값 검사하기
- `ResponseEntity` 로 상태 코드까지 돌려주기
- 인터페이스 프로젝션·`@Query` 생성자 표현식
- `fetch join`·`@EntityGraph` 와 N+1
- `@WebMvcTest`·`@DataJpaTest` 로 계층별 검사하기

## 실습 파일

- `2026B_Spring/springweb/src/main/java/day05/TestRepository.java` (엔티티와 열쇠 타입만 적어 두기 — `extends JpaRepository<TestEntity, Integer>` 의 제네릭 두 자리가 다룰 엔티티와 PK 타입이고 `@Id` 필드 타입과 맞아야 하는 점, 몸통이 비어 있어도 `findAll`·`save` 등이 물려 내려오는 구조와 이번에 실제로 쓰는 것은 `findAll()` 하나라는 점, `class` 가 아니라 `interface` 여야 구현을 물려받을 수 있는 이유와 인터페이스는 규약만 담는 자리라 상태를 두지 않는다는 일반 원칙·인터페이스의 필드가 `public static final` 상수가 되어 인스턴스마다 갖는 값이 아니게 되는 자리·의존 객체를 들고 있어야 하는 쪽은 클래스라는 갈림)
- `2026B_Spring/springweb/src/main/java/day05/TestService.java` (엔티티 목록을 DTO 목록으로 바꾸기 — 메소드 반환 타입이 `List<TestDto>` 라는 것이 계층 경계선이 되는 자리와 "컨트롤러가 다루는 타입은 DTO뿐"이 서명 하나로 지켜지는 구조·꺼내기·바꾸기·돌려주기 세 단계와 변환을 서비스에 둬 엔티티가 사는 범위를 이 메소드 안으로 닫는 배치, **`forEach` 와 람다** — 컬렉션이 안에서 반복을 돌고 나는 할 일만 적는 표기와 `for` 문과 갈리는 지점(반복을 누가 도나·적는 것·중간에 빠져나올 수 있는가)·반복변수 타입을 안 적어도 되는 이유와 괄호·중괄호 생략 조건·바깥에 만들어 둔 리스트를 람다 안에서 채우는 구조와 참조 자체를 다시 대입할 수 없는 제약, `@Autowired` 필드 주입으로 리포지토리를 받는 자리와 생성자 주입과의 갈림, **저장 방향은 반대로 흐르는 자리** — 받는 타입이 DTO이고 안에서 `toEntity()` 로 바꾸는 구조와 조회의 `from()` 과 부르는 메소드·도는 방향이 뒤집히는 대비·`toEntity()` 가 `no` 를 안 옮겨 PK가 비고 그래서 `save` 가 `insert` 로 갈리는 기준과 이어지는 점)
- `2026B_Spring/springweb/src/main/java/day05/TestController.java` (반환 타입이 DTO 목록인 자리 — 판정할 것이 없으면 컨트롤러 본문이 한 줄까지 줄어드는 점, `List<TestDto>` 가 JSON 배열이 되고 배열 원소의 키를 DTO의 getter가 정하는 자리·엔티티가 아니라 DTO의 필드 이름이 응답 키가 되므로 표 컬럼이 바뀌어도 화면 쪽을 안 고쳐도 되는 값어치, 매핑이 하나뿐이라 아직 클래스 레벨 `@RequestMapping` 을 뽑지 않은 상태와 갈래가 늘면 앞머리를 클래스로 올리게 되는 자리, 메소드 이름이 요청 처리에 관여하지 않고 주소 매핑은 표시가 정한다는 점, 세 계층이 아는 타입이 갈려 엔티티는 서비스 아래로·DTO는 서비스 위로 닫히고 서비스가 두 세계가 겹치는 유일한 자리라는 정리·day04까지 엔티티가 컨트롤러까지 올라오며 적어 둔 문제가 이 배치로 없어지는 지점)

## 관련 노트

[[Spring MOC]] · [[Spring day05 DTO 변환과 초기 데이터 적재]] · [[KDT_2026 학습 지도]]
