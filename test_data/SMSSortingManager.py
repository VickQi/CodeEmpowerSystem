"""
海智物流分拣系统
Sorting Management System 实现

该模块负责处理包裹分拣、路由规划、分拣设备控制等操作
"""

import datetime
from typing import List, Dict, Optional
from enum import Enum

class PackageStatus(Enum):
    """包裹状态枚举"""
    RECEIVED = "已接收"
    SORTING = "分拣中"
    SORTED = "已分拣"
    ROUTED = "已路由"
    LOADED = "已装车"

class Package:
    """包裹实体类"""
    
    def __init__(self, package_id: str, weight: float, destination: str, 
                 package_type: str = "普通包裹"):
        self.package_id = package_id
        self.weight = weight  # 重量(公斤)
        self.destination = destination
        self.package_type = package_type
        self.status = PackageStatus.RECEIVED
        self.create_time = datetime.datetime.now()
        self.update_time = datetime.datetime.now()
        self.sorted_time = None
        self.routed_destination = None
    
    def update_status(self, status: PackageStatus):
        """更新包裹状态"""
        self.status = status
        self.update_time = datetime.datetime.now()
        
        if status == PackageStatus.SORTED:
            self.sorted_time = datetime.datetime.now()

class SortingRule:
    """分拣规则类"""
    
    def __init__(self, rule_id: str, destination_prefix: str, target_chute: str, 
                 priority: int = 1):
        self.rule_id = rule_id
        self.destination_prefix = destination_prefix
        self.target_chute = target_chute  # 目标滑槽
        self.priority = priority

class SortingMachine:
    """分拣设备类"""
    
    def __init__(self, machine_id: str, capacity: int = 1000):
        self.machine_id = machine_id
        self.capacity = capacity  # 每小时处理能力
        self.is_operational = True
        self.current_load = 0

