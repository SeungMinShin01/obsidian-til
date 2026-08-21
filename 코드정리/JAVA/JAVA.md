---
출처: Claude 분석
작성일: 2026-08-21
tags: [코드정리]
---

# JAVA

> 상위: [[코드정리]]
> 세부: [[JAVA 기본 문법]] · [[JAVA 배열과 String]] · [[JAVA 클래스 문법]] · [[JAVA 상속과 인터페이스]] · [[JAVA 컬렉션]] · [[JAVA 예외와 유틸]] · [[JAVA JDBC]] · [[JAVA 패턴]] · [[JAVA AI 관용구]]

코드정리 JAVA 트리의 루트. 아래는 **수업(day01~12)에서 배운 코드 전체**를 한 줄 주석으로 모은 것이다. 원리·심화는 세부 노트로.

## day01 — 구조·출력·입력

```java
package day01;                                   // 패키지(폴더) 선언
public class Exam1 {                             // 클래스 = 파일명, 대문자 시작
    public static void main(String[] args) { }   // 실행 진입점 (메인 스레드)
}
System.out.println("안녕");                       // 출력 + 줄바꿈
System.out.print("안녕");                         // 출력 (줄바꿈 없음)
System.out.printf("%s %d %f %b", s, i, d, b);    // 서식 출력: 문자열 정수 실수 논리
System.out.printf("%6d %-6d %06d %5.2f %,d");    // 오른정렬 왼정렬 0채움 소수2자리 콤마
"\n \t \' \" \\"                                 // 이스케이프: 줄바꿈 탭 따옴표 역슬래시

import java.util.Scanner;                        // 입력 클래스 가져오기
Scanner scanner = new Scanner(System.in);        // 입력 객체 생성 (new = 인스턴스화)
String str = scanner.next();                     // 공백·엔터 전까지 한 단어
String line = scanner.nextLine();                // 한 줄 전체
int i = scanner.nextInt();                       // 정수
double d = scanner.nextDouble();                 // 실수
boolean b = scanner.nextBoolean();               // 논리값
char c = scanner.next().charAt(0);               // 문자 1개
scanner.nextLine();                              // nextInt 뒤 남은 엔터 비우기
```

## day01~02 — 자료형·타입 변환

```java
boolean b = true;                                // 1byte 참/거짓
char c = 'A';                                    // 2byte 문자 1개 (유니코드)
String s = "유재석";                              // 참조 타입 (주소 저장)
byte by = 100;                                   // 1byte 정수 (-128~127)
short sh = 30000;                                // 2byte 정수
int i = 2000000000;                              // 4byte 정수 (리터럴 기본)
long l = 20000000000L;                           // 8byte 정수 (L 필수)
float f = 0.123F;                                // 4byte 실수 (F 필수)
double d = 0.123;                                // 8byte 실수 (리터럴 기본)

int a = (int) 3.9;                               // 강제 변환(캐스팅) → 3 (버림)
double d2 = 5;                                   // 자동 변환 (작은 → 큰)
byte b2 = (byte) 130;                            // 범위 초과 시 값이 잘림
double avg = (double) sum / count;               // 정수 나눗셈 방지 캐스팅
int n = Integer.parseInt("10");                  // 문자열 → 정수
String s2 = String.valueOf(10);                  // 정수 → 문자열
```

## day03 — 연산자

```java
+ - * / %                                        // 산술 (/는 정수끼리면 몫, %는 나머지)
= += -= *= /= %=                                 // 대입·복합대입 (+=는 캐스팅 포함)
++x  x++  --x  x--                               // 증감 (전위: 먼저 증가, 후위: 쓰고 증가)
> < >= <= == !=                                  // 비교 (참조 타입 ==는 주소 비교)
&& || !                                          // 논리 (단축 평가: 앞이 결정하면 뒤 생략)
조건 ? 참값 : 거짓값                                // 삼항 연산자
int max = n1 > n2 ? n1 : n2;                     // 최댓값 한 줄
"admin".equals(id)                               // 문자열 값 비교 (Yoda: null 안전)
if (str != null && str.length() > 0) { }         // null 검사를 앞에 (단축 평가 활용)
n % 2 == 0                                       // 짝수 판별
sec / 60, sec % 60                               // 분·초 분리
```

## day04 — 제어문·배열

