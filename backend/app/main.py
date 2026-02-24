from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.config import settings
from app.database import engine, Base
from app.routers import auth, green_finance, system, workflow, workflow_variables, files, log, announcement
from app.scheduler import start_scheduler, stop_scheduler
import atexit
import logging
import os

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 导入所有模型,确保关系正确建立
import app.models.user
import app.models.workflow
import app.models.workflow_variable
import app.models.green_finance
import app.models.log
import app.models.announcement

# 创建数据库表
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="绿色金融管理系统 - 支持2030年碳达峰、2060年碳中和目标的银行绿色贷款管理系统"
)

# 配置CORS - 限制允许的方法
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "HEAD"],  # 禁用 OPTIONS 和 TRACE
    allow_headers=["*"],
)

# 添加日志记录中间件
from app.middleware.logging import LoggingMiddleware
app.add_middleware(LoggingMiddleware)

# 添加速率限制中间件
from app.middleware.rate_limit import RateLimitMiddleware, BlockUnsafeMethodsMiddleware
app.add_middleware(RateLimitMiddleware)
app.add_middleware(BlockUnsafeMethodsMiddleware)

# 注册路由
app.include_router(auth.router)
app.include_router(green_finance.router)
app.include_router(system.router)
app.include_router(workflow.router)
app.include_router(workflow_variables.router)
app.include_router(files.router)
app.include_router(log.router)
app.include_router(announcement.router)

# 挂载静态文件目录
os.makedirs("uploads", exist_ok=True)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")


@app.get("/")
async def root():
    return {
        "message": "绿色金融管理系统 API",
        "version": settings.APP_VERSION,
        "description": "支持绿色贷款认定、审批、统计分析的全流程管理系统"
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


@app.on_event("startup")
async def startup_event():
    """应用启动事件"""
    logger.info("应用启动中...")
    start_scheduler()
    logger.info("应用启动完成")


@app.on_event("shutdown")
async def shutdown_event():
    """应用关闭事件"""
    logger.info("应用关闭中...")
    stop_scheduler()
    logger.info("应用关闭完成")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )