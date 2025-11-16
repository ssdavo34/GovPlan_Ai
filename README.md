# GovPlan_AI

정부지원사업(Government Support)과 사업계획서 자동 생성(Plan)을 위한 AI 기반 자동화 플랫폼

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109-green.svg)](https://fastapi.tiangolo.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-14+-blue.svg)](https://www.postgresql.org/)

## 📋 프로젝트 개요

GovPlan_AI는 정부지원사업 정보를 자동으로 수집하고, 기업 정보를 기반으로 맞춤형 지원사업을 추천하며, **AI를 활용하여 사업계획서를 자동으로 생성**하는 통합 플랫폼입니다.

### 🎯 핵심 가치

- ⏰ **시간 절감**: 수동 검색 및 작성 시간 90% 단축
- 🎯 **정확한 매칭**: 기업 특성에 맞는 사업 자동 추천
- 🤖 **AI 자동화**: 사업계획서 초안 자동 생성
- 📊 **데이터 기반**: 과거 공고 데이터 분석 및 트렌드 파악

### 주요 기능

#### 1. 정부지원사업 자동 크롤링 ✅
- 기업마당, K-Startup, 소상공인24 등 주요 정부 포털 자동 크롤링
- 실시간 공고 정보 수집 및 데이터베이스 저장
- 스케줄링을 통한 자동 업데이트

#### 2. 맞춤형 지원사업 추천 ✅
- 기업 정보 (업종, 지역, 자금 규모 등) 기반 매칭
- 점수 기반 알고리즘 (최대 100점)
- 추천 등급별 분류 (강력추천 80+, 추천 60+, 검토권장 40+)

#### 3. AI 사업계획서 자동 생성 ✅
- **Anthropic Claude 3.5 Sonnet** 기반 고품질 사업계획서 생성
- 사업별 맞춤 프롬프트 및 섹션별 생성
- 섹션별 재생성 및 편집 기능
- PDF, DOCX 형식 지원 (구현 예정)

#### 4. RESTful API ✅
- 공고 조회/검색/통계 API
- 기업 정보 관리 (CRUD)
- 사업계획서 생성/관리 API
- 매칭 API (구현 예정)

## 🏗️ 프로젝트 구조

```
GovPlan_Ai/
├── backend/                    # Python 백엔드 (FastAPI)
│   ├── api/                   # REST API 엔드포인트
│   │   ├── projects.py        # 공고 API
│   │   ├── companies.py       # 기업 API
│   │   └── proposals.py       # 사업계획서 API
│   ├── core/                  # 핵심 설정
│   │   ├── config.py          # 환경 설정
│   │   └── database.py        # DB 연결 관리
│   ├── crawlers/              # 크롤러 모듈
│   │   ├── base_crawler.py
│   │   ├── bizinfo_crawler.py
│   │   └── kstartup_crawler.py
│   ├── models/                # 데이터베이스 모델
│   ├── services/              # 비즈니스 로직
│   │   ├── ai/                # AI 서비스
│   │   │   └── proposal_generator.py
│   │   ├── crawler_service.py
│   │   └── matching_service.py
│   └── app.py                 # FastAPI 메인
├── scripts/                   # 유틸리티 스크립트
│   ├── init_db.py            # DB 초기화
│   └── run_crawler.py        # 크롤러 실행
├── database/                  # DB 마이그레이션
│   └── migrations/
│       └── 001_initial_schema.sql
├── config/                    # 설정 파일
├── docs/                      # 문서
│   ├── REQUIREMENTS.md
│   └── PROJECT_STRUCTURE.md
└── PROJECT_PLAN.md           # 전체 프로젝트 계획
```

## 🚀 빠른 시작

### 필수 요구사항

- Python 3.10 이상
- PostgreSQL 14 이상
- Anthropic API 키 (사업계획서 생성용)

### 설치 및 실행

#### 1. 저장소 클론

```bash
git clone https://github.com/ssdavo34/GovPlan_Ai.git
cd GovPlan_Ai
```

#### 2. 환경 변수 설정

```bash
cp .env.example .env
```

`.env` 파일 편집:

```env
# 데이터베이스
DB_HOST=localhost
DB_PORT=5432
DB_NAME=govplan_ai
DB_USER=postgres
DB_PASSWORD=your_password

# AI API
ANTHROPIC_API_KEY=sk-ant-your-api-key-here
OPENAI_API_KEY=sk-your-openai-key  # 선택사항

# 애플리케이션
DEBUG=True
SECRET_KEY=your-secret-key-change-this
```

#### 3. 백엔드 설정

```bash
# 가상 환경 생성 및 활성화
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 의존성 설치
pip install -r backend/requirements.txt
```

#### 4. 데이터베이스 초기화

```bash
# PostgreSQL 데이터베이스 생성
createdb govplan_ai

# 스키마 초기화 (테이블 자동 생성)
python scripts/init_db.py
```

출력 예시:
```
============================================================
GovPlan_AI 데이터베이스 초기화
============================================================

✓ 데이터베이스 'govplan_ai' 생성 완료
✓ 데이터베이스 연결 성공
✓ 마이그레이션 완료

생성된 테이블 목록:
  - gov_support_projects
  - companies
  - proposals
  - matching_history
  - crawling_history
```

#### 5. FastAPI 서버 실행

```bash
# 방법 1: uvicorn 직접 실행
cd backend
uvicorn app:app --reload --host 0.0.0.0 --port 8000

# 방법 2: Python 스크립트 실행
python backend/app.py
```

서버 시작 메시지:
```
============================================================
GovPlan_AI v1.0.0 시작
============================================================
✓ 데이터베이스 연결 풀 생성 완료
INFO:     Uvicorn running on http://0.0.0.0:8000
```

#### 6. API 문서 확인

브라우저에서 다음 URL로 접속:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **헬스 체크**: http://localhost:8000/health

## 📖 사용 방법

### 1. 크롤링 실행

```bash
# 모든 사이트 크롤링 (최대 5페이지)
python scripts/run_crawler.py --site all --max-pages 5

# 특정 사이트만 크롤링
python scripts/run_crawler.py --site bizinfo --max-pages 3
python scripts/run_crawler.py --site kstartup --max-pages 3

# DB 저장 없이 테스트
python scripts/run_crawler.py --site bizinfo --no-db
```

출력 예시:
```
================================================================================
정부지원사업 크롤러 실행 - 2025-11-16 10:30:00
================================================================================

🔍 기업마당(Bizinfo) 크롤러 준비 중...
✓ 데이터베이스 연결 완료

================================================================================
📡 기업마당 크롤링 시작...
================================================================================

✓ 기업마당 크롤링 완료: 50개 공고 수집
💾 데이터베이스에 저장 중...
✓ 50개 공고 저장 완료

📋 수집된 공고 샘플 (최대 3개):
  [1] 2025년 창업기업 지원사업
      기관: 중소벤처기업부
      기간: 2025-01-01 ~ 2025-02-28
      URL: https://www.bizinfo.go.kr/...
```

### 2. REST API 사용

#### 공고 목록 조회

```bash
# 전체 공고 조회
curl http://localhost:8000/api/v1/projects

# 검색 및 필터링
curl "http://localhost:8000/api/v1/projects?search=창업&region=서울&limit=10"

# 통계 정보
curl http://localhost:8000/api/v1/projects/stats/summary
```

#### 기업 정보 등록

```bash
curl -X POST http://localhost:8000/api/v1/companies \
  -H "Content-Type: application/json" \
  -d '{
    "company_name": "테크스타트",
    "business_number": "123-45-67890",
    "company_type": "초기창업기업",
    "industry_code": "C26",
    "industry_name": "전자부품 제조업",
    "region": "서울",
    "employee_count": 5,
    "technology_fields": ["AI", "IoT"],
    "certifications": {"venture": true}
  }'
```

#### AI 사업계획서 생성

```bash
curl -X POST http://localhost:8000/api/v1/proposals/generate \
  -H "Content-Type: application/json" \
  -d '{
    "company_id": 1,
    "project_id": "BIZ2025001",
    "additional_info": {
      "사업_목표": "AI 기반 스마트 제조 솔루션 개발",
      "예상_매출": "1억원",
      "일자리_창출": "3명"
    }
  }'
```

응답 예시:
```json
{
  "message": "사업계획서가 성공적으로 생성되었습니다",
  "proposal": {
    "id": 1,
    "title": "테크스타트 - 2025년 창업기업 지원사업 사업계획서",
    "created_at": "2025-11-16T10:45:00"
  },
  "sections": {
    "1. 사업 개요": "...",
    "2. 사업의 필요성 및 목표": "...",
    "3. 사업 내용 및 추진 전략": "...",
    "4. 추진 체계 및 역량": "...",
    "5. 기대 효과 및 활용 방안": "...",
    "6. 예산 계획": "..."
  }
}
```

#### 기업 맞춤 추천 조회

```bash
# 특정 기업에 맞는 공고 추천
curl http://localhost:8000/api/v1/companies/1/recommendations
```

### 3. Python 코드에서 사용

```python
import asyncio
from backend.services.ai.proposal_generator import ProposalGenerator

# AI 사업계획서 생성기
async def generate_proposal_example():
    generator = ProposalGenerator()

    company_info = {
        'company_name': '테크스타트',
        'industry_name': '전자부품 제조업',
        'company_type': '초기창업기업'
    }

    project_info = {
        'project_name': '2025년 창업기업 지원사업',
        'agency': '중소벤처기업부',
        'support_type': '보조금',
        'support_amount': '최대 5천만원'
    }

    # 전체 사업계획서 생성
    sections = generator.generate_proposal(
        company_info=company_info,
        project_info=project_info,
        additional_info={'사업_목표': 'AI 솔루션 개발'}
    )

    print(sections)

asyncio.run(generate_proposal_example())
```

## 🔧 설정

### 크롤링 대상 사이트

| 사이트 | URL | 상태 | 설명 |
|-------|-----|------|------|
| 기업마당 | bizinfo.go.kr | ✅ 구현 | 전국 정부지원사업 통합 |
| K-Startup | k-startup.go.kr | ✅ 구현 | 창업/스타트업 지원사업 |
| 소상공인24 | sbiz.or.kr | 🚧 예정 | 소상공인 지원사업 |
| 중소벤처24 | smes.go.kr | 🚧 예정 | 중소기업 지원사업 |

### 매칭 알고리즘

매칭 점수는 다음 기준으로 계산됩니다:

```python
총점 = 업종일치도(40점)
     + 신청기간적합성(20점)
     + 자금규모적합성(20점)
     + 인증/자격요건(10점)
     + 지역적합성(10점)
```

- **80점 이상**: 강력 추천 🔥
- **60~79점**: 추천 ✅
- **40~59점**: 검토 권장 💡
- **40점 미만**: 비추천 (표시 안함)

자세한 내용은 [매칭 서비스 코드](backend/services/matching_service.py)를 참고하세요.

## 📚 API 문서

### 주요 엔드포인트

#### 공고 관련 (`/api/v1/projects`)

- `GET /` - 공고 목록 조회 (검색, 필터링, 페이지네이션)
- `GET /{project_id}` - 공고 상세 조회
- `GET /stats/summary` - 통계 정보
- `POST /refresh` - 크롤링 트리거

#### 기업 관련 (`/api/v1/companies`)

- `POST /` - 기업 정보 등록
- `GET /{company_id}` - 기업 정보 조회
- `PUT /{company_id}` - 기업 정보 수정
- `DELETE /{company_id}` - 기업 정보 삭제
- `GET /{company_id}/recommendations` - 맞춤 추천

#### 사업계획서 (`/api/v1/proposals`)

- `POST /generate` - AI 사업계획서 생성
- `GET /` - 사업계획서 목록
- `GET /{proposal_id}` - 사업계획서 조회
- `PUT /{proposal_id}` - 사업계획서 수정
- `POST /{proposal_id}/regenerate-section` - 섹션 재생성

자세한 API 스펙은 http://localhost:8000/docs 참고

## 🛠️ 기술 스택

### Backend
- **Framework**: FastAPI 0.109
- **Database**: PostgreSQL 14+ (asyncpg)
- **AI**: Anthropic Claude 3.5 Sonnet
- **Crawling**: Selenium, BeautifulSoup4

### Frontend (예정)
- **Framework**: React.js / Next.js
- **UI**: TailwindCSS
- **State Management**: Zustand / Redux Toolkit

### Infrastructure
- **Container**: Docker, Docker Compose
- **Task Queue**: Celery + Redis (예정)

## 📊 개발 로드맵

### ✅ Phase 1: 기반 구축 (완료)
- [x] 프로젝트 구조 설정
- [x] 데이터베이스 스키마
- [x] 크롤러 구현 (기업마당, K-Startup)
- [x] FastAPI 애플리케이션
- [x] REST API 엔드포인트
- [x] AI 사업계획서 생성

### 🚧 Phase 2: 핵심 기능 (진행 중)
- [ ] 매칭 API 엔드포인트
- [ ] PDF/DOCX 문서 생성
- [ ] 크롤러 스케줄링 (Celery)
- [ ] 알림 시스템

### 📅 Phase 3: UI/UX (예정)
- [ ] 웹 대시보드
- [ ] 사업계획서 편집기
- [ ] 인증 및 권한 관리

### 🚀 Phase 4: 배포 및 운영 (예정)
- [ ] Docker 컨테이너화
- [ ] CI/CD 파이프라인
- [ ] 모니터링 및 로깅
- [ ] 프로덕션 배포

## 🤝 기여하기

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
- Anthropic (Claude AI)
- FastAPI 및 오픈소스 커뮤니티

---

**현재 상태**: 🚧 개발 중 (Phase 1 완료, Phase 2 진행 중)

**마지막 업데이트**: 2025-11-16
