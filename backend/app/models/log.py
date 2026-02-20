from sqlalchemy import Column, Integer, String, DateTime, Text, Float, ForeignKey
from sqlalchemy.sql import func
from app.database import Base


class OperationLog(Base):
    """操作日志表"""
    __tablename__ = "operation_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    operation_time = Column(DateTime(timezone=True), server_default=func.now(), comment="操作时间")
    operation_menu = Column(String(100), comment="操作菜单")
    request_url = Column(String(500), comment="请求接口")
    request_duration = Column(Float, comment="请求耗时（秒）")
    operator_name = Column(String(50), comment="操作人姓名")
    operator_account = Column(String(50), comment="操作人账号")
    request_method = Column(String(10), comment="请求方法")
    request_params = Column(Text, comment="请求参数")
    response_data = Column(Text, comment="响应数据")
    ip_address = Column(String(50), comment="IP地址")
    user_agent = Column(String(500), comment="用户代理")
    status_code = Column(Integer, comment="状态码")
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class LoginLog(Base):
    """登录日志表"""
    __tablename__ = "login_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_name = Column(String(50), comment="登录人姓名")
    user_account = Column(String(50), comment="登录人账号")
    ip_address = Column(String(50), comment="登录IP")
    device_type = Column(String(50), comment="登录设备类型")
    device_name = Column(String(100), comment="设备名称")
    browser = Column(String(100), comment="浏览器")
    os = Column(String(100), comment="操作系统")
    login_time = Column(DateTime(timezone=True), server_default=func.now(), comment="登录时间")
    logout_time = Column(DateTime(timezone=True), comment="登出时间")
    status = Column(String(20), comment="登录状态: success, failed")
    failure_reason = Column(String(200), comment="失败原因")
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class ExceptionLog(Base):
    """异常日志表"""
    __tablename__ = "exception_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    exception_module = Column(String(100), comment="异常模块")
    exception_interface = Column(String(500), comment="异常接口")
    stack_trace = Column(Text, comment="报错堆栈信息")
    exception_time = Column(DateTime(timezone=True), server_default=func.now(), comment="发生异常时间")
    exception_type = Column(String(100), comment="异常类型")
    exception_message = Column(String(500), comment="异常消息")
    request_url = Column(String(500), comment="请求URL")
    request_method = Column(String(10), comment="请求方法")
    request_params = Column(Text, comment="请求参数")
    user_id = Column(Integer, comment="用户ID")
    user_name = Column(String(50), comment="用户姓名")
    user_account = Column(String(50), comment="用户账号")
    ip_address = Column(String(50), comment="IP地址")
    is_resolved = Column(Integer, default=0, comment="是否已解决: 0-未解决, 1-已解决")
    resolved_by = Column(Integer, comment="解决人ID")
    resolved_time = Column(DateTime(timezone=True), comment="解决时间")
    resolved_note = Column(Text, comment="解决备注")
    created_at = Column(DateTime(timezone=True), server_default=func.now())