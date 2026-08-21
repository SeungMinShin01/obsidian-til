---
출처: Claude 분석
작성일: 2026-08-21
tags: [코드정리]
---

# HTML 이미지 최적화

> 상위: [[HTML 텍스트와 미디어]]

전부 ※. 페이지 용량의 대부분은 이미지다 — 태그 몇 줄로 크게 줄인다.

## 지연 로딩과 크기 명시

```html
<img src="cover.jpg" alt="표지" loading="lazy" width="300" height="400">
```

- `loading="lazy"`는 화면에 가까워질 때까지 다운로드를 미룬다. 긴 목록의 썸네일에 붙이는 것만으로 초기 로딩이 확 가벼워진다(첫 화면 이미지에는 붙이지 않는다)
- width·height를 명시하면 브라우저가 자리를 미리 잡아 **로딩 중 레이아웃이 덜컥 밀리는 것**(CLS)을 막는다. CSS로 크기를 바꾸더라도 원본 비율 계산용으로 쓰인다

## srcset — 화면에 맞는 크기 내려주기

```html
<img src="photo-800.jpg"
     srcset="photo-400.jpg 400w, photo-800.jpg 800w, photo-1600.jpg 1600w"
     sizes="(max-width: 600px) 100vw, 50vw"
     alt="사진">
```

- 같은 이미지를 여러 크기로 준비해 두면 브라우저가 기기 폭·해상도에 맞는 것만 받는다 — 폰에 1600px짜리를 내려보내지 않게 된다
- sizes는 "이 이미지가 화면에서 차지할 폭"의 힌트다. srcset의 `400w` 표기는 파일의 실제 픽셀 폭이다

## picture — 포맷·조건 분기

```html
<picture>
    <source srcset="hero.webp" type="image/webp">
    <img src="hero.jpg" alt="메인 배너">
</picture>
```

- webp·avif는 jpg보다 훨씬 작다. source로 신형 포맷을 먼저 제시하고, 못 읽는 브라우저는 img로 떨어진다(안전한 점진 적용)
- media 속성을 쓰면 "모바일에선 세로 크롭 이미지"처럼 조건별로 다른 그림도 내려보낼 수 있다

## 실무 체크리스트

- 원본 4000px짜리를 300px 칸에 넣지 않는다 — 업로드 전에 리사이즈가 최우선이다
- 사진은 jpg/webp, 아이콘·로고는 svg, 투명 배경 필요하면 png/webp로 포맷을 고른다
- 장식 이미지는 CSS background로 보내고, 내용 이미지는 img + alt로 남긴다는 구분은 여기서도 그대로다
