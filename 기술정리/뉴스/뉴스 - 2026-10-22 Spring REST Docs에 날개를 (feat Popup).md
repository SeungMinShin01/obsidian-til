---
출처: Claude 분석(데일리 인풋)
원본: https://techblog.woowahan.com/2678/
작성일: 2026-10-22
성격: 예습자료
tags: [학습, spring]
---

# 뉴스 - 2026-10-22 Spring REST Docs에 날개를 (feat Popup)

> 상위: [[뉴스 인덱스]]
> 이전: [[뉴스 - 2026-10-21 엔진은 열렸고, 신뢰는 번들 파일 안에 있었다]]
> 다음: [[뉴스 - 2026-10-22 알아낸 것과 결정한 것 사이에서 2년이 갔다]]

우아한형제들 정산시스템팀(이호진) · 2020-05-13 · Backend

## 배경

글은 2018년에 도입한 Spring REST Docs가 1년 반 동안 API가 늘면서 불편해진 지점을 다룬다고 설명한다. 도입 직후에는 타 시스템에 API 스펙을 빠르게 제공하는 장점이 컸지만, 규모가 커지자 ① 느린 테스트 빌드 ② 응답 필드의 허용 코드가 문서 상단에 있어 확인이 불편 ③ 상단 코드 목록이 길어 본문 파악 방해 ④ 반복 코드 때문에 의미 파악 저해 ⑤ 버저닝된 응답 비교 불편이 드러났다고 한다.

## 핵심

- 빌드 속도: 문서 테스트마다 `@WebMvcTest` + REST Docs 설정 어노테이션을 붙이면 Spring Context가 반복 생성된다. 글은 이를 `ApiDocumentationTest` 추상 클래스 한 곳에 선언하고 각 문서 테스트가 상속하게 해 컨텍스트 재생성을 막았고, 테스트가 많을수록 시간 차이가 커졌다고 한다.
- 응답 필드의 코드 값: asciidoc이 `id=job` 형태의 div를 만드는 점을 이용해 필드 설명에 `href="url#job"` 해시 링크를 걸었다.
- 공통 코드 분리: 해시 링크는 화면이 상단으로 튀어 돌아오기 불편해 `common/job.adoc` 별도 파일로 분리하고 상대 링크 + `window="_blank"`(새 창)로 바꿨다.
- 팝업: 새 창도 불편(돌아가기·불필요한 코드 목록 노출)해 asciidoc에 없는 팝업을 asciidoctor `docinfo`(adoc에 html을 주입; private/shared, head/footer 조합, docinfo1·2는 alias)로 해결했다. `docinfo.html`에 `class="popup"` 링크 클릭 시 팝업을 띄우는 JS를 두고, 링크에 `role="popup"`(role이 class가 됨)을 준다.
- 반복 제거: `link:common/job.html[직업 코드,role="popup"]` 문자열을 `DocumentLinkGenerator`(테스트 패키지)와 `DocUrl` enum(pageId=common 폴더 파일명, text=노출 문구)으로 감싸 오타를 막았다. 링크 없는 단순 코드명용 유틸도 별도로 둔다.
- 글의 결론은 "처음엔 못 느끼던 문제를 확장되면서 느낀다"는 것이다. 팝업 방식은 글쓴이 본인도 꼼수라 부르는 방법이다.

## 내 프로젝트와의 연결

WMS(Spring Boot + React)에서 입고·재고·출고 API가 늘면 프론트와 스펙을 맞추는 문서가 필요해지는데, 글의 "문서 테스트용 슬라이스 컨텍스트를 한 번만 선언하고 상속" 구조는 테스트 속도 측면에서 구조적으로 비슷한 지점이다. 재고 상태·입출고 구분 같은 코드 값을 enum + 링크로 문서화하는 발상도 옮겨 볼 만하다. 다만 REST Docs 자체가 WMS에 쓰일지는 정해진 바 없고, 수집기와의 직접 연결은 약하다. 글은 2020년 기준이라 현재 Spring REST Docs·asciidoctor 버전에서 같은 방식이 통하는지는 검증되지 않았다.

## 오늘 정리할 것

1. `@WebMvcTest`가 테스트 클래스마다 새 컨텍스트를 만드는 조건(캐시 키가 무엇으로 정해지는지)을 Spring TestContext 캐싱 문서에서 확인해 한 줄로 정리.
2. Spring REST Docs의 핵심 흐름(테스트 실행 → snippet 생성 → adoc include → html)을 손으로 그려 보기.
3. asciidoctor `docinfo` 옵션(shared/private, head/footer)을 문서에서 찾아 표로 정리.
4. WMS API에서 코드 값으로 문서화할 후보(재고 상태, 입출고 유형)를 3개 적어 보기.
