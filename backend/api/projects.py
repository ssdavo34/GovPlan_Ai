"""
정부지원사업 공고 관련 API
"""
from fastapi import APIRouter, Depends, Query, HTTPException
from typing import List, Optional
import asyncpg
from datetime import datetime

from backend.core.database import get_db
from backend.models.project import GovSupportProject


router = APIRouter()


@router.get("/", response_model=List[dict])
async def get_projects(
    skip: int = Query(0, ge=0, description="건너뛸 항목 수"),
    limit: int = Query(20, ge=1, le=100, description="가져올 항목 수"),
    search: Optional[str] = Query(None, description="검색어"),
    category: Optional[str] = Query(None, description="카테고리 필터"),
    region: Optional[str] = Query(None, description="지역 필터"),
    status: str = Query("active", description="상태 필터 (active/closed/expired)"),
    conn: asyncpg.Connection = Depends(get_db)
):
    """
    정부지원사업 공고 목록 조회

    - **skip**: 건너뛸 항목 수 (페이지네이션)
    - **limit**: 가져올 항목 수 (최대 100)
    - **search**: 제목 또는 내용에서 검색
    - **category**: 지원 분야 필터
    - **region**: 지역 필터
    - **status**: active(진행중), closed(마감), expired(종료)
    """

    # 쿼리 구성
    conditions = ["status = $1"]
    params = [status]
    param_count = 1

    # 검색어 필터
    if search:
        param_count += 1
        conditions.append(f"(project_name ILIKE ${param_count} OR summary ILIKE ${param_count})")
        params.append(f"%{search}%")

    # 카테고리 필터
    if category:
        param_count += 1
        conditions.append(f"support_type = ${param_count}")
        params.append(category)

    # 지역 필터
    if region:
        param_count += 1
        conditions.append(f"region = ${param_count}")
        params.append(region)

    where_clause = " AND ".join(conditions)

    # 전체 개수 조회
    count_query = f"""
        SELECT COUNT(*)
        FROM gov_support_projects
        WHERE {where_clause}
    """
    total = await conn.fetchval(count_query, *params)

    # 데이터 조회
    query = f"""
        SELECT
            id, project_name, agency, project_url, summary,
            support_type, support_amount, target_type, target_requirements,
            industry_code, region,
            application_start_date, application_end_date,
            required_documents, evaluation_criteria,
            source_site, last_crawled, created_at, status
        FROM gov_support_projects
        WHERE {where_clause}
        ORDER BY application_end_date ASC, created_at DESC
        LIMIT ${param_count + 1} OFFSET ${param_count + 2}
    """
    params.extend([limit, skip])

    rows = await conn.fetch(query, *params)

    projects = []
    for row in rows:
        project = dict(row)
        # datetime을 문자열로 변환
        for key in ['application_start_date', 'application_end_date', 'last_crawled', 'created_at']:
            if project.get(key):
                project[key] = project[key].isoformat()
        projects.append(project)

    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "items": projects
    }


@router.get("/{project_id}", response_model=dict)
async def get_project(
    project_id: str,
    conn: asyncpg.Connection = Depends(get_db)
):
    """
    특정 공고 상세 정보 조회

    - **project_id**: 공고 고유 ID
    """

    query = """
        SELECT *
        FROM gov_support_projects
        WHERE id = $1
    """

    row = await conn.fetchrow(query, project_id)

    if not row:
        raise HTTPException(status_code=404, detail="공고를 찾을 수 없습니다")

    project = dict(row)

    # datetime을 문자열로 변환
    for key, value in project.items():
        if isinstance(value, datetime):
            project[key] = value.isoformat()

    return project


@router.get("/stats/summary")
async def get_project_stats(
    conn: asyncpg.Connection = Depends(get_db)
):
    """
    공고 통계 정보

    - 전체 공고 수
    - 진행중인 공고 수
    - 지원 분야별 통계
    - 지역별 통계
    """

    # 전체 통계
    total_query = """
        SELECT
            COUNT(*) as total,
            COUNT(*) FILTER (WHERE status = 'active') as active,
            COUNT(*) FILTER (WHERE status = 'closed') as closed
        FROM gov_support_projects
    """
    total_stats = await conn.fetchrow(total_query)

    # 지원 분야별 통계
    category_query = """
        SELECT support_type, COUNT(*) as count
        FROM gov_support_projects
        WHERE status = 'active' AND support_type IS NOT NULL
        GROUP BY support_type
        ORDER BY count DESC
        LIMIT 10
    """
    category_stats = await conn.fetch(category_query)

    # 지역별 통계
    region_query = """
        SELECT region, COUNT(*) as count
        FROM gov_support_projects
        WHERE status = 'active' AND region IS NOT NULL
        GROUP BY region
        ORDER BY count DESC
        LIMIT 10
    """
    region_stats = await conn.fetch(region_query)

    return {
        "total": dict(total_stats),
        "by_category": [dict(row) for row in category_stats],
        "by_region": [dict(row) for row in region_stats]
    }


@router.post("/refresh")
async def refresh_projects(
    site: Optional[str] = Query(None, description="크롤링할 사이트 (bizinfo/kstartup)"),
    conn: asyncpg.Connection = Depends(get_db)
):
    """
    공고 정보 새로고침 (크롤링 트리거)

    - **site**: 특정 사이트만 크롤링 (없으면 전체)
    """

    # 실제 구현에서는 Celery 등의 비동기 작업 큐를 사용
    # 여기서는 간단히 응답만 반환
    return {
        "message": "크롤링 작업이 백그라운드에서 시작되었습니다",
        "site": site or "all"
    }
