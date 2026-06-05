-- ============================================================
-- 测试用数据库 Schema：电商系统
-- 包含完整的用户、商品、订单、支付、物流等表结构
-- 适用数据库：MySQL
-- ============================================================

-- 用户表
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    email VARCHAR(200),
    phone VARCHAR(20),
    avatar_url VARCHAR(500),
    status TINYINT NOT NULL DEFAULT 1 COMMENT '1=正常, 0=禁用, -1=删除',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_email (email),
    INDEX idx_phone (phone),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户表';

-- 用户地址表
CREATE TABLE user_addresses (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    receiver_name VARCHAR(50) NOT NULL,
    receiver_phone VARCHAR(20) NOT NULL,
    province VARCHAR(50) NOT NULL,
    city VARCHAR(50) NOT NULL,
    district VARCHAR(50),
    detail_address VARCHAR(500) NOT NULL,
    is_default TINYINT NOT NULL DEFAULT 0 COMMENT '0=非默认, 1=默认',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_user_id (user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户地址表';

-- 商品分类表
CREATE TABLE categories (
    id INT AUTO_INCREMENT PRIMARY KEY,
    parent_id INT DEFAULT NULL COMMENT '父分类ID，NULL为顶级分类',
    name VARCHAR(100) NOT NULL,
    level TINYINT NOT NULL DEFAULT 1 COMMENT '1=一级, 2=二级, 3=三级',
    sort_order INT NOT NULL DEFAULT 0,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (parent_id) REFERENCES categories(id) ON DELETE SET NULL,
    INDEX idx_parent_id (parent_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='商品分类表';

-- 商品表
CREATE TABLE products (
    id INT AUTO_INCREMENT PRIMARY KEY,
    category_id INT,
    name VARCHAR(200) NOT NULL,
    description TEXT COMMENT '商品描述',
    price DECIMAL(10,2) NOT NULL COMMENT '原价',
    cost_price DECIMAL(10,2) COMMENT '成本价',
    stock INT NOT NULL DEFAULT 0 COMMENT '库存数量',
    sales_count INT NOT NULL DEFAULT 0 COMMENT '销量',
    image_url VARCHAR(500),
    status TINYINT NOT NULL DEFAULT 1 COMMENT '1=上架, 0=下架',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE SET NULL,
    INDEX idx_category_id (category_id),
    INDEX idx_price (price),
    INDEX idx_status (status),
    INDEX idx_created_at (created_at),
    FULLTEXT INDEX ft_name_desc (name, description)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='商品表';

-- 购物车表
CREATE TABLE shopping_carts (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    product_id INT NOT NULL,
    quantity INT NOT NULL DEFAULT 1,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE,
    UNIQUE KEY uk_user_product (user_id, product_id),
    INDEX idx_user_id (user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='购物车表';

-- 订单表
CREATE TABLE orders (
    id INT AUTO_INCREMENT PRIMARY KEY,
    order_no VARCHAR(32) NOT NULL UNIQUE COMMENT '订单编号',
    user_id INT NOT NULL,
    address_id INT,
    total_amount DECIMAL(12,2) NOT NULL COMMENT '订单总金额',
    discount_amount DECIMAL(12,2) NOT NULL DEFAULT 0 COMMENT '优惠金额',
    pay_amount DECIMAL(12,2) NOT NULL COMMENT '实付金额',
    status TINYINT NOT NULL DEFAULT 0 COMMENT '0=待付款, 1=待发货, 2=已发货, 3=已完成, 4=已取消, 5=退款中, 6=已退款',
    payment_method VARCHAR(50) COMMENT '支付宝/微信/银行卡',
    paid_at TIMESTAMP NULL COMMENT '付款时间',
    shipped_at TIMESTAMP NULL COMMENT '发货时间',
    completed_at TIMESTAMP NULL COMMENT '完成时间',
    remark VARCHAR(500),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (address_id) REFERENCES user_addresses(id) ON DELETE SET NULL,
    INDEX idx_user_id (user_id),
    INDEX idx_status (status),
    INDEX idx_created_at (created_at),
    INDEX idx_order_no (order_no)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='订单表';

-- 订单明细表
CREATE TABLE order_items (
    id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT NOT NULL,
    product_id INT NOT NULL,
    product_name VARCHAR(200) NOT NULL COMMENT '下单时的商品名称',
    product_price DECIMAL(10,2) NOT NULL COMMENT '下单时的商品单价',
    quantity INT NOT NULL DEFAULT 1,
    subtotal DECIMAL(12,2) NOT NULL COMMENT '小计金额',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE,
    INDEX idx_order_id (order_id),
    INDEX idx_product_id (product_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='订单明细表';

-- 支付记录表
CREATE TABLE payments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT NOT NULL,
    payment_no VARCHAR(64) NOT NULL UNIQUE COMMENT '支付流水号',
    method VARCHAR(50) NOT NULL COMMENT '支付方式',
    amount DECIMAL(12,2) NOT NULL,
    status TINYINT NOT NULL DEFAULT 0 COMMENT '0=待支付, 1=支付成功, 2=支付失败, 3=已退款',
    paid_at TIMESTAMP NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE,
    INDEX idx_order_id (order_id),
    INDEX idx_payment_no (payment_no)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='支付记录表';

-- 物流表
CREATE TABLE shipments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT NOT NULL,
    logistics_company VARCHAR(50) COMMENT '物流公司',
    logistics_no VARCHAR(100) COMMENT '物流单号',
    receiver_name VARCHAR(50) NOT NULL,
    receiver_phone VARCHAR(20) NOT NULL,
    receiver_address VARCHAR(500) NOT NULL,
    status TINYINT NOT NULL DEFAULT 0 COMMENT '0=待发货, 1=已发货, 2=配送中, 3=已签收',
    shipped_at TIMESTAMP NULL,
    signed_at TIMESTAMP NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE,
    INDEX idx_order_id (order_id),
    INDEX idx_logistics_no (logistics_no)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='物流表';

-- 商品评价表
CREATE TABLE product_reviews (
    id INT AUTO_INCREMENT PRIMARY KEY,
    product_id INT NOT NULL,
    user_id INT NOT NULL,
    order_id INT NOT NULL,
    rating TINYINT NOT NULL DEFAULT 5 COMMENT '1-5 星',
    content TEXT,
    images JSON COMMENT '评价图片URL列表',
    status TINYINT NOT NULL DEFAULT 1 COMMENT '0=隐藏, 1=显示',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE,
    INDEX idx_product_id (product_id),
    INDEX idx_user_id (user_id),
    INDEX idx_rating (rating)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='商品评价表';