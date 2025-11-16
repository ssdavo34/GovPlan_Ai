"""
기본 크롤러 클래스
모든 크롤러의 베이스가 되는 추상 클래스
"""
import time
import logging
from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Dict, Optional
import requests
from bs4 import BeautifulSoup


class BaseCrawler(ABC):
    """정부지원사업 크롤러 베이스 클래스"""

    def __init__(self, source_site: str, base_url: str, rate_limit: float = 1.0):
        """
        Args:
            source_site: 크롤링 대상 사이트 이름
            base_url: 기본 URL
            rate_limit: 요청 간 대기 시간(초)
        """
        self.source_site = source_site
        self.base_url = base_url
        self.rate_limit = rate_limit
        self.logger = logging.getLogger(f"{__name__}.{source_site}")
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })

    def fetch_page(self, url: str, params: Optional[Dict] = None, max_retries: int = 3) -> Optional[BeautifulSoup]:
        """
        웹 페이지를 가져와 BeautifulSoup 객체로 반환

        Args:
            url: 요청할 URL
            params: 쿼리 파라미터
            max_retries: 최대 재시도 횟수

        Returns:
            BeautifulSoup 객체 또는 None
        """
        for attempt in range(max_retries):
            try:
                response = self.session.get(url, params=params, timeout=30)
                response.raise_for_status()
                response.encoding = 'utf-8'

                # Rate limiting
                time.sleep(self.rate_limit)

                return BeautifulSoup(response.text, 'html.parser')

            except requests.exceptions.RequestException as e:
                self.logger.warning(f"Request failed (attempt {attempt + 1}/{max_retries}): {e}")
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
                else:
                    self.logger.error(f"Failed to fetch {url} after {max_retries} attempts")
                    return None

    @abstractmethod
    def get_project_list_urls(self) -> List[str]:
        """
        크롤링할 프로젝트 목록 페이지 URL 리스트를 반환
        각 사이트마다 구현 필요

        Returns:
            URL 리스트
        """
        pass

    @abstractmethod
    def parse_project_list(self, soup: BeautifulSoup) -> List[Dict]:
        """
        프로젝트 목록 페이지를 파싱하여 프로젝트 정보 리스트 반환

        Args:
            soup: BeautifulSoup 객체

        Returns:
            프로젝트 정보 딕셔너리 리스트
        """
        pass

    @abstractmethod
    def parse_project_detail(self, soup: BeautifulSoup, project_url: str) -> Optional[Dict]:
        """
        프로젝트 상세 페이지를 파싱하여 상세 정보 반환

        Args:
            soup: BeautifulSoup 객체
            project_url: 프로젝트 상세 페이지 URL

        Returns:
            프로젝트 상세 정보 딕셔너리
        """
        pass

    def crawl(self) -> List[Dict]:
        """
        크롤링 실행

        Returns:
            크롤링된 프로젝트 리스트
        """
        self.logger.info(f"Starting crawl for {self.source_site}")
        all_projects = []

        try:
            # 1. 프로젝트 목록 페이지 URL 가져오기
            list_urls = self.get_project_list_urls()
            self.logger.info(f"Found {len(list_urls)} list pages to crawl")

            # 2. 각 목록 페이지에서 프로젝트 리스트 파싱
            for list_url in list_urls:
                self.logger.info(f"Crawling list page: {list_url}")
                soup = self.fetch_page(list_url)

                if not soup:
                    self.logger.warning(f"Failed to fetch list page: {list_url}")
                    continue

                projects = self.parse_project_list(soup)
                self.logger.info(f"Found {len(projects)} projects on page")

                # 3. 각 프로젝트의 상세 페이지 크롤링
                for project in projects:
                    detail_url = project.get('detail_url')
                    if not detail_url:
                        continue

                    self.logger.debug(f"Crawling project detail: {detail_url}")
                    detail_soup = self.fetch_page(detail_url)

                    if not detail_soup:
                        self.logger.warning(f"Failed to fetch detail page: {detail_url}")
                        continue

                    # 상세 정보 파싱
                    detail_info = self.parse_project_detail(detail_soup, detail_url)
                    if detail_info:
                        # 기본 정보와 상세 정보 병합
                        project.update(detail_info)
                        project['source_site'] = self.source_site
                        project['last_crawled'] = datetime.utcnow()
                        all_projects.append(project)

            self.logger.info(f"Crawling completed. Total projects: {len(all_projects)}")
            return all_projects

        except Exception as e:
            self.logger.error(f"Error during crawling: {e}", exc_info=True)
            return all_projects

    def normalize_project_data(self, raw_data: Dict) -> Dict:
        """
        크롤링한 원시 데이터를 표준 포맷으로 변환

        Args:
            raw_data: 원시 데이터

        Returns:
            표준화된 데이터
        """
        return {
            'id': raw_data.get('id'),
            'project_name': raw_data.get('project_name', '').strip(),
            'agency': raw_data.get('agency', '').strip(),
            'project_url': raw_data.get('project_url', ''),
            'summary': raw_data.get('summary', ''),
            'support_type': raw_data.get('support_type', ''),
            'support_amount': raw_data.get('support_amount', ''),
            'target_type': raw_data.get('target_type', ''),
            'target_requirements': raw_data.get('target_requirements', ''),
            'industry_code': raw_data.get('industry_code', ''),
            'region': raw_data.get('region', ''),
            'application_start_date': raw_data.get('application_start_date'),
            'application_end_date': raw_data.get('application_end_date'),
            'required_documents': raw_data.get('required_documents', ''),
            'evaluation_criteria': raw_data.get('evaluation_criteria', ''),
            'fund_usage': raw_data.get('fund_usage', ''),
            'contact_info': raw_data.get('contact_info', ''),
            'attachments': raw_data.get('attachments', []),
            'source_site': self.source_site,
            'last_crawled': datetime.utcnow(),
            'status': 'active'
        }

    def close(self):
        """리소스 정리"""
        if self.session:
            self.session.close()

    def __enter__(self):
        """컨텍스트 매니저 진입"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """컨텍스트 매니저 종료"""
        self.close()
