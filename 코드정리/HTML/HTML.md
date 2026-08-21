---
출처: Claude 분석
작성일: 2026-08-21
tags: [코드정리]
---

# HTML

> 상위: [[코드정리]]
> 세부: [[HTML 문서 구조]] · [[HTML 텍스트와 미디어]] · [[HTML 폼]] · [[HTML 테이블]] · [[HTML AI 관용구]]

코드정리 HTML 트리의 루트. 아래는 **수업(day02·04·15)에서 배운 코드 전체**를 한 줄 주석으로 모은 것이다. 원리·심화는 세부 노트로.

## day02 — 문서 구조

```html
<!DOCTYPE html>                                  <!-- HTML5 문서 선언 -->
<html lang="ko">                                 <!-- 문서 시작 (언어 표시) -->
<head>                                           <!-- 화면에 안 보이는 정보 -->
    <meta charset="UTF-8">                       <!-- 인코딩 (한글 깨짐 방지) -->
    <title>페이지 제목</title>                     <!-- 브라우저 탭 제목 -->
    <link rel="stylesheet" href="style.css">     <!-- CSS 연결 -->
</head>
<body>                                           <!-- 실제 내용 -->
    <script src="app.js"></script>               <!-- JS 연결 (body 끝: 요소 생성 후 실행) -->
</body>
</html>
<!-- 주석 -->
```

## day02 — 텍스트·링크·목록·미디어

```html
<h1>제목1</h1> <h2>제목2</h2>                      <!-- 제목 계층 (h1~h6, 크기 아닌 구조) -->
<p>문단</p>                                       <!-- 문단 -->
<br>                                             <!-- 줄바꿈 -->
<hr>                                             <!-- 가로 구분선 -->
<strong>중요</strong> <em>강조</em>                <!-- 굵게(의미) / 기울임(의미) -->

<a href="list.html">목록으로</a>                   <!-- 링크 (이동) -->
<a href="view.html?no=3">상세</a>                  <!-- 쿼리스트링으로 값 전달 -->
<a href="https://..." target="_blank">새 탭</a>    <!-- 새 탭 열기 -->

<ul><li>항목</li></ul>                             <!-- 순서 없는 목록 (점) -->
<ol><li>항목</li></ol>                             <!-- 순서 있는 목록 (번호) -->

<img src="cat.jpg" alt="고양이">                   <!-- 이미지 (alt = 대체 텍스트) -->
<video src="clip.mp4" controls></video>           <!-- 동영상 (controls = 재생 버튼) -->
<audio src="bgm.mp3" controls></audio>            <!-- 오디오 -->
&lt; &gt; &amp; &nbsp;                            <!-- 특수문자: < > & 공백 -->
```

## day04 — 폼

```html
<form>                                            <!-- 입력 묶음 -->
    <label for="title">제목</label>                <!-- 라벨 (for = input의 id) -->
    <input type="text" id="title" placeholder="힌트">   <!-- 한 줄 텍스트 -->
    <input type="password" id="pwd">              <!-- 비밀번호 (가려짐) -->
    <input type="number" min="1" max="99">        <!-- 숫자 전용 -->
    <input type="date">                           <!-- 달력 -->
    <input type="checkbox" id="agree">            <!-- 체크박스 (.checked로 읽기) -->
    <input type="radio" name="grade" value="A">   <!-- 라디오 (같은 name = 한 그룹) -->
    <input type="file">                           <!-- 파일 선택 -->
    <textarea rows="5"></textarea>                <!-- 여러 줄 입력 -->
    <select>                                      <!-- 드롭다운 -->
        <option value="">선택하세요</option>        <!-- 빈 값 = 미선택 검증용 -->
        <option value="java" selected>Java</option>  <!-- selected = 기본 선택 -->
    </select>
    <button type="submit">등록</button>            <!-- 제출 (폼 안 기본값) -->
    <button type="button">동작</button>            <!-- JS 전용 버튼 -->
</form>
<!-- input 값은 JS에서 .value로, 체크 여부는 .checked로 -->
```

## day04·15 — 테이블

```html
<table>                                           <!-- 표 시작 -->
    <caption>도서 목록</caption>                    <!-- 표 제목 -->
    <thead>                                       <!-- 머리 구역 -->
        <tr>                                      <!-- 행 -->
            <th>번호</th> <th>제목</th>             <!-- 머리칸 (굵게·가운데) -->
        </tr>
    </thead>
    <tbody id="tableTbody">                       <!-- 몸통 (JS가 채우는 자리) -->
        <tr>
            <td>1</td>                            <!-- 데이터칸 -->
            <td><a href="view.html?no=1">글</a></td>
        </tr>
    </tbody>
</table>
<td colspan="2">가로 병합</td>                      <!-- 두 칸 합치기 (그만큼 td 빼기) -->
<td rowspan="3">세로 병합</td>                      <!-- 세 행 합치기 -->
```

## 자주 쓰는 코드 ※ (수업 밖 — 위와 중복 없음)

```html
<meta name="viewport" content="width=device-width, initial-scale=1.0">  <!-- 모바일 필수 -->
<meta name="description" content="페이지 소개">           <!-- 검색 결과 요약문 -->
<link rel="icon" href="favicon.ico">                     <!-- 탭 아이콘 -->
<script src="app.js" defer></script>                     <!-- head에 둬도 파싱 후 실행 -->

<header></header> <nav></nav> <main></main>              <!-- 시맨틱 구역 (div 대신 의미) -->
<section></section> <article></article> <footer></footer>

<img src="cover.jpg" alt="표지" loading="lazy" width="300" height="400">  <!-- 지연 로딩 + 자리 확보 -->
<button type="button" data-no="3">삭제</button>           <!-- 요소에 데이터 싣기 (dataset) -->
<button aria-label="닫기">×</button>                      <!-- 글자 없는 버튼에 이름 -->

<input required maxlength="50">                          <!-- 빈 값 차단 + 글자 제한 -->
<input type="password" minlength="4" required>           <!-- 최소 길이 -->
<input pattern="[0-9]{3}-[0-9]{4}-[0-9]{4}">             <!-- 형식 검사 (정규식) -->
<input type="email" required>                            <!-- 이메일 형식 내장 검사 -->
<input readonly>  <input disabled>                       <!-- 수정만 금지 / 아예 비활성 -->

<fieldset><legend>대여 정보</legend></fieldset>            <!-- 입력 그룹 + 제목 -->
<input list="authors"><datalist id="authors">            <!-- 자동완성 입력 -->
    <option value="김영하"></datalist>
<input type="hidden" name="postNo" value="3">            <!-- 화면엔 없고 제출엔 실림 -->
<tfoot><tr><td colspan="2">총 1건</td></tr></tfoot>        <!-- 표 바닥 구역 -->
```
