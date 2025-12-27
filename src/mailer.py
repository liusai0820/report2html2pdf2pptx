import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
import config
import logging
import os
from pathlib import Path

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def send_email(to_email: str, subject: str, body: str, attachment_path: str = None):
    """
    发送邮件（支持 HTML，可选附件）
    """
    if not config.SMTP_ENABLED:
        logger.warning("SMTP 未配置，跳过邮件发送")
        return False

    try:
        msg = MIMEMultipart()
        msg['From'] = config.SMTP_USER
        msg['To'] = to_email
        msg['Subject'] = subject

        # HTML 正文
        msg.attach(MIMEText(body, 'html'))

        # 添加附件
        if attachment_path and os.path.exists(attachment_path):
            with open(attachment_path, "rb") as f:
                # 简单处理，如果是 PDF 就用 pdf subtype，否则 binary
                if attachment_path.lower().endswith('.pdf'):
                    subtype = "pdf"
                else:
                    subtype = "octet-stream"
                    
                part = MIMEApplication(f.read(), _subtype=subtype)
                part.add_header(
                    'Content-Disposition', 
                    'attachment', 
                    filename=os.path.basename(attachment_path)
                )
                msg.attach(part)

        # 连接 SMTP 服务器
        if config.SMTP_SSL:
            server = smtplib.SMTP_SSL(config.SMTP_HOST, config.SMTP_PORT)
        else:
            server = smtplib.SMTP(config.SMTP_HOST, config.SMTP_PORT)
            server.starttls()

        server.login(config.SMTP_USER, config.SMTP_PASSWORD)
        server.send_message(msg)
        server.quit()

        logger.info(f"邮件已成功发送至 {to_email}")
        return True

    except Exception as e:
        logger.error(f"邮件发送失败: {e}")
        return False

# 兼容旧接口
send_email_with_pdf = lambda to, sub, body, pdf: send_email(to, sub, body, pdf)

def save_to_drafts(to_email: str, subject: str, body: str, pdf_path: str = None):
    """
    将邮件保存到 Gmail 草稿箱 (不发送)
    """
    import imaplib
    import time
    
    if not config.SMTP_ENABLED:
        return False

    try:
        # 1. 构建邮件对象
        msg = MIMEMultipart()
        msg['From'] = config.SMTP_USER
        msg['To'] = to_email
        msg['Subject'] = subject
        msg['Date'] = imaplib.Time2Internaldate(time.time())
        
        msg.attach(MIMEText(body, 'html'))

        if pdf_path and os.path.exists(pdf_path):
            with open(pdf_path, "rb") as f:
                pdf_attachment = MIMEApplication(f.read(), _subtype="pdf")
                pdf_attachment.add_header(
                    'Content-Disposition', 
                    'attachment', 
                    filename=os.path.basename(pdf_path)
                )
                msg.attach(pdf_attachment)

        # 2. 连接 IMAP 服务器保存草稿
        # Gmail 的 IMAP 地址通常是 imap.gmail.com
        imap_host = "imap.gmail.com" 
        imap = imaplib.IMAP4_SSL(imap_host)
        imap.login(config.SMTP_USER, config.SMTP_PASSWORD)
        
        # 选择草稿箱
        # 常见名称：'[Gmail]/Drafts', 'Drafts', '[Gmail]/&g0l6Pw-' (中文'草稿')
        draft_box = None
        
        # 1. 尝试常见名称
        candidates = ['[Gmail]/&g0l6Pw-', '[Gmail]/Drafts', 'Drafts', '草稿']
        for box in candidates:
            try:
                status, _ = imap.select(box)
                if status == 'OK':
                    draft_box = box
                    break
            except:
                pass
        
        # 2. 如果没找到，尝试通过 list 查找带 \Drafts 属性的文件夹
        if not draft_box:
            try:
                _, folders = imap.list()
                for f in folders:
                    # layout: b'(\HasNoChildren \Drafts) "/" "[Gmail]/&g0l6Pw-"'
                    desc = f.decode()
                    if '\\Drafts' in desc or '\\Draft' in desc:
                        # 解析出文件夹名，通常在最后，用引号包围
                        import shlex
                        parts = shlex.split(desc)
                        if parts:
                            draft_box = parts[-1]
                            imap.select(draft_box)
                            break
            except Exception as e:
                logger.error(f"Failed to search for drafts folder: {e}")

        if not draft_box:
            logger.error("Could not find Drafts folder")
            return False

        logger.info(f"Saving to drafts folder: {draft_box}")
            
        # Append 进去
        # appending requires the message to be bytes
        imap.append(draft_box, '', imaplib.Time2Internaldate(time.time()), msg.as_bytes())
        imap.logout()
        
        logger.info(f"邮件草稿已保存: {to_email}")
        return True
        
    except Exception as e:
        logger.error(f"保存草稿失败: {e}")
        return False
