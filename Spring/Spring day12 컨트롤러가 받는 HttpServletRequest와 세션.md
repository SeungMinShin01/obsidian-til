---
출처: Claude 분석
원본: KDT_2026/2026B_Spring/springweb/src/main/java/day12, springweb/src/main/resources/sql/0928.sql, springweb/src/main/resources/application.properties, springweb/build.gradle
작성일: 2026-09-28
tags: [학습, java]
---
<!-- 2026-09-28 보강: AppStart(@EnableJpaAuditing)·CORS 자격증명·/me·/logout·실제 비밀번호 해싱 추가 -->

# Spring day12 — 컨트롤러가 받는 HttpServletRequest와 세션

> 실습 파일: `day12/MemberController.java`, `day12/MemberEntity.java`, `day12/MemberDto.java`, `day12/MemberRepository.java`, `day12/MemberService.java`, `day12/BaseTime.java`, `day12/AppStart.java`, `resources/sql/0928.sql`, `build.gradle`
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

### 1-3. 로그인에 쓸 회원 도메인 — MemberEntity·MemberDto·초기 데이터 (보강)

세션 API를 확인한 다음으로, 실제로 그 세션에 얹을 회원 정보 쪽 도메인이 갖춰졌다. `MemberEntity`·`MemberDto`·시드 SQL 세 파일이 한 벌로 붙는다.

```java
@Entity
@Table(name = "member")
@NoArgsConstructor
@AllArgsConstructor
@Data
@Builder
public class MemberEntity extends BaseTime {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long mno;

    @Column(nullable = false, unique = true, length = 100)
    private String mid;

    @Column(nullable = false)
    private String mpwd;

    @Column(nullable = false, length = 30)
    private String mname;

    @Builder.Default
    @ColumnDefault("'user'")
    @Column(nullable = false, length = 20)
    private String role = "user";
}
```

- `extends BaseTime`으로 [[Spring day05 엔티티 제약과 감사 필드]]에서 정리해 둔 생성·수정 시각 감사 필드를 그대로 물려받는다. 새 도메인마다 다시 만들 필요 없이 상속 한 줄로 끝나는 자리다.
- `mid`에 `unique = true`를 걸어 같은 아이디로 두 번 가입하는 것을 표 단계에서 막는다.
- `role` 필드에는 기본값 표시가 두 겹 붙어 있다.

| 표시 | 적용 시점 | 막는 문제 |
| --- | --- | --- |
| `@Builder.Default`(+ 필드 초기값 `= "user"`) | 자바 쪽 — 빌더로 객체를 만드는 시점 | `role`을 안 넣고 빌드하면 `null`이 되는 것 |
| `@ColumnDefault("'user'")` | DB 쪽 — 테이블을 만드는 시점(DDL) | 스프링을 거치지 않고 다른 경로로 값 없이 들어오는 것 |

두 표시는 "같은 기본값을 자바 객체 생성 시점과 DB 스키마 시점 양쪽에 둔다"는 점에서 겹쳐 보이지만 막는 경로가 다르다. `@Builder.Default`만 있으면 DB에 직접 값을 넣는 경로(시드 SQL 등)까지는 못 막고, `@ColumnDefault`만 있으면 자바 쪽에서 빌더로 만든 객체를 저장 전에 조회했을 때는 `null`로 보일 수 있다. 여기서는 양쪽을 함께 둬 어느 경로로 값이 들어오든 `"user"`가 채워지게 했다.

```java
public MemberEntity toEntity() {
    return MemberEntity.builder()
            .mid(this.mid)
            .mpwd(this.mpwd)
            .mname(this.mname)
            .role(this.role != null && !this.role.isBlank() ? this.role : "user")
            .build();
}

public static MemberDto from(MemberEntity entity) {
    return MemberDto.builder()
            .mno(entity.getMno())
            .mid(entity.getMid()) // 비밀번호(mpwd)는 반환 DTO에서 제외
            .mname(entity.getMname())
            .role(entity.getRole())
            .createDate(entity.getCreateDate().toString())
            .updateDate(entity.getUpdateDate().toString())
            .build();
}
```

`toEntity()`·`from()` 두 변환 메소드의 기본 모양은 [[Spring day05 DTO 변환과 초기 데이터 적재]]에서 다진 것과 같다. 이 도메인에서 눈에 띄는 자리는 `from()`이다 — 엔티티에는 `mpwd` 필드가 있는데, DTO로 바꿔 내보내는 `from()`은 그 값을 아예 옮기지 않는다. 조회·마이페이지 같은 응답에 비밀번호가 실려 나가는 것을 변환 메소드 한 곳에서 막아 두는 자리다. day07·day08 노트에서 "다음에 볼 키워드"로만 적어 뒀던 비밀번호 보호가, 이 코드에서는 해싱 이전에 "애초에 응답에 안 담기"라는 형태로 먼저 나타났다.

