---
출처: Claude 분석
작성일: 2026-08-21
tags: [코드정리]
---

# JS 객체와 배열

> 상위: [[JS]]
> 세부: [[JS 배열 메소드 심화]] · [[JS JSON]] · [[JS 객체 심화]] · [[JS Map과 Set]]

## 객체 리터럴

```javascript
const post = {
    no: 1,
    title: "제목",
    write() { console.log("작성"); },
};

post.title;
post["title"];
post.views = 0;
delete post.views;
```

- 설계도(클래스) 없이 `{ 키: 값 }`으로 즉석에서 만든다 — 자바의 DTO 자리에 이게 온다
- 접근은 점이 기본, 키가 변수에 들어 있으면 대괄호(`post[keyName]`)를 쓴다
- 없는 속성을 읽으면 에러가 아니라 undefined다. 대입하면 그 자리에서 속성이 생긴다
- 단축 속성명: 변수명과 키가 같으면 `{ title, content }`로 줄인다(`{ title: title }`과 같음)
- 객체도 참조 타입이라 `const b = a`는 주소 복사다. 복사본은 `{ ...a }`

## 배열 기본 조작

```javascript
const list = ["a", "b", "c"];

list.push("d");
list.pop();
list.splice(1, 1);
list.splice(1, 0, "x");
list.length;
list.indexOf("b");
list.includes("b");
```

- `push` 끝에 추가, `pop` 끝에서 제거, `splice(위치, 개수)` 중간 삭제, `splice(위치, 0, 값)` 중간 삽입
- 자바 배열과 달리 길이 가변·타입 혼합 가능이고, `.length`로 개수를 본다
- `indexOf`는 위치(없으면 -1), `includes`는 존재 여부 boolean이다

## 탐색과 변환 — 콜백 3형제

```javascript
const found = list.find(p => p.no === no);
const idx = list.findIndex(p => p.no === no);
const mine = list.filter(p => p.writer === "유재석");
const titles = list.map(p => p.title);
```

- `find` 조건에 맞는 **첫 요소**(없으면 undefined), `findIndex` 그 위치(없으면 -1)
- `filter`는 조건에 맞는 것만 모은 **새 배열**, `map`은 각 요소를 변환한 **새 배열**이다 — 원본은 안 바뀐다
- 게시판에서 "no로 글 찾기"는 반드시 find/findIndex로 한다. `list[no]`는 삭제 후 번호와 인덱스가 어긋나 틀린다

## 정렬

```javascript
list.sort((a, b) => a.no - b.no);
list.sort((a, b) => b.no - a.no);
```

- 비교 함수가 음수면 a가 앞, 양수면 b가 앞이다. `a - b` 오름차순, `b - a` 내림차순(최신글 정렬)
- 함정: 비교 함수 없이 `sort()`하면 **문자열 기준**이라 [1, 10, 2] 순서가 된다. 숫자 정렬엔 반드시 비교 함수를 넣는다
- sort는 원본을 바꾼다. 원본 보존이 필요하면 `[...list].sort(...)`
