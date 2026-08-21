---
출처: Claude 분석
작성일: 2026-08-21
tags: [코드정리]
---

# JAVA 추상 클래스

> 상위: [[JAVA 상속과 인터페이스]]

## abstract — 미완성 설계도

```java
abstract class 동물 {
    String name;

    abstract void 울음();

    void show() { System.out.println(name + " 뜁니다."); }
}

class 참새 extends 동물 {
    @Override
    void 울음() { System.out.println("짹짹"); }
}
```

- `abstract` 메소드는 선언부만 있고 자식이 **반드시** 구현해야 한다. 하나라도 있으면 클래스에도 `abstract`를 붙인다
- 추상 클래스는 `new`가 안 된다: `동물 a = new 동물();` 불가, `동물 a = new 참새();` 가능
- 얻는 효과: 공통 코드(필드·완성 메소드)는 물려주면서, 각자 달라야 하는 부분만 구현을 강제한다

## 인터페이스와의 선택 기준

```
공통 상태(필드) + 부분 구현을 물려주고 싶다  → 추상 클래스 (is-a, 단일 상속)
순수하게 행위 규격만 정하고 싶다            → 인터페이스 (can-do, 다중 구현)
```

- "~의 한 종류다"면 추상 클래스, "~을 할 수 있다"면 인터페이스
- 실무 비중은 인터페이스가 크다 — 다중 구현이 되고 결합이 느슨해서다. 추상 클래스는 공통 필드·공통 로직이 진짜 있을 때 쓴다

## 실전형 — 공통 부모로 중복 제거

```java
abstract class BaseDao {
    protected Connection getConnection() throws SQLException {
        return DriverManager.getConnection(url, user, pw);
    }
}

class BookDao extends BaseDao { }
class MemberDao extends BaseDao { }
```

- DAO마다 반복되는 연결 코드를 부모에 한 번만 두고 자식들이 물려받는다(day12 종합예제의 BaseDao 상속이 이 구조다)
- DTO 쪽도 같다: 작성일·수정일 필드를 가진 BaseTime을 두고 각 DTO가 상속하면 공통 컬럼이 한 곳에 모인다
