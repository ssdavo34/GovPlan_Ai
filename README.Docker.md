# Docker 사용 가이드

## 🐳 빠른 시작

### 1. 환경 변수 설정

```bash
cp .env.example .env
# .env 파일을 편집하여 필요한 값 설정
```

### 2. Docker Compose로 전체 스택 실행

```bash
# 모든 서비스 빌드 및 시작
docker-compose up -d

# 또는 Makefile 사용
make up
```

### 3. 서비스 확인

서비스가 시작되면 다음 URL에서 접속 가능합니다:

- **API 서버**: http://localhost:8000
- **API 문서 (Swagger)**: http://localhost:8000/docs
- **Flower (Celery 모니터링)**: http://localhost:5555
- **pgAdmin (선택사항)**: http://localhost:5050

## 📋 사용 가능한 명령어

### Makefile 명령어 (권장)

```bash
# 도움말 보기
make help

# 개발 환경
make build      # Docker 이미지 빌드
make up         # 서비스 시작
make down       # 서비스 중지
make restart    # 서비스 재시작
make logs       # 전체 로그 보기
make logs-api   # API 로그만 보기
make shell      # API 컨테이너 쉘 접속

# 데이터베이스
make db-init    # 데이터베이스 초기화
make db-shell   # PostgreSQL 쉘 접속

# 크롤러
make crawl              # 전체 사이트 크롤링
make crawl-bizinfo      # 기업마당만 크롤링
make crawl-kstartup     # K-Startup만 크롤링

# 프로덕션
make prod-build  # 프로덕션 이미지 빌드
make prod-up     # 프로덕션 환경 시작
make prod-down   # 프로덕션 환경 중지
```

### Docker Compose 직접 사용

```bash
# 서비스 시작
docker-compose up -d

# 특정 서비스만 시작
docker-compose up -d api postgres redis

# 로그 확인
docker-compose logs -f api
docker-compose logs -f celery_worker

# 서비스 재시작
docker-compose restart api

# 컨테이너 내부 접속
docker-compose exec api bash
docker-compose exec postgres psql -U govplan -d govplan_ai

# 서비스 중지
docker-compose down

# 볼륨까지 삭제
docker-compose down -v
```

## 🏗️ 서비스 구성

### 1. PostgreSQL (postgres)
- **포트**: 5432
- **사용자**: govplan (기본값)
- **데이터베이스**: govplan_ai
- **볼륨**: postgres_data

### 2. Redis (redis)
- **포트**: 6379
- **용도**: Celery 메시지 브로커 및 캐싱
- **볼륨**: redis_data

### 3. API (api)
- **포트**: 8000
- **프레임워크**: FastAPI
- **자동 재로드**: 개발 모드에서 활성화

### 4. Celery Worker (celery_worker)
- **용도**: 비동기 작업 처리 (크롤링, 매칭 등)
- **동시 실행**: 2 (개발), 4 (프로덕션)

### 5. Celery Beat (celery_beat)
- **용도**: 주기적 작업 스케줄링
- **스케줄**:
  - 매일 오전 9시: 전체 사이트 크롤링
  - 매주 월요일 10시: 매칭 점수 재계산
  - 매일 자정: 만료 공고 상태 업데이트

### 6. Flower (flower)
- **포트**: 5555
- **용도**: Celery 작업 모니터링
- **URL**: http://localhost:5555

### 7. pgAdmin (pgadmin) - 선택사항
- **포트**: 5050
- **용도**: 데이터베이스 관리 UI
- **실행**: `make pgadmin` 또는 `docker-compose --profile tools up -d pgadmin`

## 🔧 환경 변수

`.env` 파일에서 설정 가능한 주요 환경 변수:

```env
# 데이터베이스
DB_HOST=postgres
DB_PORT=5432
DB_NAME=govplan_ai
DB_USER=govplan
DB_PASSWORD=govplan123

# Redis
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_DB=0

# AI API 키
ANTHROPIC_API_KEY=sk-ant-your-key-here
OPENAI_API_KEY=sk-your-key-here

# 애플리케이션
DEBUG=True
SECRET_KEY=your-secret-key-here

# API 포트
API_PORT=8000
```

## 📊 데이터베이스 초기화

### 자동 초기화

컨테이너 시작 시 `database/migrations/` 폴더의 SQL 파일이 자동으로 실행됩니다.

