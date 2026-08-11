---
출처: Claude 분석
원본: KDT_2026/2026B_BE/src/day09/종합예제, src/Note/Java.txt
작성일: 2026-08-10
tags: [java, day09, MVC, DTO, DAO, 싱글톤, 프로젝트]
---

# Java day09 — MVC 종합예제

> 실습 파일: `day09/종합예제/AppStart.java`, `view/BoardView.java`, `controller/BoardController.java`, `dao/BoardDAO.java`, `dto/BoardDto.java`, `Note/Java.txt`
> 허브: [[Java MOC]] · 함께 보기: [[Java day09 ArrayList]] · [[Java day08 접근제한자와 static]]

day01부터 배운 것들이 **하나의 프로젝트로 합쳐지는 지점**입니다. 클래스·생성자·메소드·캡슐화·static·ArrayList가 전부 여기서 동시에 쓰입니다.

## 1. 배운 내용

### 1-1. MVC 패턴 — Note/Java.txt

정리하면 이렇습니다.

| 항목 | 내용 |
| --- | --- |
| 정의 | 세 가지 주요 역할을 분리해 코드를 모듈화하는 디자인 패턴 |
| 목적 | 협업 시 코드와 파일을 규칙에 따라 구성해 효율성을 높임 |
| 장점 | 유지보수, 모듈화, **단일 책임 원칙(SRP)** — 객체지향 5대 원칙(SOLID) 중 하나 |
| 단점 | 분리함에 따라 관리 복잡도가 높아짐 |

**비유로 보면 이렇습니다.**
> - 1인 식당: 사장님이 혼자서 서빙하고 요리하고 재료 준비한다.
> - 직원이 있는 식당: 서빙직원, 요리직원, 재료관리직원이 각 역할을 담당한다 — 단일 책임 원칙

### 1-2. 계층과 이동객체

| 계층 | 담당 | 기술 |
| --- | --- | --- |
| **VIEW** | 입출력 | HTML/CSS/JS/React/Flutter |
| **CONTROLLER** | model과 view 사이의 제어·로직·유효성검사·전달 | Java/Python/Node.js |
| **MODEL** | 데이터 관리 | Java/Python/Node.js |

| 이동객체 | 구성 |
| --- | --- |
| **DTO** | 계층 간 데이터 객체, **setter + getter** 지원 |
| **VO** | 계층 간 데이터 객체, **getter만** 지원 |

**흐름**
```
게시물쓰기:  view <--DTO--> controller <--DTO--> DAO/REPOSITORY <--> 데이터베이스(SQL)
게시물조회:  view <--DTO--> controller <--DTO--> DAO/REPOSITORY <--> 데이터베이스(SQL)
```

**패키지 구성**
```
프로젝트폴더
├── controller 폴더
├── view 폴더
├── model 폴더
│   ├── dao 폴더
│   └── dto 폴더
└── AppStart 클래스
```

### 1-3. 실제 구조

```
day09/종합예제/
├── AppStart.java              진입점
├── view/BoardView.java        입출력
├── controller/BoardController.java   중계·검증
├── dao/BoardDAO.java          데이터 저장·조회
└── dto/BoardDto.java          계층 간 데이터 운반
```

```
AppStart
   ↓ run
BoardView      ── 입력받기, 출력하기
   ↓ BoardDto
BoardController ── 유효성검사, 전달
   ↓ BoardDto
BoardDAO       ── ArrayList에 저장/조회
```

### 1-4. AppStart — 진입점

```java
package day09.종합예제;

import day09.종합예제.view.BoardView;

public class AppStart {
    public static void main(String[] args) {
        // 최초로 실행할 화면view 요청한다.
        BoardView.getInstance().run();
    }
}
```

`main`이 하는 일이 **딱 한 줄**입니다. 실행 진입점과 실제 로직을 분리한 형태입니다.

### 1-5. BoardDto — 데이터 운반 객체

```java
public class BoardDto {
    // 1. 데이터베이스 표에서 (CRUD) 사용할 자료들을 private 멤버변수로 구성
    private String content;
    private String writer;

    // 2. 기본생성자, 전체매개변수생성자
    public BoardDto() { }
    public BoardDto(String content, String writer) {
        this.content = content;
        this.writer = writer;
    }

    // 3. setter and getter, toString
    public String getContent() { return content; }
    public void setContent(String content) { this.content = content; }
    public String getWriter() { return writer; }
    public void setWriter(String writer) { this.writer = writer; }

    @Override
    public String toString() {
        return "BoardDto [content=" + content + ", writer=" + writer + "]";
    }
}
```

