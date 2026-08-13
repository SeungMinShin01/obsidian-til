---
출처: Claude 분석
원본: KDT_2026/2026_FE/LevelUP, extra_assignment
작성일: 2026-08-10
tags: [학습, javascript]
---

# JS 과제 — LevelUP과 Message_Board

> 실습 파일: `LevelUP/LevelUPJS/1`(키오스크 모델링), `4`(틱택토), `5`(구독 조인), `LevelUpHTML/`, `extra_assignment/Massage_Board/`
> 허브: [[JavaScript MOC]]

## 1. LevelUP 과제

LevelUP은 **제약을 걸어 사고를 강제하는** 과제 모음입니다. 문법을 아는 것과 문제를 푸는 것이 다르다는 걸 체감시키는 방식입니다.

### 1-1. LevelUp1 — 데이터 모델링

문제는 코드가 아니라 **시나리오**로 주어집니다.

```
1. 고객1(유재석)이 키오스크에서 '커피' 카테고리를 선택하여 아이스아메리카노 2개 주문 요청
2. 고객1(유재석)은 주문번호를 받아서 대기한다.
3. 고객2(강호동)이 '커피' 카테고리에서 카페라떼 1개,
   '스무디' 카테고리에서 사과스무디 2개 주문 요청
4. 고객2(강호동)은 주문번호를 받아서 대기한다.

- 위 시나리오에 따른 필요한 데이터들을 찾아서
  변수와 자료형들을 이용하여 구성하시오.
```

주석에 스스로 문제를 다시 정의하셨습니다.
> 데이터를 표현하라? → 필요한 변수와 타입을 정하라

```javascript
const 카테고리 = ["커피", "스무디"];
const 고객 = ["유재석", "강호동"];
const 음료 = [
  { 카테고리: 커피, 이름: 아이스아메리카노 },
  { 카테고리: 커피, 이름: 카페라떼 },
  { 카테고리: 스무디, 이름: 사과스무디 },
];
```

**"코드를 짜라"가 아니라 "무엇을 저장할지 정하라"** 는 문제입니다. [[JS day12 제품 사원 관리 CRUD]] 의 메모리 설계와 완전히 같은 종류의 사고이고, 실제로 day12에서 이 방식이 체계화됩니다.

한 걸음 더 나가면 코드 대신 문자열로 참조하고, 주문·주문상세를 분리하게 됩니다.

```javascript
const 카테고리 = [
  { ccode: 1, cname: "커피" },
  { ccode: 2, cname: "스무디" },
];
const 음료 = [
  { mcode: 1, ccode: 1, mname: "아이스아메리카노", price: 4500 },
  { mcode: 2, ccode: 1, mname: "카페라떼",         price: 5000 },
  { mcode: 3, ccode: 2, mname: "사과스무디",        price: 5500 },
];
const 주문 = [
  { ocode: 1, 고객명: "유재석", 주문시각: "2026-07-01T10:00" },
  { ocode: 2, 고객명: "강호동", 주문시각: "2026-07-01T10:03" },
];
const 주문상세 = [
  { ocode: 1, mcode: 1, 수량: 2 },
  { ocode: 2, mcode: 2, 수량: 1 },
  { ocode: 2, mcode: 3, 수량: 2 },   // 한 주문에 여러 음료 → 1:N
];
```

**"고객2가 두 카테고리에서 각각 주문"** 이라는 조건이 `주문`과 `주문상세`를 나눠야 하는 이유입니다. 주문 1건에 음료가 여러 개 들어가기 때문입니다. [[SQL day02 테이블과 제약조건]] 의 1:N 관계와 같습니다.

`LevelUp2.html`, `LevelUp2.js`는 같은 폴더에서 화면과 연결하는 연습입니다.

### 1-2. LevelUp2 — 초를 HH:MM:SS로 (if / for / Math 금지)

```
"초 단위 → HH:MM:SS"
0 이상 정수 초 입력
단, 분·초가 한 자리면 앞에 0을 붙여 출력
if / for / Math 금지

1시간~   = 3600
1분~59분 = 60 ~ 3540
1초~59초 = 1 ~ 59
```

제어문을 전부 막았으므로 **삼항 연산자만으로** 풀어야 합니다.

```javascript
let hour =
  second < 0
    ? null
    : parseInt(second / 3600) < 0
      ? "00"
      : parseInt(second / 3600) >= 100
        ? null
        : parseInt(second / 3600) > 9
          ? `${parseInt(second / 3600)}`
          : `0${parseInt(second / 3600)}`;
```

