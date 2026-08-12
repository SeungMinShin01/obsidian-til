---
출처: Claude 분석
원본: shirhal/front-end/src/components
작성일: 2026-08-11
tags: [프로젝트, 일지, 보드게임카페예약사이트, react]
---

# components 분석 - MainPage와 고객지원

대상: `MainPage/` 6개 (MainPage · introduce · store · Beverage · ImageSliderSection · ImageSliderSimple) · `CustomerSupoort/CustomerSupport.js`
상위: [[보드게임카페예약사이트 프로젝트 MOC]]

## MainPage.js — 705줄의 얼굴

사이트 첫 화면. 메인 캐러셀 + 소개 섹션 + 인기 게임(TOP3) + 바로가기들이 한 파일에 있다. 705줄 중 절반 이상이 styled-components 정의다. 캐러셀 로직은 `useCarousel` 훅으로 빠져 있어서( → [[hooks 분석]] ) 로직 자체는 얇다.

파일 하단에 `MainImageCarousel`을 별도 함수 컴포넌트로 두고 훅을 그 안에서 쓰는 구조 — 한 파일 안에서라도 역할을 쪼갠 흔적이다.

> **피드백** — 705줄의 원인은 로직이 아니라 **스타일 정의가 화면 코드와 같은 파일에 있다는 것**이다. 섹션별로 파일을 나누거나(`HeroSection.js`, `PopularGames.js`...), styled 정의만 `MainPage.styles.js`로 분리하는 게 관례다. "스크롤을 세 번 넘겨야 JSX가 나오는 파일"은 나누라는 신호로 읽으면 된다.

## introduce.js / ImageSliderSection.js — 매장 소개

`introduce`는 매장 소개 텍스트 + `ImageSliderSection`(썸네일 슬라이더). 슬라이더는 메인 인덱스, 썸네일 시작 위치, 페이드, 슬라이드 오프셋, 애니메이션 중 여부까지 **상태 5개**로 전환 효과를 수동 구현했다. `getThumbsWithBuffer`로 썸네일 순환 버퍼를 계산하는 등 공들인 부분이다. `ImageSliderSimple`은 같은 걸 단순화한 변형.

> **피드백** — 상태 5개가 서로 맞물리는 애니메이션은 버그가 숨기 좋은 자리다. CSS transition + 인덱스 상태 1개로 같은 효과를 내는 방법을 먼저 검토하고, 안 되면 그때 상태를 늘리는 순서가 맞다. 비슷한 슬라이더가 세 군데(`useCarousel` · `ImageSliderSection` · `ImageSliderSimple`) 각각 구현돼 있는데, props로 변형을 받는 슬라이더 컴포넌트 하나로 합칠 수 있었다 — **중복 구현 세 개는 수정도 세 번**이라는 비용이 된다.

## store.js — 매장 찾기

`data/storeData.js`의 매장 정보(좌표·주소·영업시간)를 `useStore` 훅에 넘겨 **카카오맵**을 그린다. 본문 지도와 모달 확대 지도가 각각 `mapRef`를 가진다. 매장 데이터가 코드와 분리돼 있어서 지점 추가는 데이터 파일 수정으로 끝난다. → [[data와 styles 분석]]

## Beverage.js — 음료 메뉴

`data/menuData.js`(185줄, 커피/논커피/티 분류)를 카테고리 탭으로 필터링해 보여준다. `selected` 상태 하나 + `filter` 렌더링 — 전형적인 **데이터 주도 UI**라 로직이 거의 없다.

## CustomerSupport.js — 636줄, 공지 + 문의

한 화면에 공지 목록, 문의 작성 폼, 내 문의 목록 세 덩어리가 있다. 로직은 `useCustomerSupport` 훅에, 파일 길이는 역시 styled 정의가 만든다.

- 문의 폼에 **개인정보 수집 동의** 체크박스가 있고 미동의 시 제출을 막는다
- 문의자 이름을 `localStorage.user_name`으로 미리 채운다

> **피드백** — 동의 문구·항목이 코드에 하드코딩이다. 실제 서비스라면 동의 이력(누가 언제 어떤 문구에)을 서버에 남겨야 법적 의미가 있다 — 체크박스는 UI일 뿐이고 기록이 본체다. 화면 구성상 공지/문의작성/내문의는 탭이나 라우트로 나뉘는 게 자연스러운 규모가 됐다. 파일 길이 문제의 답은 MainPage와 같다: 섹션 분리.

## 관련 노트

[[보드게임카페예약사이트 프로젝트 MOC]] · [[hooks 분석]] · [[routes 분석 - 고객지원과 관리자]] · [[data와 styles 분석]] · [[전문용어 정리]]
