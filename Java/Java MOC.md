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
                                                        day13 Object·리플렉션
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
| 13 | [[Java day13 Object 클래스와 리플렉션]] | Object 최상위 클래스, toString·equals·hashCode, 문자열 리터럴 비교, Class·리플렉션, 콘솔 렌더링 |

## 주제별 심화

- [[Java 오버로딩 오버라이딩과 인터페이스(이관)]] — 다형성, 컴파일타임 vs 런타임 바인딩

## 종합

- [[Java day09 MVC 종합예제]] — day01~09의 모든 개념이 하나의 프로젝트로 합쳐지는 지점

## 다른 언어와의 연결

| Java 개념 | 대응하는 JS 개념 |
| --- | --- |
| 정적 타입 | [[JS day03 자료형과 연산자]] 동적 타입 |
| 배열(고정 길이) | [[JS day03 자료형과 연산자]] 배열(가변) |
| 클래스·인스턴스 | [[JS day07 객체]] 객체 리터럴 |
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
