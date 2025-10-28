from typing import List
from retriver import RetrievedDocument

# 定义Message类型
Message = dict

class PromptBuilder:
    def __init__(self, max_chars: int = 3500):
        self.max_chars = max_chars
        self.templates = {
            'dev': "你是一个物流系统开发专家，请基于以下上下文回答问题：\n{context}\n问题：{question}",
            'product': "你是一个物流产品专家，请基于以下上下文回答问题：\n{context}\n问题：{question}",
            'test': "你是一个物流测试专家，请基于以下上下文回答问题：\n{context}\n问题：{question}"
        }
    
    def build_prompt(self, question: str, docs: List[RetrievedDocument], 
                    agent_type: str = 'dev') -> List[Message]:
        """构建提示词"""
        # 拼接上下文
        context = ""
        for doc in docs:
            context += f"[{doc.source}#{doc.location}]\n{doc.content}\n\n"
        
        # 裁剪上下文
        context = self._truncate_context(context)
        
        # 应用模板
        template = self.templates.get(agent_type, self.templates['dev'])
        prompt = template.format(context=context, question=question)
        
        return [{"role": "user", "content": prompt}]
    
    def _truncate_context(self, context: str) -> str:
        """裁剪上下文至max_chars"""
        if len(context) <= self.max_chars:
            return context
        
        # 保留首尾，移除中间部分
        head_size = self.max_chars // 3
        tail_size = self.max_chars // 3
        return context[:head_size] + "\n... [内容过长已裁剪] ...\n" + context[-tail_size:]