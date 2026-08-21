---
출처: Claude 분석
작성일: 2026-08-21
tags: [코드정리]
---

# JS 객체 심화

> 상위: [[JS 객체와 배열]]

전부 ※. 객체를 "데이터 덩어리"로 다루는 유틸들이다.

## Object.keys · values · entries

```javascript
const price = { americano: 4500, latte: 5000 };

Object.keys(price);
Object.values(price);
Object.entries(price);

for (const [name, won] of Object.entries(price)) {
    console.log(`${name}: ${won}원`);
}
```

- keys 키 배열, values 값 배열, entries `[키, 값]` 쌍 배열 — 객체를 배열 메소드의 세계로 데려가는 다리다
- entries + 구조 분해 for...of가 객체 순회의 표준형이다(for...in보다 안전하고 읽기 좋다)
- 합계 같은 계산: `Object.values(price).reduce((s, v) => s + v, 0)`

## 동적 키

```javascript
const field = "title";
post[field] = "새 제목";

const obj = { [field]: "값", [`${field}Length`]: 3 };
```

- 키가 변수에 들어 있으면 대괄호로 접근·생성한다. `{ [식]: 값 }`(계산된 속성명)은 리터럴 안에서 키를 동적으로 만드는 문법이다
- 폼 입력 여러 개를 하나의 객체로 모을 때 `data[input.name] = input.value` 패턴으로 자주 쓴다

## 병합과 복사

```javascript
const defaults = { page: 1, size: 10 };
const options = { ...defaults, ...userOptions };

const clone = structuredClone(post);
```

- 스프레드 병합은 **뒤에 온 것이 이긴다** — 기본값을 앞에, 사용자 값을 뒤에 두면 "기본값 + 덮어쓰기"가 된다
- 스프레드·Object.assign은 얕은 복사다. 중첩 객체까지 완전 분리하려면 structuredClone

## 존재 확인과 정리

```javascript
"title" in post;
post.hasOwnProperty("title");
post.title !== undefined;

const { pwd, ...safe } = post;
```

- 속성 존재 확인 세 가지 — `in`이 가장 단순하다. 값이 undefined일 수도 있는 속성은 `in`으로 구분한다
- 구조 분해 + rest로 **특정 속성만 뺀 사본**을 만든다 — 비밀번호 빼고 넘기기의 관용구다
