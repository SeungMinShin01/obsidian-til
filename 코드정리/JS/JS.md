---
출처: Claude 분석
작성일: 2026-08-21
tags: [코드정리]
---

# JS

> 상위: [[코드정리]]
> 세부: [[JS 기본 문법]] · [[JS 함수]] · [[JS 객체와 배열]] · [[JS DOM]] · [[JS 스토리지와 타이머]] · [[JS 패턴]] · [[JS AI 관용구]]

코드정리 JS 트리의 루트. 아래는 **수업(day02~14)에서 배운 코드 전체**를 한 줄 주석으로 모은 것이다. 원리·심화는 세부 노트로.

## day02~03 — 변수·입출력·자료형

```javascript
let count = 0;                                   // 재할당 가능한 변수
const MAX = 100;                                 // 재할당 금지 (참조만 고정, 내용은 가능)
var old = 1;                                     // 옛 문법 (함수 스코프 — 안 씀)
console.log("값", a, b);                         // 콘솔 출력 (쉼표로 여러 개)
alert("알림");                                   // 알림창
const name = prompt("이름?");                    // 입력창 (항상 문자열 반환)
const yes = confirm("삭제할까요?");               // 확인/취소 → boolean

typeof 3.14                                      // "number" (정수·실수 구분 없음)
typeof "abc"                                     // "string"
typeof true                                      // "boolean"
typeof undefined                                 // 값을 아직 안 넣음
null                                             // "없음"을 일부러 넣은 값
const msg = `${name}님 ${list.length}건`;         // 템플릿 리터럴 (백틱 + ${})
Number("42")                                     // 문자열 → 숫자 (실패하면 NaN)
parseInt("42px")                                 // 앞에서 읽히는 만큼 → 42
String(42)                                       // 숫자 → 문자열
```

## day03~04 — 연산자·조건문

```javascript
+ - * / % **                                     // 산술 (**는 거듭제곱)
=== !==                                          // 값+타입 비교 (==는 안 씀)
&& || !                                          // 논리 (단축 평가)
조건 ? 참 : 거짓                                   // 삼항
"1" + 1                                          // "11" — 한쪽이 문자열이면 이어붙임

if (score >= 90) { }                             // 조건문
else if (score >= 80) { }                        // 계단은 큰 값부터
else { }
switch (grade) {                                 // switch (break 없으면 흘러내림)
    case "A": break;
    default: break;
}
if (!title) { alert("제목 입력"); return; }        // falsy 검사 (빈문자열·null·undefined·0)
```

## day05 — 반복문

```javascript
for (let i = 0; i < 10; i++) { }                 // 기본 for
while (n > 0) { n--; }                           // 조건 반복
for (const item of list) { }                     // 배열의 값을 하나씩
for (const key in obj) { }                       // 객체의 키를 하나씩
break;  continue;                                // 탈출 / 건너뛰기
for (let i = 0; i < list.length; i++) { }        // 인덱스 필요할 때
```

## day07 — 객체

```javascript
const post = { title: "제목", content: "내용" };   // 객체 리터럴 (설계도 없이 즉석)
post.title                                       // 점 접근
post["title"]                                    // 대괄호 접근 (키가 변수일 때)
post.views = 0;                                  // 속성 추가 (대입하면 생김)
delete post.views;                               // 속성 삭제
const object = { title, content, pwd };          // 단축 속성명 (변수명 = 키)
const b = a;                                     // 주소 복사 (같은 객체를 봄)
```

## day10 — 함수

```javascript
function add(x, y) { return x + y; }             // 선언식
const sub = function (x, y) { return x - y; };   // 표현식
const mul = (x, y) => x * y;                     // 화살표 (식 하나면 return 생략)
function greet(name = "손님") { }                 // 기본값 매개변수
button.addEventListener("click", () => save());  // 함수를 값으로 넘기기 (콜백)
// 같은 이름으로 다시 정의하면 덮어씀 (오버로딩 없음)
```

## day11 — DOM 조작

```javascript
const el = document.querySelector("#titleInput");     // CSS 선택자로 요소 하나
const rows = document.querySelectorAll(".row");       // 전부 (NodeList)
el.value                                         // input·textarea 값 읽기
el.value = "";                                   // 입력창 비우기
viewTitle.innerHTML = post.title;                // 표시 요소에 HTML 넣기
viewTitle.textContent = post.title;              // 글자 그대로 (XSS 안전)
btn.addEventListener("click", writefunc);        // 이벤트 걸기
e.preventDefault();                              // 기본 동작(제출·이동) 막기
location.href = "list.html";                     // 페이지 이동
```

## day12~14 — 배열 조작·CRUD

