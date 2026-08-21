---
출처: Claude 분석
작성일: 2026-08-21
tags: [코드정리]
---

# JS 스토리지와 타이머

> 상위: [[JS]]
> 세부: [[JS fetch와 비동기]] · [[JS 날짜와 시간]]

## localStorage

```javascript
localStorage.setItem("boardList", JSON.stringify(list));
const raw = localStorage.getItem("boardList");
const list = raw == null ? [] : JSON.parse(raw);
localStorage.removeItem("boardList");
localStorage.clear();
```

- 브라우저에 키-값을 저장한다. 새로고침·브라우저 재시작에도 남는다(같은 사이트 한정)
- **문자열만 저장**되므로 객체·배열은 stringify로 넣고 parse로 꺼낸다 — 이 왕복이 항상 세트다
- 없는 키는 null이 온다. `raw == null ? [] : JSON.parse(raw)` 또는 `JSON.parse(raw ?? "[]")`가 첫 실행 대비 관용구다
- 한계: 사용자 브라우저 안에만 있어 다른 기기·다른 사람과 공유가 안 된다. 이 한계가 백엔드(DB)가 필요한 이유다
- sessionStorage는 같은 API인데 탭을 닫으면 사라진다

## setInterval · setTimeout

```javascript
const id = setInterval(() => {
    idx = (idx + 1) % images.length;
    img.src = images[idx];
}, 3000);

clearInterval(id);

setTimeout(() => alert("3초 후 한 번"), 3000);
```

- `setInterval(콜백, ms)`은 주기 반복, `setTimeout`은 한 번만 지연 실행이다
- 반환된 id를 `clearInterval`/`clearTimeout`에 넘겨 멈춘다 — 슬라이드 일시정지가 이것이다
- `(idx + 1) % length`가 마지막 다음에 0으로 돌아가는 순환 관용구다(이미지 슬라이드의 심장)
- 함정: 멈추지 않은 인터벌은 페이지가 살아 있는 한 계속 돈다. 새로 걸기 전에 기존 것을 clear하는 습관이 필요하다
