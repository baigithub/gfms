from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.models.user import User
from app.schemas.user import LoginRequest, Token
from app.services.auth import authenticate_user, create_access_token, get_current_user

router = APIRouter(prefix="/api/auth", tags=["认证"])


@router.post("/login", response_model=Token)
async def login(request: Request, login_data: LoginRequest, db: Session = Depends(get_db)):
    """用户登录"""
    # 临时禁用验证码验证，方便测试
    # if not login_data.captcha or len(login_data.captcha) != 4:
    #     raise HTTPException(
    #         status_code=status.HTTP_400_BAD_REQUEST,
    #         detail="验证码格式错误",
    #     )
    
    # 获取客户端信息
    client_ip = request.client.host if hasattr(request, 'client') else None
    user_agent = request.headers.get('user-agent', None)
    
    user = authenticate_user(db, login_data.username, login_data.password)
    
    if not user:
        # 记录失败的登录日志
        from app.utils.logger import record_login_log, record_exception_log
        record_login_log(
            db=db,
            user_id=None,
            user_account=login_data.username,
            user_name=login_data.username,
            status='failed',
            ip_address=client_ip,
            user_agent=user_agent,
            failure_reason="用户名或密码错误"
        )
        
        # 同时记录到异常日志
        record_exception_log(
            db=db,
            user_id=None,
            user_account=login_data.username,
            user_name=login_data.username,
            exception_module='auth',
            exception_type='AuthenticationError',
            exception_message='用户名或密码错误',
            exception_traceback=None,
            request_url=str(request.url),
            request_method=request.method,
            ip_address=client_ip
        )
        
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
        )
    
    # 更新最后登录时间
    from datetime import datetime
    user.last_login = datetime.utcnow()
    db.commit()
    
    # 记录成功的登录日志
    from app.utils.logger import record_login_log
    record_login_log(
        db=db,
        user_id=user.id,
        user_account=user.username,
        user_name=user.real_name or user.username,
        status='success',
        ip_address=client_ip,
        user_agent=user_agent
    )
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    
    from app.schemas.user import User as UserSchema
    user_data = UserSchema.model_validate(user)
    
    # 添加用户权限列表
    if user.role:
        user_data.permissions = user.role.permissions or []
    else:
        user_data.permissions = []
    
    return Token(
        access_token=access_token,
        token_type="bearer",
        user=user_data
    )

@router.get("/me")
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """获取当前用户信息"""
    from app.schemas.user import User as UserSchema
    return UserSchema.model_validate(current_user)


@router.post("/logout")
async def logout(current_user: User = Depends(get_current_user)):
    """用户登出"""
    return {"message": "登出成功"}


@router.get("/captcha")
async def get_captcha():
    """获取验证码"""
    import random
    import string
    # 简单验证码生成，实际项目应使用更复杂的验证码
    captcha = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
    return {"captcha": captcha}