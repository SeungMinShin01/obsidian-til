---
출처: Claude 분석
원본: KDT_2026/2026_React/src/example/day09/List.jsx, View.jsx, Write.jsx
작성일: 2026-10-07
tags: [학습, react]
---

# React day10 — 게시판 첨부파일 등록과 이미지 미리보기

> 실습 파일: `src/example/day09/List.jsx` · `View.jsx` · `Write.jsx`
> 허브: [[React MOC]] · 이전: [[React day09 로그인·회원가입 폼과 세션 인증 상태]] · 다음: (예정)

이번에는 목록·상세·글쓰기 세 화면을 `async / await` 로 서버 `/api/board` 에 붙이고, 글에 파일을 첨부하는 자리가 추가된다. 서버 쪽 짝은 Spring day14 수업(파일 업로드·다운로드 게시판)이고, 화면은 그 API 세 개를 부르는 쪽이다. 정리하면 "JSON 대신 `FormData` 로 보내기", "첨부 여부를 화면에 표시하기", "다운로드 주소를 `<img src>` 로 그대로 쓰기" 세 가지가 새로 나온 내용이다.

## 1. 배운 내용

### 1-1. async / await 로 목록 조회 — List.jsx

```jsx
const API_BASE = "http://localhost:8080/api/board";

const fetchList = async () => {
  try {
    const response = await axios.get(`${API_BASE}/list`);
    setBoardList(response.data);
  } catch (error) {
    console.error("목록 로드 실패:", error);
  }
};

useEffect(() => {
  fetchList();
}, []);
```

- 서버 주소를 `API_BASE` 상수 하나로 빼 두고 세 화면이 같은 값을 쓴다. 주소가 바뀌어도 한 줄만 고치면 된다
- 조회 함수를 `useEffect` 바깥에 따로 정의하고 안에서는 호출만 한다. 이전에는 `useEffect` 안에 async 함수를 만들어 바로 불렀는데, 이름을 붙여 빼 두면 나중에 "삭제 후 다시 불러오기" 같은 자리에서 재사용하기 쉽다
- 응답이 오기 전에는 `boardList` 가 빈 배열이라 "등록된 게시물이 없습니다." 행이 먼저 보인다. 삼항 연산자로 길이가 0일 때와 아닐 때를 나눠 그린다

### 1-2. 첨부 여부와 날짜 표시 — 값이 없을 때를 대비한 삼항

```jsx
<td>{board.cdate ? board.cdate.substring(0, 10) : "-"}</td>
<td>{board.fileName ? "O" : "X"}</td>
```

- 서버가 주는 `cdate` 는 `2026-10-02T03:25:00` 같은 문자열이라 앞 10글자만 잘라 날짜로 쓴다. 값이 비어 있을 수 있어 `? :` 로 `-` 를 대신 보여 준다
- 첨부파일은 DB에 파일명만 저장되므로(Spring day14) `fileName` 이 있으면 첨부 있음, 없으면 없음으로 판단한다
- 제목은 `<Link to={`/view/${board.id}`}>` 로 상세 화면에 연결한다. 번호가 주소에 실린다

### 1-3. 상세 조회와 useParams — View.jsx

```jsx
const { id } = useParams();
const [board, setBoard] = useState(null);

const fetchBoard = async () => {
  try {
    const response = await axios.get(`${API_BASE}/view?id=${id}`);
    setBoard(response.data);
  } catch (error) {
    console.error("상세조회 실패:", error);
  }
};

useEffect(() => {
  fetchBoard();
}, [id]);

if (!board) {
  return <div>게시글을 불러오는 중입니다...</div>;
}
```

- `useParams()` 로 주소의 `:id` 를 꺼내 쿼리스트링(`?id=`)으로 서버에 넘긴다
- 의존성 배열을 `[id]` 로 두면 주소의 번호가 바뀔 때 다시 조회한다
- `board` 초기값을 `null` 로 두고, `null` 인 동안은 "불러오는 중" 만 반환한다. 이 `if (!board) return` 이 없으면 `board.title` 접근에서 첫 렌더링 때 오류가 난다. day09 노트의 `loading` 상태와 같은 목적을 `null` 검사 하나로 해결한 형태다

### 1-4. 이미지 파일 판별과 원본 파일명 복원

```jsx
const isImageFile = (fileName) => {
  if (!fileName) return false;
  const ext = fileName.split(".").pop().toLowerCase();
  return ["jpg", "jpeg", "png", "gif", "webp"].includes(ext);
};

const originalName =
  board.fileName && board.fileName.includes("_")
    ? board.fileName.substring(board.fileName.indexOf("_") + 1)
    : board.fileName;
```

- `split(".").pop()` 으로 확장자를 꺼내 소문자로 맞추고, 이미지 확장자 배열의 `includes` 로 판별한다
- 서버는 파일명 앞에 UUID를 붙여 저장하므로(`UUID_원본명`) 첫 `_` 뒤쪽만 잘라 사용자에게 보일 원본 이름으로 복원한다

### 1-5. 다운로드 주소를 img src 로 재사용 — 미리보기와 다운로드

```jsx
const fileUrl = `${API_BASE}/download/${id}`;

{isImageFile(board.fileName) ? (
  <img src={fileUrl} alt="첨부 이미지" style={{ maxWidth: "100%", maxHeight: "400px", objectFit: "contain" }} />
) : (
  <p>이미지 파일이 아닙니다.</p>
)}

<button onClick={() => { window.location.href = fileUrl; }}>
  {originalName} 다운로드
</button>
```

