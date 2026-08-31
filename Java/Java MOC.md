---
출처: Claude 분석
작성일: 2026-08-10
tags: [허브, java]
---

# Java MOC

Java 관련 노트의 허브입니다. 상위 지도는 [[KDT_2026 학습 지도]].
실제 프로젝트에서 이 주제가 쓰인 지점은 [[KDT_2026 학습 지도]]의 **프로젝트 매핑표**에서 찾습니다 (프로젝트 분석 노트와 직접 링크하지 않습니다).

## 프로젝트 매핑 — 학습 지도 ↔ 이 폴더

[[KDT_2026 학습 지도]]를 거쳐 들어온 경우, 프로젝트의 해당 주제는 이 노트들과 닿습니다. (프로젝트 쪽은 평문 — 직접 링크하지 않음)

| 프로젝트에서 만난 것 | 이 폴더의 이론 |
| --- | --- |
| Express 계층 분리 (routes → controllers), 싱글톤 | [[Java day09 MVC 종합예제]] |
| models/ Repository 미완성 — 규격/구현 분리 | [[Java day09 MVC 종합예제]] · [[Java day11 인터페이스]] |
| 구현 갈아끼우기 (타이어 교체 = DAO 교체) | [[Java day10 상속과 다형성]] · [[Java day11 인터페이스]] |
| setter 유효성 검사, 정보 은닉 | [[Java day08 접근제한자와 static]] |
| 게시판 CRUD의 원형 | [[Java day06 생성자와 콘솔 게시판]] · [[Java day07 메소드와 미니프로젝트]] |


## 학습 순서 (day별)

```
day01 자료형 ─→ day02 타입변환 ─→ day03 연산자 ─→ day04 제어문·배열
                                                        │
                                                        ▼
day09 ArrayList ←─ day08 캡슐화 ←─ day07 메소드 ←─ day06 생성자 ←─ day05 클래스
      │
      ▼
day10 상속·다형성 ←─ day11 인터페이스
                            │
                            ▼
day11 종합예제(인터페이스 DAO) ─→ day12 예외 처리·JDBC ─→ day12 종합예제(JDBC DAO)
                                                                    │
                                                                    ▼
                                                        day13 Object·리플렉션·표준 라이브러리
                                                                    │
                                                                    ▼
                                                        day14 제네릭·컬렉션 프레임워크
                                                                    │
                                                                    ▼
                                                        day15 Map·HashMap·Stack/Queue·스레드
                                                                    │
                                                                    ▼
                                                        day16 공유 자원·경쟁 상태·synchronized
                                                                    │
                                                                    ▼
                                                        Spring Boot 프로젝트 생성 — 웹 애플리케이션의 시작
                                                                    │
                                                                    ▼
                                                        Spring day01 서블릿 — 요청을 받는 자리
                                                                    │
                                                                    ▼
                                                        Spring day02 스프링 진입점 + 계층 이식 + 웹 CRUD + 두 번째 도메인 + 정적 화면 + axios CRUD + 두 번째 화면
                                                                    │
                                                                    ▼
                                                        Spring day03 애노테이션 만들기 + 리플렉션으로 읽어 실행 + 롬복·빌더 + IOC/DI + REST 컨트롤러로 다시 조립 + 요청 값 받기 — 스프링이 도는 원리
```

