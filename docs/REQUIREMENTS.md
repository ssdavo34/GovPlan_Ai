# 정부지원사업 자동화 프로그램 요구사항 명세서

## 1. 프로젝트 개요

정부지원사업 정보를 자동으로 수집하고, 기업 정보를 기반으로 맞춤형 지원사업을 추천하며, AI를 활용하여 사업계획서를 자동 생성하는 통합 플랫폼

## 2. 크롤링 대상 사이트 및 우선순위

### 2.1 우선순위 1 - 필수 구현
- **기업마당** (www.bizinfo.go.kr)
  - 전국 대부분의 정부지원사업 공고 통합 제공
  - 광범위한 정보 수집 가능
  - 가장 높은 우선순위

- **K-Startup** (www.k-startup.go.kr)
  - 창업 및 초기 스타트업 대상 집중
  - 기업 확인서 발급 등 핵심 지원사업 알림
  - 창업기업 타겟팅에 필수

### 2.2 우선순위 2 - 단계적 구현
- **소상공인24** (www.sbiz.or.kr)
  - 소상공인 전용 지원사업 집중
  - 지역 및 전통시장 사업 포함

- **중소벤처24** (www.smes.go.kr)
  - 서류 발급 및 연계 기능
  - 지원사업 공식 문서 확보용

### 2.3 우선순위 3 - 확장 기능
- **IRIS** (www.iris.go.kr)
  - R&D 과제 중심 정보
  - 신청 및 전략 수립용 분석 포털

- **NTIS** (www.ntis.go.kr)
  - 국가과학기술정보서비스
  - R&D 과제 통합 정보

### 2.4 우선순위 결정 기준
- 공신력
- 업데이트 빈도
- 데이터 가공 가능성
- 대상 기업 유형 (예비창업, 초기스타트업, R&D 중소기업, 소상공인)

## 3. 공고문 자동 파싱 핵심 필드

### 3.1 기본 정보
- 사업명 (공고명)
- 공고번호 또는 고유ID
- 시행기관 (주관부처 및 담당기관)
- 공고 URL 및 상세 자료 링크

### 3.2 사업 상세
- 사업 개요/목적
- 지원 내용 (지원금 규모, 지원 유형: 보조금/융자/바우처)
- 자금 사용처

### 3.3 신청 정보
- 모집 대상 (기업 유형, 업종, 지역, 요건 등)
- 모집 기간 (신청 시작일 / 종료일)
- 제출서류 및 신청 방법

### 3.4 평가 정보
- 평가 및 선정 기준
- 관련 산업분류 코드 (KSIC)

### 3.5 기타 정보
- 문의처 및 연락처
- 첨부파일 링크

## 4. 데이터베이스 구조 설계

### 4.1 정부지원사업 테이블 (gov_support_projects)

```sql
CREATE TABLE gov_support_projects (
    id VARCHAR(50) PRIMARY KEY,  -- 고유 식별자
    project_name VARCHAR(500) NOT NULL,  -- 사업명
    agency VARCHAR(200),  -- 시행기관
    project_url TEXT,  -- 공고 URL
    summary TEXT,  -- 사업 개요/목적
    support_type VARCHAR(100),  -- 보조금/융자/바우처 등
    support_amount VARCHAR(200),  -- 지원금 규모
    target_type VARCHAR(200),  -- 예비창업/소상공인/R&D 등
    target_requirements TEXT,  -- 모집 대상 상세 요건
    industry_code VARCHAR(100),  -- KSIC 코드
    region VARCHAR(100),  -- 지원 대상 지역
    application_start_date DATE,  -- 접수 시작일
    application_end_date DATE,  -- 접수 종료일
    required_documents TEXT,  -- 필수 제출서류
    evaluation_criteria TEXT,  -- 평가 및 선정 기준
    fund_usage TEXT,  -- 자금 사용처
    contact_info VARCHAR(500),  -- 문의처
    attachments JSON,  -- 첨부파일 정보
    source_site VARCHAR(100),  -- 출처 사이트
    last_crawled TIMESTAMP,  -- 데이터 최신화 일자
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    status VARCHAR(50) DEFAULT 'active',  -- active/closed/expired

    INDEX idx_application_dates (application_start_date, application_end_date),
    INDEX idx_target_type (target_type),
    INDEX idx_industry_code (industry_code),
    INDEX idx_status (status),
    INDEX idx_source_site (source_site)
);
```

