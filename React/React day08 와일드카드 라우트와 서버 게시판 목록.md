---
출처: Claude 분석
원본: KDT_2026/2026_React/src/example/day07, 2026_React/src/main.jsx
작성일: 2026-09-23
tags: [학습, react]
---

# React day08 — 와일드카드 라우트와 서버 게시판 목록

> 실습 파일: `src/example/day07/App.jsx` · `NotFound.jsx` · `list.jsx` · `src/main.jsx`
> 허브: [[React MOC]] · 이전: [[React day07 게시판 종합실습 스킨 분해와 mode 전환]] · 다음: (예정)

앞의 종합실습은 게시판 화면을 `mode` 상태 하나로 갈아끼웠고, 데이터도 컴포넌트 안 배열에 들어 있었다. 이번에는 두 가지를 바꾼다. 화면 전환은 **라우터(주소)** 로, 데이터는 **스프링 서버의 `/api`** 에서 받아 온다. 같은 날 Spring 수업에서 만든 게시판 목록 API(Spring day11 노트, 허브 경유)를 이 화면이 부르는 구조다. 이번 코드는 그 첫 칸인 **목록 화면 + 없는 주소 처리**까지다.

## 1. 배운 내용

### 1-1. 라우트 두 개와 와일드카드 `*` — `App.jsx`

```jsx
export default function App7() {
  return (
    <Routes>
      <Route path="*" element={<NotFound />} />
      <Route path="/list" element={<List />} />
    </Routes>
  );
}
```

| path | 뜻 | 보여 주는 것 |
| --- | --- | --- |
| `/list` | 정확히 이 주소 | 게시판 목록 |
| `*` | 와일드카드 — 위에서 못 잡은 모든 주소 | NotFound |

- `*`는 **다른 라우트와 맞지 않는 나머지 전부**를 받는다. React Router v6 이후는 적힌 순서가 아니라 **더 구체적인 경로가 이기는** 방식이라 `*`를 위에 적어도 `/list`가 먼저 잡힌다.
- 그래서 첫 화면(`/`)도 지금은 `/list`와 맞지 않으므로 NotFound가 뜨고, 거기 있는 링크로 목록에 들어가는 흐름이 된다.
- `Routes`는 Router 컨텍스트 안에서만 동작하므로 `main.jsx`는 여전히 `BrowserRouter`로 `App7`을 감싼다 → [[React day04 React Router 도입과 라우트 정의]].

### 1-2. NotFound와 JSX의 닫는 태그 — `NotFound.jsx`

```jsx
<p>
  페이지를 찾을 수 없습니다. <br />
  <Link to="/list">목록으로 바로가기</Link>
</p>
```

- HTML은 `<br>`처럼 안 닫아도 되지만 JSX는 **모든 태그를 닫아야** 한다. 내용이 없는 태그는 `<br />` · `<img />` · `<input />`처럼 스스로 닫는다.
- 라우터를 쓰는 이유를 한 줄로 정리하면 "특정 URL 경로에 맞는 컴포넌트를 불러오기 위해서"다.
- 이동은 `<a href>`가 아니라 `<Link to>` — 새로고침 없이 주소만 바꾸고 해당 컴포넌트를 그린다 → [[React day07 게시판 종합실습 스킨 분해와 mode 전환]]에서 본 `<a href>` 새로고침 문제의 답.

### 1-3. 서버에서 목록 받기 — `list.jsx`

```jsx
const [boardData, setBoardData] = useState([]);
let requestUrl = "http://localhost:8080/api";

useEffect(() => {
  async function getBoardData() {
    const response = await axios.get(requestUrl);
    setBoardData(response.data);
  }
  getBoardData();
}, []);
```

- 뼈대는 [[React day05 외부 API 호출과 목록 렌더링]]·[[React day06 내 서버를 거쳐 받는 공공데이터]]와 같다: `useState([])` 빈 배열 → `useEffect(…, [])` 마운트 1회 요청 → 응답을 state에 넣어 재렌더링.
- `useEffect`의 콜백 자체는 `async`로 만들 수 없다(정리 함수 대신 Promise를 돌려주게 되므로). 그래서 **안쪽에 async 함수를 만들고 바로 부르는** 모양을 쓴다.
- `axios`는 응답 JSON을 알아서 풀어 `response.data`에 담는다. `fetch`처럼 `.json()`을 한 번 더 부를 필요가 없다 → [[React day05 axios로 백엔드에 POST 보내기]].

### 1-4. 행 만들기 — 자르기 · `key` · 상세 링크

```jsx
let lists = boardData.map((row) => {
  let date = row.regdate.substring(0, 10);
  let subject = row.subject.substring(0, 20);
  return (
    <tr key={row.idx}>
      <td className="cen">{row.idx}</td>
      <td><Link to={"/view/" + row.idx}>{subject}</Link></td>
      <td className="cen">{row.name}</td>
      <td className="cen">{date}</td>
    </tr>
  );
});
```

| 코드 | 하는 일 |
| --- | --- |
| `regdate.substring(0, 10)` | `2026-09-01 09:00:00` → `2026-09-01`, 날짜만 |
| `subject.substring(0, 20)` | 긴 제목을 20글자로 잘라 표 폭 유지 |
| `key={row.idx}` | 행마다 고유 번호로 리액트가 목록 변화를 추적 |
| `"/view/" + row.idx` | 다음 단계 상세 화면 주소를 미리 만들어 둠 |

