---
출처: Claude 분석
원본: KDT_2026/2026B_Spring/springweb/src/main/java/day05/TestService.java, springweb/src/main/java/day05/TestController.java
작성일: 2026-09-03
tags: [학습, java]
---

# Spring day05 — 등록·수정 흐름과 변경 감지

> 실습 파일: `2026B_Spring/springweb/src/main/java/day05/TestService.java`, `TestController.java`
> 허브: [[Spring MOC]] · 이전: [[Spring day05 조회 흐름에 DTO 얹기]] · 다음: [[Spring day06 연관관계 매핑과 외래키]]

[[Spring day05 조회 흐름에 DTO 얹기]] 에서 전체조회 한 갈래를 요청부터 응답까지 이었다. 저장 쪽은 `toEntity()` 를 부르는 자리까지만 잡아 두고 리포지토리 호출은 비워 뒀다. **이번은 그 자리를 채우고 수정 갈래까지 붙이는 실습이다.**

세 갈래가 한 벌로 찬다.

| 방식 | 주소 | 서비스 | 리포지토리 호출 |
| --- | --- | --- | --- |
| `GET` | `/test` | `findAll()` | `findAll()` |
| `POST` | `/test` | `save()` | `save()` |
| `PUT` | `/test` | `update()` | `findById()` **만** |

마지막 줄이 이번의 핵심이다. 수정인데 저장을 부르는 자리가 없다.

## 1. 배운 내용

### 1-1. 저장이 끝까지 이어진 자리

비워 뒀던 두 줄이 채워졌다.

```java
// 2. 저장
public boolean save(TestDto testDto) {
    // 1. dto --> entity 변환함수 : toEntity 함수
    TestEntity testEntity = testDto.toEntity();
    // 2. entity save 저장
    TestEntity saveEntity = testRepository.save(testEntity);
    // 3. 저장 결과 pk 여부 성공
    if (saveEntity.getNo() >= 1)
        return true;
    return false;
}
```

세 단계가 조회와 정확히 반대로 돈다.

| | 조회 | 저장 |
| --- | --- | --- |
| 1단계 | 리포지토리에서 꺼낸다 | DTO를 엔티티로 바꾼다 |
| 2단계 | 엔티티를 DTO로 바꾼다 | 리포지토리에 넘긴다 |
| 3단계 | DTO를 돌려준다 | 결과를 판정해 돌려준다 |

**성공 판정을 PK로 하는 것이 이 코드의 요점이다.** `save` 는 저장된 엔티티를 돌려주고, 그 엔티티에는 DB가 채운 번호가 들어 있다. `toEntity()` 가 `no` 를 안 옮겨 뒀으므로 넘길 때는 `null` 이고 받을 때는 숫자다. 그 자리에서 번호를 꺼내 보면 실제로 줄이 만들어졌는지 확인된다.

`Integer` 를 쓴 것이 여기서 값을 한다. `int` 였다면 저장 전에도 0이라 "아직 없음"과 "0번"이 같은 모양이 된다. → [[Spring day04 JPA 엔티티와 리포지토리]]

### 1-2. 컨트롤러에 등록 갈래 붙이기

```java
// 2. 등록
@PostMapping("/test")
public boolean save(@RequestBody TestDto testDto) {
    return testService.save(testDto);
}
```

조회와 **주소가 같고 방식만 다르다.** 주소는 자원(`/test`)을 가리키고 무엇을 할지는 방식이 말한다는 배치가 그대로 이어진다. 같은 주소에 붙어도 `GET` 과 `POST` 는 다른 자리라 충돌하지 않는다.

`@RequestBody` 가 요청 본문의 JSON을 DTO로 되돌린다. 나가는 쪽에서 `from()` 이 만든 키를 그대로 실어 보내면 들어오는 쪽에서 같은 필드에 담긴다.

```json
POST /test
Content-Type: application/json

{ "name": "제로콜라", "descri": "맛있는 탄산음료4", "price": 1500 }
```

**보내지 않은 필드는 `null` 로 남는다.** `no`·`createDate`·`updateTime` 을 안 실어도 문제가 없는 것은 `toEntity()` 가 어차피 그 셋을 안 옮기기 때문이다. 변환 메소드에서 한 번 걸러 뒀기 때문에 밖에서 무엇이 들어오든 저장되는 값이 정해져 있다.

