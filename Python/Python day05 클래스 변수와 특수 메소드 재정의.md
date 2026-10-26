---
출처: Claude 분석
원본: KDT_2026/2026_Python/day05/c8-2.py
작성일: 2026-10-26
tags: [학습, python]
---

# Python day05 — 클래스 변수와 특수 메소드 재정의

> 실습 파일: `day05/c8-2.py` (앞부분 — `isinstance`·`Student2` 확장)
> 허브: [[Python 정리본 인덱스]] · 이전: [[Python day05 클래스 정의와 생성자·메소드]] · 다음: [[Python day05 프라이빗 변수·property와 상속]]

앞 노트의 `Student2`를 그대로 가져와 세 가지를 덧붙인 부분이다. 첫째, 어떤 인스턴스가 어느 클래스에서 나왔는지 묻는 `isinstance`. 둘째, 인스턴스마다 따로 갖는 멤버변수와 달리 **클래스 하나에 붙어 모든 인스턴스가 공유하는 클래스 변수**(`count`·`students`)와, 인스턴스 없이 클래스 이름으로 부르는 `@classmethod`. 셋째, `__str__`·`__eq__`처럼 **이름이 정해진 특수 메소드**를 재정의하면 `str(인스턴스)`나 `==` 같은 파이썬의 기본 동작이 내가 정한 기준으로 바뀐다는 것. 특히 `students[0] == students[1]`이 서로 다른 인스턴스인데도 `True`가 나오는 장면이 이 파일의 핵심이다 — "같다"의 기준을 주소가 아니라 총점으로 내가 정했기 때문이다.

## 1. 배운 내용

### 1-1. `isinstance(인스턴스, 클래스명)` — 어느 설계도에서 나왔나

```python
class Student:
    def __init__(self):
        pass

class Human:
    def __init__(self):
        pass

student = Student()
print(isinstance(student, Student))   # True
print(isinstance(student, Human))     # False
```

| 식 | 결과 | 이유 |
| --- | --- | --- |
| `isinstance(student, Student)` | `True` | `student`는 `Student()`로 만들었다 |
| `isinstance(student, Human)` | `False` | `Human`과는 아무 관계가 없다 — 생성자 모양이 똑같아도 다른 클래스 |

`isinstance`는 **"이 인스턴스가 이 클래스(또는 그 자식 클래스)로 만들어졌는가"**를 참·거짓으로 돌려주는 내장 함수다. day02 딕셔너리 연습에서 `type(value) is str` 대신 `isinstance(value, (str, int))`를 쓸 수 있다고 적어 두었는데, 그때는 내장 자료형에 썼고 오늘은 내가 만든 클래스에 쓴다. `Student`와 `Human`은 몸체가 글자 하나 다르지 않지만 **이름이 다르면 다른 클래스**라서 `False`다. 다음 노트의 상속에서 `Child`가 `Parent`를 물려받으면 `isinstance(child, Parent)`도 `True`가 되는데, 그래서 `type(x) is Y`보다 `isinstance`가 상속을 고려한 안전한 검사다.

### 1-2. 클래스 변수 — 인스턴스 없이도 있는 값

```python
class Student2:
    # p.484 클래스변수 ? 인스턴스없이 사용 가능한 변수
    # 클래스변수명 = 초기값
    count = 0
    students = []

    def __init__(self, name, korean, math, engligh, science):
        # 멤버/인스턴스 변수
        self.name = name
        # ...
        Student2.count += 1              # 클래스변수 호출방법: 클래스명.변수명
        Student2.students.append(self)
```

| | 인스턴스 변수 | 클래스 변수 |
| --- | --- | --- |
| 어디에 적나 | `__init__` 안에서 `self.name = ...` | 클래스 블록 바로 아래 `count = 0` (`self` 없이) |
| 누가 갖나 | **인스턴스마다 하나씩** — 학생 여섯이면 `name` 칸도 여섯 | **클래스에 하나** — 모든 인스턴스가 같은 칸을 본다 |
| 어떻게 부르나 | `self.name`, `students[0].name` | `Student2.count` (클래스명.변수명) |
| 언제 생기나 | 인스턴스를 만들 때 | 클래스 정의가 실행될 때 — 인스턴스가 하나도 없어도 존재 |

`count`는 "지금까지 만든 학생 수", `students`는 "지금까지 만든 학생 전부"인데, 이 둘은 **어느 한 학생의 정보가 아니라 학생 전체에 대한 정보**다. 그래서 `self.`에 두지 않고 클래스에 둔다. 생성자 안에서 `Student2.count += 1`과 `Student2.students.append(self)`를 해 두면 인스턴스가 만들어질 때마다 자동으로 세어지고 모인다 — `self`를 리스트에 넣는다는 것은 **방금 태어난 인스턴스 자신을 명부에 올리는 것**이다. 여섯 번 만들고 나면 `Student2.count`는 6이다.