[[Java day08 접근제한자와 static]] 에서 정리한 **DTO 관례 4가지가 그대로** 구현되어 있습니다.

1. 멤버변수 전부 `private`
2. getter/setter 제공
3. `toString()` 제공
4. 기본생성자 + 전체매개변수생성자

주석의 한 줄이 DTO의 본질을 정확히 짚습니다.
> DTO: 데이터 이동객체. **자바는 저장소가 아니다.** 즉 데이터베이스(저장소)가 저장소.

DTO는 데이터를 **담아 옮기는 상자**일 뿐, 저장하는 곳이 아닙니다.

### 1-6. 싱글톤 — 세 클래스 모두 동일

```java
public class BoardView {
    private BoardView() { }                                  // 1. 외부 생성 차단
    private static final BoardView instance = new BoardView(); // 2. 하나만 미리 생성
    public static BoardView getInstance() { return instance; } // 3. 그 하나를 반환
}
```

`BoardView`, `BoardController`, `BoardDAO` 셋 다 같은 구조입니다.

**왜 싱글톤인가**: `BoardDAO`가 데이터(`boardList`)를 들고 있습니다. `new BoardDAO()`를 여러 번 하면 리스트가 여러 개 생겨서 저장한 글이 사라진 것처럼 보입니다. **저장소는 프로그램 전체에 하나여야** 합니다.

[[Java day08 접근제한자와 static]] 의 `private` 생성자 + `static` 필드 조합이 여기서 실제 목적을 갖고 쓰입니다.

**계층 간 연결도 싱글톤으로**
```java
private BoardController bc = BoardController.getInstance();   // View 안에서
private BoardDAO bd = BoardDAO.getInstance();                 // Controller 안에서
```

### 1-7. BoardView — 입출력만

```java
private Scanner scan = new Scanner(System.in);   // 모든 메소드에서 사용 가능한 입력 객체

public void index() {
    while (true) {
        System.out.print("1. 등록 2.전체조회: ");
        int ch = scan.nextInt();
        if (ch == 1) save();
        else if (ch == 2) findAll();
    }
}

public void save() {
    System.out.print("내용: ");
    String 내용 = scan.next();          // 1. 입력받기
    System.out.print("작성자 : ");
    String 작성자 = scan.next();

    BoardDto boardDto = new BoardDto(내용, 작성자);   // 2. 객체화

    boolean result = bc.save(boardDto);              // 3. 컨트롤러에게 요청·응답
    if (result) System.out.println("등록성공");       // 4. 응답 처리
    else System.out.println("등록실패");
}

public void findAll() {
    ArrayList<BoardDto> result = bc.findAll();       // 1. 컨트롤러에게 요청
    for (BoardDto board : result) {                  // 2. 출력
        System.out.println(board.getWriter() + " : " + board.getContent());
    }
}
```

주석의 **1 입력받기 → 2 객체화 → 3 요청·응답 → 4 응답 처리** 4단계가 View의 표준 흐름입니다.

**View는 데이터를 직접 만지지 않습니다.** 리스트도 없고 저장 로직도 없습니다. 입력받아 DTO로 포장해 넘기고, 받아온 것을 화면에 뿌릴 뿐입니다.

`Scanner`를 필드로 선언해 모든 메소드가 공유하는 것도 좋은 처리입니다. 메소드마다 `new Scanner`를 만들면 입력 버퍼가 꼬입니다.

### 1-8. BoardController — 중계

```java
public boolean save(BoardDto boardDto) {
    // 1. view로부터 저장할 정보 객체로 받는다.
    // * 유효성검사 / 타입 변환 등등
    // 2. DAO 에게 요청하고 응답받기
    boolean result = bd.save(boardDto);
    // 3. DAO 에게 받은 결과를 VIEW에게 응답하기
    return result;
}

public ArrayList<BoardDto> findAll() {
    ArrayList<BoardDto> result = bd.findAll();
    return result;
}
```

지금은 그냥 넘기기만 하지만, **주석에 적어둔 "유효성검사 / 타입 변환"이 들어갈 자리**를 정확히 표시해 두셨습니다. 컨트롤러의 실제 역할이 그것입니다.

### 1-9. BoardDAO — 데이터

```java
// * 데이터베이스 대신에 ArrayList 사용하여 데이터베이스 표/데이터 역할 *
// * 추후에 MYSQL 서버와 연동
private ArrayList<BoardDto> boardList = new ArrayList<>();

public boolean save(BoardDto boardDto) {
    // * 추후에 insert 이용한 db에 저장
    boardList.add(boardDto);
    return true;
}

public ArrayList<BoardDto> findAll() {
    // * 추후에 select 이용한 db 조회
    return boardList;
}
```

