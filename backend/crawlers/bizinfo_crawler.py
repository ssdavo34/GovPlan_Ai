"""
기업마당(bizinfo.go.kr) 크롤러
"""
import re
from typing import List, Dict, Optional
from datetime import datetime
from bs4 import BeautifulSoup
from .base_crawler import BaseCrawler


class BizinfoCrawler(BaseCrawler):
    """기업마당 크롤러"""

    def __init__(self):
        super().__init__(
            source_site='기업마당',
            base_url='https://www.bizinfo.go.kr',
            rate_limit=1.5
        )
        self.list_url = f"{self.base_url}/web/lay1/bbs/S1T122C128/AS/list.do"

    def get_project_list_urls(self) -> List[str]:
        """
        크롤링할 프로젝트 목록 페이지 URL 리스트를 반환

        Returns:
            URL 리스트 (페이지네이션 포함)
        """
        # 최근 3페이지만 크롤링 (필요시 확장 가능)
        urls = []
        for page in range(1, 4):
            urls.append(f"{self.list_url}?page={page}")
        return urls

    def parse_project_list(self, soup: BeautifulSoup) -> List[Dict]:
        """
        프로젝트 목록 페이지를 파싱

        Args:
            soup: BeautifulSoup 객체

        Returns:
            프로젝트 기본 정보 리스트
        """
        projects = []

        # 주의: 실제 사이트 구조에 맞게 선택자를 수정해야 함
        # 아래는 일반적인 게시판 구조를 가정한 예시
        try:
            # 게시글 목록 테이블 또는 리스트 찾기
            # 예시: <table class="board-list"> 또는 <ul class="project-list">
            items = soup.select('.board-list tbody tr, .list-group-item, .project-item')

            for item in items:
                try:
                    # 제목과 링크 추출
                    title_elem = item.select_one('.subject a, .title a, h3 a')
                    if not title_elem:
                        continue

                    project_name = title_elem.get_text(strip=True)
                    detail_url = title_elem.get('href', '')

                    # 상대 경로를 절대 경로로 변환
                    if detail_url and not detail_url.startswith('http'):
                        detail_url = self.base_url + detail_url

                    # 공고번호 또는 고유 ID 추출
                    project_id = self._extract_id_from_url(detail_url)

                    # 기관명 추출
                    agency_elem = item.select_one('.agency, .organ, td:nth-of-type(2)')
                    agency = agency_elem.get_text(strip=True) if agency_elem else ''

                    # 접수기간 추출
                    date_elem = item.select_one('.date, .period, td:nth-of-type(3)')
                    date_text = date_elem.get_text(strip=True) if date_elem else ''

                    projects.append({
                        'id': project_id,
                        'project_name': project_name,
                        'agency': agency,
                        'detail_url': detail_url,
                        'date_text': date_text
                    })

                except Exception as e:
                    self.logger.warning(f"Error parsing project item: {e}")
                    continue

        except Exception as e:
            self.logger.error(f"Error parsing project list: {e}")

        return projects

    def parse_project_detail(self, soup: BeautifulSoup, project_url: str) -> Optional[Dict]:
        """
        프로젝트 상세 페이지를 파싱

        Args:
            soup: BeautifulSoup 객체
            project_url: 프로젝트 URL

        Returns:
            프로젝트 상세 정보
        """
        try:
            detail_info = {}

            # 사업 개요/목적
            summary_elem = soup.select_one('.summary, .overview, #bizPurpose')
            if summary_elem:
                detail_info['summary'] = summary_elem.get_text(strip=True)

            # 지원 내용 추출
            support_elem = soup.select_one('.support-info, #supportContent')
            if support_elem:
                support_text = support_elem.get_text(strip=True)
                detail_info['support_type'] = self._extract_support_type(support_text)
                detail_info['support_amount'] = self._extract_support_amount(support_text)

            # 신청 대상
            target_elem = soup.select_one('.target, #applyTarget')
            if target_elem:
                target_text = target_elem.get_text(strip=True)
                detail_info['target_requirements'] = target_text
                detail_info['target_type'] = self._extract_target_type(target_text)

            # 신청 기간 추출
            period_elem = soup.select_one('.apply-period, #applyPeriod')
            if period_elem:
                period_text = period_elem.get_text(strip=True)
                start_date, end_date = self._extract_dates(period_text)
                detail_info['application_start_date'] = start_date
                detail_info['application_end_date'] = end_date

            # 제출 서류
            docs_elem = soup.select_one('.required-docs, #requiredDocs')
            if docs_elem:
                detail_info['required_documents'] = docs_elem.get_text(strip=True)

            # 평가 기준
            eval_elem = soup.select_one('.evaluation, #evalCriteria')
            if eval_elem:
                detail_info['evaluation_criteria'] = eval_elem.get_text(strip=True)

            # 문의처
            contact_elem = soup.select_one('.contact, #contactInfo')
            if contact_elem:
                detail_info['contact_info'] = contact_elem.get_text(strip=True)

            # 첨부파일
            attachments = []
            attach_elems = soup.select('.attach-list a, .file-list a')
            for attach in attach_elems:
                file_name = attach.get_text(strip=True)
                file_url = attach.get('href', '')
                if file_url and not file_url.startswith('http'):
                    file_url = self.base_url + file_url
                attachments.append({'name': file_name, 'url': file_url})
            detail_info['attachments'] = attachments

            detail_info['project_url'] = project_url

            return detail_info

        except Exception as e:
            self.logger.error(f"Error parsing project detail: {e}")
            return None

    def _extract_id_from_url(self, url: str) -> str:
        """URL에서 프로젝트 ID 추출"""
        # 예: ?idx=123 또는 /view/123
        match = re.search(r'[?&](?:idx|id|no)=(\d+)', url)
        if match:
            return f"bizinfo_{match.group(1)}"

        match = re.search(r'/view/(\d+)', url)
        if match:
            return f"bizinfo_{match.group(1)}"

        # ID를 찾을 수 없으면 URL 해시 사용
        return f"bizinfo_{abs(hash(url)) % 100000000}"

    def _extract_support_type(self, text: str) -> str:
        """지원 유형 추출 (보조금, 융자, 바우처 등)"""
        if '보조금' in text or '지원금' in text:
            return '보조금'
        elif '융자' in text or '대출' in text:
            return '융자'
        elif '바우처' in text:
            return '바우처'
        elif '컨설팅' in text:
            return '컨설팅'
        return '기타'

    def _extract_support_amount(self, text: str) -> str:
        """지원금 규모 추출"""
        # 예: "최대 5,000만원", "1억원 이내"
        patterns = [
            r'(?:최대|최소|총|한도)\s*([\d,]+)\s*(?:만원|억원|천만원)',
            r'([\d,]+)\s*(?:만원|억원|천만원)\s*(?:이내|까지|지원)'
        ]

        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(0)

        return ''

    def _extract_target_type(self, text: str) -> str:
        """지원 대상 유형 추출"""
        if '예비창업' in text or '예비 창업' in text:
            return '예비창업'
        elif '초기창업' in text or '초기 창업' in text or '스타트업' in text:
            return '초기창업'
        elif '소상공인' in text:
            return '소상공인'
        elif '중소기업' in text or '중소 기업' in text:
            return '중소기업'
        elif 'R&D' in text or '연구개발' in text:
            return 'R&D'
        return '일반'

    def _extract_dates(self, text: str) -> tuple:
        """
        날짜 텍스트에서 시작일과 종료일 추출

        Returns:
            (start_date, end_date) 튜플
        """
        # 예: "2024-01-15 ~ 2024-02-15" 또는 "2024.01.15 - 2024.02.15"
        date_pattern = r'(\d{4})[.-](\d{1,2})[.-](\d{1,2})'
        matches = re.findall(date_pattern, text)

        start_date = None
        end_date = None

        if len(matches) >= 2:
            # 첫 번째 날짜: 시작일
            start_date = datetime(
                int(matches[0][0]),
                int(matches[0][1]),
                int(matches[0][2])
            ).date()

            # 두 번째 날짜: 종료일
            end_date = datetime(
                int(matches[1][0]),
                int(matches[1][1]),
                int(matches[1][2])
            ).date()

        return start_date, end_date
