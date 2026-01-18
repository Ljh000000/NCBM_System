"""
备份管理模块 - 负责配置备份的存储和检索
"""
import os
import shutil
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class BackupManager:
    """备份管理类"""
    
    def __init__(self, config):
        """
        初始化备份管理器
        
        Args:
            config: Config对象
        """
        self.config = config
        backup_config = config.get_backup_config()
        self.backup_dir = backup_config['backup_dir']
        self.retention_days = backup_config['retention_days']
        
        # 确保备份目录存在
        if not os.path.exists(self.backup_dir):
            os.makedirs(self.backup_dir)
            logger.info(f"创建备份目录: {self.backup_dir}")
    
    def get_device_backup_dir(self, device_name):
        """
        获取设备的备份目录路径
        
        Args:
            device_name: 设备名称
            
        Returns:
            目录路径
        """
        device_dir = os.path.join(self.backup_dir, device_name)
        if not os.path.exists(device_dir):
            os.makedirs(device_dir)
        return device_dir
    
    def backup_config(self, device_name, config_content):
        """
        备份设备配置
        
        Args:
            device_name: 设备名称
            config_content: 配置内容
            
        Returns:
            备份文件路径或None
        """
        try:
            device_dir = self.get_device_backup_dir(device_name)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_file = os.path.join(device_dir, f"{timestamp}.cfg")
            
            logger.info(f"[{device_name}] 保存备份文件: {backup_file}")
            with open(backup_file, 'w', encoding='utf-8') as f:
                f.write(config_content)
            
            # 验证文件是否成功写入
            if os.path.exists(backup_file):
                file_size = os.path.getsize(backup_file)
                logger.info(f"[{device_name}] 备份文件保存成功: {backup_file} (大小: {file_size} 字节)")
                return backup_file
            else:
                logger.error(f"[{device_name}] 备份文件保存失败: 文件不存在")
                return None
            
        except PermissionError as e:
            logger.error(f"[{device_name}] 备份配置时权限错误: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"[{device_name}] 备份配置时发生错误: {str(e)}", exc_info=True)
            return None
    
    def get_backup_history(self, device_name):
        """
        获取设备的备份历史
        
        Args:
            device_name: 设备名称
            
        Returns:
            备份历史列表，按时间倒序
        """
        history = []
        
        try:
            # 先检查设备目录是否存在，如果不存在直接返回空列表
            device_dir = os.path.join(self.backup_dir, device_name)
            if not os.path.exists(device_dir):
                logger.debug(f"备份目录不存在: {device_dir}，返回空列表")
                return history
            
            # 检查是否为目录
            if not os.path.isdir(device_dir):
                logger.warning(f"路径不是目录: {device_dir}")
                return history
            
            # 使用try-except包装文件操作，避免单个文件错误影响整体
            try:
                files = os.listdir(device_dir)
            except (PermissionError, OSError) as e:
                logger.error(f"无法读取目录 {device_dir}: {str(e)}")
                return history
            
            logger.debug(f"找到 {len(files)} 个文件在目录 {device_dir}")
            
            # 如果没有文件，直接返回空列表
            if not files:
                logger.debug(f"目录 {device_dir} 为空")
                return history
            
            for file in files:
                if not file.endswith('.cfg'):
                    continue
                    
                try:
                    file_path = os.path.join(device_dir, file)
                    
                    # 检查文件是否存在且可访问
                    if not os.path.exists(file_path):
                        logger.warning(f"文件不存在: {file_path}")
                        continue
                    
                    # 检查是否为文件（不是目录）
                    if not os.path.isfile(file_path):
                        logger.debug(f"跳过非文件项: {file_path}")
                        continue
                    
                    try:
                        stat = os.stat(file_path)
                    except (OSError, PermissionError) as e:
                        logger.warning(f"无法获取文件状态 {file_path}: {str(e)}")
                        continue
                    
                    # 从文件名提取时间戳
                    timestamp_str = file.replace('.cfg', '')
                    try:
                        timestamp = datetime.strptime(timestamp_str, '%Y%m%d_%H%M%S')
                    except ValueError:
                        # 如果文件名格式不正确，使用文件修改时间
                        try:
                            timestamp = datetime.fromtimestamp(stat.st_mtime)
                            logger.debug(f"使用文件修改时间作为时间戳: {file}")
                        except (OSError, ValueError) as e:
                            logger.warning(f"无法解析时间戳 {file}: {str(e)}")
                            continue
                    
                    history.append({
                        'timestamp': timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                        'file_path': file_path,
                        'file_name': file,
                        'size': stat.st_size,
                        'size_human': self._format_size(stat.st_size)
                    })
                except Exception as e:
                    # 单个文件处理失败，记录日志但继续处理其他文件
                    logger.warning(f"处理文件 {file} 时出错: {str(e)}")
                    continue
            
            # 按时间倒序排序
            history.sort(key=lambda x: x['timestamp'], reverse=True)
            logger.info(f"成功获取 {len(history)} 条备份历史记录")
            
        except Exception as e:
            logger.error(f"获取备份历史时发生错误: {str(e)}", exc_info=True)
        
        return history
    
    def get_latest_backup(self, device_name):
        """
        获取最新的备份文件
        
        Args:
            device_name: 设备名称
            
        Returns:
            最新备份文件路径或None
        """
        history = self.get_backup_history(device_name)
        if history:
            return history[0]['file_path']
        return None
    
    def get_backup_content(self, device_name, backup_file):
        """
        获取备份文件内容
        
        Args:
            device_name: 设备名称
            backup_file: 备份文件名
            
        Returns:
            文件内容或None
        """
        device_dir = self.get_device_backup_dir(device_name)
        file_path = os.path.join(device_dir, backup_file)
        
        if not os.path.exists(file_path):
            logger.error(f"备份文件不存在: {file_path}")
            return None
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            logger.error(f"读取备份文件时发生错误: {str(e)}")
            return None
    
    def delete_backup(self, device_name, backup_file):
        """
        删除备份文件
        
        Args:
            device_name: 设备名称
            backup_file: 备份文件名
            
        Returns:
            是否删除成功
        """
        device_dir = self.get_device_backup_dir(device_name)
        file_path = os.path.join(device_dir, backup_file)
        
        if not os.path.exists(file_path):
            logger.error(f"备份文件不存在: {file_path}")
            return False
        
        try:
            os.remove(file_path)
            logger.info(f"删除备份文件: {file_path}")
            return True
        except Exception as e:
            logger.error(f"删除备份文件时发生错误: {str(e)}")
            return False
    
    def cleanup_old_backups(self, device_name=None):
        """
        清理过期备份
        
        Args:
            device_name: 设备名称，如果为None则清理所有设备
        """
        from datetime import timedelta
        
        devices = [device_name] if device_name else os.listdir(self.backup_dir)
        cutoff_date = datetime.now() - timedelta(days=self.retention_days)
        
        for dev in devices:
            if not os.path.isdir(os.path.join(self.backup_dir, dev)):
                continue
                
            device_dir = self.get_device_backup_dir(dev)
            files = os.listdir(device_dir)
            
            for file in files:
                if file.endswith('.cfg'):
                    file_path = os.path.join(device_dir, file)
                    timestamp_str = file.replace('.cfg', '')
                    
                    try:
                        file_timestamp = datetime.strptime(timestamp_str, '%Y%m%d_%H%M%S')
                        if file_timestamp < cutoff_date:
                            os.remove(file_path)
                            logger.info(f"清理过期备份: {file_path}")
                    except:
                        # 如果无法解析时间戳，使用文件修改时间
                        stat = os.stat(file_path)
                        if datetime.fromtimestamp(stat.st_mtime) < cutoff_date:
                            os.remove(file_path)
                            logger.info(f"清理过期备份: {file_path}")
    
    def _format_size(self, size):
        """格式化文件大小"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} TB"

