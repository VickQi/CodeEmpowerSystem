import logging
import os
from datetime import datetime

def setup_logger():
    """配置系统日志"""
    # 在函数内部导入settings以避免循环导入
    from settings import settings
    
    # 确保日志目录存在
    os.makedirs(settings.LOG_PATH, exist_ok=True)
    
    logger = logging.getLogger('rag_system')
    logger.setLevel(logging.DEBUG)  # 设置为DEBUG以捕获更多日志
    
    # 避免重复添加处理器
    if logger.handlers:
        logger.handlers.clear()
    
    # 创建文件处理器
    log_file = os.path.join(settings.LOG_PATH, f'app_{datetime.now().strftime("%Y%m%d")}.log')
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
        
    audit_file = os.path.join(settings.LOG_PATH, 'audit.log')
    audit_handler = logging.FileHandler(audit_file, encoding='utf-8')
    audit_handler.setFormatter(formatter)
    audit_logger.addHandler(audit_handler)
    
    return logger

# 初始化全局日志记录器
logger = setup_logger()