| day | 노트 | 핵심 |
| --- | --- | --- |
| 01 | [[Java day01 자바 구조와 자료형]] | 클래스·main, 8가지 기본타입, printf, Scanner |
| 02 | [[Java day02 타입 변환]] | 자동/강제 변환, 연산 중 int 승격 |
| 03 | [[Java day03 연산자]] | 산술·비교·논리·삼항, equals |
| 04 | [[Java day04 제어문과 배열]] | if/switch, for/while, 배열 메모리 |
| 05 | [[Java day05 클래스와 인스턴스]] | 객체·클래스·인스턴스, new와 참조 |
| 06 | [[Java day06 생성자와 콘솔 게시판]] | 생성자 오버로딩, this, 콘솔 CRUD |
| 07 | [[Java day07 메소드와 미니프로젝트]] | 메소드 4조합, Controller/Repository |
| 08 | [[Java day08 접근제한자와 static]] | 캡슐화, DTO, final·static |
| 09 | [[Java day09 ArrayList]] | 컬렉션, 제네릭, 가변 길이 |
| 09 | [[Java day09 MVC 종합예제]] | **MVC 4계층, DTO·DAO, 싱글톤** |
| 10 | [[Java day10 상속과 다형성]] | extends, 업·다운캐스팅, instanceof, 오버라이딩 |
| 11 | [[Java day11 인터페이스]] | interface, implements, 추상메소드, 다중 구현, 익명 구현체 |
| 11 | [[Java day11 종합예제 인터페이스 DAO]] | **인터페이스 DAO 규격, 제네릭, 싱글톤 전 계층, BaseTime 상속** |
| 12 | [[Java day12 예외 처리와 JDBC]] | try-catch-finally, 다중 catch, throws, JDBC 연결·PreparedStatement·executeQuery·ResultSet 조회 |
| 12 | [[Java day12 종합예제 JDBC DAO]] | **BaseDao 상속으로 JDBC 연동 공통화, 싱글톤 MVC 배선, DB 표를 담는 DTO, 등록·조회·수정·삭제 CRUD 완성** |
| 13 | [[Java day13 Object 클래스와 리플렉션]] | Object 최상위 클래스, toString·equals·hashCode, 문자열 리터럴 비교, Class·리플렉션, 래퍼 클래스와 오토박싱, parseXXX 타입 변환, LocalDate·DateTimeFormatter, String 클래스 메소드·문자 코드값, Random·UUID, 구분자 문자열 파싱, Scanner 입력 주의, 콘솔 렌더링, 고정폭 시각 파싱과 정수 나눗셈 요금 계산 |
| 14 | [[Java day14 제네릭]] | 타입을 비워 두고 선언하기, 타입 파라미터와 래퍼 클래스, 다중·중첩 타입, 제네릭 메소드와 타입 추론, `<T extends 상위타입>` 상한 제약, Object 대비 컴파일 시점 타입 검사, 컬렉션 프레임워크(List·Set·Map)와 인터페이스 선언·다형성, 리스트 순회 세 가지, ArrayList·LinkedList·Vector 구조 차이, Set 인터페이스와 중복 제거(equals·hashCode), Iterator 순회, TreeSet 정렬, 제네릭 클래스 직접 설계와 와일드카드 `<?>` 컬렉션 |
| 15 | [[Java day15 Map과 HashMap]] | 컬렉션 세 갈래 재정리, Map 인터페이스와 엔트리(키·값 쌍), HashMap 선언과 JSON 대응, put의 키 중복 덮어쓰기, get·size·containsKey·containsValue, keySet·values의 반환 타입 차이, remove·clear·isEmpty, 인덱스가 없어 keySet()을 거치는 순회(향상된 for·forEach), JSON↔DTO/Map 통신 구간과 키 기반 조회, Stack의 후입선출(push·pop)과 Queue의 선입선출(offer·poll), Queue를 LinkedList로 구현하는 이유, 단일 스레드와 main 스레드, Thread.sleep과 검사 예외, 프로그램·프로세스·스레드 구분, 멀티스레드 구현 세 가지(익명 구현체·Runnable 구현·Thread 상속), run과 start의 차이와 순서 미보장, Runnable 구현체로 만든 시계 스레드, 플래그(boolean)를 반복 조건으로 둔 타이머 스레드와 main에서 켜고 끄기, 공유 변수로 흐름끼리 신호 주고받기, 종료된 스레드의 재시작 불가 |
| 16 | [[Java day16 스레드 동기화]] | 멀티스레드 웹서버 구조와 장단점, 동기화(락·대기)와 비동기화의 대비, 여러 스레드가 같은 객체를 참조하는 공유 자원, 경쟁 상태(race condition)가 생기는 세 조건, `Thread.sleep` 으로 틈을 벌려 어긋남 재현하기, `synchronized` 메소드로 한 스레드씩 점유시키기, 락의 주인은 메소드가 아니라 객체(`this`)라는 점, 안전과 속도의 맞바꿈, **스레드 풀** — 과부하 방지와 선입선출 작업 큐, `Executors.newFixedThreadPool` 과 `ThreadPoolExecutor`, `implements Runnable` 작업 객체와 `submit()` 배정, 풀 상태 조회(`getActiveCount`·`getQueue().size()`), `shutdown()` 종료 예약 |

