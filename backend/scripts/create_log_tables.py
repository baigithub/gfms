"""
创建日志管理相关表
"""
from sqlalchemy import create_engine, text
from app.config import settings

engine = create_engine(settings.DATABASE_URL)

def create_log_tables():
    """创建日志管理表"""
    with engine.connect() as conn:
        print("开始创建日志管理表...")
        
        # 创建操作日志表
        print("创建操作日志表...")
        conn.execute(text('''
            CREATE TABLE IF NOT EXISTS operation_logs (
                id INT AUTO_INCREMENT PRIMARY KEY,
                operation_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '操作时间',
                operation_menu VARCHAR(100) COMMENT '操作菜单',
                request_url VARCHAR(500) COMMENT '请求接口',
                request_duration FLOAT COMMENT '请求耗时（秒）',
                operator_name VARCHAR(50) COMMENT '操作人姓名',
                operator_account VARCHAR(50) COMMENT '操作人账号',
                request_method VARCHAR(10) COMMENT '请求方法',
                request_params TEXT COMMENT '请求参数',
                response_data TEXT COMMENT '响应数据',
                ip_address VARCHAR(50) COMMENT 'IP地址',
                user_agent VARCHAR(500) COMMENT '用户代理',
                status_code INT COMMENT '状态码',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_operation_time (operation_time),
                INDEX idx_operator_account (operator_account),
                INDEX idx_operation_menu (operation_menu)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='操作日志表'
        '''))
        
        # 创建登录日志表
        print("创建登录日志表...")
        conn.execute(text('''
            CREATE TABLE IF NOT EXISTS login_logs (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_name VARCHAR(50) COMMENT '登录人姓名',
                user_account VARCHAR(50) COMMENT '登录人账号',
                ip_address VARCHAR(50) COMMENT '登录IP',
                device_type VARCHAR(50) COMMENT '登录设备类型',
                device_name VARCHAR(100) COMMENT '设备名称',
                browser VARCHAR(100) COMMENT '浏览器',
                os VARCHAR(100) COMMENT '操作系统',
                login_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '登录时间',
                logout_time DATETIME COMMENT '登出时间',
                status VARCHAR(20) COMMENT '登录状态: success, failed',
                failure_reason VARCHAR(200) COMMENT '失败原因',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_login_time (login_time),
                INDEX idx_user_account (user_account),
                INDEX idx_status (status)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='登录日志表'
        '''))
        
        # 创建异常日志表
        print("创建异常日志表...")
        conn.execute(text('''
            CREATE TABLE IF NOT EXISTS exception_logs (
                id INT AUTO_INCREMENT PRIMARY KEY,
                exception_module VARCHAR(100) COMMENT '异常模块',
                exception_interface VARCHAR(500) COMMENT '异常接口',
                stack_trace TEXT COMMENT '报错堆栈信息',
                exception_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '发生异常时间',
                exception_type VARCHAR(100) COMMENT '异常类型',
                exception_message VARCHAR(500) COMMENT '异常消息',
                request_url VARCHAR(500) COMMENT '请求URL',
                request_method VARCHAR(10) COMMENT '请求方法',
                request_params TEXT COMMENT '请求参数',
                user_id INT COMMENT '用户ID',
                user_name VARCHAR(50) COMMENT '用户姓名',
                user_account VARCHAR(50) COMMENT '用户账号',
                ip_address VARCHAR(50) COMMENT 'IP地址',
                is_resolved INT DEFAULT 0 COMMENT '是否已解决: 0-未解决, 1-已解决',
                resolved_by INT COMMENT '解决人ID',
                resolved_time DATETIME COMMENT '解决时间',
                resolved_note TEXT COMMENT '解决备注',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_exception_time (exception_time),
                INDEX idx_exception_module (exception_module),
                INDEX idx_is_resolved (is_resolved)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='异常日志表'
        '''))
        
        conn.commit()
        print("✓ 日志管理表创建完成！")

if __name__ == '__main__':
    create_log_tables()