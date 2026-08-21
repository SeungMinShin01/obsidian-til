---
출처: Claude 분석
작성일: 2026-08-21
tags: [코드정리]
---

# HTML 폼 검증

> 상위: [[HTML 폼]]

전부 ※. JS를 쓰기 전에 HTML 속성만으로 걸 수 있는 1차 검증이다.

## 검증 속성

```html
<input type="text" required maxlength="50">
<input type="number" min="1" max="10">
<input type="password" minlength="4" required>
<input type="text" pattern="[0-9]{3}-[0-9]{4}-[0-9]{4}" placeholder="010-0000-0000">
<input type="email" required>
```

- `required` 빈 값 제출 차단, `minlength`/`maxlength` 글자 수, `min`/`max` 숫자 범위
- `pattern`은 정규표현식 검사다(전화번호·아이디 형식). `type="email"`은 이메일 모양 검사가 내장돼 있다
- 폼을 submit하는 순간 브라우저가 자동 검사하고 말풍선 안내까지 띄운다 — 공짜 검증층이다

## 상태 속성

```html
<input type="text" value="기본값">
<input type="text" placeholder="힌트 문구">
<input type="text" readonly>
<input type="text" disabled>
```

- `value`는 실제 값, `placeholder`는 비어 있을 때 보이는 힌트일 뿐이다 — placeholder는 제출돼도 값이 아니다
- readonly는 수정만 금지(값은 제출됨), disabled는 아예 비활성(값 제출도 안 됨) — 이 차이로 골라 쓴다

## CSS와 연동

```html
<style>
input:invalid { border-color: red; }
input:valid { border-color: green; }
</style>
```

- 검증 속성을 걸어두면 `:invalid`/`:valid` 가상 클래스로 실시간 색 표시가 된다. JS 없이 시각 피드백까지 가능하다

## 한계 — 서버 검증은 별개

- HTML 검증은 개발자도구로 속성만 지우면 우회된다. **최종 검증은 항상 서버(백엔드) 몫**이고, HTML·JS 검증은 사용자 편의를 위한 1차 필터다
- 검증을 여러 겹 두는 구조: HTML 속성 → JS(조기 반환) → 서버/DB 제약조건
