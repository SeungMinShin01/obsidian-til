---
출처: Claude 분석
원본: KDT_2026/2026B_Spring/springweb/src/main/java/day04/practice, springweb/src/main/resources/application.properties, springweb/build.gradle
작성일: 2026-09-02
tags: [학습, java]
---

# Java Spring day04 — REST 컨트롤러 CRUD 골격

> 실습 파일: `2026B_Spring/springweb/src/main/java/day04/practice/AppStart.java`, `TestController.java`, `TestDto.java`, `src/main/resources/application.properties`, `springweb/build.gradle`
> 허브: [[Spring MOC]] · 이전: [[Spring day03 애노테이션과 리플렉션]]

[[Spring day03 애노테이션과 리플렉션]] 은 표시 하나하나를 뜯어보는 쪽이었다. 애노테이션을 만들고, 리플렉션으로 읽고, 그 위에 매핑과 값 받는 통로를 얹는 데까지 갔다. 표시별로는 다 봤지만 **한 컨트롤러 안에 CRUD 네 갈래를 나란히 놓아 본 적은 없다.**

day04는 그 조립을 연습한다. 새로 나오는 표시는 `@PostMapping`·`@PutMapping` 정도이고, 나머지는 이미 본 것들이다. 대신 **어느 표시를 어느 자리에 두는가**가 주제가 된다 — 공통은 클래스에, 갈리는 것은 메소드에, 실제 일은 DAO에.

| 자리 | 하는 일 |
| --- | --- |
| `AppStart.java` | `practice` 패키지에 진입점을 두고 스캔 범위를 잡기 (1-1) |
| `@RestController` · `@RequestMapping("/test")` | 클래스 자리에 공통을 올리기 (1-2) |
| 메소드마다 붙은 매핑 넷 | 주소는 같고 방식으로 갈리는 CRUD (1-3) |
| `private TestDao td = ...` | DAO를 멤버로 들고 있기 (1-4) |
| 메소드 본문 세 줄 | 넘기고 · 받고 · 돌려주기 (1-5) |
| 반환 타입 `boolean`·`ArrayList<TestDto>`·`TestDto` | 응답의 모양이 여기서 정해진다 (1-6) |
| `TestDto` 와 롬복 표시 넷 | 오가는 값을 담는 그릇을 표시로 만들기 (1-8) |
| 필드 타입 `Integer` | 값이 안 왔을 때를 담을 수 있는 타입 고르기 (1-9) |
| `@RequestBody`·`@RequestParam`·`@PathVariable` | 값이 어디에 실려 오는지 표시로 적어 두기 (1-10) |
| `application.properties` | 연결 정보를 코드 밖 설정 파일로 옮기기 (1-11) |
| `build.gradle` 의 의존성 넷 | 표시를 처리해 줄 도구를 선언해 두기 (1-12) |

Spring day02 스프링 부트 실행과 계층 이식 에서 게시판·대기명단으로 같은 계층을 두 번 만들었는데, 여기서는 그 골격만 남기고 세 번째로 다시 써 보는 셈이다. **되풀이되는 모양이 있다는 것을 손으로 확인하는 자리**다.

## 1. 배운 내용

### 1-1. 연습 패키지에 진입점 두기

`practice` 패키지에도 진입점이 하나 있다.

```java
package day04.practice;

@SpringBootApplication
public class AppStart {
    public static void main(String[] args) {
        SpringApplication.run(AppStart.class, args);
    }
}
```

[[Spring day03 애노테이션과 리플렉션]] 의 1-23에서 본 규칙이 그대로 적용된다. `@SpringBootApplication` 안에 `@ComponentScan` 이 들어 있고, 범위를 따로 적지 않으면 **이 클래스가 속한 패키지와 그 하위**가 대상이 된다.

```
day03.exam.AppStart      →  day03.exam 아래만 스캔
day04.practice.AppStart  →  day04.practice 아래만 스캔
```

같은 프로젝트 안에 진입점이 여러 개 쌓여 가는 구조라, 어느 것을 띄우느냐에 따라 살아나는 컨트롤러가 갈린다. `main` 이 여럿일 때 `build.gradle` 의 `mainClass` 로 하나를 고르는 이야기는 Spring day02 스프링 부트 실행과 계층 이식 에 정리해 두었다.

정리하면 **패키지를 나누는 것이 곧 실습 단위를 나누는 것**이 된다. day마다 폴더를 새로 파고 진입점을 하나 두면, 앞의 실습과 주소가 겹쳐도 서로를 건드리지 않는다.

### 1-2. 공통은 클래스 자리로 — @RestController와 @RequestMapping

컨트롤러 클래스에 표시 둘이 붙는다.

```java
@RestController
@RequestMapping("/test")
public class TestController {
```

둘의 역할이 다르다.

| 표시 | 하는 일 |
| --- | --- |
| `@RestController` | 빈으로 등록 + 요청을 받는 자리 + 반환값을 본문에 그대로 싣기 |
| `@RequestMapping("/test")` | 이 클래스의 모든 메소드가 공유하는 **주소 앞머리** |

`@RestController` 는 `@Controller` + `@ResponseBody` 의 합성이라, 메소드마다 `@ResponseBody` 를 적지 않아도 된다. 값을 돌려주는 컨트롤러라 이쪽을 고르는 것이 맞다 — 화면 이름을 돌려줄 일이 없기 때문이다.

`@RequestMapping` 을 클래스에 올려 두면 메소드 쪽 값과 **이어 붙는다.**

```
클래스 @RequestMapping("/test")
  + 메소드 @GetMapping()          →  GET  /test
  + 메소드 @GetMapping("/test")   →  GET  /test/test
```

주소 체계를 바꿀 일이 생겨도 클래스의 한 줄만 고치면 되는 것이 이 배치의 값어치다. 컨트롤러가 여럿일 때 주소가 겹치지 않게 갈라 두는 자리이기도 하다.

### 1-3. 주소는 같고 방식으로 갈린다 — CRUD 매핑 넷

메소드마다 매핑 표시가 하나씩 붙는다. 괄호 안이 비어 있는 것은 **클래스 주소를 그대로 쓴다**는 뜻이다.

```java
@PostMapping()     public boolean testWrite(TestDto testDto) { ... }
@GetMapping()      public ArrayList<TestDto> testPrint()     { ... }
@DeleteMapping()   public boolean testDelete(int no)         { ... }
@PutMapping()      public boolean testUpdate(TestDto testDto){ ... }
```

넷 다 주소가 `/test` 로 같다. 그런데도 충돌하지 않는 이유는 **주소와 방식이 짝을 이뤄 하나의 자리**를 만들기 때문이다.

| 표시 | HTTP 방식 | CRUD | 하는 일 |
| --- | --- | --- | --- |
| `@PostMapping` | POST | Create | 새로 만들기 |
| `@GetMapping` | GET | Read | 읽기 |
| `@PutMapping` | PUT | Update | 고치기 |
| `@DeleteMapping` | DELETE | Delete | 지우기 |

Spring day01 서블릿과 HTTP 메소드 에서 `doGet`·`doPost`·`doPut`·`doDelete` 로 갈라 받던 그 구조다. 서블릿에서는 메소드 이름이 방식을 정했고, 여기서는 표시가 정한다. 갈라지는 기준 자체는 바뀌지 않았다.

넷 모두 `@RequestMapping(method = ...)` 의 합성 표기라는 점도 [[Spring day03 애노테이션과 리플렉션]] 에서 본 그대로다. 짧은 이름이 따로 있는 것은 자주 쓰는 조합에 이름을 붙여 둔 것이지 다른 장치가 아니다.

