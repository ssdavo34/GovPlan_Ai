# GovPlan_AI

정부지원사업(Government Support)과 사업계획서 자동 생성(Plan)을 위한 AI 기반 자동화 플랫폼

## 📋 프로젝트 개요

GovPlan_AI는 정부지원사업 정보를 자동으로 수집하고, 기업 정보를 기반으로 맞춤형 지원사업을 추천하며, AI를 활용하여 사업계획서를 자동으로 생성하는 통합 플랫폼입니다.

### 주요 기능

1. **정부지원사업 자동 크롤링**
   - 기업마당, K-Startup, 소상공인24 등 주요 정부 포털 자동 크롤링
   - 실시간 공고 정보 수집 및 데이터베이스 저장
   - 정기적 업데이트 스케줄링

2. **맞춤형 지원사업 추천**
   - 기업 정보 (업종, 지역, 자금 규모 등) 기반 매칭
   - AI 알고리즘을 통한 점수 산정 (최대 100점)
   - 추천 등급별 분류 (강력추천, 추천, 검토권장)

3. **AI 사업계획서 자동 생성**
   - Claude, GPT 등 최신 AI 모델 활용
   - 사업별 맞춤 템플릿 제공
   - PDF, DOCX, HWP 형식 지원

4. **사용자 친화적 대시보드**
   - 실시간 공고 현황 확인
   - 북마크 및 지원 이력 관리
   - 문서 편집 및 다운로드

## 🏗️ 프로젝트 구조

```
GovPlan_Ai/
├── backend/           # Python 백엔드 (FastAPI)
│   ├── api/          # REST API 엔드포인트
│   ├── core/         # 핵심 설정
│   ├── crawlers/     # 크롤러 모듈
│   ├── models/       # 데이터베이스 모델
│   ├── services/     # 비즈니스 로직
│   └── utils/        # 유틸리티
├── frontend/         # React 프론트엔드
├── database/         # DB 마이그레이션 및 스키마
├── scripts/          # 유틸리티 스크립트
├── templates/        # 사업계획서 템플릿
└── docs/            # 문서
```

자세한 구조는 [프로젝트 구조 문서](docs/PROJECT_STRUCTURE.md)를 참고하세요.

## 🚀 시작하기

### 필수 요구사항

- Python 3.10 이상
- PostgreSQL 14 이상
- Redis 6 이상
- Node.js 18 이상 (프론트엔드)

### 설치

1. **저장소 클론**
   ```bash
   git clone https://github.com/ssdavo34/GovPlan_Ai.git
   cd GovPlan_Ai
   ```

2. **백엔드 설정**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **환경 변수 설정**
   ```bash
   cp .env.example .env
   # .env 파일을 열어 필요한 값 입력 (DB, API 키 등)
   ```

4. **데이터베이스 초기화**
   ```bash
   # PostgreSQL에 데이터베이스 생성
   createdb govplan_ai

   # 스키마 적용
   psql -d govplan_ai -f database/migrations/001_initial_schema.sql
   ```

5. **서버 실행**
   ```bash
   # 백엔드 서버
   cd backend
   uvicorn app:app --reload --host 0.0.0.0 --port 8000

   # Celery Worker (별도 터미널)
   celery -A backend.celery_app worker --loglevel=info

   # Celery Beat (크롤링 스케줄러, 별도 터미널)
   celery -A backend.celery_app beat --loglevel=info
   ```

6. **프론트엔드 실행** (선택사항)
   ```bash
   cd frontend
   npm install
   npm start
   ```

## 📖 사용 방법

### 1. 크롤링 실행

```python
from backend.services import CrawlerService

crawler_service = CrawlerService()

# 특정 사이트 크롤링
result = crawler_service.crawl_site('기업마당')

# 모든 사이트 크롤링
results = crawler_service.crawl_all_sites()
```

### 2. 기업-사업 매칭

```python
from backend.services import MatchingService

matching_service = MatchingService()

company = {
    'industry_code': 'C26',  # 전자부품 제조업
    'region': '서울',
    'certifications': ['벤처인증'],
    'funding_needs': '5000만원'
}

# 프로젝트 리스트에서 매칭
matched_projects = matching_service.filter_projects(
    company=company,
    projects=all_projects,
    min_score=40.0,
    max_results=10
)
```

### 3. API 사용 (REST API)

```bash
# 프로젝트 목록 조회
curl http://localhost:8000/api/projects

# 기업 정보 등록
curl -X POST http://localhost:8000/api/companies \
  -H "Content-Type: application/json" \
  -d '{"company_name": "테크스타트", "industry_code": "C26"}'

# 매칭 실행
curl http://localhost:8000/api/matching?company_id=1
```

## 🔧 설정

### 크롤링 대상 사이트

현재 지원하는 사이트:
- ✅ 기업마당 (bizinfo.go.kr)
- ✅ K-Startup (k-startup.go.kr)
- 🚧 소상공인24 (개발 예정)
- 🚧 중소벤처24 (개발 예정)

### 매칭 알고리즘

매칭 점수는 다음 기준으로 계산됩니다:
- **업종 일치도**: 40점
- **신청 기간 적합성**: 20점
- **자금 규모 적합성**: 20점
- **인증/자격 요건**: 10점
- **지역 적합성**: 10점

자세한 내용은 [요구사항 문서](docs/REQUIREMENTS.md)를 참고하세요.

## 📚 문서

- [요구사항 명세서](docs/REQUIREMENTS.md)
- [프로젝트 구조](docs/PROJECT_STRUCTURE.md)
- [API 문서](docs/API.md) (작성 예정)
- [배포 가이드](docs/DEPLOYMENT.md) (작성 예정)

## 🛠️ 기술 스택

### Backend
- **Framework**: FastAPI
- **Database**: PostgreSQL, Redis
- **ORM**: SQLAlchemy
- **Task Queue**: Celery
- **Crawling**: Selenium, BeautifulSoup4, Scrapy

### Frontend
- **Framework**: React.js
- **UI**: TailwindCSS
- **State Management**: Redux

### AI/ML
- **LLM**: OpenAI GPT-4, Anthropic Claude
- **Framework**: LangChain

## 🤝 기여하기

프로젝트에 기여하고 싶으시다면:

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다.

## 📧 연락처

프로젝트 관리자: [@ssdavo34](https://github.com/ssdavo34)

프로젝트 링크: [https://github.com/ssdavo34/GovPlan_Ai](https://github.com/ssdavo34/GovPlan_Ai)

## 🙏 감사의 말

- 정부지원사업 정보를 제공해주시는 모든 정부기관
- 오픈소스 커뮤니티
- 프로젝트에 기여해주신 모든 분들

---

**Note**: 이 프로젝트는 현재 개발 중이며, 일부 기능은 아직 구현되지 않았을 수 있습니다.