### 1-3. 수정 — 찾아서 바꾸기

```java
// 3. 수정
@Transactional
public boolean update(TestDto testDto) {
    // 1. 수정할 엔티티 찾는다. pk
    Optional<TestEntity> optional = testRepository.findById(testDto.getNo());

    // 2. 찾은 엔티티가 존재하면
    if (optional.isPresent()) {
        // 3. 엔티티 꺼낸다.
        TestEntity entity = optional.get();
        // 4. setter 메소드 이용한 수정
        entity.setPrice(testDto.getPrice());
        entity.setDescri(testDto.getDescri());
        return true;
    }
    return false;
}
```

네 단계인데 리포지토리를 부르는 것은 첫 줄 하나뿐이다.

**`findById` 가 `Optional<TestEntity>` 를 돌려준다.** "없을 수도 있다"를 `null` 이 아니라 타입으로 옮긴 상자다. 상자를 받았으니 `isPresent()` 로 열어 보고 `get()` 으로 꺼내는 두 단계가 생긴다. 확인 없이 `get()` 을 바로 부르면 `null` 검사를 빠뜨린 것과 같아지므로 이 순서가 짝이다.

여기서 등록과 수정이 갈리는 지점이 드러난다.

| | 등록 | 수정 |
| --- | --- | --- |
| 대상 | 아직 없다 | 이미 있다 |
| PK | 비어 있다 | 반드시 실려 와야 한다 |
| 먼저 하는 일 | 변환 | 조회 |
| 없을 때 | 해당 없음 | `false` |

`testDto.getNo()` 로 번호를 꺼내므로 **수정 요청에는 `no` 가 실려 와야 한다.** 등록에서는 안 실어도 되던 필드가 수정에서는 필수가 된다. 같은 DTO를 두 갈래에 쓰면서 필수 필드가 갈리는 자리라, 등록용·수정용 DTO를 나누는 이야기가 여기서 나온다(2-1).

### 1-4. `save` 를 안 부르는데 `update` 가 나가는 자리

이 메소드에는 `testRepository.save(...)` 가 없다. setter를 두 번 부르고 `true` 를 돌려주면 끝인데, 서버 로그에는 `update` SQL이 찍힌다.

```
Hibernate:
    update test set descri=?, price=? where no=?
```

**변경 감지(더티 체킹)** 다. `findById` 로 읽어 온 엔티티는 영속성 컨텍스트가 관리하는 상태가 되고, 그때 값의 사본(스냅샷)이 함께 남는다. 트랜잭션이 끝날 때 지금 값과 사본을 견주어 **달라진 필드만** `update` 문으로 내보낸다.

```
findById()      → 엔티티를 읽어 오고 스냅샷을 함께 남긴다
setPrice()      → 자바 객체의 필드만 바뀐다 (아직 SQL 없음)
setDescri()     → 마찬가지
메소드 종료     → 트랜잭션 커밋 → 스냅샷과 비교 → 바뀐 두 필드만 update
```

바꾸지 않은 `name` 은 SQL에 안 들어간다. 조회해서 손에 든 객체를 그냥 고치면 되는 이 모양이 JPA가 SQL을 안 적게 해 주는 자리 중 가장 눈에 띄는 곳이다.

### 1-5. `@Transactional` 이 있어야 성립한다

더티 체킹은 **트랜잭션 안에서만** 돈다. 견줄 시점이 트랜잭션이 끝나는 때이기 때문에, 트랜잭션이 없으면 견주는 자리 자체가 없다.

```java
@Transactional          // 이 한 줄이 메소드 전체를 한 묶음으로 만든다
public boolean update(TestDto testDto) { … }
```

표시가 없으면 `findById` 한 번이 끝나고 컨텍스트가 닫혀, setter로 바꾼 값은 자바 객체에만 남고 DB로 안 나간다. **오류도 안 나고 `true` 도 돌려주는데 값만 안 바뀌는 모양**이라 눈치채기 어렵다. 수정이 안 먹으면 이 표시부터 보게 된다.

붙어 있는 표시가 어느 쪽 것인지도 봐 둘 자리다.