중첩 삼항 5단으로 **음수 / 0시간 / 100시간 초과 / 두 자리 / 한 자리**를 전부 분기했습니다. [[JS day03 자료형과 연산자]] 의 중첩 삼항이 실전에서 어디까지 갈 수 있는지 보여주는 예입니다.

`Math` 금지라 `Math.floor` 대신 `parseInt`로 정수 부분을 얻은 것도 조건을 잘 우회한 부분입니다.

**제약을 풀면** 훨씬 짧아집니다.
```javascript
const pad = (n) => String(n).padStart(2, "0");
const toHMS = (s) =>
  `${pad(Math.floor(s / 3600))}:${pad(Math.floor(s / 60) % 60)}:${pad(s % 60)}`;
```

`padStart(2, "0")`가 "한 자리면 앞에 0" 조건을 한 번에 처리합니다. `% 60`이 분을 0~59로 가둡니다. [[JS day13 웹 스토리지와 인터벌]] 의 시계 함수에서 쓴 `second < 10 ? "0" + second : second`도 `padStart`로 대체됩니다.

**이 과제의 목적**은 결국 "삼항으로 이렇게까지 할 수 있지만, 그래서 `if`와 헬퍼 함수가 왜 필요한가"를 느끼게 하는 것입니다.

### 1-3. LevelUp4 — 틱택토 (함수 금지, while 필수)

```
칸 번호 입력 (0~8)

1. 입력값 검증 — 0~8 범위를 벗어나면 "잘못된 위치입니다."
2. 자리 중복 검사 — 이미 값이 있으면 "이미 선택된 자리입니다."
3. 정상 입력이면 현재 플레이어 기호(X / O)를 해당 인덱스에 저장
4. 턴 교체 — X → O, O → X

추가 제한
- while 반복문 구성
- 게임 승리 조건 배열을 별도로 구성하여 반복문으로 검사할 것
- 함수 사용 금지
```

```javascript
let turn = 0;
let 승자 = " ";
let 게임판 = [
  [" ", " ", " "],
  [" ", " ", " "],
  [" ", " ", " "],
];
let 게임종료 = false;
```

**"승리 조건을 배열로 만들어 반복문으로 검사하라"** 는 조건이 핵심입니다. `if`를 8번 나열하는 대신 데이터로 만들라는 뜻입니다.

```javascript
const 승리조건 = [
  [0,1,2], [3,4,5], [6,7,8],   // 가로
  [0,3,6], [1,4,7], [2,5,8],   // 세로
  [0,4,8], [2,4,6],            // 대각선
];

for (const [a, b, c] of 승리조건) {
  if (판[a] !== " " && 판[a] === 판[b] && 판[b] === 판[c]) {
    승자 = 판[a];
    게임종료 = true;
  }
}
```

**조건을 코드가 아니라 데이터로 표현**하는 사고가 이 과제의 진짜 목표입니다. 3×3을 4×4로 바꿔도 배열만 교체하면 됩니다.

2차원 배열(`게임판[i][j]`)보다 1차원 배열(`판[0]`~`판[8]`)이 이 문제에는 더 편합니다. 입력이 0~8 한 자리 번호이기 때문입니다.

`day04/practice/tictackto.js`에서 만든 버전과 비교해보면, 함수를 쓸 수 있을 때와 없을 때의 차이가 드러납니다. → [[JS day04 조건문]]

### 1-4. LevelUp5 — 객체 배열 조인

세 배열을 코드로 연결하는 문제입니다.

```javascript
const 회원정보 = [
  { 회원코드: 1, 아이디: "user1", 회원이름: "김개발" },
  { 회원코드: 2, 아이디: "user2", 회원이름: "최코딩" },
  { 회원코드: 3, 아이디: "user3", 회원이름: "박서버" },
];

const 구독상품 = [
  { 상품코드: "P01", 상품명: "프로",     가격: 30000, 구독기간: 30 },
  { 상품코드: "P02", 상품명: "프리미엄", 가격: 15000, 구독기간: 30 },
  { 상품코드: "P03", 상품명: "베이직",   가격: 9900,  구독기간: 30 },
];

const 구독내역 = [
  { 회원코드: 1, 상품코드: "P02", 구독일자: "2026-07-15", 구독상태: "활성" },
  { 회원코드: 2, 상품코드: "P03", 구독일자: "2026-06-14", 구독상태: "만료" },
];
```

