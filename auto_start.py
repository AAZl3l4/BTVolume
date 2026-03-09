"""
开机自启动管理模块
"""
import os
import sys
import logging
import winreg as reg

logger = logging.getLogger(__name__)


class AutoStartManager:
    """开机自启动管理器"""
    
    REGISTRY_KEY = r'Software\Microsoft\Windows\CurrentVersion\Run'
    APP_NAME = 'BluetoothVolumeControl'
    
    @staticmethod
    def get_executable_path():
        """获取可执行文件路径"""
        if getattr(sys, 'frozen', False):
            # 打包后的exe
            return sys.executable
        else:
            # Python脚本模式
            script_path = os.path.abspath(sys.argv[0])
            return f'"{sys.executable}" "{script_path}"'
    
    @classmethod
    def enable(cls):
        """启用开机自启动"""
        try:
            exe_path = cls.get_executable_path()
            
            # 打开注册表项
            key = reg.OpenKey(reg.HKEY_CURRENT_USER, cls.REGISTRY_KEY, 0, reg.KEY_WRITE)
            
            # 设置值
            reg.SetValueEx(key, cls.APP_NAME, 0, reg.REG_SZ, exe_path)
            reg.CloseKey(key)
            
            logger.info(f"已启用开机自启动: {exe_path}")
            return True
            
        except Exception as e:
            logger.error(f"启用开机自启动失败: {e}")
            return False
    
    @classmethod
    def disable(cls):
        """禁用开机自启动"""
        try:
            # 打开注册表项
            key = reg.OpenKey(reg.HKEY_CURRENT_USER, cls.REGISTRY_KEY, 0, reg.KEY_WRITE)
            
            # 删除值
            try:
                reg.DeleteValue(key, cls.APP_NAME)
                logger.info("已禁用开机自启动")
            except FileNotFoundError:
                # 值不存在，说明本来就没启用
                pass
            
            reg.CloseKey(key)
            return True
            
        except Exception as e:
            logger.error(f"禁用开机自启动失败: {e}")
            return False
    
    @classmethod
    def is_enabled(cls):
        """检查是否已启用开机自启动"""
        try:
            key = reg.OpenKey(reg.HKEY_CURRENT_USER, cls.REGISTRY_KEY, 0, reg.KEY_READ)
            
            try:
                value, _ = reg.QueryValueEx(key, cls.APP_NAME)
                reg.CloseKey(key)
                
                # 检查路径是否匹配
                current_path = cls.get_executable_path()
                return value == current_path
            except FileNotFoundError:
                reg.CloseKey(key)
                return False
                
        except Exception as e:
            logger.error(f"检查开机自启动状态失败: {e}")
            return False
