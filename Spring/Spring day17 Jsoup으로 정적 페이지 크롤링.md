---
출처: Claude 분석
원본: KDT_2026/2026B_Spring/springweb/src/main/java/day17, springweb/build.gradle
작성일: 2026-10-19
tags: [학습, java]
---

# Spring day17 Jsoup으로 정적 페이지 크롤링

> 실습 파일: `day17/AppStart.java`, `day17/CrawService.java`
> 허브: [[Spring MOC]] · 이전: [[Spring day16 제미나이 API 키 서비스 뼈대]] · 다음: (아직 없음)

day17은 바깥 사이트의 HTML을 직접 받아 와서 필요한 글자만 뽑아내는 크롤링을 처음 해 본 시점이다. 지금까지는 바깥 API가 정리해 준 JSON을 받았다면, 이번에는 웹페이지 자체를 받아 그 안의 태그에서 값을 골라낸다. 라이브러리는 정적 페이지용 Jsoup이고, 서비스 클래스에 크롤링 메소드 두 개(`craw1`, `craw2`)가 만들어졌다.

## 1. 배운 내용

### 1-1. 새 패키지와 의존성

```java
package day17;

@SpringBootApplication
public class AppStart {
    public static void main(String[] args) {
        SpringApplication.run(AppStart.class);
    }
}
```

```groovy
implementation 'org.jsoup:jsoup:1.23.2' // 정적페이지 용도
```

day16까지와 같이 패키지마다 진입점을 두고, `build.gradle`에 Jsoup 의존성 한 줄을 더했다. 주석에도 적혀 있듯 이 라이브러리는 정적 페이지 용도다.

### 1-2. 크롤링 전에 정하는 네 가지

서비스 클래스 위의 주석에 크롤링 순서가 네 단계로 정리되어 있다.

| 순서 | 내용 |
| --- | --- |
| 1. 도구 선택 | 정적 페이지(자료가 한 번에 표시)는 Jsoup, 동적 페이지(구분별 자료가 순차적으로 표시)는 Playwright·Selenium 같은 브라우저 자동화 도구 |
| 2. 허용 여부 | 도메인 뒤에 `robots.txt`를 붙여 열어 보고 `Allow`/`Disallow`를 확인 |
| 3. 선택자 찾기 | 대상 페이지에서 F12(개발자도구) → `Ctrl+Shift+C`로 원하는 위치를 찍고, 그 요소의 태그·클래스·id를 확인 |
| 4. 차단 방지 | `User-Agent`를 실어 보내고, 요청 사이에 적당한 대기 시간을 둠 |

핵심은 3번이다. 어떤 선택자를 쓰느냐가 곧 크롤링 코드의 전부라서, 코드를 쓰기 전에 개발자도구에서 먼저 확인한다.

### 1-3. User-Agent 상수

```java
private final String USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) ... Chrome/154.0.0.0 Safari/537.36";
```

크롤링 요청에는 브라우저 정보를 문자열로 함께 보낸다. 값을 비워 두면 프로그램이 보낸 요청이라는 것이 그대로 드러나 막힐 수 있어서, 일반 브라우저와 같은 형태의 문자열을 상수로 한 번 정해 두고 매 요청에 붙인다.

### 1-4. `craw1` — 한 겹 크롤링: 제목 목록

```java
public List<String> craw1() {
    String url = "https://www.karnews.or.kr/news/articleList.html?sc_section_code=S1N1&view_type=sm";
    try {
        Document document = Jsoup.connect(url).userAgent(USER_AGENT).get();
        Elements elements = document.select(".titles > a");
        List<String> list = new ArrayList<>();
        for (Element element : elements) {
            list.add(element.text());
        }
        return list;
    } catch (Exception e) {
        System.out.println(e);
    }
    return null;
}
```

| 단계 | 설명 |
| --- | --- |
| 연결 | `Jsoup.connect(주소).userAgent(브라우저정보).get()`으로 HTML을 받아 `Document`로 만든다. 일반 예외(체크 예외)가 나므로 `try-catch`로 감싼다 |
| 선택 | `document.select(선택자)`에 CSS 선택자를 그대로 쓴다. `.titles > a`는 `titles` 클래스 바로 아래 자식 `a` 태그 |
| 타입 | 요소 한 개는 `Element`, 두 개 이상은 `Elements`. `Elements`는 `Element`들을 담은 목록이라 향상된 `for`로 돌 수 있다 |
| 추출 | `element.text()`는 여는 태그와 닫는 태그 사이의 글자만 꺼낸다 |

선택자 문법이 CSS와 같아서, 화면 쪽 자바스크립트에서 `querySelector`로 요소를 고르던 감각이 그대로 이어진다.

### 1-5. `craw2` — 여러 값 묶음: 도서명·가격·이미지

