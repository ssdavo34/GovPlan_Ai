# GovPlan_AI

<div align="center">

**정부지원사업 공고 자동 수집 및 AI 기반 사업계획서 자동 작성 시스템**

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

</div>

---

## 프로젝트 소개

GovPlan_AI는 정부지원사업 정보를 자동으로 수집하고, 기업 특성에 맞는 사업을 추천하며, AI를 활용하여 사업계획서를 자동으로 생성하는 통합 플랫폼입니다.

### 핵심 기능

#### 1. 자동 크롤링
- K-Startup, 기업마당, 중소벤처24, 소상공인24 등 주요 정부 포털에서 공고 자동 수집
- 일일 자동 크롤링 및 신규 공고 알림
- 공고 상세 정보 자동 파싱 (자격요건, 지원금액, 제출서류 등)

#### 2. 기업 맞춤 추천
- 기업 정보 기반 매칭 알고리즘
- 업종, 지역, 기업 규모, 기술 분야 등 다차원 필터링
- 매칭 점수 기반 우선순위 추천

#### 3. AI 사업계획서 생성
- Claude AI 기반 사업계획서 자동 작성
- 공고별 맞춤형 템플릿 적용
- PDF, DOCX, Markdown 등 다양한 포맷 지원

#### 4. 알림 및 자동화
- 신규 공고 실시간 알림 (이메일, Slack)
- 마감 임박 알림 (D-7, D-3, D-1)
- 사업계획서 생성 완료 알림

---

## 시작하기

### 사전 요구사항

- Python 3.11 이상
- Docker & Docker Compose (선택사항)
- PostgreSQL 15+ (Docker 사용 시 불필요)
- Redis (Docker 사용 시 불필요)

### 설치 방법

#### Option 1: Docker Compose (권장)

```bash
# 저장소 클론
git clone https://github.com/yourusername/GovPlan_AI.git
cd GovPlan_AI

# 환경 변수 설정
cp .env.example .env
# .env 파일을 편집하여 API 키 등 설정

# Docker Compose로 실행
docker-compose up -d

# 데이터베이스 초기화
docker-compose exec api python scripts/init_db.py

# API 서버 확인
curl http://localhost:8000/health
```

#### Option 2: 로컬 설치

```bash
# 저장소 클론
git clone https://github.com/yourusername/GovPlan_AI.git
cd GovPlan_AI

# 가상환경 생성 및 활성화
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 패키지 설치
pip install -r requirements.txt

# 환경 변수 설정
cp .env.example .env
# .env 파일 편집

# PostgreSQL 및 Redis 실행 (별도 설치 필요)

# 데이터베이스 마이그레이션
alembic upgrade head

# API 서버 실행
uvicorn src.api.main:app --reload

# 크롤러 실행 (별도 터미널)
python scripts/run_crawler.py
```

---

## 프로젝트 구조

```
GovPlan_AI/
├── src/                       # 소스 코드
│   ├── crawler/              # 크롤링 모듈
│   │   ├── scrapers/         # 사이트별 스크래퍼
│   │   └── scheduler.py      # 크롤링 스케줄러
│   ├── database/             # 데이터베이스
│   │   ├── models.py         # SQLAlchemy 모델
│   │   └── schemas.py        # Pydantic 스키마
│   ├── ai/                   # AI 모듈
│   │   ├── llm_client.py     # LLM API 클라이언트
│   │   └── proposal_generator.py
│   ├── matching/             # 매칭 엔진
│   ├── api/                  # FastAPI
│   │   ├── main.py
│   │   └── routes/
│   ├── document/             # 문서 생성
│   └── notification/         # 알림 시스템
├── config/                    # 설정 파일
├── tests/                     # 테스트
├── scripts/                   # 실행 스크립트
└── docker/                    # Docker 설정
```

자세한 구조는 [PROJECT_PLAN.md](PROJECT_PLAN.md)를 참고하세요.

---

## 사용 방법

### 1. 크롤러 실행

```bash
# 수동 크롤링 실행
python scripts/run_crawler.py

# 특정 사이트만 크롤링
python scripts/run_crawler.py --site k-startup

# 스케줄러 실행 (백그라운드)
celery -A src.crawler.scheduler beat --loglevel=info
```

### 2. API 사용

