"""
音频控制器模块 - 负责控制Windows系统音量
"""
from pycaw.pycaw import AudioUtilities
import logging

logger = logging.getLogger(__name__)


class AudioController:
    """音频控制器类，用于获取和设置系统音量"""
    
    def __init__(self):
        pass
    
    def _get_device(self):
        """
        获取默认音频设备
        
        Returns:
            AudioDevice: 音频设备对象
        """
        try:
            return AudioUtilities.GetSpeakers()
        except Exception as e:
            logger.error(f"获取音频设备失败: {e}")
            return None
    
    def get_volume(self):
        """
        获取当前系统音量
        
        Returns:
            int: 当前音量值 (0-100)
        """
        try:
            device = self._get_device()
            if device and hasattr(device, 'EndpointVolume'):
                volume_interface = device.EndpointVolume
                current_volume = volume_interface.GetMasterVolumeLevelScalar()
                return int(current_volume * 100)
        except Exception as e:
            logger.error(f"获取音量失败: {e}")
        return 0
    
    def set_volume(self, volume):
        """
        设置系统音量
        
        Args:
            volume (int): 音量值 (0-100)
        """
        try:
            device = self._get_device()
            if device and hasattr(device, 'EndpointVolume'):
                volume_interface = device.EndpointVolume
                # 限制音量范围在0-100之间
                volume = max(0, min(100, volume))
                volume_interface.SetMasterVolumeLevelScalar(volume / 100, None)
                logger.info(f"音量已设置为: {volume}%")
                return True
        except Exception as e:
            logger.error(f"设置音量失败: {e}")
        return False
    
    def get_mute_state(self):
        """
        获取静音状态
        
        Returns:
            bool: 是否静音
        """
        try:
            device = self._get_device()
            if device and hasattr(device, 'EndpointVolume'):
                volume_interface = device.EndpointVolume
                return volume_interface.GetMute()
        except Exception as e:
            logger.error(f"获取静音状态失败: {e}")
        return False
    
    def set_mute(self, mute):
        """
        设置静音状态
        
        Args:
            mute (bool): 是否静音
        """
        try:
            device = self._get_device()
            if device and hasattr(device, 'EndpointVolume'):
                volume_interface = device.EndpointVolume
                volume_interface.SetMute(mute, None)
        except Exception as e:
            logger.error(f"设置静音状态失败: {e}")
