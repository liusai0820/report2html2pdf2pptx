
"""
邮件处理模块 (Mock)
"""
import logging

logger = logging.getLogger(__name__)

def save_to_drafts(email, subject, body, pdf_path=None):
    """
    将邮件保存为草稿 (Mock 实现)
    """
    logger.info(f"📧 Mock Mailer: Saving draft for {email}")
    logger.info(f"Subject: {subject}")
    if pdf_path:
        logger.info(f"Attachment: {pdf_path}")
    return True

def send_mail(to_email, subject, body, attachment_path=None):
    """
    发送邮件 (Mock 实现)
    """
    logger.info(f"🚀 Mock Mailer: Sending email to {to_email}")
    return True
