---
출처: Claude 분석
작성일: 2026-08-21
tags: [코드정리]
---

# JS 배열 메소드 심화

> 상위: [[JS 객체와 배열]]

## reduce — 하나로 접기 ※

```javascript
const total = cart.reduce((sum, item) => sum + item.price, 0);

const byCategory = books.reduce((acc, b) => {
    (acc[b.category] ??= []).push(b);
    return acc;
}, {});
```

- `reduce((누적값, 요소) => 새 누적값, 초기값)` — 배열을 값 하나로 접는다. 합계·개수·그룹핑이 전부 이걸로 된다
- 읽는 법: 초기값 0에서 시작해 요소를 하나씩 누적한다. 자바 스트림의 `sum()`·`groupingBy` 자리다
- 두 번째 예처럼 객체를 누적하면 "카테고리별로 묶기"가 된다(`??=`는 없으면 빈 배열 만들기)

## some · every ※

```javascript
const hasOverdue = rentals.some(r => r.overdue);
const allReturned = rentals.every(r => r.returned);
```

- `some`은 하나라도 조건에 맞으면 true(자바 anyMatch), `every`는 전부 맞아야 true(allMatch)
- for + flag 변수 + break 패턴이 한 줄로 줄어든다

## slice · concat · join · flat ※

```javascript
const page = list.slice(0, 10);
const copy = list.slice();
const all = a.concat(b);
const csv = names.join(", ");
const flatList = nested.flat();
```

- `slice(시작, 끝)`은 잘라낸 **새 배열**(원본 유지 — splice와 반대), 인수 없이 부르면 복사다
- `join(구분자)`은 배열→문자열(자바 String.join), `flat()`은 중첩 배열 펼치기
- 페이지네이션이 `slice((page-1)*size, page*size)` 한 줄이다

## forEach와 만들기 유틸 ※

```javascript
list.forEach((item, i) => console.log(i, item));

Array.from({ length: 5 }, (_, i) => i + 1);
new Array(3).fill(0);
```

- `forEach`는 반환 없이 돌기만 한다(값을 모으려면 map). 콜백 둘째 인수로 인덱스가 온다
- `Array.from({length: n}, (_, i) => ...)`은 "n개짜리 배열을 규칙으로 생성"하는 관용구다. `_`는 "안 쓰는 인수"라는 표시다

## 체이닝

```javascript
const top5 = books
    .filter(b => b.stock > 0)
    .sort((a, b) => b.sales - a.sales)
    .slice(0, 5)
    .map(b => b.title);
```

- 전부 새 배열을 돌려주므로 점으로 이어진다. 읽는 법: "재고 있는 것만 → 판매순 정렬 → 앞 5개 → 제목만"
- 자바 스트림과 같은 사고방식인데 stream() 열기·toList() 닫기가 없이 바로 이어진다
