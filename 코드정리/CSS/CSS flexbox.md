---
출처: Claude 분석
작성일: 2026-08-21
tags: [코드정리]
---

# CSS flexbox

> 상위: [[CSS]]
> 세부: [[CSS Grid]]

## 기본 — 컨테이너에 켠다

```css
.container {
    display: flex;
    flex-direction: row;
    justify-content: space-between;
    align-items: center;
    gap: 16px;
}
```

- 부모에 `display: flex`를 주면 **자식들이** 가로로 나란히 배치된다. 속성 대부분이 부모(컨테이너)에 붙는다는 게 핵심이다
- `flex-direction`: row 가로(기본) / column 세로. 방향에 따라 주축이 바뀐다
- `justify-content`: **주축** 정렬 — flex-start / center / space-between(양끝 붙이고 사이 균등) / space-around
- `align-items`: **교차축** 정렬 — center(세로 가운데) / stretch(기본, 높이 늘림)
- `gap`: 자식 사이 간격. margin으로 벌리던 것을 대체하는 요즘 표준이다

## 완전 중앙 정렬

```css
.center {
    display: flex;
    justify-content: center;
    align-items: center;
}
```

- 가로·세로 동시 중앙이 세 줄이다. 로그인 박스·모달·빈 상태 문구에 그대로 쓴다

## 줄바꿈과 아이템 크기

```css
.cards {
    display: flex;
    flex-wrap: wrap;
}

.sidebar { width: 240px; }
.main { flex: 1; }
```

- `flex-wrap: wrap`은 넘치면 다음 줄로 — 카드 그리드의 기초다
- 자식에 주는 `flex: 1`은 "남는 공간을 다 차지해라"다. 고정폭 사이드바 + 나머지 본문 레이아웃이 이 두 줄로 끝난다
- 여러 자식에 flex: 1을 주면 균등 분할이다(탭 버튼 3개 등)

## 자주 쓰는 조합

```css
.navbar {
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.form-row {
    display: flex;
    flex-direction: column;
    gap: 8px;
}
```

- 로고 왼쪽·메뉴 오른쪽 내비게이션 = space-between 한 방
- 라벨 위·입력 아래 폼 = column + gap. 카페 키오스크·예약 사이트 레이아웃이 전부 이 조합들의 반복이다
