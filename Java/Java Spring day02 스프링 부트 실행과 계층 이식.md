---
출처: Claude 분석
원본: KDT_2026/2026B_Spring/springweb/src/main/java/day02, springweb/build.gradle
작성일: 2026-08-26
tags: [학습, java]
---

# Java Spring day02 — 스프링 부트 실행과 계층 이식

> 실습 파일: `2026B_Spring/springweb/src/main/java/day02/AppStart.java`, `Controller/BoardController.java`, `Model/Dao/BaseDao.java`, `Model/Dao/BoardDao.java`, `Model/Dto/BoardDto.java`, `sample.sql`, `springweb/build.gradle`
> 허브: [[Java MOC]] · 이전: [[Java Spring day01 서블릿과 HTTP 메소드]]

[[Java Spring day01 서블릿과 HTTP 메소드]] 에서 요청을 받는 자리(서블릿)를 만들어 봤다. 이번에는 방향을 한 번 되짚어서, **스프링 부트 애플리케이션을 직접 띄우는 진입점**을 만들고 그 아래에 콘솔에서 쓰던 MVC 계층을 그대로 옮겨 온다.

파일 여섯 개가 나오는데 역할이 뚜렷하게 갈린다.

| 파일 | 자리 |
| --- | --- |
| `AppStart.java` | 프로그램의 시작점 — 서버를 띄운다 |
| `Controller/BoardController.java` | 요청을 받아 DAO를 부르는 자리 |
| `Model/Dao/BaseDao.java` | JDBC 연동을 물려주는 부모 |
| `Model/Dao/BoardDao.java` | 게시판 DB 처리 담당 |
| `Model/Dto/BoardDto.java` | 표 한 줄을 담는 그릇 |
| `sample.sql` | 실습용 DB·테이블 준비 |

[[Java day12 종합예제 JDBC DAO]] 에서 만든 구조와 거의 같다. 달라진 것은 `main` 이 콘솔 메뉴를 돌리는 대신 **서버를 띄운다**는 것, 그리고 컨트롤러가 메뉴 번호 대신 **주소로 요청을 받는다**는 것 둘이다. 먼저 등록 요청 하나가 브라우저에서 DB까지 닿고, 이어서 조회·수정·삭제를 같은 모양으로 채워 [[개념 - CRUD]] 네 가지가 모두 웹 요청으로 이어진다(1-13~1-16).

## 1. 배운 내용

### 1-1. 프레임워크 — 도구와 틀을 미리 받아 놓고 시작한다

스프링은 라이브러리가 아니라 **프레임워크**다. 두 낱말이 자주 섞여 쓰이는데 갈리는 지점은 "누가 흐름을 잡는가"다.

| | 라이브러리 | 프레임워크 |
| --- | --- | --- |
| 흐름의 주인 | 내 코드 | 프레임워크 |
| 쓰는 방식 | 필요할 때 내가 부른다 | 내가 만든 것을 프레임워크가 부른다 |
| 예 | `Math`·`Scanner` | 스프링·안드로이드 |

[[Java Spring Boot 프로젝트 생성(분석)]] 3-1에서 제어의 역전으로 정리한 성질이 그대로다. 지금까지는 `main` 이 처음부터 끝까지 흐름을 쥐고 있었는데, 스프링을 쓰면 `main` 은 **시동만 걸고 물러난다.** 이후로는 요청이 들어올 때마다 스프링이 내 메소드를 불러 준다.

그래서 프레임워크를 쓴다는 것은 "편한 함수를 가져다 쓴다"가 아니라 **정해진 틀 안에 내 코드를 끼워 넣는다**에 가깝다. 틀이 정해져 있는 만큼 자유도는 줄지만, 서버·요청 처리·연결 관리 같은 반복 작업을 직접 만들지 않아도 된다.

### 1-2. 애노테이션 — 코드에 붙이는 표시

`@` 로 시작하는 표시를 애노테이션이라고 한다. 코드에 **추가 의미를 붙여 두는 라벨**이다.

주석과 헷갈리기 쉬운데 성격이 다르다.

| | 주석 (`//`) | 애노테이션 (`@`) |
| --- | --- | --- |
| 읽는 대상 | 사람 | 컴파일러·프레임워크 |
| 컴파일 후 | 사라진다 | 클래스 정보로 남는다 |
| 동작에 영향 | 없다 | 있다 |

[[Java day13 Object 클래스와 리플렉션]] 에서 `Class` 로 클래스의 멤버 정보를 읽어 보는 것을 다뤘는데, 애노테이션이 실제로 동작하는 방식이 그것이다. 프레임워크가 시작할 때 클래스들을 훑어 붙어 있는 표시를 읽고, 그에 맞춰 등록·설정을 한다. 애노테이션 자체는 아무 일도 하지 않고, **그것을 읽는 쪽이 따로 있다**는 점이 핵심이다.

이미 만난 것들을 모아 두면 이렇다.

| 애노테이션 | 읽는 주체 | 의미 |
| --- | --- | --- |
| `@Override` | 컴파일러 | 부모 메소드를 덮어쓴다 |
| `@SpringBootApplication` | 스프링 | 여기가 시작 클래스다 |
| `@WebServlet("/board")` | 서블릿 컨테이너 | 이 주소를 이 클래스가 받는다 |

### 1-3. @SpringBootApplication — 표시 하나로 준비가 끝난다

시작 클래스에 붙이는 표시다. 이것 하나에 세 가지가 묶여 있다.

| 안에 든 것 | 하는 일 |
| --- | --- |
| `@SpringBootConfiguration` | 이 클래스를 설정 클래스로 삼는다 |
| `@EnableAutoConfiguration` | 의존성에 있는 것을 보고 **자동으로 설정**한다 |
| `@ComponentScan` | 이 클래스가 있는 패키지부터 아래로 훑어 컴포넌트를 등록한다 |

실제로 눈에 보이는 결과는 두 가지다.

- **내장 톰캣이 자동으로 세팅된다** — 서버를 따로 설치하거나 war 를 배포할 필요가 없다
- **컨트롤러·컴포넌트가 자동으로 등록된다** — 클래스를 만들어 두면 스프링이 찾아 관리한다

두 번째가 [[Java Spring day01 서블릿과 HTTP 메소드]] 1-7에서 주소를 일일이 등록하던 것과 대비되는 자리다. 서블릿 시절에는 "이 클래스를 이 주소에 붙여 달라"고 직접 말해야 했는데, 스프링은 **표시를 붙여 두면 찾아서 등록한다.**

`@ComponentScan` 의 범위가 "시작 클래스가 있는 패키지부터 아래"라는 점은 기억해 둘 만하다. 클래스를 만들어도 그 범위 밖에 있으면 스프링이 알지 못한다.

### 1-4. SpringApplication.run — 시동을 거는 한 줄

```java
public class AppStart {
    public static void main(String[] args) {
        SpringApplication.run(AppStart.class);
    }
}
```

이름이 비슷한 둘을 갈라 둔다.

| 이름 | 정체 | 쓰는 자리 |
| --- | --- | --- |
| `@SpringBootApplication` | 애노테이션 | 클래스 위에 붙이는 표시 |
| `SpringApplication` | 클래스 | `run()` 을 부르는 실행 도구 |

표시를 붙이는 쪽과 실행하는 쪽이 따로 있는 구조다. 표시만 붙이면 아무것도 뜨지 않고, `run()` 만 부르면 무엇을 설정해야 할지 알 수 없다.

`run()` 에 넘기는 `AppStart.class` 는 [[Java day13 Object 클래스와 리플렉션]] 에서 본 **클래스 메타정보**다. 인스턴스가 아니라 "이 클래스가 어떻게 생겼는지"를 담은 객체이고, 스프링은 이것으로 붙어 있는 애노테이션과 패키지 위치를 읽는다.

```
SpringApplication.run(AppStart.class)
        │
        ├─ AppStart.class 의 애노테이션을 읽는다
        ├─ 패키지 위치를 기준으로 컴포넌트를 훑는다
        ├─ 스프링 컨테이너를 만들고 빈을 등록한다
        └─ 내장 톰캣을 띄운다  →  8080 포트에서 대기
```

`run()` 이 반환하는 것은 `ApplicationContext` — 스프링 컨테이너 자체다. 필요하면 받아서 등록된 빈을 꺼내 볼 수 있다.

```java
ApplicationContext ctx = SpringApplication.run(AppStart.class, args);
```

`main` 의 매개변수 `args` 를 함께 넘기는 형태도 자주 쓴다. 실행할 때 준 옵션(`--server.port=9090` 같은 것)을 스프링이 설정으로 읽어 주기 때문이다.

### 1-5. 실행 확인 — localhost와 8080

서버가 뜨면 브라우저에서 확인한다.

```
http://localhost:8080
http://127.0.0.1:8080
```

둘은 같은 곳을 가리킨다.

| 표기 | 뜻 |
| --- | --- |
| `127.0.0.1` | 자기 자신을 가리키는 IP (루프백 주소) |
| `localhost` | 그 IP에 붙은 이름 |

이름이 IP로 바뀌는 과정이 DNS인데, `localhost` 만은 밖에 물어보지 않고 컴퓨터 안에서 바로 해결된다. 네트워크가 끊겨 있어도 접속되는 이유다.

`8080` 은 포트 번호다. 한 컴퓨터 안에서 **여러 프로그램을 구분하는 번호**라, 이미 그 번호를 쓰고 있는 프로그램이 있으면 새로 뜨지 못한다. 스프링 부트 프로젝트를 두 개 이상 동시에 켤 수 없는 것도 같은 이유고, 겹칠 때는 포트를 바꿔 주면 된다(2-1).

주소를 등록하지 않은 상태에서 접속하면 오류 화면이 나온다. [[Java Spring day01 서블릿과 HTTP 메소드]] 2-3의 404 — 서버는 떠 있는데 그 주소를 담당할 자리가 없다는 뜻이라, **서버가 죽은 것과는 다른 상태**다.

### 1-6. 패키지로 계층을 나눈다

폴더 구조가 눈에 띈다.

```
day02/
├── AppStart.java
├── Controller/
│   └── BoardController.java
├── Model/
│   ├── Dao/
│   │   ├── BaseDao.java
│   │   └── BoardDao.java
│   └── Dto/
│       └── BoardDto.java
└── sample.sql
```

[[Java day09 MVC 종합예제]] 에서 View·Controller·DAO·DTO로 나눈 것이 폴더로 그대로 옮겨졌다. 달라진 점은 **View 폴더가 없다**는 것이다. 콘솔에서는 `Scanner` 로 입력을 받는 View 클래스가 필요했는데, 웹에서는 그 자리를 브라우저가 맡는다.

