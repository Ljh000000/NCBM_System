"""
配置文件读取模块
"""
import configparser
import os


class Config:
    """配置管理类"""
    
    def __init__(self, config_file='config.ini'):
        self.config_file = config_file
        self.config = configparser.ConfigParser()
        self.load_config()
    
    def load_config(self):
        """加载配置文件"""
        if os.path.exists(self.config_file):
            self.config.read(self.config_file, encoding='utf-8')
        else:
            # 创建默认配置
            self.create_default_config()
    
    def create_default_config(self):
        """创建默认配置文件"""
        self.config['devices'] = {}
        self.config['scheduler'] = {
            'enabled': 'true',
            'backup_time': '00:00',
            'timezone': 'Asia/Shanghai'
        }
        self.config['email'] = {
            'enabled': 'false',
            'smtp_server': 'smtp.example.com',
            'smtp_port': '587',
            'smtp_user': '',
            'smtp_password': '',
            'from_email': '',
            'to_emails': ''
        }
        self.config['backup'] = {
            'backup_dir': 'backups',
            'retention_days': '30',
            'command': 'show running-config'
        }
        self.save_config()
    
    def save_config(self):
        """保存配置文件"""
        with open(self.config_file, 'w', encoding='utf-8') as f:
            self.config.write(f)
    
    def get_devices(self):
        """获取所有设备配置"""
        devices = {}
        if 'devices' in self.config:
            for name, value in self.config['devices'].items():
                parts = value.split(',')
                if len(parts) >= 4:
                    devices[name] = {
                        'ip': parts[0],
                        'username': parts[1],
                        'password': parts[2],
                        'device_type': parts[3]
                    }
        return devices
    
    def get_scheduler_config(self):
        """获取定时任务配置"""
        return {
            'enabled': self.config.getboolean('scheduler', 'enabled', fallback=True),
            'backup_time': self.config.get('scheduler', 'backup_time', fallback='10:10'),
            'timezone': self.config.get('scheduler', 'timezone', fallback='Asia/Shanghai')
        }
    
    def get_email_config(self):
        """获取邮件配置"""
        return {
            'enabled': self.config.getboolean('email', 'enabled', fallback=False),
            'smtp_server': self.config.get('email', 'smtp_server', fallback=''),
            'smtp_port': self.config.getint('email', 'smtp_port', fallback=587),
            'smtp_user': self.config.get('email', 'smtp_user', fallback=''),
            'smtp_password': self.config.get('email', 'smtp_password', fallback=''),
            'from_email': self.config.get('email', 'from_email', fallback=''),
            'to_emails': self.config.get('email', 'to_emails', fallback='').split(',')
        }
    
    def get_backup_config(self):
        """获取备份配置"""
        return {
            'backup_dir': self.config.get('backup', 'backup_dir', fallback='backups'),
            'retention_days': self.config.getint('backup', 'retention_days', fallback=30),
            'command': self.config.get('backup', 'command', fallback='display current-configuration')
        }
    
    def add_device(self, name, ip, username, password, device_type):
        """
        添加设备
        
        Args:
            name: 设备名称
            ip: IP地址
            username: 用户名
            password: 密码
            device_type: 设备类型
            
        Returns:
            bool: 是否成功
        """
        try:
            if 'devices' not in self.config:
                self.config['devices'] = {}
            
            # 检查设备名称是否已存在
            if name in self.config['devices']:
                return False, '设备名称已存在'
            
            # 添加设备
            value = f"{ip},{username},{password},{device_type}"
            self.config['devices'][name] = value
            self.save_config()
            return True, '设备添加成功'
        except Exception as e:
            return False, f'添加设备失败: {str(e)}'
    
    def update_device(self, name, ip, username, password, device_type):
        """
        更新设备配置
        
        Args:
            name: 设备名称
            ip: IP地址
            username: 用户名
            password: 密码（如果为空则保持原密码）
            device_type: 设备类型
            
        Returns:
            bool, str: (是否成功, 消息)
        """
        try:
            if 'devices' not in self.config:
                return False, '设备配置不存在'
            
            if name not in self.config['devices']:
                return False, '设备不存在'
            
            # 如果密码为空，使用原密码
            if not password:
                old_value = self.config['devices'][name]
                old_parts = old_value.split(',')
                if len(old_parts) >= 4:
                    password = old_parts[2]  # 使用原密码
            
            # 更新设备
            value = f"{ip},{username},{password},{device_type}"
            self.config['devices'][name] = value
            self.save_config()
            return True, '设备更新成功'
        except Exception as e:
            return False, f'更新设备失败: {str(e)}'
    
    def delete_device(self, name):
        """
        删除设备
        
        Args:
            name: 设备名称
            
        Returns:
            bool, str: (是否成功, 消息)
        """
        try:
            if 'devices' not in self.config:
                return False, '设备配置不存在'
            
            if name not in self.config['devices']:
                return False, '设备不存在'
            
            # 删除设备
            del self.config['devices'][name]
            self.save_config()
            return True, '设备删除成功'
        except Exception as e:
            return False, f'删除设备失败: {str(e)}'

