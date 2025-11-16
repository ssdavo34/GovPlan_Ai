"""
Slack 알림 서비스
"""
import requests
from typing import List, Dict, Optional
from datetime import datetime

from backend.core.config import settings


class SlackService:
    """Slack 알림 서비스"""

    def __init__(self, webhook_url: Optional[str] = None):
        """
        Args:
            webhook_url: Slack Webhook URL
        """
        self.webhook_url = webhook_url or getattr(settings, 'slack_webhook_url', '')

    def send_message(
        self,
        text: str,
        blocks: Optional[List[Dict]] = None,
        channel: Optional[str] = None
    ) -> bool:
        """
        Slack 메시지 발송

        Args:
            text: 메시지 텍스트
            blocks: Slack Block Kit 블록 (선택사항)
            channel: 채널 (선택사항, webhook 기본 채널 사용)

        Returns:
            발송 성공 여부
        """

        if not self.webhook_url:
            print("Warning: Slack Webhook URL이 설정되지 않았습니다")
            return False

        try:
            payload = {
                "text": text
            }

            if blocks:
                payload["blocks"] = blocks

            if channel:
                payload["channel"] = channel

            response = requests.post(
                self.webhook_url,
                json=payload,
                timeout=10
            )

            if response.status_code == 200:
                print("✓ Slack 메시지 발송 성공")
                return True
            else:
                print(f"✗ Slack 메시지 발송 실패: {response.status_code} - {response.text}")
                return False

        except Exception as e:
            print(f"✗ Slack 메시지 발송 오류: {e}")
            return False

    def send_new_project_notification(
        self,
        projects: List[Dict],
        channel: Optional[str] = None
    ) -> bool:
        """
        신규 공고 알림

        Args:
            projects: 공고 정보 리스트
            channel: 채널 (선택사항)

        Returns:
            발송 성공 여부
        """

        if not projects:
            return False

        text = f"🎯 신규 정부지원사업 {len(projects)}건 등록"

        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": "🎯 신규 정부지원사업 알림",
                    "emoji": True
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"새로운 지원사업 *{len(projects)}건*이 등록되었습니다."
                }
            },
            {
                "type": "divider"
            }
        ]

        # 최대 5개 공고 표시
        for i, project in enumerate(projects[:5], 1):
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*{i}. {project.get('project_name', 'N/A')}*\n"
                            f"📍 {project.get('agency', 'N/A')}\n"
                            f"📅 마감: {project.get('application_end_date', 'N/A')}\n"
                            f"💰 {project.get('support_amount', 'N/A')}"
                },
                "accessory": {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "자세히 보기",
                        "emoji": True
                    },
                    "url": project.get('project_url', '#')
                }
            })

        if len(projects) > 5:
            blocks.append({
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": f"_외 {len(projects) - 5}건..._"
                    }
                ]
            })

        blocks.append({
            "type": "context",
            "elements": [
                {
                    "type": "mrkdwn",
                    "text": f"🕒 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                }
            ]
        })

        return self.send_message(text, blocks, channel)

    def send_matching_notification(
        self,
        company_name: str,
        matches: List[Dict],
        channel: Optional[str] = None
    ) -> bool:
        """
        매칭 결과 알림

        Args:
            company_name: 기업명
            matches: 매칭 결과 리스트
            channel: 채널 (선택사항)

        Returns:
            발송 성공 여부
        """

        if not matches:
            return False

        # 점수별 분류
        excellent = [m for m in matches if m.get('match_score', 0) >= 80]
        good = [m for m in matches if 60 <= m.get('match_score', 0) < 80]

        text = f"🎯 {company_name}님을 위한 맞춤 지원사업 추천"

        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"🎯 {company_name}님을 위한 추천",
                    "emoji": True
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"귀사에 적합한 정부지원사업 *{len(matches)}건*을 추천드립니다."
                }
            },
            {
                "type": "divider"
            }
        ]

        if excellent:
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*🔥 강력 추천 ({len(excellent)}건)*"
                }
            })

            for match in excellent[:3]:
                blocks.append({
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*{match.get('project_name', 'N/A')}*\n"
                                f"📊 매칭도: {match.get('match_score', 0):.1f}점\n"
                                f"📅 마감: {match.get('application_end_date', 'N/A')}"
                    }
                })

        if good:
            blocks.append({
                "type": "divider"
            })
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*✅ 추천 ({len(good)}건)*"
                }
            })

        blocks.append({
            "type": "context",
            "elements": [
                {
                    "type": "mrkdwn",
                    "text": "_더 많은 추천 사업은 대시보드에서 확인하세요_"
                }
            ]
        })

        return self.send_message(text, blocks, channel)

    def send_proposal_ready_notification(
        self,
        company_name: str,
        project_name: str,
        proposal_id: int,
        channel: Optional[str] = None
    ) -> bool:
        """
        사업계획서 생성 완료 알림

        Args:
            company_name: 기업명
            project_name: 지원사업명
            proposal_id: 사업계획서 ID
            channel: 채널 (선택사항)

        Returns:
            발송 성공 여부
        """

        text = f"📄 {company_name}님의 사업계획서가 준비되었습니다"

        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": "📄 사업계획서 준비 완료",
                    "emoji": True
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*{company_name}*님의 '{project_name}' 사업계획서가 AI에 의해 자동으로 생성되었습니다."
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*다운로드:*"
                },
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": f"<http://localhost:8000/api/v1/proposals/{proposal_id}/download/pdf|📕 PDF>"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"<http://localhost:8000/api/v1/proposals/{proposal_id}/download/docx|📘 DOCX>"
                    }
                ]
            },
            {
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": "_사업계획서를 검토하신 후 필요에 따라 수정하여 사용하시기 바랍니다._"
                    }
                ]
            }
        ]

        return self.send_message(text, blocks, channel)

    def send_error_notification(
        self,
        error_type: str,
        error_message: str,
        details: Optional[Dict] = None,
        channel: Optional[str] = None
    ) -> bool:
        """
        에러 알림

        Args:
            error_type: 에러 유형
            error_message: 에러 메시지
            details: 추가 상세 정보
            channel: 채널 (선택사항)

        Returns:
            발송 성공 여부
        """

        text = f"⚠️ 시스템 오류: {error_type}"

        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": "⚠️ 시스템 오류 발생",
                    "emoji": True
                }
            },
            {
                "type": "section",
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": f"*유형:*\n{error_type}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*시간:*\n{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                    }
                ]
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*메시지:*\n```{error_message}```"
                }
            }
        ]

        if details:
            details_text = "\n".join([f"*{k}:* {v}" for k, v in details.items()])
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*상세 정보:*\n{details_text}"
                }
            })

        return self.send_message(text, blocks, channel)

    def send_crawling_summary(
        self,
        site: str,
        total_projects: int,
        new_projects: int,
        duration_seconds: float,
        channel: Optional[str] = None
    ) -> bool:
        """
        크롤링 요약 알림

        Args:
            site: 사이트명
            total_projects: 전체 수집 공고 수
            new_projects: 신규 공고 수
            duration_seconds: 소요 시간 (초)
            channel: 채널 (선택사항)

        Returns:
            발송 성공 여부
        """

        text = f"🔍 {site} 크롤링 완료"

        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"🔍 {site} 크롤링 완료",
                    "emoji": True
                }
            },
            {
                "type": "section",
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": f"*수집 공고:*\n{total_projects}건"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*신규 공고:*\n{new_projects}건"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*소요 시간:*\n{duration_seconds:.1f}초"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*완료 시간:*\n{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                    }
                ]
            }
        ]

        return self.send_message(text, blocks, channel)