| 계층 | 콘솔 | 웹 |
| --- | --- | --- |
| View | View 클래스 (`Scanner`·`println`) | 브라우저 |
| Controller | 메뉴 번호로 분기 | 주소 + HTTP 방식으로 분기 |
| DAO | 그대로 | 그대로 |
| DTO | 그대로 | 그대로 |

아래 두 계층이 손댈 것 없이 그대로 온다는 점이 계층을 나눠 둔 값어치다. 입구가 콘솔에서 웹으로 바뀌었는데 DB 처리 코드는 바뀌지 않는다.

패키지 이름을 `Model` 로 묶어 둔 것도 봐 둔다. MVC의 M은 **데이터와 그 처리**를 뭉뚱그린 이름이라, 그 안에서 다시 DAO(처리)와 DTO(데이터)로 나뉜다.

### 1-7. BaseDao — 연동을 상속으로 물려준다

```java
public class BaseDao {
    private String url = "jdbc:mysql://127.0.0.1:3306/mydb0813";
    private String user = "root";
    private String password = "****";   // 실습용 로컬 값

    protected Connection conn;

    private void connect() {
        try {
            Class.forName("com.mysql.cj.jdbc.Driver");
            conn = DriverManager.getConnection(url, user, password);
        } catch (Exception e) {
            System.out.println("DB연동실패" + e);
        }
    }

    protected BaseDao() {
        connect();
    }
}
```

[[Java day12 종합예제 JDBC DAO]] 에서 만든 것과 같은 형태다. 짚을 점을 다시 정리해 둔다.

**① 접근제한자를 나눠 쓴 이유**

| 대상 | 제한자 | 이유 |
| --- | --- | --- |
| `url`·`user`·`password` | `private` | 밖에서 볼 필요가 없다 |
| `conn` | `protected` | **자식 DAO가 써야 한다** |
| `connect()` | `private` | 생성자에서만 부른다 |
| 생성자 | `protected` | 자식만 부를 수 있게 |

`protected` 는 [[Java day08 접근제한자와 static]] 에서 정리한 대로 **상속 관계면 다른 패키지에서도 접근을 허용**하는 자리다. `BaseDao` 와 `BoardDao` 가 같은 패키지에 있더라도, 상속으로 물려주는 것이 목적이라면 `protected` 를 쓰는 편이 뜻이 분명하다.

**② `Class.forName()` 이 하는 일**

```java
Class.forName("com.mysql.cj.jdbc.Driver");
```

문자열로 클래스를 찾아 메모리에 올린다. [[Java day13 Object 클래스와 리플렉션]] 의 리플렉션이 쓰이는 자리다. 드라이버 클래스는 로드되는 순간 스스로를 `DriverManager` 에 등록하도록 만들어져 있어서, 이 한 줄만으로 준비가 끝난다.

내 코드에 MySQL 클래스 이름이 직접 등장하지 않는다는 점이 요점이다. 문자열만 바꾸면 다른 DB로 갈아탈 수 있는 구조라, [[Java day11 인터페이스]] 에서 정리한 "규격에 기대고 구현은 갈아끼운다"가 라이브러리 수준에서 나타난 형태다.

**③ 생성자에 연동을 넣은 이유**

`BaseDao` 를 물려받은 DAO는 만들어지는 순간 자동으로 연결된다. 자식 생성자가 실행될 때 부모 생성자가 먼저 불리는 [[Java day10 상속과 다형성]] 의 성질을 그대로 쓴 것이다.

```
BoardDao 생성  →  (자동) BaseDao 생성자  →  connect()  →  conn 준비 완료
```

DAO가 여러 개로 늘어나도 연동 코드를 한 번만 쓰면 된다는 것이 상속으로 묶어 둔 값어치다.

**④ 연결 정보를 코드에 적어 둔 상태**

지금은 주소·계정·비밀번호가 자바 파일 안에 문자열로 들어 있다. 실습에서는 편하지만, 값이 바뀔 때마다 컴파일을 다시 해야 하고 **소스와 함께 저장소에 올라간다**는 성질이 따라온다. 설정 파일로 빼는 방법은 2-2에 정리한다.

연결 정보에서 자주 걸리는 자리를 미리 적어 두면, URL 끝의 **DB 이름이 스크립트로 만든 DB와 같아야 한다**는 것이다. 실습마다 DB를 새로 만들다 보면 스크립트 쪽만 이름이 바뀌기 쉬운데, 이때 나오는 오류는 접속 실패가 아니라 "그런 DB가 없다"라 원인이 눈에 잘 띄지 않는다. 값이 한 군데에만 있어야 어긋나지 않는다는 점이 설정을 밖으로 빼는 또 다른 이유가 된다.

### 1-8. BoardDao — 상속과 싱글톤을 겹쳐 쓴다

```java
public class BoardDao extends BaseDao {
    private BoardDao() { }

    private static final BoardDao instance = new BoardDao();

    public static BoardDao getInstance() {
        return instance;
    }
}
```

짧지만 두 가지가 겹쳐 있다.

- `extends BaseDao` — 연동을 물려받는다(1-7)
- 싱글톤 — 객체를 하나만 만들어 돌려쓴다

[[개념 - 싱글톤]] 의 세 요소가 그대로 보인다.

| 요소 | 코드 | 막는 것 |
| --- | --- | --- |
| `private` 생성자 | `private BoardDao() { }` | 밖에서 `new` 하는 것 |
| `static` 인스턴스 | `private static final BoardDao instance = ...` | 여러 개가 생기는 것 |
| `static` 반환 메소드 | `getInstance()` | 접근 경로가 흩어지는 것 |

DAO를 싱글톤으로 두는 이유가 여기서 더 분명해진다. `BaseDao` 를 물려받은 이상 **객체 하나 = DB 연결 하나**라, `new BoardDao()` 를 부를 때마다 연결이 새로 생긴다. 연결은 만드는 비용이 큰 자원이라 하나를 만들어 돌려쓰는 편이 낫다.

`final` 을 붙인 것도 봐 둔다. [[Java day08 접근제한자와 static]] 에서 정리한 대로 한 번 대입하면 바꿀 수 없어서, 인스턴스가 중간에 갈아치워질 여지를 없앤다.

이 방식은 클래스가 처음 로드될 때 인스턴스가 만들어진다(이른 초기화). 쓰이든 안 쓰이든 미리 만들어지는 대신, [[Java day16 스레드 동기화]] 에서 본 경쟁 상태를 신경 쓰지 않아도 된다는 성질이 따라온다. 여러 스레드가 동시에 `getInstance()` 를 불러도 이미 만들어진 것을 돌려주기만 하기 때문이다.

### 1-9. BoardController — 웹 기능을 애노테이션으로 단다

```java
@Controller
public class BoardController {
    private BoardDao bd = BoardDao.getInstance();

    // [1] 등록
    @PostMapping("/board/save")
    public boolean save(BoardDto boardDto) {
        boolean result = bd.save(boardDto);
        return result;
    }
}
```

컨트롤러가 DAO를 **직접 만들지 않고 `getInstance()` 로 받아 온다**는 것이 배선의 시작점이고, 그 위에 웹 기능이 얹혔다.

**① 서블릿 기능을 상속 대신 표시로 받는다**

[[Java Spring day01 서블릿과 HTTP 메소드]] 에서는 `HttpServlet` 을 물려받아 `doGet`·`doPost` 를 덮어써야 했다. 스프링에서는 클래스 위에 `@Controller` 를 붙이는 것으로 같은 자리를 만든다.

| | 서블릿 방식 | 스프링 방식 |
| --- | --- | --- |
| 웹 기능 얻기 | `extends HttpServlet` | `@Controller` |
| 요청 구분 | `doGet`·`doPost` 재정의 | 메소드마다 매핑 표시 |
| 주소 지정 | `@WebServlet("/board")` — 클래스에 하나 | 메소드마다 따로 |

갈리는 지점이 분명하다. 상속은 [[Java day10 상속과 다형성]] 에서 정리한 대로 부모를 하나밖에 못 두는데, 표시는 그런 제약이 없다. 게시판을 처리하려고 부모 자리를 써 버리는 대신, 클래스는 비워 두고 라벨만 붙이는 방식이다.

**② @Controller와 @RestController**

둘 다 요청을 받는 자리지만, 메소드가 돌려준 값을 해석하는 방식이 다르다.

| 표시 | 반환값을 무엇으로 보는가 |
| --- | --- |
| `@Controller` | 보여 줄 **화면(뷰)의 이름** |
| `@RestController` | **데이터 그 자체** (주로 JSON) |

`@RestController` 는 `@Controller` + `@ResponseBody` 를 합쳐 둔 것이다. 값을 그대로 응답 본문으로 내보내고 싶으면 클래스에 `@RestController` 를 쓰거나 메소드에 `@ResponseBody` 를 붙인다(2-8).

**③ Content-Type — 몸통에 실린 것이 무엇인지 알리는 규칙**

HTTP는 데이터를 실어 보낼 때 그 형태를 헤더로 함께 알려 준다. 받는 쪽은 이 값을 보고 어떻게 읽을지 정한다.

| Content-Type | 실리는 형태 |
| --- | --- |
| `text/html` | HTML 문서 |
| `application/json` | `{"content":"안녕하세요","writer":"유재석"}` |
| `application/x-www-form-urlencoded` | `content=안녕하세요&writer=유재석` (폼 기본값) |
| `multipart/form-data` | 파일이 섞인 폼 |

목록에 **DTO라는 형태는 없다**는 점이 요점이다. 네트워크로 오가는 것은 어디까지나 문자열이고, DTO는 그 문자열을 받은 쪽에서 담아 두는 자바 그릇이다. 문자열 ↔ 객체를 옮기는 일은 스프링이 맡는다(⑤).

**④ @PostMapping — 메소드마다 주소를 붙인다**

[[Java Spring day01 서블릿과 HTTP 메소드]] 1-6의 HTTP 방식과 CRUD 표가 그대로 짝을 이룬다.

| 표시 | HTTP 방식 | 쓰는 자리 |
| --- | --- | --- |
| `@GetMapping` | GET | 조회 |
| `@PostMapping` | POST | 등록 |
| `@PutMapping` | PUT | 수정 |
| `@DeleteMapping` | DELETE | 삭제 |

넷 다 `@RequestMapping(value = "...", method = RequestMethod.POST)` 의 줄임 표기다.

주소와 방식이 **함께** 자리를 정한다는 점을 봐 둔다. `/board/save` 라는 같은 주소라도 GET으로 오는 것과 POST로 오는 것은 다른 메소드가 받는다. 콘솔 게시판에서 메뉴 번호로 갈랐던 자리가 웹에서는 이 두 값으로 갈린다.

