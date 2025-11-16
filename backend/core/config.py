"""
애플리케이션 설정
"""
import os
from typing import Optional
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """애플리케이션 설정"""

    # 애플리케이션 기본 설정
    app_name: str = "GovPlan_AI"
    app_version: str = "1.0.0"
    debug: bool = True
    api_prefix: str = "/api/v1"

    # 서버 설정
    host: str = "0.0.0.0"
    port: int = 8000

    # 데이터베이스 설정
    db_host: str = "localhost"
    db_port: int = 5432
    db_name: str = "govplan_ai"
    db_user: str = "postgres"
    db_password: str = "postgres"

    # Redis 설정
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0

    # AI API 설정
    anthropic_api_key: Optional[str] = None
    openai_api_key: Optional[str] = None

    # 크롤링 설정
    crawler_user_agent: str = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    crawler_delay: float = 1.0  # 요청 간 지연 시간 (초)
    crawler_timeout: int = 30  # 타임아웃 (초)
    crawler_max_retries: int = 3  # 최대 재시도 횟수

    # CORS 설정
    cors_origins: list = [
        "http://localhost:3000",
        "http://localhost:8000",
    ]

    # JWT 설정
    secret_key: str = "your-secret-key-change-this-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24  # 24시간

    # 로깅 설정
    log_level: str = "INFO"
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    @property
    def database_url(self) -> str:
        """데이터베이스 URL"""
        return f"postgresql://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"

    @property
    def async_database_url(self) -> str:
        """비동기 데이터베이스 URL"""
        return f"postgresql+asyncpg://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"

    @property
    def redis_url(self) -> str:
        """Redis URL"""
        return f"redis://{self.redis_host}:{self.redis_port}/{self.redis_db}"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """설정 싱글톤 인스턴스 반환"""
    return Settings()


# 전역 설정 인스턴스
settings = get_settings()
