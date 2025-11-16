"""
K-Startup 크롤러
"""
import re
from typing import List, Dict, Optional
from datetime import datetime
from bs4 import BeautifulSoup
from .base_crawler import BaseCrawler


class KStartupCrawler(BaseCrawler):
    """K-Startup 크롤러"""

    def __init__(self):
        super().__init__(
            source_site='K-Startup',
            base_url='https://www.k-startup.go.kr',
            rate_limit=1.5
        )
        # 실제 K-Startup 사이트의 공고 목록 URL로 수정 필요
        self.list_url = f"{self.base_url}/common/announcement/list.do"

    def get_project_list_urls(self) -> List[str]:
        """프로젝트 목록 페이지 URL 리스트 반환"""
        urls = []
        # 최근 3페이지만 크롤링
        for page in range(1, 4):
            urls.append(f"{self.list_url}?page={page}")
        return urls

    def parse_project_list(self, soup: BeautifulSoup) -> List[Dict]:
        """프로젝트 목록 페이지 파싱"""
        projects = []

        try:
            # 실제 사이트 구조에 맞게 선택자 수정 필요
            items = soup.select('.board-list tr, .announce-list li')

            for item in items:
                try:
                    title_elem = item.select_one('.title a, .subject a')
                    if not title_elem:
                        continue

                    project_name = title_elem.get_text(strip=True)
                    detail_url = title_elem.get('href', '')

                    if detail_url and not detail_url.startswith('http'):
                        detail_url = self.base_url + detail_url

                    project_id = self._extract_id_from_url(detail_url)

                    # 기관명
                    agency_elem = item.select_one('.agency, .organ')
                    agency = agency_elem.get_text(strip=True) if agency_elem else 'K-Startup'

                    projects.append({
                        'id': project_id,
                        'project_name': project_name,
                        'agency': agency,
                        'detail_url': detail_url
                    })

                except Exception as e:
                    self.logger.warning(f"Error parsing item: {e}")

        except Exception as e:
            self.logger.error(f"Error parsing project list: {e}")

        return projects

    def parse_project_detail(self, soup: BeautifulSoup, project_url: str) -> Optional[Dict]:
        """프로젝트 상세 페이지 파싱"""
        try:
            detail_info = {'project_url': project_url}

            # 사업 개요
            summary_elem = soup.select_one('.content, .view-content, #content')
            if summary_elem:
                detail_info['summary'] = summary_elem.get_text(strip=True)

            # 지원 대상 - K-Startup은 주로 창업기업 대상
            detail_info['target_type'] = '초기창업'

            # 신청 기간
            period_elem = soup.select_one('.period, .date-info')
            if period_elem:
                period_text = period_elem.get_text(strip=True)
                start_date, end_date = self._extract_dates(period_text)
                detail_info['application_start_date'] = start_date
                detail_info['application_end_date'] = end_date

            # 문의처
            contact_elem = soup.select_one('.contact, .inquiry')
            if contact_elem:
                detail_info['contact_info'] = contact_elem.get_text(strip=True)

            return detail_info

        except Exception as e:
            self.logger.error(f"Error parsing detail: {e}")
            return None

    def _extract_id_from_url(self, url: str) -> str:
        """URL에서 프로젝트 ID 추출"""
        match = re.search(r'[?&](?:idx|id|no|annoId)=(\d+)', url)
        if match:
            return f"kstartup_{match.group(1)}"
        return f"kstartup_{abs(hash(url)) % 100000000}"

    def _extract_dates(self, text: str) -> tuple:
        """날짜 추출"""
        date_pattern = r'(\d{4})[.-](\d{1,2})[.-](\d{1,2})'
        matches = re.findall(date_pattern, text)

        start_date = None
        end_date = None

        if len(matches) >= 2:
            start_date = datetime(
                int(matches[0][0]),
                int(matches[0][1]),
                int(matches[0][2])
            ).date()
            end_date = datetime(
                int(matches[1][0]),
                int(matches[1][1]),
                int(matches[1][2])
            ).date()

        return start_date, end_date
