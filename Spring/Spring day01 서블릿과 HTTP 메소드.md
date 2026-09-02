---
출처: Claude 분석
원본: KDT_2026/2026B_Spring/springweb/src/main/java/day01
작성일: 2026-08-25
tags: [학습, java]
---

# Java Spring day01 — 서블릿과 HTTP 메소드

> 실습 파일: `2026B_Spring/springweb/src/main/java/day01/BoardController.java`(서블릿의 정체와 `HttpServlet` 상속·생명주기 메소드 `init`·`service`·`destroy` 재정의·HTTP 방식별 `doGet`·`doPost`·`doPut`·`doDelete` 자리 잡기·`@WebServlet` 으로 주소 등록)
> 허브: Java MOC · 이전: Spring Boot 프로젝트 생성(분석) · 다음: [[Spring day02 스프링 부트 실행과 계층 이식]]

Spring Boot 프로젝트 생성(분석) 에서 프로젝트 뼈대를 만들고 `main` 하나로 내장 톰캣이 뜨는 것까지 봤다. 그런데 서버만 떠 있고 브라우저에서 무엇을 요청해도 받아 줄 자리가 없었다. 이번에는 그 **요청을 받는 자리**를 처음 만든다.

만든 클래스는 `BoardController` 하나이고, 메소드는 전부 비어 있다(`super` 호출만 있다). 동작보다 **어떤 메소드가 언제 불리는지**를 눈에 익히는 것이 목적인 코드라, 여기서는 그 뼈대를 따라간다.

## 1. 배운 내용

### 1-1. 서블릿 — 자바 클래스에 HTTP를 붙이는 규격

지금까지 만든 클래스는 전부 `main` 에서 출발해 콘솔로 끝났다. 웹에서는 출발점이 다르다 — **브라우저의 요청이 출발점**이고, 내 클래스는 그 요청이 도착했을 때 불려야 한다.

문제는 자바 클래스가 그 자체로는 HTTP를 모른다는 것이다. "GET 요청이 왔다", "본문에 이런 값이 들어 있다" 같은 이야기를 다루려면 그것을 자바 객체로 바꿔 주는 층이 필요하다. **그 층의 규격이 서블릿(Servlet)** 이고, 규격을 지킨 클래스를 웹서버(톰캣)가 불러 준다.

```
브라우저 ──HTTP 요청──→ 톰캣 ──자바 객체로 변환──→ 내 서블릿 클래스
        ←──HTTP 응답── 톰캣 ←──반환값·출력─────────┘
```

정리하면 이렇다.

| 층 | 하는 일 |
| --- | --- |
| 톰캣(서블릿 컨테이너) | 소켓·HTTP 파싱·스레드 배정을 맡는다 |
| 서블릿 규격 | 톰캣과 내 코드가 만나는 약속 — 메소드 이름과 매개변수 |
| 내 클래스 | 요청을 받아 실제 처리를 한다 |

톰캣이 서블릿 컨테이너라고 불리는 이유가 여기 있다. **서블릿을 담아 두고 생명주기를 관리하는 그릇**이라는 뜻이다. Spring Boot 프로젝트 생성(분석) 1-4에서 `starter-webmvc` 에 톰캣이 들어 있다고 정리했는데, 그 톰캣이 지금 이 클래스를 부를 주체가 된다.

### 1-2. jakarta.servlet — 패키지 이름이 갈린다

임포트 다섯 줄부터 짚어 둔다.

```java
import jakarta.servlet.ServletException;
import jakarta.servlet.http.HttpServlet;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
```

`jakarta` 로 시작한다는 점이 눈에 띈다. 서블릿 규격은 오랫동안 `javax.servlet` 이었는데, 관리 주체가 오라클에서 이클립스 재단으로 넘어가면서 이름이 `jakarta.servlet` 으로 바뀌었다.

| 시기 | 패키지 |
| --- | --- |
| 예전 (Java EE) | `javax.servlet.*` |
| 지금 (Jakarta EE 9+) | `jakarta.servlet.*` |

자료를 찾으면 `javax` 예시가 훨씬 많이 나오는데, 코드 내용은 같고 **앞 글자만 바꿔 읽으면 된다.** 스프링 부트 3 이상은 `jakarta` 쪽이라 `javax` 로 임포트하면 클래스를 못 찾는다.

네 클래스의 역할도 함께 잡아 둔다.

