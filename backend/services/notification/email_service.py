"""
이메일 알림 서비스
"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from typing import List, Optional, Dict
from pathlib import Path
from datetime import datetime

from backend.core.config import settings


class EmailService:
    """이메일 발송 서비스"""

    def __init__(
        self,
        smtp_server: Optional[str] = None,
        smtp_port: Optional[int] = None,
        smtp_user: Optional[str] = None,
        smtp_password: Optional[str] = None,
        from_email: Optional[str] = None
    ):
        """
        Args:
            smtp_server: SMTP 서버 주소
            smtp_port: SMTP 포트
            smtp_user: SMTP 사용자명
            smtp_password: SMTP 비밀번호
            from_email: 발신자 이메일
        """
        self.smtp_server = smtp_server or getattr(settings, 'smtp_server', 'smtp.gmail.com')
        self.smtp_port = smtp_port or getattr(settings, 'smtp_port', 587)
        self.smtp_user = smtp_user or getattr(settings, 'smtp_user', '')
        self.smtp_password = smtp_password or getattr(settings, 'smtp_password', '')
        self.from_email = from_email or getattr(settings, 'from_email', self.smtp_user)

    def send_email(
        self,
        to_emails: List[str],
        subject: str,
        body: str,
        html_body: Optional[str] = None,
        attachments: Optional[List[str]] = None
    ) -> bool:
        """
        이메일 발송

        Args:
            to_emails: 수신자 이메일 리스트
            subject: 제목
            body: 본문 (plain text)
            html_body: HTML 본문 (선택사항)
            attachments: 첨부파일 경로 리스트 (선택사항)

        Returns:
            발송 성공 여부
        """

        try:
            # 메시지 생성
            msg = MIMEMultipart('alternative')
            msg['From'] = self.from_email
            msg['To'] = ', '.join(to_emails)
            msg['Subject'] = subject
            msg['Date'] = datetime.now().strftime('%a, %d %b %Y %H:%M:%S %z')

            # Plain text 본문 추가
            msg.attach(MIMEText(body, 'plain', 'utf-8'))

            # HTML 본문 추가 (있는 경우)
            if html_body:
                msg.attach(MIMEText(html_body, 'html', 'utf-8'))

            # 첨부파일 추가
            if attachments:
                for file_path in attachments:
                    self._attach_file(msg, file_path)

            # SMTP 서버 연결 및 발송
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_password)
                server.send_message(msg)

            print(f"✓ 이메일 발송 성공: {', '.join(to_emails)}")
            return True

        except Exception as e:
            print(f"✗ 이메일 발송 실패: {e}")
            return False

    def _attach_file(self, msg: MIMEMultipart, file_path: str):
        """첨부파일 추가"""
        path = Path(file_path)

        if not path.exists():
            print(f"Warning: 첨부파일을 찾을 수 없습니다: {file_path}")
            return

        with open(path, 'rb') as f:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(f.read())

        encoders.encode_base64(part)
        part.add_header(
            'Content-Disposition',
            f'attachment; filename= {path.name}'
        )

        msg.attach(part)

    def send_new_project_notification(
        self,
        to_emails: List[str],
        projects: List[Dict]
    ) -> bool:
        """
        신규 공고 알림 이메일 발송

        Args:
            to_emails: 수신자 이메일 리스트
            projects: 공고 정보 리스트

        Returns:
            발송 성공 여부
        """

        if not projects:
            return False

        subject = f"[GovPlan_AI] 신규 정부지원사업 {len(projects)}건 등록"

        # Plain text 본문
        body = f"""
안녕하세요,

새로운 정부지원사업 {len(projects)}건이 등록되었습니다.

"""
        for i, project in enumerate(projects[:5], 1):
            body += f"""
{i}. {project.get('project_name', 'N/A')}
   - 기관: {project.get('agency', 'N/A')}
   - 마감일: {project.get('application_end_date', 'N/A')}
   - URL: {project.get('project_url', 'N/A')}

"""

        if len(projects) > 5:
            body += f"\n외 {len(projects) - 5}건...\n"

        body += """
자세한 내용은 GovPlan_AI 대시보드에서 확인하세요.

