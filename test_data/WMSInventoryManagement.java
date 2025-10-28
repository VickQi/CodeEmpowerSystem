/**
 * 海智物流仓储管理系统
 * Warehouse Management System (WMS) 实现
 * 
 * 该类负责处理仓库中的入库、出库、库存管理等操作
 */
package com.haiwise.logistics.wms;

import java.util.Date;
import java.util.Map;
import java.util.HashMap;
import java.util.List;
import java.util.ArrayList;

public class WMSInventoryManagement {
    
    /**
     * 库存实体类
     */
    public static class Inventory {
        private String productId;
        private String productName;
        private int quantity;
        private String warehouseLocation;
        private Date lastUpdated;
        
        public Inventory(String productId, String productName, int quantity, String warehouseLocation) {
            this.productId = productId;
            this.productName = productName;
            this.quantity = quantity;
            this.warehouseLocation = warehouseLocation;
            this.lastUpdated = new Date();
        }
        
        // Getter和Setter方法
        public String getProductId() { return productId; }
        public String getProductName() { return productName; }
        public int getQuantity() { return quantity; }
        public String getWarehouseLocation() { return warehouseLocation; }
        public Date getLastUpdated() { return lastUpdated; }
        
        public void setQuantity(int quantity) { 
            this.quantity = quantity; 
            this.lastUpdated = new Date();
        }
        
        public void setWarehouseLocation(String warehouseLocation) { 
            this.warehouseLocation = warehouseLocation; 
            this.lastUpdated = new Date();
        }
    }
    
    /**
     * 入库单实体类
     */
    public static class InboundOrder {
        private String inboundId;
        private String productId;
        private String productName;
        private int quantity;
        private String supplier;
        private Date createTime;
        private String status; // PENDING, RECEIVED, PROCESSED
        
        public InboundOrder(String inboundId, String productId, String productName, 
                           int quantity, String supplier) {
            this.inboundId = inboundId;
            this.productId = productId;
            this.productName = productName;
            this.quantity = quantity;
            this.supplier = supplier;
            this.createTime = new Date();
            this.status = "PENDING";
        }
        
        // Getter和Setter方法
        public String getInboundId() { return inboundId; }
        public String getProductId() { return productId; }
        public String getProductName() { return productName; }
        public int getQuantity() { return quantity; }
        public String getSupplier() { return supplier; }
        public Date getCreateTime() { return createTime; }
        public String getStatus() { return status; }
        
        public void setStatus(String status) { this.status = status; }
    }
    
    /**
     * 出库单实体类
     */
    public static class OutboundOrder {
        private String outboundId;
        private String productId;
        private String productName;
        private int quantity;
        private String destination;
        private Date createTime;
        private String status; // PENDING, PICKED, PACKED, SHIPPED
        
        public OutboundOrder(String outboundId, String productId, String productName, 
                            int quantity, String destination) {
            this.outboundId = outboundId;
            this.productId = productId;
            this.productName = productName;
            this.quantity = quantity;
            this.destination = destination;
            this.createTime = new Date();
            this.status = "PENDING";
        }
        
        // Getter和Setter方法
        public String getOutboundId() { return outboundId; }
        public String getProductId() { return productId; }
        public String getProductName() { return productName; }
        public int getQuantity() { return quantity; }
        public String getDestination() { return destination; }
        public Date getCreateTime() { return createTime; }
        public String getStatus() { return status; }
        
        public void setStatus(String status) { this.status = status; }
    }
    
    // 库存映射表
    private Map<String, Inventory> inventoryMap;
    
    public WMSInventoryManagement() {
        this.inventoryMap = new HashMap<>();
    }
    
    /**
     * 处理入库操作
     * 
     * @param inboundOrder 入库单
     * @return 处理结果
     */
    public boolean processInbound(InboundOrder inboundOrder) {
        try {
            // 更新库存
            Inventory inventory = inventoryMap.get(inboundOrder.getProductId());
            if (inventory == null) {
                inventory = new Inventory(
                    inboundOrder.getProductId(),
                    inboundOrder.getProductName(),
                    inboundOrder.getQuantity(),
                    "A-01-01" // 默认库位
                );
                inventoryMap.put(inboundOrder.getProductId(), inventory);
            } else {
                inventory.setQuantity(inventory.getQuantity() + inboundOrder.getQuantity());
            }
            
            // 更新入库单状态
            inboundOrder.setStatus("PROCESSED");
            
            System.out.println("海智物流：入库单 " + inboundOrder.getInboundId() + 
                             " 处理完成，商品 " + inboundOrder.getProductName() + 
                             " 入库数量 " + inboundOrder.getQuantity());
            return true;
        } catch (Exception e) {
            System.err.println("海智物流：入库处理失败 - " + e.getMessage());
            return false;
        }
    }
    
    /**
     * 处理出库操作
     * 
     * @param outboundOrder 出库单
     * @return 处理结果
     */
    public boolean processOutbound(OutboundOrder outboundOrder) {
        try {
            // 检查库存
            Inventory inventory = inventoryMap.get(outboundOrder.getProductId());
            if (inventory == null || inventory.getQuantity() < outboundOrder.getQuantity()) {
                System.err.println("海智物流：库存不足，无法处理出库单 " + outboundOrder.getOutboundId());
                return false;
            }
            
            // 更新库存
            inventory.setQuantity(inventory.getQuantity() - outboundOrder.getQuantity());
            
            // 更新出库单状态
            outboundOrder.setStatus("SHIPPED");
            
            System.out.println("海智物流：出库单 " + outboundOrder.getOutboundId() + 
                             " 处理完成，商品 " + outboundOrder.getProductName() + 
                             " 出库数量 " + outboundOrder.getQuantity());
            return true;
        } catch (Exception e) {
            System.err.println("海智物流：出库处理失败 - " + e.getMessage());
            return false;
        }
    }
    
    /**
     * 查询库存
     * 
     * @param productId 商品ID
     * @return 库存信息
     */
    public Inventory getInventory(String productId) {
        return inventoryMap.get(productId);
    }
    
    /**
     * 获取库存水平
     * 
     * @param productId 商品ID
     * @return 库存数量
     */
    public int getInventoryLevel(String productId) {
        Inventory inventory = inventoryMap.get(productId);
        if (inventory == null) {
            return 0; // 边界条件：商品不存在时返回0
        }
        return inventory.getQuantity();
    }
    
    /**
     * 计算库存周转率
     * 公式：库存周转率 = 销售成本 / 平均库存
     * 平均库存 = (期初库存 + 期末库存) / 2
     * 
     * @param costOfGoodsSold 销售成本
     * @param beginningInventory 期初库存
     * @param endingInventory 期末库存
     * @return 库存周转率
     */
    public double calculateTurnoverRate(double costOfGoodsSold, double beginningInventory, double endingInventory) {
        // 计算平均库存
        double averageInventory = (beginningInventory + endingInventory) / 2;
        
        // 边界条件：平均库存为0时返回0
        if (averageInventory == 0) {
            return 0;
        }
        
        // 计算并返回库存周转率
        return costOfGoodsSold / averageInventory;
    }
    
    /**
     * 生成入库单ID
     * 
     * @return 入库单ID
     */
    public String generateInboundId() {
        return "INB" + System.currentTimeMillis();
    }
    
    /**
     * 生成出库单ID
     * 
     * @return 出库单ID
     */
    public String generateOutboundId() {
        return "OUT" + System.currentTimeMillis();
    }
}