| 패키지 | 속성 |
| --- | --- |
| `jakarta.transaction.Transactional` | 규격 쪽. 속성이 적다 |
| `org.springframework.transaction.annotation.Transactional` | `readOnly`·`propagation`·`isolation`·`rollbackFor` |

지금은 표시만 붙이고 속성을 안 쓰므로 어느 쪽이든 돈다. 조회에 `readOnly = true` 를 붙이기 시작하면 스프링 쪽으로 맞추게 된다. → [[Spring day05 조회 흐름에 DTO 얹기]]

### 1-6. 컨트롤러의 수정 갈래

```java
// 3. 수정
@PutMapping("/test")
public boolean update(
        @RequestBody TestDto testDto) {
    return testService.update(testDto);
}
```

등록과 모양이 같고 표시만 `@PostMapping` → `@PutMapping` 으로 갈린다. 컨트롤러가 하는 일이 넘기고 받아 돌려주는 한 줄인 것도 그대로다. **판정이 전부 서비스에 있으니 위층은 얇게 유지된다.**

주소 하나에 세 방식이 붙어 표가 이렇게 된다.

| 방식 | 주소 | 받는 것 | 돌려주는 것 |
| --- | --- | --- | --- |
| `GET` | `/test` | (없음) | `List<TestDto>` → JSON 배열 |
| `POST` | `/test` | `@RequestBody TestDto` | `boolean` |
| `PUT` | `/test` | `@RequestBody TestDto` | `boolean` |

세 메소드가 모두 `/test` 를 적고 있다. 갈래가 넷이 되면 클래스 레벨 `@RequestMapping("/test")` 로 앞머리를 올리게 되는 자리다.

### 1-7. 세 갈래가 리포지토리를 부르는 모양

한 줄로 놓으면 갈림이 보인다.

```
조회  Controller → Service → repository.findAll()   → 엔티티 목록 → DTO 목록
등록  Controller → Service → repository.save()      → 영속 엔티티 → PK 판정
수정  Controller → Service → repository.findById()  → Optional → setter → (커밋 시 update)
```

**적은 코드와 나가는 SQL이 갈리는 것은 수정 하나뿐이다.** 조회와 등록은 부른 만큼 나가는데, 수정은 부르지 않은 `update` 가 나간다. 코드를 읽어 SQL을 짐작하는 방식이 처음으로 어긋나는 자리라, 로그를 켜 두고 실제로 무엇이 나가는지 보는 습관이 여기서부터 값을 한다.

## 2. 추가로 알면 좋은 활용법

### 2-1. 수정에서 무엇을 바꿀지 고르는 자리

지금은 `price` 와 `descri` 둘만 바꾼다. `name` 은 손대지 않는데, `@Column(unique = true)` 가 걸린 필드라 바꾸는 순간 중복 판정이 따라붙기 때문에 뒤로 미뤄 두기 좋은 갈래다. → [[Spring day05 엔티티 제약과 감사 필드]]

바꿀 필드를 고르는 세 갈래가 있다.

| 방식 | 안 보낸 필드 |
| --- | --- |
| 지금처럼 정해진 필드만 setter | 원래 값이 남는다 |
| 들어온 값이 `null` 이 아닐 때만 setter | 원래 값이 남는다 |
| `save` 로 통째로 덮어쓰기 | `null` 로 덮인다 |

```java
if (testDto.getPrice() != null) entity.setPrice(testDto.getPrice());
if (testDto.getDescri() != null) entity.setDescri(testDto.getDescri());
```

**"보내지 않은 것은 그대로 둔다"가 부분 수정의 뜻이고, 이 모양은 `PUT` 보다 `PATCH` 쪽에 가깝다.** `PUT` 은 원래 자원을 통째로 갈아 끼운다는 뜻이라 안 보낸 필드가 비워지는 쪽이 규격에 맞는다. 실무에서는 `PUT` 으로 두고 부분 수정처럼 쓰는 경우가 흔하지만, 뜻이 갈린다는 것은 알고 고르는 편이 낫다.

### 2-2. setter 대신 도메인 메소드

엔티티에 `@Setter` 가 열려 있으면 값을 바꿀 수 있는 자리가 코드 어디에나 생긴다. 바꾸는 통로를 하나로 좁히는 갈래가 있다.

```java
// 엔티티에 두는 메소드
public void changeInfo(String descri, Integer price) {
    this.descri = descri;
    this.price = price;
}
```

