"""
기업-공고 매칭 관련 API
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
import asyncpg
from datetime import datetime

from backend.core.database import get_db
from backend.services.matching_service import MatchingService


router = APIRouter()


@router.post("/calculate/{company_id}")
async def calculate_matching(
    company_id: int,
    min_score: float = Query(40.0, ge=0, le=100, description="최소 매칭 점수"),
    max_results: int = Query(20, ge=1, le=100, description="최대 결과 수"),
    conn: asyncpg.Connection = Depends(get_db)
):
    """
    기업-공고 매칭 점수 계산 및 저장

    특정 기업에 대해 모든 활성 공고와의 매칭 점수를 계산하고 데이터베이스에 저장합니다.

    - **company_id**: 기업 ID
    - **min_score**: 최소 매칭 점수 (기본값: 40.0)
    - **max_results**: 최대 결과 수 (기본값: 20)
    """

    # 기업 정보 조회
    company_query = """
        SELECT *
        FROM companies
        WHERE id = $1
    """
    company = await conn.fetchrow(company_query, company_id)

    if not company:
        raise HTTPException(status_code=404, detail="기업 정보를 찾을 수 없습니다")

    # 활성 공고 조회
    projects_query = """
        SELECT *
        FROM gov_support_projects
        WHERE status = 'active'
        ORDER BY application_end_date ASC
    """
    projects = await conn.fetch(projects_query)

    if not projects:
        return {
            "message": "매칭할 활성 공고가 없습니다",
            "company_id": company_id,
            "total_matched": 0,
            "matches": []
        }

    # 매칭 서비스 초기화
    matching_service = MatchingService()

    # 기업 정보를 딕셔너리로 변환
    company_info = dict(company)

    # 프로젝트 리스트를 딕셔너리 리스트로 변환
    project_list = [dict(p) for p in projects]

    # 매칭 계산
    try:
        matched_projects = matching_service.filter_projects(
            company=company_info,
            projects=project_list,
            min_score=min_score,
            max_results=max_results
        )

        # 매칭 결과를 데이터베이스에 저장
        saved_count = 0
        for match in matched_projects:
            # 기존 매칭 이력 확인
            existing = await conn.fetchval(
                """
                SELECT id FROM matching_history
                WHERE company_id = $1 AND project_id = $2
                """,
                company_id,
                match['project_id']
            )

            if existing:
                # 업데이트
                await conn.execute(
                    """
                    UPDATE matching_history
                    SET match_score = $1, match_reasons = $2, created_at = $3
                    WHERE company_id = $4 AND project_id = $5
                    """,
                    match['match_score'],
                    match['match_reasons'],
                    datetime.now(),
                    company_id,
                    match['project_id']
                )
            else:
                # 신규 삽입
                await conn.execute(
                    """
                    INSERT INTO matching_history (
                        company_id, project_id, match_score, match_reasons
                    ) VALUES ($1, $2, $3, $4)
                    """,
                    company_id,
                    match['project_id'],
                    match['match_score'],
                    match['match_reasons']
                )

            saved_count += 1

        # datetime 객체를 문자열로 변환
        for match in matched_projects:
            for key, value in match.items():
                if isinstance(value, datetime):
                    match[key] = value.isoformat()

        return {
            "message": f"{saved_count}개 공고의 매칭 점수가 계산되었습니다",
            "company_id": company_id,
            "company_name": company_info.get('company_name'),
            "total_matched": len(matched_projects),
            "min_score": min_score,
            "matches": matched_projects
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"매칭 계산 중 오류 발생: {str(e)}"
        )


@router.get("/history/{company_id}")
async def get_matching_history(
    company_id: int,
    min_score: Optional[float] = Query(None, description="최소 매칭 점수 필터"),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    conn: asyncpg.Connection = Depends(get_db)
):
    """
    기업의 매칭 이력 조회

    특정 기업의 과거 매칭 이력을 조회합니다.

    - **company_id**: 기업 ID
    - **min_score**: 최소 매칭 점수 (선택사항)
    - **skip**: 건너뛸 항목 수
    - **limit**: 가져올 항목 수
    """

    # 기업 존재 확인
    company = await conn.fetchrow(
        "SELECT id, company_name FROM companies WHERE id = $1",
        company_id
    )

    if not company:
        raise HTTPException(status_code=404, detail="기업 정보를 찾을 수 없습니다")

    # 쿼리 구성
    conditions = ["m.company_id = $1"]
    params = [company_id]
    param_count = 1

    if min_score is not None:
        param_count += 1
        conditions.append(f"m.match_score >= ${param_count}")
        params.append(min_score)

    where_clause = " AND ".join(conditions)

    # 매칭 이력 조회
    query = f"""
        SELECT
            m.id,
            m.company_id,
            m.project_id,
            m.match_score,
            m.match_reasons,
            m.is_bookmarked,
            m.is_applied,
            m.application_date,
            m.created_at,
            p.project_name,
            p.agency,
            p.support_type,
            p.support_amount,
            p.application_start_date,
            p.application_end_date,
            p.status as project_status
        FROM matching_history m
        JOIN gov_support_projects p ON m.project_id = p.id
        WHERE {where_clause}
        ORDER BY m.match_score DESC, m.created_at DESC
        LIMIT ${param_count + 1} OFFSET ${param_count + 2}
    """
    params.extend([limit, skip])

    rows = await conn.fetch(query, *params)

    # 전체 개수 조회
    count_query = f"""
        SELECT COUNT(*)
        FROM matching_history m
        WHERE {where_clause}
    """
    total = await conn.fetchval(count_query, *params[:param_count])

    history = []
    for row in rows:
        item = dict(row)
        # datetime 변환
        for key, value in item.items():
            if isinstance(value, datetime):
                item[key] = value.isoformat()
        history.append(item)

    return {
        "company_id": company_id,
        "company_name": company['company_name'],
        "total": total,
        "skip": skip,
        "limit": limit,
        "items": history
    }


@router.put("/history/{matching_id}/bookmark")
async def toggle_bookmark(
    matching_id: int,
    is_bookmarked: bool = Query(..., description="북마크 상태"),
    conn: asyncpg.Connection = Depends(get_db)
):
    """
    매칭 이력 북마크 설정/해제

    - **matching_id**: 매칭 이력 ID
    - **is_bookmarked**: 북마크 여부 (true/false)
    """

    result = await conn.execute(
        """
        UPDATE matching_history
        SET is_bookmarked = $1
        WHERE id = $2
        """,
        is_bookmarked,
        matching_id
    )

    if result == "UPDATE 0":
        raise HTTPException(status_code=404, detail="매칭 이력을 찾을 수 없습니다")

    return {
        "message": "북마크가 업데이트되었습니다",
        "matching_id": matching_id,
        "is_bookmarked": is_bookmarked
    }


@router.put("/history/{matching_id}/apply")
async def mark_as_applied(
    matching_id: int,
    is_applied: bool = Query(..., description="지원 여부"),
    application_date: Optional[str] = Query(None, description="지원일 (YYYY-MM-DD)"),
    conn: asyncpg.Connection = Depends(get_db)
):
    """
    매칭 이력에 지원 여부 표시

    - **matching_id**: 매칭 이력 ID
    - **is_applied**: 지원 여부 (true/false)
    - **application_date**: 지원일 (선택사항)
    """

    app_date = None
    if is_applied and application_date:
        try:
            app_date = datetime.fromisoformat(application_date).date()
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail="지원일 형식이 올바르지 않습니다 (YYYY-MM-DD)"
            )
    elif is_applied:
        app_date = datetime.now().date()

    result = await conn.execute(
        """
        UPDATE matching_history
        SET is_applied = $1, application_date = $2
        WHERE id = $3
        """,
        is_applied,
        app_date,
        matching_id
    )

    if result == "UPDATE 0":
        raise HTTPException(status_code=404, detail="매칭 이력을 찾을 수 없습니다")

    return {
        "message": "지원 상태가 업데이트되었습니다",
        "matching_id": matching_id,
        "is_applied": is_applied,
        "application_date": app_date.isoformat() if app_date else None
    }


@router.get("/stats/{company_id}")
async def get_matching_stats(
    company_id: int,
    conn: asyncpg.Connection = Depends(get_db)
):
    """
    기업 매칭 통계

    특정 기업의 매칭 통계 정보를 조회합니다.

    - 총 매칭 수
    - 평균 매칭 점수
    - 등급별 분포
    - 북마크/지원 현황
    """

    # 기업 존재 확인
    company = await conn.fetchrow(
        "SELECT id, company_name FROM companies WHERE id = $1",
        company_id
    )

    if not company:
        raise HTTPException(status_code=404, detail="기업 정보를 찾을 수 없습니다")

    # 통계 쿼리
    stats_query = """
        SELECT
            COUNT(*) as total_matches,
            AVG(match_score) as avg_score,
            COUNT(*) FILTER (WHERE match_score >= 80) as excellent_matches,
            COUNT(*) FILTER (WHERE match_score >= 60 AND match_score < 80) as good_matches,
            COUNT(*) FILTER (WHERE match_score >= 40 AND match_score < 60) as fair_matches,
            COUNT(*) FILTER (WHERE is_bookmarked = true) as bookmarked,
            COUNT(*) FILTER (WHERE is_applied = true) as applied
        FROM matching_history
        WHERE company_id = $1
    """

    stats = await conn.fetchrow(stats_query, company_id)

    # 최근 매칭 (상위 5개)
    recent_query = """
        SELECT
            m.match_score,
            p.project_name,
            p.agency,
            m.created_at
        FROM matching_history m
        JOIN gov_support_projects p ON m.project_id = p.id
        WHERE m.company_id = $1
        ORDER BY m.created_at DESC
        LIMIT 5
    """

    recent_matches = await conn.fetch(recent_query, company_id)

    recent_list = []
    for match in recent_matches:
        item = dict(match)
        if item.get('created_at'):
            item['created_at'] = item['created_at'].isoformat()
        recent_list.append(item)

    return {
        "company_id": company_id,
        "company_name": company['company_name'],
        "statistics": {
            "total_matches": stats['total_matches'],
            "average_score": round(float(stats['avg_score'] or 0), 2),
            "excellent_matches": stats['excellent_matches'],  # 80+
            "good_matches": stats['good_matches'],  # 60-79
            "fair_matches": stats['fair_matches'],  # 40-59
            "bookmarked": stats['bookmarked'],
            "applied": stats['applied']
        },
        "recent_matches": recent_list
    }


@router.delete("/history/{matching_id}")
async def delete_matching_history(
    matching_id: int,
    conn: asyncpg.Connection = Depends(get_db)
):
    """
    매칭 이력 삭제

    특정 매칭 이력을 삭제합니다.
    """

    result = await conn.execute(
        "DELETE FROM matching_history WHERE id = $1",
        matching_id
    )

    if result == "DELETE 0":
        raise HTTPException(status_code=404, detail="매칭 이력을 찾을 수 없습니다")

    return {
        "message": "매칭 이력이 삭제되었습니다",
        "matching_id": matching_id
    }
