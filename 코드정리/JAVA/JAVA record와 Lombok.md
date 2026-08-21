---
출처: Claude 분석
작성일: 2026-08-21
tags: [코드정리]
---

# JAVA record와 Lombok

> 상위: [[JAVA 클래스 문법]]

전부 ※. DTO의 반복 코드(보일러플레이트)를 없애는 두 가지 방법이다.

## record — 언어 차원의 DTO (Java 16+)

```java
record BookDto(int no, String title, String author) { }

BookDto b = new BookDto(1, "제목", "저자");
int no = b.no();
String t = b.title();
```

- 한 줄로 생성자·getter·equals·hashCode·toString이 전부 생긴다
- getter 이름이 `getNo()`가 아니라 필드명 그대로 `no()`다
- **불변**이라 setter가 없다. 값을 바꾸려면 새로 만든다: `new BookDto(b.no(), "새제목", b.author())`
- 어울리는 자리: 조회 결과 운반, 좌표·기간 같은 값 묶음. 안 어울리는 자리: 단계적으로 값을 채워야 하는 폼 데이터

## Lombok — 어노테이션으로 생성 ※(외부 라이브러리)

```java
@Getter @Setter @ToString
@NoArgsConstructor @AllArgsConstructor
public class BookDto {
    private int no;
    private String title;
    private String author;
}
```

- 컴파일 시점에 getter/setter/toString/생성자 코드를 만들어 넣는다. 클래스가 10개면 수백 줄이 사라진다
- `@NoArgsConstructor` 기본 생성자, `@AllArgsConstructor` 전체 생성자 — DTO 관례 4가지가 어노테이션 5줄로 끝난다
- 라이브러리 설치 + IDE 플러그인이 필요하다. 스프링 실무에서 사실상 표준으로 쓰인다
- `@Builder`를 붙이면 빌더 패턴도 자동 생성된다

## 선택 기준

- 불변이어도 되면 record가 가장 깔끔하다(표준 문법, 설치 불필요)
- setter가 필요하거나 JPA 엔티티처럼 프레임워크가 기본 생성자를 요구하면 class + Lombok
- 수업 범위로 정리하자면: 손으로 짜는 DTO가 기본기, record/Lombok은 그 반복을 자동화한 것뿐이라 구조는 같다
