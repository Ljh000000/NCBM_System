"""
Flask主应用
"""
from flask import Flask, render_template, jsonify, request
import logging
import os
from config import Config
from device_manager import DeviceManager
from backup_manager import BackupManager
from diff_engine import DiffEngine
from email_notifier import EmailNotifier
from scheduler import BackupScheduler

# 配置日志 - 输出到logs目录
import logging.handlers
from datetime import datetime

# 确保logs目录存在
log_dir = 'logs'
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

# 配置日志格式
log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
date_format = '%Y-%m-%d %H:%M:%S'

# 配置根日志记录器
root_logger = logging.getLogger()
root_logger.setLevel(logging.INFO)

# 清除已有的处理器
root_logger.handlers.clear()

# 文件处理器 - 按日期轮转
log_file = os.path.join(log_dir, 'network_backup.log')
file_handler = logging.handlers.TimedRotatingFileHandler(
    log_file,
    when='midnight',
    interval=1,
    backupCount=30,  # 保留30天的日志
    encoding='utf-8'
)
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(logging.Formatter(log_format, date_format))

# 控制台处理器
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(logging.Formatter(log_format, date_format))

# 添加处理器
root_logger.addHandler(file_handler)
root_logger.addHandler(console_handler)

logger = logging.getLogger(__name__)
logger.info("=" * 60)
logger.info("网络设备配置备份与管理系统启动")
logger.info(f"日志文件: {log_file}")
logger.info("=" * 60)

app = Flask(__name__)

# 初始化配置和各个模块
config = Config()
device_manager = DeviceManager(config)
backup_manager = BackupManager(config)
diff_engine = DiffEngine()
email_notifier = EmailNotifier(config)
scheduler = BackupScheduler(config, device_manager, backup_manager, diff_engine, email_notifier)

# 启动定时任务
scheduler.start()


@app.route('/')
def index():
    """主页"""
    return render_template('index.html')


@app.route('/test')
def test_page():
    """测试页面"""
    return render_template('test.html')


