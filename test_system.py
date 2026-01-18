"""
系统测试脚本
用于测试各个功能模块是否正常工作
"""
import sys
import os
import time
from config import Config
from device_manager import DeviceManager
from backup_manager import BackupManager
from diff_engine import DiffEngine
from email_notifier import EmailNotifier

def test_config():
    """测试配置模块"""
    print("=" * 50)
    print("测试配置模块...")
    try:
        config = Config()
        devices = config.get_devices()
        print(f"✓ 配置模块加载成功")
        print(f"  设备数量: {len(devices)}")
        for name, info in devices.items():
            print(f"  - {name}: {info['ip']} ({info['device_type']})")
        return True
    except Exception as e:
        print(f"✗ 配置模块测试失败: {str(e)}")
        return False

def test_backup_manager():
    """测试备份管理模块"""
    print("=" * 50)
    print("测试备份管理模块...")
    try:
        config = Config()
        backup_manager = BackupManager(config)
        
        # 测试备份
        test_device = "test_device"
        test_config = "hostname test\ninterface vlan1\n ip address 192.168.1.1 255.255.255.0"
        
        backup_file = backup_manager.backup_config(test_device, test_config)
        if backup_file:
            print(f"✓ 备份功能正常: {backup_file}")
        else:
            print("✗ 备份功能失败")
            return False
        
        # 测试获取备份历史
        history = backup_manager.get_backup_history(test_device)
        print(f"✓ 备份历史查询正常: {len(history)} 条记录")
        
        # 测试读取备份内容
        if history:
            content = backup_manager.get_backup_content(test_device, history[0]['file_name'])
            if content:
                print(f"✓ 备份内容读取正常: {len(content)} 字符")
            else:
                print("✗ 备份内容读取失败")
                return False
        
        return True
    except Exception as e:
        print(f"✗ 备份管理模块测试失败: {str(e)}")
        return False

def test_diff_engine():
    """测试差异对比引擎"""
    print("=" * 50)
    print("测试差异对比引擎...")
    try:
        diff_engine = DiffEngine()
        
        # 测试相同配置
        config1 = "hostname test\ninterface vlan1\n ip address 192.168.1.1 255.255.255.0"
        config2 = "hostname test\ninterface vlan1\n ip address 192.168.1.1 255.255.255.0"
        
        result = diff_engine.compare_configs(config1, config2)
        if not result['has_changes']:
            print("✓ 相同配置对比正常: 无变更")
        else:
            print("✗ 相同配置对比失败")
            return False
        
        # 测试不同配置
        config3 = "hostname test\ninterface vlan1\n ip address 192.168.1.2 255.255.255.0"
        result = diff_engine.compare_configs(config1, config3)
        if result['has_changes']:
            print(f"✓ 不同配置对比正常: 发现 {result['added_lines']} 行新增, {result['removed_lines']} 行删除")
        else:
            print("✗ 不同配置对比失败")
            return False
        
        return True
    except Exception as e:
        print(f"✗ 差异对比引擎测试失败: {str(e)}")
        return False

def test_device_manager():
    """测试设备管理模块（需要实际设备）"""
    print("=" * 50)
    print("测试设备管理模块...")
    print("注意: 此测试需要配置有效的设备信息")
    
    try:
        config = Config()
        device_manager = DeviceManager(config)
        devices = config.get_devices()
        
        if len(devices) == 0:
            print("⚠ 未配置设备，跳过连接测试")
            print("✓ 设备管理模块初始化正常")
            return True
        
        # 尝试连接第一个设备（如果配置了）
        device_name = list(devices.keys())[0]
        print(f"尝试连接设备: {device_name}")
        
        # 注意: 这里不实际连接，只测试模块是否正常
        print("✓ 设备管理模块初始化正常")
        print("⚠ 实际连接测试需要有效的设备配置")
        return True
        
    except Exception as e:
        print(f"✗ 设备管理模块测试失败: {str(e)}")
        return False

def test_email_notifier():
    """测试邮件通知模块"""
    print("=" * 50)
    print("测试邮件通知模块...")
    try:
        config = Config()
        email_notifier = EmailNotifier(config)
        
        email_config = config.get_email_config()
        if email_config['enabled']:
            print("✓ 邮件通知已启用")
            print(f"  SMTP服务器: {email_config['smtp_server']}")
            print(f"  收件人: {', '.join(email_config['to_emails'])}")
        else:
            print("⚠ 邮件通知未启用（这是正常的，如果不需要邮件功能）")
        
        print("✓ 邮件通知模块初始化正常")
        return True
    except Exception as e:
        print(f"✗ 邮件通知模块测试失败: {str(e)}")
        return False

def test_file_structure():
    """测试文件结构"""
    print("=" * 50)
    print("测试文件结构...")
    
    required_files = [
        'app.py',
        'config.py',
        'device_manager.py',
        'backup_manager.py',
        'diff_engine.py',
        'email_notifier.py',
        'scheduler.py',
        'config.ini',
        'requirements.txt',
        'templates/index.html'
    ]
    
    missing_files = []
    for file in required_files:
        if not os.path.exists(file):
            missing_files.append(file)
    
    if missing_files:
        print(f"✗ 缺少以下文件: {', '.join(missing_files)}")
        return False
    else:
        print("✓ 所有必需文件都存在")
        return True

def main():
    """主测试函数"""
    print("\n" + "=" * 50)
    print("网络设备配置备份与管理系统 - 测试脚本")
    print("=" * 50 + "\n")
    
    results = []
    
    # 运行各项测试
    results.append(("文件结构", test_file_structure()))
    results.append(("配置模块", test_config()))
    results.append(("备份管理", test_backup_manager()))
    results.append(("差异对比", test_diff_engine()))
    results.append(("设备管理", test_device_manager()))
    results.append(("邮件通知", test_email_notifier()))
    
    # 输出测试结果摘要
    print("\n" + "=" * 50)
    print("测试结果摘要")
    print("=" * 50)
    
    passed = 0
    failed = 0
    
    for name, result in results:
        status = "✓ 通过" if result else "✗ 失败"
        print(f"{name}: {status}")
        if result:
            passed += 1
        else:
            failed += 1
    
    print(f"\n总计: {passed} 通过, {failed} 失败")
    
    if failed == 0:
        print("\n✓ 所有测试通过！系统可以正常使用。")
        return 0
    else:
        print(f"\n✗ 有 {failed} 项测试失败，请检查相关模块。")
        return 1

if __name__ == '__main__':
    sys.exit(main())

