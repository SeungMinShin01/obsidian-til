---
출처: Claude 분석
작성일: 2026-08-21
tags: [코드정리]
---

# CSS 우선순위

> 상위: [[CSS 선택자]]

전부 ※에 가깝다. "분명히 스타일을 줬는데 안 먹는다"의 원인 대부분이 여기 있다.

## 명시도(specificity) — 점수 싸움

```
인라인 style=""     1000점
#아이디              100점
.클래스 :가상클래스 [속성]   10점
태그 ::가상요소        1점
```

```css
p { color: gray; }
.notice { color: blue; }
#main .notice { color: red; }
```

- 같은 요소를 여러 규칙이 노리면 **점수 높은 쪽이 이긴다.** 위 예에서 `#main .notice`(110점) > `.notice`(10점) > `p`(1점)
- 점수가 같으면 **나중에 쓴 규칙**이 이긴다 — CSS 파일에서 아래쪽이 우선인 이유다
- 개발자도구에서 취소선 그어진 규칙이 "점수에서 진" 규칙이다. 왜 안 먹는지는 거기서 바로 보인다

## !important — 최후의 수단

```css
.hidden { display: none !important; }
```

- 점수를 무시하고 최우선이 된다. 하지만 이걸 이기려면 또 !important가 필요해져 연쇄가 시작된다
- 원칙: !important 대신 **선택자를 더 구체적으로** 써서 이긴다. 유틸리티(무조건 숨김)처럼 의도가 명확할 때만 예외

## 상속

```
상속됨:      color, font-*, line-height, text-align, list-style
상속 안 됨:  margin, padding, border, width, height, background
```

- 글자 관련 속성은 부모→자식으로 흘러내린다. body에 font-family를 주면 전체에 적용되는 이유다
- 박스 관련 속성은 상속되지 않는다 — 부모에 padding을 줘도 자식 padding은 0이다
- `inherit` 값으로 강제 상속받을 수 있다: `button { font: inherit; }`(버튼이 폰트를 무시하는 브라우저 기본값 교정)
