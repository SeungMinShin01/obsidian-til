---
출처: Claude 분석
작성일: 2026-08-21
tags: [코드정리]
---

# JS 디바운스와 쓰로틀

> 상위: [[JS 패턴]]

전부 ※. "너무 자주 발생하는 이벤트"를 다듬는 두 가지 기법이다.

## 문제

```javascript
searchInput.addEventListener("input", () => search());
window.addEventListener("scroll", () => updatePosition());
```

- input은 한 글자마다, scroll은 초당 수십 번 발생한다. 매번 검색·계산을 돌리면 낭비가 크고, fetch라면 서버에 타자 수만큼 요청이 날아간다

## 디바운스 — 멈추면 한 번

```javascript
function debounce(fn, delay) {
    let id;
    return (...args) => {
        clearTimeout(id);
        id = setTimeout(() => fn(...args), delay);
    };
}

searchInput.addEventListener("input", debounce(e => search(e.target.value), 300));
```

- 이벤트가 올 때마다 예약을 **취소하고 다시 예약**한다. 결과: 입력이 300ms 멈춘 뒤에야 한 번 실행된다
- "타자 다 치고 나면 검색"이 정확히 이 동작이다. 자동 저장·리사이즈 처리도 같은 용도
- 클로저(타이머 id를 기억)와 setTimeout의 조합이라, 두 개념의 실전 종합 문제이기도 하다

## 쓰로틀 — 일정 간격으로만

```javascript
function throttle(fn, interval) {
    let last = 0;
    return (...args) => {
        const now = Date.now();
        if (now - last >= interval) {
            last = now;
            fn(...args);
        }
    };
}

window.addEventListener("scroll", throttle(() => updatePosition(), 200));
```

- 아무리 자주 불려도 **interval에 한 번만** 통과시킨다. 스크롤 위치 표시·무한 스크롤 감지처럼 "진행 중에도 주기적으로는 반응해야 하는" 경우에 맞다

## 고르는 기준

```
디바운스  →  끝나고 한 번이면 충분   (검색어 입력, 자동 저장, 창 크기 조절 완료)
쓰로틀    →  진행 중에도 주기 반응    (스크롤 감지, 마우스 이동 추적, 게임 입력)
```

- 헷갈리면 "마지막 한 번만 중요한가(디바운스), 중간중간도 중요한가(쓰로틀)"로 묻는다
