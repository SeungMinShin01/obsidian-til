---
출처: Claude 분석
원본: KDT_2026/2026_React/src/example/day08, 2026_React/src/main.jsx
작성일: 2026-09-28
tags: [학습, react]
---

# React day09 — 로그인·회원가입 폼과 세션 인증 상태

> 실습 파일: `src/example/day08/App.jsx` · `Header.jsx` · `Login.jsx` · `SignUp.jsx` · `src/main.jsx`
> 허브: [[React MOC]] · 이전: [[React day08 와일드카드 라우트와 서버 게시판 목록]] · 다음: (예정)

지금까지는 게시판 화면이 서버 데이터를 읽고 쓰기만 했다면, 이번에는 "누가 접속했는지"를 화면이 알아야 하는 자리다. 서버(Spring day12 수업)에 회원가입·로그인·내정보조회·로그아웃 API와 세션이 갖춰진 뒤, 그 API 네 개를 부르는 화면 쪽 짝이 완성된다. 로그인 상태(`currentUser`)를 최상위 컴포넌트 하나에 두고, 그 아래 화면들이 이 상태를 보고 갈라지는 구조다.

## 1. 배운 내용

### 1-1. 로그인 상태를 최상위에 두고 새로고침에도 이어 가기 — App.jsx

```jsx
function App() {
  const [currentUser, setCurrentUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    axios.get('http://localhost:8080/api/member/me', { withCredentials: true })
      .then((res) => {
        setCurrentUser(res.data ? res.data : null);
      })
      .catch((err) => {
        console.error('세션 확인 실패:', err);
        setCurrentUser(null);
      })
      .finally(() => {
        setLoading(false);
      });
  }, []);

  if (loading) return <div>세션 확인 중...</div>;
  // ...
}
```

- `currentUser`는 `App` 컴포넌트 하나에 두고, 그 아래 `Header`·`Home`·`Login`·`SignUp`에 props로 내려보낸다. 로그인 여부를 화면마다 따로 확인하지 않고 한 곳에서만 판단하는 구조다.
- 화면을 새로고침하면 리액트의 상태는 전부 사라지지만, 톰캣 쪽 세션은 쿠키(`JSESSIONID`)로 남아 있다. 그래서 마운트될 때마다 `/api/member/me`를 한 번 불러서 "서버가 기억하고 있는 로그인 상태"를 다시 `currentUser`에 채워 넣는다 — 서버 쪽 세션과 화면 쪽 상태를 맞추는 자리다.
- 여기서 `axios.get`에 `{ withCredentials: true }`를 넘기는 것이 중요하다. 이 옵션이 없으면 브라우저가 세션 쿠키를 이 요청에 실어 보내지 않아서, 서버는 로그인된 적 없는 요청으로 보고 `/me`가 항상 미로그인 취급을 하게 된다.
- 세션 확인이 끝나기 전(`loading === true`)에는 화면을 그리지 않는다. 확인 전에 미리 "비로그인" 화면을 보여줬다가 확인이 끝난 뒤 "로그인됨"으로 바뀌는 깜빡임을 막는 자리다.

### 1-2. 로그인 여부로 라우트를 가로막기 — Navigate

```jsx
<Routes>
  <Route path="/" element={<Home currentUser={currentUser} />} />
  <Route path="/signup" element={currentUser ? <Navigate to="/" /> : <SignUp />} />
  <Route path="/login" element={currentUser ? <Navigate to="/" /> : <Login setCurrentUser={setCurrentUser} />} />
  <Route path="*" element={<Navigate to="/" />} />
</Routes>
```

- `currentUser`가 있는데 `/signup`이나 `/login`으로 들어오면 그 화면 대신 곧바로 홈(`/`)으로 돌려보낸다. 이미 로그인된 사람이 로그인 폼을 다시 보는 것을 막는 조건부 라우팅이다.
- day08에서 본 와일드카드 `*`는 이번에는 NotFound가 아니라 홈으로 보내는 용도로 쓰인다. 같은 `*` 자리도 화면 설계에 따라 다르게 채울 수 있다는 뜻이다.
- `Home` 컴포넌트는 `currentUser`가 있으면 회원번호·아이디·이름·권한을 보여주고, `role`이 `"admin"`이면 강조된 안내 문구를 얹는다. 서버가 시드 데이터로 미리 나눠 둔 admin/user 구분(Spring day12)이 화면에서 처음으로 갈라져 쓰이는 자리다.

### 1-3. 로그인 폼 — 제어 컴포넌트 두 칸과 axios.post

