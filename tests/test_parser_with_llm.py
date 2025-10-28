#!/usr/bin/env python3
"""
Parser模块结合大模型调用的测试文件
"""

import sys
import json
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
from parser import ResponseParser
from llm import LLMInterface
from prompt import PromptBuilder
from settings import settings

def test_parser_with_llm():
    """测试结合大模型调用的解析器"""
    print("开始测试结合大模型调用的解析器...")
    
    # 创建临时索引文件
    with tempfile.TemporaryDirectory() as tmp_dir:
        index_path = os.path.join(tmp_dir, "faiss.index")
        
        # 初始化组件
        loader = DocumentLoader()
        cleaner = TextCleaner()
        chunker = SemanticChunker()
        
        # 使用实际的嵌入器或Mock
        if settings.QWEN_API_KEY and not settings.USE_MOCK:
            embedder = QwenEmbedder(settings.QWEN_API_KEY)
        else:
            print("使用MockEmbedder进行测试")
            class MockEmbedder:
                def __init__(self):
                    self.dimension = 1536  # 与实际模型一致
                    
                def embed(self, text: str):
                    # 返回固定长度的模拟向量
                    return [0.1] * self.dimension
            embedder = MockEmbedder()
        
        indexer = VectorIndexer(embedder, index_path)
        retriever = Retriever(indexer)
        parser = ResponseParser()
        llm = LLMInterface()
        prompt_builder = PromptBuilder()
        
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
        
        # 构建索引
        print("开始构建向量索引...")
        indexer.build_index(all_chunks)
        print(f"索引构建完成，包含 {indexer.index.ntotal} 个向量")
        
        # 测试查询
        query = "介绍下海智物流？"
        print(f"\n开始查询 '{query}'...")
        
        # 检索相关文档
        retrieved_docs = retriever.retrieve(query, k=3, use_bm25=False)
        print(f"检索到 {len(retrieved_docs)} 个相关文档")
        
        # 打印检索到的文档内容
        print("\n检索到的文档:")
        for i, doc in enumerate(retrieved_docs):
            print(f"\n文档 {i+1}:")
            print(f"  来源: {doc.source}")
            print(f"  位置: {doc.location}")
            print(f"  得分: {doc.score}")
            print(f"  内容长度: {len(doc.content)} 字符")
            if doc.content:
                print(f"  内容预览: {doc.content[:100]}...")
            else:
                print(f"  内容: [空]")
        
        # 构建提示词
        messages = prompt_builder.build_prompt(query, retrieved_docs, 'dev')
        print(f"\n提示词构建完成，包含 {len(messages)} 条消息")
        
        # 打印实际的提示词内容
        print("\n实际发送给大模型的提示词:")
        print("=" * 50)
        prompt_content = messages[0]['content']
        print(prompt_content)
        print("=" * 50)
        
        # 检查提示词是否包含实际内容
        if "海智" in prompt_content or "物流" in prompt_content:
            print("\n✓ 提示词中包含了实际的文档内容")
        else:
            print("\n✗ 提示词中没有实际的文档内容")
        
        # 调用LLM
        print("调用LLM...")
        raw_response = llm.invoke(messages)
        print(f"LLM响应完成，响应长度: {len(raw_response)} 字符")
        
        # 解析响应
        print("解析LLM响应...")
        parsed_response = parser.parse(raw_response, retrieved_docs)
        
        # 验证解析结果
        assert 'answer' in parsed_response, "解析结果应包含answer字段"
        assert 'confidence' in parsed_response, "解析结果应包含confidence字段"
        assert 'citations' in parsed_response, "解析结果应包含citations字段"
        assert 'key_points' in parsed_response, "解析结果应包含key_points字段"
        
        print("解析结果:")
        print(f"  回答: {parsed_response['answer'][:100]}...")
        print(f"  置信度: {parsed_response['confidence']}")
        print(f"  引用数量: {len(parsed_response['citations'])}")
        print(f"  关键点数量: {len(parsed_response['key_points'])}")
        
        # 打印完整回答
        print(f"\n完整回答:\n{parsed_response['answer']}")
        
        # 检查是否成功解析了回答
        if parsed_response['answer'] and parsed_response['answer'] != "无法生成有效回答":
            print("\n✓ 成功解析了大模型的回答")
        else:
            print("\n✗ 未能成功解析大模型的回答")
        
        print("✓ 结合大模型调用的解析器测试完成")

if __name__ == "__main__":
    print("开始测试Parser模块结合大模型调用...")
    print("=" * 50)
    
    test_parser_with_llm()
    
    print("\n" + "=" * 50)
    print("Parser模块结合大模型调用测试完成!")