**⑤ 매개변수로 DTO를 받는다 — 커맨드 객체**

메소드 매개변수에 DTO를 두면, 스프링이 요청에 실려 온 값을 **이름을 맞춰** 채워 준다.

```
POST /board/save
content=안녕하세요&writer=유재석
        │
        ├─ new BoardDto()             ← 기본 생성자로 빈 객체
        ├─ setContent("안녕하세요")    ← 이름이 같은 setter를 찾아 부른다
        └─ setWriter("유재석")
                │
                ▼
        save(BoardDto boardDto) 로 전달
```

1-12에서 기본 생성자와 setter를 남겨 둔 이유가 여기서 드러난다. 값을 다 아는 상태에서 한 번에 만드는 것이 아니라 **빈 객체를 만들어 두고 하나씩 채우는** 흐름이라, 매개변수 없는 생성자가 있어야 시작할 수 있다. setter를 이름으로 찾아 부르는 것은 [[Java day13 Object 클래스와 리플렉션]] 의 자리다.

그래서 **필드 이름과 폼의 `name` 이 같아야** 값이 들어온다. 이름으로 짝을 짓는 방식이라 철자가 어긋나면 그 값만 조용히 비어 있게 된다.

**⑥ 요청이 DB까지 닿는 한 줄**

```
브라우저 ──POST /board/save──▶ BoardController ──save()──▶ BoardDao ──상속──▶ BaseDao ──JDBC──▶ MySQL
```

[[Java day09 MVC 종합예제]] · [[Java day12 종합예제 JDBC DAO]] 에서 만든 배선의 입구만 콘솔에서 웹으로 바뀐 형태다.

컨트롤러가 DAO를 필드로 들고 있다는 점은 함께 기억해 둘 만하다. 컨트롤러 객체도 보통 하나만 만들어져 여러 요청이 공유하므로, **여기에 요청별 데이터를 담으면 안 된다** — day01 1-4에서 정리한 무상태 원칙이다. 요청마다 달라지는 값은 매개변수로 받고(⑤), DAO처럼 요청과 무관한 것만 필드로 둔다.

### 1-10. BoardDao — 등록 기능을 채운다

컨트롤러가 부를 자리가 생겼으니 DAO에 실제 SQL이 들어간다.

```java
public boolean save(BoardDto boardDto) {
    try {
        // 1. SQL 작성
        String sql = "insert into board( content , writer ) values( ? , ? )";
        // 2. SQL 기재 — 자바가 아니라 MySQL 서버로 보낼 문장이다
        PreparedStatement ps = conn.prepareStatement(sql);
        // 3. 비워 둔 자리에 값 채우기
        ps.setString(1, boardDto.getContent());
        ps.setString(2, boardDto.getWriter());
        // 4. 실행
        int result = ps.executeUpdate();
        // 5. 결과 판정
        if (result == 1) {
            return true;
        }
    } catch (SQLException e) {
        System.out.println(e);
    }
    return false;
}
```

[[Java day12 예외 처리와 JDBC]] 에서 정리한 다섯 단계가 그대로 나온다. 단계별로 짚을 것이 하나씩 있다.

**① SQL은 자바 문법이 아니다**

`sql` 은 그저 문자열이다. 자바는 이 문장을 해석하지 않고 **MySQL 서버로 보내기만** 한다. 그래서 SQL이 틀려도 컴파일은 통과하고, 실행할 때 서버가 거절하면서 예외가 된다. 컴파일러가 잡아 주지 않는 영역이라 문자열을 만들 때 특히 조심한다.

**② `?` 로 비워 두고 나중에 채운다**

`PreparedStatement` 는 **뼈대를 먼저 보내 두고 값을 따로 채우는** 방식이다.

| | 문자열을 이어 붙이는 방식 | `?` 바인딩 |
| --- | --- | --- |
| 따옴표·이스케이프 | 직접 챙긴다 | 라이브러리가 처리 |
| 타입 변환 | 직접 맞춘다 | `setString`·`setInt` 로 지정 |
| 값이 문장 구조를 바꾸는 것 | 막을 수 없다 | 막힌다 |

세 번째 줄이 핵심이다. 값을 이어 붙여 문장을 만들면 값 안에 든 따옴표나 SQL 조각이 **문장 구조 자체를 바꿔 버릴 수 있다.** `?` 로 비워 두면 뼈대가 이미 정해진 뒤에 값이 들어가므로 값은 값으로만 남는다. 이것이 SQL 인젝션을 막는 기본 방법이라, 사용자 입력이 SQL에 닿는 자리에서는 예외 없이 이 형태를 쓴다.

인덱스가 **1부터** 시작한다는 점도 봐 둔다. [[Java day04 제어문과 배열]] 의 배열과 반대라 헷갈리기 쉬운 자리다.

**③ 실행 메소드가 둘로 갈린다**

| 메소드 | 쓰는 SQL | 반환 |
| --- | --- | --- |
| `executeUpdate()` | `insert`·`update`·`delete` | 바뀐 줄 수 (`int`) |
| `executeQuery()` | `select` | `ResultSet` |

등록은 표를 바꾸는 쪽이라 `executeUpdate()` 다. 돌려주는 숫자가 **실제로 바뀐 줄 수**라, 한 줄을 넣었으면 1이 온다. `result == 1` 로 성공을 판정하는 형태가 여기서 나온다.

`update`·`delete` 에서는 이 숫자가 더 쓸모 있다. 조건에 맞는 줄이 없으면 오류가 아니라 **0**이 오기 때문에, 예외가 나지 않아도 "아무것도 안 바뀌었다"를 이 값으로 알 수 있다.

**④ 성공 여부를 `boolean` 으로 돌려준다**

DAO가 `boolean` 을 돌려주면 컨트롤러는 SQL을 몰라도 결과만 보고 다음을 정할 수 있다. [[Java day09 MVC 종합예제]] 에서 계층을 나눈 목적이 이 반환 타입에 드러난다 — 위 계층은 **무슨 일이 됐는지**만 알고, 어떻게 했는지는 아래에 남는다.

**⑤ `SQLException` 은 검사 예외다**

JDBC 메소드들은 `SQLException` 을 던지도록 선언돼 있어서, `try-catch` 로 감싸지 않으면 컴파일이 되지 않는다. [[Java day12 예외 처리와 JDBC]] 에서 정리한 검사 예외의 성질이다.

`catch` 에서 출력만 하고 넘어가는 형태는 실습에서 흐름을 보기 편하지만, 문제가 콘솔에만 남고 부른 쪽은 `false` 하나만 받게 된다는 성질이 따라온다. 실제로는 로그로 남기거나 예외를 감싸 올려 보내는 쪽으로 간다(2-9).

### 1-11. sample.sql — 표를 먼저 만든다

```sql
DROP DATABASE IF EXISTS mydb0826;
CREATE DATABASE mydb0826;
USE mydb0826;

CREATE TABLE board(
    no int AUTO_INCREMENT,
    content VARCHAR(255),
    writer VARCHAR(30),
    constraint PRIMARY KEY( no )
);

insert into board( content, writer )
values ( "안녕하세요", "유재석" ), ( "하하", "강호동" );
```

[[SQL day02 테이블과 제약조건]] 에서 정리한 것이 그대로 쓰였다.

| 구문 | 하는 일 |
| --- | --- |
| `DROP DATABASE IF EXISTS` | 있으면 지운다 — 다시 실행해도 같은 결과가 되게 |
| `AUTO_INCREMENT` | 번호를 자동으로 1씩 올린다 |
| `constraint PRIMARY KEY(no)` | 중복·`NULL` 을 막고 한 줄을 식별한다 |
| `insert ... values (...), (...)` | 한 문장으로 여러 줄 넣기 |

`DROP` 을 앞에 둔 형태가 실습 스크립트의 관용구다. 몇 번을 실행해도 항상 같은 상태에서 시작하므로 `#멱등성` 을 가진다. 다만 **있던 데이터가 사라진다**는 뜻이기도 해서, 실습용 DB에서만 쓰는 형태다.

### 1-12. DTO와 표가 짝을 이룬다

```java
public class BoardDto {
    private int no;
    private String content;
    private String writer;

    public BoardDto() { }

    public BoardDto(int no, String content, String writer) {
        this.no = no;
        this.content = content;
        this.writer = writer;
    }
    // getter · setter · toString
}
```

`sample.sql` 의 컬럼 셋과 필드 셋이 정확히 맞물린다.

| DB 컬럼 | 타입 | DTO 필드 | 타입 |
| --- | --- | --- | --- |
| `no` | `int` | `no` | `int` |
| `content` | `VARCHAR(255)` | `content` | `String` |
| `writer` | `VARCHAR(30)` | `writer` | `String` |

[[Java day08 접근제한자와 static]] 의 캡슐화 형태 그대로다 — 필드는 `private`, 접근은 getter·setter로 한다. `ResultSet` 에서 값을 꺼내 담을 때 setter가, 화면으로 내보낼 때 getter가 쓰인다.

생성자가 둘인 것도 이유가 있다.

| 생성자 | 쓰는 자리 |
| --- | --- |
| 기본 생성자 `BoardDto()` | 빈 객체를 만들고 setter로 채울 때 |
| 전체 생성자 | 값이 다 있을 때 한 번에 |

기본 생성자를 남겨 두는 습관은 앞으로 계속 쓰인다. 1-9 ⑤에서 본 커맨드 객체 바인딩이 이미 그 자리이고, 같은 방식이 쓰이는 곳은 2-5에 모아 뒀다. [[Java day06 생성자와 콘솔 게시판]] 에서 정리한 대로 생성자를 하나라도 직접 만들면 기본 생성자가 자동으로 생기지 않으므로, 필요하면 직접 적어 둬야 한다.

`toString()` 재정의는 [[Java day13 Object 클래스와 리플렉션]] 의 자리다. 객체를 그대로 출력했을 때 주소 대신 내용이 보이게 하는 것이라, 콘솔로 확인하며 만드는 동안 특히 편하다.

### 1-13. @RestController — 반환값을 데이터로 내보낸다

컨트롤러에 붙는 표시가 `@Controller` 에서 `@RestController` 로 바뀐다.

```java
@RestController
public class BoardController {
    private BoardDao bd = BoardDao.getInstance();
    ...
}
```

1-9 ②에서 갈라 둔 자리가 실제로 갈리는 지점이다. `@Controller` 는 메소드가 돌려준 값을 **보여 줄 화면의 이름**으로 읽는다. 그런데 이 컨트롤러의 메소드들은 `boolean` 이나 `ArrayList<BoardDto>` 를 돌려준다 — 화면 이름이 아니라 **데이터**다.

