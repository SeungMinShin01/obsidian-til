---
출처: Claude 분석
원본: KDT_2026/2026_FE/day04
작성일: 2026-08-10
tags: [학습, html]
---

# HTML day04 — 폼과 테이블

> 실습 파일: `day04/exam/exam.txt`(입력 요소 정리), `exam1.html`, `exam2.html`(테이블)
> 허브: [[HTML MOC]] · 이전: HTML day02 문서 구조와 미디어 · 다음: HTML day15 테이블 마크업

## 1. 배운 내용

### 1-1. `<input>` 타입 8종 — exam.txt

```html
<input type="text" />
```

| `type` | 용도 |
| --- | --- |
| `text` | 일반 텍스트 |
| `password` | 비밀번호 (마스킹) |
| `file` | 첨부파일 |
| `datetime-local` | 날짜 / 시간 |
| `radio` | 단일 선택 |
| `checkbox` | 복수 선택 |
| `submit` | 폼 전송 |
| `button` | 일반 버튼 (**추후 JS 연동**) |

### 1-2. 주요 속성

| 속성 | 의미 |
| --- | --- |
| `value` | 입력된 값 |
| `disabled` | 사용 금지 (**전송도 안 됨**) |
| `readonly` | 읽기 모드 (**전송은 됨**) |
| `placeholder` | 입력 가이드 문구 |
| `name` | 서버 전송 시 식별 이름 |

`disabled`와 `readonly`의 차이가 실무에서 중요합니다. 값을 보여주되 서버로도 보내야 하면 `readonly`입니다.

### 1-3. 기타 폼 태그

```html
<textarea>긴 글 입력</textarea>

<select>
  <option>항목1</option>
  <option>항목2</option>
</select>

<button>버튼</button>
```

`<input type="text">`가 JS day11 DOM 조작 의 `.value`와 짝을 이룹니다. `<textarea>`, `<select>`도 마찬가지입니다.

### 1-4. 테이블 — exam2.html

```html
<table border="1">
  <thead>                          <!-- 제목 구역 -->
    <tr>                           <!-- 행 -->
      <th>제목1</th>                <!-- 제목 셀 -->
      <th>제목2</th>
    </tr>
  </thead>
  <tbody>                          <!-- 본문 구역 -->
    <tr>
      <td colspan="2">데이터1</td>   <!-- 가로 2칸 병합 -->
      <td rowspan="2">데이터2</td>   <!-- 세로 2칸 병합 -->
    </tr>
  </tbody>
  <tfoot></tfoot>                  <!-- 하단 구역 -->
</table>
```

| 태그 | 역할 |
| --- | --- |
| `<table>` | 표 전체 |
| `<thead>` | 제목 구역 — 가독성·SEO |
| `<tbody>` | 본문 구역 |
| `<tfoot>` | 하단 구역 (합계 등) |
| `<tr>` | 행 (table row) |
| `<th>` | 제목 셀 (굵게 + 가운데 정렬) |
| `<td>` | 데이터 셀 (table data) |

`colspan`/`rowspan`으로 셀을 병합합니다. 주석에 정확히 적어두셨습니다.

이 테이블 구조가 JS day14 게시판 CRUD 의 목록 화면에 그대로 쓰입니다.

## 2. 추가로 알면 좋은 활용법

### 2-1. `<label>`로 접근성 + 클릭 영역 확보

```html
<input type="checkbox" id="agree" />
<label for="agree">약관에 동의합니다</label>
```

`for`와 `id`를 연결하면 **글자를 클릭해도 체크박스가 토글**됩니다. 모바일에서 체감이 큽니다.

감싸는 방식도 가능합니다.
```html
<label>
  <input type="checkbox" /> 약관에 동의합니다
</label>
```

### 2-2. `radio`는 `name`이 같아야 그룹이 됩니다

```html
<input type="radio" name="gender" value="M" /> 남
<input type="radio" name="gender" value="F" /> 여
```

`name`이 다르면 각각 독립적으로 선택돼서 라디오의 의미가 사라집니다. **초보자가 가장 많이 하는 실수**입니다.

체크박스는 반대로 `name`을 같게 두면 배열로 전송됩니다.

### 2-3. `type="submit"` vs `type="button"`

```html
<form>
  <button>클릭</button>               <!-- form 안에서 기본값이 submit! -->
  <button type="button">클릭</button>  <!-- JS 연동용은 반드시 명시 -->
</form>
```

