---
출처: Claude 분석
작성일: 2026-08-21
tags: [코드정리]
---

# JAVA 날짜와 포맷 심화

> 상위: [[JAVA 예외와 유틸]]

전부 ※. LocalDate 기본 다음 단계 — 시각까지, 원하는 모양으로, 기간 계산.

## LocalDateTime · LocalTime

```java
import java.time.*;

LocalDateTime now = LocalDateTime.now();
LocalTime t = LocalTime.of(14, 30);
LocalDateTime meet = LocalDateTime.of(2026, 8, 21, 14, 30);

now.getYear();  now.getMonthValue();  now.getDayOfMonth();
now.getDayOfWeek();
```

- 날짜만이면 LocalDate, 시각까지면 LocalDateTime, 시각만이면 LocalTime이다
- 전부 불변이라 `plusDays` 등은 **새 객체를 반환**한다. `date.plusDays(7);`만 쓰고 대입을 안 하면 아무 일도 안 일어난다 — 자주 하는 실수

## DateTimeFormatter — 문자열 모양 바꾸기

```java
import java.time.format.DateTimeFormatter;

DateTimeFormatter f = DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm");
String s = LocalDateTime.now().format(f);
LocalDate d = LocalDate.parse("2026/08/21", DateTimeFormatter.ofPattern("yyyy/MM/dd"));
```

- 패턴 문자: `yyyy` 연 `MM` 월 `dd` 일 `HH` 24시 `mm` 분 `ss` 초 `E` 요일
- `format`은 날짜→문자열, `parse`는 문자열→날짜다. 화면 출력용 모양은 전부 여기서 만든다
- 함정: 월은 대문자 `MM`, 분은 소문자 `mm`이다. 바꿔 쓰면 값이 이상해진다

## 기간 계산

```java
import java.time.temporal.ChronoUnit;

long days = ChronoUnit.DAYS.between(start, end);
Period p = Period.between(birth, LocalDate.now());
p.getYears();
Duration dur = Duration.between(t1, t2);
dur.toMinutes();
```

- 날짜 차이는 `ChronoUnit.DAYS.between`이 제일 간단하다(연체일 계산)
- Period는 "몇 년 몇 개월 며칠"(나이 계산), Duration은 "몇 시간 몇 분"(이용 시간)
- 비교는 `isAfter` `isBefore` `isEqual`을 쓴다. `==`는 주소 비교라 안 된다

## DB와의 대응

```
MySQL DATE      ↔  LocalDate      rs.getDate("col").toLocalDate()
MySQL DATETIME  ↔  LocalDateTime  rs.getTimestamp("col").toLocalDateTime()
```

- JDBC로 읽을 때 위 변환 메소드를 거치면 자바 쪽에서는 전부 LocalDate/LocalDateTime로 다룰 수 있다
