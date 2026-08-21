---
출처: Claude 분석
작성일: 2026-08-21
tags: [코드정리]
---

# JAVA 입력 심화

> 상위: [[JAVA 기본 문법]]

전부 ※(수업 밖). Scanner가 느리거나 불편해지는 지점의 대안이다.

## BufferedReader — 빠른 입력

```java
import java.io.*;

BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
String line = br.readLine();
int n = Integer.parseInt(br.readLine());
```

- Scanner는 내부에서 정규식 파싱을 해서 느리다. 코딩테스트 시간 초과의 단골 원인이고, 입력이 수만 줄이면 BufferedReader로 바꾼다
- `readLine()`은 항상 문자열 한 줄을 준다. 숫자는 `parseInt`로 직접 바꾼다
- `IOException`을 던지므로 main에 `throws IOException`을 붙이거나 try-catch로 감싼다

## 한 줄에 여러 값 — split과 StringTokenizer

```java
String[] parts = br.readLine().split(" ");
int a = Integer.parseInt(parts[0]);
int b = Integer.parseInt(parts[1]);

StringTokenizer st = new StringTokenizer(br.readLine());
int x = Integer.parseInt(st.nextToken());
int y = Integer.parseInt(st.nextToken());
```

- "3 5"처럼 공백으로 붙어 오는 입력은 `split(" ")`으로 잘라 배열로 받는다
- StringTokenizer는 split보다 빠른 자르기다. `nextToken()`을 부를 때마다 다음 조각이 나온다
- 얻는 효과: 입력 형태(한 줄 통째)와 파싱(자르기·변환)을 분리해서 어떤 입력 형식이 와도 같은 방식으로 대응한다

## 입력 끝까지 읽기

```java
String line;
while ((line = br.readLine()) != null) {
    // 처리
}
```

- 입력 개수를 미리 알려주지 않는 문제의 관용구다. 더 읽을 게 없으면 `readLine()`이 null을 준다
- 대입과 검사를 한 줄에 쓴 `(line = br.readLine()) != null` 형태 자체가 자주 보이는 함축 표현이다
