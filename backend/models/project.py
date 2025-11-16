"""
정부지원사업 모델
"""
from datetime import datetime
from sqlalchemy import Column, String, Text, Date, DateTime, JSON
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class GovSupportProject(Base):
    """정부지원사업 정보 모델"""

    __tablename__ = 'gov_support_projects'

    id = Column(String(50), primary_key=True)
    project_name = Column(String(500), nullable=False, index=True)
    agency = Column(String(200))
    project_url = Column(Text)
    summary = Column(Text)
    support_type = Column(String(100))
    support_amount = Column(String(200))
    target_type = Column(String(200), index=True)
    target_requirements = Column(Text)
    industry_code = Column(String(100), index=True)
    region = Column(String(100))
    application_start_date = Column(Date, index=True)
    application_end_date = Column(Date, index=True)
    required_documents = Column(Text)
    evaluation_criteria = Column(Text)
    fund_usage = Column(Text)
    contact_info = Column(String(500))
    attachments = Column(JSON)
    source_site = Column(String(100), index=True)
    last_crawled = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    status = Column(String(50), default='active', index=True)

    def __repr__(self):
        return f"<GovSupportProject(id='{self.id}', project_name='{self.project_name}')>"

    def to_dict(self):
        """모델을 딕셔너리로 변환"""
        return {
            'id': self.id,
            'project_name': self.project_name,
            'agency': self.agency,
            'project_url': self.project_url,
            'summary': self.summary,
            'support_type': self.support_type,
            'support_amount': self.support_amount,
            'target_type': self.target_type,
            'target_requirements': self.target_requirements,
            'industry_code': self.industry_code,
            'region': self.region,
            'application_start_date': self.application_start_date.isoformat() if self.application_start_date else None,
            'application_end_date': self.application_end_date.isoformat() if self.application_end_date else None,
            'required_documents': self.required_documents,
            'evaluation_criteria': self.evaluation_criteria,
            'fund_usage': self.fund_usage,
            'contact_info': self.contact_info,
            'attachments': self.attachments,
            'source_site': self.source_site,
            'last_crawled': self.last_crawled.isoformat() if self.last_crawled else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'status': self.status
        }

    def is_active(self):
        """신청 기간이 유효한지 확인"""
        if not self.application_end_date:
            return False
        return self.application_end_date >= datetime.now().date() and self.status == 'active'

    def days_until_deadline(self):
        """마감일까지 남은 일수"""
        if not self.application_end_date:
            return None
        delta = self.application_end_date - datetime.now().date()
        return delta.days if delta.days >= 0 else 0
