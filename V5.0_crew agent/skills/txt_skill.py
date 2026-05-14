import os
import requests
from datetime import datetime

# 本地模型配置
OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "qwen2.5:1.5b"

def run_txt_skill(file_path, *args, **kwargs):
    """
    接收 TXT 文件路径，并结合【长记忆备注】进行硬件专家级润色。
    """
    # 1. 路径精准化
    target = os.path.abspath(file_path)
    if not os.path.exists(target):
        return f"❌ 找不到 TXT 文件: {target}"

    # 2. 提取长记忆备注 (来自 Agent 3.0 的 file_notes)
    file_note = kwargs.get('note', '无特定要求')
    print(f"📖 调取长记忆档案进行润色: {file_note}")

    try:
        # 读取原始文案
        with open(target, 'r', encoding='utf-8') as f:
            content = f.read()

        print(f"⚡ 正在启动硬件专家文案润色引擎...")
        
        # --- 核心改进：将长记忆 note 注入 Prompt ---
        prompt = f"""
        你是一个精通硬件业务和自动化测试的技术专家。
        请根据以下【特定备注要求】对文案进行深度润色。
        
        【特定备注要求】：{file_note}
        
        通用准则：
        1. 使用工业级词汇（例如：将"做得很好"改为"性能指标达标"）。
        2. 结构化表达，去除废话。
        3. 保持技术参数的准确性。
        4. 直接给出润色后的文案，不要任何开场白。

        待处理文案内容：
        {content}
        
        润色结果：
        """
        
        # 请求本地模型
        response = requests.post(
            OLLAMA_URL,
            json={"model": MODEL_NAME, "prompt": prompt, "stream": False},
            timeout=30
        )
        refined_text = response.json().get("response", "").strip()

        # --- 生成带时间戳的文件名 ---
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_dir, full_name = os.path.split(target)
        name_part, ext_part = os.path.splitext(full_name)
        
        new_filename = f"{name_part}_专家润色_{timestamp}{ext_part}"
        save_path = os.path.join(file_dir, new_filename)

        # 写入结果
        with open(save_path, 'w', encoding='utf-8') as f:
            f.write(refined_text)
            
        return f"✅ 文本润色成功！\n档案备注应用: {file_note}\n💾 已保存为: {new_filename}"

    except Exception as e:
        return f"❌ TXT 处理发生异常: {str(e)}"