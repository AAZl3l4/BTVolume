"""
系统托盘图标模块 - 管理系统托盘图标和菜单
"""
import pystray
from PIL import Image, ImageDraw
import threading
import logging

logger = logging.getLogger(__name__)


def create_app_icon():
    """
    创建应用程序图标
    
    Returns:
        PIL.Image: 图标图像
    """
    # 创建一个简单的音量图标
    width = 64
    height = 64
    image = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    
    # 绘制扬声器形状
    # 扬声器主体
    draw.polygon([
        (10, 25), (10, 39), (20, 39), (35, 50), (35, 14), (20, 25)
    ], fill=(66, 133, 244, 255))
    
    # 声波
    draw.arc([38, 18, 48, 46], -60, 60, fill=(66, 133, 244, 255), width=2)
    draw.arc([45, 12, 58, 52], -60, 60, fill=(66, 133, 244, 200), width=2)
    
    return image


class TrayIcon:
    """系统托盘图标类"""
    
    def __init__(self, app):
        """
        初始化托盘图标
        
        Args:
            app: 主应用实例
        """
        self.app = app
        self.icon = None
        self.menu = None
        self._setup_icon()
    
    def _create_icon_image(self):
        """
        创建托盘图标图像
        
        Returns:
            PIL.Image: 图标图像
        """
        return create_app_icon()
    
    def _setup_icon(self):
        """设置托盘图标和菜单"""
        icon_image = self._create_icon_image()
        
        # 创建菜单
        self.menu = self._create_menu()
        
        # 创建托盘图标
        self.icon = pystray.Icon(
            'bt_volume_control',
            icon_image,
            '蓝牙耳机音量控制',
            self.menu
        )
    
    def _create_menu(self):
        """
        创建托盘菜单
        音量百分比直接显示在一级菜单
        
        Returns:
            pystray.Menu: 菜单对象
        """
        menu_items = []
        
        # 显示主窗口
        menu_items.append(pystray.MenuItem(
            '打开设置',
            self._on_show_window,
            default=True
        ))
        
        menu_items.append(pystray.Menu.SEPARATOR)
        
        # 快速设置音量 - 直接显示在一级菜单
        preset_volumes = self.app.config.get_preset_volumes()
        for volume in preset_volumes:
            # 使用默认参数捕获volume，避免闭包问题
            def make_callback(vol):
                return lambda icon, item: self._on_set_volume(vol)
            menu_items.append(pystray.MenuItem(
                f'音量 {volume}%',
                make_callback(volume)
            ))
        
        menu_items.append(pystray.Menu.SEPARATOR)
        
        # 检查蓝牙状态
        menu_items.append(pystray.MenuItem(
            '检查蓝牙状态',
            self._on_check_bluetooth
        ))
        
        menu_items.append(pystray.Menu.SEPARATOR)
        
        # 退出
        menu_items.append(pystray.MenuItem(
            '退出',
            self._on_exit
        ))
        
        return pystray.Menu(*menu_items)
    
    def _on_show_window(self, icon=None, item=None):
        """显示主窗口"""
        self.app.show_window()
    
    def _on_set_volume(self, volume):
        """
        设置音量
        
        Args:
            volume (int): 音量值
        """
        self.app.set_volume(volume)
    
    def _on_check_bluetooth(self, icon=None, item=None):
        """检查蓝牙状态"""
        self.app.check_bluetooth()
    
    def _on_exit(self, icon=None, item=None):
        """退出应用"""
        self.app.exit_app()
    
    def run(self):
        """运行托盘图标"""
        try:
            logger.info("托盘图标已启动")
            self.icon.run()
        except Exception as e:
            logger.error(f"托盘图标运行错误: {e}")
    
    def stop(self):
        """停止托盘图标"""
        try:
            if self.icon:
                self.icon.stop()
                logger.info("托盘图标已停止")
        except Exception as e:
            logger.error(f"停止托盘图标失败: {e}")
    
    def update_menu(self):
        """更新菜单"""
        try:
            self.menu = self._create_menu()
            if self.icon:
                self.icon.menu = self.menu
        except Exception as e:
            logger.error(f"更新菜单失败: {e}")
    
    def notify(self, title, message):
        """
        显示通知
        
        Args:
            title (str): 通知标题
            message (str): 通知内容
        """
        try:
            if self.icon:
                self.icon.notify(message, title)
        except Exception as e:
            logger.error(f"显示通知失败: {e}")
