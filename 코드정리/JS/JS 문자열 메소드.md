---
출처: Claude 분석
작성일: 2026-08-21
tags: [코드정리]
---

# JS 문자열 메소드

> 상위: [[JS 기본 문법]]

## 검사와 탐색

```javascript
s.length;
s.includes("자바");
s.startsWith("http");
s.endsWith(".png");
s.indexOf("a");
s.charAt(0);
s[0];
```

- `length`는 프로퍼티라 괄호가 없다(자바의 메소드 `length()`와 다른 점)
- `includes` 포함 여부, `startsWith`/`endsWith` 시작·끝 검사 — URL·확장자 판별의 관용구다
- `indexOf`는 위치(없으면 -1)이고, 한 글자는 `charAt(0)`이나 대괄호 인덱싱 둘 다 된다

## 자르기와 变환

```javascript
s.substring(1, 4);
s.slice(-3);
s.split(",");
s.trim();
s.replace("a", "b");
s.replaceAll("a", "b");
s.toUpperCase();
s.toLowerCase();
s.padStart(2, "0");
s.repeat(3);
```

- `slice`는 음수 인덱스가 된다 — `slice(-3)`이 뒤 3글자(확장자 뽑기)
- `replace`는 **첫 번째만** 바꾼다. 전부 바꾸려면 `replaceAll` 또는 정규식 `/a/g`
- `padStart(2, "0")`은 앞을 0으로 채워 자릿수를 맞춘다 — 시계 표시 `9 → "09"`의 정석
- split ↔ join이 왕복 짝이다: `"a,b".split(",")` ↔ `["a","b"].join(",")`

## 템플릿 리터럴

```javascript
const msg = `${name}님, ${list.length}건의 글이 있습니다.`;

const html = `
    <tr>
        <td>${b.no}</td>
        <td>${b.title}</td>
    </tr>
`;
```

- 백틱 문자열 안 `${}`에 변수·식이 바로 들어간다. `+` 이어붙이기를 완전히 대체한다
- **여러 줄이 그대로 된다** — HTML 조각 만들기에서 진가가 나온다. 게시판 목록 렌더링이 전부 이 문법이다
- `${}` 안에는 삼항·함수 호출도 들어간다: `${b.done ? "완료" : "진행중"}`