| 표시 | `return true` 를 무엇으로 읽는가 | 결과 |
| --- | --- | --- |
| `@Controller` | `"true"` 라는 이름의 뷰를 찾는다 | 그런 화면이 없다 |
| `@RestController` | 응답 본문에 실을 값 | `true` 가 그대로 나간다 |

그래서 화면을 돌려주지 않고 값만 내보내는 컨트롤러라면 `@RestController` 를 쓰는 편이 맞다. `@Controller` + `@ResponseBody` 를 합쳐 둔 것이라(2-8), 클래스 전체가 데이터 응답이 된다.

`ArrayList<BoardDto>` 를 돌려주면 스프링이 JSON 배열로 바꿔 내보낸다. 이때 객체에서 값을 꺼내는 데 getter가 쓰이므로, 1-12에서 갖춰 둔 getter가 그대로 이어진다.

```
GET /board/findall
        │
        ▼
[ {"no":1,"content":"안녕하세요","writer":"유재석"},
  {"no":2,"content":"하하","writer":"강호동"} ]
```

DTO가 JSON으로 바뀌는 자리가 여기다. 1-9 ③에서 Content-Type 목록에 DTO가 없다고 한 것과 짝이 맞는다 — 나갈 때도 들어올 때도 오가는 것은 문자열이고, DTO는 그 안쪽에서만 쓰는 자바 그릇이다.

### 1-14. 전체조회 — ResultSet을 DTO 목록으로

```java
public ArrayList<BoardDto> findAll() {
    ArrayList<BoardDto> list = new ArrayList<>();
    try {
        String sql = "SELECT * FROM BOARD";
        PreparedStatement ps = conn.prepareStatement(sql);
        ResultSet rs = ps.executeQuery();
        while (rs.next()) {
            BoardDto boardDto = new BoardDto();
            boardDto.setNo(rs.getInt("no"));
            boardDto.setContent(rs.getString("content"));
            boardDto.setWriter(rs.getString("writer"));
            list.add(boardDto);
        }
    } catch (SQLException e) {
        System.out.println(e);
    }
    return list;
}
```

CRUD 넷 중 조회만 모양이 다르다. 표를 바꾸는 것이 아니라 **읽어 오는** 쪽이라 실행 메소드부터 갈린다(1-10 ③).

| | 등록·수정·삭제 | 조회 |
| --- | --- | --- |
| 실행 | `executeUpdate()` | `executeQuery()` |
| 돌려받는 것 | 바뀐 줄 수 (`int`) | `ResultSet` |
| 반환 | `boolean` | `ArrayList<BoardDto>` |

`ResultSet` 은 결과를 다 담아 둔 목록이 아니라 **커서**다. 처음에는 첫 줄 앞에 서 있고, `rs.next()` 를 부를 때마다 한 줄씩 내려가면서 더 읽을 줄이 있는지를 `boolean` 으로 알려 준다.

```
rs.next() → true  →  1번 줄을 읽는다
rs.next() → true  →  2번 줄을 읽는다
rs.next() → false →  반복문 종료
```

이 성질 때문에 `while (rs.next())` 라는 관용구가 나온다. 반복 조건과 커서 이동이 한 줄에 겹쳐 있는 형태다.

**① 줄마다 새 객체를 만든다**

`new BoardDto()` 가 반복문 **안에** 있다는 점이 요점이다. 밖에서 하나 만들어 두고 값만 바꿔 담으면, 리스트에 들어간 것이 전부 같은 객체를 가리키게 되어 마지막 줄의 값으로 다 덮인다. [[Java day05 클래스와 인스턴스]] 의 참조 성질이 그대로 드러나는 자리라, 줄마다 그릇을 새로 만드는 편이 안전하다.

**② 빈 객체를 만들고 setter로 채운다**

1-12에서 기본 생성자를 남겨 둔 이유가 여기서도 쓰인다. 전체 생성자로 `new BoardDto(rs.getInt("no"), ...)` 처럼 한 번에 만들 수도 있는데, setter로 채우면 컬럼이 늘거나 순서가 바뀌어도 이름만 맞으면 된다. 2-5에 적어 둔 "빈 객체를 만들어 두고 하나씩 채우는" 흐름이 손으로 쓴 형태다.

**③ 컬럼은 이름으로 꺼낸다**

`rs.getInt("no")` 처럼 컬럼 이름으로 꺼내면 `select` 의 컬럼 순서가 바뀌어도 영향을 받지 않는다. 번호로 꺼내는 `rs.getInt(1)` 도 되지만, 이름 쪽이 읽기에도 낫다.

타입에 맞는 메소드를 골라야 한다는 점은 봐 둔다 — `no` 는 `int` 라 `getInt`, 나머지는 `VARCHAR` 라 `getString` 이다. DB 타입과 자바 타입을 짝지어 둔 1-12의 표가 여기서 쓰인다.

**④ 결과가 없으면 빈 리스트가 나간다**

`list` 를 먼저 만들어 두고 채우는 형태라, 조회 결과가 한 줄도 없으면 비어 있는 리스트가 그대로 반환된다. `null` 을 돌려주지 않으므로 받는 쪽이 바로 반복문을 돌려도 되고, JSON으로는 `[]` 가 나간다.

**⑤ `SELECT * FROM BOARD` — 대소문자**

SQL 키워드와 테이블 이름은 대소문자를 가리지 않는다. 다만 리눅스에서 MySQL을 돌리면 테이블 이름이 대소문자를 구분하는 설정이 기본이라, 표를 만들 때 쓴 이름과 맞춰 두는 편이 옮겨 다니기에 안전하다.

`select *` 로 전부 가져오는 것도 실습에서는 편하지만, 컬럼이 늘면 쓰지 않는 값까지 실려 온다. 필요한 컬럼만 적는 쪽이 나중에 표가 커졌을 때 차이가 난다.

### 1-15. 수정과 삭제 — 조건에도 ?를 쓴다

```java
public boolean update(BoardDto boardDto) {
    try {
        String sql = "update board set content = ? where no = ? ";
        PreparedStatement ps = conn.prepareStatement(sql);
        ps.setString(1, boardDto.getContent());
        ps.setInt(2, boardDto.getNo());
        int result = ps.executeUpdate();
        if (result == 1) return true;
    } catch (SQLException e) {
        System.out.println(e);
    }
    return false;
}

public boolean delete(int no) {
    try {
        String sql = "delete from board where no = ?";
        PreparedStatement ps = conn.prepareStatement(sql);
        ps.setInt(1, no);
        int result = ps.executeUpdate();
        if (result == 1) return true;
    } catch (SQLException e) {
        System.out.println(e);
    }
    return false;
}
```

둘 다 1-10의 다섯 단계를 그대로 반복한다. 새로 나오는 것은 **조건절**이다.

**① `where` 를 빠뜨리면 전부 바뀐다**

`update`·`delete` 에서 `where` 는 문법상 선택이라, 없어도 SQL은 통과한다. 대신 **표의 모든 줄**이 대상이 된다. 등록과 갈리는 지점이 여기라, 조건절을 먼저 적고 값을 채우는 순서로 쓰는 편이 안전하다. [[SQL day03 DML과 조인]] 에서 정리한 자리다.

**② 조건의 값도 `?` 로 받는다**

`where no = ?` 처럼 조건에 들어가는 값도 이어 붙이지 않는다. 1-10 ②에서 정리한 대로 값이 문장 구조를 바꾸는 것을 막으려는 것이고, 조건절은 특히 그 영향이 크다 — 조건이 통째로 무력화되면 한 줄만 지우려던 것이 전부가 될 수 있다.

**③ `?` 의 순서가 곧 인덱스다**

`update` 에서 `content` 가 1번, `no` 가 2번이다. 문장에 나온 순서대로 번호가 붙는 것이라, `set` 에 들어가는 값이 앞이고 `where` 조건이 뒤다. 필드 순서나 DTO 선언 순서와는 상관이 없다.

타입에 맞는 메소드를 쓰는 것도 함께 봐 둔다 — `no` 는 숫자라 `setInt` 다. `setString(2, "3")` 처럼 넣으면 DB가 알아서 바꿔 주기도 하지만, 인덱스를 못 타거나 비교가 어긋날 수 있어 타입을 맞춰 두는 편이 낫다.

**④ 없는 번호를 지우면 0이 온다**

`executeUpdate()` 가 돌려주는 것은 **실제로 바뀐 줄 수**다(1-10 ③). 조건에 맞는 줄이 없으면 예외가 아니라 0이 나온다.

| 상황 | 반환 | `result == 1` |
| --- | --- | --- |
| 한 줄 수정·삭제됨 | 1 | `true` |
| 조건에 맞는 줄 없음 | 0 | `false` |
| SQL 오류 | 예외 | `catch` 로 |

"오류는 없었지만 아무 일도 안 일어났다"를 이 숫자로 구분한다는 것이 요점이다. 등록에서는 거의 드러나지 않던 성질이 수정·삭제에서 제 몫을 한다.

**⑤ 부분 수정의 성격**

`set content = ?` 만 두었으므로 이 메소드는 내용만 바꾼다. 작성자를 같이 바꾸려면 `set` 에 컬럼을 더하고 `?` 를 하나 늘리면 된다. HTTP 방식으로 보면 [[Java Spring day01 서블릿과 HTTP 메소드]] 1-6의 PUT과 PATCH가 갈리는 자리인데, 실습에서는 `@PutMapping` 하나로 둔다.

### 1-16. 컨트롤러 — 매핑 넷이 CRUD와 짝을 이룬다

```java
@PostMapping("/board/save")
public boolean save(BoardDto boardDto) { return bd.save(boardDto); }

@GetMapping("/board/findall")
public ArrayList<BoardDto> findAll() { return bd.findAll(); }

@PutMapping("/board/update")
public boolean update(BoardDto boardDto) { return bd.update(boardDto); }

@DeleteMapping("/board/delete")
public boolean delete(int no) { return bd.delete(no); }
```

1-9 ④의 표가 실제 코드로 채워졌다.

| HTTP | 주소 | 컨트롤러 | DAO | SQL |
| --- | --- | --- | --- | --- |
| POST | `/board/save` | `save` | `save` | `insert` |
| GET | `/board/findall` | `findAll` | `findAll` | `select` |
| PUT | `/board/update` | `update` | `update` | `update` |
| DELETE | `/board/delete` | `delete` | `delete` | `delete` |

컨트롤러 메소드가 하나같이 **DAO를 부르고 결과를 그대로 돌려주기만** 한다는 점을 봐 둔다. 지금은 사이에 할 일이 없어서 한 줄이지만, 값 검증이나 여러 DAO를 묶는 일이 생기면 그 코드가 들어갈 자리가 여기다 — 그러다 컨트롤러가 두꺼워지면 Service 계층을 두게 된다(3-2).