```jsx
function Login({ setCurrentUser }) {
  const navigate = useNavigate();
  const [mid, setMid] = useState('');
  const [mpwd, setMpwd] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const res = await axios.post(
        'http://localhost:8080/api/member/login',
        { mid, mpwd },
        { withCredentials: true }
      );
      if (res.data) {
        setCurrentUser(res.data);
        navigate('/');
      } else {
        alert('로그인 실패: 아이디 또는 비밀번호가 일치하지 않습니다.');
      }
    } catch (err) {
      alert('서버 통신 오류가 발생했습니다.');
    }
  };
  // <form onSubmit={handleSubmit}> 안에 아이디·비밀번호 두 칸
}
```

- 아이디·비밀번호 두 칸 모두 `useState`로 값을 들고 있는 제어 컴포넌트다. day03에서 본 "상태 없이 제출 시점에 읽기" 방식 대신, 여기서는 입력마다 상태를 두는 쪽을 골랐다 — 두 칸뿐이라 코드가 크게 늘지 않고, 나중에 실시간 검증(빈 값 확인 등)을 붙이기도 이 쪽이 쉽다.
- 로그인 컨트롤러는 성공하면 `MemberDto` 객체를, 실패하면 `null`을 그대로 돌려준다(Spring day12). 화면은 `res.data`가 값이 있는지 없는지만으로 성공·실패를 가른다 — 별도의 상태 코드나 메시지 필드를 보지 않는다.
- 로그인 요청에도 `{ withCredentials: true }`가 붙는다. 이 옵션이 있어야 로그인 성공 시 서버가 내려주는 `Set-Cookie`(세션 쿠키)를 브라우저가 저장하고, 이후 요청에도 실어 보낸다.
- 성공하면 응답으로 받은 회원 정보를 그대로 `setCurrentUser`에 넣는다. `/me`를 다시 부르지 않고 로그인 응답 자체를 재사용하는 자리다.

### 1-4. 회원가입 폼 — 라디오 버튼으로 권한 고르기

```jsx
function SignUp() {
  const [mid, setMid] = useState('');
  const [mpwd, setMpwd] = useState('');
  const [mname, setMname] = useState('');
  const [role, setRole] = useState('user');

  const handleSubmit = async (e) => {
    e.preventDefault();
    const res = await axios.post(
      'http://localhost:8080/api/member/signup',
      { mid, mpwd, mname, role },
      { withCredentials: true }
    );
    if (res.data === true) {
      navigate('/login');
    } else {
      alert('회원가입 실패: 이미 사용 중인 아이디입니다.');
    }
  };
  // ...
  <input type="radio" name="role" value="user" checked={role === 'user'} onChange={(e) => setRole(e.target.value)} />
  <input type="radio" name="role" value="admin" checked={role === 'admin'} onChange={(e) => setRole(e.target.value)} />
}
```

- 입력칸 네 개(`mid`·`mpwd`·`mname`·`role`)가 그대로 서버 `MemberDto`의 필드 이름과 겹친다. day08의 글쓰기 폼에서 본 "화면 쪽 이름은 자유, 보내는 키만 서버와 맞으면 된다"는 원칙과 달리, 여기서는 처음부터 서버 필드 이름을 그대로 상태 이름으로 썼다 — 번역 객체를 따로 두지 않아도 되는 대신, 서버 필드 이름이 바뀌면 화면 쪽도 같이 고쳐야 한다.
- 라디오 버튼은 `checked`와 `onChange`를 함께 둔 제어 컴포넌트다. `name="role"`을 두 `input`이 공유해야 그중 하나만 선택되는 라디오 그룹으로 묶인다.
- 회원가입 컨트롤러는 `boolean` 하나만 돌려준다(Spring day12). 로그인처럼 객체를 돌려받지 않으므로, 가입 성공 뒤에는 자동 로그인이 아니라 `/login`으로 이동시켜 다시 아이디·비밀번호를 입력하게 한다.

### 1-5. 로그아웃과 로그인 상태별 네비게이션 — Header.jsx

```jsx
function Header({ currentUser, setCurrentUser }) {
  const navigate = useNavigate();

  const handleLogout = async () => {
    const res = await axios.post(
      'http://localhost:8080/api/member/logout',
      {},
      { withCredentials: true }
    );
    if (res.data === true) {
      setCurrentUser(null);
      navigate('/login');
    }
  };

  return (
    <header>
      {currentUser ? (
        <>
          <span>{currentUser.mname} ({currentUser.mid})</span>
          <button onClick={handleLogout}>로그아웃</button>
        </>
      ) : (
        <>
          <Link to="/signup"><button>회원가입</button></Link>
          <Link to="/login"><button>로그인</button></Link>
        </>
      )}
    </header>
  );
}
```

