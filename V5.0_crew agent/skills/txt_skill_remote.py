import os
import requests
from datetime import datetime


def run_txt_skill(file_path, *args, **kwargs):
    """
    AI增强版 TXT 处理：使用外部大模型进行硬件专家级文案润色、完善和补充
    """
    target = os.path.abspath(file_path)
    if not os.path.exists(target):
        return f"❌ 找不到 TXT 文件: {target}"

    # 提取参数
    file_note = kwargs.get('note', '无特定要求')
    api_base = kwargs.get('api_base', '')
    api_key = kwargs.get('api_key', '')
    model_name = kwargs.get('model_name', '')

    if not api_base or not api_key or not model_name:
        return "❌ 缺少外部 API 配置，无法使用 AI 增强模式"

    try:
        # 读取原始文案
        with open(target, 'r', encoding='utf-8') as f:
            content = f.read()

        print(f"⚡ 启动 AI 增强版硬件专家文案润色引擎...")
        print(f"📖 调取档案记忆：备注={file_note}")
        print(f"🤖 使用模型: {model_name}")

        prompt = f"""你是一位资深的硬件工程专家，精通硬件设计、自动化测试、信号完整性、EMC/EMI、热设计及系统集成。
请对以下文案进行**深度润色、完善和专业补充**。

【特定备注要求】：{file_note}

严格准则：
1. 以硬件专家的视角，对文案内容进行详尽优化和专业化改写。
2. 使用工业级专业术语（如：将"做得好"改为"性能指标达标率 99.8%"，"测试通过"改为"验证测试全部通过，符合设计规格"）。
3. 对原文信息进行合理补充：添加技术参数、性能指标、测试方法、行业标准等专业内容。
4. 结构化表达，逻辑清晰，段落分明。
5. 保持技术参数的准确性，不要编造具体数据。
6. 直接输出润色后的完整文案，不要任何开场白、结尾语或标注。

待润色文案内容：
{content}

专业润色、完善和补充后的文案："""

        url = f"{api_base}/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": model_name,
            "messages": [{"role": "user", "content": prompt}],
            "stream": False,
            "max_tokens": 1024
        }

        response = requests.post(url, json=payload, headers=headers, timeout=60)
        if response.status_code != 200:
            return f"❌ API 请求失败（状态码 {response.status_code}），原文未修改保存"

        refined_text = response.json()["choices"][0]["message"]["content"].strip()

        if not refined_text:
            refined_text = content

        # 生成带时间戳的文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_dir, full_name = os.path.split(target)
        name_part, ext_part = os.path.splitext(full_name)

        new_filename = f"{name_part}_AI_专家润色_{timestamp}{ext_part}"
        save_path = os.path.join(file_dir, new_filename)

        with open(save_path, 'w', encoding='utf-8') as f:
            f.write(refined_text)

        # 统计信息
        original_len = len(content)
        refined_len = len(refined_text)
        diff = refined_len - original_len

        return f"✅ AI增强版文本润色完成！\n📂 档案备注应用: {file_note}\n📈 字数变化: {original_len} → {refined_len} ({'+' if diff >= 0 else ''}{diff}字)\n💾 已保存为: {new_filename}"

    except Exception as e:
        return f"❌ AI增强版 TXT 处理异常: {str(e)}"