# BTVolume

一款轻量级的Windows桌面应用，用于定时自动设置蓝牙耳机音量，支持系统托盘快速操作。

## 功能特性

- **定时音量控制**: 设置指定时间自动调整蓝牙耳机音量
- **蓝牙检测**: 仅在蓝牙耳机连接时执行音量设置
- **系统托盘**: 快速设置常用音量，最小化到托盘运行
- **开机自启动**: 支持开机自动运行
- **单实例运行**: 防止重复启动，自动激活已有窗口
- **低资源占用**: 内存占用约20-30MB，CPU占用极低

## 项目结构

```
.
├── main.py                 # 主程序入口
├── audio_controller.py     # 音频控制模块
├── bluetooth_checker.py    # 蓝牙检测模块
├── config_manager.py       # 配置管理模块
├── scheduler.py            # 定时任务调度模块
├── tray_icon.py            # 系统托盘图标模块
├── gui.py                  # GUI界面模块
├── auto_start.py           # 开机自启动管理
├── single_instance.py      # 单实例运行管理
├── build.py                # 打包脚本
├── requirements.txt        # 依赖列表
└── app_icon.ico           # 应用图标
```

## 运行说明

### 开发模式运行

```bash
# 安装依赖
pip install -r requirements.txt

# 运行程序
python main.py
```

### 打包后运行

```bash
# 打包生成exe
python build.py

# 运行exe（在dist目录中）
dist/蓝牙耳机音量控制.exe
```

### 使用说明

1. **设置定时任务**: 在"定时任务"区域添加时间和音量，程序会在指定时间自动设置蓝牙耳机音量
2. **快速设置音量**: 右键托盘图标，选择预设音量快速调整
3. **开机自启动**: 勾选"开机自启动"复选框，程序会随Windows启动
4. **双击编辑任务**: 在定时任务列表中双击任务行可直接编辑，编辑后点击保存按钮保存
5. **保存配置**: 点击"保存配置"按钮，程序会将当前设置保存到配置文件中

### 注意事项

- 定时任务只在蓝牙耳机连接时才会执行音量设置
- 程序采用单实例运行，重复启动会激活已有窗口
- 配置文件保存在程序同目录下，删除后会恢复默认设置

## 蓝牙耳机品牌支持

### 支持的设备类型

程序通过设备名称关键词匹配识别蓝牙耳机。已内置支持的品牌关键词：

```python
HEADPHONE_KEYWORDS = [
    # 通用关键词
    'headphone', 'headset', 'earphone', 'earbud', 'airpod', 'pod',
    '耳机', '耳麦', '蓝牙', 'bluetooth',
    # 国际品牌
    'sony', 'bose', 'beats', 'jbl', 'sennheiser',
    'akg', 'jabra', 'plantronics',
    # 国产品牌
    'xiaomi', 'huawei', 'oppo', 'vivo',
    '漫步者', '铁三角', 'koomze'
]
```

### 添加新品牌支持

如果你的蓝牙耳机未被识别，请在 `bluetooth_checker.py` 中的 `HEADPHONE_KEYWORDS` 列表添加设备名称关键词：

```python
# 例如：添加 "漫步者" 品牌
HEADPHONE_KEYWORDS = [
    # ... 原有关键词 ...
    '漫步者',  # 添加新品牌
]
```

**如何确定关键词**：
1. 连接蓝牙耳机
2. 查看蓝牙耳机名称（如 "EDIFIER W820NB"）
3. 提取关键词（如 "EDIFIER"）添加到列表中

## 配置说明

配置文件：`bt_volume_config.json`（与exe同目录）

```json
{
  "preset_volumes": [30, 50, 70, 100],
  "scheduled_tasks": [
    {"id": 0, "time": "09:00", "volume": 50, "enabled": true}
  ],
  "auto_start": false,
  "minimize_to_tray": true
}
```

## 依赖列表

- pycaw: Windows音频控制
- pystray: 系统托盘图标
- pywin32: Windows API调用
- Pillow: 图像处理
- schedule: 定时任务
- pyinstaller: 打包工具

## 运行环境

- Windows 10/11
- Python 3.8+ (开发模式)
- 无需Python环境 (打包后)
