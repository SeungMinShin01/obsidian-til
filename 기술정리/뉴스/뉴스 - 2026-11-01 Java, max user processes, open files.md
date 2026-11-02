---
출처: Claude 분석(데일리 인풋)
원본: https://techblog.woowahan.com/2569/
작성일: 2026-11-01
성격: 예습자료
tags: [학습, java]
---

# 뉴스 - 2026-11-01 Java, max user processes, open files

> 상위: [[뉴스 인덱스]]
> 이전: [[뉴스 - 2026-10-30 가중치는 열렸고, 숫자는 출처까지 따라가야 했다]]
> 다음: [[뉴스 - 2026-11-01 부분 점수와 완료 사이, 주장과 검증 사이]]

- 저자·날짜·카테고리: 이동욱(결제/정산 시스템) · 2018-04-17 · Backend, Infra
- 원문: https://techblog.woowahan.com/2569/
- 이 노트는 예습자료(자동 생성, 사용자 미검증)다. 아래는 글의 주장을 "글은 ~라고 설명한다" 관점으로 옮긴 것이다.

## 배경

글은 팀 서버 작업 중 쓰레드 관련 장애를 옆에서 지켜보며 `open files`와 `max user processes`가 무엇을 제한하는지 전혀 몰랐다는 데서 출발했다고 설명한다. 톰캣 운영 중 "더 이상 쓰레드를 생성할 수 없다"는 `OutOfMemoryError`가 났다고 가정하고, 어떤 OS 제한이 원인인지 AWS EC2 위에서 직접 실험으로 가려낸다. 샘플 코드는 실제 회사 코드가 아니라 별도로 만든 것이라고 밝힌다.

## 핵심

- `ulimit -a`는 soft limit, `ulimit -aH`는 hard limit을 보여준다. 초기 서버는 `open files`와 `max user processes`가 모두 1024였고, t2.micro 기본값은 open files 1024 / max user processes 3902였다고 글은 설명한다.
- 실험 1(쓰레드): `/4000` 요청 시 비동기로 쓰레드 4천 개를 만들어 20분 유지하게 하자 3855번째에서 `unable to create new native thread`가 났다. open files(1024)를 넘어 생성됐으므로 쓰레드 수는 `max user processes`를 따른다는 결론이다(Linux는 프로세스와 쓰레드를 동일하게 본다).
- 실험 2(소켓): RestTemplate 타임아웃을 30분으로 두고, 상대 서버가 20분간 응답을 지연시키는 요청 1100개를 동시에 보냈다. t2.micro는 메모리(1GB)가 먼저 부족해 t2.large(8GB)로 올렸고, 이때 `max user processes`는 인스턴스 사양에 맞게 AWS가 자동 설정하므로 손댈 필요가 없다고 글은 설명한다.
- 이상한 결과: soft open files가 1024인데 1330개가 열렸고, 1100개씩 3번(3300개)도 에러가 없었다. 총 4400개를 보내자 4097개에서 `Too many open files`가 났는데, hard limit이 정확히 4096이었다.
- 검증: hard를 5120으로 올리고 soft는 1024로 둔 채 재실행하자 4635개까지 열렸다. 소켓 생성 제한은 soft가 아니라 hard를 따라간 것으로 보인다고 글은 결론짓는다.
- 파이썬 반례: 같은 조건(soft 1024/hard 4096)에서 파이썬은 soft(표준 입출력 3개 제외 1021개)에서 바로 `Too many open files`가 났고, soft를 2000으로 올려도 같았다. 그래서 JVM이 다른 이유를 찾았다.
- 원인: `strace`로 JVM을 보니 `setrlimit` 호출이 있었고, HotSpot 옵션 `MaxFDLimit`(기본 true)이 켜져 있으면 JDK가 시작 시 soft limit을 hard limit까지 올린다(openjdk `os_linux.cpp`)고 글은 설명한다.
- 결론: Java에서 동시 쓰레드 수는 `max user processes`, 소켓 통신(HTTP API·JDBC 커넥션 등)은 `open files`를 따르되 JDK가 soft를 hard로 끌어올린다. Tomcat 8부터 기본 Connector가 NIO라 maxConnections 10,000 / maxThreads 200이 기본값이다(7까지는 BIO, 둘이 같아야 함).
- 영구 설정: 보통 soft와 hard를 같게 두고 `/etc/security/limits.conf`에 `*`(전 사용자) 또는 계정명 기준으로 적는다. 재접속 후 `ulimit`으로 확인한다.

## 내 프로젝트와의 연결

수집기와는 직접 이어지는 부분은 약하고, 구조적으로 비슷한 지점만 있다. 채용공고 API를 병렬로 많이 호출하면 연결 하나하나가 파일 디스크립터라서, 동시 요청 수를 늘리는 설계에서는 "얼마까지가 안전한가"를 OS 제한 관점에서도 따질 수 있다(GitHub Actions 러너의 실제 값은 글에 없으므로 직접 확인해야 한다). WMS 쪽은 부하 테스트와 닿는다. Spring Boot의 Tomcat maxThreads(기본 200)·maxConnections와 HikariCP 풀(DB 연결 = 소켓 = open file)을 늘릴 때, 병목이 애플리케이션 설정인지 OS 제한인지 가르는 실험 방식(프로세스의 열린 파일 수를 세면서 부하를 올리기)을 그대로 옮겨 볼 수 있다. 다만 글은 2018년 EC2 기준 실험이고, 컨테이너·최신 JDK에서의 결과는 검증되지 않았다.

## 오늘 정리할 것

1. 내 로컬(또는 WSL/리눅스)에서 `ulimit -a`와 `ulimit -aH`를 찍어 soft/hard 값을 표로 적어 본다.
2. 실행 중인 Java 프로세스의 열린 파일 개수를 `ls /proc/<PID>/fd | wc -l`로 세어 보고, 부하를 주기 전후로 비교한다.
3. 글의 `MaxFDLimit`을 `java -XX:+PrintFlagsFinal -version | grep MaxFDLimit`로 확인하고, 사용 중인 JDK 버전에서도 기본값이 true인지 본다.
4. Tomcat maxThreads(200)·maxConnections(10,000)와 HikariCP maximumPoolSize 기본값이 각각 어떤 OS 제한(max user processes / open files)에 걸리는지 연결해 한 줄씩 적는다.
