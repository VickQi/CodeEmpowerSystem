import logging
import os
from datetime import datetime
import sys
from pathlib import Path

def setup_logger():
    """配置系统日志"""
    try:
        # 在函数内部导入settings以避免循环导入
        from settings import settings
        log_path = settings.LOG_PATH
    except (ImportError, ModuleNotFoundError):
        # 如果无法导入settings，则使用默认路径
        # 检查是否在测试目录下运行
        current_path = Path.cwd()
        if 'tests' in current_path.parts:
            log_path = 'tests/logs/'
        else:
            log_path = 'logs/'
    
    # 确保日志目录存在
    os.makedirs(log_path, exist_ok=True)
    
    logger = logging.getLogger('rag_system')
    logger.setLevel(logging.DEBUG)  # 设置为DEBUG以捕获更多日志
    
    # 避免重复添加处理器
    if logger.handlers:
        logger.handlers.clear()
    
    # 创建文件处理器
    log_file = os.path.join(log_path, f'app_{datetime.now().strftime("%Y%m%d")}.log')
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    
    # 创建控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    
    # 设置详细的格式，包含模块名
    formatter = logging.Formatter('[%(asctime)s] [%(levelname)s] [%(module)s] %(message)s')
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    # 添加处理器
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    # 配置审计日志
    audit_logger = logging.getLogger('audit')
    audit_logger.setLevel(logging.INFO)
    
    # 避免重复添加处理器
    if audit_logger.handlers:
        audit_logger.handlers.clear()
        
    audit_file = os.path.join(log_path, 'audit.log')
    audit_handler = logging.FileHandler(audit_file, encoding='utf-8')
    audit_handler.setFormatter(formatter)
    audit_logger.addHandler(audit_handler)
    
    # 专门为chunker模块创建日志文件
    chunker_logger = logging.getLogger('chunker')
    chunker_log_file = os.path.join(log_path, 'chunker.log')
    if not any(isinstance(h, logging.FileHandler) and h.baseFilename == os.path.abspath(chunker_log_file) for h in chunker_logger.handlers):
        chunker_file_handler = logging.FileHandler(chunker_log_file, encoding='utf-8')
        chunker_file_handler.setLevel(logging.INFO)
        chunker_file_handler.setFormatter(formatter)
        chunker_logger.addHandler(chunker_file_handler)
    
    return logger

# 初始化全局日志记录器
logger = setup_logger()