| 클래스 | 담고 있는 것 |
| --- | --- |
| `HttpServlet` | HTTP용 서블릿의 부모 클래스 — 물려받아 쓴다 |
| `HttpServletRequest` | 들어온 요청 — 주소·파라미터·헤더·본문·세션 |
| `HttpServletResponse` | 내보낼 응답 — 상태 코드·헤더·본문 출력 스트림 |
| `ServletException` | 서블릿 처리 중 나는 예외 |

요청과 응답이 **매개변수로 들어온다**는 점이 구조의 핵심이다. 내가 만들어 쓰는 것이 아니라 톰캣이 만들어 넘겨준다 — Spring Boot 프로젝트 생성(분석) 3-1에서 정리한 제어의 역전이 가장 먼저 눈에 보이는 자리다.

### 1-3. 상속으로 규격을 물려받는다

```java
public class BoardController extends HttpServlet {
```

`extends HttpServlet` 한 줄로 이 클래스가 서블릿이 된다. Java day10 상속과 다형성 에서 정리한 상속이 여기서 **규격을 갖추는 수단**으로 쓰인다.

물려받는 것은 두 가지다.

- 생명주기 메소드 — `init()` · `service()` · `destroy()`
- HTTP 방식별 메소드 — `doGet()` · `doPost()` · `doPut()` · `doDelete()` 등

`HttpServlet` 은 이 메소드들을 **이미 구현해 두었고**, 그 구현은 대체로 "이 방식은 지원하지 않는다"는 응답(405)을 돌려주는 형태다. 그래서 내가 할 일은 새로 만드는 것이 아니라 **필요한 것만 덮어쓰는 것**이 된다 — Java day10 상속과 다형성 의 오버라이딩이다.

Java day11 인터페이스 와 갈리는 자리도 함께 봐 둔다.

| | 인터페이스 구현 | `HttpServlet` 상속 |
| --- | --- | --- |
| 구현해야 하는 것 | 선언된 메소드 전부 | 필요한 것만 |
| 기본 동작 | 없다 | 부모에 들어 있다 |

서블릿 규격에는 `Servlet` 인터페이스도 있는데, 그것을 직접 구현하면 다섯 메소드를 전부 채워야 한다. `HttpServlet` 은 그 위에 HTTP용 기본 동작을 얹어 둔 클래스라, 실제로는 이쪽을 상속하는 것이 관례다.

### 1-4. 생명주기 — 세 메소드가 불리는 시점

서블릿은 요청이 올 때마다 새로 만들어지지 않는다. **한 번 만들어져 계속 살아 있으면서** 요청을 받는다. 그 일생을 세 메소드가 나눠 표시한다.

```java
@Override
public void init() throws ServletException {
    super.init();
}

@Override
protected void service(HttpServletRequest req, HttpServletResponse resp)
        throws ServletException, IOException {
    super.service(req, resp);
}

@Override
public void destroy() {
    super.destroy();
}
```

| 메소드 | 불리는 시점 | 횟수 |
| --- | --- | --- |
| `init()` | 서블릿이 처음 만들어질 때 | **1번** |
| `service()` | 요청이 들어올 때마다 | 요청 수만큼 |
| `destroy()` | 서버가 내려갈 때 | **1번** |

가운데 줄만 여러 번이라는 것이 전부인데, 여기서 따라오는 성질이 중요하다.

- **한 번만 하면 되는 준비**는 `init()` 에 둔다 — 설정 읽기, 연결 준비 같은 것
- **요청마다 달라지는 처리**는 `service()` 계열에 둔다
- **정리 작업**은 `destroy()` 에 둔다 — 열어 둔 자원 닫기

Java day12 예외 처리와 JDBC 에서 `finally` 로 연결을 닫던 것과 같은 짝이 여기서는 `init` ↔ `destroy` 로 나타난다. **연 것은 닫는다**는 형태가 층만 바뀌어 반복된다.

그리고 서블릿 객체가 하나뿐이라는 사실이 Java day16 스레드 동기화 와 곧바로 이어진다. 톰캣은 요청마다 스레드를 붙이는데 서블릿 객체는 공유되므로, **멤버 변수에 요청별 데이터를 담으면 경쟁 상태가 생긴다.** 서블릿에 상태를 두지 않는 것이 기본 방침인 이유다.

| 자리 | 안전 여부 |
| --- | --- |
| `service()` 안의 지역 변수 | 안전 — 스레드마다 따로 |
| 매개변수 `req`·`resp` | 안전 — 요청마다 새로 만들어져 넘어온다 |
| 서블릿의 멤버 변수 | 위험 — 모든 요청이 같은 객체를 본다 |

