import re
from typing import Dict

class TextCleaner:
    def clean(self, text: str, file_type: str) -> str:
        """清洗文本内容"""
        # 去除无关注释
        text = self._remove_irrelevant_comments(text, file_type)
        
        # 修复断行
        text = self._fix_line_breaks(text)
        
        # 标准化术语
        text = self._standardize_terms(text)
        
        # 统一单位表示
        text = self._standardize_units(text)
            
        return text
    
    def _remove_irrelevant_comments(self, text: str, file_type: str) -> str:
        """去除无关注释（TODO、FIXME等）"""
        if file_type in ['java', 'python']:
            # 删除单行注释中的 TODO、FIXME、HACK 等标记
            text = re.sub(r'//\s*(TODO|FIXME|HACK).*', '', text)
            # 删除多行注释（/* ... */）
            text = re.sub(r'/\*.*?\*/', '', text, flags=re.DOTALL)
        elif file_type == 'java':
            # 特殊处理Java中的特定注释标记
            text = re.sub(r'//\s*(XXX|TODO|FIXME|HACK).*', '', text)
        elif file_type == 'python':
            # 特殊处理Python中的特定注释标记
            text = re.sub(r'#\s*(TODO|FIXME|HACK).*', '', text)
        
        return text
    
    def _fix_line_breaks(self, text: str) -> str:
        """修复代码断行"""
        # 修复被换行符分割的单词
        text = re.sub(r'([a-zA-Z])-?\n([a-zA-Z])', r'\1\2', text)
        # 修复在连字符处断开的单词
        text = re.sub(r'(\w+)-\s*\n(\w+)', r'\1\2', text)
        return text
    
    def _standardize_terms(self, text: str) -> str:
        """标准化技术术语"""
        replacements: Dict[str, str] = {
            '仓库': '仓储',
            '仓储': '仓储',  # 确保一致性
            '仓库管理': '仓储管理',
            '仓库系统': '仓储系统'
        }
        for old, new in replacements.items():
            text = text.replace(old, new)
        return text
    
    def _standardize_units(self, text: str) -> str:
        """统一单位表示"""
        # 统一公斤单位表示
        text = re.sub(r'\bkg\b', '公斤', text, flags=re.IGNORECASE)
        text = re.sub(r'\bKG\b', '公斤', text)
        # 统一吨单位表示
        text = re.sub(r'\bton\b', '吨', text, flags=re.IGNORECASE)
        text = re.sub(r'\bTON\b', '吨', text)
        return text