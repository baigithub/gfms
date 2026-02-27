from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    APP_NAME: str = "绿色金融管理系统"
    APP_VERSION: str = "1.0.0"
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30  # 30 minutes
    
    # Docker环境检测
    IS_DOCKER: bool = os.getenv('IS_DOCKER', 'false').lower() == 'true'
    
    # MySQL Database
    # 如果是Docker环境，使用Docker内部网络地址
    MYSQL_HOST: str = "mysql" if IS_DOCKER else "localhost"
    MYSQL_PORT: int = 3306
    MYSQL_USER: str = "gfms_user"
    MYSQL_PASSWORD: str = "gfms_password"
    MYSQL_DATABASE: str = "green_finance"
    
    # 本地开发环境配置（如果需要覆盖）
    MYSQL_HOST_LOCAL: Optional[str] = None
    MYSQL_PORT_LOCAL: Optional[int] = None
    MYSQL_USER_LOCAL: Optional[str] = None
    MYSQL_PASSWORD_LOCAL: Optional[str] = None
    
    # CORS
    CORS_ORIGINS: list = ["http://localhost:5173", "http://localhost:3000", "http://localhost:8082"]
    
    @property
    def DATABASE_URL(self) -> str:
        # 如果设置了本地环境变量，优先使用本地配置
        if self.IS_DOCKER == False and self.MYSQL_HOST_LOCAL:
            host = self.MYSQL_HOST_LOCAL
            port = self.MYSQL_PORT_LOCAL or self.MYSQL_PORT
            user = self.MYSQL_USER_LOCAL or self.MYSQL_USER
            password = self.MYSQL_PASSWORD_LOCAL or self.MYSQL_PASSWORD
        else:
            host = self.MYSQL_HOST
            port = self.MYSQL_PORT
            user = self.MYSQL_USER
            password = self.MYSQL_PASSWORD
        
        return f"mysql+pymysql://{user}:{password}@{host}:{port}/{self.MYSQL_DATABASE}"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()