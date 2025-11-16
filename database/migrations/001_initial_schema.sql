-- 정부지원사업 자동화 프로그램 초기 데이터베이스 스키마
-- PostgreSQL 기준 (MySQL 사용 시 일부 수정 필요)

-- 정부지원사업 테이블
CREATE TABLE IF NOT EXISTS gov_support_projects (
    id VARCHAR(50) PRIMARY KEY,
    project_name VARCHAR(500) NOT NULL,
    agency VARCHAR(200),
    project_url TEXT,
    summary TEXT,
    support_type VARCHAR(100),
    support_amount VARCHAR(200),
    target_type VARCHAR(200),
    target_requirements TEXT,
    industry_code VARCHAR(100),
    region VARCHAR(100),
    application_start_date DATE,
    application_end_date DATE,
    required_documents TEXT,
    evaluation_criteria TEXT,
    fund_usage TEXT,
    contact_info VARCHAR(500),
    attachments JSONB,
    source_site VARCHAR(100),
    last_crawled TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(50) DEFAULT 'active'
);

-- 인덱스 생성
CREATE INDEX idx_application_dates ON gov_support_projects(application_start_date, application_end_date);
CREATE INDEX idx_target_type ON gov_support_projects(target_type);
CREATE INDEX idx_industry_code ON gov_support_projects(industry_code);
CREATE INDEX idx_status ON gov_support_projects(status);
CREATE INDEX idx_source_site ON gov_support_projects(source_site);
CREATE INDEX idx_project_name ON gov_support_projects(project_name);

-- 기업 정보 테이블
CREATE TABLE IF NOT EXISTS companies (
    id SERIAL PRIMARY KEY,
    company_name VARCHAR(200) NOT NULL,
    business_number VARCHAR(50) UNIQUE,
    company_type VARCHAR(100),
    industry_code VARCHAR(100),
    industry_name VARCHAR(200),
    region VARCHAR(100),
    establishment_date DATE,
    employee_count INTEGER,
    annual_revenue BIGINT,
    certifications JSONB,
    technology_fields JSONB,
    funding_needs VARCHAR(500),
    preferred_support_types JSONB,
    user_id INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 인덱스 생성
CREATE INDEX idx_company_type ON companies(company_type);
CREATE INDEX idx_company_industry_code ON companies(industry_code);
CREATE INDEX idx_company_region ON companies(region);
CREATE INDEX idx_business_number ON companies(business_number);

-- 매칭 이력 테이블
CREATE TABLE IF NOT EXISTS matching_history (
    id SERIAL PRIMARY KEY,
    company_id INTEGER NOT NULL,
    project_id VARCHAR(50) NOT NULL,
    match_score DECIMAL(5,2),
    match_reasons JSONB,
    is_bookmarked BOOLEAN DEFAULT FALSE,
    is_applied BOOLEAN DEFAULT FALSE,
    application_date DATE,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (company_id) REFERENCES companies(id) ON DELETE CASCADE,
    FOREIGN KEY (project_id) REFERENCES gov_support_projects(id) ON DELETE CASCADE
);

-- 인덱스 생성
CREATE INDEX idx_company_project ON matching_history(company_id, project_id);
CREATE INDEX idx_match_score ON matching_history(match_score DESC);
CREATE INDEX idx_is_bookmarked ON matching_history(is_bookmarked);
CREATE INDEX idx_company_id ON matching_history(company_id);

-- 사업계획서 생성 이력 테이블
CREATE TABLE IF NOT EXISTS business_plan_history (
    id SERIAL PRIMARY KEY,
    company_id INTEGER NOT NULL,
    project_id VARCHAR(50),
    template_type VARCHAR(100),
    content JSONB,
    generated_file_path TEXT,
    status VARCHAR(50) DEFAULT 'draft',
    ai_model_used VARCHAR(100),
    generation_cost DECIMAL(10,4),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (company_id) REFERENCES companies(id) ON DELETE CASCADE,
    FOREIGN KEY (project_id) REFERENCES gov_support_projects(id) ON DELETE SET NULL
);

-- 인덱스 생성
CREATE INDEX idx_bp_company_id ON business_plan_history(company_id);
CREATE INDEX idx_bp_project_id ON business_plan_history(project_id);
CREATE INDEX idx_bp_status ON business_plan_history(status);

-- 크롤링 작업 로그 테이블
CREATE TABLE IF NOT EXISTS crawling_logs (
    id SERIAL PRIMARY KEY,
    source_site VARCHAR(100) NOT NULL,
    started_at TIMESTAMP NOT NULL,
    completed_at TIMESTAMP,
    status VARCHAR(50) DEFAULT 'running',
    projects_found INTEGER DEFAULT 0,
    projects_new INTEGER DEFAULT 0,
    projects_updated INTEGER DEFAULT 0,
    error_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 인덱스 생성
CREATE INDEX idx_crawl_source_site ON crawling_logs(source_site);
CREATE INDEX idx_crawl_status ON crawling_logs(status);
CREATE INDEX idx_crawl_started_at ON crawling_logs(started_at DESC);

-- 사용자 테이블 (추후 확장용)
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(200) UNIQUE NOT NULL,
    password_hash VARCHAR(255),
    name VARCHAR(100),
    role VARCHAR(50) DEFAULT 'user',
    is_active BOOLEAN DEFAULT TRUE,
    last_login TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 인덱스 생성
CREATE INDEX idx_user_email ON users(email);
CREATE INDEX idx_user_is_active ON users(is_active);

-- 키워드 테이블 (검색 및 필터링용)
CREATE TABLE IF NOT EXISTS keywords (
    id SERIAL PRIMARY KEY,
    keyword VARCHAR(200) NOT NULL,
    category VARCHAR(100),
    project_id VARCHAR(50),

    FOREIGN KEY (project_id) REFERENCES gov_support_projects(id) ON DELETE CASCADE
);

-- 인덱스 생성
CREATE INDEX idx_keyword ON keywords(keyword);
CREATE INDEX idx_keyword_category ON keywords(category);
CREATE INDEX idx_keyword_project_id ON keywords(project_id);

-- 업데이트 타임스탬프 자동 갱신을 위한 함수 (PostgreSQL)
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- 트리거 생성
CREATE TRIGGER update_gov_support_projects_updated_at BEFORE UPDATE ON gov_support_projects
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_companies_updated_at BEFORE UPDATE ON companies
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_matching_history_updated_at BEFORE UPDATE ON matching_history
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_business_plan_history_updated_at BEFORE UPDATE ON business_plan_history
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- 초기 데이터 (예제)
COMMENT ON TABLE gov_support_projects IS '정부지원사업 정보를 저장하는 테이블';
COMMENT ON TABLE companies IS '기업 정보를 저장하는 테이블';
COMMENT ON TABLE matching_history IS '기업과 지원사업 매칭 이력을 저장하는 테이블';
COMMENT ON TABLE business_plan_history IS 'AI로 생성된 사업계획서 이력을 저장하는 테이블';
COMMENT ON TABLE crawling_logs IS '크롤링 작업 로그를 저장하는 테이블';
