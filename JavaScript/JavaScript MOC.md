---
출처: Claude 분석
작성일: 2026-08-10
tags: [허브, javascript]
---

# JavaScript MOC

JavaScript 관련 노트의 허브입니다. 상위 지도는 [[KDT_2026 학습 지도]].
실제 프로젝트에서 이 주제가 쓰인 지점은 [[KDT_2026 학습 지도]]의 **프로젝트 매핑표**에서 찾습니다 (프로젝트 분석 노트와 직접 링크하지 않습니다).

## 프로젝트 매핑 — 학습 지도 ↔ 이 폴더

[[KDT_2026 학습 지도]]를 거쳐 들어온 경우, 프로젝트의 해당 주제는 이 노트들과 닿습니다. (프로젝트 쪽은 평문 — 직접 링크하지 않음)

| 프로젝트에서 만난 것 | 이 폴더의 이론 |
| --- | --- |
| 커스텀 훅 — 클로저로 상태 가두기 | [[JS day10 함수]] |
| 낙관적 업데이트 — 스프레드·불변·참조 | [[JS day07 객체]] |
| localStorage 세션·추천 캐시, 인터벌 캐러셀 | [[JS day13 웹 스토리지와 인터벌]] |
| 목록·폼 CRUD 화면 구조 | [[JS day12 제품 사원 관리 CRUD]] · [[JS day14 게시판 CRUD]] |
| DOM 렌더링·이벤트 | [[JS day11 DOM 조작]] |


## 학습 순서 (day별)

```
day02 변수·입출력 ─→ day03 자료형·연산자 ─→ day04 조건문 ─→ day05 반복문
                                                                │
                                                                ▼
day14 게시판 CRUD ←─ day13 웹스토리지 ←─ day12 CRUD ←─ day11 DOM ←─ day10 함수 ←─ day07 객체
```

| day | 노트 | 핵심 |
| --- | --- | --- |
| 02 | [[JS day02 변수와 입출력]] | 변수·상수, 출력·입력 함수, HTML과 JS 연결 |
| 03 | [[JS day03 자료형과 연산자]] | 자료형 6종, 배열, 형변환, 연산자 7종 |
| 04 | [[JS day04 조건문]] | if 6가지 패턴, 삼항, 분기 설계 |
| 05 | [[JS day05 반복문]] | for·중첩·break·continue, 배열 순회 |
| 07 | [[JS day07 객체]] | 객체 리터럴, Object 메소드, 중첩 |
| 10 | [[JS day10 함수]] | 함수 4조합, 매개변수·반환값, 스코프 |
| 11 | [[JS day11 DOM 조작]] | querySelector, innerHTML·value·style |
| 12 | [[JS day12 제품 사원 관리 CRUD]] | 데이터 모델링, 정규화, CRUD 4함수 |
| 13 | [[JS day13 웹 스토리지와 인터벌]] | localStorage, 쿼리스트링, setInterval |
| 14 | [[JS day14 게시판 CRUD]] | write/list/view/update 4화면 완성 |
| 과제 | [[JS 과제 LevelUP과 게시판]] | 모델링·삼항·틱택토·조인, Message_Board |

## 주제별 심화

- [[C와 JS 문자 카운트 문제(이관)]] — switch, 문자 순회, 카운트 패턴

## 함께 쓰는 언어

- HTML MOC — JS가 조작할 대상
- CSS MOC — `classList`, `style`로 JS가 바꾸는 것

## Java와의 대응

| JS 개념 | Java 대응 |
| --- | --- |
| 동적 타입 | Java day01 자바 구조와 자료형 정적 타입 |
| 가변 배열 | Java day04 제어문과 배열 고정 배열 / Java day09 ArrayList |
| 객체 리터럴 | Java day05 클래스와 인스턴스 클래스·인스턴스 |
| 오버로딩 없음 | Java day07 메소드와 미니프로젝트 메소드 오버로딩 |
| 클로저 | Java day08 접근제한자와 static private + getter |
| localStorage 게시판 | Java day06 생성자와 콘솔 게시판 배열 게시판 |
