"""
测试外部模型 API 连接脚本
"""
import os
import requests
from dotenv import load_dotenv

# 加载 .env 文件
load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

# 从 .env 读取配置
API_KEY = os.getenv("OPENAI_API_KEY")
API_BASE = os.getenv("OPENAI_API_BASE")
MODEL = os.getenv("MODEL_NAME")

print(f"📋 配置信息:")
print(f"   API Base:  {API_BASE}")
print(f"   Model:     {MODEL}")
print(f"   API Key:   {API_KEY[:10]}...{API_KEY[-4:]}" if API_KEY and len(API_KEY) > 14 else f"   API Key:   {API_KEY}")
print()

# 构造 OpenAI 兼容的请求
url = f"{API_BASE}/chat/completions"
headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}
payload = {
    "model": MODEL,
    "messages": [
        {"role": "user", "content": "你好，请用中文简短回复一句话，确认你能正常工作。"}
    ],
    "stream": False,
    "max_tokens": 100
}

print(f"🔗 正在连接: {url}")
print(f"📡 发送请求中...\n")

try:
    response = requests.post(url, json=payload, headers=headers, timeout=30)
    print(f"📊 HTTP 状态码: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        reply = result["choices"][0]["message"]["content"]
        print(f"✅ 连接成功！模型回复:")
        print(f"   💬 {reply}")
        
        # 显示用量信息
        usage = result.get("usage", {})
        if usage:
            print(f"\n📈 Token 用量:")
            print(f"   输入: {usage.get('prompt_tokens', 'N/A')}")
            print(f"   输出: {usage.get('completion_tokens', 'N/A')}")
            print(f"   总计: {usage.get('total_tokens', 'N/A')}")
    else:
        print(f"❌ 请求失败！")
        print(f"   响应内容: {response.text}")

except requests.exceptions.Timeout:
    print("❌ 请求超时（30秒），请检查网络连接或 API 地址。")
except requests.exceptions.ConnectionError as e:
    print(f"❌ 连接失败，无法访问 API 地址。")
    print(f"   错误详情: {e}")
except Exception as e:
    print(f"❌ 发生未知错误: {e}")