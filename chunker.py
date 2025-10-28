from typing import List
from dataclasses import dataclass
from typing import Any, Dict
import re
import logging
import os
from datetime import datetime

# 确保chunker日志记录器被正确初始化
def _setup_chunker_logger():
    """设置chunker模块的专用日志记录器"""
    try:
        # 尝试导入settings获取日志路径
        from settings import settings
        log_path = settings.LOG_PATH
    except (ImportError, ModuleNotFoundError):
        # 如果无法导入settings，则使用默认路径
        # 检查是否在测试目录下运行
        if 'tests' in os.getcwd():
            log_path = 'tests/logs/'
        else:
            log_path = 'logs/'
    
    # 确保日志目录存在
    os.makedirs(log_path, exist_ok=True)
    
    # 获取chunker日志记录器
    logger = logging.getLogger('chunker')
    logger.setLevel(logging.INFO)
    
    # 检查是否已经有文件处理器，避免重复添加
    chunker_log_file = os.path.join(log_path, 'chunker.log')
    if not any(isinstance(h, logging.FileHandler) and h.baseFilename.endswith('chunker.log') for h in logger.handlers):
        # 添加文件处理器
        file_handler = logging.FileHandler(chunker_log_file, encoding='utf-8')
        file_handler.setLevel(logging.INFO)
        
        # 设置格式
        formatter = logging.Formatter('[%(asctime)s] [%(levelname)s] [%(module)s] %(message)s')
        file_handler.setFormatter(formatter)
        
        # 添加处理器
        logger.addHandler(file_handler)
    
    return logger

# 初始化chunker日志记录器
_chunker_logger = _setup_chunker_logger()

@dataclass
class KnowledgeChunk:
    """知识片段类"""
    content: str
    source: str
    metadata: Dict[str, Any]

