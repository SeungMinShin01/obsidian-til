---
출처: Claude 분석
작성일: 2026-08-21
tags: [코드정리]
---

# JS 이벤트 심화

> 상위: [[JS DOM]]

전부 ※. 동적으로 생기는 요소에 이벤트를 거는 순간 필요해지는 것들이다.

## 이벤트 객체

```javascript
input.addEventListener("keydown", e => {
    if (e.key === "Enter") save();
});

list.addEventListener("click", e => {
    console.log(e.target);
});
```

- 콜백의 첫 인수 `e`에 그 사건의 정보가 담겨 온다: `e.key` 눌린 키, `e.target` 실제로 클릭된 요소
- 엔터로 등록되게 하기가 `e.key === "Enter"` 한 줄이다

## 버블링과 위임

```javascript
tbody.addEventListener("click", e => {
    const btn = e.target.closest("button.delete");
    if (!btn) return;
    const no = Number(btn.dataset.no);
    deletePost(no);
});
```

- 자식에서 난 이벤트는 부모로 올라간다(버블링). 그래서 **부모 하나에만 리스너를 걸고** `e.target`으로 누가 눌렸는지 판별할 수 있다 — 이것이 위임(delegation)이다
- 왜 필수인가: innerHTML로 목록을 다시 그리면 **기존 요소들의 리스너가 전부 사라진다.** 행마다 걸었다면 다시 걸어야 하지만, 부모(tbody)에 위임했다면 다시 그려도 그대로 동작한다
- `closest("선택자")`는 눌린 지점에서 위로 올라가며 조건에 맞는 조상을 찾는다(버튼 안의 아이콘을 눌러도 버튼을 잡아준다)

## data 속성 — 요소에 데이터 싣기

```html
<button class="delete" data-no="3">삭제</button>
```

```javascript
const no = Number(btn.dataset.no);
```

- `data-이름="값"`으로 HTML에 심고 JS에서 `dataset.이름`으로 읽는다. "이 버튼이 몇 번 글의 버튼인가"를 나르는 표준 통로다
- dataset 값도 문자열이므로 Number 변환을 잊지 않는다

## 기본 동작 취소와 전파 중단

```javascript
a.addEventListener("click", e => e.preventDefault());
inner.addEventListener("click", e => e.stopPropagation());
```

- `preventDefault()`는 브라우저 기본 동작(링크 이동·폼 제출) 취소, `stopPropagation()`은 부모로의 버블링 중단이다
- 둘은 다른 것이다 — 모달 안쪽 클릭이 바깥 닫기 리스너까지 올라가는 걸 막는 게 stopPropagation 쪽이다