### 4.2 기업 정보 테이블 (companies)

```sql
CREATE TABLE companies (
    id INT AUTO_INCREMENT PRIMARY KEY,
    company_name VARCHAR(200) NOT NULL,
    business_number VARCHAR(50) UNIQUE,  -- 사업자등록번호
    company_type VARCHAR(100),  -- 기업 유형 (예비창업/초기창업/중소기업 등)
    industry_code VARCHAR(100),  -- KSIC 코드
    industry_name VARCHAR(200),  -- 업종명
    region VARCHAR(100),  -- 소재지
    establishment_date DATE,  -- 설립일
    employee_count INT,  -- 직원 수
    annual_revenue BIGINT,  -- 연매출
    certifications JSON,  -- 보유 인증 (벤처인증, 이노비즈 등)
    technology_fields JSON,  -- 기술 분야
    funding_needs VARCHAR(500),  -- 자금 필요성
    preferred_support_types JSON,  -- 선호 지원 유형
    user_id INT,  -- 사용자 연결 (추후 확장)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    INDEX idx_company_type (company_type),
    INDEX idx_industry_code (industry_code),
    INDEX idx_region (region)
);
```

### 4.3 매칭 이력 테이블 (matching_history)

```sql
CREATE TABLE matching_history (
    id INT AUTO_INCREMENT PRIMARY KEY,
    company_id INT NOT NULL,
    project_id VARCHAR(50) NOT NULL,
    match_score DECIMAL(5,2),  -- 매칭 점수
    match_reasons JSON,  -- 매칭 사유
    is_bookmarked BOOLEAN DEFAULT FALSE,
    is_applied BOOLEAN DEFAULT FALSE,
    application_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (company_id) REFERENCES companies(id),
    FOREIGN KEY (project_id) REFERENCES gov_support_projects(id),
    INDEX idx_company_project (company_id, project_id),
    INDEX idx_match_score (match_score DESC)
);
```

## 5. 맞춤 필터링 및 매칭 로직

### 5.1 기업 정보 수집 항목
- 업종 (KSIC 코드 포함)
- 업력 (설립일 기준)
- 지역
- 자금 필요성 및 규모
- 기술 분야 (AI, IoT, 바이오 등)
- 보유 인증 (벤처인증, 이노비즈, 메인비즈 등)
- 직원 수
- 매출 규모

### 5.2 필터링 조건
1. **필수 조건 (Hard Filter)**
   - 신청 기간 유효성 (현재 날짜가 신청 기간 내)
   - 지역 조건 (전국 대상 OR 해당 지역)
   - 기본 자격 요건 (업력, 기업 유형 등)

2. **우선순위 조건 (Soft Filter)**
   - 업종 일치도
   - 기술 분야 관련성
   - 자금 규모 적합성
   - 인증 보유 여부

### 5.3 매칭 점수 산정 알고리즘

```python
매칭점수 =
    (업종일치도 × 40점) +
    (신청기간적합성 × 20점) +
    (자금규모적합성 × 20점) +
    (인증/자격요건 × 10점) +
    (지역적합성 × 10점)

# 세부 계산
업종일치도:
  - KSIC 대분류 일치: 20점
  - KSIC 중분류 일치: 30점
  - KSIC 소분류 일치: 40점

신청기간적합성:
  - 신청 마감까지 1개월 이상: 20점
  - 신청 마감까지 2주~1개월: 15점
  - 신청 마감까지 2주 미만: 10점

자금규모적합성:
  - 필요 자금과 지원금 차이 20% 이내: 20점
  - 필요 자금과 지원금 차이 50% 이내: 15점
  - 필요 자금과 지원금 차이 50% 초과: 10점

인증/자격요건:
  - 필수 인증 모두 보유: 10점
  - 필수 인증 일부 보유: 5점
  - 필수 인증 미보유: 0점

지역적합성:
  - 전국 대상: 10점
  - 해당 지역: 10점
  - 인접 지역: 5점
```

### 5.4 추천 시스템
- 매칭 점수 80점 이상: 강력 추천
- 매칭 점수 60~79점: 추천
- 매칭 점수 40~59점: 검토 권장
- 매칭 점수 40점 미만: 비추천 (표시 안함)

## 6. 사업계획서 자동 생성 파이프라인

