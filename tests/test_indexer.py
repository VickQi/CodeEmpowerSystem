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

# 初始化日志记录器
from logger import logger

from loader import DocumentLoader
from cleaner import TextCleaner
from chunker import SemanticChunker, KnowledgeChunk
from indexer import VectorIndexer
from embedder import MockEmbeddings, QwenEmbedder
from settings import settings

def test_indexer_with_mock_embeddings():
    """测试indexer使用MockEmbeddings"""
    # 临时设置为Mock模式
    original_use_mock = settings.USE_MOCK
    settings.USE_MOCK = True
    
    logger.info("开始测试indexer与MockEmbeddings...")
    print("开始测试indexer与MockEmbeddings...")
    
    # 初始化组件
    loader = DocumentLoader()
    cleaner = TextCleaner()
    chunker = SemanticChunker()
    embedder = MockEmbeddings()
    
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
        test_embedder = MockEmbeddings()
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
        new_indexer = VectorIndexer(MockEmbeddings(), tmp_index_file.name)
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
        
        print("✓ Indexer与MockEmbeddings测试通过")
        
        # 恢复原始设置
        settings.USE_MOCK = original_use_mock

def test_indexer_with_qwen_embeddings():
    """测试indexer使用QwenEmbedder（仅在有API密钥时执行）"""
    if not settings.QWEN_API_KEY:
        print("跳过QwenEmbedder测试（缺少QWEN_API_KEY）")
        return
    
    # 临时关闭Mock模式以测试QwenEmbedder
    original_use_mock = settings.USE_MOCK
    settings.USE_MOCK = False
    
    logger.info("开始测试indexer与QwenEmbedder...")
    print("开始测试indexer与QwenEmbedder...")
    
    # 初始化组件
    loader = DocumentLoader()
    cleaner = TextCleaner()
    chunker = SemanticChunker()
    embedder = QwenEmbedder()
    
    # 创建临时索引文件
    with tempfile.NamedTemporaryFile(delete=False) as tmp_index_file:
        indexer = VectorIndexer(embedder, tmp_index_file.name)
        
        # 获取test_data目录
        test_data_dir = project_root / "test_data"
        
        # 收集所有知识块（只取前2个以减少API调用）
        all_chunks = []
        chunk_count = 0
        
        # 遍历test_data目录中的所有文件
        for file_path in test_data_dir.iterdir():
            if file_path.is_file() and chunk_count < 2:  # 限制块数量
                try:
                    print(f"处理文件: {file_path.name}")
                    
                    # 加载文档
                    documents = loader.load(str(file_path))
                    
                    for doc in documents:
                        if chunk_count >= 2:  # 限制块数量
                            break
                            
                        # 清洗文本
                        file_type = doc.metadata.get('language', 'unknown')
                        cleaned_text = cleaner.clean(doc.content, file_type)
                        
                        # 切分文本
                        source = doc.metadata.get('file_path', str(file_path))
                        chunks = chunker.split(cleaned_text, source, file_type)
                        
                        # 只取前几个块
                        for chunk in chunks[:min(2, len(chunks))]:
                            if chunk_count >= 2:  # 限制块数量
                                break
                            all_chunks.append(chunk)
                            chunk_count += 1
                        
                except Exception as e:
                    print(f"处理文件 {file_path.name} 时出错: {e}")
                    continue
        
        if not all_chunks:
            print("没有生成任何知识块，跳过测试")
            # 恢复原始网络设置
            return
            
        print(f"总共生成了 {len(all_chunks)} 个知识块")
        
        # 检查前几个块的内容和维度
        print("检查前几个块的向量维度:")
        test_embedder = QwenEmbedder()
        for i, chunk in enumerate(all_chunks[:min(3, len(all_chunks))]):
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
            for i, chunk in enumerate(all_chunks[:min(5, len(all_chunks))]):  # 只测试前几个块
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
        new_indexer = VectorIndexer(QwenEmbedder(), tmp_index_file.name)
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
        
        print("✓ Indexer与QwenEmbedder测试通过")
        
        # 恢复原始设置
        settings.USE_MOCK = original_use_mock

if __name__ == "__main__":
    print("开始测试Indexer与不同Embedder的集成...")
    print("-" * 50)
    
    test_indexer_with_mock_embeddings()
    test_indexer_with_qwen_embeddings()
    
    print("-" * 50)
    print("所有集成测试通过!")