```java
// 서비스
entity.changeInfo(testDto.getDescri(), testDto.getPrice());
```

**무엇을 바꾸는 일인지가 메소드 이름에 남는다.** setter 두 줄은 "필드 두 개를 바꾼다"까지만 말하는데, 이름을 붙이면 "제품 정보를 고친다"가 된다. 바꾸면 안 되는 필드는 애초에 통로가 없어지는 것도 값어치다.

이 방향으로 가면 엔티티에서 `@Setter` 를 떼게 된다. 지금 단계에서는 setter가 있어야 더티 체킹을 눈으로 확인하기 쉬우니, 통로를 좁히는 이야기로만 알아 두면 된다.

### 2-3. `Optional` 을 다루는 네 갈래

`isPresent()` + `get()` 말고도 꺼내는 방법이 있다.

```java
// 1. 확인하고 꺼내기 (지금 방식)
if (optional.isPresent()) { TestEntity e = optional.get(); … }

// 2. 없으면 대신 쓸 값
TestEntity e = optional.orElse(new TestEntity());

// 3. 없으면 예외
TestEntity e = optional.orElseThrow(() -> new IllegalArgumentException("없는 번호"));

// 4. 있을 때만 실행
optional.ifPresent(e -> { e.setPrice(…); });
```

| 갈래 | 어울리는 자리 |
| --- | --- |
| `isPresent`+`get` | 없을 때도 정상 흐름으로 돌려줄 때 |
| `orElseThrow` | 없는 것이 잘못된 요청일 때 |
| `ifPresent` | 없으면 아무 일도 안 해도 될 때 |

`orElseThrow` 로 바꾸면 `if` 가 사라져 본문이 한 단 얕아지고, 없을 때의 처리를 예외 처리 자리로 모을 수 있다. `@RestControllerAdvice` 와 짝지어 두면 응답 모양도 한 자리에서 정해진다.

### 2-4. `boolean` 하나로는 갈라 보이지 않는 것

수정이 `false` 를 돌려주는 경우는 "그 번호가 없다" 하나다. 그런데 화면 쪽에서 받는 것은 `false` 뿐이라 이유를 모른다.

| 상황 | 지금 응답 | 어울리는 상태 코드 |
| --- | --- | --- |
| 수정 성공 | `200 true` | 200 |
| 번호가 없음 | `200 false` | 404 |
| 번호를 안 보냄 | 오류 | 400 |

```java
@PutMapping("/test")
public ResponseEntity<Void> update(@RequestBody TestDto dto) {
    return testService.update(dto)
            ? ResponseEntity.ok().build()
            : ResponseEntity.notFound().build();
}
```

**상태 코드로 갈라 두면 화면 쪽 판정이 한 겹 줄어든다.** `boolean` 을 그대로 두면 200을 받고도 본문을 열어 봐야 성공인지 알 수 있다. day04에서 적어 둔 "`boolean` 하나로는 0건과 오류를 갈라 보이지 못한다"가 수정 갈래에서 다시 나오는 자리다. → [[Spring day04 REST 컨트롤러 CRUD 골격]]

`no` 가 `null` 인 채로 `findById(null)` 이 불리면 조회 단계에서 걸리므로, 값 검사를 앞으로 당기는 이야기(2-5)와도 이어진다.

### 2-5. 값 검사를 본문 앞으로 당기기

```java
public class TestDto {
    @NotNull(message = "번호는 필수")
    private Integer no;
    @Positive
    private Integer price;
    …
}
```

```java
@PutMapping("/test")
public boolean update(@Valid @RequestBody TestDto testDto) { … }
```

`@Valid` 를 붙이면 메소드 본문이 시작되기 전에 걸러진다. **DB 제약보다 앞에서 막는 자리**라, 잘못된 값이 리포지토리까지 내려가지 않는다.

다만 등록과 수정이 같은 DTO를 쓰면 `no` 에 `@NotNull` 을 걸 수 없다. 등록에서는 비어 있어야 하기 때문이다. 이 지점이 DTO를 갈래별로 나누는 실질적인 이유가 된다.

```java
public class TestDto {
    public static class Create { … }   // no 없음
    public static class Update { … }   // no 필수
}
```

### 2-6. 수정 대상 번호를 어디에 실을까

