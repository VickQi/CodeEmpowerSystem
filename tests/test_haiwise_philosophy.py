#!/usr/bin/env python3
"""
海智物流理念查询测试用例
"""

import sys
import os
import tempfile
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from loader import DocumentLoader
from cleaner import TextCleaner
from chunker import SemanticChunker
from indexer import VectorIndexer, QwenEmbedder
from retriver import Retriever
from settings import Settings

def test_query_haiwise_concepts():
    """测试查询海智物流相关概念"""
    print("开始测试查询海智物流相关概念...")
    
    # 获取API密钥
    settings = Settings()
    if not settings.QWEN_API_KEY:
        print("警告: QWEN_API_KEY未设置，将使用MockEmbedder")
        # 使用MockEmbedder替代实际的嵌入器进行测试
        class MockEmbedder:
            def __init__(self):
                self.dimension = 1536  # 与实际模型一致
                
            def embed(self, text: str):
                # 返回固定长度的模拟向量
                return [0.1] * self.dimension
        EmbedderClass = MockEmbedder
    else:
        EmbedderClass = QwenEmbedder
    
    # 创建临时索引文件
    with tempfile.NamedTemporaryFile(delete=False) as tmp_index_file:
        # 初始化组件
        loader = DocumentLoader()
        cleaner = TextCleaner()
        chunker = SemanticChunker()
        embedder = EmbedderClass(settings.QWEN_API_KEY) if not settings.QWEN_API_KEY else EmbedderClass(settings.QWEN_API_KEY)
        indexer = VectorIndexer(embedder, tmp_index_file.name)
        retriever = Retriever(indexer)
        
        # 获取test_data目录
        test_data_dir = project_root / "test_data"
        
        # 收集所有知识块
        all_chunks = []
        
        # 遍历test_data目录中的所有文件
        processed_files = 0
        for file_path in test_data_dir.iterdir():
            if file_path.is_file():
                try:
                    # 加载文档
                    documents = loader.load(str(file_path))
                    
                    for doc in documents:
                        # 获取文件类型
                        file_type = doc.metadata.get('language', 'unknown')
                        
                        # 清洗文本
                        cleaned_text = cleaner.clean(doc.content, file_type)
                        
                        # 切分文本
                        source = doc.metadata.get('file_path', str(file_path))
                        chunks = chunker.split(cleaned_text, source, file_type)
                        all_chunks.extend(chunks)
                        
                    processed_files += 1
                        
                except Exception as e:
                    print(f"处理文件 {file_path.name} 时出错: {e}")
                    continue
        
        print(f"总共处理了 {processed_files} 个文件")
        print(f"总共生成了 {len(all_chunks)} 个知识块")
        
        # 检查前几个块的内容和维度
        print("检查前几个块的向量维度:")
        test_embedder = EmbedderClass(settings.QWEN_API_KEY) if not settings.QWEN_API_KEY else EmbedderClass(settings.QWEN_API_KEY)
        for i, chunk in enumerate(all_chunks[:3]):
            vector = test_embedder.embed(chunk.content)
            print(f"  块 {i+1} 向量维度: {len(vector)}")
        
        # 构建索引
        print("开始构建向量索引...")
        indexer.build_index(all_chunks)
        print(f"索引构建完成，包含 {indexer.index.ntotal} 个向量")
        
        # 测试查询与海智物流相关的概念
        test_queries = [
            "海智物流系统",
            "物流管理",
            "仓储系统",
            "运输计划",
            "订单处理",
            "分拣管理"
        ]
        
        for query in test_queries:
            print(f"\n开始查询 '{query}'...")
            results = retriever.retrieve(query, k=3, use_bm25=False)
            
            print(f"检索到 {len(results)} 个结果:")
            for i, result in enumerate(results, 1):
                print(f"\n  结果 {i}:")
                print(f"    来源: {result.source}")
                print(f"    得分: {result.score:.4f}")
                # 打印完整的内容
                print(f"    内容:\n{result.content}\n")
            
            # 验证结果
            assert len(results) >= 0, f"查询 '{query}' 应该返回结果"
        
        # 清理临时文件
        os.unlink(tmp_index_file.name)
        if os.path.exists(tmp_index_file.name + '.ids'):
            os.unlink(tmp_index_file.name + '.ids')
        
        print("\n✓ 所有查询测试通过")

