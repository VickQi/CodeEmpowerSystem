#!/usr/bin/env python3
"""
Logger测试文件
"""

import sys
import os
import tempfile
from pathlib import Path
from unittest.mock import patch

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import logging
from logger import setup_logger

def test_logger_format():
    """测试日志格式是否符合要求"""
    print("开始测试日志格式...")
    
    # 创建临时目录用于日志文件
    with tempfile.TemporaryDirectory() as temp_dir:
        # 临时修改日志路径
        from settings import settings
        original_log_path = settings.LOG_PATH
        settings.LOG_PATH = temp_dir
        
        try:
            # 重新设置日志记录器
            logger = setup_logger()
            
            # 记录一些测试日志
            logger.info("测试信息日志")
            logger.debug("测试调试日志")
            logger.warning("测试警告日志")
            logger.error("测试错误日志")
            
            # 检查日志文件是否存在
            log_files = [f for f in os.listdir(temp_dir) if f.startswith('app_') and f.endswith('.log')]
            assert len(log_files) > 0, "应该创建日志文件"
            
            # 读取日志文件内容
            log_file_path = os.path.join(temp_dir, log_files[0])
            with open(log_file_path, 'r', encoding='utf-8') as f:
                log_content = f.read()
            
            # 检查日志格式
            lines = log_content.strip().split('\n')
            assert len(lines) >= 4, "应该至少有4行日志"
            
            for line in lines:
                # 检查每行日志是否符合格式要求：[时间戳] [日志级别] [模块名] 日志消息
                assert line.startswith('['), f"日志行应以[开始: {line}"
                assert '] [' in line, f"日志行应包含][分隔符: {line}"
                
                # 检查是否包含时间戳、日志级别和模块名
                parts = line.split('] [')
                assert len(parts) >= 3, f"日志行应至少包含3个部分: {line}"
                
                # 检查时间戳格式
                timestamp = parts[0][1:]  # 去掉开头的[
                assert ':' in timestamp and '-' in timestamp, f"时间戳格式不正确: {timestamp}"
                
                # 检查日志级别
                level = parts[1]
                assert level in ['INFO', 'DEBUG', 'WARNING', 'ERROR'], f"日志级别不正确: {level}"
                
                # 检查模块名
                module = parts[2]
                assert len(module) > 0, f"模块名不能为空: {line}"
            
            print("✓ 日志格式测试通过")
            print(f"日志文件路径: {log_file_path}")
            print("日志内容示例:")
            for line in lines[:5]:  # 只显示前5行
                print(f"  {line}")
                
        finally:
            # 恢复原始日志路径
            settings.LOG_PATH = original_log_path

def test_retriever_logging():
    """测试Retriever模块的日志记录"""
    print("\n开始测试Retriever日志记录...")
    
    # 由于Retriever需要完整的系统环境，我们只测试其日志记录功能
    from retriver import logger
    
    # 检查logger是否正确初始化
    assert logger is not None, "Retriever的logger应正确初始化"
    assert logger.name == 'retriver', f"Logger名称应为'retriver'，实际为'{logger.name}'"
    
    # 记录测试日志
    logger.info("Retriever模块测试日志")
    logger.debug("Retriever模块调试日志")
    
    print("✓ Retriever日志记录测试通过")

def test_indexer_logging():
    """测试Indexer模块的日志记录"""
    print("\n开始测试Indexer日志记录...")
    
    # 检查Indexer的logger
    from indexer import logger
    
    # 检查logger是否正确初始化
    assert logger is not None, "Indexer的logger应正确初始化"
    assert logger.name == 'indexer', f"Logger名称应为'indexer'，实际为'{logger.name}'"
    
    # 记录测试日志
    logger.info("Indexer模块测试日志")
    logger.debug("Indexer模块调试日志")
    
    print("✓ Indexer日志记录测试通过")

if __name__ == "__main__":
    print("开始测试Logger功能...")
    print("=" * 50)
    
    test_logger_format()
    test_retriever_logging()
    test_indexer_logging()
    
    print("\n" + "=" * 50)
    print("所有日志测试通过!")