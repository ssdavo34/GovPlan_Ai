# 프로젝트 구조

## 디렉토리 구조

```
GovPlan_Ai/
├── backend/                    # 백엔드 애플리케이션
│   ├── api/                   # API 엔드포인트
│   │   ├── __init__.py
│   │   ├── projects.py        # 지원사업 관련 API
│   │   ├── companies.py       # 기업 정보 관련 API
│   │   ├── matching.py        # 매칭 관련 API
│   │   └── documents.py       # 사업계획서 생성 API
│   ├── core/                  # 핵심 설정 및 유틸리티
│   │   ├── __init__.py
│   │   ├── config.py          # 애플리케이션 설정
│   │   ├── database.py        # 데이터베이스 연결
│   │   └── security.py        # 보안 관련 기능
│   ├── crawlers/              # 크롤러 모듈
│   │   ├── __init__.py
│   │   ├── base_crawler.py    # 베이스 크롤러 클래스
│   │   ├── bizinfo_crawler.py # 기업마당 크롤러
│   │   ├── kstartup_crawler.py # K-Startup 크롤러
│   │   ├── sbiz_crawler.py    # 소상공인24 크롤러
│   │   └── parser.py          # 공고문 파서
│   ├── models/                # 데이터베이스 모델
│   │   ├── __init__.py
│   │   ├── project.py         # 지원사업 모델
│   │   ├── company.py         # 기업 정보 모델
│   │   └── matching.py        # 매칭 이력 모델
│   ├── services/              # 비즈니스 로직
│   │   ├── __init__.py
│   │   ├── crawler_service.py # 크롤링 서비스
│   │   ├── matching_service.py # 매칭 서비스
│   │   ├── ai_service.py      # AI 문서 생성 서비스
│   │   └── document_service.py # 문서 변환 서비스
│   ├── utils/                 # 유틸리티 함수
│   │   ├── __init__.py
│   │   ├── validators.py      # 검증 함수
│   │   ├── formatters.py      # 포맷 변환 함수
│   │   └── logger.py          # 로깅 설정
│   ├── app.py                 # Flask/FastAPI 메인 애플리케이션
│   └── requirements.txt       # Python 의존성
├── frontend/                  # 프론트엔드 애플리케이션
│   ├── src/
│   │   ├── components/        # React/Vue 컴포넌트
│   │   ├── pages/             # 페이지
│   │   ├── services/          # API 호출 서비스
│   │   └── App.js
│   ├── public/
│   └── package.json
├── database/                  # 데이터베이스 관련
│   ├── migrations/            # 마이그레이션 파일
│   │   └── 001_initial_schema.sql
│   └── seeds/                 # 초기 데이터
│       └── sample_data.sql
├── scripts/                   # 유틸리티 스크립트
│   ├── crawl_scheduler.py     # 크롤링 스케줄러
│   ├── db_setup.py            # 데이터베이스 초기화
│   └── data_cleaner.py        # 데이터 정제
├── tests/                     # 테스트
│   ├── unit/                  # 단위 테스트
│   └── integration/           # 통합 테스트
├── templates/                 # 사업계획서 템플릿
│   ├── common/                # 공통 템플릿
│   ├── startup/               # 창업 지원사업 템플릿
│   ├── rnd/                   # R&D 사업 템플릿
│   └── smallbiz/              # 소상공인 지원사업 템플릿
├── docs/                      # 문서
│   ├── REQUIREMENTS.md        # 요구사항 명세서
│   ├── PROJECT_STRUCTURE.md   # 프로젝트 구조
│   ├── API.md                 # API 문서
│   └── DEPLOYMENT.md          # 배포 가이드
├── .env.example               # 환경변수 예제
├── .gitignore                 # Git 무시 파일
├── docker-compose.yml         # Docker 구성
└── README.md                  # 프로젝트 소개
```

## 주요 모듈 설명

### Backend

#### API (`backend/api/`)
- REST API 엔드포인트 정의
- 요청 검증 및 응답 포맷팅
- 인증 및 권한 검사

#### Core (`backend/core/`)
- 애플리케이션 설정 관리
- 데이터베이스 연결 풀
- 보안 설정 (CORS, JWT 등)

#### Crawlers (`backend/crawlers/`)
- 각 정부 사이트별 크롤러 구현
- 공통 크롤링 로직 (재시도, 에러 핸들링)
- HTML 파싱 및 데이터 추출

#### Models (`backend/models/`)
- ORM 모델 정의 (SQLAlchemy/Django ORM)
- 데이터베이스 스키마 매핑
- 관계 정의

#### Services (`backend/services/`)
- 비즈니스 로직 구현
- 크롤링 작업 관리
- 매칭 알고리즘
- AI API 통합
- 문서 생성 파이프라인

#### Utils (`backend/utils/`)
- 재사용 가능한 유틸리티 함수
- 로깅 설정
- 데이터 검증 및 포맷팅

### Frontend

#### Components
- 재사용 가능한 UI 컴포넌트
- 프로젝트 목록, 카드, 필터 등

#### Pages
- 메인 페이지
- 기업 정보 입력 페이지
- 매칭 결과 페이지
- 사업계획서 생성 페이지

### Database

#### Migrations
- 데이터베이스 스키마 버전 관리
- 테이블 생성 및 수정 이력

#### Seeds
- 테스트용 초기 데이터
- 샘플 데이터

### Scripts

- 크롤링 스케줄러 (Cron 또는 Celery Beat)
- 데이터베이스 초기화
- 데이터 정제 및 마이그레이션

### Templates

- 정부 사업별 사업계획서 템플릿
- DOCX, HWP 템플릿 파일

## 기술 스택

### Backend
- **Framework**: FastAPI (고성능 비동기) 또는 Flask (간단한 구조)
- **ORM**: SQLAlchemy
- **Task Queue**: Celery + Redis
- **Database**: PostgreSQL 또는 MySQL
- **Crawling**: Selenium, BeautifulSoup4, Scrapy

### Frontend
- **Framework**: React.js 또는 Vue.js
- **UI Library**: TailwindCSS, Ant Design
- **State Management**: Redux 또는 Vuex
- **HTTP Client**: Axios

### AI/ML
- **LLM**: OpenAI GPT-4, Anthropic Claude
- **Framework**: LangChain

### DevOps
- **Container**: Docker
- **Orchestration**: Docker Compose
- **CI/CD**: GitHub Actions
- **Monitoring**: Sentry, Prometheus

## 개발 워크플로우

1. **로컬 개발**
   ```bash
   # 백엔드 실행
   cd backend
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   python app.py

   # 프론트엔드 실행
   cd frontend
   npm install
   npm start
   ```

2. **데이터베이스 마이그레이션**
   ```bash
   python scripts/db_setup.py
   ```

3. **크롤링 실행**
   ```bash
   python scripts/crawl_scheduler.py
   ```

4. **테스트**
   ```bash
   pytest tests/
   ```

## 배포

- Docker Compose를 사용한 컨테이너 배포
- 환경변수를 통한 설정 관리
- Nginx를 통한 리버스 프록시
