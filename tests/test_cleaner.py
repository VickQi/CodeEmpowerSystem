#!/usr/bin/env python3
"""
TextCleaner测试文件
"""

import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from cleaner import TextCleaner

def test_remove_irrelevant_comments_java():
    """测试Java文件中去除无关注释"""
    cleaner = TextCleaner()
    
    # 测试Java代码中的注释清理
    text = """
public class TestClass {
    // TODO: 这是一个待办事项
    // FIXME: 需要修复的问题
    // HACK: 临时解决方案
    // XXX: 注意事项
    /* 
     * 这是多行注释
     * 包含一些无用信息
     */
    public void testMethod() {
        System.out.println("Hello World");
    }
}
"""
    
    cleaned = cleaner.clean(text, 'java')
    assert "// TODO:" not in cleaned
    assert "// FIXME:" not in cleaned
    assert "// HACK:" not in cleaned
    assert "// XXX:" not in cleaned
    assert "/*" not in cleaned
    assert "Hello World" in cleaned
    print("✓ Java文件注释清理测试通过")

def test_remove_irrelevant_comments_python():
    """测试Python文件中去除无关注释"""
    cleaner = TextCleaner()
    
    # 测试Python代码中的注释清理
    text = """
def test_function():
    # TODO: 这是一个待办事项
    # FIXME: 需要修复的问题
    # HACK: 临时解决方案
    # XXX: 注意事项
    print("Hello World")  # 正常注释应该保留
"""
    
    cleaned = cleaner.clean(text, 'python')
    assert "# TODO:" not in cleaned
    assert "# FIXME:" not in cleaned
    assert "# HACK:" not in cleaned
    assert "# XXX:" not in cleaned
    assert "print(\"Hello World\")" in cleaned
    assert "# 正常注释应该保留" in cleaned
    print("✓ Python文件注释清理测试通过")

def test_fix_line_breaks():
    """测试修复断行"""
    cleaner = TextCleaner()
    
    # 测试修复被换行符分割的英文单词
    text = "This is a word split ex-\nample, and another case: ware-\nhouse"
    
    cleaned = cleaner.clean(text, 'text')
    assert "ex-\nample" not in cleaned
    assert "ware-\nhouse" not in cleaned
    assert "example" in cleaned
    assert "warehouse" in cleaned
    print("✓ 断行修复测试通过")

def test_standardize_terms():
    """测试标准化技术术语"""
    cleaner = TextCleaner()
    
    # 测试术语标准化
    text = "仓库管理系统用于管理仓库，仓库是重要的物流节点。订单处理系统处理订单，库存管理系统管理库存。"
    
    cleaned = cleaner.clean(text, 'text')
    # 检查原始术语是否已被替换
    # 注意：由于"订单处理"包含"订单"，所以直接检查"订单"可能不准确
    # 我们应该检查特定的术语组合
    assert "仓库管理系统" not in cleaned
    assert "订单处理系统" not in cleaned
    assert "库存管理系统" not in cleaned
    # 检查标准化术语是否已正确应用
    assert "仓储管理" in cleaned
    assert "物流节点" in cleaned
    assert "订单" in cleaned
    assert "库存管理" in cleaned
    print("✓ 技术术语标准化测试通过")

def test_standardize_units():
    """测试统一单位表示"""
    cleaner = TextCleaner()
    
    # 测试单位标准化
    text = "货物重量为5kg，10KG，运力为2ton，3TON，长度为100m，200M，距离为5km，10KM，宽度为30cm，50CM"
    
    cleaned = cleaner.clean(text, 'text')
    # 检查原始单位是否已被替换
    assert "kg" not in cleaned
    assert "KG" not in cleaned
    assert "ton" not in cleaned
    assert "TON" not in cleaned
    assert "m" not in cleaned
    assert "M" not in cleaned
    assert "km" not in cleaned
    assert "KM" not in cleaned
    assert "cm" not in cleaned
    assert "CM" not in cleaned
    # 检查标准化单位是否已正确应用
    assert "5公斤" in cleaned
    assert "10公斤" in cleaned
    assert "2吨" in cleaned
    assert "3吨" in cleaned
    assert "100米" in cleaned
    assert "200米" in cleaned
    assert "5千米" in cleaned
    assert "10千米" in cleaned
    assert "30厘米" in cleaned
    assert "50厘米" in cleaned
    print("✓ 单位标准化测试通过")

def test_clean_empty_text():
    """测试清洗空文本"""
    cleaner = TextCleaner()
    
    # 测试空文本处理
    text = ""
    cleaned = cleaner.clean(text, 'text')
    assert cleaned == ""
    print("✓ 空文本处理测试通过")

def test_clean_none_file_type():
    """测试处理不支持的文件类型"""
    cleaner = TextCleaner()
    
    # 测试不支持的文件类型
    text = "仓储 kg TODO: 测试"
    cleaned = cleaner.clean(text, 'unknown')
    # 应该仍然处理术语和单位标准化
    assert "仓储" in cleaned
    assert "公斤" in cleaned
    # 但不会移除注释，因为文件类型不支持
    assert "TODO:" in cleaned
    print("✓ 不支持文件类型处理测试通过")

if __name__ == "__main__":
    print("开始测试TextCleaner...")
    print("-" * 30)
    
    test_remove_irrelevant_comments_java()
    test_remove_irrelevant_comments_python()
    test_fix_line_breaks()
    test_standardize_terms()
    test_standardize_units()
    test_clean_empty_text()
    test_clean_none_file_type()
    
    print("-" * 30)
    print("所有测试通过!")