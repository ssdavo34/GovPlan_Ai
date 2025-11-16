# GovPlan_AI 프로젝트 계획서

## 📋 프로젝트 개요

### 프로젝트명
**GovPlan_AI** - 정부지원사업 공고 자동 수집 및 AI 기반 사업계획서 자동 작성 시스템

### 목적
정부지원사업 정보를 자동으로 수집하고, 기업 맞춤형 필터링을 통해 적합한 사업을 추천하며, AI를 활용하여 사업계획서를 자동으로 생성하는 통합 플랫폼 구축

### 핵심 가치
- ⏰ **시간 절감**: 수동 검색 및 작성 시간 90% 단축
- 🎯 **정확한 매칭**: 기업 특성에 맞는 사업 자동 추천
- 🤖 **AI 자동화**: 사업계획서 초안 자동 생성
- 📊 **데이터 기반**: 과거 공고 데이터 분석 및 트렌드 파악

---

## 🏗️ 시스템 아키텍처

```
┌─────────────────────────────────────────────────────────────┐
│                      사용자 인터페이스                         │
│         (Web Dashboard / CLI / API Endpoints)              │
└──────────────────────┬──────────────────────────────────────┘
                       │
        ┌──────────────┴──────────────┐
        │                             │
┌───────▼────────┐           ┌────────▼────────┐
│  크롤링 모듈     │           │  AI 생성 모듈    │
│  (Scraper)     │           │  (Generator)    │
└───────┬────────┘           └────────┬────────┘
        │                             │
        │         ┌───────────────────┘
        │         │
┌───────▼─────────▼────────┐
│    데이터베이스 레이어      │
│   (PostgreSQL/MongoDB)   │
└───────┬──────────────────┘
        │
┌───────▼──────────────────┐
│   필터링 & 추천 엔진       │
│  (Matching Engine)       │
└──────────────────────────┘
        │
┌───────▼──────────────────┐
│   알림 & 자동화 시스템     │
│  (Notification System)   │
└──────────────────────────┘
```

---

## 🛠️ 기술 스택

### Backend
- **언어**: Python 3.11+
- **웹 프레임워크**: FastAPI (API 서버)
- **크롤링**:
  - `requests` - HTTP 요청
  - `BeautifulSoup4` - HTML 파싱
  - `Selenium` - 동적 페이지 크롤링
  - `Playwright` - 현대적 브라우저 자동화
- **스케줄링**:
  - `APScheduler` - 주기적 크롤링 작업
  - `Celery` + `Redis` - 비동기 작업 큐

### Database
- **관계형 DB**: PostgreSQL 15+
  - 구조화된 공고 데이터 저장
  - 기업 정보 및 사용자 관리
- **문서 DB**: MongoDB (선택사항)
  - 비정형 공고 상세 내용 저장
- **ORM**: SQLAlchemy 2.0+
- **마이그레이션**: Alembic

### AI/ML
- **LLM 통합**:
  - Anthropic Claude API (사업계획서 생성)
  - OpenAI GPT API (대안)
- **벡터 DB**: ChromaDB / Pinecone (문서 유사도 검색)
- **임베딩**: sentence-transformers
- **프롬프트 관리**: LangChain

### Frontend (Optional)
- **프레임워크**: React / Next.js
- **UI 라이브러리**: Tailwind CSS, shadcn/ui
- **상태 관리**: Zustand / Redux Toolkit

### DevOps & Automation
- **컨테이너**: Docker, Docker Compose
- **CI/CD**: GitHub Actions
- **모니터링**: Prometheus + Grafana
- **로깅**: Python logging + ELK Stack (선택)
- **워크플로우**: n8n (자체 호스팅) / Zapier

### 문서 생성
- **PDF**: ReportLab / WeasyPrint
- **한글/워드**: python-docx
- **Markdown**: markdown2

---

## 📂 디렉토리 구조

