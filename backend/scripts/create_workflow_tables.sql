-- 创建流程定义表
CREATE TABLE IF NOT EXISTS process_definitions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    `key` VARCHAR(100) NOT NULL UNIQUE,
    name VARCHAR(200) NOT NULL,
    version INT DEFAULT 1,
    description TEXT,
    bpmn_xml TEXT NOT NULL,
    status ENUM('draft', 'active', 'archived') DEFAULT 'draft',
    deployed_by INT,
    deployed_at DATETIME,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_key (`key`),
    INDEX idx_status (status),
    FOREIGN KEY (deployed_by) REFERENCES users(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 创建流程实例表
CREATE TABLE IF NOT EXISTS process_instances (
    id INT AUTO_INCREMENT PRIMARY KEY,
    instance_key VARCHAR(100) NOT NULL UNIQUE,
    definition_id INT NOT NULL,
    business_key VARCHAR(100),
    status ENUM('running', 'completed', 'suspended', 'terminated') DEFAULT 'running',
    current_node VARCHAR(100),
    started_by INT,
    started_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    completed_at DATETIME,
    variables TEXT,
    INDEX idx_instance_key (instance_key),
    INDEX idx_definition_id (definition_id),
    INDEX idx_status (status),
    FOREIGN KEY (definition_id) REFERENCES process_definitions(id),
    FOREIGN KEY (started_by) REFERENCES users(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 创建流程任务表
CREATE TABLE IF NOT EXISTS process_tasks (
    id INT AUTO_INCREMENT PRIMARY KEY,
    instance_id INT NOT NULL,
    task_key VARCHAR(100) NOT NULL,
    task_name VARCHAR(200) NOT NULL,
    node_id VARCHAR(100),
    assignee_id INT,
    status ENUM('pending', 'completed', 'skipped', 'cancelled') DEFAULT 'pending',
    priority INT DEFAULT 50,
    due_date DATETIME,
    started_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    completed_at DATETIME,
    variables TEXT,
    comment TEXT,
    INDEX idx_instance_id (instance_id),
    INDEX idx_assignee_id (assignee_id),
    INDEX idx_status (status),
    FOREIGN KEY (instance_id) REFERENCES process_instances(id),
    FOREIGN KEY (assignee_id) REFERENCES users(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 创建任务节点定义表
CREATE TABLE IF NOT EXISTS task_nodes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    definition_id INT,
    node_id VARCHAR(100) NOT NULL,
    node_name VARCHAR(200) NOT NULL,
    node_type VARCHAR(50),
    role_id INT,
    org_level VARCHAR(50),
    is_skip_if_empty INT DEFAULT 0,
    sequence INT DEFAULT 0,
    INDEX idx_definition_id (definition_id),
    INDEX idx_node_id (node_id),
    FOREIGN KEY (definition_id) REFERENCES process_definitions(id),
    FOREIGN KEY (role_id) REFERENCES roles(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;