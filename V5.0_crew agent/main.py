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

# ================= 本地模型配置（选项1） =================
OLLAMA_URL = "http://localhost:11434/api/generate"
LOCAL_MODEL_NAME = "qwen2.5:1.5b"

# ================= 外部API模型配置（选项2） =================
OPENAI_API_KEY = None
OPENAI_API_BASE = None
REMOTE_MODEL_NAME = None

MEMORY_FILE = "memory.json"

# ================= 加载外部API配置 =================
def load_remote_config():
    """从 .env 文件加载外部 API 配置"""
    global OPENAI_API_KEY, OPENAI_API_BASE, REMOTE_MODEL_NAME
    env_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env')
    if not os.path.exists(env_file):
        return False
    try:
        with open(env_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                if '=' in line:
                    key, value = line.split('=', 1)
                    key, value = key.strip(), value.strip()
                    if key == 'OPENAI_API_KEY':
                        OPENAI_API_KEY = value
                    elif key == 'OPENAI_API_BASE':
                        OPENAI_API_BASE = value
                    elif key == 'MODEL_NAME':
                        REMOTE_MODEL_NAME = value
        if OPENAI_API_KEY and OPENAI_API_BASE and REMOTE_MODEL_NAME:
            return True
        return False
    except Exception:
        return False

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

# ================= 技能加载（本地模式） =================
try:
    from skills.ppt_skill import run_ppt_skill as local_ppt_skill
    from skills.image_skill import cartoonize_image
    from skills.txt_skill import run_txt_skill as local_txt_skill
except ImportError:
    def local_ppt_skill(p, **k): return "❌ 缺失 PPT Skill"
    def cartoonize_image(p, **k): return "❌ 缺失 Image Skill"
    def local_txt_skill(p, **k): return "❌ 缺失 TXT Skill"

# ================= 技能加载（外部API增强模式） =================
try:
    from skills.ppt_skill_remote import run_ppt_skill as remote_ppt_skill
    from skills.txt_skill_remote import run_txt_skill as remote_txt_skill
except ImportError:
    def remote_ppt_skill(p, **k): return "❌ 缺失 Remote PPT/TXT Skill"
    def remote_txt_skill(p, **k): return "❌ 缺失 Remote TXT Skill"

# ================= 核心逻辑 =================
def print_banner(mem, mode_label):
    """在 Banner 中直接展示输入提示和系统时间"""
    pref = mem.get("user_preference", {})
    notes_count = len(mem.get('file_notes') or {})
    
    # 获取时间
    now = datetime.now()
    time_str = now.strftime("%Y-%m-%d %H:%M")
    
    print(f"{BLUE}╔════════════════════════════════════════════════════════════════════════════════════════════════════════════{RESET}")
    print(f"{BLUE}║{RESET} {BOLD}{CYAN}🚀 智障机器人 3.0 （长记忆版） {RESET} {' ' * 20} {YELLOW}🕒 {time_str}{RESET} {BLUE}{RESET}")
    print(f"{BLUE}╠════════════════════════════════════════════════════════════════════════════════════════════════════════════{RESET}")
    print(f"{BLUE}║{RESET} {CYAN}⚙️  偏好: {pref.get('font_size')}pt/{pref.get('font_name')}{RESET} {' ' * 10} {CYAN}📝 档案: {notes_count}个{RESET} {' ' * 5} {YELLOW}🔌 模式: {mode_label}{RESET} {BLUE}{RESET}")
    print(f"{BLUE}╟────────────────────────────────────────────────────────────────────────────────────────────────────────────{RESET}")
    print(f"{BLUE}║{RESET} {BOLD}👉 输入提示：{RESET} {' ' * 68} {BLUE}{RESET}")
    print(f"{BLUE}║{RESET}    • {WHITE}处理文件：直接输入文件名 (如: test.pptx 或 1.png){RESET} {' ' * 23} {BLUE}{RESET}")
    print(f"{BLUE}║{RESET}    • {WHITE}普通对话：直接输入想说的话 (已启用长记忆){RESET} {' ' * 27} {BLUE}{RESET}")
    print(f"{BLUE}║{RESET}    • {WHITE}退出程序：输入 '退出' 或 'exit'{RESET} {' ' * 38} {BLUE}{RESET}")
    print(f"{BLUE}╚════════════════════════════════════════════════════════════════════════════════════════════════════════════{RESET}")

# ================= 本地模型聊天 =================
def chat_logic_local(u_in, mem):
    """使用本地 Ollama 模型进行聊天"""
    print(f"{CYAN}🤖 思考中...{RESET}", end="\r")
    
    now = datetime.now()
    prompt = f"""你是有长记忆的硬件助手。一律用中文详细回答。
当前时间：{now.strftime('%Y-%m-%d %H:%M:%S')}
已存备注: {mem.get('file_notes')}
近期对话: {mem.get('chat_history')[-6:]}

用户说: '{u_in}'
请详细回答："""
    
    try:
        res = requests.post(OLLAMA_URL, json={"model": LOCAL_MODEL_NAME, "prompt": prompt, "stream": False}, timeout=20)
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

# ================= 外部API模型聊天 =================
def chat_logic_remote(u_in, mem):
    """使用外部 API 模型进行聊天（OpenAI 兼容接口）"""
    print(f"{CYAN}🤖 思考中...{RESET}", end="\r")
    
    now = datetime.now()
    system_prompt = f"""你是有长记忆的硬件助手。一律用中文详细回答。
当前时间：{now.strftime('%Y-%m-%d %H:%M:%S')}
已存备注: {mem.get('file_notes')}
近期对话: {mem.get('chat_history')[-6:]}"""
    
    # 构造 OpenAI 兼容的消息列表
    messages = [{"role": "system", "content": system_prompt}]
    for msg in mem.get('chat_history', [])[-6:]:
        messages.append(msg)
    messages.append({"role": "user", "content": u_in})
    
    url = f"{OPENAI_API_BASE}/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": REMOTE_MODEL_NAME,
        "messages": messages,
        "stream": False,
        "max_tokens": 512
    }
    
    try:
        res = requests.post(url, json=payload, headers=headers, timeout=30)
        res.raise_for_status()
        result = res.json()
        reply = result["choices"][0]["message"]["content"].strip()
        
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
    except requests.exceptions.RequestException as e:
        print(f"\n{YELLOW}⚠️ API 请求异常: {e}{RESET}")
    except Exception as e:
        print(f"\n{YELLOW}⚠️ 连接异常: {e}{RESET}")

