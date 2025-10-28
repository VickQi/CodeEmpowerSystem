#!/usr/bin/env python3
"""
Embedder模块测试文件
"""

import sys
import os
from pathlib import Path
from unittest.mock import Mock, patch

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from embedder import MockEmbeddings, QwenEmbedder
from settings import settings

def test_mock_embeddings():
    """测试MockEmbeddings类"""
    print("测试MockEmbeddings类...")
    
    # 创建MockEmbeddings实例
    mock_embedder = MockEmbeddings()
    
    # 检查维度属性
    assert mock_embedder.dimension == 1536
    print("✓ 维度属性正确")
    
    # 测试embed方法
    text = "测试文本"
    embedding = mock_embedder.embed(text)
    
    # 检查返回值类型和长度
    assert isinstance(embedding, list)
    assert len(embedding) == 1536
    assert all(isinstance(x, float) for x in embedding)
    assert all(x == 0.0 for x in embedding)
    print("✓ embed方法返回正确的向量")
    
    print("MockEmbeddings类测试通过")

def test_qwen_embedder_initialization():
    """测试QwenEmbedder初始化"""
    print("测试QwenEmbedder初始化...")
    
    # 测试使用默认API密钥初始化
    with patch('embedder.settings') as mock_settings:
        mock_settings.QWEN_API_KEY = "test_api_key"
        mock_settings.USE_MOCK = False
        
        # 模拟OpenAI导入
        with patch('embedder.OpenAI') as mock_openai:
            mock_client = Mock()
            mock_openai.return_value = mock_client
            
            qwen_embedder = QwenEmbedder()
            
            # 检查属性
            assert qwen_embedder.api_key == "test_api_key"
            assert qwen_embedder.client == mock_client
            assert qwen_embedder.dimension == 1536
            print("✓ 使用默认API密钥初始化成功")
    
    # 测试使用自定义API密钥初始化
    with patch('embedder.OpenAI') as mock_openai:
        mock_client = Mock()
        mock_openai.return_value = mock_client
        
        qwen_embedder = QwenEmbedder("custom_api_key")
        
        # 检查属性
        assert qwen_embedder.api_key == "custom_api_key"
        assert qwen_embedder.client == mock_client
        assert qwen_embedder.dimension == 1536
        print("✓ 使用自定义API密钥初始化成功")
    
    # 测试OpenAI库导入失败的情况
    with patch('embedder.OpenAI', side_effect=ImportError):
        qwen_embedder = QwenEmbedder("test_api_key")
        
        # 检查属性
        assert qwen_embedder.api_key == "test_api_key"
        assert qwen_embedder.client is None
        assert qwen_embedder.dimension == 1536
        print("✓ OpenAI库导入失败时正确处理")
    
    print("QwenEmbedder初始化测试通过")

def test_qwen_embedder_with_mock_mode():
    """测试QwenEmbedder在Mock模式下的行为"""
    print("测试QwenEmbedder在Mock模式下的行为...")
    
    # 保存原始设置
    original_use_mock = settings.USE_MOCK
    
    try:
        # 设置为Mock模式
        settings.USE_MOCK = True
        
        # 创建QwenEmbedder实例
        qwen_embedder = QwenEmbedder("test_api_key")
        
        # 测试embed方法
        text = "测试文本"
        with patch('embedder.logger') as mock_logger:
            embedding = qwen_embedder.embed(text)
            
            # 检查是否记录了日志
            mock_logger.info.assert_called_with("使用MockEmbeddings模式")
            
            # 检查返回值
            assert isinstance(embedding, list)
            assert len(embedding) == 1536
            assert all(isinstance(x, float) for x in embedding)
            assert all(x == 0.0 for x in embedding)
            print("✓ Mock模式下正确返回模拟向量")
    finally:
        # 恢复原始设置
        settings.USE_MOCK = original_use_mock
    
    print("QwenEmbedder Mock模式测试通过")