지금은 본문에 `no` 를 담아 보낸다. 주소에 싣는 갈래도 있다.

```java
@PutMapping("/test/{no}")
public boolean update(@PathVariable Integer no, @RequestBody TestDto dto) { … }
```

| | 본문에 담기 | 주소에 싣기 |
| --- | --- | --- |
| 주소 | `/test` | `/test/3` |
| 무엇을 고치는지 | 본문을 열어야 안다 | 주소에 보인다 |
| 값이 둘로 갈릴 여지 | — | 주소와 본문의 `no` 가 다를 수 있다 |

**자원을 가리키는 식별자는 주소에 두는 편이 REST 쪽 관용에 맞는다.** 로그만 봐도 무엇을 고쳤는지 남는 것도 값어치다. 대신 주소와 본문 양쪽에 번호가 있을 때 어느 쪽을 믿을지 정해 둬야 한다(보통 주소).

### 2-7. `@Transactional` 이 안 먹는 자리

표시를 붙였는데 트랜잭션이 안 도는 경우가 있다.

- **같은 클래스 안에서 자기 메소드를 부를 때** — 표시는 프록시가 앞뒤에 끼어들어 동작하는데, 안에서 부르면 프록시를 안 거친다
- **`private` 메소드** — 프록시가 감쌀 수 없다
- **컨트롤러에서 리포지토리를 직접 부를 때** — 서비스를 건너뛰면 표시가 붙은 자리를 안 지나간다

```java
public boolean update(TestDto dto) {
    return doUpdate(dto);      // 여기서 부르면 아래 표시가 안 먹는다
}

@Transactional
public boolean doUpdate(TestDto dto) { … }
```

day03의 애노테이션·리플렉션에서 정리한 "표시는 스스로 아무 일도 하지 않고 읽는 쪽이 있어야 동작이 된다"가 그대로 걸리는 자리다. → [[Spring day03 애노테이션과 리플렉션]]

### 2-8. 등록 결과로 번호를 돌려주기

`save` 가 영속된 엔티티를 돌려주므로 번호가 손에 있다. `boolean` 으로 줄이면 그 번호가 버려진다.

```java
public TestDto save(TestDto testDto) {
    TestEntity saved = testRepository.save(testDto.toEntity());
    return TestDto.from(saved);       // 번호·감사 필드까지 채워져 돌아간다
}
```

**`from()` 을 한 번 더 부르면 DB가 채운 값이 그대로 응답에 실린다.** 등록 직후 화면이 상세로 넘어가야 할 때 요청을 한 번 더 보내지 않아도 된다. 감사 필드도 이때 채워져 있으므로 만든 시각까지 같이 돌아간다. → [[Spring day05 DTO 변환과 초기 데이터 적재]]

### 2-9. 수정이 안 먹을 때 훑는 순서

값이 안 바뀌는데 오류도 안 날 때 보는 자리가 정해져 있다.

1. `@Transactional` 이 붙어 있는가 (없으면 더티 체킹이 안 돈다)
2. 다른 클래스를 거쳐 불리는가 (자기 호출이면 표시가 안 먹는다)
3. `findById` 가 실제로 엔티티를 찾았는가 (`isPresent()` 가 `false` 면 조용히 `false`)
4. setter가 정말 다른 값을 넣었는가 (같은 값이면 바뀐 것이 없어 SQL이 안 나간다)
5. `ddl-auto=create-drop` 이라 서버를 다시 띄운 것은 아닌가 (표가 새로 만들어져 값이 사라진다)

마지막 줄은 실습 환경 특유의 자리다. 확인 데이터가 매번 다시 들어가므로 번호도 매번 1부터 다시 붙는다.

## 3. 더 나아가 알면 좋은 것

### 3-1. 영속성 컨텍스트가 하는 세 가지

더티 체킹은 영속성 컨텍스트가 하는 일 중 하나다.

| 기능 | 하는 일 |
| --- | --- |
| 1차 캐시 | 같은 트랜잭션에서 같은 PK를 두 번 찾으면 쿼리가 한 번만 나간다 |
| 쓰기 지연 | `save` 를 불러도 바로 안 나가고 커밋 때 모아서 나간다 |
| 변경 감지 | 스냅샷과 견주어 바뀐 필드만 `update` 로 만든다 |

