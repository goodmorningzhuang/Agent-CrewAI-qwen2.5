import json
import os
from datetime import datetime

MEMORY_FILE = "memory.json"

def get_memory():
    """读取记忆，确保包含 file_notes 核心字段"""
    initial_data = {
        "user_preference": {
            "font_name": "微软雅黑",
            "font_size": "12",
            "image_style": "黑白铅笔风",
            "last_processed_file": "无"
        },
        "file_notes": {},  # 关键：必须保留这个字段，否则 Agent 会失忆
        "history": []
    }
    
    if not os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, 'w', encoding='utf-8') as f:
            json.dump(initial_data, f, ensure_ascii=False, indent=4)
        return initial_data
    
    try:
        with open(MEMORY_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            # 自动补全缺失字段，防止 main.py 崩溃
            if "file_notes" not in data or data["file_notes"] is None:
                data["file_notes"] = {}
            if "user_preference" not in data:
                data["user_preference"] = initial_data["user_preference"]
            return data
    except Exception:
        return initial_data

def log_history(task_type, filename, status="Success"):
    """
    记录每一条操作历史，同时保护 file_notes 不被覆盖
    """
    mem = get_memory() # 这里会自动通过修复后的逻辑补全字段
    new_log = {
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "task": task_type,
        "file": filename,
        "status": status
    }
    # 记录并更新最近处理的文件
    mem["user_preference"]["last_processed_file"] = filename
    mem["history"] = ([new_log] + mem["history"])[:50]
    
    with open(MEMORY_FILE, 'w', encoding='utf-8') as f:
        json.dump(mem, f, ensure_ascii=False, indent=4)

def reset_memory():
    """清空记忆，恢复出厂设置"""
    if os.path.exists(MEMORY_FILE):
        os.remove(MEMORY_FILE)
    return "✅ 记忆已重置为出厂设置"

def get_history_summary():
    """获取简单的历史统计"""
    mem = get_memory()
    total = len(mem.get("history", []))
    if total == 0:
        return "目前还没有任何处理记录。"
    last_task = mem["history"][0]
    # 同步显示已存备注的数量
    notes_count = len(mem.get("file_notes", {}))
    return f"总计任务: {total}次 | 档案备注: {notes_count}个 | 最近: {last_task['file']}"