주소 하나에 네 자리를 두는 이 배치가 **자원 중심 주소 설계**의 기본형이다. "무엇을"은 주소가, "어떻게 할지"는 방식이 말한다.

### 1-4. 컨트롤러가 DAO를 들고 있는 자리

클래스 안에 멤버변수가 하나 있다.

```java
private TestDao td = TestDao.getInstance();
```

[[Spring day03 애노테이션과 리플렉션]] 1-20에서 본 싱글톤 창구다. `new` 로 만들지 않고 `getInstance()` 로 하나뿐인 객체를 꺼내 온다. 지역변수가 아니라 **멤버변수**로 둔 것이 요점이다.

| 두는 자리 | 결과 |
| --- | --- |
| 메소드 안 지역변수 | 요청이 올 때마다 꺼내는 코드가 되풀이된다 |
| 클래스 멤버변수 | 한 번 잡아 두고 모든 메소드가 같이 쓴다 |

컨트롤러 자신도 빈이라 기본적으로 하나만 만들어져 공유된다. 그 하나가 DAO 하나를 들고 있는 모양이라, 요청이 여럿 들어와도 객체가 늘지 않는다.

여기서 걸리는 것이 하나 있다. **DAO의 이름이 컨트롤러 코드에 직접 박혀 있다.** 구현을 갈아 끼우려면 이 줄을 고쳐야 한다는 뜻이라, [[Spring day03 애노테이션과 리플렉션]] 1-22에서 본 결합도 문제가 그대로 남아 있는 자리다. 이 줄을 지우고 컨테이너에게 받는 방식이 생성자 주입이고, 2-5에서 이어서 본다.

### 1-5. 메소드 본문이 세 줄로 같은 모양이다

다섯 메소드의 본문이 전부 같은 골격이다.

```java
@GetMapping()
public ArrayList<TestDto> testPrint() {
    ArrayList<TestDto> result = td.testPrint();   // ① DAO에 넘긴다
    return result;                                 // ② 결과를 그대로 돌려준다
}
```

컨트롤러가 하는 일이 **받아서 넘기고, 돌려주는** 것뿐이다. 값을 계산하거나 조건을 따지는 부분이 없다.

| 계층 | 맡는 일 |
| --- | --- |
| Controller | 요청을 받고, 값을 꺼내고, 결과를 응답으로 내보낸다 |
| Dao | DB와 이야기한다 |
| Dto | 오가는 값을 담는다 |

Spring day02 스프링 부트 실행과 계층 이식 에서 나눠 둔 계층이 그대로다. 컨트롤러를 얇게 두는 이유는 **바뀌는 이유가 다른 것들을 섞지 않기 위해서**다. 주소 체계가 바뀌면 컨트롤러만, 쿼리가 바뀌면 DAO만 손대면 된다.

메소드 이름을 `testWrite`·`testPrint`·`testDetail`·`testDelete`·`testUpdate` 로 두고 DAO에도 같은 이름을 둔 것도 같은 맥락이다. 이름이 층을 관통하면 따라 읽기가 쉬워진다.

### 1-6. 반환 타입이 응답의 모양을 정한다

돌려주는 타입이 셋으로 갈린다.

| 메소드 | 반환 타입 | 나가는 모양 |
| --- | --- | --- |
| `testWrite`·`testDelete`·`testUpdate` | `boolean` | `true` / `false` |
| `testPrint` | `ArrayList<TestDto>` | JSON 배열 `[{...},{...}]` |
| `testDetail` | `TestDto` | JSON 객체 `{...}` |

[[Spring day03 애노테이션과 리플렉션]] 1-26에서 본 규칙이 그대로 적용된다. 문자열만 평문으로 나가고 나머지는 JSON이 된다. 자바 안에서만 쓰는 모양을 오갈 수 있는 형식으로 옮기는 일을 스프링이 대신 해 준다.

`boolean` 을 돌려주는 세 갈래는 **성공했는지만 알려 주는** 쪽이다. DAO의 `executeUpdate` 가 돌려주는 처리 건수를 `> 0` 으로 판정해 `boolean` 으로 줄여 둔 모양인데, 화면 쪽에서는 `response.data` 가 `true` 인지만 보면 된다.

`ArrayList<TestDto>` 는 JSON 배열이 된다. 리스트 안의 DTO 하나하나가 getter를 통해 객체로 바뀌므로, **DTO의 필드 이름이 곧 화면에서 꺼내 쓰는 키**가 된다. DB 컬럼 → 필드 → getter → JSON 키 → 화면 코드로 이름 하나가 관통하는 그 자리다.

`boolean` 하나로 돌려주면 **0건인지 오류인지 갈라 보이지 않는다**는 점은 기억해 둘 만하다. 지울 대상이 없어서 `false` 인 것과 DB 연결이 끊겨 `false` 인 것이 같은 모양으로 나간다. 2-2에서 이어서 본다.

### 1-7. 값을 받는 두 모양이 한 클래스에 같이 있다

매개변수가 두 갈래로 갈린다.

```java
public boolean testWrite(TestDto testDto)   // DTO로 통째로 받기
public TestDto  testDetail(int no)          // 값 하나만 받기
```

[[Spring day03 애노테이션과 리플렉션]] 1-36에서 정리한 네 통로 중 둘이다.

| 받는 모양 | 붙는 표시 | 어울리는 자리 |
| --- | --- | --- |
| DTO 하나 | `@ModelAttribute` (생략 가능) | 값이 여럿일 때 — 등록·수정 |
| 값 하나 | `@RequestParam` (생략 가능) | 값이 하나뿐일 때 — 상세·삭제 |

둘 다 표시를 생략했다. DTO는 표시가 없으면 커맨드 객체 바인딩으로 처리되고, 기본형 매개변수는 요청 파라미터에서 이름이 같은 값을 찾아 채운다. 다만 **매개변수 이름이 `.class` 에 남지 않을 수 있어서**, 이름이 바뀌면 값이 비어 들어올 수 있다. `@RequestParam("no")` 처럼 이름을 적어 두는 편이 안전하다.

DTO에 값이 채워지는 과정도 앞에서 본 그대로다 — 기본 생성자로 객체를 만들고 setter로 하나씩 채운다. 롬복의 `@Data` 를 붙여 두면 그 통로가 함께 생긴다.

### 1-8. 오가는 값을 담는 그릇 — 롬복으로 만든 DTO

컨트롤러가 주고받는 값의 모양은 DTO 한 파일에 모여 있다.

```java
@NoArgsConstructor
@AllArgsConstructor
@Getter
@Setter
public class TestDto {
    private Integer no;
    private String content;
    private String writer;
}
```

필드 셋과 표시 넷이 전부다. 생성자·getter·setter를 손으로 적지 않는데도 다 갖춰진 클래스가 되는 것은 [[Spring day03 애노테이션과 리플렉션]] 에서 본 애노테이션 프로세서가 컴파일 시점에 그 코드를 만들어 넣기 때문이다.

넷이 각각 다른 자리에서 쓰인다.

| 표시 | 만들어지는 것 | 쓰이는 자리 |
| --- | --- | --- |
| `@NoArgsConstructor` | `new TestDto()` | 스프링이 빈 객체를 만들 때 |
| `@AllArgsConstructor` | `new TestDto(1, "내용1", "작성자1")` | 코드에서 값을 채워 만들 때 |
| `@Setter` | `setNo`·`setContent`·`setWriter` | 만든 객체에 값을 채워 넣을 때 |
| `@Getter` | `getNo`·`getContent`·`getWriter` | 객체를 JSON으로 내보낼 때 |

