---
출처: Claude 분석
작성일: 2026-08-21
tags: [코드정리]
---

# HTML 테이블

> 상위: [[HTML]]

## 기본 구조

```html
<table>
    <caption>도서 목록</caption>
    <thead>
        <tr>
            <th>번호</th>
            <th>제목</th>
        </tr>
    </thead>
    <tbody id="tableTbody">
        <tr>
            <td>1</td>
            <td><a href="view.html?no=1">첫 글</a></td>
        </tr>
    </tbody>
    <tfoot>
        <tr>
            <td colspan="2">총 1건</td>
        </tr>
    </tfoot>
</table>
```

- tr이 행, th가 머리칸(굵게·가운데 기본), td가 데이터칸이다
- thead/tbody/tfoot으로 구역을 나누면 JS가 **tbody만 골라** 목록을 다시 그릴 수 있다 — 게시판 목록 렌더링이 `tbody.innerHTML = ...`인 이유
- caption은 표 제목이다. 표가 무엇인지 스크린리더에도 전달된다

## 칸 병합

```html
<td colspan="2">가로로 두 칸</td>
<td rowspan="3">세로로 세 칸</td>
```

- colspan 가로 병합, rowspan 세로 병합이다. 병합한 만큼 그 행·열의 다른 td를 **빼야** 표가 안 깨진다
- 시간표·견적서처럼 불규칙한 표에서 쓴다. 병합이 많아지면 종이에 먼저 그려보는 게 빠르다

## 표 스타일 기본기

```html
<style>
table { border-collapse: collapse; width: 100%; }
th, td { border: 1px solid #ddd; padding: 8px; }
tbody tr:nth-child(even) { background: #f9f9f9; }
tbody tr:hover { background: #eef4ff; }
</style>
```

- `border-collapse: collapse`가 없으면 칸마다 테두리가 두 겹으로 보인다 — 표 CSS의 첫 줄 고정값
- 줄무늬(nth-child)·행 hover는 목록 가독성의 표준 조합이다

## 표 vs 레이아웃

- 표는 **행과 열이 의미 있는 데이터**(목록·통계)에만 쓴다. 화면 배치는 flexbox·grid의 몫이다
