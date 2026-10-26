---
출처: Claude 분석
원본: KDT_2026/2026_Python/day05/c8-2.py
작성일: 2026-10-26
tags: [학습, python]
---

# Python day05 — 프라이빗 변수·property와 상속

> 실습 파일: `day05/c8-2.py` (뒷부분 — `Circle`·`Parent`/`Child`)
> 허브: [[Python 정리본 인덱스]] · 이전: [[Python day05 클래스 변수와 특수 메소드 재정의]] · 다음: [[Python day06 넘파이 시작과 배열 생성]]

같은 파일의 뒷부분으로, 클래스 수업의 나머지 두 주제를 다룬다. 하나는 **캡슐화** — 멤버변수 이름 앞에 밑줄 두 개를 붙여 밖에서 직접 못 건드리게 숨기고(`__radius`), 대신 읽고 쓰는 통로를 getter·setter 메소드로 열어 주는 것, 그리고 그 통로를 `@property`로 감싸 **메소드인데 변수처럼** 쓰게 만드는 것. 다른 하나는 **상속** — `class Child(Parent):`로 부모의 멤버변수와 메소드를 물려받고, `super().__init__()`으로 부모 생성자를 먼저 돌린 뒤 자식 것을 덧붙이며, 같은 이름의 메소드를 자식이 다시 정의하면(오버라이딩) 자식 것이 실행된다는 것. `print()`가 몇 번 찍히는지 번호를 매겨 가며 확인한 순서 `(1) (3) (4) (1) (2) (4)`가 상속에서 생성자와 메소드가 어떻게 겹치고 가려지는지를 한눈에 보여 준다.

## 1. 배운 내용

### 1-1. 프라이빗 변수 — 이름 앞 밑줄 두 개

```python
# p.491 프라이빗 변수
class Circle:
    def __init__(self, radius):
        self.__radius = radius     # 프라이빗변수 , java: private int radius
        self.__radius2 = radius    # 프라이빗변수

    def get_circumference(self):
        return 2 * self.__radius   # 클래스 내부에서 프라이빗 변수 사용 가능

circle = Circle(10)
# print(circle.__radius)           # 클래스 외부에서 프라이빗 변수 사용 안됨 → AttributeError
```

| 쓰는 곳 | `self.__radius` | 결과 |
| --- | --- | --- |
| 클래스 안 (`get_circumference`) | 그대로 읽고 쓴다 | 정상 동작 |
| 클래스 밖 (`circle.__radius`) | 직접 접근 | `AttributeError` — 그런 이름이 없다고 나온다 |

멤버변수 이름을 `__`로 시작하면 **클래스 밖에서 그 이름으로는 닿지 않는다**. 자바의 `private`에 해당한다. 반지름처럼 "음수가 들어오면 안 되는 값"을 아무나 `circle.radius = -5`로 바꾸지 못하게 막고, 바꾸려면 반드시 정해진 통로(1-2의 setter)를 거치게 하려는 것이다. 자료와 그것을 다루는 규칙을 한 울타리에 넣고 바깥에는 필요한 문만 내는 것을 **캡슐화**라고 부른다. 앞 노트의 `name`·`korean`처럼 밑줄 없는 멤버변수는 전부 공개 상태였다.

### 1-2. getter·setter — 숨긴 값을 읽고 쓰는 통로

```python
    # setter and getter
    def get_radius(self):
        return self.__radius            # 프라이빗 변수 반환하는 getter 함수

    def set_radius(self, radius):
        self.__radius = radius          # 매개변수값을 프라이빗 변수에 저장하는 setter 함수

print(circle.get_radius())    # 10
circle.set_radius(20)
print(circle.get_radius())    # 20
```

| 메소드 | 역할 | 이름 관례 |
| --- | --- | --- |
| getter | 프라이빗 변수의 값을 **돌려준다** | `get_변수명` |
| setter | 받은 값을 프라이빗 변수에 **저장한다** | `set_변수명` |

밖에서는 `circle.__radius`를 쓸 수 없으니 `get_radius()`로 읽고 `set_radius(20)`으로 바꾼다. 지금은 그냥 넣고 빼기만 하지만, setter 안에 `if radius < 0: raise ValueError(...)`를 두면 **잘못된 값이 들어오는 순간을 한 곳에서 막을 수 있다** — day04의 `raise`가 바로 이 자리에서 쓰인다. 자바 수업에서 필드마다 `getXxx`·`setXxx`를 만들던 것과 같은 모양이고, 롬복의 `@Getter`·`@Setter`가 자동으로 만들어 주던 것이 이것이다.

