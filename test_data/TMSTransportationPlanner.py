"""
海智物流运输管理系统
Transportation Management System (TMS) 实现

该模块负责处理运输计划、路线优化、车辆调度等操作
"""

import datetime
from typing import List, Dict, Optional
from enum import Enum

class ShipmentStatus(Enum):
    """运输状态枚举"""
    CREATED = "已创建"
    SCHEDULED = "已排程"
    IN_TRANSIT = "运输中"
    DELIVERED = "已送达"
    CANCELLED = "已取消"

class Shipment:
    """运输单实体类"""
    
    def __init__(self, shipment_id: str, origin: str, destination: str, 
                 planned_distance: float):
        self.shipment_id = shipment_id
        self.origin = origin
        self.destination = destination
        self.planned_distance = planned_distance
        self.status = ShipmentStatus.CREATED
        self.create_time = datetime.datetime.now()
        self.update_time = datetime.datetime.now()
        self.assigned_vehicle = None
        self.estimated_arrival = None
    
    def update_status(self, status: ShipmentStatus):
        """更新运输状态"""
        self.status = status
        self.update_time = datetime.datetime.now()
        
    def assign_vehicle(self, vehicle_id: str, estimated_arrival: datetime.datetime):
        """分配运输车辆"""
        self.assigned_vehicle = vehicle_id
        self.estimated_arrival = estimated_arrival
        self.update_status(ShipmentStatus.SCHEDULED)

class Vehicle:
    """车辆实体类"""
    
    def __init__(self, vehicle_id: str, plate_number: str, capacity: float, 
                 current_location: str):
        self.vehicle_id = vehicle_id
        self.plate_number = plate_number
        self.capacity = capacity  # 载重能力(吨)
        self.current_location = current_location
        self.is_available = True
        self.current_shipment = None

