---
출처: Claude 분석
작성일: 2026-08-21
tags: [코드정리]
---

# HTML 폼 요소 심화

> 상위: [[HTML 폼]]

전부 ※. text·select 말고도 폼에는 쓸만한 부품이 많다.

## fieldset — 입력 묶기

```html
<fieldset>
    <legend>대여 정보</legend>
    <label for="member">회원</label><input id="member">
    <label for="book">도서</label><input id="book">
</fieldset>
```

- 관련 입력을 테두리로 묶고 legend가 그룹 제목이 된다. 라디오 그룹의 질문 문구를 legend로 두는 게 정석이다
- fieldset에 `disabled`를 주면 **안의 입력 전부**가 한 번에 비활성화된다 — 제출 중 잠그기에 유용

## datalist — 자동완성 입력

```html
<input list="authors" id="author">
<datalist id="authors">
    <option value="김영하">
    <option value="한강">
</datalist>
```

- select와 달리 **목록에서 고르거나 직접 입력하거나** 둘 다 된다. "자주 쓰는 값 + 자유 입력" 폼의 답이다
- input의 list 속성과 datalist의 id를 맞추는 것이 배선의 전부다

## range · color · hidden

```html
<input type="range" min="0" max="10" step="1" value="5" id="rating">
<output for="rating">5</output>
<input type="color" value="#1a73e8">
<input type="hidden" name="postNo" value="3">
```

- range는 슬라이더다. 값 표시는 안 해주므로 output + JS(input 이벤트)로 짝을 맞춘다
- hidden은 화면엔 없지만 제출에는 실리는 값이다 — 수정 폼이 "몇 번 글인지"를 나르는 전통적 통로(JS 방식에선 dataset이 이 역할)

## select 심화

```html
<select multiple size="4">
    <optgroup label="프론트엔드">
        <option value="html">HTML</option>
        <option value="css">CSS</option>
    </optgroup>
    <optgroup label="백엔드">
        <option value="java">Java</option>
    </optgroup>
</select>
```

- optgroup이 옵션에 소제목을 붙인다. multiple은 Ctrl 클릭 다중 선택인데 UX가 나빠 체크박스 목록으로 대체하는 경우가 많다

## 제출 버튼의 세 얼굴

```html
<button type="submit">저장</button>
<button type="reset">초기화</button>
<button type="button" onclick="preview()">미리보기</button>
```

- submit 제출, reset 폼 비우기, button 아무것도 안 함(JS 전용) — 폼 안에서는 type 생략이 submit이라는 걸 다시 기억한다
- reset은 사용자가 쓰던 걸 날릴 수 있어 실무에선 잘 안 둔다
