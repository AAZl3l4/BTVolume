"""
单实例运行管理模块 - 确保程序只运行一个实例
使用文件锁实现，更可靠
"""
import os
import sys
import logging
import tempfile

logger = logging.getLogger(__name__)


class SingleInstance:
    """单实例管理器 - 使用文件锁实现"""
    
    def __init__(self):
        self.lock_file = None
        self.lock_file_path = os.path.join(tempfile.gettempdir(), 'bt_volume_control.lock')
    
    def check(self):
        """
        检查是否是第一个实例
        
        Returns:
            bool: True表示是第一个实例，False表示已有实例在运行
        """
        try:
            # 尝试打开锁文件
            import msvcrt
            
            # 如果文件已存在，尝试打开
            if os.path.exists(self.lock_file_path):
                try:
                    # 尝试删除旧的锁文件（如果之前的程序异常退出）
                    os.remove(self.lock_file_path)
                except:
                    # 删除失败，说明文件被占用
                    logger.info("检测到已有实例在运行")
                    return False
            
            # 创建并锁定文件
            self.lock_file = open(self.lock_file_path, 'w')
            
            try:
                # 尝试获取独占锁
                msvcrt.locking(self.lock_file.fileno(), msvcrt.LK_NBLCK, 1)
                # 如果成功获取锁，说明是第一个实例
                # 重新锁定为独占锁（保持锁定状态）
                msvcrt.locking(self.lock_file.fileno(), msvcrt.LK_UNLCK, 1)
                msvcrt.locking(self.lock_file.fileno(), msvcrt.LK_LOCK, 1)
                logger.info("这是第一个实例")
                return True
            except IOError:
                # 无法获取锁，说明已有实例在运行
                self.lock_file.close()
                self.lock_file = None
                logger.info("检测到已有实例在运行")
                return False
                
        except Exception as e:
            logger.error(f"检查单实例失败: {e}")
            # 出错时默认允许运行
            return True
    
    def activate_existing_window(self):
        """激活已存在实例的窗口"""
        try:
            import win32gui
            import win32con
            
            # 通过窗口标题查找
            hwnd = win32gui.FindWindow(None, "蓝牙耳机音量控制")
            
            if hwnd == 0:
                # 尝试查找部分匹配的窗口
                def callback(hwnd, extra):
                    if win32gui.IsWindowVisible(hwnd):
                        title = win32gui.GetWindowText(hwnd)
                        if "蓝牙" in title and "音量" in title:
                            extra.append(hwnd)
                    return True
                
                windows = []
                win32gui.EnumWindows(callback, windows)
                if windows:
                    hwnd = windows[0]
            
            if hwnd != 0:
                logger.info(f"找到已存在的窗口: {hwnd}")
                
                # 如果窗口最小化，恢复它
                if win32gui.IsIconic(hwnd):
                    win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
                
                # 将窗口带到前台
                win32gui.ShowWindow(hwnd, win32con.SW_SHOW)
                win32gui.SetForegroundWindow(hwnd)
                
                return True
            else:
                logger.warning("未找到已存在的窗口")
                return False
                
        except Exception as e:
            logger.error(f"激活已存在窗口失败: {e}")
            return False
    
    def cleanup(self):
        """清理资源"""
        try:
            if self.lock_file:
                import msvcrt
                # 解锁文件
                try:
                    msvcrt.locking(self.lock_file.fileno(), msvcrt.LK_UNLCK, 1)
                except:
                    pass
                # 关闭文件
                self.lock_file.close()
                self.lock_file = None
            
            # 删除锁文件
            if os.path.exists(self.lock_file_path):
                try:
                    os.remove(self.lock_file_path)
                except:
                    pass
        except:
            pass


def check_single_instance():
    """
    检查单实例的便捷函数
    
    Returns:
        tuple: (is_first_instance, single_instance_manager)
               is_first_instance为False时，需要调用activate_existing_window()
    """
    manager = SingleInstance()
    is_first = manager.check()
    
    if not is_first:
        # 激活已存在的窗口
        manager.activate_existing_window()
        return False, None
    
    return True, manager