class TMSTransportationPlanner:
    """运输计划管理类"""
    
    def __init__(self):
        self.shipments: Dict[str, Shipment] = {}
        self.vehicles: Dict[str, Vehicle] = {}
    
    def create_shipment(self, origin: str, destination: str, 
                       planned_distance: float) -> Shipment:
        """
        创建运输单
        
        Args:
            origin: 起点
            destination: 终点
            planned_distance: 计划距离(公里)
            
        Returns:
            创建的运输单
        """
        shipment_id = self._generate_shipment_id()
        shipment = Shipment(shipment_id, origin, destination, planned_distance)
        self.shipments[shipment_id] = shipment
        
        print(f"海智物流：运输单 {shipment_id} 已创建，从 {origin} 到 {destination}")
        return shipment
    
    def schedule_shipment(self, shipment_id: str, vehicle_id: str, 
                         estimated_arrival: datetime.datetime) -> bool:
        """
        安排运输计划
        
        Args:
            shipment_id: 运输单ID
            vehicle_id: 车辆ID
            estimated_arrival: 预计到达时间
            
        Returns:
            安排结果
        """
        if shipment_id not in self.shipments:
            print(f"海智物流：运输单 {shipment_id} 不存在")
            return False
            
        if vehicle_id not in self.vehicles:
            print(f"海智物流：车辆 {vehicle_id} 不存在")
            return False
            
        shipment = self.shipments[shipment_id]
        vehicle = self.vehicles[vehicle_id]
        
        if not vehicle.is_available:
            print(f"海智物流：车辆 {vehicle_id} 不可用")
            return False
            
        # 分配车辆
        shipment.assign_vehicle(vehicle_id, estimated_arrival)
        vehicle.is_available = False
        vehicle.current_shipment = shipment_id
        
        print(f"海智物流：运输单 {shipment_id} 已安排车辆 {vehicle_id}")
        return True
    
    def start_transportation(self, shipment_id: str) -> bool:
        """
        开始运输
        
        Args:
            shipment_id: 运输单ID
            
        Returns:
            启动结果
        """
        if shipment_id not in self.shipments:
            print(f"海智物流：运输单 {shipment_id} 不存在")
            return False
            
        shipment = self.shipments[shipment_id]
        shipment.update_status(ShipmentStatus.IN_TRANSIT)
        
        print(f"海智物流：运输单 {shipment_id} 开始运输")
        return True
    
    def complete_transportation(self, shipment_id: str) -> bool:
        """
        完成运输
        
        Args:
            shipment_id: 运输单ID
            
        Returns:
            完成结果
        """
        if shipment_id not in self.shipments:
            print(f"海智物流：运输单 {shipment_id} 不存在")
            return False
            
        shipment = self.shipments[shipment_id]
        shipment.update_status(ShipmentStatus.DELIVERED)
        
        # 释放车辆
        if shipment.assigned_vehicle:
            vehicle = self.vehicles[shipment.assigned_vehicle]
            vehicle.is_available = True
            vehicle.current_shipment = None
            vehicle.current_location = shipment.destination
        
        print(f"海智物流：运输单 {shipment_id} 已完成，货物已送达 {shipment.destination}")
        return True
    
    def add_vehicle(self, vehicle_id: str, plate_number: str, capacity: float, 
                   current_location: str) -> Vehicle:
        """
        添加车辆
        
        Args:
            vehicle_id: 车辆ID
            plate_number: 车牌号
            capacity: 载重能力(吨)
            current_location: 当前位置
            
        Returns:
            创建的车辆对象
        """
        vehicle = Vehicle(vehicle_id, plate_number, capacity, current_location)
        self.vehicles[vehicle_id] = vehicle
        
        print(f"海智物流：车辆 {vehicle_id} ({plate_number}) 已添加到系统")
        return vehicle
    
    def _generate_shipment_id(self) -> str:
        """生成运输单ID"""
        return f"SHP{int(datetime.datetime.now().timestamp() * 1000)}"
    
    def optimize_delivery_route(self, shipments: List[Shipment], vehicles: List[Vehicle]) -> Dict[str, str]:
        """
        配送路线优化算法
        使用贪心算法进行简单的路线优化
        
        Args:
            shipments: 运输单列表
            vehicles: 车辆列表
            
        Returns:
            Dict[运输单ID, 车辆ID]: 运输单到车辆的分配映射
        """
        # 错误码定义
        ERR_NO_SHIPMENTS = "ERR_1001: 没有运输单需要处理"
        ERR_NO_VEHICLES = "ERR_1002: 没有可用的车辆"
        ERR_INSUFFICIENT_CAPACITY = "ERR_1003: 车辆容量不足"
        
        # 边界条件检查
        if not shipments:
            print(ERR_NO_SHIPMENTS)
            return {}
            
        if not vehicles:
            print(ERR_NO_VEHICLES)
            return {}
        
        # 按计划距离降序排序运输单
        sorted_shipments = sorted(shipments, key=lambda s: s.planned_distance, reverse=True)
        
        # 按容量降序排序车辆
        sorted_vehicles = sorted(vehicles, key=lambda v: v.capacity, reverse=True)
        
        # 分配结果
        assignment = {}
        
        # 贪心分配算法
        for shipment in sorted_shipments:
            assigned = False
            for vehicle in sorted_vehicles:
                # 检查车辆是否可用
                if vehicle.is_available:
                    # 简化的容量检查（实际应用中需要考虑更多因素）
                    if vehicle.capacity >= shipment.planned_distance / 100:  # 假设每100公里需要1吨容量
                        assignment[shipment.shipment_id] = vehicle.vehicle_id
                        vehicle.is_available = False
                        assigned = True
                        break
            
            # 如果没有车辆可以分配
            if not assigned:
                print(f"{ERR_INSUFFICIENT_CAPACITY} 无法为运输单 {shipment.shipment_id} 分配车辆")
        
        return assignment

# 使用示例
if __name__ == "__main__":
    # 创建运输管理系统实例
    tms = TMSTransportationPlanner()
    
    # 添加车辆
    vehicle1 = tms.add_vehicle("V001", "粤A12345", 10.0, "广州仓库")
    vehicle2 = tms.add_vehicle("V002", "粤B67890", 15.0, "深圳配送中心")
    
    # 创建运输单
    shipment = tms.create_shipment("广州仓库", "北京客户", 2000.5)
    
    # 安排运输计划
    arrival_time = datetime.datetime.now() + datetime.timedelta(hours=24)
    tms.schedule_shipment(shipment.shipment_id, "V001", arrival_time)
    
    # 开始运输
    tms.start_transportation(shipment.shipment_id)