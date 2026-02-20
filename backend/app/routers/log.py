from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import text, desc, or_
from typing import Optional, List
from datetime import datetime, timedelta
from pydantic import BaseModel
from app.database import get_db
from app.models.log import OperationLog, LoginLog, ExceptionLog

router = APIRouter(prefix="/api/logs", tags=["日志管理"])


# ==================== 操作日志 ====================

class OperationLogResponse(BaseModel):
    id: int
    operation_time: datetime
    operation_menu: Optional[str]
    request_url: Optional[str]
    request_duration: Optional[float]
    operator_name: Optional[str]
    operator_account: Optional[str]
    request_method: Optional[str]
    ip_address: Optional[str]
    status_code: Optional[int]
    
    class Config:
        from_attributes = True


@router.get("/operations", response_model=dict)
async def get_operation_logs(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    operator_account: Optional[str] = Query(None, description="操作人账号"),
    operation_menu: Optional[str] = Query(None, description="操作菜单"),
    start_time: Optional[str] = Query(None, description="开始时间"),
    end_time: Optional[str] = Query(None, description="结束时间"),
    db: Session = Depends(get_db)
):
    """获取操作日志列表"""
    query = db.query(OperationLog)
    
    # 筛选条件
    if operator_account:
        query = query.filter(OperationLog.operator_account.like(f"%{operator_account}%"))
    if operation_menu:
        query = query.filter(OperationLog.operation_menu.like(f"%{operation_menu}%"))
    if start_time:
        query = query.filter(OperationLog.operation_time >= start_time)
    if end_time:
        query = query.filter(OperationLog.operation_time <= end_time)
    
    # 分页
    total = query.count()
    logs = query.order_by(desc(OperationLog.operation_time)).offset((page - 1) * page_size).limit(page_size).all()
    
    return {
        "data": [OperationLogResponse.model_validate(log) for log in logs],
        "total": total,
        "page": page,
        "page_size": page_size
    }


@router.delete("/operations/{log_id}")
async def delete_operation_log(log_id: int, db: Session = Depends(get_db)):
    """删除操作日志"""
    log = db.query(OperationLog).filter(OperationLog.id == log_id).first()
    if not log:
        raise HTTPException(status_code=404, detail="日志不存在")
    
    db.delete(log)
    db.commit()
    return {"message": "删除成功"}


@router.delete("/operations")
async def batch_delete_operation_logs(log_ids: List[int], db: Session = Depends(get_db)):
    """批量删除操作日志"""
    db.query(OperationLog).filter(OperationLog.id.in_(log_ids)).delete(synchronize_session=False)
    db.commit()
    return {"message": f"成功删除 {len(log_ids)} 条日志"}


# ==================== 登录日志 ====================

class LoginLogResponse(BaseModel):
    id: int
    user_name: Optional[str]
    user_account: Optional[str]
    ip_address: Optional[str]
    device_type: Optional[str]
    device_name: Optional[str]
    browser: Optional[str]
    os: Optional[str]
    login_time: Optional[datetime]
    logout_time: Optional[datetime]
    status: Optional[str]
    failure_reason: Optional[str]
    
    class Config:
        from_attributes = True


@router.get("/logins", response_model=dict)
async def get_login_logs(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    user_account: Optional[str] = Query(None, description="用户账号"),
    status: Optional[str] = Query(None, description="登录状态"),
    start_time: Optional[str] = Query(None, description="开始时间"),
    end_time: Optional[str] = Query(None, description="结束时间"),
    db: Session = Depends(get_db)
):
    """获取登录日志列表"""
    query = db.query(LoginLog)
    
    # 筛选条件
    if user_account:
        query = query.filter(LoginLog.user_account.like(f"%{user_account}%"))
    if status:
        query = query.filter(LoginLog.status == status)
    if start_time:
        query = query.filter(LoginLog.login_time >= start_time)
    if end_time:
        query = query.filter(LoginLog.login_time <= end_time)
    
    # 分页
    total = query.count()
    logs = query.order_by(desc(LoginLog.login_time)).offset((page - 1) * page_size).limit(page_size).all()
    
    return {
        "data": [LoginLogResponse.model_validate(log) for log in logs],
        "total": total,
        "page": page,
        "page_size": page_size
    }


@router.delete("/logins/{log_id}")
async def delete_login_log(log_id: int, db: Session = Depends(get_db)):
    """删除登录日志"""
    log = db.query(LoginLog).filter(LoginLog.id == log_id).first()
    if not log:
        raise HTTPException(status_code=404, detail="日志不存在")
    
    db.delete(log)
    db.commit()
    return {"message": "删除成功"}


@router.delete("/logins")
async def batch_delete_login_logs(log_ids: List[int], db: Session = Depends(get_db)):
    """批量删除登录日志"""
    db.query(LoginLog).filter(LoginLog.id.in_(log_ids)).delete(synchronize_session=False)
    db.commit()
    return {"message": f"成功删除 {len(log_ids)} 条日志"}