```python
print(Student2.count)   # 6  — __init__이 6번 실행됐다
```

읽을 때도 `Student2.count`처럼 클래스 이름으로 읽는다. 자바의 `static` 필드와 같은 자리다.

### 1-3. `@classmethod` — 인스턴스 없이 부르는 메소드

```python
    # p.486 클래스함수
    @classmethod            # 클래스함수 정의하는 데코레이터/어노테이션
    def print(cls):         # 매개변수에 cls 관례적으로 선언
        for student in cls.students:
            # cls.클래스변수 <--동일--> 클래스명.클래스변수
            print(str(student))

Student2.print()            # 클래스명.클래스함수
```

| 항목 | 설명 |
| --- | --- |
| `@classmethod` | 바로 아래 `def`를 **클래스 메소드**로 바꾸는 **데코레이터**. 자바 애노테이션처럼 `@`로 시작하고 함수 정의 윗줄에 붙인다 |
| `cls` | 첫 매개변수. `self`가 인스턴스 자신이었듯 `cls`는 **클래스 자신**(`Student2`)을 가리킨다. 이름은 관례 |
| `cls.students` | `Student2.students`와 같다. 클래스 이름을 직접 적는 대신 `cls`를 쓰면 상속받은 클래스에서도 그 클래스 기준으로 동작한다 |
| `Student2.print()` | 인스턴스를 만들지 않고 **클래스 이름으로 바로 호출** |

일반 메소드는 `students[0].get_sum()`처럼 "어느 학생의"가 정해져야 부를 수 있지만, "명부 전체를 출력한다"는 특정 학생의 일이 아니다. 그래서 `self` 대신 `cls`를 받는 클래스 메소드로 만들고, `cls.students`를 돌며 한 명씩 찍는다. 안에서 `print(str(student))`라고 쓴 것은 1-4의 `__str__`이 있어야 뜻이 통한다. 메소드 이름이 내장 함수와 같은 `print`지만, 클래스 블록 안에서 정의된 것이라 밖의 `print()`를 가리지는 않는다 — 다만 읽는 사람이 헷갈리기 쉬우니 실제 코드에서는 `print_all`처럼 다른 이름이 안전하다.

### 1-4. 특수 메소드 `__str__` — `str(인스턴스)`가 돌려줄 문자열

```python
    def to_string(self):
        return "{} \t {} \t {}".format(self.name, self.get_sum(), self.get_average())

    # 특수한 이름의 메소드 # 보조기능 재정의(오버라이딩)
    def __str__(self):
        return "{} \t {} \t {}".format(self.name, self.get_sum(), self.get_average())

print(str(students[0]))     # __str__ 함수가 실행된다
```

| | `to_string` | `__str__` |
| --- | --- | --- |
| 이름 | 내가 지은 이름 | **파이썬이 정해 둔 이름** |
| 부르는 법 | `student.to_string()`이라고 직접 | `str(student)`·`print(student)`·f-문자열 `{student}`가 **알아서** 부른다 |
| 정의하지 않으면 | 없는 메소드라 `AttributeError` | 기본 `__str__`이 `<__main__.Student2 object at 0x...>`를 돌려준다 |

앞뒤 밑줄 두 개짜리 이름(`__init__`·`__str__`)은 파이썬이 **특정 상황에 자동으로 부르는 메소드**다. `__init__`이 "인스턴스를 만들 때", `__str__`은 "문자열로 바꿀 때"다. 내용은 `to_string`과 글자 하나 다르지 않지만, 이름을 `__str__`로 하면 `print(students[0])`만 쳐도 이름·총점·평균이 나온다. 원래 있던 기본 동작(주소 출력)을 내 것으로 바꿔 끼운다는 뜻에서 주석이 **재정의(오버라이딩)**라고 적어 둔 것이고, 다음 노트의 상속에서 자식이 부모 메소드를 덮어쓰는 것도 같은 말이다.

### 1-5. 비교 특수 메소드 — `==`의 기준을 총점으로 바꾸기

```python
    # 특수한 이름의 메소드 / 비교 메소드 # 총합계 비교 함수 재정의
    def __eq__(self, value):  return self.get_sum() == value.get_sum()
    def __ne__(self, value):  return self.get_sum() != value.get_sum()
    def __gt__(self, value):  return self.get_sum() >  value.get_sum()
    def __ge__(self, value):  return self.get_sum() >= value.get_sum()
    def __lt__(self, value):  return self.get_sum() <  value.get_sum()
    def __le__(self, value):  return self.get_sum() <= value.get_sum()

print(students[0] == students[1])   # True  — 주소는 다른데 __eq__가 실행된다
print(students[0] != students[1])   # False
```

