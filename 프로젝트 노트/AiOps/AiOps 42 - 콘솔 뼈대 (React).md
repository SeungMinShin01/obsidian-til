---
출처: Claude 대화
작성일: 2026-11-16
tags: [프로젝트, javascript]
---

# AiOps - 콘솔 뼈대 (React)

> 허브: [[AiOps 프로젝트 MOC]]

**PR #65 `[AI-99] React 뼈대 1부`** — 커밋 27개, 11/16 머지. 화면 내용은 아직 "준비 중"이고, 그 아래의 바닥(서버 연결, 로그인, 메뉴 틀, 가짜 응답)만 만들었다. 명세와 다르게 한 결정: JavaScript(D-108), axios(D-109), 팀 선택 화면 없음(D-111).

## 1. 배운 내용

### 1-1. 폴더

```
console/src
  api/         서버 호출 (client.js 한 곳을 거친다)
  app/         앱 전체 설정 (queryClient.js, storage.js)
  hooks/       데이터를 가져오는 훅 (useMe)
  components/  여러 화면이 같이 쓰는 부품 (TopBar, TeamSidebar, 레이아웃)
  pages/       주소 하나에 대응하는 화면
  mocks/       가짜 응답 (msw)
```

### 1-2. 코드로 보기: 서버 호출은 한 곳으로 (`api/client.js`)

```js
const http = axios.create({ withCredentials: true });        // ①

if (method !== "GET") {
  const token = csrfToken();                                 // ② XSRF-TOKEN 쿠키를 읽어
  if (token) headers["X-XSRF-TOKEN"] = token;                //    헤더로 되돌린다
}
...
if (status === 401) { window.location.assign("/login"); }    // ③
if (status === 403) { throw new ForbiddenError(403, ...); }  // ④
```

| 번호 | 뜻 |
|---|---|
| ① | 로그인 상태는 세션 쿠키뿐이다(D-020). 쿠키를 같이 보내야 서버가 누구인지 안다 |
| ② | CSRF 방어. 다른 사이트는 우리 쿠키를 **읽을 수 없으므로** 이 헤더를 만들 수 없다. 서버는 쿠키 값과 헤더 값이 같은지 본다 |
| ③ | 세션이 없거나 끝났다 → 로그인 화면 |
| ④ | 권한 판단은 서버가 한다(규칙 13). 화면은 "권한 없음"을 그릴 뿐이다 |

화면에서 axios를 직접 부르지 않는 이유: 위 네 가지를 호출마다 다시 쓰지 않으려고. 한 군데만 빠져도 그 화면만 로그인이 풀린다.

### 1-3. 코드로 보기: 개발 프록시 (`vite.config.js`)

```js
proxy: {
  "/api":          { target: "http://localhost:8080", changeOrigin: false },
  "/oauth2":       { target: "http://localhost:8080", changeOrigin: false },
  "/login/oauth2": { target: "http://localhost:8080", changeOrigin: false },
}
```

개발 중에는 화면(5173)과 서버(8080)의 주소가 다르다. 브라우저는 주소가 다르면 쿠키를 안 보낸다. 프록시는 브라우저가 "전부 5173과 이야기한다"고 믿게 만든다. 그래서 서버에 CORS 설정을 넣지 않는다 — 필요하다고 느끼면 프록시가 틀린 것이다.

`/login` 전체가 아니라 `/login/oauth2`만 넘기는 이유: `/login` 화면은 콘솔이 그리고, GitHub이 돌아오는 주소(`/login/oauth2/code/github`)만 서버가 받는다.

### 1-4. 코드로 보기: 가짜 응답은 개발에서만 (`main.jsx`)

```js
if (import.meta.env.DEV && import.meta.env.VITE_MOCK === "1") {
  const { worker } = await import("./mocks/browser");
  await worker.start({ onUnhandledRequest: "bypass" });
}
```

- `import.meta.env.DEV`는 빌드할 때 `false`로 바뀐다. 조건이 항상 거짓이 되므로 빌드 도구가 이 블록과 `mocks/`를 결과물에서 뺀다.
- `await import(...)`(필요할 때 불러오기)로 쓴 것도 같은 이유다. 맨 위 `import`였다면 빌드에 딸려 들어간다.
- `npm run dev:mock` = `vite --mode mock` → `.env.mock`의 `VITE_MOCK=1`을 읽는다.

### 1-5. 코드로 보기: 4xx는 다시 부르지 않는다 (`app/queryClient.js`)

```js
retry: (failureCount, error) => {
  if (error instanceof ApiError && error.status >= 400 && error.status < 500) return false;
  return failureCount < 2;
}
```

TanStack Query는 실패하면 기본으로 3번 다시 부른다. 401·403·404는 다시 불러도 같은 답이라 화면만 늦게 뜬다. 서버 오류(5xx)와 연결 실패(0)만 2번 더 시도한다.

### 1-6. 브라우저에 저장하는 것 (`app/storage.js`)

목록이 접혔는지, 마지막에 본 팀 번호. 이 둘뿐이다. 토큰·로그인 정보는 두지 않는다. `try/catch`로 감싼 이유: 사생활 보호 모드처럼 저장소를 못 쓰는 브라우저에서도 화면은 떠야 한다.

마지막 팀 번호는 **편의 값**이다. `Teams.jsx`는 그 번호가 지금 내 팀 목록(`/api/me`)에 있을 때만 쓴다. 번호를 바꿔 넣어도 서버가 막는다.

## 2. 설계와 다른 점

| 명세 (AI-99) | 실제 | 이유 |
|---|---|---|
| TypeScript | JavaScript(JSX) | D-108 |
| `fetch`, `useApi` 훅 | axios, TanStack Query | D-109, D-100 |
| `GET /api/me/teams` | `GET /api/me` 하나 | 서버 `MeController`가 teams를 같이 준다 |
| `POST /logout` | `POST /api/logout` | 서버 `SecurityConfig` |
| 팀 선택 화면 | 없음. 마지막에 본 팀으로 바로 | D-111 |
| 한 PR | 1부(틀)·2부(화면 내용·CI) | 다른 사람이 틀 위에서 먼저 시작할 수 있게 |

## 3. 팁

- `npm` 명령은 `console` 폴더에서 친다 (레포 루트에는 `package.json`이 없다).
- Git Bash에서는 경로의 `\`가 지워진다. `/c/Users/...`처럼 `/`로 쓴다. git은 저장소 안이면 어느 하위 폴더에서 쳐도 같다.
- `console/.gitignore`가 `node_modules`·`dist`를 이미 막는다. 루트 `.gitignore`에 또 적을 필요가 없다.

## 4. 남은 것 (확인 못 한 것)

- 실제 GitHub 로그인. 로컬에 OAuth 앱 값이 없다. 콘솔을 거치면 콜백 주소가 `http://localhost:5173/login/oauth2/code/github`
- 로그인 뒤 원래 화면으로 돌아가기: 서버는 `?next=`를 받게 됐다(PR #64). 콘솔의 `Login.jsx`·`client.js`가 아직 `next`를 붙이지 않는다
- CI에 콘솔 job 없음 (2부)

## 관련 노트

[[AiOps 26 - 로그인과 권한 (B)]] · [[AiOps 41 - LLM 기본 모델과 실패 로그]] · [[AiOps 43 - 설명 재시도 최소 나이]]
