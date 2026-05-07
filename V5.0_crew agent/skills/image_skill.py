import os
import cv2
from datetime import datetime

# 关键改动：保留核心算法，增加 *args 和 **kwargs 兼容长记忆传参
def cartoonize_image(file_path, *args, **kwargs):
    """
    接收相对路径，转换为绝对路径，进行极致的高对比度黑白铅笔素描风渲染并保存。
    """
    # 彻底解决路径重复叠加的核心逻辑
    target = os.path.abspath(file_path)
    
    # 1. 获取来自 Agent 记忆的风格偏好
    # 即使目前固定画风，也要接收这个参数以防止 main.py 报错
    style_pref = kwargs.get('style', '极致铅笔风')
    
    if not os.path.exists(target):
        return f"❌ 找不到图片文件：{target}\n提示：请确认文件是否在正确文件夹中。"

    try:
        # 读取图片
        img = cv2.imread(target)
        if img is None:
            return "❌ 图片文件损坏或格式不支持。"

        # --- 2. 极致铅笔风渲染核心算法（完全保留你的逻辑） ---
        print(f"🧠 记忆同步：正在以【{style_pref}】偏好进行处理...")
        print(f"⚡ 开始为 {os.path.basename(target)} 注入【铅笔素描】风暴...")
        
        # A. 转换为灰度图
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # B. 核心：素描化反转逻辑
        inv_gray = cv2.bitwise_not(gray)
        
        # 高斯模糊：窗口 21, 21 获得自然阴影
        inv_blurred = cv2.GaussianBlur(inv_gray, (21, 21), 0)
        
        # 颜色减淡 (Color Dodge) 混合：这是你画风的核心
        sketch = cv2.divide(gray, cv2.bitwise_not(inv_blurred), scale=256.0)

        # C. 高对比度增强（保持极致黑白感）
        # 使用 0.9 的阈值确保画面干净、对比强烈
        _, sketch_high_contrast = cv2.threshold(sketch, int(255 * 0.9), 255, cv2.THRESH_BINARY)
        
        # 双边滤波抹平杂色，保留硬朗边缘
        sketch_cleaned = cv2.bilateralFilter(sketch_high_contrast, d=9, sigmaColor=75, sigmaSpace=75)

        # 3. 生成带时间戳的文件名并保存
        time_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_dir, full_name = os.path.split(target)
        name_part, ext_part = os.path.splitext(full_name)
        
        # 文件名标注风格
        new_filename = f"{name_part}_极致铅笔_{time_str}{ext_part}"
        save_path = os.path.join(file_dir, new_filename)
        
        cv2.imwrite(save_path, sketch_cleaned)
        
        return (
            f"✨ 渲染成功！【极致黑白铅笔风】\n"
            f"📂 原始文件: {full_name}\n"
            f"💾 文件保存: {new_filename}"
        )

    except Exception as e:
        return f"❌ 处理图片时发生未知错误: {str(e)}"