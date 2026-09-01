---
출처: Claude 대화
작성일: 2026-09-01
tags: [프로젝트]
---

# WMS 진행 상황

> 허브: [[WMS 프로젝트 MOC]]

지금 어디까지 왔는지의 **스냅샷**. 세션이 끝날 때마다 덮어쓴다.
날짜별 누적 로그는 MOC의 「진행 기록」 절에 있다.

---

## 지금

0일차 진행 중. 0-A(로컬 관통) 끝, 0-B(서버 관통)는 절반쯤.
서버는 준비 끝났고 코드를 아직 안 올림.

## 완료

- [x] docker compose (MySQL 8.0, 로컬 3307)
- [x] Spring Boot 4.1.1 — JPA / Flyway / Actuator / Swagger
- [x] React + Vite (TS), 프록시로 /api 연결
- [x] /api/ping → 화면 표시 확인 (0-A 끝)
- [x] GitHub 공개 (SeungMinShin01/WMS-Web)
- [x] EC2 t3.micro 서울, Ubuntu 24.04, 20GB
- [x] 스왑 2GB, Docker 설치
- [x] 서버 MySQL 기동 (deploy/docker-compose.yml + .env)
- [x] nginx 설치, 기본 페이지 인터넷에서 확인

## 남은 것 (0-B)

- [ ] nginx 설정 — 정적 파일 + /api 프록시
- [ ] 백엔드 JAR 빌드 → scp → systemd 등록
- [ ] 프론트 build → dist scp → /var/www/wms-web
- [ ] 도메인 + HTTPS (DuckDNS 또는 구매)

## 막힌 것

- 없음. Oracle 가입이 카드 명의 문제로 실패해서 AWS로 갈아탐
- 서버 배포 절차가 아직 손에 안 붙음 → [[WMS 배포 절차]] 빈칸 채우면서 정리 중

## 메모

- 서버 IP는 자동 할당이라 인스턴스를 중지했다 켜면 바뀜
- 측정은 로컬 도커에서. 서버(1GB)는 시연용
- AWS 크레딧 $100, 월 $17쯤 나감

## 다음에 할 일

- nginx 설정부터. `deploy/nginx/wms-web.conf` 만들고 서버에 복사

## 관련 노트

[[WMS 배포 절차]]
