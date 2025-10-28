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

def test_metric_validation_within_tolerance():
    """测试指标在容差范围内的情况"""
    print("开始测试指标在容差范围内的情况...")
    
    # 创建验证器
    validator = MetricValidator()
    
    # 测试数据（在容差范围内）
    payload = {
        'answer': '根据分析，库存周转率为8.2',
        'confidence': 0.7,
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
    
    # 基准数据 (差值小于5%)
    reference_data = {
        'inventory_turnover': 8.5,  # 基准值为8.5，差值(8.5-8.2)/8.5≈3.5% < 5%
    }
    
    # 执行验证
    result = validator.validate(payload, reference_data)
    
    # 验证结果
    assert result['confidence'] == 0.8  # 差值<=5%，置信度应为0.8
    assert result['notes'] == ''  # 无超差，备注应为空
    
    print("✓ 指标在容差范围内测试通过")

def test_metric_validation_exceed_tolerance():
    """测试指标超出容差范围的情况"""
    print("\n开始测试指标超出容差范围的情况...")
    
    # 创建验证器
    validator = MetricValidator()
    
    # 测试数据（超出容差范围）
    payload = {
        'answer': '根据分析，发货准时率为85%',
        'confidence': 0.9,
        'citations': ['[TMSTransportationPlanner.py#L15]'],
        'key_points': ['发货准时率为85%'],
        'notes': '',
        'used_metrics': [
            {
                'name': 'shipment_on_time_rate',
                'value': 0.85,
                'unit': '比率'
            }
        ]
    }
    
    # 基准数据 (差值大于5%)
    reference_data = {
        'shipment_on_time_rate': 0.92,  # 基准值为92%，差值(92%-85%)/92%≈7.6% > 5%
    }
    
    # 执行验证
    result = validator.validate(payload, reference_data)
    
    # 验证结果
    assert result['confidence'] == 0.5  # 差值>5%，置信度应为0.5
    assert "shipment_on_time_rate超差7.6%" in result['notes']
    
    print("✓ 指标超出容差范围测试通过")

def test_supported_metrics_only():
    """测试只处理支持的指标"""
    print("\n开始测试只处理支持的指标...")
    
    # 创建验证器
    validator = MetricValidator()
    
    # 测试数据（包含支持和不支持的指标）
    payload = {
        'answer': '根据分析...',
        'confidence': 0.9,
        'citations': [],
        'key_points': [],
        'notes': '',
        'used_metrics': [
            {
                'name': 'inventory_turnover',
                'value': 8.0,
                'unit': '次数'
            },
            {
                'name': 'unsupported_metric',
                'value': 100,
                'unit': '单位'
            }
        ]
    }
    
    # 基准数据
    reference_data = {
        'inventory_turnover': 8.5,  # 差值(8.5-8.0)/8.5≈5.9% > 5%
        'avg_delivery_time': 24.0
    }
    
    # 执行验证
    result = validator.validate(payload, reference_data)
    
    # 验证结果 - 只有支持的指标会被处理
    assert result['confidence'] == 0.5  # inventory_turnover超差，置信度应为0.5
    assert "inventory_turnover超差5.9%" in result['notes']
    
    print("✓ 只处理支持的指标测试通过")

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
        'answer': '根据分析，平均配送时间为未知',
        'confidence': 0.75,
        'citations': ['[TMSTransportationPlanner.py#L100]'],
        'key_points': ['平均配送时间为未知'],
        'notes': '',
        'used_metrics': [
            {
                'name': 'avg_delivery_time',
                'value': '未知',  # 无效值
                'unit': '小时'
            }
        ]
    }
    
    # 基准数据
    reference_data = {
        'avg_delivery_time': 24.0,
    }
    
    # 执行验证
    result = validator.validate(payload, reference_data)
    
    # 验证结果
    assert result['confidence'] == 0.75  # 无效值不应影响置信度
    assert "avg_delivery_time：数据类型错误" in result['notes']
    
    print("✓ 无效的指标值测试通过")

if __name__ == "__main__":
    print("开始测试MetricValidator模块...")
    print("=" * 50)
    
    test_metric_validation_within_tolerance()
    test_metric_validation_exceed_tolerance()
    test_supported_metrics_only()
    test_no_metrics()
    test_invalid_metric_values()
    
    print("\n" + "=" * 50)
    print("所有MetricValidator模块测试通过!")