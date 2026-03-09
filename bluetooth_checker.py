"""
蓝牙检测模块 - 检测蓝牙耳机是否连接
使用Windows API检测蓝牙设备
"""
import win32api
import win32con
import win32gui
import ctypes
from ctypes import wintypes
import logging

logger = logging.getLogger(__name__)


# 蓝牙API常量
BLUETOOTH_MAX_NAME_SIZE = 248


class BLUETOOTH_DEVICE_INFO(ctypes.Structure):
    """蓝牙设备信息结构体"""
    _fields_ = [
        ("dwSize", wintypes.DWORD),
        ("Address", ctypes.c_ulonglong),
        ("ulClassofDevice", wintypes.ULONG),
        ("fConnected", wintypes.BOOL),
        ("fRemembered", wintypes.BOOL),
        ("fAuthenticated", wintypes.BOOL),
        ("stLastSeen", ctypes.c_uint64),
        ("stLastUsed", ctypes.c_uint64),
        ("szName", wintypes.WCHAR * BLUETOOTH_MAX_NAME_SIZE),
    ]


class BluetoothChecker:
    """蓝牙检测器类"""
    
    # 常见的蓝牙耳机设备名称关键词
    HEADPHONE_KEYWORDS = [
        'headphone', 'headset', 'earphone', 'earbud', 'airpod', 'pod',
        '耳机', '耳麦', '蓝牙', 'bluetooth', 'sony', 'bose', 'beats',
        'jbl', 'sennheiser', 'xiaomi', 'huawei', 'oppo', 'vivo',
        '漫步者', '铁三角', 'akg', 'jabra', 'plantronics', 'koomze'
    ]
    
    def __init__(self):
        self.bthprops_dll = None
        self._load_bluetooth_api()
    
    def _load_bluetooth_api(self):
        """加载蓝牙API"""
        try:
            self.bthprops_dll = ctypes.windll.LoadLibrary("bthprops.cpl")
        except Exception as e:
            logger.warning(f"加载蓝牙API失败: {e}")
            self.bthprops_dll = None
    
    def is_bluetooth_connected(self):
        """
        检查是否有蓝牙音频设备连接
        
        Returns:
            bool: 是否有蓝牙耳机连接
        """
        try:
            # 方法1: 通过音频设备检测（更可靠）
            return self._check_audio_endpoint()
        except Exception as e:
            logger.error(f"检测蓝牙连接失败: {e}")
            return False
    
    def _check_audio_endpoint(self):
        """
        通过音频端点检测蓝牙设备
        
        Returns:
            bool: 是否检测到蓝牙音频设备
        """
        try:
            from pycaw.pycaw import AudioUtilities
            from pycaw.constants import AudioDeviceState
            
            # 获取所有音频设备
            devices = AudioUtilities.GetAllDevices()
            
            for device in devices:
                try:
                    # 获取设备友好名称
                    friendly_name = device.FriendlyName.lower() if device.FriendlyName else ""
                    
                    # 检查是否是蓝牙设备
                    if self._is_bluetooth_device_name(friendly_name):
                        # 检查设备是否处于活动状态
                        # 支持多种状态表示方式
                        is_active = False
                        try:
                            if hasattr(device.state, 'value'):
                                is_active = device.state == AudioDeviceState.Active
                            elif isinstance(device.state, int):
                                is_active = device.state == 1
                            else:
                                # 字符串或其他类型
                                state_str = str(device.state).lower()
                                is_active = 'active' in state_str
                        except:
                            # 如果无法判断状态，只要有设备名匹配就认为是连接的
                            is_active = True
                        
                        if is_active:
                            logger.debug(f"检测到连接的蓝牙设备: {device.FriendlyName}")
                            return True
                except:
                    continue
            
            return False
            
        except Exception as e:
            logger.error(f"检测音频端点失败: {e}")
            return False
    
    def _is_bluetooth_device_name(self, name):
        """
        判断设备名称是否是蓝牙设备
        
        Args:
            name (str): 设备名称
            
        Returns:
            bool: 是否是蓝牙设备
        """
        if not name:
            return False
        
        name_lower = name.lower()
        
        # 检查是否包含蓝牙关键词
        for keyword in self.HEADPHONE_KEYWORDS:
            if keyword in name_lower:
                return True
        
        return False
    
    def get_connected_bluetooth_devices(self):
        """
        获取所有连接的蓝牙设备列表
        使用集合去重，避免播放设备和录音设备重复显示
        
        Returns:
            list: 设备名称列表（去重后）
        """
        devices_set = set()  # 使用集合去重
        try:
            from pycaw.pycaw import AudioUtilities
            from pycaw.constants import AudioDeviceState
            
            all_devices = AudioUtilities.GetAllDevices()
            for device in all_devices:
                try:
                    friendly_name = device.FriendlyName if device.FriendlyName else ""
                    if self._is_bluetooth_device_name(friendly_name.lower()):
                        # 检查设备是否处于活动状态
                        is_active = False
                        try:
                            if hasattr(device.state, 'value'):
                                is_active = device.state == AudioDeviceState.Active
                            elif isinstance(device.state, int):
                                is_active = device.state == 1
                            else:
                                state_str = str(device.state).lower()
                                is_active = 'active' in state_str
                        except:
                            is_active = True
                        
                        if is_active:
                            devices_set.add(friendly_name)
                except:
                    continue
                    
        except Exception as e:
            logger.error(f"获取蓝牙设备列表失败: {e}")
        
        return list(devices_set)  # 转换为列表返回
