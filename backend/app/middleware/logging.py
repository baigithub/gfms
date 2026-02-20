"""
日志记录中间件
"""
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from sqlalchemy.orm import Session
import re

from app.utils.logger import record_operation_log


class LoggingMiddleware(BaseHTTPMiddleware):
    """日志记录中间件"""
    
    # 不需要记录日志的路径
    EXCLUDE_PATHS = [
        '/api/auth/login',
        '/api/auth/captcha',
        '/api/health',
        '/api/dashboard',
        '/api/logs',
        '/docs',
        '/openapi.json',
    ]
    
    # 路径到操作菜单的映射
    OPERATION_MENU_MAP = {
        '/api/tasks/': '任务管理',
        '/api/tasks/pending': '任务管理-待办任务',
        '/api/tasks/completed': '任务管理-已完成任务',
        '/api/tasks/archived': '任务管理-已归档任务',
        '/api/green-categories': '绿色分类管理',
        '/api/identifications/': '绿色认定管理',
        '/api/users': '用户管理',
        '/api/roles': '角色管理',
        '/api/orgs': '机构管理',
        '/api/workflow-definitions': '流程管理',
        '/api/workflow-instances': '流程实例',
        '/api/files': '文件管理',
    }
    
    # HTTP方法到操作类型的映射
    OPERATION_TYPE_MAP = {
        'GET': '查询',
        'POST': '新增',
        'PUT': '修改',
        'DELETE': '删除',
        'PATCH': '更新'
    }
    
    async def dispatch(self, request: Request, call_next):
        """处理请求并记录日志"""
        # 获取响应
        response = await call_next(request)
        
        # 检查是否需要记录日志
        if self.should_log(request, response):
            await self.log_request(request, response)
        
        return response
    
    def should_log(self, request: Request, response) -> bool:
        """判断是否需要记录日志"""
        # 检查是否在排除列表中
        for exclude_path in self.EXCLUDE_PATHS:
            if request.url.path.startswith(exclude_path):
                return False
        
        # 只记录成功的请求
        if response.status_code >= 400:
            return False
        
        # 只记录需要认证的请求
        auth_header = request.headers.get('authorization')
        if not auth_header:
            return False
        
        # 只记录修改操作 (POST, PUT, DELETE, PATCH)
        if request.method not in ['POST', 'PUT', 'DELETE', 'PATCH']:
            return False
        
        return True
    
    async def log_request(self, request: Request, response):
        """记录请求日志"""
        try:
            # 从请求状态中获取数据库会话
            from app.database import get_db
            db = next(get_db())
            
            # 从token中获取用户信息
            from app.services.auth import verify_token
            from fastapi.security import HTTPBearer
            security = HTTPBearer()
            
            try:
                credentials = await security(request)
                user = verify_token(credentials, db)
            except:
                return
            
            # 获取操作信息
            operation_type = self.OPERATION_TYPE_MAP.get(request.method, request.method)
            operation_menu = self.get_operation_menu(request.url.path)
            operation_desc = self.get_operation_desc(request)
            
            # 记录操作日志
            record_operation_log(
                db=db,
                user_id=user.id,
                user_account=user.username,
                user_name=user.real_name or user.username,
                operation_menu=operation_menu,
                operation_desc=operation_desc,
                request_method=request.method,
                request_url=str(request.url),
                ip_address=request.client.host if hasattr(request, 'client') else None,
                user_agent=request.headers.get('user-agent', None),
                status_code=response.status_code
            )
            
        except Exception as e:
            print(f"记录操作日志失败: {e}")
        finally:
            db.close()
    
    def get_operation_menu(self, path: str) -> str:
        """获取操作菜单"""
        # 尝试精确匹配
        if path in self.OPERATION_MENU_MAP:
            return self.OPERATION_MENU_MAP[path]
        
        # 尝试前缀匹配
        for pattern, menu in self.OPERATION_MENU_MAP.items():
            if path.startswith(pattern):
                return menu
        
        # 提取路径信息
        parts = path.strip('/').split('/')
        if len(parts) >= 2:
            return f"{parts[0]}-{parts[1]}"
        
        return path
    
    def get_operation_desc(self, request: Request) -> str:
        """获取操作描述"""
        method = request.method
        path = request.url.path
        
        # 根据不同的路径和方法生成描述
        if 'tasks' in path:
            if method == 'POST' and 'complete' in path:
                return '完成任务'
            elif method == 'POST' and 'withdraw' in path:
                return '撤回任务'
            elif method == 'POST' and 'return' in path:
                return '退回任务'
            elif method == 'POST' and 'save' in path:
                return '保存任务'
            elif method == 'PUT' and 'category' in path:
                return '更新任务分类'
            elif method == 'POST' and 'mark-non-green' in path:
                return '标记为非绿'
        
        return f"{method} {path}"