---
출처: Claude 분석
작성일: 2026-08-21
tags: [코드정리]
---

# CSS

> 상위: [[코드정리]]
> 세부: [[CSS 선택자]] · [[CSS 박스 모델과 단위]] · [[CSS 텍스트와 배경]] · [[CSS flexbox]] · [[CSS position과 가상요소]] · [[CSS 패턴]] · [[CSS AI 관용구]]

코드정리 CSS 트리의 루트. 아래는 **수업(day05~15)에서 배운 코드 전체**를 한 줄 주석으로 모은 것이다. 원리·심화는 세부 노트로.

## day05 — 적용 방법 3가지

```html
<p style="color: red;">인라인</p>                 <!-- 태그에 직접 (우선순위 최상, 지양) -->
<style> p { color: red; } </style>               <!-- 내부: head의 style 태그 -->
<link rel="stylesheet" href="style.css">         <!-- 외부 파일 연결 (표준) -->
```

```css
선택자 { 속성: 값; }                               /* CSS 기본 문법 */
/* 주석 */
```

## day06 — 선택자

```css
p { }                                            /* 태그 선택자 */
.card { }                                        /* 클래스 (여러 요소 재사용) */
#header { }                                      /* 아이디 (페이지에 하나) */
* { }                                            /* 전체 */
h1, h2, p { }                                    /* 그룹 (쉼표) */
nav a { }                                        /* 자손 (공백: 몇 단계든) */
ul > li { }                                      /* 직계 자식만 */
a:hover { }                                      /* 마우스 올렸을 때 */
input:focus { }                                  /* 입력 커서 있을 때 */
li:first-child { }                               /* 첫 번째 자식 */
tr:nth-child(even) { }                           /* 짝수 번째 (줄무늬) */
```

## day06 — 텍스트 속성

```css
color: #333;                                     /* 글자색 (16진수) */
color: rgb(26, 115, 232);                        /* rgb */
color: rgba(0, 0, 0, 0.5);                       /* 투명도 포함 */
font-family: "Malgun Gothic", sans-serif;        /* 글꼴 후보 목록 */
font-size: 16px;                                 /* 크기 */
font-weight: 700;                                /* 굵기 (400 보통, 700 굵게) */
font-style: italic;                              /* 기울임 */
text-align: center;                              /* 정렬 (left/center/right) */
text-decoration: none;                           /* 밑줄 제거 (a 기본값 끄기) */
line-height: 1.6;                                /* 줄 간격 (단위 없는 배수) */
letter-spacing: 1px;                             /* 자간 */
```

## day06 — 박스 모델

```css
width: 300px;  height: 200px;                    /* 크기 */
padding: 16px;                                   /* 안쪽 여백 (배경색 칠해짐) */
margin: 20px;                                    /* 바깥 여백 (이웃과 거리) */
margin: 10px 20px;                               /* 상하 / 좌우 */
margin: 10px 20px 30px 40px;                     /* 상 우 하 좌 (시계방향) */
margin: 0 auto;                                  /* 블록 가로 중앙 (width 필요) */
border: 1px solid #ddd;                          /* 테두리: 두께 스타일 색 */
border-radius: 8px;                              /* 둥근 모서리 */
box-sizing: border-box;                          /* padding·border를 width에 포함 */
display: block;                                  /* 한 줄 통째로 (div p h1) */
display: inline;                                 /* 글자처럼 흐름 (span a) */
display: inline-block;                           /* 흐르면서 크기 지정 가능 */
display: none;                                   /* 화면에서 제거 (자리도 없음) */
overflow: hidden;                                /* 넘치는 내용 자르기 */
cursor: pointer;                                 /* 마우스 손가락 모양 */
box-shadow: 0 1px 4px rgba(0,0,0,.1);            /* 그림자: x y 번짐 색 */
```

## day08 — flexbox

```css
display: flex;                                   /* 부모에 켬 → 자식 가로 배치 */
flex-direction: row;                             /* 가로 (기본) */
flex-direction: column;                          /* 세로 */
justify-content: center;                         /* 주축 정렬: 가운데 */
justify-content: space-between;                  /* 양끝 붙이고 사이 균등 */
align-items: center;                             /* 교차축 정렬: 가운데 */
gap: 16px;                                       /* 자식 사이 간격 */
flex-wrap: wrap;                                 /* 넘치면 다음 줄로 */
flex: 1;                                         /* (자식에) 남는 공간 차지 */
```