**① 매개변수가 하나뿐일 때**

`delete(int no)` 는 DTO가 아니라 값 하나를 받는다. 요청에 실려 온 `no=3` 이 **이름이 같은 매개변수**로 들어온다.

```
DELETE /board/delete?no=3
        │
        └─ delete(int no)   ← 이름이 no 라서 짝이 맞는다
```

1-9 ⑤의 커맨드 객체 바인딩과 같은 규칙(이름으로 짝짓기)인데, 담을 그릇이 DTO냐 값 하나냐만 다르다. 값이 한둘이면 이렇게 받는 편이 가볍고, 여러 개면 DTO로 묶는다.

이름으로 짝을 짓는 방식이라 **매개변수 이름이 곧 규격**이 된다는 성질이 따라온다. 이름을 바꾸면 요청 쪽도 같이 바꿔야 하고, 값이 안 들어오면 기본형(`int`)은 담을 것이 없어 문제가 된다. 이름을 명시하고 필수 여부를 정하려면 `@RequestParam` 을 쓴다.

```java
public boolean delete(@RequestParam("no") int no) { ... }
```

**② 조회에만 매개변수가 없다**

`findAll()` 은 전부 가져오는 것이라 받을 값이 없다. 번호로 하나만 찾는 `findOne` 을 만든다면 `delete` 와 같은 모양이 된다.

**③ 주소에 동작 이름이 들어가 있다**

`/board/save`·`/board/delete` 처럼 주소에 동사를 넣은 형태다. 무엇을 하는지 눈에 바로 들어와서 익히기에 좋다. 자원 이름만 두고 **동작은 HTTP 방식이 맡게** 하는 REST 방식과 갈리는 지점인데, 그 정리는 2-10에 따로 뒀다.

### 1-17. main이 둘인 프로젝트 — build.gradle의 mainClass

시작 클래스가 늘면서 짚어야 할 것이 하나 생긴다. 프로젝트에는 `SpringwebApplication` 과 `day02.AppStart` 두 개의 `main` 이 있다.

```groovy
springBoot {
	mainClass = 'day02.AppStart'
}
```

실행할 클래스를 골라 주는 설정이다. `main` 이 하나뿐이면 그레이들이 알아서 찾지만, 여럿이면 어느 것을 띄울지 알 수 없어 지정이 필요하다.

day마다 새 패키지에 진입점을 만드는 실습 구조에서는 이 한 줄만 바꿔 가며 쓰게 된다. 1-3에서 정리한 컴포넌트 스캔 범위가 **시작 클래스가 있는 패키지 아래**라는 점과 맞물리는 자리이기도 하다 — 어느 `AppStart` 를 띄우느냐에 따라 등록되는 컨트롤러가 달라진다.

```
mainClass = 'day02.AppStart'   →  day02 패키지 아래만 스캔
                               →  day01 의 서블릿 클래스는 등록되지 않는다
```

[[Java Spring Boot 프로젝트 생성(분석)]] 에서 정리한 `build.gradle` 이 빌드·실행 설정을 담는 자리라는 것이 실제로 쓰인 형태다.

### 1-18. 정리 — 웹 요청이 DB까지 닿았다

지금까지의 흐름을 이어 두면 이렇다.

| 단계 | 만든 것 |
| --- | --- |
| [[Java day09 MVC 종합예제]] | 콘솔에서 계층 나누기 |
| [[Java day12 종합예제 JDBC DAO]] | DAO가 실제 DB와 이야기하기 |
| [[Java Spring Boot 프로젝트 생성(분석)]] | 서버가 뜨는 프로젝트 만들기 |
| [[Java Spring day01 서블릿과 HTTP 메소드]] | 요청을 받는 자리 만들기 |
| **이번** | 스프링 진입점 + 계층 이식 + CRUD 네 요청 잇기 |

바뀐 것은 `main` 한 줄과 컨트롤러의 표시뿐이고 아래는 그대로다.

| | 콘솔 프로젝트 | 스프링 프로젝트 |
| --- | --- | --- |
| `main` | 메뉴를 돌리는 반복문 | `SpringApplication.run()` |
| 끝나는 시점 | 사용자가 종료를 고를 때 | 서버를 내릴 때까지 계속 |
| 입력 | `Scanner` | HTTP 요청 |
| 요청 구분 | 메뉴 번호 | 주소 + HTTP 방식 |
| 값을 담는 일 | `Scanner` 로 읽어 직접 `set` | 스프링이 이름을 맞춰 채운다 |
| DAO·DTO | — | **그대로** |

[[개념 - CRUD]] 네 가지가 모두 웹 요청으로 이어졌다. 정리하면 계층은 이렇게 굳었다.

```
브라우저 ──HTTP──▶ @RestController ──자바 호출──▶ BoardDao ──상속──▶ BaseDao ──JDBC──▶ MySQL
   JSON  ◀──────── 반환값 자동 변환 ◀──── ArrayList<BoardDto> / boolean
```

콘솔 게시판에서 만든 배선이 그대로 있고, 입구가 `Scanner` 에서 HTTP로, 출구가 `println` 에서 JSON으로 바뀐 것이 전부다. 계층을 나눠 두면 입출구가 바뀌어도 아래가 그대로라는 것을 두 번째로 확인한 셈이다.

남은 것은 두 방향이다. 하나는 **요청을 실제로 보내 보는 일** — 브라우저 주소창으로는 GET밖에 못 보내서 PUT·DELETE를 확인하려면 도구가 필요하다(2-11). 다른 하나는 **손으로 한 배선을 스프링에게 맡기는 일** — `getInstance()` 대신 주입(2-4), 연결 정보는 설정 파일로(2-2)다.

## 2. 추가로 알면 좋은 활용법

### 2-1. 포트 바꾸기와 포트 충돌

같은 포트를 두 프로그램이 함께 쓸 수 없어서, 이미 8080이 잡혀 있으면 서버가 뜨지 않는다. 흔히 나오는 상황 셋이다.

- 앞서 실행한 스프링 부트가 아직 살아 있다
- 다른 프로젝트가 8080을 쓰고 있다
- 다른 프로그램이 그 번호를 잡고 있다

포트를 바꾸려면 `application.properties` 에 한 줄 적는다.

```properties
server.port=9090
```

실행할 때만 잠깐 바꾸고 싶으면 인자로 준다. `main(String[] args)` 의 `args` 를 `run()` 에 함께 넘겨 뒀다면 이 값이 반영된다.

```
--server.port=9090
```

`server.port=0` 으로 두면 비어 있는 포트를 자동으로 골라 준다 — 테스트에서 자주 쓰는 형태다.

이미 떠 있는 프로세스를 찾아 내리는 것이 근본 해결이라, 콘솔·작업 관리자에서 자바 프로세스를 정리하고 다시 실행하는 흐름도 함께 익혀 둔다.

### 2-2. 연결 정보를 코드 밖으로 — application.properties

1-7에서 자바 파일에 적어 둔 연결 정보는 설정 파일로 빼는 것이 기본이다.

```properties
spring.datasource.url=jdbc:mysql://127.0.0.1:3306/mydb
spring.datasource.username=root
spring.datasource.password=
spring.datasource.driver-class-name=com.mysql.cj.jdbc.Driver
```

| 두는 자리 | 성질 |
| --- | --- |
| 자바 코드 안 | 바꾸려면 다시 컴파일, 소스와 함께 저장소로 올라간다 |
| `application.properties` | 값만 고치면 된다, 환경별로 파일을 나눌 수 있다 |
| 환경 변수·외부 파일 | 소스에 값이 남지 않는다 |

[[Java Spring Boot 프로젝트 생성(분석)]] 2-7에서 설정 분리를 정리했는데, 연결 정보가 그 대상 중에서도 가장 먼저 빼야 하는 값이다. **비밀번호·키는 저장소에 올라가면 되돌리기 어렵다** — 커밋 이력에 남기 때문이다. 실습용 로컬 값이라도 습관을 들여 두는 편이 안전하다.

환경별로 파일을 나눠 두고 골라 쓰는 방식도 있다.

```
application.properties          공통
application-local.properties    내 컴퓨터
application-prod.properties     운영
```

```properties
spring.profiles.active=local
```

값을 코드에서 읽을 때는 `@Value` 나 `@ConfigurationProperties` 를 쓴다.

```java
@Value("${spring.datasource.url}")
private String url;
```

### 2-3. DataSource와 커넥션 풀

`DriverManager.getConnection()` 은 부를 때마다 새 연결을 만든다. 연결은 만드는 데 시간이 걸리는 자원이라, 요청마다 만들면 그 비용이 그대로 응답 시간이 된다.

그래서 실제로는 **미리 만들어 두고 빌려주는** 방식을 쓴다.

```
요청 → 풀에서 연결 하나 빌림 → 쿼리 → 반납 → (다음 요청이 다시 빌림)
```

[[Java day16 스레드 동기화]] 의 스레드 풀과 완전히 같은 발상이다. 만드는 비용이 큰 자원을 미리 준비해 두고 돌려쓴다.

| | `DriverManager` | 커넥션 풀 |
| --- | --- | --- |
| 연결 생성 | 부를 때마다 | 미리 만들어 둔다 |
| 반납 | `close()` 하면 끊긴다 | `close()` 하면 풀로 돌아간다 |
| 개수 제한 | 없다 | 최대치를 정해 둔다 |

스프링 부트는 의존성만 넣어 두면 HikariCP라는 풀을 자동으로 붙여 준다. 코드에서는 `DataSource` 라는 규격으로 받는다.

```java
@Autowired
private DataSource dataSource;

Connection conn = dataSource.getConnection();
```

`DataSource` 도 [[Java day11 인터페이스]] 의 규격 — 어떤 풀을 쓰든 내 코드는 이 인터페이스만 보면 된다.

풀을 쓸 때는 **연결을 반드시 반납해야 한다.** 빌리기만 하고 돌려주지 않으면 풀이 비어 다음 요청이 기다리게 된다. [[Java day12 예외 처리와 JDBC]] 의 try-with-resources 가 그 자리를 맡는다.

```java
try (Connection conn = dataSource.getConnection();
     PreparedStatement ps = conn.prepareStatement(sql)) {
    // ...
}   // 블록을 벗어나면 자동으로 반납
```

1-7처럼 연결을 필드에 하나 들고 계속 쓰는 형태는 실습에서는 단순하지만, 여러 요청이 동시에 같은 연결을 쓰게 되는 자리라 실제로는 요청마다 빌려 쓰는 쪽으로 바뀐다.

### 2-4. 싱글톤을 스프링에게 맡기기

1-8에서 손으로 만든 싱글톤을 스프링은 기본으로 제공한다. 표시만 붙이면 컨테이너가 객체를 하나 만들어 관리한다.

