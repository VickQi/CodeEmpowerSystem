#!/usr/bin/env python3
"""
DataSanitizer测试文件
"""

import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from sanitizer import DataSanitizer

def test_id_card_sanitization():
    """测试身份证号脱敏"""
    sanitizer = DataSanitizer()
    text = "我的身份证号是110101199001011234，请妥善保管"
    expected = "我的身份证号是[REDACTED_ID]，请妥善保管"
    result = sanitizer.sanitize(text)
    assert result == expected
    print("✓ 身份证号脱敏测试通过")

def test_phone_sanitization():
    """测试手机号脱敏"""
    sanitizer = DataSanitizer()
    text = "联系电话：13812345678"
    expected = "联系电话：138****5678"
    result = sanitizer.sanitize(text)
    assert result == expected
    print("✓ 手机号脱敏测试通过")

def test_email_sanitization():
    """测试邮箱地址脱敏"""
    sanitizer = DataSanitizer()
    text = "邮箱地址：example@test.com"
    expected = "邮箱地址：[REDACTED_EMAIL]"
    result = sanitizer.sanitize(text)
    assert result == expected
    print("✓ 邮箱地址脱敏测试通过")

def test_password_sanitization():
    """测试密码脱敏"""
    sanitizer = DataSanitizer()
    text = "password = 'secret123'"
    expected = "password = \"[REDACTED]\""
    result = sanitizer.sanitize(text)
    assert result == expected
    print("✓ 密码脱敏测试通过")

def test_credit_card_sanitization():
    """测试信用卡号脱敏"""
    sanitizer = DataSanitizer()
    text = "信用卡号：1234 5678 9012 3456"
    expected = "信用卡号：[REDACTED_CREDIT_CARD]"
    result = sanitizer.sanitize(text)
    assert result == expected
    print("✓ 信用卡号脱敏测试通过")

def test_passport_sanitization():
    """测试护照号码脱敏"""
    sanitizer = DataSanitizer()
    text = "护照号码：AB12345678"
    expected = "护照号码：[REDACTED_PASSPORT]"
    result = sanitizer.sanitize(text)
    assert result == expected
    print("✓ 护照号码脱敏测试通过")

def test_ssn_sanitization():
    """测试社会安全号码脱敏"""
    sanitizer = DataSanitizer()
    text = "社会安全号码：123-45-6789"
    expected = "社会安全号码：[REDACTED_SSN]"
    result = sanitizer.sanitize(text)
    assert result == expected
    print("✓ 社会安全号码脱敏测试通过")

def test_auth_token_sanitization():
    """测试授权令牌脱敏"""
    sanitizer = DataSanitizer()
    text = "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9"
    expected = "Authorization: [REDACTED_AUTH_TOKEN]"
    result = sanitizer.sanitize(text)
    assert result == expected
    print("✓ 授权令牌脱敏测试通过")

def test_secret_sanitization():
    """测试密钥脱敏"""
    sanitizer = DataSanitizer()
    text = "access_token = 'sk-1234567890abcdef'"
    expected = "[REDACTED_SECRET]"
    result = sanitizer.sanitize(text)
    assert result == expected
    print("✓ 密钥脱敏测试通过")

def test_non_string_input():
    """测试非字符串输入"""
    sanitizer = DataSanitizer()
    result = sanitizer.sanitize(123)
    assert result == 123
    print("✓ 非字符串输入测试通过")

def test_add_pattern():
    """测试添加新模式"""
    sanitizer = DataSanitizer()
    sanitizer.add_pattern(r'test\d+', '[REDACTED_TEST]')
    text = "test123abc"
    expected = "[REDACTED_TEST]abc"
    result = sanitizer.sanitize(text)
    assert result == expected
    print("✓ 添加新模式测试通过")

def test_sanitize_dict():
    """测试字典数据脱敏"""
    sanitizer = DataSanitizer()
    data = {
        "name": "张三",
        "id_card": "110101199001011234",
        "phone": "13812345678",
        "email": "test@example.com",
        "details": {
            "password": "mypassword123",
            "token": "sk-1234567890abcdef"
        }
    }
    result = sanitizer.sanitize_dict(data)
    assert result["id_card"] == "[REDACTED_ID]"
    assert result["phone"] == "138****5678"
    assert result["email"] == "[REDACTED_EMAIL]"
    assert result["details"]["password"] == 'password = "[REDACTED]"'
    assert result["details"]["token"] == "[REDACTED_SECRET]"
    print("✓ 字典数据脱敏测试通过")

def test_sanitize_list():
    """测试列表数据脱敏"""
    sanitizer = DataSanitizer()
    data = [
        "身份证号：110101199001011234",
        "手机号：13812345678",
        {
            "email": "test@example.com",
            "password": "secret123"
        }
    ]
    result = sanitizer.sanitize_list(data)
    assert result[0] == "身份证号：[REDACTED_ID]"
    assert result[1] == "手机号：138****5678"
    assert result[2]["email"] == "[REDACTED_EMAIL]"
    assert result[2]["password"] == 'password = "[REDACTED]"'
    print("✓ 列表数据脱敏测试通过")

if __name__ == "__main__":
    print("开始测试DataSanitizer...")
    print("-" * 30)
    
    test_id_card_sanitization()
    test_phone_sanitization()
    test_email_sanitization()
    test_password_sanitization()
    test_credit_card_sanitization()
    test_passport_sanitization()
    test_ssn_sanitization()
    test_auth_token_sanitization()
    test_secret_sanitization()
    test_non_string_input()
    test_add_pattern()
    test_sanitize_dict()
    test_sanitize_list()
    
    print("-" * 30)
    print("所有测试通过!")