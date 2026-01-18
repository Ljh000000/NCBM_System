"""
邮件发送测试脚本
用于测试邮件通知功能是否正常工作
"""
import sys
import logging
from config import Config
from email_notifier import EmailNotifier
from diff_engine import DiffEngine

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def test_email_send():
    """测试发送邮件"""
    print("=" * 60)
    print("邮件发送测试")
    print("=" * 60)
    
    try:
        # 加载配置
        config = Config()
        email_config = config.get_email_config()
        
        # 检查邮件是否启用
        if not email_config['enabled']:
            print("❌ 邮件功能未启用！")
            print("请在 config.ini 中设置 [email] enabled = true")
            return False
        
        print(f"\n邮件配置信息:")
        print(f"  SMTP服务器: {email_config['smtp_server']}")
        print(f"  SMTP端口: {email_config['smtp_port']}")
        print(f"  发件人: {email_config['from_email']}")
        print(f"  收件人: {', '.join(email_config['to_emails'])}")
        
        # 创建邮件通知器
        email_notifier = EmailNotifier(config)
        
        # 创建差异对比引擎
        diff_engine = DiffEngine()
        
        # 模拟配置变更场景
        print("\n" + "-" * 60)
        print("模拟配置变更场景...")
        
        old_config = """hostname router1
interface GigabitEthernet0/0
 ip address 192.168.1.1 255.255.255.0
 no shutdown
!
interface GigabitEthernet0/1
 ip address 192.168.2.1 255.255.255.0
 no shutdown
"""
        
        new_config = """hostname router1
interface GigabitEthernet0/0
 ip address 192.168.1.1 255.255.255.0
 no shutdown
!
interface GigabitEthernet0/1
 ip address 192.168.2.10 255.255.255.0  # IP地址已变更
 no shutdown
!
interface GigabitEthernet0/2  # 新增接口
 ip address 192.168.3.1 255.255.255.0
 no shutdown
"""
        
        # 进行差异对比
        diff_result = diff_engine.compare_configs(old_config, new_config)
        diff_result['summary'] = diff_engine.get_summary(diff_result)
        
        print(f"  变更摘要: {diff_result['summary']}")
        print(f"  发现变更: {'是' if diff_result['has_changes'] else '否'}")
        
        # 发送测试邮件
        print("\n" + "-" * 60)
        print("正在发送测试邮件...")
        
        device_name = "test_device"
        success = email_notifier.send_alert(device_name, diff_result)
        
        if success:
            print("\n✅ 测试邮件发送成功！")
            print(f"   请检查收件箱: {', '.join(email_config['to_emails'])}")
            return True
        else:
            print("\n❌ 测试邮件发送失败！")
            print("   请检查:")
            print("   1. SMTP服务器地址和端口是否正确")
            print("   2. 用户名和密码是否正确")
            print("   3. 是否已开启SMTP服务（163邮箱需要开启）")
            print("   4. 网络连接是否正常")
            return False
            
    except Exception as e:
        print(f"\n❌ 测试过程中发生错误: {str(e)}")
        logger.exception("邮件测试失败")
        return False


if __name__ == '__main__':
    print("\n")
    success = test_email_send()
    print("\n" + "=" * 60)
    sys.exit(0 if success else 1)

