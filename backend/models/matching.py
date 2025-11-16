"""
매칭 및 사업계획서 관련 모델
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Date, DateTime, Boolean, ForeignKey, DECIMAL, Text, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class MatchingHistory(Base):
    """기업-지원사업 매칭 이력 모델"""

    __tablename__ = 'matching_history'

    id = Column(Integer, primary_key=True, autoincrement=True)
    company_id = Column(Integer, ForeignKey('companies.id', ondelete='CASCADE'), nullable=False, index=True)
    project_id = Column(String(50), ForeignKey('gov_support_projects.id', ondelete='CASCADE'), nullable=False, index=True)
    match_score = Column(DECIMAL(5, 2), index=True)
    match_reasons = Column(JSON)  # {'industry_match': 40, 'date_match': 20, ...}
    is_bookmarked = Column(Boolean, default=False, index=True)
    is_applied = Column(Boolean, default=False)
    application_date = Column(Date)
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<MatchingHistory(id={self.id}, company_id={self.company_id}, project_id='{self.project_id}', score={self.match_score})>"

    def to_dict(self):
        """모델을 딕셔너리로 변환"""
        return {
            'id': self.id,
            'company_id': self.company_id,
            'project_id': self.project_id,
            'match_score': float(self.match_score) if self.match_score else None,
            'match_reasons': self.match_reasons,
            'is_bookmarked': self.is_bookmarked,
            'is_applied': self.is_applied,
            'application_date': self.application_date.isoformat() if self.application_date else None,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    def get_recommendation_level(self):
        """매칭 점수에 따른 추천 등급 반환"""
        if not self.match_score:
            return 'unknown'

        score = float(self.match_score)
        if score >= 80:
            return 'highly_recommended'
        elif score >= 60:
            return 'recommended'
        elif score >= 40:
            return 'consider'
        else:
            return 'not_recommended'


class BusinessPlanHistory(Base):
    """AI 생성 사업계획서 이력 모델"""

    __tablename__ = 'business_plan_history'

    id = Column(Integer, primary_key=True, autoincrement=True)
    company_id = Column(Integer, ForeignKey('companies.id', ondelete='CASCADE'), nullable=False, index=True)
    project_id = Column(String(50), ForeignKey('gov_support_projects.id', ondelete='SET NULL'), index=True)
    template_type = Column(String(100))  # 'common', 'startup', 'rnd', 'smallbiz'
    content = Column(JSON)  # 사업계획서 각 섹션별 내용
    generated_file_path = Column(Text)
    status = Column(String(50), default='draft', index=True)  # 'draft', 'completed', 'submitted'
    ai_model_used = Column(String(100))  # 'gpt-4', 'claude-3-opus' 등
    generation_cost = Column(DECIMAL(10, 4))  # API 호출 비용
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<BusinessPlanHistory(id={self.id}, company_id={self.company_id}, template='{self.template_type}')>"

    def to_dict(self):
        """모델을 딕셔너리로 변환"""
        return {
            'id': self.id,
            'company_id': self.company_id,
            'project_id': self.project_id,
            'template_type': self.template_type,
            'content': self.content,
            'generated_file_path': self.generated_file_path,
            'status': self.status,
            'ai_model_used': self.ai_model_used,
            'generation_cost': float(self.generation_cost) if self.generation_cost else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    def get_file_format(self):
        """생성된 파일의 형식 반환"""
        if not self.generated_file_path:
            return None

        file_ext = self.generated_file_path.split('.')[-1].lower()
        return file_ext
