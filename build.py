"""
打包脚本 - 使用PyInstaller打包为exe
"""
import PyInstaller.__main__
import os
import sys


def build():
    """
    打包应用程序为exe文件
    使用PyInstaller进行单文件打包
    """
    # 获取当前目录
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # PyInstaller参数
    args = [
        'main.py',  # 主程序入口
        '--name=蓝牙耳机音量控制',  # 应用名称
        '--onefile',  # 打包为单个exe文件
        '--windowed',  # 不显示控制台窗口
        '--icon=app_icon.ico',  # 使用自定义图标
        '--clean',  # 清理临时文件
        '--noconfirm',  # 不确认覆盖
        
        # 隐藏导入
        '--hidden-import=pycaw',
        '--hidden-import=comtypes',
        '--hidden-import=pystray',
        '--hidden-import=PIL',
        '--hidden-import=schedule',
        '--hidden-import=win32api',
        '--hidden-import=win32con',
        '--hidden-import=win32gui',
        
        # 排除不必要的模块以减小体积
        '--exclude-module=matplotlib',
        '--exclude-module=numpy',
        '--exclude-module=pandas',
        '--exclude-module=scipy',
        '--exclude-module=PyQt5',
        '--exclude-module=PyQt6',
        '--exclude-module=PySide2',
        '--exclude-module=PySide6',
        '--exclude-module=tkinter.test',
        '--exclude-module=unittest',
        '--exclude-module=pydoc',
        '--exclude-module=email',
        '--exclude-module=http',
        '--exclude-module=xml',
        '--exclude-module=html',
        '--exclude-module=lib2to3',
        '--exclude-module=distutils',
        '--exclude-module=multiprocessing',
        
        # 输出目录
        f'--distpath={os.path.join(current_dir, "dist")}',
        f'--workpath={os.path.join(current_dir, "build")}',
        f'--specpath={current_dir}',
    ]
    
    print("开始打包...")
    print(f"参数: {' '.join(args)}")
    
    try:
        PyInstaller.__main__.run(args)
        print("\n打包完成!")
        print(f"输出目录: {os.path.join(current_dir, 'dist')}")
    except Exception as e:
        print(f"打包失败: {e}")
        sys.exit(1)


if __name__ == '__main__':
    build()
