---
출처: Claude 분석
작성일: 2026-08-10
tags: [css, MOC, 허브]
---

# CSS MOC

CSS 관련 노트의 허브입니다. 상위 지도는 [[KDT_2026 학습 지도]].

## 학습 순서 (day별)

```
day05 첫 스타일링 ─→ day06 선택자·기본속성 ─→ day08 flexbox ─→ day09 카페 키오스크
                                                                      │
                                                                      ▼
day15 테이블·배경 ←─ day14 position·가상요소 ←─ day11 커뮤니티·예약 ←─ day10 강의 사이트
```

| day | 노트 | 핵심 |
| --- | --- | --- |
| 05 | [[CSS day05 첫 스타일링]] | 첫 CSS 파일 분리, 이미지 배치 |
| 06 | [[CSS day06 선택자와 기본 속성]] | 선택자 7종·우선순위, 텍스트·박스, display |
| 08 | [[CSS day08 flexbox]] | flex 10패턴 실험, 주축·교차축 |
| 09 | [[CSS day09 카페 키오스크]] | 웹폰트, fixed 헤더·푸터, 카드 그리드 |
| 10 | [[CSS day10 카메라 강의 사이트]] | container 패턴, 사이드바 2열 |
| 11 | [[CSS day11 커뮤니티와 예약 사이트]] | 리셋 CSS, 2단 헤더, 3열 본문 |
| 14 | [[CSS day14 position과 가상요소]] | position 5종, 가상요소, 쇼핑몰 드롭다운 |
| 15 | [[CSS day15 테이블과 배경]] | nth-child, object-fit, background, 스프라이트 |

## 함께 쓰는 언어

- [[HTML MOC]] — CSS가 꾸미는 대상
- [[JavaScript MOC]] — `classList`, `.style`로 CSS를 바꾸는 것

**CSS 선택자 문법을 JS가 그대로 씁니다.** `document.querySelector(".box")` → [[JS day11 DOM 조작]]

## 자주 쓰는 리셋

```css
*, *::before, *::after { box-sizing: border-box; }
* { margin: 0; padding: 0; }
ul, ol { list-style: none; }
a { text-decoration: none; color: inherit; }
img { display: block; max-width: 100%; }
```

`a { text-decoration: none; }` 도 이 리셋의 일부입니다.

## 핵심 요약표

| 하고 싶은 것 | 속성 |
| --- | --- |
| 가로 배치 | `display: flex` |
| 가운데 정렬 | `justify-content: center; align-items: center` |
| 요소 겹치기 | `position: absolute` (부모 `relative`) |
| 헤더 고정 | `position: sticky; top: 0` |
| 이미지 안 찌그러지게 | `object-fit: cover` |
| 표 테두리 하나로 | `border-collapse: collapse` |
| 크기 계산 편하게 | `box-sizing: border-box` |