앞의 둘을 같이 붙여 둔 것이 요점이다. **전체 생성자를 만들면 기본 생성자가 사라지기 때문**이다. 자바는 생성자를 하나도 안 적었을 때만 기본 생성자를 자동으로 넣어 주므로, `@AllArgsConstructor` 만 붙이면 매개변수 없는 생성자가 없어진다.

그런데 스프링이 요청 값을 DTO에 담는 과정은 **빈 객체를 먼저 만들고 setter로 채우는** 순서다. 기본 생성자가 없으면 첫 단계에서 막힌다. 그래서 둘을 짝으로 붙여 두는 것이 관용이 됐다.

```
들어올 때   요청 값  →  new TestDto()  →  setNo/setContent/setWriter  →  메소드 매개변수
나갈 때     반환 객체 →  getNo/getContent/getWriter  →  JSON 키 3개
```

들어오는 길에 `@NoArgsConstructor` + `@Setter` 가, 나가는 길에 `@Getter` 가 쓰인다. 둘 중 하나만 빠져도 값이 비어 들어오거나 빈 JSON `{}` 이 나가므로, **DTO에 표시를 붙이는 일이 곧 통로를 여는 일**이다.

`@AllArgsConstructor` 는 다른 쓸모가 있다. 목록을 돌려주는 자리에서 값을 한 줄로 채워 만들 수 있다.

```java
ArrayList<TestDto> list = new ArrayList<>();
list.add(new TestDto(1, "내용1", "작성자1"));
list.add(new TestDto(2, "내용2", "작성자2"));
return list;
```

DB를 붙이기 전에도 **응답의 모양부터 확인할 수 있다.** 컨트롤러와 DTO만 두고 값을 손으로 채워 내보내면, 화면 쪽에서 받는 JSON이 어떤 키를 갖는지 먼저 맞춰 볼 수 있다. 뒤에 DAO가 들어와도 컨트롤러가 돌려주는 타입은 그대로라, 안쪽만 갈아 끼우면 된다.

### 1-9. int와 Integer — 값이 안 왔을 때를 담을 수 있는가

번호 필드의 타입이 `int` 가 아니라 `Integer` 다.

| | `int` | `Integer` |
| --- | --- | --- |
| 갈래 | 기본형 | 참조형(`int` 의 래퍼 클래스) |
| 담는 값 | 대략 ±21억 범위의 정수 | 같은 범위의 정수 + `null` |
| 값이 없을 때 | 담을 수 없다 (0이 들어간다) | `null` 로 둘 수 있다 |

차이는 `null` 하나뿐인데, HTTP를 사이에 두면 이 하나가 크게 갈린다.

요청으로 들어오는 값은 전부 문자열이고, **아예 안 온 경우가 늘 있다.** 등록 폼에서 번호를 보내지 않았거나, JSON에 키가 빠져 있거나, 값이 빈 문자열인 경우다. 이때 담을 자리가 `int` 면 "없음"을 표현할 방법이 없다.

```
JSON {"content":"내용", "writer":"작성자"}   ← no 가 없다

Integer no  →  null        "안 왔다"가 그대로 남는다
int     no  →  담을 수 없음  변환 단계에서 걸리거나 0이 된다
```

0으로 채워지면 더 곤란하다. **"번호를 안 보냈다"와 "0번을 보냈다"가 같은 모양**이 되어, 뒤에서 갈라 볼 수가 없다. `null` 은 적어도 "이 값은 안 왔다"를 그대로 들고 있다.

정리하면 **요청 값을 받는 DTO의 필드는 래퍼 타입으로 두는 편이 안전하다.** 계산에 쓰는 지역변수는 기본형이 가볍고 `null` 검사도 필요 없으니 그대로 두면 된다 — 경계를 넘어오는 값이냐 아니냐가 기준이다.

`Integer` 를 쓸 때 따라오는 것이 두 가지 있다. 산술에 바로 쓰면 자동으로 `int` 로 풀리는데(언박싱) 값이 `null` 이면 그 자리에서 예외가 난다. 그리고 `==` 로 비교하면 값이 아니라 참조를 견주므로, 값을 견줄 때는 `equals` 를 쓴다.

### 1-10. 값이 어디에 실려 오는지 표시로 적어 두기

매개변수에 붙은 표시가 셋으로 갈린다.

```java
public boolean testWrite(@RequestBody TestDto testDto)      // 본문의 JSON
public TestDto  testDetail(@RequestParam int no)            // 쿼리스트링
public boolean  testDelete(@PathVariable(name="no") int no) // 주소 경로
```

[[Spring day03 애노테이션과 리플렉션]] 1-36에서 정리한 네 통로 중 셋이다. 갈리는 기준은 **값이 어디에 실려 오는가** 하나다.

| 표시 | 값이 실린 곳 | 보내는 쪽 모양 |
| --- | --- | --- |
| `@RequestBody` | 요청 본문 | `Content-Type: application/json` + JSON |
| `@ModelAttribute` | 쿼리스트링·폼 | `application/x-www-form-urlencoded` |
| `@RequestParam` | 쿼리스트링·폼 | `?no=3` |
| `@PathVariable` | 주소의 경로 | `/test/3` |

`@RequestBody` 와 `@ModelAttribute` 가 특히 헷갈리는 짝이다. 둘 다 DTO 하나로 받는 모양이 같은데 **읽는 곳이 다르다.** 화면에서 `axios.post(url, 객체)` 로 보내면 JSON 본문이 되므로 받는 쪽은 `@RequestBody` 여야 하고, 폼을 그대로 보내면 `@ModelAttribute` 쪽이다. 값이 비어 들어올 때 보내는 쪽 `Content-Type` 부터 보는 이유가 여기 있다.

1-7에서는 표시를 생략해도 동작하는 자리를 봤는데, **생략할 수 있는 것과 생략하는 편이 나은 것은 다르다.**

| | 생략할 때 | 적어 둘 때 |
| --- | --- | --- |
| 판정 | 스프링이 타입·이름을 보고 짐작한다 | 코드에 그대로 남는다 |
| 이름이 바뀌면 | 값이 조용히 비어 들어올 수 있다 | 이름이 박혀 있어 영향이 없다 |
| 읽는 사람 | 어디서 오는 값인지 되짚어야 한다 | 한 줄로 보인다 |

특히 `@PathVariable(name = "no")` 처럼 이름을 적어 두는 편이 안전하다. 매개변수 이름은 컴파일 옵션에 따라 `.class` 에 안 남을 수 있어서, 이름에 기대는 매칭은 환경이 바뀌면 어긋날 여지가 있다.

`@PathVariable` 은 주소 쪽에 자리 표시가 있어야 짝이 맞는다는 점도 함께 기억해 둘 만하다.

```java
@DeleteMapping("/{no}")
public boolean testDelete(@PathVariable(name = "no") int no) { ... }
// DELETE /test/3
```

매핑 값의 `{no}` 와 표시의 `name` 이 같은 이름을 가리켜야 값이 채워진다. DELETE·GET처럼 본문을 잘 싣지 않는 방식에서 값을 하나 넘길 때 쓰기 좋은 통로다.

### 1-11. 연결 정보를 코드 밖으로 — application.properties

`src/main/resources/application.properties` 에 설정이 몇 줄 붙었다.

```properties
spring.application.name=springweb
# 주석은 # 으로 단다
# 1. 내장 톰캣의 포트 번호, 기본값이 8080
server.port = 8080
# 2. 데이터베이스 연동
spring.datasource.url = jdbc:mysql://localhost:3306/mydb0902
spring.datasource.username=root
spring.datasource.password=****
```

