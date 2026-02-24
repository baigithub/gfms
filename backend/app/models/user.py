from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
import json


class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    real_name = Column(String(50), nullable=False)
    employee_id = Column(String(20), unique=True, index=True)
    email = Column(String(100), unique=True, index=True)
    phone = Column(String(20))
    wechat_openid = Column(String(255))
    wechat_unionid = Column(String(255))
    avatar = Column(String(255))
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_login = Column(DateTime(timezone=True))
    
    # Relationships
    role_id = Column(Integer, ForeignKey("roles.id"))
    role = relationship("Role", back_populates="users")
    org_id = Column(Integer, ForeignKey("organizations.id"))
    organization = relationship("Organization", back_populates="users")


class Role(Base):
    __tablename__ = "roles"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False)
    description = Column(String(200))
    _permissions = Column("permissions", Text)  # JSON string of permissions
    org_level = Column(Integer, default=1)  # 1: 总行, 2: 分行, 3: 支行
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    users = relationship("User", back_populates="role")
    
    @property
    def permissions(self):
        """获取权限列表"""
        if self._permissions:
            try:
                return json.loads(self._permissions)
            except (json.JSONDecodeError, TypeError):
                return []
        return []
    
    @permissions.setter
    def permissions(self, value):
        """设置权限列表，保存为JSON字符串"""
        if value is None:
            self._permissions = None
        elif isinstance(value, list):
            self._permissions = json.dumps(value, ensure_ascii=False)
        else:
            self._permissions = str(value)


class Organization(Base):
    __tablename__ = "organizations"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    code = Column(String(20), unique=True, index=True)
    parent_id = Column(Integer, ForeignKey("organizations.id"), nullable=True)
    level = Column(Integer, default=1)  # 1: 总行, 2: 分行, 3: 支行
    address = Column(String(200))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    users = relationship("User", back_populates="organization")
    parent = relationship("Organization", remote_side=[id])