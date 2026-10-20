---
출처: Claude 분석
작성일: 2026-08-10
tags: [허브, python]
---

# Python 정리본 인덱스

Python 정리본이 모이는 폴더입니다. 상위 지도는 [[KDT_2026 학습 지도]].
실제 프로젝트에서 Python이 쓰인 지점(크롤러 등)은 [[KDT_2026 학습 지도]]의 **프로젝트 매핑표**에서 찾습니다 (프로젝트 분석 노트와 직접 링크하지 않습니다).

## 프로젝트 매핑 — 학습 지도 ↔ 이 폴더

[[KDT_2026 학습 지도]]를 거쳐 들어온 경우, 프로젝트의 해당 주제는 이 노트들과 닿습니다. (프로젝트 쪽은 평문 — 직접 링크하지 않음)

| 프로젝트에서 만난 것 | 이 폴더의 이론 |
| --- | --- |
| Selenium 크롤러의 dict 병합(멱등), 리스트 컴프리헨션 | [[Python 코드 해석 문제(이관)]] |


## 수업 노트 (2026_Python, day 순서)

| day | 주제 | 노트 |
| --- | --- | --- |
| day01 | **파이썬 시작과 키워드 확인** — VS Code 한 줄 실행(`Shift+Enter`)·전체 실행, `print`, `#` 주석, `import keyword`·`keyword.kwlist`로 예약어 목록 보기, `type()`으로 자료형 확인, 따옴표 세 종류와 제어문자, 문자열 연산(연결·반복·인덱싱·슬라이싱·`len`), 숫자 연산자(`/`·`//`·`%`·`**`)와 우선순위, 변수와 복합대입연산자, `input()`과 `int()`·`float()`·`str()` 형변환, `format()`으로 값 끼워 넣기, 문자열 메소드(`upper`·`lower`·`strip`·`isalpha`·`isdigit`·`find`·`rfind`·`in`·`split`), f-문자열 vs `format()` | [[Python day01 파이썬 시작과 키워드 확인]] |
| day01 | **비교·논리 연산자와 if 조건문** — `==`·`!=`·`<`·`>=` 비교, `10 < x < 30` 범위 비교, `not`·`and`·`or`, `if`·`else`와 콜론·들여쓰기 블록, `if`·`elif`·`else`로 등급 나누기(좁은 조건부터), `if` 나열 vs `elif`(전부 검사·하나만 실행), `if` 중첩(`else`의 짝은 들여쓰기 깊이), 참·거짓 판정(빈 값은 거짓)·`in`·`is None`·조건부 표현식·`pass` | [[Python day01 비교·논리 연산자와 if 조건문]] |
| day02 | **리스트 선언과 인덱싱·슬라이싱** — 대괄호에 쉼표로 나열한 리스트(자료형 혼합·가변 길이, 자바 배열과 차이), 요소·인덱스 용어, 인덱싱(`[2]`)·슬라이싱(`[1:3]`, 끝 미포함·새 리스트), 요소 값 수정(문자열은 불변·리스트는 가변), 음수 인덱스(`[-2]`), 문자열 요소의 이중 인덱싱(`[3][1]`)과 정수 요소 인덱싱 불가, 1차원·2차원·3차원 리스트와 `[행][열]` 읽기(판다스로 이어지는 자리), 리스트 연결(`+`)·반복(`*`)·`len`과 요소가 리스트인 리스트를 붙일 때 펴지지 않는 점, `append`(원본 변경·반환 `None`), `insert`와 `+` vs `append`(새 리스트 vs 원본 변경), `del`·`pop`·`remove`·`clear`(인덱스·슬라이스·값으로 삭제), 슬라이싱 세 번째 칸(`[1:5:2]`·`[::-1]`), `sort()`·`reverse=True`, `in`·`not in`, 리스트·문자열을 도는 `for`(자바 향상된 for), `extend`·`sorted`·`enumerate`·`range`·슬라이스 대입, 별명과 복사(`[:]`·얕은 복사), 튜플, 리스트 컴프리헨션 | [[Python day02 리스트 선언과 인덱싱·슬라이싱]] |
| day02 | **딕셔너리 선언과 키로 값 다루기** — 중괄호 `{키: 값}`(키 중복 불가·값 자유, JS JSON / Java Map / DB 레코드 대응), 대괄호로 값 호출(`KeyError`, 인덱스 없음), 없는 키 대입으로 추가·있는 키 대입으로 수정(같은 문법·오타 주의), `del`로 쌍 삭제, `in`은 키 확인, 대괄호 vs `get`(`KeyError` vs `None`·기본값), `for`로 돌리면 키가 나옴, `keys()`·`values()`·`items()`, 리스트 안의 딕셔너리(API 응답 모양), `setdefault`·`update`·`pop`, 횟수 세기 패턴, 해시·딕셔너리 컴프리헨션·`zip`·`set`·`json` | [[Python day02 딕셔너리 선언과 키로 값 다루기]] |
| day02 | **리스트·반복문 연습문제 풀이** — 교재 213~215쪽 확인문제: 리스트 메소드 여섯 개(`extend`·`append`·`insert`·`remove`·`pop`·`clear`) 결과 예측과 값·자리·반환값 구분, `for` 안 `if` 조건식으로 100 이상만 골라내기, `% 2`로 홀짝·`/ 10` 범위 비교와 `elif`로 자릿수 판정(큰 값부터 좁히기·`pass`), `output[number % 3 - 1].append`로 2차원 리스트에 나눠 담기(음수 인덱스), `range(0, len // 2)`의 `i`로 `j = i*2+1` 홀수 인덱스를 만들어 `** 2` 제자리 대입, 다른 풀이(`len(str(i))`·`(n-1) % 3`·`range(1, len, 2)`)·컴프리헨션·`enumerate`, 나머지 연산과 버킷·제자리 수정 vs 새 리스트 | [[Python day02 리스트·반복문 연습문제 풀이]] |
| day02 | **range 함수와 for·while 반복문** — `range(끝)`·`range(시작, 끝)`·`range(시작, 끝, 단계)`(슬라이싱과 같은 끝 미포함 규칙), `print(range(5))`가 `range(0, 5)`로 찍히는 범위 객체와 `list()` 변환, `for i in range(1, 11)`로 1~10·`range(10, 0, -1)`로 거꾸로·`range(1, 11, 2)`로 홀수만(자바 `for` 세 칸 ↔ `range` 세 인자), `while 조건식:`의 구조(변수 준비·조건 검사·`i += 1`)와 경계 조건·무한 루프 주의, `for`+`range` vs `while` 고르기, `range(len())`·`reversed`·`in`·`len`, `sum(range())`·컴프리헨션, `break`·`continue`·`while True`, `while stack:` 수렴·누적, 지연 평가와 반복자, `for … else`·`itertools`, 자바 대응표(`do-while` 없음) | [[Python day02 range 함수와 for·while 반복문]] |
| day02 | **집계 함수와 reversed·enumerate 이터레이터** — `min`·`max`·`sum`으로 리스트를 돌지 않고 집계(원본 불변·새 값 반환), `reversed()`가 리스트가 아닌 `<list_reverseiterator object>`를 돌려주는 것과 `next()`로 하나 꺼낸 뒤 `list()`에 남은 요소만 담기는 소진 성질(`reverse()`·`[::-1]`·`reversed()` 비교), `int()`·`float()`·`str()`·`list()` 변환 함수, 이터러블(꺼낼 수 있는 자료)·이터레이터(하나씩 빼내는 객체)·`next()`와 `for`에 쓸 수 있는 자료(문자열·리스트·튜플·딕셔너리·`range`), `enumerate()`의 `(인덱스, 값)` 튜플과 `for index, value in …` 풀어 받기, `dict.items()`의 `(키, 값)`과 같은 모양, `key=`·`default=`·`start=`·`zip`, `next` 기본값과 한 번만 쓰는 이터레이터, `items()`·`sorted`·`enumerate`로 순위표, `iter`·`next`·`StopIteration`으로 본 `for`의 실체, 제너레이터(`yield`)·`any`·`all`·`reduce` | [[Python day02 집계 함수와 reversed·enumerate 이터레이터]] |
| day02 | **딕셔너리 연습문제 풀이** — 교재 227~229쪽 확인문제: 빈 딕셔너리에 키 대입으로 쌍 추가·`del`로 삭제(추가 메소드 없이 대괄호+키), 리스트 안 딕셔너리(`pets`)를 `for`로 돌며 `pet['name']`·`pet['age']`를 f-문자열에 대괄호 식 그대로 넣어 출력(따옴표 종류 바꾸기), 빈 `counter`에 `if number in counter`로 키 유무를 가려 `+= 1`·`= 1`로 등장 횟수 쌓기(키=숫자·값=횟수, `in`은 키 확인), `get(키, 0)`·`setdefault`·`collections.Counter`로 줄이기, `get` 대체값과 `items()` 풀어 받기, `sorted`로 키·값 기준 정렬 출력, 해시로 세는 이유(O(1))·판다스 `DataFrame`·`value_counts` | [[Python day02 딕셔너리 연습문제 풀이]] |