`키=값` 한 줄이 설정 하나다. 주석은 `#` 으로 달고, 값에 따옴표를 두르지 않는다 — 줄 끝까지가 그대로 값이 된다.

Spring day02 스프링 부트 실행과 계층 이식 의 `BaseDao` 에서는 같은 값이 자바 코드 안에 문자열로 박혀 있었다.

```java
private String url = "jdbc:mysql://127.0.0.1:3306/mydb0813";
```

| | 코드 안에 문자열로 | 설정 파일로 |
| --- | --- | --- |
| 값을 바꿀 때 | 소스를 고치고 다시 빌드한다 | 파일 한 줄만 고친다 |
| 환경별로 다를 때 | 코드가 환경에 묶인다 | 파일을 나눠 둘 수 있다 |
| 값을 찾을 때 | 어느 클래스에 있는지 뒤져야 한다 | 한 자리에 모여 있다 |

**바뀌는 이유가 다른 것을 갈라 두는** 것이 요점이다. 코드는 "무엇을 하는가"이고 설정은 "어디에 붙는가"라, 둘이 섞여 있으면 붙는 곳이 달라질 때마다 코드가 흔들린다. 1-5에서 컨트롤러를 얇게 둔 이유와 결이 같다.

이 파일은 `src/main/resources` 아래에 있어서, 빌드하면 클래스패스 루트로 들어간다. 스프링은 뜰 때 이 자리를 스스로 찾아 읽으므로 경로를 적어 줄 필요가 없다.

세 줄로 DB 주소·계정·비밀번호를 적어 두면 스프링이 그 값으로 `DataSource` 를 만들어 둔다. 직접 `Class.forName` 으로 드라이버를 부르고 `DriverManager.getConnection` 을 부르던 자리가 설정 몇 줄로 바뀌는 셈인데, 그렇게 되는 구조는 3-5에서 이어서 본다.

`server.port = 8080` 은 기본값과 같아서 적으나 안 적으나 결과가 같다. 그래도 적어 두면 **어느 포트로 뜨는지가 파일에 드러난다.** 포트가 이미 쓰이고 있으면 시작할 때 걸리므로, 이 줄이 바꿀 자리를 알려 주는 표시가 된다.

한 가지 기억해 둘 것은 **비밀번호가 파일에 그대로 남는다**는 점이다. 이 파일은 소스와 함께 저장소에 올라가므로, 실습용 로컬 계정이라도 값을 그대로 두는 습관은 들이지 않는 편이 안전하다. 2-12에서 이어서 본다.

### 1-12. 표시를 처리해 줄 도구를 선언해 두기 — build.gradle의 의존성

`build.gradle` 의 `dependencies` 블록에 줄이 늘었다.

```gradle
dependencies {
    implementation 'org.springframework.boot:spring-boot-starter-webmvc'
    runtimeOnly   'com.mysql:mysql-connector-j'

    // 롬복
    compileOnly       'org.projectlombok:lombok'
    annotationProcessor 'org.projectlombok:lombok'

    // JPA 준비
    implementation 'org.springframework.boot:spring-boot-starter'
}
```

1-8에서 `TestDto` 에 붙인 롬복 표시 넷이 실제로 동작하려면 이 선언이 있어야 한다. **표시만 붙인다고 코드가 생기지는 않는다** — 그 표시를 읽어 코드를 만들어 주는 도구가 빌드에 끼어 있어야 한다. [[Spring day03 애노테이션과 리플렉션]] 에서 본 애노테이션 프로세서가 여기 등록되는 자리다.

롬복만 두 줄인 이유가 눈에 띈다.

| 줄 | 하는 일 |
| --- | --- |
| `compileOnly` | 컴파일할 때 `@Getter` 같은 표시를 알아보게 한다 |
| `annotationProcessor` | 그 표시를 읽어 getter·setter 코드를 만들어 넣는다 |

**하나는 표시를 알아보는 쪽, 하나는 그 표시를 처리하는 쪽**이다. 둘 중 하나가 빠지면 컴파일이 안 되거나, 컴파일은 되는데 메소드가 안 생긴다.

앞에 붙는 말이 **그 라이브러리가 언제까지 필요한지**를 정한다.

| 앞말 | 컴파일 | 실행 | 결과물에 포함 |
| --- | --- | --- | --- |
| `implementation` | 필요 | 필요 | 포함 |
| `compileOnly` | 필요 | 불필요 | 미포함 |
| `runtimeOnly` | 불필요 | 필요 | 포함 |
| `annotationProcessor` | 코드 생성 단계에만 | 불필요 | 미포함 |
| `testImplementation` | 테스트 컴파일 | 테스트 실행 | 미포함 |

롬복이 `compileOnly` 인 것은 **만들어 낸 코드만 남고 롬복 자신은 남을 필요가 없기** 때문이다. 컴파일이 끝나면 `.class` 에는 평범한 getter·setter가 들어 있어서, 실행할 때 롬복이 있든 없든 같다.

MySQL 드라이버가 `runtimeOnly` 인 것은 반대 사정이다. 코드는 `Connection`·`PreparedStatement` 같은 **JDBC 인터페이스에만 기대고**, 그 구현을 실행 시점에 찾아 쓴다. 컴파일할 때 드라이버 클래스 이름을 코드에 적지 않으니 컴파일에는 필요가 없다.

정리하면 **필요한 구간만큼만 열어 두는 것**이 이 앞말들의 값어치다. 전부 `implementation` 으로 둬도 돌아가기는 하지만, 결과물이 커지고 쓰지 않는 라이브러리가 코드에 노출된다.

마지막 `spring-boot-starter` 는 JPA로 넘어가기 전에 얹어 둔 자리다. 스타터는 라이브러리 하나가 아니라 **같이 쓰는 것들을 묶어 둔 꾸러미**라, 한 줄로 여러 의존성이 함께 딸려 온다.

진입점이 여럿이라 `mainClass` 로 하나를 고르는 줄도 그대로 있다.

```gradle
springBoot {
    mainClass = 'day03.exam.AppStart'
}
```

1-1에서 본 스캔 범위 이야기와 맞물린다. day가 늘수록 `main` 이 늘어나므로, 띄우고 싶은 실습에 맞춰 이 한 줄을 바꾸는 구조가 된다.

### 1-13. 정리 — 되풀이되는 한 벌

한 컨트롤러 안에 다음이 다 들어 있다.

```
클래스 자리   @RestController + @RequestMapping("/test")   ← 공통
메소드 자리   @PostMapping / @GetMapping / @PutMapping / @DeleteMapping   ← 갈리는 것
매개변수      DTO 또는 값 하나                             ← 들어오는 값
본문          DAO에 넘기고 결과를 돌려준다                  ← 하는 일
반환 타입     boolean / 목록 / DTO                        ← 나가는 모양
```

도메인이 바뀌어도 이 다섯 줄의 모양은 그대로고 이름만 갈린다. Spring day02 스프링 부트 실행과 계층 이식 에서 게시판을 만든 뒤 대기명단을 만들 때 손대는 파일이 다섯 개로 정해져 있던 이유가 여기 있다.

여기에 DTO 한 줄을 더하면 한 벌이 채워진다.

```
DTO          필드 + 롬복 표시 넷                          ← 오가는 값의 모양
```

DTO를 먼저 정하고 컨트롤러를 붙이면 **양 끝의 모양부터 맞춰 놓고 안쪽을 채우는** 순서가 된다. 안쪽이 아직 없어도 값을 손으로 만들어 응답을 확인할 수 있어서, 화면 쪽과 맞춰 볼 지점이 일찍 생긴다.