```java
Elements nameList  = document.select(".gd_name");
Elements priceList = document.select(".txt_num > .yes_b");
Elements imgList   = document.select(".img_bdr img");

List<Map<String, Object>> list = new ArrayList<>();
for (int index = 0; index < nameList.size(); index++) {
    Map<String, Object> map = new HashMap<>();
    map.put("name",  nameList.get(index).text());
    map.put("price", priceList.get(index).text());
    map.put("image", imgList.get(index).attr("data-original"));
    list.add(map);
}
```

한 상품의 정보가 서로 다른 위치에 흩어져 있어서 선택자를 항목별로 따로 만들고, 같은 순번끼리 묶어 `Map` 한 개로 만든다.

| 메소드 | 하는 일 |
| --- | --- |
| `.text()` | 태그 사이의 글자 |
| `.attr("속성명")` | 특정 속성의 값. 여기서는 이미지 주소를 `data-original`에서 꺼낸다 |

이미지 주소를 `src`가 아니라 `data-original`에서 꺼낸 이유는, 이런 쇼핑·서점 페이지가 이미지를 화면에 보일 때 늦게 불러오도록(지연 로딩) 실제 주소를 다른 속성에 넣어 두기 때문이다. 그래서 개발자도구에서 이미지 태그의 속성을 직접 열어 보고 값이 든 속성을 찾는다.

결과가 `List<Map>` 모양이라 컨트롤러가 그대로 반환하면 `[{name, price, image}, …]` 형태의 JSON이 된다. [[Spring day11 리액트 화면에 내줄 게시판 목록 API]]에서 본 "서버가 화면에 줄 목록"과 같은 모양이다.

## 2. 추가로 알면 좋은 활용법

### 2-1. `robots.txt`와 이용 약관 확인 습관

`robots.txt`에서 `Disallow`로 막아 둔 경로는 크롤링을 자제하는 것이 기본 예의다. 코드 상으로는 막혀 있어도 요청이 나가지만, 사이트 운영 방침과 약관을 어기는 문제가 될 수 있으므로 서비스에 쓰기 전에 확인한다.

### 2-2. 요청 사이 대기

반복해서 여러 페이지를 받을 때는 `Thread.sleep()`으로 간격을 둔다. 짧은 시간에 몰아서 보내면 IP가 차단되기 쉽다.

### 2-3. 찾는 값이 없을 때의 방어

`nameList`, `priceList`, `imgList`의 길이가 다르면 `get(index)`에서 범위 오류가 난다. 사이트 구조가 바뀌면 선택자가 빈 결과를 돌려주기도 하므로, 길이를 먼저 확인하거나 한 상품 단위의 부모 요소를 잡고 그 안에서 `select`하는 방식이 더 안전하다.

### 2-4. 컨트롤러로 열기

서비스에 만든 메소드는 `@GetMapping`을 붙인 컨트롤러 메소드에서 불러 JSON으로 내줄 수 있다. [[Spring day16 제미나이 API 키 서비스 뼈대]]에서 서비스와 컨트롤러를 나눈 것과 같은 구조다.

## 3. 더 나아가 알면 좋은 것

### 3-1. 동적 페이지는 도구가 다르다

스크롤하거나 버튼을 눌러야 내용이 나타나는 페이지는 Jsoup이 받은 HTML에 값이 아직 없다. 이럴 때는 브라우저를 실제로 띄워 자바스크립트까지 실행시키는 Playwright·Selenium이 필요하다.

### 3-2. 크롤링과 공식 API

공식 API가 있으면 그쪽이 안정적이다. 크롤링은 화면 구조가 바뀌면 바로 깨지고, 서버 부담과 법적 문제도 따른다. [[Spring day10 WebClient로 공공데이터 API 대신 호출하기]]처럼 API로 받을 수 있는지 먼저 살펴본다.

### 3-3. 크롤링 결과 저장과 주기 실행

받은 결과를 DB에 저장하고, `@Scheduled`로 일정 주기마다 갱신하는 구조로 이어갈 수 있다.

### 다음에 볼 키워드

- `Jsoup`, `Document`, `Elements`, CSS 선택자, `robots.txt`, `User-Agent`, Playwright, Selenium, `@Scheduled`

## 실습 파일

- `KDT_2026/2026B_Spring/springweb/src/main/java/day17/AppStart.java` — day17 진입점
- `.../day17/CrawService.java` — 크롤링 순서 주석, `craw1`(제목 목록), `craw2`(도서명·가격·이미지 묶음)
- `KDT_2026/2026B_Spring/springweb/build.gradle` — Jsoup 의존성

## 관련 노트

[[Spring MOC]] · [[Spring day16 제미나이 API 키 서비스 뼈대]] · [[Spring day10 WebClient로 공공데이터 API 대신 호출하기]] · [[Spring day11 리액트 화면에 내줄 게시판 목록 API]] · [[KDT_2026 학습 지도]]
