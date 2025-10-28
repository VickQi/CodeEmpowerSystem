#!/usr/bin/env python3
"""
Indexer集成测试文件
验证indexer将test_data中的数据向量化并存储到FAISS向量库
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
from chunker import SemanticChunker, KnowledgeChunk
from indexer import QwenEmbedder, VectorIndexer
from settings import Settings

def test_indexer_with_test_data():
    """测试indexer将test_data中的数据向量化并存储到FAISS向量库"""
    print("开始测试indexer与test_data的集成...")
    
    # 初始化组件
    loader = DocumentLoader()
    cleaner = TextCleaner()
    chunker = SemanticChunker()
    
    # 获取API密钥
    settings = Settings()
    if not settings.QWEN_API_KEY:
        print("警告: QWEN_API_KEY未设置，将使用MockEmbedder")
        # 使用MockEmbedder替代QwenEmbedder进行测试，避免API调用
        class MockEmbedder:
            def __init__(self):
                self.dimension = 1536  # 与实际模型一致
                
            def embed(self, text: str):
                # 返回固定长度的模拟向量
                return [0.1] * self.dimension
        embedder = MockEmbedder()
    else:
        embedder = QwenEmbedder(settings.QWEN_API_KEY)
    
    # 创建临时索引文件
    with tempfile.NamedTemporaryFile(delete=False) as tmp_index_file:
        indexer = VectorIndexer(embedder, tmp_index_file.name)
        
        # 获取test_data目录
        test_data_dir = project_root / "test_data"
        
        # 收集所有知识块
        all_chunks = []
        
        # 遍历test_data目录中的所有文件
        for file_path in test_data_dir.iterdir():
            if file_path.is_file():
                try:
                    print(f"处理文件: {file_path.name}")
                    
                    # 加载文档
                    documents = loader.load(str(file_path))
                    
                    for doc in documents:
                        # 清洗文本
                        file_type = doc.metadata.get('language', 'unknown')
                        cleaned_text = cleaner.clean(doc.content, file_type)
                        
                        # 切分文本
                        source = doc.metadata.get('file_path', str(file_path))
                        chunks = chunker.split(cleaned_text, source, file_type)
                        all_chunks.extend(chunks)
                        
                except Exception as e:
                    print(f"处理文件 {file_path.name} 时出错: {e}")
                    continue
        
        print(f"总共生成了 {len(all_chunks)} 个知识块")
        
        # 检查前几个块的内容和维度
        print("检查前几个块的向量维度:")
        if not settings.QWEN_API_KEY:
            test_embedder = type(embedder)()
        else:
            test_embedder = QwenEmbedder(settings.QWEN_API_KEY)
            
        for i, chunk in enumerate(all_chunks[:3]):
            vector = test_embedder.embed(chunk.content)
            print(f"  块 {i+1} 向量维度: {len(vector)}")
        
        # 构建索引
        print("开始构建向量索引...")
        try:
            indexer.build_index(all_chunks)
            print("索引构建完成")
        except Exception as e:
            print(f"索引构建失败: {e}")
            # 尝试逐个添加块来定位问题
            print("尝试逐个添加块来定位问题...")
            for i, chunk in enumerate(all_chunks[:5]):  # 只测试前5个块
                try:
                    print(f"  添加块 {i+1}: {chunk.source}")
                    vector = test_embedder.embed(chunk.content)
                    print(f"    向量维度: {len(vector)}")
                except Exception as chunk_error:
                    print(f"    块 {i+1} 处理失败: {chunk_error}")
            raise e
        
        # 验证索引已创建
        assert indexer.index is not None, "索引未正确创建"
        assert len(indexer.doc_ids) == len(all_chunks), "文档ID数量与块数量不匹配"
        
        print(f"索引构建完成，包含 {indexer.index.ntotal} 个向量")
        
        # 测试保存索引
        print("测试保存索引...")
        indexer.save_index()
        
        # 验证索引文件已创建
        assert os.path.exists(tmp_index_file.name), "索引文件未创建"
        assert os.path.exists(tmp_index_file.name + '.ids'), "索引ID文件未创建"
        
        # 测试加载索引
        print("测试加载索引...")
        # 根据是否有API密钥选择embedder
        if not settings.QWEN_API_KEY:
            test_embedder = type(embedder)()
        else:
            test_embedder = QwenEmbedder(settings.QWEN_API_KEY)
        new_indexer = VectorIndexer(test_embedder, tmp_index_file.name)
        new_indexer.load_index()
        
        assert new_indexer.index is not None, "索引未正确加载"
        assert len(new_indexer.doc_ids) == len(all_chunks), "加载的文档ID数量不正确"
        assert new_indexer.index.ntotal == len(all_chunks), "加载的索引向量数量不正确"
        
        print(f"索引加载成功，包含 {new_indexer.index.ntotal} 个向量")
        
        # 测试搜索功能
        print("测试搜索功能...")
        search_results = new_indexer.search("物流管理", k=3)
        assert isinstance(search_results, list), "搜索结果应为列表"
        print(f"搜索返回 {len(search_results)} 个结果")
        
        # 清理临时文件
        os.unlink(tmp_index_file.name)
        os.unlink(tmp_index_file.name + '.ids')
        
        print("✓ Indexer与test_data集成测试通过")

if __name__ == "__main__":
    print("开始测试Indexer与test_data的集成...")
    print("-" * 50)
    
    test_indexer_with_test_data()
    
    print("-" * 50)
    print("所有集成测试通过!")