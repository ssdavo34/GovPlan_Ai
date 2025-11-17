# 🚀 GovPlan_AI 배포 가이드

## 📋 배포 체크리스트

### ✅ 사전 준비

- [ ] Docker 및 Docker Compose 설치 확인
- [ ] Git 저장소 클론 완료
- [ ] 환경 변수 설정 완료 (.env)
- [ ] 필요한 API 키 준비 (Anthropic, OpenAI 등)

### ✅ 배포 단계

## 1단계: 저장소 클론 및 설정

```bash
# 저장소 클론
git clone https://github.com/ssdavo34/GovPlan_Ai.git
cd GovPlan_Ai

# 올바른 브랜치 확인
git checkout claude/start-priority-coding-01NUbak4wzbP5MHv8ackke9Q
# 또는 메인 브랜치로 머지 후
# git checkout main

# 환경 변수 파일 생성
cp .env.example .env
```

## 2단계: 환경 변수 수정

`.env` 파일을 열고 다음 항목을 **반드시** 수정하세요:

```bash
# 🔐 보안 중요!
SECRET_KEY=여기에-최소-32자-이상의-랜덤-문자열-입력

# AI API 키 (필요한 경우)
ANTHROPIC_API_KEY=your-actual-api-key
OPENAI_API_KEY=your-actual-api-key

# 이메일 설정 (알림 사용 시)
SMTP_USER=actual-email@gmail.com
SMTP_PASSWORD=actual-app-password
FROM_EMAIL=actual-email@gmail.com

# Slack 설정 (알림 사용 시)
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/실제/웹훅/URL
```

**SECRET_KEY 생성 방법:**

```bash
# Python으로 안전한 랜덤 키 생성
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

## 3단계: Docker로 실행

```bash
# 모든 서비스 시작
docker-compose up -d

# 또는 Makefile 사용
make up

# 실행 확인
docker-compose ps
```

**예상 출력:**
```
NAME                COMMAND                  SERVICE             STATUS
govplan_ai-api-1    "uvicorn backend.app…"   api                 running
govplan_ai-celery_beat-1   "celery -A backend.c…"   celery_beat         running
govplan_ai-celery_worker-1 "celery -A backend.c…"   celery_worker       running
govplan_ai-postgres-1      "docker-entrypoint.s…"   postgres            running
govplan_ai-redis-1         "docker-entrypoint.s…"   redis               running
govplan_ai-flower-1        "celery -A backend.c…"   flower              running
```

## 4단계: 데이터베이스 초기화

```bash
# 사용자 테이블 생성
docker-compose exec postgres psql -U postgres -d govplan_ai \
  -f /app/backend/migrations/001_create_users_table.sql

# 또는
make db-init
```

**성공 메시지:**
```
CREATE TABLE
CREATE INDEX
CREATE INDEX
INSERT 0 1  # 관리자 계정 생성
INSERT 0 1  # 테스트 계정 생성
```

## 5단계: 접속 테스트

### 웹 대시보드
브라우저에서 접속:
```
http://localhost:8000
```

**기본 로그인 정보:**
- 이메일: `admin@govplan.ai`
- 비밀번호: `admin123`

⚠️ **프로덕션에서는 즉시 비밀번호를 변경하세요!**

### API 문서
```
http://localhost:8000/docs
```
Swagger UI에서 모든 API 엔드포인트 확인 가능

### Celery 모니터링
```
http://localhost:5555
```
Flower 대시보드에서 백그라운드 작업 모니터링

## 6단계: 기능 테스트

### 1) 로그인 테스트

```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin@govplan.ai&password=admin123"
```

**예상 응답:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### 2) 인증된 API 호출

```bash
# 위에서 받은 토큰 사용
TOKEN="your-access-token-here"

# 현재 사용자 정보
curl -X GET "http://localhost:8000/api/v1/auth/me" \
  -H "Authorization: Bearer $TOKEN"

# 공고 목록 (예시)
curl -X GET "http://localhost:8000/api/v1/projects?limit=10" \
  -H "Authorization: Bearer $TOKEN"
```

### 3) 크롤링 테스트

```bash
# 모든 사이트 크롤링
make crawl

# 또는
docker-compose exec api celery -A backend.celery_app call \
  backend.tasks.crawler_tasks.crawl_all_sites
```

## 📊 서비스 모니터링

### 로그 확인

```bash
# 전체 로그
make logs

# 특정 서비스 로그
docker-compose logs -f api
docker-compose logs -f celery_worker
docker-compose logs -f postgres

# 최근 100줄
docker-compose logs --tail=100 api
```

### 컨테이너 상태

```bash
# 실행 중인 컨테이너
docker-compose ps

