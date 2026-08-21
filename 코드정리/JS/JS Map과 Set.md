---
출처: Claude 분석
작성일: 2026-08-21
tags: [코드정리]
---

# JS Map과 Set

> 상위: [[JS 객체와 배열]]

전부 ※. 자바 컬렉션의 HashMap·HashSet에 해당하는 JS 내장 자료구조다.

## Map — 진짜 키-값 저장소

```javascript
const cache = new Map();

cache.set(3, post);
cache.get(3);
cache.has(3);
cache.delete(3);
cache.size;

for (const [no, p] of cache) {
    console.log(no, p.title);
}
```

- 객체 `{}`와 달리 **키에 숫자·객체 등 아무 타입**이나 쓸 수 있고, 넣은 순서가 유지되며, `size`로 개수를 바로 안다
- get/set/has/delete 네 개가 전부다. 순회는 for...of로 `[키, 값]`이 바로 풀린다
- "no로 글 찾기"를 배열 find(O(n)) 대신 Map get(O(1))으로 바꾸는 게 자바에서 List→Map 전환과 같은 이야기다
- 객체로 충분한 경우(키가 문자열, 구조 고정)는 그냥 객체를 쓴다 — JSON 변환도 객체가 편하다(Map은 stringify가 바로 안 됨)

## Set — 중복 없는 집합

```javascript
const tags = new Set();

tags.add("java");
tags.add("java");
tags.has("java");
tags.delete("java");
tags.size;
```

- 같은 값을 여러 번 add해도 하나만 남는다. "이미 처리했나?" 체크 목록에 최적이다
- 방문한 글 번호 기록, 선택된 항목 관리처럼 **존재 여부만 중요한 데이터**는 배열보다 Set이 맞는 그릇이다

## 중복 제거 관용구

```javascript
const unique = [...new Set(list)];
const authors = [...new Set(books.map(b => b.author))];
```

- 배열 → Set → 스프레드로 다시 배열. 중복 제거의 표준 한 줄이다
- 두 번째 줄처럼 map과 조합하면 "저자 목록 뽑기(중복 없이)"가 된다 — SQL의 SELECT DISTINCT 자리다
