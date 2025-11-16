"""
크롤링 서비스
"""
import logging
from datetime import datetime
from typing import List, Dict, Optional
from ..crawlers import BizinfoCrawler, KStartupCrawler


class CrawlerService:
    """크롤링 작업을 관리하는 서비스"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.crawlers = {
            '기업마당': BizinfoCrawler,
            'K-Startup': KStartupCrawler,
        }

    def crawl_site(self, site_name: str) -> Dict:
        """
        특정 사이트 크롤링 실행

        Args:
            site_name: 크롤링할 사이트 이름

        Returns:
            크롤링 결과 딕셔너리
        """
        if site_name not in self.crawlers:
            raise ValueError(f"Unknown site: {site_name}. Available sites: {list(self.crawlers.keys())}")

        self.logger.info(f"Starting crawl for {site_name}")
        started_at = datetime.utcnow()

        try:
            crawler_class = self.crawlers[site_name]
            with crawler_class() as crawler:
                projects = crawler.crawl()

            completed_at = datetime.utcnow()
            duration = (completed_at - started_at).total_seconds()

            result = {
                'site_name': site_name,
                'status': 'completed',
                'started_at': started_at,
                'completed_at': completed_at,
                'duration_seconds': duration,
                'projects_found': len(projects),
                'projects': projects,
                'error_message': None
            }

            self.logger.info(
                f"Crawl completed for {site_name}. "
                f"Found {len(projects)} projects in {duration:.2f} seconds"
            )

            return result

        except Exception as e:
            completed_at = datetime.utcnow()
            duration = (completed_at - started_at).total_seconds()

            error_msg = f"Error crawling {site_name}: {str(e)}"
            self.logger.error(error_msg, exc_info=True)

            result = {
                'site_name': site_name,
                'status': 'failed',
                'started_at': started_at,
                'completed_at': completed_at,
                'duration_seconds': duration,
                'projects_found': 0,
                'projects': [],
                'error_message': error_msg
            }

            return result

    def crawl_all_sites(self) -> List[Dict]:
        """
        모든 등록된 사이트 크롤링 실행

        Returns:
            각 사이트별 크롤링 결과 리스트
        """
        results = []

        for site_name in self.crawlers.keys():
            result = self.crawl_site(site_name)
            results.append(result)

        total_projects = sum(r['projects_found'] for r in results)
        self.logger.info(f"All crawls completed. Total projects found: {total_projects}")

        return results

    def get_available_sites(self) -> List[str]:
        """사용 가능한 크롤링 사이트 목록 반환"""
        return list(self.crawlers.keys())

    def save_projects_to_db(self, projects: List[Dict], db_session):
        """
        크롤링한 프로젝트를 데이터베이스에 저장

        Args:
            projects: 프로젝트 리스트
            db_session: 데이터베이스 세션

        Returns:
            저장 통계 딕셔너리
        """
        from ..models import GovSupportProject

        stats = {
            'total': len(projects),
            'new': 0,
            'updated': 0,
            'skipped': 0
        }

        for project_data in projects:
            try:
                project_id = project_data.get('id')
                if not project_id:
                    self.logger.warning("Project without ID, skipping")
                    stats['skipped'] += 1
                    continue

                # 기존 프로젝트 확인
                existing = db_session.query(GovSupportProject).filter_by(id=project_id).first()

                if existing:
                    # 업데이트
                    for key, value in project_data.items():
                        if hasattr(existing, key):
                            setattr(existing, key, value)
                    stats['updated'] += 1
                else:
                    # 새로 추가
                    new_project = GovSupportProject(**project_data)
                    db_session.add(new_project)
                    stats['new'] += 1

            except Exception as e:
                self.logger.error(f"Error saving project {project_data.get('id')}: {e}")
                stats['skipped'] += 1

        db_session.commit()
        self.logger.info(
            f"Saved projects - New: {stats['new']}, "
            f"Updated: {stats['updated']}, "
            f"Skipped: {stats['skipped']}"
        )

        return stats