되풀이가 눈에 보인다는 것은 **줄일 자리가 있다**는 신호이기도 하다. 줄이는 방향은 두 갈래다 — 공통 부분을 상위 클래스나 제네릭으로 올리는 쪽(`BaseDao` 가 그랬다), 그리고 아예 코드를 쓰지 않고 규약으로 대신하는 쪽(JPA·`JdbcTemplate`)이다. 3-1에서 이어서 본다.

## 2. 추가로 알면 좋은 활용법

### 2-1. 상세 조회 주소를 어떻게 둘까

목록과 상세가 둘 다 GET이면 주소로 갈라야 한다. 방식이 같으니 주소가 달라야 자리가 갈린다.

```java
@GetMapping()        // GET /test        → 목록
@GetMapping("/test") // GET /test/test   → 상세
```

주소 뒷부분에 이름을 하나 더 붙이는 방식이다. 여기에 [[Spring day03 애노테이션과 리플렉션]] 1-34에서 본 경로 변수를 쓰면 자원을 가리키는 모양이 분명해진다.

```java
@GetMapping("/{no}")
public TestDto testDetail(@PathVariable int no) { ... }
// GET /test/3
```

| 방식 | 주소 모양 | 어울리는 자리 |
| --- | --- | --- |
| 쿼리스트링 | `/test/test?no=3` | 걸러 내는 조건, 정렬, 페이지 |
| 경로 변수 | `/test/3` | **자원을 가리키는 식별자** |

"3번 글 하나"를 가리키는 것은 조건이 아니라 식별자라 경로 쪽이 어울린다. 다만 팀에서 정한 규칙이 있다면 그쪽을 따르는 편이 낫다 — 주소 설계는 옳고 그름보다 **한 프로젝트 안에서 일관된 것**이 더 중요하다.

### 2-2. boolean 대신 상태 코드까지 돌려주기

`boolean` 하나로는 결과를 두 갈래로만 말할 수 있다. HTTP에는 이미 결과를 말하는 자리가 따로 있다.

```java
@PostMapping()
public ResponseEntity<Boolean> testWrite(TestDto testDto) {
    boolean result = td.testWrite(testDto);
    return result
        ? ResponseEntity.status(HttpStatus.CREATED).body(true)
        : ResponseEntity.badRequest().body(false);
}
```

`ResponseEntity` 는 본문뿐 아니라 **상태 코드와 헤더까지** 함께 정한다.

| 상황 | 상태 코드 |
| --- | --- |
| 등록 성공 | 201 Created |
| 조회 성공 | 200 OK |
| 대상 없음 | 404 Not Found |
| 보낸 값이 잘못됨 | 400 Bad Request |
| 서버 쪽 문제 | 500 Internal Server Error |

화면 쪽에서 `axios` 가 `catch` 로 갈라 잡을 수 있는 것도 상태 코드 덕분이다. 200으로 `false` 를 돌려주면 실패인데도 성공 경로로 들어와서, 화면 코드에 판정이 하나 더 늘어난다.

### 2-3. 목록이 비었을 때

조회 결과가 없을 때 `null` 을 돌려주면 화면 쪽에서 반복문이 걸린다. **빈 리스트를 돌려주는 편이 안전하다.**

```java
ArrayList<TestDto> list = new ArrayList<>();
while (rs.next()) { ... }
return list;   // 한 줄도 없으면 빈 리스트가 그대로 나간다
```

빈 리스트는 JSON으로 `[]` 가 되고, 화면의 반복문은 0번 돌고 끝난다. `null` 은 `null` 로 나가서 받는 쪽에서 따로 확인해야 한다. "없음"을 **값의 부재가 아니라 빈 값으로 표현하는** 쪽이 다루기 쉽다.

상세 조회처럼 하나를 찾는 자리는 사정이 다르다. 없을 때 빈 객체를 돌려주면 있는 것처럼 보이므로, 이쪽은 404로 갈라 주는 편이 분명하다.

### 2-4. 매핑이 겹치면 뜨는 순간에 걸린다

같은 주소·같은 방식으로 메소드를 둘 두면 서버가 시작할 때 오류가 난다. 요청이 왔을 때가 아니라 **뜰 때** 걸린다는 점이 중요하다.

[[Spring day03 애노테이션과 리플렉션]] 1-12에서 본 구조 때문이다. 스프링은 시작할 때 애노테이션을 훑어 **주소 → 메소드 표**를 만들어 두는데, 같은 칸에 둘을 넣을 수가 없다. 표를 만드는 단계에서 막히니 실행 전에 드러난다.

컨트롤러를 여러 개 만들다 보면 클래스가 달라도 주소가 겹칠 수 있다. `@RequestMapping` 을 클래스마다 다르게 두면 그 사고 자체가 줄어든다.

### 2-5. DAO를 직접 만들지 않고 받기 — 생성자 주입

1-4에서 남겨 둔 결합도 문제를 푸는 자리다. DAO 쪽에 `@Repository` 를 붙여 빈으로 등록해 두면, 컨트롤러는 만들지 않고 받기만 한다.

```java
@Repository
public class TestDao { ... }

@RestController
@RequestMapping("/test")
@RequiredArgsConstructor
public class TestController {
    private final TestDao td;   // 컨테이너가 넣어 준다
}
```

`final` 로 두고 `@RequiredArgsConstructor` 를 붙이면 그 필드를 받는 생성자가 컴파일 시점에 만들어지고, 스프링이 그 생성자로 객체를 만들면서 빈을 넣어 준다. [[Spring day03 애노테이션과 리플렉션]] 1-15·3-5에서 본 그 조합이다.

| | 직접 만들기 | 생성자 주입 |
| --- | --- | --- |
| 객체를 만드는 주체 | 컨트롤러 | 컨테이너 |
| 코드에 박히는 것 | 구현 클래스 이름 | 필요한 타입 |
| 테스트할 때 | 진짜 DAO가 붙는다 | 가짜를 넣어 볼 수 있다 |

마지막 줄이 실제로 크게 갈린다. `new` 나 `getInstance()` 가 코드 안에 있으면 그 자리를 바꿀 방법이 없는데, 밖에서 받는 구조면 테스트에서 다른 것을 넣어 줄 수 있다.

필드에 `@Autowired` 를 붙이는 방식도 있지만, 생성자 쪽이 **`final` 로 둘 수 있고 의존이 생성자 서명에 드러난다**는 점에서 낫다.

### 2-6. 표시가 안 먹힐 때 보는 순서

매핑을 붙였는데 404가 나오면 다음 순서로 좁혀 가는 편이 빠르다.

1. **컴포넌트 스캔 범위** — 띄운 진입점의 패키지 아래에 컨트롤러가 있는가 (1-1)
2. **클래스 표시** — `@RestController` 나 `@Controller` 가 붙어 있는가
3. **주소** — 클래스 `@RequestMapping` 과 메소드 값이 이어 붙은 실제 주소가 무엇인가
4. **방식** — 브라우저 주소창으로는 GET만 보낼 수 있다

3번이 특히 자주 걸린다. 클래스에 앞머리를 두면 메소드에 적은 값이 전체 주소가 아니게 되는데, 메소드 쪽만 보고 있으면 눈에 안 들어온다. 서버가 뜰 때 찍히는 매핑 목록을 보면 실제 등록된 주소를 확인할 수 있다.

값이 비어 들어오는 경우는 또 다른 갈래다. 보내는 쪽 `Content-Type` 과 받는 쪽 표시가 짝을 이루는지부터 본다 — 폼·쿼리스트링이면 `@ModelAttribute` 계열, JSON 본문이면 `@RequestBody` 다.

### 2-7. 계층마다 이름이 갈려 있다

`@Component` 계열은 하는 일이 같고 이름만 다르다.

