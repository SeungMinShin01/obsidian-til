---
출처: Claude 분석
원본: KDT_2026/2026B_BE/src/day11/종합예제
작성일: 2026-08-13
tags: [학습, java]
---

# Java day11 — 종합예제 (인터페이스 DAO)

> 실습 파일: `day11/종합예제/` (AppStart, MainView, BoardController·ProductController, BoardDao·ProductDao·IBaseDao, BoardDto·ProductDto·BaseTime)
> 허브: [[Java MOC]] · 이전: [[Java day11 인터페이스]] · 다음: [[Java day12 예외 처리와 JDBC]]

[[Java day09 MVC 종합예제]] 의 구조를 그대로 가져오되, DAO를 **인터페이스로 규격화**한 버전이다. day11에서 배운 인터페이스가 실제 4계층 프로젝트의 어디에 꽂히는지가 이 예제의 핵심이다.

## 1. 배운 내용

### 1-1. 구조 한눈에

```
AppStart → MainView (View)
              ├─ BoardController → BoardDao ─┐
              └─ ProductController → ProductDao ┤ implements
                                              IBaseDao (규격)
DTO: BoardDto / ProductDto ─ extends ─ BaseTime
```

게시물·제품이라는 서로 다른 두 도메인을 **같은 규격(IBaseDao)** 아래 나란히 두었다. day09가 하나의 도메인(게시판)이었다면, day11 종합예제는 규격 하나로 여러 도메인을 관리하는 그림이다.

### 1-2. IBaseDao — 저장소 규격

```java
public interface IBaseDao<T> {
    String DB_URL = "jdbc:mysql://localhost:3306/mydb";  // 자동 public static final
    String DB_ID  = "root";
    String DB_PW  = "****";   // 실습용 로컬 계정 (노트에는 값 생략)

    boolean save(Object obj);
    ArrayList<Object> findAll();
}
```

- 저장소가 갖춰야 할 두 가지 행위 `save`, `findAll` 만 규격으로 정한다 — [[Java day11 인터페이스]] 의 "규격 먼저" 설계 그대로다
- 필드는 전부 상수(`public static final`)라 **DB 연동 정보(URL·계정)를 규격에 상수로 얹어 두었다.** 지금은 메모리(ArrayList)에 저장하지만, 이 상수는 [[Java day12 예외 처리와 JDBC]] 에서 실제 DB로 갈아끼울 때 쓰려고 미리 심어 둔 자리다
- 선언은 제네릭 `<T>` 이지만 본체에서는 `Object` 로 받는다. 규격만 잡아 두고 타입은 아직 느슨하게 둔 단계다 (2-1에서 조이는 법을 정리한다)

### 1-3. DAO — 규격을 구현하고 목록을 품는다

```java
public class BoardDao implements IBaseDao {
    private BoardDao() { }                                  // 싱글톤
    private static final BoardDao instance = new BoardDao();
    public static BoardDao getInstance() { return instance; }

    private ArrayList<Object> boardList = new ArrayList<>();

    @Override public boolean save(Object obj) { boardList.add(obj); return true; }
    @Override public ArrayList<Object> findAll() { return boardList; }
}
```

- `implements` 한 순간 `save`·`findAll` 을 **전부 오버라이딩해야** 오류가 사라진다 — 구현은 필수라는 인터페이스의 성질
- 실제 데이터(목록)는 규격이 아니라 구현 클래스가 자기 멤버변수로 들고 있다. 규격은 행위, 상태는 구현체 — [[Java day11 인터페이스]] 2-3의 원칙 그대로다
- ProductDao 도 형태가 똑같다. 저장하는 리스트 이름만 다르고 규격은 공유한다

### 1-4. 싱글톤을 전 계층에 적용

View·Controller·DAO **모두** `private 생성자 + static instance + getInstance()` 형태다.

```java
private static final MainView instance = new MainView();
public static MainView getInstance() { return instance; }
```

계층마다 인스턴스가 하나만 존재하도록 고정한다. Controller가 여러 번 new 되어 저장소가 갈라지는 사고를 막는 구조로, [[Java day09 MVC 종합예제]] 에서 익힌 싱글톤을 계층 전체로 넓힌 셈이다.

### 1-5. Controller — 규격 타입으로 DAO를 받는다

```java
public class BoardController {
    private IBaseDao ib = BoardDao.getInstance();   // 업캐스팅: 구현체를 규격 타입에 담음

    public boolean save(BoardDto boardDto) {
        return ib.save(boardDto);
    }

    public ArrayList<BoardDto> findAll() {
        ArrayList<Object> b1 = ib.findAll();
        ArrayList<BoardDto> result = new ArrayList<>();
        for (Object b2 : b1) {
            result.add((BoardDto) b2);              // 다운캐스팅: Object → BoardDto
        }
        return result;
    }
}
```

- Controller는 `BoardDao` 라는 **구현체 이름 대신 `IBaseDao` 규격 타입**으로 저장소를 참조한다. 저장소를 다른 구현으로 갈아끼워도 이 코드는 안 바뀐다
- DAO가 `Object` 로 저장·반환하므로, 꺼낼 때 `(BoardDto)` 로 **다운캐스팅**해 원래 타입을 복원한다. [[Java day10 상속과 다형성]] 의 업·다운캐스팅이 여기서 실제로 쓰인다

### 1-6. DTO — 공통 필드를 부모로 뽑기 (BaseTime)

