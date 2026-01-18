# 网络设备配置备份与管理系统

基于Python的网络设备配置备份与管理系统，支持自动备份、配置差异对比、邮件告警和设备管理功能。

## 功能特性

- ✅ **设备连接管理**: 支持通过SSH/Telnet连接多种网络设备（Cisco IOS、华为、H3C等）
- ✅ **设备管理**: Web界面支持添加、编辑、删除设备，无需手动编辑配置文件
- ✅ **自动备份**: 定时自动备份设备配置（可配置备份时间）
- ✅ **手动备份**: 通过Web界面手动触发备份
- ✅ **配置对比**: 自动对比配置差异，发现变更
- ✅ **配置恢复**: 一键恢复设备配置到指定备份版本
- ✅ **邮件告警**: 配置变更时自动发送邮件通知
- ✅ **备份历史**: 查看和管理所有备份记录
- ✅ **Web界面**: 简洁美观的Bootstrap界面，操作便捷
- ✅ **备份管理**: 自动清理过期备份，节省存储空间

## 技术栈

- **后端**: Python 3.7+, Flask
- **网络连接**: netmiko (SSH/Telnet)
- **定时任务**: APScheduler
- **前端**: Bootstrap 5, HTML/CSS/JavaScript
- **配置对比**: difflib (Python标准库)

## 项目结构

```
network/
├── app.py                 # Flask主应用
├── config.py             # 配置管理模块
├── device_manager.py     # 设备管理核心模块
├── backup_manager.py     # 备份管理模块
├── diff_engine.py        # 配置差异对比引擎
├── scheduler.py          # 定时任务调度器
├── email_notifier.py     # 邮件通知模块
├── test_system.py        # 系统测试脚本
├── test_device_management.py  # 设备管理功能测试
├── test_email.py        # 邮件发送测试
├── config.ini           # 配置文件
├── requirements.txt     # 依赖包列表
├── templates/           # HTML模板
│   └── index.html
├── backups/             # 配置备份存储目录
└── docs/                # 文档目录
    ├── TECHNICAL_DOC.md  # 技术文档
    ├── API_DOC.md       # API接口文档
    ├── DEVICE_MANAGEMENT.md  # 设备管理功能说明
    └── TEST_GUIDE.md    # 测试指南
```

## 快速开始

### 1. 环境要求

- Python 3.7 或更高版本
- pip 包管理器

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 配置设备信息

#### 方式1：使用Web界面（推荐）

1. 启动应用：`python app.py`
2. 访问 http://localhost:5000
3. 点击"添加设备"按钮，填写设备信息

#### 方式2：手动编辑配置文件

编辑 `config.ini` 文件：

```ini
[devices]
# 格式: name=ip,username,password,device_type
switch1=192.168.1.1,admin,password123,cisco_ios
router1=192.168.1.2,admin,password123,cisco_ios
```

