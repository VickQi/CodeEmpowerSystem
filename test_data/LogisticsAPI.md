# 海智物流系统API文档

## 1. 概述

海智物流系统提供了一系列API接口，用于访问物流系统中的各种功能，包括库存管理、订单处理、运输计划和包裹分拣等。

## 2. API响应格式

所有API响应都遵循统一的JSON格式：

```json
{
  "data": {},
  "message": "操作结果描述",
  "code": "响应码",
  "timestamp": "响应时间"
}
```

### 2.1 响应字段说明

| 字段名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| data | Object | 是 | API返回的具体数据 |
| message | String | 是 | 操作结果描述信息 |
| code | String | 是 | 响应码 |
| timestamp | String | 是 | 响应时间戳，格式为ISO 8601 |

### 2.2 通用错误码定义

| 错误码 | 说明 |
|--------|------|
| ERR_0001 | 参数缺失或无效 |
| ERR_0002 | 资源未找到 |
| ERR_0003 | 系统内部错误 |
| ERR_0004 | 权限不足 |
| ERR_0005 | 请求超时 |

## 3. 库存管理API

### 3.1 查询库存水平

#### 接口地址
```
GET /api/inventory/{productId}/level
```

#### 请求参数
| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| productId | String | 是 | 商品ID |

#### 响应示例
```json
{
  "data": {
    "productId": "P001",
    "productName": "智能手机",
    "quantity": 150,
    "warehouseLocation": "A-01-01"
  },
  "message": "查询成功",
  "code": "SUCCESS",
  "timestamp": "2025-10-28T10:30:00Z"
}
```

### 3.2 计算库存周转率

#### 接口地址
```
POST /api/inventory/turnover-rate
```

#### 请求参数
| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| costOfGoodsSold | Number | 是 | 销售成本 |
| beginningInventory | Number | 是 | 期初库存 |
| endingInventory | Number | 是 | 期末库存 |

#### 响应示例
```json
{
  "data": {
    "turnoverRate": 8.5,
    "formula": "销售成本 / 平均库存",
    "averageInventory": 125000
  },
  "message": "计算成功",
  "code": "SUCCESS",
  "timestamp": "2025-10-28T10:30:00Z"
}
```

## 4. 运输管理API

### 4.1 优化配送路线

#### 接口地址
```
POST /api/transportation/optimize-route
```

#### 请求参数
| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| shipments | Array | 是 | 运输单列表 |
| vehicles | Array | 是 | 车辆列表 |

#### 响应示例
```json
{
  "data": {
    "assignments": {
      "SHP001": "V001",
      "SHP002": "V002"
    },
    "totalDistance": 2500.5
  },
  "message": "路线优化完成",
  "code": "SUCCESS",
  "timestamp": "2025-10-28T10:30:00Z"
}
```

## 5. 分拣管理API

### 5.1 获取包裹状态

#### 接口地址
```
GET /api/sorting/package/{packageId}/status
```

#### 请求参数
| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| packageId | String | 是 | 包裹ID |

#### 响应示例
```json
{
  "data": {
    "packageId": "PKG001",
    "status": "SORTED",
    "chuteId": "CHUTE-01",
    "updateTime": "2025-10-28T10:15:00Z"
  },
  "message": "查询成功",
  "code": "SUCCESS",
  "timestamp": "2025-10-28T10:30:00Z"
}
```

## 6. 错误处理

### 6.1 错误响应格式

当API调用出现错误时，系统会返回以下格式的错误响应：

```json
{
  "error": {
    "code": "ERR_0001",
    "message": "参数缺失或无效",
    "details": "productId不能为空"
  },
  "timestamp": "2025-10-28T10:30:00Z"
}
```

### 6.2 特定业务错误码

| 错误码 | 说明 |
|--------|------|
| ERR_1001 | 没有运输单需要处理 |
| ERR_1002 | 没有可用的车辆 |
| ERR_1003 | 车辆容量不足 |
| ERR_2001 | 库存不足 |
| ERR_2002 | 商品不存在 |
| ERR_3001 | 包裹未找到 |
| ERR_3002 | 分拣规则不匹配 |