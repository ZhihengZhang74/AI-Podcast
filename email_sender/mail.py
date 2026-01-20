"""
邮件发送模块 - 简洁版
"""

import smtplib
from email.mime.text import MIMEText
import sys
import os

# 添加上级目录到路径，以便在直接运行时能够导入 config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from email_sender.config import EMAIL_CONFIG


def send_email(to_email: str, subject: str, body: str) -> bool:
    """
    发送邮件

    参数:
        to_email: 收件人邮箱
        subject: 邮件主题
        body: 邮件内容

    返回:
        bool: 发送是否成功
    """
    server = EMAIL_CONFIG["smtp_server"]
    port = EMAIL_CONFIG["smtp_port"]
    sender = EMAIL_CONFIG["sender_email"]
    password = EMAIL_CONFIG["sender_password"]

    try:
        # 创建SSL连接
        print("正在连接SMTP服务器...")
        smtp = smtplib.SMTP_SSL(server, port, timeout=30)
        print("正在登录...")
        smtp.login(sender, password)
        print("正在发送邮件...")

        # 构建邮件（仅支持纯文本）
        msg = MIMEText(body, 'plain', 'utf-8')
        msg['From'] = sender
        msg['To'] = to_email
        msg['Subject'] = subject

        # 发送
        smtp.sendmail(sender, [to_email], msg.as_string())
        smtp.quit()

        print(f"✓ 邮件发送成功！发送给: {to_email}")
        return True

    except Exception as e:
        print(f"✗ 邮件发送失败: {e}")
        return False


if __name__ == "__main__":
    # 测试发送给自己
    send_email(
        to_email="2116417132@qq.com",
        subject="Python邮件测试",
        body="这是一封测试邮件，收到请回复！"
    )