- 서버의 다운로드 엔드포인트는 파일 바이트를 응답 본문으로 내려 주므로, 이미지라면 그 주소를 `<img src>` 에 넣는 것만으로 미리보기가 된다
- 다운로드 버튼은 `window.location.href` 에 같은 주소를 대입해 브라우저가 파일 저장을 처리하게 한다. `axios` 로 받아 Blob 을 만드는 방법보다 단순하다
- 첨부가 있을 때만 영역 전체를 `{board.fileName && (...)}` 로 그린다. `&&` 단축 평가로 조건부 렌더링을 하는 관용구다

### 1-6. FormData 로 파일 포함 등록 — Write.jsx

```jsx
const [title, setTitle] = useState("");
const [content, setContent] = useState("");
const [file, setFile] = useState(null);

const handleSubmit = async (e) => {
  e.preventDefault();

  const formData = new FormData();
  formData.append("title", title);
  formData.append("content", content);
  if (file) {
    formData.append("file", file);
  }

  const response = await axios.post(`${API_BASE}/write`, formData);
  if (response.data === true) {
    alert("게시글이 성공적으로 등록되었습니다.");
    navigate("/");
  } else {
    alert("등록 처리에 실패했습니다.");
  }
};

<input type="file" onChange={(e) => setFile(e.target.files[0])} />
```

- 파일은 JSON 에 담을 수 없어 `FormData` 에 필드를 하나씩 `append` 해 보낸다. 서버 쪽에서는 `@ModelAttribute` 로 받는 짝이다(Spring day14)
- `append` 의 키(`title`, `content`, `file`)가 서버 DTO 의 필드명과 같아야 값이 들어간다
- 파일 선택 `<input type="file">` 은 값을 제어 컴포넌트로 묶지 않고, `onChange` 에서 `e.target.files[0]` 만 `file` 상태에 보관한다. 선택하지 않았다면 `null` 이라 `if (file)` 로 막는다
- 제목·내용 입력은 `value` + `onChange` 로 묶은 제어 컴포넌트(day03 폼 노트와 같은 방식)이고, `required` 로 빈 값 제출을 브라우저가 먼저 막는다
- 응답이 `true` 이면 `navigate("/")` 로 목록에 돌아간다. 이전에 보던 `event.target.<name>.value` 방식 대신 상태 변수를 거치는 방식이다
- `axios.post` 에 `FormData` 를 넘기면 `Content-Type: multipart/form-data` 와 경계 문자열을 브라우저가 알아서 붙인다. 헤더를 직접 지정하지 않아도 된다

## 2. 추가로 알면 좋은 활용법

- **여러 파일 첨부**: `<input type="file" multiple />` 로 두고 `e.target.files` 를 배열로 바꿔 상태에 담은 뒤 `forEach` 로 같은 키에 여러 번 `append` 한다
- **업로드 전 미리보기**: `URL.createObjectURL(file)` 로 임시 주소를 만들어 `<img src>` 에 넣으면 서버에 올리기 전에 선택한 이미지를 볼 수 있다
- **API 주소 분리**: `API_BASE` 를 환경 변수(`import.meta.env.VITE_API_URL`)로 빼 두면 개발·배포 주소를 코드 수정 없이 바꿀 수 있다
- **결과 판정**: 서버가 `boolean` 을 돌려주는 대신 상태 코드(200/400)로 성공·실패를 나누고 `catch` 에서 한꺼번에 처리하는 구조도 많이 쓴다
- **alert 대신 상태 메시지**: `alert` 는 화면 흐름을 멈추므로 실무에서는 상태 변수에 메시지를 담아 화면에 띄우는 쪽이 일반적이다

## 3. 더 나아가 알면 좋은 것

- 업로드 진행률 — `axios` 의 `onUploadProgress` 로 퍼센트 표시하기
- 파일 크기·확장자 검증을 화면과 서버 양쪽에서 이중으로 하는 이유
- 다운로드 시 `Content-Disposition` 과 한글 파일명 인코딩
- 삭제·수정 화면에서 기존 첨부파일 교체 처리
- 이미지 지연 로딩(`loading="lazy"`)과 썸네일 별도 생성
- `@tanstack/react-query` 같은 서버 상태 관리 도구로 목록·상세 조회 대체하기

## 실습 파일

- `KDT_2026/2026_React/src/example/day09/List.jsx` — `/list` 조회, 빈 목록 안내, 날짜 자르기, 첨부 여부(O/X), 상세 링크
- `KDT_2026/2026_React/src/example/day09/View.jsx` — `useParams` 상세 조회, 이미지 판별, 원본 파일명 복원, 미리보기·다운로드, 목록 복귀
- `KDT_2026/2026_React/src/example/day09/Write.jsx` — 제목·내용·파일 상태, `FormData` 구성, `/write` 전송, 성공 시 목록 이동

## 관련 노트

[[React MOC]] · [[React day09 로그인·회원가입 폼과 세션 인증 상태]] · [[React day08 와일드카드 라우트와 서버 게시판 목록]] · [[React day03 폼 제출과 입력값 읽기]] · [[KDT_2026 학습 지도]]
