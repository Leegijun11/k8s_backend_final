import os
import secrets
import html
import string
import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
from pydantic import EmailStr

load_dotenv()


SMTP_SERVER = os.getenv("SMTP_SERVER")
SMTP_PORT = int(os.getenv("SMTP_PORT"))
SMTP_USERNAME = os.getenv("SMTP_USERNAME")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")

def generate_verification_code(length: int = 8) -> str:
    characters = string.ascii_letters + string.digits   
    return "".join(secrets.choice(characters) for _ in range(length))


async def send_verification_email_async(email_to: EmailStr, u_name: str, auth_code: str):
    safe_user_name = html.escape(u_name)
    email_html = f"""
    <h3>임시 비밀번호 발급 안내</h3>
    <p>안녕하세요, {safe_user_name}님.</p>
    <p>요청하신 비밀번호 찾기 처리가 완료되었습니다.</p>
    <p>아래의 임시 비밀번호로 로그인하신 후, 마이페이지에서 비밀번호를 새로 변경해 주세요.</p>
    <div style="padding: 15px; background-color: #f5f5f5; font-size: 24px; font-weight: bold; text-align: center; color: #d9534f; letter-spacing: 5px;">
        {auth_code}
    </div>
    """

    message = MIMEMultipart("alternative")
    message["From"] = SMTP_USERNAME
    message["To"] = email_to
    message["Subject"] = "[서비스명] 요청하신 임시 비밀번호를 안내해 드립니다."

    part_html = MIMEText(email_html, "html", "utf-8")
    message.attach(part_html)

    try:
        smtp = aiosmtplib.SMTP(hostname=SMTP_SERVER, port=SMTP_PORT, use_tls=False)
        await smtp.connect()
        await smtp.login(SMTP_USERNAME, SMTP_PASSWORD)
        await smtp.send_message(message)
        await smtp.quit()
    except Exception as e:
        raise RuntimeError(f"SMTP 이메일 전송 실패: {str(e)}")
