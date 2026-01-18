"""
测试定时任务和日志功能
"""
import sys
import time
from config import Config
from device_manager import DeviceManager
from backup_manager import BackupManager
from diff_engine import DiffEngine
from email_notifier import EmailNotifier
from scheduler import BackupScheduler
import logging

logger = logging.getLogger(__name__)

def test_scheduler():
    """测试定时任务"""
    print("=" * 60)
    print("测试定时任务和日志功能")
    print("=" * 60)
    
    try:
        # 初始化配置
        config = Config()
        scheduler_config = config.get_scheduler_config()
        
        print(f"\n定时任务配置:")
        print(f"  启用状态: {scheduler_config['enabled']}")
        print(f"  备份时间: {scheduler_config['backup_time']}")
        print(f"  时区: {scheduler_config.get('timezone', 'Asia/Shanghai')}")
        
        # 初始化各个模块
        device_manager = DeviceManager(config)
        backup_manager = BackupManager(config)
        diff_engine = DiffEngine()
        email_notifier = EmailNotifier(config)
        
        # 创建调度器
        scheduler = BackupScheduler(
            config, device_manager, backup_manager, diff_engine, email_notifier
        )
        
        print(f"\n调度器状态:")
        print(f"  启用: {scheduler.enabled}")
        print(f"  运行中: {scheduler.is_running()}")
        
        # 获取下次运行时间
        next_run = scheduler.get_next_run_time()
        if next_run:
            print(f"  下次运行时间: {next_run.strftime('%Y-%m-%d %H:%M:%S')}")
        else:
            print(f"  下次运行时间: 未设置")
        
        # 启动调度器
        if scheduler.enabled:
            scheduler.start()
            print(f"\n调度器已启动")
            print(f"  运行状态: {scheduler.is_running()}")
            
            # 等待一下让调度器初始化
            time.sleep(0.5)
            
            # 再次获取下次运行时间
            next_run = scheduler.get_next_run_time()
            if next_run:
                print(f"  下次运行时间: {next_run.strftime('%Y-%m-%d %H:%M:%S')}")
            else:
                print(f"  下次运行时间: 无法获取（可能需要等待调度器完全启动）")
        else:
            print(f"\n调度器未启用")
        
        print(f"\n日志文件位置: logs/network_backup.log")
        print(f"请查看日志文件了解详细运行情况")
        
        return True
        
    except Exception as e:
        print(f"\n测试失败: {str(e)}")
        logger.exception("测试失败")
        return False

if __name__ == '__main__':
    success = test_scheduler()
    sys.exit(0 if success else 1)

