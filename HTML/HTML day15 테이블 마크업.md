---
출처: Claude 분석
원본: KDT_2026/2026_FE/day15/exam
작성일: 2026-08-10
tags: [html, day15, 테이블, 시맨틱]
---

# HTML day15 — 테이블 마크업

> 실습 파일: `day15/exam/exam1.html`(테이블 구조), `exam2~4.html`
> 허브: [[HTML MOC]] · 이전: [[HTML day04 폼과 테이블]]

## 1. 배운 내용

### 1-1. 테이블 구조 재확인

`day15/exam/exam1.html`의 주석이 각 태그의 목적을 정확히 짚습니다.

```html
<table>                       <!-- 전체 표 감싼 -->
  <thead>                     <!-- 테이블 제목 구역 : 헤더, 목적 → 가독성, SEO -->
    <tr>                      <!-- 테이블 행 -->
      <th>제목</th>            <!-- 테이블 헤더/제목 -->
    </tr>
  </thead>
  <tbody>                     <!-- 테이블 내용 구역 : 본문 -->
    <tr>
      <td>데이터</td>          <!-- 테이블 데이터/셀/한칸 -->
    </tr>
  </tbody>
  <tfoot>                     <!-- 테이블 하단 구역 : 푸터 -->
  </tfoot>
</table>
```

day04에서 형태를 배웠다면, day15에서는 **CSS로 꾸미기 위한 구조**로 다시 봅니다. `<thead>`, `<tbody>`가 분리되어 있어야 CSS 선택자로 본문만 골라 줄무늬를 넣을 수 있습니다.

```css
.styleTable > tbody > tr:nth-of-type(even) { background-color: #eeeeee; }
```
→ [[CSS day15 테이블과 배경]]

### 1-2. day15의 나머지 HTML

| 파일 | 대응 CSS | 내용 |
| --- | --- | --- |
| `exam1.html` | `exam1.css` | 테이블 구조 + nth-child |
| `exam2.html` | `exam2.css` | (테이블 스타일 심화) |
| `exam3.html` | `exam3.css` | `<img>` + `object-fit` 5종 |
| `exam4.html` | `exam4.css` | `background` 속성군, 스프라이트 |

`exam3.html`은 같은 이미지를 `.imgBox` 6개에 넣고 `object-fit` 값만 바꿔 비교하는 구조입니다. **속성 하나씩 격리해서 확인하는 방식**은 [[CSS day08 flexbox]] 의 `.flexbox1~10`과 같은 좋은 학습법입니다.

## 2. 추가로 알면 좋은 활용법

### 2-1. `<caption>`과 `scope`

```html
<table>
  <caption>2026년 월별 매출</caption>
  <thead>
    <tr>
      <th scope="col">월</th>
      <th scope="col">매출</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th scope="row">1월</th>
      <td>1,000만원</td>
    </tr>
  </tbody>
</table>
```

- `<caption>` — 표의 제목. `<table>` 바로 안, 첫 번째 자식이어야 합니다
- `scope="col"` / `scope="row"` — 이 헤더가 열의 제목인지 행의 제목인지 명시

스크린 리더가 "1월 행의 매출은 1,000만원"처럼 읽어줍니다. 시각적으로는 차이가 없지만 접근성 점수가 크게 올라갑니다.

### 2-2. `<colgroup>`으로 열 단위 스타일

```html
<table>
  <colgroup>
    <col style="width: 80px" />
    <col style="width: auto" />
    <col style="width: 120px" />
  </colgroup>
  ...
</table>
```

각 `<tr>`마다 첫 번째 `<td>`에 너비를 주는 대신 열 단위로 한 번에 지정합니다. 게시판 목록(번호·제목·작성일)처럼 열 너비가 고정된 표에 유용합니다.

### 2-3. `border` 속성 대신 CSS

```html
<table border="1">      <!-- HTML 속성 — 구식 -->
```
```css
table, th, td { border: 1px solid #000; }
table { border-collapse: collapse; }
```

HTML은 구조, CSS는 표현 — 역할 분리 원칙입니다. `border-collapse: collapse`가 이중 테두리를 하나로 합쳐줍니다.

### 2-4. 반응형 테이블

테이블은 모바일에서 가장 깨지기 쉬운 요소입니다.

```css
/* 방법 1: 가로 스크롤 */
.table-wrap { overflow-x: auto; }
```
```html
<div class="table-wrap"><table>...</table></div>
```

```css
/* 방법 2: 모바일에서 카드 형태로 전환 */
@media (max-width: 600px) {
  table, thead, tbody, tr, th, td { display: block; }
  thead { display: none; }
  td::before { content: attr(data-label); font-weight: bold; }
}
```
```html
<td data-label="제목">첫 번째 글</td>
```

`content: attr(data-label)`은 [[CSS day14 position과 가상요소]] 의 가상요소 활용입니다.

## 3. 더 나아가 알면 좋은 것

### 3-1. 테이블을 언제 쓰고 언제 안 쓰는가

| 상황 | 사용 |
| --- | --- |
| 행과 열에 각각 의미가 있는 데이터 | `<table>` O |
| 게시판 목록, 성적표, 비교표 | `<table>` O |
| 화면 레이아웃 (사이드바 + 본문) | `<table>` X → flex/grid |
| 카드 나열 | `<table>` X → flex/grid |

레이아웃은 [[CSS day08 flexbox]] 와 grid로 합니다.

### 3-2. 정렬 가능한 테이블

```javascript
document.querySelectorAll("th[data-sort]").forEach(th => {
  th.addEventListener("click", () => {
    const key = th.dataset.sort;
    list.sort((a, b) => a[key] > b[key] ? 1 : -1);
    render();
  });
});
```

[[JS day11 DOM 조작]] 의 이벤트 위임 + [[JS day14 게시판 CRUD]] 의 정렬을 합친 형태입니다.

### 3-3. 큰 테이블의 성능

행이 수천 개가 되면 DOM 노드가 그만큼 생겨 느려집니다.

- **페이지네이션** — `slice`로 한 페이지씩
- **가상 스크롤** — 화면에 보이는 행만 렌더링
- **`<thead>` 고정** — `position: sticky`

```css
thead th { position: sticky; top: 0; background: #fff; z-index: 1; }
```
→ [[CSS day14 position과 가상요소]]

## 실습 파일

- `2026_FE/day15/exam/exam1.html`, `exam2.html`, `exam3.html`, `exam4.html`
- `2026_FE/day15/test.html`
- `2026_FE/day15/project/test.css`

## 관련 노트

[[HTML MOC]] · [[HTML day04 폼과 테이블]] · [[CSS day15 테이블과 배경]] · [[JS day14 게시판 CRUD]]