| 표시 | 붙는 자리 |
| --- | --- |
| `@Controller`·`@RestController` | 요청을 받는 계층 |
| `@Service` | 업무 규칙을 다루는 계층 |
| `@Repository` | DB와 이야기하는 계층 |
| `@Component` | 그 밖의 빈 |

셋 다 `@Component` 를 품고 있어서 빈 등록이라는 결과는 같다. 그런데도 나눠 둔 것은 **코드를 읽는 사람과 프레임워크 둘 다에게 계층을 알려 주기 위해서**다. `@Repository` 는 DB 예외를 스프링의 예외로 바꿔 주는 처리가 함께 걸리기도 한다.

### 2-8. 매개변수를 여러 개 늘어놓기 전에

값이 둘·셋으로 늘면 매개변수를 계속 늘리는 대신 DTO로 묶는 쪽이 읽기 좋다.

```java
// 값이 늘어날수록 자리가 헷갈린다
public boolean testUpdate(int no, String name, int age) { ... }

// 묶어서 받으면 이름이 코드에 남는다
public boolean testUpdate(TestDto testDto) { ... }
```

[[Spring day03 애노테이션과 리플렉션]] 1-18에서 빌더가 생성자보다 읽기 좋았던 이유와 같다. **위치로만 구분되는 값이 늘어나면 자리를 헷갈릴 여지가 늘어난다.** 값이 하나뿐인 삭제·상세는 매개변수 하나로 두는 편이 간단하다.

### 2-9. DTO에 붙이는 롬복 표시를 어디까지 둘까

`@Data` 하나로 묶는 방식도 있다. 안에 들어 있는 것이 여럿이다.

```
@Data = @Getter + @Setter + @ToString + @EqualsAndHashCode + @RequiredArgsConstructor
```

짧아지는 대신 **필요 없는 것까지 함께 생긴다.** 특히 `@EqualsAndHashCode` 는 모든 필드로 같음을 판정하게 만들고, `@ToString` 은 연관이 얽히면 서로를 찍다가 순환에 빠질 여지가 있다.

| 방식 | 어울리는 자리 |
| --- | --- |
| `@Getter`·`@Setter`·생성자 둘을 따로 붙이기 | 필요한 통로만 열어 두고 싶을 때 |
| `@Data` | 값 그릇으로만 쓰는 간단한 DTO |

붙일 표시를 하나씩 고르면 **무엇 때문에 붙였는지가 코드에 남는다.** 1-8에서 기본 생성자와 전체 생성자를 짝으로 둔 이유가 눈에 보이는 것도 따로 적어 뒀기 때문이다.

`@Setter` 를 아예 빼는 갈래도 있다. 만들어진 뒤에 값이 바뀌지 않는 객체가 다루기 쉬운데, 그러려면 값을 받는 통로가 생성자여야 한다. `@RequestBody` 는 Jackson이 처리하므로 생성자 쪽으로도 맞출 수 있지만, 폼 바인딩(`@ModelAttribute`)은 기본 생성자와 setter를 쓴다. **받는 통로에 따라 열어 둬야 하는 문이 다르다.**

### 2-10. 요청용 DTO와 응답용 DTO를 갈라 두기

지금은 들어올 때도 나갈 때도 `TestDto` 하나를 쓴다. 값이 늘면 이 하나가 두 가지 일을 겸하는 것이 걸리기 시작한다.

| | 요청으로 받을 때 | 응답으로 내보낼 때 |
| --- | --- | --- |
| 번호 | 서버가 만든다 (안 받아도 된다) | 꼭 나가야 한다 |
| 작성일 | 서버가 채운다 | 나가야 한다 |
| 비밀번호 같은 값 | 받아야 한다 | 나가면 안 된다 |

한 클래스로 겸하면 **내보내면 안 되는 값이 응답에 섞이는 사고**가 생길 수 있다. 이름을 나눠 `TestCreateRequest`·`TestResponse` 처럼 두면 각각에 필요한 필드만 남는다.

작은 실습에서는 파일만 늘어 보이지만, 필드가 붙기 시작하면 갈라 두는 값어치가 커진다. 우선 한 클래스로 두더라도 `@JsonIgnore` 로 특정 필드를 응답에서 빼는 방법은 알아 둘 만하다.

### 2-11. 설정값을 코드에서 꺼내 쓰기

`application.properties` 에 적어 둔 값은 코드에서도 읽을 수 있다. 두 갈래가 있다.

```java
@Value("${spring.datasource.url}")
private String url;
```

값 하나를 그 자리에서 꺼내 쓰는 방식이다. 간단한 대신 키 문자열이 코드에 흩어진다.

```java
@ConfigurationProperties(prefix = "spring.datasource")
public class DataSourceProps {
    private String url;
    private String username;
}
```

앞머리가 같은 값들을 **객체 하나로 묶어 받는** 방식이다. 필드 이름과 키 이름이 짝을 이루고, 타입이 안 맞으면 뜰 때 걸린다.

| | `@Value` | `@ConfigurationProperties` |
| --- | --- | --- |
| 받는 단위 | 값 하나 | 앞머리가 같은 값 묶음 |
| 이름이 틀렸을 때 | 그 자리에서 드러난다 | 뜰 때 묶어서 걸린다 |
| 어울리는 자리 | 값 한둘 | 설정 그룹이 커질 때 |

다만 DB 연결 정보처럼 스프링이 **이미 알아서 쓰는 값**은 직접 꺼낼 일이 거의 없다. 스타터가 붙어 있으면 그 값을 읽어 `DataSource` 를 만들어 두기 때문이다. 직접 읽어야 하는 것은 보통 내가 정한 값(외부 API 주소, 업로드 경로 같은 것) 쪽이다.

### 2-12. 비밀번호를 파일에 그대로 두지 않기

`application.properties` 는 소스와 함께 저장소에 올라간다. 계정과 비밀번호를 적어 두면 그 값도 같이 올라간다.

```properties
spring.datasource.username=${DB_USER}
spring.datasource.password=${DB_PASSWORD}
```

`${...}` 로 적어 두면 환경변수나 실행 옵션에서 값을 찾아 채운다. 파일에는 **자리만 남고 값은 남지 않는다.**

값을 바깥에 두는 갈래가 몇 가지 있다.

| 방법 | 값이 있는 곳 |
| --- | --- |
| 환경변수 | 실행하는 컴퓨터의 설정 |
| 실행 옵션 `--spring.datasource.password=…` | 실행 명령 |
| 별도 파일 + `.gitignore` | 로컬에만 있는 파일 |
| 프로파일 분리(`application-local.properties`) | 환경별 파일 |

스프링은 여러 곳에서 같은 키를 찾으면 **우선순위대로 덮어쓴다.** 실행 옵션이 환경변수보다, 환경변수가 파일보다 앞선다. 그래서 파일에는 기본값만 두고 실제 값은 바깥에서 넣는 배치가 가능하다.

한 번 올라간 값은 지워도 이력에 남는다는 점도 기억해 둘 만하다. 실습용 로컬 DB라도 습관을 미리 들여 두는 편이 낫다.

## 3. 더 나아가 알면 좋은 것

### 3-1. Service 계층 — 컨트롤러와 DAO 사이

지금은 컨트롤러가 DAO를 바로 부른다. 값을 검사하거나, 여러 DAO를 묶어 하나의 일로 처리해야 하면 그 자리가 없다.

```
Controller  →  Service  →  Dao
   요청 받기    업무 규칙    DB
```

Service가 생기면 컨트롤러는 더 얇아지고, "주문을 넣으면 재고를 줄이고 이력을 남긴다" 같은 **여러 단계가 하나로 묶여야 하는 일**을 담을 자리가 생긴다. 트랜잭션(`@Transactional`)이 걸리는 자리도 보통 여기다.

