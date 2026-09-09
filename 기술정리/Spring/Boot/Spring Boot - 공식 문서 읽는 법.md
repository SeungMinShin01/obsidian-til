---
출처: 내가 작성
작성일: 2026-09-09
tags: [학습, spring]
개념키: spring/official-docs-reading
트랙: 부트
정본: true
---

# Spring — 공식 문서 읽는 법

> 상위: [[Boot 정리 인덱스]]

스프링 부트 학습을 공식 레퍼런스 기준으로 진행하면서 정리한 것이다. 문서 안에서 **길을 잃지 않는 법**과, 같은 사실이 여러 곳에 다르게 적혀 있을 때 **어느 쪽을 믿을지**를 다룬다.

기준 버전은 Spring Boot 4.1.1. 진입점은 하나다.

```
https://docs.spring.io/spring-boot/index.html
```

## 1. 문서는 성격이 다른 6개 구역으로 나뉜다

가장 먼저 잡아야 할 것은 "무엇이 어디 있나"가 아니라 **"이 구역은 어떤 질문에 답하는 곳인가"** 다. 구역마다 쓰인 목적이 달라서, 같은 주제라도 서술 깊이와 신뢰도가 다르다.

| 구역 | 답하는 질문 | 여는 시점 |
| --- | --- | --- |
| Tutorial | "따라 하면 하나 만들어지나" | 처음 시작할 때 한 번 |
| **Reference** | "이게 무엇이고 어떻게 동작하나" | **평소에 읽는 본체** |
| How-to Guides | "이 상황에서는 어떻게 하나" | 문제가 생겼을 때 |
| Build Tool Plugins | "그레이들·메이븐 플러그인을 어떻게 쓰나" | 빌드가 안 될 때 |
| Specification | "내부 규격이 어떻게 되나" | "왜 이렇게 도는지"가 궁금할 때 |
| Appendix | "그 값이 정확히 뭐였나" | 설정 키·버전을 찾을 때 |

구역별 경로는 이렇다.

```
https://docs.spring.io/spring-boot/tutorial/index.html
https://docs.spring.io/spring-boot/reference/index.html
https://docs.spring.io/spring-boot/how-to/index.html
https://docs.spring.io/spring-boot/build-tool-plugin/index.html
https://docs.spring.io/spring-boot/specification/
https://docs.spring.io/spring-boot/api/java/index.html
```

### 읽는 순서의 원칙

**Reference가 기본이고, 나머지는 Reference에서 뻗어 나가는 곁가지다.**

```
Tutorial 로 감을 잡고
  → Reference 로 이해하고
    → Specification 으로 파고들고
      → Appendix 에서 값을 찾는다
    ↘ How-to 는 막혔을 때만 옆으로 빠진다
```

Tutorial부터 정독하려 들면 "돌아가긴 하는데 왜 그런지 모르는" 상태가 된다. 반대로 Reference를 처음부터 순서대로 읽으려 들면 맥락이 없어 안 읽힌다. 감 → 이해 → 규격의 순서가 맞다.

## 2. Reference 안에서 길 잡기

Reference의 상위 절은 다음과 같다. 이 목록이 사실상 학습 로드맵이 된다.

- Developing with Spring Boot — 빌드 시스템, 코드 구조, 자동설정, 실행
- Core Features — SpringApplication, 외부 설정, 프로파일, 로깅
- Web — 서블릿 웹 애플리케이션, WebFlux
- Data — SQL·NoSQL 데이터 접근
- IO / Messaging / Security / Testing
- Packaging Spring Boot Applications
- Production-ready Features — Actuator

한 모듈을 공부할 때는 **그 모듈이 Reference의 어느 절인지 먼저 확인**하고 들어간다. 절 하나가 곧 학습 단위다.

## 3. 같은 사실이 다르게 적혀 있을 때

문서를 읽다 보면 숫자나 서술이 구역마다 어긋나는 것을 만난다. 대부분 **틀린 게 아니라 성격이 다른 값**이다.

예 — 필요한 메이븐 버전:

| 출처 | 값 | 성격 |
| --- | --- | --- |
| System Requirements | Maven 3.6.3 이상 | 공식 최소선. "이 아래는 지원하지 않는다" |
| Tutorial | Maven 3.9.12 이상 | 그 예제를 실제로 돌려 검증한 버전 |

판단 기준은 **질문의 종류**다.

- "규격이 뭔가" → Reference / System Requirements
- "실제로 돌아가는 조합이 뭔가" → Tutorial
- "이 상황에서 권장은 뭔가" → How-to

## 4. 문서가 쓰는 관용 표현

읽을 때 신호로 삼을 것들.

| 표현 | 뜻 |
| --- | --- |
| "recommended" | 다른 길도 있지만 이쪽을 쓰라는 뜻. 반대편 설명이 대개 바로 아래 있다 |
| "deprecated" | 아직 동작하지만 다음 메이저에서 빠질 수 있다. 새 코드에는 쓰지 않는다 |
| Maven / Gradle 탭 | 같은 내용의 빌드 도구별 표기. 둘 다 볼 필요 없다 |
| Java / Kotlin 탭 | 마찬가지. 쓰는 언어만 본다 |
| 회색 박스(NOTE·TIP) | 대개 실무에서 자주 걸리는 함정이다. 건너뛰지 않는 편이 낫다 |

## 5. 버전을 고정해서 읽는다

URL에 버전이 없으면 **현재 최신 버전**의 문서가 열린다. 시간이 지나 서술이 바뀌면 예전에 읽은 것과 달라진다. 특정 버전을 고정해 보려면 페이지 우하단(또는 상단)의 버전 선택기를 쓴다.

원문을 보고 싶으면 문서 소스가 GitHub에 있다. asciidoc(`.adoc`) 원본이고, 태그로 버전을 고정할 수 있다.

```
https://github.com/spring-projects/spring-boot/tree/v4.1.1/documentation
```

릴리스마다 무엇이 바뀌었는지는 위키의 마이그레이션 가이드가 가장 빠르다.

```
https://github.com/spring-projects/spring-boot/wiki
```

## 6. 인터넷 자료를 읽을 때의 보정

검색으로 나오는 블로그·강의 자료는 대부분 **부트 2.x~3.x 시절**이다. 부트 4 문서와 대조하며 아래를 치환해서 읽는다.

| 옛 자료 | 지금 |
| --- | --- |
| `javax.servlet.*` | `jakarta.servlet.*` |
| `spring-boot-starter-web` | `spring-boot-starter-webmvc` (앞의 것은 deprecated) |
| Java 8·11 기준 서술 | Java 17 이상 |

"자료가 틀렸다"가 아니라 **버전이 다르다**로 보는 습관이 중요하다. 판정 기준은 항상 공식 문서 쪽이다.

## 7. 한 모듈을 끝낼 때 남기는 것

모듈마다 아래 세 가지를 정리본에 남긴다.

1. **문서 경로** — 어느 구역의 어느 절을 읽었는지
2. **참조 URL** — 실제로 근거로 삼은 페이지 주소
3. **다음 경로** — 이 절에서 자연스럽게 이어지는 다음 절

이렇게 두면 나중에 같은 주제를 다시 볼 때 검색이 아니라 **경로로** 되돌아갈 수 있다.