| 연산자 | 특수 메소드 | 이름의 뜻 |
| --- | --- | --- |
| `==` | `__eq__` | equal |
| `!=` | `__ne__` | not equal |
| `>` | `__gt__` | greater than |
| `>=` | `__ge__` | greater or equal |
| `<` | `__lt__` | less than |
| `<=` | `__le__` | less or equal |

`students[0] == students[1]`을 치면 파이썬은 사실 `students[0].__eq__(students[1])`을 부른다. 왼쪽 인스턴스가 `self`, 오른쪽이 `value`로 들어간다. 기본 `__eq__`는 **같은 인스턴스인가(주소가 같은가)**를 보기 때문에 따로 만든 두 학생은 `False`여야 하는데, 여기서는 **총점이 같은가**로 바꿔 정의했으므로 점수가 같은 두 학생은 `True`가 된다. `!=`도 마찬가지로 `False`. 이렇게 하면 `students[0] > students[1]`로 성적을 바로 비교하고, 뒤에서 보듯 `sorted(students)`로 총점순 정렬도 된다. day01에서 비교 연산자가 `bool`을 돌려준다고 적었는데, 내 클래스에서도 그 규칙을 지키려면 **여섯 메소드가 전부 참·거짓을 반환**해야 한다.

## 2. 추가로 알면 좋은 활용법

### 2-1. 클래스 변수를 `self.`로 읽을 때의 함정

```python
print(students[0].count)    # 6 — 읽기는 된다 (인스턴스에 없으면 클래스에서 찾는다)
students[0].count = 100     # 이건 인스턴스 변수 count를 새로 만드는 것
print(Student2.count)       # 6 — 클래스 변수는 그대로
```

`self.count`로 **읽으면** 인스턴스에 그 이름이 없을 때 클래스 변수를 찾아 주지만, `self.count = ...`로 **쓰면** 그 인스턴스에만 있는 새 변수가 생기고 클래스 변수는 변하지 않는다. 그래서 수업 코드가 `Student2.count += 1`처럼 **클래스 이름으로 써서** 갱신한 것이다. 공유 값은 읽기도 쓰기도 `클래스명.`(또는 `cls.`)으로 통일하는 편이 안전하다. 특히 `students = []`처럼 **가변 자료형**을 클래스 변수로 두면 모든 인스턴스가 같은 리스트를 공유하므로, 인스턴스별 목록이 필요하면 `__init__`에서 `self.items = []`로 따로 만들어야 한다.

### 2-2. `__repr__` — 리스트 안에서도 보이게

```python
    def __repr__(self):
        return f"Student2({self.name!r}, {self.korean}, {self.math}, {self.engligh}, {self.science})"

print(students)     # [Student2('윤인성', 87, 98, 88, 85), ...]
```

`__str__`은 `print(student)`에는 쓰이지만 `print(students)`처럼 **리스트째로 찍을 때**는 요소마다 `__repr__`이 쓰인다. `__repr__`은 "다시 만들 수 있는 코드 모양"으로, `__str__`은 "사람이 읽기 좋은 모양"으로 두는 것이 관례다. 하나만 정의한다면 `__repr__`을 두는 편이 낫다 — `__str__`이 없으면 `__repr__`을 대신 쓰기 때문이다.

### 2-3. `functools.total_ordering` — 여섯 개 대신 두 개

```python
from functools import total_ordering

@total_ordering
class Student2:
    def __eq__(self, other): return self.get_sum() == other.get_sum()
    def __lt__(self, other): return self.get_sum() <  other.get_sum()
    # __ne__, __gt__, __ge__, __le__ 는 자동으로 채워진다
```

비교 여섯 개를 전부 쓰면 같은 식이 여섯 번 반복된다. `@total_ordering` 데코레이터를 붙이고 `__eq__`와 나머지 중 하나(`__lt__` 등)만 정의하면 나머지를 만들어 준다. 데코레이터를 클래스에도 붙일 수 있다는 예이기도 하다.

### 2-4. 비교를 정의했으니 정렬과 최댓값이 된다

```python
best = max(students)                 # __gt__ 기준으로 총점 1등
ranked = sorted(students, reverse=True)
```

