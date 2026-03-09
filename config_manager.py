"""
配置管理模块 - 管理应用的配置数据
"""
import json
import os
import logging

logger = logging.getLogger(__name__)


class ConfigManager:
    """配置管理器类"""
    
    DEFAULT_CONFIG = {
        'preset_volumes': [30, 50, 70, 100],  # 预设音量
        'scheduled_tasks': [],  # 定时任务列表
        'auto_start': False,  # 是否开机自启
        'minimize_to_tray': True,  # 关闭时最小化到托盘
    }
    
    def __init__(self, config_file='bt_volume_config.json'):
        """
        初始化配置管理器
        
        Args:
            config_file (str): 配置文件名
        """
        # 获取程序所在目录
        if getattr(os.sys, 'frozen', False):
            # 打包后的exe运行
            app_dir = os.path.dirname(os.sys.executable)
        else:
            # 脚本运行
            app_dir = os.path.dirname(os.path.abspath(__file__))
        
        self.config_file = os.path.join(app_dir, config_file)
        self.config = self.DEFAULT_CONFIG.copy()
        self.load()
    
    def load(self):
        """从文件加载配置"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    loaded_config = json.load(f)
                    self.config.update(loaded_config)
                logger.info(f"配置已加载: {self.config_file}")
        except Exception as e:
            logger.error(f"加载配置失败: {e}")
            self.config = self.DEFAULT_CONFIG.copy()
    
    def save(self):
        """保存配置到文件"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, ensure_ascii=False, indent=2)
            logger.info(f"配置已保存: {self.config_file}")
            return True
        except Exception as e:
            logger.error(f"保存配置失败: {e}")
            return False
    
    def get(self, key, default=None):
        """
        获取配置项
        
        Args:
            key (str): 配置键
            default: 默认值
            
        Returns:
            配置值
        """
        return self.config.get(key, default)
    
    def set(self, key, value):
        """
        设置配置项
        
        Args:
            key (str): 配置键
            value: 配置值
        """
        self.config[key] = value
    
    def get_preset_volumes(self):
        """
        获取预设音量列表
        
        Returns:
            list: 预设音量列表
        """
        return self.config.get('preset_volumes', self.DEFAULT_CONFIG['preset_volumes'])
    
    def set_preset_volumes(self, volumes):
        """
        设置预设音量列表
        
        Args:
            volumes (list): 音量列表
        """
        # 确保音量值在0-100之间
        valid_volumes = [max(0, min(100, int(v))) for v in volumes if isinstance(v, (int, float))]
        self.config['preset_volumes'] = valid_volumes
    
    def get_scheduled_tasks(self):
        """
        获取定时任务列表
        
        Returns:
            list: 定时任务列表
        """
        return self.config.get('scheduled_tasks', [])
    
    def add_scheduled_task(self, task_time, volume, enabled=True):
        """
        添加定时任务
        
        Args:
            task_time (str): 任务时间 (HH:MM格式)
            volume (int): 音量值
            enabled (bool): 是否启用
            
        Returns:
            dict: 任务字典
        """
        task = {
            'id': len(self.config.get('scheduled_tasks', [])),
            'time': task_time,
            'volume': max(0, min(100, int(volume))),
            'enabled': enabled
        }
        
        if 'scheduled_tasks' not in self.config:
            self.config['scheduled_tasks'] = []
        
        self.config['scheduled_tasks'].append(task)
        return task
    
    def remove_scheduled_task(self, task_id):
        """
        删除定时任务
        
        Args:
            task_id (int): 任务ID
            
        Returns:
            bool: 是否成功删除
        """
        tasks = self.config.get('scheduled_tasks', [])
        for i, task in enumerate(tasks):
            if task.get('id') == task_id:
                tasks.pop(i)
                # 重新编号
                for j, t in enumerate(tasks):
                    t['id'] = j
                return True
        return False
    
    def update_scheduled_task(self, task_id, **kwargs):
        """
        更新定时任务
        
        Args:
            task_id (int): 任务ID
            **kwargs: 要更新的字段
            
        Returns:
            bool: 是否成功更新
        """
        tasks = self.config.get('scheduled_tasks', [])
        for task in tasks:
            if task.get('id') == task_id:
                task.update(kwargs)
                # 确保音量值合法
                if 'volume' in task:
                    task['volume'] = max(0, min(100, int(task['volume'])))
                return True
        return False
    
    def is_auto_start_enabled(self):
        """
        检查是否启用开机自启动
        
        Returns:
            bool: 是否启用
        """
        return self.config.get('auto_start', False)
    
    def set_auto_start(self, enabled):
        """
        设置开机自启动
        
        Args:
            enabled (bool): 是否启用
        """
        self.config['auto_start'] = bool(enabled)