세 가지 모두 "자바 객체와 DB 사이에 한 겹을 두어서" 생기는 값이다. 그래서 이 겹이 언제 만들어지고 언제 닫히는지가 곧 트랜잭션 범위와 같아진다.

엔티티 상태는 넷으로 갈린다.

```
비영속(new)     ── persist/save ──▶  영속(managed)  ── 커밋 시 변경 감지 ──▶ DB 반영
                                          │
                                     detach/close
                                          ▼
                                     준영속(detached)  ── remove ──▶ 삭제(removed)
```

`toEntity()` 로 막 만든 객체는 비영속이고, `findById` 로 읽어 온 객체는 영속이다. **같은 `TestEntity` 인데 상태가 달라서 setter의 결과가 갈린다**는 것이 등록과 수정의 코드 모양이 다른 근본 이유다.

### 3-2. 변경 감지가 실제로 도는 순서

```
1. findById  → SELECT → 엔티티 생성 → 1차 캐시에 저장 + 스냅샷 복사
2. setter    → 1차 캐시의 엔티티만 바뀐다
3. 커밋 직전 → flush → 스냅샷과 현재 값 비교
4. 달라진 필드로 UPDATE 문 생성 → DB로 전송
5. 커밋
```

3단계의 `flush` 는 커밋 말고도 JPQL 질의 직전에도 일어난다. 바꾼 값을 조건으로 다시 조회하면 그 앞에서 `update` 가 먼저 나가야 결과가 맞기 때문이다.

**스냅샷을 들고 있어야 하므로 읽어 오는 엔티티마다 메모리가 두 벌씩 든다.** 조회 전용 메소드에 `readOnly = true` 를 붙이면 이 사본을 안 만든다는 이야기가 여기에 붙는다.

### 3-3. 두 사람이 같은 줄을 동시에 고칠 때

수정은 "읽고 → 바꾸고 → 쓴다"라 읽은 뒤 쓰기 전 사이에 남이 먼저 바꿀 수 있다. 나중에 쓴 쪽이 이기고 앞의 수정이 소리 없이 사라진다.

```java
@Entity
public class TestEntity extends BaseTime {
    @Version
    private Long version;      // 수정될 때마다 하이버네이트가 올린다
    …
}
```

`update … where no = ? and version = ?` 로 나가서, 그 사이 누가 고쳤으면 0건이 되고 예외가 난다. **막아 주는 것이 아니라 부딪혔다는 사실을 알려 주는 방식**이라 낙관적 락이라 부른다. 감사 필드가 기록이라면 이쪽은 판정이다.

### 3-4. 바뀐 필드만 나간다는 것의 뒷면

하이버네이트는 기본적으로 **모든 컬럼**을 `update` 문에 넣는 설정도 갖고 있다. 미리 만들어 둔 SQL을 재사용하는 편이 빠르기 때문이다. 지금 로그에 두 컬럼만 찍힌다면 변경 감지가 만든 동적 SQL 쪽이다.

```java
@DynamicUpdate      // 바뀐 필드만 넣은 SQL을 매번 만든다
@Entity
public class TestEntity … { }
```

컬럼이 아주 많고 바꾸는 것이 한둘일 때 값을 한다. 반대로 컬럼이 적으면 SQL을 매번 만드는 비용이 더 클 수 있어, 붙이기 전에 재 보는 자리다.

### 3-5. 삭제 갈래가 남아 있다

CRUD 네 갈래 중 아직 삭제가 없다.

```java
@DeleteMapping("/test/{no}")
public boolean delete(@PathVariable Integer no) { … }
```

```java
public boolean delete(Integer no) {
    if (!testRepository.existsById(no)) return false;
    testRepository.deleteById(no);
    return true;
}
```

`deleteById` 는 돌려주는 값이 없어 성공 여부를 `existsById` 로 따로 확인하게 된다. 없는 번호로 불러도 조용히 넘어가는 쪽이라, 판정이 필요하면 앞에 한 번 물어봐야 한다.

지운 줄을 실제로 지우지 않고 표시만 남기는 갈래(소프트 삭제)도 있는데, `name` 에 걸린 유니크 제약이 지운 줄까지 세는 문제가 따라붙는다.

### 3-6. 다음에 볼 키워드