**주석의 "추후에"가 정확한 로드맵입니다.**

| 지금 | 나중 |
| --- | --- |
| `boardList.add(dto)` | `INSERT INTO board ...` |
| `return boardList` | `SELECT * FROM board` |
| `ArrayList` | MySQL 테이블 |

**DAO만 바꾸면 View와 Controller는 그대로입니다.** 이게 계층을 나누는 가장 큰 실익입니다. → [[SQL day03 DML과 조인]]

`ArrayList<BoardDto>` — 제네릭에 내가 만든 클래스를 넣는 형태입니다. → [[Java day09 ArrayList]]

## 2. 추가로 알면 좋은 활용법

### 2-1. day06 게시판과 비교

[[Java day06 생성자와 콘솔 게시판]] 의 `OverallController`와 같은 기능인데 구조가 완전히 다릅니다.

| | day06 OverallController | day09 종합예제 |
| --- | --- | --- |
| 파일 수 | 1개 | 5개 |
| 저장소 | `Post[100]` 배열 | `ArrayList<BoardDto>` |
| 빈 칸 찾기 | `null` 탐색 루프 | 불필요 |
| 계층 | 없음 (main 안에 전부) | View / Controller / DAO / DTO |
| 필드 접근 | `post.writer` 직접 | `dto.getWriter()` |
| 인스턴스 | 필요할 때마다 `new` | 싱글톤 1개 |
| DB 전환 | 전체를 다시 써야 함 | **DAO만 교체** |

같은 게시판을 만드는 데 파일이 5배로 늘었습니다. **작은 프로그램에는 과한 구조**이지만, 기능이 20개로 늘어나는 순간 역전됩니다. "분리함에 따라 관리 복잡도가 높아진다"는 단점이 드러나는 지점입니다.

### 2-2. 메소드 이름을 맞추기

```java
BoardView.getInstance()        // AppStart에서 호출
public static BoardView getinstance()   // BoardView의 선언
```

`getInstance`와 `getinstance`처럼 대소문자가 다르면 서로 다른 메소드입니다. 자바는 **대소문자를 구분**합니다.

세 클래스가 같은 역할을 하므로 이름을 **`getInstance`로 통일**해두면 헷갈리지 않습니다. 카멜 표기법 기준으로도 `getInstance`가 맞습니다.

같은 맥락으로 `AppStart`가 `run()`을 부르고 `BoardView`에는 `index()`가 있다면, 둘 중 하나로 이름을 맞춰야 연결됩니다.

### 2-3. CRUD를 마저 채우기

지금은 C(등록)와 R(전체조회)만 있습니다. 계층 구조가 잡혀 있으니 추가가 쉽습니다.

```java
// DTO에 식별자 추가
private int no;

// DAO
public BoardDto findByNo(int no) {
    for (BoardDto b : boardList) {
        if (b.getNo() == no) return b;
    }
    return null;
}

public boolean delete(int no) {
    return boardList.removeIf(b -> b.getNo() == no);
}

public boolean update(int no, String newContent) {
    BoardDto target = findByNo(no);
    if (target == null) return false;
    target.setContent(newContent);
    return true;
}
```

**세 계층에 같은 이름의 메소드를 나란히** 만들면 됩니다.
```
BoardView.delete()  →  BoardController.delete()  →  BoardDAO.delete()
```

`removeIf`는 [[Java day09 ArrayList]] 참고. 번호 자동 증가는 [[Java day08 접근제한자와 static]] 의 static 카운터로 만듭니다.

### 2-4. Controller에 유효성검사 넣기

주석으로 자리만 잡아둔 부분을 채우면 컨트롤러가 제 역할을 합니다.

```java
public boolean save(BoardDto boardDto) {
    if (boardDto.getContent() == null || boardDto.getContent().isBlank()) return false;
    if (boardDto.getWriter() == null || boardDto.getWriter().isBlank()) return false;
    if (boardDto.getContent().length() > 500) return false;
    return bd.save(boardDto);
}
```

**검증을 어디에 둘지**가 설계 판단입니다.

| 위치 | 성격 |
| --- | --- |
| View | 입력 형식 (숫자인가, 빈칸인가) |
| **Controller** | 업무 규칙 (500자 이하, 금지어) |
| DTO setter | 객체 자체의 불변 조건 |
| DB 제약조건 | 최후의 방어선 (`NOT NULL`, `UNIQUE`) |