```java
@Repository
public class BoardDao { ... }

@Controller
public class BoardController {
    private final BoardDao boardDao;

    public BoardController(BoardDao boardDao) {   // 생성자 주입
        this.boardDao = boardDao;
    }
}
```

| 표시 | 붙이는 자리 |
| --- | --- |
| `@Controller` · `@RestController` | 요청을 받는 계층 |
| `@Service` | 업무 처리 계층 |
| `@Repository` | DB 접근 계층 |
| `@Component` | 그 밖의 일반 컴포넌트 |

넷 다 컴포넌트로 등록된다는 점은 같고, **이름이 계층을 알려 주는** 역할을 한다. `@Repository` 에는 DB 예외를 스프링 예외로 바꿔 주는 동작이 얹혀 있기도 하다.

직접 만든 싱글톤과 갈리는 자리를 정리해 두면 이렇다.

| | 직접 만든 싱글톤 | 스프링 빈 |
| --- | --- | --- |
| 객체 생성 | `getInstance()` | 컨테이너가 만든다 |
| 받는 방법 | `BoardDao.getInstance()` | 생성자 매개변수로 받는다 |
| 갈아끼우기 | 코드를 고쳐야 한다 | 다른 구현을 등록하면 된다 |
| 테스트 | 가짜로 바꾸기 어렵다 | 가짜 객체를 넣기 쉽다 |

마지막 두 줄이 스프링을 쓰는 이유에 가깝다. `getInstance()` 를 코드에 적어 두면 **어떤 구현을 쓸지가 코드에 박힌다.** 주입 방식은 그 결정을 밖으로 빼서, [[Java day11 인터페이스]] 에서 정리한 "규격에 기대고 구현은 갈아끼운다"를 실제로 쓸 수 있게 한다.

주입 방식은 셋인데 생성자 주입이 권장된다.

| 방식 | 형태 | 성질 |
| --- | --- | --- |
| 생성자 주입 | 생성자 매개변수 | `final` 가능, 빠짐을 컴파일 때 알 수 있다 |
| 필드 주입 | 필드에 `@Autowired` | 짧지만 테스트에서 갈아끼우기 어렵다 |
| setter 주입 | setter에 `@Autowired` | 나중에 바꿀 수 있다 |

생성자가 하나뿐이면 `@Autowired` 를 생략해도 스프링이 알아서 주입한다.

### 2-5. 기본 생성자가 필요한 자리

1-12에서 남겨 둔 기본 생성자는 앞으로 계속 쓰인다. 라이브러리들이 **빈 객체를 만들어 두고 값을 채워 넣는** 방식으로 동작하기 때문이다.

| 자리 | 하는 일 |
| --- | --- |
| 폼·쿼리스트링 → 커맨드 객체 | 빈 객체를 만들고 setter로 채운다 (1-9 ⑤) |
| JSON → 객체 변환 | 같은 흐름 |
| `ResultSet` → DTO | 같은 흐름 |
| JPA 엔티티 | 기본 생성자를 요구한다 |

값을 다 아는 상태가 아니라 **하나씩 채워 나가는** 흐름이라, 매개변수 없는 생성자가 있어야 시작할 수 있다. 이때 채우는 쪽은 [[Java day13 Object 클래스와 리플렉션]] 의 리플렉션으로 setter를 찾아 부른다.

DTO를 쓸 때의 관례를 정리해 두면 이렇다.

- 기본 생성자를 둔다
- 필드는 `private`, getter·setter를 만든다
- 필드 이름을 컬럼·JSON 키와 맞춘다 (이름으로 짝을 찾는다)
- `toString()` 을 재정의해 둔다

### 2-6. SQL 스크립트를 프로젝트가 실행하게 하기

`sample.sql` 을 DB 도구에서 직접 실행하는 대신, 정해진 이름으로 두면 서버가 뜰 때 실행되게 할 수 있다.

```
src/main/resources/
├── schema.sql    테이블 만들기
└── data.sql      샘플 데이터 넣기
```

```properties
spring.sql.init.mode=always
```

새로 받은 사람이 스크립트를 따로 실행하지 않아도 같은 상태에서 시작한다는 것이 값어치다. 1-11에서 `DROP` 을 앞에 둔 것과 같은 목적이 프로젝트 수준으로 올라온 셈이다.

다만 뜰 때마다 실행되므로 **데이터가 매번 초기화된다.** 개발·테스트 환경에서만 켜 두는 설정이다.

### 2-7. 나머지 CRUD를 채워 나가는 순서

> 여기 적어 둔 순서대로 실제로 채운 코드는 1-14~1-16에 있다. 아래는 그 짝을 한눈에 보려고 남겨 둔 표다.

1-10에서 등록 하나를 채웠으니 나머지 셋은 같은 다섯 단계를 반복한다. [[Java day12 종합예제 JDBC DAO]] 에서 만든 형태를 그대로 옮기면 이렇게 짝이 맞는다.

| DAO 메소드 | SQL | 실행 | 반환 | 컨트롤러 매핑 |
| --- | --- | --- | --- | --- |
| `save` | `insert` | `executeUpdate` | 성공 여부 | `@PostMapping` |
| `findAll` | `select` | `executeQuery` | `List<BoardDto>` | `@GetMapping` |
| `update` | `update` | `executeUpdate` | 성공 여부 | `@PutMapping` |
| `delete` | `delete` | `executeUpdate` | 성공 여부 | `@DeleteMapping` |

조회만 모양이 다르다. `ResultSet` 을 받아 한 줄씩 꺼내 담아야 하기 때문이다.

```java
public List<BoardDto> findAll() {
    List<BoardDto> list = new ArrayList<>();
    try {
        String sql = "select * from board";
        PreparedStatement ps = conn.prepareStatement(sql);
        ResultSet rs = ps.executeQuery();
        while (rs.next()) {
            list.add(new BoardDto(rs.getInt("no"), rs.getString("content"), rs.getString("writer")));
        }
    } catch (SQLException e) {
        System.out.println(e);
    }
    return list;
}
```

담는 그릇은 [[Java day14 제네릭]] 의 `List<BoardDto>` 다. 결과가 없을 때 `null` 대신 **빈 리스트를 돌려주는** 편이 부르는 쪽이 편하다 — 받은 자리에서 바로 반복문을 돌려도 되기 때문이다.

`rs.next()` 가 커서를 한 줄씩 옮기면서 더 읽을 줄이 있는지 알려 준다는 점, 컬럼을 이름으로 꺼낼 수 있다는 점이 [[Java day12 예외 처리와 JDBC]] 의 자리다.

번호 하나로 찾는 형태에서는 조건에도 `?` 를 쓴다.

```java
String sql = "select * from board where no = ?";
```

값이 들어가는 자리라면 조건절이든 값 목록이든 같은 규칙이 적용된다(1-10 ②).

### 2-8. 메소드가 돌려준 값이 응답이 되게 하기

`@Controller` 는 메소드가 돌려준 값을 **화면 이름**으로 읽는다(1-9 ②). 그래서 문자열이나 `boolean` 을 그대로 응답 본문으로 보내고 싶으면 그 해석을 바꿔 줘야 한다.

```java
@Controller
public class BoardController {

    @PostMapping("/board/save")
    @ResponseBody                      // 이 메소드의 반환값은 데이터다
    public boolean save(BoardDto boardDto) { ... }
}
```

```java
@RestController                        // 클래스 전체가 데이터 응답
public class BoardController { ... }
```

| 쓰는 것 | 범위 |
| --- | --- |
| `@ResponseBody` | 메소드 하나 |
| `@RestController` | 클래스 전체 |

화면을 돌려주는 메소드와 데이터를 돌려주는 메소드가 섞여 있으면 앞쪽을, 전부 데이터면 뒤쪽을 쓴다. 요즘 화면을 자바스크립트가 그리는 구조에서는 서버가 데이터만 내보내는 형태가 흔해서 `@RestController` 를 자주 본다.

반환값이 JSON으로 바뀌는 일은 스프링이 라이브러리(Jackson)로 처리한다. 이때 객체에서 값을 꺼내는 데 getter가 쓰이므로, DTO에 getter를 갖춰 두는 것이 그대로 이어진다(1-12).

성공 여부만 `true`/`false` 로 보내는 형태는 단순해서 좋지만, 실패한 이유를 담을 자리가 없다는 성질이 따라온다. 상태 코드까지 함께 정하고 싶으면 `ResponseEntity` 를 쓴다.

```java
return ResponseEntity.ok(result);                        // 200
return ResponseEntity.status(HttpStatus.BAD_REQUEST).build();   // 400
```

[[Java Spring day01 서블릿과 HTTP 메소드]] 2-3에서 정리한 상태 코드를 코드에서 직접 고르는 자리다.

> 실습에서는 클래스에 `@RestController` 를 붙이는 쪽을 골랐다(1-13).

### 2-9. 예외를 콘솔 출력으로 끝내지 않기

`catch` 에서 `System.out.println` 만 하고 넘어가면 실습에서는 흐름이 보이지만, 세 가지가 아쉬워진다.

| 아쉬운 점 | 실제로는 |
| --- | --- |
| 콘솔에만 남는다 | 로그 파일·수집 도구로 남긴다 |
| 언제·어디서인지 모른다 | 로거가 시각·클래스 이름을 붙여 준다 |
| 부른 쪽은 `false` 만 받는다 | 예외를 감싸 올려 보낸다 |

로거를 쓰면 이렇게 된다.

```java
private static final Logger log = LoggerFactory.getLogger(BoardDao.class);

catch (SQLException e) {
    log.error("게시글 등록 실패", e);
}
```

| | `System.out.println` | 로거 |
| --- | --- | --- |
| 끄고 켜기 | 코드를 고쳐야 한다 | 설정으로 단계 조절 |
| 단계 구분 | 없다 | `error`·`warn`·`info`·`debug` |
| 남는 곳 | 콘솔 | 파일·외부 수집 도구 |

예외 객체를 두 번째 인자로 넘기면 스택 트레이스가 함께 남는다는 점이 요점이다. 문자열로 이어 붙이면 메시지만 남고 **어디서 났는지가 사라진다.**

한 단계 더 가면, DAO에서 난 예외를 위 계층이 판단할 수 있게 올려 보낸다. 스프링에서는 컨트롤러 밖에서 한 번에 받는 자리를 따로 둘 수 있다.

```java
@RestControllerAdvice
public class ErrorHandler {
    @ExceptionHandler(Exception.class)
    public ResponseEntity<String> handle(Exception e) {
        log.error("처리 중 오류", e);
        return ResponseEntity.status(500).body("서버 오류");
    }
}
```

