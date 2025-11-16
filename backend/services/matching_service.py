"""
기업-지원사업 매칭 서비스
"""
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import logging


class MatchingService:
    """기업 정보와 정부지원사업을 매칭하는 서비스"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def calculate_match_score(self, company: Dict, project: Dict) -> Dict:
        """
        기업과 프로젝트 간의 매칭 점수 계산

        Args:
            company: 기업 정보 딕셔너리
            project: 프로젝트 정보 딕셔너리

        Returns:
            {'score': float, 'reasons': dict} 형태의 매칭 결과
        """
        score = 0.0
        reasons = {}

        # 1. 업종 일치도 (40점)
        industry_score = self._calculate_industry_match(
            company.get('industry_code'),
            project.get('industry_code')
        )
        score += industry_score
        reasons['industry_match'] = industry_score

        # 2. 신청 기간 적합성 (20점)
        date_score = self._calculate_date_match(
            project.get('application_end_date')
        )
        score += date_score
        reasons['date_match'] = date_score

        # 3. 자금 규모 적합성 (20점)
        funding_score = self._calculate_funding_match(
            company.get('funding_needs'),
            project.get('support_amount')
        )
        score += funding_score
        reasons['funding_match'] = funding_score

        # 4. 인증/자격 요건 (10점)
        cert_score = self._calculate_certification_match(
            company.get('certifications', []),
            project.get('target_requirements', '')
        )
        score += cert_score
        reasons['certification_match'] = cert_score

        # 5. 지역 적합성 (10점)
        region_score = self._calculate_region_match(
            company.get('region'),
            project.get('region')
        )
        score += region_score
        reasons['region_match'] = region_score

        return {
            'score': round(score, 2),
            'reasons': reasons
        }

    def _calculate_industry_match(self, company_code: Optional[str], project_code: Optional[str]) -> float:
        """
        업종 일치도 계산 (최대 40점)

        KSIC 코드 기준:
        - 완전 일치 (세분류): 40점
        - 소분류 일치: 30점
        - 중분류 일치: 20점
        - 대분류 일치: 10점
        - 불일치: 0점
        """
        if not company_code or not project_code:
            return 0.0

        # 프로젝트가 전체 업종 대상인 경우
        if project_code.lower() in ['전체', 'all', '제한없음']:
            return 30.0

        # 코드 정규화 (공백 제거, 대문자 변환)
        company_code = company_code.strip().upper()
        project_code = project_code.strip().upper()

        # 완전 일치
        if company_code == project_code:
            return 40.0

        # 부분 일치 확인
        min_len = min(len(company_code), len(project_code))

        for i in range(min_len, 0, -1):
            if company_code[:i] == project_code[:i]:
                if i >= 4:  # 세분류 일치
                    return 40.0
                elif i == 3:  # 소분류 일치
                    return 30.0
                elif i == 2:  # 중분류 일치
                    return 20.0
                elif i == 1:  # 대분류 일치
                    return 10.0

        return 0.0

    def _calculate_date_match(self, end_date) -> float:
        """
        신청 기간 적합성 계산 (최대 20점)

        - 마감까지 1개월 이상: 20점
        - 마감까지 2주~1개월: 15점
        - 마감까지 2주 미만: 10점
        - 마감 지남: 0점
        """
        if not end_date:
            return 0.0

        # datetime.date 객체가 아닌 경우 변환
        if isinstance(end_date, str):
            try:
                end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
            except:
                return 0.0

        today = datetime.now().date()
        days_left = (end_date - today).days

        if days_left < 0:
            return 0.0
        elif days_left >= 30:
            return 20.0
        elif days_left >= 14:
            return 15.0
        else:
            return 10.0

    def _calculate_funding_match(self, company_needs: Optional[str], project_amount: Optional[str]) -> float:
        """
        자금 규모 적합성 계산 (최대 20점)

        실제 구현 시 금액 파싱 및 비교 로직 필요
        현재는 단순화된 버전
        """
        if not company_needs or not project_amount:
            # 정보가 없어도 기본 점수 부여
            return 15.0

        # 금액 추출 (예: "5000만원", "1억원" 등)
        company_amount = self._parse_amount(company_needs)
        support_amount = self._parse_amount(project_amount)

        if company_amount is None or support_amount is None:
            return 15.0

        # 차이 계산
        diff_ratio = abs(company_amount - support_amount) / max(company_amount, support_amount)

        if diff_ratio <= 0.2:  # 20% 이내
            return 20.0
        elif diff_ratio <= 0.5:  # 50% 이내
            return 15.0
        else:
            return 10.0

    def _parse_amount(self, text: str) -> Optional[float]:
        """
        금액 텍스트를 숫자로 변환 (단위: 만원)

        예: "5000만원" -> 5000.0
            "1억원" -> 10000.0
            "5천만원" -> 5000.0
        """
        import re

        if not text:
            return None

        # 억원 패턴
        match = re.search(r'([\d,.]+)\s*억', text)
        if match:
            amount = float(match.group(1).replace(',', ''))
            return amount * 10000  # 억을 만원 단위로 변환

        # 천만원 패턴
        match = re.search(r'([\d,.]+)\s*천만', text)
        if match:
            amount = float(match.group(1).replace(',', ''))
            return amount * 1000

        # 만원 패턴
        match = re.search(r'([\d,.]+)\s*만', text)
        if match:
            amount = float(match.group(1).replace(',', ''))
            return amount

        return None

    def _calculate_certification_match(self, company_certs: List[str], requirements: str) -> float:
        """
        인증/자격 요건 매칭 (최대 10점)

        기업이 보유한 인증이 프로젝트 요구사항에 포함되어 있는지 확인
        """
        if not requirements:
            return 10.0  # 특별한 요구사항 없음

        if not company_certs:
            # 필수 인증이 있는지 확인
            required_keywords = ['필수', '반드시', 'required']
            if any(keyword in requirements for keyword in required_keywords):
                return 0.0
            else:
                return 5.0  # 선택사항

        # 인증 키워드 매칭
        cert_keywords = ['벤처', '이노비즈', '메인비즈', '기업부설연구소', 'ISO']
        matched_count = 0
        total_required = 0

        for keyword in cert_keywords:
            if keyword in requirements:
                total_required += 1
                if any(keyword in cert for cert in company_certs):
                    matched_count += 1

        if total_required == 0:
            return 10.0

        match_ratio = matched_count / total_required
        return match_ratio * 10.0

    def _calculate_region_match(self, company_region: Optional[str], project_region: Optional[str]) -> float:
        """
        지역 적합성 계산 (최대 10점)

        - 전국 대상: 10점
        - 동일 지역: 10점
        - 인접 지역: 5점
        - 불일치: 0점
        """
        if not project_region:
            return 10.0

        # 전국 대상 체크
        if project_region in ['전국', '전지역', '제한없음']:
            return 10.0

        if not company_region:
            return 5.0  # 기업 지역 정보 없으면 중간 점수

        # 지역 정규화 (예: "서울특별시" -> "서울", "경기도" -> "경기")
        company_region_short = self._normalize_region(company_region)
        project_region_short = self._normalize_region(project_region)

        # 동일 지역
        if company_region_short == project_region_short:
            return 10.0

        # 인접 지역 체크 (수도권: 서울, 경기, 인천)
        capital_regions = {'서울', '경기', '인천'}
        if company_region_short in capital_regions and project_region_short in capital_regions:
            return 5.0

        return 0.0

    def _normalize_region(self, region: str) -> str:
        """지역명 정규화"""
        if not region:
            return ''

        # "서울특별시" -> "서울"
        region = region.replace('특별시', '').replace('광역시', '').replace('도', '')
        region = region.strip()

        # 앞 2글자만 사용
        return region[:2]

    def filter_projects(self, company: Dict, projects: List[Dict],
                       min_score: float = 40.0,
                       max_results: Optional[int] = None) -> List[Dict]:
        """
        기업에 맞는 프로젝트 필터링 및 정렬

        Args:
            company: 기업 정보
            projects: 프로젝트 리스트
            min_score: 최소 매칭 점수 (기본 40점)
            max_results: 최대 결과 수

        Returns:
            매칭 점수가 높은 순으로 정렬된 프로젝트 리스트
        """
        matched_projects = []

        for project in projects:
            # 기본 필터링: 신청 기간 유효성
            if not self._is_project_active(project):
                continue

            # 매칭 점수 계산
            match_result = self.calculate_match_score(company, project)

            if match_result['score'] >= min_score:
                project_with_score = project.copy()
                project_with_score['match_score'] = match_result['score']
                project_with_score['match_reasons'] = match_result['reasons']
                matched_projects.append(project_with_score)

        # 매칭 점수 기준 내림차순 정렬
        matched_projects.sort(key=lambda x: x['match_score'], reverse=True)

        # 최대 결과 수 제한
        if max_results:
            matched_projects = matched_projects[:max_results]

        return matched_projects

    def _is_project_active(self, project: Dict) -> bool:
        """프로젝트가 현재 신청 가능한지 확인"""
        end_date = project.get('application_end_date')

        if not end_date:
            return True  # 마감일 정보 없으면 일단 유효한 것으로 간주

        if isinstance(end_date, str):
            try:
                end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
            except:
                return True

        return end_date >= datetime.now().date()

    def get_recommendation_level(self, score: float) -> str:
        """
        매칭 점수에 따른 추천 등급 반환

        Returns:
            'highly_recommended', 'recommended', 'consider', 'not_recommended'
        """
        if score >= 80:
            return 'highly_recommended'
        elif score >= 60:
            return 'recommended'
        elif score >= 40:
            return 'consider'
        else:
            return 'not_recommended'
