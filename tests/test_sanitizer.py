import unittest
from sanitizer import DataSanitizer


class TestDataSanitizer(unittest.TestCase):
    
    def setUp(self):
        self.sanitizer = DataSanitizer()
    
    def test_id_card_sanitization(self):
        text = "我的身份证号是110101199001011234，请妥善保管"
        expected = "我的身份证号是[REDACTED_ID]，请妥善保管"
        result = self.sanitizer.sanitize(text)
        self.assertEqual(result, expected)
    
    def test_phone_sanitization(self):
        text = "联系电话：13812345678"
        expected = "联系电话：138****5678"
        result = self.sanitizer.sanitize(text)
        self.assertEqual(result, expected)
    
    def test_email_sanitization(self):
        text = "邮箱地址：example@test.com"
        expected = "邮箱地址：[REDACTED_EMAIL]"
        result = self.sanitizer.sanitize(text)
        self.assertEqual(result, expected)
    
    def test_password_sanitization(self):
        text = "password = 'secret123'"
        expected = "password = \"[REDACTED]\""
        result = self.sanitizer.sanitize(text)
        self.assertEqual(result, expected)
    
    def test_credit_card_sanitization(self):
        text = "信用卡号：1234 5678 9012 3456"
        expected = "信用卡号：[REDACTED_CREDIT_CARD]"
        result = self.sanitizer.sanitize(text)
        self.assertEqual(result, expected)
    
    def test_passport_sanitization(self):
        text = "护照号码：AB12345678"
        expected = "护照号码：[REDACTED_PASSPORT]"
        result = self.sanitizer.sanitize(text)
        self.assertEqual(result, expected)
    
    def test_ssn_sanitization(self):
        text = "社会安全号码：123-45-6789"
        expected = "社会安全号码：[REDACTED_SSN]"
        result = self.sanitizer.sanitize(text)
        self.assertEqual(result, expected)
    
    def test_auth_token_sanitization(self):
        text = "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9"
        expected = "Authorization: [REDACTED_AUTH_TOKEN]"
        result = self.sanitizer.sanitize(text)
        self.assertEqual(result, expected)
    
    def test_secret_sanitization(self):
        text = "access_token = 'sk-1234567890abcdef'"
        expected = "[REDACTED_SECRET]"
        result = self.sanitizer.sanitize(text)
        self.assertEqual(result, expected)
    
    def test_non_string_input(self):
        # 测试非字符串输入
        result = self.sanitizer.sanitize(123)
        self.assertEqual(result, 123)
    
    def test_add_pattern(self):
        # 测试添加新的脱敏模式
        self.sanitizer.add_pattern(r'test\d+', '[REDACTED_TEST]')
        text = "test123abc"
        expected = "[REDACTED_TEST]abc"
        result = self.sanitizer.sanitize(text)
        self.assertEqual(result, expected)
    
    def test_sanitize_dict(self):
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
        result = self.sanitizer.sanitize_dict(data)
        self.assertEqual(result["id_card"], "[REDACTED_ID]")
        self.assertEqual(result["phone"], "138****5678")
        self.assertEqual(result["email"], "[REDACTED_EMAIL]")
        self.assertEqual(result["details"]["password"], 'password = "[REDACTED]"')
        self.assertEqual(result["details"]["token"], "[REDACTED_SECRET]")
    
    def test_sanitize_list(self):
        data = [
            "身份证号：110101199001011234",
            "手机号：13812345678",
            {
                "email": "test@example.com",
                "password": "secret123"
            }
        ]
        result = self.sanitizer.sanitize_list(data)
        self.assertEqual(result[0], "身份证号：[REDACTED_ID]")
        self.assertEqual(result[1], "手机号：138****5678")
        self.assertEqual(result[2]["email"], "[REDACTED_EMAIL]")
        self.assertEqual(result[2]["password"], 'password = "[REDACTED]"')


if __name__ == '__main__':
    unittest.main()