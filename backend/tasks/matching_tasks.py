"""
매칭 관련 Celery 작업
"""
import asyncio
from datetime import datetime
from backend.celery_app import celery_app
from backend.services.matching_service import MatchingService
from backend.core.config import settings


@celery_app.task(name='backend.tasks.matching_tasks.calculate_matching_for_company')
def calculate_matching_for_company(company_id: int, min_score: float = 40.0):
    """
    특정 기업의 매칭 점수 계산

    Args:
        company_id: 기업 ID
        min_score: 최소 매칭 점수
    """

    async def _calculate():
        import asyncpg

        db_config = {
            "host": settings.db_host,
            "port": settings.db_port,
            "database": settings.db_name,
            "user": settings.db_user,
            "password": settings.db_password
        }

        conn = await asyncpg.connect(**db_config)

        # 기업 정보 조회
        company_query = "SELECT * FROM companies WHERE id = $1"
        company = await conn.fetchrow(company_query, company_id)

        if not company:
            await conn.close()
            raise ValueError(f"기업 ID {company_id}를 찾을 수 없습니다")

        # 활성 공고 조회
        projects_query = """
            SELECT * FROM gov_support_projects
            WHERE status = 'active'
        """
        projects = await conn.fetch(projects_query)

        # 매칭 서비스
        matching_service = MatchingService()

        company_info = dict(company)
        project_list = [dict(p) for p in projects]

        # 매칭 계산
        matched_projects = matching_service.filter_projects(
            company=company_info,
            projects=project_list,
            min_score=min_score,
            max_results=100
        )

        # 데이터베이스에 저장
        saved_count = 0
        for match in matched_projects:
            # 기존 매칭 확인
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

        await conn.close()

        return {
            "company_id": company_id,
            "total_matched": len(matched_projects),
            "saved": saved_count,
            "timestamp": datetime.now().isoformat()
        }

    result = asyncio.run(_calculate())
    return result


@celery_app.task(name='backend.tasks.matching_tasks.recalculate_all_matching_scores')
def recalculate_all_matching_scores(min_score: float = 40.0):
    """
    모든 기업의 매칭 점수 재계산

    Args:
        min_score: 최소 매칭 점수
    """

    async def _recalculate():
        import asyncpg

        db_config = {
            "host": settings.db_host,
            "port": settings.db_port,
            "database": settings.db_name,
            "user": settings.db_user,
            "password": settings.db_password
        }

        conn = await asyncpg.connect(**db_config)

        # 모든 기업 조회
        companies_query = "SELECT id FROM companies"
        companies = await conn.fetch(companies_query)

        await conn.close()

        results = []
        for company in companies:
            try:
                # 비동기 작업 시작
                result = calculate_matching_for_company.delay(company['id'], min_score)
                results.append({
                    "company_id": company['id'],
                    "task_id": result.id,
                    "status": "started"
                })
            except Exception as e:
                results.append({
                    "company_id": company['id'],
                    "status": "failed",
                    "error": str(e)
                })

        return {
            "total_companies": len(companies),
            "results": results,
            "timestamp": datetime.now().isoformat()
        }

    result = asyncio.run(_recalculate())
    return result
