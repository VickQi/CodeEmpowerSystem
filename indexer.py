import os
import json
import faiss
import numpy as np
from typing import List, Any
from openai import OpenAI
from chunker import KnowledgeChunk
from settings import Settings
import logging

# 获取日志记录器
logger = logging.getLogger(__name__)

class QwenEmbedder:
    """使用Qwen大模型进行文本嵌入"""
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.client = OpenAI(
            api_key=api_key,
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
        )
        # 实际使用的模型维度（根据实际测试结果调整）
        self.dimension = 1536  # 实际模型维度
    
    def embed(self, text: str) -> List[float]:
        """生成文本的向量表示"""
        try:
            response = self.client.embeddings.create(
                model="text-embedding-v1",  # 使用实际的模型
                input=text
            )
            return response.data[0].embedding
        except Exception as e:
            logger.error(f"嵌入生成失败: {e}")
            # 返回零向量作为后备
            return [0.0] * self.dimension

class VectorIndexer:
    def __init__(self, embedder: Any, index_path: str):
        self.embedder = embedder
        self.index_path = index_path
        self.index = None
        self.doc_ids = []
        self.settings = Settings()
    
    def build_index(self, chunks: List[KnowledgeChunk]) -> None:
        """构建向量索引"""
        logger.info(f"开始构建向量索引，包含 {len(chunks)} 个知识块")
        
        # 仅CPU模式
        self.index = faiss.IndexFlatL2(self.embedder.dimension)
        
        # 生成向量
        vectors = []
        for chunk in chunks:
            vector = self.embedder.embed(chunk.content)
            # 确保向量维度正确
            if len(vector) != self.embedder.dimension:
                logger.warning(f"警告: 向量维度不匹配，期望 {self.embedder.dimension}，实际 {len(vector)}")
                # 如果维度不匹配，使用零向量填充或截断
                if len(vector) < self.embedder.dimension:
                    vector.extend([0.0] * (self.embedder.dimension - len(vector)))
                else:
                    vector = vector[:self.embedder.dimension]
            vectors.append(vector)
            self.doc_ids.append(chunk.source)  # 使用source作为文档ID
        
        # 添加到索引
        if vectors:
            self.index.add(np.array(vectors).astype('float32'))
            logger.info(f"成功添加 {len(vectors)} 个向量到索引")
        
        # 保存索引
        self.save_index()
        logger.info(f"索引构建完成，总共 {self.index.ntotal} 个向量")
    
    def save_index(self) -> None:
        """持久化索引"""
        if self.index is not None:
            faiss.write_index(self.index, self.index_path)
            with open(self.index_path + '.ids', 'w') as f:
                json.dump(self.doc_ids, f)
            logger.debug(f"索引已保存到 {self.index_path}")
    
    def load_index(self) -> None:
        """加载索引"""
        if os.path.exists(self.index_path):
            self.index = faiss.read_index(self.index_path)
            with open(self.index_path + '.ids', 'r') as f:
                self.doc_ids = json.load(f)
            logger.info(f"索引加载成功，包含 {self.index.ntotal} 个向量")
        else:
            logger.warning(f"索引文件不存在: {self.index_path}")
    
    def add_chunks(self, chunks: List[KnowledgeChunk]) -> None:
        """增量更新索引"""
        logger.info(f"开始增量更新索引，添加 {len(chunks)} 个新块")
        
        if self.index is None:
            # 如果索引不存在，则创建新索引
            self.build_index(chunks)
        else:
            # 增量添加新块
            vectors = []
            new_doc_ids = []
            for chunk in chunks:
                vector = self.embedder.embed(chunk.content)
                # 确保向量维度正确
                if len(vector) != self.embedder.dimension:
                    logger.warning(f"警告: 向量维度不匹配，期望 {self.embedder.dimension}，实际 {len(vector)}")
                    # 如果维度不匹配，使用零向量填充或截断
                    if len(vector) < self.embedder.dimension:
                        vector.extend([0.0] * (self.embedder.dimension - len(vector)))
                    else:
                        vector = vector[:self.embedder.dimension]
                vectors.append(vector)
                new_doc_ids.append(chunk.source)
            
            # 添加到现有索引
            if vectors:
                self.index.add(np.array(vectors).astype('float32'))
                self.doc_ids.extend(new_doc_ids)
                logger.info(f"成功添加 {len(vectors)} 个向量到现有索引")
            
            # 保存更新后的索引
            self.save_index()
    
    def search(self, query: str, k: int = 5) -> List[dict]:
        """搜索相似向量"""
        logger.debug(f"开始向量搜索，查询: \"{query}\", k={k}")
        
        if self.index is None:
            self.load_index()
            
        if self.index is None:
            logger.warning("索引未加载，返回空结果")
            return []
        
        # 生成查询向量
        query_vector = self.embedder.embed(query)
        # 确保查询向量维度正确
        if len(query_vector) != self.embedder.dimension:
            logger.warning(f"警告: 查询向量维度不匹配，期望 {self.embedder.dimension}，实际 {len(query_vector)}")
            # 如果维度不匹配，使用零向量填充或截断
            if len(query_vector) < self.embedder.dimension:
                query_vector.extend([0.0] * (self.embedder.dimension - len(query_vector)))
            else:
                query_vector = query_vector[:self.embedder.dimension]
        
        # 执行搜索
        distances, indices = self.index.search(
            np.array([query_vector]).astype('float32'), 
            min(k, self.index.ntotal)
        )
        
        # 构建结果
        results = []
        for i, (distance, index) in enumerate(zip(distances[0], indices[0])):
            if index != -1 and index < len(self.doc_ids):  # 有效索引
                results.append({
                    'id': self.doc_ids[index],
                    'distance': float(distance),
                    'score': 1.0 / (1.0 + float(distance))  # 转换为相似度得分
                })
        
        logger.debug(f"向量搜索返回 {len(results)} 个结果")
        return results