```java
if (온도 <= 10) { }                               // 조건문 (실행문 1개면 {} 생략 가능)
else if (온도 <= 30) { }                          // 계단은 좁은 조건부터
else { }

switch (grade) {                                 // switch: byte short char int String enum
    case 'A': System.out.println("A"); break;    // break 없으면 아래로 흘러내림
    default: break;                              // 어느 case도 아닐 때
}

for (int i = 1; i <= 10; i++) { }                // 초기값 → 조건 → 실행 → 증감
while (i <= 10) { i++; }                         // 조건 반복
for (;;) { }                                     // 무한루프
break;                                           // 가장 가까운 반복 탈출
continue;                                        // 증감식으로 건너뛰기
for (int 단 = 2; 단 <= 9; 단++)                   // 중첩 반복 (바깥=줄)
    for (int 곱 = 1; 곱 <= 9; 곱++) { }           // (안쪽=칸) 구구단
for (int data : ary) { }                         // 향상된 for: 요소를 하나씩

int[] arr1 = new int[3];                         // 크기 지정 (자동 초기화: 0/0.0/false/null)
String[] arr2 = {"유재석", "강호동"};              // 초기값 지정
arr2[0] = "수정";                                 // 요소 수정 (추가·삭제는 불가)
arr1.length                                      // 개수 (필드, 괄호 없음)
System.out.println(Arrays.toString(arr1));       // 배열 내용 출력 (그냥 찍으면 주소)
for (int i = 0; i < arr.length; i++) { }         // 순회 조건은 < length (<=는 항상 에러)

int sum = 0;                                     // 누적: 반복 밖에 변수
for (...) sum += arr[i];                         // 합계 패턴
int max = arr[0];                                // 최댓값: 첫 원소로 시작
if (max < arr[i]) max = arr[i];                  // 갱신 패턴
if (types[i].equals("A")) count++;               // 계수 패턴
if (arr[i] == 100) { found = true; break; }      // 탐색 + 조기 종료 패턴
```

## day05~06 — 클래스·생성자

```java
class Student {                                  // 설계 클래스 (상태 + 행위)
    int studentId;                               // 멤버변수 (인스턴스 변수)
    String studentName;
}
Student s1 = new Student();                      // 인스턴스 생성 (힙 할당)
s1.studentName = "유재석";                        // 도트(.)로 멤버 접근
Student s4 = s2;                                 // 주소 복사 (같은 객체를 봄)
System.out.println(s1);                          // 클래스명@해시코드 (주소)

class Phone {
    String model; String color; int price;
    Phone() { }                                  // 기본 생성자
    Phone(String model, String color) {          // 정의 생성자
        this.model = model;                      // this = 이 인스턴스의 멤버변수
        this.color = color;
    }
    Phone(String m, String c, int p) { }         // 생성자 오버로딩 (개수/타입/순서 다르게)
}
// 정의 생성자를 만들면 기본 생성자는 자동 생성 안 됨 — 필요하면 직접 선언
Book b1 = new Book("제목", "저자", 30000);        // 만들면서 한 번에 초기화

Post[] posts = new Post[100];                    // 객체 배열 (전부 null로 시작)
if (posts[index] == null) {                      // 빈 칸 찾기
    posts[index] = post; break;                  // 첫 빈 칸에 저장 (break 필수)
}
for (Post p : posts) if (p != null) { }          // null 아닌 것만 출력
```

## day07 — 메소드

```java
반환타입 메소드명(타입 매개변수) { return 값; }      // 메소드 기본 꼴

double getPi() { return 3.14; }                  // 매개변수 X, 반환 O
void powerOn() { return; }                       // void: 반환 없음 (return;은 즉시 종료)
void printSum(int x, int y) { }                  // 매개변수 O, 반환 X
int add(int x, int y) { return x + y; }          // 매개변수 O, 반환 O
this.printSum(x, y);                             // 같은 클래스의 다른 메소드 호출
boolean isEven(int n) { return n % 2 == 0; }     // boolean 반환 → if 조건에 바로
boolean sell(int qty) { return stock >= qty; }   // 동작 시도 결과 반환 → 호출부가 분기

int add(int x, int y) { }                        // 오버로딩: 같은 이름,
double add(double x, double y) { }               // 매개변수만 다르게
int add(int x, int y, int z) { }                 // (반환타입만 다른 건 불가)
```

## day08 — 접근제한자·static

```java
public    // 전체 공개
protected // 같은 패키지 + 자식
(생략)     // 같은 패키지 (default)
private   // 같은 클래스만

class User {
    private String name;                         // 필드는 private (직접 접근 차단)
    public void setName(String name) {           // setter = 검증 관문
        if (name.length() < 1) return;           // 유효성 검사 후 조기 반환
        this.name = name;
    }
    public String getName() { return name; }     // getter
    @Override
    public String toString() { return "..."; }   // println이 자동으로 부름
}
// DTO 관례: ①전부 private ②getter/setter ③toString ④기본+전체 생성자
// VO = getter만 (읽기 전용)

public final int 고정변수 = 3;                     // final: 재할당 불가 (초기값 필수)
public static int 정적변수 = 10;                   // static: 클래스에 1개, 클래스명으로 접근
public static final int 상수 = 30;                // 상수 (관례상 대문자)
D.정적변수 = 20;                                   // 인스턴스 없이 접근
static int seq = 0;                              // 공유 카운터
this.no = ++seq;                                 // 자동 번호 (AUTO_INCREMENT 흉내)
```

