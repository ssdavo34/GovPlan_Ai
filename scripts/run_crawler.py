#!/usr/bin/env python
"""
크롤러 실행 스크립트
"""
import sys
import os
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import asyncio
import argparse
from datetime import datetime
from backend.crawlers.bizinfo_crawler import BizinfoCrawler
from backend.crawlers.kstartup_crawler import KStartupCrawler
from backend.services.crawler_service import CrawlerService


async def run_crawler(site: str = "all", max_pages: int = 5, save_to_db: bool = True):
    """
    크롤러 실행

    Args:
        site: 크롤링할 사이트 (all, bizinfo, kstartup)
        max_pages: 크롤링할 최대 페이지 수
        save_to_db: 데이터베이스 저장 여부
    """

    print("=" * 80)
    print(f"정부지원사업 크롤러 실행 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    print()

    crawlers = []

    # 크롤러 선택
    if site in ["all", "bizinfo"]:
        print("🔍 기업마당(Bizinfo) 크롤러 준비 중...")
        crawlers.append(("기업마당", BizinfoCrawler()))

    if site in ["all", "kstartup"]:
        print("🔍 K-Startup 크롤러 준비 중...")
        crawlers.append(("K-Startup", KStartupCrawler()))

    if not crawlers:
        print(f"❌ 알 수 없는 사이트: {site}")
        print("사용 가능한 사이트: all, bizinfo, kstartup")
        return

    print()

    # 크롤링 서비스 초기화
    if save_to_db:
        # 환경 변수에서 DB 설정 읽기
        db_config = {
            "host": os.getenv("DB_HOST", "localhost"),
            "port": int(os.getenv("DB_PORT", "5432")),
            "database": os.getenv("DB_NAME", "govplan_ai"),
            "user": os.getenv("DB_USER", "postgres"),
            "password": os.getenv("DB_PASSWORD", "postgres")
        }

        try:
            crawler_service = CrawlerService(db_config)
            await crawler_service.connect()
            print("✓ 데이터베이스 연결 완료\n")
        except Exception as e:
            print(f"❌ 데이터베이스 연결 실패: {e}")
            print("데이터베이스 저장 없이 진행합니다.\n")
            save_to_db = False
            crawler_service = None
    else:
        crawler_service = None

    # 각 크롤러 실행
    total_projects = 0

    for site_name, crawler in crawlers:
        print(f"{'=' * 80}")
        print(f"📡 {site_name} 크롤링 시작...")
        print(f"{'=' * 80}")

        try:
            projects = await crawler.crawl(max_pages=max_pages)

            print(f"\n✓ {site_name} 크롤링 완료: {len(projects)}개 공고 수집")

            # 데이터베이스 저장
            if save_to_db and crawler_service and projects:
                print(f"💾 데이터베이스에 저장 중...")
                saved_count = await crawler_service.save_projects(projects, site_name)
                print(f"✓ {saved_count}개 공고 저장 완료")

            # 샘플 출력
            if projects:
                print(f"\n📋 수집된 공고 샘플 (최대 3개):")
                for i, project in enumerate(projects[:3], 1):
                    print(f"\n  [{i}] {project.get('title', 'N/A')}")
                    print(f"      기관: {project.get('agency', 'N/A')}")
                    print(f"      기간: {project.get('application_start_date', 'N/A')} ~ {project.get('application_end_date', 'N/A')}")
                    print(f"      URL: {project.get('url', 'N/A')}")

            total_projects += len(projects)

        except Exception as e:
            print(f"❌ {site_name} 크롤링 오류: {e}")
            import traceback
            traceback.print_exc()

        print()

    # 크롤링 서비스 종료
    if crawler_service:
        await crawler_service.close()

    print("=" * 80)
    print(f"✅ 크롤링 완료: 총 {total_projects}개 공고 수집")
    print("=" * 80)


def main():
    """메인 함수"""

    parser = argparse.ArgumentParser(description="정부지원사업 크롤러")
    parser.add_argument(
        "--site",
        type=str,
        default="all",
        choices=["all", "bizinfo", "kstartup"],
        help="크롤링할 사이트 (기본값: all)"
    )
    parser.add_argument(
        "--max-pages",
        type=int,
        default=5,
        help="크롤링할 최대 페이지 수 (기본값: 5)"
    )
    parser.add_argument(
        "--no-db",
        action="store_true",
        help="데이터베이스 저장 안함 (테스트용)"
    )

    args = parser.parse_args()

    # .env 파일 로드 (있는 경우)
    env_file = project_root / ".env"
    if env_file.exists():
        print(f"환경 변수 로드 중: {env_file}")
        from dotenv import load_dotenv
        load_dotenv(env_file)
        print()

    # 크롤러 실행
    asyncio.run(run_crawler(
        site=args.site,
        max_pages=args.max_pages,
        save_to_db=not args.no_db
    ))


if __name__ == "__main__":
    main()