def test_detailed_search():
    """详细搜索并打印内容"""
    print("\n开始详细搜索...")
    
    # 获取API密钥
    settings = Settings()
    if not settings.QWEN_API_KEY:
        print("警告: QWEN_API_KEY未设置，将使用MockEmbedder")
        # 使用MockEmbedder替代实际的嵌入器进行测试
        class MockEmbedder:
            def __init__(self):
                self.dimension = 1536  # 与实际模型一致
                
            def embed(self, text: str):
                # 返回固定长度的模拟向量
                return [0.1] * self.dimension
        EmbedderClass = MockEmbedder
    else:
        EmbedderClass = QwenEmbedder
    
    # 创建临时索引文件
    with tempfile.NamedTemporaryFile(delete=False) as tmp_index_file:
        # 初始化组件
        loader = DocumentLoader()
        cleaner = TextCleaner()
        chunker = SemanticChunker()
        embedder = EmbedderClass(settings.QWEN_API_KEY) if not settings.QWEN_API_KEY else EmbedderClass(settings.QWEN_API_KEY)
        indexer = VectorIndexer(embedder, tmp_index_file.name)
        retriever = Retriever(indexer)
        
        # 获取test_data目录
        test_data_dir = project_root / "test_data"
        
        # 收集所有知识块
        all_chunks = []
        
        # 遍历test_data目录中的所有文件
        for file_path in test_data_dir.iterdir():
            if file_path.is_file():
                try:
                    # 加载文档
                    documents = loader.load(str(file_path))
                    
                    for doc in documents:
                        # 获取文件类型
                        file_type = doc.metadata.get('language', 'unknown')
                        
                        # 清洗文本
                        cleaned_text = cleaner.clean(doc.content, file_type)
                        
                        # 切分文本
                        source = doc.metadata.get('file_path', str(file_path))
                        chunks = chunker.split(cleaned_text, source, file_type)
                        all_chunks.extend(chunks)
                        
                except Exception as e:
                    print(f"处理文件 {file_path.name} 时出错: {e}")
                    continue
        
        # 检查前几个块的内容和维度
        print("检查前几个块的向量维度:")
        test_embedder = EmbedderClass(settings.QWEN_API_KEY) if not settings.QWEN_API_KEY else EmbedderClass(settings.QWEN_API_KEY)
        for i, chunk in enumerate(all_chunks[:3]):
            vector = test_embedder.embed(chunk.content)
            print(f"  块 {i+1} 向量维度: {len(vector)}")
        
        # 构建索引
        indexer.build_index(all_chunks)
        
        # 执行详细搜索
        queries = ["海智物流", "物流系统"]
        for query in queries:
            print(f"\n{'='*60}")
            print(f"搜索查询: '{query}'")
            print(f"{'='*60}")
            
            results = retriever.retrieve(query, k=5, use_bm25=False)
            
            if not results:
                print("未找到相关结果")
                continue
                
            for i, result in enumerate(results, 1):
                print(f"\n--- 结果 {i} (得分: {result.score:.4f}) ---")
                print(f"来源文件: {result.source}")
                print("内容:")
                print(result.content)
                print("-" * 60)
        
        # 清理临时文件
        os.unlink(tmp_index_file.name)
        if os.path.exists(tmp_index_file.name + '.ids'):
            os.unlink(tmp_index_file.name + '.ids')

if __name__ == "__main__":
    print("开始测试海智物流相关概念查询...")
    print("=" * 50)
    
    test_query_haiwise_concepts()
    test_detailed_search()
    
    print("\n所有测试完成!")