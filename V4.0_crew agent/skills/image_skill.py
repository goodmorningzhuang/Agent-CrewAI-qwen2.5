import os
import cv2  # 需要安装 opencv-python

def cartoonize_image(file_path):
    """
    接收相对路径，转换为绝对路径，进行极致的高对比度黑白铅笔素描风（Sketch）渲染并保存。
    """
    # 彻底解决路径重复叠加（如 image/image/2.jpeg）的核心逻辑
    target = os.path.abspath(file_path)
    print(f"🔍 调试：正在精准定位图片 -> {target}")

    if not os.path.exists(target):
        return f"❌ 找不到图片文件：{target}\n提示：请确认文件是否真的在 image 文件夹里。"

    try:
        # 读取图片
        img = cv2.imread(target)
        if img is None:
            return "❌ 图片文件损坏或格式不支持，无法读取。"

        # --- 2. 极致铅笔风渲染核心算法 ---
        # 我们不再追求简约色块，而是追求高对比度的线条和阴影
        print(f"⚡ 开始为 {os.path.basename(target)} 注入【铅笔素描】风暴...")
        
        # A. 转换为灰度图
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # B. 核心：素描化反转逻辑
        # 1. 对灰度图进行色彩反转
        inv_gray = cv2.bitwise_not(gray)
        
        # 2. 对反转图进行大窗口高斯模糊
        # 窗口越大，生成的铅笔风阴影越柔和、越自然。这里调大到 21, 21
        inv_blurred = cv2.GaussianBlur(inv_gray, (21, 21), 0)
        
        # 3. 将原灰度图与模糊反转图进行“颜色减淡” (Color Dodge) 混合
        # 这一步是生成铅笔素描线条的关键。
        sketch = cv2.divide(gray, cv2.bitwise_not(inv_blurred), scale=256.0)

        # C. 高对比度增强 (Sketch Enhancement)
        # 传统的 Divide 生成的线往往偏灰。我们需要让黑线更黑，白底更白。
        # 调整阈值（0.9）来控制黑白分界。
        _, sketch_high_contrast = cv2.threshold(sketch, int(255 * 0.9), 255, cv2.THRESH_BINARY)
        
        # 再次使用双边滤波抹平杂色块，但保留硬边缘线
        sketch_cleaned = cv2.bilateralFilter(sketch_high_contrast, d=9, sigmaColor=75, sigmaSpace=75)

        # 3. 生成带时间戳的文件名并保存
        from datetime import datetime
        time_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        file_dir, full_name = os.path.split(target)
        name_part, ext_part = os.path.splitext(full_name)
        # 更新文件名标识
        new_filename = f"{name_part}_铅笔风_{time_str}{ext_part}"
        save_path = os.path.join(file_dir, new_filename)
        
        # 保存结果 (铅笔风通常是单通道灰度图)
        cv2.imwrite(save_path, sketch_cleaned)
        
        return (
            f"✨ 渲染成功！【黑白铅笔风】\n"
            f"📂 原始文件: {full_name}\n"
            f"💾 文件保存: {new_filename}"
        )

    except Exception as e:
        return f"❌ 处理图片时发生未知错误: {str(e)}"