import os
import requests
from datetime import datetime

def run_txt_skill(file_path):
    # 路径校验
    target = os.path.abspath(file_path)
    print(f"🔍 调试：正在尝试读取路径 -> {target}")

    if not os.path.exists(target):
        return f"❌ 找不到文件：{target}"

    try:
        print(f"📖 正在读取内容...")
        with open(target, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if not content.strip():
            return "⚠️ 文件为空，跳过。"

        # AI 润色步骤日志
        print(f"🤖 正在调用 Ollama (Qwen2.5-1.5B) 进行润色...")
        start_time = datetime.now()
        
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "qwen2.5:1.5b",
                "prompt": f"请优化以下硬件文案：\n\n{content}",
                "stream": False
            },
            timeout=30
        )
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        print(f"⏳ AI 处理耗时: {duration:.2f} 秒")

        refined_text = response.json().get("response", "AI 响应异常")

        # 自动带时间戳保存
        time_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_dir = os.path.dirname(target)
        base_name = os.path.basename(target)
        name_part, ext_part = os.path.splitext(base_name)
        new_path = os.path.join(file_dir, f"{name_part}_{time_str}{ext_part}")

        with open(new_path, 'w', encoding='utf-8') as f:
            f.write(refined_text)

        return f"✅ 任务完成！\n💾 原始文件: {base_name}\n💾 优化文件: {os.path.basename(new_path)}"

    except Exception as e:
        return f"❌ 运行错误: {str(e)}"