`toEntity()` 쪽의 `role` 삼항연산자도 같은 방향이다. 회원가입 요청에 `role`을 안 실어 보내거나 빈 문자열을 보내도 `"user"`로 떨어지게, 변환 자리에서 한 번 더 걸러 둔다.

시드 데이터(`sql/0928.sql`)는 회원 20명을 미리 채워 둔다.

```sql
INSERT INTO member (mid, mpwd, mname, role, create_date, update_date)
VALUES ('user01', '(BCrypt 해시 문자열)', '김민수', 'admin', now(), now());
-- user02 ~ user20 같은 모양, role은 대부분 'user' 이고 두 건만 'admin'
```

- `mpwd` 칸에 들어간 값은 평문이 아니라 BCrypt 해시다. day07·day08 노트의 "더 나아가기"에 적어 둔 "비밀번호는 해시로 저장한다"가 시드 데이터 단계에서부터 지켜지고 있는 자리로, 로그인 기능을 붙일 때는 `equals` 비교가 아니라 `PasswordEncoder.matches(입력 평문, 저장된 해시)`로 대조하게 된다.
- 20건 중 두 건만 `role = 'admin'`이고 나머지는 `'user'`다. 관리자·일반회원을 가르는 값이 코드가 아니라 데이터로 미리 준비된 셈이라, 권한별로 접근을 가르는 다음 실습(관리자 전용 화면 등)이 이어질 자리로 읽힌다.
- 설정 파일(`application.properties`)도 이 시드에 맞춰 DB(`mydb0928`)와 초기화 SQL 경로(`classpath:/sql/0928.sql`)가 갱신되어 있다. 한 설정 파일을 여러 day가 돌려 쓰는 사정은 day10·day11 노트에서 정리한 그대로다 — 이 실습을 다시 띄울 때는 `spring.sql.init.mode`가 `always`인지부터 확인하는 편이 안전하다.

### 1-4. 회원가입·로그인 흐름 — findByXXX 쿼리 메소드와 BCrypt 대조 (보강)

회원 도메인 세 파일이 갖춰진 다음, 실제로 가입·로그인 흐름이 붙었다. 리포지토리에 조회용 쿼리 메소드 두 개가 추가된다.

```java
@Repository
public interface MemberRepository extends JpaRepository<MemberEntity, Integer> {
    MemberEntity findByMid(String mid);
    Optional<MemberEntity> findByMname(String mname);
}
```

- 메소드 이름만으로 조회 조건이 정해지는 쿼리 메소드(day08에서 다진 것과 같은 규칙)다. `findByMid`는 아이디 하나로 유니크 조회이므로 엔티티를 바로 반환하고, `findByMname`은 값이 없을 수 있다는 뜻으로 `Optional`로 감싸 반환한다. 같은 성격의 조회인데도 반환 타입을 다르게 고르는 판단 기준을 보여준다.

서비스 쪽에는 `BCryptPasswordEncoder`가 붙는다. `build.gradle`에 `spring-security-crypto` 의존성 한 줄이 새로 추가된 것도 이 클래스를 쓰기 위해서다.

```java
@Service
@RequiredArgsConstructor
public class MemberService {
    private final MemberRepository memberRepository;
    private final BCryptPasswordEncoder passwordEncoder = new BCryptPasswordEncoder();

    public boolean signup(MemberDto memberDto) {
        MemberEntity savedEntity = memberRepository.save(memberDto.toEntity());
        return savedEntity.getMno() >= 1;
    }

    public MemberDto login(MemberDto memberDto) {
        MemberEntity memberEntity = memberRepository.findByMid(memberDto.getMid());
        if (memberEntity == null) return null;
        if (!passwordEncoder.matches(memberDto.getMpwd(), memberEntity.getMpwd())) return null;
        return MemberDto.from(memberEntity);
    }
}
```