# ================= 文件处理（本地模式） =================
def process_files_local(files, memory):
    """使用本地模型处理文件"""
    for fname in files:
        ext = fname.lower().split('.')[-1]
        folder = "ppt" if ext in ['pptx', 'txt'] else "image"
        path = os.path.join(folder, fname)
        file_note = memory["file_notes"].get(fname, "无特定要求")
        try:
            if ext == 'pptx':
                result = local_ppt_skill(path, font_size=memory["user_preference"]["font_size"], note=file_note)
            elif ext == 'txt':
                result = local_txt_skill(path, note=file_note)
            elif ext in ['jpeg', 'jpg', 'png']:
                result = cartoonize_image(path, style=memory["user_preference"].get("image_style"))
            print(f"{GREEN}✔ {result}{RESET}")
            save_memory(memory)
        except Exception as e:
            print(f"{YELLOW}❌ 失败: {fname} ({e}){RESET}")

# ================= 文件处理（外部API增强模式） =================
def process_files_remote(files, memory):
    """使用外部大模型进行硬件专家级文件处理"""
    for fname in files:
        ext = fname.lower().split('.')[-1]
        folder = "ppt" if ext in ['pptx', 'txt'] else "image"
        path = os.path.join(folder, fname)
        file_note = memory["file_notes"].get(fname, "无特定要求")
        try:
            if ext == 'pptx':
                result = remote_ppt_skill(
                    path,
                    font_size=memory["user_preference"]["font_size"],
                    note=file_note,
                    api_base=OPENAI_API_BASE,
                    api_key=OPENAI_API_KEY,
                    model_name=REMOTE_MODEL_NAME
                )
            elif ext == 'txt':
                result = remote_txt_skill(
                    path,
                    note=file_note,
                    api_base=OPENAI_API_BASE,
                    api_key=OPENAI_API_KEY,
                    model_name=REMOTE_MODEL_NAME
                )
            elif ext in ['jpeg', 'jpg', 'png']:
                result = cartoonize_image(path, style=memory["user_preference"].get("image_style"))
            print(f"{GREEN}✔ {result}{RESET}")
            save_memory(memory)
        except Exception as e:
            print(f"{YELLOW}❌ 失败: {fname} ({e}){RESET}")

