"""
크롤링 로그 모델
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class CrawlingLog(Base):
    """크롤링 작업 로그 모델"""

    __tablename__ = 'crawling_logs'

    id = Column(Integer, primary_key=True, autoincrement=True)
    source_site = Column(String(100), nullable=False, index=True)
    started_at = Column(DateTime, nullable=False, index=True)
    completed_at = Column(DateTime)
    status = Column(String(50), default='running', index=True)  # 'running', 'completed', 'failed'
    projects_found = Column(Integer, default=0)
    projects_new = Column(Integer, default=0)
    projects_updated = Column(Integer, default=0)
    error_message = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<CrawlingLog(id={self.id}, source='{self.source_site}', status='{self.status}')>"

    def to_dict(self):
        """모델을 딕셔너리로 변환"""
        return {
            'id': self.id,
            'source_site': self.source_site,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'status': self.status,
            'projects_found': self.projects_found,
            'projects_new': self.projects_new,
            'projects_updated': self.projects_updated,
            'error_message': self.error_message,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

    def get_duration_seconds(self):
        """크롤링 소요 시간(초) 반환"""
        if not self.completed_at or not self.started_at:
            return None
        delta = self.completed_at - self.started_at
        return delta.total_seconds()

    def mark_completed(self):
        """크롤링 완료 표시"""
        self.completed_at = datetime.utcnow()
        self.status = 'completed'

    def mark_failed(self, error_msg):
        """크롤링 실패 표시"""
        self.completed_at = datetime.utcnow()
        self.status = 'failed'
        self.error_message = error_msg
