import smtplib
from smtplib import SMTP_SSL
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header

from logs import logger
from dotenv import load_dotenv
import os
load_dotenv()

host_server = 'smtp.163.com'  #smtp服务器
sender_qq = os.environ.get('Email') #发件人邮箱
email_token = os.environ.get('EMAIL_TOKEN')


def send_email(receiver,url):
    mail_title = 'chat注册信息' #邮件标题

    #邮件正文内容
    mail_content = f"您好，<p>感谢注册，请点击下面链接激活账号</p> <p><a href='{url}'>点击进行chat账号激活</a></p>"

    msg = MIMEMultipart()
    msg["Subject"] = Header(mail_title,'utf-8')
    msg["From"] = sender_qq
    msg["To"] = Header(receiver,"utf-8")

    msg.attach(MIMEText(mail_content,'html'))

    try:
        smtp = SMTP_SSL(host_server) # ssl登录连接到邮件服务器
        smtp.set_debuglevel(1) # 0是关闭，1是开启debug
        smtp.ehlo(host_server) # 跟服务器打招呼，告诉它我们准备连接，最好加上这行代码
        smtp.login(sender_qq,email_token)
        smtp.sendmail(sender_qq,receiver,msg.as_string())
        smtp.quit()
        logger.info(f"邮件发送成功:{receiver}")
    except smtplib.SMTPException:
        logger.error("无法发送邮件")