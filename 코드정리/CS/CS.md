---
출처: Claude 분석
작성일: 2026-08-21
tags: [코드정리]
---

# CS

> 상위: [[코드정리]]
> 세부: [[CS 자료구조]] · [[CS 쓰레드와 동시성]] · [[CS 네트워크 기초]]

코드를 "돌아가게" 만드는 지식이 아니라, **왜 그렇게 돌아가는지**의 지식이다. AI가 코드를 다 짜주는 시대일수록 면접관이 확인하는 건 이쪽이다 — "이 코드가 왜 느린가", "동시에 두 명이 누르면 어떻게 되나", "브라우저에서 서버까지 무슨 일이 일어나나"에 답할 수 있는가. 전부 ※.

## 이 트리를 읽는 법

- 각 노트는 개념 → 코드에서 만나는 자리 → **면접 단골 질문** 순서다
- 외우기보다 "내 프로젝트의 어디에 이게 있었지"를 연결하는 게 기억에 남는다 — 게시판·대여 시스템의 코드가 전부 예시 재료다

## 자주 쓰는 코드 모음

```java
Thread t = new Thread(() -> job());              // 스레드 생성 (람다)
t.start();                                       // 실행 (run() 직접 호출 금지)
t.join();                                        // 끝날 때까지 대기
public synchronized void increase() { count++; } // 한 번에 한 스레드만
AtomicInteger count = new AtomicInteger();       // 락 없는 안전 카운터
count.incrementAndGet();                         // 원자적 +1
Map<Integer, Dto> m = new ConcurrentHashMap<>(); // 스레드 안전 Map
ExecutorService pool = Executors.newFixedThreadPool(10);  // 스레드 풀
```

```
자료구조 선택 한 줄:
  인덱스 접근 → ArrayList | 키 조회 → HashMap | 중복 제거 → HashSet
  순서 처리 → ArrayDeque(큐) | 되돌리기 → ArrayDeque(스택) | 정렬 유지 → TreeMap

복잡도 감각: O(1) 해시 | O(log n) 이진탐색·인덱스 | O(n) 한 바퀴 | O(n²) 이중 for = 위험

상태코드: 200 성공 | 201 생성 | 304 캐시 | 400 요청이상 | 401 미인증 | 403 권한없음
          404 없음 | 409 충돌 | 500 서버에러

메소드 = CRUD: GET 조회 | POST 생성 | PUT/PATCH 수정 | DELETE 삭제
```
