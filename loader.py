import os
from dataclasses import dataclass
from typing import List, Dict, Any

import PyPDF2
import chardet


@dataclass
class Document:
    """文档类，包含内容和元数据"""
    content: str
    metadata: Dict[str, Any]
    start_line: int = 0
    end_line: int = 0

class UnsupportedFormatError(Exception):
    """不支持的文件格式异常"""
    pass

class DocumentLoader:
    """文档加载器，支持多种格式文件加载"""
    
    def __init__(self):
        self.supported_formats = {
            '.pdf': self._load_pdf,
            '.md': self._load_markdown,
            '.markdown': self._load_markdown,
            '.java': self._load_code,
            '.py': self._load_code,
        }
    
    def load(self, file_path: str) -> List[Document]:
        """
        加载文件并返回Document列表
        
        Args:
            file_path: 文件路径
            
        Returns:
            Document列表
            
        Raises:
            UnsupportedFormatError: 不支持的文件格式
            FileNotFoundError: 文件不存在
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        ext = os.path.splitext(file_path)[1].lower()
        
        if ext in self.supported_formats:
            return self.supported_formats[ext](file_path)
        else:
            raise UnsupportedFormatError(f"Unsupported file format: {ext}")
    
    def _load_pdf(self, file_path: str) -> List[Document]:
        """
        加载PDF文件，按页生成 Document 对象
        
        Args:
            file_path: PDF文件路径
            
        Returns:
            Document列表
        """
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                documents = []
                
                for page_num, page in enumerate(pdf_reader.pages):
                    content = page.extract_text()
                    
                    metadata = {
                        'source': 'pdf',
                        'file_path': file_path,
                        'language': 'pdf',
                        'page_number': page_num + 1,
                        'start_line': 1,  # PDF没有行号概念，这里设为1
                        'end_line': len(content.split('\n'))  # 估算行数
                    }
                    
                    documents.append(Document(
                        content=content.strip(), 
                        metadata=metadata,
                        start_line=1,
                        end_line=len(content.split('\n'))
                    ))
                
                return documents
        except Exception as e:
            raise Exception(f"Failed to load PDF file {file_path}: {str(e)}")
    
    def _load_code(self, file_path: str) -> List[Document]:
        """
        加载代码文件（Java、Python等），按函数/方法边界生成 Document 对象
        
        Args:
            file_path: 代码文件路径
            
        Returns:
            Document列表
        """
        try:
            encoding = self._detect_encoding(file_path)
            with open(file_path, 'r', encoding=encoding) as file:
                content = file.read()
                
                ext = os.path.splitext(file_path)[1].lower()
                language = 'java' if ext == '.java' else 'python' if ext == '.py' else 'unknown'
                
                # 按函数/方法边界分割内容
                documents = []
                if language == 'java':
                    # Java按类或方法分割
                    # 简化实现：按行分割并识别类/方法开始行
                    lines = content.split('\n')
                    current_doc_lines = []
                    current_start_line = 1
                    
                    for i, line in enumerate(lines):
                        line_num = i + 1
                        stripped_line = line.strip()
                        
                        # 检查是否是类或方法定义的开始
                        if (stripped_line.startswith('class ') or 
                            stripped_line.startswith('public ') or 
                            stripped_line.startswith('private ') or 
                            stripped_line.startswith('protected ') or
                            stripped_line.startswith('static ')):
                            
                            # 如果已经有内容，保存为一个Document
                            if current_doc_lines:
                                doc_content = '\n'.join(current_doc_lines)
                                metadata = {
                                    'source': 'code',
                                    'file_path': file_path,
                                    'language': language,
                                    'start_line': current_start_line,
                                    'end_line': line_num - 1
                                }
                                documents.append(Document(
                                    content=doc_content, 
                                    metadata=metadata,
                                    start_line=current_start_line,
                                    end_line=line_num - 1
                                ))
                            
                            # 开始新的Document
                            current_doc_lines = [line]
                            current_start_line = line_num
                        else:
                            current_doc_lines.append(line)
                    
                    # 保存最后一个Document
                    if current_doc_lines:
                        doc_content = '\n'.join(current_doc_lines)
                        metadata = {
                            'source': 'code',
                            'file_path': file_path,
                            'language': language,
                            'start_line': current_start_line,
                            'end_line': len(lines)
                        }
                        documents.append(Document(
                            content=doc_content,
                            metadata=metadata,
                            start_line=current_start_line,
                            end_line=len(lines)
                        ))
                        
                elif language == 'python':
                    # Python按函数或类分割
                    lines = content.split('\n')
                    current_doc_lines = []
                    current_start_line = 1
                    
                    for i, line in enumerate(lines):
                        line_num = i + 1
                        stripped_line = line.strip()
                        
                        # 检查是否是类或函数定义的开始
                        if (stripped_line.startswith('class ') or 
                            stripped_line.startswith('def ')):
                            
                            # 如果已经有内容，保存为一个Document
                            if current_doc_lines:
                                doc_content = '\n'.join(current_doc_lines)
                                metadata = {
                                    'source': 'code',
                                    'file_path': file_path,
                                    'language': language,
                                    'start_line': current_start_line,
                                    'end_line': line_num - 1
                                }
                                documents.append(Document(
                                    content=doc_content,
                                    metadata=metadata,
                                    start_line=current_start_line,
                                    end_line=line_num - 1
                                ))
                            
                            # 开始新的Document
                            current_doc_lines = [line]
                            current_start_line = line_num
                        else:
                            current_doc_lines.append(line)
                    
                    # 保存最后一个Document
                    if current_doc_lines:
                        doc_content = '\n'.join(current_doc_lines)
                        metadata = {
                            'source': 'code',
                            'file_path': file_path,
                            'language': language,
                            'start_line': current_start_line,
                            'end_line': len(lines)
                        }
                        documents.append(Document(
                            content=doc_content,
                            metadata=metadata,
                            start_line=current_start_line,
                            end_line=len(lines)
                        ))
                else:
                    # 其他语言按整个文件处理
                    metadata = {
                        'source': 'code',
                        'file_path': file_path,
                        'language': language,
                        'start_line': 1,
                        'end_line': len(content.split('\n'))
                    }
                    documents.append(Document(
                        content=content,
                        metadata=metadata,
                        start_line=1,
                        end_line=len(content.split('\n'))
                    ))
                
                return documents
        except Exception as e:
            raise Exception(f"Failed to load code file {file_path}: {str(e)}")

    def _load_markdown(self, file_path: str) -> List[Document]:
        """
        加载Markdown文件，按章节/段落生成 Document 对象
        
        Args:
            file_path: Markdown文件路径
            
        Returns:
            Document列表
        """
        try:
            encoding = self._detect_encoding(file_path)
            with open(file_path, 'r', encoding=encoding) as file:
                content = file.read()
                
                # 按章节分割（以标题为界）
                documents = []
                lines = content.split('\n')
                current_doc_lines = []
                current_start_line = 1
                
                for i, line in enumerate(lines):
                    line_num = i + 1
                    stripped_line = line.strip()
                    
                    # 检查是否是标题（以#开头）
                    if stripped_line.startswith('#'):
                        # 如果已经有内容，保存为一个Document
                        if current_doc_lines:
                            doc_content = '\n'.join(current_doc_lines)
                            metadata = {
                                'source': 'markdown',
                                'file_path': file_path,
                                'language': 'markdown',
                                'start_line': current_start_line,
                                'end_line': line_num - 1
                            }
                            documents.append(Document(
                                content=doc_content,
                                metadata=metadata,
                                start_line=current_start_line,
                                end_line=line_num - 1
                            ))
                        
                        # 开始新的Document
                        current_doc_lines = [line]
                        current_start_line = line_num
                    else:
                        current_doc_lines.append(line)
                
                # 保存最后一个Document
                if current_doc_lines:
                    doc_content = '\n'.join(current_doc_lines)
                    metadata = {
                        'source': 'markdown',
                        'file_path': file_path,
                        'language': 'markdown',
                        'start_line': current_start_line,
                        'end_line': len(lines)
                    }
                    documents.append(Document(
                        content=doc_content,
                        metadata=metadata,
                        start_line=current_start_line,
                        end_line=len(lines)
                    ))
                
                return documents
        except Exception as e:
            raise Exception(f"Failed to load Markdown file {file_path}: {str(e)}")

    def _detect_encoding(self, file_path: str) -> str:
        """
        检测文件编码
        
        Args:
            file_path: 文件路径
            
        Returns:
            编码格式
        """
        try:
            with open(file_path, 'rb') as file:
                raw_data = file.read()
                result = chardet.detect(raw_data)
                return result['encoding'] or 'utf-8'
        except:
            return 'utf-8'
if __name__ == '__main__':
    loader = DocumentLoader()
    documents = loader.load('test_data/HaizhiLogistics.pdf')
    print(documents)