### 1-3. `@property` — 메소드를 변수처럼 쓰기

```python
    @property               # 게터
    def radius2(self):
        return self.__radius2

    @radius2.setter         # 세터
    def radius2(self, value):
        self.__radius2 = value

print(circle.radius2)       # 10  — 괄호 없이 읽는데 위의 게터가 실행된다
circle.radius2 = 20         #      — 대입인데 세터가 실행된다
print(circle.radius2)       # 20
```

| 항목 | 설명 |
| --- | --- |
| `@property` | 바로 아래 메소드를 **읽기 통로**로 등록하는 데코레이터. `circle.radius2`라고 **괄호 없이** 쓰면 이 메소드가 실행되어 반환값이 나온다 |
| `@radius2.setter` | 같은 이름의 메소드를 **쓰기 통로**로 등록. `circle.radius2 = 20`이라고 대입하면 `value`에 20이 들어와 실행된다. 반드시 `@property` 뒤에, 같은 이름으로 |
| 메소드 이름 | 두 메소드가 **같은 이름**(`radius2`)이어야 한 속성으로 묶인다 |

1-2와 1-3은 하는 일이 똑같다. 차이는 **쓰는 쪽의 모양**뿐이다. `get_radius()`·`set_radius(20)`은 메소드를 부른다는 것이 드러나고, `radius2`·`radius2 = 20`은 평범한 변수를 다루는 것처럼 보이지만 실제로는 메소드가 돌아간다. 파이썬에서는 뒤쪽이 관용적이다. 처음에는 `self.radius = radius`로 공개 변수로 시작했다가, 나중에 검증이 필요해지면 **쓰는 쪽 코드를 한 줄도 안 고치고** `@property`로 바꿔 끼울 수 있기 때문이다. 자바처럼 처음부터 getter·setter를 전부 만들어 두지 않아도 되는 이유가 여기 있다.

### 1-4. 상속 — `class 자식(부모):`

```python
# p.497 상속의 활용
class Parent:
    def __init__(self):
        self.value = "테스트"
        print("parent init 메소드 호출")       # (1)
    def test(self):
        print("parent test()메소드 호출")      # (2)

# class 자식클래스명( 부모클래스명1, 부모클래스명2 ) : 파이썬은 부모클래스가 여러개 가능!
class Child(Parent):                            # java: class 자식클래스명 extends 부모클래스명{ }
    def __init__(self):
        super().__init__()                      # super(): 부모 인스턴스 가리킴
        print('child init 메소드 호출')         # (3)
    def test(self):                             # 오버라이딩/재정의
        print('child test 메소드 호출')         # (4)
```

| 항목 | 설명 |
| --- | --- |
| 상속 | 어떤 클래스를 **기반으로 그 속성과 기능을 물려받아** 새 클래스를 만드는 것. 부모(기반·슈퍼) 클래스 → 자식(파생·서브) 클래스 |
| `class Child(Parent):` | 괄호 안에 부모 클래스 이름. 자바의 `extends Parent` 자리. 파이썬은 `(A, B)`처럼 **부모를 여러 개** 적을 수 있다(다중 상속) |
| `super()` | 부모 클래스(의 인스턴스 쪽)를 가리키는 호출. `super().__init__()`은 **부모 생성자를 실행**해 `self.value` 같은 부모 멤버변수를 채운다 |
| 오버라이딩 | 부모에 있는 메소드와 **같은 이름**으로 자식에 다시 정의하면 자식 것이 부모 것을 가린다 |

`Child`는 `test`를 다시 정의했지만 `value` 멤버변수는 정의하지 않았다. 그래도 `child.value`를 읽으면 `"테스트"`가 나오는데, `super().__init__()`이 부모 생성자를 돌려 채워 줬기 때문이다. 이 줄을 빼면 `Child`의 생성자만 돌아 `value`가 생기지 않는다 — **자식 생성자는 부모 생성자를 자동으로 부르지 않는다**는 것이 자바와 다른 점이다(자바는 `super()`를 생략해도 부모 기본 생성자가 호출된다).

### 1-5. 실행 순서 추적 — `(1) (3) (4) (1) (2) (4)`

```python
child = Child()
# print() 출력되는 횟수  # 자식이 태어나면 부모도 같이 태어난다 (1) (3)
child.test()            # 부모 test() 가 아닌 자식 test() 가 실행된다 (4)
parent = Parent()       # (1)
parent.test()           # (2) test()메소드 호출
parent2 = child
parent2.test()          # (4) child test 메소드 호출
```

