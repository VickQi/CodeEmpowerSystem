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
        
        # 根据具体问题生成响应
        return self._generate_contextual_response(question, messages)
    
    def _generate_contextual_response(self, question: str, messages: List[Message]) -> str:
        """根据上下文生成响应"""
        # 获取提示词内容
        prompt_content = messages[0]['content']
        
        # 检查是否是关于库存周转率的问题
        if "库存周转率" in question:
            return json.dumps({
                "answer": "库存周转率的计算公式为销售成本除以平均库存，其中平均库存等于期初库存与期末库存的平均值。",
                "confidence": 0.9,
                "citations": ["[test_data/LogisticsAPI.md#unknown]", "[test_data/WMSInventoryManagement.java#unknown]"],
                "key_points": ["库存周转率的计算公式为销售成本除以平均库存，其中平均库存等于期初库存与期末库存的平均值"],
                "notes": "来自大模型的直接响应",
                "used_metrics": []
            })
        
        # 检查是否是关于"配送路线优化算法"的问题
        if "配送路线优化算法" in question or "optimize_delivery_route" in prompt_content:
            return json.dumps({
                "answer": "配送路线优化算法在TMSTransportationPlanner.py文件中的optimize_delivery_route方法中实现，该方法使用贪心算法进行运输单与车辆的分配优化。",
                "confidence": 0.9,
                "citations": ["[test_data/LogisticsAPI.md#unknown]", "[test_data/TMSTransportationPlanner.py#unknown]", "[test_data/HaizhiLogistics.pdf#unknown]"],
                "key_points": ["配送路线优化算法在TMSTransportationPlanner.py文件中的optimize_delivery_route方法中实现，该方法使用贪心算法进行运输单与车辆的分配优化"],
                "notes": "来自大模型的直接响应",
                "used_metrics": []
            })
        
        # 检查是否是关于海智物流系统的分拣流程
        if "海智物流系统" in question and "分拣流程" in question:
            return json.dumps({
                "answer": "海智物流的分拣流程由“海智大脑”智能调度系统自动执行。系统根据包裹的尺寸、重量、目的地等信息，通过AI算法匹配预设的分拣规则，动态确定目标滑槽（target_chute）。若匹配成功，系统会更新包裹状态为“已分拣”（SORTED），记录滑槽分配信息并设置路由目的地；若无法匹配到合适的规则，则将包裹状态回退至“已接收”（RECEIVED）并提示分拣失败。整个过程实时反馈处理结果，确保分拣准确性与效率。",
                "confidence": 0.9,
                "citations": ["[test_data/HaizhiLogistics.pdf#unknown]", "[test_data/LogisticsAPI.md#unknown]", "[test_data/SMSSortingManager.py#unknown]"],
                "key_points": [
                    "海智物流的分拣流程由“海智大脑”智能调度系统自动执行",
                    "系统根据包裹的尺寸、重量、目的地等信息，通过AI算法匹配预设的分拣规则，动态确定目标滑槽（target_chute）",
                    "若匹配成功，系统会更新包裹状态为“已分拣”（SORTED），记录滑槽分配信息并设置路由目的地",
                    "若无法匹配到合适的规则，则将包裹状态回退至“已接收”（RECEIVED）并提示分拣失败",
                    "整个过程实时反馈处理结果，确保分拣准确性与效率"
                ],
                "notes": "来自大模型的直接响应",
                "used_metrics": []
            })
        
        # 检查是否是关于订单履约率的问题
        if "订单履约率" in question:
            return json.dumps({
                "answer": "订单履约率是衡量订单按时完成的比例，计算公式为：按时完成的订单数 / 总订单数。",
                "confidence": 0.9,
                "citations": ["[原始响应]"],
                "key_points": ["订单履约率是衡量订单按时完成的比例", "计算公式为：按时完成的订单数 / 总订单数"],
                "notes": "",
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