"""
蓝牙耳机音量控制工具 - 主程序入口
功能：定时设置蓝牙耳机音量，系统托盘快速设置
内存优化版本
"""
import sys
import os
import logging
import threading
import gc

# 确保可以导入本地模块
if getattr(sys, 'frozen', False):
    sys.path.insert(0, os.path.dirname(sys.executable))
else:
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 首先检查单实例
from single_instance import check_single_instance
is_first_instance, single_instance_manager = check_single_instance()

if not is_first_instance:
    # 已有实例在运行，退出
    print("程序已在运行，已激活现有窗口")
    sys.exit(0)

from audio_controller import AudioController
from bluetooth_checker import BluetoothChecker
from config_manager import ConfigManager
from scheduler import VolumeScheduler
from tray_icon import TrayIcon
from gui import MainWindow


# 配置日志 - 仅记录错误以减少开销
logging.basicConfig(
    level=logging.ERROR,
    format='%(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)


class BTVolumeControlApp:
    """
    蓝牙耳机音量控制应用主类
    优化内存占用，CPU占用极低
    """
    
    def __init__(self):
        """初始化应用"""
        self.config = ConfigManager()
        self.audio_controller = AudioController()
        self.bluetooth_checker = BluetoothChecker()
        self.tray_icon = TrayIcon(self)
        self.scheduler = VolumeScheduler(self.audio_controller, self.bluetooth_checker, self.tray_icon)
        self.gui = MainWindow(self)
        
        self.running = False
        self.tray_thread = None
        
        self._load_config()
    
    def _load_config(self):
        """加载配置并应用"""
        try:
            tasks = self.config.get_scheduled_tasks()
            for task in tasks:
                if task.get('enabled', True):
                    self.scheduler.add_task(
                        task_id=task.get('id', 0),
                        task_time=task.get('time', '00:00'),
                        volume=task.get('volume', 50)
                    )
        except Exception:
            pass
    
    def start(self):
        """启动应用"""
        self.running = True
        
        # 启动定时调度器
        self.scheduler.start()
        
        # 启动托盘图标（在单独线程中）
        self.tray_thread = threading.Thread(target=self.tray_icon.run, daemon=True)
        self.tray_thread.start()
        
        # 显示主窗口
        self.gui.show()
        
        # 运行GUI主循环
        self.gui.run()
    
    def show_window(self):
        """显示主窗口"""
        self.gui.show()
    
    def hide_window(self):
        """隐藏主窗口"""
        self.gui.hide()
    
    def set_volume(self, volume):
        """
        设置音量
        
        Args:
            volume (int): 音量值 (0-100)
        """
        try:
            if self.bluetooth_checker.is_bluetooth_connected():
                self.audio_controller.set_volume(volume)
                self.tray_icon.notify('音量设置', f'蓝牙耳机音量已设置为 {volume}%')
            else:
                self.tray_icon.notify('提示', '未检测到蓝牙耳机连接')
        except Exception:
            pass
    
    def check_bluetooth(self):
        """检查蓝牙状态"""
        try:
            if self.bluetooth_checker.is_bluetooth_connected():
                devices = self.bluetooth_checker.get_connected_bluetooth_devices()
                if devices:
                    device_names = '\n'.join(devices[:3])
                    self.tray_icon.notify('蓝牙状态', f'已连接:\n{device_names}')
                else:
                    self.tray_icon.notify('蓝牙状态', '已连接蓝牙耳机')
            else:
                self.tray_icon.notify('蓝牙状态', '未连接蓝牙耳机')
        except Exception:
            pass
    
    def reload_scheduler(self):
        """重新加载定时任务"""
        try:
            tasks = self.config.get_scheduled_tasks()
            self.scheduler.reload_tasks(tasks)
        except Exception:
            pass
    
    def exit_app(self):
        """退出应用"""
        self.running = False
        
        # 停止调度器
        self.scheduler.stop()
        
        # 停止托盘图标
        self.tray_icon.stop()
        
        # 停止GUI
        self.gui.stop()
        
        # 保存配置
        self.config.save()
        
        # 清理单实例锁
        global single_instance_manager
        if single_instance_manager:
            single_instance_manager.cleanup()
        
        # 强制垃圾回收
        gc.collect()
        
        os._exit(0)


def main():
    """主函数"""
    try:
        app = BTVolumeControlApp()
        app.start()
    except Exception as e:
        print(f"错误: {e}")
        input("按回车键退出...")


if __name__ == '__main__':
    main()