支持的设备类型：
- `cisco_ios` - Cisco IOS设备
- `cisco_ios_telnet` - Cisco IOS (Telnet)
- `huawei` - 华为设备
- `h3c` - H3C设备
- `juniper` - Juniper设备
- `linux` - Linux设备
- 更多类型请参考 [netmiko文档](https://github.com/ktbyers/netmiko)

### 4. 配置定时任务（可选）

在 `config.ini` 中配置定时备份：

```ini
[scheduler]
enabled=true
backup_time=02:00        # 每天凌晨2点备份
timezone=Asia/Shanghai
```

### 5. 配置邮件告警（可选）

在 `config.ini` 中配置邮件设置：

```ini
[email]
enabled=true
smtp_server=smtp.example.com
smtp_port=587
smtp_user=your_email@example.com
smtp_password=your_password
from_email=your_email@example.com
to_emails=admin@example.com
```

### 6. 启动应用

```bash
python app.py
```

应用将在 `http://localhost:5000` 启动。

## 使用方法

### Web界面操作

1. **设备管理**
   - **添加设备**: 点击"添加设备"按钮，填写设备信息
   - **编辑设备**: 点击设备列表中的"编辑"按钮，修改设备信息
   - **删除设备**: 点击设备列表中的"删除"按钮，确认删除

2. **备份操作**
   - **手动备份**: 选择设备后，点击"手动备份当前设备"按钮
   - **查看备份**: 在备份历史中点击"查看"按钮
   - **恢复配置**: 在备份历史中点击"恢复"按钮（⚠️ 请谨慎操作）
   - **删除备份**: 点击"删除"按钮删除不需要的备份

3. **配置对比**
   - 选择两个备份文件进行对比，查看配置差异

### API接口

系统提供RESTful API接口，详细文档请参考 [API文档](docs/API_DOC.md)

主要接口：
- `GET /api/devices` - 获取设备列表
- `POST /api/devices` - 添加设备
- `PUT /api/devices` - 更新设备
- `DELETE /api/devices` - 删除设备
- `POST /api/backup` - 手动触发备份
- `GET /api/backup/history` - 获取备份历史
- `GET /api/diff` - 获取配置差异
- `POST /api/restore` - 恢复设备配置
- `GET /api/status` - 获取系统状态

## 测试

### 系统测试

运行系统测试脚本验证功能：

```bash
python test_system.py
```

### 设备管理功能测试

运行设备管理功能测试：

```bash
# 1. 启动Flask应用（终端1）
python app.py

# 2. 运行测试（终端2）
python test_device_management.py
```

### 邮件发送测试

测试邮件告警功能：

```bash
python test_email.py
```

### Web界面测试

1. 启动应用：`python app.py`
2. 访问 http://localhost:5000
3. 测试添加、编辑、删除设备功能

详细测试指南请参考 [测试文档](docs/TEST_GUIDE.md)

## 配置说明

### 备份配置

```ini
[backup]
backup_dir=backups              # 备份存储目录
retention_days=30               # 备份保留天数
command=show running-config     # 获取配置的命令
```

### 设备配置格式

```
设备名称=IP地址,用户名,密码,设备类型
```

示例：
```
switch1=192.168.1.1,admin,password123,cisco_ios
```

## 安全注意事项

1. **密码安全**: 配置文件中的密码建议加密存储（生产环境）
2. **访问控制**: Web界面建议添加认证机制
3. **网络安全**: 确保SSH连接使用加密通道
4. **文件权限**: 备份文件应设置适当的访问权限

## 常见问题

### Q: 无法连接到设备？

A: 请检查：
- 设备IP地址是否正确
- 网络是否可达
- 用户名和密码是否正确
- 设备类型是否匹配
- 防火墙是否允许SSH连接

### Q: 定时任务不执行？

A: 请检查：
- `config.ini` 中 `scheduler.enabled` 是否为 `true`
- 系统时间是否正确
- 时区配置是否正确

### Q: 邮件发送失败？

A: 请检查：
- SMTP服务器地址和端口是否正确
- 用户名和密码是否正确
- 是否启用了SMTP认证
- 防火墙是否允许SMTP连接

### Q: 加载备份历史卡住？

A: 已添加超时机制，如果仍然卡住，请检查：
- 备份目录文件数量是否过多
- 磁盘IO是否正常
- 可以手动清理旧的备份文件

## 实现思路

### 核心库选择
- **netmiko**: 用于SSH/Telnet连接网络设备，支持多种设备类型（Cisco IOS、华为、H3C等）
- **difflib**: Python标准库，用于配置差异对比
- **APScheduler**: 定时任务调度，实现定期自动备份

### 功能模块

1. **登录设备** (`device_manager.py`)
   - 使用netmiko的`ConnectHandler`连接设备
   - 支持SSH和Telnet连接
   - 连接缓存管理，异常处理完善

2. **执行命令** (`device_manager.py`)
   - `execute_command()`: 执行任意命令（如`show running-config`）
   - 自动处理连接，错误处理

3. **保存配置** (`device_manager.py`)
   - `restore_config()`: 恢复配置到设备
   - 根据设备类型自动选择保存命令（`write memory`/`save`/`commit`）

4. **对比差异** (`diff_engine.py`)
   - 使用`difflib.unified_diff()`对比配置
   - 生成差异摘要（新增/删除行数）
   - 支持HTML格式输出

### 工作流程

#### 自动备份流程
```
定时任务触发 → 连接设备 → 执行show run → 保存到本地 → 对比差异 → 发送邮件告警
```

#### 手动备份流程
```
Web界面点击 → API调用 → 连接设备 → 执行命令 → 保存配置 → 返回结果
```

#### 配置恢复流程
```
选择备份文件 → 点击恢复 → 连接设备 → 发送配置命令 → 保存配置 → 返回结果
```

### eNSP模拟器支持
- eNSP中的设备可以通过SSH/Telnet连接
- 配置设备IP地址和SSH服务
- 使用对应的device_type（如`cisco_ios`或`huawei`）

## 需求符合度

| 需求项 | 状态 | 实现位置 |
|--------|------|----------|
| 核心库：netmiko | ✅ | device_manager.py |
| 登录设备 | ✅ | DeviceManager.connect() |
| 执行命令 | ✅ | DeviceManager.execute_command() |
| 保存配置 | ✅ | DeviceManager.restore_config() |
| 对比差异 | ✅ | DiffEngine.compare_configs() |
| 定期自动备份 | ✅ | BackupScheduler |
| 执行 show run | ✅ | DeviceManager.get_config() |
| 备份到本地 | ✅ | BackupManager.backup_config() |
| 差异对比（difflib） | ✅ | DiffEngine |
| 邮件告警 | ✅ | EmailNotifier |
| Web界面（Flask） | ✅ | app.py + templates/index.html |
| Bootstrap前端 | ✅ | templates/index.html |
| 手动触发备份 | ✅ | POST /api/backup |
| 查看备份历史 | ✅ | GET /api/backup/history |
| 一键恢复配置 | ✅ | POST /api/restore |

**需求符合度: 100%** ✅

## 文档

- [技术文档](docs/TECHNICAL_DOC.md) - 详细的技术架构和实现说明
- [API文档](docs/API_DOC.md) - 完整的API接口文档
- [设备管理文档](docs/DEVICE_MANAGEMENT.md) - 设备管理功能详细说明
- [测试指南](docs/TEST_GUIDE.md) - 测试方法和测试清单

## 许可证

本项目仅供学习和研究使用。

## 贡献

欢迎提交Issue和Pull Request！