작은 실습에서는 계층 하나가 늘어난 만큼 파일만 늘어 보이지만, 규칙이 붙기 시작하면 컨트롤러나 DAO 어느 쪽에도 넣기 애매한 코드가 생긴다. 그때가 Service를 두는 시점이다.

### 3-2. 되풀이를 줄이는 두 방향

1-13에서 본 되풀이를 줄이는 길이 갈린다.

| 방향 | 하는 일 | 예 |
| --- | --- | --- |
| 공통을 위로 올리기 | 상속·제네릭으로 골격을 한 벌만 둔다 | `BaseDao`, 제네릭 `BaseController<T>` |
| 코드를 안 쓰기 | 규약만 적고 구현은 프레임워크가 만든다 | `JdbcTemplate`, JPA·Spring Data |

뒤쪽이 더 멀리 간다. Spring Data JPA는 인터페이스에 메소드 이름만 적어 두면 그 이름을 읽어 쿼리를 만들어 준다 — [[Spring day03 애노테이션과 리플렉션]] 에서 본 "표시를 읽어 동작을 만드는" 구조가 한 단계 더 나간 모양이다.

### 3-3. 요청 값이 규칙에 맞는지 검사하기

지금은 어떤 값이 와도 그대로 DAO까지 내려간다. 검사를 컨트롤러 앞단에 둘 수 있다.

```java
public class TestDto {
    @NotBlank private String name;
    @Min(0)   private int age;
}

@PostMapping()
public boolean testWrite(@Valid TestDto testDto) { ... }
```

`@Valid` 를 붙이면 메소드 본문에 들어오기 **전에** 검사가 돌고, 어긋나면 예외가 난다. DB 제약에 걸려 실패하는 것보다 앞에서 막는 셈이다. 어떤 값이 왜 어긋났는지도 함께 잡을 수 있다.

### 3-4. 예외 처리를 한 자리에 모으기

메소드마다 `try-catch` 를 두는 대신 `@RestControllerAdvice` 로 모아 둘 수 있다.

```java
@RestControllerAdvice
public class GlobalExceptionHandler {
    @ExceptionHandler(Exception.class)
    public ResponseEntity<String> handle(Exception e) {
        return ResponseEntity.status(500).body("처리 중 문제가 생겼습니다");
    }
}
```

컨트롤러는 정상 흐름만 적고, 어긋난 경우의 응답은 한 자리에서 정한다. 응답 모양이 예외마다 제각각이 되는 것도 막을 수 있다.

### 3-5. 설정 몇 줄이 객체가 되는 자리 — 자동 설정

1-11에서 DB 정보를 세 줄 적어 뒀는데, 그 값을 읽어 쓰는 코드는 아직 없다. 그런데도 커넥션이 만들어지는 것은 스프링 부트의 **자동 설정** 때문이다.

```
클래스패스에 드라이버가 있나?      →  있다
spring.datasource.url 이 있나?     →  있다
DataSource 빈이 이미 있나?         →  없다
                                    ↓
            DataSource 를 만들어 등록한다
```

`@SpringBootApplication` 안의 `@EnableAutoConfiguration` 이 이 판정을 돌린다. 조건은 `@ConditionalOnClass`·`@ConditionalOnMissingBean` 같은 표시로 적혀 있어서, [[Spring day03 애노테이션과 리플렉션]] 에서 본 "표시를 읽어 동작을 정하는" 구조가 프레임워크 자신에게도 쓰이는 셈이다.

의존성을 넣는 일이 곧 기능을 켜는 일이 되는 것도 여기서 온다. 1-12에서 스타터 한 줄을 얹은 것이 설정 판정의 입력이 된다. 무엇이 켜졌는지는 실행할 때 `--debug` 를 주면 판정 결과를 목록으로 볼 수 있다.

직접 `Class.forName` 으로 드라이버를 부르고 `DriverManager` 로 커넥션을 꺼내던 자리가 사라지는 것이 이 단계의 값어치인데, **대신 무슨 일이 일어나는지가 코드에 안 보인다**는 것이 뒷면이다. 조건표를 한 번 열어 보는 것이 그 간극을 메우는 방법이 된다.

### 3-6. 다음에 볼 키워드

- `@Service`·`@Transactional` — 업무 규칙 계층과 여러 단계를 한 묶음으로 처리하기
- `JdbcTemplate` — JDBC의 되풀이 코드를 걷어내기
- JPA·Spring Data — 메소드 이름으로 쿼리를 만드는 자리
- `ResponseEntity`·`HttpStatus` — 상태 코드와 헤더까지 돌려주기
- `@Valid`·`BindingResult`·`@NotBlank`·`@Min` — 받은 값 검사하기
- `@RestControllerAdvice`·`@ExceptionHandler` — 예외 처리를 한 자리에 모으기
- `@Repository` 와 예외 변환 — DB 예외를 스프링 예외로 바꾸기
- `@RequiredArgsConstructor`·`final` — 생성자 주입
- Swagger·SpringDoc — 만든 API를 문서로 뽑고 브라우저에서 호출해 보기
- Postman·`curl` — GET 외의 방식을 보내 보는 도구
- `@CrossOrigin`·CORS — 화면을 다른 출처에서 띄울 때
- REST 성숙도 모델 — 주소와 방식만으로 어디까지 표현할 수 있나
- Jackson·`ObjectMapper` — JSON과 객체를 오가는 변환이 실제로 도는 자리
- `@JsonIgnore`·`@JsonProperty`·`@JsonInclude` — 응답에서 필드를 빼거나 키 이름을 바꾸기
- 오토박싱·언박싱과 `NullPointerException` — 래퍼 타입을 산술에 바로 쓸 때
- `Integer` 캐시와 `==` 비교 — 값 비교에 `equals` 를 쓰는 이유
- `Optional` — "없을 수 있음"을 타입으로 드러내기
- `record` — 값만 담는 그릇을 자바 문법으로 만들기 (롬복 없이)
- 요청 DTO·응답 DTO 분리와 엔티티를 그대로 내보내지 않는 이유
- `application.properties` 와 `.yml` 의 표기 차이, 프로파일(`spring.profiles.active`)과 환경별 파일 나누기
- `@Value`·`@ConfigurationProperties` — 설정값을 코드에서 꺼내 쓰기
- 설정 우선순위(실행 옵션 > 환경변수 > 파일)와 `${}` 치환
- `DataSource`·HikariCP — 커넥션 풀이 커넥션을 미리 잡아 두는 자리
- `@EnableAutoConfiguration`·`@ConditionalOnClass`·`spring.factories` — 자동 설정이 판정되는 구조
- 그레이들 의존성 스코프(`implementation`·`compileOnly`·`runtimeOnly`·`annotationProcessor`)
- 애노테이션 프로세서와 컴파일 시점 코드 생성 — 롬복이 실행 결과물에 남지 않는 이유
- 스타터(starter)와 BOM — 버전을 한 자리에서 맞추는 방식

## 실습 파일

