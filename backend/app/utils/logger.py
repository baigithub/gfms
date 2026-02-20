"""
日志记录工具函数
"""
from datetime import datetime
from sqlalchemy.orm import Session
from app.models.log import OperationLog, LoginLog, ExceptionLog


def record_login_log(
    db: Session,
    user_id: int,
    user_account: str,
    user_name: str,
    status: str,
    ip_address: str = None,
    user_agent: str = None,
    failure_reason: str = None
):
    """记录登录日志"""
    try:
        # 解析user_agent获取设备信息
        device_type = None
        device_name = None
        browser = None
        os = None
        
        if user_agent:
            user_agent_lower = user_agent.lower()
            # 检测浏览器
            if 'chrome' in user_agent_lower:
                browser = 'Chrome'
            elif 'firefox' in user_agent_lower:
                browser = 'Firefox'
            elif 'safari' in user_agent_lower and 'chrome' not in user_agent_lower:
                browser = 'Safari'
            elif 'edge' in user_agent_lower:
                browser = 'Edge'
            
            # 检测操作系统
            if 'windows' in user_agent_lower:
                os = 'Windows'
            elif 'mac' in user_agent_lower:
                os = 'macOS'
            elif 'linux' in user_agent_lower:
                os = 'Linux'
            elif 'android' in user_agent_lower:
                os = 'Android'
                device_type = 'Mobile'
            elif 'iphone' in user_agent_lower or 'ipad' in user_agent_lower:
                os = 'iOS'
                device_type = 'Mobile'
            
            # 检测设备类型
            if 'mobile' in user_agent_lower or 'android' in user_agent_lower or 'iphone' in user_agent_lower:
                device_type = device_type or 'Mobile'
            elif 'tablet' in user_agent_lower or 'ipad' in user_agent_lower:
                device_type = 'Tablet'
            else:
                device_type = device_type or 'Desktop'
        
        login_log = LoginLog(
            user_name=user_name,
            user_account=user_account,
            ip_address=ip_address,
            device_type=device_type,
            device_name=device_name,
            browser=browser,
            os=os,
            login_time=datetime.now(),
            status=status,
            failure_reason=failure_reason
        )
        db.add(login_log)
        db.commit()
    except Exception as e:
        print(f"记录登录日志失败: {e}")
        db.rollback()


def record_operation_log(
    db: Session,
    user_id: int,
    user_account: str,
    user_name: str,
    operation_menu: str,
    operation_desc: str,
    request_method: str = None,
    request_url: str = None,
    ip_address: str = None,
    user_agent: str = None,
    status_code: int = 200
):
    """记录操作日志"""
    try:
        operation_log = OperationLog(
            operation_menu=operation_menu,
            request_url=request_url,
            operator_name=user_name,
            operator_account=user_account,
            request_method=request_method,
            ip_address=ip_address,
            user_agent=user_agent,
            status_code=status_code
        )
        db.add(operation_log)
        db.commit()
    except Exception as e:
        print(f"记录操作日志失败: {e}")
        db.rollback()


def record_exception_log(
    db: Session,
    user_id: int,
    user_account: str,
    user_name: str,
    exception_module: str,
    exception_type: str,
    exception_message: str,
    exception_traceback: str = None,
    request_url: str = None,
    request_method: str = None,
    ip_address: str = None
):
    """记录异常日志"""
    try:
        exception_log = ExceptionLog(
            exception_module=exception_module,
            exception_type=exception_type,
            exception_message=exception_message,
            stack_trace=exception_traceback,
            request_url=request_url,
            request_method=request_method,
            user_id=user_id,
            user_name=user_name,
            user_account=user_account,
            ip_address=ip_address
        )
        db.add(exception_log)
        db.commit()
    except Exception as e:
        print(f"记录异常日志失败: {e}")
        db.rollback()