여러 겹으로 두는 게 정석입니다. → [[SQL day02 테이블과 제약조건]]

### 2-5. 무한 루프에 종료 메뉴

```java
while (true) {
    System.out.print("1. 등록 2.전체조회 0.종료: ");
    int ch = scan.nextInt();
    if (ch == 0) { System.out.println("종료합니다."); break; }
    else if (ch == 1) save();
    else if (ch == 2) findAll();
    else System.out.println("잘못된 선택입니다.");
}
```

`else`까지 두면 예상 못 한 입력에도 안내가 나갑니다.

### 2-6. `findAll()`이 내부 리스트를 그대로 반환합니다

```java
public ArrayList<BoardDto> findAll() {
    return boardList;   // 내부 리스트 자체
}
```

받은 쪽에서 `result.clear()`를 하면 DAO의 데이터가 통째로 사라집니다.

```java
public ArrayList<BoardDto> findAll() {
    return new ArrayList<>(boardList);   // 방어적 복사
}
```

[[Java day08 접근제한자와 static]] 의 캡슐화가 깨지는 사례와 같습니다. 학습 단계에서는 그대로 반환해도 되지만, 계층을 나눈 목적이 "각 계층이 자기 데이터를 지키는 것"이라는 점에서는 복사본이 맞습니다.

## 3. 더 나아가 알면 좋은 것

### 3-1. DAO를 인터페이스로

```java
public interface BoardRepository {
    boolean save(BoardDto dto);
    ArrayList<BoardDto> findAll();
}

public class MemoryBoardDAO implements BoardRepository { ... }
public class MySqlBoardDAO implements BoardRepository { ... }
```

컨트롤러는 `BoardRepository` 타입만 알면 되므로, **메모리 저장 → DB 저장으로 갈아탈 때 컨트롤러를 한 줄도 안 고쳐도 됩니다.**

```java
private BoardRepository bd = new MySqlBoardDAO();   // 이 한 줄만 교체
```

→ [[Java 오버로딩 오버라이딩과 인터페이스(이관)]]

### 3-2. JDBC 연결

```java
public boolean save(BoardDto dto) {
    String sql = "INSERT INTO board(content, writer) VALUES(?, ?)";
    try (Connection con = DriverManager.getConnection(url, id, pw);
         PreparedStatement ps = con.prepareStatement(sql)) {
        ps.setString(1, dto.getContent());
        ps.setString(2, dto.getWriter());
        return ps.executeUpdate() == 1;
    } catch (SQLException e) {
        return false;
    }
}

public ArrayList<BoardDto> findAll() {
    ArrayList<BoardDto> list = new ArrayList<>();
    String sql = "SELECT content, writer FROM board";
    try (Connection con = DriverManager.getConnection(url, id, pw);
         PreparedStatement ps = con.prepareStatement(sql);
         ResultSet rs = ps.executeQuery()) {
        while (rs.next()) {
            list.add(new BoardDto(rs.getString("content"), rs.getString("writer")));
        }
    } catch (SQLException e) { }
    return list;
}
```

`ResultSet` 한 행이 `BoardDto` 한 개가 됩니다. **DTO가 테이블 한 행의 자바 표현**이라는 게 여기서 눈으로 보입니다.

`PreparedStatement`는 SQL 인젝션 방어에 필수입니다. → [[SQL day03 DML과 조인]]

### 3-3. Spring Boot로 가면

이 구조가 그대로 이름만 바뀝니다.

| 지금 | Spring Boot |
| --- | --- |
| `AppStart` | `@SpringBootApplication` |
| `BoardView` | `@RestController` (또는 React 화면) |
| `BoardController` | `@Service` |
| `BoardDAO` | `@Repository` / `JpaRepository` |
| `BoardDto` | `@Entity` + DTO |
| 싱글톤 직접 구현 | 스프링이 자동으로 관리 (기본이 싱글톤) |
| `getInstance()` | `@Autowired` 의존성 주입 |

**지금 손으로 만든 싱글톤과 계층 분리를 스프링이 대신해 줍니다.** 직접 만들어본 경험이 있어야 프레임워크가 무엇을 해주는지 이해됩니다.

### 3-4. 프론트엔드 게시판과 나란히

| | JS ([[JS day14 게시판 CRUD]]) | Java (이 노트) |
| --- | --- | --- |
| 화면 | HTML 5개 | `BoardView` 콘솔 |
| 로직 | 각 `.js` 파일 | `BoardController` |
| 저장 | `localStorage` | `BoardDAO` + `ArrayList` |
| 데이터 | 객체 `{ title, content }` | `BoardDto` |
| 계층 분리 | `common.js`로 추출 제안 | 이미 4계층 |

