---
출처: Claude 분석
원본: KDT_2026/2026_FE/day12
작성일: 2026-08-10
tags: [학습, javascript]
---

# JS day12 — 제품·사원 관리 CRUD

> 실습 파일: `day12/pracitce/practice8.js`(제품 관리), `practice9.js`(사원·부서·휴가), `practice8.html/css`, `index.html`
> 허브: [[JavaScript MOC]] · 이전: [[JS day11 DOM 조작]] · 다음: [[JS day13 웹 스토리지와 인터벌]]

## 1. 배운 내용

이 날이 **설계 → 구현** 흐름을 처음으로 제대로 밟은 날입니다. `practice8.js` 상단에 요구사항·메모리 설계·기능 설계를 전부 글로 적어두고 코드를 작성했습니다.

### 1-1. 3단계 개발 절차

절차는 이렇습니다.

```
1. 기획서/요구사항에 따른 프로토타입
2. 메모리 설계
   1) 저장해야 할 것들을 모두 찾아보기
   2) 속성들 간의 종속관계 파악, 테이블 나누기
   3) 쪼개진 테이블 간 연관 만들기 (관계형 데이터베이스)
   4) JS(JSON)로 표현
3. 기능 설계 : CRUD, REST API
```

**코드를 치기 전에 데이터부터 설계한다** — 이 순서가 핵심입니다.

### 1-2. 메모리 설계 — 정규화를 손으로

사고 과정을 따라가면 이렇습니다.

**① 한 테이블에 다 넣으면**
```
카테고리명  제품명   가격   이미지     등록일
음료        콜라     1000   xxx.png   2026-07-22
음료        사이다   2000   xxx.png   2026-07-23
```
`음료`가 반복됩니다. 카테고리 이름을 바꾸려면 모든 행을 고쳐야 합니다.

**② 테이블을 쪼개면**
```
카테고리코드  카테고리명
1            음료
2            과자

제품코드  제품명   가격   이미지    등록일       카테고리코드(FK)
1        콜라     1000   XXX.PNG  2026-07-22   1
2        사이다   2000   XXX.PNG  2026-07-22   1
```

규칙은 두 가지입니다.
- **테이블당 식별자(PRIMARY KEY) 1개 이상 권장**
- **상하관계를 파악해서 식별자를 하위 요소에 저장** (FOREIGN KEY, 교집합)

이건 SQL day02 테이블과 제약조건 의 정규화·PK·FK와 **완전히 같은 이야기**입니다. DB를 배우기 전에 JS에서 먼저 필요성을 체감한 셈입니다.

**③ JS로 표현**
> 표 = 배열 / 객체 = 행 / 열 = 속성

```javascript
let categoryList = [
  { ccode: 1, cname: "음료" },
  { ccode: 2, cname: "과자" },
];

let productList = [
  { pcode: 1, pname: "콜라", pprice: 1000, pimg: "https://placehold.co/100x100",
    pdate: "2026-07-22", ccode: 1 },
  { pcode: 2, pname: "환타", pprice: 2000, pimg: "https://placehold.co/100x100",
    pdate: "2026-07-23", ccode: 1 },
];
```

`ccode`가 두 배열을 잇는 연결고리입니다. → JS day07 객체

### 1-3. 기능 설계 — CRUD 4함수

각 기능마다 **실행조건 / 함수명 / 매개변수 / 반환값**을 미리 정했습니다.

| 기능 | 실행조건 | 함수명 | 매개변수 | 반환값 |
| --- | --- | --- | --- | --- |
| 등록 (CREATE) | 등록 버튼 클릭 | `productAdd` | x | x |
| 조회 (READ) | JS 열릴 때 / 최신화 | `productPrint` | x | x |
| 수정 (UPDATE) | 수정 버튼 클릭 | `productUpdate` | 수정할 제품코드 | x |
| 삭제 (DELETE) | 삭제 버튼 클릭 | `productDelete` | 삭제할 제품코드 | x |

**"누구를(대상)"을 매개변수로 받는다**가 판단 기준입니다. 조회는 전체를 다시 그리므로 매개변수가 필요 없고, 수정·삭제는 대상을 지목해야 합니다.

### 1-4. 조회 함수 — 배열 조인 + HTML 문자열 생성

