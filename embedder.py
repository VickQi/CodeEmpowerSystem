import numpy as np
from typing import List
from settings import settings
import logging
import hashlib

# 获取日志记录器
logger = logging.getLogger('rag_system')

class MockEmbeddings:
    """Mock嵌入模型，不进行网络请求，返回固定维度的模拟向量"""
    
    def __init__(self):
        # 与实际模型一致的维度
        self.dimension = 1536
    
    def embed(self, text: str) -> List[float]:
        """
        生成文本的向量表示（模拟）
        
        Args:
            text: 输入文本
            
        Returns:
            固定维度的模拟向量，基于文本内容生成
        """
        # 基于文本内容生成伪随机向量
        # 使用hash来确保相同文本产生相同向量
        hash_obj = hashlib.md5(text.encode('utf-8'))
        hash_digest = hash_obj.digest()
        
        # 从hash生成确定性的浮点数向量
        np.random.seed(int.from_bytes(hash_digest, 'big') % (2**32))
        vector = np.random.rand(self.dimension).tolist()
        
        # 归一化向量，使其模长为1
        norm = np.linalg.norm(vector)
        if norm > 0:
            vector = [x / norm for x in vector]
        
        return vector

class QwenEmbedder:
    """使用Qwen大模型进行文本嵌入"""
    
    def __init__(self, api_key: str = None):
        """
        初始化Qwen嵌入器
        
        Args:
            api_key: Qwen API密钥
        """
        # 如果没有提供API密钥，从settings获取
        if api_key is None:
            api_key = settings.QWEN_API_KEY
            
        self.api_key = api_key
        try:
            from openai import OpenAI
            self.client = OpenAI(
                api_key=api_key,
                base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
            )
        except ImportError:
            # 如果无法导入openai库，使用Mock作为后备
            self.client = None
            
        # 实际使用的模型维度
        self.dimension = 1536
    
    def embed(self, text: str) -> List[float]:
        """
        生成文本的向量表示
        
        Args:
            text: 输入文本
            
        Returns:
            文本的向量表示
        """
        # 如果使用Mock模式，直接使用MockEmbeddings
        if settings.USE_MOCK:
            logger.info("使用MockEmbeddings模式")
            mock_embedder = MockEmbeddings()
            return mock_embedder.embed(text)
            
        # 检查是否有客户端
        if self.client is None:
            logger.info("OpenAI库未安装，使用MockEmbeddings作为后备方案")
            mock_embedder = MockEmbeddings()
            return mock_embedder.embed(text)
            
        try:
            logger.info(f"调用Qwen大模型生成文本嵌入，文本长度: {len(text)} 字符")
            response = self.client.embeddings.create(
                model="text-embedding-v1",
                input=text
            )
            logger.info("成功从Qwen大模型获取文本嵌入")
            return response.data[0].embedding
        except Exception as e:
            # 出现异常时回退到Mock实现
            logger.error(f"嵌入生成失败，使用Mock回退: {e}")
            mock_embedder = MockEmbeddings()
            return mock_embedder.embed(text)