| 줄 | 찍히는 것 | 왜 |
| --- | --- | --- |
| `child = Child()` | (1) parent init → (3) child init | `Child.__init__`이 먼저 시작되지만 첫 줄 `super().__init__()`이 부모 생성자를 **먼저 끝내고** 돌아와 자기 `print`를 찍는다 |
| `child.test()` | (4) child test | `Child`에 `test`가 있으므로 부모 것은 보지 않는다 |
| `parent = Parent()` | (1) parent init | 부모만 만들면 부모 생성자만 |
| `parent.test()` | (2) parent test | 부모 인스턴스니 부모 메소드 |
| `parent2 = child; parent2.test()` | (4) child test | 변수 이름이 `parent2`여도 **가리키는 것은 `child` 인스턴스** — 대입은 복사가 아니라 별명(day02의 리스트 별명과 같다) |

"자식이 태어나면 부모도 같이 태어난다"는 메모가 핵심이다. `super().__init__()`이 `Child.__init__`의 **첫 줄**에 있기 때문에 부모 쪽 (1)이 자식 쪽 (3)보다 먼저 찍힌다. 메소드를 찾는 순서는 **자식 클래스 먼저, 없으면 부모**이므로 `test`는 (4)가 나오고, 자식에 없는 `value`는 부모에서 찾아 쓴다. 마지막 두 줄은 `parent2`라는 이름에 속지 말라는 확인용이다 — 어떤 메소드가 실행되는지는 **변수 이름이 아니라 그 변수가 가리키는 인스턴스가 어느 클래스로 만들어졌는가**가 정한다. 이것이 다형성의 출발점이다.

## 2. 추가로 알면 좋은 활용법

### 2-1. 프라이빗은 "진짜 잠금"이 아니다 — 이름 맹글링

```python
circle = Circle(10)
print(circle._Circle__radius)    # 10 — 사실은 이 이름으로 저장돼 있다
print(dir(circle))               # [..., '_Circle__radius', '_Circle__radius2', ...]
```

`__radius`는 파이썬이 내부적으로 `_Circle__radius`로 **이름을 바꿔 저장**(name mangling)할 뿐이라, 바뀐 이름을 알면 밖에서도 닿는다. 자바의 `private`처럼 컴파일러가 막는 게 아니라 "실수로 건드리지 말라"는 강한 신호다. 그래서 실무에서는 밑줄 **하나**(`_radius`)를 "내부용이니 밖에서 쓰지 말 것"이라는 약속으로 더 자주 쓰고, 밑줄 두 개는 자식 클래스와 이름이 충돌하면 안 되는 변수에만 쓴다.

### 2-2. setter에서 검증하기 — 캡슐화의 진짜 이유

```python
class Circle:
    def __init__(self, radius):
        self.radius = radius            # 아래 setter를 거친다

    @property
    def radius(self):
        return self._radius

    @radius.setter
    def radius(self, value):
        if value <= 0:
            raise ValueError("반지름은 0보다 커야 합니다")
        self._radius = value

    @property
    def circumference(self):            # 읽기 전용 — setter를 안 만들면 대입이 막힌다
        return 2 * 3.14159 * self._radius
```

수업 코드의 `set_radius`·`radius2.setter`는 받은 값을 그대로 넣지만, 통로를 만든 보람은 **여기서 조건을 거는 것**이다. 생성자에서도 `self.radius = radius`로 setter를 거치게 하면 만들 때부터 검증된다. `circumference`처럼 setter 없이 `@property`만 두면 **읽기 전용 속성**이 되어 `circle.circumference = 5`는 `AttributeError`가 난다 — 계산으로 나오는 값은 이렇게 두는 편이 안전하다.

### 2-3. 부모 생성자에 인수 넘기기와 `super().메소드()`

```python
class Student(Person):
    def __init__(self, name, school):
        super().__init__(name)          # 부모가 name을 받는다면 그대로 넘긴다
        self.school = school

    def introduce(self):
        super().introduce()             # 부모 것을 먼저 실행하고
        print(f"{self.school} 다닙니다") # 덧붙인다
```

수업 예제는 부모 생성자가 인수를 받지 않았지만, 보통은 `super().__init__(name)`처럼 **부모 몫의 인수를 넘긴다**. 오버라이딩할 때도 부모 것을 완전히 버리는 대신 `super().test()`로 먼저 돌리고 자식 내용을 추가하는 패턴이 흔하다 — "부모 기능 + α"가 상속의 본래 목적이기 때문이다.

### 2-4. 상속 여부 확인 — `isinstance`·`issubclass`

