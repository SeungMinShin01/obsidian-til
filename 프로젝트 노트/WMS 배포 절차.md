---
출처: Claude 대화
작성일: 2026-09-01
tags: [프로젝트]
---

# WMS 배포 절차

> 허브: [[WMS 프로젝트 MOC]]

빈 서버에 이 프로젝트를 처음부터 올리는 방법.

**「왜」 칸은 직접 채운다.** 채우다 막히는 줄이 곧 이해가 비어 있는 지점이다. 3주차에 이 문서만 보고 서버를 다시 만들어서 검증한다.

명령 앞의 `[내 PC]` / `[서버]` 는 **어디서 실행하는지**다. 프롬프트로 구분한다.

```
PS C:\Users\harry>        ← 내 PC
ubuntu@ip-172-31-...:~$   ← 서버
```

---

## 큰 그림

```
1. 서버를 빌린다        → AWS EC2
2. 서버에 접속한다      → SSH + 키 페어
3. 필요한 걸 깐다       → Docker, nginx
4. 코드를 올리고 연결한다 → git clone(설정) + scp(빌드 결과물)
```

**설정 파일은 git으로, 빌드 결과물은 scp로 간다.** `.gitignore`에 `*.jar`과 `dist/`가 있어서 빌드 결과물은 커밋되지 않는다.

---

## 1. 서버 빌리기 (AWS EC2)

| 설정 | 값 | 왜 |
| --- | --- | --- |
| 리전 | 아시아 태평양(서울) `ap-northeast-2` | |
| AMI | Ubuntu Server 24.04 LTS (x86) | |
| 인스턴스 유형 | t3.micro | |
| 스토리지 | 20GiB gp3 | |
| 퍼블릭 IP | 자동 할당 활성화 | |
| 보안 그룹 — SSH(22) | 소스: **내 IP** | |
| 보안 그룹 — HTTP(80) | 소스: 0.0.0.0/0 | |
| 보안 그룹 — HTTPS(443) | 소스: 0.0.0.0/0 | |
| 키 페어 | 새로 생성 → `.pem` 다운로드 → `C:\Users\harry\.ssh\` | |

**함정 세 개**

- 인스턴스를 만들기 전에 **우상단 리전**을 확인한다 → 안 하면?
- `.pem` 다운로드 창은 **한 번만** 뜬다 → 놓치면?
- 키 페어는 **리전별로 따로**다 → 같은 이름으로 만들면 무슨 일이?

---

## 2. 접속

```powershell
# [내 PC]
ssh -i "$env:USERPROFILE\.ssh\wms-seoul-key.pem" ubuntu@<서버IP>
```

- 사용자 이름이 `ubuntu`인 이유 →
- 권한 에러(`UNPROTECTED PRIVATE KEY FILE`)가 나는 이유 →

```powershell
# [내 PC] 권한 에러가 났을 때
icacls "$env:USERPROFILE\.ssh\wms-seoul-key.pem" /inheritance:r
icacls "$env:USERPROFILE\.ssh\wms-seoul-key.pem" /grant:r "$($env:USERNAME):R"
```

---

## 3. 서버 기본 세팅

### 3-1. 시스템 업데이트

```bash
# [서버]
sudo apt update && sudo apt upgrade -y
```

왜 →

*(보라색 화면이 뜨면 Enter. Ubuntu 24.04의 정상 동작)*

### 3-2. 스왑 2GB

```bash
# [서버]
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
free -h
```

- 스왑이 뭔가 →
- 이 프로젝트에서 왜 필요한가 (힌트: 서버 RAM 1GB) →
- `chmod 600`을 하는 이유 →
- `/etc/fstab`에 줄을 추가하는 이유 →

### 3-3. Docker 설치

```bash
# [서버]
curl -fsSL https://get.docker.com | sudo sh
sudo usermod -aG docker $USER
exit
```

- `-aG`에서 `-a`가 빠지면 무슨 일이 →
- `$USER`가 뭔가 →
- 왜 `exit` 후 재접속해야 하나 →

```bash
# [서버] 재접속 후 확인
docker --version
docker compose version
docker run --rm hello-world
```

---

## 4. DB 올리기

### 4-1. 설정 파일 받기

```bash
# [서버]
cd ~
git clone https://github.com/SeungMinShin01/WMS-Web.git
cd WMS-Web/deploy
ls -a
```

- `cd ~`를 하는 이유 →
- `.env`가 없는 게 정상인 이유 →

### 4-2. 비밀번호 파일 만들기

```bash
# [서버]
nano .env
```

내용:

```
MYSQL_ROOT_PASSWORD=<임의의 긴 문자열>
MYSQL_USER=wms
MYSQL_PASSWORD=<다른 임의의 긴 문자열>
```

저장 `Ctrl+O` → `Enter`, 나가기 `Ctrl+X`

```bash
# [서버]
chmod 600 .env
```

- `.env`를 커밋하지 않는 이유 →
- `.env.example`은 왜 커밋하나 →
- 값을 만들 때 특수문자를 피하는 이유 →

*(`openssl rand -hex 16` 으로 32자리 임의 문자열을 만들 수 있다. 해싱이 아니라 난수 생성이다.)*

### 4-3. 기동

```bash
# [서버]
docker compose up -d
docker compose ps
```

`STATUS`가 `Up ... (healthy)` 인지 확인.

```bash
# [서버] DB 접속 확인
docker exec -it wms-mysql mysql -uwms -p wms
```

**서버용 compose가 로컬용과 다른 점**

| 항목 | 로컬 | 서버 | 왜 다른가 |
| --- | --- | --- | --- |
| `restart` | 없음 | `always` | |
| 비밀번호 | 파일에 직접 | `.env` | |
| 포트 | `3307:3306` | `127.0.0.1:3306:3306` | |
| 버퍼 풀 | 512MB | 128MB | |

---

## 5. nginx

### 5-1. 설치

```bash
# [서버]
sudo apt install -y nginx
sudo systemctl status nginx
```

브라우저에서 `http://<서버IP>` → 기본 페이지 확인.

안 뜨면 볼 것 두 가지 →

### 5-2. 설정

*(작성 예정)*

- nginx가 하는 두 가지 일 →
- `try_files $uri $uri/ /index.html;` 이 필요한 이유 →
- `location /api/`가 `location /`보다 우선하는 이유 →
- `proxy_set_header` 네 줄이 없으면 생기는 문제 →

---

## 6. 백엔드 올리기

*(작성 예정)*

- 로컬에서 JAR 빌드
- `scp`로 서버에 전송
- systemd 서비스로 등록 (재부팅 시 자동 시작)

---

## 7. 프론트 올리기

*(작성 예정)*

- 로컬에서 `npm run build`
- `dist/`를 `scp`로 전송 → `/var/www/wms-web`

---

## 8. 도메인과 HTTPS

*(작성 예정)*

- DuckDNS 또는 도메인 구매
- certbot으로 Let's Encrypt 인증서 발급

---

## 검증

3주차에 이렇게 확인한다.

1. 기존 인스턴스 종료
2. **이 문서만 보고** 처음부터 재구축
3. 막힌 지점을 이 문서에 반영

통과하면 배포 절차를 이해했다고 볼 수 있다. 이 기록 자체가 README에 쓸 재료가 된다.

## 관련 노트

[[WMS 프로젝트 MOC]]
