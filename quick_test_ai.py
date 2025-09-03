#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI解读应用快速测试脚本
"""

import requests
import json

def quick_test():
    """快速测试AI解读应用"""
    
    base_url = "http://127.0.0.1:8000/api/ai"
    
    print("🚀 快速测试AI解读应用...")
    print(f"API地址: {base_url}")
    print("-" * 50)
    
    # 测试文本解读
    test_text = "人工智能正在改变我们的世界，从智能手机到自动驾驶汽车，AI技术无处不在。"
    
    data = {
        "text": test_text,
        "prompt_type": "detailed_explanation"
    }
    
    try:
        print(f"发送文本: {test_text}")
        print("正在调用AI解读...")
        
        response = requests.post(
            f"{base_url}/interpret/",
            json=data,
            timeout=60
        )
        
        print(f"响应状态: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            if result['success']:
                print("✅ 解读成功!")
                print(f"模型: {result['data']['model_used']}")
                print(f"原文长度: {result['data']['original_text_length']} 字符")
                print("-" * 30)
                print("解读结果:")
                print(result['data']['interpretation'])
            else:
                print(f"❌ 解读失败: {result.get('error')}")
        else:
            print(f"❌ 请求失败: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ 连接失败! 请先启动Django服务器:")
        print("   ./start_server.sh")
    except Exception as e:
        print(f"❌ 测试错误: {str(e)}")

if __name__ == "__main__":
    quick_test()