#### 공고 조회
```bash
# 전체 공고 조회
curl http://localhost:8000/api/v1/grants

# 필터링 조회
curl "http://localhost:8000/api/v1/grants?category=R%26D&region=서울"

# 상세 조회
curl http://localhost:8000/api/v1/grants/{grant_id}
```

#### 기업 정보 등록
```bash
curl -X POST http://localhost:8000/api/v1/companies \
  -H "Content-Type: application/json" \
  -d '{
    "company_name": "테크스타트업",
    "industry_code": "J",
    "company_type": "스타트업",
    "region": "서울",
    "tech_fields": ["AI", "빅데이터"]
  }'
```

#### 사업계획서 생성
```bash
curl -X POST http://localhost:8000/api/v1/proposals/generate \
  -H "Content-Type: application/json" \
  -d '{
    "company_id": 1,
    "grant_id": 123,
    "format": "pdf"
  }'
```

#### 맞춤 추천
```bash
curl http://localhost:8000/api/v1/recommendations/{company_id}
```

### 3. API 문서

FastAPI Swagger UI: http://localhost:8000/docs

---

## 환경 변수 설정

`.env` 파일에서 다음 항목을 설정하세요:

```env
# 필수 설정
DATABASE_URL=postgresql://user:password@localhost:5432/govplan_ai
ANTHROPIC_API_KEY=sk-ant-xxx

# 선택 설정
OPENAI_API_KEY=sk-xxx          # 대체 AI 모델 사용 시
SMTP_USER=your-email@gmail.com # 이메일 알림 사용 시
SLACK_WEBHOOK_URL=https://...  # Slack 알림 사용 시
```

---

## 개발 로드맵

### Phase 1: 기반 구축 (4주) - 진행 중
- [x] 프로젝트 셋업
- [x] 디렉토리 구조 생성
- [ ] 크롤러 구현
- [ ] 데이터베이스 스키마

### Phase 2: AI 통합 (3주)
- [ ] Claude API 연동
- [ ] 사업계획서 생성 엔진
- [ ] 매칭 알고리즘

### Phase 3: API 및 인터페이스 (3주)
- [ ] REST API 구축
- [ ] 프론트엔드 개발 (선택)

### Phase 4: 자동화 및 배포 (2주)
- [ ] 알림 시스템
- [ ] CI/CD 구축
- [ ] 프로덕션 배포

자세한 로드맵은 [PROJECT_PLAN.md](PROJECT_PLAN.md)를 참고하세요.

---

## 기술 스택

### Backend
- **언어**: Python 3.11+
- **웹 프레임워크**: FastAPI
- **크롤링**: BeautifulSoup, Selenium, Playwright
- **데이터베이스**: PostgreSQL, Redis
- **ORM**: SQLAlchemy 2.0
- **작업 큐**: Celery

### AI/ML
- **LLM**: Anthropic Claude, OpenAI GPT
- **프롬프트 관리**: LangChain
- **벡터 DB**: ChromaDB

### DevOps
- **컨테이너**: Docker, Docker Compose
- **CI/CD**: GitHub Actions
- **모니터링**: Prometheus, Grafana (예정)

---

## 테스트

```bash
# 전체 테스트 실행
pytest

# 커버리지 포함
pytest --cov=src --cov-report=html

# 특정 테스트만 실행
pytest tests/unit/test_crawler.py
```

---

## 기여하기

프로젝트에 기여하고 싶으시다면:

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다. 자세한 내용은 [LICENSE](LICENSE) 파일을 참고하세요.

---

## 문의 및 지원

- **이슈 리포트**: [GitHub Issues](https://github.com/yourusername/GovPlan_AI/issues)
- **이메일**: support@govplanai.com

---

## 참고 자료

- [프로젝트 계획서](PROJECT_PLAN.md)
- [API 명세서](docs/API_SPEC.md) (작성 예정)
- [배포 가이드](docs/DEPLOYMENT.md) (작성 예정)

---

## 크롤링 대상 사이트

- [K-Startup](https://www.k-startup.go.kr) - 중소벤처기업부
- [기업마당](https://www.bizinfo.go.kr) - 정부24 연계
- [중소벤처24](https://www.smes.go.kr) - 중소벤처기업진흥공단
- [소상공인24](https://www.sbiz.or.kr) - 소상공인시장진흥공단

---

<div align="center">

**Made with ❤️ for Korean Startups**

</div>
