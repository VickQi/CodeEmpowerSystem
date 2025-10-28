#!/usr/bin/env python3
"""
物流指标一致性校验模块
负责识别并提取指标值、与基准值比较、评估一致性并调整置信度
"""

from typing import Dict, List, Any, Union

class MetricValidator:
    # 支持的物流指标列表 (根据FR-08需求)
    SUPPORTED_METRICS = [
        'inventory_turnover',           # 库存周转率
        'shipment_on_time_rate',        # 发货准时率
        'avg_delivery_time'             # 平均配送时间
    ]
    
    def validate(self, payload: dict, reference_data: dict) -> dict:
        """校验指标一致性
        
        Args:
            payload: 包含提取指标的响应数据
            reference_data: 基准数据字典
            
        Returns:
            更新后的payload，包含一致性校验结果和调整后的置信度
        """
        # 如果没有指标数据，直接返回原始payload
        if not payload.get('used_metrics'):
            return payload
        
        notes = []
        confidence = payload['confidence']
        
        # 遍历所有提取的指标
        for metric in payload['used_metrics']:
            name = metric['name']
            # 只处理支持的指标
            if name not in self.SUPPORTED_METRICS:
                continue
                
            # 获取基准值
            ref_value = reference_data.get(name)
            if ref_value is None:
                notes.append(f"无法验证指标 {name}：无基准值")
                continue
                
            # 获取指标值并转换为数值类型
            try:
                metric_value = float(metric['value'])
                ref_value = float(ref_value)
            except (ValueError, TypeError):
                notes.append(f"无法验证指标 {name}：数据类型错误")
                continue
                
            # 计算差值百分比
            if ref_value != 0:
                diff_percentage = abs(metric_value - ref_value) / ref_value * 100
            else:
                # 如果基准值为0，只有当抽取值也为0时才算一致
                diff_percentage = 0 if metric_value == 0 else float('inf')
            
            # 根据FR-08需求进行判断
            if diff_percentage <= 5:  # 差值<=5%视为一致
                confidence = max(confidence, 0.8)
            else:  # 差值>5%
                notes.append(f"{name}超差{diff_percentage:.1f}%")
                confidence = 0.5  # 置信度调整为0.5
        
        # 更新payload
        payload['notes'] = "；".join(notes) if notes else payload.get('notes', '')
        payload['confidence'] = confidence
        
        return payload

# 使用示例和测试
if __name__ == "__main__":
    # 创建验证器实例
    validator = MetricValidator()
    
    # 模拟一个包含指标的响应
    payload = {
        'answer': '根据分析，库存周转率为8.2',
        'confidence': 0.9,
        'citations': ['[WMSInventoryManagement.java#L50]'],
        'key_points': ['库存周转率为8.2'],
        'notes': '',
        'used_metrics': [
            {
                'name': 'inventory_turnover',
                'value': 8.2,
                'unit': '次数'
            }
        ]
    }
    
    # 模拟基准数据
    reference_data = {
        'inventory_turnover': 8.5,  # 基准值为8.5
    }
    
    # 执行验证
    result = validator.validate(payload, reference_data)
    
    # 输出结果
    print("验证结果:")
    print(f"答案: {result['answer']}")
    print(f"置信度: {result['confidence']}")
    print(f"备注: {result['notes']}")
    print(f"提取的指标: {result['used_metrics']}")