"""
크롤러 관련 Celery 작업
"""
import asyncio
from datetime import datetime, timedelta
from backend.celery_app import celery_app
from backend.crawlers.bizinfo_crawler import BizinfoCrawler
from backend.crawlers.kstartup_crawler import KStartupCrawler
from backend.services.crawler_service import CrawlerService
from backend.core.config import settings


@celery_app.task(name='backend.tasks.crawler_tasks.crawl_site')
def crawl_site(site_name: str, max_pages: int = 5):
    """
    특정 사이트 크롤링

    Args:
        site_name: 사이트 이름 (bizinfo, kstartup)
        max_pages: 최대 페이지 수
    """

    async def _crawl():
        # 크롤러 선택
        if site_name == 'bizinfo':
            crawler = BizinfoCrawler()
        elif site_name == 'kstartup':
            crawler = KStartupCrawler()
        else:
            raise ValueError(f"알 수 없는 사이트: {site_name}")

        # 크롤링 실행
        projects = await crawler.crawl(max_pages=max_pages)

        # 데이터베이스 저장
        db_config = {
            "host": settings.db_host,
            "port": settings.db_port,
            "database": settings.db_name,
            "user": settings.db_user,
            "password": settings.db_password
        }

        crawler_service = CrawlerService(db_config)
        await crawler_service.connect()

        saved_count = await crawler_service.save_projects(projects, site_name)

        await crawler_service.close()

        return {
            "site": site_name,
            "crawled": len(projects),
            "saved": saved_count,
            "timestamp": datetime.now().isoformat()
        }

    # asyncio 이벤트 루프 실행
    result = asyncio.run(_crawl())
    return result


@celery_app.task(name='backend.tasks.crawler_tasks.crawl_all_sites')
def crawl_all_sites(max_pages: int = 5):
    """
    모든 사이트 크롤링

    Args:
        max_pages: 각 사이트별 최대 페이지 수
    """

    sites = ['bizinfo', 'kstartup']
    results = []

    for site in sites:
        try:
            result = crawl_site.delay(site, max_pages)
            results.append({
                "site": site,
                "task_id": result.id,
                "status": "started"
            })
        except Exception as e:
            results.append({
                "site": site,
                "status": "failed",
                "error": str(e)
            })

    return {
        "total_sites": len(sites),
        "results": results,
        "timestamp": datetime.now().isoformat()
    }


@celery_app.task(name='backend.tasks.crawler_tasks.update_expired_projects')
def update_expired_projects():
    """
    만료된 공고 상태 업데이트

    신청 마감일이 지난 공고의 상태를 'expired'로 업데이트합니다.
    """

    async def _update():
        db_config = {
            "host": settings.db_host,
            "port": settings.db_port,
            "database": settings.db_name,
            "user": settings.db_user,
            "password": settings.db_password
        }

        import asyncpg

        conn = await asyncpg.connect(
            host=db_config['host'],
            port=db_config['port'],
            database=db_config['database'],
            user=db_config['user'],
            password=db_config['password']
        )

        # 마감일이 지난 공고 업데이트
        query = """
            UPDATE gov_support_projects
            SET status = 'expired'
            WHERE status = 'active'
            AND application_end_date < $1
        """

        result = await conn.execute(query, datetime.now().date())

        await conn.close()

        # 업데이트된 개수 추출
        updated_count = int(result.split()[-1]) if result else 0

        return {
            "updated": updated_count,
            "timestamp": datetime.now().isoformat()
        }

    result = asyncio.run(_update())
    return result


@celery_app.task(name='backend.tasks.crawler_tasks.cleanup_old_crawling_history')
def cleanup_old_crawling_history(days: int = 90):
    """
    오래된 크롤링 이력 정리

    Args:
        days: 보관 기간 (일)
    """

    async def _cleanup():
        db_config = {
            "host": settings.db_host,
            "port": settings.db_port,
            "database": settings.db_name,
            "user": settings.db_user,
            "password": settings.db_password
        }

        import asyncpg

        conn = await asyncpg.connect(
            host=db_config['host'],
            port=db_config['port'],
            database=db_config['database'],
            user=db_config['user'],
            password=db_config['password']
        )

        # 오래된 크롤링 이력 삭제
        cutoff_date = datetime.now() - timedelta(days=days)

        query = """
            DELETE FROM crawling_history
            WHERE crawled_at < $1
        """

        result = await conn.execute(query, cutoff_date)

        await conn.close()

        deleted_count = int(result.split()[-1]) if result else 0

        return {
            "deleted": deleted_count,
            "cutoff_date": cutoff_date.isoformat(),
            "timestamp": datetime.now().isoformat()
        }

    result = asyncio.run(_cleanup())
    return result
