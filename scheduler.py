"""
定时任务调度器
"""
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime
import os
import logging

logger = logging.getLogger(__name__)


class BackupScheduler:
    """备份任务调度器"""
    
    def __init__(self, config, device_manager, backup_manager, diff_engine, email_notifier):
        """
        初始化调度器
        
        Args:
            config: Config对象
            device_manager: DeviceManager对象
            backup_manager: BackupManager对象
            diff_engine: DiffEngine对象
            email_notifier: EmailNotifier对象
        """
        self.config = config
        self.device_manager = device_manager
        self.backup_manager = backup_manager
        self.diff_engine = diff_engine
        self.email_notifier = email_notifier
        
        self.scheduler = BackgroundScheduler()
        self.scheduler_config = config.get_scheduler_config()
        self.enabled = self.scheduler_config['enabled']
        
        if self.enabled:
            self._setup_schedule()
    
    def _setup_schedule(self):
        """设置定时任务"""
        backup_time = self.scheduler_config['backup_time']
        timezone = self.scheduler_config.get('timezone', 'Asia/Shanghai')
        
        try:
            hour, minute = map(int, backup_time.split(':'))
        except ValueError:
            logger.error(f"备份时间格式错误: {backup_time}，使用默认时间 10:10")
            hour, minute = 10, 10
        
        # 每天指定时间执行备份
        # 注意: APScheduler会自动处理时区，如果pytz未安装则使用系统时区
        try:
            from pytz import timezone as tz
            tz_obj = tz(timezone)
            logger.info(f"使用时区: {timezone}")
        except ImportError:
            logger.warning(f"pytz未安装，使用系统默认时区")
            tz_obj = None
        except Exception as e:
            logger.warning(f"时区 {timezone} 无效: {str(e)}，使用系统默认时区")
            tz_obj = None
        
        self.scheduler.add_job(
            func=self.backup_all_devices,
            trigger=CronTrigger(hour=hour, minute=minute, timezone=tz_obj),
            id='daily_backup',
            name='每日自动备份',
            replace_existing=True
        )
        
        logger.info(f"定时任务已设置: 每天 {backup_time} 执行备份 (时区: {timezone})")
        
        # 获取下次执行时间（需要在调度器启动后）
        # 注意：此时调度器可能还未启动，所以不在这里获取
    
    def backup_all_devices(self):
        """备份所有设备"""
        logger.info("=" * 60)
        logger.info("开始执行定时备份任务")
        logger.info(f"当前时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        devices = self.device_manager.devices
        logger.info(f"需要备份的设备数量: {len(devices)}")
        
        if not devices:
            logger.warning("没有配置设备，跳过备份任务")
            return
        
        success_count = 0
        fail_count = 0
        
        for device_name in devices:
            try:
                logger.info(f"开始备份设备: {device_name}")
                self._backup_device(device_name)
                success_count += 1
                logger.info(f"设备 {device_name} 备份完成")
            except Exception as e:
                fail_count += 1
                logger.error(f"备份设备 {device_name} 时发生错误: {str(e)}", exc_info=True)
        
        logger.info(f"备份任务完成: 成功 {success_count} 个, 失败 {fail_count} 个")
        
        # 清理过期备份
        try:
            logger.info("开始清理过期备份")
            self.backup_manager.cleanup_old_backups()
            logger.info("过期备份清理完成")
        except Exception as e:
            logger.error(f"清理过期备份时发生错误: {str(e)}", exc_info=True)
        
        logger.info("=" * 60)
    
    def _backup_device(self, device_name):
        """
        备份单个设备并检查差异
        
        Args:
            device_name: 设备名称
        """
        try:
            logger.info(f"[{device_name}] 步骤1: 开始获取设备配置")
            # 获取当前配置
            config_content = self.device_manager.get_config(device_name)
            if not config_content:
                logger.error(f"[{device_name}] 无法获取设备配置，可能原因: 设备连接失败、命令执行失败或设备无响应")
                return
            
            logger.info(f"[{device_name}] 配置获取成功，配置长度: {len(config_content)} 字符")
            
            # 获取最新备份
            logger.info(f"[{device_name}] 步骤2: 获取最新备份记录")
            latest_backup = self.backup_manager.get_latest_backup(device_name)
            if latest_backup:
                logger.info(f"[{device_name}] 找到最新备份: {os.path.basename(latest_backup)}")
            else:
                logger.info(f"[{device_name}] 这是首次备份，无历史记录")
            
            # 备份当前配置
            logger.info(f"[{device_name}] 步骤3: 保存配置到备份文件")
            backup_file = self.backup_manager.backup_config(device_name, config_content)
            if not backup_file:
                logger.error(f"[{device_name}] 备份文件保存失败")
                return
            
            logger.info(f"[{device_name}] 备份文件已保存: {backup_file}")
            
            # 如果有之前的备份，进行差异对比
            if latest_backup:
                logger.info(f"[{device_name}] 步骤4: 对比配置差异")
                old_config = self.backup_manager.get_backup_content(
                    device_name,
                    os.path.basename(latest_backup)
                )
                
                if old_config:
                    diff_result = self.diff_engine.compare_configs(old_config, config_content)
                    
                    if self.diff_engine.has_changes(diff_result):
                        logger.warning(f"[{device_name}] 配置已变更: {self.diff_engine.get_summary(diff_result)}")
                        diff_result['summary'] = self.diff_engine.get_summary(diff_result)
                        # 发送告警邮件
                        logger.info(f"[{device_name}] 步骤5: 发送配置变更告警邮件")
                        email_result = self.email_notifier.send_alert(device_name, diff_result)
                        if email_result:
                            logger.info(f"[{device_name}] 告警邮件发送成功")
                        else:
                            logger.warning(f"[{device_name}] 告警邮件发送失败")
                    else:
                        logger.info(f"[{device_name}] 配置无变更")
                else:
                    logger.warning(f"[{device_name}] 无法读取历史备份文件内容")
            else:
                logger.info(f"[{device_name}] 首次备份，跳过差异对比")
                
        except Exception as e:
            logger.error(f"[{device_name}] 备份过程中发生异常: {str(e)}", exc_info=True)
            raise
    
    def start(self):
        """启动调度器"""
        if self.enabled and not self.scheduler.running:
            self.scheduler.start()
            logger.info("定时任务调度器已启动")
    
    def stop(self):
        """停止调度器"""
        if self.scheduler.running:
            self.scheduler.shutdown()
            logger.info("定时任务调度器已停止")
    
    def is_running(self):
        """检查调度器是否运行"""
        return self.scheduler.running
    
    def get_next_run_time(self):
        """获取下次运行时间"""
        if not self.enabled or not self.scheduler.running:
            return None
        
        try:
            job = self.scheduler.get_job('daily_backup')
            if job:
                # APScheduler 3.x 使用 next_run_time 属性
                return getattr(job, 'next_run_time', None)
        except Exception as e:
            logger.warning(f"获取下次运行时间失败: {str(e)}")
        return None

