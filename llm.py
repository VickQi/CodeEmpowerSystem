import json
from typing import List
from openai import OpenAI
import os

from settings import settings
from logger import logger

# 定义Message类型
Message = dict

class LLMInterface:
    def __init__(self):
        # 根据settings中的USE_MOCK配置决定是否使用Mock模式
        self.use_mock = settings.USE_MOCK
        self.client = None
        
        if not self.use_mock:
            # 检查是否有API密钥
            # 确保API密钥存在且不为空（去除前后空格后）
            api_key = str(settings.QWEN_API_KEY).strip() if settings.QWEN_API_KEY else ""
            if not api_key:
                logger.warning("QWEN_API_KEY未设置，将使用Mock模式")
                self.use_mock = True
            else:
                try:
                    # 初始化Qwen大模型客户端
                    self.client = OpenAI(
                        # 使用阿里云百炼API Key
                        api_key=api_key,
                        # 北京地域base_url
                        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
                    )
                    logger.info("Qwen大模型客户端初始化成功")
                except Exception as e:
                    logger.error(f"Qwen大模型客户端初始化失败: {e}")
                    self.use_mock = True
    
    def invoke(self, messages: List[Message]) -> str:
        """调用LLM获取响应"""
        if self.use_mock:
            logger.info("使用Mock模式调用LLM")
            return self._mock_invoke(messages)
        else:
            logger.info("使用Qwen大模型调用LLM")
            return self._qwen_invoke(messages)
    
    def _qwen_invoke(self, messages: List[Message]) -> str:
        """调用Qwen大模型"""
        try:
            completion = self.client.chat.completions.create(
                # 使用指定模型
                model="qwen3-next-80b-a3b-thinking",
                messages=messages,
            )
            # 返回JSON格式的响应
            return completion.model_dump_json()
        except Exception as e:
            logger.error(f"调用Qwen大模型失败: {e}")
            # 出错时回退到Mock模式
            return self._mock_invoke(messages)
    
    def _mock_invoke(self, messages: List[Message]) -> str:
        """Mock LLM实现"""
        # 从测试数据中返回预定义响应
        question = messages[-1]['content']
        
        # 检测是否需要指标校验
        if any(metric in question for metric in ['库存周转率', '履约率', '运输时间']):
            return self._generate_metric_response(question)
        
        # 通用响应
        return self._generate_generic_response(question)
    
    def _generate_metric_response(self, question: str) -> str:
        """生成带指标的响应（用于测试）"""
        # 从测试数据中获取匹配的响应
        # ...
        return json.dumps({
            "answer": "库存周转率 = 销售成本 / 平均库存。平均库存 = (期初库存 + 期末库存) / 2。",
            "citations": ["[InventoryService.java#L145-167]", "[物流系统设计规范#Section2.1]"],
            "used_metrics": [{"name": "inventory_turnover", "value": "销售成本 / 平均库存", "unit": "次/年"}],
            "notes": "",
            "confidence": 0.87
        })
    
    def _generate_generic_response(self, question: str) -> str:
        """生成通用响应（用于测试）"""
        return json.dumps({
            "answer": f"这是一个针对问题 '{question}' 的模拟回答。在实际部署中，这将由大语言模型生成。",
            "citations": ["[MockResponse]"],
            "used_metrics": [],
            "notes": "这是模拟响应",
            "confidence": 0.75
        })