- 영속성 컨텍스트의 엔티티 네 상태와 `persist`·`merge`·`detach`·`clear`
- `flush` 가 일어나는 시점 셋과 `FlushMode`
- `@Transactional` 의 `propagation` 일곱 값과 중첩 트랜잭션
- `rollbackFor` 와 검사 예외에서 롤백이 안 되는 기본 동작
- `@Version` 낙관적 락과 `PESSIMISTIC_WRITE` 비관적 락의 갈림
- `@DynamicUpdate`·`@DynamicInsert` 와 미리 만든 SQL의 재사용
- `PUT` 과 `PATCH` 의 뜻 차이와 부분 수정 설계
- `@Valid`·`@Validated` 와 그룹 검증으로 등록·수정 규칙 나누기
- `@RestControllerAdvice`·`@ExceptionHandler` 로 없음·잘못된 값의 응답 모양 통일하기
- `@DataJpaTest` 로 더티 체킹이 실제로 도는지 검사하기

## 실습 파일

- `2026B_Spring/springweb/src/main/java/day05/TestService.java` (**저장이 끝까지 이어진 자리** — `toEntity()` 로 바꾸고 `repository.save()` 에 넘기고 결과를 판정하는 세 단계가 조회와 정확히 반대로 도는 구조·`save` 가 영속된 엔티티를 돌려주므로 DB가 채운 번호를 그 자리에서 꺼내 성공 판정을 PK로 하는 자리와 `toEntity()` 가 `no` 를 안 옮겨 넘길 때 `null` 이고 받을 때 숫자가 되는 대비·`Integer` 여야 "아직 없음"과 "0번"이 갈리는 점, **수정 — 찾아서 바꾸기** — `findById` 가 `Optional` 을 돌려줘 `isPresent()`·`get()` 두 단계가 짝으로 붙는 이유와 확인 없이 `get()` 을 부르면 `null` 검사를 빠뜨린 것과 같아지는 자리·등록과 수정이 갈리는 네 지점(대상이 있는가·PK가 필수인가·먼저 하는 일·없을 때의 판정)과 같은 DTO를 두 갈래에 쓰면 필수 필드가 갈리는 문제, **`save` 를 안 부르는데 `update` 가 나가는 자리** — 읽어 온 엔티티가 영속 상태가 되며 스냅샷이 함께 남고 트랜잭션이 끝날 때 견주어 바뀐 필드만 `update` 로 나가는 더티 체킹의 흐름·손대지 않은 필드가 SQL에 안 들어가는 실측, **`@Transactional` 이 있어야 성립하는 조건** — 견줄 시점이 트랜잭션 종료라 표시가 없으면 값이 자바 객체에만 남고 오류도 `true` 도 그대로라 눈치채기 어려운 모양·`jakarta` 와 스프링 쪽 표시가 속성에서 갈리는 자리, 세 갈래가 리포지토리를 부르는 모양을 한 줄로 놓으면 적은 코드와 나가는 SQL이 어긋나는 것은 수정 하나뿐이라는 정리)
- `2026B_Spring/springweb/src/main/java/day05/TestController.java` (**등록·수정 갈래를 주소 하나에 붙이기** — `@PostMapping`·`@PutMapping` 이 `@GetMapping` 과 같은 `/test` 에 붙어도 방식이 달라 충돌하지 않는 구조와 주소는 자원을 가리키고 방식이 할 일을 말하는 배치의 재확인, `@RequestBody` 가 본문 JSON을 DTO로 되돌리는 자리와 나가는 쪽 `from()` 이 만든 키를 그대로 실어 보내면 같은 필드에 담기는 왕복·보내지 않은 필드가 `null` 로 남아도 `toEntity()` 가 걸러 두었기 때문에 저장되는 값이 정해져 있는 점, 컨트롤러 본문이 넘기고 받아 돌려주는 한 줄인 채로 유지되고 판정이 전부 서비스에 있는 배치·세 메소드가 모두 `/test` 를 적고 있어 갈래가 늘면 클래스 레벨 `@RequestMapping` 으로 앞머리를 올리게 되는 자리)

## 관련 노트

[[Spring MOC]] · [[Spring day05 조회 흐름에 DTO 얹기]] · [[Spring day06 연관관계 매핑과 외래키]] · [[KDT_2026 학습 지도]]