감사합니다.
GovPlan_AI 팀
"""

        # HTML 본문
        html_body = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; }}
        .header {{ background-color: #4CAF50; color: white; padding: 20px; text-align: center; }}
        .content {{ padding: 20px; }}
        .project-card {{ border: 1px solid #ddd; padding: 15px; margin: 10px 0; border-radius: 5px; }}
        .project-title {{ font-size: 18px; font-weight: bold; color: #333; }}
        .project-info {{ color: #666; margin-top: 5px; }}
        .footer {{ background-color: #f1f1f1; padding: 10px; text-align: center; font-size: 12px; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🎯 신규 정부지원사업 알림</h1>
        <p>새로운 지원사업 {len(projects)}건이 등록되었습니다</p>
    </div>
    <div class="content">
        <p>안녕하세요,</p>
        <p>귀하에게 적합한 정부지원사업이 새로 등록되었습니다.</p>
"""

        for i, project in enumerate(projects[:5], 1):
            html_body += f"""
        <div class="project-card">
            <div class="project-title">{i}. {project.get('project_name', 'N/A')}</div>
            <div class="project-info">
                📍 시행기관: {project.get('agency', 'N/A')}<br>
                📅 신청 마감: {project.get('application_end_date', 'N/A')}<br>
                💰 지원 금액: {project.get('support_amount', 'N/A')}<br>
                🔗 <a href="{project.get('project_url', '#')}">자세히 보기</a>
            </div>
        </div>
"""

        if len(projects) > 5:
            html_body += f"<p><strong>외 {len(projects) - 5}건...</strong></p>"

        html_body += """
        <p>자세한 내용은 <a href="http://localhost:8000">GovPlan_AI 대시보드</a>에서 확인하세요.</p>
    </div>
    <div class="footer">
        <p>GovPlan_AI - 정부지원사업 자동화 플랫폼</p>
    </div>
</body>
</html>
"""

        return self.send_email(to_emails, subject, body, html_body)

    def send_matching_notification(
        self,
        to_emails: List[str],
        company_name: str,
        matches: List[Dict]
    ) -> bool:
        """
        매칭 결과 알림 이메일 발송

        Args:
            to_emails: 수신자 이메일 리스트
            company_name: 기업명
            matches: 매칭 결과 리스트

        Returns:
            발송 성공 여부
        """

        if not matches:
            return False

        # 점수별 분류
        excellent = [m for m in matches if m.get('match_score', 0) >= 80]
        good = [m for m in matches if 60 <= m.get('match_score', 0) < 80]

        subject = f"[GovPlan_AI] {company_name}님을 위한 맞춤 지원사업 추천"

        body = f"""
안녕하세요, {company_name}님

귀사에 적합한 정부지원사업 {len(matches)}건을 추천드립니다.

🔥 강력 추천 ({len(excellent)}건)
"""

        for i, match in enumerate(excellent[:3], 1):
            body += f"""
{i}. {match.get('project_name', 'N/A')} (매칭도: {match.get('match_score', 0):.1f}점)
   - 기관: {match.get('agency', 'N/A')}
   - 마감: {match.get('application_end_date', 'N/A')}

"""

        if good:
            body += f"\n✅ 추천 ({len(good)}건)\n"
            for i, match in enumerate(good[:3], 1):
                body += f"{i}. {match.get('project_name', 'N/A')} (매칭도: {match.get('match_score', 0):.1f}점)\n"

        body += """
더 많은 추천 사업은 대시보드에서 확인하세요.

감사합니다.
GovPlan_AI 팀
"""

        return self.send_email(to_emails, subject, body)

    def send_proposal_ready_notification(
        self,
        to_emails: List[str],
        company_name: str,
        project_name: str,
        proposal_id: int
    ) -> bool:
        """
        사업계획서 생성 완료 알림

        Args:
            to_emails: 수신자 이메일 리스트
            company_name: 기업명
            project_name: 지원사업명
            proposal_id: 사업계획서 ID

        Returns:
            발송 성공 여부
        """

        subject = f"[GovPlan_AI] {project_name} 사업계획서가 준비되었습니다"

        body = f"""
안녕하세요, {company_name}님

요청하신 '{project_name}' 사업계획서가 AI에 의해 자동으로 생성되었습니다.

📄 사업계획서 다운로드:
- PDF: http://localhost:8000/api/v1/proposals/{proposal_id}/download/pdf
- DOCX: http://localhost:8000/api/v1/proposals/{proposal_id}/download/docx

사업계획서를 검토하신 후 필요에 따라 수정하여 사용하시기 바랍니다.

감사합니다.
GovPlan_AI 팀
"""

        html_body = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; }}
        .header {{ background-color: #2196F3; color: white; padding: 20px; text-align: center; }}
        .content {{ padding: 20px; }}
        .button {{ background-color: #4CAF50; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; display: inline-block; margin: 5px; }}
        .footer {{ background-color: #f1f1f1; padding: 10px; text-align: center; font-size: 12px; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>📄 사업계획서 준비 완료</h1>
    </div>
    <div class="content">
        <p>안녕하세요, <strong>{company_name}</strong>님</p>
        <p>요청하신 '<strong>{project_name}</strong>' 사업계획서가 AI에 의해 자동으로 생성되었습니다.</p>

        <h3>📥 다운로드:</h3>
        <a href="http://localhost:8000/api/v1/proposals/{proposal_id}/download/pdf" class="button">PDF 다운로드</a>
        <a href="http://localhost:8000/api/v1/proposals/{proposal_id}/download/docx" class="button">DOCX 다운로드</a>

        <p style="margin-top: 20px;">사업계획서를 검토하신 후 필요에 따라 수정하여 사용하시기 바랍니다.</p>
    </div>
    <div class="footer">
        <p>GovPlan_AI - 정부지원사업 자동화 플랫폼</p>
    </div>
</body>
</html>
"""

        return self.send_email(to_emails, subject, body, html_body)