```javascript
productPrint();   // JS가 열릴 때 최초 1번 실행

function productPrint() {
  // 1. 어디에
  let tbody = document.querySelector("#main table tbody");

  // 2. 무엇을 — 배열 내 모든 객체를 HTML 문자열로 구성
  let html = "";
  for (let index = 0; index <= productList.length - 1; index++) {
    let product = productList[index];

    // 제품의 카테고리번호에 해당하는 카테고리명 찾기
    let cname = "";
    for (let j = 0; j <= categoryList.length - 1; j++) {
      if (categoryList[j].ccode == product.ccode) {
        cname = categoryList[j].cname;
        break;   // 찾았으면 끝
      }
    }

    html += `<tr>
      <td><img src=${product.pimg} /></td>
      <td>${cname}</td> <td>${product.pname}</td>
      <td>${product.pprice}</td> <td>${product.pdate}</td>
      <td>
        <button class="deleteBtn" onClick="productDelete(${product.pcode})">삭제</button>
        <button class="updateBtn" onClick="productUpdate(${product.pcode})">수정</button>
      </td>
    </tr>`;
  }

  // 3. 출력
  tbody.innerHTML = html;
}
```

**주석의 "1. 어디에 → 2. 무엇을 → 3. 출력" 3단계**가 [[JS day11 DOM 조작]] 의 패턴 그대로입니다.

이중 반복문이 하는 일이 곧 **SQL의 JOIN**입니다.
```sql
SELECT c.cname, p.pname, p.pprice
FROM productList p JOIN categoryList c ON p.ccode = c.ccode;
```
→ SQL day03 DML과 조인

`html` 문자열을 다 만든 뒤 **마지막에 한 번만** `innerHTML`에 대입한 것도 잘한 부분입니다. 반복문 안에서 `innerHTML +=`를 하면 매번 전체를 다시 그립니다.

**버튼에 코드를 심는 기법**
```javascript
onClick="productDelete(${product.pcode})"
```
템플릿 리터럴 안에서 각 행마다 자기 `pcode`를 인자로 넣습니다. 어느 버튼을 눌렀는지 함수가 알 수 있게 되는 핵심 트릭입니다.

### 1-5. 삭제 함수

```javascript
function productDelete(pcode) {
  for (let index = 0; index <= productList.length - 1; index++) {
    if (productList[index].pcode == pcode) {
      productList.splice(index, 1);   // splice(인덱스, 개수)
      alert("삭제 성공");
      productPrint();                 // 조회구역 최신화
      return;   // 주의: return은 function{} 탈출, break는 for{} 탈출
    }
  }
}
```

`return` 과 `break` 를 구분해야 합니다. 여기서는 삭제 후 함수를 아예 끝내야 하므로 `return`이 맞습니다.

**`productPrint()` 재호출**이 중요합니다. 배열만 바꾸면 화면은 그대로이므로, 데이터를 바꾼 뒤 항상 다시 그려야 합니다.

```
데이터 변경 → 화면 다시 그리기
```
이 패턴이 React의 사고방식과 정확히 같습니다.

### 1-6. 수정 함수

```javascript
function productUpdate(pcode) {
  for (let index = 0; index <= productList.length - 1; index++) {
    if (productList[index].pcode == pcode) {
      let newPname = prompt("수정할 제품명 입력하세요.");
      let newPprice = prompt("수정할 가격 입력하세요.");
      productList[index].pname = newPname;
      productList[index].pprice = newPprice;
      // ... productPrint()
    }
  }
}
```

### 1-7. practice9 — 3개 테이블 관리 시스템

`practice9.js`는 한 단계 더 복잡합니다. **부서 → 사원 → 휴가** 3단 관계입니다.

```javascript
let departmentList = [
  { dcode: 1, dname: "개발팀" },
  { dcode: 2, dname: "디자인팀" },
  { dcode: 3, dname: "기획팀" },
];
let lastDepartmentCode = departmentList.length;

let employeeList = [
  { ecode: 1, dcode: 1, ename: "김민준", eposition: "선임 개발자",
    eimg: "https://placehold.co/100x100" },
  { ecode: 2, dcode: 2, ename: "이서연", eposition: "수석디자이너", ... },
];
let lastEmployeeCode = employeeList.length;   // 최근 발급된 마지막 사원 코드

let vacationList = [
  { vcode: 1, ecode: 1, vstart: "2025-08-04", vend: "2025-08-04", vreason: "병원 진료" },
  { vcode: 2, ecode: 2, vstart: "2025-07-21", vend: "2025-07-25", vreason: "여름 휴가" },
];
```