## day09~11 — 실습에서 굳은 조합

```css
.center { display: flex; justify-content: center; align-items: center; }  /* 완전 중앙 */
.navbar { display: flex; justify-content: space-between; align-items: center; }  /* 로고-메뉴 */
.wrapper { max-width: 1200px; margin: 0 auto; }  /* 본문 폭 제한 + 중앙 */
.card { border: 1px solid #eee; border-radius: 8px; padding: 16px; }  /* 카드 */
```

## day14 — position·가상요소

```css
position: static;                                /* 기본 (흐름대로) */
position: relative;                              /* 원래 자리 기준 이동 (기준점 역할) */
position: absolute;                              /* 조상(relative) 기준 배치 */
position: fixed;                                 /* 화면 기준 고정 (상단 헤더) */
position: sticky; top: 0;                        /* 스크롤하다 걸리면 고정 */
top: -8px; right: -8px;                          /* 이동값 (배지 위치) */
z-index: 10;                                     /* 겹침 순서 (position 있어야 동작) */
.parent { position: relative; }                  /* absolute의 기준 만들기 */
.child { position: absolute; top: 0; right: 0; } /* 부모 기준 우상단 */

.title::before { content: "★"; }                 /* 요소 앞에 가짜 자식 */
.title::after { content: ""; display: block; }   /* 요소 뒤 (content 필수) */
.required::before { content: "* "; color: red; } /* 필수 표시 */
```

## day15 — 테이블·배경

```css
table { border-collapse: collapse; }             /* 테두리 겹침 제거 (표 필수) */
th, td { border: 1px solid #ddd; padding: 8px; } /* 칸 테두리·여백 */
tbody tr:hover { background: #eef4ff; }          /* 행 호버 */

background-color: #f0f4f8;                       /* 배경색 */
background-image: url("hero.jpg");               /* 배경 이미지 */
background-size: cover;                          /* 빈틈없이 채움 (일부 잘림) */
background-size: contain;                        /* 전체 보이게 (여백 생김) */
background-position: center;                     /* 위치 */
background-repeat: no-repeat;                    /* 반복 끄기 */
background: url("hero.jpg") center / cover no-repeat;  /* 축약형 한 줄 */
```

## 자주 쓰는 코드 ※ (수업 밖 — 위와 중복 없음)

```css
* { margin: 0; padding: 0; box-sizing: border-box; }   /* 시작 리셋 3종 세트 */
:root { --primary: #2563eb; --gap: 16px; }             /* 변수 선언 (한 곳에서 관리) */
.btn { background: var(--primary); }                    /* 변수 사용 */

.cards { display: grid; grid-template-columns: repeat(auto-fill, minmax(220px, 1fr)); gap: 16px; }  /* 반응형 카드 그리드 */
.ellipsis { overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }  /* 한 줄 말줄임 */
img { max-width: 100%; height: auto; }                  /* 이미지 안 넘치게 (반응형 기본) */
.thumb { aspect-ratio: 16/9; object-fit: cover; }       /* 비율 고정 썸네일 */
.overlay { position: absolute; inset: 0; background: rgba(0,0,0,.5); }  /* 부모 꽉 덮기 */
.list { max-height: 300px; overflow-y: auto; }          /* 넘치면 스크롤 */

.btn { transition: background .2s, transform .2s; }     /* 전환 (평소 상태에 걸기) */
.btn:hover { transform: translateY(-2px); }             /* 호버 시 살짝 떠오르기 */
.arrow.open { transform: rotate(180deg); }              /* 회전 (아코디언 화살표) */
h1 { font-size: clamp(1.4rem, 3vw, 2.2rem); }           /* 반응형 글자 크기 (최소~최대) */
.container { width: min(90%, 1200px); }                 /* 둘 중 작은 쪽 */

@media (max-width: 768px) {                             /* 모바일 분기 */
    .sidebar { display: none; }                         /* 좁으면 숨기기 */
    .grid-3 { grid-template-columns: 1fr; }             /* 다열 → 1열 */
}
input:invalid { border-color: red; }                    /* 검증 실패 시각화 */
li:not(.active) { opacity: .6; }                        /* 이것만 빼고 전부 */
```
