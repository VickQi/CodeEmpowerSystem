#!/usr/bin/env python3
"""
LLM模块测试文件
"""

import sys
import json
import os
from pathlib import Path
from unittest.mock import patch, MagicMock

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def test_mock_mode():
    """测试Mock模式"""
    print("开始测试Mock模式...")
    
    # 保存原始设置
    original_use_mock = os.environ.get('USE_MOCK', '')
    
    # 设置为Mock模式
    os.environ['USE_MOCK'] = 'true'
    
    try:
        # 清除模块缓存并重新导入
        modules_to_clear = [k for k in sys.modules.keys() if k.startswith(('settings', 'llm'))]
        for module in modules_to_clear:
            if module in sys.modules:
                del sys.modules[module]
        
        # 重新导入模块
        from settings import settings
        from llm import LLMInterface
        
        # 创建LLM接口实例
        llm_instance = LLMInterface()
        
        # 验证是否使用Mock模式
        assert llm_instance.use_mock == True, "应该使用Mock模式"
        
        # 测试调用
        messages = [
            {"role": "user", "content": "什么是物流系统？"}
        ]
        
        response = llm_instance.invoke(messages)
        
        # 验证响应是有效的JSON
        response_data = json.loads(response)
        assert "answer" in response_data, "响应应该包含answer字段"
        assert "confidence" in response_data, "响应应该包含confidence字段"
        
        print("✓ Mock模式测试通过")
        
    finally:
        # 恢复原始设置
        if original_use_mock:
            os.environ['USE_MOCK'] = original_use_mock
        elif 'USE_MOCK' in os.environ:
            del os.environ['USE_MOCK']

def test_qwen_mode_initialization():
    """测试Qwen模式初始化"""
    print("\n开始测试Qwen模式初始化...")
    
    # 保存原始设置
    original_use_mock = os.environ.get('USE_MOCK', '')
    original_qwen_api_key = os.environ.get('QWEN_API_KEY', '')
    
    # 设置为Qwen模式但不提供API密钥
    os.environ['USE_MOCK'] = 'false'
    os.environ['QWEN_API_KEY'] = ''
    
    try:
        # 清除模块缓存并重新导入
        modules_to_clear = [k for k in sys.modules.keys() if k.startswith(('settings', 'llm'))]
        for module in modules_to_clear:
            if module in sys.modules:
                del sys.modules[module]
        
        # 重新导入模块
        from settings import settings
        from llm import LLMInterface
        
        print(f"settings.QWEN_API_KEY=<{settings.QWEN_API_KEY}>")
        
        # 创建LLM接口实例
        llm_instance = LLMInterface()
        
        # 验证是否回退到Mock模式
        assert llm_instance.use_mock == True, "没有API密钥时应该回退到Mock模式"
        
        print("✓ Qwen模式初始化测试通过（无API密钥回退）")
        
    finally:
        # 恢复原始设置
        if original_use_mock:
            os.environ['USE_MOCK'] = original_use_mock
        elif 'USE_MOCK' in os.environ:
            del os.environ['USE_MOCK']
            
        if original_qwen_api_key:
            os.environ['QWEN_API_KEY'] = original_qwen_api_key
        elif 'QWEN_API_KEY' in os.environ:
            del os.environ['QWEN_API_KEY']