- `signup()`은 [[Spring day11 리액트 화면에 내줄 게시판 목록 API]]에서 봤던 "저장 후 PK로 성공 판정" 패턴을 그대로 가져다 쓴다 — `save()`가 돌려준 엔티티의 PK(`mno`)가 1 이상이면 저장이 된 것으로 본다.
- `login()`은 아이디로 먼저 조회하고, 없으면 곧장 `null`을 돌려준다. 있으면 `passwordEncoder.matches(평문, 저장된 해시)`로 대조하는데, 인자 순서가 "입력받은 평문이 먼저, DB에 있는 해시가 나중"이라는 점을 헷갈리지 않아야 하는 자리다. 일치하면 `MemberDto.from()`으로 비밀번호를 뺀 정보만 돌려준다.
- `BCryptPasswordEncoder`를 서비스 필드에서 `new`로 직접 만들어 쓰고 있는데, 스프링 빈으로 등록해 주입받는 방식도 흔히 쓰인다 — 어느 쪽이든 인코더 객체 하나를 앱 전체가 공유해서 쓰는 셈은 같다.

컨트롤러는 이 서비스 메소드 둘을 엔드포인트로 그대로 연결한다.

```java
@PostMapping("/signup")
public boolean signup(@RequestBody MemberDto memberDto) {
    return memberService.signup(memberDto);
}

@PostMapping("/login")
public MemberDto login(@RequestBody MemberDto memberDto, HttpSession session) {
    MemberDto result = memberService.login(memberDto);
    session.setAttribute("login_member", result);
    return result;
}
```

- 1-2에서 이론으로 짚었던 "로그인 성공 정보를 세션에 저장"이 여기서 실제로 일어난다 — 매개변수에 `HttpSession session`을 추가로 받아, 로그인 서비스가 돌려준 결과를 `"login_member"`라는 키로 얹어 둔다. 이후 다른 요청에서 `session.getAttribute("login_member")`로 이 값을 꺼내면 로그인 여부·로그인한 회원 정보를 확인할 수 있는 자리로 이어진다.

### 1-5. 로그인 뒤에 채워진 나머지 조각들 — CORS 자격증명·내 정보 조회·로그아웃·실제 해싱 (보강)

로그인 엔드포인트가 세션에 값을 얹는 것까지 확인한 다음, 이 세션을 다른 포트(리액트 개발 서버)에서 실제로 주고받는 데 필요한 나머지 조각들이 채워졌다.

```java
@RestController
@RequestMapping("/api/member")
@RequiredArgsConstructor
@CrossOrigin(origins = "http://localhost:5173", allowCredentials = "true") // 도메인 다른 경우 allowCredentials 이용한 쿠키/세션 유지
public class MemberController {
    private final MemberService memberService;
    ...
}
```

- day11 노트에서 본 `@CrossOrigin("http://localhost:5173")`은 요청 자체를 허용하는 표시였는데, 세션 쿠키(`JSESSIONID`)까지 다른 포트로 오가려면 한 단계가 더 필요하다. 서버 쪽은 `allowCredentials = "true"`를 붙이고, 화면 쪽은 `axios` 요청마다 `{ withCredentials: true }`를 넣어야 브라우저가 쿠키를 실어 보낸다. 둘 중 하나만 있으면 세션이 이어지지 않는다.

```java
// [3] 내정보조회 + 세션 (이미 로그인된 회원이 내정보 요청)
@GetMapping("/me")
public MemberDto getMyInfo(HttpSession session) {
    Object obj = session.getAttribute("login_member");
    if (obj == null) return null;
    MemberDto memberDto = (MemberDto) obj;
    return memberService.getMyInfo(memberDto.getMno());
}

// [4] 로그아웃 + 세션 (초기화)
@PostMapping("/logout")
public boolean logout(HttpSession httpSession) {
    httpSession.invalidate();
    return true;
}
```

- `/me`는 화면을 새로고침했을 때 "지금 로그인되어 있는지"를 확인하는 자리다. 세션에서 `"login_member"`를 꺼내 보고 없으면 `null`(미로그인)을 돌려주고, 있으면 `Object`로 저장돼 있던 값을 `MemberDto`로 다운캐스팅한 다음 회원번호로 서비스에 다시 조회를 맡긴다.
- `/logout`은 1-2에서 이론으로만 짚었던 `invalidate()`를 엔드포인트 하나로 내보낸 것이다. 호출 성공 여부를 `boolean`으로 돌려준다.
- 서비스 쪽 `getMyInfo(Long mno)`는 `findById`로 회원번호를 조회해 존재하면 `MemberDto.from()`으로 비밀번호를 뺀 정보를 돌려주고, 없으면 `null`이다. `login()`이 아이디로 찾는 것과 달리 여기는 PK로 찾는 차이가 있다.
- `signup()` 안쪽도 이제는 비밀번호를 그대로 저장하지 않는다.

