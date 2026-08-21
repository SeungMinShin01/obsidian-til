---
출처: Claude 분석
작성일: 2026-08-21
tags: [코드정리]
---

# JS fetch와 비동기

> 상위: [[JS 스토리지와 타이머]]

전부 ※. localStorage를 백엔드 API로 바꾸는 날 필요한 문법이다.

## 비동기 — 기다리지 않는 실행

```javascript
console.log(1);
setTimeout(() => console.log(2), 0);
console.log(3);
```

- 출력은 1, 3, 2다. 오래 걸리는 일(타이머·네트워크)은 옆에 밀어두고 다음 줄을 먼저 실행하기 때문이다
- 서버 요청도 마찬가지라 "결과가 **나중에** 온다"를 다루는 문법이 필요하다 — 그 답이 Promise와 async/await이다

## async · await

```javascript
async function loadBoards() {
    const res = await fetch("/api/boards");
    const boards = await res.json();
    return boards;
}
```

- `await`는 "결과가 올 때까지 이 줄에서 기다렸다가 값으로 받는다"이다. 비동기 코드가 동기 코드처럼 위에서 아래로 읽힌다
- `await`는 `async`가 붙은 함수 안에서만 쓸 수 있다. async 함수의 반환값은 자동으로 Promise가 된다(부르는 쪽도 await로 받는다)
- `res.json()`은 응답 본문(JSON 문자열)을 객체로 바꾸는 것이고 이것도 await가 필요하다

## fetch — GET과 POST

```javascript
const res = await fetch("/api/boards");

await fetch("/api/boards", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(newPost),
});
```

- 인수 하나면 GET(조회)이다. 만들기·수정·삭제는 두 번째 인수에 method·headers·body를 준다
- body는 문자열이어야 하므로 JSON.stringify를 거친다 — localStorage 때 하던 그 변환이 그대로 재등장한다
- CRUD 대응: 조회 GET / 등록 POST / 수정 PUT / 삭제 DELETE. localStorage 게시판의 함수 넷이 이 넷으로 1:1 치환된다

## 에러 처리

```javascript
try {
    const res = await fetch("/api/boards");
    if (!res.ok) throw new Error("HTTP " + res.status);
    const data = await res.json();
} catch (e) {
    alert("불러오기 실패: " + e.message);
}
```

- 네트워크 자체가 끊기면 fetch가 던지고(catch로), 서버가 404·500을 줘도 fetch는 **정상 완료**다 — 그래서 `res.ok` 검사를 직접 한다
- 이 try-catch 구조는 자바 예외처리와 같은 사고방식이다
