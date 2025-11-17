# 🚀 GovPlan_AI - 빠른 시작 가이드

## 📋 목차

1. [사전 요구사항](#사전-요구사항)
2. [설치](#설치)
3. [실행](#실행)
4. [테스트](#테스트)
5. [문제 해결](#문제-해결)

---

## 사전 요구사항

### 필수 소프트웨어

- **Docker** 및 **Docker Compose** (권장)
- 또는 로컬 환경:
  - Python 3.11+
  - PostgreSQL 15+
  - Redis 7+

### 확인

```bash
# Docker 설치 확인
docker --version
docker-compose --version

# 또는 로컬 환경
python3 --version
psql --version
redis-cli --version
```

---

## 설치

### Option 1: Docker로 실행 (권장)

```bash
# 1. 저장소 클론
git clone https://github.com/ssdavo34/GovPlan_Ai.git
cd GovPlan_Ai

# 2. 환경 변수 설정
cp .env.example .env
# .env 파일을 열어서 필요한 값 설정

# 3. Docker Compose로 실행
make up
# 또는
docker-compose up -d

# 4. 데이터베이스 초기화
make db-init
```

### Option 2: 로컬 환경에서 실행

```bash
# 1. 저장소 클론
git clone https://github.com/ssdavo34/GovPlan_Ai.git
cd GovPlan_Ai

# 2. 가상환경 생성 및 활성화
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. 패키지 설치
pip install -r requirements.txt

# 4. 환경 변수 설정
cp .env.example .env
# .env 파일 수정

# 5. PostgreSQL 데이터베이스 생성
createdb govplan_ai

# 6. 마이그레이션 실행
psql -U postgres -d govplan_ai -f backend/migrations/001_create_users_table.sql

# 7. Redis 시작
redis-server

# 8. Celery Worker 시작 (별도 터미널)
celery -A backend.celery_app worker --loglevel=info

# 9. Celery Beat 시작 (별도 터미널)
celery -A backend.celery_app beat --loglevel=info

# 10. FastAPI 서버 시작
python -m uvicorn backend.app:app --reload
```

---

## 실행

### 서비스 접속

실행 후 다음 URL로 접속할 수 있습니다:

| 서비스 | URL | 설명 |
|--------|-----|------|
| 🎨 **대시보드** | http://localhost:8000 | 메인 웹 대시보드 |
| 📖 **API 문서** | http://localhost:8000/docs | Swagger UI |
| 📊 **Celery 모니터링** | http://localhost:5555 | Flower |
| 🗄️ **DB 관리** | http://localhost:5050 | pgAdmin (Docker) |

### 기본 계정

#### 관리자 계정
- **이메일**: `admin@govplan.ai`
- **비밀번호**: `admin123`

#### 테스트 계정
- **이메일**: `test@govplan.ai`
- **비밀번호**: `testuser123`

⚠️ **프로덕션 환경에서는 반드시 비밀번호를 변경하세요!**

---

## 테스트

### 1. 웹 대시보드 접속

```bash
# 브라우저에서 http://localhost:8000 열기
# 로그인: admin@govplan.ai / admin123
```

### 2. API 테스트 (cURL)

```bash
# 로그인
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin@govplan.ai&password=admin123"

# 응답에서 access_token 복사 후 사용
export TOKEN="your_access_token_here"

# 현재 사용자 정보
curl -X GET "http://localhost:8000/api/v1/auth/me" \
  -H "Authorization: Bearer $TOKEN"

# 공고 목록 조회
curl -X GET "http://localhost:8000/api/v1/projects?limit=10" \
  -H "Authorization: Bearer $TOKEN"
```

### 3. Python으로 테스트

```python
import requests

API_URL = "http://localhost:8000/api/v1"

# 로그인
response = requests.post(
    f"{API_URL}/auth/login",
    data={
        "username": "admin@govplan.ai",
        "password": "admin123"
    }
)
tokens = response.json()
token = tokens["access_token"]

# 인증 헤더
headers = {"Authorization": f"Bearer {token}"}

# 현재 사용자 정보
user = requests.get(f"{API_URL}/auth/me", headers=headers).json()
print(f"로그인 사용자: {user['email']}")

# 공고 목록
projects = requests.get(f"{API_URL}/projects", headers=headers).json()
print(f"공고 수: {len(projects.get('items', []))}")
```

### 4. 크롤링 테스트

```bash
# Docker 환경
make crawl

# 로컬 환경
celery -A backend.celery_app call backend.tasks.crawler_tasks.crawl_all_sites
```

---

## 문제 해결

### Docker 관련

#### 포트 충돌
```bash
# 이미 사용 중인 포트 확인
sudo lsof -i :8000
sudo lsof -i :5432

# docker-compose.yml에서 포트 변경
```

#### 컨테이너 재시작
```bash
make down
make up

# 또는
docker-compose down
docker-compose up -d
```

#### 로그 확인
```bash
make logs

# 특정 서비스 로그
docker-compose logs -f api
docker-compose logs -f celery_worker
```

### 데이터베이스 관련

#### 연결 실패
```bash
# PostgreSQL 상태 확인
docker-compose ps postgres

# 수동 연결 테스트
docker-compose exec postgres psql -U postgres -d govplan_ai
```

#### 마이그레이션 재실행
```bash
docker-compose exec postgres psql -U postgres -d govplan_ai \
  -f /app/backend/migrations/001_create_users_table.sql
```

### API 오류

#### 401 Unauthorized
- 토큰이 만료되었거나 유효하지 않음
- 리프레시 토큰으로 갱신하거나 재로그인

#### 403 Forbidden
- 권한 부족
- 슈퍼유저 권한이 필요한 엔드포인트인지 확인

#### 500 Internal Server Error
- 서버 로그 확인: `make logs`
- 데이터베이스 연결 상태 확인
- 환경 변수 설정 확인

---

## 유용한 명령어

### Docker

```bash
make up          # 모든 서비스 시작
make down        # 모든 서비스 중지
make logs        # 로그 확인
make restart     # 재시작
make ps          # 실행 중인 컨테이너 확인
```

### 데이터베이스

```bash
make db-shell    # PostgreSQL 셸 접속
make db-init     # 데이터베이스 초기화
```

### 크롤링

```bash
make crawl       # 모든 사이트 크롤링
```

### 개발

```bash
make dev         # 개발 모드로 실행 (hot reload)
make test        # 테스트 실행 (구현 필요)
```

---

## 더 자세한 정보

- 📖 [메인 문서](README.md)
- 🐳 [Docker 가이드](README.Docker.md)
- 🔐 [인증 가이드](README.Auth.md)
- 🌐 [API 문서](http://localhost:8000/docs) (서버 실행 후)

---

## 지원

문제가 발생하면:

1. [GitHub Issues](https://github.com/ssdavo34/GovPlan_Ai/issues)에 보고
2. 로그 파일 첨부
3. 환경 정보 제공 (OS, Docker 버전 등)

---

**즐거운 개발 되세요!** 🚀