```java
public boolean signup(MemberDto memberDto) {
    MemberEntity memberEntity = memberDto.toEntity();
    String 암호문 = passwordEncoder.encode(memberDto.getMpwd());
    memberEntity.setMpwd(암호문);
    MemberEntity savedEntity = memberRepository.save(memberEntity);
    return savedEntity.getMno() >= 1;
}
```

  2-4에서 "다음에 할 일"로 적어 두었던 해싱이 여기서 실제로 들어간다 — 회원가입 시점에 받은 평문을 `passwordEncoder.encode()`로 감싸 엔티티에 다시 대입한 다음 저장한다. 로그인 쪽의 `passwordEncoder.matches(평문, 암호문)`과 짝을 이루는 자리다.
- 진입 클래스 `AppStart`에는 `@EnableJpaAuditing`이 붙어 있다. [[Spring day05 엔티티 제약과 감사 필드]]에서 다진 `@CreatedDate`·`@LastModifiedDate`는 이 애노테이션이 앱 어딘가에 하나 있어야 실제로 값을 채워 준다 — 필드에 표시만 해 두고 활성화를 빠뜨리면 두 칸이 계속 `null`로 남는 자리라, 감사 필드를 쓰는 프로젝트에서는 진입 클래스 쪽도 함께 확인하는 편이 안전하다.

## 2. 추가로 알면 좋은 활용법

### 2-1. 세션에는 최소한의 정보만 얹기

세션에는 값을 아무 타입이나(Object) 얹을 수 있어서 DTO나 엔티티를 통째로 넣는 것도 가능하지만, 세션에 얹은 객체는 로그아웃하거나 만료되기 전까지 서버 메모리를 계속 붙잡고 있다는 점을 감안해야 한다. 로그인 확인에 실제로 필요한 최소 정보(회원 번호·아이디 정도)만 세션에 두고, 나머지 상세 정보는 필요할 때마다 DB에서 다시 조회하는 편이 메모리 부담을 줄인다.

### 2-2. 로그인 확인이 여러 컨트롤러에서 반복되는 지점

로그인이 필요한 기능마다 메소드 맨 앞에서 `session.getAttribute(...)`로 로그인 여부를 확인하는 코드를 반복해서 넣게 되면 같은 검사 코드가 컨트롤러마다 흩어진다. 이 반복을 요청이 컨트롤러에 닿기 전 한 곳에서 걸러내는 방식(인터셉터·필터)으로 옮기는 것이 다음 단계다.

### 2-3. 민감한 필드를 걷어내는 자리는 변환 메소드 하나로 좁혀 두기 (보강)

`MemberDto.from()`이 `mpwd`를 옮기지 않는 것처럼, 엔티티에는 있지만 밖으로 내보내면 안 되는 필드가 있을 때는 그 판단을 컨트롤러·서비스 여기저기에 흩어 두지 않고 `from()` 한 곳에 모아 두는 편이 안전하다. 민감한 필드가 나중에 하나 더 늘어도 고칠 자리가 한 곳으로 고정된다.

### 2-4. 비밀번호는 저장하기 전에 해시로 바꿔 두기

로그인 대조를 `passwordEncoder.matches(평문, 해시)`로 하려면, 애초에 저장되는 시점부터 비밀번호가 해시 형태여야 한다. 회원가입 흐름을 짤 때는 "받은 비밀번호를 저장하기 직전에 인코더로 한 번 감싼다"를 습관으로 붙여 두는 편이 안전하다 — 시드 데이터(`0928.sql`)가 이미 해시로 채워져 있던 것도 같은 이유다.

### 2-5. 쿠키를 주고받는 요청에는 양쪽 다 자격증명을 켜 두기 (보강)

세션 쿠키로 로그인 상태를 유지하는 구조에서는 서버의 `allowCredentials = "true"`와 화면의 `axios` 요청 옵션 `{ withCredentials: true }`가 한 짝이다. 둘 중 하나만 빠뜨려도 브라우저가 쿠키를 안 보내거나 서버가 응답에 쿠키 허용 헤더를 안 붙여서, 로그인은 성공한 것처럼 보여도 다음 요청에서 세션이 끊긴 것처럼 동작한다. CORS 오류 없이 요청이 되는데 로그인 유지만 안 될 때 먼저 의심해 볼 자리다.

## 3. 더 나아가 알면 좋은 것

### 3-1. 세션 방식의 한계와 대안

