import json
from typing import List
from openai import OpenAI
import os
import re

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
            print(f"\n提示词构建完成，包含 {len(messages)} 条消息")
            # 打印实际的提示词内容
            print("\n实际发送给大模型的提示词:")
            print("=" * 50)
            prompt_content = messages[0]['content']
            print(prompt_content)
            print("=" * 50)

            # 统计提示词长度
            print(f"\n提示词长度: {len(prompt_content)} 字符")
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
        
        # 根据具体问题生成响应
        return self._generate_contextual_response(question, messages)
    
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
    
    def _generate_contextual_response(self, question: str, messages: List[Message]) -> str:
        """根据上下文生成响应"""
        # 获取提示词内容
        prompt_content = messages[0]['content']
        
        # 检查是否是关于"配送路线优化算法"的问题
        if "配送路线优化算法" in question or "optimize_delivery_route" in prompt_content:
            return json.dumps({
                "answer": "配送路线优化算法位于test_data/TMSTransportationPlanner.py文件中的optimize_delivery_route函数。该函数使用贪心算法实现基础路线优化，实际系统中还结合了'实时路由优化'（每5分钟更新路况）等更复杂技术。",
                "citations": ["test_data/TMSTransportationPlanner.py#unknown"],
                "key_points": [
                    "配送路线优化算法实现在TMSTransportationPlanner.py文件中",
                    "函数名为optimize_delivery_route",
                    "使用贪心算法进行简单的路线优化",
                    "实际系统中结合了实时路由优化技术"
                ],
                "notes": "来自基于上下文的模拟响应",
                "confidence": 0.9,
                "used_metrics": []
            })
        
        # 检查是否是关于错误码的问题
        if "错误码" in prompt_content:
            return json.dumps({
                "answer": "根据您提供的上下文（test_data/LogisticsAPI.md 中的 2.2 通用错误码定义表格），系统定义了以下核心错误码：ERR_0001（参数缺失或无效）、ERR_0002（资源未找到）、ERR_0003（系统内部错误）、ERR_0004（权限不足）、ERR_0005（请求超时）。这些错误码用于标准化系统异常处理和故障排查流程。",
                "citations": ["test_data/LogisticsAPI.md#unknown"],
                "key_points": [
                    "ERR_0001：参数缺失或无效",
                    "ERR_0002：资源未找到",
                    "ERR_0003：系统内部错误",
                    "ERR_0004：权限不足",
                    "ERR_0005：请求超时"
                ],
                "notes": "基于文档上下文的模拟响应",
                "confidence": 0.85,
                "used_metrics": []
            })
        
        # 通用响应
        # 尝试从提示词中提取一些关键信息
        sources = re.findall(r'\[(.*?)\]', prompt_content)
        citations = [f"[{source}]" for source in sources[:3]] if sources else ["[MockResponse]"]
        
        return json.dumps({
            "answer": f"基于提供的上下文信息，针对问题'{question}'的回答如下：系统包含相关实现，具体细节请参考引用的文档。",
            "citations": citations,
            "key_points": [f"问题涉及: {question}", "系统中有相关实现", "详见引用文档"],
            "notes": "基于上下文的模拟响应",
            "confidence": 0.8,
            "used_metrics": []
        })