프론트에서 "localStorage 코드를 `common.js`로 빼자"고 한 것이 백엔드에서는 **DAO 분리**입니다. 같은 문제의식이 양쪽에서 나옵니다.

## 4. 두 번째 구현 — WaitingList (대기명단)

같은 4계층 구조를 처음부터 다시 만든 두 번째 앱입니다. 게시판이 아니라 **식당 대기명단**(전화번호 + 인원수)을 CRUD합니다. `AppStart2.java`가 진입점.

```
WaitingView → WaitingController → WaitingDao → ArrayList<WaitingDto>
```

구조는 Board와 같고, 다른 지점들이 오히려 공부거리입니다.

### 4-1. 자연키 검색 — isPnumber

게시판은 번호(연번)로 글을 찾았지만, 대기명단은 **전화번호**로 사람을 찾습니다.

```java
// WaitingDao — 전화번호로 인덱스를 찾고, 없으면 -1
public int isPnumber(WaitingDto waitingDto) {
    for (int i = 0; i < waitingList.size(); i++) {
        if (waitingList.get(i).getpNumber().equals(waitingDto.getpNumber()))
            return i;
    }
    return -1;
}
```

전화번호처럼 데이터가 원래 갖고 있는 식별값을 **자연키**, 시스템이 붙이는 연번을 **대리키**라고 합니다. "없으면 -1" 관례는 [[Java day06 생성자와 콘솔 게시판]] 의 빈 칸 표시, JS의 `indexOf`와 같은 발상입니다.

수정·삭제가 이 메소드를 공유합니다.

```java
// WaitingController — 찾기와 실행을 분리하고 삼항 연산자로 접기
int isNum = wd.isPnumber(waitingDto);
boolean result = isNum == -1 ? false : wd.update(waitingDto, isNum);
```

"대상 찾기(공통) → 작업 실행(개별)"로 나눈 덕에 검색 로직이 한 곳에만 있습니다.

### 4-2. 용도별 생성자 — 오버로딩의 실전 사용

```java
public WaitingDto(String pNumber, int hCount) { ... }  // 등록용 — 전부 필요
public WaitingDto(String pNumber) { ... }              // 삭제용 — 전화번호만 필요
```

삭제할 때는 인원수가 필요 없으니 전화번호만 받는 생성자를 따로 뒀습니다. [[Java day07 메소드와 미니프로젝트]] 에서 배운 오버로딩이 "용도에 맞는 최소 입력"이라는 목적으로 쓰인 예입니다.

### 4-3. Board와 나란히 보기

| | Board | Waiting |
| --- | --- | --- |
| 식별 | 인덱스(연번) | 전화번호(자연키) |
| 수정/삭제 대상 찾기 | 번호 직접 사용 | `isPnumber()` 검색 → 인덱스 |
| DTO 생성자 | 풀 생성자 | 등록용 + 삭제용 오버로딩 |
| 싱글톤·계층 | 동일 | 동일 |

같은 뼈대에 다른 도메인을 얹어보면 **어디까지가 패턴(반복)이고 어디부터가 도메인(개별)인지** 경계가 보입니다. 싱글톤·계층 연결은 그대로 복사되고, 식별 방식과 DTO 설계만 바뀌었습니다 — 다음에 세 번째 앱을 만들면 이 반복 부분이 지겨워질 텐데, 그 지겨움이 프레임워크(3-3의 Spring)가 존재하는 이유입니다.

## 실습 파일

- `2026B_BE/src/Note/Java.txt` (자바 전 과정 종합 정리)
- `2026B_BE/src/day09/종합예제/AppStart.java` · `AppStart2.java`
- `2026B_BE/src/day09/종합예제/view/BoardView.java` · `WaitingView.java`
- `2026B_BE/src/day09/종합예제/controller/BoardController.java` · `WaitingController.java`
- `2026B_BE/src/day09/종합예제/dao/BoardDAO.java` · `WaitingDao.java`
- `2026B_BE/src/day09/종합예제/dto/BoardDto.java` · `WaitingDto.java`

## 관련 노트

[[Java MOC]] · [[Java day09 ArrayList]] · [[Java day08 접근제한자와 static]] · [[Java day06 생성자와 콘솔 게시판]] · [[Java day07 메소드와 미니프로젝트]] · [[Java 오버로딩 오버라이딩과 인터페이스(이관)]] · [[JS day14 게시판 CRUD]] · [[SQL day03 DML과 조인]]