## day09 — ArrayList·MVC

```java
import java.util.ArrayList;
ArrayList<String> list = new ArrayList<>();      // 가변 리스트 (제네릭 = 요소 타입)
ArrayList<Integer> nums;                         // 기본 타입 불가 → 래퍼 클래스
list.add("유재석");                                // 끝에 추가
list.add(1, "하하");                              // 중간 삽입 (뒤로 밀림, 크기 +1)
list.set(1, "서장훈");                             // 수정 (크기 그대로)
list.get(1);                                     // 조회
list.remove(1);                                  // 인덱스 삭제
list.size();                                     // 개수 (메소드)
list.indexOf("강호동");                            // 위치 (없으면 -1)
list.contains("값");                              // 포함 여부
list.clear();                                    // 전체 삭제
list.isEmpty();                                  // 비었는지
ArrayList<Book> books = new ArrayList<>();       // 내 클래스 담기 (실전형)
for (Book b : books) System.out.println(b);      // toString 있으면 바로 읽힘

// MVC: View(입출력) → Controller(검증·중계) → DAO(저장·조회), DTO(운반)
BoardView.getInstance().run();                   // main은 한 줄
private BoardView() { }                          // 싱글톤 ①: 외부 생성 차단
private static final BoardView instance = new BoardView();  // ②: 하나만 생성
public static BoardView getInstance() { return instance; }  // ③: 그 하나 반환
private BoardController bc = BoardController.getInstance(); // 계층 연결도 싱글톤
BoardDto dto = new BoardDto(내용, 작성자);         // View: 입력 → DTO 포장
boolean result = bc.save(dto);                   // Controller에 요청·응답
ArrayList<BoardDto> all = bd.findAll();          // DAO: 데이터 반환
```

## day10 — 상속·다형성

```java
class 조류 extends 동물 { }                        // 상속 (하위 extends 상위, 1개만)
bird1.show();                                    // 부모의 멤버를 그대로 사용
// 자식 생성 시 부모부터 생성: 참새 = 동물 → 조류 → 참새

조류 bird2 = sparrow1;                            // 업캐스팅 (자동): 부모 타입에 자식
참새 s2 = (참새) animal2;                          // 다운캐스팅 (강제, 타입 명시)
// 부모로 태어난 객체는 자식으로 못 내려감 → ClassCastException
e instanceof C                                   // 타입 포함 확인 (조상 전부 true)
if (animal instanceof 참새) { 참새 s = (참새) animal; }  // 확인 후 변환이 안전

@Override                                        // 재정의 표식 (오타 방지 검사)
void show() { System.out.println("재정의"); }      // 오버라이딩: 선언부 동일하게 재정의
super();                                         // 부모 생성자 호출 (첫 줄만, 생략 시 자동)
super(name);                                     // 부모에 기본 생성자 없으면 직접 호출
super.show();                                    // 부모 메소드 실행 후 덧붙이기
obj3.show();                                     // 타입이 부모여도 실제 객체의 메소드 실행
// 멤버변수는 반대: 변수 타입을 따라감 (오버라이딩은 메소드만)

class Car { Tire tire; void run() { tire.roll(); } }  // 조합 (has-a)
myCar.tire = new HankookTire();                  // 구현체 교체
myCar.run();                                     // Car 코드는 그대로 (다형성의 실익)
```

## day11 — 인터페이스

```java
public interface KeyBoard {
    public static final String info = "인텔";     // 필드는 전부 상수 (생략해도 자동)
    public abstract void aKey();                 // 추상메소드 (생략해도 자동)
    int bkey(int x);                             // 선언부만, 구현부 없음
}
class SportsGame implements KeyBoard {           // 구현 (오버라이딩 필수)
    public void aKey() { System.out.println("슈팅"); }
    public int bkey(int x) { return x; }
}
KeyBoard myBoard = new SportsGame();             // 인터페이스 타입 업캐스팅
myBoard = new ActionGame();                      // 구현체 갈아끼우기 (같은 aKey, 다른 동작)
// new KeyBoard() 불가 — 생성자 없음

public default void method2() { }                // 디폴트: 구현부 있음, 재정의 선택
public static void method3() { }                 // 정적: Buy.method3()로 직접 호출
private void method4() { }                       // 비공개: 내부 공통 코드
class Customer implements Buy, Sell { }          // 다중 구현 (전부의 추상메소드 구현)
interface CustomerController extends Buy, Sell { }  // 인터페이스끼리 다중 상속

myCar.tire = new Tire() {                        // 익명 구현체: 일회용 구현
    @Override public void roll() { }             // 그 자리에서 추상메소드 채움
};
interface IBaseDao<T> {                          // 제네릭 인터페이스 (종합예제)
    boolean save(T dto);                         // DAO 공통 규격
    ArrayList<T> findAll();
}
```

