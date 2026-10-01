---
출처: Claude 분석
원본: KDT_2026/2026B_Spring/springweb/src/main/java/day13
작성일: 2026-10-01
tags: [학습, java]
---

# Spring day13 — 레디스 리스트로 값 쌓고 읽기

> 실습 파일: `day13/RedisService2.java`, `day13/RedisController2.java`
> 허브: [[Spring MOC]] · 이전: [[Spring day12 컨트롤러가 받는 HttpServletRequest와 세션]] · 다음: (아직 없음)

day12에서는 레디스에 `opsForValue()`로 문자열 하나를 키에 묶어 넣었다. day13은 같은 `StringRedisTemplate`을 쓰되 값을 한 개가 아니라 **여러 개 순서대로 쌓는 리스트 구조**로 바꿔 보는 첫 걸음이다.

## 1. 배운 내용

### 1-1. 서비스 — 리스트 끝에 쌓고 전체 범위로 읽기

```java
@Service
@RequiredArgsConstructor
public class RedisService2 {
    private final StringRedisTemplate stringRedisTemplate;

    public String save(String data) {
        try {
            stringRedisTemplate.opsForList().rightPush("list", data);
            return "레디스 저장 성공";
        } catch (Exception e) {
            return "레디스 저장 실패";
        }
    }

    public List<String> getList() {
        return stringRedisTemplate.opsForList().range("list", 0, -1);
    }
}
```

- `opsForList()`는 레디스의 List 자료구조를 다루는 창구다. `opsForValue()`가 키 하나에 값 하나였다면, 리스트는 키 하나(`"list"`) 아래에 값이 줄지어 들어간다.
- `rightPush(키, 값)`은 리스트의 오른쪽 끝에 값을 붙인다. 호출할 때마다 뒤에 쌓이므로 먼저 넣은 값이 앞에 남는 입력 순서 그대로의 목록이 된다.
- `range(키, 시작, 끝)`은 인덱스 구간을 잘라서 가져온다. `0, -1`은 처음부터 마지막까지라는 뜻이라 전체 조회가 된다. 음수 인덱스는 뒤에서부터 센다.
- 레디스에 접속하지 못하면 예외가 나므로 저장 쪽은 `try-catch`로 감싸 성공·실패 문구를 문자열로 돌려주는 형태다.

| 호출 | 하는 일 | 레디스 명령 |
| --- | --- | --- |
| `rightPush("list", 값)` | 리스트 오른쪽 끝에 추가 | `RPUSH` |
| `range("list", 0, -1)` | 전체 요소를 순서대로 조회 | `LRANGE` |

### 1-2. 컨트롤러 — 쿼리스트링으로 받아 저장, 목록 반환

```java
@RestController
@RequestMapping("api/redis")
@RequiredArgsConstructor
public class RedisController2 {
    private final RedisService2 redisService;

    @GetMapping("/add")
    public String save(@RequestParam(name = "data") String data) {
        return redisService.save(data);
    }

    @GetMapping("/all")
    public List<String> getList() {
        return redisService.getList();
    }
}
```

- `GET /api/redis/add?data=값`으로 값을 하나 넣고, `GET /api/redis/all`로 지금까지 쌓인 목록을 JSON 배열로 받는다. 저장도 `GET`으로 열어 두었기 때문에 브라우저 주소창만으로 바로 확인된다.
- `@RequestParam(name = "data")`는 쿼리스트링의 `data` 값을 매개변수로 받는 방식이다. 컨트롤러는 받아서 서비스에 넘기기만 하고, 레디스 호출은 서비스에 모아 두는 계층 분리를 이번에도 지킨다.
- 컨트롤러·서비스 이름 끝에 `2`가 붙어 있는 것은 day12의 `RedisController`·`RedisService`와 클래스 이름이 겹치지 않게 두기 위한 구분으로 보인다. 스프링은 같은 이름의 빈이 두 개면 충돌을 내기 때문이다.

### 1-3. 같은 날 만들어 둔 빈 틀 — 쿠키·세션 컨트롤러

`day13/CookieController.java`, `day13/SessionController.java`는 파일만 만들어 둔 상태(내용 없음)다. day12에서 쿠키(`@CookieValue`, `ResponseCookie`)와 세션(`HttpSession`)을 각각 다룬 흐름을 day13에서 컨트롤러 단위로 다시 정리하려는 자리로 읽힌다. 내용이 채워지면 이 노트를 보강한다.

## 2. 추가로 알면 좋은 활용법

### 2-1. 키 이름은 용도가 보이게

실습에서는 키가 `"list"` 하나지만, day12에서 정리한 `도메인:식별키` 관례(`member:3`, `RT:회원번호`)를 리스트에도 그대로 쓰는 편이 안전하다. 예를 들어 `log:recent`처럼 두면 다른 키와 섞이지 않고 `keys("log:*")`로도 묶어 볼 수 있다.

### 2-2. 리스트는 쌓는 방향으로 성격이 정해진다

- 오른쪽에 넣고(`rightPush`) 왼쪽에서 꺼내면(`leftPop`) 먼저 들어온 것이 먼저 나가는 큐가 된다.
- 왼쪽에 넣고(`leftPush`) 왼쪽에서 꺼내면 나중에 들어온 것이 먼저 나가는 스택이 된다.
- 최근 N개만 보여 주는 목록이라면 `leftPush`로 쌓고 `range(키, 0, N-1)`로 앞쪽만 읽는 식으로 쓴다.

### 2-3. 저장 요청은 원래 POST

값을 바꾸는 요청은 `POST`로 여는 것이 일반적이다. 실습은 주소창에서 곧바로 확인하려고 `GET`으로 열었다고 이해해 두고, 실제 API에서는 `@PostMapping`과 `@RequestBody`로 옮기는 편이 맞다.

## 3. 더 나아가 알면 좋은 것

### 3-1. 리스트가 계속 커지는 문제

`rightPush`만 반복하면 리스트가 끝없이 길어진다. `trim`으로 길이를 자르거나, 키에 만료 시간(TTL)을 거는 방식으로 관리한다. 전체 조회(`0, -1`)도 요소가 많아지면 부담이 되므로 구간을 나눠 읽는다.

### 3-2. 다음에 볼 키워드

- `opsForSet` / `opsForHash` / `opsForZSet` — 리스트 외의 레디스 자료구조(중복 없는 집합, 필드 묶음, 점수 정렬)
- `leftPop` / `rightPop` / `size` / `trim` — 리스트의 꺼내기·길이·자르기
- 레디스 TTL(`expire`) — 쌓은 데이터의 수명 두기
- 쿠키·세션 컨트롤러 — day13에서 내용이 채워질 예정인 부분

## 실습 파일

- `KDT_2026/2026B_Spring/springweb/src/main/java/day13/RedisService2.java` — `opsForList()`의 `rightPush`·`range`로 리스트에 쌓고 전체 조회하는 서비스
- `KDT_2026/2026B_Spring/springweb/src/main/java/day13/RedisController2.java` — `/api/redis/add`, `/api/redis/all` 엔드포인트
- `KDT_2026/2026B_Spring/springweb/src/main/java/day13/CookieController.java` — 빈 파일(작성 예정)
- `KDT_2026/2026B_Spring/springweb/src/main/java/day13/SessionController.java` — 빈 파일(작성 예정)

## 관련 노트

[[Spring MOC]] · [[Spring day12 컨트롤러가 받는 HttpServletRequest와 세션]] · [[KDT_2026 학습 지도]]
