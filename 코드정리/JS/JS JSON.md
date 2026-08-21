---
출처: Claude 분석
작성일: 2026-08-21
tags: [코드정리]
---

# JS JSON

> 상위: [[JS 객체와 배열]]

## stringify · parse

```javascript
const text = JSON.stringify(list);
const back = JSON.parse(text);

const pretty = JSON.stringify(obj, null, 2);
```

- JSON은 객체·배열을 **문자열로** 표현하는 형식이다. 저장·전송은 문자열만 되기 때문에 이 변환이 필요하다
- `stringify` 객체→문자열, `parse` 문자열→객체. 항상 짝으로 다닌다
- `stringify(obj, null, 2)`는 들여쓰기 2칸으로 예쁘게 — 디버깅 출력용

## localStorage와 세트

```javascript
localStorage.setItem("boardList", JSON.stringify(list));
const list = JSON.parse(localStorage.getItem("boardList") ?? "[]");
```

- localStorage는 문자열만 저장하므로 넣을 때 stringify, 꺼낼 때 parse가 강제다
- `?? "[]"`는 저장된 게 없을 때(null) 빈 배열 문자열로 대체하는 관용구다 — 첫 실행에도 안 터진다

## JSON 형식 규칙

```json
{ "no": 1, "title": "제목", "tags": ["a", "b"], "done": false }
```

- 키는 반드시 큰따옴표, 값은 문자열·숫자·boolean·null·배열·객체만 된다
- 함수·undefined는 JSON이 될 수 없다 — stringify하면 그 속성이 조용히 사라진다
- 백엔드 API의 요청·응답 본문이 전부 이 형식이다. fetch를 배우면 그대로 이어진다

## 깊은 복사 트릭과 한계 ※

```javascript
const deep = JSON.parse(JSON.stringify(obj));
const better = structuredClone(obj);
```

- stringify→parse 왕복이 중첩까지 복사하는 고전 트릭이다. 단 함수·undefined·Date가 깨진다
- 요즘은 표준 함수 `structuredClone`이 있어 그쪽이 안전하다
