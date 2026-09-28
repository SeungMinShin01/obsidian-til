---
출처: Claude 분석
원본: KDT_2026/2026B_Spring/springweb/src/main/java/day12
작성일: 2026-09-28
tags: [학습, java]
---

# Spring day12 — 컨트롤러가 받는 HttpServletRequest와 세션

> 실습 파일: `day12/MemberController.java`
> 허브: [[Spring MOC]] · 이전: [[Spring day11 리액트 화면에 내줄 게시판 목록 API]] · 다음: (예정)

지금까지 컨트롤러 메소드는 `@RequestParam`·`@PathVariable`·`@RequestBody`로만 값을 받아 왔는데, 이번에는 매개변수에 서블릿 API 타입인 `HttpServletRequest`를 그대로 받는 자리를 확인한다. [[Spring day01 서블릿과 HTTP 메소드]]에서 이론으로만 짚었던 요청 객체·세션이 스프링 컨트롤러 안에서 실제로 어떻게 손에 잡히는지 보는 자리이고, 다음에 올 로그인 기능이 정보를 어디에 담아 둘지에 대한 준비이기도 하다.

## 1. 배운 내용

### 1-1. 컨트롤러 메소드가 HttpServletRequest를 직접 받기

```java
@RestController
@RequestMapping("/api/member")
public class MemberController {

    @GetMapping("")
    public String test(HttpServletRequest request) {
        System.out.println(request.getRemoteAddr());       // 요청한 클라이언트의 IP
        System.out.println(request.getHeader("User-Agent")); // 요청한 클라이언트 브라우저 정보
        System.out.println(request.getSession());           // 요청한 클라이언트 세션객체 정보
    }
}
```

- 매개변수 자리에 `HttpServletRequest`를 그대로 두면 스프링이 실제 요청 객체를 주입해 준다. day01의 서블릿에서 `doGet(request, response)`로 넘겨받던 것과 같은 종류의 객체를, 이번에는 스프링이 대신 만들어 컨트롤러 메소드까지 배달해 주는 자리다.
- `@RequestParam`·`@RequestBody`가 요청의 "내용물"(쿼리스트링·본문)을 꺼내는 통로라면, `HttpServletRequest`는 요청이라는 사건 자체에 딸려 온 부가 정보(보낸 주소·브라우저 정보·세션)를 꺼내는 통로다.

| 메소드 | 꺼내는 값 |
| --- | --- |
| `getRemoteAddr()` | 요청을 보낸 클라이언트의 IP |
| `getHeader("User-Agent")` | 요청 브라우저·클라이언트를 식별하는 문자열 |
| `getSession()` | 이 클라이언트의 세션 객체(없으면 새로 만들어 반환) |

### 1-2. HttpSession — 브라우저마다 독립된 저장소

```java
HttpSession session = request.getSession();
System.out.println(session.getId());                    // 세션 식별번호
System.out.println(session.getCreationTime());          // 세션 생성시간
System.out.println(session.getLastAccessedTime());      // 세션 마지막 접근 시간
System.out.println(session.getMaxInactiveInterval());   // 세션 생명주기(자동 로그아웃)

session.setAttribute("data", "사과"); // map(key:value) 구조로 저장
System.out.println(session.getAttribute("data")); // key로 value 꺼내기
session.invalidate(); // 세션 초기화
```

- 세션객체는 톰캣 서버 안에서 브라우저마다 독립적으로 유지되는 저장소다. `getSession()`을 부르면 이미 있는 세션을 돌려받거나, 없으면 새로 하나를 만들어 돌려준다.
- `setAttribute`/`getAttribute`는 `Map`과 같은 key-value 구조로 값을 얹고 꺼낸다. 로그인 성공 시 회원 정보를 이 자리에 얹어 두면, 같은 브라우저에서 다음 요청이 올 때 그 정보를 다시 꺼내 "로그인된 상태"인지 판단하는 데 쓸 수 있다.
- `invalidate()`는 세션 자체를 초기화(폐기)한다. 로그아웃 기능이 이 호출 하나로 구현되는 자리다.

