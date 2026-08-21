---
출처: Claude 분석
작성일: 2026-08-21
tags: [코드정리]
---

# CSS transform과 애니메이션

> 상위: [[CSS position과 가상요소]]

전부 ※. 움직임 3층: transform(이동·변형) → transition(변화를 부드럽게) → @keyframes(스스로 움직임).

## transform

```css
.card:hover { transform: translateY(-4px); }
.modal { transform: translate(-50%, -50%); }
.arrow.open { transform: rotate(180deg); }
.thumb:hover { transform: scale(1.05); }
```

- translate 이동, rotate 회전, scale 확대·축소. 쉼표 없이 나란히 쓰면 조합된다(`translateY(-2px) scale(1.02)`)
- transform은 **레이아웃을 다시 계산하지 않아** margin·top으로 움직이는 것보다 부드럽다 — 움직임은 무조건 transform이 정석
- 절대 중앙 정렬 관용구: `position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%)` — 자기 크기의 절반만큼 되돌아와 정확히 중앙에 선다

## transition

```css
.button {
    transition: transform 0.2s ease, background 0.2s;
}
.panel {
    max-height: 0;
    overflow: hidden;
    transition: max-height 0.3s ease;
}
.panel.open { max-height: 500px; }
```

- `transition: 속성 시간 가속곡선` — 상태(hover·클래스 토글)가 바뀔 때 그 사이를 채워 준다. **평소 상태에 걸어야** 갈 때·올 때 모두 부드럽다
- 아코디언 열닫이는 height가 auto라 transition이 안 걸리므로 max-height 트릭을 쓴다(충분히 큰 값으로)
- 가속곡선: ease(기본) / ease-out(끝에서 감속 — UI에 무난) / linear(일정 속도)

## @keyframes — 스스로 움직이는 애니메이션

```css
@keyframes fadeInUp {
    from { opacity: 0; transform: translateY(10px); }
    to   { opacity: 1; transform: translateY(0); }
}

.toast { animation: fadeInUp 0.3s ease-out; }

@keyframes spin { to { transform: rotate(360deg); } }
.loader { animation: spin 1s linear infinite; }
```

- transition은 상태 변화가 있어야 움직이지만 keyframes는 **등장하자마자** 혼자 돈다
- `animation: 이름 시간 곡선 반복` — infinite가 무한 반복(로딩 스피너의 정체가 border 원 + spin이다)
- 토스트 알림·모달 등장 효과가 fadeInUp 하나로 해결된다

## 성능과 배려

```css
.anim { will-change: transform; }

@media (prefers-reduced-motion: reduce) {
    * { animation: none !important; transition: none !important; }
}
```

- 부드러운 건 transform과 opacity 두 가지다 — width·height·top을 애니메이션하면 버벅인다
- prefers-reduced-motion 블록은 "동작 줄이기"를 켠 사용자에 대한 배려 관용구로, AI 생성 CSS에 종종 들어 있다
