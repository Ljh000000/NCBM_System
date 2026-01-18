"""
邮件通知模块
"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import logging

logger = logging.getLogger(__name__)


class EmailNotifier:
    """邮件通知类"""
    
    def __init__(self, config):
        """
        初始化邮件通知器
        
        Args:
            config: Config对象
        """
        self.config = config
        self.email_config = config.get_email_config()
        self.enabled = self.email_config['enabled']
    
    def send_alert(self, device_name, diff_result):
        """
        发送配置变更告警邮件
        
        Args:
            device_name: 设备名称
            diff_result: 差异对比结果
            
        Returns:
            是否发送成功
        """
        if not self.enabled:
            logger.info("邮件通知未启用")
            return False
        
        try:
            # 构建邮件内容
            subject = f"网络设备配置变更告警 - {device_name}"
            
            summary = diff_result.get('summary', '配置已变更')
            diff_text = diff_result.get('diff', '')
            
            body = f"""
网络设备配置变更告警

设备名称: {device_name}
变更摘要: {summary}

详细差异:
{diff_text}

---
此邮件由网络设备配置备份与管理系统自动发送
"""
            
            # 发送邮件
            return self._send_email(subject, body)
            
        except Exception as e:
            logger.error(f"发送告警邮件时发生错误: {str(e)}")
            return False
    
    def _send_email(self, subject, body):
        """
        发送邮件
        
        Args:
            subject: 邮件主题
            body: 邮件正文
            
        Returns:
            是否发送成功
        """
        try:
            msg = MIMEMultipart()
            msg['From'] = self.email_config['from_email']
            msg['To'] = ', '.join(self.email_config['to_emails'])
            msg['Subject'] = subject
            
            msg.attach(MIMEText(body, 'plain', 'utf-8'))
            
            smtp_port = self.email_config['smtp_port']
            smtp_server = self.email_config['smtp_server']
            
            # 根据端口选择SSL或TLS连接
            # 465端口使用SSL，587端口使用TLS
            if smtp_port == 465:
                # 使用SSL连接
                server = smtplib.SMTP_SSL(smtp_server, smtp_port)
            else:
                # 使用TLS连接
                server = smtplib.SMTP(smtp_server, smtp_port)
                server.starttls()
            
            server.login(
                self.email_config['smtp_user'],
                self.email_config['smtp_password']
            )
            
            server.send_message(msg)
            server.quit()
            
            logger.info("告警邮件发送成功")
            return True
            
        except Exception as e:
            logger.error(f"发送邮件时发生错误: {str(e)}")
            return False

