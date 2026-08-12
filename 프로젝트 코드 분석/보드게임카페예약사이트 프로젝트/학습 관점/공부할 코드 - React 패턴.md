---
출처: Claude 분석
원본: shirhal/front-end
작성일: 2026-08-11
tags: [프로젝트, 학습, 보드게임카페예약사이트, react]
---

# 공부할 코드 - React 패턴

프론트엔드에서 원리를 정확히 알고 넘어가야 하는 코드 3개.
허브: [[보드게임카페예약사이트 프로젝트에서 배울 것]]

## 1. useRef 실행 플래그 — state와 ref의 선택 기준

결제 성공 페이지( [[components 분석 - Reservation과 결제]] )에서 예약 POST가 두 번 나가는 사고를 막은 코드입니다.

```javascript
const didSubmit = useRef(false);
if (didSubmit.current) return;
didSubmit.current = true;
await axios.post("/api/reservations", data);
```

### 원리

React 18 StrictMode는 개발 모드에서 effect를 **일부러 두 번** 실행합니다. "두 번 실행되면 안 되는 코드"를 배포 전에 드러내기 위한 설계입니다. 이 프로젝트는 그 덕에 중복 예약 버그를 개발 중에 발견했습니다 — 콘솔에 `🛑 useRef: 이미 처리된 예약` 로그가 남아 있는 게 그 흔적입니다.

`useState`가 아니라 `useRef`인 이유가 학습 포인트입니다.

| | useState | useRef |
| --- | --- | --- |
| 값 변경 시 리렌더링 | 일어남 | 안 일어남 |
| 리렌더링 후 값 유지 | 유지 | 유지 |
| 변경 반영 시점 | 다음 렌더 | 즉시 (`.current`) |
| 어울리는 용도 | 화면에 보이는 값 | 플래그, 타이머 ID, DOM 참조 |

**"이 값이 바뀌면 화면이 바뀌어야 하는가?"** — 이 질문 하나로 갈립니다. 실행 플래그는 화면과 무관하므로 ref의 자리입니다. 게다가 state였다면 `setDidSubmit(true)`가 다음 렌더에나 반영돼서 두 번째 실행을 못 막습니다 — **즉시 반영**이 필요한 것도 ref를 고르는 이유입니다.

### 활용

`setInterval` ID 보관( JS day13 웹 스토리지와 인터벌 의 정리 패턴), 이전 값 기억, 스크롤 위치 저장 — 전부 같은 기준으로 ref입니다. 근본 해법은 결제 승인을 서버로 옮겨 프론트 effect에서 부수효과를 없애는 것( → [[더 나아가기 - 서버 상태와 결제]] ).

## 2. 커스텀 훅 — 클로저가 상태를 가둔다

훅 8개( [[hooks 분석]] ) 중 하나를 골라 구조를 뜯어보면 JS day10 함수 의 클로저가 실전에서 어떻게 쓰이는지 보입니다.

```javascript
export default function useReservationForm() {
  const [form, setForm] = useState({ ... });     // 밖에서 직접 접근 불가
  const handleChange = (e) =>
    setForm((prev) => ({ ...prev, [e.target.name]: e.target.value }));
  return { form, handleChange, handleSubmit, price };   // 공개 인터페이스
}
```

### 원리

상태는 함수 스코프(클로저)에 갇혀 있고, 반환 객체만이 바깥과의 통로입니다. `form`을 훅 밖에서 임의로 바꿀 방법은 없습니다 — `handleChange`라는 정해진 통로만 있습니다.

이것이 Java에서 배운 정보 은닉과 정확히 같은 목표입니다.

```
Java:  private 필드 + public setter    → Java day08 접근제한자와 static
JS:    클로저 변수 + 반환된 함수        → JS day10 함수
```

언어가 달라도 "상태를 숨기고 조작 통로만 연다"는 설계 목표가 같습니다. 이 대응을 자기 말로 설명할 수 있으면 두 언어 모두에서 설계가 됩니다.

`[e.target.name]` **계산된 속성명**으로 입력 필드 여러 개를 핸들러 하나로 처리하는 것도 이 코드의 부수 학습거리입니다( JS day07 객체 ).

### 활용 기준

"컴포넌트에서 fetch·상태·계산이 스크롤 한 화면을 넘으면 훅으로 뺀다." `MainPage.js` 705줄이 버틴 이유가 로직이 `useCarousel`로 빠져 있어서였다는 것( [[components 분석 - MainPage와 고객지원]] )이 실증 사례입니다. 훅을 나누는 단위는 기술이 아니라 **책임**입니다 — `useReservationForm`은 "예약 폼의 모든 것"이지 "fetch 모음"이 아닙니다.

## 3. 낙관적 업데이트 — 한 줄에 세 가지 원리

추천 버튼( [[hooks 분석]] 의 `useBoardGameList`)의 한 줄입니다.

```javascript
setBoardGames((prev) => prev.map((g) =>
  g.game_id === gameId ? { ...g, likes: currentLikes + 1 } : g));
```

### 분해

1. **함수형 업데이트** `(prev) =>` — 연속 클릭돼도 항상 최신 상태 기준으로 계산됩니다. `setBoardGames(boardGames.map(...))`이라고 썼다면 클로저에 잡힌 낡은 배열 기준이 될 수 있습니다.
2. **불변 업데이트** `map` + `{ ...g }` — 원본 배열·객체를 바꾸지 않고 새로 만듭니다. React는 **참조 비교**로 변경을 감지하므로 `g.likes += 1`(변이)로는 리렌더링이 일어나지 않습니다. JS day07 객체 의 참조·얕은 복사가 왜 중요한지가 여기서 실감됩니다.
3. **낙관적 업데이트** — 서버 응답 전에 화면을 먼저 바꿉니다. 체감 속도가 즉각적이 됩니다.

### 빠진 반쪽 — 롤백

"낙관"은 성공을 가정한다는 뜻이고, **가정이 틀렸을 때 되돌리는 것까지가 패턴의 전부**입니다. 이 코드는 서버가 409(이미 추천)를 반환해도 +1이 화면에 남습니다.

```javascript
// 연습: 롤백 붙여보기
const prev = boardGames;               // 스냅샷
setBoardGames(낙관적_반영);
try { await axios.post(...); }
catch { setBoardGames(prev); }         // 실패 시 복원
```

이 연습을 해보면 TanStack Query의 `onMutate`(스냅샷) / `onError`(복원)가 정확히 이걸 패턴화한 것임이 보입니다 → [[더 나아가기 - 서버 상태와 결제]]

### 함께 볼 것 — 쓰로틀과 디바운스

같은 훅의 무한 스크롤은 lodash `throttle`로 스크롤 이벤트를 묶었습니다.

- **쓰로틀**: 일정 간격당 최대 1회 실행 — 스크롤·리사이즈
- **디바운스**: 입력이 멈춘 뒤 1회 실행 — 검색 자동완성

이 프로젝트의 검색창은 디바운스가 없어 타이핑마다 요청이 나갔습니다. 어느 쪽을 쓸지 고르는 기준(연속 이벤트 중에도 반응이 필요한가?)까지가 한 세트입니다.

## 관련 노트

[[보드게임카페예약사이트 프로젝트에서 배울 것]] · [[공부할 코드 - SQL과 데이터]] · [[전문용어 정리]]