```
회원정보 ─(회원코드)─ 구독내역 ─(상품코드)─ 구독상품
```

**사실상 DB의 JOIN을 JS로 구현하는 문제입니다.** `database/day03.sql`의 `member` ↔ `buy` 관계와 같은 구조이고, `구독내역`이 N:M을 푸는 중간 테이블 역할을 합니다. → [[SQL day03 DML과 조인]]

### 1-5. LevelUp5 풀이 방향

**JOIN — 회원명·상품명 붙이기**
```javascript
const 결과 = 구독내역.map(내역 => {
  const 회원 = 회원정보.find(m => m.회원코드 === 내역.회원코드);
  const 상품 = 구독상품.find(p => p.상품코드 === 내역.상품코드);
  return {
    회원이름: 회원.회원이름,
    상품명: 상품.상품명,
    가격: 상품.가격,
    구독상태: 내역.구독상태,
    구독일자: 내역.구독일자,
  };
});
```

**WHERE / SUM / ORDER BY**
```javascript
const 활성 = 결과.filter(r => r.구독상태 === "활성");
const 총매출 = 활성.reduce((sum, r) => sum + r.가격, 0);
결과.sort((a, b) => b.가격 - a.가격);
```

**LEFT JOIN — 구독 없는 회원도 포함**
```javascript
const 전체 = 회원정보.map(m => {
  const 내역 = 구독내역.find(s => s.회원코드 === m.회원코드);
  return { ...m, 구독상태: 내역?.구독상태 ?? "미구독" };
});
```

`박서버`(회원코드 3)는 구독내역이 없어 `find`가 `undefined`를 반환합니다. `?.`와 `??`로 처리합니다. → [[JS day03 자료형과 연산자]]

**GROUP BY 흉내내기**
```javascript
const 상품별매출 = 결과.reduce((acc, r) => {
  acc[r.상품명] = (acc[r.상품명] ?? 0) + r.가격;
  return acc;
}, {});
// { 프리미엄: 15000, 베이직: 9900 }
```

**SQL 대응표**

| SQL | JS |
| --- | --- |
| `JOIN ... ON` | `map` + `find` |
| `LEFT JOIN` | `map` + `find` + `??` |
| `WHERE` | `filter` |
| `SUM()` | `reduce` |
| `ORDER BY` | `sort` |
| `COUNT()` | `length` |
| `GROUP BY` | `reduce`로 객체 누적 |

### 1-6. 성능 — find는 O(n)입니다

```javascript
const 회원맵 = new Map(회원정보.map(m => [m.회원코드, m]));
const 상품맵 = new Map(구독상품.map(p => [p.상품코드, p]));

const 결과 = 구독내역.map(내역 => ({
  회원이름: 회원맵.get(내역.회원코드).회원이름,   // O(1)
  상품명: 상품맵.get(내역.상품코드).상품명,
}));
```

`find`를 반복문 안에서 쓰면 O(n×m), Map을 쓰면 O(n+m)입니다. DB가 인덱스를 쓰는 이유와 완전히 같습니다. [[JS day12 제품 사원 관리 CRUD]] 의 카테고리 조회에도 그대로 적용됩니다.

### 1-7. LevelUpHTML

`LevelUpHTML/LevelUP1.html`은 마크업만 다루는 별도 과제입니다. → [[HTML MOC]]

## 2. Message_Board — 제약이 만든 설계

### 2-1. 과제 조건

`extra_assignment/Massage_Board/Message_Board` 파일에 적힌 전제조건입니다.
> **배열, 객체 사용 금지. 변수, 제어문, 반복문만 사용**

### 2-2. 설계

- 게시글 **10개 제한** → `title1`~`title10`, `Description1`~`Description10`, `index1`~`index10` 변수를 수동 선언
- `index = -1`을 **빈 칸** 표시로 사용
- `index = currentIndex + 1`로 최신순 정렬 기준 확보 (index가 높을수록 최신)
- 정렬은 **버블 정렬 9회전**

파일에 남긴 사고 과정이 좋습니다.
> 게시글을 무한히 쓸 수 있는가? 혹은 유동적으로 변수를 늘릴 수 있는가?
> → 쓸 수 있는 게시글 제한(10개), Index는 비어있는 공간(-1)과 정렬의 기준이 되는 변수

