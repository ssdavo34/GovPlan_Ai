"""
AI 기반 사업계획서 생성 서비스
"""
import json
from typing import Dict, Optional
import anthropic
from backend.core.config import settings


class ProposalGenerator:
    """사업계획서 생성기"""

    def __init__(self, api_key: Optional[str] = None):
        """
        Args:
            api_key: Anthropic API 키 (None이면 설정에서 가져옴)
        """
        self.api_key = api_key or settings.anthropic_api_key

        if not self.api_key:
            raise ValueError("Anthropic API 키가 설정되지 않았습니다")

        self.client = anthropic.Anthropic(api_key=self.api_key)
        self.model = "claude-3-5-sonnet-20241022"

    def generate_proposal(
        self,
        company_info: Dict,
        project_info: Dict,
        additional_info: Optional[Dict] = None
    ) -> Dict[str, str]:
        """
        사업계획서 생성

        Args:
            company_info: 기업 정보
            project_info: 지원사업 정보
            additional_info: 추가 정보 (사업 내용, 재무 계획 등)

        Returns:
            섹션별 생성된 내용
        """

        # 프롬프트 구성
        prompt = self._build_prompt(company_info, project_info, additional_info)

        # Claude API 호출
        try:
            message = self.client.messages.create(
                model=self.model,
                max_tokens=4096,
                temperature=0.7,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )

            # 응답 파싱
            response_text = message.content[0].text

            # 섹션별로 분리
            sections = self._parse_sections(response_text)

            return sections

        except Exception as e:
            raise Exception(f"사업계획서 생성 중 오류 발생: {str(e)}")

    def _build_prompt(
        self,
        company_info: Dict,
        project_info: Dict,
        additional_info: Optional[Dict] = None
    ) -> str:
        """프롬프트 구성"""

        additional_info = additional_info or {}

        prompt = f"""당신은 정부지원사업 사업계획서 작성 전문가입니다.
다음 정보를 바탕으로 전문적이고 설득력 있는 사업계획서를 작성해주세요.

## 기업 정보
- 기업명: {company_info.get('company_name', 'N/A')}
- 업종: {company_info.get('industry_name', 'N/A')}
- 기업 유형: {company_info.get('company_type', 'N/A')}
- 소재지: {company_info.get('region', 'N/A')}
- 직원 수: {company_info.get('employee_count', 'N/A')}명
- 기술 분야: {', '.join(company_info.get('technology_fields', [])) if company_info.get('technology_fields') else 'N/A'}
- 보유 인증: {json.dumps(company_info.get('certifications', {}), ensure_ascii=False) if company_info.get('certifications') else 'N/A'}

## 지원사업 정보
- 사업명: {project_info.get('project_name', 'N/A')}
- 시행기관: {project_info.get('agency', 'N/A')}
- 지원 분야: {project_info.get('support_type', 'N/A')}
- 지원 금액: {project_info.get('support_amount', 'N/A')}
- 대상 요건: {project_info.get('target_requirements', 'N/A')}
- 평가 기준: {project_info.get('evaluation_criteria', 'N/A')}

## 추가 정보
{self._format_additional_info(additional_info)}

## 작성 원칙
1. 구체적인 수치와 데이터 활용
2. 사업의 필요성과 타당성 명확히 제시
3. 실현 가능한 계획 수립
4. 정부 정책 방향과의 연계성 강조
5. 평가 기준에 부합하는 내용 작성

## 요청사항
다음 구조로 사업계획서를 작성해주세요. 각 섹션은 "## [섹션명]" 형태로 구분해주세요.

## 1. 사업 개요
- 사업명과 목적을 명확히 제시 (200-300자)
- 추진 배경 간단히 설명

## 2. 사업의 필요성 및 목표
- 현재 상황 및 문제점 분석 (400-500자)
- 사업 추진의 필요성
- 구체적인 목표 설정 (정량적 목표 포함)

## 3. 사업 내용 및 추진 전략
- 주요 추진 내용 상세 설명 (800-1000자)
- 핵심 기술 또는 서비스 차별성
- 단계별 추진 계획
- 추진 일정 (간트 차트 형태로)

## 4. 추진 체계 및 역량
- 조직 구성 및 역할
- 핵심 인력 및 전문성
- 보유 역량 및 인프라

## 5. 기대 효과 및 활용 방안
- 경제적 효과 (매출 증대, 일자리 창출 등)
- 사회적 효과
- 기술적 효과
- 성과 지표 및 측정 방법

## 6. 예산 계획
- 총 소요 예산
- 항목별 예산 내역 (표 형태)
- 자부담 및 정부지원금 구분

각 섹션은 평가 기준에 부합하도록 작성하고, 기업의 강점을 부각시켜주세요.
"""

        return prompt

    def _format_additional_info(self, additional_info: Dict) -> str:
        """추가 정보 포맷팅"""
        if not additional_info:
            return "없음"

        formatted = []
        for key, value in additional_info.items():
            if value:
                formatted.append(f"- {key}: {value}")

        return "\n".join(formatted) if formatted else "없음"

    def _parse_sections(self, response_text: str) -> Dict[str, str]:
        """응답을 섹션별로 파싱"""
        sections = {}

        # ## 로 구분된 섹션 추출
        lines = response_text.split('\n')
        current_section = None
        current_content = []

        for line in lines:
            if line.startswith('## '):
                # 이전 섹션 저장
                if current_section:
                    sections[current_section] = '\n'.join(current_content).strip()

                # 새로운 섹션 시작
                current_section = line.replace('## ', '').strip()
                current_content = []
            elif current_section:
                current_content.append(line)

        # 마지막 섹션 저장
        if current_section:
            sections[current_section] = '\n'.join(current_content).strip()

        return sections

    def generate_section(
        self,
        section_name: str,
        company_info: Dict,
        project_info: Dict,
        additional_info: Optional[Dict] = None
    ) -> str:
        """
        특정 섹션만 생성

        Args:
            section_name: 생성할 섹션명
            company_info: 기업 정보
            project_info: 지원사업 정보
            additional_info: 추가 정보

        Returns:
            생성된 섹션 내용
        """

        additional_info = additional_info or {}

        prompt = f"""당신은 정부지원사업 사업계획서 작성 전문가입니다.

## 기업 정보
- 기업명: {company_info.get('company_name', 'N/A')}
- 업종: {company_info.get('industry_name', 'N/A')}
- 기업 유형: {company_info.get('company_type', 'N/A')}

## 지원사업 정보
- 사업명: {project_info.get('project_name', 'N/A')}
- 시행기관: {project_info.get('agency', 'N/A')}
- 지원 분야: {project_info.get('support_type', 'N/A')}

## 추가 정보
{self._format_additional_info(additional_info)}

## 요청사항
다음 섹션의 내용을 작성해주세요:

**{section_name}**

구체적이고 설득력 있게 작성하되, 평가 기준에 부합하도록 작성해주세요.
"""

        try:
            message = self.client.messages.create(
                model=self.model,
                max_tokens=2048,
                temperature=0.7,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )

            return message.content[0].text.strip()

        except Exception as e:
            raise Exception(f"섹션 생성 중 오류 발생: {str(e)}")
