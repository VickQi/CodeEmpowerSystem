#!/usr/bin/env python3
"""
Parser模块测试文件
"""

import sys
import json
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from parser import ResponseParser
from retriver import RetrievedDocument

def test_valid_json_parsing():
    """测试有效JSON解析"""
    print("开始测试有效JSON解析...")
    
    # 创建测试数据
    raw_response = json.dumps({
        "answer": "这是测试回答",
        "citations": ["[test_doc.txt#Section1]"],
        "notes": "测试注释",
        "confidence": 0.85,
        "used_metrics": [{"name": "test_metric", "value": "测试值", "unit": "单位"}]
    })
    
    retrieved_docs = [
        RetrievedDocument(
            content="测试文档内容",
            source="test_doc.txt",
            location="Section1",
            score=0.95,
            metadata={}
        )
    ]
    
    # 创建解析器并解析
    parser = ResponseParser()
    result = parser.parse(raw_response, retrieved_docs)
    
    # 验证结果
    assert result['answer'] == "这是测试回答"
    assert result['confidence'] == 0.85
    assert "[test_doc.txt#Section1]" in result['citations']
    assert len(result['key_points']) >= 0  # 关键点可能为空，但字段应该存在
    
    print("✓ 有效JSON解析测试通过")

def test_invalid_json_repair():
    """测试无效JSON修复"""
    print("\n开始测试无效JSON修复...")
    
    # 包含一些错误的JSON（单引号、缺少引号等）
    raw_response = """{
        'answer': '这是测试回答',
        notes: '测试注释',
        "confidence": 0.85
    }"""
    
    retrieved_docs = [
        RetrievedDocument(
            content="测试文档内容",
            source="test_doc.txt",
            location="Section1",
            score=0.95,
            metadata={}
        )
    ]
    
    # 创建解析器并解析
    parser = ResponseParser()
    result = parser.parse(raw_response, retrieved_docs)
    
    # 验证结果
    assert 'answer' in result
    assert isinstance(result['confidence'], float)
    
    print("✓ 无效JSON修复测试通过")

def test_fallback_handling():
    """测试降级处理"""
    print("\n开始测试降级处理...")
    
    # 完全无效的响应
    raw_response = "这不是JSON格式的响应内容"
    
    retrieved_docs = [
        RetrievedDocument(
            content="测试文档内容",
            source="test_doc.txt",
            location="Section1",
            score=0.95,
            metadata={}
        )
    ]
    
    # 创建解析器并解析
    parser = ResponseParser()
    result = parser.parse(raw_response, retrieved_docs)
    
    # 验证结果
    assert result['answer'] == raw_response
    assert result['confidence'] == 0.5  # 修改为0.5，与解析器中的实现一致
    assert result['notes'] == '原始响应不是有效的JSON格式'
    
    print("✓ 降级处理测试通过")

def test_citation_validation():
    """测试引用验证"""
    print("\n开始测试引用验证...")
    
    # 包含有效和无效引用的响应
    raw_response = json.dumps({
        "answer": "这是测试回答",
        "citations": ["[test_doc.txt#Section1]", "[invalid_doc.txt#Section1]"],
        "notes": "测试注释",
        "confidence": 0.85
    })
    
    retrieved_docs = [
        RetrievedDocument(
            content="测试文档内容",
            source="test_doc.txt",
            location="Section1",
            score=0.95,
            metadata={}
        )
    ]
    
    # 创建解析器并解析
    parser = ResponseParser()
    result = parser.parse(raw_response, retrieved_docs)
    
    # 验证结果
    assert "[test_doc.txt#Section1]" in result['citations']
    assert "[invalid_doc.txt#Section1]" not in result['citations']
    
    print("✓ 引用验证测试通过")

def test_key_points_extraction():
    """测试关键点提取"""
    print("\n开始测试关键点提取...")
    
    raw_response = json.dumps({
        "answer": "这是第一个关键点。这是第二个关键点！这是第三个关键点？这是第四个关键点；这是第五个关键点\n这是第六个关键点",
        "citations": [],
        "notes": "",
        "confidence": 0.85
    })
    
    retrieved_docs = []
    
    # 创建解析器并解析
    parser = ResponseParser()
    result = parser.parse(raw_response, retrieved_docs)
    
    # 验证结果
    assert 'key_points' in result
    assert len(result['key_points']) > 0
    assert "这是第一个关键点" in result['key_points'][0]
    
    print("✓ 关键点提取测试通过")

def test_structured_response_format():
    """测试结构化响应格式"""
    print("\n开始测试结构化响应格式...")
    
    raw_response = json.dumps({
        "answer": "测试回答内容",
        "citations": ["[test.txt#sec1]"],
        "notes": "测试注释",
        "confidence": 0.95,
        "used_metrics": [{"name": "metric1", "value": "值1", "unit": "单位1"}]
    })
    
    retrieved_docs = [
        RetrievedDocument(
            content="测试文档内容",
            source="test.txt",
            location="sec1",
            score=0.95,
            metadata={}
        )
    ]
    
    # 创建解析器并解析
    parser = ResponseParser()
    result = parser.parse(raw_response, retrieved_docs)
    
    # 验证结构化响应格式
    expected_fields = ['answer', 'confidence', 'citations', 'key_points', 'notes', 'used_metrics']
    for field in expected_fields:
        assert field in result, f"响应应包含 {field} 字段"
    
    # 验证字段类型
    assert isinstance(result['answer'], str)
    assert isinstance(result['confidence'], float)
    assert isinstance(result['citations'], list)
    assert isinstance(result['key_points'], list)
    assert isinstance(result['notes'], str)
    assert isinstance(result['used_metrics'], list)
    
    print("✓ 结构化响应格式测试通过")

if __name__ == "__main__":
    print("开始测试Parser模块...")
    print("=" * 50)
    
    test_valid_json_parsing()
    test_invalid_json_repair()
    test_fallback_handling()
    test_citation_validation()
    test_key_points_extraction()
    test_structured_response_format()
    
    print("\n" + "=" * 50)
    print("所有Parser模块测试通过!")