예외 처리 코드가 메소드마다 흩어지지 않고 한곳에 모인다는 것이 값어치다. [[Java day12 예외 처리와 JDBC]] 에서 정리한 "예외는 처리할 수 있는 곳까지 올려 보낸다"가 웹 계층에서 나타난 형태다.

### 2-10. 주소를 REST 방식으로 정리하기

1-16 ③에서 주소에 동사가 들어간 형태를 봤다. 자원 이름만 두고 동작은 HTTP 방식이 맡는 쪽으로 정리하면 이렇게 된다.

| | 동사를 주소에 (실습) | 자원 중심 (REST) |
| --- | --- | --- |
| 등록 | `POST /board/save` | `POST /boards` |
| 전체조회 | `GET /board/findall` | `GET /boards` |
| 개별조회 | `GET /board/find?no=3` | `GET /boards/3` |
| 수정 | `PUT /board/update` | `PUT /boards/3` |
| 삭제 | `DELETE /board/delete?no=3` | `DELETE /boards/3` |

오른쪽은 주소가 **무엇을**만 가리키고, **무엇을 한다**는 HTTP 방식이 말한다. 주소가 짧아지고 규칙이 예측 가능해진다는 것이 값어치다.

주소의 일부를 값으로 받을 때는 `@PathVariable` 을 쓴다.

```java
@DeleteMapping("/boards/{no}")
public boolean delete(@PathVariable int no) { ... }
```

| 받는 방법 | 요청 모양 | 어울리는 값 |
| --- | --- | --- |
| `@RequestParam` | `?no=3` | 검색어·정렬·페이지 같은 조건 |
| `@PathVariable` | `/boards/3` | **무엇을 가리키는지** — 자원의 식별자 |
| 커맨드 객체·`@RequestBody` | 본문 | 여러 값이 묶인 데이터 |

어느 쪽이든 동작은 같으므로 실습에서 곧바로 바꿀 일은 아니지만, 남이 만든 API 문서를 읽을 때 오른쪽 형태를 자주 보게 된다. [[Java Spring day01 서블릿과 HTTP 메소드]] 2-5의 안전성·멱등성 정리와 함께 보면 왜 방식마다 자리가 정해져 있는지가 이어진다.

폼에서 보낸 값을 받을 때와 JSON을 받을 때가 갈린다는 점도 봐 둔다. 커맨드 객체 바인딩(1-9 ⑤)은 `content=..&writer=..` 형태의 폼 인코딩을 읽는 것이라, 요청 본문이 JSON이면 `@RequestBody` 를 붙여야 값이 들어온다.

```java
@PostMapping("/boards")
public boolean save(@RequestBody BoardDto boardDto) { ... }
```

### 2-11. GET 말고 다른 요청을 보내 보기

브라우저 주소창으로 보낼 수 있는 것은 GET뿐이라, `findAll` 은 주소만 쳐도 확인되지만 나머지 셋은 그렇지 않다. 확인하는 방법이 몇 가지 있다.

| 방법 | 성격 |
| --- | --- |
| HTML `<form>` | GET·POST만 된다 |
| `fetch` (자바스크립트) | 모든 방식, 브라우저 콘솔에서 바로 |
| API 테스트 도구 | 요청을 저장해 두고 반복 |
| `curl` | 터미널 한 줄 |

가장 손쉬운 것은 브라우저 개발자 도구 콘솔에서 `fetch` 를 부르는 방식이다. [[JS day13 웹 스토리지와 인터벌]] 에서 다룬 것과 같은 자리다.

```javascript
fetch('/board/delete?no=3', { method: 'DELETE' })
    .then(r => r.json())
    .then(console.log);
```

```javascript
fetch('/board/save', {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body: 'content=테스트&writer=나'
}).then(r => r.json()).then(console.log);
```

두 번째에서 `Content-Type` 을 폼 인코딩으로 맞춘 것이 1-9 ③과 이어지는 자리다. 커맨드 객체가 값을 받아 가려면 보내는 쪽이 그 형태로 실어 줘야 한다.

`curl` 로는 이렇게 된다.

```
curl -X DELETE "http://localhost:8080/board/delete?no=3"
curl -X POST "http://localhost:8080/board/save" -d "content=테스트&writer=나"
```

응답이 `true`/`false` 로만 오므로, 실제로 바뀌었는지는 `GET /board/findall` 을 한 번 더 불러 확인하는 흐름이 된다. 1-15 ④에서 정리한 대로 **`false` 는 오류가 아니라 "해당하는 줄이 없었다"** 일 수 있다는 점을 함께 본다.

## 3. 더 나아가 알면 좋은 것

### 3-1. 자동 설정이 실제로 하는 일

1-3의 `@EnableAutoConfiguration` 이 스프링 부트의 성격을 만드는 자리다. **클래스패스에 무엇이 있는지 보고 설정을 채워 넣는다.**

| 의존성에 있으면 | 자동으로 준비되는 것 |
| --- | --- |
| `spring-boot-starter-web` | 내장 톰캣, `DispatcherServlet`, JSON 변환기 |
| JDBC 드라이버 + 연결 정보 | `DataSource`, 커넥션 풀 |
| `spring-boot-starter-data-jpa` | `EntityManager`, 트랜잭션 관리자 |

조건이 붙은 설정 클래스들이 미리 준비돼 있고, 조건에 맞을 때만 적용되는 구조다.

```java
@ConditionalOnClass(DataSource.class)
@ConditionalOnMissingBean(DataSource.class)
```

두 번째 줄이 중요하다. **내가 직접 만들어 두면 자동 설정은 물러난다.** 기본값으로 돌아가되 필요하면 언제든 가져올 수 있는 형태라, 스프링 부트가 "설정 없이 시작하고 필요할 때 손댄다"를 이루는 방식이다.

무엇이 적용됐는지 확인하려면 로그를 켜 본다.

```properties
debug=true
```

### 3-2. 계층 이름 — DAO·Repository·Service

지금은 Controller와 DAO 둘뿐인데, 실제 프로젝트에서는 사이에 한 층이 더 들어간다.

```
Controller  →  Service  →  Repository(DAO)  →  DB
```

| 계층 | 맡는 것 |
| --- | --- |
| Controller | 요청 받기, 값 검증, 응답 형태 |
| Service | **업무 규칙** — 여러 DAO를 묶어 하나의 일로 |
| Repository/DAO | 한 테이블에 대한 질의 |

Service가 필요해지는 자리는 **여러 DB 작업이 하나의 일로 묶일 때**다. "글을 지우면 댓글도 지운다" 같은 것은 DAO 하나로 표현되지 않고, 컨트롤러에 넣으면 화면 코드와 업무 규칙이 섞인다.

DAO와 Repository는 이름이 다르지만 자리는 같다.

| | DAO | Repository |
| --- | --- | --- |
| 출신 | 자바 EE 쪽 관용어 | 도메인 주도 설계 용어 |
| 시선 | 테이블에 접근하는 객체 | 객체를 담아 두는 저장소 |

스프링에서는 `@Repository` 를 쓰는 쪽이 관례라 이름이 바뀌는 것을 자주 본다. [[Java day09 MVC 종합예제]] · [[Java day11 종합예제 인터페이스 DAO]] 에서 만든 것과 하는 일은 같다.

### 3-3. JdbcTemplate과 JPA — 반복을 줄이는 방향

2-7처럼 DAO를 채우다 보면 같은 모양이 계속 반복된다.

```
연결 → SQL 준비 → 값 채우기 → 실행 → 결과 꺼내기 → 닫기
```

가운데 두 단계만 메소드마다 다르고 앞뒤는 늘 같다. 그 반복을 라이브러리가 맡는 방향으로 두 단계가 있다.

**① `JdbcTemplate` — SQL은 그대로 쓰고 반복만 없앤다**

```java
List<BoardDto> list = jdbcTemplate.query(
    "select * from board",
    (rs, rowNum) -> new BoardDto(rs.getInt("no"), rs.getString("content"), rs.getString("writer"))
);
```

연결·닫기·예외 처리가 사라지고 SQL과 변환만 남는다.

**② JPA — SQL 자체를 걷어낸다**

```java
public interface BoardRepository extends JpaRepository<Board, Integer> {
    List<Board> findByWriter(String writer);
}
```

메소드 이름을 보고 SQL을 만들어 준다. 구현 클래스를 만들지 않는데도 동작하는 것이 [[Java day13 Object 클래스와 리플렉션]] 에서 본 리플렉션·프록시가 쓰이는 자리다.

| | JDBC 직접 | `JdbcTemplate` | JPA |
| --- | --- | --- | --- |
| SQL | 직접 | 직접 | 대부분 자동 |
| 반복 코드 | 많다 | 적다 | 거의 없다 |
| 무엇이 일어나는지 | 훤히 보인다 | 보인다 | 감춰진다 |

지금 JDBC를 직접 쓰는 이유가 마지막 줄에 있다. 위 도구들은 **이 과정을 줄여 주는 것**이지 다른 일을 하는 것이 아니라, 아래를 알고 나서 올라가야 문제가 났을 때 짚을 수 있다.

### 3-4. 트랜잭션 — 여러 작업을 하나로 묶기

3-2에서 Service가 필요한 이유로 든 "글을 지우면 댓글도 지운다"에는 문제가 하나 더 있다. 앞은 되고 뒤는 실패하면 **중간 상태가 남는다.**

여러 작업을 하나로 묶어 전부 되거나 전부 안 되게 하는 것이 트랜잭션이다.

```java
@Transactional
public void deleteBoard(int no) {
    replyDao.deleteByBoardNo(no);
    boardDao.delete(no);
}
```

표시 하나로 메소드 전체가 한 덩어리가 된다. 예외가 나면 앞서 한 작업까지 되돌린다.

JDBC로 직접 쓰면 이렇게 된다.

```java
conn.setAutoCommit(false);
try {
    // 작업들
    conn.commit();
} catch (Exception e) {
    conn.rollback();
}
```

기본이 `autoCommit = true` 라 문장 하나마다 바로 확정된다는 점이 요점이다. 묶으려면 그것을 꺼야 한다.

성질 네 가지를 머리글자로 ACID라고 부른다.

| 성질 | 뜻 |
| --- | --- |
| 원자성 (Atomicity) | 전부 되거나 전부 안 되거나 |
| 일관성 (Consistency) | 규칙을 깨는 상태로 끝나지 않는다 |
| 격리성 (Isolation) | 동시에 도는 것끼리 간섭하지 않는다 |
| 지속성 (Durability) | 확정된 것은 남는다 |

