#!/usr/bin/env python3
"""
Retriever测试文件
"""

import sys
from pathlib import Path
from unittest.mock import Mock, MagicMock

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from retriver import Retriever, RetrievedDocument, SimpleBM25Index
from indexer import VectorIndexer

class MockVectorIndex:
    """模拟向量索引用于测试"""
    def search(self, query: str, k: int = 5):
        """模拟搜索结果"""
        return [
            {'id': 'doc1', 'score': 0.9},
            {'id': 'doc2', 'score': 0.8},
            {'id': 'doc3', 'score': 0.7}
        ]

class MockBM25Index:
    """模拟BM25索引用于测试"""
    def search(self, query: str, k: int = 5):
        """模拟搜索结果"""
        return [
            {'id': 'doc2', 'score': 5, 'content': '测试内容2'},
            {'id': 'doc3', 'score': 3, 'content': '测试内容3'},
            {'id': 'doc4', 'score': 2, 'content': '测试内容4'}
        ]

def test_retriever_initialization():
    """测试Retriever初始化"""
    vector_index = MockVectorIndex()
    bm25_index = MockBM25Index()
    
    retriever = Retriever(vector_index, bm25_index)
    
    assert retriever.vector_index == vector_index
    assert retriever.bm25_index == bm25_index
    print("✓ Retriever初始化测试通过")

def test_retrieve_with_vector_only():
    """测试仅使用向量检索"""
    vector_index = MockVectorIndex()
    retriever = Retriever(vector_index)
    
    results = retriever.retrieve("测试查询", k=5, use_bm25=False)
    
    assert len(results) > 0
    assert all(isinstance(doc, RetrievedDocument) for doc in results)
    print("✓ 仅向量检索测试通过")

def test_retrieve_with_hybrid_search():
    """测试混合检索"""
    vector_index = MockVectorIndex()
    bm25_index = MockBM25Index()
    retriever = Retriever(vector_index, bm25_index)
    
    results = retriever.retrieve("测试查询", k=5, use_bm25=True)
    
    assert len(results) > 0
    assert all(isinstance(doc, RetrievedDocument) for doc in results)
    # 检查是否正确合并了得分
    assert hasattr(results[0], 'score')
    assert 'vector_score' in results[0].metadata
    assert 'bm25_score' in results[0].metadata
    print("✓ 混合检索测试通过")

def test_retrieve_deduplication():
    """测试检索结果去重"""
    vector_index = MockVectorIndex()
    retriever = Retriever(vector_index)
    
    # 创建包含重复项的模拟结果
    results = retriever.retrieve("测试查询", k=10, use_bm25=False)
    
    # 验证没有重复的source
    sources = [doc.source for doc in results]
    assert len(sources) == len(set(sources)), "检索结果应无重复"
    print("✓ 检索结果去重测试通过")

def test_simple_bm25_index():
    """测试SimpleBM25Index"""
    bm25_index = SimpleBM25Index()
    bm25_index.add_documents([
        "这是第一个测试文档",
        "这是第二个测试文档",
        "这是第三个文档"
    ])
    
    results = bm25_index.search("测试文档", k=2)
    
    assert len(results) <= 2
    assert all('id' in result for result in results)
    assert all('score' in result for result in results)
    print("✓ SimpleBM25Index测试通过")

def test_merge_results():
    """测试结果合并功能"""
    vector_index = MockVectorIndex()
    bm25_index = MockBM25Index()
    retriever = Retriever(vector_index, bm25_index)
    
    vec_results = [{'id': 'doc1', 'score': 0.9}]
    bm25_results = [{'id': 'doc1', 'score': 5, 'content': '测试内容'}]
    
    merged = retriever._merge_results(vec_results, bm25_results)
    
    assert len(merged) > 0
    assert isinstance(merged[0], RetrievedDocument)
    assert merged[0].score > 0
    print("✓ 结果合并功能测试通过")

if __name__ == "__main__":
    print("开始测试Retriever...")
    print("-" * 30)
    
    test_retriever_initialization()
    test_retrieve_with_vector_only()
    test_retrieve_with_hybrid_search()
    test_retrieve_deduplication()
    test_simple_bm25_index()
    test_merge_results()
    
    print("-" * 30)
    print("所有测试通过!")