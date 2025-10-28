#!/usr/bin/env python3
"""
物流指标一致性校验模块
负责识别并提取指标值、与基准值比较、评估一致性并调整置信度
"""

from typing import Dict, List, Any, Union

class MetricValidator:
    # 支持的物流指标列表
    SUPPORTED_METRICS = [
        'inventory_turnover',           # 库存周转率
        'order_fulfillment_rate',       # 订单履行率
        'transit_time',                 # 运输时间
        'warehousing_cost',             # 仓储成本
        'on_time_delivery_rate'         # 准时交付率
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
                
            # 获取容差并比较值
            tolerance = self._get_tolerance(name)
            if not self._is_within_tolerance(metric_value, ref_value, tolerance):
                diff = abs(metric_value - ref_value) / ref_value * 100
                notes.append(f"{name}超差{diff:.1f}%（基准:{ref_value}, 抽取:{metric_value}）")
                # 降低置信度
                confidence = min(confidence, 0.5)
            else:
                notes.append(f"{name}在容差范围内（基准:{ref_value}, 抽取:{metric_value}）")
        
        # 更新payload
        payload['notes'] = "；".join(notes) if notes else payload.get('notes', '')
        payload['confidence'] = confidence
        
        return payload
    
    def _get_tolerance(self, metric_name: str) -> float:
        """获取指标容差
        
        Args:
            metric_name: 指标名称
            
        Returns:
            容差值（小数形式，如0.05表示5%）
        """
        tolerances = {
            'inventory_turnover': 0.05,        # 5%
            'order_fulfillment_rate': 0.02,    # 2%
            'transit_time': 0.10,              # 10%
            'warehousing_cost': 0.05,          # 5%
            'on_time_delivery_rate': 0.02      # 2%
        }
        return tolerances.get(metric_name, 0.05)
    
    def _is_within_tolerance(self, value: float, reference: float, tolerance: float) -> bool:
        """检查值是否在容差范围内
        
        Args:
            value: 实际值
            reference: 基准值
            tolerance: 容差
            
        Returns:
            是否在容差范围内
        """
        if reference == 0:
            return value == 0
        return abs(value - reference) / reference <= tolerance

# 使用示例和测试
if __name__ == "__main__":
    # 创建验证器实例
    validator = MetricValidator()
    
    # 模拟一个包含指标的响应
    payload = {
        'answer': '根据分析，海智物流的准时交付率为95%',
        'confidence': 0.9,
        'citations': ['[TMSTransportationPlanner.py#L15]'],
        'key_points': ['准时交付率为95%'],
        'notes': '',
        'used_metrics': [
            {
                'name': 'on_time_delivery_rate',
                'value': 0.95,
                'unit': '比率'
            }
        ]
    }
    
    # 模拟基准数据
    reference_data = {
        'on_time_delivery_rate': 0.92,  # 基准值为92%
        'inventory_turnover': 8.5,
        'order_fulfillment_rate': 0.98
    }
    
    # 执行验证
    result = validator.validate(payload, reference_data)
    
    # 输出结果
    print("验证结果:")
    print(f"答案: {result['answer']}")
    print(f"置信度: {result['confidence']}")
    print(f"备注: {result['notes']}")
    print(f"提取的指标: {result['used_metrics']}")