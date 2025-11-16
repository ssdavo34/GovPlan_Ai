"""
FastAPI 메인 애플리케이션
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from contextlib import asynccontextmanager
from pathlib import Path

from backend.core.config import settings
from backend.core.database import db_manager
from backend.api import projects, companies, proposals, matching


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

# 정적 파일 및 템플릿 설정
BASE_DIR = Path(__file__).resolve().parent.parent
STATIC_DIR = BASE_DIR / "frontend" / "static"
TEMPLATES_DIR = BASE_DIR / "frontend" / "templates"

# 정적 파일 마운트
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

# 템플릿 설정
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))


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

app.include_router(
    matching.router,
    prefix=f"{settings.api_prefix}/matching",
    tags=["matching"]
)


@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    """대시보드 메인 페이지"""
    return templates.TemplateResponse(
        "index.html",
        {"request": request}
    )


@app.get("/projects", response_class=HTMLResponse)
async def projects_page(request: Request):
    """공고 검색 페이지"""
    return templates.TemplateResponse(
        "projects.html",
        {"request": request}
    )


@app.get("/matching", response_class=HTMLResponse)
async def matching_page(request: Request):
    """매칭 결과 페이지"""
    return templates.TemplateResponse(
        "matching.html",
        {"request": request}
    )


@app.get("/proposals", response_class=HTMLResponse)
async def proposals_page(request: Request):
    """사업계획서 관리 페이지"""
    return templates.TemplateResponse(
        "proposals.html",
        {"request": request}
    )


@app.get("/api")
async def api_root():
    """API 루트 엔드포인트"""
    return {
        "message": f"Welcome to {settings.app_name} API",
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
