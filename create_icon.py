"""
创建应用程序图标文件
"""
from PIL import Image, ImageDraw
import os


def create_icon():
    """创建ICO图标文件"""
    # 创建不同尺寸的图标
    sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
    images = []
    
    for size in sizes:
        # 创建图像
        image = Image.new('RGBA', size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)
        
        # 计算缩放比例
        scale = size[0] / 64
        
        # 绘制扬声器形状（缩放）
        speaker_points = [
            (int(10 * scale), int(25 * scale)),
            (int(10 * scale), int(39 * scale)),
            (int(20 * scale), int(39 * scale)),
            (int(35 * scale), int(50 * scale)),
            (int(35 * scale), int(14 * scale)),
            (int(20 * scale), int(25 * scale))
        ]
        draw.polygon(speaker_points, fill=(66, 133, 244, 255))
        
        # 绘制声波（缩放）
        if size[0] >= 32:  # 只有较大尺寸才绘制声波
            draw.arc(
                [int(38 * scale), int(18 * scale), int(48 * scale), int(46 * scale)],
                -60, 60, fill=(66, 133, 244, 255), width=max(1, int(2 * scale))
            )
            draw.arc(
                [int(45 * scale), int(12 * scale), int(58 * scale), int(52 * scale)],
                -60, 60, fill=(66, 133, 244, 200), width=max(1, int(2 * scale))
            )
        
        images.append(image)
    
    # 保存为ICO文件
    icon_path = os.path.join(os.path.dirname(__file__), 'app_icon.ico')
    images[0].save(
        icon_path,
        format='ICO',
        sizes=[(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)],
        append_images=images[1:]
    )
    
    print(f"图标已创建: {icon_path}")
    return icon_path


if __name__ == '__main__':
    create_icon()
