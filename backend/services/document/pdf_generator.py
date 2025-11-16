"""
PDF 문서 생성 서비스
"""
from typing import Dict, Optional
from pathlib import Path
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY


class PDFGenerator:
    """PDF 사업계획서 생성기"""

    def __init__(self, use_korean_font: bool = True):
        """
        Args:
            use_korean_font: 한글 폰트 사용 여부
        """
        self.use_korean_font = use_korean_font
        self.styles = getSampleStyleSheet()

        # 한글 폰트 등록 시도 (시스템에 설치된 경우)
        if use_korean_font:
            try:
                # Linux/Mac 일반적인 경로
                font_paths = [
                    "/usr/share/fonts/truetype/nanum/NanumGothic.ttf",
                    "/usr/share/fonts/truetype/nanum/NanumMyeongjo.ttf",
                    "/System/Library/Fonts/AppleSDGothicNeo.ttc",
                ]

                for font_path in font_paths:
                    if Path(font_path).exists():
                        pdfmetrics.registerFont(TTFont('Korean', font_path))
                        self._setup_korean_styles()
                        break
            except Exception as e:
                print(f"Warning: 한글 폰트를 로드할 수 없습니다: {e}")
                print("기본 폰트를 사용합니다.")
                self.use_korean_font = False

    def _setup_korean_styles(self):
        """한글 스타일 설정"""
        # 제목 스타일
        title_style = ParagraphStyle(
            'KoreanTitle',
            parent=self.styles['Title'],
            fontName='Korean',
            fontSize=24,
            alignment=TA_CENTER,
            spaceAfter=30
        )
        self.styles.add(title_style)

        # 제목2 스타일
        heading1_style = ParagraphStyle(
            'KoreanHeading1',
            parent=self.styles['Heading1'],
            fontName='Korean',
            fontSize=18,
            spaceBefore=20,
            spaceAfter=12
        )
        self.styles.add(heading1_style)

        # 제목3 스타일
        heading2_style = ParagraphStyle(
            'KoreanHeading2',
            parent=self.styles['Heading2'],
            fontName='Korean',
            fontSize=14,
            spaceBefore=12,
            spaceAfter=6
        )
        self.styles.add(heading2_style)

        # 본문 스타일
        body_style = ParagraphStyle(
            'KoreanBody',
            parent=self.styles['BodyText'],
            fontName='Korean',
            fontSize=10,
            alignment=TA_JUSTIFY,
            spaceAfter=6
        )
        self.styles.add(body_style)

    def generate(
        self,
        proposal_data: Dict,
        output_path: str,
        include_cover: bool = True
    ) -> str:
        """
        사업계획서 PDF 생성

        Args:
            proposal_data: 사업계획서 데이터
            output_path: 출력 파일 경로
            include_cover: 표지 포함 여부

        Returns:
            생성된 PDF 파일 경로
        """

        # PDF 문서 생성
        doc = SimpleDocTemplate(
            output_path,
            pagesize=A4,
            rightMargin=0.75 * inch,
            leftMargin=0.75 * inch,
            topMargin=0.75 * inch,
            bottomMargin=0.75 * inch
        )

        # 문서 요소 리스트
        story = []

        # 스타일 선택
        title_style = self.styles['KoreanTitle'] if self.use_korean_font else self.styles['Title']
        heading1_style = self.styles['KoreanHeading1'] if self.use_korean_font else self.styles['Heading1']
        heading2_style = self.styles['KoreanHeading2'] if self.use_korean_font else self.styles['Heading2']
        body_style = self.styles['KoreanBody'] if self.use_korean_font else self.styles['BodyText']

        # 표지 추가
        if include_cover:
            story.extend(self._create_cover_page(proposal_data, title_style, body_style))
            story.append(PageBreak())

        # 기업 정보 및 공고 정보
        story.extend(self._create_info_section(proposal_data, heading1_style, body_style))
        story.append(Spacer(1, 0.3 * inch))

        # 섹션별 내용 추가
        sections = proposal_data.get('sections', {})
        for section_name, section_content in sections.items():
            story.append(Paragraph(section_name, heading1_style))
            story.append(Spacer(1, 0.2 * inch))

            # 섹션 내용을 문단으로 분리
            paragraphs = section_content.split('\n\n')
            for para in paragraphs:
                if para.strip():
                    # 하위 제목 감지 (## 또는 ### 로 시작)
                    if para.strip().startswith('###'):
                        text = para.strip().replace('###', '').strip()
                        story.append(Paragraph(text, heading2_style))
                    elif para.strip().startswith('##'):
                        text = para.strip().replace('##', '').strip()
                        story.append(Paragraph(text, heading1_style))
                    else:
                        story.append(Paragraph(para.strip(), body_style))

            story.append(Spacer(1, 0.3 * inch))

        # PDF 빌드
        doc.build(story)

        return output_path

    def _create_cover_page(self, proposal_data: Dict, title_style, body_style):
        """표지 페이지 생성"""
        elements = []

        # 상단 여백
        elements.append(Spacer(1, 2 * inch))

        # 제목
        title = proposal_data.get('title', '사업계획서')
        elements.append(Paragraph(title, title_style))
        elements.append(Spacer(1, 0.5 * inch))

        # 부제목
        subtitle = proposal_data.get('project_name', '')
        if subtitle:
            elements.append(Paragraph(subtitle, body_style))
            elements.append(Spacer(1, 1.5 * inch))

        # 기업 정보 테이블
        company_info = [
            ['기업명', proposal_data.get('company_name', 'N/A')],
            ['대표자', proposal_data.get('ceo_name', 'N/A')],
            ['사업자등록번호', proposal_data.get('business_number', 'N/A')],
            ['작성일', datetime.now().strftime('%Y년 %m월 %d일')]
        ]

        table = Table(company_info, colWidths=[1.5 * inch, 3.5 * inch])
        table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Korean' if self.use_korean_font else 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 12),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LINEBELOW', (0, 0), (-1, -1), 0.5, colors.grey),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))

        elements.append(table)

        return elements

    def _create_info_section(self, proposal_data: Dict, heading_style, body_style):
        """기업 정보 및 공고 정보 섹션"""
        elements = []

        # 기업 정보
        elements.append(Paragraph("기업 정보", heading_style))
        elements.append(Spacer(1, 0.1 * inch))

        company_data = [
            ['항목', '내용'],
            ['기업명', proposal_data.get('company_name', 'N/A')],
            ['업종', proposal_data.get('industry_name', 'N/A')],
            ['소재지', proposal_data.get('region', 'N/A')],
            ['직원 수', f"{proposal_data.get('employee_count', 'N/A')}명"],
        ]

        table = Table(company_data, colWidths=[1.5 * inch, 4 * inch])
        table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Korean' if self.use_korean_font else 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))

        elements.append(table)
        elements.append(Spacer(1, 0.3 * inch))

        # 지원사업 정보
        elements.append(Paragraph("지원사업 정보", heading_style))
        elements.append(Spacer(1, 0.1 * inch))

        project_data = [
            ['항목', '내용'],
            ['사업명', proposal_data.get('project_name', 'N/A')],
            ['시행기관', proposal_data.get('agency', 'N/A')],
            ['지원 분야', proposal_data.get('support_type', 'N/A')],
            ['지원 금액', proposal_data.get('support_amount', 'N/A')],
        ]

        table = Table(project_data, colWidths=[1.5 * inch, 4 * inch])
        table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Korean' if self.use_korean_font else 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))

        elements.append(table)

        return elements
