from typing import List, Optional
from dataclasses import dataclass
from indexer import VectorIndexer
import logging

# 获取日志记录器
logger = logging.getLogger(__name__)

@dataclass
class RetrievedDocument:
    """检索到的文档类"""
    content: str
    source: str
    location: str
    score: float
    metadata: dict

class SimpleBM25Index:
    """简单的BM25索引实现（用于演示）"""
    def __init__(self):
        self.documents = []
        
    def add_documents(self, documents: List[str]):
        """添加文档到索引"""
        self.documents.extend(documents)
        
    def search(self, query: str, k: int = 5) -> List[dict]:
        """简单的关键词匹配搜索"""
        results = []
        query_terms = query.lower().split()
        
        for i, doc in enumerate(self.documents):
            score = sum(1 for term in query_terms if term in doc.lower())
            if score > 0:
                results.append({
                    'id': f'doc_{i}',
                    'score': score,
                    'content': doc
                })
        
        # 按分数排序
        results.sort(key=lambda x: x['score'], reverse=True)
        return results[:k]

class Retriever:
    def __init__(self, vector_index: VectorIndexer, bm25_index: Optional[SimpleBM25Index] = None):
        self.vector_index = vector_index
        self.bm25_index = bm25_index
    
    def retrieve(self, query: str, k: int = 5, use_bm25: bool = True) -> List[RetrievedDocument]:
        """执行混合检索"""
        logger.info(f"Starting retrieval for query: \"{query}\"")
        
        # 向量检索
        vector_results = self.vector_index.search(query, k)
        logger.debug(f"FAISS retrieved {len(vector_results)} documents")
        
        # BM25检索（如果启用）
        bm25_results = []
        if use_bm25 and self.bm25_index:
            bm25_results = self.bm25_index.search(query, k)
            logger.debug(f"BM25 retrieved {len(bm25_results)} documents")
        
        # 合并结果
        merged = self._merge_results(vector_results, bm25_results)
        logger.debug(f"Results merged to {len(merged)} documents")
        
        # 去重
        deduplicated = self._deduplicate(merged)
        logger.debug(f"Results deduplicated to {len(deduplicated)} documents")
        
        result = deduplicated[:k]
        logger.info(f"Merged and deduplicated to {len(result)} documents")
        
        return result
    
    def _merge_results(self, vec_results: List[dict], bm25_results: List[dict]) -> List[RetrievedDocument]:
        """合并向量和BM25结果"""
        # 使用加权融合策略
        vec_weight = 0.7
        bm25_weight = 0.3
        
        # 创建一个字典来存储合并后的结果
        merged_scores = {}
        
        # 处理向量检索结果
        for result in vec_results:
            doc_id = result['id']
            # 将向量相似度得分转换为0-1范围
            score = result.get('score', 0)
            merged_scores[doc_id] = {'vector_score': score, 'bm25_score': 0, 'content': ''}
        
        # 处理BM25检索结果
        for result in bm25_results:
            doc_id = result['id']
            score = result.get('score', 0)
            if doc_id in merged_scores:
                merged_scores[doc_id]['bm25_score'] = score
                merged_scores[doc_id]['content'] = result.get('content', '')
            else:
                merged_scores[doc_id] = {'vector_score': 0, 'bm25_score': score, 'content': result.get('content', '')}
        
        # 计算加权得分并创建RetrievedDocument对象
        merged_documents = []
        for doc_id, scores in merged_scores.items():
            # 归一化BM25得分（假设最大得分为10）
            normalized_bm25 = min(1.0, scores['bm25_score'] / 10.0) if scores['bm25_score'] > 0 else 0
            
            # 计算加权总分
            final_score = (vec_weight * scores['vector_score']) + (bm25_weight * normalized_bm25)
            
            document = RetrievedDocument(
                content=scores['content'],
                source=doc_id,
                location="unknown",
                score=final_score,
                metadata={
                    'vector_score': scores['vector_score'],
                    'bm25_score': scores['bm25_score']
                }
            )
            merged_documents.append(document)
        
        # 按最终得分排序
        merged_documents.sort(key=lambda x: x.score, reverse=True)
        return merged_documents
    
    def _deduplicate(self, results: List[RetrievedDocument]) -> List[RetrievedDocument]:
        """基于source去重"""
        seen = set()
        unique = []
        for res in results:
            key = res.source
            if key not in seen:
                seen.add(key)
                unique.append(res)
        return unique