```java
public class BaseTime {
    private String cdate;
    public BaseTime() {
        this.cdate = LocalDate.now().format(DateTimeFormatter.ofPattern("yyyy-MM-dd"));
    }
    public String getCdate() { return cdate; }
}

public class BoardDto extends BaseTime {   // 생성일(cdate)을 물려받는다
    private String content;
    private String writer;
    public BoardDto(String content, String writer) {
        super();                            // BaseTime() 호출 → cdate 자동 세팅
        this.content = content; this.writer = writer;
    }
}
```

- 게시물·제품이 공통으로 갖는 **생성일(cdate)** 을 `BaseTime` 부모로 올렸다. 두 DTO 모두 `extends BaseTime` 이라 `super()` 만 부르면 오늘 날짜가 자동으로 들어간다
- 중복 필드를 부모로 끌어올리는 것이 상속의 실무 용도 그대로다 — [[Java day10 상속과 다형성]] 에서 배운 상속이 "코드 재사용"으로 쓰이는 지점
- `LocalDate.now().format(DateTimeFormatter.ofPattern("yyyy-MM-dd"))` 로 날짜를 문자열로 포맷한다

## 2. 추가로 알면 좋은 활용법

### 2-1. 제네릭을 제대로 쓰면 캐스팅이 사라진다

지금은 `IBaseDao<T>` 로 선언만 제네릭이고 실제로는 `Object` 로 주고받아 Controller마다 다운캐스팅 반복이 생긴다. 타입 매개변수를 끝까지 쓰면 캐스팅을 없앨 수 있다.

```java
public interface IBaseDao<T> {
    boolean save(T obj);
    ArrayList<T> findAll();
}
public class BoardDao implements IBaseDao<BoardDto> {
    public boolean save(BoardDto obj) { ... }
    public ArrayList<BoardDto> findAll() { ... }   // 꺼낼 때 캐스팅 불필요
}
```

[[Java day09 ArrayList]] 에서 본 `ArrayList<String>` 의 제네릭이 규격 설계에도 그대로 쓰인다. 규격에 타입을 흘려보내면 쓰는 쪽이 안전해진다.

### 2-2. 규격 타입으로 받으면 교체가 자유롭다

`private IBaseDao ib = BoardDao.getInstance();` 에서 오른쪽만 바꾸면 저장 방식이 통째로 바뀐다. 예를 들어 `BoardDaoDB.getInstance()` (JDBC로 DB에 저장하는 구현)로 바꿔도 Controller·View는 손대지 않는다. 이게 [[Repository Pattern]] 이 노리는 "쓰는 쪽과 저장 방식의 분리"다.

### 2-3. Object로 받는 저장소의 한계

`Object` 로 저장하면 아무 타입이나 들어갈 수 있어 편하지만, 꺼낼 때 잘못된 타입으로 캐스팅하면 실행 중에야 오류가 드러난다. 컴파일 시점에 타입을 지키게 하려면 2-1의 제네릭이 답이다. "무엇이든 담기는 상자"는 그만큼 실수를 늦게 알려 준다.

## 3. 더 나아가 알면 좋은 것

### 3-1. 다음 단계 — 규격은 그대로, 저장을 DB로

IBaseDao에 심어 둔 `DB_URL`·`DB_ID`·`DB_PW` 상수가 예고하는 방향이다. `save()` 안을 `boardList.add(...)` 에서 **JDBC로 INSERT** 하는 코드로 바꾸면, 규격(IBaseDao)과 쓰는 쪽(Controller)은 그대로 두고 저장 위치만 메모리 → MySQL로 옮길 수 있다. 그 JDBC 연동의 첫걸음이 [[Java day12 예외 처리와 JDBC]] 다.

### 3-2. 공통 로직은 추상클래스로도 뽑을 수 있다

BoardDao·ProductDao의 `save`·`findAll` 본문이 거의 같다. 공통 부분을 추상클래스로 뽑고 달라지는 부분만 남기면 중복이 줄어든다. 순수 규격은 인터페이스, 공통 구현까지 물려주려면 추상클래스 — [[Java day11 인터페이스]] 3-1의 선택 기준이 그대로 적용된다.

### 3-3. 다음에 볼 키워드

- 제네릭 바운디드 타입 `<T extends BaseTime>`
- `abstract class` 로 공통 DAO 만들기
- JDBC `Connection`·`Statement`·`ResultSet` (전부 인터페이스)
- Spring Data JPA의 `Repository` 인터페이스 — 이 구조의 완성형

## 실습 파일

- `2026B_BE/src/day11/종합예제/AppStart.java` (진입점)
- `2026B_BE/src/day11/종합예제/view/MainView.java` (View, 메뉴 루프)
- `2026B_BE/src/day11/종합예제/controller/BoardController.java` · `ProductController.java`
- `2026B_BE/src/day11/종합예제/model/dao/IBaseDao.java` · `BoardDao.java` · `ProductDao.java`
- `2026B_BE/src/day11/종합예제/model/dto/BaseTime.java` · `BoardDto.java` · `ProductDto.java`

## 관련 노트

[[Java MOC]] · [[Java day11 인터페이스]] · [[Java day12 예외 처리와 JDBC]] · [[Java day09 MVC 종합예제]] · [[Java day10 상속과 다형성]] · [[Java day09 ArrayList]] · [[Repository Pattern]] · [[KDT_2026 학습 지도]]
