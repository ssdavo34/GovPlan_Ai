"""
기업 정보 모델
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Date, BigInteger, DateTime, JSON
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Company(Base):
    """기업 정보 모델"""

    __tablename__ = 'companies'

    id = Column(Integer, primary_key=True, autoincrement=True)
    company_name = Column(String(200), nullable=False)
    business_number = Column(String(50), unique=True, index=True)
    company_type = Column(String(100), index=True)
    industry_code = Column(String(100), index=True)
    industry_name = Column(String(200))
    region = Column(String(100), index=True)
    establishment_date = Column(Date)
    employee_count = Column(Integer)
    annual_revenue = Column(BigInteger)
    certifications = Column(JSON)  # ['벤처인증', '이노비즈', '메인비즈'] 등
    technology_fields = Column(JSON)  # ['AI', 'IoT', '바이오'] 등
    funding_needs = Column(String(500))
    preferred_support_types = Column(JSON)  # ['보조금', '융자', '바우처'] 등
    user_id = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<Company(id={self.id}, company_name='{self.company_name}')>"

    def to_dict(self):
        """모델을 딕셔너리로 변환"""
        return {
            'id': self.id,
            'company_name': self.company_name,
            'business_number': self.business_number,
            'company_type': self.company_type,
            'industry_code': self.industry_code,
            'industry_name': self.industry_name,
            'region': self.region,
            'establishment_date': self.establishment_date.isoformat() if self.establishment_date else None,
            'employee_count': self.employee_count,
            'annual_revenue': self.annual_revenue,
            'certifications': self.certifications,
            'technology_fields': self.technology_fields,
            'funding_needs': self.funding_needs,
            'preferred_support_types': self.preferred_support_types,
            'user_id': self.user_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    def get_company_age_years(self):
        """회사 업력(년) 계산"""
        if not self.establishment_date:
            return None
        delta = datetime.now().date() - self.establishment_date
        return delta.days // 365

    def has_certification(self, cert_name):
        """특정 인증 보유 여부 확인"""
        if not self.certifications:
            return False
        return cert_name in self.certifications

    def matches_industry(self, industry_code):
        """업종 코드 매칭 확인 (대분류, 중분류, 소분류)"""
        if not self.industry_code or not industry_code:
            return False

        # KSIC 코드는 5자리 (예: C2611)
        # 대분류: C (1자리)
        # 중분류: C26 (2자리)
        # 소분류: C261 (3자리)
        # 세분류: C2611 (4자리)

        if industry_code == self.industry_code:
            return True  # 완전 일치

        # 상위 분류 일치 확인
        for i in range(1, min(len(industry_code), len(self.industry_code)) + 1):
            if industry_code[:i] == self.industry_code[:i]:
                return True

        return False
