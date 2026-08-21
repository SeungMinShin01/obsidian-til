---
출처: Claude 분석
작성일: 2026-08-21
tags: [코드정리]
---

# JAVA 정규표현식

> 상위: [[JAVA 배열과 String]]

전부 ※. 문자열의 "모양"을 검사·치환하는 미니 언어다. 입력 검증에서 바로 쓴다.

## String 메소드로 쓰기

```java
boolean ok = "010-1234-5678".matches("\\d{3}-\\d{4}-\\d{4}");
String digits = s.replaceAll("[^0-9]", "");
String[] parts = s.split("\\s+");
```

- `matches(패턴)`은 문자열 **전체**가 패턴과 일치하는지 boolean으로 준다
- `replaceAll(패턴, 대체)`은 패턴에 걸리는 부분을 전부 바꾼다. `[^0-9]`(숫자가 아닌 것) 제거는 전화번호 정리의 관용구다
- `split("\\s+")`은 공백 1개 이상 기준으로 자른다. 자바 문자열 안에서는 `\d`를 `\\d`로 쓴다(백슬래시 이스케이프)

## 자주 쓰는 패턴 조각

```
\d        숫자 하나            [0-9]와 같음
\w        영문·숫자·_ 하나
\s        공백 하나
.         아무 문자 하나
X*  X+  X?   0개 이상 / 1개 이상 / 0 또는 1개
X{3}  X{2,4}  정확히 3개 / 2~4개
[abc]  [^abc]  a,b,c 중 하나 / 그것들 빼고
^  $      문자열의 시작 / 끝
A|B       A 또는 B
```

- 검증 예: 아이디 `"^[a-z0-9]{4,12}$"`, 숫자만 `"\\d+"`, 이메일 간이형 `"[\\w.]+@[\\w.]+\\.[a-z]+"`

## Pattern · Matcher — 부분 찾기

```java
import java.util.regex.*;

Pattern p = Pattern.compile("\\d+");
Matcher m = p.matcher("가격은 4500원, 할인 500원");
while (m.find()) {
    System.out.println(m.group());
}
```

- `matches`가 전체 일치라면, `find()`는 문자열 **안에서** 패턴을 하나씩 찾아 전진한다. 찾은 조각은 `group()`으로 꺼낸다
- 같은 패턴을 반복 사용할 땐 `Pattern.compile`로 한 번 만들어 재사용하는 편이 빠르다
