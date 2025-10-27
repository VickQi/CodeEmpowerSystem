#!/usr/bin/env python3
"""
DocumentLoader测试文件
"""

import os
import sys
import tempfile
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from loader import DocumentLoader, Document, UnsupportedFormatError

def test_code_file_loading():
    """测试代码文件加载"""
    loader = DocumentLoader()
    
    # 创建临时Java文件
    with tempfile.NamedTemporaryFile(mode='w', suffix='.java', delete=False) as f:
        f.write("""
/**
 * 海智物流测试类
 */
public class TestClass {
    public static void main(String[] args) {
        System.out.println("Hello, Haiwise Logistics!");
    }
}
""")
        java_file_path = f.name
    
    # 创建临时Python文件
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write("""
\"\"\"
海智物流测试模块
\"\"\"

def hello():
    print("Hello, Haiwise Logistics!")

if __name__ == "__main__":
    hello()
""")
        python_file_path = f.name
    
    try:
        # 测试Java文件加载
        java_docs = loader.load(java_file_path)
        assert len(java_docs) == 1
        assert "海智物流测试类" in java_docs[0].content
        assert java_docs[0].metadata['language'] == 'java'
        assert java_docs[0].metadata['source'] == 'code'
        print("✓ Java文件加载测试通过")
        
        # 测试Python文件加载
        python_docs = loader.load(python_file_path)
        assert len(python_docs) == 1
        assert "海智物流测试模块" in python_docs[0].content
        assert python_docs[0].metadata['language'] == 'python'
        assert python_docs[0].metadata['source'] == 'code'
        print("✓ Python文件加载测试通过")
        
    finally:
        # 清理临时文件
        os.unlink(java_file_path)
        os.unlink(python_file_path)

def test_markdown_file_loading():
    """测试Markdown文件加载"""
    loader = DocumentLoader()
    
    # 创建临时Markdown文件
    with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
        f.write("""
# 海智物流系统文档

## 简介

这是海智物流的测试文档。

## 功能列表

- 订单管理
- 仓储管理
- 运输管理
- 分拣管理
""")
        md_file_path = f.name
    
    try:
        # 测试Markdown文件加载
        md_docs = loader.load(md_file_path)
        assert len(md_docs) == 1
        assert "海智物流系统文档" in md_docs[0].content
        assert md_docs[0].metadata['language'] == 'markdown'
        assert md_docs[0].metadata['source'] == 'markdown'
        print("✓ Markdown文件加载测试通过")
        
    finally:
        # 清理临时文件
        os.unlink(md_file_path)

def test_unsupported_format():
    """测试不支持的文件格式"""
    loader = DocumentLoader()
    
    # 创建临时文本文件
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write("这是一个测试文本文件")
        txt_file_path = f.name
    
    try:
        # 测试不支持的格式
        try:
            loader.load(txt_file_path)
            assert False, "应该抛出UnsupportedFormatError异常"
        except UnsupportedFormatError:
            print("✓ 不支持格式异常测试通过")
        
    finally:
        # 清理临时文件
        os.unlink(txt_file_path)

def test_nonexistent_file():
    """测试不存在的文件"""
    loader = DocumentLoader()
    
    try:
        loader.load("/nonexistent/file.pdf")
        assert False, "应该抛出FileNotFoundError异常"
    except FileNotFoundError:
        print("✓ 文件不存在异常测试通过")

if __name__ == "__main__":
    print("开始测试DocumentLoader...")
    print("-" * 30)
    
    test_code_file_loading()
    test_markdown_file_loading()
    test_unsupported_format()
    test_nonexistent_file()
    
    print("-" * 30)
    print("所有测试通过!")