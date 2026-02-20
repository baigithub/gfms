-- 绿色金融管理系统 - 数据库初始化脚本
-- 用于Docker MySQL容器启动时自动执行

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- 创建数据库（如果不存在）
CREATE DATABASE IF NOT EXISTS `green_finance` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE `green_finance`;

-- 创建角色表
CREATE TABLE IF NOT EXISTS `roles` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `name` VARCHAR(50) NOT NULL UNIQUE,
  `description` VARCHAR(200),
  `permissions` TEXT,
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
  INDEX `idx_name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 创建机构表
CREATE TABLE IF NOT EXISTS `organizations` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `name` VARCHAR(100) NOT NULL,
  `code` VARCHAR(20) NOT NULL UNIQUE,
  `parent_id` INT,
  `level` INT DEFAULT 1,
  `address` VARCHAR(200),
  `is_active` BOOLEAN DEFAULT TRUE,
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
  INDEX `idx_code` (`code`),
  INDEX `idx_parent_id` (`parent_id`),
  INDEX `idx_level` (`level`),
  CONSTRAINT `fk_org_parent` FOREIGN KEY (`parent_id`) REFERENCES `organizations` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 创建用户表
CREATE TABLE IF NOT EXISTS `users` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `username` VARCHAR(50) NOT NULL UNIQUE,
  `password_hash` VARCHAR(255) NOT NULL,
  `real_name` VARCHAR(50) NOT NULL,
  `employee_id` VARCHAR(20) UNIQUE,
  `email` VARCHAR(100) UNIQUE,
  `phone` VARCHAR(20),
  `avatar` VARCHAR(255),
  `is_active` BOOLEAN DEFAULT TRUE,
  `is_superuser` BOOLEAN DEFAULT FALSE,
  `role_id` INT,
  `org_id` INT,
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
  `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `last_login` DATETIME,
  INDEX `idx_username` (`username`),
  INDEX `idx_employee_id` (`employee_id`),
  INDEX `idx_email` (`email`),
  INDEX `idx_role_id` (`role_id`),
  INDEX `idx_org_id` (`org_id`),
  CONSTRAINT `fk_user_role` FOREIGN KEY (`role_id`) REFERENCES `roles` (`id`) ON DELETE SET NULL,
  CONSTRAINT `fk_user_org` FOREIGN KEY (`org_id`) REFERENCES `organizations` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 创建绿色认定表
CREATE TABLE IF NOT EXISTS `green_identifications` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `loan_code` VARCHAR(50) NOT NULL UNIQUE,
  `customer_name` VARCHAR(100) NOT NULL,
  `customer_id` VARCHAR(50),
  `business_type` VARCHAR(50),
  `loan_account` VARCHAR(50),
  `loan_amount` DECIMAL(18, 2),
  `disbursement_date` DATETIME,
  `maturity_date` DATETIME,
  `interest_rate` DECIMAL(10, 4),
  `green_percentage` DECIMAL(5, 2),
  `green_loan_balance` DECIMAL(18, 2),
  `project_category_large` VARCHAR(50),
  `project_category_medium` VARCHAR(50),
  `project_category_small` VARCHAR(100),
  `esg_risk_level` VARCHAR(20),
  `esg_performance_level` VARCHAR(20),
  `status` VARCHAR(20) DEFAULT '待办',
  `initiator_id` INT,
  `current_handler_id` INT,
  `org_id` INT,
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
  `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `completed_at` DATETIME,
  `deadline` DATETIME,
  INDEX `idx_loan_code` (`loan_code`),
  INDEX `idx_customer_name` (`customer_name`),
  INDEX `idx_status` (`status`),
  INDEX `idx_initiator_id` (`initiator_id`),
  INDEX `idx_current_handler_id` (`current_handler_id`),
  INDEX `idx_org_id` (`org_id`),
  INDEX `idx_created_at` (`created_at`),
  INDEX `idx_completed_at` (`completed_at`),
  CONSTRAINT `fk_green_initiator` FOREIGN KEY (`initiator_id`) REFERENCES `users` (`id`) ON DELETE SET NULL,
  CONSTRAINT `fk_green_handler` FOREIGN KEY (`current_handler_id`) REFERENCES `users` (`id`) ON DELETE SET NULL,
  CONSTRAINT `fk_green_org` FOREIGN KEY (`org_id`) REFERENCES `organizations` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 创建工作流实例表
CREATE TABLE IF NOT EXISTS `workflow_instances` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `case_id` VARCHAR(50) NOT NULL UNIQUE,
  `process_key` VARCHAR(50) DEFAULT 'green_identification_process',
  `business_key` VARCHAR(50),
  `current_node` VARCHAR(50),
  `status` VARCHAR(20),
  `started_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
  `ended_at` DATETIME,
  `identification_id` INT NOT NULL,
  INDEX `idx_case_id` (`case_id`),
  INDEX `idx_business_key` (`business_key`),
  INDEX `idx_identification_id` (`identification_id`),
  CONSTRAINT `fk_wf_identification` FOREIGN KEY (`identification_id`) REFERENCES `green_identifications` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 创建工作流任务表
