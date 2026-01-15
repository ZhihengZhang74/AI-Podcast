"""
邮件发送程序
"""
from email_sender.mail import send_email


def main():
    send_email(
        to_email="zhangzhiheng74@163.com",
        subject="Python邮件测试成功！",
        body="恭喜！你的邮件发送程序已经可以正常工作了！\n\n这是通过 Python 发送的测试邮件。"
    )

if __name__ == "__main__":
    main()
