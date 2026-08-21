---
출처: Claude 분석
작성일: 2026-08-21
tags: [코드정리]
---

# JAVA Queue와 스택

> 상위: [[JAVA 컬렉션]]

전부 ※. "먼저 온 순서대로"와 "나중 것부터"라는 두 가지 대기 구조다.

## Queue — 선입선출 (FIFO)

```java
import java.util.ArrayDeque;
import java.util.Queue;

Queue<String> q = new ArrayDeque<>();
q.offer("손님1");
q.offer("손님2");
String next = q.poll();
String peek = q.peek();
```

- `offer` 뒤에 넣기, `poll` 앞에서 빼기(비었으면 null), `peek` 빼지 않고 보기
- 대기명단·주문 처리 순서가 정확히 이 구조다. 리스트로 하면 앞에서 빼기가 O(n)인데 큐는 O(1)이다

## 스택 — 후입선출 (LIFO)

```java
import java.util.ArrayDeque;

ArrayDeque<String> stack = new ArrayDeque<>();
stack.push("페이지1");
stack.push("페이지2");
String top = stack.pop();
```

- `push` 위에 쌓기, `pop` 맨 위 꺼내기, `peek` 보기만
- 뒤로 가기·실행 취소(undo)·괄호 짝 검사가 스택이다. 옛날 클래스 `Stack` 대신 `ArrayDeque`를 쓰는 게 표준이다

## PriorityQueue — 우선순위 큐

```java
import java.util.PriorityQueue;

PriorityQueue<Integer> pq = new PriorityQueue<>();
pq.offer(30); pq.offer(10); pq.offer(20);
pq.poll();

PriorityQueue<Book> exp = new PriorityQueue<>(Comparator.comparing(Book::getPrice).reversed());
```

- 넣는 순서와 무관하게 `poll`이 항상 **가장 작은 것**(또는 Comparator 기준 1순위)을 준다
- "다음 처리할 것 = 항상 최우선인 것"인 문제(응급실 순번, 마감 임박순)에 쓴다