### 1-5. service와 doXXX — 요청을 나누는 두 단계

`service()` 와 `doGet()` 이 둘 다 있는 것이 처음에는 헷갈린다. 순서를 보면 정리된다.

```
요청 도착
   ↓
service(req, resp)          ← 모든 요청이 여기를 먼저 지난다
   ↓ req.getMethod() 를 보고 갈라 준다
doGet / doPost / doPut / doDelete
```

`HttpServlet` 의 `service()` 는 요청 방식을 읽어 **해당 `doXXX` 를 대신 호출해 주는** 구현을 이미 갖고 있다. 그래서 보통은 `service()` 를 건드리지 않고 `doGet`·`doPost` 만 재정의한다.

| 재정의할 것 | 쓰는 자리 |
| --- | --- |
| `doGet`·`doPost` 등 | 방식별로 처리가 다를 때 — 대부분 |
| `service` | 방식과 상관없이 **공통 처리**가 필요할 때 (인코딩 설정, 로그 등) |

`service()` 를 재정의할 때 주의할 점이 하나 있다. `super.service(req, resp)` 를 부르지 않으면 갈라 주는 동작이 사라져서 `doGet` 이 아예 불리지 않는다. 공통 처리를 앞에 넣고 반드시 부모를 이어 호출하는 형태로 쓴다.

```java
@Override
protected void service(HttpServletRequest req, HttpServletResponse resp)
        throws ServletException, IOException {
    req.setCharacterEncoding("UTF-8");   // 공통 처리
    super.service(req, resp);            // 갈라 주기는 부모에게
}
```

실습 코드가 세 생명주기 메소드에서 전부 `super` 를 부르고 있는 것도 같은 이야기다. 부모가 하던 일을 그대로 두고 자리만 잡아 둔 상태다.

### 1-6. HTTP 방식 네 개와 CRUD

`doXXX` 네 개가 나란히 있는 이유는 [[개념 - CRUD]] 와 맞물린다.

```java
@Override
protected void doGet(HttpServletRequest req, HttpServletResponse resp) { ... }

@Override
protected void doPost(HttpServletRequest req, HttpServletResponse resp) { ... }

@Override
protected void doPut(HttpServletRequest req, HttpServletResponse resp) { ... }

@Override
protected void doDelete(HttpServletRequest req, HttpServletResponse resp) { ... }
```

| 메소드 | HTTP 방식 | CRUD | 게시판이라면 |
| --- | --- | --- | --- |
| `doGet` | GET | Read | 글 목록·글 하나 조회 |
| `doPost` | POST | Create | 글 등록 |
| `doPut` | PUT | Update | 글 수정 |
| `doDelete` | DELETE | Delete | 글 삭제 |

Java day06 생성자와 콘솔 게시판 · Java day09 MVC 종합예제 에서 메뉴 번호(1·2·3·4)로 갈랐던 자리가, 웹에서는 **주소 + 요청 방식**의 조합으로 갈린다. 같은 `/board` 주소라도 GET이면 조회, POST면 등록이 되는 식이다.

```
GET    /board      →  doGet     →  목록 조회
POST   /board      →  doPost    →  등록
PUT    /board      →  doPut     →  수정
DELETE /board      →  doDelete  →  삭제
```

메뉴 번호와 달라진 점은 **약속이 표준으로 정해져 있다는 것**이다. 내가 1번을 조회로 정하든 등록으로 정하든 자유였던 자리가, 여기서는 누가 만들어도 GET은 조회다. 그래서 다른 사람이 만든 API도 방식만 보고 성격을 짐작할 수 있다.

주석의 "Dao를 호출하여 처리"라는 자리도 함께 봐 둔다. Java day11 종합예제 인터페이스 DAO · Java day12 종합예제 JDBC DAO 에서 만든 DAO가 그대로 이 안에서 불린다. **컨트롤러가 입구만 바뀌고 아래 계층은 그대로**라는 것이 웹으로 넘어올 때의 실제 모습이다.

### 1-7. @WebServlet — 주소를 붙여야 불린다

클래스를 만들어 둔 것만으로는 아무도 부르지 않는다. **어떤 주소로 들어온 요청을 이 클래스가 받을지** 알려 줘야 한다.

```java
@WebServlet("/board")
public class BoardController extends HttpServlet { ... }
```

톰캣이 시작할 때 이 표시를 읽어 주소와 클래스를 짝지어 두고, 요청이 오면 그 표를 보고 담당자를 찾는다.