`sorted`·`max`·`min`은 요소끼리 `<`로 비교하므로 `__lt__`가 있으면 `key=`를 주지 않아도 동작한다. day03 콜백 노트에서는 `key=lambda s: s.get_sum()`으로 기준을 밖에서 줬는데, 오늘은 기준을 **클래스 안에 넣어** 어디서 정렬하든 같은 기준이 쓰이게 한 셈이다. 다만 `__eq__`를 재정의하면 인스턴스가 **해시 불가능**해져 `set`에 넣거나 딕셔너리 키로 쓸 수 없게 되는데, 필요하면 `__hash__`도 함께 정의한다.

### 2-5. 자바와 나란히 — 대응표

| 파이썬 | 자바 | 메모 |
| --- | --- | --- |
| 클래스 블록의 `count = 0` | `static int count = 0;` | 클래스에 하나 |
| `@classmethod` + `cls` | `static` 메소드 | 자바 `static` 메소드에는 `cls`에 해당하는 것이 없다 |
| `__str__` | `toString()` | `print(obj)`·`"" + obj`가 자동 호출 |
| `__eq__` | `equals(Object o)` | 자바는 `==`가 주소 비교로 고정, 파이썬은 `==` 자체가 바뀐다 |
| `__lt__` 등 | `Comparable.compareTo` | 자바는 메소드 하나로 세 경우, 파이썬은 연산자별 |
| `isinstance(x, C)` | `x instanceof C` | 둘 다 자식 클래스까지 참 |
| `@데코레이터` | `@애노테이션` | 모양은 같지만 파이썬 데코레이터는 **함수를 감싸는 함수**로 실제 동작을 바꾼다 |

## 3. 더 나아가 알면 좋은 것

- **던더 메소드 전체 지도** — `__len__`(`len(obj)`), `__getitem__`(`obj[i]`), `__iter__`(`for`에 올리기), `__call__`(`obj()`), `__add__`(`+`), `__contains__`(`in`), `__bool__`(참·거짓 판정). 내 클래스를 리스트처럼 보이게 만드는 길
- **`@staticmethod`** — `self`도 `cls`도 받지 않는 메소드. 클래스와 관련은 있지만 어느 쪽 상태도 안 쓰는 도우미 함수에 붙인다. `@classmethod`와의 차이가 면접 단골
- **데코레이터의 정체** — `@classmethod`는 `print = classmethod(print)`의 줄임말이다. 함수를 받아 함수를 돌려주는 고차 함수(day03 콜백 노트의 심화 키워드)로, 직접 만들면 로그·실행 시간 측정·권한 검사를 끼워 넣을 수 있다 — 관점지향(AOP)이 이것으로 구현된다
- **`__hash__`와 `__eq__`의 약속** — `__eq__`가 같다고 하는 두 객체는 `__hash__`도 같아야 한다. 어기면 `set`·`dict`가 이상하게 동작한다
- **`dataclass(order=True)`** — 필드 선언만으로 `__eq__`와 비교 네 개를 필드 순서 기준으로 만들어 준다
- **클래스 변수로 레지스트리 만들기** — `students.append(self)` 패턴은 플러그인 등록, 싱글턴, 인스턴스 캐시에 쓰이는 기본형이다. 다만 인스턴스가 영영 해제되지 않으므로 `weakref`를 알아 둘 필요가 있다

### 다음에 볼 키워드

- 던더 메소드, `__repr__`, `__hash__`, `@staticmethod`, 데코레이터 직접 만들기, `total_ordering`, `dataclass(order=True)`

## 실습 파일

- `KDT_2026/2026_Python/day05/c8-2.py` (앞부분) — 생성자만 있는 `Student`·`Human` 두 클래스로 `isinstance(student, Student)`(`True`)·`isinstance(student, Human)`(`False`) 확인, `Student2`에 클래스 변수 `count = 0`·`students = []`를 두고 `__init__`에서 `Student2.count += 1`·`Student2.students.append(self)`로 세기·모으기, `@classmethod def print(cls)`로 `cls.students`를 돌며 `str(student)` 출력, `__str__` 재정의로 `str(students[0])`이 이름·총점·평균 문자열을 돌려주는 것 확인, `__eq__`·`__ne__`·`__gt__`·`__ge__`·`__lt__`·`__le__`를 총점 비교로 재정의해 `students[0] == students[1]`이 `True`·`!=`가 `False`, `Student2.count`(6)·`Student2.print()` 호출. 뒷부분(프라이빗 변수·상속)은 다음 노트

## 관련 노트

[[Python 정리본 인덱스]] · [[Python day05 클래스 정의와 생성자·메소드]] · [[Python day05 프라이빗 변수·property와 상속]] · [[Python day03 콜백 함수와 map·filter·람다]] · [[Python day02 딕셔너리 연습문제 풀이]] · [[KDT_2026 학습 지도]]
