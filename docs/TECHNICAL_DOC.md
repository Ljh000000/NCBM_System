# 网络设备配置备份与管理系统 - 技术文档

## 1. 项目概述

本项目是一个基于Python的网络设备配置备份与管理系统，主要用于自动备份网络设备（交换机/路由器）的配置，并提供配置差异对比和告警功能。

## 2. 技术架构

### 2.1 技术栈
- **后端框架**: Flask (Python Web框架)
- **网络连接库**: netmiko (SSH/Telnet连接)
- **配置对比**: difflib (Python标准库)
- **定时任务**: APScheduler
- **邮件发送**: smtplib (Python标准库)
- **前端**: Bootstrap 5 + HTML/CSS/JavaScript

### 2.2 项目结构
```
network/
├── app.py                 # Flask主应用
├── config.py             # 配置文件
├── device_manager.py     # 设备管理核心模块
├── backup_manager.py     # 备份管理模块
├── diff_engine.py        # 配置差异对比引擎
├── scheduler.py          # 定时任务调度器
├── email_notifier.py     # 邮件通知模块
├── templates/            # HTML模板
│   └── index.html
├── static/               # 静态资源
│   ├── css/
│   └── js/
├── backups/              # 配置备份存储目录
│   └── {device_name}/
│       └── {timestamp}.cfg
├── requirements.txt      # 依赖包列表
├── config.ini           # 配置文件
└── docs/                # 文档目录
    └── TECHNICAL_DOC.md
```

## 3. 核心功能模块

### 3.1 设备管理模块 (device_manager.py)
- **功能**: 管理网络设备连接信息
- **主要类**: `DeviceManager`
- **方法**:
  - `connect(device_name)`: 连接到指定设备
  - `execute_command(device_name, command)`: 执行命令
  - `get_config(device_name)`: 获取设备配置

### 3.2 备份管理模块 (backup_manager.py)
- **功能**: 管理配置备份的存储和检索
- **主要类**: `BackupManager`
- **方法**:
  - `backup_config(device_name, config)`: 备份配置到文件
  - `get_backup_history(device_name)`: 获取备份历史
  - `get_latest_backup(device_name)`: 获取最新备份

### 3.3 差异对比引擎 (diff_engine.py)
- **功能**: 对比两个配置文件的差异
- **主要类**: `DiffEngine`
- **方法**:
  - `compare_configs(old_config, new_config)`: 对比配置差异
  - `has_changes(diff_result)`: 判断是否有变更
  - `format_diff(diff_result)`: 格式化差异输出

### 3.4 定时任务调度器 (scheduler.py)
- **功能**: 定时执行配置备份任务
- **主要类**: `BackupScheduler`
- **方法**:
  - `schedule_backup(device_name, schedule_time)`: 安排备份任务
  - `start_scheduler()`: 启动调度器
  - `stop_scheduler()`: 停止调度器

### 3.5 邮件通知模块 (email_notifier.py)
- **功能**: 发送配置变更告警邮件
- **主要类**: `EmailNotifier`
- **方法**:
  - `send_alert(device_name, diff_result)`: 发送告警邮件

## 4. API接口设计

### 4.1 RESTful API

#### GET /api/devices
获取所有设备列表

**响应**:
```json
{
  "devices": [
    {
      "name": "switch1",
      "ip": "192.168.1.1",
      "type": "cisco_ios"
    }
  ]
}
```

#### POST /api/backup
手动触发备份

**请求体**:
```json
{
  "device_name": "switch1"
}
```

**响应**:
```json
{
  "status": "success",
  "message": "备份完成",
  "backup_file": "backups/switch1/20231219_120000.cfg"
}
```

#### GET /api/backup/history?device_name=switch1
获取备份历史

**响应**:
```json
{
  "history": [
    {
      "timestamp": "2023-12-19 12:00:00",
      "file_path": "backups/switch1/20231219_120000.cfg",
      "size": 1024
    }
  ]
}
```

#### GET /api/diff?device_name=switch1&backup1=xxx&backup2=yyy
获取配置差异

**响应**:
```json
{
  "has_changes": true,
  "diff": "--- old\n+++ new\n@@ -1,2 +1,3 @@\n..."
}
```

## 5. 配置文件说明

### config.ini
```ini
[devices]
# 设备配置格式: name=ip,username,password,device_type
switch1=192.168.1.1,admin,password123,cisco_ios
router1=192.168.1.2,admin,password123,cisco_ios

[scheduler]
# 定时任务配置
enabled=true
backup_time=02:00
timezone=Asia/Shanghai

[email]
# 邮件配置
enabled=true
smtp_server=smtp.example.com
smtp_port=587
smtp_user=your_email@example.com
smtp_password=your_password
from_email=your_email@example.com
to_emails=admin@example.com

[backup]
# 备份配置
backup_dir=backups
retention_days=30
```

## 6. 部署说明

### 6.1 环境要求
- Python 3.7+
- pip

### 6.2 安装步骤
1. 安装依赖: `pip install -r requirements.txt`
2. 配置设备信息: 编辑 `config.ini`
3. 运行应用: `python app.py`

### 6.3 运行模式
- 开发模式: `python app.py` (默认端口5000)
- 生产模式: 使用 gunicorn 或 uwsgi

## 7. 安全注意事项

1. **密码安全**: 配置文件中的密码应加密存储
2. **访问控制**: Web界面应添加认证机制
3. **网络安全**: 确保SSH连接使用加密通道
4. **文件权限**: 备份文件应设置适当的访问权限

## 8. 扩展功能

- 配置恢复功能
- 多设备批量操作
- 配置模板管理
- 审计日志
- 设备健康监控