| 방식 | 형태 |
| --- | --- |
| 애노테이션 | `@WebServlet("/board")` — 클래스 위에 직접 |
| 설정 파일 | `web.xml` 에 `<servlet-mapping>` 으로 — 예전 방식 |

스프링 부트에서 이 애노테이션을 쓰려면 시작 클래스에 `@ServletComponentScan` 을 붙여 서블릿을 찾게 해 줘야 한다. Spring Boot 프로젝트 생성(분석) 1-6의 `@ComponentScan` 이 스프링 빈을 찾는 것과 별개로, 서블릿은 따로 훑어야 하기 때문이다.

패키지 위치도 함께 짚어 둔다. 실습의 클래스는 `day01` 패키지에 있는데, 시작 클래스는 `com.example` 이다. 스캔 범위 밖이라 자동으로는 잡히지 않는 자리이므로, 서블릿을 등록하려면 스캔 범위를 맞추거나 등록용 설정을 따로 두게 된다.

이 클래스는 처음에 `src/main/example/day01` 에 두었다가 나중에 `src/main/java/day01` 로 옮겼다. 그레이들이 소스로 인식하는 기본 경로가 `src/main/java` 라, 그 밖에 두면 컴파일 대상에 들어가지 않는다. 패키지 선언도 위치에 맞춰 `package day01;` 이 된다 — 자바에서 **패키지 이름과 폴더 경로는 같아야 한다**는 규칙이 소스 루트를 기준으로 적용되는 자리다. 뒤이어 만드는 `day02` 패키지가 `src/main/java` 아래에 바로 놓인 것도 같은 규칙을 따른 결과다([[Spring day02 스프링 부트 실행과 계층 이식]] 1-6).

### 1-8. 정리 — 요청이 도착하는 자리를 만들었다

지금까지의 흐름을 이어 두면 이렇다.

| 단계 | 만든 것 |
| --- | --- |
| Java day09 MVC 종합예제 | 콘솔에서 View·Controller·DAO·DTO로 나누기 |
| Java day12 종합예제 JDBC DAO | DAO가 실제 DB와 이야기하게 만들기 |
| Spring Boot 프로젝트 생성(분석) | 서버가 뜨는 프로젝트 만들기 |
| **이번** | 그 서버로 들어온 요청을 **받는 자리** 만들기 |

콘솔 프로그램에서 `Scanner` 로 입력을 받던 자리가 `HttpServletRequest` 로, `System.out.println` 으로 출력하던 자리가 `HttpServletResponse` 로 바뀐 셈이다. 아래 계층(Service·DAO·DTO)은 손댈 것이 없다.

| 콘솔 | 웹 |
| --- | --- |
| `Scanner` 입력 | `HttpServletRequest` |
| `System.out.println` | `HttpServletResponse` |
| 메뉴 번호로 분기 | 주소 + HTTP 방식으로 분기 |
| `main` 이 흐름을 돌린다 | 톰캣이 내 메소드를 부른다 |

## 2. 추가로 알면 좋은 활용법

### 2-1. 요청에서 값 꺼내기 — HttpServletRequest

`req` 하나에 요청의 모든 것이 들어 있다.

```java
String no = req.getParameter("no");            // /board?no=3
String[] tags = req.getParameterValues("tag"); // 같은 이름이 여러 개
String method = req.getMethod();               // "GET"·"POST"
String uri = req.getRequestURI();              // "/board"
String agent = req.getHeader("User-Agent");    // 헤더
```

| 메소드 | 꺼내는 것 |
| --- | --- |
| `getParameter(name)` | 쿼리 문자열·폼 값 하나 (없으면 `null`) |
| `getParameterValues(name)` | 같은 이름의 값 여러 개 |
| `getMethod()` | 요청 방식 문자열 |
| `getRequestURI()` | 요청 주소 |
| `getHeader(name)` | 헤더 값 |
| `getSession()` | 세션 객체 |
| `getReader()` · `getInputStream()` | 본문 직접 읽기 (JSON 등) |

`getParameter()` 의 반환 타입이 **항상 `String`** 이라는 점이 실제로 걸리는 부분이다. 숫자로 쓰려면 Java day13 Object 클래스와 리플렉션 에서 정리한 `Integer.parseInt()` 로 바꿔야 하고, 값이 없으면 `null` 이라 그대로 파싱하면 예외가 난다.

```java
String param = req.getParameter("no");
int no = (param == null || param.isBlank()) ? 0 : Integer.parseInt(param);
```

한글 파라미터가 깨지면 인코딩을 지정한다. 본문을 읽기 **전에** 설정해야 적용된다.

