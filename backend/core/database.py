"""
데이터베이스 연결 관리
"""
import asyncpg
from typing import Optional
from contextlib import asynccontextmanager
from backend.core.config import settings


class DatabaseManager:
    """데이터베이스 연결 관리자"""

    def __init__(self):
        self.pool: Optional[asyncpg.Pool] = None

    async def connect(self):
        """데이터베이스 연결 풀 생성"""
        if self.pool is None:
            self.pool = await asyncpg.create_pool(
                host=settings.db_host,
                port=settings.db_port,
                database=settings.db_name,
                user=settings.db_user,
                password=settings.db_password,
                min_size=5,
                max_size=20,
                command_timeout=60
            )
            print(f"✓ 데이터베이스 연결 풀 생성 완료")

    async def disconnect(self):
        """데이터베이스 연결 풀 종료"""
        if self.pool is not None:
            await self.pool.close()
            self.pool = None
            print("✓ 데이터베이스 연결 풀 종료")

    @asynccontextmanager
    async def get_connection(self):
        """데이터베이스 연결 컨텍스트 매니저"""
        if self.pool is None:
            await self.connect()

        async with self.pool.acquire() as connection:
            yield connection

    async def execute(self, query: str, *args):
        """쿼리 실행"""
        async with self.get_connection() as conn:
            return await conn.execute(query, *args)

    async def fetch(self, query: str, *args):
        """쿼리 실행 및 결과 반환"""
        async with self.get_connection() as conn:
            return await conn.fetch(query, *args)

    async def fetchrow(self, query: str, *args):
        """쿼리 실행 및 단일 행 반환"""
        async with self.get_connection() as conn:
            return await conn.fetchrow(query, *args)

    async def fetchval(self, query: str, *args):
        """쿼리 실행 및 단일 값 반환"""
        async with self.get_connection() as conn:
            return await conn.fetchval(query, *args)


# 전역 데이터베이스 매니저 인스턴스
db_manager = DatabaseManager()


async def get_db():
    """데이터베이스 의존성 (FastAPI에서 사용)"""
    if db_manager.pool is None:
        await db_manager.connect()

    async with db_manager.get_connection() as conn:
        yield conn
