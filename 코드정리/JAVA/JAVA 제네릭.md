---
출처: Claude 분석
작성일: 2026-08-21
tags: [코드정리]
---

# JAVA 제네릭

> 상위: [[JAVA 상속과 인터페이스]]

`ArrayList<String>`의 `<>`를 내 클래스·인터페이스에도 만드는 문법이다.

## 제네릭 클래스·인터페이스

```java
class Box<T> {
    private T value;

    public void set(T value) { this.value = value; }
    public T get() { return value; }
}

Box<String> b1 = new Box<>();
Box<Integer> b2 = new Box<>();
```

- `<T>`는 "타입을 나중에 정한다"는 자리표시자다. 쓰는 쪽이 `<String>`으로 정하면 T가 전부 String으로 채워진다
- 얻는 효과: 타입마다 클래스를 복사하지 않아도 되고, 잘못된 타입을 넣으면 **컴파일 시점에** 잡힌다(Object로 받으면 런타임에 터진다)
- 제네릭엔 기본 타입이 못 들어간다. `Box<int>` 불가, `Box<Integer>` 사용

## 실전형 — 공통 DAO 인터페이스

```java
interface IBaseDao<T> {
    boolean save(T dto);
    ArrayList<T> findAll();
}

class BookDao implements IBaseDao<BookDto> {
    @Override public boolean save(BookDto dto) { ... }
    @Override public ArrayList<BookDto> findAll() { ... }
}

class MemberDao implements IBaseDao<MemberDto> { ... }
```

- save/findAll의 규격은 한 번만 정의하고, DAO마다 T만 자기 DTO로 채운다(day11 종합예제의 IBaseDao가 이 구조다)
- 얻는 효과: 모든 DAO의 메소드 이름·형태가 강제로 통일된다. 새 도메인이 늘어도 규격이 흔들리지 않는다

## 제네릭 메소드 ※

```java
static <T> T firstOrNull(List<T> list) {
    return list.isEmpty() ? null : list.get(0);
}
```

- 메소드 하나에만 타입 변수를 둘 수도 있다. 반환 타입 앞의 `<T>`가 선언이다

## 와일드카드 ※

```java
void printAll(List<?> list) { }
void sum(List<? extends Number> nums) { }
```

- `?`는 "아무 타입이나", `? extends Number`는 "Number의 자식이면 뭐든"이다
- 읽을 줄만 알면 된다: 컬렉션을 받는 라이브러리 메소드 시그니처에서 자주 만난다