```java
req.setCharacterEncoding("UTF-8");
```

### 2-2. 응답 만들기 — HttpServletResponse

응답은 `resp` 로 직접 써 내려간다.

```java
resp.setContentType("text/html; charset=UTF-8");
PrintWriter out = resp.getWriter();
out.println("<h1>게시판</h1>");
```

| 메소드 | 하는 일 |
| --- | --- |
| `setContentType(type)` | 응답 형식과 문자셋 |
| `getWriter()` | 문자 출력 스트림 |
| `getOutputStream()` | 바이트 출력 (이미지·파일) |
| `setStatus(code)` | 상태 코드 지정 |
| `sendError(code, msg)` | 오류 응답 |
| `sendRedirect(url)` | 다른 주소로 보내기 |
| `setHeader(name, value)` | 헤더 추가 |

JSON을 내보내려면 형식을 바꿔 준다.

```java
resp.setContentType("application/json; charset=UTF-8");
resp.getWriter().print("{\"no\":1,\"title\":\"제목\"}");
```

문자열을 직접 만드는 대신 Java day15 Map과 HashMap 에서 본 Map·DTO를 라이브러리로 변환하는 쪽이 실제 방식이고, 스프링에서는 그 변환이 자동으로 일어난다(3-2).

`setContentType` 은 **출력 스트림을 얻기 전에** 불러야 문자셋이 반영된다. 순서가 바뀌면 한글이 깨진다.

### 2-3. 상태 코드 — 결과를 숫자로 알리기

응답 본문과 별개로, 처리 결과를 숫자로 알려 주는 자리가 있다.

| 코드 | 뜻 | 쓰는 자리 |
| --- | --- | --- |
| 200 OK | 성공 | 조회 성공 |
| 201 Created | 생성됨 | 등록 성공 |
| 204 No Content | 성공, 본문 없음 | 삭제 성공 |
| 400 Bad Request | 요청이 잘못됨 | 필수 값 누락 |
| 401 / 403 | 인증 안 됨 / 권한 없음 | 로그인 필요 |
| 404 Not Found | 대상 없음 | 없는 글 번호 |
| 405 Method Not Allowed | 지원하지 않는 방식 | 재정의하지 않은 `doXXX` |
| 500 Internal Server Error | 서버 오류 | 처리 중 예외 |

405가 눈여겨볼 자리다. `doPut` 을 재정의하지 않은 서블릿에 PUT 요청을 보내면 `HttpServlet` 의 기본 구현이 이 코드를 돌려준다(1-3). 실습에서 네 메소드를 모두 열어 둔 것은 그 자리를 미리 잡아 둔 셈이다.

### 2-4. 화면으로 넘기기 — 포워드와 리다이렉트

응답을 직접 만들지 않고 다른 자리로 넘기는 방법이 둘이다.

```java
// ① 포워드 — 서버 안에서 넘긴다
req.setAttribute("list", 목록);
req.getRequestDispatcher("/WEB-INF/board.jsp").forward(req, resp);

// ② 리다이렉트 — 브라우저에게 다시 요청하라고 한다
resp.sendRedirect("/board");
```

| | 포워드 | 리다이렉트 |
| --- | --- | --- |
| 요청 횟수 | 1번 | 2번 |
| 주소창 | 그대로 | 바뀐다 |
| 데이터 전달 | `req` 를 그대로 넘긴다 | 끊긴다 — 쿼리·세션으로 |
| 쓰는 자리 | 조회 결과를 화면에 | 등록·삭제 뒤 목록으로 |

등록 처리 뒤에 리다이렉트를 쓰는 이유가 있다. POST 처리 결과를 그대로 보여 주면 새로고침할 때 등록이 한 번 더 일어난다. 처리 후 목록 주소로 돌려보내면 새로고침해도 조회만 반복된다 — POST 후 리다이렉트라고 부르는 형태다.

### 2-5. 세션과 쿠키 — 요청 사이를 잇기

HTTP는 요청 하나가 끝나면 서로를 기억하지 않는다. 로그인 상태를 유지하려면 별도의 장치가 필요하다.

```java
HttpSession session = req.getSession();
session.setAttribute("loginId", "hong");     // 담기
String id = (String) session.getAttribute("loginId");  // 꺼내기
session.invalidate();                        // 로그아웃
```

| 저장 위치 | 방식 | 성격 |
| --- | --- | --- |
| 쿠키 | 브라우저에 저장 | 용량 작고, 사용자가 볼 수 있다 |
| 세션 | 서버에 저장, 열쇠만 쿠키로 | 민감한 값에 적합 |