### 수동 초기화

```bash
# Makefile 사용
make db-init

# 또는 직접 실행
docker-compose exec api python scripts/init_db.py
```

## 🐛 디버깅

### 로그 확인

```bash
# 전체 로그
docker-compose logs -f

# 특정 서비스 로그
docker-compose logs -f api
docker-compose logs -f celery_worker
docker-compose logs -f celery_beat

# 최근 100줄만 보기
docker-compose logs --tail=100 api
```

### 컨테이너 내부 접속

```bash
# API 컨테이너
docker-compose exec api bash

# PostgreSQL
docker-compose exec postgres psql -U govplan -d govplan_ai

# Redis
docker-compose exec redis redis-cli
```

### 서비스 상태 확인

```bash
# 모든 서비스 상태
docker-compose ps

# 헬스 체크
make health
curl http://localhost:8000/health
```

## 🚀 프로덕션 배포

### 1. 프로덕션 이미지 빌드

```bash
make prod-build
```

### 2. 환경 변수 설정

`.env` 파일에서 프로덕션 값 설정:

```env
DEBUG=False
SECRET_KEY=<강력한-시크릿-키>
DB_PASSWORD=<강력한-패스워드>
REDIS_PASSWORD=<강력한-패스워드>
```

### 3. 프로덕션 모드로 실행

```bash
make prod-up

# 또는
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

### 4. 프로덕션 특징

- **멀티 워커**: API 서버 4개 워커
- **보안**: Non-root 사용자로 실행
- **최적화**: 프로덕션 빌드 (개발 도구 제외)
- **재시작 정책**: 자동 재시작 활성화
- **헬스 체크**: 자동 헬스 체크 포함

## 📦 볼륨 관리

### 데이터 백업

```bash
# PostgreSQL 백업
docker-compose exec postgres pg_dump -U govplan govplan_ai > backup.sql

# 볼륨 백업
docker run --rm -v govplan_postgres_data:/data -v $(pwd):/backup \
  alpine tar czf /backup/postgres_backup.tar.gz /data
```

### 데이터 복원

```bash
# PostgreSQL 복원
docker-compose exec -T postgres psql -U govplan govplan_ai < backup.sql
```

### 볼륨 정리

```bash
# 모든 컨테이너 및 볼륨 삭제
make clean

# 또는
docker-compose down -v
```

## 🔍 문제 해결

### 포트 충돌

이미 사용 중인 포트가 있다면 `.env` 파일에서 변경:

```env
API_PORT=8001
DB_PORT=5433
REDIS_PORT=6380
```

### 메모리 부족

Docker Desktop 설정에서 메모리 할당 증가 (최소 4GB 권장)

### 데이터베이스 연결 실패

```bash
# PostgreSQL 준비 상태 확인
docker-compose exec postgres pg_isready -U govplan

# 연결 테스트
docker-compose exec api python -c "from backend.core.database import db_manager; import asyncio; asyncio.run(db_manager.connect())"
```

### Celery 작업 실행 안됨

```bash
# Redis 연결 확인
docker-compose exec redis redis-cli ping

# Celery 워커 로그 확인
docker-compose logs -f celery_worker
```

## 📝 개발 팁

### 코드 변경 시 자동 재로드

개발 모드에서는 코드 변경 시 자동으로 재로드됩니다:
- API: uvicorn --reload
- Celery Worker: 수동 재시작 필요

```bash
# Celery 워커 재시작
docker-compose restart celery_worker
```

### 테스트 실행

```bash
make test

# 또는
docker-compose exec api pytest tests/ -v
```

### Python 패키지 추가

```bash
# requirements.txt에 패키지 추가 후
docker-compose build api celery_worker celery_beat

# 재시작
docker-compose up -d
```

## 🌐 네트워크

모든 서비스는 `govplan_network` 브리지 네트워크에서 실행됩니다.

서비스 간 통신:
- API → PostgreSQL: `postgres:5432`
- API → Redis: `redis:6379`
- Celery → Redis: `redis:6379`

## 📚 추가 자료

- [Docker 공식 문서](https://docs.docker.com/)
- [Docker Compose 문서](https://docs.docker.com/compose/)
- [FastAPI Docker 가이드](https://fastapi.tiangolo.com/deployment/docker/)
