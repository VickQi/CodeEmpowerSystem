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
        加载PDF文件
        
        Args:
            file_path: PDF文件路径
            
        Returns:
            Document列表
        """
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                content = ""
                for page in pdf_reader.pages:
                    content += page.extract_text() + "\n"
                
                metadata = {
                    'source': 'pdf',
                    'file_path': file_path,
                    'language': 'pdf',
                    'page_count': len(pdf_reader.pages)
                }
                
                return [Document(content=content.strip(), metadata=metadata)]
        except Exception as e:
            raise Exception(f"Failed to load PDF file {file_path}: {str(e)}")
    
    def _load_markdown(self, file_path: str) -> List[Document]:
        """
        加载Markdown文件
        
        Args:
            file_path: Markdown文件路径
            
        Returns:
            Document列表
        """
        try:
            encoding = self._detect_encoding(file_path)
            with open(file_path, 'r', encoding=encoding) as file:
                content = file.read()
                
                # 可以选择是否转换为HTML
                # html = markdown.markdown(content)
                
                metadata = {
                    'source': 'markdown',
                    'file_path': file_path,
                    'language': 'markdown'
                }
                
                return [Document(content=content, metadata=metadata)]
        except Exception as e:
            raise Exception(f"Failed to load Markdown file {file_path}: {str(e)}")
    
    def _load_code(self, file_path: str) -> List[Document]:
        """
        加载代码文件（Java、Python等）
        
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
                
                metadata = {
                    'source': 'code',
                    'file_path': file_path,
                    'language': language
                }
                
                return [Document(content=content, metadata=metadata)]
        except Exception as e:
            raise Exception(f"Failed to load code file {file_path}: {str(e)}")
    
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