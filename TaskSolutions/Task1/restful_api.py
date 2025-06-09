import sys
import os
import json
import requests
import traceback

# 定义配置变量
BASE_URL = "https://api.chatfire.cn/v1"
API_KEY = "sk-zO8exlBicZh7nJeZn5GuC5X9SPuVrZzXoGyOW0i9BFvN62ON"
MODEL_NAME = "gpt-4o"

# 需求建模相关的提示词
REQUIREMENT_PROMPT = """
作为一个需求建模专家，请基于以下ATM系统描述，生成完整的需求模型，包括：
1. 用例图：识别主要参与者和用例，并定义它们之间的关系
2. 系统顺序图：为每个主要用例创建系统顺序图
3. 概念类图：识别系统中的主要类、它们的属性和关系
4. OCL合约：为关键操作提供OCL合约

ATM（自动取款机）系统描述：
ATM系统允许银行客户进行基本的银行交易，如查询账户余额、取款、存款和转账。
客户必须使用银行卡和个人识别码（PIN）登录系统。
系统会验证客户身份，然后显示可用的交易选项。
每次交易后，客户可以选择打印收据。
系统应记录所有交易并维护账户余额。
系统应具有超时功能，如果客户在一定时间内未操作，将自动退出当前会话。
系统应具备错误处理机制，如处理卡被吞、网络故障等异常情况。

请尽可能详细地生成需求模型，确保模型的完整性和准确性。
"""

print(f"BASE_URL: {BASE_URL}")
print(f"MODEL_NAME: {MODEL_NAME}")
print(f"REQUIREMENT_PROMPT的前100个字符: {REQUIREMENT_PROMPT[:100]}...")

def call_openai_api():
    """使用纯Restful API调用OpenAI模型生成需求模型"""
    
    print("正在调用OpenAI API生成需求模型...")
    
    # 设置API请求头
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }
    
    # 设置API请求体
    data = {
        "model": MODEL_NAME,
        "messages": [
            {"role": "system", "content": "你是一个专业的需求建模助手，精通UML和OCL。"},
            {"role": "user", "content": REQUIREMENT_PROMPT}
        ],
        "temperature": 0.7
    }
    
    try:
        # 发送API请求
        print(f"发送请求到: {BASE_URL}/chat/completions")
        response = requests.post(f"{BASE_URL}/chat/completions", headers=headers, json=data)
        print(f"API响应状态码: {response.status_code}")
        response.raise_for_status()
        
        # 解析响应
        result = response.json()
        print("成功解析JSON响应")
        output = result["choices"][0]["message"]["content"]
        
        # 确保目录存在
        output_dir = os.path.dirname(os.path.abspath(__file__))
        output_path = os.path.join(output_dir, "requirement_model_task1.txt")
        print(f"保存结果到: {output_path}")
        
        # 保存结果到文件
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(output)
        
        print(f"需求模型已生成并保存到 {output_path}")
        return output
    
    except requests.exceptions.RequestException as e:
        print(f"API请求错误: {e}")
        traceback.print_exc()
        return None
    except Exception as e:
        print(f"发生未知错误: {e}")
        traceback.print_exc()
        return None

if __name__ == "__main__":
    call_openai_api() 