# 리소스 사용량
docker stats

# 특정 컨테이너 상세 정보
docker-compose exec api ps aux
```

### 데이터베이스 확인

```bash
# PostgreSQL 접속
make db-shell

# 또는
docker-compose exec postgres psql -U postgres -d govplan_ai

# SQL 실행 예시
SELECT COUNT(*) FROM users;
SELECT * FROM users LIMIT 5;
```

## 🔧 문제 해결

### 포트 충돌

```bash
# 사용 중인 포트 확인
sudo lsof -i :8000
sudo lsof -i :5432

# docker-compose.yml에서 포트 변경
# ports:
#   - "8001:8000"  # 호스트:컨테이너
```

### 컨테이너 재시작

```bash
# 전체 재시작
make restart

# 또는
docker-compose restart

# 특정 서비스만 재시작
docker-compose restart api
```

### 완전 초기화

```bash
# 모든 컨테이너와 볼륨 삭제
docker-compose down -v

# 다시 시작
docker-compose up -d
```

### 데이터베이스 연결 오류

```bash
# PostgreSQL 상태 확인
docker-compose exec postgres pg_isready

# 로그 확인
docker-compose logs postgres

# 컨테이너 재시작
docker-compose restart postgres
```

## 🔐 프로덕션 배포 시 보안 체크리스트

- [ ] `.env` 파일에서 `SECRET_KEY` 변경
- [ ] `.env` 파일에서 `DB_PASSWORD` 변경
- [ ] 기본 관리자 비밀번호 변경 (`admin123` → 강력한 비밀번호)
- [ ] `DEBUG=False` 설정
- [ ] HTTPS 적용 (Nginx 리버스 프록시 권장)
- [ ] CORS 설정 확인 및 제한
- [ ] 방화벽 설정 (필요한 포트만 개방)
- [ ] 정기 백업 설정
- [ ] 로그 모니터링 설정
- [ ] Rate limiting 설정 (선택사항)

## 🌐 프로덕션 환경 설정

### Nginx 리버스 프록시 (권장)

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### SSL/TLS 인증서 (Let's Encrypt)

```bash
# Certbot 설치
sudo apt install certbot python3-certbot-nginx

# 인증서 발급
sudo certbot --nginx -d your-domain.com

# 자동 갱신 테스트
sudo certbot renew --dry-run
```

### 프로덕션 모드 실행

```bash
# docker-compose.prod.yml 사용
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# 또는
make prod-up
```

## 📦 백업 및 복구

### 데이터베이스 백업

```bash
# 백업 생성
docker-compose exec postgres pg_dump -U postgres govplan_ai > backup_$(date +%Y%m%d).sql

# 백업 복구
docker-compose exec -T postgres psql -U postgres govplan_ai < backup_20240101.sql
```

### 전체 데이터 백업

```bash
# Docker 볼륨 백업
docker run --rm \
  -v govplan_ai_postgres_data:/data \
  -v $(pwd):/backup \
  alpine tar czf /backup/postgres_data_backup.tar.gz /data
```

## 📈 성능 최적화

### 프로덕션 설정

1. **Uvicorn Workers 증가** (docker-compose.prod.yml)
   ```yaml
   command: uvicorn backend.app:app --host 0.0.0.0 --port 8000 --workers 4
   ```

2. **PostgreSQL 최적화**
   ```sql
   -- 인덱스 추가
   CREATE INDEX idx_projects_status ON projects(status);
   CREATE INDEX idx_projects_deadline ON projects(application_end_date);
   ```

3. **Redis 캐싱 활용**
   - API 응답 캐싱
   - 세션 저장소로 사용

## 🆘 긴급 상황 대응

### 서비스 다운

```bash
# 1. 로그 확인
docker-compose logs --tail=100

# 2. 컨테이너 상태 확인
docker-compose ps

# 3. 재시작
docker-compose restart

# 4. 실패 시 완전 재시작
docker-compose down && docker-compose up -d
```

### 데이터베이스 복구

```bash
# 최근 백업에서 복구
docker-compose exec -T postgres psql -U postgres govplan_ai < latest_backup.sql

# 데이터베이스 재구축
docker-compose down -v
docker-compose up -d postgres
# 마이그레이션 재실행
```

## 📞 지원

문제 발생 시:

1. **로그 확인**: `make logs`
2. **이슈 등록**: [GitHub Issues](https://github.com/ssdavo34/GovPlan_Ai/issues)
3. **문서 참조**:
   - [README.md](README.md)
   - [README.Docker.md](README.Docker.md)
   - [README.Auth.md](README.Auth.md)
   - [QUICKSTART.md](QUICKSTART.md)

---

**배포 성공을 기원합니다!** 🚀
