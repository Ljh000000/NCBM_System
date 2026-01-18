# API 接口文档

## 基础信息

- **Base URL**: `http://localhost:5000`
- **Content-Type**: `application/json`

## 接口列表

### 1. 获取设备列表

**接口**: `GET /api/devices`

**描述**: 获取所有已配置的网络设备列表

**请求参数**: 无

**响应示例**:
```json
{
  "status": "success",
  "devices": [
    {
      "name": "switch1",
      "ip": "192.168.1.1",
      "type": "cisco_ios",
      "username": "admin"
    }
  ]
}
```

---

### 1.1. 添加设备

**接口**: `POST /api/devices`

**描述**: 添加新的网络设备配置

**请求体**:
```json
{
  "name": "switch1",
  "ip": "192.168.1.1",
  "username": "admin",
  "password": "password123",
  "device_type": "cisco_ios"
}
```

**响应示例**:
```json
{
  "status": "success",
  "message": "设备添加成功"
}
```

**错误响应**:
```json
{
  "status": "error",
  "message": "设备名称已存在"
}
```

---

### 1.2. 更新设备

**接口**: `PUT /api/devices`

**描述**: 更新现有设备的配置信息

**请求体**:
```json
{
  "name": "switch1",
  "ip": "192.168.1.2",
  "username": "admin",
  "password": "newpassword",
  "device_type": "cisco_ios"
}
```

**注意**: 
- `password` 字段可选，如果为空则保持原密码不变
- `name` 字段不能修改（作为唯一标识）

**响应示例**:
```json
{
  "status": "success",
  "message": "设备更新成功"
}
```

---

### 1.3. 删除设备

**接口**: `DELETE /api/devices`

**描述**: 删除指定的设备配置

**请求参数**:
- `device_name` (required): 设备名称

**请求示例**: `DELETE /api/devices?device_name=switch1`

**响应示例**:
```json
{
  "status": "success",
  "message": "设备删除成功"
}
```

**注意**: 删除设备不会删除备份文件，备份文件会保留

---

### 2. 手动触发备份

**接口**: `POST /api/backup`

**描述**: 手动触发指定设备的配置备份

**请求体**:
```json
{
  "device_name": "switch1"
}
```

**响应示例**:
```json
{
  "status": "success",
  "message": "备份完成",
  "device_name": "switch1",
  "backup_file": "backups/switch1/20231219_120000.cfg",
  "timestamp": "2023-12-19 12:00:00"
}
```

**错误响应**:
```json
{
  "status": "error",
  "message": "设备连接失败"
}
```

---

### 3. 获取备份历史

**接口**: `GET /api/backup/history`

**描述**: 获取指定设备的备份历史记录

**请求参数**:
- `device_name` (required): 设备名称

**请求示例**: `GET /api/backup/history?device_name=switch1`

**响应示例**:
```json
{
  "status": "success",
  "device_name": "switch1",
  "history": [
    {
      "timestamp": "2023-12-19 12:00:00",
      "file_path": "backups/switch1/20231219_120000.cfg",
      "size": 1024,
      "size_human": "1.0 KB"
    },
    {
      "timestamp": "2023-12-18 12:00:00",
      "file_path": "backups/switch1/20231218_120000.cfg",
      "size": 1020,
      "size_human": "1.0 KB"
    }
  ]
}
```

---

### 4. 获取配置差异

**接口**: `GET /api/diff`

**描述**: 对比两个备份文件的差异

**请求参数**:
- `device_name` (required): 设备名称
- `backup1` (optional): 第一个备份文件名，不提供则使用最新备份
- `backup2` (optional): 第二个备份文件名，不提供则使用最新备份

**请求示例**: 
- `GET /api/diff?device_name=switch1` (对比最新两个备份)
- `GET /api/diff?device_name=switch1&backup1=20231219_120000.cfg&backup2=20231218_120000.cfg`

**响应示例**:
```json
{
  "status": "success",
  "device_name": "switch1",
  "has_changes": true,
  "backup1": "20231219_120000.cfg",
  "backup2": "20231218_120000.cfg",
  "diff": "--- old\n+++ new\n@@ -1,2 +1,3 @@\n hostname switch1\n+ interface vlan1\n+  ip address 192.168.1.1 255.255.255.0"
}
```

---

### 5. 获取备份文件内容

**接口**: `GET /api/backup/view`

**描述**: 查看指定备份文件的内容

**请求参数**:
- `device_name` (required): 设备名称
- `backup_file` (required): 备份文件名

**请求示例**: `GET /api/backup/view?device_name=switch1&backup_file=20231219_120000.cfg`

**响应示例**:
```json
{
  "status": "success",
  "device_name": "switch1",
  "backup_file": "20231219_120000.cfg",
  "content": "hostname switch1\ninterface vlan1\n ip address 192.168.1.1 255.255.255.0\n..."
}
```

---

### 6. 删除备份文件

**接口**: `DELETE /api/backup`

**描述**: 删除指定的备份文件

**请求参数**:
- `device_name` (required): 设备名称
- `backup_file` (required): 备份文件名

**请求示例**: `DELETE /api/backup?device_name=switch1&backup_file=20231219_120000.cfg`

**响应示例**:
```json
{
  "status": "success",
  "message": "备份文件已删除"
}
```

---

### 7. 恢复设备配置

**接口**: `POST /api/restore`

**描述**: 将指定备份文件的配置恢复到设备

**请求体**:
```json
{
  "device_name": "switch1",
  "backup_file": "20231219_120000.cfg"
}
```

**响应示例**:
```json
{
  "status": "success",
  "message": "配置恢复成功",
  "device_name": "switch1",
  "backup_file": "20231219_120000.cfg",
  "output": "configure terminal\nhostname switch1\nend\nwrite memory\n..."
}
```

**错误响应**:
```json
{
  "status": "error",
  "message": "无法连接到设备",
  "output": ""
}
```

**注意事项**:
- ⚠️ 此操作会覆盖设备当前配置，请谨慎使用
- 建议在执行恢复前先备份当前配置
- 不同设备类型的配置恢复方式可能不同
- 恢复过程可能需要较长时间，请耐心等待

---

### 8. 获取系统状态

**接口**: `GET /api/status`

**描述**: 获取系统运行状态和统计信息

**响应示例**:
```json
{
  "status": "success",
  "scheduler_enabled": true,
  "next_backup_time": "2023-12-20 02:00:00",
  "total_devices": 2,
  "total_backups": 10,
  "last_backup_time": "2023-12-19 12:00:00"
}
```

---

## 错误码说明

| 状态码 | 说明 |
|--------|------|
| 200 | 请求成功 |
| 400 | 请求参数错误 |
| 404 | 资源不存在 |
| 500 | 服务器内部错误 |

## 错误响应格式

```json
{
  "status": "error",
  "message": "错误描述信息",
  "error_code": "ERROR_CODE"
}
```