```
GovPlan_AI/
├── docs/                          # 프로젝트 문서
│   ├── PROJECT_PLAN.md
│   ├── API_SPEC.md
│   └── DEPLOYMENT.md
│
├── src/
│   ├── crawler/                   # 크롤링 모듈
│   │   ├── __init__.py
│   │   ├── base_crawler.py       # 크롤러 베이스 클래스
│   │   ├── scrapers/             # 사이트별 스크래퍼
│   │   │   ├── __init__.py
│   │   │   ├── k_startup.py     # K-Startup 크롤러
│   │   │   ├── smes.py           # 중소벤처24 크롤러
│   │   │   ├── sbiz.py           # 소상공인24 크롤러
│   │   │   └── bizinfo.py        # 기업마당 크롤러
│   │   ├── parser.py             # HTML 파싱 유틸
│   │   └── scheduler.py          # 크롤링 스케줄러
│   │
│   ├── database/                  # 데이터베이스 레이어
│   │   ├── __init__.py
│   │   ├── models.py             # SQLAlchemy 모델
│   │   ├── schemas.py            # Pydantic 스키마
│   │   ├── connection.py         # DB 연결 관리
│   │   └── migrations/           # Alembic 마이그레이션
│   │
│   ├── ai/                        # AI 모듈
│   │   ├── __init__.py
│   │   ├── llm_client.py         # LLM API 클라이언트
│   │   ├── prompt_templates.py   # 프롬프트 템플릿
│   │   ├── proposal_generator.py # 사업계획서 생성
│   │   └── embeddings.py         # 벡터 임베딩
│   │
│   ├── matching/                  # 매칭 엔진
│   │   ├── __init__.py
│   │   ├── filter.py             # 필터링 로직
│   │   ├── scorer.py             # 매칭 점수 계산
│   │   └── recommender.py        # 추천 알고리즘
│   │
│   ├── api/                       # FastAPI 애플리케이션
│   │   ├── __init__.py
│   │   ├── main.py               # FastAPI 앱 엔트리포인트
│   │   ├── routes/               # API 라우트
│   │   │   ├── __init__.py
│   │   │   ├── grants.py         # 공고 관련 API
│   │   │   ├── companies.py      # 기업 정보 API
│   │   │   ├── proposals.py      # 사업계획서 API
│   │   │   └── auth.py           # 인증 API
│   │   ├── dependencies.py       # FastAPI 의존성
│   │   └── middleware.py         # 미들웨어
│   │
│   ├── document/                  # 문서 생성
│   │   ├── __init__.py
│   │   ├── pdf_generator.py      # PDF 생성
│   │   ├── docx_generator.py     # 워드 문서 생성
│   │   └── templates/            # 문서 템플릿
│   │
│   ├── notification/              # 알림 시스템
│   │   ├── __init__.py
│   │   ├── email_sender.py       # 이메일 발송
│   │   ├── slack_bot.py          # Slack 알림
│   │   └── kakao_sender.py       # 카카오톡 알림 (선택)
│   │
│   └── utils/                     # 유틸리티
│       ├── __init__.py
│       ├── logger.py             # 로깅 설정
│       ├── config.py             # 설정 관리
│       └── validators.py         # 데이터 검증
│
├── tests/                         # 테스트
│   ├── unit/
│   ├── integration/
│   └── e2e/
│
├── scripts/                       # 실행 스크립트
│   ├── run_crawler.py            # 크롤러 실행
│   ├── init_db.py                # DB 초기화
│   └── test_ai.py                # AI 테스트
│
├── config/                        # 설정 파일
│   ├── settings.yaml
│   ├── crawler_targets.yaml      # 크롤링 대상 설정
│   └── prompt_config.yaml        # AI 프롬프트 설정
│
├── docker/                        # Docker 설정
│   ├── Dockerfile
│   ├── docker-compose.yml
│   └── .dockerignore
│
├── .github/                       # GitHub Actions
│   └── workflows/
│       ├── ci.yml
│       └── deploy.yml
│
├── requirements.txt               # Python 패키지
├── pyproject.toml                # Poetry 설정 (선택)
├── .env.example                  # 환경변수 예시
├── .gitignore
└── README.md
```

---

## 🔍 주요 기능별 상세 설계

