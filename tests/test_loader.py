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
    
    # 创建临时Java文件（包含多个类和方法）
    with tempfile.NamedTemporaryFile(mode='w', suffix='.java', delete=False) as f:
        f.write("""
/**
 * 海智物流测试类1
 */
public class TestClass1 {
    public static void main(String[] args) {
        System.out.println("Hello, Haiwise Logistics!");
    }
}

/**
 * 海智物流测试类2
 */
class TestClass2 {
    public void method1() {
        System.out.println("Method 1");
    }
    
    private void method2() {
        System.out.println("Method 2");
    }
}
""")
        java_file_path = f.name
    
    # 创建临时Python文件（包含多个函数和类）
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write("""
\"\"\"
海智物流测试模块
\"\"\"

def hello():
    print("Hello, Haiwise Logistics!")

def goodbye():
    print("Goodbye, Haiwise Logistics!")

class TestClass:
    def method1(self):
        print("Method 1")
    
    def method2(self):
        print("Method 2")

if __name__ == "__main__":
    hello()
""")
        python_file_path = f.name
    
    try:
        # 测试Java文件加载
        java_docs = loader.load(java_file_path)
        # 检查是否正确分割为多个Document对象
        assert len(java_docs) >= 2  # 应该至少分割为2个部分
        assert any("TestClass1" in doc.content for doc in java_docs)
        assert any("TestClass2" in doc.content for doc in java_docs)
        assert all(doc.metadata['language'] == 'java' for doc in java_docs)
        assert all(doc.metadata['source'] == 'code' for doc in java_docs)
        # 检查元数据中的行号信息
        assert all('start_line' in doc.metadata for doc in java_docs)
        assert all('end_line' in doc.metadata for doc in java_docs)
        assert all(doc.start_line > 0 for doc in java_docs)
        assert all(doc.end_line > 0 for doc in java_docs)
        print("✓ Java文件加载测试通过")
        
        # 测试Python文件加载
        python_docs = loader.load(python_file_path)
        # 检查是否正确分割为多个Document对象
        assert len(python_docs) >= 3  # 应该至少分割为3个部分
        assert any("def hello" in doc.content for doc in python_docs)
        assert any("def goodbye" in doc.content for doc in python_docs)
        assert any("class TestClass" in doc.content for doc in python_docs)
        assert all(doc.metadata['language'] == 'python' for doc in python_docs)
        assert all(doc.metadata['source'] == 'code' for doc in python_docs)
        # 检查元数据中的行号信息
        assert all('start_line' in doc.metadata for doc in python_docs)
        assert all('end_line' in doc.metadata for doc in python_docs)
        assert all(doc.start_line > 0 for doc in python_docs)
        assert all(doc.end_line > 0 for doc in python_docs)
        print("✓ Python文件加载测试通过")
        
    finally:
        # 清理临时文件
        os.unlink(java_file_path)
        os.unlink(python_file_path)

def test_markdown_file_loading():
    """测试Markdown文件加载"""
    loader = DocumentLoader()
    
    # 创建临时Markdown文件（包含多个章节）
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

# 系统架构

## 总体架构

系统采用微服务架构设计。

## 技术栈

- Java
- Python
- MySQL
""")
        md_file_path = f.name
    
    try:
        # 测试Markdown文件加载
        md_docs = loader.load(md_file_path)
        # 检查是否正确分割为多个Document对象
        assert len(md_docs) >= 2  # 应该至少分割为2个部分
        assert any("海智物流系统文档" in doc.content for doc in md_docs)
        assert any("系统架构" in doc.content for doc in md_docs)
        assert all(doc.metadata['language'] == 'markdown' for doc in md_docs)
        assert all(doc.metadata['source'] == 'markdown' for doc in md_docs)
        # 检查元数据中的行号信息
        assert all('start_line' in doc.metadata for doc in md_docs)
        assert all('end_line' in doc.metadata for doc in md_docs)
        assert all(doc.start_line > 0 for doc in md_docs)
        assert all(doc.end_line > 0 for doc in md_docs)
        print("✓ Markdown文件加载测试通过")
        
    finally:
        # 清理临时文件
        os.unlink(md_file_path)

def test_pdf_file_loading():
    """测试PDF文件加载"""
    loader = DocumentLoader()
    
    # 测试PDF文件加载（使用现有的测试文件）
    pdf_file_path = os.path.join(project_root, 'test_data', 'HaizhiLogistics.pdf')
    
    if os.path.exists(pdf_file_path):
        pdf_docs = loader.load(pdf_file_path)
        # 检查是否正确加载
        assert len(pdf_docs) > 0  # PDF应该至少有1页
        assert all(doc.metadata['language'] == 'pdf' for doc in pdf_docs)
        assert all(doc.metadata['source'] == 'pdf' for doc in pdf_docs)
        # 检查元数据中的行号信息
        assert all('start_line' in doc.metadata for doc in pdf_docs)
        assert all('end_line' in doc.metadata for doc in pdf_docs)
        assert all(doc.start_line > 0 for doc in pdf_docs)
        assert all(doc.end_line > 0 for doc in pdf_docs)
        print("✓ PDF文件加载测试通过")
    else:
        print("⚠ PDF测试文件不存在，跳过PDF测试")

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
    test_pdf_file_loading()
    test_unsupported_format()
    test_nonexistent_file()
    
    print("-" * 30)
    print("所有测试通过!")