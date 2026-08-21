---
출처: Claude 분석
작성일: 2026-08-21
tags: [코드정리]
---

# JS 날짜와 시간

> 상위: [[JS 스토리지와 타이머]]

전부 ※. 작성일 표시·정렬·경과 시간이 필요한 순간의 도구다.

## Date 만들기와 읽기

```javascript
const now = new Date();
const d = new Date("2026-08-21");
const t = new Date(2026, 7, 21, 14, 30);

now.getFullYear();
now.getMonth();
now.getDate();
now.getDay();
now.getHours();
```

- `new Date()`가 현재다. 문자열·숫자 인수로 특정 시점도 만든다
- **함정 둘**: `getMonth()`는 0부터라 8월이 7이다(+1 해서 표시). `getDay()`는 요일(일=0)이고 날짜는 `getDate()`다
- 자바처럼 LocalDate/LocalDateTime 구분이 없고 Date 하나가 날짜+시각을 다 든다

## 저장과 정렬 — ISO 문자열과 타임스탬프

```javascript
const createdAt = new Date().toISOString();

list.sort((a, b) => new Date(b.createdAt) - new Date(a.createdAt));

Date.now();
```

- 저장은 `toISOString()`("2026-08-21T05:30:00.000Z")이 표준이다 — 문자열인데 **사전순 = 시간순**이라 JSON·localStorage에 넣고 정렬해도 맞는다
- Date끼리 빼면 밀리초 차이가 나온다. 최신순 정렬이 `new Date(b) - new Date(a)` 한 줄
- `Date.now()`는 현재의 밀리초 숫자다. 소요 시간 측정·간단한 고유값에 쓴다

## 표시 형식

```javascript
now.toLocaleDateString("ko-KR");
now.toLocaleString("ko-KR");
now.toLocaleTimeString("ko-KR", { hour: "2-digit", minute: "2-digit" });

const pad = n => String(n).padStart(2, "0");
const ymd = `${now.getFullYear()}-${pad(now.getMonth() + 1)}-${pad(now.getDate())}`;
```

- `toLocaleDateString("ko-KR")`이 "2026. 8. 21." 형식을 공짜로 준다. 옵션 객체로 자릿수도 조절된다
- 원하는 모양을 정확히 만들려면 get 계열 + padStart 조합으로 직접 조립한다(자바 DateTimeFormatter 자리)

## 경과 시간 계산

```javascript
const diffMs = new Date() - new Date(post.createdAt);
const diffDay = Math.floor(diffMs / (1000 * 60 * 60 * 24));

const dayLeft = Math.ceil((new Date(due) - new Date()) / 86400000);
```

- 밀리초 차이를 일 단위로 나누는 게 기본형이다(86400000 = 하루 밀리초)
- "3일 전"·"D-5" 표시가 전부 이 나눗셈 + floor/ceil이다. 연체일 계산도 같은 식이다