```
부서(dcode) ──1:N──▶ 사원(ecode, dcode) ──1:N──▶ 휴가(vcode, ecode)
```

`lastDepartmentCode`, `lastEmployeeCode` 변수가 **AUTO_INCREMENT를 손으로 구현**한 것입니다. 새 항목을 추가할 때 `++lastEmployeeCode`로 번호를 발급합니다. → SQL day02 테이블과 제약조건

```javascript
departmentPrint();
function departmentPrint() {
  let tbody = document.querySelector(".card table tbody");
  let html = "";
  let eDepartment = document.querySelector(".e-department");   // 사원 등록 폼의 부서 select
  ...
}
```

부서 목록을 그릴 때 **사원 등록 폼의 `<select>` 옵션도 같이 갱신**하는 구조입니다. 부서가 추가되면 드롭다운에도 즉시 반영됩니다. 한 함수가 두 곳을 동시에 최신화하는 실전 패턴입니다.

## 2. 추가로 알면 좋은 활용법

### 2-1. 조인을 함수로 분리

카테고리명을 찾는 이중 반복문을 함수로 빼면 재사용됩니다.

```javascript
function findCategoryName(ccode) {
  const c = categoryList.find(c => c.ccode === ccode);
  return c ? c.cname : "";
}
```

`find`가 이중 반복문을 대체합니다. → JS day03 자료형과 연산자

```javascript
const html = productList.map(p => `
  <tr>
    <td><img src="${p.pimg}" /></td>
    <td>${findCategoryName(p.ccode)}</td>
    <td>${p.pname}</td>
    <td>${p.pprice.toLocaleString()}원</td>
    <td>${p.pdate}</td>
    <td>
      <button onclick="productDelete(${p.pcode})">삭제</button>
      <button onclick="productUpdate(${p.pcode})">수정</button>
    </td>
  </tr>
`).join("");
```

`map` + `join`이 `for` + `+=`를 대체합니다.

### 2-2. 데이터가 많아지면 Map으로

`find`는 O(n)이라 제품 1000개 × 카테고리 100개면 느려집니다.

```javascript
const categoryMap = new Map(categoryList.map(c => [c.ccode, c.cname]));
categoryMap.get(product.ccode);   // O(1)
```

DB가 인덱스를 쓰는 이유와 같습니다. → SQL day03 DML과 조인

### 2-3. 등록 함수 구현하기

`productAdd`는 설계만 있고 구현이 이어집니다. 필요한 것들을 정리하면:

```javascript
let lastProductCode = productList.length;

function productAdd() {
  const ccode = Number(document.querySelector("#category").value);
  const pname = document.querySelector("#pname").value.trim();
  const pprice = Number(document.querySelector("#pprice").value);
  const file = document.querySelector("#pimg").files[0];

  if (!pname)  { alert("제품명을 입력하세요."); return; }
  if (!pprice) { alert("가격을 입력하세요."); return; }

  productList.push({
    pcode: ++lastProductCode,
    pname, pprice, ccode,
    pimg: file ? URL.createObjectURL(file) : "https://placehold.co/100x100",
    pdate: new Date().toISOString().slice(0, 10),   // "2026-08-10"
  });

  productPrint();
}
```

**파일 업로드 미리보기**는 `URL.createObjectURL(file)`로 만듭니다. 서버 없이도 첨부한 이미지를 바로 보여줄 수 있습니다.

**오늘 날짜 자동 기록**은 `new Date().toISOString().slice(0, 10)`이 가장 간단합니다.

### 2-4. `<select>` 옵션을 데이터로 그리기

```javascript
document.querySelector("#category").innerHTML = categoryList
  .map(c => `<option value="${c.ccode}">${c.cname}</option>`)
  .join("");
```

`practice9.js`가 부서 select에 하는 일이 이것입니다. 카테고리를 추가하면 드롭다운이 자동으로 늘어납니다.

### 2-5. 수정 시 기존 값 보여주기

```javascript
let newPname = prompt("수정할 제품명 입력하세요.");
```

`prompt`의 두 번째 인자가 기본값입니다.
```javascript
const p = productList[index];
let newPname = prompt("수정할 제품명", p.pname);
if (newPname === null) return;          // 취소를 누르면 null
```

`prompt`는 취소 시 `null`을 반환하므로 검사가 필요합니다. → JS day02 변수와 입출력

또 `prompt`로 받은 값은 **항상 문자열**이라 가격은 `Number()` 변환이 필요합니다.
```javascript
p.pprice = Number(newPprice);
```