### 1. 크롤링 모듈 (Crawler)

#### 1.1 타겟 사이트
| 사이트명 | URL | 크롤링 방법 | 주기 |
|---------|-----|-----------|------|
| 기업마당 | https://www.bizinfo.go.kr | Selenium | 매일 |
| K-Startup | https://www.k-startup.go.kr | BeautifulSoup | 매일 |
| 중소벤처24 | https://www.smes.go.kr | Playwright | 매일 |
| 소상공인24 | https://www.sbiz.or.kr | BeautifulSoup | 매일 |

#### 1.2 수집 데이터 필드
```python
{
    "title": str,              # 공고 제목
    "program_id": str,         # 사업 고유 ID
    "source": str,             # 출처 사이트
    "url": str,                # 상세 페이지 URL
    "category": str,           # 지원 분야 (R&D, 마케팅, 인력 등)
    "target_industry": list,   # 대상 산업군
    "target_company_type": list, # 대상 기업 유형 (예비창업, 스타트업 등)
    "region": list,            # 지원 지역
    "budget_min": int,         # 최소 지원 금액
    "budget_max": int,         # 최대 지원 금액
    "start_date": datetime,    # 모집 시작일
    "end_date": datetime,      # 모집 마감일
    "agency": str,             # 담당 기관
    "requirements": dict,      # 자격 요건
    "documents": list,         # 제출 서류
    "description": str,        # 사업 상세 설명
    "crawled_at": datetime,    # 크롤링 시각
    "updated_at": datetime     # 업데이트 시각
}
```

#### 1.3 크롤링 프로세스
```
1. 스케줄러 실행 (매일 오전 9시)
2. 각 사이트별 크롤러 병렬 실행
3. 공고 목록 페이지 파싱
4. 신규/변경 공고 감지
5. 상세 페이지 크롤링
6. 데이터 정제 및 표준화
7. 데이터베이스 저장
8. 변경 사항 알림 발송
```

#### 1.4 에러 처리
- Retry 메커니즘 (최대 3회)
- 타임아웃 설정 (30초)
- 로깅 및 에러 알림
- 크롤링 실패 시 이전 데이터 유지

---

### 2. 데이터베이스 설계

#### 2.1 ERD (주요 테이블)

**grants (공고 정보)**
```sql
CREATE TABLE grants (
    id SERIAL PRIMARY KEY,
    program_id VARCHAR(100) UNIQUE NOT NULL,
    title VARCHAR(500) NOT NULL,
    source VARCHAR(50) NOT NULL,
    url TEXT NOT NULL,
    category VARCHAR(100),
    target_industry JSONB,
    target_company_type JSONB,
    region JSONB,
    budget_min BIGINT,
    budget_max BIGINT,
    start_date TIMESTAMP,
    end_date TIMESTAMP,
    agency VARCHAR(200),
    requirements JSONB,
    documents JSONB,
    description TEXT,
    crawled_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    status VARCHAR(20) DEFAULT 'active',
    INDEX idx_end_date (end_date),
    INDEX idx_category (category),
    INDEX idx_status (status)
);
```

