"""
Celery 애플리케이션 설정
"""
from celery import Celery
from celery.schedules import crontab
from backend.core.config import settings


# Celery 앱 생성
celery_app = Celery(
    'govplan_ai',
    broker=settings.redis_url,
    backend=settings.redis_url,
    include=['backend.tasks.crawler_tasks', 'backend.tasks.matching_tasks']
)

# Celery 설정
celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='Asia/Seoul',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30분
    task_soft_time_limit=25 * 60,  # 25분
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
)

# 주기적 작업 스케줄
celery_app.conf.beat_schedule = {
    # 매일 오전 9시에 전체 사이트 크롤링
    'crawl-all-sites-daily': {
        'task': 'backend.tasks.crawler_tasks.crawl_all_sites',
        'schedule': crontab(hour=9, minute=0),  # 매일 오전 9시
        'args': (10,)  # 최대 10페이지
    },
    # 매주 월요일 오전 10시에 매칭 점수 재계산
    'recalculate-matching-scores-weekly': {
        'task': 'backend.tasks.matching_tasks.recalculate_all_matching_scores',
        'schedule': crontab(day_of_week=1, hour=10, minute=0),  # 매주 월요일 10시
    },
    # 매일 자정에 만료된 공고 상태 업데이트
    'update-expired-projects': {
        'task': 'backend.tasks.crawler_tasks.update_expired_projects',
        'schedule': crontab(hour=0, minute=0),  # 매일 자정
    },
}

if __name__ == '__main__':
    celery_app.start()
