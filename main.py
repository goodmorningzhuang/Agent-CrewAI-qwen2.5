import os
import re
import time
import json
import requests
from datetime import datetime

# ================= 颜色配置 =================
BLUE = '\033[94m'
GREEN = '\033[92m'
YELLOW = '\033[93m'
CYAN = '\033[96m'
RESET = '\033[0m'
WHITE = '\033[97m'  
BOLD = '\033[1m'

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "qwen2.5:1.5b"
MEMORY_FILE = "memory.json"

# ================= 深度记忆模块 =================
def load_memory():
    initial = {
        "user_preference": {"font_name": "微软雅黑", "font_size": "12", "image_style": "铅笔风"},
        "file_notes": {}, 
        "last_processed_file": "无",
        "chat_history": [] 
    }
    if not os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, 'w', encoding='utf-8') as f:
            json.dump(initial, f, ensure_ascii=False, indent=4)
        return initial
    try:
        with open(MEMORY_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            for key in initial:
                if key not in data or data[key] is None:
                    data[key] = initial[key]
            return data
    except Exception:
        return initial

def save_memory(data):
    with open(MEMORY_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# ================= 技能加载 =================
try:
    from skills.ppt_skill import run_ppt_skill
    from skills.image_skill import cartoonize_image
    from skills.txt_skill import run_txt_skill
except ImportError:
    def run_ppt_skill(p, **k): return "❌ 缺失 PPT Skill"
    def cartoonize_image(p, **k): return "❌ 缺失 Image Skill"
    def run_txt_skill(p, **k): return "❌ 缺失 TXT Skill"

# ================= 核心逻辑 =================
def print_banner(mem):
    """在 Banner 中直接展示输入提示和系统时间"""
    pref = mem.get("user_preference", {})
    notes_count = len(mem.get('file_notes') or {})
    
    # 获取时间
    now = datetime.now()
    time_str = now.strftime("%Y-%m-%d %H:%M")
    
    print(f"{BLUE}╔════════════════════════════════════════════════════════════════════════════════════════════════════════════{RESET}")
    print(f"{BLUE}║{RESET} {BOLD}{CYAN}🚀 智障机器人 3.0 （长记忆版） {RESET} {' ' * 20} {YELLOW}🕒 {time_str}{RESET} {BLUE}{RESET}")
    print(f"{BLUE}╠════════════════════════════════════════════════════════════════════════════════════════════════════════════{RESET}")
    print(f"{BLUE}║{RESET} {CYAN}⚙️  偏好: {pref.get('font_size')}pt/{pref.get('font_name')}{RESET} {' ' * 10} {CYAN}📝 档案: {notes_count}个{RESET} {' ' * 15} {BLUE}{RESET}")
    print(f"{BLUE}╟────────────────────────────────────────────────────────────────────────────────────────────────────────────{RESET}")
    print(f"{BLUE}║{RESET} {BOLD}👉 输入提示：{RESET} {' ' * 68} {BLUE}{RESET}")
    print(f"{BLUE}║{RESET}    • {WHITE if 'WHITE' in globals() else ''}处理文件：直接输入文件名 (如: test.pptx 或 1.png){RESET} {' ' * 23} {BLUE}{RESET}")
    print(f"{BLUE}║{RESET}    • {WHITE if 'WHITE' in globals() else ''}普通对话：直接输入想说的话 (已启用长记忆){RESET} {' ' * 27} {BLUE}{RESET}")
    print(f"{BLUE}║{RESET}    • {WHITE if 'WHITE' in globals() else ''}退出程序：输入 '退出' 或 'exit'{RESET} {' ' * 38} {BLUE}{RESET}")
    print(f"{BLUE}╚════════════════════════════════════════════════════════════════════════════════════════════════════════════{RESET}")

def chat_logic(u_in, mem):
    print(f"{CYAN}🤖 思考中...{RESET}", end="\r")
    
    now = datetime.now()
    prompt = f"""你是有长记忆的硬件助手。一律用中文详细回答。
当前时间：{now.strftime('%Y-%m-%d %H:%M:%S')}
已存备注: {mem.get('file_notes')}
近期对话: {mem.get('chat_history')[-6:]}

用户说: '{u_in}'
请详细回答："""
    
    try:
        res = requests.post(OLLAMA_URL, json={"model": MODEL_NAME, "prompt": prompt, "stream": False}, timeout=20)
        reply = res.json().get('response', '').strip()
        
        mem["chat_history"].append({"role": "user", "content": u_in})
        mem["chat_history"].append({"role": "assistant", "content": reply.split('[')[0].strip()})
        if len(mem["chat_history"]) > 20: mem["chat_history"] = mem["chat_history"][-20:]
        
        # 提取暗号
        if "[NOTE:" in reply:
            match = re.search(r'\[NOTE:(.*?)=(.*?)\]', reply)
            if match:
                fname, note = match.groups()
                mem["file_notes"][fname] = note
                print(f"{GREEN}[系统：已更新档案 {fname}]{RESET}")
        
        save_memory(mem)
        print(f"\n{BOLD}💡 AI：{RESET}{reply.split('[')[0].strip()}")
    except Exception as e:
        print(f"\n{YELLOW}⚠️ 连接异常: {e}{RESET}")

def main():
    memory = load_memory()
    os.system('cls' if os.name == 'nt' else 'clear')
    print_banner(memory)
    
    while True:
        u_in = input(f"\n{BOLD}{BLUE}➜ {RESET} ").strip()
        
        if u_in.lower() in ['3', '退出', 'exit']:
            print(f"{YELLOW}再见！See you next time！{RESET}")
            break
        if not u_in: continue

        files = re.findall(r'[a-zA-Z0-9_\-]+\.(?:pptx|txt|jpeg|jpg|png)', u_in)

        if files:
            for fname in files:
                ext = fname.lower().split('.')[-1]
                folder = "ppt" if ext in ['pptx', 'txt'] else "image"
                path = os.path.join(folder, fname)
                file_note = memory["file_notes"].get(fname, "无特定要求")
                try:
                    if ext == 'pptx':
                        result = run_ppt_skill(path, font_size=memory["user_preference"]["font_size"], note=file_note)
                    elif ext == 'txt':
                        result = run_txt_skill(path, note=file_note)
                    elif ext in ['jpeg', 'jpg', 'png']:
                        result = cartoonize_image(path, style=memory["user_preference"].get("image_style"))
                    print(f"{GREEN}✔ {result}{RESET}")
                    save_memory(memory)
                except Exception as e:
                    print(f"{YELLOW}❌ 失败: {fname} ({e}){RESET}")
        else:
            chat_logic(u_in, memory)

if __name__ == "__main__":
    main()