- `row.idx`·`row.subject`·`row.name`·`row.regdate`는 서버 DTO의 필드 이름 그대로다. **DB 컬럼 = 엔티티 필드 = JSON 키 = `row.키`** 가 한 줄로 이어진다.
- `row.idx`는 `key`, 번호 칸, 상세 주소 세 곳에 쓰인다. 서버 응답에 이 값이 비어 있으면 세 곳이 동시에 흔들리므로, 화면을 짜기 전에 응답 JSON을 한 번 열어 키가 모두 채워져 있는지 확인하는 편이 안전하다.
- `substring`은 값이 `null`이면 오류가 난다. 서버에서 빈 값이 올 수 있으면 `row.regdate?.substring(0, 10)`처럼 옵셔널 체이닝으로 막는다.

### 1-5. 목록 화면의 뼈대

- `header`(제목) · `nav`(`<Link to="/write">글쓰기</Link>`) · `article`(표) — day07 종합실습에서 쪼갠 스킨 구조를 한 파일에 다시 모은 모양이다.
- `className="cen"` · `id="boardTable"`은 앞 실습의 `index.css` 규칙을 그대로 쓴다. JSX에서는 `class`가 아니라 `className`.

## 2. 추가로 알면 좋은 활용법

### 2-1. 첫 화면을 목록으로 — `Navigate`

```jsx
<Route path="/" element={<Navigate to="/list" replace />} />
```

- `/`로 들어오면 곧바로 `/list`로 보낸다. `replace`를 붙이면 뒤로 가기 기록에 `/`가 남지 않는다.

### 2-2. 요청 주소는 한 곳에

- `http://localhost:8080`을 컴포넌트마다 적으면 배포 때 전부 고쳐야 한다. `axios.create({ baseURL })`로 인스턴스를 만들거나 Vite 환경 변수(`import.meta.env.VITE_API_URL`)로 뺀다.

### 2-3. 로딩 · 오류 상태

```jsx
const [loading, setLoading] = useState(true);
const [error, setError] = useState(null);
// try { ... } catch (e) { setError(e) } finally { setLoading(false) }
```

- 서버가 꺼져 있으면 지금은 빈 표만 보인다. 로딩·오류 state를 두 개 더 두면 "불러오는 중", "서버에 연결할 수 없음"을 구분해 보여 줄 수 있다.

## 3. 더 나아가 알면 좋은 것

### 3-1. 다음 칸 — 상세 · 쓰기 라우트

| 주소 | 컴포넌트 | 핵심 |
| --- | --- | --- |
| `/view/:idx` | View | `useParams()`로 번호 꺼내 `axios.get("/api/" + idx)` |
| `/write` | Write | 폼 제출 → `axios.post` → `useNavigate()("/list")` |
| `/edit/:idx` | Edit | 기존 값 채운 폼 → `axios.put` |

- mode 상태로 하던 전환([[React day07 게시판 종합실습 스킨 분해와 mode 전환]])이 전부 주소로 바뀌면 새로고침·뒤로 가기·주소 공유가 자연스럽게 된다.

### 3-2. 다음에 볼 키워드

- `useParams` · `useNavigate` — 주소 값 읽기와 코드로 이동하기
- 중첩 라우트 + `<Outlet>` — 게시판 공통 레이아웃
- `AbortController` — 컴포넌트가 사라질 때 요청 취소
- TanStack Query(React Query) — 서버 데이터 캐싱·재요청
- Vite `server.proxy` — CORS 없이 개발 서버에서 API 부르기

## 실습 파일

- `KDT_2026/2026_React/src/example/day07/App.jsx` — `Routes` 안에 `*`(NotFound)와 `/list`(List) 두 라우트
- `KDT_2026/2026_React/src/example/day07/NotFound.jsx` — 없는 주소 안내와 `<Link to="/list">`, JSX 자기 닫는 태그 메모
- `KDT_2026/2026_React/src/example/day07/list.jsx` — `axios.get("http://localhost:8080/api")`로 받은 게시글을 `map`으로 표 행 렌더링
- `KDT_2026/2026_React/src/main.jsx` — 진입 컴포넌트를 `day07/App`(`App7`)으로 교체, `BrowserRouter` 유지

## 관련 노트

[[React MOC]] · [[React day07 게시판 종합실습 스킨 분해와 mode 전환]] · [[React day04 React Router 도입과 라우트 정의]] · [[React day06 내 서버를 거쳐 받는 공공데이터]] · [[KDT_2026 학습 지도]]

<!--
[문체 규칙]
- 내가 공부하며 정리한 노트다. 남의 코드를 평가하는 말투를 쓰지 않는다.
- 2인칭(하신, 쓰셨, 적으신)을 쓰지 않는다.
- 원본 코드의 오류·오타는 기록하지 않는다. 필요하면 파일 지목 없이 일반 주의사항으로 쓴다.
- 한 사람이 쭉 이어서 쓴 것처럼 문체를 일정하게 유지한다.
-->
