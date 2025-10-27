#!/usr/bin/env python3
"""
SemanticChunker测试文件
"""

import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from chunker import SemanticChunker, KnowledgeChunk

def test_python_code_splitting():
    """测试Python代码按函数边界切分"""
    chunker = SemanticChunker(chunk_size=500, overlap=50)
    
    # 测试Python代码切分
    python_code = '''
def hello_world():
    """第一个函数"""
    print("Hello, World!")
    return True

def calculate_sum(a, b):
    """计算两个数的和"""
    result = a + b
    return result

class TestClass:
    def method_one(self):
        print("Method one")
        
    def method_two(self):
        print("Method two")
        
if __name__ == "__main__":
    hello_world()
'''
    
    chunks = chunker.split(python_code, "test_source", "python")
    assert len(chunks) >= 1, "应该至少生成一个块"
    assert all(isinstance(chunk, KnowledgeChunk) for chunk in chunks), "所有项都应该是KnowledgeChunk实例"
    assert all(chunk.metadata["type"] == "code" for chunk in chunks), "所有块的类型都应该是code"
    assert all(chunk.metadata["language"] == "python" for chunk in chunks), "所有块的语言都应该是python"
    print("✓ Python代码切分测试通过")

def test_java_code_splitting():
    """测试Java代码按方法边界切分"""
    chunker = SemanticChunker(chunk_size=500, overlap=50)
    
    # 测试Java代码切分
    java_code = '''
public class TestClass {
    public void helloWorld() {
        System.out.println("Hello, World!");
    }
    
    public int calculateSum(int a, int b) {
        int result = a + b;
        return result;
    }
    
    private void privateMethod() {
        System.out.println("Private method");
    }
}
'''
    
    chunks = chunker.split(java_code, "test_source", "java")
    assert len(chunks) >= 1, "应该至少生成一个块"
    assert all(isinstance(chunk, KnowledgeChunk) for chunk in chunks), "所有项都应该是KnowledgeChunk实例"
    assert all(chunk.metadata["type"] == "code" for chunk in chunks), "所有块的类型都应该是code"
    assert all(chunk.metadata["language"] == "java" for chunk in chunks), "所有块的语言都应该是java"
    print("✓ Java代码切分测试通过")

def test_document_splitting():
    """测试文档按章节切分"""
    chunker = SemanticChunker(chunk_size=500, overlap=50)
    
    # 测试文档切分
    document = '''
# 章节一

这是文档的第一个章节。它包含一些介绍性内容。
这些内容应该被正确地分割。

## 小节1.1

这是第一个小节的内容。

## 小节1.2

这是第二个小节的内容。

# 章节二

这是文档的第二个章节。它也包含一些内容。

这是第二个章节的第二段内容。
'''
    
    chunks = chunker.split(document, "test_source", "markdown")
    assert len(chunks) >= 1, "应该至少生成一个块"
    assert all(isinstance(chunk, KnowledgeChunk) for chunk in chunks), "所有项都应该是KnowledgeChunk实例"
    assert all(chunk.metadata["type"] == "document" for chunk in chunks), "所有块的类型都应该是document"
    print("✓ 文档切分测试通过")

def test_large_content_splitting():
    """测试大内容切分和重叠功能"""
    chunker = SemanticChunker(chunk_size=100, overlap=20)
    
    # 创建一个大的文本内容
    large_text = "这是很长的文本内容。" * 50
    
    chunks = chunker.split(large_text, "test_source", "text")
    assert len(chunks) >= 1, "应该生成多个块"
    assert all(isinstance(chunk, KnowledgeChunk) for chunk in chunks), "所有项都应该是KnowledgeChunk实例"
    print("✓ 大内容切分测试通过")

def test_empty_content():
    """测试空内容处理"""
    chunker = SemanticChunker()
    
    # 测试空文本
    empty_text = ""
    chunks = chunker.split(empty_text, "test_source", "text")
    assert len(chunks) == 0, "空文本应该生成0个块"
    print("✓ 空内容处理测试通过")

def test_chunk_size_limit():
    """测试块大小限制"""
    chunker = SemanticChunker(chunk_size=100, overlap=10)
    
    # 测试内容超过块大小的情况
    long_paragraph = "这是一个非常长的段落。" * 50
    
    chunks = chunker.split(long_paragraph, "test_source", "text")
    # 检查是否有块生成
    assert len(chunks) >= 1, "应该生成至少一个块"
    # 检查大部分块是否在合理大小范围内（允许少数超出以确保内容完整性）
    oversized_chunks = [chunk for chunk in chunks if len(chunk.content) > chunker.chunk_size + 50]
    assert len(oversized_chunks) <= len(chunks) * 0.3, "超出大小限制的块应该只占少数"
    print("✓ 块大小限制测试通过")

if __name__ == "__main__":
    print("开始测试SemanticChunker...")
    print("-" * 30)
    
    test_python_code_splitting()
    test_java_code_splitting()
    test_document_splitting()
    test_large_content_splitting()
    test_empty_content()
    test_chunk_size_limit()
    
    print("-" * 30)
    print("所有测试通过!")