**"버튼을 눌렀는데 입력값이 사라진다"는 증상의 90%가 이것입니다.** 폼이 전송되며 페이지가 새로고침됩니다.

JS에서 막는 방법
```javascript
form.addEventListener("submit", (e) => {
  e.preventDefault();
});
```
→ JS day12 제품 사원 관리 CRUD

### 2-4. 브라우저 기본 검증

```html
<input type="email" required />
<input type="number" min="0" max="100" step="1" />
<input type="text" required minlength="2" maxlength="20" />
<input type="tel" pattern="010-\d{4}-\d{4}" />
<input type="date" />
<input type="search" />
<input type="color" />
<input type="range" min="0" max="100" />
```

`required`, `min`, `max`, `pattern`, `maxlength`는 **JS 없이도 브라우저가 검증**해줍니다. JS day14 게시판 CRUD 의 글쓰기 폼에 `required`만 넣어도 빈 글 등록을 막을 수 있습니다.

단, **클라이언트 검증은 우회 가능**하므로 서버 검증이 반드시 필요합니다.

### 2-5. `autocomplete`와 `inputmode`

```html
<input type="text" name="username" autocomplete="username" />
<input type="password" autocomplete="current-password" />
<input type="tel" inputmode="numeric" />   <!-- 모바일에서 숫자 키패드 -->
```

`autocomplete`를 제대로 쓰면 브라우저·비밀번호 관리자가 자동 채우기를 정확히 해줍니다.

### 2-6. `<table>`을 레이아웃에 쓰지 않기

옛날에는 화면 배치를 `<table>`로 했지만, 지금은 **표 형태의 데이터에만** 씁니다. 레이아웃은 flex와 grid로 합니다. → CSS day08 flexbox

접근성을 위해 `<caption>`과 `scope`를 추가하면 좋습니다.
```html
<table>
  <caption>2026년 월별 매출</caption>
  <thead>
    <tr><th scope="col">월</th><th scope="col">매출</th></tr>
  </thead>
</table>
```

## 3. 더 나아가 알면 좋은 것

### 3-1. 폼 전송 방식

```html
<form action="/api/boards" method="POST">
  <input name="title" />
  <button type="submit">등록</button>
</form>
```

| | GET | POST |
| --- | --- | --- |
| 데이터 위치 | URL 쿼리스트링 | 요청 본문(body) |
| 길이 제한 | 있음 | 사실상 없음 |
| 용도 | 검색, 조회 | 등록, 수정, 로그인 |
| 노출 | URL에 보임 | 안 보임 |

**GET 폼이 만드는 URL이 정확히 쿼리스트링입니다.** → JS day13 웹 스토리지와 인터벌

```
form action="/search" method="GET" + input name="q"
→ /search?q=검색어
```

파일 업로드는 `enctype`이 필요합니다.
```html
<form method="POST" enctype="multipart/form-data">
  <input type="file" name="upload" />
</form>
```

### 3-2. FormData

```javascript
const form = document.querySelector("#myForm");
const data = new FormData(form);
data.get("title");
Object.fromEntries(data);   // { title: "...", content: "..." }
```

`querySelector`로 하나씩 꺼내는 대신 폼 전체를 한 번에 객체로 만들 수 있습니다. JS day14 게시판 CRUD 의 `write.js`를 간결하게 만들 수 있습니다.

### 3-3. 테이블을 JS로 그리기

```javascript
tbody.innerHTML = list
  .map(b => `<tr><td>${b.no}</td><td><a href="view.html?no=${b.no}">${b.title}</a></td></tr>`)
  .join("");
```

day04에서 배운 `<tbody>`가 JS day11 DOM 조작 의 대상이 됩니다. `<tbody>`에 `id`를 주고 그 안만 갈아끼우는 게 표준 패턴입니다.

### 3-4. 테이블 스타일링

```css
table { border-collapse: collapse; }        /* 이중 테두리 병합 */
tbody tr:nth-of-type(even) { background: #eee; }   /* 줄무늬 */
tbody tr:hover { background: gray; }
```

CSS day15 테이블과 배경 에서 본격적으로 다룹니다.

## 실습 파일

- `2026_FE/day04/exam/exam.txt`
- `2026_FE/day04/exam/exam1.html`, `exam2.html`
- `2026_FE/day04/practice/pracitce1.html`, `practice3.html`, `tictackto.html`

## 관련 노트

[[HTML MOC]] · HTML day02 문서 구조와 미디어 · HTML day15 테이블 마크업 · JS day04 조건문 · JS day11 DOM 조작 · CSS day15 테이블과 배경
