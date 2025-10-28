import os
from dotenv import load_dotenv

# 加载.env文件
load_dotenv()

class Settings:
    def __init__(self):
        # 从环境变量加载
        self.USE_GPU = os.getenv('USE_GPU', 'false').lower() == 'true'
        self.LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
        self.LOG_PATH = os.getenv('LOG_PATH', 'logs/')
        
        self.DATA_PATH = os.getenv('DATA_PATH', 'data/')
        self.VECTOR_STORE_PATH = os.getenv('VECTOR_STORE_PATH', 'vectorstore/')
        
        self.CHUNK_SIZE = int(os.getenv('CHUNK_SIZE', '500'))
        self.CHUNK_OVERLAP = int(os.getenv('CHUNK_OVERLAP', '50'))
        
        self.TOP_K = int(os.getenv('TOP_K', '5'))
        self.USE_BM25 = os.getenv('USE_BM25', 'true').lower() == 'true'
        
        self.MAX_CONTEXT_CHARS = int(os.getenv('MAX_CONTEXT_CHARS', '3500'))
        
        # USE_MOCK控制是否使用Mock模式
        self.USE_MOCK = os.getenv('USE_MOCK', 'true').lower() == 'true'
        
        # Qwen大模型API KEY
        self.QWEN_API_KEY = os.getenv('QWEN_API_KEY', '')

# 创建全局settings实例
settings = Settings()