#!/usr/bin/env python3
"""
MetricValidator模块测试文件
"""

import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from metric_validator import MetricValidator

def test_metric_validation():
    """测试指标验证功能"""
    print("开始测试指标验证功能...")
    
    # 创建验证器
    validator = MetricValidator()
    
    # 测试数据
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
    
    # 基准数据
    reference_data = {
        'on_time_delivery_rate': 0.92,  # 基准值为92%
        'inventory_turnover': 8.5,
        'order_fulfillment_rate': 0.98
    }
    
    # 执行验证
    result = validator.validate(payload, reference_data)
    
    # 验证结果
    assert result['confidence'] == 0.5  # 超出差范围，置信度应降低
    assert "on_time_delivery_rate超差3.3%" in result['notes']
    
    print("✓ 指标验证功能测试通过")

def test_metric_within_tolerance():
    """测试指标在容差范围内的情况"""
    print("\n开始测试指标在容差范围内的情况...")
    
    # 创建验证器
    validator = MetricValidator()
    
    # 测试数据（在容差范围内）
    payload = {
        'answer': '根据分析，海智物流的订单履行率为97%',
        'confidence': 0.85,
        'citations': ['[WMSInventoryManagement.java#L50]'],
        'key_points': ['订单履行率为97%'],
        'notes': '',
        'used_metrics': [
            {
                'name': 'order_fulfillment_rate',
                'value': 0.97,
                'unit': '比率'
            }
        ]
    }
    
    # 基准数据
    reference_data = {
        'order_fulfillment_rate': 0.965,  # 基准值为96.5%
    }
    
    # 执行验证
    result = validator.validate(payload, reference_data)
    
    # 验证结果
    assert result['confidence'] == 0.85  # 在容差范围内，置信度不应降低
    assert "order_fulfillment_rate在容差范围内" in result['notes']
    
    print("✓ 指标在容差范围内测试通过")

def test_unsupported_metric():
    """测试不支持的指标"""
    print("\n开始测试不支持的指标...")
    
    # 创建验证器
    validator = MetricValidator()
    
    # 测试数据（不支持的指标）
    payload = {
        'answer': '根据分析，海智物流的客户满意度为90%',
        'confidence': 0.8,
        'citations': ['[CustomerSatisfactionReport.pdf#L10]'],
        'key_points': ['客户满意度为90%'],
        'notes': '',
        'used_metrics': [
            {
                'name': 'customer_satisfaction',
                'value': 0.90,
                'unit': '比率'
            }
        ]
    }
    
    # 基准数据
    reference_data = {}
    
    # 执行验证
    result = validator.validate(payload, reference_data)
    
    # 验证结果
    assert result['confidence'] == 0.8  # 不支持的指标不应影响置信度
    # 不支持的指标不应出现在备注中
    
    print("✓ 不支持的指标测试通过")

def test_no_metrics():
    """测试没有指标的情况"""
    print("\n开始测试没有指标的情况...")
    
    # 创建验证器
    validator = MetricValidator()
    
    # 测试数据（没有指标）
    payload = {
        'answer': '根据分析，海智物流的服务质量很高',
        'confidence': 0.7,
        'citations': ['[HaizhiLogistics.pdf#L5]'],
        'key_points': ['服务质量很高'],
        'notes': '',
        'used_metrics': []
    }
    
    # 基准数据
    reference_data = {}
    
    # 执行验证
    result = validator.validate(payload, reference_data)
    
    # 验证结果
    assert result['confidence'] == 0.7  # 没有指标，置信度不应改变
    assert result['notes'] == ''  # 没有指标，不应有备注
    
    print("✓ 没有指标的情况测试通过")

def test_invalid_metric_values():
    """测试无效的指标值"""
    print("\n开始测试无效的指标值...")
    
    # 创建验证器
    validator = MetricValidator()
    
    # 测试数据（无效的指标值）
    payload = {
        'answer': '根据分析，海智物流的库存周转率为高',
        'confidence': 0.75,
        'citations': ['[WMSInventoryManagement.java#L100]'],
        'key_points': ['库存周转率为高'],
        'notes': '',
        'used_metrics': [
            {
                'name': 'inventory_turnover',
                'value': '高',  # 无效值
                'unit': '文本'
            }
        ]
    }
    
    # 基准数据
    reference_data = {
        'inventory_turnover': 8.5,
    }
    
    # 执行验证
    result = validator.validate(payload, reference_data)
    
    # 验证结果
    assert result['confidence'] == 0.75  # 无效值不应影响置信度
    assert "inventory_turnover：数据类型错误" in result['notes']
    
    print("✓ 无效的指标值测试通过")

if __name__ == "__main__":
    print("开始测试MetricValidator模块...")
    print("=" * 50)
    
    test_metric_validation()
    test_metric_within_tolerance()
    test_unsupported_metric()
    test_no_metrics()
    test_invalid_metric_values()
    
    print("\n" + "=" * 50)
    print("所有MetricValidator模块测试通过!")