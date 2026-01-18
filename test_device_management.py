"""
设备管理功能测试脚本
测试设备的添加、编辑、删除功能
"""
import sys
import requests
import json
from config import Config

BASE_URL = "http://localhost:5000"

def test_add_device():
    """测试添加设备"""
    print("=" * 60)
    print("测试1: 添加设备")
    print("=" * 60)
    
    device_data = {
        "name": "test_switch",
        "ip": "192.168.1.10",
        "username": "admin",
        "password": "test123",
        "device_type": "cisco_ios"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/devices",
            json=device_data,
            timeout=5
        )
        
        if response.status_code == 200:
            data = response.json()
            if data['status'] == 'success':
                print("[OK] 添加设备成功")
                print(f"   消息: {data['message']}")
                return True
            else:
                print(f"[FAIL] 添加设备失败: {data['message']}")
                return False
        else:
            print(f"[FAIL] HTTP错误: {response.status_code}")
            print(f"   响应: {response.text}")
            return False
    except requests.exceptions.ConnectionError:
        print("[FAIL] 无法连接到服务器")
        print("   请确保Flask应用正在运行: python app.py")
        return False
    except Exception as e:
        print(f"[FAIL] 测试失败: {str(e)}")
        return False

def test_get_devices():
    """测试获取设备列表"""
    print("\n" + "=" * 60)
    print("测试2: 获取设备列表")
    print("=" * 60)
    
    try:
        response = requests.get(f"{BASE_URL}/api/devices", timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            if data['status'] == 'success':
                print(f"[OK] 获取设备列表成功")
                print(f"   设备数量: {len(data['devices'])}")
                for device in data['devices']:
                    print(f"   - {device['name']}: {device['ip']} ({device['type']})")
                return True, data['devices']
            else:
                print(f"[FAIL] 获取失败: {data['message']}")
                return False, []
        else:
            print(f"[FAIL] HTTP错误: {response.status_code}")
            return False, []
    except Exception as e:
        print(f"[FAIL] 测试失败: {str(e)}")
        return False, []

def test_update_device():
    """测试更新设备"""
    print("\n" + "=" * 60)
    print("测试3: 更新设备")
    print("=" * 60)
    
    update_data = {
        "name": "test_switch",
        "ip": "192.168.1.11",  # 修改IP
        "username": "admin",
        "password": "newpassword",  # 修改密码
        "device_type": "cisco_ios"
    }
    
    try:
        response = requests.put(
            f"{BASE_URL}/api/devices",
            json=update_data,
            timeout=5
        )
        
        if response.status_code == 200:
            data = response.json()
            if data['status'] == 'success':
                print("[OK] 更新设备成功")
                print(f"   消息: {data['message']}")
                return True
            else:
                print(f"[FAIL] 更新失败: {data['message']}")
                return False
        else:
            print(f"[FAIL] HTTP错误: {response.status_code}")
            return False
    except Exception as e:
        print(f"[FAIL] 测试失败: {str(e)}")
        return False

def test_delete_device():
    """测试删除设备"""
    print("\n" + "=" * 60)
    print("测试4: 删除设备")
    print("=" * 60)
    
    try:
        response = requests.delete(
            f"{BASE_URL}/api/devices?device_name=test_switch",
            timeout=5
        )
        
        if response.status_code == 200:
            data = response.json()
            if data['status'] == 'success':
                print("[OK] 删除设备成功")
                print(f"   消息: {data['message']}")
                return True
            else:
                print(f"[FAIL] 删除失败: {data['message']}")
                return False
        else:
            print(f"[FAIL] HTTP错误: {response.status_code}")
            return False
    except Exception as e:
        print(f"[FAIL] 测试失败: {str(e)}")
        return False

def test_config_file():
    """测试配置文件"""
    print("\n" + "=" * 60)
    print("测试5: 配置文件操作")
    print("=" * 60)
    
    try:
        config = Config()
        
        # 清理可能存在的测试设备
        if "test_config" in config.get_devices():
            config.delete_device("test_config")
        
        # 测试添加
        print("测试添加设备到配置文件...")
        success, msg = config.add_device("test_config", "10.0.0.1", "user", "pass", "cisco_ios")
        if success:
            print(f"[OK] {msg}")
        else:
            print(f"[FAIL] {msg}")
            return False
        
        # 测试获取
        devices = config.get_devices()
        if "test_config" in devices:
            print(f"[OK] 设备已添加到配置: {devices['test_config']}")
        else:
            print("[FAIL] 设备未找到")
            return False
        
        # 测试更新
        print("测试更新设备配置...")
        success, msg = config.update_device("test_config", "10.0.0.2", "user2", "pass2", "huawei")
        if success:
            print(f"[OK] {msg}")
        else:
            print(f"[FAIL] {msg}")
            return False
        
        # 测试删除
        print("测试删除设备配置...")
        success, msg = config.delete_device("test_config")
        if success:
            print(f"[OK] {msg}")
        else:
            print(f"[FAIL] {msg}")
            return False
        
        # 验证删除
        devices = config.get_devices()
        if "test_config" not in devices:
            print("[OK] 设备已从配置中删除")
        else:
            print("[FAIL] 设备仍然存在")
            return False
        
        return True
        
    except Exception as e:
        print(f"[FAIL] 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主测试函数"""
    print("\n" + "=" * 60)
    print("设备管理功能测试")
    print("=" * 60)
    print("\n提示: 确保Flask应用正在运行 (python app.py)")
    print("=" * 60)
    
    results = []
    
    # 测试配置文件操作（不依赖Flask）
    results.append(("配置文件操作", test_config_file()))
    
    # 测试API接口（需要Flask运行）
    print("\n" + "=" * 60)
    print("API接口测试（需要Flask应用运行）")
    print("=" * 60)
    
    try:
        # 检查Flask是否运行
        response = requests.get(f"{BASE_URL}/api/status", timeout=2)
        flask_running = True
    except:
        flask_running = False
        print("\n[WARN] Flask应用未运行，跳过API测试")
        print("   启动Flask: python app.py")
    
    if flask_running:
        results.append(("添加设备API", test_add_device()))
        results.append(("获取设备列表API", test_get_devices()[0]))
        results.append(("更新设备API", test_update_device()))
        results.append(("删除设备API", test_delete_device()))
    
    # 输出测试结果
    print("\n" + "=" * 60)
    print("测试结果汇总")
    print("=" * 60)
    
    passed = 0
    failed = 0
    
    for name, result in results:
        status = "[OK] 通过" if result else "[FAIL] 失败"
        print(f"{name}: {status}")
        if result:
            passed += 1
        else:
            failed += 1
    
    print(f"\n总计: {passed} 通过, {failed} 失败")
    
    if failed == 0:
        print("\n[OK] 所有测试通过！")
        return 0
    else:
        print(f"\n[WARN] 有 {failed} 项测试失败")
        return 1

if __name__ == '__main__':
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\n测试已取消")
        sys.exit(0)

