import os
import sys

# --- 1. 技能加载 ---
try:
    from skills.ppt_skill import run_ppt_skill
    from skills.txt_skill import run_txt_skill
    from skills.image_skill import cartoonize_image
except ImportError:
    def run_ppt_skill(f): return f"【模拟】处理 PPT: {f}"
    def run_txt_skill(f): return f"【模拟】处理 TXT: {f}"
    def cartoonize_image(f): return f"【模拟】处理图片: {f}"

# --- 2. 闲聊/咨询接口 ---
def ask_qwen_chat(prompt):
    import requests
    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "qwen2.5:1.5b",
                "prompt": f"你是一个专业的硬件 BU 助手，请回答：{prompt}",
                "stream": False
            },
            timeout=15
        )
        return response.json().get("response", "模型响应超时...")
    except:
        return "❌ 无法连接到本地 Ollama 服务。"

# --- 3. 任务执行逻辑 ---
def fast_work():
    print("\n🚀 [任务模式] 输入文件名 (如 11.txt):")
    fname = input(">> ").strip()
    if not fname or fname.lower() == 'back': return

    ext = fname.lower().split('.')[-1]
    
    # 路径防错逻辑：识别文件夹
    if ext in ['txt', 'pptx']:
        folder = "ppt"
    elif ext in ['jpg', 'png', 'jpeg']:
        folder = "image"
    else:
        print(f"❌ 不支持的格式: {ext}")
        return

    # 核心修复：如果用户输入已经带了 ppt/，就不再拼接
    if fname.startswith(folder):
        target_path = fname
    else:
        target_path = os.path.join(folder, fname)

    print(f"⚡ 正在调用原生技能处理: {target_path}...")
    
    if ext == 'txt':
        result = run_txt_skill(target_path)
    elif ext == 'pptx':
        result = run_ppt_skill(target_path)
    else:
        result = cartoonize_image(target_path)

    print(f"\n{result}")

def chat_loop():
    print("\n💬 [智障陪聊员] 请问有什么需要帮助 (输入 'back' 返回):")
    while True:
        u_input = input("智障机器人 >> ").strip()
        if not u_input or u_input.lower() == 'back': break
        
        print("🤖 思考中...")
        ans = ask_qwen_chat(u_input)
        print(f"\n💡 回复：\n{ans}\n" + "-"*30)

# --- 4. 主菜单 ---
def main():
    while True:
        print("\n" + "="*40)
        print("🛠 智障AI小助手 ")
        print("="*40)
        print("1. 🛠 黑奴模式 ")
        print("2. 💬 人工智障模式 ")
        print("3. 🚪 退出")
        
        choice = input("\n请选择 (1/2/3): ").strip()
        if choice == '1': fast_work()
        elif choice == '2': chat_loop()
        elif choice == '3': break

if __name__ == "__main__":
    main()