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
            # 删除单行注释中的 TODO、FIXME、HACK、XXX 等标记
            text = re.sub(r'//\s*(TODO|FIXME|HACK|XXX).*', '', text)
            text = re.sub(r'#\s*(TODO|FIXME|HACK|XXX).*', '', text)
            # 删除多行注释（/* ... */）
            text = re.sub(r'/\*.*?\*/', '', text, flags=re.DOTALL)
        elif file_type == 'java':
            # 特殊处理Java中的特定注释标记
            text = re.sub(r'//\s*(XXX|TODO|FIXME|HACK).*', '', text)
        elif file_type == 'python':
            # 特殊处理Python中的特定注释标记
            text = re.sub(r'#\s*(TODO|FIXME|HACK|XXX).*', '', text)
        
        return text
    
    def _fix_line_breaks(self, text: str) -> str:
        """修复代码断行"""
        # 修复被换行符分割的英文单词
        text = re.sub(r'([a-zA-Z])-?\n([a-zA-Z])', r'\1\2', text)
        # 修复在连字符处断开的英文单词
        text = re.sub(r'(\w+)-\s*\n(\w+)', r'\1\2', text)
        return text
    
    def _standardize_terms(self, text: str) -> str:
        """标准化技术术语"""
        replacements: Dict[str, str] = {
            # 仓储相关术语
            '仓库管理': '仓储管理',  # 更具体的术语放在前面
            '仓库系统': '仓储系统',
            '仓储中心': '仓储',
            '仓储设施': '仓储',
            '仓库': '仓储',
            '仓储': '仓储',  # 确保一致性
            
            # 物流相关术语
            '物流管理': '物流',
            '物流系统': '物流',
            '物流服务': '物流',
            '物流网络': '物流',
            
            # 运输相关术语
            '运输管理': '运输',
            '运输系统': '运输',
            '运输服务': '运输',
            '货运': '运输',
            
            # 订单相关术语
            '订单管理': '订单',
            '订单系统': '订单',
            '订单处理': '订单',  # 更具体的术语放在前面
            
            # 库存相关术语
            '库存管理': '库存',
            '库存系统': '库存',
            '库存控制': '库存',
            '存货': '库存',
        }
        
        # 按照术语长度降序排列，确保长术语优先被替换
        sorted_replacements = sorted(replacements.items(), key=lambda x: len(x[0]), reverse=True)
        
        for old, new in sorted_replacements:
            text = text.replace(old, new)
        return text
    
    def _standardize_units(self, text: str) -> str:
        """统一单位表示"""
        # 统一公斤单位表示
        text = re.sub(r'(?<=\d)\s*[Kk][Gg](?=\W|$)', '公斤', text)
        text = re.sub(r'(?<=\W)[Kk][Gg](?=\W|$)', '公斤', text)
        
        # 统一吨单位表示
        text = re.sub(r'(?<=\d)\s*[Tt][Oo][Nn](?=\W|$)', '吨', text)
        text = re.sub(r'(?<=\W)[Tt][Oo][Nn](?=\W|$)', '吨', text)
        
        # 统一米单位表示 (需要特别注意，因为m很常见)
        text = re.sub(r'(?<=\d)\s*[Mm](?=\W|$)', '米', text)
        
        # 统一千米单位表示
        text = re.sub(r'(?<=\d)\s*[Kk][Mm](?=\W|$)', '千米', text)
        text = re.sub(r'(?<=\W)[Kk][Mm](?=\W|$)', '千米', text)
        
        # 统一厘米单位表示
        text = re.sub(r'(?<=\d)\s*[Cc][Mm](?=\W|$)', '厘米', text)
        text = re.sub(r'(?<=\W)[Cc][Mm](?=\W|$)', '厘米', text)
        
        return text