## 주제별 심화

- [[Java 오버로딩 오버라이딩과 인터페이스(이관)]] — 다형성, 컴파일타임 vs 런타임 바인딩

## 스프링 (2026B_Spring)

| 노트 | 핵심 |
| --- | --- |
| [[Java Spring Boot 프로젝트 생성(분석)]] | 스프링 부트 프로젝트의 뼈대 — `src/main`·`src/test` 고정 구조, `build.gradle` 의 플러그인·툴체인·의존성 선언, 스타터(`spring-boot-starter-webmvc`)와 버전 자동 관리, 내장 톰캣과 실행 가능한 jar, 그레이들 래퍼로 빌드 환경 고정, `@SpringBootApplication` 의 세 애노테이션과 컴포넌트 스캔 범위, `SpringApplication.run()` 이 하는 일, `application.properties` 로 설정 분리, `@SpringBootTest` 의 `contextLoads`, 컨트롤러·의존성 주입·빈 스코프와 무상태 설계, 요청이 지나가는 계층 |
| [[Java Spring day01 서블릿과 HTTP 메소드]] | **서블릿** — 자바 클래스에 HTTP를 붙이는 규격과 서블릿 컨테이너(톰캣), `jakarta.servlet` 패키지, `extends HttpServlet` 으로 규격 물려받기, 생명주기 `init`·`service`·`destroy` 와 호출 횟수, `service` 가 `doXXX` 를 갈라 부르는 구조, `doGet`·`doPost`·`doPut`·`doDelete` 와 CRUD 대응, `@WebServlet` 주소 매핑, `HttpServletRequest`·`HttpServletResponse` 로 값을 꺼내고 응답 쓰기, 상태 코드·포워드와 리다이렉트·세션과 스코프·필터, 단일 인스턴스와 멀티스레드 안전성, 프론트 컨트롤러(`DispatcherServlet`)로 이어지는 자리, 안전성과 멱등성 |
| [[Java Spring day02 스프링 부트 실행과 계층 이식]] | **스프링 진입점과 계층 이식, 웹 CRUD 잇기** — 프레임워크와 라이브러리의 차이, 애노테이션이 코드에 의미를 붙이는 방식, `@SpringBootApplication` 의 내장 톰캣 세팅과 컴포넌트 자동 등록, `SpringApplication.run(클래스.class)` 로 시동 걸기와 `ApplicationContext`, 8080 포트와 `localhost`·`127.0.0.1`·포트 충돌, `main` 이 여럿일 때 `build.gradle` 의 `mainClass` 로 진입점 고르기, 패키지로 나눈 Controller·Model(Dao·Dto) 계층, `@Controller`·`@RestController` 의 갈림과 반환값이 데이터로 읽히는 자리·JSON 변환과 getter, HTTP Content-Type, 매핑 애노테이션 넷과 CRUD 짝짓기, 커맨드 객체 바인딩과 값 하나만 받는 매개변수·`@RequestParam`, `BaseDao` 상속으로 JDBC 연동 공통화와 `protected` 접근 범위, `Class.forName` 드라이버 로드, 싱글톤과 `BaseDao` 상속을 겹쳐 쓴 `BoardDao`, `PreparedStatement` 의 `?` 바인딩과 SQL 인젝션·`executeUpdate` 반환값으로 성공·0건 판정, `ResultSet` 커서를 훑어 DTO 목록 만들기, `where` 조건절과 `?` 인덱스 순서, DB 컬럼과 짝을 이루는 DTO와 기본 생성자, `sample.sql` 의 `AUTO_INCREMENT`·`PRIMARY KEY`, 연결 정보를 `application.properties` 로 빼기, `DataSource` 와 커넥션 풀, 스프링 빈과 의존성 주입, `@ResponseBody`·`ResponseEntity`·로거와 예외 처리 모으기, REST 주소 설계와 `@PathVariable`·`@RequestBody`, `fetch`·`curl` 로 요청 보내 보기, Service 계층·`JdbcTemplate`·JPA·트랜잭션으로 이어지는 자리, 같은 구조를 두 번째 도메인(대기명단)에 한 벌 더 쓰면서 표가 늘 때 Dto·Dao·Controller만 늘고 `BaseDao` 는 그대로인 점, `NOT NULL`·`UNIQUE` 제약과 제약 표기 두 가지, DB 컬럼 이름과 자바 필드 이름이 다를 때의 짝짓기와 자바빈 프로퍼티 규약 — 앞 두 글자가 대문자면 그대로 두는 예외와 폼 바인딩·JSON 변환의 이름 규칙이 갈리는 자리, 필드를 `private` 으로 닫아 통로를 하나로 묶기, 대리키와 자연키·`executeUpdate` 가 2 이상을 돌려주는 상황, 컨트롤러가 여럿일 때 주소 충돌과 `@RequestMapping` 공통 앞머리, `resources/static` 에 둔 HTML을 톰캣이 그대로 내보내는 정적 리소스 규칙과 폴더 구조가 곧 주소가 되는 점·`index.html` 기본 문서, 화면 요소(입력칸·표·버튼)와 CRUD 매핑 넷의 대응, 파일로 직접 여는 것과 서버가 내보내는 것의 차이·같은 출처, `fetch` 로 화면과 API 잇기, 정적 파일 주소와 컨트롤러 매핑이 겹칠 때의 우선순위와 `/api` 앞머리, 템플릿 엔진(Thymeleaf)과 서버가 화면을 그리는 방식의 갈림, 화면에 `class`·`id` 식별자와 `onclick` 을 달고 `<script>` 를 body 끝에 두는 이유·CDN과 상대 경로, axios로 HTTP 메소드를 그대로 부르기와 서버 매핑 넷과의 짝, 비동기와 `async`·`await`·Promise, 응답 한 벌과 본문(`.data`)의 갈림·JSON 배열이 자바스크립트 배열로 담기는 자리, `querySelector` 로 자리를 잡고 템플릿 리터럴로 만든 마크업을 한 번에 `innerHTML` 로 넣기, JSON 프로퍼티 이름이 곧 화면 코드의 이름이 되어 DB부터 화면까지 이름 하나가 관통하는 자리, axios와 `fetch` 의 갈림과 실패 응답 처리, 절대주소·상대주소와 출처(origin)·CORS·`@CrossOrigin`, `.value` 로 입력칸 값을 꺼내 쿼리 스트링에 실어 POST·PUT 보내기와 `response.data` 로 `boolean` 판정하기, 성공 후 조회 함수를 재호출해 표만 다시 그리기와 `location.reload()` 의 갈림, `alert`·`confirm`·`prompt` 가 각각 돌려주는 값, 수정 함수가 대상 번호를 매개변수로 받는 구조와 표를 그릴 때 `onclick` 에 값을 박아 잇기, 주소창으로는 못 보내던 PUT을 axios로 보내기, 값을 쿼리 스트링에 실을 때와 요청 본문에 실을 때의 갈림·`encodeURIComponent`·`@RequestBody`, `axios.delete` 로 삭제까지 이어 화면 쪽 CRUD 네 갈래 완성하기·값을 모으는 단계 없이 대상만 넘기는 구조·되돌릴 수 없는 요청 앞의 `confirm`·`boolean` 하나로는 0건과 오류를 갈라 보이지 못하는 자리, 같은 화면 한 벌을 두 번째 도메인에 다시 쓰기 — 화면 파일을 도메인마다 나누기와 폴더 주소로 열리는 `index.html` 의 갈림·함수 이름 앞머리를 도메인으로 나누기와 전역 이름이 겹치는 자리·대상을 `onclick` 으로 넘길 때와 `prompt` 로 물어볼 때의 갈림(대리키와 자연키)·템플릿 리터럴에 문자열 값을 박을 때 따옴표로 감싸기·응답 본문을 직접 열어 JSON 키 확인하기와 값이 `undefined` 로 찍힐 때 보는 순서·`.value` 가 언제나 문자열이라는 점과 요청 파라미터의 타입 변환·`<input type="number">` 로 DB 제약보다 앞에서 막기·도메인이 늘 때 손대는 다섯 파일과 그 되풀이를 줄이는 두 방향 |
| [[Java Spring day03 애노테이션과 리플렉션]] | **애노테이션을 직접 만들고 리플렉션으로 읽어 실행하기** — 애노테이션이 주석과 갈리는 지점(사람이 읽는 메모와 기계가 읽는 표시), `@Override` 로 재정의를 컴파일러에게 검사시키기와 `super` 호출, `@Deprecated` 로 사용 권장하지 않음을 알리기, `@interface` 로 애노테이션 정의하기, 메타 애노테이션 `@Retention` 과 `RetentionPolicy` 세 단계(`SOURCE`·`CLASS`·`RUNTIME`)·실행 중에 읽으려면 `RUNTIME` 이어야 하는 이유, `@Target`·`ElementType` 으로 붙일 자리 제한하기, 애노테이션 속성이 추상메소드 모양인 이유와 `default` 유무로 갈리는 필수·선택·`value` 이름 생략 규칙, 정의한 애노테이션을 메소드에 달기, `클래스.class` 리터럴로 `Class` 얻기와 `getClass()`·`Class.forName()` 과의 갈림, `getMethod` 와 `getDeclaredMethod` 의 범위 차이, `getAnnotation` 으로 표시 읽기와 `null` 이 나올 수 있는 자리·`isAnnotationPresent`, 속성 이름 그대로 값 꺼내기, `getDeclaredConstructor().newInstance()` 로 `new` 없이 객체 만들기와 기본 생성자가 필요한 이유, `method.invoke(대상)` 으로 이름을 박지 않고 메소드 실행하기, `setAccessible` 로 `private` 열기, 리플렉션 예외 계열과 `InvocationTargetException`·`getCause()`, 메소드를 전부 훑어 표시된 것만 실행하기, 정의→주입→읽기 세 단계가 스프링 컴포넌트 스캔·주소 매핑과 같은 구조라는 정리, 합성 애노테이션(`@RestController`=`@Controller`+`@ResponseBody`), AOP와 프록시, 애노테이션 프로세서(Lombok)와 리플렉션의 비용, **롬복으로 남이 만든 애노테이션 가져다 쓰기** — `build.gradle` 의 `compileOnly`·`annotationProcessor` 두 줄과 실행 배포본에서 빠지는 이유, 컴파일 시점에 코드를 생성하는 갈래와 실행 중 리플렉션 갈래의 대비, `@NoArgsConstructor`·`@AllArgsConstructor`·`@RequiredArgsConstructor` 로 생성자 만들기와 전체 생성자를 두면 기본 생성자가 사라지는 자리, `@Getter`·`@Setter`·`@ToString` 과 캡슐화·`toString()` 재정의의 연결, `@Data` 묶음 애노테이션의 구성, `@EqualsAndHashCode` 로 값 기준 비교 만들기와 `equals`·`hashCode` 를 짝으로 두어야 하는 이유, `exclude`·`of` 로 필드 고르기와 순환 참조 주의, 생성된 코드를 확인하는 통로, `@RequiredArgsConstructor` 와 `final` 로 만드는 생성자 주입, **`@Builder` 로 객체 조립하기** — 생성자와 갈리는 지점(순서 무관·선택적 대입·값에 이름이 남는 것)·`builder()` 가 `static` 인 이유·메소드 체이닝과 `build()`·생략한 값이 기본값이 되는 점과 빠뜨려도 컴파일이 막지 않는 약점, **객체를 누가 만드는가** — `new` 로 직접 만들 때 호출마다 객체가 쌓이고 구현 이름이 박히는 문제, 손으로 만드는 싱글톤의 `private` 생성자·`private static final` 인스턴스·`getInstance()` 창구 세 줄과 클래스마다 되풀이되는 부담·이른 초기화와 늦은 초기화의 갈림, `@Component` 로 컨테이너에 빈 자동 등록하기와 표시 한 줄이 세 줄을 대신하는 근거, IOC(제어의 역전)와 DI(의존성 주입)의 갈림·구현을 갈아 끼워도 쓰는 쪽이 그대로인 이유, 빈이 기본적으로 하나로 공유되므로 상태를 담으면 곤란한 자리·빈 스코프와 `@PostConstruct`·`@PreDestroy`·`@Primary`·`@Qualifier`, **앞의 표시들을 실제 요청 처리에 얹기** — day03 패키지에 진입점을 두고 컴포넌트 스캔 범위를 잡기, `@Controller` 가 `@Component` 를 품고 웹 요청 자리를 얹는 구조, `@GetMapping` 으로 주소를 잇기와 `value` 생략 표기, `@ResponseBody` 로 반환값을 본문에 싣기와 뷰 이름으로 읽히는 갈림·`@RestController` 와의 선택 기준, 반환 타입이 Content-Type을 정하는 규칙(`String` 은 `text/plain`·나머지는 JSON), `Map` 을 그대로 JSON으로 내보내기와 `HashMap` 의 순서 문제, `@Data` DTO가 setter로 채워지고 getter로 JSON 키가 정해지는 자리, `@RequestMapping` 으로 주소 묶기·`@RequestParam` 으로 값 받기, `HttpMessageConverter`·Jackson과 `@JsonProperty`·`@JsonIgnore`, **나가는 쪽에서 들어오는 쪽으로** — `@Component`→`@Controller`→`@RestController` 로 겹쳐 올라가는 표시의 계단과 `@RestController` 를 붙이면 `@ResponseBody` 를 생략할 수 있는 자리, `@RequestMapping` 을 클래스에 올려 공통 URL을 한 자리에서 정하기, `@RequestParam` 으로 쿼리스트링·폼 값 받기와 문자열을 매개변수 타입에 맞춰 변환해 주는 자리·표시 생략 조건과 매개변수 이름이 `.class` 에 남지 않을 수 있는 점·`name`·`required`·`defaultValue` 속성과 기본형에 `null` 을 담을 수 없어 생기는 갈림·`defaultValue` 가 문자열인 이유, `@RequestParam Map` 으로 파라미터를 통째로 받기와 값이 전부 문자열로 들어오는 점, `@ModelAttribute` 로 DTO에 담아 받기와 기본 생성자·setter로 채우는 과정이 `newInstance`·`invoke` 와 같은 구조라는 정리, 값을 받는 세 방식의 갈림과 고르는 기준, `@PathVariable` 과 `@RequestParam` 의 갈림(식별자는 주소에·조건은 쿼리스트링에), `@ModelAttribute` 와 `@RequestBody` 가 읽는 곳으로 갈리는 자리, `@DeleteMapping` 등 방식별 매핑과 DELETE에 값을 싣는 방법, `HandlerMethodArgumentResolver` 로 매개변수에 값이 채워지는 실제 자리 |

