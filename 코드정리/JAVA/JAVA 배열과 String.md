---
출처: Claude 분석
작성일: 2026-08-21
tags: [코드정리]
---

# JAVA 배열과 String

> 상위: [[JAVA]]

## 배열

```java
int[] arr = new int[3];
String[] names = {"유재석", "강호동", "신동엽"};

arr[0] = 10;
int len = arr.length;
```

- 동일 타입만, 고정 길이, 요소는 자동 초기화된다(정수 0, 실수 0.0, boolean false, 참조 null)
- 기존 요소 수정은 되지만 추가·삭제는 안 된다. 가변이 필요하면 ArrayList로 간다
- `length`는 필드라 괄호가 없다(문자열의 `length()`는 메소드)
- 배열을 그대로 출력하면 주소가 나온다. 내용은 `Arrays.toString(arr)`로 본다
- 인덱스 접근이 O(1)인 이유: 첫 칸 주소 하나만 들고 "타입 크기 × 인덱스"로 계산해 이동하기 때문이다

### 배열 문제의 4가지 기본형

```java
int sum = 0;
for (int i = 0; i < arr.length; i++) sum += arr[i];

int max = arr[0];
for (int i = 1; i < arr.length; i++) if (max < arr[i]) max = arr[i];

int count = 0;
for (int i = 0; i < types.length; i++) if (types[i].equals("A")) count++;

for (int i = 0; i < arr.length; i++) if (arr[i] == 100) { found = true; break; }
```

- 누적(sum)·최댓값(max)·계수(count)·탐색(break) — 대부분의 배열 문제가 이 넷의 조합이다
- 누적 변수는 반복문 밖에 선언하고, 최댓값 초기값은 0이 아니라 **배열의 첫 원소**로 둔다(음수만 있을 때 대비)
- 평균 낼 때 `(double)` 캐스팅을 빼면 정수 나눗셈으로 소수점이 잘린다

## Arrays 유틸

```java
import java.util.Arrays;

Arrays.toString(arr);
Arrays.sort(arr);
Arrays.fill(arr, 0);
int[] copy = Arrays.copyOf(arr, 5);
Arrays.equals(a, b);
```

- `toString` 내용 출력, `sort` 오름차순 정렬, `fill` 전체 채우기
- `copyOf`는 크기를 바꿔 복사한다 — 고정 길이 한계를 우회하는 방법이고, ArrayList가 내부에서 하는 일이 이것이다
- 배열 내용 비교는 `==`(주소)가 아니라 `Arrays.equals`다
- 2차원 배열은 `int[][] g = new int[3][4];`, 출력은 `Arrays.deepToString(g)`

## String 메소드

```java
s.length();
s.equals(other);
s.equalsIgnoreCase(other);
s.charAt(0);
s.substring(1, 4);
s.indexOf("a");
s.contains("ab");
s.split(",");
s.trim();
s.replace("a", "b");
s.toUpperCase();
s.isEmpty();
s.isBlank();
```

- `length()` 길이, `charAt(i)` i번째 문자, `substring(1, 4)`는 1 이상 4 미만 구간이다
- 값 비교는 `equals`, 대소문자 무시 비교는 `equalsIgnoreCase`다. `==`는 주소 비교라 절대 쓰지 않는다
- `indexOf`는 위치를 주고 없으면 -1, `contains`는 포함 여부를 boolean으로 준다
- `split(",")`은 구분자로 잘라 배열로 만든다. CSV 한 줄을 컬럼으로 나눌 때 쓴다
- `trim`/`strip`은 앞뒤 공백 제거다. 입력값 검증 전에 습관처럼 붙인다
- `isEmpty`는 길이 0, `isBlank`는 공백뿐인지까지 본다. 검증에는 `isBlank`가 더 안전하다

## 문자열 ↔ 숫자 변환

```java
int n = Integer.parseInt("10");
double d = Double.parseDouble("3.14");
String s = String.valueOf(10);
String t = String.format("%d점", 90);
```

- `parseInt`는 문자열→정수다. 숫자가 아닌 문자열이 들어오면 `NumberFormatException`이 난다
- 반대 방향(숫자→문자열)은 `String.valueOf`, 서식까지 입히려면 `String.format`이다

## StringBuilder ※

```java
StringBuilder sb = new StringBuilder();
sb.append("A").append("B").append(1);
String result = sb.toString();
```

- 문자열 `+=` 누적은 반복마다 새 문자열을 만들어 느리다. 반복이 많으면 StringBuilder에 `append`로 쌓고 마지막에 `toString()` 한 번으로 뽑는다
- `append`가 자기 자신을 반환해서 점을 이어 붙이는 체인이 가능하다

## 관련 노트

[[JAVA]]
