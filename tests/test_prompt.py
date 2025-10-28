#!/usr/bin/env python3
"""
Prompt模块测试文件
"""

import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from prompt import PromptBuilder
from retriver import RetrievedDocument

def test_prompt_building():
    """测试提示词构建功能"""
    print("开始测试提示词构建...")
    
    # 创建测试文档
    docs = [
        RetrievedDocument(
            content="这是第一份文档的内容，包含了关于物流系统的重要信息。",
            source="test_doc1.txt",
            location="Section 1",
            score=0.95,
            metadata={}
        ),
        RetrievedDocument(
            content="这是第二份文档的内容，描述了仓储管理的关键要点。",
            source="test_doc2.txt",
            location="Chapter 3",
            score=0.87,
            metadata={}
        )
    ]
    
    # 测试不同角色类型的提示词构建
    prompt_builder = PromptBuilder(max_chars=1000)
    
    # 测试开发者角色
    dev_prompt = prompt_builder.build_prompt("什么是物流系统？", docs, "dev")
    assert len(dev_prompt) == 1
    assert dev_prompt[0]["role"] == "user"
    assert "物流系统开发专家" in dev_prompt[0]["content"]
    assert "test_doc1.txt#Section 1" in dev_prompt[0]["content"]
    assert "什么是物流系统？" in dev_prompt[0]["content"]
    print("✓ 开发者角色提示词构建测试通过")
    
    # 测试产品角色
    product_prompt = prompt_builder.build_prompt("仓储管理的关键要点是什么？", docs, "product")
    assert len(product_prompt) == 1
    assert product_prompt[0]["role"] == "user"
    assert "物流产品专家" in product_prompt[0]["content"]
    print("✓ 产品角色提示词构建测试通过")
    
    # 测试默认角色（未指定时应为开发者）
    default_prompt = prompt_builder.build_prompt("默认角色测试", docs)
    assert "物流系统开发专家" in default_prompt[0]["content"]
    print("✓ 默认角色提示词构建测试通过")

def test_context_truncation():
    """测试上下文长度裁剪功能"""
    print("\n开始测试上下文长度裁剪...")
    
    # 创建长内容文档
    long_content = "这是一个很长的文档内容。" * 100  # 制造超过限制的内容
    docs = [
        RetrievedDocument(
            content=long_content,
            source="long_doc.txt",
            location="Section 1",
            score=0.95,
            metadata={}
        )
    ]
    
    # 设置较小的字符限制进行测试
    small_limit = 100
    prompt_builder = PromptBuilder(max_chars=small_limit)
    
    # 构建提示词
    prompt = prompt_builder.build_prompt("测试长文档", docs)
    
    # 检查上下文是否被裁剪
    content_length = len(prompt[0]["content"])
    # 允许一定误差范围，因为还有模板文本
    assert content_length <= small_limit + 200, f"内容长度超出限制: {content_length}"
    assert "... [内容过长已裁剪] ..." in prompt[0]["content"]
    print("✓ 上下文长度裁剪测试通过")

def test_empty_docs_handling():
    """测试空文档处理"""
    print("\n开始测试空文档处理...")
    
    # 使用空文档列表
    docs = []
    
    prompt_builder = PromptBuilder()
    prompt = prompt_builder.build_prompt("空文档测试", docs)
    
    assert len(prompt) == 1
    assert prompt[0]["role"] == "user"
    assert "问题：空文档测试" in prompt[0]["content"]
    print("✓ 空文档处理测试通过")

if __name__ == "__main__":
    print("开始测试Prompt模块...")
    print("=" * 50)
    
    test_prompt_building()
    test_context_truncation()
    test_empty_docs_handling()
    
    print("\n" + "=" * 50)
    print("所有Prompt模块测试通过!")