### 2-6. 참조 삭제 시 주의

카테고리를 지울 때 그 카테고리를 쓰는 제품이 남아 있으면 `cname`이 빈 문자열이 됩니다.

```javascript
function categoryDelete(ccode) {
  const used = productList.some(p => p.ccode === ccode);
  if (used) { alert("이 카테고리를 사용하는 제품이 있어 삭제할 수 없습니다."); return; }
  // ...
}
```

이게 DB의 `ON DELETE RESTRICT`를 JS로 구현한 것입니다. 부서를 지울 때 사원이 남아 있는 `practice9`에도 그대로 필요합니다. → SQL day02 테이블과 제약조건

## 3. 더 나아가 알면 좋은 것

### 3-1. 상태와 렌더링 분리

지금 구조가 이미 이 형태에 가깝습니다.

```javascript
// 상태
let productList = [...];

// 렌더링 — 상태를 화면으로 바꾸는 함수 하나
function productPrint() { ... }

// 조작 — 상태만 바꾸고 렌더링 호출
function productDelete(pcode) { /* 배열 수정 */ productPrint(); }
```

**"데이터를 바꾸고 다시 그린다"** 는 이 패턴이 React의 핵심 사고방식입니다. React는 `productPrint()` 호출을 자동으로 해주는 것뿐입니다.

### 3-2. 이벤트 위임으로 onclick 없애기

```javascript
onClick="productDelete(${product.pcode})"   // HTML에 JS가 섞임
```

```html
<button class="deleteBtn" data-code="${p.pcode}">삭제</button>
```
```javascript
tbody.addEventListener("click", (e) => {
  const code = Number(e.target.dataset.code);
  if (e.target.classList.contains("deleteBtn")) productDelete(code);
  if (e.target.classList.contains("updateBtn")) productUpdate(code);
});
```

행이 계속 다시 그려져도 **이벤트는 부모에 한 번만** 등록하면 됩니다. → [[JS day11 DOM 조작]]

### 3-3. 새로고침하면 사라지는 문제

지금은 배열이 메모리에만 있어 F5를 누르면 초기 데이터로 돌아갑니다.

```javascript
function save() {
  localStorage.setItem("productList", JSON.stringify(productList));
}
function load() {
  productList = JSON.parse(localStorage.getItem("productList") ?? "[]");
}
```

[[JS day13 웹 스토리지와 인터벌]] 에서 배우는 내용이 정확히 이 문제의 답입니다.

### 3-4. REST API로 가는 길

주석에 `CRUD, RESTAPI`라고 적어두셨습니다. 함수 4개가 그대로 API 4개에 대응합니다.

| 함수 | HTTP | 엔드포인트 | SQL |
| --- | --- | --- | --- |
| `productPrint` | GET | `/products` | `SELECT` |
| `productAdd` | POST | `/products` | `INSERT` |
| `productUpdate` | PUT | `/products/{pcode}` | `UPDATE` |
| `productDelete` | DELETE | `/products/{pcode}` | `DELETE` |

```javascript
async function productPrint() {
  const res = await fetch("/api/products");
  productList = await res.json();
  render();
}
```

배열 조작이 `fetch` 호출로 바뀔 뿐 **구조는 그대로**입니다.

### 3-5. 백엔드 버전과 나란히 보기

같은 설계를 자바로 옮기면 Java day07 메소드와 미니프로젝트 의 `miniProject`가 됩니다.

| | JS (day12) | Java (day07) |
| --- | --- | --- |
| 데이터 | 객체 배열 | 클래스 + 배열 |
| 조회 | `productPrint()` | `findAll()` |
| 등록 | `productAdd()` | `저장함수()` |
| 화면 | HTML 테이블 | 콘솔 출력 |
| 연결 | `ccode`로 조인 | FK로 참조 |

**프론트에서 배열로 푼 관계형 설계가 백엔드에서는 테이블이 됩니다.**

## 실습 파일

- `2026_FE/day12/pracitce/practice8.js`, `practice8.html`, `practice8.css`
- `2026_FE/day12/pracitce/practice9.js`
- `2026_FE/day12/pracitce/index.html`

## 관련 노트

[[JavaScript MOC]] · [[JS day11 DOM 조작]] · [[JS day13 웹 스토리지와 인터벌]] · JS day07 객체 · SQL day02 테이블과 제약조건 · SQL day03 DML과 조인 · Java day07 메소드와 미니프로젝트
