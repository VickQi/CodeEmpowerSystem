/**
 * 海智物流订单管理系统
 * Order Management System (OMS) 实现
 * 
 * 该类负责处理订单创建、更新、取消等操作
 */
package com.haiwise.logistics.oms;

import java.util.Date;
import java.util.List;
import java.util.ArrayList;

public class OMSOrderManagement {
    
    /**
     * 订单状态枚举
     */
    public enum OrderStatus {
        CREATED, CONFIRMED, PROCESSING, SHIPPED, DELIVERED, CANCELLED
    }
    
    /**
     * 订单实体类
     */
    public static class Order {
        private String orderId;
        private String customerId;
        private List<OrderItem> items;
        private double totalAmount;
        private OrderStatus status;
        private Date createTime;
        private Date updateTime;
        
        // 构造函数
        public Order(String orderId, String customerId) {
            this.orderId = orderId;
            this.customerId = customerId;
            this.items = new ArrayList<>();
            this.status = OrderStatus.CREATED;
            this.createTime = new Date();
            this.updateTime = new Date();
        }
        
        // Getter和Setter方法
        public String getOrderId() { return orderId; }
        public String getCustomerId() { return customerId; }
        public List<OrderItem> getItems() { return items; }
        public double getTotalAmount() { return totalAmount; }
        public OrderStatus getStatus() { return status; }
        public Date getCreateTime() { return createTime; }
        public Date getUpdateTime() { return updateTime; }
        
        public void setStatus(OrderStatus status) { 
            this.status = status; 
            this.updateTime = new Date();
        }
        
        public void addItem(OrderItem item) {
            this.items.add(item);
            calculateTotalAmount();
        }
        
        private void calculateTotalAmount() {
            this.totalAmount = items.stream()
                .mapToDouble(item -> item.getPrice() * item.getQuantity())
                .sum();
        }
    }
    
    /**
     * 订单项实体类
     */
    public static class OrderItem {
        private String productId;
        private String productName;
        private int quantity;
        private double price;
        
        public OrderItem(String productId, String productName, int quantity, double price) {
            this.productId = productId;
            this.productName = productName;
            this.quantity = quantity;
            this.price = price;
        }
        
        // Getter方法
        public String getProductId() { return productId; }
        public String getProductName() { return productName; }
        public int getQuantity() { return quantity; }
        public double getPrice() { return price; }
    }
    
    /**
     * 创建新订单
     * 
     * @param customerId 客户ID
     * @param items 订单项列表
     * @return 创建的订单
     */
    public Order createOrder(String customerId, List<OrderItem> items) {
        String orderId = generateOrderId();
        Order order = new Order(orderId, customerId);
        
        for (OrderItem item : items) {
            order.addItem(item);
        }
        
        System.out.println("海智物流：订单 " + orderId + " 已创建");
        return order;
    }
    
    /**
     * 确认订单
     * 
     * @param order 待确认的订单
     * @return 确认后的订单
     */
    public Order confirmOrder(Order order) {
        if (order.getStatus() == OrderStatus.CREATED) {
            order.setStatus(OrderStatus.CONFIRMED);
            System.out.println("海智物流：订单 " + order.getOrderId() + " 已确认");
        }
        return order;
    }
    
    /**
     * 取消订单
     * 
     * @param order 待取消的订单
     * @return 取消后的订单
     */
    public Order cancelOrder(Order order) {
        if (order.getStatus() != OrderStatus.SHIPPED && 
            order.getStatus() != OrderStatus.DELIVERED) {
            order.setStatus(OrderStatus.CANCELLED);
            System.out.println("海智物流：订单 " + order.getOrderId() + " 已取消");
        }
        return order;
    }
    
    /**
     * 生成订单ID
     * 
     * @return 订单ID
     */
    private String generateOrderId() {
        return "ORD" + System.currentTimeMillis();
    }
}