## day12 — 예외 처리·JDBC

```java
try {
    int r = 10 / n;                              // 위험한 코드
} catch (ArithmeticException e) {                // 예외 종류별로 잡기
    System.out.println(e.getMessage());          // 예외 메시지
} finally { }                                    // 성공/실패 무관 항상 실행
throw new IllegalArgumentException("잘못된 값");   // 예외 직접 던지기

import java.sql.*;
String url = "jdbc:mysql://localhost:3306/mydb"; // jdbc:mysql://호스트:포트/DB명
try (Connection con = DriverManager.getConnection(url, user, pw);  // 연결 (자동 close)
     PreparedStatement ps = con.prepareStatement(
         "INSERT INTO board(content, writer) VALUES(?, ?)")) {  // ?로 값 자리
    ps.setString(1, dto.getContent());           // ? 채우기 (순번 1부터)
    ps.setString(2, dto.getWriter());
    return ps.executeUpdate() == 1;              // INSERT/UPDATE/DELETE → 바뀐 행 수
}
try (ResultSet rs = ps.executeQuery()) {         // SELECT → 결과 표(커서)
    while (rs.next()) {                          // 다음 행으로 (있으면 true)
        list.add(new BoardDto(
            rs.getInt("no"),                     // 현재 행의 컬럼 값 꺼내기
            rs.getString("content")));           // 한 행 = DTO 한 개
    }
}
```

## 자주 쓰는 코드 ※ (수업 밖 — 위와 중복 없음)

### String 메소드

```java
s.length()                                       // 길이 (배열은 .length 필드)
s.substring(1, 4)                                // 부분 문자열 [1, 4)
s.contains("검색어")                              // 포함 여부
s.split(",")                                     // 구분자로 잘라 배열
s.trim()                                         // 앞뒤 공백 제거
s.isBlank()                                      // 비었거나 공백뿐인지
s.replace("a", "b")                              // 치환
s.toUpperCase()  s.toLowerCase()                 // 대소문자
s.startsWith("http")  s.endsWith(".png")         // 시작·끝 검사
String.join(", ", list)                          // 리스트 → "a, b, c"
String.format("%d점", 90)                        // 서식 문자열 만들기
StringBuilder sb = new StringBuilder();          // 반복 이어붙이기 전용
sb.append("a").append(1); sb.toString();         // 쌓고 마지막에 뽑기
```

### Map·Set·정렬

```java
Map<Integer, BookDto> map = new HashMap<>();     // 키-값 (번호로 찾기 O(1))
map.put(no, dto);  map.get(no);                  // 저장·조회
map.getOrDefault(key, 0)                         // 없으면 기본값 (카운팅)
map.containsKey(no)                              // 키 존재 확인
for (Map.Entry<Integer, BookDto> e : map.entrySet()) { }  // 키+값 순회
Set<String> set = new HashSet<>(list);           // 중복 제거
set.contains("값")                                // 있나 확인
list.removeIf(b -> b.getNo() == no);             // 조건 삭제 (순회중 remove 대체)
Collections.sort(list);                          // 오름차순
list.sort(Comparator.comparing(BookDto::getNo).reversed());  // 필드 기준 역순
List<String> menu = List.of("a", "b");           // 즉석 불변 리스트 (수정 불가)
```

### 숫자·날짜·기타

```java
Math.max(a, b);  Math.min(a, b);  Math.abs(x);   // 큰값·작은값·절댓값
int dice = (int) (Math.random() * 6) + 1;        // 1~6 랜덤
LocalDate today = LocalDate.now();               // 오늘
LocalDate due = today.plusDays(14);              // 14일 뒤 (반납예정일)
today.isAfter(due)                               // 날짜 비교
long over = ChronoUnit.DAYS.between(due, today); // 날짜 차이 (연체일)
Objects.equals(a, b)                             // null 안전 비교
var list = new ArrayList<BookDto>();             // 지역변수 타입 추론
throw new IllegalStateException("재고 없음");      // 상태 오류 던지기
```