### 6.1 입력 정보 수집
1. **기업 기본 정보**
   - 기업명, 대표자, 사업자등록번호
   - 소재지, 설립일, 업종
   - 조직 구성, 주요 연혁

2. **선택 사업 정보**
   - 사업명, 신청 분야
   - 지원 목적, 지원 규모

3. **사업 내용**
   - 사업 아이템 설명
   - 기술/서비스 차별성
   - 시장 분석 (시장 규모, 경쟁사, 타겟 고객)
   - 사업화 전략
   - 예상 성과 및 기대효과

4. **재무 계획**
   - 소요 예산 내역
   - 자부담/정부지원금 계획
   - 매출 계획

### 6.2 AI 생성 프로세스

```
1. 사용자 입력 수집
   ↓
2. 선택한 정부지원사업 템플릿 로드
   ↓
3. 입력 데이터 + 사업 정보를 AI 프롬프트로 구성
   ↓
4. Claude/GPT API 호출하여 각 섹션별 초안 생성
   - 사업 개요
   - 사업의 필요성
   - 사업 내용 및 추진 계획
   - 기대 효과 및 활용 방안
   - 예산 계획
   ↓
5. 생성된 텍스트를 사업계획서 템플릿에 자동 삽입
   ↓
6. 사용자 검토 및 수정 인터페이스 제공
   ↓
7. 최종 문서 생성 (PDF/HWP/DOCX)
```

### 6.3 템플릿 구조
- 각 정부 사업별 공식 양식을 기본으로 제공
- 공통 템플릿 (범용)
- 창업 지원사업 템플릿
- R&D 사업 템플릿
- 소상공인 지원사업 템플릿

### 6.4 AI 프롬프트 설계 원칙
- 사업의 목적과 평가 기준을 프롬프트에 반영
- 기업 강점과 차별성 부각
- 구체적 수치와 데이터 기반 서술
- 정부 사업 평가 항목에 맞춘 구조화

## 7. 시스템 아키텍처

### 7.1 백엔드
- Python (Flask/FastAPI)
- Celery (비동기 크롤링 작업)
- Redis (작업 큐, 캐싱)

### 7.2 크롤링
- Selenium (동적 페이지)
- BeautifulSoup4 (정적 페이지 파싱)
- Scrapy (대규모 크롤링)

### 7.3 데이터베이스
- PostgreSQL 또는 MySQL
- Redis (캐싱 및 세션)

### 7.4 AI/ML
- OpenAI API (GPT-4)
- Anthropic Claude API
- LangChain (프롬프트 체인 관리)

### 7.5 프론트엔드
- React.js 또는 Vue.js
- TailwindCSS

### 7.6 문서 생성
- python-docx (MS Word)
- reportlab (PDF)
- olefile/hwp 라이브러리 (한글 문서)

## 8. 개발 단계

### Phase 1: 기반 구축 (1-2주)
- 프로젝트 구조 설정
- 데이터베이스 스키마 구현
- 기본 크롤러 개발 (기업마당)
- 데이터 저장 및 파싱 로직

### Phase 2: 핵심 기능 구현 (2-3주)
- 크롤링 확장 (K-Startup, 소상공인24)
- 필터링 및 매칭 로직 구현
- 기업 정보 관리 기능
- 추천 알고리즘 구현

### Phase 3: AI 통합 (2주)
- AI API 연동
- 사업계획서 템플릿 설계
- 프롬프트 엔지니어링
- 문서 생성 파이프라인

### Phase 4: UI/UX 및 통합 (2주)
- 웹 인터페이스 개발
- 사용자 인증 및 권한 관리
- 문서 편집 인터페이스
- 종합 테스트

### Phase 5: 배포 및 최적화 (1주)
- 서버 배포
- 성능 최적화
- 모니터링 설정
- 사용자 피드백 수집 및 개선

## 9. 주요 고려사항

### 9.1 법적/윤리적 고려사항
- 크롤링 robots.txt 준수
- 개인정보 보호법 준수
- 저작권 관련 이슈
- API 이용 약관 준수

### 9.2 기술적 고려사항
- 크롤링 빈도 제한 (Rate Limiting)
- 에러 핸들링 및 로깅
- 데이터 검증 및 정제
- 확장성 있는 구조 설계

### 9.3 운영 고려사항
- 정기적인 데이터 업데이트 스케줄링
- 웹사이트 구조 변경 시 크롤러 업데이트
- AI 비용 관리
- 사용자 지원 및 문의 처리
