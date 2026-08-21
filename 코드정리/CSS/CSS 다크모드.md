---
출처: Claude 분석
작성일: 2026-08-21
tags: [코드정리]
---

# CSS 다크모드

> 상위: [[CSS 패턴]]

전부 ※. 색을 변수로 몰아 두었을 때 공짜로 따라오는 기능이다.

## 구조 — 변수 재정의가 전부다

```css
:root {
    --bg: #ffffff;
    --text: #1f2937;
    --card: #f9fafb;
    --border: #e5e7eb;
}

@media (prefers-color-scheme: dark) {
    :root {
        --bg: #111827;
        --text: #e5e7eb;
        --card: #1f2937;
        --border: #374151;
    }
}

body { background: var(--bg); color: var(--text); }
.card { background: var(--card); border: 1px solid var(--border); }
```

- 요소들은 var()만 바라보게 하고, 다크에서는 **변수 값만** 바꾼다 — 규칙을 두 벌 쓰는 게 아니라 팔레트만 교체하는 구조다
- `prefers-color-scheme: dark`는 OS·브라우저의 다크 설정을 자동으로 따라간다
- 색을 변수 없이 여기저기 하드코딩했다면 다크모드는 사실상 재작업이 된다 — 변수화가 선행 조건

## 수동 토글 — 클래스로 덮어쓰기

```css
:root { --bg: #fff; --text: #1f2937; }
html.dark { --bg: #111827; --text: #e5e7eb; }
```

```javascript
const saved = localStorage.getItem("theme");
if (saved === "dark") document.documentElement.classList.add("dark");

toggleBtn.addEventListener("click", () => {
    const dark = document.documentElement.classList.toggle("dark");
    localStorage.setItem("theme", dark ? "dark" : "light");
});
```

- html에 `.dark` 클래스를 얹으면 :root 변수가 덮인다. 토글 + localStorage 저장 + 시작 시 복원까지가 한 세트다
- OS 자동 + 수동 토글을 같이 하려면 "저장값이 있으면 그걸, 없으면 OS 설정"의 우선순위로 짠다

## 다크에서 흔히 틀리는 것

```css
.card { box-shadow: 0 1px 3px rgba(0, 0, 0, 0.4); }
img.logo { filter: brightness(0.9); }
:root { color-scheme: light dark; }
```

- 순수 검정(#000) 배경보다 짙은 회색(#111~#1f)이 눈에 덜 피로하고 그림자도 살아남는다
- 그림자는 다크에서 잘 안 보여 투명도를 높이거나 테두리로 대체한다. 쨍한 원색 텍스트는 다크에서 채도를 한 단계 낮춘다
- `color-scheme: light dark`를 선언하면 스크롤바·폼 기본 위젯까지 브라우저가 테마에 맞춰 준다
