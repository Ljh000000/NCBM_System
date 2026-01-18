"""
设备管理模块 - 负责网络设备的连接和命令执行
"""
from netmiko import ConnectHandler, NetmikoTimeoutException, NetmikoAuthenticationException
import logging

logger = logging.getLogger(__name__)


class DeviceManager:
    """设备管理类"""
    
    def __init__(self, config):
        """
        初始化设备管理器
        
        Args:
            config: Config对象
        """
        self.config = config
        self.devices = config.get_devices()
        self.connections = {}  # 连接缓存
        self.connection_retries = 3  # 连接重试次数
        self.retry_delay = 2  # 重试延迟（秒）
    
    def _check_connection(self, connection):
        """
        检查连接是否有效
        
        Args:
            connection: ConnectHandler对象
            
        Returns:
            bool: 连接是否有效
        """
        if not connection:
            return False
        
        try:
            # 尝试发送一个简单的命令来检查连接
            connection.send_command('', expect_string=r'#|>|$', max_loops=1)
            return True
        except Exception as e:
            logger.debug(f"连接检查失败: {str(e)}")
            return False
    
    def connect(self, device_name, retry_count=None):
        """
        连接到指定设备（带重试机制）
        
        Args:
            device_name: 设备名称
            retry_count: 重试次数（内部使用）
            
        Returns:
            ConnectHandler对象或None
        """
        if device_name not in self.devices:
            logger.error(f"[{device_name}] 设备不存在于配置中")
            return None
        
        device_info = self.devices[device_name]
        
        # 如果已有连接，先检查连接是否有效
        if device_name in self.connections:
            connection = self.connections[device_name]
            if self._check_connection(connection):
                logger.debug(f"[{device_name}] 使用现有有效连接")
                return connection
            else:
                logger.warning(f"[{device_name}] 现有连接已失效，重新连接")
                try:
                    connection.disconnect()
                except:
                    pass
                del self.connections[device_name]
        
        # 确定重试次数
        if retry_count is None:
            retry_count = self.connection_retries
        
        logger.info(f"[{device_name}] 开始连接设备: {device_info['ip']} (类型: {device_info['device_type']})")
        
        last_exception = None
        
        for attempt in range(1, retry_count + 1):
            try:
                if attempt > 1:
                    import time
                    logger.info(f"[{device_name}] 第 {attempt} 次尝试连接（共 {retry_count} 次）...")
                    time.sleep(self.retry_delay * (attempt - 1))  # 递增延迟
                
                logger.info(f"[{device_name}] 建立SSH/Telnet连接...")
                connection = ConnectHandler(
                    device_type=device_info['device_type'],
                    ip=device_info['ip'],
                    username=device_info['username'],
                    password=device_info['password'],
                    timeout=30,
                    secret='',  # enable密码，如果需要可以配置
                    fast_cli=False,  # 禁用快速CLI，提高稳定性
                    session_log=None,  # 不记录会话日志
                )
                
                # 验证连接
                if self._check_connection(connection):
                    self.connections[device_name] = connection
                    logger.info(f"[{device_name}] 成功连接到设备 {device_info['ip']} (尝试 {attempt}/{retry_count})")
                    return connection
                else:
                    logger.warning(f"[{device_name}] 连接建立但验证失败，关闭连接")
                    try:
                        connection.disconnect()
                    except:
                        pass
                    last_exception = Exception("连接验证失败")
                    
            except NetmikoTimeoutException as e:
                last_exception = e
                logger.warning(f"[{device_name}] 连接超时 (尝试 {attempt}/{retry_count}): {str(e)}")
                if attempt < retry_count:
                    continue
                else:
                    logger.error(f"[{device_name}] 连接超时，已重试 {retry_count} 次，可能原因: 网络不通、设备未启动、防火墙阻止")
                    
            except NetmikoAuthenticationException as e:
                last_exception = e
                logger.error(f"[{device_name}] 认证失败，请检查用户名和密码")
                return None  # 认证失败不重试
                
            except Exception as e:
                last_exception = e
                logger.warning(f"[{device_name}] 连接时发生错误 (尝试 {attempt}/{retry_count}): {str(e)}")
                if attempt < retry_count:
                    continue
                else:
                    logger.error(f"[{device_name}] 连接失败，已重试 {retry_count} 次", exc_info=True)
        
        return None
    
    def execute_command(self, device_name, command, retry_on_failure=True):
        """
        在指定设备上执行命令（带自动重连机制）
        
        Args:
            device_name: 设备名称
            command: 要执行的命令
            retry_on_failure: 失败时是否重试
            
        Returns:
            命令输出或None
        """
        connection = self.connections.get(device_name)
        
        # 如果没有连接或连接无效，先连接
        if not connection or not self._check_connection(connection):
            if connection:
                logger.warning(f"[{device_name}] 现有连接无效，重新连接")
                try:
                    connection.disconnect()
                except:
                    pass
                if device_name in self.connections:
                    del self.connections[device_name]
            
            logger.info(f"[{device_name}] 设备未连接，尝试建立连接")
            connection = self.connect(device_name)
            if not connection:
                logger.error(f"[{device_name}] 设备连接失败，无法执行命令")
                return None
        else:
            logger.debug(f"[{device_name}] 使用现有连接")
        
        # 执行命令，带重试机制
        max_attempts = 2 if retry_on_failure else 1
        
        for attempt in range(1, max_attempts + 1):
            try:
                logger.info(f"[{device_name}] 执行命令: {command} (尝试 {attempt}/{max_attempts})")
                output = connection.send_command(command, delay_factor=2)  # 增加延迟因子，提高稳定性
                
                if output:
                    logger.info(f"[{device_name}] 命令执行成功，输出长度: {len(output)} 字符")
                else:
                    logger.warning(f"[{device_name}] 命令执行完成，但输出为空")
                return output
                
            except Exception as e:
                error_msg = str(e)
                logger.warning(f"[{device_name}] 执行命令时发生错误 (尝试 {attempt}/{max_attempts}): {error_msg}")
                
                # 如果是连接相关错误，尝试重新连接
                if retry_on_failure and attempt < max_attempts:
                    if 'connection' in error_msg.lower() or 'timeout' in error_msg.lower() or 'closed' in error_msg.lower():
                        logger.info(f"[{device_name}] 检测到连接问题，尝试重新连接...")
                        # 清除旧连接
                        if device_name in self.connections:
                            try:
                                self.connections[device_name].disconnect()
                            except:
                                pass
                            del self.connections[device_name]
                        
                        # 重新连接
                        connection = self.connect(device_name)
                        if connection:
                            logger.info(f"[{device_name}] 重新连接成功，重试执行命令")
                            continue
                        else:
                            logger.error(f"[{device_name}] 重新连接失败")
                            return None
                    else:
                        # 非连接错误，直接返回
                        logger.error(f"[{device_name}] 执行命令失败: {error_msg}", exc_info=True)
                        return None
                else:
                    # 最后一次尝试失败
                    logger.error(f"[{device_name}] 执行命令失败，已重试 {max_attempts} 次: {error_msg}", exc_info=True)
                    # 清除连接缓存
                    if device_name in self.connections:
                        try:
                            self.connections[device_name].disconnect()
                        except:
                            pass
                        del self.connections[device_name]
                    return None
        
        return None
    
    def get_config(self, device_name):
        """
        获取设备配置
        
        Args:
            device_name: 设备名称
            
        Returns:
            配置内容或None
        """
        try:
            backup_config = self.config.get_backup_config()
            command = backup_config['command']
            logger.info(f"[{device_name}] 执行命令获取配置: {command}")
            result = self.execute_command(device_name, command)
            if result:
                logger.info(f"[{device_name}] 配置获取成功，长度: {len(result)} 字符")
            else:
                logger.error(f"[{device_name}] 配置获取失败，返回为空")
            return result
        except Exception as e:
            logger.error(f"[{device_name}] 获取配置时发生异常: {str(e)}", exc_info=True)
            return None
    
    def restore_config(self, device_name, config_content):
        """
        恢复设备配置
        
        Args:
            device_name: 设备名称
            config_content: 配置内容（字符串）
            
        Returns:
            dict: {
                'success': bool,
                'message': str,
                'output': str  # 命令输出
            }
        """
        if device_name not in self.devices:
            return {
                'success': False,
                'message': f'设备 {device_name} 不存在',
                'output': ''
            }
        
        connection = self.connections.get(device_name)
        
        # 如果没有连接，先连接
        if not connection:
            connection = self.connect(device_name)
            if not connection:
                return {
                    'success': False,
                    'message': '无法连接到设备',
                    'output': ''
                }
        
        try:
            # 解析配置内容，过滤掉注释和空行
            config_lines = []
            for line in config_content.splitlines():
                line = line.strip()
                # 跳过空行和注释行（以!开头的行通常是注释）
                if line and not line.startswith('!'):
                    # 跳过一些常见的非配置命令
                    if not line.startswith('Building configuration'):
                        if not line.startswith('Current configuration'):
                            config_lines.append(line)
            
            if not config_lines:
                return {
                    'success': False,
                    'message': '配置内容为空或无效',
                    'output': ''
                }
            
            # 使用send_config_set方法发送配置
            # 这个方法会自动进入配置模式，执行配置，然后退出
            output = connection.send_config_set(config_lines)
            
            # 保存配置（不同设备类型命令不同）
            device_type = self.devices[device_name]['device_type']
            save_command = self._get_save_command(device_type)
            
            if save_command:
                save_output = connection.send_command(save_command, expect_string=r'#|>|]')
                output += '\n' + save_output
            
            logger.info(f"成功恢复设备 {device_name} 的配置")
            
            return {
                'success': True,
                'message': '配置恢复成功',
                'output': output
            }
            
        except Exception as e:
            error_msg = f"恢复配置时发生错误: {str(e)}"
            logger.error(f"设备 {device_name} - {error_msg}")
            # 连接可能已断开，清除缓存
            if device_name in self.connections:
                del self.connections[device_name]
            
            return {
                'success': False,
                'message': error_msg,
                'output': ''
            }
    
    def _get_save_command(self, device_type):
        """
        根据设备类型获取保存配置的命令
        
        Args:
            device_type: 设备类型
            
        Returns:
            保存命令或None
        """
        # Cisco IOS设备
        if device_type in ['cisco_ios', 'cisco_ios_telnet', 'cisco_nxos', 'cisco_asa']:
            return 'write memory'
        # 华为设备
        elif device_type in ['huawei']:
            return 'save'
        # H3C设备
        elif device_type in ['hp_comware', 'hp_procurve']:
            return 'save'
        # Juniper设备
        elif device_type in ['juniper', 'juniper_junos']:
            return 'commit'
        # 其他设备类型，尝试通用命令
        else:
            # 默认尝试write memory
            return 'write memory'
    
    def disconnect(self, device_name):
        """
        断开指定设备的连接
        
        Args:
            device_name: 设备名称
        """
        if device_name in self.connections:
            try:
                self.connections[device_name].disconnect()
                logger.info(f"断开设备 {device_name} 的连接")
            except:
                pass
            finally:
                del self.connections[device_name]
    
    def disconnect_all(self):
        """断开所有设备的连接"""
        for device_name in list(self.connections.keys()):
            self.disconnect(device_name)