class SemanticChunker:
    def __init__(self, chunk_size: int = 500, overlap: int = 50):
        self.chunk_size = chunk_size
        self.overlap = overlap
        # 使用已初始化的chunker日志记录器
        self.logger = _chunker_logger
    
    def split(self, text: str, source: str, file_type: str) -> List[KnowledgeChunk]:
        """按语义边界切分文本"""
        if file_type in ['java', 'python']:
            return self._split_code(text, source, file_type)
        else:
            return self._split_document(text, source)
    
    def _split_code(self, text: str, source: str, file_type: str) -> List[KnowledgeChunk]:
        """代码按函数边界切分"""
        chunks = []
        chunk_id = 0
        
        if file_type == 'python':
            # Python函数/类边界分割
            # 匹配函数定义
            func_pattern = r'(def\s+\w+\s*\(.*?\)\s*:.*?)(?=def\s+\w+|\Z)'
            funcs = re.findall(func_pattern, text, re.DOTALL)
            
            # 如果没有找到函数，则将整个文本作为一个块
            if not funcs:
                funcs = [text]
                
            for func in funcs:
                # 如果函数太大，按行分割
                if len(func) > self.chunk_size:
                    lines = func.split('\n')
                    current_chunk = ""
                    for line in lines:
                        if len(current_chunk) + len(line) > self.chunk_size and current_chunk:
                            # 确保块不超过大小限制
                            if len(current_chunk.strip()) <= self.chunk_size:
                                chunk = KnowledgeChunk(
                                    content=current_chunk.strip(),
                                    source=source,
                                    metadata={
                                        "type": "code", 
                                        "language": file_type,
                                        "chunk_id": chunk_id
                                    }
                                )
                                chunks.append(chunk)
                                self.logger.info(f"chunker: chunk.size={len(chunk.content)}")
                                chunk_id += 1
                            # 保留重叠部分
                            current_chunk = current_chunk[-min(self.overlap, len(current_chunk)):] + "\n" + line + "\n"
                        else:
                            current_chunk += line + "\n"
                    
                    # 添加最后一个块
                    if current_chunk.strip() and len(current_chunk.strip()) <= self.chunk_size:
                        chunk = KnowledgeChunk(
                            content=current_chunk.strip(),
                            source=source,
                            metadata={
                                "type": "code", 
                                "language": file_type,
                                "chunk_id": chunk_id
                            }
                        )
                        chunks.append(chunk)
                        self.logger.info(f"chunker: chunk.size={len(chunk.content)}")
                        chunk_id += 1
                    # 如果最后一个块太大，强制分割
                    elif current_chunk.strip() and len(current_chunk.strip()) > self.chunk_size:
                        # 简单地按chunk_size分割
                        content = current_chunk.strip()
                        for i in range(0, len(content), self.chunk_size - self.overlap):
                            chunk_content = content[i:i + self.chunk_size]
                            if chunk_content:
                                chunk = KnowledgeChunk(
                                    content=chunk_content,
                                    source=source,
                                    metadata={
                                        "type": "code", 
                                        "language": file_type,
                                        "chunk_id": chunk_id
                                    }
                                )
                                chunks.append(chunk)
                                self.logger.info(f"chunker: chunk.size={len(chunk.content)}")
                                chunk_id += 1
                else:
                    chunk = KnowledgeChunk(
                        content=func.strip(),
                        source=source,
                        metadata={
                            "type": "code", 
                            "language": file_type,
                            "chunk_id": chunk_id
                        }
                    )
                    chunks.append(chunk)
                    self.logger.info(f"chunker: chunk.size={len(chunk.content)}")
                    chunk_id += 1
        
        elif file_type == 'java':
            # Java方法/类边界分割
            # 匹配方法定义
            method_pattern = r'((?:public|private|protected)?\s*(?:static)?\s*\w+\s+\w+\s*\([^)]*\)\s*\{[^}]*\})'
            methods = re.findall(method_pattern, text, re.DOTALL)
            
            # 如果没有找到方法，则将整个文本作为一个块
            if not methods:
                methods = [text]
                
            for method in methods:
                # 如果方法太大，按行分割
                if len(method) > self.chunk_size:
                    lines = method.split('\n')
                    current_chunk = ""
                    for line in lines:
                        if len(current_chunk) + len(line) > self.chunk_size and current_chunk:
                            # 确保块不超过大小限制
                            if len(current_chunk.strip()) <= self.chunk_size:
                                chunk = KnowledgeChunk(
                                    content=current_chunk.strip(),
                                    source=source,
                                    metadata={
                                        "type": "code", 
                                        "language": file_type,
                                        "chunk_id": chunk_id
                                    }
                                )
                                chunks.append(chunk)
                                self.logger.info(f"chunker: chunk.size={len(chunk.content)}")
                                chunk_id += 1
                            # 保留重叠部分
                            current_chunk = current_chunk[-min(self.overlap, len(current_chunk)):] + "\n" + line + "\n"
                        else:
                            current_chunk += line + "\n"
                    
                    # 添加最后一个块
                    if current_chunk.strip() and len(current_chunk.strip()) <= self.chunk_size:
                        chunk = KnowledgeChunk(
                            content=current_chunk.strip(),
                            source=source,
                            metadata={
                                "type": "code", 
                                "language": file_type,
                                "chunk_id": chunk_id
                            }
                        )
                        chunks.append(chunk)
                        self.logger.info(f"chunker: chunk.size={len(chunk.content)}")
                        chunk_id += 1
                    # 如果最后一个块太大，强制分割
                    elif current_chunk.strip() and len(current_chunk.strip()) > self.chunk_size:
                        # 简单地按chunk_size分割
                        content = current_chunk.strip()
                        for i in range(0, len(content), self.chunk_size - self.overlap):
                            chunk_content = content[i:i + self.chunk_size]
                            if chunk_content:
                                chunk = KnowledgeChunk(
                                    content=chunk_content,
                                    source=source,
                                    metadata={
                                        "type": "code", 
                                        "language": file_type,
                                        "chunk_id": chunk_id
                                    }
                                )
                                chunks.append(chunk)
                                self.logger.info(f"chunker: chunk.size={len(chunk.content)}")
                                chunk_id += 1
                else:
                    chunk = KnowledgeChunk(
                        content=method.strip(),
                        source=source,
                        metadata={
                            "type": "code", 
                            "language": file_type,
                            "chunk_id": chunk_id
                        }
                    )
                    chunks.append(chunk)
                    self.logger.info(f"chunker: chunk.size={len(chunk.content)}")
                    chunk_id += 1
        
        return chunks
    
    def _split_document(self, text: str, source: str) -> List[KnowledgeChunk]:
        """文档按章节切分"""
        chunks = []
        chunk_id = 0
        
        # 按段落分割文档
        paragraphs = re.split(r'\n\s*\n', text)
        
        current_chunk = ""
        current_section = ""  # 跟踪当前章节
        
        for paragraph in paragraphs:
            # 清理段落
            paragraph = paragraph.strip()
            if not paragraph:
                continue
                
            # 检查是否是标题
            is_heading = bool(re.match(r'^[#]+.*$', paragraph) or re.match(r'^.*\n[=-]+$', paragraph))
            
            # 如果是标题，更新当前章节
            if is_heading:
                current_section = paragraph
            
            # 如果添加这个段落会超出块大小，则保存当前块并开始新块
            if len(current_chunk) + len(paragraph) > self.chunk_size and current_chunk:
                # 确保块不超过大小限制
                if len(current_chunk.strip()) <= self.chunk_size:
                    chunk = KnowledgeChunk(
                        content=current_chunk.strip(),
                        source=source,
                        metadata={
                            "type": "document",
                            "chunk_id": chunk_id,
                            "section": current_section
                        }
                    )
                    chunks.append(chunk)
                    self.logger.info(f"chunker: chunk.size={len(chunk.content)}")
                    chunk_id += 1
                # 如果有重叠，保留部分内容
                if self.overlap > 0:
                    # 找到合适的重叠点（最后一个句子或指定字符数）
                    overlap_start = max(0, len(current_chunk) - min(self.overlap, len(current_chunk)))
                    current_chunk = current_chunk[overlap_start:] + "\n" + paragraph + "\n"
                else:
                    current_chunk = paragraph + "\n"
            else:
                current_chunk += paragraph + "\n"
        
        # 添加最后一个块
        if current_chunk.strip():
            # 如果最后一个块太大，强制分割
            if len(current_chunk.strip()) > self.chunk_size:
                content = current_chunk.strip()
                for i in range(0, len(content), self.chunk_size - self.overlap):
                    chunk_content = content[i:i + self.chunk_size]
                    if chunk_content:
                        chunk = KnowledgeChunk(
                            content=chunk_content,
                            source=source,
                            metadata={
                                "type": "document",
                                "chunk_id": chunk_id,
                                "section": current_section
                            }
                        )
                        chunks.append(chunk)
                        self.logger.info(f"chunker: chunk.size={len(chunk.content)}")
                        chunk_id += 1
            else:
                chunk = KnowledgeChunk(
                    content=current_chunk.strip(),
                    source=source,
                    metadata={
                        "type": "document",
                        "chunk_id": chunk_id,
                        "section": current_section
                    }
                )
                chunks.append(chunk)
                self.logger.info(f"chunker: chunk.size={len(chunk.content)}")
                chunk_id += 1
        
        return chunks