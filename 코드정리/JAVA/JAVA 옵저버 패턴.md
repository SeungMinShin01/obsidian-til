---
출처: Claude 분석
작성일: 2026-08-21
tags: [코드정리]
---

# JAVA 옵저버 패턴

> 상위: [[JAVA 패턴]]

전부 ※. "무슨 일이 생기면 나한테 알려줘"를 코드로 만드는 패턴이다.

## 구조

```java
interface StockListener {
    void onStockChanged(String title, int stock);
}

class Book {
    private int stock;
    private final List<StockListener> listeners = new ArrayList<>();

    public void addListener(StockListener l) { listeners.add(l); }

    public void setStock(int stock) {
        this.stock = stock;
        for (StockListener l : listeners) {
            l.onStockChanged(title, stock);
        }
    }
}
```

```java
book.addListener((title, stock) -> {
    if (stock == 0) System.out.println("[알림] " + title + " 품절");
});
```

- 구성 3요소: 듣는 규격(리스너 인터페이스), 듣는 쪽 목록(listeners), 상태가 바뀔 때 목록을 돌며 호출(통지)
- 핵심 효과: **Book은 알림을 누가 왜 받는지 모른다.** 품절 문자 발송·화면 갱신·로그 기록이 늘어나도 Book 코드는 안 바뀌고 리스너만 추가된다
- 리스너가 함수형 인터페이스(추상메소드 1개)면 위처럼 람다로 등록할 수 있다

## 이미 쓰고 있던 곳

```javascript
button.addEventListener("click", () => { ... });
```

- JS의 addEventListener가 바로 옵저버 패턴이다. 버튼(주체)은 클릭 때 등록된 함수들을 부를 뿐, 그 함수가 뭘 하는지 모른다
- 안드로이드의 OnClickListener, 스프링의 이벤트(@EventListener)도 같은 구조다. "이벤트 기반"이라는 말이 곧 이 패턴 위에 서 있다는 뜻이다