def test_qwen_invoke():
    """测试Qwen调用"""
    print("\n开始测试Qwen调用...")
    
    # 保存原始设置
    original_use_mock = os.environ.get('USE_MOCK', '')
    original_qwen_api_key = os.environ.get('QWEN_API_KEY', '')
    
    # 设置为Qwen模式并提供API密钥
    os.environ['USE_MOCK'] = 'false'
    test_api_key = 'sk-aa4e12b4623644d5a8486bf55c905dfa'
    os.environ['QWEN_API_KEY'] = test_api_key
    
    try:
        # 清除模块缓存并重新导入
        modules_to_clear = [k for k in sys.modules.keys() if k.startswith(('settings', 'llm'))]
        for module in modules_to_clear:
            if module in sys.modules:
                del sys.modules[module]
        
        # 重新导入模块
        from settings import settings
        from llm import LLMInterface
        
        print(f"settings.QWEN_API_KEY=<{settings.QWEN_API_KEY}>")
        
        # 手动创建模拟客户端
        llm_instance = LLMInterface()
        
        # 验证是否使用Qwen模式
        assert llm_instance.use_mock == False, "应该使用Qwen模式"
        assert llm_instance.client is not None, "应该有客户端实例"
        
        # 替换客户端为模拟客户端
        mock_client = MagicMock()
        mock_completion = MagicMock()
        mock_completion.model_dump_json.return_value = json.dumps({
            "choices": [{
                "message": {
                    "role": "assistant",
                    "content": "这是模拟的Qwen响应"
                }
            }]
        })
        mock_client.chat.completions.create.return_value = mock_completion
        llm_instance.client = mock_client
        
        # 测试调用
        messages = [
            {"role": "user", "content": "什么是物流系统？"}
        ]
        
        response = llm_instance.invoke(messages)
        
        # 验证调用了Qwen API
        mock_client.chat.completions.create.assert_called_once()
        call_args = mock_client.chat.completions.create.call_args
        assert call_args[1]['model'] == "qwen3-next-80b-a3b-thinking"
        assert call_args[1]['messages'] == messages
        
        # 验证响应是有效的JSON
        response_data = json.loads(response)
        assert "choices" in response_data, "响应应该包含choices字段"
        
        print("✓ Qwen调用测试通过")
        
    finally:
        # 恢复原始设置
        if original_use_mock:
            os.environ['USE_MOCK'] = original_use_mock
        elif 'USE_MOCK' in os.environ:
            del os.environ['USE_MOCK']
            
        if original_qwen_api_key:
            os.environ['QWEN_API_KEY'] = original_qwen_api_key
        elif 'QWEN_API_KEY' in os.environ:
            del os.environ['QWEN_API_KEY']

def test_fallback_to_mock_on_error():
    """测试Qwen调用出错时回退到Mock模式"""
    print("\n开始测试Qwen调用出错时回退到Mock模式...")
    
    # 保存原始设置
    original_use_mock = os.environ.get('USE_MOCK', '')
    original_qwen_api_key = os.environ.get('QWEN_API_KEY', '')
    
    # 设置为Qwen模式并提供API密钥
    os.environ['USE_MOCK'] = 'false'
    os.environ['QWEN_API_KEY'] = 'invalid_test_key'
    
    try:
        # 清除模块缓存并重新导入
        modules_to_clear = [k for k in sys.modules.keys() if k.startswith(('settings', 'llm'))]
        for module in modules_to_clear:
            if module in sys.modules:
                del sys.modules[module]
        
        # 重新导入模块
        from settings import settings
        from llm import LLMInterface
        
        # 创建LLM接口实例（会因为API密钥无效而初始化失败，回退到Mock模式）
        llm_instance = LLMInterface()
        
        # 测试调用
        messages = [
            {"role": "user", "content": "什么是物流系统？"}
        ]
        
        response = llm_instance.invoke(messages)
        
        # 验证回退到Mock模式（通过响应结构判断）
        response_data = json.loads(response)
        assert "answer" in response_data, "回退到Mock后应该返回有效响应"
        assert "confidence" in response_data, "回退到Mock后应该返回有效响应"
        
        print("✓ Qwen调用出错回退测试通过")
        
    finally:
        # 恢复原始设置
        if original_use_mock:
            os.environ['USE_MOCK'] = original_use_mock
        elif 'USE_MOCK' in os.environ:
            del os.environ['USE_MOCK']
            
        if original_qwen_api_key:
            os.environ['QWEN_API_KEY'] = original_qwen_api_key
        elif 'QWEN_API_KEY' in os.environ:
            del os.environ['QWEN_API_KEY']

if __name__ == "__main__":
    print("开始测试LLM模块...")
    print("=" * 50)
    
    test_mock_mode()
    test_qwen_mode_initialization()
    test_qwen_invoke()
    test_fallback_to_mock_on_error()
    
    print("\n" + "=" * 50)
    print("所有LLM模块测试通过!")