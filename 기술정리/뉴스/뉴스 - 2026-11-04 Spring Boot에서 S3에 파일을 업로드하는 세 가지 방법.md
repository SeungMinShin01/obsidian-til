---
출처: Claude 분석(데일리 인풋)
원본: https://techblog.woowahan.com/11392/
작성일: 2026-11-04
성격: 예습자료
tags: [학습, spring]
---

# 뉴스 - 2026-11-04 Spring Boot에서 S3에 파일을 업로드하는 세 가지 방법

> 상위: [[뉴스 인덱스]]
> 이전: [[뉴스 - 2026-11-03 다시 짓지 않고 고쳤고, 고친 범위는 증명해야 했다]]
> 다음: [[뉴스 - 2026-11-04 묶인 주장은 풀려 읽혔고, 동의는 설치 스크립트가 대신 눌렀다]]

박민규(세일즈서비스팀) · 2023-09-21 · AWS / Backend — 원문: https://techblog.woowahan.com/11392/

## 배경

전자계약서 시스템(Spring Boot + Kotlin)에서 최대 3GB 파일을 안정적으로 올려야 했다. 글은 방법이 크게 ① Stream ② MultipartFile ③ AWS Multipart 세 가지로 수렴한다고 보고, 각각의 원리와 한계를 비교한다. 예제는 AWS SDK for Java 1.x 기준이다.

## 핵심

- **Stream 업로드**: HttpServletRequest의 InputStream을 S3로 바로 흘려보낸다. 파일 전체를 디스크·힙에 두지 않지만(Grafana로 확인) 전처리(리사이징 등)가 불가능하고 요청당 파일 1개만 가능하다. 글의 측정에서 937MB 업로드에 약 16분이 걸렸고, 진행률을 줄 수 없으며 실패하면 처음부터 다시 올려야 한다.
- Stream 방식에서 ObjectMetadata의 content-type·content-length는 요청 헤더에서 가져온다. Nginx 앞단이면 별도 설정이 필요하다고 한다.
- **MultipartFile 업로드**: Tomcat이 임시 디렉터리(location)에 저장하고 요청이 끝나면 지운다. 배포·장애 시 임시 파일이 남을 수 있어 경로를 직접 지정하라고 권한다. `file-size-threshold` 이하는 임시 파일 없이 메모리에 바로 올라간다.
- Stream·MultipartFile은 동시 요청이 몰리면 서버 스레드가 고갈될 수 있다. 대응으로 resilience4j bulkhead(동시 작업 수 제한·별도 스레드 풀) 또는 업로드 전담 서버 분리를 제시한다.
- **AWS Multipart 업로드**: ① initiate-upload로 Upload ID 받기 → ② 파트별 PresignedURL 발급(PartNumber 1~10,000) → ③ 클라이언트가 PUT으로 파트 업로드(5MB~5GB, 마지막 파트만 예외), 응답 헤더 ETag 보관 → ④ complete 요청에 Upload ID와 PartNumber·ETag 배열을 실어 S3가 조립. 바이너리가 Spring Boot를 거치지 않는다.
- Multipart 운영 포인트: 완료하지 않으면 객체가 생기지 않고, 중단된 파트도 스토리지 비용이 나가므로 예외 시 abort가 필요하다(취소한 Upload ID는 재사용 불가). 버킷 Lifecycle rule로 미완료 파트 자동 삭제를 건다. 브라우저가 amazonaws.com으로 직접 요청하므로 버킷 CORS 설정이 필요하다.
- 결론 표: 진행률 표시는 AWS Multipart만 가능, 구현 복잡도는 Stream < MultipartFile < AWS Multipart. 글은 기술 선택에 성능뿐 아니라 구현 복잡도를 함께 보라고 하며, 20MB 프로필 이미지에 AWS Multipart를 쓰면 오버 엔지니어링이라고 말한다.

## 내 프로젝트와의 연결

글은 "파일 크기와 운영 조건에 맞춰 방식을 고른다"는 판단 기준을 준다. WMS에서 입고 엑셀·송장 이미지 같은 업로드가 생긴다면 용량이 작을 가능성이 커 MultipartFile 수준이면 충분할 수 있다(사용자 검증 필요). 수집기와는 직접 연결이 약하다. 구조적으로 비슷한 지점은 "중간에 실패한 작업을 이어서/정리하는 방식"이다 — Multipart의 abort·Lifecycle 정리는 수집기의 재시도·멱등성, 미완료 상태 청소 문제와 닮았다.

## 오늘 정리할 것

1. Spring Boot의 `spring.servlet.multipart.max-file-size`, `max-request-size`, `location`, `file-size-threshold` 기본값을 공식 문서에서 확인해 표로 적는다.
2. Stream / MultipartFile / AWS Multipart가 파일 바이너리를 어디(힙·디스크·S3 직행)에 두는지 한 줄씩 직접 그려 본다.
3. S3 Multipart의 4단계(Upload ID → Presigned URL → ETag 보관 → complete)와 abort가 필요한 이유를 내 말로 요약한다.
4. WMS에서 업로드가 생길 만한 기능을 적고, 글의 결론 표 기준으로 어떤 방식이면 충분할지 가설을 적어 둔다.
