---
출처: Claude 분석(데일리 인풋)
원본: https://techblog.woowahan.com/2597/
작성일: 2026-10-06
성격: 예습자료
tags: [학습, spring]
---

# 뉴스 - 2026-10-06 Spring Rest Docs 적용

> 상위: [[뉴스 인덱스]]
> 이전: [[뉴스 - 2026-10-05 멈춤과 폐기를 기본값으로]]
> 다음: [[뉴스 - 2026-10-06 모델은 책상으로 내려오고, 비용은 남의 서버로 갔다]]

이호진 · 2018-12-28 · Backend (정산시스템 개발자). 글은 아래와 같이 설명한다 — 사용자 미검증 예습자료.

## 배경
정산시스템은 API 문서를 wiki로 관리했는데 코드와 문서가 어긋났다. 글은 "있어야 할 필드가 없었고 없어야 할 필드가 있었으며 같은 값을 주는 필드가 각기 다른 이름으로 제공"되는 상황이 생겼다고 설명한다.

## 핵심
- Swagger와 비교: Swagger는 테스트 화면 제공·적용이 쉽지만 코드에 어노테이션이 필수라 동기화 위험이 있다고 보았다. Spring Rest Docs는 제품 코드에 영향이 없고 **테스트가 성공할 때만 문서가 생성**되지만 적용 복잡도가 높다. "문서의 목적은 개발 스펙을 정의하는 것"이라는 이유로 Rest Docs 채택.
- 스택: Spring Boot 2.1.1, Gradle 4.8.1, JUnit 4(Spock은 문서화용으로 과하다고 반려), MockMvc + `@WebMvcTest`(Rest Assured 대비 Controller 레이어만 띄워 빠름), AsciiDoc(Markdown은 include 제한).
- Gradle: `testImplementation('org.springframework.restdocs:spring-restdocs-mockmvc')`, 플러그인 `org.asciidoctor.convert 1.5.9.2`. 순서는 test → asciidoctor → bootJar → `/static/docs`로 HTML 복사.
- 테스트: `@WebMvcTest(PersonController.class)` + `@AutoConfigureRestDocs(uriScheme="https", uriHost="docs.api.com")`, 서비스는 MockBean, `document()`로 스니펫 생성(`./build/generated-snippets/[문서명]/`).
- 스니펫 커스터마이징: `src/test/resources/org/springframework/restdocs/templates/` 아래 Mustache 템플릿.
- 확장: 필수값 표시(`fieldWithPath("hobby").optional()` + `{{^optional}}true{{/optional}}`), 입력 포맷(`attributes(key("format").value("yyyy-MM-dd"))`), Enum 코드값 표(CustomResponseFieldsSnippet), 공통 응답(code·message·data)을 `beneathPath()`+`withSubsectionId()`로 분리.
- 성과: 코드-문서 동기화 보장, 기존 잘못된 API 문서 발견·수정.

## 내 프로젝트와의 연결
WMS(Spring Boot + React)에서 입고·재고·출고 API 명세를 프론트와 맞출 때 구조적으로 비슷한 지점이 있다 — 테스트가 통과해야 문서가 나오므로 문서가 곧 계약 테스트 역할을 한다. 다만 글은 2018년 기준(Boot 2.1, JUnit 4)이라 현재 버전 설정은 따로 확인이 필요하다. 수집기는 API 서버가 아니라 직접 연결은 약하다.

## 오늘 정리할 것
1. Spring Rest Docs 공식 문서에서 `document()`가 만드는 기본 스니펫 종류(request/response-fields 등) 확인.
2. `@WebMvcTest`와 `@SpringBootTest`가 띄우는 빈 범위 차이를 표로 정리.
3. Swagger(springdoc)와 Rest Docs의 문서 생성 시점·동기화 보장 차이를 3줄로 정리.
4. WMS 입고 API 하나를 골라 필수/선택 필드를 나열해 보기.
