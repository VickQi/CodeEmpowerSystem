#!/usr/bin/env python3

import os
import sys
import json
import click
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from loader import DocumentLoader
from cleaner import TextCleaner
from sanitizer import Sanitizer
from chunker import SemanticChunker
from indexer import VectorIndexer
from embedder import MockEmbeddings, QwenEmbedder  # 更新导入
from retriver import Retriever
from prompt import PromptBuilder
from llm import LLMInterface
from parser import ResponseParser
from metric_validator import MetricValidator
from logger import logger
from settings import settings

# 参考指标（来自haiwise哲学）
REFERENCE_METRICS = {
    "relevance": 0.8,
    "completeness": 0.9,
    "accuracy": 0.95,
    "clarity": 0.85,
    "confidence": 0.8
}

@click.group()
def cli():
    """CodeEmpowerSystem CLI"""
    pass

@cli.command()
@click.option('--build-index', is_flag=True, help='构建向量索引')
@click.option('--question', help='查询问题')
@click.option('--agent', type=click.Choice(['dev', 'product', 'test']), 
              default='dev', help='智能体类型')
def run(build_index: bool, question: str, agent: str):
    """运行系统"""
    try:
        # 初始化系统组件
        # 使用新的embedder模块
        if settings.USE_MOCK or not settings.QWEN_API_KEY:
            embedder = MockEmbeddings()
        else:
            embedder = QwenEmbedder(settings.QWEN_API_KEY)
            
        # 正确设置索引路径
        index_path = os.path.join(settings.VECTOR_STORE_PATH, "faiss.index")
        indexer = VectorIndexer(embedder, index_path)
        retriever = Retriever(indexer)
        promptor = PromptBuilder()
        # 使用根据配置决定的模式（Mock或Qwen）
        llm = LLMInterface()
        parser = ResponseParser()
        validator = MetricValidator()
        cleaner = TextCleaner()
        sanitizer = Sanitizer()
        chunker = SemanticChunker()
        loader = DocumentLoader()  # 添加这行来定义loader变量
        
        if build_index:
            # 构建向量索引流程
            logger.info("开始构建向量索引...")
            
            # 1. 读取test_data目录下所有文档
            test_data_dir = Path("test_data")
            documents = []
            
            if not test_data_dir.exists():
                logger.error(f"测试数据目录不存在: {test_data_dir}")
                sys.exit(1)
            
            for file_path in test_data_dir.iterdir():
                if file_path.is_file():
                    try:
                        logger.info(f"正在加载文件: {file_path}")
                        loaded_docs = loader.load(str(file_path))
                        documents.extend(loaded_docs)
                        logger.info(f"成功加载文件: {file_path}")
                    except Exception as e:
                        logger.warning(f"加载文件失败 {file_path}: {str(e)}")
                        continue
            
            # 2. 清洗和脱敏文档
            processed_chunks = []
            for doc in documents:
                # 清洗文档内容
                cleaned_content = cleaner.clean(doc.content, doc.metadata.get('language', 'text'))
                
                # 脱敏处理
                sanitized_content = sanitizer.sanitize(cleaned_content)
                
                # 更新文档内容
                doc.content = sanitized_content
                
                # 分块处理
                chunks = chunker.split(
                    doc.content, 
                    doc.metadata.get('file_path', 'unknown'), 
                    doc.metadata.get('language', 'text')
                )
                
                processed_chunks.extend(chunks)
                logger.info(f"文件 {doc.metadata.get('file_path', 'unknown')} 处理完成，生成 {len(chunks)} 个块")
            
            # 3. 写入FAISS向量库
            if processed_chunks:
                logger.info(f"开始构建索引，共 {len(processed_chunks)} 个知识块")
                indexer.build_index(processed_chunks)
                logger.info("向量索引构建完成")
            else:
                logger.warning("没有处理任何文档块，索引未构建")
        elif question:
            # 查询流程
            # 4. 从磁盘中读取向量库索引文件
            logger.info("加载向量索引...")
            indexer.load_index()
            
            # 5. 检索相关文档
            logger.info(f"收到查询 (agent={agent}): {question}")
            retrieved_docs = retriever.retrieve(question, k=settings.TOP_K, 
                                              use_bm25=settings.USE_BM25)
            logger.debug(f"检索到 {len(retrieved_docs)} 个相关文档")
            
            # 6. 构建提示词
            messages = promptor.build_prompt(question, retrieved_docs, agent)
            
            # 7. 调用LLM
            raw_response = llm.invoke(messages)
            
            # 8. 解析响应
            payload = parser.parse(raw_response, retrieved_docs)
            
            # 9. 指标校验
            payload = validator.validate(payload, REFERENCE_METRICS)
            
            # 10. 输出结构化结果
            click.echo(json.dumps(payload, indent=2, ensure_ascii=False))
        else:
            click.echo("请指定 --build-index 构建索引或使用 --question 进行查询")
            sys.exit(1)
            
    except Exception as e:
        logger.exception("系统运行异常")
        click.echo(json.dumps({
            "answer": "系统暂时不可用，请稍后再试",
            "notes": "内部系统错误",
            "confidence": 0.0
        }, indent=2))
        sys.exit(1)

@cli.command()
@click.option('--q', '--question', required=True, help='查询问题')
@click.option('--agent', type=click.Choice(['dev', 'product', 'test']), 
              default='dev', help='智能体类型')
def query(question: str, agent: str):
    """执行知识查询"""
    try:
        # 初始化系统组件
        # 使用新的embedder模块
        if settings.USE_MOCK or not settings.QWEN_API_KEY:
            embedder = MockEmbeddings()
        else:
            embedder = QwenEmbedder(settings.QWEN_API_KEY)
            
        # 正确设置索引路径
        index_path = os.path.join(settings.VECTOR_STORE_PATH, "faiss.index")
        indexer = VectorIndexer(embedder, index_path)
        retriever = Retriever(indexer)
        promptor = PromptBuilder()
        # 使用根据配置决定的模式（Mock或Qwen）
        llm = LLMInterface()
        parser = ResponseParser()
        validator = MetricValidator()
        
        # 执行查询流程
        logger.info(f"收到查询 (agent={agent}): {question}")
        
        # 检索相关文档
        retrieved_docs = retriever.retrieve(question, k=settings.TOP_K, 
                                          use_bm25=settings.USE_BM25)
        logger.debug(f"检索到 {len(retrieved_docs)} 个相关文档")
        
        # 构建提示词
        messages = promptor.build_prompt(question, retrieved_docs, agent)
        
        # 调用LLM
        raw_response = llm.invoke(messages)
        
        # 解析响应
        payload = parser.parse(raw_response, retrieved_docs)
        
        # 指标校验
        payload = validator.validate(payload, REFERENCE_METRICS)
        
        # 输出结果
        click.echo(json.dumps(payload, indent=2, ensure_ascii=False))
        
    except Exception as e:
        logger.exception("查询处理异常")
        click.echo(json.dumps({
            "answer": "系统暂时不可用，请稍后再试",
            "notes": "内部系统错误",
            "confidence": 0.0
        }, indent=2))
        sys.exit(1)

if __name__ == '__main__':
    cli()