```javascript
const list = [];                                 // 빈 배열
list.push(object);                               // 끝에 추가 (Create)
list.splice(i, 1);                               // i번째 삭제 (Delete)
list.splice(i, 0, item);                         // i번째에 삽입
list.length                                      // 개수
list.indexOf("b")                                // 위치 (없으면 -1)
list.includes("b")                               // 포함 여부
const found = list.find(b => b.no === no);       // 조건 맞는 첫 요소 (Read)
const idx = list.findIndex(b => b.no === Number(no));  // 그 위치 (no ≠ 인덱스!)
if (idx === -1) { alert("없습니다"); return; }     // 못 찾음 검사 후 조작
const mine = list.filter(b => b.writer === name);     // 조건 맞는 것만 새 배열
const titles = list.map(b => b.title);           // 각 요소 변환한 새 배열
list.sort((a, b) => b.no - a.no);                // 숫자 내림차순 (최신순)
boardList[i].title = title.value;                // 수정 (Update)

// 게시판 관용구
object.no = list.length == 0 ? 1 : list[list.length - 1].no + 1;  // 자동 번호
html += `<tr><td><a href="view.html?no=${b.no}">${b.title}</a></td></tr>`;  // 목록 행
tbody.innerHTML = html;                          // 다 만들고 마지막에 한 번만 대입
input.value = 기존값;                             // 수정 화면: 폼에 기존 값 채우기
if (confirm == object.pwd) { }                   // 비밀번호 확인 후 삭제
```

## day13 — 웹 스토리지·인터벌·쿼리스트링

```javascript
localStorage.setItem("boardList", JSON.stringify(list));  // 저장 (문자열만 가능)
let boardList = localStorage.getItem("boardList");        // 꺼내기 (없으면 null)
if (boardList == null) boardList = [];                    // 첫 실행 대비
else boardList = JSON.parse(boardList);                   // 문자열 → 배열 복원
localStorage.removeItem("boardList");            // 키 삭제
JSON.stringify(obj)                              // 객체 → 문자열
JSON.parse(text)                                 // 문자열 → 객체

const id = setInterval(() => next(), 3000);      // 3초마다 반복 (슬라이드)
clearInterval(id);                               // 반복 멈추기
setTimeout(() => fn(), 3000);                    // 3초 뒤 한 번
idx = (idx + 1) % images.length;                 // 순환 인덱스 (끝나면 0으로)

const url = new URLSearchParams(location.search);     // ?no=3 파싱
let selectNo = url.get("no");                    // 값 꺼내기 (문자열로 옴!)
list.find(b => b.no === Number(no));             // Number 변환 후 === 비교
```

## 자주 쓰는 코드 ※ (수업 밖 — 위와 중복 없음)

### 관용 연산자·구조 분해

```javascript
const name = input ?? "기본값";                    // null·undefined일 때만 기본값
const city = user?.address?.city;                 // 중간이 null이어도 안 터짐
onSave?.();                                       // 함수가 있으면 호출
const { title, price } = product;                 // 객체 구조 분해
const [first, ...rest] = list;                    // 배열 구조 분해 + 나머지
const copy = { ...post, title: "새 제목" };        // 일부만 바꾼 사본 (원본 유지)
const added = [...list, newItem];                 // 추가된 새 배열
const merged = { ...defaults, ...options };       // 병합 (뒤가 이김)
```

### 배열·객체 심화

```javascript
const total = cart.reduce((s, i) => s + i.price, 0);  // 합계 (배열 → 값 하나)
const exists = list.some(b => b.no === no);       // 하나라도 있나
const allDone = list.every(b => b.done);          // 전부 그런가
const page = list.slice(0, 10);                   // 잘라낸 새 배열 (페이징)
const unique = [...new Set(arr)];                 // 중복 제거
names.join(", ")                                  // 배열 → 문자열
Object.keys(obj)  Object.values(obj)              // 키 배열 / 값 배열
Object.entries(obj)                               // [키, 값] 쌍 배열
list.forEach((item, i) => { });                   // 반환 없이 돌기 (인덱스 포함)
```

### 문자열·날짜

```javascript
s.includes("검색어")                               // 포함 여부
s.trim()                                          // 공백 제거
s.split(",")                                      // 잘라 배열로
s.padStart(2, "0")                                // "9" → "09" (시계 표시)
new Date().toISOString()                          // 저장용 시간 (사전순 = 시간순)
new Date().toLocaleDateString("ko-KR")            // "2026. 8. 21." 표시용
list.sort((a, b) => new Date(b.createdAt) - new Date(a.createdAt));  // 최신순
```

### DOM·비동기

```javascript
el.classList.add("active");                       // 클래스 넣기
el.classList.toggle("open");                      // 껐다켰다
const row = btn.closest("tr");                    // 위로 올라가며 조상 찾기
const no = Number(btn.dataset.no);                // data-no="3" 읽기
const tr = document.createElement("tr");          // 요소 생성
tbody.appendChild(tr);                            // 붙이기
el.remove();                                      // 요소 삭제
const res = await fetch("/api/boards");           // GET 요청
const data = await res.json();                    // 응답 → 객체
await fetch(url, { method: "POST",                // POST 요청
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(post) });
const [a, b] = await Promise.all([fetchA(), fetchB()]);  // 동시에 보내고 다 기다림
```