격리성은 [[Java day16 스레드 동기화]] 의 경쟁 상태가 DB 층에서 나타난 것이다. 여러 연결이 같은 줄을 동시에 건드릴 때 생기는 문제라, 자바 쪽에서 `synchronized` 로 막던 것과 같은 이야기를 DB는 격리 수준과 잠금으로 다룬다.

### 3-5. 패키지 이름 규칙

실습은 `Controller`·`Model` 처럼 대문자로 시작하는 폴더를 썼는데, 자바에서 패키지 이름은 **전부 소문자**로 쓰는 것이 관례다.

| 대상 | 관례 | 예 |
| --- | --- | --- |
| 패키지 | 소문자 | `com.example.board.controller` |
| 클래스 | 파스칼 표기 | `BoardController` |
| 메소드·변수 | 카멜 표기 | `getInstance` |

클래스 이름과 헷갈리지 않게 하려는 것이 이유고, 대소문자를 가리지 않는 운영체제에서 폴더 이름이 어긋나는 문제를 피하는 뜻도 있다.

계층으로 나누는 방식도 둘이 있다.

```
① 계층별                      ② 기능별
com.example                   com.example
├── controller                ├── board
├── service                   │   ├── BoardController
├── repository                │   ├── BoardService
└── dto                       │   └── BoardRepository
                              └── member
```

작을 때는 ①이 편하고, 기능이 늘어나면 ②가 관리하기 낫다는 평이 많다. 어느 쪽이든 1-3에서 본 컴포넌트 스캔 범위(시작 클래스 아래) 안에 들어가야 한다.

### 3-6. 다음에 볼 키워드

- 프레임워크와 라이브러리의 차이, 제어의 역전(IoC)
- 애노테이션의 성격 — 주석과의 차이, 리플렉션으로 읽히는 구조
- `@SpringBootApplication` 의 세 애노테이션과 컴포넌트 스캔 범위
- `SpringApplication.run()` 과 `ApplicationContext`, `main` 의 `args` 전달
- 내장 톰캣과 포트, `server.port` 설정과 포트 충돌 해결
- `localhost` · `127.0.0.1` 루프백 주소, 포트 번호의 역할
- 패키지로 계층 나누기 — Controller·Service·Repository(DAO)·DTO
- `@Controller` 와 `@RestController`, `@ResponseBody` 의 범위 차이
- 서블릿 상속 방식과 애노테이션 방식의 갈림, 단일 상속 제약
- HTTP Content-Type — `text/html`·`application/json`·폼 인코딩·`multipart/form-data`
- `@RequestMapping` 과 `@GetMapping`·`@PostMapping`·`@PutMapping`·`@DeleteMapping`
- 커맨드 객체 바인딩 — 요청 파라미터 이름과 필드 이름 맞추기
- `ResponseEntity` 로 상태 코드까지 정하기
- `PreparedStatement` 의 `?` 바인딩과 SQL 인젝션, 인덱스가 1부터인 점
- `executeUpdate()` 반환값(바뀐 줄 수)으로 성공·0건 판정하기
- `ResultSet` 과 `rs.next()`, 컬럼 이름으로 값 꺼내기
- 로거(`Logger`·`log.error`)와 `System.out.println` 의 차이, 스택 트레이스 남기기
- `@RestControllerAdvice`·`@ExceptionHandler` 로 예외 처리 모으기
- `protected` 와 상속 관계에서의 접근 범위
- `Class.forName()` 으로 드라이버 로드, `DriverManager.getConnection()`
- 부모 생성자가 먼저 불리는 순서와 공통 초기화
- 싱글톤 세 요소(`private` 생성자·`static` 인스턴스·`getInstance`), 이른 초기화와 늦은 초기화
- 스프링 빈의 싱글톤 스코프, `@Component`·`@Controller`·`@Service`·`@Repository`
- 의존성 주입 세 가지(생성자·필드·setter)와 생성자 주입을 쓰는 이유
- `application.properties` 로 연결 정보 분리, 프로파일(`spring.profiles.active`)
- 비밀번호·키를 저장소에 올리지 않는 방법 — 환경 변수·외부 설정
- `DataSource` 와 커넥션 풀(HikariCP), 연결 반납과 try-with-resources
- `schema.sql`·`data.sql` 자동 실행, `spring.sql.init.mode`
- `AUTO_INCREMENT`·`PRIMARY KEY`·`DROP DATABASE IF EXISTS`
- DTO 기본 생성자가 필요한 자리 — JSON 변환·`ResultSet` 매핑·JPA
- `PreparedStatement` 의 `?` 바인딩, `executeUpdate`·`executeQuery`
- `JdbcTemplate` 과 JPA — 반복 코드를 줄이는 단계
- 트랜잭션과 `@Transactional`, `setAutoCommit`·`commit`·`rollback`, ACID
- 자바 패키지 이름 규칙, 계층별 구조와 기능별 구조
- `@RestController` 를 쓰는 이유 — 반환값을 뷰 이름이 아니라 데이터로 읽게 하기
- 객체·컬렉션이 JSON으로 바뀌는 과정과 getter의 역할
- `ResultSet` 커서와 `while (rs.next())`, 줄마다 새 DTO를 만드는 이유
- 컬럼을 이름으로 꺼내기(`getInt`·`getString`)와 타입 맞추기
- 결과가 없을 때 `null` 대신 빈 리스트를 돌려주는 관례
- `update`·`delete` 의 `where` 누락 위험, 조건절에도 `?` 를 쓰는 이유
- `?` 인덱스가 문장에 나온 순서를 따른다는 점 (`set` → `where`)
- `executeUpdate()` 가 0을 돌려주는 상황 — 오류 없이 아무것도 안 바뀐 경우
- 단일 값 매개변수 바인딩과 `@RequestParam`, 이름이 규격이 되는 성질
- `@PathVariable` 과 REST 자원 중심 주소 설계
- 폼 인코딩과 JSON — `@RequestBody` 가 필요한 자리
- GET 외의 요청을 보내 보는 방법 — `fetch`·`curl`·API 테스트 도구
- `main` 이 여럿일 때 `build.gradle` 의 `springBoot { mainClass }` 지정
- PUT과 PATCH의 갈림 — 전체 교체와 부분 수정

## 실습 파일

- `2026B_Spring/springweb/src/main/java/day02/AppStart.java` (프레임워크의 성격, 애노테이션이 코드에 의미를 붙이는 방식, `@SpringBootApplication` 의 내장 톰캣 세팅과 컴포넌트 자동 등록, `SpringApplication.run(클래스.class)` 로 시동 걸기, 클래스 메타정보를 넘기는 이유, 8080 포트와 `localhost`·`127.0.0.1`, 동시 실행이 안 되는 이유)
- `2026B_Spring/springweb/src/main/java/day02/Controller/BoardController.java` (컨트롤러가 DAO를 `getInstance()` 로 받아 필드로 잡아 두는 배선, 웹 기능을 상속 대신 표시로 받기, `@Controller` 와 `@RestController` 의 갈림과 반환값이 뷰 이름이 아닌 데이터로 읽히는 자리, 객체·컬렉션이 JSON으로 바뀌는 과정, HTTP Content-Type과 DTO의 자리, `@PostMapping`·`@GetMapping`·`@PutMapping`·`@DeleteMapping` 넷을 CRUD와 짝짓기, 매개변수 DTO에 요청 값이 이름으로 채워지는 커맨드 객체 바인딩, 값 하나만 받는 매개변수 바인딩과 `@RequestParam`, 컨트롤러 메소드가 DAO 호출만 감싸고 있는 얇은 구조, 컨트롤러를 무상태로 두는 이유)
- `2026B_Spring/springweb/src/main/java/day02/Model/Dao/BaseDao.java` (여러 DAO에 JDBC 연동을 상속으로 물려주기, `private`·`protected` 로 나눈 접근 범위, `Class.forName` 으로 드라이버 로드, `DriverManager.getConnection` 으로 연결, 생성자에서 연동을 실행해 자식이 자동으로 연결되게 하기)
- `2026B_Spring/springweb/src/main/java/day02/Model/Dao/BoardDao.java` (`BaseDao` 상속과 싱글톤을 겹쳐 쓰기, `private` 생성자·`static final` 인스턴스·`getInstance`, 연결 하나를 돌려쓰는 이유, 등록 SQL을 다섯 단계로 실행하기, SQL이 자바가 아니라 서버로 보내는 문자열이라는 점, `?` 로 비워 두고 `setString`·`setInt` 로 채우기와 SQL 인젝션, `executeUpdate` 가 돌려주는 줄 수로 성공·0건 판정, `executeQuery` 와 `ResultSet` 커서를 `while (rs.next())` 로 훑기, 줄마다 새 DTO를 만들어 리스트에 담기, 컬럼을 이름으로 꺼내기, 결과가 없을 때 빈 리스트를 돌려주기, `update`·`delete` 의 조건절과 `?` 인덱스 순서, `SQLException` 검사 예외 처리)
- `2026B_Spring/springweb/src/main/java/day02/Model/Dto/BoardDto.java` (DB 컬럼과 필드를 짝지은 DTO, 캡슐화와 getter·setter, 기본 생성자와 전체 생성자, JSON 변환에 getter가 쓰이는 자리, `toString` 재정의)
- `2026B_Spring/springweb/src/main/java/day02/sample.sql` (실습용 DB·테이블 생성, `AUTO_INCREMENT` 와 `PRIMARY KEY` 제약, 여러 줄 `insert`, `DROP ... IF EXISTS` 로 같은 상태에서 시작하기)
- `2026B_Spring/springweb/build.gradle` (`main` 을 가진 클래스가 여럿일 때 `springBoot { mainClass }` 로 실행할 진입점 고르기, 고른 진입점의 패키지가 곧 컴포넌트 스캔 범위가 되는 점)

## 관련 노트

[[Java MOC]] · [[Java Spring day01 서블릿과 HTTP 메소드]] · [[Java Spring Boot 프로젝트 생성(분석)]] · [[Java day16 스레드 동기화]] · [[Java day14 제네릭]] · [[Java day13 Object 클래스와 리플렉션]] · [[Java day12 예외 처리와 JDBC]] · [[Java day12 종합예제 JDBC DAO]] · [[Java day11 인터페이스]] · [[Java day11 종합예제 인터페이스 DAO]] · [[Java day10 상속과 다형성]] · [[Java day09 MVC 종합예제]] · [[Java day08 접근제한자와 static]] · [[Java day06 생성자와 콘솔 게시판]] · [[Java day05 클래스와 인스턴스]] · [[Java day04 제어문과 배열]] · [[개념 - 싱글톤]] · [[개념 - CRUD]] · [[SQL day02 테이블과 제약조건]] · [[SQL day03 DML과 조인]] · [[JS day13 웹 스토리지와 인터벌]] · [[KDT_2026 학습 지도]]