JS day13 웹 스토리지와 인터벌 에서 브라우저 쪽 저장소를 다뤘는데, 그 반대편이 이 세션이다. 로그인 정보처럼 브라우저가 마음대로 바꾸면 안 되는 값은 서버에 두고 열쇠만 넘긴다.

`getAttribute()` 의 반환 타입이 `Object` 라 꺼낼 때 캐스팅이 필요하다 — Java day10 상속과 다형성 의 다운캐스팅이 그대로 쓰인다.

### 2-6. 스코프 — 값이 살아 있는 범위

값을 담아 두는 자리가 범위별로 셋이다.

| 스코프 | 살아 있는 동안 | 담는 것 |
| --- | --- | --- |
| request | 요청 하나가 끝날 때까지 | 화면에 넘길 조회 결과 |
| session | 브라우저 하나가 접속을 유지하는 동안 | 로그인 정보 |
| application | 서버가 켜져 있는 동안 | 전체 공통 설정 |

셋 다 `setAttribute`·`getAttribute` 로 쓰는 형태가 같아서, **어느 범위에 담을지**만 고르면 된다. 아래로 갈수록 오래 살고 그만큼 공유 범위가 넓어지므로, application 스코프는 Java day16 스레드 동기화 의 공유 자원 문제를 그대로 안는다.

### 2-7. 필터 — 모든 요청을 지나가게 하기

인코딩 설정이나 로그인 확인처럼 **모든 서블릿에 공통으로 필요한 처리**는 필터로 뺀다.

```java
public class EncodingFilter implements Filter {
    @Override
    public void doFilter(ServletRequest req, ServletResponse resp, FilterChain chain)
            throws IOException, ServletException {
        req.setCharacterEncoding("UTF-8");
        chain.doFilter(req, resp);      // 다음으로 넘긴다
    }
}
```

```
요청 → 필터1 → 필터2 → 서블릿 → 필터2 → 필터1 → 응답
```

`chain.doFilter()` 를 부르면 다음으로 넘어가고, 부르지 않으면 거기서 막힌다. 로그인 확인 필터가 로그인 안 된 요청을 여기서 돌려보내는 식으로 쓰인다.

서블릿마다 같은 코드를 넣는 대신 한 자리에 모으는 형태라, 1-5에서 `service()` 에 공통 처리를 넣던 것보다 범위가 넓다.

## 3. 더 나아가 알면 좋은 것

### 3-1. 서블릿 하나가 앞을 다 받는 구조

서블릿을 주소마다 하나씩 만들면 클래스가 계속 늘어난다. 게시판만 해도 목록·상세·등록·수정·삭제가 있고, 회원·댓글이 붙으면 금세 수십 개가 된다.

그래서 **서블릿 하나가 모든 요청을 받아 안에서 나눠 주는** 구조가 나왔다.

```
모든 요청 → 서블릿 하나 → 주소를 보고 담당 객체에 넘긴다
```

이 하나를 프론트 컨트롤러라고 부르고, 스프링의 `DispatcherServlet` 이 정확히 그것이다 — Spring Boot 프로젝트 생성(분석) 3-4에서 그림으로 본 자리다. 스프링을 쓰면 서블릿을 직접 만들 일이 거의 없어지는 이유가 여기 있다. 서블릿은 하나뿐이고, 개발자는 그 뒤에 붙는 **메소드**만 만든다.

| | 서블릿 직접 | 스프링 MVC |
| --- | --- | --- |
| 주소당 단위 | 클래스 하나 | 메소드 하나 |
| 주소 등록 | `@WebServlet` | `@GetMapping` 등 |
| 요청 값 | `req.getParameter()` 로 꺼내 변환 | 매개변수로 받는다 |
| 응답 | `resp.getWriter()` 로 직접 | 반환값이 응답이 된다 |

### 3-2. 스프링 컨트롤러로 바꿔 보면

같은 게시판을 스프링 방식으로 쓰면 이렇게 줄어든다.

```java
@RestController
@RequestMapping("/board")
public class BoardController {

    @GetMapping    public String list()                     { return "목록"; }
    @PostMapping   public String write(@RequestBody Dto d)   { return "등록"; }
    @PutMapping    public String edit(@RequestBody Dto d)    { return "수정"; }
    @DeleteMapping public String delete(@RequestParam int no){ return "삭제"; }
}
```

1-6의 네 메소드가 그대로 남아 있는데 이름과 형태만 바뀌었다. 없어진 것을 정리하면 이렇다.