## 종합

- [[Java day09 MVC 종합예제]] — day01~09의 모든 개념이 하나의 프로젝트로 합쳐지는 지점

## 다른 언어와의 연결

| Java 개념 | 대응하는 JS 개념 |
| --- | --- |
| 정적 타입 | [[JS day03 자료형과 연산자]] 동적 타입 |
| 배열(고정 길이) | [[JS day03 자료형과 연산자]] 배열(가변) |
| 클래스·인스턴스 | [[JS day07 객체]] 객체 리터럴 |
| `Map`·`HashMap` ([[Java day15 Map과 HashMap]]) | [[JS day07 객체]] 객체 `{ }` 와 JSON |
| 메소드 오버로딩 | [[JS day10 함수]] 오버로딩 없음, 기본값 매개변수 |
| 상속·다형성 | [[JS day07 객체]] 프로토타입 체인 |
| `private` + getter/setter | [[JS day10 함수]] 클로저 |
| 콘솔 게시판 | [[JS day14 게시판 CRUD]] localStorage 게시판 |
| MVC 4계층 | [[JS day12 제품 사원 관리 CRUD]] 상태·렌더링 분리 |
| DTO 클래스 | [[SQL day02 테이블과 제약조건]] 테이블 |
| `equals()` 값 비교 / `==` 주소 비교 ([[Java day13 Object 클래스와 리플렉션]]) | [[JS day03 자료형과 연산자]] `==` 느슨한 비교 / `===` 엄격한 비교 |

## 데이터베이스

- [[SQL day01 데이터베이스 기초]]
- [[SQL day02 테이블과 제약조건]]
- [[SQL day03 DML과 조인]]