CREATE TABLE IF NOT EXISTS `workflow_tasks` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `task_key` VARCHAR(50),
  `task_name` VARCHAR(100),
  `node_id` VARCHAR(50),
  `assignee_id` INT,
  `status` VARCHAR(20),
  `approval_result` VARCHAR(20),
  `comment` TEXT,
  `reason` TEXT,
  `started_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
  `completed_at` DATETIME,
  `workflow_instance_id` INT,
  `identification_id` INT,
  INDEX `idx_assignee_id` (`assignee_id`),
  INDEX `idx_workflow_instance_id` (`workflow_instance_id`),
  INDEX `idx_identification_id` (`identification_id`),
  INDEX `idx_status` (`status`),
  CONSTRAINT `fk_task_assignee` FOREIGN KEY (`assignee_id`) REFERENCES `users` (`id`) ON DELETE SET NULL,
  CONSTRAINT `fk_task_workflow` FOREIGN KEY (`workflow_instance_id`) REFERENCES `workflow_instances` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 创建绿色贷款指标表
CREATE TABLE IF NOT EXISTS `green_loan_indicators` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `stat_date` DATETIME,
  `org_id` INT,
  `green_loan_balance` DECIMAL(18, 2),
  `green_loan_ratio` DECIMAL(5, 2),
  `customer_count` INT,
  `growth_rate` DECIMAL(8, 2),
  `green_investment` DECIMAL(18, 2),
  `green_leasing` DECIMAL(18, 2),
  `green_wealth_management` DECIMAL(18, 2),
  `green_underwriting` DECIMAL(18, 2),
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
  INDEX `idx_stat_date` (`stat_date`),
  INDEX `idx_org_id` (`org_id`),
  CONSTRAINT `fk_indicator_org` FOREIGN KEY (`org_id`) REFERENCES `organizations` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 插入初始角色数据
INSERT INTO `roles` (`name`, `description`) VALUES
('超级管理员', '系统超级管理员，拥有所有权限'),
('客户经理', '负责绿色贷款认定的发起'),
('绿色金融管理岗', '负责绿色贷款审核'),
('绿色金融复核岗', '负责绿色贷款最终审批'),
('普通用户', '普通系统用户');

-- 插入初始机构数据
INSERT INTO `organizations` (`name`, `code`, `level`, `address`, `is_active`) VALUES
('总行', 'HQ', 1, '北京市', TRUE);

SET @hq_id = LAST_INSERT_ID();

INSERT INTO `organizations` (`name`, `code`, `level`, `parent_id`, `address`, `is_active`) VALUES
('一级分行A', 'BRANCH_A', 2, @hq_id, '上海市', TRUE),
('一级分行B', 'BRANCH_B', 2, @hq_id, '广州市', TRUE),
('一级分行C', 'BRANCH_C', 2, @hq_id, '深圳市', TRUE);

SET @branch_a_id = LAST_INSERT_ID() - 2;
SET @branch_b_id = LAST_INSERT_ID() - 1;
SET @branch_c_id = LAST_INSERT_ID();

INSERT INTO `organizations` (`name`, `code`, `level`, `parent_id`, `address`, `is_active`) VALUES
('一级分行A_支行1', 'BRANCH_A_SUB1', 3, @branch_a_id, '上海市浦东新区', TRUE),
('一级分行A_支行2', 'BRANCH_A_SUB2', 3, @branch_a_id, '上海市徐汇区', TRUE),
('一级分行B_支行1', 'BRANCH_B_SUB1', 3, @branch_b_id, '广州市天河区', TRUE),
('一级分行B_支行2', 'BRANCH_B_SUB2', 3, @branch_b_id, '广州市越秀区', TRUE),
('一级分行C_支行1', 'BRANCH_C_SUB1', 3, @branch_c_id, '深圳市福田区', TRUE),
('一级分行C_支行2', 'BRANCH_C_SUB2', 3, @branch_c_id, '深圳市南山区', TRUE);

-- 插入初始用户数据（密码均为默认的bcrypt加密值，实际密码见下方说明）
INSERT INTO `users` (`username`, `password_hash`, `real_name`, `employee_id`, `email`, `phone`, `role_id`, `org_id`, `is_superuser`, `is_active`) VALUES
('admin', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYrWxYz7y0i', '系统管理员', 'ADMIN001', 'admin@greenfinance.com', '13800138000', 1, @hq_id, TRUE, TRUE),
('manager1', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYrWxYz7y0i', '张经理', 'MGR001', 'manager1@greenfinance.com', '13900139001', 2, @hq_id, FALSE, TRUE),
('reviewer1', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYrWxYz7y0i', '李审核', 'REV001', 'reviewer1@greenfinance.com', '13900139002', 3, @hq_id, FALSE, TRUE),
('auditor1', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYrWxYz7y0i', '王审批', 'AUD001', 'auditor1@greenfinance.com', '13900139003', 4, @hq_id, FALSE, TRUE);

-- 插入初始指标数据
INSERT INTO `green_loan_indicators` (`stat_date`, `org_id`, `green_loan_balance`, `green_loan_ratio`, `customer_count`, `growth_rate`, `green_investment`, `green_leasing`, `green_wealth_management`, `green_underwriting`) VALUES
('2025-11-01 00:00:00', @hq_id, 1000000000.00, 15.50, 552, -78.26, 123000000.00, 100000000.00, 100000000.00, 1111000000.00);

SET FOREIGN_KEY_CHECKS = 1;

-- 说明：
-- 1. 所有用户的默认密码为：123456
-- 2. 可以使用以下Python代码生成新的密码hash：
--    from passlib.context import CryptContext
--    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
--    print(pwd_context.hash("your_password"))
-- 3. 生产环境请务必修改默认密码