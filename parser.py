import json
import re
from typing import List, Dict, Any
from retriver import RetrievedDocument

class ResponseParser:
    def parse(self, raw_response: str, retrieved_docs: List[RetrievedDocument]) -> dict:
        """解析LLM响应并合成最终输出
        
        Args:
            raw_response: LLM的原始响应
            retrieved_docs: 检索到的文档列表
            
        Returns:
            dict: 结构化的响应数据
        """
        try:
            # 尝试解析JSON
            payload = json.loads(raw_response)
            return self._validate_payload(payload, retrieved_docs)
        except json.JSONDecodeError:
            # JSON解析失败，尝试修复
            payload = self._repair_json(raw_response)
            if payload:
                return self._validate_payload(payload, retrieved_docs)
            else:
                # 降级处理
                return self._fallback_response(raw_response, retrieved_docs)
    
    def _validate_payload(self, payload: dict, retrieved_docs: List[RetrievedDocument]) -> dict:
        """验证payload完整性并合成结构化响应"""
        # 检查是否是OpenAI格式的响应
        if 'choices' in payload:
            # 处理OpenAI格式响应
            return self._handle_openai_response(payload, retrieved_docs)
        
        # 检查必需字段
        required_fields = ['answer', 'citations', 'notes', 'confidence']
        for field in required_fields:
            if field not in payload:
                payload[field] = self._get_default(field)
        
        # 验证citations可追溯性
        payload['citations'] = self._validate_citations(payload['citations'], retrieved_docs)
        
        # 验证confidence范围
        payload['confidence'] = max(0.0, min(1.0, payload.get('confidence', 0.0)))
        
        # 提取关键信息
        payload['key_points'] = self._extract_key_points(payload.get('answer', ''))
        
        # 合成结构化响应
        structured_response = {
            'answer': payload.get('answer', ''),
            'confidence': payload['confidence'],
            'citations': payload['citations'],
            'key_points': payload.get('key_points', []),
            'notes': payload.get('notes', ''),
            'used_metrics': payload.get('used_metrics', [])
        }
        
        return structured_response
    
    def _handle_openai_response(self, payload: dict, retrieved_docs: List[RetrievedDocument]) -> dict:
        """处理OpenAI格式的响应"""
        try:
            choice = payload['choices'][0]
            content = ""
            if 'message' in choice:
                content = choice['message']['content']
            elif 'text' in choice:
                content = choice['text']
            
            if content:
                # 生成具体的引用信息
                citations = self._generate_citations(retrieved_docs)
                
                # 构造结构化响应
                return {
                    'answer': content.strip(),
                    'confidence': 0.9,  # OpenAI响应通常具有较高置信度
                    'citations': citations,
                    'key_points': self._extract_key_points(content.strip()),
                    'notes': '来自大模型的直接响应',
                    'used_metrics': []
                }
        except Exception as e:
            print(f"处理OpenAI响应时出错: {e}")
        
        # 如果处理失败，返回默认响应
        return {
            'answer': '无法生成有效回答',
            'confidence': 0.0,
            'citations': ["[无有效引用]"],
            'key_points': [],
            'notes': '处理OpenAI响应失败',
            'used_metrics': []
        }
    
    def _validate_citations(self, citations: List[str], 
                          retrieved_docs: List[RetrievedDocument]) -> List[str]:
        """验证引用可追溯性"""
        if not citations:
            return self._generate_citations(retrieved_docs)
            
        valid_citations = []
        for citation in citations:
            # 检查引用是否在检索结果中
            if any(doc.source + '#' + doc.location in citation for doc in retrieved_docs):
                valid_citations.append(citation)
        return valid_citations or self._generate_citations(retrieved_docs)
    
    def _generate_citations(self, retrieved_docs: List[RetrievedDocument]) -> List[str]:
        """生成引用信息"""
        if not retrieved_docs:
            return ["[无有效引用]"]
        
        citations = []
        for doc in retrieved_docs[:3]:  # 最多引用前3个文档
            citation = f"[{doc.source}#{doc.location}]"
            citations.append(citation)
        
        return citations if citations else ["[无有效引用]"]
    
    def _get_default(self, field: str) -> Any:
        """获取字段默认值"""
        defaults = {
            'answer': '无法生成有效回答',
            'citations': [],
            'notes': '',
            'confidence': 0.0,
            'used_metrics': [],
            'key_points': []
        }
        return defaults.get(field, '')
    
    def _repair_json(self, raw_response: str) -> dict:
        """尝试修复JSON格式"""
        try:
            # 尝试提取JSON部分
            json_match = re.search(r'\{.*\}', raw_response, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
                # 尝试修复常见的JSON问题
                json_str = json_str.replace("'", '"')  # 替换单引号为双引号
                # 为键添加引号（简单处理）
                json_str = re.sub(r'(\w+):', r'"\1":', json_str)
                return json.loads(json_str)
        except Exception as e:
            print(f"JSON修复失败: {e}")
            pass
            
        # 如果上面的方法失败，尝试另一种方式
        try:
            # 尝试直接解析整个响应（可能已经是JSON格式但有格式问题）
            # 移除可能的前缀和后缀
            cleaned = raw_response.strip()
            if cleaned.startswith("```json"):
                cleaned = cleaned[7:]  # 移除 ```json
            if cleaned.endswith("```"):
                cleaned = cleaned[:-3]  # 移除 ```
            cleaned = cleaned.strip()
            return json.loads(cleaned)
        except:
            pass
            
        return None
    
    def _fallback_response(self, raw_response: str, retrieved_docs: List[RetrievedDocument]) -> dict:
        """降级处理：当JSON解析失败时的处理方案"""
        # 尝试从响应中提取有用信息
        answer = self._extract_answer_from_response(raw_response)
        
        # 生成具体的引用信息
        citations = self._generate_citations(retrieved_docs)
        
        return {
            'answer': answer,
            'confidence': 0.5,  # 给一个中等的置信度
            'citations': citations,
            'key_points': self._extract_key_points(answer),
            'notes': '原始响应不是有效的JSON格式',
            'used_metrics': []
        }
    
    def _extract_answer_from_response(self, raw_response: str) -> str:
        """从原始响应中提取回答"""
        if not raw_response:
            return "无法生成有效回答"
            
        # 尝试解析OpenAI格式的响应
        try:
            response_data = json.loads(raw_response)
            if 'choices' in response_data:
                choice = response_data['choices'][0]
                if 'message' in choice:
                    content = choice['message']['content']
                    if content.strip():
                        return content.strip()
                elif 'text' in choice:
                    content = choice['text']
                    if content.strip():
                        return content.strip()
        except:
            pass
            
        # 如果不是OpenAI格式，尝试其他方法
        # 移除可能的代码块标记
        cleaned = raw_response.strip()
        if cleaned.startswith("```json"):
            cleaned = cleaned[7:]  # 移除 ```json
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3]  # 移除 ```
        cleaned = cleaned.strip()
        
        # 如果清理后的内容不为空，返回它
        if cleaned:
            return cleaned
            
        return "无法生成有效回答"
    
    def _extract_key_points(self, answer: str) -> List[str]:
        """从回答中提取关键点"""
        if not answer or answer == "无法生成有效回答":
            return []
            
        # 简单的关键点提取实现
        sentences = re.split(r'[。！？；\n]', answer)
        # 过滤掉太短的句子并去除空白
        key_points = [s.strip() for s in sentences if len(s.strip()) > 5]
        return key_points[:5]  # 最多返回5个关键点