## 이관된 내용

정보처리기사 노트에 흩어져 있던 Python 문제 풀이를 이 폴더로 모았습니다.

- Python 코드 해석 문제(이관) — 문자열 슬라이싱·제너레이터 표현식, 리스트 컴프리헨션·얕은 복사

## 앞으로 채울 주제 (제안)

- 기본 문법 — 자료형, 제어문, 함수
- 자료구조 — list / tuple / dict / set
- 컴프리헨션과 제너레이터
- 클래스와 모듈
- 표준 라이브러리 — `os`, `pathlib`, `datetime`, `json`, `re`
- 자동화 실습 — RPA 폴더와 연계

## 관련 노트

[[KDT_2026 학습 지도]] · [[Python day01 파이썬 시작과 키워드 확인]] · [[Python day01 비교·논리 연산자와 if 조건문]] · [[Python day02 리스트 선언과 인덱싱·슬라이싱]] · [[Python day02 딕셔너리 선언과 키로 값 다루기]] · [[Python day02 리스트·반복문 연습문제 풀이]] · [[Python day02 range 함수와 for·while 반복문]] · [[Python day02 집계 함수와 reversed·enumerate 이터레이터]] · [[Python day02 딕셔너리 연습문제 풀이]] · [[Python 코드 해석 문제(이관)]]