세션은 서버(톰캣) 메모리에 저장되는 정보라, 서버가 한 대일 때는 문제가 없지만 트래픽이 늘어 서버를 여러 대로 늘리면(스케일아웃) 다른 서버가 그 세션을 읽지 못하는 문제가 생긴다. 이를 해결하려고 세션을 Redis 같은 외부 저장소에 두고 여러 서버가 공유하는 방식(분산 세션), 또는 서버가 상태를 아예 들고 있지 않고 매 요청마다 토큰으로 신원을 증명하는 무상태(stateless) 방식인 JWT 인증으로 넘어가는 흐름이 있다. REST API 서버에서는 쿠키 기반 세션보다 JWT 같은 토큰을 헤더에 실어 보내는 방식이 더 흔히 쓰인다.

### 3-2. 다음에 볼 키워드

- `HandlerInterceptor` / 필터 — 로그인 검사를 컨트롤러 앞단에서 공통으로 처리하기
- Spring Security — 인증·인가를 프레임워크 단에서 표준화하기
- JWT — 세션 없이 요청마다 신원을 증명하는 토큰 방식
- 쿠키(`JSESSIONID`) — 세션 식별자를 브라우저가 들고 있게 하는 통로
- `role` 기반 접근 제어 — 시드에 심어 둔 admin/user 두 값을 실제 엔드포인트 분기에 쓰기
- 로그인 실패를 더 세분화하기 — 아이디가 없는 경우와 비밀번호가 틀린 경우를 같은 `null`로 뭉치지 않는 방법

## 실습 파일

- `KDT_2026/2026B_Spring/springweb/src/main/java/day12/MemberController.java` — `HttpServletRequest`·`HttpSession` 기본 API(요청 정보·세션 속성 저장/조회·`invalidate`)를 확인하는 컨트롤러, `@CrossOrigin(allowCredentials = "true")`·회원가입/로그인/내정보조회(`/me`)/로그아웃 엔드포인트 (보강)
- `KDT_2026/2026B_Spring/springweb/src/main/java/day12/MemberEntity.java` — `member` 표 엔티티, `extends BaseTime`으로 감사 필드 상속, `mid` 유니크 제약과 `role` 기본값 이중 처리(`@Builder.Default` + `@ColumnDefault`)
- `KDT_2026/2026B_Spring/springweb/src/main/java/day12/MemberDto.java` — `toEntity()`·`from()` 변환 메소드, 응답에서 비밀번호(`mpwd`)를 걷어내는 자리
- `KDT_2026/2026B_Spring/springweb/src/main/java/day12/MemberRepository.java` — `findByMid`·`findByMname` 쿼리 메소드
- `KDT_2026/2026B_Spring/springweb/src/main/java/day12/MemberService.java` — `BCryptPasswordEncoder`로 비밀번호를 해싱해 회원가입·로그인을 처리하고, 내정보조회(`getMyInfo`)까지 맡는 서비스 (보강)
- `KDT_2026/2026B_Spring/springweb/build.gradle` — `spring-security-crypto` 의존성 추가
- `KDT_2026/2026B_Spring/springweb/src/main/java/day12/BaseTime.java` — 생성·수정 시각 감사 필드(공통 상위 클래스)
- `KDT_2026/2026B_Spring/springweb/src/main/java/day12/AppStart.java` — `@EnableJpaAuditing`으로 감사 필드 활성화하는 진입 클래스 (보강)
- `KDT_2026/2026B_Spring/springweb/src/main/resources/sql/0928.sql` — 회원 20명 시드 데이터(BCrypt 해시 비밀번호, admin/user 권한 구분)

## 관련 노트

[[Spring MOC]] · [[Spring day11 리액트 화면에 내줄 게시판 목록 API]] · [[Spring day01 서블릿과 HTTP 메소드]] · [[Spring day05 엔티티 제약과 감사 필드]] · [[Spring day05 DTO 변환과 초기 데이터 적재]] · [[KDT_2026 학습 지도]]

<!--
[문체 규칙]
- 내가 공부하며 정리한 노트다. 남의 코드를 평가하는 말투를 쓰지 않는다.
  X  "주석이 정확합니다" / "~하신 게 좋습니다" / "이 저장소에서 가장 ~"
  O  "정리하면 이렇습니다" / "핵심은 ~입니다" / "~하는 편이 안전합니다"
- 2인칭(하신, 쓰셨, 적으신)을 쓰지 않는다.
- 원본 코드의 오류·오타는 기록하지 않는다. 필요하면 파일 지목 없이 일반 주의사항으로 쓴다.
- 한 사람이 쭉 이어서 쓴 것처럼 문체를 일정하게 유지한다.
-->
