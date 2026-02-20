"""
速率限制中间件
用于防止暴力破解攻击
"""

from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Dict
import time
from collections import defaultdict
import threading

class RateLimiter:
    """简单的内存速率限制器"""
    
    def __init__(self, max_requests: int = 5, window_seconds: int = 60):
        """
        初始化速率限制器
        
        Args:
            max_requests: 时间窗口内最大请求数
            window_seconds: 时间窗口（秒）
        """
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests: Dict[str, list] = defaultdict(list)
        self.lock = threading.Lock()
    
    def is_allowed(self, key: str) -> bool:
        """
        检查是否允许请求
        
        Args:
            key: 限制键（通常是 IP 地址或用户名）
            
        Returns:
            bool: 是否允许请求
        """
        current_time = time.time()
        
        with self.lock:
            # 获取该键的请求记录
            request_times = self.requests[key]
            
            # 移除超出时间窗口的请求
            request_times = [t for t in request_times if current_time - t < self.window_seconds]
            self.requests[key] = request_times
            
            # 检查请求数量
            if len(request_times) >= self.max_requests:
                return False
            
            # 记录当前请求
            request_times.append(current_time)
            return True
    
    def get_remaining_time(self, key: str) -> int:
        """
        获取剩余限制时间（秒）
        
        Args:
            key: 限制键
            
        Returns:
            int: 剩余秒数
        """
        current_time = time.time()
        
        with self.lock:
            request_times = self.requests[key]
            
            if not request_times:
                return 0
            
            # 找到最早的有效请求时间
            earliest_time = request_times[0]
            remaining_time = int(self.window_seconds - (current_time - earliest_time))
            
            return max(0, remaining_time)


# 创建速率限制器实例
# 登录接口：5 次/分钟
login_rate_limiter = RateLimiter(max_requests=5, window_seconds=60)

# 通用 API 接口：100 次/分钟
api_rate_limiter = RateLimiter(max_requests=100, window_seconds=60)


class RateLimitMiddleware(BaseHTTPMiddleware):
    """速率限制中间件"""
    
    async def dispatch(self, request: Request, call_next):
        """
        对登录接口和 API 接口实施速率限制
        """
        # 获取客户端 IP
        client_ip = request.client.host if request.client else "unknown"
        
        # 检查是否是登录接口
        if "/api/auth/login" in request.url.path:
            if not login_rate_limiter.is_allowed(client_ip):
                remaining_time = login_rate_limiter.get_remaining_time(client_ip)
                return JSONResponse(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    content={
                        "detail": "登录尝试次数过多，请稍后再试",
                        "retry_after": remaining_time
                    }
                )
        
        # 检查是否是 API 接口
        elif request.url.path.startswith("/api/"):
            if not api_rate_limiter.is_allowed(client_ip):
                remaining_time = api_rate_limiter.get_remaining_time(client_ip)
                return JSONResponse(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    content={
                        "detail": "请求频率过高，请稍后再试",
                        "retry_after": remaining_time
                    }
                )
        
        # 继续处理请求
        response = await call_next(request)
        
        # 添加速率限制相关的响应头
        if "/api/auth/login" in request.url.path:
            remaining = login_rate_limiter.get_remaining_time(client_ip)
            if remaining > 0:
                response.headers["X-RateLimit-Limit"] = str(login_rate_limiter.max_requests)
                response.headers["X-RateLimit-Remaining"] = "0"
                response.headers["X-RateLimit-Reset"] = str(int(time.time()) + remaining)
            else:
                with login_rate_limiter.lock:
                    request_times = login_rate_limiter.requests[client_ip]
                    response.headers["X-RateLimit-Limit"] = str(login_rate_limiter.max_requests)
                    response.headers["X-RateLimit-Remaining"] = str(max(0, login_rate_limiter.max_requests - len(request_times)))
                    response.headers["X-RateLimit-Reset"] = str(int(time.time()) + login_rate_limiter.window_seconds)
        
        return response


class BlockUnsafeMethodsMiddleware(BaseHTTPMiddleware):
    """阻止不安全的 HTTP 方法"""
    
    async def dispatch(self, request: Request, call_next):
        """
        禁用 TRACE 方法（OPTIONS 用于 CORS 预检，由 CORS 中间件处理）
        """
        # 禁用 TRACE 方法（可能泄露敏感信息）
        if request.method.upper() == "TRACE":
            return JSONResponse(
                status_code=status.HTTP_405_METHOD_NOT_ALLOWED,
                content={
                    "detail": f"Method '{request.method}' not allowed"
                }
            )
        
        # 继续处理请求
        return await call_next(request)