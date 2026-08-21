---
출처: Claude 분석
작성일: 2026-08-21
tags: [코드정리]
---

# JS this와 화살표 함수

> 상위: [[JS 함수]]

전부 ※. "this가 뭘 가리키는지"는 JS에서 가장 자주 헷갈리는 지점이다.

## this는 부르는 방법이 정한다

```javascript
const counter = {
    count: 0,
    increase() {
        this.count++;
    },
};

counter.increase();

const fn = counter.increase;
fn();
```

- 자바의 this는 항상 자기 인스턴스지만, JS의 this는 **함수를 어떻게 불렀는지**에 따라 매번 바뀐다
- `counter.increase()`처럼 점 앞에 객체가 있으면 this = 그 객체다
- 함수만 뽑아서 `fn()`으로 부르면 점 앞이 없으니 this가 객체를 잃는다(undefined/전역) — "메소드를 변수에 담았더니 안 된다"의 원인

## 화살표 함수는 this가 없다

```javascript
const timer = {
    seconds: 0,
    start() {
        setInterval(() => {
            this.seconds++;
        }, 1000);
    },
};
```

- 화살표 함수는 자기 this를 만들지 않고 **바깥(선언된 곳)의 this를 그대로** 쓴다
- setInterval에 일반 function을 넣으면 this가 timer가 아니게 되어 seconds가 안 늘어난다 — 콜백은 화살표로 쓰는 게 관용인 이유
- 반대로 **객체 메소드 자체를 화살표로 정의하면 안 된다**: `increase: () => this.count++`는 바깥 this를 붙잡아 객체를 못 가리킨다. "메소드는 단축 문법, 콜백은 화살표"로 기억한다

## 이벤트 리스너에서

```javascript
button.addEventListener("click", function () {
    this.classList.toggle("active");
});

button.addEventListener("click", e => {
    e.currentTarget.classList.toggle("active");
});
```

- 일반 function 리스너의 this는 이벤트가 걸린 요소다. 화살표 리스너에선 this가 요소가 아니므로 `e.currentTarget`을 쓴다
- 팀·AI 코드가 대부분 화살표 + `e.target`/`e.currentTarget` 스타일이다 — this에 의존하지 않는 쪽이 사고가 적다
