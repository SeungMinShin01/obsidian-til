---
출처: Claude 대화
작성일: 2026-11-16
tags: [프로젝트, javascript, react]
---

# AiOps - 콘솔 에러 목록 화면

> 허브: [[AiOps 프로젝트 MOC]]

**PR #70 `[AI-99] React 뼈대 2부-1: 에러 목록 화면`** — 커밋 9개(새 파일 5, 고친 파일 4) + develop 병합 1개, 11/16 머지. 시안의 에러 목록을 가짜 응답으로 그린다. 실서버 확인·상태 버튼·연결 배지는 김지환의 AI-100.

## 1. 배운 내용

### 1-1. 데이터가 화면까지 오는 길

```
ErrorList.jsx (화면)
  └ useErrorGroups(teamId, filter)        hooks/   TanStack Query가 불러오기·기억·다시 부르기를 맡는다
       └ getErrorGroups(teamId, filter)   api/     주소를 만들고 request()를 부른다
            └ request('GET', ...)         api/client.js   쿠키·401·403
                 └ (dev:mock이면) mocks/handlers.js가 가로채서 가짜 응답
```

화면은 "어디서 오는 데이터인지" 모른다. 가짜 응답을 진짜 서버로 바꿀 때 화면 파일을 고치지 않는다.

### 1-2. 코드로 보기: 조건을 주소에 둔다

```jsx
const [search, setSearch] = useSearchParams();
const filter = readFilter(search);            // 주소 → 조건

const change = (name, value) => {
  const next = new URLSearchParams(search);
  next.set(name, String(value));
  if (name !== "page") next.delete("page");   // 조건을 바꾸면 첫 쪽으로
  setSearch(next, { replace: true });
};
```

- `useState`에 두면 상세를 보고 뒤로 왔을 때 조건이 처음으로 돌아간다. 주소(`?env=local&status=RESOLVED`)에 두면 남는다. 주소를 복사해 팀원에게 주면 같은 화면이 뜬다.
- 주소는 사람이 고칠 수 있다. `readFilter`는 허용값이 아니면 기본값으로 바꾼다(`?days=999` → 7). 서버도 한 번 더 검사한다(400).
- `replace: true`: 조건을 바꿀 때마다 뒤로 가기 기록이 쌓이지 않게.

### 1-3. 코드로 보기: 조건이 Query 키에 들어간다

```js
errors: (teamId, filter) => ["teams", teamId, "errors", filter],
```

TanStack Query는 키가 같으면 기억해 둔 것을 쓰고, 다르면 새로 부른다. 조건을 키에 넣었으므로 "조건이 바뀌면 다시 불러라"를 따로 쓰지 않는다. `placeholderData: keepPreviousData`는 새 목록이 올 때까지 이전 목록을 보여 줘서 화면이 깜빡이지 않게 한다.

### 1-4. 표와 카드를 둘 다 그리고 CSS로 하나를 숨긴다

넓은 화면은 표(`wide-only`), 720px 이하는 카드(`narrow-only`). 표 하나를 CSS로 카드처럼 바꾸는 방법도 있지만, 표의 뜻(머리글·칸)이 깨져서 화면 낭독기에 이상하게 읽힌다. 같은 데이터를 두 번 그리는 쪽이 코드는 길어도 읽기 쉽다.

### 1-5. 서버 값과 화면 글자를 나눈다 (`app/format.js`)

서버 값 `local`·`OPEN`·`dev.shop.order.OrderService#place`는 그대로 주고받고, 화면에 낼 때만 "로컬"·"열림"·"OrderService 클래스의 place 메서드"로 바꾼다. 바꾸는 곳이 한 파일이라 상세·설정 화면도 같은 말을 쓴다.

### 1-6. 칸 너비는 짧은 칸만 정한다

```css
.error-table th:nth-child(2) { width: 96px; }   /* 환경 */
.error-table th:nth-child(3) { width: 88px; }   /* 횟수 */
```

표는 칸 너비를 안 정하면 브라우저가 남는 폭을 모든 칸에 나눠 준다. 짧은 칸(환경·횟수·상태)까지 넓어져서 칸 사이가 멀어진다. 짧은 칸만 너비를 정하면 남는 폭은 전부 긴 칸("에러")이 가져간다. 실제 모니터에 띄워 보기 전에는 몰랐던 문제다 — 시안은 한 가지 폭으로만 그렸다.

## 2. 실수 기록

- `format.js`를 `src/app/`이 아니라 `src/api/`에 만들었다. 화면은 `../app/format`을 찾으므로 뜨지 않는다. **lint는 통과했다** — ESLint 기본 규칙은 "가져오는 파일이 실제로 있는지"를 보지 않는다. `npm run build`나 화면을 직접 띄워야 잡힌다.
- 그래서 커밋 전 확인은 lint만으로 끝내지 않는다: `npm run dev:mock`으로 화면 → `npm run build`.

- PR을 기다리는 사이 조현우의 팀 설정 화면(PR #69)이 먼저 머지돼 세 파일이 충돌했다. `queryKeys.js`·`handlers.js`는 같은 자리에 줄을 추가해서, `format.js`는 **두 사람이 같은 이름의 파일을 각자 새로 만들어서**다. 셋 다 "둘 다 남기기"로 풀었다. 그 결과 `format.js`에 비슷한 함수가 두 벌 남았다(`envLabel`/`ENV_LABEL`, `timeAgo`/`formatWhen`). 공통 파일을 새로 만들 때는 먼저 "누가 만들지"를 정하면 피할 수 있었다

## 3. 시안과 다른 점

| 시안 | 실제 | 이유 |
|---|---|---|
| "열림 5 · 해결 1 · 최근 7일" | "조건에 맞는 에러 N건" | 목록 API는 지금 조건의 개수(`totalElements`)만 준다 |
| 목록의 "시작 실패" 표시 | 없음 | `phase`가 목록 응답에 없다 (잠정) |
| 왼쪽 팀 목록의 "열린 에러 N" | 없음 | `/api/me`에 그 값이 없다 |
| 연결 배지 | 없음 | AI-100에서 붙인다 |
| 내용 최대 폭 1160px | 1440px, 표의 뒤쪽 네 칸은 너비 고정 | 시안은 1280px 화면 기준이었다. 1900px 모니터에서는 오른쪽이 통째로 비고 "에러"와 "환경" 칸 사이가 벌어졌다 |

## 관련 노트

[[AiOps 42 - 콘솔 뼈대 (React)]] · [[AiOps 43 - 설명 재시도 최소 나이]] · [[AiOps 45 - 콘솔 에러 상세 화면]]