# ==================== 异常日志 ====================

class ExceptionLogResponse(BaseModel):
    id: int
    exception_module: Optional[str]
    exception_interface: Optional[str]
    stack_trace: Optional[str]
    exception_time: Optional[datetime]
    exception_type: Optional[str]
    exception_message: Optional[str]
    request_url: Optional[str]
    request_method: Optional[str]
    user_name: Optional[str]
    user_account: Optional[str]
    ip_address: Optional[str]
    is_resolved: Optional[int]
    resolved_by: Optional[int]
    resolved_time: Optional[datetime]
    resolved_note: Optional[str]
    
    class Config:
        from_attributes = True


@router.get("/exceptions", response_model=dict)
async def get_exception_logs(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    exception_module: Optional[str] = Query(None, description="异常模块"),
    is_resolved: Optional[int] = Query(None, description="是否已解决"),
    start_time: Optional[str] = Query(None, description="开始时间"),
    end_time: Optional[str] = Query(None, description="结束时间"),
    db: Session = Depends(get_db)
):
    """获取异常日志列表"""
    query = db.query(ExceptionLog)
    
    # 筛选条件
    if exception_module:
        query = query.filter(ExceptionLog.exception_module.like(f"%{exception_module}%"))
    if is_resolved is not None:
        query = query.filter(ExceptionLog.is_resolved == is_resolved)
    if start_time:
        query = query.filter(ExceptionLog.exception_time >= start_time)
    if end_time:
        query = query.filter(ExceptionLog.exception_time <= end_time)
    
    # 分页
    total = query.count()
    logs = query.order_by(desc(ExceptionLog.exception_time)).offset((page - 1) * page_size).limit(page_size).all()
    
    return {
        "data": [ExceptionLogResponse.model_validate(log) for log in logs],
        "total": total,
        "page": page,
        "page_size": page_size
    }


@router.get("/exceptions/{log_id}", response_model=ExceptionLogResponse)
async def get_exception_log_detail(log_id: int, db: Session = Depends(get_db)):
    """获取异常日志详情"""
    log = db.query(ExceptionLog).filter(ExceptionLog.id == log_id).first()
    if not log:
        raise HTTPException(status_code=404, detail="日志不存在")
    
    return ExceptionLogResponse.model_validate(log)


@router.patch("/exceptions/{log_id}/resolve")
async def resolve_exception_log(
    log_id: int,
    resolved_note: Optional[str] = Query(None, description="解决备注"),
    current_user_id: int = Query(..., description="当前用户ID"),
    db: Session = Depends(get_db)
):
    """标记异常日志为已解决"""
    log = db.query(ExceptionLog).filter(ExceptionLog.id == log_id).first()
    if not log:
        raise HTTPException(status_code=404, detail="日志不存在")
    
    log.is_resolved = 1
    log.resolved_by = current_user_id
    log.resolved_time = datetime.now()
    log.resolved_note = resolved_note
    
    db.commit()
    return {"message": "标记成功"}


@router.delete("/exceptions/{log_id}")
async def delete_exception_log(log_id: int, db: Session = Depends(get_db)):
    """删除异常日志"""
    log = db.query(ExceptionLog).filter(ExceptionLog.id == log_id).first()
    if not log:
        raise HTTPException(status_code=404, detail="日志不存在")
    
    db.delete(log)
    db.commit()
    return {"message": "删除成功"}


@router.delete("/exceptions")
async def batch_delete_exception_logs(log_ids: List[int], db: Session = Depends(get_db)):
    """批量删除异常日志"""
    db.query(ExceptionLog).filter(ExceptionLog.id.in_(log_ids)).delete(synchronize_session=False)
    db.commit()
    return {"message": f"成功删除 {len(log_ids)} 条日志"}


# ==================== 统计信息 ====================

@router.get("/statistics")
async def get_log_statistics(db: Session = Depends(get_db)):
    """获取日志统计信息"""
    # 今日操作日志数
    today = datetime.now().date()
    operation_count_today = db.query(OperationLog).filter(
        OperationLog.operation_time >= today
    ).count()
    
    # 今日登录成功数
    login_success_today = db.query(LoginLog).filter(
        LoginLog.login_time >= today,
        LoginLog.status == 'success'
    ).count()
    
    # 今日登录失败数
    login_failed_today = db.query(LoginLog).filter(
        LoginLog.login_time >= today,
        LoginLog.status == 'failed'
    ).count()
    
    # 未解决的异常数
    unresolved_exceptions = db.query(ExceptionLog).filter(
        ExceptionLog.is_resolved == 0
    ).count()
    
    return {
        "operation_count_today": operation_count_today,
        "login_success_today": login_success_today,
        "login_failed_today": login_failed_today,
        "unresolved_exceptions": unresolved_exceptions
    }