- `2026B_Spring/springweb/src/main/java/day04/practice/AppStart.java` (연습 패키지에 진입점 두기, `@SpringBootApplication` 으로 내장 톰캣과 IOC/DI를 함께 켜기, 컴포넌트 스캔 범위가 진입점이 속한 패키지와 하위로 정해지는 규칙이 day마다 폴더를 나누는 실습 구조와 맞물리는 자리, 진입점이 여럿일 때 어느 것을 띄우느냐로 살아나는 컨트롤러가 갈리는 점)
- `2026B_Spring/springweb/src/main/java/day04/practice/TestController.java` (`@RestController` 로 빈 등록·요청 수신·본문 응답을 한 번에 얻기, `@RequestMapping` 을 클래스에 올려 공통 주소 앞머리를 정하고 메소드 값과 이어 붙는 규칙·주소 체계를 한 자리에서 바꾸기, 괄호를 비운 매핑이 클래스 주소를 그대로 쓴다는 점, `@PostMapping`·`@GetMapping`·`@PutMapping`·`@DeleteMapping` 넷을 한 컨트롤러에 모아 CRUD 골격 만들기와 주소는 같고 방식으로 갈리는 구조·넷이 모두 `@RequestMapping(method=…)` 의 합성이라는 점·서블릿의 `doXXX` 와 같은 갈림, 목록과 상세가 둘 다 GET일 때 주소로 갈라 두기, DAO를 멤버변수로 들고 싱글톤 창구로 꺼내 오기와 지역변수로 둘 때와의 갈림·구현 이름이 코드에 박히는 결합도 문제와 생성자 주입으로 푸는 방향, 컨트롤러 본문이 넘기고 받고 돌려주는 세 줄로 같은 모양인 점과 계층별로 맡는 일이 갈리는 이유·이름을 층 사이에 관통시키기, 반환 타입이 응답 모양을 정하는 규칙(`boolean`·`ArrayList<DTO>` 는 JSON 배열·DTO는 JSON 객체)과 DTO 필드 이름이 곧 화면에서 꺼내는 키가 되는 자리·`boolean` 하나로는 0건과 오류를 갈라 보이지 못하는 한계와 `ResponseEntity`·상태 코드로 넓히기, 값을 받는 두 모양(DTO로 통째로 받기·값 하나만 받기)과 표시를 생략할 수 있는 조건·매개변수 이름이 `.class` 에 남지 않을 수 있어 이름을 적어 두는 편이 안전한 이유, 조회 결과가 없을 때 빈 리스트를 돌려주는 편이 다루기 쉬운 점과 상세 조회는 404로 갈라 주는 갈림, 같은 주소·같은 방식이 겹치면 요청 때가 아니라 서버가 뜰 때 걸리는 이유가 주소 표를 미리 만드는 구조와 이어지는 자리, 매핑이 안 먹힐 때 스캔 범위→클래스 표시→이어 붙은 주소→방식 순으로 좁혀 보기, 계층별 표시(`@Controller`·`@Service`·`@Repository`)가 이름만 갈린 `@Component` 라는 점, 매개변수를 늘리는 대신 DTO로 묶어 이름을 남기기, 도메인이 늘어도 다섯 줄의 골격은 그대로고 이름만 갈리는 되풀이와 그것을 줄이는 두 방향, 값이 어디에 실려 오는지 표시로 적어 두기 — `@RequestBody` 로 본문의 JSON 받기·`@RequestParam` 으로 쿼리스트링 받기·`@PathVariable(name=…)` 로 주소 경로의 값 받기와 매핑 값의 자리 표시와 이름을 맞추기·표시를 생략할 수 있는 것과 적어 두는 편이 나은 것의 갈림)
- `2026B_Spring/springweb/src/main/java/day04/practice/TestDto.java` (오가는 값을 담는 그릇을 필드 셋과 롬복 표시 넷으로 만들기, `@NoArgsConstructor`·`@AllArgsConstructor` 를 짝으로 두는 이유 — 전체 생성자를 만들면 기본 생성자가 사라지고 스프링의 바인딩은 빈 객체를 만든 뒤 setter로 채우는 순서라는 점, `@Setter` 가 들어오는 길·`@Getter` 가 나가는 길을 여는 자리와 하나만 빠져도 값이 비어 들어오거나 빈 JSON이 나가는 이유, `@AllArgsConstructor` 로 목록 더미를 한 줄씩 채워 DB 없이 응답 모양부터 확인하기, `int` 와 `Integer` 의 갈림 — 기본형에는 `null` 을 담을 수 없어 "안 보냈다"와 "0을 보냈다"가 같은 모양이 되는 문제와 경계를 넘어오는 값은 래퍼 타입으로 두는 편이 안전한 이유·언박싱 시점의 예외와 `==` 대신 `equals` 로 값 비교하기, `@Data` 묶음과 개별 표시의 갈림·`@Setter` 를 빼는 갈래는 받는 통로가 생성자여야 한다는 점, 요청용 DTO와 응답용 DTO를 갈라 두는 값어치와 내보내면 안 되는 값이 응답에 섞이는 사고)

- `2026B_Spring/springweb/src/main/resources/application.properties` (연결 정보를 코드 밖 설정 파일로 옮기기 — `키=값` 한 줄이 설정 하나이고 주석은 `#`·값에 따옴표를 두르지 않는 규칙, `server.port` 로 내장 톰캣 포트를 파일에 드러내 두기, `spring.datasource.url`·`username`·`password` 세 줄로 DB 연동 정보 적기와 DAO 안에 문자열로 박아 두던 방식과의 갈림 — 값을 바꿀 때·환경별로 다를 때·값을 찾을 때가 각각 어떻게 갈리는지, `src/main/resources` 가 빌드하면 클래스패스 루트가 되어 스프링이 경로 없이 찾아 읽는 자리, 설정값을 코드에서 꺼내 쓰는 두 갈래(`@Value` 로 값 하나·`@ConfigurationProperties` 로 앞머리가 같은 묶음)와 스프링이 이미 쓰는 값은 직접 읽을 일이 적은 이유, 비밀번호를 파일에 그대로 두지 않기 — `${}` 치환·환경변수·실행 옵션·프로파일 분리와 설정 우선순위·한 번 올라간 값은 이력에 남는다는 점)
- `2026B_Spring/springweb/build.gradle` (표시를 처리해 줄 도구를 의존성으로 선언해 두기 — 롬복 표시를 붙여도 애노테이션 프로세서가 빌드에 끼어 있어야 코드가 생긴다는 점과 `compileOnly`(표시를 알아보는 쪽)·`annotationProcessor`(표시를 읽어 코드를 만드는 쪽) 두 줄이 짝인 이유, 의존성 앞말이 그 라이브러리가 필요한 구간을 정하는 규칙 — `implementation`·`compileOnly`·`runtimeOnly`·`annotationProcessor`·`testImplementation` 의 컴파일·실행·결과물 포함 여부, 롬복이 결과물에 남지 않아도 되는 이유와 MySQL 드라이버가 `runtimeOnly` 인 반대 사정(JDBC 인터페이스에만 기대고 구현은 실행 시점에 찾는다), 스타터가 라이브러리 하나가 아니라 같이 쓰는 것들의 꾸러미라는 점과 JPA로 넘어가기 전 얹어 두는 자리, 진입점이 여럿일 때 `springBoot { mainClass }` 로 띄울 실습을 고르는 줄과 컴포넌트 스캔 범위 이야기의 맞물림, 의존성을 넣는 일이 곧 기능을 켜는 일이 되는 자동 설정 구조와 `--debug` 로 판정 결과 확인하기)

## 관련 노트

[[Spring MOC]] · [[Spring day03 애노테이션과 리플렉션]] · Spring day02 스프링 부트 실행과 계층 이식 · Spring day01 서블릿과 HTTP 메소드 · Spring Boot 프로젝트 생성(분석) · Java MOC · Java day11 인터페이스 · Java day12 종합예제 JDBC DAO · Java day15 Map과 HashMap · JS day14 게시판 CRUD · [[개념 - CRUD]] · [[개념 - 싱글톤]] · [[KDT_2026 학습 지도]]