| 하려는 일 | 세션 API | 비고 |
| --- | --- | --- |
| 로그인 성공 정보 저장 | `setAttribute(키, 값)` | 로그인/마이페이지/장바구니 등 휘발성 정보에 씀 |
| 로그인 여부·마이페이지 확인 | `getAttribute(키)` | 값이 없으면 `null` → 미로그인으로 판정 |
| 로그아웃 | `invalidate()` | 세션 전체를 없앰 |
| 자동 로그아웃 주기 확인 | `getMaxInactiveInterval()` | 초 단위, 별도 설정이 없으면 서버 기본값을 따름 |

## 2. 추가로 알면 좋은 활용법

### 2-1. 세션에는 최소한의 정보만 얹기

세션에는 값을 아무 타입이나(Object) 얹을 수 있어서 DTO나 엔티티를 통째로 넣는 것도 가능하지만, 세션에 얹은 객체는 로그아웃하거나 만료되기 전까지 서버 메모리를 계속 붙잡고 있다는 점을 감안해야 한다. 로그인 확인에 실제로 필요한 최소 정보(회원 번호·아이디 정도)만 세션에 두고, 나머지 상세 정보는 필요할 때마다 DB에서 다시 조회하는 편이 메모리 부담을 줄인다.

### 2-2. 로그인 확인이 여러 컨트롤러에서 반복되는 지점

로그인이 필요한 기능마다 메소드 맨 앞에서 `session.getAttribute(...)`로 로그인 여부를 확인하는 코드를 반복해서 넣게 되면 같은 검사 코드가 컨트롤러마다 흩어진다. 이 반복을 요청이 컨트롤러에 닿기 전 한 곳에서 걸러내는 방식(인터셉터·필터)으로 옮기는 것이 다음 단계다.

## 3. 더 나아가 알면 좋은 것

### 3-1. 세션 방식의 한계와 대안

세션은 서버(톰캣) 메모리에 저장되는 정보라, 서버가 한 대일 때는 문제가 없지만 트래픽이 늘어 서버를 여러 대로 늘리면(스케일아웃) 다른 서버가 그 세션을 읽지 못하는 문제가 생긴다. 이를 해결하려고 세션을 Redis 같은 외부 저장소에 두고 여러 서버가 공유하는 방식(분산 세션), 또는 서버가 상태를 아예 들고 있지 않고 매 요청마다 토큰으로 신원을 증명하는 무상태(stateless) 방식인 JWT 인증으로 넘어가는 흐름이 있다. REST API 서버에서는 쿠키 기반 세션보다 JWT 같은 토큰을 헤더에 실어 보내는 방식이 더 흔히 쓰인다.

### 3-2. 다음에 볼 키워드

- `HandlerInterceptor` / 필터 — 로그인 검사를 컨트롤러 앞단에서 공통으로 처리하기
- Spring Security — 인증·인가를 프레임워크 단에서 표준화하기
- JWT — 세션 없이 요청마다 신원을 증명하는 토큰 방식
- 쿠키(`JSESSIONID`) — 세션 식별자를 브라우저가 들고 있게 하는 통로

## 실습 파일

- `KDT_2026/2026B_Spring/springweb/src/main/java/day12/MemberController.java` — `HttpServletRequest`·`HttpSession` 기본 API(요청 정보·세션 속성 저장/조회·`invalidate`)를 확인하는 컨트롤러

## 관련 노트

[[Spring MOC]] · [[Spring day11 리액트 화면에 내줄 게시판 목록 API]] · [[Spring day01 서블릿과 HTTP 메소드]] · [[KDT_2026 학습 지도]]

<!--
[문체 규칙]
- 내가 공부하며 정리한 노트다. 남의 코드를 평가하는 말투를 쓰지 않는다.
  X  "주석이 정확합니다" / "~하신 게 좋습니다" / "이 저장소에서 가장 ~"
  O  "정리하면 이렇습니다" / "핵심은 ~입니다" / "~하는 편이 안전합니다"
- 2인칭(하신, 쓰셨, 적으신)을 쓰지 않는다.
- 원본 코드의 오류·오타는 기록하지 않는다. 필요하면 파일 지목 없이 일반 주의사항으로 쓴다.
- 한 사람이 쭉 이어서 쓴 것처럼 문체를 일정하게 유지한다.
-->
