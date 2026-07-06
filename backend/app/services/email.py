from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from app.core.config import settings

# Example config - in a real app these come from settings / environment variables
conf = ConnectionConfig(
    MAIL_USERNAME=getattr(settings, "MAIL_USERNAME", "dummy"),
    MAIL_PASSWORD=getattr(settings, "MAIL_PASSWORD", "dummy"),
    MAIL_FROM=getattr(settings, "MAIL_FROM", "noreply@basmaplus.com"),
    MAIL_PORT=getattr(settings, "MAIL_PORT", 587),
    MAIL_SERVER=getattr(settings, "MAIL_SERVER", "smtp.dummy.com"),
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True
)

fm = FastMail(conf)

async def send_reset_password_email(email_to: str, reset_token: str):
    """
    Send an email with a reset password token/link.
    """
    # In production, construct a link to the frontend:
    # reset_link = f"http://localhost:5173/auth/reset-password?token={reset_token}"
    
    html = f"""
    <div style="font-family: Arial, sans-serif; text-align: right; direction: rtl;">
        <h2>إعادة تعيين كلمة المرور</h2>
        <p>لقد طلبت إعادة تعيين كلمة المرور الخاصة بك في بصمة+.</p>
        <p>رمز إعادة التعيين الخاص بك هو:</p>
        <h3 style="background-color: #f4f4f4; padding: 10px; display: inline-block;">{reset_token}</h3>
        <p>إذا لم تطلب ذلك، يرجى تجاهل هذه الرسالة.</p>
    </div>
    """

    message = MessageSchema(
        subject="إعادة تعيين كلمة المرور - بصمة+",
        recipients=[email_to],
        body=html,
        subtype=MessageType.html
    )

    if getattr(settings, "MAIL_SERVER", "smtp.dummy.com") == "smtp.dummy.com":
        # Mock mode
        import logging
        logger = logging.getLogger("basma_api")
        logger.info(f"Mock Email sent to {email_to} with token {reset_token}")
    else:
        await fm.send_message(message)