# ================= 模式选择菜单 =================
def select_mode():
    """启动时选择模式"""
    has_remote = load_remote_config()
    
    print(f"\n{BOLD}{BLUE}╔═════════════════════════════════════════════════════════════════════════════════{RESET}")
    print(f"{BLUE}║{RESET}  {BOLD}{CYAN}🚀 智障机器人 3.0 — 选择运行模式{RESET}                            {BLUE}{RESET}")
    print(f"{BLUE}╠═════════════════════════════════════════════════════════════════════════════════{RESET}")
    print(f"{BLUE}║{RESET}                                                              {BLUE}{RESET}")
    print(f"{BLUE}║{RESET}    {BOLD}1{RESET} {WHITE}— 本地模型 (Ollama: {LOCAL_MODEL_NAME}){RESET}                    {BLUE}{RESET}")
    if has_remote:
        # 隐藏 API Key 中间部分显示
        masked_key = OPENAI_API_KEY[:10] + "..." + OPENAI_API_KEY[-4:] if OPENAI_API_KEY and len(OPENAI_API_KEY) > 14 else OPENAI_API_KEY
        print(f"{BLUE}║{RESET}    {BOLD}2{RESET} {WHITE}— 外部大模型 ({REMOTE_MODEL_NAME}){RESET}                {BLUE}{RESET}")
        print(f"{BLUE}║{RESET}       {YELLOW}📡 API: {OPENAI_API_BASE}{RESET}  {BLUE}{RESET}")
    else:
        print(f"{BLUE}║{RESET}    {BOLD}2{RESET} {YELLOW}— 外部大模型 {RESET}{YELLOW}(⚠ .env 配置未找到或不完整){RESET}              {BLUE}{RESET}")
    print(f"{BLUE}║{RESET}                                                              {BLUE}{RESET}")
    print(f"{BLUE}║{RESET}    {BOLD}3{RESET} {WHITE}— 退出程序{RESET}                                           {BLUE}{RESET}")
    print(f"{BLUE}║{RESET}                                                              {BLUE}{RESET}")
    print(f"{BLUE}╚═════════════════════════════════════════════════════════════════════════════════{RESET}")
    
    while True:
        choice = input(f"\n{BOLD}{BLUE}➜ 请选择模式 (1/2/3): {RESET}").strip()
        if choice == '1':
            return 'local'
        elif choice == '2':
            if not has_remote:
                print(f"{YELLOW}⚠️ 外部模型配置未就绪，请检查 .env 文件！{RESET}")
                continue
            # 测试外部API连接
            print(f"{CYAN}🔗 正在测试外部API连接...{RESET}", end="\r")
            try:
                test_url = f"{OPENAI_API_BASE}/chat/completions"
                test_headers = {
                    "Authorization": f"Bearer {OPENAI_API_KEY}",
                    "Content-Type": "application/json"
                }
                test_payload = {
                    "model": REMOTE_MODEL_NAME,
                    "messages": [{"role": "user", "content": "你好"}],
                    "stream": False,
                    "max_tokens": 20
                }
                res = requests.post(test_url, json=test_payload, headers=test_headers, timeout=15)
                if res.status_code == 200:
                    print(f"{GREEN}✔ 外部API连接成功！{RESET}")
                    return 'remote'
                else:
                    print(f"{YELLOW}⚠️ API返回状态码 {res.status_code}，请检查配置！{RESET}")
            except Exception as e:
                print(f"{YELLOW}⚠️ 连接外部API失败: {e}{RESET}")
        elif choice == '3':
            return 'exit'
        else:
            print(f"{YELLOW}请输入 1、2 或 3{RESET}")

# ================= 运行主循环 =================
def run_loop(memory, mode):
    """主交互循环"""
    mode_label = f"本地模型 ({LOCAL_MODEL_NAME})" if mode == 'local' else f"外部模型 ({REMOTE_MODEL_NAME})"
    os.system('cls' if os.name == 'nt' else 'clear')
    print_banner(memory, mode_label)
    
    # 选择聊天函数和文件处理函数
    if mode == 'local':
        chat_fn = chat_logic_local
        file_fn = process_files_local
    else:
        chat_fn = chat_logic_remote
        file_fn = process_files_remote
    
    while True:
        u_in = input(f"\n{BOLD}{BLUE}➜ {RESET} ").strip()
        
        if u_in.lower() in ['3', '退出', 'exit']:
            print(f"{YELLOW}再见！See you next time！{RESET}")
            break
        if not u_in: continue

        files = re.findall(r'[a-zA-Z0-9_\-]+\.(?:pptx|txt|jpeg|jpg|png)', u_in)

        if files:
            file_fn(files, memory)
        else:
            chat_fn(u_in, memory)

# ================= 入口 =================
if __name__ == "__main__":
    memory = load_memory()
    
    while True:
        mode = select_mode()
        
        if mode == 'exit':
            print(f"{YELLOW}再见！See you next time！{RESET}")
            break
        
        run_loop(memory, mode)
        
        # 循环结束后询问是否重新选择模式
        print(f"\n{CYAN}🔄 返回模式选择？(y/退出){RESET}")
        again = input(f"{BOLD}{BLUE}➜ {RESET}").strip()
        if again.lower() not in ['y', 'yes', '是', '']:
            print(f"{YELLOW}再见！See you next time！{RESET}")
            break
        os.system('cls' if os.name == 'nt' else 'clear')