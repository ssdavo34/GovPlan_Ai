#!/usr/bin/env python
"""
데이터베이스 초기화 스크립트
"""
import sys
import os
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import asyncio
import asyncpg
from typing import Optional


async def read_sql_file(file_path: str) -> str:
    """SQL 파일을 읽어 문자열로 반환"""
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()


async def init_database(
    host: str = "localhost",
    port: int = 5432,
    database: str = "govplan_ai",
    user: str = "postgres",
    password: str = "postgres"
):
    """데이터베이스 초기화"""

    print(f"데이터베이스 연결 중: {host}:{port}/{database}")

    try:
        # PostgreSQL 연결
        conn = await asyncpg.connect(
            host=host,
            port=port,
            database=database,
            user=user,
            password=password
        )

        print("✓ 데이터베이스 연결 성공")

        # 마이그레이션 파일 경로
        migration_file = project_root / "database" / "migrations" / "001_initial_schema.sql"

        if not migration_file.exists():
            print(f"❌ 마이그레이션 파일을 찾을 수 없습니다: {migration_file}")
            return

        print(f"마이그레이션 실행 중: {migration_file.name}")

        # SQL 파일 읽기
        sql = await read_sql_file(str(migration_file))

        # SQL 실행
        await conn.execute(sql)

        print("✓ 마이그레이션 완료")

        # 테이블 확인
        tables = await conn.fetch("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public'
            ORDER BY table_name
        """)

        print("\n생성된 테이블 목록:")
        for table in tables:
            print(f"  - {table['table_name']}")

        await conn.close()
        print("\n✓ 데이터베이스 초기화 완료!")

    except asyncpg.InvalidCatalogNameError:
        print(f"❌ 데이터베이스 '{database}'가 존재하지 않습니다.")
        print(f"다음 명령어로 데이터베이스를 먼저 생성하세요:")
        print(f"  CREATE DATABASE {database};")
    except asyncpg.PostgresError as e:
        print(f"❌ PostgreSQL 오류: {e}")
    except Exception as e:
        print(f"❌ 오류 발생: {e}")


async def create_database(
    host: str = "localhost",
    port: int = 5432,
    database: str = "govplan_ai",
    user: str = "postgres",
    password: str = "postgres"
):
    """데이터베이스 생성 (존재하지 않는 경우)"""

    try:
        # postgres 데이터베이스에 연결
        conn = await asyncpg.connect(
            host=host,
            port=port,
            database="postgres",
            user=user,
            password=password
        )

        # 데이터베이스 존재 여부 확인
        exists = await conn.fetchval(
            "SELECT 1 FROM pg_database WHERE datname = $1",
            database
        )

        if exists:
            print(f"데이터베이스 '{database}'가 이미 존재합니다.")
        else:
            # 데이터베이스 생성
            await conn.execute(f'CREATE DATABASE {database}')
            print(f"✓ 데이터베이스 '{database}' 생성 완료")

        await conn.close()

    except Exception as e:
        print(f"❌ 데이터베이스 생성 오류: {e}")
        raise


async def main():
    """메인 함수"""

    # 환경 변수에서 설정 읽기
    host = os.getenv("DB_HOST", "localhost")
    port = int(os.getenv("DB_PORT", "5432"))
    database = os.getenv("DB_NAME", "govplan_ai")
    user = os.getenv("DB_USER", "postgres")
    password = os.getenv("DB_PASSWORD", "postgres")

    print("=" * 60)
    print("GovPlan_AI 데이터베이스 초기화")
    print("=" * 60)
    print()

    # 1. 데이터베이스 생성
    await create_database(host, port, database, user, password)

    # 2. 스키마 초기화
    await init_database(host, port, database, user, password)

    print()
    print("=" * 60)
    print("초기화 작업이 모두 완료되었습니다!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
