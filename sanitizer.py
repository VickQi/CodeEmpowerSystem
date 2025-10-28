import re


class DataSanitizer:
    def __init__(self):
        # 敏感信息模式
        self.patterns = [
            (r'\d{6}[1234]\d{8}[0-9xX]{4}', '[REDACTED_ID]'),  # 身份证号码
            (r'1[3-9]\d{9}', '138****5678'),  # 手机号码
            (r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', '[REDACTED_EMAIL]'),  # 邮箱地址
            (r'password\s*[:=]\s*[\'"][^\'"]*[\'"]', 'password = "[REDACTED]"'),  # 密码
            (r'\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}', '[REDACTED_CREDIT_CARD]'),  # 信用卡号
            (r'\b[A-Z]{2}\d{8}\b', '[REDACTED_PASSPORT]'),  # 护照号码
            (r'\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{3}', '[REDACTED_BANK_ACCOUNT]'),  # 银行卡号
            (r'\b\d{3}-\d{2}-\d{4}\b', '[REDACTED_SSN]'),  # 社会安全号码
            (r'(Bearer|bearer)\s+[A-Za-z0-9\-_]+', '[REDACTED_AUTH_TOKEN]'),  # 授权令牌
            (r'(access_token|token|secret)\s*[:=]\s*[\'"][^\'"]*[\'"]', '[REDACTED_SECRET]'),  # 访问令牌/密钥
        ]
    
    def sanitize(self, text: str) -> str:
        """数据脱敏处理"""
        if not isinstance(text, str):
            return text
            
        for pattern, replacement in self.patterns:
            text = re.sub(pattern, replacement, text)
        
        return text
    
    def add_pattern(self, pattern: str, replacement: str):
        """添加新的脱敏模式"""
        self.patterns.append((pattern, replacement))
    
    def sanitize_dict(self, data: dict) -> dict:
        """对字典中的值进行脱敏处理"""
        if not isinstance(data, dict):
            return data
            
        sanitized_data = {}
        for key, value in data.items():
            if isinstance(value, str):
                sanitized_data[key] = self.sanitize(value)
            elif isinstance(value, dict):
                sanitized_data[key] = self.sanitize_dict(value)
            elif isinstance(value, list):
                sanitized_data[key] = self.sanitize_list(value)
            else:
                sanitized_data[key] = value
        return sanitized_data
    
    def sanitize_list(self, data: list) -> list:
        """对列表中的元素进行脱敏处理"""
        if not isinstance(data, list):
            return data
            
        sanitized_data = []
        for item in data:
            if isinstance(item, str):
                sanitized_data.append(self.sanitize(item))
            elif isinstance(item, dict):
                sanitized_data.append(self.sanitize_dict(item))
            elif isinstance(item, list):
                sanitized_data.append(self.sanitize_list(item))
            else:
                sanitized_data.append(item)
        return sanitized_data