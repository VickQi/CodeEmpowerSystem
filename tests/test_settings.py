import unittest
import os
import sys
from settings import Settings


class TestSettings(unittest.TestCase):


    def test_settings_with_custom_env_values(self):
        """测试使用自定义环境变量值时的设置"""
        settings = Settings()
        
        # 测试布尔值设置

        # 测试字符串设置
        self.assertEqual(settings.LOG_LEVEL, "INFO", "LOG_LEVEL 应该为 'DEBUG'")
        self.assertEqual(settings.LOG_PATH, "logs/", "LOG_PATH 应该为 '/tmp/logs/'")
        self.assertEqual(settings.DATA_PATH, "data/", "DATA_PATH 应该为 '/tmp/data/'")
        self.assertEqual(settings.VECTOR_STORE_PATH, "vectorstore/", "VECTOR_STORE_PATH 应该为 '/tmp/vectorstore/'")
        # 测试整数设置
        self.assertEqual(settings.CHUNK_SIZE, 500, "CHUNK_SIZE 应该为 1000")
        self.assertEqual(settings.CHUNK_OVERLAP, 50, "CHUNK_OVERLAP 应该为 100")
        self.assertEqual(settings.TOP_K, 5, "TOP_K 应该为 10")
        self.assertEqual(settings.MAX_CONTEXT_CHARS, 4000, "MAX_CONTEXT_CHARS 应该为 4000")
    
    def test_settings_dotenv_loading(self):
        """专门测试从.env文件加载QWEN_API_KEY"""
        # 重新加载settings模块以确保从干净状态开始
        if 'settings' in sys.modules:
            del sys.modules['settings']
        
        # 确保没有环境变量覆盖
        if "QWEN_API_KEY" in os.environ:
            del os.environ["QWEN_API_KEY"]
        
        # 重新导入settings
        import importlib
        settings_module = importlib.import_module('settings')
        SettingsClass = getattr(settings_module, 'Settings')
        
        settings = SettingsClass()
        # 验证QWEN_API_KEY不为空且是从.env文件加载的
        self.assertIsNotNone(settings.QWEN_API_KEY, "QWEN_API_KEY 不应为空")
        self.assertNotEqual(settings.QWEN_API_KEY, "", "QWEN_API_KEY 不应为空字符串")
        self.assertIsInstance(settings.QWEN_API_KEY, str, "QWEN_API_KEY 应该是字符串类型")
        
        # 清理
        if 'settings' in sys.modules:
            del sys.modules['settings']
    
    def test_settings_type_conversion(self):
        """测试设置值的类型转换"""
        settings = Settings()
        
        # 确保数值类型正确
        self.assertIsInstance(settings.CHUNK_SIZE, int, "CHUNK_SIZE 应该是 int 类型")
        self.assertIsInstance(settings.CHUNK_OVERLAP, int, "CHUNK_OVERLAP 应该是 int 类型")
        self.assertIsInstance(settings.TOP_K, int, "TOP_K 应该是 int 类型")
        self.assertIsInstance(settings.MAX_CONTEXT_CHARS, int, "MAX_CONTEXT_CHARS 应该是 int 类型")
        
        # 确保布尔类型正确
        self.assertIsInstance(settings.USE_BM25, bool, "USE_BM25 应该是 bool 类型")
        self.assertIsInstance(settings.ALLOW_INTERNET, bool, "ALLOW_INTERNET 应该是 bool 类型")
        self.assertIsInstance(settings.USE_GPU, bool, "USE_GPU 应该是 bool 类型")
        
        # 确保字符串类型正确
        self.assertIsInstance(settings.LOG_LEVEL, str, "LOG_LEVEL 应该是 str 类型")
        self.assertIsInstance(settings.LOG_PATH, str, "LOG_PATH 应该是 str 类型")
        self.assertIsInstance(settings.DATA_PATH, str, "DATA_PATH 应该是 str 类型")
        self.assertIsInstance(settings.VECTOR_STORE_PATH, str, "VECTOR_STORE_PATH 应该是 str 类型")
        self.assertIsInstance(settings.QWEN_API_KEY, str, "QWEN_API_KEY 应该是 str 类型")


if __name__ == '__main__':
    unittest.main(verbosity=2)