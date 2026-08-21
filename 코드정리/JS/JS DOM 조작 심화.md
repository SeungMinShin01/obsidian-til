---
출처: Claude 분석
작성일: 2026-08-21
tags: [코드정리]
---

# JS DOM 조작 심화

> 상위: [[JS DOM]]

전부 ※. innerHTML 문자열 조립 다음 단계 — 요소를 객체로 만들고 다루는 방법이다.

## createElement — 요소를 코드로 만들기

```javascript
const tr = document.createElement("tr");
const td = document.createElement("td");
td.textContent = post.title;
tr.appendChild(td);
tbody.appendChild(tr);

tr.remove();
```

- 만들고(createElement) → 채우고(textContent) → 붙인다(appendChild). 지우기는 `remove()` 한 방이다
- innerHTML 조립과의 차이: 사용자 입력을 textContent로 넣으면 **XSS가 원천 차단**되고, 기존 요소들의 이벤트 리스너가 날아가지 않는다
- 목록 전체를 다시 그릴 땐 innerHTML이 간단하고, 한 행만 추가·삭제할 땐 createElement 쪽이 정확하다 — 상황으로 고른다

## classList — 클래스 토글

```javascript
el.classList.add("active");
el.classList.remove("active");
el.classList.toggle("open");
el.classList.contains("active");
```

- 클래스 넣고 빼기의 표준 API다. `className = "..."`으로 통째로 덮는 것보다 안전하다
- `toggle`은 있으면 빼고 없으면 넣는다 — 메뉴 열닫이·다크모드 버튼이 이 한 줄이다
- 상태를 JS 변수로도 두고 클래스로도 두면 어긋난다. **클래스가 곧 상태**가 되게 `contains`로 판단하는 게 깔끔하다

## 삽입 위치 지정

```javascript
list.insertAdjacentHTML("afterbegin", `<li>${title}</li>`);
list.insertAdjacentElement("beforeend", li);
target.before(newEl);
target.after(newEl);
```

- `afterbegin` 안쪽 맨 앞(최신글 위로), `beforeend` 안쪽 맨 뒤(appendChild와 동일) — 네 위치 문자열로 어디든 꽂는다
- innerHTML `+=`처럼 전체를 다시 그리지 않고 **기존 내용을 보존한 채** 조각만 붙는다는 게 장점이다

## 탐색과 속성

```javascript
const row = btn.closest("tr");
const next = row.nextElementSibling;
const cells = row.children;

el.getAttribute("href");
el.setAttribute("disabled", "");
el.style.display = "none";
```

- `closest`는 위로(조상), `children`·`nextElementSibling`은 옆·아래로 — 클릭된 버튼에서 자기 행을 찾는 이동이 `closest("tr")`다
- style 직접 대입은 임시 처리엔 되지만, 스타일 상태는 가급적 classList로 다루고 CSS에 모아 두는 편이 관리된다
