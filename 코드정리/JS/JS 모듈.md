---
출처: Claude 분석
작성일: 2026-08-21
tags: [코드정리]
---

# JS 모듈

> 상위: [[JS 패턴]]

전부 ※. script 여러 개 이어 붙이기를 졸업하고 파일 간 의존을 명시하는 방법이다.

## export · import

```javascript
// storage.js
export const KEY = "boardList";

export function getBoardList() {
    return JSON.parse(localStorage.getItem(KEY) ?? "[]");
}

export default function saveBoardList(list) {
    localStorage.setItem(KEY, JSON.stringify(list));
}
```

```javascript
// write.js
import saveBoardList, { KEY, getBoardList } from "./storage.js";
```

- `export`를 붙인 것만 밖에서 보인다 — 파일 자체가 캡슐이 되고, 안 내보낸 내부 함수·변수는 자동으로 private다
- `default`는 파일당 하나뿐인 대표 수출이다. import에서 중괄호 없이 아무 이름으로 받고, 나머지(named)는 중괄호에 **정확한 이름**으로 받는다
- 경로는 `./`로 시작하는 상대경로 + 확장자까지 쓰는 게 브라우저 규칙이다

## HTML에서 켜는 법

```html
<script type="module" src="write.js"></script>
```

- `type="module"`이 있어야 import가 동작한다. 모듈은 자동으로 defer라 body 끝에 안 둬도 된다
- 함정: 모듈은 보안 정책 때문에 **파일을 더블클릭으로 열면(file://) 막힌다.** VSCode의 Live Server 같은 로컬 서버로 띄워야 한다
- 모듈의 변수는 전역에 안 뜬다 — HTML의 `onclick="fn()"`이 못 찾으므로 addEventListener 방식으로 전환하는 것까지가 세트다

## common.js 방식과의 비교

```
script 이어붙이기  →  전역 공유. 순서가 의존을 정하고, 이름 충돌 위험
모듈              →  파일마다 격리. import가 의존을 문서화, 충돌 없음
```

- "누가 누구를 쓰는지"가 import 문에 그대로 보인다는 게 핵심 이득이다 — 파일이 늘수록 차이가 커진다
- 리액트·Node의 코드가 전부 이 문법 위에 있다. import/export를 읽을 줄 알면 그쪽 코드가 바로 열린다
