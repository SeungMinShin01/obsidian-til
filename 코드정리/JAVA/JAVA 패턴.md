---
출처: Claude 분석
작성일: 2026-08-21
tags: [코드정리]
---

# JAVA 패턴

> 상위: [[JAVA]]
> 세부: [[JAVA 빌더 패턴]] · [[JAVA 팩토리 패턴]] · [[JAVA 템플릿 메소드 패턴]] · [[JAVA 옵저버 패턴]]

문법이 아니라 **코드를 조직하는 방법**들이다. 미니프로젝트의 뼈대가 전부 여기서 나온다.

## 싱글톤 — 인스턴스를 하나만

```java
public class BoardDAO {
    private BoardDAO() { }
    private static final BoardDAO instance = new BoardDAO();
    public static BoardDAO getInstance() { return instance; }
}

BoardDAO dao = BoardDAO.getInstance();
```

- 세 줄이 골격이다: `private` 생성자로 외부 `new`를 막고, `static final`로 하나만 미리 만들고, `getInstance()`로 그 하나를 꺼내 쓴다
- 왜: 데이터를 들고 있는 저장소(DAO)를 `new`로 여러 개 만들면 리스트가 갈라져 저장한 글이 사라진 것처럼 보인다. 저장소는 프로그램 전체에 하나여야 한다
- View·Controller·DAO 계층 연결도 전부 `getInstance()`로 잇는다
- 스프링에서는 빈(Bean)이 기본 싱글톤이라 이걸 프레임워크가 대신해 준다

## DTO / VO — 데이터 운반 상자

```java
public class BookDto {
    private int no;
    private String title;

    public BookDto() { }
    public BookDto(int no, String title) {
        this.no = no;
        this.title = title;
    }

    public int getNo() { return no; }
    public void setNo(int no) { this.no = no; }
    public String getTitle() { return title; }
    public void setTitle(String title) { this.title = title; }

    @Override
    public String toString() { return "BookDto [no=" + no + ", title=" + title + "]"; }
}
```

- DTO는 계층 사이에서 데이터를 담아 옮기는 상자다. 저장은 DB(저장소)가 하고, 자바 객체는 나르기만 한다
- 관례 4가지: 필드 전부 private / getter·setter / toString / 기본 + 전체 생성자
- VO는 getter만 두는 읽기 전용 버전이다(생성자로만 값을 넣는다)
- DB 테이블 한 행 = DTO 한 개. 테이블 설계가 곧 DTO 설계다

## DAO — 저장·조회 전담 계층

```java
public class BookDao {
    private ArrayList<BookDto> list = new ArrayList<>();

    public boolean save(BookDto dto) {
        list.add(dto);
        return true;
    }

    public ArrayList<BookDto> findAll() {
        return new ArrayList<>(list);
    }

    public BookDto findByNo(int no) {
        for (BookDto b : list) {
            if (b.getNo() == no) return b;
        }
        return null;
    }
}
```

- 데이터가 어디에 어떻게 저장되는지는 DAO만 안다. 지금 ArrayList여도 나중에 MySQL로 바꾸면 **DAO만 고치고** View·Controller는 그대로다
- 메소드 이름 관례: `save` 저장, `findAll` 전체 조회, `findByNo` 조건 조회, `update` 수정, `delete` 삭제 — 세 계층에 같은 이름을 나란히 만든다
- "찾기(공통) → 작업(개별)"로 나누면 검색 로직이 한 곳에만 있게 된다(`findByNo`를 update·delete가 재사용)

## MVC 흐름 — View · Controller · DAO · DTO

```
AppStart(main)
   ↓
View        입력받기 → DTO로 포장 → Controller에 요청 → 응답 출력
   ↓ DTO
Controller  유효성 검사·업무 규칙 → DAO에 요청 → 결과 반환
   ↓ DTO
DAO         저장·조회 (ArrayList 또는 DB)
```

- View는 데이터를 직접 만지지 않고, DAO는 화면을 모른다. 각자 한 가지 책임만 진다(단일 책임 원칙)
- View의 표준 4단계: ①입력받기 ②객체화(DTO) ③Controller에 요청·응답 ④응답 처리(출력)
- 검증은 여러 겹으로 둔다: View는 입력 형식(숫자인가), Controller는 업무 규칙(재고가 있는가), DB 제약조건이 최후의 방어선
- main이 하는 일은 `View.getInstance().run();` 한 줄이다

## 전략 교체 — 타입은 규격으로, 실체는 갈아끼우기

```java
interface Tire { void roll(); }

class Car {
    Tire tire;
    void run() { tire.roll(); }
}

Car car = new Car();
car.tire = new HankookTire();
car.run();
car.tire = new KumhoTire();
car.run();
```

- Car는 Tire(규격)만 알고 어떤 타이어인지 모른다. 그래서 구현체를 바꿔도 Car는 한 글자도 안 바뀐다
- 설계 순서: ①규격(인터페이스) 먼저 → ②구현체 → ③쓰는 쪽은 규격 타입으로만 받는다
- DAO에 그대로 적용된다: `DataAccessObject dao = new MySqlDao();` 한 줄만 바꾸면 저장소가 교체된다
- 이 구조를 데이터 계층에 끝까지 밀어붙인 것이 Repository Pattern이다(최상위에 별도 분석 노트가 있다 — 링크는 걸지 않는다)

## 방어적 복사 — 내부 데이터 지키기

```java
public ArrayList<BookDto> findAll() {
    return new ArrayList<>(list);
}
```

- 내부 리스트를 그대로 반환하면 받은 쪽이 `clear()` 한 번으로 DAO의 데이터를 통째로 지울 수 있다
- 복사본을 만들어 돌려주면 밖에서 무슨 짓을 해도 원본이 안전하다. 캡슐화의 마지막 조각이다

## static 카운터 — 자동 번호

```java
class Post {
    static int seq = 0;
    int no;

    Post() {
        this.no = ++seq;
    }
}
```

- 인스턴스가 만들어질 때마다 클래스 공유 변수 `seq`가 1씩 늘어 고유 번호가 붙는다
- SQL의 `AUTO_INCREMENT`를 자바로 흉내 낸 것이다. DB로 넘어가면 이 역할을 DB가 대신한다