def test_qwen_embedder_with_no_client():
    """测试QwenEmbedder在没有客户端时的行为"""
    print("测试QwenEmbedder在没有客户端时的行为...")
    
    # 保存原始设置
    original_use_mock = settings.USE_MOCK
    
    try:
        # 设置为非Mock模式
        settings.USE_MOCK = False
        
        # 创建没有客户端的QwenEmbedder实例
        qwen_embedder = QwenEmbedder("test_api_key")
        qwen_embedder.client = None  # 模拟没有客户端的情况
        
        # 测试embed方法
        text = "测试文本"
        with patch('embedder.logger') as mock_logger:
            embedding = qwen_embedder.embed(text)
            
            # 检查是否记录了日志
            mock_logger.info.assert_called_with("OpenAI库未安装，使用MockEmbeddings作为后备方案")
            
            # 检查返回值
            assert isinstance(embedding, list)
            assert len(embedding) == 1536
            assert all(isinstance(x, float) for x in embedding)
            assert all(x == 0.0 for x in embedding)
            print("✓ 没有客户端时正确回退到Mock模式")
    finally:
        # 恢复原始设置
        settings.USE_MOCK = original_use_mock
    
    print("QwenEmbedder无客户端测试通过")

def test_qwen_embedder_with_openai_exception():
    """测试QwenEmbedder在OpenAI异常时的行为"""
    print("测试QwenEmbedder在OpenAI异常时的行为...")
    
    # 保存原始设置
    original_use_mock = settings.USE_MOCK
    
    try:
        # 设置为非Mock模式
        settings.USE_MOCK = False
        
        # 创建QwenEmbedder实例并模拟OpenAI客户端
        qwen_embedder = QwenEmbedder("test_api_key")
        mock_client = Mock()
        mock_client.embeddings.create.side_effect = Exception("网络错误")
        qwen_embedder.client = mock_client
        
        # 测试embed方法
        text = "测试文本"
        with patch('embedder.logger') as mock_logger:
            embedding = qwen_embedder.embed(text)
            
            # 检查是否记录了错误日志
            mock_logger.error.assert_called()
            
            # 检查返回值（应该回退到Mock）
            assert isinstance(embedding, list)
            assert len(embedding) == 1536
            assert all(isinstance(x, float) for x in embedding)
            assert all(x == 0.0 for x in embedding)
            print("✓ OpenAI异常时正确回退到Mock模式")
    finally:
        # 恢复原始设置
        settings.USE_MOCK = original_use_mock
    
    print("QwenEmbedder异常处理测试通过")

def test_qwen_embedder_success():
    """测试QwenEmbedder成功调用的情况"""
    print("测试QwenEmbedder成功调用的情况...")
    
    # 保存原始设置
    original_use_mock = settings.USE_MOCK
    
    try:
        # 设置为非Mock模式
        settings.USE_MOCK = False
        
        # 创建QwenEmbedder实例并模拟OpenAI客户端
        qwen_embedder = QwenEmbedder("test_api_key")
        mock_client = Mock()
        mock_response = Mock()
        mock_response.data = [Mock(embedding=[0.1] * 1536)]
        mock_client.embeddings.create.return_value = mock_response
        qwen_embedder.client = mock_client
        
        # 测试embed方法
        text = "测试文本"
        with patch('embedder.logger') as mock_logger:
            embedding = qwen_embedder.embed(text)
            
            # 检查是否记录了日志
            mock_logger.info.assert_any_call(f"调用Qwen大模型生成文本嵌入，文本长度: {len(text)} 字符")
            mock_logger.info.assert_any_call("成功从Qwen大模型获取文本嵌入")
            
            # 检查返回值
            assert isinstance(embedding, list)
            assert len(embedding) == 1536
            assert all(isinstance(x, float) for x in embedding)
            assert embedding == [0.1] * 1536
            print("✓ 成功调用时返回正确的向量")
    finally:
        # 恢复原始设置
        settings.USE_MOCK = original_use_mock
    
    print("QwenEmbedder成功调用测试通过")

if __name__ == "__main__":
    print("开始测试Embedder模块...")
    print("=" * 50)
    
    test_mock_embeddings()
    print("-" * 30)
    
    test_qwen_embedder_initialization()
    print("-" * 30)
    
    test_qwen_embedder_with_mock_mode()
    print("-" * 30)
    
    test_qwen_embedder_with_no_client()
    print("-" * 30)
    
    test_qwen_embedder_with_openai_exception()
    print("-" * 30)
    
    test_qwen_embedder_success()
    print("-" * 30)
    
    print("=" * 50)
    print("所有测试通过!")