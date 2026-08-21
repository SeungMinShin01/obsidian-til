---
출처: Claude 분석
작성일: 2026-08-21
tags: [코드정리]
---

# JS 형변환과 비교

> 상위: [[JS 기본 문법]]

## == 와 === 

```javascript
1 == "1";
1 === "1";
0 == false;
null == undefined;
```

- `==`는 타입이 다르면 **멋대로 변환해서** 비교한다. 위 세 줄이 전부 true라 버그의 온상이다
- `===`는 타입까지 같아야 true다. 항상 이걸 쓴다
- 쿼리스트링·prompt에서 온 값은 문자열이라 `url.get("no") === 3`은 false다 — `Number()`로 바꾸고 비교한다

## 명시적 형변환

```javascript
Number("42");
parseInt("42px");
parseFloat("3.14");
String(42);
(42).toString();
Boolean(1);
```

- `Number()`는 전체가 숫자여야 하고 아니면 NaN, `parseInt`는 앞에서부터 읽을 수 있는 만큼 읽는다("42px"→42)
- 숫자→문자열은 `String()` 또는 템플릿 리터럴 `` `${n}` ``이 편하다

## truthy · falsy

```javascript
if (!title) {
    alert("제목을 입력하세요.");
    return;
}
```

- 조건 자리에서 거짓 취급되는 값(falsy)은 정확히 7개다: `false` `0` `-0` `""` `null` `undefined` `NaN`
- 나머지는 전부 참(truthy)이다. 빈 배열 `[]`, 빈 객체 `{}`도 truthy라는 게 함정이다
- `if (!title)` 한 줄이 "빈 문자열·null·undefined 전부 거르기"가 되는 이유가 이것이다 — 입력 검증의 관용구

## NaN

```javascript
Number("abc");
NaN === NaN;
Number.isNaN(x);
```

- 숫자 변환 실패의 결과가 NaN이다. **자기 자신과도 같지 않은 유일한 값**이라 `=== NaN` 검사는 항상 false다
- NaN 검사는 반드시 `Number.isNaN()`으로 한다. 계산 결과가 이유 없이 NaN이면 어딘가에서 문자열이 숫자 연산에 섞인 것이다