@app.route('/api/devices', methods=['GET'])
def get_devices():
    """获取所有设备列表"""
    try:
        devices = config.get_devices()
        device_list = []
        for name, info in devices.items():
            device_list.append({
                'name': name,
                'ip': info['ip'],
                'type': info['device_type'],
                'username': info['username']
            })
        return jsonify({
            'status': 'success',
            'devices': device_list
        })
    except Exception as e:
        logger.error(f"获取设备列表时发生错误: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@app.route('/api/devices', methods=['POST'])
def add_device():
    """添加设备"""
    try:
        data = request.get_json()
        name = data.get('name')
        ip = data.get('ip')
        username = data.get('username')
        password = data.get('password')
        device_type = data.get('device_type')
        
        # 验证必填字段
        if not all([name, ip, username, password, device_type]):
            return jsonify({
                'status': 'error',
                'message': '所有字段都是必填的'
            }), 400
        
        success, message = config.add_device(name, ip, username, password, device_type)
        
        if success:
            # 重新加载设备管理器
            device_manager.devices = config.get_devices()
            return jsonify({
                'status': 'success',
                'message': message
            })
        else:
            return jsonify({
                'status': 'error',
                'message': message
            }), 400
        
    except Exception as e:
        logger.error(f"添加设备时发生错误: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@app.route('/api/devices', methods=['PUT'])
def update_device():
    """更新设备"""
    try:
        data = request.get_json()
        name = data.get('name')
        ip = data.get('ip')
        username = data.get('username')
        password = data.get('password', '')  # 密码可选，为空则保持原密码
        device_type = data.get('device_type')
        
        # 验证必填字段（密码除外）
        if not all([name, ip, username, device_type]):
            return jsonify({
                'status': 'error',
                'message': '设备名称、IP地址、用户名和设备类型都是必填的'
            }), 400
        
        success, message = config.update_device(name, ip, username, password, device_type)
        
        if success:
            # 重新加载设备管理器
            device_manager.devices = config.get_devices()
            # 如果设备正在连接，断开连接
            if name in device_manager.connections:
                device_manager.disconnect(name)
            return jsonify({
                'status': 'success',
                'message': message
            })
        else:
            return jsonify({
                'status': 'error',
                'message': message
            }), 400
        
    except Exception as e:
        logger.error(f"更新设备时发生错误: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@app.route('/api/devices', methods=['DELETE'])
def delete_device():
    """删除设备"""
    try:
        device_name = request.args.get('device_name')
        
        if not device_name:
            return jsonify({
                'status': 'error',
                'message': '设备名称不能为空'
            }), 400
        
        success, message = config.delete_device(device_name)
        
        if success:
            # 重新加载设备管理器
            device_manager.devices = config.get_devices()
            # 断开设备连接
            if device_name in device_manager.connections:
                device_manager.disconnect(device_name)
            return jsonify({
                'status': 'success',
                'message': message
            })
        else:
            return jsonify({
                'status': 'error',
                'message': message
            }), 400
        
    except Exception as e:
        logger.error(f"删除设备时发生错误: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@app.route('/api/backup', methods=['POST'])
def backup_device():
    """手动触发备份"""
    try:
        data = request.get_json()
        device_name = data.get('device_name')
        
        if not device_name:
            return jsonify({
                'status': 'error',
                'message': '设备名称不能为空'
            }), 400
        
        logger.info(f"手动备份请求: 设备 {device_name}")
        
        # 获取设备配置
        logger.info(f"[{device_name}] 开始获取设备配置")
        config_content = device_manager.get_config(device_name)
        if not config_content:
            logger.error(f"[{device_name}] 无法获取设备配置")
            return jsonify({
                'status': 'error',
                'message': '无法获取设备配置，请检查设备连接和网络'
            }), 500
        
        logger.info(f"[{device_name}] 配置获取成功，开始保存备份")
        # 备份配置
        backup_file = backup_manager.backup_config(device_name, config_content)
        if not backup_file:
            logger.error(f"[{device_name}] 备份文件保存失败")
            return jsonify({
                'status': 'error',
                'message': '备份失败，无法保存备份文件'
            }), 500
        
        logger.info(f"[{device_name}] 备份成功: {backup_file}")
        
        # 获取备份历史以获取时间戳
        history = backup_manager.get_backup_history(device_name)
        timestamp = history[0]['timestamp'] if history else ''
        
        return jsonify({
            'status': 'success',
            'message': '备份完成',
            'device_name': device_name,
            'backup_file': backup_file,
            'timestamp': timestamp
        })
        
    except Exception as e:
        logger.error(f"备份设备时发生错误: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@app.route('/api/backup/history', methods=['GET'])
def get_backup_history():
    """获取备份历史"""
    try:
        device_name = request.args.get('device_name')
        
        if not device_name:
            return jsonify({
                'status': 'error',
                'message': '设备名称不能为空'
            }), 400
        
        logger.info(f"获取设备 {device_name} 的备份历史")
        
        # 检查设备是否存在
        devices = config.get_devices()
        if device_name not in devices:
            logger.warning(f"设备 {device_name} 不存在")
            return jsonify({
                'status': 'error',
                'message': f'设备 {device_name} 不存在'
            }), 404
        
        # 获取备份历史
        history = backup_manager.get_backup_history(device_name)
        logger.info(f"成功获取 {len(history)} 条备份记录")
        
        return jsonify({
            'status': 'success',
            'device_name': device_name,
            'history': history
        })
        
    except Exception as e:
        logger.error(f"获取备份历史时发生错误: {str(e)}", exc_info=True)
        return jsonify({
            'status': 'error',
            'message': f'获取备份历史失败: {str(e)}'
        }), 500


@app.route('/api/backup/view', methods=['GET'])
def view_backup():
    """查看备份文件内容"""
    try:
        device_name = request.args.get('device_name')
        backup_file = request.args.get('backup_file')
        
        if not device_name or not backup_file:
            return jsonify({
                'status': 'error',
                'message': '设备名称和备份文件名不能为空'
            }), 400
        
        content = backup_manager.get_backup_content(device_name, backup_file)
        
        if content is None:
            return jsonify({
                'status': 'error',
                'message': '备份文件不存在或读取失败'
            }), 404
        
        return jsonify({
            'status': 'success',
            'device_name': device_name,
            'backup_file': backup_file,
            'content': content
        })
        
    except Exception as e:
        logger.error(f"查看备份文件时发生错误: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@app.route('/api/backup', methods=['DELETE'])
def delete_backup():
    """删除备份文件"""
    try:
        device_name = request.args.get('device_name')
        backup_file = request.args.get('backup_file')
        
        if not device_name or not backup_file:
            return jsonify({
                'status': 'error',
                'message': '设备名称和备份文件名不能为空'
            }), 400
        
        success = backup_manager.delete_backup(device_name, backup_file)
        
        if success:
            return jsonify({
                'status': 'success',
                'message': '备份文件已删除'
            })
        else:
            return jsonify({
                'status': 'error',
                'message': '删除失败'
            }), 500
        
    except Exception as e:
        logger.error(f"删除备份文件时发生错误: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@app.route('/api/diff', methods=['GET'])
def get_diff():
    """获取配置差异"""
    try:
        device_name = request.args.get('device_name')
        backup1 = request.args.get('backup1')
        backup2 = request.args.get('backup2')
        
        if not device_name:
            return jsonify({
                'status': 'error',
                'message': '设备名称不能为空'
            }), 400
        
        # 如果没有指定备份文件，使用最新的两个
        if not backup1 or not backup2:
            history = backup_manager.get_backup_history(device_name)
            if len(history) < 2:
                return jsonify({
                    'status': 'error',
                    'message': '备份文件不足，无法对比'
                }), 400
            backup1 = history[0]['file_name']
            backup2 = history[1]['file_name']
        
        # 读取两个备份文件
        config1 = backup_manager.get_backup_content(device_name, backup1)
        config2 = backup_manager.get_backup_content(device_name, backup2)
        
        if not config1 or not config2:
            return jsonify({
                'status': 'error',
                'message': '无法读取备份文件'
            }), 500
        
        # 对比差异
        diff_result = diff_engine.compare_configs(config1, config2)
        
        return jsonify({
            'status': 'success',
            'device_name': device_name,
            'has_changes': diff_result['has_changes'],
            'backup1': backup1,
            'backup2': backup2,
            'diff': diff_result['diff'],
            'summary': diff_engine.get_summary(diff_result)
        })
        
    except Exception as e:
        logger.error(f"获取配置差异时发生错误: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@app.route('/api/restore', methods=['POST'])
def restore_config():
    """恢复设备配置"""
    try:
        data = request.get_json()
        device_name = data.get('device_name')
        backup_file = data.get('backup_file')
        
        if not device_name or not backup_file:
            return jsonify({
                'status': 'error',
                'message': '设备名称和备份文件名不能为空'
            }), 400
        
        # 读取备份文件内容
        config_content = backup_manager.get_backup_content(device_name, backup_file)
        if not config_content:
            return jsonify({
                'status': 'error',
                'message': '无法读取备份文件'
            }), 404
        
        # 执行配置恢复
        result = device_manager.restore_config(device_name, config_content)
        
        if result['success']:
            return jsonify({
                'status': 'success',
                'message': result['message'],
                'device_name': device_name,
                'backup_file': backup_file,
                'output': result['output']
            })
        else:
            return jsonify({
                'status': 'error',
                'message': result['message'],
                'output': result['output']
            }), 500
        
    except Exception as e:
        logger.error(f"恢复配置时发生错误: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@app.route('/api/status', methods=['GET'])
def get_status():
    """获取系统状态"""
    try:
        devices = config.get_devices()
        
        # 优化：直接统计备份目录中的文件数量，而不是遍历所有设备
        # 这样更快，不会因为设备多而卡住
        total_backups = 0
        backup_dir = backup_manager.backup_dir
        
        try:
            if os.path.exists(backup_dir):
                for device_name in os.listdir(backup_dir):
                    device_backup_dir = os.path.join(backup_dir, device_name)
                    if os.path.isdir(device_backup_dir):
                        # 只统计 .cfg 文件数量，不读取文件内容
                        cfg_files = [f for f in os.listdir(device_backup_dir) 
                                    if f.endswith('.cfg') and os.path.isfile(os.path.join(device_backup_dir, f))]
                        total_backups += len(cfg_files)
        except (OSError, PermissionError) as e:
            logger.warning(f"统计备份数量时出错: {str(e)}")
            # 如果统计失败，返回0，不影响其他功能
        
        next_backup = scheduler.get_next_run_time()
        next_backup_str = next_backup.strftime('%Y-%m-%d %H:%M:%S') if next_backup else None
        
        return jsonify({
            'status': 'success',
            'scheduler_enabled': scheduler.enabled,
            'scheduler_running': scheduler.is_running(),
            'next_backup_time': next_backup_str,
            'total_devices': len(devices),
            'total_backups': total_backups
        })
        
    except Exception as e:
        logger.error(f"获取系统状态时发生错误: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@app.route('/api/test/email', methods=['POST'])
def test_email():
    """测试邮件告警"""
    try:
        logger.info("收到测试邮件请求")
        
        # 检查邮件是否启用
        email_config = config.get_email_config()
        if not email_config['enabled']:
            return jsonify({
                'status': 'error',
                'message': '邮件功能未启用，请在config.ini中启用'
            }), 400
        
        # 创建测试差异结果
        from diff_engine import DiffEngine
        diff_engine = DiffEngine()
        
        old_config = "hostname test\ninterface vlan1\n ip address 192.168.1.1 255.255.255.0"
        new_config = "hostname test\ninterface vlan1\n ip address 192.168.1.2 255.255.255.0\ninterface vlan2\n ip address 192.168.2.1 255.255.255.0"
        
        diff_result = diff_engine.compare_configs(old_config, new_config)
        diff_result['summary'] = diff_engine.get_summary(diff_result)
        
        # 发送测试邮件
        success = email_notifier.send_alert('测试设备', diff_result)
        
        if success:
            logger.info("测试邮件发送成功")
            return jsonify({
                'status': 'success',
                'message': f'测试邮件已发送到: {", ".join(email_config["to_emails"])}'
            })
        else:
            logger.error("测试邮件发送失败")
            return jsonify({
                'status': 'error',
                'message': '测试邮件发送失败，请检查邮件配置和日志'
            }), 500
            
    except Exception as e:
        logger.error(f"测试邮件时发生错误: {str(e)}", exc_info=True)
        return jsonify({
            'status': 'error',
            'message': f'测试邮件失败: {str(e)}'
        }), 500


@app.route('/api/test/trigger-backup', methods=['POST'])
def trigger_backup():
    """手动触发定时备份任务"""
    try:
        logger.info("收到手动触发定时备份请求")
        
        if not scheduler.enabled:
            return jsonify({
                'status': 'error',
                'message': '定时任务未启用'
            }), 400
        
        # 在后台线程中执行备份，避免阻塞
        import threading
        def run_backup():
            try:
                scheduler.backup_all_devices()
            except Exception as e:
                logger.error(f"手动触发备份任务时发生错误: {str(e)}", exc_info=True)
        
        thread = threading.Thread(target=run_backup, daemon=True)
        thread.start()
        
        logger.info("定时备份任务已在后台启动")
        return jsonify({
            'status': 'success',
            'message': '定时备份任务已启动，请查看日志了解执行情况'
        })
        
    except Exception as e:
        logger.error(f"触发定时备份时发生错误: {str(e)}", exc_info=True)
        return jsonify({
            'status': 'error',
            'message': f'触发定时备份失败: {str(e)}'
        }), 500


@app.route('/api/test/logs', methods=['GET'])
def get_logs():
    """获取运行日志"""
    try:
        lines = request.args.get('lines', 100, type=int)  # 默认获取最近100行
        
        log_file = os.path.join('logs', 'network_backup.log')
        
        if not os.path.exists(log_file):
            return jsonify({
                'status': 'error',
                'message': '日志文件不存在，请先运行系统生成日志'
            }), 404
        
        # 读取日志文件最后N行
        try:
            with open(log_file, 'r', encoding='utf-8') as f:
                all_lines = f.readlines()
                # 获取最后N行
                recent_lines = all_lines[-lines:] if len(all_lines) > lines else all_lines
                logs = ''.join(recent_lines)
                
            return jsonify({
                'status': 'success',
                'logs': logs,
                'lines': len(recent_lines),
                'total_lines': len(all_lines)
            })
        except Exception as e:
            logger.error(f"读取日志文件时发生错误: {str(e)}")
            return jsonify({
                'status': 'error',
                'message': f'读取日志文件失败: {str(e)}'
            }), 500
            
    except Exception as e:
        logger.error(f"获取日志时发生错误: {str(e)}", exc_info=True)
        return jsonify({
            'status': 'error',
            'message': f'获取日志失败: {str(e)}'
        }), 500


@app.errorhandler(404)
def not_found(error):
    """404错误处理"""
    return jsonify({
        'status': 'error',
        'message': '接口不存在'
    }), 404


@app.errorhandler(500)
def internal_error(error):
    """500错误处理"""
    return jsonify({
        'status': 'error',
        'message': '服务器内部错误'
    }), 500


if __name__ == '__main__':
    try:
        app.run(host='0.0.0.0', port=5000, debug=True)
    finally:
        # 清理资源
        scheduler.stop()
        device_manager.disconnect_all()