**companies (기업 정보)**
```sql
CREATE TABLE companies (
    id SERIAL PRIMARY KEY,
    company_name VARCHAR(200) NOT NULL,
    business_number VARCHAR(20) UNIQUE,
    industry_code VARCHAR(10),
    company_type VARCHAR(50),  -- 예비창업, 스타트업, 중견기업 등
    region VARCHAR(100),
    founded_date DATE,
    employee_count INT,
    revenue BIGINT,
    tech_fields JSONB,         -- 기술 분야
    strengths TEXT,            -- 기업 강점
    past_grants JSONB,         -- 과거 지원 이력
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

**proposals (생성된 사업계획서)**
```sql
CREATE TABLE proposals (
    id SERIAL PRIMARY KEY,
    company_id INT REFERENCES companies(id),
    grant_id INT REFERENCES grants(id),
    title VARCHAR(500),
    content TEXT,              -- 사업계획서 전문
    sections JSONB,            -- 섹션별 내용
    format VARCHAR(20),        -- pdf, docx, md
    file_path TEXT,
    status VARCHAR(20),        -- draft, review, finalized
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

**match_scores (매칭 점수)**
```sql
CREATE TABLE match_scores (
    id SERIAL PRIMARY KEY,
    company_id INT REFERENCES companies(id),
    grant_id INT REFERENCES grants(id),
    score DECIMAL(5,2),        -- 0-100 점수
    match_details JSONB,       -- 매칭 상세 근거
    calculated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(company_id, grant_id)
);
```

#### 2.2 인덱싱 전략
- 공고 마감일 인덱스 (빠른 마감 임박 조회)
- 카테고리/지역 복합 인덱스
- 기업-공고 매칭 조회 최적화

---

### 3. AI 사업계획서 생성 시스템

#### 3.1 프롬프트 설계

**시스템 프롬프트 템플릿**
```python
SYSTEM_PROMPT = """
당신은 정부지원사업 사업계획서 작성 전문가입니다.
다음 정보를 바탕으로 전문적이고 설득력 있는 사업계획서를 작성해주세요.

작성 원칙:
1. 구체적인 수치와 데이터 활용
2. 사업의 필요성과 타당성 명확히 제시
3. 실현 가능한 계획 수립
4. 정부 정책 방향과의 연계성 강조
"""

PROPOSAL_PROMPT = """
## 공고 정보
- 사업명: {grant_title}
- 지원 분야: {category}
- 지원 금액: {budget}
- 담당 기관: {agency}

## 기업 정보
- 기업명: {company_name}
- 업종: {industry}
- 기업 유형: {company_type}
- 기술 분야: {tech_fields}
- 강점: {strengths}

## 요청사항
다음 구조로 사업계획서를 작성해주세요:
1. 사업 개요 (200자)
2. 추진 배경 및 필요성 (500자)
3. 사업 목표 및 추진 전략 (800자)
4. 추진 체계 및 일정 (600자)
5. 기대 효과 (400자)
6. 예산 계획 (표 형식)
"""
```

#### 3.2 생성 프로세스
```
1. 기업 정보 + 공고 정보 입력
2. 프롬프트 생성 (템플릿 기반)
3. Claude API 호출 (claude-3-5-sonnet)
4. 응답 파싱 및 구조화
5. 문서 포맷팅 (Markdown → PDF/DOCX)
6. 데이터베이스 저장
7. 사용자에게 전달
```

#### 3.3 개선 기능
- **과거 사례 학습**: 벡터 DB에 저장된 우수 사업계획서 검색
- **반복 개선**: 사용자 피드백 반영하여 재생성
- **맞춤형 섹션**: 공고별 필수 항목 자동 추출
- **키워드 최적화**: 공고 키워드 자동 포함

---

### 4. 기업 맞춤 추천 시스템

#### 4.1 매칭 알고리즘

**점수 계산 로직 (0-100점)**
```python
def calculate_match_score(company, grant):
    score = 0

    # 1. 기업 유형 매칭 (30점)
    if company.type in grant.target_company_type:
        score += 30

    # 2. 산업 분야 매칭 (25점)
    industry_match = len(set(company.industries) & set(grant.target_industry))
    score += min(25, industry_match * 8)

    # 3. 지역 매칭 (15점)
    if company.region in grant.region or '전국' in grant.region:
        score += 15

    # 4. 기술 분야 매칭 (20점)
    tech_match = len(set(company.tech_fields) & set(grant.tech_keywords))
    score += min(20, tech_match * 5)

    # 5. 예산 적합성 (10점)
    if grant.budget_min <= company.expected_budget <= grant.budget_max:
        score += 10

    return score
```

#### 4.2 필터링 옵션
- **필수 필터**: 마감일, 자격 요건
- **선택 필터**: 지원 금액, 지역, 카테고리
- **정렬 옵션**: 매칭 점수, 마감일 임박, 지원 금액

#### 4.3 추천 알림
- **일일 다이제스트**: 매일 오전 신규 추천 공고
- **즉시 알림**: 90점 이상 고매칭 공고 발견 시
- **마감 임박**: D-7, D-3, D-1 알림

---

### 5. 자동화 워크플로우

#### 5.1 워크플로우 예시 (n8n)

```
[스케줄 트리거: 매일 09:00]
    ↓
[크롤러 실행]
    ↓
[신규 공고 감지]
    ↓
[기업별 매칭 점수 계산]
    ↓
[80점 이상 공고 필터링]
    ↓
[사업계획서 초안 생성]
    ↓
[이메일/Slack 알림 발송]
```

#### 5.2 통합 가능한 서비스
- **이메일**: Gmail, SendGrid
- **메신저**: Slack, Discord
- **카카오톡**: 카카오톡 비즈니스 API
- **캘린더**: Google Calendar (마감일 자동 등록)
- **드라이브**: Google Drive, Dropbox (문서 자동 저장)

---

## 📅 구현 로드맵

### Phase 1: 기반 구축 (4주)
**Week 1-2: 프로젝트 셋업 및 크롤링**
- [ ] 프로젝트 환경 설정 (Python, Docker, PostgreSQL)
- [ ] 기본 디렉토리 구조 생성
- [ ] 크롤러 베이스 클래스 구현
- [ ] 1개 사이트 크롤러 구현 (K-Startup)
- [ ] 데이터베이스 스키마 설계 및 생성

**Week 3-4: 데이터 수집 확장**
- [ ] 나머지 3개 사이트 크롤러 구현
- [ ] 크롤링 스케줄러 구현
- [ ] 데이터 정제 및 표준화 로직
- [ ] 에러 처리 및 로깅 시스템
- [ ] 단위 테스트 작성

### Phase 2: AI 통합 (3주)
**Week 5-6: AI 사업계획서 생성**
- [ ] Claude API 연동
- [ ] 프롬프트 템플릿 설계
- [ ] 사업계획서 생성 엔진 구현
- [ ] PDF/DOCX 문서 생성 기능
- [ ] 생성 결과 저장 및 관리

**Week 7: 매칭 시스템**
- [ ] 기업-공고 매칭 알고리즘 구현
- [ ] 필터링 및 정렬 기능
- [ ] 추천 점수 계산 로직

### Phase 3: API 및 인터페이스 (3주)
**Week 8-9: REST API 구축**
- [ ] FastAPI 애플리케이션 구조 설계
- [ ] 공고 조회 API
- [ ] 기업 정보 관리 API
- [ ] 사업계획서 생성 API
- [ ] 인증 및 권한 관리
- [ ] API 문서화 (Swagger)

**Week 10: 프론트엔드 (선택사항)**
- [ ] React 대시보드 기본 구조
- [ ] 공고 검색 및 필터링 UI
- [ ] 사업계획서 생성 UI
- [ ] 매칭 결과 시각화

### Phase 4: 자동화 및 배포 (2주)
**Week 11: 알림 시스템**
- [ ] 이메일 알림 구현
- [ ] Slack 통합
- [ ] n8n 워크플로우 설정
- [ ] 알림 설정 관리

**Week 12: 배포 및 테스트**
- [ ] Docker 컨테이너화
- [ ] Docker Compose 설정
- [ ] CI/CD 파이프라인 구축
- [ ] 통합 테스트
- [ ] 프로덕션 배포

### Phase 5: 고도화 (지속적)
- [ ] 벡터 DB 통합 (유사 공고 검색)
- [ ] 대시보드 고도화
- [ ] 모바일 앱 개발
- [ ] 사용자 피드백 반영
- [ ] 성능 최적화
- [ ] 추가 사이트 크롤링 확장

---

## 💰 예상 비용

### 개발 비용
- **인력**: 백엔드 1명 + 프론트엔드 1명 (3개월) - 협의 필요

### 운영 비용 (월간)
| 항목 | 서비스 | 예상 비용 |
|-----|--------|----------|
| 서버 호스팅 | AWS EC2 t3.medium | $40 |
| 데이터베이스 | AWS RDS PostgreSQL | $30 |
| AI API | Claude API (100만 토큰) | $15 |
| 이메일 발송 | SendGrid | $15 |
| 도메인 | - | $2 |
| **합계** | | **$102/월** |

### 절감 방안
- 초기: 로컬 서버 또는 무료 티어 활용
- AI: 토큰 최적화, 캐싱 전략
- DB: PostgreSQL 자체 호스팅

---

## 🔒 보안 및 컴플라이언스

### 크롤링 정책
- robots.txt 준수
- 요청 간격 제어 (최소 1초)
- User-Agent 명시
- 과도한 트래픽 방지

### 데이터 보안
- API 키 환경변수 관리
- 데이터베이스 암호화
- HTTPS 통신
- 정기적 백업

### 개인정보 보호
- 기업 정보 암호화 저장
- 접근 권한 관리
- 로그 기록 및 감사

---

## 📊 성공 지표 (KPI)

### 기술적 지표
- **크롤링 성공률**: 95% 이상
- **API 응답 시간**: 평균 200ms 이하
- **사업계획서 생성 시간**: 30초 이하
- **시스템 가동률**: 99% 이상

### 비즈니스 지표
- **공고 수집 개수**: 월 500개 이상
- **매칭 정확도**: 사용자 만족도 80% 이상
- **사업계획서 생성 수**: 월 100건
- **사용자 시간 절감**: 공고당 평균 2시간

---

## 🚀 확장 가능성

### 단기 확장
- 지방자치단체 공고 추가
- 민간 지원사업 포함
- 업종별 특화 템플릿

### 중기 확장
- 컨설팅 매칭 서비스
- 공동 사업 파트너 매칭
- 과거 성공 사례 데이터베이스

### 장기 비전
- SaaS 플랫폼 전환
- 기업 신용 평가 연동
- 전문가 네트워크 구축
- 글로벌 확장 (해외 정부 지원사업)

---

## 📝 리스크 관리

### 기술적 리스크
| 리스크 | 영향도 | 대응 방안 |
|-------|--------|----------|
| 사이트 구조 변경 | 높음 | 주기적 모니터링, 유연한 파서 설계 |
| API 비용 초과 | 중간 | 토큰 사용량 모니터링, 캐싱 |
| 서버 다운타임 | 중간 | 이중화, 자동 재시작 |

### 법적 리스크
| 리스크 | 영향도 | 대응 방안 |
|-------|--------|----------|
| 저작권 문제 | 낮음 | 공공 데이터만 수집, 출처 명시 |
| 개인정보 유출 | 높음 | 암호화, 접근 제어, 정기 감사 |

---

## 👥 팀 구성 (권장)

### 필수 인력
- **백엔드 개발자** (1명): Python, FastAPI, 크롤링
- **AI/ML 엔지니어** (1명): LLM 통합, 프롬프트 엔지니어링

### 선택 인력
- **프론트엔드 개발자** (1명): React, UI/UX
- **DevOps 엔지니어** (1명): 배포, 모니터링
- **도메인 전문가** (1명): 정부 지원사업 전문 지식

---

## 📚 참고 자료

### 크롤링 대상 사이트
- [기업마당](https://www.bizinfo.go.kr)
- [K-Startup](https://www.k-startup.go.kr)
- [중소벤처24](https://www.smes.go.kr)
- [소상공인24](https://www.sbiz.or.kr)

### 기술 문서
- [FastAPI 공식 문서](https://fastapi.tiangolo.com/)
- [Anthropic Claude API](https://docs.anthropic.com/)
- [SQLAlchemy 문서](https://docs.sqlalchemy.org/)
- [BeautifulSoup 가이드](https://www.crummy.com/software/BeautifulSoup/bs4/doc/)

---

## ✅ 다음 단계

1. **프로젝트 승인 및 리소스 확보**
2. **개발 환경 설정 시작**
3. **Phase 1 작업 착수**
4. **주간 진행 상황 리뷰 일정 수립**

---

**문서 버전**: 1.0
**작성일**: 2025-11-16
**다음 업데이트 예정**: Phase 1 완료 후
