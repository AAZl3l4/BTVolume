"""
定时任务调度模块 - 管理定时音量设置任务
"""
import schedule
import time
import threading
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class VolumeScheduler:
    """音量定时调度器类"""
    
    def __init__(self, audio_controller, bluetooth_checker, tray_icon=None):
        """
        初始化调度器
        
        Args:
            audio_controller: 音频控制器实例
            bluetooth_checker: 蓝牙检测器实例
            tray_icon: 托盘图标实例（用于发送通知）
        """
        self.audio_controller = audio_controller
        self.bluetooth_checker = bluetooth_checker
        self.tray_icon = tray_icon
        self.running = False
        self.scheduler_thread = None
        self.tasks = {}  # 存储schedule任务对象
        self._lock = threading.Lock()
    
    def start(self):
        """启动调度器"""
        if not self.running:
            self.running = True
            self.scheduler_thread = threading.Thread(target=self._run_scheduler, daemon=True)
            self.scheduler_thread.start()
            logger.info("定时调度器已启动")
    
    def stop(self):
        """停止调度器"""
        self.running = False
        schedule.clear()
        self.tasks.clear()
        if self.scheduler_thread:
            self.scheduler_thread.join(timeout=1)
        logger.info("定时调度器已停止")
    
    def _run_scheduler(self):
        """调度器主循环"""
        # 初始化COM组件（Windows多线程需要）
        import pythoncom
        pythoncom.CoInitialize()
        
        while self.running:
            try:
                schedule.run_pending()
            except Exception as e:
                logger.error(f"调度器运行错误: {e}")
            time.sleep(1)
        
        # 释放COM组件
        pythoncom.CoUninitialize()
    
    def add_task(self, task_id, task_time, volume):
        """
        添加定时任务
        
        Args:
            task_id (int): 任务ID
            task_time (str): 任务时间 (HH:MM格式)
            volume (int): 音量值
            
        Returns:
            bool: 是否成功添加
        """
        try:
            with self._lock:
                # 如果任务已存在，先清除
                if task_id in self.tasks:
                    schedule.cancel_job(self.tasks[task_id])
                
                # 创建新的定时任务
                job = schedule.every().day.at(task_time).do(
                    self._execute_volume_task, volume=volume
                )
                self.tasks[task_id] = job
                
            logger.info(f"添加定时任务: {task_time} -> {volume}%")
            return True
            
        except Exception as e:
            logger.error(f"添加定时任务失败: {e}")
            return False
    
    def remove_task(self, task_id):
        """
        删除定时任务
        
        Args:
            task_id (int): 任务ID
            
        Returns:
            bool: 是否成功删除
        """
        try:
            with self._lock:
                if task_id in self.tasks:
                    schedule.cancel_job(self.tasks[task_id])
                    del self.tasks[task_id]
                    logger.info(f"删除定时任务: {task_id}")
                    return True
            return False
        except Exception as e:
            logger.error(f"删除定时任务失败: {e}")
            return False
    
    def clear_all_tasks(self):
        """清除所有定时任务"""
        with self._lock:
            schedule.clear()
            self.tasks.clear()
        logger.info("已清除所有定时任务")
    
    def _execute_volume_task(self, volume):
        """
        执行音量设置任务
        
        Args:
            volume (int): 音量值
        """
        # 初始化COM组件（Windows多线程需要）
        import pythoncom
        pythoncom.CoInitialize()
        
        try:
            current_time = datetime.now().strftime("%H:%M:%S")
            logger.info(f"[{current_time}] 执行定时任务: 设置音量 {volume}%")
            
            # 检查是否有蓝牙耳机连接
            if self.bluetooth_checker.is_bluetooth_connected():
                self.audio_controller.set_volume(volume)
                # 发送通知
                if self.tray_icon:
                    self.tray_icon.notify(
                        '定时任务执行',
                        f'蓝牙耳机音量已设置为 {volume}%'
                    )
            else:
                # 发送通知
                if self.tray_icon:
                    self.tray_icon.notify(
                        '定时任务跳过',
                        '未检测到蓝牙耳机连接'
                    )
                
        except Exception as e:
            logger.error(f"执行定时任务失败: {e}")
            if self.tray_icon:
                self.tray_icon.notify(
                    '定时任务失败',
                    f'错误: {str(e)}'
                )
        finally:
            # 释放COM组件
            pythoncom.CoUninitialize()
    
    def reload_tasks(self, tasks_config):
        """
        重新加载所有定时任务
        
        Args:
            tasks_config (list): 任务配置列表
        """
        self.clear_all_tasks()
        
        for task in tasks_config:
            if task.get('enabled', True):
                self.add_task(
                    task_id=task.get('id', 0),
                    task_time=task.get('time', '00:00'),
                    volume=task.get('volume', 50)
                )
        
        logger.info(f"已重新加载 {len(tasks_config)} 个定时任务")