class SMSSortingManager:
    """分拣管理类"""
    
    def __init__(self):
        self.packages: Dict[str, Package] = {}
        self.sorting_rules: List[SortingRule] = []
        self.machines: Dict[str, SortingMachine] = {}
        self.chute_assignments: Dict[str, str] = {}  # 包裹ID -> 滑槽ID
    
    def receive_package(self, weight: float, destination: str, 
                       package_type: str = "普通包裹") -> Package:
        """
        接收包裹
        
        Args:
            weight: 包裹重量(公斤)
            destination: 目的地
            package_type: 包裹类型
            
        Returns:
            创建的包裹对象
        """
        package_id = self._generate_package_id()
        package = Package(package_id, weight, destination, package_type)
        self.packages[package_id] = package
        
        print(f"海智物流：包裹 {package_id} 已接收，重量 {weight}kg，目的地 {destination}")
        return package
    
    def add_sorting_rule(self, destination_prefix: str, target_chute: str, 
                        priority: int = 1) -> SortingRule:
        """
        添加分拣规则
        
        Args:
            destination_prefix: 目的地前缀
            target_chute: 目标滑槽
            priority: 优先级
            
        Returns:
            创建的分拣规则对象
        """
        rule_id = f"RULE{len(self.sorting_rules) + 1}"
        rule = SortingRule(rule_id, destination_prefix, target_chute, priority)
        self.sorting_rules.append(rule)
        
        print(f"海智物流：添加分拣规则 {rule_id}，目的地前缀 {destination_prefix} -> 滑槽 {target_chute}")
        return rule
    
    def sort_package(self, package_id: str) -> Optional[str]:
        """
        分拣包裹
        
        Args:
            package_id: 包裹ID
            
        Returns:
            分拣到的滑槽ID，如果无法分拣则返回None
        """
        if package_id not in self.packages:
            print(f"海智物流：包裹 {package_id} 不存在")
            return None
            
        package = self.packages[package_id]
        package.update_status(PackageStatus.SORTING)
        
        # 根据目的地查找匹配的分拣规则
        target_chute = None
        matched_rule = None
        
        # 按优先级排序规则
        sorted_rules = sorted(self.sorting_rules, key=lambda r: r.priority)
        
        for rule in sorted_rules:
            if package.destination.startswith(rule.destination_prefix):
                target_chute = rule.target_chute
                matched_rule = rule
                break
        
        if target_chute:
            # 执行分拣
            package.update_status(PackageStatus.SORTED)
            self.chute_assignments[package_id] = target_chute
            package.routed_destination = target_chute
            
            print(f"海智物流：包裹 {package_id} 已分拣到滑槽 {target_chute} (匹配规则 {matched_rule.rule_id})")
            return target_chute
        else:
            print(f"海智物流：包裹 {package_id} 无法找到合适的分拣规则")
            package.update_status(PackageStatus.RECEIVED)  # 回退状态
            return None
    
    def route_package(self, package_id: str, target_transport: str) -> bool:
        """
        路由包裹到指定运输方式
        
        Args:
            package_id: 包裹ID
            target_transport: 目标运输方式
            
        Returns:
            路由结果
        """
        if package_id not in self.packages:
            print(f"海智物流：包裹 {package_id} 不存在")
            return False
            
        package = self.packages[package_id]
        
        if package.status != PackageStatus.SORTED:
            print(f"海智物流：包裹 {package_id} 尚未完成分拣，无法路由")
            return False
            
        package.update_status(PackageStatus.ROUTED)
        package.routed_destination = target_transport
        
        print(f"海智物流：包裹 {package_id} 已路由到 {target_transport}")
        return True
    
    def load_package(self, package_id: str, vehicle_id: str) -> bool:
        """
        装车操作
        
        Args:
            package_id: 包裹ID
            vehicle_id: 车辆ID
            
        Returns:
            装车结果
        """
        if package_id not in self.packages:
            print(f"海智物流：包裹 {package_id} 不存在")
            return False
            
        package = self.packages[package_id]
        
        if package.status != PackageStatus.ROUTED:
            print(f"海智物流：包裹 {package_id} 尚未路由，无法装车")
            return False
            
        package.update_status(PackageStatus.LOADED)
        
        print(f"海智物流：包裹 {package_id} 已装车 {vehicle_id}")
        return True
    
    def add_sorting_machine(self, machine_id: str, capacity: int = 1000) -> SortingMachine:
        """
        添加分拣设备
        
        Args:
            machine_id: 设备ID
            capacity: 每小时处理能力
            
        Returns:
            创建的分拣设备对象
        """
        machine = SortingMachine(machine_id, capacity)
        self.machines[machine_id] = machine
        
        print(f"海智物流：分拣设备 {machine_id} 已添加，处理能力 {capacity}件/小时")
        return machine
    
    def get_packages_by_status(self, status: PackageStatus) -> List[Package]:
        """
        根据状态查询包裹
        
        Args:
            status: 包裹状态
            
        Returns:
            符合条件的包裹列表
        """
        return [pkg for pkg in self.packages.values() if pkg.status == status]
    
    def _generate_package_id(self) -> str:
        """生成包裹ID"""
        return f"PKG{int(datetime.datetime.now().timestamp() * 1000)}"

# 使用示例
if __name__ == "__main__":
    # 创建分拣管理系统实例
    sms = SMSSortingManager()
    
    # 添加分拣设备
    machine1 = sms.add_sorting_machine("SM001", 1500)
    machine2 = sms.add_sorting_machine("SM002", 2000)
    
    # 添加分拣规则
    sms.add_sorting_rule("北京", "CHUTE-01", 1)
    sms.add_sorting_rule("上海", "CHUTE-02", 1)
    sms.add_sorting_rule("广州", "CHUTE-03", 1)
    sms.add_sorting_rule("深圳", "CHUTE-04", 1)
    
    # 接收包裹
    pkg1 = sms.receive_package(2.5, "北京市朝阳区")
    pkg2 = sms.receive_package(1.2, "上海市浦东新区")
    pkg3 = sms.receive_package(5.0, "广州市天河区")
    
    # 分拣包裹
    sms.sort_package(pkg1.package_id)
    sms.sort_package(pkg2.package_id)
    sms.sort_package(pkg3.package_id)