- `extends HttpServlet` — 상속이 필요 없다. 애노테이션이 역할을 표시한다
- `req`·`resp` 매개변수 — 필요할 때만 받는다
- 파라미터 꺼내 변환하기 — 매개변수 타입을 보고 알아서 변환된다
- 출력 스트림 — 반환값이 응답 본문이 된다

**서블릿이 사라진 것이 아니라 감춰진 것**이라는 점이 핵심이다. 안에서는 여전히 `DispatcherServlet` 이 요청을 받고 `HttpServletRequest` 가 오간다. 그래서 스프링을 쓰다가 세션·필터·상태 코드 이야기가 나오면 결국 이번에 본 개념으로 돌아온다.

### 3-3. 요청마다 스레드 — 서블릿과 멀티스레드

1-4에서 짚은 것을 조금 더 벌려 둔다. 톰캣의 처리 구조는 Java day16 스레드 동기화 에서 본 스레드 풀 그 자체다.

```
요청 → 톰캣 스레드 풀(기본 200) → 서블릿 객체 하나 → doGet 실행
```

- 서블릿 객체는 **하나** — 요청이 100개여도 인스턴스는 하나
- 스레드는 **여러 개** — 같은 `doGet` 을 동시에 실행한다

즉 서블릿의 메소드는 처음부터 멀티스레드 환경에서 도는 코드다. day16의 계산기 예제에서 두 스레드가 같은 객체를 건드리던 상황이, 여기서는 기본 상태다.

| 방침 | 이유 |
| --- | --- |
| 멤버 변수를 두지 않는다 | 모든 요청이 공유한다 |
| 처리 값은 지역 변수로 | 스레드마다 따로 잡힌다 |
| 공유가 꼭 필요하면 동기화·동시성 컬렉션 | day16 2-4 |

스프링 빈이 기본적으로 싱글톤인 것(Spring Boot 프로젝트 생성(분석) 3-2)도 같은 구조가 한 층 올라온 결과다. [[개념 - 싱글톤]] 을 직접 만들며 정리한 성질이 서블릿 컨테이너 수준에서 이미 적용돼 있는 셈이다.

톰캣의 스레드 수는 설정으로 조절한다.

```properties
server.tomcat.threads.max=200
server.tomcat.accept-count=100
```

day16 2-10에서 풀 크기를 정하던 이야기가 그대로 서버 설정 항목이 된다.

### 3-4. HTTP를 조금 더 — 멱등성과 안전성

방식 네 개를 나눈 기준에는 CRUD 말고 성질 두 가지가 더 있다.

| 방식 | 안전(safe) | 멱등(idempotent) |
| --- | --- | --- |
| GET | 예 — 상태를 바꾸지 않는다 | 예 |
| POST | 아니오 | **아니오** |
| PUT | 아니오 | 예 |
| DELETE | 아니오 | 예 |

**멱등하다**는 것은 같은 요청을 여러 번 보내도 결과가 같다는 뜻이다. `#멱등성`

- PUT으로 "3번 글의 제목을 X로" 를 열 번 보내도 결과는 제목이 X인 상태 하나다
- POST로 "글을 등록" 을 열 번 보내면 글이 열 개 생긴다

2-4에서 POST 후 리다이렉트를 쓰는 이유가 이 표에서 나온다. 네트워크가 끊겨 재시도하는 상황에서도 성질이 갈리므로, **어떤 방식을 고를지는 편의가 아니라 성질의 문제**다.

GET이 안전하다는 성질도 실제로 걸린다. 브라우저·검색 엔진·캐시가 GET 요청을 마음대로 다시 보낼 수 있어서, 삭제를 GET으로 만들어 두면 의도치 않게 실행될 수 있다.

### 3-5. JSP와 템플릿 — 화면을 만드는 자리

2-2처럼 `out.println("<h1>…")` 으로 HTML을 만드는 방식은 금방 한계가 온다. 자바 코드 안에 태그가 섞여 읽기 어려워진다.

그래서 **HTML 안에 자바를 넣는** 방향으로 뒤집은 것이 JSP다.

| | 서블릿 | JSP |
| --- | --- | --- |
| 중심 | 자바 코드 | HTML |
| 성격 | 처리 | 화면 |

JSP도 결국 서블릿으로 변환되어 실행된다 — 두 방식이 다른 기술이 아니라 같은 것의 두 얼굴이다.

