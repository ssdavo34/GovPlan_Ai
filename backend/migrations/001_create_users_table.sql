-- 사용자 테이블 생성
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    is_active BOOLEAN DEFAULT TRUE,
    is_superuser BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP
);

-- 이메일 인덱스
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);

-- 활성 사용자 인덱스
CREATE INDEX IF NOT EXISTS idx_users_is_active ON users(is_active);

-- 기본 슈퍼유저 생성 (비밀번호: admin123)
-- bcrypt 해시: $2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYRqL5W8.zG
INSERT INTO users (email, hashed_password, full_name, is_active, is_superuser)
VALUES (
    'admin@govplan.ai',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYRqL5W8.zG',
    'System Administrator',
    TRUE,
    TRUE
)
ON CONFLICT (email) DO NOTHING;

-- 테스트 사용자 생성 (비밀번호: testuser123)
-- bcrypt 해시: $2b$12$vBLcmKiU4IbL3j3XqRHzUOXHE.YqL8qVZYQk/YdVZqL5W8.zG
INSERT INTO users (email, hashed_password, full_name, is_active, is_superuser)
VALUES (
    'test@govplan.ai',
    '$2b$12$vBLcmKiU4IbL3j3XqRHzUOXHE.YqL8qVZYQk/YdVZqL5W8.zG',
    'Test User',
    TRUE,
    FALSE
)
ON CONFLICT (email) DO NOTHING;
