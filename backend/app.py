"""
FastAPI 메인 애플리케이션
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from backend.core.config import settings
from backend.core.database import db_manager
from backend.api import projects, companies, proposals


@asynccontextmanager
async def lifespan(app: FastAPI):
    """애플리케이션 라이프사이클 관리"""
    # 시작 시
    print("=" * 60)
    print(f"{settings.app_name} v{settings.app_version} 시작")
    print("=" * 60)

    # 데이터베이스 연결
    await db_manager.connect()

    yield

    # 종료 시
    print("\n" + "=" * 60)
    print("애플리케이션 종료")
    print("=" * 60)

    # 데이터베이스 연결 종료
    await db_manager.disconnect()


# FastAPI 앱 생성
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="정부지원사업 공고 자동 수집 및 AI 기반 사업계획서 자동 작성 시스템",
    lifespan=lifespan
)

# CORS 미들웨어 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 라우터 등록
app.include_router(
    projects.router,
    prefix=f"{settings.api_prefix}/projects",
    tags=["projects"]
)

app.include_router(
    companies.router,
    prefix=f"{settings.api_prefix}/companies",
    tags=["companies"]
)

app.include_router(
    proposals.router,
    prefix=f"{settings.api_prefix}/proposals",
    tags=["proposals"]
)


@app.get("/")
async def root():
    """루트 엔드포인트"""
    return {
        "message": f"Welcome to {settings.app_name}",
        "version": settings.app_version,
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """헬스 체크 엔드포인트"""
    return {
        "status": "healthy",
        "app": settings.app_name,
        "version": settings.app_version
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "backend.app:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug
    )