지금은 JSP보다 HTML day02 문서 구조와 미디어 같은 정적 파일 + JSON API 조합이나 타임리프 같은 템플릿 엔진을 쓰는 쪽이 많다. JS day14 게시판 CRUD 처럼 프론트가 데이터를 받아 화면을 그리는 구조라면, 서버는 화면을 만들지 않고 JSON만 내보내면 된다.

### 3-6. WAS와 웹서버

이름이 비슷해 헷갈리는 자리를 정리해 둔다.

| | 웹서버 | WAS(웹 애플리케이션 서버) |
| --- | --- | --- |
| 예 | Nginx·Apache | 톰캣·제티 |
| 하는 일 | 정적 파일 전달 | **코드를 실행**해 동적 응답 생성 |

실제 운영에서는 앞에 웹서버를 두고 뒤에 WAS를 두는 구성을 자주 쓴다. 이미지·CSS 같은 정적 파일은 앞에서 바로 내보내고, 처리해야 하는 요청만 뒤로 넘기는 형태다.

Spring Boot 프로젝트 생성(분석) 2-8에서 본 실행 가능한 jar 는 그 뒤쪽(WAS)을 통째로 안에 넣은 것이다.

### 3-7. 다음에 볼 키워드

- 서블릿(Servlet)과 서블릿 컨테이너, 톰캣의 역할
- `javax.servlet` 과 `jakarta.servlet` 패키지 이름 변경
- `HttpServlet` 상속, `Servlet` 인터페이스와의 차이
- 서블릿 생명주기 — `init()`·`service()`·`destroy()` 와 호출 횟수
- `service()` 가 `doXXX` 를 갈라 부르는 구조, `super.service()` 를 부르는 이유
- `doGet`·`doPost`·`doPut`·`doDelete` 와 CRUD 대응
- `@WebServlet` 주소 매핑, `web.xml` 과 `@ServletComponentScan`
- `HttpServletRequest` — `getParameter`·`getMethod`·`getHeader`·`getReader`
- `HttpServletResponse` — `setContentType`·`getWriter`·`setStatus`·`sendRedirect`
- 문자 인코딩 설정 시점(`setCharacterEncoding`·`setContentType`)
- HTTP 상태 코드 — 200·201·204·400·401·403·404·405·500
- 포워드와 리다이렉트, POST 후 리다이렉트
- 세션과 쿠키, `HttpSession`·`invalidate()`
- 스코프 — request·session·application
- 필터(`Filter`)와 `FilterChain`, 공통 처리 분리
- 서블릿의 단일 인스턴스와 멀티스레드 안전성, 멤버 변수 금지
- 톰캣 스레드 풀 설정(`server.tomcat.threads.max`)
- 프론트 컨트롤러 패턴과 `DispatcherServlet`
- 스프링 MVC 애노테이션 — `@RestController`·`@RequestMapping`·`@GetMapping`
- HTTP 메소드의 안전성(safe)과 멱등성(idempotent)
- JSP와 템플릿 엔진(타임리프), 서버 렌더링과 JSON API
- 웹서버와 WAS의 구분, 정적 자원과 동적 처리

## 실습 파일

- `2026B_Spring/springweb/src/main/java/day01/BoardController.java` (컨트롤러에 HTTP를 붙이는 수단으로서의 서블릿, `jakarta.servlet` 패키지 임포트, `extends HttpServlet` 으로 규격 물려받기, 생명주기 메소드 `init`·`service`·`destroy` 오버라이딩과 각각의 호출 시점, HTTP 방식별 `doGet`·`doPost`·`doPut`·`doDelete` 재정의 자리 잡기, `HttpServletRequest`·`HttpServletResponse` 를 매개변수로 받는 구조, `@WebServlet` 으로 주소 등록하기, doXXX 안에서 DAO를 불러 처리하는 배치)

## 관련 노트

Java MOC · Spring Boot 프로젝트 생성(분석) · [[Spring day02 스프링 부트 실행과 계층 이식]] · Java day16 스레드 동기화 · Java day15 Map과 HashMap · Java day13 Object 클래스와 리플렉션 · Java day12 예외 처리와 JDBC · Java day12 종합예제 JDBC DAO · Java day11 인터페이스 · Java day11 종합예제 인터페이스 DAO · Java day10 상속과 다형성 · Java day09 MVC 종합예제 · Java day06 생성자와 콘솔 게시판 · [[개념 - CRUD]] · [[개념 - 싱글톤]] · JS day13 웹 스토리지와 인터벌 · JS day14 게시판 CRUD · HTML day02 문서 구조와 미디어 · [[KDT_2026 학습 지도]]