- `axios.post`의 두 번째 인자는 요청 본문인데, 로그아웃은 보낼 값이 없으므로 빈 객체 `{}`를 그대로 넣는다. 세 번째 인자 자리에 옵션(`withCredentials`)을 넣으려면 두 번째 자리를 비워 둘 수 없어서, 본문이 없어도 형식상 빈 객체를 채운다.
- 로그아웃 컨트롤러는 세션을 `invalidate()`한 뒤 `true`를 돌려준다(Spring day12). 화면은 이 응답을 받은 다음에야 `currentUser`를 `null`로 비우고 로그인 화면으로 이동한다 — 요청이 실패했는데 화면만 먼저 로그아웃된 것처럼 보이는 상황을 막는 순서다.
- `currentUser` 유무에 따라 네비게이션 버튼 자체가 통째로 갈린다: 로그인 전에는 회원가입·로그인 버튼, 로그인 후에는 이름·권한 표시와 로그아웃 버튼. `Header`는 `App`에서 `currentUser`·`setCurrentUser`를 props로 받아 화면과 상태를 동시에 다룬다.

## 2. 추가로 알면 좋은 활용법

### 2-1. withCredentials를 매번 적지 않기

로그인·로그아웃·내정보조회·회원가입 네 요청 모두 `{ withCredentials: true }`를 반복해서 넣고 있다. `axios.create({ baseURL: 'http://localhost:8080', withCredentials: true })`로 인스턴스를 하나 만들어 두면, 이후 요청은 옵션 없이 그 인스턴스로만 불러도 된다.

### 2-2. 세션 확인을 최상위 한 곳에 모아 둔 이유

로그인 여부 확인을 화면마다 따로 하면 같은 `/me` 호출이 여러 컴포넌트에 흩어진다. `App`에서 한 번만 확인해 `currentUser`를 props로 내려주는 지금 구조는 페이지 수가 적을 때는 간단하지만, 라우트가 깊어지고 props를 여러 단계 거쳐 내려야 하면(prop drilling) Context API로 옮기는 편이 정리가 된다.

### 2-3. 엔드포인트마다 다른 응답 모양에 맞춰 분기하기

로그인은 객체 아니면 `null`, 회원가입·로그아웃은 `true`/`false`로 응답 모양이 서로 다르다(Spring day12). 화면 쪽 분기 코드(`if (res.data)` vs `if (res.data === true)`)는 이 차이를 그대로 반영한 것이라, 두 형태를 섞어 쓰면 안 되는 자리다.

## 3. 더 나아가 알면 좋은 것

### 3-1. 로그인이 필요한 화면 보호하기

지금은 "로그인된 사람이 로그인/회원가입 화면에 다시 들어가는 것"만 막고 있다. 반대 방향인 "로그인 안 한 사람이 로그인 전용 화면에 들어가는 것"을 막는 가드는 아직 없다. `currentUser`가 없으면 `/login`으로 돌려보내는 `PrivateRoute` 컴포넌트로 `<Route>`를 감싸는 패턴이 다음 단계로 이어진다.

### 3-2. 다음에 볼 키워드

- Context API — `currentUser`를 props로 내려보내지 않고 어디서든 꺼내 쓰기
- `PrivateRoute` / 인증 가드 컴포넌트
- JWT — 쿠키 세션 대신 토큰을 헤더에 실어 보내는 무상태 인증 (Spring day12에서 짚은 대안)
- 비밀번호 확인 칸, 아이디 중복 확인 버튼 등 가입 폼 검증 보강
- 로그인 실패 사유 세분화 — 아이디가 없는 경우와 비밀번호가 틀린 경우를 구분해 안내하기

## 실습 파일

- `KDT_2026/2026_React/src/example/day08/App.jsx` — `currentUser` 상태와 `/me` 세션 확인, 로그인 여부에 따른 라우트 가드, 관리자/일반회원 안내를 보여주는 `Home`
- `KDT_2026/2026_React/src/example/day08/Header.jsx` — 로그인 상태별 네비게이션과 로그아웃 처리
- `KDT_2026/2026_React/src/example/day08/Login.jsx` — 아이디·비밀번호 제어 폼과 로그인 요청
- `KDT_2026/2026_React/src/example/day08/SignUp.jsx` — 아이디·비밀번호·이름·권한(라디오) 제어 폼과 회원가입 요청
- `KDT_2026/2026_React/src/main.jsx` — 진입 컴포넌트를 `day08/App`(`App8`)으로 교체

## 관련 노트

[[React MOC]] · [[React day08 와일드카드 라우트와 서버 게시판 목록]] · [[React day04 React Router 도입과 라우트 정의]] · [[React day05 axios로 백엔드에 POST 보내기]] · [[KDT_2026 학습 지도]]

<!--
[문체 규칙]
- 내가 공부하며 정리한 노트다. 남의 코드를 평가하는 말투를 쓰지 않는다.
- 2인칭(하신, 쓰셨, 적으신)을 쓰지 않는다.
- 원본 코드의 오류·오타는 기록하지 않는다. 필요하면 파일 지목 없이 일반 주의사항으로 쓴다.
- 한 사람이 쭉 이어서 쓴 것처럼 문체를 일정하게 유지한다.
-->
