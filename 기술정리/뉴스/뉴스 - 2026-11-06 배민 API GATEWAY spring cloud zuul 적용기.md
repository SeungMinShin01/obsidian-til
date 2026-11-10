---
출처: Claude 분석(데일리 인풋)
원본: https://techblog.woowahan.com/2523/
작성일: 2026-11-06
성격: 예습자료
tags: [학습, spring]
---

# 뉴스 - 2026-11-06 배민 API GATEWAY spring cloud zuul 적용기

> 상위: [[뉴스 인덱스]]
> 이전: [[뉴스 - 2026-11-05 명령문 대신 결과를 보고, 믿음 대신 증명을 달았다]]
> 다음: [[뉴스 - 2026-11-06 찾기는 싸졌고, 값은 고르고 멈추는 데로 갔다]]

## 오늘의 글

배민 API GATEWAY – spring cloud zuul 적용기 — WoowaTech · 2017-06-13 · Backend
https://techblog.woowahan.com/2523/

## 배경

글은 7년 묵은 모놀리식 배민 API 서버(레거시)를 한 번에 도메인별로 쪼개기엔 DB 분리·스키마 재정의·마이그레이션 위험이 너무 크다고 설명한다(스키마가 틀리거나 정합성이 깨지면 서비스가 망가질 수 있다). 그래서 레거시를 "고립"시키고 도메인 단위로 조금씩 떼어내기로 했고, 서비스가 늘어도 클라이언트는 기존 URL 하나만 보게 하려고 API Gateway를 앞단에 두었다고 한다.

## 핵심

- 오픈소스 후보로 KONG, API Umbrella도 봤지만 "Java 프로젝트이고 MSA를 가장 잘하는 Netflix"의 Zuul을 골랐다고 한다.
- Zuul은 Filter 실행기다. 필터는 PRE(로깅·인증) → ROUTING(Apache HttpClient 또는 Ribbon) → POST(헤더 추가, 응답시간·상태코드 수집)이고, 오류 시 ERROR 필터가 돈다.
- 필터끼리 직접 통신하지 않고 요청별 `RequestContext`를 공유한다(thread local과 비슷하다고 설명).
- 순정 zuul-netflix-webapp은 학습곡선이 커서 Spring Cloud Netflix를 택했다. `spring-cloud-starter-zuul` 의존성과 main 클래스의 `@EnableZuulProxy`만으로 서버가 뜬다. `@EnableZuulProxy` = `@EnableZuulServer` + PreDecorationFilter·RibbonRoutingFilter·SimpleHostRoutingFilter.
- Spring MVC 위 구조: `RouteLocator`(경로 정의) → `ZuulHandlerMapping`(AbstractUrlHandlerMapping 상속) → `ZuulController`(ServletWrappingController 상속) → `ZuulServlet`. `ZuulFilterInitializer`가 필터를 FilterRegistry에 등록하고 FilterLoader로 로딩한다.
- 라우팅은 yml의 URL path 기준이다. `info/notice/**`는 신규 API 서버의 `/v1/notice`로, 나머지 `/**`는 레거시 ELB로 보낸다. 도메인이 분리될 때마다 route와 ELB를 추가한다.
- 반려한 대안은 Eureka(serviceId 라우팅)다. 이유: Eureka 운영·관리 비용(가장 큰 이유), ELB에서 서버를 빼고 배포 후 붙이는 기존 배포 방식 변경 필요, 서버 목록이 아직 적음, ELB 경유 응답시간 차이 5ms 이내.
- Spring Cloud의 `@Bean` 필터는 Java 정적 정의만 가능해 실시간 대응에 부족하다고 보고, `FilterFileManager`로 지정 디렉토리의 Groovy 필터를 주기적으로 읽어 런타임에 반영하게 했다고 한다.

## 내 프로젝트와의 연결

- WMS: 3주 팀 프로젝트에 게이트웨이/MSA는 과하므로 직접 이식할 부분은 적다. 다만 "한 번에 갈아엎지 않고 경로 단위로 새 구현에 트래픽을 넘기며 레거시를 줄인다"는 구조는 입고·재고·출고를 단계적으로 옮기는 생각틀로 구조적으로 비슷하다. "Eureka는 지금 필요 없다"며 기각 근거를 비용·현황으로 적은 방식은 결정 로그(기각 사유) 작성 예시로도 쓸 만하다.
- 수집기: 연결이 약하다.
- 2017년 글이라 Zuul 1 / `spring-cloud-starter-zuul`은 현재 Spring Cloud Gateway로 대체된 것으로 알려져 있으나, 글에는 없는 내용이므로 확인이 필요하다.

## 오늘 정리할 것

1. 글의 요청 흐름(ZuulHandlerMapping → ZuulController → ZuulServlet → PRE/ROUTING/POST)을 Spring MVC의 DispatcherServlet → HandlerMapping → Controller 흐름과 나란히 그려본다.
2. yml route 예시(path/url, `/**` 폴백)를 직접 써보고, 라우트가 겹칠 때 어느 쪽이 우선하는지 공식 문서에서 확인한다.
3. 현재 Spring Cloud Gateway에서 같은 구성(경로 기준 분기 + 로깅 필터)을 어떻게 쓰는지 찾아 Zuul 용어와 대응시킨다.
4. Eureka 대신 ELB를 택한 근거 4가지를 WMS 결정 로그 형식(문제→대안→선택→기각 사유)으로 옮겨 적는다.
