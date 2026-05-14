import os
import requests
from datetime import datetime

# 路径指向你存放文本的文件夹
TXT_DIR = r"C:\Users\user\Desktop\test-ai\PPT"
OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "qwen2.5:1.5b"

def ask_qwen_for_txt(text):
    """专门为长文本优化的提示词"""
    if not text.strip(): return text
    prompt = f"请将以下文案润色得更专业、更具逻辑感，直接输出润色后的内容：\n\n{text}"
    payload = {"model": MODEL_NAME, "prompt": prompt, "stream": False}
    try:
        response = requests.post(OLLAMA_URL, json=payload, timeout=120)
        return response.json().get('response', '').strip()
    except Exception as e:
        return f"错误: {e}"

def run_txt_skill(filename):
    input_path = os.path.join(TXT_DIR, filename)
    today_str = datetime.now().strftime("%Y%m%d")
    output_path = os.path.join(TXT_DIR, f"优化完成_{today_str}_{filename}")

    if not os.path.exists(input_path):
        print(f"❌ 找不到文本文件: {input_path}")
        return

    print(f"📄 正在读取并优化文本: {filename}...")
    
    with open(input_path, "r", encoding="utf-8") as f:
        content = f.read()

    improved_content = ask_qwen_for_txt(content)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(improved_content)
    
    print(f"✅ 文本优化完成！已保存至: {output_path}")