```python
print(isinstance(child, Child))     # True
print(isinstance(child, Parent))    # True  — 부모 클래스로도 참
print(issubclass(Child, Parent))    # True
print(type(child) is Parent)        # False — type은 정확히 그 클래스만
```

앞 노트의 `isinstance`가 상속에서 진가를 보인다. `child`는 `Parent`로도 `True`라서 "부모 타입을 받는 함수에 자식을 넘기는" 코드가 자연스럽게 된다. 정확히 어느 클래스인지가 필요할 때만 `type(x) is`를 쓴다.

### 2-5. 자바와 나란히 — 대응표

| 파이썬 | 자바 | 메모 |
| --- | --- | --- |
| `self.__radius` | `private int radius;` | 파이썬은 이름 맹글링, 강제 아님 |
| `get_radius()` / `set_radius(v)` | `getRadius()` / `setRadius(v)` | 롬복 `@Getter`·`@Setter`가 만들던 것 |
| `@property` / `@x.setter` | (없음) | 자바는 항상 메소드로 부른다 |
| `class Child(Parent):` | `class Child extends Parent {` | 파이썬은 다중 상속 가능 |
| `super().__init__()` | `super();` | 파이썬은 **생략하면 부모 생성자가 안 돈다** |
| 같은 이름으로 재정의 | `@Override` | 파이썬은 표시 없이 덮인다 — 오타로 새 메소드가 생겨도 경고 없음 |
| `isinstance(c, Parent)` | `c instanceof Parent` | |

## 3. 더 나아가 알면 좋은 것

- **다형성** — 부모 타입 자리에서 자식 인스턴스마다 다른 `test()`가 실행되는 것. `for shape in [Circle(), Square()]: shape.area()`처럼 **같은 호출, 다른 동작**. 파이썬은 상속 없이도 메소드 이름만 같으면 되는 덕 타이핑(duck typing)이 기본이다
- **MRO(메소드 탐색 순서)** — 다중 상속에서 같은 이름이 여러 부모에 있으면 `Child.__mro__` 순서로 찾는다. `super()`가 "바로 위 부모"가 아니라 "MRO의 다음"을 가리키는 이유
- **추상 클래스 `abc.ABC`·`@abstractmethod`** — 자식이 반드시 구현해야 하는 메소드를 강제. 자바 인터페이스·추상 클래스에 대응
- **상속보다 조합** — "A는 B다"가 아니라 "A는 B를 가진다"면 상속 대신 멤버변수로 들고 쓰는 편이 유연하다. 상속 계층이 세 단 넘게 깊어지면 신호
- **`__slots__`·`__getattr__`** — 속성 접근 자체를 제어하는 다음 단계. `@property`가 속성 하나라면 이쪽은 모든 속성
- **사용자 정의 예외** — day04에서 키워드로 적어 둔 `class InvalidRadiusError(ValueError): pass`가 바로 오늘의 상속이다. `Exception` 계층 전체가 상속 트리다
- **`dataclass`와 `__post_init__`** — 필드 자동 생성에 검증만 덧붙이는 자리

### 다음에 볼 키워드

- 캡슐화, 이름 맹글링, `@property` 읽기 전용, `super()`와 MRO, 오버라이딩, 다형성, 덕 타이핑, `abc.ABC`, 조합 vs 상속

## 실습 파일

- `KDT_2026/2026_Python/day05/c8-2.py` (뒷부분) — `Circle` 클래스에 `self.__radius`·`self.__radius2` 프라이빗 변수를 두고 클래스 안 `get_circumference`에서는 쓰이지만 밖에서 `circle.__radius`는 안 되는 것 확인, `get_radius`·`set_radius` getter·setter로 10 → 20 변경, `@property`·`@radius2.setter`로 `circle.radius2`·`circle.radius2 = 20`처럼 변수 모양으로 읽고 쓰기, `Parent`(`value` 멤버변수·`test` 메소드)를 `class Child(Parent):`로 상속해 `super().__init__()` 뒤 자기 `print`·`test` 오버라이딩, `Child()`·`child.test()`·`Parent()`·`parent.test()`·`parent2 = child; parent2.test()`의 출력 순서 `(1) (3) (4) (1) (2) (4)` 확인. 앞부분(`isinstance`·클래스 변수·특수 메소드)은 이전 노트

## 관련 노트

[[Python 정리본 인덱스]] · [[Python day05 클래스 변수와 특수 메소드 재정의]] · [[Python day06 넘파이 시작과 배열 생성]] · [[Python day05 클래스 정의와 생성자·메소드]] · [[Python day04 예외 처리 try·except·else·finally]] · [[KDT_2026 학습 지도]]