> 1~8번글까지 생성 → 2번글 삭제 → 다음 생성될 글은 2번글인가, 9번글인가
> → 비어있는 공간을 우선으로 글 생성

### 2-3. Java 버전과 완전히 같은 발상

[[Java day06 생성자와 콘솔 게시판]] 의 `OverallController.java`
```java
for (int index = 0; index <= posts.length - 1; index++) {
    if (posts[index] == null) {   // 빈 칸 찾기
        posts[index] = post;
        break;
    }
}
```

```javascript
// Message_Board — 배열이 없으니 if로 나열
if (index1 === -1) { title1 = 제목; index1 = ++currentIndex; }
else if (index2 === -1) { title2 = 제목; index2 = ++currentIndex; }
// ... 10번까지
```

**언어와 제약이 달라도 문제 해결 구조는 같습니다.**

### 2-4. 이 과제의 진짜 목적

"배열과 객체가 없으면 얼마나 불편한가"를 몸으로 겪게 하는 것입니다.

| | Message_Board | day14 게시판 |
| --- | --- | --- |
| 변수 | 30개 수동 선언 | 배열 1개 |
| 빈 칸 찾기 | if 10단 | 불필요 (가변) |
| 정렬 | 버블 정렬 직접 구현 | `sort()` 한 줄 |
| 저장 | 불가 (새로고침 시 소멸) | `localStorage` |
| 개수 제한 | 10개 | 무제한 |
| 코드 길이 | 수백 줄 | 수십 줄 |

그래서 [[JS day14 게시판 CRUD]] 에서 배열 + 객체 + localStorage로 다시 만들었을 때 코드가 1/5로 줄어든 겁니다.

### 2-5. 배열로 다시 쓰면

```javascript
let boards = [];
let currentIndex = 0;

function 작성(title, description) {
  if (boards.length >= 10) { alert("최대 10개까지"); return; }
  boards.push({ index: ++currentIndex, title, description });
}

function 삭제(index) {
  boards = boards.filter(b => b.index !== index);
}

function 목록() {
  return [...boards].sort((a, b) => b.index - a.index);   // 최신순
}
```

버블 정렬 9회전이 `sort()` 한 줄이 됩니다. 버블 정렬은 O(n²), `sort()`는 O(n log n)입니다.

## 3. 더 나아가 알면 좋은 것

### 3-1. 정렬 알고리즘 감각

| 알고리즘 | 복잡도 | 특징 |
| --- | --- | --- |
| 버블 정렬 | O(n²) | 구현 쉬움, 느림 |
| 선택 정렬 | O(n²) | 교환 횟수 적음 |
| 삽입 정렬 | O(n²) | 거의 정렬된 데이터에 빠름 |
| 병합 정렬 | O(n log n) | 안정 정렬 |
| 퀵 정렬 | O(n log n) 평균 | 실무 표준 |

JS의 `sort()`는 엔진마다 다르지만 대체로 팀소트(병합+삽입 혼합)입니다.

### 3-2. LevelUp1·4 — HTML/JS 연동

`LevelUPJS/1`, `4`는 HTML과 JS를 함께 다루는 과제입니다. `LevelUpHTML/LevelUP1.html`은 마크업 연습입니다. → [[HTML MOC]]

### 3-3. 이 과제들의 다음 단계

- **LevelUp5** → 실제 DB와 JOIN 쿼리로 → [[SQL day03 DML과 조인]]
- **Message_Board** → localStorage 게시판 → [[JS day14 게시판 CRUD]] → 서버 API

## 실습 파일

- `2026_FE/LevelUP/LevelUPJS/1/LevelUp1.js`, `LevelUp2.js`
- `2026_FE/LevelUP/LevelUPJS/4/LevelUp4.js`, `LevelUp4.html`
- `2026_FE/LevelUP/LevelUPJS/5/LevelUp5.js`, `LevelUp5.html`, `LevelUp5.css`
- `2026_FE/LevelUP/LevelUpHTML/LevelUP1.html`
- `2026_FE/extra_assignment/Massage_Board/Message_Board`, `Message_Board.js`, `Message_Board.html`

## 관련 노트

[[JavaScript MOC]] · [[JS day14 게시판 CRUD]] · [[JS day07 객체]] · [[SQL day03 DML과 조인]] · [[Java day06 생성자와 콘솔 게시판]]
