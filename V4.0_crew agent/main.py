import os
import re
import time
import requests
from datetime import datetime

# 终端颜色代码配置
BLUE = '\033[94m'
GREEN = '\033[92m'
YELLOW = '\033[93m'
CYAN = '\033[96m'
RESET = '\033[0m'
BOLD = '\033[1m'

# 本地大模型配置
OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "qwen2.5:1.5b"

# 动态加载你的现有技能 (保持不动)
try:
    from skills.ppt_skill import run_ppt_skill
    from skills.image_skill import cartoonize_image
    from skills.txt_skill import run_txt_skill
except ImportError:
    # 防止因缺少文件导致主程序无法启动
    def run_ppt_skill(path): pass
    def cartoonize_image(path): pass
    def run_txt_skill(path): pass

def print_banner():
    """打造具有工业科技感的中文启动界面"""
    os.system('cls' if os.name == 'nt' else 'clear')
    print(f"{BLUE}╔════════════════════════════════════════════════════════════╗{RESET}")
    print(f"{BLUE}║{RESET} {BOLD}{CYAN}      🚀     智障机器人 2.0 (多任务RAP版)     {RESET} {BLUE}            ║{RESET}")
    print(f"{BLUE}╠════════════════════════════════════════════════════════════╣{RESET}")
    print(f"{BLUE}║{RESET}  {GREEN} ● 系统状态: 运行中{RESET}        {YELLOW}⚡ 核心引擎: qwen2.5:1.5b{RESET}  {BLUE}    ║{RESET}")
    print(f"{BLUE}║{RESET}  {CYAN}📅 当前日期: {datetime.now().strftime('%Y-%m-%d')}{RESET}    {CYAN}🕒 当前时间: {datetime.now().strftime('%H:%M:%S')}{RESET}    {BLUE}      ║{RESET}")
    print(f"{BLUE}╚════════════════════════════════════════════════════════════╝{RESET}")
    print(f"{BOLD}💡 提示：直接对话或者输入包含 .pptx / .txt / .jpeg 的指令即可触发自动处理 3 退出{RESET}\n")

def add_timestamp_to_result(folder):
    """
    统一后缀处理：在指定文件夹中寻找最新生成的文件并加上时间戳
    """
    time.sleep(1.5)  # 等待 Skill 文件写入完成
    now_str = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # 获取文件夹内所有文件
    files = [os.path.join(folder, f) for f in os.listdir(folder) if os.path.isfile(os.path.join(folder, f))]
    if not files: return None
    
    # 找到最近修改的文件
    latest_file = max(files, key=os.path.getmtime)
    
    # 检查是否为刚刚生成的（5秒内），且避免重复重命名
    if time.time() - os.path.getmtime(latest_file) < 5:
        file_dir, full_name = os.path.split(latest_file)
        if "_T_" in full_name: return full_name 
        
        name_part, ext_part = os.path.splitext(full_name)
        new_name = f"{name_part}_T_{now_str}{ext_part}"
        new_path = os.path.join(file_dir, new_name)
        os.rename(latest_file, new_path)
        return os.path.basename(new_path)
    return None

def chat_with_ai(user_input):
    """闲聊模式"""
    print(f"\n{CYAN}🤖 智障机器人思考中...{RESET}")
    try:
        response = requests.post(OLLAMA_URL, json={
            "model": MODEL_NAME,
            "prompt": f"你是一个硬件自动化专家，用户说：{user_input}",
            "stream": False
        }, timeout=20)
        print(f"\n💡 智障机器人：{response.json().get('response')}")
    except:
        print(f"\n{YELLOW}⚠️  无法连接本地 AI 引擎。{RESET}")

def main():
    print_banner()
    while True:
        # 中文输入提示符
        u_in = input(f"{BOLD}{BLUE}➜ {RESET} {BOLD}请问有什么需要帮助:{RESET} ").strip()
        
        if u_in.lower() in ['3', '退出', 'exit', 'quit']:
            print(f"\n{YELLOW}⚙️  系统正在关闭... 祝工作顺利！{RESET}")
            break
        if not u_in: continue

        # 正则提取所有包含后缀的文件名
        full_filenames = re.findall(r'[a-zA-Z0-9_\-]+\.(?:pptx|txt|jpeg|jpg|png)', u_in)

        if full_filenames:
            print(f"\n{GREEN}⚙️  接收到任务:{RESET} 检测到 {len(full_filenames)} 个处理目标。")
            print(f"{BLUE}—{RESET}" * 45)
            
            for filename in full_filenames:
                ext = filename.lower().split('.')[-1]
                
                # 自动分配文件夹
                if ext in ['pptx', 'txt']:
                    folder = "ppt"
                else:
                    folder = "image"
                
                target_path = os.path.join(folder, filename)
                print(f"{YELLOW}▶ 正在处理:{RESET} {filename} ...", end="\r")

                # 调用 Skill (保持你现在的参数传递方式)
                try:
                    if ext == 'pptx':
                        run_ppt_skill(target_path)
                    elif ext == 'txt':
                        run_txt_skill(target_path)
                    elif ext in ['jpeg', 'jpg', 'png']:
                        cartoonize_image(target_path)
                    
                    # 运行完立刻检查文件夹，给生成物盖上时间戳
                    final_name = add_timestamp_to_result(folder)
                    if final_name:
                        print(f"{GREEN}✔ 执行成功:{RESET} {filename} -> [{final_name}]")
                    else:
                        print(f"{YELLOW}⚠ 处理完成，但未检测到新文件生成。{RESET}")
                except Exception as e:
                    print(f"{YELLOW}❌ 处理异常: {filename} ({str(e)}){RESET}")
            
            print(f"{BLUE}—{RESET}" * 45)
            print(f"{GREEN}✨ 队列中的所有任务已处理完毕。{RESET}")
        else:
            # 没检测到文件名后缀，进入闲聊模式
            chat_with_ai(u_in)
            print(f"{BLUE}—{RESET}" * 45)

if __name__ == "__main__":
    main()