---
출처: Claude 분석
작성일: 2026-08-21
tags: [코드정리]
---

# JAVA 사용자 정의 예외

> 상위: [[JAVA 예외와 유틸]]

전부 ※. 표준 예외 대신 **업무 용어로 이름 붙인 예외**를 만드는 방법이다.

## 만들기

```java
public class OutOfStockException extends RuntimeException {
    public OutOfStockException(String message) {
        super(message);
    }
}
```

- `RuntimeException`을 상속하고 메시지를 `super`로 넘기면 끝이다. 대부분 이 두 줄짜리다
- 이름 자체가 문서가 된다: `IllegalStateException`보다 `OutOfStockException`(재고 없음), `AlreadyRentedException`(이미 대여 중)이 원인을 바로 말해준다

## 던지고 받기

```java
public void rent(int bookNo) {
    Book b = findBook(bookNo);
    if (b == null) throw new BookNotFoundException("없는 도서: " + bookNo);
    if (b.getStock() == 0) throw new OutOfStockException(b.getTitle());
    ...
}

try {
    controller.rent(no);
    System.out.println("대여 완료");
} catch (BookNotFoundException | OutOfStockException e) {
    System.out.println("[실패] " + e.getMessage());
}
```

- 검증하는 쪽(Controller)은 이유별로 던지기만 하고, 안내문 출력은 받는 쪽(View)이 한다 — 계층 분리가 예외에도 그대로 적용된다
- `catch (A | B e)`는 여러 예외를 한 번에 받는 문법이다
- boolean 반환과의 차이: false는 "실패했다"만 알려주지만 예외는 **왜** 실패했는지를 종류와 메시지로 나른다

## Checked vs Unchecked

```
RuntimeException 상속 (unchecked)  →  try-catch 강제 아님. 업무 규칙 위반에 보통 이쪽
Exception 상속 (checked)           →  호출부가 반드시 처리해야 컴파일됨 (SQLException이 이 부류)
```

- 실무 관례는 대부분 unchecked(RuntimeException 계열)다. checked는 처리 코드가 강제로 퍼져서 번거롭다
